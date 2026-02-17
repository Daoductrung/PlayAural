"""Base game class and player dataclass."""

from dataclasses import dataclass, field
from typing import Any
from abc import ABC, abstractmethod
import threading

from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.config import BaseConfig

from ..users.base import User
from ..game_utils.actions import ActionSet
from ..game_utils.options import (
    GameOptions as DeclarativeGameOptions,
    OptionsHandlerMixin,
)
from ..game_utils.game_result import GameResult, PlayerResult
from ..game_utils.teams import TeamManager
from ..game_utils.game_sound_mixin import GameSoundMixin
from ..game_utils.game_communication_mixin import GameCommunicationMixin
from ..game_utils.game_result_mixin import GameResultMixin
from ..game_utils.game_result_mixin import GameResultMixin
from ..game_utils.game_scores_mixin import GameScoresMixin
from ..game_utils.game_scores_mixin import GameScoresMixin
from ..game_utils.game_prediction_mixin import GamePredictionMixin
from ..game_utils.turn_management_mixin import TurnManagementMixin
from ..game_utils.menu_management_mixin import MenuManagementMixin
from ..game_utils.action_visibility_mixin import ActionVisibilityMixin
from ..game_utils.lobby_actions_mixin import LobbyActionsMixin, BOT_NAMES
from ..game_utils.event_handling_mixin import EventHandlingMixin
from ..game_utils.action_set_creation_mixin import ActionSetCreationMixin
from ..game_utils.action_execution_mixin import ActionExecutionMixin
from ..game_utils.action_set_system_mixin import ActionSetSystemMixin
from ..ui.keybinds import Keybind


@dataclass
class ActionContext:
    """Context passed to action handlers when triggered by keybind."""

    menu_item_id: str | None = None  # ID of selected menu item when keybind pressed
    menu_index: int | None = None  # 1-based index of selected menu item
    from_keybind: bool = (
        False  # True if triggered by keybind, False if by menu selection
    )


@dataclass
class Player(DataClassJSONMixin):
    """
    A player in a game.

    This is a dataclass that gets serialized with the game state.
    The user field is not serialized - it's reattached on load.
    """

    id: str  # UUID - unique identifier (from user.uuid for humans, generated for bots)
    name: str  # Display name
    is_bot: bool = False
    is_spectator: bool = False
    # Bot AI state (serialized for persistence)
    bot_think_ticks: int = 0  # Ticks until bot can act
    bot_pending_action: str | None = None  # Action to execute when ready
    bot_target: int | None = None  # Game-specific target (e.g., score to reach)


# Re-export GameOptions from options module for backwards compatibility
GameOptions = DeclarativeGameOptions


@dataclass
class Game(
    ABC,
    DataClassJSONMixin,
    GameSoundMixin,
    GameCommunicationMixin,
    GameResultMixin,
    GameScoresMixin,
    GamePredictionMixin,
    TurnManagementMixin,
    MenuManagementMixin,
    ActionVisibilityMixin,
    LobbyActionsMixin,
    EventHandlingMixin,
    ActionSetCreationMixin,
    ActionExecutionMixin,
    OptionsHandlerMixin,
    ActionSetSystemMixin,
):
    """
    Abstract base class for all games.

    Games are dataclasses that can be serialized with Mashumaro.
    All game state must be stored in dataclass fields.

    Games are synchronous and state-based. They expose actions that
    players can take, and these actions modify state imperatively.

    Games have three phases:
    - waiting: Lobby phase, host can add bots and start
    - playing: Game in progress
    - finished: Game over
    """

    class Config(BaseConfig):
        # Serialize all fields (don't omit defaults - breaks state restoration)
        serialize_by_alias = True

    # Game state
    players: list[Player] = field(default_factory=list)
    round: int = 0
    game_active: bool = False
    status: str = "waiting"  # waiting, playing, finished
    host: str = ""  # Username of the host
    current_music: str = ""  # Currently playing music track
    current_ambience: str = ""  # Currently playing ambience loop
    turn_index: int = 0  # Current turn index (serialized for persistence)
    turn_direction: int = 1  # Turn direction: 1 = forward, -1 = reverse
    turn_skip_count: int = 0  # Number of players to skip on next advance
    turn_player_ids: list[str] = field(
        default_factory=list
    )  # Player IDs in turn order (serialized)
    # Round timer state (serialized for persistence)
    round_timer_state: str = "idle"  # idle, counting, paused
    round_timer_ticks: int = 0  # Remaining ticks in countdown
    # Sound scheduler state (serialized for persistence)
    scheduled_sounds: list = field(
        default_factory=list
    )  # [[tick, sound, vol, pan, pitch], ...]
    sound_scheduler_tick: int = 0  # Current tick counter
    # Action sets (serialized - actions are pure data now)
    player_action_sets: dict[str, list[ActionSet]] = field(default_factory=dict)
    # Team manager (serialized for persistence)
    _team_manager: TeamManager = field(default_factory=TeamManager)

    def __post_init__(self):
        """Initialize non-serialized state."""
        # These are runtime-only, not serialized
        self._users: dict[str, User] = {}  # player_id -> User
        self._table: Any = None  # Reference to Table (set by server)
        self._keybinds: dict[
            str, list[Keybind]
        ] = {}  # key -> list of Keybinds (allows same key for different states)
        self._pending_actions: dict[
            str, str
        ] = {}  # player_id -> action_id (waiting for input)
        self._action_context: dict[
            str, ActionContext
        ] = {}  # player_id -> context during action execution
        self._status_box_open: set[str] = set()  # player_ids with status box open
        self._actions_menu_open: set[str] = set()  # player_ids with actions menu open
        self._destroyed: bool = False  # Whether game has been destroyed
        # Duration estimation state
        self._status_box_open: set[str] = set()  # player_ids with status box open
        self._actions_menu_open: set[str] = set()  # player_ids with actions menu open
        self._destroyed: bool = False  # Whether game has been destroyed

    def rebuild_runtime_state(self) -> None:
        """
        Rebuild non-serialized runtime state after deserialization.

        Called after loading a game from JSON. Subclasses should override
        this to rebuild any runtime-only objects not stored in serialized fields.
        Turn management and sound scheduling are now built into the base class
        using serialized fields, so they don't need rebuilding.

        Note: Estimation state is initialized clean by __post_init__.
        """
        pass

    # Abstract methods games must implement

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the display name of this game (English fallback)."""
        ...

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        """Return the type identifier for this game."""
        ...

    @classmethod
    def get_name_key(cls) -> str:
        """Return the localization key for this game's name."""
        return f"game-name-{cls.get_type()}"

    @classmethod
    def get_category(cls) -> str:
        """Return the category localization key for this game."""
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        """Return minimum number of players."""
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        """Return maximum number of players."""
        return 4

    @classmethod
    def get_leaderboard_types(cls) -> list[dict]:
        """Return additional leaderboard types this game supports.

        Override in subclasses to add game-specific leaderboards.
        Each dict should have:
        - "id": leaderboard type identifier (e.g., "best_single_turn")
        - "path": dot-separated path to value in custom_data
                  Use {player_id} or {player_name} as placeholders
                  e.g., "player_stats.{player_name}.best_turn"
                  OR for ratio calculations, use:
        - "numerator": path to numerator value
        - "denominator": path to denominator value
                  (values are summed across games, then divided)
        - "aggregate": how to combine values across games
                       "sum", "max", or "avg"
        - "format": entry format key suffix (e.g., "score" for leaderboard-score-entry)
        - "decimals": optional, number of decimal places (default 0)

        The server will look up localization keys like:
        - "leaderboard-type-{id}" for menu display (with underscores as hyphens)
        - "leaderboard-{format}-entry" for each entry
        """
        return []

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        """Return list of supported built-in leaderboard types.

        Options: "total_score", "high_score", "rating", "games_played"
        Override to exclude types that don't make sense for the game.
        """
        return ["total_score", "high_score", "rating", "games_played"]

    def prestart_validate(self) -> list[str] | list[tuple[str, dict]]:
        """Validate game configuration before starting.

        Returns a list of localization keys for any errors found,
        or a list of (error_key, kwargs) tuples for errors that need context.
        Override in subclasses to add game-specific validation.

        Examples:
            return ["pig-error-min-bank-too-high"]
            return [("scopa-error-not-enough-cards", {"decks": 1, "players": 4})]
        """
        return []

    def _validate_team_mode(self, team_mode: str) -> str | None:
        """Helper to validate team mode for current player count.

        Args:
            team_mode: Internal team mode string (e.g., "individual", "2v2").

        Returns:
            Localization key for error if invalid, None if valid.
        """
        active_players = self.get_active_players()
        num_players = len(active_players)

        # Parse old display format if needed
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)

        # Check if team mode is valid for player count
        if not TeamManager.is_valid_team_mode(team_mode, num_players):
            return "game-error-invalid-team-mode"

        return None

    @abstractmethod
    def on_start(self) -> None:
        """Called when the game starts."""
        ...

    def on_tick(self) -> None:
        """Called every tick (50ms). Handle bot AI here.

        Subclasses should call super().on_tick() to ensure base functionality runs.
        """
        pass

    def _sync_table_status(self) -> None:
        """Synchronize table status with game status.
        
        Call this when game status changes (e.g., waiting -> playing -> finished)
        to keep table and game status in sync.
        """
        if self._table:
            self._table.status = self.status

    def on_round_timer_ready(self) -> None:
        """Called when round timer expires. Override in subclasses that use RoundTimer."""
        pass

    def on_player_disconnect(self, player_id: str) -> None:
        """Handle player disconnection.
        
        If game is playing, replace human with bot to keep game going.
        """
        if self.status != "playing":
            return

        player = self.get_player_by_id(player_id)
        if not player or player.is_bot:
            return

        # Check if this is the last human player (excluding spectators)
        # If so, do NOT replace with bot - just pause the game (let them reconnect)
        remaining_humans = sum(1 for p in self.players if not p.is_bot and not p.is_spectator and p.id != player_id)
        
        # Spectators should just be removed, not replaced by bots
        if player.is_spectator:
            self.remove_spectator(player_id)
            # We don't play sound here because Server plays offline sound
            return

        if remaining_humans == 0:
             # Last human leaving - don't replace
             self.broadcast_l("game-paused-host-disconnect", player=player.name)
             return

        # Convert to bot
        self._replace_with_bot(player)

        # We don't play sound here because Server plays offline sound

    def remove_spectator(self, player_id: str) -> None:
        """Remove a spectator from the game state entirely."""
        player = self.get_player_by_id(player_id)
        if not player:
            return

        # Remove from players list
        self.players = [p for p in self.players if p.id != player_id]
        
        # Clean up game-specific state
        self.player_action_sets.pop(player_id, None)
        self._users.pop(player_id, None)
        
        # Notify others
        self.broadcast_l("spectator-left", player=player.name)

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the game state entirely.
        
        Use this only during lobby phase or forced removal where 
        bot replacement is NOT desired.
        """
        player = self.get_player_by_id(player_id)
        if not player:
            return

        # Remove from players list
        self.players = [p for p in self.players if p.id != player_id]
        
        # Clean up game-specific state
        self.player_action_sets.pop(player_id, None)
        self._users.pop(player_id, None)
        
        # Notify others
        self.broadcast_l("table-left", player=player.name)

    def _replace_with_bot(self, player: "Player") -> None:
        """Replace a human player with a bot (shared logic)."""
        # strict check: only replace if playing
        if self.status != "playing":
            return

        player.is_bot = True
        self._users.pop(player.id, None)

        from ..users.bot import Bot
        # Use same UUID so user can reclaim it
        bot_user = Bot(player.name, uuid=player.id)
        self.attach_user(player.id, bot_user)
        
        self.broadcast_l("player-replaced-by-bot", player=player.name)
        # Note: Caller is responsible for playing sounds if needed


    # Player management

    def attach_user(self, player_id: str, user: User) -> None:
        """Attach a user to a player by ID."""
        self._users[player_id] = user
        # Play current music/ambience for the joining user
        if self.current_music:
            user.play_music(self.current_music)
        if self.current_ambience:
            user.play_ambience(self.current_ambience)
            
        # Check for game resume (if this was a Host vs Bot paused scenario)
        if self.status == "playing":
             player = self.get_player_by_id(player_id)
             if player and not player.is_bot and not player.is_spectator:
                 # Count humans *including* this new one (who is already in _users)
                 # Exclude spectators from this count - we only care about ACTIVE players
                 human_count = sum(1 for p in self.players if not p.is_bot and not p.is_spectator and p.id in self._users)
                 # If this is the FIRST human back, it means we were paused
                 if human_count == 1:
                      self.broadcast_l("game-resumed", player=user.username)

    def get_user(self, player: Player) -> User | None:
        """Get the user for a player."""
        return self._users.get(player.id)

    def get_player_by_id(self, player_id: str) -> Player | None:
        """Get a player by ID (UUID)."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_player_by_name(self, name: str) -> Player | None:
        """Get a player by display name. Note: Names may not be unique."""
        for player in self.players:
            if player.name == name:
                return player
        return None

    @property
    def team_manager(self) -> TeamManager:
        """Get the team manager for this game."""
        return self._team_manager
