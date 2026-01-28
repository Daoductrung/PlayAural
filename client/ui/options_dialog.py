"""Client Options Profile dialog for PlayAural v0.1 client."""

import wx
from . import uisound
from localization import Localization


class ClientOptionsDialog(wx.Dialog, uisound.SoundBindingsMixin):
    """Dialog for managing client-side options (audio, social, etc.)."""

    def __init__(
        self,
        parent,
        config_manager,
        server_id,
        lang_codes,
        sound_manager=None,
        client_options=None,
    ):
        """Initialize the client options dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            server_id: Legacy argument, kept for compatibility but not used for overrides
            lang_codes: The iso language codes
            sound_manager: SoundManager instance (optional, for applying volume changes)
            client_options: Reference to main window's client_options dict (optional, will be updated on save)
        """
        super().__init__(parent, title="Client Options", size=(600, 500))

        self.config_manager = config_manager
        self.server_id = server_id
        self.lang_codes = lang_codes
        self.sound_manager = sound_manager

        # Always use global defaults (config_manager.get_client_options now returns defaults only)
        self.options = config_manager.get_client_options()
            
        # Build games_list from local_table/creation_notifications keys in config
        local_table = self.options.get("local_table", {})
        creation_notifications = local_table.get("creation_notifications", {})
        self.games_list = [
            {"type": game_type, "name": game_type}
            for game_type in creation_notifications.keys()
        ]

        self.preferences = type('obj', (object,), {
             'music_volume': self.options.get("audio", {}).get("music_volume", 20) / 100.0,
             'ambience_volume': self.options.get("audio", {}).get("ambience_volume", 20) / 100.0
        })

        self._create_ui()
        self.CenterOnScreen()



    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        self.panel = panel  # Store panel reference
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(panel, label="Client Options")
        font = title.GetFont()
        font.PointSize += 2
        font = font.Bold()
        title.SetFont(font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        # Notebook for categories
        self.notebook = wx.Notebook(panel)

        # Audio tab
        audio_panel = self._create_audio_panel(self.notebook)
        self.notebook.AddPage(audio_panel, "Audio")

        # Social tab
        social_panel = self._create_social_panel(self.notebook)
        self.notebook.AddPage(social_panel, "Social")

        # Interface tab
        interface_panel = self._create_interface_panel(self.notebook)
        self.notebook.AddPage(interface_panel, "Interface")

        # Local Table tab
        tables_panel = self._create_tables_panel(self.notebook)
        self.notebook.AddPage(tables_panel, "Local Table")

        self.tab_names = tuple(
            [self.notebook.GetPageText(i) for i in range(self.notebook.GetPageCount())]
        )
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Reset to Last Used Settings button
        reset_last_btn = wx.Button(panel, label="Reset from Saved")
        reset_last_btn.Bind(wx.EVT_BUTTON, self.on_reset_to_last_used)
        button_sizer.Add(reset_last_btn, 0, wx.RIGHT, 5)

        button_sizer.AddStretchSpacer()

        save_btn = wx.Button(panel, label="&Save")
        save_btn.SetDefault()
        button_sizer.Add(save_btn, 0, wx.RIGHT, 5)

        done_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        button_sizer.Add(done_btn, 0)

        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Bind events
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        done_btn.Bind(wx.EVT_BUTTON, self.on_done)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel.SetSizer(main_sizer)
        self.bind_sounds(recursion=-1)

    def _create_audio_panel(self, parent):
        """Create the audio options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Music volume
        music_label = wx.StaticText(panel, label=Localization.get("options-music-volume-label"))
        # Using SpinButton as in original, but typically SpinCtrl is better. Keeping original widget type.
        # But we need a text display for the logic to work as originally implemented or refactor.
        # Original: wx.SpinButton + wx.TextCtrl
        
        sizer.Add(music_label, 0, wx.LEFT|wx.TOP, 10)
        
        # Simplified Audio UI: Use SpinCtrl for consistency with others if possible, or replicate original behavior.
        # Original code used SpinButton + TextCtrl for Music, SpinCtrl for Ambience. A bit inconsistent.
        # Let's standardize on SpinCtrl for cleanliness.
        
        self.music_spin = wx.SpinCtrl(
             panel,
             value=str(int(self.preferences.music_volume * 100)),
             min=0,
             max=100
        )
        self.music_spin.Bind(wx.EVT_SPINCTRL, self.on_music_spin_change)
        self.music_spin.Bind(wx.EVT_TEXT, self.on_music_spin_change)
        sizer.Add(self.music_spin, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)


        ambience_label = wx.StaticText(panel, label=Localization.get("options-ambience-volume-label"))
        sizer.Add(ambience_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.ambience_spin = wx.SpinCtrl(
            panel,
            value=str(self.options.get("audio", {}).get("ambience_volume", 20)),
            min=0,
            max=100,
        )
        self.ambience_spin.Bind(wx.EVT_SPINCTRL, self.on_ambience_spin_change)
        self.ambience_spin.Bind(wx.EVT_TEXT, self.on_ambience_spin_change)
        sizer.Add(self.ambience_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        # Info text
        info_text = wx.StaticText(
            panel,
            label="Note: F7-F10 hotkeys also adjust volumes.",
        )
        sizer.Add(info_text, 0, wx.ALL, 10)

        panel.SetSizer(sizer)
        return panel

    def _create_social_panel(self, parent):
        """Create the social options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        social = self.options.get("social", {})

        # Mute global chat checkbox
        self.mute_global_check = wx.CheckBox(panel, label="Mute &Global Chat")
        self.mute_global_check.SetValue(social.get("mute_global_chat", False))
        sizer.Add(self.mute_global_check, 0, wx.ALL, 10)

        # Mute table chat checkbox
        self.mute_table_check = wx.CheckBox(panel, label="Mute &Table Chat")
        self.mute_table_check.SetValue(social.get("mute_table_chat", False))
        sizer.Add(self.mute_table_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        return panel

    def _create_interface_panel(self, parent):
        """Create the interface options panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        interface = self.options.get("interface", {})

        # Invert multiline enter behavior checkbox
        self.invert_multiline_enter_check = wx.CheckBox(
            panel, label="Invert Multiline &Enter Behavior"
        )
        self.invert_multiline_enter_check.SetValue(
            interface.get("invert_multiline_enter_behavior", False)
        )
        sizer.Add(self.invert_multiline_enter_check, 0, wx.ALL, 10)

        # Play typing sounds checkbox
        self.play_typing_sounds_check = wx.CheckBox(
            panel, label="Play &Typing Sounds While Editing"
        )
        self.play_typing_sounds_check.SetValue(
            interface.get("play_typing_sounds", True)
        )
        sizer.Add(self.play_typing_sounds_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        return panel

    def _create_tables_panel(self, parent):
        """Create the Local Table panel."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        local_table = self.options.get("local_table", {})

        # Start table as publicly visible dropdown
        visibility_label = wx.StaticText(
            panel, label="Start table as publicly &visible:"
        )
        sizer.Add(visibility_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.public_visibility_choice = wx.Choice(panel, choices=("always", "ask", "never"))
        current_visibility = local_table.get("start_as_visible", "always")
        self.public_visibility_choice.SetStringSelection(current_visibility)
        sizer.Add(
            self.public_visibility_choice, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10
        )

        # Start table with a password dropdown
        password_prompt_label = wx.StaticText(
            panel, label="Start table &with a password:"
        )
        sizer.Add(password_prompt_label, 0, wx.LEFT | wx.RIGHT, 10)

        self.password_prompt_choice = wx.Choice(panel, choices=("always", "ask", "never"))
        current_password_prompt = local_table.get("start_with_password", "never")
        self.password_prompt_choice.SetStringSelection(current_password_prompt)
        sizer.Add(
            self.password_prompt_choice, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10
        )

        # Default password text field
        default_password_label = wx.StaticText(panel, label="Default password &text:")
        sizer.Add(default_password_label, 0, wx.LEFT | wx.RIGHT, 10)

        self.default_password_input = wx.TextCtrl(
            panel, value=local_table.get("default_password_text", "")
        )
        sizer.Add(
            self.default_password_input, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10
        )

        # Label
        creation_subscription_label = wx.StaticText(
            panel, label="Receive &notifications when these game tables are created:"
        )
        sizer.Add(creation_subscription_label, 0, wx.ALL, 10)

        # Build game display names from server-provided list
        # games_list is a list of dicts with 'type' and 'name' keys
        game_display_names = [game["name"] for game in self.games_list]

        self.creation_subscription_list = wx.CheckListBox(panel, choices=game_display_names)

        # Check currently subscribed games
        local_table = self.options.get("local_table", {})
        creation_notifications = local_table.get("creation_notifications", {})

        for i, game_info in enumerate(self.games_list):
            game_type = game_info["type"]  # e.g., "pig", "uno", "milebymile"
            if creation_notifications.get(game_type, False):
                self.creation_subscription_list.Check(i)

        if self.creation_subscription_list.GetCount() > 0:
            self.creation_subscription_list.SetSelection(0)
            
        sizer.Add(
            self.creation_subscription_list,
            1,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            10,
        )
        self.bind_sfx_to_control(self.creation_subscription_list, True)

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

    def _reset_current_tab_fields(self, data_source):
        """Reset fields in the current tab to values from the given data source."""
        current_page = self.notebook.GetSelection()

        if current_page == 0:  # Audio tab
            self.music_spin.SetValue(int(data_source.get("audio", {}).get("music_volume", 20)))
            self.ambience_spin.SetValue(int(data_source.get("audio", {}).get("ambience_volume", 20)))

            if self.sound_manager:
                self.sound_manager.set_music_volume(
                    data_source.get("audio", {}).get("music_volume", 20) / 100.0
                )
                self.sound_manager.set_ambience_volume(
                    data_source.get("audio", {}).get("ambience_volume", 20) / 100.0
                )

        elif current_page == 1:  # Social tab
            social = data_source.get("social", {})
            self.mute_global_check.SetValue(social.get("mute_global_chat", False))
            self.mute_table_check.SetValue(social.get("mute_table_chat", False))

        elif current_page == 2:  # Interface tab
            interface = data_source.get("interface", {})
            self.invert_multiline_enter_check.SetValue(
                interface.get("invert_multiline_enter_behavior", False)
            )
            self.play_typing_sounds_check.SetValue(
                interface.get("play_typing_sounds", True)
            )

        elif current_page == 3:  # Local Table tab
            local_table = data_source.get("local_table", {})
            self.public_visibility_choice.SetStringSelection(local_table.get("start_as_visible", "always"))
            self.password_prompt_choice.SetStringSelection(local_table.get("start_with_password", "never"))
            self.default_password_input.SetValue(local_table.get("default_password_text", ""))

            creation_notifications = local_table.get("creation_notifications", {})
            for i, game_info in enumerate(self.games_list):
                game_type = game_info["type"]
                self.creation_subscription_list.Check(
                    i, creation_notifications.get(game_type, False)
                )

    def on_reset_to_last_used(self, event):
        """Reset fields in current tab to last saved values."""
        current_page = self.notebook.GetSelection()
        current_tab_name = self.tab_names[current_page]

        result = wx.MessageBox(
            f"Reset {current_tab_name} settings to saved values?",
            "Confirm Reset",
            wx.YES_NO | wx.ICON_QUESTION,
        )

        if result == wx.YES:
            # Refresh options from config
            self.options = self.config_manager.get_client_options()
            self._reset_current_tab_fields(self.options)

    def on_save(self, event):
        """Save changes and close dialog."""
        # Get current values from controls
        music_volume = self.music_spin.GetValue()
        ambience_volume = self.ambience_spin.GetValue()

        # Save audio settings
        self.config_manager.set_client_option("audio/music_volume", music_volume, create_mode=True)
        self.config_manager.set_client_option("audio/ambience_volume", ambience_volume, create_mode=True)

        # Save social settings
        mute_global = self.mute_global_check.GetValue()
        mute_table = self.mute_table_check.GetValue()

        self.config_manager.set_client_option("social/mute_global_chat", mute_global, create_mode=True)
        self.config_manager.set_client_option("social/mute_table_chat", mute_table, create_mode=True)

        # Save interface settings
        invert_multiline_enter = self.invert_multiline_enter_check.GetValue()
        play_typing_sounds = self.play_typing_sounds_check.GetValue()
        
        self.config_manager.set_client_option(
            "interface/invert_multiline_enter_behavior", invert_multiline_enter, create_mode=True
        )
        self.config_manager.set_client_option("interface/play_typing_sounds", play_typing_sounds, create_mode=True)

        # Save Local Table settings
        public_visibility = self.public_visibility_choice.GetStringSelection()
        password_prompt = self.password_prompt_choice.GetStringSelection()
        default_password = self.default_password_input.GetValue()

        self.config_manager.set_client_option("local_table/start_as_visible", public_visibility, create_mode=True)
        self.config_manager.set_client_option("local_table/start_with_password", password_prompt, create_mode=True)
        self.config_manager.set_client_option("local_table/default_password_text", default_password, create_mode=True)

        # Save updates to subscriptions
        for i, game_info in enumerate(self.games_list):
            game_type = game_info["type"]
            is_checked = self.creation_subscription_list.IsChecked(i)
            self.config_manager.set_client_option(
                f"local_table/creation_notifications/{game_type}", is_checked, create_mode=True
            )

        # Close dialog
        self.EndModal(wx.ID_OK)

    def on_done(self, event):
        """Close dialog without saving (unless Apply was used - but we removed Apply)."""
        self.EndModal(wx.ID_CANCEL)

    def on_close(self, event):
        """Handle window close."""
        self.EndModal(wx.ID_CANCEL)
