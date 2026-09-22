# Closeout — 2026-09-22

Evidence index for the Talk Face public cut. A row is PASS only when a scrubbed gate file is linked. Notes with no gate file stay pending.

Prior index: [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md) · claim table: [CLAIMS.md](CLAIMS.md) · mouth contract: [TALK_FACE.md](TALK_FACE.md).

Scrubbed receipts: [measurements/public_index/](../measurements/public_index/). Plant source paths and private measurement-bank paths are omitted. `soft_ACCEPT` is false on every receipt. `dual_bank` is false where the seal recorded it.

On the two gate receipts, `bank` remains `COVER_ACCEPT_ARCHITECT_PENDING` as stored on the seal object. `verdict` and `architect_accept` on those same objects are `ARCHITECT_ACCEPT` and `ACCEPT`.

P1–P5, where the prior brief names it, is **internal certification** only. That is not external accreditation.

Export parity stays **PRIVATE_AHEAD**. This tree is not the live plant.

## PASS

Proved this session on the operator plant where a scrubbed gate file is in this repo (Cover + Architect ACCEPT on that file). `soft_ACCEPT` is false. Rows with no gate file are under PENDING.

| # | Claim | Exclusion beside the claim | Receipt |
|---|-------|----------------------------|---------|
| 2 | Talk Face chat text has no visible `[MODEL_REASONING]` tag. Absolute `/living/...` cites are rewritten to plant-relative form or refused. | Does not publish plant source. Copilot is not the mouth (see LOCKED). | [scrub_mouth_leak_v1.json](../measurements/public_index/scrub_mouth_leak_v1.json), [gate_talkface_visible_tag_seal_v1.json](../measurements/public_index/gate_talkface_visible_tag_seal_v1.json), [architect_accept_talkface_visible_tag_seal_v1.json](../measurements/public_index/architect_accept_talkface_visible_tag_seal_v1.json) |
| 3 | Direct-answer contract for Talk Face. Cover ACCEPT and Architect ACCEPT. `soft_ACCEPT=false`. | No LIVE_RSI / L7 unlock. `dual_bank=false`. | [gate_direct_answer_contract_talk_face_v1.json](../measurements/public_index/gate_direct_answer_contract_talk_face_v1.json), [architect_accept_direct_answer_contract_talk_face_v1.json](../measurements/public_index/architect_accept_direct_answer_contract_talk_face_v1.json) |

Gate JSON in this index covers the mouth tag seal and the direct-answer contract. Rows 1, 4, and 5 have no gate file. They stay Pending.

## PENDING

| Item | Why it stays pending |
|------|----------------------|
| Re-run of the gate files above inside this public clone | Mouth implementation is not in this tree. PASS above is the operator receipt, not a CI re-proof here. |
| Export parity (public equals live plant) | Still **PRIVATE_AHEAD**. See [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md). |
| 1. Talk Face plant presence between ticks shows Standby (not Degraded). Offline means the mouth host is unreachable | Operator note, this session. No gate file. Mouth label only. Plant clock ≠ chat. Not Proved |
| 4. Canonical operator Desktop shortcut (single location; host path unpublished) | Operator note, this session. No gate file. No second shortcut location. Not Proved |
| 5. Talk Face launcher uses normal windowed Edge (taskbar + close), not a frameless `--app` window | Operator note, this session. No gate file. The window is the mouth, not the plant clock. Not Proved |

## LOCKED

Withheld. Not claimed by this cut.

| Item | Beside the claims |
|------|-------------------|
| Dual-bank FULL_PROGRAM | Not banked. Receipts that record the field have `dual_bank=false`. |
| `soft_ACCEPT` / LIVE_RSI / L7 | `soft_ACCEPT` stays false. No unlock. |
| Copilot as plant mouth, or Copilot through Plant Truth | Not claimed. |
| Federation / swarm / autonomy theater / self-healing / gated self-modification | Not claimed as present fact. |
| Production-ready, enterprise, enterprise-grade, revolutionary | Not claimed by this cut. |
| Widen spawn wrap | Not claimed. Not published. |

## Publication limits

- No plant loop or RSI source.
- No private measurement trees.
- No credentials.
- No spawn-wrap widen.

---

# Closeout — 2026-09-22 evening (kill / create_time plant seals)

Second sealed cut. Evidence index for dual-banked plant gates. Receipts only.

The Talk Face cut above is unchanged. Those mouth receipts still record `dual_bank=false`. This cut does not rewrite them and does not dual-bank FULL_PROGRAM.

Scrubbed receipts: [measurements/public_index/](../measurements/public_index/). Plant source paths, operator home paths, credentials, and agent IDs are omitted. `soft_ACCEPT` is false on every receipt in this cut. `dual_bank` is true on the six gate receipts below.

Export parity stays **PRIVATE_AHEAD**. This tree is not the live plant. `public_equals_plant` is false. It would be true only if `gate_export_hash_parity_v1` recorded decision `PARITY_PASS`. It does not.

P1–P5, where the prior brief names it, remains **internal certification** only.

Packet list (gate names, not a seventh gate): [MANIFEST_f68b.json](../measurements/public_index/MANIFEST_f68b.json).

## PASS

Proved on the operator plant (Cover ACCEPT + Architect ACCEPT). Claim only the receipt `claim_wording`. `dual_bank=true`. `soft_ACCEPT=false`.

| # | Claim | Exclusion beside the claim | Receipt |
|---|-------|----------------------------|---------|
| 1 | Stale-PID reuse refuse as defined by gate_stale_pid_reuse_v1: kill_if_verified with expected_create_time refuses create_time_mismatch (and does not terminate) when live create_time disagrees with the bound value, even if cmdline still matches the claimed role. Revision `create_time_bind_v1`. | OS PID-number reuse was not observed and is not required. Not every call site. create_time is not sole identity. PID reuse is not impossible. Pytest in this clone does not flip the gate. Tree-kill stays **Locked on non-Windows**. A wrong live PID mismatch alone does not flip the gate. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. Job Object is not the sole stop path. Toolhelp is not retired. | [gate_stale_pid_reuse_v1_1412.json](../measurements/public_index/gate_stale_pid_reuse_v1_1412.json), [stale_pid_reuse_v1_architect_accept_15da.json](../measurements/public_index/stale_pid_reuse_v1_architect_accept_15da.json), [stale_pid_reuse_v1_cover_accept_2042.json](../measurements/public_index/stale_pid_reuse_v1_cover_accept_2042.json) |
| 2 | Live kill call sites `lh_watchdog.kill_pid`, `plant_control._kill_pid`, `lh_recover_reap.reap_orphan_probes`, and `status_report.reap_orphans` pass `expected_create_time` into `kill_if_verified`; wrong create_time refuses with `create_time_mismatch` and does not terminate. Revision `call_site_wire_v1` on `gate_expected_create_time_call_sites_v1`. | OS PID-number reuse was not observed. Not every future kill site. create_time is not sole identity. No L7, LIVE_RSI, second clock, autonomy, or public=plant. | [gate_expected_create_time_call_sites_v1_930b.json](../measurements/public_index/gate_expected_create_time_call_sites_v1_930b.json), [expected_create_time_call_sites_v1_architect_accept_00ed.json](../measurements/public_index/expected_create_time_call_sites_v1_architect_accept_00ed.json), [expected_create_time_call_sites_v1_cover_accept_c2cd.json](../measurements/public_index/expected_create_time_call_sites_v1_cover_accept_c2cd.json) |
| 3 | continuous supervised plant clock 30 minutes, mouth closed, tick advanced; as defined by `gate_endurance_v1`. | Endurance beyond that window stays locked. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. This gate does not claim Job Object kill, stale-PID reuse, or the export-hash layer. | [gate_endurance_v1_0440.json](../measurements/public_index/gate_endurance_v1_0440.json) |
| 4 | Job Object kill-path as defined by `gate_job_object_kill_path_v1`: identity-checked `TerminateJobObject` stops an assigned process tree (root and child dead). | **Proved on Windows**. **Locked on non-Windows**. Job Object is not the sole plant stop path. Toolhelp is not retired. No second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant. This gate does not claim stale-PID reuse, the export-hash layer, or a portable relaunch. Endurance beyond `gate_endurance_v1` stays locked. | [gate_job_object_kill_path_v1_a709.json](../measurements/public_index/gate_job_object_kill_path_v1_a709.json) |
| 5 | Export hash/parity receipt layer as defined by `gate_export_hash_parity_v1`: fail-closed census of public export paths vs plant counterparts with per-path hashes and an explicit decision (`PARITY_PASS` or `PRIVATE_AHEAD`); `public_equals_plant` is true only when decision is `PARITY_PASS`. | This receipt's decision is **PRIVATE_AHEAD**, so public≠plant. Export is not the full plant. The full-program claim does not include export parity. No publish sync without Denis GO. No second clock, autonomy, LIVE_RSI, or L7. | [gate_export_hash_parity_v1_79b2.json](../measurements/public_index/gate_export_hash_parity_v1_79b2.json) |
| 6 | `gate_control_plane_resume_stop_watchdog_v1` records `DUAL_BANK_COMPLETE`, Cover ACCEPT, Architect ACCEPT, `dual_bank=true`, `soft_ACCEPT=false`. | `claim_wording` is null and `locked` is empty on the scrubbed receipt. No CommandLine redact field is present. No further operational sentence is claimed. | [gate_control_plane_resume_stop_watchdog_v1_84f7.json](../measurements/public_index/gate_control_plane_resume_stop_watchdog_v1_84f7.json) |

## PENDING

| Item | Why it stays pending |
|------|----------------------|
| Re-run of these seals inside this public clone | Plant implementation is not in this tree. PASS above is the operator receipt, not a CI re-proof here. Pytest in this clone does not flip `gate_stale_pid_reuse_v1`. Tree-kill and Job Object stop stay **Locked on non-Windows**. |
| Export parity (public equals live plant) | Decision stays **PRIVATE_AHEAD**. `PUBLIC_EQUALS_PLANT` only if the decision were `PARITY_PASS`. |

## LOCKED

Withheld. Not claimed by this cut.

| Item | Beside the claims |
|------|-------------------|
| L7 / LIVE_RSI | No unlock. |
| `soft_ACCEPT` | Stays false on every receipt. |
| Second clock | Not claimed. |
| Autonomy / `autonomy_proven` / auto-dispatch | Not claimed. |
| public = plant | Decision is `PRIVATE_AHEAD`. Not `PARITY_PASS`. |
| OS PID-number reuse observation | Not observed. Not required by `gate_stale_pid_reuse_v1`. |
| Every future kill site | Named sites in row 2 only. |
| Endurance beyond the 30-minute window | Row 3 is that window only. |
| Job Object as the sole plant stop path; Toolhelp retired | Row 4 is one identity-checked Windows tree kill. |
| Portable tree-kill, Job Object stop, or watchdog relaunch | **Locked on non-Windows**. Row 4 does not travel off Windows. |
| create_time as sole identity | Not claimed. |
| Publish sync without Denis GO | Not claimed. |
| Dual-bank FULL_PROGRAM | These six gates do not bank it. |
| Federation / swarm / autonomy theater / self-healing / gated self-modification | Not claimed as present fact. |
| Production-ready, enterprise, enterprise-grade, revolutionary | Not claimed by this cut. |
| Live LoRA hot-swap | Not claimed. |

## Publication limits

- No plant loop or RSI source.
- No private measurement trees.
- No credentials, agent IDs, or operator home paths.
- No spawn-wrap widen.
