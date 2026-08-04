"""Tests for automatic and on-demand game-option descriptions.

Menu hints include custom or generated help in lobby rows by default. Turning
them off keeps Space-to-describe support while preserving active-game keybinds.
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


def _space(game, player, menu_item_id) -> None:
    game.handle_event(
        player, {"type": "keybind", "key": "space", "menu_item_id": menu_item_id}
    )


def test_space_speaks_option_description_en() -> None:
    game, user, player = _make_game("en")
    _space(game, player, "set_game_mode")
    spoken = user.get_spoken_messages()
    assert spoken, "expected a description to be spoken"
    assert "Elimination" in spoken[-1]


def test_space_speaks_option_description_vi() -> None:
    game, user, player = _make_game("vi")
    _space(game, player, "toggle_instant_wins")
    spoken = user.get_spoken_messages()
    assert spoken, "expected a Vietnamese description to be spoken"
    # The Vietnamese description contains non-ASCII characters.
    assert any(ord(ch) > 127 for ch in spoken[-1])


def test_space_on_non_option_says_nothing() -> None:
    game, user, player = _make_game("en")
    _space(game, player, "some_unrelated_button")
    assert user.get_spoken_messages() == []


def test_space_during_play_is_not_hijacked_for_descriptions() -> None:
    game, user, player = _make_game("en")
    game.status = "playing"
    _space(game, player, "set_game_mode")
    # No description spoken; space is reserved for game keybinds during play.
    assert user.get_spoken_messages() == []


def test_space_speaks_generated_description_for_option_without_custom_text() -> None:
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

    _space(game, player, "set_starting_tokens")

    spoken = user.get_spoken_messages()
    assert spoken, "expected custom option help to be spoken"
    assert "How many survival tokens each Ninety Nine player begins with" in spoken[-1]
    assert "Enter a whole number" not in spoken[-1]


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


def test_menu_hints_control_inline_option_help_without_removing_space_help() -> None:
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

    user.clear_messages()
    _space(game, player, "set_game_mode")
    assert "win rounds to go out" in user.get_spoken_messages()[-1]


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
