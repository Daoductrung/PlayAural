"""
Tests for the Snakes and Ladders game.
"""

import pytest
import random
from unittest.mock import patch, MagicMock

from ..games.snakesandladders.game import SnakesAndLaddersGame, SnakesPlayer
from ..users.test_user import MockUser
from ..users.bot import Bot


class TestSnakesGameUnit:
    """Unit tests for Snakes and Ladders game functions."""

    def test_game_creation(self):
        """Test creating a new Snakes game."""
        game = SnakesAndLaddersGame()
        assert game.get_name() == "Snakes and Ladders"
        assert game.get_type() == "snakesandladders"
        assert game.get_category() == "category-board-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4
        assert game.WINNING_SQUARE == 100

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = SnakesAndLaddersGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        # Type check to ensure we get the correct subclass
        assert isinstance(player, SnakesPlayer)
        assert player.name == "Alice"
        assert player.position == 1
        assert player.finished is False


class TestSnakesGameActions:
    """Test individual game actions and event processing."""

    def setup_method(self):
        """Set up a game with two players for each test."""
        self.game = SnakesAndLaddersGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        # Start game
        self.game.on_start()
        # Reset to first player
        self.game.reset_turn_order()
        # Initialize players
        self.player1.position = 1
        self.player2.position = 1

    def _run_ticks(self, count=100):
        """Helper to advance game time."""
        for _ in range(count):
            self.game.on_tick()

    def test_roll_movement(self):
        """Test basic movement."""
        # Patch random.randint to control roll
        # We need to patch where it is imported in the game module
        with patch('server.games.snakesandladders.game.random.randint') as mock_rand:
            # Sequence:
            # 1. Roll dice (1-6) -> 4
            # 2. Dice roll sound variant (1-3) -> 1
            # 3. 4 steps * step sound variant (1-3) -> 1, 1, 1, 1
            mock_rand.side_effect = [4, 1, 1, 1, 1, 1]
            
            # Execute
            self.game.execute_action(self.player1, "roll")
            
            # Check immediately after action (before tick processing)
            # Position should NOT have changed yet due to event queue
            assert self.player1.position == 1
            
            # Advance time sufficient for 4 steps + delays used in game.py
            # step_delay_start = 8
            # step_interval = 4
            # 4 steps: 8 + (3 * 4) = 20 ticks for sound scheduling?
            # actually logic says: move_complete_tick = current + 8 + (4*4) = current + 24
            # So running 50 ticks is safe.
            self._run_ticks(50)
            
            # Should be at 1 + 4 = 5
            assert self.player1.position == 5
            
            # Verify turn ended (switched to Bob)
            # Bob is player index 1 (Alice is 0)
            # After Alice moves, turn should pass.
            assert self.game.current_player == self.player2

    def test_ladder_climb(self):
        """Test landing on a ladder."""
        # Setup: Place player at 3. Roll 1 -> Land on 4.
        # Ladder at 4 goes to 14.
        self.player1.position = 3
        
        with patch('server.games.snakesandladders.game.random.randint') as mock_rand:
            # Sequence:
            # 1. Roll (1-6) -> 1
            # 2. Dice sound (1-3) -> 1
            # 3. Step sound (1-3) -> 1
            # 4. Ladder sound (1-3) -> 1
            mock_rand.side_effect = [1, 1, 1, 1]
            
            self.game.execute_action(self.player1, "roll")
            
            # Advance time (roll + step + ladder anim delays)
            # Ladder pause is 15 ticks.
            self._run_ticks(100)
            
            assert self.player1.position == 14
            # Turn should end
            assert self.game.current_player == self.player2

    def test_snake_bite(self):
        """Test landing on a snake."""
        # Setup: Place player at 15. Roll 1 -> Land on 16.
        # Snake at 16 goes to 6.
        self.player1.position = 15
        
        with patch('server.games.snakesandladders.game.random.randint') as mock_rand:
            # Sequence:
            # 1. Roll -> 1
            # 2. Dice sound -> 1
            # 3. Step sound -> 1
            # 4. Snake sound logic doesn't use randint, it plays fixed 'snake.ogg'
            # Wait, let's check game.py: 
            # self.schedule_sound("game_snakes/snake.ogg", ...)
            # So only 3 calls to randint here.
            mock_rand.side_effect = [1, 1, 1]
            
            self.game.execute_action(self.player1, "roll")
            
            # Advance time
            self._run_ticks(100)
            
            assert self.player1.position == 6
            assert self.game.current_player == self.player2

    def test_bounce_back(self):
        """Test bouncing back from 100."""
        # Setup: Place at 98. Roll 4.
        # 98 + 4 = 102. Overshoot 2. 100 - 2 = 98.
        self.player1.position = 98
        
        with patch('server.games.snakesandladders.game.random.randint') as mock_rand:
            # Sequence:
            # 1. Roll -> 4
            # 2. Dice sound -> 1
            # 3. 4 Steps -> 1, 1, 1, 1
            mock_rand.side_effect = [4, 1, 1, 1, 1, 1] 
            
            self.game.execute_action(self.player1, "roll")
            
            self._run_ticks(100)
            
            # Should end up back at 98, BUT there is a Snake at 98!
            # Snake at 98 goes to 78.
            assert self.player1.position == 78
            # Turn ends
            assert self.game.current_player == self.player2

    def test_win_condition(self):
        """Test exact roll to win."""
        # Setup: Place at 98. Roll 2 -> 100.
        self.player1.position = 98
        
        with patch('server.games.snakesandladders.game.random.randint') as mock_rand:
            # Sequence:
            # 1. Roll -> 2
            # 2. Dice sound -> 1
            # 3. 2 Steps -> 1, 1
            mock_rand.side_effect = [2, 1, 1, 1]
            
            self.game.execute_action(self.player1, "roll")
            
            self._run_ticks(100)
            
            assert self.player1.position == 100
            assert self.player1.finished is True
            assert self.game.winner == self.player1
            assert self.game.status == "finished"

    def test_check_positions(self):
        """Test check positions action."""
        self.player1.position = 5
        self.player2.position = 10
        
        # User 1 checks positions
        self.game.execute_action(self.player1, "check_positions")
        
        # Not a queued event, happens immediately
        # (Though status_box might be delayed, speak() is usually immediate in tests)
        messages = self.user1.get_spoken_messages()
        # Since MockUser stores messages, we can check them.
        # "Positions: Alice 5, Bob 10"
        
        # Depending on how MockUser is implemented, it might store list of strings
        combined = " ".join(messages)
        assert "Alice 5" in combined
        assert "Bob 10" in combined


class TestSnakesPlayTest:
    """Full game simulation."""

    def test_bot_game_completes(self):
        """Test that a game with bots runs to completion."""
        # Use simple seed
        random.seed(42)
        
        game = SnakesAndLaddersGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)
        
        game.on_start()
        
        # Run until finished or timeout
        # Snakes and ladders can be long, so allow many ticks
        max_ticks = 50000 
        ticks = 0
        while game.game_active and ticks < max_ticks:
            game.on_tick()
            ticks += 1
            
        assert not game.game_active, f"Game should finish within {max_ticks} ticks"
        assert game.winner is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

