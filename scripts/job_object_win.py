"""Windows Job Object helpers (optional stronger tree containment).

Aspirational public helper: create a job, assign a process, terminate the job.
If Job Objects APIs are unavailable, callers must fall back to identity-checked
refusal rather than PID-ancestry kill.
"""
from __future__ import annotations

import sys
from typing import Optional

JOB_OBJECTS_AVAILABLE = False
_kernel32 = None

if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes

        _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # Prototypes (subset)
        _kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        _kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        _kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        _kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        _kernel32.TerminateJobObject.restype = wintypes.BOOL
        _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        _kernel32.CloseHandle.restype = wintypes.BOOL
        _kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        _kernel32.OpenProcess.restype = wintypes.HANDLE
        JOB_OBJECTS_AVAILABLE = True
    except Exception:
        JOB_OBJECTS_AVAILABLE = False


PROCESS_ALL_ACCESS = 0x1F0FFF


def create_job(name: Optional[str] = None):
    if not JOB_OBJECTS_AVAILABLE or _kernel32 is None:
        return None
    handle = _kernel32.CreateJobObjectW(None, name)
    if not handle:
        return None
    return handle


def assign_pid_to_job(job_handle, pid: int) -> bool:
    if not JOB_OBJECTS_AVAILABLE or _kernel32 is None or not job_handle:
        return False
    proc = _kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
    if not proc:
        return False
    try:
        ok = bool(_kernel32.AssignProcessToJobObject(job_handle, proc))
        return ok
    finally:
        _kernel32.CloseHandle(proc)


def terminate_job(job_handle, exit_code: int = 1) -> bool:
    if not JOB_OBJECTS_AVAILABLE or _kernel32 is None or not job_handle:
        return False
    return bool(_kernel32.TerminateJobObject(job_handle, exit_code))


def close_job(job_handle) -> None:
    if JOB_OBJECTS_AVAILABLE and _kernel32 is not None and job_handle:
        _kernel32.CloseHandle(job_handle)
