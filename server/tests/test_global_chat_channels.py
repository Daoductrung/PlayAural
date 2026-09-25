from ..chat_channels import (
    GLOBAL_CHAT_CHANNEL_CODES,
    normalize_global_chat_channel,
    ordered_global_chat_channels,
    recommended_global_chat_channel,
)
from ..users.preferences import UserPreferences


def test_channel_registry_normalizes_supported_regional_codes() -> None:
    assert normalize_global_chat_channel(" PT_br ") == "pt"
    assert normalize_global_chat_channel("zh-Hant") == "zh"
    assert normalize_global_chat_channel("unknown") is None
    assert normalize_global_chat_channel(123) is None


def test_current_ui_language_is_recommended_without_changing_registry() -> None:
    ordered = ordered_global_chat_channels("vi-VN")

    assert recommended_global_chat_channel("vi-VN") == "vi"
    assert ordered[0].code == "vi"
    assert {channel.code for channel in ordered} == GLOBAL_CHAT_CHANNEL_CODES
    assert len(ordered) == len(GLOBAL_CHAT_CHANNEL_CODES)


def test_preferences_default_to_no_channel_and_reject_stale_values() -> None:
    assert UserPreferences().global_chat_channel is None
    assert UserPreferences.from_dict({}).global_chat_channel is None
    assert UserPreferences.from_dict(
        {"global_chat_channel": "es-MX"}
    ).global_chat_channel == "es"
    assert UserPreferences.from_dict(
        {"global_chat_channel": "retired-channel"}
    ).global_chat_channel is None
