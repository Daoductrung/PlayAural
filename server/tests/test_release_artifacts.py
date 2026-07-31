import pytest

from server.core.release_artifacts import (
    RELEASE_TARGETS,
    ReleaseArtifacts,
    freeze_release_registry,
    resolve_release_target,
)
from server.core.server import (
    ANDROID_UPDATE_URL,
    CLIENT_RELEASE_ARTIFACTS,
    SOUNDS_URL,
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
    assert windows.update_url == UPDATE_URL
    assert windows.sounds_url == SOUNDS_URL


def test_android_app_and_bundled_sounds_use_the_android_artifact():
    android = CLIENT_RELEASE_ARTIFACTS["android"]
    assert android.update_url == ANDROID_UPDATE_URL
    assert android.sounds_url == ANDROID_UPDATE_URL
    assert android.update_packet("1")["available"] is True
    assert android.sounds_packet("2")["available"] is True


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
        ReleaseArtifacts(target="windows", update_url=url)


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
