"""Stop, recover, and launch stop_old must not kill on PID presence alone.

Wait loops use pid_exists (exact tasklist PID column after the liveness fix).
Kills go through kill_if_verified. A live PID whose cmdline is the wrong role
is left running: no taskkill and no non-zero signal.

kill_if_verified does not take expected_create_time, so this file does not
claim a create_time mismatch refusal.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import launch_lh_detached as ld
import lh_process_identity as ident
import plant_control as pc

# Same collision fixture as the liveness tests: "12" is not the PID column.
COLLISION_STDOUT = '"python.exe","1234","Console","1","12,345 K"\n'


def _redirect(monkeypatch, tmp_path: Path) -> Path:
    meas = tmp_path / "measurements"
    meas.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pc, "MEAS", meas)
    monkeypatch.setattr(pc, "STATE_PATH", meas / "long_horizon_state.json")
    monkeypatch.setattr(pc, "STANDBY_PATH", meas / "long_horizon_STANDBY.json")
    monkeypatch.setattr(pc, "LH_STOP", meas / "long_horizon_STOP")
    monkeypatch.setattr(pc, "WD_STOP", meas / "watchdog_STOP")
    monkeypatch.setattr(pc, "LH_PID", meas / "long_horizon.pid")
    monkeypatch.setattr(pc, "WD_PID", meas / "watchdog.pid")
    monkeypatch.setattr(pc, "WD_STATUS", meas / "watchdog_status.json")
    monkeypatch.setattr(pc, "MANUAL_PATH", meas / "long_horizon_MANUAL_START.json")
    monkeypatch.setenv("AETHERIA_ROOT", str(tmp_path))
    monkeypatch.setattr(pc, "list_allowlisted", lambda: [])
    return meas


def _write_state(pid: int) -> None:
    pc.STATE_PATH.write_text(
        json.dumps({"pid": pid, "status": "running_tick", "tick": 1}),
        encoding="utf-8",
    )


def _sleeper() -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _fast_clock(monkeypatch) -> None:
    now = {"t": 1000.0}

    def fake_time() -> float:
        now["t"] += 100.0
        return now["t"]

    monkeypatch.setattr(pc.time, "time", fake_time)
    monkeypatch.setattr(pc.time, "sleep", lambda *_a, **_k: None)


def _watch_kills(monkeypatch):
    signals: list[tuple[int, int]] = []
    real_kill = os.kill

    def spy_kill(pid, sig, *args):
        signals.append((int(pid), int(sig)))
        return real_kill(pid, sig, *args)

    real_run = subprocess.run
    taskkills: list[list] = []

    def spy_run(args, *a, **k):
        argv = list(args) if isinstance(args, (list, tuple)) else [args]
        if argv and str(argv[0]).lower() == "taskkill":
            taskkills.append(argv)
        return real_run(args, *a, **k)

    monkeypatch.setattr(os, "kill", spy_kill)
    monkeypatch.setattr(subprocess, "run", spy_run)
    return signals, taskkills


def _cmdline(monkeypatch, pid: int, text: str) -> None:
    def fake(asked):
        try:
            if int(asked) == int(pid):
                return text
        except (TypeError, ValueError):
            return None
        return None

    monkeypatch.setattr(ident, "cmdline_for_pid", fake)


def _assert_survived(proc: subprocess.Popen, signals, taskkills) -> None:
    assert proc.poll() is None
    assert [(pid, sig) for pid, sig in signals if pid == proc.pid and sig != 0] == []
    assert taskkills == []


def test_stop_noops_on_wrong_role(tmp_path: Path, monkeypatch, capsys):
    proc = _sleeper()
    try:
        _redirect(monkeypatch, tmp_path)
        _write_state(proc.pid)
        _cmdline(monkeypatch, proc.pid, "python -u lh_watchdog.py --interval-sec 60")
        _fast_clock(monkeypatch)
        signals, taskkills = _watch_kills(monkeypatch)
        results: list[dict] = []
        real = ident.kill_if_verified

        def wrapped(pid, claimed, tree=True):
            out = real(pid, claimed, tree=tree)
            results.append(out)
            return out

        monkeypatch.setattr(pc, "kill_if_verified", wrapped)
        assert pc.cmd_stop(reason="identity-test") == 0
        assert results
        assert results[0]["reason"] == "identity_mismatch"
        assert results[0]["killed"] is False
        assert results[0]["role"] == ident.ROLE_WATCHDOG
        _assert_survived(proc, signals, taskkills)
        out = capsys.readouterr().out
        assert "rejected PID-only match" in out
        assert "identity_mismatch" in out
    finally:
        proc.kill()
        proc.wait(timeout=5)


def test_standby_does_not_kill_wrong_role(tmp_path: Path, monkeypatch):
    proc = _sleeper()
    try:
        _redirect(monkeypatch, tmp_path)
        _write_state(proc.pid)
        _cmdline(monkeypatch, proc.pid, "python -u lh_watchdog.py --interval-sec 60")
        signals, taskkills = _watch_kills(monkeypatch)
        kills: list = []
        monkeypatch.setattr(pc, "_kill_pid", lambda *a, **k: kills.append(a))
        assert pc.enter_standby(reason="identity-test", stop_watchdog=False, force_kill_after_s=0.0) == 0
        assert kills == []
        _assert_survived(proc, signals, taskkills)
    finally:
        proc.kill()
        proc.wait(timeout=5)


def test_recover_does_not_kill_wrong_role(tmp_path: Path, monkeypatch, capsys):
    proc = _sleeper()
    try:
        _redirect(monkeypatch, tmp_path)
        _write_state(proc.pid)
        _cmdline(monkeypatch, proc.pid, "python -c import time; time.sleep(60)")
        assert ident.verified_role(proc.pid, ident.ROLE_SUPERVISOR) is False
        signals, taskkills = _watch_kills(monkeypatch)

        def _no_launch(**kwargs):
            raise AssertionError("recover spawned on a role mismatch")

        monkeypatch.setattr(pc, "_launch_supervisor", _no_launch)
        assert pc.cmd_recover() == 1
        out = capsys.readouterr().out
        assert "supervisor identity-alive" not in out
        assert "snapshot" in out
        _assert_survived(proc, signals, taskkills)
    finally:
        proc.kill()
        proc.wait(timeout=5)


def test_recover_refuses_when_role_matches(tmp_path: Path, monkeypatch, capsys):
    proc = _sleeper()
    try:
        _redirect(monkeypatch, tmp_path)
        _write_state(proc.pid)
        _cmdline(monkeypatch, proc.pid, "python -u long_horizon_supervisor.py")
        assert ident.verified_role(proc.pid, ident.ROLE_SUPERVISOR) is True
        signals, taskkills = _watch_kills(monkeypatch)

        def _no_launch(**kwargs):
            raise AssertionError("recover spawned a second supervisor")

        monkeypatch.setattr(pc, "_launch_supervisor", _no_launch)
        assert pc.cmd_recover() == 1
        out = capsys.readouterr().out
        assert "supervisor identity-alive" in out
        _assert_survived(proc, signals, taskkills)
    finally:
        proc.kill()
        proc.wait(timeout=5)


class _Completed:
    def __init__(self, stdout: str):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


def test_stop_wait_does_not_treat_substring_pid_as_alive(tmp_path: Path, monkeypatch, capsys):
    """PID 12 is a substring of PID 1234 and of ``12,345 K``. Stop must not kill it."""
    _redirect(monkeypatch, tmp_path)
    _write_state(12)
    calls: list[list] = []

    def fake_run(args, *a, **k):
        calls.append(list(args))
        return _Completed(COLLISION_STDOUT)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(subprocess, "run", fake_run)
    kills: list = []
    monkeypatch.setattr(pc, "_kill_pid", lambda *a, **k: kills.append(a))
    started = time.monotonic()
    assert pc.cmd_stop(reason="substring") == 0
    assert time.monotonic() - started < 5
    assert kills == []
    tasklists = [c for c in calls if c and c[0] == "tasklist"]
    assert tasklists
    assert "/FO" in tasklists[0] and "CSV" in tasklists[0]
    assert "12" in COLLISION_STDOUT
    out = capsys.readouterr().out
    assert "already dead" in out
    assert "rejected PID-only match" not in out


def test_launch_stop_old_does_not_kill_wrong_cmdline(tmp_path: Path, monkeypatch):
    """A stale long_horizon.pid naming a live non-supervisor must not be killed."""
    proc = _sleeper()
    try:
        meas = tmp_path / "measurements"
        logs = tmp_path / "logs"
        meas.mkdir()
        logs.mkdir()
        monkeypatch.setattr(ld, "MEAS", meas)
        monkeypatch.setattr(ld, "LOGS", logs)
        monkeypatch.setattr(ld, "LH_PID", meas / "long_horizon.pid")
        monkeypatch.setattr(ld, "LH_STOP", meas / "long_horizon_STOP")
        monkeypatch.setattr(ld, "STANDBY", meas / "long_horizon_STANDBY.json")
        monkeypatch.setattr(ld, "MANUAL", meas / "long_horizon_MANUAL_START.json")
        ld.LH_PID.write_text(f"{proc.pid}\n", encoding="utf-8")
        _cmdline(monkeypatch, proc.pid, "python -u lh_watchdog.py --interval-sec 60")
        assert ident.verified_role(proc.pid, ident.ROLE_SUPERVISOR) is False

        signals, taskkills = _watch_kills(monkeypatch)
        seen: list[dict] = []
        real = ident.kill_if_verified

        def wrapped(pid, claimed, tree=True):
            out = real(pid, claimed, tree=tree)
            seen.append(out)
            return out

        monkeypatch.setattr(ld, "kill_if_verified", wrapped)

        def _no_popen(*_a, **_k):
            raise AssertionError("stop_old continued to spawn after an unverified pid")

        monkeypatch.setattr(subprocess, "Popen", _no_popen)
        ok, detail, pid = ld.launch_lh_detached(stop_old=True, clear_latches=True, poll_s=1.0)
        assert ok is False
        assert pid is None
        assert detail == "stop_old_refused:identity_mismatch"
        assert seen and seen[0]["reason"] == "identity_mismatch"
        assert seen[0]["killed"] is False
        assert seen[0]["claimed"] == ident.ROLE_SUPERVISOR
        assert not ld.LH_PID.exists()
        _assert_survived(proc, signals, taskkills)
    finally:
        proc.kill()
        proc.wait(timeout=5)
