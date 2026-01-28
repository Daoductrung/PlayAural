"""
Test that action_id parameter is passed correctly to is_enabled and is_hidden methods.

This verifies the enhancement to the action system that allows methods to optionally
receive the action_id as a keyword argument.
"""

import pytest

from server.games.threes.game import ThreesGame
from server.games.midnight.game import MidnightGame
from server.users.test_user import MockUser


class TestActionIdPassing:
    """Test that action_id is passed to methods that accept it."""

    def test_threes_dice_toggle_with_5_dice(self):
        """Test Threes with 5 dice - all toggle actions should work."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()

        # Get all visible actions
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # All 5 dice toggle actions should be visible
        assert "toggle_die_0" in visible_ids
        assert "toggle_die_1" in visible_ids
        assert "toggle_die_2" in visible_ids
        assert "toggle_die_3" in visible_ids
        assert "toggle_die_4" in visible_ids

        # All should be enabled (assuming more than 1 unlocked die)
        turn_set = game.get_action_set(player, "turn")
        resolved = turn_set.resolve_actions(game, player) if turn_set else []
        enabled_ids = [a.action.id for a in resolved if a.enabled]

        if player.dice.unlocked_count > 1:
            assert "toggle_die_0" in enabled_ids
            assert "toggle_die_1" in enabled_ids
            assert "toggle_die_2" in enabled_ids
            assert "toggle_die_3" in enabled_ids
            assert "toggle_die_4" in enabled_ids

    def test_midnight_dice_toggle_with_6_dice(self):
        """Test Midnight with 6 dice - all toggle actions should work."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()

        # Get all visible actions
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # All 6 dice toggle actions should be visible
        assert "toggle_die_0" in visible_ids
        assert "toggle_die_1" in visible_ids
        assert "toggle_die_2" in visible_ids
        assert "toggle_die_3" in visible_ids
        assert "toggle_die_4" in visible_ids
        assert "toggle_die_5" in visible_ids  # This is the critical one

        # All should be enabled (no dice locked yet)
        turn_set = game.get_action_set(player, "turn")
        resolved = turn_set.resolve_actions(game, player) if turn_set else []
        enabled_ids = [a.action.id for a in resolved if a.enabled]

        assert "toggle_die_0" in enabled_ids
        assert "toggle_die_1" in enabled_ids
        assert "toggle_die_2" in enabled_ids
        assert "toggle_die_3" in enabled_ids
        assert "toggle_die_4" in enabled_ids
        assert "toggle_die_5" in enabled_ids

    def test_dice_toggles_hidden_before_roll(self):
        """Test that dice toggles are hidden before first roll."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Before roll
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # No dice toggle actions should be visible
        assert "toggle_die_0" not in visible_ids
        assert "toggle_die_1" not in visible_ids
        assert "toggle_die_2" not in visible_ids
        assert "toggle_die_3" not in visible_ids
        assert "toggle_die_4" not in visible_ids
        assert "toggle_die_5" not in visible_ids

    def test_dice_toggle_index_extraction(self):
        """Test that die index is correctly extracted from action_id."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()
        original_values = player.dice.values.copy()

        # Keep die at index 2 using toggle_die_2 action
        game.execute_action(player, "toggle_die_2")

        # Die at index 2 should be kept
        assert 2 in player.dice.kept
        # Value should be preserved
        assert player.dice.values[2] == original_values[2]

    def test_backward_compatibility_without_action_id(self):
        """Test that methods without action_id parameter still work."""
        # This test verifies backward compatibility
        # Threes and Midnight both have _is_dice_toggle_enabled that doesn't use action_id
        # but the mixin delegate methods do use it

        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()
        player.dice.roll()

        # These should work without errors
        visible = game.get_all_visible_actions(player)
        turn_set = game.get_action_set(player, "turn")
        enabled = turn_set.resolve_actions(game, player) if turn_set else []

        assert len(visible) > 0
        assert len(enabled) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
