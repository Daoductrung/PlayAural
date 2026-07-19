"""Tests for metadata-driven administrator-authored translations."""

from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..messages.localized_content import (
    decode_localized_custom_text,
    encode_localized_custom_text,
    localized_custom_text_for_locale,
    localized_penalty_reason_for_locale,
    localized_text_for_locale,
    normalize_localized_text,
    normalize_localized_value,
)
from ..messages.localization import DEFAULT_LOCALE, Localization
from ..users.test_user import MockUser


def _make_server(tmp_path) -> tuple[Server, MockUser]:
    server = Server(db_path=tmp_path / "admin_localized.sqlite")
    server._db.connect()
    record = server._db.create_user("Admin", "hash", trust_level=3)
    server._db.approve_user("Admin")
    admin = MockUser("Admin", uuid=record.uuid)
    admin.trust_level = 3
    server._users[admin.username] = admin
    server._show_main_menu(admin)
    return server, admin


async def _select(
    server: Server, user: MockUser, menu_id: str, selection_id: str
) -> None:
    await server._handle_menu(
        SimpleNamespace(username=user.username),
        {
            "type": "menu",
            "menu_id": menu_id,
            "selection_id": selection_id,
        },
    )


async def _edit_translation(
    server: Server, user: MockUser, language: str, text: str
) -> None:
    await _select(
        server,
        user,
        "admin_localized_text_menu",
        f"localized_text_locale_{language}",
    )
    await server._handle_editbox(
        SimpleNamespace(username=user.username),
        {
            "type": "editbox",
            "input_id": "admin_localized_text_input",
            "text": text,
        },
    )


def _menu_ids(user: MockUser) -> list[str]:
    return [
        item.id
        for item in user.get_current_menu_items("admin_localized_text_menu") or []
    ]


def _menu_text(user: MockUser, item_id: str) -> str:
    for item in user.get_current_menu_items("admin_localized_text_menu") or []:
        if item.id == item_id:
            return item.text
    raise AssertionError(f"Missing editor item {item_id!r}")


def test_localized_content_codec_supports_fallback_legacy_and_malformed_data() -> None:
    encoded = encode_localized_custom_text({"en": "English", "vi": "Tiếng Việt"})

    assert decode_localized_custom_text(encoded) == {
        "en": "English",
        "vi": "Tiếng Việt",
    }
    assert localized_custom_text_for_locale("vi", encoded) == "Tiếng Việt"
    assert localized_custom_text_for_locale("fa", encoded) == "English"
    assert localized_custom_text_for_locale("vi", "CUSTOM_Legacy") == "Legacy"
    assert localized_custom_text_for_locale("en", "reason-spam") is None
    assert decode_localized_custom_text("CUSTOM_I18N:{broken") == {}
    assert localized_text_for_locale("fa", {DEFAULT_LOCALE: "Fallback"}) == "Fallback"
    assert normalize_localized_text({"../en": "unsafe", "en": " valid "}) == {
        "en": "valid"
    }
    assert normalize_localized_value(" one\r\n two ", multiline=True) == (
        "one\n two"
    )
    assert normalize_localized_value(" one\r\n two ", multiline=False) == "one two"
    assert localized_penalty_reason_for_locale(
        "fa", "CUSTOM_I18N:{broken"
    ) == Localization.get("fa", "admin-penalty-reason-unknown")


def test_official_locale_registry_is_metadata_driven() -> None:
    official = Localization.official_locale_codes()

    assert DEFAULT_LOCALE in official
    assert "vi" in official
    assert "fa" not in official


def test_banned_screen_resolves_structured_and_malformed_custom_reasons(
    tmp_path,
) -> None:
    server, _admin = _make_server(tmp_path)
    try:
        server._db.create_user("Target", "hash")
        reason = encode_localized_custom_text(
            {"en": "English ban reason", "vi": "Lý do cấm tiếng Việt"}
        )
        record = server._db.ban_user("Target", "Admin", reason, None)
        fa_user = MockUser("Target", locale="fa")

        server._show_banned_menu(fa_user, record)

        reason_row = next(
            item
            for item in fa_user.get_current_menu_items("banned_menu") or []
            if "English ban reason" in item.text
        )
        assert reason_row.id == ""
        assert "English ban reason" in reason_row.text

        malformed = server._db.ban_user(
            "Malformed", "Admin", "CUSTOM_I18N:{broken", None
        )
        malformed_user = MockUser("Malformed", locale="en")
        server._show_banned_menu(malformed_user, malformed)
        malformed_reason = next(
            item
            for item in malformed_user.get_current_menu_items("banned_menu") or []
            if "unspecified reason" in item.text
        )
        assert malformed_reason.id == ""
        assert "unspecified reason" in malformed_reason.text
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_motd_editor_requires_official_locales_and_skips_community(
    tmp_path,
) -> None:
    server, admin = _make_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "manage_motd")
        await _select(server, admin, "manage_motd_menu", "create_update")

        ids = _menu_ids(admin)
        assert ids.index("localized_text_locale_en") < ids.index(
            "localized_text_locale_vi"
        )
        assert "required" in _menu_text(admin, "localized_text_locale_en")
        assert "required" in _menu_text(admin, "localized_text_locale_vi")
        assert "optional" in _menu_text(admin, "localized_text_locale_fa")

        await _edit_translation(server, admin, "en", "English MOTD")
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_submit",
        )

        assert server._db.get_highest_motd_version() == 0
        assert server._user_states[admin.username]["menu"] == (
            "admin_localized_text_menu"
        )
        assert admin.menus["admin_localized_text_menu"]["selection_id"] == (
            "localized_text_locale_vi"
        )

        await _edit_translation(server, admin, "vi", "MOTD tiếng Việt")
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_submit",
        )

        assert server._db.get_motd(1, "en") == "English MOTD"
        assert server._db.get_motd(1, "vi") == "MOTD tiếng Việt"
        assert server._db.get_motd(1, "fa") == "English MOTD"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_editor_rejects_overlength_text_without_losing_parent_state(
    tmp_path,
) -> None:
    server, admin = _make_server(tmp_path)
    try:
        server.admin_manager._show_admin_localized_text_menu(
            admin,
            "ban",
            {},
            {"target_username": "Target", "duration": "1h"},
        )
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_locale_en",
        )
        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_localized_text_input",
                "text": "x" * 201,
            },
        )

        state = server._user_states[admin.username]
        assert state["menu"] == "admin_localized_text_menu"
        assert state["localized_text_translations"] == {}
        assert "maximum is 200" in (admin.get_last_spoken() or "")

        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_locale_en",
        )
        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "stale_admin_input",
                "text": "must not be accepted",
            },
        )
        state = server._user_states[admin.username]
        assert state["menu"] == "admin_localized_text_menu"
        assert state["localized_text_translations"] == {}
    finally:
        server._db.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("purpose", "starting_trust", "reduced_trust", "expected_menu", "message"),
    [
        ("power", 3, 2, "admin_menu", "restricted to Developers"),
        ("motd", 2, 1, "main_menu", "no longer an admin"),
    ],
)
async def test_editor_revalidates_access_after_role_changes(
    tmp_path,
    purpose: str,
    starting_trust: int,
    reduced_trust: int,
    expected_menu: str,
    message: str,
) -> None:
    server, admin = _make_server(tmp_path)
    try:
        admin.trust_level = starting_trust
        context = (
            {"power_action": "reboot", "power_delay_seconds": 30}
            if purpose == "power"
            else {"version": 1}
        )
        server.admin_manager._show_admin_localized_text_menu(
            admin, purpose, {}, context
        )
        admin.trust_level = reduced_trust

        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_locale_en",
        )

        assert server._user_states[admin.username]["menu"] == expected_menu
        assert message in (admin.get_last_spoken() or "")
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_power_editor_revalidates_developer_access_on_input_submit(
    tmp_path,
) -> None:
    server, admin = _make_server(tmp_path)
    try:
        server.admin_manager._show_admin_localized_text_menu(
            admin,
            "power",
            {},
            {"power_action": "reboot", "power_delay_seconds": 30},
        )
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_locale_en",
        )
        admin.trust_level = 2

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_localized_text_input",
                "text": "Must not be accepted",
            },
        )

        assert server._user_states[admin.username]["menu"] == "admin_menu"
        assert server.power_manager.active_operation is None
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_power_reason_editor_preserves_draft_and_falls_back_to_english(
    tmp_path,
) -> None:
    server, admin = _make_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "server_power")
        await _select(server, admin, "server_power_menu", "reboot")
        await _select(server, admin, "server_power_delay_menu", "delay_30")
        await _select(server, admin, "server_power_reason_menu", "reason_custom")
        await _edit_translation(server, admin, "en", "English reason")
        await _edit_translation(server, admin, "vi", "Lý do tiếng Việt")
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_submit",
        )

        state = server._user_states[admin.username]
        assert state["menu"] == "server_power_confirm_menu"
        reasons = state["power_custom_reasons"]
        assert "fa" not in reasons
        assert server.power_manager._custom_reason_for_locale("fa", reasons) == (
            "English reason"
        )

        await _select(server, admin, "server_power_confirm_menu", "back")
        restored = server._user_states[admin.username]
        assert restored["menu"] == "admin_localized_text_menu"
        assert restored["localized_text_translations"] == {
            "en": "English reason",
            "vi": "Lý do tiếng Việt",
        }
    finally:
        server._db.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("purpose", ["ban", "mute"])
async def test_penalty_editor_persists_and_broadcasts_localized_reasons(
    tmp_path, purpose: str
) -> None:
    server, admin = _make_server(tmp_path)
    target_name = f"{purpose.title()}Target"
    try:
        server._db.create_user(target_name, "hash")
        vi_recipient = MockUser("ViAdmin", locale="vi")
        vi_recipient.trust_level = 2
        fa_recipient = MockUser("FaAdmin", locale="fa")
        fa_recipient.trust_level = 2
        server._users[vi_recipient.username] = vi_recipient
        server._users[fa_recipient.username] = fa_recipient

        server.admin_manager._show_admin_localized_text_menu(
            admin,
            purpose,
            {},
            {"target_username": target_name, "duration": "1h"},
        )
        await _edit_translation(server, admin, "en", f"English {purpose} reason")
        await _edit_translation(server, admin, "vi", f"Lý do {purpose} tiếng Việt")
        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_submit",
        )

        record = (
            server._db.get_active_ban(target_name)
            if purpose == "ban"
            else server._db.get_active_mute(target_name)
        )
        assert record is not None
        stored_reason = record.reason_key if purpose == "ban" else record.reason
        assert decode_localized_custom_text(stored_reason) == {
            "en": f"English {purpose} reason",
            "vi": f"Lý do {purpose} tiếng Việt",
        }
        assert f"Lý do {purpose} tiếng Việt" in (
            vi_recipient.get_last_spoken() or ""
        )
        assert f"English {purpose} reason" in (
            fa_recipient.get_last_spoken() or ""
        )
    finally:
        server._db.close()
