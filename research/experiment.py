"""Disposable experiment roots. Never writes outside the assigned run directory."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run(repo_root: Path, name: str) -> Path:
    runs = repo_root / "research" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    rid = utc().replace(":", "").replace("-", "")[:15] + "_" + uuid.uuid4().hex[:8] + "_" + name
    root = runs / rid
    root.mkdir(parents=False)
    (root / "artifacts").mkdir()
    meta = {
        "schema": "aetheria_experiment_v1",
        "run_id": rid,
        "created_at": utc(),
        "network_access": False,
        "status": "created",
    }
    _atomic_write(root / "experiment.json", meta)
    return root


def _atomic_write(path: Path, obj: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def record_candidate(run_root: Path, candidate: Dict[str, Any]) -> Path:
    cid = candidate["candidate_id"]
    path = run_root / f"candidate_{cid}.json"
    _atomic_write(path, candidate)
    return path
