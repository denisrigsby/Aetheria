# Operational state model

Public standalone product uses **`measurements/` only**. Living jsonl, sqlite, session logs, and fractal indexes are private/deferred and are **not** a production guarantee.

All timestamps in these files are UTC.

## Authority table

| Fact | Authoritative file | Notes |
|------|--------------------|--------|
| Plant running | Process identity (`long_horizon_supervisor.py` cmdline), **not** the PID file alone | `plant_control` `alive` = PID exists **and** verified role |
| Supervisor PID | Live process table; cache `measurements/long_horizon.pid` | Unlinked after verified stop if not a live supervisor |
| Watchdog PID | Live process table; cache `measurements/watchdog.pid` | Same reconciliation |
| Probe PID | `long_horizon_state.json` `probe_pid` while a tick runs | Cleared on stop; kill only if identity is probe |
| Manual-start latch | `measurements/long_horizon_MANUAL_START.json` | `active` + `reason` + `schema` |
| Standby | `measurements/long_horizon_STANDBY.json` | Absent or `active:false` means not standby |
| Stop request | `long_horizon_STOP` and `watchdog_STOP` (plain text) | Presence is the request |
| Heartbeat | `long_horizon_state.json` `heartbeat_at` | Watchdog reads this |
| Last successful tick | `long_horizon_state.json` `last_ok`, `last_tick_finished`, `tick` | Campaign vs segment: tick may reset on new PID |
| Recovery / exit | `long_horizon_state.json` `status`, `exit_reason` | e.g. `stopped_by_file`, `tick_job_done` |

Schema field: JSON files should include `"schema": "aetheria_*_v1"` where they already do (standby, manual_start, watchdog_status). New writers must set `schema`.

## Writes

- JSON control files: `scripts/atomic_state.py` `atomic_write_json` (same-directory temp, flush, fsync, replace). `plant_control.write_json` calls that helper.
- PID files: short `write_text`; **reconcile** (unlink) after a verified stop when the PID is not a live matching role.
- STOP files: overwrite in place (idempotent).

## Stale PID policy

Retain `*.pid` while a **verified** process of that role is alive (diagnosis + tools that read the file).

After `stop` exit 0 (no allowlisted survivors), unlink `long_horizon.pid` and `watchdog.pid` if the recorded number is not a verified live supervisor/watchdog. Live validation #1 left a stale `watchdog.pid` because that policy was not yet applied; that file was harmless (`alive=False`, `identity=False`).

## Not in this model

Compaction or deletion of living/session stores from a query path. Public product does not compact “memory.”


## Transition table

Executable transitions: [STATE_TRANSITIONS.md](STATE_TRANSITIONS.md).
