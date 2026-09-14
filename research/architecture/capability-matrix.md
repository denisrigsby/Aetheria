# Capability maturity matrix

Source of truth: [capability-matrix.json](capability-matrix.json).

Stages: specified → local deterministic prototype → sandboxed operational → controlled external use → production candidate → production approved.

**Nothing in this matrix is production candidate or production approved.** A passing unit test does not promote a capability.

| id | maturity | next | owner | eligibility |
|----|----------|------|-------|-------------|
| goal_interpretation | specified | local_deterministic_prototype | research | research-only |
| clarification | local_deterministic_prototype | sandboxed_operational | research | research-only |
| bounded_planning | local_deterministic_prototype | sandboxed_operational | research | research-only |
| research_synthesis | local_deterministic_prototype | sandboxed_operational | research | research-only |
| contradiction_detection | local_deterministic_prototype | sandboxed_operational | research | research-only |
| code_fixture | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| test_generation_execution | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| failure_recovery | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| evidence_reporting | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| uncertainty_communication | local_deterministic_prototype | sandboxed_operational | research | research-only |
| user_approval_gates | specified | local_deterministic_prototype | control_plane | research-only |
| controlled_tool_invocation | specified | local_deterministic_prototype | research | research-only |
| task_state_persistence | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| auditability | local_deterministic_prototype | sandboxed_operational | research | sandbox-eligible |
| safe_refusal_escalation | specified | local_deterministic_prototype | research | research-only |

Default: `max_model_calls=0`, `network=false`.
