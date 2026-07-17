from __future__ import annotations

import sqlite3
from pathlib import Path

from pipeline.io import read_jsonl


def load(data_root: Path, expected_delivered: int) -> dict:
    facts = read_jsonl(data_root / "gold" / "sla_facts.jsonl")
    actual_delivered = sum(row["status"] == "DELIVERED" for row in facts)
    if actual_delivered != expected_delivered:
        raise RuntimeError(f"CONTROL TOTAL FAILED: gold={expected_delivered}, sql_source={actual_delivered}")
    db_path = data_root / "serving" / "sla_mart.db"; db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.executescript("""DROP TABLE IF EXISTS fct_sla; CREATE TABLE fct_sla (
          parcel_id TEXT PRIMARY KEY, lane_id TEXT, origin_hub TEXT, destination_hub TEXT, pickup_date TEXT,
          status TEXT, promised_hours INTEGER, actual_hours REAL, breach_flag INTEGER, exception_reason TEXT);
          CREATE INDEX idx_fct_sla_lane_date ON fct_sla(lane_id, pickup_date);""")
        con.executemany("INSERT INTO fct_sla VALUES (:parcel_id,:lane_id,:origin_hub,:destination_hub,:pickup_date,:status,:promised_hours,:actual_hours,:breach_flag,:exception_reason)", facts)
        rows = con.execute("SELECT COUNT(*), SUM(status='DELIVERED'), SUM(breach_flag) FROM fct_sla").fetchone()
    return {"sql_rows": rows[0], "sql_delivered": rows[1] or 0, "sql_breaches": rows[2] or 0}
