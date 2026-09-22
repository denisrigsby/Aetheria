# Claim register

Labels revised 2026-09-22. This revision does not add a proof. Front labels are **Real**, **Proved**, **Pending**, and **Locked** ([CLAIMS_TAXONOMY.md](CLAIMS_TAXONOMY.md)). A row here is not proved because an older copy of this file said PASS.

Origin: solo human–AI collaboration on **Windows** (Denis Rigsby). See [ORIGIN.md](ORIGIN.md) and [DEFINITION.md](DEFINITION.md).

P1–P5 are internal certification labels on the operator plant. They are not external accreditation, and they are not a public PASS.

| ID | Claim | Front label | Evidence and exclusion |
|----|-------|-------------|------------------------|
| C1 | Plant clock ≠ chat — mouth closed does not own the clock | **Real** for the mock. **Proved** only for the 30-minute endurance receipt | Mock: `scripts/demo_continuity.py` (CI does not run it). Plant window: `gate_endurance_v1` in [CLOSEOUT.md](CLOSEOUT.md). Longer than that window is **Locked** |
| C2 | One plant, two surfaces (Talk-face + Forge); `plant_chat` blocked; `kit_act` false | **Pending** for the operator plant. Reference refuse is **Real** / **Untested** | No gate file for Forge or for "one plant" as a standing fact. Docs: [DUAL_FACE.md](DUAL_FACE.md), [TALK_FACE.md](TALK_FACE.md). `tests/test_talk_face_ref_allowlist.py` is not in the CI command |
| C3 | Fail-closed write mouth — confirm required; `plant_chat` / `kit_act` refused | **Real** / **Untested** | `tests/test_talk_face_ref_allowlist.py`. The CI workflow on main does not run it. Not a public PASS |
| C4 | Held-out L5 stays 6/6 after the dual-face cut (MERGE_HOLD) | **Pending** | No scrubbed receipt in [measurements/public_index/](../measurements/public_index/). Not a public PASS |

Public reference tests cover allowlist / refuse / fail-closed confirm on the mock spine when you run that file locally. Full long-horizon and L5 artifacts remain on the operator machine by design (private vs public boundary).

## Operator-plant receipts (2026-09-22 evening)

Indexed from scrubbed receipts. `dual_bank=true`. `soft_ACCEPT=false`. Not re-proved by tests in this clone. Export decision stays **PRIVATE_AHEAD**. Detail and exclusions: [CLOSEOUT.md](CLOSEOUT.md).

| Gate | Claim (receipt wording) | Exclusion beside the claim |
|------|-------------------------|----------------------------|
| `gate_stale_pid_reuse_v1` (`create_time_bind_v1`) | Stale-PID reuse refuse as defined by gate_stale_pid_reuse_v1: kill_if_verified with expected_create_time refuses create_time_mismatch (and does not terminate) when live create_time disagrees with the bound value, even if cmdline still matches the claimed role. | OS PID-number reuse not observed and not required; not every call site; create_time not sole identity; PID reuse not impossible; portable pytest alone does not flip the gate; wrong live PID mismatch alone does not flip the gate; no second clock, autonomy, auto-dispatch, live LoRA hot-swap, LIVE_RSI, L7, or public=plant; Job Object not the sole stop path; Toolhelp not retired. |
| `gate_expected_create_time_call_sites_v1` (`call_site_wire_v1`) | Live kill call sites lh_watchdog.kill_pid, plant_control._kill_pid, lh_recover_reap.reap_orphan_probes, and status_report.reap_orphans pass expected_create_time into kill_if_verified; wrong create_time refuses with create_time_mismatch and does not terminate. | OS PID-number reuse not observed; L7; LIVE_RSI; second clock; autonomy; public=plant; every future kill site; create_time not sole identity. |
| `gate_endurance_v1` | continuous supervised plant clock 30 minutes, mouth closed, tick advanced; as defined by gate_endurance_v1 | Endurance beyond that window; second clock; autonomy; auto-dispatch; live LoRA hot-swap; LIVE_RSI; L7; this gate does not claim Job Object kill, stale-PID reuse, or export hash; public=plant. |
| `gate_job_object_kill_path_v1` | Job Object kill-path as defined by gate_job_object_kill_path_v1: identity-checked TerminateJobObject stops an assigned process tree (root and child dead). | Not the sole stop path; Toolhelp not retired; second clock; autonomy; auto-dispatch; live LoRA hot-swap; LIVE_RSI; L7; this gate does not claim stale-PID reuse or export hash; public=plant; endurance beyond gate_endurance_v1. |
| `gate_export_hash_parity_v1` | Export hash/parity receipt layer as defined by gate_export_hash_parity_v1: fail-closed census of public export paths vs plant counterparts with per-path hashes and an explicit decision (PARITY_PASS or PRIVATE_AHEAD); public_equals_plant is true only when decision is PARITY_PASS. | Decision on this receipt is PRIVATE_AHEAD, so public≠plant. Export is not the full plant. Full-program claim does not include export parity. No publish sync without Denis GO. No second clock, autonomy, LIVE_RSI, or L7. |
| `gate_control_plane_resume_stop_watchdog_v1` | Dual-bank record only. `claim_wording` is null. | No CommandLine redact field on the receipt. No further operational sentence. |

L7, LIVE_RSI, second clock, autonomy, and public=plant stay locked.

Discovery doctrine: searchable popular language is allowed only when bound to a proveable fact. See README.

## Public fault-injection (local test)

See [tests/test_fault_injection_public.py](../tests/test_fault_injection_public.py) for stale heartbeat, STOP idempotence, hash-mismatched snapshot refusal, wrong-role PID rejection, duplicate-supervisor role detection, interrupted checkpoint .tmp, and dirty last_ok → HOLD policy. These are control-plane checks with a mock/reference worker. The CI workflow on main does not run this file. This is not the private plant.
