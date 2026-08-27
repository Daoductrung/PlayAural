"""Serializable state models for Backgammon."""

from dataclasses import dataclass, field
import random


# Board constants
NUM_POINTS = 24
CHECKERS_PER_PLAYER = 15
HOME_BOARD_POINTS = 6
BAR_SOURCE = -1
BEAR_OFF_DESTINATION = NUM_POINTS
DIE_MIN_VALUE = 1
DIE_MAX_VALUE = 6

DEFAULT_MATCH_LENGTH = 1
MIN_MATCH_LENGTH = 1
MAX_MATCH_LENGTH = 25
INITIAL_CUBE_VALUE = 1
CUBE_DOUBLE_FACTOR = 2
SINGLE_GAME_MULTIPLIER = 1
GAMMON_MULTIPLIER = 2
BACKGAMMON_MULTIPLIER = 3

COLOR_RED = "red"
COLOR_WHITE = "white"
COLORS = (COLOR_RED, COLOR_WHITE)

PHASE_PRE_ROLL = "pre_roll"
PHASE_DOUBLING = "doubling"
PHASE_MOVING = "moving"

# Standard player-relative starting points and checker counts. Positive board
# values are Red and negative values are White; their layouts mirror each other.
STARTING_POSITION = ((24, 2), (13, 5), (8, 3), (6, 5))
INITIAL_BOARD = [0] * NUM_POINTS
for _player_point, _checker_count in STARTING_POSITION:
    INITIAL_BOARD[_player_point - 1] = _checker_count
    INITIAL_BOARD[NUM_POINTS - _player_point] = -_checker_count


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
    turn_phase: str = PHASE_PRE_ROLL
    current_color: str = COLOR_RED
    moves_this_turn: list[dict] = field(default_factory=list)

    # Doubling cube
    cube_value: int = INITIAL_CUBE_VALUE
    cube_owner: str = ""  # "" = centered, "red", "white"

    # Match play
    match_length: int = DEFAULT_MATCH_LENGTH
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
    if color == COLOR_RED:
        return 1
    if color == COLOR_WHITE:
        return -1
    raise ValueError(f"Unknown backgammon color: {color!r}")


def opponent_color(color: str) -> str:
    """Return the other color."""
    if color == COLOR_RED:
        return COLOR_WHITE
    if color == COLOR_WHITE:
        return COLOR_RED
    raise ValueError(f"Unknown backgammon color: {color!r}")


def bar_count(state: BackgammonGameState, color: str) -> int:
    """Get bar count for a color."""
    color_sign(color)
    return state.board.bar_red if color == COLOR_RED else state.board.bar_white


def off_count(state: BackgammonGameState, color: str) -> int:
    """Get borne off count for a color."""
    color_sign(color)
    return state.board.off_red if color == COLOR_RED else state.board.off_white


def set_bar(state: BackgammonGameState, color: str, count: int) -> None:
    """Set bar count for a color."""
    color_sign(color)
    if color == COLOR_RED:
        state.board.bar_red = count
    else:
        state.board.bar_white = count


def set_off(state: BackgammonGameState, color: str, count: int) -> None:
    """Set borne off count for a color."""
    color_sign(color)
    if color == COLOR_RED:
        state.board.off_red = count
    else:
        state.board.off_white = count


def point_owner(state: BackgammonGameState, point_idx: int) -> str | None:
    """Return color owning a point, or None if empty."""
    val = state.board.points[point_idx]
    if val > 0:
        return COLOR_RED
    elif val < 0:
        return COLOR_WHITE
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


def is_board_point(point_idx: int) -> bool:
    """Return whether an internal point index is on the board."""
    return 0 <= point_idx < NUM_POINTS


def is_home_point(point_idx: int, color: str) -> bool:
    """Return whether an internal point lies in ``color``'s home board."""
    color_sign(color)
    if color == COLOR_RED:
        return 0 <= point_idx < HOME_BOARD_POINTS
    return NUM_POINTS - HOME_BOARD_POINTS <= point_idx < NUM_POINTS


def is_opponent_home_point(point_idx: int, color: str) -> bool:
    """Return whether an internal point lies in the opponent's home board."""
    return is_home_point(point_idx, opponent_color(color))


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
            if not is_home_point(i, color):
                return False
    return True


def outside_home_count(state: BackgammonGameState, color: str) -> int:
    """Return the number of checkers outside a color's home board.

    Checkers on the bar are reported separately because they are useful context
    when explaining why bearing off is unavailable.
    """
    sign = color_sign(color)
    if color == COLOR_RED:
        outside_points = range(HOME_BOARD_POINTS, NUM_POINTS)
    else:
        outside_points = range(0, NUM_POINTS - HOME_BOARD_POINTS)
    return sum(
        abs(state.board.points[index])
        for index in outside_points
        if state.board.points[index] * sign > 0
    )


def pip_count(state: BackgammonGameState, color: str) -> int:
    """Calculate pip count for a color."""
    total = 0
    sign = color_sign(color)
    for i in range(NUM_POINTS):
        val = state.board.points[i]
        if val * sign > 0:
            count = abs(val)
            if color == COLOR_RED:
                # Red moves from high points toward point 1 (off)
                # Pip = point number = i + 1
                total += count * (i + 1)
            else:
                # White moves from low points toward point 24 (off)
                # Pip = 25 - point number = 25 - (i + 1) = 24 - i
                total += count * (NUM_POINTS - i)
    # Bar checkers: 25 pips each
    total += bar_count(state, color) * (NUM_POINTS + 1)
    return total


def point_number_for_player(point_idx: int, color: str) -> int:
    """Convert internal index to player-facing point number.

    Red sees index 0 as point 1, index 23 as point 24.
    White sees index 23 as point 1, index 0 as point 24.
    """
    color_sign(color)
    if color == COLOR_RED:
        return point_idx + 1
    else:
        return NUM_POINTS - point_idx


def player_point_to_index(point_num: int, color: str) -> int:
    """Convert player-facing point number to internal index."""
    color_sign(color)
    if color == COLOR_RED:
        return point_num - 1
    else:
        return NUM_POINTS - point_num


def roll_dice(rng: random.Random | None = None) -> tuple[int, int]:
    """Roll two dice."""
    r = rng or random
    return (
        r.randint(DIE_MIN_VALUE, DIE_MAX_VALUE),
        r.randint(DIE_MIN_VALUE, DIE_MAX_VALUE),
    )  # nosec B311


def build_initial_game_state(
    match_length: int = DEFAULT_MATCH_LENGTH,
) -> BackgammonGameState:
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
    return any(
        state.board.points[i] * sign > 0
        for i in range(NUM_POINTS)
        if is_opponent_home_point(i, loser_color)
    )


def game_multiplier(state: BackgammonGameState, loser_color: str) -> int:
    """Calculate game multiplier (1=single, 2=gammon, 3=backgammon)."""
    if is_backgammon(state, loser_color):
        return BACKGAMMON_MULTIPLIER
    if is_gammon(state, loser_color):
        return GAMMON_MULTIPLIER
    return SINGLE_GAME_MULTIPLIER
