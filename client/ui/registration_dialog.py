"""Registration dialog for PlayAural v0.1 client."""

import wx
import json
import asyncio
import threading
import websockets
import ssl
import sys
import os

# Ensure we can import localization
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from localization import Localization


class RegistrationDialog(wx.Dialog):
    """Registration dialog for creating new accounts."""

    def __init__(self, parent, server_url):
        """Initialize the registration dialog."""
        super().__init__(parent, title=Localization.get("reg-dialog-title"), size=(400, 350))

        self.server_url = server_url
        self.registered_username = None # Store success username
        self._create_ui()
        self.CenterOnScreen()

    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(panel, label=Localization.get("reg-title"))
        title_font = title.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        # Info text
        info_text = wx.StaticText(
            panel,
            label=Localization.get("reg-info"),
        )
        sizer.Add(info_text, 0, wx.ALL | wx.CENTER, 5)

        # Username
        username_label = wx.StaticText(panel, label=Localization.get("reg-username-label"))
        sizer.Add(username_label, 0, wx.LEFT | wx.TOP, 10)

        self.username_input = wx.TextCtrl(panel)
        sizer.Add(self.username_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        username_help = wx.StaticText(
            panel, label=Localization.get("reg-username-help")
        )
        username_help.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(username_help, 0, wx.LEFT | wx.RIGHT, 10)

        # Password
        password_label = wx.StaticText(panel, label=Localization.get("reg-password-label"))
        sizer.Add(password_label, 0, wx.LEFT | wx.TOP, 10)

        self.password_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.password_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Confirm Password
        confirm_label = wx.StaticText(panel, label=Localization.get("reg-confirm-password-label"))
        sizer.Add(confirm_label, 0, wx.LEFT | wx.TOP, 10)

        self.confirm_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.confirm_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.register_btn = wx.Button(panel, label=Localization.get("reg-register-btn"))
        self.register_btn.SetDefault()
        button_sizer.Add(self.register_btn, 0, wx.RIGHT, 5)

        cancel_btn = wx.Button(panel, wx.ID_CANCEL, Localization.get("common-cancel"))
        button_sizer.Add(cancel_btn, 0)

        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 10)

        # Set sizer
        panel.SetSizer(sizer)

        # Bind events
        self.register_btn.Bind(wx.EVT_BUTTON, self.on_register)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Set focus
        self.username_input.SetFocus()

    def on_register(self, event):
        """Handle register button click."""
        username = self.username_input.GetValue().strip()
        password = self.password_input.GetValue()
        confirm = self.confirm_input.GetValue()

        # Validate fields
        if not username:
            wx.MessageBox(Localization.get("reg-error-username"), Localization.get("common-error"), wx.OK | wx.ICON_ERROR)
            self.username_input.SetFocus()
            return

        if not password:
            wx.MessageBox(Localization.get("reg-error-password"), Localization.get("common-error"), wx.OK | wx.ICON_ERROR)
            self.password_input.SetFocus()
            return

        if password != confirm:
            wx.MessageBox(Localization.get("reg-error-match"), Localization.get("common-error"), wx.OK | wx.ICON_ERROR)
            self.confirm_input.SetFocus()
            return

        # Disable button during registration
        self.register_btn.Enable(False)

        # Send registration to server
        self._send_registration(username, password)

    def _send_registration(self, username, password):
        """Send registration packet to server."""
        # Run in a thread to avoid blocking UI
        thread = threading.Thread(
            target=self._register_thread,
            args=(username, password),
            daemon=True,
        )
        thread.start()

    def _register_thread(self, username, password):
        """Thread to handle registration."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_register_packet(username, password)
            )
            loop.close()

            # Show result on main thread
            wx.CallAfter(self._show_registration_result, result)
        except Exception as e:
            wx.CallAfter(self._show_registration_result, Localization.get("reg-connection-error", error=str(e)))

    async def _send_register_packet(self, username, password):
        """Send registration packet and wait for response."""
        try:
            # Create SSL context that allows self-signed certificates
            ssl_context = None
            if self.server_url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(self.server_url, ssl=ssl_context) as ws:
                # Send registration packet
                await ws.send(
                    json.dumps(
                        {
                            "type": "register",
                            "username": username,
                            "password": password,
                            "email": "", # Legacy field
                            "bio": "",   # Legacy field
                            "locale": Localization._locale,
                        }
                    )
                )

                # Wait for response
                message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(message)

                if data.get("type") == "register_response":
                    return data
                elif data.get("type") == "speak":
                    # Legacy server fallback
                    return {"status": "legacy", "text": data.get("text")}
                else:
                    return {"status": "error", "error": "unexpected", "text": Localization.get("reg-unexpected-error")}

        except asyncio.TimeoutError:
            return {"status": "error", "error": "timeout", "text": Localization.get("reg-timeout-error")}
        except Exception as e:
            return {"status": "error", "error": "exception", "text": Localization.get("reg-error-exception", error=str(e))}

    def _show_registration_result(self, result):
        """Show registration result to user."""
        self.register_btn.Enable(True)

        # Handle struct response
        if isinstance(result, dict) and "status" in result:
             status = result["status"]
             if status == "success":
                 # Save for pre-fill
                self.registered_username = self.username_input.GetValue().strip()
                wx.MessageBox(
                    result.get("text", Localization.get("reg-success-title")), 
                    Localization.get("reg-success-title"), 
                    wx.OK | wx.ICON_INFORMATION
                )
                self.EndModal(wx.ID_OK)
                return
             elif status == "error":
                 error_code = result.get("error")
                 msg = result.get("text", result.get("error"))
                 if error_code == "username_taken":
                      wx.MessageBox(msg, Localization.get("reg-failed-title"), wx.OK | wx.ICON_WARNING)
                 else:
                      wx.MessageBox(msg, Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)
                 return
             elif status == "legacy":
                 # Fallback to string matching
                 message = result.get("text", "")
                 pass 
        else:
             # String fallback (legacy error handling from _send wrapper)
             message = str(result)

        # Legacy String Matching (Robustness)
        is_success = "success" in message.lower() or "created" in message.lower() or "approval" in message.lower() or "thành công" in message.lower()
        is_taken = "pending" not in message.lower() and ("taken" in message.lower() or "exists" in message.lower())

        if is_success:
            self.registered_username = self.username_input.GetValue().strip()
            wx.MessageBox(
                message, Localization.get("reg-success-title"), wx.OK | wx.ICON_INFORMATION
            )
            self.EndModal(wx.ID_OK)
        elif is_taken:
             wx.MessageBox(message, Localization.get("reg-failed-title"), wx.OK | wx.ICON_WARNING)
        else:
            wx.MessageBox(message, Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event):
        """Handle cancel button click."""
        self.EndModal(wx.ID_CANCEL)
