"""Run the sound manager against the real Cosmos engine, silently.

The fake-stream tests prove the manager's bookkeeping under assumptions about
the engine; these prove the assumptions. Skipped where the cosmos wheel is not
installed or no audio device can be opened.
"""

import importlib.metadata
import importlib.util
from pathlib import Path
import sys
import time

import pytest

CLIENT_DIR = Path(__file__).resolve().parents[1]
CLICK = "menuclick.ogg"

pytest.importorskip("cosmos")

# Before 0.3.1 an HRTF sound reported playing from creation and forever after.
HRTF_COMPLETION_FIXED = tuple(
    int(part) for part in importlib.metadata.version("cosmos").split(".")[:3]
) >= (0, 3, 1)


@pytest.fixture(scope="module")
def manager():
    if str(CLIENT_DIR) not in sys.path:
        sys.path.insert(0, str(CLIENT_DIR))
    spec = importlib.util.spec_from_file_location(
        "sound_manager_real_engine", CLIENT_DIR / "sound_manager.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        instance = module.SoundManager()
    except Exception as error:  # no audio device on this machine
        pytest.skip(f"Cosmos could not open an audio device: {error}")
    instance.set_sound_volume(0)
    return instance


def _wait_until(condition, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.01)
    return condition()


def _segment(position):
    return {
        "asset": CLICK,
        "position": position,
        "destination_position": None,
        "attenuation": None if position is None else {"model": "none"},
        "gain": 1,
        "easing": "linear",
    }


def _play_chain(manager, handle, positions):
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "handle": handle,
        "segments": [_segment(position) for position in positions],
    }) is True
    return manager._sources[handle]


def test_unpositioned_chain_plays_every_segment_then_releases(manager):
    source = _play_chain(manager, "chain:direct", [None, None, None])
    cacher = manager.sound_cacher
    last = source.sequence_streams[-1]
    seconds = (source.completion_frame - cacher.clock_frames) / cacher.sample_rate

    # Every segment must become audible in turn; none may be stopped early.
    assert _wait_until(lambda: last.stream.is_playing, seconds + 1)
    assert manager._sources.get("chain:direct") is source
    assert _wait_until(lambda: "chain:direct" not in manager._sources, seconds + 2)


@pytest.mark.skipif(not HRTF_COMPLETION_FIXED, reason="needs the Cosmos 0.3.1 wheel")
def test_positioned_sound_in_headphone_mode_finishes_and_is_dropped(manager):
    cacher = manager.sound_cacher
    if not cacher.hrtf_available:
        pytest.skip("Steam Audio HRTF is unavailable")
    cacher.spatial_mode = "headphones"
    try:
        prepared = cacher.create(str(CLIENT_DIR / "sounds" / CLICK), position=(2, 1, 0))
        time.sleep(0.1)
        assert prepared.is_playing is False  # never started

        source = _play_chain(manager, "chain:hrtf", [[2, 1, 0], [-2, 1, 0]])
        streams = [item.stream for item in source.sequence_streams]
        seconds = (source.completion_frame - cacher.clock_frames) / cacher.sample_rate
        assert _wait_until(lambda: "chain:hrtf" not in manager._sources, seconds + 2)
        assert not any(stream in cacher.refs for stream in streams)
    finally:
        cacher.spatial_mode = "stereo"
