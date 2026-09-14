"""Machine measurement: logical jobs vs optional OS worker processes. No plant, no network."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .evaluate import compare_ecologies
from .elastic import ElasticController

MARKER = "AETHERIA_RESEARCH_MEASURE"
CREATE_NO_WINDOW = 0x08000000
ECOLOGIES = [
    "single_generalist",
    "planner_executor",
    "planner_executor_critic",
    "parallel_specialists_synthesizer",
    "hierarchical_coordinator",
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sample_pids(pids: List[int]) -> Dict[str, Any]:
    if not pids or sys.platform != "win32":
        return {"ws_mb": None, "cpu_s": None}
    ids = ",".join(str(p) for p in pids)
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$p=@(Get-Process -Id {ids} -EA SilentlyContinue); "
            "if(-not $p){'NONE'} else { '{0}|{1}' -f "
            "[math]::Round((($p|Measure-Object WorkingSet64 -Sum).Sum/1MB),2), "
            "[math]::Round((($p|Measure-Object CPU -Sum).Sum),2) }",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    line = (r.stdout or "").strip()
    if not line or line == "NONE" or "|" not in line:
        return {"ws_mb": None, "cpu_s": None}
    a, b = line.split("|", 1)
    try:
        return {"ws_mb": float(a), "cpu_s": float(b)}
    except Exception:
        return {"ws_mb": None, "cpu_s": None}


def _spawn_os_workers(n: int, seconds: float) -> List[subprocess.Popen]:
    procs = []
    code = f"import time,sys; sys.stderr.write('{MARKER}'); time.sleep({float(seconds)})"
    for i in range(n):
        p = subprocess.Popen(
            [sys.executable, "-c", code, MARKER, str(i)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        procs.append(p)
    return procs


def _kill_os(procs: List[subprocess.Popen]) -> float:
    t0 = time.time()
    for p in procs:
        try:
            p.kill()
        except Exception:
            pass
    for p in procs:
        try:
            p.wait(timeout=5)
        except Exception:
            pass
    return round(time.time() - t0, 4)


def measure_worker_count(repo: Path, n: int, repeats: int = 2) -> Dict[str, Any]:
    runs = []
    for r in range(repeats):
        t0 = time.time()
        procs = _spawn_os_workers(n, seconds=3.0)
        time.sleep(0.4)
        sample_mid = _sample_pids([p.pid for p in procs])
        # logical benchmark at this worker ceiling
        t1 = time.time()
        table = compare_ecologies(repo, ECOLOGIES, include_held_out=True)
        bench_s = round(time.time() - t1, 4)
        elastic = ElasticController(max_active=n, max_depth=3, max_seconds=5, max_model_calls=0, start_workers=1)
        prog = 0.0
        while True:
            prog = min(1.0, prog + 0.2)
            st = elastic.step(prog)
            if st != "continue":
                break
        fin = elastic.finish()
        elastic.cancel_overdue()
        cleanup_s = _kill_os(procs)
        sample_after = _sample_pids([p.pid for p in procs if p.poll() is None])
        survivors = sum(1 for p in procs if p.poll() is None)
        n_ok = sum(table["ecologies"][k]["ok"] for k in ECOLOGIES)
        runs.append(
            {
                "repeat": r,
                "os_workers": n,
                "logical_tasks": sum(table["ecologies"][k]["n"] for k in ECOLOGIES),
                "model_calls": fin["model_calls"],
                "cpu_s": sample_mid.get("cpu_s"),
                "peak_ws_mb": sample_mid.get("ws_mb"),
                "residual_ws_mb": sample_after.get("ws_mb"),
                "bench_s": bench_s,
                "elastic_s": round(time.time() - t0, 4),
                "cleanup_s": cleanup_s,
                "timeouts": 0,
                "failed_tasks": sum(table["ecologies"][k]["n"] - table["ecologies"][k]["ok"] for k in ECOLOGIES),
                "quality_ok": n_ok,
                "survivors": survivors,
                "elastic_stopped": fin["stopped"],
                "elastic_spawned": fin["spawned"],
            }
        )
    return {"n": n, "runs": runs}


def recommend_profile(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Conservative ceilings from measured rows (each row is a worker-count block)."""
    ok_ns = []
    peak = 0.0
    for block in rows:
        n = int(block["n"])
        bad = False
        for run in block["runs"]:
            if run.get("survivors"):
                bad = True
            if run.get("peak_ws_mb"):
                peak = max(peak, float(run["peak_ws_mb"]))
            if run.get("cleanup_s", 0) > 5:
                bad = True
        if not bad:
            ok_ns.append(n)
    max_w = max(ok_ns) if ok_ns else 4
    if max_w > 8:
        max_w = 8
    mem = int(max(256, peak * 3 + 128)) if peak else 512
    return {
        "schema": "aetheria_research_profile_v1",
        "platform": "windows-local",
        "created_at": utc(),
        "max_active_workers": max_w,
        "max_logical_tasks": 64,
        "max_model_calls": 0,
        "max_task_depth": 4,
        "max_task_lifetime_s": 30,
        "max_experiment_lifetime_s": 120,
        "max_memory_mb": mem,
        "max_cpu": None,
        "notes": "model-call limit separate from OS worker concurrency; local_deterministic uses 0 model calls",
        "measured_ns": [b["n"] for b in rows],
    }
