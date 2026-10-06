"""Public-information bot policy for Zombie Dice."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from functools import cache, lru_cache

from .rules import (
    BRAIN,
    COLORS,
    DICE_PER_ROLL,
    FACE_DISTRIBUTIONS,
    FOOTPRINT,
    SHOTGUN,
    SHOTGUNS_TO_BUST,
    DicePool,
)

PoolCounts = tuple[int, int, int]

# Two complete future rolls improve materially on a next-roll-only threshold
# while keeping every decision cheap enough for the server tick loop. The final
# layer always banks, so truncation is conservative rather than reckless.
BOT_LOOKAHEAD_ROLLS = 2
BOT_VALUE_CACHE_SIZE = 32_768
ENDGAME_PRESSURE_MARGIN = 3


@dataclass(frozen=True)
class BotObservation:
    """Everything a player may use when deciding whether to continue."""

    cup: DicePool
    footprints: DicePool
    brain_dice: DicePool
    shotguns: int
    turn_brains: int
    banked_score: int
    target_score: int
    score_to_beat: int
    final_round_active: bool
    in_tiebreaker: bool
    has_rolled: bool
    later_opponent_score: int = 0


@dataclass(frozen=True)
class NextRollMetrics:
    """Exact one-roll bust risk and safe expected brain gain."""

    bust_probability: float
    expected_safe_brains: float


@dataclass(frozen=True)
class _RollTransition:
    """One aggregated physical result of the next roll."""

    cup: PoolCounts
    footprints: PoolCounts
    brain_dice: PoolCounts
    shotguns: int
    brain_gain: int
    probability: float


def next_roll_metrics(observation: BotObservation) -> NextRollMetrics:
    """Return exact next-roll risk without consulting future random values."""

    bust_probability = 0.0
    expected_safe_brains = 0.0
    for transition in _roll_transitions(
        _pool_counts(observation.cup),
        _pool_counts(observation.footprints),
        _pool_counts(observation.brain_dice),
        observation.shotguns,
    ):
        if transition.shotguns >= SHOTGUNS_TO_BUST:
            bust_probability += transition.probability
        else:
            expected_safe_brains += transition.probability * transition.brain_gain

    return NextRollMetrics(
        bust_probability=bust_probability,
        expected_safe_brains=expected_safe_brains,
    )


def choose_action(observation: BotObservation) -> str:
    """Choose a legal roll-or-bank action from the public game state."""

    if not observation.has_rolled or observation.turn_brains == 0:
        return "roll"

    potential_score = observation.banked_score + observation.turn_brains
    match_is_deciding = observation.final_round_active or observation.in_tiebreaker
    if match_is_deciding:
        if potential_score > observation.score_to_beat:
            return "bank"
        if potential_score < observation.score_to_beat:
            # Banking while behind cannot produce a win or a tiebreak.
            return "roll"
        # Banking a tie preserves a guaranteed place in the official repeatable
        # tiebreak instead of risking immediate elimination.
        return "bank"

    if potential_score >= observation.target_score:
        return "bank"

    if observation.later_opponent_score >= (
        observation.target_score - ENDGAME_PRESSURE_MARGIN
    ):
        # A later seat is likely to trigger the final round before this bot can
        # act again, so cautious partial scoring no longer protects the match.
        return "roll"

    roll_value = _optimal_roll_value(
        _pool_counts(observation.cup),
        _pool_counts(observation.footprints),
        _pool_counts(observation.brain_dice),
        observation.shotguns,
        observation.turn_brains,
        observation.target_score - observation.banked_score,
        BOT_LOOKAHEAD_ROLLS,
    )
    return "roll" if roll_value > observation.turn_brains else "bank"


def _pool_counts(pool: DicePool) -> PoolCounts:
    return pool.green, pool.yellow, pool.red


def _add_counts(left: PoolCounts, right: PoolCounts) -> PoolCounts:
    return (
        left[0] + right[0],
        left[1] + right[1],
        left[2] + right[2],
    )


def _subtract_counts(left: PoolCounts, right: PoolCounts) -> PoolCounts:
    return (
        left[0] - right[0],
        left[1] - right[1],
        left[2] - right[2],
    )


@cache
def _draw_scenarios(
    cup: PoolCounts,
    count: int,
) -> tuple[tuple[PoolCounts, float], ...]:
    """Aggregate unordered draws using the exact hypergeometric probability."""

    total = sum(cup)
    if count < 0 or count > total:
        raise ValueError("Bot observation cannot supply a complete roll")
    denominator = math.comb(total, count)
    scenarios: list[tuple[PoolCounts, float]] = []
    for green in range(min(cup[0], count) + 1):
        for yellow in range(min(cup[1], count - green) + 1):
            red = count - green - yellow
            if red < 0 or red > cup[2]:
                continue
            drawn = (green, yellow, red)
            numerator = math.prod(
                math.comb(available, selected)
                for available, selected in zip(cup, drawn, strict=True)
            )
            scenarios.append((drawn, numerator / denominator))
    return tuple(scenarios)


@cache
def _color_face_scenarios(
    color_index: int,
    count: int,
) -> tuple[tuple[int, int, int, float], ...]:
    """Return aggregated brain, footprint, and shotgun results for one color."""

    faces = FACE_DISTRIBUTIONS[COLORS[color_index]]
    face_counts = tuple(faces.count(face) for face in (BRAIN, FOOTPRINT, SHOTGUN))
    scenarios: list[tuple[int, int, int, float]] = []
    for brains in range(count + 1):
        for footprints in range(count - brains + 1):
            shotguns = count - brains - footprints
            outcome_counts = (brains, footprints, shotguns)
            arrangements = math.factorial(count) // math.prod(
                math.factorial(value) for value in outcome_counts
            )
            probability = arrangements * math.prod(
                (face_count / len(faces)) ** outcome_count
                for face_count, outcome_count in zip(
                    face_counts,
                    outcome_counts,
                    strict=True,
                )
            )
            scenarios.append((brains, footprints, shotguns, probability))
    return tuple(scenarios)


@cache
def _face_scenarios(
    rolled: PoolCounts,
) -> tuple[tuple[PoolCounts, PoolCounts, int, float], ...]:
    """Aggregate all face outcomes while retaining the colors set aside."""

    scenarios: dict[tuple[PoolCounts, PoolCounts, int], float] = {
        ((0, 0, 0), (0, 0, 0), 0): 1.0
    }
    for color_index, count in enumerate(rolled):
        expanded: defaultdict[tuple[PoolCounts, PoolCounts, int], float] = defaultdict(
            float
        )
        for (
            brain_counts,
            footprint_counts,
            shotguns,
        ), base_probability in scenarios.items():
            for (
                brains,
                footprints,
                added_shotguns,
                probability,
            ) in _color_face_scenarios(color_index, count):
                next_brains = list(brain_counts)
                next_footprints = list(footprint_counts)
                next_brains[color_index] += brains
                next_footprints[color_index] += footprints
                key = (
                    tuple(next_brains),
                    tuple(next_footprints),
                    shotguns + added_shotguns,
                )
                expanded[key] += base_probability * probability
        scenarios = dict(expanded)
    return tuple(
        (brain_counts, footprint_counts, shotguns, probability)
        for (brain_counts, footprint_counts, shotguns), probability in scenarios.items()
    )


@cache
def _roll_transitions(
    cup: PoolCounts,
    footprints: PoolCounts,
    brain_dice: PoolCounts,
    shotguns: int,
) -> tuple[_RollTransition, ...]:
    """Enumerate every distinct next state and its exact probability."""

    if sum(cup) < DICE_PER_ROLL:
        cup = _add_counts(cup, brain_dice)
        brain_dice = (0, 0, 0)

    draw_count = DICE_PER_ROLL - sum(footprints)
    outcomes: defaultdict[
        tuple[PoolCounts, PoolCounts, PoolCounts, int, int], float
    ] = defaultdict(float)
    for drawn, draw_probability in _draw_scenarios(cup, draw_count):
        cup_after_draw = _subtract_counts(cup, drawn)
        rolled = _add_counts(footprints, drawn)
        for (
            rolled_brains,
            next_footprints,
            added_shotguns,
            face_probability,
        ) in _face_scenarios(rolled):
            key = (
                cup_after_draw,
                next_footprints,
                _add_counts(brain_dice, rolled_brains),
                shotguns + added_shotguns,
                sum(rolled_brains),
            )
            outcomes[key] += draw_probability * face_probability
    return tuple(
        _RollTransition(*state, probability) for state, probability in outcomes.items()
    )


@lru_cache(maxsize=BOT_VALUE_CACHE_SIZE)
def _optimal_turn_value(
    cup: PoolCounts,
    footprints: PoolCounts,
    brain_dice: PoolCounts,
    shotguns: int,
    turn_brains: int,
    bank_threshold: int,
    rolls_remaining: int,
) -> float:
    """Return the best expected turn score from one decision point."""

    if turn_brains >= bank_threshold or rolls_remaining <= 0:
        return float(turn_brains)
    return max(
        float(turn_brains),
        _optimal_roll_value(
            cup,
            footprints,
            brain_dice,
            shotguns,
            turn_brains,
            bank_threshold,
            rolls_remaining,
        ),
    )


@lru_cache(maxsize=BOT_VALUE_CACHE_SIZE)
def _optimal_roll_value(
    cup: PoolCounts,
    footprints: PoolCounts,
    brain_dice: PoolCounts,
    shotguns: int,
    turn_brains: int,
    bank_threshold: int,
    rolls_remaining: int,
) -> float:
    """Return the expected turn score from committing to one more roll."""

    if rolls_remaining <= 0:
        return float(turn_brains)
    expected_value = 0.0
    for transition in _roll_transitions(cup, footprints, brain_dice, shotguns):
        if transition.shotguns >= SHOTGUNS_TO_BUST:
            continue
        expected_value += transition.probability * _optimal_turn_value(
            transition.cup,
            transition.footprints,
            transition.brain_dice,
            transition.shotguns,
            turn_brains + transition.brain_gain,
            bank_threshold,
            rolls_remaining - 1,
        )
    return expected_value
