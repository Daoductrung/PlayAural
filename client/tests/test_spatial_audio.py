"""Golden-vector coverage for the client-neutral spatial-audio contract."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

CLIENT_DIR = Path(__file__).resolve().parents[1]
CONFORMANCE = json.loads(
    (CLIENT_DIR.parent / "audio_protocol_v3_conformance.json").read_text(
        encoding="utf-8"
    )
)
SPEC = importlib.util.spec_from_file_location(
    "spatial_audio_under_test", CLIENT_DIR / "spatial_audio.py"
)
assert SPEC is not None and SPEC.loader is not None
spatial_audio = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = spatial_audio
SPEC.loader.exec_module(spatial_audio)


def _sequence_segment(**overrides):
    segment = {
        "asset": "step.ogg",
        "position": None,
        "destination_position": None,
        "attenuation": None,
        "gain": 1,
        "easing": "linear",
        "next_start_ratio": 1,
    }
    segment.update(overrides)
    return segment


def test_sequence_next_onset_ratio_is_strict_and_bounded() -> None:
    normalized = spatial_audio.normalize_audio_sequence_segments(
        [_sequence_segment(next_start_ratio=0.5)]
    )
    assert normalized[0].next_start_ratio == 0.5
    for ratio in (-0.01, 1.01, float("inf"), float("nan"), True):
        with pytest.raises(ValueError):
            spatial_audio.normalize_audio_sequence_segments(
                [_sequence_segment(next_start_ratio=ratio)]
            )


def test_distance_models_match_shared_protocol_vectors() -> None:
    assert CONFORMANCE["protocol_version"] == 3
    for vector in CONFORMANCE["distance_attenuation"]:
        assert spatial_audio.distance_attenuation_gain(
            vector["position"], vector["attenuation"]
        ) == pytest.approx(vector["expected_gain"]), vector["id"]


def test_ordered_list_positions_span_the_front_audio_field_proportionally() -> None:
    assert spatial_audio.proportional_list_pan(0, 5) == -1
    assert spatial_audio.proportional_list_pan(2, 5) == 0
    assert spatial_audio.proportional_list_pan(4, 5) == 1
    assert spatial_audio.proportional_list_pan(0, 1) == 0
    assert spatial_audio.proportional_list_pan(499_999, 1_000_000) == pytest.approx(
        -1 / 999_999
    )

    assert spatial_audio.frontal_position_for_pan(-1) == (-2, 0, 0)
    assert spatial_audio.frontal_position_for_pan(0) == (0, 2, 0)
    assert spatial_audio.frontal_position_for_pan(1) == (2, 0, 0)


def test_distance_gain_clamps_distance_and_output_gain() -> None:
    attenuation = {
        "model": "inverse",
        "reference_distance": 2,
        "max_distance": 10,
        "rolloff_factor": 1,
        "min_gain": 0.25,
        "max_gain": 0.8,
    }

    assert spatial_audio.distance_attenuation_gain((0, 0, 0), attenuation) == 0.8
    assert spatial_audio.distance_attenuation_gain((100, 0, 0), attenuation) == 0.25
    assert spatial_audio.distance_attenuation_gain((100, 0, 0), None) == 1
    assert spatial_audio.distance_attenuation_gain(
        (100, 0, 0), {"model": "none"}
    ) == 1


def test_attenuation_rejects_zero_rolloff_and_invalid_dataclass() -> None:
    invalid = {
        "model": "inverse",
        "reference_distance": 2,
        "max_distance": 10,
        "rolloff_factor": 0,
        "min_gain": 0,
        "max_gain": 1,
    }
    with pytest.raises(ValueError):
        spatial_audio.normalize_distance_attenuation(invalid)
    with pytest.raises(ValueError):
        spatial_audio.normalize_distance_attenuation(
            spatial_audio.DistanceAttenuation(
                model="none",
                min_gain=0,
            )
        )
    with pytest.raises(ValueError, match="requires a spatial position"):
        spatial_audio.distance_attenuation_gain(None, {**invalid, "rolloff_factor": 1})


def test_motion_curves_match_shared_protocol_vectors() -> None:
    for vector in CONFORMANCE["motion"]:
        assert spatial_audio.audio_motion_position(
            vector["automation"]
        ) == pytest.approx(vector["expected_position"]), vector["id"]


@pytest.mark.parametrize(
    "motion",
    [
        {"origin_position": [0, 0, 0]},
        {
            "origin_position": [0, 0, 0],
            "destination_position": [1, 0, 0],
            "duration_ms": 0,
            "elapsed_ms": 0,
            "easing": "linear",
        },
        {
            "origin_position": [0, 0, 0],
            "destination_position": [1, 0, 0],
            "duration_ms": 100,
            "elapsed_ms": 101,
            "easing": "linear",
        },
        {
            "origin_position": [0, 0, 0],
            "destination_position": [1, 0, 0],
            "duration_ms": 100,
            "elapsed_ms": 0,
            "easing": "unknown",
        },
    ],
)
def test_motion_rejects_partial_and_out_of_range_objects(motion) -> None:
    with pytest.raises(ValueError):
        spatial_audio.normalize_audio_motion(motion)


def test_gain_automation_curves_match_shared_protocol_vectors() -> None:
    for vector in CONFORMANCE["source_gain"]:
        assert spatial_audio.audio_gain_at(
            vector["automation"]
        ) == pytest.approx(vector["expected_gain"]), vector["id"]


@pytest.mark.parametrize(
    "automation",
    [
        {"origin_gain": 0},
        {
            "origin_gain": -0.1,
            "destination_gain": 1,
            "duration_ms": 100,
            "elapsed_ms": 0,
            "easing": "linear",
        },
        {
            "origin_gain": 0,
            "destination_gain": 1,
            "duration_ms": 0,
            "elapsed_ms": 0,
            "easing": "linear",
        },
    ],
)
def test_gain_automation_rejects_partial_and_out_of_range_objects(
    automation,
) -> None:
    with pytest.raises(ValueError):
        spatial_audio.normalize_audio_gain_automation(automation)
