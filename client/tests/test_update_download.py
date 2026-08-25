from __future__ import annotations

import hashlib
import io
import sys
import threading
import zipfile
from pathlib import Path

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import client_info
from update_download import (
    DownloadPolicy,
    ReleaseDownloadCancelled,
    ReleaseDownloadError,
    download_windows_zip_artifact,
)
from update_delivery import (
    ReleaseArtifact,
    ReleaseDelivery,
    ReleaseKind,
    ReleaseUpdateError,
)


def _zip_bytes() -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("PlayAural/PlayAural.exe", "application")
    return output.getvalue()


def _windows_artifact(*, sha256: str = "") -> ReleaseArtifact:
    return ReleaseArtifact(
        target="windows",
        delivery=ReleaseDelivery.WINDOWS_ZIP,
        url="https://downloads.example.com/PlayAural.zip",
        version="2",
        sha256=sha256,
    )


class _FakeHop:
    def __init__(self, url: str) -> None:
        self.url = url


class _FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        url: str = "https://downloads.example.com/PlayAural.zip",
        content_length: int | None = None,
        history: list[_FakeHop] | None = None,
    ) -> None:
        self.payload = payload
        self.url = url
        self.history = history or []
        self.headers = {}
        if content_length is not None:
            self.headers["content-length"] = str(content_length)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        for offset in range(0, len(self.payload), chunk_size):
            yield self.payload[offset : offset + chunk_size]


class _FakeSession:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.max_redirects = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def get(self, *_args, **_kwargs):
        return self.response


@pytest.fixture(autouse=True)
def _windows_release_target(monkeypatch):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")


def test_download_verifies_sha256_zip_integrity_and_progress(tmp_path):
    payload = _zip_bytes()
    artifact = ReleaseArtifact.from_packet(
        {
            "available": True,
            "target": "windows",
            "delivery": "windows_zip",
            "url": "https://downloads.example.com/PlayAural.zip",
            "version": "2",
            "hash": hashlib.sha256(payload).hexdigest(),
        }
    )
    progress = []

    result = download_windows_zip_artifact(
        artifact,
        kind=ReleaseKind.APPLICATION,
        cancel_event=threading.Event(),
        progress_callback=progress.append,
        temp_directory=tmp_path,
        policy=DownloadPolicy(chunk_size=7),
        session_factory=lambda: _FakeSession(
            _FakeResponse(payload, content_length=len(payload))
        ),
    )

    assert result.read_bytes() == payload
    assert progress[-1].percent == 100


def test_hash_mismatch_deletes_every_partial_download(tmp_path):
    payload = _zip_bytes()
    artifact = _windows_artifact(sha256="0" * 64)

    with pytest.raises(ReleaseDownloadError, match="hash-mismatch"):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=threading.Event(),
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, content_length=len(payload))
            ),
        )

    assert list(tmp_path.iterdir()) == []


def test_invalid_zip_is_deleted_after_download_validation(tmp_path):
    payload = b"not a zip archive"
    artifact = _windows_artifact()

    with pytest.raises(ReleaseDownloadError, match="invalid-package"):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=threading.Event(),
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, content_length=len(payload))
            ),
        )

    assert list(tmp_path.iterdir()) == []


def test_cancellation_and_incomplete_transfer_delete_partial_files(tmp_path):
    payload = _zip_bytes()
    artifact = _windows_artifact()
    cancelled = threading.Event()
    cancelled.set()
    with pytest.raises(ReleaseDownloadCancelled):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=cancelled,
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(_FakeResponse(payload)),
        )

    with pytest.raises(ReleaseDownloadError, match="incomplete"):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=threading.Event(),
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, content_length=len(payload) + 1)
            ),
        )

    assert list(tmp_path.iterdir()) == []


def test_unsafe_redirect_and_oversized_response_are_rejected(tmp_path):
    payload = _zip_bytes()
    artifact = _windows_artifact()

    with pytest.raises(ReleaseDownloadError, match="unsafe-redirect"):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=threading.Event(),
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, history=[_FakeHop("http://unsafe.example/file")])
            ),
        )

    with pytest.raises(ReleaseDownloadError, match="too-large"):
        download_windows_zip_artifact(
            artifact,
            kind=ReleaseKind.APPLICATION,
            cancel_event=threading.Event(),
            temp_directory=tmp_path,
            policy=DownloadPolicy(maximum_bytes=len(payload) - 1),
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, content_length=len(payload))
            ),
        )


def test_release_metadata_rejects_unavailable_and_malformed_hashes():
    with pytest.raises(ReleaseUpdateError, match="unavailable"):
        ReleaseArtifact.from_packet(
            {
                "available": False,
                "target": "windows",
                "url": "https://downloads.example.com/PlayAural.zip",
            }
        )
    with pytest.raises(ReleaseUpdateError, match="invalid-hash"):
        ReleaseArtifact.from_packet(
            {
                "available": True,
                "target": "windows",
                "delivery": "windows_zip",
                "url": "https://downloads.example.com/PlayAural.zip",
                "version": "2",
                "hash": "bad",
            }
        )
    with pytest.raises(ReleaseUpdateError, match="invalid-url"):
        ReleaseArtifact(
            target="windows",
            delivery=ReleaseDelivery.WINDOWS_ZIP,
            url="http://downloads.example.com/PlayAural.zip",
            version="2",
        )


def test_download_without_sha256_succeeds_and_skips_digest_enforcement(tmp_path):
    payload = _zip_bytes()

    result = download_windows_zip_artifact(
        _windows_artifact(),
        kind=ReleaseKind.SOUNDS,
        cancel_event=threading.Event(),
        temp_directory=tmp_path,
        session_factory=lambda: _FakeSession(
            _FakeResponse(payload, content_length=len(payload))
        ),
    )

    assert result.read_bytes() == payload


def test_cancellation_after_the_final_network_block_deletes_the_package(tmp_path):
    payload = _zip_bytes()
    cancelled = threading.Event()

    def cancel_after_progress(_progress):
        cancelled.set()

    with pytest.raises(ReleaseDownloadCancelled):
        download_windows_zip_artifact(
            _windows_artifact(),
            kind=ReleaseKind.APPLICATION,
            cancel_event=cancelled,
            progress_callback=cancel_after_progress,
            temp_directory=tmp_path,
            session_factory=lambda: _FakeSession(
                _FakeResponse(payload, content_length=len(payload))
            ),
        )

    assert list(tmp_path.iterdir()) == []
