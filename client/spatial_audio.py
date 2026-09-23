"""Shared spatial position and deterministic distance-gain policy."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

MAX_AUDIO_POSITION = 1000.0
ATTENUATION_PRECISION = 6
MAX_AUDIO_DISTANCE = (
    math.ceil(math.sqrt(3.0) * MAX_AUDIO_POSITION * 10**ATTENUATION_PRECISION)
    / 10**ATTENUATION_PRECISION
)
MAX_AUDIO_ROLLOFF = 16.0
MAX_AUDIO_AUTOMATION_MS = 3_600_000
MAX_AUDIO_SEQUENCE_SEGMENTS = 32
TABLE_RADIUS = 2.0
AUDIO_ATTENUATION_MODELS = frozenset({"none", "linear", "inverse", "exponential"})
AUDIO_AUTOMATION_EASINGS = frozenset(
    {"linear", "ease-in", "ease-out", "ease-in-out"}
)

AudioPosition = tuple[float, float, float]


@dataclass(frozen=True)
class DistanceAttenuation:
    """Validated client-side representation of the protocol object."""

    model: str
    reference_distance: float | None = None
    max_distance: float | None = None
    rolloff_factor: float | None = None
    min_gain: float | None = None
    max_gain: float | None = None


@dataclass(frozen=True)
class AudioMotion:
    """Validated, resumable position automation from the audio protocol."""

    origin_position: AudioPosition
    destination_position: AudioPosition
    duration_ms: int
    elapsed_ms: int
    easing: str


@dataclass(frozen=True)
class AudioGainAutomation:
    """Validated, resumable source-gain automation."""

    origin_gain: float
    destination_gain: float
    duration_ms: int
    elapsed_ms: int
    easing: str


@dataclass(frozen=True)
class AudioSequenceSegment:
    """Validated finite SFX segment with a decoded-duration onset."""

    asset: str
    position: AudioPosition | None
    destination_position: AudioPosition | None
    attenuation: DistanceAttenuation | None
    gain: float
    easing: str
    next_start_ratio: float


def normalize_audio_gain(value: Any) -> float:
    """Return a finite source gain in the closed unit interval."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Audio source gain must be a number")
    gain = float(value)
    if not math.isfinite(gain) or not 0.0 <= gain <= 1.0:
        raise ValueError("Audio source gain is out of range")
    return gain


def normalize_audio_sequence_segments(value: Any) -> tuple[AudioSequenceSegment, ...]:
    """Parse the exact finite-sequence schema without partial playback."""
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError("Audio sequence segments must be a sequence")
    if not 0 < len(value) <= MAX_AUDIO_SEQUENCE_SEGMENTS:
        raise ValueError("Audio sequence segment count is out of range")
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
        if not isinstance(item, Mapping) or set(item) != expected:
            raise ValueError("Audio sequence segment fields are invalid")
        if not isinstance(item["asset"], str) or not item["asset"]:
            raise ValueError("Audio sequence asset must be a non-empty string")
        asset = item["asset"]
        position = normalize_audio_position(item["position"])
        destination = normalize_audio_position(item["destination_position"])
        attenuation = normalize_distance_attenuation(item["attenuation"])
        gain = normalize_audio_gain(item["gain"])
        next_start_ratio = normalize_audio_gain(item["next_start_ratio"])
        easing = str(item["easing"])
        if attenuation is not None and position is None:
            raise ValueError("Sequence attenuation requires a spatial position")
        if destination is not None and position is None:
            raise ValueError("Sequence motion requires an origin position")
        if easing not in AUDIO_AUTOMATION_EASINGS:
            raise ValueError("Unknown audio sequence easing")
        if destination is None and easing != "linear":
            raise ValueError("Static audio sequence segments require linear easing")
        normalized.append(
            AudioSequenceSegment(
                asset=asset,
                position=position,
                destination_position=destination,
                attenuation=attenuation,
                gain=gain,
                easing=easing,
                next_start_ratio=next_start_ratio,
            )
        )
    return tuple(normalized)


def normalize_audio_position(value: Any) -> AudioPosition | None:
    """Return a finite listener-relative point, or raise for malformed input."""
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError("Audio position must contain three numbers")
    coordinates = list(value)
    if len(coordinates) != 3 or any(
        isinstance(component, bool) or not isinstance(component, (int, float))
        for component in coordinates
    ):
        raise ValueError("Audio position must contain three numbers")
    position = tuple(float(component) for component in coordinates)
    if not all(
        math.isfinite(component) and abs(component) <= MAX_AUDIO_POSITION
        for component in position
    ):
        raise ValueError("Audio position coordinates must be finite and in range")
    return position


def proportional_list_pan(index: int, count: int) -> float:
    """Map a zero-based list index across the full left-to-right field."""
    if count <= 1:
        return 0.0
    bounded_index = max(0, min(count - 1, index))
    return (bounded_index / (count - 1) * 2.0) - 1.0


def frontal_position_for_pan(
    pan: float,
    radius: float = TABLE_RADIUS,
) -> AudioPosition:
    """Place a normalized pan on the listener's forward-facing semicircle."""
    bounded_pan = max(-1.0, min(1.0, float(pan)))
    x = bounded_pan * radius
    y = math.sqrt(max(0.0, radius * radius - x * x))
    return (x, y, 0.0)


def normalize_distance_attenuation(value: Any) -> DistanceAttenuation | None:
    """Parse the exact version-3 attenuation schema without client defaults."""
    if value is None:
        return None
    if isinstance(value, DistanceAttenuation):
        fields = {
            "model": value.model,
            "reference_distance": value.reference_distance,
            "max_distance": value.max_distance,
            "rolloff_factor": value.rolloff_factor,
            "min_gain": value.min_gain,
            "max_gain": value.max_gain,
        }
        parameters = tuple(fields[name] for name in fields if name != "model")
        value = (
            {"model": "none"}
            if value.model == "none" and all(item is None for item in parameters)
            else fields
        )
    if not isinstance(value, Mapping):
        raise ValueError("Audio attenuation must be an object")
    fields = dict(value)
    model = fields.get("model")
    if model not in AUDIO_ATTENUATION_MODELS:
        raise ValueError("Unknown audio attenuation model")
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
        raise ValueError("Audio attenuation has missing or unknown fields")
    if model == "none":
        return DistanceAttenuation(model="none")

    values = [
        fields["reference_distance"],
        fields["max_distance"],
        fields["rolloff_factor"],
        fields["min_gain"],
        fields["max_gain"],
    ]
    if any(
        isinstance(item, bool)
        or not isinstance(item, (int, float))
        or not math.isfinite(float(item))
        for item in values
    ):
        raise ValueError("Audio attenuation parameters must be finite numbers")
    reference_distance, max_distance, rolloff_factor, min_gain, max_gain = map(
        float, values
    )
    if not 0.0 < reference_distance < max_distance <= MAX_AUDIO_DISTANCE:
        raise ValueError("Audio attenuation distances are out of range")
    maximum_rolloff = 1.0 if model == "linear" else MAX_AUDIO_ROLLOFF
    if not 0.0 < rolloff_factor <= maximum_rolloff:
        raise ValueError("Audio attenuation rolloff is out of range")
    if not 0.0 <= min_gain <= max_gain <= 1.0:
        raise ValueError("Audio attenuation gains are out of range")
    return DistanceAttenuation(
        model=model,
        reference_distance=reference_distance,
        max_distance=max_distance,
        rolloff_factor=rolloff_factor,
        min_gain=min_gain,
        max_gain=max_gain,
    )


def normalize_audio_motion(value: Any) -> AudioMotion | None:
    """Parse the exact version-3 position-automation schema."""
    if value is None:
        return None
    if isinstance(value, AudioMotion):
        value = {
            "origin_position": value.origin_position,
            "destination_position": value.destination_position,
            "duration_ms": value.duration_ms,
            "elapsed_ms": value.elapsed_ms,
            "easing": value.easing,
        }
    if not isinstance(value, Mapping):
        raise ValueError("Audio motion must be an object")
    fields = dict(value)
    expected = {
        "origin_position",
        "destination_position",
        "duration_ms",
        "elapsed_ms",
        "easing",
    }
    if set(fields) != expected:
        raise ValueError("Audio motion has missing or unknown fields")
    origin = normalize_audio_position(fields["origin_position"])
    destination = normalize_audio_position(fields["destination_position"])
    if origin is None or destination is None:
        raise ValueError("Audio motion requires origin and destination positions")
    duration_ms = fields["duration_ms"]
    elapsed_ms = fields["elapsed_ms"]
    if (
        isinstance(duration_ms, bool)
        or not isinstance(duration_ms, int)
        or not 0 < duration_ms <= MAX_AUDIO_AUTOMATION_MS
    ):
        raise ValueError("Audio motion duration is out of range")
    if (
        isinstance(elapsed_ms, bool)
        or not isinstance(elapsed_ms, int)
        or not 0 <= elapsed_ms <= duration_ms
    ):
        raise ValueError("Audio motion elapsed time is out of range")
    easing = fields["easing"]
    if easing not in AUDIO_AUTOMATION_EASINGS:
        raise ValueError("Unknown audio motion easing")
    return AudioMotion(origin, destination, duration_ms, elapsed_ms, easing)


def normalize_audio_gain_automation(value: Any) -> AudioGainAutomation | None:
    """Parse the exact version-3 source-gain automation schema."""
    if value is None:
        return None
    if isinstance(value, AudioGainAutomation):
        value = {
            "origin_gain": value.origin_gain,
            "destination_gain": value.destination_gain,
            "duration_ms": value.duration_ms,
            "elapsed_ms": value.elapsed_ms,
            "easing": value.easing,
        }
    if not isinstance(value, Mapping):
        raise ValueError("Audio gain automation must be an object")
    fields = dict(value)
    expected = {
        "origin_gain",
        "destination_gain",
        "duration_ms",
        "elapsed_ms",
        "easing",
    }
    if set(fields) != expected:
        raise ValueError("Audio gain automation has missing or unknown fields")
    origin = normalize_audio_gain(fields["origin_gain"])
    destination = normalize_audio_gain(fields["destination_gain"])
    duration_ms = fields["duration_ms"]
    elapsed_ms = fields["elapsed_ms"]
    if (
        isinstance(duration_ms, bool)
        or not isinstance(duration_ms, int)
        or not 0 < duration_ms <= MAX_AUDIO_AUTOMATION_MS
    ):
        raise ValueError("Audio gain duration is out of range")
    if (
        isinstance(elapsed_ms, bool)
        or not isinstance(elapsed_ms, int)
        or not 0 <= elapsed_ms <= duration_ms
    ):
        raise ValueError("Audio gain elapsed time is out of range")
    easing = fields["easing"]
    if easing not in AUDIO_AUTOMATION_EASINGS:
        raise ValueError("Unknown audio gain easing")
    return AudioGainAutomation(origin, destination, duration_ms, elapsed_ms, easing)


def audio_motion_progress(progress: float, easing: str) -> float:
    """Evaluate the protocol's deterministic quadratic easing functions."""
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
    raise ValueError("Unknown audio motion easing")


def audio_motion_position(
    motion: AudioMotion | Mapping[str, Any],
    elapsed_ms: float | None = None,
) -> AudioPosition:
    """Interpolate one source position at an absolute trajectory time."""
    normalized = normalize_audio_motion(motion)
    if normalized is None:
        raise ValueError("Audio motion is required")
    elapsed = normalized.elapsed_ms if elapsed_ms is None else float(elapsed_ms)
    ratio = audio_motion_progress(elapsed / normalized.duration_ms, normalized.easing)
    return tuple(
        origin + ((destination - origin) * ratio)
        for origin, destination in zip(
            normalized.origin_position,
            normalized.destination_position,
            strict=True,
        )
    )


def audio_gain_at(
    automation: AudioGainAutomation | Mapping[str, Any],
    elapsed_ms: float | None = None,
) -> float:
    """Interpolate one source gain at an absolute automation time."""
    normalized = normalize_audio_gain_automation(automation)
    if normalized is None:
        raise ValueError("Audio gain automation is required")
    elapsed = normalized.elapsed_ms if elapsed_ms is None else float(elapsed_ms)
    ratio = audio_motion_progress(elapsed / normalized.duration_ms, normalized.easing)
    return normalized.origin_gain + (
        (normalized.destination_gain - normalized.origin_gain) * ratio
    )


def distance_attenuation_gain(
    position: AudioPosition | None,
    attenuation: DistanceAttenuation | Mapping[str, Any] | None,
) -> float:
    """Calculate the canonical distance gain used by every first-party client."""
    normalized = normalize_distance_attenuation(attenuation)
    if normalized is None or normalized.model == "none":
        return 1.0
    if position is None:
        raise ValueError("Audio attenuation requires a spatial position")
    distance = math.sqrt(sum(coordinate * coordinate for coordinate in position))
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
