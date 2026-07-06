"""Bot AI for Five Field Kono — depth-limited negamax."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from ...game_utils.grid_mixin import grid_cell_id
from .moves import (
    Move,
    apply_move,
    generate_legal_moves,
    has_any_legal_move,
    is_winner,
)
from .state import (
    FORWARD_DROW,
    TARGET_CELLS,
    FiveFieldKonoState,
    cell_rowcol,
    opponent_num,
)

if TYPE_CHECKING:
    from .game import FiveFieldKonoGame, FiveFieldKonoPlayer

SEARCH_DEPTH = 4
WIN_SCORE = 100_000


def bot_think(game: "FiveFieldKonoGame", player: "FiveFieldKonoPlayer") -> str | None:
    if game.state.current_player_num != player.player_num:
        return None
    selected = game.selected_square.get(player.id)
    if selected is not None:
        # Second click: play the stored destination for the selected source.
        dest = game.bot_move_targets.get(player.id)
        if dest is None:
            best = choose_move(game.state, player.player_num)
            if best is None:
                return None
            dest = best.destination
        row, col = cell_rowcol(dest)
        return grid_cell_id(row, col)
    best = choose_move(game.state, player.player_num)
    if best is None:
        return None
    game.bot_move_targets[player.id] = best.destination
    row, col = cell_rowcol(best.source)
    return grid_cell_id(row, col)


def choose_move(state: FiveFieldKonoState, player_num: int) -> Move | None:
    moves = generate_legal_moves(state, player_num)
    if not moves:
        return None
    best_move = moves[0]
    best_score = float("-inf")
    for move in moves:
        child = copy.deepcopy(state)
        apply_move(child, move)
        score = -_negamax(
            child, opponent_num(player_num), SEARCH_DEPTH - 1,
            float("-inf"), float("inf"),
        )
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


def _negamax(state, player_num, depth, alpha, beta) -> float:
    prev = opponent_num(player_num)
    if is_winner(state, prev):
        return -WIN_SCORE  # the player who just moved already won
    if not has_any_legal_move(state, player_num):
        return -WIN_SCORE  # side to move is stuck -> loses
    if depth <= 0:
        return _evaluate(state, player_num)
    value = float("-inf")
    for move in generate_legal_moves(state, player_num):
        child = copy.deepcopy(state)
        apply_move(child, move)
        value = max(
            value,
            -_negamax(child, opponent_num(player_num), depth - 1, -beta, -alpha),
        )
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    return value


def _evaluate(state, player_num: int) -> float:
    """Positive = good for `player_num`. Progress toward targets minus opp."""
    return _side_progress(state, player_num) - _side_progress(
        state, opponent_num(player_num)
    )


def _side_progress(state, num: int) -> float:
    targets = TARGET_CELLS[num]
    drow = FORWARD_DROW[num]
    score = 0.0
    for idx, piece in enumerate(state.board):
        if piece is None or piece.owner_num != num:
            continue
        if idx in targets:
            score += 20.0
            continue
        row, _ = cell_rowcol(idx)
        # Forward progress: rows advanced toward the goal edge.
        score += row if drow > 0 else (4 - row)
    return score
