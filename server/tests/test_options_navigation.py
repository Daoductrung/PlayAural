"""Test options navigation: submenu flows and editbox restore paths."""

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


def _make_server(tmp_path):
    server = Server(db_path=tmp_path / "options_nav.sqlite")
    server._db.connect()
    record = server._db.create_user("NavTester", "hash", trust_level=1)
    user = MockUser("NavTester", uuid=record.uuid)
    # MockUser defaults to client_type="python" (desktop-like, non-web/mobile).
    # It has no network connection so client-sync side effects are ignored.
    server._users[user.username] = user
    server._sync_pref_to_client = lambda *args, **kwargs: None
    server._show_main_menu(user)
    return server, user


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Full options navigation tree — no leaks to main_menu
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_options_audio_submenu_toggle_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        assert _current_menu(server, user.username) == "options_menu"
        # After _handle_open_options: stack = [main_menu, ...?], state = options_menu
        # We only care that the menu is correct, not exact stack depth.
        stack_before = len(_stack(server, user.username))

        # Enter Audio submenu via nav_push
        await server._handle_options_selection(user, "options_audio")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Toggle turn sound → stays in audio submenu
        await server._handle_audio_submenu_selection(user, "turn_sound")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Press Back → should return to options hub, not main_menu
        await server._handle_audio_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_game_submenu_toggle_stays_in_game_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        await server._handle_open_options(SimpleNamespace(username=user.username))
        await server._handle_options_selection(user, "options_game")
        assert _current_menu(server, user.username) == "options_game_submenu"

        # Toggle custom bot names → stays in game submenu
        await server._handle_game_submenu_selection(user, "custom_bot_names")
        assert _current_menu(server, user.username) == "options_game_submenu"

        # Press Back → options hub
        await server._handle_game_submenu_selection(user, "back")
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

        # Desktop client shows invert_multiline_enter toggle
        await server._handle_accessibility_submenu_selection(user, "invert_multiline_enter")
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        await server._handle_accessibility_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Sub-submenu navigation (options → submenu → sub-submenu → back)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audio_submenu_to_audio_input_device_and_back(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"
        # _show_options_menu replaced main_menu; nav_push saves [options_menu]
        assert len(_stack(server, user.username)) == 1

        # Push to audio input device menu
        await server._handle_audio_submenu_selection(user, "audio_input_device")
        assert _current_menu(server, user.username) == "audio_input_device_menu"
        assert len(_stack(server, user.username)) == 2

        # Back → audio submenu
        await server._handle_audio_input_device_selection(user, "back")
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Back → options hub
        await server._handle_audio_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_game_submenu_to_dice_keeping_style_and_back(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_game_submenu)
        assert _current_menu(server, user.username) == "options_game_submenu"
        assert len(_stack(server, user.username)) == 1

        # Push to dice keeping style
        await server._handle_game_submenu_selection(user, "dice_keeping_style")
        assert _current_menu(server, user.username) == "dice_keeping_style_menu"
        assert len(_stack(server, user.username)) == 2

        # Back → game submenu
        await server._handle_dice_keeping_style_selection(user, "back")
        assert _current_menu(server, user.username) == "options_game_submenu"

        # Back → options hub
        await server._handle_game_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Editbox volume from audio submenu → stays in audio submenu
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_volume_editbox_submit_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Enter music volume editbox
        await server._handle_audio_submenu_selection(user, "music_volume")
        assert _current_menu(server, user.username) == "music_volume_input"
        state = _user_state(server, user.username)
        assert state.get("_transient") is True
        assert state.get("_parent_frame", {}).get("menu") == "options_audio_submenu"

        # Submit the editbox
        packet = {"input_id": "music_volume_input", "text": "75"}
        await server._handle_editbox(
            SimpleNamespace(username=user.username), packet
        )
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_volume_editbox_cancel_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Enter ambience volume editbox
        await server._handle_audio_submenu_selection(user, "ambience_volume")
        assert _current_menu(server, user.username) == "ambience_volume_input"

        # Cancel (empty text = cancel)
        packet = {"input_id": "ambience_volume_input", "text": ""}
        await server._handle_editbox(
            SimpleNamespace(username=user.username), packet
        )
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_volume_editbox_invalid_value_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"

        # Enter voice volume with out-of-range value
        await server._handle_audio_submenu_selection(user, "voice_volume")
        packet = {"input_id": "voice_volume_input", "text": "999"}
        await server._handle_editbox(
            SimpleNamespace(username=user.username), packet
        )
        # Should stay in audio submenu (error is spoken); not main menu
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Editbox cancel via ESC packet → stays in audio submenu
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_volume_editbox_escape_cancellation_stays_in_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)
        assert _current_menu(server, user.username) == "options_audio_submenu"

        await server._handle_audio_submenu_selection(user, "voice_volume")
        assert _current_menu(server, user.username) == "voice_volume_input"

        # Simulate ESC: packet with cancelled=True (desktop client style)
        packet = {"cancelled": True, "input_id": "voice_volume_input"}
        await server._handle_editbox(
            SimpleNamespace(username=user.username), packet
        )
        assert _current_menu(server, user.username) == "options_audio_submenu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Dice keeping style selection → stays in game submenu
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dice_keeping_style_select_style_stays_in_game_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_game_submenu)
        assert _current_menu(server, user.username) == "options_game_submenu"

        await server._handle_game_submenu_selection(user, "dice_keeping_style")
        assert _current_menu(server, user.username) == "dice_keeping_style_menu"

        # Select first style option
        current_items = user.get_current_menu_items("dice_keeping_style_menu") or []
        style_items = [i for i in current_items if i.id and i.id.startswith("style_")]
        assert len(style_items) > 0, "Expected style options in dice keeping style menu"
        await server._handle_dice_keeping_style_selection(user, style_items[0].id)

        # Should return to game submenu, not main menu
        assert _current_menu(server, user.username) == "options_game_submenu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Accessibility submenu → speech settings → back chain
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_accessibility_to_speech_settings_and_back(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_accessibility_submenu)
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        # Web client (client_type="web") → shows "web_speech_settings" item
        # that leads to speech_settings_menu.
        user.client_type = "web"
        server._show_options_menu(user)
        server._nav_push(user, server._show_accessibility_submenu)
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        await server._handle_accessibility_submenu_selection(user, "web_speech_settings")
        assert _current_menu(server, user.username) == "speech_settings_menu"

        # Back → accessibility submenu
        await server._handle_speech_settings_selection(user, "back")
        assert _current_menu(server, user.username) == "options_accessibility_submenu"

        # Back → options hub
        await server._handle_accessibility_submenu_selection(user, "back")
        assert _current_menu(server, user.username) == "options_menu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: _restore_frame for options submenus — simulates what _nav_back does
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_restore_frame_audio_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_audio_submenu)

        frame = {"menu": "options_audio_submenu"}
        stack = list(_stack(server, user.username))

        server._restore_frame(user, frame, stack)
        assert _current_menu(server, user.username) == "options_audio_submenu"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_game_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_game_submenu)

        frame = {"menu": "options_game_submenu"}
        stack = list(_stack(server, user.username))

        server._restore_frame(user, frame, stack)
        assert _current_menu(server, user.username) == "options_game_submenu"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_notifications_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_notifications_submenu)

        frame = {"menu": "options_notifications_submenu"}
        stack = list(_stack(server, user.username))

        server._restore_frame(user, frame, stack)
        assert _current_menu(server, user.username) == "options_notifications_submenu"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_restore_frame_accessibility_submenu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_accessibility_submenu)

        frame = {"menu": "options_accessibility_submenu"}
        stack = list(_stack(server, user.username))

        server._restore_frame(user, frame, stack)
        assert _current_menu(server, user.username) == "options_accessibility_submenu"
        assert server._user_states[user.username]["_stack"] == stack
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Escape behavior in all options submenus defaults to SELECT_LAST
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_options_submenus_escape_behavior_is_select_last(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        from ..users.base import EscapeBehavior

        server._show_options_menu(user)

        for submenu_name, show_fn in [
            ("audio", server._show_audio_submenu),
            ("notifications", server._show_notifications_submenu),
            ("game", server._show_game_submenu),
            ("accessibility", server._show_accessibility_submenu),
        ]:
            server._nav_push(user, show_fn)
            # Find the escape_behavior from the show_menu message the MockUser received
            menu_messages = [
                m for m in user.messages
                if m.type == "show_menu" and m.data.get("menu_id")
                and m.data["menu_id"].startswith("options_")
            ]
            if menu_messages:
                last = menu_messages[-1]
                eb = last.data.get("escape_behavior")
                assert eb == EscapeBehavior.SELECT_LAST, (
                    f"{submenu_name} submenu escape_behavior = {eb!r}, "
                    f"expected SELECT_LAST"
                )
            server._nav_back(user)
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: Options hub back → returns to parent (main_menu)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_options_hub_back_returns_to_main_menu(tmp_path) -> None:
    server, user = _make_server(tmp_path)
    try:
        # Open options from main menu
        await server._handle_open_options(SimpleNamespace(username=user.username))
        assert _current_menu(server, user.username) == "options_menu"

        # Back → should return to main menu
        await server._handle_options_selection(user, "back")
        assert _current_menu(server, user.username) == "main_menu"
    finally:
        server._db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: Dice keeping style ESC → game submenu, not main menu
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dice_keeping_style_escape_returns_to_game_submenu(tmp_path) -> None:
    """Simulate ESC pressed on the dice keeping style menu.

    Client sends: {"type": "menu", "selection_id": "back"}.
    Server's _handle_menu sees _transient=False and selection_id="back"
    → routes to _handle_dice_keeping_style_selection → nav_back → game submenu.
    """
    server, user = _make_server(tmp_path)
    try:
        server._show_options_menu(user)
        server._nav_push(user, server._show_game_submenu)
        assert _current_menu(server, user.username) == "options_game_submenu"

        # Open dice keeping style
        await server._handle_game_submenu_selection(user, "dice_keeping_style")
        assert _current_menu(server, user.username) == "dice_keeping_style_menu"

        # Simulate ESC in dice keeping style menu
        await server._handle_menu(
            SimpleNamespace(username=user.username),
            {"type": "menu", "menu_id": "dice_keeping_style_menu", "selection_id": "back"}
        )
        # Should return to game submenu, NOT main menu
        assert _current_menu(server, user.username) == "options_game_submenu"
    finally:
        server._db.close()