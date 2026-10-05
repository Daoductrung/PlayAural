"""Self-contained spatial-audio design for Zombie Dice."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ...audio import TABLE_RADIUS, DistanceAttenuation, Position
from ...game_utils.audio_duration import measure_audio_duration_ticks
from .rules import DICE_PER_ROLL

TICKS_PER_SECOND = 20

SOUND_ROLL_SHAKES = tuple(
    f"game_zombiedice/roll_shake{index}.ogg" for index in range(1, 4)
)
SOUND_ROLL_LANDS = tuple(
    f"game_zombiedice/roll_land{index}.ogg" for index in range(1, 4)
)
SOUND_SHOTGUNS = tuple(f"game_zombiedice/shotgun{index}.ogg" for index in range(1, 7))
SOUND_SHOT_FLYBYS = tuple(
    f"game_zombiedice/shot_flyby{index}.ogg" for index in range(1, 6)
)
SOUND_SHOT_IMPACTS = tuple(
    f"game_zombiedice/shot_impact{index}.ogg" for index in range(1, 5)
)
SOUND_SHELL_CASINGS = tuple(
    f"game_zombiedice/shell_casing{index}.ogg" for index in range(1, 5)
)
SOUND_BUSTS = tuple(f"game_zombiedice/bust{index}.ogg" for index in range(1, 11))
SOUND_BANK_GROWLS = tuple(
    f"game_zombiedice/bank_growl{index}.ogg" for index in range(1, 4)
)
SOUND_WANDER_GROWLS = tuple(
    f"game_zombiedice/wander_growl{index}.ogg" for index in range(1, 8)
)
SOUND_WANDER_STEPS = tuple(
    f"game_zombiedice/wander_step{index}.ogg" for index in range(1, 10)
)
SOUND_WIN_ROAR_FAMILY = "game_zombiedice/win_roar"
SOUND_WIN_ROARS = tuple(f"game_zombiedice/win_roar{index}.ogg" for index in range(1, 9))
SOUND_BANK_BITE = "game_zombiedice/bank_bite.ogg"
SOUND_CUP_REFILL = "game_zombiedice/cup_refill.ogg"
SOUND_FINAL_HEARTBEAT = "game_zombiedice/final_heartbeat.ogg"
SOUND_MUSIC = "game_zombiedice/music.ogg"

TABLE_ATTENUATION = DistanceAttenuation(
    model="inverse",
    reference_distance=1.25,
    max_distance=6.0,
    rolloff_factor=0.55,
    min_gain=0.45,
    max_gain=1.0,
)
SCENE_ATTENUATION = DistanceAttenuation(
    model="inverse",
    reference_distance=2.5,
    max_distance=20.0,
    rolloff_factor=0.55,
    min_gain=0.12,
    max_gain=0.7,
)

AMBIENCE_FADE_IN_MS = 3500
AMBIENCE_FADE_OUT_MS = 1200
AMBIENCE_PRIORITY = -20
MUSIC_PRIORITY = -10
WANDER_PRIORITY = -10
ROLL_PRIORITY = 15
BANK_PRIORITY = 20
FINAL_PRIORITY = 30
WIN_PRIORITY = 50
TABLE_EFFECT_MAX_INSTANCES = 8

CUP_REFILL_GAIN = 0.58
ROLL_SHAKE_GAIN = 0.52
ROLL_LAND_GAIN = 0.62
SHOTGUN_GAIN = 1.0
SHOT_FLYBY_GAIN = 0.55
SHOT_IMPACT_GAIN = 0.82
SHELL_CASING_GAIN = 0.5
BUST_GAIN = 0.78
BANK_BITE_GAIN = 0.34
BANK_GROWL_GAIN = 0.58
WANDER_STEP_GAIN = 1.0
WANDER_GROWL_GAIN = 0.3
FINAL_HEARTBEAT_GAIN = 0.9
WIN_ROAR_GAIN = 0.34
MUSIC_GAIN = 0.8

MUSIC_FADE_IN_MS = 2500
MUSIC_FADE_OUT_MS = 1200

CUP_REFILL_NEXT_RATIO = 1.0
ROLL_SHAKE_NEXT_RATIO = 1.0
ROLL_LAND_NEXT_RATIO = 1.0
FLYBY_TO_IMPACT_RATIO = 1.0
BULLET_BURST_MIN_SHOTGUNS = 2
BULLET_BURST_INTERVAL_MS = 100
BANK_BITE_NEXT_RATIO = 0.62
WANDER_STEP_NEXT_RATIO = 1.0
FINAL_HEARTBEAT_NEXT_RATIO = 0.65

WANDER_STEP_COUNT = 4
WANDER_STEP_ROUTE_FRACTION = 0.4
WANDER_INITIAL_DELAY_TICKS = (10 * TICKS_PER_SECOND, 18 * TICKS_PER_SECOND)
WANDER_INTERVAL_TICKS = (24 * TICKS_PER_SECOND, 42 * TICKS_PER_SECOND)
WANDER_DEFER_TICKS = 8 * TICKS_PER_SECOND

# Zombie Dice always rolls three dice. These explicit density banks prevent a
# light single-die landing from being selected for the official three-die roll.
ROLL_SHAKES_BY_DICE_COUNT = {DICE_PER_ROLL: SOUND_ROLL_SHAKES}
ROLL_LANDS_BY_DICE_COUNT = {DICE_PER_ROLL: SOUND_ROLL_LANDS}

# Measured from the checked-in assets and used only when a deployment does not
# include a locally measurable sound pack. ``sound_ticks`` normally reads the
# shipped Ogg metadata so replacing a cue cannot silently desynchronize the
# serialized gameplay sequence from the client-clocked audio.
AUDIO_DURATIONS_TICKS = {
    SOUND_CUP_REFILL: 8,
    SOUND_ROLL_SHAKES[0]: 50,
    SOUND_ROLL_SHAKES[1]: 47,
    SOUND_ROLL_SHAKES[2]: 47,
    SOUND_ROLL_LANDS[0]: 12,
    SOUND_ROLL_LANDS[1]: 16,
    SOUND_ROLL_LANDS[2]: 9,
    SOUND_SHOTGUNS[0]: 16,
    SOUND_SHOTGUNS[1]: 17,
    SOUND_SHOTGUNS[2]: 16,
    SOUND_SHOTGUNS[3]: 16,
    SOUND_SHOTGUNS[4]: 16,
    SOUND_SHOTGUNS[5]: 16,
    SOUND_SHOT_FLYBYS[0]: 3,
    SOUND_SHOT_FLYBYS[1]: 4,
    SOUND_SHOT_FLYBYS[2]: 3,
    SOUND_SHOT_FLYBYS[3]: 4,
    SOUND_SHOT_FLYBYS[4]: 4,
    SOUND_SHOT_IMPACTS[0]: 4,
    SOUND_SHOT_IMPACTS[1]: 13,
    SOUND_SHOT_IMPACTS[2]: 13,
    SOUND_SHOT_IMPACTS[3]: 13,
    SOUND_SHELL_CASINGS[0]: 11,
    SOUND_SHELL_CASINGS[1]: 14,
    SOUND_SHELL_CASINGS[2]: 12,
    SOUND_SHELL_CASINGS[3]: 14,
    SOUND_BUSTS[0]: 19,
    SOUND_BUSTS[1]: 12,
    SOUND_BUSTS[2]: 16,
    SOUND_BUSTS[3]: 15,
    SOUND_BUSTS[4]: 19,
    SOUND_BUSTS[5]: 16,
    SOUND_BUSTS[6]: 26,
    SOUND_BUSTS[7]: 11,
    SOUND_BUSTS[8]: 15,
    SOUND_BUSTS[9]: 14,
}

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


def roll_sound_bank(
    dice_count: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return shake and landing variations authored for one roll density."""

    try:
        return (
            ROLL_SHAKES_BY_DICE_COUNT[dice_count],
            ROLL_LANDS_BY_DICE_COUNT[dice_count],
        )
    except KeyError as error:
        raise ValueError(
            f"No Zombie Dice audio for {dice_count} rolled dice"
        ) from error


def sound_ticks(sound: str) -> int:
    """Return the shipped asset duration in server ticks."""

    relative_path = PurePosixPath(sound)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=TICKS_PER_SECOND,
        )
        if measured is not None:
            return measured
    return AUDIO_DURATIONS_TICKS.get(sound, 0)


def sound_milliseconds(sound: str) -> int:
    """Return the shipped asset duration in whole milliseconds."""

    relative_path = PurePosixPath(sound)
    if not relative_path.is_absolute() and ".." not in relative_path.parts:
        for asset_root in _SOUND_ASSET_ROOTS:
            measured = measure_audio_duration_ticks(
                asset_root.joinpath(*relative_path.parts),
                ticks_per_second=1000,
            )
            if measured is not None:
                return measured
    fallback_ticks = AUDIO_DURATIONS_TICKS.get(sound, 0)
    return math.ceil(fallback_ticks * 1000 / TICKS_PER_SECOND)


def finite_sequence_duration_ticks(segments: list[tuple[str, float]]) -> int:
    """Return the complete duration of an overlapping client-clocked chain."""

    onset_ms = 0.0
    end_ms = 0.0
    for asset, next_start_ratio in segments:
        duration_ms = sound_milliseconds(asset)
        end_ms = max(end_ms, onset_ms + duration_ms)
        onset_ms += duration_ms * next_start_ratio
    return math.ceil(end_ms * TICKS_PER_SECOND / 1000)


def roll_result_delay_ticks(segments: list[tuple[str, float]]) -> int:
    """Return the client-clock delay through the roll's landing cue."""

    prefix: list[tuple[str, float]] = []
    for asset, next_start_ratio in segments:
        prefix.append((asset, next_start_ratio))
        if asset in SOUND_ROLL_LANDS:
            return finite_sequence_duration_ticks(prefix)
    raise ValueError("Zombie Dice roll audio has no landing cue")


@dataclass(frozen=True)
class SpatialAmbienceSource:
    """One room-fixed environmental layer around the table."""

    layer: str
    asset: str
    world_position: Position
    gain: float


AMBIENCE_SOURCES = (
    SpatialAmbienceSource(
        layer="swamp",
        asset="game_zombiedice/ambience_swamp.ogg",
        world_position=(-7.0, 6.0, 0.35),
        gain=0.75,
    ),
    SpatialAmbienceSource(
        layer="wind_crickets",
        asset="game_zombiedice/ambience_wind_crickets.ogg",
        world_position=(7.0, -6.0, 1.8),
        gain=0.65,
    ),
)

# Routes remain outside the two-metre seating ring. A finite footstep-and-growl
# chain traverses one of these paths without pretending that the ambient zombie
# is a gameplay piece or giving any player strategic information.
WANDER_WORLD_ROUTES: tuple[tuple[Position, Position], ...] = (
    ((-8.0, 5.8, 0.0), (-2.5, 5.8, 0.0)),
    ((8.0, -5.8, 0.0), (2.5, -5.8, 0.0)),
    ((-5.8, -8.0, 0.0), (-5.8, -2.5, 0.0)),
    ((5.8, 8.0, 0.0), (5.8, 2.5, 0.0)),
)


def listener_relative_scene_position(
    world_position: Position,
    listener_seat_index: int | None,
    seat_count: int,
    *,
    table_radius: float = TABLE_RADIUS,
) -> Position:
    """Transform a scene-fixed point into one listener's local frame."""

    source_x, source_y, source_z = world_position
    if listener_seat_index is None or seat_count < 2:
        return (
            round(float(source_x), 3),
            round(float(source_y), 3),
            round(float(source_z), 3),
        )

    angle = 2.0 * math.pi * (listener_seat_index % seat_count) / seat_count
    listener_x = table_radius * math.sin(angle)
    listener_y = table_radius * math.cos(angle)
    delta_x = source_x - listener_x
    delta_y = source_y - listener_y

    right_x, right_y = -math.cos(angle), math.sin(angle)
    forward_x, forward_y = -math.sin(angle), -math.cos(angle)
    return (
        round(delta_x * right_x + delta_y * right_y, 3),
        round(delta_x * forward_x + delta_y * forward_y, 3),
        round(float(source_z), 3),
    )


def interpolate_world_position(
    origin: Position,
    destination: Position,
    progress: float,
) -> Position:
    """Return one point along a scene-space route."""

    if not 0.0 <= progress <= 1.0:
        raise ValueError("Audio route progress must be from zero to one")
    return (
        round(origin[0] + (destination[0] - origin[0]) * progress, 3),
        round(origin[1] + (destination[1] - origin[1]) * progress, 3),
        round(origin[2] + (destination[2] - origin[2]) * progress, 3),
    )


def table_seat_world_position(
    seat_index: int,
    seat_count: int,
    *,
    table_radius: float = TABLE_RADIUS,
) -> Position:
    """Return one seat in the shared table-centred coordinate frame."""

    if seat_count < 2:
        raise ValueError("Spatial table audio requires at least two seats")
    angle = 2.0 * math.pi * (seat_index % seat_count) / seat_count
    return (
        round(table_radius * math.sin(angle), 3),
        round(table_radius * math.cos(angle), 3),
        0.0,
    )


ALL_SOUND_ASSETS = frozenset(
    {
        *SOUND_ROLL_SHAKES,
        *SOUND_ROLL_LANDS,
        *SOUND_SHOTGUNS,
        *SOUND_SHOT_FLYBYS,
        *SOUND_SHOT_IMPACTS,
        *SOUND_SHELL_CASINGS,
        *SOUND_BUSTS,
        *SOUND_BANK_GROWLS,
        *SOUND_WANDER_GROWLS,
        *SOUND_WANDER_STEPS,
        *SOUND_WIN_ROARS,
        SOUND_BANK_BITE,
        SOUND_CUP_REFILL,
        SOUND_FINAL_HEARTBEAT,
        SOUND_MUSIC,
        *(source.asset for source in AMBIENCE_SOURCES),
    }
)
