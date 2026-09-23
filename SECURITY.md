# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| `main` branch public control plane | Yes (best-effort) |
| Private operator plant | Not in scope of this repository |

## Reporting a vulnerability

**Do not file public GitHub issues for security reports.**

Please email **denisrigsby@users.noreply.github.com** with subject `Aetheria security` (or use GitHub Security Advisories / private vulnerability reporting on this repository when enabled).

Include: affected commit/version, reproduction steps, impact, and whether a public PoC exists.

## Response window (best-effort)

- Acknowledgement: within **7 days**
- Initial severity assessment: within **14 days**
- Fix or mitigation plan for accepted reports: as soon as practical for a solo maintainer

## Disclosure

We prefer coordinated disclosure. Please allow a reasonable window after a fix lands on `main` before public write-ups.

## Scope notes

- Localhost Talk-face is a **local UI mouth**, not a remote multi-tenant service.
- Snapshot digests in this repo are **integrity checksums**, not authentication.
- Process stop/recover must be **identity-checked**; PID-alone kill is a defect.
