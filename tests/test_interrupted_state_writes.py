"""Interrupted control-plane writes publish the previous document or the new one.

A crash while the temporary file is being written must not leave a torn
document at the canonical path that parses as success. Same for a crash at
replace. Exclusions, named so the seal stays honest:

- PID files and STOP files are short in-place text, not JSON documents
- append-only JSONL and living streams are not document replacement
- ``research/`` experiment artifacts are outside this control plane
- the private plant is not this tree
"""
from __future__ import annotations

import builtins
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import atomic_state  # noqa: E402
from atomic_state import _atomic_replace_text, atomic_write_json  # noqa: E402

OLD = {"schema": "t_v1", "n": 1, "seq": 1}
NEW = {"schema": "t_v1", "n": 2, "seq": 2}
TORN = {"schema": "torn", "ok": True}


@contextmanager
def _interrupt_temp_write():
    real_open = builtins.open

    def boom(file, mode="r", *args, **kwargs):
        handle = real_open(file, mode, *args, **kwargs)
        if str(file).endswith(".tmp") and "w" in str(mode):
            real_write = handle.write

            def write(_data):
                real_write('{"schema":"torn","ok":true}')
                raise OSError("interrupted write")

            handle.write = write
        return handle

    builtins.open = boom
    try:
        yield
    finally:
        builtins.open = real_open


def _assert_unchanged(path: Path, raw: bytes) -> None:
    assert path.read_bytes() == raw
    got = json.loads(path.read_text(encoding="utf-8"))
    assert got != TORN
    assert got == json.loads(raw.decode("utf-8"))


def test_committed_write_is_the_new_document(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, OLD)
    atomic_write_json(target, NEW)
    assert json.loads(target.read_text(encoding="utf-8")) == NEW
    assert not list(tmp_path.glob("*.tmp"))


def test_interrupted_temp_write_keeps_previous_document(tmp_path: Path):
    target = tmp_path / "state.json"
    atomic_write_json(target, OLD)
    raw = target.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            atomic_write_json(target, NEW)
    _assert_unchanged(target, raw)
    torn = target.with_suffix(target.suffix + ".tmp")
    assert torn.is_file()
    assert json.loads(torn.read_text(encoding="utf-8")) == TORN
    assert json.loads(target.read_text(encoding="utf-8")) == OLD


def test_interrupted_create_does_not_publish_a_torn_document(tmp_path: Path):
    target = tmp_path / "state.json"
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            atomic_write_json(target, NEW)
    assert not target.exists()


def test_failed_replace_keeps_previous_document(tmp_path: Path, monkeypatch):
    target = tmp_path / "state.json"
    atomic_write_json(target, OLD)
    raw = target.read_bytes()

    def boom(_src, _dst):
        raise OSError("interrupted replace")

    monkeypatch.setattr(atomic_state.os, "replace", boom)
    with pytest.raises(OSError, match="interrupted replace"):
        atomic_write_json(target, NEW)
    _assert_unchanged(target, raw)


def test_fsync_happens_before_replace(tmp_path: Path, monkeypatch):
    order = []
    real_fsync = atomic_state.os.fsync
    real_replace = atomic_state.os.replace

    def fsync(fd):
        order.append("fsync")
        return real_fsync(fd)

    def replace(src, dst):
        order.append("replace")
        return real_replace(src, dst)

    monkeypatch.setattr(atomic_state.os, "fsync", fsync)
    monkeypatch.setattr(atomic_state.os, "replace", replace)
    atomic_write_json(tmp_path / "state.json", OLD)
    assert order == ["fsync", "replace"]


def test_text_replace_interrupt_keeps_previous_bytes(tmp_path: Path):
    target = tmp_path / "gate_a_green_ticks.jsonl"
    _atomic_replace_text(target, '{"n": 1}\n{"n": 2}\n')
    raw = target.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            _atomic_replace_text(target, '{"n": 3}\n')
    assert target.read_bytes() == raw
    lines = [ln for ln in target.read_text(encoding="utf-8").splitlines() if ln]
    assert [json.loads(ln)["n"] for ln in lines] == [1, 2]


def test_canonical_bytes_stable_while_temp_is_partial(tmp_path: Path, monkeypatch):
    target = tmp_path / "state.json"
    atomic_write_json(target, OLD)
    raw = target.read_bytes()
    seen = []
    real_open = builtins.open

    def boom(file, mode="r", *args, **kwargs):
        handle = real_open(file, mode, *args, **kwargs)
        if str(file).endswith(".tmp") and "w" in str(mode):
            real_write = handle.write

            def write(data):
                seen.append(target.read_bytes())
                if data:
                    real_write(data[:1])
                seen.append(target.read_bytes())
                raise OSError("interrupted write")

            handle.write = write
        return handle

    monkeypatch.setattr(builtins, "open", boom)
    with pytest.raises(OSError, match="interrupted write"):
        atomic_write_json(target, {"schema": "t_v1", "n": 2, "seq": 2, "pad": "z" * 400})
    assert seen == [raw, raw]
    _assert_unchanged(target, raw)


def test_plant_and_watchdog_writers_keep_previous(tmp_path: Path):
    import plant_control
    import lh_watchdog

    for write in (plant_control.write_json, lh_watchdog.write_json):
        target = tmp_path / f"{write.__module__}.json"
        write(target, OLD)
        raw = target.read_bytes()
        with _interrupt_temp_write():
            with pytest.raises(OSError, match="interrupted write"):
                write(target, NEW)
        _assert_unchanged(target, raw)


def test_plant_write_json_failed_replace_keeps_previous(tmp_path: Path, monkeypatch):
    import plant_control

    target = tmp_path / "state.json"
    plant_control.write_json(target, OLD)
    raw = target.read_bytes()

    def boom(_src, _dst):
        raise OSError("interrupted replace")

    monkeypatch.setattr(atomic_state.os, "replace", boom)
    with pytest.raises(OSError, match="interrupted replace"):
        plant_control.write_json(target, NEW)
    _assert_unchanged(target, raw)


def test_supervisor_state_and_resume_keep_previous(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AETHERIA_BIN_ROOT", str(tmp_path))
    import long_horizon_supervisor as lh

    state_path = tmp_path / "long_horizon_state.json"
    resume_path = tmp_path / "RESUME_STATE.json"
    monkeypatch.setattr(lh, "STATE_PATH", state_path)
    lh.write_state({"schema": "aetheria_long_horizon_state_v1", "tick": 1, "last_ok": True})
    state_raw = state_path.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            lh.write_state({"schema": "aetheria_long_horizon_state_v1", "tick": 9, "last_ok": False})
    _assert_unchanged(state_path, state_raw)
    assert json.loads(state_raw.decode("utf-8"))["tick"] == 1
    monkeypatch.setattr(lh, "STATE_PATH", ROOT / "measurements" / "long_horizon_state.json")
    monkeypatch.setattr(lh, "RESUME_PATH", resume_path)
    lh.write_resume({"tick": 1, "last_ok": True})
    resume_raw = resume_path.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            lh.write_resume({"tick": 9, "last_ok": False})
    _assert_unchanged(resume_path, resume_raw)


def test_campaign_snapshot_interrupt_keeps_previous(tmp_path: Path, monkeypatch):
    import campaign_snapshot as cs

    meas = tmp_path / "measurements"
    meas.mkdir()
    (meas / "gate_a_green_ticks.jsonl").write_text(
        '{"ts":"t","tick":1,"ok":true}\n', encoding="utf-8"
    )
    state = {
        "tick": 1,
        "last_ok": True,
        "status": "idle_between_ticks",
        "last_final_mom": 4,
        "last_tick_finished": "t",
        "heartbeat_at": "t",
    }
    assert cs.write_after_green_tick(state, tmp_path)["written"] is True
    snap = meas / "campaign_snapshot_v1.json"
    raw = snap.read_bytes()
    nxt = dict(state, tick=2, last_final_mom=9)
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            cs.write_after_green_tick(nxt, tmp_path)
    _assert_unchanged(snap, raw)
    assert json.loads(raw.decode("utf-8"))["segment"]["tick"] == 1


def test_demo_runtime_and_pulse_keep_previous(tmp_path: Path, monkeypatch):
    import demo_continuity
    import demo_runtime

    heartbeat = tmp_path / "demo_heartbeat.json"
    demo_runtime._write(heartbeat, {"schema": "aetheria_demo_heartbeat_v1", "cycle": 1})
    raw = heartbeat.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            demo_runtime._write(heartbeat, {"schema": "aetheria_demo_heartbeat_v1", "cycle": 2})
    _assert_unchanged(heartbeat, raw)

    pulse = tmp_path / "continuity_pulse.json"
    monkeypatch.setattr(demo_continuity, "PULSE", pulse)
    demo_continuity.write_pulse(1, True)
    raw = pulse.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            demo_continuity.write_pulse(2, False)
    _assert_unchanged(pulse, raw)
    assert json.loads(raw.decode("utf-8"))["tick"] == 1


def test_hope_status_interrupt_keeps_previous(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AETHERIA_BIN_ROOT", str(tmp_path))
    from living.aetheria_canon import write_hope_status

    path = write_hope_status({"schema": "aetheria_hope_status_v1", "phase": "first"}, merge=False)
    raw = path.read_bytes()
    with _interrupt_temp_write():
        with pytest.raises(OSError, match="interrupted write"):
            write_hope_status({"schema": "aetheria_hope_status_v1", "phase": "second"}, merge=False)
    _assert_unchanged(path, raw)
    assert json.loads(raw.decode("utf-8"))["phase"] == "first"


def test_green_log_trim_interrupt_keeps_complete_lines(tmp_path: Path, monkeypatch):
    import eval_residual_gate_v2 as gate

    log = tmp_path / "gate_a_green_ticks.jsonl"
    lines = [json.dumps({"ts": f"t{i}", "tick": i, "ok": True}) for i in range(800)]
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(gate, "GATE_A_LOG", log)
    with _interrupt_temp_write():
        gate.record_green_tick("t800", 800, True, pid=1)
    kept = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln]
    assert len(kept) == 801
    for ln in kept:
        assert json.loads(ln)["ok"] is True
    assert TORN not in [json.loads(ln) for ln in kept]


def test_control_plane_json_documents_use_the_atomic_helper():
    import re

    direct = re.compile(r"\.write_text\(\s*json\.dumps\(", re.S)
    bad = []
    paths = list((ROOT / "scripts").glob("*.py"))
    paths += list((ROOT / "living").rglob("*.py"))
    for path in paths:
        if path.name == "atomic_state.py":
            continue
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT))
        if direct.search(text):
            bad.append(rel)
        if 'with_suffix(".tmp")' in text or "with_suffix('.tmp')" in text:
            bad.append(rel + " local-tmp")
    assert bad == []
    required = {
        "scripts/plant_control.py": "atomic_write_json",
        "scripts/lh_watchdog.py": "atomic_write_json",
        "scripts/long_horizon_supervisor.py": "atomic_write_json",
        "scripts/campaign_snapshot.py": "atomic_write_json",
        "scripts/demo_runtime.py": "atomic_write_json",
        "scripts/demo_continuity.py": "atomic_write_json",
        "scripts/status_report.py": "atomic_write_json",
        "scripts/registry_hygiene.py": "atomic_write_json",
        "scripts/verify_continuity_readonly.py": "atomic_write_json",
        "scripts/run_probe_bounded.py": "atomic_write_json",
        "scripts/aetheria_hope_path.py": "atomic_write_json",
        "scripts/eval_residual_gate_v2.py": "_atomic_replace_text",
        "scripts/m6_thin_safeedit.py": "atomic_write_json",
        "scripts/research_measure.py": "atomic_write_json",
        "living/aetheria_canon.py": "atomic_write_json",
    }
    missing = [rel for rel, needle in required.items() if needle not in (ROOT / rel).read_text(encoding="utf-8")]
    assert missing == []
    gate = (ROOT / "scripts" / "eval_residual_gate_v2.py").read_text(encoding="utf-8")
    assert "GATE_A_LOG.write_text" not in gate
