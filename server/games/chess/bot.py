"""Lightweight Chess bot based on the example project's single-ply evaluator."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import ChessGame, ChessPlayer, ChessPiece


PIECE_VALUES = {
    "pawn": 100,
    "knight": 320,
    "bishop": 330,
    "rook": 500,
    "queen": 900,
    "king": 20000,
}

PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0,
]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,
]

KING_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,
]

PIECE_SQUARE_TABLES = {
    "pawn": PAWN_TABLE,
    "knight": KNIGHT_TABLE,
    "bishop": BISHOP_TABLE,
    "rook": ROOK_TABLE,
    "queen": QUEEN_TABLE,
    "king": KING_TABLE,
}


def _pst_index(square: int, color: str) -> int:
    rank = square // 8
    file_index = square % 8
    if color == "white":
        return (7 - rank) * 8 + file_index
    return rank * 8 + file_index


def _piece_value(piece: "ChessPiece | None") -> int:
    if piece is None:
        return 0
    return PIECE_VALUES.get(piece.kind, 0)


def _score_move(game: "ChessGame", move: tuple[int, int], color: str) -> int:
    from_sq, to_sq = move
    piece = game.board[from_sq]
    target = game.board[to_sq]
    if piece is None:
        return 0

    score = 0

    if target is not None:
        score += _piece_value(target) * 10 - _piece_value(piece)

    if piece.kind == "pawn" and to_sq == game.en_passant_target and (from_sq % 8) != (to_sq % 8):
        score += PIECE_VALUES["pawn"] * 10

    pst = PIECE_SQUARE_TABLES.get(piece.kind)
    if pst is not None:
        old_pst = pst[_pst_index(from_sq, color)]
        new_pst = pst[_pst_index(to_sq, color)]
        score += (new_pst - old_pst) * 2

    is_castle, _ = game._is_castling_move(from_sq, to_sq, piece)
    if is_castle:
        score += 60

    if piece.kind == "pawn":
        target_rank = to_sq // 8
        if (color == "white" and target_rank == 7) or (color == "black" and target_rank == 0):
            score += PIECE_VALUES["queen"]

    saved = game.save_position()
    outcome = game._apply_move_core(from_sq, to_sq, promotion="queen", auto_promote_to_queen=True)
    opponent = "black" if color == "white" else "white"
    if outcome.get("needs_promotion"):
        game.board[to_sq] = type(piece)("queen", color, has_moved=True)
    if game.is_in_check(opponent):
        score += 50
        if game.is_checkmate(opponent):
            score += 100000
    game.restore_position(saved)

    score += random.randint(-5, 5)  # nosec B311
    return score


def find_best_move(game: "ChessGame", player: "ChessPlayer") -> tuple[int, int] | None:
    moves = game.get_legal_moves(player.color)
    if not moves:
        return None

    scored_moves: list[tuple[int, tuple[int, int]]] = []
    for move in moves:
        scored_moves.append((_score_move(game, move, player.color), move))

    scored_moves.sort(key=lambda item: item[0], reverse=True)
    top_score = scored_moves[0][0]
    top_moves = [move for score, move in scored_moves if score >= top_score - 20]
    return random.choice(top_moves)  # nosec B311


def bot_think(game: "ChessGame", player: "ChessPlayer") -> str | None:
    if game.promotion_pending and game.promotion_player_id == player.id:
        return "promote_queen"

    if game.draw_offer_from and game.draw_offer_from != player.id:
        my_material = 0
        opponent_material = 0
        for piece in game.board:
            if piece is None:
                continue
            if piece.color == player.color:
                my_material += _piece_value(piece)
            else:
                opponent_material += _piece_value(piece)
        if my_material < opponent_material - 200:
            return "accept_draw"
        return "decline_draw"

    if game.undo_request_from and game.undo_request_from != player.id:
        return "decline_undo"

    if game.current_player != player:
        return None

    if player.id in game.bot_move_targets and game.selected_square.get(player.id) is not None:
        to_sq = game.bot_move_targets.pop(player.id)
        row, col = game.square_to_view(player, to_sq)
        return game.grid_cell_action_id(row, col)

    move = find_best_move(game, player)
    if move is None:
        return None

    from_sq, to_sq = move
    game.bot_move_targets[player.id] = to_sq
    row, col = game.square_to_view(player, from_sq)
    return game.grid_cell_action_id(row, col)
