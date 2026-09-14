"""Local deterministic evaluation. Ecology-sensitive. No models, no network."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set


from .population import PopulationController


def capabilities(genome: Dict[str, Any]) -> Dict[str, Any]:
    roles: Set[str] = set(genome.get("roles") or [])
    routing = str(genome.get("routing_policy") or "")
    budget = genome.get("resource_budget") or {}
    return {
        "critic": "critic" in roles,
        "planner": "planner" in roles or "coordinator" in roles,
        "executor": "executor" in roles or "worker" in roles or "generalist" in roles,
        "specialists": any(str(r).startswith("specialist") for r in roles),
        "synthesizer": "synthesizer" in roles,
        "hierarchy": "coordinator" in roles or routing == "hierarchy",
        "parallel": routing in ("fan_in", "parallel_then_merge"),
        "roles": roles,
        "n_roles": len(roles),
        "max_active": int(budget.get("max_active_workers") or 1),
        "max_depth": int(budget.get("max_depth") or 1),
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


def run_task(name: str, spec: Dict[str, Any], genome: Dict[str, Any]) -> Dict[str, Any]:
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

    if name == "recovery_after_interruption":
        pop.spawn("generalist")
        pop.cancel_all()
        out["ok"] = pop.active_count() == 0
        out["quality"] = int(out["ok"])
        out["recovered"] = True
        return out

    if name in ("multi_doc_synthesis", "held_out_multi_doc"):
        expect = spec.get("expect") or {}
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


def compare_ecologies(repo: Path, ecology_names: List[str], include_held_out: bool) -> Dict[str, Any]:
    suite = json.loads((repo / "research" / "benchmarks" / "suite.json").read_text(encoding="utf-8"))
    tasks = list(suite["visible_tasks"])
    if include_held_out:
        tasks.extend(suite["held_out_tasks"])
    table: Dict[str, Any] = {
        "schema": "aetheria_comparison_v2",
        "benchmark": suite.get("name"),
        "ecologies": {},
    }
    for name in ecology_names:
        gpath = repo / "research" / "ecologies" / f"{name}.json"
        genome = json.loads(gpath.read_text(encoding="utf-8"))
        results = []
        for t in tasks:
            spec = (suite.get("tasks") or {}).get(t) or {}
            results.append(run_task(t, spec, genome))
        n_ok = sum(1 for r in results if r.get("ok"))
        dup = sum(float(r.get("duplication") or 0) for r in results)
        workers = sum(int(r.get("workers_used") or 0) for r in results)
        n = max(1, len(results))
        composite = n_ok - 0.15 * dup - 0.02 * (workers / n)
        table["ecologies"][name] = {
            "ok": n_ok,
            "n": len(results),
            "results": results,
            "roles": genome.get("roles"),
            "max_active": (genome.get("resource_budget") or {}).get("max_active_workers"),
            "duplication": dup,
            "mean_workers": round(workers / n, 3),
            "composite": round(composite, 4),
        }
    return table
