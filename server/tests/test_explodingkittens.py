"""Rule, accessibility, persistence, and bot tests for Exploding Kittens."""

from collections import Counter
import math
from pathlib import Path
import random
import struct

import pytest

from server.games.explodingkittens.cards import (
    ATTACK,
    BEARD_CAT,
    CARD_COUNTS,
    DEFUSE,
    EXPLODING_KITTEN,
    FAVOR,
    NOPE,
    SEE_FUTURE,
    SHUFFLE,
    SKIP,
    ExplodingKittensCard,
    build_full_deck,
)
from server.games.explodingkittens.game import (
    AUDIO_DURATIONS_TICKS,
    CARD_PLAY_INTERVAL_DIVISOR,
    FAST_GAME_PLAYER_COUNTS,
    GAME_START_DELAY_TICKS,
    KITTEN_REVEAL_DELAY_TICKS,
    SOUND_ACTION_CANCELED,
    SOUND_ATTACK,
    SOUND_COMBO_MISS,
    SOUND_DEFUSE,
    SOUND_DRAWS,
    SOUND_EXPLOSIONS,
    SOUND_FUSE,
    SOUND_GAME_OVER,
    SOUND_GAME_START,
    SOUND_KITTEN_REVEAL,
    SOUND_MUSIC,
    SOUND_NOPES,
    SOUND_PLAYS,
    SOUND_REINSERT,
    SOUND_SEE_FUTURE,
    SOUND_SHUFFLES,
    SOUND_SKIP,
    SOUND_TURN,
    NOPE_WINDOW_TICKS,
    ExplodingKittensGame,
)
from server.games.explodingkittens.state import (
    PHASE_COMBO,
    PHASE_DEFUSE,
    PHASE_FAVOR_GIVE,
    PHASE_GAME_OVER,
    PHASE_NOPE,
    PHASE_NORMAL,
    PHASE_REINSERT,
    PHASE_REQUEST,
    PHASE_RESOLVING,
    PHASE_STARTING,
    PHASE_TARGET,
)
from server.games.registry import GameRegistry
from server.messages.localization import Localization
from server.ui.keybinds import KeybindState
from server.users.bot import Bot
from server.users.network_user import NetworkUser
from server.users.test_user import MockUser


ROOT = Path(__file__).resolve().parents[2]


def card(card_id: int, kind: str) -> ExplodingKittensCard:
    return ExplodingKittensCard(id=card_id, kind=kind)


def make_game(player_count: int = 2, *, touch: bool = False) -> ExplodingKittensGame:
    game = ExplodingKittensGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = MockUser(name, uuid=f"p{index + 1}")
        if touch:
            user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    return game


def make_network_game(player_count: int = 2) -> tuple[ExplodingKittensGame, list[NetworkUser]]:
    game = ExplodingKittensGame()
    game.setup_keybinds()
    users: list[NetworkUser] = []
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = NetworkUser(
            name,
            "en",
            connection=None,
            client_type="mobile",
            uuid=f"p{index + 1}",
        )
        users.append(user)
        game.add_player(name, user)
    game.host = "Player1"
    return game, users


def make_bot_game(player_count: int = 2) -> ExplodingKittensGame:
    game = ExplodingKittensGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Bot{index + 1}"
        user = Bot(name)
        player = game.create_player(user.uuid, name, is_bot=True)
        game.players.append(player)
        game.attach_user(player.id, user)
        game.setup_player_actions(player)
    game.host = game.players[0].name
    return game


def advance_until(game: ExplodingKittensGame, condition, max_ticks: int = 3000) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
        game.flush_menus()
    return condition()


def drain_sequences(game: ExplodingKittensGame) -> None:
    assert advance_until(game, lambda: not game.active_sequences)


def start_with_current(game: ExplodingKittensGame, index: int = 0) -> None:
    game.on_start()
    drain_sequences(game)
    game.current_player = game.players[index]
    game.phase = PHASE_NORMAL
    game.turns_remaining = 1
    game.attack_obligation = False
    game.refresh_menus()
    game.flush_menus()


def execute(game: ExplodingKittensGame, player, action_id: str) -> None:
    game._sync_turn_actions(player)
    game.execute_action(player, action_id)
    drain_sequences(game)


def execute_raw(game: ExplodingKittensGame, player, action_id: str) -> None:
    game._sync_turn_actions(player)
    game.execute_action(player, action_id)


def resolve_nope(game: ExplodingKittensGame) -> None:
    ExplodingKittensGame._resolve_nope_window(game)
    drain_sequences(game)


def speech(user) -> list[str]:
    if isinstance(user, MockUser):
        return user.get_spoken_messages()
    return [packet["text"] for packet in user.get_queued_messages() if packet.get("type") == "speak"]


def sound_names(user: MockUser) -> list[str]:
    return [message.data["name"] for message in user.messages if message.type == "play_sound"]


def network_menu_packets(user: NetworkUser) -> list[dict]:
    return [
        packet
        for packet in user.get_queued_messages()
        if packet.get("type") == "menu" and packet.get("menu_id") == "turn_menu"
    ]


def menu_ids(user: MockUser) -> list[str]:
    return [item.id for item in user.menus["turn_menu"]["items"]]


def locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if "=" in line and line[:1].isalnum()
    }


def ogg_duration_ticks(path: Path) -> int:
    """Read a Vorbis file's sample rate and final granule without extra codecs."""
    data = path.read_bytes()
    identification = data.find(b"\x01vorbis")
    assert identification >= 0, f"Missing Vorbis identification header: {path}"
    sample_rate = struct.unpack_from("<I", data, identification + 12)[0]
    offset = 0
    final_granule = 0
    while True:
        page = data.find(b"OggS", offset)
        if page < 0:
            break
        segment_count = data[page + 26]
        header_size = 27 + segment_count
        body_size = sum(data[page + 27 : page + header_size])
        granule = struct.unpack_from("<Q", data, page + 6)[0]
        if granule != 0xFFFFFFFFFFFFFFFF:
            final_granule = max(final_granule, granule)
        offset = page + header_size + body_size
    assert sample_rate > 0 and final_granule > 0, f"Invalid Vorbis timing: {path}"
    return math.ceil(final_granule * 20 / sample_rate)


def test_registration_metadata_and_scoreless_behavior() -> None:
    assert GameRegistry.get("explodingkittens") is ExplodingKittensGame
    assert ExplodingKittensGame.get_name() == "Exploding Kittens"
    assert ExplodingKittensGame.get_category() == "cards"
    assert ExplodingKittensGame.get_min_players() == 2
    assert ExplodingKittensGame.get_max_players() == 5
    assert ExplodingKittensGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]
    assert not ExplodingKittensGame().supports_score_actions()


def test_full_deck_has_exact_original_edition_composition() -> None:
    deck = build_full_deck()
    assert len(deck) == 56
    assert len({card.id for card in deck}) == 56
    assert Counter(card.kind for card in deck) == Counter(CARD_COUNTS)


@pytest.mark.parametrize(
    ("player_count", "deck_count", "removed_count"),
    [(2, 35, 5), (3, 29, 3), (4, 23, 1), (5, 16, 0)],
)
def test_official_setup_counts_and_card_conservation(
    player_count: int, deck_count: int, removed_count: int
) -> None:
    random.seed(100 + player_count)
    game = make_game(player_count)
    start_with_current(game)
    assert [len(player.hand) for player in game.players] == [8] * player_count
    assert all(sum(card.kind == DEFUSE for card in player.hand) == 1 for player in game.players)
    assert len(game.deck) == deck_count
    assert len(game.removed_cards) == removed_count
    assert sum(card.kind == EXPLODING_KITTEN for card in game.deck) == player_count - 1
    all_cards = game.deck + game.removed_cards + [held for player in game.players for held in player.hand]
    assert len(all_cards) == 56
    assert len({held.id for held in all_cards}) == 56


def test_fast_game_is_officially_limited_and_removes_one_third() -> None:
    game = make_game(2)
    game.options.fast_game = True
    random.seed(8)
    start_with_current(game)
    assert len(game.deck) == 24

    for player_count in FAST_GAME_PLAYER_COUNTS:
        valid = make_game(player_count)
        valid.options.fast_game = True
        assert valid.prestart_validate() == []
    invalid = make_game(4)
    invalid.options.fast_game = True
    assert invalid.prestart_validate() == ["explodingkittens-error-fast-game-player-count"]


def test_room_options_default_to_official_rules_and_validate_nope_time() -> None:
    game = make_game(2)
    assert game.options.advanced_combos
    assert game.options.nope_response_seconds == "10"
    for seconds in ("5", "10", "15", "20"):
        game.options.nope_response_seconds = seconds
        assert game.prestart_validate() == []
    game.options.nope_response_seconds = "30"
    assert game.prestart_validate() == ["explodingkittens-error-invalid-nope-response"]


def test_game_start_opens_after_ten_seconds_while_intro_can_keep_playing() -> None:
    game = make_game(2)
    game.on_start()
    assert game.phase == PHASE_STARTING
    assert game.deck == []
    assert all(not player.hand for player in game.players)
    assert game.is_sequence_gameplay_locked()

    assert GAME_START_DELAY_TICKS == 200
    assert GAME_START_DELAY_TICKS < AUDIO_DURATIONS_TICKS[SOUND_GAME_START]
    for _ in range(GAME_START_DELAY_TICKS - 1):
        game.on_tick()
    assert game.deck == []
    assert all(not player.hand for player in game.players)

    game.on_tick()
    assert game.deck
    assert all(len(player.hand) == 8 for player in game.players)
    assert not game.active_sequences
    assert game.phase == PHASE_NORMAL
    assert game.current_music == SOUND_MUSIC
    for player in game.players:
        user = game.get_user(player)
        sounds = sound_names(user)
        assert sounds[0] == SOUND_GAME_START
        assert sounds[1] in SOUND_SHUFFLES
        assert any(
            message.type == "play_music" and message.data["name"] == SOUND_MUSIC
            for message in user.messages
        )


def test_audio_assets_match_all_clients_and_measured_sequence_durations() -> None:
    custom_sounds = {
        SOUND_ACTION_CANCELED,
        SOUND_ATTACK,
        SOUND_COMBO_MISS,
        SOUND_DEFUSE,
        SOUND_FUSE,
        SOUND_GAME_OVER,
        SOUND_GAME_START,
        SOUND_KITTEN_REVEAL,
        SOUND_REINSERT,
        SOUND_SEE_FUTURE,
        SOUND_SKIP,
        *SOUND_DRAWS,
        *SOUND_EXPLOSIONS,
        *SOUND_NOPES,
        *SOUND_PLAYS,
        *SOUND_SHUFFLES,
    }
    assert all(
        sound.startswith("game_explodingkittens/")
        for sound in (*SOUND_DRAWS, *SOUND_PLAYS, *SOUND_SHUFFLES)
    )
    expected_names = {Path(sound).name for sound in custom_sounds}
    pack_roots = [ROOT / "client/sounds", ROOT / "web_client/sounds", ROOT / "mobile_client/sounds"]
    reference_bytes: dict[str, bytes] = {}
    for pack_root in pack_roots:
        custom_dir = pack_root / "game_explodingkittens"
        assert {path.name for path in custom_dir.glob("*.ogg")} == expected_names
        for name in expected_names:
            data = (custom_dir / name).read_bytes()
            if name in reference_bytes:
                assert data == reference_bytes[name]
            else:
                reference_bytes[name] = data

    for sound, expected_ticks in AUDIO_DURATIONS_TICKS.items():
        path = ROOT / "client/sounds" / sound
        assert path.exists(), sound
        assert ogg_duration_ticks(path) == expected_ticks


def test_combo_audio_is_nonblocking_and_uses_fast_ordered_starts() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(880, BEARD_CAT), card(881, BEARD_CAT)]
    target.hand = [card(882, SKIP)]

    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_880")
    execute(game, actor, "play_card_881")
    execute_raw(game, actor, "confirm_combo")

    assert game.phase == PHASE_NOPE
    assert game.pending_action.timer_ticks == NOPE_WINDOW_TICKS
    assert not game.is_sequence_gameplay_locked()
    assert not game.active_sequences
    first_sound = sound_names(game.get_user(actor))[-1]
    assert first_sound in SOUND_PLAYS
    scheduled_plays = [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in SOUND_PLAYS
    ]
    assert len(scheduled_plays) == 1
    target_tick, second_sound, *_ = scheduled_plays[0]
    assert second_sound in SOUND_PLAYS
    expected_interval = math.ceil(
        AUDIO_DURATIONS_TICKS[first_sound] / CARD_PLAY_INTERVAL_DIVISOR
    )
    assert target_tick == (
        game.sound_scheduler_tick + expected_interval - 1
    )
    assert expected_interval * 2 <= AUDIO_DURATIONS_TICKS[first_sound]
    assert any(
        text.startswith("You play a") and "pair against" in text
        for text in speech(game.get_user(actor))
    )
    initial_second_count = sound_names(game.get_user(actor)).count(second_sound)

    for _ in range(expected_interval - 1):
        game.on_tick()
    assert sound_names(game.get_user(actor)).count(second_sound) == initial_second_count
    game.on_tick()
    assert sound_names(game.get_user(actor)).count(second_sound) == initial_second_count + 1
    assert game.phase == PHASE_NOPE
    assert not game.is_sequence_gameplay_locked()


def test_nope_and_cancellation_both_resolve_immediately_without_locks() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(883, ATTACK)]
    responder.hand = [card(884, NOPE)]
    execute(game, actor, "play_card_883")

    for player in game.players:
        game.get_user(player).clear_messages()
    execute_raw(game, responder, "play_nope")
    assert game.phase == PHASE_NOPE
    assert game.pending_action.nope_count == 1
    assert game.pending_action.timer_ticks == NOPE_WINDOW_TICKS
    assert not game.active_sequences
    assert sound_names(game.get_user(actor))[0] in SOUND_NOPES

    ExplodingKittensGame._resolve_nope_window(game)
    assert game.phase == PHASE_NORMAL
    assert game.pending_action is None
    assert not game.is_sequence_gameplay_locked()
    assert sound_names(game.get_user(actor))[-1] == SOUND_ACTION_CANCELED
    assert any("canceled" in text for text in speech(game.get_user(actor)))


def test_normal_draw_is_private_and_ends_turn() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, observer = game.players
    actor.hand = []
    game.deck = [card(900, SKIP), card(901, ATTACK)]
    game.get_user(actor).clear_messages()
    game.get_user(observer).clear_messages()

    execute(game, actor, "draw_card")

    assert [held.kind for held in actor.hand] == [SKIP]
    assert game.current_player == observer
    assert any("You draw Skip" in text for text in speech(game.get_user(actor)))
    observer_speech = speech(game.get_user(observer))
    assert "Player1 draws a card." in observer_speech
    assert not any("Skip" in text or "now has" in text for text in observer_speech)


def test_normal_draw_sound_tts_state_and_turn_are_dispatched_together() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, observer = game.players
    actor.hand = []
    drawn = card(902, SKIP)
    game.deck = [drawn, card(903, ATTACK)]
    for player in game.players:
        game.get_user(player).clear_messages()

    execute_raw(game, actor, "draw_card")
    draw_sound = sound_names(game.get_user(actor))[0]
    assert draw_sound in SOUND_DRAWS
    assert actor.hand == [drawn]
    assert game.deck == [card(903, ATTACK)]
    assert game.current_player == observer
    assert SOUND_TURN in sound_names(game.get_user(observer))
    assert not game.active_sequences


@pytest.mark.parametrize(
    ("kind", "expected_sounds"),
    [
        (ATTACK, {SOUND_ATTACK}),
        (SKIP, {SOUND_SKIP}),
        (SHUFFLE, set(SOUND_SHUFFLES)),
        (SEE_FUTURE, {SOUND_SEE_FUTURE}),
    ],
)
def test_action_resolution_uses_its_expected_sound(
    kind: str,
    expected_sounds: set[str],
) -> None:
    game = make_game(2)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(904, kind)]
    game.deck = [card(905, SKIP), card(906, ATTACK), card(907, FAVOR)]
    execute(game, actor, "play_card_904")
    for player in game.players:
        game.get_user(player).clear_messages()

    ExplodingKittensGame._resolve_nope_window(game)
    assert game.phase == PHASE_NORMAL
    assert not game.is_sequence_gameplay_locked()
    assert not game.active_sequences
    assert sound_names(game.get_user(actor))[0] in expected_sounds


def test_attack_stacking_transfers_all_remaining_turns_plus_two() -> None:
    game = make_game(2)
    start_with_current(game)
    first, second = game.players
    first.hand = [card(910, ATTACK)]
    second.hand = [card(911, ATTACK)]

    execute(game, first, "play_card_910")
    assert game.phase == PHASE_NOPE
    resolve_nope(game)
    assert game.current_player == second
    assert game.turns_remaining == 2
    assert game.attack_obligation

    execute(game, second, "play_card_911")
    resolve_nope(game)
    assert game.current_player == first
    assert game.turns_remaining == 4

    game.current_player = second
    game.turns_remaining = 1
    game.attack_obligation = True
    second.hand = [card(912, ATTACK)]
    execute(game, second, "play_card_912")
    resolve_nope(game)
    assert game.current_player == first
    assert game.turns_remaining == 3


def test_skip_consumes_only_one_attacked_turn() -> None:
    game = make_game(2)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(920, SKIP)]
    game.turns_remaining = 2
    game.attack_obligation = True

    execute(game, actor, "play_card_920")
    resolve_nope(game)

    assert game.current_player == actor
    assert game.turns_remaining == 1
    assert game.attack_obligation


def test_odd_nope_chain_cancels_action_and_even_chain_restores_it() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(930, ATTACK), card(931, NOPE)]
    responder.hand = [card(932, NOPE)]

    execute(game, actor, "play_card_930")
    execute(game, responder, "play_nope")
    assert game.pending_action.nope_count == 1
    assert game.pending_action.timer_ticks == NOPE_WINDOW_TICKS
    resolve_nope(game)
    assert game.current_player == actor
    assert game.phase == PHASE_NORMAL

    actor.hand = [card(933, ATTACK), card(934, NOPE)]
    responder.hand = [card(935, NOPE)]
    execute(game, actor, "play_card_933")
    execute(game, responder, "play_nope")
    execute(game, actor, "play_nope")
    resolve_nope(game)
    assert game.current_player == responder
    assert game.turns_remaining == 2


def test_nope_chain_can_continue_repeatedly_and_resets_passes_and_timer() -> None:
    game = make_game(4)
    game.options.nope_response_seconds = "5"
    start_with_current(game)
    actor, second, third, fourth = game.players
    actor.hand = [card(936, ATTACK), card(937, NOPE)]
    second.hand = [card(938, NOPE)]
    third.hand = [card(939, NOPE)]
    fourth.hand = [card(940, NOPE)]

    execute(game, actor, "play_card_936")
    execute(game, second, "pass_nope")
    assert second.id in game.pending_action.passed_player_ids

    execute(game, third, "play_nope")
    assert game.pending_action.nope_count == 1
    assert game.pending_action.passed_player_ids == []
    assert game.pending_action.timer_ticks == 5 * 20
    assert game._is_nope_responder(second)
    assert not game._is_nope_responder(third)

    execute(game, actor, "play_nope")
    execute(game, fourth, "play_nope")
    execute(game, second, "play_nope")
    assert game.pending_action.nope_count == 4
    resolve_nope(game)
    assert game.current_player == second
    assert game.turns_remaining == 2


def test_nope_response_timer_uses_room_setting_and_restarts_after_nope() -> None:
    game = make_game(2, touch=True)
    game.options.nope_response_seconds = "15"
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(941, ATTACK)]
    responder.hand = [card(942, NOPE)]

    execute(game, actor, "play_card_941")
    assert game.pending_action.timer_ticks == 15 * 20
    game.pending_action.timer_ticks = 23
    execute(game, responder, "play_nope")
    assert game.pending_action.timer_ticks == 15 * 20
    execute(game, actor, "check_nope_timer")
    assert "15 seconds remain." in speech(game.get_user(actor))


def test_nope_can_be_played_directly_from_the_hand() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(943, ATTACK), card(944, NOPE)]
    responder.hand = [card(945, NOPE), card(946, NOPE), card(947, SKIP)]

    execute(game, actor, "play_card_943")
    execute(game, responder, "play_card_946")

    assert game.pending_action.nope_count == 1
    assert card(946, NOPE) in game.discard_pile
    assert card(945, NOPE) in responder.hand
    assert card(946, NOPE) not in responder.hand
    assert "You play Nope." in speech(game.get_user(responder))

    execute(game, actor, "play_card_944")
    assert game.pending_action.nope_count == 2
    resolve_nope(game)
    assert game.current_player == responder
    assert game.turns_remaining == 2


def test_nope_errors_identify_own_action_own_nope_and_previous_pass() -> None:
    game = make_game(3)
    start_with_current(game)
    actor, passer, nopeer = game.players
    actor.hand = [card(948, ATTACK), card(949, NOPE)]
    passer.hand = [card(950, NOPE)]
    nopeer.hand = [card(951, NOPE), card(952, NOPE)]

    execute(game, actor, "play_card_948")
    execute(game, actor, "play_card_949")
    assert game.pending_action.nope_count == 0
    assert any(
        "You cannot Nope your own action" in text
        for text in speech(game.get_user(actor))
    )

    execute(game, passer, "pass_nope")
    execute(game, passer, "play_card_950")
    assert game.pending_action.nope_count == 0
    assert "You already passed this Nope window." in speech(game.get_user(passer))

    execute(game, nopeer, "play_card_951")
    execute(game, nopeer, "play_card_952")
    assert game.pending_action.nope_count == 1
    assert any(
        "You cannot Nope the Nope you just played" in text
        for text in speech(game.get_user(nopeer))
    )


def test_all_eligible_players_passing_resolves_immediately() -> None:
    game = make_game(3)
    start_with_current(game)
    actor, second, third = game.players
    actor.hand = [card(940, ATTACK)]
    execute(game, actor, "play_card_940")
    execute(game, second, "pass_nope")
    assert game.phase == PHASE_NOPE
    execute(game, third, "pass_nope")
    assert game.phase == PHASE_NORMAL
    assert game.current_player == second


def test_favor_target_privately_chooses_the_card() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(950, FAVOR)]
    target.hand = [card(951, DEFUSE), card(952, SKIP)]

    execute(game, actor, "play_card_950")
    assert game.phase == PHASE_NOPE
    assert game.pending_action.target_id == target.id
    resolve_nope(game)
    assert game.phase == PHASE_FAVOR_GIVE
    for player in game.players:
        game.get_user(player).clear_messages()
    execute(game, target, "play_card_952")

    assert [held.kind for held in actor.hand] == [SKIP]
    assert [held.kind for held in target.hand] == [DEFUSE]
    assert game.current_player == actor
    assert sound_names(game.get_user(actor))[0] in SOUND_DRAWS


def test_favor_automatically_transfers_the_only_available_card() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(953, FAVOR)]
    target.hand = [card(954, SKIP)]
    execute(game, actor, "play_card_953")
    resolve_nope(game)
    assert game.phase == PHASE_NORMAL
    assert [held.kind for held in actor.hand] == [SKIP]
    assert target.hand == []


def test_pair_steals_randomly_and_triple_requests_named_card() -> None:
    random.seed(12)
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(960, BEARD_CAT), card(961, BEARD_CAT)]
    target.hand = [card(962, SKIP)]

    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_960")
    execute(game, actor, "play_card_961")
    execute(game, actor, "confirm_combo")
    assert game.pending_action.target_id == target.id
    for player in game.players:
        game.get_user(player).clear_messages()
    ExplodingKittensGame._resolve_nope_window(game)
    assert sound_names(game.get_user(actor))[0] in SOUND_DRAWS
    drain_sequences(game)
    assert [held.kind for held in actor.hand] == [SKIP]
    assert not target.hand

    actor.hand = [card(963, BEARD_CAT), card(964, BEARD_CAT), card(965, BEARD_CAT)]
    target.hand = [card(966, DEFUSE), card(967, ATTACK)]
    execute(game, actor, "start_combo")
    for card_id in (963, 964, 965):
        execute(game, actor, f"play_card_{card_id}")
    execute(game, actor, "confirm_combo")
    assert game.phase == PHASE_REQUEST
    assert game.pending_action.target_id == target.id
    execute(game, actor, "request_attack")
    resolve_nope(game)
    assert any(held.kind == ATTACK for held in actor.hand)
    assert all(held.kind != ATTACK for held in target.hand)


def test_triple_plays_three_serial_cards_and_uses_miss_sound() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [
        card(958, BEARD_CAT),
        card(959, BEARD_CAT),
        card(960, BEARD_CAT),
    ]
    target.hand = [card(961, SKIP)]
    for player in game.players:
        game.get_user(player).clear_messages()

    execute(game, actor, "start_combo")
    for card_id in (958, 959, 960):
        execute(game, actor, f"play_card_{card_id}")
    execute(game, actor, "confirm_combo")
    execute(game, actor, "request_attack")
    played_sounds = [
        sound for sound in sound_names(game.get_user(actor)) if sound in SOUND_PLAYS
    ]
    scheduled_plays = [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in SOUND_PLAYS
    ]
    assert len(played_sounds) == 1
    assert len(scheduled_plays) == 2

    for player in game.players:
        game.get_user(player).clear_messages()
    ExplodingKittensGame._resolve_nope_window(game)
    assert sound_names(game.get_user(actor)) == [SOUND_COMBO_MISS]
    drain_sequences(game)
    assert game.phase == PHASE_NORMAL
    assert target.hand == [card(961, SKIP)]


def test_defuse_can_form_a_combo_and_be_requested_by_three_of_a_kind() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(968, DEFUSE), card(969, DEFUSE)]
    target.hand = [card(970, SKIP)]

    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_968")
    execute(game, actor, "play_card_969")
    execute(game, actor, "confirm_combo")
    assert game.phase == PHASE_NOPE
    assert game.pending_action.target_id == target.id
    resolve_nope(game)
    assert any(held.kind == SKIP for held in actor.hand)

    actor.hand = [card(971, BEARD_CAT), card(972, BEARD_CAT), card(973, BEARD_CAT)]
    target.hand = [card(974, DEFUSE), card(975, ATTACK)]
    execute(game, actor, "start_combo")
    for card_id in (971, 972, 973):
        execute(game, actor, f"play_card_{card_id}")
    execute(game, actor, "confirm_combo")
    assert game.phase == PHASE_REQUEST
    assert game.pending_action.target_id == target.id
    execute(game, actor, "request_defuse")
    resolve_nope(game)
    assert any(held.kind == DEFUSE for held in actor.hand)
    assert all(held.kind != DEFUSE for held in target.hand)


def test_combo_selection_rejects_mixed_titles_immediately() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [
        card(976, BEARD_CAT),
        card(977, BEARD_CAT),
        card(978, SKIP),
    ]
    target.hand = [card(979, ATTACK)]
    execute(game, actor, "start_combo")
    assert game._pending_menu_focus[actor.id] == "play_card_976"
    execute(game, actor, "play_card_976")
    execute(game, actor, "play_card_978")
    assert actor.selected_card_ids == [976]


def test_combo_keybind_routes_once_without_false_disabled_messages() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(980, BEARD_CAT), card(981, BEARD_CAT)]
    target.hand = [card(982, SKIP)]
    user = game.get_user(actor)
    assert game._keybinds["c"][0].actions == ["combo_command"]

    user.clear_messages()
    game.handle_event(actor, {"type": "keybind", "key": "c"})
    assert game.phase == PHASE_COMBO
    assert not any(
        text in (
            "Finish the current action first.",
            "Select exactly two or three cards with the same name.",
        )
        for text in speech(user)
    )

    execute(game, actor, "play_card_980")
    execute(game, actor, "play_card_981")
    user.clear_messages()
    game.handle_event(actor, {"type": "keybind", "key": "c"})
    drain_sequences(game)

    assert game.phase == PHASE_NOPE
    assert game.pending_action is not None
    assert game.pending_action.target_id == target.id
    assert "Finish the current action first." not in speech(user)
    assert "You play a Beard Cat pair against Player2." in speech(user)


def test_combo_keybind_reports_only_the_relevant_phase_error() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(983, BEARD_CAT)]
    target.hand = [card(984, SKIP)]
    user = game.get_user(actor)

    user.clear_messages()
    game.handle_event(actor, {"type": "keybind", "key": "c"})
    assert speech(user) == ["You do not have a matching pair or three of a kind."]

    actor.hand.append(card(985, BEARD_CAT))
    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_983")
    user.clear_messages()
    game.handle_event(actor, {"type": "keybind", "key": "c"})
    assert speech(user) == ["Select exactly two or three cards with the same name."]


def test_advanced_combo_option_preserves_cat_pairs_and_blocks_other_combos() -> None:
    disabled = make_game(2)
    disabled.options.advanced_combos = False
    start_with_current(disabled)
    actor, target = disabled.players
    actor.hand = [
        card(976, BEARD_CAT),
        card(977, BEARD_CAT),
        card(978, DEFUSE),
        card(979, DEFUSE),
    ]
    target.hand = [card(980, SKIP)]
    execute(disabled, actor, "start_combo")
    execute(disabled, actor, "play_card_978")
    assert actor.selected_card_ids == []
    execute(disabled, actor, "play_card_976")
    execute(disabled, actor, "play_card_977")
    execute(disabled, actor, "confirm_combo")
    assert disabled.phase == PHASE_NOPE
    assert disabled.pending_action.target_id == target.id


def test_basic_combo_errors_describe_cat_pairs_only() -> None:
    game = make_game(2)
    game.options.advanced_combos = False
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(980, BEARD_CAT)]
    target.hand = [card(981, SKIP)]

    assert (
        game._is_play_card_enabled(actor, action_id="play_card_980")
        == "explodingkittens-error-cat-needs-pair"
    )
    assert game._is_start_combo_enabled(actor) == "explodingkittens-error-no-cat-pair"

    game.phase = PHASE_COMBO
    actor.selected_card_ids = [980]
    assert (
        game._is_confirm_combo_enabled(actor)
        == "explodingkittens-error-invalid-cat-pair"
    )


def test_noped_combo_cancellation_names_the_combo() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(982, BEARD_CAT), card(983, BEARD_CAT)]
    target.hand = [card(984, SKIP), card(985, NOPE)]

    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_982")
    execute(game, actor, "play_card_983")
    execute(game, actor, "confirm_combo")
    execute(game, target, "play_card_985")
    resolve_nope(game)

    assert "Your pair is canceled." in speech(game.get_user(actor))
    assert "Player1's pair is canceled." in speech(game.get_user(target))


def test_empty_targets_block_favor_and_combo_flows() -> None:
    no_target = make_game(2)
    start_with_current(no_target)
    actor, target = no_target.players
    actor.hand = [card(981, FAVOR), card(982, BEARD_CAT), card(983, BEARD_CAT)]
    target.hand = []
    execute(no_target, actor, "play_card_981")
    assert no_target.phase == PHASE_NORMAL
    execute(no_target, actor, "start_combo")
    assert no_target.phase == PHASE_NORMAL


def test_combo_button_is_hidden_when_no_combo_is_available() -> None:
    game = make_game(2, touch=True)
    start_with_current(game)
    actor, target = game.players
    actor.hand = []
    target.hand = [card(984, SKIP)]
    game.refresh_menus(actor)
    game.flush_menus()
    ids = menu_ids(game.get_user(actor))
    assert "start_combo" not in ids
    assert "draw_card" in ids


def test_see_future_bot_knowledge_tracks_draws_and_clears_without_a_replay_action() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, other = game.players
    actor.hand = [card(970, SEE_FUTURE)]
    game.deck = [card(971, SKIP), card(972, ATTACK), card(973, FAVOR), card(974, SHUFFLE)]

    execute(game, actor, "play_card_970")
    resolve_nope(game)
    assert actor.known_future_card_ids == [971, 972, 973]
    assert game.find_action(actor, "review_future") is None

    execute(game, actor, "draw_card")
    assert actor.known_future_card_ids == [972, 973]
    game.current_player = other
    other.hand = [card(975, SHUFFLE)]
    execute(game, other, "play_card_975")
    resolve_nope(game)
    assert actor.known_future_card_ids == []


def test_shuffle_announces_play_resolution_and_named_cancellation() -> None:
    resolved = make_game(2)
    start_with_current(resolved)
    actor, observer = resolved.players
    actor.hand = [card(976, SHUFFLE)]
    for player in resolved.players:
        resolved.get_user(player).clear_messages()

    execute(resolved, actor, "play_card_976")
    assert "You play Shuffle." in speech(resolved.get_user(actor))
    assert "Player1 plays Shuffle." in speech(resolved.get_user(observer))
    resolve_nope(resolved)
    assert (
        "Your Shuffle takes effect. The draw pile is shuffled."
        in speech(resolved.get_user(actor))
    )
    assert (
        "Player1's Shuffle takes effect. The draw pile is shuffled."
        in speech(resolved.get_user(observer))
    )

    canceled = make_game(2)
    start_with_current(canceled)
    actor, responder = canceled.players
    actor.hand = [card(977, SHUFFLE)]
    responder.hand = [card(978, NOPE)]
    execute(canceled, actor, "play_card_977")
    execute(canceled, responder, "play_card_978")
    resolve_nope(canceled)
    assert "Your Shuffle is canceled." in speech(canceled.get_user(actor))
    assert "Player1's Shuffle is canceled." in speech(canceled.get_user(responder))


def test_successful_action_resolution_uses_listener_perspective() -> None:
    attack = make_game(3)
    start_with_current(attack)
    actor, target, observer = attack.players
    actor.hand = [card(979, ATTACK)]
    for player in attack.players:
        attack.get_user(player).clear_messages()
    execute(attack, actor, "play_card_979")
    resolve_nope(attack)
    assert (
        "Your Attack takes effect. Player2 must take 2 turns."
        in speech(attack.get_user(actor))
    )
    assert (
        "Player1's Attack takes effect. You must take 2 turns."
        in speech(attack.get_user(target))
    )
    assert (
        "Player1's Attack takes effect. Player2 must take 2 turns."
        in speech(attack.get_user(observer))
    )

    future = make_game(2)
    start_with_current(future)
    actor, observer = future.players
    actor.hand = [card(980, SEE_FUTURE)]
    future.deck = [card(981, SKIP), card(982, ATTACK), card(983, FAVOR)]
    execute(future, actor, "play_card_980")
    resolve_nope(future)
    assert any(
        text.startswith("Your See the Future takes effect. Next cards")
        for text in speech(future.get_user(actor))
    )
    assert (
        "Player1's See the Future takes effect."
        in speech(future.get_user(observer))
    )


def test_favor_resolution_announces_private_choice_without_repeating_play() -> None:
    game = make_game(3)
    start_with_current(game)
    actor, target, observer = game.players
    actor.hand = [card(984, FAVOR)]
    target.hand = [card(985, SKIP), card(986, DEFUSE)]
    observer.hand = [card(987, ATTACK)]
    execute(game, actor, "play_card_984")
    execute(game, actor, f"target_{target.id}")
    resolve_nope(game)

    assert (
        "Your Favor takes effect. Player2 is choosing a card."
        in speech(game.get_user(actor))
    )
    assert (
        "Player1's Favor takes effect. Choose a card to give."
        in speech(game.get_user(target))
    )
    assert (
        "Player1's Favor takes effect. Player2 is choosing a card."
        in speech(game.get_user(observer))
    )


def test_kitten_reveal_defuse_and_reinsert_are_distinct_timed_phases() -> None:
    game = make_game(2)
    start_with_current(game)
    actor = game.players[0]
    defuse = card(988, DEFUSE)
    kitten = card(989, EXPLODING_KITTEN)
    actor.hand = [defuse]
    game.deck = [kitten, card(990, SKIP)]
    for player in game.players:
        game.get_user(player).clear_messages()

    execute_raw(game, actor, "draw_card")
    assert game.phase == PHASE_RESOLVING
    sounds = sound_names(game.get_user(actor))
    assert sounds[0] in SOUND_DRAWS
    assert sounds[1] == SOUND_KITTEN_REVEAL
    assert game.drawn_kitten == kitten
    assert game.is_sequence_gameplay_locked()
    assert KITTEN_REVEAL_DELAY_TICKS == 18
    for _ in range(KITTEN_REVEAL_DELAY_TICKS - 1):
        game.on_tick()
    assert game.phase == PHASE_RESOLVING
    game.on_tick()
    assert game.phase == PHASE_DEFUSE
    assert not game.active_sequences

    execute_raw(game, actor, "use_defuse")
    assert game.phase == PHASE_REINSERT
    assert defuse not in actor.hand
    assert sound_names(game.get_user(actor))[-1] == SOUND_DEFUSE
    assert not game.active_sequences

    execute_raw(game, actor, "insert_0")
    assert sound_names(game.get_user(actor))[-1] == SOUND_REINSERT
    assert game.drawn_kitten is None
    assert game.deck[0] == kitten
    assert not game.active_sequences


def test_explosion_state_is_immediate_after_reveal_and_audio_continues_unlocked(
    monkeypatch,
) -> None:
    game = make_game(3)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(991, SKIP)]
    game.deck = [card(992, EXPLODING_KITTEN), card(993, ATTACK)]
    original_choice = random.choice

    def choose(sequence):
        if sequence is SOUND_EXPLOSIONS:
            return SOUND_EXPLOSIONS[1]
        return original_choice(sequence)

    monkeypatch.setattr(random, "choice", choose)
    for player in game.players:
        game.get_user(player).clear_messages()

    execute_raw(game, actor, "draw_card")
    assert not actor.eliminated
    for _ in range(KITTEN_REVEAL_DELAY_TICKS):
        game.on_tick()
    assert actor.eliminated
    assert not game.active_sequences
    assert not game.is_sequence_gameplay_locked()
    sounds = sound_names(game.get_user(actor))
    assert SOUND_KITTEN_REVEAL in sounds
    assert SOUND_FUSE in sounds
    assert SOUND_EXPLOSIONS[1] not in sounds
    assert any(
        scheduled[1] == SOUND_EXPLOSIONS[1]
        for scheduled in game.scheduled_sounds
    )
    for _ in range(AUDIO_DURATIONS_TICKS[SOUND_FUSE] - 1):
        game.on_tick()
    assert SOUND_EXPLOSIONS[1] not in sound_names(game.get_user(actor))
    game.on_tick()
    assert SOUND_EXPLOSIONS[1] in sound_names(game.get_user(actor))


def test_final_explosion_starts_with_winner_and_game_over(monkeypatch) -> None:
    game = make_game(2)
    start_with_current(game)
    actor, winner = game.players
    actor.hand = [card(994, SKIP)]
    game.deck = [card(995, EXPLODING_KITTEN), card(996, ATTACK)]
    original_choice = random.choice

    def choose(sequence):
        if sequence is SOUND_EXPLOSIONS:
            return SOUND_EXPLOSIONS[0]
        return original_choice(sequence)

    monkeypatch.setattr(random, "choice", choose)
    for player in game.players:
        game.get_user(player).clear_messages()

    execute_raw(game, actor, "draw_card")
    for _ in range(KITTEN_REVEAL_DELAY_TICKS):
        game.on_tick()

    assert actor.eliminated
    assert game.phase == PHASE_RESOLVING
    assert game.winner_id == ""
    assert game.status == "playing"
    assert game.is_sequence_gameplay_locked()
    assert SOUND_FUSE in sound_names(game.get_user(actor))
    assert SOUND_EXPLOSIONS[0] not in sound_names(game.get_user(actor))
    assert SOUND_GAME_OVER not in sound_names(game.get_user(actor))
    assert not any(
        "last player standing" in line for line in speech(game.get_user(winner))
    )
    final_sequence = game.active_sequences[0]
    assert final_sequence.beats[1].delay_after_ticks == 0

    for _ in range(AUDIO_DURATIONS_TICKS[SOUND_FUSE] - 1):
        game.on_tick()
    assert SOUND_EXPLOSIONS[0] not in sound_names(game.get_user(actor))
    game.on_tick()

    sounds = sound_names(game.get_user(actor))
    assert game.winner_id == winner.id
    assert game.phase == PHASE_GAME_OVER
    assert game.status == "finished"
    assert not game.active_sequences
    assert sounds.index(SOUND_FUSE) < sounds.index(SOUND_EXPLOSIONS[0])
    assert sounds.index(SOUND_EXPLOSIONS[0]) < sounds.index(SOUND_GAME_OVER)
    assert any(
        "last player standing" in line for line in speech(game.get_user(winner))
    )


def test_final_explosion_timing_survives_serialization(monkeypatch) -> None:
    game = make_game(2)
    start_with_current(game)
    actor, winner = game.players
    actor.hand = [card(997, SKIP)]
    game.deck = [card(998, EXPLODING_KITTEN), card(999, ATTACK)]
    original_choice = random.choice

    def choose(sequence):
        if sequence is SOUND_EXPLOSIONS:
            return SOUND_EXPLOSIONS[1]
        return original_choice(sequence)

    monkeypatch.setattr(random, "choice", choose)
    execute_raw(game, actor, "draw_card")
    for _ in range(
        KITTEN_REVEAL_DELAY_TICKS + AUDIO_DURATIONS_TICKS[SOUND_FUSE] // 2
    ):
        game.on_tick()

    restored = ExplodingKittensGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.winner_id == ""
    assert restored.phase == PHASE_RESOLVING
    assert restored.is_sequence_gameplay_locked()
    assert restored.active_sequences[0].beats[1].ops[0].sound == SOUND_EXPLOSIONS[1]

    drain_sequences(restored)
    assert restored.winner_id == winner.id
    assert restored.status == "finished"
    assert restored.phase == PHASE_GAME_OVER


def test_kitten_without_defuse_eliminates_and_advances() -> None:
    game = make_game(3)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(980, SKIP)]
    game.deck = [card(981, EXPLODING_KITTEN), card(982, ATTACK)]

    execute(game, actor, "draw_card")

    assert actor.eliminated
    assert game.current_player == game.players[1]
    assert game.turns_remaining == 1
    assert game.discard_pile == []
    assert card(980, SKIP) in game.removed_cards
    assert card(981, EXPLODING_KITTEN) in game.removed_cards
    all_cards = game.deck + game.discard_pile + game.removed_cards + [
        held for player in game.players for held in player.hand
    ]
    assert len({held.id for held in all_cards}) == len(all_cards)


def test_defuse_reinsertion_is_exact_private_and_consumes_one_turn() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, observer = game.players
    actor.hand = [card(990, DEFUSE)]
    game.deck = [card(991, EXPLODING_KITTEN), card(992, SKIP), card(993, ATTACK)]
    game.turns_remaining = 2
    game.attack_obligation = True
    game.get_user(observer).clear_messages()

    execute(game, actor, "draw_card")
    assert game.phase == PHASE_DEFUSE
    execute(game, actor, "use_defuse")
    assert game.phase == PHASE_REINSERT
    execute(game, actor, "insert_2")

    assert game.deck[2].kind == EXPLODING_KITTEN
    assert game.current_player == actor
    assert game.turns_remaining == 1
    assert not any("2" in text or "above" in text for text in speech(game.get_user(observer)))


def test_defuse_prompt_focus_is_one_shot_and_single_reinsertion_is_automatic() -> None:
    game, users = make_network_game(2)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(994, DEFUSE)]
    game.deck = [card(995, EXPLODING_KITTEN), card(996, SKIP)]
    for user in users:
        user.get_queued_messages()

    execute(game, actor, "draw_card")
    game.flush_menus()
    actor_packets = network_menu_packets(users[0])
    assert actor_packets[-1]["selection_id"] == "use_defuse"

    game.refresh_menus(actor)
    game.flush_menus()
    assert network_menu_packets(users[0]) == []

    single = make_game(2)
    start_with_current(single)
    actor = single.players[0]
    actor.hand = [card(997, DEFUSE)]
    single.deck = [card(998, EXPLODING_KITTEN)]
    execute(single, actor, "draw_card")
    assert single.phase == PHASE_DEFUSE
    execute(single, actor, "use_defuse")
    assert single.phase == PHASE_NORMAL
    assert single.deck == [card(998, EXPLODING_KITTEN)]


def test_explosion_choice_remains_available_if_defuse_state_is_inconsistent() -> None:
    game = make_game(2)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(999, SKIP)]
    game.phase = PHASE_DEFUSE
    game.decision_player_id = actor.id
    game.drawn_kitten = card(1000, EXPLODING_KITTEN)

    assert game._is_use_defuse_enabled(actor) == "explodingkittens-error-no-defuse"
    assert game._is_accept_explosion_enabled(actor) is None
    execute(game, actor, "accept_explosion")
    assert actor.eliminated


def test_private_combo_transition_sends_no_menu_packet_to_other_clients() -> None:
    game, users = make_network_game(2)
    start_with_current(game)
    actor, observer = game.players
    actor.hand = [card(1000, BEARD_CAT), card(1001, BEARD_CAT)]
    observer.hand = [card(1002, SKIP)]
    game.refresh_menus()
    game.flush_menus()
    for user in users:
        user.get_queued_messages()

    execute(game, actor, "start_combo")
    game.refresh_menus()
    game.flush_menus()

    assert len(network_menu_packets(users[0])) == 1
    assert network_menu_packets(users[1]) == []


def test_touch_nope_actions_are_pinned_above_the_hand() -> None:
    game = make_game(2, touch=True)
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(1010, ATTACK)]
    responder.hand = [card(1011, NOPE), card(1012, SKIP)]
    execute(game, actor, "play_card_1010")
    game.flush_menus()
    ids = menu_ids(game.get_user(responder))
    assert ids[:2] == ["play_nope", "pass_nope"]
    execute(game, responder, "check_nope_timer")
    assert "10 seconds remain." in speech(game.get_user(responder))


def test_desktop_nope_actions_are_keybind_only_and_remain_usable() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, responder = game.players
    actor.hand = [card(1013, ATTACK)]
    responder.hand = [card(1014, NOPE), card(1015, SKIP)]

    execute(game, actor, "play_card_1013")
    game.flush_menus()
    ids = menu_ids(game.get_user(responder))
    assert "play_nope" not in ids
    assert "pass_nope" not in ids
    execute(game, responder, "play_nope")
    assert game.pending_action.nope_count == 1


def test_nope_resolution_removes_touch_reactions_for_see_future_and_favor() -> None:
    future = make_game(2, touch=True)
    start_with_current(future)
    actor, responder = future.players
    actor.hand = [card(1016, SEE_FUTURE)]
    responder.hand = [card(1017, NOPE)]
    future.deck = [card(1018, SKIP), card(1019, ATTACK)]
    execute(future, actor, "play_card_1016")
    future.flush_menus()
    assert menu_ids(future.get_user(responder))[:2] == ["play_nope", "pass_nope"]
    resolve_nope(future)
    future.flush_menus()
    assert "play_nope" not in menu_ids(future.get_user(responder))
    assert "pass_nope" not in menu_ids(future.get_user(responder))

    favor = make_game(3, touch=True)
    start_with_current(favor)
    actor, target, observer = favor.players
    actor.hand = [card(1020, FAVOR)]
    target.hand = [card(1021, SKIP), card(1022, DEFUSE)]
    observer.hand = [card(1023, NOPE)]
    execute(favor, actor, "play_card_1020")
    execute(favor, actor, f"target_{target.id}")
    favor.flush_menus()
    assert "pass_nope" in menu_ids(favor.get_user(observer))
    resolve_nope(favor)
    favor.flush_menus()
    assert favor.phase == PHASE_FAVOR_GIVE
    assert "play_nope" not in menu_ids(favor.get_user(observer))
    assert "pass_nope" not in menu_ids(favor.get_user(observer))


def test_phase_and_action_state_survive_serialization() -> None:
    game = make_game(3)
    game.options.nope_response_seconds = "20"
    start_with_current(game)
    actor, target, other = game.players
    actor.hand = [card(1020, FAVOR)]
    target.hand = [card(1021, SKIP)]
    other.hand = [card(1022, ATTACK)]
    execute(game, actor, "play_card_1020")
    assert game.phase == PHASE_TARGET

    restored = ExplodingKittensGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.phase == PHASE_TARGET
    assert restored.pending_action.actor_id == actor.id
    assert restored.pending_action.card_ids == [1020]
    assert restored.options.nope_response_seconds == "20"


def test_nope_chain_and_timer_survive_serialization() -> None:
    game = make_game(3)
    game.options.nope_response_seconds = "15"
    start_with_current(game)
    actor, responder, passer = game.players
    actor.hand = [card(1023, ATTACK), card(1024, NOPE)]
    responder.hand = [card(1025, NOPE)]
    passer.hand = [card(1026, SKIP)]
    execute(game, actor, "play_card_1023")
    execute(game, passer, "pass_nope")
    execute(game, responder, "play_nope")
    game.pending_action.timer_ticks = 137

    restored = ExplodingKittensGame.from_json(game.to_json())
    assert restored.phase == PHASE_NOPE
    assert restored.pending_action.nope_count == 1
    assert restored.pending_action.last_nope_player_id == responder.id
    assert restored.pending_action.passed_player_ids == []
    assert restored.pending_action.timer_ticks == 137


def test_nonblocking_combo_audio_schedule_survives_serialization() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, target = game.players
    actor.hand = [card(1027, BEARD_CAT), card(1028, BEARD_CAT)]
    target.hand = [card(1029, SKIP)]
    execute(game, actor, "start_combo")
    execute(game, actor, "play_card_1027")
    execute(game, actor, "play_card_1028")
    execute_raw(game, actor, "confirm_combo")
    assert game.phase == PHASE_NOPE
    assert not game.active_sequences
    assert len(game.scheduled_sounds) == 1

    restored = ExplodingKittensGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.phase == PHASE_NOPE
    assert restored.scheduled_sounds == game.scheduled_sounds
    assert not restored.active_sequences
    assert not restored.is_sequence_gameplay_locked()


def test_kitten_reveal_gate_survives_serialization() -> None:
    game = make_game(2)
    start_with_current(game)
    actor = game.players[0]
    actor.hand = [card(1030, DEFUSE)]
    game.deck = [card(1031, EXPLODING_KITTEN), card(1032, SKIP)]
    execute_raw(game, actor, "draw_card")
    for _ in range(7):
        game.on_tick()
    restored = ExplodingKittensGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.phase == PHASE_RESOLVING
    assert restored.drawn_kitten == card(1031, EXPLODING_KITTEN)
    assert restored.is_sequence_gameplay_locked()
    drain_sequences(restored)
    assert restored.phase == PHASE_DEFUSE
    assert not restored.active_sequences


@pytest.mark.parametrize("advanced_combos", [False, True])
def test_bots_can_complete_a_match_without_hidden_input_prompts(
    advanced_combos: bool,
) -> None:
    random.seed(77 + int(advanced_combos))
    game = make_bot_game(2)
    game.options.advanced_combos = advanced_combos
    game.on_start()
    for _ in range(30000):
        if not game.game_active:
            break
        game.on_tick()
        game.flush_menus()
    assert not game.game_active
    assert game.status == "finished"
    assert game.winner_id


def test_game_over_sound_winner_and_result_are_dispatched_together() -> None:
    game = make_game(2)
    start_with_current(game)
    winner = game.players[1]
    for player in game.players:
        game.get_user(player).clear_messages()

    game._end_game(winner)
    assert game.phase == PHASE_GAME_OVER
    assert game.status == "finished"
    assert sound_names(game.get_user(winner)) == [SOUND_GAME_OVER]
    assert not game.active_sequences
    assert any(
        text.startswith("You are the last player standing")
        for text in speech(game.get_user(winner))
    )


def test_result_ranking_places_later_eliminations_higher() -> None:
    game = make_game(3)
    start_with_current(game)
    first, second, winner = game.players
    first.eliminated = True
    first.elimination_order = 1
    second.eliminated = True
    second.elimination_order = 2
    game.winner_id = winner.id
    result = game.build_game_result()
    assert result.custom_data["rankings"] == [winner.name, second.name, first.name]
    assert result.custom_data["winner_ids"] == [winner.id]


def test_locales_docs_keybinds_and_audio_source_are_complete() -> None:
    en = ROOT / "server/locales/en/explodingkittens.ftl"
    vi = ROOT / "server/locales/vi/explodingkittens.ftl"
    vi_manual = ROOT / "server/documentation/content/vi/games/explodingkittens.md"
    assert locale_keys(en) == locale_keys(vi)
    assert (ROOT / "server/documentation/content/en/games/explodingkittens.md").exists()
    assert vi_manual.exists()
    assert Localization.get("vi", "game-name-explodingkittens") == "Mèo Nổ"
    assert Localization.get("fa", "game-name-explodingkittens") == "Exploding Kittens"
    vi_terms = {
        "explodingkittens-card-defuse": "Gỡ Bom",
        "explodingkittens-card-nope": "Phủ Nhận",
        "explodingkittens-card-attack": "Tấn Công",
        "explodingkittens-card-skip": "Bỏ Lượt",
        "explodingkittens-card-favor": "Xin Bài",
        "explodingkittens-card-shuffle": "Xáo Bài",
        "explodingkittens-card-see-future": "Nhìn Tương Lai",
    }
    manual_text = vi_manual.read_text(encoding="utf-8")
    for key, term in vi_terms.items():
        assert Localization.get("vi", key) == term
        assert term in manual_text
    assert "lá Chặn" not in manual_text
    assert "Xem Trước Tương Lai" not in manual_text

    game = make_game(2)
    assert any(binding.state == KeybindState.ACTIVE for binding in game._keybinds["n"])
    assert game.find_action(game.players[0], "review_future") is None
    assert not any(
        "review_future" in binding.actions
        for bindings in game._keybinds.values()
        for binding in bindings
    )
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "server/games/explodingkittens").glob("*.py")
    )
    assert "SequenceOperation.sound_op" in source
    assert "play_music(SOUND_MUSIC)" in source
    assert "play_ambience(" not in source


def test_actor_and_observer_receive_correct_perspectives() -> None:
    game = make_game(2)
    start_with_current(game)
    actor, observer = game.players
    actor.hand = [card(1030, ATTACK)]
    for player in game.players:
        game.get_user(player).clear_messages()

    execute(game, actor, "play_card_1030")

    assert any(text == "You play Attack." for text in speech(game.get_user(actor)))
    assert any(text == "Player1 plays Attack." for text in speech(game.get_user(observer)))
