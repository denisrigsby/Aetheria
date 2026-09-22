# Process identity protocol (public)

**Purpose:** Design rule — do not kill, resume, or adopt a Windows process on PID number alone. OS PID-number reuse was not observed (`gate_stale_pid_reuse_v1` does not claim it). The assurance row "unrelated processes survive stale-PID recovery" stays **PARTIAL**.

## Binding tuple (required fields)

An identity match for supervisor / watchdog / probe roles SHOULD bind:

1. **PID**
2. **Process creation time** (Windows `CreationDate` / equivalent)
3. **Executable path** (resolved image name)
4. **Normalized command line** (role tokens; see `scripts/lh_process_identity.py`)
5. **Campaign / run UUID** when a campaign is active (on-disk association)
6. **Parent PID** and, when available, **Job Object** membership

## Decision rule

| Observation | Action |
|-------------|--------|
| PID missing / dead | Do not kill; reconcile PID files; treat as not alive |
| PID alive, role cmdline mismatch | **Refuse** kill / resume / adopt |
| PID alive, creation time mismatch vs recorded | **Refuse** (`create_time_mismatch`). The plant receipt covers `kill_if_verified` with `expected_create_time`. It does not record that an OS PID number was reused |
| PID alive, exe path unexpected | **Refuse** |
| All bound fields match recorded identity | Allow role-scoped operations only |

## Current public implementation

- Role classification from cmdline: `scripts/lh_process_identity.py` (**Tests**)
- Creation-time + exe binding: extended helpers + adversarial tests in this repo (**Tests** / partial on non-Windows CI). Pytest in this clone does not flip `gate_stale_pid_reuse_v1`. That pytest is not a tree-kill.
- Windows Job Objects for tree kill: plant `gate_job_object_kill_path_v1` is dual-banked for an identity-checked `TerminateJobObject` on an assigned tree (root and child dead). **Proved on Windows**. **Locked on non-Windows**. Not the sole stop path. Toolhelp is not retired. Linux CI in this clone does not re-prove that gate. Role matching on Ubuntu CI is not this stop.

## Plant receipts (create_time)

`gate_stale_pid_reuse_v1` revision `create_time_bind_v1` (`dual_bank=true`, `soft_ACCEPT=false`): `kill_if_verified` with `expected_create_time` refuses `create_time_mismatch` (and does not terminate) when live create_time disagrees with the bound value, even if cmdline still matches the claimed role.

Exclusions: OS PID-number reuse was not observed and is not required. Not every call site. create_time is not sole identity. PID reuse is not impossible. A wrong live PID mismatch alone does not flip the gate. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. Job Object is not the sole stop path. Toolhelp is not retired.

`gate_expected_create_time_call_sites_v1` revision `call_site_wire_v1` (`dual_bank=true`, `soft_ACCEPT=false`): live kill call sites `lh_watchdog.kill_pid`, `plant_control._kill_pid`, `lh_recover_reap.reap_orphan_probes`, and `status_report.reap_orphans` pass `expected_create_time` into `kill_if_verified`; wrong create_time refuses with `create_time_mismatch` and does not terminate.

Exclusions: OS PID-number reuse was not observed. Not every future kill site. create_time is not sole identity. No L7, LIVE_RSI, second clock, autonomy, or public=plant.

Index: [CLOSEOUT.md](CLOSEOUT.md).

## Mismatch policy

A mismatch must **never** kill, resume, or adopt. Prefer HOLD / report survivors.

## Binding helper

See scripts/process_identity_bind.py (creation time / exe / parent / campaign UUID / job object fields).
