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
| Process identity rejects the wrong role or a junk PID. Windows tasklist liveness uses the PID column | The assurance row "unrelated processes survive stale-PID recovery" stays **PARTIAL**. The PID-column test does not flip `gate_stale_pid_reuse_v1`. OS PID-number reuse was not observed. This row is not a tree-kill. Tree-kill and Job Object stop are **Locked on non-Windows** | CI: `tests/test_lh_process_identity.py`, `tests/test_pid_liveness_exact.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Simultaneous start and recover admit one supervisor | Assurance row is **PASS** for that test (exactly one spawn) on Ubuntu and Windows CI. It is not a tree-kill and not a watchdog relaunch. Tree-kill and Job Object stop are **Locked on non-Windows**. Corrupted / unknown-version → HOLD and clean stop ≠ crash stay **PARTIAL**. This test is not the live plant. No `soft_ACCEPT`. This CI row is not L7 and is not the bounded LIVE_RSI receipt | CI: `tests/test_two_controller_concurrency.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| An interrupted JSON state write leaves the previous valid document or the new one | Assurance row is **PASS**. Private plant ≠ this tree. This CI receipt is not L7 and is not the bounded LIVE_RSI receipt. No soft_ACCEPT. PID and STOP files are short in-place text. Append-only JSONL is out of scope. `research/` artifacts are out of scope. Not an operator-plant receipt | CI on `395643e` (run 35695450920): `tests/test_atomic_state_writes.py`, `tests/test_interrupted_state_writes.py` · [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |

Run path: [README.md](README.md).

## Proved (receipt in this repo)

Accepted on the operator plant. Files here are scrubbed copies. This clone does not re-run them. `soft_ACCEPT` is false on these receipts.

Talk Face mouth receipts record `dual_bank=false`. The evening plant receipts and the 2026-09-23 ladder duals record `dual_bank=true`. None of these cuts dual-bank a full program, and none set public equal to plant.

| Claim | Exclusion beside the claim | Receipt |
|-------|----------------------------|---------|
| Talk-face text has no visible `[MODEL_REASONING]` tag. Absolute `/living/` cites are rewritten or refused | Does not publish plant source. Copilot is not the mouth | [scrub_mouth_leak_v1.json](measurements/public_index/scrub_mouth_leak_v1.json), [gate_talkface_visible_tag_seal_v1.json](measurements/public_index/gate_talkface_visible_tag_seal_v1.json), [architect_accept_talkface_visible_tag_seal_v1.json](measurements/public_index/architect_accept_talkface_visible_tag_seal_v1.json) |
| Direct-answer contract. Cover ACCEPT and Architect ACCEPT | This mouth receipt does not unlock L7 or LIVE_RSI. `dual_bank=false`. Bounded LIVE_RSI is the 2026-09-23 ladder below | [gate_direct_answer_contract_talk_face_v1.json](measurements/public_index/gate_direct_answer_contract_talk_face_v1.json), [architect_accept_direct_answer_contract_talk_face_v1.json](measurements/public_index/architect_accept_direct_answer_contract_talk_face_v1.json) |
| Stale-PID refuse (`gate_stale_pid_reuse_v1`, revision `create_time_bind_v1`): a kill is refused when live start time disagrees with the bound value, even if the command line still matches | OS PID-number reuse was not observed. Not every call site. Start time is not the only identity. Tests in this repo do not flip this gate | [gate_stale_pid_reuse_v1_1412.json](measurements/public_index/gate_stale_pid_reuse_v1_1412.json), [cover](measurements/public_index/stale_pid_reuse_v1_cover_accept_2042.json), [architect](measurements/public_index/stale_pid_reuse_v1_architect_accept_15da.json) |
| Named kill sites pass start time (`gate_expected_create_time_call_sites_v1`, revision `call_site_wire_v1`): `lh_watchdog.kill_pid`, `plant_control._kill_pid`, `lh_recover_reap.reap_orphan_probes`, `status_report.reap_orphans` | Not every future kill site. Start time is not sole identity | [gate_expected_create_time_call_sites_v1_930b.json](measurements/public_index/gate_expected_create_time_call_sites_v1_930b.json), [cover](measurements/public_index/expected_create_time_call_sites_v1_cover_accept_c2cd.json), [architect](measurements/public_index/expected_create_time_call_sites_v1_architect_accept_00ed.json) |
| 30 minutes, mouth closed, tick advanced (`gate_endurance_v1`) | Longer than that window stays locked. This gate does not claim Job Object kill, stale-PID reuse, or the export-hash layer | [gate_endurance_v1_0440.json](measurements/public_index/gate_endurance_v1_0440.json) |
| Job Object kill (`gate_job_object_kill_path_v1`): identity-checked `TerminateJobObject` stops an assigned tree (root and child dead) | **Proved on Windows** (operator plant). **Locked on non-Windows**. Not the only stop path. Toolhelp (Windows process listing) is not retired. Linux CI does not re-prove it | [gate_job_object_kill_path_v1_a709.json](measurements/public_index/gate_job_object_kill_path_v1_a709.json) |
| Export hash / parity layer (`gate_export_hash_parity_v1`): per-path hashes and a decision of `PARITY_PASS` or `PRIVATE_AHEAD`. Public equals plant only if the decision is `PARITY_PASS` | This receipt's decision is **PRIVATE_AHEAD** | [gate_export_hash_parity_v1_79b2.json](measurements/public_index/gate_export_hash_parity_v1_79b2.json) |
| `gate_control_plane_resume_stop_watchdog_v1` is dual-banked (`DUAL_BANK_COMPLETE`) | `claim_wording` is null. No CommandLine redact field. No stop or relaunch sentence. Not a portable control plane | [gate_control_plane_resume_stop_watchdog_v1_84f7.json](measurements/public_index/gate_control_plane_resume_stop_watchdog_v1_84f7.json) |

Packet list for the evening gates (not an extra gate): [MANIFEST_f68b.json](measurements/public_index/MANIFEST_f68b.json).

### Learning / RSI ladder (2026-09-23 scrubbed duals)

**Proven (operator)** in [README.md](README.md) is one of these scrubbed dual receipts in this tree. It is not a clean-room rebuild of the Windows plant. This clone does not re-run the plant. `soft_ACCEPT` is false. `export_parity` stays **PRIVATE_AHEAD** (receipts only; public ≠ full plant). Not Certified. Parent open-ended doctrine stays **DRAFT/HOLD**.

These rows do not unlock `rsi_level7`, `may_auto_promote`, `network_live`, or unrestricted RSI. Packet list (not an extra stamp): [MANIFEST_ladder_20260923.json](measurements/public_index/MANIFEST_ladder_20260923.json).

| Claim | Exclusion beside the claim | Receipt |
|-------|----------------------------|---------|
| `DUAL_ACCEPT_BAP_APPLY_BOUNDED`. bounded_autonomous_promotion_applied | soft_ACCEPT false. Allowlist fixed. Not unbounded learning | [dual_accept_bap_apply_bounded.json](measurements/public_index/dual_accept_bap_apply_bounded.json) |
| `DUAL_ACCEPT_RPR_APPLY`. repeated_bounded_promotion_no_regression_applied | soft_ACCEPT false. Parent open-ended doctrine still DRAFT/HOLD | [dual_accept_rpr_apply.json](measurements/public_index/dual_accept_rpr_apply.json) |
| `DUAL_ACCEPT_ILD_APPLY`. isolated_learning_domains_applied | soft_ACCEPT false. No allowlist expansion | [dual_accept_ild_apply.json](measurements/public_index/dual_accept_ild_apply.json) |
| `DUAL_ACCEPT_SGE_APPLY`. sandbox_self_generated_experiments_applied | soft_ACCEPT false. Sandbox-bounded | [dual_accept_sge_apply.json](measurements/public_index/dual_accept_sge_apply.json) |
| `DUAL_ACCEPT_LHL_APPLY`. long_horizon_learning_across_model_replacement_applied | soft_ACCEPT false. Model replacement under seal | [dual_accept_lhl_apply.json](measurements/public_index/dual_accept_lhl_apply.json) |
| `DUAL_ACCEPT_BLE_APPLY`. broader_learning_externally_bounded_actions_applied | soft_ACCEPT false. Actions remain externally bounded | [dual_accept_ble_apply.json](measurements/public_index/dual_accept_ble_apply.json) |
| `DUAL_ACCEPT_VALIDATION_123`. validation_publication_steps_1_2_3_evidence_proved_operator | soft_ACCEPT false. Not Certified. Public ≠ full plant | [dual_accept_validation_123.json](measurements/public_index/dual_accept_validation_123.json) |
| `DUAL_ACCEPT_TALKFACE_APPLY_REPROVE`. talkface_prepublish_apply_and_reprove_pass_banked | soft_ACCEPT false. `publication_authorized` false. Not Certified. This stamp is not the true RSI receipt | [dual_accept_talkface_apply_reprove.json](measurements/public_index/dual_accept_talkface_apply_reprove.json) |
| `DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE`. Operator-proven as a governed runtime independent of its chat interface. | soft_ACCEPT false. `rsi_in_scope` false. Not Certified | [dual_accept_governed_runtime_nr_prove.json](measurements/public_index/dual_accept_governed_runtime_nr_prove.json) |
| `DUAL_ACCEPT_BSI_THREE_CYCLE`. Demonstrated three consecutive bounded self-improvement cycles under external governance. | soft_ACCEPT false. Not RSI (`rsi_in_scope` false). Prove-scoped at seal. Not Certified | [dual_accept_bsi_three_cycle.json](measurements/public_index/dual_accept_bsi_three_cycle.json) |
| `DUAL_ACCEPT_PRELIMINARY_RSI`. Preliminary RSI evidence under external governance. | soft_ACCEPT false. Does not satisfy true RSI. `LIVE_RSI` on this receipt is `Not Enabled`. Not Certified | [dual_accept_preliminary_rsi.json](measurements/public_index/dual_accept_preliminary_rsi.json) |
| `DUAL_ACCEPT_TRUE_RSI`. True RSI evidence under external governance (still not unrestricted / unbounded unless separately proved). | soft_ACCEPT false. `LIVE_RSI` on this prove receipt is `Not Enabled`. Not unrestricted / unbounded. Not Certified | [dual_accept_true_rsi.json](measurements/public_index/dual_accept_true_rsi.json) |
| `DUAL_ACCEPT_APPLY_TRUE_RSI`. True RSI applied under external governance; LIVE_RSI Enabled (bounded — still not unrestricted / unbounded). | soft_ACCEPT false. No `rsi_level7`. No `may_auto_promote`. No `network_live`. Not Certified. Parent open-ended doctrine still DRAFT/HOLD. Live process tick remains operator-plant (not GitHub-hosted) | [dual_accept_apply_true_rsi.json](measurements/public_index/dual_accept_apply_true_rsi.json), [live_rsi_controls_store.json](measurements/public_index/live_rsi_controls_store.json) |
| `DUAL_ACCEPT_FINAL_REPO_PUBLISH`. Final repo publish pack dual-bank sealed. Public main carries Proven (operator) claims with exclusions beside them; LIVE_RSI Enabled (bounded); soft_ACCEPT=false; Not Certified. | `export_parity` **PRIVATE_AHEAD**. Public ≠ full plant. Not unrestricted RSI | [dual_accept_final_repo_publish.json](measurements/public_index/dual_accept_final_repo_publish.json) |

[`live_rsi_controls_store.json`](measurements/public_index/live_rsi_controls_store.json) is the running snapshot for that apply row: `LIVE_RSI` true, `LIVE_RSI_mode` `bounded_under_external_governance`, `soft_ACCEPT` false, `rsi_level7` false, `may_auto_promote` false, `network_live` false, `unrestricted_rsi` false, `unbounded_rsi` false, `not_certified` true, `parent_still_DRAFT_HOLD` true, `dual_apply_status` `DUAL_ACCEPT_APPLY_TRUE_RSI`. [`lll_registry_row.json`](measurements/public_index/lll_registry_row.json) is a scrubbed registry snapshot (`soft_ACCEPT` false, `parent_doctrine_status` `DRAFT_HOLD`). It is not an extra stamp and does not unlock L7 or unrestricted RSI.

A scrubbed gate file or a scrubbed dual receipt in [measurements/public_index/](measurements/public_index/) is required for **Proved**. An operator note with no such file is **Pending**.

## Pending

| Item | Why it stays open |
|------|-------------------|
| Re-run of the proved seals inside this clone | Mouth, plant loop, and RSI source are not in this tree. Reading the scrubbed duals verifies the claims. It does not re-execute the plant. [docs/CLOSEOUT.md](docs/CLOSEOUT.md) |
| Parent open-ended learning under invariant governance | **DRAFT/HOLD**. Not operational. The ladder duals do not promote it. Not Certified |
| Unrelated processes survive stale-PID recovery / stop | Assurance **PARTIAL**. [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Corrupted or unknown-version state ends in HOLD | Assurance **PARTIAL**. Hash mismatch refuse is tested; full HOLD wiring is plant-side |
| Clean stop distinguished from a crash | Assurance **PARTIAL**. Needs an explicit CI proof |
| Localhost mutations require authorization | Assurance **PARTIAL** |
| Job Object containment in this repo's CI | Assurance **PARTIAL**. The plant receipt is **Proved on Windows** only. It does not flip this row. **Locked on non-Windows** |
| Watchdog relaunch of a process tree | No gate file. Windows launchers are the reference. **Pending** on non-Windows. Not a portable stop |
| Standby vs Offline mouth labels | Operator note, 2026-09-22 Talk Face session. No gate file. Mouth label only. [docs/CLOSEOUT.md](docs/CLOSEOUT.md) |
| One desktop shortcut | Operator note. No gate file. Host path unpublished |
| Windowed Edge launcher (taskbar and close), not a frameless `--app` window | Operator note. No gate file. The window is the mouth, not the plant clock |
| Held-out L5 stays 6/6 after the dual-face cut | No scrubbed receipt in [measurements/public_index/](measurements/public_index/). [docs/CLAIMS.md](docs/CLAIMS.md) |
| No secrets in public artifacts | Assurance **PARTIAL**. CI scans `*.md` and `*.example.*` for absolute Windows user-home paths. That scan is the **PASS** row. It is not a secret scanner |
| Narrative install and lifecycle passes with no indexed receipt | Live validation #1, a "12 passed" tree-kill count, disposable root `standalone-lifecycle`, and clean-clone install for v0.3.2. [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) |

Simultaneous start/recover is **PASS** for `tests/test_two_controller_concurrency.py` on the assurance checklist. It is listed under Real. It is not pending. It does not pass the other rows.

Interrupted write → old or new valid state is **PASS** for `tests/test_atomic_state_writes.py` and `tests/test_interrupted_state_writes.py`. It is listed under Real. It is not pending. It does not pass the other rows. The receipt is the two control-plane CI jobs on `395643e`, not an operator-plant receipt, so it is not in the Proved table above.

## Locked

Withheld. Not claimed from this index.

| Item | Why it is locked |
|------|------------------|
| Public export equals the live plant | Decision is `PRIVATE_AHEAD`, not `PARITY_PASS` |
| Dual-bank full program (`gate_full_program_asset_class_v1`) | No receipt in [docs/CLOSEOUT.md](docs/CLOSEOUT.md), [docs/CLAIMS.md](docs/CLAIMS.md), or [measurements/public_index/](measurements/public_index/) |
| `soft_ACCEPT` | Stays false. No unlock |
| `rsi_level7`, `may_auto_promote`, `network_live` | Not Enabled. The bounded LIVE_RSI receipts do not unlock these |
| Unrestricted / unbounded RSI | Not Proven. Not claimed |
| L7 | No unlock. Bounded LIVE_RSI is the ladder above, not L7 |
| Copilot as the plant mouth, or Copilot through plant truth | Not claimed |
| Federation, swarm, self-healing, unrestricted autonomy, unrestricted self-modification | Not claimed as present fact. Bounded cards are only the ladder duals under Proved |
| Production-ready, enterprise, enterprise-grade, revolutionary | Assurance checklist is not all PASS. [docs/RELEASE_GATE_ASSURANCE.md](docs/RELEASE_GATE_ASSURANCE.md) |
| Second clock, automatic dispatch, live model hot-swap | Not claimed |
| Endurance past the 30-minute window | The endurance receipt is that window only |
| Job Object as the only stop path; Toolhelp retired | The Job Object receipt is one Windows tree kill |
| Portable tree-kill, Job Object stop, or watchdog relaunch | **Locked on non-Windows**. Windows receipts do not travel with the OS |
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
- "Atomic dual start" as a plant seal. The public proof is the CI **PASS** under Real, scoped to `tests/test_two_controller_concurrency.py`
- Standby / Offline, one desktop shortcut, and the windowed Edge launcher, as proved seals. They are Pending above (no gate file)
- Held-out L5 6/6. No receipt in this index
- A GPU mutex, or "the body is real," as a public fact. No receipt
- `PARTIAL→improved` as a pass. A historical note that stays **PARTIAL** is still pending

## How to read a claim

State the receipt. Keep the exclusion beside it. Leave pending rows pending. Prefer a weaker label when a file and a sentence disagree. [docs/CLAIMS_TAXONOMY.md](docs/CLAIMS_TAXONOMY.md).
