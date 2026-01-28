"""
Bot AI for Scopa game.

Handles bot decision making for card play.
"""

from typing import TYPE_CHECKING

from ...game_utils.cards import Card
from .capture import find_captures, select_best_capture

if TYPE_CHECKING:
    from .game import ScopaGame, ScopaPlayer


def bot_think(game: "ScopaGame", player: "ScopaPlayer") -> str | None:
    """
    Bot AI decision making.

    Args:
        game: The Scopa game instance.
        player: The bot player making a decision.

    Returns:
        Action ID to execute, or None if no action available.
    """
    if not player.hand:
        return None

    # Evaluate each card and pick the best
    best_card = None
    best_score = float("-inf")

    for card in player.hand:
        score = evaluate_card(game, card, player)
        if score > best_score:
            best_score = score
            best_card = card

    if best_card:
        return f"play_card_{best_card.id}"
    return None


def evaluate_card(game: "ScopaGame", card: Card, player: "ScopaPlayer") -> float:
    """
    Evaluate a card for bot play.

    Args:
        game: The Scopa game instance.
        card: The card to evaluate.
        player: The bot player.

    Returns:
        Score for this card (higher is better).
    """
    score = 0.0
    inverse = game.options.inverse_scopa
    escoba = game.options.escoba

    captures = find_captures(game.table_cards, card.rank, escoba)

    if not captures:
        # No capture available
        if inverse:
            score = 10 - (card.rank * 0.5)  # Prefer playing low cards
        else:
            score = -5 + (card.rank * 0.5)  # Prefer playing high cards
    else:
        best_capture = select_best_capture(captures)
        num_captured = len(best_capture)

        if inverse:
            # Inverse: avoid capturing
            score = -num_captured * 10
        else:
            # Normal: prefer capturing
            score = num_captured * 10

        # Check for scopa
        is_scopa = num_captured == len(game.table_cards) and len(game.table_cards) > 0
        if is_scopa:
            score += 100 if not inverse else -100

        # Evaluate captured card values
        for c in best_capture:
            if c.suit == 1:  # Diamond
                score += 5 if not inverse else -5
            if c.rank == 7 and c.suit == 1:  # 7 of diamonds
                score += 20 if not inverse else -20
            if c.rank == 7:  # Any 7
                score += 3 if not inverse else -3
            if c.rank in (1, 6):  # Primiera cards
                score += 2 if not inverse else -2

    return score
