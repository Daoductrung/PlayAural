from typing import TYPE_CHECKING, List
from itertools import combinations
import random

from ...game_utils.cards import Card
from .evaluator import Combo, evaluate_combo, sort_cards

if TYPE_CHECKING:
    from .game import PusoyDosGame, PusoyDosPlayer

def get_all_valid_combos(hand: List[Card]) -> List[Combo]:
    combos = []
    # Singles
    for c in hand:
        combo = evaluate_combo([c])
        if combo:
            combos.append(combo)

    # Pairs
    for combo_cards in combinations(hand, 2):
        combo = evaluate_combo(list(combo_cards))
        if combo:
            combos.append(combo)

    # Three of a kind
    for combo_cards in combinations(hand, 3):
        combo = evaluate_combo(list(combo_cards))
        if combo:
            combos.append(combo)

    # 5-card combos
    if len(hand) >= 5:
        # Optimization: Don't evaluate all combinations if not necessary, or do it smartly.
        # But for 13 cards, comb(13, 5) is 1287, which is very fast in Python.
        for combo_cards in combinations(hand, 5):
            combo = evaluate_combo(list(combo_cards))
            if combo:
                combos.append(combo)

    return combos

def bot_think(game: "PusoyDosGame", player: "PusoyDosPlayer") -> List[int]:
    """
    Returns a list of card IDs to play, or an empty list to pass.
    """
    hand = sort_cards(player.hand)

    current_combo = game.current_combo
    is_first_turn = game.is_first_turn

    # Must start with 3 of Clubs
    has_three_of_clubs = any(c.rank == 3 and c.suit == 2 for c in hand)
    if is_first_turn and has_three_of_clubs:
        # Optimization: only check combos with the 3 of clubs
        all_combos = get_all_valid_combos(hand)
        valid_starts = [c for c in all_combos if any(card.rank == 3 and card.suit == 2 for card in c.cards)]
        if valid_starts:
            valid_starts.sort(key=lambda c: (-len(c.cards), c.tier, c.rank_value, c.suit_value))
            return [c.id for c in valid_starts[0].cards]

    all_combos = get_all_valid_combos(hand)

    if current_combo is None:
        # We have a free play.
        if all_combos:
            all_combos.sort(key=lambda c: (-len(c.cards), c.tier, c.rank_value, c.suit_value))
            return [c.id for c in all_combos[0].cards]
        return []

    # We need to beat the current combo
    valid_plays = [c for c in all_combos if len(c.cards) == len(current_combo.cards) and c.beats(current_combo)]

    if not valid_plays:
        return []

    # Sort to play the weakest valid combo to save good cards
    valid_plays.sort(key=lambda c: (c.tier, c.rank_value, c.suit_value))

    return [c.id for c in valid_plays[0].cards]
