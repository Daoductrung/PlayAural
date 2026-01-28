"""Mixin providing action set management for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player

from .actions import Action, ActionSet, ResolvedAction


class ActionSetSystemMixin:
    """Mixin providing action set management (get, add, remove, find, resolve).

    Expects on the Game class:
        - self.player_action_sets: dict[str, list[ActionSet]]
    """

    def get_action_sets(self, player: "Player") -> list[ActionSet]:
        """Get ordered list of action sets for a player."""
        return self.player_action_sets.get(player.id, [])

    def get_action_set(self, player: "Player", name: str) -> ActionSet | None:
        """Get a specific action set by name for a player."""
        for action_set in self.get_action_sets(player):
            if action_set.name == name:
                return action_set
        return None

    def add_action_set(self, player: "Player", action_set: ActionSet) -> None:
        """Add an action set to a player (appended to end of list)."""
        if player.id not in self.player_action_sets:
            self.player_action_sets[player.id] = []
        self.player_action_sets[player.id].append(action_set)

    def remove_action_set(self, player: "Player", name: str) -> None:
        """Remove an action set from a player by name."""
        if player.id in self.player_action_sets:
            self.player_action_sets[player.id] = [
                s for s in self.player_action_sets[player.id] if s.name != name
            ]

    def find_action(self, player: "Player", action_id: str) -> Action | None:
        """Find an action by ID across all of a player's action sets."""
        for action_set in self.get_action_sets(player):
            action = action_set.get_action(action_id)
            if action:
                return action
        return None

    def resolve_action(self, player: "Player", action: Action) -> ResolvedAction:
        """Resolve a single action's state for a player."""
        # Find the action set containing this action
        for action_set in self.get_action_sets(player):
            if action_set.get_action(action.id):
                return action_set.resolve_action(self, player, action)
        # Fallback - resolve with defaults
        return ResolvedAction(
            action=action,
            label=action.label,
            enabled=True,
            disabled_reason=None,
            visible=True,
        )

    def get_all_visible_actions(self, player: "Player") -> list[ResolvedAction]:
        """Get all visible (enabled and not hidden) actions for a player, in order."""
        result = []
        for action_set in self.get_action_sets(player):
            result.extend(action_set.get_visible_actions(self, player))
        return result

    def get_all_enabled_actions(self, player: "Player") -> list[ResolvedAction]:
        """Get all enabled actions for a player (for the actions menu), in order."""
        result = []
        for action_set in self.get_action_sets(player):
            result.extend(action_set.get_enabled_actions(self, player))
        return result
