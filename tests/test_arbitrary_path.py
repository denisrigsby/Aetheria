"""Control plane must run from an arbitrary directory copy."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_aetheria_help_from_copied_tree(tmp_path: Path):
    dest = tmp_path / "install"
    (dest / "scripts").mkdir(parents=True)
    (dest / "measurements").mkdir()
    for name in ("aetheria.py", "plant_control.py", "lh_process_identity.py"):
        shutil.copy(REPO / "scripts" / name, dest / "scripts" / name)
    r = subprocess.run(
        [sys.executable, "-u", str(dest / "scripts" / "aetheria.py"), "help"],
        cwd=str(tmp_path),  # not the install root and not the developer tree
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0
    assert str(dest) in r.stdout
    assert "backend:    none" in r.stdout
    assert r.stdout.count(str(REPO)) == 0 or str(dest) in r.stdout.split("root:")[1][:400]


def test_init_creates_dirs(tmp_path: Path):
    dest = tmp_path / "install"
    (dest / "scripts").mkdir(parents=True)
    for name in ("aetheria.py", "plant_control.py", "lh_process_identity.py"):
        shutil.copy(REPO / "scripts" / name, dest / "scripts" / name)
    r = subprocess.run(
        [sys.executable, "-u", str(dest / "scripts" / "aetheria.py"), "init"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0
    assert (dest / "measurements").is_dir()
    assert (dest / "research" / "runs").is_dir()
