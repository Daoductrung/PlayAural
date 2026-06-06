"""User preferences for PlayAural."""

from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any


class DiceKeepingStyle(Enum):
    """Dice keeping style preference."""

    INDEX_BASED = "index_based"  # Dice indexes (1-5 keys)
    VALUE_BASED = "value_based"  # Dice values (1-6 keys)

    @classmethod
    def from_str(cls, value: str) -> "DiceKeepingStyle":
        """Convert string to enum, defaulting to INDEX_BASED."""
        try:
            return cls(value)
        except ValueError:
            return cls.INDEX_BASED


@dataclass
class PrefMeta:
    """Metadata describing a declarative (game) preference.

    Drives the Game Options menu: ``label``/``description`` are Fluent keys,
    ``kind`` is "bool" or "menu", ``choices`` are (value, fluent_key) pairs for
    menu prefs, and ``sync_key`` is the existing client preference-sync key so
    web/mobile keep receiving the same updates.
    """

    category: str
    label: str  # Fluent key; receives $status (bool) or $choice (menu)
    change_msg: str  # Fluent key for the change announcement
    description: str = ""  # Fluent key spoken on space
    kind: str = "bool"  # "bool" or "menu"
    default: Any = None
    choices: list[tuple[str, str]] | None = None  # (value, fluent_key)
    enum_class: type[Enum] | None = None
    sync_key: str = ""  # client sync key, e.g. "gameplay/play_turn_sound"


def pref_field(meta: PrefMeta) -> Any:
    """Create a dataclass field carrying PrefMeta (a declarative game pref)."""
    return field(default=meta.default, metadata={"pref_meta": meta})


# Declarative game-preference categories, in Game Options menu order.
PREF_CATEGORIES: list[tuple[str, str]] = [
    ("display", "pref-category-display"),
    ("sounds", "pref-category-sounds"),
    ("gameplay", "pref-category-gameplay"),
    ("dice", "pref-category-dice"),
]


@dataclass
class UserPreferences:
    """User preferences that persist across sessions."""

    # Display preferences (declarative -> Game Options)
    brief_announcements: bool = pref_field(
        PrefMeta(
            category="display",
            label="pref-set-brief-announcements",
            change_msg="pref-changed-brief-announcements",
            description="pref-desc-brief-announcements",
            kind="bool",
            default=False,
        )
    )

    # Sound preferences (declarative -> Game Options)
    play_turn_sound: bool = pref_field(
        PrefMeta(
            category="sounds",
            label="pref-set-play-turn-sound",
            change_msg="pref-changed-play-turn-sound",
            description="pref-desc-play-turn-sound",
            kind="bool",
            default=True,
            sync_key="gameplay/play_turn_sound",
        )
    )

    # Audio preferences
    music_volume: int = 10
    ambience_volume: int = 20
    voice_volume: int = 80  # 10-100 range (not 0 to avoid complete muting)
    desktop_audio_input_device_id: str = ""
    desktop_audio_input_device_name: str = ""

    # Web speech preferences
    speech_mode: str = "aria"  # "aria" or "web_speech"
    speech_rate: int = 100
    speech_voice: str = ""  # Voice URI

    # Mobile speech preferences
    mobile_tts_engine: str = "system"
    mobile_tts_rate: int = 100
    mobile_tts_voice: str = ""  # Expo Speech voice identifier

    # Social preferences
    mute_global_chat: bool = False
    mute_table_chat: bool = False
    notify_table_created: bool = True  # Notify when a new table is created
    notify_user_presence: bool = False # Notify when normal users connect/disconnect
    notify_friend_presence: bool = True # Notify when accepted friends connect/disconnect

    # Interface preferences
    invert_multiline_enter_behavior: bool = False
    play_typing_sounds: bool = True
    active_tables_filter: str = "all"  # "all", "waiting", "playing"
    game_category_filter: str = "all"  # "all" or a game category id

    # Gameplay preferences (declarative -> Game Options)
    allow_custom_bot_names: bool = pref_field(
        PrefMeta(
            category="gameplay",
            label="pref-set-allow-custom-bot-names",
            change_msg="pref-changed-allow-custom-bot-names",
            description="pref-desc-allow-custom-bot-names",
            kind="bool",
            default=False,
            sync_key="gameplay/allow_custom_bot_names",
        )
    )
    confirm_destructive_actions: bool = pref_field(
        PrefMeta(
            category="gameplay",
            label="pref-set-confirm-destructive-actions",
            change_msg="pref-changed-confirm-destructive-actions",
            description="pref-desc-confirm-destructive-actions",
            kind="bool",
            default=True,
            sync_key="gameplay/confirm_destructive_actions",
        )
    )

    # Dice game preferences (declarative -> Game Options)
    clear_kept_on_roll: bool = pref_field(
        PrefMeta(
            category="dice",
            label="pref-set-clear-kept-on-roll",
            change_msg="pref-changed-clear-kept-on-roll",
            description="pref-desc-clear-kept-on-roll",
            kind="bool",
            default=False,
            sync_key="dice/clear_kept_on_roll",
        )
    )
    dice_keeping_style: DiceKeepingStyle = pref_field(
        PrefMeta(
            category="dice",
            label="pref-set-dice-keeping-style",
            change_msg="pref-changed-dice-keeping-style",
            description="pref-desc-dice-keeping-style",
            kind="menu",
            default=DiceKeepingStyle.INDEX_BASED,
            choices=[
                ("index_based", "dice-keeping-style-indexes"),
                ("value_based", "dice-keeping-style-values"),
            ],
            enum_class=DiceKeepingStyle,
            sync_key="dice/dice_keeping_style",
        )
    )

    # Per-game overrides: {game_type: {field_name: value}}. A game may override
    # any preference declared in its relevant_preferences; get_effective() reads
    # the override when present, otherwise the global value.
    game_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "brief_announcements": self.brief_announcements,
            "play_turn_sound": self.play_turn_sound,
            "music_volume": self.music_volume,
            "ambience_volume": self.ambience_volume,
            "voice_volume": self.voice_volume,
            "desktop_audio_input_device_id": self.desktop_audio_input_device_id,
            "desktop_audio_input_device_name": self.desktop_audio_input_device_name,
            "speech_mode": self.speech_mode,
            "speech_rate": self.speech_rate,
            "speech_voice": self.speech_voice,
            "mobile_tts_engine": self.mobile_tts_engine,
            "mobile_tts_rate": self.mobile_tts_rate,
            "mobile_tts_voice": self.mobile_tts_voice,
            "mute_global_chat": self.mute_global_chat,
            "mute_table_chat": self.mute_table_chat,
            "notify_table_created": self.notify_table_created,
            "notify_user_presence": self.notify_user_presence,
            "notify_friend_presence": self.notify_friend_presence,
            "invert_multiline_enter_behavior": self.invert_multiline_enter_behavior,
            "play_typing_sounds": self.play_typing_sounds,
            "active_tables_filter": self.active_tables_filter,
            "game_category_filter": self.game_category_filter,
            "allow_custom_bot_names": self.allow_custom_bot_names,
            "confirm_destructive_actions": self.confirm_destructive_actions,
            "clear_kept_on_roll": self.clear_kept_on_roll,
            "dice_keeping_style": self.dice_keeping_style.value,
            "game_overrides": self.game_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create from dictionary."""
        return cls(
            brief_announcements=data.get("brief_announcements", False),
            play_turn_sound=data.get("play_turn_sound", True),
            music_volume=data.get("music_volume", 10),
            ambience_volume=data.get("ambience_volume", 20),
            voice_volume=data.get("voice_volume", 80),
            desktop_audio_input_device_id=data.get("desktop_audio_input_device_id", ""),
            desktop_audio_input_device_name=data.get(
                "desktop_audio_input_device_name", ""
            ),
            speech_mode=data.get("speech_mode", "aria"),
            speech_rate=data.get("speech_rate", 100),
            speech_voice=data.get("speech_voice", ""),
            mobile_tts_engine=data.get("mobile_tts_engine", "system"),
            mobile_tts_rate=data.get("mobile_tts_rate", 100),
            mobile_tts_voice=data.get("mobile_tts_voice", ""),
            mute_global_chat=data.get("mute_global_chat", False),
            mute_table_chat=data.get("mute_table_chat", False),
            notify_table_created=data.get("notify_table_created", True),
            notify_user_presence=data.get("notify_user_presence", False),
            notify_friend_presence=data.get("notify_friend_presence", True),
            invert_multiline_enter_behavior=data.get("invert_multiline_enter_behavior", False),
            play_typing_sounds=data.get("play_typing_sounds", True),
            active_tables_filter=data.get("active_tables_filter", "all"),
            game_category_filter=data.get("game_category_filter", "all"),
            allow_custom_bot_names=data.get("allow_custom_bot_names", False),
            confirm_destructive_actions=data.get("confirm_destructive_actions", True),
            clear_kept_on_roll=data.get("clear_kept_on_roll", False),
            dice_keeping_style=DiceKeepingStyle.from_str(
                data.get("dice_keeping_style", "index_based")
            ),
            game_overrides=data.get("game_overrides", {}) or {},
        )

    # ------------------------------------------------------------------
    # Declarative pref introspection (Game Options menu)
    # ------------------------------------------------------------------

    @classmethod
    def get_pref_fields(cls) -> list[tuple[str, PrefMeta]]:
        """Return (field_name, PrefMeta) for every declarative pref, in order."""
        result: list[tuple[str, PrefMeta]] = []
        for f in fields(cls):
            meta = f.metadata.get("pref_meta")
            if meta is not None:
                result.append((f.name, meta))
        return result

    @classmethod
    def get_fields_for_category(cls, category: str) -> list[tuple[str, PrefMeta]]:
        """Return declarative prefs in a category, in definition order."""
        return [(n, m) for n, m in cls.get_pref_fields() if m.category == category]

    @classmethod
    def get_pref_meta(cls, field_name: str) -> "PrefMeta | None":
        """Return the PrefMeta for a declarative pref field, if any."""
        for f in fields(cls):
            if f.name == field_name:
                return f.metadata.get("pref_meta")
        return None

    def _clear_overrides_for(self, field_name: str) -> None:
        """Drop every per-game override of a given field."""
        for game_type in list(self.game_overrides):
            self.game_overrides[game_type].pop(field_name, None)
            if not self.game_overrides[game_type]:
                del self.game_overrides[game_type]

    def reset_category(self, category: str) -> None:
        """Reset declarative prefs in a category to defaults + clear overrides."""
        for name, meta in self.get_fields_for_category(category):
            setattr(self, name, meta.default)
            self._clear_overrides_for(name)

    def reset_all_game_prefs(self) -> None:
        """Reset all declarative (game) prefs to defaults + clear their overrides."""
        for name, meta in self.get_pref_fields():
            setattr(self, name, meta.default)
            self._clear_overrides_for(name)

    # ------------------------------------------------------------------
    # Per-game overrides
    # ------------------------------------------------------------------

    def get_effective(self, field_name: str, game_type: str | None = None) -> Any:
        """Return a preference's effective value, honoring per-game overrides.

        If ``game_type`` has an override for ``field_name``, that wins; otherwise
        the global value is returned. Enum-typed preferences stored as raw
        strings are converted back to their enum.
        """
        if game_type and game_type in self.game_overrides:
            overrides = self.game_overrides[game_type]
            if field_name in overrides:
                raw = overrides[field_name]
                current = getattr(self, field_name, None)
                if isinstance(current, Enum) and not isinstance(raw, Enum):
                    try:
                        return type(current)(raw)
                    except (ValueError, KeyError):
                        return current
                return raw
        return getattr(self, field_name)

    def set_game_override(self, field_name: str, game_type: str, value: Any) -> None:
        """Set a per-game override (enums are stored as their value)."""
        if isinstance(value, Enum):
            value = value.value
        self.game_overrides.setdefault(game_type, {})[field_name] = value

    def clear_game_override(self, field_name: str, game_type: str) -> None:
        """Remove a per-game override, reverting to the global value."""
        if game_type in self.game_overrides:
            self.game_overrides[game_type].pop(field_name, None)
            if not self.game_overrides[game_type]:
                del self.game_overrides[game_type]

    def get_game_override(self, field_name: str, game_type: str) -> Any | None:
        """Return the raw per-game override, or None if unset."""
        return self.game_overrides.get(game_type, {}).get(field_name)

    def has_game_override(self, field_name: str, game_type: str) -> bool:
        """Whether a per-game override exists for this field."""
        return field_name in self.game_overrides.get(game_type, {})
