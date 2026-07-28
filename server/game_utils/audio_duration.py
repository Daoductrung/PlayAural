"""Dependency-free duration measurement for server-timed audio assets."""

from __future__ import annotations

import math
import struct
import wave
from functools import lru_cache
from pathlib import Path


def measure_audio_duration_ticks(
    path: Path,
    *,
    ticks_per_second: int,
) -> int | None:
    """Return a WAV/OGG duration in ticks, or ``None`` when unavailable."""

    if ticks_per_second <= 0:
        raise ValueError("ticks_per_second must be positive")
    try:
        stat = path.stat()
    except OSError:
        return None
    absolute = path.absolute()
    return _measure_cached(
        str(absolute),
        stat.st_mtime_ns,
        stat.st_size,
        ticks_per_second,
    )


@lru_cache(maxsize=1024)
def _measure_cached(
    path_text: str,
    modified_ns: int,
    size: int,
    ticks_per_second: int,
) -> int | None:
    """Measure a stable file revision; metadata arguments invalidate the cache."""

    del modified_ns, size
    path = Path(path_text)
    try:
        if path.suffix.lower() == ".wav":
            with wave.open(str(path), "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
            if frames <= 0 or sample_rate <= 0:
                return None
            return math.ceil(frames * ticks_per_second / sample_rate)
        if path.suffix.lower() == ".ogg":
            return _measure_ogg_ticks(path, ticks_per_second)
    except (OSError, EOFError, struct.error, wave.Error):
        return None
    return None


def _measure_ogg_ticks(path: Path, ticks_per_second: int) -> int | None:
    with path.open("rb") as audio_file:
        header = audio_file.read(65536)
        audio_file.seek(0, 2)
        file_size = audio_file.tell()
        tail_size = min(file_size, 131072)
        audio_file.seek(file_size - tail_size)
        tail = audio_file.read(tail_size)

    identification = header.find(b"\x01vorbis")
    if identification < 0 or identification + 16 > len(header):
        return None
    sample_rate = struct.unpack_from("<I", header, identification + 12)[0]
    if sample_rate <= 0:
        return None

    page = tail.rfind(b"OggS")
    while page >= 0:
        if page + 27 > len(tail):
            page = tail.rfind(b"OggS", 0, page)
            continue
        segment_count = tail[page + 26]
        segment_table_end = page + 27 + segment_count
        if segment_table_end > len(tail):
            page = tail.rfind(b"OggS", 0, page)
            continue
        body_size = sum(tail[page + 27 : segment_table_end])
        page_end = segment_table_end + body_size
        if page_end <= len(tail):
            final_granule = struct.unpack_from("<Q", tail, page + 6)[0]
            if final_granule not in {0, 0xFFFFFFFFFFFFFFFF}:
                return math.ceil(
                    final_granule * ticks_per_second / sample_rate
                )
        page = tail.rfind(b"OggS", 0, page)
    return None
