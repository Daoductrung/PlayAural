from pathlib import Path
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import client_info


def test_client_auth_metadata_includes_canonical_windows_release_target(monkeypatch):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")
    monkeypatch.setattr(client_info, "get_client_platform_label", lambda: "Windows 11")

    assert client_info.client_auth_metadata() == {
        "client": "python",
        "platform": "Windows 11",
        "release_platform": "windows",
    }


def test_client_release_platform_maps_supported_desktop_operating_systems(
    monkeypatch,
):
    for system, expected in (
        ("Windows", "windows"),
        ("Darwin", "macos"),
        ("Linux", "linux"),
        ("FreeBSD", "unknown"),
    ):
        monkeypatch.setattr(client_info.platform, "system", lambda value=system: value)
        assert client_info.get_client_release_platform() == expected


def test_release_download_url_requires_https_and_matching_target(monkeypatch):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")
    valid_url = "https://downloads.example.com/PlayAural.zip"

    assert (
        client_info.get_release_download_url(
            {"target": "windows", "url": valid_url}
        )
        == valid_url
    )
    assert (
        client_info.get_release_download_url(
            {"target": "macos", "url": valid_url}
        )
        == ""
    )
    assert (
        client_info.get_release_download_url(
            {"target": "windows", "url": "http://example.com/update.zip"}
        )
        == ""
    )


def test_legacy_untargeted_download_is_windows_only(monkeypatch):
    url = "https://downloads.example.com/PlayAural.zip"

    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")
    assert client_info.get_release_download_url({"url": url}) == url

    monkeypatch.setattr(client_info.platform, "system", lambda: "Darwin")
    assert client_info.get_release_download_url({"url": url}) == ""
