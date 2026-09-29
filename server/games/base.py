"""Base game class and player dataclass."""

from dataclasses import (
    FrozenInstanceError,
    dataclass,
    field,
    fields,
    is_dataclass,
    replace,
)
from typing import Any, ClassVar
from abc import ABC, abstractmethod

from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.config import BaseConfig

from ..users.base import User
from ..gender import Gender, gender_localization_kwargs, normalize_gender
from ..game_utils.actions import ActionSet
from ..game_utils.options import (
    GameOptions as DeclarativeGameOptions,
    OptionsHandlerMixin,
)
from ..game_utils.teams import TeamManager
from ..game_utils.game_sound_mixin import GameSoundMixin
from ..audio import AudioPlaybackState
from ..game_utils.game_communication_mixin import GameCommunicationMixin
from ..game_utils.game_result_mixin import GameResultMixin
from ..game_utils.game_scores_mixin import GameScoresMixin
from ..game_utils.game_prediction_mixin import GamePredictionMixin
from ..game_utils.sequence_runner_mixin import SequenceRunnerMixin, SequenceState
from ..game_utils.turn_management_mixin import TurnManagementMixin
from ..game_utils.menu_management_mixin import MenuManagementMixin
from ..game_utils.action_visibility_mixin import ActionVisibilityMixin
from ..game_utils.lobby_actions_mixin import LobbyActionsMixin
from ..game_utils.bot_names import get_valid_bot_name_pool
from ..game_utils.event_handling_mixin import EventHandlingMixin
from ..game_utils.action_set_creation_mixin import ActionSetCreationMixin
from ..game_utils.action_execution_mixin import ActionExecutionMixin
from ..game_utils.action_set_system_mixin import ActionSetSystemMixin
from ..game_utils.action_context import ActionContext
from ..game_utils.client_types import (
    is_touch_client as user_is_touch_client,
    is_touch_client_type,
)
from ..game_utils.player import Player
from ..ui.keybinds import Keybind
from ..users.bot import Bot
from .categories import CATEGORY_MISC, normalize_category

BOT_NAMES = get_valid_bot_name_pool()


def _replace_exact_state_value(value: Any, old_value: str, new_value: str) -> Any:
    """Replace one exact player identity value inside Mashumaro-safe state.

    Player UUIDs and, in a few legacy game fields, display names occur both as
    values and mapping keys. A seat substitution changes both, so every exact
    reference must move together. This helper deliberately does not perform
    substring replacement; historical prose remains historical prose.
    """
    if isinstance(value, str):
        return new_value if value == old_value else value
    if isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = _replace_exact_state_value(item, old_value, new_value)
        return value
    if isinstance(value, dict):
        replaced_items = [
            (
                _replace_exact_state_value(key, old_value, new_value),
                _replace_exact_state_value(item, old_value, new_value),
            )
            for key, item in value.items()
            if old_value not in value or key not in {old_value, new_value}
        ]
        if old_value in value:
            # A newly joined spectator can have disposable view state under
            # the destination value. The retained seat always wins a key
            # collision.
            replaced_items.insert(
                0,
                (
                    new_value,
                    _replace_exact_state_value(
                        value[old_value],
                        old_value,
                        new_value,
                    ),
                ),
            )
        value.clear()
        value.update(replaced_items)
        return value
    if isinstance(value, set):
        replaced_values = {
            _replace_exact_state_value(item, old_value, new_value)
            for item in value
        }
        value.clear()
        value.update(replaced_values)
        return value
    if isinstance(value, frozenset):
        updated = frozenset(
            _replace_exact_state_value(item, old_value, new_value)
            for item in value
        )
        return value if updated == value else updated
    if isinstance(value, tuple):
        updated_items = tuple(
            _replace_exact_state_value(item, old_value, new_value)
            for item in value
        )
        if all(updated is current for updated, current in zip(updated_items, value)):
            return value
        if hasattr(value, "_fields"):
            return type(value)(*updated_items)
        return updated_items
    if is_dataclass(value) and not isinstance(value, type):
        replacements: dict[str, Any] = {}
        for declared_field in fields(value):
            current = getattr(value, declared_field.name)
            updated = _replace_exact_state_value(current, old_value, new_value)
            if updated is not current:
                replacements[declared_field.name] = updated
        if not replacements:
            return value
        try:
            for name, updated in replacements.items():
                setattr(value, name, updated)
            return value
        except FrozenInstanceError:
            return replace(value, **replacements)
    return value


@dataclass(frozen=True)
class SeatSubstitutionResult:
    """The identities affected by one completed in-game substitution."""

    previous_controller_name: str
    replaced_human_name: str
    outgoing_spectator: Player | None


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
    SequenceRunnerMixin,
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
        lazy_compilation = True

    #: User preference names this game is relevant to (for per-game overrides).
    relevant_preferences: ClassVar[list[str]] = []
    #: Action sets whose pure visibility callbacks may run before enabled-state
    #: callbacks so contextually hidden rows can be discarded cheaply.
    visibility_first_action_sets: ClassVar[frozenset[str]] = frozenset()

    # Game state
    players: list[Player] = field(default_factory=list)
    round: int = 0
    game_active: bool = False
    status: str = "waiting"  # waiting, playing, finished
    host: str = ""  # Username of the host
    # Read-only migration inputs retained so pre-protocol saves deserialize.
    current_music: str = ""
    current_ambience: str = ""
    current_ambience_outro: str = ""
    # Canonical reconnect/save state for independently managed audio layers.
    # The three fields above remain a read-migration bridge for older saves.
    active_audio: dict[str, AudioPlaybackState] = field(default_factory=dict)
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
    active_sequences: list[SequenceState] = field(default_factory=list)
    # Action sets (serialized - actions are pure data now)
    player_action_sets: dict[str, list[ActionSet]] = field(default_factory=dict)
    # Team manager (serialized for persistence)
    _team_manager: TeamManager = field(default_factory=TeamManager)
    team_arrangement_active: bool = False
    team_arrangement_selected_player_id: str = ""
    team_arrangement_team_mode: str = ""

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
        self._live_status_boxes: dict[str, Any] = {}  # player_id -> live status state
        self._actions_menu_open: set[str] = set()  # player_ids with actions menu open
        self._actions_menu_return_focus: dict[str, str] = {}
        self._pending_action_return_focus: dict[str, str] = {}
        self._status_box_return_focus: dict[str, str] = {}
        # Menu refresh recording (runtime-only). refresh_menus() and
        # request_menu_focus() mark intent here; the framework-driven
        # flush_menus() consumes it (end of handle_event + once per tick).
        self._menu_dirty: set[str] = set()  # player_ids needing a repaint
        self._menu_dirty_all: bool = False  # repaint everyone at next flush
        # player_id -> item id for a one-shot focus jump at the next flush.
        self._pending_menu_focus: dict[str, str] = {}
        # Runtime-only options navigation stack for multi-select options
        # (player_id -> list of path segments). Transient lobby state; not
        # serialized, so it safely resets to top-level on reconnect/restore.
        self._options_path: dict[str, list[str]] = {}
        self._destroyed: bool = False  # Whether game has been destroyed
        self._last_game_result = None  # Stored for end-screen restoration
        self._end_screen_open_player_ids: set[str] = set()
        # Per-player transcript of table events (runtime-only). Games that want a
        # reviewable history call record_transcript_event(); see get_transcript().
        self._transcripts: dict[str, list[dict[str, str]]] = {}

    def rebuild_runtime_state(self) -> None:
        """
        Rebuild non-serialized runtime state after deserialization.

        Called after loading a game from JSON. Subclasses should override
        this to rebuild any runtime-only objects not stored in serialized fields.
        Turn management and sound scheduling are now built into the base class
        using serialized fields, so they don't need rebuilding.

        Note: Estimation state is initialized clean by __post_init__.
        """
        # Waiting lobbies are intentionally silent. Drop replayable audio from
        # older saves/checkpoints so a pre-change lobby track cannot return
        # when users attach to the restored game.
        if self.status == "waiting":
            self.active_audio.clear()
            self.current_music = ""
            self.current_ambience = ""
            self.current_ambience_outro = ""
        else:
            self.migrate_legacy_audio_state()

    def on_discard(self) -> None:
        """Release game-specific memory before this instance is abandoned.

        Table closure and table restart both call this idempotent lifecycle hook.
        Persistent fields that exist only to inform the current match may be
        cleared here so stale references cannot retain them while the discarded
        game instance awaits garbage collection.
        """
        table_audio_batcher = getattr(self, "_table_presence_audio_batcher", None)
        if table_audio_batcher is not None:
            # A lifecycle boundary may occur in the same synchronous action
            # that queued a legitimate final departure cue. Flush it before
            # detaching the game's users so the event is not lost or replayed
            # later in an unrelated menu.
            table_audio_batcher.flush()

    def _reset_transcripts(self) -> None:
        """Initialize transcript storage for seated players."""
        self._transcripts = {
            player.id: [] for player in self.players if not player.is_spectator
        }

    def record_transcript_event(
        self, player: "Player | None", text: str, buffer: str = "table"
    ) -> None:
        """Store a transcript entry for a player."""
        if not player or player.is_spectator:
            return
        self._transcripts.setdefault(player.id, []).append(
            {"text": text, "buffer": buffer}
        )

    def get_transcript(self, player_id: str) -> list[dict[str, str]]:
        """Return the transcript history for a player."""
        return list(self._transcripts.get(player_id, []))

    @staticmethod
    def is_touch_client_type(client_type: str | None) -> bool:
        """Return True for touch-oriented clients."""
        return is_touch_client_type(client_type)

    def is_touch_client(self, user: User | None) -> bool:
        """Return True if the provided user is on a touch-oriented client."""
        return bool(user and user_is_touch_client(user))

    def is_touch_player(self, player: Player) -> bool:
        """Return True if the player's attached user is on a touch-oriented client."""
        return self.is_touch_client(self.get_user(player))

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
        """Return the backend category id for this game."""
        return CATEGORY_MISC

    @classmethod
    def get_categories(cls) -> tuple[str, ...]:
        """Return all backend category ids this game belongs to."""
        return (normalize_category(cls.get_category()),)

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

        Options: "wins", "total_score", "high_score", "rating", "games_played"
        Games must opt in to the types that match their GameResult data.
        """
        return []

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

    def validate_start(self) -> list[str | tuple[str, dict]]:
        """Return complete framework and game-specific start errors.

        Player-count validation is framework-owned so a game cannot bypass it
        by omitting ``super().prestart_validate()``. ``prestart_validate()``
        remains the game hook for option, deal, team, and ruleset checks.
        """
        active_count = self.get_active_player_count()
        minimum = self.get_min_players()
        maximum = self.get_max_players()
        errors: list[str | tuple[str, dict]] = []

        if minimum == maximum and active_count != minimum:
            errors.append(
                (
                    "action-start-requires-exact-players",
                    {"current": active_count, "required": minimum},
                )
            )
        elif active_count < minimum:
            errors.append(
                (
                    "action-start-needs-more-players",
                    {"current": active_count, "minimum": minimum},
                )
            )
        elif active_count > maximum:
            errors.append(
                (
                    "action-start-has-too-many-players",
                    {"current": active_count, "maximum": maximum},
                )
            )

        if not self.get_active_human_players():
            errors.append("action-start-needs-human-player")

        legacy_count_keys = {"action-need-more-players", "action-table-full"}
        for error in self.prestart_validate():
            key = error[0] if isinstance(error, tuple) else error
            if errors and key in legacy_count_keys:
                continue
            if error not in errors:
                errors.append(error)

        return errors

    def _validate_team_mode(self, team_mode: str) -> str | None:
        """Helper to validate team mode for current player count.

        Args:
            team_mode: Internal team mode string (e.g., "individual", "2v2").

        Returns:
            Localization key for error if invalid, None if valid.
        """
        active_players = self.get_active_players()
        num_players = len(active_players)

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
        self.process_audio_automations()
        self._sync_replacement_team_members()
        for player in self.players:
            if getattr(player, "reconnect_grace_ticks", 0) > 0:
                player.reconnect_grace_ticks -= 1

    def _sync_table_status(self) -> None:
        """Synchronize table status with game status.
        
        Call this when game status changes (e.g., waiting -> playing -> finished)
        to keep table and game status in sync.
        """
        if self._table:
            if (
                getattr(self._table, "game", None) is self
                and hasattr(self._table, "_sync_status_from_game")
            ):
                self._table._sync_status_from_game()
                return

            status_changed = self._table.status != self.status
            self._table.status = self.status
            if (
                status_changed
                and self.status != "waiting"
                and hasattr(self._table, "_member_offline_since")
            ):
                self._table._member_offline_since.clear()
            if (
                status_changed
                and self._table._server
                and hasattr(self._table._server, "on_tables_changed")
            ):
                self._table._server.on_tables_changed()

    def _notify_table_presence_changed(self) -> None:
        """Notify server-owned table overlays that the game roster changed."""
        server = getattr(getattr(self, "_table", None), "_server", None)
        if server and hasattr(server, "on_tables_changed"):
            server.on_tables_changed()

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

        self.play_table_disconnect_sound(player)

        # Spectators should just be removed, not replaced by bots
        if player.is_spectator:
            user = self.get_user(player)
            username = user.username if user else player.name
            self.remove_spectator(player_id)
            remove_member = getattr(self._table, "remove_member", None)
            if callable(remove_member):
                remove_member(
                    username,
                    voice_reason="voice-status-connection-lost",
                )
            return

        # A present spectator host can supervise continued bot play without
        # occupying a seat.  Otherwise the last active human retains their
        # seat so the bounded reconnect grace can pause the game safely.
        remaining_humans = sum(
            1
            for candidate in self.players
            if not candidate.is_bot
            and not candidate.is_spectator
            and candidate.id != player_id
        )
        spectator_host_online = bool(
            self._table and self._table.has_online_spectator_host()
        )

        if remaining_humans == 0 and not spectator_host_online:
            self.broadcast_l(
                "game-paused-host-disconnect",
                buffer="system",
                player=player.name,
            )
            return

        if self._replace_with_bot(player):
            self.refresh_menus()

    def remove_spectator(self, player_id: str) -> None:
        """Remove a spectator from the game state entirely."""
        player = self.get_player_by_id(player_id)
        if not player:
            return

        # Release modal/runtime intent while the player's declarative actions
        # are still available for lock detection and game-owned cleanup hooks.
        self._clear_player_ui_runtime_state(player_id, player=player)

        # Remove from players list and game-specific action state.
        self.players = [p for p in self.players if p.id != player_id]
        self.player_action_sets.pop(player_id, None)
        self._users.pop(player_id, None)
        self.prune_audio_recipient(player_id)
        discard_end_screen = getattr(self, "_discard_end_screen_player_id", None)
        if discard_end_screen:
            discard_end_screen(player_id)
        
        # Notify others
        self.broadcast_l("spectator-left", buffer="system", player=player.name)
        self._notify_table_presence_changed()

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the game state entirely.
        
        Use this only during lobby phase or forced removal where 
        bot replacement is NOT desired.
        """
        player = self.get_player_by_id(player_id)
        if not player:
            return

        if self.team_arrangement_active and not player.is_spectator:
            self._cancel_team_arrangement_for_roster_change()

        # Release modal/runtime intent while the player's declarative actions
        # are still available for lock detection and game-owned cleanup hooks.
        self._clear_player_ui_runtime_state(player_id, player=player)

        # Remove from players list and game-specific action state.
        self.players = [p for p in self.players if p.id != player_id]
        self.player_action_sets.pop(player_id, None)
        self._users.pop(player_id, None)
        self.prune_audio_recipient(player_id)
        discard_end_screen = getattr(self, "_discard_end_screen_player_id", None)
        if discard_end_screen:
            discard_end_screen(player_id)
        
        # Notify others
        self.broadcast_l("table-left", buffer="system", player=player.name)
        self._notify_table_presence_changed()

    def _replace_with_bot(
        self,
        player: "Player",
        *,
        allow_waiting: bool = False,
    ) -> bool:
        """Replace a human player with a bot (shared logic)."""
        if self.status != "playing" and not (
            allow_waiting and self.status == "waiting"
        ):
            return False
        if player.is_bot:
            return False

        human_name = player.replaced_human_name or player.name
        existing_names = self._reserved_table_names(exclude_player_id=player.id)
        existing_names.append(human_name)
        bot_name = self._generate_available_bot_name(existing_names)

        player.replaced_human = True
        player.is_bot = True
        player.replaced_human_name = human_name
        player.replacement_bot_name = bot_name
        player.name = bot_name
        self._rename_team_member(human_name, bot_name)
        self._clear_player_ui_runtime_state(player.id, player=player)
        self._users.pop(player.id, None)

        # Use same UUID so user can reclaim it
        bot_user = Bot(bot_name, uuid=player.id)
        self.attach_user(player.id, bot_user)
        
        self.broadcast_l(
            "player-replaced-by-bot",
            buffer="system",
            player=human_name,
            bot=bot_name,
        )
        self._notify_table_presence_changed()
        # Note: Caller is responsible for playing sounds if needed
        return True

    def _prepare_seat_substitution(self, player: "Player") -> None:
        """Cancel game-specific work before another human takes control.

        Most bots are tick-driven and need no extra cleanup. Games with
        asynchronous bot work may override this hook, cancel only work owned by
        ``player``, and then call ``super()``.
        """

    def _rekey_game_state_value(self, old_value: str, new_value: str) -> None:
        """Move one exact UUID or legacy display-name reference everywhere."""
        serialized_names = {declared_field.name for declared_field in fields(self)}
        for declared_field in fields(self):
            current = getattr(self, declared_field.name)
            updated = _replace_exact_state_value(current, old_value, new_value)
            if updated is not current:
                setattr(self, declared_field.name, updated)

        # Runtime-only game containers can also key harmless view/history state
        # by player id. Restrict traversal to built-in containers so sockets,
        # tasks, users, and the table/server object graph are never inspected.
        for name, current in list(vars(self).items()):
            if name in serialized_names or name in {"_table", "_users"}:
                continue
            if isinstance(current, (dict, list, set, frozenset, tuple)):
                updated = _replace_exact_state_value(
                    current,
                    old_value,
                    new_value,
                )
                if updated is not current:
                    setattr(self, name, updated)

    def substitute_player_with_spectator(
        self,
        seat_player: "Player",
        spectator: "Player",
        spectator_user: User,
        *,
        outgoing_user: User | None = None,
    ) -> SeatSubstitutionResult:
        """Atomically give an active seat to a consenting spectator.

        The seat player object is retained so every game-specific attribute on
        it survives. A relinquishing human receives a fresh spectator object;
        bot-held seats have no outgoing spectator. Exact UUID and legacy-name
        references move with the seat across serialized state and bounded
        runtime containers.
        """
        if self.status != "playing":
            raise ValueError("Player substitution requires an active game")
        if (
            not any(player is seat_player for player in self.players)
            or seat_player.is_spectator
        ):
            raise ValueError("The requested player seat is no longer available")
        if (
            not any(player is spectator for player in self.players)
            or spectator.is_bot
            or not spectator.is_spectator
        ):
            raise ValueError("The recipient is no longer a human spectator")

        old_id = str(seat_player.id)
        new_id = str(spectator.id)
        if not old_id or not new_id or old_id == new_id:
            raise ValueError("Player substitution requires distinct identifiers")
        if str(getattr(spectator_user, "uuid", "")) != new_id:
            raise ValueError(
                "The spectator session does not own the requested identity"
            )
        if any(
            player is not spectator
            and player is not seat_player
            and player.id == new_id
            for player in self.players
        ):
            raise ValueError(
                "The spectator identity is already assigned to another seat"
            )
        if seat_player.is_bot:
            if outgoing_user is not None:
                raise ValueError("A bot-controlled seat cannot have an outgoing user")
        elif (
            outgoing_user is None
            or str(getattr(outgoing_user, "uuid", "")) != old_id
            or self._users.get(old_id) is not outgoing_user
        ):
            raise ValueError("The outgoing session does not own the requested seat")

        previous_controller_name = seat_player.name
        replaced_human_name = seat_player.replaced_human_name
        spectator_name = spectator.name
        outgoing_name = "" if seat_player.is_bot else seat_player.name
        retained_host = self.host

        self._prepare_seat_substitution(seat_player)
        self._clear_player_ui_runtime_state(new_id, player=spectator)
        self._clear_player_ui_runtime_state(old_id, player=seat_player)

        # Clear role-specific gameplay sources before authoritative public and
        # private layers are replayed for each new role. Table voice is a
        # separate LiveKit context and is deliberately unaffected.
        spectator_user.stop_all_audio(fade_ms=0)
        if outgoing_user is not None:
            outgoing_user.stop_all_audio(fade_ms=0)

        # Retire the spectator slot without emitting a misleading leave event.
        self.players = [player for player in self.players if player is not spectator]
        self.player_action_sets.pop(new_id, None)
        self._users.pop(new_id, None)
        self.prune_audio_recipient(new_id)
        self._transcripts.pop(new_id, None)
        discard_end_screen = getattr(self, "_discard_end_screen_player_id", None)
        if discard_end_screen:
            discard_end_screen(new_id)

        # The old controller must never remain attached to the retained seat.
        self._users.pop(old_id, None)

        # Rekey every serialized/runtime identity reference. This includes the
        # retained Player.id plus legacy name-based turn/tiebreak state.
        self._rekey_game_state_value(old_id, new_id)
        self._rekey_game_state_value(previous_controller_name, spectator_name)
        self._reindex_active_audio()
        # Table ownership is independent of the seat. A host who voluntarily
        # becomes a spectator retains host permissions and identity.
        self.host = retained_host

        seat_player.is_bot = False
        seat_player.replaced_human = False
        seat_player.replaced_human_name = ""
        seat_player.replacement_bot_name = ""
        seat_player.is_spectator = False
        seat_player.bot_pending_action = None
        seat_player.bot_think_ticks = 0

        self.attach_user(new_id, spectator_user)
        # This explicit synchronized action must not reset or extend any
        # authoritative game/turn timer with reconnect grace.
        seat_player.reconnect_grace_ticks = 0

        # Rebuild labels and declarative actions using the incoming user's
        # locale and client capabilities.
        self.player_action_sets.pop(new_id, None)
        self.setup_player_actions(seat_player)
        self._on_replacement_slot_reclaimed(
            previous_controller_name,
            spectator_name,
        )

        outgoing_spectator = None
        if outgoing_user is not None:
            outgoing_spectator = self.create_player(
                old_id,
                outgoing_name,
                is_bot=False,
            )
            outgoing_spectator.is_spectator = True
            self.players.append(outgoing_spectator)
            self.attach_user(old_id, outgoing_user)
            self.setup_player_actions(outgoing_spectator)

        self.refresh_menus()
        return SeatSubstitutionResult(
            previous_controller_name=previous_controller_name,
            replaced_human_name=replaced_human_name,
            outgoing_spectator=outgoing_spectator,
        )

    def _clear_player_ui_runtime_state(
        self,
        player_id: str,
        *,
        player: "Player | None" = None,
    ) -> None:
        """Release transient UI intent that must not outlive a human seat."""
        player = player or self.get_player_by_id(player_id)
        if player and player_id in self._pending_actions:
            self._discard_pending_action_input(player)
        else:
            self._pending_actions.pop(player_id, None)
            self._pending_action_return_focus.pop(player_id, None)
        self._action_context.pop(player_id, None)
        self._actions_menu_open.discard(player_id)
        self._actions_menu_return_focus.pop(player_id, None)
        self._status_box_open.discard(player_id)
        self._live_status_boxes.pop(player_id, None)
        self._status_box_return_focus.pop(player_id, None)
        self._menu_dirty.discard(player_id)
        self._pending_menu_focus.pop(player_id, None)
        self._options_path.pop(player_id, None)

    def _reserved_table_names(self, *, exclude_player_id: str | None = None) -> list[str]:
        """Return all names currently reserved by the table and game state."""
        names: list[str] = []
        if self._table and hasattr(self._table, "reserved_names"):
            names.extend(self._table.reserved_names(exclude_player_id=exclude_player_id))
        else:
            for existing_player in self.players:
                if getattr(existing_player, "id", None) == exclude_player_id:
                    continue
                names.append(existing_player.name)
                if existing_player.replaced_human_name:
                    names.append(existing_player.replaced_human_name)
        return names

    # Player management

    def attach_user(
        self,
        player_id: str,
        user: User,
        *,
        session_handover: bool = False,
    ) -> None:
        """Attach a user to a player by ID.

        ``session_handover`` replaces one live device with another without
        treating the player as having left gameplay. Authoritative timers and
        sequences continue, active audio is replayed, and no reconnect grace or
        table-wide resume announcement is introduced.
        """
        self._users[player_id] = user
        # Play current music/ambience for the joining user
        for state in self.active_audio.values():
            if state.recipient_ids and player_id not in state.recipient_ids:
                continue
            for command in state.replay_commands():
                user.send_audio_command(command)
            if state.paused and state.kind == "music":
                user.pause_music(handle=state.handle, fade_ms=0)
        # Check for game resume (if this was a paused-table reconnect scenario).
        if self.status == "playing":
            player = self.get_player_by_id(player_id)
            if player and not player.is_bot and not player.is_spectator:
                # Clear pending bot actions.
                player.bot_pending_action = None
                player.bot_think_ticks = 0

                table = getattr(self, "_table", None)
                power_restore_active = bool(
                    table
                    and hasattr(table, "is_power_restore_grace_active")
                    and table.is_power_restore_grace_active()
                )

                # Normal reconnects keep a short sync grace. Planned reboot
                # restores use a table-level grace with explicit feedback, so
                # do not leave a second silent per-player block behind. A live
                # session handover never disconnected from authoritative game
                # state and therefore must not reset or extend this gate.
                if not session_handover:
                    player.reconnect_grace_ticks = (
                        0 if power_restore_active else 20
                    )

                # Count humans including this new one (already in _users).
                # During planned reboot restore grace, the table owns the
                # resume announcement after all returning players are handled.
                human_count = sum(
                    1
                    for p in self.players
                    if not p.is_bot and not p.is_spectator and p.id in self._users
                )
                if (
                    human_count == 1
                    and not power_restore_active
                    and not session_handover
                ):
                    self.broadcast_l(
                        "game-resumed",
                        buffer="system",
                        player=user.username,
                    )

                # Mark the player's menu for repaint so they have UI state
                # at the next flush (within the current tick).
                self.refresh_menus(player)

    def get_user(self, player: Player) -> User | None:
        """Get the user for a player."""
        return self._users.get(player.id)

    def get_player_gender(self, player: Player) -> Gender:
        """Return current account gender for a game seat.

        Connected humans carry their live account value. Disconnected seats
        and bots temporarily controlling a human seat resolve through the
        immutable account UUID, keeping saved games free of duplicated profile
        data while still supporting announcements and future audio choices.
        Synthetic bots and deleted accounts use the neutral default.
        """
        user = self.get_user(player)
        if user is not None and not player.is_bot:
            return normalize_gender(getattr(user, "gender", None))

        bot_gender = (
            normalize_gender(getattr(user, "gender", None))
            if user is not None
            else None
        )
        if bot_gender is not None and bot_gender is not Gender.UNSPECIFIED:
            return bot_gender

        # Native bots do not represent an account. Avoid an unnecessary
        # database query for every announcement involving one; only a bot
        # explicitly holding a disconnected human's seat needs UUID lookup.
        if player.is_bot and not player.replaced_human:
            return Gender.UNSPECIFIED

        table = getattr(self, "_table", None)
        database = getattr(table, "_db", None) if table is not None else None
        lookup_gender = (
            getattr(database, "get_user_gender_by_uuid", None)
            if database is not None
            else None
        )
        if callable(lookup_gender):
            return normalize_gender(lookup_gender(player.id))
        return bot_gender or Gender.UNSPECIFIED

    def player_localization_kwargs(
        self,
        player: Player,
        variable: str = "player",
    ) -> dict[str, str]:
        """Build the canonical Fluent name and gender arguments for a player."""
        return {
            variable: player.name,
            **gender_localization_kwargs(
                self.get_player_gender(player),
                variable,
            ),
        }

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
