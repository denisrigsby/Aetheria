# Witness concurrent OEIG + UL7C (20260923T161703Z)

1) **What was proved**
   Concurrent OEIG-live + UL7C-continuous proved on one control plane, with locks frozen, soft_ACCEPT false, UL7C apply held, and authority unchanged.
   Happy `concurrent_oeig_ul7c_20260923T153720Z`. Plant dual `DUAL_BANK_PROVE_CONCURRENT_OEIG_LIVE_UL7C @ 20260923T161118Z`.

2) **What stayed held**
   soft_ACCEPT=false. Apply held. UL7C apply held. L7 / rsi_level7 locked. may_auto_promote false. network_live false. Floor dual_bank false. Not Certified.

3) **What the hash/receipt says**
   Plant dual SHA-256 (unchanged): `bbcd205ff90f78d4fe78b02df1c4510e4b276695b8b49142ee975364b9f569f7`
   Scrubbed dual SHA-256: `9134c82ba1b3015e3a8b9b830831d4ee714c08e1f1721edbf40e4b7308c377a6`
   `scrubbed=true`. `public_equals_plant=false`. `export_parity=PRIVATE_AHEAD`.

4) **What outsiders can verify**
   - [dual_bank_prove_concurrent_oeig_ul7c.json](dual_bank_prove_concurrent_oeig_ul7c.json) — scrubbed concurrent dual
   - [support/](support/) — COVER + FLOOR_PROVE_PASS + SUMMARY + PROVE_RECEIPT + RECEIPT_AT_X1..X10 (scrubbed)
   - [INDEX_witness_concurrent_oeig_ul7c.json](INDEX_witness_concurrent_oeig_ul7c.json)
   - [MANIFEST_witness_concurrent_oeig_ul7c_20260923T161703Z.json](MANIFEST_witness_concurrent_oeig_ul7c_20260923T161703Z.json)
   Recompute SHA-256 of listed files; confirm locks soft_ACCEPT=false and apply/ul7c_apply held.

5) **What the next gate is**
   Cover PR ACCEPT + Architect PR ACCEPT on this public_index PR, then Floor squash-merge (same pattern as #39). Floor does not dual_bank. No apply / soft_ACCEPT / L7 / UL7C apply / canary / promote.
