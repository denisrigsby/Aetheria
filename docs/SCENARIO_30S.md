# 30-second scenario (public)

## What to picture

1. Start a multi-hour research-style job under the supervisor.
2. Close the UI (Talk-face / mouth). The plant clock keeps its own schedule.
3. Kill the worker mid-cycle.
4. Observe: heartbeat goes stale; status moves toward **HOLD** (fail-closed); no blind auto-resume after a dirty death.
5. Recovery is identity-checked (correct process role / snapshot hash) — not “restart whatever PID looks free.”

## What this public repo can prove today

| Step | Public artifact |
|------|-----------------|
| UI closed, pulse continues | `python -u scripts/demo_continuity.py` |
| Role / PID identity checks | `tests/test_lh_process_identity.py`, `tests/test_fault_injection_public.py` |
| STOP / stale heartbeat / bad snapshot | `tests/test_fault_injection_public.py` |

The private operator plant (Forge + living memory + real cycle body) is **not** shipped. Public demos use a **real supervisor control plane** with a **mock / reference worker** where noted.
