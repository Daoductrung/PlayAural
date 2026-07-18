"""
Mile by Mile Game Implementation.

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
from ...users.base import EscapeBehavior, MenuItem

from .bot import MileByMileBotStrategy
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
from .state import DirtyTrickWindow, RaceState, is_critical_problem

# Hand size
HAND_SIZE = 6
DIRTY_TRICK_WINDOW_TICKS = 7 * 20
UNPLAYABLE_REASON_OPTION = "read_unplayable_reason"
UNPLAYABLE_DISCARD_OPTION = "discard_unplayable_card"


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
    race_completed_after_deck_exhausted: bool = False

    # Dirty trick windows. The singular fields mirror the newest window for
    # backward-compatible save restoration.
    dirty_trick_windows: list[DirtyTrickWindow] = field(default_factory=list)
    dirty_trick_bonus_turn_player_ids: list[str] = field(default_factory=list)
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
        self._legacy_dirty_trick_turn_advance = False
        self._migrate_legacy_dirty_trick_window()

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()
        self._round_timer = RoundTimer(self, delay_seconds=10.0)
        self._migrate_legacy_dirty_trick_window()
        if self._legacy_dirty_trick_turn_advance:
            self._legacy_dirty_trick_turn_advance = False
            self._end_turn()

    @classmethod
    def get_name(cls) -> str:
        return "Mile by Mile"

    @classmethod
    def get_type(cls) -> str:
        return "milebymile"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 9

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

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
        self._setup_team_manager_for_start(self.options.team_mode, active_players)

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

    def _format_status_score_info(self, name: str, score: int, locale: str) -> str:
        """Format a localized score segment for status readouts."""
        target = self.options.winning_score
        unit_count = target if target else score
        unit = Localization.get(locale, self.get_score_unit_key(), count=unit_count)
        if target:
            return Localization.get(
                locale,
                "game-score-line-target",
                player=name,
                score=score,
                target=target,
                unit=unit,
            )
        return Localization.get(
            locale,
            "game-score-line",
            player=name,
            score=score,
            unit=unit,
        )

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

    def _broadcast_actor_l(
        self,
        actor: MileByMilePlayer,
        personal_message_id: str,
        others_message_id: str,
        **kwargs,
    ) -> None:
        """Broadcast first-person text to the actor and third-person text to others."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener == actor:
                user.speak_l(personal_message_id, buffer="game", **kwargs)
            else:
                user.speak_l(
                    others_message_id,
                    buffer="game",
                    player=actor.name,
                    **kwargs,
                )

    def _broadcast_actor_card_l(
        self,
        actor: MileByMilePlayer,
        personal_message_id: str,
        others_message_id: str,
        card: Card,
        **kwargs,
    ) -> None:
        """Broadcast a localized card line with actor-aware wording."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            card_name = self._get_localized_card_name(card, user.locale)
            if listener == actor:
                user.speak_l(
                    personal_message_id,
                    buffer="game",
                    card=card_name,
                    **kwargs,
                )
            else:
                user.speak_l(
                    others_message_id,
                    buffer="game",
                    player=actor.name,
                    card=card_name,
                    **kwargs,
                )

    def _broadcast_actor_team_l(
        self,
        actor: MileByMilePlayer,
        personal_message_id: str,
        teammate_message_id: str,
        opponent_message_id: str,
        **kwargs,
    ) -> None:
        """Broadcast an action with actor, teammate, and opponent perspectives."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener == actor:
                key = personal_message_id
                params = kwargs
            elif (
                isinstance(listener, MileByMilePlayer)
                and not listener.is_spectator
                and listener.team_index == actor.team_index
            ):
                key = teammate_message_id
                params = {"player": actor.name, **kwargs}
            else:
                key = opponent_message_id
                params = {"player": actor.name, **kwargs}
            user.speak_l(key, buffer="game", **params)

    def _broadcast_actor_team_card_l(
        self,
        actor: MileByMilePlayer,
        personal_message_id: str,
        teammate_message_id: str,
        opponent_message_id: str,
        card: Card,
        **kwargs,
    ) -> None:
        """Broadcast a localized card with team-aware listener wording."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            params = {
                "card": self._get_localized_card_name(card, user.locale),
                **kwargs,
            }
            if listener == actor:
                key = personal_message_id
            elif (
                isinstance(listener, MileByMilePlayer)
                and not listener.is_spectator
                and listener.team_index == actor.team_index
            ):
                key = teammate_message_id
                params["player"] = actor.name
            else:
                key = opponent_message_id
                params["player"] = actor.name
            user.speak_l(key, buffer="game", **params)

    def _broadcast_team_l(
        self,
        team_index: int,
        personal_message_id: str,
        others_message_id: str,
        **kwargs,
    ) -> None:
        """Broadcast first-person text to a team and third-person text to others."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if (
                isinstance(listener, MileByMilePlayer)
                and not listener.is_spectator
                and listener.team_index == team_index
            ):
                user.speak_l(personal_message_id, buffer="game", **kwargs)
            else:
                user.speak_l(others_message_id, buffer="game", **kwargs)

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: MileByMilePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Card slot actions will be dynamically added/removed

        # Dirty trick action (hidden, triggered by keybind)
        action_set.add(
            Action(
                id="dirty_trick",
                label=Localization.get(locale, "milebymile-dirty-trick"),
                handler="_action_dirty_trick",
                is_enabled="_is_dirty_trick_enabled",
                is_hidden="_is_dirty_trick_hidden",
                show_in_actions_menu=False,
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
                show_in_actions_menu=False,
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = [
        "info",
        "check_status",
        "check_status_detailed",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Remove redundant score actions (superseded by check_status)
        if action_set.get_action("check_scores"):
            action_set.remove("check_scores")
        if action_set.get_action("check_scores_detailed"):
            action_set.remove("check_scores_detailed")

        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "milebymile-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_status_detailed",
                label=Localization.get(locale, "milebymile-detailed-status"),
                handler="_action_check_status_detailed",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_detailed_status_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="info",
                label=Localization.get(locale, "milebymile-info-button"),
                handler="_action_info",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)

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

            # Check if this card needs an action input menu.
            input_request = None
            if not playable:
                input_request = MenuInput(
                    prompt="milebymile-unplayable-card-menu-title",
                    options="_unplayable_card_options",
                    bot_select="_bot_select_unplayable_card",
                    pre_input_check="_pre_input_check_unplayable_card",
                    option_label="_unplayable_card_option_label",
                )
            elif card.card_type == CardType.HAZARD:
                targets = self._get_valid_hazard_targets(player, card.value)
                if len(targets) > 1:
                    input_request = MenuInput(
                        prompt="milebymile-select-target",
                        options="_hazard_target_options",
                        bot_select="_bot_select_hazard_target",
                        pre_input_check="_pre_input_check_card_target_selection",
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
                    show_in_actions_menu=False,
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
        if self.is_touch_client(user):
            if "dirty_trick" in turn_set._order:
                turn_set._order.remove("dirty_trick")
                turn_set._order.insert(0, "dirty_trick")

            # Keep touch utility buttons together, with Info before View status.
            if "info" in turn_set._order:
                turn_set._order.remove("info")
                if "check_status" in turn_set._order:
                    turn_set._order.insert(turn_set._order.index("check_status"), "info")
                else:
                    turn_set._order.append("info")

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
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
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_detailed_status_hidden(self, player: Player) -> Visibility:
        """Detailed status is always hidden (in overflow menu)."""
        return Visibility.HIDDEN

    def _is_dirty_trick_enabled(self, player: Player) -> str | None:
        """Check if dirty trick action is enabled."""
        if player.is_spectator:
            return "action-not-playing"

        if self.status != "playing":
            return "action-not-playing"
        
        # WEB-SPECIFIC: Identify client type
        user = self.get_user(player)
        is_touch = self.is_touch_client(user)

        mbm_player: MileByMilePlayer = player  # type: ignore
        
        # For web, return None (enabled) so button is 'always light', validation moves to handler
        if is_touch:
            return None

        if not self.dirty_trick_windows:
            return "milebymile-no-dirty-trick-window"
        if not any(
            window.team_index == mbm_player.team_index
            for window in self.dirty_trick_windows
        ):
            return "milebymile-not-your-dirty-trick"
        return None

    def _is_dirty_trick_hidden(self, player: Player) -> Visibility:
        """Dirty trick is hidden (keybind only), unless Web during active gameplay."""
        if player.is_spectator:
            return Visibility.HIDDEN

        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_junk_card_enabled(self, player: Player) -> str | None:
        """Check if junk card action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_junk_card_hidden(self, player: Player) -> Visibility:
        """Junk card is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_card_action_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | None:
        """Check if card actions are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        return None

    def _pre_input_check_card_target_selection(self, player: Player, action_id: str) -> str | None:
        disabled_reason = self._is_card_action_enabled(player, action_id=action_id)
        if disabled_reason:
            return disabled_reason
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _pre_input_check_unplayable_card(self, player: Player, action_id: str) -> str | None:
        """Validate before opening the unplayable-card discard prompt."""
        if not isinstance(player, MileByMilePlayer):
            return "action-not-playing"
        disabled_reason = self._is_card_action_enabled(player, action_id=action_id)
        if disabled_reason:
            return disabled_reason
        if (
            self.current_player != player
            and not self._action_is_matching_dirty_trick_card(player, action_id)
        ):
            return "action-not-your-turn"
        return None

    def _is_unplayable_card_prompt_action(
        self, player: Player, action_id: str | None
    ) -> bool:
        """Return whether a pending action is a card action using the discard prompt."""
        if not isinstance(player, MileByMilePlayer) or not action_id:
            return False
        action = self.find_action(player, action_id)
        req = action.input_request if action else None
        return isinstance(req, MenuInput) and req.options == "_unplayable_card_options"

    def _get_card_for_action_id(
        self, player: MileByMilePlayer, action_id: str
    ) -> Card | None:
        """Resolve a card-slot action id to the current card in that hand slot."""
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return None
        if 0 <= slot < len(player.hand):
            return player.hand[slot]
        return None

    def _request_action_input(self, action: Action, player: Player) -> None:
        """Request input, with a custom menu for unplayable card discard prompts."""
        req = action.input_request
        if (
            isinstance(player, MileByMilePlayer)
            and isinstance(req, MenuInput)
            and req.options == "_unplayable_card_options"
        ):
            self._request_unplayable_card_input(action, player)
            return
        super()._request_action_input(action, player)

    def _request_unplayable_card_input(
        self, action: Action, player: MileByMilePlayer
    ) -> None:
        """Show a discard prompt with a static reason row and Discard focused."""
        user = self.get_user(player)
        if not user:
            return

        req = action.input_request
        if isinstance(req, MenuInput) and req.pre_input_check:
            pre_input_check = getattr(self, req.pre_input_check, None)
            if pre_input_check:
                disabled_reason = pre_input_check(player, action.id)
                if disabled_reason:
                    user.speak_l(disabled_reason, buffer="game")
                    return

        card = self._get_card_for_action_id(player, action.id)
        if card is None:
            user.speak_l("no-options-available", buffer="game")
            return

        reason_text = Localization.get(
            user.locale,
            "milebymile-unplayable-discard-question",
            card=self._get_localized_card_name(card, user.locale),
            reason=self._get_unplayable_reason(player, card, user.locale),
        )
        user.speak(reason_text, buffer="game")
        self._pending_actions[player.id] = action.id
        return_focus = self._get_action_return_focus_id(player, action.id)
        if return_focus:
            self._pending_action_return_focus[player.id] = return_focus
        user.show_menu(
            "action_input_menu",
            [
                MenuItem(text=reason_text, id=""),
                MenuItem(
                    text=Localization.get(user.locale, "milebymile-discard-card"),
                    id=UNPLAYABLE_DISCARD_OPTION,
                ),
                MenuItem(text=Localization.get(user.locale, "cancel"), id="_cancel"),
            ],
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            selection_id=UNPLAYABLE_DISCARD_OPTION,
        )

    def _handle_menu_event(self, player: Player, event: dict) -> None:
        """Keep static rows in the unplayable-card prompt read-only."""
        if event.get("menu_id") == "action_input_menu":
            selection_id = event.get("selection_id", "")
            action_id = self._pending_actions.get(player.id)
            if (
                selection_id in ("", None)
                and self._is_unplayable_card_prompt_action(player, action_id)
            ):
                return
        super()._handle_menu_event(player, event)

    def _is_card_action_hidden(self, player: Player) -> Visibility:
        """Card actions are visible during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_info_enabled(self, player: Player) -> str | None:
        """Info enabled check."""
        if player.is_spectator:
            return "action-not-playing"
        return self._is_check_status_enabled(player)

    def _is_info_hidden(self, player: Player) -> Visibility:
        """Info is visible in Turn Menu for Web, Hidden for Python (Access via Action Menu/Keybind)."""
        if player.is_spectator:
             return Visibility.HIDDEN

        user = self.get_user(player)
        # Web: Show in Turn Menu
        if self.is_touch_client(user):
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
                specific_problem = self._blocking_driving_problem(race_state)
                if specific_problem:
                    return self._get_problem_block_reason(specific_problem, locale)
                if race_state.has_problem(HazardType.STOP):
                    return Localization.get(locale, "milebymile-reason-stopped")
                return Localization.get(locale, "milebymile-reason-has-problem")
            if self._speed_limit_restricts_distance(race_state) and distance > 50:
                return Localization.get(locale, "milebymile-reason-speed-limit")
            if self.options.only_allow_perfect_crossing:
                if race_state.miles + distance > self.options.round_distance:
                    total = race_state.miles + distance
                    return Localization.get(
                        locale,
                        "milebymile-reason-exceeds-distance",
                        miles=max(0, self.options.round_distance - race_state.miles),
                        current=race_state.miles,
                        distance=distance,
                        total=total,
                        target=self.options.round_distance,
                    )
            if distance == 200 and race_state.used_200_mile_count >= 2:
                return Localization.get(locale, "milebymile-reason-too-many-200s")

        elif card.card_type == CardType.HAZARD:
            return self._get_hazard_unplayable_reason(player, card, locale)

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
                        remedy_name = self._localized_remedy_for_problem(problem, locale)
                        return Localization.get(
                            locale,
                            "milebymile-reason-must-fix-first",
                            problem=problem_name,
                            remedy=remedy_name,
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

    def _blocking_driving_problem(self, race_state: RaceState) -> str | None:
        """Return the highest-priority problem that blocks distance cards."""
        for problem in (
            HazardType.OUT_OF_GAS,
            HazardType.FLAT_TIRE,
            HazardType.ACCIDENT,
        ):
            if race_state.has_problem(problem):
                return problem
        return None

    def _get_problem_block_reason(self, problem: str, locale: str) -> str:
        """Return a specific distance-blocking reason for a hazard."""
        key_map = {
            HazardType.OUT_OF_GAS: "milebymile-reason-out-of-gas",
            HazardType.FLAT_TIRE: "milebymile-reason-flat-tire",
            HazardType.ACCIDENT: "milebymile-reason-accident",
        }
        key = key_map.get(problem)
        if key:
            return Localization.get(locale, key)
        return Localization.get(locale, "milebymile-reason-has-problem")

    def _localized_remedy_for_problem(self, problem: str, locale: str) -> str:
        """Return the localized remedy card name for a hazard."""
        remedy_map = {
            HazardType.OUT_OF_GAS: RemedyType.GASOLINE,
            HazardType.FLAT_TIRE: RemedyType.SPARE_TIRE,
            HazardType.ACCIDENT: RemedyType.REPAIRS,
            HazardType.SPEED_LIMIT: RemedyType.END_OF_LIMIT,
            HazardType.STOP: RemedyType.ROLL,
        }
        remedy = remedy_map.get(problem)
        if not remedy:
            return Localization.get(locale, "milebymile-card-green-light")
        return self._get_localized_card_name(
            Card(id=-1, card_type=CardType.REMEDY, value=remedy),
            locale,
        )

    def _get_hazard_unplayable_reason(
        self,
        player: MileByMilePlayer,
        card: Card,
        locale: str,
    ) -> str:
        """Return a specific reason why a hazard has no legal target."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return Localization.get(locale, "milebymile-reason-not-on-team")

        opponents = [
            target_state
            for target_idx, target_state in self.iter_teams()
            if target_idx != player.team_index
        ]
        if not opponents:
            return Localization.get(locale, "milebymile-reason-no-opponents")

        blocking_safety = HAZARD_TO_SAFETY.get(card.value)
        if blocking_safety and all(
            target.has_safety(blocking_safety) for target in opponents
        ):
            return Localization.get(
                locale,
                "milebymile-reason-hazard-protected",
                card=self._get_localized_card_name(card, locale),
                safety=self._get_localized_safety_name(blocking_safety, locale),
            )

        if self.options.karma_rule and not attacker_state.has_karma and any(
            target.has_karma for target in opponents
        ):
            return Localization.get(locale, "milebymile-reason-hazard-karma")

        if card.value == HazardType.SPEED_LIMIT:
            if all(target.has_problem(HazardType.SPEED_LIMIT) for target in opponents):
                return Localization.get(
                    locale,
                    "milebymile-reason-hazard-duplicate-speed-limit",
                )
        else:
            if all(target.has_problem(card.value) for target in opponents):
                return Localization.get(
                    locale,
                    "milebymile-reason-hazard-duplicate",
                    card=self._get_localized_card_name(card, locale),
                )
            if not self.options.allow_stacking_attacks and all(
                target.has_any_problem() for target in opponents
            ):
                return Localization.get(locale, "milebymile-reason-hazard-blocked")

        return Localization.get(locale, "milebymile-reason-no-targets")

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
        if self._speed_limit_restricts_distance(race_state) and distance > 50:
            return False

        # Check perfect crossing
        if self.options.only_allow_perfect_crossing:
            if race_state.miles + distance > self.options.round_distance:
                return False

        if distance == 200 and race_state.used_200_mile_count >= 2:
            return False

        return True

    @staticmethod
    def _speed_limit_restricts_distance(race_state: RaceState) -> bool:
        """Return whether an active Speed Limit currently limits distance cards."""
        return (
            race_state.has_problem(HazardType.SPEED_LIMIT)
            and not race_state.has_safety(SafetyType.RIGHT_OF_WAY)
        )

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
                buffer="game",
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
                buffer="game",
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

            score_info = self._format_status_score_info(name, score, locale)

            user.speak_l(
                "milebymile-status",
                buffer="game",
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

        self.live_status_box(
            player,
            "milebymile_status",
            lambda _player, live_user: self._detailed_status_lines(live_user.locale),
        )

    def _detailed_status_lines(self, locale: str) -> list[str]:
        lines = []

        none_str = Localization.get(locale, "milebymile-none")

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

            score_info = self._format_status_score_info(name, score, locale)
            
            line = Localization.get(
                locale,
                "milebymile-status",
                score_info=score_info,
                miles=race_state.miles,
                problems=problems_str,
                safeties=safeties_str,
            )
            lines.append(line)

        return lines

    def _migrate_legacy_dirty_trick_window(self) -> None:
        """Restore an active reaction saved before multi-window support."""
        if (
            not self.dirty_trick_windows
            and self.dirty_trick_window_team is not None
            and self.dirty_trick_window_hazard
            and self.dirty_trick_window_ticks > 0
        ):
            self.dirty_trick_windows.append(
                DirtyTrickWindow(
                    team_index=self.dirty_trick_window_team,
                    hazard=self.dirty_trick_window_hazard,
                    ticks=self.dirty_trick_window_ticks,
                )
            )
            self._legacy_dirty_trick_turn_advance = (
                self.game_active and self.status == "playing"
            )
        self._sync_legacy_dirty_trick_window()

    def _sync_legacy_dirty_trick_window(self) -> None:
        """Mirror the newest reaction into the legacy singular fields."""
        if self.dirty_trick_windows:
            newest = self.dirty_trick_windows[-1]
            self.dirty_trick_window_team = newest.team_index
            self.dirty_trick_window_hazard = newest.hazard
            self.dirty_trick_window_ticks = newest.ticks
            return
        self.dirty_trick_window_team = None
        self.dirty_trick_window_hazard = None
        self.dirty_trick_window_ticks = 0
        self._clear_stale_dirty_trick_bot_actions()

    def _open_dirty_trick_window(self, team_index: int, hazard: str) -> None:
        """Open an independent asynchronous response opportunity."""
        for window in self.dirty_trick_windows:
            if window.team_index == team_index and window.hazard == hazard:
                window.ticks = DIRTY_TRICK_WINDOW_TICKS
                self._sync_legacy_dirty_trick_window()
                return
        self.dirty_trick_windows.append(
            DirtyTrickWindow(
                team_index=team_index,
                hazard=hazard,
                ticks=DIRTY_TRICK_WINDOW_TICKS,
            )
        )
        self._sync_legacy_dirty_trick_window()

    def _matching_dirty_trick_window(
        self,
        player: MileByMilePlayer,
        card: Card,
    ) -> DirtyTrickWindow | None:
        """Return the newest reaction that this Safety can answer."""
        if card.card_type != CardType.SAFETY:
            return None
        for window in reversed(self.dirty_trick_windows):
            if (
                window.team_index == player.team_index
                and HAZARD_TO_SAFETY.get(window.hazard) == card.value
            ):
                return window
        return None

    def _action_dirty_trick(self, player: Player, action_id: str) -> None:
        """Handle dirty trick (Coup Fourré) attempt."""
        if not isinstance(player, MileByMilePlayer):
            return

        # Explicit validation (moved from is_enabled for web clients)
        if not self.dirty_trick_windows:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-dirty-trick-window", buffer="game")
            return

        team_windows = [
            window
            for window in self.dirty_trick_windows
            if window.team_index == player.team_index
        ]
        if not team_windows:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-not-your-dirty-trick", buffer="game")
            return

        safety_card = None
        card_index = -1
        selected_window = None
        for window in reversed(team_windows):
            blocking_safety = HAZARD_TO_SAFETY.get(window.hazard)
            for index, card in enumerate(player.hand):
                if (
                    card.card_type == CardType.SAFETY
                    and card.value == blocking_safety
                ):
                    safety_card = card
                    card_index = index
                    selected_window = window
                    break
            if safety_card:
                break

        if not safety_card or not selected_window:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-matching-safety", buffer="game")
            return

        self._play_dirty_trick_safety(
            player,
            card_index,
            safety_card,
            selected_window,
        )

    def _is_matching_dirty_trick_safety(
        self,
        player: MileByMilePlayer,
        card: Card,
    ) -> bool:
        """Return whether this card can answer the active dirty-trick window."""
        return self._matching_dirty_trick_window(player, card) is not None

    def _action_is_matching_dirty_trick_card(
        self,
        player: MileByMilePlayer,
        action_id: str,
    ) -> bool:
        """Return whether an action id points at a dirty-trick safety."""
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return False
        if slot < 0 or slot >= len(player.hand):
            return False
        return self._is_matching_dirty_trick_safety(player, player.hand[slot])

    def _play_dirty_trick_safety(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        window: DirtyTrickWindow | None = None,
    ) -> None:
        """Resolve a reaction without interrupting the active player's action."""
        selected_window = window or self._matching_dirty_trick_window(player, card)
        if selected_window is None:
            return

        active_player = self.current_player
        self._play_safety(
            player,
            slot,
            card,
            is_dirty_trick=True,
            dirty_trick_hazard=selected_window.hazard,
        )
        self.dirty_trick_windows = [
            pending
            for pending in self.dirty_trick_windows
            if not (
                pending.team_index == player.team_index
                and HAZARD_TO_SAFETY.get(pending.hazard) == card.value
            )
        ]
        self._sync_legacy_dirty_trick_window()
        self._clear_stale_dirty_trick_bot_actions()

        if active_player is not None and active_player != player:
            self.dirty_trick_bonus_turn_player_ids.append(player.id)
        elif player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))

        self._update_all_turn_actions()
        self.refresh_menus(player)
        if active_player is not None and active_player != player:
            self.refresh_menus(active_player)
        elif not player.hand:
            self._end_turn()

    def _clear_dirty_trick_windows(self) -> None:
        """Clear every pending hazard response."""
        self.dirty_trick_windows = []
        self.dirty_trick_window_team = None
        self.dirty_trick_window_hazard = None
        self.dirty_trick_window_ticks = 0
        self._clear_stale_dirty_trick_bot_actions()

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

    def _unplayable_card_options(self, player: Player) -> list[str]:
        """Return menu options for an unplayable card."""
        del player
        return [UNPLAYABLE_REASON_OPTION, UNPLAYABLE_DISCARD_OPTION]

    def _bot_select_unplayable_card(
        self,
        player: Player,
        options: list[str],
    ) -> str | None:
        """Bots discard cards they deliberately selected but cannot play."""
        del player
        if UNPLAYABLE_DISCARD_OPTION in options:
            return UNPLAYABLE_DISCARD_OPTION
        return None

    def _unplayable_card_option_label(self, player: Player, option: str) -> str:
        """Return localized labels for the unplayable-card decision menu."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if option == UNPLAYABLE_DISCARD_OPTION:
            return Localization.get(locale, "milebymile-discard-card")
        if option == UNPLAYABLE_REASON_OPTION and isinstance(player, MileByMilePlayer):
            action_id = self._pending_actions.get(player.id)
            if action_id:
                try:
                    slot = int(action_id.split("_")[-1]) - 1
                except (ValueError, IndexError):
                    slot = -1
                if 0 <= slot < len(player.hand):
                    card = player.hand[slot]
                    return Localization.get(
                        locale,
                        "milebymile-unplayable-discard-question",
                        card=self._get_localized_card_name(card, locale),
                        reason=self._get_unplayable_reason(player, card, locale),
                    )
        return Localization.get(locale, "milebymile-unplayable-card-menu-title")

    def _bot_select_hazard_target(
        self, player: Player, options: list[str]
    ) -> str | None:
        """Select the opponent where the pending hazard has the most value."""
        del options
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

        best_idx = MileByMileBotStrategy(self).choose_hazard_target(
            player,
            card,
            target_indices,
        )
        if best_idx is None:
            return None
        race_state = self.race_states[best_idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._get_target_display_string(best_idx, race_state, locale)

    def _action_play_card(self, player: Player, *args) -> None:
        """Handle playing a card from hand.

        Can be called as:
        - _action_play_card(player, action_id) - no input
        - _action_play_card(player, input_value, action_id) - with menu input
        """
        if not isinstance(player, MileByMilePlayer):
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

        if self._is_matching_dirty_trick_safety(player, card):
            self._play_dirty_trick_safety(player, slot, card)
            return

        # Check if it's this player's turn. Dirty tricks are the exception above.
        if self.current_player != player:
            user = self.get_user(player)
            if user:
                user.speak_l("action-not-your-turn", buffer="game")
            return

        if self._can_play_card(player, card):
            if input_value == UNPLAYABLE_REASON_OPTION:
                return
            if input_value == UNPLAYABLE_DISCARD_OPTION:
                self._discard_card(player, slot, card)
                return
            self._play_card(player, slot, card, input_value)
        else:
            if input_value == UNPLAYABLE_REASON_OPTION:
                return
            if input_value == UNPLAYABLE_DISCARD_OPTION:
                self._discard_card(player, slot, card)
                return
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
            if self._is_matching_dirty_trick_safety(player, card):
                self._play_dirty_trick_safety(player, slot, card)
            else:
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
            self._broadcast_actor_l(
                player,
                "milebymile-you-play-distance-individual",
                "milebymile-plays-distance-individual",
                distance=distance,
                total=race_state.miles,
            )
        else:
            self._broadcast_actor_team_l(
                player,
                "milebymile-you-play-distance-team",
                "milebymile-teammate-plays-distance-team",
                "milebymile-plays-distance-team",
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
                    self._broadcast_actor_l(
                        player,
                        "milebymile-you-complete-perfect-individual",
                        "milebymile-journey-complete-perfect-individual",
                    )
                else:
                    self._broadcast_team_l(
                        player.team_index,
                        "milebymile-your-team-completes-perfect",
                        "milebymile-journey-complete-perfect-team",
                        team=player.team_index + 1,
                    )
            else:
                if self.is_individual_mode():
                    self._broadcast_actor_l(
                        player,
                        "milebymile-you-complete-individual",
                        "milebymile-journey-complete-individual",
                    )
                else:
                    self._broadcast_team_l(
                        player.team_index,
                        "milebymile-your-team-completes",
                        "milebymile-journey-complete-team",
                        team=player.team_index + 1,
                    )

            self.play_sound("game_milebymile/winround.ogg")
            self.race_winner_team_index = player.team_index
            self.race_completed_after_deck_exhausted = (
                self.deck.is_empty() and not self.options.reshuffle_discard_pile
            )

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
                self._announce_hazard_played(player, card, target_idx)

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

        self._announce_hazard_played(player, card, target_idx)

        # Announce karma loss (personalized)
        if attacker_shunned:
            self._announce_attacker_shunned(player, player.team_index)

        # Open a response opportunity without delaying ordinary turn flow.
        self._open_dirty_trick_window(target_idx, card.value)

        # Schedule bot dirty trick check
        for member_name in target_team.members:
            member = self._get_player_by_name(member_name)
            if member and member.is_bot:
                if member.bot_pending_action != "dirty_trick":
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

        if self.is_individual_mode():
            self._broadcast_actor_card_l(
                player,
                "milebymile-you-play-card",
                "milebymile-plays-card",
                card,
            )
        else:
            self._broadcast_actor_team_card_l(
                player,
                "milebymile-you-play-team-card",
                "milebymile-teammate-plays-team-card",
                "milebymile-opponent-plays-team-card",
                card,
            )
        self.discard_pile.append(card)
        self._end_turn()

    def _play_safety(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        is_dirty_trick: bool = False,
        dirty_trick_hazard: str | None = None,
    ) -> None:
        """Play a safety card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)
        race_state.add_safety(card.value)

        if is_dirty_trick:
            race_state.dirty_trick_count += 1
            if self.is_individual_mode():
                self._broadcast_actor_card_l(
                    player,
                    "milebymile-you-play-dirty-trick",
                    "milebymile-plays-dirty-trick",
                    card,
                )
            else:
                self._broadcast_actor_team_card_l(
                    player,
                    "milebymile-you-play-dirty-trick-team",
                    "milebymile-teammate-plays-dirty-trick-team",
                    "milebymile-opponent-plays-dirty-trick-team",
                    card,
                )
            self.play_sound("mention.ogg")

            self._discard_countered_hazard(race_state, dirty_trick_hazard)
            self._apply_safety_protection(race_state, card.value)
        else:
            if self.is_individual_mode():
                self._broadcast_actor_card_l(
                    player,
                    "milebymile-you-play-card",
                    "milebymile-plays-card",
                    card,
                )
            else:
                self._broadcast_actor_team_card_l(
                    player,
                    "milebymile-you-play-team-card",
                    "milebymile-teammate-plays-team-card",
                    "milebymile-opponent-plays-team-card",
                    card,
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

            self._apply_safety_protection(race_state, card.value)

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

        if not is_dirty_trick:
            if not player.hand:
                self._end_turn()
                return
            self._update_all_turn_actions()
            self.announce_turn()
            self.refresh_menus(player)
            # Don't end turn: this draw begins the Safety's extra turn.
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(30, 40))

    def _discard_countered_hazard(
        self,
        race_state: RaceState,
        hazard: str | None,
    ) -> None:
        """Move the Hazard cancelled by a dirty trick to the discard pile."""
        if not hazard:
            return
        for index in range(len(race_state.battle_pile) - 1, -1, -1):
            played_card = race_state.battle_pile[index]
            if (
                played_card.card_type == CardType.HAZARD
                and played_card.value == hazard
            ):
                self.discard_pile.append(race_state.battle_pile.pop(index))
                return

    def _apply_safety_protection(self, race_state: RaceState, safety: str) -> None:
        """Cancel active hazards covered by a newly played safety."""
        protected_hazard = SAFETY_TO_HAZARD.get(safety)
        had_matching_hazard = (
            protected_hazard is not None and race_state.has_problem(protected_hazard)
        )

        if protected_hazard:
            race_state.remove_problem(protected_hazard)

        if safety == SafetyType.RIGHT_OF_WAY:
            race_state.remove_problem(HazardType.SPEED_LIMIT)
            race_state.remove_problem(HazardType.STOP)
            return

        if had_matching_hazard and not any(
            problem != HazardType.STOP and is_critical_problem(problem)
            for problem in race_state.problems
        ):
            race_state.remove_problem(HazardType.STOP)

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

        self._broadcast_actor_card_l(
            player,
            "milebymile-you-discard",
            "milebymile-discards",
            card,
        )
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
            self.broadcast_l("milebymile-deck-reshuffled", buffer="game")
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

        if (
            self.options.only_allow_perfect_crossing
            and self.options.round_distance % 25 != 0
        ):
            errors.append("milebymile-error-perfect-distance-step")

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        # Always set up teams unconditionally to ensure correct assignments,
        # matching every other game.
        self._setup_teams()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.current_race = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(self._get_team_turn_players(active_players))

        # Play music and ambience
        self.play_music("game_milebymile/music.ogg")
        self.play_ambience("game_milebymile/amloop.ogg")

        # Start first race
        self._start_race()

    def _start_race(self) -> None:
        """Start a new race."""
        self.current_race += 1
        self.race_winner_team_index = None
        self.race_completed_after_deck_exhausted = False
        self._clear_dirty_trick_windows()
        self.dirty_trick_bonus_turn_player_ids = []

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
        self.broadcast_l("milebymile-new-race", buffer="game")

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
        elif not player.hand:
            # Once no draw source remains, empty-handed players have no legal
            # play. Skip them so the final cards can be played out normally.
            self._end_turn()
            return

        # Announce turn
        self.announce_turn()

        if player.is_bot:
            if self._bot_dirty_trick_action(player):
                if player.bot_pending_action != "dirty_trick":
                    player.bot_think_ticks = min(player.bot_think_ticks, 18)
            else:
                BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self._update_all_turn_actions()
        self.refresh_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Don't process turns during countdown
        if self._round_timer.is_active:
            return

        # Check for race end
        if self.race_winner_team_index is not None:
            self._end_race()
            return

        if self._start_pending_dirty_trick_bonus_turn():
            return

        # End the race once neither the deck nor a permitted reshuffle can
        # provide a card and every hand has been played out.
        draw_source_exhausted = self.deck.is_empty() and (
            not self.options.reshuffle_discard_pile or not self.discard_pile
        )
        if draw_source_exhausted:
            all_empty = all(len(p.hand) == 0 for p in self.get_active_players())
            if all_empty:
                self._end_race()
                return

        # Advance to next player
        dirty_trick_bot_ids = self._dirty_trick_bot_responder_ids()
        ordinary_bots = [
            player
            for player in self.players
            if player.id not in dirty_trick_bot_ids
        ]
        BotHelper.jolt_bots(
            self,
            ticks=random.randint(15, 25),
            players=ordinary_bots,
        )
        self.advance_turn(announce=False)
        self._start_turn()

    def _start_pending_dirty_trick_bonus_turn(self) -> bool:
        """Start the next queued turn awarded by an asynchronous response."""
        active_ids = {player.id for player in self.get_active_players()}
        while self.dirty_trick_bonus_turn_player_ids:
            player_id = self.dirty_trick_bonus_turn_player_ids.pop(0)
            player = self.get_player_by_id(player_id)
            if (
                not isinstance(player, MileByMilePlayer)
                or player.id not in active_ids
            ):
                continue
            self.current_player = player
            self._start_turn()
            return True
        return False

    def _end_race(self) -> None:
        """End the current race and calculate scores."""
        self._clear_dirty_trick_windows()
        self.dirty_trick_bonus_turn_player_ids = []

        # Find winner (team index with most miles if no one reached target)
        winning_team_idx: int | None = self.race_winner_team_index
        if winning_team_idx is None:
            # Find team with most miles
            max_miles = -1
            for team_idx, race_state in self.iter_teams():
                if race_state.miles > max_miles:
                    max_miles = race_state.miles
                    winning_team_idx = team_idx

        self.broadcast_l("milebymile-race-complete", buffer="game")

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
            self.refresh_menus()

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

                if self.race_completed_after_deck_exhausted:
                    score += 300
                    bonus_parts.append(("milebymile-from-delayed", {"points": 300}))

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
                    buffer="game",
                    name=name,
                    score=score,
                    breakdown=breakdown,
                )

        # Announce total scores
        self.broadcast_l("milebymile-total-scores", buffer="game")
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
            winner_player = self._get_player_by_name(winner_team.members[0])
            if winner_player:
                self._broadcast_actor_l(
                    winner_player,
                    "milebymile-you-win-individual",
                    "milebymile-wins-individual",
                )
            else:
                self.broadcast_l(
                    "milebymile-wins-individual",
                    buffer="game",
                    player=winner_team.members[0],
                )
        else:
            members_str = ", ".join(winner_team.members)
            self._broadcast_team_l(
                winner_idx,
                "milebymile-your-team-wins",
                "milebymile-wins-team",
                team=winner_idx + 1,
                members=members_str,
            )
        self.broadcast_l("milebymile-final-score", buffer="game", score=winner_score)

        self.finish_game()

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
            # Resolve name: if key is digit, it's a team index. Else it's a direct name.
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
                        "milebymile-karma-clash-you-attacker", buffer="game", attacker=attacker.name
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-others",
                        buffer="game",
                        attacker=attacker.name,
                        target=target_name,
                    )
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if not p.is_spectator and p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-clash-your-team", buffer="game")
                elif not p.is_spectator and p.team_index == target_team_idx:
                    user.speak_l(
                        "milebymile-karma-clash-target-team",
                        buffer="game",
                        team=attacker_team_idx + 1,
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-other-teams",
                        buffer="game",
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
                if not p.is_spectator and p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-shunned-your-team", buffer="game")
                else:
                    user.speak_l(
                        "milebymile-karma-shunned-other-team",
                        buffer="game",
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
            self._broadcast_actor_team_l(
                player,
                "milebymile-false-virtue-you",
                "milebymile-false-virtue-teammate",
                "milebymile-false-virtue-opponent",
            )

    def _announce_hazard_played(
        self,
        attacker: MileByMilePlayer,
        card: Card,
        target_idx: int,
    ) -> None:
        """Announce a hazard with attacker and target context."""
        target_team = self._team_manager.teams[target_idx]
        target_name = target_team.members[0] if target_team.members else ""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            card_name = self._get_localized_card_name(card, user.locale)
            if self.is_individual_mode():
                if listener == attacker:
                    user.speak_l(
                        "milebymile-you-play-hazard-individual",
                        buffer="game",
                        card=card_name,
                        target=target_name,
                    )
                elif listener.name == target_name:
                    user.speak_l(
                        "milebymile-hazard-played-on-you",
                        buffer="game",
                        player=attacker.name,
                        card=card_name,
                    )
                else:
                    user.speak_l(
                        "milebymile-plays-hazard-individual",
                        buffer="game",
                        player=attacker.name,
                        card=card_name,
                        target=target_name,
                    )
            else:
                if listener == attacker:
                    user.speak_l(
                        "milebymile-you-play-hazard-team",
                        buffer="game",
                        card=card_name,
                        team=target_idx + 1,
                    )
                elif (
                    isinstance(listener, MileByMilePlayer)
                    and not listener.is_spectator
                    and listener.team_index == target_idx
                ):
                    user.speak_l(
                        "milebymile-hazard-played-on-your-team",
                        buffer="game",
                        player=attacker.name,
                        card=card_name,
                    )
                else:
                    user.speak_l(
                        "milebymile-plays-hazard-team",
                        buffer="game",
                        player=attacker.name,
                        card=card_name,
                        team=target_idx + 1,
                    )

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

        if self.dirty_trick_windows:
            for window in self.dirty_trick_windows:
                window.ticks -= 1
            self.dirty_trick_windows = [
                window for window in self.dirty_trick_windows if window.ticks > 0
            ]
            self._sync_legacy_dirty_trick_window()
            self._clear_stale_dirty_trick_bot_actions()

        current_bot_reserved = self._process_dirty_trick_bots()
        if current_bot_reserved:
            return
        BotHelper.on_tick(self)

    def _process_dirty_trick_bots(self) -> bool:
        """Process one eligible bot responder per team without pausing play."""
        current = self.current_player
        processed_ids: set[str] = set()
        current_bot_reserved = False
        active_players = self.get_active_players()
        for window in reversed(self.dirty_trick_windows):
            blocking_safety = HAZARD_TO_SAFETY.get(window.hazard)
            responder = next(
                (
                    player
                    for player in active_players
                    if isinstance(player, MileByMilePlayer)
                    and player.is_bot
                    and player.id not in processed_ids
                    and player.team_index == window.team_index
                    and any(
                        card.card_type == CardType.SAFETY
                        and card.value == blocking_safety
                        for card in player.hand
                    )
                ),
                None,
            )
            if responder is None:
                continue
            processed_ids.add(responder.id)
            BotHelper.process_bot_action(
                responder,
                lambda responder=responder: self._bot_dirty_trick_action(responder),
                lambda action_id, responder=responder: self.execute_action(
                    responder, action_id
                ),
            )
            if responder == current:
                current_bot_reserved = True
        return current_bot_reserved

    def _dirty_trick_bot_responder_ids(self) -> set[str]:
        """Return bots whose reaction countdown must survive ordinary turns."""
        return {
            player.id
            for player in self.get_active_players()
            if isinstance(player, MileByMilePlayer)
            and player.is_bot
            and self._bot_dirty_trick_action(player) is not None
        }

    def _clear_stale_dirty_trick_bot_actions(self) -> None:
        """Discard queued bot reactions whose matching window has closed."""
        for player in self.get_active_players():
            if (
                isinstance(player, MileByMilePlayer)
                and player.is_bot
                and player.bot_pending_action == "dirty_trick"
                and self._bot_dirty_trick_action(player) is None
            ):
                player.bot_pending_action = None

    def _bot_dirty_trick_action(
        self,
        player: MileByMilePlayer,
    ) -> str | None:
        """Return the response action while this bot still has a matching Safety."""
        for card in player.hand:
            if self._matching_dirty_trick_window(player, card) is not None:
                return "dirty_trick"
        return None

    def bot_think(self, player: MileByMilePlayer) -> str | None:
        """Bot AI decision making."""
        # Don't act during between-race countdown
        if self._round_timer.is_active:
            return None

        dirty_trick_action = self._bot_dirty_trick_action(player)
        if dirty_trick_action:
            return dirty_trick_action

        # Not our turn? Skip
        if self.current_player != player:
            return None

        # Choose best card to play
        return self._bot_choose_card(player)

    def _bot_choose_card(self, player: MileByMilePlayer) -> str | None:
        """Choose a card through the strategic public-information evaluator."""
        return MileByMileBotStrategy(self).choose_card_action(player)

    def build_game_result(self) -> GameResult:
        """Build the game result for Mile by Mile."""
        team_scores = [(i, self.get_team_score(i)) for i in range(self.get_num_teams())]
        sorted_teams = sorted(team_scores, key=lambda item: item[1], reverse=True)
        winner_team_idx, winner_score = sorted_teams[0] if sorted_teams else (None, 0)
        winner_ids = []
        winner_name = None

        final_scores = {}
        # Calculate team scores/progress — use str(index) as key for dynamic
        # localization in format_end_screen (same pattern as the first build_game_result)
        for i, score in sorted_teams:
            team = self._team_manager.teams[i]
            final_scores[str(i)] = score

            if winner_team_idx is not None and i == winner_team_idx:
                winner_name = self.get_team_name(i)

                # Map members to IDs
                active_players = self.get_active_players()
                name_to_id = {p.name: p.id for p in active_players}
                for member_name in team.members:
                    if member_name in name_to_id:
                        winner_ids.append(name_to_id[member_name])

        result = GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner_name,
                "winner_ids": winner_ids if winner_ids else None,
                "winner_score": winner_score,
                "final_scores": final_scores,
                "rounds_played": self.current_race,
                "target_score": self.options.winning_score,
                "race_distance": self.options.round_distance,
                "team_mode": self.options.team_mode,
            },
        )
        return result
