# Talk-face — scrubbed safety mouth

Talk-face is a **localhost-only** HTML mouth between the operator and plant power.

## MUST NOT

- enable / call `plant_chat`
- enable / call `kit_act`
- silent disk write
- invent a second clock
- bypass typed apply / work watchdog / kit_pending brief

## API allowlist (localhost)

| Method | Path | Spine |
|--------|------|-------|
| POST | `/api/turn` | workbench turn |
| GET | `/api/status` | workbench status |
| GET | `/api/pending` | pending + instructional brief |
| POST | `/api/apply` | apply only with `confirm: true` |
| POST | `/api/open_forge` | spawn Forge TUI (new console) |

Bind: `127.0.0.1` only.

## Public reference demo

```powershell
python -u scripts/talk_face_ref_demo.py
```

This repo's reference Talk-face uses a **mock spine** so reviewers can exercise the mouth contract without private plant code.
