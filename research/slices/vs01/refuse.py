"""Backward-compatible refusal helper."""
from __future__ import annotations

from typing import Any, Dict, Optional

from research.slices.classify import classify


def classify_request(goal: str, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = classify(goal, request)
    return {
        "decision": "accept" if c["decision"] in ("accept", "probe") else c["decision"],
        "reason": c["reason"],
        "alternative": c.get("alternative"),
        "unauthorized_work": c["unauthorized_work"],
        "classification": c["classification"],
        "question": c.get("question"),
        "escalation": c.get("escalation"),
        "missing_fields": c.get("missing_fields") or [],
    }
