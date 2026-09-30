"""Tests for locale-owned, identity-safe lobby bot naming."""

import json

import pytest

from ..game_utils import bot_names as bot_names_module
from ..game_utils.bot_names import (
    allocate_bot_display_name,
    bot_name_key,
    format_bot_display_name,
    generate_bot_base_name,
    get_localized_bot_name_pool,
    get_native_bot_name_pool,
    normalize_bot_name,
    validate_custom_bot_name,
)
from ..games.pig.game import PigGame
from ..messages.localization import Localization
from ..users.preferences import UserPreferences
from ..users.test_user import MockUser


def make_game(*, locale: str = "en"):
    """Create a waiting lobby with one human host."""
    game = PigGame()
    game.setup_keybinds()
    user = MockUser("Host", locale=locale, uuid="host")
    host = game.add_player("Host", user)
    game.host = "Host"
    game.refresh_menus()
    game.flush_menus()
    return game, host, user


def get_bots(game: PigGame):
    return [player for player in game.players if player.is_bot]


def speak_messages(user: MockUser) -> list[dict]:
    return [message.data for message in user.messages if message.type == "speak"]


def submit_custom_bot_name(
    game: PigGame,
    host,
    user: MockUser,
    name: str,
) -> None:
    user.preferences.allow_custom_bot_names = True
    game.execute_action(host, "add_bot")
    game.handle_event(
        host,
        {
            "type": "editbox",
            "input_id": "action_input_editbox",
            "text": name,
        },
    )


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


def test_default_add_bot_uses_localized_pool_and_bare_unique_label(monkeypatch) -> None:
    game, host, user = make_game()
    choices = []

    def choose_last(options):
        choices.append(tuple(options))
        return options[-1]

    monkeypatch.setattr(bot_names_module.random, "choice", choose_last)

    game.execute_action(host, "add_bot")

    pool = get_localized_bot_name_pool("en")
    bot = get_bots(game)[0]
    assert "action_input_editbox" not in user.editboxes
    assert choices == [pool]
    assert bot.bot_name_base == pool[-1]
    assert bot.name == pool[-1]
    assert host.id not in game._pending_actions


def test_vietnamese_host_draws_from_vietnamese_pool(monkeypatch) -> None:
    game, host, _user = make_game(locale="vi")
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])
    vietnamese_native = get_native_bot_name_pool("vi")

    game.execute_action(host, "add_bot")

    bot = get_bots(game)[0]
    assert vietnamese_native
    assert bot.bot_name_base == vietnamese_native[0]
    assert bot.name == vietnamese_native[0]


def test_vietnamese_pool_falls_back_to_english_only_after_exhaustion(
    monkeypatch,
) -> None:
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])
    vietnamese_native = get_native_bot_name_pool("vi")
    english = get_native_bot_name_pool("en")
    native_keys = {bot_name_key(name) for name in vietnamese_native}
    first_fallback = next(
        name for name in english if bot_name_key(name) not in native_keys
    )

    assert vietnamese_native
    assert generate_bot_base_name(vietnamese_native[:-1], "vi") == vietnamese_native[-1]
    assert generate_bot_base_name(vietnamese_native, "vi") == first_fallback


def test_untranslated_locale_falls_back_to_complete_english_pool() -> None:
    assert get_localized_bot_name_pool("es") == get_localized_bot_name_pool("en")


@pytest.mark.parametrize(
    "configured_value",
    (
        "Valid Name | Bad_name",
        "Valid Name | valid name",
        "Valid Name | ",
    ),
)
def test_malformed_locale_pool_fails_instead_of_silently_dropping_names(
    monkeypatch,
    configured_value: str,
) -> None:
    monkeypatch.setattr(
        Localization,
        "get_message_attribute_values",
        lambda *_args, **_kwargs: (configured_value,),
    )

    with pytest.raises(RuntimeError, match="invalid or duplicate"):
        get_native_bot_name_pool("en")


def test_custom_name_preference_opens_existing_prompt() -> None:
    game, host, user = make_game()
    user.preferences.allow_custom_bot_names = True

    game.execute_action(host, "add_bot")

    assert get_bots(game) == []
    assert "action_input_editbox" in user.editboxes
    assert host.id in game._pending_actions


def test_custom_name_can_match_human_and_is_normalized_and_marked() -> None:
    game, host, user = make_game()

    submit_custom_bot_name(game, host, user, "  Host  ")

    bot = get_bots(game)[0]
    assert bot.bot_name_base == "Host"
    assert bot.name == "Host (Bot)"
    assert game.get_player_by_id(host.id).name == "Host"


def test_duplicate_bot_bases_receive_stable_ordinals() -> None:
    game, host, user = make_game()

    submit_custom_bot_name(game, host, user, "Trung")
    submit_custom_bot_name(game, host, user, "trung")
    submit_custom_bot_name(game, host, user, "Trung")

    bots = get_bots(game)
    assert [bot.bot_name_base for bot in bots] == ["Trung", "trung", "Trung"]
    assert [bot.name for bot in bots] == [
        "Trung (Bot)",
        "trung 2 (Bot)",
        "Trung 3 (Bot)",
    ]
    assert len({bot_name_key(bot.name) for bot in bots}) == 3


def test_cli_capture_keeps_duplicate_bot_bases_distinct() -> None:
    from ..cli import GameSimulator

    simulator = GameSimulator(
        "pig",
        ["Trung", "Trung"],
        {},
        quiet=True,
    )

    assert simulator.setup()
    assert len(simulator.capturing_bots) == 2
    assert [
        player.name for player in simulator.game.players if player.is_bot
    ] == ["Trung (Bot)", "Trung 2 (Bot)"]
    assert [
        bot.username for bot in simulator.capturing_bots.values()
    ] == ["Trung (Bot)", "Trung 2 (Bot)"]


def test_bot_marker_appears_and_disappears_with_matching_human() -> None:
    game, host, user = make_game()
    submit_custom_bot_name(game, host, user, "Trung")
    bot = get_bots(game)[0]
    assert bot.name == "Trung"
    game.team_manager.setup_teams([bot.name])

    spectator_user = MockUser("trung", uuid="spectator")
    spectator = game.add_spectator("trung", spectator_user)

    assert bot.name == "Trung (Bot)"
    assert game.get_user(bot).username == "Trung (Bot)"
    assert game.team_manager.get_team("Trung (Bot)") is not None
    assert game.team_manager.get_team("Trung") is None
    assert spectator.name == "trung"

    game.remove_spectator(spectator.id)

    assert bot.name == "Trung"
    assert game.get_user(bot).username == "Trung"
    assert game.team_manager.get_team("Trung") is not None


def test_replaced_human_identity_disambiguates_matching_dedicated_bot() -> None:
    game = PigGame()
    dedicated = game.create_player("dedicated", "Guest", is_bot=True)
    dedicated.bot_name_base = "Guest"
    replacement = game.create_player("guest-id", "Alice", is_bot=True)
    replacement.bot_name_base = "Alice"
    replacement.replaced_human = True
    replacement.replaced_human_name = "Guest"
    replacement.replacement_bot_name = "Alice"
    game.players.extend((dedicated, replacement))

    game.ensure_bot_display_names("en")

    assert dedicated.name == "Guest (Bot)"
    assert replacement.name == "Alice"


def test_invalid_custom_name_is_rejected_with_game_buffer() -> None:
    game, host, user = make_game()

    submit_custom_bot_name(game, host, user, "Bad_bot!")

    assert get_bots(game) == []
    assert speak_messages(user)[-1] == {
        "text": Localization.get("en", "bot-name-invalid-characters"),
        "buffer": "game",
    }


def test_generated_names_prefer_unused_bot_bases_not_human_names(monkeypatch) -> None:
    game, host, _user = make_game()
    pool = get_localized_bot_name_pool("en")
    game.add_player(pool[0], MockUser(pool[0], uuid="existing"))
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])

    game.execute_action(host, "add_bot")
    game.execute_action(host, "add_bot")

    bots = get_bots(game)
    assert [bot.bot_name_base for bot in bots] == [pool[0], pool[1]]
    assert bots[0].name == f"{pool[0]} (Bot)"


def test_exhausted_pool_reuses_base_and_allocator_indexes_label(monkeypatch) -> None:
    monkeypatch.setattr(bot_names_module.random, "choice", lambda options: options[0])
    base = generate_bot_base_name(["Only Name"], "en", name_pool=["Only Name"])

    assert base == "Only Name"
    assert allocate_bot_display_name(
        base,
        ["Only Name", "Only Name (Bot)", "only name 2 (bot)"],
        "en",
    ) == "Only Name 3 (Bot)"

    with pytest.raises(ValueError):
        generate_bot_base_name([], "en", name_pool=[])


def test_curated_pools_are_valid_distinct_and_personality_rich() -> None:
    english = get_localized_bot_name_pool("en")
    vietnamese = get_localized_bot_name_pool("vi")
    vietnamese_native = get_native_bot_name_pool("vi")

    assert english[:26] == (
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace",
        "Henry", "Ivy", "Jack", "Kate", "Leo", "Mia", "Noah", "Olivia",
        "Pete", "Quinn", "Rose", "Sam", "Tina", "Uma", "Vic", "Wendy",
        "Xander", "Yara", "Zack",
    )
    assert "Stupid bot" in english
    assert "Oops" in english
    assert vietnamese_native
    native_keys = {bot_name_key(name) for name in vietnamese_native}
    english_fallback = tuple(
        name for name in english if bot_name_key(name) not in native_keys
    )
    assert vietnamese == (*vietnamese_native, *english_fallback)
    assert any(name not in english for name in vietnamese_native)
    for pool in (english, vietnamese):
        assert len({bot_name_key(name) for name in pool}) == len(pool)
        assert all(validate_custom_bot_name(name) is None for name in pool)


def test_custom_bot_name_validation_and_unicode_normalization() -> None:
    assert validate_custom_bot_name(" Abc  123 ") is None
    assert validate_custom_bot_name("ab") == "bot-name-invalid-length"
    assert validate_custom_bot_name("Bad_bot!") == "bot-name-invalid-characters"
    assert normalize_bot_name("  Đa\u0300o   Đức  ") == "Đào Đức"


def test_bot_state_round_trip_preserves_bare_base_and_display_label() -> None:
    game, host, user = make_game()
    submit_custom_bot_name(game, host, user, "Trung")

    restored = PigGame.from_json(game.to_json())
    bot = next(player for player in restored.players if player.is_bot)

    assert bot.bot_name_base == "Trung"
    assert bot.name == "Trung"


def test_legacy_unique_bot_migration_keeps_bare_label_and_name_state() -> None:
    game = PigGame()
    legacy_bot = game.create_player("bot-id", "Trung", is_bot=True)
    legacy_bot.round_score = 7
    game.players.append(legacy_bot)
    game.set_turn_players([legacy_bot])
    game.host = "Trung"

    game.ensure_bot_display_names("en")

    assert legacy_bot.bot_name_base == "Trung"
    assert legacy_bot.name == "Trung"
    assert game.turn_players[0].name == "Trung"
    assert game.host == "Trung"


def test_pre_feature_json_without_bot_base_deserializes_and_migrates() -> None:
    game = PigGame()
    bot = game.create_player("bot-id", "Legacy Friend", is_bot=True)
    game.players.append(bot)
    payload = json.loads(game.to_json())
    payload["players"][0].pop("bot_name_base")

    restored = PigGame.from_json(json.dumps(payload))
    restored.ensure_bot_display_names("en")
    migrated = restored.players[0]

    assert migrated.bot_name_base == "Legacy Friend"
    assert migrated.name == "Legacy Friend"


def test_bot_name_format_rejects_invalid_inputs(monkeypatch) -> None:
    with pytest.raises(ValueError):
        format_bot_display_name("Bad_bot!", "en")
    with pytest.raises(ValueError):
        format_bot_display_name("Valid Name", "en", ordinal=0)

    monkeypatch.setattr(
        Localization,
        "get",
        lambda *_args, **kwargs: kwargs["name"],
    )
    with pytest.raises(RuntimeError):
        format_bot_display_name("Valid Name", "en")
    with pytest.raises(RuntimeError):
        format_bot_display_name("Valid Name", "en", ordinal=2)


def test_invalid_community_bot_label_falls_back_to_english(monkeypatch) -> None:
    def render(locale, _message_id, **kwargs):
        if locale == "vi":
            return kwargs["name"]
        return f'{kwargs["name"]} ({kwargs["number"]} Bot)'

    monkeypatch.setattr(Localization, "get", render)

    assert format_bot_display_name("Tên Vui", "vi") == "Tên Vui (1 Bot)"


def test_new_bot_localization_keys_have_en_vi_parity() -> None:
    keys = [
        "custom-bot-names-option",
        "bot-name-invalid-length",
        "bot-name-invalid-characters",
        "bot-display-name",
        "bot-display-name-numbered",
        "table-name-already-used",
    ]

    for key in keys:
        kwargs = {"status": "On", "name": "Test", "number": 2}
        assert Localization.get("en", key, **kwargs) != key
        assert Localization.get("vi", key, **kwargs) != key
