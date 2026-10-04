from pathlib import Path

import pytest

from server.documentation.manager import DocumentationManager
from server.messages.localization import (
    DEFAULT_LOCALE,
    LOCALE_RESOLUTION_CACHE_SIZE,
    Localization,
)
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
    assert Localization.has_message("fr", "hello") is True
    assert Localization.has_message("fr", "only-english") is True
    assert Localization.has_message("fr", "missing-key") is False
    assert Localization.resolve_locale("fr-CA") == "fr"
    assert Localization.resolve_locale("zz") == DEFAULT_LOCALE


def test_attribute_collection_uses_stable_per_attribute_fallback(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(
        locales_dir / "en" / "main.ftl",
        """
names =
    .name-001 = First English
    .name-002 = Second English
""".strip(),
    )
    _write(
        locales_dir / "vi" / "main.ftl",
        """
names =
    .name-001 = Tên thứ nhất
    .name-003 = Tên bổ sung
""".strip(),
    )

    Localization.init(locales_dir)

    assert Localization.get_message_attribute_values("vi", "names") == (
        "Tên thứ nhất",
        "Second English",
        "Tên bổ sung",
    )
    assert Localization.get_message_attribute_values("unknown", "names") == (
        "First English",
        "Second English",
    )
    assert Localization.get_message_attribute_values("vi", "names.bad") == ()


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


def test_locale_catalog_cache_refreshes_explicitly_and_on_init(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(locales_dir / "en" / "main.ftl", "hello = Hello")
    _write(locales_dir / "vi" / "main.ftl", "hello = Xin chao")

    Localization.init(locales_dir)
    assert Localization.available_locale_codes() == ["en", "vi"]
    assert Localization.resolve_locale("fr") == "en"

    _write(locales_dir / "fr" / "main.ftl", "hello = Bonjour")
    # Runtime formatting stays filesystem-free until configuration explicitly
    # changes; both refresh paths invalidate locale fallback results as well.
    assert Localization.available_locale_codes() == ["en", "vi"]
    assert Localization.resolve_locale("fr") == "en"

    Localization.refresh_locale_catalog()
    assert Localization.available_locale_codes() == ["en", "vi", "fr"]
    assert Localization.resolve_locale("fr") == "fr"

    _write(locales_dir / "es" / "main.ftl", "hello = Hola")
    Localization.init(locales_dir)
    assert Localization.available_locale_codes() == ["en", "vi", "es", "fr"]


def test_locale_resolution_cache_is_bounded_for_untrusted_locale_values(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(locales_dir / "en" / "main.ftl", "hello = Hello")
    Localization.init(locales_dir)

    for index in range(LOCALE_RESOLUTION_CACHE_SIZE * 2):
        assert Localization.resolve_locale(f"unknown-{index}") == "en"

    assert (
        Localization._resolve_locale_from_catalog.cache_info().currsize
        == LOCALE_RESOLUTION_CACHE_SIZE
    )


def test_bundle_cache_only_retains_installed_locale_codes(tmp_path):
    locales_dir = tmp_path / "locales"
    _write(locales_dir / "en" / "main.ftl", "hello = Hello")
    Localization.init(locales_dir)

    for index in range(LOCALE_RESOLUTION_CACHE_SIZE * 2):
        assert Localization.get(f"unknown-{index}", "hello") == "Hello"

    assert set(Localization._bundles) == {"en"}


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
gender-optional = { $player } ends { GENDER_TERM($player_gender, "possessive-determiner") } turn.
gender-renamed = { $player } ends { GENDER_TERM($player_gender, "possessive-determiner") } turn.
formatted-number = { NUMBER($value, maximumFractionDigits: 1) } MiB
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
gender-optional = { $player } ket thuc luot.
gender-renamed = { $player } ket thuc luot { GENDER_TERM($wrong_gender, "possessive-determiner") }.
formatted-number = MiB
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
    assert file_report.variable_mismatches == [
        ("formatted-number", ["value"], []),
        (
            "gender-renamed",
            ["player", "player_gender"],
            ["player", "wrong_gender"],
        ),
        ("keep", ["count"], []),
    ]
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


@pytest.mark.asyncio
async def test_language_change_rebuilds_active_game_ui_and_restores_focus():
    from server.core.server import Server
    from server.games.pig.game import PigGame
    from server.users.network_user import NetworkUser
    from server.users.test_user import MockUser

    class Connection:
        def __init__(self):
            self.sent_messages = []

        async def send(self, packet):
            self.sent_messages.append(packet)

    server = Server(db_path=":memory:")
    server._db.connect()
    record = server._db.create_user(
        "Reader",
        "hash",
        locale="en",
        approved=True,
        email="reader@example.com",
    )
    assert record is not None
    connection = Connection()
    reader = NetworkUser(
        record.username,
        "en",
        connection,
        uuid=record.uuid,
        approved=True,
    )
    observer = MockUser("Observer", locale="en", uuid="observer-id")
    server._users = {reader.username: reader, observer.username: observer}

    table = server._tables.create_table("pig", reader.username, reader)
    game = PigGame()
    table.game = game
    game._table = table
    game.initialize_lobby(reader.username, reader)
    assert table.add_member(observer.username, observer)
    observer_player = game.add_player(observer.username, observer)
    reader_player = game.get_player_by_id(reader.uuid)
    assert reader_player is not None
    assert game.find_action(reader_player, "leave_game").label == "Leave table"
    assert game.find_action(observer_player, "leave_game").label == "Leave table"

    server._user_states[reader.username] = {
        "menu": "language_menu",
        "_stack": [
            {
                "menu": "in_game",
                "table_id": table.table_id,
                "_game_return_focus_id": "start_game",
            }
        ],
    }

    await server._handle_language_selection(reader, "lang_vi")

    assert reader.locale == "vi"
    assert server._db.get_user(reader.username).locale == "vi"
    assert connection.sent_messages == [
        {"type": "update_locale", "locale": "vi"}
    ]
    assert game.find_action(reader_player, "leave_game").label == "Rời bàn"
    assert game.find_action(observer_player, "leave_game").label == "Leave table"
    assert server._user_states[reader.username] == {
        "menu": "in_game",
        "table_id": table.table_id,
    }
    turn_menu = reader._current_menus["turn_menu"]
    assert any(
        item["id"] == "start_game"
        and item["text"] == Localization.get("vi", "start-game")
        for item in turn_menu["items"]
    )
    assert any(
        packet.get("type") == "menu"
        and packet.get("menu_id") == "turn_menu"
        and packet.get("selection_id") == "start_game"
        for packet in reader._message_queue
    )


@pytest.mark.asyncio
async def test_language_change_rejects_unavailable_locale_without_mutation():
    from server.core.server import Server
    from server.users.network_user import NetworkUser

    class Connection:
        def __init__(self):
            self.sent_messages = []

        async def send(self, packet):
            self.sent_messages.append(packet)

    server = Server(db_path=":memory:")
    server._db.connect()
    record = server._db.create_user(
        "Reader",
        "hash",
        locale="en",
        approved=True,
        email="reader@example.com",
    )
    assert record is not None
    connection = Connection()
    reader = NetworkUser(
        record.username,
        "en",
        connection,
        uuid=record.uuid,
        approved=True,
    )
    server._users[reader.username] = reader
    server._user_states[reader.username] = {
        "menu": "language_menu",
        "_stack": [{"menu": "main_menu"}],
    }

    await server._handle_language_selection(reader, "lang_not-installed")

    assert reader.locale == "en"
    assert server._db.get_user(reader.username).locale == "en"
    assert connection.sent_messages == []


@pytest.mark.asyncio
async def test_language_change_keeps_live_locale_when_persistence_fails(monkeypatch):
    from server.core.server import Server
    from server.users.network_user import NetworkUser

    class Connection:
        def __init__(self):
            self.sent_messages = []

        async def send(self, packet):
            self.sent_messages.append(packet)

    server = Server(db_path=":memory:")
    server._db.connect()
    record = server._db.create_user(
        "Reader",
        "hash",
        locale="en",
        approved=True,
        email="reader@example.com",
    )
    assert record is not None
    connection = Connection()
    reader = NetworkUser(
        record.username,
        "en",
        connection,
        uuid=record.uuid,
        approved=True,
    )
    server._users[reader.username] = reader
    server._user_states[reader.username] = {
        "menu": "language_menu",
        "_stack": [{"menu": "main_menu"}],
    }

    def fail_update(_username, _locale):
        raise RuntimeError("storage unavailable")

    monkeypatch.setattr(server._db, "update_user_locale", fail_update)

    await server._handle_language_selection(reader, "lang_vi")

    assert reader.locale == "en"
    assert server._db.get_user(reader.username).locale == "en"
    assert connection.sent_messages == []
    assert Localization.get("en", "server-error-changing-language") in [
        message["text"]
        for message in reader._message_queue
        if message.get("type") == "speak"
    ]
