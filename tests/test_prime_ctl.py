"""prime_ctl refusals exit 2 and spawn nothing. Allowed calls pass through."""
from __future__ import annotations

import sys

import prime_ctl


def _capture_spawn(monkeypatch):
    calls: list[list[str]] = []

    def fake(argv):
        calls.append(list(argv))
        if any(str(part).endswith("run_probe_bounded.py") for part in argv):
            return 7
        return 0

    monkeypatch.setattr(prime_ctl, "spawn", fake)
    return calls


def test_denied_verb_exits_2_and_spawns_nothing(monkeypatch):
    calls = _capture_spawn(monkeypatch)
    for verb in ("start", "resume", "init", "demo"):
        assert prime_ctl.main([verb]) == 2
        assert prime_ctl.main([verb, "--cycles", "1"]) == 2
    assert calls == []


def test_unknown_verb_exits_2_and_spawns_nothing(monkeypatch):
    calls = _capture_spawn(monkeypatch)
    assert "recover-ack" not in prime_ctl.VERBS
    assert prime_ctl.main(["recover-ack"]) == 2
    assert prime_ctl.main(["not-a-verb"]) == 2
    assert calls == []


def test_non_whitelisted_flag_exits_2_and_spawns_nothing(monkeypatch, capsys):
    calls = _capture_spawn(monkeypatch)
    assert prime_ctl.main(["gate", "--json"]) == 2
    assert prime_ctl.main(["prime.submit", "--authorize"]) == 2
    assert prime_ctl.main(["status.detailed", "--reap-orphans"]) == 2
    assert prime_ctl.main(["prime.submit", "--draft-id", "d1", "--authorize"]) == 2
    err = capsys.readouterr().err
    assert "denied flag --authorize" in err
    assert "denied flag --reap-orphans" in err
    assert calls == []


def test_measure_cycles_over_max_exits_2_and_spawns_nothing(monkeypatch):
    calls = _capture_spawn(monkeypatch)
    assert prime_ctl.MAX_CYCLES == 2
    assert prime_ctl.main(["measure", "--cycles", "3"]) == 2
    assert prime_ctl.main(["measure", "--cycles", "0"]) == 2
    assert prime_ctl.main(["measure", "--cycles", "two"]) == 2
    assert calls == []


def test_prime_draft_dash_positional_exits_2_and_spawns_nothing(monkeypatch, capsys):
    calls = _capture_spawn(monkeypatch)
    parsed = prime_ctl.parse_flags_then_positionals("prime.draft", ["-keep-out-of-flags"])
    assert isinstance(parsed, prime_ctl.Parsed)
    assert parsed.flags == ()
    assert parsed.positionals == ("-keep-out-of-flags",)
    assert prime_ctl.main(["prime.draft", "-keep-out-of-flags"]) == 2
    assert prime_ctl.main(["stop", "--reason", "-x"]) == 2
    err = capsys.readouterr().err
    assert "positional text must not start with '-'" in err
    assert calls == []


def test_allowed_call_passes_through(monkeypatch):
    calls = _capture_spawn(monkeypatch)
    assert prime_ctl.main(["measure", "--cycles", "2"]) == 7
    assert prime_ctl.main(["prime.draft", "local-first"]) == 0
    assert prime_ctl.main(["prime.draft"]) == 0
    assert prime_ctl.main(["prime.submit", "--draft-id", "d1"]) == 0

    measure, draft, stdin_draft, submit = calls
    assert measure[0] == sys.executable
    assert measure[1] == "-u"
    assert measure[2].endswith("run_probe_bounded.py")
    assert measure[-2:] == ["--cycles", "2"]
    assert draft[-2:] == ["draft", "local-first"]
    assert stdin_draft[-1] == "draft"
    assert stdin_draft[-2].endswith("prime_continuity.py")
    assert submit[-3:] == ["submit", "--draft-id", "d1"]

    interleaved = prime_ctl.parse_flags_then_positionals(
        "stop", ["please", "--reason", "now"]
    )
    assert isinstance(interleaved, prime_ctl.Parsed)
    assert interleaved.flags == (("--reason", "now"),)
    assert interleaved.positionals == ("please",)
    child = prime_ctl.child_argv("stop", interleaved)
    assert child.index("--reason") < child.index("please")
    assert prime_ctl.main(["stop", "please", "--reason", "now"]) == 2
    assert len(calls) == 4
