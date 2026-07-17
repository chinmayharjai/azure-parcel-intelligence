from __future__ import annotations

import sqlite3
from pathlib import Path

if __name__ == "__main__":
    with sqlite3.connect(Path("data/serving/sla_mart.db")) as con:
        for row in con.execute("SELECT lane_id, COUNT(*) parcels, ROUND(AVG(breach_flag)*100,2) breach_pct FROM fct_sla GROUP BY lane_id ORDER BY parcels DESC LIMIT 10"):
            print(row)
