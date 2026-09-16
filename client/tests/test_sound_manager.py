import importlib.util
import sys
import time
import types
from pathlib import Path

import pytest

CLIENT_DIR = Path(__file__).resolve().parents[1]


class FakeStream:
    def __init__(self):
        self.is_playing = True
        self.volume = 1.0
        self.looping = False
        self.paused = False
        self.stopped = False

    def stop(self):
        self.stopped = True
        self.is_playing = False

    def pause(self):
        self.paused = True
        self.is_playing = False

    def play(self):
        self.paused = False
        self.is_playing = True


class FakeSoundCacher:
    def __init__(self):
        self.cache = {}
        self.refs = []
        self.pinned = set()

    def create(
        self,
        file_name,
        pan=0.0,
        volume=1.0,
        pitch=1.0,
        looping=False,
        pinned=False,
        position=None,
    ):
        stream = FakeStream()
        stream.file_name = file_name
        stream.pan = pan
        stream.volume = volume
        stream.pitch = pitch
        stream.looping = looping
        stream.position = position
        stream.is_playing = False
        self.refs.append(stream)
        if pinned:
            self.pinned.add(id(stream))
        return stream

    def play(
        self,
        file_name,
        pan=0.0,
        volume=1.0,
        pitch=1.0,
        looping=False,
        pinned=False,
        position=None,
    ):
        stream = self.create(
            file_name,
            pan=pan,
            volume=volume,
            pitch=pitch,
            looping=looping,
            pinned=pinned,
            position=position,
        )
        stream.play()
        return stream

    def pin(self, stream):
        self.pinned.add(id(stream))

    def unpin(self, stream):
        self.pinned.discard(id(stream))


def _load_sound_manager_module(monkeypatch):
    monkeypatch.syspath_prepend(str(CLIENT_DIR))
    fake_sound_cacher = types.ModuleType("sound_cacher")
    fake_sound_cacher.SoundCacher = FakeSoundCacher
    monkeypatch.setitem(sys.modules, "sound_cacher", fake_sound_cacher)

    spec = importlib.util.spec_from_file_location(
        "sound_manager_under_test", CLIENT_DIR / "sound_manager.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_sound_volume_updates_currently_playing_effects(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    manager.set_sound_volume(0.5)
    stream = manager.play("roll.ogg", volume=0.8)

    assert stream.volume == pytest.approx(0.4)

    manager.set_sound_volume(0.25)

    assert stream.volume == pytest.approx(0.2)


def test_sound_volume_can_mute_active_effects(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    stream = manager.play("roll.ogg", volume=1.0)

    manager.set_sound_volume(0)

    assert stream.volume == pytest.approx(0)


def test_numbered_sound_family_is_discovered_and_randomly_selected(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    variants = manager._sound_family_variants("notify")

    expected = tuple(
        path.name
        for path in sorted(
            (
                path
                for path in (CLIENT_DIR / "sounds").glob("notify[1-9]*.ogg")
                if path.stem.removeprefix("notify").isdigit()
            ),
            key=lambda path: int(path.stem.removeprefix("notify")),
        )
    )
    assert variants == expected
    assert set(f"notify{index}.ogg" for index in range(1, 5)) <= set(variants)

    monkeypatch.setattr(sound_manager.random, "choice", lambda choices: choices[-1])
    stream = manager.play_family("notify")

    assert stream.file_name.endswith(variants[-1])


def test_looping_effect_stops_only_matching_handle(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    fuse = manager.play("fuse.ogg", looping=True, handle="bomb:fuse")
    hiss = manager.play("hiss.ogg", looping=True, handle="bomb:hiss")

    manager.stop_sound("bomb:fuse")

    assert fuse.stopped is True
    assert hiss.stopped is False


def test_ducking_restores_music_bus_after_effect_stops(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    music = manager._play_layer(
        {
            "kind": "music",
            "asset": "music.ogg",
            "handle": "music",
            "bus": "music",
            "scope": "global",
            "layer": "main",
            "loop": True,
        }
    )
    effect = manager.play(
        "alert.ogg",
        looping=True,
        handle="alert",
        ducking={"music": 0.25},
    )

    assert music.stream.volume == pytest.approx(manager.music_volume * 0.25)
    manager.stop_sound("alert")
    assert effect.stopped is True
    assert music.stream.volume == pytest.approx(manager.music_volume)


def test_paused_music_remains_managed_and_resumes(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    music = manager.music("music.ogg", fade_in_ms=0)

    manager.pause_music(fade_ms=0)

    assert music.stream.paused is True
    assert "music" in manager._sources

    manager.resume_music(fade_ms=0)

    assert music.stream.paused is False
    assert music.stream.is_playing is True
    assert music.stream.volume == pytest.approx(manager.music_volume)


def test_client_owned_music_layer_is_independently_addressable(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    connection = manager.music(
        "connectloop.ogg",
        handle="client:connection",
        layer="connection",
        fade_in_ms=0,
    )
    game = manager.music("game.ogg", fade_in_ms=0)

    assert manager.has_managed_audio(
        "music",
        handle="client:connection",
        asset="connectloop.ogg",
    )
    manager.stop_music(fade=False, handle="client:connection")

    assert connection.stream.stopped is True
    assert game.stream.stopped is False
    assert manager.has_managed_audio(
        "music",
        handle="music",
        asset="game.ogg",
    )


def test_replacing_managed_effect_retires_old_source(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    old = manager.play("old.ogg", looping=True, handle="machine")

    new = manager.play(
        "new.ogg",
        looping=True,
        handle="machine",
        fade_out_ms=0,
    )

    assert old.stopped is True
    assert new.stopped is False
    assert manager._sources["machine"].stream is new


def test_ambience_loop_to_outro_has_no_fade_or_load_delay(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    ambience = manager.ambience(
        "",
        "rain.ogg",
        "rain_out.ogg",
        pitch=1.5,
        fade_in_ms=0,
        fade_out_ms=0,
    )

    loop_stream = ambience.stream
    manager.stop_ambience(fade_ms=500, outro_mode="boundary")

    assert loop_stream.stopped is False
    assert loop_stream.looping is False
    prepared_outro = next(
        stream
        for stream in manager.sound_cacher.refs
        if stream.file_name.endswith("rain_out.ogg")
    )
    assert prepared_outro.is_playing is False
    assert prepared_outro.volume == pytest.approx(manager.ambience_volume)
    assert loop_stream.pitch == pytest.approx(1.5)
    assert prepared_outro.pitch == pytest.approx(1.5)

    loop_stream.is_playing = False
    for _ in range(50):
        if prepared_outro.is_playing:
            break
        time.sleep(0.005)

    assert prepared_outro.is_playing is True
    outro = next(iter(manager._sources.values()))
    assert outro.asset == "rain_out.ogg"
    assert outro.kind == "ambience"
    assert outro.bus == "ambience"
    assert outro.envelope == pytest.approx(1)


def test_ambience_immediate_outro_does_not_wait_for_long_loop(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    ambience = manager.ambience(
        "",
        "pirates_loop.ogg",
        "pirates_outro.ogg",
        fade_in_ms=0,
        fade_out_ms=0,
    )

    loop_stream = ambience.stream
    manager.stop_ambience(fade_ms=1200)

    active = next(iter(manager._sources.values()))
    assert loop_stream.stopped is True
    assert active.asset == "pirates_outro.ogg"
    assert active.stream.is_playing is True
    assert active.envelope == pytest.approx(1)
    assert manager._targets["ambience:global::environment"] == active.handle


def test_stop_all_can_preserve_every_ambience_outro(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    manager.ambience(
        "",
        "weather.ogg",
        "weather_out.ogg",
        fade_in_ms=0,
        handle="weather",
        layer="weather",
    )
    manager.ambience(
        "",
        "ocean.ogg",
        "ocean_out.ogg",
        fade_in_ms=0,
        handle="ocean",
        layer="ocean",
    )

    manager.stop_all(800, play_outros=True)

    assert {source.asset for source in manager._sources.values()} == {
        "weather_out.ogg",
        "ocean_out.ogg",
    }


def test_ambience_intro_to_loop_reuses_envelope_without_crossfade(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    intro_source = manager.ambience(
        "rain_in.ogg",
        "rain.ogg",
        "rain_out.ogg",
        pitch=0.75,
        fade_in_ms=0,
        fade_out_ms=500,
    )
    intro_stream = intro_source.stream
    prepared_loop = next(
        stream
        for stream in manager.sound_cacher.refs
        if stream.file_name.endswith("rain.ogg")
    )

    assert intro_stream.is_playing is True
    assert prepared_loop.is_playing is False
    assert intro_stream.pitch == pytest.approx(0.75)
    assert prepared_loop.pitch == pytest.approx(0.75)

    intro_stream.is_playing = False
    for _ in range(50):
        if prepared_loop.is_playing:
            break
        time.sleep(0.005)

    active = manager._sources["ambience:global:default:environment"]
    assert active.asset == "rain.ogg"
    assert active.stream is prepared_loop
    assert prepared_loop.is_playing is True
    assert active.envelope == pytest.approx(1)
    assert prepared_loop.volume == pytest.approx(manager.ambience_volume)


def test_named_bus_gain_updates_active_sources(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    music = manager.music("music.ogg", fade_in_ms=0)

    accepted = manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "set_bus",
            "bus": "music",
            "volume": 50,
        }
    )

    assert accepted is True
    assert music.stream.volume == pytest.approx(manager.music_volume * 0.5)


def test_malformed_protocol_version_is_rejected_without_raising(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.handle_audio_command(
        {"version": "invalid", "command": "stop_all"}
    ) is False
    assert manager.handle_audio_command(
        {"version": "3", "command": "stop_all"}
    ) is False
    assert manager.handle_audio_command(
        {"version": 3.0, "command": "stop_all"}
    ) is False
    assert manager.handle_audio_command(
        {"version": 3, "command": "stop_all", "ducking": []}
    ) is False
    assert manager.handle_audio_command(
        {"version": 3, "command": "stop_all", "family": "notify"}
    ) is False
    assert manager.handle_audio_command(
        {"version": 3, "command": "stop_all", "buffer": "private"}
    ) is False
    assert manager.handle_audio_command(
        {
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "asset": "pm.ogg",
            "buffer": "unknown",
        }
    ) is False


def test_audio_protocol_resolves_numbered_sound_family(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    monkeypatch.setattr(sound_manager.random, "choice", lambda choices: choices[0])

    assert manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "family": "notify",
        }
    ) is True
    assert manager.sound_cacher.refs[-1].file_name.endswith("notify1.ogg")
    assert manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "asset": "roll.ogg",
            "family": "notify",
        }
    ) is False
    assert manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "family": "notify",
            "loop": True,
            "handle": "invalid:family-loop",
        }
    ) is False


def test_audio_protocol_threads_position_through_to_the_stream(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "asset": "roll.ogg",
            "position": [2, 0, 0],
        }
    ) is True
    assert manager.sound_cacher.refs[-1].position == (2.0, 0.0, 0.0)

    for bad in (
        [1, 2],
        "north",
        [1, "x", 3],
        ["1", 0, 0],
        [True, 0, 0],
        [float("inf"), 0, 0],
        [5000, 0, 0],
    ):
        assert manager.handle_audio_command(
            {
                "type": "audio",
                "version": 3,
                "command": "play",
                "kind": "sfx",
                "asset": "roll.ogg",
                "position": bad,
            }
        ) is False


def test_spatial_mode_is_normalized_and_forwarded_to_the_backend(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.spatial_mode == "headphones"
    assert manager.set_spatial_mode("STEREO") == "stereo"
    assert manager.sound_cacher.spatial_mode == "stereo"
    assert manager.set_spatial_mode("nonsense") == "headphones"


def test_audio_protocol_rejects_position_on_non_play_command(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "stop",
        "kind": "sfx",
        "handle": "test",
        "position": [1, 0, 0],
    }) is False


def test_audio_protocol_applies_explicit_distance_gain_once(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()
    attenuation = {
        "model": "linear",
        "reference_distance": 2,
        "max_distance": 10,
        "rolloff_factor": 1,
        "min_gain": 0,
        "max_gain": 1,
    }

    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "asset": "roll.ogg",
        "handle": "test:attenuated",
        "volume": 80,
        "position": [6, 0, 0],
        "attenuation": attenuation,
    }) is True

    source = manager._sources["test:attenuated"]
    assert source.distance_gain == pytest.approx(0.5)
    assert source.stream.volume == pytest.approx(0.4)


def test_audio_protocol_moves_source_and_recomputes_attenuation(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    monkeypatch.setattr(sound_manager, "SOURCE_AUTOMATION_INTERVAL_S", 10)
    manager = sound_manager.SoundManager()
    attenuation = {
        "model": "linear",
        "reference_distance": 1,
        "max_distance": 11,
        "rolloff_factor": 1,
        "min_gain": 0,
        "max_gain": 1,
    }
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "asset": "roll.ogg",
        "handle": "test:moving",
        "loop": True,
        "position": [0, 1, 0],
        "attenuation": attenuation,
    }) is True
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "update",
        "kind": "sfx",
        "handle": "test:moving",
        "motion": {
            "origin_position": [0, 1, 0],
            "destination_position": [0, 11, 0],
            "duration_ms": 1000,
            "elapsed_ms": 0,
            "easing": "linear",
        },
    }) is True

    runtime = manager._motions["test:moving"]
    source = manager._sources["test:moving"]
    with manager._lock:
        assert manager._apply_motion_to_source_locked(
            source,
            runtime,
            runtime.started_at + 0.5,
        ) is False
    assert source.position == pytest.approx((0, 6, 0))
    assert source.stream.position == pytest.approx((0, 6, 0))
    assert source.distance_gain == pytest.approx(0.5)
    assert source.stream.volume == pytest.approx(0.5)

    with manager._lock:
        assert manager._apply_motion_to_source_locked(
            source,
            runtime,
            runtime.started_at + 1,
        ) is True
    assert source.position == pytest.approx((0, 11, 0))
    assert source.stream.volume == pytest.approx(0)

    manager.stop_sound("test:moving")
    assert "test:moving" not in manager._motions


def test_audio_protocol_automates_gain_concurrently_with_motion(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    monkeypatch.setattr(sound_manager, "SOURCE_AUTOMATION_INTERVAL_S", 10)
    manager = sound_manager.SoundManager()
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "asset": "roll.ogg",
        "handle": "test:automated",
        "loop": True,
        "position": [0, 1, 0],
        "gain": 0.2,
    }) is True
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "update",
        "kind": "sfx",
        "handle": "test:automated",
        "motion": {
            "origin_position": [0, 1, 0],
            "destination_position": [0, 3, 0],
            "duration_ms": 1000,
            "elapsed_ms": 0,
            "easing": "linear",
        },
        "gain_automation": {
            "origin_gain": 0.2,
            "destination_gain": 0.8,
            "duration_ms": 1000,
            "elapsed_ms": 0,
            "easing": "linear",
        },
    }) is True

    source = manager._sources["test:automated"]
    motion = manager._motions["test:automated"]
    gain = manager._gain_automations["test:automated"]
    with manager._lock:
        manager._apply_motion_to_source_locked(
            source, motion, motion.started_at + 0.5
        )
        manager._apply_gain_to_source_locked(
            source, gain, gain.started_at + 0.5
        )
    assert source.position == pytest.approx((0, 2, 0))
    assert source.source_gain == pytest.approx(0.5)
    assert source.stream.volume == pytest.approx(0.5)

    manager.stop_sound("test:automated")
    assert "test:automated" not in manager._motions
    assert "test:automated" not in manager._gain_automations


def test_replacing_a_moving_source_cancels_stale_motion(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    monkeypatch.setattr(sound_manager, "SOURCE_AUTOMATION_INTERVAL_S", 10)
    manager = sound_manager.SoundManager()
    manager.play(
        "roll.ogg",
        looping=True,
        handle="test:moving",
        position=(0, 1, 0),
    )
    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "update",
        "kind": "sfx",
        "handle": "test:moving",
        "motion": {
            "origin_position": [0, 1, 0],
            "destination_position": [0, 2, 0],
            "duration_ms": 1000,
            "elapsed_ms": 0,
            "easing": "linear",
        },
    }) is True

    replacement = manager.play(
        "notify1.ogg",
        looping=True,
        handle="test:moving",
        position=(1, 0, 0),
        fade_out_ms=0,
    )

    assert "test:moving" not in manager._motions
    assert manager._sources["test:moving"].stream is replacement
    assert replacement.position == (1, 0, 0)


def test_motion_expires_when_source_loading_failed(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    monkeypatch.setattr(sound_manager, "SOURCE_AUTOMATION_INTERVAL_S", 0.001)
    manager = sound_manager.SoundManager()
    manager._next_generation("test:failed-load")

    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "update",
        "kind": "sfx",
        "handle": "test:failed-load",
        "motion": {
            "origin_position": [0, 1, 0],
            "destination_position": [0, 2, 0],
            "duration_ms": 1,
            "elapsed_ms": 0,
            "easing": "linear",
        },
    }) is True

    for _ in range(100):
        if "test:failed-load" not in manager._motions:
            break
        time.sleep(0.001)
    assert "test:failed-load" not in manager._motions


@pytest.mark.parametrize(
    "attenuation",
    [
        {"model": "linear"},
        {
            "model": "linear",
            "reference_distance": 2,
            "max_distance": 10,
            "rolloff_factor": 2,
            "min_gain": 0,
            "max_gain": 1,
        },
        {
            "model": "inverse",
            "reference_distance": 10,
            "max_distance": 2,
            "rolloff_factor": 1,
            "min_gain": 0,
            "max_gain": 1,
        },
        {
            "model": "none",
            "reference_distance": 2,
        },
    ],
)
def test_audio_protocol_rejects_invalid_attenuation(monkeypatch, attenuation):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "asset": "roll.ogg",
        "position": [6, 0, 0],
        "attenuation": attenuation,
    }) is False


def test_audio_protocol_rejects_attenuation_without_position(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    assert manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "asset": "roll.ogg",
        "attenuation": {"model": "none"},
    }) is False


def test_audio_protocol_plays_numbered_asset_exactly_even_when_looping(monkeypatch):
    sound_manager = _load_sound_manager_module(monkeypatch)
    manager = sound_manager.SoundManager()

    def reject_family_selection(_choices):
        raise AssertionError("exact asset playback attempted family selection")

    monkeypatch.setattr(sound_manager.random, "choice", reject_family_selection)

    assert manager.handle_audio_command(
        {
            "type": "audio",
            "version": 3,
            "command": "play",
            "kind": "sfx",
            "asset": "notify2.ogg",
            "loop": True,
            "handle": "test:numbered-loop",
        }
    ) is True
    source = manager._sources["test:numbered-loop"]
    assert source.asset == "notify2.ogg"
    assert source.stream.file_name.endswith("notify2.ogg")
    assert source.stream.looping is True
