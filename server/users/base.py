"""Abstract User class that games interact with."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any
import uuid as uuid_module

from ..messages.localization import Localization
from ..audio import (
    AudioCommand,
    DEFAULT_AMBIENCE_FADE_MS,
    DEFAULT_MUSIC_FADE_MS,
    new_audio_handle,
)

if TYPE_CHECKING:
    from .preferences import UserPreferences


class EscapeBehavior(Enum):
    """How the escape key behaves in menus."""

    KEYBIND = "keybind"  # Sent as keybind event (ignored if no handler)
    SELECT_LAST = "select_last_option"  # Auto-selects the last menu item
    SELECT_FIRST = "select_first_option"  # Auto-selects the first menu item
    ESCAPE_EVENT = "escape_event"  # Sends explicit escape event to server


@dataclass
class MenuItem:
    """A menu row with optional sound and reusable descriptive help.

    ``description`` is already-localized text. ``description_key`` is the
    equivalent Fluent-backed form for framework menus. Callers set one or the
    other; the user layer resolves and displays the hint consistently for
    every client according to the account's menu-hints preference.
    """

    text: str
    id: str | None = None
    sound: str | None = None  # Sound played when this item is highlighted
    description: str | None = None
    description_key: str | None = None
    description_kwargs: dict[str, Any] | None = None
    label: str | None = None

    def __post_init__(self) -> None:
        if self.description is not None and self.description_key is not None:
            raise ValueError(
                "MenuItem accepts description or description_key, not both"
            )

    def resolved_description(self, locale: str) -> str | None:
        """Return localized row help without exposing a Fluent key."""
        if self.description is not None:
            return self.description.strip() or None
        if self.description_key is None:
            return None
        text = Localization.get(
            locale,
            self.description_key,
            **(self.description_kwargs or {}),
        )
        if text == self.description_key and not Localization.has_message(
            locale,
            self.description_key,
        ):
            return None
        return text.strip() or None

    @property
    def canonical_text(self) -> str:
        """Return the concise label retained by rendered/restored rows."""
        return self.label if self.label is not None else self.text

    def display_text(self, locale: str, *, show_description: bool) -> str:
        """Render the row label under the global menu-hints policy."""
        description = self.resolved_description(locale)
        return self._display_text(
            locale,
            description,
            show_description=show_description,
        )

    def _display_text(
        self,
        locale: str,
        description: str | None,
        *,
        show_description: bool,
    ) -> str:
        """Combine a label and an already-resolved hint."""
        if not show_description or not description:
            return self.canonical_text
        return Localization.get(
            locale,
            "menu-item-with-hint",
            label=self.canonical_text,
            hint=description,
        )

    def rendered(self, locale: str, *, show_description: bool) -> "MenuItem":
        """Return a display-ready copy while retaining on-demand help."""
        description = self.resolved_description(locale)
        return MenuItem(
            text=self._display_text(
                locale,
                description,
                show_description=show_description,
            ),
            id=self.id,
            sound=self.sound,
            description=description,
            label=self.canonical_text,
        )

    def to_dict(
        self,
        *,
        locale: str = "en",
        show_description: bool = False,
    ) -> dict[str, Any] | str:
        description = self.resolved_description(locale)
        if (
            self.id is not None
            or self.sound is not None
            or description is not None
        ):
            data: dict[str, Any] = {
                "text": self._display_text(
                    locale,
                    description,
                    show_description=show_description,
                )
            }
            if self.id is not None:
                data["id"] = self.id
            if self.sound is not None:
                data["sound"] = self.sound
            if description is not None:
                # ``label`` keeps restoration idempotent after the rendered
                # text has been stored in NetworkUser's current-menu state.
                data["label"] = self.canonical_text
                data["description"] = description
            return data
        return self.canonical_text


class User(ABC):
    """
    Abstract base class for users.

    Games interact with this interface, never with network code directly.
    Implementations include NetworkUser (real players), TestUser (for testing),
    and Bot (AI players).
    """

    @property
    @abstractmethod
    def uuid(self) -> str:
        """The user's unique identifier (UUID string)."""
        ...

    @property
    @abstractmethod
    def username(self) -> str:
        """The user's display name."""
        ...

    @property
    @abstractmethod
    def locale(self) -> str:
        """The user's locale for localization (e.g., 'en', 'es')."""
        ...

    @property
    def trust_level(self) -> int:
        """The user's trust level (1 = player, 2 = admin). Defaults to 1 if not overridden."""
        return 1

    @property
    def preferences(self) -> "UserPreferences":
        """The user's preferences. Returns defaults if not overridden."""
        from .preferences import UserPreferences

        return UserPreferences()

    @abstractmethod
    def speak(self, text: str, buffer: str = "misc") -> None:
        """
        Send a text message to be displayed and spoken via TTS.

        Args:
            text: The message text.
            buffer: Which buffer to route the message to (game, system, chat, misc).
        """
        ...

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs) -> None:
        """
        Send a localized message to be displayed and spoken via TTS.

        Args:
            message_id: The message ID from the .ftl file.
            buffer: Which buffer to route the message to (game, system, chat, misc).
            **kwargs: Variables to substitute into the message.
        """
        text = Localization.get(self.locale, message_id, **kwargs)
        self.speak(text, buffer=buffer)

    @abstractmethod
    def send_audio_command(self, command: AudioCommand) -> None:
        """Deliver one validated audio command to this user."""
        ...

    def _record_audio_command(self, command: AudioCommand) -> None:
        """Mirror managed command ownership for this runtime user.

        This state is deliberately runtime-only.  It lets framework navigation
        avoid restarting an already-owned layer without assuming anything
        about a specific client backend.  A replacement connection receives a
        fresh ``User`` instance, so reconnect restoration still replays every
        authoritative layer.
        """
        states = getattr(self, "_runtime_audio_states", None)
        if states is None:
            states = {}
            self._runtime_audio_states = states

        if command.command == "stop_all":
            states.clear()
            return

        if command.command == "play" and command.handle:
            for key, state in list(states.items()):
                if (
                    state.kind == command.kind
                    and state.scope == command.scope
                    and state.context == command.context
                    and state.layer == command.layer
                ):
                    states.pop(key, None)
            states[(command.kind, command.handle)] = command
            return

        if command.command != "stop":
            return

        if command.handle:
            states.pop((command.kind, command.handle), None)
            return

        for key, state in list(states.items()):
            if (
                state.kind == command.kind
                and state.scope == command.scope
                and state.context == command.context
                and state.layer == command.layer
            ):
                states.pop(key, None)

    def has_managed_audio(
        self,
        kind: str,
        *,
        handle: str,
        asset: str = "",
    ) -> bool:
        """Return whether this live client session owns a matching layer."""
        states = getattr(self, "_runtime_audio_states", {})
        state = states.get((kind, handle))
        return bool(state and (not asset or state.asset == asset))

    def play_sound(
        self,
        name: str,
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
        *,
        loop: bool = False,
        handle: str = "",
        bus: str = "sfx",
        fade_in_ms: int = 0,
        fade_out_ms: int = 0,
        priority: int = 0,
        max_instances: int = 0,
        ducking: dict[str, int] | None = None,
        scope: str = "global",
        context: str = "",
        layer: str = "main",
    ) -> str:
        """Play an effect and return its optional lifecycle handle."""
        resolved_handle = handle or (new_audio_handle("sfx") if loop else "")
        self.send_audio_command(
            AudioCommand(
                command="play",
                kind="sfx",
                asset=name,
                handle=resolved_handle,
                bus=bus,
                scope=scope,
                context=context,
                layer=layer,
                loop=loop,
                volume=volume,
                pan=pan,
                pitch=pitch,
                fade_in_ms=fade_in_ms,
                fade_out_ms=fade_out_ms,
                priority=priority,
                max_instances=max_instances,
                ducking=ducking or {},
            )
        )
        return resolved_handle

    def play_sound_family(
        self,
        family: str,
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
        *,
        bus: str = "sfx",
        priority: int = 0,
        max_instances: int = 0,
    ) -> None:
        """Play one randomly selected numbered member of an SFX family."""
        self.send_audio_command(
            AudioCommand(
                command="play",
                kind="sfx",
                family=family,
                bus=bus,
                volume=volume,
                pan=pan,
                pitch=pitch,
                priority=priority,
                max_instances=max_instances,
            )
        )

    def stop_sound(self, handle: str, *, fade_ms: int = 0) -> None:
        """Stop one managed sound effect without affecting other instances."""
        self.send_audio_command(
            AudioCommand(
                command="stop",
                kind="sfx",
                handle=handle,
                fade_out_ms=fade_ms,
            )
        )

    def play_music(
        self,
        name: str,
        looping: bool = True,
        *,
        handle: str = "music",
        bus: str = "music",
        fade_in_ms: int = DEFAULT_MUSIC_FADE_MS,
        fade_out_ms: int = DEFAULT_MUSIC_FADE_MS,
        priority: int = 0,
        ducking: dict[str, int] | None = None,
        scope: str = "global",
        context: str = "",
        layer: str = "main",
    ) -> str:
        """Play or crossfade a music layer and return its stable handle."""
        self.send_audio_command(
            AudioCommand(
                command="play",
                kind="music",
                asset=name,
                handle=handle,
                bus=bus,
                scope=scope,
                context=context,
                layer=layer,
                loop=looping,
                fade_in_ms=fade_in_ms,
                fade_out_ms=fade_out_ms,
                priority=priority,
                ducking=ducking or {},
            )
        )
        return handle

    def pause_music(
        self, *, handle: str = "music", fade_ms: int = DEFAULT_MUSIC_FADE_MS
    ) -> None:
        """Fade and pause music, preserving its playback position."""
        self.send_audio_command(
            AudioCommand(
                command="pause",
                kind="music",
                handle=handle,
                fade_out_ms=fade_ms,
            )
        )

    def resume_music(
        self, *, handle: str = "music", fade_ms: int = DEFAULT_MUSIC_FADE_MS
    ) -> None:
        """Resume paused music with a fade-in."""
        self.send_audio_command(
            AudioCommand(
                command="resume",
                kind="music",
                handle=handle,
                fade_in_ms=fade_ms,
            )
        )

    def stop_music(
        self, *, handle: str = "music", fade_ms: int = DEFAULT_MUSIC_FADE_MS
    ) -> None:
        """Fade and stop music."""
        self.send_audio_command(
            AudioCommand(
                command="stop",
                kind="music",
                handle=handle,
                fade_out_ms=fade_ms,
            )
        )

    def play_ambience(
        self,
        loop: str,
        intro: str = "",
        outro: str = "",
        *,
        handle: str = "",
        bus: str = "ambience",
        fade_in_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        fade_out_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        volume: int = 100,
        priority: int = 0,
        ducking: dict[str, int] | None = None,
        play_intro: bool = True,
        seamless: bool = True,
        scope: str = "global",
        context: str = "",
        layer: str = "environment",
    ) -> str:
        """Play or crossfade one independently scoped ambience layer."""
        resolved_handle = handle or f"ambience:{scope}:{context or 'default'}:{layer}"
        self.send_audio_command(
            AudioCommand(
                command="play",
                kind="ambience",
                asset=loop,
                handle=resolved_handle,
                bus=bus,
                scope=scope,
                context=context,
                layer=layer,
                loop=True,
                intro=intro,
                outro=outro,
                play_intro=play_intro,
                seamless=seamless,
                volume=volume,
                fade_in_ms=fade_in_ms,
                fade_out_ms=fade_out_ms,
                priority=priority,
                ducking=ducking or {},
            )
        )
        return resolved_handle

    def stop_ambience(
        self,
        *,
        handle: str = "",
        fade_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        play_outro: bool = True,
        outro_mode: str = "immediate",
        scope: str = "global",
        context: str = "",
        layer: str = "environment",
    ) -> None:
        """Fade and stop an ambience handle or scoped layer."""
        self.send_audio_command(
            AudioCommand(
                command="stop",
                kind="ambience",
                handle=handle,
                scope=scope,
                context=context,
                layer=layer,
                fade_out_ms=fade_ms,
                play_outro=play_outro,
                outro_mode=outro_mode,
            )
        )

    def stop_all_ambience(
        self,
        *,
        fade_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        play_outro: bool = True,
        outro_mode: str = "immediate",
    ) -> None:
        """Stop every ambience layer while preserving configured outros."""
        self.send_audio_command(
            AudioCommand(
                command="stop",
                kind="ambience",
                all_layers=True,
                fade_out_ms=fade_ms,
                play_outro=play_outro,
                outro_mode=outro_mode,
            )
        )

    def set_audio_bus(self, bus: str, gain: int, *, fade_ms: int = 0) -> None:
        """Set a server-controlled bus gain without changing user preferences."""
        self.send_audio_command(
            AudioCommand(
                command="set_bus",
                bus=bus,
                volume=gain,
                fade_in_ms=fade_ms,
            )
        )

    def stop_all_audio(
        self,
        *,
        fade_ms: int = 0,
        play_outros: bool = False,
        outro_mode: str = "immediate",
    ) -> None:
        """Stop all server-controlled audio for this user."""
        self.send_audio_command(
            AudioCommand(
                command="stop_all",
                fade_out_ms=fade_ms,
                play_outros=play_outros,
                outro_mode=outro_mode,
            )
        )

    @abstractmethod
    def show_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        *,
        multiletter: bool = True,
        escape_behavior: EscapeBehavior = EscapeBehavior.KEYBIND,
        position: int | None = None,
        selection_id: str | None = None,
        grid_enabled: bool = False,
        grid_height: int = 0,
        grid_width: int = 1,
    ) -> None:
        """
        Display a menu to the user.

        Args:
            menu_id: String identifier for this menu.
            items: List of menu items (strings or MenuItem objects).
            multiletter: Enable type-to-search navigation.
            escape_behavior: How escape key behaves (see EscapeBehavior enum).
            position: 1-based position to select (None for first item).
            selection_id: Optional item ID to focus on (overrides position).
            grid_enabled: Enable grid navigation mode.
            grid_height: Number of rows in grid mode.
            grid_width: Number of columns in grid mode.
        """
        ...

    @abstractmethod
    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
        *,
        grid_enabled: bool = False,
        grid_height: int = 0,
        grid_width: int = 1,
    ) -> None:
        """
        Update an existing menu's items.

        Args:
            menu_id: The menu to update.
            items: New list of items.
            position: Optional new position (1-based).
            selection_id: Optional item ID to focus on.
            grid_enabled: Enable grid navigation mode.
            grid_height: Number of rows in grid mode.
            grid_width: Number of columns in grid mode.
        """
        ...

    @abstractmethod
    def remove_menu(self, menu_id: str, *, send_packet: bool = True) -> None:
        """
        Remove a menu.

        Args:
            menu_id: The menu to remove.
            send_packet: Whether to notify the client with an empty menu packet.
        """
        ...

    @abstractmethod
    def show_editbox(
        self,
        input_id: str,
        prompt: str,
        default_value: str = "",
        *,
        multiline: bool = False,
        read_only: bool = False,
        max_length: int | None = None,
    ) -> None:
        """
        Display an editbox to the user.

        Args:
            input_id: String identifier for this editbox.
            prompt: Prompt text to display.
            default_value: Default text in the editbox.
            multiline: Whether to use a multiline editbox.
            read_only: Whether the editbox is read-only.
            max_length: Optional maximum number of input characters.
        """
        ...

    @abstractmethod
    def remove_editbox(self, input_id: str) -> None:
        """
        Remove an editbox.

        Args:
            input_id: The editbox to remove.
        """
        ...

    @abstractmethod
    def clear_ui(self) -> None:
        """Clear all menus and editboxes."""
        ...

    def set_table_context(self, table_id: str) -> None:
        """Notify the client which table context is currently active."""
        return


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid_module.uuid4())
