from pathlib import Path
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from localization import Localization


def test_set_locale_reloads_client_bundle_without_restart(tmp_path):
    en_dir = tmp_path / "en"
    vi_dir = tmp_path / "vi"
    en_dir.mkdir()
    vi_dir.mkdir()
    (en_dir / "client.ftl").write_text(
        "dynamic-label = English label\nfallback-only = Fallback value\n",
        encoding="utf-8",
    )
    (vi_dir / "client.ftl").write_text(
        "dynamic-label = Nhãn tiếng Việt\n",
        encoding="utf-8",
    )

    Localization.init(locales_dir=tmp_path, locale="en")
    assert Localization.get("dynamic-label") == "English label"

    changed = Localization.set_locale("vi")

    assert changed is True
    assert Localization.current_locale() == "vi"
    assert Localization.get("dynamic-label") == "Nhãn tiếng Việt"
    assert Localization.get("fallback-only") == "Fallback value"


def test_inaccurate_community_username_help_falls_back_to_english():
    Localization.init(locales_dir=CLIENT_DIR / "locales", locale="es")
    try:
        assert Localization.get("reg-username-help") == (
            "Use letters, numbers, and single spaces. Vietnamese names are "
            "supported; do not use consecutive spaces or special characters."
        )
    finally:
        Localization.set_locale("en")
