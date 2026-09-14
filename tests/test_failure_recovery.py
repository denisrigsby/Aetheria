"""Failure-recovery without starting the plant."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import lh_process_identity as ident
from research.experiment import _atomic_write, create_run, record_candidate
from research.population import PopulationController

REPO = Path(__file__).resolve().parents[1]


def test_atomic_write_leaves_valid_json(tmp_path: Path):
    p = tmp_path / "s.json"
    _atomic_write(p, {"schema": "t", "n": 1})
    assert json.loads(p.read_text(encoding="utf-8"))["n"] == 1
    assert not list(tmp_path.glob("*.tmp"))


def test_malformed_json_does_not_crash_create_run(tmp_path: Path):
    root = create_run(tmp_path, "x")
    bad = root / "broken.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        json.loads(bad.read_text(encoding="utf-8"))
    # run metadata still valid
    meta = json.loads((root / "experiment.json").read_text(encoding="utf-8"))
    assert meta["schema"] == "aetheria_experiment_v1"


def test_failed_candidate_is_preserved(tmp_path: Path):
    root = create_run(tmp_path, "fail")
    cand = {
        "schema": "aetheria_candidate_v1",
        "candidate_id": "c_fail",
        "parent_ids": [],
        "generation": 0,
        "creation_time": "2026-01-01T00:00:00Z",
        "genome": {"name": "x"},
        "task_set": ["t"],
        "resource_limits": {},
        "failures": ["boom"],
        "promotion_status": "rejected",
    }
    path = record_candidate(root, cand)
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["failures"] == ["boom"]
    assert loaded["promotion_status"] == "rejected"


def test_cancel_all_leaves_no_active_workers():
    p = PopulationController(max_active=3, max_depth=2)
    p.spawn("a")
    p.spawn("b")
    p.cancel_all()
    assert p.active_count() == 0


def test_pid_exists_junk():
    assert ident.pid_exists(None) is False
    assert ident.pid_exists("x") is False
    assert ident.verified_role(42424242, ident.ROLE_SUPERVISOR) is False
