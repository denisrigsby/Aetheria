# Architecture (research)

This folder is the **versioned capability contract**. It does not start processes.

| File | Role |
|------|------|
| [aetheria-capability-contract.md](aetheria-capability-contract.md) | What Aetheria is intended to become |
| [capability-matrix.json](capability-matrix.json) | Machine-readable maturity |
| [capability-matrix.md](capability-matrix.md) | Human table |
| [reference-task-portfolio.json](reference-task-portfolio.json) | Missions mapped to capabilities and benchmark tasks |
| [reference-task-portfolio.md](reference-task-portfolio.md) | Human summary |
| [research-production-boundary.md](research-production-boundary.md) | Three boundaries |
| [promotion-gates.md](promotion-gates.md) | Stage transitions |
| [vertical-slice-01.md](vertical-slice-01.md) | Spec only — not implemented |
| [RESEARCH_INTAKE.md](RESEARCH_INTAKE.md) | Template for future proposals |

Stable control plane remains `scripts/` (identity, stop, aetheria.py). Research remains `research/`. Production plant is out of this repository's automatic authority.

Every future change must name: capability id, boundary, and whether it needs model calls or external access (default **no**).
