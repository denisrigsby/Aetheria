"""Fixed ecologies, lineage, bounded population, local benchmark."""
from __future__ import annotations

import json
from pathlib import Path

from research.evaluate import compare_ecologies
from research.experiment import create_run, record_candidate
from research.population import PopulationController

REPO = Path(__file__).resolve().parents[1]
ECOLOGIES = [
    "single_generalist",
    "planner_executor",
    "planner_executor_critic",
    "parallel_specialists_synthesizer",
    "hierarchical_coordinator",
]


def test_genomes_load_and_deny_network():
    for name in ECOLOGIES:
        g = json.loads((REPO / "research" / "ecologies" / f"{name}.json").read_text(encoding="utf-8"))
        assert g["schema"] == "aetheria_genome_v1"
        assert g["network_access"] is False
        assert g["promotion"] == "research"
        assert g["resource_budget"]["max_active_workers"] <= 32


def test_population_bounds():
    p = PopulationController(max_active=2, max_depth=2)
    a = p.spawn("planner")
    b = p.spawn("executor", parent_id=a.worker_id)
    c = p.spawn("extra", parent_id=b.worker_id)
    assert a and b
    assert c is None
    assert "rejected:max_active" in p.spawn_log or p.active_count() <= 2
    p.pause()
    assert p.spawn("x") is None


def test_compare_visible_and_held_out():
    table = compare_ecologies(REPO, ECOLOGIES, include_held_out=True)
    assert len(table["ecologies"]) == 5
    gen = table["ecologies"]["single_generalist"]
    assert gen["n"] >= 6
    # at least some deterministic tasks pass
    assert gen["ok"] >= 1
    # all five can be compared under the same task set
    ns = {table["ecologies"][k]["n"] for k in ECOLOGIES}
    assert len(ns) == 1


def test_lineage_record(tmp_path: Path):
    # create_run expects repo_root/research/runs
    fake = tmp_path
    (fake / "research").mkdir()
    run = create_run(fake, "lineage")
    rec = {
        "schema": "aetheria_candidate_v1",
        "candidate_id": "c1",
        "parent_ids": [],
        "generation": 0,
        "creation_time": "2026-01-01T00:00:00Z",
        "genome": json.loads((REPO / "research" / "ecologies" / "single_generalist.json").read_text(encoding="utf-8")),
        "task_set": ["contradiction_detection"],
        "resource_limits": {"max_active_workers": 1},
        "results": {},
        "scores": {"Q": 1},
        "failures": [],
        "regressions": [],
        "artifacts": [],
        "promotion_status": "research",
    }
    path = record_candidate(run, rec)
    assert path.is_file()
    assert json.loads(path.read_text(encoding="utf-8"))["parent_ids"] == []
