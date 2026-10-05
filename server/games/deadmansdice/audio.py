"""Spatial-audio configuration for Dead Man's Dice."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ...audio import TABLE_RADIUS, DistanceAttenuation, Position
from ...game_utils.audio_duration import measure_audio_duration_ticks

TICKS_PER_SECOND = 20

SOUND_DICE_SHAKES = (
    "game_deadmansdice/dice_shake_rattle.ogg",
    "game_deadmansdice/dice_shake_quick.ogg",
    "game_deadmansdice/dice_shake_loose.ogg",
    "game_deadmansdice/dice_shake_heavy.ogg",
)
SOUND_BID_TAPS = (
    "game_deadmansdice/bid_tap_short.ogg",
    "game_deadmansdice/bid_tap_hollow.ogg",
    "game_deadmansdice/bid_tap_resonant.ogg",
)
SOUND_CALL_LIAR = "game_deadmansdice/call_liar.ogg"
SOUND_CALL_SPOT_ON = "game_deadmansdice/call_spot_on.ogg"
SOUND_CUP_REVEAL = "game_deadmansdice/cup_reveal.ogg"
SOUND_POISON_DRINKS = (
    "game_deadmansdice/poison_drink_steady.ogg",
    "game_deadmansdice/poison_drink_gulp.ogg",
)
SOUND_DEATH_CHOKE = "game_deadmansdice/death_choke.ogg"
SOUND_DEATH_HEADFALL = "game_deadmansdice/death_headfall.ogg"
SOUND_AMBIENT_EVENTS = (
    "game_deadmansdice/ambience_pour_glug.ogg",
    "game_deadmansdice/ambience_ice_glass.ogg",
    "game_deadmansdice/ambience_cigarette_lighter.ogg",
)
SOUND_MUSIC = "game_deadmansdeck/music.ogg"
SOUND_WIN = "game_deadmansdice/win.ogg"

TABLE_EFFECT_ATTENUATION = DistanceAttenuation(
    model="inverse",
    reference_distance=1.25,
    max_distance=6.0,
    rolloff_factor=0.6,
    min_gain=0.4,
    max_gain=1.0,
)
ROOM_ATTENUATION = DistanceAttenuation(
    model="inverse",
    reference_distance=2.0,
    max_distance=18.0,
    rolloff_factor=0.65,
    min_gain=0.12,
    max_gain=0.55,
)

OPENING_DURATION_TICKS = 5 * TICKS_PER_SECOND
OPENING_SETUP_DELAY_TICKS = OPENING_DURATION_TICKS // 2
OPENING_ROLL_DELAY_TICKS = OPENING_DURATION_TICKS - OPENING_SETUP_DELAY_TICKS

AMBIENCE_FADE_IN_MS = OPENING_DURATION_TICKS * 1000 // TICKS_PER_SECOND
AMBIENCE_FADE_OUT_MS = 1200
AMBIENCE_PRIORITY = -20
AMBIENT_EVENT_PRIORITY = -15
TABLE_EFFECT_MAX_INSTANCES = 8
PRIORITY_DICE_SHAKE = 15
PRIORITY_BID = 20
PRIORITY_REVEAL = 30
PRIORITY_CHALLENGE = 35
PRIORITY_POISON = 35
PRIORITY_WIN = 50
MUSIC_PRIORITY = -10

# Dice and bid attacks are the mix reference. Their checked-in variants peak in
# a narrow range, so one shared gain preserves their authored differences.
DICE_SHAKE_GAIN = 0.63
BID_TAP_GAIN = 0.63
CHALLENGE_GAIN = 0.68
CUP_REVEAL_GAIN = 1.0
POISON_DRINK_GAIN = 0.6
DEATH_CHOKE_GAIN = 0.34
DEATH_HEADFALL_GAIN = 0.46
AMBIENT_EVENT_GAIN = 0.58
MUSIC_GAIN = 0.22
WIN_GAIN = 0.6

POISON_DRINK_STAGGER_RATIO = 0.09
DEATH_CHOKE_TO_FALL_RATIO = 0.96

# Measured from the checked-in assets and used only when a deployment does not
# include a locally measurable sound pack. ``sound_ticks`` normally reads the
# shipped Ogg metadata so replacement cues cannot silently desynchronize the
# serialized gameplay sequence from the client-clocked audio.
AUDIO_DURATIONS_TICKS = {
    SOUND_CALL_LIAR: 29,
    SOUND_CALL_SPOT_ON: 31,
    SOUND_CUP_REVEAL: 6,
    SOUND_POISON_DRINKS[0]: 102,
    SOUND_POISON_DRINKS[1]: 134,
    SOUND_DEATH_CHOKE: 94,
    SOUND_DEATH_HEADFALL: 43,
}
CHALLENGE_WAIT_RATIO = 0.95
REVEAL_ANNOUNCEMENT_PAUSE_TICKS = 32
REVEAL_TOTAL_PAUSE_TICKS = 30
RESULT_ANNOUNCEMENT_PAUSE_TICKS = 28
POST_POISON_PAUSE_TICKS = 10
ELIMINATION_ANNOUNCEMENT_PAUSE_TICKS = 36
AMBIENT_EVENT_INTERVAL_TICKS = (45 * TICKS_PER_SECOND, 90 * TICKS_PER_SECOND)
AMBIENT_EVENT_DEFER_TICKS = 8 * TICKS_PER_SECOND
MUSIC_FADE_IN_MS = OPENING_DURATION_TICKS * 1000 // TICKS_PER_SECOND
MUSIC_FADE_OUT_MS = 1200

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


def sound_ticks(sound: str) -> int:
    """Return the shipped asset's duration in ticks, with a tested fallback."""

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


def finite_sequence_duration_ticks(segments: list[tuple[str, float]]) -> int:
    """Return the full duration of a client-clocked finite audio sequence."""

    onset_ticks = 0
    end_ticks = 0
    for asset, next_start_ratio in segments:
        duration_ticks = sound_ticks(asset)
        end_ticks = max(end_ticks, onset_ticks + duration_ticks)
        onset_ticks += math.ceil(duration_ticks * next_start_ratio)
    return end_ticks


@dataclass(frozen=True)
class SpatialAmbienceSource:
    """One fixed point source in the room around the table."""

    layer: str
    asset: str
    world_position: Position
    gain: float


# World coordinates use the same axes as protocol positions: +X is right,
# +Y is forward from the table centre, and +Z is above the tabletop. Distances
# deliberately place room tone beyond the two-metre seating ring.
AMBIENCE_SOURCES = (
    SpatialAmbienceSource(
        layer="crowd_west",
        asset="game_deadmansdice/ambience_crowd_west.ogg",
        world_position=(-8.0, 6.5, 1.5),
        gain=0.68,
    ),
    SpatialAmbienceSource(
        layer="crowd_east",
        asset="game_deadmansdice/ambience_crowd_east.ogg",
        world_position=(7.5, -6.5, 1.4),
        gain=0.54,
    ),
    SpatialAmbienceSource(
        layer="bar",
        asset="game_deadmansdice/ambience_bar.ogg",
        world_position=(6.5, 4.0, 1.0),
        gain=0.8,
    ),
    SpatialAmbienceSource(
        layer="glasses",
        asset="game_deadmansdice/ambience_glasses.ogg",
        world_position=(-5.5, -4.5, 0.85),
        gain=0.56,
    ),
    SpatialAmbienceSource(
        layer="fan",
        asset="game_deadmansdice/ambience_fan.ogg",
        world_position=(0.0, -1.0, 4.5),
        gain=0.4,
    ),
)

# Occasional glass and pouring details occupy three stable service/patron
# points. One point is selected per event, then transformed into every
# listener's seat-relative frame exactly like the persistent room layers.
AMBIENT_EVENT_WORLD_POSITIONS: tuple[Position, ...] = (
    (6.2, 3.8, 0.95),
    (-7.0, 5.8, 0.85),
    (6.8, -5.7, 0.85),
)


def listener_relative_room_position(
    world_position: Position,
    listener_seat_index: int | None,
    seat_count: int,
    *,
    table_radius: float = TABLE_RADIUS,
) -> Position:
    """Transform a room-fixed point into one listener's coordinate frame.

    A spectator has no seat and therefore listens from the table centre. A
    seated listener is placed on the seating ring and faces the centre. This
    keeps every ambience source fixed in the same room for all listeners.
    """

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

    # Every seated listener faces the table centre. These are their local
    # right and forward unit vectors in the shared room coordinate system.
    right_x, right_y = -math.cos(angle), math.sin(angle)
    forward_x, forward_y = -math.sin(angle), -math.cos(angle)
    return (
        round(delta_x * right_x + delta_y * right_y, 3),
        round(delta_x * forward_x + delta_y * forward_y, 3),
        round(float(source_z), 3),
    )


ALL_SOUND_ASSETS = frozenset(
    {
        *SOUND_DICE_SHAKES,
        *SOUND_BID_TAPS,
        SOUND_CALL_LIAR,
        SOUND_CALL_SPOT_ON,
        SOUND_CUP_REVEAL,
        *SOUND_POISON_DRINKS,
        SOUND_DEATH_CHOKE,
        SOUND_DEATH_HEADFALL,
        *SOUND_AMBIENT_EVENTS,
        SOUND_MUSIC,
        SOUND_WIN,
        *(source.asset for source in AMBIENCE_SOURCES),
    }
)
