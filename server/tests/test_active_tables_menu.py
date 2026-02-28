from pathlib import Path

from ..core.server import Server
from ..tables.manager import TableManager
from ..users.test_user import MockUser
from ..messages.localization import Localization

# Ensure games are registered for name lookups.
from .. import games  # noqa: F401


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
    server._users = {}
    return server


def test_active_tables_menu_lists_members_without_host() -> None:
    server = _make_server()
    host = MockUser("Bob")
    sue = MockUser("Sue")
    jim = MockUser("Jim")
    viewer = MockUser("Alice")
    server._users = {"Bob": host, "Sue": sue, "Jim": jim, "Alice": viewer}
    table = server._tables.create_table("pig", "Bob", host)
    table.add_member("Sue", sue, as_spectator=False)
    table.add_member("Jim", jim, as_spectator=True)

    from ..games.pig.game import PigGame
    table.game = PigGame()

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Pig [Waiting]: Bob's table (3 users) with Sue and Jim"
    assert expected in texts


def test_active_tables_menu_singular_player_format() -> None:
    server = _make_server()
    host = MockUser("Kate")
    viewer = MockUser("Alice")
    server._users = {"Kate": host, "Alice": viewer}
    table = server._tables.create_table("farkle", "Kate", host)

    from ..games.farkle.game import FarkleGame
    table.game = FarkleGame()

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Farkle [Waiting]: Kate's table (1 user)"
    assert expected in texts


def test_main_menu_includes_active_tables_option() -> None:
    server = _make_server()
    viewer = MockUser("Alice")
    server._show_main_menu(viewer)

    texts = _menu_texts(viewer, "main_menu")
    expected = Localization.get(viewer.locale, "view-active-tables")
    assert expected in texts

