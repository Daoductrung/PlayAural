"""Network user implementation for real players."""

from typing import Any, TYPE_CHECKING

from .base import User, MenuItem, EscapeBehavior, generate_uuid
from .preferences import UserPreferences

if TYPE_CHECKING:
    from ..network.websocket_server import ClientConnection


class NetworkUser(User):
    """
    Network implementation of User for real players connected via websocket.

    Queues messages to be sent asynchronously by the network layer.
    """

    def __init__(
        self,
        username: str,
        locale: str,
        connection: "ClientConnection",
        uuid: str | None = None,
        preferences: UserPreferences | None = None,
        trust_level: int = 1,
        approved: bool = False,
    ):
        self._uuid = uuid or generate_uuid()
        self._username = username
        self._locale = locale
        self._connection = connection
        self._preferences = preferences or UserPreferences()
        self._trust_level = trust_level
        self._approved = approved
        self._message_queue: list[dict[str, Any]] = []

        # Track current UI state for session resumption
        self._current_menus: dict[str, dict[str, Any]] = {}
        self._current_editboxes: dict[str, dict[str, Any]] = {}
        self._current_music: dict[str, Any] | None = None

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def username(self) -> str:
        return self._username

    @property
    def locale(self) -> str:
        return self._locale

    def set_locale(self, locale: str) -> None:
        """Set the user's locale."""
        self._locale = locale

    @property
    def trust_level(self) -> int:
        return self._trust_level

    @property
    def approved(self) -> bool:
        return self._approved

    def set_approved(self, approved: bool) -> None:
        """Set the user's approval status."""
        self._approved = approved

    def set_trust_level(self, trust_level: int) -> None:
        """Set the user's trust level."""
        self._trust_level = trust_level

    @property
    def preferences(self) -> UserPreferences:
        return self._preferences

    def set_preferences(self, preferences: UserPreferences) -> None:
        """Set the user's preferences."""
        self._preferences = preferences

    @property
    def connection(self) -> "ClientConnection":
        return self._connection

    def _queue_packet(self, packet: dict[str, Any]) -> None:
        """Queue a packet to be sent to the client."""
        self._message_queue.append(packet)

    def get_queued_messages(self) -> list[dict[str, Any]]:
        """Get and clear the message queue."""
        messages = self._message_queue
        self._message_queue = []
        return messages

    def speak(self, text: str, buffer: str = "misc") -> None:
        packet = {"type": "speak", "text": text}
        if buffer != "misc":
            packet["buffer"] = buffer
        self._queue_packet(packet)

    def play_sound(
        self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100
    ) -> None:
        self._queue_packet(
            {
                "type": "play_sound",
                "name": name,
                "volume": volume,
                "pan": pan,
                "pitch": pitch,
            }
        )

    def play_music(self, name: str, looping: bool = True) -> None:
        self._current_music = {"name": name, "looping": looping}
        self._queue_packet(
            {
                "type": "play_music",
                "name": name,
                "looping": looping,
            }
        )

    def stop_music(self) -> None:
        self._current_music = None
        self._queue_packet({"type": "stop_music"})

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        self._queue_packet(
            {
                "type": "play_ambience",
                "intro": intro,
                "loop": loop,
                "outro": outro,
            }
        )

    def stop_ambience(self) -> None:
        self._queue_packet({"type": "stop_ambience"})

    def _convert_items(self, items: list[str | MenuItem]) -> list[str | dict]:
        """Convert MenuItem objects to dicts for JSON serialization."""
        result = []
        for item in items:
            if isinstance(item, MenuItem):
                result.append(item.to_dict())
            else:
                result.append(item)
        return result

    def show_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        *,
        multiletter: bool = True,
        escape_behavior: EscapeBehavior = EscapeBehavior.KEYBIND,
        position: int | None = None,
        grid_enabled: bool = False,
        grid_width: int = 1,
    ) -> None:
        converted_items = self._convert_items(items)
        escape_str = escape_behavior.value

        # Store for session resumption
        self._current_menus[menu_id] = {
            "items": converted_items,
            "multiletter_enabled": multiletter,
            "escape_behavior": escape_str,
            "position": position,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
        }

        packet: dict[str, Any] = {
            "type": "menu",
            "menu_id": menu_id,
            "items": converted_items,
            "multiletter_enabled": multiletter,
            "escape_behavior": escape_str,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
        }
        if position is not None:
            # Convert 1-based to 0-based for client
            packet["position"] = position - 1
        self._queue_packet(packet)

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
    ) -> None:
        converted_items = self._convert_items(items)

        if menu_id in self._current_menus:
            self._current_menus[menu_id]["items"] = converted_items
            if position is not None:
                self._current_menus[menu_id]["position"] = position

        packet: dict[str, Any] = {
            "type": "menu",
            "menu_id": menu_id,
            "items": converted_items,
        }
        if position is not None:
            packet["position"] = position - 1
        if selection_id is not None:
            packet["selection_id"] = selection_id
        self._queue_packet(packet)

    def remove_menu(self, menu_id: str) -> None:
        self._current_menus.pop(menu_id, None)
        # Send empty menu to clear it
        self._queue_packet(
            {
                "type": "menu",
                "menu_id": menu_id,
                "items": [],
            }
        )

    def show_editbox(
        self,
        input_id: str,
        prompt: str,
        default_value: str = "",
        *,
        multiline: bool = False,
        read_only: bool = False,
    ) -> None:
        self._current_editboxes[input_id] = {
            "prompt": prompt,
            "default_value": default_value,
            "multiline": multiline,
            "read_only": read_only,
        }
        self._queue_packet(
            {
                "type": "request_input",
                "input_id": input_id,
                "prompt": prompt,
                "default_value": default_value,
                "multiline": multiline,
                "read_only": read_only,
            }
        )

    def remove_editbox(self, input_id: str) -> None:
        self._current_editboxes.pop(input_id, None)
        # There's no explicit remove_editbox packet, showing a menu will replace it

    def clear_ui(self) -> None:
        self._current_menus.clear()
        self._current_editboxes.clear()
        self._queue_packet({"type": "clear_ui"})
