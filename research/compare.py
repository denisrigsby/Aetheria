"""Fixed-baseline comparison with lineage. Resource policy is an input, not an afterthought."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .evaluate import compare_ecologies
from .experiment import create_run, record_candidate, utc


ECOLOGIES = [
    "single_generalist",
    "planner_executor",
    "planner_executor_critic",
    "planner_executor_critic_feedback",
    "parallel_specialists_synthesizer",
    "hierarchical_coordinator",
]


def run_comparison(repo: Path, profile: Dict[str, Any]) -> Path:
    run = create_run(repo, "baseline_compare")
    suite = json.loads((repo / "research" / "benchmarks" / "suite.json").read_text(encoding="utf-8"))
    t0 = time.time()
    table = compare_ecologies(repo, ECOLOGIES, include_held_out=True)
    elapsed = round(time.time() - t0, 4)
    artifacts = []
    for name in ECOLOGIES:
        genome = json.loads((repo / "research" / "ecologies" / f"{name}.json").read_text(encoding="utf-8"))
        eco = table["ecologies"][name]
        cand = {
            "schema": "aetheria_candidate_v1",
            "candidate_id": f"fixed_{name}",
            "parent_ids": [],
            "generation": 0,
            "creation_time": utc(),
            "genome": genome,
            "task_set": suite["visible_tasks"] + suite["held_out_tasks"],
            "resource_limits": {
                "max_active_workers": genome["resource_budget"]["max_active_workers"],
                "profile_ceiling": profile.get("max_active_workers"),
                "max_model_calls": profile.get("max_model_calls", 0),
                "wall_s": elapsed,
            },
            "results": {"per_task": eco["results"], "ok": eco["ok"], "n": eco["n"]},
            "scores": {
                "quality_ok": eco["ok"],
                "n_tasks": eco["n"],
                "roles": len(genome.get("roles") or []),
                "max_active": eco["max_active"],
                "mean_workers": eco.get("mean_workers"),
                "duplication": eco.get("duplication"),
                "composite": eco.get("composite"),
                "shared_wall_s": elapsed,
            },
            "failures": [r["task"] for r in eco["results"] if not r.get("ok")],
            "regressions": [],
            "artifacts": [],
            "promotion_status": "research",
        }
        path = record_candidate(run, cand)
        artifacts.append(str(path.name))
    summary = {
        "schema": "aetheria_baseline_compare_v1",
        "created_at": utc(),
        "elapsed_s": elapsed,
        "profile": profile,
        "ecologies": {
            k: {
                "ok": v["ok"],
                "n": v["n"],
                "max_active": v["max_active"],
                "roles": v["roles"],
                "mean_workers": v.get("mean_workers"),
                "composite": v.get("composite"),
            }
            for k, v in table["ecologies"].items()
        },
        "note": "Quality ok is correctness, not extra compute. composite penalizes duplication and mean workers. Same task set for all genomes.",
        "candidates": artifacts,
    }
    (run / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return run
