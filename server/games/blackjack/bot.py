"""Blackjack bot decision logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import BlackjackGame, BlackjackPlayer


def bot_think(game: "BlackjackGame", player: "BlackjackPlayer") -> str | None:
    """Return a basic blackjack bot action for the current player."""
    if game.current_player != player:
        return None

    if game.phase == "insurance":
        if game._can_take_even_money(player):
            return "even_money"
        if game._can_take_insurance(player):
            return "decline_insurance"
        if game._player_needs_insurance_decision(player):
            return "decline_insurance"
        return None

    if game._current_hand_done(player):
        return None

    hand = game._current_hand(player)
    total, is_soft = game.hand_value(hand)
    if total >= 21:
        return "stand"

    dealer_up = game.dealer_hand[0] if game.dealer_hand else None
    dealer_value = game.card_blackjack_value(dealer_up) if dealer_up else 10

    if game._can_surrender(player):
        if not is_soft and total == 16 and dealer_value in (9, 10, 11):
            return "surrender"
        if not is_soft and total == 15 and dealer_value == 10:
            return "surrender"

    if game._can_split(player):
        split_value = game.card_blackjack_value(hand[0])
        if split_value in (8, 11):
            return "split"
        if split_value == 9 and dealer_value not in (7, 10, 11):
            return "split"

    if game._can_double_down(player):
        if total == 11:
            return "double_down"
        if total == 10 and dealer_value <= 9:
            return "double_down"
        if total == 9 and 3 <= dealer_value <= 6:
            return "double_down"

    if total <= 11:
        return "hit"
    if is_soft and total <= 17:
        return "hit"
    if not is_soft and total >= 17:
        return "stand"
    if dealer_value >= 7 and total <= 16:
        return "hit"
    if dealer_value <= 6 and total <= 11:
        return "hit"
    return "stand"
