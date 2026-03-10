from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.cards import Card, Deck, DeckFactory, card_name, read_cards
from ...game_utils.turn_timer_mixin import TurnTimerMixin
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .evaluator import Combo, evaluate_combo, sort_cards, card_value
from .bot import bot_think

TURN_TIMER_CHOICES = ["10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "10": "pusoydos-timer-10",
    "15": "pusoydos-timer-15",
    "20": "pusoydos-timer-20",
    "30": "pusoydos-timer-30",
    "45": "pusoydos-timer-45",
    "60": "pusoydos-timer-60",
    "90": "pusoydos-timer-90",
    "0": "pusoydos-timer-unlimited",
}

@dataclass
class PusoyDosPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    selected_cards: set[int] = field(default_factory=set)
    score: int = 0
    passed_this_trick: bool = False

@dataclass
class PusoyDosOptions(GameOptions):
    min_entry: int = option_field(
        IntOption(
            default=1000,
            min_val=100,
            max_val=100000,
            value_key="count",
            label="pusoydos-set-min-entry",
            prompt="pusoydos-enter-min-entry",
            change_msg="pusoydos-option-changed-min-entry",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            value_key="choice",
            label="pusoydos-set-turn-timer",
            prompt="pusoydos-select-turn-timer",
            change_msg="pusoydos-option-changed-turn-timer",
        )
    )
    penalty_multiplier: int = option_field(
        IntOption(
            default=10,
            min_val=1,
            max_val=500,
            value_key="count",
            label="pusoydos-set-penalty",
            prompt="pusoydos-enter-penalty",
            change_msg="pusoydos-option-changed-penalty",
        )
    )

@dataclass
@register_game
class PusoyDosGame(Game, TurnTimerMixin):
    players: list[PusoyDosPlayer] = field(default_factory=list)
    options: PusoyDosOptions = field(default_factory=PusoyDosOptions)

    current_combo: Combo | None = None
    trick_winner_id: str | None = None
    trick_cards: list[Card] = field(default_factory=list)

    is_first_turn: bool = True
    hand_wait_ticks: int = 0
    intro_wait_ticks: int = 0
    round: int = 0

    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)

    def __post_init__(self):
        super().__post_init__()
        self._timer_warning_played = False

    @classmethod
    def get_name(cls) -> str:
        return "Pusoy Dos"

    @classmethod
    def get_type(cls) -> str:
        return "pusoydos"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False, display_name: str = "") -> PusoyDosPlayer:
        return PusoyDosPlayer(id=player_id, name=name, is_bot=is_bot, display_name=display_name)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        for p in self.get_active_players():
            p.score = self.options.min_entry

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.get_active_players()])
        self._sync_team_scores()

        self.play_music("game_ninetynine/mus.ogg")
        self.play_sound("game_crazyeights/intro.ogg")
        self.intro_wait_ticks = 7 * 20
        self.broadcast_l("pusoydos-game-start")

    def _start_new_hand(self) -> None:
        self.round += 1
        self.is_first_turn = True
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []

        self.broadcast_l("pusoydos-new-hand", round=self.round)

        deck, _ = DeckFactory.standard_deck()
        deck.shuffle()
        active = self.get_active_players()

        # Clear hands and state
        for p in active:
            p.hand = []
            p.selected_cards.clear()
            p.passed_this_trick = False

        # Deal 13 cards each
        for _ in range(13):
            for p in active:
                card = deck.draw_one()
                if card:
                    p.hand.append(card)

        # Sort hands and find 3 of Clubs
        start_player = None
        for p in active:
            p.hand = sort_cards(p.hand)
            if any(c.rank == 3 and c.suit == 2 for c in p.hand):
                start_player = p

        # If playing with fewer than 4 players, someone might not have 3 of Clubs
        # Just pick the lowest card across all players if 3 of Clubs is missing.
        if not start_player:
            lowest_card_val = 999
            for p in active:
                if p.hand:
                    val = card_value(p.hand[0])
                    if val < lowest_card_val:
                        lowest_card_val = val
                        start_player = p

        self.set_turn_players(active)
        if start_player:
            idx = self.turn_player_ids.index(start_player.id)
            self.turn_index = idx

        self.play_sound("game_crazyeights/newhand.ogg")
        self.schedule_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg", 10, volume=100)
        self.schedule_sound(f"game_cards/draw{random.randint(1, 4)}.ogg", 20, volume=100)
        self.schedule_sound(f"game_cards/draw{random.randint(1, 4)}.ogg", 25, volume=100)

        for p in active:
            user = self.get_user(p)
            if user:
                user.speak_l("pusoydos-dealt", buffer="game", cards=read_cards(p.hand, user.locale))

        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player or not isinstance(player, PusoyDosPlayer):
            return

        # Edge case: everyone else left/disconnected, forcing trick to clear
        active_ids = [p.id for p in self.get_active_players() if isinstance(p, PusoyDosPlayer)]
        if self.trick_winner_id not in active_ids and self.current_combo is not None:
            # Trick winner is gone, trick goes to whoever is currently up.
            self.trick_winner_id = player.id

        if self.trick_winner_id == player.id:
            # Trick is over, I won it. Start a new trick.
            self.current_combo = None
            self.trick_cards = []
            self.trick_winner_id = None
            for p in self.get_active_players():
                if isinstance(p, PusoyDosPlayer):
                    p.passed_this_trick = False
            # No loud broadcast, trick just clears quietly for pacing

        elif player.passed_this_trick:
            # Still in current trick, but I passed. Skip me.
            # To avoid infinite loop if everyone is flagged pass (shouldn't happen), check:
            all_passed = all((p.passed_this_trick for p in self.get_active_players() if isinstance(p, PusoyDosPlayer) and p.id != self.trick_winner_id))
            if all_passed:
                 self.trick_winner_id = player.id
                 self._start_turn()
                 return

            self.advance_turn(announce=False)
            self._start_turn()
            return

        self.announce_turn(turn_sound="game_pig/turn.ogg")

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self.start_turn_timer()
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return

        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return

        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return

        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def bot_think(self, player: PusoyDosPlayer) -> str | None:
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return None

        ids = bot_think(self, player)
        if not ids:
            return "pass"

        # Bot selected cards to play. Update selection.
        player.selected_cards = set(ids)
        return "play_selected"

    def _on_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, PusoyDosPlayer):
            return

        if not self.current_combo:
            # Cannot pass if forced to play. Use bot logic to auto-play.
            ids = bot_think(self, player)
            if ids:
                player.selected_cards = set(ids)
                self._action_play_selected(player, "play_selected")
                return

        self._action_pass(player, "pass")

    # ==========================================================================
    # Action Logic
    # ==========================================================================

    def create_turn_action_set(self, player: PusoyDosPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        for card in player.hand:
            action_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        action_set.add(
            Action(
                id="play_selected",
                label="", # Dynamic label
                handler="_action_play_selected",
                is_enabled="_is_play_selected_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_play_selected_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "pusoydos-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
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
                id="check_trick",
                label=Localization.get(locale, "pusoydos-check-trick"),
                handler="_action_check_trick",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "pusoydos-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "pusoydos-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "pusoydos-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "check_trick",
                "read_hand",
                "read_card_counts",
                "check_scores",
                "check_turn_timer",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Play Selected Cards", ["play_selected"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Check current trick", ["check_trick"], include_spectators=True)
        self.define_keybind("h", "Read your hand", ["read_hand"], include_spectators=False)
        self.define_keybind("e", "Read card counts", ["read_card_counts"], include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], include_spectators=True)

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
        if not isinstance(player, PusoyDosPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        turn_set.remove_by_prefix("toggle_select_")
        turn_set.remove("play_selected")
        turn_set.remove("pass")

        if self.status != "playing" or player.is_spectator:
            return

        # Hide cards ONLY during transitions
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return

        # Cards always visible for the player so they can read hand, but toggling only works on turn
        for card in player.hand:
            turn_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Action buttons are only added if it is the player's turn to keep the menu clean
        if self.current_player == player:
            turn_set.add(
                Action(
                    id="play_selected",
                    label="",
                    handler="_action_play_selected",
                    is_enabled="_is_play_selected_enabled",
                    is_hidden="_is_turn_action_hidden",
                    get_label="_get_play_selected_label",
                    show_in_actions_menu=False,
                )
            )
            turn_set.add(
                Action(
                    id="pass",
                    label=Localization.get(self._player_locale(player), "pusoydos-pass"),
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    show_in_actions_menu=False,
                )
            )

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_toggle_select(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return

        if card_id in p.selected_cards:
            p.selected_cards.remove(card_id)
        else:
            p.selected_cards.add(card_id)

        # If playing in Python CLI, just updating menu doesn't re-read the focus, but
        # that's handled by core engine.
        self.update_player_menu(p)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return

        if not p.selected_cards:
            self._send_error(p, "pusoydos-error-no-cards")
            return

        selected = [c for c in p.hand if c.id in p.selected_cards]
        combo = evaluate_combo(selected)

        if not combo:
            self._send_error(p, "pusoydos-error-invalid-combo")
            return

        # Check first turn rule: must contain 3 of Clubs (if the player has it)
        if self.is_first_turn:
            player_has_three = any(c.rank == 3 and c.suit == 2 for c in p.hand)
            has_three_of_clubs = any(c.rank == 3 and c.suit == 2 for c in selected)
            if player_has_three and not has_three_of_clubs:
                self._send_error(p, "pusoydos-error-first-turn-3c")
                return

        # Check against trick
        if self.current_combo:
            if len(combo.cards) != len(self.current_combo.cards):
                self._send_error(p, "pusoydos-error-wrong-length", count=len(self.current_combo.cards))
                return
            if not combo.beats(self.current_combo):
                self._send_error(p, "pusoydos-error-lower-combo")
                return

        # Play is valid!
        for c in selected:
            p.hand.remove(c)
        p.selected_cards.clear()

        self.current_combo = combo
        self.trick_cards = selected
        self.trick_winner_id = p.id
        self.is_first_turn = False

        # Audio for playing cards based on how many
        if len(selected) > 1:
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")
        else:
            self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")

        if combo.type_name in ["full_house", "four_of_a_kind", "straight_flush"]:
            self.play_sound("game_crazyeights/hitmark.ogg")
        self._broadcast_play(p, combo)

        if len(p.hand) == 1:
            self.play_sound("game_crazyeights/onecard.ogg")

        if len(p.hand) == 0:
            self._end_hand(p)
            return

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_pass(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return

        # Cannot pass if starting a trick
        if not self.current_combo:
            self._send_error(p, "pusoydos-error-must-play")
            return

        p.passed_this_trick = True
        self.play_sound("game_crazyeights/pass.ogg")
        self._broadcast_pass(p)
        p.selected_cards.clear()

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_check_trick(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        if not self.current_combo:
            user.speak_l("pusoydos-trick-empty", buffer="game")
            return

        trick_winner = self.get_player_by_id(self.trick_winner_id)
        trick_winner_name = trick_winner.name if trick_winner else Localization.get(user.locale, "unknown-player")

        combo_name = Localization.get(user.locale, f"pusoydos-combo-{self.current_combo.type_name}")
        cards_str = read_cards(self.trick_cards, user.locale)

        user.speak_l("pusoydos-trick-status", buffer="game", player=trick_winner_name, combo=combo_name, cards=cards_str)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PusoyDosPlayer):
            return
        user = self.get_user(player)
        if user:
            user.speak_l("pusoydos-your-hand", buffer="game", cards=read_cards(player.hand, user.locale))

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        lines = []
        for p in self.get_active_players():
            if isinstance(p, PusoyDosPlayer):
                lines.append(Localization.get(user.locale, "pusoydos-card-count-line", player=p.name, count=len(p.hand)))

        if not lines:
            return

        user.speak("; ".join(lines), buffer="game")

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("pusoydos-timer-disabled", buffer="game")
        else:
            user.speak_l("pusoydos-timer-remaining", buffer="game", seconds=remaining)

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _require_active_player(self, player: Player) -> PusoyDosPlayer | None:
        if not isinstance(player, PusoyDosPlayer):
            return None
        if player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _send_error(self, player: PusoyDosPlayer, msg_key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(msg_key, buffer="game", **kwargs)

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, PusoyDosPlayer):
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
        name = card_name(card, locale)
        if card_id in player.selected_cards:
            return Localization.get(locale, "pusoydos-card-selected", card=name)
        return Localization.get(locale, "pusoydos-card-unselected", card=name)

    def _get_play_selected_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, PusoyDosPlayer):
            return action_id

        user = self.get_user(player)
        locale = user.locale if user else "en"

        if not player.selected_cards:
            return Localization.get(locale, "pusoydos-play-none")

        selected = [c for c in player.hand if c.id in player.selected_cards]
        combo = evaluate_combo(selected)

        if not combo:
            return Localization.get(locale, "pusoydos-play-invalid")

        combo_name = Localization.get(locale, f"pusoydos-combo-{combo.type_name}")
        return Localization.get(locale, "pusoydos-play-combo", combo=combo_name)

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
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_card_toggle_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        # NOTE: Do NOT return an error if it's not their turn!
        # If we return an error (like "action-not-your-turn"), the server filters it out of the UI payload for out-of-turn players, which causes it to disappear.
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.hand_wait_ticks > 0:
            return "action-wait-for-hand"
        if self.intro_wait_ticks > 0:
            return "action-wait-for-intro"
        return None

    def _is_card_toggle_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, PusoyDosPlayer):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        return self._is_turn_action_enabled(player)

    def _is_pass_enabled(self, player: Player) -> str | None:
        # Cannot pass if starting a trick
        if not self.current_combo:
            return "pusoydos-error-must-play"
        return self._is_turn_action_enabled(player)

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if not self.current_combo:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return self._is_check_enabled(player)

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_check_hidden(player)

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

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    # ==========================================================================
    # Broadcasts and Scoring
    # ==========================================================================

    def _broadcast_play(self, player: PusoyDosPlayer, combo: Combo) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            combo_name = Localization.get(user.locale, f"pusoydos-combo-{combo.type_name}")
            cards_str = read_cards(combo.cards, user.locale)

            if combo.type_name == "single":
                user.speak_l("pusoydos-player-plays-single", buffer="game", player=player.name, card=cards_str)
            else:
                user.speak_l("pusoydos-player-plays-combo", buffer="game", player=player.name, combo=combo_name, cards=cards_str)

    def _broadcast_pass(self, player: PusoyDosPlayer) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l("pusoydos-player-passes", buffer="game", player=player.name)

    def _end_hand(self, winner: PusoyDosPlayer) -> None:
        penalty = self.options.penalty_multiplier
        total_won = 0

        loser_penalties = []
        for p in self.get_active_players():
            if isinstance(p, PusoyDosPlayer) and p.id != winner.id:
                cards_left = len(p.hand)
                coins_lost = cards_left * penalty

                # Check 13-card penalty (doubled)
                if cards_left == 13:
                    coins_lost *= 2

                p.score -= coins_lost
                total_won += coins_lost
                loser_penalties.append((p.name, coins_lost))

        winner.score += total_won
        self._sync_team_scores()

        # Audio Polish for win/lose
        if total_won >= (penalty * 15): # big win threshold
            self.play_sound("game_crazyeights/bigwin.ogg")
        else:
            self.play_sound("game_crazyeights/youwin.ogg")

        for p in self.get_active_players():
            if isinstance(p, PusoyDosPlayer) and p.id != winner.id:
                user = self.get_user(p)
                if user:
                    cards_left = len(p.hand)
                    if cards_left == 13:
                        user.play_sound("game_crazyeights/loser.ogg")
                    else:
                        user.play_sound("game_crazyeights/youlose.ogg")

        self.broadcast_l("pusoydos-hand-winner", player=winner.name, amount=total_won)
        for name, lost in loser_penalties:
            self.broadcast_l("pusoydos-hand-loser", player=name, amount=lost)

        # Check if anyone is bankrupt or hit max score limit (if one existed, but it's coin based).
        # For coins, if someone is bankrupt we end game.
        bankrupt = [p.name for p in self.get_active_players() if isinstance(p, PusoyDosPlayer) and p.score <= 0]
        if bankrupt:
            self._end_game(final_winner=winner)
            return

        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _end_game(self, final_winner: PusoyDosPlayer) -> None:
        self.play_sound("game_crazyeights/hitmark.ogg")
        self.broadcast_l("pusoydos-game-over", player=final_winner.name)
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
                Localization.get(locale, "pusoydos-line-format", rank=i, player=name, score=score)
            )
        return lines

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team and isinstance(p, PusoyDosPlayer):
                team.total_score = p.score
