"""Client Options Profile dialog for PlayAural client."""

import wx
from . import uisound
from localization import Localization


class ClientOptionsDialog(wx.Dialog, uisound.SoundBindingsMixin):
    """Dialog for managing client-side options (audio, social, etc.)."""

    def __init__(
        self,
        parent,
        config_manager,
        lang_codes,
        sound_manager=None,
        voice_manager=None,
    ):
        """Initialize the client options dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            lang_codes: The iso language codes
            sound_manager: SoundManager instance (optional, for applying volume changes)
            voice_manager: VoiceManager instance (optional, for applying voice volume changes)
        """
        super().__init__(
            parent,
            title=Localization.get("options-dialog-title"),
            size=(600, 520),
        )

        self.config_manager = config_manager
        self.lang_codes = lang_codes
        self.sound_manager = sound_manager
        self.voice_manager = voice_manager

        # Always use global defaults
        self.options = config_manager.get_client_options()

        self.preferences = type('obj', (object,), {
             'music_volume': self.options.get("audio", {}).get("music_volume", 20) / 100.0,
             'sound_volume': self.options.get("audio", {}).get("sound_volume", 100) / 100.0,
             'ambience_volume': self.options.get("audio", {}).get("ambience_volume", 20) / 100.0,
             'voice_volume': self.options.get("audio", {}).get("voice_volume", 80) / 100.0,
        })

        self._create_ui()
        self.CenterOnScreen()

    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        self.panel = panel
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label=Localization.get("options-dialog-title"))
        font = title.GetFont()
        font.PointSize += 2
        font = font.Bold()
        title.SetFont(font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        self.notebook = wx.Notebook(panel)
        audio_panel = self._create_audio_panel(self.notebook)
        self.notebook.AddPage(audio_panel, Localization.get("options-tab-audio"))
        social_panel = self._create_social_panel(self.notebook)
        self.notebook.AddPage(social_panel, Localization.get("options-tab-social"))
        interface_panel = self._create_interface_panel(self.notebook)
        self.notebook.AddPage(
            interface_panel, Localization.get("options-tab-interface")
        )

        self.tab_names = tuple(
            [self.notebook.GetPageText(i) for i in range(self.notebook.GetPageCount())]
        )
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        reset_last_btn = wx.Button(
            panel, label=Localization.get("options-reset-saved")
        )
        reset_last_btn.Bind(wx.EVT_BUTTON, self.on_reset_to_last_used)
        button_sizer.Add(reset_last_btn, 0, wx.RIGHT, 5)
        button_sizer.AddStretchSpacer()
        save_btn = wx.Button(panel, label=Localization.get("common-save"))
        save_btn.SetDefault()
        button_sizer.Add(save_btn, 0, wx.RIGHT, 5)
        done_btn = wx.Button(
            panel, wx.ID_CANCEL, Localization.get("common-cancel")
        )
        button_sizer.Add(done_btn, 0)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)

        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        done_btn.Bind(wx.EVT_BUTTON, self.on_done)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel.SetSizer(main_sizer)
        self.bind_sounds(recursion=-1)

    def _create_audio_panel(self, parent):
        """Create the audio options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(panel, label=Localization.get("options-music-volume-label")),
                  0, wx.LEFT | wx.TOP, 10)
        self.music_spin = wx.SpinCtrl(panel, value=str(int(self.preferences.music_volume * 100)), min=0, max=100)
        self.music_spin.Bind(wx.EVT_SPINCTRL, self.on_music_spin_change)
        self.music_spin.Bind(wx.EVT_TEXT, self.on_music_spin_change)
        sizer.Add(self.music_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        sizer.Add(wx.StaticText(panel, label=Localization.get("options-sound-volume-label")),
                  0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        self.sound_spin = wx.SpinCtrl(
            panel,
            value=str(int(self.preferences.sound_volume * 100)),
            min=0, max=100,
        )
        self.sound_spin.Bind(wx.EVT_SPINCTRL, self.on_sound_spin_change)
        self.sound_spin.Bind(wx.EVT_TEXT, self.on_sound_spin_change)
        sizer.Add(self.sound_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        sizer.Add(wx.StaticText(panel, label=Localization.get("options-ambience-volume-label")),
                  0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        self.ambience_spin = wx.SpinCtrl(
            panel,
            value=str(self.options.get("audio", {}).get("ambience_volume", 20)),
            min=0, max=100,
        )
        self.ambience_spin.Bind(wx.EVT_SPINCTRL, self.on_ambience_spin_change)
        self.ambience_spin.Bind(wx.EVT_TEXT, self.on_ambience_spin_change)
        sizer.Add(self.ambience_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        voice_label_text = Localization.get("options-voice-volume-label")
        sizer.Add(wx.StaticText(panel, label=voice_label_text),
                  0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        self.voice_spin = wx.SpinCtrl(
            panel,
            value=str(int(self.preferences.voice_volume * 100)),
            min=10, max=100,
        )
        self.voice_spin.Bind(wx.EVT_SPINCTRL, self.on_voice_spin_change)
        self.voice_spin.Bind(wx.EVT_TEXT, self.on_voice_spin_change)
        sizer.Add(self.voice_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        sizer.Add(wx.StaticText(panel, label=Localization.get("options-audio-hotkeys-note")),
                  0, wx.ALL, 10)

        panel.SetSizer(sizer)
        return panel

    def _create_social_panel(self, parent):
        """Create the social options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        social = self.options.get("social", {})
        self.mute_global_check = wx.CheckBox(
            panel, label=Localization.get("options-mute-global-chat")
        )
        self.mute_global_check.SetValue(social.get("mute_global_chat", False))
        sizer.Add(self.mute_global_check, 0, wx.ALL, 10)
        self.mute_table_check = wx.CheckBox(
            panel, label=Localization.get("options-mute-table-chat")
        )
        self.mute_table_check.SetValue(social.get("mute_table_chat", False))
        sizer.Add(self.mute_table_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        return panel

    def _create_interface_panel(self, parent):
        """Create the interface options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        interface = self.options.get("interface", {})
        self.invert_multiline_enter_check = wx.CheckBox(
            panel, label=Localization.get("options-invert-multiline-enter")
        )
        self.invert_multiline_enter_check.SetValue(interface.get("invert_multiline_enter_behavior", False))
        sizer.Add(self.invert_multiline_enter_check, 0, wx.ALL, 10)
        self.play_typing_sounds_check = wx.CheckBox(
            panel, label=Localization.get("options-play-typing-sounds")
        )
        self.play_typing_sounds_check.SetValue(interface.get("play_typing_sounds", True))
        sizer.Add(self.play_typing_sounds_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        return panel

    def on_music_spin_change(self, event):
        """Handle music volume spin control change - apply immediately."""
        value = self.music_spin.GetValue()
        if self.sound_manager:
            self.sound_manager.set_music_volume(value / 100.0)

    def on_ambience_spin_change(self, event):
        """Handle ambience volume spin control change - apply immediately."""
        value = self.ambience_spin.GetValue()
        if self.sound_manager:
            self.sound_manager.set_ambience_volume(value / 100.0)

    def on_sound_spin_change(self, event):
        """Handle sound effects volume spin control change - apply immediately."""
        value = max(10, min(100, self.sound_spin.GetValue()))
        if self.sound_manager:
            self.sound_manager.set_sound_volume(value / 100.0)

    def on_voice_spin_change(self, event):
        """Handle voice chat volume spin control change - apply immediately."""
        value = max(10, min(100, self.voice_spin.GetValue()))
        if self.voice_manager:
            self.voice_manager.set_voice_volume(value / 100.0)

    def _reset_current_tab_fields(self, data_source):
        """Reset fields in the current tab to values from the given data source."""
        current_page = self.notebook.GetSelection()

        if current_page == 0:  # Audio tab
            audio = data_source.get("audio", {})
            self.music_spin.SetValue(int(audio.get("music_volume", 20)))
            self.sound_spin.SetValue(int(audio.get("sound_volume", 100)))
            self.ambience_spin.SetValue(int(audio.get("ambience_volume", 20)))
            self.voice_spin.SetValue(int(audio.get("voice_volume", 80)))

            if self.sound_manager:
                self.sound_manager.set_music_volume(audio.get("music_volume", 20) / 100.0)
                self.sound_manager.set_sound_volume(audio.get("sound_volume", 100) / 100.0)
                self.sound_manager.set_ambience_volume(audio.get("ambience_volume", 20) / 100.0)
            if self.voice_manager:
                self.voice_manager.set_voice_volume(audio.get("voice_volume", 80) / 100.0)

        elif current_page == 1:  # Social tab
            social = data_source.get("social", {})
            self.mute_global_check.SetValue(social.get("mute_global_chat", False))
            self.mute_table_check.SetValue(social.get("mute_table_chat", False))

        elif current_page == 2:  # Interface tab
            interface = data_source.get("interface", {})
            self.invert_multiline_enter_check.SetValue(interface.get("invert_multiline_enter_behavior", False))
            self.play_typing_sounds_check.SetValue(interface.get("play_typing_sounds", True))

    def on_reset_to_last_used(self, event):
        """Reset fields in current tab to last saved values."""
        current_page = self.notebook.GetSelection()
        current_tab_name = self.tab_names[current_page]
        result = wx.MessageBox(
            Localization.get("options-reset-confirm-message", tab=current_tab_name),
            Localization.get("options-reset-confirm-title"),
            wx.YES_NO | wx.ICON_QUESTION,
        )
        if result == wx.YES:
            self.options = self.config_manager.get_client_options()
            self._reset_current_tab_fields(self.options)

    def on_save(self, event):
        """Save changes and close dialog."""
        music_volume = self.music_spin.GetValue()
        sound_volume = max(10, min(100, self.sound_spin.GetValue()))
        ambience_volume = self.ambience_spin.GetValue()
        voice_volume = max(10, min(100, self.voice_spin.GetValue()))

        self.config_manager.set_client_option("audio/music_volume", music_volume, create_mode=True)
        self.config_manager.set_client_option("audio/sound_volume", sound_volume, create_mode=True)
        self.config_manager.set_client_option("audio/ambience_volume", ambience_volume, create_mode=True)
        self.config_manager.set_client_option("audio/voice_volume", voice_volume, create_mode=True)

        mute_global = self.mute_global_check.GetValue()
        mute_table = self.mute_table_check.GetValue()
        self.config_manager.set_client_option("social/mute_global_chat", mute_global, create_mode=True)
        self.config_manager.set_client_option("social/mute_table_chat", mute_table, create_mode=True)

        invert_multiline_enter = self.invert_multiline_enter_check.GetValue()
        play_typing_sounds = self.play_typing_sounds_check.GetValue()
        self.config_manager.set_client_option("interface/invert_multiline_enter_behavior", invert_multiline_enter, create_mode=True)
        self.config_manager.set_client_option("interface/play_typing_sounds", play_typing_sounds, create_mode=True)

        self.EndModal(wx.ID_OK)

    def on_done(self, event):
        """Close dialog without saving."""
        self.EndModal(wx.ID_CANCEL)

    def on_close(self, event):
        """Handle window close."""
        self.EndModal(wx.ID_CANCEL)
