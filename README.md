# Aetheria

[![CI](https://github.com/denisrigsby/Aetheria-sovereign-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/denisrigsby/Aetheria-sovereign-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/denisrigsby/Aetheria-sovereign-agent)](https://github.com/denisrigsby/Aetheria-sovereign-agent/releases)

**Aetheria is a versioned, auditable process-continuity layer for long-running local workloads**, with a reference (mock) runtime in this repo and an optional private agent on one PC.

This repository is the **control plane**: supervisor, watchdog, STOP, heartbeat, checkpoint, recover. It is not a chat app, not a model host, and not a dump of the private organism.

The private install — **mouth** (local admin / architect) + **plant** (detached ticks) + living memory — is an **extension**, not a missing GitHub file. Chat never parents the clock. Talk is a mirror of the ledger, not a dependency: if the chat window is closed, the worker still ticks. Dirty `last_ok` **HOLDs**. There is **no AUTORUN** after a dirty death.

**Plant clock ≠ chat.**

Protocol: [docs/RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md) · boundary: [docs/STANDALONE_PRODUCT.md](docs/STANDALONE_PRODUCT.md) · state: [docs/STATE_MODEL.md](docs/STATE_MODEL.md) · sitting picture: [docs/SANITIZED_DEMO.md](docs/SANITIZED_DEMO.md)

Launcher: `python -u scripts/aetheria.py status|stop|start|resume|recover|diagnose|demo`

`recover` is not `start`. Recover loads `measurements/campaign_snapshot_v1.json` only when the supervisor is identity-dead. Hash mismatch → no spawn.

> Think **supervisor / pm2 for agent work loops**: hard stop, recovery, structured cycle completion — not a multi-agent framework and not a chat UI.

### The pain this targets

| Common AI complaint | Control plane answer |
|---------------------|----------------------|
| Dies when chat/IDE closes | Detached supervisor + on-disk state |
| Hangs / stuck forever | Timeouts, STOP files, conservation bounds |
| “Is it still working?” | `status_report` + measurements JSON |
| Overnight babysitting | Rolling ticks / segments + watchdog |
| Thrash restart after power flap | HOLD after dirty `last_ok`; resume when stable |
| Chat is the whole runtime | **Plant clock ≠ chat** — chat never owns the schedule |
| Crash vs green stop | Dirty `last_ok=false` HOLDs; green interruptions may guardian-start |

### Job #1 — local campaign runner

| Step | What you prove |
|------|----------------|
| 1 | `python -u scripts/demo_local_smoke.py` — control plane layout + compile (no private sauce) |
| 2 | (Full operator root) launch supervisor + watchdog — detached ticks |
| 3 | `status_report` / measurements — still alive? |
| 4 | `python -u scripts/plant_control.py stop` — STOP files + identity-checked tree kill; survivors reported |

**Clone alone = Job #1 smoke (step 1).** Full multi-hour plant needs a complete local Aetheria root (cycle body is private by design).

## Verify the supervisor (no LLM, no GPU)

```powershell
python -m aetheria demo --cycles 3
# or:
python -u scripts/aetheria.py demo --cycles 3
python -u scripts/demo_local_smoke.py
```

The **supervisor** (real code) starts a **mock runtime** (sleep + print + ledger files). That is heartbeat, checkpoint, and `lh_probe_summary_v1` without private keys, Ollama, or the private cycle body.

## Why public vs private

| Stays private | Why |
|---------------|-----|
| Living memory / session traces | User-specific; merge/concat forbidden |
| Mouth (Forge, local models) | Operator chair; must not parent the clock |
| Cycle body / probe internals | Security-sensitive runtime + unpublished research |
| Credentials, host paths | Deployment-specific |

This repo stays fully evaluable as infrastructure. See [docs/WHY.md](docs/WHY.md).

## Quick start

```powershell
git clone https://github.com/denisrigsby/Aetheria-sovereign-agent.git
cd Aetheria-sovereign-agent
python -u scripts/demo_local_smoke.py
```

**Status (read-only):**

```powershell
python -u scripts/status_report.py
```

**Stop (full install):**

```powershell
python -u scripts/aetheria.py stop --reason "operator"
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md) | **Protocol v1** (heartbeat, STOP, recover, exits) |
| [docs/STANDALONE_PRODUCT.md](docs/STANDALONE_PRODUCT.md) | Product boundary |
| [docs/STATE_MODEL.md](docs/STATE_MODEL.md) | Authoritative files |
| [docs/SANITIZED_DEMO.md](docs/SANITIZED_DEMO.md) | Sitting picture (no private dump) |
| [docs/WHY.md](docs/WHY.md) | Problem and non-goals |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Start / stop / recover |

## What this repository is not

- Not a hosted multi-tenant agent cloud
- Not a dump of private memory, registries, or host paths
- Not a chat UI or “digital employee” with a general shell
- Not “chat as the long-run parent”
- Not AUTORUN after a dirty death

## License

[MIT](LICENSE) © 2026 Denis Rigsby / Aetheria Project
