"""Centralized sound routing and measured timing for Flip 7."""

from __future__ import annotations

from functools import cache
from pathlib import Path, PurePosixPath

from ...game_utils.audio_duration import measure_audio_duration_ticks
from .constants import TICKS_PER_SECOND

# Randomly picked numbered one-shots use the validated audio `family` field;
# clients discover the numbered members dynamically. Their durations below are
# the longest shipped member so server pacing stays deterministic regardless of
# which variant a client picks.
SOUND_CARD_NUMBER_FAMILY = "game_cards/draw"
SOUND_SHUFFLE_FAMILY = "game_cards/shuffle"

SOUND_STAY = "notify2.ogg"
SOUND_MODIFIER_BY_VALUE = {
    2: "game_rollingballs/plus1.ogg",
    4: "game_rollingballs/plus2.ogg",
    6: "game_rollingballs/plus3.ogg",
    8: "game_rollingballs/plus4.ogg",
    10: "game_rollingballs/plus5.ogg",
}
SOUND_DOUBLE = "game_farkle/hotdice.ogg"
SOUND_SECOND_CHANCE = "game_uno/winround.ogg"
SOUND_SECOND_CHANCE_SAVE = "game_coup/challengesuccess.ogg"
SOUND_FREEZE = "game_coup/challengefail.ogg"
SOUND_FLIP_THREE = "game_squares/start.ogg"
SOUND_BUST = "game_pig/lose.ogg"
SOUND_FLIP_SEVEN = "game_rollingballs/wingame.ogg"
SOUND_ROUND_START = "game_deadmanspoker/deal_card.ogg"
SOUND_ROUND_END = "notify3.ogg"
SOUND_MATCH_WIN = "game_uno/wingame.ogg"
SOUND_PLAY_MUSIC = "game_3cardpoker/mus.ogg"

# Ceiling-rounded from the shipped files' OGG granules at 20 Hz.
# Family entries carry the longest member so a family reveal can be sequenced.
AUDIO_DURATIONS_TICKS = {
    SOUND_CARD_NUMBER_FAMILY: 11,
    SOUND_SHUFFLE_FAMILY: 28,
    SOUND_MODIFIER_BY_VALUE[2]: 19,
    SOUND_MODIFIER_BY_VALUE[4]: 19,
    SOUND_MODIFIER_BY_VALUE[6]: 19,
    SOUND_MODIFIER_BY_VALUE[8]: 19,
    SOUND_MODIFIER_BY_VALUE[10]: 18,
    SOUND_STAY: 99,
    SOUND_DOUBLE: 40,
    SOUND_SECOND_CHANCE: 74,
    SOUND_SECOND_CHANCE_SAVE: 42,
    SOUND_FREEZE: 15,
    SOUND_FLIP_THREE: 44,
    SOUND_BUST: 51,
    SOUND_FLIP_SEVEN: 42,
    SOUND_ROUND_START: 24,
    SOUND_ROUND_END: 103,
    SOUND_MATCH_WIN: 81,
}

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


@cache
def sound_ticks(sound_or_family: str) -> int:
    """Return this server run's asset duration, with metadata as fallback."""

    relative_path = PurePosixPath(sound_or_family)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return AUDIO_DURATIONS_TICKS.get(sound_or_family, 0)
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=TICKS_PER_SECOND,
        )
        if measured is not None:
            return measured
    return AUDIO_DURATIONS_TICKS.get(sound_or_family, 0)
