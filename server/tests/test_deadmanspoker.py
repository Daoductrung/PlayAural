"""Tests for Dead Man's Poker."""

from pathlib import Path
import random

from server.games.deadmanspoker.bot import bot_think as deadmanspoker_bot_think
from server.games.deadmanspoker.game import (
    AUDIO_DURATIONS_TICKS,
    EIGHT_BULLET_DEATH_CHANCE,
    MAX_BULLETS,
    PHASE_ROULETTE,
    PHASE_ALL_IN_RESPONSE,
    PHASE_DECISION,
    PHASE_SHOWDOWN,
    PHASE_SWITCH,
    PRIVATE_REVEAL_DELAY_TICKS,
    ROULETTE_POST_COCK_WAIT_TICKS,
    ROULETTE_POST_SPIN_WAIT_TICKS,
    SOUND_COCK,
    SOUND_DEATH_SIGNAL,
    SOUND_EMPTY_CLICK,
    SOUND_GAME_START,
    SOUND_GUNSHOTS,
    SOUND_PICK_UP_GUN,
    SOUND_PICK_UP_BULLETS,
    SOUND_PLACE_BULLETS,
    SOUND_REVEAL_PRIVATE_CARDS,
    SOUND_ROUNDS,
    SOUND_SPIN_CYLINDER,
    DeadMansPokerGame,
)
from server.game_utils.cards import Card, card_name
from server.game_utils.sequence_runner_mixin import SequenceOperation
from server.games.registry import GameRegistry
from server.messages.localization import Localization
from server.ui.keybinds import KeybindState
from server.users.bot import Bot
from server.users.test_user import MockUser


ROOT = Path(__file__).resolve().parents[2]


def make_game(player_count: int = 2) -> DeadMansPokerGame:
    game = DeadMansPokerGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    return game


def make_touch_game(player_count: int = 2) -> DeadMansPokerGame:
    game = DeadMansPokerGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = MockUser(name, uuid=f"p{index + 1}")
        user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    return game


def make_bot_game(player_count: int = 2) -> DeadMansPokerGame:
    game = DeadMansPokerGame()
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


def advance_until(game: DeadMansPokerGame, condition, max_ticks: int = 3000) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def start_to_decision(game: DeadMansPokerGame) -> None:
    game.on_start()
    assert advance_until(
        game,
        lambda: game.phase == PHASE_DECISION and not game.active_sequences,
        max_ticks=1000,
    )


def sound_names(user: MockUser) -> list[str]:
    return [message.data["name"] for message in user.messages if message.type == "play_sound"]


def speech_texts(user: MockUser) -> list[str]:
    return [message.data["text"] for message in user.messages if message.type == "speak"]


def locale_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and line[:1].isalnum():
            keys.add(line.split("=", 1)[0].strip())
    return keys


def sequence_operations(
    game: DeadMansPokerGame,
    sequence_id: str,
) -> list[tuple[int, SequenceOperation]]:
    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.sequence_id == sequence_id
    )
    tick = 0
    operations: list[tuple[int, SequenceOperation]] = []
    for beat in sequence.beats:
        for operation in beat.ops:
            operations.append((tick, operation))
        tick += beat.delay_after_ticks
    return operations


def finish_decision_round(game: DeadMansPokerGame) -> None:
    stage = game.round_stage
    while game.phase == PHASE_DECISION and game.round_stage == stage:
        actor = game.current_player
        assert actor is not None
        game.execute_action(actor, "call")
        assert advance_until(game, lambda: not game.active_sequences, max_ticks=1200)


def advance_to_flop(game: DeadMansPokerGame) -> None:
    finish_decision_round(game)
    assert game.phase == PHASE_DECISION
    assert game.round_stage == 2
    assert game.revealed_community_count == 3


def test_game_registration_and_metadata() -> None:
    game_cls = GameRegistry.get("deadmanspoker")
    assert game_cls is DeadMansPokerGame
    assert DeadMansPokerGame.get_name() == "Dead Man's Poker"
    assert DeadMansPokerGame.get_type() == "deadmanspoker"
    assert DeadMansPokerGame.get_category() == "poker"
    assert DeadMansPokerGame.get_min_players() == 2
    assert DeadMansPokerGame.get_max_players() == 4
    assert DeadMansPokerGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]


def test_game_delegates_bot_logic_to_bot_module() -> None:
    game = make_game(2)
    player = game.players[0]

    assert game.bot_think(player) == deadmanspoker_bot_think(game, player)


def test_bot_game_completes_without_deadlock() -> None:
    random.seed(12345)
    game = make_bot_game(2)
    game.on_start()

    assert advance_until(game, lambda: game.status == "finished", max_ticks=60000)


def test_score_actions_are_disabled_silently() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.execute_action(player, "check_scores")
    game.execute_action(player, "check_scores_detailed")

    assert user.messages == []


def test_keybinds_use_active_state_and_do_not_collide_with_reserved_keys() -> None:
    game = make_game(2)
    reserved = {
        "enter",
        "escape",
        "b",
        "shift+b",
        "f3",
        "t",
        "s",
        "shift+s",
        "ctrl+m",
        "ctrl+q",
        "ctrl+u",
        "ctrl+s",
        "ctrl+r",
        "ctrl+i",
        "ctrl+f1",
    }
    game_keys = {"c", "f", "shift+f", "d", "shift+a", "w", "g", "e", "v", "h", "p"}
    assert game_keys.isdisjoint(reserved)
    for key in game_keys:
        assert key in game._keybinds
        assert all(binding.state == KeybindState.ACTIVE for binding in game._keybinds[key])
    assert not any(binding.actions == ["all_in"] for binding in game._keybinds.get("r", []))
    assert any(binding.include_spectators for binding in game._keybinds["e"])
    assert any(binding.include_spectators for binding in game._keybinds["v"])
    assert any(binding.include_spectators for binding in game._keybinds["h"])
    assert any(binding.include_spectators for binding in game._keybinds["p"])


def test_audio_assets_exist_in_all_sound_packs() -> None:
    required = {
        SOUND_GAME_START,
        *SOUND_PLACE_BULLETS,
        *SOUND_GUNSHOTS,
        *SOUND_ROUNDS.values(),
        "game_deadmanspoker/all_in.ogg",
        "game_deadmanspoker/call.ogg",
        "game_deadmanspoker/community_cards_arrive.ogg",
        "game_deadmanspoker/deal_card.ogg",
        "game_deadmanspoker/death_signal.ogg",
        "game_deadmanspoker/empty_click.ogg",
        "game_deadmanspoker/fold.ogg",
        "game_deadmanspoker/load_bullet.ogg",
        "game_deadmanspoker/pick_up_bullets.ogg",
        "game_deadmanspoker/pick_up_gun.ogg",
        "game_deadmanspoker/reveal_card.ogg",
        "game_deadmanspoker/reveal_private_cards.ogg",
        "game_deadmanspoker/reveal_three_cards.ogg",
        "game_deadmanspoker/shuffle.ogg",
        "game_deadmanspoker/spin_cylinder.ogg",
        "game_deadmanspoker/switch_card.ogg",
        "game_deadmanspoker/unload_bullet.ogg",
    }
    for pack in ["client", "web_client", "mobile_client"]:
        for sound in required:
            assert (ROOT / pack / "sounds" / sound).exists(), f"missing {pack}/{sound}"

    game_files = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "server" / "games" / "deadmanspoker").glob("*.py")
    )
    assert ("trigger" + "_pull.ogg") not in game_files
    assert ("hand" + "_start.ogg") not in game_files
    assert AUDIO_DURATIONS_TICKS[SOUND_GAME_START] == 132
    assert AUDIO_DURATIONS_TICKS["game_deadmanspoker/round_1.ogg"] == 40
    assert AUDIO_DURATIONS_TICKS["game_deadmanspoker/round_2.ogg"] == 40


def test_hand_setup_forced_bullets_and_private_cards() -> None:
    random.seed(1)
    game = make_game(3)
    start_to_decision(game)

    assert game.hand_number == 1
    assert game.round_stage == 1
    assert game.revealed_community_count == 0
    assert len(game.community) == 5
    assert [len(player.hand) for player in game.players] == [2, 2, 2]
    assert [player.committed_bullets for player in game.players] == [1, 1, 1]
    assert [player.active_in_hand for player in game.players] == [True, True, True]


def test_call_adds_bullet_and_announces_with_sound() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None
    user.clear_messages()
    other_user.clear_messages()

    game.execute_action(player, "call")

    assert player.committed_bullets == 2
    assert "game_deadmanspoker/call.ogg" in sound_names(user)
    assert any(sound in sound_names(user) for sound in SOUND_PLACE_BULLETS)
    assert any("You call" in text for text in speech_texts(user))
    assert any(f"{player.name} calls" in text for text in speech_texts(other_user))


def test_read_hand_and_hand_value_are_separate_actions() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    user.clear_messages()
    game.execute_action(player, "read_hand")
    hand_messages = speech_texts(user)
    assert len(hand_messages) == 1
    assert "private cards" in hand_messages[0]

    user.clear_messages()
    game.execute_action(player, "read_hand_value")
    value_messages = speech_texts(user)
    assert len(value_messages) == 1
    assert "private cards" not in value_messages[0]


def test_read_community_cards_reports_only_table_cards() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    game.revealed_community_count = 3

    user.clear_messages()
    game.execute_action(player, "read_community_cards")

    text = user.get_last_spoken()
    assert text is not None
    assert "Community cards:" in text
    assert "Hidden:" in text
    assert "Current turn" not in text


def test_touch_turn_menu_does_not_duplicate_info_actions() -> None:
    game = make_touch_game(2)
    start_to_decision(game)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    items = user.get_current_menu_items("turn_menu") or []
    item_ids = [getattr(item, "id", "") for item in items]
    item_texts = [getattr(item, "text", str(item)) for item in items]
    info_ids = [
        "read_hand",
        "read_community_cards",
        "read_hand_value",
        "read_table",
        "read_card_counts",
        "read_revolvers",
    ]
    info_labels = [
        Localization.get("en", "deadmanspoker-read-hand"),
        Localization.get("en", "deadmanspoker-read-community-cards"),
        Localization.get("en", "deadmanspoker-read-hand-value"),
        Localization.get("en", "deadmanspoker-read-table"),
        Localization.get("en", "deadmanspoker-read-card-counts"),
        Localization.get("en", "deadmanspoker-read-revolvers"),
    ]

    for action_id in info_ids:
        assert item_ids.count(action_id) == 1
    for label in info_labels:
        assert item_texts.count(label) == 1


def test_decision_rounds_reveal_community_cards_in_order() -> None:
    game = make_game(2)
    start_to_decision(game)

    finish_decision_round(game)
    assert game.phase == PHASE_DECISION
    assert game.round_stage == 2
    assert game.revealed_community_count == 3

    finish_decision_round(game)
    assert game.phase == PHASE_DECISION
    assert game.round_stage == 3
    assert game.revealed_community_count == 4

    finish_decision_round(game)
    assert game.phase == PHASE_DECISION
    assert game.round_stage == 4
    assert game.revealed_community_count == 5


def test_switch_replacement_flow_keeps_turn_available() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None
    old_hand = list(player.hand)
    discarded = old_hand[0]
    other_user.clear_messages()

    game.execute_action(player, "switch_card", input_value="0")
    assert game.phase == PHASE_SWITCH
    assert len(game.pending_switch_candidates) == 3

    game.execute_action(player, "choose_switch_1")
    assert advance_until(game, lambda: not game.active_sequences)

    assert game.phase == PHASE_DECISION
    assert game.current_player == player
    assert player.used_switch
    assert len(player.hand) == 2
    assert player.hand != old_hand
    assert any(card_name(discarded, "en") in text for text in speech_texts(other_user))


def test_switch_card_resets_each_hand() -> None:
    game = make_game(2)
    start_to_decision(game)
    for player in game.players:
        player.used_switch = True

    game._start_new_hand()

    assert all(not player.used_switch for player in game.players)


def test_normal_fold_first_decision_requires_coward_fold() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None

    assert game._is_fold_enabled(player) == "deadmanspoker-fold-first-decision-use-coward"
    assert game._is_coward_fold_enabled(player) is None


def test_all_in_is_blocked_until_flop() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None

    assert game._is_all_in_enabled(player) == "deadmanspoker-all-in-too-early"

    advance_to_flop(game)
    player = game.current_player
    assert player is not None
    assert game._is_all_in_enabled(player) is None


def test_coward_fold_is_one_use_and_only_risks_one_bullet(monkeypatch) -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    monkeypatch.setattr(random, "random", lambda: 0.99)

    game.execute_action(player, "coward_fold")
    assert advance_until(
        game,
        lambda: game.phase == PHASE_DECISION and not game.active_sequences and game.hand_number == 2,
        max_ticks=2000,
    )

    assert player.used_coward_fold
    game.current_player = player
    assert game._is_coward_fold_enabled(player) == "deadmanspoker-coward-used"


def test_all_in_response_fold_can_award_uncontested_hand(monkeypatch) -> None:
    game = make_game(2)
    start_to_decision(game)
    advance_to_flop(game)
    initiator = game.current_player
    assert initiator is not None
    monkeypatch.setattr(random, "random", lambda: 0.99)

    game.execute_action(initiator, "all_in")
    assert advance_until(
        game,
        lambda: game.phase == PHASE_ALL_IN_RESPONSE and not game.active_sequences,
        max_ticks=1200,
    )
    responder = game.current_player
    assert responder is not None and responder != initiator
    game.execute_action(responder, "fold")
    assert advance_until(
        game,
        lambda: game.phase == PHASE_DECISION and not game.active_sequences and game.hand_number == 2,
        max_ticks=2500,
    )

    assert initiator.hands_won == 1


def test_all_in_places_added_bullets_together() -> None:
    game = make_game(2)
    start_to_decision(game)
    advance_to_flop(game)
    initiator = game.current_player
    assert initiator is not None
    user = game.get_user(initiator)
    assert user is not None
    committed_before = initiator.committed_bullets
    user.clear_messages()

    game.execute_action(initiator, "all_in")

    immediate_bullet_sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound" and message.data["name"] in SOUND_PLACE_BULLETS
    ]
    assert len(immediate_bullet_sounds) == MAX_BULLETS - committed_before


def test_folded_players_are_batched_before_roulette(monkeypatch) -> None:
    game = make_game(3)
    start_to_decision(game)
    monkeypatch.setattr(random, "random", lambda: 0.99)

    first_folder = game.current_player
    assert first_folder is not None
    first_folder.acted_this_hand = True
    first_folder.committed_bullets = 2
    game.execute_action(first_folder, "fold")
    assert advance_until(game, lambda: not game.active_sequences, max_ticks=1000)

    assert game.pending_roulette_ids == [first_folder.id]
    assert not game.has_active_sequence(tag="deadmanspoker_roulette")
    assert game.phase == PHASE_DECISION

    second_folder = game.current_player
    assert second_folder is not None and second_folder != first_folder
    second_folder.acted_this_hand = True
    second_folder.committed_bullets = 2
    game.execute_action(second_folder, "fold")
    assert advance_until(
        game,
        lambda: game.has_active_sequence(tag="deadmanspoker_roulette"),
        max_ticks=1000,
    )
    assert set(game.pending_roulette_ids) == {first_folder.id, second_folder.id}


def test_pending_fold_batch_resumes_all_in_flow(monkeypatch) -> None:
    game = make_game(3)
    start_to_decision(game)
    advance_to_flop(game)
    monkeypatch.setattr(random, "random", lambda: 0.99)

    first_folder = game.current_player
    assert first_folder is not None
    game.execute_action(first_folder, "fold")
    assert advance_until(game, lambda: not game.active_sequences, max_ticks=1000)

    all_in_player = game.current_player
    assert all_in_player is not None
    game.execute_action(all_in_player, "all_in")
    assert advance_until(
        game,
        lambda: game.phase == PHASE_ALL_IN_RESPONSE and not game.active_sequences,
        max_ticks=1000,
    )

    responder = game.current_player
    assert responder is not None
    game.execute_action(responder, "call")
    assert advance_until(
        game,
        lambda: game.has_active_sequence(tag="deadmanspoker_roulette"),
        max_ticks=1000,
    )
    assert game.pending_roulette_context == "all_in_fold"
    assert advance_until(
        game,
        lambda: game.phase == PHASE_SHOWDOWN or game.has_active_sequence(tag="deadmanspoker_showdown"),
        max_ticks=2500,
    )


def test_showdown_tie_has_no_roulette_sequence() -> None:
    game = make_game(2)
    game.status = "playing"
    game.game_active = True
    game.community = [
        Card(id=1, rank=10, suit=4),
        Card(id=2, rank=11, suit=4),
        Card(id=3, rank=12, suit=4),
        Card(id=4, rank=13, suit=4),
        Card(id=5, rank=1, suit=4),
    ]
    game.revealed_community_count = 5
    game.players[0].hand = [Card(id=6, rank=2, suit=1), Card(id=7, rank=3, suit=1)]
    game.players[1].hand = [Card(id=8, rank=4, suit=2), Card(id=9, rank=5, suit=2)]
    for player in game.players:
        player.active_in_hand = True
        player.committed_bullets = 2

    game._resolve_showdown()

    assert not game.has_active_sequence(tag="deadmanspoker_roulette")
    assert all(not player.eliminated for player in game.players)


def test_showdown_win_counts_as_hand_win_in_results() -> None:
    game = make_game(2)
    game.status = "playing"
    game.game_active = True
    game.hand_number = 1
    winner = game.players[0]
    loser = game.players[1]
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=1),
        Card(id=3, rank=12, suit=1),
        Card(id=4, rank=2, suit=2),
        Card(id=5, rank=3, suit=3),
    ]
    game.revealed_community_count = 5
    winner.hand = [Card(id=6, rank=13, suit=1), Card(id=7, rank=1, suit=1)]
    loser.hand = [Card(id=8, rank=9, suit=2), Card(id=9, rank=9, suit=3)]
    for player in game.players:
        player.active_in_hand = True
        player.committed_bullets = 2

    game._resolve_showdown()

    assert winner.showdowns_won == 1
    assert winner.hands_won == 1
    result = game.build_game_result()
    assert result.custom_data["player_stats"][winner.name]["hands_won"] == 1


def test_roulette_uses_eight_bullet_god_save_rule(monkeypatch) -> None:
    game = make_game(2)
    monkeypatch.setattr(random, "random", lambda: EIGHT_BULLET_DEATH_CHANCE - 0.01)
    assert game._roulette_is_lethal(MAX_BULLETS)
    monkeypatch.setattr(random, "random", lambda: EIGHT_BULLET_DEATH_CHANCE + 0.01)
    assert not game._roulette_is_lethal(MAX_BULLETS)


def test_multi_player_roulette_uses_panning_and_single_death_signal(monkeypatch) -> None:
    game = make_game(3)
    game.status = "playing"
    game.game_active = True
    for player in game.players:
        player.committed_bullets = 2
        player.active_in_hand = True
    game.pending_roulette_ids = [player.id for player in game.players]
    game.pending_roulette_context = "showdown"
    monkeypatch.setattr(random, "random", lambda: 0.0)

    game._start_pending_roulette()
    assert game.phase == PHASE_ROULETTE
    operations = sequence_operations(game, "deadmanspoker_roulette")
    first_pan = -25
    spin_tick = next(
        tick
        for tick, operation in operations
        if operation.kind == "sound"
        and operation.sound == SOUND_SPIN_CYLINDER
        and operation.pan == first_pan
    )
    cock_tick = next(
        tick
        for tick, operation in operations
        if operation.kind == "sound"
        and operation.sound == SOUND_COCK
        and operation.pan == first_pan
    )
    result_tick = next(
        tick
        for tick, operation in operations
        if operation.kind == "sound"
        and operation.pan == first_pan
        and operation.sound in {SOUND_EMPTY_CLICK, *SOUND_GUNSHOTS}
    )
    post_spin_wait = cock_tick - spin_tick - AUDIO_DURATIONS_TICKS[SOUND_SPIN_CYLINDER]
    post_cock_wait = result_tick - cock_tick - AUDIO_DURATIONS_TICKS[SOUND_COCK]
    assert ROULETTE_POST_SPIN_WAIT_TICKS[0] <= post_spin_wait <= ROULETTE_POST_SPIN_WAIT_TICKS[1]
    assert ROULETTE_POST_COCK_WAIT_TICKS[0] <= post_cock_wait <= ROULETTE_POST_COCK_WAIT_TICKS[1]

    first_user = game.get_user(game.players[0])
    assert first_user is not None
    assert advance_until(game, lambda: not game.has_active_sequence(tag="deadmanspoker_roulette"), max_ticks=2000)

    pickup_gun_pans = [
        message.data["pan"]
        for message in first_user.messages
        if message.type == "play_sound" and message.data["name"] == SOUND_PICK_UP_GUN
    ]
    pickup_bullet_pans = [
        message.data["pan"]
        for message in first_user.messages
        if message.type == "play_sound" and message.data["name"] == SOUND_PICK_UP_BULLETS
    ]
    assert pickup_gun_pans == [-25, 0, 25]
    assert pickup_bullet_pans == [-25, 0, 25]

    death_signal_count = sound_names(first_user).count(SOUND_DEATH_SIGNAL)
    assert death_signal_count == 1
    assert any(sound in sound_names(first_user) for sound in SOUND_GUNSHOTS)


def test_showdown_reveals_private_cards_two_seconds_apart() -> None:
    game = make_game(3)
    game.status = "playing"
    game.game_active = True
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=12, suit=3),
        Card(id=4, rank=13, suit=4),
        Card(id=5, rank=1, suit=1),
    ]
    game.revealed_community_count = 5
    for index, player in enumerate(game.players):
        player.hand = [
            Card(id=10 + index, rank=2 + index, suit=1),
            Card(id=20 + index, rank=5 + index, suit=2),
        ]
        player.active_in_hand = True
        player.committed_bullets = 2

    game._start_showdown_sequence()

    reveal_ticks = [
        tick
        for tick, operation in sequence_operations(game, "deadmanspoker_showdown")
        if operation.kind == "sound" and operation.sound == SOUND_REVEAL_PRIVATE_CARDS
    ]
    assert reveal_ticks == [0, PRIVATE_REVEAL_DELAY_TICKS, PRIVATE_REVEAL_DELAY_TICKS * 2]


def test_active_sequences_are_serialization_safe() -> None:
    game = make_game(2)
    start_to_decision(game)
    advance_to_flop(game)
    actor = game.current_player
    assert actor is not None

    game.execute_action(actor, "all_in")
    payload = game.to_json()
    restored = DeadMansPokerGame.from_json(payload)
    restored_actor = restored.get_player_by_id(actor.id)

    assert restored.phase == PHASE_ALL_IN_RESPONSE
    assert restored.active_sequences
    assert restored_actor is not None
    assert restored_actor.committed_bullets == MAX_BULLETS


def test_hand_start_message_distinguishes_all_alive_from_survivors() -> None:
    game = make_game(2)
    game.status = "playing"
    game.game_active = True
    user = game.get_user(game.players[0])
    assert user is not None
    user.clear_messages()

    game.hand_number = 1
    game.on_sequence_callback("test", "announce_hand_start", {})
    assert any("Everyone commits" in text for text in speech_texts(user))

    game.players[1].eliminated = True
    user.clear_messages()
    game.hand_number = 2
    game.on_sequence_callback("test", "announce_hand_start", {})
    assert any("Each survivor commits" in text for text in speech_texts(user))


def test_localization_and_documentation_are_present() -> None:
    en_file = ROOT / "server" / "locales" / "en" / "deadmanspoker.ftl"
    vi_file = ROOT / "server" / "locales" / "vi" / "deadmanspoker.ftl"
    assert en_file.exists()
    assert vi_file.exists()
    assert locale_keys(en_file) == locale_keys(vi_file)
    assert Localization.get("en", "game-name-deadmanspoker") == "Dead Man's Poker"
    assert Localization.get("vi", "game-name-deadmanspoker") == "Poker Tử Thần"
    assert (ROOT / "server" / "documentation" / "content" / "en" / "games" / "deadmanspoker.md").exists()
    assert (ROOT / "server" / "documentation" / "content" / "vi" / "games" / "deadmanspoker.md").exists()
