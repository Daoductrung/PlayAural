from server.core.server import Server
from server.game_utils.game_result import GameResult, PlayerResult
from server.game_utils.stats_extractor import StatsExtractor
from server.games.backgammon.game import BackgammonGame
from server.games.base import Game
from server.games.metalpipe.game import MetalPipeGame
from server.games.pig.game import PigGame
from server.games.threes.game import ThreesGame
from server.games.twentyone.game import TwentyOneGame
from server.users.test_user import MockUser


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.id for item in items if hasattr(item, "id")]


def test_base_game_does_not_advertise_leaderboards_by_default() -> None:
    assert Game.get_supported_leaderboards() == []


def test_leaderboards_menu_hides_games_without_declared_leaderboards() -> None:
    server = Server(db_path=":memory:")
    user = MockUser("Viewer")

    server._show_leaderboards_menu(user)

    item_ids = _menu_ids(user, "leaderboards_menu")
    assert "lb_metalpipe" not in item_ids
    assert "lb_pig" in item_ids
    assert "lb_backgammon" in item_ids
    assert "lb_twentyone" in item_ids
    assert item_ids[-1] == "back"


def test_scoreless_examples_do_not_expose_score_leaderboards() -> None:
    assert MetalPipeGame.get_supported_leaderboards() == []
    assert "total_score" not in BackgammonGame.get_supported_leaderboards()
    assert "high_score" not in BackgammonGame.get_supported_leaderboards()
    assert "total_score" not in TwentyOneGame.get_supported_leaderboards()
    assert "high_score" not in TwentyOneGame.get_supported_leaderboards()
    assert "total_score" not in ThreesGame.get_supported_leaderboards()
    assert "high_score" not in ThreesGame.get_supported_leaderboards()


def test_score_games_keep_explicit_score_leaderboards() -> None:
    assert PigGame.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]


def test_unsupported_game_type_menu_has_no_leaderboard_actions() -> None:
    server = Server(db_path=":memory:")
    user = MockUser("Viewer")

    server._show_leaderboard_types_menu(user, "metalpipe")

    assert _menu_ids(user, "leaderboard_types_menu") == ["no_data", "back"]
    assert not server._leaderboard_selection_exists("metalpipe", "type_wins")
    assert not server._leaderboard_selection_exists("metalpipe", "type_games_played")


def test_non_score_games_only_offer_supported_leaderboard_types() -> None:
    server = Server(db_path=":memory:")
    user = MockUser("Viewer")

    server._show_leaderboard_types_menu(user, "backgammon")

    item_ids = _menu_ids(user, "leaderboard_types_menu")
    assert "type_wins" in item_ids
    assert "type_rating" in item_ids
    assert "type_games_played" in item_ids
    assert "type_total_score" not in item_ids
    assert "type_high_score" not in item_ids


def test_unsupported_game_results_do_not_create_stats_updates() -> None:
    result = GameResult(
        game_type="metalpipe",
        timestamp="2026-06-10T00:00:00",
        duration_ticks=0,
        player_results=[
            PlayerResult("alice-id", "Alice", False),
            PlayerResult("bob-id", "Bob", False),
        ],
        custom_data={"winner_names": ["Alice"]},
    )

    assert StatsExtractor.extract_incremental_stats(result) == {}
