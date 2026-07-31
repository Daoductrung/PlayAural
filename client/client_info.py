"""Runtime client metadata sent during authentication."""

from __future__ import annotations

import platform
import sys
from collections.abc import Mapping
from urllib.parse import urlsplit


def _compact(text: str) -> str:
    return " ".join(str(text or "").split())


def _machine_suffix() -> str:
    machine = _compact(platform.machine())
    return machine if machine else ""


def _windows_release() -> str:
    try:
        version = sys.getwindowsversion()
    except AttributeError:
        return _compact(platform.release())

    if version.major == 10 and version.build >= 22000:
        return "11"
    if version.major == 10:
        return "10"
    if version.major == 6 and version.minor == 3:
        return "8.1"
    release = _compact(platform.release())
    return release if release else f"{version.major}.{version.minor}"


def get_client_platform_label() -> str:
    """Return a concise OS label for online presence display."""
    system = _compact(platform.system())
    machine = _machine_suffix()

    if system == "Windows":
        parts = ["Windows", _windows_release(), machine]
    elif system == "Darwin":
        mac_version = _compact(platform.mac_ver()[0])
        parts = ["macOS", mac_version, machine]
    elif system == "Linux":
        linux_name = ""
        freedesktop_os_release = getattr(platform, "freedesktop_os_release", None)
        if freedesktop_os_release:
            try:
                os_release = freedesktop_os_release()
                linux_name = _compact(
                    os_release.get("PRETTY_NAME") or os_release.get("NAME") or ""
                )
            except OSError:
                linux_name = ""
        if not linux_name:
            linux_name = _compact(platform.platform(aliased=True, terse=True))
        parts = [linux_name or "Linux", machine]
    else:
        release = _compact(platform.release())
        parts = [system or "Unknown OS", release, machine]

    return _compact(" ".join(part for part in parts if part))[:60]


def get_client_release_platform() -> str:
    """Return the canonical platform key used to select release artifacts."""
    system = _compact(platform.system()).lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "macos"
    if system == "linux":
        return "linux"
    return "unknown"


def client_auth_metadata(client: str = "python") -> dict[str, str]:
    """Return standardized client metadata for auth-related packets."""
    metadata = {
        "client": client,
        "release_platform": get_client_release_platform(),
    }
    platform_label = get_client_platform_label()
    if platform_label:
        metadata["platform"] = platform_label
    return metadata


def get_release_download_url(info: object) -> str:
    """Return a safe download URL addressed to this desktop platform.

    Packets from the immediately preceding server release have no target. They
    are accepted only by Windows, which was the only distributed desktop build.
    """
    if not isinstance(info, Mapping):
        return ""

    current_target = get_client_release_platform()
    packet_target = _compact(info.get("target", "")).lower()
    if packet_target:
        if packet_target != current_target:
            return ""
    elif current_target != "windows":
        return ""

    url = _compact(info.get("url", ""))
    if not url:
        return ""
    parsed = urlsplit(url)
    if (
        parsed.scheme.lower() != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        return ""
    return url
