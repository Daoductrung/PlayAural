"""Regression tests for documented grid-game keyboard shortcuts."""

from pathlib import Path

from ..games.backgammon.game import BackgammonGame, BackgammonOptions
from ..games.senet.game import SenetGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def _message_types(user: MockUser) -> list[str]:
    return [message.type for message in user.messages]


def _turn_menu_paints(user: MockUser) -> list:
    return [
        message
        for message in user.messages
        if message.type == "show_menu" and message.data.get("menu_id") == "turn_menu"
    ]


def test_backgammon_ctrl_navigation_moves_focus_with_a_single_paint() -> None:
    game = BackgammonGame(options=BackgammonOptions())
    game.setup_keybinds()
    user = MockUser("Alice", uuid="backgammon-shortcut-1")
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="backgammon-shortcut-2"))
    game.host = "Alice"
    game.on_start()
    game.flush_menus()

    game.game_state.turn_phase = "moving"
    game.game_state.current_color = player.color
    game.game_state.dice = [3, 1]
    game.game_state.dice_used = [False, False]
    game.refresh_menus(player)
    game.flush_menus()
    user.clear_messages()

    game.handle_event(player, {"type": "keybind", "key": "down", "control": True})

    # One paint, carrying the focus intent: a navigation keybind must move
    # the cursor without double-painting (the focus slot is consumed by the
    # same flush that repaints).
    paints = _turn_menu_paints(user)
    assert len(paints) == 1
    assert paints[0].data["selection_id"] is not None
    assert paints[0].data["selection_id"].startswith("point_")


def test_backgammon_ctrl_backspace_deselects_selected_checker() -> None:
    game = BackgammonGame(options=BackgammonOptions())
    game.setup_keybinds()
    user = MockUser("Alice", uuid="backgammon-deselect-1")
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="backgammon-deselect-2"))
    game.host = "Alice"
    game.on_start()
    game.flush_menus()

    game.game_state.turn_phase = "moving"
    game.game_state.current_color = player.color
    game._selected_source = 23
    user.clear_messages()

    game.handle_event(player, {"type": "keybind", "key": "backspace", "control": True})

    assert game._selected_source is None
    assert "show_menu" in _message_types(user)


def test_senet_ctrl_navigation_moves_focus_with_a_single_paint() -> None:
    game = SenetGame()
    game.setup_keybinds()
    user = MockUser("Alice", uuid="senet-shortcut-1")
    player = game.add_player("Alice", user)
    game.add_player("Bob", MockUser("Bob", uuid="senet-shortcut-2"))
    game.host = "Alice"
    game.on_start()
    game.flush_menus()

    game.game_state.turn_phase = "moving"
    game.game_state.current_player_num = player.player_num
    game.game_state.current_roll = 1
    game.refresh_menus(player)
    game.flush_menus()
    user.clear_messages()

    game.handle_event(player, {"type": "keybind", "key": "right", "control": True})

    paints = _turn_menu_paints(user)
    assert len(paints) == 1
    assert paints[0].data["selection_id"] is not None
    assert paints[0].data["selection_id"].startswith("sq_")
