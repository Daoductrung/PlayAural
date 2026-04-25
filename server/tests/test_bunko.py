"""Tests for Bunko."""

from pathlib import Path
import random
from unittest.mock import patch

from ..games.bunko.game import (
    BunkoGame,
    BunkoOptions,
    WINNING_MODE_TOTAL_SCORE,
    evaluate_roll,
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
) -> BunkoGame:
    game = BunkoGame(options=BunkoOptions(**option_overrides))
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


def advance_until(game: BunkoGame, condition, max_ticks: int = 400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def test_game_registered_and_defaults() -> None:
    assert GameRegistry.get("bunko") is BunkoGame
    game = BunkoGame()
    assert game.get_name() == "Bunko"
    assert game.get_type() == "bunko"
    assert game.get_category() == "dice"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 6
    assert game.get_supported_leaderboards() == ["wins", "rating", "games_played"]
    assert game.options.round_count == 6
    assert game.options.winning_mode == "round_wins"


def test_evaluate_roll_scores_authentically() -> None:
    assert evaluate_roll([3, 3, 3], 3) == ("bunko", 21)
    assert evaluate_roll([4, 4, 4], 3) == ("mini_bunko", 5)
    assert evaluate_roll([3, 3, 5], 3) == ("match", 2)
    assert evaluate_roll([1, 2, 4], 3) == ("no_score", 0)


def test_on_start_initializes_round_and_music() -> None:
    game = make_game(start=True)

    assert game.status == "playing"
    assert game.round == 1
    assert game.current_target_number == 1
    assert game.current_player == game.players[0]

    user = game.get_user(game.players[0])
    assert user is not None
    assert any(
        message.type == "play_music" and message.data["name"] == "game_pig/mus.ogg"
        for message in user.messages
    )


def test_roll_match_scores_and_keeps_turn() -> None:
    game = make_game(start=True)
    player = game.players[0]

    with patch("server.games.bunko.game.random.randint", side_effect=[1, 1, 4]):
        game.execute_action(player, "roll")

    assert advance_until(game, lambda: not game.has_active_sequence(sequence_id="bunko_roll"))
    assert player.round_score == 2
    assert player.total_score == 2
    assert game.current_player == player
    assert game.last_roll_outcome == "match"


def test_mini_bunko_scores_five_points() -> None:
    game = make_game(start=True)
    player = game.players[0]

    with patch("server.games.bunko.game.random.randint", side_effect=[4, 4, 4]):
        game.execute_action(player, "roll")

    assert advance_until(game, lambda: not game.has_active_sequence(sequence_id="bunko_roll"))
    assert player.round_score == 5
    assert player.total_score == 5
    assert player.mini_bunkos == 1
    assert game.last_roll_outcome == "mini_bunko"


def test_bunko_ends_round_and_next_round_starts_left_of_winner() -> None:
    game = make_game(player_count=3, start=True)
    winner = game.players[0]

    with patch("server.games.bunko.game.random.randint", side_effect=[1, 1, 1]):
        game.execute_action(winner, "roll")

    assert advance_until(game, lambda: game.round == 2)
    assert winner.rounds_won == 1
    assert winner.total_score == 21
    assert winner.bunkos == 1
    assert winner.round_score == 0
    assert game.current_target_number == 2
    assert game.current_player == game.players[1]


def test_no_score_passes_turn() -> None:
    game = make_game(start=True)
    player = game.players[0]

    with patch("server.games.bunko.game.random.randint", side_effect=[2, 3, 4]):
        game.execute_action(player, "roll")

    assert advance_until(game, lambda: not game.has_active_sequence(sequence_id="bunko_roll"))
    assert player.round_score == 0
    assert game.current_player == game.players[1]
    assert game.last_roll_outcome == "no_score"


def test_roll_sequence_resumes_after_restore() -> None:
    game = make_game(start=True)
    player1 = game.players[0]
    player2 = game.players[1]
    user1 = game.get_user(player1)
    user2 = game.get_user(player2)

    with patch("server.games.bunko.game.random.randint", side_effect=[1, 1, 4]):
        game.execute_action(player1, "roll")

    assert game.has_active_sequence(sequence_id="bunko_roll") is True

    payload = game.to_json()
    restored = BunkoGame.from_json(payload)
    if user1:
        restored.attach_user(player1.id, user1)
    if user2:
        restored.attach_user(player2.id, user2)
    restored.rebuild_runtime_state()

    assert advance_until(
        restored, lambda: not restored.has_active_sequence(sequence_id="bunko_roll")
    )
    restored_player1 = restored.players[0]
    assert restored_player1.round_score == 2
    assert restored.current_player == restored_player1


def test_web_info_actions_visible_in_waiting_and_playing_states() -> None:
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
    assert "check_last_roll" in active_actions
    assert "check_scores" in active_actions


def test_check_scores_uses_selected_winning_mode_order() -> None:
    game = make_game(start=True, winning_mode=WINNING_MODE_TOTAL_SCORE)
    player1 = game.players[0]
    player2 = game.players[1]
    user = game.get_user(player1)
    assert isinstance(user, MockUser)

    player1.total_score = 20
    player1.rounds_won = 1
    player2.total_score = 35
    player2.rounds_won = 0
    user.clear_messages()
    game.execute_action(player1, "check_scores")

    spoken = " ".join(user.get_spoken_messages())
    assert spoken.index("Player2") < spoken.index("Player1")


def test_bot_game_completes() -> None:
    random.seed(1234)
    game = make_game(
        player_count=3,
        start=True,
        bot_all=True,
        round_count=2,
    )

    assert advance_until(game, lambda: game.status == "finished", max_ticks=12000)
    assert game.status == "finished"
