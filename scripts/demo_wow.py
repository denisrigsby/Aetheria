#!/usr/bin/env python3
"""Deprecated entrypoint. Use scripts/demo_continuity.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

print(
    "note: demo_wow.py renamed to demo_continuity.py (honest continuity proof)",
    file=sys.stderr,
)
raise SystemExit(
    runpy.run_path(str(Path(__file__).with_name("demo_continuity.py")), run_name="__main__")
)
