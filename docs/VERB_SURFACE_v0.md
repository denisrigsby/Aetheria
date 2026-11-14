# Verb surface v0

The long-horizon supervisor is the only plant clock. `scripts/prime_ctl.py` is a client dispatcher: one shot, no socket, no timer, no second clock. It does not parent the supervisor. A refusal exits **2** before any child process is spawned.

Denied verbs: `start`, `resume`, `init`, `demo`. Denied flags on every verb: `--authorize`, `--reap-orphans`. Unknown verbs and flags that are not in that verb's whitelist are the same refusal. `recover-ack` is not a verb here.

Operator recovery acknowledgement is `python -u scripts/plant_control.py recover-ack`. It is not reachable through `prime_ctl.py`.

| Verb | Child | Allowed flags | Positionals | Effect |
|---|---|---|---|---|
| `status` | `plant_control.py status` | `--json` | none | Read plant, watchdog, standby |
| `status.detailed` | `status_report.py` | `--json` | none | Writes `measurements/status_report_latest.json` |
| `stop` | `plant_control.py stop` | `--reason` | none | Writes the plant's two STOP files and no others: `measurements/long_horizon_STOP`, `measurements/watchdog_STOP`. Child is the existing stop |
| `recover` | `plant_control.py recover` | none | none | Dead plant, valid snapshot. Dirty state needs a recovery ack. Does not add a clock |
| `measure` | `run_probe_bounded.py` | `--cycles` | none | `--cycles` is an integer in `1..2` (`MAX_CYCLES=2`). Omitted cycles use the script default, which is 2 |
| `gate` | `eval_residual_gate_v2.py` | none | none | Evaluates the residual gate. Does not spawn the supervisor |
| `prime.draft` | `prime_continuity.py draft` | none | at most one | Text must not start with `-`. Omit the text to use the existing stdin path |
| `prime.analyze` | `prime_continuity.py analyze` | `--draft-id` | none | Local analysis. No execute |
| `prime.submit` | `prime_continuity.py submit` | `--draft-id` only | none | Commits the draft. `--authorize` is denied |
| `prime.checkpoint` | `prime_continuity.py checkpoint` | none | none | Reload checkpoint from disk |
| `prime.handoff` | `prime_continuity.py handoff` | `--out` | none | Export the handoff package |
| `prime.verify` | `prime_continuity.py verify` | none | none | Verify the local ledger |

Parse: long options and their values are taken first, then positionals. Child argv is emitted in that order. A single-dash token is a positional. `prime.draft` text that starts with `-` is refused.

Dirty recover: `campaign.last_ok is not True`, or `long_horizon_state.json` `last_ok is not True`, or `running_tick is True`. The ack is sha256 of the raw bytes of `measurements/campaign_snapshot_v1.json` (`measurements/recovery_ack_v1.json`). Consume renames that file to `measurements/recovery_ack_v1.consumed.json` only after resume returns 0. A clean plant needs no ack, and the writer refuses to create one.
