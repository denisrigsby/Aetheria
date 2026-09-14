"""Consistency of capability contract metadata. No plant, no network."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARCH = REPO / "research" / "architecture"
STAGES = {
    "specified",
    "local_deterministic_prototype",
    "sandboxed_operational",
    "controlled_external_use",
    "production_candidate",
    "production_approved",
}
ELIG = {
    "research-only",
    "sandbox-eligible",
    "controlled-use-eligible",
    "production-eligible",
}


def _matrix():
    return json.loads((ARCH / "capability-matrix.json").read_text(encoding="utf-8"))


def _portfolio():
    return json.loads((ARCH / "reference-task-portfolio.json").read_text(encoding="utf-8"))


def _suite():
    return json.loads((REPO / "research" / "benchmarks" / "suite.json").read_text(encoding="utf-8"))


def _profile():
    return json.loads((REPO / "research" / "config" / "windows-local.json").read_text(encoding="utf-8"))


def test_required_architecture_files_exist():
    for name in (
        "README.md",
        "aetheria-capability-contract.md",
        "capability-matrix.json",
        "capability-matrix.md",
        "reference-task-portfolio.json",
        "reference-task-portfolio.md",
        "research-production-boundary.md",
        "promotion-gates.md",
        "vertical-slice-01.md",
        "RESEARCH_INTAKE.md",
    ):
        assert (ARCH / name).is_file(), name


def test_capabilities_have_maturity_and_promotion_metadata():
    m = _matrix()
    assert m["default_model_calls"] == 0
    assert m["default_network"] is False
    ids = []
    for c in m["capabilities"]:
        ids.append(c["id"])
        assert c["maturity"] in STAGES
        assert c["next_maturity"] in STAGES
        assert c["eligibility"] in ELIG
        assert c["maturity"] not in ("production_candidate", "production_approved")
        assert c["evaluator"]
        assert c["safety_controls"]
        assert c["acceptance_criteria"]
        assert c["blocking_risks"]
        assert c["owner"] in ("research", "control_plane")
        assert c["resource_limits"].get("max_model_calls", 0) == 0
    assert len(ids) == len(set(ids))
    assert len(ids) >= 15


def test_no_document_claims_production_readiness():
    for p in ARCH.glob("*.md"):
        text = p.read_text(encoding="utf-8").lower()
        assert "production approved" not in text or "not" in text
        assert "production-ready" not in text
        assert "production ready" not in text


def test_portfolio_maps_to_capabilities_and_suite():
    caps = {c["id"] for c in _matrix()["capabilities"]}
    suite = _suite()
    vis = set(suite["visible_tasks"])
    held = set(suite["held_out_tasks"])
    assert vis.isdisjoint(held)
    port = _portfolio()
    assert port["model_calls"] == 0
    assert port["network_access"] is False
    for t in port["tasks"]:
        assert t["capability_ids"]
        assert set(t["capability_ids"]) <= caps
        bt = t.get("benchmark_task")
        if bt:
            assert bt in vis or bt in held
            if t["visibility"] == "visible":
                assert bt in vis
                assert bt not in held
            if t["visibility"] == "held-out":
                assert bt in held
                assert bt not in vis
        else:
            assert t["id"] == "safe_refusal"


def test_held_out_not_in_visible_manifest():
    suite = _suite()
    for name in suite["held_out_tasks"]:
        assert name not in suite["visible_tasks"]
        assert name.startswith("held_out") or name == "recovery_after_interruption"


def test_forbidden_boundaries_listed():
    m = _matrix()
    assert "production_modification_by_research" in m["forbidden_automatic"]
    bound = (ARCH / "research-production-boundary.md").read_text(encoding="utf-8")
    assert "exactly one" in bound.lower()
    assert "Production plant" in bound


def test_every_production_facing_claim_has_a_gate():
    gates = (ARCH / "promotion-gates.md").read_text(encoding="utf-8")
    for stage in ("production_candidate", "production_approved"):
        assert stage in gates
    assert "never automatic" in gates.lower() or "never automatic into production" in gates.lower()


def test_vertical_slice_has_no_cloud_or_production_dependency():
    vs = (ARCH / "vertical-slice-01.md").read_text(encoding="utf-8").lower()
    assert "not implemented" in vs or "research/slices/vs01" in vs
    assert "credential" in vs
    for needle in ("api key", "openai", "anthropic", "ollama serve"):
        assert needle not in vs
    assert "production plant" in vs or "production files" in vs
    assert "max_model_calls = 0" in vs or "max_model_calls = 0" in vs.replace(" ", "")


def test_research_default_model_call_budget_zero():
    assert _profile()["max_model_calls"] == 0
    assert _matrix()["default_model_calls"] == 0


def test_intake_template_has_required_questions():
    text = (ARCH / "RESEARCH_INTAKE.md").read_text(encoding="utf-8").lower()
    for q in ("capability", "smallest local experiment", "rollback", "boundary", "model calls"):
        assert q in text
