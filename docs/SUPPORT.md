# Support, rollback, and backup

## Support scope

This repository supports the **process control plane** and the **research substrate** under `research/`. Companion, cloud, market adapters, and living-memory stores are out of scope.

Report issues with: Python version, OS, `python -u scripts/aetheria.py diagnose` output (no secrets), and the failing test name.

## Backup

Authoritative operational state is `measurements/*.json` plus STOP files (see [STATE_MODEL.md](STATE_MODEL.md)).

Copy that directory to a backup folder. PID files are caches; they may be omitted. Do not back up `research/runs/` as production state — those are disposable experiment artifacts you may archive separately.

## Restore

1. Stop: `python -u scripts/aetheria.py stop --reason restore`
2. Replace `measurements/` JSON from backup.
3. Remove stale `*.pid` if identity would not verify.
4. `python -u scripts/aetheria.py status`

## Rollback

```text
git fetch origin
git checkout v0.3.2    # last process-control-only tag
# or
git checkout <previous-main-sha>
```

Research modules under `research/` are not part of v0.3.2. Checking out that tag removes them; that is expected.

## Failed experiment

Keep the run directory under `research/runs/<id>/`. Do not delete because a later candidate scored higher. Stop workers with the run’s cancel file; then delete the run only after archiving lineage JSON.
