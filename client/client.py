"""
PlayAural Client (v0.1)
A wxPython-based client for PlayAural with websocket support.
Features:
- Menu list with multiletter navigation (toggle-able)
- Chat input
- History display
- Alt+M shortcut to focus menu
"""

import wx
import logging
import sys
import os

# Fix CWD before importing modules that depend on it (sound_lib, etc)
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # Stream default is sys.stderr when filename is not specified
    # We do not output to a file to prevent cluttering the user directory
)

version = "0.1.11"

def main():
    """Main entry point for the PlayAural v0.1 client."""
    # Move imports here to ensure CWD is set first
    from ui import MainWindow
    from ui.login_dialog import LoginDialog
    
    app = wx.App(False)
    
    # Initialize config manager and localization
    from config_manager import ConfigManager
    config_manager = ConfigManager()
    
    # Get saved language or default to 'en'
    # Check default options
    locale = config_manager.get_client_options().get("interface_language", "en")
    
    from localization import Localization
    logging.getLogger("playaural").info(
        f"Starting PlayAural Client v{version} (Locale: {locale})"
    )
    Localization.init(locale=locale)

    disconnect_message = None
    
    while True:
        # Show login dialog
        login_dialog = LoginDialog(disconnect_message=disconnect_message, version=version)

        credentials = None
        came_from_failure = bool(disconnect_message)
        disconnect_message = None # Reset message for next iteration

        # Access the detected account from the dialog we just created.
        # If auto-login is set, trust the cached credentials and skip the dialog.
        # Skip if we came from a failure — user must see the error and act manually.
        # The server will reject bad credentials via on_login_failed, so there is
        # no need for a separate _test_connection round-trip that doubles the
        # number of WebSocket handshakes the user pays for on every startup.
        if login_dialog.account_id and not came_from_failure:
            account = login_dialog.config_manager.get_account_by_id(login_dialog.server_id, login_dialog.account_id)
            if account and account.get("auto_login", False):
                logging.getLogger("playaural").info("Auto-login: using cached credentials.")
                credentials = {
                    "username": account["username"],
                    "password": account["password"],
                    "server_url": login_dialog.server_url,
                    "server_id": login_dialog.server_id,
                    "account_id": login_dialog.account_id,
                    "config_manager": login_dialog.config_manager,
                }

        # If no auto-login or verification failed, show dialog
        if not credentials:
            if login_dialog.ShowModal() == wx.ID_OK:
                credentials = login_dialog.get_credentials()
            else:
                 login_dialog.Destroy()
                 break

        login_dialog.Destroy()

        if credentials:
            # Create main window with credentials
            frame = MainWindow(credentials)
            frame.Show()
            app.MainLoop()
            
            # Application loop finished (window closed)
            # Check for disconnect reason
            if hasattr(frame, 'disconnect_reason') and frame.disconnect_reason:
                if frame.disconnect_reason == "exit":
                    # Exit requested
                    break
                disconnect_message = frame.disconnect_reason
            else:
                # Normal close, exit
                break
        else:
            break


if __name__ == "__main__":
    main()
