"""Tests for Color Game."""

from pathlib import Path
import random
from unittest.mock import patch

from ..games.colorgame.game import (
    ColorGameGame,
    ColorGameOptions,
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
    assert game.options.starting_bankroll == 100
    assert game.options.minimum_bet == 1


def test_evaluate_color_bet_matches_traditional_payouts() -> None:
    assert evaluate_color_bet(5, 0) == (0, -5)
    assert evaluate_color_bet(5, 1) == (10, 5)
    assert evaluate_color_bet(5, 2) == (15, 10)
    assert evaluate_color_bet(5, 3) == (20, 15)


def test_prestart_validate_checks_bet_constraints() -> None:
    game = make_game(maximum_total_bet=3, minimum_bet=5)
    assert "colorgame-error-max-bet-too-small" in game.prestart_validate()

    game = make_game(starting_bankroll=10, maximum_total_bet=20)
    assert "colorgame-error-max-bet-too-large" in game.prestart_validate()


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
