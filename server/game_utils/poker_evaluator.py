"""
Poker hand evaluator for standard 52-card decks.

Provides helpers for scoring a 5-card hand and selecting the best 5-card hand
from a larger set (e.g., 7 cards in Hold'em).
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable

from .cards import Card, SUIT_NONE, RANK_KEYS
from ..messages.localization import Localization

# Hand category ranks (higher is better)
HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8


def best_hand(cards: list[Card]) -> tuple[tuple[int, tuple[int, ...]], list[Card]]:
    """Return the best 5-card hand score and the chosen 5 cards."""
    if len(cards) < 5:
        raise ValueError("best_hand requires at least 5 cards")

    best_score: tuple[int, tuple[int, ...]] | None = None
    best_five: list[Card] | None = None

    for hand in combinations(cards, 5):
        score = score_5_cards(list(hand))
        if best_score is None or score > best_score:
            best_score = score
            best_five = list(hand)

    # best_score and best_five are always set because len(cards) >= 5
    return best_score, best_five  # type: ignore[return-value]


def score_5_cards(cards: list[Card]) -> tuple[int, tuple[int, ...]]:
    """Score exactly 5 cards. Higher tuples compare as better hands."""
    if len(cards) != 5:
        raise ValueError("score_5_cards requires exactly 5 cards")

    ranks = [_rank_value(card.rank) for card in cards]
    suits = [card.suit for card in cards]

    rank_counts = Counter(ranks)
    counts_sorted = sorted(
        ((count, rank) for rank, count in rank_counts.items()),
        key=lambda x: (x[0], x[1]),
        reverse=True,
    )

    is_flush = _is_flush(suits)
    is_straight, straight_high = _is_straight(ranks)

    if is_straight and is_flush:
        return (STRAIGHT_FLUSH, (straight_high,))

    if counts_sorted[0][0] == 4:
        quad_rank = counts_sorted[0][1]
        kicker = _highest_of_excluding(ranks, {quad_rank})[0]
        return (FOUR_OF_A_KIND, (quad_rank, kicker))

    if counts_sorted[0][0] == 3 and counts_sorted[1][0] == 2:
        trip_rank = counts_sorted[0][1]
        pair_rank = counts_sorted[1][1]
        return (FULL_HOUSE, (trip_rank, pair_rank))

    if is_flush:
        return (FLUSH, tuple(sorted(ranks, reverse=True)))

    if is_straight:
        return (STRAIGHT, (straight_high,))

    if counts_sorted[0][0] == 3:
        trip_rank = counts_sorted[0][1]
        kickers = _highest_of_excluding(ranks, {trip_rank})
        return (THREE_OF_A_KIND, (trip_rank, *kickers))

    if counts_sorted[0][0] == 2 and counts_sorted[1][0] == 2:
        high_pair = max(counts_sorted[0][1], counts_sorted[1][1])
        low_pair = min(counts_sorted[0][1], counts_sorted[1][1])
        kicker = _highest_of_excluding(ranks, {high_pair, low_pair})[0]
        return (TWO_PAIR, (high_pair, low_pair, kicker))

    if counts_sorted[0][0] == 2:
        pair_rank = counts_sorted[0][1]
        kickers = _highest_of_excluding(ranks, {pair_rank})
        return (ONE_PAIR, (pair_rank, *kickers))

    return (HIGH_CARD, tuple(sorted(ranks, reverse=True)))


def describe_hand(score: tuple[int, tuple[int, ...]], locale: str = "en") -> str:
    """Return a human-friendly description for a scored hand."""
    category, tiebreakers = score

    if category == HIGH_CARD:
        high = _cap(_rank_name(tiebreakers[0], locale))
        kickers = _rank_list(tiebreakers[1:], locale, cap=True)
        return Localization.get(
            locale, "poker-high-card-with", high=high, rest=kickers
        )

    if category == ONE_PAIR:
        pair = _cap(_rank_name_plural(tiebreakers[0], locale))
        kickers = _rank_list(tiebreakers[1:], locale, cap=True)
        return Localization.get(
            locale, "poker-pair-with", pair=pair, rest=kickers
        )

    if category == TWO_PAIR:
        high_pair = _cap(_rank_name_plural(tiebreakers[0], locale))
        low_pair = _cap(_rank_name_plural(tiebreakers[1], locale))
        kicker = _cap(_rank_name(tiebreakers[2], locale))
        return Localization.get(
            locale,
            "poker-two-pair-with",
            high=high_pair,
            low=low_pair,
            kicker=kicker,
        )

    if category == THREE_OF_A_KIND:
        trips = _cap(_rank_name_plural(tiebreakers[0], locale))
        kickers = _rank_list(tiebreakers[1:], locale, cap=True)
        return Localization.get(
            locale, "poker-trips-with", trips=trips, rest=kickers
        )

    if category == STRAIGHT:
        high = _cap(_rank_name(tiebreakers[0], locale))
        return Localization.get(locale, "poker-straight-high", high=high)

    if category == FLUSH:
        high = _cap(_rank_name(tiebreakers[0], locale))
        kickers = _rank_list(tiebreakers[1:], locale, cap=True)
        return Localization.get(
            locale, "poker-flush-high-with", high=high, rest=kickers
        )

    if category == FULL_HOUSE:
        trips = _cap(_rank_name_plural(tiebreakers[0], locale))
        pair = _cap(_rank_name_plural(tiebreakers[1], locale))
        return Localization.get(
            locale, "poker-full-house", trips=trips, pair=pair
        )

    if category == FOUR_OF_A_KIND:
        quads = _cap(_rank_name_plural(tiebreakers[0], locale))
        kicker = _cap(_rank_name(tiebreakers[1], locale))
        return Localization.get(
            locale, "poker-quads-with", quads=quads, kicker=kicker
        )

    if category == STRAIGHT_FLUSH:
        high = _cap(_rank_name(tiebreakers[0], locale))
        return Localization.get(
            locale, "poker-straight-flush-high", high=high
        )

    return Localization.get(locale, "poker-unknown-hand")


def describe_best_hand(cards: list[Card], locale: str = "en") -> tuple[str, list[Card]]:
    """Return the best hand description and the chosen 5 cards."""
    score, best = best_hand(cards)
    return describe_hand(score, locale), best


def describe_partial_hand(cards: list[Card], locale: str = "en") -> str:
    """Describe a partial hand without inventing missing cards."""
    if len(cards) >= 5:
        score, _ = best_hand(cards)
        return describe_hand(score, locale)
    ranks = [_rank_value(card.rank) for card in cards]
    counts = Counter(ranks)
    by_count = sorted(((c, r) for r, c in counts.items()), reverse=True)
    if not by_count:
        return Localization.get(locale, "poker-unknown-hand")
    if by_count[0][0] == 4:
        quads = _cap(_rank_name_plural(by_count[0][1], locale))
        return Localization.get(locale, "poker-quads", quads=quads)
    if by_count[0][0] == 3:
        trips = _cap(_rank_name_plural(by_count[0][1], locale))
        kickers = _rank_list([r for r in ranks if r != by_count[0][1]], locale, cap=True)
        if kickers:
            return Localization.get(locale, "poker-trips-with", trips=trips, rest=kickers)
        return Localization.get(locale, "poker-trips", trips=trips)
    if by_count[0][0] == 2 and len(by_count) > 1 and by_count[1][0] == 2:
        high_pair = max(by_count[0][1], by_count[1][1])
        low_pair = min(by_count[0][1], by_count[1][1])
        high_pair_name = _cap(_rank_name_plural(high_pair, locale))
        low_pair_name = _cap(_rank_name_plural(low_pair, locale))
        kickers = _rank_list(
            [r for r in ranks if r not in (by_count[0][1], by_count[1][1])],
            locale,
            cap=True,
        )
        if kickers:
            return Localization.get(
                locale,
                "poker-two-pair-with",
                high=high_pair_name,
                low=low_pair_name,
                kicker=kickers,
            )
        return Localization.get(
            locale, "poker-two-pair", high=high_pair_name, low=low_pair_name
        )
    if by_count[0][0] == 2:
        pair = _cap(_rank_name_plural(by_count[0][1], locale))
        kickers = _rank_list([r for r in ranks if r != by_count[0][1]], locale, cap=True)
        if kickers:
            return Localization.get(locale, "poker-pair-with", pair=pair, rest=kickers)
        return Localization.get(locale, "poker-pair", pair=pair)
    high = _cap(_rank_name(max(ranks), locale))
    return Localization.get(locale, "poker-high-card", high=high)


def _rank_value(rank: int) -> int:
    """Convert Card.rank to standard poker rank (Ace high)."""
    return 14 if rank == 1 else rank


def _rank_name(rank: int, locale: str) -> str:
    normalized = 1 if rank == 14 else rank
    key = RANK_KEYS.get(normalized)
    return Localization.get(locale, key) if key else str(rank)


def _rank_name_plural(rank: int, locale: str) -> str:
    name = _rank_name(rank, locale)
    normalized = 1 if rank == 14 else rank
    key = RANK_KEYS.get(normalized)
    if not key:
        return name
    plural_key = f"{key}-plural"
    return Localization.get(locale, plural_key)


def _rank_list(ranks: Iterable[int], locale: str, cap: bool = False) -> str:
    names = [_rank_name(rank, locale) for rank in ranks]
    if cap:
        names = [_cap(name) for name in names]
    return Localization.format_list_and(locale, names)


def _cap(name: str) -> str:
    if not name:
        return name
    first = name[0].upper()
    return f"{first}{name[1:]}"


def _is_flush(suits: Iterable[int]) -> bool:
    suit_set = set(suits)
    return len(suit_set) == 1 and next(iter(suit_set)) != SUIT_NONE


def _is_straight(ranks: list[int]) -> tuple[bool, int]:
    unique = sorted(set(ranks), reverse=True)
    if len(unique) != 5:
        return False, 0

    high = unique[0]
    low = unique[-1]
    if high - low == 4:
        return True, high

    # Wheel: A-2-3-4-5 (A counted as 14)
    if unique == [14, 5, 4, 3, 2]:
        return True, 5

    return False, 0


def _highest_of_excluding(ranks: list[int], excluded: set[int]) -> list[int]:
    remaining = [r for r in ranks if r not in excluded]
    return sorted(remaining, reverse=True)
