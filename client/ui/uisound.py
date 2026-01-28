# Custom utility from Zarvox, allowing for playing sounds for ui events with seemless integration.

import wx
import wx.adv

default_sounds_path = "sounds"


def play_sound(name: str, blocking: bool = False):
    try:
        sound = wx.adv.Sound(name + ".wav")
        if sound.IsOk():
            sound.Play(wx.adv.SOUND_SYNC if blocking else wx.adv.SOUND_ASYNC)
    except Exception as e:
        print("Sound error:", e)


class SoundBindingsMixin:
    """
    Add sound cues for ui event interactions:
      - For any frame, panel, or dialog, add this class along with it. Then simply call 'self.bind_sounds()' after controls have been added to apply it.
    """

    def bind_sounds(self, enable_focus: bool = False, *, recursion: int = None):
        """
        Bind sound events on this window (frame/panel/dialog):
          - Focus events on the root window itself
          - Command events on all child controls recursively (if requested)
        """
        if not hasattr(self, "play_sfx"):
            self.audio_settings()
        self.toggle_focus_sfx(enable_focus)
        # if recursion is negative, don't bind any events. Useful for controlling exactly which controls have sounds.
        self.bind_sfx_to_area(self, recursion)

    def audio_settings(self, *, sounds_path: str = None, block: bool = False):
        if sounds_path is None:
            sounds_path = default_sounds_path

        def play_sfx(name: str, blocking: bool = None, *, path: str = None):
            """Play sound using defaults unless caller explicitly overrides."""
            return play_sound(
                f"{sounds_path}/{name}" if path is None else f"{path}/{name}",
                block if blocking is None else blocking,
            )

        self.play_sfx = play_sfx

    def toggle_focus_sfx(self, enabled: bool, *, ctrl=None):
        if ctrl is None:
            ctrl = self
        if enabled:
            ctrl.Bind(wx.EVT_CHILD_FOCUS, self.on_focus_sfx)
        else:
            ctrl.Unbind(wx.EVT_CHILD_FOCUS, handler=self.on_focus_sfx)

    def bind_sfx_to_control(self, ctrl, include_focus: bool = False):
        """
        Apply event bindings to a single control.
        """
        if include_focus:
            self.toggle_focus_sfx(True, ctrl=ctrl)
        # checklistbox is a subclass of listbox
        if isinstance(ctrl, wx.CheckListBox):
            ctrl.Bind(wx.EVT_CHECKLISTBOX, self.on_checklistbox_sfx)
        if isinstance(ctrl, wx.ListBox):
            ctrl.Bind(wx.EVT_LISTBOX, self.on_listbox_sfx)
        if isinstance(ctrl, wx.Button):
            ctrl.Bind(wx.EVT_BUTTON, self.on_button_sfx)
        if isinstance(ctrl, wx.CheckBox):
            ctrl.Bind(wx.EVT_CHECKBOX, self.on_checkbox_sfx)
        if isinstance(ctrl, wx.Choice):
            ctrl.Bind(wx.EVT_CHOICE, self.on_choice_sfx)

    def unbind_sfx_from_control(self, ctrl, include_focus: bool = False):
        """
        Remove event bindings from a single control.
        """
        if include_focus:
            self.toggle_focus_sfx(False, ctrl=ctrl)
        # checklistbox is a subclass of listbox
        if isinstance(ctrl, wx.CheckListBox):
            ctrl.Unbind(wx.EVT_CHECKLISTBOX, handler=self.on_checklistbox_sfx)
        if isinstance(ctrl, wx.ListBox):
            ctrl.Unbind(wx.EVT_LISTBOX, handler=self.on_listbox_sfx)
        if isinstance(ctrl, wx.Button):
            ctrl.Unbind(wx.EVT_BUTTON, handler=self.on_button_sfx)
        if isinstance(ctrl, wx.CheckBox):
            ctrl.Unbind(wx.EVT_CHECKBOX, handler=self.on_checkbox_sfx)
        if isinstance(ctrl, wx.Choice):
            ctrl.Unbind(wx.EVT_CHOICE, handler=self.on_choice_sfx)

    def bind_sfx_to_area(self, root, recursion: int = 0, level: int = 0):
        """
        Recursively bind command events to all supported controls under root.
        - By default recursion is disabled.
        """
        for ctrl in root.GetChildren():
            self.bind_sfx_to_control(ctrl)

            if (recursion is None or level < recursion) and isinstance(ctrl, wx.Panel):
                self.bind_sfx_to_area(ctrl, recursion, level + 1)

    def unbind_sfx_from_area(self, root, recursion: int = 0, level: int = 0):
        """
        Recursively unbind command events from all supported controls under root.
        - By default recursion is disabled.
        """
        for ctrl in root.GetChildren():
            self.unbind_sfx_from_control(ctrl)

            if (recursion is None or level < recursion) and isinstance(ctrl, wx.Panel):
                self.unbind_sfx_from_area(ctrl, recursion, level + 1)

    # event handlers
    def on_focus_sfx(self, evt: wx.FocusEvent):
        # window= evt.GetWindow()
        child = evt.GetEventObject()
        if isinstance(child, wx.ListBox):
            self.on_listbox_sfx(evt)
        elif isinstance(child, wx.Choice):
            self.on_choice_sfx(evt)
        elif isinstance(child, wx.CheckBox):
            self.on_checkbox_sfx(evt)
        else:
            self.play_sfx("element_focus")
        evt.Skip()

    def on_button_sfx(self, evt: wx.CommandEvent):
        self.play_sfx("button_press")
        evt.Skip()

    def on_checkbox_sfx(self, evt: wx.CommandEvent):
        ctrl = evt.GetEventObject()
        val = evt.GetValue() if hasattr(evt, "GetValue") else ctrl.GetValue()
        if val is None or val == wx.NOT_FOUND:
            self.play_sfx("error")
        else:
            self.play_sfx("checkbox_" + ("on" if val else "off"))
        evt.Skip()

    def on_listbox_sfx(self, evt: wx.CommandEvent):
        ctrl = evt.GetEventObject()
        if isinstance(ctrl, wx.CheckListBox):
            self.on_checklistbox_sfx(evt)
        else:
            # index= evt.GetSelection() if hasattr(evt, "GetSelection") else ctrl.GetSelection()
            self.play_sfx("list_move")
        evt.Skip()

    def on_checklistbox_sfx(self, evt: wx.CommandEvent):
        ctrl = evt.GetEventObject()
        index = (
            evt.GetSelection() if hasattr(evt, "GetSelection") else ctrl.GetSelection()
        )
        if index is None or ctrl.GetCount() == 0 or index == wx.NOT_FOUND:
            self.play_sfx("list_move")
        else:
            self.play_sfx("checkbox_list_" + ("on" if ctrl.IsChecked(index) else "off"))
        evt.Skip()

    def on_choice_sfx(self, evt: wx.CommandEvent):
        # index= evt.GetSelection() if hasattr(evt, "GetSelection") else ctrl.GetSelection()
        self.play_sfx("dropdown_move")
        evt.Skip()
