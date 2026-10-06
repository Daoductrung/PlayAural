"""Public-information bot policy for Flip 7."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    CARD_DOUBLE,
    CARD_MODIFIER,
    CARD_NUMBER,
    CHOICE_FLIP_THREE,
    CHOICE_FREEZE,
    CHOICE_SECOND_CHANCE,
    FLIP_SEVEN_BONUS,
    FLIP_SEVEN_TARGET,
)


@dataclass(frozen=True)
class CardCount:
    """One publicly inferable card type in the remaining draw pool."""

    kind: str
    value: int
    count: int


@dataclass(frozen=True)
class BotObservation:
    """Public state needed for one draw-or-stop decision."""

    numbers: tuple[int, ...]
    number_total: int
    has_double: bool
    second_chance: bool
    round_points: int
    total_score: int
    target_score: int
    secured_score_to_beat: int
    draw_counts: tuple[CardCount, ...]


@dataclass(frozen=True)
class NextDrawMetrics:
    """Exact immediate risk and stop value of taking one more card."""

    bust_probability: float
    expected_stop_score: float


@dataclass(frozen=True)
class TargetObservation:
    """Public state used to spend one targeted action card."""

    player_id: str
    is_actor: bool
    number_count: int
    round_points: int
    total_score: int
    second_chance: bool
    bust_probability: float

    @property
    def projected_score(self) -> int:
        return self.total_score + self.round_points


def next_draw_metrics(observation: BotObservation) -> NextDrawMetrics:
    """Evaluate one unknown draw without consulting the shuffled card order."""

    total_cards = sum(card.count for card in observation.draw_counts)
    if total_cards <= 0:
        return NextDrawMetrics(0.0, float(observation.round_points))

    held = set(observation.numbers)
    expected_score = 0.0
    bust_cards = 0
    for card in observation.draw_counts:
        score = observation.round_points
        if card.kind == CARD_NUMBER:
            if card.value in held:
                if not observation.second_chance:
                    bust_cards += card.count
                    score = 0
            else:
                multiplier = 2 if observation.has_double else 1
                score += card.value * multiplier
                if len(held) + 1 == FLIP_SEVEN_TARGET:
                    score += FLIP_SEVEN_BONUS
        elif card.kind == CARD_MODIFIER:
            score += card.value
        elif card.kind == CARD_DOUBLE and not observation.has_double:
            score += observation.number_total
        expected_score += card.count * score

    return NextDrawMetrics(
        bust_probability=bust_cards / total_cards,
        expected_stop_score=expected_score / total_cards,
    )


def choose_action(observation: BotObservation) -> str:
    """Choose Draw or Stop from public state and exact one-card expectation."""

    if not observation.numbers:
        # A first number cannot repeat, while every non-number card is safe.
        return "hit"

    projected_score = observation.total_score + observation.round_points
    if (
        projected_score >= observation.target_score
        and projected_score >= observation.secured_score_to_beat
    ):
        # Securing either the lead or an official extra-round tie is preferable
        # to risking a score that already reaches the match target.
        return "stay"

    metrics = next_draw_metrics(observation)
    if metrics.bust_probability == 0:
        return "hit"

    if (
        observation.secured_score_to_beat >= observation.target_score
        and projected_score < observation.secured_score_to_beat
    ):
        # Stopping behind a target-reaching opponent cannot win this round.
        return "hit"

    return "hit" if metrics.expected_stop_score > observation.round_points else "stay"


def choose_target(
    kind: str,
    targets: tuple[TargetObservation, ...],
    *,
    actor_should_stay: bool = False,
) -> str | None:
    """Spend an action card without using private or future information."""

    if not targets:
        return None

    actor = next((target for target in targets if target.is_actor), None)
    opponents = tuple(target for target in targets if not target.is_actor)

    if kind == CHOICE_SECOND_CHANCE:
        # Keeping protection never helps an opponent. If the actor already
        # has one, give the extra where it has the least defensive value.
        if actor is not None:
            return actor.player_id
        return min(
            targets,
            key=lambda target: (
                target.bust_probability,
                target.round_points,
                target.number_count,
                target.projected_score,
            ),
        ).player_id

    if kind == CHOICE_FREEZE:
        if actor is not None and actor_should_stay:
            return actor.player_id
        if opponents:
            # Freeze an opponent who banks as little as possible; among equal
            # stakes, stop the greater match threat first.
            return min(
                opponents,
                key=lambda target: (
                    target.round_points,
                    -target.total_score,
                    -target.number_count,
                ),
            ).player_id
        return actor.player_id if actor is not None else targets[0].player_id

    if kind == CHOICE_FLIP_THREE:
        if (
            actor is not None
            and actor.number_count == FLIP_SEVEN_TARGET - 1
            and (actor.second_chance or actor.bust_probability <= 0.15)
        ):
            # A protected or low-risk sixth number makes self-targeting the
            # strongest route to the round-ending Flip 7 bonus.
            return actor.player_id
        candidates = opponents or targets
        # Prefer an exposed opponent with the most to lose. A held Second
        # Chance makes the immediate duplicate risk zero and is considered
        # before every other tie-breaker.
        return max(
            candidates,
            key=lambda target: (
                not target.second_chance,
                target.bust_probability,
                target.round_points,
                target.number_count,
                target.total_score,
            ),
        ).player_id

    return targets[0].player_id
