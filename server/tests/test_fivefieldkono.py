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


# ----------------------------------------------------------------------------
# Task 2: moves
# ----------------------------------------------------------------------------

from ..games.fivefieldkono.moves import (  # noqa: E402
    Move,
    apply_move,
    generate_legal_moves,
    has_any_legal_move,
    is_winner,
    legal_destinations,
)
from ..games.fivefieldkono.state import (  # noqa: E402
    FiveFieldKonoState,
    Piece,
)


def _empty_state():
    return FiveFieldKonoState(board=[None] * 25, current_player_num=1)


def test_forward_diagonals_only_for_p1():
    state = _empty_state()
    src = cell_index(2, 2)  # C3, index 12
    state.board[src] = Piece(owner_id="p1", owner_num=1)
    dests = set(legal_destinations(state.board, src, 1))
    # P1 moves to row+1 diagonals only: (3,1)=16 and (3,3)=18
    assert dests == {cell_index(3, 1), cell_index(3, 3)}


def test_forward_diagonals_only_for_p2():
    state = _empty_state()
    src = cell_index(2, 2)
    state.board[src] = Piece(owner_id="p2", owner_num=2)
    dests = set(legal_destinations(state.board, src, 2))
    # P2 moves to row-1 diagonals only: (1,1)=6 and (1,3)=8
    assert dests == {cell_index(1, 1), cell_index(1, 3)}


def test_blocked_destination_is_illegal():
    state = _empty_state()
    src = cell_index(2, 2)
    state.board[src] = Piece(owner_id="p1", owner_num=1)
    state.board[cell_index(3, 1)] = Piece(owner_id="p1", owner_num=1)  # own blocks
    state.board[cell_index(3, 3)] = Piece(owner_id="p2", owner_num=2)  # opp blocks
    assert legal_destinations(state.board, src, 1) == []


def test_edge_column_has_single_diagonal():
    state = _empty_state()
    src = cell_index(2, 0)  # A3, col 0 -> only (3,1)
    state.board[src] = Piece(owner_id="p1", owner_num=1)
    assert set(legal_destinations(state.board, src, 1)) == {cell_index(3, 1)}


def test_apply_move_moves_piece():
    state = _empty_state()
    src = cell_index(2, 2)
    dst = cell_index(3, 3)
    state.board[src] = Piece(owner_id="p1", owner_num=1)
    apply_move(state, Move(source=src, destination=dst))
    assert state.board[src] is None
    assert state.board[dst].owner_id == "p1"


def test_win_when_all_pieces_on_targets():
    state = _empty_state()
    for idx in TARGET_CELLS[1]:
        state.board[idx] = Piece(owner_id="p1", owner_num=1)
    assert is_winner(state, 1) is True


def test_stuck_player_has_no_moves():
    state = _empty_state()
    # A single P1 piece at top row can never move forward (row+1 off board).
    state.board[cell_index(4, 2)] = Piece(owner_id="p1", owner_num=1)
    assert has_any_legal_move(state, 1) is False


def test_generate_legal_moves_from_initial_state():
    state = build_initial_state("p1", "p2")
    p1_moves = generate_legal_moves(state, 1)
    # Row-1 has empty gaps at 6,7,8, so every P1 start piece has at least one
    # empty forward diagonal at the opening.
    assert {m.source for m in p1_moves} == set(START_CELLS[1])
    # Player 2 mirrors: every P2 start piece can also move at the opening.
    assert {m.source for m in generate_legal_moves(state, 2)} == set(START_CELLS[2])


# ----------------------------------------------------------------------------
# Task 3: game skeleton, registration, rendering
# ----------------------------------------------------------------------------

from ..games import GameRegistry  # noqa: E402
from ..games.fivefieldkono.game import (  # noqa: E402
    FiveFieldKonoGame,
    FiveFieldKonoOptions,
)
from ..users.test_user import MockUser  # noqa: E402


def make_kono(*, start: bool = False, player_count: int = 2) -> FiveFieldKonoGame:
    game = FiveFieldKonoGame(options=FiveFieldKonoOptions())
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def test_game_is_registered():
    assert GameRegistry.get("fivefieldkono") is FiveFieldKonoGame


def test_metadata():
    assert FiveFieldKonoGame.get_type() == "fivefieldkono"
    assert FiveFieldKonoGame.get_category() == "board"
    assert FiveFieldKonoGame.get_min_players() == 2
    assert FiveFieldKonoGame.get_max_players() == 2


def test_on_start_sets_up_board_and_grid():
    game = make_kono(start=True)
    assert game.status == "playing"
    assert game.grid_rows == 5 and game.grid_cols == 5
    assert sum(1 for c in game.state.board if c is not None) == 14
    assert game.current_player is not None


def test_game_name_localized():
    assert Localization.get("en", "game-name-fivefieldkono") == "Five Field Kono"


def test_cell_label_reads_coordinate():
    game = make_kono(start=True)
    p1 = game._get_player_by_num(1)
    label = game.get_cell_label(0, 0, p1, "en")
    assert "A1" in label
