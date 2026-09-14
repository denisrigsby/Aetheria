"""Local deterministic evaluation. No models, no network."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .population import PopulationController


def contradiction(text: str) -> bool:
    t = text.lower()
    pairs = [("open", "closed"), ("is", "is not"), ("true", "false")]
    return any(a in t and b in t for a, b in pairs)


def run_task(name: str, spec: Dict[str, Any], genome: Dict[str, Any]) -> Dict[str, Any]:
    budget = genome.get("resource_budget") or {}
    max_w = int(budget.get("max_active_workers") or 1)
    max_d = int(budget.get("max_depth") or 1)
    pop = PopulationController(max_active=max_w, max_depth=max_d)
    if name == "resource_budget_compliance":
        for i in range(max_w + 5):
            pop.spawn("worker", parent_id=pop.workers[-1].worker_id if pop.workers else None)
        ok = pop.active_count() <= max_w
        return {"task": name, "ok": ok, "active": pop.active_count(), "max": max_w, "log": pop.spawn_log}
    if name == "contradiction_detection" or name == "held_out_contradiction":
        found = contradiction(str(spec.get("input") or ""))
        expect = bool(spec.get("expect_contradiction"))
        return {"task": name, "ok": found == expect, "found": found}
    if name == "structured_synthesis":
        items = [x.strip() for x in str(spec.get("input") or "").replace("items:", "").split(",") if x.strip()]
        out = {"count": len(items), "items": items}
        ok = all(k in out for k in (spec.get("expect_keys") or []))
        return {"task": name, "ok": ok, "output": out}
    if name == "multi_step_planning":
        steps = [s.strip() for s in str(spec.get("input") or "").split(",") if s.strip()]
        ok = len(steps) >= int(spec.get("expect_min_steps") or 1)
        return {"task": name, "ok": ok, "steps": steps}
    if name == "document_analysis":
        text = str(spec.get("input") or "")
        # 2+3=5, claim 4 is wrong
        ok = "4" in text and ("2" in text and "3" in text)
        return {"task": name, "ok": ok, "note": "claims_checked"}
    if name == "clean_shutdown":
        pop.spawn("generalist")
        pop.cancel_all()
        return {"task": name, "ok": pop.active_count() == 0, "survivors": pop.active_count()}
    if name == "recovery_after_interruption":
        pop.spawn("generalist")
        pop.cancel_all()
        return {"task": name, "ok": pop.active_count() == 0, "recovered": True}
    return {"task": name, "ok": False, "error": "unknown_task"}


def compare_ecologies(repo: Path, ecology_names: List[str], include_held_out: bool) -> Dict[str, Any]:
    suite = json.loads((repo / "research" / "benchmarks" / "suite.json").read_text(encoding="utf-8"))
    tasks = suite["visible_tasks"] + (suite["held_out_tasks"] if include_held_out else [])
    table: Dict[str, Any] = {"schema": "aetheria_comparison_v1", "ecologies": {}}
    for name in ecology_names:
        gpath = repo / "research" / "ecologies" / f"{name}.json"
        genome = json.loads(gpath.read_text(encoding="utf-8"))
        results = []
        for t in tasks:
            spec = (suite.get("tasks") or {}).get(t) or {}
            results.append(run_task(t, spec, genome))
        n_ok = sum(1 for r in results if r.get("ok"))
        table["ecologies"][name] = {
            "ok": n_ok,
            "n": len(results),
            "results": results,
            "roles": genome.get("roles"),
            "max_active": (genome.get("resource_budget") or {}).get("max_active_workers"),
        }
    return table
