"""TwentyOne bot decision logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import TwentyOneGame, TwentyOnePlayer


def bot_think(game: "TwentyOneGame", player: "TwentyOnePlayer") -> str | None:
    """Return a bot action for the current TwentyOne turn."""
    if game.phase != "turns" or game.current_player != player:
        return None

    opponent = game._opponent_of(player)
    if not opponent:
        return "stand"

    target = game._current_target()
    total = game._hand_total(player)
    estimated_opp_total = game._bot_estimate_opponent_total(player, opponent)

    if not game._modifiers_locked_for(player) and player.modifiers:
        if game._bot_choose_modifier_to_play(player):
            return "play_modifier"

    # Draw-lock effects make hit impossible; avoid infinite bot retry loops.
    if game._draws_locked_for(player):
        return "stand"

    return game._bot_choose_hit_or_stand(opponent, total, estimated_opp_total, target)
