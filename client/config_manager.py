"""Configuration manager for Play Aural client.

Handles client-side configuration including:
- Server management with user accounts (identities.json - private)
- Global default options (option_profiles.json - shareable)
- Per-server option overrides (option_profiles.json - shareable)
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

def get_item_from_dict(dictionary: dict, key_path: (str, tuple), *, create_mode: bool= False):
  """Return the item in a dictionary, typically a nested layer dict.
  Optionally create keys that don't exist, or require the full path to exist already.
  This function supports an infinite number of layers."""
  if isinstance(key_path, str)  and len(key_path)>0:
    if key_path[0] == "/": key_path = key_path[1:]
    if key_path[-1] == "/": key_path = key_path[:-1]
    key_path = key_path.split("/")
  scope= dictionary
  for l in range(len(key_path)):
    if key_path[l] == "": continue
    layer= key_path[l]
    if layer not in scope:
      if not create_mode: raise KeyError(f"Key '{layer}' not in "+ (("nested dictionary "+ '/'.join(key_path[:l])) if l>0 else "root dictionary")+ ".")
      scope[layer] = {}
    scope= scope[layer]
  return scope

def set_item_in_dict(dictionary: dict, key_path: (str, tuple), value, *, create_mode: bool= False) -> bool:
  """Modify the value of an item in a dictionary.
  Optionally create keys that don't exist, or require the full path to exist already.
  This function supports an infinite number of layers."""
  if isinstance(key_path, str) and len(key_path)>0:
    if key_path[0] == "/": key_path = key_path[1:]
    if key_path[-1] == "/": key_path = key_path[:-1]
    key_path = key_path.split("/")
  if not key_path or key_path[-1] == "": raise ValueError("No dictionary key path was specified.")
  final_key = key_path.pop(-1)
  obj = get_item_from_dict(dictionary, key_path, create_mode = create_mode)
  if not isinstance(obj, dict): raise TypeError(f"Expected type 'dict', instead got '{type(obj)}'.")
  if not create_mode and final_key not in obj: raise KeyError(f"Key '{final_key}' not in dictionary '{key_path}'.")
  obj[final_key] = value
  return True

def delete_item_from_dict(dictionary: dict, key_path: (str, tuple), *, delete_empty_layers: bool = True) -> bool:
  """Delete an item in a dictionary.
  Optionally delete layers that are empty.
  This function supports an infinite number of layers."""
  if isinstance(key_path, str) and len(key_path)>0:
    if key_path[0] == "/": key_path = key_path[1:]
    if key_path[-1] == "/": key_path = key_path[:-1]
    key_path = key_path.split("/")
  if not key_path or key_path[-1] == "": raise ValueError("No dictionary key path was specified.")
  final_key = key_path.pop(-1)
  obj = get_item_from_dict(dictionary, key_path)
  if not isinstance(obj, dict): raise TypeError(f"Expected type 'dict', instead got '{type(obj)}'.")
  if final_key not in obj: return False
  del obj[final_key]
  if not delete_empty_layers: return True
  # Walk from deepest to shallowest, removing empty dicts
  for i in range(len(key_path), 0, -1):
    try:
      obj = get_item_from_dict(dictionary, key_path[:i])
      if isinstance(obj, dict) and not obj:  # Empty dict
        if i == 1:
          del dictionary[key_path[0]]
        else:
          parent = get_item_from_dict(dictionary, key_path[:i-1])
          del parent[key_path[i-1]]
    except KeyError:
      break
  return True


class ConfigManager:
    """Manages client configuration and per-server settings.

    Uses two separate files:
    - identities.json: Contains servers with user accounts (private, not shareable)
    - option_profiles.json: Contains client options (shareable, no credentials)
    """

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the config manager.

        Args:
            base_path: Base directory path. Defaults to ~/.playaural/
        """
        if base_path is None:
            import os
            appdata = os.getenv("APPDATA")
            if appdata:
                base_path = Path(appdata) / "ddt.one" / "PlayAural"
            else:
                # Fallback if APPDATA is not set
                base_path = Path.home() / ".playaural"

        self.base_path = base_path
        self.identities_path = base_path / "identities.json"
        self.profiles_path = base_path / "option_profiles.json"

        self.identities = self._load_identities()
        self.profiles = self._load_profiles()

    def _load_identities(self) -> Dict[str, Any]:
        """Load identities from file (servers with user accounts)."""
        if self.identities_path.exists():
            try:
                with open(self.identities_path, "r") as f:
                    identities = json.load(f)
                    return identities
            except Exception as e:
                print(f"Error loading identities: {e}")
                return self._get_default_identities()

        return self._get_default_identities()

    def _get_default_identities(self) -> Dict[str, Any]:
        """Get default identities structure."""
        # Returned to localhost for testing as requested
        return {
            "last_server_id": None,
            "servers": {},  # server_id -> server info with accounts
        }

    def _load_profiles(self) -> Dict[str, Any]:
        """Load option profiles from file (shareable, no credentials)."""
        if not self.profiles_path.exists():
            return self._get_default_profiles()

        try:
            with open(self.profiles_path, "r") as f:
                profiles = json.load(f)
                # Migrate old combined config if needed
                return self._migrate_profiles(profiles)
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return self._get_default_profiles()

    def _get_default_profiles(self) -> Dict[str, Any]:
        """Get default profiles structure (shareable)."""
        return {
            "client_options_defaults": {
                "interface_language": "en",
                "audio": {"music_volume": 20, "ambience_volume": 20},
                "social": {
                    "mute_global_chat": False,
                    "mute_table_chat": False,
                },
                "interface": {
                    "invert_multiline_enter_behavior": False,
                    "play_typing_sounds": True,
                },
                "local_table": {
                    "start_as_visible": "always",
                    "start_with_password": "never",
                    "default_password_text": "",
                    "creation_notifications": {}},  # Will be populated dynamically
            },
        }

    def _migrate_profiles(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate profiles to fix data issues.

        Args:
            profiles: The loaded profiles dictionary

        Returns:
            Migrated profiles dictionary
        """
        needs_save = False

        # Migration: Convert old "servers" structure to "server_options"
        if "servers" in profiles and "server_options" not in profiles:
            profiles["server_options"] = {}
            for server_id, server_info in profiles["servers"].items():
                if "options_overrides" in server_info and server_info["options_overrides"]:
                    profiles["server_options"][server_id] = server_info["options_overrides"]
            del profiles["servers"]
            needs_save = True
            print("Migrated 'servers' to 'server_options' in profiles")

        # Ensure server_options exists
        if "server_options" not in profiles:
            profiles["server_options"] = {}

        # Migration: Rename table_creations to local_table/creation_notifications
        # and add new default options to local_table
        if "client_options_defaults" in profiles:
            defaults = profiles["client_options_defaults"]
            if "table_creations" in defaults:
                table_creations_value = defaults.pop("table_creations")
                if "local_table" not in defaults:
                    defaults["local_table"] = {}
                # Build local_table with proper ordering (new options before creation_notifications)
                new_local_table = {
                    "start_as_visible": defaults["local_table"].get("start_as_visible", "always"),
                    "start_with_password": defaults["local_table"].get("start_with_password", "never"),
                    "default_password_text": defaults["local_table"].get("default_password_text", ""),
                    "creation_notifications": table_creations_value,
                }
                # Preserve any other existing keys in local_table
                for key, value in defaults["local_table"].items():
                    if key not in new_local_table:
                        new_local_table[key] = value
                defaults["local_table"] = new_local_table
                needs_save = True
                print("Migrated 'table_creations' -> 'local_table/creation_notifications' in default profile")

        # Check each server override for table_creations
        for server_id, overrides in profiles.get("server_options", {}).items():
            if "table_creations" in overrides:
                table_creations_value = overrides.pop("table_creations")
                if "local_table" not in overrides:
                    overrides["local_table"] = {}
                # Build local_table with proper ordering
                new_local_table = {
                    "start_as_visible": overrides["local_table"].get("start_as_visible", "always"),
                    "start_with_password": overrides["local_table"].get("start_with_password", "never"),
                    "default_password_text": overrides["local_table"].get("default_password_text", ""),
                    "creation_notifications": table_creations_value,
                }
                # Preserve any other existing keys in local_table
                for key, value in overrides["local_table"].items():
                    if key not in new_local_table:
                        new_local_table[key] = value
                overrides["local_table"] = new_local_table
                needs_save = True
                print(f"Migrated 'table_creations' -> 'local_table/creation_notifications' in server {server_id}")

        # Save immediately if migration occurred
        if needs_save:
            self.profiles = profiles
            self.save_profiles()
            print("Profile migration completed and saved to disk.")

        return profiles

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any], override_wins: bool = True
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries with configurable precedence.

        Supports infinite nesting depth.

        Args:
            base: Base dictionary
            override: Dictionary to merge into base
            override_wins: If True, override values take precedence on conflicts.
                           If False, base values take precedence (override fills missing keys only).

        Returns:
            Merged dictionary
        """
        result = self._deep_copy(base)

        for key, value in override.items():
            if key not in result:
                result[key] = self._deep_copy(value)
            elif isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value, override_wins)
            elif override_wins:
                result[key] = self._deep_copy(value)
            # else: base wins, keep existing value

        return result

    def save_identities(self):
        """Save identities to file."""
        try:
            # Create directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)

            with open(self.identities_path, "w") as f:
                json.dump(self.identities, f, indent=2)
        except Exception as e:
            print(f"Error saving identities: {e}")

    def save_profiles(self):
        """Save option profiles to file."""
        try:
            # Create config directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)

            with open(self.profiles_path, "w") as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def save(self):
        """Save both identities and profiles."""
        self.save_identities()
        self.save_profiles()

    # ========== Server Management ==========

    def get_last_server_id(self) -> Optional[str]:
        """Get ID of last connected server."""
        return self.identities.get("last_server_id")

    def get_last_account_id(self, server_id: str) -> Optional[str]:
        """Get ID of last used account for a server.

        Args:
            server_id: Server ID

        Returns:
            Account ID or None if not set
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("last_account_id")
        return None

    def get_server_by_id(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get server info by ID.

        Args:
            server_id: Unique server ID

        Returns:
            Server info dict or None if not found
        """
        return self.identities["servers"].get(server_id)

    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all servers.

        Returns:
            Dict mapping server_id to server info
        """
        return self.identities["servers"]

    def add_server(
        self,
        name: str,
        host: str,
        port: str,
        notes: str = "",
        server_id: Optional[str] = None,
    ) -> str:
        """Add a new server.

        Args:
            name: Server display name
            host: Server host address
            port: Server port
            notes: Optional notes about the server
            server_id: Optional specific server ID (otherwise generated)

        Returns:
            New server ID
        """
        if server_id is None:
            server_id = str(uuid.uuid4())
            
        self.identities["servers"][server_id] = {
            "server_id": server_id,
            "name": name,
            "host": host,
            "port": port,
            "notes": notes,
            "accounts": {},  # account_id -> account info
        }
        self.save_identities()
        return server_id

    def update_server(
        self,
        server_id: str,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        """Update server information.

        Args:
            server_id: Server ID
            name: New server name (if provided)
            host: New host address (if provided)
            port: New port (if provided)
            notes: New notes (if provided)
        """
        if server_id not in self.identities["servers"]:
            return

        server = self.identities["servers"][server_id]
        if name is not None:
            server["name"] = name
        if host is not None:
            server["host"] = host
        if port is not None:
            server["port"] = port
        if notes is not None:
            server["notes"] = notes
        self.save_identities()

    def delete_server(self, server_id: str):
        """Delete a server and all its accounts.

        Args:
            server_id: Server ID to delete
        """
        if server_id in self.identities["servers"]:
            del self.identities["servers"][server_id]
            # Clear last_server_id if it was this server
            if self.identities.get("last_server_id") == server_id:
                self.identities["last_server_id"] = None
            self.save_identities()

    def get_server_display_name(self, server_id: str) -> str:
        """Get display name for a server.

        Args:
            server_id: Server ID

        Returns:
            Display name
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("name", "Unknown Server")
        return "Unknown Server"

    def get_server_url(self, server_id: str) -> Optional[str]:
        """Build WebSocket URL for a server.

        Args:
            server_id: Server ID

        Returns:
            WebSocket URL or None if server not found
        """
        server = self.get_server_by_id(server_id)
        if not server:
            return None

        host = server.get("host", "")
        port = server.get("port", "8000")

        # Check if host already has a scheme
        if "://" in host:
            scheme = host.split("://")[0].lower()
            host_part = host.split("://", 1)[1]
            return f"{scheme}://{host_part}:{port}"
        else:
            return f"ws://{host}:{port}"

    def set_last_server(self, server_id: str):
        """Set the last connected server.

        Args:
            server_id: Server ID
        """
        self.identities["last_server_id"] = server_id
        self.save_identities()

    # ========== Account Management ==========

    def get_server_accounts(self, server_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all accounts for a server.

        Args:
            server_id: Server ID

        Returns:
            Dict mapping account_id to account info
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("accounts", {})
        return {}

    def get_account_by_id(
        self, server_id: str, account_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get account info by ID.

        Args:
            server_id: Server ID
            account_id: Account ID

        Returns:
            Account info dict or None if not found
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("accounts", {}).get(account_id)
        return None

    def add_account(
        self,
        server_id: str,
        username: str,
        password: str,
        notes: str = "",
        auto_login: bool = False,
    ) -> Optional[str]:
        """Add a new account to a server.

        Args:
            server_id: Server ID
            username: Account username
            password: Account password
            notes: Optional notes about the account
            auto_login: Whether to auto-login with this account

        Returns:
            New account ID, or None if server not found
        """
        if server_id not in self.identities["servers"]:
            return None

        account_id = str(uuid.uuid4())
        if "accounts" not in self.identities["servers"][server_id]:
            self.identities["servers"][server_id]["accounts"] = {}

        self.identities["servers"][server_id]["accounts"][account_id] = {
            "account_id": account_id,
            "username": username,
            "password": password,
            "notes": notes,
            "auto_login": auto_login,
        }
        self.save_identities()
        return account_id

    def update_account(
        self,
        server_id: str,
        account_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        notes: Optional[str] = None,
        auto_login: Optional[bool] = None,
    ):
        """Update account information.

        Args:
            server_id: Server ID
            account_id: Account ID
            username: New username (if provided)
            password: New password (if provided)
            notes: New notes (if provided)
            auto_login: New auto-login settings (if provided)
        """
        account = self.get_account_by_id(server_id, account_id)
        if not account:
            return

        if username is not None:
            account["username"] = username
        if password is not None:
            account["password"] = password
        if notes is not None:
            account["notes"] = notes
        if auto_login is not None:
             account["auto_login"] = auto_login
        self.save_identities()

    def delete_account(self, server_id: str, account_id: str):
        """Delete an account from a server.

        Args:
            server_id: Server ID
            account_id: Account ID to delete
        """
        server = self.get_server_by_id(server_id)
        if server and account_id in server.get("accounts", {}):
            del server["accounts"][account_id]
            # Clear last_account_id if it was this account
            if server.get("last_account_id") == account_id:
                server["last_account_id"] = None
            self.save_identities()

    def set_last_account(self, server_id: str, account_id: str):
        """Set the last used account for a server.

        Args:
            server_id: Server ID
            account_id: Account ID
        """
        self.identities["last_server_id"] = server_id
        server = self.get_server_by_id(server_id)
        if server:
            server["last_account_id"] = account_id
        self.save_identities()

    def get_client_options(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """Get client options (global defaults).
        
        Args:
            server_id: Legacy argument, ignored.
            
        Returns:
            Global options dict
        """
        # Always return defaults
        return self._deep_copy(self.profiles["client_options_defaults"])

    def set_client_option(
        self, key_path: str, value: Any, server_id: Optional[str] = None, *, create_mode: bool = False
    ):
        """Set a client option (global default).

        Args:
            key_path: Path to the option (e.g., "audio/music_volume")
            value: Option value
            server_id: Legacy argument, ignored.
            create_mode: If True, create intermediate dictionaries as needed
        """
        # Always set default
        target = self.profiles["client_options_defaults"]
        
        success = set_item_in_dict(target, key_path, value, create_mode=create_mode)
        if success:
             self.save_profiles()



    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a nested dict/list structure."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

