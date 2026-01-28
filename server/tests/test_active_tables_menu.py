from pathlib import Path

from server.core.server import Server
from server.tables.manager import TableManager
from server.users.test_user import MockUser
from server.messages.localization import Localization

# Ensure games are registered for name lookups.
import server.games  # noqa: F401


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    texts: list[str] = []
    for item in items:
        texts.append(item.text if hasattr(item, "text") else item)
    return texts


def _make_server() -> Server:
    Localization.init(Path(__file__).resolve().parents[1] / "locales")
    server = Server.__new__(Server)
    server._tables = TableManager()
    server._user_states = {}
    return server


def test_active_tables_menu_lists_members_without_host() -> None:
    server = _make_server()
    host = MockUser("Bob")
    table = server._tables.create_table("pig", "Bob", host)
    table.add_member("Sue", MockUser("Sue"), as_spectator=False)
    table.add_member("Jim", MockUser("Jim"), as_spectator=True)

    viewer = MockUser("Alice")
    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Pig: Bob's table (3 users) with Sue and Jim"
    assert expected in texts


def test_active_tables_menu_singular_player_format() -> None:
    server = _make_server()
    host = MockUser("Kate")
    server._tables.create_table("farkle", "Kate", host)

    viewer = MockUser("Alice")
    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Farkle: Kate's table (1 user)"
    assert expected in texts


def test_main_menu_includes_active_tables_option() -> None:
    server = _make_server()
    viewer = MockUser("Alice")
    server._show_main_menu(viewer)

    texts = _menu_texts(viewer, "main_menu")
    expected = Localization.get(viewer.locale, "view-active-tables")
    assert expected in texts
