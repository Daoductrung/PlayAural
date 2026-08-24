"""Unified audio protocol, routing, and persistence coverage."""

import asyncio
from pathlib import Path

import pytest

from ..audio import (
    AUDIO_PROTOCOL_VERSION,
    AudioCommand,
    AudioPlaybackState,
    SameTurnAudioBatcher,
)
from ..games.pig.game import PigGame
from ..users.network_user import NetworkUser
from ..users.test_user import MockUser


ROOT = Path(__file__).resolve().parents[2]


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


def test_audio_command_serializes_validated_one_shot_sound_family() -> None:
    packet = AudioCommand(
        command="play",
        kind="sfx",
        family="notifications/notify",
    ).to_packet()

    assert packet["family"] == "notifications/notify"
    assert "asset" not in packet


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
    user.play_music("music.ogg")
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
