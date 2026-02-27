from __future__ import annotations

from dataclasses import dataclass, field
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.cards import Card, Deck, DeckFactory, card_name
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.bot import Bot
from ...users.base import User
from datetime import datetime
from .bot import bot_think
from ...game_utils.turn_timer_mixin import TurnTimerMixin

SUIT_SORT_ORDER = {1: 0, 2: 1, 3: 2, 4: 3}

TURN_TIMER_CHOICES = ["5", "10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "5": "crazyeights-timer-5",
    "10": "crazyeights-timer-10",
    "15": "crazyeights-timer-15",
    "20": "crazyeights-timer-20",
    "30": "crazyeights-timer-30",
    "45": "crazyeights-timer-45",
    "60": "crazyeights-timer-60",
    "90": "crazyeights-timer-90",
    "0": "crazyeights-timer-unlimited",
}


@dataclass
class CrazyEightsOptions(GameOptions):
    """Options for Crazy Eights."""

    winning_score: int = option_field(
        IntOption(
            min_val=1,
            max_val=10000,
            default=500,
            value_key="score",
            label="crazyeights-set-winning-score",
            prompt="crazyeights-enter-winning-score",
            change_msg="crazyeights-option-changed-winning-score",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            default="0",
            label="crazyeights-set-turn-timer",
            prompt="crazyeights-select-turn-timer",
            change_msg="crazyeights-option-changed-turn-timer",
            choice_labels=TURN_TIMER_LABELS,
        )
    )


@dataclass
class CrazyEightsPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    score: int = 0


@register_game
@dataclass
class CrazyEightsGame(Game, TurnTimerMixin):
    """Crazy Eights game implementation."""

    players: list[CrazyEightsPlayer] = field(default_factory=list)
    options: CrazyEightsOptions = field(default_factory=CrazyEightsOptions)

    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    current_suit: int | None = None

    awaiting_wild_suit: bool = False
    wild_wait_ticks: int = 0
    dealer_index: int = -1

    turn_has_drawn: bool = False
    turn_drawn_card: Card | None = None

    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    # timer_warning_played removed, handled by Mixin

    intro_wait_ticks: int = 0
    hand_wait_ticks: int = 0
    max_hand_size: int = 12

    def __post_init__(self):
        super().__post_init__()
        # Ensure timer warning flag is initialized (Mixin field)
        self._timer_warning_played = False

    # ==========================================================================
    # Metadata
    # ==========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "Crazy Eights"

    @classmethod
    def get_type(cls) -> str:
        return "crazyeights"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> CrazyEightsPlayer:
        return CrazyEightsPlayer(id=player_id, name=name, is_bot=is_bot)

    def broadcast_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        """Suppress default system sounds that conflict with custom ones."""
        if name in ("join.ogg", "leave.ogg", "join_spectator.ogg", "leave_spectator.ogg"):
            return
        super().broadcast_sound(name, volume, pan, pitch)

    def add_player(self, name: str, user: User) -> CrazyEightsPlayer:
        player = super().add_player(name, user)
        sound = "game_crazyeights/botsit.ogg" if player.is_bot else "game_crazyeights/personsit.ogg"
        self.play_sound(sound)
        return player

    def add_spectator(self, name: str, user: User) -> Player:
        player = super().add_spectator(name, user)
        # Restore spectator join sound since we suppressed the default one
        super().broadcast_sound("join_spectator.ogg")
        return player

    def _action_add_bot(self, player: Player, bot_name: str, action_id: str) -> None:
        if not bot_name.strip():
            from ...game_utils.lobby_actions_mixin import BOT_NAMES

            bot_name = next(
                (
                    n
                    for n in BOT_NAMES
                    if n.lower() not in {x.name.lower() for x in self.players}
                ),
                None,
            )
            if not bot_name:
                user = self.get_user(player)
                if user:
                    user.speak_l("no-bot-names-available", buffer="game")
                return

        bot_user = Bot(bot_name)
        self.add_player(bot_name, bot_user)
        self.broadcast_l("table-joined", player=bot_name)
        self.rebuild_all_menus()

    def _action_remove_bot(self, player: Player, action_id: str) -> None:
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_bot:
                bot = self.players[i]
                # remove_player already broadcasts "table-left"
                self.remove_player(bot.id)
                self.play_sound("game_crazyeights/botleave.ogg")
                break
        self.rebuild_all_menus()

    def _perform_leave_game(self, player: Player) -> None:
        if player.is_spectator:
            # remove_spectator already broadcasts "spectator-left"
            self.remove_spectator(player.id)
            if self._table:
                self._table.remove_member(player.name)
            # Standard spectator leave sound
            super().broadcast_sound("leave_spectator.ogg")
            self.rebuild_all_menus()
            return

        if self.status == "playing" and not player.is_bot:
            # Check if any humans remain (excluding spectators)
            other_humans = any(not p.is_bot and not p.is_spectator and p.id != player.id for p in self.players)
            
            if other_humans:
                self._replace_with_bot(player)
                self.broadcast_l("player-replaced-by-bot", player=player.name)
                self.play_sound("game_crazyeights/personleave.ogg")
                self.rebuild_all_menus()
                return

        # Full removal logic
        # remove_player already broadcasts "table-left"
        self.remove_player(player.id)
        if self.status == "waiting" and self._table:
            self._table.remove_member(player.name)
        
        leave_sound = "game_crazyeights/botleave.ogg" if player.is_bot else "game_crazyeights/personleave.ogg"
        self.play_sound(leave_sound)

        # Correct spectator eviction / destruction logic
        has_humans = any(not p.is_bot and not p.is_spectator for p in self.players)
        if not has_humans:
            self.destroy()
            return

        self.rebuild_all_menus()

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: CrazyEightsPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="draw",
                label=Localization.get(locale, "crazyeights-draw"),
                handler="_action_draw",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "crazyeights-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
                show_in_actions_menu=False,
            )
        )

        # Suit selection actions (keybind only)
        action_set.add(
            Action(
                id="suit_clubs",
                label=Localization.get(locale, "suit-clubs"),
                handler="_action_choose_suit",
                is_enabled="_is_suit_choice_enabled",
                is_hidden="_is_suit_choice_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="suit_diamonds",
                label=Localization.get(locale, "suit-diamonds"),
                handler="_action_choose_suit",
                is_enabled="_is_suit_choice_enabled",
                is_hidden="_is_suit_choice_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="suit_hearts",
                label=Localization.get(locale, "suit-hearts"),
                handler="_action_choose_suit",
                is_enabled="_is_suit_choice_enabled",
                is_hidden="_is_suit_choice_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="suit_spades",
                label=Localization.get(locale, "suit-spades"),
                handler="_action_choose_suit",
                is_enabled="_is_suit_choice_enabled",
                is_hidden="_is_suit_choice_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="read_top",
                label=Localization.get(locale, "crazyeights-read-top"),
                handler="_action_read_top",
                is_enabled="_is_read_top_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_counts",
                label=Localization.get(locale, "crazyeights-read-counts"),
                handler="_action_read_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "crazyeights-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )


        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "read_top",
                "read_counts",
                "check_scores",
                "check_turn_timer",
                "whose_turn",
                "whos_at_table",
            ]
            # Keep existing items that are NOT in the target list
            new_order = [aid for aid in action_set._order if aid not in target_order]
            # Append target items if they exist in the set
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)

            action_set._order = new_order

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Draw", ["draw"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Read top card", ["read_top"], include_spectators=True)
        self.define_keybind("e", "Read counts", ["read_counts"], include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], include_spectators=True)
        # Suit selection overrides (keybind only)
        self.define_keybind("c", "Choose clubs", ["suit_clubs"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Choose diamonds", ["suit_diamonds"], state=KeybindState.ACTIVE)
        self.define_keybind("h", "Choose hearts", ["suit_hearts"], state=KeybindState.ACTIVE)
        self.define_keybind("s", "Choose spades", ["suit_spades"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # Menu syncing
    # ==========================================================================

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_turn_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
        super().rebuild_all_menus()

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, CrazyEightsPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        turn_set.remove_by_prefix("play_card_")
        turn_set.remove("draw")
        turn_set.remove("pass")
        if self.status != "playing" or player.is_spectator:
            return
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return
        nonwild_cards = sorted(
            (card for card in player.hand if card.rank != 8),
            key=lambda c: (SUIT_SORT_ORDER.get(c.suit, 4), -c.rank, c.id),
        )
        wild_cards = [card for card in player.hand if card.rank == 8]
        ordered_cards = nonwild_cards + wild_cards
        for card in ordered_cards:
            turn_set.add(
                Action(
                    id=f"play_card_{card.id}",
                    label="",
                    handler="_action_play_card",
                    is_enabled="_is_play_card_enabled",
                    is_hidden="_is_play_card_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )
        if self.current_player == player:
            turn_set.add(
                Action(
                    id="draw",
                    label=Localization.get(self._player_locale(player), "crazyeights-draw"),
                    handler="_action_draw",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=False,
                )
            )
            turn_set.add(
                Action(
                    id="pass",
                    label=Localization.get(self._player_locale(player), "crazyeights-pass"),
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    show_in_actions_menu=False,
                )
            )

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.round = 0
        self.turn_direction = 1
        self.awaiting_wild_suit = False
        self.wild_wait_ticks = 0

        # Synchronize table status
        self._sync_table_status()

        # Replace main menu music with a silent track for this game.
        self.play_music("game_uno/music.ogg")

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.players])
        self._sync_team_scores()

        self.play_sound("game_crazyeights/intro.ogg")
        self.intro_wait_ticks = 7 * 20

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        if self.wild_wait_ticks > 0:
            self.wild_wait_ticks -= 1
            if self.wild_wait_ticks == 0:
                self._advance_turn()
            return
        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return
        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return
        
        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def _start_new_hand(self) -> None:
        self.round += 1
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.awaiting_wild_suit = False
        self.wild_wait_ticks = 0
        self.turn_has_drawn = False
        self.turn_drawn_card = None

        self.broadcast_l("crazyeights-new-hand", round=self.round)
        self.play_sound("game_crazyeights/newhand.ogg")

        # Deal new deck
        self.deck, _ = DeckFactory.standard_deck(num_decks=2)
        self.discard_pile = []
        self.current_suit = None

        active_players = [p for p in self.players if not p.is_spectator]
        self.set_turn_players(active_players, reset_index=False)
        for p in active_players:
            p.hand = []

        # Deal 7 cards to each
        for _ in range(7):
            for p in active_players:
                card = self.deck.draw_one()
                if card:
                    p.hand.append(card)

        # Rotate dealer/first player each hand
        if self.turn_player_ids:
            self.dealer_index = (self.dealer_index + 1) % len(self.turn_player_ids)
            self.turn_index = (self.dealer_index + 1) % len(self.turn_player_ids)
        else:
            self.dealer_index = -1
            self.turn_index = 0

        # Select starting card (numbered only)
        start_card = self._draw_start_card()
        if start_card:
            self.discard_pile.append(start_card)
            self.current_suit = start_card.suit
            self._broadcast_start_card()
            self.broadcast_l("crazyeights-dealt-cards", cards=7)
        self._start_turn()

    def _draw_start_card(self) -> Card | None:
        while True:
            card = self.deck.draw_one()
            if not card:
                return None
            if self._is_number_card(card):
                return card
            # Put it back and reshuffle
            self.deck.add([card])
            self.deck.shuffle()



    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, CrazyEightsPlayer):
            return
        self.turn_has_drawn = False
        self.turn_drawn_card = None
        # timer_warning_played reset handled by start_turn_timer

        self.announce_turn(turn_sound="game_pig/turn.ogg")

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))

        self.start_turn_timer()
        self._sync_turn_actions(player)
        self.rebuild_all_menus()

    def _advance_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    def _on_turn_timeout(self) -> None:
        """Called by TurnTimerMixin when time runs out."""
        player = self.current_player
        if not isinstance(player, CrazyEightsPlayer):
            return
        self.play_sound("game_crazyeights/expired.ogg")
        action_id = bot_think(self, player)
        if action_id:
            self.execute_action(player, action_id)

    def bot_think(self, player: CrazyEightsPlayer) -> str | None:
        return bot_think(self, player)

    # ==========================================================================
    # Actions
    # ==========================================================================

    def _action_play_card(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if self.awaiting_wild_suit:
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        card = next((c for c in p.hand if c.id == card_id), None)
        if not card:
            return
        if not self._is_card_playable(card):
            return

        p.hand.remove(card)
        self.discard_pile.append(card)
        self.turn_has_drawn = False
        self.turn_drawn_card = None

        self._play_card_sound(card)
        self._broadcast_play(p, card)

        if card.rank == 8:
            if len(p.hand) == 0:
                self._end_round(p, last_card=card)
                return
            self.awaiting_wild_suit = True
            self.start_turn_timer()  # reset timer for suit selection
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(20, 30))
            return

        self.current_suit = card.suit

        if card.rank == 13 and len(p.hand) == 0:
            next_player = self._next_player()
            if next_player:
                self._draw_for_player(next_player, 2)
            self._end_round(p, last_card=card)
            return

        self._apply_card_effects(card)

        if len(p.hand) == 1:
            self.play_sound("game_crazyeights/onecard.ogg")

        if len(p.hand) == 0:
            self._end_round(p, last_card=card)
            return

        self._advance_turn()

    def _action_draw(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if not self._can_draw(p):
            return
        card = self._draw_card()
        if not card:
            self._handle_empty_draw()
            return
        p.hand.append(card)
        self.turn_has_drawn = True
        self.turn_drawn_card = card
        playable = self._is_card_playable(card)
        if playable:
            user = self.get_user(p)
            if user:
                user.play_sound("game_crazyeights/drawPlayable.ogg")
            for other in self.players:
                if other.id == p.id:
                    continue
                other_user = self.get_user(other)
                if other_user:
                    other_user.play_sound("game_crazyeights/draw.ogg")
        else:
            self.play_sound("game_crazyeights/draw.ogg")
        self.start_turn_timer()  # reset timer after drawing
        self._broadcast_draw(p, 1)
        selection_id = f"play_card_{card.id}"
        self.update_player_menu(p, selection_id=selection_id)
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(20, 30))

    def _action_pass(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if not self.turn_has_drawn:
            return
        self.play_sound("game_crazyeights/pass.ogg")
        self._broadcast_pass(p)
        self.turn_has_drawn = False
        self.turn_drawn_card = None
        self._advance_turn()

    def _action_choose_suit(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if not self.awaiting_wild_suit:
            return
        suit = self._suit_from_action(action_id)
        if suit is None:
            return
        self.current_suit = suit
        self.awaiting_wild_suit = False
        self.play_sound("game_crazyeights/morf.ogg")
        self.schedule_sound(self._suit_sound(suit), delay_ticks=15)
        self._broadcast_suit_chosen(suit)
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(20, 30))

        self.timer.clear()
        self.wild_wait_ticks = 15
        return

    def _action_read_top(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak(self.format_top_card(user.locale), buffer="game")

    def _action_read_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        parts = []
        for p in self.turn_players:
            if p.is_spectator:
                continue
            if isinstance(p, CrazyEightsPlayer):
                parts.append(f"{p.name} {len(p.hand)}")
        deck_count = self.deck.size()
        if deck_count > 0:
            parts.append(Localization.get(locale, "crazyeights-deck-count", count=deck_count))
        text = ", ".join(parts) if parts else Localization.get(locale, "crazyeights-no-players")
        user.speak(text, buffer="game")

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("crazyeights-timer-disabled", buffer="game")
        else:
            user.speak_l("crazyeights-timer-remaining", buffer="game", seconds=remaining)

    # ==========================================================================
    # Action state helpers
    # ==========================================================================

    def _require_active_player(self, player: Player) -> CrazyEightsPlayer | None:
        if not isinstance(player, CrazyEightsPlayer):
            return None
        if player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.hand_wait_ticks > 0:
            return "action-wait-for-hand"
        if self.intro_wait_ticks > 0:
            return "action-wait-for-intro"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.wild_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        if self.hand_wait_ticks > 0:
            return "action-wait-for-hand"
        if self.intro_wait_ticks > 0:
            return "action-wait-for-intro"
        return None

    def _is_play_card_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, CrazyEightsPlayer):
            return Visibility.HIDDEN
        if not action_id:
            return Visibility.HIDDEN
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return Visibility.HIDDEN
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        if self._is_turn_action_enabled(player) is not None:
            return self._is_turn_action_enabled(player)
        if not isinstance(player, CrazyEightsPlayer):
            return "action-not-available"
        if self.turn_has_drawn:
            return "action-not-available"
        if self._has_playable_cards(player):
            return "action-not-available"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.awaiting_wild_suit:
            return Visibility.HIDDEN
        if self._is_turn_action_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, CrazyEightsPlayer):
            return Visibility.HIDDEN
        if self.turn_has_drawn:
            return Visibility.HIDDEN
        if self._has_playable_cards(player):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_pass_enabled(self, player: Player) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        if self._is_turn_action_enabled(player) is not None:
            return self._is_turn_action_enabled(player)
        if isinstance(player, CrazyEightsPlayer) and self._has_playable_cards(player):
            return "action-not-available"
        if self.turn_has_drawn:
            return None
        if isinstance(player, CrazyEightsPlayer) and len(player.hand) >= self.max_hand_size:
            return None
        if not self._can_draw(player if isinstance(player, CrazyEightsPlayer) else None):
            return None
        return "action-not-available"

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if self.awaiting_wild_suit:
            return Visibility.HIDDEN
        if self._is_turn_action_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if isinstance(player, CrazyEightsPlayer) and self._has_playable_cards(player):
            return Visibility.HIDDEN
        if self.turn_has_drawn:
            return Visibility.VISIBLE
        if isinstance(player, CrazyEightsPlayer) and len(player.hand) >= self.max_hand_size:
            return Visibility.VISIBLE
        if not self._can_draw(player if isinstance(player, CrazyEightsPlayer) else None):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_suit_choice_enabled(self, player: Player) -> str | None:
        if not self.awaiting_wild_suit:
            return "action-not-available"
        if self._is_turn_action_enabled(player) is not None:
            return self._is_turn_action_enabled(player)
        return None

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        """Override: Web visible when playing."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

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

    def _is_read_top_enabled(self, player: Player) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        return self._is_check_enabled(player)

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        return super()._is_check_scores_enabled(player)

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.awaiting_wild_suit:
            return "action-not-available"
        return super()._is_check_scores_detailed_enabled(player)

    def _is_suit_choice_hidden(self, player: Player) -> Visibility:
        if not self.awaiting_wild_suit:
            return Visibility.HIDDEN
        if self._is_turn_action_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _can_draw(self, player: CrazyEightsPlayer | None) -> bool:
        if not player:
            return False
        if self.awaiting_wild_suit:
            return False
        if self.turn_has_drawn:
            return False
        if len(player.hand) >= self.max_hand_size:
            return False
        if self._has_playable_cards(player):
            return False
        return True

    # ==========================================================================
    # Card helpers
    # ==========================================================================

    def _is_number_card(self, card: Card) -> bool:
        if card.rank in (8,11, 12, 13):
            return False
        return True

    def _is_card_playable(self, card: Card) -> bool:
        if self.awaiting_wild_suit:
            return False
        if card.rank == 8:
            return True
        top = self.top_card
        if not top:
            return True
        if self.current_suit and card.suit == self.current_suit:
            return True
        if top.rank != 8 and card.rank == top.rank:
            return True
        return False

    def _has_playable_cards(self, player: CrazyEightsPlayer) -> bool:
        return any(self._is_card_playable(card) for card in player.hand)

    def get_playable_indices(self, player: CrazyEightsPlayer) -> list[int]:
        return [i for i, card in enumerate(player.hand) if self._is_card_playable(card)]

    @property
    def top_card(self) -> Card | None:
        return self.discard_pile[-1] if self.discard_pile else None

    def _draw_card(self) -> Card | None:
        if self.deck.is_empty():
            self._reshuffle_discard_into_deck()
        return self.deck.draw_one()

    def _handle_empty_draw(self) -> None:
        # No cards available to draw; end the round with no scoring and start a new hand.
        self._start_new_hand()

    def _reshuffle_discard_into_deck(self) -> None:
        if len(self.discard_pile) <= 1:
            return
        top = self.discard_pile[-1]
        rest = self.discard_pile[:-1]
        self.discard_pile = [top]
        self.deck.add(rest)
        self.deck.shuffle()
        self.play_sound("game_crazyeights/pileempty.ogg")



    def _apply_card_effects(self, card: Card) -> None:
        if card.rank == 12:  # Skip
            self.skip_next_players(1)
        elif card.rank == 11:  # Reverse
            if len(self.turn_player_ids) == 2:
                self.skip_next_players(1)
            else:
                self.reverse_turn_direction()
        elif card.rank == 13:  # Draw Two
            next_player = self._next_player()
            if next_player:
                self._draw_for_player(next_player, 2)
            self.skip_next_players(1)

    def _draw_for_player(self, player: CrazyEightsPlayer, count: int) -> None:
        for _ in range(count):
            card = self._draw_card()
            if card:
                player.hand.append(card)
        if count > 0:
            self._broadcast_draw(player, count)

    def _next_player(self) -> CrazyEightsPlayer | None:
        if not self.turn_player_ids:
            return None
        idx = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
        player_id = self.turn_player_ids[idx]
        p = self.get_player_by_id(player_id)
        return p if isinstance(p, CrazyEightsPlayer) else None

    def _suit_from_action(self, action_id: str) -> int | None:
        if action_id == "suit_clubs":
            return 2
        if action_id == "suit_diamonds":
            return 1
        if action_id == "suit_hearts":
            return 3
        if action_id == "suit_spades":
            return 4
        return None

    def suit_action_id(self, suit: int) -> str:
        return {
            1: "suit_diamonds",
            2: "suit_clubs",
            3: "suit_hearts",
            4: "suit_spades",
        }.get(suit, "suit_clubs")

    def _suit_sound(self, suit: int) -> str:
        return {
            1: "game_crazyeights/diamonds.ogg",
            2: "game_crazyeights/clubs.ogg",
            3: "game_crazyeights/hearts.ogg",
            4: "game_crazyeights/spades.ogg",
        }[suit]

    def _suit_name(self, suit: int, locale: str) -> str:
        return Localization.get(locale, {
            1: "suit-diamonds",
            2: "suit-clubs",
            3: "suit-hearts",
            4: "suit-spades",
        }[suit])

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, CrazyEightsPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self.format_card(card, locale)

    def format_card(self, card: Card, locale: str) -> str:
        if card.rank == 8:
            return Localization.get(locale, "crazyeights-wild")
        if card.rank == 11:
            return Localization.get(
                locale, "crazyeights-reverse", suit=self._suit_name(card.suit, locale)
            )
        if card.rank == 12:
            return Localization.get(
                locale, "crazyeights-skip", suit=self._suit_name(card.suit, locale)
            )
        if card.rank == 13:
            return Localization.get(
                locale, "crazyeights-draw-two", suit=self._suit_name(card.suit, locale)
            )
        return card_name(card, locale)

    def format_top_card(self, locale: str) -> str:
        top = self.top_card
        if not top:
            return Localization.get(locale, "crazyeights-no-top")
        if top.rank == 8:
            if self.current_suit:
                return Localization.get(
                    locale,
                    "crazyeights-wild-suit",
                    suit=self._suit_name(self.current_suit, locale),
                )
            return Localization.get(locale, "crazyeights-wild")
        return self.format_card(top, locale)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    # ==========================================================================
    # Scoring / end of hand
    # ==========================================================================

    def _end_round(self, winner: CrazyEightsPlayer, last_card: Card | None) -> None:
        points_from: list[tuple[CrazyEightsPlayer, int]] = []
        total = 0
        for p in self.players:
            if not isinstance(p, CrazyEightsPlayer):
                continue
            if p.is_spectator:
                continue
            if p.id == winner.id:
                continue
            score = self._hand_points(p.hand)
            points_from.append((p, score))
            total += score

        # Update score on the authoritative player instance
        real_winner = self.get_player_by_id(winner.id)
        if isinstance(real_winner, CrazyEightsPlayer):
            real_winner.score += total
        
        self._sync_team_scores()

        self._announce_round_points(winner, points_from, total)
        self._play_round_end_sounds(winner, points_from, total)

        if isinstance(real_winner, CrazyEightsPlayer) and real_winner.score >= self.options.winning_score:
            self._end_game(real_winner)
            return

        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _hand_points(self, hand: list[Card]) -> int:
        total = 0
        for card in hand:
            if card.rank == 8:
                total += 50
            elif card.rank in (11, 12, 13):
                total += 20
            elif card.rank == 1:
                total += 1
            else:
                total += card.rank
        return total

    def _announce_round_points(
        self,
        winner: CrazyEightsPlayer,
        points_from: list[tuple[CrazyEightsPlayer, int]],
        total: int,
    ) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            points_parts = [
                Localization.get(
                    user.locale,
                    "crazyeights-round-points-from",
                    player=opp.name,
                    points=score,
                )
                for opp, score in points_from
            ]
            details = (
                Localization.format_list_and(user.locale, points_parts)
                if points_parts
                else Localization.get(user.locale, "crazyeights-round-details-none")
            )
            user.speak_l(
                "crazyeights-round-summary",
                buffer="game",
                player=winner.name,
                details=details,
                total=total,
            )

    def _broadcast_start_card(self) -> None:
        dealer = (
            self.get_player_by_id(self.turn_player_ids[self.dealer_index])
            if self.turn_player_ids and self.dealer_index >= 0
            else None
        )
        dealer_name = dealer.name if dealer else Localization.get("en", "unknown-player")
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(
                "crazyeights-start-card",
                buffer="game",
                player=dealer_name,
                card=self.format_top_card(user.locale),
            )

    def _broadcast_suit_chosen(self, suit: int) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            suit_name = self._suit_name(suit, user.locale)
            user.speak_l("crazyeights-suit-chosen", buffer="game", suit=suit_name)

    def _broadcast_play(self, player: CrazyEightsPlayer, card: Card) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(
                "crazyeights-player-plays",
                buffer="game",
                player=player.name,
                card=self.format_card(card, user.locale),
            )

    def _broadcast_draw(self, player: CrazyEightsPlayer, count: int) -> None:
        key = "crazyeights-player-draws-one" if count == 1 else "crazyeights-player-draws-many"
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(key, buffer="game", player=player.name, count=count)

    def _broadcast_pass(self, player: CrazyEightsPlayer) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l("crazyeights-player-passes", buffer="game", player=player.name)

    def _play_round_end_sounds(
        self,
        winner: CrazyEightsPlayer,
        points_from: list[tuple[CrazyEightsPlayer, int]],
        total: int,
    ) -> None:
        win_sound = "game_crazyeights/bigwin.ogg" if total >= 100 else "game_crazyeights/youwin.ogg"
        lose_sound = "game_crazyeights/loser.ogg"
        lose_small = "game_crazyeights/youlose.ogg"

        for p in self.players:
            user = self.get_user(p)
            if not user or not isinstance(p, CrazyEightsPlayer):
                continue
            if p.id == winner.id:
                user.play_sound(win_sound)
                continue
            points = self._hand_points(p.hand)
            if points >= 50:
                user.play_sound(lose_sound)
            else:
                user.play_sound(lose_small)

    def _end_game(self, winner: CrazyEightsPlayer) -> None:
        self.play_sound("game_crazyeights/hitmark.ogg")
        self.broadcast_l("crazyeights-game-winner", player=winner.name, score=winner.score)
        # Call finish_game() to show results to everyone
        self.finish_game()

    def build_game_result(self) -> GameResult:
        active = [p for p in self.players if not p.is_spectator]
        winner = max(active, key=lambda p: p.score, default=None)
        final_scores = {p.name: p.score for p in active}
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
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.score if winner else 0,
                "final_scores": final_scores,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
        for i, (name, score) in enumerate(sorted_scores, 1):
            lines.append(
                Localization.get(locale, "crazyeights-line-format", rank=i, player=name, score=score)
            )
        return lines

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team and isinstance(p, CrazyEightsPlayer):
                team.total_score = p.score

    # ==========================================================================
    # Sounds
    # ==========================================================================

    def _play_card_sound(self, card: Card = None) -> None:
        if not card:
            self.play_sound("game_crazyeights/discarded.ogg")
            return

        sound = "game_crazyeights/discarded.ogg"
        if card.rank == 8:
            sound = "game_crazyeights/discwild.ogg"
        elif card.rank == 11:
            sound = "game_crazyeights/discskip.ogg"
        elif card.rank == 12:
            sound = "game_crazyeights/discrev.ogg"
        elif card.rank == 13:
            sound = "game_crazyeights/discdraw.ogg"
        
        self.play_sound(sound)
