"""Unified audio protocol, routing, and persistence coverage."""

import asyncio
import json
from pathlib import Path

import pytest

from ..audio import (
    AUDIO_PROTOCOL_VERSION,
    AudioCommand,
    AudioGainAutomation,
    AudioMotion,
    AudioPlaybackState,
    AudioSequenceSegment,
    DistanceAttenuation,
    SameTurnAudioBatcher,
    audio_motion_position,
    clock_position,
    distance_attenuation_gain,
    pan_from_position,
    seat_position,
)
from ..games.pig.game import PigGame
from ..users.network_user import NetworkUser
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE = json.loads(
    (ROOT / "audio_protocol_v3_conformance.json").read_text(encoding="utf-8")
)


@pytest.mark.asyncio
async def test_same_turn_audio_batcher_has_no_time_debounce_window() -> None:
    batcher = SameTurnAudioBatcher()
    calls: list[str] = []

    assert batcher.queue("join", lambda: calls.append("first")) is True
    assert batcher.queue("join", lambda: calls.append("duplicate")) is False
    assert calls == []

    await asyncio.sleep(0)
    assert calls == ["first"]

    assert batcher.queue("join", lambda: calls.append("next-turn")) is True
    await asyncio.sleep(0)
    assert calls == ["first", "next-turn"]


@pytest.mark.asyncio
async def test_same_turn_audio_batcher_keeps_only_highest_group_priority() -> None:
    batcher = SameTurnAudioBatcher()
    calls: list[str] = []

    assert batcher.queue(
        "voice",
        lambda: calls.append("voice"),
        group="alice-leave",
        priority=10,
    )
    assert batcher.queue(
        "table",
        lambda: calls.append("table"),
        group="alice-leave",
        priority=20,
    )
    assert not batcher.queue(
        "late-voice",
        lambda: calls.append("late-voice"),
        group="alice-leave",
        priority=10,
    )
    assert batcher.queue(
        "second-table",
        lambda: calls.append("second-table"),
        group="alice-leave",
        priority=20,
    )

    await asyncio.sleep(0)

    assert calls == ["table", "second-table"]


@pytest.mark.asyncio
async def test_same_turn_audio_batcher_isolates_callback_failures() -> None:
    batcher = SameTurnAudioBatcher()
    loop = asyncio.get_running_loop()
    reported_errors: list[dict] = []
    previous_handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda _loop, context: reported_errors.append(context))
    calls: list[str] = []

    def fail() -> None:
        raise RuntimeError("listener disconnected")

    try:
        assert batcher.queue("alice", fail) is True
        assert batcher.queue("bob", lambda: calls.append("bob")) is True
        await asyncio.sleep(0)
    finally:
        loop.set_exception_handler(previous_handler)

    assert calls == ["bob"]
    assert len(reported_errors) == 1
    assert isinstance(reported_errors[0]["exception"], RuntimeError)


@pytest.mark.asyncio
async def test_table_presence_cues_batch_only_within_one_event_loop_turn(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice.clear_messages()
    bob.clear_messages()

    game.play_table_join_sound(is_bot=False, is_spectator=False)
    game.play_table_join_sound(is_bot=False, is_spectator=True)
    game.play_table_leave_sound(is_bot=False, is_spectator=False)
    game.play_table_leave_sound(is_bot=False, is_spectator=True)
    await asyncio.sleep(0)

    for user in (alice, bob):
        assert user.get_sounds_played() == ["table_join.ogg", "table_leave.ogg"]

    game.play_table_join_sound(is_bot=False, is_spectator=False)
    await asyncio.sleep(0)

    for user in (alice, bob):
        assert user.get_sounds_played() == [
            "table_join.ogg",
            "table_leave.ogg",
            "table_join.ogg",
        ]


def test_audio_command_rejects_unsafe_assets_and_ids() -> None:
    for asset in ("../secret.ogg", "/absolute.ogg", "https://bad/audio.ogg"):
        with pytest.raises(ValueError):
            AudioCommand(command="play", kind="sfx", asset=asset)
    with pytest.raises(ValueError):
        AudioCommand(
            command="play",
            kind="ambience",
            asset="rain.ogg",
            scope="context",
        )


def test_game_sound_family_dispatches_one_validated_family_to_every_listener(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice.clear_messages()
    bob.clear_messages()

    game.play_sound_family("game_squares/diceroll")

    for user in (alice, bob):
        message = user.messages[-1]
        assert message.type == "play_sound"
        assert message.data["family"] == "game_squares/diceroll"
        assert "asset" not in message.data


def test_seated_sound_is_positioned_per_listener(pig_game_with_players) -> None:
    game, alice, bob = pig_game_with_players
    alice.clear_messages()
    bob.clear_messages()
    seated = next(player for player in game.players if str(player.id) == alice.uuid)

    attenuation = DistanceAttenuation(
        model="linear",
        reference_distance=1,
        max_distance=4,
        rolloff_factor=1,
        min_gain=0,
        max_gain=1,
    )
    game.play_sound("game/test.ogg", seat_of=seated, attenuation=attenuation)

    # The seated player hears their own cue unpositioned and centred.
    own = alice.messages[-1].data
    assert "position" not in own
    assert "attenuation" not in own
    assert own.get("pan", 0) == 0
    # Two players face each other, so the other player hears it straight
    # ahead, with a centred pan for clients that cannot place it.
    other = bob.messages[-1].data
    assert other["position"] == [0.0, 2.0, 0.0]
    assert other["attenuation"]["model"] == "linear"
    assert other.get("pan", 0) == 0

    with pytest.raises(ValueError, match="mutually exclusive"):
        game.play_sound(
            "game/test.ogg",
            seat_of=seated,
            position=(0, 2, 0),
        )


def test_audio_sequence_serializes_complete_atomic_timeline() -> None:
    attenuation = DistanceAttenuation(
        model="inverse",
        reference_distance=1,
        max_distance=30,
        rolloff_factor=1,
        min_gain=0.05,
        max_gain=1,
    )
    command = AudioCommand(
        command="play",
        kind="sfx",
        handle="grenade:42",
        segments=[
            AudioSequenceSegment(
                asset="battle/mvsounds_named/throw.ogg",
                position=(0, 1, 0),
            ),
            AudioSequenceSegment(
                asset="battle/mvsounds_named/hand grenade.ogg",
                position=(0, 1, 0),
                destination_position=(8, 14, -2),
                attenuation=attenuation,
                gain=0.8,
                easing="ease-out",
            ),
            AudioSequenceSegment(
                asset="game_bang/dynamite_explosion.ogg",
                position=(8, 14, -2),
                attenuation=attenuation,
            ),
        ],
    )

    packet = command.to_packet()
    assert packet["handle"] == "grenade:42"
    assert "asset" not in packet
    assert packet["segments"] == [
        {
            "asset": "battle/mvsounds_named/throw.ogg",
            "position": [0.0, 1.0, 0.0],
            "destination_position": None,
            "attenuation": None,
            "gain": 1.0,
            "easing": "linear",
            "next_start_ratio": 1.0,
        },
        {
            "asset": "battle/mvsounds_named/hand grenade.ogg",
            "position": [0.0, 1.0, 0.0],
            "destination_position": [8.0, 14.0, -2.0],
            "attenuation": attenuation.to_packet(),
            "gain": 0.8,
            "easing": "ease-out",
            "next_start_ratio": 1.0,
        },
        {
            "asset": "game_bang/dynamite_explosion.ogg",
            "position": [8.0, 14.0, -2.0],
            "destination_position": None,
            "attenuation": attenuation.to_packet(),
            "gain": 1.0,
            "easing": "linear",
            "next_start_ratio": 1.0,
        },
    ]
    with pytest.raises(ValueError, match="stable handle"):
        AudioCommand(
            command="play",
            kind="sfx",
            segments=[AudioSequenceSegment(asset="game/test.ogg")],
        )


def test_non_sequence_audio_packet_omits_empty_segments() -> None:
    packet = AudioCommand(
        command="play",
        kind="sfx",
        asset="game/test.ogg",
    ).to_packet()

    assert "segments" not in packet


@pytest.mark.parametrize("ratio", [-0.01, 1.01, float("inf"), float("nan"), True])
def test_audio_sequence_rejects_invalid_next_onset_ratios(ratio) -> None:
    with pytest.raises(ValueError):
        AudioSequenceSegment(asset="game/test.ogg", next_start_ratio=ratio)


@pytest.mark.parametrize(
    "segments",
    [
        [],
        [{"asset": "sound.ogg"}],
        [
            {
                "asset": "sound.ogg",
                "position": None,
                "destination_position": [1, 2, 3],
                "attenuation": None,
                "gain": 1,
                "easing": "linear",
            }
        ],
        [
            {
                "asset": "../sound.ogg",
                "position": None,
                "destination_position": None,
                "attenuation": None,
                "gain": 1,
                "easing": "linear",
            }
        ],
    ],
)
def test_audio_sequence_rejects_partial_empty_or_unsafe_payloads(segments) -> None:
    with pytest.raises(ValueError):
        AudioCommand(
            command="play",
            kind="sfx",
            handle="sequence:test",
            segments=segments,
        )

    if segments:
        with pytest.raises(ValueError):
            AudioCommand(command="play", kind="sfx", segments=segments)


def test_game_sound_chain_dispatches_one_packet_and_is_not_replay_state(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice.clear_messages()
    bob.clear_messages()

    handle = game.play_sound_chain(
        [AudioSequenceSegment(asset="game/test.ogg", position=(0, 2, 0))],
        handle="sequence:test",
    )

    assert handle == "sequence:test"
    for user in (alice, bob):
        assert user.messages[-1].data["handle"] == handle
        assert len(user.messages[-1].data["segments"]) == 1
    assert all(state.handle != handle for state in game.active_audio.values())


def test_runtime_audio_cannot_replace_a_replayable_handle(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    game.play_sound(
        "fuse.ogg",
        loop=True,
        handle="shared:source",
        persist=True,
    )
    alice.clear_messages()
    bob.clear_messages()

    with pytest.raises(ValueError, match="replayable stable handle"):
        game.play_sound_chain(
            [AudioSequenceSegment(asset="explosion.ogg")],
            handle="shared:source",
        )

    assert alice.messages == []
    assert bob.messages == []
    assert next(iter(game.active_audio.values())).asset == "fuse.ogg"


def test_seated_loop_persists_for_a_disconnected_listener(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    seated = game.get_player_by_id(alice.uuid)
    assert seated is not None
    game._users.pop(bob.uuid)
    alice.clear_messages()
    bob.clear_messages()

    game.play_sound(
        "game/moving_loop.ogg",
        loop=True,
        handle="moving-loop",
        persist=True,
        seat_of=seated,
    )

    states = list(game.active_audio.values())
    assert len(states) == 2
    assert sorted(state.recipient_ids for state in states) == sorted(
        [[alice.uuid], [bob.uuid]]
    )
    assert len(alice.messages) == 1
    assert bob.messages == []

    game.attach_user(bob.uuid, bob)

    replay = bob.messages[-1].data
    assert replay["handle"] == "moving-loop"
    assert replay["position"] == [0.0, 2.0, 0.0]
    assert replay["play_intro"] is False
    assert "fade_in_ms" not in replay


def test_audio_command_serializes_validated_one_shot_sound_family() -> None:
    packet = AudioCommand(
        command="play",
        kind="sfx",
        family="notifications/notify",
    ).to_packet()

    assert packet["family"] == "notifications/notify"
    assert "asset" not in packet


def test_audio_command_serializes_validated_output_buffer_for_notification_sfx() -> None:
    packet = AudioCommand(
        command="play",
        kind="sfx",
        asset="pm.ogg",
        buffer="private",
    ).to_packet()

    assert packet["buffer"] == "private"


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "command": "play",
            "kind": "sfx",
            "asset": "pm.ogg",
            "buffer": "unknown",
        },
        {
            "command": "play",
            "kind": "music",
            "asset": "music.ogg",
            "handle": "music",
            "buffer": "private",
        },
        {
            "command": "play",
            "kind": "sfx",
            "asset": "pm.ogg",
            "handle": "pm",
            "loop": True,
            "buffer": "private",
        },
        {"command": "stop_all", "buffer": "private"},
    ],
)
def test_audio_command_rejects_invalid_output_buffer_usage(kwargs) -> None:
    with pytest.raises(ValueError):
        AudioCommand(**kwargs)


@pytest.mark.parametrize("loop", [False, True])
def test_numbered_asset_remains_an_exact_sound_reference(loop: bool) -> None:
    packet = AudioCommand(
        command="play",
        kind="sfx",
        asset="effects/alert2.ogg",
        handle="alert:exact" if loop else "",
        loop=loop,
    ).to_packet()

    assert packet["asset"] == "effects/alert2.ogg"
    assert "family" not in packet
    assert packet["loop"] is loop


@pytest.mark.parametrize(
    "kwargs",
    [
        {"command": "play", "kind": "sfx", "family": "../notify"},
        {"command": "play", "kind": "sfx", "family": "notify.ogg"},
        {"command": "play", "kind": "sfx", "family": "notify.variant"},
        {
            "command": "play",
            "kind": "sfx",
            "asset": "notify1.ogg",
            "family": "notify",
        },
        {"command": "play", "kind": "music", "family": "notify"},
        {"command": "play", "kind": "sfx", "family": "notify", "loop": True},
        {"command": "stop_all", "family": "notify"},
    ],
)
def test_audio_command_rejects_invalid_sound_family_usage(kwargs) -> None:
    with pytest.raises(ValueError):
        AudioCommand(**kwargs)


def test_shared_presence_and_notification_assets_match_every_sound_pack() -> None:
    pack_roots = [
        ROOT / "client" / "sounds",
        ROOT / "web_client" / "sounds",
        ROOT / "mobile_client" / "sounds",
    ]
    required_assets = {
        "chatlocal.ogg",
        "disconnect.ogg",
        "reconnect.ogg",
        "table_join.ogg",
        "table_kick.ogg",
        "table_leave.ogg",
        *(f"notify{index}.ogg" for index in range(1, 5)),
    }

    for asset in required_assets:
        payloads = [(pack / asset).read_bytes() for pack in pack_roots]
        assert payloads[1:] == payloads[:-1]
    assert all(not (pack / "notify.ogg").exists() for pack in pack_roots)


def test_audio_command_clamps_untrusted_mix_values() -> None:
    command = AudioCommand(
        command="play",
        kind="sfx",
        asset="game/test.ogg",
        volume=500,
        pan=-500,
        pitch=0,
        fade_in_ms=999_999,
        priority=999,
        max_instances=999,
        ducking={"music": -5},
    )
    packet = command.to_packet()

    assert packet["version"] == AUDIO_PROTOCOL_VERSION
    assert command.volume == 100
    assert command.pan == -100
    assert command.pitch == 25
    assert command.fade_in_ms == 60_000
    assert command.priority == 100
    assert command.max_instances == 64
    assert packet["ducking"] == {"music": 0}


def test_audio_command_validates_position_and_derives_pan() -> None:
    right = AudioCommand(
        command="play", kind="sfx", asset="game/test.ogg", position=[2, 0, 0]
    )
    assert right.position == (2.0, 0.0, 0.0)
    assert right.pan == 100
    packet = right.to_packet()
    assert packet["position"] == [2.0, 0.0, 0.0]
    assert packet["pan"] == 100

    ahead = AudioCommand(
        command="play", kind="sfx", asset="game/test.ogg", position=(0, 2, 0)
    )
    assert ahead.pan == 0
    assert "pan" not in ahead.to_packet()

    front_left = AudioCommand(
        command="play", kind="sfx", asset="game/test.ogg", position=(-1, 1, 0)
    )
    assert front_left.pan == -71

    explicit = AudioCommand(
        command="play", kind="sfx", asset="game/test.ogg", position=[2, 0, 0], pan=-20
    )
    assert explicit.pan == -20
    explicit_center = AudioCommand(
        command="play", kind="sfx", asset="game/test.ogg", position=[2, 0, 0], pan=0
    )
    assert explicit_center.pan == 0

    plain = AudioCommand(command="play", kind="sfx", asset="game/test.ogg")
    assert plain.position is None
    assert "position" not in plain.to_packet()

    for bad in (
        [1, 2],
        "north",
        ["1", 0, 0],
        [True, 0, 0],
        [1, float("nan"), 0],
        [1e9, 0, 0],
        {"x": 1},
    ):
        with pytest.raises(ValueError):
            AudioCommand(
                command="play", kind="sfx", asset="game/test.ogg", position=bad
            )

    with pytest.raises(ValueError, match="only valid on play"):
        AudioCommand(command="stop", kind="sfx", handle="test", position=[1, 0, 0])

    state = AudioPlaybackState.from_command(
        AudioCommand(
            command="play",
            kind="sfx",
            asset="game/loop.ogg",
            handle="engine",
            loop=True,
            position=[0, -2, 0],
        )
    )
    assert state.to_command(replay=True).position == (0.0, -2.0, 0.0)


def test_distance_attenuation_matches_shared_protocol_vectors() -> None:
    assert CONFORMANCE["protocol_version"] == AUDIO_PROTOCOL_VERSION
    for vector in CONFORMANCE["distance_attenuation"]:
        attenuation = DistanceAttenuation(**vector["attenuation"])
        assert distance_attenuation_gain(
            vector["position"], attenuation
        ) == pytest.approx(vector["expected_gain"]), vector["id"]


def test_audio_command_serializes_complete_attenuation_and_replays_it() -> None:
    attenuation = DistanceAttenuation(
        model="linear",
        reference_distance=2,
        max_distance=10,
        rolloff_factor=1,
        min_gain=0.1,
        max_gain=0.9,
    )
    command = AudioCommand(
        command="play",
        kind="ambience",
        asset="forest/loop.ogg",
        handle="forest",
        loop=True,
        position=(6, 0, 0),
        attenuation=attenuation,
    )

    assert command.to_packet()["attenuation"] == {
        "model": "linear",
        "reference_distance": 2.0,
        "max_distance": 10.0,
        "rolloff_factor": 1.0,
        "min_gain": 0.1,
        "max_gain": 0.9,
    }
    replay = AudioPlaybackState.from_command(command).to_command(replay=True)
    assert replay.attenuation == attenuation
    assert replay.position == (6.0, 0.0, 0.0)


@pytest.mark.parametrize(
    "attenuation",
    [
        {"model": "linear"},
        {
            "model": "linear",
            "reference_distance": 2,
            "max_distance": 10,
            "rolloff_factor": 0,
            "min_gain": 0,
            "max_gain": 1,
        },
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
        {"model": "none", "reference_distance": 2},
        {"model": "unknown"},
    ],
)
def test_audio_command_rejects_malformed_attenuation(attenuation) -> None:
    with pytest.raises(ValueError):
        AudioCommand(
            command="play",
            kind="sfx",
            asset="game/test.ogg",
            position=(6, 0, 0),
            attenuation=attenuation,
        )


def test_audio_command_requires_position_for_attenuation() -> None:
    with pytest.raises(ValueError, match="requires a spatial position"):
        AudioCommand(
            command="play",
            kind="sfx",
            asset="game/test.ogg",
            attenuation={"model": "none"},
        )

    command = AudioCommand(
        command="play",
        kind="sfx",
        asset="game/test.ogg",
        position=(100, 0, 0),
        attenuation={"model": "none"},
    )
    assert command.to_packet()["attenuation"] == {"model": "none"}
    assert distance_attenuation_gain(command.position, command.attenuation) == 1

    with pytest.raises(ValueError, match="requires a spatial position"):
        distance_attenuation_gain(None, attenuation={
            "model": "linear",
            "reference_distance": 2,
            "max_distance": 10,
            "rolloff_factor": 1,
            "min_gain": 0,
            "max_gain": 1,
        })


def test_audio_motion_matches_shared_protocol_vectors() -> None:
    for vector in CONFORMANCE["motion"]:
        motion = AudioMotion(**vector["automation"])
        assert audio_motion_position(motion) == pytest.approx(
            vector["expected_position"]
        ), vector["id"]
        packet = AudioCommand(
            command="update",
            kind="sfx",
            handle="engine",
            motion=motion,
        ).to_packet()
        assert packet["motion"] == motion.to_packet()
        assert "position" not in packet


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
            "easing": "cubic-mystery",
        },
    ],
)
def test_audio_command_rejects_partial_or_invalid_motion(motion) -> None:
    with pytest.raises((TypeError, ValueError)):
        AudioCommand(
            command="update",
            kind="sfx",
            handle="engine",
            motion=motion,
        )



def test_audio_command_rejects_motion_on_play() -> None:
    with pytest.raises(ValueError, match="only valid on update"):
        AudioCommand(
            command="play",
            kind="sfx",
            asset="engine.ogg",
            motion=AudioMotion(
                origin_position=(0, 0, 0),
                destination_position=(1, 0, 0),
                duration_ms=100,
            ),
        )


def test_audio_gain_automation_matches_shared_protocol_vectors() -> None:
    for vector in CONFORMANCE["source_gain"]:
        automation = AudioGainAutomation(**vector["automation"])
        assert automation.gain_at() == pytest.approx(
            vector["expected_gain"]
        ), vector["id"]
        packet = AudioCommand(
            command="update",
            kind="ambience",
            handle="forest",
            gain_automation=automation,
        ).to_packet()
        assert packet["gain_automation"] == automation.to_packet()
        assert "gain" not in packet


@pytest.mark.parametrize("gain", [-0.01, 1.01, float("nan"), True, "0.5"])
def test_audio_command_rejects_invalid_source_gain(gain) -> None:
    with pytest.raises(ValueError):
        AudioCommand(
            command="play",
            kind="sfx",
            asset="engine.ogg",
            gain=gain,
        )


def test_audio_update_requires_at_least_one_automation() -> None:
    with pytest.raises(ValueError, match="automation"):
        AudioCommand(command="update", kind="ambience", handle="forest")


def test_clock_and_seat_geometry_place_sounds_around_the_listener() -> None:
    assert clock_position(12) == (0.0, 2.0, 0.0)
    assert clock_position(3) == (2.0, 0.0, 0.0)
    assert clock_position(6) == (0.0, -2.0, 0.0)
    assert clock_position(9) == (-2.0, 0.0, 0.0)
    assert pan_from_position(clock_position(6)) == 0
    assert pan_from_position(clock_position(9)) == -100
    assert pan_from_position(clock_position(1)) == 50

    # Four seats, listener in seat 0: next clockwise is left, opposite is
    # ahead, previous is right, own seat is unpositioned.
    assert seat_position(0, 0, 4) is None
    assert seat_position(1, 0, 4) == (-2.0, 0.0, 0.0)
    assert seat_position(2, 0, 4) == (0.0, 2.0, 0.0)
    assert seat_position(3, 0, 4) == (2.0, 0.0, 0.0)
    # The same table heard from seat 2.
    assert seat_position(0, 2, 4) == (0.0, 2.0, 0.0)
    assert seat_position(3, 2, 4) == (-2.0, 0.0, 0.0)
    # Two players face each other.
    assert seat_position(1, 0, 2) == (0.0, 2.0, 0.0)
    # A spectator hears seat 0 ahead and the rest clockwise.
    assert seat_position(0, None, 4) == (0.0, 2.0, 0.0)
    assert seat_position(1, None, 4) == (2.0, 0.0, 0.0)
    # Degenerate tables have nothing to place.
    assert seat_position(0, None, 1) is None


def test_audio_packet_keeps_explicit_non_looping_and_stem_controls() -> None:
    packet = AudioCommand(
        command="play",
        kind="ambience",
        asset="storm/loop.ogg",
        handle="storm",
        intro="storm/intro.ogg",
        outro="storm/outro.ogg",
        loop=False,
        play_intro=False,
        play_outro=False,
        seamless=False,
    ).to_packet()

    assert packet["loop"] is False
    assert packet["play_intro"] is False
    assert packet["play_outro"] is False
    assert packet["seamless"] is False


def test_audio_playback_state_preserves_disabled_outro_on_replay() -> None:
    command = AudioCommand(
        command="play",
        kind="ambience",
        asset="storm/loop.ogg",
        handle="storm",
        intro="storm/intro.ogg",
        outro="storm/outro.ogg",
        play_outro=False,
    )

    state = AudioPlaybackState.from_command(command)
    replay = state.to_command(replay=True)

    assert state.play_outro is False
    assert replay.play_outro is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"command": "pause", "kind": "sfx", "handle": "effect"},
        {"command": "resume", "kind": "music"},
        {"command": "stop", "kind": "sfx"},
        {"command": "set_bus"},
        {
            "command": "play",
            "kind": "sfx",
            "asset": "loop.ogg",
            "loop": True,
        },
    ],
)
def test_audio_command_rejects_incomplete_lifecycle_operations(kwargs) -> None:
    with pytest.raises(ValueError):
        AudioCommand(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "command": "stop",
            "kind": "ambience",
            "outro_mode": "after_the_next_full_moon",
        },
        {"command": "stop_all", "all_layers": True},
        {
            "command": "stop",
            "kind": "ambience",
            "handle": "weather",
            "all_layers": True,
        },
        {
            "command": "stop",
            "kind": "ambience",
            "play_outros": True,
        },
    ],
)
def test_audio_command_rejects_invalid_teardown_controls(kwargs) -> None:
    with pytest.raises(ValueError):
        AudioCommand(**kwargs)


def test_all_layer_ambience_stop_preserves_music_and_requests_outros(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.play_music("music/round.ogg")
    game.play_ambience(
        "weather/rain.ogg",
        outro="weather/rain_outro.ogg",
        layer="weather",
    )
    game.play_ambience(
        "room/fire.ogg",
        outro="room/fire_outro.ogg",
        layer="room",
    )
    alice.clear_messages()

    game.stop_all_ambience(outro_mode="immediate")

    packet = alice.messages[-1].data
    assert packet["command"] == "stop"
    assert packet["kind"] == "ambience"
    assert packet["all_layers"] is True
    assert packet.get("play_outro", True) is True
    assert packet.get("outro_mode", "immediate") == "immediate"
    assert [state.kind for state in game.active_audio.values()] == ["music"]


def test_finite_music_crossfades_without_becoming_replayable_state(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.play_music(
        "music/round_loop.ogg",
        handle="phase-music",
        layer="phase",
    )
    assert any(
        state.kind == "music" and state.handle == "phase-music"
        for state in game.active_audio.values()
    )
    alice.clear_messages()

    game.play_music(
        "music/round_stinger.ogg",
        looping=False,
        handle="phase-music",
        layer="phase",
    )

    packet = alice.messages[-1].data
    assert packet["command"] == "play"
    assert packet["kind"] == "music"
    assert packet["loop"] is False
    assert packet["handle"] == "phase-music"
    assert not any(
        state.kind == "music" and state.handle == "phase-music"
        for state in game.active_audio.values()
    )


def test_stop_all_can_preserve_every_ambience_outro(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.play_music("music/round.ogg")
    game.play_ambience(
        "weather/rain.ogg",
        outro="weather/rain_outro.ogg",
        layer="weather",
    )
    alice.clear_messages()

    game.stop_all_audio(
        fade_ms=800,
        play_outros=True,
        outro_mode="immediate",
    )

    packet = alice.messages[-1].data
    assert packet["command"] == "stop_all"
    assert packet["fade_out_ms"] == 800
    assert packet["play_outros"] is True
    assert packet.get("outro_mode", "immediate") == "immediate"
    assert game.active_audio == {}


def test_network_audio_packets_are_unified_and_ordered() -> None:
    user = NetworkUser("Alice", "en", connection=object())
    handle = user.play_sound("fuse.ogg", loop=True, ducking={"music": 35})
    user.stop_sound(handle, fade_ms=250)
    user.play_music("music.ogg", pitch=125)
    user.pause_music()
    user.resume_music()
    user.stop_music()

    packets = user.get_queued_messages()
    assert {packet["type"] for packet in packets} == {"audio"}
    assert [packet["sequence"] for packet in packets] == list(
        range(1, len(packets) + 1)
    )
    assert packets[0]["handle"] == handle
    assert packets[0]["loop"] is True
    assert packets[0]["ducking"] == {"music": 35}
    assert packets[2]["pitch"] == 125
    assert [packet["command"] for packet in packets[2:]] == [
        "play",
        "pause",
        "resume",
        "stop",
    ]


def test_runtime_audio_ownership_tracks_replacements_and_teardown() -> None:
    user = MockUser("Alice")

    user.play_music("mainmus.ogg")
    assert user.has_managed_audio(
        "music",
        handle="music",
        asset="mainmus.ogg",
    )

    user.play_music(
        "game_pig/mus.ogg",
        handle="round:music",
    )
    assert not user.has_managed_audio(
        "music",
        handle="music",
        asset="mainmus.ogg",
    )
    assert user.has_managed_audio(
        "music",
        handle="round:music",
        asset="game_pig/mus.ogg",
    )

    user.stop_all_audio()
    assert not user.has_managed_audio(
        "music",
        handle="round:music",
        asset="game_pig/mus.ogg",
    )


def test_runtime_audio_ownership_keeps_independent_sfx_handles() -> None:
    user = MockUser("Alice")

    user.play_sound("engine.ogg", loop=True, handle="vehicle:engine")
    user.play_sound("radio.ogg", loop=True, handle="vehicle:radio")

    assert user.has_managed_audio("sfx", handle="vehicle:engine")
    assert user.has_managed_audio("sfx", handle="vehicle:radio")


def test_runtime_audio_ownership_treats_handles_as_client_global() -> None:
    user = MockUser("Alice")

    user.play_sound("engine.ogg", loop=True, handle="shared:source")
    user.play_music("music.ogg", handle="shared:source")

    assert not user.has_managed_audio("sfx", handle="shared:source")
    assert user.has_managed_audio(
        "music",
        handle="shared:source",
        asset="music.ogg",
    )

    user.stop_music(handle="shared:source")
    assert not user.has_managed_audio("music", handle="shared:source")


def test_runtime_audio_ownership_clears_every_ambience_layer() -> None:
    user = MockUser("Alice")

    user.play_music("music.ogg")
    user.play_ambience("rain.ogg", layer="weather")
    user.play_ambience("fire.ogg", layer="room")
    user.stop_all_ambience()

    assert user.has_managed_audio("music", handle="music")
    assert not user.has_managed_audio(
        "ambience",
        handle="ambience:global:default:weather",
    )
    assert not user.has_managed_audio(
        "ambience",
        handle="ambience:global:default:room",
    )


def test_game_start_stops_waiting_music_before_game_music(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    game.host = "Alice"
    game.play_music("test/waiting_music.ogg")
    alice.clear_messages()
    bob.clear_messages()

    game._start_game_from_lobby()

    for user in (alice, bob):
        stop_index = next(
            index
            for index, message in enumerate(user.messages)
            if message.type == "stop_music"
        )
        play_index = next(
            index
            for index, message in enumerate(user.messages)
            if (
                message.type == "play_music"
                and message.data.get("name") == "game_pig/mus.ogg"
            )
        )
        assert stop_index < play_index
    assert any(
        state.kind == "music" and state.asset == "game_pig/mus.ogg"
        for state in game.active_audio.values()
    )


def test_replayable_audio_teardown_preserves_unmanaged_one_shots(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    game.play_sound("test/victory.ogg")
    loop_handle = game.play_sound(
        "test/countdown.ogg",
        loop=True,
        handle="round:countdown",
        persist=True,
    )
    game.play_music("test/game_music.ogg")
    ambience_handle = game.play_ambience(
        "test/room_loop.ogg",
        outro="test/room_outro.ogg",
    )
    alice.clear_messages()
    bob.clear_messages()

    game.stop_replayable_audio(
        fade_ms=0,
        play_ambience_outros=True,
    )

    for user in (alice, bob):
        stops = [
            message.data
            for message in user.messages
            if message.type in {"audio", "stop_music", "stop_ambience"}
            and message.data.get("command") == "stop"
        ]
        assert {
            (packet.get("kind"), packet.get("handle"))
            for packet in stops
        } == {
            ("sfx", loop_handle),
            ("music", "music"),
            ("ambience", ambience_handle),
        }
        ambience_stop = next(
            packet
            for packet in stops
            if packet.get("kind") == "ambience"
        )
        assert ambience_stop.get("play_outro", True) is True
        assert not any(
            message.data.get("command") == "stop_all"
            for message in user.messages
        )
    assert game.active_audio == {}
    assert game.current_music == ""
    assert game.current_ambience == ""


def test_game_managed_effect_can_be_stopped_by_handle(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players

    handle = game.play_sound(
        "fuse.ogg",
        loop=True,
        handle="bomb:fuse",
        persist=True,
        priority=50,
    )
    assert handle == "bomb:fuse"
    assert "sfx:bomb:fuse" in game.active_audio
    assert alice.messages[-1].type == "audio"
    assert bob.messages[-1].data["handle"] == "bomb:fuse"

    game.stop_sound(handle, fade_ms=300)
    assert "sfx:bomb:fuse" not in game.active_audio
    assert alice.messages[-1].data["command"] == "stop"
    assert alice.messages[-1].data["fade_out_ms"] == 300


def test_replayable_handle_replacement_prunes_the_previous_layer(
    pig_game_with_players,
) -> None:
    game, _, _ = pig_game_with_players
    game.play_ambience(
        "forest/loop.ogg",
        handle="environment:shared",
        layer="forest",
    )
    game.play_ambience(
        "cave/loop.ogg",
        handle="environment:shared",
        layer="cave",
    )

    states = list(game.active_audio.values())
    assert len(states) == 1
    assert states[0].asset == "cave/loop.ogg"
    assert states[0].layer == "cave"


def test_private_layer_replacement_splits_state_and_public_takeover_unifies_it(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    bob_player = game.get_player_by_id(bob.uuid)
    assert alice_player is not None
    assert bob_player is not None
    game.play_ambience(
        "weather/rain.ogg",
        handle="weather:rain",
        audience=[alice_player, bob_player],
        scope="context",
        context="weather",
        layer="weather",
    )
    game.play_ambience(
        "weather/snow.ogg",
        handle="weather:snow",
        audience=alice_player,
        scope="context",
        context="weather",
        layer="weather",
    )

    states = sorted(game.active_audio.values(), key=lambda state: state.asset)
    assert [(state.asset, state.recipient_ids) for state in states] == [
        ("weather/rain.ogg", [bob.uuid]),
        ("weather/snow.ogg", [alice.uuid]),
    ]

    game.play_ambience(
        "weather/clear.ogg",
        handle="weather:clear",
        scope="context",
        context="weather",
        layer="weather",
    )
    state = next(iter(game.active_audio.values()))
    assert state.asset == "weather/clear.ogg"
    assert state.recipient_ids == []


def test_network_audio_sequence_is_one_ordered_websocket_packet() -> None:
    user = NetworkUser("Alice", "en", connection=object())

    user.play_sound_chain(
        [
            AudioSequenceSegment(asset="throw.ogg", position=(0, 1, 0)),
            AudioSequenceSegment(
                asset="flight.ogg",
                position=(0, 1, 0),
                destination_position=(0, 10, 0),
            ),
        ],
        handle="grenade:packet",
    )

    packets = user.get_queued_messages()
    assert len(packets) == 1
    assert packets[0]["type"] == "audio"
    assert packets[0]["sequence"] == 1
    assert packets[0]["handle"] == "grenade:packet"
    assert [segment["asset"] for segment in packets[0]["segments"]] == [
        "throw.ogg",
        "flight.ogg",
    ]


def test_managed_layer_pitch_is_configurable_and_replayable(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players

    game.play_music("music/slow.ogg", handle="slow-music", pitch=75)
    game.play_ambience(
        "weather/wind.ogg",
        intro="weather/wind-in.ogg",
        outro="weather/wind-out.ogg",
        handle="fast-wind",
        layer="weather",
        pitch=150,
    )

    packets = [message.data for message in alice.messages[-2:]]
    assert [packet["pitch"] for packet in packets] == [75, 150]
    states = {state.handle: state for state in game.active_audio.values()}
    assert states["slow-music"].pitch == 75
    assert states["fast-wind"].pitch == 150
    assert states["slow-music"].to_command(replay=True).pitch == 75
    assert states["fast-wind"].to_command(replay=True).pitch == 150

def test_private_layer_cannot_partially_replace_public_replay_state(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    assert alice_player is not None
    game.play_ambience("weather/rain.ogg", handle="weather:rain")
    alice.clear_messages()
    bob.clear_messages()

    with pytest.raises(ValueError, match="public handle or layer"):
        game.play_ambience(
            "weather/snow.ogg",
            handle="weather:snow",
            audience=alice_player,
        )

    assert alice.messages == []
    assert bob.messages == []
    state = next(iter(game.active_audio.values()))
    assert state.asset == "weather/rain.ogg"


def test_managed_source_motion_advances_at_server_ticks_and_replays(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    game.status = "playing"
    attenuation = DistanceAttenuation(
        model="linear",
        reference_distance=1,
        max_distance=11,
        rolloff_factor=1,
        min_gain=0,
        max_gain=1,
    )
    handle = game.play_sound(
        "engine.ogg",
        loop=True,
        handle="vehicle:engine",
        persist=True,
        position=(0, 1, 0),
        attenuation=attenuation,
    )
    alice.clear_messages()
    bob.clear_messages()

    game.move_sound(
        handle,
        (0, 11, 0),
        1000,
        easing="ease-in-out",
    )

    for user in (alice, bob):
        packet = user.messages[-1].data
        assert packet["command"] == "update"
        assert packet["handle"] == handle
        assert packet["motion"]["origin_position"] == [0.0, 1.0, 0.0]
        assert packet["motion"]["destination_position"] == [0.0, 11.0, 0.0]
    for _ in range(10):
        game.on_tick()
    state = next(iter(game.active_audio.values()))
    assert state.position == (0.0, 6.0, 0.0)
    assert state.motion is not None
    assert state.motion.elapsed_ms == 500

    restored = PigGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_alice = MockUser("Alice", uuid=alice.uuid)
    restored.attach_user(alice.uuid, restored_alice)
    replay_packets = [
        message.data
        for message in restored_alice.messages
        if "command" in message.data
    ]
    assert [packet["command"] for packet in replay_packets[-2:]] == [
        "play",
        "update",
    ]
    assert replay_packets[-2]["position"] == [0.0, 6.0, 0.0]
    assert replay_packets[-1]["motion"]["elapsed_ms"] == 500

    for _ in range(10):
        restored.on_tick()
    restored_state = next(iter(restored.active_audio.values()))
    assert restored_state.position == (0.0, 11.0, 0.0)
    assert restored_state.motion is None


def test_source_motion_rejects_unknown_unpositioned_and_partial_public_sources(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    assert alice_player is not None
    with pytest.raises(ValueError, match="Unknown replayable"):
        game.move_sound("missing", (1, 0, 0), 100)

    game.play_sound(
        "engine.ogg",
        loop=True,
        handle="unpositioned",
        persist=True,
    )
    with pytest.raises(ValueError, match="already-positioned"):
        game.move_sound("unpositioned", (1, 0, 0), 100)

    game.play_sound(
        "engine.ogg",
        loop=True,
        handle="public-engine",
        persist=True,
        position=(0, 1, 0),
    )
    with pytest.raises(ValueError, match="only part"):
        game.move_sound(
            "public-engine",
            (1, 0, 0),
            100,
            audience=alice_player,
        )


def test_source_motion_persists_current_fallback_pan(pig_game_with_players) -> None:
    game, _, _ = pig_game_with_players
    game.status = "playing"
    game.play_sound(
        "engine.ogg",
        loop=True,
        handle="moving-pan",
        persist=True,
        position=(0, 1, 0),
    )
    game.move_sound("moving-pan", (1, 0, 0), 1000)

    for _ in range(10):
        game.on_tick()

    state = next(iter(game.active_audio.values()))
    assert state.position == (0.5, 0.5, 0.0)
    assert state.pan == pan_from_position(state.position) == 71
    assert state.to_command(replay=True).pan == 71


def test_private_source_motion_splits_recipient_state(pig_game_with_players) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    bob_player = game.get_player_by_id(bob.uuid)
    assert alice_player is not None
    assert bob_player is not None
    game.play_sound(
        "engine.ogg",
        loop=True,
        handle="private-engine",
        persist=True,
        audience=[alice_player, bob_player],
        position=(0, 1, 0),
    )
    alice.clear_messages()
    bob.clear_messages()

    game.move_sound(
        "private-engine",
        (0, 11, 0),
        1000,
        audience=alice_player,
    )

    assert alice.messages[-1].data["command"] == "update"
    assert bob.messages == []
    states = sorted(game.active_audio.values(), key=lambda state: state.recipient_ids)
    alice_state = next(state for state in states if state.recipient_ids == [alice.uuid])
    bob_state = next(state for state in states if state.recipient_ids == [bob.uuid])
    assert alice_state.motion is not None
    assert bob_state.motion is None
    for _ in range(10):
        game.on_tick()
    assert alice_state.position == (0.0, 6.0, 0.0)
    assert bob_state.position == (0.0, 1.0, 0.0)


def test_source_position_and_gain_automate_concurrently_and_replay(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.status = "playing"
    game.play_ambience(
        "vehicle/engine.ogg",
        handle="vehicle:engine",
        position=(0, 1, 0),
        gain=0.2,
    )
    alice.clear_messages()

    game.update_audio_source(
        "ambience",
        "vehicle:engine",
        1000,
        destination=(0, 11, 0),
        gain=0.8,
        easing="linear",
    )

    packet = alice.messages[-1].data
    assert packet["command"] == "update"
    assert packet["motion"]["destination_position"] == [0.0, 11.0, 0.0]
    assert packet["gain_automation"]["destination_gain"] == 0.8
    for _ in range(10):
        game.on_tick()
    state = next(iter(game.active_audio.values()))
    assert state.position == (0.0, 6.0, 0.0)
    assert state.gain == pytest.approx(0.5)

    replay = state.replay_commands()
    assert replay[0].gain == pytest.approx(0.5)
    assert replay[1].motion is not None
    assert replay[1].gain_automation is not None
    assert replay[1].motion.elapsed_ms == 500
    assert replay[1].gain_automation.elapsed_ms == 500

    restored = PigGame.from_json(game.to_json())
    restored_state = next(iter(restored.active_audio.values()))
    assert restored_state.gain == pytest.approx(0.5)
    assert restored_state.gain_automation is not None
    assert restored_state.gain_automation.destination_gain == 0.8


def test_ambience_zone_blend_uses_normalized_constant_power_without_restart(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.play_ambience("forest/loop.ogg", handle="zone:forest", layer="forest")
    game.play_ambience(
        "cave/loop.ogg", handle="zone:cave", layer="cave", gain=0
    )
    alice.clear_messages()

    gains = game.blend_ambience_layers(
        {"zone:forest": 1, "zone:cave": 1},
        1000,
    )

    expected = 2 ** -0.5
    assert gains == pytest.approx({"zone:forest": expected, "zone:cave": expected})
    assert [message.data["command"] for message in alice.messages] == [
        "update",
        "update",
    ]
    assert all(
        message.data["gain_automation"]["destination_gain"]
        == pytest.approx(expected)
        for message in alice.messages
    )
    assert all(message.data.get("asset") is None for message in alice.messages)
    for _ in range(20):
        game.on_tick()
    assert {
        state.handle: state.gain for state in game.active_audio.values()
    } == pytest.approx({"zone:forest": expected, "zone:cave": expected})
    assert all(
        state.gain_automation is None for state in game.active_audio.values()
    )


def test_ambience_zone_blend_is_all_or_nothing(pig_game_with_players) -> None:
    game, alice, _ = pig_game_with_players
    game.play_ambience("forest/loop.ogg", handle="zone:forest", layer="forest")
    alice.clear_messages()

    with pytest.raises(ValueError, match="Unknown replayable"):
        game.blend_ambience_layers(
            {"zone:forest": 1, "zone:missing": 1},
            1000,
        )

    assert alice.messages == []
    state = next(iter(game.active_audio.values()))
    assert state.gain == 1
    assert state.gain_automation is None


@pytest.mark.parametrize(
    "weights",
    [
        {},
        {"forest": 0, "cave": 0},
        {"forest": -1, "cave": 2},
        {"forest": float("nan")},
        {"forest": 1e308, "cave": 1e308},
    ],
)
def test_ambience_zone_blend_rejects_invalid_weights(weights) -> None:
    with pytest.raises(ValueError):
        PigGame.ambience_mix_gains(weights)


def test_private_and_contextual_ambience_isolated_and_serialized(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    assert alice_player is not None
    alice.clear_messages()
    bob.clear_messages()

    handle = game.play_private_ambience(
        alice_player,
        "forest/night.ogg",
        intro="forest/enter.ogg",
        layer="weather",
        position=(6, 0, 0),
        attenuation=DistanceAttenuation(
            model="exponential",
            reference_distance=2,
            max_distance=10,
            rolloff_factor=2,
            min_gain=0.05,
            max_gain=1,
        ),
    )

    assert handle.startswith("ambience:player:")
    assert [message.type for message in alice.messages] == ["audio"]
    assert bob.messages == []
    state = next(iter(game.active_audio.values()))
    assert state.scope == "player"
    assert state.recipient_ids == [alice.uuid]

    restored = PigGame.from_json(game.to_json())
    restored_alice = MockUser("Alice", uuid=alice.uuid)
    restored_bob = MockUser("Bob", uuid=bob.uuid)
    restored.attach_user(alice.uuid, restored_alice)
    restored.attach_user(bob.uuid, restored_bob)
    assert restored_alice.messages[-1].data["asset"] == "forest/night.ogg"
    assert restored_alice.messages[-1].data["play_intro"] is False
    assert restored_alice.messages[-1].data.get("fade_in_ms", 0) == 0
    assert restored_alice.messages[-1].data["position"] == [6.0, 0.0, 0.0]
    assert restored_alice.messages[-1].data["attenuation"]["model"] == "exponential"
    assert restored_bob.messages == []


def test_disconnected_private_audio_keeps_its_recipient_scope(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    assert alice_player is not None
    game._users.pop(alice.uuid)

    game.play_private_ambience(alice_player, "forest/night.ogg")

    state = next(iter(game.active_audio.values()))
    assert state.recipient_ids == [alice.uuid]
    bob.clear_messages()
    game.attach_user(bob.uuid, bob)
    assert bob.messages == []
    game.attach_user(alice.uuid, alice)
    assert alice.messages[-1].data["asset"] == "forest/night.ogg"


def test_music_pause_state_survives_serialization(pig_game_with_players) -> None:
    game, alice, _ = pig_game_with_players
    game.play_music("music/round.ogg", handle="round_music")
    game.pause_music(handle="round_music", fade_ms=450)

    state = next(
        state for state in game.active_audio.values() if state.kind == "music"
    )
    assert state.paused is True
    assert state.recipient_ids == []
    restored = PigGame.from_json(game.to_json())
    restored_state = next(
        state for state in restored.active_audio.values() if state.kind == "music"
    )
    assert restored_state.paused is True
    assert alice.messages[-1].data["command"] == "pause"


def test_waiting_restore_discards_legacy_and_unified_audio_state(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.status = "waiting"
    game.play_music("legacy/waiting_music.ogg")
    game.play_ambience("test/waiting_room.ogg")

    restored = PigGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_user = MockUser("Alice", uuid=alice.uuid)
    restored.attach_user(alice.uuid, restored_user)

    assert restored.active_audio == {}
    assert restored.current_music == ""
    assert restored.current_ambience == ""
    assert restored.current_ambience_outro == ""
    assert not any(
        message.type in {"play_music", "play_ambience", "audio"}
        for message in restored_user.messages
    )


def test_playing_restore_migrates_legacy_tracks_once(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    game.status = "playing"
    game.active_audio.clear()
    game.current_music = "legacy/round_music.ogg"
    game.current_ambience = "legacy/room_loop.ogg"
    game.current_ambience_outro = "legacy/room_outro.ogg"

    restored = PigGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.current_music == ""
    assert restored.current_ambience == ""
    assert restored.current_ambience_outro == ""
    states = list(restored.active_audio.values())
    assert {
        (state.kind, state.asset, state.outro)
        for state in states
    } == {
        ("music", "legacy/round_music.ogg", ""),
        (
            "ambience",
            "legacy/room_loop.ogg",
            "legacy/room_outro.ogg",
        ),
    }

    restored_user = MockUser("Alice", uuid=alice.uuid)
    restored.attach_user(alice.uuid, restored_user)
    replayed_assets = {
        message.data.get("asset")
        for message in restored_user.messages
        if message.data.get("command") == "play"
    }
    assert replayed_assets == {
        "legacy/round_music.ogg",
        "legacy/room_loop.ogg",
    }


def test_private_managed_effect_stop_preserves_other_audiences(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    bob_player = game.get_player_by_id(bob.uuid)
    assert alice_player is not None
    assert bob_player is not None

    game.play_sound(
        "machine.ogg",
        loop=True,
        handle="machine",
        persist=True,
        audience=(alice_player, bob_player),
        scope="context",
        context="duo",
    )

    game.stop_sound("machine", audience=alice_player)

    remaining = list(game.active_audio.values())
    assert len(remaining) == 1
    assert remaining[0].recipient_ids == [bob.uuid]


def test_private_music_pause_splits_multi_recipient_replay_state(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    bob_player = game.get_player_by_id(bob.uuid)
    assert alice_player is not None
    assert bob_player is not None
    game.play_music(
        "music/duo.ogg",
        handle="duo-music",
        audience=(alice_player, bob_player),
        scope="context",
        context="duo",
    )

    game.pause_music(handle="duo-music", audience=alice_player)

    states = list(game.active_audio.values())
    assert len(states) == 2
    alice_state = next(state for state in states if alice.uuid in state.recipient_ids)
    bob_state = next(state for state in states if bob.uuid in state.recipient_ids)
    assert alice_state.recipient_ids == [alice.uuid]
    assert alice_state.paused is True
    assert bob_state.recipient_ids == [bob.uuid]
    assert bob_state.paused is False


def test_private_ambience_stop_preserves_other_audiences(
    pig_game_with_players,
) -> None:
    game, alice, bob = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    bob_player = game.get_player_by_id(bob.uuid)
    assert alice_player is not None
    assert bob_player is not None

    game.play_ambience(
        "alice/rain.ogg",
        handle="alice-weather",
        layer="weather",
        audience=alice_player,
    )
    game.play_ambience(
        "bob/wind.ogg",
        handle="bob-weather",
        layer="weather",
        audience=bob_player,
    )

    game.stop_ambience(layer="weather", audience=alice_player)

    remaining = [
        state for state in game.active_audio.values()
        if state.kind == "ambience"
    ]
    assert len(remaining) == 1
    assert remaining[0].asset == "bob/wind.ogg"
    assert remaining[0].recipient_ids == [bob.uuid]


def test_ducking_is_available_but_default_commands_are_dormant(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players

    game.play_music("music/default.ogg")
    assert "ducking" not in alice.messages[-1].data

    game.play_music(
        "music/opt-in.ogg",
        handle="opt-in-music",
        layer="opt-in",
        ducking={"ambience": 40},
    )
    assert alice.messages[-1].data["ducking"] == {"ambience": 40}


def test_departed_player_private_audio_is_pruned(
    pig_game_with_players,
) -> None:
    game, alice, _ = pig_game_with_players
    alice_player = game.get_player_by_id(alice.uuid)
    assert alice_player is not None
    game.play_private_ambience(alice_player, "private/rain.ogg")

    game.remove_player(alice.uuid)

    assert not [
        state for state in game.active_audio.values()
        if alice.uuid in state.recipient_ids
    ]
