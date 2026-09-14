# Reference-task portfolio

Machine source: [reference-task-portfolio.json](reference-task-portfolio.json).

Missions map to `local_deterministic_v2` where a benchmark task exists. `safe_refusal` is portfolio-only until a dedicated evaluator exists (specified, not prototype).

Held-out benchmark names must not appear in the suite `visible_tasks` list. Candidates must not rewrite these definitions at runtime (`research.evaluate.sanitize_genome`).
