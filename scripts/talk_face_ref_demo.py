#!/usr/bin/env python3
"""Open the public Talk-face reference mouth (mock spine). Never starts a plant clock."""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST, PORT = "127.0.0.1", 8765
URL = f"http://{HOST}:{PORT}/"


def listening() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.4):
            return True
    except OSError:
        return False


def main() -> int:
    server = ROOT / "living" / "talk_face_ref" / "server.py"
    if not server.is_file():
        print("missing", server)
        return 2
    child = None
    child = None
    if not listening():
        child = subprocess.Popen([sys.executable, "-u", str(server)], cwd=str(ROOT))
        for _ in range(40):
            if listening():
                break
            if child.poll() is not None:
                return child.returncode or 1
            time.sleep(0.1)
        if not listening():
            print("did not bind", URL)
            return 1
    webbrowser.open(URL)
    print("Opened", URL)
    print("Mock spine only — plant clock is not involved.")
    if child is not None:
        try:
            child.wait()
        except KeyboardInterrupt:
            child.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
