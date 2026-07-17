from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from quality.dq_checks import run as dq_run
from serving.azure_sql.load_mart import load as load_mart
from serving.cosmos.upsert_state import upsert
from simulator.scan_events import generate
from pipeline.transform import bronze, gold, silver


def main(data_root: Path, parcels: int, seed: int, keep_data: bool) -> dict:
    if data_root.exists() and not keep_data: shutil.rmtree(data_root)
    generated = generate(data_root, parcels, seed)
    bronze_rows = bronze(data_root)
    silver_rows, dedup_removed = silver(data_root)
    gold_metrics = gold(data_root, silver_rows)
    dq_metrics = dq_run(data_root, expected_parcels=parcels)
    sql_metrics = load_mart(data_root, gold_metrics["gold_delivered"])
    cosmos_docs = upsert(data_root, silver_rows)
    summary = {"simulator": generated, "bronze_rows": bronze_rows, "silver_rows": len(silver_rows), "dedup_removed": dedup_removed, "gold": gold_metrics, "quality": dq_metrics, "sql_mart": sql_metrics, "cosmos_documents": cosmos_docs, "control_total_status": "PASSED"}
    (data_root / "demo_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the complete local parcel intelligence demo")
    parser.add_argument("--parcels", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--keep-data", action="store_true")
    args = parser.parse_args()
    print(json.dumps(main(args.data_root, args.parcels, args.seed, args.keep_data), indent=2))
