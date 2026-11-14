"""Recovery ack binds raw snapshot bytes and is consumed once."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

import plant_control as pc  # noqa: E402
import recovery_ack as rack  # noqa: E402


def _raw_snapshot(*, last_ok: bool, spaced: bool = False) -> bytes:
    flag = "true" if last_ok else "false"
    if spaced:
        body = (
            "{\n"
            '  "schema": "aetheria_campaign_snapshot_v1",\n'
            '  "campaign": {\n'
            f'    "last_ok": {flag},\n'
            '    "mom": 1\n'
            "  }\n"
            "}\n"
        )
    else:
        body = (
            '{"schema":"aetheria_campaign_snapshot_v1",'
            f'"campaign":{{"last_ok":{flag},"mom":1}}}}'
        )
    return body.encode("utf-8")


def _install(monkeypatch, tmp_path: Path, *, raw: bytes, state: dict) -> Path:
    monkeypatch.setenv("AETHERIA_ROOT", str(tmp_path))
    meas = tmp_path / "measurements"
    meas.mkdir(parents=True, exist_ok=True)
    (meas / "campaign_snapshot_v1.json").write_bytes(raw)
    (meas / "long_horizon_state.json").write_text(
        json.dumps(state), encoding="utf-8"
    )
    return meas


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


def _green(tmp_path: Path) -> None:
    import campaign_snapshot as cs

    meas = tmp_path / "measurements"
    meas.mkdir(parents=True, exist_ok=True)
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n', encoding="utf-8"
    )
    rec = cs.write_after_green_tick(
        {
            "tick": 2,
            "last_ok": True,
            "status": "idle_between_ticks",
            "last_final_mom": 7,
            "last_tick_finished": "t",
            "heartbeat_at": "t",
        },
        tmp_path,
    )
    assert rec["ok"] is True


def test_valid_ack_works_once_then_refused_after_consume(tmp_path: Path, monkeypatch):
    raw = _raw_snapshot(last_ok=False, spaced=True)
    meas = _install(
        monkeypatch,
        tmp_path,
        raw=raw,
        state={"last_ok": False, "running_tick": False},
    )
    written = rack.write_ack(tmp_path)
    assert written["snapshot_sha256"] == rack.snapshot_hash(raw)
    assert written["snapshot_sha256"] == hashlib.sha256(raw).hexdigest()
    ok, dirty, reason = rack.verify_ack(tmp_path)
    assert (ok, dirty, reason) == (True, True, "acked")
    dest = rack.consume_ack(tmp_path)
    assert dest.name == "recovery_ack_v1.consumed.json"
    assert not (meas / "recovery_ack_v1.json").exists()
    assert dest.is_file()
    ok2, dirty2, reason2 = rack.verify_ack(tmp_path)
    assert ok2 is False and dirty2 is True
    assert reason2 == "ack_required"
    with pytest.raises(rack.AckRefused):
        rack.consume_ack(tmp_path)


def test_reserialized_snapshot_hash_is_refused(tmp_path: Path, monkeypatch):
    raw = _raw_snapshot(last_ok=False, spaced=True)
    _install(
        monkeypatch,
        tmp_path,
        raw=raw,
        state={"last_ok": True, "running_tick": False},
    )
    reserialized = json.dumps(json.loads(raw.decode("utf-8"))).encode("utf-8")
    assert reserialized != raw
    bad = hashlib.sha256(reserialized).hexdigest()
    assert bad != rack.snapshot_hash(raw)
    ack = {
        "schema": rack.ACK_SCHEMA,
        "snapshot_sha256": bad,
    }
    (tmp_path / "measurements" / "recovery_ack_v1.json").write_text(
        json.dumps(ack), encoding="utf-8"
    )
    ok, dirty, reason = rack.verify_ack(tmp_path)
    assert ok is False and dirty is True
    assert reason == "snapshot_hash_mismatch"


def test_clean_plant_needs_no_ack(tmp_path: Path, monkeypatch):
    raw = _raw_snapshot(last_ok=True)
    meas = _install(
        monkeypatch,
        tmp_path,
        raw=raw,
        state={"last_ok": True, "running_tick": False},
    )
    assert rack.is_dirty(json.loads(raw.decode("utf-8")), {"last_ok": True}) is False
    ok, dirty, reason = rack.verify_ack(tmp_path)
    assert (ok, dirty, reason) == (True, False, "clean")
    assert not (meas / "recovery_ack_v1.json").exists()
    with pytest.raises(rack.AckRefused) as raised:
        rack.write_ack(tmp_path)
    assert raised.value.reason == "clean"
    assert not (meas / "recovery_ack_v1.json").exists()


def test_running_tick_marker_makes_plant_dirty(tmp_path: Path, monkeypatch):
    raw = _raw_snapshot(last_ok=True)
    snap = json.loads(raw.decode("utf-8"))
    clean_state = {"last_ok": True, "running_tick": False}
    dirty_state = {"last_ok": True, "running_tick": True}
    assert rack.is_dirty(snap, clean_state) is False
    assert rack.is_dirty(snap, dirty_state) is True
    _install(monkeypatch, tmp_path, raw=raw, state=dirty_state)
    ok, dirty, reason = rack.verify_ack(tmp_path)
    assert ok is False and dirty is True
    assert reason == "ack_required"
    rack.write_ack(tmp_path)
    ok2, dirty2, reason2 = rack.verify_ack(tmp_path)
    assert (ok2, dirty2, reason2) == (True, True, "acked")


def test_cmd_recover_refuses_dirty_without_ack(tmp_path: Path, monkeypatch, capsys):
    _redirect(monkeypatch, tmp_path)
    _green(tmp_path)
    (tmp_path / "measurements" / "long_horizon_state.json").write_text(
        json.dumps({"last_ok": False, "running_tick": False}),
        encoding="utf-8",
    )
    calls: list[int] = []
    monkeypatch.setattr(pc, "resume", lambda **kwargs: calls.append(1) or 0)
    assert pc.cmd_recover() == 1
    assert calls == []
    assert "FAIL" in capsys.readouterr().out


def test_cmd_recover_consumes_ack_only_after_successful_resume(
    tmp_path: Path, monkeypatch
):
    meas = _redirect(monkeypatch, tmp_path)
    _green(tmp_path)
    (meas / "long_horizon_state.json").write_text(
        json.dumps({"last_ok": False}),
        encoding="utf-8",
    )
    rack.write_ack(tmp_path)
    monkeypatch.setattr(pc, "resume", lambda **kwargs: 1)
    assert pc.cmd_recover() == 1
    assert (meas / "recovery_ack_v1.json").is_file()
    assert not (meas / "recovery_ack_v1.consumed.json").exists()

    monkeypatch.setattr(pc, "resume", lambda **kwargs: 0)
    assert pc.cmd_recover() == 0
    assert not (meas / "recovery_ack_v1.json").exists()
    assert (meas / "recovery_ack_v1.consumed.json").is_file()


def test_operator_ack_writer_requires_dead_identity_and_valid_snapshot(
    tmp_path: Path, monkeypatch, capsys
):
    meas = _redirect(monkeypatch, tmp_path)
    (meas / "long_horizon_state.json").write_text(
        json.dumps({"last_ok": False}),
        encoding="utf-8",
    )
    assert pc.cmd_recover_ack() == 1
    assert "snapshot" in capsys.readouterr().out
    assert not (meas / "recovery_ack_v1.json").exists()

    _green(tmp_path)
    monkeypatch.setattr(
        pc,
        "plant_snap",
        lambda: {"pid": 99, "pid_exists": True, "identity_ok": True, "alive": True},
    )
    assert pc.cmd_recover_ack() == 1
    assert not (meas / "recovery_ack_v1.json").exists()

    monkeypatch.setattr(
        pc,
        "plant_snap",
        lambda: {"pid": None, "pid_exists": False, "identity_ok": False, "alive": False},
    )
    assert pc.cmd_recover_ack() == 0
    assert (meas / "recovery_ack_v1.json").is_file()
    ok, dirty, reason = rack.verify_ack(tmp_path)
    assert (ok, dirty, reason) == (True, True, "acked")


def test_operator_ack_refuses_live_pid_when_role_cannot_be_disproved(
    tmp_path: Path, monkeypatch, capsys
):
    _redirect(monkeypatch, tmp_path)
    _green(tmp_path)
    (tmp_path / "measurements" / "long_horizon_state.json").write_text(
        json.dumps({"pid": 99, "last_ok": False}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        pc,
        "plant_snap",
        lambda: {"pid": 99, "pid_exists": True, "identity_ok": False, "alive": False},
    )
    monkeypatch.setattr(pc, "cmdline_for_pid", lambda pid: None)
    assert pc.cmd_recover_ack() == 1
    assert not (tmp_path / "measurements" / "recovery_ack_v1.json").exists()
    assert "cannot be disproved" in capsys.readouterr().out


def test_aetheria_recover_ack_does_not_spawn(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "aetheria_cli_ack", ROOT / "scripts" / "aetheria.py"
    )
    cli = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(cli)
    called: list[str] = []
    monkeypatch.setattr(pc, "cmd_recover", lambda: called.append("recover") or 0)
    monkeypatch.setattr(pc, "cmd_recover_ack", lambda: called.append("ack") or 0)
    assert cli.main(["recover", "--ack"]) == 2
    assert called == []
    assert cli.main(["recover"]) == 0
    assert called == ["recover"]


def test_prime_ctl_cannot_reach_ack_writer():
    text = (ROOT / "scripts" / "prime_ctl.py").read_text(encoding="utf-8")
    assert "recover-ack" not in text
    assert "recovery_ack" not in text
    assert "import socket" not in text
    assert "socket." not in text
