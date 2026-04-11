from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import MenuOption, option_field
from ...game_utils.cards import Card, DeckFactory, card_name, read_cards
from ...game_utils.turn_timer_mixin import TurnTimerMixin
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .bot import bot_think
from .evaluator import (
    NORTHERN_VARIANT,
    SOUTHERN_VARIANT,
    TienLenCombo,
    card_strength,
    evaluate_combo,
    sort_cards,
)
from .rules import get_rules


TURN_TIMER_CHOICES = ["10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "10": "tienlen-timer-10",
    "15": "tienlen-timer-15",
    "20": "tienlen-timer-20",
    "30": "tienlen-timer-30",
    "45": "tienlen-timer-45",
    "60": "tienlen-timer-60",
    "90": "tienlen-timer-90",
    "0": "tienlen-timer-unlimited",
}

VARIANT_CHOICES = [SOUTHERN_VARIANT, NORTHERN_VARIANT]
VARIANT_LABELS = {
    SOUTHERN_VARIANT: "tienlen-variant-south",
    NORTHERN_VARIANT: "tienlen-variant-north",
}

MATCH_CHOICES = ["1", "3", "5"]
MATCH_LABELS = {
    "1": "tienlen-match-1",
    "3": "tienlen-match-3",
    "5": "tienlen-match-5",
}


@dataclass
class TienLenPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    selected_cards: set[int] = field(default_factory=set)
    hand_wins: int = 0
    passed_this_trick: bool = False


@dataclass
class TienLenOptions(GameOptions):
    variant: str = option_field(
        MenuOption(
            choices=VARIANT_CHOICES,
            choice_labels=VARIANT_LABELS,
            default=SOUTHERN_VARIANT,
            value_key="choice",
            label="tienlen-set-variant",
            prompt="tienlen-select-variant",
            change_msg="tienlen-option-changed-variant",
        )
    )
    match_length: str = option_field(
        MenuOption(
            choices=MATCH_CHOICES,
            choice_labels=MATCH_LABELS,
            default="1",
            value_key="choice",
            label="tienlen-set-match-length",
            prompt="tienlen-select-match-length",
            change_msg="tienlen-option-changed-match-length",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            value_key="choice",
            label="tienlen-set-turn-timer",
            prompt="tienlen-select-turn-timer",
            change_msg="tienlen-option-changed-turn-timer",
        )
    )


@dataclass
@register_game
class TienLenGame(Game, TurnTimerMixin):
    players: list[TienLenPlayer] = field(default_factory=list)
    options: TienLenOptions = field(default_factory=TienLenOptions)

    current_combo: TienLenCombo | None = None
    trick_winner_id: str | None = None
    trick_cards: list[Card] = field(default_factory=list)
    hand_winner_id: str | None = None
    is_first_turn: bool = True
    hand_wait_ticks: int = 0
    intro_wait_ticks: int = 0
    round: int = 0

    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._timer_warning_played = False

    @classmethod
    def get_name(cls) -> str:
        return "Tien Len"

    @classmethod
    def get_type(cls) -> str:
        return "tienlen"

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
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> TienLenPlayer:
        return TienLenPlayer(id=player_id, name=name, is_bot=is_bot)

    def _target_hand_wins(self) -> int:
        return int(self.options.match_length)

    @property
    def timer_warning_sound(self) -> str:
        return "game_crazyeights/fivesec.ogg"

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _rules(self):
        return get_rules(self.options.variant)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []
        self.hand_winner_id = None

        for player in self.get_active_players():
            if isinstance(player, TienLenPlayer):
                player.hand_wins = 0
                player.selected_cards.clear()
                player.passed_this_trick = False

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([player.name for player in self.get_active_players()])
        self._sync_team_scores()

        self.play_music("game_crazyeights/mus.ogg")
        self.play_sound("game_crazyeights/intro.ogg")
        self.intro_wait_ticks = 7 * 20
        self.broadcast_l("tienlen-game-start", buffer="game")

    def _start_new_hand(self) -> None:
        self.round += 1
        self.is_first_turn = True
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []

        active = self.get_active_players()
        for player in active:
            if isinstance(player, TienLenPlayer):
                player.hand = []
                player.selected_cards.clear()
                player.passed_this_trick = False

        deck, _ = DeckFactory.standard_deck()
        deck.shuffle()
        for _ in range(13):
            for player in active:
                if isinstance(player, TienLenPlayer):
                    card = deck.draw_one()
                    if card:
                        player.hand.append(card)

        rules = self._rules()
        start_player = None
        for player in active:
            if isinstance(player, TienLenPlayer):
                player.hand = sort_cards(player.hand)
                if any(card.rank == rules.opening_rank and card.suit == rules.opening_suit for card in player.hand):
                    start_player = player
                    break

        if self.hand_winner_id:
            previous_winner = self.get_player_by_id(self.hand_winner_id)
            if previous_winner and previous_winner in active:
                start_player = previous_winner

        if not start_player:
            start_player = min(
                (
                    player
                    for player in active
                    if isinstance(player, TienLenPlayer) and player.hand
                ),
                key=lambda player: card_strength(player.hand[0]),
            )

        self.set_turn_players(active)
        if start_player:
            self.turn_index = self.turn_player_ids.index(start_player.id)

        self.broadcast_l("tienlen-new-hand", buffer="game", round=self.round)
        self.play_sound("game_crazyeights/newhand.ogg")
        self.schedule_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg", 10, volume=100)
        self.schedule_sound(f"game_cards/draw{random.randint(1, 4)}.ogg", 20, volume=100)
        self.schedule_sound(f"game_cards/draw{random.randint(1, 4)}.ogg", 25, volume=100)

        for player in active:
            user = self.get_user(player)
            if user and isinstance(player, TienLenPlayer):
                user.speak_l("tienlen-dealt", buffer="game", cards=read_cards(player.hand, user.locale))

        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player or not isinstance(player, TienLenPlayer):
            return

        active_ids = [active_player.id for active_player in self.get_active_players()]
        if self.trick_winner_id not in active_ids and self.current_combo is not None:
            self.trick_winner_id = player.id

        if self.trick_winner_id == player.id:
            self.current_combo = None
            self.trick_cards = []
            self.trick_winner_id = None
            for active_player in self.get_active_players():
                if isinstance(active_player, TienLenPlayer):
                    active_player.passed_this_trick = False
        elif player.passed_this_trick and not (
            self.options.variant == SOUTHERN_VARIANT
            and self.current_combo is not None
            and self._rules().is_two_combo(self.current_combo)
        ):
            self.advance_turn(announce=False)
            self._start_turn()
            return

        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(18, 30))
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

    def bot_think(self, player: TienLenPlayer) -> str | None:
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return None

        ids = bot_think(self, player)
        if not ids:
            return "pass"
        player.selected_cards = set(ids)
        return "play_selected"

    def _on_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, TienLenPlayer):
            return

        ids = bot_think(self, player)
        if ids:
            player.selected_cards = set(ids)
            self._action_play_selected(player, "play_selected")
            return

        if self.current_combo:
            self._action_pass(player, "pass")

    def create_turn_action_set(self, player: TienLenPlayer) -> ActionSet:
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
                label="",
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
                label="",
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
                get_label="_get_pass_label",
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
                label=Localization.get(locale, "tienlen-check-trick"),
                handler="_action_check_trick",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "tienlen-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "tienlen-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_variant",
                label=Localization.get(locale, "tienlen-check-variant"),
                handler="_action_check_variant",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "tienlen-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            target_order = [
                "check_trick",
                "read_hand",
                "read_card_counts",
                "check_variant",
                "check_scores",
                "check_turn_timer",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [action_id for action_id in action_set._order if action_id not in target_order]
            for action_id in target_order:
                if action_set.get_action(action_id):
                    new_order.append(action_id)
            action_set._order = new_order

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Play Selected Cards", ["play_selected"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Check current trick", ["check_trick"], include_spectators=True)
        self.define_keybind("h", "Read your hand", ["read_hand"], include_spectators=False)
        self.define_keybind("e", "Read card counts", ["read_card_counts"], include_spectators=True)
        self.define_keybind("v", "Check variant", ["check_variant"], include_spectators=True)
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
        if not isinstance(player, TienLenPlayer):
            return
        player.hand = sort_cards(player.hand)
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        turn_set.remove_by_prefix("toggle_select_")
        turn_set.remove("play_selected")
        turn_set.remove("pass")

        if self.status != "playing" or player.is_spectator:
            return
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return

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
                    label="",
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    get_label="_get_pass_label",
                    show_in_actions_menu=False,
                )
            )

    def _require_active_player(self, player: Player) -> TienLenPlayer | None:
        if not isinstance(player, TienLenPlayer):
            return None
        if player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _send_error(self, player: TienLenPlayer, msg_key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(msg_key, buffer="game", **kwargs)

    def _action_toggle_select(self, player: Player, action_id: str) -> None:
        active_player = self._require_active_player(player) or (
            player if isinstance(player, TienLenPlayer) and not player.is_spectator else None
        )
        if not isinstance(active_player, TienLenPlayer):
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        if card_id in active_player.selected_cards:
            active_player.selected_cards.remove(card_id)
        else:
            active_player.selected_cards.add(card_id)
        self.update_player_menu(active_player)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        active_player = self._require_active_player(player)
        if not active_player:
            return

        if not active_player.selected_cards:
            self._send_error(active_player, "tienlen-error-no-cards")
            return

        selected = [card for card in active_player.hand if card.id in active_player.selected_cards]
        rules = self._rules()
        is_valid, error_key, error_kwargs = rules.validate_play(
            active_player.hand,
            selected,
            self.current_combo,
            self.is_first_turn,
            active_player.passed_this_trick,
        )
        if not is_valid:
            self._send_error(active_player, error_key or "tienlen-error-invalid-combo", **error_kwargs)
            return

        combo = rules.evaluate(selected)
        if not combo:
            self._send_error(active_player, "tienlen-error-invalid-combo")
            return

        for card in selected:
            active_player.hand.remove(card)
        active_player.hand = sort_cards(active_player.hand)
        active_player.selected_cards.clear()
        self.current_combo = combo
        self.trick_cards = combo.cards[:]
        self.trick_winner_id = active_player.id
        self.is_first_turn = False

        if len(selected) > 1:
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")
        else:
            self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")
        if rules.is_special_cutter(combo):
            self.play_sound("game_crazyeights/hitmark.ogg")

        self._broadcast_play(active_player, combo)

        if len(active_player.hand) == 1:
            self.play_sound("game_crazyeights/onecard.ogg")

        if not active_player.hand:
            self._end_hand(active_player)
            return

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_pass(self, player: Player, action_id: str) -> None:
        active_player = self._require_active_player(player)
        if not active_player:
            return
        if not self.current_combo:
            self._send_error(active_player, "tienlen-error-must-play")
            return
        active_player.passed_this_trick = True
        active_player.selected_cards.clear()
        self.play_sound("game_crazyeights/pass.ogg")
        self._broadcast_pass(active_player)
        self.advance_turn(announce=False)
        self._start_turn()

    def _action_check_trick(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not self.current_combo:
            user.speak_l("tienlen-trick-empty", buffer="game")
            return
        trick_winner = self.get_player_by_id(self.trick_winner_id)
        winner_name = trick_winner.name if trick_winner else Localization.get(user.locale, "unknown-player")
        combo_name = Localization.get(user.locale, f"tienlen-combo-{self.current_combo.type_name}")
        user.speak_l(
            "tienlen-trick-status",
            buffer="game",
            player=winner_name,
            combo=combo_name,
            cards=read_cards(self.trick_cards, user.locale),
        )

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TienLenPlayer):
            return
        user = self.get_user(player)
        if user:
            player.hand = sort_cards(player.hand)
            user.speak_l("tienlen-your-hand", buffer="game", cards=read_cards(player.hand, user.locale))

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = []
        for active_player in self.get_active_players():
            if isinstance(active_player, TienLenPlayer):
                lines.append(
                    Localization.get(
                        user.locale,
                        "tienlen-card-count-line",
                        player=active_player.name,
                        count=len(active_player.hand),
                    )
                )
        if lines:
            user.speak("; ".join(lines), buffer="game")

    def _action_check_variant(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "tienlen-variant-status",
            buffer="game",
            variant=Localization.get(user.locale, VARIANT_LABELS[self.options.variant]),
        )

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("tienlen-timer-disabled", buffer="game")
        else:
            user.speak_l("tienlen-timer-remaining", buffer="game", seconds=remaining)

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, TienLenPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((card for card in player.hand if card.id == card_id), None)
        if not card:
            return action_id
        locale = self._player_locale(player)
        name = card_name(card, locale)
        if card_id in player.selected_cards:
            return Localization.get(locale, "tienlen-card-selected", card=name)
        return Localization.get(locale, "tienlen-card-unselected", card=name)

    def _get_play_selected_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, TienLenPlayer):
            return action_id
        locale = self._player_locale(player)
        if not player.selected_cards:
            return Localization.get(locale, "tienlen-play-none")
        selected = [card for card in player.hand if card.id in player.selected_cards]
        combo = evaluate_combo(selected, self.options.variant)
        if not combo:
            return Localization.get(locale, "tienlen-play-invalid")
        combo_name = Localization.get(locale, f"tienlen-combo-{combo.type_name}")
        return Localization.get(locale, "tienlen-play-combo", combo=combo_name)

    def _get_pass_label(self, player: Player, action_id: str) -> str:
        return Localization.get(self._player_locale(player), "tienlen-pass")

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
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_card_toggle_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
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
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        return self._is_turn_action_enabled(player)

    def _is_pass_enabled(self, player: Player) -> str | None:
        if not self.current_combo:
            return "tienlen-error-must-play"
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
        if self.is_touch_client(user):
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

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _broadcast_play(self, player: TienLenPlayer, combo: TienLenCombo) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            combo_name = Localization.get(user.locale, f"tienlen-combo-{combo.type_name}")
            cards = read_cards(combo.cards, user.locale)
            if combo.type_name == "single":
                user.speak_l("tienlen-player-plays-single", buffer="game", player=player.name, card=cards)
            else:
                user.speak_l("tienlen-player-plays-combo", buffer="game", player=player.name, combo=combo_name, cards=cards)

    def _broadcast_pass(self, player: TienLenPlayer) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if user:
                user.speak_l("tienlen-player-passes", buffer="game", player=player.name)

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for player in self.players:
            if isinstance(player, TienLenPlayer):
                team = self._team_manager.get_team(player.name)
                if team:
                    team.total_score = player.hand_wins

    def _end_hand(self, winner: TienLenPlayer) -> None:
        winner.hand_wins += 1
        self.hand_winner_id = winner.id
        self._sync_team_scores()

        if winner.hand_wins >= self._target_hand_wins():
            self.play_sound("game_crazyeights/bigwin.ogg")
            self.broadcast_l("tienlen-game-over", buffer="game", player=winner.name)
            self.finish_game()
            return

        self.play_sound("game_crazyeights/youwin.ogg")
        self.broadcast_l(
            "tienlen-hand-winner",
            buffer="game",
            player=winner.name,
            wins=winner.hand_wins,
            target=self._target_hand_wins(),
        )
        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def build_game_result(self) -> GameResult:
        active_players = [player for player in self.players if not player.is_spectator]
        winner = max(
            (player for player in active_players if isinstance(player, TienLenPlayer)),
            key=lambda player: (
                player.hand_wins,
                -len(player.hand),
                -card_strength(player.hand[0]) if player.hand else 0,
            ),
            default=None,
        )
        final_scores = {
            player.name: player.hand_wins
            for player in active_players
            if isinstance(player, TienLenPlayer)
        }
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.hand_wins if winner else 0,
                "final_scores": final_scores,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
        for index, (name, score) in enumerate(sorted_scores, 1):
            lines.append(Localization.get(locale, "tienlen-line-format", rank=index, player=name, score=score))
        return lines
