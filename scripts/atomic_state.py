"""Atomic replace for public control-plane state documents.

One replace body: same-directory temporary file, flush, fsync, then
``os.replace`` onto the target name. JSON object writers call
``atomic_write_json``. Full-file text rewrites (gate-A log trim, raw copies
of an existing JSON file) call ``_atomic_replace_text``, which is that same
body — not a second writer.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Set


def atomic_write_json(path: Path, doc: Dict[str, Any], *, default: Any = None) -> None:
    if not isinstance(doc, dict):
        raise TypeError("state document must be a JSON object")
    raw = json.dumps(doc, indent=2, default=default) + "\n"
    _atomic_replace_text(path, raw)


def _atomic_replace_text(path: Path, raw: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
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
