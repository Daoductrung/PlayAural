"""Tests for the space-to-describe option feature.

Pressing space while an option is focused in the lobby/options menu speaks
custom or generated option help; during play, space remains a game keybind.
"""

from pathlib import Path

from ..game_utils.options import BoolOption, MultiSelectOption
from ..games import GameRegistry
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
    game.status = "waiting"
    game.setup_player_actions(player)

    _space(game, player, "set_num_games")

    spoken = user.get_spoken_messages()
    assert spoken, "expected generated option help to be spoken"
    assert "Enter a whole number from 1 to 10" in spoken[-1]
    assert "Default: 1" in spoken[-1]


def test_generated_option_description_is_localized() -> None:
    game = YahtzeeGame()
    user = MockUser("Alice")
    user._locale = "vi"
    player = game.add_player("Alice", user)
    game.status = "waiting"
    game.setup_player_actions(player)

    _space(game, player, "set_num_games")

    spoken = user.get_spoken_messages()
    assert spoken, "expected generated Vietnamese option help to be spoken"
    assert "số nguyên" in spoken[-1].lower()
    assert any(ord(ch) > 127 for ch in spoken[-1])


def test_generated_bool_description_is_platform_neutral() -> None:
    game = SnakesAndLaddersGame()
    user = MockUser("Alice")
    player = game.add_player("Alice", user)
    game.status = "waiting"
    game.setup_player_actions(player)

    _space(game, player, "toggle_extra_turn_on_six")

    spoken = user.get_spoken_messages()
    assert spoken, "expected generated bool option help to be spoken"
    assert "Activate this item" in spoken[-1]
    assert "Enter" not in spoken[-1]


def _option_action_id(option_name: str, meta) -> str:
    if isinstance(meta, BoolOption):
        return f"toggle_{option_name}"
    if isinstance(meta, MultiSelectOption):
        return f"multiselect_{option_name}"
    return f"set_{option_name}"


def test_every_declarative_game_option_produces_spoken_help() -> None:
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
                before = len(user.get_spoken_messages())
                action_id = _option_action_id(option_name, meta)
                if not game._speak_option_description(player, action_id):
                    missing.append(f"{locale}:{game_type}.{option_name}")
                    continue
                spoken = user.get_spoken_messages()
                if len(spoken) <= before or spoken[-1] == meta.description:
                    missing.append(f"{locale}:{game_type}.{option_name}")

    assert not missing
