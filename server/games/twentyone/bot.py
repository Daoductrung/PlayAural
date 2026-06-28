"""TwentyOne bot decision logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import TwentyOneGame, TwentyOnePlayer


def bot_think(game: "TwentyOneGame", player: "TwentyOnePlayer") -> str | None:
    """Return a bot action for the current TwentyOne turn."""
    if game.phase != "turns" or game.current_player != player:
        return None

    opponents = game._opponents_of(player)
    if not opponents:
        return "stand"

    if not game._modifiers_locked_for(player) and player.modifiers:
        if game._bot_choose_modifier_to_play(player):
            return "play_modifier"

    # Draw-lock effects and empty decks make hit impossible; avoid infinite bot retry loops.
    if game._draws_locked_for(player) or not game.deck or game.deck.is_empty():
        return "stand"

    return game._bot_choose_hit_or_stand(player)
