"""Login dialog for PlayAural client."""

import wx
import sys
import os
import asyncio
import json
import websockets
import ssl
from pathlib import Path
from threading import Thread

# Add parent directory to path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager
from localization import Localization


class LoginDialog(wx.Dialog):
    """Login dialog with simplified flow."""

    def __init__(self, parent=None, disconnect_message=None):
        """Initialize the login dialog."""
        super().__init__(parent, title=Localization.get("login-title"), size=(450, 450))

        if disconnect_message:
            wx.CallAfter(lambda: wx.MessageBox(
                disconnect_message,
                Localization.get("common-disconnected"),
                wx.OK | wx.ICON_INFORMATION
            ))

        # Initialize config manager
        self.config_manager = ConfigManager()

        # Initialize Official Server
        self.server_id = "official_server"  # Using a fixed ID for the "Official" server
        # Ensure this server exists in config, if not create it default to official server
        if not self.config_manager.get_server_by_id(self.server_id):
            self.config_manager.add_server("Official Server", "wss://playaural.ddt.one", "443", server_id=self.server_id)
        
        self.server_url = self.config_manager.get_server_url(self.server_id)

        self.username = ""
        self.password = ""
        self.account_id = None
        self.auto_login = False

        self._create_ui()
        self.CenterOnScreen()

        # Auto-detect existing account
        self._check_existing_account()

    def _create_ui(self):
        """Create the UI components."""
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Title / Welcome Message
        self.title = wx.StaticText(self.panel, label=Localization.get("login-welcome-title"))
        title_font = self.title.GetFont()
        title_font.PointSize += 4
        title_font.Bold()
        self.title.SetFont(title_font)
        self.sizer.Add(self.title, 0, wx.ALL | wx.CENTER, 20)

        # Info Text
        self.info_text = wx.StaticText(self.panel, label=Localization.get("login-welcome-info"))
        self.sizer.Add(self.info_text, 0, wx.ALL | wx.CENTER, 10)

        # Content Sizers (swapped based on state)
        self.action_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.action_sizer, 1, wx.EXPAND | wx.ALL, 20)

        # Status text
        self.status_text = wx.StaticText(self.panel, label="")
        self.sizer.Add(self.status_text, 0, wx.ALL | wx.CENTER, 10)
        
        # Set sizer
        self.panel.SetSizer(self.sizer)

    def _check_existing_account(self):
        """Check if an account is already saved and update UI."""
        # Get accounts for our hardcoded server
        accounts = self.config_manager.get_server_accounts(self.server_id)
        
        # Just pick the last used one or the first one found
        last_account_id = self.config_manager.get_last_account_id(self.server_id)
        
        target_account = None
        if last_account_id and last_account_id in accounts:
            target_account = accounts[last_account_id]
            self.account_id = last_account_id
        elif accounts:
            # Fallback to first account
            self.account_id = list(accounts.keys())[0]
            target_account = accounts[self.account_id]

        self.action_sizer.Clear(True) # Clear previous buttons

        if target_account:
            self._show_logged_in_ui(target_account)
        else:
            self._show_guest_ui()
        
        self.panel.Layout()

    def _show_logged_in_ui(self, account):
        """Show UI for when user has an account."""
        self.username = account.get("username", "")
        self.password = account.get("password", "")
        self.auto_login = account.get("auto_login", False)

        # Logged in as...
        lbl = wx.StaticText(self.panel, label=Localization.get("login-logged-in-as", username=self.username))
        lbl_font = lbl.GetFont()
        lbl_font.PointSize += 2
        lbl.SetFont(lbl_font)
        self.action_sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 10)

        # Login Now Button
        btn_login = wx.Button(self.panel, label=Localization.get("login-btn-login-now"))
        btn_login.Bind(wx.EVT_BUTTON, self.on_login_cached)
        btn_login.SetDefault()
        self.action_sizer.Add(btn_login, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Auto Login Checkbox
        self.chk_auto = wx.CheckBox(self.panel, label=Localization.get("login-btn-auto-login"))
        self.chk_auto.SetValue(self.auto_login)
        self.action_sizer.Add(self.chk_auto, 0, wx.ALL | wx.CENTER, 10)

        # Remove Account Button
        btn_remove = wx.Button(self.panel, label=Localization.get("login-btn-remove-account"))
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove_account)
        self.action_sizer.Add(btn_remove, 0, wx.EXPAND | wx.TOP, 20)

        # Focus login button
        btn_login.SetFocus()

    def _show_guest_ui(self):
        """Show UI for new user."""
        # Register New Account
        btn_reg = wx.Button(self.panel, label=Localization.get("login-btn-register-new"))
        btn_reg.Bind(wx.EVT_BUTTON, self.on_register)
        self.action_sizer.Add(btn_reg, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Login with Existing (Not simplified yet, but let's assume manual entry or simplified flow later)
        # For now, we can reuse the old RegistrationDialog for registration, 
        # but for manual login without saved account, we might need a simple username/pass dialog.
        # However, the user request implies: "If chose to login...".
        # Let's add a "Login with Existing Account" which opens what?
        # Maybe we should use a simplified manual login dialog or reuse registration dialog mechanics (it has login fields?)
        # Wait, the prompt says: "Register new", "Login existing".
        # Let's allow creating a new account (RegistrationDialog).
        # For logging in existing, we'll need a tiny dialog to enter user/pass. 
        # For simplicity, let's assume we can trigger a manual login dialog here.
        
        btn_login_manual = wx.Button(self.panel, label=Localization.get("login-btn-login-existing"))
        btn_login_manual.Bind(wx.EVT_BUTTON, self.on_manual_login)
        self.action_sizer.Add(btn_login_manual, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Forgot Password Button
        btn_forgot_pw = wx.Button(self.panel, label=Localization.get("login-btn-forgot-password"))
        btn_forgot_pw.Bind(wx.EVT_BUTTON, self.on_forgot_password)
        self.action_sizer.Add(btn_forgot_pw, 0, wx.EXPAND | wx.BOTTOM, 10)

    def on_login_cached(self, event):
        """Login with current cached credentials."""
        self._verify_and_login(self.username, self.password)

    def on_remove_account(self, event):
        """Remove current account and reset UI."""
        if self.server_id and self.account_id:
            try:
                self.config_manager.delete_account(self.server_id, self.account_id)
                wx.MessageBox(
                    Localization.get("login-account-deleted"),
                    Localization.get("common-ok"),
                    wx.OK | wx.ICON_INFORMATION
                )
            except Exception as e:
                wx.MessageBox(f"Error: {e}", Localization.get("common-error"), wx.OK | wx.ICON_ERROR)
                
        self._check_existing_account()

    def on_register(self, event):
        """Open registration dialog."""
        if not self.server_url:
             wx.MessageBox(
                Localization.get("login-error-server-url"), Localization.get("common-error"), wx.OK | wx.ICON_ERROR
            )
             return

        from .registration_dialog import RegistrationDialog
        dlg = RegistrationDialog(self, self.server_url)
        if dlg.ShowModal() == wx.ID_OK:
            # Refresh UI logic after registration
            self._check_existing_account()
            
            # Auto-open manual login since they just registered, pre-filling username
            self.on_manual_login(None, prefill_username=dlg.registered_username)
        dlg.Destroy()
    
    def on_manual_login(self, event, prefill_username=None):
        """Show manual login input (simple username/password)."""
        # Simple dialog to get username/password
        dlg = wx.Dialog(self, title=Localization.get("login-manual-title"), size=(350, 250))
        pnl = wx.Panel(dlg)
        sz = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        lbl_inst = wx.StaticText(pnl, label=Localization.get("login-btn-login-existing"))
        font = lbl_inst.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_inst.SetFont(font)
        sz.Add(lbl_inst, 0, wx.ALL | wx.CENTER, 10)

        # Inputs
        input_sizer = wx.FlexGridSizer(2, 2, 10, 10)
        
        input_sizer.Add(wx.StaticText(pnl, label=Localization.get("login-account-label")), 0, wx.ALIGN_CENTER_VERTICAL)
        user_txt = wx.TextCtrl(pnl)
        if prefill_username:
            user_txt.SetValue(prefill_username)
        input_sizer.Add(user_txt, 1, wx.EXPAND)

        input_sizer.Add(wx.StaticText(pnl, label=Localization.get("reg-password-label")), 0, wx.ALIGN_CENTER_VERTICAL)
        pass_txt = wx.TextCtrl(pnl, style=wx.TE_PASSWORD)
        input_sizer.Add(pass_txt, 1, wx.EXPAND)
        
        input_sizer.AddGrowableCol(1, 1)
        sz.Add(input_sizer, 1, wx.EXPAND | wx.ALL, 15)

        # Buttons
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, label=Localization.get("login-login-btn"))
        ok_btn.SetDefault()
        btn_sz.Add(ok_btn, 0, wx.ALL, 5)
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, label=Localization.get("common-cancel"))
        btn_sz.Add(cancel_btn, 0, wx.ALL, 5)
        sz.Add(btn_sz, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        
        pnl.SetSizer(sz)
        dlg.CenterOnParent()
        
        # Forgot password button in manual login
        btn_forgot_pw_man = wx.Button(pnl, label=Localization.get("login-btn-forgot-password"))
        btn_forgot_pw_man.Bind(wx.EVT_BUTTON, lambda e: self._handle_manual_forgot_password(dlg, e))
        btn_sz.Add(btn_forgot_pw_man, 0, wx.ALL, 5)

        pnl.SetSizer(sz)
        dlg.CenterOnParent()

        # Focus appropriately
        if prefill_username:
            pass_txt.SetFocus()
        else:
            user_txt.SetFocus()
        
        if dlg.ShowModal() == wx.ID_OK:
            username = user_txt.GetValue().strip()
            password = pass_txt.GetValue()
            if username and password:
                self._verify_and_login(username, password)
        dlg.Destroy()

    def _handle_manual_forgot_password(self, parent_dlg, event):
        """Helper to close manual login dialog and launch forgot password."""
        parent_dlg.EndModal(wx.ID_CANCEL)
        wx.CallAfter(self.on_forgot_password, None)

    def on_forgot_password(self, event):
        """Handle forgot password flow."""
        if not self.server_url:
             wx.MessageBox(
                Localization.get("login-error-server-url"), Localization.get("common-error"), wx.OK | wx.ICON_ERROR
            )
             return

        # 1. Prompt for Email
        dlg = wx.TextEntryDialog(
            self,
            Localization.get("forgot-password-prompt"),
            Localization.get("login-btn-forgot-password")
        )

        if dlg.ShowModal() == wx.ID_OK:
            email = dlg.GetValue().strip()
            if email:
                self.status_text.SetLabel(Localization.get("login-info-verifying"))
                self.panel.Layout()
                wx.Yield()

                # Send request in background thread
                import threading
                thread = threading.Thread(
                    target=self._request_password_reset_thread,
                    args=(email,),
                    daemon=True,
                )
                thread.start()
        dlg.Destroy()

    def _request_password_reset_thread(self, email):
        """Background thread to send reset request."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_password_reset_request(email)
            )
            loop.close()

            # Show result on main thread
            wx.CallAfter(self._handle_password_reset_response, result, email)
        except Exception as e:
            wx.CallAfter(self._show_registration_result, Localization.get("reg-connection-error", error=str(e)))

    async def _send_password_reset_request(self, email):
        """Send the reset request to the server."""
        try:
            ssl_context = None
            if self.server_url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(self.server_url, ssl=ssl_context) as ws:
                await ws.send(
                    json.dumps(
                        {
                            "type": "request_password_reset",
                            "email": email,
                            "locale": Localization._locale,
                        }
                    )
                )

                # Wait for response (can take a moment if server is actually sending email)
                message = await asyncio.wait_for(ws.recv(), timeout=15.0)
                data = json.loads(message)
                return data

        except asyncio.TimeoutError:
            return {"status": "error", "error": "timeout", "text": Localization.get("reg-timeout-error")}
        except Exception as e:
            return {"status": "error", "error": "exception", "text": Localization.get("reg-error-exception", error=str(e))}

    def _handle_password_reset_response(self, result, email):
        """Handle the server's response to the reset request."""
        self.status_text.SetLabel("")

        if isinstance(result, dict) and "status" in result:
             status = result["status"]
             if status == "success":
                 # Open code submission dialog
                 wx.MessageBox(
                     result.get("text", Localization.get("success-reset-email-sent")),
                     Localization.get("login-btn-forgot-password"),
                     wx.OK | wx.ICON_INFORMATION
                 )
                 self._show_reset_code_dialog(email)
             elif status == "error":
                 msg = result.get("text", result.get("error"))
                 wx.MessageBox(msg, Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)
        else:
             # String fallback
             wx.MessageBox(str(result), Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)

    def _show_reset_code_dialog(self, email):
        """Show the dialog to enter the 6-digit code and new password."""
        dlg = wx.Dialog(self, title=Localization.get("login-btn-forgot-password"), size=(400, 350))
        pnl = wx.Panel(dlg)
        sz = wx.BoxSizer(wx.VERTICAL)

        # Instructions
        lbl_inst = wx.StaticText(pnl, label=Localization.get("reset-code-instructions"))
        sz.Add(lbl_inst, 0, wx.ALL | wx.CENTER, 10)

        input_sizer = wx.FlexGridSizer(3, 2, 10, 10)

        # Code
        code_lbl = wx.StaticText(pnl, label=Localization.get("reset-code-prompt"))
        input_sizer.Add(code_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        code_txt = wx.TextCtrl(pnl)
        input_sizer.Add(code_txt, 1, wx.EXPAND)

        # New Password
        pass_lbl = wx.StaticText(pnl, label=Localization.get("new-password-prompt"))
        input_sizer.Add(pass_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        pass_txt = wx.TextCtrl(pnl, style=wx.TE_PASSWORD)
        input_sizer.Add(pass_txt, 1, wx.EXPAND)

        # Confirm New Password
        confirm_lbl = wx.StaticText(pnl, label=Localization.get("reg-confirm-password-label"))
        input_sizer.Add(confirm_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        confirm_txt = wx.TextCtrl(pnl, style=wx.TE_PASSWORD)
        input_sizer.Add(confirm_txt, 1, wx.EXPAND)

        input_sizer.AddGrowableCol(1, 1)
        sz.Add(input_sizer, 1, wx.EXPAND | wx.ALL, 15)

        # Buttons
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, label=Localization.get("common-ok"))
        ok_btn.SetDefault()
        btn_sz.Add(ok_btn, 0, wx.ALL, 5)
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, label=Localization.get("common-cancel"))
        btn_sz.Add(cancel_btn, 0, wx.ALL, 5)
        sz.Add(btn_sz, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        pnl.SetSizer(sz)
        dlg.CenterOnParent()
        code_txt.SetFocus()

        while dlg.ShowModal() == wx.ID_OK:
            code = code_txt.GetValue().strip()
            new_password = pass_txt.GetValue()
            confirm_password = confirm_txt.GetValue()

            if not code or not new_password:
                wx.MessageBox(
                    Localization.get("auth-username-password-required"),
                    Localization.get("common-error"),
                    wx.OK | wx.ICON_ERROR
                )
                continue

            import re
            has_letters = bool(re.search(r'[a-zA-Z]', new_password))
            has_numbers = bool(re.search(r'[0-9]', new_password))

            if len(new_password) < 8 or not has_letters or not has_numbers:
                wx.MessageBox(
                    Localization.get("auth-error-password-weak"),
                    Localization.get("common-error"),
                    wx.OK | wx.ICON_ERROR
                )
                continue

            if new_password != confirm_password:
                wx.MessageBox(
                    Localization.get("reg-error-password-match"),
                    Localization.get("common-error"),
                    wx.OK | wx.ICON_ERROR
                )
                continue

            self.status_text.SetLabel(Localization.get("login-info-verifying"))
            self.panel.Layout()
            wx.Yield()

            # Send verification request in background thread
            import threading
            thread = threading.Thread(
                target=self._submit_reset_code_thread,
                args=(email, code, new_password),
                daemon=True,
            )
            thread.start()
            break

        dlg.Destroy()

    def _submit_reset_code_thread(self, email, code, new_password):
        """Background thread to submit the reset code."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_submit_reset_code(email, code, new_password)
            )
            loop.close()

            # Show result on main thread
            wx.CallAfter(self._handle_submit_code_response, result, email, new_password)
        except Exception as e:
            wx.CallAfter(self._show_registration_result, Localization.get("reg-connection-error", error=str(e)))

    async def _send_submit_reset_code(self, email, code, new_password):
        """Send the reset code validation request to the server."""
        try:
            ssl_context = None
            if self.server_url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(self.server_url, ssl=ssl_context) as ws:
                await ws.send(
                    json.dumps(
                        {
                            "type": "submit_reset_code",
                            "email": email,
                            "code": code,
                            "new_password": new_password,
                            "locale": Localization._locale,
                        }
                    )
                )

                message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(message)
                return data

        except asyncio.TimeoutError:
            return {"status": "error", "error": "timeout", "text": Localization.get("reg-timeout-error")}
        except Exception as e:
            return {"status": "error", "error": "exception", "text": Localization.get("reg-error-exception", error=str(e))}

    def _handle_submit_code_response(self, result, email, new_password):
        """Handle the server's response to the code submission."""
        self.status_text.SetLabel("")

        if isinstance(result, dict) and "status" in result:
             status = result["status"]
             if status == "success":
                 wx.MessageBox(
                     result.get("text", Localization.get("success-password-reset")),
                     Localization.get("login-btn-forgot-password"),
                     wx.OK | wx.ICON_INFORMATION
                 )
                 # Re-fetch username if returned, or we could just prompt manual login
                 # Let's prompt manual login with the known password
                 username = result.get("username", "")
                 self.on_manual_login(None, prefill_username=username)
             elif status == "error":
                 msg = result.get("text", result.get("error"))
                 wx.MessageBox(msg, Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)
        else:
             wx.MessageBox(str(result), Localization.get("reg-failed-title"), wx.OK | wx.ICON_ERROR)


    def _verify_and_login(self, username, password):
        """Verify credentials by connecting to server, then save and exit."""
        # CAPTURE UI STATE EARLY to prevent RuntimeError if dialog is closed during async call
        auto_login_val = self.auto_login
        if hasattr(self, 'chk_auto') and self.chk_auto:
            try:
                auto_login_val = self.chk_auto.GetValue()
            except RuntimeError:
                pass # Object deleted, use default

        self.status_text.SetLabel(Localization.get("login-info-verifying"))
        self.panel.Layout()
        wx.Yield() # Update UI
        
        # Check connection
        result = self._test_connection(username, password)
        
        # NOTE: Dialog might have been destroyed here!
        if not self or not self.panel: 
            return

        if result is True:
            try:
                self.status_text.SetLabel(Localization.get("login-info-success"))
                self.panel.Layout()
            except RuntimeError:
                return # UI dead

            try:
                # Find if account with this username already exists to prevent duplicates
                target_account_id = self.account_id
                
                # If we don't have an ID yet (manual login), search for username
                if not target_account_id:
                    accounts = self.config_manager.get_server_accounts(self.server_id)
                    for acc_id, acc_data in accounts.items():
                        if acc_data.get("username") == username:
                            target_account_id = acc_id
                            break
                
                if target_account_id:
                    # Update existing
                    self.config_manager.update_account(
                        self.server_id, 
                        target_account_id, 
                        username=username, 
                        password=password,
                        auto_login=auto_login_val
                    )
                    self.config_manager.set_last_account(self.server_id, target_account_id)
                else:
                    # Add new
                    new_account_id = self.config_manager.add_account(
                        self.server_id,
                        username,
                        password,
                        auto_login=auto_login_val
                    )
                    if new_account_id:
                         self.config_manager.set_last_account(self.server_id, new_account_id)
                
                # Set this values for get_credentials
                self.username = username
                self.password = password
                
                self.EndModal(wx.ID_OK)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                wx.MessageBox(f"Login Error: {e}", Localization.get("common-error"), wx.OK | wx.ICON_ERROR)
                try:
                    self.status_text.SetLabel(Localization.get("login-info-failed"))
                except RuntimeError:
                    pass

        else:
            # Handle error codes
            error_msg = Localization.get("login-info-failed")
            if result == "timeout":
                error_msg = Localization.get("login-error-connection-timeout")
            elif result == "refused":
                 error_msg = Localization.get("login-error-connection-refused")
            elif result == "auth_failed":
                  error_msg = Localization.get("login-info-failed") # Verification failed
            elif isinstance(result, dict) and result.get("type") == "login_failed":
                 reason = result.get("reason")
                 if reason == "wrong_password":
                      error_msg = Localization.get("auth-error-wrong-password")
                 elif reason == "user_not_found":
                      error_msg = Localization.get("auth-error-user-not-found")
                 else:
                      error_msg = Localization.get("login-info-failed")
            elif isinstance(result, str) and result.startswith("error:"):
                  error_msg = Localization.get("login-error-unknown", error=result)
            
            try:
                self.status_text.SetLabel(error_msg)
                wx.MessageBox(error_msg, Localization.get("login-failed-title"), wx.OK | wx.ICON_ERROR)
            except RuntimeError:
                pass

    def _test_connection(self, username, password):
        """Test connection and auth synchronously (blocking UI briefly)."""
        try:
            return asyncio.run(self._async_test(username, password))
        except Exception as e:
            print(f"Async Loop Error: {e}")
            return False

    async def _async_test(self, username, password):
        try:
             ssl_context = None
             if self.server_url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
             async with websockets.connect(self.server_url, ssl=ssl_context) as ws:
                # Send authorize
                await ws.send(json.dumps({
                    "type": "authorize",
                    "username": username,
                    "password": password,
                    "major": 0, "minor": 1, "patch": 0
                }))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "authorize_success":
                        return True
                    elif data.get("type") == "login_failed":
                        return data
                    else:
                        return "auth_failed"
                except asyncio.TimeoutError:
                    return "timeout"
                    
        except ConnectionRefusedError:
            return "refused"
        except OSError as e:
            # Check for Windows socket error codes if needed, or generic OSError
            if "WinError 10061" in str(e): # Connection refused
                return "refused"
            return f"os_error:{str(e)}"
        except Exception as e:
             # websockets.exceptions.InvalidURI, etc
             return f"error:{str(e)}"

    def get_credentials(self):
        """Get the login credentials."""
        return {
            "username": self.username,
            "password": self.password,
            "server_url": self.server_url,
            "server_id": self.server_id,
            "config_manager": self.config_manager,
        }
