from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import Optional

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...game_utils.cards import (
    Card,
    Deck,
    SUIT_CLUBS,
    SUIT_DIAMONDS,
    SUIT_HEARTS,
    SUIT_SPADES,
)

from .player import NinePlayer
from .state import NineState, SequenceState


# Card Ranks for Nine: 6, 7, 8, 9, 10, J, Q, K, A
# Using standard ranks 1-13, but mapping 1 (Ace) to a higher internal value for comparison.
RANK_SIX = 6
RANK_SEVEN = 7
RANK_EIGHT = 8
RANK_NINE = 9
RANK_TEN = 10
RANK_JACK = 11
RANK_QUEEN = 12
RANK_KING = 13
RANK_ACE = 1  # Standard Ace rank

# Internal mapping for comparison (Ace is highest)
NINE_RANK_ORDER = {
    RANK_SIX: 6,
    RANK_SEVEN: 7,
    RANK_EIGHT: 8,
    RANK_NINE: 9,
    RANK_TEN: 10,
    RANK_JACK: 11,
    RANK_QUEEN: 12,
    RANK_KING: 13,
    RANK_ACE: 14,  # Ace is highest in Nine
}

# Ordered list of ranks for easy iteration and checking adjacency
NINE_RANKS_IN_ORDER = [
    RANK_SIX,
    RANK_SEVEN,
    RANK_EIGHT,
    RANK_NINE,
    RANK_TEN,
    RANK_JACK,
    RANK_QUEEN,
    RANK_KING,
    RANK_ACE,
]

# Map standard ranks to localization keys
NINE_RANK_KEYS = {
    RANK_SIX: "rank-six",
    RANK_SEVEN: "rank-seven",
    RANK_EIGHT: "rank-eight",
    RANK_NINE: "rank-nine",
    RANK_TEN: "rank-ten",
    RANK_JACK: "rank-jack",
    RANK_QUEEN: "rank-queen",
    RANK_KING: "rank-king",
    RANK_ACE: "rank-ace",
}

# Suit localization keys (from game_utils.cards)
SUIT_KEYS = {
    SUIT_DIAMONDS: "suit-diamonds",
    SUIT_CLUBS: "suit-clubs",
    SUIT_HEARTS: "suit-hearts",
    SUIT_SPADES: "suit-spades",
}

SUPPORTED_PLAYER_COUNTS = {3, 4, 6}
STARTING_NINE_SUIT = SUIT_DIAMONDS
CARD_ACTION_PREFIX = "play_card_"
SEQUENCE_SUIT_ORDER = [SUIT_DIAMONDS, SUIT_CLUBS, SUIT_HEARTS, SUIT_SPADES]


@dataclass
@register_game
class NineGame(Game):
    "nine-description"

    #    Nine - A card game where players form sequences.

    relevant_preferences = ["brief_announcements"]

    players: list[NinePlayer] = field(default_factory=list)
    nine_state: NineState = field(default_factory=NineState)

    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)

    # Game state variables
    game_active: bool = False
    first_turn_player_id: Optional[str] = None  # Player who has the opening nine

    def __post_init__(self):
        """Initialize runtime state."""
        super().__post_init__()

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()

    @classmethod
    def get_name(cls) -> str:
        return "Nine"

    @classmethod
    def get_type(cls) -> str:
        return "nine"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 3

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> NinePlayer:
        """Create a new player."""
        return NinePlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Deck and Card Utilities
    # ==========================================================================

    def _build_nine_deck(self) -> Deck:
        """
        Create a 36-card deck for Nine (6s through Aces).
        """
        cards = []
        card_id_counter = 0
        for suit in [SUIT_CLUBS, SUIT_DIAMONDS, SUIT_HEARTS, SUIT_SPADES]:
            for rank in NINE_RANKS_IN_ORDER:
                card = Card(id=card_id_counter, rank=rank, suit=suit)
                cards.append(card)
                card_id_counter += 1
        return Deck(cards=cards)

    def _get_card_nine_value(self, card: Card) -> int:
        """Get the internal value of a card for Nine game logic (Ace is highest)."""
        return NINE_RANK_ORDER.get(card.rank, 0)  # Default to 0 for unknown ranks

    def _get_localized_rank_name(self, rank: int, locale: str = "en") -> str:
        """Get localized name for a card rank specific to Nine."""
        key = NINE_RANK_KEYS.get(rank)
        if key:
            return Localization.get(locale, key)
        return str(rank)  # Fallback to number if not found

    def _get_localized_suit_name(self, suit: int, locale: str = "en") -> str:
        """Get localized name for a card suit."""
        key = SUIT_KEYS.get(suit)
        if key:
            return Localization.get(locale, key)
        return str(suit)  # Fallback to number if not found

    def _get_localized_card_name(self, card: Card, locale: str = "en") -> str:
        """Get localized full card name (e.g., 'Nine of Clubs')."""
        rank_name = self._get_localized_rank_name(card.rank, locale)
        suit_name = self._get_localized_suit_name(card.suit, locale)
        return Localization.get(locale, "card-name", rank=rank_name, suit=suit_name)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_starting_card_name(self, locale: str = "en") -> str:
        """Get the localized name of the required opening card."""
        return self._get_localized_card_name(
            Card(id=-1, rank=RANK_NINE, suit=STARTING_NINE_SUIT), locale
        )

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _localize_message_kwargs(self, kwargs: dict, locale: str) -> dict:
        """Localize Card and suit payloads per recipient before speaking."""
        msg_kwargs = dict(kwargs)
        if "card" in msg_kwargs and isinstance(msg_kwargs["card"], Card):
            msg_kwargs["card"] = self._get_localized_card_name(msg_kwargs["card"], locale)
        if "suit" in msg_kwargs and isinstance(msg_kwargs["suit"], int):
            msg_kwargs["suit"] = self._get_localized_suit_name(msg_kwargs["suit"], locale)
        if "starting_card" in msg_kwargs and isinstance(msg_kwargs["starting_card"], Card):
            msg_kwargs["starting_card"] = self._get_localized_card_name(
                msg_kwargs["starting_card"], locale
            )
        return msg_kwargs

    def _has_localized_message(self, locale: str, message_key: str) -> bool:
        return Localization.get(locale, message_key) != message_key

    def _get_localized_check_sequences_label(self, player: Player, action_id: str) -> str:
        """Get localized label for the 'Check Sequences' action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "nine-action-check-sequences")

    def _sort_player_hand(self, hand: list[Card]) -> list[Card]:
        """Sorts a player's hand according to Nine's rules (rank ascending, then suit)."""
        # Sort by rank using NINE_RANK_ORDER for custom Ace value, then by suit
        return sorted(hand, key=lambda card: (self._get_card_nine_value(card), card.suit))

    def _draw_card(self, player: NinePlayer) -> Card | None:
        """Draw a card for a player."""
        if self.deck.is_empty():
            # In Nine, the game typically ends when deck is empty and players empty hands,
            # so no reshuffling of discard pile is needed.
            return None
        return self.deck.draw_one()

    def _broadcast_nine_message(
        self, message_key: str, sending_player: NinePlayer | None = None, **kwargs
    ) -> None:
        """Broadcasts a localized message to all players, personalizing 'you' vs 'player',
        with fallback for 'you' messages to 'player' messages if 'you' version is not defined."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            target_locale = user.locale
            listener_is_actor = sending_player is not None and p.id == sending_player.id

            final_message_key = f"nine-player-{message_key}"
            if listener_is_actor:
                you_version_key = f"nine-you-{message_key}"
                if self._has_localized_message(target_locale, you_version_key):
                    final_message_key = you_version_key

            if self._wants_brief(user):
                brief_key = f"{final_message_key}-brief"
                if self._has_localized_message(target_locale, brief_key):
                    final_message_key = brief_key

            msg_kwargs = self._localize_message_kwargs(kwargs, target_locale)
            user.speak_l(final_message_key, buffer="game", **msg_kwargs)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        num_players = len(self.get_active_players())
        if num_players in {2, 5}:
            errors.append("nine-error-invalid-player-count")

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        active_players = self.get_active_players()
        if len(active_players) not in SUPPORTED_PLAYER_COUNTS:
            self.broadcast_l("nine-error-invalid-player-count", buffer="game")
            return

        self.status = "playing"
        self.game_active = True
        self.nine_state = NineState()  # Reset game state for new game

        # Initialize turn order
        self.set_turn_players(active_players)

        # Build and shuffle deck
        self.deck = self._build_nine_deck()
        self.deck.shuffle()
        self.discard_pile = []

        # Deal hands and find who has the required opening nine.
        self._deal_initial_hands()
        self.first_turn_player_id = self._find_starting_nine_player()

        if self.first_turn_player_id:
            # Set the current player to the one with the opening nine.
            # Find the player object by ID
            first_player_obj = None
            for p in self.get_active_players():
                if p.id == self.first_turn_player_id:
                    first_player_obj = p
                    break

            if first_player_obj:
                self.current_player = first_player_obj
                self._broadcast_nine_message(
                    "start-player-announcement",
                    player=first_player_obj.name,
                    sending_player=first_player_obj,
                )
        else:
            # This should ideally not happen if deck is built correctly
            self.broadcast_l("nine-error-starting-nine-missing", buffer="game")
            self.finish_game()
            return

        self.play_sound(
            random.choice(
                ["game_cards/shuffle1.ogg", "game_cards/shuffle2.ogg", "game_cards/shuffle3.ogg"]
            )
        )

        self._start_turn()

    def _deal_initial_hands(self) -> None:
        """Deal initial hands to all players based on player count."""
        active_players = self.get_active_players()
        num_players = len(active_players)
        if num_players not in SUPPORTED_PLAYER_COUNTS:
            return

        cards_to_deal_per_player = len(self.deck.cards) // num_players
        self._broadcast_nine_message("nine-deal", cards=cards_to_deal_per_player)

        for player in active_players:
            player.hand = []
            for _ in range(cards_to_deal_per_player):
                card = self._draw_card(player)
                if card:
                    player.hand.append(card)
            # Sort hand after dealing all cards
            player.hand = self._sort_player_hand(player.hand)

        self.play_sound(
            random.choice(
                [
                    "game_cards/draw1.ogg",
                    "game_cards/draw2.ogg",
                    "game_cards/draw3.ogg",
                    "game_cards/draw4.ogg",
                ]
            )
        )

    def _find_starting_nine_player(self) -> Optional[str]:
        """Find the player who has the required opening nine."""
        for player in self.get_active_players():
            for card in player.hand:
                if card.rank == RANK_NINE and card.suit == STARTING_NINE_SUIT:
                    return player.id
        return None

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, NinePlayer):
            return

        # Check for automatic skip
        if not self._has_valid_move(player):
            self._auto_skip_current_player_turn(player)
            return

        self.announce_turn()

        # Jolt bot to think about next play
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self._update_all_turn_actions()
        self.refresh_menus()

    def _auto_skip_current_player_turn(self, player: NinePlayer) -> None:
        """Execute the logic for automatically skipping a player's turn."""
        self._broadcast_nine_message("skips-turn", sending_player=player, player=player.name)
        self._end_turn()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Check for game winner
        winning_player_id = self._check_game_winner()
        if winning_player_id:
            self._end_game(winning_player_id)
            return

        # Advance to next player
        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))
        self.advance_turn(announce=False)
        self._start_turn()

    def _check_game_winner(self) -> Optional[str]:
        """Check if any player has won the game (empty hand)."""
        for player in self.get_active_players():
            if not player.hand:
                return player.id
        return None

    def _end_game(self, winner_id: str) -> None:
        """End the game with a winner."""
        winner_obj = None
        for p in self.get_active_players():
            if p.id == winner_id:
                winner_obj = p
                break

        if winner_obj:
            self._broadcast_nine_message(
                "wins-game", sending_player=winner_obj, player=winner_obj.name
            )
            self._broadcast_nine_message("game-ended")

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Nine-specific data."""
        # Sort players by cards remaining (ascending)
        players_with_cards = [
            (player, len(player.hand))
            for player in self.get_active_players()
        ]
        sorted_players = sorted(players_with_cards, key=lambda entry: entry[1])

        final_scores = {}
        for player, cards_left in sorted_players:
            final_scores[player.name] = cards_left

        winner_name = sorted_players[0][0].name if sorted_players else "N/A"
        winning_count = sorted_players[0][1] if sorted_players else None
        winner_ids = [
            player.id
            for player, cards_left in sorted_players
            if winning_count is not None and cards_left == winning_count
        ]

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(player)
                for player, _cards_left in players_with_cards
            ],
            custom_data={
                "winner_name": winner_name,
                "winner_ids": winner_ids,
                "final_scores": final_scores,
                "rounds_played": 1,  # Nine is usually one round
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Nine game."""
        lines = [Localization.get(locale, "game-final-scores-header")]

        final_scores = result.custom_data.get("final_scores", {})
        winner_name = result.custom_data.get("winner_name")

        if not final_scores:
            return lines

        # Sort players by score (cards left) for a consistent display order
        sorted_players = sorted(final_scores.items(), key=lambda item: item[1])

        for name, cards_left in sorted_players:
            if name == winner_name:
                # Announce the winner by name
                lines.append(Localization.get(locale, "game-winner", player=name))
                lines.append(Localization.get(locale, "nine-final-score", score=cards_left))
            else:
                # Announce other players' scores
                lines.append(
                    Localization.get(locale, "game-eliminated", player=name, score=cards_left)
                )

        return lines

    # ==========================================================================
    # Action Sets and Keybinds
    # ==========================================================================

    def create_turn_action_set(self, player: NinePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")

        # Actions for playing cards dynamically added based on hand
        # This will be updated by _update_card_actions
        return action_set

    def create_standard_action_set(self, player: NinePlayer) -> ActionSet:
        """Create the standard action set for Nine."""
        action_set = super().create_standard_action_set(player)

        # Add a custom status action
        action_set.add(
            Action(
                id="check_sequences_status",
                label="",
                handler="_action_check_sequences_status",
                is_enabled="_is_check_sequences_status_enabled",
                is_hidden="_is_check_sequences_status_hidden",
                get_label="_get_localized_check_sequences_label",  # Use get_label for dynamic localization
                include_spectators=True,
            )
        )

        action_set.add(
            Action(
                id="check_hand_counts_status",
                label="",
                handler="_action_check_hand_counts_status",
                is_enabled="_is_check_hand_counts_status_enabled",
                is_hidden="_is_check_hand_counts_status_hidden",
                get_label="_get_localized_check_hand_counts_label",
                include_spectators=True,
            )
        )

        # Hide generic score actions as they don't apply directly
        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_sequences_status",
                    "check_hand_counts_status",
                    "whose_turn",
                    "whos_at_table",
                ],
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Custom keybind for status (check sequences)
        self.define_keybind(
            "c",
            Localization.get("en", "nine-action-check-sequences"),
            ["check_sequences_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Custom keybind for status (check hand counts)
        self.define_keybind(
            "e",
            Localization.get("en", "nine-action-check-hand-counts"),
            ["check_hand_counts_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _update_card_actions(self, player: NinePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        turn_set.remove_by_prefix(CARD_ACTION_PREFIX)

        # Add actions for cards in hand
        for card in player.hand:
            action_id = f"{CARD_ACTION_PREFIX}{card.id}"
            turn_set.add(
                Action(
                    id=action_id,
                    label="",  # Dynamic label will be set
                    handler="_action_play_card",
                    is_enabled="_is_card_action_enabled",
                    is_hidden=Visibility.VISIBLE,
                    get_label="_get_card_slot_label",
                    show_in_actions_menu=False,
                )
            )

    def _card_for_action_id(self, player: NinePlayer, action_id: str) -> tuple[int, Card] | None:
        """Resolve a stable card action ID to the current hand index and card."""
        if not action_id.startswith(CARD_ACTION_PREFIX):
            return None
        try:
            card_id = int(action_id.removeprefix(CARD_ACTION_PREFIX))
        except ValueError:
            return None
        for slot, card in enumerate(player.hand):
            if card.id == card_id:
                return slot, card
        return None

    def _is_card_action_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        """Return a precise disabled reason for a visible hand-card action."""
        if not isinstance(player, NinePlayer) or action_id is None:
            return "action-disabled"
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "nine-reason-not-your-turn"
        resolved_card = self._card_for_action_id(player, action_id)
        if resolved_card is None:
            return "nine-reason-card-slot-gone"

        _, card = resolved_card
        can_play, reason = self._can_play_card(player, card)
        return None if can_play else reason

    def _get_card_slot_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for a card slot action."""
        if not isinstance(player, NinePlayer):
            return ""
        resolved_card = self._card_for_action_id(player, action_id)
        if resolved_card is None:
            return ""
        _, card = resolved_card
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._get_localized_card_name(card, locale)

    def _update_turn_actions(self, player: NinePlayer) -> None:
        """Update dynamic card actions for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update card actions for all players."""
        for player in self.players:
            self._update_turn_actions(player)

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_check_sequences_status_enabled(self, player: Player) -> str | None:
        """Check if check sequences status action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_sequences_status_hidden(self, player: Player) -> Visibility:
        """Check sequences status is keybind-only except on touch clients."""
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        """Show shared turn status in the touch turn menu."""
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        """Show table presence in the touch turn menu."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_skip_turn_enabled(self, player: Player) -> str | None:
        """Skip turn action is never enabled for direct player interaction."""
        return "action-disabled"

    def _is_skip_turn_hidden(self, player: Player) -> Visibility:
        """Skip turn action is always hidden from the UI."""
        return Visibility.HIDDEN

    def _has_valid_move(self, player: NinePlayer) -> bool:
        """Check if the player has any valid moves."""
        for card in player.hand:
            if self._can_play_card(player, card, check_only=True)[0]:
                return True
        return False

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_check_sequences_status(self, player: Player, action_id: str) -> None:
        """Show game sequences status to player."""
        user = self.get_user(player)
        if not user:
            return

        self.live_status_box(
            player,
            "nine_sequences",
            lambda _player, live_user: self._sequence_status_lines(live_user.locale),
        )

    def _sequence_status_lines(self, locale: str) -> list[str]:
        lines = []

        # Only Sequences on the table
        for suit in SEQUENCE_SUIT_ORDER:
            suit_name = self._get_localized_suit_name(suit, locale)
            sequence_state = self.nine_state.sequences.get(suit)
            if sequence_state and sequence_state.low_card and sequence_state.high_card:
                sequence_str = self._format_sequence_range(sequence_state, locale)
                lines.append(
                    Localization.get(
                        locale, "nine-status-sequence", suit=suit_name, sequence=sequence_str
                    )
                )
            else:
                lines.append(Localization.get(locale, "nine-status-no-sequence", suit=suit_name))

        return lines

    def _format_sequence_range(self, sequence_state: SequenceState, locale: str) -> str:
        """Return a localized summary of the visible range in one suit sequence."""
        low_card = sequence_state.low_card
        high_card = sequence_state.high_card
        if not low_card or not high_card:
            return Localization.get(locale, "nine-none")
        if low_card.id == high_card.id:
            return self._get_localized_rank_name(low_card.rank, locale)

        low_rank = self._get_localized_rank_name(low_card.rank, locale)
        high_rank = self._get_localized_rank_name(high_card.rank, locale)
        return Localization.get(locale, "nine-sequence-range", low=low_rank, high=high_rank)

    def _get_localized_check_hand_counts_label(self, player: Player, action_id: str) -> str:
        """Get localized label for the 'Check Hand Counts' action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "nine-action-check-hand-counts")

    def _is_check_hand_counts_status_enabled(self, player: Player) -> str | None:
        """Check if check hand counts action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hand_counts_status_hidden(self, player: Player) -> Visibility:
        """Check hand counts is keybind-only except on touch clients."""
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _action_check_hand_counts_status(self, player: Player, action_id: str) -> None:
        """Announce the number of cards in each player's hand to the player."""
        user = self.get_user(player)
        if not user:
            return

        for p in self.get_active_players():
            user.speak_l(
                "nine-status-player-hand-count", buffer="game", player=p.name, count=len(p.hand)
            )

    def _action_skip_turn(self, player: Player, action_id: str) -> None:
        """Handle skipping a turn."""
        if not isinstance(player, NinePlayer):
            return

        # All checks should have happened before this point, if this action is still callable,
        # it means a player wants to skip when they legitimately have no moves.
        self._auto_skip_current_player_turn(player)

    def _action_play_card(self, player: Player, action_id: str) -> None:
        """Handle playing a card from hand."""
        if not isinstance(player, NinePlayer):
            return

        if self.current_player != player:
            user = self.get_user(player)
            if user:
                user.speak_l("nine-reason-not-your-turn", buffer="game")
            return

        resolved_card = self._card_for_action_id(player, action_id)
        if resolved_card is None:
            self._speak_action_disabled_reason(player, "nine-reason-card-slot-gone")
            self.refresh_menus(player)
            return

        slot, card_to_play = resolved_card

        can_play, reason = self._can_play_card(player, card_to_play)

        if can_play:
            self._play_card(player, slot, card_to_play)
        else:
            self._speak_action_disabled_reason(player, reason)

    # ==========================================================================
    # Card Play Logic
    # ==========================================================================

    def _can_play_card(
        self, player: NinePlayer, card: Card, check_only: bool = False
    ) -> tuple[bool, str | tuple[str, dict]]:
        """
        Check if a card can be played.
        Returns (bool, reason_message_key_or_tuple)
        """
        locale = self._player_locale(player)
        card_name = self._get_localized_card_name(card, locale)
        suit_name = self._get_localized_suit_name(card.suit, locale)
        starting_card_name = self._get_starting_card_name(locale)

        # Rule 1: first card must be the required opening nine.
        if not self.nine_state.nine_of_clubs_played:
            if not (card.rank == RANK_NINE and card.suit == STARTING_NINE_SUIT):
                if check_only:
                    return False, ""
                return False, (
                    "nine-reason-must-play-starting-nine",
                    {"card": card_name, "starting_card": starting_card_name},
                )
            return True, ""

        # Rule 2: Play any nine to start the sequence of that suit.
        if card.rank == RANK_NINE:
            if card.suit not in self.nine_state.sequences:
                return True, ""  # Can start a new sequence with this nine
            if check_only:
                return False, ""
            if not self._has_valid_move(player):
                return False, "nine-reason-must-skip"
            return False, (
                "nine-reason-nine-already-started",
                {"card": card_name, "suit": suit_name},
            )

        # Rule 3: Extend an already existing sequence.
        # Check if the suit has a sequence
        if card.suit in self.nine_state.sequences:
            sequence = self.nine_state.sequences[card.suit]
            if sequence.low_card and sequence.high_card:
                card_nine_value = self._get_card_nine_value(card)
                low_nine_value = self._get_card_nine_value(sequence.low_card)
                high_nine_value = self._get_card_nine_value(sequence.high_card)

                # Check if card is one lower than current low or one higher than current high

                is_one_lower = card_nine_value == low_nine_value - 1
                is_one_higher = card_nine_value == high_nine_value + 1
                if is_one_lower or is_one_higher:
                    return True, ""

            if check_only:
                return False, ""
            if not self._has_valid_move(player):
                return False, "nine-reason-must-skip"
            return False, (
                "nine-reason-cannot-extend",
                {"card": card_name, "suit": suit_name},
            )

        if not check_only:
            if not self._has_valid_move(player):
                return False, "nine-reason-must-skip"
            return False, (
                "nine-reason-unopened-suit",
                {"card": card_name, "suit": suit_name},
            )
        return False, ""  # For check_only, if not playable, return False with empty reason

    def _play_card(self, player: NinePlayer, slot: int, card: Card) -> None:
        """Execute playing a card."""
        player.hand.pop(slot)
        player.hand = self._sort_player_hand(player.hand)  # Sort hand after card is played

        if not self.nine_state.nine_of_clubs_played:
            # Must be the required opening nine.
            self.nine_state.nine_of_clubs_played = True
            self.nine_state.sequences[card.suit] = SequenceState(low_card=card, high_card=card)
            self._broadcast_nine_message(
                "plays-starting-nine",
                sending_player=player,
                player=player.name,
                card=card,
            )
        elif card.rank == RANK_NINE:
            # Playing a nine to start a new sequence
            self.nine_state.sequences[card.suit] = SequenceState(low_card=card, high_card=card)
            self._broadcast_nine_message(
                "plays-nine-suit",
                sending_player=player,
                player=player.name,
                card=card,  # Pass raw Card object
                suit=card.suit,  # Pass raw suit integer
            )
        else:
            # Extending an existing sequence
            sequence = self.nine_state.sequences[card.suit]
            card_nine_value = self._get_card_nine_value(card)

            if (
                sequence.low_card
                and self._get_card_nine_value(sequence.low_card) == card_nine_value + 1
            ):
                sequence.low_card = card
            elif (
                sequence.high_card
                and self._get_card_nine_value(sequence.high_card) == card_nine_value - 1
            ):
                sequence.high_card = card

            self._broadcast_nine_message(
                "extend-sequence",
                sending_player=player,
                player=player.name,
                card=card,  # Pass raw Card object
                suit=card.suit,  # Pass raw suit integer
            )

        self.discard_pile.append(card)
        self.play_sound(
            random.choice(
                [
                    "game_cards/play1.ogg",
                    "game_cards/play2.ogg",
                    "game_cards/play3.ogg",
                    "game_cards/play4.ogg",
                ]
            )
        )
        self._end_turn()

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def _next_rank(self, rank: int, offset: int) -> int | None:
        try:
            index = NINE_RANKS_IN_ORDER.index(rank)
        except ValueError:
            return None
        next_index = index + offset
        if 0 <= next_index < len(NINE_RANKS_IN_ORDER):
            return NINE_RANKS_IN_ORDER[next_index]
        return None

    def _bot_has_card(self, player: NinePlayer, suit: int, rank: int | None) -> bool:
        if rank is None:
            return False
        return any(card.suit == suit and card.rank == rank for card in player.hand)

    def _playable_card_actions(self, player: NinePlayer) -> list[tuple[str, Card]]:
        return [
            (f"{CARD_ACTION_PREFIX}{card.id}", card)
            for card in player.hand
            if self._can_play_card(player, card, check_only=True)[0]
        ]

    def _bot_card_priority(self, player: NinePlayer, card: Card) -> tuple[int, int]:
        score = 0
        if len(player.hand) == 1:
            score += 1000

        if not self.nine_state.nine_of_clubs_played:
            if card.rank == RANK_NINE and card.suit == STARTING_NINE_SUIT:
                score += 900
            return score, -card.id

        suit_cards = [hand_card for hand_card in player.hand if hand_card.suit == card.suit]

        if card.rank == RANK_NINE:
            score += 80
            if self._bot_has_card(player, card.suit, self._next_rank(RANK_NINE, -1)):
                score += 18
            if self._bot_has_card(player, card.suit, self._next_rank(RANK_NINE, 1)):
                score += 18
            score += len(suit_cards) * 2
            return score, -card.id

        sequence = self.nine_state.sequences.get(card.suit)
        if sequence and sequence.low_card and sequence.high_card:
            card_value = self._get_card_nine_value(card)
            low_value = self._get_card_nine_value(sequence.low_card)
            high_value = self._get_card_nine_value(sequence.high_card)
            if card_value == low_value - 1:
                score += 55
                if self._bot_has_card(player, card.suit, self._next_rank(card.rank, -1)):
                    score += 20
            elif card_value == high_value + 1:
                score += 55
                if self._bot_has_card(player, card.suit, self._next_rank(card.rank, 1)):
                    score += 20

        score += max(0, 10 - len(suit_cards))
        return score, -card.id

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: NinePlayer) -> str | None:
        """Bot AI decision making."""
        if self.current_player != player:
            return None

        playable_actions = self._playable_card_actions(player)
        if playable_actions:
            action_id, _ = max(
                playable_actions,
                key=lambda action_card: self._bot_card_priority(player, action_card[1]),
            )
            return action_id

        # If no valid moves, skip turn
        if not self._has_valid_move(player):
            return "skip_turn"

        return None  # No move decided, wait for next tick or user input
