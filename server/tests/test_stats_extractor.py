import pytest
from server.game_utils.game_result import GameResult, PlayerResult
from server.game_utils.stats_extractor import StatsExtractor
import server.game_utils.stats_extractor

class MockGameClass:
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
            }
        ]

@pytest.fixture(autouse=True)
def mock_get_game_class(monkeypatch):
    # StatsExtractor does `from ..games.registry import get_game_class` inside the method.
    # To mock it effectively, we'll patch it in the sys.modules before it's imported, or just monkeypatch the method entirely.

    original_extract = StatsExtractor.extract_incremental_stats

    def extract_with_mock(result):
        # We can temporarily patch the game_class logic inside by subclassing/overriding
        pass

    # Since it imports it locally, we can just patch `server.game_utils.stats_extractor.get_game_class` if we pre-import it,
    # but Python local imports bind to the module they are imported from.
    # Easiest way is to monkeypatch the `builtins.__import__` or just monkeypatch the registry module directly
    import server.games.registry as registry
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
            "final_scores": {
                "Alice": 105,
                "Bob": 85,
                "Bot": 50
            }
        }
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
            "player_stats": {
                "Alice": {
                    "best_turn": 45,
                    "wins": 1,
                    "games": 1
                }
            }
        }
    )

    updates = StatsExtractor.extract_incremental_stats(gr)

    alice_stats = updates["uuid-1"]

    # "best_turn" uses aggregate: "max", so it gets the "_high" suffix
    assert alice_stats["custom_best_turn_high"] == 45.0

    # "win_percentage" uses ratio
    assert alice_stats["custom_win_percentage_numerator"] == 1.0
    assert alice_stats["custom_win_percentage_denominator"] == 1.0

def test_extract_path_value():
    """Test the internal dot-notation dictionary path extractor."""
    data = {
        "level1": {
            "level2": {
                "value": 42
            }
        }
    }

    assert StatsExtractor._extract_path_value(data, "level1.level2.value") == 42.0
    assert StatsExtractor._extract_path_value(data, "level1.invalid.value") is None
    assert StatsExtractor._extract_path_value(data, "missing") is None
