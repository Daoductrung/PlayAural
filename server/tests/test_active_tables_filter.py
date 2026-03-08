import pytest
from server.core.server import Server
from server.users.test_user import MockUser
from server.messages.localization import Localization
from pathlib import Path

@pytest.fixture
def mock_server():
    server = Server(db_path=":memory:")
    server._db.connect()
    server._db.initialize_trust_levels()
    Localization.init(Path("locales"))
    Localization.preload_bundles()
    return server

@pytest.mark.asyncio
async def test_active_tables_filter_toggle(mock_server):
    user_a = MockUser("UserA")
    mock_server._users["UserA"] = user_a
    mock_server._user_states["UserA"] = {"menu": "active_tables_menu"}
    user_a.menus["active_tables_menu"] = {"items": []}

    assert user_a.preferences.active_tables_filter == "all"

    # Toggle to waiting
    await mock_server._handle_active_tables_selection(user_a, "toggle_filter")
    assert user_a.preferences.active_tables_filter == "waiting"

    # Toggle to playing
    await mock_server._handle_active_tables_selection(user_a, "toggle_filter")
    assert user_a.preferences.active_tables_filter == "playing"

    # Toggle to all
    await mock_server._handle_active_tables_selection(user_a, "toggle_filter")
    assert user_a.preferences.active_tables_filter == "all"


@pytest.mark.asyncio
async def test_active_tables_dynamic_filter(mock_server):
    user_a = MockUser("UserA")
    user_b = MockUser("UserB")
    mock_server._users["UserA"] = user_a
    mock_server._users["UserB"] = user_b

    # User B sets filter to "waiting" and looks at active tables
    user_b.preferences.active_tables_filter = "waiting"
    mock_server._user_states["UserB"] = {"menu": "active_tables_menu"}
    user_b.menus["active_tables_menu"] = {"items": []}

    # User A creates a waiting table
    table = mock_server._tables.create_table("holdem", "UserA", user_a)
    from server.games.registry import get_game_class
    game_class = get_game_class("holdem")
    game = game_class()
    table.game = game
    game._table = table
    game.initialize_lobby("UserA", user_a)

    # Menu should show the table
    menu_items = user_b.menus["active_tables_menu"]["items"]
    text_content = " ".join([getattr(i, 'text', str(i)).lower() for i in menu_items])
    assert "usera" in text_content, "Table should be visible in 'waiting' filter"

    # Game status changes to playing
    table._game.status = "playing"
    table._last_menu_state_hash = f"{table._game.status}_{len(table.members)}_{table.host}"
    mock_server.on_tables_changed()

    # User B's menu should dynamically update to hide the table
    menu_items = user_b.menus["active_tables_menu"]["items"]
    text_content = " ".join([getattr(i, 'text', str(i)).lower() for i in menu_items])
    assert "usera" not in text_content, "Table should dynamically vanish from 'waiting' filtered view when it starts playing"
    assert "no waiting tables available" in text_content.lower() or "không có bàn nào đang chờ" in text_content.lower(), "Empty message should appear"
