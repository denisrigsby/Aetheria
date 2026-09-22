# Proven claims

Updated: `2026-09-19T22:08:39.940577+00:00`

Origin: solo human–AI collaboration on **Windows**. See [ORIGIN.md](ORIGIN.md) and [DEFINITION.md](DEFINITION.md).

| ID | Claim | Status | How to verify in this repo |
|----|-------|--------|----------------------------|
| C1 | Plant clock ≠ chat — mouth down does not own the clock | PASS (operator plant) | Doctrine + Talk-face ref does not host a plant clock |
| C2 | Dual face, one plant — Talk-face + Open Forge; plant_chat blocked; kit_act false | PASS (operator plant) | [DUAL_FACE.md](DUAL_FACE.md), [TALK_FACE.md](TALK_FACE.md) |
| C3 | Fail-closed write mouth — confirm required; plant_chat/kit_act refused | PASS | `tests/test_talk_face_ref_allowlist.py` |
| C4 | Held-out L5 stays 6/6 after dual-face cut (MERGE_HOLD) | PASS (operator plant) | Private plant gate; not re-soft-greened here |

Public reference tests cover allowlist / refuse / fail-closed confirm on the mock spine. Full long-horizon and L5 artifacts remain on the operator machine by design (private vs public boundary).

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

## Public fault-injection (CI)

See 	ests/test_fault_injection_public.py for stale heartbeat, STOP idempotence, hash-mismatched snapshot refusal, wrong-role PID rejection, duplicate-supervisor role detection, interrupted checkpoint .tmp, and dirty last_ok → HOLD policy. These are control-plane proofs with a mock/reference worker — not the private plant.
