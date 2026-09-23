#!/usr/bin/env python3
"""
plant_control.py — Safe plant standby / halt / resume / status.

Operator control for long-horizon supervisor + watchdog when you need
CPU/RAM/GPU for other heavy work, or after power loss.

Modes:
  status   — read-only plant + WD + standby intent
  standby  — durable pause: stop LH (and optional WD); NO auto-relaunch until resume
  halt     — standby + always stop watchdog (stronger "hands off")
  resume   — clear standby/stop, relaunch LH (optional WD), continue tick when possible

Durable intent: measurements/long_horizon_STANDBY.json
  Survives power outage. Watchdog will not relaunch while active.
  Graceful stop still uses long_horizon_STOP for in-process exit.

Stop contract (ordinary stop):
  - signal long_horizon_STOP then watchdog_STOP
  - wait on process-table presence only (pid_exists); the wait does not kill
  - kill a still-present PID only through kill_if_verified (claimed role)
  - kill recorded probe_pid only when identity is probe
  - reject PID-only matches
  - print any remaining allowlisted descendants; exit 1 if any remain

Never parents residual/G4. Companion chat is independent.

Examples:
  python scripts/plant_control.py status
  python scripts/plant_control.py standby --reason "gpu render job"
  python scripts/plant_control.py halt --reason "heavy local train"
  python scripts/plant_control.py resume --with-watchdog
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from atomic_state import atomic_write_json  # noqa: E402
from campaign_lock import single_flight_spawn  # noqa: E402
from lh_process_identity import (  # noqa: E402
    ROLE_PROBE,
    ROLE_SUPERVISOR,
    ROLE_WATCHDOG,
    kill_if_verified,
    list_allowlisted,
    pid_exists,
    verified_role,
)

_SECRET_KEY = re.compile(r"(secret|password|api[_-]?key|token|credential|authorization)", re.I)

MEAS = ROOT / "measurements"
STATE_PATH = MEAS / "long_horizon_state.json"
STANDBY_PATH = MEAS / "long_horizon_STANDBY.json"
LH_STOP = MEAS / "long_horizon_STOP"
WD_STOP = MEAS / "watchdog_STOP"
LH_PID = MEAS / "long_horizon.pid"
WD_PID = MEAS / "watchdog.pid"
WD_STATUS = MEAS / "watchdog_status.json"
MANUAL_PATH = MEAS / "long_horizon_MANUAL_START.json"


def _policy():
    import importlib.util

    p = ROOT / "scripts" / "lh_run_policy.py"
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location("lh_run_policy", p)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod



def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"_error": "unreadable", "path": str(path)}


def _reject_secret_fields(doc: dict) -> None:
    if any(_SECRET_KEY.search(str(k)) for k in doc):
        raise ValueError("secret_field")


def write_json(path: Path, obj: dict) -> None:
    atomic_write_json(path, obj, default=str)


def read_pid(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip().splitlines()[0].strip())
    except Exception:
        return None


def plant_snap() -> Dict[str, Any]:
    st = read_json(STATE_PATH)
    pid = st.get("pid") or read_pid(LH_PID)
    identity_ok = bool(pid) and verified_role(pid, ROLE_SUPERVISOR)
    return {
        "status": st.get("status"),
        "tick": st.get("tick"),
        "max_ticks": st.get("max_ticks"),
        "last_ok": st.get("last_ok"),
        "mom": st.get("last_final_mom") or st.get("persisted_mom"),
        "pid": pid,
        "alive": identity_ok,
        "pid_exists": bool(pid) and pid_exists(pid),
        "identity_ok": identity_ok,
        "cycles_per_tick": st.get("cycles_per_tick"),
        "interval_min": st.get("interval_min"),
        "history_len": len(st.get("history") or []) if isinstance(st.get("history"), list) else 0,
    }


def wd_snap() -> Dict[str, Any]:
    st = read_json(WD_STATUS)
    pid = st.get("watchdog_pid") or read_pid(WD_PID)
    identity_ok = bool(pid) and verified_role(pid, ROLE_WATCHDOG)
    return {
        "pid": pid,
        "alive": identity_ok,
        "pid_exists": bool(pid) and pid_exists(pid),
        "identity_ok": identity_ok,
        "updated_at": st.get("updated_at"),
        "last_action": (st.get("last_applied") or {}).get("action")
        if isinstance(st.get("last_applied"), dict)
        else None,
        "diag_reason": (st.get("diag") or {}).get("reason")
        if isinstance(st.get("diag"), dict)
        else None,
    }


def standby_snap() -> Dict[str, Any]:
    if not STANDBY_PATH.exists():
        return {"active": False}
    s = read_json(STANDBY_PATH)
    s["active"] = bool(s.get("active", True))
    return s


def cmd_status(*, as_json: bool = False) -> int:
    pol = _policy()
    manual = pol.read_manual() if pol else {"active": False}
    manual_req = bool(pol.manual_start_required()) if pol else False
    out = {
        "schema": "aetheria_plant_control_status_v1",
        "ts": utc(),
        "standby": standby_snap(),
        "manual_start": manual,
        "manual_start_required": manual_req,
        "plant": plant_snap(),
        "watchdog": wd_snap(),
        "flags": {
            "lh_stop": LH_STOP.exists(),
            "wd_stop": WD_STOP.exists(),
            "standby_file": STANDBY_PATH.exists(),
            "manual_start_file": MANUAL_PATH.exists(),
        },
        "hints": {
            "standby": "python scripts/plant_control.py standby --reason '…'",
            "halt": "python scripts/plant_control.py halt --reason '…'",
            "resume": "python scripts/plant_control.py resume --with-watchdog",
            "stop": "python scripts/plant_control.py stop --reason '…'",
        },
        "power_flap_policy": (
            "Auto-relaunch OFF after stop/standby/crash unless long_horizon_AUTORUN.enable"
        ),
        "survivors": list_allowlisted(),
    }
    if as_json:
        print(json.dumps(out, indent=2))
        return 0
    sb = out["standby"]
    pl = out["plant"]
    wd = out["watchdog"]
    print("Aetheria plant control")
    print(
        f"  standby: {'ACTIVE' if sb.get('active') else 'off'}"
        + (f"  reason={sb.get('reason')!r}" if sb.get("active") else "")
    )
    print(
        f"  manual_start: {'REQUIRED' if manual_req else 'clear'}"
        + (f"  reason={manual.get('reason')!r}" if manual_req else "")
    )
    print(
        f"  plant:   status={pl.get('status')} tick={pl.get('tick')}/{pl.get('max_ticks')} "
        f"last_ok={pl.get('last_ok')} mom={pl.get('mom')} "
        f"pid={pl.get('pid')} alive={pl.get('alive')}"
    )
    print(
        f"  watchdog: pid={wd.get('pid')} alive={wd.get('alive')} "
        f"last={wd.get('last_action')} reason={wd.get('diag_reason')}"
    )
    print(
        f"  flags: lh_stop={out['flags']['lh_stop']} wd_stop={out['flags']['wd_stop']}"
        f" plant_identity={pl.get('identity_ok')} wd_identity={wd.get('identity_ok')}"
    )
    surv = out.get("survivors") or []
    if surv:
        print(f"  survivors: {len(surv)}")
        for row in surv:
            print(f"    pid={row.get('pid')} parent={row.get('parent')} role={row.get('role')}")
    if sb.get("active") or manual_req:
        print("  → plant will NOT auto-start (power-flap safe). resume/start when power is stable")
    elif pl.get("alive"):
        print("  → plant running; use standby/stop before heavy jobs or storms")
    else:
        print("  → plant not alive; use resume/start when ready")
    return 0


def _write_stop(path: Path, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"stop\n# {reason}\n# {utc()}\n", encoding="utf-8")


def _kill_pid(pid: Any, label: str, claimed: str) -> None:
    r = kill_if_verified(pid, claimed, tree=True)
    print(f"  kill {label} pid={pid} claimed={claimed} {r.get('reason')}")
    if r.get("reason") == "identity_mismatch":
        print(f"  rejected PID-only match for {label} (live pid is {r.get('role')})")


def _report_survivors() -> List[dict]:
    rows = list_allowlisted()
    if not rows:
        print("  survivors: none")
        return []
    print("  survivors (allowlisted cmdlines):")
    for row in rows:
        print(f"    pid={row.get('pid')} parent={row.get('parent')} role={row.get('role')}")
    return rows


def enter_standby(
    *,
    reason: str,
    stop_watchdog: bool,
    force_kill_after_s: float = 90.0,
) -> int:
    """Durable standby: plant will not auto-relaunch until resume."""
    pl0 = plant_snap()
    st = read_json(STATE_PATH)
    intent = {
        "schema": "aetheria_lh_standby_v1",
        "active": True,
        "reason": reason or "operator_standby",
        "entered_at": utc(),
        "entered_by": "plant_control",
        "stop_watchdog": bool(stop_watchdog),
        "resume_hint": {
            "cycles": st.get("cycles_per_tick") or 2,
            "interval_min": st.get("interval_min") or 30.0,
            "max_ticks": st.get("max_ticks") or 48,
            "continue_tick": True,
            "from_tick": st.get("tick"),
            "last_ok": st.get("last_ok"),
            "last_mom": st.get("last_final_mom") or st.get("persisted_mom"),
        },
        "plant_snapshot": pl0,
    }
    write_json(STANDBY_PATH, intent)
    pol = _policy()
    if pol:
        pol.require_manual_start(reason=f"standby:{intent['reason']}", source="plant_control")
    print(f"STANDBY intent written: {STANDBY_PATH}")
    print(f"  reason: {intent['reason']}")
    print("  manual_start REQUIRED (no auto-relaunch until resume/start)")

    # Graceful LH stop first
    if pl0.get("alive"):
        _write_stop(LH_STOP, intent["reason"])
        print("  signaled long_horizon_STOP (graceful)")
        deadline = time.time() + max(15.0, force_kill_after_s)
        while time.time() < deadline:
            if not pid_exists(pl0.get("pid")):
                break
            time.sleep(2)
        if pid_exists(pl0.get("pid")):
            print("  graceful wait timed out — force kill LH tree (identity)")
            _kill_pid(pl0.get("pid"), "lh", ROLE_SUPERVISOR)
    else:
        # ensure stop file present so nothing races a launch
        _write_stop(LH_STOP, intent["reason"] + " (already dead)")
        print("  plant already dead; STOP + STANDBY set")

    # Patch state if process already gone
    st2 = read_json(STATE_PATH)
    if st2 and not pid_exists(st2.get("pid") or pl0.get("pid")):
        st2["status"] = "standby"
        st2["standby"] = True
        st2["standby_reason"] = intent["reason"]
        st2["standby_at"] = utc()
        st2["pid"] = None
        write_json(STATE_PATH, st2)

    if stop_watchdog:
        wd = wd_snap()
        _write_stop(WD_STOP, intent["reason"])
        print("  signaled watchdog_STOP")
        if wd.get("alive"):
            deadline = time.time() + 45
            while time.time() < deadline:
                if not pid_exists(wd.get("pid")):
                    break
                time.sleep(1)
            if pid_exists(wd.get("pid")):
                _kill_pid(wd.get("pid"), "watchdog", ROLE_WATCHDOG)
    else:
        print("  watchdog left running (will respect STANDBY — no relaunch)")

    # Leave LH_STOP in place while standby is active (defense in depth)
    cmd_status(as_json=False)
    print("OK standby active — heavy programs safe; plant will not auto-return until resume")
    return 0


def clear_standby_files() -> None:
    for p in (STANDBY_PATH, LH_STOP, WD_STOP):
        if p.exists():
            try:
                p.unlink()
                print(f"  cleared {p.name}")
            except Exception as e:
                print(f"  clear {p.name} note: {e}")
    pol = _policy()
    if pol:
        pol.clear_manual_start()
        print("  cleared manual_start latch")


def cmd_stop(*, reason: str = "operator_stop") -> int:
    """Graceful stop: supervisor tree + recorded probe + watchdog. Manual-start latch."""
    pl0 = plant_snap()
    st0 = read_json(STATE_PATH)
    probe_pid = st0.get("probe_pid")
    pol = _policy()
    if pol:
        pol.require_manual_start(reason=reason, source="plant_control_stop")
    _write_stop(LH_STOP, reason)
    print(f"STOP signaled ({reason})")
    if pl0.get("pid"):
        deadline = time.time() + 90
        while time.time() < deadline:
            if not pid_exists(pl0.get("pid")):
                break
            time.sleep(2)
        if pid_exists(pl0.get("pid")):
            print("  graceful wait timed out — kill supervisor tree while still alive")
            _kill_pid(pl0.get("pid"), "lh", ROLE_SUPERVISOR)
        else:
            print("  supervisor pid already dead; will not /T a dead parent (kills recorded probe next)")
    if probe_pid:
        _kill_pid(probe_pid, "probe", ROLE_PROBE)
    wd = wd_snap()
    _write_stop(WD_STOP, reason)
    print("  signaled watchdog_STOP")
    if wd.get("pid"):
        deadline = time.time() + 45
        while time.time() < deadline:
            if not pid_exists(wd.get("pid")):
                break
            time.sleep(1)
        if pid_exists(wd.get("pid")):
            _kill_pid(wd.get("pid"), "watchdog", ROLE_WATCHDOG)
    for row in list_allowlisted():
        role = row.get("role")
        pid = row.get("pid")
        if role in (ROLE_SUPERVISOR, ROLE_WATCHDOG, ROLE_PROBE) and pid:
            _kill_pid(pid, f"survivor-{role}", role)
    st = read_json(STATE_PATH)
    if st:
        st["status"] = "stopped_by_file"
        st["pid"] = None
        st["probe_pid"] = None
        st["manual_start"] = True
        write_json(STATE_PATH, st)
    survivors = _report_survivors()
    if survivors:
        print("INCOMPLETE stop: allowlisted descendants remain. Manual /start or resume after they are gone.")
        cmd_status(as_json=False)
        return 1
    _reconcile_stale_pid_files()
    print("OK stopped (no allowlisted survivors). Manual /start or resume required when power is stable.")
    cmd_status(as_json=False)
    return 0


def _reconcile_stale_pid_files() -> None:
    """After verified stop: unlink PID files whose recorded PID is not a live matching role.

    Policy: retain PID files while a process with that identity is alive; remove after
    reconciliation so status does not display a stale number. Numbers remain in STOP
    file comments and state JSON history / manual_start extra if needed.
    """
    pairs = (
        (LH_PID, ROLE_SUPERVISOR, "supervisor"),
        (WD_PID, ROLE_WATCHDOG, "watchdog"),
    )
    for path, role, label in pairs:
        pid = read_pid(path)
        if pid is None:
            if path.exists():
                try:
                    path.unlink()
                    print(f"  reconciled empty/unreadable {path.name}")
                except Exception as e:
                    print(f"  reconcile {path.name} note: {e}")
            continue
        if verified_role(pid, role):
            print(f"  keep {path.name}: pid={pid} still verified {label}")
            continue
        try:
            path.unlink()
            print(f"  reconciled stale {path.name} (pid={pid} not verified {label})")
        except Exception as e:
            print(f"  reconcile {path.name} note: {e}")


def _supervisor_lock_paths() -> tuple[Path, Path]:
    return (
        MEAS / "campaign_supervisor.lock",
        MEAS / "campaign_supervisor_claim.json",
    )


def single_supervisor_critical(
    spawn,
    *,
    origin: str,
    lock_path: Optional[Path] = None,
    claim_path: Optional[Path] = None,
    role_alive=None,
    timeout_s: float = 90.0,
) -> Dict[str, Any]:
    """Start/recover admit. At most one caller runs ``spawn`` for the supervisor role."""
    lock_p, claim_p = _supervisor_lock_paths()
    if lock_path is not None:
        lock_p = Path(lock_path)
    if claim_path is not None:
        claim_p = Path(claim_path)
    if role_alive is None:

        def role_alive() -> bool:
            return bool(plant_snap().get("alive"))
    result = single_flight_spawn(
        lock_p,
        claim_p,
        role=ROLE_SUPERVISOR,
        role_alive=role_alive,
        spawn=spawn,
        timeout_s=timeout_s,
    )
    result["origin"] = origin
    return result


def _apply_recover_record(rec: dict) -> None:
    camp = rec.get("campaign") or {}
    st = read_json(STATE_PATH) or {}
    if st.get("_error"):
        st = {}
    st["last_ok"] = bool(camp.get("last_ok"))
    st["last_final_mom"] = camp.get("mom")
    st["persisted_mom"] = camp.get("mom")
    st["last_tick_finished"] = camp.get("last_tick_finished")
    st["recovered_from_snapshot_at"] = utc()
    st["status"] = "idle_between_ticks"
    _reject_secret_fields(st)
    atomic_write_json(STATE_PATH, st)
    print(f"  snapshot applied mom={camp.get('mom')} last_ok={camp.get('last_ok')}")
    print("  segment tick may reset; campaign mom restored")


def _optional_recover_reap() -> None:
    try:
        import importlib.util

        rr_path = ROOT / "scripts" / "lh_recover_reap.py"
        if not rr_path.is_file():
            return
        spec = importlib.util.spec_from_file_location("lh_recover_reap", rr_path)
        rrmod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(rrmod)
        rr = rrmod.run_all(dry_run=False, reap=True, recover=True)
        eng = rr.get("english") or rrmod.english_handoff(rr)
        print(eng)
        rec = rr.get("recover") or {}
        reap = rr.get("reap") or {}
        print(f"  detail recover: {rec.get('note')}")
        print(
            f"  detail reap: orphans={len(reap.get('orphans_found') or [])} "
            f"killed={reap.get('killed')} lh_was_alive={reap.get('lh_alive')}"
        )
    except Exception as e:
        print(f"  recover/reap note: {type(e).__name__}: {e}")


def admit_launch_kwargs(
    *,
    cycles: int,
    interval_min: float,
    max_ticks: int,
    continue_tick: bool,
) -> Dict[str, Any]:
    """Start/recover launch options. Do not kill from a PID file (stop_old stays false)."""
    return {
        "cycles": cycles,
        "interval_min": interval_min,
        "max_ticks": max_ticks,
        "continue_tick": bool(continue_tick),
        "clear_latches": True,
        "stop_old": False,
        "poll_s": 60.0,
    }


def _launch_supervisor(
    *,
    cycles: int,
    interval_min: float,
    max_ticks: int,
    continue_tick: bool,
) -> Dict[str, Any]:
    """Detach one supervisor. Returns {ok, pid, detail}. Does not decide single-flight."""
    import importlib.util

    launch_mod_path = ROOT / "scripts" / "launch_lh_detached.py"
    spec = importlib.util.spec_from_file_location("launch_lh_detached", launch_mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    ok_l, detail, pid_l = mod.launch_lh_detached(
        **admit_launch_kwargs(
            cycles=cycles,
            interval_min=interval_min,
            max_ticks=max_ticks,
            continue_tick=continue_tick,
        )
    )
    return {"ok": bool(ok_l), "pid": pid_l, "detail": detail}


def resume(
    *,
    with_watchdog: bool,
    cycles: Optional[int],
    interval_min: Optional[float],
    max_ticks: Optional[int],
    continue_tick: bool = True,
    recover_record: Optional[dict] = None,
) -> int:
    sb = standby_snap()
    hint = (sb.get("resume_hint") or {}) if sb.get("active") else {}
    st = read_json(STATE_PATH)

    cyc = int(cycles if cycles is not None else hint.get("cycles") or st.get("cycles_per_tick") or 2)
    iv = float(
        interval_min
        if interval_min is not None
        else hint.get("interval_min") or st.get("interval_min") or 30.0
    )
    mt = int(max_ticks if max_ticks is not None else hint.get("max_ticks") or st.get("max_ticks") or 48)
    # Continue-tick past a prior max_ticks ceiling (e.g. tick 84 with max 48) must extend
    # the ceiling or the supervisor exits after one tick (false "idle" then dead PID).
    cur_tick = 0
    try:
        cur_tick = int(st.get("tick") or 0)
    except Exception:
        cur_tick = 0
    if continue_tick and cur_tick >= mt:
        extend_by = int(st.get("max_ticks") or 48) or 48
        mt = cur_tick + extend_by
        print(
            f"  note: extending max_ticks → {mt} "
            f"(continue_tick past prior ceiling; state_tick={cur_tick})"
        )

    origin = "recover" if recover_record is not None else "start"
    print("RESUME plant" if origin == "start" else "RESUME plant (recover admit)")
    print(f"  cycles={cyc} interval_min={iv} max_ticks={mt} continue_tick={continue_tick}")

    def _work() -> Dict[str, Any]:
        if recover_record is not None:
            _apply_recover_record(recover_record)
        clear_standby_files()
        _optional_recover_reap()
        state = read_json(STATE_PATH) or {}
        if state.get("_error"):
            state = {}
        if state:
            state["standby"] = False
            state["resume_requested_at"] = utc()
            state["continue_tick"] = bool(continue_tick)
            state["max_ticks"] = mt
            _reject_secret_fields(state)
            atomic_write_json(STATE_PATH, state)
        elif recover_record is None and st and not st.get("_error"):
            patched = dict(st)
            patched["standby"] = False
            patched["resume_requested_at"] = utc()
            patched["continue_tick"] = bool(continue_tick)
            patched["max_ticks"] = mt
            _reject_secret_fields(patched)
            atomic_write_json(STATE_PATH, patched)
        return _launch_supervisor(
            cycles=cyc,
            interval_min=iv,
            max_ticks=mt,
            continue_tick=bool(continue_tick),
        )

    try:
        timeout_s = float(os.environ.get("AETHERIA_ROLE_LOCK_TIMEOUT_S", "90"))
    except ValueError:
        timeout_s = 90.0
    gate = single_supervisor_critical(_work, origin=origin, timeout_s=timeout_s)
    if not gate.get("spawned"):
        reason = gate.get("reason")
        print(f"FAIL: single-flight supervisor ({reason})")
        if reason in ("role_alive", "claim_held", "lock_timeout", "role_check_error"):
            print("  refused: will not spawn a second supervisor")
        elif reason == "spawn_failed":
            print("FAIL: detached launch did not produce live LH")
            if gate.get("detail"):
                print(f"  launch: {gate.get('detail')}")
        elif reason == "spawn_error":
            print(f"FAIL launch: {gate.get('detail')}")
        return 1

    pid_l = gate.get("pid")
    print(f"  launch: {gate.get('detail')}")
    print(f"  LH alive pid={pid_l}")
    print(
        f"--- Start handoff ---\n"
        f"Plant starting (pid={pid_l}). Interval={iv}m continue_tick={continue_tick}.\n"
        f"Check /status or: python -u scripts/plant_control.py status\n"
        f"Shop: measurements/SHOP_CARD.md\n"
        f"---"
    )

    if with_watchdog:
        # clear wd stop if any
        if WD_STOP.exists():
            try:
                WD_STOP.unlink()
            except Exception:
                pass
        wd = wd_snap()
        if not wd.get("alive"):
            wlaunch = ROOT / "scripts" / "launch_lh_watchdog.ps1"
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(wlaunch),
                    ],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                print("  watchdog launch requested")
            except Exception as e:
                print(f"  watchdog launch note: {e}")
        else:
            print(f"  watchdog already alive pid={wd.get('pid')}")

    cmd_status(as_json=False)
    print("OK resume — plant should continue (tick continuity if prior state present)")
    return 0


def cmd_recover() -> int:
    """Dead plant only. Load campaign_snapshot_v1. Hash fail → exit 1, do not spawn."""
    print("RECOVER plant from campaign_snapshot_v1")
    snap = plant_snap()
    if snap.get("alive"):
        print("FAIL: supervisor identity-alive — recover will not spawn a second clock")
        print(f"  pid={snap.get('pid')}")
        return 1
    try:
        import campaign_snapshot as csnap
    except Exception as e:
        print(f"FAIL: campaign_snapshot import: {e}")
        return 1
    rec, why = csnap.load_snapshot()
    if rec is None:
        print(f"FAIL: snapshot {why}")
        print("  path: measurements/campaign_snapshot_v1.json")
        print("  recover does not spawn without a valid snapshot")
        return 1
    camp = rec.get("campaign") or {}
    print(f"  snapshot valid mom={camp.get('mom')} last_ok={camp.get('last_ok')}")
    print("  apply + spawn run under the supervisor single-flight lock")
    return resume(
        with_watchdog=True,
        cycles=None,
        interval_min=None,
        max_ticks=None,
        continue_tick=True,
        recover_record=rec,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Safe plant standby / halt / resume")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_st = sub.add_parser("status", help="Plant + watchdog + standby + manual_start")
    p_st.add_argument("--json", action="store_true")

    p_sb = sub.add_parser("standby", help="Durable pause; no auto-relaunch until resume")
    p_sb.add_argument("--reason", type=str, default="operator_standby")
    p_sb.add_argument(
        "--stop-watchdog",
        action="store_true",
        help="Also stop watchdog (default: leave WD up; it still respects STANDBY)",
    )
    p_sb.add_argument("--force-kill-after", type=float, default=90.0)

    p_h = sub.add_parser("halt", help="Standby + stop watchdog (full hands-off)")
    p_h.add_argument("--reason", type=str, default="operator_halt")
    p_h.add_argument("--force-kill-after", type=float, default=90.0)

    p_stop = sub.add_parser("stop", help="Stop plant + manual-start latch (power-flap safe)")
    p_stop.add_argument("--reason", type=str, default="operator_stop")

    p_r = sub.add_parser("resume", help="Clear standby/manual latch and relaunch plant")
    p_r.add_argument("--with-watchdog", action="store_true", help="Ensure watchdog is up")
    p_r.add_argument("--cycles", type=int, default=None)
    p_r.add_argument("--interval-min", type=float, default=None)
    p_r.add_argument("--max-ticks", type=int, default=None)
    p_r.add_argument(
        "--fresh-segment",
        action="store_true",
        help="Do not continue tick counter (new segment from tick 1)",
    )
    # alias
    p_start = sub.add_parser("start", help="Alias for resume --with-watchdog")
    p_start.add_argument("--cycles", type=int, default=None)
    p_start.add_argument("--interval-min", type=float, default=None)
    p_start.add_argument("--max-ticks", type=int, default=None)
    p_start.add_argument("--fresh-segment", action="store_true")
    sub.add_parser(
        "recover",
        help="Dead plant only: load campaign_snapshot_v1 then spawn. Hash fail = no spawn.",
    )

    args = ap.parse_args(argv)

    if args.cmd == "status":
        return cmd_status(as_json=bool(args.json))
    if args.cmd == "standby":
        return enter_standby(
            reason=args.reason,
            stop_watchdog=bool(args.stop_watchdog),
            force_kill_after_s=float(args.force_kill_after),
        )
    if args.cmd == "halt":
        return enter_standby(
            reason=args.reason,
            stop_watchdog=True,
            force_kill_after_s=float(args.force_kill_after),
        )
    if args.cmd == "stop":
        return cmd_stop(reason=args.reason)
    if args.cmd == "resume":
        return resume(
            with_watchdog=bool(args.with_watchdog),
            cycles=args.cycles,
            interval_min=args.interval_min,
            max_ticks=args.max_ticks,
            continue_tick=not bool(args.fresh_segment),
        )
    if args.cmd == "start":
        return resume(
            with_watchdog=True,
            cycles=args.cycles,
            interval_min=args.interval_min,
            max_ticks=args.max_ticks,
            continue_tick=not bool(args.fresh_segment),
        )
    if args.cmd == "recover":
        return cmd_recover()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
