# Runnable demo

> Validation is self-run and receipt-backed; we publish how to reproduce it. We do not claim external certification.

## Goal

From a clean clone, confirm:

1. **It works** — each named dual stamp is a scrubbed receipt in this tree
2. **It is running (bounded)** — [`live_rsi_controls_store.json`](../measurements/public_index/live_rsi_controls_store.json) shows LIVE_RSI enabled bounded, with hard locks false

**Proven (operator)** means that scrubbed dual receipt. It is not a clean-room rebuild of the Windows plant. The live process tick remains on the operator plant. It is not GitHub-hosted.

`soft_ACCEPT` is false. Not Certified. `export_parity` is **PRIVATE_AHEAD** (receipts only; public ≠ full plant). Parent open-ended doctrine stays **DRAFT/HOLD**.

## Primary path (clean clone)

No plant install is required. Open the files under [measurements/public_index/](../measurements/public_index/). A stranger does not need plant-only `measurements/integration/` paths to verify these claims.

1. Confirm each dual `status` (exact string):

| File | `status` |
| --- | --- |
| [dual_accept_bap_apply_bounded.json](../measurements/public_index/dual_accept_bap_apply_bounded.json) | `DUAL_ACCEPT_BAP_APPLY_BOUNDED` |
| [dual_accept_rpr_apply.json](../measurements/public_index/dual_accept_rpr_apply.json) | `DUAL_ACCEPT_RPR_APPLY` |
| [dual_accept_ild_apply.json](../measurements/public_index/dual_accept_ild_apply.json) | `DUAL_ACCEPT_ILD_APPLY` |
| [dual_accept_sge_apply.json](../measurements/public_index/dual_accept_sge_apply.json) | `DUAL_ACCEPT_SGE_APPLY` |
| [dual_accept_lhl_apply.json](../measurements/public_index/dual_accept_lhl_apply.json) | `DUAL_ACCEPT_LHL_APPLY` |
| [dual_accept_ble_apply.json](../measurements/public_index/dual_accept_ble_apply.json) | `DUAL_ACCEPT_BLE_APPLY` |
| [dual_accept_validation_123.json](../measurements/public_index/dual_accept_validation_123.json) | `DUAL_ACCEPT_VALIDATION_123` |
| [dual_accept_talkface_apply_reprove.json](../measurements/public_index/dual_accept_talkface_apply_reprove.json) | `DUAL_ACCEPT_TALKFACE_APPLY_REPROVE` |
| [dual_accept_governed_runtime_nr_prove.json](../measurements/public_index/dual_accept_governed_runtime_nr_prove.json) | `DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE` |
| [dual_accept_bsi_three_cycle.json](../measurements/public_index/dual_accept_bsi_three_cycle.json) | `DUAL_ACCEPT_BSI_THREE_CYCLE` |
| [dual_accept_preliminary_rsi.json](../measurements/public_index/dual_accept_preliminary_rsi.json) | `DUAL_ACCEPT_PRELIMINARY_RSI` |
| [dual_accept_true_rsi.json](../measurements/public_index/dual_accept_true_rsi.json) | `DUAL_ACCEPT_TRUE_RSI` |
| [dual_accept_apply_true_rsi.json](../measurements/public_index/dual_accept_apply_true_rsi.json) | `DUAL_ACCEPT_APPLY_TRUE_RSI` |
| [dual_accept_final_repo_publish.json](../measurements/public_index/dual_accept_final_repo_publish.json) | `DUAL_ACCEPT_FINAL_REPO_PUBLISH` |

2. Confirm [live_rsi_controls_store.json](../measurements/public_index/live_rsi_controls_store.json):

- `LIVE_RSI` is true
- `LIVE_RSI_mode` is `bounded_under_external_governance`
- `live_rsi_enabled` is true
- `soft_ACCEPT` is false
- `rsi_level7` is false
- `may_auto_promote` is false
- `network_live` is false
- `unrestricted_rsi` is false
- `unbounded_rsi` is false
- `not_certified` is true
- `parent_still_DRAFT_HOLD` is true
- `dual_apply_status` is `DUAL_ACCEPT_APPLY_TRUE_RSI`

3. Confirm [dual_accept_apply_true_rsi.json](../measurements/public_index/dual_accept_apply_true_rsi.json): `status` is `DUAL_ACCEPT_APPLY_TRUE_RSI`, and `LIVE_RSI` is `Enabled (bounded under external governance)`.

4. Optional snapshot: [lll_registry_row.json](../measurements/public_index/lll_registry_row.json) has `soft_ACCEPT` false and `parent_doctrine_status` `DRAFT_HOLD`. It does not unlock L7 or unrestricted RSI.

Packet list: [MANIFEST_ladder_20260923.json](../measurements/public_index/MANIFEST_ladder_20260923.json).

## Pass criteria

- Every listed `status` matches the table
- LIVE_RSI is enabled bounded, and `rsi_level7`, `may_auto_promote`, `network_live`, `unrestricted_rsi`, and `unbounded_rsi` are false
- `soft_ACCEPT` is false on every file in the ladder

## Fail closed

Any missing stamp, `soft_ACCEPT` true, or a claim of unrestricted or unbounded RSI → **demo FAIL**. Do not narrate around it.

## Appendix — operator-plant replay (optional)

This appendix does not verify the public claims. A stranger does not need `measurements/integration/` on a clean clone. Those paths live on the operator Windows plant.

On that plant, the same stamps were sealed under the integration cards (validation publication, Talk Face prepublish, governed runtime, bounded self-improvement, preliminary RSI, true RSI prove, and true RSI apply). The live process tick is that plant. It is not GitHub-hosted. If a plant file and the scrubbed copy disagree, public ≠ full plant stays **PRIVATE_AHEAD**.
