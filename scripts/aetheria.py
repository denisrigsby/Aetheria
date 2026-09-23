#!/usr/bin/env python3
"""Standalone Aetheria control-plane launcher.

One entry: this file. Root is the directory that contains scripts/ and measurements/.
Does not start companion, Ollama, or cloud APIs.

  python -u scripts/aetheria.py status|stop|start|resume|recover|diagnose|demo
  python -m aetheria demo --cycles 3
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cmd_demo(cycles: int = 3) -> int:
    """Supervisor + mock runtime. No LLM, no private cycle body, no plant start."""
    print("Verify the Supervisor — mock lifecycle (no LLM, no GPU, no private keys)")
    print(f"  cycles: {cycles}")
    os.environ.setdefault("AETHERIA_PROBE_TIMEOUT_S", "60")
    os.environ.setdefault("AETHERIA_DEMO_SLEEP_S", "2")
    os.environ["AETHERIA_DEMO"] = "1"
    import long_horizon_supervisor as lh

    probe = ROOT / "scripts" / "demo_runtime.py"
    rec = lh.run_probe_cycles(cycles, tick=0, probe_script=probe)
    summary = ROOT / "measurements" / "lh_probe_summary_latest.json"
    hb = ROOT / "measurements" / "demo_heartbeat.json"
    ck = ROOT / "measurements" / "demo_checkpoint.json"
    print(f"  supervisor_ok: {rec.get('ok')}  error={rec.get('error')}")
    for label, p in (("summary", summary), ("heartbeat", hb), ("checkpoint", ck)):
        if p.is_file():
            print(f"  {label}: {p.relative_to(ROOT)}")
            print("   ", p.read_text(encoding="utf-8").strip().replace("\n", "\n    ")[:800])
    if rec.get("ok"):
        print("DEMO LIFECYCLE PASS — heartbeat, checkpoint, contract summary.")
        return 0
    print("DEMO LIFECYCLE FAIL", file=sys.stderr)
    return 1


def _banner() -> None:
    print(f"aetheria control-plane")
    print(f"  root:       {ROOT}")
    print(f"  python:     {sys.executable}")
    print(f"  state_dir:  {ROOT / 'measurements'}")
    print(f"  backend:    none (control plane only; no model/API)")
    print(f"  config:     measurements/*.json + env AETHERIA_* (see docs/STANDALONE_PRODUCT.md)")


def _take_opt(rest: list[str], flag: str) -> tuple[str | None, list[str]]:
    if flag not in rest:
        return None, rest
    i = rest.index(flag)
    if i + 1 >= len(rest) or rest[i + 1].startswith("-"):
        raise ValueError(f"{flag} needs a value")
    val = rest[i + 1]
    return val, rest[:i] + rest[i + 2 :]


def _start_options(rest: list[str]) -> dict:
    """Flags shared with plant_control start/resume. Unknown flags fail closed."""
    cycles_s, rest = _take_opt(rest, "--cycles")
    interval_s, rest = _take_opt(rest, "--interval-min")
    max_ticks_s, rest = _take_opt(rest, "--max-ticks")
    fresh = False
    kept: list[str] = []
    for item in rest:
        if item in ("--fresh-segment", "fresh-segment"):
            fresh = True
        else:
            kept.append(item)
    if kept:
        raise ValueError("unknown start/resume flags: " + " ".join(kept))

    def _int(raw: str | None, flag: str) -> int | None:
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError as e:
            raise ValueError(f"{flag} needs an integer") from e

    def _float(raw: str | None, flag: str) -> float | None:
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError as e:
            raise ValueError(f"{flag} needs a number") from e

    return {
        "cycles": _int(cycles_s, "--cycles"),
        "interval_min": _float(interval_s, "--interval-min"),
        "max_ticks": _int(max_ticks_s, "--max-ticks"),
        "continue_tick": not fresh,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "scripts"))
    if not argv or argv[0] in ("-h", "--help", "help"):
        _banner()
        print("commands: init | status | stop | start | resume | recover | diagnose | demo")
        print("start|resume flags: --cycles N --interval-min N --max-ticks N --fresh-segment")
        return 0
    cmd = argv[0]
    rest = argv[1:]
    _banner()
    if cmd == "demo":
        cycles = 3
        if "--cycles" in rest:
            i = rest.index("--cycles")
            if i + 1 < len(rest):
                try:
                    cycles = max(1, int(rest[i + 1]))
                except ValueError:
                    cycles = 3
        return cmd_demo(cycles)
    if cmd == "init":
        # Creates empty state dirs only. Does not start the plant, watchdog, or probes.
        (ROOT / "measurements").mkdir(parents=True, exist_ok=True)
        (ROOT / "research" / "runs").mkdir(parents=True, exist_ok=True)
        print("initialized measurements/ and research/runs/ (no processes started)")
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
    if cmd == "recover":
        return pc.cmd_recover()
    if cmd in ("start", "resume"):
        try:
            opts = _start_options(rest)
        except ValueError as e:
            print(f"FAIL: {e}", file=sys.stderr)
            return 2
        return pc.resume(
            with_watchdog=True,
            cycles=opts["cycles"],
            interval_min=opts["interval_min"],
            max_ticks=opts["max_ticks"],
            continue_tick=opts["continue_tick"],
        )
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
