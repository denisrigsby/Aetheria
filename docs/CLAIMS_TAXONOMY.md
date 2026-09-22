# Claims taxonomy

Public pages use four front labels. They match the [README](../README.md) and the [evidence index](../FINAL_STATE_BRIEF.md).

| Front label | Meaning |
|-------------|---------|
| **Real** | You can run it in this repository, or CI on main runs it |
| **Proved** | A scrubbed gate file is in this repo. An operator note with no gate file is **Pending** |
| **Pending** | Named, and not PASS on main |
| **Locked** | Withheld. Not a claim |

Finer labels, when a front label needs a split:

| Finer label | Meaning |
|-------------|---------|
| **Tests** | A test in this repository, and the CI workflow on main runs it |
| **Mock** | Shown only with a mock / reference worker |
| **Untested** | Code or a test file is here, and the CI workflow on main does not prove it |
| **Private** | On the operator plant. Unverifiable from this repo unless a scrubbed receipt is indexed (then the front label is **Proved**, with that limit) |

When in doubt, prefer the weaker label.

## Current map

| Claim | Front | Finer | Evidence |
|-------|-------|-------|----------|
| Supervisor, watchdog, STOP, and heartbeat files exist | **Real** | **Tests** | CI and the public scripts |
| Reference mouth closes; mock pulse keeps advancing | **Real** | **Mock** | `scripts/demo_continuity.py` |
| Process identity rejects wrong role / junk PID. Windows tasklist liveness uses the PID column | **Real** | **Tests** | CI runs `tests/test_lh_process_identity.py` and `tests/test_pid_liveness_exact.py`. `tests/test_process_identity_adversarial.py` is in the repo and is not in the CI command. Does not flip `gate_stale_pid_reuse_v1`. OS PID-number reuse was not observed. Not a tree-kill. Tree-kill is **Locked on non-Windows** |
| Simultaneous start/recover admits one supervisor | **Real** | **Tests** | **PASS** in [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md) for exactly one spawn. CI runs `tests/test_two_controller_concurrency.py` on Ubuntu and Windows. Not a tree-kill. Not a watchdog relaunch. Not the live plant |
| Talk-face reference refuses plant_chat / kit_act and requires confirm | **Real** | **Untested** | `tests/test_talk_face_ref_allowlist.py` exists. The CI command on main does not run it. Not a public PASS |
| Plant clock ≠ chat on the operator plant, beyond the 30-minute window | **Locked** | **Private** | `gate_endurance_v1` is that window only. The mock demo is **Real** |
| One plant, two surfaces, including Forge, as an operator-plant fact | **Pending** | **Private** | No gate file. Forge is not shipped in this tree. [DUAL_FACE.md](DUAL_FACE.md) describes the split |
| Standby / Offline, one desktop shortcut, windowed Edge launcher | **Pending** | **Private** | Operator notes. No gate file. [CLOSEOUT.md](CLOSEOUT.md) |
| Held-out L5 stays 6/6 | **Pending** | **Private** | No scrubbed receipt in this repo |
| Absolute Windows user-home paths absent from public markdown and example files | **Real** | **Tests** | CI step "No absolute Windows operator paths in public docs" in `.github/workflows/ci.yml`. Scope: `*.md` and `*.example.*` |
| No secrets in public artifacts | **Pending** | **Untested** | No secret scanner in CI. The path scan above does not cover this |
| Unrelated processes survive stale-PID recovery | **Pending** | **Untested** | Assurance row is **PARTIAL** |
| Stale-PID start-time refuse on the operator plant | **Proved** | **Private** | `gate_stale_pid_reuse_v1` receipt. OS PID-number reuse was not observed. Portable pytest does not flip that gate |
| Job Object tree kill on the operator plant | **Proved on Windows** | **Private** | `gate_job_object_kill_path_v1`. **Locked on non-Windows**. Not the only stop path. This repo's CI row stays **PARTIAL** |
| Watchdog relaunch of a process tree | **Pending** | — | No gate file. Windows is the reference. **Pending** on non-Windows. Not a portable control plane |
| Portable tree-kill or Job Object stop | **Locked** | — | Windows receipts do not apply off Windows |
| Interrupted write leaves old or new valid state | **Real** | **Tests** | **PASS** in [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md). Both control-plane jobs green on `395643e` (run 35695450920). CI runs `tests/test_atomic_state_writes.py` and `tests/test_interrupted_state_writes.py`. Private plant ≠ this tree. No L7 / LIVE_RSI. No soft_ACCEPT. PID/STOP text and append-only JSONL are out of scope. `research/` artifacts are out of scope |
| Snapshot digest is an authenticity signature (HMAC) | **Locked** | **Private** | Public digests are integrity checksums only |
| Live plant, living memory, Forge, real cycle body | **Locked** | **Private** | Not shipped. Public export ≠ live plant (**PRIVATE_AHEAD**) |
| Dual-bank full program | **Locked** | — | No receipt for `gate_full_program_asset_class_v1` in this repo |
| P1–P5 | — | — | Internal certification only. Not external accreditation. Not a public PASS |
| Production-ready, enterprise, enterprise-grade, revolutionary, autonomous, self-healing, gated self-modification | **Locked** | — | [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md) is not all PASS |

Plant receipt wording and exclusions: [CLOSEOUT.md](CLOSEOUT.md).
