# Release gate — assurance (auditor checklist)

**Status:** The first table is the status on main. Later sections are history. They do not override the first table.

Simultaneous start/recover is **PASS** in that table (control-plane test, both CI jobs). That row does not change the **PARTIAL** rows, and it does not make this tree the live plant.

Interrupted write → old OR new valid state is **PASS** in that table. Both control-plane jobs were green on `395643e` (run 35695450920). That does not flip corrupted / unknown-version → HOLD or clean stop ≠ crash, and it does not make this tree the live plant.

This checklist is not a production-ready claim. Several rows are still **PARTIAL**. Front labels: **PASS** here is **Real** in the [README](../README.md); **PARTIAL** stays **Pending**.

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL** | Role/junk PID refusal tested; full creation-time reuse sim limited on Linux CI. Plant `gate_stale_pid_reuse_v1` does not claim OS PID-number reuse was observed. Portable pytest alone does not flip that gate. |
| Interrupted write → old OR new valid state | **PASS** | Sealed: both control-plane jobs green on `395643e` (run 35695450920) — Ubuntu "Control plane checks" and Windows "Windows launcher and process tests". Evidence is `tests/test_atomic_state_writes.py` and `tests/test_interrupted_state_writes.py` on both jobs. Public control-plane JSON documents use `atomic_write_json` (temp, fsync, replace). Exclusions: private plant ≠ this tree; no L7 / LIVE_RSI; no soft_ACCEPT; PID and STOP files stay short in-place text; append-only JSONL is not document replacement; `research/` experiment artifacts are outside this control plane. Corrupted / unknown-version → HOLD stays **PARTIAL**. Clean stop ≠ crash stays **PARTIAL**. |
| Simultaneous start/recover → ≤1 worker | **PASS** | Sealed: both control-plane pytest jobs green on `424b52d` (run 35692278176) — Ubuntu "Control plane checks" and Windows "Windows launcher and process tests". Evidence is `tests/test_two_controller_concurrency.py` on both jobs (exactly one spawn). Windows `/Date(ms)/` create_time is stored as `ms:<digits>` and is not a host path. A create_time mismatch is not a kill and is not `gate_stale_pid_reuse_v1` or `gate_expected_create_time_call_sites_v1`. Corrupted / unknown-version → HOLD stays **PARTIAL**. Clean stop ≠ crash stays **PARTIAL**. No soft_ACCEPT. No L7 / LIVE_RSI. This tree is not the plant. |
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

