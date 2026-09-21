# Control-plane readiness checklist (evidence index)

Standalone product = process control plane ([STANDALONE_PRODUCT.md](STANDALONE_PRODUCT.md)). Companion, Ollama, cloud, and living memory are **out of scope** until this list is green.

## Gates

1. Product boundary documented and public README matches it.
2. Lifecycle tests: already-dead stop (live validation #1), **live supervisor tree-kill** (isolated fixture / Windows CI), repeated stop, identity mismatch.
3. State model: authority table, stale PID reconciliation, no PID-file-only “alive”.
4. Memory: public product does **not** expose split living/overlay/sqlite.
5. Capabilities: control plane has no network/paid API/shell-from-chat. Probe bodies in a full install are separate.
6. Clean clone from an arbitrary path; no operator-home hardcoding.
7. One launcher: `scripts/aetheria.py`.
8. Observability: plant_control prints identities, survivors, exit 0/1; watchdog reason codes.
9. Failure tests: portable + Windows process tests in CI.
10. Support: this checklist, RELEASE_GATE.md, backup of `measurements/` JSON (not living dumps).

## Evidence so far

| Item | Status |
|------|--------|
| Public v0.3.2 | Tagged; CI Ubuntu+Windows on merge |
| Live validation #1 | Already-dead stop **passed** (not a live tree-kill) |
| Isolated live-parent tree-kill | Windows tests (12 passed) |
| Isolated standalone lifecycle | Disposable root `standalone-lifecycle`: start, heartbeat, stop, resume, restart, recover-from-stopped, stale PID unlink, Pass F empty. Production plant not used. |
| Clean-clone install | Passed for v0.3.2 |
| Full start/stop/restart of the operator production plant | **Not run** (by design) |
| Memory authority | Deferred; public product is operational JSON only |
| Capability hardening (STL/web/xAI) | Out of standalone scope |

## Rollback

Checkout previous tag (e.g. v0.3.0). `measurements/` JSON is the state; restore from backup copies if needed. PID files are caches.
