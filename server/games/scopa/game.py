"""
Scopa Card Game Implementation for PlayAural v0.1.0.

Classic Italian card game: capture cards from the table by matching ranks or sums.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.cards import (
    Card,
    Deck,
    DeckFactory,
    card_name,
    read_cards,
    sort_cards,
)
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import (
    IntOption,
    MenuOption,
    BoolOption,
    TeamModeOption,
    option_field,
)
from ...game_utils.teams import TeamManager, Team
from ...game_utils.round_timer import RoundTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

# Modular components
from .capture import find_captures, select_best_capture, get_capture_hint
from .scoring import score_round, check_winner, declare_winner
from .bot import bot_think


@dataclass
class ScopaPlayer(Player):
    """Player state for Scopa game."""

    hand: list[Card] = field(default_factory=list)
    captured: list[Card] = field(default_factory=list)


@dataclass
class ScopaOptions(GameOptions):
    """Options for Scopa game using declarative option system."""

    target_score: int = option_field(
        IntOption(
            default=11,
            min_val=1,
            max_val=121,
            value_key="score",
            label="game-set-target-score",
            prompt="scopa-enter-target-score",
            change_msg="game-option-changed-target",
        )
    )
    cards_per_deal: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            value_key="cards",
            label="scopa-set-cards-per-deal",
            prompt="scopa-enter-cards-per-deal",
            change_msg="scopa-option-changed-cards",
        )
    )
    number_of_decks: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=6,
            value_key="decks",
            label="scopa-set-decks",
            prompt="scopa-enter-decks",
            change_msg="scopa-option-changed-decks",
        )
    )
    escoba: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="scopa-toggle-escoba",
            change_msg="scopa-option-changed-escoba",
        )
    )
    show_capture_hints: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="scopa-toggle-hints",
            change_msg="scopa-option-changed-hints",
        )
    )
    scopa_mechanic: str = option_field(
        MenuOption(
            default="normal",
            value_key="mechanic",
            choices=["normal", "no_scopas", "only_scopas"],
            choice_labels={
                "normal": "scopa-mechanic-normal",
                "no_scopas": "scopa-mechanic-no_scopas",
                "only_scopas": "scopa-mechanic-only_scopas",
            },
            label="scopa-set-mechanic",
            prompt="scopa-select-mechanic",
            change_msg="scopa-option-changed-mechanic",
        )
    )
    instant_win_scopas: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="scopa-toggle-instant-win",
            change_msg="scopa-option-changed-instant",
        )
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=lambda g, p: TeamManager.get_all_team_modes(2, 6),
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
        )
    )
    team_card_scoring: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="scopa-toggle-team-scoring",
            change_msg="scopa-option-changed-team-scoring",
        )
    )
    inverse_scopa: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="scopa-toggle-inverse",
            change_msg="scopa-option-changed-inverse",
        )
    )


@dataclass
@register_game
class ScopaGame(Game):
    """
    Scopa card game.

    Players take turns playing cards from their hand. If the played card matches
    a table card by rank, or if table cards sum to the played card's value,
    those cards are captured. Clearing all table cards scores a "scopa" point.
    Points are also awarded for most cards, most diamonds, the 7 of diamonds,
    and most 7s.
    """

    players: list[ScopaPlayer] = field(default_factory=list)
    options: ScopaOptions = field(default_factory=ScopaOptions)

    # Game state
    deck: Deck = field(default_factory=Deck)
    table_cards: list[Card] = field(default_factory=list)
    last_capture_player_id: str | None = None  # Player ID of last capturer
    dealer_index: int = 0
    current_round: int = 0
    _current_deal: int = 0  # Current deal number in round
    _total_deals: int = 0  # Total deals in round

    def __post_init__(self):
        """Initialize runtime state."""
        super().__post_init__()
        # Round timer for delays between rounds (state is in game fields)
        self._round_timer = RoundTimer(self)

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()
        # Rebuild round timer
        self._round_timer = RoundTimer(self)

    def on_round_timer_ready(self) -> None:
        """Called when round timer expires. Start the next round."""
        self._start_round()

    @classmethod
    def get_name(cls) -> str:
        return "Scopa"

    @classmethod
    def get_type(cls) -> str:
        return "scopa"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 16

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ScopaPlayer:
        """Create a new player with Scopa-specific state."""
        return ScopaPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: ScopaPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Dynamic card actions will be created per-turn
        # Dynamic card actions will be created per-turn
        
        # WEB-SPECIFIC: Moved to Standard Action Set for Web
        is_web = user and getattr(user, "client_type", "") == "web"
        if not is_web:
            # Add info actions (hidden from menu)
            action_set.add(
                Action(
                    id="view_table",
                    label=Localization.get(locale, "scopa-view-table"),
                    handler="_action_view_table",
                    is_enabled="_is_view_enabled",
                    is_hidden="_is_view_hidden",
                )
            )
            action_set.add(
                Action(
                    id="view_captured",
                    label=Localization.get(locale, "scopa-view-captured"),
                    handler="_action_view_captured",
                    is_enabled="_is_view_enabled",
                    is_hidden="_is_view_hidden",
                )
            )
        
        # Note: whose_turn, check_scores, check_scores_detailed are in base class standard set

        # View individual table cards (0-9 keys)
        for i in range(10):
            card_idx = i if i > 0 else 10
            action_set.add(
                Action(
                    id=f"view_table_card_{i}",
                    label=Localization.get(locale, "scopa-view-table-card", index=card_idx),
                    handler="_action_view_table_card",
                    is_enabled="_is_view_enabled",
                    is_hidden="_is_view_hidden",
                )
            )

        # Host-only pause timer action (hidden from menu)
        action_set.add(
            Action(
                id="pause_timer",
                label=Localization.get(locale, "scopa-pause-timer"),
                handler="_action_pause_timer",
                is_enabled="_is_pause_timer_enabled",
                is_hidden="_is_pause_timer_hidden",
            )
        )

        return action_set

    # Options are now defined declaratively in ScopaOptions - no need to override
    # create_options_action_set as the base class handles it automatically

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["view_table", "view_captured", "check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            locale = user.locale

            # Ensure 'view_table' is in standard set (moved from turn set for web)
            if not action_set.get_action("view_table"):
                 action_set.add(
                    Action(
                        id="view_table",
                        label=Localization.get(locale, "scopa-view-table"),
                        handler="_action_view_table",
                        is_enabled="_is_view_enabled",
                        is_hidden="_is_check_table_hidden", # Use new visibility method
                    )
                )

            # Ensure 'view_captured' is in standard set
            if not action_set.get_action("view_captured"):
                 action_set.add(
                    Action(
                        id="view_captured",
                        label=Localization.get(locale, "scopa-view-captured"),
                        handler="_action_view_captured",
                        is_enabled="_is_view_enabled",
                        is_hidden="_is_check_captured_hidden", # Use new visibility method
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
        # Base class has t/s/shift+s for whose_turn/check_scores/check_scores_detailed
        super().setup_keybinds()

        # Scopa-specific info keybinds
        self.define_keybind(
            "c",
            "View table cards",
            ["view_table"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            "View captured cards",
            ["view_captured"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Number keys to view specific table cards
        for i in range(1, 10):
            self.define_keybind(
                str(i),
                f"View table card {i}",
                [f"view_table_card_{i}"],
                state=KeybindState.ACTIVE,
                include_spectators=True,
            )
        self.define_keybind(
            "0",
            "View table card 10",
            ["view_table_card_0"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Host-only pause keybind (hidden from menu)
        self.define_keybind(
            "p", "Pause/skip round timer", ["pause_timer"], state=KeybindState.ACTIVE
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_view_enabled(self, player: Player) -> str | None:
        """View actions are enabled during play."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_hidden(self, player: Player) -> Visibility:
        """View actions are always hidden (keybind only)."""
        return Visibility.HIDDEN

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

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_check_captured_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_pause_timer_enabled(self, player: Player) -> str | None:
        """Pause timer is enabled for host when timer is active."""
        if player.name != self.host:
            return "action-not-host"
        if not self._round_timer.is_active:
            return "scopa-timer-not-active"
        return None

    def _is_pause_timer_hidden(self, player: Player) -> Visibility:
        """Pause timer is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_card_action_enabled(self, player: Player) -> str | None:
        """Card actions are visibly enabled during play so they show up."""
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_card_action_hidden(self, player: Player) -> Visibility:
        """Card actions are visible for current player during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        # Allow visibility even if not current player (handler rejects out-of-turn play)
        return Visibility.VISIBLE

    def _get_card_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for a card action."""
        if not isinstance(player, ScopaPlayer):
            return ""
        # Extract card ID from action_id (e.g., "play_card_42" -> 42)
        try:
            card_id = int(action_id.split("_")[-1])
        except (ValueError, IndexError):
            return ""
        # Find card in player's hand
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return ""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        name = card_name(card, locale)
        if self.options.show_capture_hints:
            hint = get_capture_hint(
                self.table_cards, card, self.options.escoba, locale
            )
            name += hint
        return name

    def _update_card_actions(self, player: ScopaPlayer) -> None:
        """Update card actions for a player (called when rebuilding menus)."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        is_playing = self.status == "playing"
        is_spectator = player.is_spectator
        is_current = self.current_player == player

        # Remove old card actions
        turn_set.remove_by_prefix("play_card_")

        # Add card actions for current player AND waiting players (so they can see hand)
        # Use dynamic label to ensure locale changes are reflected
        if is_playing and not is_spectator:
            for card in sort_cards(player.hand, by_suit=False):
                turn_set.add(
                    Action(
                        id=f"play_card_{card.id}",
                        label="",  # Fallback, dynamic label used instead
                        handler="_action_play_card",
                        is_enabled="_is_card_action_enabled",
                        is_hidden="_is_card_action_hidden",
                        get_label="_get_card_label",
                    )
                )

    def _update_all_card_actions(self) -> None:
        """Update card actions for all players."""
        for player in self.players:
            self._update_card_actions(player)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        # Validate team mode for current player count
        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)

        # Ensure there are enough cards in the deck for the initial deal
        active_players = self.get_active_players()
        num_players = len(active_players)
        cards_per_deck = 40  # Italian deck
        total_cards = cards_per_deck * self.options.number_of_decks
        cards_needed = self.options.cards_per_deal * num_players

        if cards_needed > total_cards:
            errors.append((
                "scopa-error-not-enough-cards",
                {
                    "decks": self.options.number_of_decks,
                    "players": num_players,
                    "cards_per_deal": self.options.cards_per_deal,
                    "total_cards": total_cards,
                    "cards_needed": cards_needed,
                }
            ))

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.current_round = 0

        # Setup teams
        active_players = self.get_active_players()
        player_names = [p.name for p in active_players]
        # options.team_mode should be in internal format, but handle old display format for backwards compatibility
        team_mode = self.options.team_mode
        # If it contains spaces or uppercase (except 'v'), it's likely old display format
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)
        self._team_manager.team_mode = team_mode
        self._team_manager.setup_teams(player_names)

        # Initialize turn order
        self.set_turn_players(active_players)

        # Reset player state
        for player in active_players:
            player.captured = []
            player.hand = []

        self.team_manager.reset_all_scores()

        # Play music
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _broadcast_cards_l(
        self,
        message_id: str,
        cards: list[Card] | None = None,
        card: Card | None = None,
        exclude: ScopaPlayer | None = None,
        buffer: str = "game",
        **kwargs,
    ) -> None:
        """Broadcast a message with per-user localized card names."""
        for player in self.players:
            if player is exclude:
                continue
            user = self.get_user(player)
            if user:
                msg_kwargs = dict(kwargs)
                if cards is not None:
                    msg_kwargs["cards"] = read_cards(cards, user.locale)
                if card is not None:
                    msg_kwargs["card"] = card_name(card, user.locale)
                user.speak_l(message_id, buffer=buffer, **msg_kwargs)

    def broadcast_team_l(
        self,
        message_id: str,
        team: Team,
        exclude: ScopaPlayer | None = None,
        **kwargs,
    ) -> None:
        """Broadcast a message with localized team name."""
        for player in self.players:
            if player is exclude:
                continue
            user = self.get_user(player)
            if user:
                # Localize team name for this user
                team_name = self.team_manager.get_team_name(team, user.locale)
                user.speak_l(message_id, player=team_name, **kwargs)

    def _create_deck(self) -> None:
        """Create and shuffle the deck."""
        self.deck, _ = DeckFactory.italian_deck(self.options.number_of_decks)
        # Play shuffle sound
        shuffle_sound = random.choice(["shuffle1.ogg", "shuffle2.ogg", "shuffle3.ogg"])
        self.play_sound(f"game_cards/{shuffle_sound}")

    def _start_round(self) -> None:
        """Start a new round."""
        self.current_round += 1
        self.last_capture_player_id = None

        # Reset player state for round
        for player in self.get_active_players():
            player.captured = []
            player.hand = []

        self.team_manager.reset_round_scores()
        self.table_cards = []

        # Announce round
        self.broadcast_l("game-round-start", round=self.current_round)

        # Rotate dealer (rightmost/last player, moves left/decreases)
        active_players = self.get_active_players()
        self.dealer_index = (
            (self.dealer_index - 1) % len(active_players) if active_players else 0
        )
        dealer = active_players[self.dealer_index] if active_players else None

        # Announce dealer
        if dealer:
            self.broadcast_personal_l(dealer, "game-you-deal", "game-player-deals")

        # Create and shuffle deck
        self._create_deck()

        # Calculate deal tracking
        total_cards = self.deck.size()
        cards_for_players = (
            self.options.cards_per_deal * len(active_players) if active_players else 1
        )
        initial_table = total_cards % cards_for_players if cards_for_players > 0 else 0
        cards_after_table = total_cards - initial_table
        self._total_deals = (
            cards_after_table // cards_for_players if cards_for_players > 0 else 0
        )
        self._current_deal = 0

        # For standard scopa, avoid too many 10s on table (re-shuffle if needed)
        if not self.options.escoba:
            max_attempts = 10
            for _ in range(max_attempts):
                self.table_cards = self.deck.draw(initial_table)
                tens_count = sum(1 for c in self.table_cards if c.rank == 10)
                total_tens = 4 * self.options.number_of_decks
                max_tens = total_tens // 2 + 1
                if tens_count <= max_tens:
                    break
                # Re-shuffle and try again
                self.deck.add(self.table_cards)
                self.deck.shuffle()
        else:
            self.table_cards = self.deck.draw(initial_table)

        if self.table_cards:
            self._broadcast_cards_l("scopa-initial-table", cards=self.table_cards)
        else:
            self.broadcast_l("scopa-no-initial-table")

        # Set starting player (player after dealer)
        if active_players:
            self.turn_index = (self.dealer_index + 1) % len(active_players)

        # Deal cards to players
        self._deal_cards()

    def _deal_cards(self) -> None:
        """Deal cards to all active players."""
        active_players = self.get_active_players()
        if not active_players or self.deck.is_empty():
            return

        # Increment deal counter
        self._current_deal += 1

        # Play small shuffle sound for deals after the first
        if self._current_deal > 1:
            self.play_sound("game_cards/small_shuffle.ogg")

        # Announce deal counter
        self.broadcast_l(
            "game-deal-counter", current=self._current_deal, total=self._total_deals
        )

        cards_to_deal = self.options.cards_per_deal

        for player in active_players:
            cards = self.deck.draw(cards_to_deal)
            player.hand.extend(cards)

        # Reset to the player after the dealer for each deal within the round
        # (Traditional scopa: play order only rotates once per round, not per deal)
        self.turn_index = (self.dealer_index + 1) % len(active_players)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        # Announce turn (plays sound and broadcasts message)
        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 25))

        self._update_all_card_actions()
        self.rebuild_all_menus()

    def _play_card(self, player: ScopaPlayer, card: Card) -> None:
        """Handle playing a card."""
        # Remove card from hand
        player.hand = [c for c in player.hand if c.id != card.id]

        # Play sound
        play_sound = random.choice(["play1.ogg", "play2.ogg", "play3.ogg", "play4.ogg"])
        self.play_sound(f"game_cards/{play_sound}")

        # Find and execute capture
        captures = find_captures(self.table_cards, card.rank, self.options.escoba)

        if captures:
            best_capture = select_best_capture(captures)
            self._execute_capture(player, card, best_capture)
        else:
            # No capture, card goes to table
            self.table_cards.append(card)

            # Personal message for player
            user = self.get_user(player)
            if user:
                user.speak_l("scopa-you-put-down", buffer="game", card=card_name(card, user.locale))

            # Broadcast to others
            self._broadcast_cards_l(
                "scopa-player-puts-down", card=card, player=player.name, exclude=player
            )

        BotHelper.jolt_bots(self, ticks=random.randint(8, 15))
        self._end_turn()

    def _execute_capture(
        self, player: ScopaPlayer, played_card: Card, captured: list[Card]
    ) -> None:
        """Execute a capture."""
        # Remove captured cards from table
        for card in captured:
            self.table_cards = [c for c in self.table_cards if c.id != card.id]

        # Add to player's captured pile
        player.captured.append(played_card)
        player.captured.extend(captured)
        self.last_capture_player_id = player.id

        # Play capture sound with pitch based on cards captured
        num_captured = len(captured)
        is_scopa = len(self.table_cards) == 0

        if is_scopa:
            pitch = 200  # 2x for scopa
        else:
            # Calculate pitch: 100 for 1 card, 110 for 2, 120 for 3, etc.
            pitch = min(100 + (num_captured - 1) * 10, 190)

        self.play_sound("mention.ogg", pitch=pitch, volume=50)

        # Determine suffix key based on scopa status
        suffix_key = None
        if is_scopa:
            if self.options.scopa_mechanic != "no_scopas":
                suffix_key = "scopa-scopa-suffix"
                # Award point to team
                self.team_manager.add_to_team_score(player.name, 1)
            else:
                suffix_key = "scopa-clear-table-suffix"

        # Send per-user localized capture messages
        for p in self.players:
            usr = self.get_user(p)
            if not usr:
                continue

            captured_str = read_cards(captured, usr.locale)
            card_str = card_name(played_card, usr.locale)
            suffix = Localization.get(usr.locale, suffix_key) if suffix_key else ""

            if p is player:
                msg = (
                    Localization.get(
                        usr.locale,
                        "scopa-you-collect",
                        cards=captured_str,
                        card=card_str,
                    )
                    + suffix
                )
            else:
                msg = (
                    Localization.get(
                        usr.locale,
                        "scopa-player-collects",
                        player=player.name,
                        cards=captured_str,
                        card=card_str,
                    )
                    + suffix
                )
            usr.speak(msg, buffer="game")

        # Check for instant win
        if (
            is_scopa
            and self.options.scopa_mechanic != "no_scopas"
            and self.options.instant_win_scopas
        ):
            team = self.team_manager.get_team(player.name)
            if team and team.total_score >= self.options.target_score:
                declare_winner(self, team)
                return

    def _end_turn(self) -> None:
        """Handle end of a player's turn."""
        active_players = self.get_active_players()

        # Check if all players are out of cards
        all_empty_hands = all(len(p.hand) == 0 for p in active_players)

        if all_empty_hands:
            if self.deck.is_empty():
                # Round is over
                self._end_round()
            else:
                # Deal more cards
                self._deal_cards()
        else:
            # Next player (don't announce yet, _start_turn will do it)
            self.advance_turn(announce=False)
            self._start_turn()

    def _end_round(self) -> None:
        """Handle end of a round."""
        # Give remaining table cards to last capturer
        if self.table_cards and self.last_capture_player_id:
            last_capturer = self.get_player_by_id(self.last_capture_player_id)
            if last_capturer:
                self.broadcast_l("scopa-remaining-cards", player=last_capturer.name)
                last_capturer.captured.extend(self.table_cards)
                self.table_cards = []

        self.broadcast_l("game-round-end", round=self.current_round)

        # Score the round
        if self.options.scopa_mechanic != "only_scopas":
            score_round(self)

        # Commit round scores to total
        self.team_manager.commit_round_scores()

        # Check for winner
        winner = check_winner(self)
        if winner:
            declare_winner(self, winner)
        else:
            # Start timer for next round
            self._round_timer.start()
            self._update_all_card_actions()
            self.rebuild_all_menus()

    # ==========================================================================
    # Game Result
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        """Build the game result with Scopa-specific data."""
        sorted_teams = self.team_manager.get_sorted_teams(by_score=True, descending=True)

        # Build final scores and team data
        final_scores = {}
        team_rankings = []
        for team in sorted_teams:
            name = self.team_manager.get_team_name(team)
            final_scores[name] = team.total_score
            team_rankings.append({
                "index": team.index,
                "members": team.members,
                "score": team.total_score,
                "name": name # fallback
            })

        winner = sorted_teams[0] if sorted_teams else None

        winner_ids = []
        if winner:
            # Map member names to player IDs
            active_players = self.get_active_players()
            name_to_id = {p.name: p.id for p in active_players}
            for member_name in winner.members:
                if member_name in name_to_id:
                    winner_ids.append(name_to_id[member_name])

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
                "winner_name": self.team_manager.get_team_name(winner) if winner else None,
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "team_mode": self.options.team_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Scopa game."""
        lines = [Localization.get(locale, "game-final-scores")]

        # Use team_rankings if available (for proper localization)
        team_rankings = result.custom_data.get("team_rankings")
        
        if team_rankings:
            for i, team_data in enumerate(team_rankings, 1):
                members = team_data.get("members", [])
                index = team_data.get("index", 0)
                score = team_data.get("score", 0)
                
                # Determine display name
                if len(members) == 1:
                    name = members[0]
                else:
                    name = Localization.get(locale, "game-team-name", index=index + 1)
                
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(locale, "scopa-line-format", rank=i, player=name, points=points_str)
                )
        else:
            # Fallback for old results
            final_scores = result.custom_data.get("final_scores", {})
            for i, (name, score) in enumerate(final_scores.items(), 1):
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(locale, "scopa-line-format", rank=i, player=name, points=points_str)
                )

        return lines

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI and round timer."""
        super().on_tick()

        if not self.game_active:
            return
        # Tick round timer
        self._round_timer.on_tick()
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Bot AI decision making - delegated to bot module."""
        if not isinstance(player, ScopaPlayer):
            return None
        return bot_think(self, player)

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_play_card(self, player: Player, action_id: str) -> None:
        """Handle playing a card - extracts card ID from action_id."""
        if not isinstance(player, ScopaPlayer):
            return

        # Explicitly reject play if it's not their turn (since action is enabled to be visible)
        if self.current_player != player:
            return

        # Extract card ID from action_id (e.g., "play_card_42" -> 42)
        try:
            card_id = int(action_id.removeprefix("play_card_"))
        except ValueError:
            return

        # Find the card in player's hand
        card = next((c for c in player.hand if c.id == card_id), None)
        if card:
            self._play_card(player, card)

    def _action_view_table(self, player: Player, action_id: str) -> None:
        """View all table cards."""
        user = self.get_user(player)
        if user:
            if self.table_cards:
                cards_str = read_cards(self.table_cards, user.locale)
                user.speak(cards_str)
            else:
                user.speak_l("scopa-table-empty")

    def _action_view_table_card(self, player: Player, action_id: str) -> None:
        """View a specific table card."""
        user = self.get_user(player)
        if not user:
            return

        # Extract card number from action ID
        try:
            num = int(action_id.replace("view_table_card_", ""))
            if num == 0:
                num = 10
        except ValueError:
            return

        if num <= len(self.table_cards):
            card = self.table_cards[num - 1]
            user.speak(card_name(card, user.locale))
        else:
            user.speak_l("scopa-no-such-card")

    def _action_view_captured(self, player: Player, action_id: str) -> None:
        """View captured card count."""
        user = self.get_user(player)
        if user and isinstance(player, ScopaPlayer):
            count = len(player.captured)
            user.speak_l("scopa-captured-count", count=count)

    def _action_pause_timer(self, player: Player, action_id: str) -> None:
        """Handle pause timer action (host only)."""
        if player.name == self.host:
            self._round_timer.toggle_pause(player.name)

    # Note: _action_check_scores, _action_check_scores_detailed, _action_whose_turn
    # are now provided by the base Game class using TeamManager

    # Options are now handled by the declarative system in GameOptions
