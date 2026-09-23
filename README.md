# Aetheria

**Prove it works. Prove it is running.**

Aetheria is a governed, persistent AI runtime — not a chatbot. Chat is only its mouth.

In its currently demonstrated configuration it combines persistent memory, capability registration, receipt-backed evidence, fail-closed authority, bounded learning under external governance, and sealed RSI-style evidence with **LIVE_RSI Enabled (bounded)**.

> Validation is self-run and receipt-backed; we publish how to reproduce it. We do not claim external certification.

## Status labels (only these)

| Label | Meaning |
| --- | --- |
| **Proven (operator)** | Scrubbed dual receipt in this tree for the named scope. Operator-run and dual-bank sealed on the plant. Not a clean-room rebuild of the Windows plant |
| **HOLD** | Banked / gated; not promoted or not authorized to apply |
| **Not Proven** | No sealed receipt chain for the claim |
| **Not Enabled** | Implemented or specified but not live-enabled |

Soft ACCEPT is **false** plant-wide. Nothing here is Certified, independently audited, or unrestricted.

"Not a chatbot / chat is mouth" is an **Architectural classification**, not a Proven (operator) row by itself.

## Prove it works — sealed evidence

All of the following are **Proven (operator)**: a scrubbed dual receipt in this tree, not a clean-room rebuild of the Windows plant. Exclusions sit beside each claim. `status` strings match the JSON.

### Authority / learning ladder (applied)

| Card | Dual stamp | Claim | Beside the claim |
| --- | --- | --- | --- |
| Bounded autonomous promotion | [`DUAL_ACCEPT_BAP_APPLY_BOUNDED`](measurements/public_index/dual_accept_bap_apply_bounded.json) | bounded_autonomous_promotion_applied | soft_ACCEPT=false; allowlist fixed |
| Repeated promotion no-regression | [`DUAL_ACCEPT_RPR_APPLY`](measurements/public_index/dual_accept_rpr_apply.json) | repeated_bounded_promotion_no_regression_applied | parent open-ended doctrine still DRAFT/HOLD |
| Isolated learning domains | [`DUAL_ACCEPT_ILD_APPLY`](measurements/public_index/dual_accept_ild_apply.json) | isolated_learning_domains_applied | no allowlist expansion |
| Sandbox self-generated experiments | [`DUAL_ACCEPT_SGE_APPLY`](measurements/public_index/dual_accept_sge_apply.json) | sandbox_self_generated_experiments_applied | sandbox-bounded |
| Long-horizon learning across model replacement | [`DUAL_ACCEPT_LHL_APPLY`](measurements/public_index/dual_accept_lhl_apply.json) | long_horizon_learning_across_model_replacement_applied | model replacement under seal |
| Broader learning, externally bounded actions | [`DUAL_ACCEPT_BLE_APPLY`](measurements/public_index/dual_accept_ble_apply.json) | broader_learning_externally_bounded_actions_applied | actions remain externally bounded |

Validation publication steps 1–3: **Proven (operator)** — [`DUAL_ACCEPT_VALIDATION_123`](measurements/public_index/dual_accept_validation_123.json). `claim_sealed`: validation_publication_steps_1_2_3_evidence_proved_operator.

### Talk Face / mouth

Talk Face prepublish apply + re-prove: **Proven (operator)** — [`DUAL_ACCEPT_TALKFACE_APPLY_REPROVE`](measurements/public_index/dual_accept_talkface_apply_reprove.json)  
`claim_sealed`: talkface_prepublish_apply_and_reprove_pass_banked. Beside the claim: `publication_authorized` false; Not Certified. This stamp is not the true RSI receipt.

### Governed runtime (not merely chatbot)

**Proven (operator)** — [`DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE`](measurements/public_index/dual_accept_governed_runtime_nr_prove.json)  
`claim_sealed`: Operator-proven as a governed runtime independent of its chat interface. Beside the claim: `rsi_in_scope` false; **Not Certified.**

### Bounded self-improvement

**Proven (operator)** — [`DUAL_ACCEPT_BSI_THREE_CYCLE`](measurements/public_index/dual_accept_bsi_three_cycle.json)  
`claim_sealed`: Demonstrated three consecutive bounded self-improvement cycles under external governance.  
Beside claim: **not RSI** (`rsi_in_scope` false); prove-scoped at seal; **Not Certified.**

### RSI ladder

| Stage | Dual stamp | Claim | Beside the claim |
| --- | --- | --- | --- |
| Preliminary RSI | [`DUAL_ACCEPT_PRELIMINARY_RSI`](measurements/public_index/dual_accept_preliminary_rsi.json) | Preliminary RSI evidence under external governance. | does **not** satisfy true RSI; `LIVE_RSI` on this receipt is `Not Enabled` |
| True RSI evidence | [`DUAL_ACCEPT_TRUE_RSI`](measurements/public_index/dual_accept_true_rsi.json) | True RSI evidence under external governance (still not unrestricted / unbounded unless separately proved). | `LIVE_RSI` on this prove receipt is `Not Enabled`; still **not** unrestricted / unbounded; Not Certified |
| True RSI apply | [`DUAL_ACCEPT_APPLY_TRUE_RSI`](measurements/public_index/dual_accept_apply_true_rsi.json) | True RSI applied under external governance; LIVE_RSI Enabled (bounded — still not unrestricted / unbounded). | soft_ACCEPT=false; no rsi_level7; no may_auto_promote; no network_live; Not Certified; parent DRAFT/HOLD |

Publication pack: **Proven (operator)** — [`DUAL_ACCEPT_FINAL_REPO_PUBLISH`](measurements/public_index/dual_accept_final_repo_publish.json). `claim_sealed`: Final repo publish pack dual-bank sealed. Public main carries Proven (operator) claims with exclusions beside them; LIVE_RSI Enabled (bounded); soft_ACCEPT=false; Not Certified. Beside the claim: `export_parity` **PRIVATE_AHEAD**; public ≠ full plant.

## Prove it is running — live state

Read these two files in this tree:

- [`dual_accept_apply_true_rsi.json`](measurements/public_index/dual_accept_apply_true_rsi.json) — `status` `DUAL_ACCEPT_APPLY_TRUE_RSI`; `LIVE_RSI` is `Enabled (bounded under external governance)`; happy `true_rsi_20260923T044857Z`
- [`live_rsi_controls_store.json`](measurements/public_index/live_rsi_controls_store.json) — `LIVE_RSI` true; `LIVE_RSI_mode` `bounded_under_external_governance`; `dual_apply_status` `DUAL_ACCEPT_APPLY_TRUE_RSI`

Scrubbed registry snapshot (not an extra stamp): [`lll_registry_row.json`](measurements/public_index/lll_registry_row.json).

- **LIVE_RSI = Enabled (bounded under external governance)**
- soft_ACCEPT = false
- rsi_level7 = false
- may_auto_promote = false
- network_live = false
- unrestricted_rsi = false
- unbounded_rsi = false
- parent open-ended doctrine = **DRAFT/HOLD** (not operational; `parent_still_DRAFT_HOLD` true)
- FIXED_OPERATOR_SPACE unchanged at apply
- Sibling applied organs preserved (RPR/ILD/SGE/LHL/BLE)
- Not Certified

The live process tick remains on the operator plant. It is not GitHub-hosted. This record is **running under seal**, not unrestricted RSI and not certification.

## What remains HOLD / Not Enabled / Not Proven

- Parent open-ended learning under invariant governance: **DRAFT/HOLD**
- Unrestricted / unbounded RSI: **Not Proven** (explicitly excluded)
- rsi_level7 / may_auto_promote / network_live: **Not Enabled**
- External certification / independent audit: **Not Proven** (not claimed)
- Broader vision of replaceable-model governed intelligence: labeled separately; **not** mixed into this as-is definition

## How to verify the claims (clean clone)

A stranger verifies the claims by opening the scrubbed duals linked above. That does not require plant-only `measurements/integration/` paths, and it is not a clean-room rebuild of the Windows plant.

1. Open each `measurements/public_index/dual_accept_*.json` linked in the Proven tables and confirm `status`. Packet list: [`MANIFEST_ladder_20260923.json`](measurements/public_index/MANIFEST_ladder_20260923.json).
2. Open [`live_rsi_controls_store.json`](measurements/public_index/live_rsi_controls_store.json) and [`dual_accept_apply_true_rsi.json`](measurements/public_index/dual_accept_apply_true_rsi.json). LIVE_RSI is Enabled (bounded under external governance). `soft_ACCEPT` is false. `rsi_level7`, `may_auto_promote`, and `network_live` are false.
3. The live process tick remains on the operator plant. It is not GitHub-hosted.

Exact demo script: [docs/RUNNABLE_DEMO.md](docs/RUNNABLE_DEMO.md). Optional operator-plant replay of `measurements/integration/` is an appendix there. It is not required to verify these claims.  
Threat model: [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

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
