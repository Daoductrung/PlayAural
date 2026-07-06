"""Serializable state models for Five Field Kono."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin

BOARD_SIZE = 5
NUM_CELLS = BOARD_SIZE * BOARD_SIZE  # 25
PIECES_PER_PLAYER = 7

# Player 1 ("south") occupies rows 0-1 and moves toward higher rows.
# Player 2 ("north") occupies rows 3-4 and moves toward lower rows.
START_CELLS: dict[int, frozenset[int]] = {
    1: frozenset({0, 1, 2, 3, 4, 5, 9}),
    2: frozenset({20, 21, 22, 23, 24, 15, 19}),
}
# Win by occupying the opponent's start cells.
TARGET_CELLS: dict[int, frozenset[int]] = {
    1: START_CELLS[2],
    2: START_CELLS[1],
}
# Forward row delta per player (P1 goes up in index, P2 goes down).
FORWARD_DROW: dict[int, int] = {1: 1, 2: -1}


def cell_index(row: int, col: int) -> int:
    return row * BOARD_SIZE + col


def cell_rowcol(index: int) -> tuple[int, int]:
    return divmod(index, BOARD_SIZE)


def opponent_num(player_num: int) -> int:
    return 3 - player_num


@dataclass
class Piece(DataClassJSONMixin):
    owner_id: str
    owner_num: int


@dataclass
class FiveFieldKonoState(DataClassJSONMixin):
    board: list[Piece | None] = field(default_factory=lambda: [None] * NUM_CELLS)
    current_player_num: int = 1


def build_initial_state(p1_id: str, p2_id: str) -> FiveFieldKonoState:
    state = FiveFieldKonoState()
    for idx in START_CELLS[1]:
        state.board[idx] = Piece(owner_id=p1_id, owner_num=1)
    for idx in START_CELLS[2]:
        state.board[idx] = Piece(owner_id=p2_id, owner_num=2)
    return state


def player_piece_cells(state: FiveFieldKonoState, owner_id: str) -> set[int]:
    return {
        idx
        for idx, piece in enumerate(state.board)
        if piece is not None and piece.owner_id == owner_id
    }
