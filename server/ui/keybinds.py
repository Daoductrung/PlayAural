"""Keybind definitions for game input handling."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Game, Player


class KeybindScope(Enum):
    """Scope in which a keybind can be performed."""

    GLOBAL = auto()  # Client-managed (not used server-side)
    TABLE = auto()  # Table/game-specific


class KeybindState(Enum):
    """When a keybind should be enabled."""

    NEVER = auto()  # Completely unavailable
    IDLE = auto()  # Only when game is not active (lobby/waiting)
    ACTIVE = auto()  # Only when game is active (playing)
    ALWAYS = auto()  # Always available


@dataclass
class Keybind:
    """
    A keybind definition for triggering game actions.

    Keybinds act as hotkeys to trigger actions that can typically
    be accessed from a menu. A keybind references one or more actions
    by their IDs.

    Attributes:
        name: Human-readable name for the keybind (e.g., "Roll dice")
        default_key: The default key combination (e.g., "space", "shift+b")
        actions: List of action IDs this keybind triggers
        requires_focus: If True, must be focused on a valid action menu item
        state: When this keybind is enabled (NEVER, IDLE, ACTIVE, ALWAYS)
        scope: Where the keybind applies (GLOBAL or TABLE)
        players: List of player names who can use (empty = all players)
        include_spectators: Whether spectators can use this keybind
    """

    name: str
    default_key: str
    actions: list[str]
    requires_focus: bool = False
    state: KeybindState = KeybindState.ALWAYS
    scope: KeybindScope = KeybindScope.TABLE
    players: list[str] = field(default_factory=list)
    include_spectators: bool = False

    def is_state_active(self, game: "Game") -> bool:
        """Check if keybind state allows activation based on game status."""
        if self.state == KeybindState.NEVER:
            return False
        if self.state == KeybindState.ALWAYS:
            return True
        if self.state == KeybindState.IDLE:
            return game.status != "playing"
        if self.state == KeybindState.ACTIVE:
            return game.status == "playing"
        return False

    def can_player_use(
        self, game: "Game", player: "Player", is_spectator: bool = False
    ) -> bool:
        """Check if a specific player can use this keybind."""
        # Check state first
        if not self.is_state_active(game):
            return False

        # Check spectator permission
        if is_spectator and not self.include_spectators:
            return False

        # Check player list (empty means all players)
        if self.players and player.name not in self.players:
            return False

        return True
