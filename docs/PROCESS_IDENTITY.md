# Process identity protocol (public)

**Purpose:** Never kill, resume, or adopt a Windows process on PID alone (PIDs are reused).

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
| PID alive, creation time mismatch vs recorded | **Refuse** (likely PID reuse) |
| PID alive, exe path unexpected | **Refuse** |
| All bound fields match recorded identity | Allow role-scoped operations only |

## Current public implementation

- Role classification from cmdline: `scripts/lh_process_identity.py` (**Tests**)
- Creation-time + exe binding: extended helpers + adversarial tests in this PR (**Tests** / partial on non-Windows CI)
- Windows Job Objects for tree kill: **Untested** aspirational — do not claim until coded + CI-proven

## Mismatch policy

A mismatch must **never** kill, resume, or adopt. Prefer HOLD / report survivors.
