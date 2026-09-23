"""Cross-process single-flight lock for one campaign role.

Fail-closed: a controller that does not acquire the lock, or that observes a
live role or a live claim, must not spawn. A failed acquire still checks the
role and the claim before it reports lock_timeout. O_EXCL is the atomic claim.
A dead holder's lock file may be reclaimed. A live holder is never stolen.
"""
from __future__ import annotations

import errno
import json
import os
import re
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from atomic_state import atomic_write_json

CLAIM_SCHEMA = "aetheria_campaign_role_claim_v1"
_EMPTY_LOCK_GRACE_S = 1.0
_STILL_ACTIVE = 259
_DATE_MS = re.compile(r"/Date\((-?\d+)\)/")
_WMI_CREATE = re.compile(r"^(\d{14})\.(\d+)([+-]\d+)?$")


def pid_alive(pid: Any) -> bool:
    """Process-table presence. Does not treat signal 0 as a Windows kill."""
    try:
        p = int(pid)
    except (TypeError, ValueError):
        return False
    if p <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel.OpenProcess(0x1000, False, p)  # PROCESS_QUERY_LIMITED_INFORMATION
        if handle:
            code = ctypes.c_ulong()
            queried = bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code)))
            kernel.CloseHandle(handle)
            # An exited process can still be opened while a handle remains.
            # STILL_ACTIVE (259) is the running code; any other code is dead.
            if queried and int(code.value) != _STILL_ACTIVE:
                return False
            return True
        # ERROR_ACCESS_DENIED: the pid exists but this token cannot open it.
        return ctypes.get_last_error() == 5
    try:
        os.kill(p, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _read_holder(path: Path) -> tuple[str, int | None]:
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "missing", None
    except OSError:
        return "unreadable", None
    if not raw:
        return "empty", None
    tok = raw.split()[0]
    try:
        return "pid", int(tok)
    except ValueError:
        return "unreadable", None


class CampaignLock:
    def __init__(self, path: Path, timeout_s: float = 2.0):
        self.path = Path(path)
        self.timeout_s = timeout_s
        self._fd: int | None = None
        self.acquired = False

    def __enter__(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + max(0.0, float(self.timeout_s))
        while True:
            if self._try_acquire():
                return True
            if time.time() >= deadline:
                return False
            time.sleep(0.01)

    def __exit__(self, exc_type, exc, tb) -> bool:
        fd = self._fd
        self._fd = None
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if self.acquired and _read_holder(self.path)[1] == os.getpid():
            try:
                self.path.unlink()
            except OSError:
                pass
        self.acquired = False
        return False

    def _try_acquire(self) -> bool:
        try:
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            self._steal_if_stale()
            return False
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            self._steal_if_stale()
            return False
        try:
            os.write(fd, f"{os.getpid()}\n".encode())
            try:
                os.fsync(fd)
            except OSError:
                pass
        except OSError:
            self._abort_open(fd)
            return False
        if _read_holder(self.path)[1] != os.getpid():
            self._abort_open(fd)
            return False
        self._fd = fd
        self.acquired = True
        return True

    def _abort_open(self, fd: int) -> None:
        try:
            os.close(fd)
        except OSError:
            pass
        kind, pid = _read_holder(self.path)
        if kind == "missing":
            return
        if pid == os.getpid() or kind == "empty":
            try:
                self.path.unlink()
            except OSError:
                pass

    def _steal_if_stale(self) -> None:
        kind, pid = _read_holder(self.path)
        if kind == "missing":
            return
        if kind == "pid":
            if pid is not None and pid_alive(pid):
                return
        elif kind == "empty":
            try:
                age = time.time() - self.path.stat().st_mtime
            except OSError:
                return
            if age < _EMPTY_LOCK_GRACE_S:
                return
        else:
            # Unreadable holder: fail closed. Do not steal.
            return
        stale = self.path.with_name(
            self.path.name + f".stale.{os.getpid()}.{time.time_ns()}"
        )
        try:
            os.replace(self.path, stale)
        except (FileNotFoundError, OSError):
            return
        try:
            stale.unlink()
        except OSError:
            pass


def _as_pid(value: Any) -> int | None:
    try:
        p = int(value)
    except (TypeError, ValueError):
        return None
    if p <= 0:
        return None
    return p


def _read_claim(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"_corrupt": True}
    if not isinstance(doc, dict) or doc.get("schema") != CLAIM_SCHEMA:
        return {"_corrupt": True}
    return doc


def normalize_create_time(raw: Any) -> str | None:
    """Slash-free create_time token. The same raw value always normalizes the same way.

    Windows CIM JSON often yields ``/Date(milliseconds)/``. That is not a host path.
    Path-shaped values are dropped (None) so a claim cannot store them.
    """
    if raw is None:
        return None
    text = str(raw).strip().strip('"')
    if not text or text.lower() == "none":
        return None
    text = text.replace("\\/", "/")
    dated = _DATE_MS.search(text)
    if dated:
        return "ms:" + dated.group(1)
    wmi = _WMI_CREATE.fullmatch(text)
    if wmi:
        return "wmi:" + wmi.group(1) + wmi.group(2)
    if text.startswith(("ms:", "wmi:", "boot:")) and "/" not in text and "\\" not in text:
        return text
    if "/" in text or "\\" in text or re.search(r"[A-Za-z]:[\\/]", text):
        return None
    if text.isdigit():
        return "boot:" + text
    return text


def process_create_time(pid: int) -> str | None:
    """Stable process start token. Not a path. None when the OS does not provide one."""
    try:
        p = int(pid)
    except (TypeError, ValueError):
        return None
    if p <= 0:
        return None
    if sys.platform == "win32":
        try:
            from process_identity_bind import windows_binding
        except Exception:
            return None
        binding = windows_binding(p)
        if binding is None or not binding.creation_time:
            return None
        return normalize_create_time(binding.creation_time)
    stat_path = Path(f"/proc/{p}/stat")
    try:
        text = stat_path.read_text(encoding="utf-8")
    except OSError:
        return None
    end = text.rfind(")")
    if end < 0:
        return None
    fields = text[end + 1 :].split()
    # proc(5) field 22 starttime is index 19 after the comm field.
    if len(fields) < 20 or not fields[19].isdigit():
        return None
    return normalize_create_time(fields[19])


def _write_claim(path: Path, doc: Mapping[str, Any]) -> None:
    atomic_write_json(path, dict(doc))


def _same_process(pid: int, recorded: Any, create_time_fn: Callable[[int], str | None]) -> bool:
    """Whether a live pid is still the process we recorded.

    A create_time mismatch is PID reuse: not our worker, and not a kill target.
    A recorded create_time that cannot be re-read fails closed (treat as same).
    """
    recorded_s = str(recorded).strip() if recorded else ""
    if not recorded_s or recorded_s.lower() == "none":
        return True
    try:
        live = create_time_fn(pid)
    except Exception:
        live = None
    if not live:
        return True
    return str(live) == recorded_s


def _claim_blocks(
    doc: dict | None,
    *,
    alive: Callable[[int], bool],
    create_time_fn: Callable[[int], str | None],
) -> bool:
    if doc is None:
        return False
    if doc.get("_corrupt"):
        return True
    state = doc.get("state")
    if state == "spawning":
        owner = _as_pid(doc.get("owner_pid"))
        if owner is None or not alive(owner):
            return owner is None
        return _same_process(owner, doc.get("owner_create_time"), create_time_fn)
    if state == "live":
        worker = _as_pid(doc.get("worker_pid"))
        if worker is None or not alive(worker):
            return worker is None
        return _same_process(worker, doc.get("worker_create_time"), create_time_fn)
    return True


def _clear_claim(path: Path, claim_id: str) -> None:
    doc = _read_claim(path)
    if not doc or doc.get("_corrupt") or doc.get("claim_id") != claim_id:
        return
    try:
        path.unlink()
    except OSError:
        pass


def _probe_create_time(pid: int | None, create_time_fn: Callable[[int], str | None]) -> str | None:
    if pid is None:
        return None
    try:
        value = create_time_fn(pid)
    except Exception:
        return None
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _stamp_create_times(
    lock_path: Path,
    claim_path: Path,
    claim_id: str,
    *,
    owner_pid: int,
    owner_create: str | None,
    worker_pid: int | None,
    worker_create: str | None,
    timeout_s: float,
) -> None:
    """Fill create_time on the claim this admit published.

    If the lock is busy or the claim id changed, leave the document alone.
    A live claim with no create_time still blocks a later admit.
    """
    if not claim_id or (owner_create is None and worker_create is None):
        return
    with CampaignLock(lock_path, timeout_s=timeout_s) as acquired:
        if not acquired:
            return
        doc = _read_claim(claim_path)
        if not doc or doc.get("_corrupt") or doc.get("claim_id") != claim_id:
            return
        if doc.get("state") not in ("spawning", "live"):
            return
        changed = False
        if (
            owner_create
            and not doc.get("owner_create_time")
            and _as_pid(doc.get("owner_pid")) == owner_pid
        ):
            doc["owner_create_time"] = owner_create
            changed = True
        if (
            worker_create
            and worker_pid is not None
            and not doc.get("worker_create_time")
            and _as_pid(doc.get("worker_pid")) == worker_pid
        ):
            doc["worker_create_time"] = worker_create
            changed = True
        if not changed:
            return
        doc.pop("_corrupt", None)
        _write_claim(claim_path, doc)


def _observed_block_reason(
    claim_path: Path,
    *,
    role_alive: Callable[[], bool],
    alive: Callable[[int], bool],
    create_time_fn: Callable[[int], str | None],
) -> str | None:
    """Refuse reason when a role or claim already blocks another spawn.

    ``role_alive`` is checked first, then ``_claim_blocks``. None means both
    still look dead. A role-check error fails closed and does not spawn.
    """
    try:
        busy = bool(role_alive())
    except Exception:
        return "role_check_error"
    if busy:
        return "role_alive"
    if _claim_blocks(_read_claim(claim_path), alive=alive, create_time_fn=create_time_fn):
        return "claim_held"
    return None


def single_flight_spawn(
    lock_path: Path,
    claim_path: Path,
    *,
    role: str,
    role_alive: Callable[[], bool],
    spawn: Callable[[], Mapping[str, Any]],
    timeout_s: float = 2.0,
    pid_alive_fn: Callable[[int], bool] | None = None,
    create_time_fn: Callable[[int], str | None] | None = None,
) -> dict[str, Any]:
    """Admit at most one spawn for ``role`` across processes.

    The lock is held across the role check, the claim publish, and ``spawn``.
    Create-time reads stored on the new claim run after that hold is released.
    On Windows those reads are CIM queries and can outlast a short waiter.
    If the lock is not acquired, this still observes ``role_alive`` and the
    claim before reporting ``lock_timeout``. A published admit must surface as
    ``role_alive`` or ``claim_held``; ``lock_timeout`` is only when both still
    look dead. A live claim with no create_time yet still blocks another spawn
    (missing create_time is treated as the same process). A caller that loses
    the lock or sees a live role or claim does not call ``spawn``.
    """
    alive = pid_alive_fn or pid_alive
    created = create_time_fn or process_create_time
    lock_path = Path(lock_path)
    claim_path = Path(claim_path)
    refused = {
        "spawned": False,
        "role": role,
        "pid": None,
        "detail": None,
    }
    admitted: dict[str, Any] | None = None
    claim_id = ""
    worker: int | None = None
    with CampaignLock(lock_path, timeout_s=timeout_s) as acquired:
        if not acquired:
            # The winner may already have published. Post-admit create-time
            # probes do not hold this lock, but a live holder can still outlast
            # timeout_s (Windows run 35916007830). Observe before lock_timeout.
            visible = _observed_block_reason(
                claim_path,
                role_alive=role_alive,
                alive=alive,
                create_time_fn=created,
            )
            if visible is not None:
                return {**refused, "reason": visible}
            return {**refused, "reason": "lock_timeout"}
        visible = _observed_block_reason(
            claim_path,
            role_alive=role_alive,
            alive=alive,
            create_time_fn=created,
        )
        if visible is not None:
            return {**refused, "reason": visible}
        claim_id = f"{os.getpid()}-{time.time_ns()}"
        owner_pid = os.getpid()
        _write_claim(
            claim_path,
            {
                "schema": CLAIM_SCHEMA,
                "role": role,
                "state": "spawning",
                "owner_pid": owner_pid,
                "owner_create_time": None,
                "worker_pid": None,
                "worker_create_time": None,
                "claim_id": claim_id,
            },
        )
        try:
            result = spawn()
        except Exception as e:
            _clear_claim(claim_path, claim_id)
            return {**refused, "reason": "spawn_error", "detail": type(e).__name__}
        if not isinstance(result, Mapping) or not result.get("ok"):
            _clear_claim(claim_path, claim_id)
            detail = None
            if isinstance(result, Mapping):
                detail = result.get("detail")
            return {**refused, "reason": "spawn_failed", "detail": detail}
        worker = _as_pid(result.get("pid"))
        _write_claim(
            claim_path,
            {
                "schema": CLAIM_SCHEMA,
                "role": role,
                "state": "live",
                "owner_pid": owner_pid,
                "owner_create_time": None,
                "worker_pid": worker,
                "worker_create_time": None,
                "claim_id": claim_id,
            },
        )
        admitted = {
            "spawned": True,
            "reason": "admitted",
            "role": role,
            "pid": worker,
            "detail": result.get("detail"),
        }
    owner_create = _probe_create_time(owner_pid, created)
    worker_create = _probe_create_time(worker, created)
    _stamp_create_times(
        lock_path,
        claim_path,
        claim_id,
        owner_pid=owner_pid,
        owner_create=owner_create,
        worker_pid=worker,
        worker_create=worker_create,
        timeout_s=timeout_s,
    )
    return admitted if admitted is not None else {**refused, "reason": "spawn_failed"}
