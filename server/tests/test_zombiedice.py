"""Rules, accessibility, persistence, and bot tests for Zombie Dice."""

from __future__ import annotations

import hashlib
import math
import random
import struct
from itertools import pairwise
from pathlib import Path
from unittest.mock import patch

import pytest

from ..game_utils.actions import Visibility
from ..games.registry import GameRegistry
from ..games.zombiedice import audio as zombie_audio
from ..games.zombiedice.bot import (
    BotObservation,
    choose_action,
    next_roll_metrics,
)
from ..games.zombiedice.game import (
    BOT_THINK_TICKS,
    ZombieDiceGame,
    ZombieDiceOptions,
    ZombieDicePlayer,
)
from ..games.zombiedice.rules import (
    BRAIN,
    COLORS,
    DICE_BY_COLOR,
    DICE_PER_ROLL,
    FACE_DISTRIBUTIONS,
    FOOTPRINT,
    GREEN,
    OFFICIAL_TARGET_SCORE,
    RED,
    SHOTGUN,
    YELLOW,
    DicePool,
    RollResult,
    draw_colors,
    has_complete_die_set,
)
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
Localization.init(ROOT / "server" / "locales")


def make_game(
    player_count: int = 2,
    *,
    start: bool = True,
    bots: bool = False,
    touch_indexes: set[int] | None = None,
    target_score: int = OFFICIAL_TARGET_SCORE,
) -> ZombieDiceGame:
    game = ZombieDiceGame(options=ZombieDiceOptions(target_score=target_score))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bots:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if touch_indexes and index in touch_indexes:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        with patch("server.games.zombiedice.game.random.shuffle", lambda values: None):
            game.on_start()
        game.flush_menus()
    return game


def finish_active_sequences(game: ZombieDiceGame) -> None:
    for _ in range(100):
        if not game.active_sequences:
            return
        game.sound_scheduler_tick = max(
            game.sound_scheduler_tick,
            min(sequence.next_tick for sequence in game.active_sequences),
        )
        game.process_sequences()
    pytest.fail("Zombie Dice sequence did not finish")


def start_roll(
    game: ZombieDiceGame,
    faces: tuple[str, str, str],
) -> None:
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)

    def fixed_roll(colors: list[str]) -> list[RollResult]:
        assert len(colors) == len(faces) == 3
        return [
            RollResult(color=color, face=face)
            for color, face in zip(colors, faces, strict=True)
        ]

    with (
        patch("server.games.zombiedice.game.roll_colors", fixed_roll),
        patch("server.games.zombiedice.game.random.shuffle", lambda values: None),
    ):
        game.execute_action(player, "roll")


def play_roll(
    game: ZombieDiceGame,
    faces: tuple[str, str, str],
) -> None:
    start_roll(game, faces)
    finish_active_sequences(game)
    game.flush_menus()


def bank(game: ZombieDiceGame, brains: int) -> None:
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    game.has_rolled = True
    game.turn_brains = brains
    game.execute_action(player, "bank")
    game.flush_menus()


def set_score(game: ZombieDiceGame, player: ZombieDicePlayer, score: int) -> None:
    team = game._team_manager.get_team(player.name)
    assert team is not None
    team.total_score = score


def locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and "=" in line
        and not line[0].isspace()
    }


def audio_packets(user: MockUser, *, kind: str | None = None) -> list[dict]:
    packets = [
        message.data
        for message in user.messages
        if message.data.get("type") == "audio" and message.data.get("command") == "play"
    ]
    if kind is None:
        return packets
    return [packet for packet in packets if packet.get("kind") == kind]


def audio_segment_onsets(segments: list) -> dict[str, float]:
    """Return each uniquely selected test asset's client-clock onset."""

    elapsed_ms = 0.0
    onsets: dict[str, float] = {}
    for segment in segments:
        asset = segment.asset if hasattr(segment, "asset") else segment["asset"]
        ratio = (
            segment.next_start_ratio
            if hasattr(segment, "next_start_ratio")
            else segment["next_start_ratio"]
        )
        onsets[asset] = elapsed_ms
        elapsed_ms += zombie_audio.sound_milliseconds(asset) * ratio
    return onsets


def test_sound_assets_are_complete_identical_and_use_authored_formats() -> None:
    pack_roots = (
        ROOT / "client" / "sounds",
        ROOT / "web_client" / "sounds",
        ROOT / "mobile_client" / "sounds",
    )

    for root in pack_roots:
        actual_assets = {
            f"game_zombiedice/{path.name}"
            for path in (root / "game_zombiedice").iterdir()
            if path.is_file()
        }
        assert actual_assets == zombie_audio.ALL_SOUND_ASSETS

    for asset in zombie_audio.ALL_SOUND_ASSETS:
        copies = [root / Path(asset) for root in pack_roots]
        contents = [copy.read_bytes() for copy in copies]
        assert all(content.startswith(b"OggS") for content in contents)
        assert len({hashlib.sha256(content).digest() for content in contents}) == 1
        identification = contents[0].find(b"\x01vorbis")
        assert identification >= 0
        channels = contents[0][identification + 11]
        sample_rate = struct.unpack_from("<I", contents[0], identification + 12)[0]
        if asset == zombie_audio.SOUND_MUSIC:
            assert channels == 2
            assert sample_rate == 44100
        else:
            assert channels == 1
            assert sample_rate == 48000


def test_timed_audio_fallbacks_match_every_shipped_roll_sequence_asset() -> None:
    timed_assets = {
        zombie_audio.SOUND_CUP_REFILL,
        *zombie_audio.SOUND_ROLL_SHAKES,
        *zombie_audio.SOUND_ROLL_LANDS,
        *zombie_audio.SOUND_SHOTGUNS,
        *zombie_audio.SOUND_SHOT_FLYBYS,
        *zombie_audio.SOUND_SHOT_IMPACTS,
        *zombie_audio.SOUND_SHELL_CASINGS,
        *zombie_audio.SOUND_BUSTS,
    }
    assert set(zombie_audio.AUDIO_DURATIONS_TICKS) == timed_assets
    assert all(
        zombie_audio.sound_ticks(asset) == zombie_audio.AUDIO_DURATIONS_TICKS[asset]
        for asset in timed_assets
    )


def test_roll_audio_banks_are_authored_for_the_exact_three_dice_roll() -> None:
    shakes, lands = zombie_audio.roll_sound_bank(DICE_PER_ROLL)
    assert shakes == zombie_audio.SOUND_ROLL_SHAKES
    assert lands == zombie_audio.SOUND_ROLL_LANDS
    with pytest.raises(ValueError):
        zombie_audio.roll_sound_bank(DICE_PER_ROLL - 1)


def test_scene_transform_and_route_interpolation_are_listener_relative() -> None:
    source = (8.0, 6.0, 2.0)
    assert zombie_audio.listener_relative_scene_position(source, None, 4) == source
    assert zombie_audio.listener_relative_scene_position(source, 0, 4) == (
        -8.0,
        -4.0,
        2.0,
    )
    assert zombie_audio.listener_relative_scene_position(source, 1, 4) == (
        6.0,
        -6.0,
        2.0,
    )
    assert zombie_audio.interpolate_world_position(
        (-8.0, 5.8, 0.0),
        (-2.5, 5.8, 0.0),
        0.4,
    ) == (-5.8, 5.8, 0.0)
    with pytest.raises(ValueError):
        zombie_audio.interpolate_world_position(source, source, 1.1)
    assert zombie_audio.table_seat_world_position(0, 2) == (0.0, 2.0, 0.0)
    assert zombie_audio.table_seat_world_position(1, 2) == (0.0, -2.0, 0.0)
    with pytest.raises(ValueError):
        zombie_audio.table_seat_world_position(0, 1)


def test_start_builds_private_spatial_ambience_and_schedules_first_passby() -> None:
    game = make_game()
    first, second = game.players
    first_user = game.get_user(first)
    second_user = game.get_user(second)
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)

    first_ambience = audio_packets(first_user, kind="ambience")
    second_ambience = audio_packets(second_user, kind="ambience")
    assert len(first_ambience) == len(zombie_audio.AMBIENCE_SOURCES)
    assert len(second_ambience) == len(zombie_audio.AMBIENCE_SOURCES)
    assert all(packet["scope"] == "player" for packet in first_ambience)
    assert all(packet["context"] == first.id for packet in first_ambience)
    assert all(
        packet["attenuation"] == zombie_audio.SCENE_ATTENUATION.to_packet()
        for packet in first_ambience
    )
    assert [packet["position"] for packet in first_ambience] != [
        packet["position"] for packet in second_ambience
    ]
    first_music = audio_packets(first_user, kind="music")
    assert len(first_music) == 1
    assert first_music[0]["asset"] == zombie_audio.SOUND_MUSIC
    assert first_music[0]["fade_in_ms"] == zombie_audio.MUSIC_FADE_IN_MS
    assert first_music[0]["fade_out_ms"] == zombie_audio.MUSIC_FADE_OUT_MS
    assert first_music[0]["gain"] == zombie_audio.MUSIC_GAIN == 0.8
    assert (
        game.sound_scheduler_tick + zombie_audio.WANDER_INITIAL_DELAY_TICKS[0]
        <= game.next_ambient_event_tick
        <= game.sound_scheduler_tick + zombie_audio.WANDER_INITIAL_DELAY_TICKS[1]
    )


def test_roll_audio_fires_from_centre_and_travels_to_the_victim() -> None:
    game = make_game()
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    actor_roll = audio_packets(actor_user, kind="sfx")[0]
    observer_roll = audio_packets(observer_user, kind="sfx")[0]
    actor_segments = actor_roll["segments"]
    assert actor_roll["buffer"] == "game"
    assert len(actor_segments) == 6
    assert actor_segments[0]["asset"] in zombie_audio.SOUND_ROLL_SHAKES
    assert actor_segments[1]["asset"] in zombie_audio.SOUND_ROLL_LANDS
    assert actor_segments[2]["asset"] in zombie_audio.SOUND_SHOTGUNS
    assert actor_segments[3]["asset"] in zombie_audio.SOUND_SHOT_FLYBYS
    assert actor_segments[4]["asset"] in zombie_audio.SOUND_SHOT_IMPACTS
    assert actor_segments[5]["asset"] in zombie_audio.SOUND_SHELL_CASINGS
    assert [segment["position"] for segment in actor_segments] == [
        None,
        None,
        [0.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 2.0, 0.0],
    ]
    assert actor_segments[3]["destination_position"] == [0.0, 0.0, 0.0]
    observer_segments = observer_roll["segments"]
    assert [segment["position"] for segment in observer_segments] == [
        [0.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 4.0, 0.0],
        [0.0, 2.0, 0.0],
    ]
    assert observer_segments[3]["destination_position"] == [0.0, 4.0, 0.0]
    assert actor_segments[4]["gain"] == zombie_audio.SHOT_IMPACT_GAIN
    assert actor_segments[4]["attenuation"] == (
        zombie_audio.TABLE_ATTENUATION.to_packet()
    )
    assert actor_segments[0]["next_start_ratio"] == (zombie_audio.ROLL_SHAKE_NEXT_RATIO)
    assert actor_segments[1]["next_start_ratio"] == (zombie_audio.ROLL_LAND_NEXT_RATIO)
    assert actor_segments[2]["next_start_ratio"] == 0.0
    assert actor_segments[3]["next_start_ratio"] == (zombie_audio.FLYBY_TO_IMPACT_RATIO)
    assert actor_segments[4]["next_start_ratio"] == 0.0


@pytest.mark.parametrize(
    ("shotgun_count", "busted"),
    [(2, False), (2, True), (3, True)],
)
def test_multiple_shotguns_use_the_breachpoint_style_burst_cadence(
    shotgun_count: int,
    busted: bool,
) -> None:
    game = make_game()
    plan = {
        "shake": zombie_audio.SOUND_ROLL_SHAKES[0],
        "land": zombie_audio.SOUND_ROLL_LANDS[0],
        "shotguns": list(zombie_audio.SOUND_SHOTGUNS[:shotgun_count]),
        "flybys": list(zombie_audio.SOUND_SHOT_FLYBYS[:shotgun_count]),
        "impacts": list(zombie_audio.SOUND_SHOT_IMPACTS[:shotgun_count]),
        "casings": list(zombie_audio.SOUND_SHELL_CASINGS[:shotgun_count]),
        "bust": zombie_audio.SOUND_BUSTS[0] if busted else "",
    }

    segments = game._build_roll_audio_segments(
        plan,
        recycled=0,
        shotgun_count=shotgun_count,
        busted=busted,
    )

    assert segments is not None
    onsets = audio_segment_onsets(segments)
    shotgun_onsets = [onsets[asset] for asset in plan["shotguns"]]

    assert len(shotgun_onsets) == shotgun_count
    assert all(
        following - current
        == pytest.approx(
            zombie_audio.BULLET_BURST_INTERVAL_MS,
            abs=0.01,
        )
        for current, following in pairwise(shotgun_onsets)
    )
    for shotgun, flyby, impact, casing in zip(
        plan["shotguns"],
        plan["flybys"],
        plan["impacts"],
        plan["casings"],
        strict=True,
    ):
        assert onsets[flyby] == pytest.approx(onsets[shotgun], abs=0.01)
        assert onsets[impact] - onsets[flyby] == pytest.approx(
            zombie_audio.sound_milliseconds(flyby) * zombie_audio.FLYBY_TO_IMPACT_RATIO,
            abs=0.01,
        )
        assert onsets[casing] == pytest.approx(onsets[impact], abs=0.01)
    if busted:
        assert onsets[plan["bust"]] == pytest.approx(
            onsets[plan["impacts"][-1]],
            abs=0.01,
        )


def test_roll_resolves_at_landing_while_the_dispatched_effect_tail_continues() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    cup_before = game.cup.copy()

    start_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    assert len(game.active_sequences) == 1
    sequence = game.active_sequences[0]
    assert sequence.current_index == 1
    assert sequence.next_tick > game.sound_scheduler_tick
    assert game.cup == cup_before
    assert game.last_roll == []
    assert not game.has_rolled
    assert player.rolls_made == 0
    assert game._is_roll_enabled(player) == "zombiedice-error-roll-resolving"
    assert len(audio_packets(user, kind="sfx")) == 1
    roll_segments = audio_packets(user, kind="sfx")[0]["segments"]
    timeline = [
        (segment["asset"], segment["next_start_ratio"]) for segment in roll_segments
    ]
    result_delay = zombie_audio.roll_result_delay_ticks(timeline)
    full_audio_duration = zombie_audio.finite_sequence_duration_ticks(timeline)
    assert sequence.next_tick - game.sound_scheduler_tick == result_delay
    assert result_delay == math.ceil(
        sum(zombie_audio.sound_milliseconds(asset) for asset, _ratio in timeline[:2])
        * zombie_audio.TICKS_PER_SECOND
        / 1000
    )
    assert result_delay < full_audio_duration

    game.execute_action(player, "roll")

    assert len(game.active_sequences) == 1
    assert len(audio_packets(user, kind="sfx")) == 1
    assert any(
        "still rolling" in message.lower() for message in user.get_spoken_messages()
    )

    game.sound_scheduler_tick = sequence.next_tick - 1
    game.process_sequences()
    assert game.last_roll == []
    assert game.active_sequences

    finish_active_sequences(game)

    assert not game.active_sequences
    assert game.has_rolled
    assert player.rolls_made == 1
    assert [result.face for result in game.last_roll] == [
        BRAIN,
        FOOTPRINT,
        SHOTGUN,
    ]


def test_bust_passes_the_turn_at_landing_without_waiting_for_audio_tails() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    next_player = game.players[1]
    user = game.get_user(player)
    observer_user = game.get_user(next_player)
    assert isinstance(user, MockUser)
    assert isinstance(observer_user, MockUser)
    user.clear_messages()
    observer_user.clear_messages()

    start_roll(game, (SHOTGUN, SHOTGUN, SHOTGUN))

    sequence = game.active_sequences[0]
    roll_segments = audio_packets(user, kind="sfx")[0]["segments"]
    timeline = [
        (segment["asset"], segment["next_start_ratio"]) for segment in roll_segments
    ]
    assert timeline[-1][0] in zombie_audio.SOUND_BUSTS
    assert roll_segments[-1]["position"] is None
    observer_segments = audio_packets(observer_user, kind="sfx")[0]["segments"]
    assert observer_segments[-1]["position"] == [0.0, 4.0, 0.0]
    assert all(
        segment["position"] == [0.0, 2.0, 0.0]
        for segment in observer_segments
        if segment["asset"] in zombie_audio.SOUND_SHOTGUNS
    )
    assert all(
        segment["destination_position"] == [0.0, 4.0, 0.0]
        for segment in observer_segments
        if segment["asset"] in zombie_audio.SOUND_SHOT_FLYBYS
    )
    assert zombie_audio.roll_result_delay_ticks(timeline) < (
        zombie_audio.finite_sequence_duration_ticks(timeline)
    )

    game.sound_scheduler_tick = sequence.next_tick
    game.process_sequences()

    assert not game.active_sequences
    assert game.current_player is next_player
    assert player.busts == 1
    assert game._is_roll_enabled(next_player) is None


def test_roll_sequence_locks_banking_but_keeps_information_available() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    play_roll(game, (BRAIN, FOOTPRINT, FOOTPRINT))
    assert game.turn_brains == 1

    start_roll(game, (BRAIN, BRAIN, BRAIN))

    assert game._is_bank_hidden(player) is Visibility.VISIBLE
    assert game._is_bank_enabled(player) == "zombiedice-error-roll-resolving"
    assert game._is_public_info_enabled(player) is None
    game.execute_action(player, "bank")
    assert game.current_player is player
    assert game.get_player_score(player) == 0
    assert game.turn_brains == 1
    assert game.active_sequences

    finish_active_sequences(game)

    assert game.turn_brains == 4


def test_refill_and_bust_sounds_follow_the_resolved_physical_roll() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    game.cup = DicePool(green=1)
    game.footprints = DicePool(yellow=1)
    game.brain_dice = DicePool(green=5, yellow=3, red=1)
    game.shotgun_dice = DicePool(red=2)
    game.turn_brains = 12
    game.has_rolled = True
    user.clear_messages()

    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    roll = audio_packets(user, kind="sfx")[0]
    assets = [segment["asset"] for segment in roll["segments"]]
    assert assets[0] == zombie_audio.SOUND_CUP_REFILL
    assert assets[1] in zombie_audio.SOUND_ROLL_SHAKES
    assert assets[2] in zombie_audio.SOUND_ROLL_LANDS
    assert assets[3] in zombie_audio.SOUND_SHOTGUNS
    assert assets[4] in zombie_audio.SOUND_SHOT_FLYBYS
    assert assets[5] in zombie_audio.SOUND_SHOT_IMPACTS
    assert assets[6] in zombie_audio.SOUND_SHELL_CASINGS
    assert assets[7] in zombie_audio.SOUND_BUSTS


def test_positive_bank_has_a_seated_cue_but_zero_bank_is_silent() -> None:
    game = make_game(target_score=50)
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    bank(game, 4)

    actor_bank = audio_packets(actor_user, kind="sfx")[0]
    observer_bank = audio_packets(observer_user, kind="sfx")[0]
    assert actor_bank["segments"][0]["asset"] == zombie_audio.SOUND_BANK_BITE
    assert actor_bank["segments"][1]["asset"] in zombie_audio.SOUND_BANK_GROWLS
    assert all(segment["position"] is None for segment in actor_bank["segments"])
    assert all(
        segment["position"] == [0.0, 2.0, 0.0] for segment in observer_bank["segments"]
    )

    actor_user.clear_messages()
    observer_user.clear_messages()
    bank(game, 0)
    for user in (actor_user, observer_user):
        assert not any(
            segment["asset"] == zombie_audio.SOUND_BANK_BITE
            or segment["asset"] in zombie_audio.SOUND_BANK_GROWLS
            for packet in audio_packets(user, kind="sfx")
            for segment in packet.get("segments", [])
        )


def test_final_round_and_win_cues_do_not_leave_replayable_audio() -> None:
    game = make_game(target_score=5)
    first, _second = game.players
    first_user = game.get_user(first)
    assert isinstance(first_user, MockUser)
    first_user.clear_messages()

    bank(game, 5)

    assert any(
        packet["segments"][0]["asset"] == zombie_audio.SOUND_FINAL_HEARTBEAT
        for packet in audio_packets(first_user, kind="sfx")
    )
    first_user.clear_messages()
    bank(game, 0)

    assert game.status == "finished"
    assert not game.active_audio
    assert any(
        packet["family"] == zombie_audio.SOUND_WIN_ROAR_FAMILY
        for packet in audio_packets(first_user, kind="sfx")
    )


def test_tiebreak_uses_a_distinct_double_heartbeat_cue() -> None:
    game = make_game(player_count=3, target_score=5)
    listener = game.get_user(game.players[0])
    assert isinstance(listener, MockUser)
    bank(game, 5)
    bank(game, 5)
    listener.clear_messages()

    bank(game, 0)

    heartbeat = next(
        packet
        for packet in audio_packets(listener, kind="sfx")
        if packet["segments"][0]["asset"] == zombie_audio.SOUND_FINAL_HEARTBEAT
    )
    assert len(heartbeat["segments"]) == 2
    assert heartbeat["segments"][0]["next_start_ratio"] == (
        zombie_audio.FINAL_HEARTBEAT_NEXT_RATIO
    )


def test_wandering_zombie_is_one_continuous_listener_relative_passby() -> None:
    game = make_game()
    first, second = game.players
    first_user = game.get_user(first)
    second_user = game.get_user(second)
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    first_user.clear_messages()
    second_user.clear_messages()
    route = zombie_audio.WANDER_WORLD_ROUTES[0]
    steps = list(zombie_audio.SOUND_WANDER_STEPS[: zombie_audio.WANDER_STEP_COUNT])
    growl = zombie_audio.SOUND_WANDER_GROWLS[0]

    with (
        patch(
            "server.games.zombiedice.game.random.choice",
            side_effect=[route, growl],
        ),
        patch("server.games.zombiedice.game.random.sample", return_value=steps),
    ):
        game._play_wandering_zombie()

    first_passby = audio_packets(first_user, kind="sfx")[0]
    second_passby = audio_packets(second_user, kind="sfx")[0]
    assert [segment["asset"] for segment in first_passby["segments"]] == [
        *steps,
        growl,
    ]
    assert all(
        segment["destination_position"] is not None
        for segment in first_passby["segments"]
    )
    assert all(
        current["destination_position"] == following["position"]
        for current, following in zip(
            first_passby["segments"],
            first_passby["segments"][1:],
        )
    )
    assert all(
        segment["next_start_ratio"] == zombie_audio.WANDER_STEP_NEXT_RATIO
        for segment in first_passby["segments"][:-1]
    )
    assert all(
        segment["attenuation"] == zombie_audio.SCENE_ATTENUATION.to_packet()
        for segment in first_passby["segments"]
    )
    assert (
        first_passby["segments"][0]["position"]
        != (second_passby["segments"][0]["position"])
    )
    growl_origin = zombie_audio.interpolate_world_position(
        *route,
        zombie_audio.WANDER_STEP_ROUTE_FRACTION,
    )
    assert first_passby["segments"][-1]["position"] == list(
        zombie_audio.listener_relative_scene_position(growl_origin, 0, 2)
    )
    assert first_passby["segments"][-1]["destination_position"] == list(
        zombie_audio.listener_relative_scene_position(route[1], 0, 2)
    )


def test_due_wandering_zombie_plays_once_and_reschedules() -> None:
    game = make_game()
    listener = game.get_user(game.players[0])
    assert isinstance(listener, MockUser)
    listener.clear_messages()
    game.next_ambient_event_tick = game.sound_scheduler_tick

    with patch(
        "server.games.zombiedice.game.random.randint",
        return_value=zombie_audio.WANDER_INTERVAL_TICKS[0],
    ):
        game._maybe_play_ambient_event()

    assert len(audio_packets(listener, kind="sfx")) == 1
    assert game.next_ambient_event_tick == (
        game.sound_scheduler_tick + zombie_audio.WANDER_INTERVAL_TICKS[0]
    )


def test_reconnect_replays_ambience_without_duplicating_persistent_state() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    state_count = len(game.active_audio)
    user.clear_messages()

    game.attach_user(player.id, user, session_handover=True)

    assert len(game.active_audio) == state_count
    assert len(audio_packets(user, kind="ambience")) == len(
        zombie_audio.AMBIENCE_SOURCES
    )


def test_registration_metadata_and_defaults() -> None:
    assert GameRegistry.get("zombiedice") is ZombieDiceGame
    assert ZombieDiceGame.get_name() == "Zombie Dice"
    assert ZombieDiceGame.get_name_key() == "game-name-zombiedice"
    assert ZombieDiceGame.get_category() == "dice"
    assert ZombieDiceGame.get_min_players() == 2
    assert ZombieDiceGame.get_max_players() == 8
    assert ZombieDiceGame.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]
    assert ZombieDiceOptions().target_score == 13


@pytest.mark.parametrize("target", [4, 51])
def test_target_score_is_validated_even_when_state_is_constructed_directly(
    target: int,
) -> None:
    game = make_game(start=False, target_score=target)
    assert (
        "zombiedice-error-target-score-range",
        {"value": target, "min": 5, "max": 50},
    ) in game.prestart_validate()


def test_official_dice_composition_and_faces() -> None:
    assert DICE_BY_COLOR == {GREEN: 6, YELLOW: 4, RED: 3}
    assert DicePool.full().total == 13
    assert FACE_DISTRIBUTIONS[GREEN].count(BRAIN) == 3
    assert FACE_DISTRIBUTIONS[GREEN].count(FOOTPRINT) == 2
    assert FACE_DISTRIBUTIONS[GREEN].count(SHOTGUN) == 1
    assert FACE_DISTRIBUTIONS[YELLOW].count(BRAIN) == 2
    assert FACE_DISTRIBUTIONS[YELLOW].count(FOOTPRINT) == 2
    assert FACE_DISTRIBUTIONS[YELLOW].count(SHOTGUN) == 2
    assert FACE_DISTRIBUTIONS[RED].count(BRAIN) == 1
    assert FACE_DISTRIBUTIONS[RED].count(FOOTPRINT) == 2
    assert FACE_DISTRIBUTIONS[RED].count(SHOTGUN) == 3


def test_draw_colors_is_uniform_without_replacement_and_mutates_the_cup() -> None:
    class LowestPick:
        @staticmethod
        def randrange(stop: int) -> int:
            assert stop > 0
            return 0

    cup = DicePool.full()
    assert draw_colors(cup, 3, LowestPick()) == [GREEN, GREEN, GREEN]
    assert cup == DicePool(green=3, yellow=4, red=3)
    assert draw_colors(cup, 0, LowestPick()) == []


def test_pool_rejects_invalid_colors_counts_and_overdraws() -> None:
    with pytest.raises(ValueError):
        DicePool(green=-1)
    with pytest.raises(ValueError):
        DicePool(yellow=True)

    pool = DicePool(green=1)
    with pytest.raises(ValueError):
        pool.add("blue")
    with pytest.raises(ValueError):
        pool.add(GREEN, -1)
    with pytest.raises(ValueError):
        pool.remove(GREEN, 2)
    with pytest.raises(ValueError):
        draw_colors(pool, 2)


def test_start_randomizes_once_then_establishes_fixed_order_and_clean_state() -> None:
    game = make_game(player_count=3)
    assert game.status == "playing"
    assert game.round == 1
    assert game.match_order_ids == ["p1", "p2", "p3"]
    assert game.turn_player_ids == game.match_order_ids
    assert game.current_player is game.players[0]
    assert game._team_manager.team_mode == "individual"
    assert all(game.get_player_score(player) == 0 for player in game.players)
    assert game.cup == DicePool.full()
    assert game._turn_dice_are_complete()
    assert game.players[0].turns_taken == 1
    assert game.players[1].turns_taken == 0


def test_first_safe_roll_preserves_every_die_and_opens_stop_choice() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)

    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    assert game.has_rolled
    assert game.turn_brains == 1
    assert game.footprints.total == 1
    assert game.brain_dice.total == 1
    assert game.shotgun_dice.total == 1
    assert game.cup.total == 10
    assert game._turn_dice_are_complete()
    assert game._is_bank_enabled(player) is None
    assert game._is_bank_hidden(player) is Visibility.VISIBLE


def test_safe_roll_announcement_reports_results_without_repeating_totals() -> None:
    game = make_game()
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_before = len(actor_user.get_spoken_messages())
    observer_before = len(observer_user.get_spoken_messages())

    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    actor_messages = actor_user.get_spoken_messages()[actor_before:]
    observer_messages = observer_user.get_spoken_messages()[observer_before:]
    assert len(actor_messages) == len(observer_messages) == 1
    assert actor_messages[0].startswith("You roll: ")
    assert observer_messages[0].startswith("Player1 rolls: ")
    for face in ("brain", "footprint", "shotgun"):
        assert face in actor_messages[0]
        assert face in observer_messages[0]
    assert all("turn total" not in message.lower() for message in actor_messages)


def test_stopping_with_zero_brains_is_legal_after_a_safe_roll() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    play_roll(game, (FOOTPRINT, FOOTPRINT, SHOTGUN))
    assert game.turn_brains == 0

    game.execute_action(player, "bank")

    assert game.get_player_score(player) == 0
    assert game.current_player is game.players[1]


def test_cannot_stop_before_first_roll() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    assert game._is_bank_enabled(player) == "zombiedice-error-roll-before-stopping"
    assert game._is_bank_hidden(player) is Visibility.HIDDEN


def test_footprints_are_rerolled_and_only_missing_dice_are_drawn() -> None:
    game = make_game()
    play_roll(game, (FOOTPRINT, FOOTPRINT, BRAIN))
    cup_before = game.cup.total
    assert game.footprints.total == 2

    play_roll(game, (BRAIN, BRAIN, BRAIN))

    assert game.cup.total == cup_before - 1
    assert game.footprints.total == 0
    assert game.brain_dice.total == 4
    assert game.turn_brains == 4
    assert game._turn_dice_are_complete()


def test_three_footprints_reroll_without_drawing_from_the_cup() -> None:
    game = make_game()
    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))
    cup_before = game.cup.copy()

    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))

    assert game.cup == cup_before
    assert game.footprints.total == 3
    assert game._turn_dice_are_complete()


def test_low_cup_recycles_only_physical_brain_dice_and_keeps_turn_total() -> None:
    game = make_game()
    game.cup = DicePool(green=1)
    game.footprints = DicePool(yellow=1)
    game.brain_dice = DicePool(green=5, yellow=3, red=1)
    game.shotgun_dice = DicePool(red=2)
    game.turn_brains = 12
    game.has_rolled = True
    assert game._turn_dice_are_complete()

    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))

    assert game.turn_brains == 12
    assert game.brain_dice.total == 0
    assert game.shotgun_dice == DicePool(red=2)
    assert game.cup.total == 8
    assert game.footprints.total == 3
    assert game._turn_dice_are_complete()


def test_cup_refills_below_three_even_when_it_can_supply_the_required_draw() -> None:
    game = make_game()
    game.cup = DicePool(green=1, red=1)
    game.footprints = DicePool(yellow=2)
    game.brain_dice = DicePool(green=5, yellow=2)
    game.shotgun_dice = DicePool(red=2)
    game.turn_brains = 7
    game.has_rolled = True
    assert game._turn_dice_are_complete()

    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))

    assert game.cup.total == 8
    assert game.brain_dice.total == 0
    assert game.turn_brains == 7


def test_cup_does_not_refill_while_three_dice_remain() -> None:
    game = make_game()
    game.cup = DicePool(green=1, yellow=1, red=1)
    game.footprints = DicePool(yellow=2)
    game.brain_dice = DicePool(green=5, yellow=1)
    game.shotgun_dice = DicePool(red=2)
    game.turn_brains = 6
    game.has_rolled = True
    assert game._turn_dice_are_complete()

    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))

    assert game.cup.total == 2
    assert game.brain_dice.total == 6
    assert game.turn_brains == 6


def test_low_cup_refills_before_rerolling_three_footprints() -> None:
    game = make_game()
    game.cup = DicePool(red=2)
    game.footprints = DicePool(green=3)
    game.brain_dice = DicePool(green=3, yellow=4)
    game.shotgun_dice = DicePool(red=1)
    game.turn_brains = 7
    game.has_rolled = True
    assert game._turn_dice_are_complete()

    play_roll(game, (FOOTPRINT, FOOTPRINT, FOOTPRINT))

    assert game.cup == DicePool(green=3, yellow=4, red=2)
    assert game.brain_dice.total == 0
    assert game.footprints == DicePool(green=3)
    assert game.turn_brains == 7


def test_third_or_later_shotgun_busts_and_loses_brains_from_same_roll() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    game.cup = DicePool(green=5, yellow=3, red=2)
    game.footprints = DicePool()
    game.brain_dice = DicePool(green=1)
    game.shotgun_dice = DicePool(yellow=1, red=1)
    game.turn_brains = 1
    game.has_rolled = True
    assert game._turn_dice_are_complete()

    play_roll(game, (BRAIN, SHOTGUN, SHOTGUN))

    assert player.busts == 1
    assert player.brains_banked == 0
    assert game.get_player_score(player) == 0
    assert game.current_player is game.players[1]


def test_busting_shotgun_total_is_not_clamped_to_three() -> None:
    game = make_game()
    game.cup = DicePool(green=5, yellow=4, red=1)
    game.brain_dice = DicePool()
    game.footprints = DicePool()
    game.shotgun_dice = DicePool(green=1, red=2)
    game.turn_brains = 0
    game.has_rolled = True
    # This is intentionally not a reachable decision state because a third
    # shotgun would already have ended the turn. Resolve directly to verify the
    # result accumulator itself never truncates a multi-shotgun roll.
    with patch.object(game, "_turn_dice_are_complete", return_value=True):
        play_roll(game, (SHOTGUN, SHOTGUN, SHOTGUN))
    messages = game.get_user(game.players[0]).get_spoken_messages()
    assert any("6 shotguns" in message for message in messages)


def test_banking_updates_score_and_player_statistics() -> None:
    game = make_game()
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    bank(game, 4)
    assert game.get_player_score(player) == 4
    assert player.brains_banked == 4
    assert player.best_turn == 4


def test_unbanked_brains_never_trigger_the_final_round() -> None:
    game = make_game(target_score=5)
    game.turn_brains = 8
    game.has_rolled = True
    game.refresh_menus()
    assert not game.final_round_active
    assert game.status == "playing"


def test_triggering_player_only_leaves_later_seats_in_the_final_round() -> None:
    game = make_game(player_count=3, target_score=5)
    trigger = game.current_player
    assert trigger is game.players[0]
    bank(game, 5)

    assert game.final_round_active
    assert game.final_round_trigger_id == trigger.id
    assert game.current_player is game.players[1]

    bank(game, 0)
    assert game.current_player is game.players[2]
    bank(game, 0)
    assert game.winner_id == trigger.id
    assert game.final_round_trigger_id == ""
    assert game.status == "finished"


def test_final_round_warning_is_pluralized_only_for_players_who_remain() -> None:
    game = make_game(player_count=3, target_score=5)
    first_user = game.get_user(game.players[0])
    assert isinstance(first_user, MockUser)
    first_before = len(first_user.get_spoken_messages())
    bank(game, 5)
    assert any(
        message == "You reach 5 brains. 2 players remain in the final round."
        for message in first_user.get_spoken_messages()[first_before:]
    )

    game = make_game(player_count=3, target_score=5)
    bank(game, 0)
    second = game.current_player
    assert second is game.players[1]
    second_user = game.get_user(second)
    assert isinstance(second_user, MockUser)
    second_before = len(second_user.get_spoken_messages())
    bank(game, 5)
    assert any(
        message == "You reach 5 brains. 1 player remains in the final round."
        for message in second_user.get_spoken_messages()[second_before:]
    )


def test_last_seat_trigger_finishes_the_round_immediately() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 0)
    bank(game, 0)
    last = game.current_player
    assert last is game.players[2]
    users = [game.get_user(player) for player in game.players]
    before = [len(user.get_spoken_messages()) for user in users]
    bank(game, 5)
    assert game.winner_id == last.id
    assert game.status == "finished"
    new_messages = [
        message
        for user, start in zip(users, before, strict=True)
        for message in user.get_spoken_messages()[start:]
    ]
    assert not any("final round" in message.lower() for message in new_messages)
    assert not any("0 turns" in message.lower() for message in new_messages)


def test_last_seat_target_tie_starts_tiebreak_without_zero_turn_warning() -> None:
    game = make_game(player_count=3, target_score=5)
    first = game.players[0]
    set_score(game, first, 5)
    bank(game, 0)
    bank(game, 0)
    last = game.current_player
    assert last is game.players[2]
    users = [game.get_user(player) for player in game.players]
    before = [len(user.get_spoken_messages()) for user in users]

    bank(game, 5)

    assert game.status == "playing"
    assert game.tiebreaker_player_ids == [first.id, last.id]
    assert game.tiebreak_round == 1
    new_messages = [
        message
        for user, start in zip(users, before, strict=True)
        for message in user.get_spoken_messages()[start:]
    ]
    assert any("Tiebreak 1" in message for message in new_messages)
    assert not any("final round" in message.lower() for message in new_messages)
    assert not any("0 turns" in message.lower() for message in new_messages)


def test_later_player_can_overtake_the_final_round_trigger() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 5)
    overtaker = game.current_player
    assert overtaker is game.players[1]
    bank(game, 6)
    bank(game, 0)
    assert game.winner_id == overtaker.id


def test_tie_uses_only_leader_ids_without_mutating_player_roles() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 5)
    bank(game, 5)
    bank(game, 0)

    assert not game.final_round_active
    assert game.final_round_trigger_id == ""
    assert game.tiebreaker_player_ids == ["p1", "p2"]
    assert game.turn_player_ids == ["p1", "p2"]
    assert game.current_player is game.players[0]
    assert all(not player.is_spectator for player in game.players)
    assert game.players[2] in game.get_active_players()


def test_repeated_ties_continue_until_one_leader_wins() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 5)
    bank(game, 5)
    bank(game, 0)
    assert game.tiebreak_round == 1

    bank(game, 1)
    bank(game, 1)
    assert game.tiebreak_round == 2
    assert game.status == "playing"
    assert game.tiebreaker_player_ids == ["p1", "p2"]

    winner = game.current_player
    bank(game, 1)
    bank(game, 0)
    assert game.winner_id == winner.id
    assert game.status == "finished"


def test_completed_normal_round_returns_to_fixed_first_seat() -> None:
    game = make_game(player_count=3, target_score=50)
    bank(game, 0)
    bank(game, 0)
    bank(game, 0)
    assert game.round == 2
    assert game.current_player is game.players[0]
    assert game.turn_player_ids == game.match_order_ids


def test_save_restore_preserves_midturn_and_final_round_state() -> None:
    game = make_game(player_count=3, target_score=5)
    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))
    game.final_round_active = True
    game.final_round_trigger_id = game.players[2].id
    restored = ZombieDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert isinstance(restored.cup, DicePool)
    assert isinstance(restored.last_roll[0], RollResult)
    assert restored.turn_brains == 1
    assert restored.footprints.total == 1
    assert restored.shotgun_dice.total == 1
    assert restored.final_round_active
    assert restored.final_round_trigger_id == "p3"
    assert restored._turn_dice_are_complete()


def test_save_restore_preserves_an_unresolved_roll_without_revealing_it_early() -> None:
    game = make_game()
    start_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))
    assert game.last_roll == []
    assert game.active_sequences[0].current_index == 1

    restored = ZombieDiceGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.last_roll == []
    assert not restored.has_rolled
    assert len(restored.active_sequences) == 1
    assert restored.active_sequences[0].current_index == 1

    finish_active_sequences(restored)

    assert not restored.active_sequences
    assert restored.has_rolled
    assert [result.face for result in restored.last_roll] == [
        BRAIN,
        FOOTPRINT,
        SHOTGUN,
    ]
    assert restored._turn_dice_are_complete()


def test_current_turn_status_exposes_all_public_physical_state() -> None:
    game = make_game()
    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))
    viewer = game.players[1]
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)
    items = game._build_turn_status(viewer, user)
    text = " ".join(item.text for item in items)
    assert text.startswith("Player1's turn")
    assert "player's turn" not in text
    assert "1 brain, 1 shotgun, and 1 footprint" in text
    assert "Cup: 10 dice" in text
    assert "green" not in next(item.text for item in items if item.id == "cup")
    assert "Footprints to reroll" in text
    footprint_text = next(item.text for item in items if item.id == "footprints")
    assert footprint_text.endswith(" die.")
    assert "Brain dice set aside" in text
    assert "Shotgun dice set aside" in text
    assert "Last roll" in text


def test_touch_clients_receive_information_and_orientation_actions_in_order() -> None:
    game = make_game(touch_indexes={0})
    player = game.players[0]
    standard = game.get_action_set(player, "standard")
    assert standard is not None
    visible = [
        resolved.action.id for resolved in standard.get_visible_actions(game, player)
    ]
    expected = [
        "check_turn_totals",
        "review_turn",
        "review_table",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]
    assert [
        action_id for action_id in standard._order if action_id in expected
    ] == expected
    assert set(expected).issubset(visible)


def test_desktop_information_actions_remain_keybind_or_actions_menu_utilities() -> None:
    game = make_game()
    player = game.players[0]
    assert game._is_public_info_hidden(player) is Visibility.HIDDEN
    assert "c" in game._keybinds
    assert "v" in game._keybinds
    assert "shift+v" in game._keybinds


def test_check_turn_totals_speaks_without_opening_a_status_view() -> None:
    game = make_game()
    current, viewer = game.players
    game.turn_brains = 2
    game.brain_dice = DicePool(green=2)
    game.shotgun_dice = DicePool(yellow=1)
    game.footprints = DicePool(red=1)
    game.cup = DicePool(green=4, yellow=3, red=2)
    assert game._turn_dice_are_complete()

    current_user = game.get_user(current)
    viewer_user = game.get_user(viewer)
    assert isinstance(current_user, MockUser)
    assert isinstance(viewer_user, MockUser)
    current_before = len(current_user.get_spoken_messages())
    viewer_before = len(viewer_user.get_spoken_messages())

    game.execute_action(current, "check_turn_totals")
    game.execute_action(viewer, "check_turn_totals")

    assert current_user.get_spoken_messages()[current_before:] == [
        "You: 2 brains, 1 shotgun, and 1 footprint."
    ]
    assert viewer_user.get_spoken_messages()[viewer_before:] == [
        "Player1: 2 brains, 1 shotgun, and 1 footprint."
    ]
    assert getattr(current_user, "active_status_box", None) is None
    assert getattr(viewer_user, "active_status_box", None) is None


def test_off_turn_roll_reports_standard_not_your_turn_reason() -> None:
    game = make_game()
    off_turn = game.players[1]
    user = game.get_user(off_turn)
    assert isinstance(user, MockUser)
    game.execute_action(off_turn, "roll")
    assert any(
        "not your turn" in message.lower() for message in user.get_spoken_messages()
    )


def test_roll_is_persistent_but_bank_is_visible_only_to_the_current_player() -> None:
    game = make_game(touch_indexes={0, 1})
    current, off_turn = game.players

    assert game._is_turn_action_hidden(current) is Visibility.VISIBLE
    assert game._is_turn_action_hidden(off_turn) is Visibility.VISIBLE
    assert game._is_bank_hidden(current) is Visibility.HIDDEN
    assert game._is_bank_hidden(off_turn) is Visibility.HIDDEN

    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    assert game._is_bank_hidden(current) is Visibility.VISIBLE
    assert game._is_bank_hidden(off_turn) is Visibility.HIDDEN
    off_turn_roll = game.resolve_action(off_turn, game.find_action(off_turn, "roll"))
    assert off_turn_roll.label == "Roll 3 dice"
    assert (
        off_turn_roll.description
        == "Draw three hidden dice from the cup and roll them."
    )


def test_touch_bank_focuses_persistent_roll_anchor_for_the_actor() -> None:
    game = make_game(touch_indexes={0})
    actor, next_player = game.players
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    game.execute_action(actor, "bank")
    game.flush_menus()

    assert game.current_player is next_player
    assert actor_user.menus["turn_menu"]["selection_id"] == "roll"
    item_ids = [item.id for item in actor_user.menus["turn_menu"]["items"]]
    assert item_ids[0] == "roll"
    assert "bank" not in item_ids


def test_desktop_bank_does_not_request_a_focus_jump() -> None:
    game = make_game()
    actor = game.players[0]
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))

    game.execute_action(actor, "bank")
    game.flush_menus()

    assert actor_user.menus["turn_menu"]["selection_id"] is None


def test_roll_action_id_survives_safe_repaint_for_focus_stability() -> None:
    game = make_game(touch_indexes={0})
    player = game.players[0]
    before = game.resolve_action(player, game.find_action(player, "roll"))
    play_roll(game, (BRAIN, FOOTPRINT, SHOTGUN))
    after = game.resolve_action(player, game.find_action(player, "roll"))
    assert before.action.id == after.action.id == "roll"
    assert "1 brain" in after.label


def test_table_status_uses_names_stable_ids_and_current_round_order() -> None:
    game = make_game(player_count=3)
    viewer = game.players[1]
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)

    items = game._build_table_status(viewer, user)
    by_id = {item.id: item.text for item in items}

    assert by_id["turn_order"] == "Turn order: Player1, Player2, and Player3."
    assert by_id["current_turn"] == "Player1's turn."
    assert by_id["score:p1"] == "Player1: 0 brains."
    assert by_id["score:p2"] == "You: 0 brains."
    assert all("{ $" not in item.text for item in items)


def test_tiebreak_status_has_one_contextual_round_and_only_finalist_order() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 5)
    bank(game, 5)
    bank(game, 0)
    user = game.get_user(game.players[2])
    assert isinstance(user, MockUser)

    items = game._build_table_status(game.players[2], user)
    by_id = {item.id: item.text for item in items}

    assert by_id["table_header"] == "Zombie Dice — target: 5 brains."
    assert by_id["phase"].startswith("Tiebreak 1:")
    assert by_id["turn_order"] == "Turn order: Player1 and Player2."


def test_final_round_status_interpolates_the_trigger_name() -> None:
    game = make_game(player_count=3, target_score=5)
    bank(game, 5)
    viewer = game.players[2]
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)

    by_id = {item.id: item.text for item in game._build_table_status(viewer, user)}

    assert by_id["phase"] == "Final round — Player1 reached the target."


def test_vietnamese_status_interpolates_player_names_naturally() -> None:
    game = make_game()
    viewer = game.players[1]
    user = game.get_user(viewer)
    assert isinstance(user, MockUser)
    user.set_locale("vi")

    turn_text = " ".join(item.text for item in game._build_turn_status(viewer, user))
    table_text = " ".join(item.text for item in game._build_table_status(viewer, user))

    assert "Lượt của Player1" in turn_text
    assert "Lượt của Player1" in table_text
    assert "Player1: 0 não" in table_text


def test_initial_next_roll_bust_probability_matches_exact_official_dice() -> None:
    metrics = next_roll_metrics(
        BotObservation(
            cup=DicePool.full(),
            footprints=DicePool(),
            brain_dice=DicePool(),
            shotguns=0,
            turn_brains=0,
            banked_score=0,
            target_score=13,
            score_to_beat=0,
            final_round_active=False,
            in_tiebreaker=False,
            has_rolled=False,
        )
    )
    assert math.isclose(metrics.bust_probability, 94 / 3861, rel_tol=1e-12)
    assert metrics.expected_safe_brains > 0


def test_bot_metrics_apply_refill_before_evaluating_the_draw() -> None:
    observation = BotObservation(
        cup=DicePool(red=2),
        footprints=DicePool(green=2),
        brain_dice=DicePool(green=4, yellow=4, red=1),
        shotguns=0,
        turn_brains=9,
        banked_score=0,
        target_score=13,
        score_to_beat=0,
        final_round_active=False,
        in_tiebreaker=False,
        has_rolled=True,
    )
    metrics = next_roll_metrics(observation)
    assert math.isclose(metrics.bust_probability, 7 / 792, rel_tol=1e-12)
    assert metrics.expected_safe_brains >= 0


def test_bot_looks_past_a_marginal_next_roll_when_followup_is_favorable() -> None:
    observation = BotObservation(
        cup=DicePool(green=5, yellow=3),
        footprints=DicePool(green=1),
        brain_dice=DicePool(yellow=1, red=2),
        shotguns=1,
        turn_brains=12,
        banked_score=0,
        target_score=50,
        score_to_beat=0,
        final_round_active=False,
        in_tiebreaker=False,
        has_rolled=True,
    )
    metrics = next_roll_metrics(observation)
    assert metrics.expected_safe_brains <= (
        observation.turn_brains * metrics.bust_probability
    )
    assert choose_action(observation) == "roll"


def test_bot_rolls_first_banks_a_reached_target_and_handles_final_scores() -> None:
    base = {
        "cup": DicePool.full(),
        "footprints": DicePool(),
        "brain_dice": DicePool(),
        "shotguns": 0,
        "banked_score": 10,
        "target_score": 13,
        "score_to_beat": 14,
        "in_tiebreaker": False,
    }
    assert (
        choose_action(
            BotObservation(
                **base,
                turn_brains=0,
                final_round_active=False,
                has_rolled=False,
            )
        )
        == "roll"
    )
    assert (
        choose_action(
            BotObservation(
                **base,
                turn_brains=3,
                final_round_active=False,
                has_rolled=True,
            )
        )
        == "bank"
    )
    assert (
        choose_action(
            BotObservation(
                **base,
                turn_brains=4,
                final_round_active=True,
                has_rolled=True,
            )
        )
        == "bank"
    )
    assert (
        choose_action(
            BotObservation(
                **base,
                turn_brains=3,
                final_round_active=True,
                has_rolled=True,
            )
        )
        == "roll"
    )
    assert (
        choose_action(
            BotObservation(
                **base,
                turn_brains=5,
                final_round_active=True,
                has_rolled=True,
            )
        )
        == "bank"
    )


def test_bot_pushes_for_the_target_when_a_later_opponent_can_end_the_match() -> None:
    base = {
        "cup": DicePool(green=5, yellow=3, red=2),
        "footprints": DicePool(),
        "brain_dice": DicePool(green=1),
        "shotguns": 2,
        "turn_brains": 1,
        "banked_score": 8,
        "target_score": 13,
        "score_to_beat": 10,
        "final_round_active": False,
        "in_tiebreaker": False,
        "has_rolled": True,
    }
    assert choose_action(BotObservation(**base)) == "bank"
    assert choose_action(BotObservation(**base, later_opponent_score=10)) == "roll"


def test_bot_observation_only_treats_later_round_seats_as_endgame_threats() -> None:
    game = make_game(player_count=3, target_score=13)
    first, second, third = game.players
    assert isinstance(first, ZombieDicePlayer)
    assert isinstance(second, ZombieDicePlayer)
    assert isinstance(third, ZombieDicePlayer)
    set_score(game, first, 12)
    set_score(game, second, 4)
    set_score(game, third, 10)

    game.turn_index = 1
    observation = game._bot_observation(second)

    assert observation.score_to_beat == 12
    assert observation.later_opponent_score == 10


def test_bot_cadence_is_deliberate_and_serialized() -> None:
    game = make_game(bots=True)
    player = game.current_player
    assert isinstance(player, ZombieDicePlayer)
    assert BOT_THINK_TICKS[0] <= player.bot_think_ticks <= BOT_THINK_TICKS[1]
    restored = ZombieDiceGame.from_json(game.to_json())
    assert restored.current_player is not None
    assert restored.current_player.bot_think_ticks == player.bot_think_ticks


@pytest.mark.parametrize("seed", range(3))
def test_two_bot_match_reaches_a_unique_winner(seed: int) -> None:
    random.seed(seed)
    game = make_game(bots=True, target_score=5)
    for _ in range(20000):
        if game.winner_id:
            break
        current = game.current_player
        if current:
            current.bot_think_ticks = 0
        game.on_tick()
    assert game.winner_id in {"p1", "p2"}


def test_results_use_immutable_ids_and_complete_scores() -> None:
    game = make_game(target_score=5)
    bank(game, 5)
    bank(game, 0)
    result = game._last_game_result
    assert result is not None
    assert result.custom_data["winner_ids"] == ["p1"]
    assert result.custom_data["final_scores"] == {"Player1": 5, "Player2": 0}
    competitors = result.custom_data["rating_competitors"]
    assert competitors == [
        {"player_ids": ["p1"], "rank": 0},
        {"player_ids": ["p2"], "rank": 1},
    ]
    assert set(result.custom_data["player_stats"]) == {"p1", "p2"}


def test_result_lines_use_competition_ranks_for_tied_scores() -> None:
    game = make_game(player_count=3, target_score=50)
    set_score(game, game.players[0], 8)
    set_score(game, game.players[1], 8)
    set_score(game, game.players[2], 3)

    result = game.build_game_result()
    assert [entry["rank"] for entry in result.custom_data["rankings"]] == [1, 1, 3]
    lines = game.format_end_screen(result, "en")
    assert lines[-3:] == [
        "1. Player1: 8 brains.",
        "1. Player2: 8 brains.",
        "3. Player3: 3 brains.",
    ]


def test_english_and_vietnamese_locales_and_manuals_are_paired() -> None:
    en = ROOT / "server" / "locales" / "en" / "zombiedice.ftl"
    vi = ROOT / "server" / "locales" / "vi" / "zombiedice.ftl"
    assert en.exists() and vi.exists()
    assert locale_keys(en) == locale_keys(vi)
    assert (
        ROOT / "server" / "documentation" / "content" / "en" / "games" / "zombiedice.md"
    ).exists()
    assert (
        ROOT / "server" / "documentation" / "content" / "vi" / "games" / "zombiedice.md"
    ).exists()


@pytest.mark.parametrize("seed", range(10))
def test_random_legal_turns_never_lose_or_duplicate_dice(seed: int) -> None:
    random.seed(seed)
    game = make_game()
    for _ in range(100):
        if game.current_player is not game.players[0]:
            break
        game.execute_action(game.players[0], "roll")
        finish_active_sequences(game)
        assert game._turn_dice_are_complete()
        assert has_complete_die_set(
            game.cup,
            game.footprints,
            game.brain_dice,
            game.shotgun_dice,
        )
        if game.current_player is not game.players[0]:
            break
    else:
        pytest.fail("A legal Zombie Dice turn did not terminate within 100 rolls")


def test_dice_pool_color_iteration_is_stable_for_accessible_status() -> None:
    assert COLORS == (GREEN, YELLOW, RED)
