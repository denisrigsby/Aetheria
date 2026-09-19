# Atomic on-disk state (measurements protocol)

Authoritative control-plane files under `measurements/` must not tear across power loss.

## Required write pattern

1. Write to a **same-directory** temporary file (`*.tmp`)
2. `flush` + `fsync` (or platform equivalent) when available
3. **Atomic replace** onto the target name
4. **Schema / version** validation on read
5. Prefer **single-writer** discipline; document multi-writer as unsafe
6. Prefer **monotonic sequence** fields in JSON status docs when updating ticks

## Integrity vs authenticity

SHA-256 (or similar) over snapshot bodies is an **integrity checksum** against accidental corruption.
It is **not** authentication. A local attacker can replace both body and digest.
Do not describe digests as a security boundary unless an HMAC with a protected local key is implemented (**not** claimed in public today).

## Tests

See `tests/test_atomic_state_writes.py`.
