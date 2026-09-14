# Aetheria — high-level description

**Local multi-cycle agent runtime** with process supervision and on-disk persistence.

Scheduled work runs as a detached supervisor with status files and a watchdog — not as a long-lived interactive chat session.

This repository publishes the **control plane**: supervisor, watchdog, measured entry path, continuity audit, optional change-control gate, and documentation.

Private deployment state — living memory, asset registries, host configuration — remains on the operator machine.

## One sentence

Process supervision for long-horizon local AI work: start a loop, persist progress, recover from crashes, treat process restarts as normal segments, and make **stop** mean identity-checked termination of the supervisor tree, recorded probe, and watchdog — with survivors reported. Private runtime (companion, living dumps, model adapters) is **not** in this repository.

## Keywords

local agent runtime · supervised LLM agent · persistent AI loop · watchdog process supervision · long-horizon agents · rolling process segments
