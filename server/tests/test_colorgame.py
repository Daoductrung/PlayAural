"""Tests for Color Game."""

from pathlib import Path
import random
from unittest.mock import patch

from ..games.colorgame.game import (
    ColorGameGame,
    ColorGameOptions,
    PHASE_ROLLING,
    RISK_CONFIRM_TICKS,
    evaluate_color_bet,
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
    start: bool = False,
    bot_all: bool = False,
    web_first: bool = False,
    **option_overrides,
) -> ColorGameGame:
    game = ColorGameGame(options=ColorGameOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if web_first and index == 0:
                user.client_type = "web"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def advance_until(game: ColorGameGame, condition, max_ticks: int = 400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def test_game_registered_and_defaults() -> None:
    assert GameRegistry.get("colorgame") is ColorGameGame
    game = ColorGameGame()
    assert game.get_name() == "Color Game"
    assert game.get_type() == "colorgame"
    assert game.get_category() == "dice"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 6
    assert game.get_supported_leaderboards() == ["wins", "games_played"]
    assert game.relevant_preferences == [
        "brief_announcements",
        "confirm_destructive_actions",
    ]
    assert game.options.starting_bankroll == 100
    assert game.options.minimum_bet == 1


def test_evaluate_color_bet_matches_traditional_payouts() -> None:
    assert evaluate_color_bet(5, 0) == (0, -5)
    assert evaluate_color_bet(5, 1) == (10, 5)
    assert evaluate_color_bet(5, 2) == (15, 10)
    assert evaluate_color_bet(5, 3) == (20, 15)


def test_prestart_validate_checks_bet_constraints() -> None:
    game = make_game(maximum_total_bet=3, minimum_bet=5)
    assert (
        "colorgame-error-max-bet-too-small",
        {"maximum": 3, "minimum": 5},
    ) in game.prestart_validate()

    game = make_game(starting_bankroll=10, maximum_total_bet=20)
    assert (
        "colorgame-error-max-bet-too-large",
        {"maximum": 20, "bankroll": 10},
    ) in game.prestart_validate()

    game = make_game(
        starting_bankroll=10,
        minimum_bet=11,
        maximum_total_bet=11,
    )
    assert (
        "colorgame-error-minimum-exceeds-bankroll",
        {"minimum": 11, "bankroll": 10},
    ) in game.prestart_validate()


def test_selecting_color_opens_dynamic_quick_bet_menu() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "set_bet_red")

    items = user.get_current_menu_items("action_input_menu")
    assert [item.id for item in items] == [
        "minimum:1",
        "quarter:5",
        "half:10",
        "all_in:20",
        "custom",
        "_cancel",
    ]
    assert game._pending_actions[player.id] == "set_bet_red"


def test_quick_bets_respect_other_colors_and_can_clear_one_color() -> None:
    game = make_game(start=True)
    player = game.players[0]
    player.current_bets = {"red": 8, "blue": 6}
    game._pending_actions[player.id] = "set_bet_green"

    assert game._quick_bet_options(player) == [
        "minimum:1",
        "half:3",
        "preset:5",
        "all_in:6",
        "custom",
    ]

    game._pending_actions[player.id] = "set_bet_red"
    assert game._quick_bet_options(player)[-2:] == ["clear", "custom"]


def test_new_color_is_disabled_when_remaining_capacity_is_below_minimum() -> None:
    game = make_game(
        start=True,
        minimum_bet=5,
        maximum_total_bet=10,
    )
    player = game.players[0]
    player.current_bets = {"red": 8}

    assert game._is_set_bet_enabled(player, action_id="set_bet_blue") == (
        "colorgame-no-room-for-color-bet",
        {"minimum": 5, "available": 2},
    )
    assert game._is_set_bet_enabled(player, action_id="set_bet_red") is None


def test_player_below_minimum_is_out_instead_of_soft_locked() -> None:
    game = make_game(
        start=True,
        minimum_bet=5,
        maximum_total_bet=10,
    )
    eliminated, survivor = game.players
    eliminated.bankroll = 4
    survivor.bankroll = 20

    game._reset_round_state()

    assert eliminated not in game._live_players()
    assert eliminated.bets_locked is True
    assert game._should_finish_now() is True
    assert game._is_set_bet_enabled(eliminated, action_id="set_bet_red") == (
        "colorgame-below-minimum-bankroll",
        {"bankroll": 4, "minimum": 5},
    )


def test_quick_bet_selection_updates_wager_and_returns_focus_to_color() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "set_bet_red")
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "quarter:5",
        },
    )

    assert player.current_bets == {"red": 5}
    menu = user.menus["turn_menu"]
    assert menu["selection_id"] == "set_bet_red"


def test_custom_bet_chains_to_editbox_without_losing_context() -> None:
    game = make_game(start=True)
    player = game.players[0]

    game.execute_action(player, "set_bet_blue")
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "custom",
        },
    )
    assert game._pending_actions[player.id] == "custom_bet_blue"

    game.handle_event(
        player,
        {
            "type": "editbox",
            "input_id": "action_input_editbox",
            "text": "7",
        },
    )
    assert player.current_bets == {"blue": 7}


def test_all_in_respects_risky_action_confirmation() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "set_bet_red", "all_in:20")
    assert player.current_bets == {}
    assert player.pending_risky_action == "all_in:red:20"
    assert player.risky_confirm_ticks == RISK_CONFIRM_TICKS
    assert any(
        "repeat the same all-in choice" in message.lower()
        for message in user.get_spoken_messages()
    )

    game.execute_action(player, "set_bet_red", "all_in:20")
    assert player.current_bets == {"red": 20}
    assert player.pending_risky_action == ""


def test_all_in_confirmation_keeps_color_menu_open_for_repeat() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "set_bet_red")
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "all_in:20",
        },
    )

    assert player.current_bets == {}
    assert player.pending_risky_action == "all_in:red:20"
    assert game._pending_actions[player.id] == "set_bet_red"
    assert user.menus["action_input_menu"]["selection_id"] == "all_in:20"

    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "all_in:20",
        },
    )

    assert player.current_bets == {"red": 20}
    assert player.pending_risky_action == ""
    assert player.id not in game._pending_actions


def test_cancelled_all_in_confirmation_clears_pending_risky_action() -> None:
    game = make_game(start=True)
    player = game.players[0]

    game.execute_action(player, "set_bet_red")
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "all_in:20",
        },
    )
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "_cancel",
        },
    )

    assert player.current_bets == {}
    assert player.pending_risky_action == ""
    assert player.risky_confirm_ticks == 0
    assert player.id not in game._pending_actions


def test_all_in_confirmation_can_be_disabled_per_player() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.preferences.confirm_destructive_actions = False

    game.execute_action(player, "set_bet_red", "all_in:20")

    assert player.current_bets == {"red": 20}
    assert player.risky_confirm_ticks == 0


def test_locking_no_bet_requires_confirmation_when_enabled() -> None:
    game = make_game(start=True)
    player = game.players[0]

    game.execute_action(player, "confirm_bets")
    assert player.bets_locked is False
    assert player.pending_risky_action == "sit_out"

    game.execute_action(player, "confirm_bets")
    assert player.bets_locked is True
    assert player.pending_risky_action == ""


def test_risky_confirmation_expires() -> None:
    game = make_game(start=True)
    player = game.players[0]
    game.execute_action(player, "confirm_bets")

    player.risky_confirm_ticks = 1
    game.on_tick()

    assert player.risky_confirm_ticks == 0
    assert player.pending_risky_action == ""


def test_betting_actions_remain_visible_as_focus_anchors() -> None:
    game = make_game(start=True)
    player = game.players[0]
    player.bets_locked = True
    game.phase = PHASE_ROLLING

    visible_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(player)
    }

    assert "set_bet_red" in visible_ids
    assert "clear_bets" in visible_ids
    assert "confirm_bets" in visible_ids
    assert game._is_set_bet_enabled(player, action_id="set_bet_red") == (
        "colorgame-betting-closed"
    )


def test_brief_result_announcements_are_personalized_per_listener() -> None:
    game = make_game(start=True)
    actor, observer = game.players
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.preferences.brief_announcements = True

    game._broadcast_actor_l(
        actor,
        "colorgame-you-won",
        "colorgame-player-won",
        brief_personal_key="colorgame-you-won-brief",
        brief_others_key="colorgame-player-won-brief",
        amount=5,
        bankroll=105,
    )

    assert actor_user.get_spoken_messages()[-1] == "You: +5, 105."
    assert observer_user.get_spoken_messages()[-1] == (
        "Player1 wins 5 chips and rises to 105."
    )


def test_on_start_initializes_bankrolls_and_music() -> None:
    game = make_game(start=True)
    assert game.status == "playing"
    assert game.round == 1
    assert all(player.bankroll == 100 for player in game.players)
    user = game.get_user(game.players[0])
    assert user is not None
    assert any(
        message.type == "play_music" and message.data["name"] == "game_pig/mus.ogg"
        for message in user.messages
    )


def test_players_can_bet_simultaneously_and_round_resolves() -> None:
    game = make_game(start=True)
    p1, p2 = game.players

    game.execute_action(p1, "set_bet_red", "5")
    game.execute_action(p2, "set_bet_blue", "4")
    assert p1.current_bets == {"red": 5}
    assert p2.current_bets == {"blue": 4}

    with patch("server.games.colorgame.game.roll_colors", return_value=["red", "red", "green"]):
        with patch("server.games.colorgame.game.random.randint", return_value=1):
            game.execute_action(p1, "confirm_bets")
            assert game.phase == "betting"
            game.execute_action(p2, "confirm_bets")
            assert game.has_active_sequence(sequence_id="colorgame_roll")

    assert advance_until(game, lambda: game.round == 2)
    assert p1.bankroll == 110
    assert p2.bankroll == 96
    assert game.last_roll == ["red", "red", "green"]


def test_invalid_bet_above_cap_speaks_error() -> None:
    game = make_game(start=True, starting_bankroll=10, maximum_total_bet=6)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "set_bet_red", "7")
    assert player.current_bets == {}
    assert any("cannot exceed" in message.lower() for message in user.get_spoken_messages())


def test_timer_auto_locks_and_rolls() -> None:
    game = make_game(start=True, betting_timer_seconds=1)
    p1, p2 = game.players
    game.execute_action(p1, "set_bet_red", "5")

    with patch("server.games.colorgame.game.roll_colors", return_value=["yellow", "yellow", "yellow"]):
        with patch("server.games.colorgame.game.random.randint", return_value=1):
            assert advance_until(game, lambda: game.has_active_sequence(sequence_id="colorgame_roll"))
    assert p1.bets_locked is True
    assert p2.bets_locked is True


def test_roll_sequence_resumes_after_restore() -> None:
    game = make_game(start=True, round_limit=3)
    p1, p2 = game.players
    user1 = game.get_user(p1)
    user2 = game.get_user(p2)

    game.execute_action(p1, "set_bet_red", "5")
    game.execute_action(p2, "set_bet_blue", "5")
    with patch("server.games.colorgame.game.roll_colors", return_value=["blue", "blue", "white"]):
        with patch("server.games.colorgame.game.random.randint", return_value=1):
            game.execute_action(p1, "confirm_bets")
            game.execute_action(p2, "confirm_bets")

    payload = game.to_json()
    restored = ColorGameGame.from_json(payload)
    if user1:
        restored.attach_user(p1.id, user1)
    if user2:
        restored.attach_user(p2.id, user2)
    restored.rebuild_runtime_state()

    assert advance_until(
        restored, lambda: not restored.has_active_sequence(sequence_id="colorgame_roll")
    )
    assert restored.last_roll == ["blue", "blue", "white"]
    assert restored.players[0].bankroll == 95
    assert restored.players[1].bankroll == 110


def test_web_info_actions_visible() -> None:
    waiting_game = make_game(web_first=True)
    web_player = waiting_game.players[0]
    waiting_actions = {
        entry.action.id for entry in waiting_game.get_all_visible_actions(web_player)
    }
    assert "whos_at_table" in waiting_actions

    active_game = make_game(web_first=True, start=True)
    web_player = active_game.players[0]
    active_actions = {
        entry.action.id for entry in active_game.get_all_visible_actions(web_player)
    }
    assert "check_status" in active_actions
    assert "check_bets" in active_actions
    assert "check_last_roll" in active_actions
    assert "check_scores" in active_actions


def test_round_limit_finishes_game_by_bankroll() -> None:
    game = make_game(start=True, round_limit=1, win_condition="highest_bankroll")
    p1, p2 = game.players
    game.execute_action(p1, "set_bet_red", "5")
    game.execute_action(p2, "set_bet_blue", "5")

    with patch("server.games.colorgame.game.roll_colors", return_value=["red", "yellow", "white"]):
        with patch("server.games.colorgame.game.random.randint", return_value=1):
            game.execute_action(p1, "confirm_bets")
            game.execute_action(p2, "confirm_bets")

    assert advance_until(game, lambda: game.status == "finished")
    assert game.status == "finished"
    assert p1.bankroll == 105
    assert p2.bankroll == 95


def test_tied_standings_share_rank_and_end_screen_announces_tie() -> None:
    game = make_game(start=True)
    p1, p2 = game.players
    p1.bankroll = p2.bankroll = 100
    p1.profitable_rounds = p2.profitable_rounds = 2
    p1.biggest_win = p2.biggest_win = 10

    standings = game._standings_lines("en")
    assert standings[0].startswith("1. Player1")
    assert standings[1].startswith("1. Player2")

    result = game.build_game_result()
    lines = game.format_end_screen(result, "en")
    assert "Tied winners: Player1 and Player2." in lines
    assert sum(line.startswith("1. Player") for line in lines) == 2


def test_bot_game_completes() -> None:
    random.seed(12345)
    game = make_game(
        player_count=3,
        start=True,
        bot_all=True,
        round_limit=4,
        starting_bankroll=25,
        maximum_total_bet=6,
    )
    assert advance_until(game, lambda: game.status == "finished", max_ticks=12000)
    assert game.status == "finished"
