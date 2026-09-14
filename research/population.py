"""Bounded population controller. Logical workers, not unbounded OS processes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Worker:
    worker_id: str
    role: str
    parent_id: Optional[str]
    depth: int
    cancelled: bool = False


@dataclass
class PopulationController:
    max_active: int
    max_depth: int
    paused: bool = False
    workers: List[Worker] = field(default_factory=list)
    spawn_log: List[str] = field(default_factory=list)

    def spawn(self, role: str, parent_id: Optional[str] = None) -> Optional[Worker]:
        if self.paused:
            self.spawn_log.append("rejected:paused")
            return None
        active = [w for w in self.workers if not w.cancelled]
        if len(active) >= self.max_active:
            self.spawn_log.append("rejected:max_active")
            return None
        depth = 1
        if parent_id:
            parent = next((w for w in self.workers if w.worker_id == parent_id), None)
            depth = (parent.depth + 1) if parent else 1
        if depth > self.max_depth:
            self.spawn_log.append("rejected:max_depth")
            return None
        w = Worker(worker_id=f"w{len(self.workers)+1}", role=role, parent_id=parent_id, depth=depth)
        self.workers.append(w)
        self.spawn_log.append(f"ok:{w.worker_id}")
        return w

    def pause(self) -> None:
        self.paused = True

    def retire(self, worker_id: str) -> None:
        for w in self.workers:
            if w.worker_id == worker_id:
                w.cancelled = True

    def cancel_all(self) -> None:
        for w in self.workers:
            w.cancelled = True

    def active_count(self) -> int:
        return sum(1 for w in self.workers if not w.cancelled)
