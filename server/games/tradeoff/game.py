"""
Tradeoff Game Implementation for PlayAural.

A dice trading game where players roll dice, trade unwanted ones to a shared pool,
and take dice back in turn order (lowest scorer first). After 3 iterations,
players score based on set combinations formed from their 15 accumulated dice.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import random_dice_throw_sound, roll_dice
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.preferences import DiceKeepingStyle

from .scoring import find_best_scoring
from .bot import bot_think_trading, bot_think_taking


MIN_TARGET_SCORE = 30
MAX_TARGET_SCORE = 500
ITERATIONS_PER_ROUND = 3
DICE_PER_ITERATION = 5


@dataclass
class TradeoffPlayer(Player):
    """Player state for Tradeoff game."""

    # Current hand of dice (accumulates over 3 iterations)
    hand: list[int] = field(default_factory=list)

    # Current iteration's rolled dice (before trading)
    rolled_dice: list[int] = field(default_factory=list)

    # Dice selected for trading (indices into rolled_dice)
    trading_indices: list[int] = field(default_factory=list)

    # Whether this player has confirmed their trades
    trades_confirmed: bool = False

    # Dice that were traded (stored for reveal after all confirm)
    traded_dice: list[int] = field(default_factory=list)

    # How many dice this player traded (to know how many to take back)
    dice_traded_count: int = 0

    # How many dice taken from pool so far this taking phase
    dice_taken_count: int = 0

    # Round score (accumulated during scoring phase)
    round_score: int = 0


@dataclass
class TradeoffOptions(GameOptions):
    """Options for Tradeoff game."""

    target_score: int = option_field(
        IntOption(
            default=60,
            min_val=MIN_TARGET_SCORE,
            max_val=MAX_TARGET_SCORE,
            value_key="score",
            label="tradeoff-set-target",
            prompt="tradeoff-enter-target",
            change_msg="tradeoff-option-changed-target",
            description="tradeoff-desc-target-score",
        )
    )


@dataclass
@register_game
class TradeoffGame(Game):
    """
    Tradeoff dice trading game.

    Players roll 5 dice each, select dice to trade to a shared pool, then
    take dice back from the pool in turn order (lowest scorer first).
    After 3 iterations of this, players score based on the sets they form
    from their 15 accumulated dice.

    First to reach the target score wins.
    """

    relevant_preferences = ["brief_announcements", "dice_keeping_style"]

    players: list[TradeoffPlayer] = field(default_factory=list)
    options: TradeoffOptions = field(default_factory=TradeoffOptions)

    # Game state
    phase: str = "waiting"  # waiting, trading, taking, scoring
    iteration: int = 0  # 1-3 within a round

    # Pool of traded dice
    pool: list[int] = field(default_factory=list)

    # Taking order (player ids, sorted by score)
    taking_order: list[str] = field(default_factory=list)
    taking_index: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Tradeoff"

    @classmethod
    def get_type(cls) -> str:
        return "tradeoff"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    def _get_player_score(self, player_name: str) -> int:
        """Get a player's total score from the team manager."""
        team = self._team_manager.get_team(player_name)
        return team.total_score if team else 0

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    @classmethod
    def get_leaderboard_types(cls) -> list[dict]:
        return [
            {
                "id": "score_per_round",
                "numerator": "final_scores.{player_name}",
                "denominator": "rounds_played",
                "aggregate": "sum",
                "format": "avg",
                "decimals": 1,
            },
        ]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> TradeoffPlayer:
        """Create a new player with Tradeoff-specific state."""
        return TradeoffPlayer(id=player_id, name=name, is_bot=is_bot)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: TradeoffPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast actor-owned events with listener-specific perspective."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == actor.id
            key = personal_key if is_actor else others_key
            if self._wants_brief(user):
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key

            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = actor
            payload = self._resolve_broadcast_kwargs(user.locale, payload)
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_l(
        self,
        full_key: str,
        brief_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast a global event with optional brief wording per listener."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _format_dice_values(self, values: list[int], locale: str) -> str:
        return Localization.format_list(locale, [str(value) for value in sorted(values)])

    def _format_dice_counts(self, values: list[int], locale: str) -> str:
        counts = Counter(values)
        parts = [
            Localization.get(locale, "tradeoff-die-count", value=value, count=counts[value])
            for value in range(1, 7)
            if counts[value] > 0
        ]
        return Localization.format_list(locale, parts)

    def _hand_text(self, player: TradeoffPlayer, locale: str) -> str:
        if player.hand:
            return self._format_dice_values(player.hand, locale)
        return Localization.get(locale, "tradeoff-hand-state-empty")

    def _focus_first_take_or_status(self, player: TradeoffPlayer) -> None:
        """After a direct touch action, land on the next useful Tradeoff control."""
        if not self.is_touch_client(self.get_user(player)):
            return
        if self.phase == "taking" and self.taking_index < len(self.taking_order):
            if self.taking_order[self.taking_index] == player.id:
                for value in range(1, 7):
                    if value in self.pool:
                        self.request_menu_focus(player, f"take_{value}")
                        return
        if self.phase == "trading" and player.rolled_dice and not player.trades_confirmed:
            self.request_menu_focus(player, "toggle_trade_0")
        elif self.phase == "taking":
            self.request_menu_focus(player, "view_pool")
        elif self.status == "playing":
            self.request_menu_focus(player, "view_hand")

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not MIN_TARGET_SCORE <= self.options.target_score <= MAX_TARGET_SCORE:
            errors.append(
                (
                    "tradeoff-error-target-out-of-range",
                    {
                        "score": self.options.target_score,
                        "min": MIN_TARGET_SCORE,
                        "max": MAX_TARGET_SCORE,
                    },
                )
            )
        return errors

    # ==========================================================================
    # Action guards — toggle trade (shared logic, index injected dynamically)
    # ==========================================================================

    def _is_toggle_trade_enabled(self, player: Player, index: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.phase != "trading":
            return "tradeoff-not-trading-phase"
        tp: TradeoffPlayer = player  # type: ignore
        if tp.trades_confirmed:
            return "tradeoff-already-confirmed"
        if index >= len(tp.rolled_dice):
            return ("tradeoff-no-die-position", {"position": index + 1})
        return None

    def _is_toggle_trade_hidden(self, player: Player, index: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.phase != "trading":
            return Visibility.HIDDEN
        tp: TradeoffPlayer = player  # type: ignore
        if tp.trades_confirmed:
            return Visibility.HIDDEN
        if not tp.rolled_dice:
            return Visibility.HIDDEN
        if index >= len(tp.rolled_dice):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_toggle_trade_label(self, player: Player, index: int) -> str:
        tp: TradeoffPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if index >= len(tp.rolled_dice):
            return f"Die {index + 1}"
        die_val = tp.rolled_dice[index]
        is_trading = index in tp.trading_indices
        status = Localization.get(
            locale,
            "tradeoff-trade-status-trading" if is_trading else "tradeoff-trade-status-keeping",
        )
        return Localization.get(locale, "tradeoff-toggle-trade", value=die_val, status=status)

    # Per-die enabled/hidden/label methods generated dynamically at module level.

    # ==========================================================================
    # Action guards — confirm trades
    # ==========================================================================

    def _is_confirm_trades_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.phase != "trading":
            return "tradeoff-not-trading-phase"
        tp: TradeoffPlayer = player  # type: ignore
        if tp.trades_confirmed:
            return "tradeoff-already-confirmed"
        return None

    def _is_confirm_trades_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.phase != "trading":
            return Visibility.HIDDEN
        tp: TradeoffPlayer = player  # type: ignore
        if tp.trades_confirmed:
            return Visibility.HIDDEN
        if not tp.rolled_dice:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_confirm_trades_label(self, player: Player, action_id: str) -> str:
        tp: TradeoffPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        trade_count = len(tp.trading_indices)
        return Localization.get(locale, "tradeoff-confirm-trades", count=trade_count)

    # ==========================================================================
    # Action guards — take dice (shared logic, value injected dynamically)
    # ==========================================================================

    def _is_take_enabled(self, player: Player, value: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.phase != "taking":
            return "tradeoff-not-taking-phase"
        if self.taking_index >= len(self.taking_order):
            return "action-not-your-turn"
        if self.taking_order[self.taking_index] != player.id:
            current_taker = self.get_player_by_id(self.taking_order[self.taking_index])
            if current_taker:
                return ("tradeoff-not-your-take-turn", {"player": current_taker.name})
            return "action-not-your-turn"
        tp: TradeoffPlayer = player  # type: ignore
        if tp.dice_taken_count >= tp.dice_traded_count:
            return "tradeoff-no-more-takes"
        if value not in self.pool:
            return ("tradeoff-not-in-pool", {"value": value})
        return None

    def _is_take_hidden(self, player: Player, value: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.phase != "taking":
            return Visibility.HIDDEN
        if self.taking_index >= len(self.taking_order):
            return Visibility.HIDDEN
        if self.taking_order[self.taking_index] != player.id:
            return Visibility.HIDDEN
        tp: TradeoffPlayer = player  # type: ignore
        if tp.dice_taken_count >= tp.dice_traded_count:
            return Visibility.HIDDEN
        if value not in self.pool:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_take_label(self, player: Player, value: int) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        count = self.pool.count(value)
        return Localization.get(locale, "tradeoff-take-die", value=value, remaining=count)

    # Per-value take enabled/hidden/label methods generated dynamically at module level.

    # ==========================================================================
    # Action guards — dice keybind actions (always hidden, keybind-dispatched)
    # ==========================================================================

    def _is_dice_key_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"

        value = 0
        if action_id:
            try:
                value = int(action_id.split("_")[-1])
            except ValueError:
                value = 0

        tp: TradeoffPlayer = player  # type: ignore
        user = self.get_user(player)
        style = (
            user.preferences.get_effective(
                "dice_keeping_style", game_type=self.get_type()
            )
            if user
            else DiceKeepingStyle.INDEX_BASED
        )

        if self.phase == "trading":
            if tp.trades_confirmed:
                return "tradeoff-already-confirmed"
            if not tp.rolled_dice:
                return "tradeoff-no-rolled-dice"
            if action_id and action_id.startswith("dice_trade_"):
                if style != DiceKeepingStyle.VALUE_BASED:
                    return "tradeoff-value-trade-style-required"
                if value not in [
                    die
                    for index, die in enumerate(tp.rolled_dice)
                    if index not in tp.trading_indices
                ]:
                    return ("tradeoff-no-kept-die-value", {"value": value})
                return None
            if style == DiceKeepingStyle.INDEX_BASED:
                if not 1 <= value <= len(tp.rolled_dice):
                    return ("tradeoff-no-die-position", {"position": value})
                return None
            if value not in [
                die
                for index, die in enumerate(tp.rolled_dice)
                if index in tp.trading_indices
            ]:
                return ("tradeoff-no-trading-die-value", {"value": value})
            return None

        if self.phase == "taking":
            if action_id and action_id.startswith("dice_trade_"):
                return "tradeoff-use-plain-number-to-take"
            if self.taking_index >= len(self.taking_order):
                return "action-not-your-turn"
            if self.taking_order[self.taking_index] != player.id:
                current_taker = self.get_player_by_id(self.taking_order[self.taking_index])
                if current_taker:
                    return ("tradeoff-not-your-take-turn", {"player": current_taker.name})
                return "action-not-your-turn"
            if tp.dice_taken_count >= tp.dice_traded_count:
                return "tradeoff-no-more-takes"
            if value not in self.pool:
                return ("tradeoff-not-in-pool", {"value": value})
            return None

        return "tradeoff-no-dice-key-phase"

    def _is_dice_key_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    # ==========================================================================
    # Action guards — view actions
    # ==========================================================================

    def _is_view_hand_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_hand_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing" and not player.is_spectator:
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_pool_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_pool_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_players_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_players_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: TradeoffPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Trading phase actions — toggle each die (menu items, phase-gated)
        for i in range(DICE_PER_ITERATION):
            action_set.add(
                Action(
                    id=f"toggle_trade_{i}",
                    label=f"Die {i + 1}",
                    handler="_action_toggle_trade",
                    is_enabled=f"_is_toggle_trade_{i}_enabled",
                    is_hidden=f"_is_toggle_trade_{i}_hidden",
                    get_label=f"_get_toggle_trade_{i}_label",
                    show_in_actions_menu=False,
                )
            )

        # Keybind-only dice key actions 1-6 (respect user's DiceKeepingStyle preference)
        for v in range(1, 7):
            action_set.add(
                Action(
                    id=f"dice_key_{v}",
                    label=f"Dice key {v}",
                    handler="_action_dice_key",
                    is_enabled="_is_dice_key_enabled",
                    is_hidden="_is_dice_key_hidden",
                    show_in_actions_menu=False,
                )
            )
            # Shift+key for trading by face value (Quentin C style)
            action_set.add(
                Action(
                    id=f"dice_trade_{v}",
                    label=f"Trade {v}",
                    handler="_action_dice_trade",
                    is_enabled="_is_dice_key_enabled",
                    is_hidden="_is_dice_key_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Confirm trades
        action_set.add(
            Action(
                id="confirm_trades",
                label=Localization.get(locale, "tradeoff-confirm-trades", count=0),
                handler="_action_confirm_trades",
                is_enabled="_is_confirm_trades_enabled",
                is_hidden="_is_confirm_trades_hidden",
                get_label="_get_confirm_trades_label",
                show_in_actions_menu=False,
            )
        )

        # Taking phase actions — take a die of each face value 1-6
        for v in range(1, 7):
            action_set.add(
                Action(
                    id=f"take_{v}",
                    label=f"Take a {v}",
                    handler="_action_take",
                    is_enabled=f"_is_take_{v}_enabled",
                    is_hidden=f"_is_take_{v}_hidden",
                    get_label=f"_get_take_{v}_label",
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
                id="view_hand",
                label=Localization.get(locale, "tradeoff-view-hand"),
                handler="_action_view_hand",
                is_enabled="_is_view_hand_enabled",
                is_hidden="_is_view_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="view_pool",
                label=Localization.get(locale, "tradeoff-view-pool"),
                handler="_action_view_pool",
                is_enabled="_is_view_pool_enabled",
                is_hidden="_is_view_pool_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="view_players",
                label=Localization.get(locale, "tradeoff-view-players"),
                handler="_action_view_players",
                is_enabled="_is_view_players_enabled",
                is_hidden="_is_view_players_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            info_actions = [
                "view_hand",
                "view_pool",
                "view_players",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, info_actions)
        return action_set

    # Web-specific visibility overrides for global info actions

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Number keys 1-6 for dice actions (respects user preference)
        for v in range(1, 7):
            self.define_keybind(
                str(v),
                f"Dice key {v}",
                [f"dice_key_{v}"],
                state=KeybindState.ACTIVE,
            )
            # Shift+1-6 for trading by value (Quentin C style)
            self.define_keybind(
                f"shift+{v}",
                f"Trade dice {v}",
                [f"dice_trade_{v}"],
                state=KeybindState.ACTIVE,
            )

        self.define_keybind("b", "Confirm trades", ["confirm_trades"], state=KeybindState.ACTIVE)
        self.define_keybind("h", "View hand", ["view_hand"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "p", "View pool", ["view_pool"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "v", "View players", ["view_players"], state=KeybindState.ACTIVE, include_spectators=True
        )

    # ==========================================================================
    # Unified action handlers (extract parameter from action_id)
    # ==========================================================================

    def _action_toggle_trade(self, player: Player, action_id: str) -> None:
        index = int(action_id.split("_")[-1])
        self._toggle_trade(player, index)

    def _action_dice_key(self, player: Player, action_id: str) -> None:
        key_num = int(action_id.split("_")[-1])
        self._handle_dice_key(player, key_num)

    def _action_dice_trade(self, player: Player, action_id: str) -> None:
        value = int(action_id.split("_")[-1])
        self._handle_dice_trade(player, value)

    def _action_take(self, player: Player, action_id: str) -> None:
        value = int(action_id.split("_")[-1])
        self._take_die(player, value)

    # ==========================================================================
    # Trading logic
    # ==========================================================================

    def _handle_dice_key(self, player: Player, key_num: int) -> None:
        """
        Handle a dice key press (1-6).

        PlayAural style: toggle die at index (key_num - 1), keys 1-5.
        Value-based style: keep (unmark) first trading die with that face value.
        """
        user = self.get_user(player)
        if not user:
            return
        if self.phase == "taking":
            self._take_die(player, key_num)
            return
        style = user.preferences.get_effective(
            "dice_keeping_style", game_type=self.get_type()
        )
        if style == DiceKeepingStyle.INDEX_BASED:
            if key_num <= 5:
                self._toggle_trade(player, key_num - 1)
        else:
            self._keep_by_value(player, key_num)

    def _handle_dice_trade(self, player: Player, value: int) -> None:
        """
        Handle Shift+key press (trade by face value).

        Only active in value-based style; silent in index-based style.
        """
        user = self.get_user(player)
        if not user:
            return
        effective_style = user.preferences.get_effective(
            "dice_keeping_style", game_type=self.get_type()
        )
        if effective_style == DiceKeepingStyle.VALUE_BASED:
            self._trade_by_value(player, value)

    def _keep_by_value(self, player: Player, value: int) -> None:
        """Keep the first trading die with the given face value (value-based style)."""
        tp: TradeoffPlayer = player  # type: ignore
        if self.phase != "trading" or tp.trades_confirmed:
            return
        for i, die_val in enumerate(tp.rolled_dice):
            if die_val == value and i in tp.trading_indices:
                tp.trading_indices.remove(i)
                user = self.get_user(player)
                if user:
                    user.speak_l("tradeoff-keeping", buffer="game", value=value)
                self.refresh_menus(player)
                return

    def _trade_by_value(self, player: Player, value: int) -> None:
        """Trade the first keeping die with the given face value (Quentin C style)."""
        tp: TradeoffPlayer = player  # type: ignore
        if self.phase != "trading" or tp.trades_confirmed:
            return
        for i, die_val in enumerate(tp.rolled_dice):
            if die_val == value and i not in tp.trading_indices:
                tp.trading_indices.append(i)
                user = self.get_user(player)
                if user:
                    user.speak_l("tradeoff-trading", buffer="game", value=value)
                self.refresh_menus(player)
                return

    def _toggle_trade(self, player: Player, index: int) -> None:
        """Toggle whether a die at the given index is being traded."""
        tp: TradeoffPlayer = player  # type: ignore
        if self.phase != "trading" or tp.trades_confirmed:
            return
        if index >= len(tp.rolled_dice):
            return
        die_value = tp.rolled_dice[index]
        user = self.get_user(player)
        if index in tp.trading_indices:
            tp.trading_indices.remove(index)
            if user:
                user.speak_l("tradeoff-keeping", buffer="game", value=die_value)
        else:
            tp.trading_indices.append(index)
            if user:
                user.speak_l("tradeoff-trading", buffer="game", value=die_value)
        self.refresh_menus(player)

    def _action_confirm_trades(self, player: Player, action_id: str) -> None:
        """Confirm the player's trade selections."""
        tp: TradeoffPlayer = player  # type: ignore
        if self.phase != "trading" or tp.trades_confirmed:
            return

        tp.trades_confirmed = True
        tp.dice_traded_count = len(tp.trading_indices)

        # Store traded dice for announcement after all players confirm
        tp.traded_dice = [tp.rolled_dice[i] for i in tp.trading_indices]

        # Move non-traded dice to hand; traded dice to pool
        for i, die_val in enumerate(tp.rolled_dice):
            if i in tp.trading_indices:
                self.pool.append(die_val)
            else:
                tp.hand.append(die_val)

        tp.rolled_dice = []
        tp.trading_indices = []

        self._check_all_traded()
        self._focus_first_take_or_status(tp)
        self.refresh_menus()

    def _check_all_traded(self) -> None:
        """Move to the taking phase once every active player has confirmed."""
        active_players = self.get_active_players()
        if not all(p.trades_confirmed for p in active_players):
            return

        # Announce what each player traded (locale-formatted per recipient)
        for p in active_players:
            tp: TradeoffPlayer = p  # type: ignore
            self._broadcast_trade_reveal(tp)

        if self.pool:
            self._start_taking_phase()
        else:
            self._end_iteration()

    def _broadcast_trade_reveal(self, actor: TradeoffPlayer) -> None:
        """Reveal one player's confirmed trade with actor/observer wording."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == actor.id
            payload: dict[str, int | str] = {
                "count": len(actor.traded_dice),
            }
            if not is_actor:
                payload["player"] = actor.name

            if actor.traded_dice:
                payload["dice"] = self._format_dice_values(actor.traded_dice, user.locale)
                if self._wants_brief(user):
                    key = (
                        "tradeoff-you-traded-brief"
                        if is_actor
                        else "tradeoff-player-traded-brief"
                    )
                else:
                    key = "tradeoff-you-traded" if is_actor else "tradeoff-player-traded"
            else:
                key = (
                    "tradeoff-you-traded-none"
                    if is_actor
                    else "tradeoff-player-traded-none"
                )
            user.speak_l(key, buffer="game", **payload)

    # ==========================================================================
    # Taking logic
    # ==========================================================================

    def _take_die(self, player: Player, value: int) -> None:
        """Take a die with the specified face value from the shared pool."""
        tp: TradeoffPlayer = player  # type: ignore
        if self.phase != "taking":
            return
        if self.taking_index >= len(self.taking_order):
            return
        if self.taking_order[self.taking_index] != player.id:
            return
        if tp.dice_taken_count >= tp.dice_traded_count:
            return
        if value not in self.pool:
            return

        self.pool.remove(value)
        tp.hand.append(value)
        tp.dice_taken_count += 1

        self.broadcast_personal_l(
            player,
            "tradeoff-you-take",
            "tradeoff-player-takes",
            buffer="game",
            value=value,
        )

        # Round-robin: advance to next taker after every die taken
        self._advance_taker()
        self._focus_first_take_or_status(tp)
        self.refresh_menus()

    def _start_taking_phase(self) -> None:
        """Transition to the taking phase, lowest scorer goes first."""
        self.phase = "taking"
        active_players = self.get_active_players()

        def sort_key(p: TradeoffPlayer):
            score = self._get_player_score(p.name)
            dice_sum = sum(p.hand) if p.hand else sum(p.rolled_dice) if p.rolled_dice else 0
            return (score, dice_sum, random.random())  # nosec B311

        sorted_players = sorted(active_players, key=sort_key)
        self.taking_order = [p.id for p in sorted_players if p.dice_traded_count > 0]
        self.taking_index = 0

        for p in active_players:
            p.dice_taken_count = 0

        if self.taking_order:
            self._announce_current_taker()
        else:
            self._end_iteration()

    def _announce_current_taker(self) -> None:
        """Tell the current taker it is their turn, including turn sound."""
        if self.taking_index >= len(self.taking_order):
            return
        player = self.get_player_by_id(self.taking_order[self.taking_index])
        if player:
            user = self.get_user(player)
            if user:
                if user.preferences.play_turn_sound:
                    user.play_sound("turn.ogg")
                user.speak_l("tradeoff-your-turn-take", buffer="game")
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))  # nosec B311

    def _advance_taker(self) -> None:
        """Advance to the next player in taking order (round-robin)."""
        if not self.pool:
            self._end_iteration()
            return
        num_players = len(self.taking_order)
        if num_players == 0:
            self._end_iteration()
            return
        for _ in range(num_players):
            self.taking_index = (self.taking_index + 1) % num_players
            player = self.get_player_by_id(self.taking_order[self.taking_index])
            if player:
                tp: TradeoffPlayer = player  # type: ignore
                if tp.dice_taken_count < tp.dice_traded_count:
                    self._announce_current_taker()
                    return
        self._end_iteration()

    def _end_iteration(self) -> None:
        """End this iteration; start next or score if this was iteration 3."""
        if self.iteration < ITERATIONS_PER_ROUND:
            self._start_iteration()
        else:
            self._do_scoring()

    # ==========================================================================
    # View action handlers
    # ==========================================================================

    def _action_view_hand(self, player: Player, action_id: str) -> None:
        """Speak the player's accumulated hand."""
        tp: TradeoffPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return
        hand_str = self._hand_text(tp, user.locale)
        if tp.rolled_dice:
            roll_parts = []
            for index, value in enumerate(tp.rolled_dice):
                status_key = (
                    "tradeoff-trade-status-trading"
                    if index in tp.trading_indices
                    else "tradeoff-trade-status-keeping"
                )
                roll_parts.append(
                    Localization.get(
                        user.locale,
                        "tradeoff-roll-die-status",
                        position=index + 1,
                        value=value,
                        status=Localization.get(user.locale, status_key),
                    )
                )
            roll_str = Localization.format_list(user.locale, roll_parts)
            user.speak_l(
                "tradeoff-hand-display-with-roll",
                buffer="game",
                count=len(tp.hand),
                dice=hand_str,
                roll=roll_str,
                trade_count=len(tp.trading_indices),
            )
        elif tp.hand:
            user.speak_l(
                "tradeoff-hand-display",
                buffer="game",
                count=len(tp.hand),
                dice=hand_str,
            )
        else:
            user.speak_l("tradeoff-hand-empty", buffer="game")

    def _action_view_pool(self, player: Player, action_id: str) -> None:
        """Speak the current shared pool."""
        user = self.get_user(player)
        if not user:
            return
        if self.pool:
            pool_str = self._format_dice_counts(self.pool, user.locale)
            user.speak_l(
                "tradeoff-pool-display",
                buffer="game",
                count=len(self.pool),
                dice=pool_str,
            )
        else:
            user.speak_l("tradeoff-pool-empty", buffer="game")

    def _action_view_players(self, player: Player, action_id: str) -> None:
        """Speak each active player's hand and traded dice."""
        user = self.get_user(player)
        if not user:
            return
        for p in self.get_active_players():
            tp: TradeoffPlayer = p  # type: ignore
            hand_str = self._hand_text(tp, user.locale)
            if tp.traded_dice:
                traded_str = self._format_dice_values(tp.traded_dice, user.locale)
                user.speak_l(
                    "tradeoff-player-info",
                    buffer="game",
                    player=p.name,
                    hand=hand_str,
                    traded=traded_str,
                )
            else:
                user.speak_l(
                    "tradeoff-player-info-no-trade",
                    buffer="game",
                    player=p.name,
                    hand=hand_str,
                )

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        self.play_music("game_pig/mus.ogg")
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round, resetting all per-round player state."""
        self.round += 1
        self.iteration = 0
        self.pool = []

        for p in self.get_active_players():
            tp: TradeoffPlayer = p  # type: ignore
            tp.hand = []
            tp.rolled_dice = []
            tp.trading_indices = []
            tp.trades_confirmed = False
            tp.traded_dice = []
            tp.dice_traded_count = 0
            tp.dice_taken_count = 0
            tp.round_score = 0

        self._broadcast_global_l("tradeoff-round-start", round=self.round)
        self._start_iteration()

    def _start_iteration(self) -> None:
        """Roll dice for all players and begin the trading phase."""
        self.iteration += 1
        self.phase = "trading"
        self.pool = []

        self._broadcast_global_l("tradeoff-iteration", iteration=self.iteration)

        active_players = self.get_active_players()
        for p in active_players:
            tp: TradeoffPlayer = p  # type: ignore
            tp.rolled_dice = roll_dice(DICE_PER_ITERATION, 6)
            tp.trading_indices = list(range(DICE_PER_ITERATION))  # all dice traded by default
            tp.trades_confirmed = False
            tp.traded_dice = []
            tp.dice_traded_count = 0
            tp.dice_taken_count = 0

            user = self.get_user(p)
            if user:
                user.play_sound(random_dice_throw_sound())
                dice_str = Localization.format_list(
                    user.locale, [str(d) for d in tp.rolled_dice]
                )
                user.speak_l("tradeoff-you-rolled", buffer="game", dice=dice_str)

        for p in active_players:
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(15, 30))  # nosec B311

        self.refresh_menus()

    # ==========================================================================
    # Scoring
    # ==========================================================================

    def _format_set_description(self, locale: str, set_name: str, dice: list[int]) -> str:
        """Return a concise localized description of a scored set."""
        sorted_dice = sorted(dice)
        if set_name == "triple":
            return Localization.get(locale, "tradeoff-set-triple", value=sorted_dice[0])
        if set_name == "group":
            return Localization.get(locale, "tradeoff-set-group", value=sorted_dice[0])
        if set_name == "mini_straight":
            return Localization.get(
                locale, "tradeoff-set-mini-straight", low=sorted_dice[0], high=sorted_dice[-1]
            )
        if set_name == "straight":
            return Localization.get(
                locale, "tradeoff-set-straight", low=sorted_dice[0], high=sorted_dice[-1]
            )
        if set_name == "double_triple":
            counts = Counter(sorted_dice)
            values = sorted(counts.keys())
            return Localization.get(
                locale, "tradeoff-set-double-triple", v1=values[0], v2=values[1]
            )
        if set_name == "double_group":
            counts = Counter(sorted_dice)
            values = sorted(counts.keys())
            return Localization.get(
                locale, "tradeoff-set-double-group", v1=values[0], v2=values[1]
            )
        if set_name == "all_groups":
            return Localization.get(locale, "tradeoff-set-all-groups")
        if set_name == "all_triplets":
            return Localization.get(locale, "tradeoff-set-all-triplets")
        return set_name

    def _do_scoring(self) -> None:
        """Score every player's 15-die hand and check for a winner."""
        self.phase = "scoring"
        self.play_sound("game_pig/bank.ogg")

        active_players = self.get_active_players()
        for p in active_players:
            tp: TradeoffPlayer = p  # type: ignore
            sets = find_best_scoring(tp.hand)
            total_points = sum(s[2] for s in sets)
            tp.round_score = total_points

            self._broadcast_scoring_result(tp, sets, total_points)

            self._team_manager.add_to_team_round_score(p.name, total_points)

        self._team_manager.commit_round_scores()

        # Announce round summary
        self._broadcast_global_l(
            "tradeoff-round-scores",
            "tradeoff-round-scores-brief",
            round=self.round,
        )
        for p in active_players:
            tp: TradeoffPlayer = p  # type: ignore
            total = self._get_player_score(p.name)
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                key = (
                    "tradeoff-score-line-brief"
                    if self._wants_brief(user)
                    else "tradeoff-score-line"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    player=p.name,
                    round_points=tp.round_score,
                    total=total,
                )

        # Announce leader
        best_score = 0
        leader = None
        for p in active_players:
            score = self._get_player_score(p.name)
            if score > best_score:
                best_score = score
                leader = p
        if leader:
            self._broadcast_global_l(
                "tradeoff-leader",
                "tradeoff-leader-brief",
                player=leader.name,
                score=best_score,
            )

        # Check for winner
        for p in active_players:
            if self._get_player_score(p.name) >= self.options.target_score:
                self._end_game()
                return

        self._team_manager.reset_round_scores()
        self._start_round()

    def _broadcast_scoring_result(
        self,
        actor: TradeoffPlayer,
        sets: list[tuple[str, list[int], int]],
        total_points: int,
    ) -> None:
        """Announce one player's round score with localized set names."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == actor.id
            payload: dict[str, object] = {"points": total_points}
            if not is_actor:
                payload["player"] = actor

            if sets:
                set_descriptions = [
                    self._format_set_description(user.locale, set_name, dice_used)
                    for set_name, dice_used, _ in sets
                ]
                payload["sets"] = Localization.format_list_and(
                    user.locale, set_descriptions
                )
                if self._wants_brief(user):
                    key = (
                        "tradeoff-you-scored-brief"
                        if is_actor
                        else "tradeoff-player-scored-brief"
                    )
                else:
                    key = "tradeoff-you-scored" if is_actor else "tradeoff-player-scored"
            else:
                key = "tradeoff-you-no-sets" if is_actor else "tradeoff-no-sets"
            payload = self._resolve_broadcast_kwargs(user.locale, payload)
            user.speak_l(key, buffer="game", **payload)

    def _end_game(self) -> None:
        """Announce the winner and end the game."""
        active_players = self.get_active_players()
        high_score = max(self._get_player_score(p.name) for p in active_players)
        winners = [p for p in active_players if self._get_player_score(p.name) == high_score]

        self.play_sound("game_pig/win.ogg")

        if len(winners) == 1:
            winner: TradeoffPlayer = winners[0]  # type: ignore
            self._broadcast_actor_l(
                winner,
                "tradeoff-you-win",
                "tradeoff-winner",
                score=high_score,
            )
        else:
            winner_names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    if p in winners:
                        other_names = [name for name in winner_names if name != p.name]
                        names_str = Localization.format_list_and(user.locale, other_names)
                        user.speak_l(
                            "tradeoff-you-tie-win",
                            buffer="game",
                            players=names_str,
                            score=high_score,
                        )
                    else:
                        names_str = Localization.format_list_and(user.locale, winner_names)
                        user.speak_l(
                            "tradeoff-winners-tie",
                            buffer="game",
                            players=names_str,
                            score=high_score,
                        )

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Tradeoff-specific data."""
        active_players = self.get_active_players()
        sorted_players = sorted(
            active_players,
            key=lambda p: self._get_player_score(p.name),
            reverse=True,
        )
        final_scores = {p.name: self._get_player_score(p.name) for p in sorted_players}
        winner = sorted_players[0] if sorted_players else None

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": self._get_player_score(winner.name) if winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Tradeoff."""
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(f"{i}. {name}: {points_str}")
        return lines

    # ==========================================================================
    # Tick / bot processing
    # ==========================================================================

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return
        if self.phase == "trading":
            self._process_trading_bots()
        elif self.phase == "taking":
            self._process_taking_bot()

    def _process_trading_bots(self) -> None:
        """Drive bot decisions during the trading phase (all bots act simultaneously)."""
        for player in self.players:
            if not player.is_bot or player.is_spectator:
                continue
            tp: TradeoffPlayer = player  # type: ignore
            if tp.trades_confirmed:
                continue
            if player.bot_think_ticks > 0:
                player.bot_think_ticks -= 1
                continue
            if player.bot_pending_action:
                action_id = player.bot_pending_action
                player.bot_pending_action = None
                self.execute_action(player, action_id)
                continue
            action_id = self.bot_think(tp)
            if action_id:
                player.bot_pending_action = action_id

    def _process_taking_bot(self) -> None:
        """Drive bot decision during the taking phase (only the current taker)."""
        if self.taking_index >= len(self.taking_order):
            return
        current_taker = self.get_player_by_id(self.taking_order[self.taking_index])
        if not current_taker or not current_taker.is_bot:
            return
        tp: TradeoffPlayer = current_taker  # type: ignore
        if current_taker.bot_think_ticks > 0:
            current_taker.bot_think_ticks -= 1
            return
        if current_taker.bot_pending_action:
            action_id = current_taker.bot_pending_action
            current_taker.bot_pending_action = None
            self.execute_action(current_taker, action_id)
            return
        action_id = self.bot_think(tp)
        if action_id:
            current_taker.bot_pending_action = action_id

    def bot_think(self, player: TradeoffPlayer) -> str | None:
        """Route bot decisions to the appropriate phase AI."""
        if self.phase == "trading":
            return bot_think_trading(self, player)
        if self.phase == "taking":
            return bot_think_taking(self, player)
        return None


# =============================================================================
# Dynamic per-die toggle_trade methods (replaces 15 boilerplate stubs)
# =============================================================================

def _make_toggle_trade_enabled(index: int):
    def method(self, player, *, action_id=None):
        return self._is_toggle_trade_enabled(player, index)
    return method


def _make_toggle_trade_hidden(index: int):
    def method(self, player, *, action_id=None):
        return self._is_toggle_trade_hidden(player, index)
    return method


def _make_toggle_trade_label(index: int):
    def method(self, player, action_id):
        return self._get_toggle_trade_label(player, index)
    return method


for _i in range(5):
    setattr(TradeoffGame, f"_is_toggle_trade_{_i}_enabled", _make_toggle_trade_enabled(_i))
    setattr(TradeoffGame, f"_is_toggle_trade_{_i}_hidden", _make_toggle_trade_hidden(_i))
    setattr(TradeoffGame, f"_get_toggle_trade_{_i}_label", _make_toggle_trade_label(_i))


# =============================================================================
# Dynamic per-value take methods (replaces 18 boilerplate stubs)
# =============================================================================

def _make_take_enabled(value: int):
    def method(self, player, *, action_id=None):
        return self._is_take_enabled(player, value)
    return method


def _make_take_hidden(value: int):
    def method(self, player, *, action_id=None):
        return self._is_take_hidden(player, value)
    return method


def _make_take_label(value: int):
    def method(self, player, action_id):
        return self._get_take_label(player, value)
    return method


for _v in range(1, 7):
    setattr(TradeoffGame, f"_is_take_{_v}_enabled", _make_take_enabled(_v))
    setattr(TradeoffGame, f"_is_take_{_v}_hidden", _make_take_hidden(_v))
    setattr(TradeoffGame, f"_get_take_{_v}_label", _make_take_label(_v))
