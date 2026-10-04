"""Public-information strategy for Skip-Bo bots."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from . import cards

if TYPE_CHECKING:
    from .cards import SkipBoCard
    from .game import PlayChoice, SkipBoGame, SkipBoPlayer


SOURCE_PRIORITY = {
    "stock": 10_000,
    "discard": 3_000,
    "hand": 1_000,
}
OWN_STOCK_BONUS = 25
HAND_WILD_PENALTY = 1_500
BUILDING_COMPLETION_BONUS = 500
STOCK_FOLLOW_UP_BONUS = 4_000
DISCARD_FOLLOW_UP_BONUS = 800
HAND_FOLLOW_UP_BONUS = 250

EMPTY_DISCARD_BONUS = 40
DESCENDING_DISCARD_BONUS = 300
MATCHING_DISCARD_BONUS = 180
DISCARD_DEPTH_PENALTY = 2
DISCARD_CARD_VALUE_WEIGHT = 10
DISCARD_DUPLICATE_BONUS = 30
DISCARD_WILD_PENALTY = 250
NEXT_VALUE_RETENTION_BONUS = 80
SECOND_NEXT_VALUE_RETENTION_BONUS = 35


def _choice_score(game: SkipBoGame, player: SkipBoPlayer, choice: PlayChoice) -> float:
    """Score a legal play without looking beneath a face-up stock card."""

    score = float(SOURCE_PRIORITY[choice.source_kind])

    if choice.source_kind == "stock":
        score -= len(choice.owner.stock_pile)
        if choice.owner.id == player.id:
            score += OWN_STOCK_BONUS

    if choice.card.is_wild and choice.source_kind == "hand":
        score -= HAND_WILD_PENALTY

    if choice.needed_value == cards.MAX_NUMBER:
        score += BUILDING_COMPLETION_BONUS

    next_needed = (
        cards.MIN_NUMBER
        if choice.needed_value == cards.MAX_NUMBER
        else choice.needed_value + 1
    )
    for owner in game._playable_source_owners(player):
        if (
            owner.stock_pile
            and owner.stock_pile[-1].id != choice.card.id
            and (
                owner.stock_pile[-1].is_wild
                or owner.stock_pile[-1].value == next_needed
            )
        ):
            score += STOCK_FOLLOW_UP_BONUS
        for pile in owner.discard_piles:
            if (
                pile
                and pile[-1].id != choice.card.id
                and (pile[-1].is_wild or pile[-1].value == next_needed)
            ):
                score += DISCARD_FOLLOW_UP_BONUS

    for card in player.hand:
        if card.id != choice.card.id and (card.is_wild or card.value == next_needed):
            score += HAND_FOLLOW_UP_BONUS

    return score + random.random()


def _discard_placement_score(
    player: SkipBoPlayer,
    card: SkipBoCard,
    pile_index: int,
) -> float:
    """Score one destination using only its visible top card and size."""

    pile = player.discard_piles[pile_index]
    if not pile:
        return float(EMPTY_DISCARD_BONUS)

    top = pile[-1]
    score = -len(pile) * DISCARD_DEPTH_PENALTY
    if not card.is_wild and not top.is_wild and top.value == card.value + 1:
        score += DESCENDING_DISCARD_BONUS
    elif top.value == card.value:
        score += MATCHING_DISCARD_BONUS
    return float(score)


def _steps_until_playable(game: SkipBoGame, card: SkipBoCard) -> int:
    """Return the fewest visible building steps before a numbered card is usable."""

    if card.is_wild:
        return 0
    return min(
        (card.value - (value + 1)) % cards.MAX_NUMBER for value in game.building_values
    )


def _discard_card_score(
    game: SkipBoGame,
    player: SkipBoPlayer,
    card: SkipBoCard,
) -> float:
    """Prefer shedding awkward high or duplicate cards while retaining near plays."""

    if card.is_wild:
        return -float(DISCARD_WILD_PENALTY)

    score = card.value * DISCARD_CARD_VALUE_WEIGHT
    duplicate_count = sum(
        1 for other in player.hand if other.id != card.id and other.value == card.value
    )
    score += duplicate_count * DISCARD_DUPLICATE_BONUS

    steps = _steps_until_playable(game, card)
    if steps == 1:
        score -= NEXT_VALUE_RETENTION_BONUS
    elif steps == 2:
        score -= SECOND_NEXT_VALUE_RETENTION_BONUS
    return float(score)


def choose_discard_pile(
    player: SkipBoPlayer,
    card: SkipBoCard,
) -> int:
    """Prefer descending or same-rank discard stacks that can be replayed cleanly."""

    return max(
        range(len(player.discard_piles)),
        key=lambda index: (
            _discard_placement_score(player, card, index) + random.random()
        ),
    )


def choose_discard_card(
    game: SkipBoGame,
    player: SkipBoPlayer,
) -> SkipBoCard:
    """Choose a card by considering its best available discard destination."""

    return max(
        player.hand,
        key=lambda card: (
            _discard_card_score(game, player, card)
            + max(
                _discard_placement_score(player, card, index)
                for index in range(len(player.discard_piles))
            )
            + random.random()
        ),
    )


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
        discard_card = choose_discard_card(game, player)
        return game._source_action_id("hand", player, -1, discard_card)

    if not game._draw_available():
        return "end_turn_empty"
    return None
