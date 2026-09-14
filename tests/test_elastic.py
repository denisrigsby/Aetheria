"""Elastic controller: bounds, plateau, interrupt, recovery."""
from __future__ import annotations

from research.elastic import ElasticController
from research.evaluate import compare_ecologies
from research.experiment import create_run, record_candidate
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_never_exceeds_active_or_model_caps():
    e = ElasticController(max_active=3, max_depth=2, max_seconds=5, max_model_calls=0, start_workers=1)
    for i in range(20):
        e.step(0.1 * (i % 3))
        assert e.pop.active_count() <= 3
        assert e.record_model_call() is False
    e.finish()
    assert e.model_calls == 0


def test_plateau_stops_spawning():
    e = ElasticController(max_active=8, max_depth=3, max_seconds=30, start_workers=1, plateau_needed=2)
    e.step(0.5)
    e.step(0.5)
    st = e.step(0.5)
    assert st == "stop"
    assert e.stopped == "plateau"
    assert e.pop.paused is True


def test_interrupt_queued_and_active():
    e = ElasticController(max_active=4, max_depth=3, max_seconds=30, start_workers=1, interrupt_after_events=1)
    st = e.step(0.2)
    assert st == "interrupted"
    e.cancel_overdue()
    fin = e.finish()
    assert fin["active"] == 0
    assert fin["stopped"] == "interrupted"


def test_interrupt_during_expansion_then_cleanup():
    e = ElasticController(max_active=4, max_depth=3, max_seconds=30, start_workers=1)
    e.step(0.1)
    e.step(0.7)
    e.interrupt_after_events = len(e.events)
    st = e.step(0.9)
    assert st == "interrupted"
    e.cancel_overdue()
    assert e.pop.active_count() == 0


def test_interrupt_during_retirement():
    e = ElasticController(max_active=3, max_depth=2, max_seconds=30, start_workers=2)
    wid = e.pop.workers[0].worker_id
    e.retire(wid)
    e.cancel_overdue()
    assert e.pop.active_count() == 0
    assert any(ev["kind"] == "retire" for ev in e.events)


def test_failed_candidate_kept_after_interrupt(tmp_path: Path):
    run = create_run(tmp_path, "int")
    e = ElasticController(max_active=2, max_depth=2, max_seconds=30, start_workers=1, interrupt_after_events=2)
    e.step(0.1)
    fin = e.finish()
    rec = {
        "schema": "aetheria_candidate_v1",
        "candidate_id": "elastic_int",
        "parent_ids": [],
        "generation": 0,
        "creation_time": "2026-01-01T00:00:00Z",
        "genome": {"name": "elastic"},
        "task_set": ["x"],
        "resource_limits": {"max_active": 2},
        "results": fin,
        "scores": {},
        "failures": ["interrupted"],
        "regressions": [],
        "artifacts": [],
        "promotion_status": "rejected",
    }
    path = record_candidate(run, rec)
    assert path.is_file()
    assert "interrupted" in path.read_text(encoding="utf-8")


def test_baselines_still_comparable():
    table = compare_ecologies(
        REPO,
        [
            "single_generalist",
            "planner_executor",
            "planner_executor_critic",
            "parallel_specialists_synthesizer",
            "hierarchical_coordinator",
        ],
        include_held_out=True,
    )
    ns = {v["n"] for v in table["ecologies"].values()}
    assert len(ns) == 1
