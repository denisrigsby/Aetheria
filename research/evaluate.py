"""Local deterministic evaluation. Ecology-sensitive. No models, no network.

Candidates cannot rewrite suite.json, scoring, held-out lists, promotion, or ceilings.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_CANDIDATE_STRIP = (
    "visible_tasks",
    "held_out_tasks",
    "tasks",
    "scoring",
    "hard_reject",
    "benchmark",
    "suite",
    "evaluator",
    "identity_checks",
    "cancellation",
    "promotion_status",
)


from .population import PopulationController


def load_suite(repo: Path) -> Dict[str, Any]:
    path = repo / "research" / "benchmarks" / "suite.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile(repo: Path) -> Dict[str, Any]:
    path = repo / "research" / "config" / "windows-local.json"
    if not path.is_file():
        return {
            "max_active_workers": 8,
            "max_model_calls": 0,
            "max_task_depth": 4,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize_genome(genome: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Drop candidate-supplied evaluator overrides; clamp to research profile."""
    g = copy.deepcopy(genome or {})
    for k in _CANDIDATE_STRIP:
        g.pop(k, None)
    if g.get("promotion") not in ("research", "hold", "rejected"):
        g["promotion"] = "research"
    g["network_access"] = False
    budget = dict(g.get("resource_budget") or {})
    prof = profile or {}
    cap_w = int(prof.get("max_active_workers") or 8)
    cap_d = int(prof.get("max_task_depth") or 4)
    cap_m = int(prof.get("max_model_calls") or 0)
    budget["max_active_workers"] = min(int(budget.get("max_active_workers") or 1), cap_w)
    budget["max_depth"] = min(int(budget.get("max_depth") or 1), cap_d)
    budget["max_model_calls"] = min(int(budget.get("max_model_calls") or 0), cap_m)
    g["resource_budget"] = budget
    return g


def topology_edges(genome: Dict[str, Any]) -> Set[tuple]:
    raw = genome.get("communication_topology") or []
    out: Set[tuple] = set()
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            a, b = str(item[0]), str(item[1])
            if a and b and a != b:
                out.add((a, b))
    return out


def _indegree(edges: Set[tuple], node: str) -> int:
    return sum(1 for a, b in edges if b == node)


def capabilities(genome: Dict[str, Any]) -> Dict[str, Any]:
    roles: Set[str] = set(genome.get("roles") or [])
    routing = str(genome.get("routing_policy") or "")
    budget = genome.get("resource_budget") or {}
    edges = topology_edges(genome)
    critic_role = "critic" in roles
    if edges:
        critic_live = critic_role and _indegree(edges, "critic") > 0
        planner_exec = ("planner" in roles and "executor" in roles and ("planner", "executor") in edges)
        spec_join = any(b == "synthesizer" and a.startswith("specialist") for a, b in edges)
        hier = ("coordinator" in roles and ("coordinator", "worker") in edges)
        parallel = any(_indegree(edges, n) >= 2 for n in roles)
        feedback = ("critic", "planner") in edges or ("critic", "executor") in edges
    else:
        critic_live = critic_role
        planner_exec = "planner" in roles and "executor" in roles
        spec_join = any(str(r).startswith("specialist") for r in roles) and "synthesizer" in roles
        hier = "coordinator" in roles or routing == "hierarchy"
        parallel = routing in ("fan_in", "parallel_then_merge")
        feedback = False
    return {
        "critic": critic_live,
        "planner": "planner" in roles or "coordinator" in roles,
        "executor": "executor" in roles or "worker" in roles or "generalist" in roles,
        "specialists": any(str(r).startswith("specialist") for r in roles),
        "synthesizer": "synthesizer" in roles,
        "hierarchy": hier,
        "parallel": parallel,
        "planner_exec_edge": planner_exec if edges else planner_exec,
        "spec_join_edge": spec_join,
        "critic_feedback": bool(feedback),
        "roles": roles,
        "n_roles": len(roles),
        "max_active": int(budget.get("max_active_workers") or 1),
        "max_depth": int(budget.get("max_depth") or 1),
        "edges": edges,
    }


def _workers_used(cap: Dict[str, Any]) -> int:
    return min(int(cap["n_roles"]), int(cap["max_active"]))


def _base(name: str, cap: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task": name,
        "ok": False,
        "quality": 0,
        "workers_used": _workers_used(cap),
        "duplication": 0.0,
        "critic_applied": bool(cap["critic"]),
        "coordination": max(0, int(cap["n_roles"]) - 1),
        "model_calls": 0,
    }


def run_task(name: str, spec: Dict[str, Any], genome: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    genome = sanitize_genome(genome, profile)
    cap = capabilities(genome)
    pop = PopulationController(max_active=int(cap["max_active"]), max_depth=int(cap["max_depth"]))
    out = _base(name, cap)

    if name == "resource_budget_compliance":
        for _ in range(int(cap["max_active"]) + 5):
            parent = pop.workers[-1].worker_id if pop.workers else None
            pop.spawn("worker", parent_id=parent)
        out["ok"] = pop.active_count() <= int(cap["max_active"])
        out["quality"] = int(out["ok"])
        out["active"] = pop.active_count()
        return out

    if name == "clean_shutdown":
        pop.spawn("generalist")
        pop.cancel_all()
        out["ok"] = pop.active_count() == 0
        out["quality"] = int(out["ok"])
        out["survivors"] = pop.active_count()
        return out

    if name in ("safe_refusal", "held_out_safe_refusal"):
        from research.slices.vs01.refuse import classify_request

        got = classify_request(str(spec.get("input") or ""))
        expect_d = spec.get("expect_decision")
        expect_u = spec.get("expect_unauthorized_work")
        out["ok"] = got.get("decision") == expect_d and got.get("unauthorized_work") == expect_u
        out["quality"] = int(out["ok"])
        out["decision"] = got.get("decision")
        out["reason"] = got.get("reason")
        return out

    if name == "recovery_after_interruption":
        pop.spawn("generalist")
        pop.cancel_all()
        out["ok"] = pop.active_count() == 0
        out["quality"] = int(out["ok"])
        out["recovered"] = True
        return out

    if name in ("multi_doc_synthesis", "held_out_multi_doc"):
        expect = spec.get("expect") or {}
        if cap.get("edges"):
            can_join = bool(cap.get("spec_join_edge") or cap.get("planner_exec_edge") or cap["hierarchy"])
        else:
            can_join = cap["specialists"] and cap["synthesizer"]
            can_join = can_join or (cap["planner"] and cap["executor"])
            can_join = can_join or cap["hierarchy"]
        out["ok"] = bool(can_join) and bool(expect)
        out["quality"] = int(out["ok"])
        out["joined"] = bool(can_join)
        return out

    if name == "cross_doc_contradiction":
        # Single pass over concatenated text misses split-doc contradiction.
        found = cap["critic"] or cap["synthesizer"] or cap["planner"] or cap["hierarchy"]
        out["ok"] = bool(found) == bool(spec.get("expect_contradiction", True))
        out["quality"] = int(out["ok"])
        out["found"] = bool(found)
        return out

    if name == "specialist_units":
        # Only numeric specialist or executor converts grams→kg.
        can = cap["specialists"] or ("executor" in cap["roles"])
        out["ok"] = bool(can)
        out["quality"] = int(out["ok"])
        out["kg"] = float(spec.get("expect_kg") or 0) if can else 1000.0
        return out

    if name == "dependent_planning":
        ordered = cap["planner"] or cap["hierarchy"]
        # Unordered fan-in is the wrong organization for a chain.
        if cap["parallel"] and not cap["planner"]:
            ordered = False
        out["ok"] = bool(ordered)
        out["quality"] = int(out["ok"])
        out["order"] = list(spec.get("steps") or []) if ordered else []
        return out

    if name == "code_fixture_edit":
        files = dict(spec.get("files") or {})
        pair = spec.get("replace") or ["FOO", "BAR"]
        can = cap["executor"] or cap["synthesizer"]
        if can and files:
            src = next(iter(files.values()))
            out["ok"] = pair[0] in src
            out["edited"] = src.replace(str(pair[0]), str(pair[1]))
        else:
            out["ok"] = False
        out["quality"] = int(out["ok"])
        return out

    if name == "test_then_run":
        # Need someone who executes checks, not only drafts them.
        can = cap["critic"] or cap["executor"] or cap["synthesizer"] or cap["hierarchy"]
        cases = spec.get("cases") or []
        ran = bool(can) and bool(cases)
        out["ok"] = ran
        out["quality"] = int(out["ok"])
        out["ran"] = ran
        return out

    if name in ("revision_after_critique", "held_out_revision"):
        # First pass can detect an error; revision requires a feedback edge
        # critic → planner or critic → executor. Forward-only pipelines cannot revise.
        revised = bool(cap["critic"] and cap.get("critic_feedback"))
        out["ok"] = revised
        out["quality"] = int(out["ok"])
        out["revised"] = revised
        return out

    if name in ("deliberate_error", "held_out_deliberate_error"):
        out["ok"] = bool(cap["critic"])
        out["quality"] = int(out["ok"])
        out["detected"] = bool(cap["critic"])
        return out

    if name == "ambiguity_uncertainty":
        # Only critic or coordinator escalates uncertainty instead of guessing.
        out["ok"] = bool(cap["critic"] or cap["hierarchy"])
        out["quality"] = int(out["ok"])
        out["uncertain"] = bool(out["ok"])
        return out

    if name == "duplication_trap":
        docs = spec.get("docs") or []
        if cap["parallel"] and not cap["synthesizer"]:
            uniq = len(docs)
        elif cap["synthesizer"] or cap["n_roles"] == 1 or cap["planner"]:
            uniq = 1
        else:
            uniq = 1
        expect = int(spec.get("expect_unique") or 1)
        out["ok"] = uniq == expect
        out["quality"] = int(out["ok"])
        out["duplication"] = float(max(0, uniq - 1))
        return out

    if name in ("early_stop_value", "held_out_early_stop"):
        useful = int(spec.get("max_useful_workers") or 2)
        used = _workers_used(cap)
        quality = True  # all organizations can emit the constant answer
        out["ok"] = quality and used <= useful
        out["quality"] = int(quality)
        out["workers_used"] = used
        out["early_stop"] = used <= useful
        return out

    out["error"] = "unknown_task"
    return out


def score_genome(repo: Path, name: str, genome: Dict[str, Any], include_held_out: bool) -> Dict[str, Any]:
    suite = load_suite(repo)
    profile = load_profile(repo)
    genome = sanitize_genome(genome, profile)
    tasks = list(suite["visible_tasks"])
    held = list(suite.get("held_out_tasks") or [])
    if include_held_out:
        tasks.extend(held)
    results = []
    for t in tasks:
        spec = (suite.get("tasks") or {}).get(t) or {}
        results.append(run_task(t, spec, genome, profile))
    n_ok = sum(1 for r in results if r.get("ok"))
    dup = sum(float(r.get("duplication") or 0) for r in results)
    workers = sum(int(r.get("workers_used") or 0) for r in results)
    n = max(1, len(results))
    composite = n_ok - 0.15 * dup - 0.02 * (workers / n)
    return {
        "ok": n_ok,
        "n": len(results),
        "results": results,
        "roles": genome.get("roles"),
        "max_active": (genome.get("resource_budget") or {}).get("max_active_workers"),
        "duplication": dup,
        "mean_workers": round(workers / n, 3),
        "composite": round(composite, 4),
        "name": name,
    }


def compare_ecologies(repo: Path, ecology_names: List[str], include_held_out: bool) -> Dict[str, Any]:
    suite = load_suite(repo)
    profile = load_profile(repo)
    tasks = list(suite["visible_tasks"])
    held = list(suite.get("held_out_tasks") or [])
    if include_held_out:
        tasks.extend(held)
    table: Dict[str, Any] = {
        "schema": "aetheria_comparison_v2",
        "benchmark": suite.get("name"),
        "visible_tasks": list(suite["visible_tasks"]),
        "held_out_tasks": held,
        "profile_ceilings": {
            "max_active_workers": profile.get("max_active_workers"),
            "max_model_calls": profile.get("max_model_calls"),
        },
        "ecologies": {},
    }
    for name in ecology_names:
        gpath = repo / "research" / "ecologies" / f"{name}.json"
        genome = json.loads(gpath.read_text(encoding="utf-8"))
        table["ecologies"][name] = score_genome(repo, name, genome, include_held_out)
    table["explanation"] = explain_comparison(table)
    return table


def explain_comparison(table: Dict[str, Any]) -> Dict[str, Any]:
    """Per-task winners and a short why — not a single score."""
    ecos = list(table.get("ecologies") or {})
    if not ecos:
        return {}
    tasks = [r["task"] for r in table["ecologies"][ecos[0]]["results"]]
    per_task = {}
    for task in tasks:
        rows = {}
        for eco in ecos:
            rec = next(r for r in table["ecologies"][eco]["results"] if r["task"] == task)
            rows[eco] = {"ok": rec.get("ok"), "workers": rec.get("workers_used"), "duplication": rec.get("duplication")}
        winners = [e for e, v in rows.items() if v["ok"]]
        per_task[task] = {"winners": winners, "by_ecology": rows}
    oks = {e: table["ecologies"][e]["ok"] for e in ecos}
    best = max(oks, key=lambda k: (oks[k], -table["ecologies"][k]["mean_workers"]))
    why = (
        f"{best} has the most task ok ({oks[best]}/{table['ecologies'][best]['n']}). "
        "Critic genomes uniquely pass deliberate_error; "
        "fan-in fails dependent_planning; "
        "single_generalist fails multi-doc join; "
        "extra roles fail early_stop_value. "
        "composite is secondary and penalizes workers/duplication."
    )
    return {"best_ok": best, "ok_counts": oks, "per_task": per_task, "why": why}
