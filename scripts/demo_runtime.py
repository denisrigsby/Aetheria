#!/usr/bin/env python3
"""Mock cycle body for the public control plane.

No LLM, no private logic, no network. Honors AETHERIA_NUM_CYCLES and writes
the same contract the supervisor already reads:

  measurements/lh_probe_summary_latest.json   (lh_probe_summary_v1)
  measurements/demo_heartbeat.json
  measurements/demo_checkpoint.json
  measurements/demo_green_ticks.jsonl
  stdout: CYCLE n/N COMPLETE

Sleep per cycle: AETHERIA_DEMO_SLEEP_S (default 2). Tests use 0.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AETHERIA_ROOT") or Path(__file__).resolve().parents[1])
MEAS = ROOT / "measurements"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _cycles() -> int:
    for k in ("AETHERIA_NUM_CYCLES", "NUM_CYCLES"):
        v = (os.environ.get(k) or "").strip()
        if v.isdigit() and int(v) > 0:
            return int(v)
    return 3


def _sleep_s() -> float:
    try:
        return max(0.0, float(os.environ.get("AETHERIA_DEMO_SLEEP_S", "2")))
    except Exception:
        return 2.0


def run(cycles: int | None = None) -> dict:
    n = int(cycles or _cycles())
    n = max(1, n)
    started = utc()
    mom: list[float] = []
    hb = MEAS / "demo_heartbeat.json"
    ck = MEAS / "demo_checkpoint.json"
    green = MEAS / "demo_green_ticks.jsonl"
    summary = MEAS / "lh_probe_summary_latest.json"
    MEAS.mkdir(parents=True, exist_ok=True)
    if green.exists():
        pass
    print(f"[demo_runtime] start cycles={n} root={ROOT}", flush=True)
    _write(
        hb,
        {"schema": "aetheria_demo_heartbeat_v1", "alive": True, "cycle": 0, "n": n, "ts": utc()},
    )
    for i in range(1, n + 1):
        if _sleep_s() > 0:
            time.sleep(_sleep_s())
        pct = int(round(100.0 * i / n))
        mom.append(100.0 + i)
        _write(
            hb,
            {
                "schema": "aetheria_demo_heartbeat_v1",
                "alive": True,
                "cycle": i,
                "n": n,
                "ts": utc(),
            },
        )
        _write(
            ck,
            {
                "schema": "aetheria_demo_checkpoint_v1",
                "progress": f"{pct}%",
                "status": "simulating",
                "cycle": i,
                "n": n,
                "ts": utc(),
            },
        )
        with green.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps({"ts": utc(), "cycle": i, "n": n, "ok": True, "kind": "demo_green"})
                + "\n"
            )
        print(f"CYCLE {i}/{n} COMPLETE", flush=True)
    rec = {
        "schema": "lh_probe_summary_v1",
        "ok": True,
        "cycles_requested": n,
        "cycles_complete": n,
        "final_mom": mom[-1] if mom else 0.0,
        "mom_series": mom,
        "exit_code": 0,
        "started_at": started,
        "finished_at": utc(),
        "error": None,
        "error_class": None,
        "log_path": None,
        "runner": "demo_runtime",
        "notes": ["mock_cycle_no_llm"],
    }
    _write(summary, rec)
    _write(
        hb,
        {
            "schema": "aetheria_demo_heartbeat_v1",
            "alive": False,
            "cycle": n,
            "n": n,
            "ts": utc(),
            "status": "complete",
        },
    )
    print(f"[demo_runtime] stop ok cycles_complete={n}", flush=True)
    return rec


def main() -> int:
    rec = run()
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
