# Research / control plane / production boundary

Every future feature must be classified into **exactly one** boundary before implementation.

## 1. Research substrate (`research/`)

- Local, disposable, credential-free.
- No production files, no private memory, no living jsonl/sqlite.
- No external services unless a named experiment is explicitly approved.
- `max_model_calls` default **0** (`research/config/windows-local.json`).
- Candidates cannot rewrite the evaluator, suite, held-out list, or promotion status.
- Failed candidates are retained.

## 2. Stable control plane (`scripts/`)

Accountability boundary: identity, resource and permission enforcement, cancellation, cleanup, lineage recording, promotion and rollback **control** (not automatic promotion).

Research code must not replace or rewrite this layer.

## 3. Production plant

- Not modified by this documentation task.
- Receives only manually reviewed and separately certified changes.
- Must never inherit research authority automatically.
- Starting or stopping it requires explicit operator approval.

## Forbidden automatic crossings

- Research writing production state.
- Promotion_status `production` set by a candidate.
- Expanding `network_access` or model-call budget from a genome.
- Unrestricted recursive delegation.
