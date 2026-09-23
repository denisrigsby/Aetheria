# -*- coding: utf-8 -*-
"""Stranger / fresh-clone public verify for under_l7_continuous_live_v1."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    exp = json.loads((HERE / "EXPECTED_HASHES.json").read_text(encoding="utf-8"))
    fails = []
    for name, want in exp.get("files", {}).items():
        if name == "EXPECTED_HASHES.json":
            continue
        p = HERE / name
        if not p.exists():
            fails.append("missing:" + name)
            continue
        if sha256_file(p) != want:
            fails.append("hash_mismatch:" + name)
    tip = None
    prev = "0" * 64
    log = HERE / "events.jsonl"
    if not log.exists():
        fails.append("missing:events.jsonl")
    else:
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            body = {"kind": rec["kind"], "payload": rec["payload"], "soft_ACCEPT": False, "utc": rec["utc"]}
            raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
            eh = hashlib.sha256(raw).hexdigest()
            ch = hashlib.sha256((prev + eh).encode("utf-8")).hexdigest()
            if eh != rec.get("entry_hash") or ch != rec.get("chain_hash") or rec.get("prev_chain_hash") != prev:
                fails.append("chain_break:seq=%s" % rec.get("seq"))
                break
            prev = rec["chain_hash"]
            tip = prev
        if tip != exp.get("immutable_tip"):
            fails.append("tip_mismatch")
    if not (HERE / "PRIVATE_AHEAD.json").exists():
        fails.append("private_ahead_missing")
    ok = len(fails) == 0
    print(json.dumps({"pass": ok, "fails": fails, "tip": tip, "soft_ACCEPT": False}, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
