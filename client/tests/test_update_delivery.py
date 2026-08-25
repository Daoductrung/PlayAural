from __future__ import annotations

import sys
from pathlib import Path

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import client_info
from update_delivery import (
    ReleaseArtifact,
    ReleaseDelivery,
    ReleaseKind,
    ReleaseUpdateError,
    resolve_release_update_strategy,
)


class _RecordingHost:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ReleaseArtifact, ReleaseKind]] = []

    def begin_windows_zip_update(
        self,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None:
        self.calls.append(("windows_zip", artifact, kind))

    def open_release_in_browser(
        self,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None:
        self.calls.append(("browser", artifact, kind))


def _set_platform(monkeypatch, system: str) -> None:
    monkeypatch.setattr(client_info.platform, "system", lambda: system)


@pytest.mark.parametrize("hash_value", [None, "", "   "])
def test_windows_metadata_accepts_an_omitted_or_empty_sha256(
    monkeypatch,
    hash_value,
):
    _set_platform(monkeypatch, "Windows")
    packet = {
        "available": True,
        "target": "windows",
        "delivery": "windows_zip",
        "url": "https://downloads.example.com/PlayAural.zip",
        "version": "2",
    }
    if hash_value is not None:
        packet["hash"] = hash_value

    artifact = ReleaseArtifact.from_packet(packet)

    assert artifact.sha256 == ""
    assert artifact.delivery is ReleaseDelivery.WINDOWS_ZIP


def test_windows_metadata_enforces_sha256_only_when_supplied(monkeypatch):
    _set_platform(monkeypatch, "Windows")
    packet = {
        "available": True,
        "target": "windows",
        "delivery": "windows_zip",
        "url": "https://downloads.example.com/PlayAural.zip",
        "version": "2",
    }

    with pytest.raises(ReleaseUpdateError, match="invalid-hash"):
        ReleaseArtifact.from_packet({**packet, "hash": "not-a-sha256"})

    artifact = ReleaseArtifact.from_packet({**packet, "hash": "A" * 64})
    assert artifact.sha256 == "a" * 64


def test_legacy_targetless_delivery_defaults_to_windows_zip_only_on_windows(
    monkeypatch,
):
    packet = {
        "url": "https://downloads.example.com/PlayAural.zip",
        "version": "2",
    }
    _set_platform(monkeypatch, "Windows")
    artifact = ReleaseArtifact.from_packet(packet)
    assert artifact.target == "windows"
    assert artifact.delivery is ReleaseDelivery.WINDOWS_ZIP

    _set_platform(monkeypatch, "Darwin")
    with pytest.raises(ReleaseUpdateError, match="invalid-target"):
        ReleaseArtifact.from_packet(packet)


@pytest.mark.parametrize("kind", list(ReleaseKind))
def test_browser_delivery_dispatches_application_and_sounds_on_macos(
    monkeypatch,
    kind,
):
    _set_platform(monkeypatch, "Darwin")
    artifact = ReleaseArtifact.from_packet(
        {
            "available": True,
            "target": "macos",
            "delivery": "browser",
            "url": "https://downloads.example.com/release",
            "version": "2",
        }
    )
    strategy = resolve_release_update_strategy(artifact, kind)
    host = _RecordingHost()

    strategy.begin(host, artifact, kind)

    assert host.calls == [("browser", artifact, kind)]


def test_windows_zip_strategy_dispatches_both_release_kinds(monkeypatch):
    _set_platform(monkeypatch, "Windows")
    artifact = ReleaseArtifact.from_packet(
        {
            "available": True,
            "target": "windows",
            "delivery": "windows_zip",
            "url": "https://downloads.example.com/release.ZIP?channel=stable",
            "version": "2",
        }
    )
    host = _RecordingHost()

    for kind in ReleaseKind:
        resolve_release_update_strategy(artifact, kind).begin(host, artifact, kind)

    assert [call[0] for call in host.calls] == ["windows_zip", "windows_zip"]
    assert [call[2] for call in host.calls] == list(ReleaseKind)


def test_windows_zip_is_rejected_on_macos_even_with_matching_packet_target(
    monkeypatch,
):
    _set_platform(monkeypatch, "Darwin")
    artifact = ReleaseArtifact(
        target="macos",
        delivery=ReleaseDelivery.WINDOWS_ZIP,
        url="https://downloads.example.com/release.zip",
        version="2",
    )

    with pytest.raises(ReleaseUpdateError, match="platform-mismatch"):
        resolve_release_update_strategy(artifact, ReleaseKind.APPLICATION)


def test_windows_zip_requires_zip_url_and_rejects_target_mismatch(monkeypatch):
    _set_platform(monkeypatch, "Windows")
    non_zip = ReleaseArtifact(
        target="windows",
        delivery=ReleaseDelivery.WINDOWS_ZIP,
        url="https://downloads.example.com/release.exe",
        version="2",
    )
    with pytest.raises(ReleaseUpdateError, match="zip-required"):
        resolve_release_update_strategy(non_zip, ReleaseKind.APPLICATION)

    with pytest.raises(ReleaseUpdateError, match="target-mismatch"):
        ReleaseArtifact.from_packet(
            {
                "available": True,
                "target": "macos",
                "delivery": "browser",
                "url": "https://downloads.example.com/release",
                "version": "2",
            }
        )


def test_browser_delivery_rejects_a_checksum_it_cannot_enforce(monkeypatch):
    _set_platform(monkeypatch, "Darwin")
    artifact = ReleaseArtifact(
        target="macos",
        delivery=ReleaseDelivery.BROWSER,
        url="https://downloads.example.com/release",
        version="2",
        sha256="a" * 64,
    )

    with pytest.raises(ReleaseUpdateError, match="hash-unsupported"):
        resolve_release_update_strategy(artifact, ReleaseKind.APPLICATION)
