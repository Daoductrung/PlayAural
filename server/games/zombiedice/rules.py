"""Pure rules and dice-pool operations for Zombie Dice."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

GREEN = "green"
YELLOW = "yellow"
RED = "red"
COLORS = (GREEN, YELLOW, RED)

BRAIN = "brain"
FOOTPRINT = "footprint"
SHOTGUN = "shotgun"
FACES = (BRAIN, FOOTPRINT, SHOTGUN)

OFFICIAL_TARGET_SCORE = 13
MIN_TARGET_SCORE = 5
MAX_TARGET_SCORE = 50
DICE_PER_ROLL = 3
SHOTGUNS_TO_BUST = 3

DICE_BY_COLOR = {
    GREEN: 6,
    YELLOW: 4,
    RED: 3,
}

# Repeated values represent the six equally likely faces of each die.
FACE_DISTRIBUTIONS = {
    GREEN: (BRAIN, BRAIN, BRAIN, FOOTPRINT, FOOTPRINT, SHOTGUN),
    YELLOW: (BRAIN, BRAIN, FOOTPRINT, FOOTPRINT, SHOTGUN, SHOTGUN),
    RED: (BRAIN, FOOTPRINT, FOOTPRINT, SHOTGUN, SHOTGUN, SHOTGUN),
}


class RandomSource(Protocol):
    """The subset of ``random`` used by the rules engine."""

    def randrange(self, stop: int) -> int: ...


@dataclass
class DicePool:
    """A serializable count of green, yellow, and red dice."""

    green: int = 0
    yellow: int = 0
    red: int = 0

    def __post_init__(self) -> None:
        for color in COLORS:
            self._validate_count(getattr(self, color))

    @classmethod
    def full(cls) -> DicePool:
        return cls(
            green=DICE_BY_COLOR[GREEN],
            yellow=DICE_BY_COLOR[YELLOW],
            red=DICE_BY_COLOR[RED],
        )

    @property
    def total(self) -> int:
        return self.green + self.yellow + self.red

    def count(self, color: str) -> int:
        self._validate_color(color)
        return int(getattr(self, color))

    def add(self, color: str, count: int = 1) -> None:
        self._validate_count(count)
        self._validate_color(color)
        setattr(self, color, self.count(color) + count)

    def remove(self, color: str, count: int = 1) -> None:
        self._validate_count(count)
        self._validate_color(color)
        remaining = self.count(color) - count
        if remaining < 0:
            raise ValueError(f"Cannot remove {count} {color} dice from this pool")
        setattr(self, color, remaining)

    def add_pool(self, other: DicePool) -> None:
        for color in COLORS:
            self.add(color, other.count(color))

    def clear(self) -> None:
        self.green = 0
        self.yellow = 0
        self.red = 0

    def colors(self) -> list[str]:
        return [color for color in COLORS for _ in range(self.count(color))]

    def copy(self) -> DicePool:
        return DicePool(self.green, self.yellow, self.red)

    @staticmethod
    def _validate_color(color: str) -> None:
        if color not in COLORS:
            raise ValueError(f"Unsupported Zombie Dice color: {color!r}")

    @staticmethod
    def _validate_count(count: int) -> None:
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"Dice counts must be non-negative integers: {count!r}")


@dataclass(frozen=True)
class RollResult:
    """One rolled die and its public face."""

    color: str
    face: str

    def __post_init__(self) -> None:
        if self.color not in COLORS:
            raise ValueError(f"Unsupported Zombie Dice color: {self.color!r}")
        if self.face not in FACES:
            raise ValueError(f"Unsupported Zombie Dice face: {self.face!r}")


def draw_colors(
    pool: DicePool,
    count: int,
    rng: RandomSource = random,
) -> list[str]:
    """Draw ``count`` colors uniformly without replacement, mutating ``pool``."""

    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Draw count must be a non-negative integer")
    if count > pool.total:
        raise ValueError("The cup does not contain enough dice for this draw")

    drawn: list[str] = []
    for _ in range(count):
        pick = rng.randrange(pool.total)
        for color in COLORS:
            color_count = pool.count(color)
            if pick < color_count:
                pool.remove(color)
                drawn.append(color)
                break
            pick -= color_count
    return drawn


def roll_colors(
    colors: list[str],
    rng: RandomSource = random,
) -> list[RollResult]:
    """Roll the supplied colored dice using their official face distributions."""

    results: list[RollResult] = []
    for color in colors:
        DicePool._validate_color(color)
        faces = FACE_DISTRIBUTIONS[color]
        results.append(RollResult(color=color, face=faces[rng.randrange(len(faces))]))
    return results


def combined_pool(*pools: DicePool) -> DicePool:
    """Return the color-wise total of several pools without mutating them."""

    result = DicePool()
    for pool in pools:
        result.add_pool(pool)
    return result


def has_complete_die_set(*pools: DicePool) -> bool:
    """Return whether the supplied locations contain exactly the official set."""

    total = combined_pool(*pools)
    return all(total.count(color) == DICE_BY_COLOR[color] for color in COLORS)
