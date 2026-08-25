"""Windows-only launcher for transactional ZIP application and sound updates."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

import psutil

from client_info import get_client_release_platform
from update_contract import (
    PYINSTALLER_INTERNAL_DIRECTORY,
    SOUND_VERSION_FILE_NAME,
    TEMPORARY_UPDATER_PREFIX,
    UPDATER_EXECUTABLE_NAME,
    WINDOWS_ARCHIVE_SUFFIX,
    WINDOWS_EXECUTABLE_SUFFIX,
    WINDOWS_RELEASE_TARGET,
    is_valid_locale_tag,
    is_valid_windows_executable_name,
)
from update_delivery import (
    ReleaseArtifact,
    ReleaseDelivery,
    ReleaseKind,
    ReleaseUpdateError,
    resolve_release_update_strategy,
)


UPDATER_RELATIVE_PATHS = (
    Path(UPDATER_EXECUTABLE_NAME),
    Path(PYINSTALLER_INTERNAL_DIRECTORY) / UPDATER_EXECUTABLE_NAME,
)


@dataclass(frozen=True, slots=True)
class WindowsUpdaterLaunchRequest:
    artifact: ReleaseArtifact
    kind: ReleaseKind
    archive_path: Path
    installation_directory: Path
    executable_name: str
    process_id: int
    locale: str
    current_client_version: str
    sounds_directory: Path | None = None

    def __post_init__(self) -> None:
        resolve_release_update_strategy(self.artifact, self.kind)
        if (
            get_client_release_platform() != WINDOWS_RELEASE_TARGET
            or self.artifact.target != WINDOWS_RELEASE_TARGET
            or self.artifact.delivery is not ReleaseDelivery.WINDOWS_ZIP
        ):
            raise ReleaseUpdateError("updater-error-windows-only")

        archive_path = Path(self.archive_path).resolve()
        installation_directory = Path(self.installation_directory).resolve()
        executable_name = str(self.executable_name or "").strip()
        if archive_path.suffix.lower() != WINDOWS_ARCHIVE_SUFFIX:
            raise ReleaseUpdateError("update-release-windows-zip-required")
        if not is_valid_windows_executable_name(executable_name):
            raise ReleaseUpdateError("updater-error-invalid-executable")
        if self.process_id <= 0:
            raise ReleaseUpdateError("updater-error-invalid-process")
        if not is_valid_locale_tag(self.locale):
            raise ReleaseUpdateError("updater-error-invalid-locale")
        if not str(self.current_client_version or "").strip():
            raise ReleaseUpdateError("updater-error-invalid-artifact-version")
        if self.kind is ReleaseKind.SOUNDS and self.sounds_directory is None:
            raise ReleaseUpdateError("updater-error-sounds-directory-missing")
        if self.kind is ReleaseKind.APPLICATION and self.sounds_directory is not None:
            raise ReleaseUpdateError("updater-error-unexpected-sounds-directory")

        object.__setattr__(self, "archive_path", archive_path)
        object.__setattr__(self, "installation_directory", installation_directory)
        object.__setattr__(self, "executable_name", executable_name)
        object.__setattr__(self, "locale", str(self.locale).strip())
        object.__setattr__(
            self,
            "current_client_version",
            str(self.current_client_version).strip(),
        )
        if self.sounds_directory is not None:
            object.__setattr__(
                self,
                "sounds_directory",
                Path(self.sounds_directory).resolve(),
            )


def find_packaged_updater(installation_directory: Path) -> Path | None:
    """Find the updater in either supported PyInstaller bundle layout."""
    for relative_path in UPDATER_RELATIVE_PATHS:
        candidate = installation_directory / relative_path
        if candidate.is_file():
            return candidate
    return None


def build_windows_updater_command(
    helper_path: Path,
    request: WindowsUpdaterLaunchRequest,
    *,
    process_started_at: float | None,
) -> list[str]:
    """Build the standalone updater command, omitting an absent checksum."""
    command = [
        str(helper_path),
        "--zip",
        str(request.archive_path),
        "--target",
        str(request.installation_directory),
        "--exe",
        request.executable_name,
        "--pid",
        str(request.process_id),
        "--locale",
        request.locale,
        "--artifact-version",
        request.artifact.version,
        "--expected-client-version",
        (
            request.artifact.version
            if request.kind is ReleaseKind.APPLICATION
            else request.current_client_version
        ),
    ]
    if process_started_at is not None:
        command.extend(["--process-started-at", str(process_started_at)])
    if request.artifact.sha256:
        command.extend(["--sha256", request.artifact.sha256])
    if request.kind is ReleaseKind.SOUNDS:
        command.extend(["--extract-dir", str(request.sounds_directory)])
        command.extend(["--version-file", SOUND_VERSION_FILE_NAME])
    return command


def launch_windows_updater(request: WindowsUpdaterLaunchRequest) -> Path:
    """Copy the packaged helper to temp and start it outside the update tree."""
    updater_path = find_packaged_updater(request.installation_directory)
    if updater_path is None:
        raise ReleaseUpdateError(
            "updater-not-found",
            path=str(request.installation_directory / UPDATER_RELATIVE_PATHS[0]),
        )

    helper_path = Path(tempfile.gettempdir()) / (
        f"{TEMPORARY_UPDATER_PREFIX}{uuid.uuid4().hex}{WINDOWS_EXECUTABLE_SUFFIX}"
    )
    try:
        shutil.copy2(updater_path, helper_path)
        try:
            process_started_at = psutil.Process(request.process_id).create_time()
        except (psutil.Error, OSError):
            process_started_at = None
        command = build_windows_updater_command(
            helper_path,
            request,
            process_started_at=process_started_at,
        )
        subprocess.Popen(command, close_fds=True)
    except Exception:
        helper_path.unlink(missing_ok=True)
        raise
    return helper_path
