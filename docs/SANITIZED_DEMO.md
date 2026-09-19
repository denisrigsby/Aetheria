# Sanitized demo (what a sitting should feel like)

**Purpose:** A rough, public picture of Aetheria as a **clocked organism on one private PC** â€” not a dump of the operator machine.

This is **not** the private Forge chat, living memory, host measurements, or model weights. Those stay on the operator box.

## One sitting

Aetheria is meant to feel like a **local admin and architect** of *this* computer:

1. You talk in ordinary language.
2. It knows the machine from host facts (not invented stats).
3. If you ask it to think, it judges *this* system.
4. The **clock** (detached ticks) is not the chat. Closing the window does not have to kill the room.
5. Writes wait for you unless they are an allowlisted leftover (a miss you already marked twice). Chat does not start the plant.

That is the demo to polish. Hardware and extra models are optional.

## Verify the supervisor (no LLM)

```powershell
python -m aetheria demo --cycles 3
```

The real supervisor drives a mock runtime: heartbeat, checkpoint, contract summary. No GPU, no keys.

## Clone smoke (this repo)

```powershell
git clone https://github.com/denisrigsby/Aetheria.git
cd Aetheria
python -u scripts/demo_local_smoke.py
```

Windows: `Demo-Local.bat`

**Expected:** Python check, compile, example JSON, **plant â‰  chat** banner.  
**Not expected:** multi-hour plant, companion UI, private memory.

See [PUBLIC_DEMO.md](PUBLIC_DEMO.md).

## What is public vs private

| Public (this repo) | Private (operator machine) |
|--------------------|----------------------------|
| Supervisor, watchdog, stop/status contracts | Living streams, Forge mouth, Ollama surface |
| Example measurement *shapes* | Live host state, chat logs, credentials |
| Docs: clock â‰  chat, recovery, conservation | Absolute paths, host names, personal notes |

## Law (sanitized)

- Chat never owns the plant PID.
- Unexpected death does not AUTORUN a brownout (HOLD until green).
- Green interruptions (sleep, a finished batch) may guardian-start; dirty `last_ok=false` stays parked.
- No Google-as-RAM. No whole-disk. No silent apply of new code.

## Honest status (2026-09)

Working prototype. The **body** (clock, gates, one GPU mutex, fail-closed facts) is real. The **face** is what a demo still polishes: stay with the question, no routing cards, no invented training loops.

Same organism on more iron would still be a clock + mouth, not a cloud chatbot with extra files.
