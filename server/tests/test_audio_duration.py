"""Tests for dependency-free server audio-duration measurement."""

from __future__ import annotations

import wave
from pathlib import Path

import pytest

from ..game_utils.audio_duration import measure_audio_duration_ticks


def _write_silent_wav(path: Path, *, frames: int, sample_rate: int) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\0\0" * frames)


def test_measure_audio_duration_ticks_reads_wav_and_invalidates_replacement(
    tmp_path: Path,
) -> None:
    sound = tmp_path / "cue.wav"
    _write_silent_wav(sound, frames=500, sample_rate=1000)
    assert measure_audio_duration_ticks(sound, ticks_per_second=20) == 10

    _write_silent_wav(sound, frames=1000, sample_rate=1000)
    assert measure_audio_duration_ticks(sound, ticks_per_second=20) == 20


def test_measure_audio_duration_ticks_handles_unavailable_assets(
    tmp_path: Path,
) -> None:
    assert (
        measure_audio_duration_ticks(
            tmp_path / "missing.ogg",
            ticks_per_second=20,
        )
        is None
    )
    unsupported = tmp_path / "cue.mp3"
    unsupported.write_bytes(b"not audio")
    assert (
        measure_audio_duration_ticks(
            unsupported,
            ticks_per_second=20,
        )
        is None
    )


def test_measure_audio_duration_ticks_rejects_invalid_tick_rate(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError):
        measure_audio_duration_ticks(
            tmp_path / "cue.wav",
            ticks_per_second=0,
        )
