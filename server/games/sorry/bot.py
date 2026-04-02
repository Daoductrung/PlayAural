"""Bot move selection for Sorry."""

from copy import deepcopy

from .moves import SorryMove, apply_move
from .rules import SorryRulesProfile
from .state import (
    SAFETY_LENGTH,
    SorryGameState,
    SorryPlayerState,
    TRACK_LENGTH,
    clockwise_distance,
)


def _track_threat_count(
    state: SorryGameState,
    player_id: str,
    target_track: int,
) -> int:
    threats = 0
    for opponent_id, opponent_state in state.player_states.items():
        if opponent_id == player_id:
            continue
        for pawn in opponent_state.pawns:
            if pawn.zone != "track" or pawn.track_position is None:
                continue
            forward = clockwise_distance(pawn.track_position, target_track)
            backward = clockwise_distance(target_track, pawn.track_position)
            if 1 <= forward <= 12:
                threats += 1
            elif 1 <= backward <= 4:
                threats += 1
    return threats


def _pawn_progress(player_state: SorryPlayerState, pawn_index: int) -> int:
    if pawn_index < 1 or pawn_index > len(player_state.pawns):
        return 0
    pawn = player_state.pawns[pawn_index - 1]
    if pawn.zone == "start":
        return 0
    if pawn.zone == "track":
        if pawn.track_position is None:
            return 0
        return 1 + clockwise_distance(player_state.start_track, pawn.track_position)
    if pawn.zone == "home_path":
        return TRACK_LENGTH + max(0, pawn.home_steps)
    if pawn.zone == "home":
        return TRACK_LENGTH + SAFETY_LENGTH + 1
    return 0


def _moved_pawn_indexes(move: SorryMove) -> list[int]:
    indexes: list[int] = []
    if move.pawn_index is not None:
        indexes.append(move.pawn_index)
    if move.secondary_pawn_index is not None:
        indexes.append(move.secondary_pawn_index)
    return indexes


def _capture_count(before: SorryGameState, after: SorryGameState, player_id: str) -> int:
    before_start = 0
    after_start = 0
    for opponent_id, opponent_state in before.player_states.items():
        if opponent_id == player_id:
            continue
        before_start += sum(1 for pawn in opponent_state.pawns if pawn.zone == "start")
    for opponent_id, opponent_state in after.player_states.items():
        if opponent_id == player_id:
            continue
        after_start += sum(1 for pawn in opponent_state.pawns if pawn.zone == "start")
    return max(0, after_start - before_start)


def choose_move(
    state: SorryGameState,
    player_state: SorryPlayerState,
    moves: list[SorryMove],
    rules: SorryRulesProfile,
) -> SorryMove | None:
    if not moves:
        return None

    best_move: SorryMove | None = None
    best_score: tuple[int, int, int, int, int, int] | None = None

    for move in moves:
        sim_state = deepcopy(state)
        sim_player = sim_state.player_states.get(player_state.player_id)
        if sim_player is None:
            continue

        moved_indexes = _moved_pawn_indexes(move)
        progress_before = sum(_pawn_progress(player_state, idx) for idx in moved_indexes)
        own_start_before = sum(1 for pawn in player_state.pawns if pawn.zone == "start")

        try:
            captures = apply_move(sim_state, sim_player, move, rules)
        except ValueError:
            continue

        progress_after = sum(_pawn_progress(sim_player, idx) for idx in moved_indexes)
        own_start_after = sum(1 for pawn in sim_player.pawns if pawn.zone == "start")

        winning_flag = int(all(pawn.zone == "home" for pawn in sim_player.pawns))
        capture_total = _capture_count(state, sim_state, player_state.player_id) + len(captures)
        leave_start_flag = int(own_start_after < own_start_before)

        threat_count = 0
        safety_bonus = 0
        for idx in moved_indexes:
            if idx < 1 or idx > len(sim_player.pawns):
                continue
            pawn = sim_player.pawns[idx - 1]
            if pawn.zone == "track" and pawn.track_position is not None:
                threat_count += _track_threat_count(
                    sim_state,
                    player_state.player_id,
                    pawn.track_position,
                )
            else:
                safety_bonus += 3
        safe_score = safety_bonus - threat_count
        progress_gain = progress_after - progress_before

        score = (
            winning_flag,
            capture_total,
            leave_start_flag,
            safe_score,
            progress_gain,
            -len(move.action_id),
        )

        if best_score is None or score > best_score:
            best_score = score
            best_move = move
            continue
        if score == best_score and best_move is not None and move.action_id < best_move.action_id:
            best_move = move

    return best_move if best_move is not None else moves[0]
