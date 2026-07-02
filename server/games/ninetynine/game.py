"""
Ninety Nine Game Implementation.

A card game where players try to avoid pushing the running total over 99.
Last player standing wins!

Rules match v10 implementation with standard and action cards variants.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.cards import (
    Card,
    Deck,
    DeckFactory,
    card_name,
    card_name_with_article,
    sort_cards,
    N99_RANK_PLUS_10,
    N99_RANK_MINUS_10,
    N99_RANK_PASS,
    N99_RANK_REVERSE,
    N99_RANK_SKIP,
    N99_RANK_NINETY_NINE,
)
from ...game_utils.options import BoolOption, IntOption, MenuOption, option_field
from ...game_utils.round_timer import RoundTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_think as _bot_think, _score_outcome


# =============================================================================
# Game Constants
# =============================================================================

# Count thresholds
MIN_COUNT = 0
MAX_COUNT = 99
MILESTONE_33 = 33
MILESTONE_66 = 66
ACE_AUTO_THRESHOLD = 88  # Auto-choose +1 when count > this
TEN_AUTO_THRESHOLD = 90  # Auto-choose -10 when count >= this
TWO_DIVIDE_THRESHOLD = 49  # Divide by 2 when count > this and even

# Default options
DEFAULT_TOKENS = 9

# Token penalties
PENALTY_BUST = 2  # Standard: going over 99
PENALTY_BUST_ACTION = 1  # Action cards: going over 99
PENALTY_MILESTONE_PASS = 1  # Passing through 33 or 66
PENALTY_MILESTONE_99 = 2  # Landing on 99 (others lose this)
PENALTY_MILESTONE_33_66 = 1  # Landing on 33/66 (others lose this)
PENALTY_NO_CARDS = 3  # Running out of cards

# Draw timeout (manual draw mode)
DRAW_TIMEOUT_TICKS = 200  # 10 seconds at 20 ticks/sec
ROUND_TRANSITION_SECONDS = 10
ROUND_TRANSITION_TAG = "ninetynine_round_transition"
START_ROUND_CALLBACK = "ninetynine_start_round"


@dataclass
class NinetyNinePlayer(Player):
    """Player state for Ninety Nine."""

    hand: list[Card] = field(default_factory=list)
    tokens: int = DEFAULT_TOKENS
    draw_timeout_ticks: int = 0  # Per-player manual-draw countdown


@dataclass
class NinetyNineOptions(GameOptions):
    """Options for Ninety Nine game."""

    starting_tokens: int = option_field(
        IntOption(
            default=9,
            min_val=1,
            max_val=50,
            value_key="tokens",
            label="ninetynine-set-tokens",
            prompt="ninetynine-enter-tokens",
            change_msg="ninetynine-option-changed-tokens",
        )
    )
    hand_size: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=13,
            value_key="size",
            label="ninetynine-set-hand-size",
            prompt="ninetynine-enter-hand-size",
            change_msg="ninetynine-option-changed-hand-size",
        )
    )
    rules_variant: str = option_field(
        MenuOption(
            default="standard",
            value_key="rules",
            choices=["standard", "action_cards"],
            choice_labels={
                "standard": "ninetynine-rules-variant-standard",
                "action_cards": "ninetynine-rules-variant-action-cards",
            },
            label="ninetynine-set-rules",
            prompt="ninetynine-select-rules",
            change_msg="ninetynine-option-changed-rules",
        )
    )
    autodraw: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="ninetynine-set-autodraw",
            change_msg="ninetynine-option-changed-autodraw",
        )
    )


@dataclass
@register_game
class NinetyNineGame(Game):
    """
    Ninety Nine - A card game where players try to avoid going over 99.

    Players take turns playing cards that modify a running count.
    Rules match v10 with standard and action cards variants.
    """

    players: list[NinetyNinePlayer] = field(default_factory=list)
    options: NinetyNineOptions = field(default_factory=NinetyNineOptions)
    score_unit_key = "game-score-unit-ninetynine-tokens"

    # Game state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    count: int = 0  # Running count

    # Players still in the game (have tokens)
    alive_player_ids: list[str] = field(default_factory=list)

    # Pending choice state (for Ace or Ten)
    pending_choice: str | None = None  # "ace" or "ten"
    pending_card_index: int = -1

    @classmethod
    def get_name(cls) -> str:
        return "Ninety Nine"

    @classmethod
    def get_type(cls) -> str:
        return "ninetynine"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> NinetyNinePlayer:
        """Create a new player with Ninety Nine-specific state."""
        return NinetyNinePlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            tokens=self.options.starting_tokens,
        )

    def __post_init__(self) -> None:
        """Initialize runtime-only helpers."""
        super().__post_init__()
        self._round_timer = RoundTimer(self, delay_seconds=ROUND_TRANSITION_SECONDS)

    def rebuild_runtime_state(self) -> None:
        """Rebuild runtime-only helpers after deserialization."""
        super().rebuild_runtime_state()
        self._round_timer = RoundTimer(self, delay_seconds=ROUND_TRANSITION_SECONDS)

    def on_round_timer_ready(self) -> None:
        """Start the next round when the between-round timer finishes."""
        if self.game_active:
            self._start_round()

    def _get_round_timer(self) -> RoundTimer:
        """Return the round timer, rebuilding it for legacy restored objects."""
        timer = getattr(self, "_round_timer", None)
        if timer is None:
            timer = RoundTimer(self, delay_seconds=ROUND_TRANSITION_SECONDS)
            self._round_timer = timer
        return timer

    @property
    def alive_players(self) -> list[NinetyNinePlayer]:
        """Get players who still have tokens."""
        return [
            p for p in self.players
            if p.id in self.alive_player_ids and p.tokens > 0 and not p.is_spectator
        ]

    @property
    def is_standard_rules(self) -> bool:
        """Check if using standard rules (52-card deck)."""
        return self.options.rules_variant == "standard"

    def on_player_skipped(self, player: Player) -> None:
        """Announce when a player is skipped."""
        self.broadcast_personal_l(
            player,
            "ninetynine-you-skipped",
            "ninetynine-player-skipped",
            buffer="game",
        )

    def _play_outcome_sounds(
        self,
        *,
        winners: list[NinetyNinePlayer] | None = None,
        losers: list[NinetyNinePlayer] | None = None,
        win_sound: str,
        lose_sound: str,
    ) -> None:
        """Play winner and loser sounds, with spectators hearing the winner sound."""
        loser_ids = {player.id for player in losers or []}

        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            if table_player.id in loser_ids:
                user.play_sound(lose_sound)
            else:
                user.play_sound(win_sound)

    def _sort_hand(self, player: NinetyNinePlayer) -> None:
        """Sort a player's hand by rank."""
        player.hand = sort_cards(player.hand, by_suit=False)

    def _deck_size_for_options(self) -> int:
        """Return the deck size implied by the selected rules variant."""
        return 52 if self.is_standard_rules else 60

    def _floor_count(self, value: int) -> int:
        """Keep the running count from ever becoming negative."""
        return max(MIN_COUNT, value)

    def _normalize_count_floor(self) -> int:
        """Repair a stale negative count and return the playable count."""
        self.count = self._floor_count(self.count)
        return self.count

    def _new_count_with_delta(self, current_count: int, delta: int) -> int:
        """Apply a card value without allowing the count to underflow."""
        return self._floor_count(current_count + delta)

    def _is_alive_player(self, player: Player) -> bool:
        """Return whether a player is still eligible to act in this game."""
        return (
            isinstance(player, NinetyNinePlayer)
            and player.id in self.alive_player_ids
            and player.tokens > 0
            and not player.is_spectator
        )

    def _is_round_transition_active(self) -> bool:
        """Return whether the game is waiting before the next round."""
        return self._get_round_timer().is_active or self.has_active_sequence(
            tag=ROUND_TRANSITION_TAG
        )

    def _choose_round_start_index(self, player_count: int) -> int:
        """Choose a random alive player to start the new round."""
        return random.randrange(player_count) if player_count > 1 else 0

    # ==========================================================================
    # Card Value Calculation
    # ==========================================================================

    def calculate_card_value(self, card: Card, current_count: int) -> int | None:
        """
        Calculate the value a card adds to the count.
        Returns None if player choice is needed or special handling required.
        """
        current_count = self._floor_count(current_count)
        rank = card.rank

        if self.is_standard_rules:
            return self._calculate_standard_value(rank, current_count)
        else:
            return self._calculate_action_cards_value(rank)

    def _calculate_standard_value(self, rank: int, current_count: int) -> int | None:
        """Calculate card value for standard variant."""
        if rank == 1:  # Ace: +1 or +11
            if current_count > ACE_AUTO_THRESHOLD:
                return 1  # Auto +1 if would bust with +11
            return None  # Choice needed

        elif rank == 2:  # 2: multiply or divide (special handling)
            return None

        elif rank == 4:  # 4: Reverse (Adds 4)
            return 4

        elif 3 <= rank <= 8:  # 3, 5-8: face value
            return rank

        elif rank == 9:  # 9: pass
            return 0

        elif rank == 10:  # 10: +10 or -10
            if current_count >= TEN_AUTO_THRESHOLD:
                return -10  # Auto -10 at high counts
            return None  # Choice needed

        elif rank in (11, 12, 13):  # Jack, Queen, King: +10
            return 10

        return 0

    def _calculate_action_cards_value(self, rank: int) -> int | None:
        """Calculate card value for action cards variant."""
        if 1 <= rank <= 9:  # Number cards: face value
            return rank
        elif rank == N99_RANK_PLUS_10:
            return 10
        elif rank == N99_RANK_MINUS_10:
            return -10
        elif rank in (N99_RANK_PASS, N99_RANK_REVERSE, N99_RANK_SKIP):
            return 0
        elif rank == N99_RANK_NINETY_NINE:
            return None  # Special handling - sets to exactly 99
        return 0

    def calculate_two_effect(self, current_count: int) -> int:
        """Calculate the new count after playing a 2 (standard rules)."""
        current_count = self._floor_count(current_count)
        if current_count % 2 == 0 and current_count > TWO_DIVIDE_THRESHOLD:
            return current_count // 2
        else:
            return current_count * 2

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: NinetyNinePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="pause_timer",
                label=Localization.get(locale, "ninetynine-pause-timer"),
                handler="_action_pause_timer",
                is_enabled="_is_pause_timer_enabled",
                is_hidden="_is_pause_timer_hidden",
            )
        )
        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_count", "check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_count",
                label=Localization.get(locale, "ninetynine-check-count"),
                handler="_action_check_count",
                is_enabled="_is_check_count_enabled",
                is_hidden="_is_check_count_hidden",
                get_label="_get_check_count_label",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(action_set, self.web_target_order)

        return action_set

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        """Validate option combinations before the game starts."""
        errors = list(super().prestart_validate())
        player_count = len(self.get_active_players())
        cards_needed = player_count * self.options.hand_size
        deck_size = self._deck_size_for_options()
        if cards_needed > deck_size:
            errors.append(
                (
                    "ninetynine-error-too-many-cards",
                    {
                        "players": player_count,
                        "hand_size": self.options.hand_size,
                        "deck_size": deck_size,
                    },
                )
            )
        return errors

    def before_menu_build(self, player: Player) -> None:
        """Refresh localized dynamic card labels before any menu paint."""
        if isinstance(player, NinetyNinePlayer):
            self._update_turn_actions(player)

    def _on_replacement_slot_reclaimed(
        self, bot_name: str, human_name: str
    ) -> None:
        """Refresh dynamic player actions when a human reclaims a bot seat."""
        super()._on_replacement_slot_reclaimed(bot_name, human_name)
        self._update_all_turn_actions()

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        # Card-slot and draw keybinds depend on the options (hand size,
        # autodraw), so they live in a helper that is also refreshed at
        # on_start once the host's options are locked. See _define_card_keybinds.
        self._define_card_keybinds()

        # Count check
        self.define_keybind(
            "c",
            Localization.get(locale, "ninetynine-check-count"),
            ["check_count"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "p",
            Localization.get(locale, "ninetynine-pause-timer"),
            ["pause_timer"],
            state=KeybindState.ACTIVE,
        )

    def _define_card_keybinds(self) -> None:
        """(Re)define the card-slot and draw keybinds to match current options.

        Card slots map to the keys 1-9 then 0, but only for as many cards as a
        hand can actually hold (``hand_size``, capped at the ten available
        keys) — so no keybind ever points at a ``card_slot`` action the game
        never creates. The draw keybind exists only in manual-draw mode; with
        autodraw on, the game refills automatically and a draw key would be a
        dead binding.

        Called from setup_keybinds (lobby) and refreshed at on_start once the
        host's options are locked.
        """
        user = None
        host_name = getattr(self, "host", None)
        if host_name:
            player = self.get_player_by_name(host_name)
            if player:
                user = self.get_user(player)
        locale = user.locale if user else "en"

        # Clear any prior definitions so a refresh replaces rather than
        # duplicates them (define_keybind appends per key).
        for key in [str(i) for i in range(1, 10)] + ["0", "space", "d"]:
            self._keybinds.pop(key, None)

        slot_count = min(self.options.hand_size, 10)
        for i in range(1, slot_count + 1):
            key = str(i) if i < 10 else "0"
            self.define_keybind(
                key, f"Play card {i}", [f"card_slot_{i}"], state=KeybindState.ACTIVE
            )

        if not self.options.autodraw:
            for key in ("space", "d"):
                self.define_keybind(
                    key,
                    Localization.get(locale, "ninetynine-draw-card"),
                    ["draw_card"],
                    state=KeybindState.ACTIVE,
                )

    def _update_card_actions(self, player: NinetyNinePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"

        is_current = self.current_player == player
        is_playing = self.status == "playing"
        has_pending_choice = self.pending_choice is not None
        needs_to_draw = player.draw_timeout_ticks > 0

        # Remove old dynamic actions
        turn_set.remove_by_prefix("card_slot_")
        turn_set.remove("resolve_choice")
        turn_set.remove("draw_card")

        if (
            self.status != "playing"
            or self._is_round_transition_active()
            or not self._is_alive_player(player)
        ):
            return

        # Add card slot actions for cards in hand
        for i, card in enumerate(player.hand, 1):
            action_id = f"card_slot_{i}"
            input_request = None
            if self._card_requires_manual_choice(card):
                input_request = MenuInput(
                    prompt="ninetynine-select-card-choice",
                    options="_choice_options_for_card",
                    bot_select="_bot_select_card_choice",
                    pre_input_check="_pre_input_check_card_choice",
                )
            turn_set.add(
                Action(
                    id=action_id,
                    label=card_name(card, locale),
                    handler="_action_play_card",
                    is_enabled="_is_card_slot_enabled",
                    is_hidden="_is_card_slot_hidden",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )

        # Preserve old pending choice saves by routing them through the same
        # action_input_menu flow, including a cancel button.
        if has_pending_choice and is_current:
            pending_options = self._pending_choice_options(player)
            input_request = None
            if len(pending_options) > 1:
                input_request = MenuInput(
                    prompt="ninetynine-select-card-choice",
                    options="_pending_choice_options",
                    bot_select="_bot_select_pending_choice",
                    pre_input_check="_pre_input_check_pending_choice",
                )
            turn_set.add(
                Action(
                    id="resolve_choice",
                    label=self._pending_choice_prompt(locale),
                    handler="_action_resolve_pending_choice",
                    is_enabled="_is_choice_enabled",
                    is_hidden="_is_choice_hidden",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )

        # Add draw action if in manual draw mode
        if needs_to_draw and is_playing:
            turn_set.add(
                Action(
                    id="draw_card",
                    label=Localization.get(locale, "ninetynine-draw-card"),
                    handler="_action_draw_card",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=False,
                )
            )
            
            # WEB-SPECIFIC: For web, force "draw_card" to be the FIRST action
            # This ensures it appears at the top of the menu, above the disabled cards.
            # Python client doesn't need this because it uses keybinds (Space/D).
            if self.is_touch_client(user):
                if "draw_card" in turn_set._order:
                    turn_set._order.remove("draw_card")
                    turn_set._order.insert(0, "draw_card")

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

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_count_enabled(self, player: Player) -> str | None:
        """Check if check count action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_count_hidden(self, player: Player) -> Visibility:
        """Check count is always hidden (keybind only), unless Web."""
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _get_check_count_label(self, player: Player, action_id: str) -> str:
        """Get the localized label for checking the current count."""
        del action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ninetynine-check-count")

    def _is_pause_timer_enabled(self, player: Player) -> str | None:
        """Pause timer is enabled for the host during the next-round wait."""
        if player.name != self.host:
            return "action-not-host"
        if not self._get_round_timer().is_active:
            return "ninetynine-timer-not-active"
        return None

    def _is_pause_timer_hidden(self, player: Player) -> Visibility:
        """Keep the host timer control keybind-only, matching Scopa."""
        return Visibility.HIDDEN

    def _is_card_slot_enabled(self, player: Player) -> str | None:
        """Check if card slot actions are enabled. (Keep explicitly visible so UI displays them out-of-turn)"""
        if self.status != "playing":
            return "action-not-playing"
        if self._is_round_transition_active():
            return "ninetynine-round-transition-waiting"
        if not self._is_alive_player(player):
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.pending_choice is not None:
            return "ninetynine-choose-first"
        return None

    def _is_card_slot_hidden(self, player: Player) -> Visibility:
        """Card slots are visible during play."""
        if (
            self.status != "playing"
            or self._is_round_transition_active()
            or not self._is_alive_player(player)
        ):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_choice_enabled(self, player: Player) -> str | None:
        """Check if choice actions are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._is_round_transition_active():
            return "ninetynine-round-transition-waiting"
        if not self._is_alive_player(player):
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.pending_choice is None:
            return "action-not-available"
        return None

    def _is_choice_hidden(self, player: Player) -> Visibility:
        """Choice actions are visible during play."""
        if (
            self.status != "playing"
            or self._is_round_transition_active()
            or not self._is_alive_player(player)
            or self.pending_choice is None
        ):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_enabled(self, player: Player) -> str | None:
        """Check if draw action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._is_round_transition_active():
            return "ninetynine-round-transition-waiting"
        if not self._is_alive_player(player):
            return "action-not-available"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        """Draw action is visible during play."""
        if (
            self.status != "playing"
            or self._is_round_transition_active()
            or not self._is_alive_player(player)
        ):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _update_turn_actions(self, player: NinetyNinePlayer) -> None:
        """Update turn action availability for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update turn actions for all players."""
        for player in self.players:
            if isinstance(player, NinetyNinePlayer):
                self._update_turn_actions(player)

    def _card_requires_manual_choice(self, card: Card) -> bool:
        """Return True only when the card currently has multiple valid outcomes."""
        choice_type = self._choice_type_for_card(card)
        if not choice_type:
            return False
        return len(self._choice_values_for_type(choice_type)) > 1

    def _choice_values_for_type(self, choice_type: str) -> list[int]:
        """Get the currently valid numeric outcomes for a choice card."""
        count = self._floor_count(self.count)
        if choice_type == "ace":
            return [1] if count > ACE_AUTO_THRESHOLD else [11, 1]
        if choice_type == "ten":
            return [-10] if count >= TEN_AUTO_THRESHOLD else [10, -10]
        return []

    def _choice_labels_for_values(
        self, choice_type: str, values: list[int], locale: str
    ) -> list[str]:
        """Map currently valid outcomes to localized labels."""
        if choice_type == "ace":
            label_map = {
                11: Localization.get(locale, "ninetynine-ace-add-eleven"),
                1: Localization.get(locale, "ninetynine-ace-add-one"),
            }
            return [label_map[value] for value in values if value in label_map]
        if choice_type == "ten":
            label_map = {
                10: Localization.get(locale, "ninetynine-ten-add"),
                -10: Localization.get(locale, "ninetynine-ten-subtract"),
            }
            return [label_map[value] for value in values if value in label_map]
        return [
            Localization.get(locale, "ninetynine-choice-1"),
            Localization.get(locale, "ninetynine-choice-2"),
        ]

    def _choice_type_for_card(self, card: Card) -> str | None:
        """Resolve the card's choice type."""
        if not self.is_standard_rules:
            return None
        if card.rank == 1:
            return "ace"
        if card.rank == 10:
            return "ten"
        return None

    def _choice_type_for_action(self, player: NinetyNinePlayer) -> str | None:
        """Resolve the choice type for the currently pending action input."""
        action_id = self._pending_actions.get(player.id)
        if not action_id or not action_id.startswith("card_slot_"):
            return None
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return None
        if slot < 0 or slot >= len(player.hand):
            return None
        return self._choice_type_for_card(player.hand[slot])

    def _choice_options_for_card(self, player: NinetyNinePlayer) -> list[str]:
        """Build localized options for the currently selected choice card."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        choice_type = self._choice_type_for_action(player)
        if not choice_type:
            return []
        return self._choice_labels_for_values(
            choice_type, self._choice_values_for_type(choice_type), locale
        )

    def _pending_choice_options(self, player: NinetyNinePlayer) -> list[str]:
        """Build localized options for a legacy saved pending choice."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if not self.pending_choice:
            return []
        return self._choice_labels_for_values(
            self.pending_choice,
            self._choice_values_for_type(self.pending_choice),
            locale,
        )

    def _pending_choice_prompt(self, locale: str) -> str:
        """Get the localized label for an outstanding choice."""
        if self.pending_choice == "ace":
            return Localization.get(locale, "ninetynine-ace-choice")
        if self.pending_choice == "ten":
            return Localization.get(locale, "ninetynine-ten-choice")
        return Localization.get(locale, "ninetynine-select-card-choice")

    def _pre_input_check_card_choice(self, player: Player, action_id: str) -> str | None:
        """Validate before opening a choice dialog from a card click."""
        if self.status != "playing":
            return "action-not-playing"
        if self._is_round_transition_active():
            return "ninetynine-round-transition-waiting"
        if not self._is_alive_player(player):
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.pending_choice is not None:
            return "ninetynine-choose-first"
        return None

    def _pre_input_check_pending_choice(self, player: Player, action_id: str) -> str | None:
        """Validate before opening a legacy pending choice dialog."""
        if self.status != "playing":
            return "action-not-playing"
        if self._is_round_transition_active():
            return "ninetynine-round-transition-waiting"
        if not self._is_alive_player(player):
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.pending_choice is None:
            return "action-not-available"
        return None

    def _choice_value_from_input(self, choice_type: str, input_value: str, locale: str) -> int | None:
        """Resolve the numeric effect from the selected localized choice label."""
        values = self._choice_values_for_type(choice_type)
        labels = self._choice_labels_for_values(choice_type, values, locale)
        for value, label in zip(values, labels, strict=False):
            if input_value == label:
                return value
        return None

    def _bot_select_card_choice(self, player: NinetyNinePlayer, options: list[str]) -> str | None:
        """Pick the best Ace/Ten value for a bot using the current pending action."""
        action_id = self._pending_actions.get(player.id)
        if not action_id or not action_id.startswith("card_slot_"):
            return None
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return None
        if slot < 0 or slot >= len(player.hand):
            return None

        card = player.hand[slot]
        choice_type = self._choice_type_for_card(card)
        if not choice_type:
            return None

        locale = "en"
        if choice_type == "ace":
            current_count = self._floor_count(self.count)
            score_11 = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 11)
            )
            score_1 = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 1)
            )
            labels = self._choice_labels_for_values(
                choice_type, self._choice_values_for_type(choice_type), locale
            )
            return labels[0] if score_11 > score_1 else labels[1]

        if choice_type == "ten":
            current_count = self._floor_count(self.count)
            score_plus = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 10)
            )
            score_minus = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, -10)
            )
            labels = self._choice_labels_for_values(
                choice_type, self._choice_values_for_type(choice_type), locale
            )
            return labels[0] if score_plus > score_minus else labels[1]

        return None

    def _bot_select_pending_choice(self, player: NinetyNinePlayer, options: list[str]) -> str | None:
        """Pick the best option for a legacy pending choice state."""
        if self.pending_card_index < 0 or self.pending_card_index >= len(player.hand):
            return None
        card = player.hand[self.pending_card_index]
        locale = "en"
        if self.pending_choice == "ace":
            current_count = self._floor_count(self.count)
            score_11 = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 11)
            )
            score_1 = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 1)
            )
            labels = self._choice_labels_for_values(
                "ace", self._choice_values_for_type("ace"), locale
            )
            return labels[0] if score_11 > score_1 else labels[1]
        if self.pending_choice == "ten":
            current_count = self._floor_count(self.count)
            score_plus = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, 10)
            )
            score_minus = _score_outcome(
                self, player, card.rank, self._new_count_with_delta(current_count, -10)
            )
            labels = self._choice_labels_for_values(
                "ten", self._choice_values_for_type("ten"), locale
            )
            return labels[0] if score_plus > score_minus else labels[1]
        return None

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Options are locked now; align card-slot/draw keybinds to them so the
        # keys offered match the actual hand size and draw mode.
        self._define_card_keybinds()

        # Set up teams (individual mode)
        active_players = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Initialize alive players
        self.alive_player_ids = [p.id for p in active_players]

        # Initialize player tokens
        for player in active_players:
            player.tokens = self.options.starting_tokens
        self._sync_team_scores()

        # Play music
        self.play_music("game_ninetynine/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self._get_round_timer().stop()
        self.cancel_sequences_by_tag(ROUND_TRANSITION_TAG)
        self.round += 1
        self.count = 0
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.pending_choice = None

        # Build and shuffle deck based on variant
        if self.is_standard_rules:
            self.deck, _ = DeckFactory.standard_deck()
        else:
            self.deck, _ = DeckFactory.n99_action_deck()
        self.discard_pile = []

        # Update alive players list
        self.alive_player_ids = [
            p.id
            for p in self.get_active_players()
            if isinstance(p, NinetyNinePlayer) and p.tokens > 0
        ]

        # Clear every hand first so eliminated players cannot keep stale cards
        # or stale touch-menu entries from earlier rounds, and close any draw
        # window left open from the previous round.
        for player in self.players:
            if isinstance(player, NinetyNinePlayer):
                player.hand = []
                player.draw_timeout_ticks = 0

        # Deal cards to alive players
        for player in self.alive_players:
            for _ in range(self.options.hand_size):
                card = self.deck.draw_one()
                if card:
                    player.hand.append(card)
            self._sort_hand(player)

        # Set turn order to alive players, rotating the first turn randomly.
        round_players = list(self.alive_players)
        if round_players:
            start_index = self._choose_round_start_index(len(round_players))
            round_players = round_players[start_index:] + round_players[:start_index]
        self.set_turn_players(round_players)

        self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")
        self.broadcast_l("ninetynine-round", buffer="game", round=self.round)

        self._start_turn()

    def _schedule_next_round(self) -> None:
        """Pause briefly before starting the next round."""
        if not self.game_active:
            return

        self.pending_choice = None
        self.pending_card_index = -1
        for player in self.players:
            if isinstance(player, NinetyNinePlayer):
                player.draw_timeout_ticks = 0
        self.cancel_sequences_by_tag(ROUND_TRANSITION_TAG)
        self.broadcast_l(
            "ninetynine-next-round-wait",
            buffer="game",
            seconds=ROUND_TRANSITION_SECONDS,
        )
        self._get_round_timer().start()
        self._update_all_turn_actions()
        self.refresh_menus()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        self._normalize_count_floor()
        player = self.current_player
        if not player:
            return
        if not isinstance(player, NinetyNinePlayer) or not self._is_alive_player(player):
            self._advance_turn()
            return

        # Check if player has cards
        if not player.hand:
            self._player_out_of_cards(player)
            return

        # Announce turn
        self.announce_turn()

        # Action cards: Check if player has any safe cards
        if not self.is_standard_rules and not self._has_safe_card(player):
            self._action_cards_no_safe_cards(player)
            return

        # Set up bot thinking
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

        self._update_all_turn_actions()
        self.refresh_menus()

    def _has_safe_card(self, player: NinetyNinePlayer) -> bool:
        """Check if player has any card that won't make them go over 99 (action cards)."""
        current_count = self._floor_count(self.count)
        for card in player.hand:
            if card.rank == N99_RANK_NINETY_NINE:
                return True

            value = self.calculate_card_value(card, current_count)
            if value is not None:
                new_count = self._new_count_with_delta(current_count, value)
                if MIN_COUNT <= new_count <= MAX_COUNT:
                    return True

        return False

    def _action_cards_no_safe_cards(self, player: NinetyNinePlayer) -> None:
        """Handle action cards auto-lose when player has no safe cards."""
        self.broadcast_personal_l(
            player,
            "ninetynine-you-no-valid-cards",
            "ninetynine-player-no-valid-cards",
            buffer="game",
        )

        winners = [alive_player for alive_player in self.alive_players if alive_player != player]
        self._play_outcome_sounds(
            winners=winners,
            losers=[player],
            win_sound="game_pig/win.ogg",
            lose_sound="game_ninetynine/lose2.ogg",
        )

        player.tokens = max(0, player.tokens - PENALTY_BUST_ACTION)
        self._announce_token_loss(player, PENALTY_BUST_ACTION)

        if player.tokens <= 0:
            self._eliminate_player(player)

        self._check_game_end()
        if self.game_active:
            self._schedule_next_round()

    def _advance_turn(self) -> None:
        """Advance to the next player's turn."""
        if not self.alive_players:
            return

        current_id = self.current_player.id if self.current_player else ""
        valid_ids = [
            pid
            for pid in self.turn_player_ids
            if (player := self.get_player_by_id(pid)) is not None
            and self._is_alive_player(player)
        ]
        if not valid_ids:
            return
        if valid_ids != self.turn_player_ids:
            self.turn_player_ids = valid_ids
            if current_id in self.turn_player_ids:
                self.turn_index = self.turn_player_ids.index(current_id)
            else:
                self.turn_index %= len(self.turn_player_ids)

        # Handle skip using base class mechanism
        while self.turn_skip_count > 0:
            self.turn_skip_count -= 1
            self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
            skipped = self.current_player
            if skipped:
                self.on_player_skipped(skipped)

        # Move to next player
        self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)

        # Make sure current player is still alive
        attempts = 0
        while attempts < len(self.turn_player_ids):
            player = self.current_player
            if player and self._is_alive_player(player):
                break
            self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
            attempts += 1

        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))
        self._start_turn()

    def _draw_card(self) -> Card | None:
        """Draw a card, recycling older discards while preserving the top discard."""
        if self.deck.is_empty():
            if not self.discard_pile:
                return None
            top_discard = self.discard_pile[-1]
            recycle_cards = self.discard_pile[:-1]
            if not recycle_cards:
                return None
            # Preserve the live top discard and recycle only older discards.
            self.deck.cards = recycle_cards
            self.discard_pile = [top_discard]
            self.deck.shuffle()

        return self.deck.draw_one()

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_play_card(self, player: Player, *args) -> None:
        """Handle playing a card."""
        if not isinstance(player, NinetyNinePlayer):
            return
        if self._is_round_transition_active() or not self._is_alive_player(player):
            return

        # Explicitly reject play if it's not their turn (since action is enabled to be visible)
        if self.current_player != player:
            user = self.get_user(player)
            if user:
                user.speak_l("action-not-your-turn", buffer="game")
            return

        if self.pending_choice is not None:
            return  # Must make choice first

        if len(args) == 1:
            action_id = args[0]
            input_value = None
        elif len(args) == 2:
            input_value, action_id = args
        else:
            return

        # Extract slot number
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]
        old_count = self._normalize_count_floor()
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Calculate value and check if choice is needed
        value = self.calculate_card_value(card, old_count)

        # Handle cards that need choice
        if card.rank == 1 and value is None:  # Ace needs choice
            resolved_value = None
            if input_value is not None:
                resolved_value = self._choice_value_from_input("ace", input_value, locale)
            if resolved_value is None:
                return
            self._play_card(
                player,
                slot,
                card,
                self._new_count_with_delta(old_count, resolved_value),
            )
            return

        if card.rank == 10 and value is None:  # Ten needs choice
            resolved_value = None
            if input_value is not None:
                resolved_value = self._choice_value_from_input("ten", input_value, locale)
            if resolved_value is None:
                return
            self._play_card(
                player,
                slot,
                card,
                self._new_count_with_delta(old_count, resolved_value),
            )
            return

        if card.rank == 2 and self.is_standard_rules:  # 2 card special handling
            new_count = self.calculate_two_effect(old_count)
            self._play_card(player, slot, card, new_count)
            return

        if card.rank == N99_RANK_NINETY_NINE and not self.is_standard_rules:
            self._play_card(player, slot, card, MAX_COUNT)
            return

        # Normal card play
        if value is None:
            value = 0
        self._play_card(player, slot, card, self._new_count_with_delta(old_count, value))

    def _action_resolve_pending_choice(self, player: Player, *args) -> None:
        """Resolve a legacy saved Ace/Ten choice through the standard action input menu."""
        if not isinstance(player, NinetyNinePlayer):
            return
        if self._is_round_transition_active() or not self._is_alive_player(player):
            return

        if len(args) == 1:
            action_id = args[0]
            input_value = None
        elif len(args) == 2:
            input_value, action_id = args
        else:
            return

        if self.current_player != player or self.pending_choice is None:
            user = self.get_user(player)
            if user and self.current_player != player:
                user.speak_l("action-not-your-turn", buffer="game")
            return

        slot = self.pending_card_index
        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if input_value is None:
            available_options = self._pending_choice_options(player)
            if len(available_options) == 1:
                input_value = available_options[0]
        value = self._choice_value_from_input(
            self.pending_choice,
            input_value,
            locale,
        )
        if value is None:
            return

        old_count = self._normalize_count_floor()
        self.pending_choice = None
        self.pending_card_index = -1
        self._play_card(player, slot, card, self._new_count_with_delta(old_count, value))

    def _play_card(
        self,
        player: NinetyNinePlayer,
        slot: int,
        card: Card,
        new_count: int,
    ) -> None:
        """Play a card with the calculated new count."""
        if self._is_round_transition_active() or not self._is_alive_player(player):
            return

        old_count = self._normalize_count_floor()
        new_count = self._floor_count(new_count)
        value = new_count - old_count

        # Remove card from hand
        player.hand.pop(slot)
        self.discard_pile.append(card)

        # Play card sound
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg", 70)

        # Announce the play
        # Announce the play (localized per player)
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            c_name = card_name_with_article(card, user.locale)
            
            if p == player:
                user.speak_l(
                    "ninetynine-you-play",
                    buffer="game",
                    card=c_name,
                    count=new_count,
                )
            else:
                user.speak_l(
                    "ninetynine-player-plays",
                    buffer="game",
                    player=player.name,
                    card=c_name,
                    count=new_count,
                )

        # Update count
        self.count = new_count

        # Check milestones and handle effects
        round_ended = self._check_milestones(player, old_count, new_count, value, card.rank)

        # Always check if game should end (someone may have been eliminated)
        self._check_game_end()
        if not self.game_active:
            return

        if round_ended:
            self._schedule_next_round()
            return

        # Apply special card effects (reverse, skip)
        self._apply_special_effects(player, card)

        # A milestone *pass* penalty on this very play can cost the player their
        # last token and eliminate them while the round still continues (e.g.
        # crossing 66 leaves the count at 67 but does not end the round). Such a
        # player must never be dealt a replacement card, so move straight past
        # them to the next living player.
        if not self._is_alive_player(player):
            self._update_all_turn_actions()
            self._advance_turn()
            return

        # Handle card drawing
        if self.options.autodraw:
            drawn = self._draw_card()
            if drawn:
                player.hand.append(drawn)
                self._sort_hand(player)
            self._update_all_turn_actions()
            self._advance_turn()
        else:
            # Manual draw mode: open a private draw window and pass the turn
            # immediately so play keeps flowing. The player tops their hand back
            # up during the next players' turns; bots draw after a short delay,
            # humans get the full window and simply forfeit the top-up if they
            # let it lapse (serviced in on_tick).
            if player.is_bot:
                player.draw_timeout_ticks = random.randint(15, 30)
            else:
                player.draw_timeout_ticks = DRAW_TIMEOUT_TICKS
                user = self.get_user(player)
                if user:
                    user.speak_l("ninetynine-draw-prompt", buffer="game")
            self._update_all_turn_actions()
            self._advance_turn()

    def _check_milestones(
        self,
        player: NinetyNinePlayer,
        old_count: int,
        new_count: int,
        value: int,
        card_rank: int,
    ) -> bool:
        """
        Check for milestones (33, 66, 99) and apply penalties.
        Returns True if round should end.
        """
        # Check for going over 99
        if new_count > MAX_COUNT:
            self._player_busts(player)
            return True

        # Landing on 99
        if new_count == MAX_COUNT:
            if self.is_standard_rules and value > 0:
                self._others_lose_tokens(player, PENALTY_MILESTONE_99, "99")
                return True

        # Only check 33/66 milestones in Quentin C with positive value
        if self.is_standard_rules and value > 0:
            passed_33 = old_count < MILESTONE_33 < new_count
            landed_33 = new_count == MILESTONE_33
            passed_66 = old_count < MILESTONE_66 < new_count
            landed_66 = new_count == MILESTONE_66

            if landed_33:
                self._others_lose_tokens(player, PENALTY_MILESTONE_33_66, "33")
            elif passed_33:
                self._player_loses_tokens(player, PENALTY_MILESTONE_PASS, "passed_33")

            if landed_66:
                self._others_lose_tokens(player, PENALTY_MILESTONE_33_66, "66")
            elif passed_66:
                self._player_loses_tokens(player, PENALTY_MILESTONE_PASS, "passed_66")

        return False

    def _others_lose_tokens(
        self, player: NinetyNinePlayer, amount: int, milestone: str
    ) -> None:
        """All other players lose tokens (milestone bonus for player)."""
        others = [p for p in self.alive_players if p != player]

        if milestone == "99":
            self._play_outcome_sounds(
                winners=[player],
                losers=others,
                win_sound="game_pig/win.ogg",
                lose_sound="game_ninetynine/lose2.ogg",
            )
        else:
            for table_player in self.players:
                user = self.get_user(table_player)
                if not user:
                    continue
                if table_player == player:
                    user.play_sound("game_ninetynine/lose1_other.ogg")
                elif table_player in others:
                    user.play_sound("game_ninetynine/lose1_you.ogg")
                else:
                    user.play_sound("game_ninetynine/lose1_other.ogg")

        for other in others:
            other.tokens = max(0, other.tokens - amount)
            self._announce_token_loss(other, amount)

            if other.tokens <= 0:
                self._eliminate_player(other)

    def _player_loses_tokens(
        self, player: NinetyNinePlayer, amount: int, reason: str
    ) -> None:
        """Player loses tokens (passing through milestone or busting)."""
        del reason
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            if table_player == player:
                user.play_sound("game_ninetynine/lose1_you.ogg")
            else:
                user.play_sound("game_ninetynine/lose1_other.ogg")

        player.tokens = max(0, player.tokens - amount)
        self._announce_token_loss(player, amount)

        if player.tokens <= 0:
            self._eliminate_player(player)

    def _player_busts(self, player: NinetyNinePlayer) -> None:
        """Player went over 99."""
        winners = [alive_player for alive_player in self.alive_players if alive_player != player]
        self._play_outcome_sounds(
            winners=winners,
            losers=[player],
            win_sound="game_pig/win.ogg",
            lose_sound="game_ninetynine/lose2.ogg",
        )

        amount = PENALTY_BUST if self.is_standard_rules else PENALTY_BUST_ACTION
        player.tokens = max(0, player.tokens - amount)
        self._announce_token_loss(player, amount)

        if player.tokens <= 0:
            self._eliminate_player(player)

    def _player_out_of_cards(self, player: NinetyNinePlayer) -> None:
        """Player has no cards on their turn."""
        if not self._is_alive_player(player):
            return

        winners = [alive_player for alive_player in self.alive_players if alive_player != player]
        self._play_outcome_sounds(
            winners=winners,
            losers=[player],
            win_sound="game_pig/win.ogg",
            lose_sound="game_ninetynine/lose2.ogg",
        )

        player.tokens = max(0, player.tokens - PENALTY_NO_CARDS)
        self._announce_token_loss(player, PENALTY_NO_CARDS)

        if player.tokens <= 0:
            self._eliminate_player(player)

        self._check_game_end()
        if self.game_active:
            self._schedule_next_round()

    def _announce_token_loss(self, player: NinetyNinePlayer, amount: int) -> None:
        """Announce token loss."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            if listener == player:
                user.speak_l("ninetynine-you-lose-tokens", buffer="game", amount=amount)
            else:
                user.speak_l("ninetynine-player-loses-tokens", buffer="game", player=player.name, amount=amount)
        self._sync_team_scores()

    def _sync_team_scores(self) -> None:
        """Mirror player tokens into TeamManager totals for scoreboard output."""
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.tokens

    def _eliminate_player(self, player: NinetyNinePlayer) -> None:
        """Eliminate a player from the game."""
        self.broadcast_personal_l(
            player,
            "ninetynine-you-eliminated",
            "ninetynine-player-eliminated",
            buffer="game",
        )

        if player.id in self.alive_player_ids:
            self.alive_player_ids.remove(player.id)
        player.hand = []
        player.draw_timeout_ticks = 0
        if self.current_player == player:
            self.pending_choice = None
            self.pending_card_index = -1
        self._update_turn_actions(player)

    def _apply_special_effects(self, player: NinetyNinePlayer, card: Card) -> None:
        """Apply special card effects (reverse, skip)."""
        rank = card.rank

        if self.is_standard_rules:
            if rank == 4 and len(self.alive_players) > 2:
                self.reverse_turn_direction()
                self.broadcast_l("ninetynine-direction-reverses", buffer="game")
            if rank == 11:  # Jack skips
                self.skip_next_players(1)
        else:
            if rank == N99_RANK_REVERSE and len(self.alive_players) > 2:
                self.reverse_turn_direction()
                self.broadcast_l("ninetynine-direction-reverses", buffer="game")
            if rank == N99_RANK_SKIP:
                self.skip_next_players(1)

    def _check_game_end(self) -> None:
        """Check if the game should end."""
        alive = [p for p in self.get_active_players() if p.tokens > 0]

        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)

    def _end_game(self, winner: NinetyNinePlayer | None) -> None:
        """End the game with a winner."""
        self._get_round_timer().stop()
        self.cancel_sequences_by_tag(ROUND_TRANSITION_TAG)
        self.play_sound("game_pig/win.ogg")

        if winner:
            self.broadcast_personal_l(
                winner,
                "ninetynine-you-win",
                "ninetynine-player-wins",
                buffer="game",
            )

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with NinetyNine-specific data."""
        sorted_players = sorted(
            self.get_active_players(), key=lambda p: p.tokens, reverse=True
        )

        # Build final tokens
        final_tokens = {}
        for p in sorted_players:
            nn_p: NinetyNinePlayer = p  # type: ignore
            final_tokens[p.name] = nn_p.tokens

        winner = sorted_players[0] if sorted_players else None
        winner_nn: NinetyNinePlayer = winner  # type: ignore

        return GameResult(
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
                "winner_name": winner.name if winner else None,
                "winner_tokens": winner_nn.tokens if winner_nn else 0,
                "final_tokens": final_tokens,
                "rounds_played": self.round,
                "starting_tokens": self.options.starting_tokens,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for NinetyNine game."""


        lines = [Localization.get(locale, "game-final-scores")]

        final_tokens = result.custom_data.get("final_tokens", {})
        for i, (name, tokens) in enumerate(final_tokens.items(), 1):
            lines.append(
                Localization.get(
                    locale, "ninetynine-end-score", rank=i, player=name, tokens=tokens
                )
            )

        return lines

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        """Handle manual card draw."""
        if not isinstance(player, NinetyNinePlayer):
            return
        if self._is_round_transition_active() or not self._is_alive_player(player):
            return

        # The draw window is open only while draw_timeout_ticks > 0. The turn has
        # already moved on, so drawing tops the hand back up without touching the
        # turn order.
        if player.draw_timeout_ticks <= 0:
            return

        drawn = self._draw_card()
        drawn_slot_id: str | None = None
        if drawn:
            player.hand.append(drawn)
            self._sort_hand(player)

            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")

            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue

                if p == player:
                    c_name = card_name_with_article(drawn, user.locale)
                    user.speak_l("ninetynine-you-draw", buffer="game", card=c_name)
                else:
                    user.speak_l("ninetynine-player-draws", buffer="game", player=player.name)

            # Slot id of the card just drawn, so the drawer's cursor lands on it.
            try:
                drawn_slot_id = f"card_slot_{player.hand.index(drawn) + 1}"
            except ValueError:
                drawn_slot_id = None
        else:
            user = self.get_user(player)
            if user:
                user.speak_l("ninetynine-no-card-to-draw", buffer="game")

        player.draw_timeout_ticks = 0
        # Focus-preserving refresh: the drawer is a background player and the
        # current player is mid-turn — a full rebuild would yank their cursor.
        # The drawer lands on the card they drew; everyone else keeps their focus.
        self._update_all_turn_actions()
        for p in self.players:
            if not isinstance(p, NinetyNinePlayer):
                continue
            if p.id == player.id and drawn_slot_id is not None:
                self.request_menu_focus(p, drawn_slot_id)
            else:
                self.refresh_menus(p)

    def _action_check_count(self, player: Player, action_id: str) -> None:
        """Announce the current count."""
        self._normalize_count_floor()
        user = self.get_user(player)
        if user:
            user.speak_l("ninetynine-current-count", buffer="game", count=self.count)

    def _action_pause_timer(self, player: Player, action_id: str) -> None:
        """Handle host pause/skip for the between-round timer."""
        if player.name == self.host:
            self._get_round_timer().toggle_pause(player.name)

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        """Handle delayed round-transition callbacks."""
        if callback_id == START_ROUND_CALLBACK:
            if self.game_active:
                self._start_round()
            return
        super().on_sequence_callback(sequence_id, callback_id, payload)

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if not self.game_active:
            return

        self._get_round_timer().on_tick()
        if self._is_round_transition_active() or self.is_sequence_bot_paused():
            return

        # Service per-player manual-draw windows. The turn has already advanced,
        # so these resolve in the background while play continues; several can be
        # open at once.
        for player in list(self.alive_players):
            ticks = player.draw_timeout_ticks
            if ticks <= 0:
                continue

            if player.is_bot:
                # Bot draws the moment its short delay elapses, while the window
                # is still open so the draw isn't rejected as stale.
                if ticks <= 1:
                    self._action_draw_card(player, "draw_card")
                    if not self.game_active:
                        return
                else:
                    player.draw_timeout_ticks = ticks - 1
                continue

            player.draw_timeout_ticks = ticks - 1
            if player.draw_timeout_ticks <= 0:
                # Human let the window lapse: the top-up is forfeited. If that
                # leaves them empty-handed, they are out of cards.
                if len(player.hand) == 0:
                    self._player_out_of_cards(player)
                    if not self.game_active:
                        return
                else:
                    self._update_turn_actions(player)
                    self.refresh_menus(player)

        BotHelper.on_tick(self)

    def bot_think(self, player: NinetyNinePlayer) -> str | None:
        """Bot AI decision making - delegates to bot module."""
        return _bot_think(self, player)
