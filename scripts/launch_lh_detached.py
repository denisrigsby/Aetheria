#!/usr/bin/env python3
"""
launch_lh_detached.py — Reliable detached long-horizon launch (no PowerShell wait hang).

Proven fix for: plant_control resume / WD relaunch timing out 180s while
`Start-Process python` (Store alias) never returns a live supervisor.

Uses absolute Python when possible (Python310, then sys.executable).
Never parents residual/G4. Conservation env defaults.

Usage:
  python -u scripts/launch_lh_detached.py
  python -u scripts/launch_lh_detached.py --continue-tick --max-ticks 48
  python -u scripts/launch_lh_detached.py --clear-latches
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from lh_process_identity import pid_exists  # noqa: E402

MEAS = ROOT / "measurements"
LOGS = ROOT / "logs"
LH_PID = MEAS / "long_horizon.pid"
LH_STOP = MEAS / "long_horizon_STOP"
STANDBY = MEAS / "long_horizon_STANDBY.json"
MANUAL = MEAS / "long_horizon_MANUAL_START.json"


def resolve_python() -> str:
    env = (os.environ.get("AETHERIA_PYTHON") or "").strip()
    candidates = [
        env,
        r"C:\Program Files\Python310\python.exe",
        r"C:\Program Files\Python311\python.exe",
        str(Path(sys.executable).resolve()) if sys.executable else "",
        str(ROOT / ".venv" / "Scripts" / "python.exe"),
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return "python"


def pid_alive(pid: Optional[int]) -> bool:
    """Process-table presence for launch polling. Not an identity check and not a kill."""
    if not pid:
        return False
    try:
        return pid_exists(pid)
    except Exception:
        return False


def read_pid() -> Optional[int]:
    try:
        if not LH_PID.exists():
            return None
        t = LH_PID.read_text(encoding="utf-8").strip()
        return int(t) if t else None
    except Exception:
        return None


def conservation_env() -> None:
    os.environ.setdefault("AETHERIA_LIGHT_MANAGE", "1")
    os.environ.setdefault("AETHERIA_SKIP_FINAL_RECON", "1")
    os.environ.setdefault("AETHERIA_HEAVY_HEALTH_CYCLES", "6,12")
    os.environ.setdefault("AETHERIA_META_RECON", "0")
    if (MEAS / "red_helix_c2.enable").exists():
        os.environ["AETHERIA_RED_HELIX"] = "1"
    if (MEAS / "red_helix_c2_actuate.enable").exists():
        os.environ["AETHERIA_RED_HELIX_ACTUATE"] = "1"


def supervisor_argv(
    py: str,
    script: str,
    *,
    cycles: int,
    interval_min: float,
    max_ticks: int,
    backup_every: int,
    continue_tick: bool,
    once: bool,
    ignore_standby: bool,
) -> List[str]:
    """Argv the supervisor parser accepts. No flags outside that contract."""
    args: List[str] = [
        py,
        "-u",
        script,
        "--cycles",
        str(int(cycles)),
        "--interval-min",
        str(float(interval_min)),
        "--max-ticks",
        str(int(max_ticks)),
        "--backup-every",
        str(int(backup_every)),
    ]
    if continue_tick:
        args.append("--continue-tick")
    if once:
        args.append("--once")
    if ignore_standby:
        args.append("--ignore-standby")
    return args


def launch_lh_detached(
    *,
    cycles: int = 2,
    interval_min: float = 30.0,
    max_ticks: int = 48,
    backup_every: int = 4,
    continue_tick: bool = True,
    once: bool = False,
    clear_latches: bool = False,
    stop_old: bool = True,
    poll_s: float = 90.0,
) -> Tuple[bool, str, Optional[int]]:
    """
    Detach long_horizon_supervisor. Returns (ok, detail, pid).
    """
    LOGS.mkdir(parents=True, exist_ok=True)
    MEAS.mkdir(parents=True, exist_ok=True)
    conservation_env()

    if not clear_latches:
        if STANDBY.exists():
            return False, "standby_active — use plant_control resume or --clear-latches", None
        if MANUAL.exists():
            try:
                import json

                m = json.loads(MANUAL.read_text(encoding="utf-8"))
                if m.get("active", True):
                    return False, "manual_start_required — plant_control start or --clear-latches", None
            except Exception:
                return False, "manual_start_latch_present", None

    if clear_latches:
        for p in (STANDBY, MANUAL, LH_STOP, MEAS / "watchdog_STOP"):
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass

    if LH_STOP.exists():
        try:
            LH_STOP.unlink()
        except Exception:
            pass

    if stop_old:
        old = read_pid()
        if old and pid_alive(old):
            try:
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/PID", str(old), "/F"],
                        capture_output=True,
                        timeout=30,
                    )
                else:
                    os.kill(old, 15)
            except Exception:
                pass
            time.sleep(1.0)

    py = resolve_python()
    args = supervisor_argv(
        py,
        str(ROOT / "scripts" / "long_horizon_supervisor.py"),
        cycles=cycles,
        interval_min=interval_min,
        max_ticks=max_ticks,
        backup_every=backup_every,
        continue_tick=continue_tick,
        once=once,
        ignore_standby=clear_latches,
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = LOGS / f"long_horizon_launch_{ts}.log"
    err = LOGS / f"long_horizon_launch_{ts}.log.err"

    flags = 0
    if sys.platform == "win32":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        # CREATE_NO_WINDOW if available
        flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

    try:
        with open(out, "a", encoding="utf-8") as fo, open(err, "a", encoding="utf-8") as fe:
            proc = subprocess.Popen(
                args,
                cwd=str(ROOT),
                stdout=fo,
                stderr=fe,
                stdin=subprocess.DEVNULL,
                creationflags=flags if sys.platform == "win32" else 0,
                start_new_session=(sys.platform != "win32"),
                env=os.environ.copy(),
            )
    except Exception as e:
        return False, f"popen_failed: {type(e).__name__}: {e}", None

    # Poll pid file (supervisor writes it); also accept Popen pid if file lags
    deadline = time.time() + max(15.0, float(poll_s))
    last_pf: Optional[int] = None
    while time.time() < deadline:
        last_pf = read_pid()
        if last_pf and pid_alive(last_pf):
            detail = f"ok pid={last_pf} py={py} continue_tick={continue_tick} log={out.name}"
            return True, detail, last_pf
        if proc.pid and pid_alive(proc.pid) and (last_pf is None or last_pf == proc.pid):
            # supervisor may still be writing state
            time.sleep(0.5)
            last_pf = read_pid()
            if last_pf and pid_alive(last_pf):
                return True, f"ok pid={last_pf} py={py} log={out.name}", last_pf
        # if popen died immediately
        if proc.poll() is not None:
            tail = ""
            try:
                tail = err.read_text(encoding="utf-8", errors="replace")[-400:]
            except Exception:
                pass
            return False, f"supervisor_exited_early code={proc.returncode} {tail}", None
        time.sleep(1.0)

    last_pf = read_pid()
    if last_pf and pid_alive(last_pf):
        return True, f"ok pid={last_pf} late_poll py={py}", last_pf
    if proc.pid and pid_alive(proc.pid):
        return True, f"ok popen_pid={proc.pid} pidfile={last_pf} py={py}", int(proc.pid)
    return False, f"pid_not_alive after {poll_s}s popen={proc.pid} pidfile={last_pf} py={py}", last_pf


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Detach long-horizon supervisor reliably")
    ap.add_argument("--cycles", type=int, default=2)
    ap.add_argument("--interval-min", type=float, default=30.0)
    ap.add_argument("--max-ticks", type=int, default=48)
    ap.add_argument("--backup-every", type=int, default=4)
    ap.add_argument("--continue-tick", action="store_true", default=True)
    ap.add_argument("--no-continue-tick", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--clear-latches", action="store_true")
    ap.add_argument("--poll-s", type=float, default=45.0)
    args = ap.parse_args(argv)
    cont = not args.no_continue_tick
    ok, detail, pid = launch_lh_detached(
        cycles=args.cycles,
        interval_min=args.interval_min,
        max_ticks=args.max_ticks,
        backup_every=args.backup_every,
        continue_tick=cont,
        once=args.once,
        clear_latches=args.clear_latches,
        poll_s=args.poll_s,
    )
    print(detail)
    if ok:
        print(f"LONG_HORIZON_PID={pid}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
