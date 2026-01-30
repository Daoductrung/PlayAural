"""
PlayAural Client (v0.1.1)
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
    filename='playaural.log' if getattr(sys, 'frozen', False) else None
)

version = "0.1.1"

def main():
    """Main entry point for the PlayAural v0.1.1 client."""
    # Move imports here to ensure CWD is set first
    from ui import MainWindow
    from ui.login_dialog import LoginDialog
    
    app = wx.App(False)
    
    # Initialize config manager and localization
    from config_manager import ConfigManager
    config_manager = ConfigManager()
    
    # Get saved language or default to 'en'
    # Check default options
    locale = config_manager.profiles["client_options_defaults"].get("interface_language", "en")
    
    from localization import Localization
    logging.getLogger("playaural").info(
        f"Starting PlayAural Client v{version} (Locale: {locale})"
    )
    Localization.init(locale=locale)

    disconnect_message = None
    
    while True:
        # Show login dialog
        # Check for auto-login
        login_dialog = LoginDialog(disconnect_message=disconnect_message)
        
        credentials = None
        disconnect_message = None # Reset message
        
        # Check if we should auto-login
        # We must instantiate LoginDialog to know server_id and config, 
        # but more efficiently we can query config_manager directly if we knew the server ID.
        # But LoginDialog handles server ID initialization for "official_server".
        # So let's re-use LoginDialog logic but check internal state.
        # LoginDialog.__init__ checks existing account.
        
        # Access the detected account from the dialog we just created
        if login_dialog.account_id:
            account = login_dialog.config_manager.get_account_by_id(login_dialog.server_id, login_dialog.account_id)
            if account and account.get("auto_login", False):
                # Verify connection quickly (optional, but requested "verify on login")
                # The user requested "verify if successful login".
                # For auto-login, we assume we skip the dialog.
                # But we should probably verify credentials to be safe, ensuring "perfect feature".
                # LoginDialog has _test_connection but it's internal.
                # Let's verify.
                logging.getLogger("playaural").info("Auto-login: Verifying credentials...")
                if login_dialog._test_connection(account["username"], account["password"]):
                    credentials = {
                        "username": account["username"],
                        "password": account["password"],
                        "server_url": login_dialog.server_url,
                        "server_id": login_dialog.server_id,
                        "config_manager": login_dialog.config_manager,
                    }
                    logging.getLogger("playaural").info("Auto-login: Success.")

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
