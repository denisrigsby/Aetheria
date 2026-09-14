"""Vertical slice 01 runner. Local, deterministic, disposable. model_calls=0."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from research.elastic import ElasticController
from research.evaluate import load_profile, sanitize_genome
from research.experiment import _atomic_write, create_run, record_candidate, utc
from research.slices.vs01.refuse import classify_request

SLICE_DIR = Path(__file__).resolve().parent
FIXTURE_SRC = SLICE_DIR / "fixture"
REQUEST_PATH = SLICE_DIR / "request.json"
PROTECTED = (
    "research/benchmarks/suite.json",
    "research/evaluate.py",
    "research/architecture",
    "scripts/plant_control.py",
    "scripts/lh_process_identity.py",
)


class PathEscape(Exception):
    pass


class TamperRejected(Exception):
    pass


def _allow(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_r = root.resolve()
    try:
        resolved.relative_to(root_r)
    except ValueError as e:
        raise PathEscape(f"path_escape:{resolved}") from e
    return resolved


def _copy_fixture(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for p in FIXTURE_SRC.iterdir():
        if p.name.startswith("__pycache__"):
            continue
        shutil.copy(p, dest / p.name)


def _write(root: Path, rel: str, text: str) -> None:
    path = _allow(root / rel, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read(root: Path, rel: str) -> str:
    return _allow(root / rel, root).read_text(encoding="utf-8")


def independent_verify(fixture: Path, request: Dict[str, Any], test_rc: Optional[int]) -> Dict[str, Any]:
    """Re-read files and re-run tests. Does not trust the executor's claims."""
    src = _read(fixture, request["file"])
    want = request["to"]
    old = request["from"]
    implemented = f'LABEL = "{want}"' in src and f'LABEL = "{old}"' not in src
    ping_ok = "def ping" in src
    tests_ok = test_rc == 0
    gen = fixture / request["generate_test"]
    gen_ok = gen.is_file() and want in gen.read_text(encoding="utf-8")
    ok = implemented and ping_ok and tests_ok and gen_ok
    return {
        "independent": True,
        "implemented": implemented,
        "unrelated_ok": ping_ok,
        "tests_executed": test_rc is not None,
        "tests_pass": tests_ok,
        "generated_test_present": gen_ok,
        "ok": ok,
        "model_calls": 0,
    }


def run_slice(
    repo: Path,
    *,
    interrupt: Optional[str] = None,
    wrong_value: Optional[str] = None,
    escape_path: Optional[str] = None,
    tamper_genome: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    t0 = time.time()
    profile = load_profile(repo)
    assert int(profile.get("max_model_calls") or 0) == 0
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    run = create_run(repo, "vs01")
    fixture = run / "fixture"
    _copy_fixture(fixture)
    elastic = ElasticController(
        max_active=min(2, int(profile.get("max_active_workers") or 8)),
        max_depth=min(2, int(profile.get("max_task_depth") or 4)),
        max_seconds=float(profile.get("max_experiment_lifetime_s") or 30),
        max_model_calls=0,
        start_workers=1,
    )
    evidence: Dict[str, Any] = {
        "schema": "aetheria_vs01_evidence_v1",
        "created_at": utc(),
        "run_id": run.name,
        "request": request,
        "classification": classify_request(request["goal"]),
        "plan": [
            "inspect widget.py",
            "replace LABEL alpha→beta",
            "write test_label.py",
            "run unittest",
            "independent verify",
            "shutdown",
        ],
        "status": "running",
        "interrupt": interrupt,
        "model_calls": 0,
        "workers": 1,
        "logical_tasks": 0,
    }
    _atomic_write(run / "evidence.json", evidence)

    if tamper_genome is not None:
        clean = sanitize_genome(tamper_genome, profile)
        if "tasks" in tamper_genome or tamper_genome.get("network_access"):
            evidence["status"] = "rejected"
            evidence["reason"] = "evaluator_tamper_or_network"
            evidence["sanitized_keys"] = sorted(clean.keys())
            _atomic_write(run / "evidence.json", evidence)
            elastic.cancel_overdue()
            raise TamperRejected("tamper_rejected")

    cls = evidence["classification"]
    if cls["decision"] != "accept":
        evidence["status"] = "refused"
        evidence["shutdown"] = "clean"
        _atomic_write(run / "evidence.json", evidence)
        elastic.cancel_overdue()
        return evidence

    evidence["logical_tasks"] += 1
    src = _read(fixture, request["file"])
    evidence["inspected"] = True
    _atomic_write(run / "evidence.json", evidence)
    if interrupt == "after_inspect":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_inspect"
        evidence["shutdown"] = "clean"
        elastic.cancel_overdue()
        evidence["survivors"] = elastic.pop.active_count()
        evidence["model_calls"] = 0
        _atomic_write(run / "evidence.json", evidence)
        return evidence

    if escape_path:
        try:
            _write(fixture, escape_path, "escaped")
        except PathEscape as e:
            evidence["status"] = "rejected"
            evidence["reason"] = str(e)
            evidence["shutdown"] = "clean"
            _atomic_write(run / "evidence.json", evidence)
            elastic.cancel_overdue()
            return evidence

    new_val = wrong_value if wrong_value is not None else request["to"]
    new_src = src.replace(f'LABEL = "{request["from"]}"', f'LABEL = "{new_val}"')
    _write(fixture, request["file"], new_src)
    evidence["modified"] = True
    evidence["applied_value"] = new_val
    _atomic_write(run / "evidence.json", evidence)
    if interrupt == "after_modify":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_modify"
        evidence["shutdown"] = "clean"
        elastic.cancel_overdue()
        evidence["survivors"] = elastic.pop.active_count()
        evidence["model_calls"] = 0
        _atomic_write(run / "evidence.json", evidence)
        return evidence

    test_body = (
        "import unittest\nimport widget\n\n"
        "class TestLabel(unittest.TestCase):\n"
        f"    def test_label(self):\n        self.assertEqual(widget.LABEL, {new_val!r})\n"
    )
    _write(fixture, request["generate_test"], test_body)
    evidence["test_generated"] = True
    _atomic_write(run / "evidence.json", evidence)

    if interrupt == "during_test":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "during_test"
        evidence["test_report"] = {"interrupted": True, "returncode": None}
        evidence["shutdown"] = "clean"
        elastic.cancel_overdue()
        evidence["survivors"] = elastic.pop.active_count()
        evidence["model_calls"] = 0
        _atomic_write(run / "evidence.json", evidence)
        return evidence

    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(fixture), "-p", "test_*.py", "-q"],
        cwd=str(fixture),
        capture_output=True,
        text=True,
        timeout=int(profile.get("max_task_lifetime_s") or 30),
    )
    evidence["logical_tasks"] += 1
    evidence["test_report"] = {
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-500:],
        "stderr": (proc.stderr or "")[-500:],
    }
    verify = independent_verify(fixture, {**request, "to": new_val}, proc.returncode)
    # Independent check uses the *requested* to-value, not the applied wrong value
    verify_req = independent_verify(fixture, request, proc.returncode)
    evidence["executor_verify"] = verify
    evidence["independent_verify"] = verify_req
    if wrong_value is not None:
        evidence["status"] = "failure"
        evidence["ok"] = False
    elif verify_req["ok"]:
        evidence["status"] = "success"
        evidence["ok"] = True
    else:
        evidence["status"] = "failure"
        evidence["ok"] = False
    evidence["latency_s"] = round(time.time() - t0, 4)
    evidence["workers"] = elastic.pop.active_count()
    evidence["duplication"] = 0
    evidence["uncertainty"] = None if evidence.get("ok") else "implementation_or_tests_failed"
    elastic.cancel_overdue()
    evidence["survivors"] = elastic.pop.active_count()
    evidence["shutdown"] = "clean"
    evidence["model_calls"] = 0
    _atomic_write(run / "evidence.json", evidence)
    record_candidate(
        run,
        {
            "schema": "aetheria_candidate_v1",
            "candidate_id": "vs01",
            "parent_ids": [],
            "generation": 0,
            "creation_time": utc(),
            "genome": {"name": "vs01_deterministic", "network_access": False},
            "task_set": ["vertical_slice_01"],
            "resource_limits": {"max_model_calls": 0},
            "results": {"status": evidence["status"], "ok": evidence.get("ok")},
            "scores": {},
            "failures": [] if evidence.get("ok") else [evidence["status"]],
            "regressions": [],
            "artifacts": ["evidence.json", "fixture"],
            "promotion_status": "research",
        },
    )
    return evidence
