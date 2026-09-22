"""Start vs recover single-flight: at most one supervisor spawn.

Linux CI proof for the release gate "Simultaneous start/recover → ≤1 worker".
Does not launch the Windows plant. Raw detached launch and the watchdog are
outside this test.
"""
from __future__ import annotations

import json
import multiprocessing
import os
import re
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
from campaign_lock import (  # noqa: E402
    CLAIM_SCHEMA,
    CampaignLock,
    normalize_create_time,
    pid_alive,
    single_flight_spawn,
)


def _release_popen(proc: subprocess.Popen) -> None:
    """Drop the process handle so a dead PID is not still queryable."""
    for stream in (proc.stdout, proc.stderr, proc.stdin):
        if stream is None:
            continue
        try:
            stream.close()
        except OSError:
            pass
    if sys.platform == "win32":
        handle = getattr(proc, "_handle", None)
        if handle:
            import ctypes

            ctypes.windll.kernel32.CloseHandle(handle)
            proc._handle = None


def _dead_pid() -> int:
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pid = int(proc.pid)
    proc.kill()
    proc.wait(timeout=5)
    _release_popen(proc)
    deadline = time.time() + 5.0
    while time.time() < deadline and pid_alive(pid):
        time.sleep(0.05)
    if pid_alive(pid):
        raise RuntimeError("killed pid still alive")
    return pid


_PATH_SHAPE = re.compile(
    r"([A-Za-z]:[\\/])|(/home/)|(/tmp/)|(/opt/)|(/usr/)|(/var/)|(/workspace/)|(/Users/)|([\\]Users[\\])",
    re.IGNORECASE,
)


def _assert_no_host_path(blob: str) -> None:
    """Reject host paths. Slash-bearing create_time tokens are not paths."""
    assert "\\" not in blob
    assert _PATH_SHAPE.search(blob) is None


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
    _assert_no_host_path(blob)
    assert str(tmp_path) not in blob
    for key in ("worker_create_time", "owner_create_time"):
        val = claim.get(key)
        if val is not None:
            assert "/" not in str(val)
            assert "\\" not in str(val)


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

    real_run = pc.subprocess.run

    def _guard_subprocess(args, *pos, **kwargs):
        cmd = args if isinstance(args, (list, tuple)) else kwargs.get("args", args)
        flat = " ".join(str(part) for part in cmd) if isinstance(cmd, (list, tuple)) else str(cmd)
        if "launch_lh_watchdog" in flat:
            raise AssertionError("watchdog launch is outside this refusal")
        return real_run(args, *pos, **kwargs)

    monkeypatch.setattr(pc.subprocess, "run", _guard_subprocess)

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


def test_launcher_argv_is_accepted_by_supervisor():
    from launch_lh_detached import supervisor_argv
    from long_horizon_supervisor import make_parser

    argv = supervisor_argv(
        "python",
        "scripts/long_horizon_supervisor.py",
        cycles=2,
        interval_min=30.0,
        max_ticks=48,
        backup_every=4,
        continue_tick=True,
        once=False,
        ignore_standby=True,
    )
    args = make_parser().parse_args(argv[3:])
    assert args.continue_tick is True
    assert args.ignore_standby is True
    assert args.cycles == 2
    with pytest.raises(SystemExit):
        make_parser().parse_args(argv[3:] + ["--not-a-supervisor-flag"])


def test_continue_tick_and_standby_fail_closed(tmp_path: Path):
    from long_horizon_supervisor import resolve_continue_tick, standby_blocks

    assert resolve_continue_tick(tmp_path / "missing.json", True)["tick"] == 0
    good = tmp_path / "state.json"
    good.write_text(json.dumps({"tick": 4, "persisted_mom": 3}), encoding="utf-8")
    got = resolve_continue_tick(good, True)
    assert got["ok"] is True and got["tick"] == 4
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    assert resolve_continue_tick(bad, True)["reason"] == "state_unreadable"
    secret = tmp_path / "secret.json"
    secret.write_text(json.dumps({"tick": 1, "api_key": "x"}), encoding="utf-8")
    refused = resolve_continue_tick(secret, True)
    assert refused["ok"] is False
    assert refused["reason"] == "secret_field"
    assert refused["prior"] == {}
    standby = tmp_path / "long_horizon_STANDBY.json"
    standby.write_text("{}", encoding="utf-8")
    assert standby_blocks(standby, False) is True
    assert standby_blocks(standby, True) is False


def test_reused_pid_create_time_does_not_block_or_kill(tmp_path: Path):
    claim = tmp_path / "claim.json"
    claim.write_text(
        json.dumps(
            {
                "schema": CLAIM_SCHEMA,
                "role": "supervisor",
                "state": "live",
                "owner_pid": os.getpid(),
                "worker_pid": os.getpid(),
                "worker_create_time": "100",
                "claim_id": "old",
            }
        ),
        encoding="utf-8",
    )
    calls: list[int] = []
    result = single_flight_spawn(
        tmp_path / "lock",
        claim,
        role="supervisor",
        role_alive=lambda: False,
        spawn=lambda: calls.append(1) or {"ok": True, "pid": os.getpid()},
        timeout_s=1.0,
        pid_alive_fn=lambda _p: True,
        create_time_fn=lambda _p: "200",
    )
    assert result["spawned"] is True
    assert result["reason"] == "admitted"
    assert calls == [1]


def test_matching_or_unreadable_create_time_blocks(tmp_path: Path):
    claim = tmp_path / "claim.json"
    body = {
        "schema": CLAIM_SCHEMA,
        "role": "supervisor",
        "state": "live",
        "owner_pid": os.getpid(),
        "worker_pid": os.getpid(),
        "worker_create_time": "100",
        "claim_id": "live",
    }
    claim.write_text(json.dumps(body), encoding="utf-8")
    calls: list[int] = []

    def spawn():
        calls.append(1)
        return {"ok": True, "pid": os.getpid()}

    matched = single_flight_spawn(
        tmp_path / "lock-a",
        claim,
        role="supervisor",
        role_alive=lambda: False,
        spawn=spawn,
        timeout_s=1.0,
        pid_alive_fn=lambda _p: True,
        create_time_fn=lambda _p: "100",
    )
    assert matched["spawned"] is False and matched["reason"] == "claim_held"
    unreadable = single_flight_spawn(
        tmp_path / "lock-b",
        claim,
        role="supervisor",
        role_alive=lambda: False,
        spawn=spawn,
        timeout_s=1.0,
        pid_alive_fn=lambda _p: True,
        create_time_fn=lambda _p: None,
    )
    assert unreadable["spawned"] is False and unreadable["reason"] == "claim_held"
    assert calls == []


def test_aetheria_start_flags_reach_resume(monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "aetheria_cli_under_test", ROOT / "scripts" / "aetheria.py"
    )
    cli = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(cli)
    seen: dict = {}

    def fake_resume(**kwargs):
        seen.update(kwargs)
        return 0

    monkeypatch.setattr(pc, "resume", fake_resume)
    assert cli.main(["start", "--cycles", "4", "--interval-min", "5", "--max-ticks", "9", "--fresh-segment"]) == 0
    assert seen["cycles"] == 4
    assert seen["interval_min"] == 5.0
    assert seen["max_ticks"] == 9
    assert seen["continue_tick"] is False
    assert seen["with_watchdog"] is True
    assert cli.main(["resume", "--not-a-flag"]) == 2
    assert seen["cycles"] == 4


def test_create_time_normalizes_without_storing_a_path():
    assert normalize_create_time(r"/Date(1710000000000)/") == "ms:1710000000000"
    assert normalize_create_time(r"\/Date(1710000000000)\/") == "ms:1710000000000"
    assert normalize_create_time("/Date(1710000000000)/") == normalize_create_time(
        r"\/Date(1710000000000)\/"
    )
    assert normalize_create_time("20260922054822.123456-000") == "wmi:20260922054822123456"
    assert normalize_create_time("84952") == "boot:84952"
    assert normalize_create_time("boot:84952") == "boot:84952"
    assert normalize_create_time(r"C:\Users\operator\plant") is None
    assert normalize_create_time("/home/operator/plant") is None
    assert normalize_create_time("/tmp/campaign") is None


def test_admit_launch_does_not_kill_from_pid_file():
    kw = pc.admit_launch_kwargs(cycles=2, interval_min=30.0, max_ticks=48, continue_tick=True)
    assert kw["stop_old"] is False


def test_secret_state_field_does_not_spawn(tmp_path: Path, monkeypatch):
    meas = _redirect(monkeypatch, tmp_path)
    (meas / "long_horizon_state.json").write_text(
        json.dumps({"tick": 1, "api_key": "do-not-copy"}),
        encoding="utf-8",
    )
    launches: list[int] = []
    monkeypatch.setattr(
        pc,
        "_launch_supervisor",
        lambda **_k: launches.append(1) or {"ok": True, "pid": os.getpid(), "detail": "no"},
    )
    assert pc.resume(with_watchdog=False, cycles=1, interval_min=1.0, max_ticks=2) == 1
    assert launches == []
    kept = (meas / "long_horizon_state.json").read_text(encoding="utf-8")
    assert "api_key" in kept
