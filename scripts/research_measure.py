#!/usr/bin/env python3
"""Measure worker scaling and write research/config/windows-local.json. No plant, no network."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from atomic_state import atomic_write_json  # noqa: E402

from research.compare import ECOLOGIES, run_comparison  # noqa: E402
from research.measure import measure_worker_count, recommend_profile, utc  # noqa: E402


def main() -> int:
    counts = [1, 2, 4, 8]
    blocks = []
    for n in counts:
        print("measure n=", n, flush=True)
        blocks.append(measure_worker_count(ROOT, n, repeats=2))
    # try one higher if 8 was clean
    if all(r.get("survivors") == 0 for r in blocks[-1]["runs"]):
        print("measure n=16", flush=True)
        blocks.append(measure_worker_count(ROOT, 16, repeats=1))
    profile = recommend_profile(blocks)
    cfg = ROOT / "research" / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    outp = cfg / "windows-local.json"
    atomic_write_json(outp, profile)
    meas_path = cfg / "windows-local.measurement.json"
    atomic_write_json(
        meas_path,
        {
            "schema": "aetheria_measurement_v1",
            "created_at": utc(),
            "blocks": blocks,
            "profile": profile,
        },
    )
    print("profile", outp)
    print("measurement", meas_path)
    run = run_comparison(ROOT, profile)
    print("comparison", run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
