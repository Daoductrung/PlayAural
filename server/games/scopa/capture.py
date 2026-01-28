"""
Capture logic for Scopa game.

Handles finding valid capture combinations and selecting the best one.
"""

from ...game_utils.cards import Card, card_name


def find_subsets_with_sum(cards: list[Card], target: int) -> list[list[Card]]:
    """Find all subsets of cards that sum to target."""
    if target <= 0:
        return []

    results: list[list[Card]] = []

    def backtrack(start: int, current: list[Card], current_sum: int):
        if current_sum == target:
            results.append(list(current))
            return
        if current_sum > target:
            return
        for i in range(start, len(cards)):
            current.append(cards[i])
            backtrack(i + 1, current, current_sum + cards[i].rank)
            current.pop()

    backtrack(0, [], 0)
    return results


def find_captures(
    table_cards: list[Card], card_value: int, escoba: bool = False
) -> list[list[Card]]:
    """
    Find all valid capture combinations for a card value.

    Args:
        table_cards: Cards currently on the table.
        card_value: The rank of the card being played.
        escoba: If True, use escoba rules (sum to 15).

    Returns:
        List of possible capture combinations (each is a list of cards).

    For standard scopa: rank match first, then sum combinations.
    For escoba: find combinations that sum to 15 (including played card).
    """
    if escoba:
        # Escoba: find subsets that sum to 15 - card_value
        target = 15 - card_value
        return find_subsets_with_sum(table_cards, target)
    else:
        # Standard scopa: rank match first
        rank_matches = [c for c in table_cards if c.rank == card_value]
        if rank_matches:
            # Return each single match as a separate option
            return [[c] for c in rank_matches]
        # No rank match, find sum combinations
        return find_subsets_with_sum(table_cards, card_value)


def select_best_capture(captures: list[list[Card]]) -> list[Card]:
    """Select the best capture (most cards)."""
    if not captures:
        return []
    return max(captures, key=len)


from ...messages.localization import Localization

def get_capture_hint(
    table_cards: list[Card], card: Card, escoba: bool = False, locale: str = "en"
) -> str:
    """
    Get a hint about what cards would be captured.

    Args:
        table_cards: Cards currently on the table.
        card: The card being considered for play.
        escoba: If True, use escoba rules.
        locale: Locale for card names.

    Returns:
        Hint string like " -> 7 of Coins" or " -> 3 cards", or empty string.
    """
    captures = find_captures(table_cards, card.rank, escoba)
    if not captures:
        return ""
    best = select_best_capture(captures)
    if len(best) == 1:
        card_str = card_name(best[0], locale)
        return Localization.get(locale, "scopa-hint-match", card=card_str)
    else:
        return Localization.get(locale, "scopa-hint-multi", count=len(best))
