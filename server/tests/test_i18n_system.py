from pathlib import Path

from server.documentation.manager import DocumentationManager
from server.messages.localization import DEFAULT_LOCALE, Localization
from server.tools.compare_locales import compare_locale


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_localization_falls_back_per_missing_key_and_base_locale(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(
        locales_dir / "en" / "main.ftl",
        """
language-en = English
language-fr = French
hello = Hello, { $name }.
only-english = English fallback
""".strip(),
    )
    _write(
        locales_dir / "fr" / "main.ftl",
        """
language-fr = Francais
hello = Bonjour, { $name }.
""".strip(),
    )

    Localization.init(locales_dir)

    assert Localization.get("fr-CA", "hello", name="Ada") == "Bonjour, Ada."
    assert Localization.get("fr", "only-english") == "English fallback"
    assert Localization.get("zz", "only-english") == "English fallback"
    assert Localization.get("fr", "missing-key") == "missing-key"
    assert Localization.resolve_locale("fr-CA") == "fr"
    assert Localization.resolve_locale("zz") == DEFAULT_LOCALE


def test_available_languages_uses_installed_dirs_and_safe_fallbacks(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(
        locales_dir / "en" / "main.ftl",
        """
language-en = English
language-vi = Vietnamese
language-fr = French
""".strip(),
    )
    _write(
        locales_dir / "fr" / "main.ftl",
        """
language-fr = Francais
""".strip(),
    )
    _write(
        locales_dir / "vi" / "main.ftl",
        """
language-vi = Tieng Viet
""".strip(),
    )
    _write(
        locales_dir / "es" / "main.ftl",
        """
hello = Hola
""".strip(),
    )
    _write(
        locales_dir / "es" / "metadata.json",
        """
{
  "name": "Spanish",
  "native_name": "Espanol",
  "translators": ["Elena"],
  "official": false
}
""".strip(),
    )

    Localization.init(locales_dir)

    assert list(Localization.get_available_languages("fr")) == ["en", "vi", "es", "fr"]
    assert Localization.get_available_languages("fr") == {
        "en": "English",
        "vi": "Vietnamese",
        "es": "Espanol",
        "fr": "Francais",
    }
    assert Localization.get_available_languages() == {
        "en": "English",
        "vi": "Tieng Viet",
        "es": "Espanol",
        "fr": "Francais",
    }
    metadata = Localization.get_locale_metadata("es")
    assert metadata.available is True
    assert metadata.native_name == "Espanol"
    assert metadata.translators == ("Elena",)
    assert metadata.official is False


def test_documentation_manager_resolves_base_locale_and_falls_back(tmp_path):
    content_dir = tmp_path / "content"
    _write(content_dir / "en" / "intro.md", "# Welcome\n\nEnglish intro")
    _write(content_dir / "en" / "games" / "sample.md", "# Sample\n\nEnglish rules")
    _write(content_dir / "vi" / "intro.md", "# Xin chao\n\nVietnamese intro")

    manager = DocumentationManager(base_path=content_dir)

    assert "Vietnamese intro" in (manager.get_document("intro", "vi-VN") or "")
    assert "English rules" in (manager.get_document("games/sample", "vi") or "")
    assert "English intro" in (manager.get_document("intro", "../vi") or "")
    assert manager.get_document("../intro", "en") is None


def test_compare_locales_reports_missing_obsolete_and_structural_drift(tmp_path):
    locales_dir = tmp_path / "locales"
    source_dir = locales_dir / "en"
    target_dir = locales_dir / "vi"
    _write(
        source_dir / "main.ftl",
        """
keep = Keep { $count }
duplicate = Keep one definition
choice =
    { $count ->
        [one] One point
       *[other] { $count } points
    }
attrs =
    .label = Label
""".strip(),
    )
    _write(source_dir / "extra.ftl", "source-only = Source only")
    _write(
        target_dir / "main.ftl",
        """
keep = Giu
duplicate = Giu mot
duplicate = Giu hai
choice =
    { $count ->
       *[other] { $count } diem
    }
attrs =
old-key = Old
""".strip(),
    )
    _write(target_dir / "obsolete.ftl", "obsolete-file-key = Old file")
    _write(
        target_dir / "metadata.json",
        """
{
  "code": "vi",
  "translators": ["Lan"]
}
""".strip(),
    )

    report = compare_locale(source_dir, target_dir, "en", "vi")

    assert report.has_issues
    assert report.missing_files == [Path("extra.ftl")]
    assert report.obsolete_files == [Path("obsolete.ftl")]
    assert report.metadata_errors == []
    [file_report] = report.file_reports
    assert ("target", "duplicate") in {
        (label, key) for label, key, _lines in file_report.duplicate_keys
    }
    assert file_report.obsolete_keys == ["old-key"]
    assert file_report.variable_mismatches == [("keep", ["count"], [])]
    assert file_report.variant_mismatches == [("choice", ["one", "other"], ["other"])]
    assert file_report.attribute_mismatches == [("attrs", ["label"], [])]


def test_compare_locales_reports_cross_file_duplicate_keys(tmp_path):
    locales_dir = tmp_path / "locales"
    source_dir = locales_dir / "en"
    target_dir = locales_dir / "vi"
    _write(source_dir / "main.ftl", "shared-key = Source one")
    _write(source_dir / "games.ftl", "shared-key = Source two")
    _write(target_dir / "main.ftl", "shared-key = Target one")
    _write(target_dir / "games.ftl", "shared-key = Target two")
    _write(
        target_dir / "metadata.json",
        """
{
  "code": "vi",
  "translators": ["Lan"]
}
""".strip(),
    )

    report = compare_locale(source_dir, target_dir, "en", "vi")

    assert report.has_issues
    assert ("source", "shared-key") in {
        (label, key) for label, key, _locations in report.duplicate_keys
    }
    assert ("target", "shared-key") in {
        (label, key) for label, key, _locations in report.duplicate_keys
    }


def test_language_menu_pins_defaults_and_displays_translator_metadata():
    from server.core.server import Server
    from server.users.test_user import MockUser

    server = Server(db_path=":memory:")
    user = MockUser("Reader", locale="en")

    server._show_language_menu(user)

    items = user.get_current_menu_items("language_menu") or []
    rows = {item.id: item.text for item in items if hasattr(item, "id")}
    ids = [item.id for item in items if hasattr(item, "id")]

    assert ids[:2] == ["lang_en", "lang_vi"]
    assert rows["lang_en"].startswith("Current: English.")
    assert "Official PlayAural language" in rows["lang_en"]
    assert "Translators: PlayAural core team" in rows["lang_en"]
    assert rows["lang_vi"].startswith("Vietnamese (Tiếng Việt).")
    assert "Translators: Trung and PlayAural core team" in rows["lang_vi"]
    assert ids[-1] == "back"
