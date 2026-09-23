# Runnable demo (operator)

> Validation is self-run and receipt-backed; we publish how to reproduce it. We do not claim external certification.

## Goal

In about five minutes, show:

1. **It works** — sealed dual-bank receipts exist for the named claims
2. **It is running** — LIVE_RSI Enabled (bounded) with hard locks false

## Preconditions

- Windows plant used for the sealed runs
- Aetheria measurements tree present under the plant `measurements/integration/` path

## Steps

1. Confirm validation dual: open `measurements/integration/validation_publication_post_ble_v1/DUAL_BANK.json` → status `DUAL_ACCEPT_VALIDATION_123`.
2. Confirm Talk Face dual: `talkface_prepublish_acceptance_v1` GATE → `DUAL_ACCEPT_TALKFACE_APPLY_REPROVE`.
3. Confirm governed runtime dual: `governed_runtime_not_merely_chatbot_v1/DUAL_BANK.json` → `DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE`.
4. Confirm BSI / preliminary / true RSI prove duals on their cards.
5. Confirm apply dual: `true_rsi_evidence_v1/DUAL_BANK_APPLY.json` → `DUAL_ACCEPT_APPLY_TRUE_RSI`.
6. Confirm running: `measurements/lll/LLL_REGISTRY_ROW.json` and `LIVE_RSI_CONTROLS_STORE.json` show LIVE_RSI true, soft_ACCEPT false, rsi_level7 false, may_auto_promote false, network_live false, parent DRAFT_HOLD.

## Pass criteria

- Every listed dual status matches
- LIVE_RSI Enabled bounded with locks held
- No soft_ACCEPT true anywhere in the chain

## Fail closed

Any missing stamp, soft_ACCEPT true, or LIVE_RSI unrestricted claim → **demo FAIL**. Do not narrate around it.

---
Final cut pack 20260923T051217Z.
