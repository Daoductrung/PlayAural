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
)
from windows_update import (
    WindowsUpdaterLaunchRequest,
    build_windows_updater_command,
)


@pytest.fixture(autouse=True)
def _windows_release_target(monkeypatch):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")


def _artifact(*, sha256: str = "") -> ReleaseArtifact:
    return ReleaseArtifact(
        target="windows",
        delivery=ReleaseDelivery.WINDOWS_ZIP,
        url="https://downloads.example.com/PlayAural.zip",
        version="2",
        sha256=sha256,
    )


def _request(
    tmp_path: Path,
    *,
    kind: ReleaseKind = ReleaseKind.APPLICATION,
    sha256: str = "",
) -> WindowsUpdaterLaunchRequest:
    return WindowsUpdaterLaunchRequest(
        artifact=_artifact(sha256=sha256),
        kind=kind,
        archive_path=tmp_path / "release.zip",
        installation_directory=tmp_path / "PlayAural",
        executable_name="PlayAural.exe",
        process_id=123,
        locale="en",
        current_client_version="1",
        sounds_directory=(
            tmp_path / "PlayAural" / "_internal" / "sounds"
            if kind is ReleaseKind.SOUNDS
            else None
        ),
    )


def test_updater_command_omits_sha256_when_server_does_not_provide_one(tmp_path):
    command = build_windows_updater_command(
        tmp_path / "updater.exe",
        _request(tmp_path),
        process_started_at=None,
    )

    assert "--sha256" not in command
    assert command[command.index("--artifact-version") + 1] == "2"
    assert command[command.index("--expected-client-version") + 1] == "2"


def test_updater_command_includes_and_preserves_a_supplied_sha256(tmp_path):
    digest = "a" * 64
    command = build_windows_updater_command(
        tmp_path / "updater.exe",
        _request(tmp_path, sha256=digest),
        process_started_at=42.5,
    )

    assert command[command.index("--sha256") + 1] == digest
    assert command[command.index("--process-started-at") + 1] == "42.5"


def test_sound_command_uses_the_same_launcher_with_sound_specific_contract(
    tmp_path,
):
    request = _request(tmp_path, kind=ReleaseKind.SOUNDS)
    command = build_windows_updater_command(
        tmp_path / "updater.exe",
        request,
        process_started_at=None,
    )

    assert command[command.index("--extract-dir") + 1] == str(
        request.sounds_directory
    )
    assert command[command.index("--version-file") + 1] == "version.txt"
    assert command[command.index("--expected-client-version") + 1] == "1"


@pytest.mark.parametrize(
    ("archive_name", "executable_name", "error_id"),
    [
        ("release.exe", "PlayAural.exe", "windows-zip-required"),
        ("release.zip", "PlayAural", "invalid-executable"),
        ("release.zip", "../PlayAural.exe", "invalid-executable"),
    ],
)
def test_windows_launcher_rejects_non_zip_or_non_executable_contracts(
    tmp_path,
    archive_name,
    executable_name,
    error_id,
):
    with pytest.raises(ReleaseUpdateError, match=error_id):
        WindowsUpdaterLaunchRequest(
            artifact=_artifact(),
            kind=ReleaseKind.APPLICATION,
            archive_path=tmp_path / archive_name,
            installation_directory=tmp_path / "PlayAural",
            executable_name=executable_name,
            process_id=123,
            locale="en",
            current_client_version="1",
        )


def test_windows_launcher_is_rejected_on_non_windows_platform(monkeypatch, tmp_path):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Darwin")

    with pytest.raises(ReleaseUpdateError, match="platform-mismatch|windows-only"):
        _request(tmp_path)


def test_application_and_sound_requests_reject_crossed_destinations(tmp_path):
    with pytest.raises(ReleaseUpdateError, match="sounds-directory-missing"):
        WindowsUpdaterLaunchRequest(
            artifact=_artifact(),
            kind=ReleaseKind.SOUNDS,
            archive_path=tmp_path / "release.zip",
            installation_directory=tmp_path / "PlayAural",
            executable_name="PlayAural.exe",
            process_id=123,
            locale="en",
            current_client_version="1",
        )

    with pytest.raises(ReleaseUpdateError, match="unexpected-sounds-directory"):
        WindowsUpdaterLaunchRequest(
            artifact=_artifact(),
            kind=ReleaseKind.APPLICATION,
            archive_path=tmp_path / "release.zip",
            installation_directory=tmp_path / "PlayAural",
            executable_name="PlayAural.exe",
            process_id=123,
            locale="en",
            current_client_version="1",
            sounds_directory=tmp_path / "sounds",
        )
