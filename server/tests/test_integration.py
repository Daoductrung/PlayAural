"""
Integration tests for PlayAural v0.1.

Tests larger chunks of server code working together.
"""

import pytest
import tempfile
import os

from ..persistence.database import Database
from ..auth.auth import AuthManager
from ..tables.manager import TableManager
from ..tables.table import Table
from ..users.test_user import MockUser
from ..users.bot import Bot
from ..games.pig.game import PigGame, PigOptions
from ..games.registry import GameRegistry, get_game_class


class TestDatabaseIntegration:
    """Test database operations."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()

    def teardown_method(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_file.name)

    def test_user_creation_and_retrieval(self):
        """Test creating and retrieving users."""
        # Create user
        user = self.db.create_user("testuser", "hashedpassword", "en")
        assert user.username == "testuser"
        assert user.password_hash == "hashedpassword"
        assert user.locale == "en"

        # Retrieve user
        retrieved = self.db.get_user("testuser")
        assert retrieved is not None
        assert retrieved.username == "testuser"

    def test_user_exists(self):
        """Test checking if user exists."""
        assert not self.db.user_exists("newuser")
        self.db.create_user("newuser", "hash", "en")
        assert self.db.user_exists("newuser")

    def test_table_save_and_load(self):
        """Test saving and loading tables."""
        # Create a table
        table = Table(
            table_id="test123",
            game_type="pig",
            host="testhost",
            status="waiting",
        )
        table.add_member("testhost", MockUser("testhost"))

        # Save
        self.db.save_table(table)

        # Load
        loaded = self.db.load_table("test123")
        assert loaded is not None
        assert loaded.table_id == "test123"
        assert loaded.game_type == "pig"
        assert loaded.host == "testhost"
        assert len(loaded.members) == 1
        assert loaded.members[0].username == "testhost"

    def test_table_with_game_state(self):
        """Test saving and loading table with game state."""
        table = Table(
            table_id="game123",
            game_type="pig",
            host="player1",
        )

        # Create a game with some state
        game = PigGame()
        user1 = MockUser("player1")
        user2 = Bot("Bot1")
        game.add_player("player1", user1)
        game.add_player("Bot1", user2)
        game.on_start()  # Initialize TeamManager
        game.round = 3
        game._team_manager.add_to_team_score("player1", 25)

        table.game = game
        table.game_json = game.to_json()

        # Save
        self.db.save_table(table)

        # Load
        loaded = self.db.load_table("game123")
        assert loaded is not None
        assert loaded.game_json is not None

        # Deserialize game
        loaded_game = PigGame.from_json(loaded.game_json)
        assert loaded_game.round == 3
        assert loaded_game.get_player_score(loaded_game.players[0]) == 25


class TestAuthIntegration:
    """Test authentication system."""

    def setup_method(self):
        """Create temporary database and auth manager."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()
        self.auth = AuthManager(self.db)

    def teardown_method(self):
        """Clean up."""
        self.db.close()
        os.unlink(self.temp_file.name)

    def test_register_and_authenticate(self):
        """Test user registration and authentication."""
        # Register
        assert self.auth.register("newuser", "password123")
        assert not self.auth.register("newuser", "different")  # Already exists

        # Authenticate
        assert self.auth.authenticate("newuser", "password123")
        assert not self.auth.authenticate("newuser", "wrongpassword")
        assert not self.auth.authenticate("nonexistent", "password")

    def test_session_management(self):
        """Test session token creation and validation."""
        self.auth.register("sessionuser", "pass")

        # Create session
        token = self.auth.create_session("sessionuser")
        assert token is not None

        # Validate
        username = self.auth.validate_session(token)
        assert username == "sessionuser"

        # Invalidate
        self.auth.invalidate_session(token)
        assert self.auth.validate_session(token) is None


class TestTableManagerIntegration:
    """Test table manager operations."""

    def test_create_and_find_table(self):
        """Test creating and finding tables."""
        manager = TableManager()
        user = MockUser("host")

        table = manager.create_table("pig", "host", user)
        assert table.table_id is not None
        assert table.game_type == "pig"
        assert table.host == "host"

        # Find by ID
        found = manager.get_table(table.table_id)
        assert found is table

        # Find by user
        user_table = manager.find_user_table("host")
        assert user_table is table

    def test_waiting_tables(self):
        """Test getting waiting tables."""
        manager = TableManager()
        user1 = MockUser("host1")
        user2 = MockUser("host2")

        manager.create_table("pig", "host1", user1)
        manager.create_table("pig", "host2", user2)
        manager.create_table("other", "host1", user1)

        waiting = manager.get_waiting_tables("pig")
        assert len(waiting) == 2

        waiting_all = manager.get_waiting_tables()
        assert len(waiting_all) == 3


class TestGameRegistryIntegration:
    """Test game registry."""

    def test_pig_game_registered(self):
        """Test that Pig game is registered."""
        # Import to trigger registration
        from ..games.pig.game import PigGame

        game_class = get_game_class("pig")
        assert game_class is PigGame

    def test_get_by_category(self):
        """Test getting games by category."""
        from ..games.pig.game import PigGame

        categories = GameRegistry.get_by_category()
        assert "category-dice-games" in categories
        assert PigGame in categories["category-dice-games"]


class TestFullGameFlow:
    """Test complete game flow from creation to completion."""

    def test_complete_game_with_persistence(self):
        """Test a complete game flow with save/load at each step."""
        import random

        random.seed(42)

        # Create table
        manager = TableManager()
        host = MockUser("Host")
        table = manager.create_table("pig", "Host", host)

        # Add players
        player2 = MockUser("Player2")
        bot = Bot("Bot1")
        table.add_member("Player2", player2)
        table.add_member("Bot1", bot)

        # Start game
        game = PigGame(options=PigOptions(target_score=25))
        for member in table.get_players():
            user = table.get_user(member.username)
            game.add_player(member.username, user)

        table.game = game
        table.status = "playing"
        game.on_start()

        # Run game with periodic saves
        max_ticks = 500
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save state every 10 ticks
            if tick % 10 == 0:
                table.save_game_state()
                json_data = table.game_json

                # Verify we can reload
                loaded = PigGame.from_json(json_data)
                assert loaded.round == game.round

            # Tick
            game.on_tick()

            # Simulate human player actions (simple strategy)
            current = game.current_player
            if current and not current.is_bot:
                if current.round_score >= 15:
                    game.execute_action(current, "bank")
                else:
                    game.execute_action(current, "roll")

        assert not game.game_active, "Game should complete"
        max_score = max(game.get_player_score(p) for p in game.players)
        assert max_score >= 25, "Winner should have reached target"

        # Verify messages were sent
        host_messages = host.get_spoken_messages()
        assert any("Round" in m for m in host_messages)
        assert any("winner" in m.lower() for m in host_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

