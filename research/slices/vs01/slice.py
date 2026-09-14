"""VS01 wrapper around the shared pipeline."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from research.slices.pipeline import PathEscape, TamperRejected, recover_run, run_mission

SLICE_DIR = Path(__file__).resolve().parent
FIXTURE_SRC = SLICE_DIR / "fixture"
REQUEST_PATH = SLICE_DIR / "request.json"


def run_slice(repo: Path, **kw: Any) -> Dict[str, Any]:
    req = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    extra = kw.pop("request_override", None)
    if extra:
        req.update(extra)
    if "goal" in kw:
        req["goal"] = kw.pop("goal")
    return run_mission(
        repo,
        name="vs01",
        fixture_src=FIXTURE_SRC,
        request=req,
        fixture_version="vs01-v1",
        baseline_commit=kw.pop("baseline_commit", "147eb60"),
        **kw,
    )
