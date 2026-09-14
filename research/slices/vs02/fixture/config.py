"""Disposable parser/config fixture. MODE is the edit target; MAX/parse must stay."""

MODE = "strict"
MAX = 3


def parse(line: str) -> list:
    return [p.strip() for p in line.split(",") if p.strip()]
