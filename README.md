# Aetheria

[![CI](https://github.com/denisrigsby/Aetheria/actions/workflows/ci.yml/badge.svg)](https://github.com/denisrigsby/Aetheria/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/denisrigsby/Aetheria)](https://github.com/denisrigsby/Aetheria/releases)

**Aetheria is a local plant clock for serious AI work on your Windows PC.**
Chat is a mouth you can open or close. **The work clock is not the chat.**

**Literal subtitle:** A Windows-local, fail-closed supervisor for long-running AI work loops.

> **Scope (read this):** Windows-first · local-only · reference implementation.  
> This public repo ships a **real supervisor control plane** and a **mock / reference worker**.  
> The private operator plant (Forge console, living memory, real cycle body) is **not** included.

People need AI work that keeps going when the chat dies — overnight, after a crash, without babysitting a fragile window.

### 30-second scenario

Start a long job → close the UI → kill the worker mid-cycle → see heartbeat go stale and land in **HOLD** (fail-closed) → recover only through an identity-checked path (not blind PID reuse).  
Runnable public slice: `python -u scripts/demo_continuity.py` (UI closed, pulse continues). Full narrative: [docs/SCENARIO_30S.md](docs/SCENARIO_30S.md).

### Glossary

| Aetheria term | Plain technical equivalent |
|---------------|----------------------------|
| Plant clock | Detached supervised job runtime |
| Mouth / Talk-face | Optional local chat or operator UI |
| Forge | Private operator console |
| Tick / cycle | One bounded unit of agent work |
| HOLD | Fail-closed paused state pending operator action |

More: [docs/GLOSSARY.md](docs/GLOSSARY.md) · Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/ARCHITECTURE_PUBLIC_OVERLAY.md](docs/ARCHITECTURE_PUBLIC_OVERLAY.md) · States: [docs/STATE_TRANSITIONS.md](docs/STATE_TRANSITIONS.md)

Origin: solo human–AI collaboration on a real Windows operator machine. See [docs/ORIGIN.md](docs/ORIGIN.md) · [docs/DEFINITION.md](docs/DEFINITION.md).

## Continuity proof (run this)

```powershell
python -u scripts/demo_continuity.py
# or: Demo-Continuity.bat
```

Public reference only (mock pulse + Talk-face reference mouth). Close Talk-face; the pulse file keeps advancing. That is **plant clock â‰  chat**, runnable.
Docs: [docs/CONTINUITY_DEMO.md](docs/CONTINUITY_DEMO.md) Â· Claims: [docs/CLAIMS.md](docs/CLAIMS.md)

Talk-face only:

```powershell
python -u scripts/talk_face_ref_demo.py
```

## One plant, two surfaces

| Surface | Role |
|---------|------|
| **Talk-face** | Scrubbed localhost safety mouth |
| **Forge** | Industrial operator console (private plant) |

Same plant underneath. Surfaces do not own the clock. See [docs/DUAL_FACE.md](docs/DUAL_FACE.md).

## Discovery posts

Paste-ready Show HN / Reddit text: [docs/DISCOVERY_POST.md](docs/DISCOVERY_POST.md).

The private install Ã¢â‚¬â€ **mouth** (local admin / architect) + **plant** (detached ticks) + living memory Ã¢â‚¬â€ is an **extension**, not a missing GitHub file. Chat never parents the clock. Talk is a mirror of the ledger, not a dependency: if the chat window is closed, the worker still ticks. Dirty `last_ok` **HOLDs**. There is **no AUTORUN** after a dirty death.

**Plant clock Ã¢â€°Â  chat.**

Protocol: [docs/RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md) Ã‚Â· boundary: [docs/STANDALONE_PRODUCT.md](docs/STANDALONE_PRODUCT.md) Ã‚Â· state: [docs/STATE_MODEL.md](docs/STATE_MODEL.md) Ã‚Â· operator walkthrough: [docs/SANITIZED_DEMO.md](docs/SANITIZED_DEMO.md)

Launcher: `python -u scripts/aetheria.py status|stop|start|resume|recover|diagnose|demo`

`recover` is not `start`. Recover loads `measurements/campaign_snapshot_v1.json` only when the supervisor is identity-dead. Hash mismatch Ã¢â€ â€™ no spawn.

> Think **supervisor / pm2 for agent work loops**: hard stop, recovery, structured cycle completion Ã¢â‚¬â€ not a multi-agent framework and not a chat UI.

### The pain this targets

| Common AI complaint | Control plane answer |
|---------------------|----------------------|
| Dies when chat/IDE closes | Detached supervisor + on-disk state |
| Hangs / stuck forever | Timeouts, STOP files, conservation bounds |
| Ã¢â‚¬Å“Is it still working?Ã¢â‚¬Â | `status_report` + measurements JSON |
| Overnight babysitting | Rolling ticks / segments + watchdog |
| Thrash restart after power flap | HOLD after dirty `last_ok`; resume when stable |
| Chat is the whole runtime | **Plant clock Ã¢â€°Â  chat** Ã¢â‚¬â€ chat never owns the schedule |
| Crash vs green stop | Dirty `last_ok=false` HOLDs; green interruptions may guardian-start |

### Job #1 Ã¢â‚¬â€ local campaign runner

| Step | What you prove |
|------|----------------|
| 1 | `python -u scripts/demo_local_smoke.py` Ã¢â‚¬â€ control plane layout + compile (no private sauce) |
| 2 | (Full operator root) launch supervisor + watchdog Ã¢â‚¬â€ detached ticks |
| 3 | `status_report` / measurements Ã¢â‚¬â€ still alive? |
| 4 | `python -u scripts/plant_control.py stop` Ã¢â‚¬â€ STOP files + identity-checked tree kill; survivors reported |

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
git clone https://github.com/denisrigsby/Aetheria.git
cd Aetheria
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
- Not a chat UI or Ã¢â‚¬Å“digital employeeÃ¢â‚¬Â with a general shell
- Not Ã¢â‚¬Å“chat as the long-run parentÃ¢â‚¬Â
- Not AUTORUN after a dirty death

## License

[MIT](LICENSE) Ã‚Â© 2026 Denis Rigsby / Aetheria Project
