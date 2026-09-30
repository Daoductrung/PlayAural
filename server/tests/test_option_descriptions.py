"""Tests for automatic and on-demand game-option descriptions.

Menu hints include custom or generated help in lobby rows by default. Turning
them off keeps the description metadata that clients request semantically.
"""

from pathlib import Path

from ..game_utils.options import BoolOption, MultiSelectOption
from ..games import GameRegistry
from ..games.ninetynine.game import NinetyNineGame
from ..games.pusoydos.game import PusoyDosGame
from ..games.snakesandladders.game import SnakesAndLaddersGame
from ..games.yahtzee.game import YahtzeeGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def _make_game(locale: str = "en") -> tuple[PusoyDosGame, MockUser, object]:
    game = PusoyDosGame()
    user = MockUser("Alice")
    user._locale = locale
    player = game.add_player("Alice", user)
    game.status = "waiting"
    game.setup_player_actions(player)
    return game, user, player


def _menu_item(game, user, player, menu_item_id):
    game.refresh_menus(player)
    game.flush_menus()
    return next(
        item
        for item in user.get_current_menu_items("turn_menu")
        if item.id == menu_item_id
    )


def test_option_menu_item_retains_description_en() -> None:
    game, user, player = _make_game("en")
    item = _menu_item(game, user, player, "set_game_mode")
    assert "Elimination" in item.description


def test_option_menu_item_retains_description_vi() -> None:
    game, user, player = _make_game("vi")
    item = _menu_item(game, user, player, "toggle_instant_wins")
    assert item.description
    # The Vietnamese description contains non-ASCII characters.
    assert any(ord(ch) > 127 for ch in item.description)


def test_non_option_id_has_no_generated_description() -> None:
    game, _user, player = _make_game("en")
    assert game._option_description_text(player, "some_unrelated_button") is None


def test_space_keybind_is_not_repurposed_for_descriptions() -> None:
    game, user, player = _make_game("en")
    game.status = "playing"
    game.handle_event(
        player,
        {"type": "keybind", "key": "space", "menu_item_id": "set_game_mode"},
    )
    assert user.get_spoken_messages() == []


def test_generated_description_exists_for_option_without_custom_text() -> None:
    game = YahtzeeGame()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    meta = game.options.get_option_metas()["num_games"]

    description = meta.get_description(user.locale, 1, game=game, player=player)

    assert "Enter a whole number from 1 to 10" in description
    assert "Default: 1" in description


def test_generated_option_description_is_localized() -> None:
    game = YahtzeeGame()
    user = MockUser("Alice")
    user._locale = "vi"
    player = game.add_player("Alice", user)
    meta = game.options.get_option_metas()["num_games"]

    description = meta.get_description(user.locale, 1, game=game, player=player)

    assert "số nguyên" in description.lower()
    assert any(ord(ch) > 127 for ch in description)


def test_generated_bool_description_is_platform_neutral() -> None:
    game = SnakesAndLaddersGame()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    meta = game.options.get_option_metas()["extra_turn_on_six"]

    description = meta.get_description(user.locale, True, game=game, player=player)

    assert "Activate this item" in description
    assert "Enter" not in description


def test_conventional_custom_description_is_used_before_generated_fallback() -> None:
    game = NinetyNineGame()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    game.status = "waiting"
    game.setup_player_actions(player)

    item = _menu_item(game, user, player, "set_starting_tokens")
    assert "How many survival tokens each Ninety Nine player begins with" in item.description
    assert "Enter a whole number" not in item.description


def _option_action_id(option_name: str, meta) -> str:
    if isinstance(meta, BoolOption):
        return f"toggle_{option_name}"
    if isinstance(meta, MultiSelectOption):
        return f"multiselect_{option_name}"
    return f"set_{option_name}"


def test_every_declarative_game_option_produces_localized_help() -> None:
    missing: list[str] = []
    for locale in ("en", "vi"):
        for game_type in sorted(GameRegistry._games):
            game_cls = GameRegistry.get(game_type)
            game = game_cls()
            options = getattr(game, "options", None)
            if not options or not hasattr(options, "get_option_metas"):
                continue

            user = MockUser("Alice")
            user._locale = locale
            player = game.add_player("Alice", user)
            for option_name, meta in options.get_option_metas().items():
                action_id = _option_action_id(option_name, meta)
                description = game._option_description_text(player, action_id)
                if not description or description == meta.description:
                    missing.append(f"{locale}:{game_type}.{option_name}")

    assert not missing


def test_menu_hints_control_inline_help_without_removing_description_metadata() -> None:
    game, user, player = _make_game("en")
    game.refresh_menus(player)
    game.flush_menus()

    item = next(
        item
        for item in user.get_current_menu_items("turn_menu")
        if item.id == "set_game_mode"
    )
    assert "win rounds to go out" in item.text

    user.preferences.show_menu_hints = False
    game.refresh_menus(player)
    game.flush_menus()
    item = next(
        item
        for item in user.get_current_menu_items("turn_menu")
        if item.id == "set_game_mode"
    )
    assert "win rounds to go out" not in item.text
    assert "win rounds to go out" in item.description


def test_every_declarative_game_option_has_custom_description_key() -> None:
    missing: list[str] = []
    for locale in ("en", "vi"):
        for game_type in sorted(GameRegistry._games):
            game_cls = GameRegistry.get(game_type)
            game = game_cls()
            options = getattr(game, "options", None)
            if not options or not hasattr(options, "get_option_metas"):
                continue

            for option_name in options.get_option_metas():
                key = game._option_description_key(option_name)
                if not key or not Localization.has_message(locale, key):
                    missing.append(f"{locale}:{game_type}.{option_name}")

    assert not missing
