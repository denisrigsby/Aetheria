# -*- coding: utf-8 -*-
"""Public stranger verify for OEIG claim/invariant pack. soft_ACCEPT=false."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    here = Path(__file__).resolve().parent
    exp = json.loads((here / 'EXPECTED_HASHES.json').read_text(encoding='utf-8-sig'))
    fails = []
    for name in ['CLAIM_FROZEN.json', 'INVARIANT_BOUNDARIES.json', 'NONCLAIMS.json']:
        p = here / name
        if not p.exists():
            fails.append('missing:' + name)
            continue
        h = sha256_file(p)
        if h != exp.get(name):
            fails.append('hash_mismatch:' + name)
    claim = json.loads((here / 'CLAIM_FROZEN.json').read_text(encoding='utf-8-sig'))
    if claim.get('claim_frozen') != exp.get('claim_text'):
        fails.append('claim_text_mismatch')
    if claim.get('soft_ACCEPT') is not False:
        fails.append('soft_ACCEPT_not_false')
    out = {'pass': len(fails) == 0, 'fails': fails, 'soft_ACCEPT': False, 'checker': 'verify_oeig_public.py'}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not fails else 1

if __name__ == '__main__':
    raise SystemExit(main())
