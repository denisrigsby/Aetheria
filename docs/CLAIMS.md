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

Discovery doctrine: searchable popular language is allowed only when bound to a proveable fact. See README.

## Public fault-injection (CI)

See 	ests/test_fault_injection_public.py for stale heartbeat, STOP idempotence, hash-mismatched snapshot refusal, wrong-role PID rejection, duplicate-supervisor role detection, interrupted checkpoint .tmp, and dirty last_ok → HOLD policy. These are control-plane proofs with a mock/reference worker — not the private plant.
