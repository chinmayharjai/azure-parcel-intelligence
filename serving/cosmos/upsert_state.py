from __future__ import annotations

from pathlib import Path
from pipeline.io import write_jsonl
from pipeline.transform import latest_states


def upsert(data_root: Path, events: list[dict]) -> int:
    return write_jsonl(data_root / "cosmos" / "parcel_state.jsonl", latest_states(events))
