# Claims taxonomy

Public pages use four front labels. They match the [README](../README.md) and the [evidence index](../FINAL_STATE_BRIEF.md).

| Front label | Meaning |
|-------------|---------|
| **Real** | You can run it in this repository, or CI on main runs it |
| **Proved** | A scrubbed receipt is in this repo (or the closeout says the note has no gate file) |
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
| Process identity rejects wrong role / junk PID | **Real** | **Tests** | CI runs `tests/test_lh_process_identity.py`. `tests/test_process_identity_adversarial.py` is in the repo and is not in the CI command |
| Simultaneous start/recover admits one supervisor | **Real** | **Tests** | **PASS** in [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md). CI runs `tests/test_two_controller_concurrency.py`. Not the live plant |
| Talk-face reference refuses plant_chat / kit_act and requires confirm | **Real** | **Untested** | `tests/test_talk_face_ref_allowlist.py` exists. The CI command on main does not run it |
| Unrelated processes survive stale-PID recovery | **Pending** | **Untested** | Assurance row is **PARTIAL** |
| Stale-PID start-time refuse on the operator plant | **Proved** | **Private** | `gate_stale_pid_reuse_v1` receipt. OS PID-number reuse was not observed. Portable pytest does not flip that gate |
| Job Object tree kill on the operator plant | **Proved** | **Private** | `gate_job_object_kill_path_v1`. Not the only stop path. This repo's CI row stays **PARTIAL** |
| Interrupted write leaves old or new valid state | **Pending** | **Untested** | Assurance **PARTIAL**. `tests/test_atomic_state_writes.py` is not the whole writer set and is not in the CI command |
| Snapshot digest is an authenticity signature (HMAC) | **Locked** | **Private** | Public digests are integrity checksums only |
| Live plant, living memory, Forge, real cycle body | **Locked** | **Private** | Not shipped. Public export ≠ live plant (**PRIVATE_AHEAD**) |
| Dual-bank full program | **Locked** | — | No receipt for `gate_full_program_asset_class_v1` in this repo |
| P1–P5 | — | — | Internal certification only. Not external accreditation. Not a public PASS |
| Production-ready, enterprise, autonomous, self-healing | **Locked** | — | [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md) is not all PASS |

Plant receipt wording and exclusions: [CLOSEOUT.md](CLOSEOUT.md).
