"""python -m aetheria → scripts/aetheria.py"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
cli = ROOT / "scripts" / "aetheria.py"
spec = importlib.util.spec_from_file_location("aetheria_cli", cli)
if spec is None or spec.loader is None:
    raise SystemExit("aetheria CLI missing")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
raise SystemExit(mod.main())
