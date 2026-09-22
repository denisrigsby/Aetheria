# Market pain this control plane targets

User and open-source issue language (Ollama, Open WebUI, CrewAI, LangGraph, Reddit/HN) clusters around:

| Pain | Control plane answer |
|------|----------------------|
| Hang / stuck / timeout | Hard timeouts, STOP files, status/orphan tools |
| Session death / no resume | Detached supervisor + watchdog + on-disk state |
| Overnight / multi-hour babysitting | Rolling ticks/segments and green-tick logs are the design. The indexed plant window is 30 minutes (`gate_endurance_v1`). Longer stays locked |
| Runaway loops | max_ticks, bounded runners |
| Fake-local surprises | This repo is local control plane; cloud not required |

**Job #1:** run the smoke in the README. Smoke is **Real**. It is not an assurance PASS. See README.

This is **not** a multi-agent chat framework and not a hosted multi-tenant SaaS.
