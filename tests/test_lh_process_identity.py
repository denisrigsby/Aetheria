"""Portable tests for scripts/lh_process_identity.py (no live plant, no CIM)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lh_process_identity as ident  # noqa: E402


def test_roles_supervisor_watchdog_probes_other():
    assert ident.role_from_cmdline("python -u long_horizon_supervisor.py --cycles 2") == ident.ROLE_SUPERVISOR
    assert ident.role_from_cmdline("python -u lh_watchdog.py --interval-sec 60") == ident.ROLE_WATCHDOG
    assert ident.role_from_cmdline("python -u grok_supervised_12_probe.py") == ident.ROLE_PROBE
    assert ident.role_from_cmdline("python -u scripts/_lh_probe_3_1.py") == ident.ROLE_PROBE
    assert ident.role_from_cmdline(r"python -u scripts\_lh_probe_3_1.py") == ident.ROLE_PROBE
    assert ident.role_from_cmdline("python -c sleep") == ident.ROLE_OTHER
    assert ident.role_from_cmdline("launch_lh_watchdog.ps1") == ident.ROLE_OTHER


def test_supervisor_wins_over_probe_token_in_same_line():
    # Observer-style command listing all tokens is supervisor if that script is named.
    cmd = "python long_horizon_supervisor.py"
    assert ident.is_supervisor(cmd)
    assert not ident.is_probe(cmd)


def test_unified_probe_includes_both_families():
    assert ident.is_probe("python grok_supervised_12_probe.py --cycles 2")
    assert ident.is_probe("python grok_supervised_12_probe")  # status-report family
    assert ident.is_probe("python scripts/_lh_probe_9.py")
    assert not ident.is_probe("python long_horizon_supervisor.py")
    assert not ident.is_probe("python lh_watchdog.py")


def test_identity_matches_rejects_wrong_role():
    other = "python -c import time; time.sleep(1)"
    assert not ident.identity_matches(other, ident.ROLE_SUPERVISOR)
    assert ident.identity_matches("python lh_watchdog.py", ident.ROLE_WATCHDOG)


def test_pid_exists_rejects_junk():
    assert ident.pid_exists(None) is False
    assert ident.pid_exists("nope") is False
    assert ident.pid_exists(0) is False
    assert ident.pid_exists(-1) is False
    assert ident.pid_exists(42424242) is False
