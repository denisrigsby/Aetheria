# Discovery posts (ready to paste)

Honest, verifiable. Lead with the need. Link the mock continuity check, and name the 30-minute plant receipt when you mean the operator machine.

Repo: https://github.com/denisrigsby/Aetheria

---

## Show HN

**Title:** Show HN: Aetheria – local plant clock so AI work keeps going when chat dies

**Body:**

I built Aetheria because I was tired of long AI work dying when the chat window closed.

Aetheria is a local plant clock / control plane for AI work on Windows. Chat is a mouth you can open or close. The work clock is not the chat.

This repo is the public control-plane slice (supervisor, watchdog, stop/recover, Talk-face reference mouth). The private operator plant stays private by design. Public export ≠ live plant (PRIVATE_AHEAD).

One-minute check you can run here (mock pulse + reference mouth — not the private plant, not an overnight proof):

    python -u scripts/demo_continuity.py

Open Talk-face, close it, watch the pulse keep advancing. That is the mock slice of plant clock ≠ chat. The indexed operator-plant window is 30 minutes (gate_endurance_v1). Longer than that is not claimed.

Solo human–AI collaboration, Denis Rigsby, built on Windows as the operator machine. P1–P5 on that machine are internal certification, not an outside audit.

https://github.com/denisrigsby/Aetheria

Happy to answer questions about the control-plane boundary and what stays private.

---

## Reddit (r/LocalLLaMA or similar)

**Title:** Aetheria – local plant clock for AI work that survives when chat dies (Windows, open control plane)

**Body:**

Problem I kept hitting: long local AI work tied to a chat/IDE session. Close the window, lose the run.

Aetheria is my answer: a local plant clock on Windows. Chat is an optional mouth. The plant keeps its own clock.

Public repo = control plane + a runnable mock continuity check (not my private plant, not an overnight proof):

https://github.com/denisrigsby/Aetheria

```powershell
python -u scripts/demo_continuity.py
```

Close Talk-face → the mock pulse still advances. That is the claim you can run here. The plant receipt I will stand behind in the repo is the 30-minute gate, with its exclusions in the evidence index.

Built solo with AI tools on my Windows operator PC. Feedback welcome — especially from people running long-horizon local agents. I am not calling this production-ready.
