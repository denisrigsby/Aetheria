# Control-plane checklist (not a readiness claim)

This page is a checklist of control-plane work. It is **Locked** as a production-ready, enterprise, enterprise-grade, or revolutionary claim. The assurance table is not all PASS. [RELEASE_GATE_ASSURANCE.md](RELEASE_GATE_ASSURANCE.md).

Standalone product means the process control plane ([STANDALONE_PRODUCT.md](STANDALONE_PRODUCT.md)). Companion, Ollama, cloud, and living memory stay out of this tree. P1–P5 are internal certification on the operator plant, not external accreditation.

`soft_ACCEPT` stays false. No soft-green.

## Checklist (desired, not a pass list)

1. Product boundary documented and public README matches it.
2. Lifecycle tests: already-dead stop, isolated supervisor tree-kill, repeated stop, identity mismatch. Tree-kill in this list is Windows-only.
3. State model: authority table, stale PID reconciliation, no PID-file-only "alive".
4. Memory: public product does not expose split living/overlay/sqlite.
5. Capabilities: control plane has no network/paid API/shell-from-chat. Probe bodies in a full install are separate.
6. Clean clone from an arbitrary path; no operator-home hardcoding.
7. One launcher: `scripts/aetheria.py`.
8. Observability: plant_control prints identities, survivors, exit 0/1; watchdog reason codes.
9. Failure tests: Ubuntu CI runs the workflow files that are not Windows-only. Tree-kill fixtures run on the Windows job. That split is not a portable stop.
10. Support: this checklist, RELEASE_GATE.md, backup of `measurements/` JSON (not living dumps).

## What the index can say

| Item | Label | Evidence and exclusion |
|------|--------|------------------------|
| Public v0.3.2 tag exists | **Real** | Tag named in [SUPPORT.md](SUPPORT.md) as the last process-control-only rollback point. The tag is not a current assurance PASS |
| Windows CI runs `tests/test_lh_process_windows.py` | **Real on Windows** | Windows job in `.github/workflows/ci.yml`. Isolated fixtures, including already-dead stop and a tree-kill case. **Locked on non-Windows** (the Ubuntu job does not run this file). This is not `gate_job_object_kill_path_v1` and not a live operator-plant tree-kill |
| Live validation #1, "12 passed", disposable root `standalone-lifecycle`, clean-clone install for v0.3.2 | **Pending** | Narrative only. No indexed receipt, and the Windows test file does not contain 12 tests |
| Full start/stop/restart of the operator production plant | **Locked** | Not run, by design. Public export stays **PRIVATE_AHEAD** |
| Memory authority for living/overlay/sqlite | **Locked** | Public product is operational JSON only |
| Capability hardening (STL/web/xAI) | **Locked** | Out of standalone scope |

## Rollback

Checkout a previous tag (for example v0.3.2) or a previous main SHA. `measurements/` JSON is the state; restore from backup copies if needed. PID files are caches. Publish sync still needs an explicit Denis GO. This page does not grant that GO.
