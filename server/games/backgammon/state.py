"""Serializable state models for Backgammon."""

from dataclasses import dataclass, field
import random


# Board constants
NUM_POINTS = 24
CHECKERS_PER_PLAYER = 15

# Initial position: positive = Red (P1), negative = White (P2)
# Index 0 = point 1 (Red's perspective). Red's home = points 1-6 (indices 0-5).
# Standard backgammon: each player has 2 on 24pt, 5 on 13pt, 3 on 8pt, 5 on 6pt.
INITIAL_BOARD = [0] * 24
INITIAL_BOARD[23] = 2  # point 24: +2 Red
INITIAL_BOARD[12] = 5  # point 13: +5 Red
INITIAL_BOARD[7] = 3  # point 8: +3 Red
INITIAL_BOARD[5] = 5  # point 6: +5 Red
INITIAL_BOARD[0] = -2  # point 1: -2 White (White's 24-point)
INITIAL_BOARD[11] = -5  # point 12: -5 White (White's 13-point)
INITIAL_BOARD[16] = -3  # point 17: -3 White (White's 8-point)
INITIAL_BOARD[18] = -5  # point 19: -5 White (White's 6-point)


@dataclass
class BackgammonBoardState:
    """Board representation: signed integers per point + bar/off."""

    points: list[int] = field(default_factory=lambda: list(INITIAL_BOARD))
    bar_red: int = 0
    bar_white: int = 0
    off_red: int = 0
    off_white: int = 0


@dataclass
class BackgammonGameState:
    """Serializable game-level state for Backgammon."""

    board: BackgammonBoardState = field(default_factory=BackgammonBoardState)
    dice: list[int] = field(default_factory=list)
    dice_used: list[bool] = field(default_factory=list)
    turn_phase: str = "pre_roll"  # pre_roll | doubling | moving | turn_end
    current_color: str = "red"  # red | white
    selected_source: int | None = None  # -1=bar, 0-23=point, None=no selection
    moves_this_turn: list[dict] = field(default_factory=list)

    # Doubling cube
    cube_value: int = 1
    cube_owner: str = ""  # "" = centered, "red", "white"

    # Match play
    match_length: int = 1
    score_red: int = 0
    score_white: int = 0
    is_crawford: bool = False
    crawford_used: bool = False
    game_number: int = 1

    # Opening roll
    opening_roll: bool = True
    opening_die_red: int = 0
    opening_die_white: int = 0


def color_sign(color: str) -> int:
    """Return +1 for red, -1 for white."""
    return 1 if color == "red" else -1


def opponent_color(color: str) -> str:
    """Return the other color."""
    return "white" if color == "red" else "red"


def bar_count(state: BackgammonGameState, color: str) -> int:
    """Get bar count for a color."""
    return state.board.bar_red if color == "red" else state.board.bar_white


def off_count(state: BackgammonGameState, color: str) -> int:
    """Get borne off count for a color."""
    return state.board.off_red if color == "red" else state.board.off_white


def set_bar(state: BackgammonGameState, color: str, count: int) -> None:
    """Set bar count for a color."""
    if color == "red":
        state.board.bar_red = count
    else:
        state.board.bar_white = count


def set_off(state: BackgammonGameState, color: str, count: int) -> None:
    """Set borne off count for a color."""
    if color == "red":
        state.board.off_red = count
    else:
        state.board.off_white = count


def point_owner(state: BackgammonGameState, point_idx: int) -> str | None:
    """Return color owning a point, or None if empty."""
    val = state.board.points[point_idx]
    if val > 0:
        return "red"
    elif val < 0:
        return "white"
    return None


def point_count(state: BackgammonGameState, point_idx: int) -> int:
    """Return absolute checker count on a point."""
    return abs(state.board.points[point_idx])


def remaining_dice(state: BackgammonGameState) -> list[int]:
    """Return list of unused die values."""
    return [d for d, used in zip(state.dice, state.dice_used) if not used]


def remaining_dice_unique(state: BackgammonGameState) -> list[int]:
    """Return sorted unique unused die values."""
    return sorted(set(remaining_dice(state)))


def all_checkers_in_home(state: BackgammonGameState, color: str) -> bool:
    """Check if all checkers are in the home board (points 1-6 for that color)."""
    sign = color_sign(color)
    on_bar = bar_count(state, color)
    if on_bar > 0:
        return False
    # For red, home = points 1-6 (indices 0-5)
    # For white, home = points 19-24 (indices 18-23)
    for i in range(NUM_POINTS):
        val = state.board.points[i]
        if val * sign > 0:  # This color has checkers here
            if color == "red" and i > 5:
                return False
            if color == "white" and i < 18:
                return False
    return True


def pip_count(state: BackgammonGameState, color: str) -> int:
    """Calculate pip count for a color."""
    total = 0
    sign = color_sign(color)
    for i in range(NUM_POINTS):
        val = state.board.points[i]
        if val * sign > 0:
            count = abs(val)
            if color == "red":
                # Red moves from high points toward point 1 (off)
                # Pip = point number = i + 1
                total += count * (i + 1)
            else:
                # White moves from low points toward point 24 (off)
                # Pip = 25 - point number = 25 - (i + 1) = 24 - i
                total += count * (24 - i)
    # Bar checkers: 25 pips each
    total += bar_count(state, color) * 25
    return total


def point_number_for_player(point_idx: int, color: str) -> int:
    """Convert internal index to player-facing point number.

    Red sees index 0 as point 1, index 23 as point 24.
    White sees index 23 as point 1, index 0 as point 24.
    """
    if color == "red":
        return point_idx + 1
    else:
        return 24 - point_idx


def player_point_to_index(point_num: int, color: str) -> int:
    """Convert player-facing point number to internal index."""
    if color == "red":
        return point_num - 1
    else:
        return 24 - point_num


def roll_dice(rng: random.Random | None = None) -> tuple[int, int]:
    """Roll two dice."""
    r = rng or random
    return (r.randint(1, 6), r.randint(1, 6))  # nosec B311


def build_initial_game_state(match_length: int = 1) -> BackgammonGameState:
    """Build initial state for a new backgammon game."""
    return BackgammonGameState(
        board=BackgammonBoardState(points=list(INITIAL_BOARD)),
        match_length=match_length,
    )


def is_gammon(state: BackgammonGameState, loser_color: str) -> bool:
    """Check if the loser has been gammoned (no checkers borne off)."""
    return off_count(state, loser_color) == 0


def is_backgammon(state: BackgammonGameState, loser_color: str) -> bool:
    """Check if the loser has been backgammoned.

    Backgammon: loser has no checkers off AND has checkers on the bar
    or in the winner's home board.
    """
    if not is_gammon(state, loser_color):
        return False
    if bar_count(state, loser_color) > 0:
        return True
    sign = color_sign(loser_color)
    # Check if loser has checkers in winner's home board
    if loser_color == "red":
        # Red lost: check if red has checkers in white's home (indices 18-23)
        for i in range(18, 24):
            if state.board.points[i] * sign > 0:
                return True
    else:
        # White lost: check if white has checkers in red's home (indices 0-5)
        for i in range(0, 6):
            if state.board.points[i] * sign > 0:
                return True
    return False


def game_multiplier(state: BackgammonGameState, loser_color: str) -> int:
    """Calculate game multiplier (1=single, 2=gammon, 3=backgammon)."""
    if is_backgammon(state, loser_color):
        return 3
    if is_gammon(state, loser_color):
        return 2
    return 1
