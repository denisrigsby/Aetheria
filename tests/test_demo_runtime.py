"""Mock cycle body: no LLM, no plant start, supervisor contract."""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_demo_runtime_writes_contract(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERIA_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERIA_NUM_CYCLES", "3")
    monkeypatch.setenv("AETHERIA_DEMO_SLEEP_S", "0")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "demo_runtime", REPO / "scripts" / "demo_runtime.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rec = mod.run(3)
    assert rec["ok"] is True
    assert rec["cycles_complete"] == 3
    assert rec["schema"] == "lh_probe_summary_v1"
    assert rec["runner"] == "demo_runtime"
    summary = json.loads((tmp_path / "measurements" / "lh_probe_summary_latest.json").read_text(encoding="utf-8"))
    assert summary["ok"] is True
    hb = json.loads((tmp_path / "measurements" / "demo_heartbeat.json").read_text(encoding="utf-8"))
    assert hb["cycle"] == 3
    ck = json.loads((tmp_path / "measurements" / "demo_checkpoint.json").read_text(encoding="utf-8"))
    assert ck["progress"] == "100%"
    green = (tmp_path / "measurements" / "demo_green_ticks.jsonl").read_text(encoding="utf-8")
    assert green.count("demo_green") == 3


def test_supervisor_runs_mock_runtime(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)
    monkeypatch.setenv("AETHERIA_DEMO_SLEEP_S", "0")
    monkeypatch.setenv("AETHERIA_PROBE_TIMEOUT_S", "30")
    monkeypatch.setenv("AETHERIA_DEMO", "1")
    sys_path_scripts = str(REPO / "scripts")
    import sys

    if sys_path_scripts not in sys.path:
        sys.path.insert(0, sys_path_scripts)
    import long_horizon_supervisor as lh

    rec = lh.run_probe_cycles(
        2, tick=0, probe_script=REPO / "scripts" / "demo_runtime.py"
    )
    assert rec.get("ok") is True, rec
    contract = REPO / "measurements" / "lh_probe_summary_latest.json"
    assert contract.is_file()
    body = json.loads(contract.read_text(encoding="utf-8"))
    assert body.get("ok") is True
    assert int(body.get("cycles_complete") or 0) >= 2
    hb = REPO / "measurements" / "demo_heartbeat.json"
    assert hb.is_file()
