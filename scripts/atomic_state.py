"""Atomic JSON write helper for measurements protocol."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Set


def atomic_write_json(path: Path, doc: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    raw = json.dumps(doc, indent=2) + "\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


def read_json_strict(path: Path, *, allowed_schemas: Set[str] | Iterable[str]) -> Dict[str, Any]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("not an object")
    allowed = set(allowed_schemas)
    schema = doc.get("schema")
    if schema not in allowed:
        raise ValueError(f"unknown schema: {schema!r}")
    return doc
