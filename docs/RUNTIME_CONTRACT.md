# Runtime contract v1

Aetheria’s **public** product is a versioned process-continuity layer. Compatibility is described at this protocol, not at an unpublished agent. This page is the contract text. A behavior line is **Real** or **Proved** only when [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md) cites a test or a gate for that line.

The **private** install (mouth, living, GPU plant, credentials) is an extension of this contract, not a missing GitHub file. Chat is a mirror of the ledger. It is not a parent of the runtime. Mouth-closed continuity in this repo is the mock continuity demo, plus `gate_endurance_v1` (30 minutes). Longer than that window is locked.

This document names the protocol the scripts implement. It does not invent a second clock or a dummy `--cycle-id` CLI. It is not a production-ready claim.

## Why some of it stays private

| Private | Why |
|---------|-----|
| Living jsonl / session traces | User-specific memory. Merge and concat forbidden. |
| Mouth / Forge / Ollama | Operator-facing chair on one PC. Not the supervisor. |
| Cycle body / probe internals | Security-sensitive runtime + unpublished research. |
| Credentials, host paths, `/link` folders | Deployment-specific. Never in the public repo. |

From this tree you can read the scripts and run the CI tests named in the [README](../README.md): start, heartbeat, checkpoint, and STOP files are in the tree. Identity-checked kill on the operator plant is the Windows Job Object receipt and the create_time refuse receipts. **Proved on Windows** for that Job Object wording. **Locked on non-Windows**. Those receipts do not make the CI Job Object row PASS, and they are not a portable relaunch.

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
- Identity (public tests): role/junk PID refusal, and Windows tasklist liveness on the PID column. PID file alone is not truth. Unrelated-process survival stays **PARTIAL**. OS PID-number reuse was not observed.
- Watchdog intent: HOLD after dirty last_ok, and no AUTORUN after dirty death. Clean stop ≠ crash and full HOLD wiring stay **PARTIAL**.
- recover loads measurements/campaign_snapshot_v1.json only when the supervisor is identity-dead.
  Schema/hash fail → exit 1, no spawn. recover is not start.
```

## Exit meanings (operator commands)

| Exit | Meaning |
|------|---------|
| 0 | Command completed. On Windows, stop means no allowlisted survivors. That survivor list is not a non-Windows tree-kill |
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
