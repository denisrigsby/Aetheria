"""Atomic measurements write helper tests."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys_path_scripts = ROOT / "scripts"
import sys

sys.path.insert(0, str(sys_path_scripts))

from atomic_state import atomic_write_json, read_json_strict  # noqa: E402


def test_atomic_write_leaves_valid_json(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, {"schema": "t_v1", "n": 1, "seq": 1})
    doc = json.loads(target.read_text(encoding="utf-8"))
    assert doc["n"] == 1
    assert not list(tmp_path.glob("*.tmp"))


def test_atomic_replace_overwrites_cleanly(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, {"schema": "t_v1", "n": 1, "seq": 1})
    atomic_write_json(target, {"schema": "t_v1", "n": 2, "seq": 2})
    doc = json.loads(target.read_text(encoding="utf-8"))
    assert doc == {"schema": "t_v1", "n": 2, "seq": 2}


def test_read_json_strict_rejects_unknown_schema(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, {"schema": "nope", "n": 1})
    with pytest.raises(ValueError):
        read_json_strict(target, allowed_schemas={"t_v1"})


def test_partial_tmp_is_not_authoritative(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, {"schema": "t_v1", "n": 1, "seq": 1})
    partial = tmp_path / "state.json.tmp"
    partial.write_text("{", encoding="utf-8")
    # Canonical remains valid; tmp ignored by reader
    doc = read_json_strict(target, allowed_schemas={"t_v1"})
    assert doc["n"] == 1
    with pytest.raises(json.JSONDecodeError):
        json.loads(partial.read_text(encoding="utf-8"))
