"""Stable filenames shared by the desktop client and standalone updater."""

from __future__ import annotations

import re
from pathlib import Path

RELEASE_KIND_APPLICATION = "application"
RELEASE_KIND_SOUNDS = "sounds"
RELEASE_DELIVERY_BROWSER = "browser"
RELEASE_DELIVERY_WINDOWS_ZIP = "windows_zip"
WINDOWS_RELEASE_TARGET = "windows"
DESKTOP_RELEASE_TARGETS = frozenset({WINDOWS_RELEASE_TARGET, "macos", "linux"})
WINDOWS_ARCHIVE_SUFFIX = ".zip"
WINDOWS_EXECUTABLE_SUFFIX = ".exe"
PYINSTALLER_INTERNAL_DIRECTORY = "_internal"
DEFAULT_LOCALE_TAG = "en"
MAXIMUM_LOCALE_TAG_LENGTH = 64
DEFAULT_RELEASE_DOWNLOAD_PREFIX = "playaural-release-"
APPLICATION_DOWNLOAD_PREFIX = "playaural-application-"
SOUNDS_DOWNLOAD_PREFIX = "playaural-sounds-"
UPDATER_EXECUTABLE_NAME = "updater.exe"
SOUND_VERSION_FILE_NAME = "version.txt"
SOUNDS_DIRECTORY_NAME = "sounds"
TEMPORARY_UPDATER_PREFIX = "playaural-updater-"

LOCALE_TAG_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


def is_valid_locale_tag(value: object) -> bool:
    """Return whether a locale is a bounded, path-safe BCP-47-style tag."""
    locale = str(value or "").strip()
    return bool(
        locale
        and len(locale) <= MAXIMUM_LOCALE_TAG_LENGTH
        and LOCALE_TAG_RE.fullmatch(locale)
    )


def is_valid_windows_executable_name(value: object) -> bool:
    """Return whether a value is one leaf Windows executable filename."""
    name = str(value or "").strip()
    return bool(
        name
        and Path(name).name == name
        and Path(name).suffix.lower() == WINDOWS_EXECUTABLE_SUFFIX
    )


def path_is_within(path: Path, parent: Path) -> bool:
    """Return whether a resolved path is the parent or one of its descendants."""
    resolved_path = Path(path).resolve()
    resolved_parent = Path(parent).resolve()
    return resolved_path == resolved_parent or resolved_parent in resolved_path.parents


def packaged_sounds_directory(installation_directory: Path) -> Path:
    """Return the sound tree used by the supported PyInstaller layouts."""
    installation_directory = Path(installation_directory).resolve()
    internal_directory = installation_directory / PYINSTALLER_INTERNAL_DIRECTORY
    content_directory = (
        internal_directory if internal_directory.is_dir() else installation_directory
    )
    return content_directory / SOUNDS_DIRECTORY_NAME
