from __future__ import annotations

from typing import TYPE_CHECKING
import random

from ...game_utils.cards import Card

if TYPE_CHECKING:
    from .game import CrazyEightsGame, CrazyEightsPlayer


def choose_suit(game: "CrazyEightsGame", player: "CrazyEightsPlayer") -> int:
    suit_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for card in player.hand:
        if card.rank == 8:
            continue
        if card.suit in suit_counts:
            suit_counts[card.suit] += 1
    best = max(suit_counts.items(), key=lambda item: item[1])[0]
    return best


def _card_priority(game: "CrazyEightsGame", card: Card) -> int:
    if card.rank == 13:  # Draw Two (King)
        return 5
    if card.rank == 12:  # Skip (Queen)
        return 4
    if card.rank == 11:  # Reverse (Jack)
        return 3
    if card.rank == 8:  # Wild
        return 1
    return 2


def choose_playable_card_id(
    game: "CrazyEightsGame", player: "CrazyEightsPlayer"
) -> int | None:
    playable = game.get_playable_indices(player)
    if not playable:
        return None

    # Prefer action cards when not low on cards; save wilds when possible.
    hand_size = len(player.hand)
    scored = []
    for idx in playable:
        card = player.hand[idx]
        base = _card_priority(game, card)
        if hand_size <= 2:
            base += 2
        if card.rank == 8 and hand_size > 3:
            base -= 1
        scored.append((base, random.random(), card.id))

    scored.sort(reverse=True)
    return scored[0][2]


def bot_think(game: "CrazyEightsGame", player: "CrazyEightsPlayer") -> str | None:
    if game.awaiting_wild_suit and game.current_player == player:
        suit = choose_suit(game, player)
        return game.suit_action_id(suit)

    if game.turn_has_drawn:
        playable = game.get_playable_indices(player)
        if playable:
            # 80% chance to play, otherwise pass
            if random.random() < 0.8:
                card_id = choose_playable_card_id(game, player)
                if card_id is not None:
                    return f"play_card_{card_id}"
        return "pass"

    playable = game.get_playable_indices(player)
    if playable:
        card_id = choose_playable_card_id(game, player)
        if card_id is not None:
            return f"play_card_{card_id}"
    if game._can_draw(player):
        return "draw"
    return "pass"
