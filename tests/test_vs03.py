"""VS03 defect repair + regression test from failing assertion."""
from __future__ import annotations

from pathlib import Path

import pytest

from research.slices.pipeline import TamperRejected, recover_run
from research.slices.vs03.mission import run_vs03

REPO = Path(__file__).resolve().parents[1]


def test_repair_success_and_unrelated_mul():
    ev = run_vs03(REPO)
    assert ev["ok"] is True
    assert ev["model_calls"] == 0
    assert ev["survivors"] == 0
    src = (REPO / "research" / "runs" / ev["run_id"] / "fixture" / "mathy.py").read_text(encoding="utf-8")
    assert "return a + b" in src
    assert "def mul" in src
    assert "return a - b" not in src
    gen = (REPO / "research" / "runs" / ev["run_id"] / "fixture" / "test_add_regression.py").read_text(encoding="utf-8")
    assert "mathy.add(2, 3)" in gen and "5" in gen
    template = (REPO / "research" / "slices" / "vs03" / "fixture" / "mathy.py").read_text(encoding="utf-8")
    assert "return a - b" in template


def test_wrong_repair_rejected():
    ev = run_vs03(REPO, wrong_value="return a * b")
    assert ev["ok"] is False
    assert ev["independent_verify"]["implemented"] is False


def test_omit_regression_test_fails():
    ev = run_vs03(REPO, omit_test=True)
    assert ev["ok"] is False


def test_interrupts_path_tamper_repeat():
    a = run_vs03(REPO, interrupt="after_inspect")
    assert a["status"] == "incomplete" and a["survivors"] == 0
    recover_run(REPO, a["run_id"])
    b = run_vs03(REPO, interrupt="after_modify")
    assert b.get("modified") is True
    c = run_vs03(REPO, interrupt="during_test")
    assert c["test_report"]["interrupted"] is True
    esc = run_vs03(REPO, escape_path="../hack.py")
    assert esc["status"] == "rejected"
    with pytest.raises(TamperRejected):
        run_vs03(REPO, tamper_genome={"roles": ["generalist"], "scoring": {}, "network_access": True})
    x = run_vs03(REPO)
    y = run_vs03(REPO)
    fx = lambda rid: (REPO / "research" / "runs" / rid / "fixture" / "mathy.py").read_text(encoding="utf-8")
    assert x["ok"] and y["ok"] and fx(x["run_id"]) == fx(y["run_id"])
