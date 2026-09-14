"""Bounded elastic population: size and lifetime only, not topology."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .population import PopulationController, Worker


@dataclass
class ElasticController:
    max_active: int
    max_depth: int
    max_seconds: float
    max_model_calls: int = 0
    model_calls: int = 0
    start_workers: int = 1
    plateau_needed: int = 2
    pop: PopulationController = field(init=False)
    events: List[Dict[str, Any]] = field(default_factory=list)
    scores: List[float] = field(default_factory=list)
    stopped: Optional[str] = None
    interrupt_after_events: Optional[int] = None
    started_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.pop = PopulationController(max_active=self.max_active, max_depth=self.max_depth)
        self.started_at = time.time()
        self._log("start", {"max_active": self.max_active, "max_model_calls": self.max_model_calls})
        for _ in range(max(1, self.start_workers)):
            self._spawn("generalist")

    def _log(self, kind: str, detail: Dict[str, Any]) -> None:
        self.events.append({"t": round(time.time() - self.started_at, 4), "kind": kind, **detail})

    def _spawn(self, role: str, parent_id: Optional[str] = None) -> Optional[Worker]:
        if self.stopped:
            self._log("spawn_rejected", {"reason": self.stopped, "role": role})
            return None
        w = self.pop.spawn(role, parent_id=parent_id)
        self._log("spawn" if w else "spawn_rejected", {"role": role, "ok": bool(w), "active": self.pop.active_count()})
        return w

    def pause_spawning(self) -> None:
        self.pop.pause()
        self._log("pause", {})

    def retire(self, worker_id: str) -> None:
        self.pop.retire(worker_id)
        self._log("retire", {"worker_id": worker_id, "active": self.pop.active_count()})

    def cancel_overdue(self) -> None:
        self.pop.cancel_all()
        self.stopped = self.stopped or "cancelled"
        self._log("cancel_all", {"active": self.pop.active_count()})

    def record_model_call(self) -> bool:
        if self.model_calls >= self.max_model_calls:
            self._log("model_call_rejected", {"used": self.model_calls, "max": self.max_model_calls})
            return False
        self.model_calls += 1
        self._log("model_call", {"used": self.model_calls})
        return True

    def step(self, progress: float) -> str:
        """progress in [0,1]. Returns continue|stop|interrupted."""
        if self.interrupt_after_events is not None and len(self.events) >= self.interrupt_after_events:
            self.stopped = "interrupted"
            self._log("interrupt", {"events": len(self.events)})
            return "interrupted"
        if time.time() - self.started_at > self.max_seconds:
            self.cancel_overdue()
            self.stopped = "deadline"
            self._log("deadline", {})
            return "stop"
        self.scores.append(progress)
        self._log("progress", {"value": progress, "active": self.pop.active_count()})
        if len(self.scores) >= self.plateau_needed + 1:
            recent = self.scores[-(self.plateau_needed + 1) :]
            if all(abs(recent[i] - recent[i - 1]) < 0.02 for i in range(1, len(recent))):
                self.stopped = "plateau"
                self.pause_spawning()
                self._log("plateau", {"scores": recent})
                return "stop"
        if progress < 0.5 and self.pop.active_count() < self.max_active:
            if not any(w.role == "critic" and not w.cancelled for w in self.pop.workers):
                self._spawn("critic")
                self._log("escalate_critic", {})
        if progress >= 0.5 and self.scores and progress > max(self.scores[:-1] or [0]) + 0.05:
            if self.pop.active_count() < self.max_active:
                self._spawn("generalist")
        return "continue"

    def finish(self) -> Dict[str, Any]:
        if not self.stopped:
            self.stopped = "complete"
        self._log("finish", {"reason": self.stopped, "active": self.pop.active_count(), "model_calls": self.model_calls})
        return {
            "schema": "aetheria_elastic_v1",
            "stopped": self.stopped,
            "active": self.pop.active_count(),
            "spawned": len(self.pop.workers),
            "model_calls": self.model_calls,
            "max_model_calls": self.max_model_calls,
            "max_active": self.max_active,
            "events": self.events,
            "scores": self.scores,
        }
