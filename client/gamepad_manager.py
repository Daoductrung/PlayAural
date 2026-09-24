"""Gamepad / Controller manager for PlayAural desktop client.

Provides cross-platform game controller support (PS5 DualSense, Xbox, Switch Pro,
and generic gamepads) powered by SDL2 via pygame-ce.

Features:
- Standardized controller mapping using SDL's GameController database.
- Hotplug detection (connect/disconnect events).
- Analog stick deadzone filtering and directional repeat pacing.
- Semantic button abstraction (south, east, west, north, dpad, shoulders, triggers, start, back).
- Dual-motor haptic feedback / rumble support.
- Safe, non-blocking polling suitable for wx.Timer on the GUI thread.
- Graceful degradation if controller hardware or driver is absent.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_PS4", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_PS4_RUMBLE", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_PS5", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_PS5_RUMBLE", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_SWITCH", "1")
    os.environ.setdefault("SDL_JOYSTICK_HIDAPI_XBOX", "1")
    import pygame
    from pygame._sdl2 import controller as sdl_controller
    PYGAME_CONTROLLER_AVAILABLE = True
except Exception as e:
    PYGAME_CONTROLLER_AVAILABLE = False
    sdl_controller = None
    logger.info("pygame-ce controller subsystem is unavailable: %s", e)


# Semantic button names mapping from SDL controller buttons
BUTTON_MAP: Dict[int, str] = {
    0: "south",          # A / Cross
    1: "east",           # B / Circle
    2: "west",           # X / Square
    3: "north",          # Y / Triangle
    4: "back",           # Back / View / Share / Create
    5: "guide",          # Guide / Home / PS
    6: "start",          # Start / Menu / Options
    7: "left_stick",     # L3
    8: "right_stick",    # R3
    9: "left_shoulder",  # L1 / LB
    10: "right_shoulder", # R1 / RB
    11: "dpad_up",
    12: "dpad_down",
    13: "dpad_left",
    14: "dpad_right",
    15: "touchpad",      # PS4 / PS5 touchpad click
    16: "misc1",         # Mic mute on DualSense
}

# Reverse mapping for testing and simulation
SEMANTIC_TO_SDL_BUTTON: Dict[str, int] = {v: k for k, v in BUTTON_MAP.items()}


class GamepadManager:
    """Manages gamepads/controllers, event polling, and semantic mapping."""

    def __init__(
        self,
        on_button_down: Optional[Callable[[str, int], None]] = None,
        on_button_up: Optional[Callable[[str, int], None]] = None,
        on_controller_connected: Optional[Callable[[str], None]] = None,
        on_controller_disconnected: Optional[Callable[[str], None]] = None,
        vibration_enabled: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_button_down = on_button_down
        self.on_button_up = on_button_up
        self.on_controller_connected = on_controller_connected
        self.on_controller_disconnected = on_controller_disconnected
        self.vibration_enabled = vibration_enabled
        self.enabled = enabled

        self._controllers: Dict[int, Any] = {}
        self._initialized = False

        # Stick direction tracking for D-pad simulation and history navigation with pacing
        self._stick_state: Dict[str, bool] = {
            "dpad_up": False,
            "dpad_down": False,
            "dpad_left": False,
            "dpad_right": False,
            "right_stick_up": False,
            "right_stick_down": False,
            "right_stick_left": False,
            "right_stick_right": False,
        }
        self._stick_repeat_time: Dict[str, float] = {
            "dpad_up": 0.0,
            "dpad_down": 0.0,
            "dpad_left": 0.0,
            "dpad_right": 0.0,
            "right_stick_up": 0.0,
            "right_stick_down": 0.0,
            "right_stick_left": 0.0,
            "right_stick_right": 0.0,
        }

        # DualSense Touchpad gesture tracking state per controller ID
        self._touch_data: Dict[int, Dict[str, Any]] = {}

        # Trigger digital state tracking
        self._trigger_state: Dict[str, bool] = {
            "left_trigger": False,
            "right_trigger": False,
        }

        if PYGAME_CONTROLLER_AVAILABLE and self.enabled:
            self._init_sdl()

    def _init_sdl(self) -> None:
        """Initialize the SDL Controller subsystem and discover attached controllers."""
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            if not sdl_controller.get_init():
                sdl_controller.init()
            self._initialized = True
            logger.debug("GamepadManager initialized with SDL Controller subsystem.")

            # Attach any controllers that are already plugged in
            count = sdl_controller.get_count()
            for index in range(count):
                if sdl_controller.is_controller(index):
                    try:
                        c = sdl_controller.Controller(index)
                        c.init()
                        self._controllers[c.id] = c
                        logger.info("Found attached controller: %s (id=%s)", c.name, c.id)
                    except Exception as err:
                        logger.warning("Could not initialize controller %d: %s", index, err)
        except Exception as e:
            logger.warning("Failed to initialize SDL Controller subsystem: %s", e)
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Return True if the controller subsystem was successfully initialized."""
        return self._initialized

    @property
    def connected_count(self) -> int:
        """Return the number of currently connected controllers."""
        return len(self._controllers)

    def get_controller_names(self) -> List[str]:
        """Return a list of names for all connected controllers."""
        return [c.name for c in self._controllers.values() if hasattr(c, "name")]

    def poll(self) -> None:
        """Process pending SDL controller events. Non-blocking."""
        if not self._initialized or not self.enabled:
            return

        try:
            for event in pygame.event.get():
                self._handle_event(event)
        except Exception as e:
            logger.error("Error during GamepadManager.poll: %s", e)

        # Check stick directional repeats
        self._process_stick_repeats()

    def _handle_event(self, event: Any) -> None:
        event_type = getattr(event, "type", None)
        if event_type == pygame.CONTROLLERDEVICEADDED:
            device_index = getattr(event, "device_index", None)
            if device_index is not None and sdl_controller.is_controller(device_index):
                try:
                    c = sdl_controller.Controller(device_index)
                    c.init()
                    cid = c.id
                    self._controllers[cid] = c
                    logger.info("Controller connected: %s (id=%s)", c.name, cid)
                    if self.on_controller_connected:
                        self.on_controller_connected(c.name)
                except Exception as e:
                    logger.warning("Could not attach controller index %s: %s", device_index, e)

        elif event_type == pygame.CONTROLLERDEVICEREMOVED:
            instance_id = getattr(event, "instance_id", None)
            if instance_id is not None and instance_id in self._controllers:
                c = self._controllers.pop(instance_id)
                name = getattr(c, "name", "Controller")
                try:
                    c.quit()
                except Exception:
                    pass
                logger.info("Controller disconnected: %s (id=%s)", name, instance_id)
                if self.on_controller_disconnected:
                    self.on_controller_disconnected(name)

        elif event_type == pygame.CONTROLLERBUTTONDOWN:
            btn_id = getattr(event, "button", -1)
            cid = getattr(event, "instance_id", 0)
            btn_name = BUTTON_MAP.get(btn_id)
            if btn_name and self.on_button_down:
                self.on_button_down(btn_name, cid)

        elif event_type == pygame.CONTROLLERBUTTONUP:
            btn_id = getattr(event, "button", -1)
            cid = getattr(event, "instance_id", 0)
            btn_name = BUTTON_MAP.get(btn_id)
            if btn_name and self.on_button_up:
                self.on_button_up(btn_name, cid)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADDOWN", -999):
            self._handle_touch_down(event)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADMOTION", -999):
            self._handle_touch_motion(event)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADUP", -999):
            self._handle_touch_up(event)

        elif event_type == pygame.CONTROLLERAXISMOTION:
            axis = getattr(event, "axis", -1)
            val = getattr(event, "value", 0)
            cid = getattr(event, "instance_id", 0)
            self._handle_axis_motion(axis, val, cid)

    def _handle_touch_down(self, event: Any) -> None:
        """Handle finger touch down on touchpad."""
        finger = getattr(event, "finger", 0)
        if finger != 0:
            return
        cid = getattr(event, "instance_id", 0)
        x = float(getattr(event, "x", 0.0))
        y = float(getattr(event, "y", 0.0))
        now = time.monotonic()
        self._touch_data[cid] = {
            "start_x": x,
            "start_y": y,
            "last_x": x,
            "last_y": y,
            "start_time": now,
            "last_time": now,
            "swiped": False,
        }

    def _handle_touch_motion(self, event: Any) -> None:
        """Track finger motion on touchpad and detect directional swipes in real time."""
        finger = getattr(event, "finger", 0)
        if finger != 0:
            return
        cid = getattr(event, "instance_id", 0)
        td = self._touch_data.get(cid)
        if not td:
            return
        x = float(getattr(event, "x", td["last_x"]))
        y = float(getattr(event, "y", td["last_y"]))
        td["last_x"] = x
        td["last_y"] = y
        now = time.monotonic()
        td["last_time"] = now

        if td["swiped"]:
            return

        dx = x - td["start_x"]
        dy = y - td["start_y"]
        dt = now - td["start_time"]

        # Active swipe threshold (0.18 normalized distance, within 0.7s)
        if dt < 0.7:
            if abs(dy) >= 0.18 and abs(dy) >= abs(dx) * 1.3:
                td["swiped"] = True
                gesture = "touchpad_swipe_down" if dy > 0 else "touchpad_swipe_up"
                if self.on_button_down:
                    self.on_button_down(gesture, cid)
            elif abs(dx) >= 0.18 and abs(dx) >= abs(dy) * 1.3:
                td["swiped"] = True
                gesture = "touchpad_swipe_right" if dx > 0 else "touchpad_swipe_left"
                if self.on_button_down:
                    self.on_button_down(gesture, cid)

    def _handle_touch_up(self, event: Any) -> None:
        """Handle finger release on touchpad; recognize tap or flick swipe."""
        finger = getattr(event, "finger", 0)
        if finger != 0:
            return
        cid = getattr(event, "instance_id", 0)
        td = self._touch_data.pop(cid, None)
        if not td:
            return

        if not td["swiped"]:
            dx = td["last_x"] - td["start_x"]
            dy = td["last_y"] - td["start_y"]
            dt = time.monotonic() - td["start_time"]

            # Tap: short duration and minimal movement
            if dt < 0.35 and abs(dx) < 0.08 and abs(dy) < 0.08:
                if self.on_button_down:
                    self.on_button_down("touchpad_tap", cid)
            # Flick release swipe: quick flick released before motion threshold
            elif dt < 0.5:
                if abs(dy) >= 0.12 and abs(dy) >= abs(dx) * 1.2:
                    gesture = "touchpad_swipe_down" if dy > 0 else "touchpad_swipe_up"
                    if self.on_button_down:
                        self.on_button_down(gesture, cid)
                elif abs(dx) >= 0.12 and abs(dx) >= abs(dy) * 1.2:
                    gesture = "touchpad_swipe_right" if dx > 0 else "touchpad_swipe_left"
                    if self.on_button_down:
                        self.on_button_down(gesture, cid)

    def _handle_axis_motion(self, axis: int, value: int, controller_id: int) -> None:
        threshold = 16000

        # Left Stick Y (Up / Down)
        if axis == pygame.CONTROLLER_AXIS_LEFTY:
            up_pressed = value < -threshold
            down_pressed = value > threshold
            self._update_directional_stick("dpad_up", up_pressed, controller_id)
            self._update_directional_stick("dpad_down", down_pressed, controller_id)

        # Left Stick X (Left / Right)
        elif axis == pygame.CONTROLLER_AXIS_LEFTX:
            left_pressed = value < -threshold
            right_pressed = value > threshold
            self._update_directional_stick("dpad_left", left_pressed, controller_id)
            self._update_directional_stick("dpad_right", right_pressed, controller_id)

        # Right Stick Y (History: Older / Newer messages)
        elif axis == pygame.CONTROLLER_AXIS_RIGHTY:
            up_pressed = value < -threshold
            down_pressed = value > threshold
            self._update_directional_stick("right_stick_up", up_pressed, controller_id)
            self._update_directional_stick("right_stick_down", down_pressed, controller_id)

        # Right Stick X (History: Oldest / Newest messages)
        elif axis == pygame.CONTROLLER_AXIS_RIGHTX:
            left_pressed = value < -threshold
            right_pressed = value > threshold
            self._update_directional_stick("right_stick_left", left_pressed, controller_id)
            self._update_directional_stick("right_stick_right", right_pressed, controller_id)

        # Triggers (0 to 32767)
        elif axis == pygame.CONTROLLER_AXIS_TRIGGERLEFT:
            pressed = value > 16384
            if pressed != self._trigger_state["left_trigger"]:
                self._trigger_state["left_trigger"] = pressed
                if pressed and self.on_button_down:
                    self.on_button_down("left_trigger", controller_id)
                elif not pressed and self.on_button_up:
                    self.on_button_up("left_trigger", controller_id)

        elif axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT:
            pressed = value > 16384
            if pressed != self._trigger_state["right_trigger"]:
                self._trigger_state["right_trigger"] = pressed
                if pressed and self.on_button_down:
                    self.on_button_down("right_trigger", controller_id)
                elif not pressed and self.on_button_up:
                    self.on_button_up("right_trigger", controller_id)

    def _update_directional_stick(self, direction: str, pressed: bool, controller_id: int) -> None:
        now = time.monotonic()
        if pressed and not self._stick_state[direction]:
            # Initial tilt
            self._stick_state[direction] = True
            self._stick_repeat_time[direction] = now + 0.35  # 350ms delay before repeat
            if self.on_button_down:
                self.on_button_down(direction, controller_id)
        elif not pressed and self._stick_state[direction]:
            # Centered
            self._stick_state[direction] = False
            self._stick_repeat_time[direction] = 0.0
            if self.on_button_up:
                self.on_button_up(direction, controller_id)

    def _process_stick_repeats(self) -> None:
        now = time.monotonic()
        for direction, pressed in self._stick_state.items():
            if pressed and self._stick_repeat_time[direction] > 0.0 and now >= self._stick_repeat_time[direction]:
                self._stick_repeat_time[direction] = now + 0.18  # 180ms repeat pacing
                if self.on_button_down:
                    self.on_button_down(direction, 0)

    def rumble(self, low_frequency: float = 0.5, high_frequency: float = 0.5, duration_ms: int = 200) -> bool:
        """Trigger dual-motor vibration on all connected controllers."""
        if not self.vibration_enabled or not self.enabled or not self._controllers:
            return False

        clamped_low = max(0.0, min(1.0, float(low_frequency)))
        clamped_high = max(0.0, min(1.0, float(high_frequency)))
        clamped_duration = max(10, min(5000, int(duration_ms)))

        success = False
        for c in list(self._controllers.values()):
            try:
                res = c.rumble(clamped_low, clamped_high, clamped_duration)
                if not res and hasattr(c, "as_joystick"):
                    res = c.as_joystick().rumble(clamped_low, clamped_high, clamped_duration)
                if res:
                    success = True
            except Exception as e:
                logger.debug("Rumble error on controller %s: %s", getattr(c, "name", "unknown"), e)
        return success

    def shutdown(self) -> None:
        """Cleanly release all controllers and stop SDL controller subsystem."""
        for c in list(self._controllers.values()):
            try:
                c.quit()
            except Exception:
                pass
        self._controllers.clear()
        self._touch_data.clear()
        try:
            if PYGAME_CONTROLLER_AVAILABLE and sdl_controller and sdl_controller.get_init():
                sdl_controller.quit()
        except Exception:
            pass
        self._initialized = False
