#!/usr/bin/env python3
"""
lh_watchdog.py — External guardian for long_horizon_supervisor.

Runs detached. Does NOT attach to Grok chat.
- Detects dead PID, stale heartbeat, stuck running_tick, completed_max_ticks
- Relaunches launch_long_horizon.ps1 (or python supervisor) when needed
- Writes measurements/watchdog_status.json always
- Writes measurements/NOTIFY_USER.md only on events that need human attention
- Never wipes registry; never merges living; never kills a healthy supervisor

Stop:
  echo stop > measurements/watchdog_STOP

Usage:
  python -u scripts/lh_watchdog.py --interval-sec 60
  # detached:
  powershell -File scripts/launch_lh_watchdog.ps1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from atomic_state import _atomic_replace_text, atomic_write_json  # noqa: E402
from lh_process_identity import (  # noqa: E402
    ROLE_SUPERVISOR,
    kill_if_verified,
    pid_exists,
    verified_role,
)

MEAS = ROOT / "measurements"
STATE_PATH = MEAS / "long_horizon_state.json"
PID_PATH = MEAS / "long_horizon.pid"
LH_STOP = MEAS / "long_horizon_STOP"
LH_STANDBY = MEAS / "long_horizon_STANDBY.json"
RH_RELAUNCH_REQ = MEAS / "red_helix_relaunch_request.json"
WD_STOP = MEAS / "watchdog_STOP"
WD_PID = MEAS / "watchdog.pid"
WD_STATUS = MEAS / "watchdog_status.json"
NOTIFY = MEAS / "NOTIFY_USER.md"
WD_LOG = ROOT / "logs" / f"lh_watchdog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def standby_active() -> bool:
    """Durable operator pause — survives reboot; blocks relaunch until plant_control resume."""
    if not LH_STANDBY.exists():
        return False
    try:
        s = json.loads(LH_STANDBY.read_text(encoding="utf-8"))
        return bool(s.get("active", True))
    except Exception:
        # Unreadable standby file: fail closed (do not relaunch)
        return True


def _run_policy():
    import importlib.util

    p = ROOT / "scripts" / "lh_run_policy.py"
    spec = importlib.util.spec_from_file_location("lh_run_policy", p)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def manual_start_required() -> bool:
    mod = _run_policy()
    if mod is None:
        return standby_active()
    return bool(mod.manual_start_required())


# Thresholds (minutes)
HEARTBEAT_STALE_MIN = 5.0          # idle should heartbeat ~30s
RUNNING_STUCK_MIN = 25.0           # 2-cycle probe soft wall ~10–15m; 25m = stuck
POST_EXIT_RELAUNCH_DELAY_S = 15


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    try:
        WD_LOG.parent.mkdir(parents=True, exist_ok=True)
        with WD_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def write_json(path: Path, obj: dict) -> None:
    atomic_write_json(path, obj, default=str)


def read_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"_error": "unreadable_state"}


def pid_alive(pid: Any) -> bool:
    """Process-table presence. Not an identity check and not a kill."""
    try:
        return pid_exists(pid)
    except Exception:
        try:
            p = int(pid)
        except Exception:
            return False
        if p <= 0:
            return False
        try:
            os.kill(p, 0)
            return True
        except Exception:
            return False


def read_pid_file() -> Optional[int]:
    if not PID_PATH.exists():
        return None
    try:
        t = PID_PATH.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        return int(t)
    except Exception:
        return None


def parse_ts(s: Any) -> Optional[datetime]:
    if not s:
        return None
    try:
        t = str(s).replace("Z", "+00:00")
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def age_min(ts: Any) -> Optional[float]:
    dt = parse_ts(ts)
    if not dt:
        return None
    return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 60.0


def notify(title: str, body: str, level: str = "info") -> None:
    """User-facing notify — only when something matters."""
    MEAS.mkdir(exist_ok=True)
    stamp = utc_now()
    block = f"""# Aetheria notify — {title}

- **When:** {stamp}
- **Level:** {level}

{body}

---
_Auto-written by lh_watchdog. Safe to ignore if already handled. Delete this file to clear._
"""
    # Append if exists so we don't clobber history of issues
    prev = ""
    if NOTIFY.exists():
        try:
            prev = NOTIFY.read_text(encoding="utf-8")
        except Exception:
            prev = ""
    NOTIFY.write_text(block + "\n" + prev[:8000], encoding="utf-8")
    log(f"NOTIFY [{level}] {title}")
    try:
        from living.aetheria_canon import write_hope_status

        write_hope_status(
            {
                "notify": {
                    "title": title,
                    "level": level,
                    "ts": stamp,
                    "file": str(NOTIFY),
                }
            }
        )
    except Exception:
        pass


def relaunch_lh(cycles: int = 2, interval_min: float = 30.0, max_ticks: int = 0) -> Tuple[bool, str]:
    """Relaunch long horizon. Success = long_horizon.pid alive (P1), not just PS return.

    Default max_ticks=48 rolling segment (P2), not single-PID 200 heroics.
    """
    if standby_active():
        return False, "standby_active_not_relaunching"
    if manual_start_required():
        return False, "manual_start_required_not_relaunching"
    if LH_STOP.exists():
        return False, "lh_stop_file_present_not_relaunching"
    # P2: rolling segment default — direct detached Python (no PS 180s hang)
    mt = max_ticks if max_ticks > 0 else 48
    try:
        import importlib.util

        lp = ROOT / "scripts" / "launch_lh_detached.py"
        spec = importlib.util.spec_from_file_location("launch_lh_detached", lp)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        ok, detail, pid = mod.launch_lh_detached(
            cycles=int(cycles),
            interval_min=float(interval_min),
            max_ticks=int(mt),
            continue_tick=True,
            clear_latches=False,
            stop_old=True,
            poll_s=90.0,
        )
        log(f"relaunch detached ok={ok} detail={detail[:400]}")
        if ok:
            return True, detail[:500]
        return False, detail[:500]
    except Exception as e:
        out = f"{type(e).__name__}: {e}"
        log(f"relaunch exception: {out}")
        return False, out[:400]


def diagnose() -> Dict[str, Any]:
    state = read_state()
    pid = state.get("pid") or read_pid_file()
    alive = bool(pid) and verified_role(pid, ROLE_SUPERVISOR)
    status = state.get("status")
    hb_age = age_min(state.get("heartbeat_at") or state.get("updated_at"))
    tick_age = age_min(state.get("last_tick_finished"))
    last_ok = state.get("last_ok")
    action = "none"
    reason = "healthy"

    # Power-flap safe default: no auto-relaunch unless AUTORUN opt-in
    pol = _run_policy()

    if standby_active():
        action = "none"
        reason = "user_standby"
    elif manual_start_required():
        action = "none"
        reason = "manual_start_required"
    elif LH_STOP.exists():
        action = "none"
        reason = "user_stop_file"
    elif RH_RELAUNCH_REQ.exists() and alive and not manual_start_required():
        # C2 actuator only while intentionally running (not during manual latch)
        action = "kill_relaunch"
        reason = "red_helix_coherence_debt"
    elif not alive:
        # Unexpected death (crash / power loss): latch manual start; do not thrash relaunch
        if status in ("completed_max_ticks", "completed_once"):
            action = "none"
            reason = f"exited_{status}"
            if pol is not None:
                try:
                    pol.require_manual_start(
                        reason=f"segment_ended:{status}",
                        source="watchdog",
                    )
                except Exception:
                    pass
        elif status in ("stopped_by_file", "standby") or LH_STOP.exists() or standby_active():
            action = "none"
            reason = f"exited_{status}"
        else:
            action = "none"
            reason = "pid_dead_manual_start"
            if pol is not None:
                try:
                    pol.require_manual_start(
                        reason="unexpected_process_death_crash_or_power",
                        source="watchdog",
                        extra={
                            "last_status": status,
                            "last_ok": last_ok,
                            "tick": state.get("tick"),
                        },
                    )
                except Exception:
                    pass
            try:
                notify(
                    "Plant stopped — manual start required",
                    f"LH process not alive (status={status}).\n\n"
                    "Auto-relaunch is **off** (power-flap safe).\n"
                    "When power is stable: `python scripts/plant_control.py resume --with-watchdog`\n"
                    "or companion chat: `/start`\n\n"
                    "Opt-in thrash relaunch: measurements/long_horizon_AUTORUN.enable",
                    level="warn",
                )
            except Exception:
                pass
    elif status == "running_tick" and hb_age is not None and hb_age > RUNNING_STUCK_MIN:
        # Machine is up but tick stuck — still no relaunch if manual latch; else recover
        if manual_start_required():
            action = "none"
            reason = "stuck_but_manual_latch"
        else:
            action = "kill_relaunch"
            reason = f"running_tick_stuck_{hb_age:.1f}m"
    elif status == "idle_between_ticks" and hb_age is not None and hb_age > HEARTBEAT_STALE_MIN:
        if manual_start_required():
            action = "none"
            reason = "stale_but_manual_latch"
        else:
            # Stale heartbeat while "alive" may be false positive after power blip — prefer manual
            action = "none"
            reason = "heartbeat_stale_manual_preferred"
            if pol is not None:
                try:
                    pol.require_manual_start(
                        reason=f"heartbeat_stale_{hb_age:.1f}m",
                        source="watchdog",
                    )
                except Exception:
                    pass
    elif last_ok is False and status == "degraded":
        action = "notify_only"
        reason = "last_tick_failed_alive"
    else:
        action = "none"
        reason = "healthy"

    return {
        "ts": utc_now(),
        "pid": pid,
        "alive": alive,
        "status": status,
        "tick": state.get("tick"),
        "last_ok": last_ok,
        "last_final_mom": state.get("last_final_mom"),
        "hb_age_min": hb_age,
        "tick_age_min": tick_age,
        "action": action,
        "reason": reason,
        "interval_min": state.get("interval_min"),
        "max_ticks": state.get("max_ticks"),
        "lh_stop": LH_STOP.exists(),
        "standby": standby_active(),
        "manual_start": manual_start_required(),
    }


def kill_pid(pid: Any) -> None:
    r = kill_if_verified(pid, ROLE_SUPERVISOR, tree=True)
    log(f"kill supervisor pid={pid} {r.get('reason')}")


def apply_action(diag: Dict[str, Any]) -> Dict[str, Any]:
    action = diag.get("action")
    result = {"action": action, "ok": True, "detail": ""}
    if action == "none":
        return result
    if action == "notify_only":
        notify(
            "Long-horizon tick failed",
            f"Supervisor still alive (pid={diag.get('pid')}) but last_ok=false.\n\n"
            f"- tick: {diag.get('tick')}\n"
            f"- reason: {diag.get('reason')}\n"
            f"- Check: `measurements/long_horizon_state.json` and latest `logs/lh_probe_tick*`\n\n"
            "Watchdog will keep monitoring; Grok will repair on next session if it persists.",
            level="warn",
        )
        result["detail"] = "notified"
        return result
    if action in ("relaunch", "kill_relaunch"):
        if action == "kill_relaunch" and diag.get("alive") and diag.get("pid"):
            kill_pid(diag.get("pid"))
            time.sleep(2)
        ok, detail = relaunch_lh()
        result["ok"] = ok
        result["detail"] = detail
        # clear RH actuator request after attempt (success or fail — avoid loop spam)
        if diag.get("reason") == "red_helix_coherence_debt" and RH_RELAUNCH_REQ.exists():
            try:
                # archive then clear
                arch = MEAS / "red_helix_relaunch_request_last.json"
                _atomic_replace_text(arch, RH_RELAUNCH_REQ.read_text(encoding="utf-8"))
                RH_RELAUNCH_REQ.unlink()
            except Exception as e:
                log(f"rh request clear note: {e}")
        if ok:
            notify(
                "Long-horizon relaunched",
                f"Watchdog action `{action}` reason `{diag.get('reason')}`.\n\n"
                f"New run started. State: `measurements/long_horizon_state.json`.\n"
                f"Detail: {detail[:300]}",
                level="info",
            )
        else:
            notify(
                "Long-horizon relaunch FAILED",
                f"Watchdog could not relaunch.\n\n- reason: {diag.get('reason')}\n"
                f"- detail: {detail}\n\n"
                "Need human or Grok session: `powershell -File scripts\\launch_long_horizon.ps1`",
                level="critical",
            )
        return result
    return result


def hope_patch(diag: Dict[str, Any], applied: Dict[str, Any]) -> None:
    try:
        from living.aetheria_canon import write_hope_status

        write_hope_status(
            {
                "watchdog": {
                    "ts": utc_now(),
                    "alive_lh": diag.get("alive"),
                    "lh_pid": diag.get("pid"),
                    "action": applied.get("action"),
                    "reason": diag.get("reason"),
                    "last_ok": diag.get("last_ok"),
                    "tick": diag.get("tick"),
                    "mom": diag.get("last_final_mom"),
                    "status_file": str(WD_STATUS),
                    "notify_file": str(NOTIFY),
                }
            }
        )
    except Exception as e:
        log(f"hope patch note: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval-sec", type=float, default=60.0)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    MEAS.mkdir(exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    if WD_STOP.exists():
        try:
            WD_STOP.unlink()
        except Exception:
            pass
    WD_PID.write_text(str(os.getpid()), encoding="utf-8")
    log(f"WATCHDOG START pid={os.getpid()} interval={args.interval_sec}s")

    last_action_key = ""
    while True:
        if WD_STOP.exists():
            log("watchdog STOP file — exit")
            break
        try:
            diag = diagnose()
            # Debounce identical relaunch loops
            key = f"{diag.get('action')}|{diag.get('reason')}|{diag.get('pid')}|{diag.get('tick')}"
            applied = {"action": "none", "ok": True, "detail": "skipped_debounce"}
            if diag.get("action") != "none":
                if key != last_action_key or diag.get("action") == "notify_only":
                    applied = apply_action(diag)
                    last_action_key = key
                    if diag.get("action") in ("relaunch", "kill_relaunch"):
                        time.sleep(POST_EXIT_RELAUNCH_DELAY_S)
                else:
                    applied = {"action": "none", "ok": True, "detail": "debounced"}
            else:
                last_action_key = ""

            status = {
                "schema": "lh_watchdog_v1",
                "watchdog_pid": os.getpid(),
                "log": str(WD_LOG),
                "diag": diag,
                "last_applied": applied,
                "updated_at": utc_now(),
                "mandate": "full_autonomy_velocity; notify only as needed",
            }
            write_json(WD_STATUS, status)
            hope_patch(diag, applied)
            log(
                f"tick={diag.get('tick')} alive={diag.get('alive')} status={diag.get('status')} "
                f"ok={diag.get('last_ok')} action={diag.get('action')}/{applied.get('action')} "
                f"reason={diag.get('reason')}"
            )
        except Exception as e:
            log(f"watchdog loop error: {e}\n{traceback.format_exc()[-400:]}")
            try:
                write_json(
                    WD_STATUS,
                    {"error": str(e)[:300], "updated_at": utc_now(), "watchdog_pid": os.getpid()},
                )
            except Exception:
                pass

        if args.once:
            break
        # responsive stop
        end = time.time() + max(15.0, float(args.interval_sec))
        while time.time() < end:
            if WD_STOP.exists():
                break
            time.sleep(min(5.0, end - time.time()))

    try:
        WD_PID.unlink()
    except Exception:
        pass
    log("WATCHDOG EXIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
