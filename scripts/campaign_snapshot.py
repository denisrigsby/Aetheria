#!/usr/bin/env python3
"""Campaign snapshot v1 — one commit after a green tick.

Not living, not registry, not chat. Recover loads this file only.
Does not AUTORUN. Does not start the plant from chat.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from atomic_state import atomic_write_json  # noqa: E402

SCHEMA = "aetheria_campaign_snapshot_v1"
SNAP_NAME = "campaign_snapshot_v1.json"
GREEN_REL = "measurements/gate_a_green_ticks.jsonl"
BACKUP_SET = (
    "campaign_snapshot_v1.json",
    "long_horizon_state.json",
    "gate_a_green_ticks.jsonl",
    "guidance_momentum.json",
    "watchdog_status.json",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def root() -> Path:
    return Path(os.environ.get("AETHERIA_ROOT") or Path(__file__).resolve().parents[1])


def snap_path(r: Optional[Path] = None) -> Path:
    return (r or root()) / "measurements" / SNAP_NAME


def green_path(r: Optional[Path] = None) -> Path:
    return (r or root()) / GREEN_REL.replace("/", os.sep)


def _green_meta(r: Path) -> Dict[str, Any]:
    p = green_path(r)
    if not p.is_file():
        return {"path": GREEN_REL, "bytes": 0, "last_line_sha256": ""}
    data = p.read_bytes()
    last = b""
    for ln in data.splitlines():
        if ln.strip():
            last = ln
    return {
        "path": GREEN_REL,
        "bytes": len(data),
        "last_line_sha256": hashlib.sha256(last).hexdigest() if last else "",
    }


def green_meta_matches(snap: dict, r: Optional[Path] = None) -> bool:
    r = r or root()
    g = (snap or {}).get("green_log") or {}
    now = _green_meta(r)
    return (
        int(g.get("bytes") or 0) == int(now.get("bytes") or 0)
        and str(g.get("last_line_sha256") or "") == str(now.get("last_line_sha256") or "")
    )


def should_write(state: dict, r: Optional[Path] = None) -> Tuple[bool, str]:
    r = r or root()
    if (r / "measurements" / "long_horizon_STOP").exists():
        return False, "stop_in_progress"
    st = str((state or {}).get("status") or "")
    if st in ("running_tick", "running_probe"):
        return False, f"status_{st}"
    if (state or {}).get("last_ok") is not True:
        return False, "last_ok_false"
    return True, "green"


def write_after_green_tick(state: dict, r: Optional[Path] = None) -> Dict[str, Any]:
    """tmp+replace snapshot after a tick that already qualifies as green. No spawn."""
    r = r or root()
    ok, why = should_write(state, r)
    if not ok:
        return {"ok": False, "written": False, "reason": why}
    meas = r / "measurements"
    meas.mkdir(parents=True, exist_ok=True)
    rec = {
        "schema": SCHEMA,
        "written_at": utc(),
        "segment": {
            "tick": int(state.get("tick") or 0),
            "supervisor_role": "long_horizon_supervisor.py",
        },
        "campaign": {
            "mom": state.get("last_final_mom") or state.get("persisted_mom") or 0,
            "last_ok": True,
            "last_tick_finished": state.get("last_tick_finished") or utc(),
        },
        "green_log": _green_meta(r),
        "heartbeat_at": state.get("heartbeat_at") or utc(),
        "exit_reason": None,
        "probe_contract": "lh_probe_summary_v1",
    }
    dest = snap_path(r)
    atomic_write_json(dest, rec)
    backup_measurements_set(r)
    return {"ok": True, "written": True, "path": str(dest.relative_to(r)), "reason": "green"}


def load_snapshot(r: Optional[Path] = None) -> Tuple[Optional[dict], str]:
    r = r or root()
    p = snap_path(r)
    if not p.is_file():
        return None, "missing"
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return None, f"unreadable:{type(e).__name__}"
    if rec.get("schema") != SCHEMA:
        return None, "schema_mismatch"
    if not green_meta_matches(rec, r):
        return None, "green_log_stale"
    return rec, "ok"


def backup_measurements_set(r: Optional[Path] = None) -> Path:
    r = r or root()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = r / "backups" / "measurements" / stamp
    dest.mkdir(parents=True, exist_ok=True)
    meas = r / "measurements"
    for name in BACKUP_SET:
        src = meas / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    return dest
