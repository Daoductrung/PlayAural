"""
Tests for the Light Turret game.
"""

import json

from server.games.lightturret.game import (
    LightTurretGame,
    LightTurretPlayer,
    LightTurretOptions,
)
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestLightTurretGameUnit:
    """Unit tests for Light Turret game functions."""

    def test_game_creation(self):
        """Test creating a new Light Turret game."""
        game = LightTurretGame()
        assert game.get_name() == "Light Turret"
        assert game.get_type() == "lightturret"
        assert game.get_category() == "category-rb-play-center"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = LightTurretGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, LightTurretPlayer)
        assert player.alive is True
        assert player.power == 10
        assert player.light == 0

    def test_options_defaults(self):
        """Test default game options."""
        game = LightTurretGame()
        assert game.options.starting_power == 10

    def test_custom_options(self):
        """Test custom game options."""
        options = LightTurretOptions(starting_power=15)
        game = LightTurretGame(options=options)
        assert game.options.starting_power == 15

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = LightTurretGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.round = 3
        game.players[0].light = 2

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 3
        assert len(data["players"]) == 2
        assert data["players"][0]["light"] == 2

        # Deserialize
        loaded_game = LightTurretGame.from_json(json_str)
        assert loaded_game.round == 3
        assert loaded_game.players[0].light == 2


class TestLightTurretPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = LightTurretGame()

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 10000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = LightTurretGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 15000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestLightTurretPersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = LightTurretGame(options=LightTurretOptions(starting_power=15))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.round = 3
        game.players[0].light = 2
        game.players[0].power = 5

        # Save
        json_str = game.to_json()

        # Load
        loaded = LightTurretGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.round == 3
        assert loaded.players[0].light == 2
        assert loaded.players[0].power == 5
