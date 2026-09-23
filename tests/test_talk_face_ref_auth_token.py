"""Per-launch auth token for Talk-face reference server."""
from __future__ import annotations

import importlib.util
import json
import threading
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_server():
    path = ROOT / "living" / "talk_face_ref" / "server.py"
    spec = importlib.util.spec_from_file_location("talk_face_ref_server", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_state_changing_post_requires_token_when_enabled(tmp_path, monkeypatch):
    mod = _load_server()
    if not hasattr(mod, "make_server_with_token"):
        # Older server without helper — skip soft? fail to force wiring
        assert hasattr(mod, "make_server_with_token"), "server must expose make_server_with_token"
    httpd, token = mod.make_server_with_token(host="127.0.0.1", port=0)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        conn = HTTPConnection("127.0.0.1", port, timeout=3)
        # GET status may be open or token-gated; POST apply/turn must require token
        body = json.dumps({"message": "hi"}).encode()
        conn.request("POST", "/api/turn", body=body, headers={"Content-Type": "application/json"})
        r = conn.getresponse()
        assert r.status in (401, 403)
        r.read()
        conn.close()
        conn = HTTPConnection("127.0.0.1", port, timeout=3)
        conn.request(
            "POST",
            "/api/turn",
            body=body,
            headers={"Content-Type": "application/json", "X-Aetheria-Token": token},
        )
        r2 = conn.getresponse()
        assert r2.status == 200
        r2.read()
        conn.close()
    finally:
        httpd.shutdown()
