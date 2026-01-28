"""Protocol definitions for client-server communication."""

from enum import Enum
from dataclasses import dataclass
from typing import Any


class PacketType(Enum):
    """Types of packets in the protocol."""

    # Client to server
    AUTHORIZE = "authorize"
    MENU = "menu"
    KEYBIND = "keybind"
    ESCAPE = "escape"
    EDITBOX = "editbox"
    CHAT = "chat"

    # Server to client
    AUTHORIZE_SUCCESS = "authorize_success"
    SPEAK = "speak"
    PLAY_SOUND = "play_sound"
    PLAY_MUSIC = "play_music"
    STOP_MUSIC = "stop_music"
    PLAY_AMBIENCE = "play_ambience"
    STOP_AMBIENCE = "stop_ambience"
    MENU_RESPONSE = "menu"
    REQUEST_INPUT = "request_input"
    CLEAR_UI = "clear_ui"
    DISCONNECT = "disconnect"
    TABLE_CREATE = "table_create"
    UPDATE_OPTIONS_LISTS = "update_options_lists"


@dataclass
class Packet:
    """A network packet."""

    type: str
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, d: dict) -> "Packet":
        """Create a packet from a dictionary."""
        packet_type = d.get("type", "unknown")
        return cls(type=packet_type, data=d)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.data
