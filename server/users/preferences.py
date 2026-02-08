"""User preferences for PlayAural."""

from dataclasses import dataclass, field
from enum import Enum


class DiceKeepingStyle(Enum):
    """Dice keeping style preference."""

    PlayAural = "PlayAural"  # Dice indexes (1-5 keys)
    QUENTIN_C = "quentin_c"  # Dice values (1-6 keys)

    @classmethod
    def from_str(cls, value: str) -> "DiceKeepingStyle":
        """Convert string to enum, defaulting to PlayAural."""
        try:
            return cls(value)
        except ValueError:
            return cls.PlayAural


@dataclass
class UserPreferences:
    """User preferences that persist across sessions."""

    # Sound preferences
    play_turn_sound: bool = True  # Play sound when it's your turn

    # Audio preferences
    music_volume: int = 20
    ambience_volume: int = 20

    # Speech preferences (Web only)
    speech_mode: str = "aria"  # "aria" or "web_speech"
    speech_rate: int = 100
    speech_voice: str = ""  # Voice URI

    # Social preferences
    mute_global_chat: bool = False
    mute_table_chat: bool = False
    notify_table_created: bool = True  # Notify when a new table is created

    # Interface preferences
    invert_multiline_enter_behavior: bool = False
    play_typing_sounds: bool = True

    # Dice game preferences
    clear_kept_on_roll: bool = False  # Clear kept dice after rolling
    dice_keeping_style: DiceKeepingStyle = field(
        default_factory=lambda: DiceKeepingStyle.PlayAural
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "play_turn_sound": self.play_turn_sound,
            "music_volume": self.music_volume,
            "ambience_volume": self.ambience_volume,
            "speech_mode": self.speech_mode,
            "speech_rate": self.speech_rate,
            "speech_voice": self.speech_voice,
            "mute_global_chat": self.mute_global_chat,
            "mute_table_chat": self.mute_table_chat,
            "notify_table_created": self.notify_table_created,
            "invert_multiline_enter_behavior": self.invert_multiline_enter_behavior,
            "play_typing_sounds": self.play_typing_sounds,
            "clear_kept_on_roll": self.clear_kept_on_roll,
            "dice_keeping_style": self.dice_keeping_style.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create from dictionary."""
        return cls(
            play_turn_sound=data.get("play_turn_sound", True),
            music_volume=data.get("music_volume", 20),
            ambience_volume=data.get("ambience_volume", 20),
            speech_mode=data.get("speech_mode", "aria"),
            speech_rate=data.get("speech_rate", 100),
            speech_voice=data.get("speech_voice", ""),
            mute_global_chat=data.get("mute_global_chat", False),
            mute_table_chat=data.get("mute_table_chat", False),
            notify_table_created=data.get("notify_table_created", True),
            invert_multiline_enter_behavior=data.get("invert_multiline_enter_behavior", False),
            play_typing_sounds=data.get("play_typing_sounds", True),
            clear_kept_on_roll=data.get("clear_kept_on_roll", False),
            dice_keeping_style=DiceKeepingStyle.from_str(
                data.get("dice_keeping_style", "PlayAural")
            ),
        )
