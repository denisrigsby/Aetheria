"""PID liveness must match the tasklist PID column, not a substring.

PID 12 is a substring of PID 1234 and of a memory field like ``12,345 K``.
A check for 12 against stdout whose PID column is only 1234 must be not alive.
"""
from __future__ import annotations

import os
import subprocess
import sys

import lh_process_identity as ident

# PID column is 1234. "12" occurs inside that PID and inside the memory field.
COLLISION_STDOUT = '"python.exe","1234","Console","1","12,345 K"\n'
EXACT_12_STDOUT = '"python.exe","12","Console","1","8 K"\n'


class _Completed:
    def __init__(self, stdout: str):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


def test_collision_stdout_is_a_substring_hit_for_pid_12():
    """The fixture really does contain the digit sequence 12, so substring checks lie."""
    assert "12" in COLLISION_STDOUT
    assert "1234" in COLLISION_STDOUT


def test_tasklist_csv_pid_column_rejects_substring_collision():
    assert ident.tasklist_csv_has_pid(COLLISION_STDOUT, 12) is False
    assert ident.tasklist_csv_has_pid(COLLISION_STDOUT, 1234) is True


def test_tasklist_csv_pid_column_accepts_exact_12_only():
    assert ident.tasklist_csv_has_pid(EXACT_12_STDOUT, 12) is True
    assert ident.tasklist_csv_has_pid(EXACT_12_STDOUT, 1234) is False


def test_tasklist_csv_ignores_info_and_header():
    info = "INFO: No tasks are running which match the specified criteria.\n"
    assert ident.tasklist_csv_has_pid(info, 12) is False
    headed = (
        '"Image Name","PID","Session Name","Session#","Mem Usage"\n'
        + COLLISION_STDOUT
    )
    assert ident.tasklist_csv_has_pid(headed, 12) is False
    assert ident.tasklist_csv_has_pid(headed, 1234) is True


def test_tasklist_csv_pid_column_not_shifted_by_comma_in_image_name():
    stdout = '"app,12.exe","99","Console","1","8 K"\n'
    assert ident.tasklist_csv_has_pid(stdout, 12) is False
    assert ident.tasklist_csv_has_pid(stdout, 99) is True


def _liveness_fns():
    cwd = os.getcwd()
    try:
        import launch_lh_detached
        import lh_watchdog
        import plant_control
        import status_report
        import verify_continuity_readonly
    finally:
        os.chdir(cwd)
    return {
        "lh_process_identity.pid_exists": ident.pid_exists,
        "lh_watchdog.pid_alive": lh_watchdog.pid_alive,
        "launch_lh_detached.pid_alive": launch_lh_detached.pid_alive,
        "plant_control.pid_alive": plant_control.pid_alive,
        "status_report.pid_alive": status_report.pid_alive,
        "verify_continuity_readonly.pid_alive": verify_continuity_readonly.pid_alive,
    }


def _patch_tasklist(monkeypatch, stdout: str, calls: list):
    def fake_run(args, *a, **k):
        calls.append(list(args))
        return _Completed(stdout)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(subprocess, "run", fake_run)


def test_liveness_checks_reject_pid_12_when_stdout_pid_is_1234(monkeypatch):
    """Synthetic CSV stdout only. This does not run tasklist.exe."""
    calls: list = []
    _patch_tasklist(monkeypatch, COLLISION_STDOUT, calls)
    for name, fn in _liveness_fns().items():
        calls.clear()
        assert fn(12) is False, name
        assert calls, name
        assert calls[0][0] == "tasklist", name
        assert "/FO" in calls[0] and "CSV" in calls[0], name
        assert fn(1234) is True, name


def test_liveness_checks_accept_exact_pid_column_12(monkeypatch):
    calls: list = []
    _patch_tasklist(monkeypatch, EXACT_12_STDOUT, calls)
    for name, fn in _liveness_fns().items():
        assert fn(12) is True, name
        assert fn(1234) is False, name
