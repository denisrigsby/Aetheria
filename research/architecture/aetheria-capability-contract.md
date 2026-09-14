# Aetheria capability contract (v1)

Aetheria is a **governed general-purpose agent system** that can accept varied user goals, decide whether and how it can help, execute **bounded** plans using **authorized** capabilities, verify important results, recover from failures, and **refuse or escalate** work outside its envelope.

It is **not** an uncontrolled swarm, a chat UI, a cloud agent, or a self-modifying production runtime.

## Layers

1. Stable runtime (control plane): identity, stop, state, recovery, limits.
2. Agent ecology (research): holons, roles, tools, coordination — inside contracts.
3. Evolution laboratory: candidates in disposable roots. **No candidate rewrites the runtime.**

## Capabilities

See [capability-matrix.json](capability-matrix.json) for purpose, I/O, evidence, tools, limits, failure/recovery, approval, and eligibility (`research-only` | `sandbox-eligible` | `controlled-use-eligible` | `production-eligible`).

Current eligibility: **research-only** or **sandbox-eligible** only. None are production-eligible.

## Prohibited automatic behavior

- Irreversible external actions without approval
- Private systems without explicit authorization
- Production modification by research code
- Permission expansion
- Unrestricted recursive delegation
- Treating generated code or plans as trusted
- Unbounded memory retention
- Self-modification of live models or production policies

## Resource defaults

From `research/config/windows-local.json`: max_active_workers 8, max_model_calls **0**, max_task_depth 4, experiment lifetime 120s.

## Versioning

This contract is v1. Changes require a documentation PR and must not silently raise model-call or network defaults.
