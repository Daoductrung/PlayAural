"""Validated, client-neutral audio command contract.

Gameplay WebSockets carry control messages only. Audio assets remain local to
clients, and voice media continues to use LiveKit.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Hashable
from dataclasses import dataclass, field
import math
from pathlib import PurePosixPath
import re
from typing import Any, ClassVar
import uuid


AUDIO_PROTOCOL_VERSION = 1
DEFAULT_MUSIC_FADE_MS = 800
DEFAULT_AMBIENCE_FADE_MS = 1200
MAX_FADE_MS = 60_000
MAX_AUDIO_PRIORITY = 100
MAX_AUDIO_INSTANCES = 64
MAX_AUDIO_ASSET_LENGTH = 256
MAX_AUDIO_DUCK_BUSES = 32

AUDIO_KINDS = frozenset({"sfx", "music", "ambience"})
AUDIO_COMMANDS = frozenset(
    {"play", "stop", "pause", "resume", "set_bus", "stop_all"}
)
AUDIO_SCOPES = frozenset({"global", "player", "context"})
AUDIO_OUTRO_MODES = frozenset({"immediate", "boundary"})

_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def _finite_number(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def clamp_float(value: Any, minimum: float, maximum: float, default: float) -> float:
    """Return a finite number constrained to a protocol-safe range."""
    return max(minimum, min(maximum, _finite_number(value, default)))


def clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    """Return an integer constrained to a protocol-safe range."""
    return int(clamp_float(value, minimum, maximum, default))


def normalize_audio_id(value: str, *, field_name: str) -> str:
    """Validate a stable protocol identifier."""
    normalized = str(value or "")
    if not _ID_PATTERN.fullmatch(normalized):
        raise ValueError(f"Invalid audio {field_name}: {value!r}")
    return normalized


def normalize_audio_asset(value: str, *, required: bool = True) -> str:
    """Validate a repository-relative sound asset path.

    This deliberately rejects URLs, drive paths, traversal, query strings, and
    fragments. A compromised server must not turn a client into an arbitrary
    local-file or network fetcher.
    """
    normalized = str(value or "").strip().replace("\\", "/")
    if not normalized:
        if required:
            raise ValueError("Audio asset is required")
        return ""
    if (
        len(normalized) > MAX_AUDIO_ASSET_LENGTH
        or normalized.startswith("/")
        or ":" in normalized
        or "?" in normalized
        or "#" in normalized
    ):
        raise ValueError(f"Invalid audio asset path: {value!r}")
    path = PurePosixPath(normalized)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Invalid audio asset path: {value!r}")
    return path.as_posix()


def new_audio_handle(prefix: str = "audio") -> str:
    """Create an opaque lifecycle handle safe for every client runtime."""
    safe_prefix = normalize_audio_id(prefix, field_name="handle prefix")
    return f"{safe_prefix}:{uuid.uuid4().hex}"


class SameTurnAudioBatcher:
    """Coalesce identical cues queued in one event-loop turn.

    This deliberately has no time window. A callback scheduled after any
    event-loop yield belongs to a new batch, even when only a tiny amount of
    wall-clock time has passed. Synchronous tools and tests without a running
    loop dispatch immediately instead of retaining work indefinitely.
    """

    def __init__(self) -> None:
        self._pending: dict[Hashable, Callable[[], None]] = {}
        self._flush_handle: asyncio.Handle | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def queue(self, key: Hashable, callback: Callable[[], None]) -> bool:
        """Queue one cue, returning whether this batch accepted the key."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            callback()
            return True

        if self._loop is not None and self._loop is not loop:
            self.cancel()
        self._loop = loop

        if key in self._pending:
            return False
        self._pending[key] = callback
        if self._flush_handle is None:
            self._flush_handle = loop.call_soon(self.flush)
        return True

    def cancel(self) -> None:
        """Discard queued cues and release the scheduled callback."""
        if self._flush_handle is not None:
            self._flush_handle.cancel()
        self._flush_handle = None
        self._pending.clear()
        self._loop = None

    def flush(self) -> None:
        """Dispatch the current batch immediately."""
        if self._flush_handle is not None:
            self._flush_handle.cancel()
        pending = self._pending
        self._pending = {}
        self._flush_handle = None
        for callback in pending.values():
            try:
                callback()
            except Exception as error:
                if self._loop is None:
                    raise
                self._loop.call_exception_handler(
                    {
                        "message": "Same-turn audio callback failed",
                        "exception": error,
                        "callback": callback,
                    }
                )


@dataclass
class AudioCommand:
    """One validated operation in the versioned audio control protocol."""

    command: str
    kind: str = ""
    asset: str = ""
    handle: str = ""
    bus: str = ""
    scope: str = "global"
    context: str = ""
    layer: str = "main"
    loop: bool = False
    intro: str = ""
    outro: str = ""
    play_intro: bool = True
    play_outro: bool = True
    play_outros: bool = False
    outro_mode: str = "immediate"
    all_layers: bool = False
    seamless: bool = True
    volume: int = 100
    pan: int = 0
    pitch: int = 100
    fade_in_ms: int = 0
    fade_out_ms: int = 0
    priority: int = 0
    max_instances: int = 0
    ducking: dict[str, int] = field(default_factory=dict)

    VERSION: ClassVar[int] = AUDIO_PROTOCOL_VERSION

    def __post_init__(self) -> None:
        self.command = str(self.command)
        if self.command not in AUDIO_COMMANDS:
            raise ValueError(f"Unknown audio command: {self.command!r}")

        if self.kind:
            self.kind = str(self.kind)
            if self.kind not in AUDIO_KINDS:
                raise ValueError(f"Unknown audio kind: {self.kind!r}")
        if self.command == "play" and not self.kind:
            raise ValueError("Play commands require an audio kind")

        if self.asset:
            self.asset = normalize_audio_asset(self.asset)
        if self.command == "play" and not self.asset:
            raise ValueError("Play commands require an audio asset")
        self.intro = normalize_audio_asset(self.intro, required=False)
        self.outro = normalize_audio_asset(self.outro, required=False)

        if self.handle:
            self.handle = normalize_audio_id(self.handle, field_name="handle")
        if self.bus:
            self.bus = normalize_audio_id(self.bus, field_name="bus")
        elif self.kind:
            self.bus = self.kind
        if self.context:
            self.context = normalize_audio_id(self.context, field_name="context")
        self.layer = normalize_audio_id(self.layer or "main", field_name="layer")

        self.scope = str(self.scope or "global")
        if self.scope not in AUDIO_SCOPES:
            raise ValueError(f"Unknown audio scope: {self.scope!r}")
        if self.scope in {"player", "context"} and not self.context:
            raise ValueError(f"{self.scope.title()}-scoped audio requires a context id")

        self.volume = clamp_int(self.volume, 0, 100, 100)
        self.pan = clamp_int(self.pan, -100, 100, 0)
        self.pitch = clamp_int(self.pitch, 25, 400, 100)
        self.fade_in_ms = clamp_int(self.fade_in_ms, 0, MAX_FADE_MS, 0)
        self.fade_out_ms = clamp_int(self.fade_out_ms, 0, MAX_FADE_MS, 0)
        self.priority = clamp_int(
            self.priority, -MAX_AUDIO_PRIORITY, MAX_AUDIO_PRIORITY, 0
        )
        self.max_instances = clamp_int(
            self.max_instances, 0, MAX_AUDIO_INSTANCES, 0
        )
        if len(dict(self.ducking or {})) > MAX_AUDIO_DUCK_BUSES:
            raise ValueError("Too many audio ducking buses")
        self.ducking = {
            normalize_audio_id(bus, field_name="ducking bus"): clamp_int(
                gain, 0, 100, 100
            )
            for bus, gain in dict(self.ducking or {}).items()
        }
        self.loop = bool(self.loop)
        self.play_intro = bool(self.play_intro)
        self.play_outro = bool(self.play_outro)
        self.play_outros = bool(self.play_outros)
        self.outro_mode = str(self.outro_mode or "immediate")
        if self.outro_mode not in AUDIO_OUTRO_MODES:
            raise ValueError(f"Unknown audio outro mode: {self.outro_mode!r}")
        self.all_layers = bool(self.all_layers)
        self.seamless = bool(self.seamless)

        if self.command in {"pause", "resume"} and (
            self.kind != "music" or not self.handle
        ):
            raise ValueError(f"{self.command.title()} requires a music handle")
        if self.command == "set_bus" and not self.bus:
            raise ValueError("Set-bus commands require a bus")
        if self.command == "stop":
            if not self.kind:
                raise ValueError("Stop commands require an audio kind")
            if self.kind in {"sfx", "music"} and not self.handle:
                raise ValueError(f"Stopping {self.kind} requires a handle")
        if self.all_layers and (
            self.command != "stop" or self.kind != "ambience" or self.handle
        ):
            raise ValueError(
                "All-layer stops require an ambience stop without a handle"
            )
        if self.play_outros and self.command != "stop_all":
            raise ValueError("Multi-outro playback is only valid for stop-all")
        if self.command == "play" and (
            self.kind in {"music", "ambience"} or (self.kind == "sfx" and self.loop)
        ) and not self.handle:
            raise ValueError("Managed or looping audio requires a handle")

    @property
    def target(self) -> str:
        """Stable channel key used for music and ambience replacement."""
        return f"{self.scope}:{self.context}:{self.layer}"

    def to_packet(self) -> dict[str, Any]:
        """Serialize without meaningless optional fields."""
        packet: dict[str, Any] = {
            "type": "audio",
            "version": self.VERSION,
            "command": self.command,
        }
        optional: dict[str, Any] = {
            "kind": self.kind,
            "asset": self.asset,
            "handle": self.handle,
            "bus": self.bus,
            "scope": self.scope,
            "context": self.context,
            "layer": self.layer,
            "loop": self.loop,
            "intro": self.intro,
            "outro": self.outro,
            "play_intro": self.play_intro,
            "play_outro": self.play_outro,
            "play_outros": self.play_outros,
            "outro_mode": self.outro_mode,
            "all_layers": self.all_layers,
            "seamless": self.seamless,
            "volume": self.volume,
            "pan": self.pan,
            "pitch": self.pitch,
            "fade_in_ms": self.fade_in_ms,
            "fade_out_ms": self.fade_out_ms,
            "priority": self.priority,
            "max_instances": self.max_instances,
            "ducking": self.ducking,
        }
        defaults: dict[str, Any] = {
            "scope": "global",
            "layer": "main",
            "loop": False,
            "play_intro": True,
            "play_outro": True,
            "play_outros": False,
            "outro_mode": "immediate",
            "all_layers": False,
            "seamless": True,
            "volume": 100,
            "pan": 0,
            "pitch": 100,
            "fade_in_ms": 0,
            "fade_out_ms": 0,
            "priority": 0,
            "max_instances": 0,
        }
        for key, value in optional.items():
            if value in ("", {}, None):
                continue
            if key in defaults and value == defaults[key]:
                continue
            packet[key] = value
        # Looping is command data, not an optional truthy feature. In
        # particular, non-looping music must arrive as ``loop: false`` rather
        # than falling into the clients' managed-layer default of ``true``.
        if self.command == "play":
            packet["loop"] = self.loop
        return packet


@dataclass
class AudioPlaybackState:
    """Persistence-safe description of an audio layer restored on reconnect."""

    kind: str
    asset: str
    handle: str
    bus: str
    scope: str = "global"
    context: str = ""
    layer: str = "main"
    loop: bool = True
    intro: str = ""
    outro: str = ""
    play_intro: bool = True
    play_outro: bool = True
    seamless: bool = True
    volume: int = 100
    pan: int = 0
    pitch: int = 100
    fade_in_ms: int = 0
    fade_out_ms: int = 0
    priority: int = 0
    max_instances: int = 0
    ducking: dict[str, int] = field(default_factory=dict)
    recipient_ids: list[str] = field(default_factory=list)
    paused: bool = False

    @classmethod
    def from_command(
        cls, command: AudioCommand, recipient_ids: list[str] | None = None
    ) -> "AudioPlaybackState":
        """Capture the replayable fields of a play command."""
        if command.command != "play":
            raise ValueError("Only play commands can become playback state")
        return cls(
            kind=command.kind,
            asset=command.asset,
            handle=command.handle,
            bus=command.bus,
            scope=command.scope,
            context=command.context,
            layer=command.layer,
            loop=command.loop,
            intro=command.intro,
            outro=command.outro,
            play_intro=command.play_intro,
            play_outro=command.play_outro,
            seamless=command.seamless,
            volume=command.volume,
            pan=command.pan,
            pitch=command.pitch,
            fade_in_ms=command.fade_in_ms,
            fade_out_ms=command.fade_out_ms,
            priority=command.priority,
            max_instances=command.max_instances,
            ducking=dict(command.ducking),
            recipient_ids=list(recipient_ids or []),
        )

    def to_command(self, *, replay: bool = False) -> AudioCommand:
        """Build an idempotent play command.

        A reconnect/save replay joins an already-running soundscape at its
        steady-state loop. It must not replay a cinematic intro that the rest
        of the table heard earlier.
        """
        return AudioCommand(
            command="play",
            kind=self.kind,
            asset=self.asset,
            handle=self.handle,
            bus=self.bus,
            scope=self.scope,
            context=self.context,
            layer=self.layer,
            loop=self.loop,
            intro=self.intro,
            outro=self.outro,
            play_intro=self.play_intro and not replay,
            play_outro=self.play_outro,
            seamless=self.seamless,
            volume=self.volume,
            pan=self.pan,
            pitch=self.pitch,
            fade_in_ms=0 if replay else self.fade_in_ms,
            fade_out_ms=self.fade_out_ms,
            priority=self.priority,
            max_instances=self.max_instances,
            ducking=dict(self.ducking),
        )
