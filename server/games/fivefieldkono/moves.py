"""Move generation and application for Five Field Kono."""

from __future__ import annotations

from dataclasses import dataclass

from .state import (
    BOARD_SIZE,
    FORWARD_DROW,
    TARGET_CELLS,
    FiveFieldKonoState,
    cell_index,
    cell_rowcol,
)


@dataclass(frozen=True)
class Move:
    source: int
    destination: int


def legal_destinations(board, source: int, player_num: int) -> list[int]:
    """Empty forward-diagonal cells reachable from `source`. No captures."""
    piece = board[source]
    if piece is None or piece.owner_num != player_num:
        return []
    row, col = cell_rowcol(source)
    drow = FORWARD_DROW[player_num]
    dests: list[int] = []
    for dcol in (-1, 1):
        nr, nc = row + drow, col + dcol
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            idx = cell_index(nr, nc)
            if board[idx] is None:
                dests.append(idx)
    return dests


def generate_legal_moves(state: FiveFieldKonoState, player_num: int) -> list[Move]:
    moves: list[Move] = []
    for src, piece in enumerate(state.board):
        if piece is None or piece.owner_num != player_num:
            continue
        for dst in legal_destinations(state.board, src, player_num):
            moves.append(Move(source=src, destination=dst))
    return moves


def apply_move(state: FiveFieldKonoState, move: Move) -> None:
    piece = state.board[move.source]
    state.board[move.source] = None
    state.board[move.destination] = piece


def has_any_legal_move(state: FiveFieldKonoState, player_num: int) -> bool:
    for src, piece in enumerate(state.board):
        if piece is None or piece.owner_num != player_num:
            continue
        if legal_destinations(state.board, src, player_num):
            return True
    return False


def is_winner(state: FiveFieldKonoState, player_num: int) -> bool:
    cells = {
        idx
        for idx, piece in enumerate(state.board)
        if piece is not None and piece.owner_num == player_num
    }
    return cells == set(TARGET_CELLS[player_num])
