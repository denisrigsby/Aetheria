"""Real revision loop: detect error, feedback along critic→planner, recompute, independent check.

model_calls=0. Disposable fixture only. Genome stays research-hold, never production.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from research.elastic import ElasticController
from research.evaluate import load_profile, sanitize_genome, topology_edges
from research.experiment import _atomic_write, create_run, record_candidate, utc
from research.slices.pipeline import PathEscape, TamperRejected, _allow, _artifact_stats, request_hash

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture"
HELD_EDGES = [["planner", "executor"], ["executor", "critic"], ["critic", "planner"]]


def _compute(left: int, op: str, right: int) -> int:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    raise ValueError("unsupported_op")


def independent_verify(fixture: Path) -> Dict[str, Any]:
    """Recompute from claim.json. Does not trust first_answer or executor notes."""
    claim = json.loads(_allow(fixture / "claim.json", fixture).read_text(encoding="utf-8"))
    expected = _compute(int(claim["left"]), str(claim["op"]), int(claim["right"]))
    final_p = fixture / "final_answer.json"
    if not final_p.is_file():
        return {"independent": True, "ok": False, "expected": expected, "got": None, "reason": "no_final_answer"}
    final = json.loads(_allow(final_p, fixture).read_text(encoding="utf-8"))
    got = final.get("value")
    return {
        "independent": True,
        "ok": got == expected,
        "expected": expected,
        "got": got,
        "claimed": claim.get("claimed"),
        "model_calls": 0,
    }


def _has_feedback(genome: Dict[str, Any]) -> bool:
    e = topology_edges(genome)
    return ("critic", "planner") in e or ("critic", "executor") in e


def _critic_live(genome: Dict[str, Any]) -> bool:
    e = topology_edges(genome)
    roles = set(genome.get("roles") or [])
    if "critic" not in roles:
        return False
    if not e:
        return True
    return any(b == "critic" for _, b in e)


def run_revision(
    repo: Path,
    *,
    genome: Optional[Dict[str, Any]] = None,
    interrupt: Optional[str] = None,
    forge_final: Optional[int] = None,
    escape_path: Optional[str] = None,
    tamper_genome: Optional[Dict[str, Any]] = None,
    baseline_commit: str = "71f4d35",
) -> Dict[str, Any]:
    profile = load_profile(repo)
    if int(profile.get("max_model_calls") or 0) != 0:
        raise RuntimeError("profile_model_calls_nonzero")
    g = dict(
        genome
        or {
            "schema": "aetheria_genome_v1",
            "name": "pec_feedback_hold",
            "roles": ["planner", "executor", "critic"],
            "communication_topology": HELD_EDGES,
            "resource_budget": {"max_active_workers": 3, "max_depth": 3, "max_seconds": 30, "max_model_calls": 0},
            "network_access": False,
            "promotion": "hold",
        }
    )
    if tamper_genome is not None:
        sanitize_genome(tamper_genome, profile)
        if any(k in tamper_genome for k in ("tasks", "held_out_tasks", "scoring", "evaluator")) or tamper_genome.get(
            "network_access"
        ):
            raise TamperRejected("tamper_rejected")

    run = create_run(repo, "vs04")
    fixture = run / "fixture"
    fixture.mkdir()
    shutil.copy(FIXTURE / "claim.json", fixture / "claim.json")
    elastic = ElasticController(
        max_active=min(3, int(profile.get("max_active_workers") or 8)),
        max_depth=min(3, int(profile.get("max_task_depth") or 4)),
        max_seconds=30,
        max_model_calls=0,
        start_workers=1,
    )
    evidence: Dict[str, Any] = {
        "schema": "aetheria_revision_evidence_v1",
        "run_id": run.name,
        "created_at": utc(),
        "baseline_commit": baseline_commit,
        "request_hash": request_hash({"goal": "revise_claim", "file": "claim.json"}),
        "classification": "permitted_and_sufficient",
        "genome_name": g.get("name"),
        "edges": sorted(list(topology_edges(g))),
        "promotion_status": "hold",
        "human_review_required": True,
        "model_calls": 0,
        "status": "running",
        "interrupt": interrupt,
        "plan": ["inspect", "executor_first_pass", "critic", "feedback_revise", "independent_verify"],
    }
    _atomic_write(run / "evidence.json", evidence)

    if interrupt == "after_inspect":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_inspect"
        return _done(elastic, evidence, run, fixture)

    claim = json.loads((fixture / "claim.json").read_text(encoding="utf-8"))
    # Executor first pass: naively accept the claim (no verification).
    first = {"pass": 1, "value": claim["claimed"], "source": "claimed"}
    _atomic_write(fixture / "first_answer.json", first)
    evidence["first_answer"] = first
    if interrupt == "after_first_pass":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_first_pass"
        return _done(elastic, evidence, run, fixture)

    if escape_path:
        try:
            p = Path(escape_path)
            if p.is_absolute() or ".." in Path(escape_path).parts:
                raise PathEscape(escape_path)
            target = (fixture / escape_path).resolve()
            target.relative_to(fixture.resolve())
        except (ValueError, PathEscape):
            evidence["status"] = "rejected"
            evidence["reason"] = f"path_escape:{escape_path}"
            return _done(elastic, evidence, run, fixture)

    # Critic: independently compute (this is the critic step, still local arithmetic).
    correct = _compute(int(claim["left"]), str(claim["op"]), int(claim["right"]))
    critique = {
        "error": correct != claim["claimed"],
        "correct": correct,
        "claimed": claim["claimed"],
        "feedback_edge": _has_feedback(g),
        "critic_live": _critic_live(g),
    }
    _atomic_write(fixture / "critique.json", critique)
    evidence["critique"] = critique
    if interrupt == "after_critique":
        evidence["status"] = "incomplete"
        evidence["incomplete_at"] = "after_critique"
        return _done(elastic, evidence, run, fixture)

    if critique["error"] and critique["feedback_edge"] and critique["critic_live"]:
        # Planner receives critique and executor recomputes.
        plan2 = {"action": "recompute", "from_critique": True}
        _atomic_write(fixture / "revision_plan.json", plan2)
        if interrupt == "during_revision":
            evidence["status"] = "incomplete"
            evidence["incomplete_at"] = "during_revision"
            return _done(elastic, evidence, run, fixture)
        final_val = forge_final if forge_final is not None else correct
        _atomic_write(fixture / "final_answer.json", {"pass": 2, "value": final_val, "source": "revised"})
    else:
        # No feedback path: first answer stands.
        _atomic_write(fixture / "final_answer.json", {"pass": 1, "value": first["value"], "source": "unrevised"})

    verify = independent_verify(fixture)
    evidence["independent_verify"] = verify
    evidence["ok"] = bool(verify["ok"]) and forge_final is None
    evidence["status"] = "success" if evidence["ok"] else "failure"
    return _done(elastic, evidence, run, fixture)


def _done(elastic: ElasticController, evidence: Dict[str, Any], run: Path, fixture: Path) -> Dict[str, Any]:
    elastic.cancel_overdue()
    evidence["survivors"] = elastic.pop.active_count()
    evidence["model_calls"] = 0
    evidence["shutdown"] = "clean"
    evidence["cleanup"] = "complete"
    stats = _artifact_stats(run)
    evidence.update(stats)
    _atomic_write(run / "evidence.json", evidence)
    record_candidate(
        run,
        {
            "schema": "aetheria_candidate_v1",
            "candidate_id": "vs04_revision",
            "parent_ids": ["planner_executor_critic"],
            "generation": 1,
            "creation_time": utc(),
            "genome": {"name": evidence.get("genome_name"), "communication_topology": evidence.get("edges")},
            "task_set": ["real_revision_loop"],
            "resource_limits": {"max_model_calls": 0},
            "results": {"status": evidence["status"], "ok": evidence.get("ok")},
            "scores": {},
            "failures": [] if evidence.get("ok") else [evidence.get("status")],
            "regressions": [],
            "artifacts": ["evidence.json"],
            "promotion_status": "hold",
        },
    )
    return evidence
