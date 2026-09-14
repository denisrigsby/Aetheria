# local_deterministic_v2

Credential-free, model_calls=0. Organizations are scored by **roles and routing**, not by calling a model.

Visible and held-out sets share mechanisms (join, critic, early-stop) but not the same strings.

Quality `ok` is not the same as `composite` (composite subtracts duplication and extra workers).

`revision_after_critique` / `held_out_revision` require a **feedback edge** (`critic→planner` or `critic→executor`). A forward-only planner→executor→critic pipeline can detect an error but cannot revise. Same roles, different edges, different scores.
