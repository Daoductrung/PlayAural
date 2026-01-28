"""Custom ListBox with multiletter navigation support."""

import wx
import time


class MenuList(wx.ListBox):
    """
    A ListBox with multiletter navigation and keybind support.

    Keybind System:
    - Space and Enter always trigger keybinds (printed with modifiers)
    - Letters and numbers trigger keybinds only when multiletter is OFF
    - When multiletter is ON, letters/numbers do multiletter navigation

    Multiletter Navigation:
    When enabled, typing consecutive letters quickly will search for items
    starting with those letters (1 second timeout).
    """

    def __init__(
        self,
        parent,
        sound_manager=None,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        choices=None,
        style=0,
    ):
        """Initialize the MenuList."""
        if choices is None:
            choices = []

        super().__init__(parent, id, pos, size, choices, style)

        self.sound_manager = sound_manager
        self.multiletter_enabled = True
        self.grid_enabled = False
        self.grid_width = 1  # Number of columns in grid mode
        self.search_buffer = ""
        self.last_keypress_time = 0
        self.search_timeout = 0.15  # 150ms like in the old version

        # Bind keyboard events - use KEY_DOWN to intercept before default behavior
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # Also bind CHAR to catch Enter which might be handled specially
        self.Bind(wx.EVT_CHAR, self.on_char)
        # Bind LISTBOX_DCLICK which is triggered by Enter in ListBox
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_listbox_dclick)
        # Bind selection change to play menuclick sound
        self.Bind(wx.EVT_LISTBOX, self.on_selection_change)

    def enable_multiletter_navigation(self, enable=True):
        """Enable or disable multiletter navigation."""
        self.multiletter_enabled = enable
        if not enable:
            self.search_buffer = ""

    def enable_grid_mode(self, enable=True, grid_width=1):
        """Enable or disable grid mode navigation."""
        self.grid_enabled = enable
        self.grid_width = max(1, grid_width)  # Ensure at least 1 column

    def on_key_down(self, event):
        """Handle key down events for keybinds and multiletter navigation."""
        key_code = event.GetKeyCode()

        # Handle Tab for focus navigation
        if key_code == wx.WXK_TAB:
            # Use Navigate to explicitly move focus
            if event.ShiftDown():
                self.Navigate(wx.NavigationKeyEvent.IsBackward)
            else:
                self.Navigate(wx.NavigationKeyEvent.IsForward)
            return

        # Handle arrow keys in grid mode
        if self.grid_enabled:
            is_arrow = key_code in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN)
            if is_arrow:
                self._handle_grid_navigation(key_code)
                return
        else:
            if key_code in (wx.WXK_UP, wx.WXK_DOWN) and self.GetCount() == 1:
                self._repeat_single_item()
                return

        # Check if this is a letter, number, space, or enter
        is_letter = ord("A") <= key_code <= ord("Z")
        is_number = ord("0") <= key_code <= ord("9")
        is_space = key_code == wx.WXK_SPACE
        # Don't include 307 anymore - need to find the real Enter key code
        is_enter = key_code == wx.WXK_RETURN or key_code == wx.WXK_NUMPAD_ENTER

        # Handle Enter directly since WANTS_CHARS prevents dclick from firing
        # Only activate if no modifiers are held (shift+enter etc. should be keybinds)
        if is_enter and not event.ControlDown() and not event.ShiftDown() and not event.AltDown():
            self._on_activation()
            return

        # If it's one of our keybind keys (letters/numbers/space)
        if is_letter or is_number or is_space:
            # Get modifier states
            alt = event.AltDown()

            # Letters and numbers only trigger keybinds when multiletter is off
            should_trigger_keybind = not self.multiletter_enabled

            if should_trigger_keybind:
                # For letters/numbers, consume the event to prevent default behavior
                return

            # If we get here, multiletter is enabled and it's a letter/number/space
            # Do multiletter navigation
            if is_letter or is_number or is_space:
                # Don't do multiletter navigation if Alt is pressed
                if alt:
                    # Let the event through for Alt+letter combinations
                    event.Skip()
                    return

                char = chr(key_code).lower()
                current_time = time.time()

                # Reset search buffer if too much time has passed
                if current_time - self.last_keypress_time > self.search_timeout:
                    self.search_buffer = ""

                self.search_buffer += char
                self.last_keypress_time = current_time

                # Search for matching item
                self._find_and_select(self.search_buffer)
                # Don't skip - we handled it
                return

        # For all other keys (arrows, etc.), let them work normally
        event.Skip()

    def _repeat_single_item(self):
        """Repeat the single menu item when up/down is pressed."""
        if self.GetCount() != 1:
            return
        self.SetSelection(0)
        self.EnsureVisible(0)
        evt = wx.CommandEvent(wx.EVT_LISTBOX.typeId, self.GetId())
        evt.SetInt(0)
        self.GetEventHandler().ProcessEvent(evt)

    def on_char(self, event):
        """Handle CHAR events, specifically for Enter which may bypass KEY_DOWN."""
        key_code = event.GetKeyCode()

        # Handle Tab in char events too
        if key_code == wx.WXK_TAB or key_code == 9:  # 9 is tab character
            if event.ShiftDown():
                self.Navigate(wx.NavigationKeyEvent.IsBackward)
            else:
                self.Navigate(wx.NavigationKeyEvent.IsForward)
            return

        # Let plain Enter pass through (no modifiers)
        is_enter = (
            key_code == wx.WXK_RETURN
            or key_code == wx.WXK_NUMPAD_ENTER
            or key_code == 13
        )  # 13 is carriage return

        if is_enter and not event.ControlDown() and not event.ShiftDown() and not event.AltDown():
            # Skip to allow dclick to fire
            event.Skip()
            return

        # For everything else, skip so KEY_DOWN can handle it
        event.Skip()

    def _on_activation(self):
        """Handle menu item activation (Enter/Space/Double-click)."""
        # Play menuenter sound
        if self.sound_manager:
            self.sound_manager.play_menuenter()

        # Call the parent's activation handler directly
        parent = self.GetParent()
        while parent:
            if hasattr(parent, "on_menu_activate"):
                # Create a dummy event
                dummy_event = wx.CommandEvent()
                parent.on_menu_activate(dummy_event)
                break
            parent = parent.GetParent()

    def on_listbox_dclick(self, event):
        """Handle double-click event (for actual mouse double-clicks)."""
        # Play menuenter sound and call activation
        self._on_activation()
        # Don't skip - we handled it
        return

    def on_selection_change(self, event):
        """Handle selection change to play menuclick sound."""
        if self.sound_manager:
            # Call directly - CallAfter can cause issues with rapid events
            self.sound_manager.play_menuclick()
        event.Skip()

    def _find_and_select(self, search_text):
        """
        Find and select item that starts with the search text.
        Works like the old version:
        - If current item already matches and we have >1 char, stay on it
        - Otherwise search from next item forward, wrapping around
        """
        search_text = search_text.lower()
        current_pos = self.GetSelection()

        # If we have more than 1 character and current item matches, stay on it
        if len(search_text) > 1 and current_pos != wx.NOT_FOUND:
            current_text = self.GetString(current_pos).lower()
            if current_text.startswith(search_text):
                return  # Stay on current item

        # Search from next item forward, wrapping around
        count = self.GetCount()
        start_pos = current_pos if current_pos != wx.NOT_FOUND else 0

        for offset in range(1, count + 1):
            i = (start_pos + offset) % count
            item_text = self.GetString(i).lower()
            if item_text.startswith(search_text):
                old_selection = self.GetSelection()
                self.SetSelection(i)
                self.EnsureVisible(i)
                # Play menuclick sound if selection changed
                if old_selection != i and self.sound_manager:
                    self.sound_manager.play_menuclick()
                return

    def clear_search_buffer(self):
        """Clear the search buffer."""
        self.search_buffer = ""

    def _handle_grid_navigation(self, key_code):
        """
        Handle arrow key navigation in grid mode.
        Treats the list as a 2D array with grid_width columns.
        """
        current_pos = self.GetSelection()
        if current_pos == wx.NOT_FOUND:
            current_pos = 0

        count = self.GetCount()
        if count == 0:
            return

        # Calculate current row and column (0-based)
        current_row = current_pos // self.grid_width
        current_col = current_pos % self.grid_width

        new_pos = current_pos

        if key_code == wx.WXK_LEFT:
            # Move left on x-axis
            if current_col > 0:
                new_pos = current_pos - 1
            # else: at left edge
            pass

        elif key_code == wx.WXK_RIGHT:
            # Move right on x-axis
            if current_col < self.grid_width - 1 and current_pos + 1 < count:
                new_pos = current_pos + 1
            # else: at right edge
            pass

        elif key_code == wx.WXK_UP:
            # Move up (positive y-axis in grid terms, but negative row index)
            if current_row > 0:
                new_pos = current_pos - self.grid_width
                # Make sure we don't go out of bounds
                if new_pos < 0:
                    new_pos = current_pos
            # else: at top edge
            pass

        elif key_code == wx.WXK_DOWN:
            # Move down (negative y-axis in grid terms, but positive row index)
            potential_new_pos = current_pos + self.grid_width
            if potential_new_pos < count:
                new_pos = potential_new_pos
            # else: at bottom edge
            pass

        # Only update selection and play sound if position changed
        if new_pos != current_pos:
            self.SetSelection(new_pos)
            self.EnsureVisible(new_pos)
            # Play menuclick sound when moving
            if self.sound_manager:
                self.sound_manager.play_menuclick()
