"""Rules, accessibility, persistence, and bot tests for Dead Man's Dice."""

import hashlib
import random
import re
import struct
from pathlib import Path
from unittest.mock import patch

import pytest

from ..game_utils.audio_duration import measure_audio_duration_ticks
from ..games.deadmansdice import audio as dice_audio
from ..games.deadmansdice.bot import (
    BotObservation,
    bid_exact_probability,
    bid_truth_probability,
    choose_decision,
    is_legal_bid,
    perceived_truth_probability,
)
from ..games.deadmansdice.game import (
    BOT_THINK_TICKS,
    DICE_PER_PLAYER,
    DIE_SIDES,
    MAX_POISON_DOSES,
    RESULT_LIAR_BIDDER_LOST,
    RESULT_SPOT_CORRECT,
    RULESET_BASIC,
    RULESET_TRADITIONAL,
    SEQUENCE_CHALLENGE,
    SEQUENCE_OPENING,
    DeadMansDiceGame,
    DeadMansDiceOptions,
    DeadMansDicePlayer,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 2,
    ruleset: str = RULESET_TRADITIONAL,
    start: bool = True,
    bot_indexes: set[int] | None = None,
    touch_indexes: set[int] | None = None,
    finish_opening: bool = True,
) -> DeadMansDiceGame:
    game = DeadMansDiceGame(options=DeadMansDiceOptions(ruleset=ruleset))
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_indexes and index in bot_indexes:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if touch_indexes and index in touch_indexes:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    game.setup_keybinds()
    if start:
        with patch(
            "server.games.deadmansdice.game.random.shuffle", lambda values: None
        ):
            game.on_start()
        if finish_opening:
            finish_active_sequences(game)
    return game


def set_dice(game: DeadMansDiceGame, *rolls: list[int]) -> None:
    for player, dice in zip(game.alive_players, rolls, strict=True):
        player.dice = list(dice)


def place_bid(
    game: DeadMansDiceGame,
    player: DeadMansDicePlayer,
    quantity: int,
    face: int,
) -> None:
    game.execute_action(player, f"bid_face_{face}", input_value=str(quantity))


def spoken(user: MockUser) -> list[str]:
    return user.get_spoken_messages()


def audio_packets(user: MockUser, *, kind: str | None = None) -> list[dict]:
    packets = [
        message.data
        for message in user.messages
        if message.data.get("type") == "audio" and message.data.get("command") == "play"
    ]
    if kind is None:
        return packets
    return [packet for packet in packets if packet.get("kind") == kind]


def finish_active_sequences(game: DeadMansDiceGame) -> None:
    for _ in range(1000):
        if not game.active_sequences:
            return
        game.on_tick()
    raise AssertionError("Dead Man's Dice sequence did not finish")


def test_registration_metadata_and_defaults() -> None:
    assert GameRegistry.get("deadmansdice") is DeadMansDiceGame
    assert DeadMansDiceGame.get_name() == "Dead Man's Dice"
    assert DeadMansDiceGame.get_category() == "dice"
    assert DeadMansDiceGame.get_min_players() == 2
    assert DeadMansDiceGame.get_max_players() == 4
    assert DeadMansDiceGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]
    assert DeadMansDiceGame().options.ruleset == RULESET_TRADITIONAL


def test_opening_establishes_the_room_for_five_seconds_before_the_first_roll() -> None:
    game = make_game(finish_opening=False)
    first = game.players[0]
    user = game.get_user(first)
    assert isinstance(user, MockUser)

    opening = game._get_sequence(SEQUENCE_OPENING)
    assert opening is not None
    assert game.round == 0
    assert game.current_player is None
    assert all(not player.dice for player in game.alive_players)
    assert "Only one of you will leave standing." in spoken(user)[-1]
    assert game._is_mutating_turn_enabled(first) == "deadmansdice-action-opening"
    assert game._is_read_dice_enabled(first) == "deadmansdice-action-opening-no-dice"
    assert (
        game._is_bid_history_enabled(first)
        == "deadmansdice-action-opening-no-bids"
    )
    opening_table = " ".join(
        item.text for item in game._build_table_status(first, user)
    )
    assert "2 players wait with 10 dice still unrolled." in opening_table
    assert "No turn is active yet." in opening_table

    ambience = audio_packets(user, kind="ambience")
    music = audio_packets(user, kind="music")
    assert ambience and all(
        packet["fade_in_ms"] == dice_audio.AMBIENCE_FADE_IN_MS
        for packet in ambience
    )
    assert music[0]["fade_in_ms"] == dice_audio.MUSIC_FADE_IN_MS
    assert dice_audio.AMBIENCE_FADE_IN_MS == 5000
    assert dice_audio.MUSIC_FADE_IN_MS == 5000

    for _ in range(dice_audio.OPENING_SETUP_DELAY_TICKS - 1):
        game.on_tick()
    assert game.round == 0
    assert not any("Rules: Traditional" in line for line in spoken(user))

    game.on_tick()
    assert any("Rules: Traditional" in line for line in spoken(user))
    assert any("Ones are wild" in line for line in spoken(user))
    assert game.round == 0

    for _ in range(dice_audio.OPENING_ROLL_DELAY_TICKS - 1):
        game.on_tick()
    assert game.round == 0
    assert all(not player.dice for player in game.alive_players)

    game.on_tick()
    assert game.round == 1
    assert all(len(player.dice) == DICE_PER_PLAYER for player in game.alive_players)
    assert game._get_sequence(SEQUENCE_OPENING) is None


def test_reconnecting_during_opening_recovers_missed_narrative_and_setup() -> None:
    game = make_game(finish_opening=False)
    for _ in range(dice_audio.OPENING_SETUP_DELAY_TICKS):
        game.on_tick()

    player = game.players[0]
    replacement = MockUser(player.name, uuid=player.id)
    game.attach_user(player.id, replacement, session_handover=True)

    lines = spoken(replacement)
    assert any("Only one of you will leave standing." in line for line in lines)
    assert any("Rules: Traditional" in line for line in lines)
    assert any("Ones are wild" in line for line in lines)


def test_basic_opening_explains_literal_faces_without_wild_ones() -> None:
    game = make_game(ruleset=RULESET_BASIC, finish_opening=False)
    user = game.get_user(game.players[0])
    assert isinstance(user, MockUser)

    for _ in range(dice_audio.OPENING_SETUP_DELAY_TICKS):
        game.on_tick()

    setup = next(line for line in spoken(user) if "Rules: Basic" in line)
    assert "Every face counts only itself, including ones." in setup
    assert "wild" not in setup


def test_opening_sequence_survives_save_and_restore_without_restarting() -> None:
    game = make_game(finish_opening=False)
    elapsed = 30
    for _ in range(elapsed):
        game.on_tick()

    restored = DeadMansDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    opening = restored._get_sequence(SEQUENCE_OPENING)
    assert opening is not None
    assert opening.current_index == 1
    assert restored.round == 0

    for _ in range(dice_audio.OPENING_DURATION_TICKS - elapsed - 1):
        restored.on_tick()
    assert restored.round == 0

    restored.on_tick()
    assert restored.round == 1
    assert restored._get_sequence(SEQUENCE_OPENING) is None


@pytest.mark.parametrize(
    ("quantity", "face", "current_quantity", "current_face", "expected"),
    [
        (1, 1, 0, 0, True),
        (4, 6, 4, 5, True),
        (5, 1, 4, 5, True),
        (4, 4, 4, 5, False),
        (3, 6, 4, 5, False),
        (21, 1, 0, 0, False),
        (0, 6, 0, 0, False),
        (1, 7, 0, 0, False),
    ],
)
def test_bid_ladder(
    quantity: int,
    face: int,
    current_quantity: int,
    current_face: int,
    expected: bool,
) -> None:
    assert is_legal_bid(quantity, face, current_quantity, current_face, 20) is expected


def test_start_rolls_five_private_dice_and_announces_public_total() -> None:
    rolls = [[1, 2, 3, 4, 5], [6, 6, 5, 4, 3]]
    with patch("server.games.deadmansdice.game.roll_dice", side_effect=rolls):
        game = make_game()

    first_user = game.get_user(game.players[0])
    second_user = game.get_user(game.players[1])
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    assert game.round == 1
    assert game.current_player is game.players[0]
    assert game.players[0].dice == rolls[0]
    assert game.players[1].dice == rolls[1]
    assert any("Your dice: 1, 2, 3, 4, and 5." == line for line in spoken(first_user))
    assert not any("6, 6, 5, 4, and 3" in line for line in spoken(first_user))
    assert any(
        "2 survivors seal 10 dice beneath their cups" in line
        for line in spoken(first_user)
    )


def test_sound_assets_are_complete_identical_ogg_files_in_every_client() -> None:
    repository = Path(__file__).resolve().parents[2]
    pack_roots = (
        repository / "client" / "sounds",
        repository / "web_client" / "sounds",
        repository / "mobile_client" / "sounds",
    )

    for asset in dice_audio.ALL_SOUND_ASSETS:
        copies = [root / Path(asset) for root in pack_roots]
        assert all(copy.is_file() for copy in copies)
        contents = [copy.read_bytes() for copy in copies]
        assert all(content.startswith(b"OggS") for content in contents)
        assert len({hashlib.sha256(content).digest() for content in contents}) == 1
        if asset.startswith("game_deadmansdice/"):
            identification = contents[0].find(b"\x01vorbis")
            assert identification >= 0
            assert contents[0][identification + 11] == 1
            assert struct.unpack_from("<I", contents[0], identification + 12)[0] == 48000


def test_cinematic_timing_constants_match_the_shipped_audio() -> None:
    sound_root = Path(__file__).resolve().parents[2] / "client" / "sounds"

    def ticks(asset: str) -> int:
        measured = measure_audio_duration_ticks(
            sound_root / asset,
            ticks_per_second=20,
        )
        assert measured is not None
        return measured

    for asset, fallback_ticks in dice_audio.AUDIO_DURATIONS_TICKS.items():
        assert ticks(asset) == fallback_ticks
        assert dice_audio.sound_ticks(asset) == fallback_ticks


def test_sound_timing_rechecks_asset_metadata_after_replacement() -> None:
    with patch.object(
        dice_audio,
        "measure_audio_duration_ticks",
        side_effect=[5, 7],
    ) as measure:
        assert dice_audio.sound_ticks("game_deadmansdice/timing_probe.ogg") == 5
        assert dice_audio.sound_ticks("game_deadmansdice/timing_probe.ogg") == 7

    assert measure.call_count == 2


def test_room_position_transform_keeps_spectator_at_table_centre() -> None:
    source = (8.0, 6.0, 2.0)

    assert dice_audio.listener_relative_room_position(source, None, 4) == source
    # Seat 0 is north of the table and faces south: world east is on the
    # listener's left, and a source farther north is behind them.
    assert dice_audio.listener_relative_room_position(source, 0, 4) == (
        -8.0,
        -4.0,
        2.0,
    )
    # Seat 1 is east of the table and faces west: the same source is behind.
    assert dice_audio.listener_relative_room_position(source, 1, 4) == (
        6.0,
        -6.0,
        2.0,
    )

    west = (-8.0, 0.0, 1.0)
    # Seat 0 faces south, so west is on the right. The opposite seat faces
    # north and therefore hears that same room-fixed source on the left.
    assert dice_audio.listener_relative_room_position(west, 0, 2) == (
        8.0,
        2.0,
        1.0,
    )
    assert dice_audio.listener_relative_room_position(west, 1, 2) == (
        -8.0,
        2.0,
        1.0,
    )


def test_start_builds_private_room_mix_and_atomic_seat_rolls() -> None:
    game = make_game(player_count=4)
    listener = game.players[0]
    user = game.get_user(listener)
    assert isinstance(user, MockUser)

    ambience = audio_packets(user, kind="ambience")
    assert len(ambience) == len(dice_audio.AMBIENCE_SOURCES)
    assert {packet["layer"] for packet in ambience} == {
        source.layer for source in dice_audio.AMBIENCE_SOURCES
    }
    assert all(packet["scope"] == "player" for packet in ambience)
    assert all(packet["context"] == listener.id for packet in ambience)
    assert all(packet["attenuation"]["model"] == "inverse" for packet in ambience)
    assert {packet["layer"]: packet["gain"] for packet in ambience} == {
        source.layer: source.gain for source in dice_audio.AMBIENCE_SOURCES
    }
    assert [source.gain for source in dice_audio.AMBIENCE_SOURCES] == [
        0.68,
        0.54,
        0.8,
        0.56,
        0.4,
    ]

    music = audio_packets(user, kind="music")
    assert len(music) == 1
    assert music[0]["asset"] == dice_audio.SOUND_MUSIC
    assert music[0]["gain"] == dice_audio.MUSIC_GAIN

    roll = next(
        packet
        for packet in audio_packets(user, kind="sfx")
        if packet.get("segments")
        and all(
            segment["asset"] in dice_audio.SOUND_DICE_SHAKES
            for segment in packet["segments"]
        )
    )
    assert roll["buffer"] == "game"
    assert len(roll["segments"]) == 4
    assert roll["segments"][0].get("position") is None
    assert roll["segments"][1]["position"] == [-2.0, 0.0, 0.0]
    assert roll["segments"][2]["position"] == [0.0, 2.0, 0.0]
    assert roll["segments"][3]["position"] == [2.0, 0.0, 0.0]
    assert all(segment["next_start_ratio"] == 0.0 for segment in roll["segments"])
    assert len({segment["asset"] for segment in roll["segments"]}) == 4
    assert all(
        segment["gain"] == dice_audio.DICE_SHAKE_GAIN
        for segment in roll["segments"]
    )


def test_spectator_hears_room_and_seats_from_table_centre() -> None:
    game = make_game(start=False)
    spectator_user = MockUser("Watcher", uuid="watcher")
    spectator = game.add_spectator("Watcher", spectator_user)
    with patch("server.games.deadmansdice.game.random.shuffle", lambda values: None):
        game.on_start()
    finish_active_sequences(game)

    ambience = audio_packets(spectator_user, kind="ambience")
    by_layer = {packet["layer"]: packet for packet in ambience}
    for source in dice_audio.AMBIENCE_SOURCES:
        assert by_layer[source.layer]["position"] == list(source.world_position)

    roll = next(
        packet
        for packet in audio_packets(spectator_user, kind="sfx")
        if packet.get("segments")
        and all(
            segment["asset"] in dice_audio.SOUND_DICE_SHAKES
            for segment in packet["segments"]
        )
    )
    assert [segment["position"] for segment in roll["segments"]] == [
        [0.0, 2.0, 0.0],
        [0.0, -2.0, 0.0],
    ]
    assert spectator.is_spectator


def test_reconnect_replays_ambience_without_duplicating_persistent_state() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    state_count = len(game.active_audio)
    user.clear_messages()

    game.attach_user(player.id, user, session_handover=True)

    assert len(game.active_audio) == state_count
    assert len(audio_packets(user, kind="ambience")) == len(dice_audio.AMBIENCE_SOURCES)


def test_ambient_bar_detail_uses_one_room_fixed_source_for_every_listener() -> None:
    game = make_game()
    north_listener, south_listener = game.players
    north_user = game.get_user(north_listener)
    south_user = game.get_user(south_listener)
    assert isinstance(north_user, MockUser)
    assert isinstance(south_user, MockUser)
    north_user.clear_messages()
    south_user.clear_messages()

    game._play_room_one_shot(
        dice_audio.SOUND_AMBIENT_EVENTS[0],
        (-8.0, 0.0, 1.0),
    )

    north_packet = audio_packets(north_user, kind="sfx")[0]
    south_packet = audio_packets(south_user, kind="sfx")[0]
    assert north_packet["segments"][0]["position"] == [8.0, 2.0, 1.0]
    assert south_packet["segments"][0]["position"] == [-8.0, 2.0, 1.0]
    assert north_packet["segments"][0]["attenuation"]["model"] == "inverse"


def test_due_ambient_bar_event_plays_once_and_reschedules() -> None:
    game = make_game()
    listener = game.players[0]
    user = game.get_user(listener)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game.next_ambient_event_tick = game.sound_scheduler_tick

    with (
        patch(
            "server.games.deadmansdice.game.random.choice",
            side_effect=[
                dice_audio.SOUND_AMBIENT_EVENTS[0],
                dice_audio.AMBIENT_EVENT_WORLD_POSITIONS[0],
            ],
        ),
        patch(
            "server.games.deadmansdice.game.random.randint",
            return_value=dice_audio.AMBIENT_EVENT_INTERVAL_TICKS[0],
        ),
    ):
        game._maybe_play_ambient_event()

    event = audio_packets(user, kind="sfx")[0]
    assert event["segments"][0]["asset"] == dice_audio.SOUND_AMBIENT_EVENTS[0]
    assert game.next_ambient_event_tick == (
        game.sound_scheduler_tick + dice_audio.AMBIENT_EVENT_INTERVAL_TICKS[0]
    )


def test_due_ambient_bar_event_defers_during_a_challenge_sequence() -> None:
    game = make_game()
    bidder, challenger = game.players
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, bidder, 4, 5)
    listener = game.get_user(bidder)
    assert isinstance(listener, MockUser)
    game.execute_action(challenger, "call_liar")
    listener.clear_messages()
    game.next_ambient_event_tick = game.sound_scheduler_tick

    game._maybe_play_ambient_event()

    assert not any(
        segment["asset"] in dice_audio.SOUND_AMBIENT_EVENTS
        for packet in audio_packets(listener, kind="sfx")
        for segment in packet.get("segments", [])
    )
    assert game.next_ambient_event_tick == (
        game.sound_scheduler_tick + dice_audio.AMBIENT_EVENT_DEFER_TICKS
    )


def test_bid_sound_is_local_to_actor_seat_and_game_buffer() -> None:
    game = make_game()
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    place_bid(game, actor, 2, 4)

    actor_tap = next(
        packet
        for packet in audio_packets(actor_user, kind="sfx")
        if packet["segments"][0]["asset"] in dice_audio.SOUND_BID_TAPS
    )
    observer_tap = next(
        packet
        for packet in audio_packets(observer_user, kind="sfx")
        if packet["segments"][0]["asset"] in dice_audio.SOUND_BID_TAPS
    )
    assert actor_tap["buffer"] == "game"
    assert actor_tap["segments"][0].get("position") is None
    assert actor_tap["segments"][0]["gain"] == dice_audio.BID_TAP_GAIN
    assert observer_tap["segments"][0]["position"] == [0.0, 2.0, 0.0]


def test_challenge_audio_paces_reveal_poison_and_next_round() -> None:
    game = make_game()
    bidder, challenger = game.players
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, bidder, 4, 5)

    game.execute_action(challenger, "call_liar")

    assert game.is_sequence_gameplay_locked()
    assert game.last_reveal == []
    assert bidder.poison_doses == 0
    assert (
        game._is_call_liar_enabled(challenger) == "deadmansdice-action-sequence-running"
    )
    sequence = game._get_sequence(SEQUENCE_CHALLENGE)
    assert sequence is not None
    assert sequence.next_tick > game.sound_scheduler_tick

    finish_active_sequences(game)

    assert game.last_reveal_result == RESULT_LIAR_BIDDER_LOST
    assert bidder.poison_doses == 1
    assert game.round == 2
    assert not game.is_sequence_gameplay_locked()


def test_challenge_reveals_each_cup_and_announces_each_player_separately() -> None:
    game = make_game(player_count=3)
    bidder, challenger, _third = game.players
    set_dice(
        game,
        [2, 2, 3, 3, 4],
        [2, 4, 5, 6, 6],
        [3, 3, 4, 4, 6],
    )
    place_bid(game, bidder, 5, 5)
    listener = game.get_user(bidder)
    assert isinstance(listener, MockUser)
    listener.clear_messages()

    game.execute_action(challenger, "call_liar")
    finish_active_sequences(game)

    cup_packets = [
        packet
        for packet in audio_packets(listener, kind="sfx")
        if packet.get("segments")
        and packet["segments"][0]["asset"] == dice_audio.SOUND_CUP_REVEAL
    ]
    assert len(cup_packets) == 3
    assert all(len(packet["segments"]) == 1 for packet in cup_packets)
    assert all(
        packet["segments"][0]["gain"] == dice_audio.CUP_REVEAL_GAIN
        for packet in cup_packets
    )

    lines = spoken(listener)
    own = lines.index("Your cup lifts: 2, 2, 3, 3, and 4.")
    second = lines.index("Player2's cup lifts: 2, 4, 5, 6, and 6.")
    last = lines.index("Player3's cup lifts: 3, 3, 4, 4, and 6.")
    total = next(
        index for index, line in enumerate(lines) if line.startswith("The cups hold")
    )
    assert own < second < last < total


def test_lethal_poison_plays_drink_choke_and_headfall_before_next_round() -> None:
    game = make_game()
    loser, challenger = game.players
    loser.poison_doses = MAX_POISON_DOSES - 1
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, loser, 4, 5)
    listener = game.get_user(challenger)
    assert isinstance(listener, MockUser)
    listener.clear_messages()

    game.execute_action(challenger, "call_liar")
    sequence = game._get_sequence(SEQUENCE_CHALLENGE)
    assert sequence is not None
    poison_asset = sequence.metadata["poison_assets"][loser.id]
    expected_audio_ticks = dice_audio.finite_sequence_duration_ticks(
        [
            (poison_asset, 1.0),
            (
                dice_audio.SOUND_DEATH_CHOKE,
                dice_audio.DEATH_CHOKE_TO_FALL_RATIO,
            ),
            (dice_audio.SOUND_DEATH_HEADFALL, 1.0),
        ]
    )
    poison_beat = next(
        beat
        for beat in sequence.beats
        if any(operation.callback_id == "resolve_poison" for operation in beat.ops)
    )
    assert poison_beat.delay_after_ticks == (
        expected_audio_ticks + dice_audio.POST_POISON_PAUSE_TICKS
    )
    finish_active_sequences(game)

    death_packet = next(
        packet
        for packet in audio_packets(listener, kind="sfx")
        if any(
            segment["asset"] == dice_audio.SOUND_DEATH_CHOKE
            for segment in packet["segments"]
        )
    )
    assets = [segment["asset"] for segment in death_packet["segments"]]
    assert assets[0] in dice_audio.SOUND_POISON_DRINKS
    assert assets[1:] == [
        dice_audio.SOUND_DEATH_CHOKE,
        dice_audio.SOUND_DEATH_HEADFALL,
    ]
    assert [segment["gain"] for segment in death_packet["segments"]] == [
        dice_audio.POISON_DRINK_GAIN,
        dice_audio.DEATH_CHOKE_GAIN,
        dice_audio.DEATH_HEADFALL_GAIN,
    ]
    assert death_packet["segments"][1]["next_start_ratio"] == (
        dice_audio.DEATH_CHOKE_TO_FALL_RATIO
    )
    assert loser.eliminated
    assert game.status == "finished"
    lines = spoken(listener)
    poison_line = next(
        index for index, line in enumerate(lines) if "swallows the poison" in line
    )
    death_line = next(
        index for index, line in enumerate(lines) if "is out" in line
    )
    assert poison_line < death_line


def test_bot_cadence_is_deliberate_and_serialized_on_the_player() -> None:
    assert BOT_THINK_TICKS == (32, 64)
    game = make_game(bot_indexes={0, 1})
    current = game.current_player
    assert isinstance(current, DeadMansDicePlayer)
    assert current.is_bot

    with patch("server.games.deadmansdice.game.random.randint", return_value=64):
        game._jolt_current_bot()

    assert current.bot_think_ticks == 64


def test_pending_challenge_sequence_survives_save_and_restore() -> None:
    game = make_game()
    bidder, challenger = game.players
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, bidder, 4, 5)
    game.execute_action(challenger, "call_liar")

    restored = DeadMansDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    for player in restored.players:
        restored.attach_user(
            player.id,
            MockUser(player.name, uuid=player.id),
        )

    assert restored.is_sequence_gameplay_locked()
    assert restored.last_reveal == []
    finish_active_sequences(restored)

    restored_bidder = restored.get_player_by_id(bidder.id)
    assert isinstance(restored_bidder, DeadMansDicePlayer)
    assert restored_bidder.poison_doses == 1
    assert restored.last_reveal_result == RESULT_LIAR_BIDDER_LOST
    assert restored.round == 2


def test_finishing_match_retires_ambience_but_keeps_one_shot_win_cue() -> None:
    game = make_game()
    winner, loser = game.players
    loser.eliminated = True
    loser.dice.clear()
    winner_user = game.get_user(winner)
    assert isinstance(winner_user, MockUser)
    winner_user.clear_messages()

    game._finish_match()

    assert game.status == "finished"
    assert not game.active_audio
    assert any(
        packet.get("segments", [{}])[0].get("asset") == dice_audio.SOUND_WIN
        for packet in audio_packets(winner_user, kind="sfx")
    )


def test_bid_selector_contains_only_legal_quantities_for_chosen_face() -> None:
    game = make_game()
    current = game.players[0]
    game.current_bid_quantity = 4
    game.current_bid_face = 5
    game.current_bidder_id = game.players[1].id

    game.execute_action(current, "bid_face_6")
    assert game._pending_actions[current.id] == "bid_face_6"
    assert game._bid_quantity_options(current)[0] == "4"

    game._discard_pending_action_input(current)
    game.execute_action(current, "bid_face_4")
    assert game._bid_quantity_options(current)[0] == "5"


def test_bid_announces_perspectives_and_advances_turn() -> None:
    game = make_game()
    actor = game.players[0]
    observer = game.players[1]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    place_bid(game, actor, 3, 4)

    assert game.current_bid_quantity == 3
    assert game.current_bid_face == 4
    assert game.current_bidder_id == actor.id
    assert game.current_player is observer
    assert actor.bids_made == 1
    assert spoken(actor_user)[0] == "You bid 3 fours."
    assert spoken(observer_user)[0] == "Player1 bids 3 fours."


def test_single_die_bid_uses_singular_face_names_everywhere() -> None:
    game = make_game()
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    assert game._bid_quantity_label(actor, "1") == "1 one"
    place_bid(game, actor, 1, 5)

    assert spoken(actor_user)[0] == "You bid 1 five."
    assert spoken(observer_user)[0] == "Player1 bids 1 five."
    visible = {
        action.action.id: action for action in game.get_all_visible_actions(observer)
    }
    assert visible["call_liar"].label == "Call liar — 1 five"
    assert "bid of 1 five" in visible["call_liar"].description


def test_stale_or_invalid_bid_is_rejected_without_mutation() -> None:
    game = make_game()
    actor = game.players[0]
    place_bid(game, actor, 4, 5)
    current = game.current_player
    assert isinstance(current, DeadMansDicePlayer)

    game.execute_action(current, "bid_face_4", input_value="4")

    assert game.current_bid_quantity == 4
    assert game.current_bid_face == 5
    assert len(game.bid_history) == 1
    user = game.get_user(current)
    assert isinstance(user, MockUser)
    assert any("no longer legal" in line for line in spoken(user))


def test_traditional_ones_are_wild_except_on_ones_bid() -> None:
    game = make_game()
    set_dice(game, [1, 1, 5, 3, 4], [1, 5, 5, 2, 6])

    assert game._actual_count(5) == 6
    assert game._actual_count(1) == 3


def test_basic_rules_count_every_face_literally() -> None:
    game = make_game(ruleset=RULESET_BASIC)
    set_dice(game, [1, 1, 5, 3, 4], [1, 5, 5, 2, 6])

    assert game._actual_count(5) == 3
    assert game._actual_count(1) == 3
    assert (
        game._is_call_spot_on_enabled(game.players[0]) == "deadmansdice-action-no-bid"
    )
    assert game._is_turn_action_hidden(game.players[0]).value == "visible"


def test_basic_rules_allow_spot_on_but_do_not_treat_ones_as_wild() -> None:
    game = make_game(ruleset=RULESET_BASIC)
    bidder, caller = game.players
    set_dice(game, [1, 5, 5, 3, 4], [1, 5, 2, 2, 6])
    place_bid(game, bidder, 3, 5)

    assert game._is_call_spot_on_enabled(caller) is None
    game.execute_action(caller, "call_spot_on")
    finish_active_sequences(game)

    assert game.last_reveal_result == RESULT_SPOT_CORRECT
    assert game.last_reveal_actual == 3
    assert bidder.poison_doses == 1
    assert caller.poison_doses == 0


def test_false_bid_poisons_bidder_and_bidder_opens_next_round() -> None:
    game = make_game()
    bidder, challenger = game.players
    bidder_user = game.get_user(bidder)
    challenger_user = game.get_user(challenger)
    assert isinstance(bidder_user, MockUser)
    assert isinstance(challenger_user, MockUser)
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, bidder, 4, 5)
    bidder_user.clear_messages()
    challenger_user.clear_messages()

    game.execute_action(challenger, "call_liar")
    finish_active_sequences(game)

    assert bidder.poison_doses == 1
    assert challenger.poison_doses == 0
    assert game.round == 2
    assert game.current_player is bidder
    assert game.last_reveal_actual == 1
    assert game.last_reveal_result == RESULT_LIAR_BIDDER_LOST
    assert len(game.last_reveal) == 2
    assert game.current_bid_quantity == 0
    assert any("Your bid collapses" in line for line in spoken(bidder_user))
    assert any("Player1's bid collapses" in line for line in spoken(challenger_user))
    assert any(
        "You swallow the poison. Dose 1 of 2." == line
        for line in spoken(bidder_user)
    )
    assert any(
        "Player1 swallows the poison. Dose 1 of 2." == line
        for line in spoken(challenger_user)
    )


def test_challenge_calls_address_the_caller_personally() -> None:
    liar_game = make_game(player_count=3)
    bidder, caller, observer = liar_game.players
    set_dice(
        liar_game,
        [2, 2, 3, 3, 4],
        [2, 4, 5, 6, 6],
        [1, 3, 4, 5, 6],
    )
    place_bid(liar_game, bidder, 4, 5)
    caller_user = liar_game.get_user(caller)
    observer_user = liar_game.get_user(observer)
    assert isinstance(caller_user, MockUser)
    assert isinstance(observer_user, MockUser)
    caller_user.clear_messages()
    observer_user.clear_messages()

    liar_game.execute_action(caller, "call_liar")

    assert "You call Player1 a liar over 4 fives." in spoken(caller_user)
    assert "Player2 calls Player1 a liar over 4 fives." in spoken(observer_user)
    assert not any(
        line.startswith("Player2 calls") for line in spoken(caller_user)
    )

    spot_game = make_game(player_count=3)
    bidder, caller, observer = spot_game.players
    set_dice(
        spot_game,
        [1, 5, 2, 3, 4],
        [5, 2, 2, 3, 4],
        [1, 6, 6, 3, 4],
    )
    place_bid(spot_game, bidder, 4, 5)
    caller_user = spot_game.get_user(caller)
    observer_user = spot_game.get_user(observer)
    assert isinstance(caller_user, MockUser)
    assert isinstance(observer_user, MockUser)
    caller_user.clear_messages()
    observer_user.clear_messages()

    spot_game.execute_action(caller, "call_spot_on")

    assert "You call Spot On against Player1's bid of 4 fives." in spoken(
        caller_user
    )
    assert (
        "Player2 calls Spot On against Player1's bid of 4 fives."
        in spoken(observer_user)
    )
    assert not any(
        line.startswith("Player2 calls") for line in spoken(caller_user)
    )


def test_bid_that_holds_poisons_challenger() -> None:
    game = make_game()
    bidder, challenger = game.players
    set_dice(game, [1, 5, 3, 3, 4], [1, 5, 5, 6, 6])
    place_bid(game, bidder, 4, 5)

    game.execute_action(challenger, "call_liar")
    finish_active_sequences(game)

    assert challenger.poison_doses == 1
    assert bidder.poison_doses == 0
    assert game.current_player is challenger
    assert game.last_reveal_actual == 5


def test_second_poison_eliminates_loser_and_next_living_player_starts() -> None:
    game = make_game(player_count=3)
    bidder, challenger, third = game.players
    bidder.poison_doses = 1
    set_dice(
        game,
        [2, 2, 3, 3, 4],
        [2, 4, 5, 6, 6],
        [2, 3, 4, 6, 6],
    )
    place_bid(game, bidder, 5, 5)
    bidder_user = game.get_user(bidder)
    challenger_user = game.get_user(challenger)
    assert isinstance(bidder_user, MockUser)
    assert isinstance(challenger_user, MockUser)
    bidder_user.clear_messages()
    challenger_user.clear_messages()

    game.execute_action(challenger, "call_liar")
    finish_active_sequences(game)

    assert bidder.eliminated
    assert bidder.poison_doses == MAX_POISON_DOSES
    assert bidder.dice == []
    assert game.current_player is challenger
    assert bidder.id not in game.turn_player_ids
    assert third.id in game.turn_player_ids
    assert "The second dose takes you. You are out." in spoken(bidder_user)
    assert (
        "The second dose takes Player1. Player1 is out."
        in spoken(challenger_user)
    )
    assert "The second dose takes Player1. Player1 is out." not in spoken(
        bidder_user
    )


def test_correct_spot_on_poisons_every_other_survivor_and_can_end_match() -> None:
    game = make_game(player_count=3)
    bidder, caller, third = game.players
    caller_user = game.get_user(caller)
    bidder_user = game.get_user(bidder)
    assert isinstance(caller_user, MockUser)
    assert isinstance(bidder_user, MockUser)
    bidder.poison_doses = 1
    third.poison_doses = 1
    set_dice(
        game,
        [1, 5, 2, 3, 4],
        [5, 2, 2, 3, 4],
        [1, 6, 6, 3, 4],
    )
    place_bid(game, bidder, 4, 5)
    caller_user.clear_messages()
    bidder_user.clear_messages()

    game.execute_action(caller, "call_spot_on")
    finish_active_sequences(game)

    assert game.last_reveal_result == RESULT_SPOT_CORRECT
    assert game.last_reveal_actual == 4
    assert bidder.eliminated
    assert third.eliminated
    assert not caller.eliminated
    assert game.winner_id == caller.id
    assert game.status == "finished"
    lines = spoken(caller_user)
    assert "Your Spot On is exact. Everyone else must drink." in lines
    assert "You are the last survivor. You win Dead Man's Dice." in lines
    assert not any(line.startswith("Player2 calls it exactly") for line in lines)
    assert (
        "Player2 calls it exactly. Everyone else must drink."
        in spoken(bidder_user)
    )
    assert (
        "Player2 is the last survivor and wins Dead Man's Dice."
        in spoken(bidder_user)
    )
    bidder_eliminated = lines.index(
        "The second dose takes Player1. Player1 is out."
    )
    third_eliminated = lines.index(
        "The second dose takes Player3. Player3 is out."
    )
    assert bidder_eliminated < third_eliminated


def test_wrong_spot_on_poisons_only_caller() -> None:
    game = make_game()
    bidder, caller = game.players
    set_dice(game, [1, 5, 5, 3, 4], [1, 5, 5, 2, 6])
    place_bid(game, bidder, 4, 5)

    game.execute_action(caller, "call_spot_on")
    finish_active_sequences(game)

    assert caller.poison_doses == 1
    assert bidder.poison_doses == 0
    assert game.last_reveal_actual == 6
    assert game.current_player is caller


def test_maximum_bid_leaves_challenge_actions_but_no_raise() -> None:
    game = make_game()
    game.current_bid_quantity = game.maximum_bid_quantity
    game.current_bid_face = 6
    game.current_bidder_id = game.players[1].id
    current = game.players[0]

    assert all(not game._legal_quantities(face) for face in range(1, 7))
    assert game._is_call_liar_enabled(current) is None
    observation = game._bot_observation(current)
    with patch("server.games.deadmansdice.bot.random.uniform", return_value=0.0):
        assert choose_decision(observation).action in {"call_liar", "call_spot_on"}


def test_information_views_separate_private_and_public_state() -> None:
    game = make_game()
    first, second = game.players
    set_dice(game, [1, 2, 3, 4, 5], [6, 6, 6, 6, 6])
    user = game.get_user(first)
    assert isinstance(user, MockUser)

    table_text = " ".join(item.text for item in game._build_table_status(first, user))
    bids_text = " ".join(item.text for item in game._build_bid_status(first, user))
    assert "2 survivors; 10 dice in play" in table_text
    assert "Ones are wild" in table_text
    assert "Spot On is available" in table_text
    assert "1, 2, 3, 4" not in table_text
    assert "6, 6, 6" not in table_text
    assert "6, 6, 6" not in bids_text

    user.clear_messages()
    game.execute_action(first, "read_dice")
    assert spoken(user) == ["Your dice: 1, 2, 3, 4, and 5."]
    assert second.dice == [6, 6, 6, 6, 6]


def test_information_views_use_personal_perspective_for_the_listener() -> None:
    game = make_game()
    first, second = game.players
    first_user = game.get_user(first)
    second_user = game.get_user(second)
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    set_dice(game, [2, 2, 3, 3, 4], [2, 4, 5, 6, 6])
    place_bid(game, first, 4, 5)

    first_table = " ".join(
        item.text for item in game._build_table_status(first, first_user)
    )
    second_table = " ".join(
        item.text for item in game._build_table_status(second, second_user)
    )
    first_bids = " ".join(
        item.text for item in game._build_bid_status(first, first_user)
    )
    second_bids = " ".join(
        item.text for item in game._build_bid_status(second, second_user)
    )

    assert "Current bid: your 4 fives." in first_table
    assert "You: poison dose 0 of 2." in first_table
    assert "Player1" not in first_table
    assert "Current bid: 4 fives, by Player1." in second_table
    assert "1. You: 4 fives." in first_bids
    assert "1. Player1: 4 fives." in second_bids

    game.execute_action(second, "call_liar")
    finish_active_sequences(game)
    first_reveal = " ".join(
        item.text for item in game._build_last_reveal_status(first, first_user)
    )
    second_reveal = " ".join(
        item.text for item in game._build_last_reveal_status(second, second_user)
    )

    assert "You: 2, 2, 3, 3, and 4." in first_reveal
    assert "Your bid was too high; you lost the challenge." in first_reveal
    assert "Player1: 2, 2, 3, 3, and 4." in second_reveal
    assert "The bid was too high; Player1 lost the challenge." in second_reveal


def test_private_dice_are_sorted_for_review_without_mutating_the_roll() -> None:
    game = make_game()
    player = game.players[0]
    player.dice = [6, 1, 4, 1, 3]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game.execute_action(player, "read_dice")

    assert spoken(user) == ["Your dice: 1, 1, 3, 4, and 6."]
    assert player.dice == [6, 1, 4, 1, 3]


def test_touch_clients_receive_info_controls_and_descriptions() -> None:
    game = make_game(touch_indexes={0})
    player = game.players[0]
    visible = {
        action.action.id: action for action in game.get_all_visible_actions(player)
    }

    assert "read_dice" in visible
    assert "read_table" in visible
    assert "review_bids" in visible
    assert visible["bid_face_1"].description
    assert visible["call_liar"].description


def test_device_handover_rebuilds_standard_action_order() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    standard = game.get_action_set(player, "standard")
    assert standard is not None
    desktop_order = list(standard._order)

    user.client_type = "mobile"
    game.before_menu_build(player)
    standard = game.get_action_set(player, "standard")
    assert standard is not None
    assert standard._order != desktop_order
    assert standard._order.index("read_dice") < standard._order.index("whose_turn")

    user.client_type = None
    game.before_menu_build(player)
    standard = game.get_action_set(player, "standard")
    assert standard is not None
    assert standard._order == desktop_order


def test_challenge_controls_name_the_current_bid() -> None:
    game = make_game()
    bidder, caller = game.players
    place_bid(game, bidder, 3, 4)

    visible = {
        action.action.id: action for action in game.get_all_visible_actions(caller)
    }

    assert visible["call_liar"].label == "Call liar — 3 fours"
    assert "bid of 3 fours" in visible["call_liar"].description
    assert visible["call_spot_on"].label == "Call Spot On — exactly 3 fours"
    assert "exactly 3 fours" in visible["call_spot_on"].description


def test_bid_quantity_prompt_names_the_selected_face_without_history() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game.execute_action(player, "bid_face_5")

    assert spoken(user) == ["Bidding fives. Choose a quantity."]


def test_spectator_can_review_public_state_but_not_private_dice() -> None:
    game = make_game(start=False)
    spectator_user = MockUser("Watcher", uuid="watcher")
    spectator = game.add_spectator("Watcher", spectator_user)
    assert spectator is not None
    with patch("server.games.deadmansdice.game.random.shuffle", lambda values: None):
        game.on_start()
    finish_active_sequences(game)

    public_action = game.find_action(spectator, "read_table")
    private_action = game.find_action(spectator, "read_dice")
    assert public_action is not None and public_action.include_spectators
    assert private_action is not None and not private_action.include_spectators
    spectator_user.clear_messages()
    game.execute_action(spectator, "read_dice")
    assert not spectator_user.get_spoken_messages()


def test_save_restore_preserves_hidden_and_public_round_state() -> None:
    game = make_game(player_count=3)
    set_dice(
        game,
        [1, 2, 3, 4, 5],
        [2, 2, 3, 3, 4],
        [6, 6, 5, 5, 4],
    )
    place_bid(game, game.players[0], 3, 4)

    restored = DeadMansDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert [player.dice for player in restored.players] == [
        [1, 2, 3, 4, 5],
        [2, 2, 3, 3, 4],
        [6, 6, 5, 5, 4],
    ]
    assert restored.current_bid_quantity == 3
    assert restored.current_bid_face == 4
    assert restored.bid_history[0].player_id == game.players[0].id
    assert restored.current_player is restored.players[1]


def test_save_restore_preserves_a_bots_complete_pending_bid_plan() -> None:
    game = make_game(bot_indexes={0})
    bot = game.players[0]
    bot.dice = [1, 2, 2, 4, 6]

    with patch("server.games.deadmansdice.bot.random.uniform", return_value=0.0):
        action_id = game.bot_think(bot)
    assert action_id and action_id.startswith("bid_face_")
    assert bot.bot_target is not None
    bot.bot_pending_action = action_id
    bot.bot_think_ticks = 0
    planned_quantity = bot.bot_target
    planned_face = int(action_id.removeprefix("bid_face_"))

    restored = DeadMansDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_bot = restored.players[0]

    assert restored_bot.bot_pending_action == action_id
    assert restored_bot.bot_target == planned_quantity

    restored.on_tick()

    assert restored.current_bid_quantity == planned_quantity
    assert restored.current_bid_face == planned_face
    assert restored.bid_history[-1].player_id == restored_bot.id


def test_results_use_immutable_ids_for_stats_and_rating_competitors() -> None:
    game = make_game()
    winner, loser = game.players
    game.winner_id = winner.id
    loser.eliminated = True
    loser.eliminated_round = 2
    winner.bids_made = 3

    result = game.build_game_result()

    assert result.custom_data["winner_ids"] == [winner.id]
    assert set(result.custom_data["player_stats"]) == {winner.id, loser.id}
    assert result.custom_data["player_stats"][winner.id]["bids_made"] == 3
    assert result.custom_data["rating_competitors"]


def test_bot_probability_uses_only_own_dice_and_public_counts() -> None:
    observation = BotObservation(
        own_dice=(1, 5, 2, 3, 4),
        unknown_dice=5,
        maximum_quantity=10,
        ones_are_wild=True,
        poison_doses=0,
        poison_limit=MAX_POISON_DOSES,
        current_quantity=4,
        current_face=5,
    )
    truth = bid_truth_probability(observation, 4, 5)
    exact = bid_exact_probability(observation, 4, 5)

    assert 0.0 < exact < truth < 1.0
    assert not hasattr(observation, "opponent_dice")


def test_bot_treats_public_bid_history_as_weak_evidence() -> None:
    base = BotObservation(
        own_dice=(2, 3, 4, 5, 6),
        unknown_dice=10,
        maximum_quantity=15,
        ones_are_wild=False,
        poison_doses=0,
        poison_limit=MAX_POISON_DOSES,
        current_quantity=4,
        current_face=5,
    )
    informed = BotObservation(
        own_dice=base.own_dice,
        unknown_dice=base.unknown_dice,
        maximum_quantity=base.maximum_quantity,
        ones_are_wild=base.ones_are_wild,
        poison_doses=base.poison_doses,
        poison_limit=base.poison_limit,
        current_quantity=base.current_quantity,
        current_face=base.current_face,
        bid_history=((2, 5, False), (4, 5, False)),
    )
    own_claims = BotObservation(
        own_dice=base.own_dice,
        unknown_dice=base.unknown_dice,
        maximum_quantity=base.maximum_quantity,
        ones_are_wild=base.ones_are_wild,
        poison_doses=base.poison_doses,
        poison_limit=base.poison_limit,
        current_quantity=base.current_quantity,
        current_face=base.current_face,
        bid_history=((2, 5, True), (4, 5, True)),
    )

    raw = perceived_truth_probability(base, 4, 5)
    with_claims = perceived_truth_probability(informed, 4, 5)

    assert bid_truth_probability(base, 4, 5) == raw
    assert perceived_truth_probability(own_claims, 4, 5) == raw
    assert raw < with_claims < 1.0


def test_bot_observation_contains_public_stakes_but_no_hidden_opponent_dice() -> None:
    game = make_game(player_count=3)
    bidder, bot_player, third = game.players
    bidder.poison_doses = 1
    third.poison_doses = 1
    place_bid(game, bidder, 3, 4)

    observation = game._bot_observation(bot_player)

    assert observation.bid_history == ((3, 4, False),)
    assert observation.bidder_poison_doses == 1
    assert observation.opponent_poison_doses == (1, 1)
    assert not hasattr(observation, "opponent_dice")


def test_bot_varies_near_equal_opening_bids_without_making_illegal_bids() -> None:
    observation = BotObservation(
        own_dice=(1, 2, 3, 4, 5),
        unknown_dice=15,
        maximum_quantity=20,
        ones_are_wild=True,
        poison_doses=0,
        poison_limit=MAX_POISON_DOSES,
    )
    random_state = random.getstate()
    try:
        random.seed(1447)
        decisions = {choose_decision(observation) for _ in range(40)}
    finally:
        random.setstate(random_state)

    assert len(decisions) > 1
    assert all(
        decision.quantity is not None
        and is_legal_bid(
            decision.quantity,
            int(decision.action.removeprefix("bid_face_")),
            0,
            0,
            observation.maximum_quantity,
        )
        for decision in decisions
    )


@pytest.mark.parametrize("ones_are_wild", [False, True])
def test_bot_decisions_are_legal_across_random_public_states(
    ones_are_wild: bool,
) -> None:
    generator = random.Random(5137 + int(ones_are_wild))
    random_state = random.getstate()
    try:
        random.seed(8317 + int(ones_are_wild))
        for _ in range(400):
            player_count = generator.randint(2, 4)
            maximum = player_count * DICE_PER_PLAYER
            has_bid = generator.choice([False, True])
            current_quantity = generator.randint(1, maximum) if has_bid else 0
            current_face = generator.randint(1, DIE_SIDES) if has_bid else 0
            observation = BotObservation(
                own_dice=tuple(
                    generator.randint(1, DIE_SIDES) for _ in range(DICE_PER_PLAYER)
                ),
                unknown_dice=maximum - DICE_PER_PLAYER,
                maximum_quantity=maximum,
                ones_are_wild=ones_are_wild,
                poison_doses=generator.randint(0, MAX_POISON_DOSES - 1),
                poison_limit=MAX_POISON_DOSES,
                current_quantity=current_quantity,
                current_face=current_face,
                bidder_poison_doses=generator.randint(
                    0,
                    MAX_POISON_DOSES - 1,
                ),
                opponent_poison_doses=tuple(
                    generator.randint(0, MAX_POISON_DOSES - 1)
                    for _ in range(player_count - 1)
                ),
            )

            decision = choose_decision(observation)

            if decision.action.startswith("bid_face_"):
                assert decision.quantity is not None
                assert is_legal_bid(
                    decision.quantity,
                    int(decision.action.removeprefix("bid_face_")),
                    current_quantity,
                    current_face,
                    maximum,
                )
            else:
                assert has_bid
                assert decision.quantity is None
                assert decision.action in {"call_liar", "call_spot_on"}
    finally:
        random.setstate(random_state)


def test_bot_turn_completes_face_and_quantity_without_private_opponent_data() -> None:
    game = make_game(bot_indexes={0})
    bot = game.players[0]
    assert bot.is_bot and game.current_player is bot
    bot.dice = [1, 2, 2, 4, 6]
    bot.bot_think_ticks = 0

    with (
        patch("server.games.deadmansdice.bot.random.uniform", return_value=0.0),
        patch(
            "server.games.deadmansdice.game.choose_bot_quantity",
            side_effect=AssertionError("the precomputed quantity should be reused"),
        ),
    ):
        game.on_tick()
        game.on_tick()

    assert len(game.bid_history) == 1
    assert game.bid_history[0].player_id == bot.id
    assert game.current_player is game.players[1]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_four_bot_match_reaches_one_survivor(seed: int) -> None:
    random_state = random.getstate()
    try:
        random.seed(seed)
        game = make_game(
            player_count=4,
            bot_indexes={0, 1, 2, 3},
        )
        for _ in range(10000):
            if game.winner_id:
                break
            game.on_tick()

        assert game.winner_id
        assert len(game.alive_players) == 1
        assert game.alive_players[0].id == game.winner_id
    finally:
        random.setstate(random_state)


def test_keybinds_use_scoped_nonconflicting_commands() -> None:
    game = make_game(start=False)
    active_bindings = {
        key: [binding for binding in bindings if binding.state.name == "ACTIVE"]
        for key, bindings in game._keybinds.items()
    }
    assert active_bindings["b"][0].actions == ["review_bids"]
    assert any(binding.actions == ["add_bot"] for binding in game._keybinds["b"])
    assert "f1" not in game._keybinds
    assert "ctrl+f1" in game._keybinds


def test_english_and_vietnamese_game_locales_have_identical_keys() -> None:
    def keys(locale: str) -> set[str]:
        path = _locales_dir / locale / "deadmansdice.ftl"
        return {
            line.split("=", 1)[0].strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith((" ", "#")) and "=" in line
        }

    assert keys("en") == keys("vi")
    assert Localization.get("en", "game-name-deadmansdice") == "Dead Man's Dice"
    assert Localization.get("vi", "game-name-deadmansdice") == "Xúc Xắc Tử Thần"


def test_every_game_locale_key_is_referenced_and_perspective_pairs_are_complete() -> None:
    locale_path = _locales_dir / "en" / "deadmansdice.ftl"
    locale_keys = {
        line.split("=", 1)[0].strip()
        for line in locale_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith((" ", "#")) and "=" in line
    }
    source_path = Path(__file__).parent.parent / "games" / "deadmansdice" / "game.py"
    source = source_path.read_text(encoding="utf-8")
    referenced = set(re.findall(r'["\'](deadmansdice-[a-z0-9-]+)["\']', source))
    referenced.add("game-name-deadmansdice")
    for face in range(1, DIE_SIDES + 1):
        referenced.add(f"deadmansdice-face-{face}")
        referenced.add(f"deadmansdice-face-{face}-singular")

    assert locale_keys - referenced == set()

    perspective_pairs = (
        ("deadmansdice-you-bid", "deadmansdice-player-bids"),
        ("deadmansdice-you-call-liar", "deadmansdice-player-calls-liar"),
        (
            "deadmansdice-you-call-spot-on",
            "deadmansdice-player-calls-spot-on",
        ),
        ("deadmansdice-your-cup-reveals", "deadmansdice-player-cup-reveals"),
        ("deadmansdice-your-bid-too-high", "deadmansdice-player-bid-too-high"),
        (
            "deadmansdice-you-challenged-truth",
            "deadmansdice-player-challenged-truth",
        ),
        (
            "deadmansdice-your-spot-on-correct",
            "deadmansdice-player-spot-on-correct",
        ),
        (
            "deadmansdice-your-spot-on-wrong",
            "deadmansdice-player-spot-on-wrong",
        ),
        (
            "deadmansdice-you-drink-poison",
            "deadmansdice-player-drinks-poison",
        ),
        ("deadmansdice-you-eliminated", "deadmansdice-player-eliminated"),
        ("deadmansdice-you-win", "deadmansdice-player-wins"),
        (
            "deadmansdice-table-current-bid-you",
            "deadmansdice-table-current-bid",
        ),
        ("deadmansdice-table-turn-you", "deadmansdice-table-turn"),
        ("deadmansdice-table-player-you", "deadmansdice-table-player"),
        (
            "deadmansdice-table-player-you-eliminated",
            "deadmansdice-table-player-eliminated",
        ),
        ("deadmansdice-bids-line-you", "deadmansdice-bids-line"),
        (
            "deadmansdice-last-reveal-player-you",
            "deadmansdice-last-reveal-player",
        ),
        (
            "deadmansdice-last-result-liar-bidder-lost-you",
            "deadmansdice-last-result-liar-bidder-lost",
        ),
        (
            "deadmansdice-last-result-liar-challenger-lost-you",
            "deadmansdice-last-result-liar-challenger-lost",
        ),
        (
            "deadmansdice-last-result-spot-correct-you",
            "deadmansdice-last-result-spot-correct",
        ),
        (
            "deadmansdice-last-result-spot-wrong-you",
            "deadmansdice-last-result-spot-wrong",
        ),
    )
    for locale in ("en", "vi"):
        locale_text = (_locales_dir / locale / "deadmansdice.ftl").read_text(
            encoding="utf-8"
        )
        for personal_key, public_key in perspective_pairs:
            assert personal_key in locale_keys
            assert public_key in locale_keys
            personal = re.search(
                rf"(?m)^{re.escape(personal_key)}\s*=\s*(.+)$",
                locale_text,
            )
            public = re.search(
                rf"(?m)^{re.escape(public_key)}\s*=\s*(.+)$",
                locale_text,
            )
            assert personal is not None
            assert public is not None
            assert "{$player}" not in personal.group(1).replace(" ", "")
            assert "{$player}" in public.group(1).replace(" ", "")


def test_manuals_exist_in_both_official_languages() -> None:
    documentation = Path(__file__).parent.parent / "documentation" / "content"
    for locale in ("en", "vi"):
        text = (documentation / locale / "games" / "deadmansdice.md").read_text(
            encoding="utf-8"
        )
        assert "Spot On" in text if locale == "en" else "Chính xác" in text
        assert "Ctrl+U" in text
