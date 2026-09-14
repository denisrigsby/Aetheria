"""Bounded edge-only search. No auto-promotion. model_calls=0. Disposable runs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from research.elastic import ElasticController
from research.evaluate import compare_ecologies, load_profile, load_suite, score_genome
from research.experiment import create_run, record_candidate, utc
from research.topology import genome_fingerprint, neighborhood, topology_edges

PARENTS = ["planner_executor_critic", "planner_executor", "parallel_specialists_synthesizer"]


def _score_row(row: Dict[str, Any]) -> Dict[str, float]:
    ok = float(row["ok"])
    n = float(row["n"] or 1)
    w = float(row.get("mean_workers") or 1)
    held = [r for r in row["results"] if str(r["task"]).startswith("held_out") or r["task"] == "recovery_after_interruption"]
    held_ok = sum(1 for r in held if r.get("ok"))
    return {
        "ok": ok,
        "held_ok": float(held_ok),
        "mean_workers": w,
        "ok_per_worker": round(ok / max(w, 1.0), 4),
        "held_per_worker": round(held_ok / max(w, 1.0), 4),
        "quality_frac": round(ok / n, 4),
    }


def run_edge_search(repo: Path) -> Dict[str, Any]:
    profile = load_profile(repo)
    assert int(profile.get("max_model_calls") or 0) == 0
    suite = load_suite(repo)
    run = create_run(repo, "topo_edges")
    elastic = ElasticController(
        max_active=int(profile.get("max_active_workers") or 8),
        max_depth=int(profile.get("max_task_depth") or 4),
        max_seconds=float(profile.get("max_experiment_lifetime_s") or 120),
        max_model_calls=0,
        start_workers=1,
    )
    baselines = compare_ecologies(repo, PARENTS, include_held_out=True)
    pec = baselines["ecologies"]["planner_executor_critic"]
    pec_s = _score_row(pec)
    candidates: List[Dict[str, Any]] = []
    for pname in PARENTS:
        parent = json.loads((repo / "research" / "ecologies" / f"{pname}.json").read_text(encoding="utf-8"))
        parent["name"] = pname
        for child in neighborhood(parent):
            row = score_genome(repo, child.get("name") or "child", child, include_held_out=True)
            sc = _score_row(row)
            rec = {
                "schema": "aetheria_candidate_v1",
                "candidate_id": f"edge_{genome_fingerprint(child)}",
                "parent_ids": [pname],
                "generation": 1,
                "creation_time": utc(),
                "genome": {k: child[k] for k in child if k != "role_prompts"},
                "task_set": list(suite.get("visible_tasks") or []) + list(suite.get("held_out_tasks") or []),
                "resource_limits": {"max_model_calls": 0, "max_active_workers": child["resource_budget"]["max_active_workers"]},
                "results": {"ok": row["ok"], "n": row["n"], "held_ok": sc["held_ok"]},
                "scores": sc,
                "failures": [r["task"] for r in row["results"] if not r.get("ok")],
                "regressions": [],
                "artifacts": [],
                "promotion_status": "research",
            }
            # never auto-promote
            beats_pec_held = sc["held_ok"] > pec_s["held_ok"] and sc["mean_workers"] <= pec_s["mean_workers"]
            rec["beats_pec_held_without_extra_workers"] = beats_pec_held
            if beats_pec_held:
                rec["promotion_status"] = "hold"
            record_candidate(run, rec)
            candidates.append(rec)
            elastic.step(sc["quality_frac"])
            if elastic.pop.active_count() > int(profile.get("max_active_workers") or 8):
                raise RuntimeError("worker_ceiling_exceeded")
    elastic.cancel_overdue()
    any_beat = any(c.get("beats_pec_held_without_extra_workers") for c in candidates)
    summary = {
        "schema": "aetheria_topology_edge_search_v1",
        "created_at": utc(),
        "parent_baselines": {k: _score_row(baselines["ecologies"][k]) for k in PARENTS},
        "n_candidates": len(candidates),
        "any_beat_pec_held_without_extra_workers": any_beat,
        "promotion": "none_automatic",
        "survivors": elastic.pop.active_count(),
        "model_calls": 0,
        "best_ok": max(c["results"]["ok"] for c in candidates) if candidates else 0,
        "pec_ok": pec_s["ok"],
    }
    (run / "topology_search.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
