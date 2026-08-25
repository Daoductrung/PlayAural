"""Race-safe, handle-based audio engine for the desktop client."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
import random
import re
import threading
import time
import uuid

from sound_cacher import SoundCacher
from sound_lib.external import pybass


AUDIO_PROTOCOL_VERSION = 2
MAX_ACTIVE_EFFECTS = 64
MAX_ACTIVE_LAYERS = 32
MAX_SOUND_FAMILY_CACHE = 64
MAX_GENERATION_ENTRIES = 512
MAX_FADE_MS = 60_000
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def _clamp(value, minimum, maximum, default):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


@dataclass
class _AudioSource:
    handle: str
    stream: object
    kind: str
    bus: str
    asset: str
    base_volume: float
    priority: int = 0
    target: str = ""
    outro: str = ""
    ducking: dict[str, float] = field(default_factory=dict)
    generation: int = 0
    created_at: float = field(default_factory=time.monotonic)
    paused: bool = False
    envelope: float = 1.0
    fade_token: int = 0
    seamless: bool = True
    stopping: bool = False
    queued_streams: list[object] = field(default_factory=list)
    backend_callbacks: list[object] = field(default_factory=list)


class SoundManager:
    """Mix SFX, music, and scoped ambience through one lifecycle API."""

    def __init__(self):
        self.sound_cacher = SoundCacher()
        self.music_volume = 0.2
        self.sound_volume = 1.0
        self.ambience_volume = 0.3
        self.menuclick_sound = "menuclick.ogg"
        self.menuenter_sound = "menuenter.ogg"

        import sys

        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
            internal_path = os.path.join(base_path, "_internal")
            if os.path.exists(internal_path):
                base_path = internal_path
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.sounds_folder = os.path.realpath(os.path.join(base_path, "sounds"))

        self._lock = threading.RLock()
        self._sources: dict[str, _AudioSource] = {}
        self._targets: dict[str, str] = {}
        self._generations: dict[str, int] = {}
        self._bus_gains: dict[str, float] = {}
        self._bus_fade_tokens: dict[str, int] = {}
        self._duck_requests: dict[str, dict[str, float]] = {}
        self._sound_family_cache: dict[str, tuple[str, ...]] = {}

    # ------------------------------------------------------------------
    # Validation and low-level stream lifecycle
    # ------------------------------------------------------------------

    def _asset_path(self, name: str) -> str | None:
        normalized = str(name or "").strip().replace("\\", "/")
        if (
            not normalized
            or len(normalized) > 256
            or normalized.startswith("/")
            or ":" in normalized
            or "?" in normalized
            or "#" in normalized
            or any(part in {"", ".", ".."} for part in normalized.split("/"))
        ):
            return None
        resolved = os.path.realpath(os.path.join(self.sounds_folder, *normalized.split("/")))
        try:
            if os.path.commonpath((self.sounds_folder, resolved)) != self.sounds_folder:
                return None
        except ValueError:
            return None
        return resolved

    def _sound_family_variants(self, family: str) -> tuple[str, ...]:
        """Discover members only for an explicit family playback request.

        Numbered files remain ordinary, exactly addressable assets everywhere
        else; their names alone never opt a play command into randomization.
        """
        normalized = str(family or "").strip().replace("\\", "/")
        cached = self._sound_family_cache.get(normalized)
        if cached is not None:
            return cached
        if not normalized or os.path.splitext(normalized.rsplit("/", 1)[-1])[1]:
            return ()

        probe = self._asset_path(f"{normalized}1.ogg")
        if not probe:
            return ()
        directory = os.path.dirname(probe)
        stem = normalized.rsplit("/", 1)[-1]
        pattern = re.compile(
            rf"^{re.escape(stem)}([1-9][0-9]*)\.(ogg|wav|mp3)$",
            re.IGNORECASE,
        )
        matches: list[tuple[int, str]] = []
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    match = pattern.fullmatch(entry.name)
                    if not entry.is_file() or not match:
                        continue
                    relative = os.path.relpath(
                        entry.path,
                        self.sounds_folder,
                    ).replace(os.sep, "/")
                    matches.append((int(match.group(1)), relative))
        except OSError:
            pass
        variants = tuple(path for _, path in sorted(matches))
        self._sound_family_cache[normalized] = variants
        while len(self._sound_family_cache) > MAX_SOUND_FAMILY_CACHE:
            self._sound_family_cache.pop(next(iter(self._sound_family_cache)))
        return variants

    def _choose_sound_family_variant(self, family: str) -> str:
        variants = self._sound_family_variants(family)
        return random.choice(variants) if variants else ""

    @staticmethod
    def _valid_id(value):
        return bool(_ID_PATTERN.fullmatch(str(value or "")))

    @staticmethod
    def _stream_is_playing(stream_obj):
        try:
            return bool(getattr(stream_obj, "is_playing", False))
        except Exception:
            return False

    @staticmethod
    def _set_stream_volume(stream_obj, volume):
        try:
            stream_obj.volume = _clamp(volume, 0.0, 1.0, 0.0)
        except Exception:
            pass

    @staticmethod
    def _stop_stream(stream_obj):
        try:
            stream_obj.stop()
        except Exception:
            pass

    @staticmethod
    def _start_stream(stream_obj):
        try:
            stream_obj.play()
            return True
        except Exception:
            return False

    @staticmethod
    def _set_stream_looping(stream_obj, looping):
        try:
            stream_obj.looping = bool(looping)
            return True
        except Exception:
            return False

    def _create_stream(
        self,
        asset: str,
        *,
        volume: float,
        pan: float = 0.0,
        pitch: float = 1.0,
        looping: bool = False,
        start: bool = True,
    ):
        path = self._asset_path(asset)
        if not path:
            return None
        try:
            if not start:
                stream_obj = self.sound_cacher.create(
                    path,
                    pan=pan,
                    volume=volume,
                    pitch=pitch,
                    looping=looping,
                    pinned=True,
                )
            else:
                stream_obj = self.sound_cacher.play(
                    path,
                    pan=pan,
                    volume=volume,
                    pitch=pitch,
                    looping=looping,
                    pinned=True,
                )
            if stream_obj is not None:
                self.sound_cacher.pin(stream_obj)
            return stream_obj
        except Exception:
            return None

    @staticmethod
    def _on_stream_end(stream_obj, callback) -> object | None:
        """Register the backend's end sync, retaining its ctypes callback."""
        handle = getattr(stream_obj, "handle", 0)
        if not handle:
            return None
        try:
            sync_callback = pybass.SYNCPROC(
                lambda _sync, _channel, _data, _user: callback()
            )
            sync_handle = pybass.BASS_ChannelSetSync(
                handle,
                pybass.BASS_SYNC_END
                | pybass.BASS_SYNC_MIXTIME
                | pybass.BASS_SYNC_ONETIME,
                0,
                sync_callback,
                None,
            )
            return sync_callback if sync_handle else None
        except Exception:
            return None

    def _next_generation(self, handle: str) -> int:
        generation = self._generations.get(handle, 0) + 1
        self._generations.pop(handle, None)
        self._generations[handle] = generation
        while len(self._generations) > MAX_GENERATION_ENTRIES:
            removable = next(
                (
                    candidate
                    for candidate in self._generations
                    if candidate not in self._sources
                ),
                None,
            )
            if removable is None:
                break
            self._generations.pop(removable, None)
        return generation

    def _master_gain(self, kind: str) -> float:
        if kind == "music":
            return self.music_volume
        if kind == "ambience":
            return self.ambience_volume
        return self.sound_volume

    def _duck_gain(self, bus: str) -> float:
        gains = [
            request[bus]
            for request in self._duck_requests.values()
            if bus in request
        ]
        return min(gains, default=1.0)

    def _base_mix_volume(self, source: _AudioSource) -> float:
        return (
            source.base_volume
            * self._master_gain(source.kind)
            * self._bus_gains.get(source.bus, 1.0)
            * self._duck_gain(source.bus)
        )

    def _effective_volume(self, source: _AudioSource) -> float:
        return self._base_mix_volume(source) * source.envelope

    def _apply_mix(self) -> None:
        with self._lock:
            for source in self._sources.values():
                if not source.paused:
                    self._set_stream_volume(
                        source.stream, self._effective_volume(source)
                    )

    def _set_bus_gain(self, bus: str, gain, fade_ms=0) -> None:
        target = _clamp(gain, 0, 100, 100) / 100
        duration_ms = int(_clamp(fade_ms, 0, MAX_FADE_MS, 0))
        with self._lock:
            start = self._bus_gains.get(bus, 1.0)
            token = self._bus_fade_tokens.get(bus, 0) + 1
            self._bus_fade_tokens[bus] = token

        def run():
            steps = max(1, min(100, duration_ms // 25))
            for index in range(steps + 1):
                with self._lock:
                    if self._bus_fade_tokens.get(bus) != token:
                        return
                    ratio = index / steps
                    self._bus_gains[bus] = start + ((target - start) * ratio)
                self._apply_mix()
                if duration_ms:
                    time.sleep(duration_ms / steps / 1000)

        if duration_ms:
            threading.Thread(target=run, daemon=True).start()
        else:
            run()

    def _fade(
        self,
        source: _AudioSource,
        duration_ms: int,
        *,
        fade_in: bool,
        stop: bool = False,
        pause: bool = False,
        play_outro: bool = False,
    ) -> None:
        duration_ms = int(_clamp(duration_ms, 0, MAX_FADE_MS, 0))
        generation = source.generation
        with self._lock:
            source.fade_token += 1
            fade_token = source.fade_token

        def run():
            steps = max(1, min(100, duration_ms // 25))
            start_envelope = 0.0 if fade_in else source.envelope
            for index in range(steps + 1):
                with self._lock:
                    if (
                        self._generations.get(source.handle) != generation
                        or source.fade_token != fade_token
                    ):
                        return
                    ratio = index / steps
                    source.envelope = (
                        ratio if fade_in else start_envelope * (1.0 - ratio)
                    )
                    volume = self._effective_volume(source)
                self._set_stream_volume(source.stream, volume)
                if duration_ms:
                    time.sleep(duration_ms / steps / 1000)
            with self._lock:
                if (
                    self._generations.get(source.handle) != generation
                    or source.fade_token != fade_token
                ):
                    return
            if stop:
                outro = source.outro if play_outro else ""
                outro_kind = source.kind
                outro_bus = source.bus
                outro_volume = source.base_volume
                outro_priority = source.priority
                self._stop_stream(source.stream)
                self._release_source(source.handle, generation)
                if outro:
                    outro_id = uuid.uuid4().hex
                    self._play_layer(
                        {
                            "kind": outro_kind,
                            "asset": outro,
                            "handle": f"outro:{outro_id}",
                            "bus": outro_bus,
                            "scope": "global",
                            "layer": f"outro:{outro_id}",
                            "loop": False,
                            "volume": round(outro_volume * 100),
                            "priority": outro_priority,
                        }
                    )
            elif pause:
                source.paused = True
                try:
                    source.stream.pause()
                except Exception:
                    source.paused = False
                    # A backend without pause support stops safely instead of
                    # leaving an inaudible stream consuming resources.
                    self._stop_stream(source.stream)
                    self._release_source(source.handle, generation)

        if duration_ms <= 0:
            run()
        else:
            threading.Thread(target=run, daemon=True).start()

    def _release_source(self, handle: str, generation: int | None = None) -> None:
        queued_streams = []
        with self._lock:
            source = self._sources.get(handle)
            if not source or (
                generation is not None and source.generation != generation
            ):
                return
            self._sources.pop(handle, None)
            self._duck_requests.pop(handle, None)
            if source.target and self._targets.get(source.target) == handle:
                self._targets.pop(source.target, None)
            queued_streams = list(source.queued_streams)
            source.queued_streams.clear()
            source.backend_callbacks.clear()
            self.sound_cacher.unpin(source.stream)
            self._apply_mix()
        for queued in queued_streams:
            self._stop_stream(queued)
            self.sound_cacher.unpin(queued)

    def _watch(self, source: _AudioSource) -> None:
        if getattr(source.stream, "looping", False):
            return

        def run():
            while True:
                with self._lock:
                    if self._sources.get(source.handle) is not source:
                        return
                    paused = source.paused
                if paused or self._stream_is_playing(source.stream):
                    time.sleep(0.05)
                    continue
                self._release_source(source.handle, source.generation)
                return

        threading.Thread(target=run, daemon=True).start()

    def _retire_handle(self, handle: str, fade_ms: int) -> None:
        with self._lock:
            old = self._sources.get(handle)
            if not old:
                return
            retired_handle = f"retired:{uuid.uuid4().hex}"
            self._sources.pop(old.handle, None)
            self._duck_requests.pop(old.handle, None)
            self._next_generation(old.handle)
            if old.target and self._targets.get(old.target) == old.handle:
                self._targets.pop(old.target, None)
            old.handle = retired_handle
            old.generation = self._next_generation(retired_handle)
            old.target = ""
            self._sources[retired_handle] = old
        self._fade(old, fade_ms, fade_in=False, stop=True)

    def _retire_target(self, target: str, fade_ms: int) -> None:
        with self._lock:
            handle = self._targets.get(target)
        if handle:
            self._retire_handle(handle, fade_ms)

    # ------------------------------------------------------------------
    # Public SFX API
    # ------------------------------------------------------------------

    def play(
        self,
        sound_name,
        volume=1.0,
        pan=0.0,
        pitch=1.0,
        *,
        looping=False,
        handle="",
        bus="sfx",
        fade_in_ms=0,
        fade_out_ms=0,
        priority=0,
        max_instances=0,
        ducking=None,
    ):
        """Play an effect; managed/looping calls may later stop by handle."""
        base_volume = _clamp(volume, 0.0, 1.0, 1.0)
        resolved_handle = str(handle or f"oneshot:{uuid.uuid4().hex}")
        with self._lock:
            same_asset = [
                source
                for source in self._sources.values()
                if source.kind == "sfx" and source.asset == sound_name
            ]
            limit = int(_clamp(max_instances, 0, MAX_ACTIVE_EFFECTS, 0))
            if limit and len(same_asset) >= limit:
                victim = min(same_asset, key=lambda item: (item.priority, item.created_at))
                if victim.priority > int(priority):
                    return None
                self._stop_handle(victim.handle, fade_ms=0)
            effects = [
                source for source in self._sources.values() if source.kind == "sfx"
            ]
            if len(effects) >= MAX_ACTIVE_EFFECTS:
                victim = min(effects, key=lambda item: (item.priority, item.created_at))
                if victim.priority > int(priority):
                    return None
                self._stop_handle(victim.handle, fade_ms=0)
            if resolved_handle in self._sources:
                self._retire_handle(resolved_handle, fade_out_ms)

            generation = self._next_generation(resolved_handle)
            stream_obj = self._create_stream(
                sound_name,
                volume=0.0 if fade_in_ms else base_volume * self.sound_volume,
                pan=_clamp(pan, -1.0, 1.0, 0.0),
                pitch=_clamp(pitch, 0.25, 4.0, 1.0),
                looping=bool(looping),
            )
            if not stream_obj:
                return None
            source = _AudioSource(
                handle=resolved_handle,
                stream=stream_obj,
                kind="sfx",
                bus=str(bus or "sfx"),
                asset=str(sound_name),
                base_volume=base_volume,
                priority=int(_clamp(priority, -100, 100, 0)),
                ducking={
                    str(key): _clamp(value, 0.0, 1.0, 1.0)
                    for key, value in dict(ducking or {}).items()
                },
                generation=generation,
                envelope=0.0 if fade_in_ms else 1.0,
            )
            self._sources[resolved_handle] = source
            if source.ducking:
                self._duck_requests[resolved_handle] = source.ducking
            self._apply_mix()
        if fade_in_ms:
            self._fade(source, fade_in_ms, fade_in=True)
        self._watch(source)
        return stream_obj

    def play_family(self, family, **kwargs):
        """Play one randomly selected numbered member of an SFX family."""
        asset = self._choose_sound_family_variant(family)
        return self.play(asset, **kwargs) if asset else None

    def _stop_handle(
        self,
        handle: str,
        *,
        fade_ms: int = 0,
        pause=False,
        play_outro=False,
        outro_mode="immediate",
    ) -> None:
        with self._lock:
            source = self._sources.get(str(handle))
        if not source:
            return
        if pause:
            source.paused = True
        else:
            source.stopping = True
            if (
                play_outro
                and source.seamless
                and source.outro
                and bool(getattr(source.stream, "looping", False))
            ):
                transitioned = (
                    self._begin_boundary_outro(source)
                    if outro_mode == "boundary"
                    else self._begin_immediate_outro(source)
                )
                if transitioned:
                    return
        self._fade(
            source,
            fade_ms,
            fade_in=False,
            stop=not pause,
            pause=pause,
            play_outro=play_outro,
        )

    def _begin_immediate_outro(self, source: _AudioSource) -> bool:
        """Splice a preloaded outro now, without a fade or silent gap."""
        outro_asset = source.outro
        outro_stream = self._create_stream(
            outro_asset,
            volume=self._effective_volume(source),
            looping=False,
            start=False,
        )
        if not outro_stream:
            return False
        if not self._start_stream(outro_stream):
            self._stop_stream(outro_stream)
            self.sound_cacher.unpin(outro_stream)
            return False

        old_handle = source.handle
        queued_streams = []
        with self._lock:
            if self._sources.get(old_handle) is not source:
                self._stop_stream(outro_stream)
                self.sound_cacher.unpin(outro_stream)
                return False
            retired_handle = f"outro:{uuid.uuid4().hex}"
            old_stream = source.stream
            target = source.target
            self._sources.pop(old_handle, None)
            duck_request = self._duck_requests.pop(old_handle, None)
            self._next_generation(old_handle)
            source.handle = retired_handle
            source.generation = self._next_generation(retired_handle)
            source.outro = ""
            source.stream = outro_stream
            source.asset = outro_asset
            source.stopping = False
            source.backend_callbacks.clear()
            queued_streams = list(source.queued_streams)
            source.queued_streams.clear()
            self._sources[retired_handle] = source
            if target and self._targets.get(target) == old_handle:
                self._targets[target] = retired_handle
            if duck_request:
                self._duck_requests[retired_handle] = duck_request

        self._stop_stream(old_stream)
        self.sound_cacher.unpin(old_stream)
        for queued in queued_streams:
            self._stop_stream(queued)
            self.sound_cacher.unpin(queued)
        self._watch(source)
        return True

    def _begin_boundary_outro(self, source: _AudioSource) -> bool:
        """Finish the current loop iteration and append its outro at the seam."""
        outro_asset = source.outro
        outro_stream = self._create_stream(
            outro_asset,
            volume=self._effective_volume(source),
            looping=False,
            start=False,
        )
        if not outro_stream:
            return False

        old_handle = source.handle
        with self._lock:
            if self._sources.get(old_handle) is not source:
                self._stop_stream(outro_stream)
                self.sound_cacher.unpin(outro_stream)
                return False
            retired_handle = f"outro:{uuid.uuid4().hex}"
            self._sources.pop(old_handle, None)
            duck_request = self._duck_requests.pop(old_handle, None)
            self._next_generation(old_handle)
            target = source.target
            source.handle = retired_handle
            source.generation = self._next_generation(retired_handle)
            source.outro = ""
            source.queued_streams.append(outro_stream)
            self._sources[retired_handle] = source
            if target and self._targets.get(target) == old_handle:
                self._targets[target] = retired_handle
            if duck_request:
                self._duck_requests[retired_handle] = duck_request

        transitioned = threading.Event()

        def start_outro():
            if transitioned.is_set():
                return
            transitioned.set()
            with self._lock:
                if self._sources.get(retired_handle) is not source:
                    return
                if outro_stream not in source.queued_streams:
                    return
                source.queued_streams.remove(outro_stream)
                old_stream = source.stream
                source.stream = outro_stream
                source.asset = outro_asset
                source.stopping = False
                source.backend_callbacks.clear()
                self._set_stream_volume(outro_stream, self._effective_volume(source))
            self._stop_stream(old_stream)
            self.sound_cacher.unpin(old_stream)
            if not self._start_stream(outro_stream):
                self._release_source(retired_handle, source.generation)
                return
            self._watch(source)

        callback = self._on_stream_end(source.stream, start_outro)
        if callback is not None:
            source.backend_callbacks.append(callback)
        else:
            def wait_for_boundary():
                while (
                    self._stream_is_playing(source.stream)
                    and self._sources.get(retired_handle) is source
                ):
                    time.sleep(0.005)
                start_outro()

            threading.Thread(target=wait_for_boundary, daemon=True).start()

        # Removing the loop flag lets BASS finish the current iteration. The
        # preloaded outro then starts from the native end callback with no
        # fade or asset-load delay between same-stem segments.
        if not self._set_stream_looping(source.stream, False):
            self._release_source(retired_handle, source.generation)
            return False
        return True

    def stop_sound(self, handle: str, fade_ms: int = 0) -> None:
        self._stop_handle(handle, fade_ms=fade_ms)

    # ------------------------------------------------------------------
    # Music and ambience layers
    # ------------------------------------------------------------------

    @staticmethod
    def _target(packet) -> str:
        return (
            f"{packet.get('kind', '')}:{packet.get('scope', 'global')}:"
            f"{packet.get('context', '')}:{packet.get('layer', 'main')}"
        )

    def _play_layer(self, packet):
        kind = packet["kind"]
        asset = packet["asset"]
        handle = str(packet.get("handle") or f"{kind}:{uuid.uuid4().hex}")
        target = self._target(packet)
        fade_in_ms = int(_clamp(packet.get("fade_in_ms", 0), 0, MAX_FADE_MS, 0))
        fade_out_ms = int(_clamp(packet.get("fade_out_ms", 0), 0, MAX_FADE_MS, 0))
        with self._lock:
            layers = [
                source for source in self._sources.values() if source.kind != "sfx"
            ]
            if target not in self._targets and len(layers) >= MAX_ACTIVE_LAYERS:
                victim = min(layers, key=lambda item: (item.priority, item.created_at))
                if victim.priority > int(
                    _clamp(packet.get("priority", 0), -100, 100, 0)
                ):
                    return None
                self._stop_handle(victim.handle, fade_ms=0)
        self._retire_target(target, fade_out_ms)

        generation = self._next_generation(handle)
        base_volume = _clamp(packet.get("volume", 100), 0, 100, 100) / 100
        intro = (
            str(packet.get("intro") or "")
            if packet.get("play_intro", True)
            else ""
        )
        loop_asset = asset
        seamless = bool(packet.get("seamless", True))

        def install(
            asset_name,
            looping,
            *,
            stream_obj=None,
            initial_envelope=None,
            remaining_fade_ms=None,
            outro=None,
            watch=True,
        ):
            if initial_envelope is not None:
                envelope = initial_envelope
            elif fade_in_ms:
                envelope = 0.0
            else:
                envelope = 1.0
            stream_obj = stream_obj or self._create_stream(
                asset_name,
                volume=base_volume * self._master_gain(kind) * envelope,
                looping=looping,
            )
            if not stream_obj:
                return None
            source = _AudioSource(
                handle=handle,
                stream=stream_obj,
                kind=kind,
                bus=str(packet.get("bus") or kind),
                asset=asset_name,
                base_volume=base_volume,
                priority=int(_clamp(packet.get("priority", 0), -100, 100, 0)),
                target=target,
                outro=(
                    str(packet.get("outro") or "")
                    if outro is None
                    else outro
                ),
                generation=generation,
                envelope=envelope,
                seamless=seamless,
                ducking={
                    str(key): _clamp(value, 0, 100, 100) / 100
                    for key, value in dict(packet.get("ducking") or {}).items()
                },
            )
            with self._lock:
                if self._generations.get(handle) != generation:
                    self._stop_stream(stream_obj)
                    self.sound_cacher.unpin(stream_obj)
                    return None
                self._sources[handle] = source
                self._targets[target] = handle
                if source.ducking:
                    self._duck_requests[handle] = source.ducking
                self._apply_mix()
            if stream_obj is not None and not self._stream_is_playing(stream_obj):
                if not self._start_stream(stream_obj):
                    self._release_source(handle, generation)
                    return None
            fade_duration = (
                fade_in_ms if remaining_fade_ms is None else remaining_fade_ms
            )
            if fade_duration and source.envelope < 1.0:
                self._fade(source, fade_duration, fade_in=True)
            if watch:
                self._watch(source)
            return source

        if not intro:
            return install(loop_asset, bool(packet.get("loop", True)))

        loop_enabled = bool(packet.get("loop", True))
        prepared_loop = self._create_stream(
            loop_asset,
            volume=0.0 if fade_in_ms else base_volume * self._master_gain(kind),
            looping=loop_enabled,
            start=False,
        )
        intro_started_at = time.monotonic()
        intro_source = install(intro, False, outro="", watch=False)
        if not intro_source:
            if prepared_loop:
                self._stop_stream(prepared_loop)
                self.sound_cacher.unpin(prepared_loop)
            return install(loop_asset, loop_enabled)
        if prepared_loop:
            intro_source.queued_streams.append(prepared_loop)

        transitioned = threading.Event()

        def continue_after_intro():
            if transitioned.is_set():
                return
            transitioned.set()
            with self._lock:
                if (
                    self._generations.get(handle) != generation
                    or self._sources.get(handle) is not intro_source
                    or intro_source.stopping
                ):
                    return
                intro_source.fade_token += 1
                envelope = intro_source.envelope
                self._sources.pop(handle, None)
                if prepared_loop in intro_source.queued_streams:
                    intro_source.queued_streams.remove(prepared_loop)
                intro_source.backend_callbacks.clear()
                self.sound_cacher.unpin(intro_source.stream)
            elapsed_ms = int((time.monotonic() - intro_started_at) * 1000)
            remaining = max(0, fade_in_ms - elapsed_ms)
            install(
                loop_asset,
                loop_enabled,
                stream_obj=prepared_loop,
                initial_envelope=envelope,
                remaining_fade_ms=remaining,
            )

        callback = self._on_stream_end(intro_source.stream, continue_after_intro)
        if callback is not None:
            intro_source.backend_callbacks.append(callback)
        else:
            def wait_for_intro():
                while (
                    self._stream_is_playing(intro_source.stream)
                    and self._generations.get(handle) == generation
                    and not intro_source.stopping
                ):
                    time.sleep(0.005)
                continue_after_intro()

            threading.Thread(target=wait_for_intro, daemon=True).start()
        return intro_source

    def music(
        self,
        music_name: str,
        looping: bool = True,
        fade_out_old: bool = True,
        *,
        handle: str = "music",
        bus: str = "music",
        scope: str = "global",
        context: str = "",
        layer: str = "main",
        fade_in_ms: int = 800,
        fade_out_ms: int = 800,
    ):
        return self._play_layer(
            {
                "kind": "music",
                "asset": music_name,
                "handle": handle,
                "bus": bus,
                "scope": scope,
                "context": context,
                "layer": layer,
                "loop": looping,
                "fade_in_ms": fade_in_ms if fade_out_old else 0,
                "fade_out_ms": fade_out_ms if fade_out_old else 0,
            }
        )

    def has_managed_audio(
        self,
        kind: str,
        *,
        handle: str,
        asset: str = "",
    ) -> bool:
        """Return whether one matching managed source is still active."""
        with self._lock:
            source = self._sources.get(handle)
            if not source:
                return False
            return source.kind == kind and (not asset or source.asset == asset)

    def pause_music(self, fade_ms=800, handle="music"):
        self._stop_handle(handle, fade_ms=fade_ms, pause=True)

    def resume_music(self, fade_ms=800, handle="music"):
        with self._lock:
            source = self._sources.get(handle)
            if not source or not source.paused:
                return
            try:
                source.stream.play()
            except Exception:
                return
            source.paused = False
            self._set_stream_volume(source.stream, self._effective_volume(source))
        self._fade(source, fade_ms, fade_in=True)

    def stop_music(self, fade=True, fade_ms=800, handle="music"):
        self._stop_handle(handle, fade_ms=fade_ms if fade else 0)

    def ambience(
        self,
        intro_name,
        loop_name,
        outro_name,
        *,
        fade_in_ms=1200,
        fade_out_ms=1200,
        handle="ambience:global:default:environment",
        scope="global",
        context="",
        layer="environment",
        play_intro=True,
        seamless=True,
    ):
        return self._play_layer(
            {
                "kind": "ambience",
                "asset": loop_name,
                "handle": handle,
                "bus": "ambience",
                "scope": scope,
                "context": context,
                "layer": layer,
                "loop": True,
                "intro": intro_name or "",
                "outro": outro_name or "",
                "play_intro": play_intro,
                "seamless": seamless,
                "fade_in_ms": fade_in_ms,
                "fade_out_ms": fade_out_ms,
            }
        )

    def stop_ambience(
        self,
        force=False,
        *,
        fade_ms=1200,
        handle="",
        scope="global",
        context="",
        layer="environment",
        outro_mode="immediate",
    ):
        if handle:
            targets = [handle]
        else:
            target = f"ambience:{scope}:{context}:{layer}"
            targets = [self._targets.get(target, "")]
        for resolved in targets:
            if resolved:
                self._stop_handle(
                    resolved,
                    fade_ms=0 if force else fade_ms,
                    play_outro=not force,
                    outro_mode=outro_mode,
                )

    # ------------------------------------------------------------------
    # Unified protocol router and mix controls
    # ------------------------------------------------------------------

    def handle_audio_command(self, packet):
        """Validate and execute a versioned server audio command."""
        if not isinstance(packet, dict):
            return False
        try:
            version = int(packet.get("version", 0))
        except (TypeError, ValueError, OverflowError):
            return False
        if version != AUDIO_PROTOCOL_VERSION:
            return False
        for field in ("handle", "bus", "context", "layer"):
            if packet.get(field) and not self._valid_id(packet[field]):
                return False
        if packet.get("scope", "global") not in {"global", "player", "context"}:
            return False
        outro_mode = str(packet.get("outro_mode") or "immediate")
        if outro_mode not in {"immediate", "boundary"}:
            return False
        ducking_data = packet.get("ducking", {})
        if ducking_data is None:
            ducking_data = {}
        if not isinstance(ducking_data, dict) or len(ducking_data) > 32:
            return False
        if any(not self._valid_id(bus) for bus in ducking_data):
            return False
        command = packet.get("command")
        kind = packet.get("kind", "")
        if packet.get("family") and command != "play":
            return False
        if packet.get("all_layers") and (
            command != "stop"
            or kind != "ambience"
            or packet.get("handle")
        ):
            return False
        if packet.get("play_outros") and command != "stop_all":
            return False
        if command == "play":
            asset = str(packet.get("asset") or "")
            family = str(packet.get("family") or "")
            if bool(asset) == bool(family):
                return False
            if family:
                if kind != "sfx" or packet.get("loop"):
                    return False
                asset = self._choose_sound_family_variant(family)
            if not self._asset_path(asset) or kind not in {"sfx", "music", "ambience"}:
                return False
            if kind == "sfx":
                ducking = {
                    str(key): _clamp(value, 0, 100, 100) / 100
                    for key, value in dict(packet.get("ducking") or {}).items()
                }
                self.play(
                    asset,
                    volume=_clamp(packet.get("volume", 100), 0, 100, 100) / 100,
                    pan=_clamp(packet.get("pan", 0), -100, 100, 0) / 100,
                    pitch=_clamp(packet.get("pitch", 100), 25, 400, 100) / 100,
                    looping=bool(packet.get("loop", False)),
                    handle=str(packet.get("handle") or ""),
                    bus=str(packet.get("bus") or "sfx"),
                    fade_in_ms=packet.get("fade_in_ms", 0),
                    fade_out_ms=packet.get("fade_out_ms", 0),
                    priority=packet.get("priority", 0),
                    max_instances=packet.get("max_instances", 0),
                    ducking=ducking,
                )
            else:
                self._play_layer(packet)
            return True
        if command in {"stop", "pause", "resume"}:
            if kind not in {"sfx", "music", "ambience"}:
                return False
            if command in {"pause", "resume"} and (
                kind != "music" or not packet.get("handle")
            ):
                return False
            if command == "stop" and kind in {"sfx", "music"} and not packet.get(
                "handle"
            ):
                return False
            if (
                command == "stop"
                and kind == "ambience"
                and packet.get("all_layers", False)
            ):
                with self._lock:
                    handles = [
                        source.handle
                        for source in self._sources.values()
                        if source.kind == "ambience"
                    ]
                for ambience_handle in handles:
                    self._stop_handle(
                        ambience_handle,
                        fade_ms=packet.get("fade_out_ms", 0),
                        play_outro=packet.get("play_outro", True),
                        outro_mode=outro_mode,
                    )
                return True
            handle = str(packet.get("handle") or "")
            if not handle and kind == "ambience":
                handle = self._targets.get(self._target(packet), "")
            if not handle:
                return True
            if command == "resume":
                self.resume_music(packet.get("fade_in_ms", 0), handle)
                return True
            self._stop_handle(
                handle,
                fade_ms=packet.get("fade_out_ms", 0),
                pause=command == "pause",
                play_outro=(
                    command == "stop"
                    and kind == "ambience"
                    and packet.get("play_outro", True)
                ),
                outro_mode=outro_mode,
            )
            return True
        if command == "set_bus":
            bus = str(packet.get("bus") or "")
            if not bus:
                return False
            self._set_bus_gain(
                bus,
                packet.get("volume", 100),
                packet.get("fade_in_ms", 0),
            )
            return True
        if command == "stop_all":
            self.stop_all(
                fade_ms=packet.get("fade_out_ms", 0),
                play_outros=packet.get("play_outros", False),
                outro_mode=outro_mode,
            )
            return True
        return False

    def stop_all(
        self,
        fade_ms=0,
        *,
        play_outros=False,
        outro_mode="immediate",
    ):
        with self._lock:
            handles = list(self._sources)
        for handle in handles:
            with self._lock:
                source = self._sources.get(handle)
            self._stop_handle(
                handle,
                fade_ms=fade_ms,
                play_outro=bool(
                    play_outros and source and source.kind == "ambience"
                ),
                outro_mode=outro_mode,
            )

    def set_music_volume(self, volume):
        self.music_volume = _clamp(volume, 0.0, 1.0, 0.2)
        self._apply_mix()

    def set_sound_volume(self, volume):
        self.sound_volume = _clamp(volume, 0.0, 1.0, 1.0)
        self._apply_mix()

    def set_ambience_volume(self, volume):
        self.ambience_volume = _clamp(volume, 0.0, 1.0, 0.3)
        self._apply_mix()

    def play_menuclick(self):
        self.play(self.menuclick_sound, volume=0.5, priority=100)

    def play_menuenter(self):
        self.play(self.menuenter_sound, volume=0.5, priority=100)
