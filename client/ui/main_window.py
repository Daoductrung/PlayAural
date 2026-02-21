"""Main window for PlayAural v0.1 client."""

import wx
from .menu_list import MenuList
import accessible_output2.outputs.auto as auto_output
import sys
import os
import json
from pathlib import Path
import requests
import zipfile
import subprocess
import threading
import time

# Add parent directory to path to import sound_manager and network_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import slash_commands
from sound_manager import SoundManager
from network_manager import NetworkManager
from buffer_system import BufferSystem
from config_manager import set_item_in_dict
from localization import Localization

VERSION = "0.1.5"


class MainWindow(wx.Frame):
    """Main application window for PlayAural v9 client."""

    def __init__(self, credentials=None):
        """
        Initialize the main window.

        Args:
            credentials: Dict with username, password, server_url, server_id, config_manager
        """

        
        super().__init__(
            parent=None,
            title=Localization.get("main-window-title", version=VERSION),
            size=(1, 1),  # Minimal size for audio-only interface
        )

        # Store credentials
        self.credentials = credentials or {}
        self.server_id = self.credentials.get("server_id")
        self.config_manager = self.credentials.get("config_manager")

        # Initialize TTS speaker
        self.speaker = auto_output.Auto()

        # Initialize sound manager
        self.sound_manager = SoundManager()

        slash_commands.client = self

        # Play open sound
        self.sound_manager.play("open.ogg", volume=1.0)

        # Initialize network manager
        self.network = NetworkManager(self)
        self.connected = False
        self.expecting_reconnect = False  # Track if we're expecting to reconnect (server restart)
        self.is_reconnecting = False # Track if we are in silent reconnect mode
        self.quitting = False # Track if finding to exit
        self.reconnect_start_time = None
        self.max_silent_reconnect_duration = 30 # seconds
        self.reconnect_attempts = 0  # Track reconnection attempts
        self.max_reconnect_attempts = 30  # Maximum reconnection attempts
        self.last_server_message = None  # Track last speak message for error display
        self.disconnect_reason = None  # Track reason for disconnection

        # Store user's options
        # Client-side options (from config file, per-server)
        self.client_options = {}
        # Server-side options (received from server on login)
        self.server_options = {}

        # Load client-side options for this server
        if self.config_manager and self.server_id:
            self.client_options = self.config_manager.get_client_options(self.server_id)
            # Apply initial volumes from client options
            self._apply_client_audio_options()

        # Track which test music is playing
        self.current_test_music = "mainmus.ogg"

        # Track current mode (list or edit)
        self.current_mode = "list"  # "list" or "edit"
        self.edit_mode_callback = None  # Callback for when edit mode submits
        self.current_menu_id = None  # Track which menu is currently displayed
        self.current_menu_state = None  # Track previous menu state for comparison
        self.current_menu_item_ids = []  # Track item IDs for current menu (parallel to menu items)
        self.current_edit_multiline = False  # Track if current editbox is multiline
        self.current_edit_read_only = False  # Track if current editbox is read-only

        # Ping tracking
        self._ping_start_time = None  # Track when ping was sent

        # Initialize buffer system
        self.buffer_system = BufferSystem()
        self.buffer_system.create_buffer("all")
        self.buffer_system.create_buffer("chat")
        self.buffer_system.create_buffer("game")
        self.buffer_system.create_buffer("system")
        self.buffer_system.create_buffer("misc")

        # Load muted buffers from preferences
        preferences = self._load_preferences()
        if "muted_buffers" in preferences:
            for buffer_name in preferences["muted_buffers"]:
                if not self.buffer_system.is_muted(buffer_name):
                    self.buffer_system.toggle_mute(buffer_name)

        # Initialize UI components
        self._create_ui()
        self._setup_accelerators()
        self._populate_test_data()

        # Language codes map
        self.lang_codes = {"en": "English", "vi": "Vietnamese", "es": "Spanish"}

        # Auto-connect
        self._auto_connect()

    def _apply_client_audio_options(self):
        """Apply audio settings from client-side options."""
        if "audio" in self.client_options:
            audio = self.client_options["audio"]
            music_volume = audio.get("music_volume", 20) / 100.0
            ambience_volume = audio.get("ambience_volume", 20) / 100.0

            self.sound_manager.set_music_volume(music_volume)
            self.sound_manager.set_ambience_volume(ambience_volume)

    def _create_ui(self):
        """Create the UI components (audio-only, no visual layout)."""
        # Main panel - no sizing needed
        panel = wx.Panel(self)

        # Menu label and list - labels help screen readers
        self.menu_label = wx.StaticText(panel, label=Localization.get("main-menu-label"))
        self.menu_list = MenuList(
            panel,
            sound_manager=self.sound_manager,
            size=(0, 0),
            style=wx.LB_SINGLE | wx.WANTS_CHARS,
        )
        # Bind to activation events to handle menu selections
        self.menu_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_menu_activate)
        # Bind focus events to enable/disable buffer navigation
        self.menu_list.Bind(wx.EVT_SET_FOCUS, self.on_menu_focus)
        self.menu_list.Bind(wx.EVT_KILL_FOCUS, self.on_menu_unfocus)

        # Edit mode input - initially hidden, replaces menu list when in edit mode
        self.edit_label = wx.StaticText(panel, label=Localization.get("main-edit-label"))
        self.edit_input = wx.TextCtrl(panel, size=(0, 0), style=wx.TE_PROCESS_ENTER)
        self.edit_input.Bind(wx.EVT_TEXT_ENTER, self.on_edit_enter)
        self.edit_input.Bind(wx.EVT_CHAR, self.on_edit_char)
        self.edit_input.Bind(wx.EVT_KEY_DOWN, self.on_edit_key_down)
        self.edit_input.Hide()
        self.edit_label.Hide()

        # Multiline edit input - for longer text
        self.edit_input_multiline = wx.TextCtrl(
            panel, size=(0, 0), style=wx.TE_MULTILINE | wx.TE_DONTWRAP
        )
        self.edit_input_multiline.Bind(wx.EVT_CHAR, self.on_edit_multiline_char)
        self.edit_input_multiline.Bind(wx.EVT_KEY_DOWN, self.on_edit_key_down)
        self.edit_input_multiline.Hide()

        # Multiletter navigation is now server-controlled
        self.multiletter_enabled = True  # Track state from server
        self.escape_behavior = "keybind"  # Track escape behavior from server

        # Chat input comes before history in tab order
        wx.StaticText(panel, label=Localization.get("main-chat-label"))
        self.chat_input = wx.TextCtrl(panel, size=(0, 0), style=wx.TE_PROCESS_ENTER)
        self.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_chat_enter)

        # History text - not visible, just exists for data storage
        # No word wrap for better screen reader accessibility
        wx.StaticText(panel, label=Localization.get("main-history-label"))
        self.history_text = wx.TextCtrl(
            panel, size=(0, 0), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP
        )

        # No sizers, no layout - audio-only interface

    def _setup_accelerators(self):
        """Setup keyboard accelerators."""
        # Create unique IDs for each accelerator
        self.ID_FOCUS_MENU = wx.NewIdRef()
        self.ID_FOCUS_CHAT = wx.NewIdRef()
        self.ID_FOCUS_HISTORY = wx.NewIdRef()        
        self.ID_VOLUME_DOWN = wx.NewIdRef()
        self.ID_VOLUME_UP = wx.NewIdRef()
        self.ID_AMBIENCE_DOWN = wx.NewIdRef()
        self.ID_AMBIENCE_UP = wx.NewIdRef()
        self.ID_TOGGLE_TABLE_CHAT = wx.NewIdRef()
        self.ID_TOGGLE_GLOBAL_CHAT = wx.NewIdRef()
        self.ID_PING = wx.NewIdRef()
        self.ID_LIST_ONLINE = wx.NewIdRef()
        self.ID_LIST_ONLINE_WITH_GAMES = wx.NewIdRef()

        # Buffer system IDs
        self.ID_PREV_BUFFER = wx.NewIdRef()
        self.ID_NEXT_BUFFER = wx.NewIdRef()
        self.ID_FIRST_BUFFER = wx.NewIdRef()
        self.ID_LAST_BUFFER = wx.NewIdRef()
        self.ID_OLDER_MESSAGE = wx.NewIdRef()
        self.ID_NEWER_MESSAGE = wx.NewIdRef()
        self.ID_OLDEST_MESSAGE = wx.NewIdRef()
        self.ID_NEWEST_MESSAGE = wx.NewIdRef()
        self.ID_TOGGLE_MUTE = wx.NewIdRef()

        # Common accelerators that work everywhere
        common_entries = [
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("M"), self.ID_FOCUS_MENU),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("C"), self.ID_FOCUS_CHAT),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("H"), self.ID_FOCUS_HISTORY),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F6, self.ID_TOGGLE_TABLE_CHAT),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F6, self.ID_TOGGLE_GLOBAL_CHAT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F7, self.ID_AMBIENCE_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F8, self.ID_AMBIENCE_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F9, self.ID_VOLUME_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F10, self.ID_VOLUME_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, self.ID_LIST_ONLINE),
            wx.AcceleratorEntry(
                wx.ACCEL_SHIFT, wx.WXK_F2, self.ID_LIST_ONLINE_WITH_GAMES
            ),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("P"), self.ID_PING),
        ]

        # Buffer navigation accelerators (only for menu list)
        buffer_entries = [
            # Buffer switching: [ and ]
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("["), self.ID_PREV_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("]"), self.ID_NEXT_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("["), self.ID_FIRST_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("]"), self.ID_LAST_BUFFER),
            # Message navigation: , and .
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord(","), self.ID_OLDER_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("."), self.ID_NEWER_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord(","), self.ID_OLDEST_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("."), self.ID_NEWEST_MESSAGE),
            # Buffer mute: F4
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, self.ID_TOGGLE_MUTE),
        ]

        # Create two accelerator tables
        self.accel_table_with_buffers = wx.AcceleratorTable(
            common_entries + buffer_entries
        )
        self.accel_table_without_buffers = wx.AcceleratorTable(common_entries)

        # Start without buffer keys (will be enabled when menu gets focus)
        self.SetAcceleratorTable(self.accel_table_without_buffers)

        # Bind the accelerator events
        self.Bind(wx.EVT_MENU, self.on_focus_menu, id=self.ID_FOCUS_MENU)
        self.Bind(wx.EVT_MENU, self.on_focus_chat, id=self.ID_FOCUS_CHAT)
        self.Bind(wx.EVT_MENU, self.on_focus_history, id=self.ID_FOCUS_HISTORY)
        self.Bind(wx.EVT_MENU, self.on_toggle_table_chat, id=self.ID_TOGGLE_TABLE_CHAT)
        self.Bind(
            wx.EVT_MENU, self.on_toggle_global_chat, id=self.ID_TOGGLE_GLOBAL_CHAT
        )
        self.Bind(wx.EVT_MENU, self.on_ambience_down, id=self.ID_AMBIENCE_DOWN)
        self.Bind(wx.EVT_MENU, self.on_ambience_up, id=self.ID_AMBIENCE_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_VOLUME_DOWN)
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_VOLUME_UP)
        self.Bind(wx.EVT_MENU, self.on_ping, id=self.ID_PING)
        self.Bind(wx.EVT_MENU, self.on_list_online, id=self.ID_LIST_ONLINE)
        self.Bind(
            wx.EVT_MENU,
            self.on_list_online_with_games,
            id=self.ID_LIST_ONLINE_WITH_GAMES,
        )

        # Buffer system event bindings
        self.Bind(wx.EVT_MENU, self.on_prev_buffer, id=self.ID_PREV_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_next_buffer, id=self.ID_NEXT_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_first_buffer, id=self.ID_FIRST_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_last_buffer, id=self.ID_LAST_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_older_message, id=self.ID_OLDER_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_newer_message, id=self.ID_NEWER_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_oldest_message, id=self.ID_OLDEST_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_newest_message, id=self.ID_NEWEST_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_buffer_mute_toggle, id=self.ID_TOGGLE_MUTE)

        # Bind key events for game keypresses
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def _populate_test_data(self):
        """Populate UI with test data."""
        # Menu will be populated by server after connection
        # History starts empty - first message will be "Connecting..."
        pass

    def on_focus_menu(self, event):
        """Handle Alt+M shortcut to focus menu list."""
        self.menu_list.SetFocus()

    def on_focus_chat(self, event):
        """Handle Alt+C shortcut to focus chat input."""
        self.chat_input.SetFocus()

    def on_focus_history(self, event):
        """Handle Alt+H shortcut to focus history text."""
        self.history_text.SetFocus()

    def on_menu_focus(self, event):
        """Handle menu list gaining focus - enable buffer navigation."""
        self.SetAcceleratorTable(self.accel_table_with_buffers)
        event.Skip()

    def on_menu_unfocus(self, event):
        """Handle menu list losing focus - disable buffer navigation."""
        self.SetAcceleratorTable(self.accel_table_without_buffers)
        event.Skip()

    def modify_option_value(self, key_path: str, value, *, create_mode: bool = True) -> bool:
        if not self.config_manager or not self.server_id:
            return False
        self.config_manager.set_client_option(key_path, value, self.server_id, create_mode= create_mode)
        # Update local cache
        set_item_in_dict(self.client_options, key_path, value, create_mode= create_mode)
        
        # Sync to server if connected
        if self.connected:
            self.network.send_packet({
                "type": "set_preference",
                "key": key_path,
                "value": value
            })

    def on_ambience_down(self, event):
        """Handle F7 to decrease ambience volume."""
        current_volume = self.sound_manager.ambience_volume
        new_volume = max(0.0, current_volume - 0.1)
        self.sound_manager.set_ambience_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(Localization.get("main-ambience-volume", value=percentage))
        self.modify_option_value("audio/ambience_volume", percentage)

    def on_ambience_up(self, event):
        """Handle F8 to increase ambience volume."""
        current_volume = self.sound_manager.ambience_volume
        new_volume = min(1.0, current_volume + 0.1)
        self.sound_manager.set_ambience_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(Localization.get("main-ambience-volume", value=percentage))
        self.modify_option_value("audio/ambience_volume", percentage)

    def on_volume_down(self, event):
        """Handle F9 to decrease music volume."""
        current_volume = self.sound_manager.music_volume
        new_volume = max(0.0, current_volume - 0.1)
        self.sound_manager.set_music_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(Localization.get("main-music-volume", value=percentage))
        self.modify_option_value("audio/music_volume", percentage)

    def on_volume_up(self, event):
        """Handle F10 to increase music volume."""
        current_volume = self.sound_manager.music_volume
        new_volume = min(1.0, current_volume + 0.1)
        self.sound_manager.set_music_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(Localization.get("main-music-volume", value=percentage))
        self.modify_option_value("audio/music_volume", percentage)

    def on_ping(self, event):
        """Handle Alt+P to ping the server and measure latency."""
        import time
        self._ping_start_time = time.time()
        self.sound_manager.play("pingstart.ogg")
        self.network.send_packet({"type": "ping"})

    def on_list_online(self, event):
        """Handle F2 to request list of online users."""
        if self.connected:
            self.network.send_packet({"type": "list_online"})

    def on_list_online_with_games(self, event):
        """Handle Shift+F2 to request online users with game info."""
        if self.connected:
            if self.current_menu_id == "online_users":
                return
            self.network.send_packet({"type": "list_online_with_games"})

    def on_server_pong(self, packet):
        """Handle pong response from server."""
        import time
        if self._ping_start_time is not None:
            elapsed_ms = int((time.time() - self._ping_start_time) * 1000)
            self._ping_start_time = None
            self.sound_manager.play("pingstop.ogg")
            self.speaker.speak(Localization.get("main-ping-result", value=elapsed_ms))

    def on_toggle_table_chat(self, event):
        """Handle F6 to toggle muting table chat."""
        if not self.config_manager or not self.server_id:
            return
        # Get current state
        current_state = self.client_options.get("social", {}).get(
            "mute_table_chat", False
        )
        # Toggle it
        current_state = not current_state
        # Announce
        status = Localization.get("main-table-chat-muted") if current_state else Localization.get("main-table-chat-unmuted")
        self.speaker.speak(status)
        self.modify_option_value("social/mute_table_chat", current_state)

    def on_toggle_global_chat(self, event):
        """Handle Shift+F6 to toggle muting global chat."""
        if not self.config_manager or not self.server_id:
            return
        # Get current state
        current_state = self.client_options.get("social", {}).get(
            "mute_global_chat", False
        )
        # Toggle it
        current_state = not current_state
        # Announce
        status = Localization.get("main-global-chat-muted") if current_state else Localization.get("main-global-chat-unmuted")
        self.speaker.speak(status)
        self.modify_option_value("social/mute_global_chat", current_state)

    # Buffer navigation event handlers

    def on_prev_buffer(self, event):
        """Handle [ key to switch to previous buffer."""
        self.buffer_system.previous_buffer()
        self._announce_buffer_info()

    def on_next_buffer(self, event):
        """Handle ] key to switch to next buffer."""
        self.buffer_system.next_buffer()
        self._announce_buffer_info()

    def on_first_buffer(self, event):
        """Handle Shift+[ to jump to first buffer."""
        self.buffer_system.first_buffer()
        self._announce_buffer_info()

    def on_last_buffer(self, event):
        """Handle Shift+] to jump to last buffer."""
        self.buffer_system.last_buffer()
        self._announce_buffer_info()

    def on_older_message(self, event):
        """Handle , key to move to older message in current buffer."""
        self.buffer_system.move_in_buffer("older")
        self._announce_current_message()

    def on_newer_message(self, event):
        """Handle . key to move to newer message in current buffer."""
        self.buffer_system.move_in_buffer("newer")
        self._announce_current_message()

    def on_oldest_message(self, event):
        """Handle Shift+, to jump to oldest message in buffer."""
        self.buffer_system.move_in_buffer("oldest")
        self._announce_current_message()

    def on_newest_message(self, event):
        """Handle Shift+. to jump to newest message in buffer."""
        self.buffer_system.move_in_buffer("newest")
        self._announce_current_message()

    def _get_localized_buffer_name(self, buffer_name):
        """Get localized name for a standard buffer, or return original if custom."""
        if buffer_name in ["all", "misc", "chats", "activity", "game", "system", "chat"]:
            return Localization.get(f"buffer-name-{buffer_name}")
        return buffer_name

    def on_buffer_mute_toggle(self, event):
        """Handle F4 to toggle mute for current buffer."""
        buffer_name = self.buffer_system.get_current_buffer_name()
        self.buffer_system.toggle_mute(buffer_name)
        is_muted = self.buffer_system.is_muted(buffer_name)

        # Save muted buffers to config
        self._save_muted_buffers()

        # Announce mute status
        localized_name = self._get_localized_buffer_name(buffer_name)
        status = Localization.get("main-status-muted") if is_muted else Localization.get("main-status-unmuted")
        self.speaker.speak(Localization.get("main-buffer-status", name=localized_name, status=status), interrupt=True)

    def _announce_buffer_info(self):
        """Announce current buffer information (matches Legends format)."""
        name, count, position = self.buffer_system.get_buffer_info()
        is_muted = self.buffer_system.is_muted(name)
        mute_status = Localization.get("main-status-muted-suffix") if is_muted else ""
        
        localized_name = self._get_localized_buffer_name(name)
        
        # Format: "{name}{mute_status}. {count} items"
        self.speaker.speak(Localization.get("main-buffer-info", name=localized_name, status=mute_status, count=count), interrupt=True)

    def _announce_current_message(self):
        """Announce the current message in the buffer (matches Legends format)."""
        item = self.buffer_system.get_current_item()
        if item:
            # Just speak the message text, no position info
            self.speaker.speak(item["text"], interrupt=True)
        # If no item, fail silently (don't announce empty buffer)

    def on_char_hook(self, event):
        """Handle character input for game keypresses."""
        focused = wx.Window.FindFocus()

        # SKIP IMMEDIATELY for text controls to avoid breaking IME (Vietnamese Telex)
        # We handle Escape/Enter for these in their specific handlers or TextEnter events
        if isinstance(focused, wx.TextCtrl) or self.current_mode == "edit":
            event.Skip()
            return

        # Only process keybinds when menu list has focus
        if focused != self.menu_list:
            event.Skip()
            return

        key_code = event.GetKeyCode()
        
        # Get modifiers
        modifiers = event.GetModifiers()

        # Map key codes to key names for the server
        key_name = None

        # Handle arrow keys - only send as keybinds if menu is empty
        menu_is_empty = self.menu_list.GetCount() == 0
        if key_code == wx.WXK_UP:
            if menu_is_empty:
                key_name = "up"
            else:
                event.Skip()
                return
        elif key_code == wx.WXK_DOWN:
            if menu_is_empty:
                key_name = "down"
            else:
                event.Skip()
                return
        elif key_code == wx.WXK_LEFT:
            if menu_is_empty:
                key_name = "left"
            else:
                event.Skip()
                return
        elif key_code == wx.WXK_RIGHT:
            if menu_is_empty:
                key_name = "right"
            else:
                event.Skip()
                return
        # Handle function keys
        elif key_code == wx.WXK_F1:
            key_name = "f1"
        elif key_code == wx.WXK_F2:
            # F2 is handled by accelerator table for online list
            # Don't send to server, let it bubble up to the accelerator
            event.Skip()
            return
        elif key_code == wx.WXK_F3:
            key_name = "f3"
        elif key_code == wx.WXK_F4:
            # F4 is handled by accelerator table for buffer mute
            # Don't send to server, let it bubble up to the accelerator
            event.Skip()
            return
        elif key_code == wx.WXK_F5:
            key_name = "f5"
        elif key_code == wx.WXK_ESCAPE or key_code == wx.WXK_BACK:
            if key_code == wx.WXK_BACK and self.current_menu_id == "main_menu":
                event.Skip()
                return
            # Handle escape based on current menu's escape_behavior
            if self.escape_behavior == "select_last_option":
                # Send selection for the last item without actually moving focus
                if self.current_mode == "list" and self.connected:
                    item_count = self.menu_list.GetCount()
                    if item_count > 0:
                        # Play menuenter sound like a normal activation
                        if self.sound_manager:
                            self.sound_manager.play_menuenter()
                        # Build packet with selection (1-based index)
                        packet = {
                            "type": "menu",
                            "menu_id": self.current_menu_id,
                            "selection": item_count,
                        }
                        # Include selection_id for the last item if available
                        last_index = item_count - 1  # 0-based for array access
                        if 0 <= last_index < len(self.current_menu_item_ids):
                            item_id = self.current_menu_item_ids[last_index]
                            if item_id is not None:
                                packet["selection_id"] = item_id
                        self.network.send_packet(packet)
                return
            elif self.escape_behavior == "escape_event":
                # Send explicit escape event to server
                if self.connected:
                    self.network.send_packet(
                        {"type": "escape", "menu_id": self.current_menu_id}
                    )
                return
            # else: "keybind" - fall through to send as normal keybind
            key_name = "escape"
        elif key_code == wx.WXK_SPACE:
            key_name = "space"
        elif key_code == wx.WXK_BACK:
            key_name = "backspace"
        elif key_code == wx.WXK_RETURN or key_code == wx.WXK_NUMPAD_ENTER:
            # Only send Enter as keybind if modifiers are held
            # Plain Enter should activate the menu (handled by MenuList)
            if event.ControlDown() or event.ShiftDown() or event.AltDown():
                key_name = "enter"
        # Handle letter keys (case insensitive)
        elif 65 <= key_code <= 90:  # A-Z
            # Alt+P, M, C, H are handled by accelerator table
            if event.AltDown() and key_code in [ord("P"), ord("M"), ord("C"), ord("H")]:
                event.Skip()
                return
            key_name = chr(key_code).lower()
        # Handle number keys
        elif 48 <= key_code <= 57:  # 0-9
            key_name = chr(key_code)

        # Extract modifier flags
        has_control = (modifiers & wx.MOD_CONTROL) != 0
        has_alt = (modifiers & wx.MOD_ALT) != 0
        has_shift = (modifiers & wx.MOD_SHIFT) != 0

        # Send keybind event to server if we mapped it
        # Don't send letter/number keys when multiletter nav is on (they do navigation)
        # But DO send function keys, escape, space, backspace, and arrow keys (when menu is empty) always
        # Note: F4 is excluded as it's handled by accelerator table for buffer mute
        is_function_key = key_name in [
            "f1",
            "f2",
            "f3",
            "f5",
            "escape",
            "space",
            "backspace",
            "enter",
            "up",
            "down",
            "left",
            "right",
        ]

        # Send if: connected AND (is function key OR multiletter nav is off OR has modifiers)
        should_send = (
            key_name
            and self.connected
            and (
                is_function_key
                or not self.multiletter_enabled
                or has_control
                or has_alt
                or has_shift
            )
        )

        if should_send:
            # Get current menu context
            menu_selection = self.menu_list.GetSelection()
            if menu_selection == wx.NOT_FOUND:
                menu_index = None
                menu_item_id = None
            else:
                menu_index = menu_selection + 1  # Convert to 1-based index for server
                # Get item ID if available
                if 0 <= menu_selection < len(self.current_menu_item_ids):
                    menu_item_id = self.current_menu_item_ids[menu_selection]
                else:
                    menu_item_id = None

            self.network.send_packet(
                {
                    "type": "keybind",
                    "key": key_name,
                    "control": has_control,
                    "alt": has_alt,
                    "shift": has_shift,
                    "menu_id": self.current_menu_id,
                    "menu_index": menu_index,  # 1-based index, or None if nothing selected
                    "menu_item_id": menu_item_id,  # Item ID, or None if not available
                }
            )
            # Don't skip - we handled it
            return

        # Let other keys be processed normally (including Enter on menu)
        event.Skip()

    def on_menu_activate(self, event):
        """Handle menu item activation (Enter/Space/Double-click)."""
        selection = self.menu_list.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        # Send menu event to server with selection index and ID
        if self.connected:
            packet = {
                "type": "menu",
                "selection": selection + 1,  # Server expects 1-indexed
            }
            # Include menu_id if we have one
            if self.current_menu_id:
                packet["menu_id"] = self.current_menu_id
            # Include selection_id if available
            if 0 <= selection < len(self.current_menu_item_ids):
                item_id = self.current_menu_item_ids[selection]
                if item_id is not None:
                    packet["selection_id"] = item_id
            self.network.send_packet(packet)

        event.Skip()

    def set_multiletter_navigation(self, enabled):
        """Set multiletter navigation state (called by server)."""
        self.multiletter_enabled = enabled
        self.menu_list.enable_multiletter_navigation(enabled)

    def set_grid_mode(self, enabled, grid_width=1):
        """Set grid mode navigation state (called by server)."""
        self.grid_enabled = enabled
        self.grid_width = grid_width
        self.menu_list.enable_grid_mode(enabled, grid_width)

    def on_chat_enter(self, event):
        """Handle chat message send."""
        message = self.chat_input.GetValue().strip()
        if not message:
            return
        if message.startswith("/"):
            # Slash commands
            prefix = message[1:].split(" ")[0]
            # Content is everything after the command
            content = message[len(prefix) + 2 :] if len(message) > len(prefix) + 1 else ""
            slash_commands.process_command(prefix, content)
        else:
            # Regular chat (context sensitive: table or lobby)
            self.send_chat_message(message)
        self.chat_input.Clear()

    def send_chat_message(self, message: str):
        """Send chat message to server."""
        if not message:
            return
        self.network.send_packet(
            {"type": "chat", "convo": "local", "message": message}
        )

    # Legacy language methods removed
    # get_language_name, get_language_code, send_table_chat, send_global_chat removed/replaced

    def add_history(self, text, buffer_name="misc", speak_aloud=True):
        """
        Add text to the history window and optionally speak it.

        Args:
            text: The message to add
            buffer_name: Which buffer to add to (default: "misc")
            speak_aloud: Whether to speak the text aloud (default: True)
        """
        # Add to buffer system (automatically adds to "all" as well)
        self.buffer_system.add_item(buffer_name, text)

        # Only update UI if current buffer is not muted
        if not self.buffer_system.is_muted(
            self.buffer_system.get_current_buffer_name()
        ):
            current = self.history_text.GetValue()
            if current and not current.endswith("\n"):
                text = "\n" + text

            # Save current insertion point to prevent auto-scrolling
            old_insertion_point = self.history_text.GetInsertionPoint()

            # Append text to history widget
            self.history_text.AppendText(text + "\n")

            # Restore insertion point (prevents auto-scroll to end)
            self.history_text.SetInsertionPoint(old_insertion_point)

            # Only speak if speak_aloud is True
            if speak_aloud:
                # Speak the text using TTS
                # Use interrupt=False to queue messages without interrupting
                try:
                    self.speaker.speak(text, interrupt=False)
                except Exception:
                    pass

    # List/Edit mode switching methods

    def switch_to_edit_mode(
        self,
        prompt="",
        callback=None,
        default_value="",
        multiline=False,
        read_only=False,
    ):
        """
        Switch from list mode to edit mode.

        Args:
            prompt: Optional prompt text to speak/display
            callback: Optional callback function to call with the entered text
            default_value: Default text to populate the editbox with
            multiline: Whether to use a multiline editbox
            read_only: Whether the editbox is read-only
        """
        if self.current_mode == "edit":
            return  # Already in edit mode

        # Hide menu list and label
        self.menu_list.Hide()
        self.menu_label.Hide()

        # Set the edit label to the prompt
        if prompt:
            self.edit_label.SetLabel(prompt)
        else:
            self.edit_label.SetLabel("&Edit")

        # Choose which edit control to use
        if multiline:
            self.edit_input.Hide()
            self.edit_input_multiline.Show()
            self.edit_input_multiline.Clear()
            self.edit_input_multiline.SetValue(default_value)
            self.edit_input_multiline.SetEditable(not read_only)
            self.edit_input_multiline.SetFocus()
            self.edit_input_multiline.SelectAll()
            self.current_edit_multiline = True
        else:
            self.edit_input_multiline.Hide()
            self.edit_input.Show()
            self.edit_input.Clear()
            self.edit_input.SetValue(default_value)
            self.edit_input.SetEditable(not read_only)
            self.edit_input.SetFocus()
            self.edit_input.SelectAll()
            self.current_edit_multiline = False

        self.edit_label.Show()

        self.current_mode = "edit"
        self.edit_mode_callback = callback
        self.current_edit_read_only = read_only

        # Don't speak prompt - screen reader will announce it when focusing the editbox

    def switch_to_list_mode(self):
        """Switch from edit mode back to list mode."""
        if self.current_mode == "list":
            return  # Already in list mode

        # Hide edit inputs and label
        self.edit_input.Hide()
        self.edit_input_multiline.Hide()
        self.edit_label.Hide()

        # Show menu list and label
        self.menu_list.Show()
        self.menu_label.Show()
        self.menu_list.SetFocus()

        self.current_mode = "list"
        self.edit_mode_callback = None

    def on_edit_enter(self, event):
        """Handle Enter key in edit mode input."""
        text = self.edit_input.GetValue().strip()

        # For read-only editboxes, Enter just closes them
        # For editable editboxes, Enter submits the value
        if self.edit_mode_callback:
            self.edit_mode_callback(text)
        else:
            # Default behavior: just show what was entered
            self.add_history(f"Entered: {text}")

        # Switch back to list mode
        self.switch_to_list_mode()

    def on_edit_key_down(self, event):
        """Handle key down events for edit inputs (Escape handling)."""
        key_code = event.GetKeyCode()
        
        if key_code == wx.WXK_ESCAPE:
             if self.edit_mode_callback:
                 self.edit_mode_callback("")
             self.switch_to_list_mode()
             return

        event.Skip()

    def on_edit_char(self, event):
        """Handle character input in edit mode to play typing sounds."""
        import random

        key_code = event.GetKeyCode()

        # Escape is handled in on_edit_key_down

        # Only play typing sounds for printable characters (not Enter, Backspace, etc.)
        # Don't play if read-only or if user has disabled typing sounds
        if 32 <= key_code <= 126:  # Printable ASCII range
            should_play = not self.current_edit_read_only and self.client_options.get(
                "interface", {}
            ).get("play_typing_sounds", True)
            if should_play:
                # Randomly pick typing1.ogg through typing4.ogg
                sound_num = random.randint(1, 4)
                sound_name = f"typing{sound_num}.ogg"
                self.sound_manager.play(sound_name, volume=0.5)

        # Let the event continue to process normally
        event.Skip()

    def on_edit_multiline_char(self, event):
        """Handle character input in multiline edit mode."""
        import random

        key_code = event.GetKeyCode()

        # Escape is handled in on_edit_key_down

        # Check for Enter key
        if key_code == wx.WXK_RETURN:
            # For read-only editboxes, plain Enter closes them
            if self.current_edit_read_only:
                text = self.edit_input_multiline.GetValue()
                if self.edit_mode_callback:
                    self.edit_mode_callback(text)
                self.switch_to_list_mode()
                return  # Don't process the Enter key

            # For editable editboxes, behavior depends on invert_multiline_enter_behavior
            if not self.client_options.get("interface", {}).get(
                "invert_multiline_enter_behavior", False
            ):
                # Default behavior: Enter submits, Shift/Ctrl+Enter adds newline
                if not event.ShiftDown() and not event.ControlDown():
                    # Plain Enter submits
                    text = self.edit_input_multiline.GetValue()
                    if self.edit_mode_callback:
                        self.edit_mode_callback(text)
                    self.switch_to_list_mode()
                    return  # Don't process the Enter key
                # Shift/Ctrl+Enter adds newline (falls through to Skip())
            else:
                # Swapped behavior: Enter adds newline, Shift/Ctrl+Enter submits
                if event.ShiftDown() or event.ControlDown():
                    # Shift/Ctrl+Enter submits
                    text = self.edit_input_multiline.GetValue()
                    if self.edit_mode_callback:
                        self.edit_mode_callback(text)
                    self.switch_to_list_mode()
                    return  # Don't process the Enter key
                # Plain Enter adds newline (falls through to Skip())

        # Play typing sounds for printable characters (not Enter, Backspace, etc.)
        # Don't play if read-only or if user has disabled typing sounds
        if 32 <= key_code <= 126:  # Printable ASCII range
            should_play = not self.current_edit_read_only and self.client_options.get(
                "interface", {}
            ).get("play_typing_sounds", True)
            if should_play:
                # Randomly pick typing1.ogg through typing4.ogg
                sound_num = random.randint(1, 4)
                sound_name = f"typing{sound_num}.ogg"
                self.sound_manager.play(sound_name, volume=0.5)

        # Allow all other keys (including plain Enter for newlines in editable mode)
        event.Skip()

    # Sound and music methods (for server calls via CallAfter)

    def play_sound(self, sound_name, volume=1.0, pan=0.0, pitch=1.0):
        """
        Play a sound effect (called via CallAfter for non-blocking).

        Args:
            sound_name: Name of sound file (in sounds/ folder)
            volume: Volume 0.0-1.0
            pan: Pan -1.0 to 1.0
            pitch: Pitch multiplier
        """
        wx.CallAfter(self.sound_manager.play, sound_name, volume, pan, pitch)

    def play_music(
        self, music_name: str, looping: bool = True, fade_out_old: bool = True
    ):
        """
        Play background music (called via CallAfter for non-blocking).

        Args:
            music_name: Name of music file (in sounds/ folder)
            looping: whether to loop the music
            fade_out_old: Whether to fade out current music
        """
        wx.CallAfter(self.sound_manager.music, music_name, looping, fade_out_old)

    def stop_music(self, fade=True):
        """Stop background music."""
        wx.CallAfter(self.sound_manager.stop_music, fade)

    def set_music_volume(self, volume):
        """Set music volume 0.0-1.0."""
        wx.CallAfter(self.sound_manager.set_music_volume, volume)

    def set_menuclick_sound(self, sound_name):
        """Set the menu click sound (server command)."""
        self.sound_manager.set_menuclick_sound(sound_name)

    def set_menuenter_sound(self, sound_name):
        """Set the menu enter/activate sound (server command)."""
        self.sound_manager.set_menuenter_sound(sound_name)

    # Network methods

    def _auto_connect(self):
        """Auto-connect to server using login credentials."""
        username = self.credentials.get("username", "Guest")
        password = self.credentials.get("password", "")
        server_url = self.credentials.get("server_url", "wss://playaural.ddt.one")

        # Play connection loop sound
        self.sound_manager.music("connectloop.ogg")

        self.add_history(Localization.get("main-connecting-to", url=server_url))
        if self.network.connect(server_url, username, password, client_version=VERSION):
            self.add_history(Localization.get("main-connecting-as", username=username))
            # Start timeout check
            wx.CallLater(5000, self._check_connection_timeout)
        else:
            self._show_connection_error(Localization.get("main-connection-failed"))

    def _check_connection_timeout(self):
        """Check if connection succeeded within timeout period."""
        # Don't timeout if we're in the middle of reconnecting (either expected or silent)
        if not self.connected and not self.expecting_reconnect and not self.is_reconnecting:
            self._show_connection_error(
                Localization.get("main-connection-timeout")
            )

    def on_connection_lost(self):
        """Handle connection loss."""
        # If we are quitting/exiting, ignore any connection loss events logic
        if self.quitting:
            return

        self.connected = False
        self.current_menu_id = None
        self.current_menu_state = None
        
        # If explicit disconnect (e.g. kicked or logged out), normal error flow
        if self.disconnect_reason:
             self._show_connection_error(Localization.get("main-disconnected"))
             return

        # Don't show error if we're expecting a server requested reconnect (restart)
        if self.expecting_reconnect:
            # Server driven restart logic handled in on_server_disconnect
            return

        # Unexpected disconnect - Try smart reconnect
        if not self.is_reconnecting:
            self.is_reconnecting = True
            import time
            self.reconnect_start_time = time.time()
            self.speaker.speak(Localization.get("main-attempting-reconnect"), interrupt=True)
            self._attempt_silent_reconnect()
        else:
            # We are already attempting, but maybe connection failed immediately
            # Just let the loop continue
            pass

    def _attempt_silent_reconnect(self):
        """Attempt to reconnect silently in background."""
        import time
        if not self.is_reconnecting:
            return

        # Check timeout
        elapsed = time.time() - self.reconnect_start_time
        if elapsed > self.max_silent_reconnect_duration:
             self.is_reconnecting = False
             self._show_connection_error(Localization.get("main-connection-timeout"))
             return
             
        # Attempt connection
        server_url = self.credentials.get("server_url")
        username = self.credentials.get("username")
        password = self.credentials.get("password", "")
        
        if server_url and username:
            # Attempt to connect - if returns False, it means we are already connecting
            # so we just wait and check status later
            if not self.network.connect(server_url, username, password):
                 # Already connecting or error, just wait
                 pass
            
            # Check status after a delay
            wx.CallLater(1000, self._check_reconnect_status)

    def _check_reconnect_status(self):
        """Check if silent reconnect succeeded."""
        if not self.is_reconnecting:
            return

        if self.network.connected:
             # Success!
             self.is_reconnecting = False
             self.connected = True
             self.speaker.speak(Localization.get("main-connected"), interrupt=True)
        else:
             # Just signal to try again (which will check timeouts and existing connection attempts)
             wx.CallLater(1000, self._attempt_silent_reconnect)

    def on_server_disconnect(self, packet):
        """Handle server disconnect packet."""
        should_reconnect = packet.get("reconnect", False)

        if should_reconnect:
            # Server is restarting, reconnect after 3 seconds
            self.expecting_reconnect = True
            self.speaker.speak(
                Localization.get("main-reconnecting-in-3s"), interrupt=False
            )

            def reconnect():
                # Attempt reconnection
                server_url = self.credentials.get("server_url")
                username = self.credentials.get("username")
                if server_url and username:
                    self.speaker.speak(Localization.get("main-reconnecting"), interrupt=False)
                    # Disconnect old connection first - this will trigger on_connection_lost which handles retry
                    self.network.disconnect()
            
            wx.CallLater(3000, reconnect)
            return

        # Explicit disconnect, close the client
        reason = packet.get("reason", "")
        
        # Internal codes: EXIT
        if reason == "exit":
            self.speaker.speak(Localization.get("goodbye"), interrupt=True)
            
            # Hard exit after 1s to allow speech
            def hard_exit():
                import sys
                self.Destroy()
                sys.exit(0)
            
            wx.CallLater(1000, hard_exit)
            return

        # Localize specific reasons
        if reason == "logged-out":
            reason = Localization.get("logged-out")
            # Don't speak "Disconnected" for logout, just "Goodbye"
        
        self.disconnect_reason = reason
        self.quitting = True
        self.is_reconnecting = False
        self.expecting_reconnect = False
        
        if reason != Localization.get("logged-out"):
            self.speaker.speak(Localization.get("main-disconnected"), interrupt=False)
        
        if reason:
             self.speaker.speak(reason, interrupt=False)
             
        # Also trigger the error popup immediately to stop connection loss race
        self._show_connection_error(Localization.get("main-disconnected"))

    def on_force_exit(self, packet):
        """Handle forced exit command from server."""
        try:
            self.quitting = True
            
            try:
                self.speaker.speak(Localization.get("goodbye"), interrupt=True)
            except Exception:
                pass
            
            def hard_exit():
                try:
                    # Try graceful exit first
                    import sys
                    self.Destroy()
                    sys.exit(0)
                except Exception:
                    # Fallback to hard process termination
                    import os
                    os._exit(0)
                finally:
                    # Should not assume we get here, but just in case
                    import os
                    os._exit(0)
                
            # Give 1s for speech then kill process
            wx.CallLater(1000, hard_exit)
            
        except Exception:
             # If setup fails, die immediately
             import os
             os._exit(0)

    def on_update_preference(self, packet):
        """Handle preference update from server."""
        key = packet.get("key") # e.g. "audio/music_volume"
        value = packet.get("value")
        
        if not key or value is None:
            return

        # Update local config (and save)
        self.config_manager.set_client_option(key, value, create_mode=True)
        
        # Apply changes immediately
        if key == "audio/music_volume":
             if self.sound_manager:
                 self.sound_manager.set_music_volume(value / 100.0)
        elif key == "audio/ambience_volume":
             if self.sound_manager:
                 self.sound_manager.set_ambience_volume(value / 100.0)
        
        # Reload full options to be safe
        self.client_options = self.config_manager.get_client_options(self.server_id)

    def _do_reconnect(self, server_url, username, password):
        """Actually perform the reconnection attempt."""
        self.reconnect_attempts += 1

        # Check if already connected (successful)
        if self.connected:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            return

        # Check if exceeded max attempts
        if self.reconnect_attempts > self.max_reconnect_attempts:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            self.speaker.speak(
                "Failed to reconnect after multiple attempts.", interrupt=False
            )
            self.Close()
            return

        # Attempt to connect
        self.add_history(
            f"Reconnecting as {username}... (attempt {self.reconnect_attempts})"
        )
        self.network.disconnect()

        if self.network.connect(server_url, username, password):
            # Wait 3 seconds then check again
            wx.CallLater(
                3000, lambda: self._do_reconnect(server_url, username, password)
            )
        elif self.network.is_connecting():
            # Connection is in progress (slow connection), wait more
            wx.CallLater(
                3000, lambda: self._do_reconnect(server_url, username, password)
            )
        else:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            self.speaker.speak("Failed to reconnect.", interrupt=False)
            self.Close()

    def _show_connection_error(self, message):
        """Show error modal and quit application."""
        self.quitting = True
        self.is_reconnecting = False

        # Stop any music
        self.sound_manager.stop_music(fade=False)

        # Build error message
        # Use provided message only - do not append stale last_server_message
        error_body = message
        
        # If we have a specific disconnect reason stored, append it
        if self.disconnect_reason:
             error_body += f"\n\n{self.disconnect_reason}"

        error_body += "\n\n" + Localization.get("common-app-closing")

        # Show error dialog
        wx.MessageBox(error_body, Localization.get("main-connection-error-title"), wx.OK | wx.ICON_ERROR)

        # Quit the application
        try:
            self.Destroy()
            import sys
            sys.exit(0)
        except Exception:
            import os
            os._exit(0)

    def restart_application(self):
        """Restart the client application."""
        import os
        import sys
        import subprocess

        self.speaker.speak(Localization.get("main-restarting"), interrupt=True)
        time.sleep(1.0) # Give time to speak

        try:
            # Determine how to restart
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                cmd = [sys.executable]
            else:
                # Running from source
                # Use sys.executable and current arguments
                cmd = [sys.executable] + sys.argv

            # Launch new instance
            subprocess.Popen(cmd)
            
            # Close current
            self.Destroy()
            sys.exit(0)
        except Exception as e:
            print(f"Failed to restart: {e}")
            self.Close()

    # Server packet handlers

    def on_authorize_success(self, packet):
        """Handle authorization success from server."""
        # Reset reconnect flags on success instead of restarting
        if self.is_reconnecting or self.expecting_reconnect:
            self.is_reconnecting = False
            self.expecting_reconnect = False
            self.reconnect_attempts = 0

        self.connected = True
        version = packet.get("version", "unknown")
        locale = packet.get("locale", "en")

        # Save locale to config
        self.config_manager.profiles["client_options_defaults"]["interface_language"] = locale
        self.config_manager.save_profiles()
        
        # Apply preferences from server
        preferences = packet.get("preferences", {})
        if preferences:
            # Map server preference keys to client config keys
            # Server sends flat dict (e.g. "music_volume"), Client uses paths (e.g. "audio/music_volume")
            
            # Audio
            if "music_volume" in preferences:
                vol = preferences["music_volume"]
                self.config_manager.set_client_option("audio/music_volume", vol, create_mode=True)
                if self.sound_manager:
                    self.sound_manager.set_music_volume(vol / 100.0)
                    
            if "ambience_volume" in preferences:
                vol = preferences["ambience_volume"]
                self.config_manager.set_client_option("audio/ambience_volume", vol, create_mode=True)
                if self.sound_manager:
                    self.sound_manager.set_ambience_volume(vol / 100.0)
            
            # Social
            if "mute_global_chat" in preferences:
                self.config_manager.set_client_option("social/mute_global_chat", preferences["mute_global_chat"], create_mode=True)
            if "mute_table_chat" in preferences:
                self.config_manager.set_client_option("social/mute_table_chat", preferences["mute_table_chat"], create_mode=True)
                
            # Interface
            if "play_typing_sounds" in preferences:
                self.config_manager.set_client_option("interface/play_typing_sounds", preferences["play_typing_sounds"], create_mode=True)
            if "invert_multiline_enter_behavior" in preferences:
                self.config_manager.set_client_option("interface/invert_multiline_enter_behavior", preferences["invert_multiline_enter_behavior"], create_mode=True)
            
            # Dice (Game specific options often handled by server state, but good to store)
            if "clear_kept_on_roll" in preferences:
                 # Client might not use this directly yet, but store it
                 self.config_manager.set_client_option("game/clear_kept_on_roll", preferences["clear_kept_on_roll"], create_mode=True)

        # Verify if we need to reload localization (though UI is already built)
        # For now, it will apply on next restart, which is what the user asked for.

        # Stop connection loop and play welcome sound
        self.sound_manager.stop_music(fade=False)
        self.sound_manager.play("welcome.ogg", volume=1.0)

        # Check for updates
        update_info = packet.get("update_info")
        if update_info:
            server_ver = update_info.get("version")
            if server_ver and server_ver != VERSION:
                wx.CallAfter(self._prompt_update, update_info)

        # Notify user (but don't speak redundantly)
        # self.speaker.speak(Localization.get("main-connected"))
        self.add_history(Localization.get("main-connected-version", version=version))

    def _prompt_update(self, update_info):
        """Prompt user to update."""
        self.sound_manager.play("update_alert.ogg")
        version = update_info.get("version")
        result = wx.MessageBox(
            Localization.get("update-available-message", version=version),
            Localization.get("update-available-title"),
            wx.YES_NO | wx.ICON_QUESTION
        )
        if result == wx.YES:
            # Create modal progress dialog with Cancel button
            self.update_dialog = wx.ProgressDialog(
                Localization.get("update-available-title"),
                Localization.get("update-downloading", percent=0),
                maximum=100,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT
            )
            
            # Stop existing music and play download loop
            self.sound_manager.stop_music(fade=False)
            self.sound_manager.music("download_loop.ogg", looping=True, fade_out_old=False)
            
            # Start download in thread
            import threading
            self.download_thread = threading.Thread(target=self._download_update, args=(update_info,), daemon=True)
            self.download_thread.start()
        else:
            # Mandatory update - exit if refused by initial prompt
            # (If they cancel during download, we also close)
            self.Close()
            wx.GetApp().ExitMainLoop()

    def _download_update(self, update_info):
        """Download update file."""
        # Imports already at module level

        url = update_info.get("url")
        import tempfile
        
        url = update_info.get("url")
        # Use temp directory for download to avoid permission issues
        temp_dir = tempfile.gettempdir()
        target_zip = os.path.join(temp_dir, f"playaural_update_{int(time.time())}.zip")
        self.download_cancelled = False
        
        try:
            # self.speaker.speak(Localization.get("update-downloading", percent=0))
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size_header = response.headers.get("content-length")
            total_size = int(total_size_header) if total_size_header else 0
            
            block_size = 1024 * 64 # 64KB blocks
            downloaded = 0
            
            last_percent = 0
            last_update_check = 0

            with open(target_zip, "wb") as f:
                for data in response.iter_content(block_size):
                    if self.download_cancelled:
                        break
                        
                    downloaded += len(data)
                    f.write(data)
                    
                    # Update UI in main thread
                    # For performance, don't flood the UI queue if blocks are small/fast
                    current_time = time.time()
                    if current_time - last_update_check > 0.1: # Update max 10 times per second
                        last_update_check = current_time
                        
                        keep_going = True
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            # Call Update on main thread and get result (requires passing a callback or using a shared flag? 
                            # Update returns (continue, skip). But we can't get return value via CallAfter easily
                            # So we define a wrapper
                            
                            def update_modal(p, msg):
                                if not self.update_dialog: return
                                (cont, skip) = self.update_dialog.Update(p, msg)
                                if not cont:
                                    self.download_cancelled = True
                            
                            if percent > last_percent:
                                wx.CallAfter(update_modal, percent, Localization.get("update-downloading", percent=percent))
                                
                                if percent % 10 == 0:
                                    wx.CallAfter(self.speaker.speak, Localization.get("update-downloading", percent=percent))
                                
                                last_percent = percent
                        else:
                            # Indeterminate size
                            downloaded_mb = downloaded / (1024*1024)
                            msg = f"Downloading... {downloaded_mb:.2f} MB"
                            
                            def pulse_modal(msg):
                                if not self.update_dialog: return
                                (cont, skip) = self.update_dialog.Pulse(msg)
                                if not cont:
                                    self.download_cancelled = True

                            wx.CallAfter(pulse_modal, msg)
            
            if self.download_cancelled:
                # Cleanup
                f.close() # Ensure closed
                if os.path.exists(target_zip):
                    try:
                        os.remove(target_zip)
                    except:
                        pass
                
                wx.CallAfter(self.sound_manager.stop_music)
                wx.CallAfter(self.update_dialog.Destroy)
                # If cancelled mandatory update, close app?
                # User request: "khi hủy sẽ xóa tệp tạm". Implies they return to game or close?
                # Mandatory update usually implies "Update or Die". 
                # If I let them cancel, they stay on old version?
                # The user said "cho phép người dùng hủy".
                # If I let them cancel, do I exit app?
                # User didn't specify. But "Mandatory" logic (lines 1339) implies they must update.
                # However, maybe they want to cancel to try again later?
                # I will Close App if cancelled, consistent with mandatory policy.
                wx.CallAfter(wx.MessageBox, Localization.get("update-cancelled"), Localization.get("main-options-error-title"), wx.OK)
                wx.CallAfter(self.Close)
                wx.CallAfter(wx.GetApp().ExitMainLoop)
                return

            # Download complete
            wx.CallAfter(self.update_dialog.Update, 100, Localization.get("update-complete"))
            wx.CallAfter(self.sound_manager.stop_music, fade=True)
            wx.CallAfter(self.sound_manager.play, "update_complete.ogg")
            wx.CallAfter(self.speaker.speak, Localization.get("update-complete"))
            
            time.sleep(3) # Wait for sound to finish
            
            wx.CallAfter(self.update_dialog.Destroy)
            
            # Launch updater
            self._launch_updater(target_zip)
            
        except Exception as e:
            wx.CallAfter(self.sound_manager.stop_music)
            if self.update_dialog:
                 wx.CallAfter(self.update_dialog.Destroy)
            wx.CallAfter(self.speaker.speak, Localization.get("update-error", error=str(e)))
            wx.CallAfter(wx.MessageBox, Localization.get("update-error", error=str(e)), "Error", wx.OK | wx.ICON_ERROR)
            # Cleanup broken zip
            if os.path.exists(target_zip):
                 try:
                     os.remove(target_zip)
                 except: pass

    def _launch_updater(self, zip_path):
        """Launch the standalone updater."""
        import os
        import sys
        import subprocess

        try:
            # Check if updater.py exists (running from source) or internal
            updater_script = os.path.join(os.getcwd(), "client", "updater.py")
            pid = os.getpid()
            
            if os.path.exists(updater_script):
                # Running from source, call python
                python_exe = sys.executable
                exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "PlayAural.exe"
                cmd = [python_exe, updater_script, "--zip", zip_path, "--target", os.getcwd(), "--exe", "PlayAural.exe", "--pid", str(pid)]
                subprocess.Popen(cmd)
            else:
                # Running frozen (compiled)
                # Assume updater.exe is in the same directory as the main executable
                updater_exe = os.path.join(os.path.dirname(sys.executable), "updater.exe")
                
                # Check if it exists
                if not os.path.exists(updater_exe):
                     # Try internal folder just in case (fallback)
                     updater_exe = os.path.join(os.path.dirname(sys.executable), "_internal", "updater.exe")
                
                if os.path.exists(updater_exe):
                    # Copy to temp to avoid file locking on overwrite
                    import shutil
                    import tempfile
                    
                    temp_dir = tempfile.gettempdir()
                    # Use unique name to avoid conflicts or permission issues on temp
                    temp_updater = os.path.join(temp_dir, f"playaural_updater_{pid}.exe")
                    
                    try:
                         shutil.copy2(updater_exe, temp_updater)
                         updater_exe = temp_updater
                    except Exception as e:
                         # Fallback to local if copy fails (though unlikely)
                         print(f"Failed to copy updater to temp: {e}")
                    
                    cmd = [updater_exe, "--zip", zip_path, "--target", os.path.dirname(sys.executable), "--exe", os.path.basename(sys.executable), "--pid", str(pid)]
                    subprocess.Popen(cmd)
                else:
                     wx.CallAfter(wx.MessageBox, f"Updater not found at: {updater_exe}", "Error", wx.OK | wx.ICON_ERROR)
                     return
            
            # Quit immediately
            wx.CallAfter(self.Close)
            wx.CallAfter(wx.GetApp().ExitMainLoop)
            os._exit(0)
            
        except Exception as e:
            wx.CallAfter(wx.MessageBox, f"Failed to launch updater: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_update_locale(self, packet):
        """Handle update_locale packet from server."""
        locale = packet.get("locale", "en")
        self.config_manager.profiles["client_options_defaults"]["interface_language"] = locale
        self.config_manager.save_profiles()
        
        # Notify user that restart is required if locale changed
        if locale != Localization._locale:
            wx.MessageBox(
                Localization.get("options-restart-required-message"),
                Localization.get("options-restart-required-title"),
                wx.OK | wx.ICON_INFORMATION,
            )

    def on_open_server_options(self, packet):
        """Handle open server options packet from server.

        #This handler is for
        server-side options like battle reserves and account settings.
        """
        self.server_options = packet.get("options", {})

    def on_update_options_lists(self, packet):
        """Handle update_options_lists packet from server.

        Automatically updates client options to include new games and languages
        without requiring the user to open the options dialog.
        """
        self.games_list = packet.get("games", [])
        self.lang_codes = packet.get("languages", {})
        if not self.config_manager or not self.server_id:
            return

        updated = False

        languages = tuple(self.lang_codes.values())
        # Update games in both default profile and server profile
        if self.games_list:
            # Update default profile
            default_local_table = self.config_manager.profiles[
                "client_options_defaults"
            ].setdefault("local_table", {})
            default_creation_notifications = default_local_table.setdefault("creation_notifications", {})
            for game_info in self.games_list:
                game_name = game_info["name"]
                if game_name not in default_creation_notifications:
                    default_creation_notifications[game_name] = True
                    updated = True

            # Update server profile
            if "servers" in self.config_manager.profiles and self.server_id in self.config_manager.profiles["servers"]:
                server_overrides = self.config_manager.profiles["servers"][
                    self.server_id
                ].setdefault("options_overrides", {})
                server_local_table = server_overrides.setdefault("local_table", {})
                server_creation_notifications = server_local_table.setdefault(
                    "creation_notifications", {}
                )
                for game_info in self.games_list:
                    game_name = game_info["name"]
                    if game_name not in server_creation_notifications:
                        server_creation_notifications[game_name] = True
                        updated = True

        # Update languages in both default profile and server profile
        # Rebuild dicts to match server order (alphabetical ascending)
        if languages:
            # Update default profile - rebuild to match server order
            default_social = self.config_manager.profiles[
                "client_options_defaults"
            ].setdefault("social", {})
            default_lang_subscriptions = default_social.get(
                "language_subscriptions", {}
            )
            new_default_subscriptions = {}
            for language in languages:
                # Preserve existing value or default to False
                new_default_subscriptions[language] = default_lang_subscriptions.get(language, False)
            # Update if keys changed (order or new languages added)
            if list(new_default_subscriptions.keys()) != list(default_lang_subscriptions.keys()):
                default_social["language_subscriptions"] = new_default_subscriptions
                updated = True

            # Update server profile - rebuild to match server order
            if self.server_id in self.config_manager.profiles["servers"]:
                server_overrides = self.config_manager.profiles["servers"][
                    self.server_id
                ].setdefault("options_overrides", {})
                social_overrides = server_overrides.setdefault("social", {})
                lang_subscriptions = social_overrides.get(
                    "language_subscriptions", {}
                )
                new_subscriptions = {}
                for language in languages:
                    # Preserve existing value or default to False
                    new_subscriptions[language] = lang_subscriptions.get(language, False)
                # Update if keys changed (order or new languages added)
                if list(new_subscriptions.keys()) != list(lang_subscriptions.keys()):
                    social_overrides["language_subscriptions"] = new_subscriptions
                    updated = True

        # Save if any changes were made
        if updated:
            self.config_manager.save_profiles()
            # Reload client options to reflect the changes
            self.client_options = self.config_manager.get_client_options(self.server_id)

        # Send client options to server after update_options_lists is complete
        # (this ensures migration and options list updates are both finished)
        self.send_client_options_to_server()

    def send_client_options_to_server(self):
        """Send server profile client options to the server.

        Sends only the server-specific options (not defaults) to inform
        the server of the client's preferences.
        """
        if not self.connected or not self.config_manager or not self.server_id:
            return

        # Get server profile options (defaults + overrides merged)
        options = self.config_manager.get_client_options(self.server_id)

        self.network.send_packet({
            "type": "client_options",
            "options": options,
        })

    def on_open_client_options(self, packet):
        """Handle server request to open client options dialog (includes server nickname)."""
        if not self.config_manager or not self.server_id:
            wx.MessageBox(
                Localization.get("main-options-error"), Localization.get("main-options-error-title"), wx.OK | wx.ICON_ERROR
            )
            return

        # Import the dialog
        from .options_dialog import ClientOptionsDialog

        # Open client-side dialog (pass client_options for in-memory updates)
        # Games and languages will be read from config (already populated at login)
        dlg = ClientOptionsDialog(
            self,
            self.config_manager,
            self.server_id,
            self.lang_codes,
            self.sound_manager,
            self.client_options,
        )

        dlg.Destroy()
        # Send updated client options to server after saving
        self.send_client_options_to_server()

    def on_server_speak(self, packet):
        """Handle speak packet from server."""
        text = packet.get("text", "")
        buffer_name = packet.get(
            "buffer", "misc"
        )  # Optional buffer parameter, defaults to "misc"
        is_muted = packet.get(
            "muted", False
        )  # Check if message should be muted (no TTS)

        if text:
            # Store last message for error display on disconnect
            self.last_server_message = text
            # Add to history regardless of mute status
            self.add_history(text, buffer_name, speak_aloud=(not is_muted))

    def on_receive_chat(self, packet):
        """Handle chat packet from server."""
        convo = packet.get("convo")
        lang = packet.get("language")
        # For now all chats are in English
        same_user = packet.get("sender") == self.credentials["username"]
        """comment out all of this code for now
        if lang not in self.lang_codes.values():
            lang = "Other"
        # If language matches, ignore subscription tracking
        if (
            not same_user
            and lang != self.client_options["social"]["chat_input_language"]
        ):
            if convo == "global" or (
                convo == "local"
                and self.client_options["social"][
                    "include_language_filters_for_table_chat"
                ]
            ):
                # Check if the user is ignoring this language
                if not self.client_options["social"]["language_subscriptions"][lang]:
                    return
        end this comment"""
        if convo == "global":
            message = Localization.get("chat-global", player=packet.get("sender"), message=packet.get("message"))
        elif convo == "announcement":
            message = f"{Localization.get('system-announcement')}: {packet.get('message')}"
        else:
            message = Localization.get("chat-local", player=packet.get("sender"), message=packet.get("message"))
        # Convo doesn't support muting, or the mute flag is disabled
        if True:
            """(
            same_user
            or convo not in {"global", "local"}
            or not self.client_options["social"][f"mute_{convo}_chat"]
        ):"""
            sound = "chat"
            if convo == "local":
                sound += "local"
            elif convo == "announcement":
                sound = "notify"
                
            self.sound_manager.play(sound + ".ogg")
            self.speaker.speak(message)
        self.add_history(message, "chat", False)

    def on_server_play_sound(self, packet):
        """Handle play_sound packet from server."""
        sound = packet.get("name", packet.get("sound", ""))  # Server sends "name"
        volume = packet.get("volume", 100) / 100.0  # Convert 0-100 to 0.0-1.0
        pan = packet.get("pan", 0) / 100.0  # Convert -100 to 100 to -1.0 to 1.0
        pitch = packet.get("pitch", 100) / 100.0  # Convert 0-200 to 0.0-2.0
        if sound:
            self.sound_manager.play(sound, volume, pan, pitch)

    def on_server_play_music(self, packet):
        """Handle play_music packet from server."""
        music = packet.get("name", packet.get("music", ""))  # Server sends "name"
        looping = packet.get(
            "looping", True
        )  # Default to True for backwards compatibility
        if music:
            self.sound_manager.music(music, looping=looping)

    def on_server_play_ambience(self, packet):
        """Handle play_ambience packet from server."""
        intro = packet.get("intro")
        loop = packet.get("loop")
        outro = packet.get("outro")
        if loop:  # Loop is required
            self.sound_manager.ambience(intro, loop, outro)

    def on_server_stop_ambience(self, packet):
        """Handle stop_ambience packet from server."""
        self.sound_manager.stop_ambience()

    def on_server_add_playlist(self, packet):
        """Handle add_playlist packet from server."""
        playlist_id = packet.get(
            "playlist_id", "music_playlist"
        )  # Default to backward-compatible ID
        tracks = packet.get("tracks", [])
        audio_type = packet.get("audio_type", "music")  # Default to music
        shuffle_tracks = packet.get("shuffle_tracks", False)
        repeats = packet.get("repeats", 1)  # Default to 1 repeat
        auto_start = packet.get("auto_start", True)
        auto_remove = packet.get("auto_remove", True)  # Default to True
        if tracks:
            self.sound_manager.add_playlist(
                playlist_id,
                tracks,
                audio_type,
                shuffle_tracks,
                repeats,
                auto_start,
                auto_remove,
            )

    def on_server_start_playlist(self, packet):
        """Handle start_playlist packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        playlist = self.sound_manager.get_playlist(playlist_id)
        if playlist and not playlist.is_active:
            playlist.is_active = True
            playlist._play_next_track()

    def on_server_remove_playlist(self, packet):
        """Handle remove_playlist packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        self.sound_manager.remove_playlist(playlist_id)

    def on_server_get_playlist_duration(self, packet):
        """Handle get_playlist_duration packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        duration_type = packet.get(
            "duration_type", "total"
        )  # "total", "elapsed", or "remaining"
        request_id = packet.get("request_id")

        playlist = self.sound_manager.get_playlist(playlist_id)
        duration = 0

        if playlist:
            if duration_type == "total":
                result = playlist.get_total_duration()
                duration = result if result is not None else 0
            elif duration_type == "elapsed":
                duration = playlist.get_elapsed_duration()
            elif duration_type == "remaining":
                duration = playlist.get_remaining_duration()

        # Send response back to server
        if request_id:
            response = {
                "type": "playlist_duration_response",
                "request_id": request_id,
                "playlist_id": playlist_id,
                "duration_type": duration_type,
                "duration": duration,
            }
            self.network.send_packet(response)

    def on_table_create(self, packet):
        host = packet.get("host")
        game = packet.get("game")
        if not self.client_options["local_table"]["creation_notifications"][game]:
            return
        self.sound_manager.play("notify.ogg")
        self.add_history(f"{host} is hosting {game}.", "activity")

    def compute_menu_diff_by_id(self, old_items, new_items, old_ids, new_ids):
        """
        Compute minimal operations using item IDs to transform old_items into new_items.
        This is much simpler and more reliable than text-based LCS diffing.

        Returns list of operations: ('insert', index, text), ('delete', index), ('update', index, text)

        Algorithm:
        1. Build maps of IDs to (index, text) for old and new lists
        2. Identify deleted IDs (in old but not new)
        3. Identify inserted IDs (in new but not old)
        4. Identify common IDs that may need text updates
        5. Generate operations accordingly
        """
        operations = []

        # Build ID maps: {id: (index, text)}
        old_map = {}
        for i, (item_id, text) in enumerate(zip(old_ids, old_items)):
            if item_id is not None:
                old_map[item_id] = (i, text)

        new_map = {}
        for i, (item_id, text) in enumerate(zip(new_ids, new_items)):
            if item_id is not None:
                new_map[item_id] = (i, text)

        # Identify deleted, inserted, and common IDs
        old_id_set = set(old_map.keys())
        new_id_set = set(new_map.keys())

        deleted_ids = old_id_set - new_id_set
        inserted_ids = new_id_set - old_id_set
        common_ids = old_id_set & new_id_set

        # Generate delete operations (using old indices)
        for item_id in deleted_ids:
            old_index = old_map[item_id][0]
            operations.append(("delete", old_index))

        # Generate insert and update operations (using new indices)
        for i, (new_id, new_text) in enumerate(zip(new_ids, new_items)):
            if new_id is None:
                continue

            if new_id in inserted_ids:
                # New item - insert it
                operations.append(("insert", i, new_text))
            elif new_id in common_ids:
                # Existing item - check if text changed
                old_text = old_map[new_id][1]
                if old_text != new_text:
                    operations.append(("update", i, new_text))

        return operations

    def compute_menu_diff(self, old_items, new_items, old_ids=None, new_ids=None):
        """
        Compute minimal operations to transform old_items into new_items.
        Returns list of operations: ('insert', index, text), ('delete', index), ('update', index, text)

        If all items have IDs (old_ids and new_ids provided and no None values), use the simpler
        ID-based algorithm. Otherwise fall back to LCS-based text diffing.

        For simplicity and screen reader friendliness:
        - If lists are same length, generate update operations for changed items
        - Otherwise use LCS-based diff for structural changes
        """
        # Check if we can use ID-based diffing (all items have IDs)
        if (old_ids is not None and new_ids is not None and
            len(old_ids) == len(old_items) and len(new_ids) == len(new_items) and
            all(item_id is not None for item_id in old_ids) and
            all(item_id is not None for item_id in new_ids)):
            # Use simpler ID-based algorithm
            return self.compute_menu_diff_by_id(old_items, new_items, old_ids, new_ids)

        # Fall back to text-based LCS algorithm
        operations = []

        # Simple case: same length, just update changed items
        if len(old_items) == len(new_items):
            for i in range(len(old_items)):
                if old_items[i] != new_items[i]:
                    operations.append(("update", i, new_items[i]))
            return operations

        # Different lengths: use LCS algorithm for structural changes
        m, n = len(old_items), len(new_items)
        lcs = [[0] * (n + 1) for _ in range(m + 1)]

        # Fill LCS table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if old_items[i - 1] == new_items[j - 1]:
                    lcs[i][j] = lcs[i - 1][j - 1] + 1
                else:
                    lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])

        # Backtrack to generate operations
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and old_items[i - 1] == new_items[j - 1]:
                # Items match - no operation needed
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or lcs[i][j - 1] >= lcs[i - 1][j]):
                # Insert new item
                operations.insert(0, ("insert", j - 1, new_items[j - 1]))
                j -= 1
            else:
                # Delete old item
                operations.insert(0, ("delete", i - 1))
                i -= 1

        return operations

    def apply_menu_diff(self, operations, old_selection):
        """
        Apply diff operations to menu_list while preserving screen reader context.
        Returns new selection index after operations.

        Operations must be applied carefully:
        - Deletes in reverse order (high index to low) to avoid index shifting issues
        - Inserts in forward order
        - Updates in any order
        """
        new_selection = old_selection

        # Separate operations by type
        deletes = [(op[1],) for op in operations if op[0] == "delete"]
        inserts = [op for op in operations if op[0] == "insert"]
        updates = [op for op in operations if op[0] == "update"]

        # Apply deletes in reverse order (highest index first)
        # This prevents index shifting issues
        for (index,) in sorted(deletes, key=lambda x: x[0], reverse=True):
            self.menu_list.Delete(index)
            # Adjust selection if deleting before/at selected item
            if new_selection != wx.NOT_FOUND:
                if index < new_selection:
                    new_selection -= 1
                elif index == new_selection:
                    # Selected item was deleted, select next item (or last if at end)
                    new_selection = min(new_selection, self.menu_list.GetCount() - 1)

        # Apply inserts in forward order
        for op_type, *args in inserts:
            index, text = args
            self.menu_list.Insert(text, index)
            # Adjust selection if inserting before selected item
            if new_selection != wx.NOT_FOUND and index <= new_selection:
                new_selection += 1

        # Apply updates (order doesn't matter)
        for op_type, *args in updates:
            index, text = args
            self.menu_list.SetString(index, text)

        return new_selection

    def on_server_menu(self, packet):
        """Handle menu packet from server."""
        items_raw = packet.get("items", [])
        menu_id = packet.get("menu_id", None)
        multiletter_enabled = packet.get("multiletter_enabled", True)
        escape_behavior = packet.get("escape_behavior", "keybind")
        position = packet.get("position", None)  # Optional position to move to
        selection_id = packet.get("selection_id", None)  # Optional item ID to focus
        grid_enabled = packet.get("grid_enabled", False)
        grid_width = packet.get("grid_width", 1)

        # Parse items - can be strings or objects with {text, id}
        items = []
        item_ids = []
        for item in items_raw:
            if isinstance(item, dict):
                items.append(item.get("text", ""))
                item_ids.append(item.get("id"))
            else:
                items.append(str(item))
                item_ids.append(None)

        # Save old item IDs before updating (for diff algorithm)
        old_item_ids = getattr(self, 'current_menu_item_ids', [])

        # Store item IDs for later use
        self.current_menu_item_ids = item_ids

        # Convert selection_id to position if provided
        if selection_id is not None and position is None:
            try:
                position = item_ids.index(selection_id)
            except ValueError:
                pass  # ID not found, ignore

        # Handle menus even if empty (items could be [])
        # Check if this menu is identical to the previous one
        new_menu_state = {
            "menu_id": menu_id,
            "items": items,
            "multiletter_enabled": multiletter_enabled,
            "escape_behavior": escape_behavior,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
        }

        # if self.current_menu_state == new_menu_state:
            # Menu is identical - skip wx update to avoid confusing screen readers
            # However, if position is specified, we should still move to it
        #    if position is not None and len(items) > 0:
        #        if 0 <= position < len(items):
        #            self.menu_list.SetSelection(position)
        #    return

        # Store new menu state for future comparisons
        self.current_menu_state = new_menu_state

        # Set multiletter navigation for this menu
        self.set_multiletter_navigation(multiletter_enabled)

        # Set grid mode for this menu
        self.set_grid_mode(grid_enabled, grid_width)

        # Set escape behavior for this menu
        self.escape_behavior = escape_behavior

        # Make sure we're in list mode
        if self.current_mode == "edit":
            self.switch_to_list_mode()

        # Check if this is the same menu or a different one
        is_same_menu_id = self.current_menu_id == menu_id

        # Store the menu_id so we can send it back with selections
        self.current_menu_id = menu_id

        # Different menu ID → always clear and rebuild (don't bother with diff)
        if not is_same_menu_id:
            self.menu_list.Clear()
            for item in items:
                self.menu_list.Append(item)

            # Set focus first to avoid double announcement
            focused = wx.Window.FindFocus()
            if focused != self.chat_input and focused != self.history_text:
                self.menu_list.SetFocus()

            # Set initial selection (use position if provided, otherwise 0)
            if len(items) > 0:
                if position is not None and 0 <= position < len(items):
                    self.menu_list.SetSelection(position)
                else:
                    self.menu_list.SetSelection(0)

        # Same menu ID → use diff algorithm to minimize screen reader disruption
        elif self.menu_list.GetCount() > 0:
            # Get current menu items
            old_items = [
                self.menu_list.GetString(i) for i in range(self.menu_list.GetCount())
            ]

            # Preserve current selection
            old_selection = self.menu_list.GetSelection()

            # Compute minimal diff (pass IDs if available for simpler algorithm)
            operations = self.compute_menu_diff(old_items, items, old_item_ids, item_ids)

            # Apply diff operations (screen reader friendly)
            new_selection = self.apply_menu_diff(operations, old_selection)

            # Override selection if position is explicitly provided
            if position is not None and len(items) > 0:
                if 0 <= position < len(items):
                    new_selection = position
                    # Force selection update when position is explicitly provided
                    self.menu_list.SetSelection(new_selection)
            # Set selection after diff operations
            elif len(items) > 0:
                # Check if an item is actually selected and if it matches our target
                current_selection = self.menu_list.GetSelection()
                if new_selection != wx.NOT_FOUND:
                    # Only call SetSelection if nothing is selected or wrong item is selected
                    if current_selection != new_selection:
                        self.menu_list.SetSelection(new_selection)
                else:
                    # No valid selection computed, default to 0 if nothing selected
                    if current_selection == wx.NOT_FOUND:
                        self.menu_list.SetSelection(0)
        else:
            # Same menu ID but list is empty - full rebuild
            self.menu_list.Clear()
            for item in items:
                self.menu_list.Append(item)

            # Set focus first to avoid double announcement
            focused = wx.Window.FindFocus()
            if focused != self.chat_input and focused != self.history_text:
                self.menu_list.SetFocus()

            # Set initial selection (use position if provided, otherwise 0)
            if len(items) > 0:
                if position is not None and 0 <= position < len(items):
                    self.menu_list.SetSelection(position)
                else:
                    self.menu_list.SetSelection(0)

    def on_server_request_input(self, packet):
        """Handle request_input packet from server."""
        prompt = packet.get("prompt", "Enter text:")
        input_id = packet.get("input_id", None)
        default_value = packet.get("default_value", "")
        multiline = packet.get("multiline", False)
        read_only = packet.get("read_only", False)

        def on_submit(text):
            # Send editbox event back to server
            event_packet = {"type": "editbox", "text": text}
            if input_id:
                event_packet["input_id"] = input_id
            self.network.send_packet(event_packet)

        self.switch_to_edit_mode(prompt, on_submit, default_value, multiline, read_only)

    def on_server_clear_ui(self, packet):
        """Handle clear_ui packet from server."""
        # Clear menu
        self.menu_list.Clear()
        self.current_menu_id = None
        self.current_menu_state = None
        # Switch to list mode if in edit mode
        if self.current_mode == "edit":
            self.switch_to_list_mode()
        # Remove all playlists when leaving game
        self.sound_manager.remove_all_playlists()
        # Stop music and ambience when leaving game
        self.sound_manager.stop_music(fade=True)
        self.sound_manager.stop_ambience(force=False)

    def on_server_game_list(self, packet):
        """Handle game_list packet from server."""
        games = packet.get("games", [])
        if games:
            game_list_str = "Available games:\n"
            for game in games:
                game_list_str += f"{game['id']}: {game['name']} ({game['type']}) - {game['players']}/{game['max_players']} players\n"
            self.add_history(game_list_str)
        else:
            self.add_history("No games available")

    # Config persistence methods

    def _load_preferences(self):
        """
        Load preferences from AppData/Roaming/ddt.one/PlayAural/preferences.json

        Returns:
            Dict containing preferences, or empty dict if file doesn't exist
        """
        import os
        appdata = os.getenv("APPDATA")
        if appdata:
             config_dir = Path(appdata) / "ddt.one" / "PlayAural"
        else:
             config_dir = Path.home() / "ddt.one" / "PlayAural"
        
        preferences_file = config_dir / "preferences.json"

        if preferences_file.exists():
            try:
                with open(preferences_file, "r") as f:
                    return json.load(f)
            except Exception:
                # If preferences is corrupted, return empty dict
                return {}
        return {}

    def _save_muted_buffers(self):
        """Save muted buffers to preferences file."""
        import os
        appdata = os.getenv("APPDATA")
        if appdata:
             config_dir = Path(appdata) / "ddt.one" / "PlayAural"
        else:
             config_dir = Path.home() / "ddt.one" / "PlayAural"
             
        preferences_file = config_dir / "preferences.json"

        # Load existing preferences
        preferences = self._load_preferences()

        # Update muted buffers
        preferences["muted_buffers"] = list(self.buffer_system.get_muted_buffers())

        # Save
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(preferences_file, "w") as f:
                json.dump(preferences, f, indent=2)
        except Exception:
            # Silently fail if we can't save preferences
            pass

    def on_login_failed(self, packet):
        """Handle login failure from server."""
        reason = packet.get("reason", "Login failed")
        self.disconnect_reason = reason
        self.Close()
