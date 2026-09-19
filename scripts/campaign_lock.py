"""Cross-process campaign lock (best-effort single writer)."""
from __future__ import annotations

import os
import time
from pathlib import Path


class CampaignLock:
    def __init__(self, path: Path, timeout_s: float = 2.0):
        self.path = Path(path)
        self.timeout_s = timeout_s
        self._fd = None
        self.acquired = False

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + self.timeout_s
        while time.time() < deadline:
            try:
                self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, str(os.getpid()).encode())
                self.acquired = True
                return True
            except FileExistsError:
                time.sleep(0.01)
        return False

    def __exit__(self, exc_type, exc, tb):
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
        if self.acquired:
            try:
                self.path.unlink()
            except OSError:
                pass
        return False
