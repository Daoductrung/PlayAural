from types import SimpleNamespace

from server.core.server import Server
from server.game_utils.game_result import GameResult, PlayerResult
from server.game_utils.stats_extractor import StatsExtractor
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


def test_blackjack_leaderboards_exclude_rating_and_prediction_action() -> None:
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
    assert "predict_outcomes" not in enabled_ids
    assert "ctrl+r" not in game._keybinds


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

        assert game._calculate_rating_updates(result) == {}

        assert server._db.get_player_rating(host_player.id, "blackjack") is None
        assert server._db.get_player_rating(guest_player.id, "blackjack") is None
    finally:
        server._db.close()


def test_blackjack_results_only_extract_games_played() -> None:
    game = BlackjackGame()
    host = game.add_player("Host", MockUser("Host", uuid="blackjack-host"))
    guest = game.add_player("Guest", MockUser("Guest", uuid="blackjack-guest"))
    host.chips = 200
    guest.chips = 50

    result = game.build_game_result()

    assert result.custom_data == {"final_chips": {"Host": 200, "Guest": 50}}
    assert StatsExtractor.extract_incremental_stats(result) == {
        "blackjack-host": {"games_played": 1.0},
        "blackjack-guest": {"games_played": 1.0},
    }


def test_blackjack_saved_results_only_store_games_played_stats(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        host = server._db.create_user("Host", "hash", trust_level=1)
        guest = server._db.create_user("Guest", "hash", trust_level=1)

        server._db.save_game_result(
            "blackjack",
            "2026-03-26T00:00:00",
            0,
            [(host.uuid, "Host", False), (guest.uuid, "Guest", False)],
            {"final_chips": {"Host": 200, "Guest": 50}},
        )

        host_stats = server._db.get_all_player_game_stats(host.uuid, "blackjack")
        guest_stats = server._db.get_all_player_game_stats(guest.uuid, "blackjack")

        assert host_stats == {"games_played": 1.0}
        assert guest_stats == {"games_played": 1.0}

        row = server._db._conn.execute(
            "SELECT custom_data FROM game_results WHERE game_type = 'blackjack'"
        ).fetchone()
        assert row is not None
        assert row["custom_data"] == '{"final_chips": {"Host": 200, "Guest": 50}}'
    finally:
        server._db.close()


def test_rated_game_settlement_is_calculated_then_persisted_with_result(tmp_path) -> None:
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

        updates = game._calculate_rating_updates(result)

        assert updates.keys() == {"pig-winner", "pig-loser"}
        assert server._db.get_player_rating("pig-winner", "pig") is None
        server._db.save_game_result(
            "pig",
            result.timestamp,
            result.duration_ticks,
            [
                (player.player_id, player.player_name, player.is_bot)
                for player in result.player_results
            ],
            result.custom_data,
            rating_updates=updates,
        )

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


def test_result_persistence_failure_does_not_strand_game_lifecycle(caplog) -> None:
    game = PigGame()

    class FailingTable:
        _db = None

        @staticmethod
        def save_game_result(result, *, rating_updates=None) -> None:
            raise RuntimeError("storage unavailable")

    game._table = FailingTable()
    result = GameResult(
        game_type="pig",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=0,
        player_results=[PlayerResult("human-id", "Human", False)],
        custom_data={"winner_ids": []},
    )

    game._persist_result(result)

    assert "Failed to persist completed pig game result" in caplog.text


def test_rating_ui_exposes_skill_score_without_model_parameters(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        account = server._db.create_user("RatedUser", "hash", trust_level=1)
        viewer = MockUser("RatedUser", uuid=account.uuid)
        server._db.set_player_rating(account.uuid, "pig", 32.0, 5.5)
        server._db._conn.execute(
            """
            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
            VALUES (?, 'pig', 'games_played', 1)
            """,
            (account.uuid,),
        )
        server._db._conn.commit()

        server._show_rating_leaderboard(viewer, "pig", "Pig")
        leaderboard_text = " ".join(_menu_texts(viewer, "game_leaderboard"))
        assert "RatedUser: 16 rating" in leaderboard_text
        assert "32.0" not in leaderboard_text
        assert "5.5" not in leaderboard_text

        server._show_my_game_stats(viewer, "pig")
        personal_text = " ".join(_menu_texts(viewer, "my_game_stats"))
        assert "Skill rating: 16" in personal_text
        assert "32.0" not in personal_text
        assert "5.5" not in personal_text
    finally:
        server._db.close()


def test_personal_stats_display_stored_zero_and_negative_scores(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        viewer = MockUser("ScoreUser", uuid="score-user")
        server._db._conn.executemany(
            """
            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
            VALUES (?, 'pig', ?, ?)
            """,
            [
                (viewer.uuid, "games_played", 1),
                (viewer.uuid, "total_score", -4),
                (viewer.uuid, "high_score", 0),
            ],
        )
        server._db._conn.commit()

        server._show_my_game_stats(viewer, "pig")

        stats_text = " ".join(_menu_texts(viewer, "my_game_stats"))
        assert "Total score: -4" in stats_text
        assert "High score: 0" in stats_text
    finally:
        server._db.close()


def test_battle_custom_leaderboards_and_personal_stats_display_from_saved_results(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        user = server._db.create_user("StatsUser", "hash", trust_level=1)
        rival = server._db.create_user("Rival", "hash", trust_level=1)
        viewer = MockUser("StatsUser", uuid=user.uuid)

        server._db.save_game_result(
            "battle",
            "2026-03-26T00:00:00",
            0,
            [(user.uuid, "StatsUser", False), (rival.uuid, "Rival", False)],
            {
                "player_stats": {
                    user.uuid: {"survival_kills": 9, "deepest_wave": 4},
                    rival.uuid: {"survival_kills": 6, "deepest_wave": 2},
                }
            },
        )

        server._show_custom_leaderboard(
            viewer,
            "battle",
            "Battle",
            {"id": "most_enemies_defeated", "aggregate": "max", "format": "score"},
        )
        leaderboard_texts = _menu_texts(viewer, "game_leaderboard")
        assert any("StatsUser" in text and "9" in text for text in leaderboard_texts)

        server._show_my_game_stats(viewer, "battle")
        stats_texts = _menu_texts(viewer, "my_game_stats")
        assert any("Games played: 1" in text for text in stats_texts)
        assert any("Most Enemies Defeated: 9" in text for text in stats_texts)
        assert any("Deepest Wave Reached: 4" in text for text in stats_texts)
    finally:
        server._db.close()


def test_battle_custom_leaderboard_orders_higher_kills_first(tmp_path) -> None:
    server = _make_server(tmp_path)
    try:
        higher = server._db.create_user("HigherKills", "hash", trust_level=1)
        lower = server._db.create_user("LowerKills", "hash", trust_level=1)
        viewer = MockUser("HigherKills", uuid=higher.uuid)

        server._db.save_game_result(
            "battle",
            "2026-03-26T00:00:00",
            0,
            [(higher.uuid, "HigherKills", False), (lower.uuid, "LowerKills", False)],
            {
                "player_stats": {
                    higher.uuid: {"survival_kills": 13, "deepest_wave": 2},
                    lower.uuid: {"survival_kills": 12, "deepest_wave": 3},
                }
            },
        )

        server._show_custom_leaderboard(
            viewer,
            "battle",
            "Battle",
            {"id": "most_enemies_defeated", "aggregate": "max", "format": "score"},
        )
        leaderboard_texts = _menu_texts(viewer, "game_leaderboard")
        ranked_entries = [text for text in leaderboard_texts if text and text[0].isdigit()]

        assert "HigherKills" in ranked_entries[0]
        assert "13" in ranked_entries[0]
        assert "LowerKills" in ranked_entries[1]
        assert "12" in ranked_entries[1]
    finally:
        server._db.close()


def test_prediction_action_is_absent_from_rated_games() -> None:
    game = PigGame()
    player = game.add_player("Host", MockUser("Host", uuid="predict-host"))
    game.add_player("Guest", MockUser("Guest", uuid="predict-guest"))
    game.status = "playing"
    game.setup_keybinds()
    game.setup_player_actions(player)

    standard = game.get_action_set(player, "standard")
    assert standard is not None
    assert "predict_outcomes" not in standard._order
    assert "ctrl+r" not in game._keybinds
