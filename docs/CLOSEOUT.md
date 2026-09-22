# Closeout — 2026-09-22

Evidence index for the Talk Face public cut. Receipts only.

Prior index: [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md) · claim table: [CLAIMS.md](CLAIMS.md) · mouth contract: [TALK_FACE.md](TALK_FACE.md).

Scrubbed receipts: [measurements/public_index/](../measurements/public_index/). Plant source paths and private measurement-bank paths are omitted. `soft_ACCEPT` is false on every receipt. `dual_bank` is false where the seal recorded it.

On the two gate receipts, `bank` remains `COVER_ACCEPT_ARCHITECT_PENDING` as stored on the seal object. `verdict` and `architect_accept` on those same objects are `ARCHITECT_ACCEPT` and `ACCEPT`.

P1–P5, where the prior brief names it, is **internal certification** only. That is not external accreditation.

Export parity stays **PRIVATE_AHEAD**. This tree is not the live plant.

## PASS

Proved this session on the operator plant (Cover + Architect ACCEPT).

| # | Claim | Exclusion beside the claim | Receipt |
|---|-------|----------------------------|---------|
| 1 | Talk Face plant presence between ticks shows **Standby** (not Degraded). **Offline** means the mouth host is unreachable. | Mouth label only. Plant clock ≠ chat. Offline names mouth-host reachability; Standby names plant presence between ticks. | Operator GO, this session. No separate gate file in this packet. |
| 2 | Talk Face chat text has no visible `[MODEL_REASONING]` tag. Absolute `/living/...` cites are rewritten to plant-relative form or refused. | Does not publish plant source. Copilot is not the mouth (see LOCKED). | [scrub_mouth_leak_v1.json](../measurements/public_index/scrub_mouth_leak_v1.json), [gate_talkface_visible_tag_seal_v1.json](../measurements/public_index/gate_talkface_visible_tag_seal_v1.json), [architect_accept_talkface_visible_tag_seal_v1.json](../measurements/public_index/architect_accept_talkface_visible_tag_seal_v1.json) |
| 3 | Direct-answer contract for Talk Face. Cover ACCEPT and Architect ACCEPT. `soft_ACCEPT=false`. | No LIVE_RSI / L7 unlock. `dual_bank=false`. | [gate_direct_answer_contract_talk_face_v1.json](../measurements/public_index/gate_direct_answer_contract_talk_face_v1.json), [architect_accept_direct_answer_contract_talk_face_v1.json](../measurements/public_index/architect_accept_direct_answer_contract_talk_face_v1.json) |
| 4 | Canonical operator Desktop shortcut (single location; host path unpublished). | No second shortcut location. | Operator GO, this session. No separate gate file in this packet. |
| 5 | Talk Face launcher uses normal windowed Edge (taskbar + close), not a frameless `--app` black window. | The window is the mouth, not the plant clock. | Operator GO, this session. No separate gate file in this packet. |

Gate JSON in this index covers the mouth tag seal and the direct-answer contract. Items 1, 4, and 5 are the same session’s operator proofs; they are not re-run from this clone.

## PENDING

| Item | Why it stays pending |
|------|----------------------|
| Re-run of these seals inside this public clone | Mouth implementation is not in this tree. PASS above is the operator receipt, not a CI re-proof here. |
| Export parity (public equals live plant) | Still **PRIVATE_AHEAD**. See [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md). |

## LOCKED

Withheld. Not claimed by this cut.

| Item | Beside the claims |
|------|-------------------|
| Dual-bank FULL_PROGRAM | Not banked. Receipts that record the field have `dual_bank=false`. |
| `soft_ACCEPT` / LIVE_RSI / L7 | `soft_ACCEPT` stays false. No unlock. |
| Copilot as plant mouth, or Copilot through Plant Truth | Not claimed. |
| Federation / swarm / autonomy theater | Not claimed as present fact. |
| Widen spawn wrap | Not claimed. Not published. |

## Publication limits

- No plant loop or RSI source.
- No private measurement trees.
- No credentials.
- No spawn-wrap widen.
