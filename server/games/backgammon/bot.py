"""Bot AI for Backgammon — random and simple heuristic strategies.

Both strategies are self-contained and synchronous: bot_think() never
blocks or waits on a future, and always returns an action immediately
(or None when the current phase has nothing to do).
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

log = logging.getLogger(__name__)

from .moves import BackgammonMove
from .state import color_sign

if TYPE_CHECKING:
    from .game import BackgammonGame, BackgammonPlayer


def bot_think(game: BackgammonGame, player: BackgammonPlayer) -> str | None:
    """Decide the bot's next action. Always synchronous."""
    gs = game.game_state
    color = player.color

    if gs.turn_phase == "pre_roll":
        cube_action = _maybe_offer_double(game, player)
        if cube_action:
            return cube_action
        return "point_0"

    if gs.turn_phase == "doubling":
        return _decide_take_or_drop(game, player)

    if gs.turn_phase == "moving":
        legal_moves = game._legal_turn_moves()
        if not legal_moves:
            game._end_moving_phase()
            return None
        return _pick_move(game, player, legal_moves)

    return None


def _maybe_offer_double(game: BackgammonGame, player: BackgammonPlayer) -> str | None:
    """These bots never initiate a double. Returns None (just roll)."""
    return None


def _decide_take_or_drop(game: BackgammonGame, player: BackgammonPlayer) -> str | None:
    """These bots always accept a double."""
    return "accept_double"


def _pick_move(
    game: BackgammonGame,
    player: BackgammonPlayer,
    legal_moves: list[BackgammonMove] | None = None,
) -> str | None:
    """Pick a move based on the configured difficulty."""
    gs = game.game_state
    color = player.color
    difficulty = game.options.bot_difficulty
    moves = legal_moves if legal_moves is not None else game._legal_turn_moves()

    if difficulty == "random":
        return _pick_random_move(moves)

    # "simple" and any unknown value fall back to the simple heuristic.
    return _pick_simple_move(game, color, moves)


def _pick_random_move(moves: list[BackgammonMove]) -> str | None:
    """Pick a random move from the complete-roll legal set."""
    if not moves:
        return None
    move = random.choice(moves)  # nosec B311
    return f"point_{move.source}_{move.destination}"


def _pick_simple_move(
    game: BackgammonGame,
    color: str,
    legal_moves: list[BackgammonMove] | None = None,
) -> str | None:
    """Pick a move using simple heuristics.

    Priority scoring:
    - Bearing off is great
    - Hitting an opponent blot is good
    - Making a new point (landing where we have exactly 1) is good
    - Escaping from opponent's home board is decent
    - Leaving a blot in a dangerous area is bad
    """
    gs = game.game_state
    best_move: BackgammonMove | None = None
    best_score = -9999

    moves = legal_moves if legal_moves is not None else game._legal_turn_moves()
    for move in moves:
        score = _score_move(gs, move, color)
        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        return None
    return f"point_{best_move.source}_{best_move.destination}"


def _score_move(gs, move: BackgammonMove, color: str) -> int:
    """Score a move with simple heuristics. Higher is better."""
    score = 0
    sign = color_sign(color)
    # Bear off: strongly prefer
    if move.is_bear_off:
        score += 100

    # Hit: good, especially in our home board
    if move.is_hit:
        score += 40
        # Hitting in our home board is even better (harder to re-enter)
        if color == "red" and move.destination <= 5:
            score += 20
        elif color == "white" and move.destination >= 18:
            score += 20

    # Making a point (landing where we have exactly 1 checker already)
    if not move.is_bear_off and move.destination >= 0 and move.destination <= 23:
        current = gs.board.points[move.destination]
        if current * sign == 1:
            # We have 1 there — this makes a 2-stack (a point!)
            score += 35
            # Making points in our home board is premium
            if color == "red" and move.destination <= 5:
                score += 15
            elif color == "white" and move.destination >= 18:
                score += 15

    # Leaving a blot (source had 2, now will have 1)
    if move.source >= 0:
        src_count = abs(gs.board.points[move.source])
        if src_count == 2:
            # We're exposing a blot
            score -= 15
            # Worse if in opponent's home board
            if color == "red" and move.source >= 18:
                score -= 15
            elif color == "white" and move.source <= 5:
                score -= 15

    # Landing alone (creating a blot) on an empty point
    if not move.is_bear_off and move.destination >= 0 and move.destination <= 23:
        dest_val = gs.board.points[move.destination]
        if dest_val * sign == 0 and not move.is_hit:
            # Landing alone on empty point = blot
            score -= 10
            # Worse in dangerous territory
            if color == "red" and move.destination >= 18:
                score -= 10
            elif color == "white" and move.destination <= 5:
                score -= 10

    # Prefer advancing runners from opponent's home board
    if move.source >= 0:
        if color == "red" and move.source >= 18:
            score += 8
        elif color == "white" and move.source <= 5:
            score += 8

    # Bar entry: just do it (no penalty, no bonus beyond the hit check)
    if move.source == -1:
        score += 5

    # Small tiebreaker: prefer moving from higher points (advance)
    if move.source >= 0:
        if color == "red":
            score += move.source // 6
        else:
            score += (23 - move.source) // 6

    return score
