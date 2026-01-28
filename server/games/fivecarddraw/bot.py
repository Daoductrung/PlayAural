"""
Bot AI for Five Card Draw.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...game_utils.poker_evaluator import best_hand

if TYPE_CHECKING:
    from .game import FiveCardDrawGame, FiveCardDrawPlayer


def bot_think(game: "FiveCardDrawGame", player: "FiveCardDrawPlayer") -> str | None:
    if game.current_player != player:
        return None
    if game.phase == "draw":
        _choose_discards(game, player)
        return "draw_cards"
    if not game.betting:
        return None
    return _decide_bet(game, player)


def _choose_discards(game: "FiveCardDrawGame", player: "FiveCardDrawPlayer") -> None:
    if len(player.hand) >= 5:
        score, _ = best_hand(player.hand)
        category = score[0]
    else:
        category = 0
    ranks = [card.rank for card in player.hand]
    counts: dict[int, int] = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1
    keep_ranks: set[int] = set()
    if category >= 4:  # straight or better
        keep_ranks = set(ranks)
    elif category == 3:  # three of a kind
        keep_ranks = {r for r, c in counts.items() if c == 3}
    elif category == 2:  # two pair
        keep_ranks = {r for r, c in counts.items() if c == 2}
    elif category == 1:  # one pair
        keep_ranks = {r for r, c in counts.items() if c == 2}
    discard_indices = [i for i, card in enumerate(player.hand) if card.rank not in keep_ranks]
    max_discards = 4 if any(card.rank == 1 for card in player.hand) else 3
    if len(discard_indices) > max_discards:
        discard_indices = discard_indices[:max_discards]
    player.to_discard = set(discard_indices)


def _decide_bet(game: "FiveCardDrawGame", player: "FiveCardDrawPlayer") -> str | None:
    to_call = game.betting.amount_to_call(player.id)
    if len(player.hand) >= 5:
        score, _ = best_hand(player.hand)
        category = score[0]
    else:
        category = 0
    min_raise = max(game.betting.last_raise_size, 1)
    can_raise = game.betting.can_raise() and (to_call + min_raise) <= player.chips
    if to_call == 0:
        if can_raise and category >= 1:
            return "raise"
        return "call"
    if to_call >= player.chips:
        return "call"
    if category >= 2 and to_call <= max(1, player.chips // 6):
        return "call"
    if category >= 1 and to_call <= max(1, player.chips // 12):
        return "call"
    if to_call <= max(1, player.chips // 25):
        return "call"
    return "fold"
