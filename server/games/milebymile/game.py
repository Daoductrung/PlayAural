"""
Mile by Mile Game Implementation for PlayAural v0.1.0.

A racing card game based on Mille Bornes. Players race to reach a target distance
while playing hazards on opponents and defending with safeties.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.round_timer import RoundTimer
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .cards import (
    Card,
    Deck,
    CardType,
    HazardType,
    RemedyType,
    SafetyType,
    HAZARD_TO_SAFETY,
    SAFETY_TO_HAZARD,
)
from .options import MileByMileOptions
from .player import MileByMilePlayer
from .state import RaceState

# Hand size
HAND_SIZE = 6


@dataclass
@register_game
class MileByMileGame(Game):
    """
    Mile by Mile - A racing card game based on Mille Bornes.

    Players race to reach a target distance by playing distance cards.
    Hazards slow opponents, remedies fix problems, and safeties provide
    permanent protection. First team to reach the winning score wins.
    """

    players: list[MileByMilePlayer] = field(default_factory=list)
    options: MileByMileOptions = field(default_factory=MileByMileOptions)

    # Game state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    protections_pile: list[Card] = field(
        default_factory=list
    )  # Safeties, never reshuffled
    race_states: list[RaceState] = field(default_factory=list)  # Per-team race state
    current_race: int = 0
    race_winner_team_index: int | None = None

    # Dirty trick window
    dirty_trick_window_team: int | None = None
    dirty_trick_window_hazard: str | None = None
    dirty_trick_window_ticks: int = 0

    # Round timer state (serialized)
    round_timer_state: str = "idle"
    round_timer_ticks: int = 0

    def __post_init__(self):
        """Initialize runtime state."""
        super().__post_init__()
        self._round_timer = RoundTimer(self, delay_seconds=10.0)

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()
        self._round_timer = RoundTimer(self, delay_seconds=10.0)

    @classmethod
    def get_name(cls) -> str:
        return "Mile by Mile"

    @classmethod
    def get_type(cls) -> str:
        return "milebymile"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 9

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> MileByMilePlayer:
        """Create a new player."""
        return MileByMilePlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Team Management
    # ==========================================================================

    def _setup_teams(self) -> None:
        """Set up teams using TeamManager."""
        active_players = self.get_active_players()
        player_names = [p.name for p in active_players]

        # options.team_mode should be in internal format, but handle old display format for backwards compatibility
        team_mode = self.options.team_mode
        # If it contains spaces or uppercase (except 'v'), it's likely old display format
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)
        self._team_manager.team_mode = team_mode
        self._team_manager.setup_teams(player_names)

        # Set player team indices
        for player in active_players:
            team = self._team_manager.get_team(player.name)
            if team:
                player.team_index = team.index

        # Initialize race states for each team
        self.race_states = [RaceState() for _ in self._team_manager.teams]

    def get_race_state(self, team_index: int) -> RaceState | None:
        """Get the race state for a team by index."""
        if 0 <= team_index < len(self.race_states):
            return self.race_states[team_index]
        return None

    def get_player_race_state(self, player: MileByMilePlayer) -> RaceState | None:
        """Get the race state for a player's team."""
        return self.get_race_state(player.team_index)

    def get_team_name(self, team_index: int, locale: str = "en") -> str:
        """Get display name for a team by index."""
        if team_index < len(self._team_manager.teams):
            return self._team_manager.get_team_name(self._team_manager.teams[team_index], locale)
        # Fallback if team doesn't exist in manager (shouldn't happen)

        return Localization.get(locale, "game-team-name", index=team_index + 1)

    def is_individual_mode(self) -> bool:
        """Check if game is in individual mode."""
        return self.options.team_mode == "individual"

    def get_num_teams(self) -> int:
        """Get the number of teams."""
        return len(self._team_manager.teams)

    def get_team_score(self, team_index: int) -> int:
        """Get total score for a team."""
        if team_index < len(self._team_manager.teams):
            return self._team_manager.teams[team_index].total_score
        return 0

    def add_team_score(self, team_index: int, points: int) -> None:
        """Add points to a team's score."""
        if team_index < len(self._team_manager.teams):
            self._team_manager.teams[team_index].total_score += points

    def set_team_round_score(self, team_index: int, points: int) -> None:
        """Set the round score for a team."""
        if team_index < len(self._team_manager.teams):
            self._team_manager.teams[team_index].round_score = points

    def iter_teams(self):
        """Iterate over (team_index, race_state) pairs."""
        for i, race_state in enumerate(self.race_states):
            yield i, race_state

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: MileByMilePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Card slot actions will be dynamically added/removed
        # Status action (will be repositioned after cards in _update_card_actions)
        # WEB-SPECIFIC: Moved to Standard Action Set for Web
        is_web = user and getattr(user, "client_type", "") == "web"
        if not is_web:
            action_set.add(
                Action(
                    id="check_status",
                    label=Localization.get(locale, "milebymile-check-status"),
                    handler="_action_check_status",
                    is_enabled="_is_check_status_enabled",
                    is_hidden="_is_check_status_hidden",
                )
            )

        # Dirty trick action (hidden, triggered by keybind)
        action_set.add(
            Action(
                id="dirty_trick",
                label=Localization.get(locale, "milebymile-dirty-trick"),
                handler="_action_dirty_trick",
                is_enabled="_is_dirty_trick_enabled",
                is_hidden="_is_dirty_trick_hidden",
            )
        )

        # Junk card action (hidden, triggered by shift+enter or backspace keybind)
        action_set.add(
            Action(
                id="junk_card",
                label=Localization.get(locale, "milebymile-discard-card"),
                handler="_action_junk_card",
                is_enabled="_is_junk_card_enabled",
                is_hidden="_is_junk_card_hidden",
            )
        )

        # Detailed status action (hidden, triggered by shift+s keybind)
        # WEB-SPECIFIC: Moved to Standard Action Set for Web
        if not is_web:
            action_set.add(
                Action(
                    id="check_status_detailed",
                    label=Localization.get(locale, "milebymile-detailed-status"),
                    handler="_action_check_status_detailed",
                    is_enabled="_is_check_status_enabled",
                    is_hidden="_is_check_status_hidden",
                )
            )

        # Info action (Button "Info" / "Thông tin")
        # Python: Action menu only (Info 1 of 8 removed), Shortcut 'i'
        # Web: Turn menu
        action_set.add(
            Action(
                id="info",
                label=Localization.get(locale, "milebymile-info-button"),
                handler="_action_info",
                is_enabled="_is_check_status_enabled", # Enabled when playing
                is_hidden="_is_info_hidden", # Visible when playing (Web), hidden otherwise (Python)
                show_in_actions_menu=True, # Show in generic Action Menu (Python)
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_status", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            locale = user.locale

            # Ensure 'check_status' is in standard set (moved from turn set for web)
            if not action_set.get_action("check_status"):
                 action_set.add(
                    Action(
                        id="check_status",
                        label=Localization.get(locale, "milebymile-check-status"),
                        handler="_action_check_status",
                        is_enabled="_is_check_status_enabled",
                        is_hidden="_is_check_status_hidden",
                    )
                )

            # Ensure 'check_status_detailed' is in standard set (moved from turn set for web)
            if not action_set.get_action("check_status_detailed"):
                 action_set.add(
                    Action(
                        id="check_status_detailed",
                        label=Localization.get(locale, "milebymile-detailed-status"),
                        handler="_action_check_status_detailed",
                        is_enabled="_is_check_status_enabled",
                        is_hidden="_is_detailed_status_hidden", # Hidden to push to Actions Menu
                    )
                )

            # Reordering Logic
            final_order = []
            for aid in self.web_target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)
            
            for aid in action_set._order:
                if aid not in self.web_target_order:
                    final_order.append(aid)
            
            action_set._order = final_order

        return action_set


    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        # Remove base class's 's' and 'shift+s' keybinds before adding ours
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        # Override 's' to only show status (not scores from base class)
        self.define_keybind(
            "s",
            Localization.get("en", "milebymile-check-status"),
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Override 'shift+s' to show detailed status (not just scores)
        self.define_keybind(
            "shift+s",
            Localization.get(locale, "milebymile-detailed-status"),
            ["check_status_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Info keybind 'i'
        self.define_keybind(
            "i",
            Localization.get(locale, "milebymile-info-button"),
            ["info"],
            state=KeybindState.ACTIVE,
        )

        # Dirty trick keybind
        self.define_keybind(
            "d",
            Localization.get(locale, "milebymile-dirty-trick"),
            ["dirty_trick"],
            state=KeybindState.ACTIVE,
        )

        # Number keys for card slots (1-6)
        for i in range(1, HAND_SIZE + 1):
            self.define_keybind(
                str(i), f"Play card {i}", [f"card_slot_{i}"], state=KeybindState.ACTIVE
            )

        # Shift+Enter or Backspace to discard the selected card
        self.define_keybind(
            "shift+enter",
            Localization.get(locale, "milebymile-discard-card"),
            ["junk_card"],
            state=KeybindState.ACTIVE,
        )

    def _update_card_actions(self, player: MileByMilePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        # Remove old card actions and ensure they're removed from _order
        # Note: HAND_SIZE + 2 to account for the card drawn at start of turn
        for i in range(1, HAND_SIZE + 2):
            action_id = f"card_slot_{i}"
            if turn_set.get_action(action_id):
                turn_set.remove(action_id)
            # Also ensure it's not lingering in _order
            if action_id in turn_set._order:
                turn_set._order.remove(action_id)

        # Add actions for cards in hand
        for i, card in enumerate(player.hand, 1):
            action_id = f"card_slot_{i}"
            playable = self._can_play_card(player, card)

            # Check if hazard with multiple targets needs menu
            input_request = None
            if card.card_type == CardType.HAZARD and playable:
                targets = self._get_valid_hazard_targets(player, card.value)
                if len(targets) > 1:
                    input_request = MenuInput(
                        prompt="milebymile-select-target",
                        options="_hazard_target_options",
                        bot_select="_bot_select_hazard_target",
                    )

            # Always show cards in menu, but enable/disable based on state
            # Use dynamic label to ensure locale changes are reflected
            turn_set.add(
                Action(
                    id=action_id,
                    label="",  # Fallback, dynamic label used instead
                    handler="_action_play_card",
                    is_enabled="_is_card_action_enabled",
                    is_hidden="_is_card_action_hidden",
                    get_label="_get_card_slot_label",
                    input_request=input_request,
                )
            )

        # Move check_status to the end (after card actions)
        if "check_status" in turn_set._order:
            turn_set._order.remove("check_status")
            turn_set._order.append("check_status")

        # WEB-SPECIFIC: 
        # 1. Force dirty_trick to the top
        # 2. Force info to the bottom (below cards)
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if "dirty_trick" in turn_set._order:
                turn_set._order.remove("dirty_trick")
                turn_set._order.insert(0, "dirty_trick")
            
            # Ensure info is at the end (after cards)
            if "info" in turn_set._order:
                turn_set._order.remove("info")
                turn_set._order.append("info")

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_status_enabled(self, player: Player) -> str | None:
        """Check if check status action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        """Check status is always hidden (triggered by keybind only), unless Web."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_detailed_status_hidden(self, player: Player) -> Visibility:
        """Detailed status is always hidden (in overflow menu)."""
        return Visibility.HIDDEN

    def _is_dirty_trick_enabled(self, player: Player) -> str | None:
        """Check if dirty trick action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        
        # WEB-SPECIFIC: Identify client type
        user = self.get_user(player)
        is_web = user and getattr(user, "client_type", "") == "web"

        mbm_player: MileByMilePlayer = player  # type: ignore
        
        # For web, return None (enabled) so button is 'always light', validation moves to handler
        if is_web:
            return None

        if self.dirty_trick_window_team is None:
            return "milebymile-no-dirty-trick-window"
        if mbm_player.team_index != self.dirty_trick_window_team:
            return "milebymile-not-your-dirty-trick"
        return None

    def _is_dirty_trick_hidden(self, player: Player) -> Visibility:
        """Dirty trick is hidden (keybind only), unless Web."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_junk_card_enabled(self, player: Player) -> str | None:
        """Check if junk card action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        return None

    def _is_junk_card_hidden(self, player: Player) -> Visibility:
        """Junk card is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_card_action_enabled(self, player: Player) -> str | None:
        """Check if card actions are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        return None

    def _is_card_action_hidden(self, player: Player) -> Visibility:
        """Card actions are visible during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_info_hidden(self, player: Player) -> Visibility:
        """Info is visible in Turn Menu for Web, Hidden for Python (Access via Action Menu/Keybind)."""
        user = self.get_user(player)
        # Web: Show in Turn Menu
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        
        # Python: Hide from Turn Menu (use Action Menu instead)
        return Visibility.HIDDEN

    def _get_card_slot_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for a card slot action."""
        if not isinstance(player, MileByMilePlayer):
            return ""
        # Extract slot number from action_id (e.g., "card_slot_1" -> 0)
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return ""
        if slot < 0 or slot >= len(player.hand):
            return ""
        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._get_localized_card_name(card, locale)

    def _update_turn_actions(self, player: MileByMilePlayer) -> None:
        """Update dynamic card actions for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update card actions for all players."""
        for player in self.players:
            self._update_turn_actions(player)

    # ==========================================================================
    # Card Logic
    # ==========================================================================

    def _can_play_card(self, player: MileByMilePlayer, card: Card) -> bool:
        """Check if a card can be played."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return False

        if card.card_type == CardType.DISTANCE:
            return self._can_play_distance(race_state, card)
        elif card.card_type == CardType.HAZARD:
            return self._can_play_hazard(player, card)
        elif card.card_type == CardType.REMEDY:
            return self._can_play_remedy(race_state, card)
        elif card.card_type == CardType.SAFETY:
            return not race_state.has_safety(card.value)
        elif card.card_type == CardType.SPECIAL:
            if card.value == "false_virtue":
                return not race_state.has_karma
        return False

    def _get_unplayable_reason(
        self, player: MileByMilePlayer, card: Card, locale: str = "en"
    ) -> str:
        """Get a human-readable reason why a card can't be played."""


        race_state = self.get_player_race_state(player)
        if not race_state:
            return Localization.get(locale, "milebymile-reason-not-on-team")

        if card.card_type == CardType.DISTANCE:
            distance = card.distance
            if not race_state.can_play_distance():
                if race_state.has_problem(HazardType.STOP):
                    return Localization.get(locale, "milebymile-reason-stopped")
                return Localization.get(locale, "milebymile-reason-has-problem")
            if race_state.has_problem(HazardType.SPEED_LIMIT) and distance > 50:
                return Localization.get(locale, "milebymile-reason-speed-limit")
            if self.options.only_allow_perfect_crossing:
                if race_state.miles + distance > self.options.round_distance:
                    return Localization.get(
                        locale,
                        "milebymile-reason-exceeds-distance",
                        miles=self.options.round_distance,
                    )

        elif card.card_type == CardType.HAZARD:
            return Localization.get(locale, "milebymile-reason-no-targets")

        elif card.card_type == CardType.REMEDY:
            remedy = card.value
            if remedy == RemedyType.END_OF_LIMIT:
                return Localization.get(locale, "milebymile-reason-no-speed-limit")
            if remedy == RemedyType.ROLL:
                if race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                    return Localization.get(
                        locale, "milebymile-reason-has-right-of-way"
                    )
                if not race_state.has_problem(HazardType.STOP):
                    return Localization.get(locale, "milebymile-reason-already-moving")
                # Check for other problems
                for problem in race_state.problems:
                    if problem not in (HazardType.STOP, HazardType.SPEED_LIMIT):
                        problem_name = self._get_localized_problem_name(problem, locale)
                        return Localization.get(
                            locale,
                            "milebymile-reason-must-fix-first",
                            problem=problem_name,
                        )
            if remedy == RemedyType.GASOLINE:
                return Localization.get(locale, "milebymile-reason-has-gas")
            if remedy == RemedyType.SPARE_TIRE:
                return Localization.get(locale, "milebymile-reason-tires-fine")
            if remedy == RemedyType.REPAIRS:
                return Localization.get(locale, "milebymile-reason-no-accident")

        elif card.card_type == CardType.SAFETY:
            return Localization.get(locale, "milebymile-reason-has-safety")

        elif card.card_type == CardType.SPECIAL:
            if card.value == "false_virtue":
                return Localization.get(locale, "milebymile-reason-has-karma")

        return Localization.get(locale, "milebymile-reason-generic")

    def _get_localized_problem_name(self, problem: str, locale: str) -> str:
        """Get localized name for a problem/hazard type."""


        key_map = {
            HazardType.OUT_OF_GAS: "milebymile-card-out-of-gas",
            HazardType.FLAT_TIRE: "milebymile-card-flat-tire",
            HazardType.ACCIDENT: "milebymile-card-accident",
            HazardType.SPEED_LIMIT: "milebymile-card-speed-limit",
            HazardType.STOP: "milebymile-card-stop",
        }
        key = key_map.get(problem, "")
        return Localization.get(locale, key) if key else problem

    def _get_localized_safety_name(self, safety: str, locale: str) -> str:
        """Get localized name for a safety type."""


        key_map = {
            SafetyType.EXTRA_TANK: "milebymile-card-extra-tank",
            SafetyType.PUNCTURE_PROOF: "milebymile-card-puncture-proof",
            SafetyType.DRIVING_ACE: "milebymile-card-driving-ace",
            SafetyType.RIGHT_OF_WAY: "milebymile-card-right-of-way",
        }
        key = key_map.get(safety, "")
        return Localization.get(locale, key) if key else safety

    def _get_localized_card_name(self, card: Card, locale: str) -> str:
        """Get localized name for a card."""


        if card.card_type == CardType.DISTANCE:
            return Localization.get(locale, "milebymile-card-miles", miles=card.value)

        key_map = {
            # Hazards
            HazardType.OUT_OF_GAS: "milebymile-card-out-of-gas",
            HazardType.FLAT_TIRE: "milebymile-card-flat-tire",
            HazardType.ACCIDENT: "milebymile-card-accident",
            HazardType.SPEED_LIMIT: "milebymile-card-speed-limit",
            HazardType.STOP: "milebymile-card-stop",
            # Remedies
            RemedyType.GASOLINE: "milebymile-card-gasoline",
            RemedyType.SPARE_TIRE: "milebymile-card-spare-tire",
            RemedyType.REPAIRS: "milebymile-card-repairs",
            RemedyType.END_OF_LIMIT: "milebymile-card-end-of-limit",
            RemedyType.ROLL: "milebymile-card-green-light",
            # Safeties
            SafetyType.EXTRA_TANK: "milebymile-card-extra-tank",
            SafetyType.PUNCTURE_PROOF: "milebymile-card-puncture-proof",
            SafetyType.DRIVING_ACE: "milebymile-card-driving-ace",
            SafetyType.RIGHT_OF_WAY: "milebymile-card-right-of-way",
            # Special
            "false_virtue": "milebymile-card-false-virtue",
        }
        key = key_map.get(card.value, "")
        return Localization.get(locale, key) if key else card.name

    def _can_play_distance(self, race_state: RaceState, card: Card) -> bool:
        """Check if team can play a distance card."""
        if not race_state.can_play_distance():
            return False

        distance = card.distance

        # Check speed limit
        if race_state.has_problem(HazardType.SPEED_LIMIT) and distance > 50:
            return False

        # Check perfect crossing
        if self.options.only_allow_perfect_crossing:
            if race_state.miles + distance > self.options.round_distance:
                return False

        if distance == 200 and race_state.used_200_mile_count >= 2:
            return False

        return True

    def _can_play_hazard(self, player: MileByMilePlayer, card: Card) -> bool:
        """Check if hazard can be played on any opponent."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return False

        for target_idx, target_state in self.iter_teams():
            if target_idx == player.team_index:
                continue
            if self._can_play_hazard_on_team(card.value, target_state, attacker_state):
                return True
        return False

    def _can_play_hazard_on_team(
        self, hazard: str, target: RaceState, attacker: RaceState
    ) -> bool:
        """Check if hazard can be played on a specific team."""
        # Check if target has blocking safety
        blocking_safety = HAZARD_TO_SAFETY.get(hazard)
        if blocking_safety and target.has_safety(blocking_safety):
            return False

        # Karma rule check
        if self.options.karma_rule:
            if not attacker.has_karma and target.has_karma:
                return False

        # Check for existing problems
        if hazard == HazardType.SPEED_LIMIT:
            # Speed limit just checks for duplicate
            return not target.has_problem(hazard)
        else:
            # Critical hazards: can't stack unless option enabled
            if self.options.allow_stacking_attacks:
                return not target.has_problem(hazard)
            else:
                return not target.has_any_problem()

    def _can_play_remedy(self, race_state: RaceState, card: Card) -> bool:
        """Check if remedy can be played."""
        remedy = card.value

        if remedy == RemedyType.END_OF_LIMIT:
            return race_state.has_problem(HazardType.SPEED_LIMIT)

        if remedy == RemedyType.ROLL:
            # Can't play if have Right of Way
            if race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                return False
            # Must have stop problem
            if not race_state.has_problem(HazardType.STOP):
                return False
            # Can't have other problems (except speed limit)
            for problem in race_state.problems:
                if problem not in (HazardType.STOP, HazardType.SPEED_LIMIT):
                    return False
            return True

        # Specific remedies
        remedy_to_hazard = {
            RemedyType.GASOLINE: HazardType.OUT_OF_GAS,
            RemedyType.SPARE_TIRE: HazardType.FLAT_TIRE,
            RemedyType.REPAIRS: HazardType.ACCIDENT,
        }
        hazard = remedy_to_hazard.get(remedy)
        return hazard and race_state.has_problem(hazard)

    def _get_valid_hazard_targets(
        self, player: MileByMilePlayer, hazard: str
    ) -> list[int]:
        """Get list of team indices that can be targeted by a hazard."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return []

        targets = []
        for target_idx, target_state in self.iter_teams():
            if target_idx == player.team_index:
                continue
            if self._can_play_hazard_on_team(hazard, target_state, attacker_state):
                targets.append(target_idx)
        return targets

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_info(self, player: Player, action_id: str) -> None:
        """Show detailed info about the player/team status."""
        user = self.get_user(player)
        if not user or not isinstance(player, MileByMilePlayer):
            return

        locale = user.locale
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        # Get problems/hazards
        if not race_state.problems:
            hazards_str = Localization.get(locale, "milebymile-none")
        else:
            names = [self._get_localized_problem_name(p, locale) for p in race_state.problems]
            hazards_str = ", ".join(names)

        # Get safeties
        if not race_state.safeties:
            safeties_str = Localization.get(locale, "milebymile-none")
        else:
            names = [self._get_localized_safety_name(s, locale) for s in race_state.safeties]
            safeties_str = ", ".join(names)

        miles = race_state.miles

        if self.is_individual_mode():
            user.speak_l(
                "milebymile-info-msg-individual",
                player=player.name,
                miles=miles,
                hazards=hazards_str,
                safeties=safeties_str,
            )
        else:
            # Team info
            team_idx = player.team_index
            team_name = self.get_team_name(team_idx, locale)
            # Find team members
            if team_idx < len(self._team_manager.teams):
                member_names = ", ".join(self._team_manager.teams[team_idx].members)
            else:
                member_names = player.name

            user.speak_l(
                "milebymile-info-msg-team",
                team=team_name,
                members=member_names,
                miles=miles,
                hazards=hazards_str,
                safeties=safeties_str,
            )

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show game status to player."""
        user = self.get_user(player)
        if not user:
            return



        locale = user.locale
        none_str = Localization.get(locale, "milebymile-none")

        for team_idx, race_state in self.iter_teams():
            name = self.get_team_name(team_idx, locale)

            # Get score
            team = self._team_manager.teams[team_idx] if team_idx < len(self._team_manager.teams) else None
            score = team.total_score if team else 0

            if race_state.problems:
                problems_str = ", ".join(
                    self._get_localized_problem_name(p, locale) for p in race_state.problems
                )
            else:
                problems_str = none_str
            if race_state.safeties:
                safeties_str = ", ".join(
                    self._get_localized_safety_name(s, locale) for s in race_state.safeties
                )
            else:
                safeties_str = none_str

            # Use global score format for consistency
            if self.options.winning_score:
                score_info = Localization.get(
                    locale,
                    "game-score-line-target",
                    player=name,
                    score=score,
                    target=self.options.winning_score,
                )
            else:
                score_info = Localization.get(
                    locale,
                    "game-score-line",
                    player=name,
                    score=score,
                )

            user.speak_l(
                "milebymile-status",
                score_info=score_info,
                miles=race_state.miles,
                problems=problems_str,
                safeties=safeties_str,
            )

    def _action_check_status_detailed(self, player: Player, action_id: str) -> None:
        """Show detailed game status in a status box menu."""
        user = self.get_user(player)
        if not user:
            return



        locale = user.locale
        none_str = Localization.get(locale, "milebymile-none")
        lines = []

        for team_idx, race_state in self.iter_teams():
            name = self.get_team_name(team_idx, locale)

            # Get score
            team = self._team_manager.teams[team_idx] if team_idx < len(self._team_manager.teams) else None
            score = team.total_score if team else 0

            # Format problems
            if race_state.problems:
                problems_str = ", ".join(
                    self._get_localized_problem_name(p, locale) for p in race_state.problems
                )
            else:
                problems_str = none_str

            # Format safeties
            if race_state.safeties:
                safeties_str = ", ".join(
                    self._get_localized_safety_name(s, locale) for s in race_state.safeties
                )
            else:
                safeties_str = none_str

            # Add team status line using uniform format
            # Use global score format for consistency
            if self.options.winning_score:
                score_info = Localization.get(
                    locale,
                    "game-score-line-target",
                    player=name,
                    score=score,
                    target=self.options.winning_score,
                )
            else:
                score_info = Localization.get(
                    locale,
                    "game-score-line",
                    player=name,
                    score=score,
                )
            
            line = Localization.get(
                locale,
                "milebymile-status",
                score_info=score_info,
                miles=race_state.miles,
                problems=problems_str,
                safeties=safeties_str,
            )
            lines.append(line)

        self.status_box(player, lines)

    def _action_dirty_trick(self, player: Player, action_id: str) -> None:
        """Handle dirty trick (Coup Fourré) attempt."""
        if not isinstance(player, MileByMilePlayer):
            return

        # Explicit validation (moved from is_enabled for web clients)
        if self.dirty_trick_window_team is None:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-dirty-trick-window", buffer="game")
            return

        race_state = self.get_player_race_state(player)
        if not race_state or self.dirty_trick_window_team != player.team_index:
             user = self.get_user(player)
             if user:
                 user.speak_l("milebymile-not-your-dirty-trick", buffer="game")
             return

        hazard = self.dirty_trick_window_hazard
        if not hazard:
            return

        # Find matching safety in hand
        blocking_safety = HAZARD_TO_SAFETY.get(hazard)
        if not blocking_safety:
            return

        safety_card = None
        card_index = -1
        for i, card in enumerate(player.hand):
            if card.card_type == CardType.SAFETY and card.value == blocking_safety:
                safety_card = card
                card_index = i
                break

        if not safety_card:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-matching-safety", buffer="game")
            return

        # Play the dirty trick!
        self._play_safety(player, card_index, safety_card, is_dirty_trick=True)

        # Close the window
        self.dirty_trick_window_team = None
        self.dirty_trick_window_hazard = None
        self.dirty_trick_window_ticks = 0

    def _get_target_display_string(self, team_idx: int, race_state: "RaceState", locale: str) -> str:
        """Get localized display string for a target team."""

        
        team = self._team_manager.teams[team_idx]
        if self.is_individual_mode():
            return Localization.get(
                locale, 
                "milebymile-target-individual", 
                name=team.members[0], 
                miles=race_state.miles
            )
        else:
            members = ", ".join(team.members)
            return Localization.get(
                locale, 
                "milebymile-target-team", 
                team=team_idx + 1, 
                members=members, 
                miles=race_state.miles
            )

    def _hazard_target_options(self, player: Player) -> list[str]:
        """Get list of valid hazard target names for menu input."""
        if not isinstance(player, MileByMilePlayer):
            return []

        # Get the pending action to find which card slot
        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return []

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return []

        if slot < 0 or slot >= len(player.hand):
            return []

        card = player.hand[slot]
        if card.card_type != CardType.HAZARD:
            return []

        target_indices = self._get_valid_hazard_targets(player, card.value)
        options = []
        
        user = self.get_user(player)
        locale = user.locale if user else "en"
        
        for team_idx in target_indices:
            race_state = self.race_states[team_idx]
            options.append(self._get_target_display_string(team_idx, race_state, locale))
            
        return options

    def _bot_select_hazard_target(
        self, player: Player, options: list[str]
    ) -> str | None:
        """Bot selects hazard target - picks team with most miles."""
        if not isinstance(player, MileByMilePlayer):
            return None

        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return None

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return None

        if slot < 0 or slot >= len(player.hand):
            return None

        card = player.hand[slot]
        if card.card_type != CardType.HAZARD:
            return None

        target_indices = self._get_valid_hazard_targets(player, card.value)
        if not target_indices:
            return None

        # Pick target with most miles
        best_idx = max(target_indices, key=lambda i: self.race_states[i].miles)
        race_state = self.race_states[best_idx]
        
        # We need to return the string that matches what options would provide
        # But bots don't really have a locale, so existing logic effectively assumes 'en'
        # or the format string match.
        # Since _play_hazard uses the text to lookup, we should match standard behavior.
        # Let's default to English for bots, or maybe the host's locale?
        # A simpler way is to just generate it using 'en' since bot actions 
        # usually pass internal checks, but here the 'input' is the string itself when passed to _action_play_card.
        # Wait, usually bot input is passed directly to _action handler.
        # If _action_play_card expects the string, we need to match it.
        # But bots don't see menus, so they should return the formatted string.
        # Let's use English for safety.
        return self._get_target_display_string(best_idx, race_state, "en")

    def _action_play_card(self, player: Player, *args) -> None:
        """Handle playing a card from hand.

        Can be called as:
        - _action_play_card(player, action_id) - no input
        - _action_play_card(player, input_value, action_id) - with menu input
        """
        if not isinstance(player, MileByMilePlayer):
            return

        # Check if it's this player's turn
        if self.current_player != player:
            return

        # Parse arguments - handler can receive (player, action_id) or (player, input_value, action_id)
        if len(args) == 1:
            action_id = args[0]
            input_value = None
        elif len(args) == 2:
            input_value, action_id = args
        else:
            return

        # Extract slot number from action_id (e.g., "card_slot_1" -> 0)
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]

        if self._can_play_card(player, card):
            self._play_card(player, slot, card, input_value)
        else:
            # Can't play - tell human players why, bots auto-discard
            if player.is_bot:
                self._discard_card(player, slot, card)
            else:
                user = self.get_user(player)
                if user:
                    reason = self._get_unplayable_reason(player, card, user.locale)
                    card_name = self._get_localized_card_name(card, user.locale)
                    user.speak_l("milebymile-cant-play", buffer="game", card=card_name, reason=reason)

    def _action_junk_card(self, player: Player, action_id: str) -> None:
        """Handle discarding the currently selected card (shift+enter or backspace keybind)."""
        if not isinstance(player, MileByMilePlayer):
            return

        # Check if it's this player's turn
        if self.current_player != player:
            return

        # Get the selected menu item from context
        context = self.get_action_context(player)
        menu_item_id = context.menu_item_id

        if not menu_item_id or not menu_item_id.startswith("card_slot_"):
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-card-selected", buffer="game")
            return

        # Extract slot number from menu_item_id
        try:
            slot = int(menu_item_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]



        self._discard_card(player, slot, card)

    def _play_card(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        target_name: str | None = None,
    ) -> None:
        """Play a card from hand."""
        if card.card_type == CardType.DISTANCE:
            self._play_distance(player, slot, card)
        elif card.card_type == CardType.HAZARD:
            self._play_hazard(player, slot, card, target_name)
        elif card.card_type == CardType.REMEDY:
            self._play_remedy(player, slot, card)
        elif card.card_type == CardType.SAFETY:
            self._play_safety(player, slot, card, is_dirty_trick=False)
        elif card.card_type == CardType.SPECIAL:
            self._play_special(player, slot, card)

    def _play_distance(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a distance card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        distance = card.distance
        player.hand.pop(slot)
        race_state.miles += distance

        if distance == 200:
            race_state.used_200_mile_count += 1

        # Play sounds
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

        # Distance-specific sounds
        sound_variants = {25: 2, 50: 3, 75: 3, 100: 3, 200: 3}
        if distance in sound_variants:
            variant = random.randint(1, sound_variants[distance])
            self.play_sound(f"game_milebymile/{distance}miles{variant}.ogg")

        # Announce
        if self.is_individual_mode():
            self.broadcast_l(
                "milebymile-plays-distance-individual",
                player=player.name,
                distance=distance,
                total=race_state.miles,
            )
        else:
            self.broadcast_l(
                "milebymile-plays-distance-team",
                player=player.name,
                distance=distance,
                total=race_state.miles,
            )

        self.discard_pile.append(card)

        # Check for race win
        if race_state.miles >= self.options.round_distance:
            if (
                race_state.miles == self.options.round_distance
                and not self.options.only_allow_perfect_crossing
            ):
                if self.is_individual_mode():
                    self.broadcast_l(
                        "milebymile-journey-complete-perfect-individual",
                        player=player.name,
                    )
                else:
                    self.broadcast_l(
                        "milebymile-journey-complete-perfect-team", team=player.team_index + 1
                    )
            else:
                if self.is_individual_mode():
                    self.broadcast_l(
                        "milebymile-journey-complete-individual", player=player.name
                    )
                else:
                    self.broadcast_l(
                        "milebymile-journey-complete-team", team=player.team_index + 1
                    )

            self.play_sound("game_milebymile/winround.ogg")
            self.race_winner_team_index = player.team_index

        self._end_turn()

    def _play_hazard(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        target_selection: str | None = None,
    ) -> None:
        """Play a hazard card on an opponent."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return

        target_indices = self._get_valid_hazard_targets(player, card.value)
        if not target_indices:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-valid-targets", buffer="game")
            return

        # Find target team index
        target_idx: int | None = None

        if target_selection:
            # Robust matching: generate strings for all valid targets and see which one matches
            user = self.get_user(player)
            # Use English for bots or fallback
            locale = user.locale if user else "en"
            
            for idx in target_indices:
                race_state = self.race_states[idx]
                target_string = self._get_target_display_string(idx, race_state, locale)
                if target_string == target_selection:
                    target_idx = idx
                    break
            
            if target_idx is None:
                # Fallback: if we can't match it (maybe lag?), and there's only one valid target, use it?
                # Or maybe try matching just the name? 
                # For now, strict matching is safest to avoid hitting wrong target.
                return
        elif len(target_indices) == 1:
            target_idx = target_indices[0]
        else:
            # Multiple targets but no selection - shouldn't happen with MenuInput
            target_idx = target_indices[0]

        target_state = self.race_states[target_idx]
        target_team = self._team_manager.teams[target_idx]

        player.hand.pop(slot)

        # Karma rule: handle karma interactions
        attacker_shunned = False
        if self.options.karma_rule:
            if attacker_state.has_karma and target_state.has_karma:
                # Both have karma - attack neutralized
                attacker_state.has_karma = False
                target_state.has_karma = False

                self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

                # First announce the attack
                if self.is_individual_mode():
                    target_name = target_team.members[0]
                    self._broadcast_card_message(
                        "milebymile-plays-hazard-individual",
                        card,
                        player=player.name,
                        target=target_name,
                    )
                else:
                    self._broadcast_card_message(
                        "milebymile-plays-hazard-team",
                        card,
                        player=player.name,
                        team=target_idx + 1,
                    )

                # Then announce neutralization with personalized messages
                self._announce_karma_clash(player, player.team_index, target_idx)

                self.discard_pile.append(card)
                self._end_turn()
                return

            elif attacker_state.has_karma and not target_state.has_karma:
                # Attacker loses karma
                attacker_state.has_karma = False
                attacker_shunned = True

        # Apply hazard
        target_state.battle_pile.append(card)
        target_state.add_problem(card.value)

        # All hazards except speed limit also add stop
        if card.value != HazardType.SPEED_LIMIT:
            if not target_state.has_safety(SafetyType.RIGHT_OF_WAY):
                target_state.add_problem(HazardType.STOP)

        # Announce
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

        # Hazard-specific sounds
        hazard_sounds = {
            HazardType.ACCIDENT: f"game_milebymile/crash{random.randint(1, 2)}.ogg",
            HazardType.OUT_OF_GAS: "game_milebymile/outofgas.ogg",
            HazardType.FLAT_TIRE: "game_milebymile/flat.ogg",
            HazardType.STOP: "game_milebymile/stop.ogg",
            HazardType.SPEED_LIMIT: "game_milebymile/speedlimit.ogg",
        }
        if card.value in hazard_sounds:
            self.play_sound(hazard_sounds[card.value])

        if self.is_individual_mode():
            target_name = target_team.members[0]
            self._broadcast_card_message(
                "milebymile-plays-hazard-individual",
                card,
                player=player.name,
                target=target_name,
            )
        else:
            self._broadcast_card_message(
                "milebymile-plays-hazard-team",
                card,
                player=player.name,
                team=target_idx + 1,
            )

        # Announce karma loss (personalized)
        if attacker_shunned:
            self._announce_attacker_shunned(player, player.team_index)

        # Open dirty trick window
        self.dirty_trick_window_team = target_idx
        self.dirty_trick_window_hazard = card.value
        self.dirty_trick_window_ticks = 140  # 7 seconds at 20 ticks/sec

        # Schedule bot dirty trick check
        for member_name in target_team.members:
            member = self._get_player_by_name(member_name)
            if member and member.is_bot:
                BotHelper.jolt_bot(member, ticks=random.randint(12, 18))

        self._end_turn()

    def _play_remedy(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a remedy card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)
        race_state.battle_pile.append(card)

        remedy = card.value
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

        if remedy == RemedyType.END_OF_LIMIT:
            race_state.remove_problem(HazardType.SPEED_LIMIT)
            self.play_sound("game_milebymile/speedlimitend.ogg")
        elif remedy == RemedyType.ROLL:
            race_state.remove_problem(HazardType.STOP)
            self.play_sound(f"game_milebymile/greenlight{random.randint(1, 3)}.ogg")
        elif remedy == RemedyType.GASOLINE:
            race_state.remove_problem(HazardType.OUT_OF_GAS)
            self.play_sound("game_milebymile/gas.ogg")
        elif remedy == RemedyType.SPARE_TIRE:
            race_state.remove_problem(HazardType.FLAT_TIRE)
            self.play_sound("game_milebymile/sparetyre.ogg")
        elif remedy == RemedyType.REPAIRS:
            race_state.remove_problem(HazardType.ACCIDENT)
            self.play_sound(f"game_milebymile/repair{random.randint(1, 2)}.ogg")

        self._broadcast_card_message("milebymile-plays-card", card, player=player.name)
        self.discard_pile.append(card)
        self._end_turn()

    def _play_safety(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        is_dirty_trick: bool = False,
    ) -> None:
        """Play a safety card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)
        race_state.add_safety(card.value)

        if is_dirty_trick:
            race_state.dirty_trick_count += 1
            self._broadcast_card_message(
                "milebymile-plays-dirty-trick", card, player=player.name
            )
            self.play_sound("mention.ogg")

            # Remove the hazard that triggered this
            hazard = SAFETY_TO_HAZARD.get(card.value)
            if hazard:
                race_state.remove_problem(hazard)
            if card.value == SafetyType.RIGHT_OF_WAY:
                race_state.remove_problem(HazardType.SPEED_LIMIT)
                race_state.remove_problem(HazardType.STOP)

            # Clean up remaining stop if no other problems
            if len(race_state.problems) == 1 and HazardType.STOP in race_state.problems:
                race_state.remove_problem(HazardType.STOP)
        else:
            self._broadcast_card_message(
                "milebymile-plays-card", card, player=player.name
            )
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

            # Safety-specific sounds
            safety_sounds = {
                SafetyType.DRIVING_ACE: "game_milebymile/drivingace.ogg",
                SafetyType.EXTRA_TANK: f"game_milebymile/extratank{random.randint(1, 2)}.ogg",
                SafetyType.PUNCTURE_PROOF: "game_milebymile/punctureproof.ogg",
                SafetyType.RIGHT_OF_WAY: "game_milebymile/rightofway.ogg",
            }
            if card.value in safety_sounds:
                self.play_sound(safety_sounds[card.value])

            # Remove matching problem
            hazard = SAFETY_TO_HAZARD.get(card.value)
            if hazard:
                race_state.remove_problem(hazard)
            if card.value == SafetyType.RIGHT_OF_WAY:
                race_state.remove_problem(HazardType.SPEED_LIMIT)
                race_state.remove_problem(HazardType.STOP)

        # Safety cards go to protections pile (never reshuffled)
        self.protections_pile.append(card)

        # Safety grants extra turn - draw replacement and continue
        new_card = self._draw_card(player)
        if new_card:
            player.hand.append(new_card)
            user = self.get_user(player)
            if user:
                card_name = self._get_localized_card_name(new_card, user.locale)
                user.speak_l("milebymile-you-drew", buffer="game", card=card_name)

        self._update_turn_actions(player)
        self.rebuild_player_menu(player)
        # Don't end turn - safety grants extra turn

        # Jolt bot to think about next play
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))

    def _play_special(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a special card (False Virtue)."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)

        if card.value == "false_virtue":
            race_state.has_karma = True
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

            # Personalized messages like v10
            self._announce_false_virtue(player, player.team_index)

        self.protections_pile.append(card)
        self._end_turn()

    def _discard_card(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Discard a card."""
        player.hand.pop(slot)

        # Safety cards go to protections to prevent reshuffling
        if card.card_type == CardType.SAFETY:
            self.protections_pile.append(card)
        else:
            self.discard_pile.append(card)

        self.broadcast_l("milebymile-discards", player=player.name)
        self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")
        self._end_turn()

    # ==========================================================================
    # Deck Management
    # ==========================================================================

    def _draw_card(self, player: MileByMilePlayer) -> Card | None:
        """Draw a card for a player."""
        if self.deck.is_empty():
            if not self.discard_pile or not self.options.reshuffle_discard_pile:
                return None
            # Reshuffle discard pile
            self.deck.add_all(self.discard_pile)
            self.discard_pile = []
            self.deck.shuffle()
            self.broadcast_l("milebymile-deck-reshuffled")
            self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")

        if self.options.rig_game == "no_duplicates":
            return self.deck.draw_non_duplicate(player.hand)
        return self.deck.draw()

    def _deal_initial_hands(self) -> None:
        """Deal initial hands to all players."""
        active_players = self.get_active_players()
        for player in active_players:
            player.hand = []
            for _ in range(HAND_SIZE):
                card = self._draw_card(player)
                if card:
                    player.hand.append(card)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        # Always set up teams to ensure we have the latest player list
        # (needed for karma rule validation and proper team count)
        self._setup_teams()

        # Validate team mode for current player count
        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)

        # Check karma rule requirement: need at least 3 teams/cars
        if self.options.karma_rule:
            num_teams = len(self._team_manager.teams)
            if num_teams < 3:
                errors.append("milebymile-error-karma-needs-three-teams")

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        # Ensure teams are set up (normally done in prestart_validate, but handle direct calls)
        if not self._team_manager.teams:
            self._setup_teams()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.current_race = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Play music and ambience
        self.play_music("game_milebymile/music.ogg")
        self.play_ambience("game_milebymile/amloop.ogg")

        # Start first race
        self._start_race()

    def _start_race(self) -> None:
        """Start a new race."""
        self.current_race += 1
        self.race_winner_team_index = None

        # Reset race states for new race
        for race_state in self.race_states:
            race_state.reset()

        # Build and shuffle deck
        attack_mult = 2 if self.options.rig_game == "2x_attacks" else 1
        defense_mult = 2 if self.options.rig_game == "2x_defenses" else 1
        self.deck = Deck()
        self.deck.build_standard_deck(
            attack_multiplier=attack_mult,
            defense_multiplier=defense_mult,
            include_karma_cards=self.options.karma_rule,
        )
        self.deck.shuffle()

        self.discard_pile = []
        self.protections_pile = []

        # Deal hands
        self._deal_initial_hands()

        # Play shuffle sound (like Scopa)
        shuffle_sound = random.choice(["shuffle1.ogg", "shuffle2.ogg", "shuffle3.ogg"])
        self.play_sound(f"game_cards/{shuffle_sound}")
        self.broadcast_l("milebymile-new-race")

        # Start first turn
        self.reset_turn_order()
        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, MileByMilePlayer):
            return

        # Draw a card at start of turn
        card = self._draw_card(player)
        if card:
            player.hand.append(card)
            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
            user = self.get_user(player)
            if user:
                card_name = self._get_localized_card_name(card, user.locale)
                user.speak_l("milebymile-you-drew", buffer="game", card=card_name)

        # Announce turn
        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Don't process turns during countdown
        if self._round_timer.is_active:
            return

        # Check for race end
        if self.race_winner_team_index is not None:
            self._end_race()
            return

        # Check for deck exhaustion (when reshuffling is disabled)
        if self.deck.is_empty() and not self.options.reshuffle_discard_pile:
            # No cards left to draw and can't reshuffle - check if all hands empty
            all_empty = all(len(p.hand) == 0 for p in self.get_active_players())
            if all_empty:
                self._end_race()
                return

        # Advance to next player
        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))
        self.advance_turn(announce=False)
        self._start_turn()

    def _end_race(self) -> None:
        """End the current race and calculate scores."""
        # Find winner (team index with most miles if no one reached target)
        winning_team_idx: int | None = self.race_winner_team_index
        if winning_team_idx is None:
            # Find team with most miles
            max_miles = -1
            for team_idx, race_state in self.iter_teams():
                if race_state.miles > max_miles:
                    max_miles = race_state.miles
                    winning_team_idx = team_idx

        self.broadcast_l("milebymile-race-complete")

        # Calculate and announce scores
        self._calculate_race_scores(winning_team_idx)

        # Check for game winner
        game_winner = self._check_game_winner()
        if game_winner is not None:
            self._end_game(game_winner)
        else:
            # Start next race after delay (silent countdown)
            self._round_timer.start()
            # Disable all actions during countdown
            self._update_all_turn_actions()
            self.rebuild_all_menus()

    def on_round_timer_ready(self) -> None:
        """Called when round timer expires - start the next race."""
        self._start_race()

    def _calculate_race_scores(self, winning_team_idx: int | None) -> None:
        """Calculate and announce race scores."""


        for team_idx, race_state in self.iter_teams():
            base_miles = min(race_state.miles, self.options.round_distance)
            score = base_miles
            # Store bonus keys and their parameters for localization
            bonus_parts: list[tuple[str, dict]] = []  # (message_key, params)

            is_winner = team_idx == winning_team_idx
            if is_winner and race_state.miles >= self.options.round_distance:
                # Trip complete bonus
                score += 400
                bonus_parts.append(("milebymile-from-trip", {"points": 400}))

                # Perfect crossing (only if not forced)
                if not self.options.only_allow_perfect_crossing:
                    if race_state.miles == self.options.round_distance:
                        score += 200
                        bonus_parts.append(("milebymile-from-perfect", {"points": 200}))

                # Safe trip (no 200s)
                if race_state.used_200_mile_count == 0:
                    score += 300
                    bonus_parts.append(("milebymile-from-safe", {"points": 300}))

                # Shut out
                if all(rs.miles == 0 for i, rs in self.iter_teams() if i != team_idx):
                    score += 500
                    bonus_parts.append(("milebymile-from-shutout", {"points": 500}))

            # Safety bonuses (all teams)
            safety_count = len(race_state.safeties)
            if safety_count > 0:
                safety_bonus = safety_count * 100
                score += safety_bonus
                bonus_parts.append(
                    (
                        "milebymile-from-safeties",
                        {"points": safety_bonus, "count": safety_count},
                    )
                )

            # All 4 safeties bonus
            if safety_count == 4:
                score += 300
                bonus_parts.append(("milebymile-from-all-safeties", {"points": 300}))

            # Dirty trick bonuses
            if race_state.dirty_trick_count > 0:
                dt_bonus = race_state.dirty_trick_count * 300
                score += dt_bonus
                bonus_parts.append(
                    (
                        "milebymile-from-dirty-tricks",
                        {"points": dt_bonus, "count": race_state.dirty_trick_count},
                    )
                )

            self.set_team_round_score(team_idx, score)
            self.add_team_score(team_idx, score)

            # Announce to each player in their locale
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                locale = user.locale
                name = self.get_team_name(team_idx, locale)

                # Build localized bonus descriptions
                bonus_descriptions = [
                    Localization.get(
                        locale, "milebymile-from-distance", miles=base_miles
                    )
                ]
                for key, params in bonus_parts:
                    bonus_descriptions.append(Localization.get(locale, key, **params))

                # Format list with babel via Localization wrapper
                breakdown = Localization.format_list_and(locale, bonus_descriptions)
                user.speak_l(
                    "milebymile-earned-points",
                    name=name,
                    score=score,
                    breakdown=breakdown,
                )

        # Announce total scores
        self.broadcast_l("milebymile-total-scores")
        for team_idx in range(self.get_num_teams()):
            # Manually broadcast to support per-user localization of team name
            for p in self.players:
                user = self.get_user(p)
                if user:
                    name = self.get_team_name(team_idx, user.locale)
                    user.speak_l("milebymile-team-score", buffer="game", name=name, score=self.get_team_score(team_idx))

    def _check_game_winner(self) -> int | None:
        """Check if any team has won the game. Returns team index or None."""
        for team_idx in range(self.get_num_teams()):
            if self.get_team_score(team_idx) >= self.options.winning_score:
                # Find team with highest score
                best_idx = team_idx
                for other_idx in range(self.get_num_teams()):
                    if self.get_team_score(other_idx) > self.get_team_score(best_idx):
                        best_idx = other_idx
                return best_idx
        return None

    def _end_game(self, winner_idx: int) -> None:
        """End the game with a winner."""
        self.play_sound("game_pig/win.ogg")

        winner_team = self._team_manager.teams[winner_idx]
        winner_score = self.get_team_score(winner_idx)

        if self.is_individual_mode():
            self.broadcast_l("milebymile-wins-individual", player=winner_team.members[0])
        else:
            members_str = ", ".join(winner_team.members)
            self.broadcast_l(
                "milebymile-wins-team", team=winner_idx + 1, members=members_str
            )
        self.broadcast_l("milebymile-final-score", score=winner_score)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with MileByMile-specific data."""
        # Sort teams by score descending
        team_scores = [(i, self.get_team_score(i)) for i in range(self.get_num_teams())]
        sorted_teams = sorted(team_scores, key=lambda t: t[1], reverse=True)

        # Build final scores
        final_scores = {}
        for team_idx, score in sorted_teams:
            # Store team index as key for dynamic localization in format_end_screen
            # We use string of index because JSON keys must be strings
            final_scores[str(team_idx)] = score

        winner_idx, winner_score = sorted_teams[0] if sorted_teams else (0, 0)
        winner_name = self.get_team_name(winner_idx)

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                )
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner_name,
                "winner_score": winner_score,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "target_score": self.options.round_distance,
                "team_mode": self.options.team_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for MileByMile game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        # Sort by points descending (though usually they are stored sorted, dict order isn't guaranteed in all py versions/json)
        # But we preserved order in build_game_result, and py3.7+ dicts preserve insertion order.
        # Let's trust insertion order or re-sort if needed. Since it comes from JSON, it *should* be fine if stored as list of tuples,
        # but here it's a dict.
        
        # safely re-sort just in case
        sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        for i, (key, score) in enumerate(sorted_scores, 1):
            # Resolve name: if key is digit, it's a team index. Else it's a legacy name.
            if key.isdigit():
                team_idx = int(key)
                name = self.get_team_name(team_idx, locale)
            else:
                name = key

            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(locale, "milebymile-line-format", rank=i, name=name, points=points_str)
            )

        return lines

    def _get_player_by_name(self, name: str) -> MileByMilePlayer | None:
        """Get a player by name."""
        for player in self.players:
            if player.name == name:
                return player
        return None

    # ==========================================================================
    # Karma Announcements (personalized per player like v10)
    # ==========================================================================

    def _announce_karma_clash(
        self,
        attacker: MileByMilePlayer,
        attacker_team_idx: int,
        target_team_idx: int,
    ) -> None:
        """Announce when both attacker and target lose karma (attack neutralized)."""
        if self.is_individual_mode():
            target_team = self._team_manager.teams[target_team_idx]
            target_name = target_team.members[0]
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == attacker:
                    user.speak_l("milebymile-karma-clash-you-target", buffer="game")
                elif p.name == target_name:
                    user.speak_l(
                        "milebymile-karma-clash-you-attacker", attacker=attacker.name
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-others",
                        attacker=attacker.name,
                        target=target_name,
                    )
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-clash-your-team", buffer="game")
                elif p.team_index == target_team_idx:
                    user.speak_l(
                        "milebymile-karma-clash-target-team",
                        team=attacker_team_idx + 1,
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-other-teams",
                        attacker=attacker_team_idx + 1,
                        target=target_team_idx + 1,
                    )

    def _announce_attacker_shunned(
        self, attacker: MileByMilePlayer, attacker_team_idx: int
    ) -> None:
        """Announce when attacker loses karma for attacking."""
        if self.is_individual_mode():
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == attacker:
                    user.speak_l("milebymile-karma-shunned-you", buffer="game")
                else:
                    user.speak_l("milebymile-karma-shunned-other", buffer="game", player=attacker.name)
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-shunned-your-team", buffer="game")
                else:
                    user.speak_l(
                        "milebymile-karma-shunned-other-team",
                        team=attacker_team_idx + 1,
                    )

    def _announce_false_virtue(
        self, player: MileByMilePlayer, team_idx: int
    ) -> None:
        """Announce when a player plays False Virtue to regain karma."""
        if self.is_individual_mode():
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == player:
                    user.speak_l("milebymile-false-virtue-you", buffer="game")
                else:
                    user.speak_l("milebymile-false-virtue-other", buffer="game", player=player.name)
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == team_idx:
                    user.speak_l("milebymile-false-virtue-your-team", buffer="game")
                else:
                    user.speak_l(
                        "milebymile-false-virtue-other-team", team=team_idx + 1
                    )

    def _broadcast_card_message(self, message_key: str, card: Card, **kwargs) -> None:
        """Broadcast a message with a localized card name to all players."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            card_name = self._get_localized_card_name(card, user.locale)
            user.speak_l(message_key, buffer="game", card=card_name, **kwargs)

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        # Handle round timer
        self._round_timer.on_tick()

        # Handle dirty trick window
        if self.dirty_trick_window_ticks > 0:
            self.dirty_trick_window_ticks -= 1
            if self.dirty_trick_window_ticks <= 0:
                self.dirty_trick_window_team = None
                self.dirty_trick_window_hazard = None

        BotHelper.on_tick(self)

    def bot_think(self, player: MileByMilePlayer) -> str | None:
        """Bot AI decision making."""
        # Don't act during between-race countdown
        if self._round_timer.is_active:
            return None

        # Check for dirty trick opportunity first
        if self.dirty_trick_window_team is not None:
            if player.team_index == self.dirty_trick_window_team:
                hazard = self.dirty_trick_window_hazard
                blocking_safety = HAZARD_TO_SAFETY.get(hazard) if hazard else None
                if blocking_safety:
                    for card in player.hand:
                        if (
                            card.card_type == CardType.SAFETY
                            and card.value == blocking_safety
                        ):
                            return "dirty_trick"

        # Not our turn? Skip
        if self.current_player != player:
            return None

        # Choose best card to play
        return self._bot_choose_card(player)

    def _bot_choose_card(self, player: MileByMilePlayer) -> str | None:
        """Bot card selection logic."""
        if not player.hand:
            return None

        race_state = self.get_player_race_state(player)
        if not race_state:
            return None

        target_distance = self.options.round_distance
        distance_needed = target_distance - race_state.miles
        is_endgame = distance_needed <= 200

        # Score each card
        best_slot = 0
        best_priority = -1

        for i, card in enumerate(player.hand):
            priority = self._bot_score_card(
                player, card, race_state, distance_needed, is_endgame
            )
            if priority > best_priority:
                best_priority = priority
                best_slot = i

        return f"card_slot_{best_slot + 1}"

    def _bot_score_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        race_state: RaceState,
        distance_needed: int,
        is_endgame: bool,
    ) -> int:
        """Score a card for bot decision making."""
        if card.card_type == CardType.DISTANCE:
            if not self._can_play_card(player, card):
                return 100

            distance = card.distance
            if is_endgame:
                if distance == distance_needed:
                    return 5000  # Perfect finish
                elif distance > distance_needed:
                    if self.options.only_allow_perfect_crossing:
                        return 50
                    return 4000  # Finish anyway
                else:
                    return 1000 + distance
            return 1000 + distance

        elif card.card_type == CardType.REMEDY:
            if card.value == RemedyType.ROLL and race_state.has_problem(HazardType.STOP):
                if not race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                    return 3000
            if card.value == RemedyType.END_OF_LIMIT and race_state.has_problem(
                HazardType.SPEED_LIMIT
            ):
                return 2800
            if self._can_play_card(player, card):
                return 2500
            return 150

        elif card.card_type == CardType.SAFETY:
            if race_state.has_safety(card.value):
                return 50
            if is_endgame and distance_needed <= 100:
                return 1500
            return 2000

        elif card.card_type == CardType.HAZARD:
            if not self._can_play_card(player, card):
                return 200
            if self.options.karma_rule and race_state.has_karma:
                # Prefer not attacking if we have karma and can play distance
                has_playable_distance = any(
                    c.card_type == CardType.DISTANCE and self._can_play_card(player, c)
                    for c in player.hand
                )
                if has_playable_distance:
                    return 50
            return 800

        elif card.card_type == CardType.SPECIAL:
            if card.value == "false_virtue" and not race_state.has_karma:
                return 1800
            return 50

        return 100
