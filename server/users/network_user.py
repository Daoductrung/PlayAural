"""Network user implementation for real players."""

from typing import Any, TYPE_CHECKING

from .base import User, MenuItem, EscapeBehavior, generate_uuid
from .preferences import UserPreferences
from ..messages.localization import Localization
from ..audio import AudioCommand

if TYPE_CHECKING:
    from ..network.websocket_server import ClientConnection


def _menu_content(state: dict[str, Any]) -> dict[str, Any]:
    """The fields of a stored menu state that the client renders.

    ``position`` is excluded: it is a one-shot focus directive, not content,
    and a repaint that omits it must still be skippable against a stored
    state that recorded one.
    """
    return {k: v for k, v in state.items() if k != "position"}


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
        client_type: str = "python",
        client_platform: str = "",
        uuid: str | None = None,
        preferences: UserPreferences | None = None,
        trust_level: int = 1,
        approved: bool = False,
        session_handover_pending: bool = False,
    ):
        self._uuid = uuid or generate_uuid()
        self._username = username
        self._locale = locale
        self._connection = connection
        self._client_type = client_type
        self._client_platform = client_platform
        self._preferences = preferences or UserPreferences()
        self._trust_level = trust_level
        self._approved = approved
        self._active = True
        self._session_handover_pending = session_handover_pending
        self._message_queue: list[dict[str, Any]] = []

        # Track current UI state for session resumption
        self._current_menus: dict[str, dict[str, Any]] = {}
        self._current_editboxes: dict[str, dict[str, Any]] = {}
        self._audio_sequence = 0
        # The menu_id of the last menu packet queued for this client, or None
        # when a non-menu UI (editbox, clear_ui) has taken the screen since.
        # Clients display one menu at a time, so this is what the client is
        # showing; a repaint may only be content-diff-skipped against it.
        self._last_menu_packet_id: str | None = None

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
    def client_type(self) -> str:
        return self._client_type

    @property
    def client_platform(self) -> str:
        return self._client_platform

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

    @property
    def active(self) -> bool:
        """Whether this runtime user still owns a live account session."""
        return self._active

    def deactivate(self) -> None:
        """Retire this runtime user and discard unsent session output."""
        self._active = False
        self._session_handover_pending = False
        self._message_queue.clear()
        self._current_menus.clear()
        self._current_editboxes.clear()
        self._last_menu_packet_id = None
        self._runtime_audio_states = {}

    @property
    def session_handover_pending(self) -> bool:
        """Whether a forced login screen still precedes live state restore."""
        return self._session_handover_pending

    def complete_session_handover(self) -> None:
        """Mark deferred live-session restoration as complete."""
        self._session_handover_pending = False

    def _queue_packet(self, packet: dict[str, Any]) -> None:
        """Queue a packet to be sent to the client."""
        if not self._active:
            return
        self._message_queue.append(packet)

    def get_queued_messages(self) -> list[dict[str, Any]]:
        """Get and clear the message queue.

        Coalesces redundant menu repaints: when more than one ``menu`` packet for
        the same ``menu_id`` is queued in a single flush — e.g. an action handler
        rebuilds the menu and the event framework rebuilds it again on the same
        tick — only the last one survives. This collapses double-sends (double
        screen-reader announcements and double focus churn) without games having
        to police their own rebuild calls. All non-menu packets, and menus with
        distinct ids, pass through untouched and in order.
        """
        if not self._active:
            self._message_queue.clear()
            return []
        messages = self._message_queue
        self._message_queue = []

        # For each menu_id: the index of the final repaint (whose items win) and
        # the most recent *explicit* focus directive in the batch. A handler that
        # targets a specific item (e.g. the freshly drawn card in Ninety Nine)
        # commonly does so just before the event framework fires a blanket
        # rebuild with no focus; a plain repaint means "keep focus", never "reset
        # it", so the explicit directive must survive the later repaint.
        last_menu_index: dict[str, int] = {}
        last_focus: dict[str, dict[str, Any]] = {}
        for i, packet in enumerate(messages):
            if packet.get("type") == "menu":
                menu_id = packet.get("menu_id")
                if menu_id is not None:
                    last_menu_index[menu_id] = i
                    if (
                        packet.get("selection_id") is not None
                        or packet.get("position") is not None
                    ):
                        last_focus[menu_id] = {
                            "selection_id": packet.get("selection_id"),
                            "position": packet.get("position"),
                        }

        if not last_menu_index:
            return messages

        coalesced = []
        for i, packet in enumerate(messages):
            if packet.get("type") == "menu":
                menu_id = packet.get("menu_id")
                if menu_id is not None:
                    if last_menu_index.get(menu_id) != i:
                        continue  # superseded by a later repaint of the same menu
                    focus = last_focus.get(menu_id)
                    if (
                        focus is not None
                        and packet.get("selection_id") is None
                        and packet.get("position") is None
                    ):
                        # Carry the batch's latest explicit focus onto the
                        # surviving repaint without mutating the original packet.
                        packet = {**packet}
                        if focus["selection_id"] is not None:
                            packet["selection_id"] = focus["selection_id"]
                        if focus["position"] is not None:
                            packet["position"] = focus["position"]
            coalesced.append(packet)
        return coalesced

    def speak(self, text: str, buffer: str = "misc") -> None:
        packet = {"type": "speak", "text": text, "buffer": buffer}
        self._queue_packet(packet)

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs) -> None:
        """
        Send a localized message with params.
        Attempts server-side translation first, but sends raw key and params
        to allow client-side translation/overrides.
        """
        # Try to format on server
        text = Localization.get(self.locale, message_id, **kwargs)
        
        packet = {
            "type": "speak",
            "text": text,        # Result of server translation (or key if missing)
            "key": message_id,   # The raw key
            "params": kwargs,    # The params for client-side functionality
            "buffer": buffer,
        }

        self._queue_packet(packet)

    def send_audio_command(self, command: AudioCommand) -> None:
        """Queue an ordered command from the unified audio protocol."""
        if not self._active:
            return
        self._record_audio_command(command)
        self._audio_sequence += 1
        packet = command.to_packet()
        packet["sequence"] = self._audio_sequence
        self._queue_packet(packet)

    def _convert_items(self, items: list[str | MenuItem]) -> list[str | dict]:
        """Render menu hints and convert rows for JSON serialization."""
        result = []
        for item in items:
            if isinstance(item, MenuItem):
                result.append(
                    item.to_dict(
                        locale=self.locale,
                        show_description=self.preferences.show_menu_hints,
                    )
                )
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
        selection_id: str | None = None,
        grid_enabled: bool = False,
        grid_height: int = 0,
        grid_width: int = 1,
    ) -> None:
        converted_items = self._convert_items(items)
        escape_str = escape_behavior.value

        state = {
            "items": converted_items,
            "multiletter_enabled": multiletter,
            "escape_behavior": escape_str,
            "position": position,
            "grid_enabled": grid_enabled,
            "grid_height": grid_height,
            "grid_width": grid_width,
        }

        # Content-diff skip: a repaint of the menu the client is already
        # displaying, with identical content and no explicit focus directive,
        # is a client-side no-op — don't spend a packet on it. Restricted to
        # the menu named by _last_menu_packet_id so a re-show after the client
        # moved to another menu/editbox always goes out in full.
        previous = self._current_menus.get(menu_id)
        if (
            position is None
            and selection_id is None
            and menu_id == self._last_menu_packet_id
            and previous is not None
            and _menu_content(previous) == _menu_content(state)
        ):
            self._current_menus[menu_id] = state
            return

        # Store for session resumption
        self._current_menus[menu_id] = state

        packet: dict[str, Any] = {
            "type": "menu",
            "menu_id": menu_id,
            "items": converted_items,
            "multiletter_enabled": multiletter,
            "escape_behavior": escape_str,
            "grid_enabled": grid_enabled,
            "grid_height": grid_height,
            "grid_width": grid_width,
        }
        if position is not None:
            # Convert 1-based to 0-based for client
            packet["position"] = position - 1
        if selection_id is not None:
            packet["selection_id"] = selection_id
        self._last_menu_packet_id = menu_id
        self._queue_packet(packet)

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
        converted_items = self._convert_items(items)

        previous = self._current_menus.get(menu_id)
        if (
            position is None
            and selection_id is None
            and menu_id == self._last_menu_packet_id
            and previous is not None
            and previous.get("items") == converted_items
            and previous.get("grid_enabled") == grid_enabled
            and previous.get("grid_height") == grid_height
            and previous.get("grid_width") == grid_width
        ):
            return  # Content-diff skip; see show_menu.

        if previous is not None:
            previous["items"] = converted_items
            if position is not None:
                previous["position"] = position
            previous["grid_enabled"] = grid_enabled
            previous["grid_height"] = grid_height
            previous["grid_width"] = grid_width

        packet: dict[str, Any] = {
            "type": "menu",
            "menu_id": menu_id,
            "items": converted_items,
            "grid_enabled": grid_enabled,
            "grid_height": grid_height,
            "grid_width": grid_width,
        }
        if position is not None:
            packet["position"] = position - 1
        if selection_id is not None:
            packet["selection_id"] = selection_id
        self._last_menu_packet_id = menu_id
        self._queue_packet(packet)

    def remove_menu(self, menu_id: str, *, send_packet: bool = True) -> None:
        self._current_menus.pop(menu_id, None)
        if self._last_menu_packet_id == menu_id:
            self._last_menu_packet_id = None
        if not send_packet:
            return
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
        max_length: int | None = None,
    ) -> None:
        self._current_editboxes[input_id] = {
            "prompt": prompt,
            "default_value": default_value,
            "multiline": multiline,
            "read_only": read_only,
            "max_length": max_length,
        }
        packet = {
            "type": "request_input",
            "input_id": input_id,
            "prompt": prompt,
            "default_value": default_value,
            "multiline": multiline,
            "read_only": read_only,
        }
        if max_length is not None:
            packet["max_length"] = max_length
        # The editbox takes the client's screen; the next menu paint must be
        # sent in full even if its content is unchanged.
        self._last_menu_packet_id = None
        self._queue_packet(packet)

    def remove_editbox(self, input_id: str) -> None:
        self._current_editboxes.pop(input_id, None)
        # The client may have had an overlay above the last recorded menu, so
        # the first replacement menu must never be content-diff suppressed.
        self._last_menu_packet_id = None
        self._queue_packet({"type": "remove_editbox", "input_id": input_id})

    def clear_ui(self) -> None:
        self._current_menus.clear()
        self._current_editboxes.clear()
        self._last_menu_packet_id = None
        self._queue_packet({"type": "clear_ui"})

    def set_table_context(self, table_id: str) -> None:
        self._queue_packet(
            {
                "type": "table_context",
                "table_id": table_id,
            }
        )
