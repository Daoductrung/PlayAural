"""Platform-neutral release metadata and delivery-strategy dispatch."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Protocol
from urllib.parse import urlsplit

from client_info import get_client_release_platform, is_safe_https_download_url
from update_contract import (
    DESKTOP_RELEASE_TARGETS,
    RELEASE_DELIVERY_BROWSER,
    RELEASE_DELIVERY_WINDOWS_ZIP,
    RELEASE_KIND_APPLICATION,
    RELEASE_KIND_SOUNDS,
    WINDOWS_ARCHIVE_SUFFIX,
    WINDOWS_RELEASE_TARGET,
)
from update_engine import UpdateInstallationError, validate_sha256


class ReleaseUpdateError(Exception):
    """A localized, user-actionable release update failure."""

    def __init__(self, message_id: str, **params: object) -> None:
        super().__init__(message_id)
        self.message_id = message_id
        self.params = params


class ReleaseKind(str, Enum):
    APPLICATION = RELEASE_KIND_APPLICATION
    SOUNDS = RELEASE_KIND_SOUNDS


class ReleaseDelivery(str, Enum):
    BROWSER = RELEASE_DELIVERY_BROWSER
    WINDOWS_ZIP = RELEASE_DELIVERY_WINDOWS_ZIP


def _compact(value: object) -> str:
    return " ".join(str(value or "").split())


@dataclass(frozen=True, slots=True)
class ReleaseArtifact:
    """Normalized release instructions accepted from the authenticated server."""

    target: str
    delivery: ReleaseDelivery
    url: str
    version: str
    sha256: str = ""

    def __post_init__(self) -> None:
        target = _compact(self.target).lower()
        url = _compact(self.url)
        version = _compact(self.version)
        try:
            delivery = ReleaseDelivery(self.delivery)
        except ValueError as error:
            raise ReleaseUpdateError("update-release-unsupported-delivery") from error
        if target not in DESKTOP_RELEASE_TARGETS:
            raise ReleaseUpdateError("update-release-invalid-target")
        if not is_safe_https_download_url(url):
            raise ReleaseUpdateError("update-release-invalid-url")
        if not version:
            raise ReleaseUpdateError("update-release-invalid-version")
        try:
            sha256 = validate_sha256(self.sha256)
        except UpdateInstallationError as error:
            raise ReleaseUpdateError("update-release-invalid-hash") from error

        object.__setattr__(self, "target", target)
        object.__setattr__(self, "delivery", delivery)
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "sha256", sha256)

    @classmethod
    def from_packet(cls, info: object) -> "ReleaseArtifact":
        if not isinstance(info, Mapping):
            raise ReleaseUpdateError("update-release-invalid-metadata")
        if info.get("available") is False:
            raise ReleaseUpdateError("update-release-unavailable")

        current_target = get_client_release_platform()
        packet_target = _compact(info.get("target", "")).lower()
        if packet_target:
            if packet_target != current_target:
                raise ReleaseUpdateError("update-release-target-mismatch")
            target = packet_target
        elif current_target == WINDOWS_RELEASE_TARGET:
            # Releases predating explicit platform delivery were Windows-only.
            target = WINDOWS_RELEASE_TARGET
        else:
            raise ReleaseUpdateError("update-release-invalid-target")

        raw_delivery = _compact(info.get("delivery", "")).lower()
        if not raw_delivery and target == WINDOWS_RELEASE_TARGET:
            # Preserve one-release updater compatibility without making ZIP
            # extraction the default for any future operating system.
            raw_delivery = RELEASE_DELIVERY_WINDOWS_ZIP
        try:
            delivery = ReleaseDelivery(raw_delivery)
        except ValueError as error:
            raise ReleaseUpdateError("update-release-unsupported-delivery") from error

        return cls(
            target=target,
            delivery=delivery,
            url=_compact(info.get("url", "")),
            version=_compact(info.get("version", "")),
            sha256=_compact(info.get("hash", "")),
        )


class ReleaseUpdateHost(Protocol):
    """UI operations that delivery strategies may request."""

    def begin_windows_zip_update(
        self,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None: ...

    def open_release_in_browser(
        self,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ReleaseUpdateStrategy:
    delivery: ReleaseDelivery
    supported_targets: frozenset[str]
    supported_kinds: frozenset[ReleaseKind]
    supports_sha256: bool

    def validate(self, artifact: ReleaseArtifact, kind: ReleaseKind) -> None:
        current_target = get_client_release_platform()
        if (
            artifact.delivery is not self.delivery
            or artifact.target != current_target
            or artifact.target not in self.supported_targets
        ):
            raise ReleaseUpdateError("update-release-delivery-platform-mismatch")
        if kind not in self.supported_kinds:
            raise ReleaseUpdateError("update-release-delivery-kind-mismatch")
        if artifact.sha256 and not self.supports_sha256:
            raise ReleaseUpdateError("update-release-hash-unsupported")

    def begin(
        self,
        host: ReleaseUpdateHost,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None:
        raise NotImplementedError


class WindowsZipUpdateStrategy(ReleaseUpdateStrategy):
    def validate(self, artifact: ReleaseArtifact, kind: ReleaseKind) -> None:
        super().validate(artifact, kind)
        if not urlsplit(artifact.url).path.lower().endswith(WINDOWS_ARCHIVE_SUFFIX):
            raise ReleaseUpdateError("update-release-windows-zip-required")

    def begin(
        self,
        host: ReleaseUpdateHost,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None:
        self.validate(artifact, kind)
        host.begin_windows_zip_update(artifact, kind)


class BrowserUpdateStrategy(ReleaseUpdateStrategy):
    def begin(
        self,
        host: ReleaseUpdateHost,
        artifact: ReleaseArtifact,
        kind: ReleaseKind,
    ) -> None:
        self.validate(artifact, kind)
        host.open_release_in_browser(artifact, kind)


ALL_RELEASE_KINDS = frozenset(ReleaseKind)
RELEASE_UPDATE_STRATEGIES: Mapping[
    ReleaseDelivery,
    ReleaseUpdateStrategy,
] = MappingProxyType(
    {
        ReleaseDelivery.WINDOWS_ZIP: WindowsZipUpdateStrategy(
            delivery=ReleaseDelivery.WINDOWS_ZIP,
            supported_targets=frozenset({WINDOWS_RELEASE_TARGET}),
            supported_kinds=ALL_RELEASE_KINDS,
            supports_sha256=True,
        ),
        ReleaseDelivery.BROWSER: BrowserUpdateStrategy(
            delivery=ReleaseDelivery.BROWSER,
            supported_targets=DESKTOP_RELEASE_TARGETS,
            supported_kinds=ALL_RELEASE_KINDS,
            supports_sha256=False,
        ),
    }
)


def resolve_release_update_strategy(
    artifact: ReleaseArtifact,
    kind: ReleaseKind,
) -> ReleaseUpdateStrategy:
    """Resolve and validate the configured strategy for one artifact."""
    strategy = RELEASE_UPDATE_STRATEGIES.get(artifact.delivery)
    if strategy is None:
        raise ReleaseUpdateError("update-release-unsupported-delivery")
    strategy.validate(artifact, kind)
    return strategy
