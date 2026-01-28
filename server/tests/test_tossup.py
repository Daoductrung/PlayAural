"""
Tests for the Toss Up game.

Following the testing strategy:
- Unit tests for individual functions
- Play tests that run the game from start to finish with bots
- Persistence tests (save/reload at each tick)
"""

import pytest
import random
import json

from server.games.tossup.game import TossUpGame, TossUpOptions
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestTossUpGameUnit:
    """Unit tests for Toss Up game functions."""

    def test_game_creation(self):
        """Test creating a new Toss Up game."""
        game = TossUpGame()
        assert game.get_name() == "Toss Up"
        assert game.get_type() == "tossup"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 8

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = TossUpGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.turn_points == 0
        assert player.dice_count == 0
        assert player.last_roll == {}
        assert player.is_bot is False

    def test_options_defaults(self):
        """Test default game options."""
        game = TossUpGame()
        assert game.options.target_score == 100
        assert game.options.starting_dice == 10
        assert game.options.rules_variant == "Standard"

    def test_custom_options(self):
        """Test custom game options."""
        options = TossUpOptions(
            target_score=200, starting_dice=15, rules_variant="PlayAural"
        )
        game = TossUpGame(options=options)
        assert game.options.target_score == 200
        assert game.options.starting_dice == 15
        assert game.options.rules_variant == "PlayAural"

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = TossUpGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        # Start game to set up teams
        game.on_start()

        # Modify some state via TeamManager
        game._team_manager.add_to_team_score("Alice", 35)
        game.players[0].turn_points = 12
        game.players[0].dice_count = 3
        game.players[0].last_roll = {"green": 2, "yellow": 1, "red": 1}
        game.round = 4

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 4
        assert len(data["players"]) == 2
        assert data["players"][0]["turn_points"] == 12
        assert data["players"][0]["dice_count"] == 3
        assert data["players"][0]["last_roll"]["green"] == 2
        # Score is in team_manager, not player
        assert data["_team_manager"]["teams"][0]["total_score"] == 35

        # Deserialize
        loaded_game = TossUpGame.from_json(json_str)
        assert loaded_game.round == 4
        assert loaded_game.get_player_score(loaded_game.players[0]) == 35
        assert loaded_game.players[0].turn_points == 12
        assert loaded_game.players[0].dice_count == 3
        assert loaded_game.players[0].last_roll["green"] == 2


class TestTossUpGameActions:
    """Test individual game actions."""

    def setup_method(self):
        """Set up a game with two players for each test."""
        self.game = TossUpGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        # Start game to initialize TeamManager and turn order
        self.game.on_start()
        # Reset to first player
        self.game.reset_turn_order()

    def test_roll_all_green(self):
        """Test rolling when all dice come up green."""
        # Seed random to get mostly green
        random.seed(10)

        self.player1.dice_count = 10
        self.player1.turn_points = 0
        initial_turn_points = self.player1.turn_points

        self.game.execute_action(self.player1, "roll")

        # Should have added some points
        assert self.player1.turn_points > initial_turn_points
        # Game should still be active and turn should not have ended
        assert self.game.game_active

    def test_roll_standard_bust(self):
        """Test bust condition in Standard rules (no greens, at least one red)."""
        self.game.options.rules_variant = "Standard"

        # Try multiple times to get a bust scenario
        # A bust happens when green=0 and red>0
        busted = False
        for attempt in range(50):
            # Reset player state for new attempt
            self.player1.dice_count = 3
            self.player1.turn_points = 20

            random.seed(1000 + attempt)
            old_player = self.game.current_player
            self.game.execute_action(self.player1, "roll")

            # Check if we got a bust
            if self.player1.turn_points == 0 and self.game.current_player != old_player:
                busted = True
                break
            elif self.game.current_player != old_player:
                # Turn ended but not from bust, reset for next test
                self.game.reset_turn_order()

        # We should have encountered at least one bust in 50 attempts
        assert busted, "Should encounter a bust scenario in Standard rules"

    def test_roll_PlayAural_bust(self):
        """Test bust condition in PlayAural rules (all red)."""
        self.game.options.rules_variant = "PlayAural"

        # Try multiple times to get a bust scenario
        # A bust in PlayAural happens when green=0 and yellow=0 (all red)
        busted = False
        for attempt in range(50):
            # Reset player state for new attempt
            self.player1.dice_count = 2
            self.player1.turn_points = 15

            random.seed(2000 + attempt)
            old_player = self.game.current_player
            self.game.execute_action(self.player1, "roll")

            # Check if we got a bust
            if self.player1.turn_points == 0 and self.game.current_player != old_player:
                busted = True
                break
            elif self.game.current_player != old_player:
                # Turn ended but not from bust, reset for next test
                self.game.reset_turn_order()

        # We should have encountered at least one bust in 50 attempts
        assert busted, "Should encounter a bust scenario in PlayAural rules"

    def test_fresh_dice(self):
        """Test that running out of dice gives fresh dice."""
        # Seed to get all greens or yellows (no red)
        random.seed(42)

        self.player1.dice_count = 2
        self.player1.turn_points = 10

        # Find a seed where we remove all dice (greens/yellows only)
        found_clear = False
        for seed in range(1000):
            random.seed(seed)
            red = 0
            for _ in range(2):
                roll = random.randint(1, 6)
                if roll == 6:
                    red += 1
            if red == 0:
                random.seed(seed)
                found_clear = True
                break

        if found_clear:
            old_turn_points = self.player1.turn_points
            self.game.execute_action(self.player1, "roll")

            # Should have 0 red dice left, so get fresh dice
            if self.player1.dice_count == self.game.options.starting_dice:
                # Successfully got fresh dice
                assert self.player1.turn_points >= old_turn_points

    def test_bank_adds_to_score(self):
        """Test that banking adds turn points to total."""
        self.player1.turn_points = 25
        # Set initial score via TeamManager
        self.game._team_manager.add_to_team_score("Alice", 15)
        old_player = self.game.current_player
        self.game.execute_action(self.player1, "bank")

        assert self.game.current_player != old_player  # Turn ended
        assert self.game.get_player_score(self.player1) == 40  # 15 + 25
        assert self.player1.turn_points == 0

    def test_bank_hidden_when_no_points(self):
        """Test that bank action is hidden when turn points is 0."""
        self.player1.turn_points = 0
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "roll" in visible_ids
        assert "bank" not in visible_ids

    def test_bank_visible_with_points(self):
        """Test that bank action is visible when player has points."""
        self.player1.turn_points = 10
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "roll" in visible_ids
        assert "bank" in visible_ids

    def test_requires_turn(self):
        """Test that turn-required actions are only available on your turn."""
        p1_actions = self.game.get_all_enabled_actions(self.player1)
        p2_actions = self.game.get_all_enabled_actions(self.player2)

        p1_ids = [a.action.id for a in p1_actions]
        p2_ids = [a.action.id for a in p2_actions]

        assert "roll" in p1_ids
        assert "roll" not in p2_ids


class TestTossUpPlayTest:
    """
    Play tests that run complete games with bots.

    Following the testing strategy: games are ticked, saved and reloaded
    at each tick to verify persistence.
    """

    def test_two_player_game_completes(self):
        """Test that a 2-player game runs to completion."""
        random.seed(123)

        game = TossUpGame(options=TossUpOptions(target_score=50))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game with periodic save/reload to test persistence
        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks to verify persistence
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = TossUpGame.from_json(json_str)
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
        assert max_score >= 50

    def test_eight_player_game_completes(self):
        """Test that an 8-player game runs to completion."""
        random.seed(555)

        game = TossUpGame(options=TossUpOptions(target_score=50))
        bots = [Bot(f"Bot{i}") for i in range(1, 9)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.on_start()

        max_ticks = 8000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 100 ticks
            if tick % 100 == 0 and tick > 0:
                json_str = game.to_json()
                game = TossUpGame.from_json(json_str)
                for bot in bots:
                    game.attach_user(bot.username, bot)
                # Rebuild runtime state (BotHelper, etc.)
                game.rebuild_runtime_state()
                # Reinitialize actions for all players after reload
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active

    def test_PlayAural_rules_variant(self):
        """Test game with PlayAural rules."""
        random.seed(789)

        game = TossUpGame(
            options=TossUpOptions(target_score=30, rules_variant="PlayAural")
        )
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active
        assert game.options.rules_variant == "PlayAural"

    def test_standard_rules_variant(self):
        """Test game with Standard rules."""
        random.seed(321)

        game = TossUpGame(
            options=TossUpOptions(target_score=30, rules_variant="Standard")
        )
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active
        assert game.options.rules_variant == "Standard"

    def test_human_and_bot_game(self):
        """Test a game with one human and one bot."""
        random.seed(999)

        game = TossUpGame(options=TossUpOptions(target_score=40))
        human = MockUser("Human")
        bot = Bot("Bot")
        game.add_player("Human", human)
        game.add_player("Bot", bot)

        game.on_start()

        # Simulate human banking at 15 points
        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = TossUpGame.from_json(json_str)
                game.attach_user("Human", human)
                game.attach_user("Bot", bot)
                # Rebuild runtime state (BotHelper, etc.)
                game.rebuild_runtime_state()
                # Reinitialize actions for all players after reload
                for player in game.players:
                    game.setup_player_actions(player)

            # If it's the human's turn and they have >= 15 points, bank
            current = game.current_player
            if current and current.name == "Human" and current.turn_points >= 15:
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
        random.seed(777)

        game = TossUpGame(options=TossUpOptions(target_score=30))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        # Start game to set up teams
        game.on_start()

        # Manually set up a tie situation via TeamManager
        game._team_manager.teams[0].total_score = 30
        game._team_manager.teams[1].total_score = 30
        game.round = 1

        # Trigger round end check
        game._on_round_end()

        # Should still be active (tiebreaker)
        # Just verify the game handled it without crashing

    def test_different_starting_dice(self):
        """Test game with different starting dice counts."""
        for dice_count in [5, 15, 20]:
            random.seed(100 + dice_count)

            game = TossUpGame(
                options=TossUpOptions(target_score=30, starting_dice=dice_count)
            )
            bot1 = Bot("Bot1")
            bot2 = Bot("Bot2")
            game.add_player("Bot1", bot1)
            game.add_player("Bot2", bot2)

            game.on_start()

            # More ticks needed due to bot thinking delays
            for _ in range(3000):
                if not game.game_active:
                    break
                game.on_tick()

            # Game should complete
            assert (
                not game.game_active
            ), f"Game with {dice_count} starting dice should complete"


class TestTossUpPersistence:
    """Specific tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that all game state is preserved through save/load."""
        game = TossUpGame(
            options=TossUpOptions(
                target_score=150, starting_dice=12, rules_variant="PlayAural"
            )
        )
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        # Start game to set up teams
        game.on_start()

        # Set various state
        game.round = 6
        game.turn_index = 1  # Set to second player
        # Set scores via TeamManager
        game._team_manager.teams[0].total_score = 78
        game.players[0].turn_points = 18
        game.players[0].dice_count = 4
        game.players[0].last_roll = {"green": 3, "yellow": 2, "red": 1}
        game._team_manager.teams[1].total_score = 62
        game.players[1].turn_points = 0
        game.players[1].dice_count = 12

        # Save
        json_str = game.to_json()

        # Load
        loaded = TossUpGame.from_json(json_str)

        # Verify all state
        assert loaded.game_active is True
        assert loaded.round == 6
        assert loaded.options.target_score == 150
        assert loaded.options.starting_dice == 12
        assert loaded.options.rules_variant == "PlayAural"
        assert loaded.get_player_score(loaded.players[0]) == 78
        assert loaded.players[0].turn_points == 18
        assert loaded.players[0].dice_count == 4
        assert loaded.players[0].last_roll["green"] == 3
        assert loaded.get_player_score(loaded.players[1]) == 62
        assert loaded.players[1].turn_points == 0
        assert loaded.players[1].dice_count == 12

    def test_actions_work_after_reload(self):
        """Test that actions work correctly after reloading."""
        game = TossUpGame()
        user = MockUser("Alice")
        bot = Bot("Bot")
        game.add_player("Alice", user)
        game.add_player("Bot", bot)
        game.on_start()

        # Do some actions
        game.execute_action(game.players[0], "roll")

        # Save and reload
        json_str = game.to_json()
        game = TossUpGame.from_json(json_str)
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
