from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from process_identity_bind import (  # noqa: E402
    ProcessBinding,
    bindings_match,
    normalize_cmdline,
    refuse_action_on_mismatch,
)


def test_normalize_cmdline_stable():
    assert normalize_cmdline(r"Python  -u  long_horizon_supervisor.py") == normalize_cmdline(
        "python -u long_horizon_supervisor.py"
    )


def test_creation_time_mismatch_refuses():
    a = ProcessBinding(pid=1, role="supervisor", creation_time="t1", cmdline="python long_horizon_supervisor.py")
    b = ProcessBinding(pid=1, role="supervisor", creation_time="t2", cmdline="python long_horizon_supervisor.py")
    assert bindings_match(a, b) is False
    d = refuse_action_on_mismatch(a.to_dict(), b.to_dict())
    assert d["may_kill"] is False and d["action"] == "refuse"


def test_match_allows_when_bound_fields_equal():
    a = ProcessBinding(
        pid=7,
        role="supervisor",
        creation_time="t1",
        exe_path=r"C:\Python\python.exe",
        cmdline="python -u long_horizon_supervisor.py",
        parent_pid=1,
    )
    b = ProcessBinding(
        pid=7,
        role="supervisor",
        creation_time="t1",
        exe_path=r"C:\Python\python.exe",
        cmdline="python -u long_horizon_supervisor.py",
        parent_pid=1,
    )
    assert bindings_match(a, b) is True
    d = refuse_action_on_mismatch(a.to_dict(), b.to_dict())
    assert d["may_kill"] is True


def test_missing_binding_refuses():
    d = refuse_action_on_mismatch(None, {"pid": 1, "role": "x"})
    assert d["may_adopt"] is False
