"""Tests for Dead Man's Poker."""

from pathlib import Path
import random

from server.games.deadmanspoker.bot import (
    bot_select_switch_card,
    bot_think as deadmanspoker_bot_think,
)
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
from server.game_utils.actions import Visibility
from server.game_utils.cards import Card, card_name
from server.game_utils.sequence_runner_mixin import SequenceOperation
from server.games.registry import GameRegistry
from server.messages.localization import Localization
from server.ui.keybinds import KeybindState
from server.users.bot import Bot
from server.users.network_user import NetworkUser
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


def make_network_touch_game(
    player_count: int = 3,
) -> tuple[DeadMansPokerGame, list[NetworkUser]]:
    game = DeadMansPokerGame()
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
        game.flush_menus()
    return condition()


def start_to_decision(game: DeadMansPokerGame) -> None:
    game.on_start()
    game.flush_menus()
    assert advance_until(
        game,
        lambda: game.phase == PHASE_DECISION and not game.active_sequences,
        max_ticks=1000,
    )


def sound_names(user: MockUser) -> list[str]:
    return [message.data["name"] for message in user.messages if message.type == "play_sound"]


def speech_texts(user: MockUser) -> list[str]:
    return [message.data["text"] for message in user.messages if message.type == "speak"]


def turn_menu_updates(user: MockUser):
    return [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]


def menu_item_ids(user: MockUser, menu_id: str = "turn_menu") -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [getattr(item, "id", str(item)) for item in items]


def network_turn_menu_packets(user: NetworkUser) -> list[dict]:
    return [
        packet
        for packet in user.get_queued_messages()
        if packet.get("type") == "menu" and packet.get("menu_id") == "turn_menu"
    ]


def network_current_menu_item_ids(
    user: NetworkUser, menu_id: str = "turn_menu"
) -> list[str]:
    menu = user._current_menus[menu_id]
    return [
        item.get("id", str(item)) if isinstance(item, dict) else str(item)
        for item in menu["items"]
    ]


def status_texts(user: MockUser) -> list[str]:
    items = user.get_current_menu_items("status_box") or []
    return [getattr(item, "text", str(item)) for item in items]


def status_ids(user: MockUser) -> list[str | None]:
    items = user.get_current_menu_items("status_box") or []
    return [getattr(item, "id", None) for item in items]


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
    game.flush_menus()

    assert advance_until(game, lambda: game.status == "finished", max_ticks=60000)


def test_bot_waits_for_community_before_switching(monkeypatch) -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_DECISION
    game.round_stage = 1
    game.community = []
    game.revealed_community_count = 0
    player.hand = [Card(id=1, rank=2, suit=1), Card(id=2, rank=7, suit=2)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
        hand_player.committed_bullets = 1
    player.acted_this_hand = True
    game.set_turn_players([player])
    monkeypatch.setattr(random, "random", lambda: 0.0)

    assert game.bot_think(player) != "switch_card"


def test_bot_switches_after_flop_when_private_cards_do_not_help(monkeypatch) -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_DECISION
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=3, suit=3),
    ]
    game.revealed_community_count = 3
    player.hand = [Card(id=4, rank=2, suit=4), Card(id=5, rank=7, suit=1)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
        hand_player.committed_bullets = 2
    player.acted_this_hand = True
    game.set_turn_players([player])
    monkeypatch.setattr(random, "random", lambda: 0.0)

    assert game.bot_think(player) == "switch_card"


def test_bot_switches_dead_card_when_chasing_flush(monkeypatch) -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_DECISION
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=2, suit=3),
        Card(id=2, rank=6, suit=3),
        Card(id=3, rank=10, suit=3),
    ]
    game.revealed_community_count = 3
    player.hand = [Card(id=4, rank=13, suit=3), Card(id=5, rank=3, suit=2)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
        hand_player.committed_bullets = 2
    player.acted_this_hand = True
    game.set_turn_players([player])
    monkeypatch.setattr(random, "random", lambda: 0.0)

    assert game.bot_think(player) == "switch_card"
    assert bot_select_switch_card(game, player, ["0", "1"]) == "1"


def test_bot_records_missed_draw_after_switch_choice() -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_SWITCH
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=2, suit=3),
        Card(id=2, rank=6, suit=3),
        Card(id=3, rank=10, suit=3),
    ]
    game.revealed_community_count = 3
    player.hand = [Card(id=4, rank=13, suit=3), Card(id=5, rank=3, suit=2)]
    player.active_in_hand = True
    player.bot_switch_round_stage = 2
    player.bot_switch_plan = "draw"
    player.bot_switch_float_bias = 0.5
    game.pending_switch_player_id = player.id
    game.pending_switch_card_index = 1
    game.pending_switch_candidates = [
        Card(id=6, rank=4, suit=2),
        Card(id=7, rank=5, suit=1),
        Card(id=8, rank=7, suit=4),
    ]
    game.pending_switch_previous_phase = PHASE_DECISION

    game._action_choose_switch(player, "choose_switch_0")

    assert player.used_switch
    assert player.bot_switch_missed
    assert player.bot_switch_plan == "draw"


def test_bot_mixes_after_missed_round_two_switch(monkeypatch) -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_DECISION
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=2, suit=3),
        Card(id=2, rank=6, suit=3),
        Card(id=3, rank=10, suit=3),
    ]
    game.revealed_community_count = 3
    player.hand = [Card(id=4, rank=13, suit=3), Card(id=6, rank=4, suit=2)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
        hand_player.committed_bullets = 2
    player.acted_this_hand = True
    player.used_switch = True
    player.bot_switch_round_stage = 2
    player.bot_switch_plan = "draw"
    player.bot_switch_missed = True
    player.bot_switch_float_bias = 0.5
    game.set_turn_players([player])

    monkeypatch.setattr(random, "random", lambda: 0.0)
    assert game.bot_think(player) == "fold"

    monkeypatch.setattr(random, "random", lambda: 0.99)
    assert game.bot_think(player) == "call"


def test_bot_does_not_panic_fold_after_heavy_commitment(monkeypatch) -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_DECISION
    game.round_stage = 3
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=3, suit=3),
        Card(id=4, rank=5, suit=4),
        Card(id=5, rank=8, suit=1),
    ]
    game.revealed_community_count = 5
    player.hand = [Card(id=6, rank=2, suit=2), Card(id=7, rank=7, suit=3)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
        hand_player.committed_bullets = 5
    player.acted_this_hand = True
    game.set_turn_players([player])
    monkeypatch.setattr(random, "random", lambda: 0.0)

    assert game.bot_think(player) != "fold"


def test_bot_folds_garbage_to_early_all_in(monkeypatch) -> None:
    game = make_bot_game(2)
    responder = game.players[0]
    initiator = game.players[1]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_ALL_IN_RESPONSE
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=3, suit=3),
    ]
    game.revealed_community_count = 3
    responder.hand = [Card(id=4, rank=2, suit=4), Card(id=5, rank=7, suit=1)]
    initiator.hand = [Card(id=6, rank=1, suit=1), Card(id=7, rank=13, suit=2)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
    responder.committed_bullets = 2
    initiator.committed_bullets = MAX_BULLETS
    initiator.matched_all_in = True
    game.set_turn_players([responder])
    monkeypatch.setattr(random, "random", lambda: 0.0)

    assert game.bot_think(responder) == "fold"


def test_bot_calls_all_in_with_strong_made_hand(monkeypatch) -> None:
    game = make_bot_game(2)
    responder = game.players[0]
    initiator = game.players[1]
    game.status = "playing"
    game.game_active = True
    game.phase = PHASE_ALL_IN_RESPONSE
    game.round_stage = 2
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=12, suit=3),
    ]
    game.revealed_community_count = 3
    responder.hand = [Card(id=4, rank=13, suit=4), Card(id=5, rank=1, suit=1)]
    initiator.hand = [Card(id=6, rank=2, suit=1), Card(id=7, rank=2, suit=2)]
    for hand_player in game.players:
        hand_player.active_in_hand = True
    responder.committed_bullets = 2
    initiator.committed_bullets = MAX_BULLETS
    initiator.matched_all_in = True
    game.set_turn_players([responder])
    monkeypatch.setattr(random, "random", lambda: 0.99)

    assert game.bot_think(responder) == "call"


def test_bot_switch_selection_keeps_board_made_pair() -> None:
    game = make_bot_game(2)
    player = game.players[0]
    game.community = [
        Card(id=1, rank=2, suit=1),
        Card(id=2, rank=13, suit=2),
        Card(id=3, rank=12, suit=3),
    ]
    game.revealed_community_count = 3
    player.hand = [Card(id=4, rank=2, suit=4), Card(id=5, rank=1, suit=1)]

    assert bot_select_switch_card(game, player, ["0", "1"]) == "1"


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
        "ctrl+i",
        "ctrl+f1",
    }
    game_keys = {"c", "f", "d", "shift+a", "w", "g", "e", "v", "p"}
    assert game_keys.isdisjoint(reserved)
    for key in game_keys:
        assert key in game._keybinds
        assert all(binding.state == KeybindState.ACTIVE for binding in game._keybinds[key])
    assert "shift+f" not in game._keybinds
    assert "h" not in game._keybinds
    assert not any(binding.actions == ["all_in"] for binding in game._keybinds.get("r", []))
    assert any(binding.include_spectators for binding in game._keybinds["e"])
    assert any(binding.include_spectators for binding in game._keybinds["v"])
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


def test_read_table_and_revolvers_use_live_status_boxes() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.execute_action(player, "read_table")

    table_texts = status_texts(user)
    assert "status_box" in user.menus
    assert status_ids(user)[:3] == ["hand", "community", "turn"]
    assert user.menus["status_box"]["selection_id"] == "hand"
    assert any("Hand" in text and "betting round" in text for text in table_texts)
    assert any("Community:" in text for text in table_texts)
    assert any(text.startswith("Player1:") for text in table_texts)
    assert [message.type for message in user.messages] == ["show_menu"]

    user.clear_messages()
    game.execute_action(player, "read_revolvers")

    revolver_texts = status_texts(user)
    assert status_ids(user)[0] == "header"
    assert user.menus["status_box"]["selection_id"] == "header"
    assert revolver_texts[0] == "Revolver risk"
    assert any(text.startswith("Player1:") for text in revolver_texts)
    assert [message.type for message in user.messages] == ["show_menu"]

    game.players[0].committed_bullets = 4
    game.refresh_menus(player)
    game.flush_menus()

    assert any("4 bullets committed" in text for text in status_texts(user))


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
        "read_revolvers",
    ]
    info_labels = [
        Localization.get("en", "deadmanspoker-read-hand"),
        Localization.get("en", "deadmanspoker-read-community-cards"),
        Localization.get("en", "deadmanspoker-read-hand-value"),
        Localization.get("en", "deadmanspoker-read-table"),
        Localization.get("en", "deadmanspoker-read-revolvers"),
    ]

    assert "read_card_counts" not in item_ids
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
    player_user = game.get_user(player)
    assert player_user is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None
    old_hand = list(player.hand)
    discarded = old_hand[0]
    other_user.clear_messages()

    game.execute_action(player, "switch_card", input_value="0")
    game.flush_menus()
    assert game.phase == PHASE_SWITCH
    assert len(game.pending_switch_candidates) == 3
    assert turn_menu_updates(other_user) == []

    player_user.clear_messages()
    game.execute_action(player, "choose_switch_1")
    game.flush_menus()
    assert turn_menu_updates(other_user) == []
    assert [
        message.data.get("selection_id")
        for message in turn_menu_updates(player_user)
        if message.data.get("selection_id") == "call"
    ] == ["call"]
    assert advance_until(game, lambda: not game.active_sequences)

    assert game.phase == PHASE_DECISION
    assert game.current_player == player
    assert player.used_switch
    assert len(player.hand) == 2
    assert player.hand != old_hand
    # The focus jump to "call" fired exactly once; the delayed sequence
    # repaints carry no focus directive, so the client keeps the cursor on
    # "call" by item identity instead of being jumped a second time.
    assert [
        message.data.get("selection_id")
        for message in turn_menu_updates(player_user)
        if message.data.get("selection_id") == "call"
    ] == ["call"]
    assert any(
        message.data.get("selection_id") is None
        for message in turn_menu_updates(player_user)
    )
    assert any(card_name(discarded, "en") in text for text in speech_texts(other_user))


def test_human_switch_choice_does_not_pull_other_player_focus_to_call() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    player_user = game.get_user(player)
    assert player_user is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None

    game.execute_action(player, "switch_card", input_value="0")
    assert game.phase == PHASE_SWITCH
    player_user.clear_messages()
    other_user.clear_messages()

    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "choose_switch_1",
        },
    )

    # The regression this test pins: resolving one player's switch must not
    # repaint another player's menu or carry the actor's "call" focus.
    assert turn_menu_updates(other_user) == []
    assert [
        message.data.get("selection_id")
        for message in turn_menu_updates(player_user)
        if message.data.get("selection_id") == "call"
    ] == ["call"]
    assert advance_until(game, lambda: not game.active_sequences)

    other_updates = turn_menu_updates(other_user)
    assert other_updates
    assert all(message.data.get("selection_id") is None for message in other_updates)
    assert [
        message.data.get("selection_id")
        for message in turn_menu_updates(player_user)
        if message.data.get("selection_id") == "call"
    ] == ["call"]


def test_switch_card_action_does_not_refresh_other_players() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    player_user = game.get_user(player)
    assert player_user is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None
    other_user.clear_messages()

    game.handle_event(
        player,
        {
            "type": "action",
            "action": "switch_card",
            "context": {"menu_item_id": "switch_card"},
        },
    )

    assert "action_input_menu" in player_user.menus
    assert turn_menu_updates(other_user) == []
    assert menu_item_ids(other_user)[:4] == [
        "call",
        "fold",
        "switch_card",
        "all_in",
    ]
    assert all(
        not item_id.startswith("choose_switch_") for item_id in menu_item_ids(other_user)
    )


def test_switch_phase_keeps_other_players_menu_stable_during_refresh() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert other_user is not None

    other_user.clear_messages()
    game.execute_action(player, "switch_card", input_value="0")
    game.flush_menus()
    assert game.phase == PHASE_SWITCH
    baseline_ids = menu_item_ids(other_user)
    assert baseline_ids[:4] == [
        "call",
        "fold",
        "switch_card",
        "all_in",
    ]
    assert all(
        not item_id.startswith("choose_switch_") for item_id in baseline_ids
    )

    other_user.clear_messages()
    game.refresh_menus()
    game.flush_menus()

    assert menu_item_ids(other_user) == baseline_ids
    assert all(
        not item_id.startswith("choose_switch_") for item_id in menu_item_ids(other_user)
    )


def test_touch_switch_menu_keeps_primary_anchors_and_focuses_first_choice() -> None:
    game = make_touch_game(3)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    player_user = game.get_user(player)
    assert player_user is not None
    player_user.clear_messages()

    game.execute_action(player, "switch_card", input_value="0")
    game.flush_menus()

    item_ids = menu_item_ids(player_user)
    assert item_ids[:4] == [
        "call",
        "fold",
        "switch_card",
        "all_in",
    ]
    assert item_ids[4:7] == [
        "choose_switch_0",
        "choose_switch_1",
        "choose_switch_2",
    ]
    assert [
        message.data.get("selection_id")
        for message in turn_menu_updates(player_user)
        if message.data.get("selection_id") == "choose_switch_0"
    ] == ["choose_switch_0"]


def test_touch_switch_refreshes_do_not_send_redundant_non_actor_packets() -> None:
    game, users = make_network_touch_game(3)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    other = next(table_player for table_player in game.players if table_player != player)
    other_user = game.get_user(other)
    assert isinstance(other_user, NetworkUser)
    baseline_ids = network_current_menu_item_ids(other_user)
    assert baseline_ids[:4] == [
        "call",
        "fold",
        "switch_card",
        "all_in",
    ]

    for user in users:
        user.get_queued_messages()

    game.execute_action(player, "switch_card", input_value="0")
    game.flush_menus()

    assert network_turn_menu_packets(other_user) == []
    assert network_current_menu_item_ids(other_user) == baseline_ids

    for user in users:
        user.get_queued_messages()

    game.refresh_menus()
    game.flush_menus()

    assert network_turn_menu_packets(other_user) == []
    assert network_current_menu_item_ids(other_user) == baseline_ids

    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "choose_switch_1",
        },
    )

    assert network_turn_menu_packets(other_user) == []
    assert network_current_menu_item_ids(other_user) == baseline_ids

    assert advance_until(game, lambda: not game.active_sequences)
    assert network_turn_menu_packets(other_user) == []
    assert network_current_menu_item_ids(other_user) == baseline_ids


def test_switch_card_resets_each_hand() -> None:
    game = make_game(2)
    start_to_decision(game)
    for player in game.players:
        player.used_switch = True

    game._start_new_hand()

    assert all(not player.used_switch for player in game.players)


def test_fold_button_becomes_coward_fold_on_first_decision() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None

    assert game._is_fold_enabled(player) is None
    assert game._is_coward_fold_enabled(player) is None
    assert game._is_fold_hidden(player) == Visibility.VISIBLE
    assert game._is_coward_fold_hidden(player) == Visibility.HIDDEN
    assert game.get_all_visible_actions(player)[1].label == Localization.get(
        user.locale,
        "deadmanspoker-coward-fold",
    )


def test_fold_button_keeps_coward_context_after_coward_fold_is_used() -> None:
    game = make_game(2)
    start_to_decision(game)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None
    player.used_coward_fold = True
    user.clear_messages()

    assert game._is_fold_enabled(player) == "deadmanspoker-coward-used"
    assert game.get_all_visible_actions(player)[1].label == Localization.get(
        user.locale,
        "deadmanspoker-coward-fold",
    )

    game.execute_action(player, "fold")

    assert any("already used Coward's Fold" in text for text in speech_texts(user))
    assert not player.folded_this_hand


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

    game.execute_action(player, "fold")
    assert advance_until(
        game,
        lambda: game.phase == PHASE_DECISION and not game.active_sequences and game.hand_number == 2,
        max_ticks=2000,
    )

    assert player.used_coward_fold
    game.current_player = player
    assert game._is_coward_fold_enabled(player) == "deadmanspoker-coward-used"
    assert game._is_fold_enabled(player) == "deadmanspoker-coward-used"


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


def test_all_in_button_matches_all_in_during_response(monkeypatch) -> None:
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
    committed_before = responder.committed_bullets
    assert committed_before < MAX_BULLETS
    assert game._is_call_enabled(responder) is None
    assert game._is_all_in_enabled(responder) is None

    game.execute_action(responder, "all_in")

    assert responder.committed_bullets == MAX_BULLETS
    assert responder.matched_all_in
    assert responder.all_ins_matched == 1
    assert initiator.all_ins_initiated == 1
    assert game.all_in_initiator_id == initiator.id


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
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._resolve_showdown()

    assert not game.has_active_sequence(tag="deadmanspoker_roulette")
    assert all(not player.eliminated for player in game.players)
    assert all(player.showdowns_won == 0 for player in game.players)
    assert all(player.hands_won == 0 for player in game.players)
    first_user = game.get_user(game.players[0])
    assert first_user is not None
    assert any("tie the showdown" in text for text in speech_texts(first_user))
    assert any("complete draw" in text for text in speech_texts(first_user))


def test_showdown_top_tie_is_draw_and_penalizes_only_lower_hands() -> None:
    game = make_game(3)
    game.status = "playing"
    game.game_active = True
    first_tied = game.players[0]
    second_tied = game.players[1]
    lower_hand = game.players[2]
    game.community = [
        Card(id=1, rank=10, suit=1),
        Card(id=2, rank=11, suit=2),
        Card(id=3, rank=12, suit=3),
        Card(id=4, rank=13, suit=4),
        Card(id=5, rank=2, suit=1),
    ]
    game.revealed_community_count = 5
    first_tied.hand = [Card(id=6, rank=1, suit=1), Card(id=7, rank=3, suit=2)]
    second_tied.hand = [Card(id=8, rank=1, suit=2), Card(id=9, rank=4, suit=3)]
    lower_hand.hand = [Card(id=10, rank=9, suit=1), Card(id=11, rank=9, suit=2)]
    for player in game.players:
        player.active_in_hand = True
        player.committed_bullets = 2
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._resolve_showdown()

    assert first_tied.showdowns_won == 0
    assert second_tied.showdowns_won == 0
    assert first_tied.hands_won == 0
    assert second_tied.hands_won == 0
    assert lower_hand.showdowns_lost == 1
    assert not lower_hand.active_in_hand
    assert lower_hand.folded_this_hand
    assert game.pending_roulette_ids == [lower_hand.id]
    assert game.pending_roulette_context == "showdown"
    assert game.has_active_sequence(tag="deadmanspoker_roulette")
    tied_user = game.get_user(first_tied)
    assert tied_user is not None
    tied_text = " ".join(speech_texts(tied_user))
    assert "tie the showdown" in tied_text
    assert "do not win this hand" in tied_text
    assert "win the showdown" not in tied_text


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
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._resolve_showdown()

    assert winner.showdowns_won == 1
    assert winner.hands_won == 1
    result = game.build_game_result()
    assert result.custom_data["player_stats"][winner.name]["hands_won"] == 1
    winner_user = game.get_user(winner)
    assert winner_user is not None
    winner_texts = speech_texts(winner_user)
    assert any("You win the showdown with" in text for text in winner_texts)
    assert not any("win the hand at showdown" in text for text in winner_texts)


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
