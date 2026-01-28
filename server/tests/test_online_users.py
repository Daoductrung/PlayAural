from pathlib import Path

import pytest

from server.core.server import Server
from server.tables.manager import TableManager
from server.users.test_user import MockUser
from server.messages.localization import Localization

# Ensure games are registered for name lookups.
import server.games  # noqa: F401


class DummyClient:
    def __init__(self, username: str):
        self.username = username


def _make_server() -> Server:
    Localization.init(Path(__file__).resolve().parents[1] / "locales")
    server = Server.__new__(Server)
    server._tables = TableManager()
    server._user_states = {}
    server._users = {}
    return server


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.menus.get(menu_id, {}).get("items", [])
    texts: list[str] = []
    for item in items:
        texts.append(item.text if hasattr(item, "text") else item)
    return texts


@pytest.mark.asyncio
async def test_list_online_users_speaks_sorted_list() -> None:
    server = _make_server()
    alice = MockUser("Alice")
    bob = MockUser("Bob")
    server._users = {"Bob": bob, "Alice": alice}

    client = DummyClient("Alice")
    await server._handle_list_online(client)

    assert alice.messages[-1].data["text"] == "2 users: Alice and Bob"


def test_online_users_menu_formats_game_names() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    bob = MockUser("Bob")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Bob": bob, "Alice": alice}

    server._tables.create_table("crazyeights", "Bob", bob)

    server._show_online_users_menu(viewer)

    texts = _menu_texts(viewer, "online_users")
    assert "Bob: Crazy Eights" in texts
    assert "Alice: Not in game" in texts
