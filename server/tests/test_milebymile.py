"""
Tests for the Mile by Mile game.
"""

import json
import random

from server.games.milebymile.game import (
    MileByMileGame,
    MileByMilePlayer,
    MileByMileOptions,
    RaceState,
)
from server.games.milebymile.cards import HazardType, SafetyType
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestMileByMileGameUnit:
    """Unit tests for Mile by Mile game functions."""

    def test_game_creation(self):
        """Test creating a new Mile by Mile game."""
        game = MileByMileGame()
        assert game.get_name() == "Mile by Mile"
        assert game.get_type() == "milebymile"
        assert game.get_category() == "category-card-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 9

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = MileByMileGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, MileByMilePlayer)
        assert player.hand == []

    def test_options_defaults(self):
        """Test default game options."""
        game = MileByMileGame()
        assert game.options.round_distance == 1000
        assert game.options.winning_score == 5000

    def test_custom_options(self):
        """Test custom game options."""
        options = MileByMileOptions(round_distance=700, winning_score=3000)
        game = MileByMileGame(options=options)
        assert game.options.round_distance == 700
        assert game.options.winning_score == 3000


class TestRightOfWayBehavior:
    """Tests for Right of Way safety card behavior."""

    def test_right_of_way_allows_driving_when_stopped(self):
        """Right of Way should allow playing distance when only STOP is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_speed_limit(self):
        """Right of Way should allow playing distance when SPEED_LIMIT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_stop_and_speed_limit(self):
        """Right of Way should allow playing distance with both STOP and SPEED_LIMIT."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_does_not_protect_against_accident(self):
        """Right of Way should NOT allow playing distance when ACCIDENT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_flat_tire(self):
        """Right of Way should NOT allow playing distance when FLAT_TIRE is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.FLAT_TIRE)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_out_of_gas(self):
        """Right of Way should NOT allow playing distance when OUT_OF_GAS is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.OUT_OF_GAS)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_with_accident_and_stop(self):
        """Right of Way should NOT allow distance with ACCIDENT even if STOP also present."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False


class TestMileByMileSerialization:
    """Tests for game serialization."""

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = MileByMileGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.current_race = 1

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["current_race"] == 1
        assert len(data["players"]) == 2

        # Deserialize
        loaded_game = MileByMileGame.from_json(json_str)
        assert loaded_game.current_race == 1


class TestMileByMilePlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = MileByMileGame()
        game.options.round_distance = 300  # Lower target for faster test
        game.options.winning_score = 1000

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 30000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_team_game_completes(self):
        """Test that a 4-player team game completes."""
        random.seed(12345)
        game = MileByMileGame()
        game.options.round_distance = 500
        game.options.winning_score = 1000
        game.options.team_mode = "2v2"  # Internal format

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        # Verify teams are set up
        assert game.get_num_teams() == 2

        max_ticks = 100000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestMileByMilePersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = MileByMileGame(options=MileByMileOptions(round_distance=500))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.current_race = 1

        # Save
        json_str = game.to_json()

        # Load
        loaded = MileByMileGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.current_race == 1
        assert loaded.options.round_distance == 500
