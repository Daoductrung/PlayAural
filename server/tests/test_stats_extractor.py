import pytest

import server.games.registry as registry
from server.game_utils.game_result import GameResult, PlayerResult
from server.game_utils.stats_extractor import StatsExtractor


class MockGameClass:
    score_unit_key = "game-score-unit-chips"

    @classmethod
    def get_supported_leaderboards(cls):
        return ["wins", "total_score", "high_score", "games_played"]

    @classmethod
    def get_leaderboard_types(cls):
        return [
            {
                "id": "best_turn",
                "path": "player_stats.{player_name}.best_turn",
                "aggregate": "max",
            },
            {
                "id": "win_percentage",
                "numerator": "player_stats.{player_name}.wins",
                "denominator": "player_stats.{player_name}.games",
            },
        ]


@pytest.fixture(autouse=True)
def mock_get_game_class(monkeypatch):
    original_get = registry.get_game_class

    def override_get(gtype):
        if gtype == "mock_game":
            return MockGameClass
        return original_get(gtype)

    monkeypatch.setattr(registry, "get_game_class", override_get)


def test_extract_incremental_stats_basic():
    """Test extraction of basic stats like wins, losses, games_played, and scores."""
    gr = GameResult(
        game_type="mock_game",
        timestamp="2023-01-01T00:00:00",
        duration_ticks=100,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
            PlayerResult(player_id="uuid-2", player_name="Bob", is_bot=False),
            PlayerResult(player_id="uuid-3", player_name="Bot", is_bot=True),
        ],
        custom_data={
            "winner_name": "Alice",
            "winner_ids": ["uuid-1"],
            "score_unit_key": "game-score-unit-chips",
            "final_scores": {
                "Alice": 105,
                "Bob": 85,
                "Bot": 50,
            },
        },
    )

    updates = StatsExtractor.extract_incremental_stats(gr)

    # Bots should be ignored
    assert "uuid-3" not in updates

    alice_stats = updates["uuid-1"]
    assert alice_stats["games_played"] == 1.0
    assert alice_stats["wins"] == 1.0
    assert "losses" not in alice_stats
    assert alice_stats["total_score"] == 105.0
    assert alice_stats["high_score_high"] == 105.0

    bob_stats = updates["uuid-2"]
    assert bob_stats["games_played"] == 1.0
    assert bob_stats["losses"] == 1.0
    assert "wins" not in bob_stats
    assert bob_stats["total_score"] == 85.0
    assert bob_stats["high_score_high"] == 85.0


def test_extract_incremental_stats_custom_paths():
    """Test extraction of custom paths and ratios."""
    gr = GameResult(
        game_type="mock_game",
        timestamp="2023-01-01T00:00:00",
        duration_ticks=100,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
        ],
        custom_data={
            "winner_name": "Alice",
            "winner_ids": ["uuid-1"],
            "player_stats": {
                "Alice": {
                    "best_turn": 45,
                    "wins": 1,
                    "games": 1,
                }
            },
        },
    )

    updates = StatsExtractor.extract_incremental_stats(gr)

    alice_stats = updates["uuid-1"]

    # "best_turn" uses aggregate: "max", so it gets the "_high" suffix
    assert alice_stats["custom_best_turn_high"] == 45.0

    # "win_percentage" uses ratio
    assert alice_stats["custom_win_percentage_numerator"] == 1.0
    assert alice_stats["custom_win_percentage_denominator"] == 1.0


def test_supported_persisted_stat_keys_matches_extraction_schema():
    assert StatsExtractor.supported_persisted_stat_keys(MockGameClass) == {
        "games_played",
        "wins",
        "losses",
        "total_score",
        "high_score",
        "custom_best_turn_high",
        "custom_win_percentage_numerator",
        "custom_win_percentage_denominator",
    }


def test_draw_counts_a_game_without_awarding_wins_or_losses():
    result = GameResult(
        game_type="mock_game",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=20,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
            PlayerResult(player_id="uuid-2", player_name="Bob", is_bot=False),
        ],
        custom_data={"winner_ids": []},
    )

    updates = StatsExtractor.extract_incremental_stats(result)

    assert updates == {
        "uuid-1": {"games_played": 1.0},
        "uuid-2": {"games_played": 1.0},
    }


@pytest.mark.parametrize("score", [0, -5])
def test_numeric_nonpositive_scores_are_not_treated_as_missing(score):
    result = GameResult(
        game_type="mock_game",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=20,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
        ],
        custom_data={
            "winner_ids": [],
            "final_scores": {"Alice": score},
        },
    )

    assert StatsExtractor.extract_incremental_stats(result)["uuid-1"] == {
        "games_played": 1.0,
        "total_score": float(score),
        "high_score_high": float(score),
    }


@pytest.mark.parametrize(
    ("custom_data", "error"),
    [
        ({}, "immutable winner ids"),
        ({"winner_ids": ["outside-roster"]}, "result participants"),
        ({"winner_ids": ["uuid-1", "uuid-1"]}, "unique list"),
    ],
)
def test_win_stats_reject_invalid_winner_identity(custom_data, error):
    result = GameResult(
        game_type="mock_game",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=20,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
            PlayerResult(player_id="uuid-2", player_name="Bob", is_bot=False),
        ],
        custom_data=custom_data,
    )

    with pytest.raises(ValueError, match=error):
        StatsExtractor.extract_incremental_stats(result)


def test_stats_reject_duplicate_result_participants():
    result = GameResult(
        game_type="mock_game",
        timestamp="2026-10-01T00:00:00",
        duration_ticks=20,
        player_results=[
            PlayerResult(player_id="uuid-1", player_name="Alice", is_bot=False),
            PlayerResult(player_id="uuid-1", player_name="Alice again", is_bot=False),
        ],
        custom_data={"winner_ids": ["uuid-1"]},
    )

    with pytest.raises(ValueError, match="duplicate player ids"):
        StatsExtractor.extract_incremental_stats(result)


def test_extract_path_value():
    """Test the internal dot-notation dictionary path extractor."""
    data = {
        "level1": {
            "level2": {
                "value": 42,
            }
        }
    }

    assert StatsExtractor._extract_path_value(data, "level1.level2.value") == 42.0
    assert StatsExtractor._extract_path_value(data, "level1.invalid.value") is None
    assert StatsExtractor._extract_path_value(data, "missing") is None
    assert StatsExtractor._extract_path_value({"value": float("nan")}, "value") is None
    assert StatsExtractor._extract_path_value({"value": True}, "value") is None
