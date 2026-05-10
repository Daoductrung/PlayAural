from pathlib import Path

import pytest

from server.core.server import Server
from server.messages.localization import Localization
from server.users.preferences import UserPreferences
from server.users.test_user import MockUser


@pytest.fixture
def mock_server():
    server = Server(
        db_path=":memory:",
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    server._db.connect()
    server._db.initialize_trust_levels()
    Localization.init(Path(__file__).resolve().parents[1] / "locales")
    Localization.preload_bundles()
    try:
        yield server
    finally:
        server._db.close()


def test_game_category_filter_preference_defaults_and_round_trips() -> None:
    prefs = UserPreferences()
    data = prefs.to_dict()

    assert prefs.game_category_filter == "all"
    assert data["game_category_filter"] == "all"
    assert UserPreferences.from_dict({}).game_category_filter == "all"
    assert (
        UserPreferences.from_dict({"game_category_filter": "poker"}).game_category_filter
        == "poker"
    )


@pytest.mark.asyncio
async def test_game_category_filter_toggle_and_selection(mock_server) -> None:
    from server import games as registered_games
    from server.games.registry import GameRegistry

    assert registered_games.GameRegistry is GameRegistry

    user = MockUser("UserA")
    mock_server._users[user.username] = user
    mock_server._show_games_list_menu(user)

    assert user.preferences.game_category_filter == "all"

    await mock_server._handle_games_selection(user, "toggle_category_filter", {})
    assert mock_server._user_states[user.username]["menu"] == "game_category_filter_menu"

    await mock_server._handle_game_category_filter_selection(user, "category_poker")

    assert user.preferences.game_category_filter == "poker"
    assert mock_server._user_states[user.username]["menu"] == "games_menu"

    menu_items = user.get_current_menu_items("games_menu") or []
    item_ids = [item.id for item in menu_items if hasattr(item, "id")]
    item_text = " ".join(item.text for item in menu_items if hasattr(item, "text"))

    assert item_ids[0] == "toggle_category_filter"
    assert "game_holdem" in item_ids
    assert "game_pig" not in item_ids
    assert "Category: Poker Games" in item_text


@pytest.mark.asyncio
async def test_game_category_filter_back_does_not_change_selection(mock_server) -> None:
    user = MockUser("UserA")
    mock_server._users[user.username] = user
    user.preferences.game_category_filter = "dice"
    mock_server._show_games_list_menu(user)

    await mock_server._handle_games_selection(user, "toggle_category_filter", {})
    await mock_server._handle_game_category_filter_selection(user, "back")

    assert user.preferences.game_category_filter == "dice"
    assert mock_server._user_states[user.username]["menu"] == "games_menu"
