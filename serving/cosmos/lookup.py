from __future__ import annotations

import argparse
import json
from pathlib import Path


def lookup(parcel_id: str, data_root: Path = Path("data")) -> dict | None:
    with (data_root / "cosmos" / "parcel_state.jsonl").open(encoding="utf-8") as handle:
        return next((json.loads(line) for line in handle if json.loads(line)["parcel_id"] == parcel_id), None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cosmos-style parcel tracking point read")
    parser.add_argument("parcel_id")
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    args = parser.parse_args(); print(json.dumps(lookup(args.parcel_id, args.data_root), indent=2))
