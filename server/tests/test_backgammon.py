"""Tests for Backgammon."""

from pathlib import Path

import pytest

from ..games.backgammon.game import (
    BackgammonBoard,
    BackgammonGame,
    BackgammonMove,
    BackgammonOptions,
    COLOR_RED,
    COLOR_WHITE,
    SOUND_TURN,
    TURN_PHASE_DOUBLING,
    TURN_PHASE_MOVING,
    TURN_PHASE_PRE_ROLL,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(start: bool = False, bot_second: bool = False, **option_overrides) -> BackgammonGame:
    game = BackgammonGame(options=BackgammonOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player("Alice", MockUser("Alice", uuid="p1"))
    if bot_second:
        game.add_player("Bot", Bot("Bot", uuid="p2"))
    else:
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = "Alice"
    if start:
        game.on_start()
    return game


def advance_until(game: BackgammonGame, condition, max_ticks: int = 500) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def set_board(game: BackgammonGame, *, points=None, red_bar=0, white_bar=0, red_off=0, white_off=0) -> None:
    game.board = BackgammonBoard(
        points=list(points or ([0] * 24)),
        bar_red=red_bar,
        bar_white=white_bar,
        off_red=red_off,
        off_white=white_off,
    )


class TestRegistration:
    def test_game_registered(self) -> None:
        assert GameRegistry.get("backgammon") is BackgammonGame

    def test_class_methods_and_defaults(self) -> None:
        assert BackgammonGame.get_name() == "Backgammon"
        assert BackgammonGame.get_type() == "backgammon"
        assert BackgammonGame.get_category() == "category-board-games"
        assert BackgammonGame.get_min_players() == 2
        assert BackgammonGame.get_max_players() == 2
        assert BackgammonGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]
        options = BackgammonOptions()
        assert options.match_length == 5
        assert options.bot_strategy == "simple"
        assert BackgammonOptions(bot_strategy="smart").bot_strategy == "smart"


def test_on_start_assigns_colors_and_music() -> None:
    game = make_game(start=True)
    assert [player.color for player in game.players] == [COLOR_RED, COLOR_WHITE]
    sounds = game.get_user(game.players[0]).messages
    assert any(msg.type == "play_music" and msg.data["name"] == "game_ninetynine/mus.ogg" for msg in sounds)


def test_opening_roll_sets_first_turn_and_dice(monkeypatch) -> None:
    rolls = iter([6, 2, 1])
    monkeypatch.setattr("server.games.backgammon.game.random.randint", lambda a, b: next(rolls))
    game = make_game()
    game.on_start()
    assert game.current_player == game.players[0]
    assert game.turn_phase == TURN_PHASE_MOVING
    assert game.remaining_dice == [6, 2]


def test_bar_entry_moves_generated_before_other_moves() -> None:
    game = make_game()
    game.add_player  # keep import silence
    set_board(game, red_bar=1)
    moves = game._generate_moves_for_die(COLOR_RED, 1)
    assert moves == [BackgammonMove(source=-1, destination=23, die_value=1, is_hit=False, is_bear_off=False)]


def test_forced_higher_die_when_only_one_die_can_be_played() -> None:
    game = make_game()
    points = [0] * 24
    points[4] = 1
    points[2] = -2
    set_board(game, points=points)
    game.remaining_dice = [5, 3]
    legal = game._get_legal_submoves(COLOR_RED)
    assert legal == [BackgammonMove(source=4, destination=1, die_value=3)]


def test_hit_sends_opponent_checker_to_bar() -> None:
    game = make_game()
    points = [0] * 24
    points[7] = 1
    points[4] = -1
    set_board(game, points=points)
    move = BackgammonMove(source=7, destination=4, die_value=3, is_hit=True)
    game._apply_move(move, COLOR_RED)
    assert game.board.points[4] == 1
    assert game.board.bar_white == 1


def test_bear_off_points_backgammon() -> None:
    game = make_game()
    points = [0] * 24
    points[0] = 1
    points[2] = -1
    set_board(game, points=points, red_off=14, white_off=0, white_bar=1)
    assert game._game_points_for_winner(COLOR_RED) == 3


def test_double_offer_accept_and_drop_flow() -> None:
    game = make_game(start=True, match_length=5)
    red = game.players[0]
    white = game.players[1]
    game.turn_phase = TURN_PHASE_PRE_ROLL
    game.set_turn_players([red, white])

    game._action_offer_double(red, "offer_double")
    assert game.turn_phase == TURN_PHASE_DOUBLING
    assert game.pending_double_to == COLOR_WHITE

    game._action_accept_double(white, "accept_double")
    assert game.turn_phase == TURN_PHASE_PRE_ROLL
    assert game.cube_value == 2
    assert game.cube_owner == COLOR_WHITE

    game.set_turn_players([white, red])
    game._action_offer_double(white, "offer_double")
    game._action_drop_double(red, "drop_double")
    assert game.pending_double_to == ""
    assert game.score_white == 2


def test_crawford_rule_activates_for_next_game() -> None:
    game = make_game(start=True, match_length=3)
    game.score_red = 1
    game.score_white = 0
    game._award_game(COLOR_RED, 1)
    assert game.is_crawford is True
    assert game.crawford_used is True


def test_web_standard_menu_order_places_turn_info_last() -> None:
    game = make_game(start=True)
    user = game.get_user(game.players[0])
    user.client_type = "web"
    action_set = game.create_standard_action_set(game.players[0])
    order = action_set._order
    assert order.index("read_board") < order.index("check_scores")
    assert order.index("check_scores") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")
    assert order[-2:] == ["whose_turn", "whos_at_table"]


def test_turn_info_actions_hidden_for_python_but_visible_for_web() -> None:
    game = make_game(start=True)
    player = game.players[0]
    python_visible = [ra.action.id for ra in game.get_all_visible_actions(player)]
    for action_id in ("read_board", "check_status", "check_pip", "check_cube", "check_dice"):
        assert action_id not in python_visible

    user = game.get_user(player)
    user.client_type = "web"
    game.rebuild_player_menu(player)
    web_visible = [item.id for item in user.menus["turn_menu"]["items"]]
    for action_id in ("read_board", "check_status", "check_pip", "check_cube", "check_dice"):
        assert action_id in web_visible
        assert web_visible.count(action_id) == 1


def test_advance_to_next_turn_announces_once_and_only_plays_turn_sound_for_active_player() -> None:
    game = make_game(start=True)
    red = game.players[0]
    white = game.players[1]
    red_user = game.get_user(red)
    white_user = game.get_user(white)
    red_user.clear_messages()
    white_user.clear_messages()
    game.set_turn_players([red, white])
    game.turn_phase = TURN_PHASE_MOVING
    expected = Localization.get("en", "game-turn-start", player=white.name)

    game._advance_to_next_turn()

    assert red_user.get_spoken_messages().count(expected) == 1
    assert white_user.get_spoken_messages().count(expected) == 1
    assert SOUND_TURN not in red_user.get_sounds_played()
    assert white_user.get_sounds_played().count(SOUND_TURN) == 1


def test_turn_sound_respects_player_preference() -> None:
    game = make_game(start=True)
    red = game.players[0]
    white = game.players[1]
    red_user = game.get_user(red)
    white_user = game.get_user(white)
    white_user.preferences.play_turn_sound = False
    red_user.clear_messages()
    white_user.clear_messages()
    game.set_turn_players([red, white])
    game.turn_phase = TURN_PHASE_MOVING

    game._advance_to_next_turn()

    assert SOUND_TURN not in red_user.get_sounds_played()
    assert SOUND_TURN not in white_user.get_sounds_played()


def test_smart_bot_prefers_hitting_blot() -> None:
    game = make_game(bot_second=True, bot_strategy="smart")
    bot = game.players[1]
    human = game.players[0]
    bot.color = COLOR_WHITE
    human.color = COLOR_RED
    game.set_turn_players([bot, human])
    game.turn_phase = TURN_PHASE_MOVING
    game.remaining_dice = [3]
    points = [0] * 24
    points[4] = -1
    points[7] = 1
    set_board(game, points=points)
    game.rebuild_all_menus()

    assert game.bot_think(bot) == game.action_id_for_move(
        BackgammonMove(source=4, destination=7, die_value=3, is_hit=True)
    )


def test_keybinds_avoid_reserved_keys() -> None:
    game = make_game()
    reserved = {"enter", "escape", "b", "shift+b", "f3", "t", "s", "shift+s", "ctrl+m", "ctrl+q", "ctrl+u", "ctrl+s", "ctrl+r", "ctrl+i", "ctrl+f1"}
    custom_keys = {"r", "shift+d", "y", "n", "u", "v", "e", "p", "c", "x"}
    assert custom_keys.isdisjoint(reserved)
    assert all(key in game._keybinds for key in custom_keys)


def test_roll_and_move_emit_game_audio() -> None:
    game = make_game(start=True)
    red = game.players[0]
    user = game.get_user(red)

    set_board(game, points=[0] * 24)
    game.board.points[0] = 1
    game.remaining_dice = [1]
    game.turn_phase = TURN_PHASE_MOVING
    game.set_turn_players([red, game.players[1]])

    move = BackgammonMove(source=0, destination=24, die_value=1, is_bear_off=True)
    game._action_move_option(red, game.action_id_for_move(move))

    assert any(msg.type == "play_sound" for msg in user.messages)
    assert any(msg.type == "speak" and msg.data["buffer"] == "game" for msg in user.messages)


def test_bot_can_finish_simple_game() -> None:
    game = make_game(start=True, bot_second=True, match_length=1)
    red = game.players[0]
    bot = game.players[1]
    game.set_turn_players([bot, red])
    game.turn_phase = TURN_PHASE_MOVING
    game.remaining_dice = [1]
    points = [0] * 24
    points[23] = -1
    set_board(game, points=points, white_off=14, red_off=14)
    game.rebuild_all_menus()

    assert advance_until(game, lambda: game.match_winner_color == COLOR_WHITE)


def test_serialization_preserves_state() -> None:
    game = make_game(start=True, match_length=7)
    game.score_red = 3
    game.score_white = 2
    game.cube_value = 4
    game.turn_phase = TURN_PHASE_MOVING
    game.remaining_dice = [6, 1]
    payload = game.to_json()
    loaded = BackgammonGame.from_json(payload)
    assert loaded.score_red == 3
    assert loaded.score_white == 2
    assert loaded.cube_value == 4
    assert loaded.remaining_dice == [6, 1]
