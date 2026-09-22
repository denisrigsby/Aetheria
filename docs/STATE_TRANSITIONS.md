# State transitions (public control plane)

Executable companion to [STATE_MODEL.md](STATE_MODEL.md). Authority remains on-disk under `measurements/` (see that doc).

This is the intended model. Corrupted / unknown-version → HOLD and clean stop ≠ crash stay **PARTIAL** on [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md). The diagram does not flip those rows.

## States

| State | Meaning |
|-------|---------|
| `IDLE` | No verified supervisor loop |
| `RUNNING` | Supervisor alive; ticks may be in flight |
| `CHECKPOINTED` | Last successful tick recorded; heartbeat fresh |
| `STALE` | Heartbeat older than policy window |
| `HOLD` | Fail-closed pause after dirty death / unsafe condition; needs operator |
| `STOPPING` | STOP file present. Tree termination is the Windows tree-kill / Job Object path. **Locked on non-Windows** |
| `STOPPED` | Verified stop; PID caches reconciled |

## Valid transitions

```text
IDLE ──start──► RUNNING ──tick ok──► CHECKPOINTED ──► RUNNING
RUNNING ──heartbeat timeout──► STALE
STALE ──dirty death / unsafe──► HOLD
RUNNING ──STOP──► STOPPING ──► STOPPED ──► IDLE
HOLD ──operator recover (identity + hash ok)──► RUNNING
HOLD ──operator abort──► STOPPED
```

Invalid / refused (public policy):

- `HOLD → RUNNING` without identity-checked recover
- Auto-resume after dirty `last_ok` (no AUTORUN)
- Kill-by-PID-alone when role identity does not match

## Expected files (public)

| Event | Files |
|-------|--------|
| Running | `measurements/long_horizon.pid`, `long_horizon_state.json` (`heartbeat_at`) |
| STOP | `long_horizon_STOP` (and/or `watchdog_STOP`) |
| HOLD | `long_horizon_state.json` status / exit_reason reflecting hold |
| Snapshot | `measurements/campaign_snapshot_v1.json` (hash must match on recover) |

## Invariant checks (tests)

`tests/test_lh_process_identity.py` is in CI. `tests/test_fault_injection_public.py` is a local file. The CI workflow on main does not run it.
