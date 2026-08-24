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
    """Return any die-value restriction imposed by the complete remaining roll.

    This compatibility helper is intentionally derived from
    :func:`generate_legal_turn_moves`.  A die-value-only restriction cannot
    identify every illegal turn prefix, so callers that execute moves must use
    that function directly.
    """
    legal_moves = generate_legal_turn_moves(state, color, dice_values)
    if not legal_moves:
        return []
    available_values = set(dice_values)
    legal_values = {move.die_value for move in legal_moves}
    if legal_values == available_values:
        return None
    return sorted(legal_values)


def generate_legal_turn_moves(
    state: BackgammonGameState,
    color: str,
    dice_values: list[int] | None = None,
) -> list[BackgammonMove]:
    """Generate legal next moves while enforcing the complete-roll rules.

    Backgammon requires a player to use as many dice as the position permits.
    When only one of two different dice can be used, the higher die is required.
    Consequently, a move that is legal for one die in isolation may still be an
    illegal first move if it prevents another die from being played.  This
    function filters those turn-stranding prefixes for both humans and bots.
    """
    dice = list(remaining_dice(state) if dice_values is None else dice_values)
    if not dice:
        return []

    cache: dict[tuple, int] = {}
    maximum = _max_playable_dice(state, color, dice, cache)
    if maximum == 0:
        return []

    legal: list[BackgammonMove] = []
    for die_value in sorted(set(dice)):
        remaining = list(dice)
        remaining.remove(die_value)
        for move in generate_legal_moves(state, color, die_value):
            _apply_temp(state, move, color)
            playable_after = _max_playable_dice(state, color, remaining, cache)
            _undo_temp(state, move, color)
            if 1 + playable_after == maximum:
                legal.append(move)

    # With two different dice and room to play only one, the larger value is
    # mandatory even if the lower die also has an isolated legal move.
    if maximum == 1 and len(dice) == 2 and dice[0] != dice[1]:
        higher = max(dice)
        higher_moves = [move for move in legal if move.die_value == higher]
        if higher_moves:
            legal = higher_moves

    return legal


def _max_playable_dice(
    state: BackgammonGameState,
    color: str,
    dice_values: list[int],
    cache: dict[tuple, int],
) -> int:
    """Return the maximum number of remaining dice playable from ``state``."""
    if not dice_values:
        return 0

    board = state.board
    key = (
        tuple(board.points),
        board.bar_red,
        board.bar_white,
        board.off_red,
        board.off_white,
        color,
        tuple(sorted(dice_values)),
    )
    cached = cache.get(key)
    if cached is not None:
        return cached

    best = 0
    for die_value in set(dice_values):
        remaining = list(dice_values)
        remaining.remove(die_value)
        for move in generate_legal_moves(state, color, die_value):
            _apply_temp(state, move, color)
            best = max(best, 1 + _max_playable_dice(state, color, remaining, cache))
            _undo_temp(state, move, color)
            if best == len(dice_values):
                cache[key] = best
                return best

    cache[key] = best
    return best


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
    return bool(generate_legal_turn_moves(state, color))
