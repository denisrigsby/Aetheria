
# Localhost mouth: bind loopback only. Per-launch auth token = tracked gap (see RELEASE_GATE_ASSURANCE).
# -*- coding: utf-8 -*-
"""Localhost Talk-face reference server (mock spine). Public-safe demo."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "measurements" / "visual_refs" / "talk_face_v1"
HOST, PORT = "127.0.0.1", 8765
ALLOWLIST = ["/api/turn", "/api/status", "/api/pending", "/api/apply", "/api/open_forge"]
FLAGS = {"plant_chat": "BLOCKED", "kit_act": False}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_turn(msg: str) -> Dict[str, Any]:
    low = (msg or "").lower()
    if any(x in low for x in ("enable plant_chat", "enable plant chat", "enable kit_act", "enable kit act")):
        return {"ok": False, "error": "refused: plant_chat/kit_act not available via Talk-face", "ts": _utc(), "flags": dict(FLAGS)}
    return {
        "ok": True,
        "text": (
            "Talk-face reference mouth online (mock spine). "
            "Plant clock is not chat. "
            f"You said: {(msg or '')[:240]}"
        ),
        "ts": _utc(),
        "flags": dict(FLAGS),
        "source": "talk_face_ref_mock",
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        try:
            line = fmt % args
        except Exception:
            line = str(fmt)
        if "favicon.ico" in line:
            return
        sys.stderr.write("[talk_face_ref] " + line + "\n")

    def _json(self, code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/favicon.ico":
            svg = (
                b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
                b"<rect width='32' height='32' rx='8' fill='%2300d9a3'/>"
                b"<text x='16' y='22' text-anchor='middle' font-size='18' "
                b"font-weight='800' fill='%2304120e'>A</text></svg>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(svg)))
            self.end_headers()
            self.wfile.write(svg)
            return
        if path == "/api/status":
            self._json(200, {"ok": True, "text": "Talk-face reference · mock spine · plant_chat BLOCKED", "ts": _utc(), "flags": dict(FLAGS), "data": {"flags": dict(FLAGS), "mode": "reference_mock"}})
            return
        if path == "/api/pending":
            self._json(200, {"ok": True, "brief": "", "data": {}, "flags": dict(FLAGS), "ts": _utc()})
            return
        if path.startswith("/api/"):
            self._json(404, {"ok": False, "error": "unknown_api", "allowlist": ALLOWLIST})
            return
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/api/turn":
            out = _mock_turn(str(body.get("message") or body.get("text") or ""))
            code = 403 if out.get("ok") is False else 200
            self._json(code, out)
            return
        if path == "/api/apply":
            if not bool(body.get("confirm")):
                self._json(400, {"ok": False, "error": "confirm_required", "ts": _utc()})
                return
            self._json(400, {"ok": False, "error": "reference_stub_fail_closed: no disk write in public demo", "ts": _utc(), "flags": dict(FLAGS)})
            return
        if path == "/api/open_forge":
            self._json(200, {"ok": True, "text": "Reference stub: Open Forge would spawn the industrial TUI on a private plant. No Forge binary is bundled here.", "ts": _utc(), "flags": dict(FLAGS)})
            return
        self._json(404, {"ok": False, "error": "unknown_api", "allowlist": ALLOWLIST})


def main() -> int:
    if not STATIC.is_dir():
        print("missing static", STATIC, file=sys.stderr)
        return 2
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Talk-face REF http://{HOST}:{PORT}/  (localhost only, mock spine)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("bye", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
