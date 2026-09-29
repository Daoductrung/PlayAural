"""Data-driven timing for Bingo's sequence-timed sound effects.

CALL_SPIN_DELAY_TICKS and CLAIM_SUSPENSE_TICKS decide how long the game
waits for call.ogg and suspense.ogg to finish before announcing a number
or revealing a claim's result. Measuring the assets prevents replacements
with different lengths from silently desynchronizing game state and audio.

``sound_ticks()`` measures the real shipped asset (same idiom as Bang!'s
and Monopoly's audio.py) and only falls back to the fixed durations below
when the file cannot be found or read, e.g. in a stripped-down deployment
without audio assets.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path, PurePosixPath

from ...game_utils.audio_duration import measure_audio_duration_ticks

TICKS_PER_SECOND = 20

SOUND_CALL = "game_bingo/call.ogg"
SOUND_SUSPENSE = "game_bingo/suspense.ogg"

# Measured from the checked-in assets (see
# test_bingo_timed_audio_is_measured_from_the_shipped_assets); used only as the
# fallback when the actual file cannot be measured.
AUDIO_DURATIONS_TICKS = {
    SOUND_CALL: 68,
    SOUND_SUSPENSE: 42,
}

BINGO_TIMED_ASSET_PATHS = tuple(AUDIO_DURATIONS_TICKS)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


@cache
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
