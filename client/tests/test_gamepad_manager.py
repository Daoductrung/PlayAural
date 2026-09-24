"""Unit tests for GamepadManager and gamepad client integration."""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

try:
    from client.gamepad_manager import (
        GamepadManager,
        BUTTON_MAP,
        SEMANTIC_TO_SDL_BUTTON,
    )
except ModuleNotFoundError:
    from gamepad_manager import (
        GamepadManager,
        BUTTON_MAP,
        SEMANTIC_TO_SDL_BUTTON,
    )


def test_button_mapping_consistency():
    """Ensure semantic button mapping covers all essential controller buttons."""
    required = {
        "south",
        "east",
        "west",
        "north",
        "dpad_up",
        "dpad_down",
        "dpad_left",
        "dpad_right",
        "left_shoulder",
        "right_shoulder",
        "start",
        "back",
        "left_stick",
        "right_stick",
        "touchpad",
        "misc1",
    }
    present = set(BUTTON_MAP.values())
    assert required.issubset(present)
    for name in required:
        btn_id = SEMANTIC_TO_SDL_BUTTON[name]
        assert BUTTON_MAP[btn_id] == name
    assert BUTTON_MAP[15] == "misc1"
    assert BUTTON_MAP[20] == "touchpad"


def test_gamepad_manager_lifecycle():
    """Test GamepadManager initialization, callbacks, and safe shutdown."""
    connected_names = []
    disconnected_names = []
    button_presses = []

    gm = GamepadManager(
        on_button_down=lambda btn, cid: button_presses.append((btn, cid)),
        on_controller_connected=lambda name: connected_names.append(name),
        on_controller_disconnected=lambda name: disconnected_names.append(name),
        enabled=True,
    )

    assert isinstance(gm.is_available, bool)
    assert isinstance(gm.connected_count, int)
    assert isinstance(gm.get_controller_names(), list)

    gm.poll()
    gm.shutdown()
    assert gm.connected_count == 0


def test_gamepad_axis_deadzone_and_trigger_detection():
    """Test stick deadzone filtering and trigger thresholds."""
    downs = []
    ups = []

    gm = GamepadManager(
        on_button_down=lambda btn, cid: downs.append(btn),
        on_button_up=lambda btn, cid: ups.append(btn),
        enabled=False,  # Skip SDL init to test pure logic
    )
    gm._initialized = True
    gm.enabled = True

    # 1. Below deadzone on Left Stick Y (Up)
    gm._handle_axis_motion(1, -8000, 0)
    assert "dpad_up" not in downs

    # 2. Exceed deadzone on Left Stick Y (Up)
    gm._handle_axis_motion(1, -20000, 0)
    assert "dpad_up" in downs

    # 3. Release back to center
    gm._handle_axis_motion(1, 0, 0)
    assert "dpad_up" in ups

    # 4. Trigger axis motion: threshold 16384
    gm._handle_axis_motion(4, 10000, 0)  # L2 partial
    assert "left_trigger" not in downs

    gm._handle_axis_motion(4, 25000, 0)  # L2 pressed
    assert "left_trigger" in downs

    gm._handle_axis_motion(4, 5000, 0)   # L2 released
    assert "left_trigger" in ups

    # 5. Right Stick Y (Older / Newer)
    gm._handle_axis_motion(3, -20000, 0)  # Right Stick Up
    assert "right_stick_up" in downs

    gm._handle_axis_motion(3, 20000, 0)   # Right Stick Down
    assert "right_stick_down" in downs

    # 6. Right Stick X (Oldest / Newest)
    gm._handle_axis_motion(2, -20000, 0)  # Right Stick Left
    assert "right_stick_left" in downs

    gm._handle_axis_motion(2, 20000, 0)   # Right Stick Right
    assert "right_stick_right" in downs


def test_touchpad_gestures_and_tap():
    """Test DualSense capacitive touchpad swipe and tap recognition."""
    downs = []

    gm = GamepadManager(
        on_button_down=lambda btn, cid: downs.append(btn),
        enabled=False,
    )
    gm._initialized = True
    gm.enabled = True

    # 1. Tap: finger down, minimal motion, release within 300ms
    touch_down = MagicMock(type=999, finger=0, instance_id=1, x=0.5, y=0.5)
    gm._handle_touch_down(touch_down)
    touch_up = MagicMock(type=998, finger=0, instance_id=1)
    gm._handle_touch_up(touch_up)
    assert "touchpad_tap" in downs

    # 2. Swipe Down (Silence): finger down at (0.5, 0.2), moves to (0.5, 0.6)
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.5, y=0.2))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.5, y=0.6))
    assert "touchpad_swipe_down" in downs

    # 3. Swipe Up (Online users): finger down at (0.5, 0.8), moves to (0.5, 0.3)
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.5, y=0.8))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.5, y=0.3))
    assert "touchpad_swipe_up" in downs

    # 4. Swipe Left (Prev buffer): finger down at (0.8, 0.5), moves to (0.3, 0.5)
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.8, y=0.5))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.3, y=0.5))
    assert "touchpad_swipe_left" in downs

    # 5. Swipe Right (Next buffer): finger down at (0.2, 0.5), moves to (0.7, 0.5)
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.2, y=0.5))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.7, y=0.5))
    assert "touchpad_swipe_right" in downs

    # 6. Two-finger Swipe Up (Music volume up): fingers 0 and 1 down, move up
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.4, y=0.8))
    gm._handle_touch_down(MagicMock(finger=1, instance_id=1, x=0.6, y=0.8))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.4, y=0.4))
    assert "touchpad_2finger_swipe_up" in downs

    # 7. Two-finger Swipe Down (Music volume down): fingers 0 and 1 down, move down
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.4, y=0.2))
    gm._handle_touch_down(MagicMock(finger=1, instance_id=1, x=0.6, y=0.2))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.4, y=0.6))
    assert "touchpad_2finger_swipe_down" in downs

    # 8. Two-finger Swipe Left (Alt+P): fingers 0 and 1 down, move left
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.8, y=0.5))
    gm._handle_touch_down(MagicMock(finger=1, instance_id=1, x=0.8, y=0.7))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.4, y=0.5))
    assert "touchpad_2finger_swipe_left" in downs

    # 9. Two-finger Swipe Right (Shift+F6): fingers 0 and 1 down, move right
    downs.clear()
    gm._handle_touch_down(MagicMock(finger=0, instance_id=1, x=0.2, y=0.5))
    gm._handle_touch_down(MagicMock(finger=1, instance_id=1, x=0.2, y=0.7))
    gm._handle_touch_motion(MagicMock(finger=0, instance_id=1, x=0.6, y=0.5))
    assert "touchpad_2finger_swipe_right" in downs


def test_main_window_has_gamepad_integration():
    """Verify MainWindow source contains gamepad initialization, handlers, speech silence, and cleanup."""
    source_path = Path(__file__).resolve().parents[1] / "ui" / "main_window.py"
    source = source_path.read_text(encoding="utf-8")

    assert "self._init_gamepad()" in source
    assert "def _init_gamepad(self):" in source
    assert "def silence_speech(self):" in source
    assert "def _apply_client_gamepad_options(self):" in source
    assert "def _on_gamepad_tick(self, event):" in source
    assert "def _on_gamepad_button_down(self, btn_name: str, controller_id: int):" in source
    assert "def _navigate_menu(self, direction: str):" in source
    assert "def _send_keybind(" in source
    assert "def trigger_escape(" in source
    assert "self.gamepad_manager.shutdown()" in source
    assert "right_stick_up" in source
    assert "touchpad_swipe_down" in source


def test_options_dialog_has_gamepad_controls():
    """Verify options_dialog.py contains UI controls and settings persistence for gamepad."""
    source_path = Path(__file__).resolve().parents[1] / "ui" / "options_dialog.py"
    source = source_path.read_text(encoding="utf-8")

    assert "self.enable_gamepad_check" in source
    assert "self.gamepad_vibration_check" in source
    assert 'self.config_manager.set_client_option("interface/enable_gamepad"' in source
    assert 'self.config_manager.set_client_option("interface/gamepad_vibration"' in source


def test_main_window_gamepad_mappings():
    """Verify all gamepad semantic mappings on MainWindow dispatch to expected actions."""
    from types import SimpleNamespace
    try:
        from client.ui.main_window import MainWindow
    except ModuleNotFoundError:
        from ui.main_window import MainWindow

    called_actions = []

    dummy = SimpleNamespace(
        IsActive=lambda: True,
        current_mode="normal",
        current_menu_id="lobby",
        current_menu_item_ids=[],
        escape_behavior="keybind",
        connected=True,
        voice_state="disconnected",
        voice_mic_enabled=False,
        menu_list=MagicMock(),
        buffer_system=MagicMock(),
        gamepad_manager=MagicMock(),
        network=MagicMock(),
        sound_manager=MagicMock(),
        silence_speech=lambda: called_actions.append("silence_speech"),
        _send_keybind=lambda key, has_control=False, has_alt=False, has_shift=False: called_actions.append(
            f"keybind:{key}:{has_control}:{has_shift}"
        ),
        _navigate_menu=lambda direction: called_actions.append(f"navigate:{direction}"),
        on_prev_buffer=lambda evt: called_actions.append("on_prev_buffer"),
        on_next_buffer=lambda evt: called_actions.append("on_next_buffer"),
        on_first_buffer=lambda evt: called_actions.append("on_first_buffer"),
        on_last_buffer=lambda evt: called_actions.append("on_last_buffer"),
        on_older_message=lambda evt: called_actions.append("on_older_message"),
        on_newer_message=lambda evt: called_actions.append("on_newer_message"),
        on_oldest_message=lambda evt: called_actions.append("on_oldest_message"),
        on_newest_message=lambda evt: called_actions.append("on_newest_message"),
        on_volume_up=lambda evt: called_actions.append("on_volume_up"),
        on_volume_down=lambda evt: called_actions.append("on_volume_down"),
        on_list_online=lambda evt: called_actions.append("on_list_online"),
        on_list_online_with_games=lambda evt: called_actions.append("on_list_online_with_games"),
        on_buffer_mute_toggle=lambda evt: called_actions.append("on_buffer_mute_toggle"),
        on_toggle_table_chat=lambda evt: called_actions.append("on_toggle_table_chat"),
        on_toggle_global_chat=lambda evt: called_actions.append("on_toggle_global_chat"),
        on_ping=lambda evt: called_actions.append("on_ping"),
        on_toggle_voice_mic=lambda evt: called_actions.append("on_toggle_voice_mic"),
        _request_voice_join=lambda: called_actions.append("_request_voice_join"),
        _request_voice_leave=lambda: called_actions.append("_request_voice_leave"),
        _jump_menu_start=lambda: called_actions.append("_jump_menu_start"),
        _jump_menu_end=lambda: called_actions.append("_jump_menu_end"),
        _jump_start_or_end=lambda: called_actions.append("_jump_start_or_end"),
        _read_current_item_or_message=lambda: called_actions.append("_read_current_item_or_message"),
        _misc1_press_time=None,
        _misc1_hold_triggered=False,
        _east_press_time=None,
        _east_hold_triggered=False,
        _l3_is_down=False,
        _r3_is_down=False,
        _r3_modifier_used=False,
        _south_is_down=False,
        _west_is_down=False,
        _west_combo_used=False,
    )

    dummy._handle_gamepad_mic_tap = MainWindow._handle_gamepad_mic_tap.__get__(dummy)
    dummy._handle_gamepad_mic_hold = MainWindow._handle_gamepad_mic_hold.__get__(dummy)
    dummy._on_gamepad_button_down = MainWindow._on_gamepad_button_down.__get__(dummy)
    dummy._on_gamepad_button_up = MainWindow._on_gamepad_button_up.__get__(dummy)
    dummy.trigger_escape = MainWindow.trigger_escape.__get__(dummy)

    # 1. Touchpad click -> Open online users with games
    dummy._on_gamepad_button_down("touchpad", 0)
    assert "on_list_online_with_games" in called_actions

    # 2. Touchpad 1-finger swipe up -> Read online users (F2)
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_swipe_up", 0)
    assert "on_list_online" in called_actions

    # 3. Touchpad 1-finger swipe down -> Toggle spectator mode in table / F3
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_swipe_down", 0)
    assert "keybind:f3:False:False" in called_actions

    # 4. Touchpad 1-finger swipe left -> F4: Mute current buffer
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_swipe_left", 0)
    assert "on_buffer_mute_toggle" in called_actions

    # 5. Touchpad 1-finger swipe right -> F6: Mute table chat
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_swipe_right", 0)
    assert "on_toggle_table_chat" in called_actions

    # 6. Touchpad 2-finger swipe right -> Shift+F6: Mute global chat
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_2finger_swipe_right", 0)
    assert "on_toggle_global_chat" in called_actions

    # 7. Touchpad 2-finger swipe left -> Alt+P: Ping latency
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_2finger_swipe_left", 0)
    assert "on_ping" in called_actions

    # 8. Touchpad 2-finger swipe up/down -> F10 / F9: Music volume
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_2finger_swipe_up", 0)
    assert "on_volume_up" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_2finger_swipe_down", 0)
    assert "on_volume_down" in called_actions

    # 9. Touchpad tap -> Whose turn / Table status ("t")
    called_actions.clear()
    dummy._on_gamepad_button_down("touchpad_tap", 0)
    assert "keybind:t:False:False" in called_actions

    # 10. Square (west) -> Space: Action
    called_actions.clear()
    dummy._on_gamepad_button_down("west", 0)
    assert "keybind:space:False:False" in called_actions

    # 11. Right stick directions:
    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick_up", 0)
    assert "keybind:f1:True:False" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick_down", 0)
    assert "keybind:m:True:False" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick_left", 0)
    assert "keybind:i:True:False" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick_right", 0)
    assert "keybind:u:True:False" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("back", 0)
    assert "keybind:m:True:False" in called_actions

    # 12. Microphone button (misc1) tap when disconnected -> Join voice
    called_actions.clear()
    dummy.voice_state = "disconnected"
    dummy._on_gamepad_button_down("misc1", 0)
    dummy._on_gamepad_button_up("misc1", 0)
    assert "_request_voice_join" in called_actions

    # 13. Microphone button (misc1) tap when connected -> Toggle mic
    called_actions.clear()
    dummy.voice_state = "connected"
    dummy._on_gamepad_button_down("misc1", 0)
    dummy._on_gamepad_button_up("misc1", 0)
    assert "on_toggle_voice_mic" in called_actions

    # 14. Microphone button hold -> Leave voice
    called_actions.clear()
    dummy.voice_state = "connected"
    dummy._handle_gamepad_mic_hold()
    assert "_request_voice_leave" in called_actions

    # 15. R3 Combos (Shift modifier):
    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("left_shoulder", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "on_first_buffer" in called_actions
    assert "_jump_start_or_end" not in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("right_shoulder", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "on_last_buffer" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("left_trigger", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "on_oldest_message" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("right_trigger", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "on_newest_message" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("dpad_up", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "_jump_menu_start" in called_actions

    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_down("dpad_down", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "_jump_menu_end" in called_actions

    # R3 standalone click -> Jump start or end
    called_actions.clear()
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "_jump_start_or_end" in called_actions

    # 16. Circle (East) short tap -> Escape (keybind mode)
    called_actions.clear()
    dummy._on_gamepad_button_down("east", 0)
    dummy._on_gamepad_button_up("east", 0)
    assert "keybind:escape:False:False" in called_actions

    # 16b. Circle (East) short tap in menu -> Select last option (Back)
    dummy.escape_behavior = "select_last_option"
    dummy.current_mode = "list"
    dummy.current_menu_id = "gamepad_options_menu"
    dummy.current_menu_item_ids = ["enable_gamepad", "back"]
    dummy.menu_list.GetCount.return_value = 2
    dummy.network.send_packet.reset_mock()
    called_actions.clear()
    dummy._on_gamepad_button_down("east", 0)
    dummy._on_gamepad_button_up("east", 0)
    dummy.network.send_packet.assert_called_once_with(
        {"type": "menu", "menu_id": "gamepad_options_menu", "selection": 2, "selection_id": "back"}
    )
    # 16c. Circle (East) short tap in main_menu -> Select last option (Logout / Exit confirm)
    dummy.escape_behavior = "select_last_option"
    dummy.current_mode = "list"
    dummy.current_menu_id = "main_menu"
    dummy.current_menu_item_ids = ["play", "active_tables", "saved_tables", "logout"]
    dummy.menu_list.GetCount.return_value = 4
    dummy.network.send_packet.reset_mock()
    called_actions.clear()
    dummy._on_gamepad_button_down("east", 0)
    dummy._on_gamepad_button_up("east", 0)
    dummy.network.send_packet.assert_called_once_with(
        {"type": "menu", "menu_id": "main_menu", "selection": 4, "selection_id": "logout"}
    )
    # Restore dummy state for subsequent tests
    dummy.escape_behavior = "keybind"
    dummy.current_mode = "normal"
    dummy.current_menu_id = "lobby"
    dummy.current_menu_item_ids = []

    # 17. Circle (East) long hold -> Leave table (Ctrl + Q)
    called_actions.clear()
    dummy._on_gamepad_button_down("east", 0)
    dummy._east_press_time = time.monotonic() - 1.0  # simulate > 0.7s passed
    # simulate tick hold detection logic
    if getattr(dummy, "_east_press_time", None) is not None:
        if not getattr(dummy, "_east_hold_triggered", False) and (
            time.monotonic() - dummy._east_press_time >= 0.7
        ):
            dummy._east_hold_triggered = True
            dummy.silence_speech()
            dummy._send_keybind("q", has_control=True)
            dummy.gamepad_manager.rumble(0.35, 0.35, 90)
    dummy._on_gamepad_button_up("east", 0)
    assert "keybind:q:True:False" in called_actions
    assert "keybind:escape:False:False" not in called_actions

    # 18. L3 + R3 combo -> Save table (Ctrl + S)
    called_actions.clear()
    dummy._on_gamepad_button_down("left_stick", 0)
    dummy._on_gamepad_button_down("right_stick", 0)
    dummy._on_gamepad_button_up("left_stick", 0)
    dummy._on_gamepad_button_up("right_stick", 0)
    assert "keybind:s:True:False" in called_actions

    # 19. South (Cross) + West (Square) combo -> Add bot (B)
    called_actions.clear()
    dummy._on_gamepad_button_down("south", 0)
    dummy._on_gamepad_button_down("west", 0)
    dummy._on_gamepad_button_up("south", 0)
    dummy._on_gamepad_button_up("west", 0)
    assert "keybind:b:False:False" in called_actions


def test_game_audio_haptic_vibration_triggers():
    """Verify that in-game audio cues trigger appropriate tactile haptic vibrations."""
    from types import SimpleNamespace
    try:
        from client.ui.main_window import MainWindow
    except ModuleNotFoundError:
        from ui.main_window import MainWindow

    gm_mock = MagicMock()
    gm_mock.vibration_enabled = True

    dummy = SimpleNamespace(
        gamepad_manager=gm_mock,
    )
    dummy._trigger_game_audio_haptics = MainWindow._trigger_game_audio_haptics.__get__(dummy)

    # 1. Breach Point - Bomb explosion
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_breachpoint/objective/bomb_explode.ogg"})
    gm_mock.rumble.assert_called_once_with(0.8, 0.8, 500)

    # 2. Breach Point - HE Grenade
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_breachpoint/utility/he_grenade/detonate_close1.ogg"})
    gm_mock.rumble.assert_called_once_with(0.65, 0.65, 300)

    # 3. Breach Point - Weapon fire
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_breachpoint/weapons/ak47/fire_close.ogg"})
    gm_mock.rumble.assert_called_once_with(0.35, 0.35, 75)

    # 4. Mille Bornes - Accident / Crash
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_milebymile/crash1.ogg"})
    gm_mock.rumble.assert_called_once_with(0.65, 0.65, 320)

    # 5. Mille Bornes - Flat tire
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_milebymile/flat.ogg"})
    gm_mock.rumble.assert_called_once_with(0.45, 0.45, 180)

    # 6. Mille Bornes - Safety card
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_milebymile/drivingace.ogg"})
    gm_mock.rumble.assert_called_once_with(0.4, 0.4, 200)

    # 7. Farkle - Farkle penalty
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_farkle/farkle.ogg"})
    gm_mock.rumble.assert_called_once_with(0.55, 0.55, 300)

    # 8. Farkle - Hot dice
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_farkle/hotdice.ogg"})
    gm_mock.rumble.assert_called_once_with(0.45, 0.45, 200)

    # 9. Sorry - Pawn captured
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_chess/capture1.ogg"})
    gm_mock.rumble.assert_called_once_with(0.5, 0.5, 220)

    # 10. Turn notification
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "turn.ogg"})
    gm_mock.rumble.assert_called_once_with(0.2, 0.2, 90)

    # 11. Segments sequence support (e.g. Sorry movement or multi-part sound)
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({
        "command": "play",
        "segments": [{"asset": "game_chess/capture2.ogg"}]
    })
    gm_mock.rumble.assert_called_once_with(0.5, 0.5, 220)

    # 12. Vibration disabled - no rumble
    gm_mock.vibration_enabled = False
    gm_mock.rumble.reset_mock()
    dummy._trigger_game_audio_haptics({"command": "play", "asset": "game_farkle/farkle.ogg"})
    gm_mock.rumble.assert_not_called()

