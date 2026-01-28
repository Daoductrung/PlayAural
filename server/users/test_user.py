"""Test user implementation for unit and play tests."""

from dataclasses import dataclass
from typing import Any

from .base import User, MenuItem, EscapeBehavior, generate_uuid


@dataclass
class Message:
    """A captured message from the test user."""

    type: str
    data: dict[str, Any]


class MockUser(User):
    """
    Mock implementation of User that captures all messages for assertion.

    Used in unit tests and play tests to verify game behavior.
    """

    def __init__(self, username: str, locale: str = "en", uuid: str | None = None, approved: bool = True):
        self._uuid = uuid or generate_uuid()
        self._username = username
        self._locale = locale
        self._approved = approved
        self.messages: list[Message] = []
        self.menus: dict[str, dict[str, Any]] = {}
        self.editboxes: dict[str, dict[str, Any]] = {}

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def username(self) -> str:
        return self._username

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def approved(self) -> bool:
        return self._approved

    def speak(self, text: str, buffer: str = "misc") -> None:
        self.messages.append(Message("speak", {"text": text, "buffer": buffer}))

    def play_sound(
        self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100
    ) -> None:
        self.messages.append(
            Message(
                "play_sound",
                {"name": name, "volume": volume, "pan": pan, "pitch": pitch},
            )
        )

    def play_music(self, name: str, looping: bool = True) -> None:
        self.messages.append(Message("play_music", {"name": name, "looping": looping}))

    def stop_music(self) -> None:
        self.messages.append(Message("stop_music", {}))

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        self.messages.append(
            Message("play_ambience", {"loop": loop, "intro": intro, "outro": outro})
        )

    def stop_ambience(self) -> None:
        self.messages.append(Message("stop_ambience", {}))

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
        menu_data = {
            "items": items,
            "multiletter": multiletter,
            "escape_behavior": escape_behavior,
            "position": position,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
        }
        self.menus[menu_id] = menu_data
        self.messages.append(Message("show_menu", {"menu_id": menu_id, **menu_data}))

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
    ) -> None:
        if menu_id in self.menus:
            self.menus[menu_id]["items"] = items
            if position is not None:
                self.menus[menu_id]["position"] = position
        self.messages.append(
            Message(
                "update_menu",
                {
                    "menu_id": menu_id,
                    "items": items,
                    "position": position,
                    "selection_id": selection_id,
                },
            )
        )

    def remove_menu(self, menu_id: str) -> None:
        self.menus.pop(menu_id, None)
        self.messages.append(Message("remove_menu", {"menu_id": menu_id}))

    def show_editbox(
        self,
        input_id: str,
        prompt: str,
        default_value: str = "",
        *,
        multiline: bool = False,
        read_only: bool = False,
    ) -> None:
        editbox_data = {
            "prompt": prompt,
            "default_value": default_value,
            "multiline": multiline,
            "read_only": read_only,
        }
        self.editboxes[input_id] = editbox_data
        self.messages.append(
            Message("show_editbox", {"input_id": input_id, **editbox_data})
        )

    def remove_editbox(self, input_id: str) -> None:
        self.editboxes.pop(input_id, None)
        self.messages.append(Message("remove_editbox", {"input_id": input_id}))

    def clear_ui(self) -> None:
        self.menus.clear()
        self.editboxes.clear()
        self.messages.append(Message("clear_ui", {}))

    # Test helper methods

    def get_spoken_messages(self) -> list[str]:
        """Get all spoken text messages."""
        return [m.data["text"] for m in self.messages if m.type == "speak"]

    def get_last_spoken(self) -> str | None:
        """Get the most recent spoken message."""
        for m in reversed(self.messages):
            if m.type == "speak":
                return m.data["text"]
        return None

    def get_sounds_played(self) -> list[str]:
        """Get all sound effect names played."""
        return [m.data["name"] for m in self.messages if m.type == "play_sound"]

    def get_current_menu_items(self, menu_id: str) -> list[str | MenuItem] | None:
        """Get the current items for a menu."""
        if menu_id in self.menus:
            return self.menus[menu_id]["items"]
        return None

    def clear_messages(self) -> None:
        """Clear the message history (but not current UI state)."""
        self.messages.clear()
