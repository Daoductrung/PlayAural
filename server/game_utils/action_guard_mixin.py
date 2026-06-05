"""Shared helpers for common action guard logic."""

from __future__ import annotations

from .actions import Visibility


class ActionGuardMixin:
    """Provides reusable guard logic for turn actions."""

    def guard_game_active(self) -> str | None:
        """Return standard error code if game is not currently playing."""
        if getattr(self, "status", None) != "playing":
            return "action-not-playing"
        return None

    def guard_turn_action_enabled(
        self,
        player,
        *,
        allow_spectators: bool = False,
        require_current_player: bool = True,
    ) -> str | None:
        """Common rules for checking if a player can perform a turn action."""
        error = self.guard_game_active()
        if error:
            return error
        if not allow_spectators and getattr(player, "is_spectator", False):
            return "action-spectator"
        if require_current_player and getattr(self, "current_player", None) != player:
            return "action-not-your-turn"
        return None

    def turn_action_visibility(
        self,
        player,
        *,
        allow_spectators: bool = False,
        require_current_player: bool = True,
        extra_condition: bool = True,
    ) -> Visibility:
        """Return Visibility for a turn action with optional extra conditions."""
        error = self.guard_turn_action_enabled(
            player,
            allow_spectators=allow_spectators,
            require_current_player=require_current_player,
        )
        if error is None and extra_condition:
            return Visibility.VISIBLE
        return Visibility.HIDDEN


__all__ = ["ActionGuardMixin"]
