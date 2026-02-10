"""Table management for games."""

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

    # Not serialized
    _game: "Game | None" = field(default=None, repr=False)
    _users: dict[str, "User"] = field(default_factory=dict, repr=False)
    _manager: Any = field(default=None, repr=False)  # Reference to TableManager
    _server: Any = field(default=None, repr=False)  # Reference to Server (for saves)
    _db: Any = field(default=None, repr=False)  # Reference to Database (for ratings)

    def __post_init__(self):
        self._game = None
        self._users = {}
        self._manager = None
        self._server = None
        self._db = None

    @property
    def game(self) -> "Game | None":
        return self._game

    @game.setter
    def game(self, value: "Game | None") -> None:
        self._game = value
        if value:
            self.game_json = value.to_json()

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

    def remove_member(self, username: str) -> None:
        """Remove a member from the table."""
        self.members = [m for m in self.members if m.username != username]
        self._users.pop(username, None)
        
        if self.status == "waiting" and username == self.host:
            # Host left/kicked in lobby -> promote new host
            # Filter for humans (not bots). Note: Removed user is already gone from self.members
            candidates = [m for m in self.members if not m.is_spectator and not (self._users.get(m.username) and getattr(self._users.get(m.username), "is_bot", False))]
            
            if candidates:
                # Prioritize ONLINE humans
                candidates.sort(key=lambda m: m.username in self._server._users if self._server else False, reverse=True)
                
                new_host = candidates[0].username
                self.host = new_host
                # Broadcast via game if possible
                if self._game:
                    self._game.broadcast_l("new-host", player=new_host)
                    self._game.host = new_host
                    if hasattr(self._game, "rebuild_all_menus"):
                        self._game.rebuild_all_menus()

        # Auto-destroy if no members left (e.g. all humans left)
        if not self.members:
            self.destroy()

    def get_user(self, username: str) -> "User | None":
        """Get a user by username."""
        return self._users.get(username)

    def attach_user(self, username: str, user: "User") -> None:
        """Attach a user to a member (e.g., after deserialization)."""
        self._users[username] = user

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

            import time
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
                    # We iterate a copy to allow modification during iteration if we were removing immediately,
                    # but here we just mark them. Removal happens after timeout.
                    
                    # Initialize tracker if needed
                    if not hasattr(self, "_member_offline_since"):
                        self._member_offline_since = {}

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
                                self._game.broadcast_l("player-kicked-offline", player=member.username)
                                
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

                            self.remove_member(member.username)
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
                    if not hasattr(self, "_offline_since") or self._offline_since is None:
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
        if getattr(self, "_destroyed", False):
            return
        self._destroyed = True

        # Ensure Game is also destroyed (e.g. if table is destroyed by timeout)
        # We need to avoid infinite recursion since Game.destroy calls Table.destroy
        if self._game and hasattr(self._game, "destroy") and not getattr(self._game, "_destroyed", False):
             self._game.destroy()

        if self._manager:
            self._manager.on_table_destroy(self)

    def save_and_close(self, username: str) -> None:
        """Save game state and close table. Called by game save action."""
        if self._server:
            self._server.on_table_save(self, username)

    def save_game_result(self, result: Any) -> None:
        """Save a game result to the database. Called by game when it finishes."""
        if self._server:
            self._server.on_game_result(result)
