"""Windows-only process tests. Harmless sleep fixtures. Never touches measurements/ or the plant."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

if sys.platform != "win32":
    pytest.skip("Windows taskkill/tasklist tests", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lh_process_identity as ident  # noqa: E402

CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
MARKER = "AETHERIA_TEST_LH_IDENT"


def _spawn(seconds: float, tail: str, *, new_group: bool = False) -> subprocess.Popen:
    code = f"import time,sys; sys.stderr.write('{MARKER}\\n'); time.sleep({float(seconds)})"
    flags = CREATE_NO_WINDOW
    if new_group:
        flags |= CREATE_NEW_PROCESS_GROUP
    p = subprocess.Popen(
        [sys.executable, "-c", code, MARKER, tail],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=flags,
    )
    time.sleep(0.3)
    return p


def _reap_marker() -> None:
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -like '*AETHERIA_TEST_LH_IDENT*' } | "
            "ForEach-Object { $_.ProcessId }",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    for tok in (r.stdout or "").split():
        if tok.isdigit():
            ident.taskkill(int(tok), tree=True)


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    _reap_marker()


def test_verified_role_supervisor_vs_other():
    sup = _spawn(25, "long_horizon_supervisor.py")
    oth = _spawn(25, "unrelated_sleep.py")
    try:
        assert ident.verified_role(sup.pid, ident.ROLE_SUPERVISOR)
        assert not ident.verified_role(oth.pid, ident.ROLE_SUPERVISOR)
        assert ident.pid_exists(oth.pid)
    finally:
        ident.taskkill(sup.pid, tree=False)
        ident.taskkill(oth.pid, tree=False)


def test_kill_f_leaves_child_t_kills_tree():
    parent_code = (
        "import subprocess,sys,time\n"
        f"flags={CREATE_NO_WINDOW}|{CREATE_NEW_PROCESS_GROUP}\n"
        "c=subprocess.Popen([sys.executable,'-c','import time; time.sleep(40)',"
        f"'{MARKER}','child'], creationflags=flags,"
        "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        "print(c.pid, flush=True)\n"
        "time.sleep(35)\n"
    )
    p = subprocess.Popen(
        [sys.executable, "-c", parent_code, MARKER, "parent"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )
    raw = (p.stdout.readline() if p.stdout else "") or ""
    child = int(raw.strip()) if raw.strip().isdigit() else 0
    time.sleep(0.4)
    assert ident.pid_exists(p.pid) and ident.pid_exists(child)
    ident.taskkill(p.pid, tree=False)
    time.sleep(0.5)
    assert not ident.pid_exists(p.pid)
    assert ident.pid_exists(child), " /F without /T should leave descendant"
    # dead parent /T does not kill child
    kr = ident.taskkill(p.pid, tree=True)
    time.sleep(0.3)
    assert kr["returncode"] != 0
    assert ident.pid_exists(child)
    ident.taskkill(child, tree=True)

    p2 = subprocess.Popen(
        [sys.executable, "-c", parent_code, MARKER, "parent2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )
    raw2 = (p2.stdout.readline() if p2.stdout else "") or ""
    child2 = int(raw2.strip()) if raw2.strip().isdigit() else 0
    time.sleep(0.4)
    ident.taskkill(p2.pid, tree=True)
    time.sleep(0.5)
    assert not ident.pid_exists(p2.pid)
    assert not ident.pid_exists(child2)


def test_kill_if_verified_rejects_wrong_identity():
    oth = _spawn(20, "unrelated_sleep.py")
    try:
        r = ident.kill_if_verified(oth.pid, ident.ROLE_SUPERVISOR, tree=True)
        assert r["reason"] == "identity_mismatch"
        assert ident.pid_exists(oth.pid)
    finally:
        ident.taskkill(oth.pid, tree=False)


def test_kill_if_verified_already_dead():
    p = _spawn(15, "long_horizon_supervisor.py")
    ident.taskkill(p.pid, tree=False)
    time.sleep(0.3)
    r = ident.kill_if_verified(p.pid, ident.ROLE_SUPERVISOR, tree=True)
    assert r["reason"] == "already_dead"
