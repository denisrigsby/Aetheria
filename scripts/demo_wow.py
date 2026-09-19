#!/usr/bin/env python3
"""Aetheria WOW demo (public / honest).

Shows the one thing people need to feel:
  the plant clock keeps ticking after the chat mouth closes.

This is a reference demo — mock plant pulse + Talk-face reference mouth.
It is NOT the private operator plant.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PULSE = ROOT / "measurements" / "demo_wow_pulse.json"
HOST, FACE_PORT, PULSE_PORT = "127.0.0.1", 8765, 8766
FACE_URL = f"http://{HOST}:{FACE_PORT}/"
STOP = threading.Event()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_pulse(tick: int, mouth_open: bool) -> None:
    PULSE.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema": "aetheria_demo_wow_pulse_v1",
        "demo": True,
        "private_plant": False,
        "tick": tick,
        "mouth_open": mouth_open,
        "claim": "plant clock != chat",
        "updated_at": utc(),
    }
    PULSE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def listening(port: int) -> bool:
    try:
        with socket.create_connection((HOST, port), timeout=0.2):
            return True
    except OSError:
        return False


class PulseHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/pulse":
            self.send_response(404)
            self.end_headers()
            return
        body = PULSE.read_bytes() if PULSE.is_file() else b"{}"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def plant_loop() -> None:
    tick = 0
    mouth = True
    while not STOP.is_set():
        # mouth_open flips false once Talk-face port is down after having been up
        if mouth and tick > 8 and not listening(FACE_PORT):
            mouth = False
        write_pulse(tick, mouth_open=mouth)
        tick += 1
        time.sleep(0.7)


def banner(lines) -> None:
    print()
    print("=" * 64)
    for line in lines:
        print(line)
    print("=" * 64)
    print()


def main() -> int:
    os.chdir(ROOT)
    banner(
        [
            "  AETHERIA  —  WOW DEMO (public reference)",
            "  Need: AI work that keeps going when chat dies.",
            "  Claim: plant clock != chat",
            "  This is a MOCK plant + Talk-face reference mouth.",
            "  Not the private operator plant.",
        ]
    )

    # Start pulse HTTP + plant loop
    write_pulse(0, mouth_open=True)
    pulse_httpd = ThreadingHTTPServer((HOST, PULSE_PORT), PulseHandler)
    threading.Thread(target=pulse_httpd.serve_forever, daemon=True).start()
    threading.Thread(target=plant_loop, daemon=True).start()

    # Start Talk-face reference
    face_proc = None
    if not listening(FACE_PORT):
        server = ROOT / "living" / "talk_face_ref" / "server.py"
        if not server.is_file():
            print("missing", server)
            return 2
        face_proc = subprocess.Popen([sys.executable, "-u", str(server)], cwd=str(ROOT))
        for _ in range(40):
            if listening(FACE_PORT):
                break
            if face_proc.poll() is not None:
                print("Talk-face failed to start")
                return 1
            time.sleep(0.1)

    print(f"[1/4] Plant pulse live  →  http://{HOST}:{PULSE_PORT}/pulse")
    print(f"[2/4] Opening Talk-face →  {FACE_URL}")
    webbrowser.open(FACE_URL)
    time.sleep(1.2)

    print("[3/4] WATCH THE CLOCK — ticks rise while the mouth is open.")
    for i in range(6):
        doc = json.loads(PULSE.read_text(encoding="utf-8"))
        print(f"      tick={doc['tick']:3d}  mouth_open={doc['mouth_open']}")
        time.sleep(0.7)

    banner(
        [
            "  >>> CLOSE THE TALK-FACE / BROWSER TAB NOW <<<",
            "  The wow is: ticks keep rising after the mouth is gone.",
            "  Waiting up to ~20s for the mouth port to drop...",
        ]
    )

    # Wait for user to close browser (port may stay up if server still running —
    # so we ALSO offer Enter to simulate mouth-closed by stopping Talk-face server)
    print("Press Enter after you close the tab (or to force-stop the Talk-face server)...")
    try:
        input()
    except EOFError:
        pass

    if face_proc is not None and face_proc.poll() is None:
        face_proc.terminate()
        try:
            face_proc.wait(timeout=3)
        except Exception:
            face_proc.kill()

    # Force mouth_open false in pulse for clarity even if something else holds 8765
    deadline = time.time() + 12
    while time.time() < deadline:
        doc = json.loads(PULSE.read_text(encoding="utf-8"))
        # rewrite with mouth closed for the demo beat
        write_pulse(int(doc["tick"]), mouth_open=False)
        print(f"      tick={doc['tick']:3d}  mouth_open=False   ← plant still alive")
        time.sleep(0.7)

    banner(
        [
            "  WOW BEAT COMPLETE",
            "  Mouth closed. Plant pulse still advancing.",
            "  That is Aetheria: chat is a mouth; the work clock is not the chat.",
            f"  Pulse file: {PULSE}",
            "  Try: curl http://127.0.0.1:8766/pulse",
        ]
    )
    STOP.set()
    pulse_httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
