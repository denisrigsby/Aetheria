# Discovery posts (ready to paste)

Honest, verifiable. Lead with the need. Link the continuity proof.

Repo: https://github.com/denisrigsby/Aetheria

---

## Show HN

**Title:** Show HN: Aetheria – local plant clock so AI work keeps going when chat dies

**Body:**

I built Aetheria because I was tired of long AI work dying when the chat window closed.

Aetheria is a local plant clock / control plane for serious AI work on Windows. Chat is a mouth you can open or close. The work clock is not the chat.

This repo is the public control-plane slice (supervisor, watchdog, stop/recover, Talk-face reference mouth). The private operator plant stays private by design.

One-minute proof (mock pulse + reference mouth — not the private plant):

    python -u scripts/demo_continuity.py

Open Talk-face, close it, watch the pulse keep advancing. That is plant clock ≠ chat.

Solo human–AI collaboration, built on Windows as a real operator machine.

https://github.com/denisrigsby/Aetheria

Happy to answer questions about the control-plane boundary and what stays private.

---

## Reddit (r/LocalLLaMA or similar)

**Title:** Aetheria – local plant clock for AI work that survives when chat dies (Windows, open control plane)

**Body:**

Problem I kept hitting: long local AI work tied to a chat/IDE session. Close the window, lose the run.

Aetheria is my answer: a local plant clock on Windows. Chat is an optional mouth. The plant keeps its own clock.

Public repo = control plane + a runnable continuity proof (mock pulse; not my private plant):

https://github.com/denisrigsby/Aetheria

```powershell
python -u scripts/demo_continuity.py
```

Close Talk-face → pulse still advances. That is the claim you can verify without trusting marketing.

Built solo with AI tools on a real Windows operator PC. Feedback welcome — especially from people running overnight / long-horizon local agents.
