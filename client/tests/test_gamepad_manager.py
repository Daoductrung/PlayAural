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
