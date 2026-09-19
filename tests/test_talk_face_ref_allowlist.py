# -*- coding: utf-8 -*-
"""Public Talk-face reference: allowlist + refuse + fail-closed confirm."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import living.talk_face_ref.server as srv


def _http(method: str, path: str, body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"http://127.0.0.1:{srv.PORT}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")


def test_talk_face_ref_allowlist_and_failclosed(monkeypatch):
    static = Path(__file__).resolve().parents[1] / "measurements" / "visual_refs" / "talk_face_v1"
    assert static.is_dir()
    monkeypatch.setattr(srv, "STATIC", static)
    httpd = srv.ThreadingHTTPServer((srv.HOST, srv.PORT), srv.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        code, st = _http("GET", "/api/status")
        assert code == 200 and st.get("flags", {}).get("plant_chat") == "BLOCKED"
        code, refused = _http("POST", "/api/turn", {"message": "enable plant_chat"})
        assert code == 403 and refused.get("ok") is False
        code, turn = _http("POST", "/api/turn", {"message": "hello"})
        assert code == 200 and turn.get("ok") is True
        code, bad = _http("POST", "/api/apply", {"confirm": False})
        assert code == 400 and bad.get("error") == "confirm_required"
        code, apply = _http("POST", "/api/apply", {"confirm": True})
        assert code == 400 and "fail_closed" in str(apply.get("error") or "")
    finally:
        httpd.shutdown()
