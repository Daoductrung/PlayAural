"""Bot strategy for Flip 7."""

from __future__ import annotations

import random

from .constants import (
    CARD_NUMBER,
    CHOICE_FLIP_THREE,
    CHOICE_FREEZE,
    CHOICE_SECOND_CHANCE,
    PHASE_PLAYING,
    STATUS_STAYED,
)


def _bust_risk(game, player) -> float:
    """Chance that the next drawn card repeats a number already held."""
    if not player.numbers:
        return 0.0

    total = len(game.deck)
    source = game.deck
    if total == 0:
        source = game.discard
        total = len(source)
    if total <= 0:
        return 0.0

    held = set(player.numbers)
    unsafe = 0
    for card in source:
        if card.kind == CARD_NUMBER and card.value in held:
            unsafe += 1
    return unsafe / total


def _should_hit(game, player) -> bool:
    """Push the luck while the expected gain still beats the bust chance."""
    if not player.numbers:
        # Nothing can repeat yet, so always take a card.
        return True

    held = len(player.numbers)
    risk = _bust_risk(game, player)
    if player.second_chance:
        # The duplicate is absorbed, but the safety net is spent.
        risk = 0.0

    if held == 6:
        # One more unique number pays the Flip 7 bonus immediately.
        return risk < 0.30

    threshold = 0.20 if player.second_chance else 0.11
    if held >= 4:
        threshold += 0.05
    if held <= 2:
        threshold += 0.06

    if risk < threshold:
        return True
    # Occasionally take a calculated risk so bots do not play identically.
    return random.random() < 0.12


def _pick_target(game, kind):
    targets = game._choice_targets()
    if not targets:
        return None
    actor = game._choice_actor()

    if kind == CHOICE_SECOND_CHANCE:
        # Protect whoever is closest to a dangerous hand.
        return max(targets, key=lambda p: (len(p.numbers), p.total_score))
    if kind == CHOICE_FLIP_THREE:
        # Hurt the strongest table presence.
        return max(targets, key=lambda p: (p.total_score, len(p.numbers)))
    if kind == CHOICE_FREEZE:
        leader = max(targets, key=lambda p: (p.total_score, len(p.numbers)))
        if actor is not None and leader is actor and len(targets) > 1:
            others = [p for p in targets if p is not actor]
            return max(others, key=lambda p: (p.total_score, len(p.numbers)))
        return leader
    return targets[0]


def bot_think(game, player):
    if game.pending_choice is not None:
        if game._choice_actor() is not player:
            return None
        target = _pick_target(game, game.pending_choice.kind)
        if target is None:
            return None
        return f"choose_{game.pending_choice.kind}_{target.id}"

    if game.phase != PHASE_PLAYING or game.flip_state is not None:
        return None
    if game.deal_index < len(game.deal_order):
        return None
    if game.current_player is not player:
        return None
    if game._is_hit_enabled(player) is not None:
        return None

    if _should_hit(game, player):
        return "hit"
    if game._is_stay_enabled(player) is None:
        # Staying requires something to bank; otherwise there is nothing to do.
        flip_player = player
        if flip_player.round_status != STATUS_STAYED:
            return "stay"
    return None
