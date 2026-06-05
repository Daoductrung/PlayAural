"""Legal move generation and application for Backgammon."""

from __future__ import annotations

from dataclasses import dataclass

from .state import (
    BackgammonGameState,
    all_checkers_in_home,
    bar_count,
    color_sign,
    opponent_color,
    point_count,
    point_owner,
    remaining_dice,
    set_bar,
    set_off,
    off_count,
)


@dataclass(frozen=True)
class BackgammonMove:
    """A single sub-move (one die)."""

    source: int  # -1=bar, 0-23=point index
    destination: int  # 0-23=point index, 24=bear off
    die_value: int
    is_hit: bool = False
    is_bear_off: bool = False


def generate_legal_moves(
    state: BackgammonGameState, color: str, die_value: int
) -> list[BackgammonMove]:
    """Generate all legal moves for a single die value.

    Args:
        state: Current game state.
        color: "red" or "white".
        die_value: The die value to use (1-6).

    Returns:
        List of legal BackgammonMove objects.
    """
    sign = color_sign(color)
    opp = opponent_color(color)
    moves: list[BackgammonMove] = []

    # Must enter from bar first
    on_bar = bar_count(state, color)
    if on_bar > 0:
        # Red enters on points 24..19 (indices 23..18), die 1 -> index 23
        # White enters on points 1..6 (indices 0..5), die 1 -> index 0
        if color == "red":
            dest_idx = 24 - die_value
        else:
            dest_idx = die_value - 1

        dest_val = state.board.points[dest_idx]
        opp_sign = color_sign(opp)
        # Can land if: empty, own checkers, or exactly 1 opponent (hit)
        if dest_val * opp_sign <= 1:
            is_hit = dest_val * opp_sign == 1
            moves.append(
                BackgammonMove(
                    source=-1,
                    destination=dest_idx,
                    die_value=die_value,
                    is_hit=is_hit,
                )
            )
        return moves

    # Check if we can bear off
    can_bear_off = all_checkers_in_home(state, color)

    for i in range(24):
        val = state.board.points[i]
        if val * sign <= 0:
            continue  # No own checkers here

        # Calculate destination
        if color == "red":
            # Red moves from high index toward 0, then off
            dest_idx = i - die_value
        else:
            # White moves from low index toward 23, then off
            dest_idx = i + die_value

        # Bear off
        if color == "red" and dest_idx < 0:
            if not can_bear_off:
                continue
            # Exact bear off or highest point
            if dest_idx == -1:
                moves.append(
                    BackgammonMove(
                        source=i,
                        destination=24,
                        die_value=die_value,
                        is_bear_off=True,
                    )
                )
            else:
                # Can bear off with higher die only if no checkers on higher points
                if _is_highest_checker(state, color, i):
                    moves.append(
                        BackgammonMove(
                            source=i,
                            destination=24,
                            die_value=die_value,
                            is_bear_off=True,
                        )
                    )
            continue

        if color == "white" and dest_idx > 23:
            if not can_bear_off:
                continue
            if dest_idx == 24:
                moves.append(
                    BackgammonMove(
                        source=i,
                        destination=24,
                        die_value=die_value,
                        is_bear_off=True,
                    )
                )
            else:
                if _is_highest_checker(state, color, i):
                    moves.append(
                        BackgammonMove(
                            source=i,
                            destination=24,
                            die_value=die_value,
                            is_bear_off=True,
                        )
                    )
            continue

        if dest_idx < 0 or dest_idx > 23:
            continue

        # Normal move - check destination
        dest_val = state.board.points[dest_idx]
        opp_sign = color_sign(opp)
        if dest_val * opp_sign > 1:
            continue  # Blocked by 2+ opponent checkers

        is_hit = dest_val * opp_sign == 1
        moves.append(
            BackgammonMove(
                source=i,
                destination=dest_idx,
                die_value=die_value,
                is_hit=is_hit,
            )
        )

    return moves


def _is_highest_checker(state: BackgammonGameState, color: str, point_idx: int) -> bool:
    """Check if point_idx holds the furthest-from-off checker for bearing off.

    For red (moving toward index 0): no checkers on indices > point_idx
    For white (moving toward index 23): no checkers on indices < point_idx
    """
    sign = color_sign(color)
    if color == "red":
        for i in range(point_idx + 1, 6):
            if state.board.points[i] * sign > 0:
                return False
    else:
        for i in range(18, point_idx):
            if state.board.points[i] * sign > 0:
                return False
    return True


def apply_move(state: BackgammonGameState, move: BackgammonMove, color: str) -> None:
    """Apply a sub-move to the game state. Mutates state."""
    sign = color_sign(color)
    opp = opponent_color(color)

    # Remove checker from source
    if move.source == -1:
        # From bar
        set_bar(state, color, bar_count(state, color) - 1)
    else:
        state.board.points[move.source] -= sign

    # Place checker at destination
    if move.is_bear_off:
        set_off(state, color, off_count(state, color) + 1)
    else:
        # Hit opponent if present
        if move.is_hit:
            opp_sign = color_sign(opp)
            state.board.points[move.destination] -= opp_sign
            set_bar(state, opp, bar_count(state, opp) + 1)
        state.board.points[move.destination] += sign

    # Record the move
    state.moves_this_turn.append(
        {
            "source": move.source,
            "destination": move.destination,
            "die_value": move.die_value,
            "is_hit": move.is_hit,
            "is_bear_off": move.is_bear_off,
        }
    )


def undo_last_move(state: BackgammonGameState, color: str) -> BackgammonMove | None:
    """Undo the last sub-move. Returns the undone move or None."""
    if not state.moves_this_turn:
        return None

    move_dict = state.moves_this_turn.pop()
    move = BackgammonMove(**move_dict)
    sign = color_sign(color)
    opp = opponent_color(color)

    # Reverse destination
    if move.is_bear_off:
        set_off(state, color, off_count(state, color) - 1)
    else:
        state.board.points[move.destination] -= sign
        if move.is_hit:
            opp_sign = color_sign(opp)
            state.board.points[move.destination] += opp_sign
            set_bar(state, opp, bar_count(state, opp) - 1)

    # Reverse source
    if move.source == -1:
        set_bar(state, color, bar_count(state, color) + 1)
    else:
        state.board.points[move.source] += sign

    return move


def must_use_both_dice(
    state: BackgammonGameState, color: str, dice_values: list[int]
) -> list[int] | None:
    """Enforce the "must use both dice" rule.

    If both dice can be used, return None (no restriction).
    If only one die can be used, return [larger_die] to enforce using the larger.
    If neither can be used, return [].
    """
    if len(dice_values) != 2 or dice_values[0] == dice_values[1]:
        return None  # Doubles or single die - no special rule

    d1, d2 = dice_values
    moves_d1 = generate_legal_moves(state, color, d1)
    moves_d2 = generate_legal_moves(state, color, d2)

    if not moves_d1 and not moves_d2:
        return []

    if not moves_d1:
        return [d2]
    if not moves_d2:
        return [d1]

    # Both have moves - check if using d1 first allows d2 after, and vice versa
    can_use_both_d1_first = False
    for m1 in moves_d1:
        # Simulate applying m1
        _apply_temp(state, m1, color)
        if generate_legal_moves(state, color, d2):
            can_use_both_d1_first = True
        _undo_temp(state, m1, color)
        if can_use_both_d1_first:
            break

    can_use_both_d2_first = False
    for m2 in moves_d2:
        _apply_temp(state, m2, color)
        if generate_legal_moves(state, color, d1):
            can_use_both_d2_first = True
        _undo_temp(state, m2, color)
        if can_use_both_d2_first:
            break

    if can_use_both_d1_first or can_use_both_d2_first:
        return None  # Can use both

    # Only one die can be used - must use the larger
    return [max(d1, d2)]


def _apply_temp(state: BackgammonGameState, move: BackgammonMove, color: str) -> None:
    """Temporarily apply a move (without recording to moves_this_turn)."""
    sign = color_sign(color)
    opp = opponent_color(color)

    if move.source == -1:
        set_bar(state, color, bar_count(state, color) - 1)
    else:
        state.board.points[move.source] -= sign

    if move.is_bear_off:
        set_off(state, color, off_count(state, color) + 1)
    else:
        if move.is_hit:
            opp_sign = color_sign(opp)
            state.board.points[move.destination] -= opp_sign
            set_bar(state, opp, bar_count(state, opp) + 1)
        state.board.points[move.destination] += sign


def _undo_temp(state: BackgammonGameState, move: BackgammonMove, color: str) -> None:
    """Undo a temporary move."""
    sign = color_sign(color)
    opp = opponent_color(color)

    if move.is_bear_off:
        set_off(state, color, off_count(state, color) - 1)
    else:
        state.board.points[move.destination] -= sign
        if move.is_hit:
            opp_sign = color_sign(opp)
            state.board.points[move.destination] += opp_sign
            set_bar(state, opp, bar_count(state, opp) - 1)

    if move.source == -1:
        set_bar(state, color, bar_count(state, color) + 1)
    else:
        state.board.points[move.source] += sign


def has_any_legal_move(state: BackgammonGameState, color: str) -> bool:
    """Check if any legal move exists for any remaining die."""
    for die_val in remaining_dice(state):
        if generate_legal_moves(state, color, die_val):
            return True
    return False
