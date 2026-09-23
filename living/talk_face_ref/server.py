"""Localhost Talk-face reference server (mock spine). Public-safe demo.

Hardening:
- loopback bind only
- per-launch auth token required for state-changing POSTs
- MAX_BODY request size limit
- no state-changing GET
"""
from __future__ import annotations

import json
import secrets
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "measurements" / "visual_refs" / "talk_face_v1"
HOST = "127.0.0.1"
PORT = 8765
MAX_BODY = 256_000
FLAGS = {"plant_chat": "BLOCKED", "kit_act": False}

# Set by make_server_with_token / main
LAUNCH_TOKEN: Optional[str] = None


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_turn(msg: str) -> Dict[str, Any]:
    text = (
        "Talk-face reference mouth online (mock spine). "
        "plant_chat BLOCKED; kit_act false. "
        f"Echo: {msg[:200]}"
    )
    return {"ok": True, "text": text, "ts": _utc(), "flags": dict(FLAGS), "source": "talk_face_ref_mock"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        sys.stderr.write("[talk_face_ref] " + (fmt % args) + "\n")

    def _json(self, code: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _token_ok(self) -> bool:
        if not LAUNCH_TOKEN:
            return True
        return self.headers.get("X-Aetheria-Token") == LAUNCH_TOKEN

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/api/status", "/api/pending"):
            if path == "/api/status":
                self._json(200, {"ok": True, "ts": _utc(), "flags": dict(FLAGS), "data": {"flags": dict(FLAGS), "mode": "reference_mock"}})
            else:
                self._json(200, {"ok": True, "ts": _utc(), "data": {}, "brief": "No staged write (mock)." })
            return
        if path == "/api/token":
            # Intentionally not exposing token over GET in hardened mode
            self._json(404, {"ok": False, "error": "token_not_via_get"})
            return
        # static
        if path == "/":
            path = "/index.html"
        target = (STATIC / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
            self.send_error(404)
            return
        data = target.read_bytes()
        ctype = "text/html" if target.suffix == ".html" else "application/octet-stream"
        if target.suffix == ".js":
            ctype = "application/javascript"
        elif target.suffix == ".css":
            ctype = "text/css"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self._json(413, {"ok": False, "error": "body_too_large"})
            return
        if not self._token_ok():
            self._json(401, {"ok": False, "error": "unauthorized", "hint": "X-Aetheria-Token required for POST"})
            return
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}
        if path == "/api/turn":
            msg = str(body.get("message") or body.get("text") or "")
            self._json(200, _mock_turn(msg))
            return
        if path == "/api/apply":
            self._json(200, {"ok": False, "error": "need_brief", "text": "Mock fail-closed confirm (need_brief).", "ts": _utc(), "flags": dict(FLAGS)})
            return
        self._json(404, {"ok": False, "error": "unknown_api"})


def make_server_with_token(host: str = HOST, port: int = PORT) -> Tuple[ThreadingHTTPServer, str]:
    global LAUNCH_TOKEN
    LAUNCH_TOKEN = secrets.token_urlsafe(24)
    httpd = ThreadingHTTPServer((host, port), Handler)
    return httpd, LAUNCH_TOKEN


def main() -> int:
    global LAUNCH_TOKEN
    httpd, token = make_server_with_token(HOST, PORT)
    print(f"Talk-face REF http://{HOST}:{httpd.server_address[1]}/  (localhost only, mock spine)", flush=True)
    print(f"POST requires header X-Aetheria-Token: {token}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
