from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, EditboxInput
from ...game_utils.poker_keybinds import setup_poker_keybinds
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.cards import Card, Deck, DeckFactory, read_cards, sort_cards, card_name
from ...game_utils.poker_betting import PokerBettingRound
from ...game_utils.poker_pot import PokerPotManager
from ...game_utils.poker_table import PokerTableState
from ...game_utils.poker_timer import PokerTurnTimer
from ...game_utils.poker_evaluator import best_hand, describe_hand, describe_partial_hand
from ...game_utils.poker_actions import compute_pot_limit_caps
from ...game_utils import poker_log
from ...game_utils.poker_showdown import order_winners_by_button, format_showdown_lines
from ...game_utils.poker_payout import resolve_pot
from ...game_utils.poker_announcer import announce_pot_winners
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_think
from ...game_utils.turn_timer_mixin import TurnTimerMixin


TURN_TIMER_CHOICES = ["5", "10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "5": "poker-timer-5",
    "10": "poker-timer-10",
    "15": "poker-timer-15",
    "20": "poker-timer-20",
    "30": "poker-timer-30",
    "45": "poker-timer-45",
    "60": "poker-timer-60",
    "90": "poker-timer-90",
    "0": "poker-timer-unlimited",
}

RAISE_MODES = ["no_limit", "pot_limit", "double_pot"]
RAISE_MODE_LABELS = {
    "no_limit": "poker-raise-no-limit",
    "pot_limit": "poker-raise-pot-limit",
    "double_pot": "poker-raise-double-pot",
}

DRAW_LIMITS = ["three_cards", "four_with_ace"]
DRAW_LIMIT_LABELS = {
    "three_cards": "draw-limit-three-cards",
    "four_with_ace": "draw-limit-four-with-ace",
}

BETTING_PHASES = {"bet1", "bet2"}


@dataclass
class FiveCardDrawPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    chips: int = 0
    folded: bool = False
    all_in: bool = False
    to_discard: set[int] = field(default_factory=set)


@dataclass
class FiveCardDrawOptions(GameOptions):
    starting_chips: int = option_field(
        IntOption(
            default=20000,
            min_val=100,
            max_val=1000000,
            value_key="count",
            label="draw-set-starting-chips",
            prompt="draw-enter-starting-chips",
            change_msg="draw-option-changed-starting-chips",
        )
    )
    ante: int = option_field(
        IntOption(
            default=100,
            min_val=0,
            max_val=1000000,
            value_key="count",
            label="draw-set-ante",
            prompt="draw-enter-ante",
            change_msg="draw-option-changed-ante",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            label="draw-set-turn-timer",
            prompt="draw-select-turn-timer",
            change_msg="draw-option-changed-turn-timer",
        )
    )
    raise_mode: str = option_field(
        MenuOption(
            choices=RAISE_MODES,
            choice_labels=RAISE_MODE_LABELS,
            default="no_limit",
            label="draw-set-raise-mode",
            prompt="draw-select-raise-mode",
            change_msg="draw-option-changed-raise-mode",
        )
    )
    max_raises: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=10,
            value_key="count",
            label="draw-set-max-raises",
            prompt="draw-enter-max-raises",
            change_msg="draw-option-changed-max-raises",
        )
    )
    draw_limit: str = option_field(
        MenuOption(
            choices=DRAW_LIMITS,
            choice_labels=DRAW_LIMIT_LABELS,
            default="three_cards",
            label="draw-set-draw-limit",
            prompt="draw-select-draw-limit",
            change_msg="draw-option-changed-draw-limit",
        )
    )


@dataclass
@register_game
class FiveCardDrawGame(Game, TurnTimerMixin):
    players: list[FiveCardDrawPlayer] = field(default_factory=list)
    options: FiveCardDrawOptions = field(default_factory=FiveCardDrawOptions)
    deck: Deck | None = None
    score_unit_key = "game-score-unit-chips"
    discard_pile: list[Card] = field(default_factory=list)
    pot_manager: PokerPotManager = field(default_factory=PokerPotManager)
    betting: PokerBettingRound | None = None
    table_state: PokerTableState = field(default_factory=PokerTableState)
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    hand_number: int = 0
    phase: str = "lobby"
    current_bet_round: int = 0
    action_log: list[tuple[str, dict]] = field(default_factory=list)
    last_showdown_winner_ids: set[str] = field(default_factory=set)
    first_round_opener_id: str | None = None
    _next_hand_wait_ticks: int = 0

    def __post_init__(self):
        super().__post_init__()
        # Ensure timer warning flag is initialized (Mixin field)
        self._timer_warning_played = False

    @classmethod
    def get_name(cls) -> str:
        return "Five Card Draw"

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    @classmethod
    def get_type(cls) -> str:
        return "fivecarddraw"

    @classmethod
    def get_category(cls) -> str:
        return "poker"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> FiveCardDrawPlayer:
        return FiveCardDrawPlayer(id=player_id, name=name, is_bot=is_bot, chips=0)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        if self.options.ante >= self.options.starting_chips:
            errors.append(
                (
                    "draw-error-ante-too-high",
                    {
                        "ante": self.options.ante,
                        "chips": self.options.starting_chips,
                    },
                )
            )
        if self.options.ante == 0 and self.options.raise_mode != "no_limit":
            errors.append(("draw-error-capped-mode-needs-ante", {"mode": self.options.raise_mode}))
        return errors

    # ==========================================================================
    # Action availability
    # ==========================================================================
    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_fold_enabled(self, player: Player) -> str | None:
        if self.phase == "draw":
            return "draw-fold-not-available"
        if self.phase not in BETTING_PHASES or self._next_hand_wait_ticks > 0:
            return "poker-no-active-betting"
        return self._is_turn_action_enabled(player)

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self._next_hand_wait_ticks > 0 or self.phase == "showdown":
            return Visibility.HIDDEN
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p or p.folded:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    # ==========================================================================
    # Action sets / keybinds
    # ==========================================================================
    def create_turn_action_set(self, player: FiveCardDrawPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="call",
                label=Localization.get(locale, "poker-call"),
                handler="_action_call",
                is_enabled="_is_bet_action_enabled",
                is_hidden="_is_bet_action_hidden",
                get_label="_get_call_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="fold",
                label=Localization.get(locale, "poker-fold"),
                handler="_action_fold",
                is_enabled="_is_fold_enabled",
                is_hidden="_is_bet_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="raise",
                label=Localization.get(locale, "poker-raise"),
                handler="_action_raise",
                is_enabled="_is_raise_enabled",
                is_hidden="_is_bet_action_hidden",
                input_request=EditboxInput(
                    prompt="poker-enter-raise",
                    default="",
                    bot_input="_bot_input_raise",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="all_in",
                label=Localization.get(locale, "poker-all-in"),
                handler="_action_all_in",
                is_enabled="_is_all_in_enabled",
                is_hidden="_is_bet_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="draw_cards",
                label=Localization.get(locale, "draw-draw-cards"),
                handler="_action_draw_cards",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                get_label="_get_draw_label",
                show_in_actions_menu=False,
            )
        )
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"card_key_{i}",
                    label=Localization.get(locale, "draw-card-key", index=i),
                    handler="_action_card_key",
                    is_enabled="_is_discard_toggle_enabled",
                    is_hidden="_is_always_hidden",
                    get_label="_get_card_key_label",
                    show_in_actions_menu=False,
                )
            )
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"toggle_discard_{i}",
                    label=Localization.get(locale, "draw-toggle-discard", index=i),
                    handler="_action_toggle_discard",
                    is_enabled="_is_discard_toggle_enabled",
                    is_hidden="_is_discard_toggle_hidden",
                    get_label="_get_toggle_discard_label",
                    show_in_actions_menu=False,
                )
            )

        if self.is_touch_client(user):
            draw_actions = [f"toggle_discard_{i}" for i in range(1, 6)] + ["draw_cards"]
            bet_actions = ["call", "fold", "raise", "all_in"]
            pinned = set(draw_actions) | set(bet_actions)
            rest = [aid for aid in action_set._order if aid not in pinned]
            action_set._order = (
                [aid for aid in draw_actions if aid in action_set._order]
                + [aid for aid in bet_actions if aid in action_set._order]
                + rest
            )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Add Game-Specific Standard Actions
        action_set.add(
            Action(
                id="check_pot",
                label=Localization.get(locale, "poker-check-pot"),
                handler="_action_check_pot",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_bet",
                label=Localization.get(locale, "poker-check-bet"),
                handler="_action_check_bet",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_min_raise",
                label=Localization.get(locale, "poker-check-min-raise"),
                handler="_action_check_min_raise",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_hand_players",
                label=Localization.get(locale, "poker-check-hand-players"),
                handler="_action_check_hand_players",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "poker-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="speak_hand",
                label=Localization.get(locale, "poker-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="speak_hand_value",
                label=Localization.get(locale, "poker-hand-value"),
                handler="_action_read_hand_value",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_dealer",
                label=Localization.get(locale, "poker-check-dealer"),
                handler="_action_check_dealer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_position",
                label=Localization.get(locale, "poker-check-position"),
                handler="_action_check_position",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=False,
            )
        )
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"speak_card_{i}",
                    label=Localization.get(locale, "poker-read-card", index=i),
                    handler="_action_read_card",
                    is_enabled="_is_check_enabled",
                    is_hidden="_is_always_hidden",
                    show_in_actions_menu=False,
                )
            )

        if self.is_touch_client(user):
            target_order = [
                "speak_hand",
                "speak_hand_value",
                "check_pot",
                "check_bet",
                "check_min_raise",
                "check_hand_players",
                "check_dealer",
                "check_position",
                "check_turn_timer",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)

        return action_set

    # Touch-client visibility overrides

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

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        setup_poker_keybinds(
            self,
            check_dealer="check_dealer",
            dealer_label="Dealer",
            check_position="check_position",
            check_bet="check_bet",
            check_min_raise="check_min_raise",
            check_hand_players="check_hand_players",
            check_turn_timer="check_turn_timer",
            draw_cards="draw_cards",
        )
        for i in range(1, 6):
            self.define_keybind(
                str(i),
                Localization.get("en", "draw-card-key", index=i), # Keybind doc strings often stick to EN, or we can assume locale lookup happened elsewhere if this was dynamic. But setup_keybinds usually runs once. Using default EN for the friendly name is standard for now unless we refactor base keybind system.
                [f"card_key_{i}"],
                state=KeybindState.ACTIVE,
            )

    # ==========================================================================
    # Game flow
    # ==========================================================================
    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        for player in self.get_active_players():
            player.chips = self.options.starting_chips
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.get_active_players()])
        self._sync_team_scores()
        self.set_turn_players(self.get_active_players())
        self.play_music("game_3cardpoker/mus.ogg")
        self._start_new_hand()

    def _start_new_hand(self) -> None:
        self.hand_number += 1
        self.phase = "deal"
        self.action_log = []
        self.current_bet_round = 0
        self.first_round_opener_id = None
        self.pot_manager.reset()
        self.discard_pile = []
        self.deck, _ = DeckFactory.standard_deck()
        self.deck.shuffle()

        table_players = [
            p for p in self.get_active_players() if isinstance(p, FiveCardDrawPlayer)
        ]
        active = [p for p in table_players if p.chips > 0]
        active_ids = {p.id for p in active}
        for p in table_players:
            p.hand = []
            p.folded = p.id not in active_ids
            p.all_in = False
            p.to_discard = set()
        if len(active) <= 1:
            self._end_game(active[0] if active else None)
            return

        self.table_state.advance_button([p.id for p in active])

        self.play_sound("game_cards/small_shuffle.ogg")
        self._post_ante(active)
        self._deal_cards(active, 5)
        for p in active:
            user = self.get_user(p)
            if user:
                user.speak_l("draw-dealt-cards", buffer="game", cards=read_cards(p.hand, user.locale))
        self._start_betting_round()

    def _post_ante(self, active: list[FiveCardDrawPlayer]) -> None:
        ante = self.options.ante
        if ante <= 0:
            return
        self.play_sound("game_3cardpoker/bet.ogg")
        for p in active:
            pay = min(p.chips, ante)
            p.chips -= pay
            if p.chips == 0:
                p.all_in = True
            self.pot_manager.add_contribution(p.id, pay)
        self._sync_team_scores()
        self.broadcast_l(
            "draw-antes-posted",
            buffer="game",
            amount=self.pot_manager.total_pot(),
        )

    def _deal_cards(self, players: list[FiveCardDrawPlayer], count: int) -> None:
        if not players:
            return
        start_index = (self.table_state.button_index + 1) % len(players)
        order = players[start_index:] + players[:start_index]
        delay_ticks = 4
        for _ in range(count):
            for p in order:
                card = self.deck.draw_one() if self.deck else None
                if card:
                    p.hand.append(card)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks, volume=100)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks + 1, volume=100)
            delay_ticks += 6
        for p in players:
            p.hand = sort_cards(p.hand)

    def _start_betting_round(self) -> None:
        self.current_bet_round += 1
        self.phase = f"bet{self.current_bet_round}"
        active_ids = [p.id for p in self.get_active_players() if p.chips > 0 and not p.folded]
        order = [p.id for p in self.get_active_players() if p.id in active_ids]
        self.betting = PokerBettingRound(
            order=order, max_raises=self.options.max_raises or None
        )
        self.betting.reset()
        if not order:
            self._showdown()
            return
        if self.current_bet_round == 2 and self.first_round_opener_id:
            start_index = self._turn_index_from_player(self.first_round_opener_id, order)
        else:
            start_index = self._turn_index_after_dealer(order)
        self._announce_betting_round()
        self._set_turn_by_index(start_index, order)

    def _announce_betting_round(self) -> None:
        if self.current_bet_round == 1:
            self.broadcast_l("draw-betting-round-1", buffer="game")
        else:
            self.broadcast_l("draw-betting-round-2", buffer="game")

    def _set_turn_by_index(self, start_index: int, order: list[str]) -> None:
        if not order:
            return
        idx = start_index % len(order)
        self.turn_player_ids = order
        self.turn_index = idx
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p or p.folded or (p.all_in and self.phase != "draw"):
            self._advance_turn()
            return
        if self.phase == "draw" and p.is_bot and p.all_in:
            self.bot_think(p)
            self._action_draw_cards(p, "draw_cards")
            return
        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(30, 50))
        self.start_turn_timer()
        self.refresh_menus()

    def _advance_turn(self) -> None:
        if not self.betting:
            return
        active_ids = self._active_betting_ids()
        next_id = self.betting.next_player(self.current_player.id if self.current_player else None, active_ids)
        if next_id is None:
            return
        self.turn_index = self.turn_player_ids.index(next_id)
        self._start_turn()

    # _start_turn_timer removed, handled by Mixin

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        if self._next_hand_wait_ticks > 0:
            self._next_hand_wait_ticks -= 1
            if self._next_hand_wait_ticks == 0:
                self._start_new_hand()
            return
        
        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def bot_think(self, player: FiveCardDrawPlayer) -> str | None:
        return bot_think(self, player)

    # ==========================================================================
    # Action handlers
    # ==========================================================================
    def _action_fold(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        p.folded = True
        self.pot_manager.mark_folded(p.id)
        poker_log.log_fold(self.action_log, p.name)
        self.broadcast_personal_l(p, "poker-you-fold", "poker-player-folds", buffer="game")
        self._after_action()

    def _action_call(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        to_call = self.betting.amount_to_call(p.id)
        pay = min(p.chips, to_call)
        p.chips -= pay
        if p.chips == 0:
            p.all_in = True
        self.pot_manager.add_contribution(p.id, pay)
        self.betting.record_bet(p.id, pay, is_raise=False)
        if to_call == 0:
            poker_log.log_check(self.action_log, p.name)
            self.broadcast_personal_l(p, "poker-you-check", "poker-player-checks", buffer="game")
        else:
            self.play_sound("game_3cardpoker/bet.ogg")
            poker_log.log_call(self.action_log, p.name, pay)
            self.broadcast_personal_l(p, "poker-you-call", "poker-player-calls", buffer="game", amount=pay)
        if p.all_in and pay > 0:
            self.broadcast_personal_l(p, "poker-you-all-in", "poker-player-all-in", buffer="game", amount=pay)
        self._sync_team_scores()
        self._after_action()

    def _action_raise(self, player: Player, amount_str: str, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        user = self.get_user(p)
        try:
            amount = int(amount_str)
        except ValueError:
            if user:
                user.speak_l("draw-raise-invalid", buffer="game")
            return
        if amount <= 0:
            if user:
                user.speak_l("draw-raise-invalid", buffer="game")
            return
        if not self.betting.can_raise():
            if user:
                user.speak_l(
                    "draw-raise-cap-reached",
                    buffer="game",
                    count=self.options.max_raises,
                )
            return
        min_raise = max(self.betting.last_raise_size, 1)
        if amount > p.chips:
            if user:
                user.speak_l(
                    "draw-raise-over-stack",
                    buffer="game",
                    requested=amount,
                    chips=p.chips,
                )
            return
        if amount == p.chips:
            self._action_all_in(p, "all_in")
            return
        if amount < min_raise:
            if user:
                user.speak_l(
                    "draw-raise-too-small",
                    buffer="game",
                    requested=amount,
                    minimum=min_raise,
                )
            return
        to_call = self.betting.amount_to_call(p.id)
        total = to_call + amount
        maximum = self._maximum_additional_bet(p)
        if total > maximum and total <= p.chips:
            if user:
                user.speak_l(
                    "draw-raise-over-limit",
                    buffer="game",
                    mode=self.options.raise_mode,
                    requested=amount,
                    maximum=max(0, maximum - to_call),
                )
            return
        if total > p.chips:
            total = p.chips
        if total < to_call + min_raise:
            # Treat short stack as all-in (does not reopen betting)
            self._action_all_in(p, "all_in")
            return
        was_unopened = self.current_bet_round == 1 and self.betting.current_bet == 0
        p.chips -= total
        if p.chips == 0:
            p.all_in = True
        self.play_sound("game_3cardpoker/bet.ogg")
        self.pot_manager.add_contribution(p.id, total)
        self.betting.record_bet(p.id, total, is_raise=True)
        new_bet_total = self.betting.bets[p.id]
        if was_unopened:
            self.first_round_opener_id = p.id
        poker_log.log_raise(self.action_log, p.name, new_bet_total)
        self.broadcast_personal_l(
            p,
            "poker-you-raise",
            "poker-player-raises",
            buffer="game",
            amount=new_bet_total,
        )
        if p.all_in:
            self.broadcast_personal_l(p, "poker-you-all-in", "poker-player-all-in", buffer="game", amount=total)
        self._sync_team_scores()
        self._after_action()

    def _bot_input_raise(self, player: Player) -> str:
        if isinstance(player, FiveCardDrawPlayer):
            if not self.betting:
                return "1"
            to_call = self.betting.amount_to_call(player.id)
            min_raise = max(self.betting.last_raise_size, 1)
            max_raise = max(0, self._maximum_additional_bet(player) - to_call)
            if max_raise < min_raise:
                return str(min_raise)
            desired = max(min_raise, self.pot_manager.total_pot() // 2)
            amount = min(desired, max_raise)
            return str(amount)
        return "1"

    def _action_all_in(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        amount = p.chips
        if amount <= 0:
            return
        to_call = self.betting.amount_to_call(p.id)
        min_raise = max(self.betting.last_raise_size, 1)
        pay = amount
        raise_amount = pay - to_call
        is_raise = raise_amount >= min_raise and pay > to_call
        user = self.get_user(p)
        if is_raise and not self.betting.can_raise():
            if user:
                user.speak_l(
                    "draw-all-in-raise-cap-reached",
                    buffer="game",
                    count=self.options.max_raises,
                )
            return
        maximum = self._maximum_additional_bet(p)
        if pay > maximum:
            if user:
                user.speak_l(
                    "draw-all-in-over-limit",
                    buffer="game",
                    mode=self.options.raise_mode,
                    stack=pay,
                    maximum=max(0, maximum - to_call),
                )
            return
        was_unopened = self.current_bet_round == 1 and self.betting.current_bet == 0
        p.chips -= pay
        p.all_in = True
        self.play_sound("game_3cardpoker/bet.ogg")
        self.pot_manager.add_contribution(p.id, pay)
        self.betting.record_bet(p.id, pay, is_raise=is_raise)
        if was_unopened and is_raise:
            self.first_round_opener_id = p.id
        poker_log.log_all_in(self.action_log, p.name, pay)
        self.broadcast_personal_l(p, "poker-you-all-in", "poker-player-all-in", buffer="game", amount=pay)
        self._sync_team_scores()
        self._after_action()

    def _action_draw_cards(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if self.phase != "draw":
            user = self.get_user(player)
            if user:
                user.speak_l("draw-not-draw-phase", buffer="game")
            return
        p.to_discard = {idx for idx in p.to_discard if 0 <= idx < len(p.hand)}
        selection_error = self._discard_selection_error(p, p.to_discard)
        if selection_error:
            user = self.get_user(p)
            if user:
                key, kwargs = selection_error
                user.speak_l(key, buffer="game", **kwargs)
            return
        if not p.to_discard:
            self.broadcast_personal_l(p, "draw-you-stand-pat", "draw-player-stands-pat", buffer="game")
            self._advance_after_draw(p, direct_action=action_id == "draw_cards")
            return
        indices = sorted(p.to_discard)
        drawn_cards: list[Card] = []
        for idx in reversed(indices):
            if 0 <= idx < len(p.hand):
                self.discard_pile.append(p.hand.pop(idx))
        for _ in range(len(indices)):
            card = self.deck.draw_one() if self.deck else None
            if card:
                drawn_cards.append(card)
                p.hand.append(card)
        p.hand = sort_cards(p.hand)
        self._play_draw_sounds(len(indices))
        user = self.get_user(p)
        self.broadcast_personal_l(
            p,
            "draw-you-draw",
            "draw-player-draws",
            buffer="game",
            count=len(indices),
        )
        if user and drawn_cards:
            user.speak_l(
                "draw-you-drew-cards",
                buffer="game",
                count=len(drawn_cards),
                cards=read_cards(drawn_cards, user.locale),
            )
            user.speak_l("poker-your-hand", buffer="game", cards=read_cards(p.hand, user.locale))
        p.to_discard = set()
        self._advance_after_draw(p, direct_action=action_id == "draw_cards")

    def _action_toggle_discard(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or self.phase != "draw":
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        self._set_discard(p, idx, discard=idx not in p.to_discard)
        self.refresh_menus(p)

    # ==========================================================================
    # Action helpers
    # ==========================================================================
    def _after_action(self) -> None:
        if not self.betting:
            return
        active_ids = self._active_betting_ids()
        if len(active_ids) <= 1:
            self._award_uncontested(active_ids)
            return
        if active_ids and active_ids.issubset(self._all_in_ids()):
            if self.current_bet_round == 1:
                self.phase = "draw"
                self._start_draw_phase()
            else:
                self._showdown()
            return
        if self.betting.is_complete(active_ids, self._all_in_ids()):
            if self.current_bet_round == 1:
                self.phase = "draw"
                self._start_draw_phase()
            else:
                self._showdown()
            return
        self._advance_turn()

    def _start_draw_phase(self) -> None:
        self.broadcast_l("draw-begin-draw", buffer="game")
        order = [p.id for p in self.get_active_players() if not p.folded]
        start_index = self._turn_index_after_dealer(order)
        self.turn_player_ids = order[start_index:] + order[:start_index]
        self.turn_index = 0
        self._start_turn()

    def _advance_after_draw(self, player: FiveCardDrawPlayer, *, direct_action: bool = True) -> None:
        if self.current_player != player:
            return
        self.advance_turn(announce=False)
        if self.current_player is None or (
            self.current_player and self.current_player.id == self.turn_player_ids[0]
        ):
            self._start_betting_round()
        else:
            self._start_turn()
        if direct_action:
            self.request_menu_focus(player, "call")

    def _showdown(self) -> None:
        self.phase = "showdown"
        self.broadcast_l("poker-showdown", buffer="game")
        self._resolve_pots()
        self._announce_showdown_hands(skip_best=True)
        self._queue_new_hand()

    def _award_uncontested(self, active_ids: set[str]) -> None:
        winner = self.get_player_by_id(next(iter(active_ids))) if active_ids else None
        if not winner:
            return
        amount = self.pot_manager.total_pot()
        if isinstance(winner, FiveCardDrawPlayer):
            winner.chips += amount
        winner_contribution = self.pot_manager.contributions.get(winner.id, 0)
        amount_from_others = amount - winner_contribution
        self.play_sound(random.choice(["game_blackjack/win1.ogg", "game_blackjack/win2.ogg", "game_blackjack/win3.ogg"]))
        if amount_from_others > 0:
            self.broadcast_personal_l(
                winner,
                "poker-you-win-pot",
                "poker-player-wins-pot",
                buffer="game",
                amount=amount_from_others,
            )
        else:
            self.broadcast_personal_l(
                winner,
                "poker-your-uncalled-bet-returned",
                "poker-uncalled-bet-returned",
                buffer="game",
                amount=winner_contribution,
            )
        self._sync_team_scores()
        self._queue_new_hand()

    def _resolve_pots(self) -> None:
        self.last_showdown_winner_ids.clear()
        pots = self.pot_manager.get_pots()
        for pot_index, pot in enumerate(pots):
            eligible_players = [self.get_player_by_id(pid) for pid in pot.eligible_player_ids]
            eligible_players = [p for p in eligible_players if isinstance(p, FiveCardDrawPlayer)]
            if not eligible_players:
                continue
            active_ids = [p.id for p in self.get_active_players()]
            winners, best_score, share, remainder = resolve_pot(
                pot.amount,
                eligible_players,
                active_ids,
                self.table_state.get_button_id(active_ids),
                lambda p: p.id,
                lambda p: best_hand(p.hand)[0],
            )
            if not winners or not best_score:
                continue
            self.last_showdown_winner_ids.update(w.id for w in winners)
            for w in winners:
                w.chips += share
            if remainder > 0:
                winners[0].chips += remainder
            
            # Announce winners using shared logic
            announce_pot_winners(self, pot_index, pot.amount, winners, best_score)
        self._sync_team_scores()

    def _announce_showdown_hands(self, skip_best: bool = False) -> None:
        active = [p for p in self.get_active_players() if isinstance(p, FiveCardDrawPlayer) and not p.folded]
        if len(active) <= 1:
            return
        skip_ids: set[str] = set()
        if skip_best and self.last_showdown_winner_ids:
            skip_ids = set(self.last_showdown_winner_ids)
        active_ids = [p.id for p in active]
        lines_data = format_showdown_lines(
            active,
            active_ids,
            self.table_state.get_button_id(active_ids),
            lambda p: p.id,
            lambda p: (lambda s: ((p, s), s))(best_hand(p.hand)[0]),
        )
        
        # Iterate over formatted lines (which give us the player and score)
        # Note: format_showdown_lines returns list of (player_id, content, score)
        # We abused the content lambda to pass the player object back so we can localize in the loop.
        
        for player_id, (player_obj, hand_score), _score in lines_data:
            if skip_ids and player_id in skip_ids:
                continue
            
            # Broadcast personalized message
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                    
                cards_str = read_cards(player_obj.hand, user.locale)
                hand_desc = describe_hand(hand_score, user.locale)
                
                user.speak_l(
                    "poker-you-show-hand" if p.id == player_obj.id else "poker-show-hand",
                    buffer="game",
                    player=player_obj.name,
                    cards=cards_str,
                    hand=hand_desc
                )

    def _queue_new_hand(self) -> None:
        self._next_hand_wait_ticks = 100
        self.refresh_menus()

    def _order_winners_by_button(self, winners: list[FiveCardDrawPlayer]) -> list[FiveCardDrawPlayer]:
        if len(winners) <= 1:
            return winners
        active_ids = [p.id for p in self.get_active_players()]
        return order_winners_by_button(winners, active_ids, self.table_state.get_button_id(active_ids), lambda p: p.id)

    # ==========================================================================
    # Utility / status actions
    # ==========================================================================
    def _action_check_pot(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        pots = self.pot_manager.get_pots()
        if not pots:
            user.speak_l("poker-pot-total", buffer="game", amount=0)
            return
        user.speak_l("poker-pot-total", buffer="game", amount=self.pot_manager.total_pot())
        if not self._all_in_ids():
            return
        user.speak_l("poker-pot-main", buffer="game", amount=pots[0].amount)
        for idx, pot in enumerate(pots[1:], start=1):
            user.speak_l("poker-pot-side", buffer="game", index=idx, amount=pot.amount)

    def _action_check_bet(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not self.betting or self.phase not in BETTING_PHASES:
            if user:
                user.speak_l("poker-no-active-betting", buffer="game")
            return
        if user:
            if (
                player.is_spectator
                or not isinstance(player, FiveCardDrawPlayer)
                or player.folded
                or player.all_in
                or player.id not in self.betting.bets
            ):
                user.speak_l(
                    "draw-current-bet",
                    buffer="game",
                    amount=self.betting.current_bet,
                )
            else:
                user.speak_l(
                    "poker-to-call",
                    buffer="game",
                    amount=self.betting.amount_to_call(player.id),
                )

    def _action_check_min_raise(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not self.betting or self.phase not in BETTING_PHASES:
            if user:
                user.speak_l("poker-no-active-betting", buffer="game")
            return
        if not self.betting.can_raise():
            if user:
                user.speak_l(
                    "draw-raise-cap-reached",
                    buffer="game",
                    count=self.options.max_raises,
                )
            return
        min_raise = max(self.betting.last_raise_size, 1)
        if user:
            if (
                isinstance(player, FiveCardDrawPlayer)
                and not player.folded
                and not player.all_in
                and player.id in self.betting.bets
            ):
                to_call = self.betting.amount_to_call(player.id)
                maximum = max(0, self._maximum_additional_bet(player) - to_call)
                if maximum >= min_raise:
                    user.speak_l(
                        "draw-raise-range",
                        buffer="game",
                        minimum=min_raise,
                        maximum=maximum,
                    )
                else:
                    user.speak_l(
                        "draw-no-full-raise-available",
                        buffer="game",
                        to_call=to_call,
                        chips=player.chips,
                    )
            else:
                user.speak_l("poker-min-raise", buffer="game", amount=min_raise)

    def _action_check_hand_players(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [
            p.name
            for p in self.get_active_players()
            if isinstance(p, FiveCardDrawPlayer) and not p.folded
        ]
        count = len(active)
        if count == 0:
            user.speak_l("poker-hand-players-none", buffer="game")
            return
        names = Localization.format_list_and(user.locale, active)
        if count == 1:
            user.speak_l("poker-hand-players-one", buffer="game", names=names, count=count)
        else:
            user.speak_l("poker-hand-players", buffer="game", names=names, count=count)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            if not p.hand:
                user.speak_l("poker-hand-no-cards", buffer="game")
                return
            user.speak_l("poker-your-hand", buffer="game", cards=read_cards(p.hand, user.locale))

    def _action_read_hand_value(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            desc = describe_partial_hand(p.hand, user.locale)
            user.speak(desc, buffer="game")

    def _action_read_card(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        user = self.get_user(player)
        if user:
            user.speak(card_name(p.hand[idx], user.locale), buffer="game")

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("poker-timer-disabled", buffer="game")
        else:
            user.speak_l("poker-timer-remaining", buffer="game", seconds=remaining)

    def _action_check_dealer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0 or p.all_in]
        dealer_id = self.table_state.get_button_id([p.id for p in active])
        dealer_player = self.get_player_by_id(dealer_id) if dealer_id else None
        if dealer_player:
            user.speak_l("poker-dealer-is", buffer="game", player=dealer_player.name)
        else:
            user.speak_l("draw-dealer-unavailable", buffer="game")

    def _action_check_position(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0 or p.all_in]
        if not active:
            user.speak_l("draw-position-unavailable", buffer="game")
            return
        dealer_id = self.table_state.get_button_id([p.id for p in active])
        order = [p.id for p in active]
        if dealer_id and player.id in order:
            idx = (order.index(player.id) - order.index(dealer_id)) % len(order)
            if idx == 0:
                user.speak_l("poker-position-dealer", buffer="game")
            else:
                key = "poker-position-dealer-seat" if idx == 1 else "poker-position-dealer-seats"
                user.speak_l(key, buffer="game", position=idx)
        else:
            user.speak_l("draw-position-unavailable", buffer="game")

    # ==========================================================================
    # Helpers
    # ==========================================================================
    def _turn_index_after_dealer(self, order: list[str]) -> int:
        dealer_id = self.table_state.button_player_id
        return self._turn_index_from_player(dealer_id, order, include_player=False)

    def _turn_index_from_player(
        self,
        player_id: str | None,
        order: list[str],
        *,
        include_player: bool = True,
    ) -> int:
        if not order:
            return 0
        seating = [p.id for p in self.get_active_players()]
        if not player_id or player_id not in seating:
            return 0
        start = seating.index(player_id) + (0 if include_player else 1)
        for offset in range(len(seating)):
            candidate = seating[(start + offset) % len(seating)]
            if candidate in order:
                return order.index(candidate)
        return 0

    def _maximum_additional_bet(self, player: FiveCardDrawPlayer) -> int:
        if not self.betting or self.options.raise_mode == "no_limit":
            return player.chips
        to_call = self.betting.amount_to_call(player.id)
        caps = compute_pot_limit_caps(
            self.pot_manager.total_pot(),
            to_call,
            self.options.raise_mode,
        )
        if not caps:
            return player.chips
        return min(player.chips, caps.total_cap)

    def _can_make_full_raise(self, player: FiveCardDrawPlayer) -> bool:
        if not self.betting or not self.betting.can_raise():
            return False
        to_call = self.betting.amount_to_call(player.id)
        min_raise = max(self.betting.last_raise_size, 1)
        return self._maximum_additional_bet(player) >= to_call + min_raise

    def _active_betting_ids(self) -> set[str]:
        return {
            p.id
            for p in self.get_active_players()
            if isinstance(p, FiveCardDrawPlayer) and not p.folded and (p.chips > 0 or p.all_in)
        }

    def _all_in_ids(self) -> set[str]:
        return {p.id for p in self.get_active_players() if isinstance(p, FiveCardDrawPlayer) and p.all_in}

    def _require_active_player(self, player: Player) -> FiveCardDrawPlayer | None:
        if not isinstance(player, FiveCardDrawPlayer):
            return None
        if self.current_player != player:
            return None
        if player.folded:
            return None
        return player

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "draw-not-draw-phase"
        return self._is_turn_action_enabled(player)

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.phase != "draw":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_bet_action_enabled(self, player: Player) -> str | None:
        if self.phase == "draw":
            return "draw-not-betting"
        if self.phase not in BETTING_PHASES or self._next_hand_wait_ticks > 0:
            return "poker-no-active-betting"
        return self._is_turn_action_enabled(player)

    def _is_all_in_enabled(self, player: Player) -> str | None:
        reason = self._is_bet_action_enabled(player)
        if reason:
            return reason
        if not isinstance(player, FiveCardDrawPlayer) or not self.betting:
            return "poker-no-active-betting"
        to_call = self.betting.amount_to_call(player.id)
        min_raise = max(self.betting.last_raise_size, 1)
        is_full_raise = player.chips > to_call and player.chips - to_call >= min_raise
        if is_full_raise and not self.betting.can_raise():
            return "draw-all-in-unavailable-raise-cap"
        if player.chips > self._maximum_additional_bet(player):
            return "draw-all-in-unavailable-limit"
        return None

    def _is_raise_enabled(self, player: Player) -> str | None:
        reason = self._is_bet_action_enabled(player)
        if reason:
            return reason
        if not isinstance(player, FiveCardDrawPlayer) or not self.betting:
            return "poker-no-active-betting"
        if not self.betting.can_raise():
            return "draw-raise-unavailable-cap"
        if not self._can_make_full_raise(player):
            return "draw-raise-unavailable-limit"
        return None

    def _is_bet_action_hidden(self, player: Player) -> Visibility:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p or self.status != "playing" or p.is_spectator:
            return Visibility.HIDDEN
        if self.phase in BETTING_PHASES:
            if self._next_hand_wait_ticks > 0:
                return Visibility.VISIBLE
            if p.folded:
                return Visibility.HIDDEN
            if p.all_in:
                return Visibility.VISIBLE
            if p.chips <= 0:
                return Visibility.HIDDEN
            return self._is_turn_action_hidden(player)
        if self.phase == "draw":
            return (
                Visibility.HIDDEN
                if self.current_player == player
                else Visibility.VISIBLE
            )
        if self._next_hand_wait_ticks > 0 or self.phase == "showdown":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_discard_toggle_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "action-not-playing"
        return self._is_turn_action_enabled(player)

    def _is_discard_key_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "draw-not-draw-phase"
        return self._is_turn_action_enabled(player)

    def _is_discard_toggle_hidden(self, player: Player) -> Visibility:
        if self.phase != "draw":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _get_toggle_discard_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return action_id
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return action_id
        if idx < 0 or idx >= len(p.hand):
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        name = card_name(p.hand[idx], locale)
        if idx in p.to_discard:
            return Localization.get(locale, "draw-card-discard", card=name)
        return Localization.get(locale, "draw-card-keep", card=name)

    def _get_card_key_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return action_id
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return action_id
        if idx < 0 or idx >= len(p.hand):
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        name = card_name(p.hand[idx], locale)
        if idx in p.to_discard:
            return Localization.get(locale, "draw-card-discard", card=name)
        return Localization.get(locale, "draw-card-keep", card=name)

    def _get_draw_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return Localization.get("en", "draw-draw-cards")
        count = len(p.to_discard)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "draw-draw-cards-count", count=count)

    def _get_call_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if not self.betting or self.phase not in BETTING_PHASES:
            return Localization.get(locale, "poker-call")
        key = "poker-check" if self.betting.amount_to_call(player.id) == 0 else "poker-call"
        return Localization.get(locale, key)

    def _discard_selection_error(
        self,
        player: FiveCardDrawPlayer,
        selection: set[int],
    ) -> tuple[str, dict] | None:
        if self.options.draw_limit != "four_with_ace" and len(selection) > 3:
            return "draw-you-discard-limit", {"count": 3}
        if len(selection) > 4:
            return "draw-you-discard-limit", {"count": 4}
        if len(selection) == 4:
            keeps_ace = any(
                card.rank == 1 and card_index not in selection
                for card_index, card in enumerate(player.hand)
            )
            if not keeps_ace:
                return "draw-four-requires-kept-ace", {}
        return None

    def _set_discard(self, player: FiveCardDrawPlayer, idx: int, discard: bool) -> None:
        if discard:
            candidate = set(player.to_discard)
            candidate.add(idx)
            user = self.get_user(player)
            selection_error = self._discard_selection_error(player, candidate)
            if selection_error:
                if user:
                    key, kwargs = selection_error
                    user.speak_l(key, buffer="game", **kwargs)
                return
            if idx in player.to_discard:
                return
            player.to_discard = candidate
        else:
            player.to_discard.discard(idx)

    def _action_card_key(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or self.phase != "draw":
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        self._set_discard(p, idx, discard=idx not in p.to_discard)
        self.refresh_menus(p)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _on_turn_timeout(self) -> None:
        """Called by TurnTimerMixin when time runs out."""
        player = self.current_player
        if not isinstance(player, FiveCardDrawPlayer):
            return
        if self.phase == "draw":
            self._action_draw_cards(player, "turn_timeout")
            return
        self._action_fold(player, "turn_timeout")

    def _play_draw_sounds(self, count: int) -> None:
        delay_ticks = 0
        for _ in range(count):
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks, volume=100)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks + 1, volume=100)
            delay_ticks += 6

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.get_active_players():
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.chips

    def build_game_result(self) -> GameResult:
        active = self.get_active_players()
        winner = max(active, key=lambda p: p.chips, default=None)
        winner_ids = [p.id for p in active if winner and p.chips == winner.chips]
        final_chips = {p.name: p.chips for p in active}
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": winner_ids,
                "winner_chips": winner.chips if winner else 0,
                "final_chips": final_chips,
            },
        )

    def _end_game(self, winner: FiveCardDrawPlayer | None) -> None:
        self.play_sound("game_pig/win.ogg")
        if winner:
            self.broadcast_personal_l(winner, "poker-you-win-game", "poker-player-wins-game", buffer="game")
        self.finish_game()

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_chips = result.custom_data.get("final_chips", {})
        sorted_scores = sorted(final_chips.items(), key=lambda item: item[1], reverse=True)
        for i, (name, chips) in enumerate(sorted_scores, 1):
             lines.append(
                Localization.get(locale, "draw-winner-chips", rank=i, player=name, chips=chips)
            )
        return lines
