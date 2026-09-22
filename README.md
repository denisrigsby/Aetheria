# Aetheria

[![CI](https://github.com/denisrigsby/Aetheria/actions/workflows/ci.yml/badge.svg)](https://github.com/denisrigsby/Aetheria/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/denisrigsby/Aetheria)](https://github.com/denisrigsby/Aetheria/releases)

A local supervisor for long-running AI work on one Windows PC. The chat window is optional. The work schedule is a separate process plus files on disk.

**Plant clock ≠ chat.** "Plant clock" means that schedule. "Chat" (also called the mouth, or Talk-face) does not own it. Closing the chat does not stop the schedule.

This repository is a public control-plane export. It is **not** the live operator plant. The parity label is **PRIVATE_AHEAD** (public export ≠ live plant): [docs/EXPORT_PARITY.md](docs/EXPORT_PARITY.md).

P1–P5 are internal certification labels used on the operator plant. They are not an outside audit, and this repo does not treat them as one.

## This repo and the private plant

| In this GitHub repo | On the private operator machine |
|---------------------|----------------------------------|
| Supervisor, watchdog, stop and recover scripts, docs | Live plant, Forge console, living memory, real cycle body |
| A mock / reference worker you can run | Host paths, credentials, private measurements |
| Scrubbed receipt copies under [measurements/public_index/](measurements/public_index/) | The mouth and plant code those receipts describe |

Cloning this repo does not give you the live plant. A full multi-hour run needs a complete local operator root. That root is private by design.

## Real, proved, pending, locked

Finer labels (Tests, Mock, Untested, Private) live in [docs/CLAIMS_TAXONOMY.md](docs/CLAIMS_TAXONOMY.md). The four words below are the ones that matter on this page. A receipt or a named CI check sits beside each claim, and the exclusion sits in the same row. One **PASS** cell is that row only. The evidence index is [FINAL_STATE_BRIEF.md](FINAL_STATE_BRIEF.md).

### Real (in this repository, or the CI workflow on main runs it)

| What | Limit | Evidence |
|------|--------|----------|
| Layout and compile of this tree | Does not start the private plant | `python -u scripts/demo_local_smoke.py` · [docs/PUBLIC_DEMO.md](docs/PUBLIC_DEMO.md) |
| Reference mouth closes; a mock pulse keeps advancing | Mock worker. This is the public slice of plant clock ≠ chat. CI does not run this script | `python -u scripts/demo_continuity.py` · [docs/CONTINUITY_DEMO.md](docs/CONTINUITY_DEMO.md) |
| Process identity rejects the wrong role or a junk PID. Windows tasklist liveness uses the PID column | "Unrelated processes survive stale-PID recovery" stays **PARTIAL**. The PID-column test does not flip `gate_stale_pid_reuse_v1`. OS PID-number reuse was not observed. This row is not a tree-kill. Tree-kill and Job Object stop are **Proved on Windows** only where a receipt says so, and **Locked on non-Windows** | CI runs `tests/test_lh_process_identity.py` and `tests/test_pid_liveness_exact.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| A raced start and recover admit one supervisor | Assurance row is **PASS** for that test (exactly one spawn) on the Ubuntu and Windows CI jobs. It is not a tree-kill and not a watchdog relaunch. Tree-kill and Job Object stop are **Locked on non-Windows**. Corrupted / unknown-version → HOLD and clean stop ≠ crash stay **PARTIAL**. The test is not the live plant | CI runs `tests/test_two_controller_concurrency.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| An interrupted JSON state write leaves the previous valid document or the new one | Assurance row is **PASS** for that test. Private plant ≠ this tree. No L7 / LIVE_RSI. No soft_ACCEPT. PID and STOP files are short in-place text. Append-only JSONL is out of scope. `research/` artifacts are out of scope. HOLD and clean stop stay **PARTIAL** | CI on `395643e` (run 35695450920) runs `tests/test_atomic_state_writes.py` and `tests/test_interrupted_state_writes.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |

### Proved (a receipt is in this repo)

These were accepted on the operator plant. The JSON files are scrubbed copies. Cloning does not re-run them. Exclusions in full: [docs/CLOSEOUT.md](docs/CLOSEOUT.md).

| Claim, in plain language | What it does not prove | Receipt |
|--------------------------|------------------------|---------|
| Talk-face text has no visible `[MODEL_REASONING]` tag. Absolute `/living/` cites are rewritten or refused | Does not publish plant source. Copilot is not the mouth | [scrub](measurements/public_index/scrub_mouth_leak_v1.json), [gate](measurements/public_index/gate_talkface_visible_tag_seal_v1.json), [accept](measurements/public_index/architect_accept_talkface_visible_tag_seal_v1.json) |
| Direct-answer contract accepted by Cover and Architect. `soft_ACCEPT` is false. `dual_bank` is false | Does not unlock L7 or LIVE_RSI | [gate](measurements/public_index/gate_direct_answer_contract_talk_face_v1.json), [accept](measurements/public_index/architect_accept_direct_answer_contract_talk_face_v1.json) |
| A kill is refused when the process start time does not match, even if the command line still looks right | OS PID-number reuse was not observed. Tests in this repo do not flip that plant gate | [gate](measurements/public_index/gate_stale_pid_reuse_v1_1412.json) |
| Four named kill sites pass that start time and refuse a mismatch | Not every future kill site. Start time is not the only identity check | [gate](measurements/public_index/gate_expected_create_time_call_sites_v1_930b.json) |
| Supervised clock ran 30 minutes with the mouth closed and the tick advanced | Longer runs stay locked | [gate](measurements/public_index/gate_endurance_v1_0440.json) |
| An identity-checked Windows Job Object stop ended an assigned process tree | **Proved on Windows** (operator plant). **Locked on non-Windows**. Not the only stop path. Linux CI does not re-prove it. Toolhelp is not retired | [gate](measurements/public_index/gate_job_object_kill_path_v1_a709.json) |
| Export hash census, with an explicit parity decision | The decision on the receipt is **PRIVATE_AHEAD**, so public ≠ plant | [gate](measurements/public_index/gate_export_hash_parity_v1_79b2.json) |
| Resume / stop / watchdog record is dual-banked | The receipt has no claim sentence (`claim_wording` is null). No stop or relaunch behavior is claimed. Not a portable control plane | [gate](measurements/public_index/gate_control_plane_resume_stop_watchdog_v1_84f7.json) |

### Pending (not PASS on main)

- Re-run of the receipts above inside this clone. The mouth and the plant body are not in this tree. [docs/CLOSEOUT.md](docs/CLOSEOUT.md)
- Same Talk Face session, **no gate file**: Standby vs Offline labels, one desktop shortcut, windowed Edge instead of a frameless app window. Operator notes only. [docs/CLOSEOUT.md](docs/CLOSEOUT.md)
- Assurance rows that are still **PARTIAL**: unrelated processes surviving stale-PID recovery; corrupted or unknown-version state ending in HOLD; clean stop distinguished from a crash; localhost mutations requiring authorization; a general "no secrets" scan (the CI path scan is narrower — see the assurance table). [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md)
- Job Object containment on this repo's CI (**PARTIAL**). The plant receipt above is **Proved on Windows** only. It does not make the CI row PASS, and it is **Locked on non-Windows**.
- Watchdog relaunch of a process tree. No gate file. Windows is the reference. **Pending** on non-Windows. Not a portable stop.
- Held-out L5 "6/6" after the dual-face cut. No scrubbed receipt in this repo. [docs/CLAIMS.md](docs/CLAIMS.md)

### Locked (not claimed)

- This tree equals the live plant
- Dual-bank full program. No receipt for `gate_full_program_asset_class_v1` is in this repo
- `soft_ACCEPT`, LIVE_RSI, L7
- Copilot as the plant mouth
- Federation, swarm, autonomy, self-healing, gated self-modification
- Production-ready, enterprise, enterprise-grade, revolutionary
- A second clock, automatic dispatch, live model hot-swap
- Endurance past the 30-minute receipt
- Job Object as the only stop path
- A portable control plane: tree-kill, Job Object stop, or watchdog relaunch on non-Windows
- A wider spawn wrap
- P1–P5 as external accreditation

## Run and check

Python 3.10+. Windows is the reference OS for stop, tree-kill, Job Object, and relaunch. The smoke commands below can run on other systems. They do not make stop or relaunch portable.

```powershell
git clone https://github.com/denisrigsby/Aetheria.git
cd Aetheria

# 1. Run — layout and compile. No private plant.
python -u scripts/demo_local_smoke.py

# 2. Test — reference mouth closes; the mock pulse still advances.
python -u scripts/demo_continuity.py

# 3. Local checks — identity, single-flight start/recover, and fault injection.
python -m pip install pytest
python -m pytest tests/test_lh_process_identity.py tests/test_pid_liveness_exact.py tests/test_two_controller_concurrency.py tests/test_fault_injection_public.py -q
```

Windows wrappers for steps 1 and 2: `Demo-Local.bat`, `Demo-Continuity.bat`.

[CI](https://github.com/denisrigsby/Aetheria/actions/workflows/ci.yml) runs the files named in `.github/workflows/ci.yml`, including `tests/test_lh_process_identity.py`, `tests/test_pid_liveness_exact.py`, `tests/test_two_controller_concurrency.py`, `tests/test_atomic_state_writes.py`, and `tests/test_interrupted_state_writes.py`. It does not run `demo_continuity.py`, `tests/test_fault_injection_public.py`, or `tests/test_talk_face_ref_allowlist.py`. Those three are local checks. The workflow file is the list.

On a full local root, read-only status is `python -u scripts/status_report.py`. Stop is `python -u scripts/aetheria.py stop` (Windows tree-kill / Job Object; **Locked on non-Windows**). Recover is a different command from start: [docs/OPERATIONS.md](docs/OPERATIONS.md). The CI start/recover test is one supervisor admitted. It is not an OS relaunch.

## Read next

| Doc | Why |
|-----|-----|
| [FINAL_STATE_BRIEF.md](FINAL_STATE_BRIEF.md) | Evidence index (real / proved / pending / locked) |
| [docs/CLOSEOUT.md](docs/CLOSEOUT.md) | Receipt tables and exclusions |
| [docs/CLAIMS_TAXONOMY.md](docs/CLAIMS_TAXONOMY.md) | Front labels and finer labels |
| [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) | PASS / PARTIAL / FAIL |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Plant clock, mouth, HOLD, Forge |
| [docs/WHY.md](docs/WHY.md) | Problem and non-goals |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers |
| [docs/RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md) | Heartbeat, STOP, recover |
| [SETUP.md](SETUP.md) | What a full local root still needs |
| [docs/SCENARIO_30S.md](docs/SCENARIO_30S.md) | The crash-and-hold picture, and what this clone can show |

### Glossary (short)

| Term | Plain meaning |
|------|----------------|
| Plant clock | Detached supervised job runtime |
| Mouth / Talk-face | Optional local chat or operator UI |
| Forge | Private operator console |
| Tick / cycle | One bounded unit of work |
| HOLD | Fail-closed pause until an operator acts |
| Cover / Architect | Two accept roles on a plant receipt. Both accepted means the receipt says so. It is not an outside audit |

## License

[MIT](LICENSE) © 2026 Denis Rigsby / Aetheria Project
