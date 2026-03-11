"""Main server class that ties everything together."""

import asyncio
import logging
import sys
from pathlib import Path

import json

from .tick import TickScheduler
from ..administration.manager import AdministrationManager
from ..network.websocket_server import WebSocketServer, ClientConnection
from ..persistence.database import Database
from ..auth.auth import AuthManager
from ..auth.rate_limit import RateLimiter
from ..tables.manager import TableManager
from ..users.network_user import NetworkUser
from ..users.base import MenuItem, EscapeBehavior
from ..users.preferences import UserPreferences, DiceKeepingStyle
from ..games.registry import GameRegistry, get_game_class
from ..messages.localization import Localization
from ..documentation.manager import DocumentationManager


VERSION = "0.1.8"
LATEST_CLIENT_VERSION = "0.1.8"
UPDATE_URL = "https://github.com/Daoductrung/PlayAural/releases/latest/download/PlayAural.zip"
UPDATE_HASH = "" # Optional SHA256

SOUNDS_VERSION = "1"
SOUNDS_URL = "https://github.com/Daoductrung/PlayAural/releases/latest/download/sounds.zip"

# Default paths based on module location
_MODULE_DIR = Path(__file__).parent.parent
_DEFAULT_LOCALES_DIR = _MODULE_DIR / "locales"


class Server:
    """
    Main PlayAural v0.1 server.

    Coordinates all components: network, auth, tables, games, and persistence.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        db_path: str = "PlayAural.db",
        locales_dir: str | Path | None = None,
        ssl_cert: str | Path | None = None,
        ssl_key: str | Path | None = None,
    ):
        self.host = host
        self.port = port
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key

        # Initialize components
        self._db = Database(db_path)
        self._auth: AuthManager | None = None
        self._tables = TableManager()
        self._tables._server = self  # Enable callbacks from TableManager
        self._ws_server: WebSocketServer | None = None
        self._tick_scheduler: TickScheduler | None = None

        # User tracking
        self._users: dict[str, NetworkUser] = {}  # username -> NetworkUser
        self._user_states: dict[str, dict] = {}  # username -> UI state
        self._pending_disconnects: dict[str, asyncio.Task] = {} # username -> broadcast task

        # Initialize admin manager
        self.admin_manager = AdministrationManager(self)

        # Initialize rate limiter
        self._rate_limiter = RateLimiter()

        # Initialize localization
        if locales_dir is None:
            locales_dir = _DEFAULT_LOCALES_DIR
        Localization.init(Path(locales_dir))
        Localization.preload_bundles()

    @property
    def db(self) -> Database:
        return self._db

    @property
    def users(self) -> dict[str, NetworkUser]:
        return self._users

    @property
    def user_states(self) -> dict[str, dict]:
        return self._user_states

    async def start(self) -> None:
        """
PlayAural Server
"""
        print(f"Starting PlayAural v{VERSION} server...")

        # Connect to database
        self._db.connect()
        self._auth = AuthManager(self._db)

        # Initialize trust levels for users
        promoted_user = self._db.initialize_trust_levels()
        if promoted_user:
            print(f"User '{promoted_user}' has been promoted to admin (trust level 2).")

        # Load existing tables
        self._load_tables()

        # Start WebSocket server
        self._ws_server = WebSocketServer(
            host=self.host,
            port=self.port,
            on_connect=self._on_client_connect,
            on_disconnect=self._on_client_disconnect,
            on_message=self._on_client_message,
            ssl_cert=self._ssl_cert,
            ssl_key=self._ssl_key,
        )
        await self._ws_server.start()

        # Start tick scheduler
        self._tick_scheduler = TickScheduler(self._on_tick)
        await self._tick_scheduler.start()

        protocol = "wss" if self._ssl_cert else "ws"
        print(f"Server running on {protocol}://{self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the server."""
        print("Stopping server...")

        # Save all tables
        self._save_tables()

        # Stop tick scheduler
        if self._tick_scheduler:
            await self._tick_scheduler.stop()

        # Stop WebSocket server
        if self._ws_server:
            await self._ws_server.stop()

        # Close database
        self._db.close()

        print("Server stopped.")

    def _load_tables(self) -> None:
        """Load tables from database and restore their games."""
        from ..users.bot import Bot

        tables = self._db.load_all_tables()
        for table in tables:
            self._tables.add_table(table)

            # Restore game from JSON if present
            if table.game_json:
                game_class = get_game_class(table.game_type)
                if not game_class:
                    print(f"WARNING: Could not find game class for {table.game_type}")
                    continue

                # Deserialize game and rebuild runtime state
                game = game_class.from_json(table.game_json)
                game.rebuild_runtime_state()
                table.game = game
                game._table = table

                # Setup keybinds (runtime only, not serialized)
                game.setup_keybinds()
                # Attach bots (humans will be attached when they reconnect)
                # Action sets are already restored from serialization
                for player in game.players:
                    if player.is_bot:
                        bot_user = Bot(player.name)
                        game.attach_user(player.id, bot_user)

        print(f"Loaded {len(tables)} tables from database.")

        # Delete all tables from database after loading to prevent stale data
        # on subsequent restarts. Tables will be re-saved on shutdown.
        self._db.delete_all_tables()

    def _save_tables(self) -> None:
        """Save all tables to database."""
        tables = self._tables.save_all()
        self._db.save_all_tables(tables)
        print(f"Saved {len(tables)} tables to database.")

    def _on_tick(self) -> None:
        """Called every tick (50ms)."""
        # Tick all tables
        self._tables.on_tick()

        # Flush queued messages for all users
        self._flush_user_messages()

    def _flush_user_messages(self) -> None:
        """Send all queued messages for all users."""
        for username, user in list(self._users.items()):
            messages = user.get_queued_messages()
            if messages and self._ws_server:
                client = self._ws_server.get_client_by_username(username)
                if client:
                    for msg in messages:
                        asyncio.create_task(client.send(msg))

    async def _on_client_connect(self, client: ClientConnection) -> None:
        """Handle new client connection."""
        print(f"Client connected: {client.address}")

    async def _on_client_disconnect(self, client: ClientConnection) -> None:
        """Handle client disconnection."""
        print(f"Client disconnected: {client.address}")
        if client.username:
            # Check if the disconnecting user is an admin before cleanup
            user = self._users.get(client.username)
            is_admin = user and user.trust_level >= 2

            # Check if user is banned (we don't want offline broadcast for them)
            # We must check the database directly in case the user state was already
            # cleaned up or not fully initialized, ensuring we never broadcast for banned users.
            is_banned = False
            active_ban = self._db.get_active_ban(client.username)
            if active_ban:
                is_banned = True

            # Broadcast offline announcement to all users with appropriate sound
            if user and user.trust_level >= 3:
                offline_sound = "offlinedev.ogg"
            elif is_admin:
                offline_sound = "offlineadmin.ogg"
            else:
                offline_sound = "offline.ogg"
            # Clean up users immediately so they can rejoin
            # Table cleanup is now handled by Table.on_tick timeout
            # and visibility is hidden immediately by menu filtering.
            
            # Auto-substitute with bot if in a playing game (requested feature)
            if hasattr(self, "_tables"):
                table = self._tables.find_user_table(client.username)
                if table and table.game and table.game.status == "playing":
                     # We need the user UUID. The user object is about to be popped, so get it now.
                     if user:
                         table.game.on_player_disconnect(user.uuid)

            # Clean up user state immediately so they can rejoin
            # FIX: Only remove from memory if the currently registered user actually belongs to this disconnecting client object
            if user and user.connection == client:
                self._users.pop(client.username, None)
                self._user_states.pop(client.username, None)

            # Schedule delayed offline broadcast to prevent spam on quick reconnects
            # Only broadcast if this client was actually the active one AND not banned
            if user and user.connection == client and not is_banned:
                task = asyncio.create_task(self._delayed_offline_broadcast(
                    client.username, user.uuid, offline_sound, user.trust_level
                ))
                self._pending_disconnects[client.username] = task

    async def _delayed_offline_broadcast(self, username: str, user_uuid: str, sound: str, trust_level: int) -> None:
        """Wait briefly then broadcast offline message if user hasn't reconnected."""
        try:
            await asyncio.sleep(2.0) # 2 seconds grace period
            
            # If we are here, user hasn't reconnected (or task wasn't cancelled)
            self._pending_disconnects.pop(username, None)
            
            # Broadcast
            self._broadcast_presence_l("user-offline", username, user_uuid, sound, trust_level)
            
        except asyncio.CancelledError:
            # User reconnected in time
            pass
        finally:
            self.on_user_presence_changed()

    def _broadcast_presence_l(
        self, message_id: str, player_name: str, player_uuid: str, default_sound: str, target_trust_level: int = 1
    ) -> None:
        """Broadcast a localized presence announcement to all approved online users with sound."""
        is_online_event = (message_id == "user-online")
        friend_message_id = "friend-online" if is_online_event else "friend-offline"
        friend_sound = "onlinefriend.ogg" if is_online_event else "offlinefriend.ogg"

        # Optimization: Fetch the connected player's friends once to avoid N+1 queries.
        # The database returns a list of UUIDs for friends.
        connecting_player_friends_uuids = set(self._db.get_friends(player_uuid))

        for user in self._users.values():
            if not user.approved:
                continue

            # Check if this connected user's UUID is in the joining/leaving player's friend list.
            # Friendship is bidirectional, so checking one side is sufficient.
            is_friend = False
            if user.preferences.notify_friend_presence:
                is_friend = user.uuid in connecting_player_friends_uuids

            if is_friend:
                # Play friend priority notification
                user.speak_l(friend_message_id, buffer="system", player=player_name)
                user.play_sound(friend_sound)
            else:
                # If target is a normal user (trust level < 2) and this user has general presence notifications off, skip
                if target_trust_level < 2 and not user.preferences.notify_user_presence:
                    continue
                # Use "system" buffer for joins/parts
                user.speak_l(message_id, buffer="system", player=player_name)
                # Play default sound
                user.play_sound(default_sound)

    async def _broadcast_admin_announcement(self, admin_name: str) -> None:
        """Broadcast an admin announcement to all approved online users."""
        for user in self._users.values():
            if user.approved:
                user.speak_l("admin-announcement-broadcast", buffer="system", admin=admin_name)

    async def _broadcast_dev_announcement(self, dev_name: str) -> None:
        """Broadcast a developer announcement to all approved online users."""
        for user in self._users.values():
            if not user.approved:
                continue  # Don't send broadcasts to unapproved users
            user.speak_l("dev-announcement-broadcast", buffer="system", dev=dev_name)

    def _notify_admins(self, message_id: str, sound: str) -> None:
        """Notify all online admins (trust level >= 2) with a message and sound."""
        for user in self._users.values():
            if user.trust_level >= 2:
                user.speak_l(message_id)
                user.play_sound(sound)

    async def _on_client_message(self, client: ClientConnection, packet: dict) -> None:
        """Handle incoming message from client."""
        packet_type = packet.get("type")

        if packet_type == "authorize":
            await self._handle_authorize(client, packet)
        elif packet_type == "register":
            await self._handle_register(client, packet)
        elif not client.authenticated:
            # Ignore non-auth packets from unauthenticated clients
            return
        elif packet_type == "ping":
            # Always allow ping to keep connection alive
            await self._handle_ping(client)
        else:
            user = self._users.get(client.username)

            if user:
                # Check if user is in lockdown state (banned)
                state = self._user_states.get(client.username, {})
                if state.get("menu") == "banned_menu":
                    # Banned users can only interact with the banned menu (Disconnect)
                    if packet_type == "menu":
                        await self._handle_menu(client, packet)
                    return

                # For all other packets, check if user is approved
                if not user.approved:
                    # Unapproved users can only ping - drop all other packets
                    return

            if packet_type == "menu":
                await self._handle_menu(client, packet)
            elif packet_type == "keybind":
                await self._handle_keybind(client, packet)
            elif packet_type == "editbox":
                await self._handle_editbox(client, packet)
            elif packet_type == "read_documentation":
                 await self._handle_read_documentation(client, packet)
            elif packet_type == "chat":
                await self._handle_chat(client, packet)
            elif packet_type == "list_online":
                await self._handle_list_online(client)
            elif packet_type == "list_online_with_games":
                await self._handle_list_online_with_games(client)
            elif packet_type == "broadcast_cmd":
                await self._handle_broadcast_cmd(client, packet)
            elif packet_type == "set_preference":
                await self._handle_set_preference(client, packet)

    async def _handle_authorize(self, client: ClientConnection, packet: dict) -> None:
        """Handle authorization packet."""
        username = packet.get("username", "")
        password = packet.get("password", "")
        # Extract client type (default to python for legacy clients)
        client_type = packet.get("client", "python")

        # Rate limit check (brute force protection)
        if not self._rate_limiter.is_login_allowed(client.ip_address):
            await client.send({
                "type": "login_failed",
                "reason": "rate_limit",
                "reconnect": False,
            })
            await client.close()
            return

        # Check version if provided
        client_version = packet.get("version", "0.0.0")
        
        # WEB CLIENT: Strict validation
        # If version mismatch, send 'login_failed' so it shows the error message.
        if client_type == "web" and client_version != VERSION:
             print(f"Login failed for {username} (Web): Version mismatch (Server: {VERSION}, Client: {client_version})")
             await client.send({
                 "type": "login_failed",
                 "reason": "version_mismatch",
                 "text": f"Version mismatch. Server: {VERSION}, Client: {client_version}"
             })
             await client.close()
             return

        # PYTHON CLIENT: Legacy logic
        # We proceed to authenticate and send 'authorize_success' so it receives 'update_info'.
        # The logic at the end of this function will prevent sending the game list, triggering the update dialog.

        # Try to authenticate
        if not self._auth.authenticate(username, password):
            # Record failed login
            self._rate_limiter.record_failed_login(client.ip_address)

            # Determine specific failure reason
            reason = "wrong_password"
            if not self._auth.get_user(username):
                reason = "user_not_found"
            
            await client.send(
                {
                    "type": "login_failed",
                    "reason": reason,
                    "reconnect": False,
                }
            )
            return

        # Success - clear failed logins for this IP
        self._rate_limiter.clear_failed_logins(client.ip_address)

        # Check if user is already connected
        old_client = self._ws_server.get_client_by_username(username)
        if old_client and old_client != client:
            user_record = self._auth.get_user(username)
            old_locale = user_record.locale if user_record else "en"
            # Send strictly recognized disconnect message to prevent auto-reconnect loop
            await old_client.send({
                "type": "disconnect",
                "reason": Localization.get(old_locale, "auth-kicked-logged-in-elsewhere"),
                "reconnect": False
            })
            # Close old connection
            await old_client.close()
            # Remove from users dict to ensure clean state for new connection
            self._users.pop(username, None)

        # Authentication successful
        client.username = username
        client.authenticated = True

        # Create network user with preferences and persistent UUID
        user_record = self._auth.get_user(username)
        locale = user_record.locale if user_record else "en"
        user_uuid = user_record.uuid if user_record else None
        trust_level = user_record.trust_level if user_record else 1
        is_approved = user_record.approved if user_record else False
        preferences = UserPreferences()
        if user_record and user_record.preferences_json:
            try:
                prefs_data = json.loads(user_record.preferences_json)
                preferences = UserPreferences.from_dict(prefs_data)
            except (json.JSONDecodeError, KeyError):
                pass  # Use defaults on error
        user = NetworkUser(
            username, locale, client, client_type=client_type, uuid=user_uuid, preferences=preferences,
            trust_level=trust_level, approved=is_approved
        )
        self._users[username] = user

        # Check for pending disconnect (debounce)
        pending_task = self._pending_disconnects.pop(username, None)
        if pending_task:
            # User reconnected quickly - cancel offline broadcast
            pending_task.cancel()
            # We skip broadcasting "online" because we cancelled the "offline"
            # Effectively silencing the flap.

        # Send success response
        # MUST generate this packet first so client considers itself "logged in"
        await client.send(
            {
                "type": "authorize_success",
                "username": username,
                "version": VERSION,
                "locale": user.locale,
                "update_info": {
                    "version": LATEST_CLIENT_VERSION,
                    "url": UPDATE_URL,
                    "hash": UPDATE_HASH,
                },
                "sounds_info": {
                    "version": SOUNDS_VERSION,
                    "url": SOUNDS_URL,
                },
                "preferences": user.preferences.to_dict(),
            }
        )

        # Check if user is banned before broadcasting presence
        active_ban = self._db.get_active_ban(username)

        if not active_ban:
            # Broadcast online announcement to all users with appropriate sound
            # We do this AFTER authorize_success so the client is ready to receive/play it.
            # This fixes the "no self sound" issue.
            if trust_level >= 3:
                online_sound = "onlinedev.ogg"
            elif trust_level >= 2:
                online_sound = "onlineadmin.ogg"
            else:
                online_sound = "online.ogg"

            # Only broadcast if we didn't cancel a pending disconnect (debounce)
            if not pending_task:
                 self._broadcast_presence_l("user-online", username, user_uuid, online_sound, trust_level)
                 self.on_user_presence_changed()

                 # If user is a developer or admin, announce that as well
                 if trust_level >= 3:
                      await self._broadcast_dev_announcement(username)
                 elif trust_level >= 2:
                      await self._broadcast_admin_announcement(username)

        # Check client version
        client_version = packet.get("version", "0.0.0")
        if client_version != LATEST_CLIENT_VERSION:
            # If version mismatch, do NOT send game list.
            # The client will prompt for update.
            return

        # Send game list
        await self._send_game_list(client)

        # Check if user is banned
        active_ban = self._db.get_active_ban(username)
        if active_ban:
            self._show_banned_menu(user, active_ban)
            return

        # Check if user is approved
        if not user.approved:
            # User needs approval - show waiting screen
            self._show_waiting_for_approval(user)
            return

        # Check MOTD
        active_motd = self._db.get_active_motd(user.locale)
        motd_version = active_motd[0] if active_motd else 0
        user_motd_version = user_record.motd_version if user_record else 0

        if motd_version != user_motd_version and active_motd:
            # User has not acknowledged the active MOTD version. Show it to them.
            self._show_motd_menu(user, active_motd[1], motd_version)
            return

        self._restore_user_state(user, username)

    def _restore_user_state(self, user: NetworkUser, username: str) -> None:
        """Restore user state or show main menu after successful login."""
        # Enforce mandatory email requirement
        user_record = self._db.get_user(username)
        if user_record and not user_record.email:
            self._show_mandatory_email_menu(user)
            return

        # Check if user is in a table
        table = self._tables.find_user_table(username)

        restored_game = False
        is_spectator = False
        if table and table.game:
            # Check if user was a spectator
            # We need to find the member record to know their role
            for member in table.members:
                if member.username == username:
                    is_spectator = member.is_spectator
                    break

            if is_spectator:
                # OPTIMIZATION: Spectators should NOT be automatically restored to the table.
                # If they reconnect, they should land in the main menu.
                # We remove them from the table to clean up the stale session.
                table.remove_member(username)
                
                # BUGFIX: Also remove from the game state to prevent "ghost" spectators
                # Table.members is for the lobby/listing, Game.players is for the game logic.
                if table.game:
                    # We need the player ID (UUID) to remove from game
                    # user.uuid is available here from the newly created NetworkUser
                    # Use the centralized helper
                    table.game.remove_spectator(user.uuid)

            else:
                # Active player rejoining
                player = table.game.get_player_by_id(user.uuid)
                if player:
                    # Update player's bot status in case they were replaced
                    player.is_bot = False
                    
                    # Rejoin table - use same approach as _restore_saved_table
                    table.attach_user(username, user)

                    # Check status: if game is finished, we don't rebuild state, we let them see the table menu
                    if table.game.status != "finished":
                        restored_game = True

                        # Restore humanity if they were replaced by a bot
                        if player.is_bot:
                            player.is_bot = False
                            table.game.broadcast_l("player-rejoined", player=player.name)
                        
                        table.game.attach_user(player.id, user)
                        
                        # Set user state so menu selections are handled correctly
                        self._user_states[username] = {
                            "menu": "in_game",
                            "table_id": table.table_id,
                        }

        # Process Offline Notifications exactly once when they enter active state
        self._process_offline_notifications(user)

        if not restored_game:
            # Not in an active game (or was a spectator); restore menu state
            state = self._user_states.get(username, {})
            current_menu = state.get("menu", "main_menu")

            if current_menu == "tables_menu":
                game_type = state.get("game_type")
                if game_type:
                    self._show_games_list_menu(user)
                    self._show_tables_menu(user, game_type)
                else:
                    self._show_main_menu(user)
            elif current_menu == "active_tables_menu":
                self._show_active_tables_menu(user)
            elif current_menu == "games_menu":
                self._show_games_list_menu(user)
            elif current_menu == "options_menu":
                self._show_options_menu(user)
            elif current_menu == "documentation_menu":
                self._show_documentation_menu(user)
            elif current_menu == "saved_tables_menu":
                self._show_saved_tables_menu(user)
            elif current_menu == "leaderboards_menu":
                self._show_leaderboards_menu(user)
            elif current_menu == "personal_options_menu":
                self._show_personal_options_menu(user)
            elif current_menu == "my_stats_menu":
                self._show_my_stats_menu(user)
            elif current_menu == "profile_menu":
                self._show_profile_menu(user)
            else:
                self._show_main_menu(user)

    def _show_mandatory_email_menu(self, user: NetworkUser) -> None:
        """Show the mandatory email setup menu."""
        user.speak_l("mandatory-email-notice")
        items = [
            MenuItem(text=Localization.get(user.locale, "mandatory-email-notice"), id=""),
            MenuItem(text=Localization.get(user.locale, "ok"), id="ok")
        ]
        user.show_menu(
            "mandatory_email_menu",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "mandatory_email_menu"
        }

    def _process_offline_notifications(self, user: NetworkUser) -> None:
        """Fetch, group, and announce offline notifications for a user."""
        notifications = self._db.get_and_clear_notifications(user.uuid)
        if not notifications:
            return

        # Group by event_type
        grouped = {}
        for notif in notifications:
            etype = notif["event_type"]
            if etype not in grouped:
                grouped[etype] = []
            if notif["source_username"] not in grouped[etype]:
                grouped[etype].append(notif["source_username"])

        for etype, usernames in grouped.items():
            # Cap the list at 3 to prevent TTS flooding
            if len(usernames) > 3:
                displayed_names = usernames[:3]
                remaining_count = len(usernames) - 3
                formatted_names_base = Localization.format_list_and(user.locale, displayed_names)
                formatted_names = Localization.get(user.locale, "friends-and-others", names=formatted_names_base, count=remaining_count)
            else:
                formatted_names = Localization.format_list_and(user.locale, usernames)

            if etype == "friend_request_received":
                user.speak_l("friends-grouped-requests", usernames=formatted_names)
                user.play_sound("friend_request_received.ogg")
            elif etype == "friend_accepted":
                user.speak_l("friends-grouped-accepted", usernames=formatted_names)
                user.play_sound("friend_accepted.ogg")
            elif etype == "friend_declined":
                user.speak_l("friends-grouped-declined", usernames=formatted_names)
                user.play_sound("friend_declined.ogg")
            elif etype == "friend_removed":
                user.speak_l("friends-grouped-removed", usernames=formatted_names)
                user.play_sound("friend_removed.ogg")

    def _show_motd_menu(self, user: NetworkUser, message: str, version: int) -> None:
        """Show the forced-read MOTD menu."""
        user.speak_l("motd-announcement")
        items = []
        for i, line in enumerate(message.split('\n')):
            items.append(MenuItem(text=line, id=f"line_{i}"))
        items.append(MenuItem(text=Localization.get(user.locale, "ok"), id="ok"))

        user.show_menu(
            "motd_menu",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "motd_menu",
            "motd_version": version
        }

    async def _handle_register(self, client: ClientConnection, packet: dict) -> None:
        """Handle registration packet from registration dialog."""
        import re

        # Rate limit check (spam protection)
        if not self._rate_limiter.is_registration_allowed(client.ip_address):
            locale = packet.get("locale", "en")
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "rate_limit",
                "text": Localization.get(locale, "error-rate-limit-register")
            })
            await client.close()
            return

        username = packet.get("username", "")
        password = packet.get("password", "")
        locale = packet.get("locale", "en") # Get locale from client, default to en
        email = packet.get("email", "")
        bio = packet.get("bio", "")

        if not username or not password:
            await client.send({
                "type": "speak",
                "text": Localization.get(locale, "auth-username-password-required")
            })
            return

        if not email:
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "email_empty",
                "text": Localization.get(locale, "reg-error-email")
            })
            return

        if self._db.email_exists(email):
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "email_taken",
                "text": Localization.get(locale, "error-email-taken")
            })
            return

        if len(username) < 3 or len(username) > 30:
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "username_length",
                "text": Localization.get(locale, "auth-error-username-length")
            })
            return

        has_letters = bool(re.search(r'[a-zA-Z]', password))
        has_numbers = bool(re.search(r'[0-9]', password))

        if len(password) < 8 or not has_letters or not has_numbers:
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "password_weak",
                "text": Localization.get(locale, "auth-error-password-weak")
            })
            return

        # Check if this will be a user that needs approval (not the first user)
        needs_approval = self._db.get_user_count() > 0

        # Try to register the user
        if self._auth.register(username, password, locale=locale, email=email, bio=bio):
            self._rate_limiter.record_registration(client.ip_address)
            await client.send({
                "type": "register_response",
                "status": "success",
                "text": Localization.get(locale, "auth-registration-success"), # Fallback text
                "locale": locale
            })
            # Notify admins of new account request (only if user needs approval)
            if needs_approval:
                self._notify_admins("account-request", "accountrequest.ogg")
        else:
            await client.send({
                "type": "register_response",
                "status": "error",
                "error": "username_taken",
                "text": Localization.get(locale, "auth-username-taken")
            })

    async def _send_game_list(self, client: ClientConnection) -> None:
        """Send the list of available games to the client."""
        games = []
        for game_class in GameRegistry.get_all():
            games.append(
                {
                    "type": game_class.get_type(),
                    "name": game_class.get_name(),
                }
            )

        await client.send(
            {
                "type": "update_options_lists",
                "games": games
            }
        )

    def _show_main_menu(self, user: NetworkUser) -> None:
        """Show the main menu to a user."""
        items = [
            MenuItem(text=Localization.get(user.locale, "play"), id="play"),
            MenuItem(
                text=Localization.get(user.locale, "view-active-tables"),
                id="active_tables",
            ),
            MenuItem(
                text=Localization.get(user.locale, "saved-tables"), id="saved_tables"
            ),
            MenuItem(
                text=Localization.get(user.locale, "leaderboards"), id="leaderboards"
            ),
            MenuItem(
                text=Localization.get(user.locale, "personal-and-options"), id="personal_options"
            ),
            MenuItem(
                text=Localization.get(user.locale, "documentation-menu"), id="documentation"
            ),
        ]
        # Add administration menu for admins
        if user.trust_level >= 2:
            items.append(
                MenuItem(text=Localization.get(user.locale, "administration"), id="administration")
            )
        items.append(MenuItem(text=Localization.get(user.locale, "logout"), id="logout"))
        user.show_menu(
            "main_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        user.play_music("mainmus.ogg")
        user.stop_ambience()
        self._user_states[user.username] = {"menu": "main_menu"}

    def _show_games_list_menu(self, user: NetworkUser) -> None:
        """Show flat list of all games."""
        games = GameRegistry.get_all()
        # Sort games by localized name
        # We need to get pairs of (game, name) to sort
        game_list = []
        for game_class in games:
            name = Localization.get(user.locale, game_class.get_name_key())
            game_list.append((game_class, name))
        
        # Sort by name
        game_list.sort(key=lambda x: x[1])

        items = []
        for game_class, name in game_list:
            items.append(MenuItem(text=name, id=f"game_{game_class.get_type()}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "games_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "games_menu"}

    def _show_games_menu(self, user: NetworkUser, category: str) -> None:
        """Show games in a category."""
        categories = GameRegistry.get_by_category()
        games = categories.get(category, [])

        items = []
        for game_class in games:
            game_name = Localization.get(user.locale, game_class.get_name_key())
            items.append(MenuItem(text=game_name, id=f"game_{game_class.get_type()}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "games_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "games_menu", "category": category}

    def _show_tables_menu(self, user: NetworkUser, game_type: str) -> None:
        """Show available tables for a game."""
        all_tables = self._tables.get_tables_by_type(game_type)
        # Filter: Only show waiting or playing tables (exclude finished)
        # - Show if host is online (for waiting tables)
        # - OR table is playing (so players can rejoin)
        # Filter: Only show tables with at least one online, non-spectator human player
        tables = []
        for t in all_tables:
            if not t.game:
                continue
            if t.game.status not in ["waiting", "playing"]:
                continue
            
            # Check for at least one active human player
            has_active_human = False
            for member in t.members:
                if not member.is_spectator and member.username in self._users:
                    has_active_human = True
                    break
            
            if has_active_human:
                tables.append(t)
        
        game_class = get_game_class(game_type)
        game_name = (
            Localization.get(user.locale, game_class.get_name_key())
            if game_class
            else game_type
        )

        items = [
            MenuItem(
                text=Localization.get(user.locale, "create-table"), id="create_table"
            )
        ]

        for table in tables:
            member_count = len(table.members)
            member_names = [
                member.username
                for member in table.members
                if member.username != table.host
            ]
            members_str = Localization.format_list_and(user.locale, member_names)
            # Determine status for display
            if table.game:
                if table.game.status == "waiting":
                    status_key = "table-status-waiting"
                elif table.game.status == "playing":
                    status_key = "table-status-playing"
                elif table.game.status == "finished":
                    status_key = "table-status-finished"
                else:
                    status_key = "table-status-waiting"  # fallback
            else:
                status_key = "table-status-waiting"  # fallback
            status_text = Localization.get(user.locale, status_key)

            if member_count == 1:
                listing_key = "table-listing-game-one-status"
            elif member_names:
                listing_key = "table-listing-game-with-status"
            else:
                listing_key = "table-listing-game-status"
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        listing_key,
                        game=game_name,
                        host=table.host,
                        count=member_count,
                        members=members_str,
                        status=status_text,
                    ),
                    id=f"table_{table.table_id}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "tables_menu",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_active_tables_menu(self, user: NetworkUser) -> None:
        """Show available tables across all games."""
        items = self._get_active_tables_menu_items(user)
        user.show_menu(
            "active_tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "active_tables_menu"}

    def _show_active_tables_filter_menu(self, user: NetworkUser) -> None:
        """Show menu to select the active tables filter."""
        items = [
            MenuItem(text=Localization.get(user.locale, "filter-name-all"), id="filter_all"),
            MenuItem(text=Localization.get(user.locale, "filter-name-waiting"), id="filter_waiting"),
            MenuItem(text=Localization.get(user.locale, "filter-name-playing"), id="filter_playing"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]

        user.show_menu(
            "active_tables_filter_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "active_tables_filter_menu"}

    def _get_tables_menu_items(self, user: NetworkUser, game_type: str) -> list[MenuItem]:
        """Generate the list of MenuItems for a specific game's tables menu."""
        all_tables = self._tables.get_tables_by_type(game_type)
        tables = []
        for t in all_tables:
            if not t.game:
                continue
            if t.game.status not in ["waiting", "playing"]:
                continue

            has_active_human = False
            for member in t.members:
                if not member.is_spectator and member.username in self._users:
                    has_active_human = True
                    break

            if has_active_human:
                tables.append(t)

        game_class = get_game_class(game_type)
        game_name = (
            Localization.get(user.locale, game_class.get_name_key())
            if game_class
            else game_type
        )

        items = [
            MenuItem(
                text=Localization.get(user.locale, "create-table"), id="create_table"
            )
        ]

        for table in tables:
            member_count = len(table.members)
            member_names = [
                member.username
                for member in table.members
                if member.username != table.host
            ]
            members_str = Localization.format_list_and(user.locale, member_names)
            if table.game:
                if table.game.status == "waiting":
                    status_key = "table-status-waiting"
                elif table.game.status == "playing":
                    status_key = "table-status-playing"
                elif table.game.status == "finished":
                    status_key = "table-status-finished"
                else:
                    status_key = "table-status-waiting"
            else:
                status_key = "table-status-waiting"
            status_text = Localization.get(user.locale, status_key)

            if member_count == 1:
                listing_key = "table-listing-game-one-status"
            elif member_names:
                listing_key = "table-listing-game-with-status"
            else:
                listing_key = "table-listing-game-status"
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        listing_key,
                        game=game_name,
                        host=table.host,
                        count=member_count,
                        members=members_str,
                        status=status_text,
                    ),
                    id=f"table_{table.table_id}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        return items

    def _get_active_tables_menu_items(self, user: NetworkUser) -> list[MenuItem]:
        """Generate the list of MenuItems for the global active tables menu."""
        all_tables = self._tables.get_all_tables()
        tables = []
        filter_type = user.preferences.active_tables_filter

        for t in all_tables:
            if not t.game:
                continue
            if t.game.status not in ["waiting", "playing"]:
                continue

            # Apply filter
            if filter_type != "all" and t.game.status != filter_type:
                continue

            has_active_human = False
            for member in t.members:
                if not member.is_spectator and member.username in self._users:
                    has_active_human = True
                    break

            if has_active_human:
                tables.append(t)

        items: list[MenuItem] = []

        # 1. Add Filter Toggle
        filter_name_key = f"filter-name-{filter_type}"
        filter_name = Localization.get(user.locale, filter_name_key)
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "active-tables-filter", filter=filter_name),
                id="toggle_filter"
            )
        )

        # 2. Add empty message if no tables match filter
        if not tables:
            empty_msg_key = f"no-active-tables-{filter_type}"
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, empty_msg_key),
                    id="no_tables_msg"
                )
            )

        for table in tables:
            game_class = get_game_class(table.game_type)
            game_name = (
                Localization.get(user.locale, game_class.get_name_key())
                if game_class
                else table.game_type
            )
            member_count = len(table.members)
            member_names = [
                member.username
                for member in table.members
                if member.username != table.host
            ]
            members_str = Localization.format_list_and(user.locale, member_names)

            if table.game:
                if table.game.status == "waiting":
                    status_key = "table-status-waiting"
                elif table.game.status == "playing":
                    status_key = "table-status-playing"
                elif table.game.status == "finished":
                    status_key = "table-status-finished"
                else:
                    status_key = "table-status-waiting"
            else:
                status_key = "table-status-waiting"
            status_text = Localization.get(user.locale, status_key)

            if member_count == 1:
                listing_key = "table-listing-game-one-status"
            elif member_names:
                listing_key = "table-listing-game-with-status"
            else:
                listing_key = "table-listing-game-status"
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        listing_key,
                        game=game_name,
                        host=table.host,
                        count=member_count,
                        members=members_str,
                        status=status_text,
                    ),
                    id=f"table_{table.table_id}",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        return items

    def on_user_presence_changed(self) -> None:
        """Called when a user logs in or disconnects to refresh social menus."""
        for username, user in self._users.items():
            state = self._user_states.get(username, {})
            current_menu = state.get("menu")
            if current_menu == "friends_list_menu":
                self._show_friends_list_menu(user)
            elif current_menu == "online_users":
                items = self._get_online_users_menu_items(user)
                user.update_menu("online_users", items)

    def on_friend_requests_changed(self, target_uuid: str) -> None:
        """Called when friend requests are sent, accepted, or declined to refresh UI."""
        # We need to find the user by UUID to update their menu
        for username, user in self._users.items():
            if user.uuid == target_uuid:
                state = self._user_states.get(username, {})
                current_menu = state.get("menu")
                if current_menu == "friends_hub_menu":
                    self._show_friends_hub_menu(user)
                elif current_menu == "friend_requests_menu":
                    self._show_friend_requests_menu(user)
                elif current_menu == "friends_list_menu":
                    self._show_friends_list_menu(user)

    def on_tables_changed(self) -> None:
        """Called by TableManager when a table is created, destroyed, or changes status.
        Dynamically updates the tables menus for any users currently viewing them."""
        self.on_user_presence_changed()
        for username, user in self._users.items():
            state = self._user_states.get(username, {})
            current_menu = state.get("menu")

            if current_menu == "active_tables_menu":
                # Check if there are still tables available. If not, we might want to let them
                # stay in the menu (it will just show 'back'), or kick them out.
                # Since the client handles empty lists poorly, we can just send the updated items.
                # If there are no tables, it will just contain 'back'.
                items = self._get_active_tables_menu_items(user)
                if len(items) == 1: # Only 'back' is left
                    # If empty, speak a message and boot them to main menu using show_menu logic
                    # Or we just let it update to 'back' and they can press escape.
                    # Let's dynamically update to just show 'back'.
                    pass
                user.update_menu("active_tables_menu", items)

            elif current_menu == "tables_menu":
                game_type = state.get("game_type")
                if game_type:
                    items = self._get_tables_menu_items(user, game_type)
                    user.update_menu("tables_menu", items)

    # Dice keeping style display names
    DICE_KEEPING_STYLES = {
        DiceKeepingStyle.PlayAural: "dice-keeping-style-indexes",
        DiceKeepingStyle.QUENTIN_C: "dice-keeping-style-values",
    }

    def _show_options_menu(self, user: NetworkUser) -> None:
        """Show options menu."""
        languages = Localization.get_available_languages(user.locale, fallback= user.locale)
        current_lang = languages.get(user.locale, user.locale)
        prefs = user.preferences

        # Turn sound option
        turn_sound_status = Localization.get(
            user.locale,
            "option-on" if prefs.play_turn_sound else "option-off",
        )

        # Clear kept dice option
        clear_kept_status = Localization.get(
            user.locale,
            "option-on" if prefs.clear_kept_on_roll else "option-off",
        )

        # Dice keeping style option
        style_key = self.DICE_KEEPING_STYLES.get(
            prefs.dice_keeping_style, "dice-keeping-style-indexes"
        )
        dice_style_name = Localization.get(user.locale, style_key)
        
        items = []

        # 1. Audio & Media
        items.extend([
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "music-volume-option",
                    value=prefs.music_volume,
                ),
                id="music_volume",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "ambience-volume-option",
                    value=prefs.ambience_volume,
                ),
                id="ambience_volume",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "turn-sound-option",
                    status=Localization.get(
                        user.locale, "option-on" if prefs.play_turn_sound else "option-off"
                    ),
                ),
                id="turn_sound",
            ),
        ])

        if user.client_type != "web":
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "play-typing-sounds-option",
                        status=Localization.get(
                            user.locale,
                            "option-on" if prefs.play_typing_sounds else "option-off",
                        ),
                    ),
                    id="play_typing_sounds",
                )
            )

        # 2. Accessibility & Interface
        items.append(
            MenuItem(
                text=Localization.get(
                    user.locale, "language-option", language=current_lang
                ),
                id="language",
            )
        )

        if user.client_type == "web":
            items.append(
                MenuItem(text=Localization.get(user.locale, "speech-settings"), id="speech_settings")
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "invert-multiline-enter-option",
                        status=Localization.get(
                            user.locale,
                            "option-on" if prefs.invert_multiline_enter_behavior else "option-off",
                        ),
                    ),
                    id="invert_multiline_enter",
                )
            )

        # 3. Social & Notifications
        items.extend([
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "mute-global-chat-option",
                    status=Localization.get(
                        user.locale, "option-on" if prefs.mute_global_chat else "option-off"
                    ),
                ),
                id="mute_global_chat",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "mute-table-chat-option",
                    status=Localization.get(
                        user.locale, "option-on" if prefs.mute_table_chat else "option-off"
                    ),
                ),
                id="mute_table_chat",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "option-notify-user-presence-on" if prefs.notify_user_presence else "option-notify-user-presence-off"
                ),
                id="notify_user_presence",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "option-notify-friend-presence-on" if prefs.notify_friend_presence else "option-notify-friend-presence-off"
                ),
                id="notify_friend_presence",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "option-notify-table-created-on" if prefs.notify_table_created else "option-notify-table-created-off"
                ),
                id="notify_table_created",
            ),
        ])

        # 4. Gameplay Preferences
        items.extend([
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "dice-keeping-style-option",
                    style=Localization.get(
                        user.locale, self.DICE_KEEPING_STYLES.get(prefs.dice_keeping_style, "dice-keeping-style-indexes")
                    ),
                ),
                id="dice_keeping_style",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "clear-kept-option",
                    status=Localization.get(
                        user.locale, "option-on" if prefs.clear_kept_on_roll else "option-off"
                    ),
                ),
                id="clear_kept",
            ),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ])

        user.show_menu(
            "options_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "options_menu"}

    def _show_language_menu(self, user: NetworkUser) -> None:
        """Show language selection menu."""
        # Get languages in their native names and in user's locale for comparison
        languages = Localization.get_available_languages(fallback = user.locale)
        localized_languages = Localization.get_available_languages(user.locale, fallback= user.locale)

        items = []
        for lang_code, lang_name in languages.items():
            prefix = "* " if lang_code == user.locale else ""
            localized_name = localized_languages.get(lang_code, lang_name)
            # Show localized name first, then native name in parentheses if different
            if localized_name != lang_name:
                display = f"{prefix}{localized_name} ({lang_name})"
            else:
                display = f"{prefix}{lang_name}"
            items.append(MenuItem(text=display, id=f"lang_{lang_code}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "language_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "language_menu"}

    def _show_speech_settings_menu(self, user: NetworkUser) -> None:
        """Show speech settings menu (Web only)."""
        prefs = user.preferences
        items = []

        # Speech Mode (Aria / Web Speech)
        mode_key = "mode-aria" if prefs.speech_mode == "aria" else "mode-web-speech"
        items.append(MenuItem(
            text=Localization.get(
                user.locale,
                "speech-mode-option",
                status=Localization.get(user.locale, mode_key)
            ),
            id="speech_mode"
        ))

        # Speech Rate
        items.append(MenuItem(
            text=Localization.get(
                user.locale,
                "speech-rate-option",
                value=prefs.speech_rate
            ),
            id="speech_rate"
        ))

        # Speech Voice
        voice_name = prefs.speech_voice if prefs.speech_voice else Localization.get(user.locale, "default-voice")
        # Since voice is an ID, we might want to let the client render the name?
        # For now, we display the ID or "Default". Client can improve this if needed.
        items.append(MenuItem(
            text=Localization.get(
                user.locale,
                "speech-voice-option",
                voice=voice_name
            ),
            id="speech_voice"
        ))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "speech_settings_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "speech_settings_menu"}

    async def _handle_speech_settings_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle speech settings menu selection."""
        prefs = user.preferences

        if selection_id == "back":
            self._show_options_menu(user)
        
        elif selection_id == "speech_mode":
            # Toggle between "aria" and "web_speech"
            new_mode = "web_speech" if prefs.speech_mode == "aria" else "aria"
            prefs.speech_mode = new_mode
            self._save_user_preferences(user)
            self._sync_pref_to_client(user, "speech_mode", new_mode)
            self._show_speech_settings_menu(user)
        
        elif selection_id == "speech_rate":
            user.show_editbox(
                "speech_rate_input",
                Localization.get(user.locale, "enter-speech-rate"),
                default_value=str(prefs.speech_rate),
            )
            self._user_states[user.username]["menu"] = "speech_rate_input"
        
        elif selection_id == "speech_voice":
            # Send an empty menu with a specific ID.
            # The Web Client will intercept this ID and populate it with available voices.
            # When selected, it will send the voice URI as selection_id to _handle_voice_selection.
            user.show_menu(
                "voice_selection_menu",
                [MenuItem(text=Localization.get(user.locale, "select-voice"), id="placeholder")],
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST
            )
            self._user_states[user.username] = {"menu": "voice_selection_menu"}

    async def _handle_voice_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle voice selection override (Web only)."""
        if selection_id == "back":
            self._show_speech_settings_menu(user)
            return

        # selection_id is the voice URI
        user.preferences.speech_voice = selection_id
        self._save_user_preferences(user)
        self._sync_pref_to_client(user, "speech_voice", selection_id)
        self._show_speech_settings_menu(user)


    def _sync_pref_to_client(self, user: NetworkUser, key: str, value: any) -> None:
        """Sync a preference update to the client."""
        asyncio.create_task(user.connection.send({
            "type": "update_preference",
            "key": key,
            "value": value
        }))

    async def _handle_options_input(
        self, user: NetworkUser, packet: dict, state: dict
    ) -> bool:
        """Handle input from options menu editbox."""
        menu_id = state.get("menu")
        input_id = packet.get("input_id")
        value = packet.get("text", packet.get("value"))
        prefs = user.preferences

        if menu_id == "music_volume_input":
            try:
                # Validate input
                if not value or not value.isdigit():
                     raise ValueError
                vol = int(value)
                if 0 <= vol <= 100:
                    prefs.music_volume = vol
                    self._save_user_preferences(user)
                    self._sync_pref_to_client(user, "audio/music_volume", vol)
                    self._show_options_menu(user)
                    return True
                else:
                    raise ValueError
            except ValueError:
                user.speak_l("invalid-volume")
                self._show_options_menu(user) 
                return True
        
        elif menu_id == "ambience_volume_input":
            try:
                if not value or not value.isdigit():
                     raise ValueError
                vol = int(value)
                if 0 <= vol <= 100:
                    prefs.ambience_volume = vol
                    self._save_user_preferences(user)
                    self._sync_pref_to_client(user, "audio/ambience_volume", vol)
                    self._show_options_menu(user)
                    return True
                else:
                    raise ValueError
            except ValueError:
                user.speak_l("invalid-volume")
                self._show_options_menu(user)
                return True
        
        elif menu_id == "speech_rate_input":
            try:
                if not value or not value.isdigit():
                     raise ValueError
                rate = int(value)
                if 50 <= rate <= 300:
                    prefs.speech_rate = rate
                    self._save_user_preferences(user)
                    self._sync_pref_to_client(user, "speech_rate", rate)
                    self._show_speech_settings_menu(user)
                    return True
                else:
                    raise ValueError
            except ValueError:
                user.speak_l("invalid-rate")
                self._show_speech_settings_menu(user)
                return True

        return False

    async def _handle_set_preference(self, client: ClientConnection, packet: dict) -> None:
        """Handle set_preference packet from client."""
        username = client.username
        if not username:
            return
        user = self._users.get(username)
        if not user:
            return

        key = packet.get("key")
        value = packet.get("value")
        prefs = user.preferences

        if key == "social/mute_global_chat":
            prefs.mute_global_chat = bool(value)
        elif key == "social/mute_table_chat":
            prefs.mute_table_chat = bool(value)
        elif key == "audio/music_volume":
            try:
                prefs.music_volume = int(value)
            except (ValueError, TypeError):
                return
        elif key == "audio/ambience_volume":
            try:
                prefs.ambience_volume = int(value)
            except (ValueError, TypeError):
                return
        elif key == "interface/invert_multiline_enter_behavior":
            prefs.invert_multiline_enter_behavior = bool(value)
        elif key == "interface/play_typing_sounds":
            prefs.play_typing_sounds = bool(value)
        else:
            return # Unknown key

        self._save_user_preferences(user)
        # If the user is currently looking at the options menu, we should refresh it
        # But determining that is complex. Updating the backend state is sufficient for next view.

    def _show_banned_menu(self, user: NetworkUser, active_ban) -> None:
        """Show banned screen with reason and expiration."""
        user.speak_l("banned-menu-title")

        from datetime import datetime
        # Format reason
        if active_ban.reason_key.startswith("CUSTOM_"):
            loc_reason = active_ban.reason_key[7:]
        else:
            loc_reason = Localization.get(user.locale, active_ban.reason_key)

        # Format expiration
        if not active_ban.expires_at:
            expires_text = Localization.get(user.locale, "banned-permanent")
        else:
            try:
                dt = datetime.fromisoformat(active_ban.expires_at)
                # Localize or just use standard formatting
                formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
                expires_text = Localization.get(user.locale, "banned-expires", expires=formatted_dt)
            except ValueError:
                expires_text = Localization.get(user.locale, "banned-expires", expires=active_ban.expires_at)

        items = [
            MenuItem(text=Localization.get(user.locale, "banned-reason", reason=loc_reason), id="info_reason"),
            MenuItem(text=expires_text, id="info_expires"),
            MenuItem(text=Localization.get(user.locale, "disconnect"), id="disconnect"),
        ]

        user.show_menu(
            "banned_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "banned_menu"}

    def _show_waiting_for_approval(self, user: NetworkUser) -> None:
        """Show waiting for approval screen to unapproved user."""
        user.speak_l("waiting-for-approval")
        user.clear_ui()
        self._user_states[user.username] = {"menu": "waiting_for_approval"}

    def _show_saved_tables_menu(self, user: NetworkUser) -> None:
        """Show saved tables menu."""
        saved = self._db.get_user_saved_tables(user.username)

        if not saved:
            user.speak_l("no-saved-tables")
            self._show_main_menu(user)
            return

        items = []
        for record in saved:
            items.append(MenuItem(text=record.save_name, id=f"saved_{record.id}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "saved_tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "saved_tables_menu"}

    def _show_saved_table_actions_menu(self, user: NetworkUser, save_id: int) -> None:
        """Show actions for a saved table (restore, delete)."""
        items = [
            MenuItem(text=Localization.get(user.locale, "restore-table"), id="restore"),
            MenuItem(
                text=Localization.get(user.locale, "delete-saved-table"), id="delete"
            ),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "saved_table_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "saved_table_actions_menu",
            "save_id": save_id,
        }

    async def _handle_menu(self, client: ClientConnection, packet: dict) -> None:
        """Handle menu selection."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        selection_id = packet.get("selection_id", "")

        state = self._user_states.get(username, {})
        current_menu = state.get("menu")

        # Check if user is in a system lockdown menu. If so, intercept before game logic.
        if current_menu == "banned_menu":
            if selection_id == "disconnect":
                await user.connection.send({"type": "force_exit", "reason": "banned"})
                asyncio.create_task(self._failsafe_close(user))
            return
        elif current_menu == "motd_menu":
            await self._handle_motd_selection(user, selection_id, state)
            return
        elif current_menu == "mandatory_email_menu":
            await self._handle_mandatory_email_selection(user, selection_id)
            return

        # Check if user is in a table - delegate all events to game
        table = self._tables.find_user_table(username)
        if table and table.game:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user)
            return

        # Handle menu selections based on current menu
        if current_menu == "main_menu":
            await self._handle_main_menu_selection(user, selection_id)
        elif current_menu == "personal_options_menu":
            await self._handle_personal_options_selection(user, selection_id)
        elif current_menu == "games_menu":
            await self._handle_games_selection(user, selection_id, state)
        elif current_menu == "tables_menu":
            await self._handle_tables_selection(user, selection_id, state)
        elif current_menu == "active_tables_menu":
            await self._handle_active_tables_selection(user, selection_id)
        elif current_menu == "active_tables_filter_menu":
            await self._handle_active_tables_filter_selection(user, selection_id)
        elif current_menu == "join_menu":
            await self._handle_join_selection(user, selection_id, state)
        elif current_menu == "options_menu":
            await self._handle_options_selection(user, selection_id)
        elif current_menu == "language_menu":
            await self._handle_language_selection(user, selection_id)
        elif current_menu == "speech_settings_menu":
            await self._handle_speech_settings_selection(user, selection_id)
        elif current_menu == "voice_selection_menu":
            await self._handle_voice_selection(user, selection_id)
        elif current_menu == "dice_keeping_style_menu":
            await self._handle_dice_keeping_style_selection(user, selection_id)
        elif current_menu == "saved_tables_menu":
            await self._handle_saved_tables_selection(user, selection_id, state)
        elif current_menu == "saved_table_actions_menu":
            await self._handle_saved_table_actions_selection(user, selection_id, state)
        elif current_menu == "leaderboards_menu":
            await self._handle_leaderboards_selection(user, selection_id, state)
        elif current_menu == "leaderboard_types_menu":
            await self._handle_leaderboard_types_selection(user, selection_id, state)
        elif current_menu == "game_leaderboard":
            await self._handle_game_leaderboard_selection(user, selection_id, state)
        elif current_menu == "my_stats_menu":
            await self._handle_my_stats_selection(user, selection_id, state)
        elif current_menu == "my_game_stats":
            await self._handle_my_game_stats_selection(user, selection_id, state)
        elif current_menu == "profile_menu":
            await self._handle_profile_selection(user, selection_id)
        elif current_menu == "gender_menu":
            await self._handle_gender_selection(user, selection_id)
        elif current_menu == "bio_actions_menu":
            await self._handle_bio_actions_selection(user, selection_id, state)
        elif current_menu == "email_confirm_menu":
            await self._handle_email_confirm_selection(user, selection_id, state)
        elif current_menu == "friends_hub_menu":
            await self._handle_friends_hub_selection(user, selection_id)
        elif current_menu == "friends_list_menu":
            await self._handle_friends_list_selection(user, selection_id)
        elif current_menu == "friend_actions_menu":
            await self._handle_friend_actions_selection(user, selection_id, state)
        elif current_menu == "friend_requests_menu":
            await self._handle_friend_requests_selection(user, selection_id)
        elif current_menu == "friend_request_actions_menu":
            await self._handle_friend_request_actions_selection(user, selection_id, state)
        elif current_menu == "public_profile_menu":
            await self._handle_public_profile_selection(user, selection_id, state)
        elif current_menu == "online_users":
            await self._handle_online_users_selection(user, selection_id, state)
        elif current_menu == "online_user_actions_menu":
            await self._handle_online_user_actions_selection(user, selection_id, state)
        elif current_menu in [
            "admin_menu", "account_approval_menu", "pending_user_actions_menu",
            "promote_admin_menu", "demote_admin_menu", "promote_confirm_menu",
            "demote_confirm_menu", "kick_menu", "kick_confirm_menu", "broadcast_choice_menu",
            "ban_menu", "ban_duration_menu", "ban_reason_menu", "unban_menu",
            "manage_motd_menu", "view_motd_menu"
        ]:
            await self.admin_manager.handle_menu_selection(user, selection_id, current_menu, state)
        elif current_menu == "logout_confirm_menu":
             await self._handle_logout_confirm_selection(user, selection_id)
        elif current_menu == "documentation_menu":
            await self._handle_documentation_selection(user, selection_id)
        elif current_menu == "doc_games_menu":
            await self._handle_doc_games_selection(user, selection_id)
        elif current_menu == "doc_viewer":
            await self._handle_doc_viewer_selection(user, selection_id, state)

    async def _handle_mandatory_email_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle mandatory email setup acknowledgment."""
        if selection_id == "ok":
            user_record = self._db.get_user(user.username)
            user.show_editbox(
                "email_input",
                Localization.get(user.locale, "enter-email"),
                default_value=user_record.email if user_record else "",
            )
            self._user_states[user.username]["menu"] = "email_input"
            # Flag that we came from the mandatory loop so we know where to route after
            self._user_states[user.username]["from_mandatory"] = True

    async def _handle_motd_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle MOTD acknowledgment."""
        if selection_id == "ok":
            version = state.get("motd_version", 0)
            if version > 0:
                self._db.update_user_motd_version(user.username, version)

            # Now proceed with normal login flow
            self._restore_user_state(user, user.username)

    async def _handle_main_menu_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle main menu selection."""
        if selection_id == "play":
            self._show_games_list_menu(user)
        elif selection_id == "active_tables":
            self._show_active_tables_menu(user)
        elif selection_id == "saved_tables":
            self._show_saved_tables_menu(user)
        elif selection_id == "leaderboards":
            self._show_leaderboards_menu(user)
        elif selection_id == "personal_options":
            self._show_personal_options_menu(user)
        elif selection_id == "documentation":
            self._show_documentation_menu(user)
        elif selection_id == "administration":
            if user.trust_level >= 2:
                self.admin_manager._show_admin_menu(user)
        elif selection_id == "logout":
            self._show_logout_confirm_menu(user)

    def _show_personal_options_menu(self, user: NetworkUser) -> None:
        """Show the personal and options sub-menu."""
        items = [
            MenuItem(text=Localization.get(user.locale, "profile"), id="profile"),
            MenuItem(text=Localization.get(user.locale, "friends"), id="friends"),
            MenuItem(text=Localization.get(user.locale, "my-stats"), id="my_stats"),
            MenuItem(text=Localization.get(user.locale, "options"), id="options"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back")
        ]
        user.show_menu(
            "personal_options_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "personal_options_menu"}

    async def _handle_personal_options_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle personal and options menu selection."""
        if selection_id == "profile":
            self._show_profile_menu(user)
        elif selection_id == "friends":
            self._show_friends_hub_menu(user)
        elif selection_id == "my_stats":
            self._show_my_stats_menu(user)
        elif selection_id == "options":
            self._show_options_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    def _show_friends_hub_menu(self, user: NetworkUser) -> None:
        """Show the main friends hub menu."""
        # Get counts for the menu labels
        pending_requests = self._db.get_pending_incoming_requests(user.uuid)
        pending_count = len(pending_requests)

        req_text = Localization.get(user.locale, "friends-pending-requests", count=pending_count) if pending_count > 0 else Localization.get(user.locale, "friends-no-pending-requests")

        items = [
            MenuItem(text=Localization.get(user.locale, "friends-my-friends"), id="my_friends"),
            MenuItem(text=req_text, id="pending_requests"),
            MenuItem(text=Localization.get(user.locale, "friends-send-request"), id="send_request"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back")
        ]
        user.show_menu(
            "friends_hub_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "friends_hub_menu"}

    async def _handle_friends_hub_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle selection in friends hub."""
        if selection_id == "my_friends":
            self._show_friends_list_menu(user)
        elif selection_id == "pending_requests":
            self._show_friend_requests_menu(user)
        elif selection_id == "send_request":
            user.show_editbox(
                "send_friend_request_input",
                Localization.get(user.locale, "enter-friend-username"),
            )
            self._user_states[user.username]["menu"] = "send_friend_request_input"
        elif selection_id == "back":
            self._show_personal_options_menu(user)

    def _show_friends_list_menu(self, user: NetworkUser) -> None:
        """Show the list of accepted friends and their status."""
        friend_uuids = self._db.get_friends(user.uuid)
        items = []

        if not friend_uuids:
            items.append(MenuItem(text=Localization.get(user.locale, "friends-list-empty"), id=""))
        else:
            # Sort friends alphabetically
            friends = []
            for f_uuid in friend_uuids:
                f_name = self._db.get_user_name_by_uuid(f_uuid)
                if f_name:
                    friends.append(f_name)
            friends.sort(key=str.lower)

            for f_name in friends:
                # Determine status
                online_user = self._users.get(f_name)
                # Ensure they are truly online and not stuck in banned screen or unapproved
                state = self._user_states.get(f_name, {})
                is_online = online_user is not None and online_user.approved and state.get("menu") != "banned_menu"

                if not is_online:
                    status = Localization.get(user.locale, "friend-status-offline")
                else:
                    table = self._tables.find_user_table(f_name)
                    if table:
                        game_class = get_game_class(table.game_type)
                        game_name = Localization.get(user.locale, game_class.get_name_key()) if game_class else table.game_type

                        # Determine if spectating
                        is_spectator = False
                        for m in table.members:
                            if m.username == f_name:
                                is_spectator = m.is_spectator
                                break

                        if is_spectator:
                            status = Localization.get(user.locale, "friend-status-spectating", game=game_name)
                        else:
                            status = Localization.get(user.locale, "friend-status-playing", game=game_name)
                    else:
                        status = Localization.get(user.locale, "friend-status-lobby")

                display_text = Localization.get(user.locale, "friend-list-entry", username=f_name, status=status)
                items.append(MenuItem(text=display_text, id=f"friend_{f_name}"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "friends_list_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "friends_list_menu"}

    async def _handle_friends_list_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "back":
            self._show_friends_hub_menu(user)
        elif selection_id.startswith("friend_"):
            target_username = selection_id[7:]
            self._show_friend_actions_menu(user, target_username)

    def _show_friend_actions_menu(self, user: NetworkUser, target_username: str) -> None:
        """Show actions for a specific friend."""
        items = [
            MenuItem(text=Localization.get(user.locale, "view-profile"), id="view_profile"),
        ]

        # Check if they are online and in a table
        if target_username in self._users:
            items.append(MenuItem(text=Localization.get(user.locale, "send-private-message"), id="send_pm"))
            table = self._tables.find_user_table(target_username)
            if table:
                items.append(MenuItem(text=Localization.get(user.locale, "join-table"), id="join_table"))

        items.append(MenuItem(text=Localization.get(user.locale, "remove-friend"), id="remove_friend"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        # Prepend title dynamically as a read-only item
        title = Localization.get(user.locale, "friend-actions-title", username=target_username)
        items.insert(0, MenuItem(text=title, id=""))
        user.show_menu(
            "friend_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "friend_actions_menu",
            "target_username": target_username
        }

    async def _handle_friend_actions_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        target_username = state.get("target_username")
        if not target_username:
            self._show_friends_list_menu(user)
            return

        if selection_id == "back":
            self._show_friends_list_menu(user)

        elif selection_id == "view_profile":
            self._show_public_profile(user, target_username, "friend_actions_menu")

        elif selection_id == "send_pm":
            user.show_editbox(
                "send_pm_input",
                Localization.get(user.locale, "enter-pm-message", username=target_username),
                multiline=True,
                max_length=500
            )
            self._user_states[user.username]["menu"] = "send_pm_input"
            self._user_states[user.username]["target_username"] = target_username

        elif selection_id == "join_table":
            table = self._tables.find_user_table(target_username)
            if table:
                # Check if we are already in a table
                current_table = self._tables.find_user_table(user.username)
                if current_table:
                    if current_table == table:
                         user.speak_l("already-in-table")
                         self._show_friend_actions_menu(user, target_username)
                         return
                    else:
                         current_table.remove_member(user.username)

                # Proceed to join
                self._auto_join_table(user, table, table.game_type)
            else:
                user.speak_l("table-not-exists")
                self._show_friend_actions_menu(user, target_username)

        elif selection_id == "remove_friend":
            target_record = self._db.get_user(target_username)
            if target_record:
                self._db.remove_friendship(user.uuid, target_record.uuid)
                user.speak_l("friend-removed-success", username=target_username)
                user.play_sound("friend_removed.ogg")

                # Notify target
                target_user = self._users.get(target_username)
                if target_user:
                    target_user.speak_l("friend-removed-notify", username=user.username)
                    target_user.play_sound("friend_removed.ogg")
                else:
                    self._db.add_notification(target_record.uuid, user.username, "friend_removed")

                self.on_friend_requests_changed(target_record.uuid)

            self._show_friends_list_menu(user)

    def _show_friend_requests_menu(self, user: NetworkUser) -> None:
        """Show list of pending incoming requests."""
        pending_uuids = self._db.get_pending_incoming_requests(user.uuid)
        items = []

        if not pending_uuids:
            items.append(MenuItem(text=Localization.get(user.locale, "no-pending-requests"), id=""))
        else:
            for r_uuid in pending_uuids:
                r_name = self._db.get_user_name_by_uuid(r_uuid)
                if r_name:
                    items.append(MenuItem(text=r_name, id=f"req_{r_name}"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "friend_requests_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "friend_requests_menu"}

    async def _handle_friend_requests_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "back":
            self._show_friends_hub_menu(user)
        elif selection_id.startswith("req_"):
            target_username = selection_id[4:]
            self._show_friend_request_actions_menu(user, target_username)

    def _show_friend_request_actions_menu(self, user: NetworkUser, target_username: str) -> None:
        """Show accept/decline for a specific request."""
        title = Localization.get(user.locale, "friend-request-from", username=target_username)
        items = [
            MenuItem(text=title, id=""),
            MenuItem(text=Localization.get(user.locale, "accept"), id="accept"),
            MenuItem(text=Localization.get(user.locale, "decline"), id="decline"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back")
        ]
        user.show_menu(
            "friend_request_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "friend_request_actions_menu",
            "target_username": target_username
        }

    async def _handle_friend_request_actions_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        target_username = state.get("target_username")
        if not target_username:
            self._show_friend_requests_menu(user)
            return

        target_record = self._db.get_user(target_username)
        if not target_record:
            user.speak_l("unknown-player")
            self._show_friend_requests_menu(user)
            return

        if selection_id == "back":
            self._show_friend_requests_menu(user)

        elif selection_id == "accept":
            # Attempt to accept
            success = self._db.accept_friend_request(target_record.uuid, user.uuid)
            if success:
                user.speak_l("friend-accepted-success", username=target_username)
                user.play_sound("friend_accepted.ogg")

                # Notify target
                target_user = self._users.get(target_username)
                if target_user:
                    target_user.speak_l("friend-accepted-notify", username=user.username)
                    target_user.play_sound("friend_accepted.ogg")
                else:
                    self._db.add_notification(target_record.uuid, user.username, "friend_accepted")
                self.on_friend_requests_changed(target_record.uuid)
            else:
                user.speak_l("request-not-found")
            self._show_friend_requests_menu(user)

        elif selection_id == "decline":
            # Delete it
            self._db.remove_friendship(user.uuid, target_record.uuid)
            user.speak_l("friend-declined-success")

            # Notify target
            target_user = self._users.get(target_username)
            if target_user:
                target_user.speak_l("friend-declined-notify", username=user.username)
                target_user.play_sound("friend_declined.ogg")
            else:
                self._db.add_notification(target_record.uuid, user.username, "friend_declined")

            self.on_friend_requests_changed(target_record.uuid)
            self._show_friend_requests_menu(user)

    def _show_public_profile(self, requesting_user: NetworkUser, target_username: str, return_menu_id: str) -> None:
        """Show a read-only profile view of another player."""
        target_record = self._db.get_user(target_username)
        if not target_record:
            requesting_user.speak_l("unknown-player")
            # Fallback to the previous menu based on state if it's tricky, but we have return_menu_id
            state = self._user_states.get(requesting_user.username, {})
            if return_menu_id == "friend_actions_menu":
                 self._show_friend_actions_menu(requesting_user, state.get("target_username", ""))
            else:
                 self._show_main_menu(requesting_user)
            return

        date_str = target_record.registration_date[:10] if target_record.registration_date else "Unknown"
        bio_str = target_record.bio if target_record.bio else Localization.get(requesting_user.locale, "profile-bio-empty")
        gender_loc_key = f"gender-{target_record.gender.lower().replace(' ', '-')}"
        gender_str = Localization.get(requesting_user.locale, gender_loc_key)

        items = [
            MenuItem(text=Localization.get(requesting_user.locale, "profile-registration-date", date=date_str), id=""),
            MenuItem(text=Localization.get(requesting_user.locale, "profile-username", username=target_record.username), id=""),
            MenuItem(text=Localization.get(requesting_user.locale, "profile-gender", gender=gender_str), id=""),
            MenuItem(text=Localization.get(requesting_user.locale, "profile-bio", bio=bio_str), id=""),
        ]

        # Admins and Devs can see the email
        if requesting_user.trust_level >= 2:
             email_str = target_record.email if target_record.email else Localization.get(requesting_user.locale, "profile-email-empty")
             items.append(MenuItem(text=Localization.get(requesting_user.locale, "admin-view-email", email=email_str), id=""))

        items.append(MenuItem(text=Localization.get(requesting_user.locale, "back"), id="back"))

        title = Localization.get(requesting_user.locale, "public-profile-title", username=target_record.username)
        items.insert(0, MenuItem(text=title, id=""))

        requesting_user.show_menu(
            "public_profile_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[requesting_user.username] = {
            "menu": "public_profile_menu",
            "return_menu_id": return_menu_id,
            "target_username": target_username
        }

    async def _handle_public_profile_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle selection in public profile."""
        if selection_id == "back":
            return_menu_id = state.get("return_menu_id")
            if return_menu_id == "friend_actions_menu":
                 self._show_friend_actions_menu(user, state.get("target_username", ""))
            elif return_menu_id == "online_user_actions_menu":
                 # For online user actions, we need to construct a pseudo-state to resume correctly
                 # However, _show_online_user_actions_menu expects a state dict representing the Online List's origins.
                 # Let's pass a generic state to avoid crashing, though the deeply nested back might route to main_menu if lost.
                 pseudo_state = {"return_menu_id": "main_menu", "return_menu": {}, "return_state": {}}
                 self._show_online_user_actions_menu(user, state.get("target_username", ""), pseudo_state)
            else:
                 self._show_main_menu(user)

    def _show_profile_menu(self, user: NetworkUser) -> None:
        """Show the user's profile menu."""
        user_record = self._db.get_user(user.username)
        if not user_record:
            self._show_personal_options_menu(user)
            return

        date_str = user_record.registration_date[:10] if user_record.registration_date else "Unknown"
        email_str = user_record.email if user_record.email else Localization.get(user.locale, "profile-email-empty")
        bio_str = user_record.bio if user_record.bio else Localization.get(user.locale, "profile-bio-empty")
        gender_loc_key = f"gender-{user_record.gender.lower().replace(' ', '-')}"
        gender_str = Localization.get(user.locale, gender_loc_key)

        items = [
            MenuItem(text=Localization.get(user.locale, "profile-registration-date", date=date_str), id=""),
            MenuItem(text=Localization.get(user.locale, "profile-username", username=user_record.username), id=""),
            MenuItem(text=Localization.get(user.locale, "profile-email", email=email_str), id="edit_email"),
            MenuItem(text=Localization.get(user.locale, "profile-gender", gender=gender_str), id="edit_gender"),
            MenuItem(text=Localization.get(user.locale, "profile-bio", bio=bio_str), id="edit_bio"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back")
        ]

        user.show_menu(
            "profile_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "profile_menu"}

    async def _handle_profile_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle profile menu selection."""
        if selection_id == "edit_email":
            user_record = self._db.get_user(user.username)
            user.show_editbox(
                "email_input",
                Localization.get(user.locale, "enter-email"),
                default_value=user_record.email if user_record else "",
            )
            self._user_states[user.username]["menu"] = "email_input"
        elif selection_id == "edit_gender":
            self._show_gender_menu(user)
        elif selection_id == "edit_bio":
            self._show_bio_actions_menu(user)
        elif selection_id == "back":
            self._show_personal_options_menu(user)

    def _show_gender_menu(self, user: NetworkUser) -> None:
        """Show the gender selection menu."""
        genders = ["Male", "Female", "Non-binary", "Not set"]
        user_record = self._db.get_user(user.username)
        current_gender = user_record.gender if user_record else "Not set"

        items = []
        for g in genders:
            prefix = "* " if g == current_gender else ""
            loc_key = f"gender-{g.lower().replace(' ', '-')}"
            localized_gender = Localization.get(user.locale, loc_key)
            items.append(MenuItem(text=f"{prefix}{localized_gender}", id=f"gender_{g}"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "gender_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "gender_menu"}

    async def _handle_gender_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle gender selection."""
        if selection_id.startswith("gender_"):
            new_gender = selection_id[7:]
            user_record = self._db.get_user(user.username)
            if user_record and user_record.gender == new_gender:
                user.speak_l("no-changes-made")
            else:
                self._db.update_user_gender(user.username, new_gender)
                user.speak_l("gender-updated")
            self._show_profile_menu(user)
        elif selection_id == "back":
            self._show_profile_menu(user)

    def _show_bio_actions_menu(self, user: NetworkUser) -> None:
        """Show bio action options."""
        items = [
            MenuItem(text=Localization.get(user.locale, "action-set-edit"), id="set_bio"),
            MenuItem(text=Localization.get(user.locale, "action-delete"), id="delete_bio"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back")
        ]
        user.show_menu(
            "bio_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "bio_actions_menu"}

    async def _handle_bio_actions_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle bio action selection."""
        if selection_id == "set_bio":
            user_record = self._db.get_user(user.username)
            user.show_editbox(
                "bio_input",
                Localization.get(user.locale, "enter-bio"),
                default_value=user_record.bio if user_record else "",
                multiline=True,
                max_length=250
            )
            self._user_states[user.username]["menu"] = "bio_input"
        elif selection_id == "delete_bio":
            user_record = self._db.get_user(user.username)
            if user_record and user_record.bio:
                self._db.update_user_bio(user.username, "")
                user.speak_l("bio-deleted")
            else:
                user.speak_l("bio-already-empty")
            self._show_profile_menu(user)
        elif selection_id == "back":
            self._show_profile_menu(user)

    def _show_email_confirm_menu(self, user: NetworkUser, new_email: str) -> None:
        """Show email change confirmation menu."""
        user.speak_l("confirm-email-change", email=new_email)
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "email_confirm_menu",
            items,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "email_confirm_menu",
            "pending_email": new_email
        }

    async def _handle_email_confirm_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle email change confirmation selection."""
        if selection_id == "yes":
            new_email = state.get("pending_email", "")
            self._db.update_user_email(user.username, new_email)
            user.speak_l("email-updated")
            self._show_profile_menu(user)
        elif selection_id == "no":
            self._show_profile_menu(user)

    def _show_logout_confirm_menu(self, user: NetworkUser) -> None:
        """Show logout confirmation menu."""
        user.speak_l("logout-confirm-title")
        items = [
            MenuItem(text=Localization.get(user.locale, "logout-confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "logout-confirm-no"), id="no"),
        ]
        user.show_menu(
            "logout_confirm_menu",
            items,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "logout_confirm_menu"}

    async def _handle_logout_confirm_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle logout confirmation selection."""
        if selection_id == "yes":
            # Send force_exit command
            # The client will speak "Goodbye" and sys.exit(0), checking self.quitting to avoid reconnects
            await user.connection.send({"type": "force_exit"})
            
            # We don't close the connection immediately. We let the client close it.
            # But we can schedule a failsafe close in case client is stuck
            asyncio.create_task(self._failsafe_close(user))
        elif selection_id == "no":
            self._show_main_menu(user)

    async def _failsafe_close(self, user):
        """Close connection after delay if client hasn't already."""
        await asyncio.sleep(5.0)
        try:
             await user.connection.close(1000, "Logout Failsafe")
        except:
             pass

    # ==========================================================================
    # Documentation System
    # ==========================================================================

    def _show_documentation_menu(self, user: NetworkUser) -> None:
        """Show main documentation menu with categories."""
        # Get categories (hardcoded for now, could be dynamic)
        manager = DocumentationManager.get_instance()
        categories = manager.get_all_categories(user.locale)
        
        items = []
        for doc_id, label_key in categories.items():
            items.append(
                MenuItem(text=Localization.get(user.locale, label_key), id=doc_id)
            )
        
        # Add Rules section
        items.append(MenuItem(text=Localization.get(user.locale, "game-rules"), id="game_rules"))
        
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "documentation_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "documentation_menu"}

    def _show_game_rules_menu(self, user: NetworkUser) -> None:
        """Show list of games to read rules for."""
        games = GameRegistry.get_all()
        # Sort games by localized name
        game_list = []
        for game_class in games:
            name = Localization.get(user.locale, game_class.get_name_key())
            game_list.append((game_class, name))
        game_list.sort(key=lambda x: x[1])

        items = []
        for game_class, name in game_list:
             # Using game type as doc_id suffix: games/scopa
            items.append(MenuItem(text=name, id=f"games/{game_class.get_type()}"))
            
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "doc_games_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "doc_games_menu"}

    async def _handle_read_documentation(self, client: ClientConnection, packet: dict) -> None:
        """Handle request to read a specific documentation file."""
        # This packet comes from the client when user selects a doc item
        # But actually we handle menu Selections, so this might be used if we had a direct command
        # For now, we use menu handlers.
        pass

    async def _show_document_content(self, user: NetworkUser, doc_id: str) -> None:
        """
        Display document content.
        For simplicity in this text/audio interface, we will:
        1. Parse markdown headings and paragraphs
        2. Present them as a read-only menu or speak them?
        
        Better approach for accessibility:
        Present as a menu where:
        - Each Header is a menu item (e.g. "H1: Welcome")
        - Each Paragraph is a menu item (e.g. "PlayAural is...")
        User can browse line by line.
        """
        manager = DocumentationManager.get_instance()
        content = manager.get_document(doc_id, user.locale)
        
        if not content:
            user.speak_l("document-not-found")
            return

        # Simple Markdown Element Parser
        items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Clean markdown formatting characters
            # Remove bold/italic markers
            clean_text = line.replace('**', '').replace('__', '').replace('*', '').replace('`', '').replace('&nbsp;', '')
            
            if clean_text.startswith('#'):
                # Header - remove # and extra spaces
                clean_text = clean_text.lstrip('#').strip()
                # Just show the text, no decorative ===
                items.append(MenuItem(text=clean_text, id="header"))
            elif clean_text.startswith('-') or clean_text.startswith('•'):
                # List item
                clean_text = clean_text.lstrip('-• ').strip()
                items.append(MenuItem(text=f"{clean_text}", id="list_item"))
            else:
                # Paragraph
                items.append(MenuItem(text=clean_text, id="text"))
        
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        
        user.show_menu(
            "doc_viewer",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST
        )
        # Store metadata so we know where to go back to
        self._user_states[user.username] = {
            "menu": "doc_viewer",
            "doc_id": doc_id
        }

    async def _handle_documentation_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle main documentation menu selection."""
        if selection_id == "back":
            self._show_main_menu(user)
        elif selection_id == "game_rules":
            self._show_game_rules_menu(user)
        else:
            # Assume selection_id is a doc_id (e.g., 'intro', 'global_keys')
            await self._show_document_content(user, selection_id)

    async def _handle_doc_games_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle game rules list selection."""
        if selection_id == "back":
            self._show_documentation_menu(user)
        else:
            # selection_id is like 'games/scopa'
            await self._show_document_content(user, selection_id)

    async def _handle_doc_viewer_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle selection in document viewer."""
        if selection_id == "back":
            # Logic to decide where to go back to
            doc_id = state.get("doc_id", "")
            if doc_id.startswith("games/"):
                self._show_game_rules_menu(user)
            else:
                self._show_documentation_menu(user)
        else:
            # User clicked a text line - maybe just read it again?
            # Or do nothing, TTS reads it on focus.
            pass

    async def _handle_options_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle options menu selection."""
        if selection_id == "language":
            self._show_language_menu(user)
            return
        elif selection_id == "speech_settings":
            self._show_speech_settings_menu(user)
            return

        prefs = user.preferences

        if selection_id == "music_volume":
            user.show_editbox(
                "music_volume_input",
                Localization.get(user.locale, "enter-music-volume"),
                default_value=str(prefs.music_volume),
            )
            self._user_states[user.username]["menu"] = "music_volume_input"
            return
        elif selection_id == "ambience_volume":
            user.show_editbox(
                "ambience_volume_input",
                Localization.get(user.locale, "enter-ambience-volume"),
                default_value=str(prefs.ambience_volume),
            )
            self._user_states[user.username]["menu"] = "ambience_volume_input"
            return
        elif selection_id == "turn_sound":
            prefs.play_turn_sound = not prefs.play_turn_sound
            self._save_user_preferences(user)
            self._show_options_menu(user)
        elif selection_id == "mute_global_chat":
            prefs.mute_global_chat = not prefs.mute_global_chat
            self._save_user_preferences(user)
            self._sync_pref_to_client(user, "social/mute_global_chat", prefs.mute_global_chat)
            self._show_options_menu(user)
        elif selection_id == "mute_table_chat":
            prefs.mute_table_chat = not prefs.mute_table_chat
            self._save_user_preferences(user)
            self._sync_pref_to_client(user, "social/mute_table_chat", prefs.mute_table_chat)
            self._show_options_menu(user)
        elif selection_id == "invert_multiline_enter":
            prefs.invert_multiline_enter_behavior = not prefs.invert_multiline_enter_behavior
            self._save_user_preferences(user)
            self._sync_pref_to_client(user, "interface/invert_multiline_enter_behavior", prefs.invert_multiline_enter_behavior)
            self._show_options_menu(user)
        elif selection_id == "play_typing_sounds":
            prefs.play_typing_sounds = not prefs.play_typing_sounds
            self._save_user_preferences(user)
            self._sync_pref_to_client(user, "interface/play_typing_sounds", prefs.play_typing_sounds)
            self._show_options_menu(user)
        elif selection_id == "notify_table_created":
            prefs.notify_table_created = not prefs.notify_table_created
            self._save_user_preferences(user)
            # No client sync needed as this is purely server-side logic
            self._show_options_menu(user)
        elif selection_id == "notify_user_presence":
            prefs.notify_user_presence = not prefs.notify_user_presence
            self._save_user_preferences(user)
            self._show_options_menu(user)
        elif selection_id == "notify_friend_presence":
            prefs.notify_friend_presence = not prefs.notify_friend_presence
            self._save_user_preferences(user)
            self._show_options_menu(user)
        elif selection_id == "clear_kept":
            prefs.clear_kept_on_roll = not prefs.clear_kept_on_roll
            self._save_user_preferences(user)
            self._show_options_menu(user)
        elif selection_id == "dice_keeping_style":
            self._show_dice_keeping_style_menu(user)
        elif selection_id == "back":
            self._show_personal_options_menu(user)

    def _show_dice_keeping_style_menu(self, user: NetworkUser) -> None:
        """Show dice keeping style selection menu."""
        items = []
        current_style = user.preferences.dice_keeping_style
        for style, name_key in self.DICE_KEEPING_STYLES.items():
            prefix = "* " if style == current_style else ""
            name = Localization.get(user.locale, name_key)
            items.append(MenuItem(text=f"{prefix}{name}", id=f"style_{style.value}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "dice_keeping_style_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "dice_keeping_style_menu"}

    async def _handle_dice_keeping_style_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle dice keeping style selection."""
        if selection_id.startswith("style_"):
            style_value = selection_id[6:]  # Remove "style_" prefix
            style = DiceKeepingStyle.from_str(style_value)
            user.preferences.dice_keeping_style = style
            self._save_user_preferences(user)
            style_key = self.DICE_KEEPING_STYLES.get(style, "dice-keeping-style-indexes")
            style_name = Localization.get(user.locale, style_key)
            user.speak_l("dice-keeping-style-changed", style=style_name)
            self._show_options_menu(user)
            return
        # Back or invalid
        self._show_options_menu(user)

    def _save_user_preferences(self, user: NetworkUser) -> None:
        """Save user preferences to database."""
        prefs_json = json.dumps(user.preferences.to_dict())
        self._db.update_user_preferences(user.username, prefs_json)

    async def _handle_language_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle language selection."""
        if selection_id.startswith("lang_"):
            try:
                # Change language
                lang_code = selection_id[5:]
                user.set_locale(lang_code)
                self._db.update_user_locale(user.username, lang_code)
                user.speak_l("language-changed", language=Localization.get(lang_code, f"language-{lang_code}"))
                
                # Send packet to update client config immediately
                await user.connection.send({
                    "type": "update_locale",
                    "locale": lang_code
                })
            except Exception as e:
                logging.getLogger("playaural").exception("Error changing language")
                user.speak_l("server-error-changing-language", error=str(e))
            
            self._show_options_menu(user)
            return
        # Back or invalid
        self._show_options_menu(user)

    async def _handle_categories_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle category selection."""
        if selection_id.startswith("category_"):
            category = selection_id[9:]  # Remove "category_" prefix
            self._show_games_menu(user, category)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_games_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle game selection."""
        if selection_id.startswith("game_"):
            game_type = selection_id[5:]  # Remove "game_" prefix
            self._show_tables_menu(user, game_type)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_tables_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle tables menu selection."""
        game_type = state.get("game_type", "")

        if selection_id == "create_table":
            table = self._tables.create_table(game_type, user.username, user)

            # Create game immediately and initialize lobby
            game_class = get_game_class(game_type)
            if game_class:
                game = game_class()
                table.game = game
                game._table = table  # Enable game to call table.destroy()
                game.initialize_lobby(user.username, user)

                user.speak_l(
                    "table-created",
                    buffer="game",
                    host=user.username,
                    game=state.get("game_name", game_type),
                )
                
                # Broadcast table creation to all other approved users
                name_key = game_class.get_name_key()
                for u in self._users.values():
                    if u.username != user.username and u.approved and u.preferences.notify_table_created:
                        local_game_name = Localization.get(u.locale, name_key)
                        u.speak_l(
                            "table-created-broadcast", 
                            buffer="system",
                            host=user.username, 
                            game=local_game_name
                        )

                min_players = game_class.get_min_players()
                max_players = game_class.get_max_players()
                user.speak_l(
                    "waiting-for-players",
                    buffer="game",
                    current=len(game.players),
                    min=min_players,
                    max=max_players,
                )
            self._user_states[user.username] = {
                "menu": "in_game",
                "table_id": table.table_id,
            }

        elif selection_id.startswith("table_"):
            table_id = selection_id[6:]  # Remove "table_" prefix
            table = self._tables.get_table(table_id)
            if table:
                self._auto_join_table(user, table, game_type)
            else:
                user.speak_l("table-not-exists", buffer="system")
                self._show_tables_menu(user, game_type)

        elif selection_id == "back":
            # Return to the main games list (not category view)
            self._show_games_list_menu(user)

    async def _handle_active_tables_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle active tables menu selection."""
        if selection_id == "toggle_filter":
            self._show_active_tables_filter_menu(user)
            return

        elif selection_id == "no_tables_msg":
            return  # Do nothing if they click the empty message

        elif selection_id.startswith("table_"):
            table_id = selection_id[6:]
            table = self._tables.get_table(table_id)
            if table:
                self._auto_join_table(user, table, table.game_type)
            else:
                user.speak_l("table-not-exists")
                self._show_active_tables_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_active_tables_filter_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle active tables filter sub-menu selection."""
        if selection_id.startswith("filter_"):
            new_filter = selection_id[7:]  # Remove 'filter_' prefix (all, waiting, playing)
            user.preferences.active_tables_filter = new_filter
            self._save_user_preferences(user)

            filter_name_key = f"filter-name-{new_filter}"
            filter_name = Localization.get(user.locale, filter_name_key)
            user.speak_l("active-tables-filter", filter=filter_name)

            # Return to the active tables menu (which will automatically apply the new filter)
            self._show_active_tables_menu(user)
            return

        elif selection_id == "back":
            self._show_active_tables_menu(user)
            return

    def _auto_join_table(
        self, user: NetworkUser, table: "Table", game_type: str
    ) -> None:
        """Automatically join a table as player or spectator.

        Joins as player if:
        - Game has not started yet (status is "waiting")
        - Game has room for more players (less than max_players)

        Otherwise joins as spectator.
        """
        game = table.game
        if not game:
            user.speak_l("table-not-exists")
            self._show_tables_menu(user, game_type)
            return

        table_id = table.table_id

        # Check if user is reclaiming a bot-replaced slot
        reclaimed_player = None
        if game.status == "playing":
            for player in game.players:
                if player.is_bot and player.id == user.uuid:
                    reclaimed_player = player
                    break

        if reclaimed_player:
            # User is reclaiming their slot from a bot
            reclaimed_player.is_bot = False
            game._users.pop(reclaimed_player.id, None)  # Remove bot user
            game.attach_user(reclaimed_player.id, user)  # Attach human user
            table.add_member(user.username, user, as_spectator=reclaimed_player.is_spectator)
            game.broadcast_l("player-reclaimed-from-bot", player=user.username)
            game.broadcast_sound("online.ogg")
            game.rebuild_all_menus()
        else:
            # Determine if user can join as player
            active_players_count = sum(1 for p in game.players if not p.is_spectator)
            can_join_as_player = (
                game.status != "playing"
                and active_players_count < game.get_max_players()
            )

            if can_join_as_player:
                # Join as player
                table.add_member(user.username, user, as_spectator=False)
                game.add_player(user.username, user)
                game.broadcast_l("table-joined", player=user.username)
                game.broadcast_sound("join.ogg")
                game.rebuild_all_menus()
            else:
                # Join as spectator
                table.add_member(user.username, user, as_spectator=True)
                game.add_spectator(user.username, user)
                user.speak_l("spectator-joined", host=table.host)
                game.broadcast_l("now-spectating", player=user.username)
                game.broadcast_sound("join_spectator.ogg")
                game.rebuild_all_menus()

        self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

    def _return_from_join_menu(self, user: NetworkUser, state: dict) -> None:
        """Return to the appropriate tables menu after join."""
        if state.get("return_menu") == "active_tables_menu":
            self._show_active_tables_menu(user)
        else:
            self._show_tables_menu(user, state.get("game_type", ""))

    async def _handle_join_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle join menu selection."""
        table_id = state.get("table_id")
        table = self._tables.get_table(table_id)

        if not table or not table.game:
            user.speak_l("table-not-exists")
            self._return_from_join_menu(user, state)
            return

        game = table.game

        if selection_id == "join_player":
            # Check if game is already in progress
            if game.status == "playing":
                # Look for a player with matching UUID that is now a bot
                matching_player = None
                for p in game.players:
                    if p.id == user.uuid and p.is_bot:
                        matching_player = p
                        break

                if matching_player:
                    # Take over from the bot
                    matching_player.is_bot = False
                    game.attach_user(matching_player.id, user)
                    table.add_member(user.username, user, as_spectator=False)
                    game.broadcast_l("player-took-over", player=user.username)
                    game.broadcast_sound("join.ogg")
                    game.rebuild_all_menus()
                    self._user_states[user.username] = {
                        "menu": "in_game",
                        "table_id": table_id,
                    }
                    return
                else:
                    # No matching player - join as spectator instead
                    table.add_member(user.username, user, as_spectator=True)
                    game.add_spectator(user.username, user)
                    user.speak_l("spectator-joined", host=table.host)
                    game.broadcast_l("now-spectating", player=user.username)
                    game.broadcast_sound("join_spectator.ogg")
                    game.rebuild_all_menus()
                    self._user_states[user.username] = {
                        "menu": "in_game",
                        "table_id": table_id,
                    }
                    return

            active_players_count = sum(1 for p in game.players if not p.is_spectator)
            if active_players_count >= game.get_max_players():
                user.speak_l("table-full")
                self._return_from_join_menu(user, state)
                return

            # Add player to game
            table.add_member(user.username, user, as_spectator=False)
            game.add_player(user.username, user)
            game.broadcast_l("table-joined", player=user.username)
            game.broadcast_sound("join.ogg")
            game.rebuild_all_menus()
            self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

        elif selection_id == "join_spectator":
            table.add_member(user.username, user, as_spectator=True)
            game.add_spectator(user.username, user)
            user.speak_l("spectator-joined", host=table.host)
            game.broadcast_l("now-spectating", player=user.username)
            game.broadcast_sound("join_spectator.ogg")
            game.rebuild_all_menus()
            self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

        elif selection_id == "back":
            self._return_from_join_menu(user, state)

    async def _handle_saved_tables_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle saved tables menu selection."""
        if selection_id.startswith("saved_"):
            try:
                save_id = int(selection_id[6:])  # Remove "saved_" prefix
                self._show_saved_table_actions_menu(user, save_id)
            except ValueError:
                # Malformed selection_id (like 'saved_tables') -> refresh menu
                self._show_saved_tables_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_saved_table_actions_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle saved table actions (restore/delete)."""
        save_id = state.get("save_id")
        if not save_id:
            self._show_main_menu(user)
            return

        if selection_id == "restore":
            await self._restore_saved_table(user, save_id)
        elif selection_id == "delete":
            self._db.delete_saved_table(save_id)
            user.speak_l("saved-table-deleted")
            self._show_saved_tables_menu(user)
        elif selection_id == "back":
            self._show_saved_tables_menu(user)

    async def _restore_saved_table(self, user: NetworkUser, save_id: int) -> None:
        """Restore a saved table."""
        import json
        from ..users.bot import Bot

        record = self._db.get_saved_table(save_id)
        if not record:
            user.speak_l("table-not-exists")
            self._show_main_menu(user)
            return

        # Get the game class
        game_class = get_game_class(record.game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            self._show_main_menu(user)
            return

        # Parse members from saved state
        members_data = json.loads(record.members_json)
        human_players = [m for m in members_data if not m.get("is_bot", False)]

        # Check all human players are available
        missing_players = []
        for member in human_players:
            member_username = member.get("username")
            if member_username not in self._users:
                missing_players.append(member_username)
            else:
                # Check they're not already in a table
                existing_table = self._tables.find_user_table(member_username)
                if existing_table:
                    missing_players.append(member_username)

        if missing_players:
            user.speak_l("missing-players", players=", ".join(missing_players))
            self._show_saved_tables_menu(user)
            return

        # All players available - create table and restore game
        table = self._tables.create_table(record.game_type, user.username, user)

        # Load game from JSON and rebuild runtime state
        game = game_class.from_json(record.game_json)
        game.rebuild_runtime_state()
        table.game = game
        game._table = table  # Enable game to call table.destroy()

        # Update host to the restorer
        game.host = user.username

        # Attach users and transfer all human players
        # NOTE: We must attach users by player.id (UUID), not by username.
        # The deserialized game has player objects with their original IDs.
        for member in members_data:
            member_username = member.get("username")
            is_bot = member.get("is_bot", False)

            # Find the player object by name to get their ID
            player = game.get_player_by_name(member_username)
            if not player:
                continue

            if is_bot:
                # Recreate bot with the player's original ID
                bot_user = Bot(member_username, uuid=player.id)
                game.attach_user(player.id, bot_user)
            else:
                # Attach human user by player ID
                member_user = self._users.get(member_username)
                if member_user:
                    table.add_member(member_username, member_user, as_spectator=False)
                    game.attach_user(player.id, member_user)
                    self._user_states[member_username] = {
                        "menu": "in_game",
                        "table_id": table.table_id,
                    }

        # Setup keybinds (runtime only, not serialized)
        # Action sets are already restored from serialization
        game.setup_keybinds()

        # Rebuild menus for all players
        game.rebuild_all_menus()

        # Notify all players
        game.broadcast_l("table-restored")

        # Delete the saved table now that it's been restored
        self._db.delete_saved_table(save_id)

    def _show_leaderboards_menu(self, user: NetworkUser) -> None:
        """Show leaderboards game selection menu."""
        categories = GameRegistry.get_by_category()
        items = []

        # Add all games from all categories
        for category_key in sorted(categories.keys()):
            for game_class in categories[category_key]:
                game_name = Localization.get(user.locale, game_class.get_name_key())
                items.append(
                    MenuItem(text=game_name, id=f"lb_{game_class.get_type()}")
                )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "leaderboards_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "leaderboards_menu"}

    def _show_leaderboard_types_menu(self, user: NetworkUser, game_type: str) -> None:
        """Show leaderboard type selection menu for a game."""
        game_class = get_game_class(game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            return

        # Check if there's any data for this game
        results = self._db.get_game_stats(game_type, limit=1)
        if not results:
            # No data - speak message and stay on game selection
            user.speak_l("leaderboard-no-data")
            return

        game_name = Localization.get(user.locale, game_class.get_name_key())

        # Available leaderboard types (common to all games)
        supported_types = game_class.get_supported_leaderboards()
        items = [
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-wins"),
                id="type_wins",
            )
        ]

        if "rating" in supported_types:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-type-rating"),
                    id="type_rating",
                )
            )

        if "total_score" in supported_types:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-type-total-score"),
                    id="type_total_score",
                )
            )

        if "high_score" in supported_types:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-type-high-score"),
                    id="type_high_score",
                )
            )

        if "games_played" in supported_types:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-type-games-played"),
                    id="type_games_played",
                )
            )

        # Game-specific leaderboards (declared by each game class)
        for lb_config in game_class.get_leaderboard_types():
            lb_id = lb_config["id"]
            # Convert underscores to hyphens for localization key
            loc_key = f"leaderboard-type-{lb_id.replace('_', '-')}"
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, loc_key),
                    id=f"type_{lb_id}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "leaderboard_types_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "leaderboard_types_menu",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_wins_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show win leaders leaderboard."""
        from ..game_utils.stats_helpers import LeaderboardHelper

        # Fetch top wins from pre-calculated stats avoiding N+1 queries
        top_wins = self._db.get_top_wins_with_losses(game_type, limit=10)

        items = []

        for rank, (player_id, player_name, wins, losses) in enumerate(top_wins, 1):
            total = wins + losses
            percentage = round((wins / total * 100) if total > 0 else 0)
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-wins-entry",
                        rank=rank,
                        player=player_name,
                        wins=int(wins),
                        losses=int(losses),
                        percentage=int(percentage),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_rating_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show skill rating leaderboard."""
        from ..game_utils.stats_helpers import RatingHelper

        rating_helper = RatingHelper(self._db, game_type)
        ratings = rating_helper.get_leaderboard(limit=10)

        items = []

        if not ratings:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-no-ratings"),
                    id="no_data",
                )
            )
        else:
            for rank, (player_name, rating) in enumerate(ratings, 1):
                items.append(
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "leaderboard-rating-entry",
                            rank=rank,
                            player=player_name,
                            rating=round(rating.ordinal),
                            mu=round(rating.mu, 1),
                            sigma=round(rating.sigma, 1),
                        ),
                        id=f"entry_{rank}",
                    )
                )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_total_score_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show total score leaderboard."""
        from ..game_utils.stats_helpers import LeaderboardHelper

        top_scores = self._db.get_top_player_game_stats(game_type, "total_score", limit=10)

        items = []

        for rank, (player_id, player_name, total) in enumerate(top_scores, 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-score-entry",
                        rank=rank,
                        player=player_name,
                        value=int(total),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_high_score_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show high score leaderboard."""
        top_scores = self._db.get_top_player_game_stats(game_type, "high_score", limit=10)

        items = []

        for rank, (player_id, player_name, high) in enumerate(top_scores, 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-score-entry",
                        rank=rank,
                        player=player_name,
                        value=int(high),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_games_played_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show games played leaderboard."""
        top_games = self._db.get_top_player_game_stats(game_type, "games_played", limit=10)

        items = []

        for rank, (player_id, player_name, count) in enumerate(top_games, 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-games-entry",
                        rank=rank,
                        player=player_name,
                        value=int(count),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _extract_value_from_path(
        self, data: dict, path: str, player_id: str, player_name: str
    ) -> float | None:
        """Extract a value from custom_data using a dot-separated path.

        Supports {player_id} and {player_name} placeholders in path.
        """
        # Replace placeholders
        resolved_path = path.replace("{player_id}", player_id)
        resolved_path = resolved_path.replace("{player_name}", player_name)

        # Navigate the path
        parts = resolved_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        # Convert to float if possible
        if isinstance(current, (int, float)):
            return float(current)
        return None

    def _show_custom_leaderboard(
        self,
        user: NetworkUser,
        game_type: str,
        game_name: str,
        config: dict,
    ) -> None:
        """Show a custom leaderboard using declarative config."""
        lb_id = config["id"]
        format_key = config.get("format", "score")
        decimals = config.get("decimals", 0)
        aggregate = config.get("aggregate", "sum")

        # Check if this is a ratio calculation or simple path
        is_ratio = "numerator" in config and "denominator" in config
        is_avg = (aggregate == "avg")

        player_scores: list[tuple[str, str, float]] = []

        if is_ratio or is_avg:
            if is_avg:
                num_key = f"custom_{lb_id}_sum"
                denom_key = f"custom_{lb_id}_count"
            else:
                num_key = f"custom_{lb_id}_numerator"
                denom_key = f"custom_{lb_id}_denominator"

            # Custom ratio or average extraction via aggregate fetch
            ratio_stats = self._db.get_top_ratio_stats(
                game_type,
                num_key,
                denom_key
            )
            for player_id, player_name, total_num, total_denom in ratio_stats:
                if total_denom > 0:
                    value = total_num / total_denom
                    player_scores.append((player_id, player_name, value))
            player_scores.sort(key=lambda x: x[2], reverse=True)
            player_scores = player_scores[:10]  # Apply limit for ratio stats
        else:
            # Simple stat
            if aggregate == "max":
                stat_key = f"custom_{lb_id}_high"
            else:
                stat_key = f"custom_{lb_id}"
            player_scores = self._db.get_top_player_game_stats(game_type, stat_key, limit=10)

        # Build menu items
        items = []
        entry_key = f"leaderboard-{format_key}-entry"

        for rank, (player_id, name, value) in enumerate(player_scores, 1):
            display_value = round(value, decimals) if decimals > 0 else int(value)
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        entry_key,
                        rank=rank,
                        player=name,
                        value=display_value,
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    async def _handle_leaderboards_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle leaderboards menu selection."""
        if selection_id.startswith("lb_"):
            game_type = selection_id[3:]  # Remove "lb_" prefix
            self._show_leaderboard_types_menu(user, game_type)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_leaderboard_types_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle leaderboard type selection."""
        game_type = state.get("game_type", "")
        game_name = state.get("game_name", "")

        # Built-in leaderboard types
        if selection_id == "type_wins":
            self._show_wins_leaderboard(user, game_type, game_name)
        elif selection_id == "type_rating":
            self._show_rating_leaderboard(user, game_type, game_name)
        elif selection_id == "type_total_score":
            self._show_total_score_leaderboard(user, game_type, game_name)
        elif selection_id == "type_high_score":
            self._show_high_score_leaderboard(user, game_type, game_name)
        elif selection_id == "type_games_played":
            self._show_games_played_leaderboard(user, game_type, game_name)
        elif selection_id == "back":
            self._show_leaderboards_menu(user)
        elif selection_id.startswith("type_"):
            # Custom leaderboard type - look up config from game class
            lb_id = selection_id[5:]  # Remove "type_" prefix
            game_class = get_game_class(game_type)
            if game_class:
                for config in game_class.get_leaderboard_types():
                    if config["id"] == lb_id:
                        self._show_custom_leaderboard(
                            user, game_type, game_name, config
                        )
                        return

    async def _handle_game_leaderboard_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle game leaderboard menu selection."""
        if selection_id == "back":
            game_type = state.get("game_type", "")
            game_name = state.get("game_name", "")
            self._show_leaderboard_types_menu(user, game_type)
        # Other selections (entries, header) are informational only

    # =========================================================================
    # My Stats menu
    # =========================================================================

    def _show_my_stats_menu(self, user: NetworkUser) -> None:
        """Show game selection menu for personal stats (only games user has played)."""
        categories = GameRegistry.get_by_category()
        items = []

        # Add only games where the user has stats
        for category_key in sorted(categories.keys()):
            for game_class in categories[category_key]:
                game_type = game_class.get_type()
                # Check if user has played this game
                stats = self._db.get_all_player_game_stats(user.uuid, game_type)
                if stats and stats.get("games_played", 0) > 0:
                    game_name = Localization.get(user.locale, game_class.get_name_key())
                    items.append(
                        MenuItem(text=game_name, id=f"stats_{game_type}")
                    )

        if not items:
            user.speak_l("my-stats-no-games")
            self._show_main_menu(user)
            return

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "my_stats_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "my_stats_menu"}

    def _show_my_game_stats(self, user: NetworkUser, game_type: str) -> None:
        """Show personal stats for a specific game."""
        from ..game_utils.stats_helpers import RatingHelper

        game_class = get_game_class(game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            return

        game_name = Localization.get(user.locale, game_class.get_name_key())
        stats = self._db.get_all_player_game_stats(user.uuid, game_type)

        games_played = int(stats.get("games_played", 0))

        if games_played == 0:
            user.speak_l("my-stats-no-data")
            return

        wins = int(stats.get("wins", 0))
        losses = int(stats.get("losses", 0))
        total_score = int(stats.get("total_score", 0))
        high_score = int(stats.get("high_score", 0))

        items = []
        # Basic stats
        winrate = round((wins / games_played * 100) if games_played > 0 else 0)

        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-games-played", value=games_played),
                id="games_played",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-wins", value=wins),
                id="wins",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-losses", value=losses),
                id="losses",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-winrate", value=winrate),
                id="winrate",
            )
        )


        # Score stats (if applicable)
        supported_types = game_class.get_supported_leaderboards()

        if total_score > 0:
            if "total_score" in supported_types:
                items.append(
                    MenuItem(
                        text=Localization.get(user.locale, "my-stats-total-score", value=total_score),
                        id="total_score",
                    )
                )

            if "high_score" in supported_types:
                items.append(
                    MenuItem(
                        text=Localization.get(user.locale, "my-stats-high-score", value=high_score),
                        id="high_score",
                    )
                )


        # Skill rating
        rating_helper = RatingHelper(self._db, game_type)
        rating = rating_helper.get_rating(user.uuid)
        if rating.mu != 25.0 or rating.sigma != 25.0 / 3:  # Non-default rating
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "my-stats-rating",
                        value=round(rating.ordinal),
                        mu=round(rating.mu, 1),
                        sigma=round(rating.sigma, 1),
                    ),
                    id="rating",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "my-stats-no-rating"),
                    id="no_rating",
                )
            )

        # Game-specific stats from custom leaderboard configs
        self._add_custom_stats(user, game_class, stats, items)

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "my_game_stats",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "my_game_stats",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _add_custom_stats(
        self,
        user: NetworkUser,
        game_class,
        stats: dict,
        items: list,
    ) -> None:
        """Add game-specific custom stats from leaderboard configs."""
        for config in game_class.get_leaderboard_types():
            lb_id = config["id"]
            numerator_path = config.get("numerator")
            denominator_path = config.get("denominator")
            aggregate = config.get("aggregate", "sum")
            decimals = config.get("decimals", 0)

            # Check if this is a ratio calculation or simple path
            is_ratio = bool(numerator_path and denominator_path)
            is_avg = (aggregate == "avg")

            final_value = None

            if is_ratio:
                num = stats.get(f"custom_{lb_id}_numerator", 0)
                denom = stats.get(f"custom_{lb_id}_denominator", 0)
                if denom > 0:
                    final_value = num / denom
            elif is_avg:
                sum_val = stats.get(f"custom_{lb_id}_sum", 0)
                count_val = stats.get(f"custom_{lb_id}_count", 0)
                if count_val > 0:
                    final_value = sum_val / count_val
            else:
                if aggregate == "max":
                    final_value = stats.get(f"custom_{lb_id}_high")
                else:
                    final_value = stats.get(f"custom_{lb_id}")

            if final_value is not None:
                # Format the value
                if decimals > 0:
                    formatted_value = f"{final_value:.{decimals}f}"
                else:
                    formatted_value = str(round(final_value))

                # Get localization key
                loc_key = f"my-stats-{lb_id.replace('_', '-')}"
                # Try game-specific key first, fall back to generic
                text = Localization.get(user.locale, loc_key, value=formatted_value)
                if text == loc_key:
                    # Key not found, use leaderboard type name
                    type_key = f"leaderboard-type-{lb_id.replace('_', '-')}"
                    type_name = Localization.get(user.locale, type_key)
                    text = f"{type_name}: {formatted_value}"

                items.append(MenuItem(text=text, id=f"custom_{lb_id}"))

    async def _handle_my_stats_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle my stats game selection."""
        if selection_id == "back":
            self._show_personal_options_menu(user)
        elif selection_id.startswith("stats_"):
            game_type = selection_id[6:]  # Remove "stats_" prefix
            self._show_my_game_stats(user, game_type)

    async def _handle_my_game_stats_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle my game stats menu selection."""
        if selection_id == "back":
            self._show_my_stats_menu(user)
        # Other selections (stats entries) are informational only

    def on_table_destroy(self, table) -> None:
        """Handle table destruction. Called by TableManager."""
        if not table.game:
            return
        # Return all human players to main menu
        for player in table.game.players:
            if not player.is_bot:
                player_user = self._users.get(player.name)
                if player_user:
                    self._show_main_menu(player_user)

    def on_game_result(self, result) -> None:
        """Handle game result persistence. Called by Table when a game finishes."""
        from ..game_utils.game_result import GameResult

        if not isinstance(result, GameResult):
            return

        # Save to database
        self._db.save_game_result(
            game_type=result.game_type,
            timestamp=result.timestamp,
            duration_ticks=result.duration_ticks,
            players=[
                (p.player_id, p.player_name, p.is_bot)
                for p in result.player_results
            ],
            custom_data=result.custom_data,
        )

    def on_table_save(self, table, username: str) -> None:
        """Handle table save request. Called by TableManager."""
        import json
        from datetime import datetime

        game = table.game
        if not game:
            return

        # Generate save name
        user_record = self._db.get_user(username)
        locale = user_record.locale if user_record else "en"
        
        game_name_key = f"game-name-{table.game_type}"
        game_name = Localization.get(locale, game_name_key)
        # Fallback if key missing (though it shouldn't be)
        if game_name == game_name_key:
             game_name = game.get_name()

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_name = Localization.get(locale, "default-save-name", game=game_name, date=date_str)

        # Get game JSON
        game_json = game.to_json()

        # Build members list (includes bot status)
        members_data = []
        for player in game.players:
            members_data.append(
                {
                    "username": player.name,
                    "is_bot": player.is_bot,
                }
            )
        members_json = json.dumps(members_data)

        # Save to database
        self._db.save_user_table(
            username=username,
            save_name=save_name,
            game_type=table.game_type,
            game_json=game_json,
            members_json=members_json,
        )

        # Broadcast save message and destroy the table
        game.broadcast_l("table-saved-destroying")
        game.destroy()

    async def _handle_keybind(self, client: ClientConnection, packet: dict) -> None:
        """Handle keybind press."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        table = self._tables.find_user_table(username)
        if table and table.game and user:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user)

    async def _handle_editbox(self, client: ClientConnection, packet: dict) -> None:
        """Handle editbox submission."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        
        # Check if user is in a game
        table = self._tables.find_user_table(username)
        if table and table.game and user:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user)
            return

        # Not in a game, check if there's a system menu input handler
        if user:
            user_state = self._user_states.get(username, {})
            # Try admin handler
            if await self.admin_manager.handle_input(user, packet, user_state):
                return
            
            # Try options handler
            if await self._handle_options_input(user, packet, user_state):
               return

            # Profile inputs
            menu_id = user_state.get("menu")
            value = packet.get("text", packet.get("value", ""))

            if menu_id == "email_input":
                value = value.strip()
                user_record = self._db.get_user(user.username)
                current_email = user_record.email if user_record else ""
                from_mandatory = user_state.get("from_mandatory", False)

                if not value:
                    user.speak_l("error-email-empty")
                    if from_mandatory:
                        self._show_mandatory_email_menu(user)
                    else:
                        self._show_profile_menu(user)
                    return

                if value == current_email:
                    user.speak_l("no-changes-made")
                    if from_mandatory:
                         # Should not hit this since mandatory means current was empty and value is empty, which is caught above
                         self._show_mandatory_email_menu(user)
                    else:
                         self._show_profile_menu(user)
                    return

                if self._db.email_exists(value, exclude_username=user.username):
                    user.speak_l("error-email-taken")
                    if from_mandatory:
                        self._show_mandatory_email_menu(user)
                    else:
                        self._show_profile_menu(user)
                    return

                if not current_email:
                    self._db.update_user_email(user.username, value)
                    user.speak_l("email-updated")
                    if from_mandatory:
                        self._restore_user_state(user, user.username)
                    else:
                        self._show_profile_menu(user)
                else:
                    self._show_email_confirm_menu(user, value)
                return
            elif menu_id == "bio_input":
                if len(value) > 250:
                    user.speak_l("error-bio-length")
                    self._show_profile_menu(user)
                    return

                user_record = self._db.get_user(user.username)
                current_bio = user_record.bio if user_record else ""

                if value == current_bio:
                    user.speak_l("no-changes-made")
                else:
                    self._db.update_user_bio(user.username, value)
                    user.speak_l("bio-updated")
                self._show_profile_menu(user)
                return

            elif menu_id == "send_friend_request_input":
                value = value.strip()
                if not value:
                     self._show_friends_hub_menu(user)
                     return

                if value.lower() == user.username.lower():
                     user.speak_l("friend-error-self")
                     self._show_friends_hub_menu(user)
                     return

                target_record = self._db.get_user(value)
                if not target_record:
                     user.speak_l("unknown-player")
                     self._show_friends_hub_menu(user)
                     return

                # Send request
                status = self._db.send_friend_request(user.uuid, target_record.uuid)

                if status == "already_friends":
                     user.speak_l("friend-error-already-friends")
                elif status == "duplicate":
                     user.speak_l("friend-error-duplicate")
                elif status == "accepted":
                     user.speak_l("friend-accepted-success", username=target_record.username)
                     user.play_sound("friend_accepted.ogg")
                     # Notify target if online
                     target_user = self._users.get(target_record.username)
                     if target_user:
                         target_user.speak_l("friend-accepted-notify", username=user.username)
                         target_user.play_sound("friend_accepted.ogg")
                     else:
                         self._db.add_notification(target_record.uuid, user.username, "friend_accepted")
                     self.on_friend_requests_changed(target_record.uuid)
                elif status == "sent":
                     user.speak_l("friend-request-sent", username=target_record.username)
                     user.play_sound("friend_request_sent.ogg")
                     # Notify target if online
                     target_user = self._users.get(target_record.username)
                     if target_user:
                         target_user.speak_l("friend-request-received", username=user.username)
                         target_user.play_sound("friend_request_received.ogg")
                     else:
                         self._db.add_notification(target_record.uuid, user.username, "friend_request_received")
                     self.on_friend_requests_changed(target_record.uuid)

                self._show_friends_hub_menu(user)
                return

            elif menu_id == "send_pm_input":
                target_username = user_state.get("target_username")
                value = value.strip()
                if value and target_username:
                    await self._deliver_private_message(user, target_username, value)

                # Return to friend actions menu regardless
                if target_username:
                    self._show_friend_actions_menu(user, target_username)
                else:
                    self._show_friends_list_menu(user)
                return

    async def _deliver_private_message(self, sender: NetworkUser, target_username: str, message: str) -> None:
        """Deliver a private message after validating friendship and online status."""
        target_user = self._users.get(target_username)

        # 1. Online Check
        if not target_user or not target_user.approved:
            sender.speak_l("pm-error-offline", username=target_username)
            sender.play_sound("accounterror.ogg")
            return

        # 2. Friend Check
        friend_uuids = self._db.get_friends(sender.uuid)
        if target_user.uuid not in friend_uuids:
            sender.speak_l("pm-error-not-friends")
            sender.play_sound("accounterror.ogg")
            return

        # 3. Delivery
        # Receiver
        target_user.speak_l("pm-received", buffer="chat", username=sender.username, message=message)
        target_user.play_sound("pm.ogg")

        # Sender FTL confirmation
        sender.speak_l("pm-sent-success", username=target_username)
        sender.play_sound("pm.ogg")


    async def _handle_chat(self, client: ClientConnection, packet: dict) -> None:
        """Handle chat message."""
        username = client.username
        if not username:
            return

        convo = packet.get("convo", "local")
        message = packet.get("message", "")

        # Handle Private Message chat command
        if message.startswith("@"):
            parts = message.split(" ", 1)
            if len(parts) == 2:
                target_username = parts[0][1:] # Strip the @
                pm_content = parts[1].strip()
                if not pm_content:
                    # Stop empty chat messages from accidentally falling back into global chat
                    return
                user = self._users.get(username)
                if user:
                    await self._deliver_private_message(user, target_username, pm_content)
                return

        if message.startswith("/reboot") or message.startswith("/stop"):
            # Check permissions
            user = self._users.get(username)
            if user and user.trust_level >= 3:
                is_reboot = message.startswith("/reboot")
                action_text = "restarting" if is_reboot else "shutting down"
                
                import os
                
                # Broadcast warning messages localized for each user
                for u in self._users.values():
                    if u.approved:
                         sys_name = Localization.get(u.locale, "system-name")
                         msg = Localization.get(u.locale, f"server-{action_text}", seconds=3)
                         full_msg = f"{sys_name}: {msg}"
                         
                         asyncio.create_task(u.connection.send({
                             "type": "chat",
                             "convo": "announcement",
                             "sender": sys_name,
                             "message": msg, # Client will format it if needed, or we send formatted
                         }))
                
                # Schedule exit
                async def delayed_exit():
                    await asyncio.sleep(3)
                    await self.stop()
                    # Use os._exit to avoid SystemExit exception being caught by asyncio handler
                    # Exit code 1 to ensure systemd restarts it
                    os._exit(1) 
                
                asyncio.create_task(delayed_exit())
                return
                
                asyncio.create_task(delayed_exit())
                return
            else:
                 # Fake command not found for non-admins to avoid revealing existence
                 pass

        elif message.startswith("/kick"):
             # Kick command
             # Format: /kick <username>
             user = self._users.get(username)
             if user and user.trust_level >= 2:
                 parts = message.split(" ", 1)
                 if len(parts) < 2:
                     user.speak_l("usage-kick") # Need to add this key or just speak generic
                     # Or just ignore if empty
                     return
                 
                 target_name = parts[1].strip()
                 await self.admin_manager.kick_user(user, target_name, show_menu=False)
                 return
             else:
                 pass # Ignore for non-admins

        chat_packet = {
            "type": "chat",
            "convo": convo,
            "sender": username,
            "message": message,
            "buffer": "chat",
            # "language": language,
        }

        if convo == "local":
            table = self._tables.find_user_table(username)
            if table:
                for member_name in [m.username for m in table.members]:
                    user = self._users.get(member_name)
                    if user and user.approved:  # Only send to approved users
                        await user.connection.send(chat_packet)
            else:
                # Lobby chat: send to all users who are NOT in a table
                for user in self._users.values():
                    if user.approved:
                        # Check if this user is in a table
                        user_table = self._tables.find_user_table(user.username)
                        if not user_table:
                            await user.connection.send(chat_packet)
        elif convo == "global":
            # Broadcast to all approved users only
            for user in self._users.values():
                if user.approved:
                    await user.connection.send(chat_packet)

    def _get_user_role_and_client_text(self, locale: str, user: NetworkUser) -> tuple[str, str]:
        """Get localized role and client type text for a user."""
        # Role
        if user.trust_level >= 3:
            role_key = "user-role-dev"
        elif user.trust_level >= 2:
            role_key = "user-role-admin"
        else:
            role_key = "user-role-user"
        role_text = Localization.get(locale, role_key)

        # Client
        client_type = user.client_type or "python"
        client_key = f"client-type-{client_type.lower()}"
        client_text = Localization.get(locale, client_key)
        # Fallback if key missing
        if client_text == client_key:
             client_text = client_type.capitalize()
        
        return role_text, client_text

    def _get_online_usernames(self) -> list[str]:
        """Return sorted list of online usernames. Excludes banned users."""
        online_users = []
        for username in self._users.keys():
            # Hide banned users from the public online list
            state = self._user_states.get(username, {})
            if state.get("menu") != "banned_menu":
                online_users.append(username)
        return sorted(online_users, key=str.lower)

    def _format_online_users_lines(self, user: NetworkUser) -> list[tuple[str, str]]:
        """Format online users with game names for menu display. Returns tuples of (username, display_text)."""
        lines: list[tuple[str, str]] = []
        for username in self._get_online_usernames():
            online_user = self._users.get(username)
            if not online_user:
                continue

            # Get Role and Client
            role_text, client_text = self._get_user_role_and_client_text(
                user.locale, online_user
            )

            # Check if user is waiting for approval
            if not online_user.approved:
                status = Localization.get(user.locale, "online-user-waiting-approval")
            else:
                table = self._tables.find_user_table(username)
                if table:
                    game_class = get_game_class(table.game_type)
                    status = (
                        Localization.get(user.locale, game_class.get_name_key())
                        if game_class
                        else table.game_type
                    )
                else:
                    status = Localization.get(user.locale, "online-user-not-in-game")
            
            # Use the full entry format: {username} ({role}, {client}): {status}
            line = Localization.get(
                user.locale,
                "online-user-full-entry",
                username=username,
                role=role_text,
                client=client_text,
                status=status,
            )
            lines.append((username, line))

        if not lines:
            lines.append(("", Localization.get(user.locale, "online-users-none")))
        return lines

    def _get_online_users_menu_items(self, user: NetworkUser) -> list[MenuItem]:
        """Generate the list of MenuItems for the interactive online users list."""
        items = [MenuItem(text=Localization.get(user.locale, "close-menu"), id="back")]

        for username, line in self._format_online_users_lines(user):
            if not username:
                # E.g. "No users online"
                items.append(MenuItem(text=line, id=""))
            elif username == user.username:
                # Do not allow opening an action menu for oneself
                items.append(MenuItem(text=line, id=""))
            else:
                items.append(MenuItem(text=line, id=f"online_{username}"))

        return items

    def _show_online_users_menu(self, user: NetworkUser) -> None:
        """Show interactive online users menu."""
        current_state = self._user_states.get(user.username, {})
        previous_menu_id = current_state.get("menu")
        previous_menu = None
        if previous_menu_id:
            current_menus = getattr(user, "_current_menus", {})
            previous_menu = current_menus.get(previous_menu_id)

        items = self._get_online_users_menu_items(user)

        user.show_menu(
            "online_users",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_FIRST, # Back is at index 0
            position=1, # Default focus to first user, not the 'Back' button
        )
        self._user_states[user.username] = {
            "menu": "online_users",
            "return_menu_id": previous_menu_id,
            "return_menu": previous_menu,
            "return_state": dict(current_state),
        }

    async def _handle_online_users_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle selection from the interactive online users list."""
        if selection_id == "back":
            self._restore_previous_menu(user, state)
        elif selection_id.startswith("online_"):
            target_username = selection_id[7:]
            self._show_online_user_actions_menu(user, target_username, state)

    def _show_online_user_actions_menu(self, user: NetworkUser, target_username: str, previous_state: dict) -> None:
        """Show context menu for an online user."""
        target_user = self._users.get(target_username)
        if not target_user:
            user.speak_l("user-not-online-anymore")
            # Restart the menu process to clean state
            self._show_online_users_menu(user)
            return

        title = Localization.get(user.locale, "online-user-actions-title", username=target_username)
        items = [
            MenuItem(text=title, id=""),
            MenuItem(text=Localization.get(user.locale, "view-profile"), id="view_profile"),
        ]

        # Add "Send Friend Request" if not already friends and not pending
        friend_uuids = self._db.get_friends(user.uuid)
        pending_uuids = self._db.get_pending_incoming_requests(user.uuid)
        # Check if we sent one to them too
        # To be safe, just use the helper which handles "duplicate" cleanly, but for UI:
        if target_user.uuid not in friend_uuids and target_user.uuid not in pending_uuids:
             items.append(MenuItem(text=Localization.get(user.locale, "friends-send-request"), id="send_friend_request"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "online_user_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )

        # Preserve the deep return state needed to eventually close the online list
        self._user_states[user.username] = {
            "menu": "online_user_actions_menu",
            "target_username": target_username,
            "return_menu_id": previous_state.get("return_menu_id"),
            "return_menu": previous_state.get("return_menu"),
            "return_state": previous_state.get("return_state"),
        }


    async def _handle_online_user_actions_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        """Handle selection in the online user actions menu."""
        target_username = state.get("target_username")

        if selection_id == "back":
            # Reconstruct the deep state to pass back to the online list so it knows how to close later
            user_state = dict(state)
            user_state["menu"] = "online_users"
            self._user_states[user.username] = user_state

            items = self._get_online_users_menu_items(user)
            user.show_menu(
                "online_users",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_FIRST,
                position=1,
            )
            return

        target_user = self._users.get(target_username)
        if not target_user:
            user.speak_l("user-not-online-anymore")
            self._show_online_users_menu(user)
            return

        if selection_id == "view_profile":
            self._show_public_profile(user, target_username, "online_user_actions_menu")

        elif selection_id == "send_friend_request":
            status = self._db.send_friend_request(user.uuid, target_user.uuid)

            if status == "already_friends":
                 user.speak_l("friend-error-already-friends")
            elif status == "duplicate":
                 user.speak_l("friend-error-duplicate")
            elif status == "accepted":
                 user.speak_l("friend-accepted-success", username=target_user.username)
                 user.play_sound("friend_accepted.ogg")
                 # Notify target if online
                 target_user.speak_l("friend-accepted-notify", username=user.username)
                 target_user.play_sound("friend_accepted.ogg")
                 self.on_friend_requests_changed(target_user.uuid)
            elif status == "sent":
                 user.speak_l("friend-request-sent", username=target_user.username)
                 user.play_sound("friend_request_sent.ogg")
                 # Notify target if online
                 target_user.speak_l("friend-request-received", username=user.username)
                 target_user.play_sound("friend_request_received.ogg")
                 self.on_friend_requests_changed(target_user.uuid)

            # Refresh the actions menu so the button disappears
            self._show_online_user_actions_menu(user, target_username, state)

    def _restore_previous_menu(self, user: NetworkUser, state: dict) -> None:
        """Restore the previous menu after closing the online users list."""
        previous_menu_id = state.get("return_menu_id")
        previous_menu = state.get("return_menu")
        if not previous_menu_id or not previous_menu:
            self._show_main_menu(user)
            return

        user.show_menu(
            previous_menu_id,
            previous_menu.get("items", []),
            multiletter=previous_menu.get("multiletter_enabled", True),
            escape_behavior=EscapeBehavior(previous_menu.get("escape_behavior", "keybind")),
            position=previous_menu.get("position"),
            grid_enabled=previous_menu.get("grid_enabled", False),
            grid_width=previous_menu.get("grid_width", 1),
        )
        restored_state = dict(state.get("return_state", {}))
        restored_state["menu"] = previous_menu_id
        self._user_states[user.username] = restored_state

    async def _handle_list_online(self, client: ClientConnection) -> None:
        """Handle request for online users list."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        online = self._get_online_usernames()
        count = len(online)
        if count == 0:
            user.speak_l("online-users-none")
            return
        
        users_str = Localization.format_list_and(user.locale, online)
        if count == 1:
            user.speak_l("online-users-one", users=users_str)
        else:
            user.speak_l("online-users-many", count=count, users=users_str)

    async def _handle_list_online_with_games(self, client: ClientConnection) -> None:
        """Handle request for online users list with game info."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        table = self._tables.find_user_table(username)
        if table and table.game:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                # Strip the username tuples back down to just strings for the read-only status box
                string_lines = [line for _, line in self._format_online_users_lines(user)]
                table.game.status_box(player, string_lines)
                return

        self._show_online_users_menu(user)

    async def _handle_ping(self, client: ClientConnection) -> None:
        """Handle ping request - respond immediately with pong."""
        await client.send({"type": "pong"})

    async def _handle_broadcast_cmd(self, client: ClientConnection, packet: dict) -> None:
        """Handle broadcast slash command."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        # Check permissions - only trust level 2 (admin) can broadcast
        if not user or user.trust_level < 2:
            return

        message = packet.get("message", "")
        if message:
            await self.admin_manager.perform_broadcast(user, message, show_menu=False)


async def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    ssl_cert: str | Path | None = None,
    ssl_key: str | Path | None = None,
) -> None:
    """Run the server.

    Args:
        host: Host address to bind to
        port: Port number to listen on
        ssl_cert: Path to SSL certificate file (for WSS support)
        ssl_key: Path to SSL private key file (for WSS support)
    """
    logging.basicConfig(
        filename="errors.log",
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    def _log_uncaught(exc_type, exc, tb):
        if exc_type in (KeyboardInterrupt, asyncio.CancelledError):
            return
        logging.getLogger("playaural").exception(
            "Uncaught exception", exc_info=(exc_type, exc, tb)
        )

    sys.excepthook = _log_uncaught
    loop = asyncio.get_running_loop()

    def _asyncio_exception_handler(loop, context):
        exc = context.get("exception")
        if isinstance(exc, asyncio.CancelledError):
            return
        if exc:
            logging.getLogger("playaural").exception(
                "Asyncio exception", exc_info=exc
            )
        else:
            logging.getLogger("playaural").error(
                "Asyncio error: %s", context.get("message")
            )

    loop.set_exception_handler(_asyncio_exception_handler)

    server = Server(host=host, port=port, ssl_cert=ssl_cert, ssl_key=ssl_key)
    await server.start()

    try:
        # Run forever
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()
