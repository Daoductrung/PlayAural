"""Validated, platform-aware release artifact configuration."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit


RELEASE_TARGETS_BY_CLIENT_TYPE: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        "python": frozenset({"windows", "macos", "linux"}),
        "mobile": frozenset({"android", "ios", "web"}),
        "web": frozenset({"web"}),
    }
)
RELEASE_TARGETS = frozenset(
    target
    for targets in RELEASE_TARGETS_BY_CLIENT_TYPE.values()
    for target in targets
)


def _validated_download_url(value: str, field_name: str) -> str:
    """Return a normalized HTTPS download URL or an empty placeholder."""
    url = str(value or "").strip()
    if not url:
        return ""

    parsed = urlsplit(url)
    if (
        parsed.scheme.lower() != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(f"{field_name} must be an absolute HTTPS URL")
    return url


@dataclass(frozen=True, slots=True)
class ReleaseArtifacts:
    """Application and sound-pack artifacts for one canonical release target."""

    target: str
    update_url: str = ""
    sounds_url: str = ""
    update_hash: str = ""
    sounds_hash: str = ""

    def __post_init__(self) -> None:
        target = str(self.target or "").strip().lower()
        if target not in RELEASE_TARGETS:
            raise ValueError(f"Unknown release target: {target or '<empty>'}")

        object.__setattr__(self, "target", target)
        object.__setattr__(
            self,
            "update_url",
            _validated_download_url(self.update_url, "update_url"),
        )
        object.__setattr__(
            self,
            "sounds_url",
            _validated_download_url(self.sounds_url, "sounds_url"),
        )
        object.__setattr__(self, "update_hash", str(self.update_hash or "").strip())
        object.__setattr__(self, "sounds_hash", str(self.sounds_hash or "").strip())

    def update_packet(self, version: str) -> dict[str, str | bool]:
        """Return backward-compatible app update metadata for this target."""
        return {
            "version": str(version),
            "target": self.target,
            "available": bool(self.update_url),
            "url": self.update_url,
            "hash": self.update_hash,
        }

    def sounds_packet(self, version: str) -> dict[str, str | bool]:
        """Return backward-compatible sound update metadata for this target."""
        return {
            "version": str(version),
            "target": self.target,
            "available": bool(self.sounds_url),
            "url": self.sounds_url,
            "hash": self.sounds_hash,
        }


def freeze_release_registry(
    entries: Mapping[str, ReleaseArtifacts],
) -> Mapping[str, ReleaseArtifacts]:
    """Validate and freeze a complete release-target registry."""
    registry = dict(entries)
    missing = RELEASE_TARGETS.difference(registry)
    extra = set(registry).difference(RELEASE_TARGETS)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unknown: {', '.join(sorted(extra))}")
        raise ValueError(f"Invalid release registry ({'; '.join(details)})")

    for target, artifacts in registry.items():
        if artifacts.target != target:
            raise ValueError(
                f"Release registry key {target!r} does not match "
                f"artifact target {artifacts.target!r}"
            )
    return MappingProxyType(registry)


def resolve_release_target(
    client_type: str,
    release_platform: object = "",
    platform_label: object = "",
) -> str:
    """Resolve untrusted client metadata to an allowed canonical target.

    Current clients send ``release_platform``. The display-oriented
    ``platform_label`` fallback keeps the mandatory updater usable for clients
    from the immediately preceding release.
    """
    canonical_client = str(client_type or "").strip().lower()
    allowed_targets = RELEASE_TARGETS_BY_CLIENT_TYPE.get(canonical_client)
    if not allowed_targets:
        raise ValueError(f"Unknown client type: {canonical_client or '<empty>'}")

    if canonical_client == "web":
        return "web"

    requested_target = str(release_platform or "").strip().lower()
    if requested_target in allowed_targets:
        return requested_target

    label = str(platform_label or "").strip().lower()
    if canonical_client == "mobile":
        if "ios" in label or "ipad" in label:
            return "ios"
        if "web" in label:
            return "web"
        # Android is the only currently distributed native mobile client.
        return "android"

    if "windows" in label:
        return "windows"
    if "macos" in label or "darwin" in label or "mac os" in label:
        return "macos"
    if label:
        # The legacy desktop label reports the distribution name on Linux, so
        # any remaining non-empty desktop OS label is treated as Linux.
        return "linux"

    # Pre-platform-metadata desktop clients were Windows-only.
    return "windows"
