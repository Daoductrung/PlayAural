"""Mixin providing turn management functionality for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from ..users.base import User


class TurnManagementMixin:
    """Mixin providing turn order management and advancement.

    Expects on the Game class:
        - self.turn_player_ids: list[str]
        - self.turn_index: int
        - self.turn_direction: int
        - self.turn_skip_count: int
        - self.players: list[Player]
        - self.get_player_by_id(player_id) -> Player | None
        - self.get_user(player) -> User | None
        - self.broadcast_l(message_id, **kwargs)
        - self.refresh_menus()
    """

    @property
    def current_player(self) -> "Player | None":
        """Get the current player based on turn_index and turn_player_ids."""
        if not self.turn_player_ids:
            return None
        index = self.turn_index % len(self.turn_player_ids)
        player_id = self.turn_player_ids[index]
        return self.get_player_by_id(player_id)

    @current_player.setter
    def current_player(self, player: "Player | None") -> None:
        """Set the current player by updating turn_index."""
        if player is None or player.id not in self.turn_player_ids:
            return
        self.turn_index = self.turn_player_ids.index(player.id)

    def set_turn_players(self, players: list["Player"], reset_index: bool = True) -> None:
        """Set the list of players in turn order.

        Args:
            players: List of players to include in turn rotation.
            reset_index: If True, reset turn_index to 0.
        """
        self.turn_player_ids = [p.id for p in players]
        if reset_index:
            self.turn_index = 0

    def advance_turn(self, announce: bool = True) -> "Player | None":
        """Advance to the next player's turn (respects turn_direction and skips).

        Args:
            announce: If True, announce the turn and play sound.

        Returns:
            The new current player.
        """
        if not self.turn_player_ids:
            return None

        # Handle skips first
        skipped_players: list["Player"] = []
        while self.turn_skip_count > 0:
            self.turn_skip_count -= 1
            self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
            skipped = self.current_player
            if skipped:
                skipped_players.append(skipped)

        # Announce skipped players
        for skipped in skipped_players:
            self.on_player_skipped(skipped)

        # Normal advance
        self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
        if announce:
            self.announce_turn()
        self.refresh_menus()
        return self.current_player

    def skip_next_players(self, count: int = 1) -> None:
        """Queue players to be skipped on next turn advance.

        Args:
            count: Number of players to skip (default 1).
        """
        self.turn_skip_count += count

    def on_player_skipped(self, player: "Player") -> None:
        """Called when a player is skipped. Override to customize announcement.

        Args:
            player: The player who was skipped.
        """
        self.broadcast_l("game-player-skipped", buffer="game", player=player.name)

    def reverse_turn_direction(self) -> None:
        """Reverse the turn direction (forward <-> backward)."""
        self.turn_direction *= -1

    def reset_turn_order(self, announce: bool = False) -> None:
        """Reset to the first player in turn order.

        Args:
            announce: If True, announce the turn and play sound.
        """
        self.turn_index = 0
        self.turn_direction = 1  # Reset direction to forward
        self.turn_skip_count = 0  # Clear any pending skips
        if announce:
            self.announce_turn()

    turn_announcement_personal_key = "game-turn-start-you"
    turn_announcement_others_key = "game-turn-start-player"
    no_turn_announcement_key = "game-no-turn"

    def _is_turn_listener(self, listener: "Player", current: "Player") -> bool:
        """Return whether the listener is the player whose turn is active."""
        return listener is current or listener.id == current.id

    def speak_turn_l(
        self,
        listener: "Player",
        current: "Player | None" = None,
        *,
        buffer: str = "game",
    ) -> None:
        """Speak the current turn to one listener with the correct perspective."""
        user = self.get_user(listener)
        if not user:
            return

        turn_player = current if current is not None else self.current_player
        if not turn_player:
            user.speak_l(self.no_turn_announcement_key, buffer=buffer)
            return

        if self._is_turn_listener(listener, turn_player):
            user.speak_l(self.turn_announcement_personal_key, buffer=buffer)
        else:
            user.speak_l(
                self.turn_announcement_others_key,
                buffer=buffer,
                player=turn_player.name,
            )

    def broadcast_turn_l(
        self,
        current: "Player | None" = None,
        *,
        buffer: str = "game",
    ) -> None:
        """Broadcast the current turn with first-person text for the actor."""
        turn_player = current if current is not None else self.current_player
        for listener in self.players:
            self.speak_turn_l(listener, turn_player, buffer=buffer)

    def announce_turn(self, turn_sound: str = "turn.ogg") -> None:
        """Announce the current player's turn with sound and perspective-aware text."""
        player = self.current_player
        if not player:
            return

        # Play turn sound to the current player (if they have it enabled)
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound(turn_sound)

        self.broadcast_turn_l(player, buffer="game")

    @property
    def turn_players(self) -> list["Player"]:
        """Get the list of players in turn order."""
        return [
            p
            for player_id in self.turn_player_ids
            if (p := self.get_player_by_id(player_id)) is not None
        ]
