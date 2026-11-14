#!/usr/bin/env python3
"""Client verb surface for the Aetheria control plane.

The plant clock is the long-horizon supervisor. This process is not that
clock: it never parents the supervisor, never listens on a socket, and never
loops. Refusals exit 2 before any child is spawned.

No in-repo draft or corrected parser existed (scripts/, docs/, tests/).
``parse_flags_then_positionals`` is the corrected parse for this contract:
long options are flags and consume their values first; every other token is
a positional; child argv is emitted flag+value, then positionals. A
positional that starts with '-' is refused (prime.draft stdin stays the
path for text that is not a safe positional).
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAX_CYCLES = 2

DENY_VERBS = frozenset({"start", "resume", "init", "demo"})
DENY_FLAGS = frozenset({"--authorize", "--reap-orphans"})


@dataclass(frozen=True)
class Verb:
    """One allowlisted dispatch. ``flags`` maps a flag to ``bool`` or ``value``."""

    script: str
    prefix: tuple[str, ...]
    flags: dict[str, str]
    max_positionals: int


VERBS: dict[str, Verb] = {
    "status": Verb("plant_control.py", ("status",), {"--json": "bool"}, 0),
    "status.detailed": Verb("status_report.py", (), {"--json": "bool"}, 0),
    "stop": Verb("plant_control.py", ("stop",), {"--reason": "value"}, 0),
    "recover": Verb("plant_control.py", ("recover",), {}, 0),
    "measure": Verb("run_probe_bounded.py", (), {"--cycles": "value"}, 0),
    "gate": Verb("eval_residual_gate_v2.py", (), {}, 0),
    "prime.draft": Verb("prime_continuity.py", ("draft",), {}, 1),
    "prime.analyze": Verb("prime_continuity.py", ("analyze",), {"--draft-id": "value"}, 0),
    "prime.submit": Verb("prime_continuity.py", ("submit",), {"--draft-id": "value"}, 0),
    "prime.checkpoint": Verb("prime_continuity.py", ("checkpoint",), {}, 0),
    "prime.handoff": Verb("prime_continuity.py", ("handoff",), {"--out": "value"}, 0),
    "prime.verify": Verb("prime_continuity.py", ("verify",), {}, 0),
}


@dataclass(frozen=True)
class Parsed:
    flags: tuple[tuple[str, str | None], ...]
    positionals: tuple[str, ...]


@dataclass(frozen=True)
class Refusal:
    reason: str


def _split_flag(token: str) -> tuple[str, str | None]:
    if token.startswith("--") and "=" in token[2:]:
        name, value = token.split("=", 1)
        return name, value
    return token, None


def parse_flags_then_positionals(verb: str, rest: list[str]) -> Parsed | Refusal:
    """Collect whitelist flags (and their values) before positionals.

    A long option is always a flag. Its value is the ``=`` payload or the
    next token, including a token that starts with '-'. A single-dash token
    is a positional, not a short flag. ``--`` ends flag parsing; the
    remainder are positionals.
    """
    spec = VERBS[verb]
    flags: list[tuple[str, str | None]] = []
    positionals: list[str] = []
    seen: set[str] = set()
    i = 0
    while i < len(rest):
        token = rest[i]
        if token == "--":
            positionals.extend(rest[i + 1 :])
            break
        if token.startswith("--"):
            name, inline = _split_flag(token)
            if name in DENY_FLAGS:
                return Refusal(f"denied flag {name}")
            kind = spec.flags.get(name)
            if kind is None:
                return Refusal(f"flag not allowed for {verb}: {name}")
            if name in seen:
                return Refusal(f"repeated flag {name}")
            seen.add(name)
            if kind == "bool":
                if inline is not None:
                    return Refusal(f"{name} takes no value")
                flags.append((name, None))
                i += 1
                continue
            if inline is None:
                if i + 1 >= len(rest):
                    return Refusal(f"{name} needs a value")
                inline = rest[i + 1]
                i += 2
            else:
                i += 1
            if inline == "" or inline.startswith("-"):
                return Refusal(f"{name} value must not start with '-'")
            flags.append((name, inline))
            continue
        positionals.append(token)
        i += 1
    for pos in positionals:
        head = pos.split("=", 1)[0]
        if head in DENY_FLAGS:
            return Refusal(f"denied flag {head}")
    return Parsed(tuple(flags), tuple(positionals))


def _refuse_positionals(verb: str, parsed: Parsed) -> Refusal | None:
    for pos in parsed.positionals:
        if pos.startswith("-"):
            return Refusal("positional text must not start with '-'")
    if len(parsed.positionals) > VERBS[verb].max_positionals:
        return Refusal(f"unexpected positional for {verb}")
    return None


def _refuse_measure_cycles(parsed: Parsed) -> Refusal | None:
    raw = None
    for name, value in parsed.flags:
        if name == "--cycles":
            raw = value
    if raw is None:
        return None
    try:
        cycles = int(raw, 10)
    except (TypeError, ValueError):
        return Refusal("measure --cycles needs an integer")
    if cycles < 1 or cycles > MAX_CYCLES:
        return Refusal(f"measure --cycles must be 1..{MAX_CYCLES}")
    return None


def child_argv(verb: str, parsed: Parsed) -> list[str]:
    """Flag+value tokens, then positionals. No shell."""
    spec = VERBS[verb]
    script = ROOT / "scripts" / spec.script
    argv = [sys.executable, "-u", str(script), *spec.prefix]
    for name, value in parsed.flags:
        argv.append(name)
        if value is not None:
            argv.append(value)
    argv.extend(parsed.positionals)
    return argv


def spawn(argv: list[str]) -> int:
    """Run one allowlisted child. Policy refusals must not call this."""
    completed = subprocess.run(argv, cwd=str(ROOT))
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("FAIL: verb required", file=sys.stderr)
        return 2
    verb = argv[0]
    rest = argv[1:]
    if verb in DENY_VERBS:
        print(f"FAIL: denied verb {verb}", file=sys.stderr)
        return 2
    if verb not in VERBS:
        print(f"FAIL: unknown verb {verb}", file=sys.stderr)
        return 2
    parsed = parse_flags_then_positionals(verb, rest)
    if isinstance(parsed, Refusal):
        print(f"FAIL: {parsed.reason}", file=sys.stderr)
        return 2
    positional_refusal = _refuse_positionals(verb, parsed)
    if positional_refusal is not None:
        print(f"FAIL: {positional_refusal.reason}", file=sys.stderr)
        return 2
    if verb == "measure":
        cycle_refusal = _refuse_measure_cycles(parsed)
        if cycle_refusal is not None:
            print(f"FAIL: {cycle_refusal.reason}", file=sys.stderr)
            return 2
    return spawn(child_argv(verb, parsed))


if __name__ == "__main__":
    raise SystemExit(main())
