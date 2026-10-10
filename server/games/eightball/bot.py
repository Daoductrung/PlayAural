"""Pocket-planning bot for Eight-Ball Pool.

The game still uses PlayAural's BotHelper for scheduling.  This module only
chooses the physical cue parameters when the native bot turn arrives.
"""

from __future__ import annotations

import math
import random
from typing import Iterable

from .physics import BALL_RADIUS, Ball, get_table_geometry


DIFFICULTIES = ("easy", "medium", "hard", "hardcore")
DEFAULT_DIFFICULTY = "medium"

_SETTINGS = {
    # aim error, power error, number of credible shots considered
    "easy": (4.5, 12, 6),
    "medium": (1.8, 7, 4),
    "hard": (0.65, 3, 2),
    "hardcore": (0.18, 1, 1),
}


def choose_shot(
    balls: list[Ball], legal_numbers: set[int], difficulty: str, *,
    break_shot: bool = False, table_size: str = "9ft",
) -> tuple[float, int, int]:
    angle, power, spin, _, _ = choose_shot_plan(
        balls, legal_numbers, difficulty, break_shot=break_shot,
        table_size=table_size,
    )
    return angle, power, spin


def choose_shot_plan(
    balls: list[Ball], legal_numbers: set[int], difficulty: str, *,
    break_shot: bool = False, table_size: str = "9ft",
) -> tuple[float, int, int, int, int]:
    geometry = get_table_geometry(table_size)
    pockets = geometry.pocket_aim_points
    cue = next((ball for ball in balls if ball.number == 0 and not ball.potted), None)
    if cue is None:
        return 180.0, 70, 0, -1, -1
    aim_error, power_error, candidate_count = _SETTINGS.get(
        difficulty, _SETTINGS[DEFAULT_DIFFICULTY]
    )
    if break_shot:
        angle = math.degrees(
            math.atan2(-cue.y, -geometry.half_width / 2.0 - cue.x)
        ) % 360.0
        return (
            (angle + random.gauss(0.0, aim_error * 0.18)) % 360.0,
            max(60, min(100, 92 + random.randint(-power_error // 2, power_error // 2))),
            0, -1, -1,
        )

    candidates: list[tuple[float, float, int, int, int]] = []
    objects = [ball for ball in balls if not ball.potted and ball.number in legal_numbers]
    blockers = [ball for ball in balls if not ball.potted and ball.number != 0]
    for target in objects:
        for pocket_index, pocket in enumerate(pockets):
            tx, ty = pocket[0] - target.x, pocket[1] - target.y
            target_path = math.hypot(tx, ty)
            if target_path <= 0.01:
                continue
            ux, uy = tx / target_path, ty / target_path
            contact_x = target.x - ux * BALL_RADIUS * 2.0
            contact_y = target.y - uy * BALL_RADIUS * 2.0
            cue_path = math.hypot(contact_x - cue.x, contact_y - cue.y)
            if cue_path <= 0.01:
                continue
            if _blocked(cue.x, cue.y, contact_x, contact_y, blockers, {target.number}):
                continue
            if _blocked(target.x, target.y, pocket[0], pocket[1], blockers, {target.number}):
                continue
            cut = _angle_between(
                contact_x - cue.x, contact_y - cue.y, pocket[0] - target.x, pocket[1] - target.y
            )
            if cut > 76.0:
                continue
            score = cue_path + target_path * 0.65 + cut * 1.7
            angle = math.degrees(math.atan2(contact_y - cue.y, contact_x - cue.x)) % 360.0
            power = int(max(28, min(100, 30 + (cue_path + target_path) * 0.62)))
            candidates.append((score, angle, power, target.number, pocket_index))

    if candidates:
        credible = sorted(candidates, key=lambda item: item[0])[:candidate_count]
        # Weaker bots still recognize real potting lines, but choose less
        # consistently among them and execute with larger human-like errors.
        weights = [1.0 / (index + 1) for index in range(len(credible))]
        _, angle, power, target_number, pocket_index = random.choices(
            credible, weights=weights, k=1,
        )[0]
    elif objects:
        target = random.choice(objects)
        angle = math.degrees(math.atan2(target.y - cue.y, target.x - cue.x)) % 360.0
        power = random.randint(45, 82)
        target_number = target.number
        pocket_index = min(
            range(len(pockets)),
            key=lambda index: math.hypot(
                pockets[index][0] - target.x, pockets[index][1] - target.y,
            ),
        )
    else:
        return 180.0, 65, 0, -1, -1

    angle = (angle + random.gauss(0.0, aim_error)) % 360.0
    power = max(10, min(100, power + random.randint(-power_error, power_error)))
    spin = random.choice((-1, 0, 0, 0, 1)) if difficulty != "easy" else 0
    return round(angle, 1), power, spin, target_number, pocket_index


def _blocked(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    balls: Iterable[Ball],
    ignored: set[int],
) -> bool:
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq <= 0.01:
        return False
    for ball in balls:
        if ball.number in ignored:
            continue
        projection = ((ball.x - ax) * dx + (ball.y - ay) * dy) / length_sq
        if projection <= 0.04 or projection >= 0.96:
            continue
        px, py = ax + projection * dx, ay + projection * dy
        if math.hypot(ball.x - px, ball.y - py) < BALL_RADIUS * 2.08:
            return True
    return False


def _angle_between(ax: float, ay: float, bx: float, by: float) -> float:
    divisor = max(1e-9, math.hypot(ax, ay) * math.hypot(bx, by))
    cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / divisor))
    return math.degrees(math.acos(cosine))
