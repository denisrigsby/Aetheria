# Promotion gates

Stages: `specified` → `local_deterministic_prototype` → `sandboxed_operational` → `controlled_external_use` → `production_candidate` → `production_approved`.

A unit test passing is **not** sufficient for `production_candidate` or `production_approved`.

## Required evidence between stages

| From → To | Minimum evidence |
|-----------|------------------|
| specified → local_deterministic_prototype | Deterministic evaluator; fixture; resource clamp; no network |
| local_deterministic_prototype → sandboxed_operational | Visible + held-out; failure injection; interrupt recovery; cleanup; no unmanaged survivors; artifacts retained |
| sandboxed_operational → controlled_external_use | Explicit authorization; independent evaluator; audit trail; refusal behavior; **manual review** |
| controlled_external_use → production_candidate | All of the above plus rollback drill; leak scan; no production plant auto-start |
| production_candidate → production_approved | Separate certification; human sign-off; production plant remains out of research authority |

## Automatic fail

Promotion **fails** if success on tasks is achieved by violating resource, authorization, cleanup, identity, audit, or evaluator-independence rules.

Promotion is never automatic into production.
