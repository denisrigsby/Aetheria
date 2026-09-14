"""VS02: MODE strict→lenient. Distinct from LABEL alpha→beta."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from research.slices.pipeline import run_mission

HERE = Path(__file__).resolve().parent


def run_vs02(repo: Path, **kw: Any) -> Dict[str, Any]:
    req = json.loads((HERE / "request.json").read_text(encoding="utf-8"))
    extra = kw.pop("request_override", None)
    if extra:
        req.update(extra)
    return run_mission(
        repo,
        name="vs02",
        fixture_src=HERE / "fixture",
        request=req,
        fixture_version="vs02-v1",
        baseline_commit=kw.pop("baseline_commit", "147eb60"),
        **kw,
    )
