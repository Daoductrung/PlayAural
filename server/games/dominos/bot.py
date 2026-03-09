"""Bot AI logic for Dominos."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import DominosGame, DominosPlayer

def bot_think(game: "DominosGame", player: "DominosPlayer") -> str | None:
    """
    Determine the best action for a bot in Dominos.
    Returns the action ID string to execute.
    """
    # Find playable tiles
    playable = []

    if game.left_end == -1 and game.right_end == -1:
        playable = player.hand.copy()
    else:
        for tile in player.hand:
            if tile.matches(game.left_end) or tile.matches(game.right_end):
                playable.append(tile)

    if playable:
        # Prefer playing higher value tiles to get rid of pips
        playable.sort(key=lambda t: t.pips, reverse=True)
        # Select the highest value tile
        best_tile = playable[0]
        return f"play_tile_{best_tile.id}"

    # Cannot play, must draw or pass
    if game.options.game_mode != "block" and game.boneyard:
        return "draw_tile"

    return "pass_turn"
