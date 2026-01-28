"""
Tests for the Chaos Bear game.
"""

import json

from server.games.chaosbear.game import ChaosBearGame, ChaosBearPlayer
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestChaosBearGameUnit:
    """Unit tests for Chaos Bear game functions."""

    def test_game_creation(self):
        """Test creating a new Chaos Bear game."""
        game = ChaosBearGame()
        assert game.get_name() == "Chaos Bear"
        assert game.get_type() == "chaosbear"
        assert game.get_category() == "category-rb-play-center"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = ChaosBearGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, ChaosBearPlayer)
        assert player.alive is True
        assert player.position == 0

    def test_initial_game_state(self):
        """Test initial game state."""
        game = ChaosBearGame()
        assert game.bear_position == 0
        assert game.bear_energy == 1
        assert game.round_number == 0

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.bear_position = 5
        game.bear_energy = 3
        game.round_number = 2
        game.players[0].position = 10

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["bear_position"] == 5
        assert data["bear_energy"] == 3
        assert data["round_number"] == 2
        assert data["players"][0]["position"] == 10

        # Deserialize
        loaded_game = ChaosBearGame.from_json(json_str)
        assert loaded_game.bear_position == 5
        assert loaded_game.bear_energy == 3
        assert loaded_game.round_number == 2
        assert loaded_game.players[0].position == 10


class TestChaosBearPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = ChaosBearGame()

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 20000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = ChaosBearGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 30000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestChaosBearPersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.bear_position = 5
        game.bear_energy = 3
        game.round_number = 2
        game.players[0].position = 10
        game.players[0].alive = True

        # Save
        json_str = game.to_json()

        # Load
        loaded = ChaosBearGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.bear_position == 5
        assert loaded.bear_energy == 3
        assert loaded.round_number == 2
        assert loaded.players[0].position == 10
        assert loaded.players[0].alive is True
