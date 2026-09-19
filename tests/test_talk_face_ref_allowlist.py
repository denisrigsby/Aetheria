"""Allowlist / refuse / fail-closed for Talk-face reference server."""
from __future__ import annotations

import importlib.util
import json
import threading
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "living" / "talk_face_ref" / "server.py"
    spec = importlib.util.spec_from_file_location("tfr", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_talk_face_ref_allowlist_and_failclosed():
    mod = _load()
    httpd, token = mod.make_server_with_token(host="127.0.0.1", port=0)
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    try:
        c = HTTPConnection("127.0.0.1", port, timeout=5)
        c.request("GET", "/api/status")
        r = c.getresponse(); body = json.loads(r.read().decode())
        assert r.status == 200 and body.get("flags", {}).get("plant_chat") == "BLOCKED"
        c.close()
        # POST without token → 401
        c = HTTPConnection("127.0.0.1", port, timeout=5)
        raw = json.dumps({"message": "/status"}).encode()
        c.request("POST", "/api/turn", body=raw, headers={"Content-Type": "application/json"})
        r = c.getresponse(); r.read()
        assert r.status == 401
        c.close()
        # POST with token → 200
        c = HTTPConnection("127.0.0.1", port, timeout=5)
        c.request(
            "POST",
            "/api/turn",
            body=raw,
            headers={"Content-Type": "application/json", "X-Aetheria-Token": token},
        )
        r = c.getresponse(); body = json.loads(r.read().decode())
        assert r.status == 200 and body.get("ok") is True
        c.close()
        # apply fail-closed
        c = HTTPConnection("127.0.0.1", port, timeout=5)
        c.request(
            "POST",
            "/api/apply",
            body=b"{"confirm": true}",
            headers={"Content-Type": "application/json", "X-Aetheria-Token": token},
        )
        r = c.getresponse(); body = json.loads(r.read().decode())
        assert body.get("error") == "need_brief" or body.get("ok") is False
        c.close()
    finally:
        httpd.shutdown()
