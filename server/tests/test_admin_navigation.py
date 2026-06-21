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
    admin = MockUser("Admin", uuid=record.uuid)
    admin.trust_level = 3
    server._users[admin.username] = admin
    server._show_main_menu(admin)
    return server, admin


def _create_approved_user(server: Server, username: str, trust_level: int = 1) -> None:
    server._db.create_user(username, "hash", trust_level=trust_level)
    server._db.approve_user(username)


async def _select(server: Server, user: MockUser, menu_id: str, selection_id: str) -> None:
    await server._handle_menu(
        SimpleNamespace(username=user.username),
        {
            "type": "menu",
            "menu_id": menu_id,
            "selection_id": selection_id,
        },
    )


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
