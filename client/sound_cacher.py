"""Cosmos-backed audio streams for the desktop client.

Cosmos is the CalmComputers audio engine: miniaudio for playback and mixing,
Steam Audio for HRTF. Its source is in ../cosmos and the built wheel in
vendor/. This module presents it to sound_manager.py through the interface
the BASS-based cacher had: ``create``, ``play``, ``pin``, ``unpin``, ``clean``
and stream objects with ``play``, ``stop``, ``pause``, ``is_playing``,
``volume``, ``pan``, ``pitch`` and ``looping``.

It adds one thing: a stream may carry a 3D ``position``, rendered according
to the spatial mode ("off", "stereo" or "headphones"). Positions arrive from
the server already in the listener's frame, so the listener never moves: it
sits at the origin facing +Y, with +X to its right and +Z up.

Cosmos keeps decoded audio cached inside its engine, so there is no byte
cache here. The ``refs`` list only keeps stream objects alive until they
finish, as the old cacher did.
"""

from __future__ import annotations

import logging
import threading

import cosmos
from spatial_audio import normalize_audio_position

SPATIAL_MODES = ("off", "stereo", "headphones")
DEFAULT_SPATIAL_MODE = "headphones"

# One table unit is the distance from the listener to a seat. A seat at this
# radius pans fully in the basic-stereo fallback; distance gain is controlled
# independently by the versioned PlayAural mixer policy.
TABLE_RADIUS = 2.0
# Cosmos adds this fixed amount to the pan of every off-centre sound in
# stereo mode; the pan step supplies the rest over one table radius.
_HARD_CLOSE_PAN = 0.2
_PAN_STEP = (1.0 - _HARD_CLOSE_PAN) / TABLE_RADIUS
# Moving point sources need smooth interpolation between measured HRTF
# directions. Full spatial blend keeps distance attenuation independent from
# binaural coloration and matches the browser HRTF renderers.
HRTF_INTERPOLATION = "bilinear"
HRTF_SPATIAL_BLEND = 1.0

_log = logging.getLogger("playaural")


def normalize_spatial_mode(value) -> str:
    """Return a valid spatial mode, defaulting to headphones."""
    text = str(value or "").strip().lower()
    return text if text in SPATIAL_MODES else DEFAULT_SPATIAL_MODE


def _cosmos_mode(position, spatial_mode: str) -> str:
    """Pick the Cosmos rendering mode for one stream."""
    if position is None or spatial_mode == "off":
        return "direct"
    return "hrtf" if spatial_mode == "headphones" else "basic"


class CosmosStream:
    """One playback of one asset: a thin adapter over ``cosmos.Sound``."""

    __slots__ = ("_sound", "_spatial_mode", "_position", "file_name")

    def __init__(
        self,
        sound,
        file_name: str,
        *,
        pan: float,
        volume: float,
        pitch: float,
        looping: bool,
        position,
        spatial_mode: str,
    ):
        self._sound = sound
        self._spatial_mode = spatial_mode
        self._position = normalize_audio_position(position)
        self.file_name = file_name

        # Everything set before the load is applied by the load itself.
        sound.spatial_mode = _cosmos_mode(self._position, spatial_mode)
        sound.hrtf_interpolation = HRTF_INTERPOLATION
        sound.hrtf_spatial_blend = HRTF_SPATIAL_BLEND
        # PlayAural's versioned mixer owns distance gain. Keep Cosmos neutral
        # so Basic and HRTF render direction without applying different hidden
        # falloff curves. Pitch is likewise explicit protocol data, not a
        # renderer-specific behind-the-listener cue.
        sound.min_gain = 1.0
        sound.max_gain = 1.0
        sound.volume_step = 0.0
        sound.behind_pitch_decrease = 0.0
        sound.pan_step = _PAN_STEP
        sound.pan = float(pan)
        sound.volume = float(volume)
        sound.pitch = float(pitch)
        if self._position is not None:
            sound.set_position(*self._position)
        if not sound.load(file_name):
            raise RuntimeError(f"Cosmos could not load {file_name}")
        sound.looping = bool(looping)

    def play(self) -> None:
        self._sound.play()

    def stop(self) -> None:
        self._sound.stop()

    def pause(self) -> None:
        self._sound.pause()

    @property
    def is_playing(self) -> bool:
        return bool(self._sound.playing)

    @property
    def volume(self) -> float:
        return self._sound.volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._sound.volume = float(value)

    @property
    def pan(self) -> float:
        return self._sound.pan

    @pan.setter
    def pan(self, value: float) -> None:
        self._sound.pan = float(value)

    @property
    def pitch(self) -> float:
        return self._sound.pitch

    @pitch.setter
    def pitch(self, value: float) -> None:
        self._sound.pitch = float(value)

    @property
    def looping(self) -> bool:
        return bool(self._sound.looping)

    @looping.setter
    def looping(self, value: bool) -> None:
        self._sound.looping = bool(value)

    @property
    def position(self):
        """The 3D position as an (x, y, z) tuple, or None for a plain cue."""
        return self._position

    @position.setter
    def position(self, value) -> None:
        if value is None:
            self._position = None
            self._sound.spatial_mode = "direct"
            return
        position = normalize_audio_position(value)
        self._sound.set_position(*position)
        self._sound.spatial_mode = _cosmos_mode(position, self._spatial_mode)
        self._position = position


class SoundCacher:
    """Create Cosmos streams and keep them alive while they play."""

    def __init__(self):
        self.manager = cosmos.SoundManager()
        # Listener at the origin facing +Y; the server sends listener-relative
        # positions, so this never changes.
        self.manager.set_listener(0.0, 0.0, 0.0, 90.0)
        self.hrtf_available = bool(self.manager.hrtf_available)
        self.spatial_mode = DEFAULT_SPATIAL_MODE
        self.refs: list[CosmosStream] = []
        self.pinned: set[int] = set()
        self._lock = threading.Lock()
        if not self.hrtf_available:
            _log.warning(
                "SoundCacher: Steam Audio HRTF unavailable; headphone mode "
                "falls back to stereo panning."
            )

    def create(
        self,
        file_name,
        pan=0.0,
        volume=1.0,
        pitch=1.0,
        looping=False,
        pinned=False,
        position=None,
    ) -> CosmosStream:
        stream = CosmosStream(
            self.manager.create_sound(),
            file_name,
            pan=pan,
            volume=volume,
            pitch=pitch,
            looping=looping,
            position=position,
            spatial_mode=normalize_spatial_mode(self.spatial_mode),
        )
        with self._lock:
            self.refs.append(stream)
            if pinned:
                self.pinned.add(id(stream))
        self.clean()
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
    ) -> CosmosStream:
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

    def clean(self) -> None:
        """Drop unpinned streams that have finished."""
        with self._lock:
            self.refs = [
                stream
                for stream in self.refs
                if id(stream) in self.pinned or stream.is_playing
            ]

    def pin(self, stream) -> None:
        with self._lock:
            self.pinned.add(id(stream))

    def unpin(self, stream) -> None:
        with self._lock:
            self.pinned.discard(id(stream))
        self.clean()
