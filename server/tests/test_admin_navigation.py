"""Admin menu navigation and focus restoration tests."""

from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..users.test_user import MockUser


def _current_menu(server: Server, username: str) -> str:
    return server._user_states.get(username, {}).get("menu", "")


def _make_admin_server(tmp_path):
    server = Server(db_path=tmp_path / "admin_nav.sqlite")
    server._db.connect()
    record = server._db.create_user("Admin", "hash", trust_level=3)
    server._db.approve_user("Admin")
    admin = MockUser("Admin", uuid=record.uuid)
    admin.trust_level = 3
    server._users[admin.username] = admin
    server._show_main_menu(admin)
    return server, admin


def _create_approved_user(server: Server, username: str, trust_level: int = 1):
    record = server._db.create_user(username, "hash", trust_level=trust_level)
    server._db.approve_user(username)
    return record


async def _select(server: Server, user: MockUser, menu_id: str, selection_id: str) -> None:
    await server._handle_menu(
        SimpleNamespace(username=user.username),
        {
            "type": "menu",
            "menu_id": menu_id,
            "selection_id": selection_id,
        },
    )


def _menu_item_ids(user: MockUser, menu_id: str) -> list[str]:
    return [item.id for item in user.get_current_menu_items(menu_id) or []]


@pytest.mark.asyncio
async def test_global_admin_shortcut_is_server_permission_checked(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        user_record = _create_approved_user(server, "Player")
        player = MockUser("Player", uuid=user_record.uuid)
        player.trust_level = 1
        server._users[player.username] = player
        server._show_main_menu(player)

        await server._handle_open_admin_menu(SimpleNamespace(username=player.username))
        assert _current_menu(server, player.username) == "main_menu"

        await server._handle_open_admin_menu(SimpleNamespace(username=admin.username))
        assert _current_menu(server, admin.username) == "admin_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_editbox_input_is_permission_checked(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        user_record = _create_approved_user(server, "Player")
        player = MockUser("Player", uuid=user_record.uuid)
        player.trust_level = 1
        server._users[player.username] = player
        server._user_states[player.username] = {
            "menu": "admin_target_search_input",
            "target_mode": "ban",
        }

        await server._handle_editbox(
            SimpleNamespace(username=player.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Admin",
            },
        )

        assert _current_menu(server, player.username) == "main_menu"
        assert player.get_last_spoken() == (
            "You are no longer an admin and cannot perform this action."
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_account_approval_menu_pages_pending_accounts(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(101):
            server._db.create_user(f"Pending{index:03d}", "hash")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "account_approval")

        ids = _menu_item_ids(admin, "account_approval_menu")
        assert len([item_id for item_id in ids if item_id.startswith("pending_")]) == 100
        assert "pending_Pending100" not in ids
        assert "refresh" in ids
        assert "page_next" in ids

        await _select(server, admin, "account_approval_menu", "page_next")
        assert server._user_states[admin.username]["account_approval_page"] == 2
        last_page_ids = _menu_item_ids(admin, "account_approval_menu")
        assert "pending_Pending100" in last_page_ids
        assert "page_previous" in last_page_ids
        assert "page_next" not in last_page_ids
        assert admin.menus["account_approval_menu"]["position"] == 1

        await _select(server, admin, "account_approval_menu", "pending_Pending100")
        assert _current_menu(server, admin.username) == "pending_user_actions_menu"

        await _select(server, admin, "pending_user_actions_menu", "back")
        assert _current_menu(server, admin.username) == "account_approval_menu"
        assert server._user_states[admin.username]["account_approval_page"] == 2
        assert admin.menus["account_approval_menu"]["selection_id"] == "pending_Pending100"
    finally:
        server._db.close()


def test_admin_empty_paginated_menus_do_not_show_manual_refresh(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        server.admin_manager._show_account_approval_menu(admin)
        approval_ids = _menu_item_ids(admin, "account_approval_menu")
        assert "refresh" not in approval_ids

        server.admin_manager._show_ban_menu(admin)
        ban_ids = _menu_item_ids(admin, "ban_menu")
        assert "refresh" not in ban_ids
    finally:
        server._db.close()


def test_account_approval_list_auto_refreshes_when_pending_queue_changes(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        server.admin_manager._show_account_approval_menu(admin)
        assert "pending_NewPlayer" not in _menu_item_ids(admin, "account_approval_menu")

        server._db.create_user("NewPlayer", "hash")
        server.admin_manager.refresh_account_approval_menus()

        ids = _menu_item_ids(admin, "account_approval_menu")
        assert "pending_NewPlayer" in ids
        assert "refresh" in ids
        assert admin.menus["account_approval_menu"]["position"] is None
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_searchable_ban_menu_limits_and_filters_results(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(100):
            _create_approved_user(server, f"User{index:03d}")
        _create_approved_user(server, "ZzzNeedleTarget")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "ban_user")
        assert _current_menu(server, admin.username) == "ban_menu"

        ids = _menu_item_ids(admin, "ban_menu")
        assert ids[0] == "search"
        assert len([item_id for item_id in ids if item_id.startswith("ban_")]) == 100
        assert "ban_ZzzNeedleTarget" not in ids
        assert "refresh" in ids
        assert "page_next" in ids
        assert "page_last" in ids

        await _select(server, admin, "ban_menu", "page_next")
        assert server._user_states[admin.username]["target_page"] == 2
        last_page_ids = _menu_item_ids(admin, "ban_menu")
        assert "ban_ZzzNeedleTarget" in last_page_ids
        assert "page_previous" in last_page_ids
        assert "page_next" not in last_page_ids
        assert admin.menus["ban_menu"]["position"] == 3

        await _select(server, admin, "ban_menu", "ban_ZzzNeedleTarget")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_ZzzNeedleTarget"
        assert server._user_states[admin.username]["target_page"] == 2

        await _select(server, admin, "ban_menu", "search")
        assert _current_menu(server, admin.username) == "admin_target_search_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Needle",
            },
        )

        assert _current_menu(server, admin.username) == "ban_menu"
        filtered_ids = _menu_item_ids(admin, "ban_menu")
        assert "ban_ZzzNeedleTarget" in filtered_ids
        assert server._user_states[admin.username]["search_query"] == "Needle"
        assert server._user_states[admin.username]["target_page"] == 1

        await _select(server, admin, "ban_menu", "ban_ZzzNeedleTarget")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_ZzzNeedleTarget"
        assert server._user_states[admin.username]["search_query"] == "Needle"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_searchable_unban_menu_uses_active_ban_search(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(100):
            username = f"Banned{index:03d}"
            _create_approved_user(server, username)
            server._db.ban_user(username, admin.username, "reason-spam", None)
        _create_approved_user(server, "SpecialBan")
        server._db.ban_user("SpecialBan", admin.username, "reason-spam", None)

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "unban_user")
        ids = _menu_item_ids(admin, "unban_menu")
        assert ids[0] == "search"
        assert len([item_id for item_id in ids if item_id.startswith("unban_")]) == 100
        assert "unban_SpecialBan" not in ids
        assert "refresh" in ids
        assert "page_next" in ids

        await _select(server, admin, "unban_menu", "page_next")
        assert server._user_states[admin.username]["target_page"] == 2
        assert "unban_SpecialBan" in _menu_item_ids(admin, "unban_menu")

        await _select(server, admin, "unban_menu", "search")
        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Special",
            },
        )

        filtered_ids = _menu_item_ids(admin, "unban_menu")
        assert "unban_SpecialBan" in filtered_ids
        assert not any(item_id == "unban_Banned00" for item_id in filtered_ids)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_submenu_back_restores_admin_focus_and_outer_stack(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        assert _current_menu(server, admin.username) == "admin_menu"

        await _select(server, admin, "admin_menu", "kick_user")
        assert _current_menu(server, admin.username) == "kick_menu"

        await _select(server, admin, "kick_menu", "back")
        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "kick_user"

        await _select(server, admin, "admin_menu", "back")
        assert _current_menu(server, admin.username) == "main_menu"
        assert admin.menus["main_menu"]["selection_id"] == "administration"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_nested_dynamic_back_restores_target_and_root_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "ban_user")
        assert _current_menu(server, admin.username) == "ban_menu"

        await _select(server, admin, "ban_menu", "ban_Target")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_Target"

        await _select(server, admin, "ban_menu", "back")
        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "ban_user"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_confirmation_cancel_restores_list_target_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "promote_admin")
        await _select(server, admin, "promote_admin_menu", "promote_Target")
        assert _current_menu(server, admin.username) == "promote_confirm_menu"

        await _select(server, admin, "promote_confirm_menu", "no")
        assert _current_menu(server, admin.username) == "promote_admin_menu"
        assert admin.menus["promote_admin_menu"]["selection_id"] == "promote_Target"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_broadcast_scope_back_restores_confirmation_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "promote_admin")
        await _select(server, admin, "promote_admin_menu", "promote_Target")
        await _select(server, admin, "promote_confirm_menu", "yes")
        assert _current_menu(server, admin.username) == "broadcast_choice_menu"

        await _select(server, admin, "broadcast_choice_menu", "back")
        assert _current_menu(server, admin.username) == "promote_confirm_menu"
        assert admin.menus["promote_confirm_menu"]["selection_id"] == "yes"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_editbox_cancel_restores_admin_focus_and_back_path(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "broadcast_announcement")
        assert _current_menu(server, admin.username) == "admin_broadcast_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "broadcast_message",
                "text": "",
            },
        )

        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "broadcast_announcement"

        await _select(server, admin, "admin_menu", "back")
        assert _current_menu(server, admin.username) == "main_menu"
        assert admin.menus["main_menu"]["selection_id"] == "administration"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_sequential_editbox_cancel_restores_stable_parent(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "manage_motd")
        await _select(server, admin, "manage_motd_menu", "create_update")
        assert _current_menu(server, admin.username) == "admin_motd_version_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "motd_version",
                "text": "1",
            },
        )
        assert _current_menu(server, admin.username) == "admin_motd_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "motd_message_en",
                "cancelled": True,
            },
        )

        assert _current_menu(server, admin.username) == "manage_motd_menu"
        assert admin.menus["manage_motd_menu"]["selection_id"] == "create_update"
    finally:
        server._db.close()
