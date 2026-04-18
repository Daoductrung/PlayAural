from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..users.test_user import MockUser


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.text for item in items if hasattr(item, "text")]


def _make_server_with_games_played_leaderboard(tmp_path):
    server = Server(db_path=tmp_path / "leaderboard_nav.sqlite")
    server._db.connect()

    viewer_record = server._db.create_user("Viewer", "hash", trust_level=1)
    ranked_record = server._db.create_user("RankedPlayer", "hash", trust_level=1)
    server._db._conn.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, 'pig', 'games_played', 11)
        """,
        (ranked_record.uuid,),
    )
    server._db._conn.commit()

    viewer = MockUser("Viewer", uuid=viewer_record.uuid)
    server._users[viewer.username] = viewer

    server._show_main_menu(viewer)
    server._nav_push(viewer, server._show_leaderboards_menu)
    server._nav_push(viewer, server._show_leaderboard_types_menu, "pig")
    server._nav_push(viewer, server._show_games_played_leaderboard, "pig", "Pig")
    return server, viewer


@pytest.mark.asyncio
async def test_options_shortcut_restores_exact_leaderboard_and_back_path(tmp_path) -> None:
    server, viewer = _make_server_with_games_played_leaderboard(tmp_path)
    try:
        initial_texts = _menu_texts(viewer, "game_leaderboard")
        assert any("RankedPlayer" in text and "11" in text for text in initial_texts)

        await server._handle_open_options(SimpleNamespace(username=viewer.username))
        assert server._user_states[viewer.username]["menu"] == "options_menu"

        await server._handle_options_selection(viewer, "back")

        restored_state = server._user_states[viewer.username]
        assert restored_state["menu"] == "game_leaderboard"
        assert restored_state["leaderboard_selection_id"] == "type_games_played"
        assert _menu_texts(viewer, "game_leaderboard") == initial_texts

        await server._handle_game_leaderboard_selection(viewer, "back", restored_state)
        assert server._user_states[viewer.username]["menu"] == "leaderboard_types_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_friends_shortcut_restores_exact_leaderboard_and_back_path(tmp_path) -> None:
    server, viewer = _make_server_with_games_played_leaderboard(tmp_path)
    try:
        initial_texts = _menu_texts(viewer, "game_leaderboard")
        assert any("RankedPlayer" in text and "11" in text for text in initial_texts)

        await server._handle_open_friends_hub(SimpleNamespace(username=viewer.username))
        assert server._user_states[viewer.username]["menu"] == "friends_hub_menu"

        await server._handle_friends_hub_selection(viewer, "back")

        restored_state = server._user_states[viewer.username]
        assert restored_state["menu"] == "game_leaderboard"
        assert restored_state["leaderboard_selection_id"] == "type_games_played"
        assert _menu_texts(viewer, "game_leaderboard") == initial_texts

        await server._handle_game_leaderboard_selection(viewer, "back", restored_state)
        assert server._user_states[viewer.username]["menu"] == "leaderboard_types_menu"
    finally:
        server._db.close()
