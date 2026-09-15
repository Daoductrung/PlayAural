"""Exercise the Cosmos-backed sound cacher against the real engine.

Skipped where the cosmos wheel is not installed (any non-Windows CI) and
where no audio device can be opened.
"""

import importlib.util
from pathlib import Path
import sys
import threading

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]
CLICK = str(CLIENT_DIR / "sounds" / "menuclick.ogg")

cosmos = pytest.importorskip("cosmos")


def _load_sound_cacher():
    if str(CLIENT_DIR) not in sys.path:
        sys.path.insert(0, str(CLIENT_DIR))
    spec = importlib.util.spec_from_file_location(
        "sound_cacher_under_test", CLIENT_DIR / "sound_cacher.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def cacher():
    module = _load_sound_cacher()
    try:
        return module.SoundCacher()
    except Exception as error:  # no audio device on this machine
        pytest.skip(f"Cosmos could not open an audio device: {error}")


def test_create_applies_requested_parameters_before_playback(cacher):
    stream = cacher.create(CLICK, pan=0.5, volume=0.25, pitch=1.5, looping=True)

    assert stream.is_playing is False
    assert stream.pan == pytest.approx(0.5)
    assert stream.volume == pytest.approx(0.25)
    assert stream.pitch == pytest.approx(1.5)
    assert stream.looping is True
    assert stream.position is None


def test_plain_cue_keeps_its_pan_when_volume_changes(cacher):
    stream = cacher.create(CLICK, pan=-0.75)

    stream.volume = 0.5

    assert stream.pan == pytest.approx(-0.75)


def test_volume_can_be_set_from_another_thread(cacher):
    stream = cacher.play(CLICK, volume=1.0)
    outcome = {}

    def worker():
        try:
            stream.volume = 0.3
            outcome["volume"] = stream.volume
        except BaseException as error:  # a pyo3 panic is not an Exception
            outcome["error"] = repr(error)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    assert outcome == {"volume": pytest.approx(0.3)}


def test_positioned_cue_reports_its_position_and_clears_to_direct(cacher):
    cacher.spatial_mode = "stereo"
    stream = cacher.create(CLICK, position=(2, 0, 0))

    assert stream.position == (2.0, 0.0, 0.0)
    # A seat to the right pans right in stereo mode.
    assert stream.pan > 0.5

    stream.position = None
    stream.pan = 0.0
    assert stream.position is None
    assert stream.pan == pytest.approx(0.0)


def test_headphone_mode_uses_full_bilinear_hrtf_without_detuning(cacher):
    cacher.spatial_mode = "headphones"
    stream = cacher.create(CLICK, pitch=1.25, position=(0, -2, 1))

    assert stream._sound.hrtf_interpolation == "bilinear"
    assert stream._sound.hrtf_spatial_blend == pytest.approx(1.0)
    assert stream._sound.min_gain == pytest.approx(1.0)
    assert stream._sound.max_gain == pytest.approx(1.0)
    assert stream._sound.volume_step == pytest.approx(0.0)
    assert stream._sound.behind_pitch_decrease == pytest.approx(0.0)
    assert stream.pitch == pytest.approx(1.25)


def test_cosmos_rejects_non_finite_runtime_parameters(cacher):
    stream = cacher.create(CLICK, volume=0.6, pitch=1.2, position=(2, 0, 0))

    stream._sound.position = (float("nan"), 5, 0)
    stream.volume = float("nan")
    stream.pitch = float("inf")

    assert stream._sound.position == (2.0, 0.0, 0.0)
    assert stream.volume == pytest.approx(0.6)
    assert stream.pitch == pytest.approx(1.2)

    with pytest.raises(ValueError, match="finite and in range"):
        stream.position = (float("nan"), 5, 0)
    assert stream.position == (2.0, 0.0, 0.0)

    with pytest.raises(ValueError, match="finite and in range"):
        stream.position = (5000, 0, 0)
    assert stream.position == (2.0, 0.0, 0.0)


def test_hrtf_position_updates_are_safe_while_audio_is_rendering(cacher):
    if not cacher.hrtf_available:
        pytest.skip("Steam Audio HRTF is unavailable")
    cacher.spatial_mode = "headphones"
    stream = cacher.create(CLICK, looping=True, position=(0, 2, 0))
    positions = ((0, 2, 0), (2, 0, 0), (0, -2, 0), (-2, 0, 0), (0, 0, 2))
    outcome = {}

    def move_source():
        try:
            for index in range(1000):
                stream._sound.position = positions[index % len(positions)]
        except BaseException as error:
            outcome["error"] = repr(error)

    stream.play()
    try:
        thread = threading.Thread(target=move_source)
        thread.start()
        thread.join(timeout=5)
        assert thread.is_alive() is False
        assert outcome == {}
        assert stream._sound.position == positions[999 % len(positions)]
    finally:
        stream.stop()


def test_multiple_managers_share_hrtf_lifetime_but_not_audio_caches(cacher):
    module = _load_sound_cacher()
    other = module.SoundCacher()

    assert other.hrtf_available is cacher.hrtf_available
    first_stream = cacher.create(CLICK, volume=0.2)
    other_stream = other.create(CLICK, volume=0.8)
    assert first_stream.volume == pytest.approx(0.2)
    assert other_stream.volume == pytest.approx(0.8)


def test_missing_asset_raises_so_the_manager_can_skip_it(cacher):
    with pytest.raises(RuntimeError):
        cacher.create(str(CLIENT_DIR / "sounds" / "does-not-exist.ogg"))


def test_pinned_streams_stay_until_unpinned(cacher):
    # The manager pins every stream it creates and unpins on release; an
    # unpinned stream that is not playing is dropped at the next clean.
    stream = cacher.create(CLICK, pinned=True)
    assert stream in cacher.refs

    cacher.unpin(stream)

    assert stream not in cacher.refs
    assert cacher.create(CLICK) not in cacher.refs
