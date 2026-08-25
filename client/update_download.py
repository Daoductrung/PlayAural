"""Validated, cancellable downloads for desktop release artifacts."""

from __future__ import annotations

import hashlib
import os
import tempfile
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests

from client_info import is_safe_https_download_url
from update_contract import DEFAULT_RELEASE_DOWNLOAD_PREFIX, WINDOWS_ARCHIVE_SUFFIX
from update_delivery import (
    ReleaseArtifact,
    ReleaseDelivery,
    ReleaseKind,
    ReleaseUpdateError,
    resolve_release_update_strategy,
)
from update_engine import UpdateInstallationError, validate_archive_package


class ReleaseDownloadError(ReleaseUpdateError):
    """A localized, user-actionable release download failure."""


class ReleaseDownloadCancelled(ReleaseDownloadError):
    """Raised when the user cancels an active release download."""

    def __init__(self) -> None:
        super().__init__("update-download-cancelled")


@dataclass(frozen=True, slots=True)
class DownloadPolicy:
    """Network and resource limits for one release download."""

    chunk_size: int = 256 * 1024
    connect_timeout_seconds: float = 15.0
    read_timeout_seconds: float = 60.0
    maximum_bytes: int = 2 * 1024 * 1024 * 1024
    maximum_redirects: int = 10

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.connect_timeout_seconds <= 0 or self.read_timeout_seconds <= 0:
            raise ValueError("download timeouts must be positive")
        if self.maximum_bytes <= 0:
            raise ValueError("maximum_bytes must be positive")
        if self.maximum_redirects < 0:
            raise ValueError("maximum_redirects cannot be negative")


@dataclass(frozen=True, slots=True)
class DownloadProgress:
    """One throttling-independent download progress sample."""

    downloaded_bytes: int
    total_bytes: int | None

    @property
    def percent(self) -> int | None:
        if not self.total_bytes:
            return None
        return min(100, int(self.downloaded_bytes * 100 / self.total_bytes))


def _validated_content_length(value: object, maximum_bytes: int) -> int | None:
    if value in (None, ""):
        return None
    try:
        size = int(str(value))
    except (TypeError, ValueError) as error:
        raise ReleaseDownloadError("update-download-invalid-size") from error
    if size < 0:
        raise ReleaseDownloadError("update-download-invalid-size")
    if size > maximum_bytes:
        raise ReleaseDownloadError(
            "update-download-too-large",
            maximum_mb=maximum_bytes // (1024 * 1024),
        )
    return size


def _validate_response_urls(response: requests.Response) -> None:
    for hop in [*response.history, response]:
        if not is_safe_https_download_url(hop.url):
            raise ReleaseDownloadError("update-download-unsafe-redirect")


def _validate_zip(path: Path) -> None:
    try:
        validate_archive_package(path)
    except UpdateInstallationError as error:
        raise ReleaseDownloadError("update-download-invalid-package") from error


def download_windows_zip_artifact(
    artifact: ReleaseArtifact,
    *,
    kind: ReleaseKind,
    cancel_event: threading.Event,
    progress_callback: Callable[[DownloadProgress], None] | None = None,
    policy: DownloadPolicy | None = None,
    temp_directory: Path | None = None,
    file_prefix: str = DEFAULT_RELEASE_DOWNLOAD_PREFIX,
    session_factory: Callable[[], requests.Session] = requests.Session,
) -> Path:
    """Download one Windows ZIP artifact, deleting partial files on failure."""
    strategy = resolve_release_update_strategy(artifact, kind)
    if strategy.delivery is not ReleaseDelivery.WINDOWS_ZIP:
        raise ReleaseDownloadError("update-release-windows-zip-required")
    active_policy = policy or DownloadPolicy()
    target_parent = Path(temp_directory or tempfile.gettempdir()).resolve()
    target_parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(
        prefix=file_prefix,
        suffix=f"{WINDOWS_ARCHIVE_SUFFIX}.part",
        dir=target_parent,
    )
    os.close(descriptor)
    partial_path = Path(raw_path)
    completed_path = partial_path.with_suffix("")
    digest = hashlib.sha256() if artifact.sha256 else None
    downloaded = 0
    succeeded = False

    try:
        if cancel_event.is_set():
            raise ReleaseDownloadCancelled()

        with session_factory() as session:
            session.max_redirects = active_policy.maximum_redirects
            with session.get(
                artifact.url,
                allow_redirects=True,
                stream=True,
                headers={"Accept-Encoding": "identity"},
                timeout=(
                    active_policy.connect_timeout_seconds,
                    active_policy.read_timeout_seconds,
                ),
            ) as response:
                response.raise_for_status()
                _validate_response_urls(response)
                total_size = _validated_content_length(
                    response.headers.get("content-length"),
                    active_policy.maximum_bytes,
                )
                with partial_path.open("wb") as output:
                    for block in response.iter_content(active_policy.chunk_size):
                        if cancel_event.is_set():
                            raise ReleaseDownloadCancelled()
                        if not block:
                            continue
                        downloaded += len(block)
                        if downloaded > active_policy.maximum_bytes:
                            raise ReleaseDownloadError(
                                "update-download-too-large",
                                maximum_mb=active_policy.maximum_bytes // (1024 * 1024),
                            )
                        output.write(block)
                        if digest is not None:
                            digest.update(block)
                        if progress_callback:
                            progress_callback(DownloadProgress(downloaded, total_size))

                content_encoding = str(
                    response.headers.get("content-encoding", "") or ""
                ).strip().lower()
                if total_size is not None and content_encoding in {"", "identity"}:
                    if downloaded != total_size:
                        raise ReleaseDownloadError("update-download-incomplete")

        if downloaded == 0:
            raise ReleaseDownloadError("update-download-empty")
        if cancel_event.is_set():
            raise ReleaseDownloadCancelled()
        if digest is not None and digest.hexdigest() != artifact.sha256:
            raise ReleaseDownloadError("update-download-hash-mismatch")

        os.replace(partial_path, completed_path)
        _validate_zip(completed_path)
        if cancel_event.is_set():
            raise ReleaseDownloadCancelled()
        succeeded = True
        return completed_path
    except ReleaseDownloadError:
        raise
    except requests.TooManyRedirects as error:
        raise ReleaseDownloadError("update-download-too-many-redirects") from error
    except requests.Timeout as error:
        raise ReleaseDownloadError("update-download-timeout") from error
    except requests.RequestException as error:
        raise ReleaseDownloadError("update-download-network-error") from error
    except OSError as error:
        raise ReleaseDownloadError("update-download-file-error") from error
    finally:
        if partial_path.exists():
            partial_path.unlink(missing_ok=True)
        if completed_path.exists() and not succeeded:
            completed_path.unlink(missing_ok=True)
