# Release gate (public control plane)

Do not publish a revision until every item is true. Private companion, Ollama, living dumps, and local audit reports are **out of scope**.

1. External characterization fixture (operator machine, outside this repo) has been run for `/F` vs `/T` and identity predicates, or the Windows CI job `tests/test_lh_process_windows.py` has passed.
2. Private operator-tree tests pass (`tests/test_lh_process_identity.py` and, on Windows, `tests/test_lh_process_windows.py`).
3. Public export tests pass **from this tree alone**: `python -m pytest tests/test_lh_process_identity.py -q`.
4. Sanitized demo: `python -u scripts/demo_local_smoke.py` from a clean clone.
5. `python -m compileall -q scripts living tests`.
6. Windows launcher/smoke: `scripts/launch_long_horizon.ps1` and `scripts/launch_lh_watchdog.ps1` present; Windows CI job green.
7. Documentation matches observed stop/watchdog contract (README, SETUP, OPERATIONS, HIGH_LEVEL_DESCRIPTION, CHANGELOG).
8. Scan: no operator home-directory absolute paths, no runtime JSONL/SQLite, no credentials, no private handoff, no companion/STL modules.
9. Diff review: no accidental private-runtime leakage.
10. Tag a small release whose changelog is process-control correctness.

Stop success means: no allowlisted supervisor, watchdog, or probe command lines remain; `plant_control.py stop` exit 0. Exit 1 means survivors were reported.
