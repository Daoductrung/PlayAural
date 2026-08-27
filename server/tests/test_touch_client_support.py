"""Regression tests for touch-client support across server and games."""

from pathlib import Path

import pytest

from ..game_utils.actions import Visibility
from ..game_utils.client_types import (
    is_touch_client_type,
    uses_self_voicing_settings_type,
)
from ..games.ageofheroes.game import AgeOfHeroesGame
from ..games.backgammon.game import BackgammonGame, BackgammonOptions
from ..games.battleship.game import BattleshipGame, BattleshipOptions
from ..games.chess.game import ChessGame, ChessOptions
from ..games.coup.game import CoupGame
from ..games.bunko.game import BunkoGame
from ..games.farkle.game import FarkleGame
from ..games.humanitycards.game import HumanityCardsGame
from ..games.leftrightcenter.game import LeftRightCenterGame
from ..games.lightturret.game import LightTurretGame
from ..games.ludo.game import LudoGame
from ..games.midnight.game import MidnightGame
from ..games.milebymile.game import MileByMileGame
from ..games.metalpipe.game import MetalPipeGame
from ..games.nine.game import NineGame
from ..games.ninetynine.game import NinetyNineGame
from ..games.pig.game import PigGame
from ..games.pusoydos.game import PusoyDosGame
from ..games.registry import GameRegistry
from ..games.rollingballs.game import RollingBallsGame
from ..games.senet.game import SenetGame
from ..games.snakesandladders.game import SnakesAndLaddersGame
from ..games.threes.game import ThreesGame
from ..games.tossup.game import TossUpGame
from ..games.twentyone.game import TwentyOneGame
from ..games.uno.game import UnoGame
from ..games.yahtzee.game import YahtzeeGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)

_BASE_TOUCH_WAITING_STANDARD_ACTIONS = {
    "show_actions",
    "save_table",
    "whose_turn",
    "whos_at_table",
    "check_scores",
    "check_scores_detailed",
    "predict_outcomes",
    "game_info",
    "game_rules",
}


def test_touch_client_type_helper_recognizes_mobile() -> None:
    assert is_touch_client_type("web") is True
    assert is_touch_client_type("mobile") is True
    assert is_touch_client_type("python") is False


def test_self_voicing_settings_helper_recognizes_mobile() -> None:
    assert uses_self_voicing_settings_type("web") is True
    assert uses_self_voicing_settings_type("mobile") is True
    assert uses_self_voicing_settings_type("python") is False


def test_mobile_client_label_is_localized() -> None:
    assert Localization.get("en", "client-type-mobile") == "Mobile"
    assert Localization.get("vi", "client-type-mobile") == "Di động"


def test_ludo_mobile_standard_actions_follow_touch_order() -> None:
    game = LudoGame()
    game.setup_keybinds()
    u1 = MockUser("Alice", uuid="p1")
    u2 = MockUser("Bob", uuid="p2")
    p1 = game.add_player("Alice", u1)
    game.add_player("Bob", u2)
    game.host = "Alice"
    game.on_start()

    u1.client_type = "mobile"
    action_set = game.create_standard_action_set(p1)
    order = action_set._order

    assert order.index("check_board") < order.index("check_scores")
    assert order.index("check_scores") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")

    game.refresh_menus(p1)
    game.flush_menus()
    visible_ids = [
        item.id
        for item in u1.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "web_actions_menu" in visible_ids
    assert "web_leave_table" in visible_ids


def test_milebymile_touch_info_stays_before_status_actions() -> None:
    game = MileByMileGame()
    game.setup_keybinds()
    u1 = MockUser("Alice", uuid="p1")
    u2 = MockUser("Bob", uuid="p2")
    u1.client_type = "mobile"
    p1 = game.add_player("Alice", u1)
    game.add_player("Bob", u2)
    game.host = "Alice"
    game.on_start()

    action_set = game.create_standard_action_set(p1)
    order = action_set._order

    assert order.index("info") < order.index("check_status")
    assert order.index("check_status") < order.index("whose_turn")
    assert order[-2:] == ["whose_turn", "whos_at_table"]

    game.refresh_menus(p1)
    game.flush_menus()
    visible_ids = [
        item.id
        for item in u1.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert visible_ids.index("info") < visible_ids.index("check_status")
    assert visible_ids.index("check_status") < visible_ids.index("whose_turn")
    assert visible_ids.index("whose_turn") < visible_ids.index("whos_at_table")


def _new_game_with_players(game_cls, player_count: int, client_type: str = "mobile"):
    game = game_cls()
    game.setup_keybinds()
    players = []
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = MockUser(name, uuid=f"new-game-{game.get_type()}-{index + 1}")
        if index == 0:
            user.client_type = client_type
        players.append(game.add_player(name, user))
    game.host = "Player1"
    return game, players[0]


def _touch_waiting_gameplay_action_ids(game, player) -> list[str]:
    action_ids: list[str] = []
    for action_set in game.get_action_sets(player):
        visible_ids = {
            resolved.action.id for resolved in action_set.get_visible_actions(game, player)
        }
        if action_set.name in {"lobby", "options"}:
            continue
        if action_set.name == "standard":
            action_ids.extend(sorted(visible_ids - _BASE_TOUCH_WAITING_STANDARD_ACTIONS))
        else:
            action_ids.extend(sorted(visible_ids))
    return action_ids


@pytest.mark.parametrize(
    "game_cls",
    sorted(GameRegistry.get_all(), key=lambda cls: cls.get_type()),
)
def test_touch_waiting_lobby_hides_gameplay_actions_for_all_games(game_cls) -> None:
    game, player = _new_game_with_players(game_cls, 1)

    assert game.status != "playing"
    assert _touch_waiting_gameplay_action_ids(game, player) == []


@pytest.mark.parametrize(
    ("game_cls", "action_ids"),
    [
        (CoupGame, {"check_wealth", "check_hand", "check_table"}),
        (MileByMileGame, {"check_status"}),
        (NinetyNineGame, {"check_count"}),
    ],
)
def test_touch_gameplay_info_actions_only_appear_after_start(
    game_cls, action_ids: set[str]
) -> None:
    game, player = _new_game_with_players(game_cls, 2)

    waiting_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(player)
    }
    assert action_ids.isdisjoint(waiting_ids)

    game.on_start()
    playing_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(player)
    }
    assert action_ids <= playing_ids


@pytest.mark.parametrize(
    ("game_cls", "player_count", "expected_order"),
    [
        (
            AgeOfHeroesGame,
            2,
            ["check_hand", "check_status", "check_status_detailed", "whose_turn", "whos_at_table"],
        ),
        (
            HumanityCardsGame,
            3,
            ["view_black_card", "whose_judge", "check_scores", "whose_turn", "whos_at_table"],
        ),
        (
            BackgammonGame,
            2,
            [
                "check_status",
                "check_pip",
                "check_scores",
                "check_cube",
                "check_dice",
                "check_legal_moves",
                "whose_turn",
                "whos_at_table",
            ],
        ),
        (
            NineGame,
            3,
            ["check_sequences_status", "check_hand_counts_status", "whose_turn", "whos_at_table"],
        ),
        (
            PusoyDosGame,
            3,
            [
                "check_trick",
                "read_hand",
                "read_card_counts",
                "check_turn_timer",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ],
        ),
        (
            RollingBallsGame,
            2,
            ["view_pipe", "reshuffle", "check_scores", "whose_turn", "whos_at_table"],
        ),
        (
            SenetGame,
            2,
            ["check_status", "check_sticks", "check_scores", "whose_turn", "whos_at_table"],
        ),
        (
            TwentyOneGame,
            2,
            [
                "modifier_guide",
                "check_21_status",
                "read_21_opponent_face_up",
                "read_21_hand",
                "read_21_bets",
                "read_21_active_effects",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ],
        ),
        (
            UnoGame,
            2,
            [
                "read_top",
                "read_color",
                "read_counts",
                "read_hand",
                "sort_color",
                "sort_number",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ],
        ),
    ],
)
def test_new_games_touch_standard_actions_follow_touch_order(
    game_cls, player_count: int, expected_order: list[str]
) -> None:
    game, player = _new_game_with_players(game_cls, player_count)
    action_set = game.create_standard_action_set(player)
    order = action_set._order

    positions = [order.index(action_id) for action_id in expected_order]
    assert positions == sorted(positions)


@pytest.mark.parametrize(
    ("game_cls", "player_count", "custom_actions"),
    [
        (AgeOfHeroesGame, 2, ["check_hand", "check_status", "check_status_detailed"]),
        (HumanityCardsGame, 3, ["view_black_card", "whose_judge"]),
        (
            BackgammonGame,
            2,
            [
                "check_status",
                "check_pip",
                "check_cube",
                "check_dice",
                "check_legal_moves",
            ],
        ),
        (NineGame, 3, ["check_sequences_status", "check_hand_counts_status"]),
        (PusoyDosGame, 3, ["check_trick", "read_hand", "read_card_counts", "check_turn_timer"]),
        (RollingBallsGame, 2, ["view_pipe", "reshuffle"]),
        (SenetGame, 2, ["check_status", "check_sticks"]),
        (
            TwentyOneGame,
            2,
            [
                "modifier_guide",
                "check_21_status",
                "read_21_opponent_face_up",
                "read_21_hand",
                "read_21_bets",
                "read_21_active_effects",
            ],
        ),
        (
            UnoGame,
            2,
            ["read_top", "read_color", "read_counts", "read_hand", "sort_color", "sort_number"],
        ),
    ],
)
def test_new_games_desktop_standard_actions_keep_base_order(
    game_cls, player_count: int, custom_actions: list[str]
) -> None:
    game, player = _new_game_with_players(game_cls, player_count, client_type="python")
    action_set = game.create_standard_action_set(player)
    order = action_set._order
    base_tail = max(order.index("whose_turn"), order.index("whos_at_table"))

    assert all(order.index(action_id) > base_tail for action_id in custom_actions)


def test_humanitycards_vi_judge_list_omits_empty_conjunction() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    judge_user = MockUser("Trung", locale="vi", uuid="hc-judge")
    listener_user = MockUser("Lan", locale="vi", uuid="hc-listener")
    other_user = MockUser("Minh", locale="vi", uuid="hc-other")
    game.add_player("Trung", judge_user)
    listener = game.add_player("Lan", listener_user)
    game.add_player("Minh", other_user)
    game.status = "playing"

    game.judge_indices = [0]
    game._action_whose_judge(listener, "whose_judge")
    assert listener_user.get_last_spoken() == "Trung là trọng tài."
    assert "và là" not in listener_user.get_last_spoken()

    game.judge_indices = [0, 2]
    game._action_whose_judge(listener, "whose_judge")
    assert listener_user.get_last_spoken() == "Trung và Minh là các trọng tài."


def test_humanitycards_waiting_list_uses_locale_conjunction() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    judge_user = MockUser("Trung", locale="vi", uuid="hc-wait-judge")
    listener_user = MockUser("Lan", locale="vi", uuid="hc-wait-listener")
    other_user = MockUser("Minh", locale="vi", uuid="hc-wait-other")
    game.add_player("Trung", judge_user)
    listener = game.add_player("Lan", listener_user)
    game.add_player("Minh", other_user)
    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [0]

    game._action_whose_turn(listener, "whose_turn")
    assert listener_user.get_last_spoken() == "Đang chờ Lan và Minh nộp bài."


def test_backgammon_mobile_gets_info_and_double_buttons() -> None:
    game = BackgammonGame(options=BackgammonOptions(match_length=3))
    game.setup_keybinds()
    user = MockUser("Alice", uuid="backgammon-mobile-1")
    user.client_type = "mobile"
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="backgammon-mobile-2"))
    game.host = "Alice"
    game.on_start()

    game.game_state.turn_phase = "pre_roll"
    game.game_state.current_color = player.color
    game.current_player = player

    visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(player)]
    assert "roll_dice" not in visible_ids
    for action_id in (
        "offer_double",
        "check_status",
        "check_pip",
        "check_scores",
        "check_cube",
        "check_dice",
        "check_legal_moves",
        "whose_turn",
        "whos_at_table",
    ):
        assert action_id in visible_ids


def test_rollingballs_shortcut_utilities_are_touch_only_turn_buttons() -> None:
    game = RollingBallsGame()
    game.setup_keybinds()
    mobile_user = MockUser("Alice", uuid="rolling-mobile-1")
    mobile_user.client_type = "mobile"
    player = game.add_player("Alice", mobile_user)
    game.add_player("Bob", MockUser("Bob", uuid="rolling-mobile-2"))
    game.host = "Alice"
    game.on_start()
    game.current_player = player

    visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(player)]
    assert "view_pipe" in visible_ids
    assert "reshuffle" in visible_ids

    mobile_user.client_type = "python"
    desktop_visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(player)]
    assert "view_pipe" not in desktop_visible_ids
    assert "reshuffle" not in desktop_visible_ids


@pytest.mark.parametrize(
    ("game_cls", "player_count", "roll_action_id"),
    [
        (BunkoGame, 2, "roll"),
        (FarkleGame, 2, "roll"),
        (LeftRightCenterGame, 3, "roll"),
        (LudoGame, 2, "roll_dice"),
        (MidnightGame, 2, "roll"),
        (PigGame, 2, "roll"),
        (SnakesAndLaddersGame, 2, "roll"),
        (ThreesGame, 2, "roll"),
        (TossUpGame, 2, "roll"),
        (YahtzeeGame, 2, "roll"),
    ],
)
def test_roll_actions_remain_visible_for_touch_clients_out_of_turn(
    game_cls, player_count: int, roll_action_id: str
) -> None:
    game = game_cls()
    game.setup_keybinds()
    players = []
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = MockUser(name, uuid=f"roll-anchor-{game.get_type()}-{index + 1}")
        user.client_type = "mobile"
        players.append(game.add_player(name, user))
    game.host = "Player1"
    game.on_start()

    player = next(p for p in players if p != game.current_player)
    visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(player)]

    assert roll_action_id in visible_ids


def test_disabled_turn_menu_action_click_speaks_same_reason_as_keybind() -> None:
    game = PigGame()
    game.setup_keybinds()
    alice = MockUser("Alice", uuid="pig-anchor-1")
    bob = MockUser("Bob", uuid="pig-anchor-2")
    bob.client_type = "mobile"
    game.add_player("Alice", alice)
    bob_player = game.add_player("Bob", bob)
    game.host = "Alice"
    game.on_start()
    assert game.current_player != bob_player

    game.refresh_menus(bob_player)
    game.flush_menus()
    visible_ids = [item.id for item in bob.menus["turn_menu"]["items"] if getattr(item, "id", None)]
    assert "roll" in visible_ids

    bob.clear_messages()
    game.handle_event(bob_player, {"type": "keybind", "key": "r"})
    keybind_message = bob.get_last_spoken()

    bob.clear_messages()
    game.handle_event(
        bob_player,
        {"type": "menu", "menu_id": "turn_menu", "selection_id": "roll"},
    )
    menu_message = bob.get_last_spoken()

    assert menu_message == keybind_message == Localization.get("en", "action-not-your-turn")


@pytest.mark.parametrize(
    ("game_cls", "player_count"),
    [
        (AgeOfHeroesGame, 2),
        (BackgammonGame, 2),
        (HumanityCardsGame, 3),
        (LightTurretGame, 2),
        (MetalPipeGame, 2),
        (NineGame, 3),
        (PusoyDosGame, 3),
        (RollingBallsGame, 2),
        (SenetGame, 2),
        (TwentyOneGame, 2),
        (UnoGame, 2),
    ],
)
def test_recent_games_mobile_turn_menu_has_static_table_controls(
    game_cls, player_count: int
) -> None:
    game, player = _new_game_with_players(game_cls, player_count)
    user = game.get_user(player)
    assert user is not None

    game.on_start()
    game.refresh_menus(player)
    game.flush_menus()

    visible_ids = [
        item.id
        for item in user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "web_actions_menu" in visible_ids
    assert "web_leave_table" in visible_ids


def test_backgammon_mobile_grid_menu_keeps_static_controls_after_grid() -> None:
    game = BackgammonGame()
    game.setup_keybinds()
    user = MockUser("Alice", uuid="backgammon-grid-mobile-1")
    user.client_type = "mobile"
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="backgammon-grid-mobile-2"))
    game.host = "Alice"
    game.on_start()
    game.refresh_menus(player)
    game.flush_menus()

    menu = user.menus["turn_menu"]
    visible_ids = [
        item.id
        for item in menu["items"]
        if getattr(item, "id", None)
    ]
    assert menu["grid_enabled"] is True
    assert menu["grid_width"] == 12
    assert menu["grid_height"] == 2
    assert all(action_id.startswith("point_") for action_id in visible_ids[:24])
    assert visible_ids.index("web_actions_menu") > 23
    assert visible_ids.index("web_leave_table") > visible_ids.index("web_actions_menu")


def test_senet_mobile_grid_menu_keeps_static_controls_after_grid() -> None:
    game = SenetGame()
    game.setup_keybinds()
    user = MockUser("Alice", uuid="senet-grid-mobile-1")
    user.client_type = "mobile"
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="senet-grid-mobile-2"))
    game.host = "Alice"
    game.on_start()
    game.refresh_menus(player)
    game.flush_menus()

    menu = user.menus["turn_menu"]
    visible_ids = [
        item.id
        for item in menu["items"]
        if getattr(item, "id", None)
    ]
    assert menu["grid_enabled"] is True
    assert menu["grid_width"] == 10
    assert menu["grid_height"] == 3
    assert all(action_id.startswith("sq_") for action_id in visible_ids[:30])
    assert visible_ids.index("web_actions_menu") > 29
    assert visible_ids.index("web_leave_table") > visible_ids.index("web_actions_menu")


def test_chess_mobile_standard_actions_are_visible_once() -> None:
    game = ChessGame(options=ChessOptions())
    game.setup_keybinds()
    white = game.add_player("Alice", MockUser("Alice", uuid="p1"))
    game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = "Alice"
    game.on_start()

    user = game.get_user(white)
    user.client_type = "mobile"

    action_set = game.create_standard_action_set(white)
    order = action_set._order
    assert order.index("read_board") < order.index("check_status")
    assert order.index("check_status") < order.index("flip_board")
    assert order.index("flip_board") < order.index("check_clock")
    assert order.index("check_clock") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")

    game.refresh_menus(white)
    game.flush_menus()
    visible_ids = [
        item.id
        for item in user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    for action_id in ("read_board", "check_status", "flip_board", "check_clock"):
        assert action_id in visible_ids
        assert visible_ids.count(action_id) == 1


def test_battleship_toggle_visible_for_mobile() -> None:
    game = BattleshipGame(options=BattleshipOptions(placement_mode="auto"))
    game.setup_keybinds()
    alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
    game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = "Alice"
    game.on_start()

    user = game.get_user(alice)
    user.client_type = "mobile"

    assert game._is_toggle_view_hidden(alice) == Visibility.VISIBLE
