"""Validated, client-neutral audio command contract.

Gameplay WebSockets carry control messages only. Audio assets remain local to
clients, and voice media continues to use LiveKit.
"""

from __future__ import annotations

import asyncio
import math
import re
import uuid
from collections.abc import Callable, Hashable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, ClassVar

AUDIO_PROTOCOL_VERSION = 3
# Positions are in the listener's frame: the listener sits at the origin
# facing +Y, +X is to their right and +Z is up. One unit is a table radius,
# so a seat at the table edge is TABLE_RADIUS away.
MAX_AUDIO_POSITION = 1000.0
ATTENUATION_PRECISION = 6
MAX_AUDIO_DISTANCE = (
    math.ceil(math.sqrt(3.0) * MAX_AUDIO_POSITION * 10**ATTENUATION_PRECISION)
    / 10**ATTENUATION_PRECISION
)
TABLE_RADIUS = 2.0
DEFAULT_MUSIC_FADE_MS = 800
DEFAULT_AMBIENCE_FADE_MS = 1200
MAX_FADE_MS = 60_000
MAX_AUDIO_PRIORITY = 100
MAX_AUDIO_INSTANCES = 64
MAX_AUDIO_ASSET_LENGTH = 256
MAX_AUDIO_DUCK_BUSES = 32
MAX_AUDIO_SEQUENCE_SEGMENTS = 32
MAX_AUDIO_ROLLOFF = 16.0
MAX_AUDIO_AUTOMATION_MS = 3_600_000

AUDIO_KINDS = frozenset({"sfx", "music", "ambience"})
AUDIO_COMMANDS = frozenset(
    {"play", "update", "stop", "pause", "resume", "set_bus", "stop_all"}
)
AUDIO_SCOPES = frozenset({"global", "player", "context"})
AUDIO_OUTRO_MODES = frozenset({"immediate", "boundary"})
AUDIO_OUTPUT_BUFFERS = frozenset({"chat", "private", "game", "system", "misc"})
AUDIO_ATTENUATION_MODELS = frozenset({"none", "linear", "inverse", "exponential"})
AUDIO_AUTOMATION_EASINGS = frozenset(
    {"linear", "ease-in", "ease-out", "ease-in-out"}
)

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


def normalize_audio_family(value: str, *, required: bool = True) -> str:
    """Validate an extensionless, repository-relative numbered sound family."""
    normalized = str(value or "").strip().replace("\\", "/")
    if not normalized:
        if required:
            raise ValueError("Audio family is required")
        return ""
    if "." in normalized.rsplit("/", 1)[-1]:
        raise ValueError(f"Audio family must not include an extension: {value!r}")
    validated = normalize_audio_asset(f"{normalized}1.ogg")
    return validated.removesuffix("1.ogg")


Position = tuple[float, float, float]


@dataclass(frozen=True)
class DistanceAttenuation:
    """Deterministic, client-neutral distance-gain configuration.

    ``none`` is the explicit no-falloff mode and has no numeric parameters.
    Every active model carries all of its parameters in the packet so a client
    never substitutes backend-specific defaults.
    """

    model: str = "none"
    reference_distance: float | None = None
    max_distance: float | None = None
    rolloff_factor: float | None = None
    min_gain: float | None = None
    max_gain: float | None = None

    def __post_init__(self) -> None:
        model = str(self.model)
        if model not in AUDIO_ATTENUATION_MODELS:
            raise ValueError(f"Unknown audio attenuation model: {self.model!r}")
        object.__setattr__(self, "model", model)

        values = (
            self.reference_distance,
            self.max_distance,
            self.rolloff_factor,
            self.min_gain,
            self.max_gain,
        )
        if model == "none":
            if any(value is not None for value in values):
                raise ValueError("No-falloff attenuation cannot include curve parameters")
            return
        if any(
            value is None
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            for value in values
        ):
            raise ValueError("Active attenuation requires finite numeric parameters")

        # Round before validating: the rounded values are what clients receive
        # and divide by, so they are the ones that must satisfy the contract.
        reference_distance = round(float(self.reference_distance), ATTENUATION_PRECISION)
        max_distance = round(float(self.max_distance), ATTENUATION_PRECISION)
        rolloff_factor = round(float(self.rolloff_factor), ATTENUATION_PRECISION)
        min_gain = round(float(self.min_gain), ATTENUATION_PRECISION)
        max_gain = round(float(self.max_gain), ATTENUATION_PRECISION)
        if not 0.0 < reference_distance < max_distance <= MAX_AUDIO_DISTANCE:
            raise ValueError(
                "Attenuation distances must satisfy "
                "0 < reference_distance < max_distance <= MAX_AUDIO_DISTANCE"
            )
        maximum_rolloff = 1.0 if model == "linear" else MAX_AUDIO_ROLLOFF
        if not 0.0 < rolloff_factor <= maximum_rolloff:
            raise ValueError(
                f"Invalid {model} attenuation rolloff factor: {rolloff_factor!r}"
            )
        if not 0.0 <= min_gain <= max_gain <= 1.0:
            raise ValueError("Attenuation gains must satisfy 0 <= min_gain <= max_gain <= 1")

        for name, value in (
            ("reference_distance", reference_distance),
            ("max_distance", max_distance),
            ("rolloff_factor", rolloff_factor),
            ("min_gain", min_gain),
            ("max_gain", max_gain),
        ):
            object.__setattr__(self, name, value)

    def to_packet(self) -> dict[str, Any]:
        """Serialize the complete selected model without implicit defaults."""
        if self.model == "none":
            return {"model": "none"}
        return {
            "model": self.model,
            "reference_distance": self.reference_distance,
            "max_distance": self.max_distance,
            "rolloff_factor": self.rolloff_factor,
            "min_gain": self.min_gain,
            "max_gain": self.max_gain,
        }


def normalize_distance_attenuation(value: Any) -> DistanceAttenuation | None:
    """Validate an optional attenuation object and reject partial schemas."""
    if value is None:
        return None
    if isinstance(value, DistanceAttenuation):
        return value
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid audio attenuation: {value!r}")
    fields = dict(value)
    model = fields.get("model")
    expected = (
        {"model"}
        if model == "none"
        else {
            "model",
            "reference_distance",
            "max_distance",
            "rolloff_factor",
            "min_gain",
            "max_gain",
        }
    )
    if set(fields) != expected:
        raise ValueError(
            f"Invalid audio attenuation fields: {sorted(map(str, fields))!r}"
        )
    return DistanceAttenuation(**fields)


def distance_attenuation_gain(
    position: Position | Sequence[float] | None,
    attenuation: DistanceAttenuation | Mapping[str, Any] | None,
) -> float:
    """Calculate the canonical linear gain for one listener-relative point."""
    normalized = normalize_distance_attenuation(attenuation)
    if normalized is None or normalized.model == "none":
        return 1.0
    normalized_position = normalize_audio_position(position)
    if normalized_position is None:
        raise ValueError("Audio attenuation requires a spatial position")
    distance = math.sqrt(
        sum(coordinate * coordinate for coordinate in normalized_position)
    )
    clamped_distance = min(
        max(distance, normalized.reference_distance), normalized.max_distance
    )
    if normalized.model == "linear":
        gain = 1.0 - normalized.rolloff_factor * (
            (clamped_distance - normalized.reference_distance)
            / (normalized.max_distance - normalized.reference_distance)
        )
    elif normalized.model == "inverse":
        gain = normalized.reference_distance / (
            normalized.reference_distance
            + normalized.rolloff_factor
            * (clamped_distance - normalized.reference_distance)
        )
    else:
        gain = (
            clamped_distance / normalized.reference_distance
        ) ** -normalized.rolloff_factor
    return max(normalized.min_gain, min(normalized.max_gain, gain))


def normalize_audio_position(value: Any) -> Position | None:
    """Validate an optional (x, y, z) position in the listener's frame."""
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"Invalid audio position: {value!r}")
    items = list(value)
    if len(items) != 3:
        raise ValueError(f"Audio position needs three coordinates: {value!r}")
    coords: list[float] = []
    for item in items:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"Invalid audio position: {value!r}")
        parsed = float(item)
        if not math.isfinite(parsed) or abs(parsed) > MAX_AUDIO_POSITION:
            raise ValueError(f"Invalid audio position: {value!r}")
        coords.append(round(parsed, 3))
    return (coords[0], coords[1], coords[2])


def audio_motion_progress(progress: float, easing: str) -> float:
    """Evaluate one of the protocol's deterministic quadratic easing curves."""
    bounded = max(0.0, min(1.0, float(progress)))
    if easing == "linear":
        return bounded
    if easing == "ease-in":
        return bounded * bounded
    if easing == "ease-out":
        return 1.0 - (1.0 - bounded) ** 2
    if easing == "ease-in-out":
        return (
            2.0 * bounded * bounded
            if bounded < 0.5
            else 1.0 - ((-2.0 * bounded + 2.0) ** 2) / 2.0
        )
    raise ValueError(f"Unknown audio motion easing: {easing!r}")


@dataclass(frozen=True)
class AudioMotion:
    """A complete, resumable position automation for one managed source."""

    origin_position: Position
    destination_position: Position
    duration_ms: int
    elapsed_ms: int = 0
    easing: str = "linear"

    def __post_init__(self) -> None:
        origin = normalize_audio_position(self.origin_position)
        destination = normalize_audio_position(self.destination_position)
        if origin is None or destination is None:
            raise ValueError("Audio motion requires origin and destination positions")
        if (
            isinstance(self.duration_ms, bool)
            or not isinstance(self.duration_ms, int)
            or not 0 < self.duration_ms <= MAX_AUDIO_AUTOMATION_MS
        ):
            raise ValueError(f"Invalid audio motion duration: {self.duration_ms!r}")
        if (
            isinstance(self.elapsed_ms, bool)
            or not isinstance(self.elapsed_ms, int)
            or not 0 <= self.elapsed_ms <= self.duration_ms
        ):
            raise ValueError(f"Invalid audio motion elapsed time: {self.elapsed_ms!r}")
        easing = str(self.easing)
        if easing not in AUDIO_AUTOMATION_EASINGS:
            raise ValueError(f"Unknown audio motion easing: {self.easing!r}")
        object.__setattr__(self, "origin_position", origin)
        object.__setattr__(self, "destination_position", destination)
        object.__setattr__(self, "easing", easing)

    @property
    def complete(self) -> bool:
        return self.elapsed_ms >= self.duration_ms

    def position_at(self, elapsed_ms: int | None = None) -> Position:
        """Return the point on the authored trajectory at one elapsed time."""
        elapsed = self.elapsed_ms if elapsed_ms is None else elapsed_ms
        ratio = audio_motion_progress(elapsed / self.duration_ms, self.easing)
        if ratio >= 1.0:
            return self.destination_position
        # Floating-point interpolation can overshoot an endpoint by one ulp,
        # which at the coordinate limit would fail validation. A point on the
        # segment is always between its endpoints, so clamp it there.
        return normalize_audio_position(
            tuple(
                min(
                    max(origin + ((destination - origin) * ratio), min(origin, destination)),
                    max(origin, destination),
                )
                for origin, destination in zip(
                    self.origin_position,
                    self.destination_position,
                    strict=True,
                )
            )
        )

    def advance(self, elapsed_ms: int) -> AudioMotion:
        """Advance by a non-negative amount without passing the destination."""
        if isinstance(elapsed_ms, bool) or not isinstance(elapsed_ms, int) or elapsed_ms < 0:
            raise ValueError(f"Invalid audio motion advance: {elapsed_ms!r}")
        return AudioMotion(
            origin_position=self.origin_position,
            destination_position=self.destination_position,
            duration_ms=self.duration_ms,
            elapsed_ms=min(self.duration_ms, self.elapsed_ms + elapsed_ms),
            easing=self.easing,
        )

    def to_packet(self) -> dict[str, Any]:
        return {
            "origin_position": list(self.origin_position),
            "destination_position": list(self.destination_position),
            "duration_ms": self.duration_ms,
            "elapsed_ms": self.elapsed_ms,
            "easing": self.easing,
        }


def normalize_audio_motion(value: Any) -> AudioMotion | None:
    """Validate the exact source-motion schema without client-side defaults."""
    if value is None:
        return None
    if isinstance(value, AudioMotion):
        return value
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid audio motion: {value!r}")
    fields = dict(value)
    expected = {
        "origin_position",
        "destination_position",
        "duration_ms",
        "elapsed_ms",
        "easing",
    }
    if set(fields) != expected:
        raise ValueError(f"Invalid audio motion fields: {sorted(map(str, fields))!r}")
    return AudioMotion(**fields)


def audio_motion_position(
    motion: AudioMotion | Mapping[str, Any],
    elapsed_ms: int | None = None,
) -> Position:
    """Interpolate one validated source trajectory at an absolute time."""
    normalized = normalize_audio_motion(motion)
    if normalized is None:
        raise ValueError("Audio motion is required")
    return normalized.position_at(elapsed_ms)


def normalize_audio_gain(value: Any) -> float:
    """Validate a finite per-source mix gain in the closed unit interval."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid audio source gain: {value!r}")
    gain = float(value)
    if not math.isfinite(gain) or not 0.0 <= gain <= 1.0:
        raise ValueError(f"Invalid audio source gain: {value!r}")
    return gain


@dataclass(frozen=True)
class AudioGainAutomation:
    """A complete, resumable gain automation for one managed source."""

    origin_gain: float
    destination_gain: float
    duration_ms: int
    elapsed_ms: int = 0
    easing: str = "linear"

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_gain", normalize_audio_gain(self.origin_gain))
        object.__setattr__(
            self,
            "destination_gain",
            normalize_audio_gain(self.destination_gain),
        )
        if (
            isinstance(self.duration_ms, bool)
            or not isinstance(self.duration_ms, int)
            or not 0 < self.duration_ms <= MAX_AUDIO_AUTOMATION_MS
        ):
            raise ValueError(f"Invalid audio gain duration: {self.duration_ms!r}")
        if (
            isinstance(self.elapsed_ms, bool)
            or not isinstance(self.elapsed_ms, int)
            or not 0 <= self.elapsed_ms <= self.duration_ms
        ):
            raise ValueError(f"Invalid audio gain elapsed time: {self.elapsed_ms!r}")
        easing = str(self.easing)
        if easing not in AUDIO_AUTOMATION_EASINGS:
            raise ValueError(f"Unknown audio gain easing: {self.easing!r}")
        object.__setattr__(self, "easing", easing)

    @property
    def complete(self) -> bool:
        return self.elapsed_ms >= self.duration_ms

    def gain_at(self, elapsed_ms: int | None = None) -> float:
        elapsed = self.elapsed_ms if elapsed_ms is None else elapsed_ms
        ratio = audio_motion_progress(elapsed / self.duration_ms, self.easing)
        if ratio >= 1.0:
            return self.destination_gain
        gain = self.origin_gain + ((self.destination_gain - self.origin_gain) * ratio)
        return min(
            max(gain, min(self.origin_gain, self.destination_gain)),
            max(self.origin_gain, self.destination_gain),
        )

    def advance(self, elapsed_ms: int) -> AudioGainAutomation:
        if (
            isinstance(elapsed_ms, bool)
            or not isinstance(elapsed_ms, int)
            or elapsed_ms < 0
        ):
            raise ValueError(f"Invalid audio gain advance: {elapsed_ms!r}")
        return AudioGainAutomation(
            origin_gain=self.origin_gain,
            destination_gain=self.destination_gain,
            duration_ms=self.duration_ms,
            elapsed_ms=min(self.duration_ms, self.elapsed_ms + elapsed_ms),
            easing=self.easing,
        )

    def to_packet(self) -> dict[str, Any]:
        return {
            "origin_gain": self.origin_gain,
            "destination_gain": self.destination_gain,
            "duration_ms": self.duration_ms,
            "elapsed_ms": self.elapsed_ms,
            "easing": self.easing,
        }


def normalize_audio_gain_automation(value: Any) -> AudioGainAutomation | None:
    """Validate the exact source-gain automation schema."""
    if value is None:
        return None
    if isinstance(value, AudioGainAutomation):
        return value
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid audio gain automation: {value!r}")
    fields = dict(value)
    expected = {
        "origin_gain",
        "destination_gain",
        "duration_ms",
        "elapsed_ms",
        "easing",
    }
    if set(fields) != expected:
        raise ValueError(
            f"Invalid audio gain automation fields: {sorted(map(str, fields))!r}"
        )
    return AudioGainAutomation(**fields)


@dataclass(frozen=True)
class AudioSequenceSegment:
    """One sample-scheduled asset in a finite client-clocked SFX sequence.

    A destination, when present, moves the source over the decoded duration of
    this segment. ``next_start_ratio`` controls when the following segment
    starts as a fraction of this segment's decoded duration, allowing authored
    tails to overlap without changing pitch. The duration deliberately is not
    repeated in protocol data, so replacements cannot leave stale timing
    constants behind.
    """

    asset: str
    position: Position | None = None
    destination_position: Position | None = None
    attenuation: DistanceAttenuation | Mapping[str, Any] | None = None
    gain: float = 1.0
    easing: str = "linear"
    next_start_ratio: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "asset", normalize_audio_asset(self.asset))
        position = normalize_audio_position(self.position)
        destination = normalize_audio_position(self.destination_position)
        attenuation = normalize_distance_attenuation(self.attenuation)
        gain = normalize_audio_gain(self.gain)
        next_start_ratio = normalize_audio_gain(self.next_start_ratio)
        easing = str(self.easing)
        if attenuation is not None and position is None:
            raise ValueError("Sequence attenuation requires a spatial position")
        if destination is not None and position is None:
            raise ValueError("Sequence motion requires an origin position")
        if easing not in AUDIO_AUTOMATION_EASINGS:
            raise ValueError(f"Unknown audio sequence easing: {self.easing!r}")
        if destination is None and easing != "linear":
            raise ValueError("Static audio sequence segments require linear easing")
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "destination_position", destination)
        object.__setattr__(self, "attenuation", attenuation)
        object.__setattr__(self, "gain", gain)
        object.__setattr__(self, "easing", easing)
        object.__setattr__(self, "next_start_ratio", next_start_ratio)

    def to_packet(self) -> dict[str, Any]:
        """Serialize a complete segment without renderer-specific defaults."""
        return {
            "asset": self.asset,
            "position": list(self.position) if self.position is not None else None,
            "destination_position": (
                list(self.destination_position)
                if self.destination_position is not None
                else None
            ),
            "attenuation": (
                self.attenuation.to_packet()
                if isinstance(self.attenuation, DistanceAttenuation)
                else None
            ),
            "gain": self.gain,
            "easing": self.easing,
            "next_start_ratio": self.next_start_ratio,
        }


def normalize_audio_sequence_segments(
    value: Any,
) -> tuple[AudioSequenceSegment, ...]:
    """Validate an optional, bounded, all-or-nothing SFX sequence."""
    if value is None or value == () or value == []:
        return ()
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ValueError("Audio sequence segments must be a sequence")
    if not 0 < len(value) <= MAX_AUDIO_SEQUENCE_SEGMENTS:
        raise ValueError(
            "Audio sequences require between 1 and "
            f"{MAX_AUDIO_SEQUENCE_SEGMENTS} segments"
        )
    expected = {
        "asset",
        "position",
        "destination_position",
        "attenuation",
        "gain",
        "easing",
        "next_start_ratio",
    }
    normalized: list[AudioSequenceSegment] = []
    for item in value:
        if isinstance(item, AudioSequenceSegment):
            normalized.append(item)
            continue
        if not isinstance(item, Mapping):
            raise ValueError(f"Invalid audio sequence segment: {item!r}")
        fields = dict(item)
        if set(fields) != expected:
            raise ValueError(
                "Invalid audio sequence segment fields: "
                f"{sorted(map(str, fields))!r}"
            )
        normalized.append(AudioSequenceSegment(**fields))
    return tuple(normalized)


def pan_from_position(position: Position) -> int:
    """Stereo pan for clients without spatial audio: the sine of the azimuth.

    Straight ahead and straight behind are centred; a source level with the
    listener's ears is hard left or right.
    """
    x, y, _ = position
    horizontal = math.hypot(x, y)
    if horizontal < 1e-6:
        return 0
    return clamp_int(round(100.0 * x / horizontal), -100, 100, 0)


def direction_position(
    degrees_clockwise: float, radius: float = TABLE_RADIUS, height: float = 0.0
) -> Position:
    """A point `radius` away in the horizontal plane.

    Angles are clockwise from straight ahead: 0 is ahead, 90 is right, 180 is
    behind, 270 is left.
    """
    phi = math.radians(degrees_clockwise)
    return (
        round(radius * math.sin(phi), 3),
        round(radius * math.cos(phi), 3),
        round(height, 3),
    )


def clock_position(hour: int, radius: float = TABLE_RADIUS) -> Position:
    """A point at a clock-face hour: 12 is ahead, 3 is right, 6 is behind."""
    return direction_position(30.0 * (int(hour) % 12), radius)


def seat_position(
    seat_index: int,
    listener_index: int | None,
    seat_count: int,
    radius: float = TABLE_RADIUS,
) -> Position | None:
    """Where one seat sits, as heard from another.

    Seats are numbered clockwise around the table. The listener's own seat
    has no position (None): their own sounds play unpositioned. The seat
    after the listener is to their left, the seat opposite is straight ahead
    and the seat before them is to their right.

    A listener with no seat (a spectator) hears seat 0 straight ahead and the
    rest spread clockwise from there.

        k = (seat_index - listener_index) mod seat_count
        angle = 180 + 360 * k / seat_count      (clockwise from ahead)
        position = (radius * sin(angle), radius * cos(angle), 0)
    """
    if seat_count < 2:
        return None
    if listener_index is None:
        return direction_position(360.0 * (seat_index % seat_count) / seat_count, radius)
    if seat_index == listener_index:
        return None
    step = (seat_index - listener_index) % seat_count
    return direction_position(180.0 + 360.0 * step / seat_count, radius)


def new_audio_handle(prefix: str = "audio") -> str:
    """Create an opaque lifecycle handle safe for every client runtime."""
    safe_prefix = normalize_audio_id(prefix, field_name="handle prefix")
    return f"{safe_prefix}:{uuid.uuid4().hex}"


class SameTurnAudioBatcher:
    """Coalesce and prioritize cues queued in one event-loop turn.

    This deliberately has no time window. A callback scheduled after any
    event-loop yield belongs to a new batch, even when only a tiny amount of
    wall-clock time has passed. Synchronous tools and tests without a running
    loop dispatch immediately instead of retaining work indefinitely. Callers
    may assign related cues to a group; only the highest-priority cues in that
    group survive the turn, while distinct cues at the same priority remain.
    """

    def __init__(self) -> None:
        self._pending: dict[
            Hashable,
            tuple[Hashable | None, int, Callable[[], None]],
        ] = {}
        self._group_priorities: dict[Hashable, int] = {}
        self._flush_handle: asyncio.Handle | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def queue(
        self,
        key: Hashable,
        callback: Callable[[], None],
        *,
        group: Hashable | None = None,
        priority: int = 0,
    ) -> bool:
        """Queue one cue, returning whether this batch accepted it."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            callback()
            return True

        if self._loop is not None and self._loop is not loop:
            self.cancel()
        self._loop = loop

        existing = self._pending.get(key)
        if existing is not None and priority <= existing[1]:
            return False
        if existing is not None:
            self._pending.pop(key, None)
            existing_group = existing[0]
            if existing_group is not None and not any(
                entry[0] == existing_group for entry in self._pending.values()
            ):
                self._group_priorities.pop(existing_group, None)

        if group is not None:
            current_priority = self._group_priorities.get(group)
            if current_priority is not None and priority < current_priority:
                return False
            if current_priority is not None and priority > current_priority:
                self._pending = {
                    pending_key: entry
                    for pending_key, entry in self._pending.items()
                    if entry[0] != group
                }
            self._group_priorities[group] = priority

        self._pending[key] = (group, priority, callback)
        if self._flush_handle is None:
            self._flush_handle = loop.call_soon(self.flush)
        return True

    def cancel(self) -> None:
        """Discard queued cues and release the scheduled callback."""
        if self._flush_handle is not None:
            self._flush_handle.cancel()
        self._flush_handle = None
        self._pending.clear()
        self._group_priorities.clear()
        self._loop = None

    def flush(self) -> None:
        """Dispatch the current batch immediately."""
        if self._flush_handle is not None:
            self._flush_handle.cancel()
        pending = self._pending
        self._pending = {}
        self._group_priorities = {}
        self._flush_handle = None
        for _, _, callback in pending.values():
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
    family: str = ""
    handle: str = ""
    bus: str = ""
    buffer: str = ""
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
    pan: int | None = None
    pitch: int = 100
    fade_in_ms: int = 0
    fade_out_ms: int = 0
    priority: int = 0
    max_instances: int = 0
    ducking: dict[str, int] = field(default_factory=dict)
    # Optional (x, y, z) in the listener's frame. Spatial clients render it;
    # the others use the pan derived from it when no pan was given.
    position: Position | None = None
    attenuation: DistanceAttenuation | Mapping[str, Any] | None = None
    motion: AudioMotion | Mapping[str, Any] | None = None
    gain: float = 1.0
    gain_automation: AudioGainAutomation | Mapping[str, Any] | None = None
    segments: Sequence[AudioSequenceSegment | Mapping[str, Any]] = field(
        default_factory=tuple
    )

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
        if self.family:
            self.family = normalize_audio_family(self.family)
        self.segments = normalize_audio_sequence_segments(self.segments)
        play_sources = sum(
            bool(value) for value in (self.asset, self.family, self.segments)
        )
        if play_sources > 1:
            raise ValueError(
                "Play commands cannot combine an asset, family, and sequence"
            )
        if self.command == "play" and play_sources != 1:
            raise ValueError("Play commands require one asset, family, or sequence")
        if self.segments and (
            self.command != "play"
            or self.kind != "sfx"
            or self.loop
            or self.intro
            or self.outro
        ):
            raise ValueError(
                "Audio sequences are only valid for finite SFX without stems"
            )
        self.intro = normalize_audio_asset(self.intro, required=False)
        self.outro = normalize_audio_asset(self.outro, required=False)

        if self.handle:
            self.handle = normalize_audio_id(self.handle, field_name="handle")
        if self.segments and not self.handle:
            raise ValueError("Audio sequences require a stable handle")
        if self.bus:
            self.bus = normalize_audio_id(self.bus, field_name="bus")
        elif self.command == "play" and self.kind:
            self.bus = self.kind
        self.buffer = str(self.buffer or "")
        if self.buffer and self.buffer not in AUDIO_OUTPUT_BUFFERS:
            raise ValueError(f"Unknown audio output buffer: {self.buffer!r}")
        if self.context:
            self.context = normalize_audio_id(self.context, field_name="context")
        self.layer = normalize_audio_id(self.layer or "main", field_name="layer")

        self.scope = str(self.scope or "global")
        if self.scope not in AUDIO_SCOPES:
            raise ValueError(f"Unknown audio scope: {self.scope!r}")
        if self.scope in {"player", "context"} and not self.context:
            raise ValueError(f"{self.scope.title()}-scoped audio requires a context id")

        self.volume = clamp_int(self.volume, 0, 100, 100)
        derive_position_pan = self.position is not None and self.pan is None
        self.pan = clamp_int(self.pan, -100, 100, 0)
        self.position = normalize_audio_position(self.position)
        if self.position is not None and self.command != "play":
            raise ValueError("Audio positions are only valid on play commands")
        if self.segments and self.position is not None:
            raise ValueError("Sequence positions belong to individual segments")
        self.attenuation = normalize_distance_attenuation(self.attenuation)
        if self.attenuation is not None and self.command != "play":
            raise ValueError("Audio attenuation is only valid on play commands")
        if self.attenuation is not None and self.position is None:
            raise ValueError("Audio attenuation requires a spatial position")
        if self.segments and self.attenuation is not None:
            raise ValueError("Sequence attenuation belongs to individual segments")
        self.motion = normalize_audio_motion(self.motion)
        if self.motion is not None and self.command != "update":
            raise ValueError("Audio motion is only valid on update commands")
        self.gain = normalize_audio_gain(self.gain)
        if self.gain != 1.0 and self.command != "play":
            raise ValueError("Audio source gain is only valid on play commands")
        if self.segments and self.gain != 1.0:
            raise ValueError("Sequence source gain belongs to individual segments")
        self.gain_automation = normalize_audio_gain_automation(self.gain_automation)
        if self.gain_automation is not None and self.command != "update":
            raise ValueError("Audio gain automation is only valid on update commands")
        if derive_position_pan and self.position is not None:
            self.pan = pan_from_position(self.position)
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
        if self.family and (
            self.command != "play" or self.kind != "sfx" or self.loop
        ):
            raise ValueError("Audio families are only valid for one-shot SFX")
        if self.buffer and (
            self.command != "play" or self.kind != "sfx" or self.loop
        ):
            raise ValueError("Output buffers are only valid for one-shot SFX")
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
        if self.command == "update" and (
            not self.kind
            or not self.handle
            or (self.motion is None and self.gain_automation is None)
        ):
            raise ValueError("Update commands require a kind, handle, and automation")
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
            self.kind in {"music", "ambience"}
            or (self.kind == "sfx" and (self.loop or self.segments))
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
            "family": self.family,
            "handle": self.handle,
            "bus": self.bus,
            "buffer": self.buffer,
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
            "position": list(self.position) if self.position is not None else None,
            "attenuation": (
                self.attenuation.to_packet()
                if isinstance(self.attenuation, DistanceAttenuation)
                else None
            ),
            "motion": (
                self.motion.to_packet()
                if isinstance(self.motion, AudioMotion)
                else None
            ),
            "gain": self.gain,
            "gain_automation": (
                self.gain_automation.to_packet()
                if isinstance(self.gain_automation, AudioGainAutomation)
                else None
            ),
            "segments": [segment.to_packet() for segment in self.segments],
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
            "gain": 1.0,
            "segments": [],
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
    position: Position | None = None
    attenuation: DistanceAttenuation | None = None
    motion: AudioMotion | None = None
    gain: float = 1.0
    gain_automation: AudioGainAutomation | None = None
    recipient_ids: list[str] = field(default_factory=list)
    paused: bool = False

    @classmethod
    def from_command(
        cls, command: AudioCommand, recipient_ids: list[str] | None = None
    ) -> AudioPlaybackState:
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
            position=command.position,
            attenuation=command.attenuation,
            gain=command.gain,
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
            position=self.position,
            attenuation=self.attenuation,
            gain=self.gain,
        )

    def replay_commands(self) -> list[AudioCommand]:
        """Return steady-state playback plus unfinished source automation."""
        commands = [self.to_command(replay=True)]
        motion = (
            self.motion
            if self.motion is not None and not self.motion.complete
            else None
        )
        gain_automation = (
            self.gain_automation
            if self.gain_automation is not None and not self.gain_automation.complete
            else None
        )
        if motion is not None or gain_automation is not None:
            commands.append(
                AudioCommand(
                    command="update",
                    kind=self.kind,
                    handle=self.handle,
                    motion=motion,
                    gain_automation=gain_automation,
                )
            )
        return commands
