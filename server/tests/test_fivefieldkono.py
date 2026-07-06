"""Tests for Five Field Kono."""

from pathlib import Path

from ..games.fivefieldkono.state import (
    NUM_CELLS,
    PIECES_PER_PLAYER,
    START_CELLS,
    TARGET_CELLS,
    build_initial_state,
    cell_index,
    cell_rowcol,
    opponent_num,
    player_piece_cells,
)
from ..messages.localization import Localization

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def test_start_cells_are_correct():
    assert START_CELLS[1] == frozenset({0, 1, 2, 3, 4, 5, 9})
    assert START_CELLS[2] == frozenset({20, 21, 22, 23, 24, 15, 19})


def test_targets_are_opponent_start_cells():
    assert TARGET_CELLS[1] == START_CELLS[2]
    assert TARGET_CELLS[2] == START_CELLS[1]


def test_parity_matches_between_start_and_target():
    # Diagonal moves preserve (row+col) parity; each side must have matching
    # even/odd counts so every piece can reach a target on its own diagonal.
    def parity_counts(cells):
        even = sum(1 for c in cells if (c // 5 + c % 5) % 2 == 0)
        return even, len(cells) - even
    assert parity_counts(START_CELLS[1]) == parity_counts(TARGET_CELLS[1])
    assert parity_counts(START_CELLS[2]) == parity_counts(TARGET_CELLS[2])


def test_initial_state_places_seven_pieces_each():
    state = build_initial_state("p1", "p2")
    assert len(state.board) == NUM_CELLS
    p1 = player_piece_cells(state, "p1")
    p2 = player_piece_cells(state, "p2")
    assert p1 == START_CELLS[1]
    assert p2 == START_CELLS[2]
    assert len(p1) == PIECES_PER_PLAYER
    assert len(p2) == PIECES_PER_PLAYER


def test_cell_index_roundtrip_and_opponent():
    assert cell_index(1, 4) == 9
    assert cell_rowcol(9) == (1, 4)
    assert opponent_num(1) == 2 and opponent_num(2) == 1
