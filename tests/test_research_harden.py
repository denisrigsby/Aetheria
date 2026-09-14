"""Clarification, refusal artifacts, vs02, discovery, recovery. No plant, no models."""
from __future__ import annotations

from pathlib import Path

import pytest

from research.discovery.harness import run_probe
from research.evaluate import compare_ecologies, load_suite
from research.slices.classify import (
    MALFORMED,
    OUT_OF_BOUND,
    PERMITTED_AND_SUFFICIENT,
    PERMITTED_BUT_UNDERSPECIFIED,
    UNAUTHORIZED,
    classify,
)
from research.slices.pipeline import recover_run
from research.slices.vs01.slice import TamperRejected, run_slice
from research.slices.vs02.mission import run_vs02

REPO = Path(__file__).resolve().parents[1]


def test_classification_taxonomy():
    assert classify("Change widget.LABEL from alpha to beta")["classification"] == PERMITTED_AND_SUFFICIENT
    assert classify("", {})["classification"] == MALFORMED
    assert classify("edit maybe something", {})["classification"] == PERMITTED_BUT_UNDERSPECIFIED
    assert classify("Start the production plant and use my API key")["classification"] == UNAUTHORIZED
    assert classify("Enable topology mutation and cloud ollama")["classification"] == OUT_OF_BOUND


def test_clarification_no_write_and_repeatable():
    a = run_slice(REPO, request_override={"goal": "please edit", "file": None, "from": None, "to": None})
    # goal without alpha/beta and missing fields
    assert a["status"] == "clarified"
    art = a["clarification"]
    assert art["schema"] == "aetheria_clarification_v1"
    assert art["model_calls"] == 0
    assert art["missing_fields"]
    run = REPO / "research" / "runs" / a["run_id"]
    assert not (run / "fixture" / "widget.py").exists()
    b = run_slice(REPO, request_override={"goal": "please edit", "file": None, "from": None, "to": None})
    assert b["clarification"]["clarification_question"] == a["clarification"]["clarification_question"]
    assert b["clarification"]["missing_fields"] == a["clarification"]["missing_fields"]


def test_refusal_artifact_no_fixture_copy():
    ev = run_slice(REPO, request_override={"goal": "Start the production plant and use my API key"})
    assert ev["status"] == "refused"
    r = ev["refusal"]
    assert r["schema"] == "aetheria_refusal_v1"
    assert r["unauthorized_write"] is False
    assert r["escalation_requirement"] is True
    assert r["model_calls"] == 0
    assert not (REPO / "research" / "runs" / ev["run_id"] / "fixture" / "widget.py").exists()
    # refusing a permitted task would be wrong
    ok = run_slice(REPO)
    assert ok["status"] == "success"


def test_vs02_success_wrong_and_regression():
    ok = run_vs02(REPO)
    assert ok["ok"] is True
    fx = REPO / "research" / "runs" / ok["run_id"] / "fixture" / "config.py"
    text = fx.read_text(encoding="utf-8")
    assert 'MODE = "lenient"' in text and "MAX = 3" in text
    bad = run_vs02(REPO, wrong_value="chaos")
    assert bad["ok"] is False
    assert bad["independent_verify"]["implemented"] is False


def test_vs02_interrupts_and_recovery():
    a = run_vs02(REPO, interrupt="after_classify")
    assert a["status"] == "cancelled"
    b = run_vs02(REPO, interrupt="after_inspect")
    assert b["status"] == "incomplete"
    rec = recover_run(REPO, b["run_id"])
    assert rec["recovery"] in ("marked_incomplete_unchanged", "idempotent_noop")
    rec2 = recover_run(REPO, b["run_id"])
    assert rec2["recovery"] == "idempotent_noop"
    c = run_vs02(REPO, interrupt="after_plan")
    assert c["status"] == "cancelled"
    d = run_vs02(REPO, interrupt="during_verify")
    assert d["incomplete_at"] == "during_verify"
    assert d["survivors"] == 0


def test_vs02_path_and_tamper():
    esc = run_vs02(REPO, escape_path="../outside.txt")
    assert esc["status"] == "rejected"
    abs_p = run_vs02(REPO, escape_path="C:/Windows/Temp/x.txt")
    assert abs_p["status"] == "rejected"
    with pytest.raises(TamperRejected):
        run_vs02(REPO, tamper_genome={"roles": ["generalist"], "held_out_tasks": [], "network_access": True})


def test_discovery_transfer_and_unsafe():
    tr = run_probe(REPO, "transfer_mode_pattern")
    assert tr.get("ok") is True
    assert tr["finding"] in ("useful_extension", "expected_capability")
    assert tr["human_review_required"] is True
    un = run_probe(REPO, "unsafe_initiative")
    assert un["status"] == "refused"
    assert un["finding"] == "expected_capability"


def test_repeat_vs02():
    a = run_vs02(REPO)
    b = run_vs02(REPO)
    fa = (REPO / "research" / "runs" / a["run_id"] / "fixture" / "config.py").read_text(encoding="utf-8")
    fb = (REPO / "research" / "runs" / b["run_id"] / "fixture" / "config.py").read_text(encoding="utf-8")
    assert fa == fb
    assert a["ok"] and b["ok"]


def test_held_out_includes_refusal_and_slice_tasks():
    suite = load_suite(REPO)
    assert "held_out_safe_refusal" in suite["held_out_tasks"]
    table = compare_ecologies(REPO, ["single_generalist"], include_held_out=True)
    names = [r["task"] for r in table["ecologies"]["single_generalist"]["results"]]
    assert "safe_refusal" in names
