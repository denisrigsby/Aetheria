#!/usr/bin/env python3
"""Operator recovery acknowledgement for a dirty plant.

The ack binds the raw bytes of measurements/campaign_snapshot_v1.json.
Hashing a re-serialized document is not that binding. A clean plant
(snapshot campaign.last_ok is True, state last_ok is True, and the
supervisor is not inside a tick) needs no ack. write_ack refuses to
create one.

This module does not spawn the supervisor and does not resume.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

from atomic_state import atomic_write_json
from campaign_snapshot import SCHEMA as SNAPSHOT_SCHEMA

ACK_SCHEMA = "aetheria_recovery_ack_v1"
ACK_NAME = "recovery_ack_v1.json"
CONSUMED_NAME = "recovery_ack_v1.consumed.json"
ACK_KEYS = frozenset({"schema", "snapshot_sha256"})


class AckRefused(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def root() -> Path:
    return Path(os.environ.get("AETHERIA_ROOT") or Path(__file__).resolve().parents[1])


def snapshot_file(r: Path | None = None) -> Path:
    return (r or root()) / "measurements" / "campaign_snapshot_v1.json"


def state_file(r: Path | None = None) -> Path:
    return (r or root()) / "measurements" / "long_horizon_state.json"


def ack_file(r: Path | None = None) -> Path:
    return (r or root()) / "measurements" / ACK_NAME


def consumed_file(r: Path | None = None) -> Path:
    return (r or root()) / "measurements" / CONSUMED_NAME


def snapshot_hash(raw: bytes) -> str:
    """sha256 of the snapshot file's raw bytes. Never re-serialize first."""
    if isinstance(raw, str) or not isinstance(raw, (bytes, bytearray)):
        raise TypeError("snapshot_hash requires the raw snapshot bytes")
    return hashlib.sha256(raw).hexdigest()


def is_dirty(snapshot: dict, state: dict) -> bool:
    """True when the campaign or the segment is not a finished successful tick.

    ``running_tick`` is the mid-tick marker. ``last_ok`` is not cleared at
    tick start, so a crash during a tick can still show last_ok True.
    """
    camp = snapshot.get("campaign") if isinstance(snapshot, dict) else None
    camp_ok = camp.get("last_ok") if isinstance(camp, dict) else None
    if isinstance(state, dict):
        state_ok = state.get("last_ok")
        running = state.get("running_tick") is True
    else:
        state_ok = None
        running = False
    return camp_ok is not True or state_ok is not True or running


def _read_json_object(path: Path) -> tuple[dict | None, str]:
    if not path.is_file():
        return None, "missing"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, "unreadable"
    if not isinstance(doc, dict):
        return None, "not_object"
    return doc, "ok"


def _read_snapshot(r: Path) -> tuple[bytes | None, dict | None, str]:
    path = snapshot_file(r)
    if not path.is_file():
        return None, None, "snapshot_missing"
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None, "snapshot_unreadable"
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return raw, None, "snapshot_unreadable"
    if not isinstance(doc, dict):
        return raw, None, "snapshot_not_object"
    if doc.get("schema") != SNAPSHOT_SCHEMA:
        return raw, doc, "snapshot_schema"
    return raw, doc, "ok"


def _read_state(r: Path) -> dict:
    doc, why = _read_json_object(state_file(r))
    if why != "ok" or doc is None:
        return {}
    return doc


def _hex_eq(left: Any, right: str) -> bool:
    if not isinstance(left, str) or len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def verify_ack(r: Path | None = None) -> tuple[bool, bool, str]:
    """Return (ok, dirty, reason).

    A clean plant is ok with no ack file. A dirty plant is ok only when
    measurements/recovery_ack_v1.json names the sha256 of the snapshot's
    raw bytes. The consumed file is not an ack.
    """
    base = r or root()
    raw, snap, why = _read_snapshot(base)
    if why != "ok" or raw is None or snap is None:
        return False, True, why
    state = _read_state(base)
    dirty = is_dirty(snap, state)
    if not dirty:
        return True, False, "clean"
    ack, ack_why = _read_json_object(ack_file(base))
    if ack_why == "missing" or ack is None:
        return False, True, "ack_required"
    if ack_why != "ok":
        return False, True, "ack_unreadable"
    if set(ack) != ACK_KEYS or ack.get("schema") != ACK_SCHEMA:
        return False, True, "ack_schema"
    if not _hex_eq(ack.get("snapshot_sha256"), snapshot_hash(raw)):
        return False, True, "snapshot_hash_mismatch"
    return True, True, "acked"


def write_ack(r: Path | None = None) -> dict:
    """Atomically write the ack. Refuses when the plant is clean."""
    base = r or root()
    raw, snap, why = _read_snapshot(base)
    if why != "ok" or raw is None or snap is None:
        raise AckRefused(why)
    if not is_dirty(snap, _read_state(base)):
        raise AckRefused("clean")
    doc = {
        "schema": ACK_SCHEMA,
        "snapshot_sha256": snapshot_hash(raw),
    }
    atomic_write_json(ack_file(base), doc)
    return doc


def consume_ack(r: Path | None = None) -> Path:
    """Rename the live ack to recovery_ack_v1.consumed.json.

    Call only after a successful resume of a dirty plant. A second consume
    fails because the live file is gone.
    """
    base = r or root()
    src = ack_file(base)
    dest = consumed_file(base)
    if not src.is_file():
        raise AckRefused("ack_missing")
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dest)
    return dest
