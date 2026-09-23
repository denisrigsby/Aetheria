"""Disposable-root tests for campaign_snapshot_v1. No live plant."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(monkeypatch, tmp_path):
    import importlib.util
    import sys

    monkeypatch.setenv("AETHERIA_ROOT", str(tmp_path))
    scripts = str(REPO / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location(
        "campaign_snapshot", REPO / "scripts" / "campaign_snapshot.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_write_after_green_and_backup(tmp_path, monkeypatch):
    cs = _load(monkeypatch, tmp_path)
    meas = tmp_path / "measurements"
    meas.mkdir()
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n', encoding="utf-8"
    )
    state = {
        "tick": 3,
        "last_ok": True,
        "status": "idle_between_ticks",
        "last_final_mom": 42,
        "last_tick_finished": "t",
        "heartbeat_at": "t",
    }
    rec = cs.write_after_green_tick(state, tmp_path)
    assert rec["ok"] is True
    snap = json.loads((meas / "campaign_snapshot_v1.json").read_text(encoding="utf-8"))
    assert snap["schema"] == "aetheria_campaign_snapshot_v1"
    assert snap["campaign"]["mom"] == 42
    assert snap["campaign"]["last_ok"] is True
    assert snap["green_log"]["bytes"] > 0
    assert snap["green_log"]["last_line_sha256"]
    loaded, why = cs.load_snapshot(tmp_path)
    assert why == "ok"
    assert loaded["campaign"]["mom"] == 42
    backups = list((tmp_path / "backups" / "measurements").iterdir())
    assert backups


def test_skip_dirty_and_running(tmp_path, monkeypatch):
    cs = _load(monkeypatch, tmp_path)
    (tmp_path / "measurements").mkdir()
    bad = cs.write_after_green_tick({"last_ok": False, "status": "idle_between_ticks"}, tmp_path)
    assert bad["written"] is False
    run = cs.write_after_green_tick(
        {"last_ok": True, "status": "running_tick"}, tmp_path
    )
    assert run["written"] is False
    (tmp_path / "measurements" / "long_horizon_STOP").write_text("stop", encoding="utf-8")
    stop = cs.write_after_green_tick(
        {"last_ok": True, "status": "idle_between_ticks"}, tmp_path
    )
    assert stop["reason"] == "stop_in_progress"


def test_stale_green_log_rejects_recover(tmp_path, monkeypatch):
    cs = _load(monkeypatch, tmp_path)
    meas = tmp_path / "measurements"
    meas.mkdir()
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n', encoding="utf-8"
    )
    cs.write_after_green_tick(
        {
            "tick": 1,
            "last_ok": True,
            "status": "idle_between_ticks",
            "last_final_mom": 1,
        },
        tmp_path,
    )
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n{"ts":"t2","tick":2,"ok":true}\n',
        encoding="utf-8",
    )
    rec, why = cs.load_snapshot(tmp_path)
    assert rec is None
    assert why == "green_log_stale"
