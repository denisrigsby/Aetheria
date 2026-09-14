# Arbitrary-path installation

The control plane and research substrate run from **any directory**. They do not require a developer home path, a nested clone, or a pre-existing `.venv`.

## Supported

- Python 3.10, 3.11, or 3.12
- Windows 10/11 (reference). POSIX: identity matching is portable; process tree-kill tests are Windows-only.

## Install

```text
git clone https://github.com/denisrigsby/Aetheria-sovereign-agent.git aetheria
cd aetheria
python -m pip install -r requirements-dev.lock
python -u scripts/aetheria.py init
python -u scripts/aetheria.py help
python -m pytest tests/test_lh_process_identity.py tests/test_arbitrary_path.py tests/test_failure_recovery.py tests/test_research_substrate.py -q
```

Runtime of `scripts/aetheria.py` and `research/` is **stdlib only**. `requirements-dev.lock` pins **pytest** for tests.

## Initialize

`init` creates `measurements/` (operational state) and `research/runs/` (disposable experiment roots). It does not start the plant, contact the network, or read credentials.

## Uninstall / reset

Delete the clone directory. To reset state only: delete `measurements/*.pid`, `measurements/*STOP`, and `research/runs/*` (keep `*.example.json`).

## Not required

Cloud keys, Ollama, companion, living memory, or the operator production tree.
