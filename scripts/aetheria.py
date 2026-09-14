#!/usr/bin/env python3
"""Standalone Aetheria control-plane launcher.

One entry: this file. Root is the directory that contains scripts/ and measurements/.
Does not start companion, Ollama, or cloud APIs.

  python -u scripts/aetheria.py status|stop|start|resume|recover|diagnose
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _banner() -> None:
    print(f"aetheria control-plane")
    print(f"  root:       {ROOT}")
    print(f"  python:     {sys.executable}")
    print(f"  state_dir:  {ROOT / 'measurements'}")
    print(f"  backend:    none (control plane only; no model/API)")
    print(f"  config:     measurements/*.json + env AETHERIA_* (see docs/STANDALONE_PRODUCT.md)")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "scripts"))
    if not argv or argv[0] in ("-h", "--help", "help"):
        _banner()
        print("commands: init | status | stop | start | resume | recover | diagnose")
        return 0
    cmd = argv[0]
    rest = argv[1:]
    _banner()
    if cmd == "init":
        (ROOT / "measurements").mkdir(parents=True, exist_ok=True)
        (ROOT / "research" / "runs").mkdir(parents=True, exist_ok=True)
        print("initialized measurements/ and research/runs/")
        return 0
    import plant_control as pc

    if cmd == "status":
        return pc.cmd_status(as_json=("--json" in rest))
    if cmd == "diagnose":
        return pc.cmd_status(as_json=True)
    if cmd == "stop":
        reason = "operator_stop"
        if "--reason" in rest:
            i = rest.index("--reason")
            if i + 1 < len(rest):
                reason = rest[i + 1]
        return pc.cmd_stop(reason=reason)
    if cmd in ("start", "resume", "recover"):
        return pc.resume(
            with_watchdog=True,
            cycles=None,
            interval_min=None,
            max_ticks=None,
            continue_tick=("fresh-segment" not in rest and "--fresh-segment" not in rest),
        )
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
