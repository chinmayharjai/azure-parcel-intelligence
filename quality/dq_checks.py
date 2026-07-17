from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pipeline.io import read_jsonl, read_jsonl_tree, write_jsonl


class DataQualityError(RuntimeError): pass


def run(data_root: Path, expected_parcels: int | None = None) -> dict:
    bronze = read_jsonl_tree(data_root / "bronze")
    silver = read_jsonl(data_root / "silver" / "scan_events.jsonl")
    facts = read_jsonl(data_root / "gold" / "sla_facts.jsonl")
    incidents: list[dict] = []
    required = ("scan_id", "parcel_id", "event_type", "event_time", "hub_id", "lane_id")
    for field in required:
        missing = sum(not row.get(field) for row in silver)
        if missing: incidents.append({"check": "mandatory_fields", "field": field, "failed_rows": missing})
    if len({r["scan_id"] for r in silver}) != len(silver): incidents.append({"check": "duplicate_scan_id", "failed_rows": 1})
    parcel_ids = {r["parcel_id"] for r in silver}
    if any(r["parcel_id"] not in parcel_ids for r in facts): incidents.append({"check": "referential_integrity", "failed_rows": 1})
    if expected_parcels is not None and len(facts) != expected_parcels: incidents.append({"check": "parcel_coverage", "expected": expected_parcels, "actual": len(facts)})
    result = {"bronze_rows": len(bronze), "silver_rows": len(silver), "gold_parcels": len(facts), "dedup_removed": len(bronze) - len(silver), "incident_count": len(incidents)}
    if incidents:
        for item in incidents: item["recorded_at"] = datetime.now(timezone.utc).isoformat()
        write_jsonl(data_root / "quality" / "dq_incidents.jsonl", incidents)
        raise DataQualityError(str(incidents))
    write_jsonl(data_root / "quality" / "dq_incidents.jsonl", [])
    return result
