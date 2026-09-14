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


def test_feedback_named_baseline_is_research_not_production():
    g = json.loads((REPO / "research" / "ecologies" / "planner_executor_critic_feedback.json").read_text(encoding="utf-8"))
    pec = _pec()
    assert g["promotion"] == "research"
    assert g["roles"] == pec["roles"]
    assert g["resource_budget"]["max_model_calls"] == 0
    assert ["critic", "planner"] in g["communication_topology"]
    assert ["critic", "planner"] not in pec["communication_topology"]
    hold = json.loads((REPO / "research" / "holds" / "feedback-edge-genome.json").read_text(encoding="utf-8"))
    assert hold["promotion_status"] == "hold"
    assert hold["auto_promote"] is False
    fb = score_genome(REPO, "fb", g, True)
    parent = score_genome(REPO, "pec", pec, True)
    assert fb["ok"] > parent["ok"]
    assert fb["mean_workers"] == parent["mean_workers"]


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


def test_feedback_edge_enables_revision_without_extra_roles():
    p = _pec()
    parent = score_genome(REPO, "pec", p, True)
    child = mutate_edges(p, "add", ("critic", "planner"))
    improved = score_genome(REPO, "feedback", child, True)
    assert child["roles"] == p["roles"]
    def _ok(row, task):
        return next(r for r in row["results"] if r["task"] == task)["ok"]
    assert _ok(parent, "revision_after_critique") is False
    assert _ok(improved, "revision_after_critique") is True
    assert _ok(improved, "held_out_revision") is True
    assert improved["mean_workers"] == parent["mean_workers"]
    assert improved["ok"] > parent["ok"]


def test_edge_search_no_auto_promote_and_cleanup():
    summary = run_edge_search(REPO)
    assert summary["survivors"] == 0
    assert summary["model_calls"] == 0
    assert summary["promotion"] == "none_automatic"
    assert summary["n_candidates"] > 0
    # Adding critic→planner is in the neighborhood and should beat PEC held-out
    # without extra workers (same 3 roles).
    assert summary["any_beat_pec_held_without_extra_workers"] is True
    assert summary["best_ok"] > summary["pec_ok"]
