"""Bot AI for Dead Man's Poker."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.poker_evaluator import best_hand

if TYPE_CHECKING:
    from .game import DeadMansPokerGame, DeadMansPokerPlayer


PHASE_DECISION = "decision"
PHASE_ALL_IN_RESPONSE = "all_in_response"
PHASE_SWITCH = "switch"
MAX_BULLETS = 8
STARTING_BULLETS = 1


def bot_think(game: "DeadMansPokerGame", player: "DeadMansPokerPlayer") -> str | None:
    """Return the next legal bot action."""
    if player.eliminated or player.folded_this_hand or not player.active_in_hand:
        return None
    if game.current_player != player:
        return None

    if game.phase == PHASE_SWITCH:
        return _choose_switch_replacement(game, player)

    strength = _hand_strength(game, player)
    risk = player.committed_bullets / MAX_BULLETS

    if game.phase == PHASE_ALL_IN_RESPONSE:
        if strength >= 5 or (strength >= 4 and random.random() < 0.45):  # nosec B311
            return "call"
        return "fold"

    if game.phase != PHASE_DECISION:
        return None

    if _should_use_switch(game, player, strength):
        return "switch_card"

    if _should_use_coward_fold(player, strength):
        return "coward_fold"

    if _should_all_in(game, player, strength, risk):
        return "all_in"

    if _should_fold(player, strength, risk):
        return "fold"
    return "call"


def bot_select_switch_card(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    options: list[str],
) -> str | None:
    """Choose which private card to switch."""
    if not options or len(player.hand) < 2:
        return options[0] if options else None
    values = [_rank_value(card.rank) for card in player.hand]
    return str(values.index(min(values)))


def _choose_switch_replacement(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
) -> str | None:
    if game.pending_switch_player_id != player.id:
        return None
    if not game.pending_switch_candidates:
        return None
    best_index = 0
    best_strength = -1
    for index, candidate in enumerate(game.pending_switch_candidates):
        trial = list(player.hand)
        if 0 <= game.pending_switch_card_index < len(trial):
            trial[game.pending_switch_card_index] = candidate
        value = _partial_strength(trial + game.revealed_community_cards)
        if value > best_strength:
            best_strength = value
            best_index = index
    return f"choose_switch_{best_index}"


def _should_use_switch(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    strength: int,
) -> bool:
    if player.used_switch or game.revealed_community_count >= 5:
        return False
    if player.committed_bullets > 3:
        return False
    if strength <= 1 and random.random() < 0.40:  # nosec B311
        return True
    return False


def _should_use_coward_fold(player: "DeadMansPokerPlayer", strength: int) -> bool:
    if player.used_coward_fold or player.acted_this_hand:
        return False
    if player.committed_bullets != 1:
        return False
    return strength == 0 and random.random() < 0.35  # nosec B311


def _should_all_in(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    strength: int,
    risk: float,
) -> bool:
    if game.round_stage < 2 or game.revealed_community_count < 3:
        return False
    if player.committed_bullets >= MAX_BULLETS:
        return False
    opponents = len(game.active_hand_players) - 1
    if opponents <= 0:
        return False
    if strength >= 6 and random.random() < 0.32:  # nosec B311
        return True
    if strength >= 4 and risk <= 0.35 and random.random() < 0.08:  # nosec B311
        return True
    if strength <= 1 and risk <= 0.25 and random.random() < 0.04:  # nosec B311
        return True
    return False


def _should_fold(player: "DeadMansPokerPlayer", strength: int, risk: float) -> bool:
    if not player.acted_this_hand and player.committed_bullets == STARTING_BULLETS:
        return False
    if strength >= 4:
        return False
    if risk >= 0.50 and strength <= 2:
        return random.random() < 0.62  # nosec B311
    if risk >= 0.35 and strength <= 1:
        return random.random() < 0.48  # nosec B311
    return strength == 0 and random.random() < 0.18  # nosec B311


def _hand_strength(game: "DeadMansPokerGame", player: "DeadMansPokerPlayer") -> int:
    cards = player.hand + game.revealed_community_cards
    return _partial_strength(cards)


def _partial_strength(cards) -> int:
    if len(cards) >= 5:
        score, _ = best_hand(cards)
        return score[0]
    counts: dict[int, int] = {}
    for card in cards:
        value = _rank_value(card.rank)
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return 0
    max_count = max(counts.values())
    if max_count >= 3:
        return 3
    pairs = sum(1 for count in counts.values() if count == 2)
    if pairs >= 2:
        return 2
    if pairs == 1:
        return 1
    high = max(counts)
    return 1 if high >= 13 else 0


def _rank_value(rank: int) -> int:
    return 14 if rank == 1 else rank
