"""Public-information strategy for Skip-Bo bots."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cards import SkipBoCard
    from .game import PlayChoice, SkipBoGame, SkipBoPlayer


def _choice_score(game: SkipBoGame, player: SkipBoPlayer, choice: PlayChoice) -> float:
    """Score a legal play without looking beneath a face-up stock card."""

    source_score = {
        "stock": 10_000,
        "discard": 3_000,
        "hand": 1_000,
    }[choice.source_kind]
    score = float(source_score)

    if choice.source_kind == "stock":
        score += max(0, 100 - len(choice.owner.stock_pile))
        if choice.owner.id == player.id:
            score += 25

    if choice.card.is_wild and choice.source_kind == "hand":
        score -= 1_500

    if choice.needed_value == 12:
        score += 500

    next_needed = 1 if choice.needed_value == 12 else choice.needed_value + 1
    for owner in game._playable_source_owners(player):
        if (
            owner.stock_pile
            and owner.stock_pile[-1].id != choice.card.id
            and (
                owner.stock_pile[-1].is_wild
                or owner.stock_pile[-1].value == next_needed
            )
        ):
            score += 4_000
        for pile in owner.discard_piles:
            if (
                pile
                and pile[-1].id != choice.card.id
                and (pile[-1].is_wild or pile[-1].value == next_needed)
            ):
                score += 800

    for card in player.hand:
        if card.id != choice.card.id and (card.is_wild or card.value == next_needed):
            score += 250

    return score + random.random()


def choose_discard_pile(
    game: SkipBoGame,
    player: SkipBoPlayer,
    card: SkipBoCard,
) -> int:
    """Prefer descending or same-rank discard stacks that can be replayed cleanly."""

    best_index = 0
    best_score = float("-inf")
    for index, pile in enumerate(player.discard_piles):
        score = 0.0
        if not pile:
            score += 40
        else:
            top = pile[-1]
            if not card.is_wild and not top.is_wild and top.value == card.value + 1:
                score += 300
            elif top.value == card.value:
                score += 180
            score -= len(pile) * 2
        if card.is_wild:
            score -= 250
        score += random.random()
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def choose_play(
    game: SkipBoGame,
    player: SkipBoPlayer,
    choices: list[PlayChoice],
) -> PlayChoice:
    """Choose the strongest destination among known legal plays."""

    return max(choices, key=lambda choice: _choice_score(game, player, choice))


def choose_action(game: SkipBoGame, player: SkipBoPlayer) -> str | None:
    """Choose one legal play, otherwise end the turn with a strategic discard."""

    choices = game._legal_play_choices(player)
    if choices:
        return choose_play(game, player, choices).action_id

    if player.hand:
        discard_card = min(
            player.hand,
            key=lambda card: (
                card.is_wild,
                -card.value if not card.is_wild else 0,
                random.random(),
            ),
        )
        return game._source_action_id("hand", player, -1, discard_card)

    if not game._draw_available():
        return "end_turn_empty"
    return None
