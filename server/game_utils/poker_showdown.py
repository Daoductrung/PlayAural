"""Shared showdown helpers for poker games."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

from .poker_state import order_after_button

TPlayer = TypeVar("TPlayer")


def order_winners_by_button(
    winners: list[TPlayer],
    active_ids: list[str],
    button_id: str | None,
    get_id: Callable[[TPlayer], str],
) -> list[TPlayer]:
    if len(winners) <= 1:
        return winners
    order = order_after_button(active_ids, button_id)
    return sorted(winners, key=lambda p: order.index(get_id(p)) if get_id(p) in order else len(order))


def sort_players_for_showdown(
    players: Iterable[TPlayer],
    active_ids: list[str],
    button_id: str | None,
    get_id: Callable[[TPlayer], str],
) -> list[TPlayer]:
    order = order_after_button(active_ids, button_id)
    return sorted(list(players), key=lambda p: order.index(get_id(p)) if get_id(p) in order else len(order))


def format_showdown_lines(
    players: Iterable[TPlayer],
    active_ids: list[str],
    button_id: str | None,
    get_id: Callable[[TPlayer], str],
    format_fn: Callable[[TPlayer], tuple[tuple[str, dict], tuple[int, tuple[int, ...]]]],
) -> list[tuple[str, tuple[str, dict], tuple[int, tuple[int, ...]]]]:
    ordered = sort_players_for_showdown(players, active_ids, button_id, get_id)
    lines: list[tuple[str, tuple[str, dict], tuple[int, tuple[int, ...]]]] = []
    for p in ordered:
        line, score = format_fn(p)
        lines.append((get_id(p), line, score))
    lines.sort(key=lambda item: item[2], reverse=True)
    return lines
