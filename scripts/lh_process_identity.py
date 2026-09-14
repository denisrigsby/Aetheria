#!/usr/bin/env python3
"""Plant process identity and Windows kill helpers.

One matcher contract for supervisor, watchdog, and both probe families.
No chdir, no measurements I/O, no plant launch. Stdlib only.

Windows-specific helpers (tasklist/taskkill/CIM) are isolated; role matching is portable.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

ROLE_SUPERVISOR = "supervisor"
ROLE_WATCHDOG = "watchdog"
ROLE_PROBE = "probe"
ROLE_OTHER = "other"

SUPERVISOR_TOKEN = "long_horizon_supervisor.py"
WATCHDOG_TOKEN = "lh_watchdog.py"
PROBE_NAMED = "grok_supervised_12_probe"
PROBE_WRAP = "_lh_probe_"


def role_from_cmdline(cmd: Optional[str]) -> str:
    c = (cmd or "").replace("\\", "/")
    if SUPERVISOR_TOKEN in c:
        return ROLE_SUPERVISOR
    if WATCHDOG_TOKEN in c:
        return ROLE_WATCHDOG
    if PROBE_NAMED in c or PROBE_WRAP in c:
        return ROLE_PROBE
    return ROLE_OTHER


def is_supervisor(cmd: Optional[str]) -> bool:
    return role_from_cmdline(cmd) == ROLE_SUPERVISOR


def is_watchdog(cmd: Optional[str]) -> bool:
    return role_from_cmdline(cmd) == ROLE_WATCHDOG


def is_probe(cmd: Optional[str]) -> bool:
    return role_from_cmdline(cmd) == ROLE_PROBE


def identity_matches(cmd: Optional[str], claimed: str) -> bool:
    return role_from_cmdline(cmd) == claimed


def pid_exists(pid: Any) -> bool:
    """Process table presence. Windows: filtered tasklist CSV PID column (not substring)."""
    try:
        p = int(pid)
    except Exception:
        return False
    if p <= 0:
        return False
    if sys.platform != "win32":
        try:
            os.kill(p, 0)
            return True
        except Exception:
            return False
    r = subprocess.run(
        ["tasklist", "/FI", f"PID eq {p}", "/NH", "/FO", "CSV"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    out = (r.stdout or "").strip()
    if not out or out.upper().startswith("INFO:"):
        return False
    for line in out.splitlines():
        line = line.strip()
        if not line or line.upper().startswith("INFO:"):
            continue
        parts = [x.strip().strip('"') for x in line.split(",")]
        if len(parts) >= 2:
            try:
                if int(parts[1]) == p:
                    return True
            except Exception:
                continue
    return False


def cmdline_for_pid(pid: Any) -> Optional[str]:
    try:
        p = int(pid)
    except Exception:
        return None
    if p <= 0:
        return None
    if sys.platform != "win32":
        return None
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"(Get-CimInstance Win32_Process -Filter 'ProcessId={p}').CommandLine",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    t = (r.stdout or "").strip()
    return t or None


def verified_role(pid: Any, claimed: str) -> bool:
    """True only if PID exists and cmdline matches claimed role. Rejects PID-only matches."""
    if not pid_exists(pid):
        return False
    cmd = cmdline_for_pid(pid)
    return identity_matches(cmd, claimed)


def taskkill(pid: int, *, tree: bool) -> Dict[str, Any]:
    args = ["taskkill", "/PID", str(int(pid)), "/F"]
    if tree:
        args.append("/T")
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return {
        "args": args,
        "returncode": r.returncode,
        "stdout": (r.stdout or "")[-300:],
        "stderr": (r.stderr or "")[-300:],
    }


def kill_if_verified(pid: Any, claimed: str, *, tree: bool = True) -> Dict[str, Any]:
    """Kill only while the PID is still alive and cmdline matches claimed role."""
    out: Dict[str, Any] = {"pid": pid, "claimed": claimed, "killed": False, "reason": ""}
    try:
        p = int(pid)
    except Exception:
        out["reason"] = "bad_pid"
        return out
    if not pid_exists(p):
        out["reason"] = "already_dead"
        return out
    cmd = cmdline_for_pid(p)
    if not identity_matches(cmd, claimed):
        out["reason"] = "identity_mismatch"
        out["role"] = role_from_cmdline(cmd)
        return out
    if sys.platform != "win32":
        try:
            os.kill(p, 15)
            out["killed"] = True
            out["reason"] = "posix_sigterm"
        except Exception as e:
            out["reason"] = f"posix_kill:{type(e).__name__}"
        return out
    kr = taskkill(p, tree=tree)
    out["taskkill"] = kr
    out["killed"] = kr.get("returncode") == 0 or not pid_exists(p)
    out["reason"] = "ok" if out["killed"] else "taskkill_failed"
    return out


def list_allowlisted() -> List[Dict[str, Any]]:
    """CIM rows whose CommandLine contains a plant token. Not a full process dump."""
    if sys.platform != "win32":
        return []
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "$t=@('long_horizon_supervisor.py','lh_watchdog.py','grok_supervised_12_probe','_lh_probe_');"
            "Get-CimInstance Win32_Process | ForEach-Object {"
            "  $c=$_.CommandLine; if(-not $c){return};"
            "  $hit=$false; foreach($x in $t){ if($c.IndexOf($x) -ge 0){ $hit=$true } };"
            "  if(-not $hit){return};"
            "  '{0}|{1}' -f $_.ProcessId,$_.ParentProcessId"
            "}",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    rows: List[Dict[str, Any]] = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        a, b = line.split("|", 1)
        if not a.isdigit():
            continue
        pid = int(a)
        parent = int(b) if b.strip().isdigit() else None
        cmd = cmdline_for_pid(pid)
        role = role_from_cmdline(cmd)
        if role == ROLE_OTHER:
            continue
        rows.append({"pid": pid, "parent": parent, "role": role})
    return rows
