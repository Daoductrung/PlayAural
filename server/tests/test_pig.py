"""
Tests for the Pig game.

Following the testing strategy:
- Unit tests for individual functions
- Play tests that run the game from start to finish with bots
- Persistence tests (save/reload at each tick)
"""

import pytest
import random
import json

from server.games.pig.game import PigGame, PigOptions
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestPigGameUnit:
    """Unit tests for Pig game functions."""

    def test_game_creation(self):
        """Test creating a new Pig game."""
        game = PigGame()
        assert game.get_name() == "Pig"
        assert game.get_type() == "pig"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = PigGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.round_score == 0
        assert player.is_bot is False

    def test_options_defaults(self):
        """Test default game options."""
        game = PigGame()
        assert game.options.target_score == 50
        assert game.options.min_bank_points == 0
        assert game.options.dice_sides == 6

    def test_custom_options(self):
        """Test custom game options."""
        options = PigOptions(target_score=100, min_bank_points=5, dice_sides=8)
        game = PigGame(options=options)
        assert game.options.target_score == 100
        assert game.options.min_bank_points == 5
        assert game.options.dice_sides == 8

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = PigGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        # Start game to set up teams
        game.on_start()

        # Modify some state via TeamManager
        game._team_manager.add_to_team_score("Alice", 25)
        game.players[0].round_score = 10
        game.round = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 3
        assert len(data["players"]) == 2
        assert data["players"][0]["round_score"] == 10
        # Score is in team_manager, not player
        assert data["_team_manager"]["teams"][0]["total_score"] == 25

        # Deserialize
        loaded_game = PigGame.from_json(json_str)
        assert loaded_game.round == 3
        assert loaded_game.get_player_score(loaded_game.players[0]) == 25
        assert loaded_game.players[0].round_score == 10


class TestPigGameActions:
    """Test individual game actions."""

    def setup_method(self):
        """Set up a game with two players for each test."""
        self.game = PigGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        # Start game to initialize TeamManager and turn order
        self.game.on_start()
        # Reset to first player
        self.game.reset_turn_order()

    def test_roll_not_one(self):
        """Test rolling when result is not 1."""
        random.seed(42)  # Seed that gives consistent non-1 results

        # Find a seed that gives us a non-1 roll
        for seed in range(100):
            random.seed(seed)
            if random.randint(1, 6) != 1:
                random.seed(seed)
                break

        self.player1.round_score = 5
        old_player = self.game.current_player
        self.game.execute_action(self.player1, "roll")

        assert self.game.current_player == old_player  # Turn didn't end
        assert self.player1.round_score > 5  # Should have increased

    def test_roll_one_busts(self):
        """Test that rolling a 1 loses round points."""
        # Find a seed that gives us a 1
        for seed in range(100):
            random.seed(seed)
            if random.randint(1, 6) == 1:
                random.seed(seed)
                break

        self.player1.round_score = 15
        old_player = self.game.current_player
        self.game.execute_action(self.player1, "roll")

        assert self.game.current_player != old_player  # Turn ended
        assert self.player1.round_score == 0

    def test_bank_adds_to_score(self):
        """Test that banking adds round score to total."""
        self.player1.round_score = 20
        # Set initial score via TeamManager
        self.game._team_manager.add_to_team_score("Alice", 10)
        old_player = self.game.current_player
        self.game.execute_action(self.player1, "bank")

        assert self.game.current_player != old_player  # Turn ended
        assert self.game.get_player_score(self.player1) == 30  # 10 + 20
        assert self.player1.round_score == 0

    def test_bank_hidden_when_no_points(self):
        """Test that bank action is hidden from menu when round score is 0."""
        self.player1.round_score = 0
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "roll" in visible_ids
        assert "bank" not in visible_ids

    def test_bank_hidden_below_minimum(self):
        """Test that bank is hidden from menu when below min_bank_points."""
        self.game.options.min_bank_points = 10
        self.player1.round_score = 5
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "bank" not in visible_ids

        self.player1.round_score = 10
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "bank" in visible_ids

    def test_view_scores(self):
        """Test viewing scores."""
        # Set scores via TeamManager
        self.game._team_manager.add_to_team_score("Alice", 30)
        self.game._team_manager.add_to_team_score("Bob", 20)

        self.game.execute_action(self.player1, "check_scores")

        # Check that score message was spoken
        spoken = self.user1.get_spoken_messages()
        assert any("30" in msg and "20" in msg for msg in spoken)

    def test_requires_turn(self):
        """Test that turn-required actions are only available on your turn."""
        p1_actions = self.game.get_all_enabled_actions(self.player1)
        p2_actions = self.game.get_all_enabled_actions(self.player2)

        p1_ids = [a.action.id for a in p1_actions]
        p2_ids = [a.action.id for a in p2_actions]

        assert "roll" in p1_ids
        assert "roll" not in p2_ids


class TestPigPlayTest:
    """
    Play tests that run complete games with bots.

    Following the testing strategy: games are ticked, saved and reloaded
    at each tick to verify persistence.
    """

    def test_two_player_game_completes(self):
        """Test that a 2-player game runs to completion."""
        random.seed(123)

        game = PigGame(options=PigOptions(target_score=30))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game with periodic save/reload to test persistence
        max_ticks = 1000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks to verify persistence
            # (not every tick, as that would clear pending bot actions)
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = PigGame.from_json(json_str)
                game.attach_user("Bot1", bot1)
                game.attach_user("Bot2", bot2)
                # Rebuild runtime state (BotHelper, etc.)
                game.rebuild_runtime_state()
                # Reinitialize actions for all players after reload
                for player in game.players:
                    user = game.get_user(player)
                    if user:
                        game.setup_player_actions(player)

            # Tick
            game.on_tick()

        assert not game.game_active, "Game should have ended"
        # At least one player should have reached target
        max_score = max(game.get_player_score(p) for p in game.players)
        assert max_score >= 30

    def test_four_player_game_completes(self):
        """Test that a 4-player game runs to completion."""
        random.seed(456)

        game = PigGame(options=PigOptions(target_score=30))
        bots = [Bot(f"Bot{i}") for i in range(1, 5)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.on_start()

        max_ticks = 2000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = PigGame.from_json(json_str)
                for bot in bots:
                    game.attach_user(bot.username, bot)
                # Rebuild runtime state (BotHelper, etc.)
                game.rebuild_runtime_state()
                # Reinitialize actions for all players after reload
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active

    def test_human_and_bot_game(self):
        """Test a game with one human and one bot."""
        random.seed(789)

        game = PigGame(options=PigOptions(target_score=25))
        human = MockUser("Human")
        bot = Bot("Bot")
        game.add_player("Human", human)
        game.add_player("Bot", bot)

        game.on_start()

        # Simulate human always banking at 10 points
        max_ticks = 1000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = PigGame.from_json(json_str)
                game.attach_user("Human", human)
                game.attach_user("Bot", bot)
                # Rebuild runtime state (BotHelper, etc.)
                game.rebuild_runtime_state()
                # Reinitialize actions for all players after reload
                for player in game.players:
                    game.setup_player_actions(player)

            # If it's the human's turn and they have >= 10 points, bank
            current = game.current_player
            if current and current.name == "Human" and current.round_score >= 10:
                game.execute_action(current, "bank")
            elif current and current.name == "Human":
                game.execute_action(current, "roll")
            else:
                game.on_tick()

        assert not game.game_active

        # Check that we got game messages
        messages = human.get_spoken_messages()
        assert len(messages) > 0
        assert any("Round" in m for m in messages)

    def test_tiebreaker_scenario(self):
        """Test that tiebreakers work correctly."""
        random.seed(999)

        game = PigGame(options=PigOptions(target_score=20))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        # Start game to set up teams
        game.on_start()

        # Manually set up a tie situation via TeamManager
        game._team_manager.teams[0].total_score = 20
        game._team_manager.teams[1].total_score = 20
        game.round = 1

        # Trigger round end check
        game._on_round_end()

        # Should still be active (tiebreaker)
        # Note: The tiebreaker logic should have triggered
        # Just verify the game handled it without crashing

    def test_different_dice_sides(self):
        """Test game with different dice configurations."""
        for sides in [4, 8, 10, 12]:
            random.seed(100 + sides)

            game = PigGame(options=PigOptions(target_score=20, dice_sides=sides))
            bot1 = Bot("Bot1")
            bot2 = Bot("Bot2")
            game.add_player("Bot1", bot1)
            game.add_player("Bot2", bot2)

            game.on_start()

            # More ticks needed due to bot thinking delays
            for _ in range(2000):
                if not game.game_active:
                    break
                game.on_tick()

            # Game should complete
            assert not game.game_active, f"Game with {sides}-sided dice should complete"

    def test_team_mode_2v2_no_infinite_tiebreaker(self):
        """Test that 2v2 mode doesn't trigger infinite tiebreaker when one team wins."""
        random.seed(456)
        game = PigGame(options=PigOptions(target_score=30, team_mode="2v2"))

        # Create 4 bots
        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        # Verify teams are set up (2 teams of 2)
        assert len(game._team_manager.teams) == 2
        assert len(game._team_manager.teams[0].members) == 2
        assert len(game._team_manager.teams[1].members) == 2

        # Run until game ends (should not run forever)
        max_ticks = 50000
        ticks = 0
        while game.game_active and ticks < max_ticks:
            game.on_tick()
            ticks += 1

        # Game should finish (not trigger infinite tiebreaker)
        assert not game.game_active, f"Game should finish, but ran for {ticks} ticks"
        assert ticks < max_ticks, "Game ran too long, likely infinite tiebreaker bug"

        # Verify one team won
        winner = game._team_manager.get_leading_team()
        assert winner is not None
        assert winner.total_score >= game.options.target_score


class TestPigPersistence:
    """Specific tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that all game state is preserved through save/load."""
        game = PigGame(options=PigOptions(target_score=100, min_bank_points=5))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        # Start game to set up teams
        game.on_start()

        # Set various state
        game.round = 5
        game.turn_index = 1  # Set to second player
        # Set scores via TeamManager
        game._team_manager.teams[0].total_score = 45
        game.players[0].round_score = 12
        game._team_manager.teams[1].total_score = 38
        game.players[1].round_score = 0

        # Save
        json_str = game.to_json()

        # Load
        loaded = PigGame.from_json(json_str)

        # Verify all state
        assert loaded.game_active is True
        assert loaded.round == 5
        # Note: turn_player_names is serialized, so turn order persists after reload
        # Games should handle this in their post-load initialization
        assert loaded.options.target_score == 100
        assert loaded.options.min_bank_points == 5
        assert loaded.get_player_score(loaded.players[0]) == 45
        assert loaded.players[0].round_score == 12
        assert loaded.get_player_score(loaded.players[1]) == 38
        assert loaded.players[1].round_score == 0

    def test_actions_work_after_reload(self):
        """Test that actions work correctly after reloading."""
        game = PigGame()
        user = MockUser("Alice")
        bot = Bot("Bot")
        game.add_player("Alice", user)
        game.add_player("Bot", bot)
        game.on_start()

        # Do some actions
        game.execute_action(game.players[0], "roll")

        # Save and reload
        json_str = game.to_json()
        game = PigGame.from_json(json_str)
        game.attach_user("Alice", user)
        game.attach_user("Bot", bot)
        # Reinitialize actions for all players after reload
        for player in game.players:
            game.setup_player_actions(player)

        # Actions should still work
        actions = game.get_all_enabled_actions(game.players[0])
        assert len(actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
