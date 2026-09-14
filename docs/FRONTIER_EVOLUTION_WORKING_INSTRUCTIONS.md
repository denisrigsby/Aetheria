# Aetheria Frontier Evolution Working Instructions

## Mission

Aetheria is evolving from a validated local process-control product into a controlled research platform for **holonic, elastic, self-evaluating agent populations**.

The goal is not to create an uncontrolled swarm or permit unrestricted self-modification. The goal is to discover whether a population of specialized, coordinated agents can improve planning, research, testing, memory, and execution while remaining:

- bounded;
- observable;
- reproducible;
- recoverable;
- resource-aware;
- externally evaluable;
- safe to stop;
- independent of the production plant.

The central research question is:

> Can Aetheria evolve better agent organizations, strategies, and memory policies while preserving a stable and accountable control plane?

## Current baseline

The current process-control baseline has passed:

- clean isolated start;
- verified supervisor, watchdog, and probe identities;
- status and heartbeat checks;
- bounded execution;
- graceful stop;
- descendant cleanup;
- survivor checks;
- watchdog stop;
- resume and restart;
- recovery from stopped state;
- stale PID cleanup;
- diagnosis;
- constrained post-stop absence checks;
- arbitrary-path clean-clone validation of the standalone launcher.

The production plant must remain untouched during research.

The stable baseline is a foundation, not an experimental target. New research components must run in separate disposable roots and must not weaken the existing lifecycle contract.

## Core architectural principle

Aetheria consists of three layers:

```text
Stable Runtime
    lifecycle, identity, state, recovery, resource limits

Agent Ecology
    holons, workers, roles, memory, tools, coordination

Evolution Laboratory
    candidate generation, mutation, evaluation, selection, lineage
```

The stable runtime is the accountability boundary.

The agent ecology may evolve within explicit contracts.

The evolution laboratory creates and evaluates candidates in disposable environments.

No candidate may directly rewrite or replace the stable runtime.

## Definitions

### Agent

A bounded unit that performs a defined task and returns a structured result.

### Holon

An agent that can operate independently for a bounded objective while also acting as a component within a larger agent organization.

### Agent ecology

A population of agents, holons, coordinators, critics, tools, memories, and communication relationships used to solve an objective.

### Genome

A structured description of an agent ecology:

```text
AgentEcologyGenome:
    roles
    role_prompts
    model_assignments
    communication_topology
    routing_policy
    memory_policy
    tool_policy
    spawn_policy
    stopping_policy
    resource_budget
```

### Candidate

A version of an ecology or strategy evaluated in a disposable run.

### Generation

A set of candidates produced from one or more parent candidates and evaluated against the same benchmark conditions.

### Promotion

The controlled transfer of a candidate from research status into a later test stage. Promotion is never automatic into production.

## Non-negotiable boundaries

The following rules apply to every future task:

1. Never start or stop the real production plant without explicit approval.
2. Do not modify the frozen production/operator tree unless a task explicitly authorizes a specific remediation.
3. Do not use production credentials, private memory, living session stores, SQLite databases, or unrelated roots in research experiments.
4. Do not connect research candidates to external APIs unless explicitly authorized for a named experiment.
5. Default all experiments to local-only, credential-free, bounded operation.
6. Do not allow candidates to modify their own evaluation criteria.
7. Do not let candidates directly modify the stable runtime.
8. Do not allow unrestricted recursive spawning.
9. Every worker must have an identity, parent, deadline, resource budget, and cancellation path.
10. Every experiment must be stoppable and recoverable.
11. Preserve failed candidates, logs, scores, and state for analysis.
12. Never discard evidence merely because a later candidate performs better.
13. Use separate disposable roots for separate experiments.
14. Do not claim an experiment passed without recorded evidence.
15. Prefer a partial, reproducible experiment over an ambitious but unverifiable system.

## Operating model

The default system should use:

- one stable orchestrator;
- bounded worker concurrency;
- logical agents represented as jobs;
- short-lived workers;
- explicit parent-child relationships;
- structured messages;
- isolated experiment directories;
- independent evaluation;
- manual promotion.

“Hundreds of agents” should initially mean hundreds of possible logical candidates or tasks, not hundreds of continuously running model processes.

A reasonable initial configuration is:

```text
logical population capacity: configurable
active worker limit: bounded
model-call limit: separately bounded
task depth: bounded
task lifetime: bounded
experiment lifetime: bounded
network access: disabled by default
promotion: manual
```

The actual values must be measured on the target Windows machine rather than assumed.

## Evolution targets

Initial evolution should focus on:

- task decomposition;
- role selection;
- population size;
- agent specialization;
- communication topology;
- critic placement;
- routing policy;
- memory retrieval and summarization;
- tool selection;
- model assignment;
- stopping criteria;
- retry and escalation behavior.

Do not begin with unrestricted self-rewriting or model-weight modification.

The first useful question is:

> When should Aetheria use one agent, a small team, a hierarchy, or a dynamically generated population?

## Research phases

### Phase 1: Research substrate

Build the experimental foundation:

- experiment registry;
- candidate registry;
- task queue;
- worker lifecycle;
- heartbeat;
- cancellation;
- resource accounting;
- disposable run management;
- structured result format;
- lineage recording;
- benchmark runner;
- cleanup and recovery.

Exit condition:

> A failed experiment can be stopped, inspected, cleaned up, and reproduced without affecting the stable runtime.

### Phase 2: Fixed agent ecologies

Implement several manually defined baselines:

```text
single generalist
planner + executor
planner + executor + critic
parallel specialists + synthesizer
hierarchical coordinator + workers
```

Measure quality, latency, cost, duplication, reliability, and recovery.

Exit condition:

> The system can compare agent organizations under identical benchmark conditions.

### Phase 3: Elastic population control

Add a population controller that can:

- spawn workers;
- pause spawning;
- retire workers;
- merge redundant roles;
- escalate uncertainty;
- add critics;
- stop when additional work has diminishing value.

Exit condition:

> The system can select an appropriate population for a task and beat or match fixed baselines without exceeding resource limits.

### Phase 4: Topology evolution

Allow candidates to mutate:

- roles;
- edges;
- hierarchy;
- routing;
- critic placement;
- parallelism;
- specialization boundaries.

Every topology must remain bounded and inspectable.

Exit condition:

> An evolved topology improves held-out benchmark performance without degrading lifecycle, reliability, or recovery.

### Phase 5: Strategy and memory evolution

Allow candidates to evolve:

- planning prompts;
- role instructions;
- memory retention;
- retrieval;
- summarization;
- tool-selection policies;
- disagreement resolution.

Exit condition:

> Improvements generalize across tasks rather than only optimizing a visible benchmark.

### Phase 6: Controlled code evolution

Only after the previous phases are reliable may candidates propose changes to noncritical research modules.

Every candidate must pass:

- syntax and compile checks;
- unit tests;
- integration tests;
- lifecycle tests;
- resource-limit tests;
- clean shutdown;
- recovery;
- arbitrary-path execution;
- regression comparison;
- absence and survivor checks.

Code evolution remains sandboxed and requires human review before promotion.

## Evaluation model

Every candidate must be evaluated against:

- task quality;
- reliability;
- repeatability;
- latency;
- compute usage;
- memory usage;
- coordination overhead;
- duplication;
- recovery behavior;
- shutdown behavior;
- unauthorized behavior;
- generalization to held-out tasks.

A candidate score may be represented as:

S = w_q Q + w_r R + w_g G + w_n N - w_c C - w_l L - w_d D - w_f F

Where:

- Q = quality;
- R = reliability;
- G = generalization;
- N = useful novelty;
- C = resource cost;
- L = latency;
- D = duplication and coordination noise;
- F = failure or policy violations.

Hard rejection conditions override the score. Reject any candidate that:

- cannot stop cleanly;
- loses state consistency;
- escapes its assigned root;
- exceeds its resource budget;
- spawns without authorization;
- bypasses identity checks;
- accesses unauthorized tools;
- manipulates the evaluator;
- changes the benchmark without approval;
- produces unrecoverable state;
- degrades the stable baseline.

## Candidate lineage

Every candidate must have a durable record:

```text
candidate_id
parent_ids
generation
creation_time
genome
task_set
resource_limits
results
scores
failures
regressions
artifacts
promotion_status
```

Candidates should be retained as a population or archive, not reduced to one “latest” version. A strong candidate may be useful for one task while another candidate is better for a different class of work.

## Benchmark requirements

The initial benchmark should be local, deterministic where possible, and free of credentials.

It should include:

- document analysis;
- structured synthesis;
- contradiction detection;
- local code planning;
- code modification in a disposable fixture;
- test generation;
- multi-step planning;
- recovery after interruption;
- resource-budget compliance;
- clean shutdown.

The benchmark must contain hidden or held-out tasks. Otherwise the evolutionary system may optimize for the visible evaluation rather than genuine capability.

## Windows execution requirements

The system must be designed for a Windows PC:

- use explicit process identities;
- avoid broad process enumeration;
- keep role-specific PID records;
- verify identity before termination;
- use bounded worker pools;
- isolate experiment roots;
- avoid dependence on the current working directory;
- record absolute paths only inside private evidence;
- provide deterministic cleanup;
- test arbitrary-path execution;
- distinguish observer shells from managed roles;
- treat stale PID files according to verified identity, not filename presence.

The research system must not assume Linux-only process semantics.

## Handoff protocol

Every completed task must report:

```text
Task:
Date:
Repository commit:
Branch:
Working root:
Authorization scope:

Changes made:
Files added:
Files modified:
Files not modified:

Tests run:
Test results:
Warnings:
Known failures:

Processes started:
Processes verified:
Processes stopped:
Survivors:
State artifacts:
Logs:
Cleanup result:

Production plant started: yes/no
Production tree modified: yes/no
External access used: yes/no
Credentials used: yes/no

Next approved action:
Explicitly deferred actions:
```

Private paths, credentials, session contents, and sensitive artifacts must not enter public handoff documents.

## Definition of done for the first evolutionary milestone

The first milestone is complete only when Aetheria can:

1. run a single-agent baseline;
2. run at least two multi-agent baselines;
3. vary population size;
4. record structured lineage;
5. compare candidates under the same benchmark;
6. stop all workers cleanly;
7. recover from interruption;
8. prove no managed survivors remain;
9. preserve failed candidates;
10. demonstrate one improvement on held-out work;
11. remain isolated from the production plant;
12. produce a sanitized handoff report.

## Immediate work order

Continue in this order:

1. Complete arbitrary-path installation and dependency locking.
2. Add failure-recovery coverage.
3. Define support, rollback, and backup policy.
4. Create the sanitized frontier-evolution document.
5. Create the research directory contract.
6. Define the first benchmark suite.
7. Implement the candidate and lineage schemas.
8. Build fixed ecology baselines.
9. Add bounded population control.
10. Begin topology evolution only after baseline comparison works.

Do not add companion, cloud, market, memory synchronization, or broad capability expansion before the standalone research substrate is reproducible and recoverable.

## Guiding principle

Aetheria should be ambitious in its research scope and conservative in its control plane.

The target is not an uncontrolled autonomous system. The target is:

> A stable local substrate that can generate, test, compare, and evolve many bounded holons while preserving evidence, recoverability, and human authority over promotion.

This creates a credible path from process-control software to a frontier research platform without confusing experimentation with production readiness.
