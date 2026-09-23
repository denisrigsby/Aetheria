# Witness governed runtime NR (NR1-NR6) — 20260923T175546Z

1) **What was proved**
   Operator-proven governed runtime (NR1-NR6): non-chat control-plane job, persistence across restart, same capability/policy via chat and non-chat, fail-closed unauthorized, receipt-backed completion, one-command repeatable Windows CI PASS - soft_ACCEPT false; Not Certified.
   Happy `nr_governed_runtime_20260923T035912Z`. Plant dual status `DUAL_ACCEPT_GOVERNED_RUNTIME_NR_PROVE`.

2) **What stayed held**
   soft_ACCEPT=false. Apply held. Canary held. L7 / rsi_level7 locked. may_auto_promote false. network_live false. Floor dual_bank false. Not Certified. Publication blocked until later gates.

3) **What the hash/receipt says**
   Plant dual SHA-256 (unchanged): `fd0d96ca1a411f29e4143d036c9001670f78fc78ae0106a2618bd305cba22edb`
   Scrubbed dual SHA-256 (disk bytes): `c12bf86fb62e7136f99b5a77ca28d1e271e77a4ed64f1b404b6cccaa95c1853b`
   Pack dual_accept prior thin SHA (reference): `e0c3d4a6cacc1c3f82474b4d7c6309bc69434a692914ec0bc9c7bc2f9e0e93c3`
   CI artifact SHA (from card): `7254565e6423d8c3af401da9ab8349f003702c88893dc4d444b4b3b3979d42f9`
   `scrubbed=true`. `public_equals_plant=false`. `export_parity=PRIVATE_AHEAD`. NR1-NR6 all PASS.
   Remediates Cover HOLD_WITNESS_SCRUB_GOVERNED_RUNTIME_NR @ 20260923T175135Z (AT-W1 hash bind + AT-W7 tNNNNu residual).

4) **What outsiders can verify**
   - [dual_accept_governed_runtime_nr_prove.json](dual_accept_governed_runtime_nr_prove.json) — scrubbed dual_accept + plant hash bind
   - [support/](support/) — COVER / ARCHITECT / CI_WITNESS / PROVE_RECEIPT / AT_RESULTS / PROVE_PASS / GATE (scrubbed)
   - [happy/](happy/) — NR1 / NR2 / NR5 receipts + NR3/NR4 bind summary (scrubbed)
   - [INDEX_witness_governed_runtime_nr.json](INDEX_witness_governed_runtime_nr.json)
   - [MANIFEST_witness_governed_runtime_nr_20260923T175546Z.json](MANIFEST_witness_governed_runtime_nr_20260923T175546Z.json)
   Recompute SHA-256 of listed files from disk bytes; confirm soft_ACCEPT=false; CI_WITNESS github_hosted=false returncode 0; no tNNNNu / home paths.

5) **What the next gate is**
   Cover ACCEPT then Architect dual-bank on WITNESS_SCRUB_EXPORT_GOVERNED_RUNTIME_NR before public_index PR merge. Floor does not dual_bank. No apply / soft_ACCEPT / L7 / canary / promote. Canary stays held until PR clean.
