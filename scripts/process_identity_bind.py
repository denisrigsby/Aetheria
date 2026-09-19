"""Stronger process-identity binding beyond PID alone.

Public control-plane helper. On non-Windows, creation-time/exe probes are best-effort.
Mismatch policy: refuse kill/resume/adopt (caller must HOLD).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ProcessBinding:
    pid: int
    role: str
    creation_time: Optional[str] = None  # ISO UTC when known
    exe_path: Optional[str] = None
    cmdline: Optional[str] = None
    parent_pid: Optional[int] = None
    campaign_uuid: Optional[str] = None
    job_object: Optional[str] = None  # name/handle id when Job Objects used

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_cmdline(cmd: str) -> str:
    s = (cmd or "").strip().lower().replace("\\", "/")
    s = re.sub(r"\s+", " ", s)
    return s


def windows_binding(pid: int) -> Optional[ProcessBinding]:
    """Query Win32_Process for creation time, exe, cmdline, parent."""
    if sys.platform != "win32":
        return None
    try:
        # Avoid shell=True — argv list only
        ps = (
            f"$p=Get-CimInstance Win32_Process -Filter \"ProcessId={int(pid)}\";"
            f"if(-not $p){{''}}else{{ConvertTo-Json -Compress @{{"
            f"ProcessId=$p.ProcessId;ParentProcessId=$p.ParentProcessId;"
            f"ExecutablePath=$p.ExecutablePath;CommandLine=$p.CommandLine;"
            f"CreationDate=$p.CreationDate}}}}"
        )
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps],
            text=True,
            timeout=8,
        ).strip()
        if not out:
            return None
        data = json.loads(out)
        return ProcessBinding(
            pid=int(data.get("ProcessId") or pid),
            role="unknown",
            creation_time=str(data.get("CreationDate") or "") or None,
            exe_path=data.get("ExecutablePath"),
            cmdline=data.get("CommandLine"),
            parent_pid=int(data["ParentProcessId"]) if data.get("ParentProcessId") is not None else None,
        )
    except Exception:
        return None


def bindings_match(recorded: ProcessBinding, live: ProcessBinding, *, require_creation_time: bool = True) -> bool:
    if int(recorded.pid) != int(live.pid):
        return False
    if recorded.cmdline and live.cmdline:
        if normalize_cmdline(recorded.cmdline) != normalize_cmdline(live.cmdline):
            # Allow role token equality via substring roles checked by caller;
            # here require exact normalized match when both present.
            return False
    if recorded.exe_path and live.exe_path:
        if Path(recorded.exe_path).name.lower() != Path(live.exe_path).name.lower():
            return False
    if require_creation_time:
        if not recorded.creation_time or not live.creation_time:
            return False
        if recorded.creation_time != live.creation_time:
            return False
    if recorded.parent_pid is not None and live.parent_pid is not None:
        if int(recorded.parent_pid) != int(live.parent_pid):
            return False
    if recorded.campaign_uuid and live.campaign_uuid:
        if recorded.campaign_uuid != live.campaign_uuid:
            return False
    if recorded.job_object and live.job_object:
        if recorded.job_object != live.job_object:
            return False
    return True


def refuse_action_on_mismatch(recorded: Optional[Dict[str, Any]], live: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a fail-closed decision object — never kill/resume/adopt on mismatch."""
    if not recorded or not live:
        return {
            "ok": False,
            "action": "refuse",
            "reason": "missing_binding",
            "may_kill": False,
            "may_resume": False,
            "may_adopt": False,
            "at": _utc(),
        }
    rec = ProcessBinding(**{k: recorded.get(k) for k in ProcessBinding.__dataclass_fields__})  # type: ignore[arg-type]
    liv = ProcessBinding(**{k: live.get(k) for k in ProcessBinding.__dataclass_fields__})  # type: ignore[arg-type]
    matched = bindings_match(rec, liv)
    return {
        "ok": matched,
        "action": "allow_role_scoped" if matched else "refuse",
        "reason": "identity_match" if matched else "identity_mismatch_or_pid_reuse",
        "may_kill": matched,
        "may_resume": matched,
        "may_adopt": matched,
        "at": _utc(),
    }
