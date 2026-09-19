# Threat model (concise)

## Assets

- Control-plane correctness (who is the supervisor / worker)
- On-disk campaign state under `measurements/`
- Operator machine integrity (do not kill unrelated processes)
- Localhost Talk-face as an optional UI mouth

## Adversaries / faults

- PID reuse after crash
- Power loss mid-write
- Concurrent CLI controllers
- Local process replacing snapshot + digest
- Malicious or buggy localhost clients on loopback

## Non-goals (public repo)

- Protecting against a fully compromised local admin
- Shipping the private operator plant
- Multi-tenant remote security

## Mitigations (current)

- Fail-closed HOLD after dirty death
- Identity-checked role matching before stop/adopt
- Atomic replace for state helpers
- Loopback bind for Talk-face reference
- Claims taxonomy so mock ≠ production plant
