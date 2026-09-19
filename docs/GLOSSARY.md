# Glossary (Aetheria → plain technical)

Keep the voice. Use this table when reading public docs.

| Aetheria term | Plain technical equivalent |
|---------------|----------------------------|
| **Plant clock** | Detached supervised job runtime |
| **Mouth / Talk-face** | Optional local chat or operator UI |
| **Forge** | Private operator console |
| **Tick / cycle** | One bounded unit of agent work |
| **HOLD** | Fail-closed paused state pending operator action |
| **Supervisor** | Process that owns the long-running work loop |
| **Watchdog** | Side process that relaunches the supervisor if it dies |
| **STOP** | Explicit request to terminate the process tree |
| **Measurements** | On-disk status / heartbeat / checkpoint artifacts |
| **Living memory** | Private durable operator memory (not in this public repo) |

Public claim in one sentence: **agent reliability is an operations and process-supervision problem**, not another chat framework.
