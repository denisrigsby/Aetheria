# Sanitized demo (what a sitting should feel like)

**Purpose:** A rough, public picture of Aetheria as a local supervisor on one private PC. This page is not a dump of the operator machine, and it is not a proof.

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

The supervisor in this repo drives a mock runtime: heartbeat, checkpoint, contract summary. No GPU, no keys. That command is a local demo. It is not an assurance PASS.

## Clone smoke (this repo)

```powershell
git clone https://github.com/denisrigsby/Aetheria.git
cd Aetheria
python -u scripts/demo_local_smoke.py
```

Windows: `Demo-Local.bat`

**Expected:** Python check, compile, example JSON, **plant ≠ chat** banner.  
**Not expected:** multi-hour plant, companion UI, private memory.

See [PUBLIC_DEMO.md](PUBLIC_DEMO.md).

## What is public vs private

| Public (this repo) | Private (operator machine) |
|--------------------|----------------------------|
| Supervisor, watchdog, stop/status contracts | Living streams, Forge mouth, Ollama surface |
| Example measurement *shapes* | Live host state, chat logs, credentials |
| Docs: clock ≠ chat, recovery, conservation | Absolute paths, host names, personal notes |

## Intended rules (sanitized)

These are the rules the design aims at. They are not a checklist PASS.

- Chat does not own the plant PID. The mock demo and the 30-minute endurance receipt are the indexed evidence. [../FINAL_STATE_BRIEF.md](../FINAL_STATE_BRIEF.md)
- Unexpected death is not supposed to AUTORUN. Clean stop ≠ crash stays **PARTIAL**.
- Dirty `last_ok=false` is supposed to stay parked. Full HOLD wiring stays **PARTIAL**.
- No Google-as-RAM. No whole-disk. No silent apply of new code. Gated self-modification is **Locked**.

## Status

Use the four labels on [../README.md](../README.md). This page does not add a GPU mutex, a "body is real" claim, or a production-ready claim. The face of a sitting demo (stay with the question, no routing cards, no invented training loops) is polish, not a gate.

The same clock-and-mouth split on more hardware would still be that split. It would not become a cloud chatbot, and it would not become enterprise-grade.
