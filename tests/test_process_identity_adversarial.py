"""Adversarial process-identity checks (public control plane)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lh_process_identity as ident  # noqa: E402


def test_unrelated_cmdline_never_matches_supervisor():
    assert not ident.identity_matches("C:\\Windows\\System32\\notepad.exe", ident.ROLE_SUPERVISOR)
    assert not ident.identity_matches("python -c pass", ident.ROLE_SUPERVISOR)


def test_junk_and_dead_pids_never_verify_supervisor():
    assert ident.verified_role(None, ident.ROLE_SUPERVISOR) is False
    assert ident.verified_role(0, ident.ROLE_SUPERVISOR) is False
    assert ident.verified_role(42424242, ident.ROLE_SUPERVISOR) is False


def test_watchdog_not_adoptable_as_supervisor():
    cmd = "python -u lh_watchdog.py --interval-sec 60"
    assert ident.role_from_cmdline(cmd) == ident.ROLE_WATCHDOG
    assert not ident.identity_matches(cmd, ident.ROLE_SUPERVISOR)


def test_probe_not_adoptable_as_supervisor():
    cmd = "python -u scripts/_lh_probe_3_1.py"
    assert ident.is_probe(cmd)
    assert not ident.identity_matches(cmd, ident.ROLE_SUPERVISOR)
