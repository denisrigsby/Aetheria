"""Start vs recover single-flight: at most one supervisor spawn.

Linux CI proof for the release gate "Simultaneous start/recover → ≤1 worker".
Does not launch the Windows plant. Raw detached launch and the watchdog are
outside this test.
"""
from __future__ import annotations

import json
import multiprocessing
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import plant_control as pc  # noqa: E402
from campaign_lock import CLAIM_SCHEMA, CampaignLock, pid_alive, single_flight_spawn  # noqa: E402


def _dead_pid() -> int:
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pid = int(proc.pid)
    proc.kill()
    proc.wait(timeout=5)
    deadline = time.time() + 2.0
    while time.time() < deadline and pid_alive(pid):
        time.sleep(0.01)
    if pid_alive(pid):
        raise RuntimeError("killed pid still alive")
    return pid


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
    return meas


def _valid_snapshot(tmp_path: Path) -> None:
    import campaign_snapshot as cs

    meas = tmp_path / "measurements"
    meas.mkdir(parents=True, exist_ok=True)
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n',
        encoding="utf-8",
    )
    rec = cs.write_after_green_tick(
        {
            "tick": 3,
            "last_ok": True,
            "status": "idle_between_ticks",
            "last_final_mom": 42,
            "last_tick_finished": "t",
            "heartbeat_at": "t",
        },
        tmp_path,
    )
    assert rec["ok"] is True


def _race_child(
    lock_path: str,
    claim_path: str,
    alive_path: str,
    origin: str,
    barrier,
    queue,
    inflight,
    max_seen,
    inst_lock,
    timeout_s: float,
) -> None:
    def role_alive() -> bool:
        return Path(alive_path).is_file()

    def spawn():
        with inst_lock:
            inflight.value += 1
            if inflight.value > max_seen.value:
                max_seen.value = inflight.value
        try:
            time.sleep(0.3)
            Path(alive_path).write_text(origin, encoding="utf-8")
            return {"ok": True, "pid": os.getpid(), "detail": origin}
        finally:
            with inst_lock:
                inflight.value -= 1

    try:
        barrier.wait(15)
        result = pc.single_supervisor_critical(
            spawn,
            origin=origin,
            lock_path=Path(lock_path),
            claim_path=Path(claim_path),
            role_alive=role_alive,
            timeout_s=timeout_s,
        )
        queue.put(
            {
                "origin": origin,
                "spawned": bool(result.get("spawned")),
                "reason": result.get("reason"),
                "pid": result.get("pid"),
            }
        )
    except Exception as e:
        queue.put({"origin": origin, "spawned": False, "reason": f"child_error:{type(e).__name__}"})


def test_contended_start_and_recover_admit_one_spawn(tmp_path: Path):
    """Two controllers race the same admit used by start and recover."""
    ctx = multiprocessing.get_context("spawn")
    barrier = ctx.Barrier(2)
    queue = ctx.Queue()
    inflight = ctx.Value("i", 0)
    max_seen = ctx.Value("i", 0)
    inst_lock = ctx.Lock()
    lock_path = tmp_path / "campaign_supervisor.lock"
    claim_path = tmp_path / "campaign_supervisor_claim.json"
    alive_path = tmp_path / "role_alive"
    procs = []
    for origin in ("start", "recover"):
        proc = ctx.Process(
            target=_race_child,
            args=(
                str(lock_path),
                str(claim_path),
                str(alive_path),
                origin,
                barrier,
                queue,
                inflight,
                max_seen,
                inst_lock,
                5.0,
            ),
        )
        proc.start()
        procs.append(proc)
    for proc in procs:
        proc.join(20)
    assert all(proc.exitcode == 0 for proc in procs), [p.exitcode for p in procs]
    rows = [queue.get(timeout=5) for _ in procs]
    spawned = [row for row in rows if row.get("spawned")]
    refused = [row for row in rows if not row.get("spawned")]
    assert len(spawned) == 1, rows
    assert len(refused) == 1, rows
    assert refused[0]["reason"] in {"role_alive", "claim_held"}
    assert max_seen.value == 1
    assert {row["origin"] for row in rows} == {"start", "recover"}
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    assert claim["schema"] == CLAIM_SCHEMA
    assert claim["state"] == "live"
    assert claim["role"] == "supervisor"
    blob = json.dumps(claim)
    assert str(tmp_path) not in blob
    assert "\\" not in blob
    assert "/" not in blob


def test_single_flight_timeout_does_not_spawn(tmp_path: Path):
    lock_path = tmp_path / "campaign.lock"
    started = threading.Event()
    release = threading.Event()

    def holder():
        with CampaignLock(lock_path, timeout_s=2.0) as ok:
            assert ok is True
            started.set()
            assert release.wait(2.0)

    thread = threading.Thread(target=holder)
    thread.start()
    assert started.wait(2.0)
    calls: list[int] = []
    result = single_flight_spawn(
        lock_path,
        tmp_path / "claim.json",
        role="supervisor",
        role_alive=lambda: False,
        spawn=lambda: calls.append(1) or {"ok": True, "pid": os.getpid()},
        timeout_s=0.25,
    )
    release.set()
    thread.join(2.0)
    assert result["spawned"] is False
    assert result["reason"] == "lock_timeout"
    assert calls == []


def test_live_lock_holder_fail_closed(tmp_path: Path):
    lock_path = tmp_path / "campaign.lock"
    started = threading.Event()
    release = threading.Event()

    def holder():
        with CampaignLock(lock_path, timeout_s=2.0) as ok:
            assert ok is True
            started.set()
            assert release.wait(2.0)

    thread = threading.Thread(target=holder)
    thread.start()
    assert started.wait(2.0)
    with CampaignLock(lock_path, timeout_s=0.25) as ok:
        assert ok is False
    release.set()
    thread.join(2.0)
    assert not thread.is_alive()


def test_dead_holder_lock_is_reclaimed(tmp_path: Path):
    lock_path = tmp_path / "campaign.lock"
    lock_path.write_text(f"{_dead_pid()}\n", encoding="utf-8")
    with CampaignLock(lock_path, timeout_s=2.0) as ok:
        assert ok is True
        assert lock_path.read_text(encoding="utf-8").strip() == str(os.getpid())


def test_fresh_empty_lock_is_not_stolen(tmp_path: Path):
    lock_path = tmp_path / "campaign.lock"
    lock_path.write_text("", encoding="utf-8")
    with CampaignLock(lock_path, timeout_s=0.2) as ok:
        assert ok is False


def test_corrupt_claim_refuses_spawn(tmp_path: Path):
    claim = tmp_path / "claim.json"
    claim.write_text("{", encoding="utf-8")
    calls = []

    def spawn():
        calls.append(1)
        return {"ok": True, "pid": os.getpid()}

    result = single_flight_spawn(
        tmp_path / "lock",
        claim,
        role="supervisor",
        role_alive=lambda: False,
        spawn=spawn,
        timeout_s=1.0,
    )
    assert result["spawned"] is False
    assert result["reason"] == "claim_held"
    assert calls == []


def test_dead_worker_claim_allows_next_admit(tmp_path: Path):
    claim = tmp_path / "claim.json"
    dead = _dead_pid()
    claim.write_text(
        json.dumps(
            {
                "schema": CLAIM_SCHEMA,
                "role": "supervisor",
                "state": "live",
                "owner_pid": dead,
                "worker_pid": dead,
                "token": "stale",
            }
        ),
        encoding="utf-8",
    )
    result = single_flight_spawn(
        tmp_path / "lock",
        claim,
        role="supervisor",
        role_alive=lambda: False,
        spawn=lambda: {"ok": True, "pid": os.getpid(), "detail": "again"},
        timeout_s=1.0,
    )
    assert result["spawned"] is True
    assert result["reason"] == "admitted"


def test_start_then_recover_second_does_not_launch(tmp_path: Path, monkeypatch):
    """resume (start) and cmd_recover share single_supervisor_critical."""
    meas = _redirect(monkeypatch, tmp_path)
    _valid_snapshot(tmp_path)
    (meas / "long_horizon_state.json").write_text(
        json.dumps({"tick": 1, "status": "idle_between_ticks"}),
        encoding="utf-8",
    )
    launches: list[dict] = []
    origins: list[str] = []
    reasons: list[str] = []
    real = pc.single_supervisor_critical

    def wrapped(spawn, **kwargs):
        origins.append(kwargs.get("origin"))
        result = real(spawn, **kwargs)
        reasons.append(result.get("reason"))
        return result

    def fake_launch(**kwargs):
        launches.append(kwargs)
        return {"ok": True, "pid": os.getpid(), "detail": "injected"}

    monkeypatch.setattr(pc, "single_supervisor_critical", wrapped)
    monkeypatch.setattr(pc, "_launch_supervisor", fake_launch)
    monkeypatch.setattr(pc, "wd_snap", lambda: {"alive": True, "pid": os.getpid()})

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("watchdog launch is outside this refusal")

    monkeypatch.setattr(pc.subprocess, "run", _no_subprocess)

    assert pc.resume(with_watchdog=False, cycles=1, interval_min=1, max_ticks=2) == 0
    assert pc.cmd_recover() == 1
    assert origins == ["start", "recover"]
    assert reasons == ["admitted", "claim_held"]
    assert len(launches) == 1
    claim = json.loads((meas / "campaign_supervisor_claim.json").read_text(encoding="utf-8"))
    assert claim["schema"] == CLAIM_SCHEMA
    assert claim["worker_pid"] == os.getpid()
    assert str(tmp_path) not in json.dumps(claim)
    state = json.loads((meas / "long_horizon_state.json").read_text(encoding="utf-8"))
    assert state["tick"] == 1
    assert "recovered_from_snapshot_at" not in state


def test_recover_alone_applies_snapshot_once(tmp_path: Path, monkeypatch, capsys):
    _redirect(monkeypatch, tmp_path)
    _valid_snapshot(tmp_path)
    launches: list[int] = []

    def fake_launch(**kwargs):
        launches.append(1)
        return {"ok": True, "pid": os.getpid(), "detail": "injected"}

    monkeypatch.setattr(pc, "_launch_supervisor", fake_launch)
    monkeypatch.setattr(pc, "wd_snap", lambda: {"alive": True, "pid": os.getpid()})
    assert pc.cmd_recover() == 0
    assert launches == [1]
    state = json.loads((tmp_path / "measurements" / "long_horizon_state.json").read_text(encoding="utf-8"))
    assert state["persisted_mom"] == 42
    assert state["recovered_from_snapshot_at"]
    out = capsys.readouterr().out
    assert "single-flight" in out
    assert str(tmp_path) not in out
