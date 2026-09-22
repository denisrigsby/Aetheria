# Windows Job Objects (stop containment)

## Why

PID ancestry reconstruction is unsafe. Prefer assigning the worker tree to a **Job Object** and terminating the job after identity checks pass.

## Plant gate (2026-09-22 evening)

`gate_job_object_kill_path_v1` is dual-banked (`dual_bank=true`, Cover ACCEPT, Architect ACCEPT, `soft_ACCEPT=false`).

Claim, as the receipt words it: Job Object kill-path as defined by `gate_job_object_kill_path_v1`: identity-checked `TerminateJobObject` stops an assigned process tree (root and child dead).

Exclusions beside that claim: Job Object is not the sole plant stop path. Toolhelp is not retired. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. This gate does not claim stale-PID reuse or the export-hash layer. Endurance beyond `gate_endurance_v1` stays locked.

Receipt: [gate_job_object_kill_path_v1_a709.json](../measurements/public_index/gate_job_object_kill_path_v1_a709.json). Index: [CLOSEOUT.md](CLOSEOUT.md).

## Public status

| Piece | Status |
|-------|--------|
| `scripts/job_object_win.py` Create/Assign/Terminate helpers | **Untested** on CI Linux; available on Windows |
| Sole plant stop path / Toolhelp retired | **Not claimed** |
| Identity mismatch still refuses kill | **Tests** via `process_identity_bind.refuse_action_on_mismatch` |
| This repo's release-gate CI | **PARTIAL** — Linux CI does not re-prove the plant gate |

The helper in this clone is not the plant seal. Do not claim Job Object containment as the only stop path.
