"""Candidates cannot rewrite the evaluator, suite, or ceilings."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from research.elastic import ElasticController
from research.evaluate import (
    compare_ecologies,
    load_profile,
    load_suite,
    run_task,
    sanitize_genome,
)

REPO = Path(__file__).resolve().parents[1]
ECOLOGIES = [
    "single_generalist",
    "planner_executor",
    "planner_executor_critic",
    "parallel_specialists_synthesizer",
    "hierarchical_coordinator",
]


def test_visible_held_out_disjoint_and_different_strings():
    suite = load_suite(REPO)
    vis = set(suite["visible_tasks"])
    held = set(suite["held_out_tasks"])
    assert vis.isdisjoint(held)
    vdocs = (suite["tasks"]["multi_doc_synthesis"].get("docs") or [])
    hdocs = (suite["tasks"]["held_out_multi_doc"].get("docs") or [])
    assert vdocs != hdocs


def test_sanitize_strips_suite_overrides_and_clamps_ceiling():
    prof = load_profile(REPO)
    dirty = {
        "schema": "aetheria_genome_v1",
        "name": "attack",
        "roles": ["generalist"],
        "visible_tasks": [],
        "held_out_tasks": [],
        "tasks": {"deliberate_error": {"claim": "ok"}},
        "scoring": {"always": 1},
        "promotion_status": "production",
        "promotion": "production",
        "network_access": True,
        "resource_budget": {
            "max_active_workers": 999,
            "max_depth": 99,
            "max_seconds": 999,
            "max_model_calls": 50,
        },
    }
    clean = sanitize_genome(dirty, prof)
    assert "visible_tasks" not in clean
    assert "tasks" not in clean
    assert "scoring" not in clean
    assert clean["promotion"] == "research"
    assert clean["network_access"] is False
    assert clean["resource_budget"]["max_active_workers"] <= int(prof["max_active_workers"])
    assert clean["resource_budget"]["max_model_calls"] == 0


def test_poisoned_genome_cannot_change_held_out_or_scoring():
    suite = load_suite(REPO)
    genome = json.loads((REPO / "research" / "ecologies" / "single_generalist.json").read_text(encoding="utf-8"))
    poison = copy.deepcopy(genome)
    poison["held_out_tasks"] = []
    poison["visible_tasks"] = ["deliberate_error"]
    poison["tasks"] = {"deliberate_error": {"claim": "2+2=4"}}
    poison["promotion"] = "promoted_test"
    spec = suite["tasks"]["deliberate_error"]
    a = run_task("deliberate_error", spec, genome)
    b = run_task("deliberate_error", spec, poison)
    assert a["ok"] == b["ok"] is False
    assert load_suite(REPO)["held_out_tasks"] == suite["held_out_tasks"]


def test_repeated_comparison_stable():
    a = compare_ecologies(REPO, ECOLOGIES, include_held_out=True)
    b = compare_ecologies(REPO, ECOLOGIES, include_held_out=True)
    assert {k: a["ecologies"][k]["ok"] for k in ECOLOGIES} == {
        k: b["ecologies"][k]["ok"] for k in ECOLOGIES
    }
    assert "explanation" in a
    assert a["explanation"]["per_task"]


def test_elastic_respects_profile_on_v2():
    prof = load_profile(REPO)
    cap = int(prof["max_active_workers"])
    e = ElasticController(
        max_active=cap,
        max_depth=int(prof.get("max_task_depth") or 4),
        max_seconds=5,
        max_model_calls=int(prof.get("max_model_calls") or 0),
        start_workers=1,
    )
    table = compare_ecologies(REPO, ["single_generalist"], include_held_out=False)
    progress = table["ecologies"]["single_generalist"]["ok"] / max(1, table["ecologies"]["single_generalist"]["n"])
    for _ in range(20):
        st = e.step(progress)
        assert e.pop.active_count() <= cap
        assert e.record_model_call() is False
        if st != "continue":
            break
    e.cancel_overdue()
    fin = e.finish()
    assert fin["active"] == 0
    assert fin["model_calls"] == 0
    assert e.pop.active_count() == 0
