"""Mixin providing communication helpers for games."""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..games.base import Game, Player
    from ..users.base import User

from ..messages.localization import Localization


class GameCommunicationMixin:
    """Mixin providing message broadcasting and localization helpers.

    Expects on the Game class:
        - self.players: list[Player]
        - self.get_user(player) -> User | None
    """

    def broadcast(
        self, text: str, buffer: str = "misc", exclude: "Player | None" = None
    ) -> None:
        """Send a message to all players, optionally excluding one."""
        for player in self.players:
            if player is exclude:
                continue
            user = self.get_user(player)
            if user:
                user.speak(text, buffer)

    def broadcast_l(
        self,
        message_id: str,
        buffer: str = "misc",
        exclude: "Player | None" = None,
        **kwargs,
    ) -> None:
        """Send a localized message to all players (each in their own locale)."""
        for player in self.players:
            if player is exclude:
                continue
            user = self.get_user(player)
            if user:
                user.speak_l(message_id, buffer, **kwargs)

    def broadcast_personal_l(
        self,
        player: "Player",
        personal_message_id: str,
        others_message_id: str,
        buffer: str = "misc",
        **kwargs,
    ) -> None:
        """
        Send a personalized message to one player and a different message to everyone else.

        The player receives personal_message_id, while all other players receive
        others_message_id with an additional player=player.name argument.

        Args:
            player: The player who gets the personal message.
            personal_message_id: Message ID for the player (e.g., "you-rolled").
            others_message_id: Message ID for everyone else (e.g., "player-rolled").
            buffer: Audio buffer for speech.
            **kwargs: Additional arguments passed to all speak_l calls.
        """
        user = self.get_user(player)
        if user:
            user.speak_l(personal_message_id, buffer, **kwargs)

        for p in self.players:
            if p is player:
                continue
            u = self.get_user(p)
            if u:
                u.speak_l(others_message_id, buffer, player=player.name, **kwargs)

    def label_l(self, message_id: str) -> Callable[["Game", "Player"], str]:
        """
        Create a localized label callable for use in action definitions.

        Usage:
            self.define_action("roll", label=self.label_l("pig-roll"), ...)
        """

        def get_label(game: "Game", player: "Player") -> str:
            user = game.get_user(player)
            locale = user.locale if user else "en"
            return Localization.get(locale, message_id)

        return get_label
