# Windows Job Objects (stop containment)

## Why

PID ancestry reconstruction is unsafe. Prefer assigning the worker tree to a **Job Object** and terminating the job after identity checks pass.

## Plant gate (2026-09-22 evening)

`gate_job_object_kill_path_v1` is dual-banked (`dual_bank=true`, Cover ACCEPT, Architect ACCEPT, `soft_ACCEPT=false`).

Claim, as the receipt words it: Job Object kill-path as defined by `gate_job_object_kill_path_v1`: identity-checked `TerminateJobObject` stops an assigned process tree (root and child dead).

Exclusions beside that claim: **Proved on Windows**. **Locked on non-Windows**. Job Object is not the sole plant stop path. Toolhelp is not retired. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. This gate does not claim stale-PID reuse, the export-hash layer, or a portable relaunch. Endurance beyond `gate_endurance_v1` stays locked.

Receipt: [gate_job_object_kill_path_v1_a709.json](../measurements/public_index/gate_job_object_kill_path_v1_a709.json). Index: [CLOSEOUT.md](CLOSEOUT.md).

## Public status

| Piece | Status |
|-------|--------|
| `scripts/job_object_win.py` Create/Assign/Terminate helpers | **Real** on Windows as code in this tree. **Locked on non-Windows**. Linux CI does not run them |
| Plant `TerminateJobObject` on an assigned tree | **Proved on Windows** (`gate_job_object_kill_path_v1`). **Locked on non-Windows** |
| Sole plant stop path / Toolhelp retired | **Locked** |
| Identity mismatch still refuses kill | **Tests** via `process_identity_bind.refuse_action_on_mismatch`. That refuse is not a tree-kill |
| This repo's release-gate CI | **PARTIAL** — Linux CI does not re-prove the plant gate |
| Watchdog relaunch | **Pending**. No gate file. Not a portable control plane |

The helper in this clone is not the plant seal. Job Object containment is not the only stop path, and it is not a portable stop.
