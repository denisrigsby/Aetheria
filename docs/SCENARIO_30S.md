# 30-second scenario (public)

## Picture (not a receipt)

1. Start a multi-hour research-style job under the supervisor.
2. Close the UI (Talk-face / mouth). The plant clock keeps its own schedule.
3. Kill the worker mid-cycle.
4. Heartbeat goes stale; status is supposed to move toward **HOLD**; no blind auto-resume after a dirty death.
5. Recovery is supposed to check process role and snapshot hash.

Steps 3–5 are the picture. Clean stop ≠ crash and full HOLD wiring stay **PARTIAL**. Endurance past 30 minutes is **Locked**.

## What this public repo can show

| Step | Label | Evidence |
|------|--------|----------|
| UI closed, mock pulse continues | **Real** | `python -u scripts/demo_continuity.py`. CI does not run it |
| Mouth closed, tick advanced, 30 minutes, on the operator plant | **Proved** | `gate_endurance_v1`. This clone does not re-run it |
| Role / junk PID refusal; Windows tasklist PID column | **Real** | CI: `tests/test_lh_process_identity.py`, `tests/test_pid_liveness_exact.py` |
| STOP / stale heartbeat / bad snapshot / dirty last_ok policy | **Real** / **Untested** | `tests/test_fault_injection_public.py`. CI on main does not run this file |

The private operator plant (Forge + living memory + real cycle body) is not in this tree. Public demos use the supervisor control plane in this repo with a mock / reference worker where noted.
