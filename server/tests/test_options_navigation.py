"""Test options navigation: General Options submenus, Game Options (declarative
preferences with per-game overrides), and editbox restore paths."""

from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..users.test_user import MockUser


def _user_state(server, username: str) -> dict:
    return server._user_states.get(username, {})


def _stack(server, username: str) -> list:
    return _user_state(server, username).get("_stack", [])


def _current_menu(server, username: str) -> str:
    return _user_state(server, username).get("menu", "")


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.id for item in items]


async def _press_space_on(
    server: Server,
    user: MockUser,
    menu_id: str,
    menu_item_id: str,
) -> None:
    await server._handle_keybind(
        SimpleNamespace(username=user.username),
        {
            "type": "keybind",
            "key": "space",
            "menu_id": menu_id,
            "menu_item_id": menu_item_id,
        },
    )


def _make_server(tmp_path):
    server = Server(db_path=tmp_path / "options_nav.sqlite")
    server._db.connect()
    record = server._db.create_user("NavTester", "hash", trust_level=1)
    user = MockUser("NavTester", uuid=record.uuid)
    # MockUser defaults to client_type="python" (desktop-like, non-web/mobile).
    server._users[user.username] = user
    server._sync_pref_to_client = lambda *args, **kwargs: None
    server._show_main_menu(user)
    return server, user


# ─────────────────────────────────────────────────────────────────────────────
# General Options submenus
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_space_speaks_general_option_row_description_only_for_active_row(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        user.clear_messages()

        await _press_space_on(server, user, "personal_options_menu", "options")
        spoken = user.get_spoken_messages()
        assert spoken
        assert "language, audio, accessibility" in spoken[-1]

        user.clear_messages()
        await _press_space_on(server, user, "personal_options_menu", "back")
        assert user.get_spoken_messages() == []

        user.clear_messages()
        await _press_space_on(server, user, "wrong_menu", "options")
        assert user.get_spoken_messages() == []
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_space_speaks_general_options_submenu_descriptions(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        await server._handle_options_selection(user, "options_audio")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        user.clear_messages()
        await _press_space_on(server, user, "options_audio_submenu", "play_typing_sounds")
        spoken = user.get_spoken_messages()
        assert spoken
        assert "typing sounds" in spoken[-1]

        user.clear_messages()
        await _press_space_on(server, user, "options_audio_submenu", "back")
        assert user.get_spoken_messages() == []
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_audio_submenu_toggle_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        assert _current_menu(server, user.username) == "options_menu"

        await server._handle_options_selection(user, "options_audio")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Toggle a still-present audio toggle → stays in audio submenu
        await server._handle_audio_submenu_selection(user, "play_typing_sounds")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        await server._handle_audio_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_notifications_toggle_stays_in_notifications_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        await server._handle_options_selection(user, "options_notifications")
        assert _current_menu(server, user.username) == "options_notifications_submenu"

        await server._handle_notifications_submenu_selection(user, "mute_global_chat")
        assert _current_menu(server, user.username) == "options_notifications_submenu"

        await server._handle_notifications_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_accessibility_toggle_stays_in_accessibility_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        await server._handle_options_selection(user, "options_accessibility")
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        await server._handle_accessibility_submenu_selection(user, "invert_multiline_enter")
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        await server._handle_accessibility_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_audio_submenu_to_audio_input_device_and_back(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"
        assert len(_stack(server, user.username)) == 1

        await server._handle_audio_submenu_selection(user, "audio_input_device")
        assert _current_menu(server, user.username) == "audio_input_device_menu"
        assert len(_stack(server, user.username)) == 2

        await server._handle_audio_input_device_selection(user, "back")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        await server._handle_audio_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_volume_selection_menu_submit_returns_to_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)

        await server._handle_audio_submenu_selection(user, "music_volume")
        assert _current_menu(server, user.username) == "volume_selection_menu"
        state = _user_state(server, user.username)
        assert state.get("volume_type") == "music_volume"
        assert state.get("_stack", [])[-1].get("menu") == "options_audio_submenu"

        item_ids = [item.id for item in user.menus["volume_selection_menu"]["items"]]
        assert item_ids[:2] == ["volume_0", "volume_10"]
        assert item_ids[-2:] == ["volume_100", "back"]

        await server._handle_volume_selection(user, "volume_70", state)
        assert user.preferences.music_volume == 70
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_sound_effects_volume_has_no_off_choice(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)

        await server._handle_audio_submenu_selection(user, "sound_volume")
        assert _current_menu(server, user.username) == "volume_selection_menu"
        state = _user_state(server, user.username)
        assert state.get("volume_type") == "sound_volume"

        item_ids = [item.id for item in user.menus["volume_selection_menu"]["items"]]
        assert "volume_0" not in item_ids
        assert item_ids[0] == "volume_10"
        assert item_ids[-2:] == ["volume_100", "back"]

        await server._handle_volume_selection(user, "volume_50", state)
        assert user.preferences.sound_volume == 50
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_set_preference_rejects_invalid_volume_steps(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        client = SimpleNamespace(username=user.username)

        await server._handle_set_preference(
            client,
            {"key": "audio/sound_volume", "value": 0},
        )
        assert user.preferences.sound_volume == 100

        await server._handle_set_preference(
            client,
            {"key": "audio/music_volume", "value": 75},
        )
        assert user.preferences.music_volume == 10

        await server._handle_set_preference(
            client,
            {"key": "audio/sound_volume", "value": 60},
        )
        assert user.preferences.sound_volume == 60

        await server._handle_set_preference(
            client,
            {"key": "speech_rate", "value": 125},
        )
        assert user.preferences.speech_rate == 100

        await server._handle_set_preference(
            client,
            {"key": "speech_rate", "value": 130},
        )
        assert user.preferences.speech_rate == 130

        await server._handle_set_preference(
            client,
            {"key": "mobile/tts_rate", "value": 205},
        )
        assert user.preferences.mobile_tts_rate == 100

        await server._handle_set_preference(
            client,
            {"key": "mobile/tts_rate", "value": 180},
        )
        assert user.preferences.mobile_tts_rate == 180
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_hub_back_returns_to_main_menu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        assert _current_menu(server, user.username) == "options_menu"
        await server._handle_options_selection(user, "back")
        assert _current_menu(server, user.username) == "main_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_global_back_restores_focus_to_parent_item(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "main_menu",
                "selection_id": "leaderboards",
            },
        )
        assert _current_menu(server, user.username) == "leaderboards_menu"

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "leaderboards_menu",
                "selection_id": "back",
            },
        )

        assert _current_menu(server, user.username) == "main_menu"
        assert user.menus["main_menu"]["selection_id"] == "leaderboards"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_action_close_restores_focus_to_parent_opener(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._nav_push(user, server._show_profile_menu)
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "profile_menu",
                "selection": 4,
                "selection_id": "edit_gender",
            },
        )
        assert _current_menu(server, user.username) == "gender_menu"

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "gender_menu",
                "selection": 1,
                "selection_id": "gender_Male",
            },
        )

        assert _current_menu(server, user.username) == "profile_menu"
        assert user.menus["profile_menu"]["selection_id"] == "edit_gender"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_action_close_uses_position_when_parent_item_disappears(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        requester = server._db.create_user("Requester", "hash", trust_level=1)
        viewer = server._db.get_user(user.username)
        assert viewer is not None
        assert server._db.send_friend_request(requester.uuid, viewer.uuid) == "sent"

        server._show_friend_requests_menu(user)
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "friend_requests_menu",
                "selection": 1,
                "selection_id": "req_Requester",
            },
        )
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "friend_request_actions_menu",
                "selection": 1,
                "selection_id": "accept",
            },
        )

        assert _current_menu(server, user.username) == "friend_requests_menu"
        restored = user.menus["friend_requests_menu"]
        assert restored["selection_id"] is None
        assert restored["position"] == 1
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_friend_requests_menu_pages_large_pending_lists(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        viewer = server._db.get_user(user.username)
        assert viewer is not None
        for index in range(101):
            requester = server._db.create_user(f"Requester{index:03d}", "hash")
            assert requester is not None
            assert server._db.send_friend_request(requester.uuid, viewer.uuid) == "sent"

        server._show_friend_requests_menu(user)
        ids = _menu_ids(user, "friend_requests_menu")
        assert len([item_id for item_id in ids if item_id.startswith("req_")]) == 100
        assert "req_Requester100" not in ids
        assert "refresh" not in ids
        assert "page_next" in ids

        await server._handle_friend_requests_selection(
            user,
            "page_next",
            server._user_states[user.username],
        )

        second_page_ids = _menu_ids(user, "friend_requests_menu")
        assert server._user_states[user.username]["friend_requests_page"] == 2
        assert "req_Requester100" in second_page_ids
        assert "page_previous" in second_page_ids
        assert "page_next" not in second_page_ids
        assert user.menus["friend_requests_menu"]["position"] == 1
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_saved_tables_menu_pages_large_lists(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        last_record_id = 0
        for index in range(101):
            record = server._db.save_user_table(
                user.username,
                f"Save {index:03d}",
                "pig",
                "{}",
                "[]",
            )
            last_record_id = record.id

        server._show_saved_tables_menu(user)
        ids = _menu_ids(user, "saved_tables_menu")
        assert len([item_id for item_id in ids if item_id.startswith("saved_")]) == 100
        assert f"saved_{last_record_id}" in ids
        assert "refresh" not in ids
        assert "page_next" in ids

        await server._handle_saved_tables_selection(
            user,
            "page_next",
            server._user_states[user.username],
        )

        second_page_ids = _menu_ids(user, "saved_tables_menu")
        assert server._user_states[user.username]["saved_tables_page"] == 2
        assert "page_previous" in second_page_ids
        assert "page_next" not in second_page_ids
        assert user.menus["saved_tables_menu"]["position"] == 1
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_speech_rate_selection_menu_restores_parent_focus(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.client_type = "web"
        server._show_speech_settings_menu(user)
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "speech_settings_menu",
                "selection": 2,
                "selection_id": "speech_rate",
            },
        )
        assert _current_menu(server, user.username) == "speech_rate_selection_menu"
        state = _user_state(server, user.username)
        assert state.get("speech_rate_type") == "speech_rate"
        item_ids = [item.id for item in user.menus["speech_rate_selection_menu"]["items"]]
        assert item_ids[:2] == ["rate_50", "rate_60"]
        assert item_ids[-2:] == ["rate_300", "back"]

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "speech_rate_selection_menu",
                "selection_id": "rate_150",
            },
        )

        assert user.preferences.speech_rate == 150
        assert _current_menu(server, user.username) == "speech_settings_menu"
        assert user.menus["speech_settings_menu"]["selection_id"] == "speech_rate"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_mobile_tts_rate_selection_menu_restores_parent_focus(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.client_type = "mobile"
        server._show_mobile_speech_settings_menu(user)
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "mobile_speech_settings_menu",
                "selection": 3,
                "selection_id": "mobile_tts_rate",
            },
        )
        assert _current_menu(server, user.username) == "speech_rate_selection_menu"
        state = _user_state(server, user.username)
        assert state.get("speech_rate_type") == "mobile_tts_rate"
        item_ids = [item.id for item in user.menus["speech_rate_selection_menu"]["items"]]
        assert item_ids[:2] == ["rate_50", "rate_60"]
        assert item_ids[-2:] == ["rate_200", "back"]

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "speech_rate_selection_menu",
                "selection_id": "rate_180",
            },
        )

        assert user.preferences.mobile_tts_rate == 180
        assert _current_menu(server, user.username) == "mobile_speech_settings_menu"
        assert user.menus["mobile_speech_settings_menu"]["selection_id"] == "mobile_tts_rate"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_mobile_voice_selection_accepts_client_hydrated_voice_value(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.client_type = "mobile"
        server._show_mobile_speech_settings_menu(user)

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "mobile_speech_settings_menu",
                "selection": 2,
                "selection_id": "mobile_tts_voice",
            },
        )
        assert _current_menu(server, user.username) == "mobile_voice_selection_menu"

        voice_id = "com.google.android.tts:vi-vn-x-vif-local"
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "mobile_voice_selection_menu",
                "selection": 3,
                "selection_id": "mobile_voice_0",
                "selection_value": voice_id,
            },
        )

        assert user.preferences.mobile_tts_voice == voice_id
        assert _current_menu(server, user.username) == "mobile_speech_settings_menu"
        assert user.menus["mobile_speech_settings_menu"]["selection_id"] == "mobile_tts_voice"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_speech_rate_menu_preserves_legacy_off_step_current_value(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.client_type = "web"
        user.preferences.speech_rate = 125
        server._show_speech_settings_menu(user)

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "speech_settings_menu",
                "selection_id": "speech_rate",
            },
        )

        item_ids = [item.id for item in user.menus["speech_rate_selection_menu"]["items"]]
        assert "rate_125" in item_ids
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "speech_rate_selection_menu",
                "selection_id": "rate_125",
            },
        )
        assert user.preferences.speech_rate == 125
        assert _current_menu(server, user.username) == "speech_settings_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_stale_server_menu_packets_are_ignored(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "main_menu",
                "selection_id": "leaderboards",
            },
        )
        assert _current_menu(server, user.username) == "leaderboards_menu"

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "main_menu",
                "selection_id": "play",
            },
        )
        assert _current_menu(server, user.username) == "leaderboards_menu"

        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {
                "type": "menu",
                "menu_id": "leaderboards_menu",
                "selection": 1,
                "selection_id": "play",
            },
        )
        assert _current_menu(server, user.username) == "leaderboards_menu"
        state = _user_state(server, user.username)
        assert state.get("_last_selection_id") != "play"
        assert "_last_selection_position" not in state
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Game Options (declarative preferences)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_game_options_category_and_back(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        assert _current_menu(server, user.username) == "game_options_menu"

        await server._handle_game_options_selection(user, "cat_gameplay")
        assert _current_menu(server, user.username) == "pref_category_menu"
        assert _user_state(server, user.username).get("pref_category") == "gameplay"

        await server._handle_pref_category_selection(user, "back")
        assert _current_menu(server, user.username) == "game_options_menu"

        await server._handle_game_options_selection(user, "back")
        assert _current_menu(server, user.username) == "personal_options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_simple_bool_pref_toggles_in_place(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        await server._handle_game_options_selection(user, "cat_gameplay")

        before = user.preferences.allow_custom_bot_names
        # allow_custom_bot_names has no per-game overrides → toggles in place.
        await server._handle_pref_category_selection(user, "pref_allow_custom_bot_names")
        assert _current_menu(server, user.username) == "pref_category_menu"
        assert user.preferences.allow_custom_bot_names is (not before)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_pref_with_overrides_opens_detail_and_sets_per_game(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        await server._handle_game_options_selection(user, "cat_gameplay")

        # confirm_destructive_actions is relevant to pusoydos → opens detail menu.
        await server._handle_pref_category_selection(user, "pref_confirm_destructive_actions")
        assert _current_menu(server, user.username) == "pref_detail_menu"
        assert _user_state(server, user.username).get("pref_field") == "confirm_destructive_actions"

        # Cycle the per-game override for pusoydos: Default -> On.
        await server._handle_pref_detail_selection(user, "detail_game_pusoydos")
        assert _current_menu(server, user.username) == "pref_detail_menu"
        assert user.preferences.get_game_override("confirm_destructive_actions", "pusoydos") is True
        assert (
            user.preferences.get_effective("confirm_destructive_actions", "pusoydos") is True
        )

        await server._handle_pref_detail_selection(user, "back")
        assert _current_menu(server, user.username) == "pref_category_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_menu_pref_global_choice_via_detail(tmp_path) -> None:
    from ..users.preferences import DiceKeepingStyle

    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        await server._handle_game_options_selection(user, "cat_dice")

        # dice_keeping_style is a menu pref relevant to dice games → detail menu.
        await server._handle_pref_category_selection(user, "pref_dice_keeping_style")
        assert _current_menu(server, user.username) == "pref_detail_menu"

        # Global value -> choices list.
        await server._handle_pref_detail_selection(user, "detail_global")
        assert _current_menu(server, user.username) == "pref_choices_menu"
        assert _user_state(server, user.username).get("pref_game_type") is None

        await server._handle_pref_choices_selection(user, "choice_value_based")
        assert user.preferences.dice_keeping_style is DiceKeepingStyle.VALUE_BASED
        # Returns to the detail menu.
        assert _current_menu(server, user.username) == "pref_detail_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_menu_pref_per_game_choice(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        await server._handle_game_options_selection(user, "cat_dice")
        await server._handle_pref_category_selection(user, "pref_dice_keeping_style")

        # Per-game override for yahtzee -> choices (with a Default option).
        await server._handle_pref_detail_selection(user, "detail_game_yahtzee")
        assert _current_menu(server, user.username) == "pref_choices_menu"
        assert _user_state(server, user.username).get("pref_game_type") == "yahtzee"

        await server._handle_pref_choices_selection(user, "choice_value_based")
        assert user.preferences.get_game_override("dice_keeping_style", "yahtzee") == "value_based"
        assert _current_menu(server, user.username) == "pref_detail_menu"

        # Reopen and reset to Default clears the override.
        await server._handle_pref_detail_selection(user, "detail_game_yahtzee")
        await server._handle_pref_choices_selection(user, "choice_default")
        assert user.preferences.get_game_override("dice_keeping_style", "yahtzee") is None
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_reset_all_game_prefs(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.preferences.allow_custom_bot_names = True
        user.preferences.set_game_override("confirm_destructive_actions", "pusoydos", False)
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")

        await server._handle_game_options_selection(user, "reset_all")
        assert _current_menu(server, user.username) == "game_options_menu"
        assert user.preferences.allow_custom_bot_names is False
        assert user.preferences.get_game_override("confirm_destructive_actions", "pusoydos") is None
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_space_speaks_pref_description(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_personal_options_menu(user)
        await server._handle_personal_options_selection(user, "game_options")
        await server._handle_game_options_selection(user, "cat_gameplay")

        spoken_before = len(user.get_spoken_messages())
        await server._handle_keybind(
            SimpleNamespace(username=user.username),
            {
                "type": "keybind",
                "key": "space",
                "menu_item_id": "pref_confirm_destructive_actions",
            },
        )
        spoken = user.get_spoken_messages()
        assert len(spoken) > spoken_before
        assert "irreversible" in spoken[-1].lower() or "risky" in spoken[-1].lower()
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# _restore_frame for the new menus
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_space_speaks_pref_detail_description_only_on_pref_rows(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_pref_detail_menu(user, "brief_announcements")
        assert _current_menu(server, user.username) == "pref_detail_menu"

        spoken_before = len(user.get_spoken_messages())
        await server._handle_keybind(
            SimpleNamespace(username=user.username),
            {
                "type": "keybind",
                "key": "space",
                "menu_id": "pref_detail_menu",
                "menu_item_id": "detail_global",
            },
        )
        spoken = user.get_spoken_messages()
        assert len(spoken) == spoken_before + 1
        assert "shorten" in spoken[-1].lower()

        await server._handle_keybind(
            SimpleNamespace(username=user.username),
            {
                "type": "keybind",
                "key": "space",
                "menu_id": "pref_detail_menu",
                "menu_item_id": "back",
            },
        )
        assert user.get_spoken_messages() == spoken
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_space_ignores_stale_or_wrong_pref_description_ids(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_pref_detail_menu(user, "brief_announcements")
        assert _current_menu(server, user.username) == "pref_detail_menu"

        spoken_before = list(user.get_spoken_messages())
        await server._handle_keybind(
            SimpleNamespace(username=user.username),
            {
                "type": "keybind",
                "key": "space",
                "menu_id": "pref_detail_menu",
                "menu_item_id": "pref_confirm_destructive_actions",
            },
        )
        await server._handle_keybind(
            SimpleNamespace(username=user.username),
            {
                "type": "keybind",
                "key": "space",
                "menu_id": "pref_category_menu",
                "menu_item_id": "detail_global",
            },
        )
        assert user.get_spoken_messages() == spoken_before
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        stack = list(_stack(server, user.username))
        server._restore_frame(user, {"menu": "options_audio_submenu"}, stack)
        assert _current_menu(server, user.username) == "options_audio_submenu"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_volume_selection_menu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        stack = list(_stack(server, user.username))
        server._restore_frame(
            user,
            {"menu": "volume_selection_menu", "volume_type": "sound_volume"},
            stack,
        )
        assert _current_menu(server, user.username) == "volume_selection_menu"
        assert _user_state(server, user.username).get("volume_type") == "sound_volume"
        item_ids = [item.id for item in user.menus["volume_selection_menu"]["items"]]
        assert "volume_0" not in item_ids
        assert item_ids[0] == "volume_10"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_speech_rate_selection_menu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        user.client_type = "web"
        server._show_speech_settings_menu(user)
        stack = list(_stack(server, user.username))
        server._restore_frame(
            user,
            {"menu": "speech_rate_selection_menu", "speech_rate_type": "speech_rate"},
            stack,
        )
        assert _current_menu(server, user.username) == "speech_rate_selection_menu"
        assert _user_state(server, user.username).get("speech_rate_type") == "speech_rate"
        item_ids = [item.id for item in user.menus["speech_rate_selection_menu"]["items"]]
        assert item_ids[0] == "rate_50"
        assert item_ids[-2:] == ["rate_300", "back"]
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_game_options_and_category(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_game_options_menu(user)
        stack = list(_stack(server, user.username))
        server._restore_frame(user, {"menu": "game_options_menu"}, stack)
        assert _current_menu(server, user.username) == "game_options_menu"

        server._restore_frame(
            user, {"menu": "pref_category_menu", "pref_category": "dice"}, stack
        )
        assert _current_menu(server, user.username) == "pref_category_menu"
        assert _user_state(server, user.username).get("pref_category") == "dice"

        server._restore_frame(
            user, {"menu": "pref_detail_menu", "pref_field": "dice_keeping_style"}, stack
        )
        assert _current_menu(server, user.username) == "pref_detail_menu"
        assert _user_state(server, user.username).get("pref_field") == "dice_keeping_style"
    finally:
        server._db.close()
