# Aetheria — high-level description

A local supervisor for long-running AI work on one Windows PC. The chat window (the mouth, also called Talk-face) is optional. The work schedule (the plant clock) is a separate process plus files on disk. Closing the chat does not stop that schedule. **Plant clock ≠ chat.**

This repository publishes the **control plane**: supervisor, watchdog, stop and recover scripts, and documentation. It is a public export. It is not the live operator plant. Parity decision: **PRIVATE_AHEAD**. [EXPORT_PARITY.md](docs/EXPORT_PARITY.md).

What is real, proved, pending, and locked, with receipts beside the claims: [FINAL_STATE_BRIEF.md](FINAL_STATE_BRIEF.md). P1–P5 are internal certification on the operator plant, not an outside audit.

## One sentence

Keep a local AI job's schedule on disk, under a supervisor, so a closed chat window is not the parent of the clock.

The 30-minute plant receipt (`gate_endurance_v1`) is the indexed window where the mouth was closed and the tick advanced. Longer than that window is locked. Clean stop versus a crash stays pending.

## What it is / is not

| Is | Is not |
|----|--------|
| Detached plant clock + on-disk ledger, on the operator machine | A ChatGPT clone |
| Public control plane you can clone | A dump of private living / chat logs |
| Chat does not own the schedule (mock demo here; 30-minute plant receipt there) | AUTORUN after every crash |
| Fail-closed intent, with HOLD still pending on the assurance checklist | Invented GPU/RAM theater |
| Claim ≤ proof | Production-ready, enterprise-grade, revolutionary, autonomous, or self-healing |

## Keywords

local agent runtime · supervised LLM agent · persistent AI loop · watchdog process supervision · long-horizon agents · plant clock ≠ chat · private PC

Denis Rigsby / Aetheria Project. Origin: [docs/ORIGIN.md](docs/ORIGIN.md).
