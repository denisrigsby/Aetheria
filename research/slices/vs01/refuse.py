"""Deterministic safe_refusal. No models. Default deny production/credentials/network."""
from __future__ import annotations

from typing import Any, Dict

_UNAUTH = ("production plant", "credential", "api key", "password", "private memory", "living jsonl")
_OUTSIDE = ("topology mutation", "cloud", "ollama", "market adapter", "self-modify weights")


def classify_request(goal: str) -> Dict[str, Any]:
    g = (goal or "").strip().lower()
    if not g:
        return {
            "decision": "clarify",
            "reason": "underspecified_empty_goal",
            "alternative": "Provide a bounded fixture edit, e.g. change LABEL from alpha to beta.",
            "unauthorized_work": False,
        }
    if any(x in g for x in _UNAUTH):
        return {
            "decision": "refuse",
            "reason": "unauthorized_private_or_production",
            "alternative": "Use a disposable fixture under research/runs only.",
            "unauthorized_work": True,
        }
    if any(x in g for x in _OUTSIDE):
        return {
            "decision": "refuse",
            "reason": "outside_permitted_task_boundary",
            "alternative": "Stay on local_deterministic_v2 / vertical-slice-01.",
            "unauthorized_work": True,
        }
    if "label" in g and ("alpha" in g or "beta" in g):
        return {
            "decision": "accept",
            "reason": "in_scope_fixture_edit",
            "alternative": None,
            "unauthorized_work": False,
        }
    return {
        "decision": "clarify",
        "reason": "underspecified_or_unknown",
        "alternative": "State file, from-value, and to-value inside the disposable fixture.",
        "unauthorized_work": False,
    }
