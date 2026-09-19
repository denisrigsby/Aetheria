# Standalone product boundary

This repository is **one product**: a local **process control plane** for a long-horizon work loop.

It is not a chat app, not a model host, and not a marketplace.

Aetheria (full install) is a **versioned, auditable process-continuity layer** for long-running local work, with this public control plane and an **optional private agent** (mouth + living + GPU plant) on one PC. The private piece is an extension, not a hole in GitHub. Protocol: [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

## Why public vs private is architectural

| Stays private | Reason |
|---------------|--------|
| Living jsonl, session traces | User-specific memory; merge/concat forbidden |
| Mouth / local models | Operator chair; must not parent the clock |
| Cycle body / probe internals | Security-sensitive runtime + unpublished research |
| Credentials, host paths | Deployment-specific |

Public GitHub stays fully evaluable as infrastructure (start, heartbeat, STOP, recover, mock demo) without those.

## Supported product

| Slot | Choice |
|------|--------|
| Launcher | `python -u scripts/aetheria.py` (wraps `plant_control.py`) |
| Runtime directory | The clone/install root (directory that contains `scripts/` and `measurements/`) |
| Configuration | `measurements/*.json` plus documented `AETHERIA_*` env vars. No cloud keys required. |
| State directory | `measurements/` |
| Memory/state authority | Operational JSON in `measurements/` only (see [STATE_MODEL.md](STATE_MODEL.md)). **Not** living jsonl, sqlite mirrors, or session logs. |
| Supervisor / watchdog | `long_horizon_supervisor.py` + `lh_watchdog.py` |
| Stop / resume / status / recover | `aetheria.py stop\|resume\|status\|recover\|diagnose` |
| Model/backend | **None.** Control plane runs without a model. Cycle probe bodies are supplied by a full install; this repo ships the supervisor contract and a bounded probe runner, not a chatbot. |

## Explicitly out of scope (deferred)

- Companion chat, STL, workbench, tray
- Private living jsonl / overlay / `living_mirror.db`
- Market / TEE / “routed” adapters
- Ollama, G4 adapters, xAI/cloud completions
- `trust_remote_code`, model downloads
- Legacy launchers: `aetheria.bat`, `aetheria_flawless.bat`, `Launch-Aetheria*.bat`, Typer `htmc.cli` — **not** the standalone front door

## Commands

```text
python -u scripts/aetheria.py status
python -u scripts/aetheria.py stop --reason "…"
python -u scripts/aetheria.py start
python -u scripts/aetheria.py resume
python -u scripts/aetheria.py recover
python -u scripts/aetheria.py diagnose
```

Each command prints the root, Python interpreter, state directory, and backend (`none`).

## Stop contract (Windows)

The supervisor honors `long_horizon_STOP` and may exit before force-kill. Tree-kill (`taskkill /PID /F /T` on Windows) runs only if a **verified live** supervisor still exists after the wait. Dead parent `/T` is not success. Remaining allowlisted supervisor/watchdog/probe identities are then killed by role. Probe kill requires probe identity. Watchdog STOP is always written. Exit 1 if allowlisted processes remain. Stale PID files are removed after verified reconciliation (see STATE_MODEL).
