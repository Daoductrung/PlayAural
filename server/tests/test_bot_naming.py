"""Tests for lobby bot naming behavior."""

from ..game_utils.bot_names import (
    DEFAULT_BOT_NAME_POOL,
    generate_unique_bot_name,
    get_valid_bot_name_pool,
    normalize_pool_bot_name,
    PLAYPALACE_BOT_NAMES,
    validate_custom_bot_name,
)
from ..game_utils import bot_names as bot_names_module
from ..games.pig.game import PigGame
from ..messages.localization import Localization
from ..users.preferences import UserPreferences
from ..users.test_user import MockUser


def make_game():
    """Create a waiting lobby with one human host."""
    game = PigGame()
    game.setup_keybinds()
    user = MockUser("Host", uuid="host")
    host = game.add_player("Host", user)
    game.host = "Host"
    game.rebuild_all_menus()
    return game, host, user


def get_bot_names(game: PigGame) -> list[str]:
    return [player.name for player in game.players if player.is_bot]


def speak_messages(user: MockUser) -> list[dict]:
    return [message.data for message in user.messages if message.type == "speak"]


def test_allow_custom_bot_names_preference_defaults_and_round_trips() -> None:
    prefs = UserPreferences()
    data = prefs.to_dict()

    assert prefs.allow_custom_bot_names is False
    assert data["allow_custom_bot_names"] is False
    assert UserPreferences.from_dict({}).allow_custom_bot_names is False
    assert (
        UserPreferences.from_dict({"allow_custom_bot_names": True}).allow_custom_bot_names
        is True
    )


def test_default_add_bot_generates_random_name_without_prompt(monkeypatch) -> None:
    game, host, user = make_game()
    choices = []

    def choose_last(options):
        choices.append(tuple(options))
        return options[-1]

    monkeypatch.setattr(bot_names_module.random, "choice", choose_last)

    game.execute_action(host, "add_bot")

    pool = get_valid_bot_name_pool()
    assert "action_input_editbox" not in user.editboxes
    assert choices == [pool]
    assert get_bot_names(game) == [pool[-1]]
    assert host.id not in game._pending_actions


def test_custom_name_preference_opens_existing_prompt() -> None:
    game, host, user = make_game()
    user.preferences.allow_custom_bot_names = True

    game.execute_action(host, "add_bot")

    assert get_bot_names(game) == []
    assert "action_input_editbox" in user.editboxes
    assert host.id in game._pending_actions


def test_custom_name_submission_adds_normalized_bot() -> None:
    game, host, user = make_game()
    user.preferences.allow_custom_bot_names = True
    game.execute_action(host, "add_bot")

    game.handle_event(
        host,
        {
            "type": "editbox",
            "input_id": "action_input_editbox",
            "text": "  Custom   Bot  ",
        },
    )

    assert get_bot_names(game) == ["Custom Bot"]


def test_duplicate_custom_name_is_rejected_with_game_buffer() -> None:
    game, host, user = make_game()
    user.preferences.allow_custom_bot_names = True
    game.execute_action(host, "add_bot")

    game.handle_event(
        host,
        {
            "type": "editbox",
            "input_id": "action_input_editbox",
            "text": "host",
        },
    )

    assert get_bot_names(game) == []
    assert speak_messages(user)[-1] == {
        "text": Localization.get("en", "bot-name-already-used"),
        "buffer": "game",
    }


def test_invalid_custom_name_is_rejected_with_game_buffer() -> None:
    game, host, user = make_game()
    user.preferences.allow_custom_bot_names = True
    game.execute_action(host, "add_bot")

    game.handle_event(
        host,
        {
            "type": "editbox",
            "input_id": "action_input_editbox",
            "text": "Bad_bot!",
        },
    )

    assert get_bot_names(game) == []
    assert speak_messages(user)[-1] == {
        "text": Localization.get("en", "bot-name-invalid-characters"),
        "buffer": "game",
    }


def test_generated_names_skip_existing_human_and_bot_names(monkeypatch) -> None:
    game, host, user = make_game()
    pool = get_valid_bot_name_pool()
    game.add_player(pool[0], MockUser("Existing", uuid="existing"))
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])

    game.execute_action(host, "add_bot")

    assert get_bot_names(game) == [pool[1]]
    assert "action_input_editbox" not in user.editboxes


def test_generated_names_skip_case_insensitive_existing_names(monkeypatch) -> None:
    pool = get_valid_bot_name_pool()
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])
    name = generate_unique_bot_name([pool[0].lower()])

    assert name == pool[1]


def test_name_pool_exhaustion_uses_unique_numeric_suffix(monkeypatch) -> None:
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])
    name = generate_unique_bot_name(DEFAULT_BOT_NAME_POOL)

    assert name == f"{get_valid_bot_name_pool()[0]} 2"


def test_playpalace_names_are_extracted_and_sanitized_for_generated_pool() -> None:
    pool = get_valid_bot_name_pool()

    assert len(PLAYPALACE_BOT_NAMES) == 88
    assert "Assembly_programmer" in PLAYPALACE_BOT_NAMES
    assert "Assembly Programmer" in pool
    assert "Omega Alpha" in pool
    assert "Amazing" in pool
    assert "Still Thinking" in pool
    assert "Sa" not in pool
    assert normalize_pool_bot_name("Music_and_lasers") == "Music And Lasers"


def test_custom_bot_name_validation_matches_expected_shape() -> None:
    assert validate_custom_bot_name(" Abc  123 ") is None
    assert validate_custom_bot_name("ab") == "bot-name-invalid-length"
    assert validate_custom_bot_name("Bad_bot!") == "bot-name-invalid-characters"
    assert validate_custom_bot_name("Host", ["host"]) == "bot-name-already-used"


def test_new_bot_name_localization_keys_have_en_vi_parity() -> None:
    keys = [
        "custom-bot-names-option",
        "bot-name-invalid-length",
        "bot-name-invalid-characters",
        "bot-name-already-used",
    ]

    for key in keys:
        assert Localization.get("en", key, status="On") != key
        assert Localization.get("vi", key, status="On") != key
