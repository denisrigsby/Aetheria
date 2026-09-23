# Aetheria

**Prove it works. Prove it is running.**

Aetheria is a governed, persistent AI runtime — not a chatbot. Chat is only its mouth.

In its currently demonstrated configuration it combines persistent memory, capability registration, receipt-backed evidence, fail-closed authority, bounded learning under external governance, and sealed RSI-style evidence with **LIVE_RSI Enabled (bounded)**.

> Validation is self-run and receipt-backed; we publish how to reproduce it. We do not claim external certification.

## Status labels (only these)

| Label | Meaning |
| --- | --- |
| **Proven (operator)** | Operator-run, receipt-backed, dual-bank sealed for the named scope |
| **HOLD** | Banked / gated; not promoted or not authorized to apply |
| **Not Proven** | No sealed receipt chain for the claim |
| **Not Enabled** | Implemented or specified but not live-enabled |

Soft ACCEPT is **false** plant-wide. Nothing here is Certified, independently audited, or unrestricted.

"Not a chatbot / chat is mouth" is an **Architectural classification**, not a Proven (operator) row by itself.

## Prove it works — sealed evidence

All of the following are **Proven (operator)** with dual-bank stamps. Exclusions sit beside each claim.

### Authority / learning ladder (applied)

| Card | Dual stamp | Claim | Beside the claim |
| --- | --- | --- | --- |
| Bounded autonomous promotion | `DUAL_ACCEPT_BAP_APPLY_BOUNDED` | Applied under sealed controls | soft_ACCEPT=false; allowlist fixed |
| Repeated promotion no-regression | `DUAL_ACCEPT_RPR_APPLY` | Applied | parent open-ended doctrine still DRAFT/HOLD |
| Isolated learning domains | `DUAL_ACCEPT_ILD_APPLY` | Applied | no allowlist expansion |
| Sandbox self-generated experiments | `DUAL_ACCEPT_SGE_APPLY` | Applied | sandbox-bounded |
| Long-horizon learning across model replacement | `DUAL_ACCEPT_LHL_APPLY` | Applied | model replacement under seal |
| Broader learning, externally bounded actions | `DUAL_ACCEPT_BLE_APPLY` | Applied | actions remain externally bounded |

Validation publication steps 1–3: **Proven (operator)** — `DUAL_ACCEPT_VALIDATION_123` (snapshot, sealed-evidence replay, invariant/rollback audit).

### Talk Face / mouth

Talk Face prepublish apply + re-prove: **Proven (operator)** — `DUAL_ACCEPT_TALKFACE_APPLY_REPROVE`  
Registry-bound, fail-closed, claims != proposals, coherent controls/memory/evidence.

### Governed runtime (not merely chatbot)

`governed_runtime_not_merely_chatbot_v1` NR1–NR6: **Proven (operator)** — `DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE`  
NR6 witness is an **operator Windows subprocess**, not GitHub-hosted CI. **Not Certified.**

### Bounded self-improvement

Three consecutive bounded self-improvement cycles under external governance: **Proven (operator)** — `DUAL_ACCEPT_BSI_THREE_CYCLE`  
Beside claim: **not RSI**; was prove-scoped at seal.

### RSI ladder

| Stage | Dual stamp | Claim | Beside the claim |
| --- | --- | --- | --- |
| Preliminary RSI | `DUAL_ACCEPT_PRELIMINARY_RSI` | Preliminary RSI evidence under external governance | does **not** satisfy true RSI; was not LIVE_RSI enable |
| True RSI evidence | `DUAL_ACCEPT_TRUE_RSI` | True RSI evidence under external governance | still **not** unrestricted / unbounded; Not Certified |
| True RSI apply | `DUAL_ACCEPT_APPLY_TRUE_RSI` | True RSI applied; **LIVE_RSI Enabled (bounded)** | soft_ACCEPT=false; no rsi_level7; no may_auto_promote; no network_live; Not Certified; parent DRAFT/HOLD |

## Prove it is running — live state

As of apply dual `DUAL_ACCEPT_APPLY_TRUE_RSI` (happy `true_rsi_20260923T044857Z`):

- **LIVE_RSI = Enabled (bounded under external governance)**
- soft_ACCEPT = false
- rsi_level7 = false
- may_auto_promote = false
- network_live = false
- parent open-ended doctrine = **DRAFT/HOLD** (not operational)
- FIXED_OPERATOR_SPACE unchanged at apply
- Sibling applied organs preserved (RPR/ILD/SGE/LHL/BLE)

This is **running under seal**, not unrestricted RSI and not certification.

## What remains HOLD / Not Enabled / Not Proven

- Parent open-ended learning under invariant governance: **DRAFT/HOLD**
- Unrestricted / unbounded RSI: **Not Proven** (explicitly excluded)
- rsi_level7 / may_auto_promote / network_live: **Not Enabled**
- External certification / independent audit: **Not Proven** (not claimed)
- Broader vision of replaceable-model governed intelligence: labeled separately; **not** mixed into this as-is definition

## How to reproduce (operator)

1. Clean Windows plant with Aetheria install path used for the sealed runs.
2. Replay sealed validation pack under `measurements/integration/validation_publication_post_ble_v1/` (steps 1–3 receipts).
3. Confirm dual-bank stamps listed above on disk.
4. Confirm LIVE_RSI controls store + registry: Enabled bounded; soft_ACCEPT false; hard locks false.
5. Run Talk Face acceptance suite receipts under `talkface_prepublish_acceptance_v1`.

Exact demo script: see [docs/RUNNABLE_DEMO.md](docs/RUNNABLE_DEMO.md).  
Threat model: see [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Public trust order

1. Plain-English problem statement (this README)
2. Five-minute reproducible demo
3. Architecture / trust-boundary diagrams (as published)
4. Automated public CI (where wired)
5. Machine-readable receipts
6. Threat model and limitations
7. LLL/RSI material only with the sealed stamps above — never without exclusions

---
Final repo cut authorized by Denis `GO: FINAL_REPO_PUBLISH` (t1369u–t1371u).  
Voice: prove it works; prove it is running; no known failings; all receipts.  
soft_ACCEPT=false. Not Certified. Generated 2026-09-23T05:12:17.887768+00:00.
