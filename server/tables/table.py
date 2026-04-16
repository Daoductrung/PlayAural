"""Table management for games."""

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mashumaro.mixins.json import DataClassJSONMixin

if TYPE_CHECKING:
    from ..games.base import Game
    from ..users.base import User


@dataclass
class TableMember:
    """A member of a table (player or spectator)."""

    username: str
    is_spectator: bool = False


@dataclass
class Table(DataClassJSONMixin):
    """
    A game table that holds members and a game instance.

    Tables track who is present and forward actions to the game.
    Role management is handled by games, not tables.
    """

    table_id: str
    game_type: str
    host: str
    members: list[TableMember] = field(default_factory=list)
    game_json: str | None = None  # Serialized game state
    status: str = "waiting"  # waiting, playing, finished
    is_private: bool = False  # Private tables are hidden from active tables lists

    # Not serialized
    _game: "Game | None" = field(default=None, repr=False)
    _users: dict[str, "User"] = field(default_factory=dict, repr=False)
    _manager: Any = field(default=None, repr=False)  # Reference to TableManager
    _server: Any = field(default=None, repr=False)  # Reference to Server (for saves)
    _db: Any = field(default=None, repr=False)  # Reference to Database (for ratings)
    _last_menu_state_hash: str | None = field(default=None, repr=False)
    _member_offline_since: dict = field(default_factory=dict, repr=False)
    _offline_since: float | None = field(default=None, repr=False)
    _destroyed: bool = field(default=False, repr=False)

    def __post_init__(self):
        self._game = None
        self._users = {}
        self._manager = None
        self._server = None
        self._db = None
        self._last_menu_state_hash = None
        self._member_offline_since = {}
        self._offline_since = None
        self._destroyed = False
        # Table-scoped ban list — runtime only, never serialized.
        # Keyed by player UUID. Dies with this Table instance, so no ban can
        # carry over even if a future table reuses the same table_id.
        self._banned_uuids: set[str] = set()

    @property
    def game(self) -> "Game | None":
        return self._game

    @game.setter
    def game(self, value: "Game | None") -> None:
        self._game = value
        if value:
            self.game_json = value.to_json()
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()

    def add_member(
        self, username: str, user: "User", as_spectator: bool = False
    ) -> None:
        """Add a member to the table."""
        # Check if already a member
        for member in self.members:
            if member.username == username:
                return

        self.members.append(TableMember(username=username, is_spectator=as_spectator))
        self._users[username] = user
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table[username] = self.table_id
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()

    def remove_member(
        self,
        username: str,
        *,
        voice_reason: str = "voice-status-left-table",
    ) -> None:
        """Remove a member from the table."""
        self.members = [m for m in self.members if m.username != username]
        self._users.pop(username, None)
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table.pop(username, None)
        if self._server and hasattr(self._server, "on_table_member_removed"):
            self._server.on_table_member_removed(
                self,
                username,
                voice_reason=voice_reason,
            )

        if self.status == "waiting" and username == self.host:
            # Host left/kicked in lobby -> promote new host
            # Filter for non-spectator humans. Note: Removed user is already gone from self.members
            candidates = [m for m in self.members if not m.is_spectator and not (self._users.get(m.username) and getattr(self._users.get(m.username), "is_bot", False))]

            if candidates:
                # Prioritize ONLINE humans
                candidates.sort(key=lambda m: m.username in self._server._users if self._server else False, reverse=True)

                new_host = candidates[0].username
                self.host = new_host
                # Broadcast via game if possible
                if self._game:
                    self._game.broadcast_l("new-host", buffer="system", player=new_host)
                    self._game.host = new_host
                    if hasattr(self._game, "rebuild_all_menus"):
                        self._game.rebuild_all_menus()
            else:
                # No non-spectator human can take over as host: destroy the table.
                # This handles the case where only spectators remain after the host leaves
                # (e.g. host is the only player and others joined as spectators, or the
                # host toggled to spectator and all remaining members are spectators).
                self.destroy()
                return

        # Auto-destroy if no members left (e.g. all humans left)
        if not self.members:
            self.destroy()

    def is_banned(self, user_uuid: str) -> bool:
        """Check if a UUID is banned from this table instance."""
        return user_uuid in self._banned_uuids

    def ban_user(self, user_uuid: str) -> None:
        """Add a UUID to the table-scoped ban list."""
        self._banned_uuids.add(user_uuid)

    def get_user(self, username: str) -> "User | None":
        """Get a user by username."""
        return self._users.get(username)

    def attach_user(self, username: str, user: "User") -> None:
        """Attach a user to a member (e.g., after deserialization)."""
        self._users[username] = user
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table[username] = self.table_id

    def get_players(self) -> list[TableMember]:
        """Get all non-spectator members."""
        return [m for m in self.members if not m.is_spectator]

    def get_spectators(self) -> list[TableMember]:
        """Get all spectator members."""
        return [m for m in self.members if m.is_spectator]

    @property
    def player_count(self) -> int:
        """Get the number of players (non-spectators)."""
        return len(self.get_players())

    def broadcast(self, text: str, buffer: str = "game") -> None:
        """Send a message to all members."""
        for username, user in self._users.items():
            user.speak(text, buffer)

    def broadcast_sound(self, name: str, volume: int = 100) -> None:
        """Play a sound for all members."""
        for user in self._users.values():
            user.play_sound(name, volume)

    def on_tick(self) -> None:
        """Called every tick. Forwards to game."""
        if self._game:
            self._game.on_tick()

            # Check if state changed for menu auto-refresh
            current_state_hash = f"{self._game.status}|{len(self.members)}|{self.host}"
            if self._last_menu_state_hash is None:
                self._last_menu_state_hash = current_state_hash
            elif self._last_menu_state_hash != current_state_hash:
                self._last_menu_state_hash = current_state_hash
                if self._server and hasattr(self._server, "on_tables_changed"):
                    self._server.on_tables_changed()

        # Timeout for abandoned tables
        if self._server:
            # Check host presence
            host_online = self.host in self._server._users
            
            # Check if any human is present
            any_human_present = False
            if self._game:
                for p in self._game.players:
                    if not p.is_bot:
                        user = self._game.get_user(p)
                        if user and user.username in self._server._users:
                            any_human_present = True
                            break
            # Fallback for lobby if game not started (members check)
            else:
                for m in self.members:
                    if not m.is_spectator and m.username in self._server._users:
                        any_human_present = True
                        break

            current_time = time.time()
            
            should_destroy = False
            
            if self.status == "waiting":
                # Waiting: 
                # 1. If host offline and no other humans -> Destroy immediately
                if not host_online and not any_human_present:
                    should_destroy = True
                
                # 2. Check individual members for offline timeout (Auto-kick)
                # This prevents "zombie members" in the lobby
                if not should_destroy:
                    for member in list(self.members): # Copy for safe iteration
                        # Skip bots (they are always "offline" in server._users but valid in game)
                        # Optimization: Check if username in server._users first (Fast path)
                        if member.username in self._server._users:
                            self._member_offline_since.pop(member.username, None)
                            continue

                        # If not in server._users, check if it's a Bot instance
                        user = self._users.get(member.username)
                        if user and hasattr(user, "is_bot") and user.is_bot:
                            continue # Bots are fine
                        
                        # It's a human and they are offline
                        if member.username not in self._member_offline_since:
                            self._member_offline_since[member.username] = current_time
                        
                        # Check timeout (15 seconds grace period for lobby)
                        elif current_time - self._member_offline_since[member.username] > 15.0:
                            # Kick them
                            if self._game:
                                self._game.broadcast_l("player-kicked-offline", buffer="system", player=member.username)
                                
                                # Clean up Game state to prevent ghost players
                                # We need the UUID to call game methods
                                user_record = self._users.get(member.username)
                                if user_record:
                                    if member.is_spectator:
                                        self._game.remove_spectator(user_record.uuid)
                                    elif self.status == "waiting":
                                        # In lobby, just remove the player
                                        self._game.remove_player(user_record.uuid)
                                    elif self.status == "playing":
                                        # In game, treat as disconnect (bot replacement)
                                        self._game.on_player_disconnect(user_record.uuid)

                            self.remove_member(
                                member.username,
                                voice_reason="voice-status-connection-lost",
                            )
                            # Remove from tracker
                            self._member_offline_since.pop(member.username, None)
            
            elif self.status == "playing":
                # Playing: 
                # - If humans present: Keep alive forever (reset timer)
                # - If NO humans present (e.g. host vs bot, host offline): 5 min timeout
                if any_human_present:
                    self._offline_since = None
                else:
                    # No humans left - start/check timer
                    if self._offline_since is None:
                        self._offline_since = current_time
                    elif current_time - self._offline_since > 300:  # 5 minutes
                        should_destroy = True

            if should_destroy:
                self.destroy()
            elif any_human_present:
                # Reset timer if humans are back
                self._offline_since = None

    def handle_event(self, username: str, event: dict) -> None:
        """Handle an event from a member."""
        if self._game:
            # Find the player
            for player in self._game.players:
                if player.name == username:
                    self._game.handle_event(player, event)
                    break

    def save_game_state(self) -> None:
        """Save the current game state to game_json."""
        if self._game:
            self.game_json = self._game.to_json()

    def can_start(self, min_players: int) -> bool:
        """Check if the game can start."""
        return self.player_count >= min_players

    def destroy(self) -> None:
        """Destroy this table. Called by Game.destroy()."""
        if self._destroyed:
            return
        self._destroyed = True

        # Ensure Game is also destroyed (e.g. if table is destroyed by timeout)
        # We need to avoid infinite recursion since Game.destroy calls Table.destroy
        if self._game and hasattr(self._game, "destroy") and not getattr(self._game, "_destroyed", False):
             self._game.destroy()

        if self._manager:
            self._manager.on_table_destroy(self)

    def reset_game(self) -> None:
        """Reset the table to the lobby state with a completely fresh Game instance."""
        if not self._game:
            return

        from ..games.registry import get_game_class
        game_class = get_game_class(self.game_type)
        if not game_class:
            return

        # 1. Store old game state we need
        old_game = self._game
        old_options = None
        if hasattr(old_game, "options"):
            old_options = old_game.options

        # 2. Clean up stale members
        # If a player disconnected during the end-game sequence, they might still be in self.members
        # but not in self._users. We must remove them now to prevent ghost players.
        # We also check the server's master user list to ensure they are actually online.
        valid_members = []
        for member in self.members:
            user = self._users.get(member.username)
            if user:
                # Bots are always "online" for the game's purposes, though they aren't in server._users
                is_bot = getattr(user, "is_bot", False)
                # Humans must be actively connected to the server
                if is_bot or (self._server and member.username in self._server._users):
                    valid_members.append(member)
        self.members = valid_members

        # 3. Track humans, bots, and spectators
        active_players = []
        active_spectators = []
        active_bots = []

        # Table.members is the SINGLE SOURCE OF TRUTH for humans and their roles
        for member in self.members:
            user = self._users.get(member.username)
            if not user:
                continue # Safety check, though we just cleaned up

            if member.is_spectator:
                active_spectators.append((user.uuid, member.username, user))
            else:
                active_players.append((user.uuid, member.username, user))

        # old_game.players is the ONLY source for bots
        for player in old_game.players:
            if player.is_bot:
                user = old_game._users.get(player.id)
                if user:
                    active_bots.append((player.id, player.name, user))

        # 4. Re-evaluate host
        # If the old host left, they won't be in active_players or active_spectators
        old_host = self.host
        host_present = any(name == self.host for _, name, _ in active_players) or \
                       any(name == self.host for _, name, _ in active_spectators)

        if not host_present:
            # Promote a new host. Prioritize players over spectators.
            candidates = [p for p in active_players]
            if not candidates:
                candidates = [s for s in active_spectators]

            if candidates:
                # Prioritize online humans (though valid_members cleanup should ensure this)
                if self._server:
                    candidates.sort(key=lambda p: p[1] in self._server._users, reverse=True)
                self.host = candidates[0][1]
            else:
                # No humans left at all
                self.destroy()
                return

        # 5. Instantiate fresh game
        new_game = game_class()

        # 6. Safe Option Cloning
        if old_options and hasattr(new_game, "options"):
            # Serialize old options to dict and rebuild to avoid deepcopy issues with dataclasses
            options_dict = old_options.to_dict()
            new_game.options = type(new_game.options).from_dict(options_dict)

        # 7. Link table
        new_game._table = self
        self._game = new_game

        # 8. Initialize lobby state
        new_game.host = self.host
        new_game.status = "waiting"
        new_game.setup_keybinds()

        def _restore_member(uuid_str: str, name: str, user: "User", *, is_spectator: bool) -> None:
            """Reattach an existing table member without replaying join side effects."""
            restored_player = new_game.create_player(uuid_str, name, is_bot=False)
            restored_player.is_spectator = is_spectator
            new_game.players.append(restored_player)
            new_game.attach_user(restored_player.id, user)
            new_game.setup_player_actions(restored_player)

        # 9. Add players back
        for uuid_str, name, user in active_players:
             _restore_member(uuid_str, name, user, is_spectator=False)

        for uuid_str, name, user in active_spectators:
             _restore_member(uuid_str, name, user, is_spectator=True)

        for uuid_str, name, user in active_bots:
             # Use the raw create_player/append logic for bots to perfectly match LobbyActionsMixin
             bot_player = new_game.create_player(uuid_str, name, is_bot=True)
             new_game.players.append(bot_player)
             new_game.attach_user(bot_player.id, user)
             new_game.setup_player_actions(bot_player)

        # 10. Announce new host if changed
        if old_host != self.host:
             new_game.broadcast_l("table-new-host-promoted", buffer="system", player=self.host)

        # 11. Transfer scheduled sounds and sound scheduler tick from old game
        new_game.scheduled_sounds = list(old_game.scheduled_sounds)
        new_game.sound_scheduler_tick = old_game.sound_scheduler_tick

        # 12. Play waiting lobby music
        new_game.play_music("findgamemus.ogg")

        # 13. Mark old game as destroyed so ticks stop affecting it
        old_game._destroyed = True

        # 14. Sync status
        self.status = "waiting"

    def save_and_close(self, username: str) -> None:
        """Save game state and close table. Called by game save action."""
        if self._server:
            self._server.on_table_save(self, username)

    def save_game_result(self, result: Any) -> None:
        """Save a game result to the database. Called by game when it finishes."""
        if self._server:
            self._server.on_game_result(result)
