from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pipeline.io import read_jsonl_tree, write_jsonl

TERMINAL = {"DELIVERED", "FAILED_DELIVERY", "RTO_INITIATED"}


def parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def bronze(data_root: Path) -> int:
    raw = read_jsonl_tree(data_root / "landing")
    return write_jsonl(data_root / "bronze" / "scan_events.jsonl", raw)


def silver(data_root: Path, late_hours: int = 6) -> tuple[list[dict], int]:
    raw = read_jsonl_tree(data_root / "bronze")
    selected: dict[str, dict] = {}
    for event in raw:  # idempotent MERGE key selection: retain newest ingestion of scan_id
        previous = selected.get(event["scan_id"])
        if previous is None or event["ingest_time"] > previous["ingest_time"]:
            selected[event["scan_id"]] = event
    by_parcel: dict[str, list[dict]] = defaultdict(list)
    for event in selected.values(): by_parcel[event["parcel_id"]].append(event)
    cleaned: list[dict] = []
    for parcel_events in by_parcel.values():
        parcel_events.sort(key=lambda e: (e["event_time"], e["scan_id"]))
        prior_event_time = None
        for order, event in enumerate(parcel_events, start=1):
            event = event.copy()
            event["event_order"] = order
            event["phone_hash"] = hashlib.sha256(event.pop("phone_number").encode()).hexdigest()
            event["is_late"] = (parse(event["ingest_time"]) - parse(event["event_time"])).total_seconds() > late_hours * 3600
            event["out_of_order_repaired"] = bool(prior_event_time and parse(event["event_time"]) < prior_event_time)
            prior_event_time = parse(event["event_time"])
            cleaned.append(event)
    cleaned.sort(key=lambda e: (e["parcel_id"], e["event_order"]))
    write_jsonl(data_root / "silver" / "scan_events.jsonl", cleaned)
    return cleaned, len(raw) - len(cleaned)


def gold(data_root: Path, events: list[dict]) -> dict[str, int]:
    by_parcel: dict[str, list[dict]] = defaultdict(list)
    for event in events: by_parcel[event["parcel_id"]].append(event)
    ops: dict[tuple[str, str], dict] = {}
    sla: list[dict] = []
    delivered = 0
    now = datetime(2026, 2, 5, tzinfo=timezone.utc)
    for parcel_id, trail in by_parcel.items():
        trail.sort(key=lambda e: e["event_order"])
        first, latest = trail[0], trail[-1]
        pickup = parse(first["event_time"])
        terminal = next((x for x in reversed(trail) if x["event_type"] in TERMINAL), None)
        actual_hours = round(((parse(terminal["event_time"]) if terminal else now) - pickup).total_seconds() / 3600, 2)
        status = terminal["event_type"] if terminal else latest["event_type"]
        is_delivered = status == "DELIVERED"
        delivered += is_delivered
        breach = actual_hours > first["sla_hours"]
        sla.append({"parcel_id": parcel_id, "lane_id": first["lane_id"], "origin_hub": first["origin_hub"], "destination_hub": first["destination_hub"], "pickup_date": first["event_time"][:10], "status": status, "promised_hours": first["sla_hours"], "actual_hours": actual_hours, "breach_flag": breach, "exception_reason": None if is_delivered else status})
        key = (latest["event_time"][:13] + ":00Z", latest["hub_id"])
        record = ops.setdefault(key, {"hour": key[0], "hub_id": key[1], "parcel_count": 0, "backlog_count": 0, "failed_delivery_count": 0, "breach_risk_count": 0})
        record["parcel_count"] += 1
        record["backlog_count"] += status not in TERMINAL
        record["failed_delivery_count"] += status == "FAILED_DELIVERY"
        record["breach_risk_count"] += (not terminal and actual_hours > first["sla_hours"] * .8)
    for record in ops.values():
        record["failed_delivery_rate"] = round(record["failed_delivery_count"] / record["parcel_count"], 4)
    write_jsonl(data_root / "gold" / "ops_hourly.jsonl", sorted(ops.values(), key=lambda x: (x["hour"], x["hub_id"])))
    write_jsonl(data_root / "gold" / "sla_facts.jsonl", sla)
    return {"gold_sla_rows": len(sla), "gold_delivered": delivered, "ops_rows": len(ops)}


def latest_states(events: list[dict]) -> list[dict]:
    states: list[dict] = []
    for parcel_id, trail in _group(events).items():
        trail.sort(key=lambda e: e["event_order"])
        latest = trail[-1]
        states.append({"id": parcel_id, "parcel_id": parcel_id, "partition_key": parcel_id, "current_status": latest["event_type"], "last_hub": latest["hub_id"], "last_event_time": latest["event_time"], "mini_history": [{"type": e["event_type"], "time": e["event_time"], "hub": e["hub_id"]} for e in trail[-5:]]})
    return states


def _group(events: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for event in events: grouped[event["parcel_id"]].append(event)
    return grouped
