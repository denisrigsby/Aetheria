# Arbitrary-path installation

The scripts and research substrate can be checked out in **any directory**. They do not require a developer home path, a nested clone, or a pre-existing `.venv`. That is a path layout. It is not a portable stop or relaunch.

## Supported

- Python 3.10, 3.11, or 3.12
- Windows 10/11 is the reference OS for stop, tree-kill, Job Object, and relaunch.
- Ubuntu CI runs role-matching tests. Those tests are not a tree-kill and not a relaunch.
- Tree-kill and Job Object stop are **Proved on Windows** only where a receipt says so, and **Locked on non-Windows**.

## Install

```text
git clone https://github.com/denisrigsby/Aetheria.git aetheria
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
