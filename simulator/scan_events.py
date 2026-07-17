from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline.io import write_jsonl

EVENTS = ("PICKED_UP", "AT_ORIGIN_HUB", "IN_TRANSIT", "AT_DESTINATION_HUB", "OUT_FOR_DELIVERY", "DELIVERED")
HUBS = [f"HUB-{i:02d}" for i in range(1, 41)]
NAMES = ("Aarav", "Diya", "Kabir", "Ananya", "Vivaan", "Isha", "Arjun", "Meera")


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def generate(output: Path, parcels: int, seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events: list[dict] = []
    sellers: dict[str, dict] = {}
    for n in range(1, parcels + 1):
        parcel_id = f"PAR{n:08d}"
        seller_id = f"SEL{(n % 250) + 1:04d}"
        sellers.setdefault(seller_id, {"seller_id": seller_id, "seller_name": f"Seller {(n % 250) + 1:03d}", "tier": ("standard", "gold", "platinum")[n % 3]})
        origin = HUBS[n % len(HUBS)]
        destination = HUBS[(n * 7) % len(HUBS)]
        picked = start + timedelta(hours=rng.randrange(30 * 24), minutes=rng.randrange(60))
        sla_hours = (24, 48, 72)[n % 3]
        trail = list(EVENTS)
        if rng.random() < 0.12:
            trail[-1] = "FAILED_DELIVERY"
        if rng.random() < 0.035:
            trail = trail[:-1] + ["RTO_INITIATED"]
        if rng.random() < 0.08:
            del trail[rng.randrange(1, len(trail) - 1)]
        previous = picked
        for sequence, event_type in enumerate(trail):
            if sequence:
                delay = rng.randint(2, 13)
                if origin == "HUB-13" and sequence in (1, 2):
                    delay += 12  # systemic late-sync hub
                previous += timedelta(hours=delay, minutes=rng.randrange(50))
            event_time = previous
            ingest_time = event_time + timedelta(minutes=rng.randrange(5, 50))
            if rng.random() < 0.05:
                ingest_time += timedelta(hours=rng.randint(8, 30))
            event = {
                "scan_id": f"SCN{n:08d}{sequence:02d}", "parcel_id": parcel_id,
                "seller_id": seller_id, "event_type": event_type,
                "event_time": iso(event_time), "ingest_time": iso(ingest_time),
                "hub_id": origin if sequence < 3 else destination,
                "origin_hub": origin, "destination_hub": destination,
                "lane_id": f"{origin}_{destination}", "phone_number": f"+9198{n % 100000000:08d}",
                "sla_hours": sla_hours, "sequence_hint": sequence,
            }
            events.append(event)
            if rng.random() < 0.02:
                duplicate = event.copy(); duplicate["ingest_time"] = iso(ingest_time + timedelta(minutes=3)); events.append(duplicate)
        # Arrival order is deliberately unreliable, not just source event time.
    rng.shuffle(events)
    grouped: dict[tuple[str, str], list[dict]] = {}
    for event in events:
        dt = event["ingest_time"][:10]
        hour = event["ingest_time"][11:13]
        grouped.setdefault((dt, hour), []).append(event)
    for (dt, hour), batch in grouped.items():
        write_jsonl(output / "landing" / f"dt={dt}" / f"hour={hour}" / "scan_events.jsonl", batch)
    seller_path = output / "landing" / "seller_master.csv"
    seller_path.parent.mkdir(parents=True, exist_ok=True)
    with seller_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["seller_id", "seller_name", "tier"])
        writer.writeheader(); writer.writerows(sellers.values())
    return {"parcels": parcels, "raw_events": len(events), "batches": len(grouped), "sellers": len(sellers)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate partitioned parcel scan batches")
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--parcels", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(generate(args.output, args.parcels, args.seed))
