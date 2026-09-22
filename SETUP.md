# Setup

## Requirements

| Item | Notes |
|------|--------|
| OS | Windows is the reference platform. Tree-kill, Job Object stop, and relaunch are not claimed off Windows |
| Python | 3.10+ |
| PowerShell | 5.1+; PowerShell 7+ recommended |
| Full install | Orchestrator, registry, and cycle probe modules (not in this repo) |

## Full install vs this repository

This repository publishes the **control plane**:

- Supervisor, watchdog, measured entry path  
- Continuity audit and change-control gate evaluator  
- Path helpers and a disposable sandbox edit target  
- Documentation and example status shapes  

Scripts import runtime modules that belong to a **complete local Aetheria tree**. Overlay this tree onto that root, or copy `scripts/` and `living/` into an existing root.

Without those modules, some imports fail **by design**. The control plane remains useful as documentation and partial reuse of supervision patterns.

## Environment

```powershell
$env:AETHERIA_LIGHT_MANAGE = "1"
$env:AETHERIA_SKIP_FINAL_RECON = "1"
$env:AETHERIA_HEAVY_HEALTH_CYCLES = "6,12"
$env:AETHERIA_META_RECON = "0"
```

Optional: `AETHERIA_BIN_ROOT`, `AETHERIA_LIVING_PATH`.

Full install steps: [docs/INSTALL.md](docs/INSTALL.md). Support/rollback: [docs/SUPPORT.md](docs/SUPPORT.md). Research: [docs/FRONTIER_EVOLUTION_WORKING_INSTRUCTIONS.md](docs/FRONTIER_EVOLUTION_WORKING_INSTRUCTIONS.md).

## Smoke tests

```powershell
cd <AETHERIA_ROOT>

# Structure / syntax (works on this repository alone)
python -m compileall -q scripts living tests
python -m pytest tests/test_lh_process_identity.py -q

# Windows (reference platform): also
# python -m pytest tests/test_lh_process_windows.py -q

# Runtime health (needs full install)
python -u scripts/aetheria_hope_path.py --health-only
python -u scripts/aetheria_hope_path.py --cycles 2

# Continuity audit when a plant is present
python -u scripts/verify_continuity_readonly.py
```

## Next steps

- [docs/OPERATIONS.md](docs/OPERATIONS.md) — detached schedule and recovery  
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — process model  
- [CHANGELOG.md](CHANGELOG.md) — what changed in each release  
