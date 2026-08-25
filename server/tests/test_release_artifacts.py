import pytest

from server.core.release_artifacts import (
    RELEASE_DELIVERY_BROWSER,
    RELEASE_DELIVERY_WINDOWS_ZIP,
    RELEASE_KIND_APPLICATION,
    RELEASE_KIND_SOUNDS,
    RELEASE_TARGETS,
    ReleaseArtifact,
    ReleaseArtifacts,
    freeze_release_registry,
    resolve_release_target,
)
from server.core.server import (
    ANDROID_UPDATE_URL,
    CLIENT_RELEASE_ARTIFACTS,
    SOUNDS_HASH,
    SOUNDS_URL,
    UPDATE_HASH,
    UPDATE_URL,
)


def test_release_registry_covers_every_canonical_target():
    assert set(CLIENT_RELEASE_ARTIFACTS) == set(RELEASE_TARGETS)
    with pytest.raises(TypeError):
        CLIENT_RELEASE_ARTIFACTS["windows"] = ReleaseArtifacts(target="windows")


def test_windows_registry_retains_exact_legacy_release_urls():
    assert (
        UPDATE_URL
        == "https://github.com/Daoductrung/PlayAural/releases/latest/download/PlayAural.zip"
    )
    assert (
        SOUNDS_URL
        == "https://github.com/Daoductrung/PlayAural/releases/latest/download/sounds.zip"
    )
    windows = CLIENT_RELEASE_ARTIFACTS["windows"]
    assert windows.application.url == UPDATE_URL
    assert windows.application.delivery == RELEASE_DELIVERY_WINDOWS_ZIP
    assert windows.application.sha256 == UPDATE_HASH == ""
    assert windows.sounds.url == SOUNDS_URL
    assert windows.sounds.delivery == RELEASE_DELIVERY_WINDOWS_ZIP
    assert windows.sounds.sha256 == SOUNDS_HASH == ""


def test_android_app_and_bundled_sounds_use_the_android_artifact():
    android = CLIENT_RELEASE_ARTIFACTS["android"]
    assert android.application.url == ANDROID_UPDATE_URL
    assert android.sounds.url == ANDROID_UPDATE_URL
    assert android.packet(RELEASE_KIND_APPLICATION, "1")["available"] is True
    assert android.packet(RELEASE_KIND_SOUNDS, "2")["available"] is True
    assert android.application.delivery == RELEASE_DELIVERY_BROWSER
    assert android.sounds.delivery == RELEASE_DELIVERY_BROWSER


@pytest.mark.parametrize(
    ("client_type", "release_platform", "platform_label", "expected"),
    [
        ("python", "windows", "Windows 11 x86_64", "windows"),
        ("python", "macos", "macOS 15 arm64", "macos"),
        ("python", "linux", "Ubuntu 24.04 x86_64", "linux"),
        ("mobile", "android", "Android 16 (API 36)", "android"),
        ("mobile", "ios", "iOS 19", "ios"),
        ("mobile", "web", "Web", "web"),
        # Browser host OS must never select a native installer.
        ("web", "windows", "Windows", "web"),
        # A target from the wrong client family is ignored.
        ("mobile", "windows", "Android 16 (API 36)", "android"),
        ("python", "android", "macOS 15 arm64", "macos"),
        # Immediately preceding clients do not send release_platform.
        ("python", "", "Windows 11 x86_64", "windows"),
        ("python", "", "Ubuntu 24.04 x86_64", "linux"),
        ("mobile", "", "Android 15 (API 35)", "android"),
        ("python", "", "", "windows"),
        ("mobile", "", "", "android"),
    ],
)
def test_release_target_resolution_is_client_family_aware(
    client_type,
    release_platform,
    platform_label,
    expected,
):
    assert (
        resolve_release_target(client_type, release_platform, platform_label)
        == expected
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/update.zip",
        "file:///tmp/update.zip",
        "/relative/update.zip",
        "https://user:secret@example.com/update.zip",
    ],
)
def test_release_artifacts_reject_unsafe_download_urls(url):
    with pytest.raises(ValueError):
        ReleaseArtifact(url=url, delivery=RELEASE_DELIVERY_WINDOWS_ZIP)


@pytest.mark.parametrize(
    "digest",
    ["not-a-hash", "a" * 63, "g" * 64],
)
def test_release_artifacts_reject_malformed_sha256_digests(digest):
    with pytest.raises(ValueError, match="SHA-256"):
        ReleaseArtifact(
            url="https://example.com/update.zip",
            delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
            sha256=digest,
        )


def test_release_artifacts_normalize_sha256_digests():
    digest = "A" * 64
    artifacts = ReleaseArtifacts(
        target="windows",
        application=ReleaseArtifact(
            url="https://example.com/update.zip",
            delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
            sha256=digest,
        ),
        sounds=ReleaseArtifact(
            url="https://example.com/sounds.zip",
            delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
            sha256=digest,
        ),
    )

    assert artifacts.packet(RELEASE_KIND_APPLICATION, "1")["hash"] == digest.lower()
    assert artifacts.packet(RELEASE_KIND_SOUNDS, "2")["hash"] == digest.lower()


def test_sha256_is_optional_and_packets_keep_it_empty_when_omitted():
    artifact = ReleaseArtifact(
        url="https://example.com/update.zip",
        delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
    )
    packet = artifact.packet(version="1", target="windows")

    assert packet["available"] is True
    assert packet["hash"] == ""


def test_unavailable_artifacts_do_not_invent_delivery_or_checksum_metadata():
    packet = ReleaseArtifact().packet(version="1", target="macos")

    assert packet == {
        "version": "1",
        "target": "macos",
        "available": False,
        "url": "",
        "delivery": "",
        "hash": "",
    }


def test_artifact_packet_rejects_empty_versions_and_unknown_targets():
    artifact = ReleaseArtifact()
    with pytest.raises(ValueError, match="version"):
        artifact.packet(version="", target="windows")
    with pytest.raises(ValueError, match="target"):
        artifact.packet(version="1", target="unknown")


def test_delivery_is_independent_for_application_and_sound_artifacts():
    artifacts = ReleaseArtifacts(
        target="macos",
        application=ReleaseArtifact(
            url="https://example.com/application",
            delivery=RELEASE_DELIVERY_BROWSER,
        ),
        sounds=ReleaseArtifact(
            url="https://example.com/sounds",
            delivery=RELEASE_DELIVERY_BROWSER,
        ),
    )

    assert artifacts.packet(RELEASE_KIND_APPLICATION, "1")["delivery"] == "browser"
    assert artifacts.packet(RELEASE_KIND_SOUNDS, "2")["delivery"] == "browser"


def test_windows_zip_delivery_is_rejected_for_non_windows_targets():
    with pytest.raises(ValueError, match="does not support"):
        ReleaseArtifacts(
            target="macos",
            application=ReleaseArtifact(
                url="https://example.com/update.zip",
                delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
            ),
        )


def test_windows_zip_delivery_requires_a_zip_url():
    with pytest.raises(ValueError, match="ZIP"):
        ReleaseArtifact(
            url="https://example.com/update.exe",
            delivery=RELEASE_DELIVERY_WINDOWS_ZIP,
        )


def test_browser_delivery_cannot_silently_ignore_a_checksum():
    with pytest.raises(ValueError, match="cannot enforce SHA-256"):
        ReleaseArtifact(
            url="https://example.com/download",
            delivery=RELEASE_DELIVERY_BROWSER,
            sha256="a" * 64,
        )


def test_release_registry_rejects_missing_or_mismatched_targets():
    with pytest.raises(ValueError, match="missing"):
        freeze_release_registry(
            {"windows": ReleaseArtifacts(target="windows")}
        )

    complete = {
        target: ReleaseArtifacts(target=target)
        for target in RELEASE_TARGETS
    }
    complete["windows"] = ReleaseArtifacts(target="linux")
    with pytest.raises(ValueError, match="does not match"):
        freeze_release_registry(complete)
