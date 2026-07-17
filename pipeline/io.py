from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_jsonl_tree(root: Path) -> list[dict]:
    return [record for path in root.rglob("*.jsonl") for record in read_jsonl(path)]
