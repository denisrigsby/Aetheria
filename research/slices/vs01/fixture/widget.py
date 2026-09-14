"""Disposable fixture module. LABEL is the only intended edit target."""

LABEL = "alpha"


def greet() -> str:
    return f"hello {LABEL}"


def ping() -> str:
    return "pong"
