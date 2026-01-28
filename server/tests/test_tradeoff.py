"""
Tests for the Tradeoff game.
"""

import json

from server.games.tradeoff.game import (
    TradeoffGame,
    TradeoffPlayer,
    TradeoffOptions,
)
from server.games.tradeoff.scoring import (
    SET_DEFINITIONS,
    find_best_scoring,
    is_triple,
    is_group,
    is_mini_straight,
    is_double_triple,
    is_straight,
    is_double_group,
    is_all_groups,
    is_all_triplets,
)
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestTradeoffScoring:
    """Unit tests for Tradeoff scoring functions."""

    def test_is_triple(self):
        """Test triple detection."""
        assert is_triple([3, 3, 3]) is True
        assert is_triple([1, 1, 1]) is True
        assert is_triple([6, 6, 6]) is True
        assert is_triple([3, 3, 4]) is False
        assert is_triple([1, 2, 3]) is False
        assert is_triple([3, 3]) is False
        assert is_triple([3, 3, 3, 3]) is False

    def test_is_group(self):
        """Test group detection (5 of the same value)."""
        assert is_group([3, 3, 3, 3, 3]) is True
        assert is_group([1, 1, 1, 1, 1]) is True
        assert is_group([6, 6, 6, 6, 6]) is True
        assert is_group([3, 3, 3, 3, 4]) is False  # Not all same
        assert is_group([1, 2, 3, 4, 5]) is False  # All different
        assert is_group([3, 3, 3, 3]) is False  # Only 4 dice
        assert is_group([3, 3, 3, 3, 3, 3]) is False  # 6 dice

    def test_is_double_triple(self):
        """Test double triple detection."""
        assert is_double_triple([1, 1, 1, 2, 2, 2]) is True
        assert is_double_triple([3, 3, 3, 5, 5, 5]) is True
        assert is_double_triple([1, 1, 1, 1, 2, 2]) is False
        assert is_double_triple([1, 2, 3, 4, 5, 6]) is False
        assert is_double_triple([1, 1, 1, 2, 2]) is False

    def test_is_mini_straight(self):
        """Test mini straight detection (4 consecutive)."""
        assert is_mini_straight([1, 2, 3, 4]) is True
        assert is_mini_straight([2, 3, 4, 5]) is True
        assert is_mini_straight([3, 4, 5, 6]) is True
        assert is_mini_straight([4, 3, 2, 1]) is True  # Order doesn't matter
        assert is_mini_straight([1, 2, 3, 5]) is False  # Not consecutive
        assert is_mini_straight([1, 2, 3, 4, 5]) is False  # Too many dice
        assert is_mini_straight([1, 2, 3]) is False  # Too few dice

    def test_is_straight(self):
        """Test straight detection (5 consecutive)."""
        assert is_straight([1, 2, 3, 4, 5]) is True
        assert is_straight([2, 3, 4, 5, 6]) is True
        assert is_straight([5, 4, 3, 2, 1]) is True  # Order doesn't matter
        assert is_straight([1, 2, 3, 4, 6]) is False  # Not consecutive
        assert is_straight([1, 2, 3, 4, 5, 6]) is False  # Too many dice
        assert is_straight([1, 2, 3, 4]) is False  # Too few dice

    def test_is_double_group(self):
        """Test double group detection (5 of 2 kinds, 10 dice total)."""
        assert is_double_group([1, 1, 1, 1, 1, 2, 2, 2, 2, 2]) is True
        assert is_double_group([4, 4, 4, 4, 4, 6, 6, 6, 6, 6]) is True
        assert is_double_group([1, 1, 1, 1, 1, 2, 2, 2, 2, 3]) is False  # Not 5+5
        assert is_double_group([1, 1, 2, 2, 3, 3]) is False  # Only 6 dice
        assert is_double_group([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]) is False  # All same

    def test_is_all_triplets(self):
        """Test all triplets detection (5 triples, 15 dice)."""
        # 5 triples: 1,1,1 + 2,2,2 + 3,3,3 + 4,4,4 + 5,5,5
        dice = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
        assert is_all_triplets(dice) is True

        # Not valid - only 4 different values
        dice = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4]
        assert is_all_triplets(dice) is False

        # Wrong count
        dice = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]
        assert is_all_triplets(dice) is False

    def test_is_all_groups(self):
        """Test all groups detection (3 groups of 5 same, 15 dice)."""
        # Valid: 3 values, each appearing 5 times
        dice = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        assert is_all_groups(dice) is True

        # Different values work too
        dice = [4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6]
        assert is_all_groups(dice) is True

        # Not valid - only 2 different values
        dice = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        assert is_all_groups(dice) is False

        # Not valid - 4 different values
        dice = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
        assert is_all_groups(dice) is False

        # Wrong count
        dice = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        assert is_all_groups(dice) is False

    def test_find_best_scoring_single_triple(self):
        """Test finding a single triple."""
        dice = [3, 3, 3]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "triple"
        assert result[0][2] == 3

    def test_find_best_scoring_single_group(self):
        """Test finding a single group (5 of same)."""
        dice = [4, 4, 4, 4, 4]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "group"
        assert result[0][2] == 8

    def test_find_best_scoring_prefers_higher_points(self):
        """Test that scoring prefers groups (8 pts) over triples (3 pts)."""
        # With 5 same dice, we can make either a triple + leftover or a group
        # Group (8 pts) should be preferred over triple (3 pts)
        dice = [2, 2, 2, 2, 2]
        result = find_best_scoring(dice)
        assert result[0][0] == "group"
        assert result[0][2] == 8

    def test_find_best_scoring_double_group(self):
        """Test finding a double group (5 of 2 kinds, 10 dice)."""
        dice = [1, 1, 1, 1, 1, 3, 3, 3, 3, 3]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "double_group"
        assert result[0][2] == 30

    def test_find_best_scoring_straight(self):
        """Test finding a straight (5 consecutive)."""
        dice = [1, 2, 3, 4, 5]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "straight"
        assert result[0][2] == 12

    def test_find_best_scoring_all_triplets(self):
        """Test finding all triplets (highest possible, 50 pts)."""
        dice = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "all_triplets"
        assert result[0][2] == 50

    def test_find_best_scoring_multiple_sets(self):
        """Test finding multiple non-overlapping sets."""
        # 6 dice: double_triple (10 pts) vs 2 triples (6 pts)
        dice = [1, 1, 1, 2, 2, 2]
        result = find_best_scoring(dice)
        # Should prefer double_triple at 10 points
        assert sum(r[2] for r in result) == 10
        assert result[0][0] == "double_triple"

    def test_find_best_scoring_mini_straight(self):
        """Test finding a mini straight (4 consecutive)."""
        dice = [2, 3, 4, 5]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "mini_straight"
        assert result[0][2] == 7

    def test_find_best_scoring_prefers_straight_over_mini(self):
        """Test that straight (12 pts) is preferred over mini straight (7 pts)."""
        dice = [1, 2, 3, 4, 5]
        result = find_best_scoring(dice)
        assert result[0][0] == "straight"
        assert result[0][2] == 12

    def test_find_best_scoring_all_groups(self):
        """Test finding all groups (3 groups of 5 same, 50 pts)."""
        dice = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        result = find_best_scoring(dice)
        assert len(result) == 1
        assert result[0][0] == "all_groups"
        assert result[0][2] == 50

    def test_find_best_scoring_empty(self):
        """Test with empty dice list."""
        result = find_best_scoring([])
        assert result == []


class TestTradeoffPlayer:
    """Tests for TradeoffPlayer."""

    def test_player_defaults(self):
        """Test player default values."""
        player = TradeoffPlayer(id="123", name="Test")
        assert player.hand == []
        assert player.rolled_dice == []
        assert player.trading_indices == []
        assert player.trades_confirmed is False
        assert player.dice_traded_count == 0
        assert player.dice_taken_count == 0
        assert player.round_score == 0

    def test_player_is_bot(self):
        """Test bot player creation."""
        player = TradeoffPlayer(id="bot1", name="Bot", is_bot=True)
        assert player.is_bot is True


class TestTradeoffGameUnit:
    """Unit tests for Tradeoff game functions."""

    def test_game_creation(self):
        """Test creating a new Tradeoff game."""
        game = TradeoffGame()
        assert game.get_name() == "Tradeoff"
        assert game.get_type() == "tradeoff"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 8

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = TradeoffGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, TradeoffPlayer)

    def test_options_defaults(self):
        """Test default game options."""
        game = TradeoffGame()
        assert game.options.target_score == 60

    def test_custom_options(self):
        """Test custom game options."""
        options = TradeoffOptions(target_score=50)
        game = TradeoffGame(options=options)
        assert game.options.target_score == 50

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = TradeoffGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert len(data["players"]) == 2
        assert "hand" in data["players"][0]
        assert "rolled_dice" in data["players"][0]

        # Deserialize
        loaded_game = TradeoffGame.from_json(json_str)
        assert len(loaded_game.players) == 2


class TestTradeoffPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = TradeoffGame()
        game.options.target_score = 30  # Low target for fast test

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        max_ticks = 5000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_three_player_game_completes(self):
        """Test that a 3-player bot game completes."""
        game = TradeoffGame()
        game.options.target_score = 30  # Low target for fast test

        for i in range(3):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 5000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_eight_player_game_completes(self):
        """Test that an 8-player bot game completes."""
        game = TradeoffGame()
        game.options.target_score = 30  # Low target for fast test

        for i in range(8):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 10000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestTradeoffPersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = TradeoffGame(options=TradeoffOptions(target_score=50))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        alice: TradeoffPlayer = game.players[0]  # type: ignore
        alice.hand = [1, 2, 3, 4, 5]
        alice.dice_traded_count = 2

        game.pool = [6, 6]
        game.phase = "taking"

        # Save
        json_str = game.to_json()

        # Load
        loaded = TradeoffGame.from_json(json_str)
        loaded_alice: TradeoffPlayer = loaded.players[0]  # type: ignore

        # Verify state
        assert loaded.game_active is True
        assert loaded.options.target_score == 50
        assert loaded_alice.hand == [1, 2, 3, 4, 5]
        assert loaded_alice.dice_traded_count == 2
        assert loaded.pool == [6, 6]
        assert loaded.phase == "taking"

    def test_trading_state_preserved(self):
        """Test that trading phase state is preserved."""
        game = TradeoffGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set up trading state
        alice: TradeoffPlayer = game.players[0]  # type: ignore
        alice.rolled_dice = [1, 2, 3, 4, 5]
        alice.trading_indices = [0, 2]
        alice.trades_confirmed = False

        # Save and load
        json_str = game.to_json()
        loaded = TradeoffGame.from_json(json_str)
        loaded_alice: TradeoffPlayer = loaded.players[0]  # type: ignore

        assert loaded_alice.rolled_dice == [1, 2, 3, 4, 5]
        assert loaded_alice.trading_indices == [0, 2]
        assert loaded_alice.trades_confirmed is False


class TestTradeoffPhases:
    """Tests for game phase transitions."""

    def test_game_starts_in_trading_phase(self):
        """Test that game starts in trading phase."""
        game = TradeoffGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        assert game.phase == "trading"
        assert game.iteration == 1

    def test_pool_starts_empty(self):
        """Test that pool starts empty."""
        game = TradeoffGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        assert game.pool == []

    def test_players_get_rolled_dice(self):
        """Test that players get rolled dice at start of iteration."""
        game = TradeoffGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for p in game.players:
            tp: TradeoffPlayer = p  # type: ignore
            assert len(tp.rolled_dice) == 5
            assert all(1 <= d <= 6 for d in tp.rolled_dice)
