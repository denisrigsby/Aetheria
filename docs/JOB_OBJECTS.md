# Windows Job Objects (stop containment)

## Why

PID ancestry reconstruction is unsafe. Prefer assigning the worker tree to a **Job Object** and terminating the job after identity checks pass.

## Public status

| Piece | Status |
|-------|--------|
| `scripts/job_object_win.py` Create/Assign/Terminate helpers | **Untested** on CI Linux; available on Windows |
| Wired into every plant stop path | **PARTIAL** — helper shipped; full plant stop migration is follow-up |
| Identity mismatch still refuses kill | **Tests** via `process_identity_bind.refuse_action_on_mismatch` |

Until Job Objects are wired into production stop and CI-proven on Windows, do **not** claim Job Object containment as PASS on the release gate.
