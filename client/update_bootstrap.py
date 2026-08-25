"""Bounded startup handshake used to confirm a newly installed client boots."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import time
from collections.abc import Sequence
from pathlib import Path

from update_contract import (
    APPLICATION_DOWNLOAD_PREFIX,
    DEFAULT_RELEASE_DOWNLOAD_PREFIX,
    SOUNDS_DOWNLOAD_PREFIX,
    TEMPORARY_UPDATER_PREFIX,
    WINDOWS_ARCHIVE_SUFFIX,
    WINDOWS_EXECUTABLE_SUFFIX,
)


UPDATE_TOKEN_OPTION = "--update-token"
UPDATE_HELPER_CLEANUP_OPTION = "--cleanup-update-helper"
UPDATE_TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
READY_FILE_PREFIX = "playaural-update-ready-"
STALE_UPDATE_FILE_MAX_AGE_SECONDS = 24 * 60 * 60
UPDATE_HANDSHAKE_VERSION = 1
MAXIMUM_READY_MARKER_BYTES = 4 * 1024
UPDATE_HELPER_DELETE_TIMEOUT_SECONDS = 60.0
UPDATE_HELPER_DELETE_RETRY_SECONDS = 0.25
TEMPORARY_UPDATER_RE = re.compile(
    rf"^{re.escape(TEMPORARY_UPDATER_PREFIX)}[0-9a-f]{{32}}"
    rf"{re.escape(WINDOWS_EXECUTABLE_SUFFIX)}$"
)
LEGACY_TEMPORARY_UPDATER_RE = re.compile(r"^playaural_updater_[0-9]+\.exe$")
READY_FILE_RE = re.compile(
    rf"^{re.escape(READY_FILE_PREFIX)}[0-9a-f]{{32}}\.json$"
)
RELEASE_DOWNLOAD_RE = re.compile(
    rf"^(?:{'|'.join(re.escape(prefix) for prefix in (APPLICATION_DOWNLOAD_PREFIX, DEFAULT_RELEASE_DOWNLOAD_PREFIX, SOUNDS_DOWNLOAD_PREFIX))})"
    rf"[A-Za-z0-9_-]+{re.escape(WINDOWS_ARCHIVE_SUFFIX)}(?:\.part)?$"
)
LEGACY_RELEASE_DOWNLOAD_RE = re.compile(
    r"^playaural_(?:update|sounds)_[0-9]+\.zip$"
)


def update_ready_path(token: str, temp_directory: Path | None = None) -> Path:
    """Return the fixed temp location for one validated update token."""
    normalized = str(token or "").strip().lower()
    if not UPDATE_TOKEN_RE.fullmatch(normalized):
        raise ValueError("Invalid update token")
    parent = Path(temp_directory or tempfile.gettempdir()).resolve()
    return parent / f"{READY_FILE_PREFIX}{normalized}.json"


def update_token_from_arguments(arguments: Sequence[str] | None = None) -> str:
    """Read a valid health token without consuming unrelated client arguments."""
    values = list(sys.argv[1:] if arguments is None else arguments)
    try:
        option_index = values.index(UPDATE_TOKEN_OPTION)
    except ValueError:
        return ""
    if option_index + 1 >= len(values):
        return ""
    candidate = values[option_index + 1].strip().lower()
    return candidate if UPDATE_TOKEN_RE.fullmatch(candidate) else ""


def temporary_updater_path(
    value: object,
    *,
    temp_directory: Path | None = None,
) -> Path | None:
    """Validate one updater-owned helper path in the system temp root."""
    parent = Path(temp_directory or tempfile.gettempdir()).resolve()
    try:
        candidate = Path(str(value or "")).resolve()
    except (OSError, ValueError):
        return None
    if (
        candidate.parent != parent
        or not TEMPORARY_UPDATER_RE.fullmatch(candidate.name)
    ):
        return None
    return candidate


def update_helper_cleanup_arguments(
    executable_path: Path,
    *,
    temp_directory: Path | None = None,
) -> list[str]:
    """Build a bounded cleanup handoff only for a genuine temp updater helper."""
    helper_path = temporary_updater_path(
        executable_path,
        temp_directory=temp_directory,
    )
    if helper_path is None:
        return []
    return [UPDATE_HELPER_CLEANUP_OPTION, str(helper_path)]


def consume_update_helper_cleanup_path(
    *,
    temp_directory: Path | None = None,
) -> Path | None:
    """Consume and validate the one-time updater cleanup handoff from argv."""
    helper_path: Path | None = None
    retained = [sys.argv[0]]
    values = sys.argv[1:]
    index = 0
    while index < len(values):
        if values[index] == UPDATE_HELPER_CLEANUP_OPTION:
            if index + 1 < len(values):
                if helper_path is None:
                    helper_path = temporary_updater_path(
                        values[index + 1],
                        temp_directory=temp_directory,
                    )
                index += 2
                continue
            index += 1
            continue
        retained.append(values[index])
        index += 1
    sys.argv[:] = retained
    return helper_path


def delete_update_helper_with_retry(
    helper_path: Path,
    *,
    temp_directory: Path | None = None,
    timeout_seconds: float = UPDATE_HELPER_DELETE_TIMEOUT_SECONDS,
    retry_seconds: float = UPDATE_HELPER_DELETE_RETRY_SECONDS,
) -> bool:
    """Delete one validated helper after its updater process releases the file."""
    if timeout_seconds < 0 or retry_seconds <= 0:
        raise ValueError("helper cleanup timing must be positive")
    validated_path = temporary_updater_path(
        helper_path,
        temp_directory=temp_directory,
    )
    if validated_path is None:
        return False
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            if validated_path.is_symlink():
                return False
            validated_path.unlink(missing_ok=True)
            return not validated_path.exists()
        except OSError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(retry_seconds)


def schedule_update_helper_cleanup(helper_path: Path | None) -> None:
    """Start bounded background cleanup while the updater finishes exiting."""
    if helper_path is None:
        return
    worker = threading.Thread(
        target=delete_update_helper_with_retry,
        args=(helper_path,),
        name="PlayAural updater cleanup",
        daemon=True,
    )
    worker.start()


def _consume_update_token_from_sys_argv() -> str:
    """Remove the one-time token so client-initiated restarts cannot replay it."""
    token = ""
    retained = [sys.argv[0]]
    values = sys.argv[1:]
    index = 0
    while index < len(values):
        if values[index] == UPDATE_TOKEN_OPTION:
            if index + 1 < len(values):
                candidate = values[index + 1].strip().lower()
                if not token and UPDATE_TOKEN_RE.fullmatch(candidate):
                    token = candidate
                index += 2
                continue
            index += 1
            continue
        retained.append(values[index])
        index += 1
    sys.argv[:] = retained
    return token


def mark_update_ready(
    *,
    client_version: str,
    arguments: Sequence[str] | None = None,
) -> bool:
    """Atomically signal that the updated desktop client initialized safely."""
    token = (
        _consume_update_token_from_sys_argv()
        if arguments is None
        else update_token_from_arguments(arguments)
    )
    normalized_version = str(client_version or "").strip()
    if not token or not normalized_version:
        return False
    ready_path = update_ready_path(token)
    temporary_path = ready_path.with_suffix(f".{os.getpid()}.tmp")
    payload = json.dumps(
        {
            "protocol": UPDATE_HANDSHAKE_VERSION,
            "pid": os.getpid(),
            "token": token,
            "client_version": normalized_version,
        }
    )
    try:
        temporary_path.write_text(payload, encoding="utf-8")
        os.replace(temporary_path, ready_path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        return False
    return True


def update_ready_marker_matches(
    path: Path,
    *,
    token: str,
    process_id: int,
    client_version: str,
) -> bool:
    """Validate that a marker belongs to the exact launched client process."""
    try:
        if path.stat().st_size > MAXIMUM_READY_MARKER_BYTES:
            return False
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return bool(
        isinstance(payload, dict)
        and payload.get("protocol") == UPDATE_HANDSHAKE_VERSION
        and payload.get("pid") == process_id
        and payload.get("token") == token
        and payload.get("client_version") == client_version
    )


def cleanup_stale_update_files(
    *,
    temp_directory: Path | None = None,
    maximum_age_seconds: float = STALE_UPDATE_FILE_MAX_AGE_SECONDS,
) -> None:
    """Remove only old updater helpers and health markers from the temp root."""
    if maximum_age_seconds < 0:
        raise ValueError("maximum_age_seconds cannot be negative")
    parent = Path(temp_directory or tempfile.gettempdir()).resolve()
    cutoff = time.time() - maximum_age_seconds
    try:
        candidates = tuple(parent.iterdir())
    except OSError:
        return
    for candidate in candidates:
        if not (
            TEMPORARY_UPDATER_RE.fullmatch(candidate.name)
            or LEGACY_TEMPORARY_UPDATER_RE.fullmatch(candidate.name)
            or READY_FILE_RE.fullmatch(candidate.name)
            or RELEASE_DOWNLOAD_RE.fullmatch(candidate.name)
            or LEGACY_RELEASE_DOWNLOAD_RE.fullmatch(candidate.name)
        ):
            continue
        try:
            resolved = candidate.resolve()
            if resolved.parent != parent or not resolved.is_file():
                continue
            if resolved.stat().st_mtime <= cutoff:
                resolved.unlink()
        except OSError:
            continue
