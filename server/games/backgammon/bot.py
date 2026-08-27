"""Bot AI for Backgammon — random and simple heuristic strategies.

Both strategies are self-contained and synchronous: bot_think() never
blocks or waits on a future, and always returns an action immediately
(or None when the current phase has nothing to do).
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .moves import BackgammonMove
from .state import (
    BAR_SOURCE,
    BEAR_OFF_DESTINATION,
    COLOR_RED,
    HOME_BOARD_POINTS,
    PHASE_DOUBLING,
    PHASE_MOVING,
    PHASE_PRE_ROLL,
    color_sign,
    is_board_point,
    is_home_point,
    is_opponent_home_point,
)

if TYPE_CHECKING:
    from .game import BackgammonGame, BackgammonPlayer


BOT_DIFFICULTY_RANDOM = "random"
BOT_DIFFICULTY_SIMPLE = "simple"

BEAR_OFF_SCORE = 100
HIT_SCORE = 40
HOME_BOARD_HIT_BONUS = 20
MAKE_POINT_SCORE = 35
HOME_BOARD_POINT_BONUS = 15
LEAVE_BLOT_PENALTY = 15
OPPONENT_HOME_BLOT_PENALTY = 15
CREATE_BLOT_PENALTY = 10
OPPONENT_HOME_DESTINATION_PENALTY = 10
ESCAPE_RUNNER_SCORE = 8
BAR_ENTRY_SCORE = 5


def bot_think(game: BackgammonGame, player: BackgammonPlayer) -> str | None:
    """Decide the bot's next action. Always synchronous."""
    gs = game.game_state

    if gs.turn_phase == PHASE_PRE_ROLL:
        cube_action = _maybe_offer_double(game, player)
        if cube_action:
            return cube_action
        return "roll_dice"

    if gs.turn_phase == PHASE_DOUBLING:
        return _decide_take_or_drop(game, player)

    if gs.turn_phase == PHASE_MOVING:
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
    color = player.color
    difficulty = game.options.bot_difficulty
    moves = legal_moves if legal_moves is not None else game._legal_turn_moves()

    if difficulty == BOT_DIFFICULTY_RANDOM:
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
    best_score: int | None = None

    moves = legal_moves if legal_moves is not None else game._legal_turn_moves()
    for move in moves:
        score = _score_move(gs, move, color)
        if best_score is None or score > best_score:
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
        score += BEAR_OFF_SCORE

    # Hit: good, especially in our home board
    if move.is_hit:
        score += HIT_SCORE
        # Hitting in our home board is even better (harder to re-enter)
        if is_home_point(move.destination, color):
            score += HOME_BOARD_HIT_BONUS

    # Making a point (landing where we have exactly 1 checker already)
    if not move.is_bear_off and is_board_point(move.destination):
        current = gs.board.points[move.destination]
        if current * sign == 1:
            # We have 1 there — this makes a 2-stack (a point!)
            score += MAKE_POINT_SCORE
            # Making points in our home board is premium
            if is_home_point(move.destination, color):
                score += HOME_BOARD_POINT_BONUS

    # Leaving a blot (source had 2, now will have 1)
    if move.source != BAR_SOURCE:
        src_count = abs(gs.board.points[move.source])
        if src_count == 2:
            # We're exposing a blot
            score -= LEAVE_BLOT_PENALTY
            # Worse if in opponent's home board
            if is_opponent_home_point(move.source, color):
                score -= OPPONENT_HOME_BLOT_PENALTY

    # Landing alone (creating a blot) on an empty point
    if not move.is_bear_off and is_board_point(move.destination):
        dest_val = gs.board.points[move.destination]
        if dest_val * sign == 0 and not move.is_hit:
            # Landing alone on empty point = blot
            score -= CREATE_BLOT_PENALTY
            # Worse in dangerous territory
            if is_opponent_home_point(move.destination, color):
                score -= OPPONENT_HOME_DESTINATION_PENALTY

    # Prefer advancing runners from opponent's home board
    if move.source != BAR_SOURCE and is_opponent_home_point(move.source, color):
        score += ESCAPE_RUNNER_SCORE

    # Bar entry: just do it (no penalty, no bonus beyond the hit check)
    if move.source == BAR_SOURCE:
        score += BAR_ENTRY_SCORE

    # Small tiebreaker: prefer moving from higher points (advance)
    if move.source != BAR_SOURCE:
        if color == COLOR_RED:
            score += move.source // HOME_BOARD_POINTS
        else:
            score += (
                BEAR_OFF_DESTINATION - 1 - move.source
            ) // HOME_BOARD_POINTS

    return score
