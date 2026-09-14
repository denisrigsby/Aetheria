"""Real revision loop: recompute after critique. Independent check. Hold genome."""
from __future__ import annotations

from pathlib import Path

import pytest

from research.evaluate import topology_edges
from research.slices.pipeline import TamperRejected
from research.slices.vs04.revision import HELD_EDGES, independent_verify, run_revision
from research.topology import mutate_edges
import json

REPO = Path(__file__).resolve().parents[1]


def _pec_forward():
    g = json.loads((REPO / "research" / "ecologies" / "planner_executor_critic.json").read_text(encoding="utf-8"))
    return g


def test_feedback_genome_revises_and_independent_check():
    ev = run_revision(REPO)
    assert ev["ok"] is True
    assert ev["model_calls"] == 0
    assert ev["survivors"] == 0
    assert ev["promotion_status"] == "hold"
    assert ev["independent_verify"]["ok"] is True
    assert ev["independent_verify"]["got"] == 4
    assert ev["independent_verify"]["claimed"] == 5
    assert ev["critique"]["error"] is True
    fx = REPO / "research" / "runs" / ev["run_id"] / "fixture"
    final = json.loads((fx / "final_answer.json").read_text(encoding="utf-8"))
    assert final["source"] == "revised" and final["value"] == 4
    # independent recompute matches files
    assert independent_verify(fx)["ok"] is True


def test_forward_only_cannot_revise():
    ev = run_revision(REPO, genome=_pec_forward())
    assert ev["ok"] is False
    fx = REPO / "research" / "runs" / ev["run_id"] / "fixture"
    final = json.loads((fx / "final_answer.json").read_text(encoding="utf-8"))
    assert final["source"] == "unrevised" and final["value"] == 5
    assert independent_verify(fx)["ok"] is False


def test_forged_final_rejected():
    ev = run_revision(REPO, forge_final=6)
    assert ev["ok"] is False
    assert ev["independent_verify"]["got"] == 6
    assert ev["independent_verify"]["expected"] == 4


def test_interrupts_keep_partial_no_false_success():
    a = run_revision(REPO, interrupt="after_inspect")
    assert a["status"] == "incomplete" and a.get("ok") is not True
    b = run_revision(REPO, interrupt="after_first_pass")
    assert (REPO / "research" / "runs" / b["run_id"] / "fixture" / "first_answer.json").is_file()
    assert b["status"] == "incomplete"
    c = run_revision(REPO, interrupt="after_critique")
    assert (REPO / "research" / "runs" / c["run_id"] / "fixture" / "critique.json").is_file()
    assert not (REPO / "research" / "runs" / c["run_id"] / "fixture" / "final_answer.json").is_file()
    d = run_revision(REPO, interrupt="during_revision")
    assert d["incomplete_at"] == "during_revision"
    assert d["survivors"] == 0


def test_path_and_tamper():
    ev = run_revision(REPO, escape_path="../secret.json")
    assert ev["status"] == "rejected"
    with pytest.raises(TamperRejected):
        run_revision(REPO, tamper_genome={"roles": ["critic"], "tasks": {}, "network_access": True})


def test_repeatable_and_template_unchanged():
    a = run_revision(REPO)
    b = run_revision(REPO)
    fa = (REPO / "research" / "runs" / a["run_id"] / "fixture" / "final_answer.json").read_text(encoding="utf-8")
    fb = (REPO / "research" / "runs" / b["run_id"] / "fixture" / "final_answer.json").read_text(encoding="utf-8")
    assert json.loads(fa)["value"] == json.loads(fb)["value"] == 4
    claim = (REPO / "research" / "slices" / "vs04" / "fixture" / "claim.json").read_text(encoding="utf-8")
    assert '"claimed": 5' in claim


def test_hold_packet_not_production():
    hold = json.loads((REPO / "research" / "holds" / "feedback-edge-genome.json").read_text(encoding="utf-8"))
    assert hold["promotion_status"] == "hold"
    assert hold["auto_promote"] is False
    assert hold["max_model_calls"] == 0
    g = _pec_forward()
    held = mutate_edges(g, "add", ("critic", "planner"))
    assert ("critic", "planner") in topology_edges(held)
    assert held["roles"] == g["roles"]
