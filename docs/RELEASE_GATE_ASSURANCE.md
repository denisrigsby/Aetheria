# Release gate — assurance (auditor checklist)

**Status:** Aetheria is **not** described as production-ready until items below are CI **PASS**.

| Gate | Status | Notes |
|------|--------|-------|
| Unrelated processes survive stale-PID recovery/stop | **PARTIAL** | Role/junk PID refusal tested; full creation-time reuse sim limited on Linux CI |
| Interrupted write → old OR new valid state | **PARTIAL** | Atomic helper + tests; not all writers migrated |
| Simultaneous start/recover → ≤1 worker | **FAIL** | Needs two-controller concurrency tests |
| Corrupted / unknown-version state → HOLD | **PARTIAL** | Hash mismatch refuse tested; full HOLD wiring plant-side |
| Clean stop ≠ crash | **PARTIAL** | Documented; needs explicit CI |
| Localhost mutations require authorization | **PARTIAL** | Loopback-only; per-launch token tracked |
| No secrets / host paths in public artifacts | **PASS** | Repo hygiene + .gitignore doctrine |

Update this table only when CI proves a change. No soft-green.
