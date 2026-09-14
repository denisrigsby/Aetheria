"""Communication-edge-only mutation. No role/prompt changes. No production plant."""
from __future__ import annotations

import json
from pathlib import Path

from research.evaluate import compare_ecologies, score_genome
from research.topology import mutate_edges, neighborhood, topology_edges
from research.topology_experiment import run_edge_search

REPO = Path(__file__).resolve().parents[1]


def _pec():
    return json.loads((REPO / "research" / "ecologies" / "planner_executor_critic.json").read_text(encoding="utf-8"))


def test_fixed_baselines_still_discriminate():
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
    oks = {k: table["ecologies"][k]["ok"] for k in table["ecologies"]}
    assert len(set(oks.values())) >= 3
    assert oks["planner_executor_critic"] >= oks["single_generalist"]


def test_mutate_edges_does_not_change_roles_or_prompts():
    p = _pec()
    child = mutate_edges(p, "remove", ("executor", "critic"))
    assert child["roles"] == p["roles"]
    assert child["role_prompts"] == p["role_prompts"]
    assert child["resource_budget"]["max_model_calls"] == 0
    assert child["network_access"] is False
    assert child["promotion"] == "research"
    assert ("executor", "critic") not in topology_edges(child)


def test_removing_critic_edge_drops_error_detection():
    p = _pec()
    parent = score_genome(REPO, "pec", p, True)
    child = mutate_edges(p, "remove", ("executor", "critic"))
    dropped = score_genome(REPO, "ablate", child, True)
    def _ok(row, task):
        return next(r for r in row["results"] if r["task"] == task)["ok"]
    assert _ok(parent, "deliberate_error") is True
    assert _ok(dropped, "deliberate_error") is False
    assert dropped["ok"] < parent["ok"]


def test_neighborhood_bounded_and_legal():
    p = _pec()
    kids = neighborhood(p)
    n = len(p["roles"])
    assert len(kids) == n * (n - 1)
    roles = set(p["roles"])
    for k in kids:
        for a, b in topology_edges(k):
            assert a in roles and b in roles and a != b


def test_edge_search_no_auto_promote_and_cleanup():
    summary = run_edge_search(REPO)
    assert summary["survivors"] == 0
    assert summary["model_calls"] == 0
    assert summary["promotion"] == "none_automatic"
    assert summary["n_candidates"] > 0
    # Worker-normalized held-out beat of PEC is not required to exist on this suite.
    assert "any_beat_pec_held_without_extra_workers" in summary
