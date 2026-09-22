# Export parity (local stage)

**Decision:** PRIVATE_AHEAD  
**public = plant:** false (locked)

This tree is a curated public control-plane export. It is **not** a byte-for-byte copy of the live operator plant.

`gate_export_hash_parity_v1` is dual-banked (`dual_bank=true`, Cover ACCEPT, Architect ACCEPT, `soft_ACCEPT=false`).

Claim, as the receipt words it: Export hash/parity receipt layer as defined by `gate_export_hash_parity_v1`: fail-closed census of public export paths vs plant counterparts with per-path hashes and an explicit decision (`PARITY_PASS` or `PRIVATE_AHEAD`); `public_equals_plant` is true only when decision is `PARITY_PASS`.

This receipt's decision is **PRIVATE_AHEAD**. `public_equals_plant` stays false.

Exclusions beside that claim: `public_equals_plant` without `PARITY_PASS`; the export is not the full plant; the full-program claim does not include export parity; publish sync without Denis GO; second clock; autonomy; LIVE_RSI; L7.

- Do not claim the GitHub tree equals the live plant.
- No receipt for `gate_full_program_asset_class_v1` is in this index. That name is not a public proof. Export parity is the receipt above, and its decision is **PRIVATE_AHEAD**.
- Remote push of a plant sync requires a separate Denis GO. This index does not grant that GO.

Receipt: [gate_export_hash_parity_v1_79b2.json](../measurements/public_index/gate_export_hash_parity_v1_79b2.json).

See [FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md) and [CLOSEOUT.md](CLOSEOUT.md).
