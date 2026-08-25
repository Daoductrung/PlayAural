"""Validated, platform-aware release delivery configuration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit


RELEASE_KIND_APPLICATION = "application"
RELEASE_KIND_SOUNDS = "sounds"

RELEASE_DELIVERY_BROWSER = "browser"
RELEASE_DELIVERY_WINDOWS_ZIP = "windows_zip"
WINDOWS_ZIP_SUFFIX = ".zip"

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
RELEASE_TARGETS_BY_DELIVERY: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        RELEASE_DELIVERY_BROWSER: RELEASE_TARGETS,
        RELEASE_DELIVERY_WINDOWS_ZIP: frozenset({"windows"}),
    }
)
SHA256_DELIVERIES = frozenset({RELEASE_DELIVERY_WINDOWS_ZIP})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _validated_sha256(value: str, field_name: str) -> str:
    """Normalize an optional SHA-256 digest, validating only when supplied."""
    digest = str(value or "").strip().lower()
    if digest and not SHA256_RE.fullmatch(digest):
        raise ValueError(f"{field_name} must be a 64-character SHA-256 digest")
    return digest


@dataclass(frozen=True, slots=True)
class ReleaseArtifact:
    """Delivery instructions for one application or sound-pack artifact."""

    url: str = ""
    delivery: str = ""
    sha256: str = ""

    def __post_init__(self) -> None:
        url = _validated_download_url(self.url, "url")
        delivery = str(self.delivery or "").strip().lower()
        sha256 = _validated_sha256(self.sha256, "sha256")

        if not url:
            if delivery or sha256:
                raise ValueError(
                    "Unavailable release artifacts cannot define delivery or SHA-256"
                )
        elif delivery not in RELEASE_TARGETS_BY_DELIVERY:
            raise ValueError(
                f"Unknown release delivery: {delivery or '<empty>'}"
            )
        elif (
            delivery == RELEASE_DELIVERY_WINDOWS_ZIP
            and not urlsplit(url).path.lower().endswith(WINDOWS_ZIP_SUFFIX)
        ):
            raise ValueError("Windows ZIP release artifacts must use a .zip URL")
        elif sha256 and delivery not in SHA256_DELIVERIES:
            raise ValueError(
                f"Delivery {delivery!r} cannot enforce SHA-256 validation"
            )

        object.__setattr__(self, "url", url)
        object.__setattr__(self, "delivery", delivery)
        object.__setattr__(self, "sha256", sha256)

    @property
    def available(self) -> bool:
        return bool(self.url)

    def packet(self, *, version: str, target: str) -> dict[str, str | bool]:
        """Serialize this artifact without inventing a checksum or delivery."""
        normalized_version = str(version or "").strip()
        normalized_target = str(target or "").strip().lower()
        if not normalized_version:
            raise ValueError("Release artifact version cannot be empty")
        if normalized_target not in RELEASE_TARGETS:
            raise ValueError(f"Unknown release target: {normalized_target or '<empty>'}")
        if (
            self.available
            and normalized_target not in RELEASE_TARGETS_BY_DELIVERY[self.delivery]
        ):
            raise ValueError(
                f"Delivery {self.delivery!r} does not support target "
                f"{normalized_target!r}"
            )
        return {
            "version": normalized_version,
            "target": normalized_target,
            "available": self.available,
            "url": self.url,
            "delivery": self.delivery,
            "hash": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class ReleaseArtifacts:
    """Application and sound-pack delivery configuration for one target."""

    target: str
    application: ReleaseArtifact = field(default_factory=ReleaseArtifact)
    sounds: ReleaseArtifact = field(default_factory=ReleaseArtifact)

    def __post_init__(self) -> None:
        target = str(self.target or "").strip().lower()
        if target not in RELEASE_TARGETS:
            raise ValueError(f"Unknown release target: {target or '<empty>'}")
        object.__setattr__(self, "target", target)

        for artifact in (self.application, self.sounds):
            if not isinstance(artifact, ReleaseArtifact):
                raise TypeError("Release artifact entries must be ReleaseArtifact values")
            if (
                artifact.available
                and target not in RELEASE_TARGETS_BY_DELIVERY[artifact.delivery]
            ):
                raise ValueError(
                    f"Delivery {artifact.delivery!r} does not support target {target!r}"
                )

    def packet(self, kind: str, version: str) -> dict[str, str | bool]:
        """Return release metadata for one validated artifact kind."""
        if kind == RELEASE_KIND_APPLICATION:
            artifact = self.application
        elif kind == RELEASE_KIND_SOUNDS:
            artifact = self.sounds
        else:
            raise ValueError(f"Unknown release artifact kind: {kind!r}")
        return artifact.packet(version=version, target=self.target)


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
