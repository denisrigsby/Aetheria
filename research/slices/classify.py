"""Request classification. Deterministic. No models."""
from __future__ import annotations

from typing import Any, Dict, Optional

PERMITTED_AND_SUFFICIENT = "permitted_and_sufficient"
PERMITTED_BUT_UNDERSPECIFIED = "permitted_but_underspecified"
UNAUTHORIZED = "unauthorized"
OUT_OF_BOUND = "out_of_bound"
MALFORMED = "malformed"
CAPABILITY_PROBE = "capability_probe"

_UNAUTH = (
    "production plant",
    "credential",
    "api key",
    "password",
    "private memory",
    "living jsonl",
)
_OUTSIDE = (
    "topology mutation",
    "cloud",
    "ollama",
    "market adapter",
    "self-modify weights",
    "network access",
)


def classify(goal: Optional[str], request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    req = dict(request or {})
    g = (goal if goal is not None else req.get("goal") or "").strip()
    gl = g.lower()
    if req.get("probe") or gl.startswith("capability probe:"):
        return {
            "classification": CAPABILITY_PROBE,
            "decision": "probe",
            "reason": "declared_capability_probe",
            "missing_fields": [],
            "unauthorized_work": False,
            "escalation": False,
            "question": None,
            "alternative": None,
        }
    if not g and not req.get("file"):
        return {
            "classification": MALFORMED,
            "decision": "clarify",
            "reason": "malformed_empty",
            "missing_fields": ["goal"],
            "unauthorized_work": False,
            "escalation": False,
            "question": "Provide a bounded fixture edit with file, from, and to.",
            "alternative": None,
        }
    if any(x in gl for x in _UNAUTH):
        return {
            "classification": UNAUTHORIZED,
            "decision": "refuse",
            "reason": "unauthorized_private_or_production",
            "missing_fields": [],
            "unauthorized_work": True,
            "escalation": True,
            "question": None,
            "alternative": "Use a disposable fixture under research/runs only.",
        }
    if any(x in gl for x in _OUTSIDE):
        return {
            "classification": OUT_OF_BOUND,
            "decision": "refuse",
            "reason": "outside_permitted_task_boundary",
            "missing_fields": [],
            "unauthorized_work": True,
            "escalation": True,
            "question": None,
            "alternative": "Stay on local_deterministic_v2 / vertical-slice missions.",
        }
    if ("label" in gl and "alpha" in gl and "beta" in gl) or (
        "mode" in gl and "strict" in gl and "lenient" in gl
    ):
        if "ambiguous" not in gl and "maybe" not in gl:
            return {
                "classification": PERMITTED_AND_SUFFICIENT,
                "decision": "accept",
                "reason": "in_scope_fixture_edit",
                "missing_fields": [],
                "unauthorized_work": False,
                "escalation": False,
                "question": None,
                "alternative": None,
            }
    missing = []
    if not req.get("file"):
        missing.append("file")
    if not req.get("from"):
        missing.append("from")
    if not req.get("to"):
        missing.append("to")
    if "ambiguous" in gl or "maybe" in gl:
        missing.append("scope")
    if missing:
        q = {
            "file": "Which fixture file may be edited?",
            "from": "What is the current value?",
            "to": "What is the desired value?",
            "scope": "Which single field is in scope?",
        }
        return {
            "classification": PERMITTED_BUT_UNDERSPECIFIED,
            "decision": "clarify",
            "reason": "missing_" + "+".join(missing),
            "missing_fields": missing,
            "unauthorized_work": False,
            "escalation": False,
            "question": q.get(missing[0], "Supply the missing fields."),
            "alternative": None,
        }
    return {
        "classification": PERMITTED_AND_SUFFICIENT,
        "decision": "accept",
        "reason": "in_scope_fixture_edit",
        "missing_fields": [],
        "unauthorized_work": False,
        "escalation": False,
        "question": None,
        "alternative": None,
    }
