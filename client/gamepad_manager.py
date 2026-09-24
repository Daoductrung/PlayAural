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
    15: "misc1",         # Mic mute on DualSense / Share on Xbox (SDL_CONTROLLER_BUTTON_MISC1)
    16: "paddle1",       # Elite / Pro controller paddle 1
    17: "paddle2",       # Elite / Pro controller paddle 2
    18: "paddle3",       # Elite / Pro controller paddle 3
    19: "paddle4",       # Elite / Pro controller paddle 4
    20: "touchpad",      # PS4 / PS5 touchpad click (SDL_CONTROLLER_BUTTON_TOUCHPAD)
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
        vibration_strength: int = 100,
        preferred_controller_id: str = "",
        enabled: bool = True,
    ) -> None:
        self.on_button_down = on_button_down
        self.on_button_up = on_button_up
        self.on_controller_connected = on_controller_connected
        self.on_controller_disconnected = on_controller_disconnected
        self.vibration_enabled = vibration_enabled
        self.vibration_strength: int = vibration_strength
        self.preferred_controller_id: str = str(preferred_controller_id or "")
        self.enabled = enabled

        self._controllers: Dict[int, Any] = {}
        self._instance_to_stable_id: Dict[int, str] = {}
        self._stable_to_instance_id: Dict[str, int] = {}
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
            self._rebuild_device_identities()
        except Exception as e:
            logger.warning("Failed to initialize SDL Controller subsystem: %s", e)
            self._initialized = False

    @staticmethod
    def _get_controller_guid(controller: Any) -> str:
        """Extract a stable hardware GUID string from a controller object."""
        try:
            if hasattr(controller, "as_joystick"):
                joy = controller.as_joystick()
                if hasattr(joy, "get_guid"):
                    guid = joy.get_guid()
                    if guid:
                        return str(guid).strip()
        except Exception:
            pass
        name = getattr(controller, "name", "")
        if name:
            return f"name:{str(name).strip()}"
        return f"controller:{getattr(controller, 'id', 0)}"

    def _rebuild_device_identities(self) -> None:
        """Rebuild mapping between SDL runtime instance IDs and stable persistent device IDs."""
        self._instance_to_stable_id.clear()
        self._stable_to_instance_id.clear()
        guid_counts: Dict[str, int] = {}

        for cid in sorted(self._controllers.keys()):
            c = self._controllers[cid]
            guid = self._get_controller_guid(c)
            guid_counts[guid] = guid_counts.get(guid, 0) + 1
            occ = guid_counts[guid]
            stable_id = f"{guid}#{occ}" if occ > 1 else guid
            self._instance_to_stable_id[cid] = stable_id
            self._stable_to_instance_id[stable_id] = cid
            if occ == 1:
                self._stable_to_instance_id[f"{guid}#1"] = cid

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

    def get_controller_info_list(self) -> List[Dict[str, str]]:
        """Return a list of dicts with stable id and name for all connected controllers."""
        self._rebuild_device_identities()
        name_counts: Dict[str, int] = {}
        total_names: Dict[str, int] = {}
        for cid in sorted(self._controllers.keys()):
            c = self._controllers[cid]
            base_name = getattr(c, "name", f"Controller {cid}")
            total_names[base_name] = total_names.get(base_name, 0) + 1

        res = []
        for cid in sorted(self._controllers.keys()):
            c = self._controllers[cid]
            base_name = getattr(c, "name", f"Controller {cid}")
            stable_id = self._instance_to_stable_id.get(cid, str(cid))
            if total_names.get(base_name, 0) > 1:
                name_counts[base_name] = name_counts.get(base_name, 0) + 1
                display_name = f"{base_name} ({name_counts[base_name]})"
            else:
                display_name = base_name
            res.append({"id": stable_id, "name": display_name})
        return res

    def _is_controller_active(self, cid: int) -> bool:
        """Check if controller with instance_id cid is accepted based on preferred_controller_id."""
        pref = str(self.preferred_controller_id or "").strip()
        if not pref:
            return True
        stable_id = self._instance_to_stable_id.get(cid)
        if not stable_id:
            self._rebuild_device_identities()
            stable_id = self._instance_to_stable_id.get(cid)
        if stable_id and (
            stable_id == pref
            or pref == f"{stable_id}#1"
            or stable_id == f"{pref}#1"
        ):
            return True
        # Backward compatibility fallback if preferred_controller_id was a raw instance ID
        return str(cid) == pref

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
                    self._rebuild_device_identities()
                    logger.info("Controller connected: %s (id=%s)", c.name, cid)
                    if self.on_controller_connected:
                        self.on_controller_connected(c.name)
                except Exception as e:
                    logger.warning("Could not attach controller index %s: %s", device_index, e)

        elif event_type == pygame.CONTROLLERDEVICEREMOVED:
            instance_id = getattr(event, "instance_id", None)
            if instance_id is not None and instance_id in self._controllers:
                c = self._controllers.pop(instance_id)
                self._rebuild_device_identities()
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
            if self._is_controller_active(cid):
                btn_name = BUTTON_MAP.get(btn_id)
                if btn_name and self.on_button_down:
                    self.on_button_down(btn_name, cid)

        elif event_type == pygame.CONTROLLERBUTTONUP:
            btn_id = getattr(event, "button", -1)
            cid = getattr(event, "instance_id", 0)
            if self._is_controller_active(cid):
                btn_name = BUTTON_MAP.get(btn_id)
                if btn_name and self.on_button_up:
                    self.on_button_up(btn_name, cid)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADDOWN", -999):
            cid = getattr(event, "instance_id", 0)
            if self._is_controller_active(cid):
                self._handle_touch_down(event)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADMOTION", -999):
            cid = getattr(event, "instance_id", 0)
            if self._is_controller_active(cid):
                self._handle_touch_motion(event)

        elif event_type == getattr(pygame, "CONTROLLERTOUCHPADUP", -999):
            cid = getattr(event, "instance_id", 0)
            if self._is_controller_active(cid):
                self._handle_touch_up(event)

        elif event_type == pygame.CONTROLLERAXISMOTION:
            axis = getattr(event, "axis", -1)
            val = getattr(event, "value", 0)
            cid = getattr(event, "instance_id", 0)
            if self._is_controller_active(cid):
                self._handle_axis_motion(axis, val, cid)

    def _handle_touch_down(self, event: Any) -> None:
        """Handle finger touch down on touchpad, supporting single and multi-touch gestures."""
        cid = getattr(event, "instance_id", 0)
        finger = getattr(event, "finger", 0)
        x = float(getattr(event, "x", 0.0))
        y = float(getattr(event, "y", 0.0))
        now = time.monotonic()

        td = self._touch_data.get(cid)
        if not td or not td.get("fingers") or finger == 0:
            td = {
                "fingers": {},
                "start_time": now,
                "max_fingers": 1,
                "swiped": False,
                "last_dx": 0.0,
                "last_dy": 0.0,
            }
            self._touch_data[cid] = td

        td["fingers"][finger] = {
            "start_x": x,
            "start_y": y,
            "last_x": x,
            "last_y": y,
            "time": now,
        }
        num_fingers = len(td["fingers"])
        if num_fingers > td["max_fingers"]:
            td["max_fingers"] = num_fingers

    def _handle_touch_motion(self, event: Any) -> None:
        """Track finger motion on touchpad and detect directional swipes in real time."""
        cid = getattr(event, "instance_id", 0)
        finger = getattr(event, "finger", 0)
        td = self._touch_data.get(cid)
        if not td or not td.get("fingers"):
            return

        x = float(getattr(event, "x", 0.0))
        y = float(getattr(event, "y", 0.0))
        now = time.monotonic()

        f_data = td["fingers"].get(finger)
        if f_data:
            f_data["last_x"] = x
            f_data["last_y"] = y
            f_data["time"] = now
        else:
            td["fingers"][finger] = {
                "start_x": x,
                "start_y": y,
                "last_x": x,
                "last_y": y,
                "time": now,
            }
            num_fingers = len(td["fingers"])
            if num_fingers > td["max_fingers"]:
                td["max_fingers"] = num_fingers

        if td["swiped"]:
            return

        dt = now - td["start_time"]
        if dt > 0.7:
            return

        # Determine reference finger (finger 0 if present, else first active finger)
        primary = td["fingers"].get(0)
        if not primary:
            primary = next(iter(td["fingers"].values()))

        dx = primary["last_x"] - primary["start_x"]
        dy = primary["last_y"] - primary["start_y"]
        td["last_dx"] = dx
        td["last_dy"] = dy

        is_two_finger = td["max_fingers"] >= 2 or len(td["fingers"]) >= 2
        prefix = "touchpad_2finger_swipe_" if is_two_finger else "touchpad_swipe_"
        threshold = 0.15 if is_two_finger else 0.18
        ratio = 1.2 if is_two_finger else 1.3

        if abs(dy) >= threshold and abs(dy) >= abs(dx) * ratio:
            td["swiped"] = True
            gesture = f"{prefix}down" if dy > 0 else f"{prefix}up"
            if self.on_button_down:
                self.on_button_down(gesture, cid)
        elif abs(dx) >= threshold and abs(dx) >= abs(dy) * ratio:
            td["swiped"] = True
            gesture = f"{prefix}right" if dx > 0 else f"{prefix}left"
            if self.on_button_down:
                self.on_button_down(gesture, cid)

    def _handle_touch_up(self, event: Any) -> None:
        """Handle finger release on touchpad; recognize tap or flick swipe."""
        cid = getattr(event, "instance_id", 0)
        finger = getattr(event, "finger", 0)
        td = self._touch_data.get(cid)
        if not td:
            return

        f_data = td.get("fingers", {}).pop(finger, None)
        if f_data:
            td["last_dx"] = f_data["last_x"] - f_data["start_x"]
            td["last_dy"] = f_data["last_y"] - f_data["start_y"]

        # Wait until all fingers are lifted before finishing touch contact
        if td.get("fingers"):
            return

        self._touch_data.pop(cid, None)

        if not td["swiped"]:
            dx = td["last_dx"]
            dy = td["last_dy"]
            dt = time.monotonic() - td["start_time"]
            is_two_finger = td["max_fingers"] >= 2

            if not is_two_finger:
                # Tap: short duration and minimal movement
                if dt < 0.35 and abs(dx) < 0.08 and abs(dy) < 0.08:
                    if self.on_button_down:
                        self.on_button_down("touchpad_tap", cid)
                    return

            prefix = "touchpad_2finger_swipe_" if is_two_finger else "touchpad_swipe_"
            # Flick release swipe: quick flick released before motion threshold
            if dt < 0.5:
                if abs(dy) >= 0.12 and abs(dy) >= abs(dx) * 1.2:
                    gesture = f"{prefix}down" if dy > 0 else f"{prefix}up"
                    if self.on_button_down:
                        self.on_button_down(gesture, cid)
                elif abs(dx) >= 0.12 and abs(dx) >= abs(dy) * 1.2:
                    gesture = f"{prefix}right" if dx > 0 else f"{prefix}left"
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
            if not direction.startswith("dpad_"):
                continue
            if pressed and self._stick_repeat_time[direction] > 0.0 and now >= self._stick_repeat_time[direction]:
                self._stick_repeat_time[direction] = now + 0.18  # 180ms repeat pacing
                if self.on_button_down:
                    self.on_button_down(direction, 0)

    def rumble(self, low_frequency: float = 0.5, high_frequency: float = 0.5, duration_ms: int = 200) -> bool:
        """Trigger dual-motor vibration on controllers with strength scaling."""
        if not self.vibration_enabled or not self.enabled or not self._controllers:
            return False

        mult = max(0.0, min(1.0, float(getattr(self, "vibration_strength", 100)) / 100.0))
        clamped_low = max(0.0, min(1.0, float(low_frequency) * mult))
        clamped_high = max(0.0, min(1.0, float(high_frequency) * mult))
        clamped_duration = max(10, min(5000, int(duration_ms)))

        target_controllers = []
        pref_id = str(getattr(self, "preferred_controller_id", "") or "").strip()
        if pref_id:
            target_cid = self._stable_to_instance_id.get(pref_id)
            if target_cid is None:
                self._rebuild_device_identities()
                target_cid = self._stable_to_instance_id.get(pref_id)
            if target_cid is not None and target_cid in self._controllers:
                target_controllers = [self._controllers[target_cid]]
            else:
                try:
                    int_cid = int(pref_id)
                    if int_cid in self._controllers:
                        target_controllers = [self._controllers[int_cid]]
                except (ValueError, TypeError):
                    pass

        if not target_controllers:
            target_controllers = list(self._controllers.values())

        success = False
        for c in target_controllers:
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
        self._instance_to_stable_id.clear()
        self._stable_to_instance_id.clear()
        self._touch_data.clear()
        try:
            if PYGAME_CONTROLLER_AVAILABLE and sdl_controller and sdl_controller.get_init():
                sdl_controller.quit()
        except Exception:
            pass
        self._initialized = False
