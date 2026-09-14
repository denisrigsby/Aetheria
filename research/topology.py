"""Communication-edge-only mutation. Does not change roles, prompts, or budgets."""
from __future__ import annotations

import copy
import hashlib
from typing import Any, Dict, List, Tuple

from research.evaluate import topology_edges


def _legal_edges(roles: List[str]) -> List[Tuple[str, str]]:
    out = []
    for a in roles:
        for b in roles:
            if a != b:
                out.append((a, b))
    return out


def genome_fingerprint(genome: Dict[str, Any]) -> str:
    edges = sorted(topology_edges(genome))
    blob = repr(edges).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:12]


def mutate_edges(parent: Dict[str, Any], op: str, edge: Tuple[str, str]) -> Dict[str, Any]:
    """op: add|remove. Roles, prompts, and resource_budget are copied unchanged."""
    child = copy.deepcopy(parent)
    roles = list(child.get("roles") or [])
    legal = set(_legal_edges(roles))
    a, b = edge
    if (a, b) not in legal:
        raise ValueError("edge_not_among_roles")
    cur = topology_edges(child)
    if op == "add":
        cur.add((a, b))
    elif op == "remove":
        cur.discard((a, b))
    else:
        raise ValueError("op_must_be_add_or_remove")
    child["communication_topology"] = [[x, y] for x, y in sorted(cur)]
    child["name"] = f"{parent.get('name')}_e_{op}_{a}_{b}"
    child["promotion"] = "research"
    child["network_access"] = False
    rb = dict(child.get("resource_budget") or {})
    rb["max_model_calls"] = 0
    child["resource_budget"] = rb
    return child


def neighborhood(parent: Dict[str, Any]) -> List[Dict[str, Any]]:
    """All single-edge add/remove children. Bounded by role count."""
    roles = list(parent.get("roles") or [])
    cur = topology_edges(parent)
    kids = []
    for e in _legal_edges(roles):
        if e in cur:
            kids.append(mutate_edges(parent, "remove", e))
        else:
            kids.append(mutate_edges(parent, "add", e))
    return kids
