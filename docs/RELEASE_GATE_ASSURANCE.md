# Release gate — assurance (auditor checklist)

**Status:** Aetheria is **not** described as production-ready until items below are CI **PASS**.

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL** | Role/junk PID refusal tested; full creation-time reuse sim limited on Linux CI. Plant `gate_stale_pid_reuse_v1` does not claim OS PID-number reuse was observed. Portable pytest alone does not flip that gate. |
| Interrupted write → old OR new valid state | **PARTIAL** | Atomic helper + tests; not all writers migrated |
| Simultaneous start/recover → ≤1 worker | **PASS** | Sealed after both control-plane pytest jobs passed on `424b52d` (run 35692278176): Ubuntu "Control plane checks" and Windows "Windows launcher and process tests". Evidence is `tests/test_two_controller_concurrency.py` on both jobs. Two processes race start vs recover: exactly one spawn. Live role, live claim, lock timeout, and a corrupt claim refuse. Windows `/Date(ms)/` create_time is stored as `ms:<digits>` and is not a host path. A create_time mismatch is not killed. Admit launch sets `stop_old=false`. Not this proof: a live Windows plant dual-launch, watchdog relaunch, or raw `launch_lh_detached.py` outside this admit. |
| Corrupted / unknown-version state → HOLD | **PARTIAL** | Hash mismatch refuse tested; full HOLD wiring plant-side |
| Clean stop ≠ crash | **PARTIAL** | Documented; needs explicit CI |
| Localhost mutations require authorization | **PARTIAL** | Loopback-only; per-launch token tracked |
| No secrets / host paths in public artifacts | **PASS** | Repo hygiene + .gitignore doctrine |

Update this table only when CI proves a change. No soft-green.

## Update after P0b

Historical notes from that slice. They are not the authoritative gate. The table above is. The P0b start/recover row was not a pass: its lock test checked unique thread names and was not on the control-plane pytest list.

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL→improved** | `process_identity_bind` creation-time mismatch refuses kill |
| Simultaneous start/recover → ≤1 worker | **insufficient** | `CampaignLock` existed; start/recover did not use it. See the primary row. |
| Localhost mutations require authorization | **PARTIAL→improved** | Talk-face ref POST requires `X-Aetheria-Token` |
| Job Object containment | **PARTIAL** | `job_object_win.py` helper shipped; Linux CI does not re-prove it. Plant `gate_job_object_kill_path_v1` is indexed in [CLOSEOUT.md](CLOSEOUT.md) (identity-checked `TerminateJobObject` on an assigned tree). Not the sole stop path. Toolhelp not retired. This row stays PARTIAL. |

## Update after start/recover single-flight

| Gate | Status | Notes |
|------|--------|-------|
| Simultaneous start/recover → ≤1 worker | **FAIL→PASS** | Sealed when Ubuntu and Windows control-plane jobs both passed on `424b52d` (run 35692278176). `6f7d7be` Windows failures were the `/Date/` claim assertion, the dead-PID helper, and the status subprocess ban. create_time on the claim is a reuse check for that admit, not `gate_stale_pid_reuse_v1` and not `gate_expected_create_time_call_sites_v1`. Other state writers stay **PARTIAL**. Still open: corrupted/unknown-version → HOLD, clean-stop CI. No soft_ACCEPT. No L7 / LIVE_RSI. This tree is not the plant. |

