# Vertical slice 01 — disposable fixture edit (specification only)

**Not implemented.** Do not connect to production files, credentials, live data, external APIs, or topology mutation.

## Mission

Inspect a **disposable** fixture repository, apply a requested small change, generate or update tests, run the tests, report what changed, name remaining uncertainty, preserve artifacts, shut down.

Flow:

User request → classify → clarify or accept bounded → declarative plan → bounded execution → independent verification → evidence-backed result → artifact retention → safe shutdown

## Input contract

- `goal`: short instruction (e.g. rename a constant in one fixture file).
- `fixture`: in-memory or temp directory created for the run; never the production tree.
- `budget`: from `windows-local.json` (max_active_workers ≤ 8, max_model_calls = 0, max_depth ≤ 4).

## Output contract

JSON: `plan`, `diff`, `test_report`, `uncertainty`, `artifacts[]`, `shutdown: clean`.

## Filesystem

Allowed: the run’s fixture directory only. Forbidden: production plant, operator home, credentials, `living/`, private jsonl.

## Workers and cancellation

Logical workers only unless a later approved experiment says otherwise. Cancel on deadline or STOP. Interruption points: after plan, after edit, after tests. Incomplete work marked; do not silently retry completed steps.

## Verification

Independent of the executor: tests must actually run (`test_then_run` semantics). Generated tests are untrusted until executed.

## Evidence

Retain under `research/runs/<id>/`. Failed runs kept.

## Human approval

Required before any path outside the fixture, any network, any credential, any production file. Default: **deny**.

## Out of scope

Model calls, cloud, companion, market, topology mutation, live plant, private memory.

## Capabilities touched

`goal_interpretation`, `clarification`, `bounded_planning`, `code_fixture`, `test_generation_execution`, `evidence_reporting`, `uncertainty_communication`, `failure_recovery`, `safe_refusal_escalation`.
