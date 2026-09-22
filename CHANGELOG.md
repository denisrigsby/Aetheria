# Changelog

All notable changes to the **public control plane** are documented here.


## [Unreleased]

### Changed

- **Claim scope** ([FINAL_STATE_BRIEF.md](FINAL_STATE_BRIEF.md)): top-level Claim is the asset-class **as defined by** `gate_full_program_asset_class_v1` only. Dual-bank FULL_PROGRAM stays locked. The 2026-09-22 evening cut did not extend it. `soft_ACCEPT` stays false. Not claimed: L7, LIVE_RSI, public=plant, autonomy, second clock. Stale pending line "verify public CI green on main after bleach push" removed; public CI on main for that evening cut is green.

### Added

- **Public closeout 2026-09-22 evening** ([docs/CLOSEOUT.md](docs/CLOSEOUT.md)): second sealed cut for dual-banked plant gates (`dual_bank=true`, `soft_ACCEPT=false`). PASS as receipt wording: `gate_stale_pid_reuse_v1` (`create_time_bind_v1`); `gate_expected_create_time_call_sites_v1` (`call_site_wire_v1`); `gate_endurance_v1` (30 minutes, mouth closed, tick advanced); `gate_job_object_kill_path_v1` (identity-checked `TerminateJobObject` on an assigned tree; not the sole stop path; Toolhelp not retired); `gate_export_hash_parity_v1` (fail-closed receipt layer; decision stays **PRIVATE_AHEAD**); `gate_control_plane_resume_stop_watchdog_v1` (dual-bank record; `claim_wording` null; no CommandLine redact field). LOCKED: L7, LIVE_RSI, second clock, autonomy, public=plant, OS PID-number reuse observation, every future kill site, endurance beyond that window, publish sync without Denis GO, `soft_ACCEPT`. Scrubbed receipts in `measurements/public_index/`.
- **Public closeout 2026-09-22** ([docs/CLOSEOUT.md](docs/CLOSEOUT.md)): evidence index for the Talk Face cut. PASS: Standby (not Degraded) between ticks; Offline = mouth host unreachable; no visible `[MODEL_REASONING]` tag and absolute `/living/` cites rewritten or refused; direct-answer contract with Cover + Architect ACCEPT and `soft_ACCEPT=false`; canonical operator Desktop shortcut (single location; host path unpublished); windowed Edge launcher. LOCKED: dual-bank FULL_PROGRAM, `soft_ACCEPT` / LIVE_RSI / L7, Copilot as plant mouth, federation / swarm / autonomy theater, widen spawn wrap. Scrubbed receipts in `measurements/public_index/` (plant source paths omitted).
- **Campaign snapshot v1** (`scripts/campaign_snapshot.py`): after a green tick, tmp+replace `measurements/campaign_snapshot_v1.json` + measurements-set backup. `python -m aetheria recover` loads that file only (dead plant, hash fail = no spawn). `start`/`resume` no longer alias recover.
- **Mock public demo runtime** (`scripts/demo_runtime.py`, `python -m aetheria demo --cycles 3`): supervisor manages heartbeat/checkpoint/contract with no LLM
- **Sanitized sitting demo** ([docs/SANITIZED_DEMO.md](docs/SANITIZED_DEMO.md)): clocked organism on a private PC; plant ≠ chat; public vs private boundary; honest 2026-09 prototype status
- README / HIGH_LEVEL: mouth + plant picture; green interruptions vs dirty HOLD (no AUTORUN brownout)
- Arbitrary-path install: [docs/INSTALL.md](docs/INSTALL.md), `python -u scripts/aetheria.py init`, `requirements-dev.lock`
- Support/rollback/backup: [docs/SUPPORT.md](docs/SUPPORT.md)
- Frontier evolution instructions and research substrate (`research/`: schemas, five fixed ecologies, local benchmark, bounded population controller)
- Benchmark `local_deterministic_v2`: ecology-sensitive tasks (multi-doc, critic, early-stop, held-out). Comparison no longer ties 40/40.
- `research/elastic.py` bounded elastic population; `research/config/windows-local.json` measured ceilings (workers vs model-calls separate)
- `scripts/research_measure.py` local worker-scaling measurement (no plant, no network)
- Capability contract, maturity matrix, reference-task portfolio, promotion gates, vertical-slice-01 spec (not implemented)
- Vertical slice 01 implemented as local disposable experiment (`research/slices/vs01`); safe_refusal classifier + suite tasks
- Shared slice pipeline: clarification/refusal artifacts, vs02 MODE mission, capability-discovery harness, topology design note (not implemented)
- VS03: repair localized `add()` defect and generate a regression test from a failing assertion
- Communication-edge-only topology search (`research/topology.py`); no auto-promotion; model_calls=0
- `revision_after_critique` / `held_out_revision`: requires critic feedback edge; same roles, different wires, different scores
- VS04 real revision loop: first pass accepts a false claim, critic recomputes, feedback edge triggers a second pass; independent verify recomputes 2+2. Genome remains hold.
- Named research baseline `planner_executor_critic_feedback.json`; stock PEC kept; hold packet not promoted

### Added


- `scripts/lh_process_identity.py` — portable role matching; Windows PID-column liveness and identity-checked tree kill
- `scripts/plant_control.py` — operator stop/standby/halt/resume (stop now signals watchdog and reports survivors)
- `tests/test_lh_process_identity.py` (portable) and `tests/test_lh_process_windows.py` (Windows process fixtures)
- CI: pytest on Ubuntu; Windows job for process tests + launcher presence
- [docs/RELEASE_GATE.md](docs/RELEASE_GATE.md)

### Changed

- Stop contract: identity-checked `taskkill /PID /F /T` while supervisor is alive; recorded probe killed by probe identity; PID-only matches rejected; incomplete stop if allowlisted descendants remain
- Watchdog `diagnose`/`kill_pid` use verified supervisor identity (not PID-only)
- `status_report` orphan matcher includes `_lh_probe_` wrappers via the unified probe contract
- OPERATIONS / README: watchdog default is **manual-start latch**, not automatic segment relaunch; STOP files are graceful, not a tree guarantee
- **Sanitized public demo:** `scripts/demo_local_smoke.py`, `scripts/demo_local.ps1`, `Demo-Local.bat`, [docs/PUBLIC_DEMO.md](docs/PUBLIC_DEMO.md)
- README **Try the local demo** section (clone → smoke without private core)
- Operator hygiene PR propose path (dry-run default; human merge)
- **`scripts/launch_lh_detached.py`** — reliable detached LH launch (absolute Python; no Store-`python` hang)
- README / OPERATIONS: recovery path + pain table (session death, hang, thrash, plant≠chat)

### Changed

- Docs index links PUBLIC_DEMO + HYGIENE
- PUBLIC_DEMO / README: one-line optional `ollama pull qwen2.5:14b` (not required for smoke)
- `launch_long_horizon.ps1` prefers absolute Python310 + detached launcher
- Watchdog / plant_control resume use detached Python path (no 180s PowerShell wait hang)

## [0.3.1] - 2026-07-12

### Added

- `status_report` **segment vs campaign** progress block (avoids misreading PID/tick reset as wiped progress)
- Architecture / WHY notes: **plant clock != chat**; optional private companion stays out of this repo
- OPERATIONS: preferred one-screen status pulse and orphan reap caution

### Changed

- Control-plane scripts refreshed from operator tree with host absolute paths scrubbed
- README: explicit private-depth boundary (companion / generate not published)

### Security / privacy

- Continues policy: no private living streams, chat ownership, generative train stacks, or host paths in the public surface

## [0.3.0] — 2026-07-11

### Added

- **Cycle runner contract** documentation ([docs/CYCLE_RUNNER.md](docs/CYCLE_RUNNER.md))
- `measurements/lh_probe_summary.example.json` — structured completion schema
- Supervisor + hope-path consumers: env cycle count, summary dual-read, bounded finalize
- `status_report` / `resource_check`: related processes, orphan cycle workers, host RAM/CPU
- `--reap-orphans` for safe cleanup when the plant is not mid-tick
- `run_probe_bounded.py` — manual smokes with hard timeout (prevents host lag from orphans)

### Changed

- README rewritten for technical clarity and engagement (problem → architecture → features)
- Public language prefers **cycle runner / contract** over informal codenames
- Operator-facing strings scrubbed of host absolute paths and session-vendor specifics
- OPERATIONS: lag/orphan playbook; ARCHITECTURE: cycle boundary diagram section

### Fixed

- Class of failures where cycle work finished but child finalize hung unbounded (parent path)
- Class of host lag from orphan cycle processes while supervisor already idle

## [0.2.1] — 2026-07-11

### Added

- `docs/WHY.md` — problem, non-goals, success criteria (public “why”)  
- `scripts/status_report.py` — one-screen read-only plant/control-plane status  

### Changed

- README links WHY + status report in quick path  

## [0.2.0] — 2026-07-11

### Added

- Durable green-tick log for change-control Gate A (`gate_a_green_ticks.jsonl`), unioned with in-process history so process restarts do not erase progress  
- `verify_continuity_readonly.py` — read-only continuity audit (backups, resume shape, momentum carry, process liveness)  
- Example `measurements/gate_a_progress.example.json`  
- Rolling **segment** model documented as the default campaign unit  

### Changed

- Default / recommended `MaxTicks` **48** (was commonly documented as 96–200 single-PID heroics)  
- Watchdog relaunch: longer launcher timeout, **success = supervisor PID alive** (poll), default relaunch segment length 48  
- Supervisor records durable green ticks on successful ticks  
- Public docs rewritten as product descriptions (less operator-checklist dump, no host absolute paths)  
- Example handoff / resume templates aligned with segment defaults  

### Fixed

- False “relaunch failed” class of outcomes when the supervisor starts after a slow launcher return  

## [0.1.0] — 2026-07-10

### Added

- Initial public control plane: supervisor, watchdog, hope path, launch scripts  
- Architecture / operations docs, CONTRIBUTING, SECURITY, CI  
