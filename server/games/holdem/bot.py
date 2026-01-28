"""
Bot AI for Texas Hold'em.

Lightweight strategy based on preflop hand strength, position, stack size,
and postflop hand category.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import random

from ...game_utils.poker_evaluator import best_hand
from ...game_utils.poker_state import order_after_button
from ...game_utils.poker_actions import compute_pot_limit_caps, clamp_total_to_cap

if TYPE_CHECKING:
    from .game import HoldemGame, HoldemPlayer


def bot_think(game: "HoldemGame", player: "HoldemPlayer") -> str | None:
    if game.current_player != player or not game.betting:
        return None

    to_call = game.betting.amount_to_call(player.id)
    can_raise = game.betting.can_raise()
    stack_bb = player.chips / max(1, game.current_big_blind or 1)
    position = _position_index(game, player)

    can_raise_amount = _can_raise_amount(game, player, to_call)
    variance = random.uniform(0.85, 1.2)
    if len(game.community) < 3:
        strength = _preflop_strength(player)
        return _decide_preflop(
            strength, to_call, can_raise, stack_bb, position, can_raise_amount, variance
        )

    score = None
    if len(player.hand) + len(game.community) >= 5:
        score, _ = best_hand(player.hand + game.community)
    return _decide_postflop(
        score, to_call, can_raise, stack_bb, position, can_raise_amount, variance
    )


def _position_index(game: "HoldemGame", player: "HoldemPlayer") -> int:
    active = [p for p in game.get_active_players() if isinstance(p, type(player)) and not p.folded]
    active_ids = [p.id for p in active]
    order = order_after_button(active_ids, game.table_state.get_button_id(active_ids))
    if not order or player.id not in order:
        return 0
    return order.index(player.id)


def _preflop_strength(player: "HoldemPlayer") -> int:
    if len(player.hand) < 2:
        return 0
    ranks = sorted([_rank_value(c.rank) for c in player.hand], reverse=True)
    suited = player.hand[0].suit == player.hand[1].suit
    pair = ranks[0] == ranks[1]
    high, low = ranks
    gap = high - low
    broadway = high >= 10 and low >= 10

    if pair and high >= 11:
        return 4  # premium pair
    if (high == 14 and low >= 13) or (pair and high >= 9):
        return 3  # AK, QQ+, or medium pair
    if suited and (broadway or gap == 1):
        return 2  # suited broadway or connectors
    if high == 14 and low >= 10:
        return 2  # strong ace
    if pair:
        return 1  # small pair
    if suited and high >= 10:
        return 1
    return 0


def _decide_preflop(
    strength: int,
    to_call: int,
    can_raise: bool,
    stack_bb: float,
    position: int,
    can_raise_amount: bool,
    variance: float,
) -> str:
    late_position = position >= 2
    short_stack = stack_bb <= 12
    loose = variance > 1.05
    if to_call == 0:
        if can_raise and can_raise_amount and (strength >= 2 or (strength >= 1 and loose)) and stack_bb >= 6:
            return "raise"
        if loose and can_raise and can_raise_amount and random.random() < 0.15:
            return "raise"
        return "call"
    if strength >= 3:
        if can_raise and can_raise_amount and stack_bb >= 8 and to_call <= stack_bb * 2:
            return "raise"
        return "call"
    if strength == 2:
        if to_call <= stack_bb * (1.5 if late_position or loose else 1.0) or short_stack:
            return "call"
        return "fold"
    if strength == 1:
        if to_call <= max(1, stack_bb * (0.7 if late_position or loose else 0.4)):
            return "call"
        return "fold"
    if to_call <= max(1, stack_bb * (0.3 if late_position or loose else 0.15)):
        return "call"
    return "fold"


def _decide_postflop(
    score: tuple[int, tuple[int, ...]] | None,
    to_call: int,
    can_raise: bool,
    stack_bb: float,
    position: int,
    can_raise_amount: bool,
    variance: float,
) -> str:
    late_position = position >= 2
    loose = variance > 1.05
    if to_call == 0:
        if score and score[0] >= 2 and can_raise and can_raise_amount and stack_bb >= 6:
            return "raise"
        if loose and can_raise and can_raise_amount and random.random() < 0.2:
            return "raise"
        return "call"
    if score and score[0] >= 4:
        return "raise" if can_raise and can_raise_amount and stack_bb >= 6 else "call"
    if score and score[0] >= 2:
        if to_call <= max(1, stack_bb * (2.5 if loose else 2)):
            return "call"
        return "fold"
    if score and score[0] >= 1:
        if to_call <= max(1, stack_bb * (1.3 if late_position or loose else 1.0)):
            return "call"
        return "fold"
    if to_call <= max(1, stack_bb * (0.7 if late_position or loose else 0.4)):
        return "call"
    return "fold"


def _rank_value(rank: int) -> int:
    return 14 if rank == 1 else rank


def _can_raise_amount(game: "HoldemGame", player: "HoldemPlayer", to_call: int) -> bool:
    if not game.betting:
        return False
    min_raise = max(game.betting.last_raise_size, 1)
    if player.chips - to_call < min_raise:
        return False
    caps = compute_pot_limit_caps(game.pot_manager.total_pot(), to_call, game.options.raise_mode)
    total = clamp_total_to_cap(to_call + min_raise, caps)
    return total - to_call >= min_raise
