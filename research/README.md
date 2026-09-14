# Research directory contract

Isolated from the stable control plane. Experiments **must not** start the production plant or write outside their run root.

```text
research/
  README.md                 this contract
  schemas/                  JSON schemas (genome, candidate, lineage, result)
  ecologies/                fixed baseline genomes (Phase 2)
  benchmarks/               local, credential-free task suite + held-out set
  population.py             bounded spawn / pause / retire
  experiment.py             disposable run root + registry
  evaluate.py               deterministic local scoring (no models required)
  runs/                     created by init; one subdirectory per experiment
```

Rules:

- One experiment = one directory under `runs/`.
- Network disabled by default (`network_access: false` in genome).
- Active workers ≤ `resource_budget.max_active_workers`.
- Depth ≤ `resource_budget.max_depth`.
- Promotion is **manual** (`promotion_status` never auto-set to production).
- Failed candidates are kept (JSON under the run dir).
- Cleanup: stop workers, record survivors, leave artifacts.
