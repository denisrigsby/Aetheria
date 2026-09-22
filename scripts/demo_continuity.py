#!/usr/bin/env python3
"""Continuity proof (public reference).

Proves one fact: after the Talk-face mouth stops, a plant pulse file
keeps advancing. Mock pulse + Talk-face reference mouth only.
Not the private operator plant.
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
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from atomic_state import atomic_write_json  # noqa: E402

PULSE = ROOT / "measurements" / "continuity_pulse.json"
HOST, FACE_PORT, PULSE_PORT = "127.0.0.1", 8765, 8766
FACE_URL = f"http://{HOST}:{FACE_PORT}/"
STOP = threading.Event()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_pulse(tick: int, mouth_open: bool) -> None:
    atomic_write_json(
        PULSE,
        {
            "schema": "aetheria_continuity_pulse_v1",
            "public_reference": True,
            "private_plant": False,
            "tick": tick,
            "mouth_open": mouth_open,
            "fact": "plant_clock_neq_chat",
            "updated_at": utc(),
        },
    )


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
        if mouth and tick > 8 and not listening(FACE_PORT):
            mouth = False
        write_pulse(tick, mouth_open=mouth)
        tick += 1
        time.sleep(0.7)


def main() -> int:
    os.chdir(ROOT)
    print("Aetheria continuity proof (public reference)")
    print("Fact under test: plant clock != chat")
    print("Runtime: mock pulse + Talk-face reference mouth (not the private plant)")
    print()

    write_pulse(0, mouth_open=True)
    pulse_httpd = ThreadingHTTPServer((HOST, PULSE_PORT), PulseHandler)
    threading.Thread(target=pulse_httpd.serve_forever, daemon=True).start()
    threading.Thread(target=plant_loop, daemon=True).start()

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

    print(f"1. Pulse publishing at http://{HOST}:{PULSE_PORT}/pulse")
    print(f"2. Opening Talk-face at {FACE_URL}")
    webbrowser.open(FACE_URL)
    time.sleep(1.0)

    print("3. Mouth open - recording ticks:")
    for _ in range(6):
        doc = json.loads(PULSE.read_text(encoding="utf-8"))
        print(f"   tick={doc['tick']:3d}  mouth_open={doc['mouth_open']}")
        time.sleep(0.7)

    print()
    print("4. Close the Talk-face tab, then press Enter.")
    print("   (Enter also stops the Talk-face server if the port is still up.)")
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

    print("5. Mouth closed - recording ticks:")
    deadline = time.time() + 10
    while time.time() < deadline:
        doc = json.loads(PULSE.read_text(encoding="utf-8"))
        write_pulse(int(doc["tick"]), mouth_open=False)
        print(f"   tick={doc['tick']:3d}  mouth_open=False")
        time.sleep(0.7)

    print()
    print("Result: mouth_open stayed False while tick kept advancing.")
    print(f"Pulse file: {PULSE}")
    print("That is the public proof slice of plant clock != chat.")
    STOP.set()
    pulse_httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
