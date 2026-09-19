# Runtime contract v1

Aetheria’s **public** product is a versioned process-continuity layer. Compatibility is promised at this protocol, not at an unpublished agent.

The **private** install (mouth, living, GPU plant, credentials) is an extension of this contract, not a missing GitHub file. Chat is a mirror of the ledger. It is not a parent of the runtime. If the chat window is closed, the worker still ticks.

This document names the protocol **this tree already runs**. It does not invent a second clock or a dummy `--cycle-id` CLI.

## Why some of it stays private

| Private | Why |
|---------|-----|
| Living jsonl / session traces | User-specific memory. Merge and concat forbidden. |
| Mouth / Forge / Ollama | Operator-facing chair on one PC. Not the supervisor. |
| Cycle body / probe internals | Security-sensitive runtime + unpublished research. |
| Credentials, host paths, `/link` folders | Deployment-specific. Never in the public repo. |

Public GitHub stays evaluable as **infrastructure**: start, heartbeat, checkpoint, STOP, recover, identity-checked kill.

## Working directory and env

- Root: directory that contains `scripts/` and `measurements/`.
- State: `measurements/` only (see [STATE_MODEL.md](STATE_MODEL.md)).
- Config: `measurements/*.json` plus `AETHERIA_*` env. No cloud keys required for the control plane.
- Model backend for this contract: **none**.

## Lifecycle

```text
Runtime protocol v1
- Operator launches via python -u scripts/aetheria.py start|resume|recover
  (or Camp A dispatcher on a full install).
- Supervisor writes measurements/long_horizon_state.json (tmp+replace).
  Heartbeat field: heartbeat_at. Success: last_ok, last_tick_finished, tick.
- Probe completion: measurements/lh_probe_summary_latest.json (lh_probe_summary_v1).
- STOP: presence of measurements/long_horizon_STOP and watchdog_STOP.
- Standby: measurements/long_horizon_STANDBY.json.
- Manual-start latch: measurements/long_horizon_MANUAL_START.json.
- Identity: alive = PID exists AND cmdline is the claimed role. PID file alone is not truth.
- Watchdog: HOLD after dirty last_ok. Green interruption may ensure_dispatcher.
  No AUTORUN after dirty death.
- recover loads measurements/campaign_snapshot_v1.json only when the supervisor is identity-dead.
  Schema/hash fail → exit 1, no spawn. recover is not start.
```

## Exit meanings (operator commands)

| Exit | Meaning |
|------|---------|
| 0 | Command completed (stop with no allowlisted survivors; status ok) |
| 1 | Stop left survivors, recover refused a bad snapshot, or diagnose failed closed |
| 2 | Usage / missing root |

Probe/worker exit between ticks is **normal**. Do not treat worker death as a second plant to start.

## Reference runtime (public)

Clones do not need the private cycle body:

```text
python -m aetheria demo --cycles 3
python -u scripts/demo_local_smoke.py
```

The supervisor (real) drives a **mock** workload: sleep, print, ledger files, `lh_probe_summary_v1`. That is heartbeat + checkpoint + STOP without Ollama, living, or secrets.

## Chat is not in this contract

The mouth may observe status and never start the dispatcher. `parents_lh=false`. Talk must not be required for a tick to complete.

## Compatibility

Pin to this document + `lh_probe_summary_v1` + [STATE_MODEL.md](STATE_MODEL.md). Private agent changes do not break the control plane so long as those schemas hold.
