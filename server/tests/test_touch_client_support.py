"""Regression tests for touch-client support across server and games."""

from pathlib import Path

from ..game_utils.actions import Visibility
from ..game_utils.client_types import (
    is_touch_client_type,
    uses_self_voicing_settings_type,
)
from ..games.battleship.game import BattleshipGame, BattleshipOptions
from ..games.chess.game import ChessGame, ChessOptions
from ..games.ludo.game import LudoGame
from ..games.milebymile.game import MileByMileGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


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

    game.rebuild_player_menu(p1)
    visible_ids = [
        item.id
        for item in u1.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "web_actions_menu" in visible_ids
    assert "web_leave_table" in visible_ids


def test_milebymile_touch_info_stays_above_bottom_status_actions() -> None:
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

    assert order.index("check_status") < order.index("info")
    assert order.index("info") < order.index("whose_turn")
    assert order[-2:] == ["whose_turn", "whos_at_table"]

    game.rebuild_player_menu(p1)
    visible_ids = [
        item.id
        for item in u1.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert visible_ids.index("check_status") < visible_ids.index("info")
    assert visible_ids.index("info") < visible_ids.index("whose_turn")
    assert visible_ids.index("whose_turn") < visible_ids.index("whos_at_table")


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

    game.rebuild_player_menu(white)
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
