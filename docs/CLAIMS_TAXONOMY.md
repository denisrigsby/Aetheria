# Claims taxonomy

Every public claim about Aetheria must be labeled exactly one of:

| Label | Meaning |
|-------|---------|
| **Tests** | Demonstrated by automated CI tests in this repository |
| **Mock** | Demonstrated only with a mock / reference worker |
| **Untested** | Implemented in public code but not yet CI-proven |
| **Private** | Lives in the private operator plant — unverifiable from this repo |

## Current map (honest)

| Claim | Label | Evidence / note |
|-------|-------|-----------------|
| Supervisor / watchdog / STOP / heartbeat files exist as control plane | **Tests** | CI + public scripts |
| Talk-face reference refuse plant_chat / kit_act / fail-closed confirm | **Tests** | `tests/test_talk_face_ref_allowlist.py` |
| Continuity: pulse advances after mouth closes | **Mock** | `scripts/demo_continuity.py` |
| Crash→resume multi-step with verified checkpoints | **Mock** / plant-private prove | Public slice is mock-safe; full plant prove is **Private** |
| Process identity rejects wrong role / junk PID | **Tests** | `tests/test_lh_process_identity.py`, `tests/test_process_identity_adversarial.py` |
| Stale-PID never kills unrelated process | **Tests** (partial) in this repo; plant receipt is separate | Adversarial tests here. Plant `gate_stale_pid_reuse_v1` (`create_time_bind_v1`) refuses `create_time_mismatch` and does not terminate. OS PID-number reuse was not observed. Portable pytest alone does not flip that gate. |
| Job Object tree kill | **Private** receipt; **PARTIAL** on this repo's CI | Plant `gate_job_object_kill_path_v1`: identity-checked `TerminateJobObject` stops an assigned tree. Not the sole stop path. Toolhelp not retired. Linux CI does not re-prove it. |
| Atomic measurements writes (temp→replace) | **Tests** (partial) | `tests/test_atomic_state_writes.py` |
| Snapshot digest authenticity (HMAC) | **Private** / not claimed | Public digests are **integrity checksums only** |
| Real multi-hour cycle body / living memory / Forge | **Private** | Not shipped |
| Production-ready for valuable/security-sensitive work | **Not claimed** | See [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md) |

When in doubt, prefer a weaker label.
