"""Shared pot resolution helpers for poker games."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

from .poker_showdown import order_winners_by_button

TPlayer = TypeVar("TPlayer")


def resolve_pot(
    pot_amount: int,
    eligible_players: Iterable[TPlayer],
    active_ids: list[str],
    button_id: str | None,
    get_id: Callable[[TPlayer], str],
    score_fn: Callable[[TPlayer], tuple[int, tuple[int, ...]]],
) -> tuple[list[TPlayer], tuple[int, tuple[int, ...]] | None, int, int]:
    """Resolve a single pot.

    Returns:
        winners, best_score, share, remainder
    """
    best_score = None
    winners: list[TPlayer] = []
    for p in eligible_players:
        score = score_fn(p)
        if best_score is None or score > best_score:
            best_score = score
            winners = [p]
        elif score == best_score:
            winners.append(p)
    if not best_score or not winners:
        return ([], None, 0, 0)
    share = pot_amount // len(winners)
    remainder = pot_amount % len(winners)
    ordered_winners = order_winners_by_button(winners, active_ids, button_id, get_id)
    return (ordered_winners, best_score, share, remainder)
