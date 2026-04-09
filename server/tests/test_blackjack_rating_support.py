from types import SimpleNamespace

from server.core.server import Server
from server.game_utils.game_result import GameResult, PlayerResult
from server.games.blackjack.game import BlackjackGame
from server.games.pig.game import PigGame
from server.users.test_user import MockUser


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.id for item in items if hasattr(item, "id")]


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.text for item in items if hasattr(item, "text")]


def _make_server(tmp_path) -> Server:
    server = Server(db_path=tmp_path / "test_stats.sqlite")
    server._db.connect()
    return server


def test_blackjack_leaderboards_exclude_rating_and_prediction_is_disabled() -> None:
    game = BlackjackGame()
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    host_player = game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)

    game.status = "playing"
    game.setup_keybinds()
    game.setup_player_actions(host_player)

    enabled_ids = [action.action.id for action in game.get_all_enabled_actions(host_player)]

    assert game.get_supported_leaderboards() == ["games_played"]
    assert game._is_predict_outcomes_enabled(host_player) == "action-not-available"
    assert "predict_outcomes" not in enabled_ids


def test_blackjack_does_not_update_ratings_when_finished(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        game = BlackjackGame()
        host_player = game.add_player("Host", MockUser("Host", uuid="blackjack-host"))
        guest_player = game.add_player("Guest", MockUser("Guest", uuid="blackjack-guest"))
        game._table = SimpleNamespace(_db=server._db)

        result = GameResult(
            game_type="blackjack",
            timestamp="2026-03-26T00:00:00",
            duration_ticks=0,
            player_results=[
                PlayerResult(host_player.id, host_player.name, False),
                PlayerResult(guest_player.id, guest_player.name, False),
            ],
            custom_data={"winner_name": host_player.name},
        )

        game._update_ratings(result)

        assert server._db.get_player_rating(host_player.id, "blackjack") is None
        assert server._db.get_player_rating(guest_player.id, "blackjack") is None
    finally:
        server._db.close()


def test_rated_games_still_update_ratings(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        game = PigGame()
        game._table = SimpleNamespace(_db=server._db)

        result = GameResult(
            game_type="pig",
            timestamp="2026-03-26T00:00:00",
            duration_ticks=0,
            player_results=[
                PlayerResult("pig-winner", "Alice", False),
                PlayerResult("pig-loser", "Bob", False),
            ],
            custom_data={"winner_ids": ["pig-winner"], "winner_name": "Alice"},
        )

        game._update_ratings(result)

        assert server._db.get_player_rating("pig-winner", "pig") is not None
        assert server._db.get_player_rating("pig-loser", "pig") is not None
    finally:
        server._db.close()


def test_blackjack_ui_hides_rating_everywhere_but_rated_games_still_show_it(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        user = MockUser("StatsUser", uuid="stats-user")

        cursor = server._db._conn.cursor()
        cursor.execute(
            """
            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
            VALUES (?, 'blackjack', 'games_played', 12)
            """,
            (user.uuid,),
        )
        cursor.execute(
            """
            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
            VALUES (?, 'pig', 'games_played', 7)
            """,
            (user.uuid,),
        )
        server._db.set_player_rating(user.uuid, "blackjack", 31.0, 6.0)
        server._db.set_player_rating(user.uuid, "pig", 32.0, 5.5)
        server._db._conn.commit()

        server._show_leaderboard_types_menu(user, "blackjack")
        assert "type_rating" not in _menu_ids(user, "leaderboard_types_menu")

        server._show_leaderboard_types_menu(user, "pig")
        assert "type_rating" in _menu_ids(user, "leaderboard_types_menu")

        server._show_my_game_stats(user, "blackjack")
        blackjack_ids = _menu_ids(user, "my_game_stats")
        assert "rating" not in blackjack_ids
        assert "no_rating" not in blackjack_ids

        server._show_my_game_stats(user, "pig")
        assert "rating" in _menu_ids(user, "my_game_stats")
    finally:
        server._db.close()


def test_predict_outcomes_shows_probability_only_in_two_player_matches(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        game = PigGame()
        host_user = MockUser("Host", uuid="predict-host")
        guest_user = MockUser("Guest", uuid="predict-guest")
        host_player = game.add_player("Host", host_user)
        game.add_player("Guest", guest_user)
        game._table = SimpleNamespace(_db=server._db)
        game.status = "playing"

        game._action_predict_outcomes(host_player, "predict_outcomes")

        lines = _menu_texts(host_user, "status_box")
        assert any("%" in line for line in lines)
        assert not any("2-player matches" in line for line in lines)
    finally:
        server._db.close()


def test_predict_outcomes_explains_multiplayer_rating_only_mode(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        game = PigGame()
        host_user = MockUser("Host", uuid="predict-host")
        guest_user = MockUser("Guest", uuid="predict-guest")
        third_user = MockUser("Third", uuid="predict-third")
        host_player = game.add_player("Host", host_user)
        game.add_player("Guest", guest_user)
        game.add_player("Third", third_user)
        game._table = SimpleNamespace(_db=server._db)
        game.status = "playing"

        game._action_predict_outcomes(host_player, "predict_outcomes")

        lines = _menu_texts(host_user, "status_box")
        assert any("3 or more human players" in line for line in lines)
        assert not any("% win chance" in line for line in lines)
    finally:
        server._db.close()
