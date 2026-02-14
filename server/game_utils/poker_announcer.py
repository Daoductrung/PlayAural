"""Shared announcement logic for poker pot results."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ..messages.localization import Localization
from .cards import read_cards
from .poker_evaluator import describe_hand

if TYPE_CHECKING:
    from ..games.base import Game, Player


def announce_pot_winners(
    game: Game,
    pot_index: int,
    pot_amount: int,
    winners: list[Player],
    best_score: tuple[int, tuple[int, ...]]
) -> None:
    """Announce the winners of a pot to all players in the game."""
    # Play win sound
    game.play_sound(random.choice(["game_blackjack/win1.ogg", "game_blackjack/win2.ogg", "game_blackjack/win3.ogg"]))

    if len(winners) == 1:
        winner = winners[0]
        # Notify each player
        for p in game.players:
            user = game.get_user(p)
            if not user:
                continue
            
            # We assume winner has a .hand attribute (HoldemPlayer, FiveCardDrawPlayer)
            hand = getattr(winner, "hand", [])
            cards_str = read_cards(hand, user.locale)
            desc_str = describe_hand(best_score, user.locale)
            
            if pot_index == 0:
                user.speak_l(
                    "poker-player-wins-pot-hand",
                    player=winner.name,
                    amount=pot_amount,
                    cards=cards_str,
                    hand=desc_str,
                )
            else:
                 user.speak_l(
                    "poker-player-wins-side-pot-hand",
                    player=winner.name,
                    amount=pot_amount,
                    index=pot_index,
                    cards=cards_str,
                    hand=desc_str,
                )
    else:
        names = ", ".join(w.name for w in winners)
        for p in game.players:
            user = game.get_user(p)
            if not user:
                continue
                
            desc_str = describe_hand(best_score, user.locale)
            
            if pot_index == 0:
                user.speak_l(
                    "poker-players-split-pot",
                    buffer="game",
                    players=names,
                    amount=pot_amount,
                    hand=desc_str
                )
            else:
                user.speak_l(
                    "poker-players-split-side-pot",
                    players=names,
                    amount=pot_amount,
                    index=pot_index,
                    hand=desc_str,
                )
