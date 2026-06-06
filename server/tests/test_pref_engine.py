"""Tests for the declarative preference engine and client-compat invariants."""

from ..users.preferences import UserPreferences, DiceKeepingStyle, PREF_CATEGORIES


# The exact key set web/mobile clients read from preferences.to_dict(). Migrating
# game prefs to the declarative engine must NOT change this set.
EXPECTED_TO_DICT_KEYS = {
    "brief_announcements",
    "play_turn_sound", "music_volume", "ambience_volume", "voice_volume",
    "desktop_audio_input_device_id", "desktop_audio_input_device_name",
    "speech_mode", "speech_rate", "speech_voice",
    "mobile_tts_engine", "mobile_tts_rate", "mobile_tts_voice",
    "mute_global_chat", "mute_table_chat", "notify_table_created",
    "notify_user_presence", "notify_friend_presence",
    "invert_multiline_enter_behavior", "play_typing_sounds",
    "active_tables_filter", "game_category_filter",
    "allow_custom_bot_names", "confirm_destructive_actions",
    "clear_kept_on_roll", "dice_keeping_style", "game_overrides",
}


def test_to_dict_key_set_is_stable() -> None:
    assert set(UserPreferences().to_dict().keys()) == EXPECTED_TO_DICT_KEYS


def test_declarative_categories_and_fields() -> None:
    cats = {c for c, _ in PREF_CATEGORIES}
    assert cats == {"display", "sounds", "gameplay", "dice"}
    assert [n for n, _ in UserPreferences.get_fields_for_category("dice")] == [
        "clear_kept_on_roll",
        "dice_keeping_style",
    ]
    # Non-declarative prefs have no PrefMeta.
    assert UserPreferences.get_pref_meta("music_volume") is None
    assert UserPreferences.get_pref_meta("dice_keeping_style").kind == "menu"


def test_get_effective_bool_and_enum_overrides() -> None:
    p = UserPreferences()
    assert p.get_effective("confirm_destructive_actions", "pusoydos") is True
    p.set_game_override("confirm_destructive_actions", "pusoydos", False)
    assert p.get_effective("confirm_destructive_actions", "pusoydos") is False
    assert p.get_effective("confirm_destructive_actions", "yahtzee") is True  # unaffected

    p.set_game_override("dice_keeping_style", "yahtzee", DiceKeepingStyle.VALUE_BASED)
    assert p.get_effective("dice_keeping_style", "yahtzee") is DiceKeepingStyle.VALUE_BASED
    assert p.get_effective("dice_keeping_style", "midnight") is DiceKeepingStyle.INDEX_BASED


def test_overrides_round_trip_through_to_from_dict() -> None:
    p = UserPreferences()
    p.set_game_override("dice_keeping_style", "yahtzee", DiceKeepingStyle.VALUE_BASED)
    p.set_game_override("confirm_destructive_actions", "pusoydos", False)
    p2 = UserPreferences.from_dict(p.to_dict())
    assert p2.get_effective("dice_keeping_style", "yahtzee") is DiceKeepingStyle.VALUE_BASED
    assert p2.get_effective("confirm_destructive_actions", "pusoydos") is False


def test_reset_category_and_all_clear_overrides() -> None:
    p = UserPreferences()
    p.allow_custom_bot_names = True
    p.set_game_override("dice_keeping_style", "yahtzee", DiceKeepingStyle.VALUE_BASED)

    p.reset_category("dice")
    assert p.get_game_override("dice_keeping_style", "yahtzee") is None
    assert p.dice_keeping_style is DiceKeepingStyle.INDEX_BASED
    assert p.allow_custom_bot_names is True  # other category untouched

    p.reset_all_game_prefs()
    assert p.allow_custom_bot_names is False
