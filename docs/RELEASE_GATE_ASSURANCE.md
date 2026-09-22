# Release gate — assurance (auditor checklist)

**Status:** Aetheria is **not** described as production-ready until items below are CI **PASS**.

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL** | Role/junk PID refusal tested; full creation-time reuse sim limited on Linux CI. Plant `gate_stale_pid_reuse_v1` does not claim OS PID-number reuse was observed. Portable pytest alone does not flip that gate. |
| Interrupted write → old OR new valid state | **PARTIAL** | Atomic helper + tests; not all writers migrated |
| Simultaneous start/recover → ≤1 worker | **FAIL** | Needs two-controller concurrency tests |
| Corrupted / unknown-version state → HOLD | **PARTIAL** | Hash mismatch refuse tested; full HOLD wiring plant-side |
| Clean stop ≠ crash | **PARTIAL** | Documented; needs explicit CI |
| Localhost mutations require authorization | **PARTIAL** | Loopback-only; per-launch token tracked |
| No secrets / host paths in public artifacts | **PASS** | Repo hygiene + .gitignore doctrine |

Update this table only when CI proves a change. No soft-green.

## Update after P0b

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL→improved** | `process_identity_bind` creation-time mismatch refuses kill |
| Simultaneous start/recover → ≤1 worker | **PARTIAL** | `CampaignLock` + concurrency test (lock protocol) |
| Localhost mutations require authorization | **PARTIAL→improved** | Talk-face ref POST requires `X-Aetheria-Token` |
| Job Object containment | **PARTIAL** | `job_object_win.py` helper shipped; Linux CI does not re-prove it. Plant `gate_job_object_kill_path_v1` is indexed in [CLOSEOUT.md](CLOSEOUT.md) (identity-checked `TerminateJobObject` on an assigned tree). Not the sole stop path. Toolhelp not retired. This row stays PARTIAL. |

