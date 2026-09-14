"""Shared disposable edit pipeline for vs01/vs02/discovery. model_calls=0."""
from __future__ import annotations

import hashlib
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
from research.slices.classify import (
    CAPABILITY_PROBE,
    MALFORMED,
    OUT_OF_BOUND,
    PERMITTED_AND_SUFFICIENT,
    PERMITTED_BUT_UNDERSPECIFIED,
    UNAUTHORIZED,
    classify,
)


class PathEscape(Exception):
    pass


class TamperRejected(Exception):
    pass


def request_hash(req: Dict[str, Any]) -> str:
    blob = json.dumps(req, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def plan_hash(plan: List[str]) -> str:
    return hashlib.sha256("\n".join(plan).encode("utf-8")).hexdigest()[:16]


def _allow(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as e:
        raise PathEscape(f"path_escape:{resolved}") from e
    if resolved.is_symlink():
        raise PathEscape(f"symlink_escape:{resolved}")
    return resolved


def _copy_fixture(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for p in src.iterdir():
        if p.name.startswith("__pycache__") or p.suffix == ".pyc":
            continue
        if p.is_file():
            shutil.copy(p, dest / p.name)


def _write(root: Path, rel: str, text: str) -> None:
    if Path(rel).is_absolute() or rel.startswith("/") or (len(rel) > 1 and rel[1] == ":"):
        raise PathEscape(f"absolute_path:{rel}")
    path = _allow(root / rel, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read(root: Path, rel: str) -> str:
    return _allow(root / rel, root).read_text(encoding="utf-8")


def _artifact_stats(run: Path) -> Dict[str, Any]:
    files = []
    total = 0
    for p in run.rglob("*"):
        if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in p.parts:
            files.append(str(p.relative_to(run)).replace("\\", "/"))
            total += p.stat().st_size
    return {"artifact_count": len(files), "artifact_bytes": total, "artifact_paths": sorted(files)}


def _implemented(src: str, request: Dict[str, Any], applied: Optional[str] = None) -> bool:
    want, old = request["to"], request["from"]
    if request.get("kind") == "repair":
        return want in src and old not in src
    key = request.get("assign", "LABEL")
    return f'{key} = "{want}"' in src and f'{key} = "{old}"' not in src


def independent_verify(fixture: Path, request: Dict[str, Any], test_rc: Optional[int]) -> Dict[str, Any]:
    src = _read(fixture, request["file"])
    want = request["to"]
    implemented = _implemented(src, request)
    marker = request.get("unrelated_marker") or "def ping"
    unrelated_ok = marker in src or any(
        marker in p.read_text(encoding="utf-8")
        for p in fixture.glob("*.py")
        if p.name != request.get("generate_test")
    )
    gen = fixture / request["generate_test"]
    needle = str((request.get("failing_assertion") or {}).get("expect", want))
    gen_ok = gen.is_file() and needle in gen.read_text(encoding="utf-8")
    tests_ok = test_rc == 0
    return {
        "independent": True,
        "implemented": implemented,
        "unrelated_ok": unrelated_ok,
        "tests_executed": test_rc is not None,
        "tests_pass": bool(tests_ok),
        "generated_test_present": gen_ok,
        "ok": implemented and unrelated_ok and tests_ok and gen_ok,
        "model_calls": 0,
    }


def _finish(elastic: ElasticController, evidence: Dict[str, Any], run: Path, t0: float) -> Dict[str, Any]:
    elastic.cancel_overdue()
    evidence["survivors"] = elastic.pop.active_count()
    evidence["model_calls"] = 0
    evidence["shutdown"] = "clean"
    evidence["cleanup"] = "complete"
    evidence["latency_s"] = round(time.time() - t0, 4)
    stats = _artifact_stats(run)
    evidence.update(stats)
    _atomic_write(run / "evidence.json", evidence)
    _atomic_write(run / "manifest.json", _manifest(evidence, run))
    return evidence


def _manifest(evidence: Dict[str, Any], run: Path) -> Dict[str, Any]:
    return {
        "schema": "aetheria_run_manifest_v1",
        "run_id": evidence.get("run_id"),
        "baseline_commit": evidence.get("baseline_commit"),
        "fixture_version": evidence.get("fixture_version"),
        "request_hash": evidence.get("request_hash"),
        "request_classification": (evidence.get("classification") or {}).get("classification"),
        "plan_hash": evidence.get("plan_hash"),
        "modified_paths": evidence.get("modified_paths") or [],
        "generated_tests": evidence.get("generated_tests") or [],
        "test_command": evidence.get("test_command"),
        "test_result": evidence.get("test_report"),
        "independent_verification": evidence.get("independent_verify"),
        "evidence_completeness": evidence.get("status"),
        "interruption_point": evidence.get("incomplete_at") or evidence.get("interrupt"),
        "recovery_result": evidence.get("recovery"),
        "worker_count": evidence.get("workers"),
        "logical_task_count": evidence.get("logical_tasks"),
        "duplication_count": evidence.get("duplication", 0),
        "artifact_count": evidence.get("artifact_count"),
        "artifact_byte_size": evidence.get("artifact_bytes"),
        "elapsed_time": evidence.get("latency_s"),
        "model_calls": 0,
        "cleanup_result": evidence.get("cleanup"),
        "survivor_status": evidence.get("survivors"),
        "observed_not_claimed": True,
    }


def recover_run(repo: Path, run_id: str) -> Dict[str, Any]:
    run = repo / "research" / "runs" / run_id
    ev_path = run / "evidence.json"
    if not ev_path.is_file():
        return {"status": "missing", "run_id": run_id}
    evidence = json.loads(ev_path.read_text(encoding="utf-8"))
    if evidence.get("recovery"):
        evidence["recovery"] = "idempotent_noop"
        _atomic_write(ev_path, evidence)
        return evidence
    if evidence.get("status") in ("success", "failure", "refused", "clarified", "rejected"):
        evidence["recovery"] = "idempotent_noop"
        _atomic_write(ev_path, evidence)
        return evidence
    evidence["recovery"] = "marked_incomplete_unchanged"
    evidence["status"] = evidence.get("status") or "incomplete"
    _atomic_write(ev_path, evidence)
    return evidence


def run_mission(
    repo: Path,
    *,
    name: str,
    fixture_src: Path,
    request: Dict[str, Any],
    fixture_version: str,
    interrupt: Optional[str] = None,
    wrong_value: Optional[str] = None,
    wrong_file: Optional[str] = None,
    omit_test: bool = False,
    escape_path: Optional[str] = None,
    tamper_genome: Optional[Dict[str, Any]] = None,
    recover_id: Optional[str] = None,
    baseline_commit: str = "unknown",
) -> Dict[str, Any]:
    t0 = time.time()
    profile = load_profile(repo)
    if int(profile.get("max_model_calls") or 0) != 0:
        raise RuntimeError("profile_model_calls_nonzero")
    if recover_id:
        return recover_run(repo, recover_id)

    run = create_run(repo, name)
    fixture = run / "fixture"
    elastic = ElasticController(
        max_active=min(2, int(profile.get("max_active_workers") or 8)),
        max_depth=min(2, int(profile.get("max_task_depth") or 4)),
        max_seconds=float(profile.get("max_experiment_lifetime_s") or 30),
        max_model_calls=0,
        start_workers=1,
    )
    cls = classify(request.get("goal"), request)
    plan = [
        "classify",
        "inspect",
        "validate_plan",
        "modify",
        "generate_test",
        "run_tests",
        "independent_verify",
        "shutdown",
    ]
    evidence: Dict[str, Any] = {
        "schema": "aetheria_slice_evidence_v2",
        "created_at": utc(),
        "run_id": run.name,
        "baseline_commit": baseline_commit,
        "fixture_version": fixture_version,
        "request": {k: request[k] for k in request if k != "hidden"},
        "request_hash": request_hash(request),
        "classification": cls,
        "plan": plan,
        "plan_hash": plan_hash(plan),
        "status": "running",
        "interrupt": interrupt,
        "model_calls": 0,
        "workers": 1,
        "logical_tasks": 0,
        "modified_paths": [],
        "generated_tests": [],
        "duplication": 0,
    }
    _atomic_write(run / "evidence.json", evidence)

    if tamper_genome is not None:
        sanitize_genome(tamper_genome, profile)
        if any(k in tamper_genome for k in ("tasks", "held_out_tasks", "scoring", "evaluator")) or tamper_genome.get(
            "network_access"
        ):
            evidence["status"] = "rejected"
            evidence["reason"] = "evaluator_tamper_or_network"
            elastic.cancel_overdue()
            _finish(elastic, evidence, run, t0)
            raise TamperRejected("tamper_rejected")

    if interrupt == "after_classify":
        evidence["status"] = "cancelled"
        evidence["incomplete_at"] = "after_classify"
        return _finish(elastic, evidence, run, t0)

    if cls["classification"] in (PERMITTED_BUT_UNDERSPECIFIED, MALFORMED):
        art = {
            "schema": "aetheria_clarification_v1",
            "run_id": run.name,
            "request_hash": evidence["request_hash"],
            "classification": cls["classification"],
            "missing_fields": cls["missing_fields"],
            "clarification_question": cls["question"],
            "permitted_scope": "disposable fixture edit only",
            "forbidden_actions": ["production", "network", "credentials", "topology"],
            "timestamps": {"created_at": evidence["created_at"]},
            "cleanup_status": "complete",
            "model_calls": 0,
        }
        _atomic_write(run / "clarification.json", art)
        evidence["status"] = "clarified"
        evidence["clarification"] = art
        return _finish(elastic, evidence, run, t0)

    if cls["classification"] in (UNAUTHORIZED, OUT_OF_BOUND):
        art = {
            "schema": "aetheria_refusal_v1",
            "run_id": run.name,
            "request_hash": evidence["request_hash"],
            "classification": cls["classification"],
            "refusal_reason": cls["reason"],
            "requested_action": request.get("goal"),
            "prohibited_action": cls["reason"],
            "permitted_alternative": cls.get("alternative"),
            "escalation_requirement": bool(cls.get("escalation")),
            "unauthorized_write": False,
            "artifact_paths": ["refusal.json"],
            "cleanup_result": "complete",
            "model_calls": 0,
        }
        _atomic_write(run / "refusal.json", art)
        evidence["status"] = "refused"
        evidence["refusal"] = art
        return _finish(elastic, evidence, run, t0)

    _copy_fixture(fixture_src, fixture)

    if interrupt == "after_inspect":
        evidence["inspected"] = True
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_inspect"
        return _finish(elastic, evidence, run, t0)

    if interrupt == "after_plan":
        evidence["status"] = "cancelled"
        evidence["incomplete_at"] = "after_plan"
        return _finish(elastic, evidence, run, t0)

    if escape_path:
        try:
            _write(fixture, escape_path, "escaped")
        except PathEscape as e:
            evidence["status"] = "rejected"
            evidence["reason"] = str(e)
            return _finish(elastic, evidence, run, t0)

    target_file = wrong_file or request["file"]
    key = request.get("assign", "LABEL")
    new_val = wrong_value if wrong_value is not None else request["to"]
    src = _read(fixture, target_file)
    if request.get("kind") == "repair":
        new_src = src.replace(request["from"], new_val)
    else:
        new_src = src.replace(f'{key} = "{request["from"]}"', f'{key} = "{new_val}"')
    _write(fixture, target_file, new_src)
    evidence["modified"] = True
    evidence["modified_paths"] = [target_file]
    evidence["applied_value"] = new_val
    if interrupt == "after_modify":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_modify"
        return _finish(elastic, evidence, run, t0)

    if not omit_test:
        tname = request["generate_test"]
        fail = request.get("failing_assertion") or {}
        if fail:
            body = (
                "import unittest\nimport {mod}\n\nclass T(unittest.TestCase):\n"
                "    def test_regression_from_failing_assertion(self):\n"
                "        self.assertEqual({expr}, {expect!r})\n"
            ).format(mod=Path(request["file"]).stem, expr=fail["expr"], expect=fail["expect"])
        else:
            body = (
                "import unittest\nimport {mod}\n\nclass T(unittest.TestCase):\n"
                "    def test_val(self):\n        self.assertEqual({mod}.{key}, {val!r})\n"
            ).format(mod=Path(target_file).stem, key=key, val=new_val)
        _write(fixture, tname, body)
        evidence["generated_tests"] = [tname]
        evidence["test_generated"] = True

    if interrupt == "during_test":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "during_test"
        evidence["test_report"] = {"interrupted": True, "returncode": None}
        return _finish(elastic, evidence, run, t0)

    cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(fixture), "-p", "test_*.py", "-q"]
    evidence["test_command"] = cmd
    proc = subprocess.run(
        cmd,
        cwd=str(fixture),
        capture_output=True,
        text=True,
        timeout=int(profile.get("max_task_lifetime_s") or 30),
    )
    evidence["logical_tasks"] = 2
    evidence["test_report"] = {"returncode": proc.returncode, "stdout": (proc.stdout or "")[-400:], "stderr": (proc.stderr or "")[-400:]}

    if interrupt == "during_verify":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "during_verify"
        return _finish(elastic, evidence, run, t0)

    verify_req = independent_verify(fixture, request, proc.returncode)
    evidence["independent_verify"] = verify_req
    if wrong_value is not None or wrong_file is not None or omit_test:
        evidence["status"] = "failure"
        evidence["ok"] = False
    elif verify_req["ok"]:
        evidence["status"] = "success"
        evidence["ok"] = True
    else:
        evidence["status"] = "failure"
        evidence["ok"] = False
    evidence["workers"] = elastic.pop.active_count()
    record_candidate(
        run,
        {
            "schema": "aetheria_candidate_v1",
            "candidate_id": name,
            "parent_ids": [],
            "generation": 0,
            "creation_time": utc(),
            "genome": {"name": name, "network_access": False},
            "task_set": [name],
            "resource_limits": {"max_model_calls": 0},
            "results": {"status": evidence["status"], "ok": evidence.get("ok")},
            "scores": {},
            "failures": [] if evidence.get("ok") else [evidence["status"]],
            "regressions": [],
            "artifacts": ["evidence.json", "manifest.json"],
            "promotion_status": "research",
        },
    )
    return _finish(elastic, evidence, run, t0)
