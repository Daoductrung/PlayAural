"""Move models and generation/application helpers for Sorry."""

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin

from .rules import SorryRulesProfile
from .state import (
    SAFETY_LENGTH,
    SorryGameState,
    SorryPawnState,
    SorryPlayerState,
    clockwise_distance,
    normalize_track_position,
)


@dataclass(frozen=True)
class CaptureEvent(DataClassJSONMixin):
    captured_player_id: str
    captured_pawn_index: int
    by_player_id: str


_SLIDE_START_TO_STEPS_BY_OFFSET: dict[int, int] = {
    1: 3,
    9: 4,
}


@dataclass(frozen=True)
class PawnDestination(DataClassJSONMixin):
    zone: str
    track_position: int | None = None
    home_steps: int = 0


@dataclass(frozen=True)
class SorryMove(DataClassJSONMixin):
    action_id: str
    move_type: str
    description: str
    pawn_index: int | None = None
    steps: int | None = None
    secondary_pawn_index: int | None = None
    secondary_steps: int | None = None
    target_player_id: str | None = None
    target_pawn_index: int | None = None


def _get_pawn(player_state: SorryPlayerState, pawn_index: int | None) -> SorryPawnState | None:
    if pawn_index is None or pawn_index < 1 or pawn_index > len(player_state.pawns):
        return None
    return player_state.pawns[pawn_index - 1]


def _player_by_id(
    state: SorryGameState,
    player_id: str | None,
) -> SorryPlayerState | None:
    if player_id is None:
        return None
    return state.player_states.get(player_id)


def _compute_forward_destination(
    player_state: SorryPlayerState,
    pawn: SorryPawnState,
    steps: int,
) -> PawnDestination | None:
    if steps <= 0 or pawn.zone == "home":
        return None

    if pawn.zone == "home_path":
        next_steps = pawn.home_steps + steps
        if next_steps <= SAFETY_LENGTH:
            return PawnDestination(zone="home_path", home_steps=next_steps)
        if next_steps == SAFETY_LENGTH + 1:
            return PawnDestination(zone="home")
        return None

    if pawn.zone != "track" or pawn.track_position is None:
        return None

    distance_to_home_entry = clockwise_distance(
        pawn.track_position,
        player_state.home_entry_track,
    )
    if steps <= distance_to_home_entry:
        return PawnDestination(
            zone="track",
            track_position=normalize_track_position(pawn.track_position + steps),
        )

    remaining = steps - distance_to_home_entry
    if remaining <= SAFETY_LENGTH:
        return PawnDestination(zone="home_path", home_steps=remaining)
    if remaining == SAFETY_LENGTH + 1:
        return PawnDestination(zone="home")
    return None


def _compute_backward_destination(
    pawn: SorryPawnState,
    steps: int,
) -> PawnDestination | None:
    if steps <= 0 or pawn.zone != "track" or pawn.track_position is None:
        return None
    return PawnDestination(
        zone="track",
        track_position=normalize_track_position(pawn.track_position - steps),
    )


def _is_destination_legal_for_player(
    player_state: SorryPlayerState,
    destination: PawnDestination,
    *,
    ignore_pawn_indexes: set[int] | None = None,
) -> bool:
    ignore = ignore_pawn_indexes or set()
    for pawn in player_state.pawns:
        if pawn.pawn_index in ignore:
            continue
        if destination.zone == "track":
            if (
                pawn.zone == "track"
                and pawn.track_position is not None
                and normalize_track_position(pawn.track_position)
                == normalize_track_position(destination.track_position or 0)
            ):
                return False
        elif destination.zone == "home_path":
            if pawn.zone == "home_path" and pawn.home_steps == destination.home_steps:
                return False
    return True


def _iter_track_pawns(player_state: SorryPlayerState) -> list[SorryPawnState]:
    return [
        pawn
        for pawn in player_state.pawns
        if pawn.zone == "track" and pawn.track_position is not None
    ]


def _generate_start_moves(player_state: SorryPlayerState) -> list[SorryMove]:
    destination = PawnDestination(zone="track", track_position=player_state.start_track)
    if not _is_destination_legal_for_player(player_state, destination):
        return []
    return [
        SorryMove(
            action_id=f"start_p{pawn.pawn_index}",
            move_type="start",
            description=f"Move pawn {pawn.pawn_index} out of start",
            pawn_index=pawn.pawn_index,
        )
        for pawn in player_state.pawns
        if pawn.zone == "start"
    ]


def _generate_forward_moves(player_state: SorryPlayerState, steps: int) -> list[SorryMove]:
    moves: list[SorryMove] = []
    for pawn in player_state.pawns:
        destination = _compute_forward_destination(player_state, pawn, steps)
        if destination is None:
            continue
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            continue
        moves.append(
            SorryMove(
                action_id=f"forward{steps}_p{pawn.pawn_index}",
                move_type="forward",
                description=f"Move pawn {pawn.pawn_index} forward {steps}",
                pawn_index=pawn.pawn_index,
                steps=steps,
            )
        )
    return moves


def _generate_backward_moves(player_state: SorryPlayerState, steps: int) -> list[SorryMove]:
    moves: list[SorryMove] = []
    for pawn in player_state.pawns:
        destination = _compute_backward_destination(pawn, steps)
        if destination is None:
            continue
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            continue
        moves.append(
            SorryMove(
                action_id=f"backward{steps}_p{pawn.pawn_index}",
                move_type="backward",
                description=f"Move pawn {pawn.pawn_index} backward {steps}",
                pawn_index=pawn.pawn_index,
                steps=steps,
            )
        )
    return moves


def _generate_swap_moves(
    state: SorryGameState,
    player_state: SorryPlayerState,
) -> list[SorryMove]:
    own_track = _iter_track_pawns(player_state)
    if not own_track:
        return []

    moves: list[SorryMove] = []
    for own_pawn in own_track:
        for opponent_id, opponent_state in state.player_states.items():
            if opponent_id == player_state.player_id:
                continue
            for target in _iter_track_pawns(opponent_state):
                moves.append(
                    SorryMove(
                        action_id=f"swap_p{own_pawn.pawn_index}_{opponent_id}_p{target.pawn_index}",
                        move_type="swap",
                        description=f"Swap pawn {own_pawn.pawn_index} with {opponent_id} pawn {target.pawn_index}",
                        pawn_index=own_pawn.pawn_index,
                        target_player_id=opponent_id,
                        target_pawn_index=target.pawn_index,
                    )
                )
    return moves


def _generate_sorry_moves(
    state: SorryGameState,
    player_state: SorryPlayerState,
) -> list[SorryMove]:
    start_pawns = [pawn for pawn in player_state.pawns if pawn.zone == "start"]
    if not start_pawns:
        return []

    moves: list[SorryMove] = []
    for own_pawn in start_pawns:
        for opponent_id, opponent_state in state.player_states.items():
            if opponent_id == player_state.player_id:
                continue
            for target in _iter_track_pawns(opponent_state):
                destination = PawnDestination(zone="track", track_position=target.track_position)
                if not _is_destination_legal_for_player(
                    player_state,
                    destination,
                    ignore_pawn_indexes={own_pawn.pawn_index},
                ):
                    continue
                moves.append(
                    SorryMove(
                        action_id=f"sorry_p{own_pawn.pawn_index}_{opponent_id}_p{target.pawn_index}",
                        move_type="sorry",
                        description=f"Move pawn {own_pawn.pawn_index} to replace {opponent_id} pawn {target.pawn_index}",
                        pawn_index=own_pawn.pawn_index,
                        target_player_id=opponent_id,
                        target_pawn_index=target.pawn_index,
                    )
                )
    return moves


def _generate_sorry_fallback_forward_moves(
    player_state: SorryPlayerState,
    steps: int,
) -> list[SorryMove]:
    moves: list[SorryMove] = []
    for pawn in player_state.pawns:
        destination = _compute_forward_destination(player_state, pawn, steps)
        if destination is None:
            continue
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            continue
        moves.append(
            SorryMove(
                action_id=f"sorry_fwd{steps}_p{pawn.pawn_index}",
                move_type="sorry_fallback_forward",
                description=f"Move pawn {pawn.pawn_index} forward {steps}",
                pawn_index=pawn.pawn_index,
                steps=steps,
            )
        )
    return moves


def _pair_has_any_valid_split(
    player_state: SorryPlayerState,
    pawn_a: SorryPawnState,
    pawn_b: SorryPawnState,
) -> bool:
    for first_steps in range(1, 7):
        second_steps = 7 - first_steps
        dest_a = _compute_forward_destination(player_state, pawn_a, first_steps)
        dest_b = _compute_forward_destination(player_state, pawn_b, second_steps)
        if dest_a is None or dest_b is None:
            continue
        if dest_a.zone == dest_b.zone == "track" and dest_a.track_position == dest_b.track_position:
            continue
        if dest_a.zone == dest_b.zone == "home_path" and dest_a.home_steps == dest_b.home_steps:
            continue
        ignore = {pawn_a.pawn_index, pawn_b.pawn_index}
        if not _is_destination_legal_for_player(player_state, dest_a, ignore_pawn_indexes=ignore):
            continue
        if not _is_destination_legal_for_player(player_state, dest_b, ignore_pawn_indexes=ignore):
            continue
        return True
    return False


def _generate_split_seven_moves(player_state: SorryPlayerState) -> list[SorryMove]:
    movable = [
        pawn.pawn_index
        for pawn in player_state.pawns
        if pawn.zone in {"track", "home_path"}
    ]
    if len(movable) < 2:
        return []

    moves: list[SorryMove] = []
    for i, pawn_a_index in enumerate(movable):
        for pawn_b_index in movable[i + 1 :]:
            pawn_a = _get_pawn(player_state, pawn_a_index)
            pawn_b = _get_pawn(player_state, pawn_b_index)
            if pawn_a is None or pawn_b is None:
                continue
            if not _pair_has_any_valid_split(player_state, pawn_a, pawn_b):
                continue
            moves.append(
                SorryMove(
                    action_id=f"split7_pair_p{pawn_a_index}_p{pawn_b_index}",
                    move_type="split7_pick",
                    description=f"Split 7 between pawn {pawn_a_index} and pawn {pawn_b_index}",
                    pawn_index=pawn_a_index,
                    secondary_pawn_index=pawn_b_index,
                )
            )
    return moves


def generate_split_options_for_pair(
    player_state: SorryPlayerState,
    pawn_a_index: int,
    pawn_b_index: int,
) -> list[SorryMove]:
    pawn_a = _get_pawn(player_state, pawn_a_index)
    pawn_b = _get_pawn(player_state, pawn_b_index)
    if pawn_a is None or pawn_b is None:
        return []

    moves: list[SorryMove] = []
    for first_steps in range(1, 7):
        second_steps = 7 - first_steps
        dest_a = _compute_forward_destination(player_state, pawn_a, first_steps)
        dest_b = _compute_forward_destination(player_state, pawn_b, second_steps)
        if dest_a is None or dest_b is None:
            continue
        if dest_a.zone == dest_b.zone == "track" and dest_a.track_position == dest_b.track_position:
            continue
        if dest_a.zone == dest_b.zone == "home_path" and dest_a.home_steps == dest_b.home_steps:
            continue
        ignore = {pawn_a_index, pawn_b_index}
        if not _is_destination_legal_for_player(player_state, dest_a, ignore_pawn_indexes=ignore):
            continue
        if not _is_destination_legal_for_player(player_state, dest_b, ignore_pawn_indexes=ignore):
            continue
        moves.append(
            SorryMove(
                action_id=f"split7_p{pawn_a_index}_{first_steps}_p{pawn_b_index}_{second_steps}",
                move_type="split7",
                description=f"Pawn {pawn_a_index} moves {first_steps}, pawn {pawn_b_index} moves {second_steps}",
                pawn_index=pawn_a_index,
                steps=first_steps,
                secondary_pawn_index=pawn_b_index,
                secondary_steps=second_steps,
            )
        )
    return moves


def generate_legal_moves(
    state: SorryGameState,
    player_state: SorryPlayerState,
    card_face: str,
    rules: SorryRulesProfile,
) -> list[SorryMove]:
    if card_face not in rules.card_faces():
        return []

    moves: list[SorryMove] = []
    if rules.can_leave_start_with_card(card_face):
        moves.extend(_generate_start_moves(player_state))
    for forward_steps in rules.forward_steps_for_card(card_face):
        moves.extend(_generate_forward_moves(player_state, forward_steps))
    for backward_steps in rules.backward_steps_for_card(card_face):
        moves.extend(_generate_backward_moves(player_state, backward_steps))
    if rules.allows_split_seven(card_face):
        moves.extend(_generate_split_seven_moves(player_state))
    if rules.allows_swap(card_face):
        moves.extend(_generate_swap_moves(state, player_state))
    if rules.allows_sorry(card_face):
        sorry_moves = _generate_sorry_moves(state, player_state)
        moves.extend(sorry_moves)
        if not sorry_moves:
            for fallback_steps in rules.sorry_fallback_forward_steps(card_face):
                moves.extend(_generate_sorry_fallback_forward_moves(player_state, fallback_steps))
    return sorted(moves, key=lambda move: move.action_id)


def _send_pawn_to_start(pawn: SorryPawnState) -> None:
    pawn.zone = "start"
    pawn.track_position = None
    pawn.home_steps = 0


def _apply_destination(pawn: SorryPawnState, destination: PawnDestination) -> None:
    pawn.zone = destination.zone
    if destination.zone == "track":
        pawn.track_position = destination.track_position
        pawn.home_steps = 0
    elif destination.zone == "home_path":
        pawn.track_position = None
        pawn.home_steps = destination.home_steps
    elif destination.zone == "home":
        pawn.track_position = None
        pawn.home_steps = SAFETY_LENGTH + 1
    else:
        raise ValueError(f"Unsupported destination zone: {destination.zone}")


def _capture_opponents_on_track(
    state: SorryGameState,
    player_state: SorryPlayerState,
    track_position: int | None,
) -> list[CaptureEvent]:
    if track_position is None:
        return []
    events: list[CaptureEvent] = []
    normalized = normalize_track_position(track_position)
    for other_id, other_state in state.player_states.items():
        if other_id == player_state.player_id:
            continue
        for pawn in other_state.pawns:
            if pawn.zone == "track" and pawn.track_position is not None:
                if normalize_track_position(pawn.track_position) == normalized:
                    _send_pawn_to_start(pawn)
                    events.append(
                        CaptureEvent(
                            captured_player_id=other_id,
                            captured_pawn_index=pawn.pawn_index,
                            by_player_id=player_state.player_id,
                        )
                    )
    return events


def _resolve_slide_for_pawn(
    state: SorryGameState,
    player_state: SorryPlayerState,
    pawn: SorryPawnState,
    rules: SorryRulesProfile,
) -> list[CaptureEvent]:
    if pawn.zone != "track" or pawn.track_position is None:
        return []

    start = normalize_track_position(pawn.track_position)
    slide_steps = _SLIDE_START_TO_STEPS_BY_OFFSET.get(start % 15)
    if slide_steps is None:
        return []

    slide_owner_seat = start // 15
    same_color_slide = slide_owner_seat == player_state.seat_index
    if rules.slide_policy_id() == "a5065_core":
        should_slide = same_color_slide
    else:
        should_slide = not same_color_slide
    if not should_slide:
        return []

    events: list[CaptureEvent] = []
    end = normalize_track_position(start + slide_steps)
    slide_positions = {normalize_track_position(start + step) for step in range(slide_steps + 1)}
    for other_id, other_state in state.player_states.items():
        for other_pawn in other_state.pawns:
            if other_pawn is pawn:
                continue
            if other_pawn.zone != "track" or other_pawn.track_position is None:
                continue
            if normalize_track_position(other_pawn.track_position) in slide_positions:
                _send_pawn_to_start(other_pawn)
                events.append(
                    CaptureEvent(
                        captured_player_id=other_id,
                        captured_pawn_index=other_pawn.pawn_index,
                        by_player_id=player_state.player_id,
                    )
                )

    pawn.track_position = end
    return events


def apply_move(
    state: SorryGameState,
    player_state: SorryPlayerState,
    move: SorryMove,
    rules: SorryRulesProfile,
) -> list[CaptureEvent]:
    events: list[CaptureEvent] = []

    if move.move_type == "start":
        pawn = _get_pawn(player_state, move.pawn_index)
        if pawn is None or pawn.zone != "start":
            raise ValueError("Invalid start move pawn")
        destination = PawnDestination(zone="track", track_position=player_state.start_track)
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            raise ValueError("Start destination blocked by own pawn")
        _apply_destination(pawn, destination)
        events.extend(_capture_opponents_on_track(state, player_state, pawn.track_position))
        events.extend(_resolve_slide_for_pawn(state, player_state, pawn, rules))
        return events

    if move.move_type in {"forward", "sorry_fallback_forward"}:
        pawn = _get_pawn(player_state, move.pawn_index)
        if pawn is None:
            raise ValueError("Invalid forward move pawn")
        destination = _compute_forward_destination(player_state, pawn, move.steps or 0)
        if destination is None:
            raise ValueError("Forward move not legal")
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            raise ValueError("Forward destination blocked by own pawn")
        _apply_destination(pawn, destination)
        events.extend(_capture_opponents_on_track(state, player_state, pawn.track_position))
        events.extend(_resolve_slide_for_pawn(state, player_state, pawn, rules))
        return events

    if move.move_type == "backward":
        pawn = _get_pawn(player_state, move.pawn_index)
        if pawn is None:
            raise ValueError("Invalid backward move pawn")
        destination = _compute_backward_destination(pawn, move.steps or 0)
        if destination is None:
            raise ValueError("Backward move not legal")
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={pawn.pawn_index},
        ):
            raise ValueError("Backward destination blocked by own pawn")
        _apply_destination(pawn, destination)
        events.extend(_capture_opponents_on_track(state, player_state, pawn.track_position))
        events.extend(_resolve_slide_for_pawn(state, player_state, pawn, rules))
        return events

    if move.move_type == "swap":
        own_pawn = _get_pawn(player_state, move.pawn_index)
        target_player = _player_by_id(state, move.target_player_id)
        target_pawn = _get_pawn(target_player, move.target_pawn_index) if target_player else None
        if own_pawn is None or target_pawn is None:
            raise ValueError("Swap references missing pawn")
        if own_pawn.zone != "track" or own_pawn.track_position is None:
            raise ValueError("Own pawn not on track for swap")
        if target_pawn.zone != "track" or target_pawn.track_position is None:
            raise ValueError("Target pawn not on track for swap")
        own_pos = own_pawn.track_position
        target_pos = target_pawn.track_position
        own_pawn.track_position = target_pos
        target_pawn.track_position = own_pos
        events.extend(_resolve_slide_for_pawn(state, player_state, own_pawn, rules))
        return events

    if move.move_type == "sorry":
        own_pawn = _get_pawn(player_state, move.pawn_index)
        target_player = _player_by_id(state, move.target_player_id)
        target_pawn = _get_pawn(target_player, move.target_pawn_index) if target_player else None
        if own_pawn is None or own_pawn.zone != "start" or target_pawn is None:
            raise ValueError("Invalid Sorry move")
        if target_pawn.zone != "track" or target_pawn.track_position is None:
            raise ValueError("Sorry target not on track")
        destination = PawnDestination(zone="track", track_position=target_pawn.track_position)
        if not _is_destination_legal_for_player(
            player_state,
            destination,
            ignore_pawn_indexes={own_pawn.pawn_index},
        ):
            raise ValueError("Sorry destination blocked by own pawn")
        _send_pawn_to_start(target_pawn)
        events.append(
            CaptureEvent(
                captured_player_id=target_player.player_id,
                captured_pawn_index=target_pawn.pawn_index,
                by_player_id=player_state.player_id,
            )
        )
        _apply_destination(own_pawn, destination)
        events.extend(_resolve_slide_for_pawn(state, player_state, own_pawn, rules))
        return events

    if move.move_type == "split7":
        pawn_a = _get_pawn(player_state, move.pawn_index)
        pawn_b = _get_pawn(player_state, move.secondary_pawn_index)
        if pawn_a is None or pawn_b is None:
            raise ValueError("Invalid split move pawn")
        dest_a = _compute_forward_destination(player_state, pawn_a, move.steps or 0)
        dest_b = _compute_forward_destination(player_state, pawn_b, move.secondary_steps or 0)
        if dest_a is None or dest_b is None:
            raise ValueError("Invalid split destinations")
        if dest_a.zone == dest_b.zone == "track" and dest_a.track_position == dest_b.track_position:
            raise ValueError("Split destinations overlap")
        if dest_a.zone == dest_b.zone == "home_path" and dest_a.home_steps == dest_b.home_steps:
            raise ValueError("Split destinations overlap")
        ignore = {pawn_a.pawn_index, pawn_b.pawn_index}
        if not _is_destination_legal_for_player(player_state, dest_a, ignore_pawn_indexes=ignore):
            raise ValueError("First split destination blocked")
        if not _is_destination_legal_for_player(player_state, dest_b, ignore_pawn_indexes=ignore):
            raise ValueError("Second split destination blocked")
        _apply_destination(pawn_a, dest_a)
        _apply_destination(pawn_b, dest_b)
        events.extend(_capture_opponents_on_track(state, player_state, pawn_a.track_position))
        events.extend(_capture_opponents_on_track(state, player_state, pawn_b.track_position))
        events.extend(_resolve_slide_for_pawn(state, player_state, pawn_a, rules))
        events.extend(_resolve_slide_for_pawn(state, player_state, pawn_b, rules))
        return events

    raise ValueError(f"Unsupported move type: {move.move_type}")
