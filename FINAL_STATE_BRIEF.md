# Aetheria evidence index

This page is the public index of what is real in this repo, what has a receipt, what is still open, and what is withheld.

**What it is.** Aetheria is a local supervisor for long-running AI work on one Windows PC. The chat window is optional. The work schedule (the plant clock) is a separate process plus files on disk. Closing the chat does not stop that schedule. **Plant clock ≠ chat.**

**Public export ≠ live plant.** Parity decision: **PRIVATE_AHEAD**. [docs/EXPORT_PARITY.md](docs/EXPORT_PARITY.md). Scrubbed copies: [measurements/public_index/](measurements/public_index/). Narrative tables: [docs/CLOSEOUT.md](docs/CLOSEOUT.md).

**P1–P5** are internal certification labels on the operator plant. They are not an outside audit. This index has no public receipt that turns them into one.

Words used below: **Cover** and **Architect** are two accept roles on a plant receipt. **dual_bank** means both roles accepted on that receipt. **soft_ACCEPT** false means the receipt was not waved through. **HOLD** means a fail-closed pause. **create_time** means the process start time used as an identity check.

## Real (this repository)

You can run these here. They do not re-prove the plant receipts below.

| Claim | Limit | Evidence |
|-------|--------|----------|
| This tree has a supervisor control plane and a mock worker | Clone smoke does not start the private plant | `python -u scripts/demo_local_smoke.py` · [docs/PUBLIC_DEMO.md](docs/PUBLIC_DEMO.md) |
| A mock pulse keeps advancing after the reference mouth closes | Mock only. That is the public slice of plant clock ≠ chat | `python -u scripts/demo_continuity.py` · [docs/CONTINUITY_DEMO.md](docs/CONTINUITY_DEMO.md) |
| Process identity rejects the wrong role or a junk PID | The assurance row "unrelated processes survive stale-PID recovery" is **PARTIAL** | CI: `tests/test_lh_process_identity.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Simultaneous start and recover admit one supervisor | Assurance row is **PASS**. Other state writers stay **PARTIAL**. This test is not the live plant. No `soft_ACCEPT`. No L7 / LIVE_RSI | CI: `tests/test_two_controller_concurrency.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |

Run path: [README.md](README.md).

## Proved (receipt in this repo)

Accepted on the operator plant. Files here are scrubbed copies. This clone does not re-run them. `soft_ACCEPT` is false on these receipts.

Talk Face mouth receipts record `dual_bank=false`. The evening plant receipts record `dual_bank=true`. Neither cut dual-banks a full program, and neither sets public equal to plant.

| Claim | Exclusion beside the claim | Receipt |
|-------|----------------------------|---------|
| Talk-face text has no visible `[MODEL_REASONING]` tag. Absolute `/living/` cites are rewritten or refused | Does not publish plant source. Copilot is not the mouth | [scrub_mouth_leak_v1.json](measurements/public_index/scrub_mouth_leak_v1.json), [gate_talkface_visible_tag_seal_v1.json](measurements/public_index/gate_talkface_visible_tag_seal_v1.json), [architect_accept_talkface_visible_tag_seal_v1.json](measurements/public_index/architect_accept_talkface_visible_tag_seal_v1.json) |
| Direct-answer contract. Cover ACCEPT and Architect ACCEPT | No L7 / LIVE_RSI. `dual_bank=false` | [gate_direct_answer_contract_talk_face_v1.json](measurements/public_index/gate_direct_answer_contract_talk_face_v1.json), [architect_accept_direct_answer_contract_talk_face_v1.json](measurements/public_index/architect_accept_direct_answer_contract_talk_face_v1.json) |
| Stale-PID refuse (`gate_stale_pid_reuse_v1`, revision `create_time_bind_v1`): a kill is refused when live start time disagrees with the bound value, even if the command line still matches | OS PID-number reuse was not observed. Not every call site. Start time is not the only identity. Tests in this repo do not flip this gate | [gate_stale_pid_reuse_v1_1412.json](measurements/public_index/gate_stale_pid_reuse_v1_1412.json), [cover](measurements/public_index/stale_pid_reuse_v1_cover_accept_2042.json), [architect](measurements/public_index/stale_pid_reuse_v1_architect_accept_15da.json) |
| Named kill sites pass start time (`gate_expected_create_time_call_sites_v1`, revision `call_site_wire_v1`): `lh_watchdog.kill_pid`, `plant_control._kill_pid`, `lh_recover_reap.reap_orphan_probes`, `status_report.reap_orphans` | Not every future kill site. Start time is not sole identity | [gate_expected_create_time_call_sites_v1_930b.json](measurements/public_index/gate_expected_create_time_call_sites_v1_930b.json), [cover](measurements/public_index/expected_create_time_call_sites_v1_cover_accept_c2cd.json), [architect](measurements/public_index/expected_create_time_call_sites_v1_architect_accept_00ed.json) |
| 30 minutes, mouth closed, tick advanced (`gate_endurance_v1`) | Longer than that window stays locked. This gate does not claim Job Object kill, stale-PID reuse, or the export-hash layer | [gate_endurance_v1_0440.json](measurements/public_index/gate_endurance_v1_0440.json) |
| Job Object kill (`gate_job_object_kill_path_v1`): identity-checked `TerminateJobObject` stops an assigned tree (root and child dead) | Not the only stop path. Toolhelp (Windows process listing) is not retired. Linux CI does not re-prove it | [gate_job_object_kill_path_v1_a709.json](measurements/public_index/gate_job_object_kill_path_v1_a709.json) |
| Export hash / parity layer (`gate_export_hash_parity_v1`): per-path hashes and a decision of `PARITY_PASS` or `PRIVATE_AHEAD`. Public equals plant only if the decision is `PARITY_PASS` | This receipt's decision is **PRIVATE_AHEAD** | [gate_export_hash_parity_v1_79b2.json](measurements/public_index/gate_export_hash_parity_v1_79b2.json) |
| `gate_control_plane_resume_stop_watchdog_v1` is dual-banked (`DUAL_BANK_COMPLETE`) | `claim_wording` is null. No CommandLine redact field. No further operational sentence | [gate_control_plane_resume_stop_watchdog_v1_84f7.json](measurements/public_index/gate_control_plane_resume_stop_watchdog_v1_84f7.json) |

Packet list for the evening gates (not an extra gate): [MANIFEST_f68b.json](measurements/public_index/MANIFEST_f68b.json).

**Operator notes with no gate file** (2026-09-22 Talk Face session). Same closeout, weaker receipt. Not re-run from this clone:

| Note | Limit |
|------|--------|
| Between ticks the mouth shows Standby, not Degraded. Offline means the mouth host is unreachable | Mouth label only |
| One desktop shortcut. Host path unpublished | No second shortcut location |
| Launcher is a normal Edge window (taskbar and close), not a frameless `--app` window | The window is the mouth, not the plant clock |

## Pending

| Item | Why it stays open |
|------|-------------------|
| Re-run of the proved seals inside this clone | Mouth and plant body are not in this tree. [docs/CLOSEOUT.md](docs/CLOSEOUT.md) |
| Unrelated processes survive stale-PID recovery / stop | Assurance **PARTIAL**. [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Interrupted write leaves the old or the new valid state | Assurance **PARTIAL**. Not every writer is migrated |
| Corrupted or unknown-version state ends in HOLD | Assurance **PARTIAL**. Hash mismatch refuse is tested; full HOLD wiring is plant-side |
| Clean stop distinguished from a crash | Assurance **PARTIAL**. Needs an explicit CI proof |
| Localhost mutations require authorization | Assurance **PARTIAL** |
| Job Object containment in this repo's CI | Assurance **PARTIAL**. The plant receipt above does not flip this row |

Simultaneous start/recover is **PASS** on the assurance checklist. It is listed under Real. It is not pending.

## Locked

Withheld. Not claimed from this index.

| Item | Why it is locked |
|------|------------------|
| Public export equals the live plant | Decision is `PRIVATE_AHEAD`, not `PARITY_PASS` |
| Dual-bank full program (`gate_full_program_asset_class_v1`) | No receipt in [docs/CLOSEOUT.md](docs/CLOSEOUT.md), [docs/CLAIMS.md](docs/CLAIMS.md), or [measurements/public_index/](measurements/public_index/) |
| `soft_ACCEPT`, LIVE_RSI, L7 | `soft_ACCEPT` stays false. No unlock |
| Copilot as the plant mouth, or Copilot through plant truth | Not claimed |
| Federation, swarm, autonomy, self-healing | Not claimed as present fact |
| Production-ready, enterprise | Assurance checklist is not all PASS. [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Second clock, automatic dispatch, live model hot-swap | Not claimed |
| Endurance past the 30-minute window | The endurance receipt is that window only |
| Job Object as the only stop path; Toolhelp retired | The Job Object receipt is one tree kill |
| Start time as the only identity | Not claimed |
| OS PID-number reuse was observed | Not observed |
| Every future kill site | Named sites only |
| Publish sync without an explicit operator GO | Not granted here |
| Wider spawn wrap | Not published |
| P1–P5 as external accreditation | Internal certification only |

## Not listed as proved

An earlier draft of this index named items that have no receipt in this tree. They are not public claims:

- LoRA train (`may_train`) and LoRA shadow deploy
- A generic "identity-checked kill path" beyond the Job Object receipt and the named call sites
- A generic offline cold-start, beyond the 30-minute endurance receipt and the mock continuity demo
- "Atomic dual start" as a plant seal. The public proof is the CI **PASS** under Real, scoped to that test

## How to read a claim

State the receipt. Keep the exclusion beside it. Leave pending rows pending. Prefer a weaker label when a file and a sentence disagree. [docs/CLAIMS_TAXONOMY.md](docs/CLAIMS_TAXONOMY.md).
