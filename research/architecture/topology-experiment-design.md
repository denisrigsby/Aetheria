# Future topology experiment (NOT IMPLEMENTED, NOT EXECUTED, NOT APPROVED)

This note prepares a later human decision. It does **not** enable topology mutation.

If approved later, an experiment may:

- mutate **communication edges only** (not prompts, not production code, not model weights);
- keep the fixed `local_deterministic_v2` evaluator;
- keep `max_active_workers` from `windows-local.json` (currently 8);
- keep `max_model_calls=0`;
- use disposable `research/runs/` roots only;
- require a held-out gain that is **not** explained by extra workers (worker-normalized quality);
- pass interruption, cleanup, rollback, and survivor=0 gates;
- require human approval before any promotion.

Do not add flags, mutation code, or tests that execute topology change until this document is explicitly approved.
