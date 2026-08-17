"""Accessible, rules-faithful Monopoly game engine."""

from __future__ import annotations

import random
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar

from ...game_utils.actions import Action, ActionSet, EditboxInput, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.menu_management_mixin import StatusBoxBuild
from ...game_utils.options import BoolOption, GameOptions, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, Player
from ..categories import CATEGORY_BOARD
from ..registry import register_game
from . import audio as game_audio
from . import australia as _australia  # noqa: F401 - registers bundled board
from . import germany as _germany  # noqa: F401 - registers bundled board
from . import hanoi as _hanoi  # noqa: F401 - registers bundled board
from . import italy as _italy  # noqa: F401 - registers bundled board
from . import london as _london  # noqa: F401 - registers bundled board
from . import madrid as _madrid  # noqa: F401 - registers bundled board
from . import new_zealand as _new_zealand  # noqa: F401 - registers bundled board
from . import paris as _paris  # noqa: F401 - registers bundled board
from . import standard as _standard  # noqa: F401 - registers bundled board
from . import tokyo as _tokyo  # noqa: F401 - registers bundled board
from .boards import DEFAULT_BOARD_ID, get_board, get_board_ids
from .bot import (
    building_sale_damage,
    development_score,
    group_building_sale_damage,
    maximum_auction_bid,
    mortgage_damage,
    opponent_rent_pressure,
    required_counterparty_trade_gain,
    risk_adjusted_cash_reserve,
    should_buy_property,
    strategic_position_value,
    trade_value_delta,
)
from .models import (
    CARD_BACK,
    CARD_COLLECT,
    CARD_COLLECT_EACH,
    CARD_GO_TO_JAIL,
    CARD_JAIL_FREE,
    CARD_MOVE,
    CARD_NEAREST,
    CARD_PAY,
    CARD_PAY_EACH,
    CARD_REPAIRS,
    OWNABLE_SPACE_KINDS,
    SPACE_CHANCE,
    SPACE_COMMUNITY,
    SPACE_FREE_PARKING,
    SPACE_GO,
    SPACE_GO_TO_JAIL,
    SPACE_JAIL,
    SPACE_STREET,
    SPACE_TAX,
    SPACE_TRANSIT,
    SPACE_UTILITY,
    AuctionState,
    BankruptcyState,
    BoardDefinition,
    BoardSpaceDefinition,
    CardDefinition,
    DebtState,
    MortgageTransferState,
    PaymentBatchState,
    PropertyState,
    QueuedPayment,
    RentState,
    TradeState,
)
from .rules import (
    calculate_rent,
    can_build,
    can_mortgage,
    can_sell_building,
    liquid_assets,
    net_worth,
    owns_group,
    transfer_mortgage_interest,
    unmortgage_cost,
)

PHASE_SETUP = "setup"
PHASE_AWAIT_ROLL = "await_roll"
PHASE_PROPERTY = "property_decision"
PHASE_RENT = "rent_decision"
PHASE_AUCTION = "auction"
PHASE_TURN_ACTIONS = "turn_actions"
PHASE_JAIL = "jail_choice"
PHASE_DEBT = "debt"
PHASE_MANAGE = "manage"
PHASE_TRADE_BUILD = "trade_build"
PHASE_TRADE_RESPONSE = "trade_response"
PHASE_MORTGAGE_TRANSFER = "mortgage_transfer"

SELL_GROUP_OPTION_PREFIX = "group:"

STABLE_INTERRUPT_PHASES = {
    PHASE_AWAIT_ROLL,
    PHASE_PROPERTY,
    PHASE_AUCTION,
    PHASE_TURN_ACTIONS,
    PHASE_JAIL,
    PHASE_DEBT,
}

PHASE_ENTRY_ACTIONS: dict[str, tuple[str, ...]] = {
    PHASE_AWAIT_ROLL: ("roll_dice",),
    PHASE_PROPERTY: ("buy_property", "decline_property"),
    PHASE_RENT: ("claim_rent", "waive_rent"),
    PHASE_AUCTION: ("bid_minimum", "place_bid", "pass_auction"),
    PHASE_JAIL: ("jail_roll", "jail_pay", "jail_card"),
    PHASE_DEBT: ("pay_debt", "raise_cash", "declare_bankruptcy"),
    PHASE_MANAGE: (
        "choose_build_property",
        "choose_sell_property",
        "choose_mortgage_property",
        "choose_unmortgage_property",
        "choose_managed_property",
        "build",
        "sell_building",
        "sell_group_buildings",
        "mortgage",
        "unmortgage",
        "finish_management",
    ),
    PHASE_TRADE_BUILD: (
        "trade_offer_property",
        "trade_request_property",
        "trade_offer_cash",
        "trade_request_cash",
        "trade_offer_jail_card",
        "trade_request_jail_card",
        "trade_submit",
        "trade_cancel",
    ),
    PHASE_TRADE_RESPONSE: ("trade_review", "trade_accept", "trade_reject"),
    PHASE_MORTGAGE_TRANSFER: (
        "keep_received_mortgaged",
        "unmortgage_received_now",
    ),
}


@dataclass
class MonopolyPlayer(Player):
    cash: int = 0
    position: int = 0
    in_jail: bool = False
    jail_turns: int = 0
    jail_card_ids: list[str] = field(default_factory=list)
    bankrupt: bool = False
    bankruptcy_order: int = 0
    passed_go_once: bool = False
    bot_trade_turn: int = -1
    bot_trade_cooldowns: dict[str, int] = field(default_factory=dict)


@dataclass
class BoardOption(MenuOption):
    """A registry-backed option that localizes any installed board by metadata."""

    def create_action(
        self,
        option_name: str,
        game: Game,
        player: Player,
        current_value: Any,
        locale: str,
    ) -> Action:
        action = super().create_action(option_name, game, player, current_value, locale)
        if isinstance(action.input_request, MenuInput):
            action.input_request.initial_selection = "_first_menu_option"
            action.input_request.option_description = "_board_option_description"
        return action

    def get_localized_choice(self, value: str, locale: str) -> str:
        return Localization.get(locale, get_board(value).name_key)


@dataclass
class SnakeEyesBonusOption(BoolOption):
    """Describe the selected board's bonus without naming a specific board."""

    def get_description(
        self,
        locale: str,
        current_value: Any,
        *,
        game: Game | None = None,
        player: Player | None = None,
    ) -> str:
        del current_value, player
        board_id = getattr(getattr(game, "options", None), "board_id", DEFAULT_BOARD_ID)
        board = get_board(board_id)
        return Localization.get(
            locale,
            self.description,
            amount=Localization.get(
                locale, board.currency_key, amount=board.snake_eyes_bonus
            ),
        )


@dataclass
class MonopolyOptions(GameOptions):
    """Board selection and optional setup variations."""

    board_id: str = option_field(
        BoardOption(
            default=DEFAULT_BOARD_ID,
            label="monopoly-option-board",
            change_msg="monopoly-option-changed-board",
            prompt="monopoly-option-select-board",
            description="monopoly-option-board-description",
            choices=lambda game, player: game._board_option_ids(player),
            choice_labels={
                board_id: get_board(board_id).name_key for board_id in get_board_ids()
            },
            value_key="board",
        )
    )
    free_parking_cash: bool = option_field(
        BoolOption(
            default=False,
            label="monopoly-option-free-parking-cash",
            change_msg="monopoly-option-changed-free-parking-cash",
            description="monopoly-option-free-parking-cash-description",
        )
    )
    double_salary_on_go: bool = option_field(
        BoolOption(
            default=False,
            label="monopoly-option-double-salary-on-go",
            change_msg="monopoly-option-changed-double-salary-on-go",
            description="monopoly-option-double-salary-on-go-description",
        )
    )
    no_rent_in_jail: bool = option_field(
        BoolOption(
            default=False,
            label="monopoly-option-no-rent-in-jail",
            change_msg="monopoly-option-changed-no-rent-in-jail",
            description="monopoly-option-no-rent-in-jail-description",
        )
    )
    buy_after_passing_go: bool = option_field(
        BoolOption(
            default=False,
            label="monopoly-option-buy-after-passing-go",
            change_msg="monopoly-option-changed-buy-after-passing-go",
            description="monopoly-option-buy-after-passing-go-description",
        )
    )
    snake_eyes_bonus: bool = option_field(
        SnakeEyesBonusOption(
            default=False,
            label="monopoly-option-snake-eyes-bonus",
            change_msg="monopoly-option-changed-snake-eyes-bonus",
            description="monopoly-option-snake-eyes-bonus-description",
        )
    )


@register_game
@dataclass
class MonopolyGame(Game):
    """Board-driven property trading with explicit accessible decision phases."""

    relevant_preferences: ClassVar[list[str]] = ["brief_announcements"]
    bot_trade_rejection_cooldown_rounds: ClassVar[int] = 2
    touch_standard_action_order: ClassVar[tuple[str, ...]] = (
        "manage_properties",
        "propose_trade",
        "read_cash",
        "read_current_space",
        "read_my_portfolio",
        "read_status",
        "read_property_groups",
        "read_portfolios",
        "read_board",
        "whose_turn",
        "whos_at_table",
    )

    players: list[MonopolyPlayer] = field(default_factory=list)
    options: MonopolyOptions = field(default_factory=MonopolyOptions)

    phase: str = PHASE_AWAIT_ROLL
    decision_player_id: str = ""
    property_states: dict[str, PropertyState] = field(default_factory=dict)
    chance_deck: list[str] = field(default_factory=list)
    community_deck: list[str] = field(default_factory=list)
    bank_houses: int = 32
    bank_hotels: int = 12
    free_parking_pot: int = 0
    last_die_1: int = 0
    last_die_2: int = 0
    doubles_count: int = 0
    extra_roll_pending: bool = False
    pending_property_id: str = ""
    rent_state: RentState | None = None
    auction_state: AuctionState | None = None
    debt_state: DebtState | None = None
    payment_batch_state: PaymentBatchState | None = None
    trade_state: TradeState | None = None
    mortgage_transfer_state: MortgageTransferState | None = None
    bankruptcy_state: BankruptcyState | None = None
    management_property_id: str = ""
    management_resume_phase: str = ""
    management_resume_decision_player_id: str = ""
    winner_id: str = ""
    bankruptcy_counter: int = 0
    turn_number: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        # Runtime-only pacing marker. Serialized bot timers remain authoritative;
        # restoration simply gives the current bot a fresh human-sized pause.
        self._bot_pacing_actor_id = ""

    def on_discard(self) -> None:
        """Drop match-scoped bot observations when this game loses ownership."""

        self._clear_bot_strategy_memory()
        super().on_discard()

    @classmethod
    def get_name(cls) -> str:
        return "Monopoly"

    @classmethod
    def get_type(cls) -> str:
        return "monopoly"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_BOARD

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def supports_score_actions(self) -> bool:
        return False

    @property
    def board(self) -> BoardDefinition:
        return get_board(self.options.board_id)

    @property
    def alive_players(self) -> list[MonopolyPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, MonopolyPlayer) and not player.bankrupt
        ]

    @property
    def winner(self) -> MonopolyPlayer | None:
        player = self.get_player_by_id(self.winner_id) if self.winner_id else None
        return (
            player
            if isinstance(player, MonopolyPlayer) and not player.bankrupt
            else None
        )

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> MonopolyPlayer:
        return MonopolyPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        try:
            get_board(self.options.board_id)
        except ValueError:
            errors.append(
                (
                    "monopoly-error-unsupported-board",
                    {"board": self.options.board_id},
                )
            )
        return errors

    # ------------------------------------------------------------------
    # Action sets and accessible controls
    # ------------------------------------------------------------------

    def _locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _action(
        self,
        player: Player,
        action_id: str,
        label_key: str,
        handler: str,
        enabled: str,
        hidden: str,
        *,
        description_key: str | None = None,
        input_request: MenuInput | EditboxInput | None = None,
        include_spectators: bool = False,
        show_in_actions_menu: bool = False,
        get_label: str | None = None,
        get_description: str | None = None,
    ) -> Action:
        locale = self._locale(player)
        return Action(
            id=action_id,
            label=Localization.get(locale, label_key),
            handler=handler,
            is_enabled=enabled,
            is_hidden=hidden,
            description=(
                Localization.get(locale, description_key) if description_key else None
            ),
            input_request=input_request,
            include_spectators=include_spectators,
            show_in_actions_menu=show_in_actions_menu,
            get_label=get_label,
            get_description=get_description,
        )

    def create_turn_action_set(self, player: MonopolyPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        action_set.add(
            self._action(
                player,
                "roll_dice",
                "monopoly-action-roll",
                "_action_roll_dice",
                "_is_roll_enabled",
                "_is_roll_hidden",
                description_key="monopoly-desc-roll",
            )
        )
        # Desktop uses one phase-aware shortcut action so a single Space press
        # cannot execute the normal-roll action and then re-evaluate the jail
        # alternative after the first action has started its sequence.
        action_set.add(
            self._action(
                player,
                "roll_shortcut",
                "monopoly-action-roll",
                "_action_roll_shortcut",
                "_is_roll_shortcut_enabled",
                "_is_roll_shortcut_hidden",
            )
        )
        action_set.add(
            self._action(
                player,
                "buy_property",
                "monopoly-action-buy",
                "_action_buy_property",
                "_is_buy_enabled",
                "_is_buy_hidden",
                get_label="_get_buy_label",
                get_description="_get_buy_description",
            )
        )
        action_set.add(
            self._action(
                player,
                "decline_property",
                "monopoly-action-auction-property",
                "_action_decline_property",
                "_is_decline_enabled",
                "_is_decline_hidden",
                description_key="monopoly-desc-decline-property",
            )
        )
        for action_id, label_key, handler in (
            ("claim_rent", "monopoly-action-claim-rent", "_action_claim_rent"),
            ("waive_rent", "monopoly-action-waive-rent", "_action_waive_rent"),
        ):
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    "_is_rent_action_enabled",
                    "_is_rent_action_hidden",
                    get_label=(
                        "_get_claim_rent_label" if action_id == "claim_rent" else None
                    ),
                )
            )
        action_set.add(
            self._action(
                player,
                "bid_minimum",
                "monopoly-action-bid-minimum",
                "_action_bid_minimum",
                "_is_bid_enabled",
                "_is_auction_action_hidden",
                get_label="_get_minimum_bid_label",
                get_description="_get_bid_description",
            )
        )
        action_set.add(
            self._action(
                player,
                "place_bid",
                "monopoly-action-custom-bid",
                "_action_place_bid",
                "_is_bid_enabled",
                "_is_auction_action_hidden",
                get_label="_get_custom_bid_label",
                get_description="_get_bid_description",
                input_request=EditboxInput(
                    prompt="monopoly-prompt-bid",
                    bot_input="_bot_bid_input",
                ),
            )
        )
        action_set.add(
            self._action(
                player,
                "pass_auction",
                "monopoly-action-pass-auction",
                "_action_pass_auction",
                "_is_auction_action_enabled",
                "_is_auction_action_hidden",
            )
        )
        for action_id, label_key, handler, enabled in (
            (
                "jail_roll",
                "monopoly-action-jail-roll",
                "_action_jail_roll",
                "_is_jail_roll_enabled",
            ),
            (
                "jail_pay",
                "monopoly-action-jail-pay",
                "_action_jail_pay",
                "_is_jail_pay_enabled",
            ),
            (
                "jail_card",
                "monopoly-action-jail-card",
                "_action_jail_card",
                "_is_jail_card_enabled",
            ),
        ):
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    enabled,
                    "_is_jail_action_hidden",
                    get_label=(
                        "_get_jail_pay_label" if action_id == "jail_pay" else None
                    ),
                )
            )
        management_selectors = (
            (
                "choose_build_property",
                "monopoly-action-choose-build-property",
                "monopoly-desc-choose-build-property",
                "_build_property_options",
                "_build_property_option_label",
                "_property_option_description",
            ),
            (
                "choose_sell_property",
                "monopoly-action-choose-sell-property",
                "monopoly-desc-choose-sell-property",
                "_sell_property_options",
                "_sell_property_option_label",
                "_sell_property_option_description",
            ),
            (
                "choose_mortgage_property",
                "monopoly-action-choose-mortgage-property",
                "monopoly-desc-choose-mortgage-property",
                "_mortgage_property_options",
                "_mortgage_property_option_label",
                "_property_option_description",
            ),
            (
                "choose_unmortgage_property",
                "monopoly-action-choose-unmortgage-property",
                "monopoly-desc-choose-unmortgage-property",
                "_unmortgage_property_options",
                "_unmortgage_property_option_label",
                "_property_option_description",
            ),
        )
        for (
            action_id,
            label_key,
            description_key,
            options,
            option_label,
            option_description,
        ) in management_selectors:
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    "_action_choose_management_property",
                    "_is_management_selector_enabled",
                    "_is_management_selector_hidden",
                    description_key=description_key,
                    input_request=MenuInput(
                        prompt=f"monopoly-prompt-{action_id.replace('_', '-')}",
                        options=options,
                        bot_select="_first_menu_option",
                        option_label=option_label,
                        option_description=option_description,
                        initial_selection="_first_menu_option",
                    ),
                    get_label="_get_management_selector_label",
                )
            )
        for action_id, label_key, handler, enabled in (
            (
                "keep_received_mortgaged",
                "monopoly-action-keep-received-mortgaged",
                "_action_keep_received_mortgaged",
                "_is_keep_received_mortgaged_enabled",
            ),
            (
                "unmortgage_received_now",
                "monopoly-action-unmortgage-received-now",
                "_action_unmortgage_received_now",
                "_is_unmortgage_received_now_enabled",
            ),
        ):
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    enabled,
                    "_is_mortgage_transfer_action_hidden",
                    get_label="_get_mortgage_transfer_action_label",
                    get_description="_get_mortgage_transfer_action_description",
                )
            )
        for action_id, label_key, handler, enabled in (
            (
                "pay_debt",
                "monopoly-action-pay-debt",
                "_action_pay_debt",
                "_is_pay_debt_enabled",
            ),
            (
                "raise_cash",
                "monopoly-action-raise-cash",
                "_action_raise_cash",
                "_is_raise_cash_enabled",
            ),
            (
                "declare_bankruptcy",
                "monopoly-action-bankruptcy",
                "_action_declare_bankruptcy",
                "_is_bankruptcy_enabled",
            ),
        ):
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    enabled,
                    "_is_debt_action_hidden",
                    description_key=(
                        "monopoly-desc-raise-cash"
                        if action_id == "raise_cash"
                        else (
                            "monopoly-desc-bankruptcy"
                            if action_id == "declare_bankruptcy"
                            else None
                        )
                    ),
                    get_label=(
                        "_get_pay_debt_label" if action_id == "pay_debt" else None
                    ),
                )
            )
        for action_id, label_key, handler, enabled in (
            ("build", "monopoly-action-build", "_action_build", "_is_build_enabled"),
            (
                "sell_building",
                "monopoly-action-sell-building",
                "_action_sell_building",
                "_is_sell_building_enabled",
            ),
            (
                "sell_group_buildings",
                "monopoly-action-sell-group-buildings",
                "_action_sell_group_buildings",
                "_is_sell_group_buildings_enabled",
            ),
            (
                "mortgage",
                "monopoly-action-mortgage",
                "_action_mortgage",
                "_is_mortgage_enabled",
            ),
            (
                "unmortgage",
                "monopoly-action-unmortgage",
                "_action_unmortgage",
                "_is_unmortgage_enabled",
            ),
        ):
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    enabled,
                    "_is_management_action_hidden",
                    description_key=f"monopoly-desc-{action_id.replace('_', '-')}",
                    get_label="_get_management_action_label",
                )
            )
        action_set.add(
            self._action(
                player,
                "choose_managed_property",
                "monopoly-action-choose-managed-property",
                "_action_choose_managed_property",
                "_is_choose_managed_property_enabled",
                "_is_choose_managed_property_hidden",
                input_request=MenuInput(
                    prompt="monopoly-prompt-choose-managed-property",
                    options="_manage_property_options",
                    bot_select="_bot_manage_property_input",
                    option_label="_manage_property_option_label",
                    option_description="_property_option_description",
                    initial_selection="_first_menu_option",
                ),
            )
        )
        action_set.add(
            self._action(
                player,
                "back_to_property_list",
                "monopoly-action-back-to-property-list",
                "_action_choose_managed_property",
                "_is_management_action_enabled",
                "_is_back_to_property_list_hidden",
                input_request=MenuInput(
                    prompt="monopoly-prompt-back-to-property-list",
                    options="_manage_property_options",
                    bot_select="_bot_manage_property_input",
                    option_label="_manage_property_option_label",
                    option_description="_property_option_description",
                    initial_selection="_first_menu_option",
                ),
            )
        )
        action_set.add(
            self._action(
                player,
                "finish_management",
                "monopoly-action-finish-management",
                "_action_finish_management",
                "_is_management_action_enabled",
                "_is_management_action_hidden",
            )
        )
        self._add_trade_turn_actions(player, action_set)
        action_set.add(
            self._action(
                player,
                "end_turn",
                "monopoly-action-end-turn",
                "_action_end_turn",
                "_is_end_turn_enabled",
                "_is_end_turn_hidden",
            )
        )
        return action_set

    def _add_trade_turn_actions(
        self, player: MonopolyPlayer, action_set: ActionSet
    ) -> None:
        trade_inputs = {
            "trade_offer_property": MenuInput(
                prompt="monopoly-prompt-offer-property",
                options="_trade_offer_property_options",
                bot_select="_bot_trade_offer_property_input",
                option_label="_trade_offer_property_label",
                option_description="_property_option_description",
                initial_selection="_first_menu_option",
            ),
            "trade_request_property": MenuInput(
                prompt="monopoly-prompt-request-property",
                options="_trade_request_property_options",
                bot_select="_bot_trade_request_property_input",
                option_label="_trade_request_property_label",
                option_description="_property_option_description",
                initial_selection="_first_menu_option",
            ),
            "trade_offer_cash": EditboxInput(
                prompt="monopoly-prompt-offer-cash",
                default="0",
                bot_input="_bot_trade_offer_cash_input",
            ),
            "trade_request_cash": EditboxInput(
                prompt="monopoly-prompt-request-cash",
                default="0",
                bot_input="_bot_trade_request_cash_input",
            ),
            "trade_offer_jail_card": MenuInput(
                prompt="monopoly-prompt-offer-jail-card",
                options="_trade_offer_jail_card_options",
                option_label="_jail_card_option_label",
                initial_selection="_first_menu_option",
            ),
            "trade_request_jail_card": MenuInput(
                prompt="monopoly-prompt-request-jail-card",
                options="_trade_request_jail_card_options",
                option_label="_jail_card_option_label",
                initial_selection="_first_menu_option",
            ),
        }
        specs = (
            (
                "trade_offer_property",
                "monopoly-action-trade-offer-property",
                "_action_trade_toggle_offer_property",
                "_is_trade_offer_property_enabled",
            ),
            (
                "trade_request_property",
                "monopoly-action-trade-request-property",
                "_action_trade_toggle_request_property",
                "_is_trade_request_property_enabled",
            ),
            (
                "trade_offer_cash",
                "monopoly-action-trade-offer-cash",
                "_action_trade_offer_cash",
                "_is_trade_builder_enabled",
            ),
            (
                "trade_request_cash",
                "monopoly-action-trade-request-cash",
                "_action_trade_request_cash",
                "_is_trade_builder_enabled",
            ),
            (
                "trade_offer_jail_card",
                "monopoly-action-trade-offer-jail-card",
                "_action_trade_toggle_offer_jail_card",
                "_is_trade_offer_jail_card_enabled",
            ),
            (
                "trade_request_jail_card",
                "monopoly-action-trade-request-jail-card",
                "_action_trade_toggle_request_jail_card",
                "_is_trade_request_jail_card_enabled",
            ),
            (
                "trade_review",
                "monopoly-action-trade-review",
                "_action_trade_review",
                "_is_trade_review_enabled",
            ),
            (
                "trade_submit",
                "monopoly-action-trade-submit",
                "_action_trade_submit",
                "_is_trade_submit_enabled",
            ),
            (
                "trade_cancel",
                "monopoly-action-trade-cancel",
                "_action_trade_cancel",
                "_is_trade_builder_enabled",
            ),
            (
                "trade_accept",
                "monopoly-action-trade-accept",
                "_action_trade_accept",
                "_is_trade_response_enabled",
            ),
            (
                "trade_reject",
                "monopoly-action-trade-reject",
                "_action_trade_reject",
                "_is_trade_response_enabled",
            ),
        )
        for action_id, label_key, handler, enabled in specs:
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    enabled,
                    "_is_trade_action_hidden",
                    input_request=trade_inputs.get(action_id),
                    get_label="_get_trade_action_label",
                )
            )

    def create_standard_action_set(self, player: MonopolyPlayer) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        for action_id, label_key, handler, include_spectators in (
            (
                "read_cash",
                "monopoly-action-read-cash",
                "_action_read_cash",
                False,
            ),
            (
                "read_current_space",
                "monopoly-action-read-current-space",
                "_action_read_current_space",
                False,
            ),
            ("read_board", "monopoly-action-read-board", "_action_read_board", True),
            (
                "read_property_groups",
                "monopoly-action-read-property-groups",
                "_action_read_property_groups",
                True,
            ),
            (
                "read_portfolios",
                "monopoly-action-read-portfolios",
                "_action_read_portfolios",
                True,
            ),
            (
                "read_my_portfolio",
                "monopoly-action-read-my-portfolio",
                "_action_read_my_portfolio",
                False,
            ),
            ("read_status", "monopoly-action-read-status", "_action_read_status", True),
        ):
            input_request = None
            if action_id == "read_portfolios":
                input_request = MenuInput(
                    prompt="monopoly-prompt-portfolio-player",
                    options="_portfolio_player_options",
                    option_label="_portfolio_player_label",
                    initial_selection="_first_menu_option",
                )
            action_set.add(
                self._action(
                    player,
                    action_id,
                    label_key,
                    handler,
                    (
                        "_is_cash_enabled"
                        if action_id == "read_cash"
                        else (
                            "_is_current_space_enabled"
                            if action_id == "read_current_space"
                            else "_is_info_enabled"
                        )
                    ),
                    (
                        "_is_cash_hidden"
                        if action_id == "read_cash"
                        else (
                            "_is_current_space_hidden"
                            if action_id == "read_current_space"
                            else "_is_info_hidden"
                        )
                    ),
                    input_request=input_request,
                    include_spectators=include_spectators,
                    show_in_actions_menu=True,
                )
            )
        action_set.add(
            self._action(
                player,
                "manage_properties",
                "monopoly-action-manage-properties",
                "_action_manage_properties",
                "_is_manage_entry_enabled",
                "_is_mutating_standard_hidden",
                show_in_actions_menu=True,
            )
        )
        action_set.add(
            self._action(
                player,
                "propose_trade",
                "monopoly-action-propose-trade",
                "_action_propose_trade",
                "_is_propose_trade_enabled",
                "_is_mutating_standard_hidden",
                input_request=MenuInput(
                    prompt="monopoly-prompt-trade-player",
                    options="_trade_target_options",
                    bot_select="_bot_trade_target_input",
                    option_label="_trade_target_label",
                    option_description="_trade_target_description",
                    initial_selection="_first_menu_option",
                ),
                show_in_actions_menu=True,
            )
        )
        self._apply_standard_action_order(action_set, player)
        return action_set

    def _apply_standard_action_order(
        self, action_set: ActionSet, player: Player
    ) -> None:
        """Keep desktop native; apply the priority layout only to touch clients."""

        action_set._order = list(action_set._actions)
        if self.is_touch_player(player):
            self._order_touch_standard_actions(
                action_set,
                list(self.touch_standard_action_order),
            )

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "space", "Roll dice", ["roll_shortcut"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "f",
            "Read current space",
            ["read_current_space"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "v",
            "Read board",
            ["read_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+c",
            "Read property groups",
            ["read_property_groups"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            "Read cash",
            ["read_cash"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "p", "Read your portfolio", ["read_my_portfolio"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "o",
            "Read all portfolios",
            ["read_portfolios"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            "Read game status",
            ["read_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "g", "Manage properties", ["manage_properties"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "r", "Propose trade", ["propose_trade"], state=KeybindState.ACTIVE
        )

    def before_menu_build(self, player: Player) -> None:
        super().before_menu_build(player)
        turn = self.get_action_set(player, "turn")
        if turn and "roll_dice" in turn._order:
            without_anchor = [
                action_id for action_id in turn._order if action_id != "roll_dice"
            ]
            turn._order = ["roll_dice", *without_anchor]
        standard = self.get_action_set(player, "standard")
        if standard:
            self._apply_standard_action_order(standard, player)

    def _focus_after_user_transition(self, player: MonopolyPlayer) -> None:
        """Focus a newly opened turn state only for the human who caused it."""

        if (
            player.is_bot
            or self.status != "playing"
            or self.decision_player_id != player.id
        ):
            return
        action_set = self.get_action_set(player, "turn")
        if not action_set:
            return
        visible = action_set.get_visible_actions(self, player)
        visible_ids = {item.action.id for item in visible}
        preferred = (
            ("roll_dice",)
            if self.phase == PHASE_TURN_ACTIONS
            else PHASE_ENTRY_ACTIONS.get(self.phase, ())
        )
        target_id = next(
            (action_id for action_id in preferred if action_id in visible_ids),
            visible[0].action.id if visible else None,
        )
        if target_id:
            self.request_menu_focus(player, target_id)

    def _first_menu_option(self, player: Player, options: list[str]) -> str | None:
        del player
        return options[0] if options else None

    def _board_option_description(self, player: Player, board_id: str) -> str:
        return Localization.get(
            self._locale(player),
            get_board(board_id).description_key,
        )

    def _board_option_ids(self, player: Player) -> list[str]:
        """Keep the primary board first, then sort boards for this listener."""

        locale = self._locale(player)

        def sort_key(board_id: str) -> tuple[str, str]:
            name = Localization.get(locale, get_board(board_id).name_key)
            folded = name.casefold().replace("đ", "d")
            letters = "".join(
                character
                for character in unicodedata.normalize("NFKD", folded)
                if not unicodedata.combining(character)
            )
            return letters, board_id

        regional_ids = [
            board_id for board_id in get_board_ids() if board_id != DEFAULT_BOARD_ID
        ]
        return [DEFAULT_BOARD_ID, *sorted(regional_ids, key=sort_key)]

    # ------------------------------------------------------------------
    # Lifecycle, turn ownership, and bots
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        board = self.board
        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        self.clear_last_game_result()
        self.winner_id = ""
        self.property_states = {
            space.id: PropertyState()
            for space in board.spaces
            if space.kind in OWNABLE_SPACE_KINDS
        }
        self.chance_deck = [card.id for card in board.chance_cards]
        self.community_deck = [card.id for card in board.community_cards]
        random.shuffle(self.chance_deck)
        random.shuffle(self.community_deck)
        self.bank_houses = board.bank_houses
        self.bank_hotels = board.bank_hotels
        self.free_parking_pot = 0
        self._clear_interactions()

        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, MonopolyPlayer)
        ]
        for player in active:
            player.cash = board.starting_cash
            player.position = board.space_index(board.go_space_id)
            player.in_jail = False
            player.jail_turns = 0
            player.jail_card_ids.clear()
            player.bankrupt = False
            player.bankruptcy_order = 0
            player.passed_go_once = False
        self._clear_bot_strategy_memory()

        # No player owns the turn until the audible opening rolls have revealed
        # their winner. Keeping the turn list empty also prevents information
        # actions from leaking the precomputed result during the intro.
        self.turn_player_ids = []
        self.turn_index = 0
        self.phase = PHASE_SETUP
        self.bankruptcy_counter = 0
        self.turn_number = 0
        first_player, opening_rounds = self._choose_first_player(active)
        self._start_game_intro_sequence(
            opening_rounds,
            first_player.id if first_player else "",
        )

    def _clear_interactions(self) -> None:
        self.phase = PHASE_AWAIT_ROLL
        self.decision_player_id = ""
        self.pending_property_id = ""
        self.rent_state = None
        self.auction_state = None
        self.debt_state = None
        self.payment_batch_state = None
        self.trade_state = None
        self.mortgage_transfer_state = None
        self.bankruptcy_state = None
        self.management_property_id = ""
        self.management_resume_phase = ""
        self.management_resume_decision_player_id = ""
        self.last_die_1 = 0
        self.last_die_2 = 0
        self.doubles_count = 0
        self.extra_roll_pending = False

    def _choose_first_player(
        self, players: list[MonopolyPlayer]
    ) -> tuple[MonopolyPlayer | None, list[dict[str, Any]]]:
        contenders = players[:]
        rounds: list[dict[str, Any]] = []
        while len(contenders) > 1:
            rolls = {
                player.id: random.randint(1, 6) + random.randint(1, 6)
                for player in contenders
            }
            high = max(rolls.values())
            tied = [player for player in contenders if rolls[player.id] == high]
            rounds.append(
                {
                    "rolls": [
                        {"player_id": player.id, "total": rolls[player.id]}
                        for player in contenders
                    ],
                    "tied_player_ids": [player.id for player in tied]
                    if len(tied) > 1
                    else [],
                }
            )
            contenders = tied
        return (contenders[0] if contenders else None), rounds

    def _start_game_intro_sequence(
        self,
        rounds: list[dict[str, Any]],
        first_player_id: str,
    ) -> None:
        beats = [
            SequenceBeat.after_audio(
                game_audio.sound_ticks(game_audio.SOUND_BOARD_SETUP),
                ops=[
                    SequenceOperation.sound_op(game_audio.SOUND_BOARD_SETUP),
                    SequenceOperation.callback_op("announce_game_start"),
                ],
            ),
            SequenceBeat.after_audio(
                game_audio.sound_ticks(game_audio.SOUND_DECK_SHUFFLE),
                ops=[SequenceOperation.sound_op(game_audio.SOUND_DECK_SHUFFLE)],
            ),
            SequenceBeat(ops=[SequenceOperation.callback_op("start_music")]),
        ]
        for round_data in rounds:
            for roll in round_data["rolls"]:
                roll_sound = random.choice(  # nosec B311
                    game_audio.SOUND_OPENING_ROLLS
                )
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(roll_sound),
                            SequenceOperation.callback_op(
                                "announce_opening_roll", dict(roll)
                            ),
                        ],
                        delay_after_ticks=(
                            game_audio.sound_ticks(roll_sound)
                            + game_audio.OPENING_ROLL_GAP_TICKS
                        ),
                    )
                )
            tied_player_ids = round_data["tied_player_ids"]
            if tied_player_ids:
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "announce_opening_roll_tie",
                                {"player_ids": list(tied_player_ids)},
                            )
                        ],
                        delay_after_ticks=game_audio.OPENING_ROLL_GAP_TICKS,
                    )
                )
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "start_first_turn",
                        {"player_id": first_player_id},
                    )
                ]
            )
        )
        self.start_sequence(
            "monopoly_game_intro",
            beats,
            tag="monopoly_intro",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _start_turn(self, *, announce: bool) -> None:
        current = self.current_player
        if not isinstance(current, MonopolyPlayer) or current.bankrupt:
            return
        self.doubles_count = 0
        self.extra_roll_pending = False
        self.phase = PHASE_JAIL if current.in_jail else PHASE_AWAIT_ROLL
        self.decision_player_id = current.id
        self.turn_number += 1
        if announce:
            user = self.get_user(current)
            if user and user.preferences.play_turn_sound:
                user.play_sound(game_audio.SOUND_TURN)
            self._broadcast_actor(
                current,
                "monopoly-your-turn-status",
                "monopoly-player-turn-status",
                cash=lambda locale: self._money(locale, current.cash),
                space=self._space_name_for_locale(current.position),
                jailed="yes" if current.in_jail else "no",
                brief_personal_key="monopoly-your-turn-status-brief",
                brief_others_key="monopoly-player-turn-status-brief",
            )
        self.refresh_menus()

    def _finish_turn(self) -> None:
        if self.status != "playing":
            return
        self.pending_property_id = ""
        self.rent_state = None
        self.extra_roll_pending = False
        self.doubles_count = 0
        self.advance_turn(announce=False)
        self._start_turn(announce=True)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status != "playing" or not self.game_active:
            return
        if self.is_sequence_bot_paused():
            return
        actor = self._decision_player()
        if not actor or not actor.is_bot:
            self._bot_pacing_actor_id = ""
            return
        if self._bot_pacing_actor_id != actor.id:
            self._bot_pacing_actor_id = actor.id
            self._jolt_bot(actor)
            return
        BotHelper.process_bot_action(
            actor,
            lambda: self.bot_think(actor),
            lambda action_id: self._execute_bot_action(actor, action_id),
        )

    def _jolt_bot(self, player: MonopolyPlayer) -> None:
        BotHelper.jolt_bot(
            player,
            ticks=random.randint(  # nosec B311 - humanized game pacing
                game_audio.BOT_ACTION_DELAY_MIN_TICKS,
                game_audio.BOT_ACTION_DELAY_MAX_TICKS,
            ),
        )

    def _execute_bot_action(self, player: MonopolyPlayer, action_id: str) -> None:
        self.execute_action(player, action_id)
        # Force a fresh pause before the next decision, including consecutive
        # actions by the same bot in auctions, debt, trades, and management.
        self._bot_pacing_actor_id = ""

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict[str, Any],
    ) -> None:
        if callback_id == "announce_game_start":
            board = self.board
            self._broadcast_global(
                "monopoly-game-started",
                "monopoly-game-started-brief",
                players=len(self.alive_players),
                board=lambda locale: Localization.get(locale, board.name_key),
                cash=lambda locale: self._money(locale, board.starting_cash),
            )
            return
        if callback_id == "start_music":
            self.play_music(game_audio.SOUND_MUSIC_LOOP)
            return
        if callback_id == "announce_opening_roll":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer):
                self._broadcast_actor(
                    player,
                    "monopoly-you-opening-roll",
                    "monopoly-player-opening-roll",
                    total=int(payload.get("total", 0)),
                    brief_personal_key="monopoly-you-opening-roll-brief",
                    brief_others_key="monopoly-player-opening-roll-brief",
                )
            return
        if callback_id == "announce_opening_roll_tie":
            tied = [
                player
                for player_id in payload.get("player_ids", [])
                if isinstance(
                    (player := self.get_player_by_id(str(player_id))),
                    MonopolyPlayer,
                )
            ]
            if tied:
                self._broadcast_global(
                    "monopoly-opening-roll-tie",
                    "monopoly-opening-roll-tie-brief",
                    players=lambda locale: Localization.format_list_and(
                        locale, [player.name for player in tied]
                    ),
                )
            return
        if callback_id == "start_first_turn":
            active = self.alive_players
            self.set_turn_players(active)
            first_player = self._alive_player_by_id(
                str(payload.get("player_id", ""))
            )
            if first_player:
                self.current_player = first_player
            self._start_turn(announce=True)
            return
        if callback_id == "regular_roll_move":
            self._sequence_move_regular_roll(payload)
            return
        if callback_id == "award_snake_eyes_bonus":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer) and not player.bankrupt:
                self._award_snake_eyes_bonus(
                    player,
                    int(payload.get("die_1", 0)),
                    int(payload.get("die_2", 0)),
                )
            return
        if callback_id == "regular_roll_landing":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer) and not player.bankrupt:
                self._resolve_landing(player)
                if not self.has_active_sequence(tag="monopoly_card"):
                    self._focus_after_user_transition(player)
            return
        if callback_id == "regular_roll_jail":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer) and not player.bankrupt:
                self._broadcast_actor(
                    player,
                    "monopoly-you-three-doubles",
                    "monopoly-player-three-doubles",
                    jail=lambda locale: self._space_name(
                        locale, self.board.space(self.board.jail_space_id)
                    ),
                    brief_personal_key="monopoly-you-three-doubles-brief",
                    brief_others_key="monopoly-player-three-doubles-brief",
                )
                self._send_to_jail(player)
                self._focus_after_user_transition(player)
            return
        if callback_id == "jail_roll_release":
            self._sequence_release_from_jail(payload)
            return
        if callback_id == "jail_roll_move":
            self._sequence_move_regular_roll(payload)
            return
        if callback_id == "jail_roll_failed":
            self._sequence_failed_jail_roll(payload)
            return
        if callback_id == "jail_roll_landing":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer) and not player.bankrupt:
                self._resolve_landing(player)
                if not self.has_active_sequence(tag="monopoly_card"):
                    self._focus_after_user_transition(player)
            return
        if callback_id == "resolve_drawn_card":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if not isinstance(player, MonopolyPlayer) or player.bankrupt:
                return
            card = self.board.card(
                str(payload.get("deck_id", "")),
                str(payload.get("card_id", "")),
            )
            self._announce_card(player, card)
            self._resolve_card(player, card)
            if not any(
                sequence.tag == "monopoly_card"
                and sequence.sequence_id != sequence_id
                for sequence in self.active_sequences
            ):
                self._focus_after_user_transition(player)
            return
        if callback_id == "repair_card_charge":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, MonopolyPlayer) and not player.bankrupt:
                self._start_debt(
                    player,
                    "",
                    int(payload.get("amount", 0)),
                    "monopoly-debt-repairs",
                    continuation="finish_landing",
                )
                self._focus_after_user_transition(player)

    def _decision_player(self) -> MonopolyPlayer | None:
        if self.phase == PHASE_SETUP:
            return None
        player = (
            self.get_player_by_id(self.decision_player_id)
            if self.decision_player_id
            else self.current_player
        )
        return player if isinstance(player, MonopolyPlayer) else None

    def bot_think(self, player: MonopolyPlayer) -> str | None:
        if self.phase == PHASE_AWAIT_ROLL:
            return "roll_dice"
        if self.phase == PHASE_JAIL:
            if not self._bot_prefers_jail(player):
                if player.jail_card_ids:
                    return "jail_card"
                if player.cash >= self.board.jail_fine:
                    return "jail_pay"
            return "jail_roll"
        if self.phase == PHASE_PROPERTY:
            space = self.board.space(self.pending_property_id)
            return (
                "buy_property"
                if should_buy_property(
                    self.board,
                    self.property_states,
                    space,
                    player.id,
                    player.cash,
                )
                else "decline_property"
            )
        if self.phase == PHASE_RENT:
            return "claim_rent"
        if self.phase == PHASE_AUCTION:
            auction = self.auction_state
            if not auction:
                return None
            space = self.board.space(auction.property_id)
            maximum = maximum_auction_bid(
                self.board,
                self.property_states,
                space,
                player.id,
                player.cash,
            )
            if self._auction_minimum_bid() <= maximum:
                return (
                    "place_bid"
                    if int(self._bot_bid_input(player)) > self._auction_minimum_bid()
                    else "bid_minimum"
                )
            return "pass_auction"
        if self.phase == PHASE_DEBT:
            debt = self.debt_state
            if debt and player.cash >= debt.amount:
                return "pay_debt"
            if (
                debt
                and liquid_assets(
                    self.board,
                    self.property_states,
                    player.id,
                    player.cash,
                )
                >= debt.amount
            ):
                return "raise_cash"
            return "declare_bankruptcy"
        if self.phase == PHASE_TRADE_RESPONSE:
            return (
                "trade_accept"
                if self._bot_should_accept_trade(player)
                else "trade_reject"
            )
        if self.phase == PHASE_MORTGAGE_TRANSFER:
            context = self._current_mortgage_transfer(player)
            if context:
                space, _ = context
                cost = unmortgage_cost(
                    space.mortgage_value,
                    self.board.rules.mortgage_interest_percent,
                )
                reserve = risk_adjusted_cash_reserve(
                    self.board,
                    self.property_states,
                    player.id,
                )
                if player.cash >= cost + reserve:
                    return "unmortgage_received_now"
            return "keep_received_mortgaged"
        if self.phase == PHASE_TRADE_BUILD:
            return self._bot_trade_builder_action(player)
        if self.phase == PHASE_MANAGE:
            if not self.management_property_id:
                return "choose_managed_property"
            choice = self._bot_management_choice(
                player,
                self.management_property_id,
            )
            if choice:
                return choice[0]
            if any(
                self._bot_management_choice(player, property_id)
                for property_id in self._other_managed_property_options(player)
            ):
                return "back_to_property_list"
            return "finish_management"
        if self.phase == PHASE_TURN_ACTIONS:
            if self.extra_roll_pending:
                return "roll_dice"
            if self._bot_has_management_opportunity(player):
                return "manage_properties"
            if player.bot_trade_turn != self.turn_number:
                player.bot_trade_turn = self.turn_number
                if self._bot_best_trade_plan(player):
                    return "propose_trade"
            return "end_turn"
        return None

    def _bot_bid_input(self, player: MonopolyPlayer) -> str:
        auction = self.auction_state
        if not auction:
            return str(self.board.rules.auction_opening_bid)
        space = self.board.space(auction.property_id)
        maximum = maximum_auction_bid(
            self.board,
            self.property_states,
            space,
            player.id,
            player.cash,
        )
        minimum = self._auction_minimum_bid()
        step = max(
            self.board.rules.auction_bid_increment,
            max(1, space.price // 10),
        )
        return str(min(maximum, max(minimum, auction.highest_bid + step)))

    def _bot_prefers_jail(self, player: MonopolyPlayer) -> bool:
        """Stay safe only when opponents create meaningful rent exposure."""

        unowned = sum(
            1 for state in self.property_states.values() if not state.owner_id
        )
        opposing_engine = any(
            state.owner_id
            and state.owner_id != player.id
            and (
                state.buildings > 0
                or owns_group(
                    self.board,
                    self.property_states,
                    state.owner_id,
                    self.board.space(property_id).group_id,
                )
            )
            for property_id, state in self.property_states.items()
        )
        mostly_owned = unowned <= max(2, len(self.property_states) // 4)
        meaningful_rent = opponent_rent_pressure(
            self.board,
            self.property_states,
            player.id,
        ) >= max(1, self.board.starting_cash // 60)
        return meaningful_rent and (opposing_engine or mostly_owned)

    def _clear_bot_strategy_memory(self) -> None:
        """Clear bounded observations that belong only to this match instance."""

        self._bot_pacing_actor_id = ""
        for player in self.players:
            if not isinstance(player, MonopolyPlayer):
                continue
            player.bot_trade_turn = -1
            player.bot_trade_cooldowns.clear()

    def _bot_management_choice(
        self,
        player: MonopolyPlayer,
        property_id: str,
    ) -> tuple[str, int] | None:
        state = self.property_states.get(property_id)
        if not state or state.owner_id != player.id:
            return None
        space = self.board.space(property_id)
        reserve = risk_adjusted_cash_reserve(
            self.board,
            self.property_states,
            player.id,
        )

        # Auctions must be funded from available cash. Taking a mortgage only
        # to keep bidding creates a fragile win followed by forced liquidation.
        if self.phase == PHASE_AUCTION or (
            self.phase == PHASE_MANAGE
            and self.management_resume_phase == PHASE_AUCTION
        ):
            return None

        if state.mortgaged:
            cost = unmortgage_cost(
                space.mortgage_value,
                self.board.rules.mortgage_interest_percent,
            )
            if player.cash >= cost + reserve:
                priority = 400 + space.price
                if owns_group(
                    self.board,
                    self.property_states,
                    player.id,
                    space.group_id,
                ):
                    priority += 1_000
                return "unmortgage", priority
            return None

        build_error = can_build(
            self.board,
            self.property_states,
            property_id,
            player.id,
            self.bank_houses,
            self.bank_hotels,
        )
        score = development_score(self.board, self.property_states, property_id)
        cash_after_build = player.cash - space.building_cost
        if (
            build_error is None
            and cash_after_build >= reserve
            and self._bot_should_develop(
                player,
                property_id,
                score=score,
                cash_after_build=cash_after_build,
                reserve=reserve,
            )
        ):
            return (
                "build",
                2_000 + score,
            )
        return None

    def _bot_should_develop(
        self,
        player: MonopolyPlayer,
        property_id: str,
        *,
        score: int,
        cash_after_build: int,
        reserve: int,
    ) -> bool:
        """Balance rent growth, liquidity, and any finite development supply."""

        level = self.property_states[property_id].buildings
        if level < 3:
            return score > 0
        # Three houses are usually the strongest return-per-dollar point. Later
        # development is worthwhile only when it leaves a second risk buffer.
        if score <= 0 or cash_after_build < reserve * 2:
            return False
        if level < 4:
            return True
        if not self.board.development.finite_supply:
            return True
        # Converting four houses into a hotel returns scarce houses to the Bank.
        # Preserve that blocking advantage while an opponent could immediately
        # use them, unless the supply is already comfortable.
        return self.bank_houses >= max(
            8, self.board.bank_houses // 4
        ) or not self._opponent_can_use_houses(player.id)

    def _opponent_can_use_houses(self, player_id: str) -> bool:
        for group in self.board.property_groups:
            spaces = self.board.group_spaces(group.id)
            if not spaces or spaces[0].kind != SPACE_STREET:
                continue
            for opponent in self.alive_players:
                if opponent.id == player_id or not owns_group(
                    self.board,
                    self.property_states,
                    opponent.id,
                    group.id,
                ):
                    continue
                if any(
                    self.property_states[space.id].buildings < 4 for space in spaces
                ):
                    return True
        return False

    def _bot_manage_property_input(
        self,
        player: MonopolyPlayer,
        options: list[str],
    ) -> str | None:
        ranked: list[tuple[int, str]] = []
        for property_id in options:
            choice = self._bot_management_choice(player, property_id)
            if choice:
                ranked.append((choice[1], property_id))
        return max(ranked, default=(0, options[0] if options else ""))[1] or None

    def _bot_has_management_opportunity(self, player: MonopolyPlayer) -> bool:
        return any(
            self._bot_management_choice(player, property_id)
            for property_id in self._manage_property_options(player)
        )

    def _bot_best_trade_plan(
        self,
        player: MonopolyPlayer,
        *,
        target_id: str = "",
    ) -> dict[str, Any] | None:
        """Find a fair, cash-safe deal that completes one of the bot's groups."""

        reserve = risk_adjusted_cash_reserve(
            self.board,
            self.property_states,
            player.id,
        )
        self._prune_bot_trade_cooldowns(player)
        player_strength = strategic_position_value(
            self.board,
            self.property_states,
            player.id,
            player.cash,
        )
        unit = max(1, self.board.starting_cash // 150)
        offered_candidates = [""] + [
            property_id
            for property_id in self._owned_property_ids(player.id)
            if self._property_is_tradeable(property_id, player.id)
            and not self.property_states[property_id].mortgaged
        ]
        best: tuple[int, dict[str, Any] | None] = (-1, None)
        for group in self.board.property_groups:
            members = self.board.group_spaces(group.id)
            owned = [
                space
                for space in members
                if self.property_states[space.id].owner_id == player.id
            ]
            missing = [space for space in members if space not in owned]
            if len(missing) != 1 or not owned:
                continue
            requested = missing[0]
            owner = self._alive_player_by_id(
                self.property_states[requested.id].owner_id
            )
            if (
                not owner
                or (target_id and owner.id != target_id)
                or self.property_states[requested.id].mortgaged
                or not self._property_is_tradeable(requested.id, owner.id)
            ):
                continue
            memory_key = self._bot_trade_memory_key(owner.id, requested.id)
            if player.bot_trade_cooldowns.get(memory_key, 0) > self.turn_number:
                continue
            owner_strength = strategic_position_value(
                self.board,
                self.property_states,
                owner.id,
                owner.cash,
            )
            owner_reserve = risk_adjusted_cash_reserve(
                self.board,
                self.property_states,
                owner.id,
            )
            for offered_id in offered_candidates:
                offered_ids = [offered_id] if offered_id else []
                requested_ids = [requested.id]
                bot_base = trade_value_delta(
                    self.board,
                    self.property_states,
                    player_id=player.id,
                    proposer_id=player.id,
                    target_id=owner.id,
                    offered_property_ids=offered_ids,
                    requested_property_ids=requested_ids,
                )
                target_base = trade_value_delta(
                    self.board,
                    self.property_states,
                    player_id=owner.id,
                    proposer_id=player.id,
                    target_id=owner.id,
                    offered_property_ids=offered_ids,
                    requested_property_ids=requested_ids,
                )
                if bot_base <= 0:
                    continue
                target_required = required_counterparty_trade_gain(
                    player_strength,
                    owner_strength,
                    bot_base,
                )
                cash_needed = max(
                    0,
                    target_required - target_base,
                    owner_reserve - owner.cash,
                )
                offered_cash = ((cash_needed + unit - 1) // unit) * unit
                if player.cash - offered_cash < reserve:
                    continue
                bot_delta = bot_base - offered_cash
                target_delta = target_base + offered_cash
                if bot_delta <= 0 or target_delta < target_required:
                    continue
                score = bot_delta + target_delta // 3
                plan = {
                    "target_id": owner.id,
                    "offered_property_id": offered_id,
                    "requested_property_id": requested.id,
                    "offered_cash": offered_cash,
                }
                if score > best[0]:
                    best = score, plan
        return best[1]

    @staticmethod
    def _bot_trade_memory_key(target_id: str, requested_property_id: str) -> str:
        return f"{target_id}:{requested_property_id}"

    def _prune_bot_trade_cooldowns(self, player: MonopolyPlayer) -> None:
        valid_keys = {
            self._bot_trade_memory_key(target.id, property_id)
            for target in self.alive_players
            if target.id != player.id
            for property_id in self.property_states
        }
        player.bot_trade_cooldowns = {
            key: expires
            for key, expires in player.bot_trade_cooldowns.items()
            if key in valid_keys and expires > self.turn_number
        }

    def _remember_rejected_bot_trade(
        self,
        proposer: MonopolyPlayer,
        trade: TradeState,
    ) -> None:
        if not proposer.is_bot:
            return
        expires = self.turn_number + max(
            2,
            self.bot_trade_rejection_cooldown_rounds * len(self.alive_players),
        )
        for property_id in trade.requested_property_ids:
            proposer.bot_trade_cooldowns[
                self._bot_trade_memory_key(trade.target_id, property_id)
            ] = expires

    def _bot_trade_target_input(
        self,
        player: MonopolyPlayer,
        options: list[str],
    ) -> str | None:
        plan = self._bot_best_trade_plan(player)
        if plan and plan["target_id"] in options:
            return str(plan["target_id"])
        return options[0] if options else None

    def _bot_current_trade_plan(
        self,
        player: MonopolyPlayer,
    ) -> dict[str, Any] | None:
        trade = self.trade_state
        if not trade or trade.proposer_id != player.id:
            return None
        return self._bot_best_trade_plan(player, target_id=trade.target_id)

    def _bot_trade_offer_property_input(
        self,
        player: MonopolyPlayer,
        options: list[str],
    ) -> str | None:
        plan = self._bot_current_trade_plan(player)
        value = str(plan["offered_property_id"]) if plan else ""
        return value if value in options else (options[0] if options else None)

    def _bot_trade_request_property_input(
        self,
        player: MonopolyPlayer,
        options: list[str],
    ) -> str | None:
        plan = self._bot_current_trade_plan(player)
        value = str(plan["requested_property_id"]) if plan else ""
        return value if value in options else (options[0] if options else None)

    def _bot_trade_offer_cash_input(self, player: MonopolyPlayer) -> str:
        plan = self._bot_current_trade_plan(player)
        return str(plan["offered_cash"] if plan else 0)

    def _bot_trade_request_cash_input(self, player: MonopolyPlayer) -> str:
        del player
        return "0"

    def _bot_trade_builder_action(self, player: MonopolyPlayer) -> str:
        trade = self.trade_state
        plan = self._bot_current_trade_plan(player)
        if not trade or not plan:
            return "trade_cancel"
        requested_id = str(plan["requested_property_id"])
        offered_id = str(plan["offered_property_id"])
        if trade.requested_property_ids != [requested_id]:
            return "trade_request_property"
        expected_offered = [offered_id] if offered_id else []
        if trade.offered_property_ids != expected_offered:
            return "trade_offer_property" if offered_id else "trade_cancel"
        if trade.offered_cash != int(plan["offered_cash"]):
            return "trade_offer_cash"
        return "trade_submit"

    def _bot_should_accept_trade(self, player: MonopolyPlayer) -> bool:
        trade = self.trade_state
        if not trade or trade.target_id != player.id:
            return False
        own_delta = trade_value_delta(
            self.board,
            self.property_states,
            player_id=player.id,
            proposer_id=trade.proposer_id,
            target_id=trade.target_id,
            offered_property_ids=trade.offered_property_ids,
            requested_property_ids=trade.requested_property_ids,
            offered_cash=trade.offered_cash,
            requested_cash=trade.requested_cash,
            offered_jail_cards=len(trade.offered_jail_card_ids),
            requested_jail_cards=len(trade.requested_jail_card_ids),
        )
        proposer_delta = trade_value_delta(
            self.board,
            self.property_states,
            player_id=trade.proposer_id,
            proposer_id=trade.proposer_id,
            target_id=trade.target_id,
            offered_property_ids=trade.offered_property_ids,
            requested_property_ids=trade.requested_property_ids,
            offered_cash=trade.offered_cash,
            requested_cash=trade.requested_cash,
            offered_jail_cards=len(trade.offered_jail_card_ids),
            requested_jail_cards=len(trade.requested_jail_card_ids),
        )
        own_interest = self._trade_transfer_interest(trade.offered_property_ids)
        proposer_interest = self._trade_transfer_interest(
            trade.requested_property_ids
        )
        own_delta -= own_interest
        proposer_delta -= proposer_interest
        remaining_cash = (
            player.cash
            - trade.requested_cash
            + trade.offered_cash
            - own_interest
        )
        reserve = risk_adjusted_cash_reserve(
            self.board,
            self.property_states,
            player.id,
        )
        proposer = self._alive_player_by_id(trade.proposer_id)
        if not proposer:
            return False
        proposer_strength = strategic_position_value(
            self.board,
            self.property_states,
            proposer.id,
            proposer.cash,
        )
        own_strength = strategic_position_value(
            self.board,
            self.property_states,
            player.id,
            player.cash,
        )
        required_gain = required_counterparty_trade_gain(
            proposer_strength,
            own_strength,
            proposer_delta,
        )
        return own_delta >= max(1, required_gain) and remaining_cash >= reserve

    # ------------------------------------------------------------------
    # Visibility and contextual disabled reasons
    # ------------------------------------------------------------------

    def _is_actor(self, player: Player, phase: str | None = None) -> bool:
        return (
            self.status == "playing"
            and not getattr(player, "bankrupt", False)
            and not self.is_sequence_gameplay_locked()
            and (phase is None or self.phase == phase)
            and self.decision_player_id == player.id
        )

    def _visible_for_actor(self, player: Player, phase: str) -> Visibility:
        # Visibility deliberately ignores sequence locks. The authoritative
        # control stays in place but resolves disabled until the movement or
        # effect completes, preserving touch and screen-reader focus anchors.
        return (
            Visibility.VISIBLE
            if (
                self.status == "playing"
                and not getattr(player, "bankrupt", False)
                and self.phase == phase
                and self.decision_player_id == player.id
            )
            else Visibility.HIDDEN
        )

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if (
            self.status != "playing"
            or player.is_spectator
            or getattr(player, "bankrupt", False)
        ):
            return Visibility.HIDDEN
        # This stable disabled control keeps every active player's turn menu from
        # collapsing while ownership of a required action moves around the table.
        return Visibility.VISIBLE

    def _is_roll_shortcut_hidden(self, player: Player) -> Visibility:
        del player
        return Visibility.HIDDEN

    def _is_roll_shortcut_enabled(self, player: Player) -> str | None:
        if self.phase == PHASE_JAIL:
            return self._is_jail_roll_enabled(player)
        return self._is_roll_enabled(player)

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.phase == PHASE_SETUP:
            return "monopoly-error-setup-in-progress"
        if (
            self.decision_player_id == player.id
            and self.is_sequence_gameplay_locked()
        ):
            return "monopoly-error-roll-resolving"
        if self._is_actor(player, PHASE_AWAIT_ROLL):
            return None
        if self._is_actor(player, PHASE_TURN_ACTIONS) and self.extra_roll_pending:
            return None
        return self._waiting_reason(player)

    def _is_buy_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_PROPERTY)

    def _can_buy_properties(self, player: MonopolyPlayer) -> bool:
        return not self.options.buy_after_passing_go or player.passed_go_once

    def _is_buy_enabled(self, player: MonopolyPlayer) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_PROPERTY):
            return self._waiting_reason(player)
        if not self._can_buy_properties(player):
            return "monopoly-error-must-pass-go-to-buy"
        space = self.board.space(self.pending_property_id)
        if player.cash < space.price:
            locale = self._locale(player)
            return (
                "monopoly-error-buy-needs-cash",
                {
                    "price": self._money(locale, space.price),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _is_decline_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_PROPERTY)

    def _is_decline_enabled(self, player: Player) -> str | None:
        return (
            None
            if self._is_actor(player, PHASE_PROPERTY)
            else self._waiting_reason(player)
        )

    def _is_rent_action_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_RENT)

    def _is_rent_action_enabled(self, player: Player) -> str | None:
        return (
            None if self._is_actor(player, PHASE_RENT) else self._waiting_reason(player)
        )

    def _is_auction_action_hidden(self, player: Player) -> Visibility:
        auction = self.auction_state
        auction_interface_open = self.phase == PHASE_AUCTION or (
            self.phase == PHASE_MANAGE
            and self.management_resume_phase == PHASE_AUCTION
        )
        return (
            Visibility.VISIBLE
            if (
                self.status == "playing"
                and auction_interface_open
                and auction
                and player.id in auction.active_bidder_ids
                and not getattr(player, "bankrupt", False)
            )
            else Visibility.HIDDEN
        )

    def _is_auction_action_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_AUCTION):
            return self._waiting_reason(player)
        if self.auction_state and self.auction_state.highest_bidder_id == player.id:
            return "monopoly-error-leading-bid-cannot-pass"
        return None

    def _is_bid_enabled(self, player: MonopolyPlayer) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_AUCTION):
            return self._waiting_reason(player)
        minimum = self._auction_minimum_bid()
        if player.cash < minimum:
            locale = self._locale(player)
            return (
                "monopoly-error-bid-needs-cash",
                {
                    "minimum": self._money(locale, minimum),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _is_jail_action_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_JAIL)

    def _is_jail_roll_enabled(self, player: Player) -> str | None:
        if (
            self.decision_player_id == player.id
            and self.is_sequence_gameplay_locked()
        ):
            return "monopoly-error-roll-resolving"
        return (
            None if self._is_actor(player, PHASE_JAIL) else self._waiting_reason(player)
        )

    def _is_jail_pay_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_JAIL):
            return self._waiting_reason(player)
        if player.cash < self.board.jail_fine:
            locale = self._locale(player)
            return (
                "monopoly-error-jail-fine-cash",
                {
                    "fine": self._money(locale, self.board.jail_fine),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _is_jail_card_enabled(self, player: MonopolyPlayer) -> str | None:
        if not self._is_actor(player, PHASE_JAIL):
            return self._waiting_reason(player)
        return None if player.jail_card_ids else "monopoly-error-no-jail-card"

    def _is_debt_action_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_DEBT)

    def _is_mortgage_transfer_action_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_MORTGAGE_TRANSFER)

    def _current_mortgage_transfer(
        self, player: MonopolyPlayer | None = None
    ) -> tuple[BoardSpaceDefinition, PropertyState] | None:
        transfer = self.mortgage_transfer_state
        if not transfer or not transfer.property_ids:
            return None
        property_id = transfer.property_ids[0]
        state = self.property_states.get(property_id)
        if not state:
            return None
        if player and (
            not self._is_actor(player, PHASE_MORTGAGE_TRANSFER)
            or state.owner_id != player.id
        ):
            return None
        return self.board.space(property_id), state

    def _is_keep_received_mortgaged_enabled(self, player: MonopolyPlayer) -> str | None:
        return (
            None
            if self._current_mortgage_transfer(player)
            else self._waiting_reason(player)
        )

    def _is_unmortgage_received_now_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        context = self._current_mortgage_transfer(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        cost = unmortgage_cost(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        if player.cash < cost:
            return (
                "monopoly-error-unmortgage-received-needs-cash",
                {
                    "cost": self._money(self._locale(player), cost),
                    "cash": self._money(self._locale(player), player.cash),
                },
            )
        return None

    def _is_pay_debt_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        debt = self.debt_state
        if not debt or not self._is_actor(player, PHASE_DEBT):
            return self._waiting_reason(player)
        if player.cash < debt.amount:
            locale = self._locale(player)
            return (
                "monopoly-error-debt-cash",
                {
                    "amount": self._money(locale, debt.amount),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _is_raise_cash_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        debt = self.debt_state
        if not debt or not self._is_actor(player, PHASE_DEBT):
            return self._waiting_reason(player)
        if player.cash >= debt.amount:
            return "monopoly-error-debt-ready"
        if (
            liquid_assets(
                self.board,
                self.property_states,
                player.id,
                player.cash,
            )
            <= player.cash
        ):
            locale = self._locale(player)
            return (
                "monopoly-error-no-assets-to-liquidate",
                {"development": self._development_collective_text(locale)},
            )
        return None

    def _is_bankruptcy_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        debt = self.debt_state
        if not debt or not self._is_actor(player, PHASE_DEBT):
            return self._waiting_reason(player)
        if (
            liquid_assets(
                self.board,
                self.property_states,
                player.id,
                player.cash,
            )
            >= debt.amount
        ):
            locale = self._locale(player)
            return (
                "monopoly-error-can-still-raise-cash",
                {"development": self._development_collective_text(locale)},
            )
        return None

    def _is_management_action_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if not self._is_actor(player, PHASE_MANAGE):
            return Visibility.HIDDEN
        if action_id != "finish_management" and not self.management_property_id:
            return Visibility.HIDDEN
        if action_id in {"build", "sell_building", "sell_group_buildings"}:
            space = (
                self.board.space(self.management_property_id)
                if self.management_property_id in self.property_states
                else None
            )
            if not space or space.kind != SPACE_STREET:
                return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_management_selector_hidden(self, player: Player) -> Visibility:
        if not self._is_actor(player, PHASE_MANAGE):
            return Visibility.HIDDEN
        return Visibility.HIDDEN if self.management_property_id else Visibility.VISIBLE

    def _is_management_selector_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_MANAGE):
            return self._waiting_reason(player)
        if action_id and self._management_selector_options(player, action_id):
            return None
        if not isinstance(player, MonopolyPlayer):
            return "monopoly-error-no-properties"
        return self._management_selector_empty_reason(player, action_id or "")

    def _is_management_action_enabled(self, player: Player) -> str | None:
        return (
            None
            if self._is_actor(player, PHASE_MANAGE)
            else self._waiting_reason(player)
        )

    def _is_choose_managed_property_hidden(self, player: Player) -> Visibility:
        if not self._is_actor(player, PHASE_MANAGE) or self.management_property_id:
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self._manage_property_options(player)
            else Visibility.HIDDEN
        )

    def _is_choose_managed_property_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_MANAGE):
            return self._waiting_reason(player)
        return (
            None
            if self._manage_property_options(player)
            else "monopoly-error-no-properties"
        )

    def _is_back_to_property_list_hidden(self, player: Player) -> Visibility:
        if not self._is_actor(player, PHASE_MANAGE):
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.management_property_id else Visibility.HIDDEN

    def _management_context(
        self, player: MonopolyPlayer
    ) -> tuple[BoardSpaceDefinition, PropertyState] | None:
        if not self._is_actor(player, PHASE_MANAGE) or not self.management_property_id:
            return None
        return (
            self.board.space(self.management_property_id),
            self.property_states[self.management_property_id],
        )

    def _is_build_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        context = self._management_context(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        return self._build_property_error(player, space.id)

    def _is_sell_building_enabled(self, player: MonopolyPlayer) -> str | None:
        context = self._management_context(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        return self._sell_property_error(player, space.id)

    def _is_sell_group_buildings_enabled(self, player: MonopolyPlayer) -> str | None:
        context = self._management_context(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        if space.kind != SPACE_STREET:
            return self._development_error_key("monopoly-error-not-your-street")
        group = self.board.group_spaces(space.group_id)
        if not all(
            self.property_states[item.id].owner_id == player.id for item in group
        ):
            return self._development_error_key("monopoly-error-need-color-set")
        if not any(self.property_states[item.id].buildings for item in group):
            return self._development_error_key("monopoly-error-no-group-buildings")
        return None

    def _is_mortgage_enabled(self, player: MonopolyPlayer) -> str | None:
        context = self._management_context(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        return self._mortgage_property_error(player, space.id)

    def _is_unmortgage_enabled(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict] | None:
        context = self._management_context(player)
        if not context:
            return self._waiting_reason(player)
        space, _ = context
        return self._unmortgage_property_error(player, space.id)

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        return self._visible_for_actor(player, PHASE_TURN_ACTIONS)

    def _is_end_turn_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_TURN_ACTIONS):
            return self._waiting_reason(player)
        if self.extra_roll_pending:
            return "monopoly-error-must-roll-doubles"
        return None

    def _is_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_info_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self.status == "playing" and self.is_touch_player(player)
            else Visibility.HIDDEN
        )

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        if self.is_touch_player(player):
            return (
                Visibility.VISIBLE
                if self.status == "playing"
                else Visibility.HIDDEN
            )
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        if self.is_touch_player(player):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_current_space_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator or getattr(player, "bankrupt", False):
            return "monopoly-error-no-current-space"
        return None

    def _is_cash_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator or not isinstance(player, MonopolyPlayer):
            return "action-not-available"
        return None

    def _is_cash_hidden(self, player: Player) -> Visibility:
        if player.is_spectator or not isinstance(player, MonopolyPlayer):
            return Visibility.HIDDEN
        return self._is_info_hidden(player)

    def _is_current_space_hidden(self, player: Player) -> Visibility:
        if player.is_spectator or getattr(player, "bankrupt", False):
            return Visibility.HIDDEN
        return self._is_info_hidden(player)

    def _is_mutating_standard_hidden(self, player: Player) -> Visibility:
        if player.is_spectator or getattr(player, "bankrupt", False):
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self.status == "playing" and self.is_touch_player(player)
            else Visibility.HIDDEN
        )

    def _can_interrupt(self, player: MonopolyPlayer) -> bool:
        if self.is_sequence_gameplay_locked():
            return False
        if self.phase not in STABLE_INTERRUPT_PHASES:
            return False
        if self.phase in {PHASE_PROPERTY, PHASE_AUCTION, PHASE_DEBT}:
            return self.decision_player_id == player.id
        return True

    def _is_manage_entry_enabled(self, player: MonopolyPlayer) -> str | None:
        transfer_management = self._is_actor(player, PHASE_MORTGAGE_TRANSFER)
        if not transfer_management and not self._can_interrupt(player):
            return self._waiting_reason(player)
        return None

    def _is_propose_trade_enabled(self, player: MonopolyPlayer) -> str | None:
        if self.phase == PHASE_AUCTION:
            return "monopoly-error-no-trade-during-auction"
        if not self._can_interrupt(player):
            return self._waiting_reason(player)
        if len(self.alive_players) < 2:
            return "monopoly-error-no-trade-targets"
        return None

    def _is_trade_action_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        build_actions = {
            "trade_offer_property",
            "trade_request_property",
            "trade_offer_cash",
            "trade_request_cash",
            "trade_offer_jail_card",
            "trade_request_jail_card",
            "trade_submit",
            "trade_cancel",
        }
        response_actions = {"trade_accept", "trade_reject"}
        review_phases = {PHASE_TRADE_BUILD, PHASE_TRADE_RESPONSE}
        if (
            self.phase in review_phases
            and self.decision_player_id == player.id
            and action_id == "trade_review"
        ):
            return Visibility.VISIBLE
        if (
            self.phase == PHASE_TRADE_BUILD
            and self.decision_player_id == player.id
            and action_id in build_actions
        ):
            return Visibility.VISIBLE
        if (
            self.phase == PHASE_TRADE_RESPONSE
            and self.decision_player_id == player.id
            and action_id in response_actions
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_trade_builder_enabled(self, player: Player) -> str | None:
        return (
            None
            if self._is_actor(player, PHASE_TRADE_BUILD)
            else self._waiting_reason(player)
        )

    def _is_trade_response_enabled(self, player: Player) -> str | None:
        return (
            None
            if self._is_actor(player, PHASE_TRADE_RESPONSE)
            else self._waiting_reason(player)
        )

    def _is_trade_review_enabled(self, player: Player) -> str | None:
        if self.phase not in {PHASE_TRADE_BUILD, PHASE_TRADE_RESPONSE}:
            return self._waiting_reason(player)
        return (
            None
            if self._is_actor(player) and self.trade_state
            else self._waiting_reason(player)
        )

    def _is_trade_offer_property_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_TRADE_BUILD):
            return self._waiting_reason(player)
        return (
            None
            if self._trade_offer_property_options(player)
            else (
                "monopoly-error-no-tradeable-properties",
                {
                    "development": self._development_collective_text(
                        self._locale(player)
                    )
                },
            )
        )

    def _is_trade_request_property_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        if not self._is_actor(player, PHASE_TRADE_BUILD):
            return self._waiting_reason(player)
        return (
            None
            if self._trade_request_property_options(player)
            else (
                "monopoly-error-target-no-tradeable-properties",
                {
                    "development": self._development_collective_text(
                        self._locale(player)
                    )
                },
            )
        )

    def _is_trade_offer_jail_card_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_TRADE_BUILD):
            return self._waiting_reason(player)
        return (
            None
            if self._trade_offer_jail_card_options(player)
            else "monopoly-error-no-jail-card"
        )

    def _is_trade_request_jail_card_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_TRADE_BUILD):
            return self._waiting_reason(player)
        return (
            None
            if self._trade_request_jail_card_options(player)
            else "monopoly-error-target-no-jail-card"
        )

    def _is_trade_submit_enabled(self, player: Player) -> str | None:
        if not self._is_actor(player, PHASE_TRADE_BUILD):
            return self._waiting_reason(player)
        error = self._validate_trade(player)
        return error

    def _waiting_reason(self, player: Player) -> str | tuple[str, dict]:
        if self.phase == PHASE_SETUP:
            return "monopoly-error-setup-in-progress"
        if self.is_sequence_gameplay_locked():
            return "monopoly-error-roll-resolving"
        actor = self._decision_player()
        if actor:
            if actor.id == player.id:
                return (
                    "monopoly-error-action-required-you",
                    {"phase": self._phase_name(self._locale(player))},
                )
            return (
                "monopoly-error-waiting-player",
                {
                    "player": actor.name,
                    "phase": self._phase_name(self._locale(player)),
                },
            )
        return "monopoly-error-action-unavailable"

    # ------------------------------------------------------------------
    # Labels and menu descriptions
    # ------------------------------------------------------------------

    def _space_name(self, locale: str, space: BoardSpaceDefinition) -> str:
        return Localization.get(locale, space.name_key)

    def _space_of_kind(self, kind: str) -> BoardSpaceDefinition:
        return next(space for space in self.board.spaces if space.kind == kind)

    def _group_name(self, locale: str, group_id: str) -> str:
        return Localization.get(locale, self.board.property_group(group_id).name_key)

    def _group_members_text(self, locale: str, group_id: str) -> str:
        return Localization.format_list_and(
            locale,
            [
                self._space_name(locale, space)
                for space in self.board.group_spaces(group_id)
            ],
        )

    def _owner_name(self, locale: str, owner_id: str) -> str:
        owner = self.get_player_by_id(owner_id) if owner_id else None
        return owner.name if owner else Localization.get(locale, "monopoly-bank")

    def _rent_schedule_text(self, locale: str, space: BoardSpaceDefinition) -> str:
        if space.kind == SPACE_STREET:
            return Localization.get(
                locale,
                self.board.development.rent_schedule_key,
                base=self._money(locale, space.rents[0]),
                house1=self._money(locale, space.rents[1]),
                house2=self._money(locale, space.rents[2]),
                house3=self._money(locale, space.rents[3]),
                house4=self._money(locale, space.rents[4]),
                hotel=self._money(locale, space.rents[5]),
            )
        if space.kind == SPACE_TRANSIT:
            return Localization.format_list_and(
                locale,
                [
                    Localization.get(
                        locale,
                        "monopoly-transit-rent-level",
                        count=count,
                        rent=self._money(locale, rent),
                    )
                    for count, rent in enumerate(space.rents, 1)
                ],
            )
        if space.kind == SPACE_UTILITY:
            return Localization.get(
                locale,
                self.board.terminology.utility_rent_schedule_key,
                single=self.board.rules.utility_single_multiplier,
                complete=self.board.rules.utility_complete_group_multiplier,
            )
        return Localization.get(locale, "monopoly-not-applicable")

    def _space_name_for_locale(self, position: int):
        space = self.board.spaces[position % len(self.board.spaces)]
        return lambda locale: self._space_name(locale, space)

    def _money(self, locale: str, amount: int) -> str:
        return Localization.get(locale, self.board.currency_key, amount=amount)

    def _get_buy_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        if not self.pending_property_id:
            return Localization.get(locale, "monopoly-action-buy")
        space = self.board.space(self.pending_property_id)
        return Localization.get(
            locale,
            "monopoly-buy-property-label",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            price=self._money(locale, space.price),
        )

    def _get_buy_description(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        if not self.pending_property_id:
            return Localization.get(locale, "monopoly-desc-buy")
        space = self.board.space(self.pending_property_id)
        return Localization.get(
            locale,
            "monopoly-buy-property-description",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            group_members=self._group_members_text(locale, space.group_id),
            price=self._money(locale, space.price),
            mortgage=self._money(locale, space.mortgage_value),
            rents=self._rent_schedule_text(locale, space),
            cash=self._money(locale, getattr(player, "cash", 0)),
        )

    def _get_claim_rent_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        rent = self.rent_state
        amount = rent.amount if rent else 0
        return Localization.get(
            locale,
            "monopoly-claim-rent-label",
            amount=self._money(locale, amount),
        )

    def _get_jail_pay_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        return Localization.get(
            locale,
            "monopoly-jail-pay-label",
            amount=self._money(locale, self.board.jail_fine),
        )

    def _auction_minimum_bid(self) -> int:
        auction = self.auction_state
        if not auction:
            return self.board.rules.auction_opening_bid
        return max(
            auction.minimum_bid,
            auction.highest_bid + self.board.rules.auction_bid_increment,
        )

    def _get_minimum_bid_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        return Localization.get(
            locale,
            "monopoly-minimum-bid-label",
            minimum=self._money(locale, self._auction_minimum_bid()),
        )

    def _get_custom_bid_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        return Localization.get(
            locale,
            "monopoly-custom-bid-label",
            minimum=self._money(locale, self._auction_minimum_bid()),
        )

    def _get_bid_description(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        auction = self.auction_state
        highest = auction.highest_bid if auction else 0
        leader = self.get_player_by_id(auction.highest_bidder_id) if auction else None
        return Localization.get(
            locale,
            "monopoly-bid-description",
            highest=self._money(locale, highest),
            leader=(
                leader.name
                if leader
                else Localization.get(locale, "monopoly-no-bidder")
            ),
            cash=self._money(locale, getattr(player, "cash", 0)),
        )

    def _get_pay_debt_label(self, player: Player, action_id: str) -> str:
        del action_id
        locale = self._locale(player)
        amount = self.debt_state.amount if self.debt_state else 0
        return Localization.get(
            locale, "monopoly-pay-debt-label", amount=self._money(locale, amount)
        )

    def _get_mortgage_transfer_action_label(
        self, player: Player, action_id: str
    ) -> str:
        locale = self._locale(player)
        context = self._current_mortgage_transfer(
            player if isinstance(player, MonopolyPlayer) else None
        )
        if not context:
            return Localization.get(
                locale, f"monopoly-action-{action_id.replace('_', '-')}"
            )
        space, _ = context
        if action_id == "unmortgage_received_now":
            cost = unmortgage_cost(
                space.mortgage_value, self.board.rules.mortgage_interest_percent
            )
            return Localization.get(
                locale,
                "monopoly-unmortgage-received-now-label",
                property=self._space_name(locale, space),
                cost=self._money(locale, cost),
            )
        interest = transfer_mortgage_interest(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        return Localization.get(
            locale,
            "monopoly-keep-received-mortgaged-label",
            property=self._space_name(locale, space),
            interest=self._money(locale, interest),
        )

    def _get_mortgage_transfer_action_description(
        self, player: Player, action_id: str
    ) -> str:
        locale = self._locale(player)
        context = self._current_mortgage_transfer(
            player if isinstance(player, MonopolyPlayer) else None
        )
        if not context:
            return ""
        space, _ = context
        return Localization.get(
            locale,
            "monopoly-mortgage-transfer-description",
            property=self._space_name(locale, space),
            interest=self._money(
                locale,
                transfer_mortgage_interest(
                    space.mortgage_value,
                    self.board.rules.mortgage_interest_percent,
                ),
            ),
            unmortgage=self._money(
                locale,
                unmortgage_cost(
                    space.mortgage_value,
                    self.board.rules.mortgage_interest_percent,
                ),
            ),
            action=action_id,
        )

    def _management_action_disabled_reason(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        if not isinstance(player, MonopolyPlayer):
            return None
        checks = {
            "build": self._is_build_enabled,
            "sell_building": self._is_sell_building_enabled,
            "sell_group_buildings": self._is_sell_group_buildings_enabled,
            "mortgage": self._is_mortgage_enabled,
            "unmortgage": self._is_unmortgage_enabled,
        }
        check = checks.get(action_id)
        return check(player) if check else None

    def _get_management_action_label(self, player: Player, action_id: str) -> str:
        locale = self._locale(player)
        context = (
            self._management_context(player)
            if isinstance(player, MonopolyPlayer)
            else None
        )
        if not context:
            return Localization.get(
                locale, f"monopoly-action-{action_id.replace('_', '-')}"
            )
        space, state = context
        if space.kind != SPACE_STREET and action_id in {
            "build",
            "sell_building",
            "sell_group_buildings",
        }:
            return Localization.get(
                locale, f"monopoly-action-{action_id.replace('_', '-')}"
            )
        reason = self._management_action_disabled_reason(player, action_id)
        if reason:
            if action_id == "build":
                return Localization.get(
                    locale, self.board.development.build_selector_key
                )
            if action_id == "sell_building":
                return Localization.get(
                    locale, self.board.development.sell_selector_key
                )
            if action_id == "sell_group_buildings":
                return Localization.get(
                    locale,
                    "monopoly-action-sell-group-development",
                    development=self._development_collective_text(locale),
                )
            return Localization.get(
                locale, f"monopoly-action-{action_id.replace('_', '-')}"
            )
        if action_id == "build":
            return Localization.get(
                locale,
                "monopoly-build-label",
                building=self._development_level_text(
                    locale, state.buildings + 1
                ),
                cost=self._money(locale, space.building_cost),
            )
        if action_id == "sell_building":
            return Localization.get(
                locale,
                "monopoly-sell-building-label",
                building=self._development_level_text(locale, state.buildings),
                value=self._money(locale, self._building_sale_value(space)),
            )
        if action_id == "sell_group_buildings":
            return Localization.get(
                locale,
                "monopoly-sell-group-buildings-label",
                group=self._group_name(locale, space.group_id),
                development=self._development_collective_text(locale),
                value=self._money(
                    locale, self._group_building_sale_value(space.group_id)
                ),
            )
        if action_id == "mortgage":
            return Localization.get(
                locale,
                "monopoly-mortgage-label",
                value=self._money(locale, space.mortgage_value),
            )
        if action_id == "unmortgage":
            return Localization.get(
                locale,
                "monopoly-unmortgage-label",
                cost=self._money(
                    locale,
                    unmortgage_cost(
                        space.mortgage_value, self.board.rules.mortgage_interest_percent
                    ),
                ),
            )
        return Localization.get(
            locale, f"monopoly-action-{action_id.replace('_', '-')}"
        )

    def _get_management_selector_label(
        self, player: Player, action_id: str
    ) -> str:
        keys = {
            "choose_build_property": self.board.development.build_selector_key,
            "choose_sell_property": self.board.development.sell_selector_key,
        }
        return Localization.get(
            self._locale(player),
            keys.get(action_id, f"monopoly-action-{action_id.replace('_', '-')}"),
        )

    def _get_trade_action_label(self, player: Player, action_id: str) -> str:
        locale = self._locale(player)
        trade = self.trade_state
        if not trade:
            return Localization.get(
                locale, f"monopoly-action-{action_id.replace('_', '-')}"
            )
        values = {
            "trade_offer_cash": self._money(locale, trade.offered_cash),
            "trade_request_cash": self._money(locale, trade.requested_cash),
            "trade_offer_property": str(len(trade.offered_property_ids)),
            "trade_request_property": str(len(trade.requested_property_ids)),
            "trade_offer_jail_card": str(len(trade.offered_jail_card_ids)),
            "trade_request_jail_card": str(len(trade.requested_jail_card_ids)),
        }
        key = f"monopoly-action-{action_id.replace('_', '-')}"
        return Localization.get(locale, key, value=values.get(action_id, ""))

    # ------------------------------------------------------------------
    # Dice, movement, spaces, cards, rent, and purchase
    # ------------------------------------------------------------------

    def _roll_pair(self) -> tuple[int, int]:
        return random.randint(1, 6), random.randint(1, 6)

    def _build_roll_cue_beats(
        self,
        player: MonopolyPlayer,
        die_1: int,
        die_2: int,
    ) -> list[SequenceBeat]:
        roll_sound = random.choice(game_audio.SOUND_DICE_ROLLS)  # nosec B311
        beats = [
            SequenceBeat.after_audio(
                game_audio.sound_ticks(roll_sound),
                ops=[SequenceOperation.sound_op(roll_sound)],
            )
        ]
        if die_1 == die_2:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(game_audio.SOUND_ROLL_DOUBLES)],
                )
            )
        if self.options.snake_eyes_bonus and (die_1, die_2) == (1, 1):
            beats.append(
                SequenceBeat.after_audio(
                    game_audio.sound_ticks(game_audio.SOUND_SNAKE_EYES_BONUS),
                    ops=[
                        SequenceOperation.callback_op(
                            "award_snake_eyes_bonus",
                            {
                                "player_id": player.id,
                                "die_1": die_1,
                                "die_2": die_2,
                            },
                        )
                    ],
                )
            )
        return beats

    def _action_roll_dice(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_roll_enabled(player):
            return
        die_1, die_2 = self._roll_pair()
        self._start_regular_roll_sequence(player, die_1, die_2)

    def _action_roll_shortcut(
        self, player: MonopolyPlayer, action_id: str
    ) -> None:
        del action_id
        if self.phase == PHASE_JAIL:
            self._action_jail_roll(player, "jail_roll")
            return
        self._action_roll_dice(player, "roll_dice")

    def _start_regular_roll_sequence(
        self,
        player: MonopolyPlayer,
        die_1: int,
        die_2: int,
    ) -> None:
        self.last_die_1 = die_1
        self.last_die_2 = die_2
        total = die_1 + die_2
        is_double = die_1 == die_2
        self._broadcast_actor(
            player,
            "monopoly-you-roll",
            "monopoly-player-roll",
            die1=die_1,
            die2=die_2,
            total=total,
            doubles="yes" if is_double else "no",
            brief_personal_key="monopoly-you-roll-brief",
            brief_others_key="monopoly-player-roll-brief",
        )
        if is_double:
            self.doubles_count += 1
        send_to_jail = (
            is_double
            and self.doubles_count >= self.board.rules.consecutive_doubles_to_jail
        )
        self.extra_roll_pending = is_double and not send_to_jail
        beats = self._build_roll_cue_beats(player, die_1, die_2)
        beats.append(SequenceBeat.pause(game_audio.ROLL_TO_LANDING_PAUSE_TICKS))
        if send_to_jail:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "regular_roll_jail", {"player_id": player.id}
                        )
                    ]
                )
            )
        else:
            beats.extend(
                [
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "regular_roll_move",
                                {"player_id": player.id, "spaces": total},
                            )
                        ],
                        delay_after_ticks=(
                            game_audio.sound_ticks(game_audio.SOUND_TOKEN_LANDED)
                            + game_audio.LANDING_TO_EVENT_PAUSE_TICKS
                        ),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "regular_roll_landing", {"player_id": player.id}
                            )
                        ]
                    ),
                ]
            )
        self.start_sequence(
            f"monopoly_regular_roll_{self.turn_number}",
            beats,
            tag="monopoly_roll",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _sequence_move_regular_roll(self, payload: dict[str, Any]) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, MonopolyPlayer) or player.bankrupt:
            return
        self._move_by(
            player,
            int(payload.get("spaces", 0)),
            collect_go=True,
            resolve_landing=False,
        )

    def _move_by(
        self,
        player: MonopolyPlayer,
        spaces: int,
        *,
        collect_go: bool,
        resolve_landing: bool = True,
    ) -> None:
        board_size = len(self.board.spaces)
        start = player.position
        destination = (start + spaces) % board_size
        go_position = self.board.space_index(self.board.go_space_id)
        distance_to_go = (go_position - start) % board_size or board_size
        if spaces >= distance_to_go and collect_go:
            self._collect_go(player, landed_on_go=destination == go_position)
        player.position = destination
        self._announce_move(player, destination, spaces)
        if resolve_landing:
            self._resolve_landing(player)

    def _move_to(
        self,
        player: MonopolyPlayer,
        destination_id: str,
        *,
        collect_go: bool,
        rent_multiplier: int = 1,
        utility_override: bool = False,
    ) -> None:
        start = player.position
        destination = self.board.space_index(destination_id)
        board_size = len(self.board.spaces)
        distance = (destination - start) % board_size
        go_position = self.board.space_index(self.board.go_space_id)
        distance_to_go = (go_position - start) % board_size or board_size
        if collect_go and (
            destination_id == self.board.go_space_id
            or (distance and distance_to_go <= distance)
        ):
            self._collect_go(
                player, landed_on_go=destination_id == self.board.go_space_id
            )
        player.position = destination
        self._announce_move(player, destination, distance)
        self._resolve_landing(
            player,
            rent_multiplier=rent_multiplier,
            utility_override=utility_override,
        )

    def _collect_go(
        self, player: MonopolyPlayer, *, landed_on_go: bool = False
    ) -> None:
        amount = self.board.go_salary
        if landed_on_go and self.options.double_salary_on_go:
            amount *= 2
        player.cash += amount
        player.passed_go_once = True
        self._broadcast_actor(
            player,
            "monopoly-you-pass-go",
            "monopoly-player-pass-go",
            go=lambda locale: self._space_name(
                locale, self.board.space(self.board.go_space_id)
            ),
            amount=lambda locale: self._money(locale, amount),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-pass-go-brief",
            brief_others_key="monopoly-player-pass-go-brief",
        )
        self.play_sound(random.choice(game_audio.SOUND_CASH_RECEIVED))  # nosec B311

    def _award_snake_eyes_bonus(
        self, player: MonopolyPlayer, die_1: int, die_2: int
    ) -> None:
        if not self.options.snake_eyes_bonus or (die_1, die_2) != (1, 1):
            return
        amount = self.board.snake_eyes_bonus
        player.cash += amount
        self._broadcast_actor(
            player,
            "monopoly-you-snake-eyes-bonus",
            "monopoly-player-snake-eyes-bonus",
            amount=lambda locale: self._money(locale, amount),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-snake-eyes-bonus-brief",
            brief_others_key="monopoly-player-snake-eyes-bonus-brief",
        )
        self.play_sound(game_audio.SOUND_SNAKE_EYES_BONUS)

    def _announce_move(
        self,
        player: MonopolyPlayer,
        destination: int,
        spaces: int,
    ) -> None:
        destination_space = self.board.spaces[destination]
        self._broadcast_actor(
            player,
            "monopoly-you-move",
            "monopoly-player-move",
            spaces=abs(spaces),
            direction="back" if spaces < 0 else "forward",
            position=destination + 1,
            destination=lambda locale: self._space_name(locale, destination_space),
            brief_personal_key="monopoly-you-move-brief",
            brief_others_key="monopoly-player-move-brief",
        )
        self.play_sound(game_audio.SOUND_TOKEN_LANDED)

    def _resolve_landing(
        self,
        player: MonopolyPlayer,
        *,
        rent_multiplier: int = 1,
        utility_override: bool = False,
    ) -> None:
        space = self.board.spaces[player.position]
        if space.kind in OWNABLE_SPACE_KINDS:
            state = self.property_states[space.id]
            if not state.owner_id:
                if not self._can_buy_properties(player):
                    self._broadcast_actor(
                        player,
                        "monopoly-you-must-pass-go-property",
                        "monopoly-player-must-pass-go-property",
                        go=lambda locale: self._space_name(
                            locale, self.board.space(self.board.go_space_id)
                        ),
                        property=lambda locale: self._space_name(locale, space),
                        brief_personal_key="monopoly-you-must-pass-go-property-brief",
                        brief_others_key="monopoly-player-must-pass-go-property-brief",
                    )
                    self._start_auction(space.id, resume_kind="landing")
                    return
                self.pending_property_id = space.id
                self.phase = PHASE_PROPERTY
                self.decision_player_id = player.id
                self._broadcast_actor(
                    player,
                    "monopoly-you-land-unowned",
                    "monopoly-player-land-unowned",
                    property=lambda locale: self._space_name(locale, space),
                    group=lambda locale: self._group_name(locale, space.group_id),
                    price=lambda locale: self._money(locale, space.price),
                    cash=lambda locale: self._money(locale, player.cash),
                    brief_personal_key="monopoly-you-land-unowned-brief",
                    brief_others_key="monopoly-player-land-unowned-brief",
                )
                self.refresh_menus()
                return
            owner = self._alive_player_by_id(state.owner_id)
            if state.owner_id == player.id:
                self._broadcast_actor(
                    player,
                    "monopoly-you-land-own-property",
                    "monopoly-player-lands-own-property",
                    property=lambda locale: self._space_name(locale, space),
                    brief_personal_key="monopoly-you-land-own-property-brief",
                    brief_others_key="monopoly-player-lands-own-property-brief",
                )
                self._finish_landing()
                return
            if owner and state.mortgaged:
                self._broadcast_actor(
                    player,
                    "monopoly-you-land-mortgaged-property",
                    "monopoly-player-lands-mortgaged-property",
                    owner=owner.name,
                    property=lambda locale: self._space_name(locale, space),
                    brief_personal_key="monopoly-you-land-mortgaged-property-brief",
                    brief_others_key="monopoly-player-lands-mortgaged-property-brief",
                )
                self._finish_landing()
                return
            if owner:
                if self.options.no_rent_in_jail and owner.in_jail:
                    self._broadcast_actor(
                        player,
                        "monopoly-you-owe-no-jailed-rent",
                        "monopoly-player-owes-no-jailed-rent",
                        owner=owner.name,
                        property=lambda locale: self._space_name(locale, space),
                        brief_personal_key="monopoly-you-owe-no-jailed-rent-brief",
                        brief_others_key="monopoly-player-owes-no-jailed-rent-brief",
                    )
                    self._finish_landing()
                    return
                dice_total = self.last_die_1 + self.last_die_2
                if space.kind == SPACE_UTILITY and utility_override:
                    die_1, die_2 = self._roll_pair()
                    dice_total = die_1 + die_2
                    self._broadcast_actor(
                        player,
                        "monopoly-your-utility-rent-roll",
                        "monopoly-player-utility-rent-roll",
                        utility=lambda locale: Localization.get(
                            locale, self.board.terminology.utility_kind_key
                        ),
                        die1=die_1,
                        die2=die_2,
                        total=dice_total,
                        brief_personal_key="monopoly-your-utility-rent-roll-brief",
                        brief_others_key="monopoly-player-utility-rent-roll-brief",
                    )
                    self.play_sound(
                        random.choice(game_audio.SOUND_DICE_ROLLS)  # nosec B311
                    )
                rent = calculate_rent(
                    self.board,
                    self.property_states,
                    space,
                    dice_total,
                    rent_multiplier=rent_multiplier,
                    utility_override=utility_override,
                )
                self.rent_state = RentState(
                    tenant_id=player.id,
                    owner_id=owner.id,
                    property_id=space.id,
                    amount=rent,
                )
                self.phase = PHASE_RENT
                self.decision_player_id = owner.id
                self._announce_rent_opportunity(owner, player, space, rent)
                self.refresh_menus()
                return
            self._finish_landing()
            return

        if space.kind == SPACE_TAX:
            self._start_debt(
                player,
                "",
                space.tax_amount,
                "monopoly-debt-tax",
                continuation="finish_landing",
            )
            return
        if space.kind == SPACE_CHANCE:
            self._draw_card(player, "chance")
            return
        if space.kind == SPACE_COMMUNITY:
            self._draw_card(player, "community")
            return
        if space.kind == SPACE_GO_TO_JAIL:
            self._send_to_jail(player)
            return
        if space.kind == SPACE_FREE_PARKING:
            if self.options.free_parking_cash:
                amount = self.free_parking_pot
                self.free_parking_pot = 0
                if amount:
                    player.cash += amount
                    self._broadcast_actor(
                        player,
                        "monopoly-you-collect-free-parking",
                        "monopoly-player-collects-free-parking",
                        space=lambda locale: self._space_name(locale, space),
                        amount=lambda locale: self._money(locale, amount),
                        cash=lambda locale: self._money(locale, player.cash),
                        brief_personal_key="monopoly-you-collect-free-parking-brief",
                        brief_others_key="monopoly-player-collects-free-parking-brief",
                    )
                    self.play_sound(game_audio.SOUND_LARGE_CASH_PAYOUT)
                else:
                    self._broadcast_actor(
                        player,
                        "monopoly-you-free-parking-empty",
                        "monopoly-player-free-parking-empty",
                        space=lambda locale: self._space_name(locale, space),
                        suppress_brief=True,
                    )
            else:
                self._broadcast_actor(
                    player,
                    "monopoly-you-free-parking",
                    "monopoly-player-free-parking",
                    space=lambda locale: self._space_name(locale, space),
                    suppress_brief=True,
                )
        elif space.kind == SPACE_JAIL:
            self._broadcast_actor(
                player,
                "monopoly-you-just-visiting",
                "monopoly-player-just-visiting",
                jail=lambda locale: self._space_name(locale, space),
                suppress_brief=True,
            )
        elif space.kind == SPACE_GO:
            self._broadcast_actor(
                player,
                "monopoly-you-land-go",
                "monopoly-player-land-go",
                go=lambda locale: self._space_name(locale, space),
                suppress_brief=True,
            )
        self._finish_landing()

    def _finish_landing(self) -> None:
        if self.status != "playing":
            return
        current = self.current_player
        if not isinstance(current, MonopolyPlayer) or current.bankrupt:
            return
        self.phase = PHASE_TURN_ACTIONS
        self.decision_player_id = current.id
        self.pending_property_id = ""
        self.rent_state = None
        self.refresh_menus()

    def _action_buy_property(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_buy_enabled(player):
            return
        space = self.board.space(self.pending_property_id)
        state = self.property_states[space.id]
        if state.owner_id:
            return
        player.cash -= space.price
        state.owner_id = player.id
        self._broadcast_actor(
            player,
            "monopoly-you-buy-property",
            "monopoly-player-buy-property",
            property=lambda locale: self._space_name(locale, space),
            group=lambda locale: self._group_name(locale, space.group_id),
            price=lambda locale: self._money(locale, space.price),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-buy-property-brief",
            brief_others_key="monopoly-player-buy-property-brief",
        )
        self.play_sound(game_audio.SOUND_PROPERTY_PURCHASED)
        self._announce_completed_groups(player, [space.id])
        self._finish_landing()
        self._focus_after_user_transition(player)

    def _action_decline_property(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if not self._is_actor(player, PHASE_PROPERTY):
            return
        property_id = self.pending_property_id
        space = self.board.space(property_id)
        self._broadcast_actor(
            player,
            "monopoly-you-decline-property",
            "monopoly-player-decline-property",
            property=lambda locale: self._space_name(locale, space),
            brief_personal_key="monopoly-you-decline-property-brief",
            brief_others_key="monopoly-player-decline-property-brief",
        )
        self.pending_property_id = ""
        self._start_auction(
            property_id, resume_kind="landing", first_bidder_id=player.id
        )
        self._focus_after_user_transition(player)

    def _announce_rent_opportunity(
        self,
        owner: MonopolyPlayer,
        tenant: MonopolyPlayer,
        space: BoardSpaceDefinition,
        rent: int,
    ) -> None:
        user = self.get_user(owner)
        if not user:
            return
        user.speak_l(
            (
                "monopoly-you-rent-opportunity-brief"
                if self._wants_brief(user)
                else "monopoly-you-rent-opportunity"
            ),
            buffer="game",
            tenant=tenant.name,
            property=self._space_name(user.locale, space),
            amount=self._money(user.locale, rent),
        )

    def _action_claim_rent(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        rent = self.rent_state
        if not rent or not self._is_actor(player, PHASE_RENT):
            return
        tenant = self.get_player_by_id(rent.tenant_id)
        space = self.board.space(rent.property_id)
        self.rent_state = None
        if not isinstance(tenant, MonopolyPlayer) or tenant.bankrupt:
            self._finish_landing()
            self._focus_after_user_transition(player)
            return
        self._start_debt(
            tenant,
            player.id,
            rent.amount,
            "monopoly-debt-rent",
            continuation="finish_landing",
            property_id=space.id,
        )
        self._focus_after_user_transition(player)

    def _action_waive_rent(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        rent = self.rent_state
        if not rent or not self._is_actor(player, PHASE_RENT):
            return
        tenant = self.get_player_by_id(rent.tenant_id)
        space = self.board.space(rent.property_id)
        self.rent_state = None
        self._broadcast_actor(
            player,
            "monopoly-you-waive-rent",
            "monopoly-player-waive-rent",
            tenant=tenant.name if tenant else "",
            property=lambda locale: self._space_name(locale, space),
            amount=lambda locale: self._money(locale, rent.amount),
            brief_personal_key="monopoly-you-waive-rent-brief",
            brief_others_key="monopoly-player-waive-rent-brief",
        )
        self._finish_landing()
        self._focus_after_user_transition(player)

    def _draw_card(self, player: MonopolyPlayer, deck_id: str) -> None:
        deck = self.chance_deck if deck_id == "chance" else self.community_deck
        if not deck:
            raise RuntimeError(f"Monopoly {deck_id} deck is unexpectedly empty")
        card_id = deck.pop(0)
        card = self.board.card(deck_id, card_id)
        if card.action != CARD_JAIL_FREE:
            deck.append(card_id)
        draw_sound = random.choice(game_audio.SOUND_CARD_DRAWS)  # nosec B311
        self.start_sequence(
            (
                f"monopoly_draw_card_{self.turn_number}_{deck_id}_"
                f"{card_id}_{self.sound_scheduler_tick}"
            ),
            [
                SequenceBeat.after_audio(
                    game_audio.sound_ticks(draw_sound),
                    ops=[SequenceOperation.sound_op(draw_sound)],
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "resolve_drawn_card",
                            {
                                "player_id": player.id,
                                "deck_id": deck_id,
                                "card_id": card_id,
                            },
                        )
                    ]
                ),
            ],
            tag="monopoly_card",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _announce_card(self, player: MonopolyPlayer, card: CardDefinition) -> None:
        self._broadcast_actor(
            player,
            "monopoly-you-draw-card",
            "monopoly-player-draw-card",
            suppress_brief=True,
            card=lambda locale: self._card_text(locale, card),
        )

    def _card_text(self, locale: str, card: CardDefinition) -> str:
        kwargs: dict[str, str] = {
            "go": self._space_name(locale, self.board.space(self.board.go_space_id)),
            "jail": self._space_name(
                locale, self.board.space(self.board.jail_space_id)
            ),
        }
        if card.amount:
            kwargs["amount"] = self._money(locale, card.amount)
        if card.destination_id:
            kwargs["destination"] = self._space_name(
                locale, self.board.space(card.destination_id)
            )
        if card.per_house:
            kwargs["perHouse"] = self._money(locale, card.per_house)
        if card.per_hotel:
            kwargs["perHotel"] = self._money(locale, card.per_hotel)
        if card.action == CARD_NEAREST and card.nearest_kind == SPACE_TRANSIT:
            kwargs["transit"] = Localization.get(
                locale, self.board.terminology.transit_kind_key
            )
        if card.action == CARD_NEAREST and card.nearest_kind == SPACE_UTILITY:
            kwargs["utility"] = Localization.get(
                locale, self.board.terminology.utility_kind_key
            )
        return Localization.get(locale, card.text_key, **kwargs)

    def _resolve_card(self, player: MonopolyPlayer, card: CardDefinition) -> None:
        if card.action == CARD_MOVE:
            self._move_to(player, card.destination_id, collect_go=card.collect_go)
            return
        if card.action == CARD_BACK:
            player.position = (player.position - card.amount) % len(self.board.spaces)
            self._announce_move(player, player.position, -card.amount)
            self._resolve_landing(player)
            return
        if card.action == CARD_NEAREST:
            destination = self._nearest_space_id(player.position, card.nearest_kind)
            self._move_to(
                player,
                destination,
                collect_go=True,
                rent_multiplier=card.rent_multiplier,
                utility_override=card.nearest_kind == SPACE_UTILITY,
            )
            return
        if card.action == CARD_COLLECT:
            player.cash += card.amount
            self._broadcast_actor(
                player,
                "monopoly-you-collect-bank",
                "monopoly-player-collect-bank",
                amount=lambda locale: self._money(locale, card.amount),
                cash=lambda locale: self._money(locale, player.cash),
                brief_personal_key="monopoly-you-collect-bank-brief",
                brief_others_key="monopoly-player-collect-bank-brief",
            )
            self.play_sound(
                random.choice(game_audio.SOUND_CASH_RECEIVED)  # nosec B311
            )
            self._finish_landing()
            return
        if card.action == CARD_PAY:
            self._start_debt(
                player,
                "",
                card.amount,
                "monopoly-debt-card",
                continuation="finish_landing",
            )
            return
        if card.action == CARD_COLLECT_EACH:
            payments = [
                QueuedPayment(
                    other.id, player.id, card.amount, "monopoly-debt-card-player"
                )
                for other in self.alive_players
                if other.id != player.id
            ]
            self._start_payment_batch(player, CARD_COLLECT_EACH, card.amount, payments)
            return
        if card.action == CARD_PAY_EACH:
            payments = [
                QueuedPayment(
                    player.id, other.id, card.amount, "monopoly-debt-card-player"
                )
                for other in self.alive_players
                if other.id != player.id
            ]
            self._start_payment_batch(player, CARD_PAY_EACH, card.amount, payments)
            return
        if card.action == CARD_REPAIRS:
            houses, hotels = self._owned_building_counts(player.id)
            amount = houses * card.per_house + hotels * card.per_hotel
            if amount <= 0:
                self._broadcast_actor(
                    player,
                    "monopoly-you-no-repair-cost",
                    "monopoly-player-no-repair-cost",
                    development=lambda locale: self._development_collective_text(
                        locale
                    ),
                    brief_personal_key="monopoly-you-no-repair-cost-brief",
                    brief_others_key="monopoly-player-no-repair-cost-brief",
                )
                self._finish_landing()
                return
            self.start_sequence(
                f"monopoly_repair_charge_{self.turn_number}",
                [
                    SequenceBeat.after_audio(
                        game_audio.sound_ticks(game_audio.SOUND_REPAIR_FEE),
                        ops=[SequenceOperation.sound_op(game_audio.SOUND_REPAIR_FEE)],
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "repair_card_charge",
                                {"player_id": player.id, "amount": amount},
                            )
                        ]
                    ),
                ],
                tag="monopoly_card",
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            return
        if card.action == CARD_JAIL_FREE:
            player.jail_card_ids.append(card.id)
            self._broadcast_actor(
                player,
                "monopoly-you-keep-jail-card",
                "monopoly-player-keeps-jail-card",
                brief_personal_key="monopoly-you-keep-jail-card-brief",
                brief_others_key="monopoly-player-keeps-jail-card-brief",
            )
            self._finish_landing()
            return
        if card.action == CARD_GO_TO_JAIL:
            self._send_to_jail(player)
            return
        self._finish_landing()

    def _nearest_space_id(self, position: int, kind: str) -> str:
        for offset in range(1, len(self.board.spaces) + 1):
            space = self.board.spaces[(position + offset) % len(self.board.spaces)]
            if space.kind == kind:
                return space.id
        raise ValueError(f"Board has no space of kind {kind}")

    # ------------------------------------------------------------------
    # Jail
    # ------------------------------------------------------------------

    def _send_to_jail(self, player: MonopolyPlayer) -> None:
        player.position = self.board.space_index(self.board.jail_space_id)
        player.in_jail = True
        player.jail_turns = 0
        self.extra_roll_pending = False
        self._broadcast_actor(
            player,
            "monopoly-you-go-jail",
            "monopoly-player-go-jail",
            jail=lambda locale: self._space_name(
                locale, self.board.space(self.board.jail_space_id)
            ),
            go=lambda locale: self._space_name(
                locale, self.board.space(self.board.go_space_id)
            ),
            brief_personal_key="monopoly-you-go-jail-brief",
            brief_others_key="monopoly-player-go-jail-brief",
        )
        self.play_sound(game_audio.SOUND_SENT_TO_JAIL)
        self._finish_turn()

    def _action_jail_pay(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_jail_pay_enabled(player):
            return
        player.cash -= self.board.jail_fine
        if self.options.free_parking_cash:
            self.free_parking_pot += self.board.jail_fine
        player.in_jail = False
        player.jail_turns = 0
        self._broadcast_actor(
            player,
            "monopoly-you-pay-jail",
            "monopoly-player-pays-jail",
            amount=lambda locale: self._money(locale, self.board.jail_fine),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-pay-jail-brief",
            brief_others_key="monopoly-player-pays-jail-brief",
        )
        self.phase = PHASE_AWAIT_ROLL
        self.decision_player_id = player.id
        self._play_jail_release_cues(include_payment=True)
        self.refresh_menus()
        self._focus_after_user_transition(player)

    def _action_jail_card(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_jail_card_enabled(player):
            return
        card_id = player.jail_card_ids.pop(0)
        deck_id = self.board.deck_id_for_card(card_id)
        deck = self.chance_deck if deck_id == "chance" else self.community_deck
        deck.append(card_id)
        player.in_jail = False
        player.jail_turns = 0
        self._broadcast_actor(
            player,
            "monopoly-you-use-jail-card",
            "monopoly-player-uses-jail-card",
            brief_personal_key="monopoly-you-use-jail-card-brief",
            brief_others_key="monopoly-player-uses-jail-card-brief",
        )
        self.phase = PHASE_AWAIT_ROLL
        self.decision_player_id = player.id
        self._play_jail_release_cues()
        self.refresh_menus()
        self._focus_after_user_transition(player)

    def _action_jail_roll(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_jail_roll_enabled(player):
            return
        die_1, die_2 = self._roll_pair()
        self._start_jail_roll_sequence(player, die_1, die_2)

    def _start_jail_roll_sequence(
        self,
        player: MonopolyPlayer,
        die_1: int,
        die_2: int,
    ) -> None:
        self.last_die_1 = die_1
        self.last_die_2 = die_2
        total = die_1 + die_2
        is_double = die_1 == die_2
        self._broadcast_actor(
            player,
            "monopoly-you-jail-roll",
            "monopoly-player-jail-roll",
            die1=die_1,
            die2=die_2,
            total=total,
            doubles="yes" if is_double else "no",
            brief_personal_key="monopoly-you-jail-roll-brief",
            brief_others_key="monopoly-player-jail-roll-brief",
        )
        beats = self._build_roll_cue_beats(player, die_1, die_2)
        beats.append(SequenceBeat.pause(game_audio.ROLL_TO_LANDING_PAUSE_TICKS))
        if is_double:
            beats.extend(
                [
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "jail_roll_release", {"player_id": player.id}
                            )
                        ]
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "jail_roll_move",
                                {"player_id": player.id, "spaces": total},
                            )
                        ],
                        delay_after_ticks=(
                            game_audio.sound_ticks(game_audio.SOUND_TOKEN_LANDED)
                            + game_audio.LANDING_TO_EVENT_PAUSE_TICKS
                        ),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "jail_roll_landing", {"player_id": player.id}
                            )
                        ]
                    ),
                ]
            )
        else:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "jail_roll_failed", {"player_id": player.id}
                        )
                    ]
                )
            )
        self.start_sequence(
            f"monopoly_jail_roll_{self.turn_number}",
            beats,
            tag="monopoly_roll",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _sequence_release_from_jail(self, payload: dict[str, Any]) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, MonopolyPlayer) or player.bankrupt:
            return
        player.in_jail = False
        player.jail_turns = 0
        self.extra_roll_pending = False
        self._broadcast_actor(
            player,
            "monopoly-you-leave-jail-doubles",
            "monopoly-player-leaves-jail-doubles",
            brief_personal_key="monopoly-you-leave-jail-doubles-brief",
            brief_others_key="monopoly-player-leaves-jail-doubles-brief",
        )
        self._play_jail_release_cues()

    def _play_jail_release_cues(self, *, include_payment: bool = False) -> None:
        """Start the shared release cues without blocking the next action."""

        if include_payment:
            self.play_sound(game_audio.SOUND_TAX_OR_FINE_PAID)
        self.play_sound(game_audio.SOUND_LEAVE_JAIL, max_instances=1)

    def _sequence_failed_jail_roll(self, payload: dict[str, Any]) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, MonopolyPlayer) or player.bankrupt:
            return
        player.jail_turns += 1
        if player.jail_turns < self.board.rules.failed_jail_rolls_before_fine:
            self._broadcast_actor(
                player,
                "monopoly-you-stay-jail",
                "monopoly-player-stays-jail",
                attempt=player.jail_turns,
                brief_personal_key="monopoly-you-stay-jail-brief",
                brief_others_key="monopoly-player-stays-jail-brief",
            )
            self._finish_turn()
            self._focus_after_user_transition(player)
            return
        player.in_jail = False
        player.jail_turns = 0
        self._start_debt(
            player,
            "",
            self.board.jail_fine,
            "monopoly-debt-jail",
            continuation="move_after_jail",
        )
        if self.phase == PHASE_DEBT:
            self._focus_after_user_transition(player)

    # ------------------------------------------------------------------
    # Auctions
    # ------------------------------------------------------------------

    def _start_auction(
        self,
        property_id: str,
        *,
        resume_kind: str,
        first_bidder_id: str = "",
    ) -> None:
        bidders = [
            player.id
            for player in self.alive_players
            if self._can_buy_properties(player)
        ]
        if not bidders:
            space = self.board.space(property_id)
            self.auction_state = None
            self._broadcast_global(
                "monopoly-auction-no-eligible-bidders",
                "monopoly-auction-no-eligible-bidders-brief",
                property=lambda locale: self._space_name(locale, space),
            )
            self._resume_after_auction(resume_kind)
            return
        if first_bidder_id not in bidders:
            first_bidder_id = bidders[0]
        self.auction_state = AuctionState(
            property_id=property_id,
            bidder_ids=bidders[:],
            active_bidder_ids=bidders[:],
            minimum_bid=self.board.rules.auction_opening_bid,
            resume_kind=resume_kind,
        )
        self.phase = PHASE_AUCTION
        self.decision_player_id = first_bidder_id
        space = self.board.space(property_id)
        self._broadcast_global(
            "monopoly-auction-started",
            "monopoly-auction-started-brief",
            property=lambda locale: self._space_name(locale, space),
            group=lambda locale: self._group_name(locale, space.group_id),
            minimum=lambda locale: self._money(
                locale, self.board.rules.auction_opening_bid
            ),
        )
        self.play_sound(game_audio.SOUND_AUCTION_STARTED)
        first_bidder = self._alive_player_by_id(first_bidder_id)
        if first_bidder:
            self._announce_auction_turn(first_bidder)
        self.refresh_menus()

    def _announce_auction_turn(self, bidder: MonopolyPlayer) -> None:
        auction = self.auction_state
        if not auction:
            return
        space = self.board.space(auction.property_id)
        self._broadcast_actor(
            bidder,
            "monopoly-your-auction-turn",
            "monopoly-player-auction-turn",
            brief_personal_key="monopoly-your-auction-turn-brief",
            brief_others_key="monopoly-player-auction-turn-brief",
            property=lambda locale: self._space_name(locale, space),
            minimum=lambda locale: self._money(
                locale,
                self._auction_minimum_bid(),
            ),
        )

    def _action_bid_minimum(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_bid_enabled(player):
            return
        if self._place_bid(player, self._auction_minimum_bid()):
            self._focus_after_auction_action(player, "bid_minimum")

    def _action_place_bid(
        self,
        player: MonopolyPlayer,
        input_value: str,
        action_id: str,
    ) -> None:
        del action_id
        auction = self.auction_state
        if not auction or not self._is_actor(player, PHASE_AUCTION):
            return
        try:
            amount = int(input_value.strip())
        except ValueError:
            self._speak(player, "monopoly-error-bid-number")
            return
        if self._place_bid(player, amount):
            self._focus_after_auction_action(player, "place_bid")

    def _place_bid(self, player: MonopolyPlayer, amount: int) -> bool:
        auction = self.auction_state
        if not auction or not self._is_actor(player, PHASE_AUCTION):
            return False
        minimum = self._auction_minimum_bid()
        if amount < minimum:
            self._speak(
                player,
                "monopoly-error-bid-too-low",
                minimum=self._money(self._locale(player), minimum),
            )
            return False
        if amount > player.cash:
            self._speak(
                player,
                "monopoly-error-bid-needs-cash",
                minimum=self._money(self._locale(player), amount),
                cash=self._money(self._locale(player), player.cash),
            )
            return False
        auction.highest_bid = amount
        auction.highest_bidder_id = player.id
        self._broadcast_actor(
            player,
            "monopoly-you-bid",
            "monopoly-player-bids",
            amount=lambda locale: self._money(locale, amount),
            brief_personal_key="monopoly-you-bid-brief",
            brief_others_key="monopoly-player-bids-brief",
        )
        self.play_sound(
            game_audio.SOUND_AUCTION_BID,
            max_instances=1,
        )
        self._advance_auction(player.id)
        return True

    def _action_pass_auction(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        auction = self.auction_state
        if not auction or not self._is_actor(player, PHASE_AUCTION):
            return
        if player.id == auction.highest_bidder_id:
            self._speak(player, "monopoly-error-leading-bid-cannot-pass")
            return
        if player.id in auction.active_bidder_ids:
            auction.active_bidder_ids.remove(player.id)
        self._broadcast_actor(
            player,
            "monopoly-you-pass-auction",
            "monopoly-player-passes-auction",
            brief_personal_key="monopoly-you-pass-auction-brief",
            brief_others_key="monopoly-player-passes-auction-brief",
        )
        self._advance_auction(player.id)
        self._focus_after_auction_action(player, "pass_auction")

    def _focus_after_auction_action(
        self,
        player: MonopolyPlayer,
        action_id: str,
    ) -> None:
        """Keep an explicit bidder action anchored without moving anyone else."""

        if player.is_bot:
            return
        auction = self.auction_state
        focus_id = (
            action_id
            if auction and player.id in auction.active_bidder_ids
            else "roll_dice"
        )
        self.request_menu_focus(player, focus_id)

    def _advance_auction(self, previous_bidder_id: str) -> None:
        auction = self.auction_state
        if not auction:
            return
        active = [
            player_id
            for player_id in auction.active_bidder_ids
            if self._alive_player_by_id(player_id) is not None
        ]
        auction.active_bidder_ids = active
        if not active:
            self._finish_auction()
            return
        if auction.highest_bidder_id and active == [auction.highest_bidder_id]:
            self._finish_auction()
            return
        ordered = auction.bidder_ids
        try:
            start = ordered.index(previous_bidder_id)
        except ValueError:
            start = -1
        for offset in range(1, len(ordered) + 1):
            candidate = ordered[(start + offset) % len(ordered)]
            if candidate in active and candidate != auction.highest_bidder_id:
                self.decision_player_id = candidate
                next_bidder = self._alive_player_by_id(candidate)
                if next_bidder:
                    self._announce_auction_turn(next_bidder)
                self.refresh_menus()
                return
        self._finish_auction()

    def _finish_auction(self) -> None:
        auction = self.auction_state
        if not auction:
            return
        property_id = auction.property_id
        resume_kind = auction.resume_kind
        space = self.board.space(property_id)
        winner = self._alive_player_by_id(auction.highest_bidder_id)
        if winner and auction.highest_bid > 0 and winner.cash >= auction.highest_bid:
            winner.cash -= auction.highest_bid
            state = self.property_states[property_id]
            state.owner_id = winner.id
            state.mortgaged = False
            state.buildings = 0
            self._broadcast_actor(
                winner,
                "monopoly-you-win-auction",
                "monopoly-player-wins-auction",
                property=lambda locale: self._space_name(locale, space),
                group=lambda locale: self._group_name(locale, space.group_id),
                amount=lambda locale: self._money(locale, auction.highest_bid),
                cash=lambda locale: self._money(locale, winner.cash),
                brief_personal_key="monopoly-you-win-auction-brief",
                brief_others_key="monopoly-player-wins-auction-brief",
            )
            self.play_sound(game_audio.SOUND_AUCTION_SOLD)
            self._announce_completed_groups(winner, [property_id])
        else:
            self._broadcast_global(
                "monopoly-auction-no-sale",
                "monopoly-auction-no-sale-brief",
                property=lambda locale: self._space_name(locale, space),
            )
        self.auction_state = None
        self._resume_after_auction(resume_kind)

    def _resume_after_auction(self, resume_kind: str) -> None:
        if resume_kind == "bankruptcy":
            self._continue_bankruptcy_auctions()
        else:
            self._finish_landing()

    # ------------------------------------------------------------------
    # Debt, liquidation, and bankruptcy
    # ------------------------------------------------------------------

    def _start_debt(
        self,
        debtor: MonopolyPlayer,
        creditor_id: str,
        amount: int,
        reason_key: str,
        *,
        continuation: str,
        property_id: str = "",
    ) -> None:
        if amount <= 0:
            self._continue_after_debt(continuation)
            return
        debt = DebtState(
            debtor_id=debtor.id,
            creditor_id=creditor_id,
            amount=amount,
            reason_key=reason_key,
            continuation=continuation,
            property_id=property_id,
        )
        if debtor.cash >= amount:
            self.debt_state = debt
            self._complete_debt_payment(debtor)
            return
        self.debt_state = debt
        self.phase = PHASE_DEBT
        self.decision_player_id = debtor.id
        creditor = self.get_player_by_id(creditor_id) if creditor_id else None
        self._announce_debt(debtor, creditor, debt)
        self.play_sound(game_audio.SOUND_DEBT_WARNING)
        self.refresh_menus()

    def _announce_debt(
        self,
        debtor: MonopolyPlayer,
        creditor: Player | None,
        debt: DebtState,
    ) -> None:
        self._broadcast_actor(
            debtor,
            "monopoly-you-owe",
            "monopoly-player-owes",
            creditor=creditor.name if creditor else "",
            destination="player" if creditor else "bank",
            amount=lambda locale: self._money(locale, debt.amount),
            cash=lambda locale: self._money(locale, debtor.cash),
            reason=lambda locale: Localization.get(locale, debt.reason_key),
            brief_personal_key="monopoly-you-owe-brief",
            brief_others_key="monopoly-player-owes-brief",
        )

    def _action_pay_debt(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_pay_debt_enabled(player):
            return
        self._complete_debt_payment(player)
        self._focus_after_user_transition(player)

    def _complete_debt_payment(self, debtor: MonopolyPlayer) -> None:
        debt = self.debt_state
        if not debt or debt.debtor_id != debtor.id or debtor.cash < debt.amount:
            return
        debtor.cash -= debt.amount
        creditor = self._alive_player_by_id(debt.creditor_id)
        if creditor:
            creditor.cash += debt.amount
        elif self._payment_funds_free_parking(debt.reason_key):
            self.free_parking_pot += debt.amount
        continuation = debt.continuation
        amount = debt.amount
        reason_key = debt.reason_key
        property_id = debt.property_id
        self.debt_state = None
        if continuation == "payment_batch" and self.payment_batch_state:
            self.payment_batch_state.completed_count += 1
            self.payment_batch_state.completed_total += amount
            self._continue_after_debt(continuation)
            return
        if (
            reason_key == "monopoly-debt-rent"
            and creditor
            and property_id in self.property_states
        ):
            self._announce_rent_payment(
                creditor,
                debtor,
                self.board.space(property_id),
                amount,
            )
        else:
            self._broadcast_actor(
                debtor,
                "monopoly-you-pay-debt",
                "monopoly-player-pays-debt",
                creditor=creditor.name if creditor else "",
                destination="player" if creditor else "bank",
                amount=lambda locale: self._money(locale, amount),
                cash=lambda locale: self._money(locale, debtor.cash),
                reason=lambda locale: Localization.get(locale, reason_key),
                brief_personal_key="monopoly-you-pay-debt-brief",
                brief_others_key="monopoly-player-pays-debt-brief",
            )
        if continuation == "move_after_jail" and reason_key == "monopoly-debt-jail":
            self._play_jail_release_cues(include_payment=True)
            self._continue_after_debt(continuation)
            return
        if creditor:
            self.play_sound(game_audio.SOUND_RENT_PAID)
        elif reason_key != "monopoly-debt-repairs":
            self.play_sound(game_audio.SOUND_TAX_OR_FINE_PAID)
        self._continue_after_debt(continuation)

    def _announce_rent_payment(
        self,
        owner: MonopolyPlayer,
        tenant: MonopolyPlayer,
        space: BoardSpaceDefinition,
        amount: int,
    ) -> None:
        self._broadcast_actor_target(
            owner,
            tenant,
            "monopoly-you-collect-rent",
            "monopoly-you-pay-rent",
            "monopoly-player-pays-rent",
            brief_personal_key="monopoly-you-collect-rent-brief",
            brief_target_key="monopoly-you-pay-rent-brief",
            brief_others_key="monopoly-player-pays-rent-brief",
            owner=owner.name,
            tenant=tenant.name,
            property=lambda locale: self._space_name(locale, space),
            amount=lambda locale: self._money(locale, amount),
            owner_cash=lambda locale: self._money(locale, owner.cash),
            tenant_cash=lambda locale: self._money(locale, tenant.cash),
        )

    def _payment_funds_free_parking(self, reason_key: str) -> bool:
        return self.options.free_parking_cash and reason_key in {
            "monopoly-debt-tax",
            "monopoly-debt-card",
            "monopoly-debt-repairs",
            "monopoly-debt-jail",
        }

    def _action_raise_cash(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        debt = self.debt_state
        if not debt or not self._is_actor(player, PHASE_DEBT):
            return
        raised_before = player.cash
        while player.cash < debt.amount:
            sale = self._best_building_sale(player.id)
            if sale:
                self._apply_sell_building(player, sale, announce=False)
                continue
            group_id = self._best_building_group_sale(player.id)
            if not group_id:
                break
            self._apply_sell_group_buildings(player, group_id, announce=False)
        while player.cash < debt.amount:
            mortgage_id = self._best_mortgage(player.id)
            if not mortgage_id:
                break
            self._apply_mortgage(player, mortgage_id, announce=False)
        self._broadcast_actor(
            player,
            "monopoly-you-raise-cash",
            "monopoly-player-raises-cash",
            development=lambda locale: self._development_collective_text(locale),
            amount=lambda locale: self._money(locale, player.cash - raised_before),
            cash=lambda locale: self._money(locale, player.cash),
            debt=lambda locale: self._money(locale, debt.amount),
            brief_personal_key="monopoly-you-raise-cash-brief",
            brief_others_key="monopoly-player-raises-cash-brief",
        )
        self.refresh_menus()

    def _best_building_sale(self, owner_id: str) -> str:
        candidates: list[tuple[int, str]] = []
        owner = self._alive_player_by_id(owner_id)
        if not owner:
            return ""
        for property_id, state in self.property_states.items():
            if state.owner_id != owner_id or not state.buildings:
                continue
            if (
                can_sell_building(
                    self.board,
                    self.property_states,
                    property_id,
                    owner_id,
                    self.bank_houses,
                )
                is None
            ):
                candidates.append(
                    (
                        building_sale_damage(
                            self.board,
                            self.property_states,
                            property_id,
                        ),
                        property_id,
                    )
                )
        return min(candidates, default=(0, ""))[1]

    def _best_building_group_sale(self, owner_id: str) -> str:
        candidates: list[tuple[int, str]] = []
        seen_groups: set[str] = set()
        for property_id, state in self.property_states.items():
            if state.owner_id != owner_id or not state.buildings:
                continue
            space = self.board.space(property_id)
            if space.kind != SPACE_STREET or space.group_id in seen_groups:
                continue
            seen_groups.add(space.group_id)
            candidates.append(
                (
                    group_building_sale_damage(
                        self.board,
                        self.property_states,
                        space.group_id,
                    ),
                    space.group_id,
                )
            )
        return min(candidates, default=(0, ""))[1]

    def _best_mortgage(self, owner_id: str) -> str:
        candidates: list[tuple[int, str]] = []
        for property_id, state in self.property_states.items():
            if state.owner_id != owner_id:
                continue
            if (
                can_mortgage(
                    self.board,
                    self.property_states,
                    property_id,
                    owner_id,
                )
                is None
            ):
                candidates.append(
                    (
                        mortgage_damage(
                            self.board,
                            self.property_states,
                            property_id,
                        ),
                        property_id,
                    )
                )
        return min(candidates, default=(0, ""))[1]

    def _action_declare_bankruptcy(
        self, player: MonopolyPlayer, action_id: str
    ) -> None:
        del action_id
        if self._is_bankruptcy_enabled(player):
            return
        debt = self.debt_state
        if not debt:
            return
        creditor = self._alive_player_by_id(debt.creditor_id)
        continuation = debt.continuation
        batch = self.payment_batch_state
        if (
            continuation == "payment_batch"
            and batch
            and batch.actor_id == player.id
        ):
            self._finish_payment_batch()
        self._broadcast_actor(
            player,
            "monopoly-you-bankrupt",
            "monopoly-player-bankrupt",
            creditor=creditor.name if creditor else "",
            destination="player" if creditor else "bank",
            amount=lambda locale: self._money(locale, debt.amount),
            brief_personal_key="monopoly-you-bankrupt-brief",
            brief_others_key="monopoly-player-bankrupt-brief",
        )
        self.play_sound(game_audio.SOUND_BANKRUPTCY_DECLARED)
        if creditor:
            self._bankrupt_to_player(player, creditor, continuation)
        else:
            self._bankrupt_to_bank(player, continuation)
        self._focus_after_user_transition(player)

    def _bankrupt_to_player(
        self,
        debtor: MonopolyPlayer,
        creditor: MonopolyPlayer,
        continuation: str,
    ) -> None:
        property_ids = self._owned_property_ids(debtor.id)
        for property_id in property_ids:
            state = self.property_states[property_id]
            space = self.board.space(property_id)
            if state.buildings:
                self._return_buildings_to_bank(state)
                debtor.cash += state.buildings * self._building_sale_value(space)
                state.buildings = 0
        creditor.cash += debtor.cash
        debtor.cash = 0
        mortgaged_property_ids: list[str] = []
        for property_id in property_ids:
            state = self.property_states[property_id]
            state.owner_id = creditor.id
            if state.mortgaged:
                mortgaged_property_ids.append(property_id)
        self._announce_completed_groups(creditor, property_ids)
        creditor.jail_card_ids.extend(debtor.jail_card_ids)
        debtor.jail_card_ids.clear()
        was_current = self.current_player is debtor
        self.debt_state = None
        self._eliminate_player(debtor)
        if self._check_for_winner():
            return
        self._start_mortgage_transfers(
            mortgaged_property_ids,
            resume_kind="bankruptcy",
            resume_continuation=continuation,
            resume_was_current=was_current,
        )

    def _bankrupt_to_bank(self, debtor: MonopolyPlayer, continuation: str) -> None:
        property_ids = self._owned_property_ids(debtor.id)
        for property_id in property_ids:
            state = self.property_states[property_id]
            self._return_buildings_to_bank(state)
            state.owner_id = ""
            state.mortgaged = False
            state.buildings = 0
        self._return_jail_cards(debtor)
        debtor.cash = 0
        was_current = self.current_player is debtor
        self.debt_state = None
        self._eliminate_player(debtor)
        if self._check_for_winner():
            return
        self.bankruptcy_state = BankruptcyState(
            was_current_player=was_current,
            resume_continuation=continuation,
            property_auction_ids=property_ids,
        )
        self._continue_bankruptcy_auctions()

    def _continue_bankruptcy_auctions(self) -> None:
        state = self.bankruptcy_state
        if not state:
            self._resume_after_bankruptcy()
            return
        while state.property_auction_ids:
            property_id = state.property_auction_ids.pop(0)
            if self.property_states[property_id].owner_id:
                continue
            self._start_auction(property_id, resume_kind="bankruptcy")
            return
        self._resume_after_bankruptcy()

    def _resume_after_bankruptcy(self) -> None:
        state = self.bankruptcy_state
        if not state:
            self._finish_landing()
            return
        continuation = state.resume_continuation
        was_current = state.was_current_player
        self.bankruptcy_state = None
        self._finish_bankruptcy_resume(continuation, was_current)

    def _finish_bankruptcy_resume(self, continuation: str, was_current: bool) -> None:
        if was_current:
            if continuation == "payment_batch":
                self._finish_payment_batch()
            if continuation == "mortgage_transfer":
                self._complete_current_mortgage_transfer()
                return
            self._start_turn(announce=True)
            return
        self._continue_after_debt(continuation)

    def _eliminate_player(self, player: MonopolyPlayer) -> None:
        player.bankrupt = True
        self.bankruptcy_counter += 1
        player.bankruptcy_order = self.bankruptcy_counter
        player.in_jail = False
        if player.id in self.turn_player_ids:
            removed_index = self.turn_player_ids.index(player.id)
            self.turn_player_ids.remove(player.id)
            if self.turn_player_ids:
                if removed_index < self.turn_index:
                    self.turn_index -= 1
                self.turn_index %= len(self.turn_player_ids)
            else:
                self.turn_index = 0
        self.refresh_menus()

    def _continue_after_debt(self, continuation: str) -> None:
        if continuation == "move_after_jail":
            current = self.current_player
            if isinstance(current, MonopolyPlayer):
                self.extra_roll_pending = False
                self._start_post_jail_move_sequence(
                    current, self.last_die_1 + self.last_die_2
                )
            return
        if continuation == "payment_batch":
            self._process_payment_batch()
            return
        if continuation == "resume_after_bankruptcy":
            self._resume_after_bankruptcy()
            return
        if continuation == "mortgage_transfer":
            self._complete_current_mortgage_transfer()
            return
        self._finish_landing()

    def _start_post_jail_move_sequence(
        self, player: MonopolyPlayer, spaces: int
    ) -> None:
        self.start_sequence(
            f"monopoly_post_jail_move_{self.turn_number}",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "jail_roll_move",
                            {"player_id": player.id, "spaces": spaces},
                        )
                    ],
                    delay_after_ticks=(
                        game_audio.sound_ticks(game_audio.SOUND_TOKEN_LANDED)
                        + game_audio.LANDING_TO_EVENT_PAUSE_TICKS
                    ),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "jail_roll_landing", {"player_id": player.id}
                        )
                    ]
                ),
            ],
            tag="monopoly_roll",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _start_payment_batch(
        self,
        actor: MonopolyPlayer,
        kind: str,
        amount_each: int,
        payments: list[QueuedPayment],
    ) -> None:
        self.payment_batch_state = PaymentBatchState(
            actor_id=actor.id,
            kind=kind,
            amount_each=amount_each,
            payments=payments,
        )
        self._process_payment_batch()

    def _process_payment_batch(self) -> None:
        batch = self.payment_batch_state
        if not batch:
            self._finish_landing()
            return
        while batch.payments:
            payment = batch.payments.pop(0)
            payer = self._alive_player_by_id(payment.payer_id)
            payee = self._alive_player_by_id(payment.payee_id)
            if not payer or not payee:
                continue
            self._start_debt(
                payer,
                payee.id,
                payment.amount,
                payment.reason_key,
                continuation="payment_batch",
            )
            return
        self._finish_payment_batch()
        self._finish_landing()

    def _finish_payment_batch(self) -> None:
        batch = self.payment_batch_state
        self.payment_batch_state = None
        if not batch or batch.completed_count <= 0:
            return
        actor = self.get_player_by_id(batch.actor_id)
        if not isinstance(actor, MonopolyPlayer):
            return
        if batch.kind == CARD_COLLECT_EACH:
            personal_key = "monopoly-you-collect-player-batch"
            public_key = "monopoly-player-collects-player-batch"
            brief_personal_key = "monopoly-you-collect-player-batch-brief"
            brief_others_key = "monopoly-player-collects-player-batch-brief"
        else:
            personal_key = "monopoly-you-pay-player-batch"
            public_key = "monopoly-player-pays-player-batch"
            brief_personal_key = "monopoly-you-pay-player-batch-brief"
            brief_others_key = "monopoly-player-pays-player-batch-brief"
        self._broadcast_actor(
            actor,
            personal_key,
            public_key,
            amount=lambda locale: self._money(locale, batch.amount_each),
            count=batch.completed_count,
            total=lambda locale: self._money(locale, batch.completed_total),
            cash=lambda locale: self._money(locale, actor.cash),
            brief_personal_key=brief_personal_key,
            brief_others_key=brief_others_key,
        )
        self.play_sound(game_audio.SOUND_RENT_PAID, max_instances=1)

    # ------------------------------------------------------------------
    # Mortgaged-property transfer choices
    # ------------------------------------------------------------------

    def _start_mortgage_transfers(
        self,
        property_ids: list[str],
        *,
        resume_kind: str,
        resume_phase: str = "",
        resume_decision_player_id: str = "",
        resume_continuation: str = "finish_landing",
        resume_was_current: bool = False,
    ) -> None:
        self.mortgage_transfer_state = MortgageTransferState(
            property_ids=list(dict.fromkeys(property_ids)),
            resume_kind=resume_kind,
            resume_phase=resume_phase,
            resume_decision_player_id=resume_decision_player_id,
            resume_continuation=resume_continuation,
            resume_was_current=resume_was_current,
        )
        self._advance_mortgage_transfers()

    def _advance_mortgage_transfers(self) -> None:
        transfer = self.mortgage_transfer_state
        if not transfer:
            return
        while transfer.property_ids:
            property_id = transfer.property_ids[0]
            state = self.property_states.get(property_id)
            owner = self._alive_player_by_id(state.owner_id) if state else None
            if not state or not state.mortgaged or not owner:
                transfer.property_ids.pop(0)
                continue
            self.phase = PHASE_MORTGAGE_TRANSFER
            self.decision_player_id = owner.id
            space = self.board.space(property_id)
            interest = transfer_mortgage_interest(
                space.mortgage_value,
                self.board.rules.mortgage_interest_percent,
            )
            unmortgage = unmortgage_cost(
                space.mortgage_value,
                self.board.rules.mortgage_interest_percent,
            )
            self._broadcast_actor(
                owner,
                "monopoly-you-receive-mortgaged",
                "monopoly-player-receives-mortgaged",
                property=lambda locale, space=space: self._space_name(locale, space),
                interest=lambda locale, interest=interest: self._money(
                    locale, interest
                ),
                unmortgage=lambda locale, unmortgage=unmortgage: self._money(
                    locale, unmortgage
                ),
                brief_personal_key="monopoly-you-receive-mortgaged-brief",
                brief_others_key="monopoly-player-receives-mortgaged-brief",
            )
            self.refresh_menus()
            return
        self._finish_mortgage_transfers()

    def _action_keep_received_mortgaged(
        self, player: MonopolyPlayer, action_id: str
    ) -> None:
        del action_id
        context = self._current_mortgage_transfer(player)
        if not context:
            return
        space, _ = context
        interest = transfer_mortgage_interest(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        if player.cash < interest:
            self._start_debt(
                player,
                "",
                interest,
                "monopoly-debt-transfer-interest",
                continuation="mortgage_transfer",
            )
            self._focus_after_user_transition(player)
            return
        player.cash -= interest
        self._broadcast_actor(
            player,
            "monopoly-you-keep-received-mortgaged",
            "monopoly-player-keeps-received-mortgaged",
            property=lambda locale: self._space_name(locale, space),
            interest=lambda locale: self._money(locale, interest),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-keep-received-mortgaged-brief",
            brief_others_key="monopoly-player-keeps-received-mortgaged-brief",
        )
        self._complete_current_mortgage_transfer()
        self._focus_after_user_transition(player)

    def _action_unmortgage_received_now(
        self, player: MonopolyPlayer, action_id: str
    ) -> None:
        del action_id
        if self._is_unmortgage_received_now_enabled(player):
            return
        context = self._current_mortgage_transfer(player)
        if not context:
            return
        space, state = context
        cost = unmortgage_cost(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        player.cash -= cost
        state.mortgaged = False
        self._broadcast_actor(
            player,
            "monopoly-you-unmortgage-received-now",
            "monopoly-player-unmortgages-received-now",
            property=lambda locale: self._space_name(locale, space),
            cost=lambda locale: self._money(locale, cost),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-unmortgage-received-now-brief",
            brief_others_key="monopoly-player-unmortgages-received-now-brief",
        )
        self.play_sound(game_audio.SOUND_PROPERTY_UNMORTGAGED)
        self._complete_current_mortgage_transfer()
        self._focus_after_user_transition(player)

    def _complete_current_mortgage_transfer(self) -> None:
        transfer = self.mortgage_transfer_state
        if transfer and transfer.property_ids:
            transfer.property_ids.pop(0)
        self._advance_mortgage_transfers()

    def _finish_mortgage_transfers(self) -> None:
        transfer = self.mortgage_transfer_state
        if not transfer:
            return
        self.mortgage_transfer_state = None
        if transfer.resume_kind == "bankruptcy":
            self._finish_bankruptcy_resume(
                transfer.resume_continuation, transfer.resume_was_current
            )
            return
        if transfer.resume_decision_player_id and not self._alive_player_by_id(
            transfer.resume_decision_player_id
        ):
            self._start_turn(announce=True)
            return
        self._restore_interrupted_phase(
            transfer.resume_phase, transfer.resume_decision_player_id
        )

    # ------------------------------------------------------------------
    # Property management
    # ------------------------------------------------------------------

    def _manage_property_options(self, player: Player) -> list[str]:
        if not isinstance(player, MonopolyPlayer):
            return []
        return [
            space.id
            for space in self.board.spaces
            if space.id in self.property_states
            and self.property_states[space.id].owner_id == player.id
        ]

    def _build_property_error(
        self, player: MonopolyPlayer, property_id: str
    ) -> str | tuple[str, dict] | None:
        state = self.property_states.get(property_id)
        if not state or state.owner_id != player.id:
            return "monopoly-error-not-your-property"
        space = self.board.space(property_id)
        error = can_build(
            self.board,
            self.property_states,
            property_id,
            player.id,
            self.bank_houses,
            self.bank_hotels,
        )
        if error:
            return self._development_error_key(error)
        if player.cash < space.building_cost:
            locale = self._locale(player)
            return (
                "monopoly-error-building-needs-cash",
                {
                    "cost": self._money(locale, space.building_cost),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _sell_property_error(
        self, player: MonopolyPlayer, property_id: str
    ) -> str | None:
        error = can_sell_building(
            self.board,
            self.property_states,
            property_id,
            player.id,
            self.bank_houses,
        )
        return self._development_error_key(error) if error else None

    def _mortgage_property_error(
        self, player: MonopolyPlayer, property_id: str
    ) -> str | None:
        error = can_mortgage(
            self.board,
            self.property_states,
            property_id,
            player.id,
        )
        return self._development_error_key(error) if error else None

    def _unmortgage_property_error(
        self, player: MonopolyPlayer, property_id: str
    ) -> str | tuple[str, dict] | None:
        state = self.property_states.get(property_id)
        if not state or state.owner_id != player.id:
            return "monopoly-error-not-your-property"
        if not state.mortgaged:
            return "monopoly-error-not-mortgaged"
        space = self.board.space(property_id)
        cost = unmortgage_cost(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        if player.cash < cost:
            locale = self._locale(player)
            return (
                "monopoly-error-unmortgage-needs-cash",
                {
                    "cost": self._money(locale, cost),
                    "cash": self._money(locale, player.cash),
                },
            )
        return None

    def _build_property_options(self, player: Player) -> list[str]:
        if not isinstance(player, MonopolyPlayer):
            return []
        return [
            property_id
            for property_id in self._manage_property_options(player)
            if self._build_property_error(player, property_id) is None
        ]

    def _sell_property_options(self, player: Player) -> list[str]:
        if not isinstance(player, MonopolyPlayer):
            return []
        options = [
            property_id
            for property_id in self._manage_property_options(player)
            if self._sell_property_error(player, property_id) is None
        ]
        for group in self.board.property_groups:
            spaces = self.board.group_spaces(group.id)
            if (
                not spaces
                or spaces[0].kind != SPACE_STREET
                or not all(
                    self.property_states[space.id].owner_id == player.id
                    for space in spaces
                )
                or not any(self.property_states[space.id].buildings for space in spaces)
                or any(space.id in options for space in spaces)
            ):
                continue
            options.append(f"{SELL_GROUP_OPTION_PREFIX}{group.id}")
        return options

    def _mortgage_property_options(self, player: Player) -> list[str]:
        if not isinstance(player, MonopolyPlayer):
            return []
        return [
            property_id
            for property_id in self._manage_property_options(player)
            if self._mortgage_property_error(player, property_id) is None
        ]

    def _unmortgage_property_options(self, player: Player) -> list[str]:
        if not isinstance(player, MonopolyPlayer):
            return []
        return [
            property_id
            for property_id in self._manage_property_options(player)
            if self._unmortgage_property_error(player, property_id) is None
        ]

    def _management_selector_options(self, player: Player, action_id: str) -> list[str]:
        builders = {
            "choose_build_property": self._build_property_options,
            "choose_sell_property": self._sell_property_options,
            "choose_mortgage_property": self._mortgage_property_options,
            "choose_unmortgage_property": self._unmortgage_property_options,
        }
        builder = builders.get(action_id)
        return builder(player) if builder else []

    def _management_selector_empty_reason(
        self, player: MonopolyPlayer, action_id: str
    ) -> str | tuple[str, dict]:
        if action_id == "choose_build_property":
            return self._build_selector_empty_reason(player)
        if action_id == "choose_sell_property":
            return self._development_error_key(
                "monopoly-error-no-sellable-buildings"
            )
        if action_id == "choose_mortgage_property":
            owned = [
                property_id
                for property_id in self._manage_property_options(player)
                if property_id in self.property_states
            ]
            if not owned:
                return "monopoly-error-no-properties"
            if not any(
                not self.property_states[property_id].mortgaged
                for property_id in owned
            ):
                return "monopoly-error-no-unmortgaged-properties"
            return self._development_error_key(
                "monopoly-error-no-mortgageable-properties"
            )
        if action_id == "choose_unmortgage_property":
            mortgaged = [
                self.board.space(property_id)
                for property_id in self._manage_property_options(player)
                if self.property_states[property_id].mortgaged
            ]
            if not mortgaged:
                return "monopoly-error-no-mortgaged-properties"
            cheapest = min(
                unmortgage_cost(
                    space.mortgage_value,
                    self.board.rules.mortgage_interest_percent,
                )
                for space in mortgaged
            )
            locale = self._locale(player)
            return (
                "monopoly-error-unmortgage-none-needs-cash",
                {
                    "cost": self._money(locale, cheapest),
                    "cash": self._money(locale, player.cash),
                },
            )
        return "monopoly-error-no-properties"

    def _build_selector_empty_reason(
        self, player: MonopolyPlayer
    ) -> str | tuple[str, dict]:
        owned_streets = [
            space
            for space in self.board.spaces
            if space.kind == SPACE_STREET
            and self.property_states[space.id].owner_id == player.id
        ]
        if not owned_streets:
            return self._development_error_key(
                "monopoly-error-build-none-no-streets"
            )

        complete_group_ids = {
            space.group_id
            for space in owned_streets
            if owns_group(
                self.board,
                self.property_states,
                player.id,
                space.group_id,
            )
        }
        if not complete_group_ids:
            return self._development_error_key(
                "monopoly-error-build-none-no-color-set"
            )

        available_group_ids = {
            group_id
            for group_id in complete_group_ids
            if not any(
                self.property_states[space.id].mortgaged
                for space in self.board.group_spaces(group_id)
            )
        }
        if not available_group_ids:
            return self._development_error_key(
                "monopoly-error-build-none-groups-mortgaged"
            )

        candidates = [
            space
            for group_id in available_group_ids
            for space in self.board.group_spaces(group_id)
        ]
        if all(self.property_states[space.id].buildings >= 5 for space in candidates):
            key = (
                "monopoly-error-build-none-developed-or-mortgaged"
                if available_group_ids != complete_group_ids
                else "monopoly-error-build-none-fully-developed"
            )
            return self._development_error_key(key)

        structurally_eligible = [
            space
            for space in candidates
            if can_build(
                self.board,
                self.property_states,
                space.id,
                player.id,
                max(self.bank_houses, 4),
                max(self.bank_hotels, 1),
            )
            is None
        ]
        bank_errors = {
            space.id: can_build(
                self.board,
                self.property_states,
                space.id,
                player.id,
                self.bank_houses,
                self.bank_hotels,
            )
            for space in structurally_eligible
        }
        bank_eligible = [
            space for space in structurally_eligible if bank_errors[space.id] is None
        ]
        if not bank_eligible:
            shortages = set(bank_errors.values())
            if shortages == {"monopoly-error-no-houses"}:
                return "monopoly-error-no-houses"
            if shortages == {"monopoly-error-no-hotels"}:
                return "monopoly-error-no-hotels"
            return "monopoly-error-no-development-pieces"

        cheapest = min(space.building_cost for space in bank_eligible)
        locale = self._locale(player)
        return (
            self._development_error_key("monopoly-error-build-none-needs-cash"),
            {
                "cost": self._money(locale, cheapest),
                "cash": self._money(locale, player.cash),
            },
        )

    def _other_managed_property_options(self, player: Player) -> list[str]:
        return [
            property_id
            for property_id in self._manage_property_options(player)
            if property_id != self.management_property_id
        ]

    def _manage_property_option_label(self, player: Player, value: str) -> str:
        locale = self._locale(player)
        if value not in self.property_states:
            return value
        space = self.board.space(value)
        state = self.property_states[value]
        return Localization.get(
            locale,
            "monopoly-property-option",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            status=self._property_state_text(locale, state, space),
        )

    def _build_property_option_label(self, player: Player, value: str) -> str:
        if value not in self.property_states:
            return value
        locale = self._locale(player)
        space = self.board.space(value)
        state = self.property_states[value]
        return Localization.get(
            locale,
            "monopoly-build-property-option",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            building=self._development_level_text(locale, state.buildings + 1),
            cost=self._money(locale, space.building_cost),
            current=self._building_text(locale, state.buildings),
            cash=self._money(locale, getattr(player, "cash", 0)),
        )

    def _sell_property_option_label(self, player: Player, value: str) -> str:
        locale = self._locale(player)
        if value.startswith(SELL_GROUP_OPTION_PREFIX):
            group_id = value.removeprefix(SELL_GROUP_OPTION_PREFIX)
            return Localization.get(
                locale,
                "monopoly-sell-group-option",
                group=self._group_name(locale, group_id),
                development=self._development_collective_text(locale),
                value=self._money(locale, self._group_building_sale_value(group_id)),
            )
        if value not in self.property_states:
            return value
        space = self.board.space(value)
        state = self.property_states[value]
        return Localization.get(
            locale,
            "monopoly-sell-property-option",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            building=self._development_level_text(locale, state.buildings),
            value=self._money(locale, self._building_sale_value(space)),
            current=self._building_text(locale, state.buildings),
        )

    def _mortgage_property_option_label(self, player: Player, value: str) -> str:
        if value not in self.property_states:
            return value
        locale = self._locale(player)
        space = self.board.space(value)
        return Localization.get(
            locale,
            "monopoly-mortgage-property-option",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            value=self._money(locale, space.mortgage_value),
            cash=self._money(locale, getattr(player, "cash", 0)),
        )

    def _unmortgage_property_option_label(self, player: Player, value: str) -> str:
        if value not in self.property_states:
            return value
        locale = self._locale(player)
        space = self.board.space(value)
        cost = unmortgage_cost(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        return Localization.get(
            locale,
            "monopoly-unmortgage-property-option",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            cost=self._money(locale, cost),
            cash=self._money(locale, getattr(player, "cash", 0)),
        )

    def _property_option_description(self, player: Player, value: str) -> str:
        return self._property_description(self._locale(player), value)

    def _sell_property_option_description(self, player: Player, value: str) -> str:
        if not value.startswith(SELL_GROUP_OPTION_PREFIX):
            return self._property_option_description(player, value)
        locale = self._locale(player)
        group_id = value.removeprefix(SELL_GROUP_OPTION_PREFIX)
        summaries = [
            Localization.get(
                locale,
                "monopoly-group-building-member",
                property=self._space_name(locale, space),
                buildings=self._building_text(
                    locale, self.property_states[space.id].buildings
                ),
            )
            for space in self.board.group_spaces(group_id)
        ]
        return Localization.get(
            locale,
            self.board.development.group_sale_description_key,
            group=self._group_name(locale, group_id),
            development=self._development_collective_text(locale),
            properties=Localization.format_list_and(locale, summaries),
            value=self._money(locale, self._group_building_sale_value(group_id)),
            bank_houses=self.bank_houses,
        )

    def _property_description(self, locale: str, value: str) -> str:
        if value not in self.property_states:
            return ""
        space = self.board.space(value)
        state = self.property_states[value]
        return Localization.get(
            locale,
            "monopoly-property-description",
            property=self._space_name(locale, space),
            kind=self._space_kind_text(locale, space),
            group=self._group_name(locale, space.group_id),
            group_members=self._group_members_text(locale, space.group_id),
            owner=self._owner_name(locale, state.owner_id),
            price=self._money(locale, space.price),
            mortgage=self._money(locale, space.mortgage_value),
            buildings=(
                self._building_text(locale, state.buildings)
                if space.kind == SPACE_STREET
                else Localization.get(locale, "monopoly-not-applicable")
            ),
            rents=self._rent_schedule_text(locale, space),
        )

    def _action_manage_properties(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_manage_entry_enabled(player):
            return
        if not self._manage_property_options(player):
            self._speak(player, "monopoly-error-no-properties")
            return
        self.management_resume_phase = self.phase
        self.management_resume_decision_player_id = self.decision_player_id
        self.management_property_id = ""
        self.phase = PHASE_MANAGE
        self.decision_player_id = player.id
        self._focus_after_user_transition(player)
        self.refresh_menus()

    def _action_choose_management_property(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        if not self._is_actor(player, PHASE_MANAGE):
            return
        options = self._management_selector_options(player, action_id)
        if input_value not in options:
            self._speak(player, "monopoly-error-property-no-longer-eligible")
            return
        focus_ids = {
            "choose_build_property": "build",
            "choose_sell_property": "sell_building",
            "choose_mortgage_property": "mortgage",
            "choose_unmortgage_property": "unmortgage",
        }
        property_id = input_value
        focus_id = focus_ids[action_id]
        if input_value.startswith(SELL_GROUP_OPTION_PREFIX):
            group_id = input_value.removeprefix(SELL_GROUP_OPTION_PREFIX)
            group = self.board.group_spaces(group_id)
            property_id = max(
                group,
                key=lambda space: self.property_states[space.id].buildings,
            ).id
            focus_id = "sell_group_buildings"
        self._select_managed_property(player, property_id, focus_id=focus_id)

    def _action_choose_managed_property(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        if not self._is_actor(player, PHASE_MANAGE):
            return
        if input_value not in self._manage_property_options(player):
            self._speak(player, "monopoly-error-not-your-property")
            return
        space = self.board.space(input_value)
        focus_id = "build" if space.kind == SPACE_STREET else "mortgage"
        self._select_managed_property(player, input_value, focus_id=focus_id)

    def _select_managed_property(
        self, player: MonopolyPlayer, property_id: str, *, focus_id: str
    ) -> None:
        if property_id not in self.property_states:
            return
        self.management_property_id = property_id
        space = self.board.space(property_id)
        state = self.property_states[property_id]
        locale = self._locale(player)
        self._speak(
            player,
            "monopoly-managing-property",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            state=self._property_state_text(locale, state, space),
            cash=self._money(locale, player.cash),
        )
        self.request_menu_focus(player, focus_id)
        self.refresh_menus(player)

    def _action_build(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_build_enabled(player):
            return
        self._apply_build(player, self.management_property_id)
        self._focus_management_task(player, "choose_build_property")

    def _apply_build(
        self, player: MonopolyPlayer, property_id: str, *, announce: bool = True
    ) -> None:
        if self._build_property_error(player, property_id):
            return
        space = self.board.space(property_id)
        state = self.property_states[property_id]
        player.cash -= space.building_cost
        built_level = state.buildings + 1
        state.buildings = built_level
        if self.board.development.finite_supply:
            if built_level == 5:
                self.bank_hotels -= 1
                self.bank_houses += 4
            else:
                self.bank_houses -= 1
        if announce:
            self._broadcast_actor(
                player,
                "monopoly-you-build",
                "monopoly-player-builds",
                building=lambda locale: self._development_level_text(
                    locale, built_level
                ),
                property=lambda locale: self._space_name(locale, space),
                cost=lambda locale: self._money(locale, space.building_cost),
                cash=lambda locale: self._money(locale, player.cash),
                brief_personal_key="monopoly-you-build-brief",
                brief_others_key="monopoly-player-builds-brief",
            )
            self.play_sound(game_audio.SOUND_DEVELOPMENT_BUILT)
        self.refresh_menus()

    def _action_sell_building(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_sell_building_enabled(player):
            return
        self._apply_sell_building(player, self.management_property_id)
        self._focus_management_task(player, "choose_sell_property")

    def _action_sell_group_buildings(
        self, player: MonopolyPlayer, action_id: str
    ) -> None:
        del action_id
        if self._is_sell_group_buildings_enabled(player):
            return
        space = self.board.space(self.management_property_id)
        self._apply_sell_group_buildings(player, space.group_id)
        self._focus_management_task(player, "choose_sell_property")

    def _apply_sell_building(
        self, player: MonopolyPlayer, property_id: str, *, announce: bool = True
    ) -> None:
        if self._sell_property_error(player, property_id):
            return
        space = self.board.space(property_id)
        state = self.property_states[property_id]
        sold_level = state.buildings
        state.buildings -= 1
        if self.board.development.finite_supply:
            if sold_level == 5:
                self.bank_hotels += 1
                self.bank_houses -= 4
            else:
                self.bank_houses += 1
        value = self._building_sale_value(space)
        player.cash += value
        if announce:
            self._broadcast_actor(
                player,
                "monopoly-you-sell-building",
                "monopoly-player-sells-building",
                building=lambda locale: self._development_level_text(
                    locale, sold_level
                ),
                property=lambda locale: self._space_name(locale, space),
                value=lambda locale: self._money(locale, value),
                cash=lambda locale: self._money(locale, player.cash),
                brief_personal_key="monopoly-you-sell-building-brief",
                brief_others_key="monopoly-player-sells-building-brief",
            )
            self.play_sound(game_audio.SOUND_DEVELOPMENT_SOLD)
        self.refresh_menus()

    def _apply_sell_group_buildings(
        self, player: MonopolyPlayer, group_id: str, *, announce: bool = True
    ) -> None:
        group = self.board.group_spaces(group_id)
        value = self._group_building_sale_value(group_id)
        if value <= 0 or not all(
            self.property_states[space.id].owner_id == player.id for space in group
        ):
            return
        houses = 0
        hotels = 0
        for space in group:
            state = self.property_states[space.id]
            if state.buildings == 5:
                hotels += 1
            else:
                houses += state.buildings
            state.buildings = 0
        if self.board.development.finite_supply:
            self.bank_houses += houses
            self.bank_hotels += hotels
        player.cash += value
        if announce:
            self._broadcast_actor(
                player,
                "monopoly-you-sell-group-buildings",
                "monopoly-player-sells-group-buildings",
                group=lambda locale: self._group_name(locale, group_id),
                development=lambda locale: self._development_collective_text(locale),
                value=lambda locale: self._money(locale, value),
                cash=lambda locale: self._money(locale, player.cash),
                brief_personal_key="monopoly-you-sell-group-buildings-brief",
                brief_others_key="monopoly-player-sells-group-buildings-brief",
            )
            self.play_sound(game_audio.SOUND_DEVELOPMENT_SOLD)
        self.refresh_menus()

    def _action_mortgage(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_mortgage_enabled(player):
            return
        self._apply_mortgage(player, self.management_property_id)
        self._focus_management_task(player, "choose_mortgage_property")

    def _apply_mortgage(
        self, player: MonopolyPlayer, property_id: str, *, announce: bool = True
    ) -> None:
        if self._mortgage_property_error(player, property_id):
            return
        space = self.board.space(property_id)
        state = self.property_states[property_id]
        state.mortgaged = True
        player.cash += space.mortgage_value
        if announce:
            self._broadcast_actor(
                player,
                "monopoly-you-mortgage",
                "monopoly-player-mortgages",
                property=lambda locale: self._space_name(locale, space),
                value=lambda locale: self._money(locale, space.mortgage_value),
                cash=lambda locale: self._money(locale, player.cash),
                brief_personal_key="monopoly-you-mortgage-brief",
                brief_others_key="monopoly-player-mortgages-brief",
            )
            self.play_sound(game_audio.SOUND_PROPERTY_MORTGAGED)
        self.refresh_menus()

    def _action_unmortgage(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_unmortgage_enabled(player):
            return
        space = self.board.space(self.management_property_id)
        state = self.property_states[space.id]
        cost = unmortgage_cost(
            space.mortgage_value, self.board.rules.mortgage_interest_percent
        )
        player.cash -= cost
        state.mortgaged = False
        self._broadcast_actor(
            player,
            "monopoly-you-unmortgage",
            "monopoly-player-unmortgages",
            property=lambda locale: self._space_name(locale, space),
            cost=lambda locale: self._money(locale, cost),
            cash=lambda locale: self._money(locale, player.cash),
            brief_personal_key="monopoly-you-unmortgage-brief",
            brief_others_key="monopoly-player-unmortgages-brief",
        )
        self.play_sound(game_audio.SOUND_PROPERTY_UNMORTGAGED)
        self._focus_management_task(player, "choose_unmortgage_property")
        self.refresh_menus()

    def _focus_management_task(self, player: MonopolyPlayer, action_id: str) -> None:
        """Return to the task workspace after a confirmed management action."""

        if not self._is_actor(player, PHASE_MANAGE):
            return
        self.management_property_id = ""
        if not player.is_bot:
            self.request_menu_focus(player, action_id)
        self.refresh_menus(player)

    def _action_finish_management(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if not self._is_actor(player, PHASE_MANAGE):
            return
        resume_phase = self.management_resume_phase
        resume_actor = self.management_resume_decision_player_id
        self.management_property_id = ""
        self.management_resume_phase = ""
        self.management_resume_decision_player_id = ""
        self._restore_interrupted_phase(resume_phase, resume_actor)
        self._focus_after_user_transition(player)

    # ------------------------------------------------------------------
    # Player-to-player trades
    # ------------------------------------------------------------------

    def _trade_target_options(self, player: Player) -> list[str]:
        return [other.id for other in self.alive_players if other.id != player.id]

    def _trade_target_label(self, player: Player, value: str) -> str:
        target = self._alive_player_by_id(value)
        return target.name if target else value

    def _trade_target_description(self, player: Player, value: str) -> str:
        target = self._alive_player_by_id(value)
        if not target:
            return ""
        locale = self._locale(player)
        return Localization.get(
            locale,
            "monopoly-trade-target-description",
            player=target.name,
            cash=self._money(locale, target.cash),
            properties=len(self._owned_property_ids(target.id)),
            net_worth=self._money(locale, self._net_worth(target)),
        )

    def _action_propose_trade(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        if self._is_propose_trade_enabled(player):
            return
        target = self._alive_player_by_id(input_value)
        if not target or target.id == player.id:
            self._speak(player, "monopoly-error-invalid-trade-target")
            return
        self.trade_state = TradeState(
            proposer_id=player.id,
            target_id=target.id,
            resume_phase=self.phase,
            resume_decision_player_id=self.decision_player_id,
        )
        self.phase = PHASE_TRADE_BUILD
        self.decision_player_id = player.id
        self._broadcast_actor_target(
            player,
            target,
            "monopoly-you-start-trade",
            "monopoly-player-starts-trade-with-you",
            "monopoly-player-starts-trade",
            brief_personal_key="monopoly-you-start-trade-brief",
            brief_target_key="monopoly-player-starts-trade-with-you-brief",
            brief_others_key="monopoly-player-starts-trade-brief",
        )
        self._focus_after_user_transition(player)
        self.refresh_menus()

    def _property_is_tradeable(self, property_id: str, owner_id: str) -> bool:
        state = self.property_states.get(property_id)
        if not state or state.owner_id != owner_id:
            return False
        space = self.board.space(property_id)
        if space.kind != SPACE_STREET:
            return True
        return not any(
            self.property_states[group_space.id].buildings
            for group_space in self.board.group_spaces(space.group_id)
        )

    def _trade_offer_property_options(self, player: Player) -> list[str]:
        trade = self.trade_state
        if not trade or trade.proposer_id != player.id:
            return []
        return [
            space.id
            for space in self.board.spaces
            if space.id in self.property_states
            and self._property_is_tradeable(space.id, trade.proposer_id)
        ]

    def _trade_request_property_options(self, player: Player) -> list[str]:
        trade = self.trade_state
        if not trade or trade.proposer_id != player.id:
            return []
        return [
            space.id
            for space in self.board.spaces
            if space.id in self.property_states
            and self._property_is_tradeable(space.id, trade.target_id)
        ]

    def _trade_property_label(
        self, player: Player, value: str, selected: list[str]
    ) -> str:
        locale = self._locale(player)
        if value not in self.property_states:
            return value
        space = self.board.space(value)
        return Localization.get(
            locale,
            "monopoly-trade-property-option",
            selected="yes" if value in selected else "no",
            property=self._space_name(locale, space),
            group=self._group_name(locale, space.group_id),
            status=self._property_state_text(
                locale, self.property_states[value], space
            ),
        )

    def _trade_offer_property_label(self, player: Player, value: str) -> str:
        selected = self.trade_state.offered_property_ids if self.trade_state else []
        return self._trade_property_label(player, value, selected)

    def _trade_request_property_label(self, player: Player, value: str) -> str:
        selected = self.trade_state.requested_property_ids if self.trade_state else []
        return self._trade_property_label(player, value, selected)

    def _toggle_trade_value(self, values: list[str], value: str) -> None:
        if value in values:
            values.remove(value)
        else:
            values.append(value)

    def _action_trade_toggle_offer_property(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        if not trade or input_value not in self._trade_offer_property_options(player):
            return
        self._toggle_trade_value(trade.offered_property_ids, input_value)
        self.refresh_menus(player)

    def _action_trade_toggle_request_property(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        if not trade or input_value not in self._trade_request_property_options(player):
            return
        self._toggle_trade_value(trade.requested_property_ids, input_value)
        self.refresh_menus(player)

    def _trade_offer_jail_card_options(self, player: Player) -> list[str]:
        trade = self.trade_state
        proposer = self._alive_player_by_id(trade.proposer_id) if trade else None
        return (
            proposer.jail_card_ids[:] if proposer and proposer.id == player.id else []
        )

    def _trade_request_jail_card_options(self, player: Player) -> list[str]:
        trade = self.trade_state
        target = self._alive_player_by_id(trade.target_id) if trade else None
        return (
            target.jail_card_ids[:]
            if target and trade and trade.proposer_id == player.id
            else []
        )

    def _jail_card_option_label(self, player: Player, value: str) -> str:
        locale = self._locale(player)
        trade = self.trade_state
        selected = False
        if trade:
            selected = (
                value in trade.offered_jail_card_ids
                or value in trade.requested_jail_card_ids
            )
        try:
            deck_id = self.board.deck_id_for_card(value)
        except KeyError:
            return value
        deck = (
            self.board.terminology.chance_deck_key
            if deck_id == "chance"
            else self.board.terminology.community_deck_key
        )
        return Localization.get(
            locale,
            "monopoly-trade-jail-card-option",
            selected="yes" if selected else "no",
            deck=Localization.get(locale, deck),
        )

    def _action_trade_toggle_offer_jail_card(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        if not trade or input_value not in self._trade_offer_jail_card_options(player):
            return
        self._toggle_trade_value(trade.offered_jail_card_ids, input_value)
        self.refresh_menus(player)

    def _action_trade_toggle_request_jail_card(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        if not trade or input_value not in self._trade_request_jail_card_options(
            player
        ):
            return
        self._toggle_trade_value(trade.requested_jail_card_ids, input_value)
        self.refresh_menus(player)

    def _parse_trade_cash(
        self, player: MonopolyPlayer, input_value: str, *, maximum: int
    ) -> int | None:
        try:
            amount = int(input_value.strip())
        except ValueError:
            self._speak(player, "monopoly-error-cash-number")
            return None
        if amount < 0:
            self._speak(player, "monopoly-error-cash-negative")
            return None
        if amount > maximum:
            self._speak(
                player,
                "monopoly-error-trade-cash-too-high",
                cash=self._money(self._locale(player), maximum),
            )
            return None
        return amount

    def _action_trade_offer_cash(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        if not trade or not self._is_actor(player, PHASE_TRADE_BUILD):
            return
        amount = self._parse_trade_cash(player, input_value, maximum=player.cash)
        if amount is not None:
            trade.offered_cash = amount
            self.refresh_menus(player)

    def _action_trade_request_cash(
        self, player: MonopolyPlayer, input_value: str, action_id: str
    ) -> None:
        del action_id
        trade = self.trade_state
        target = self._alive_player_by_id(trade.target_id) if trade else None
        if not trade or not target or not self._is_actor(player, PHASE_TRADE_BUILD):
            return
        amount = self._parse_trade_cash(player, input_value, maximum=target.cash)
        if amount is not None:
            trade.requested_cash = amount
            self.refresh_menus(player)

    def _trade_transfer_interest(self, property_ids: list[str]) -> int:
        return sum(
            transfer_mortgage_interest(
                self.board.space(property_id).mortgage_value,
                self.board.rules.mortgage_interest_percent,
            )
            for property_id in property_ids
            if self.property_states[property_id].mortgaged
        )

    def _validate_trade(
        self, listener: Player | None = None
    ) -> str | tuple[str, dict] | None:
        trade = self.trade_state
        if not trade:
            return "monopoly-error-no-trade"
        proposer = self._alive_player_by_id(trade.proposer_id)
        target = self._alive_player_by_id(trade.target_id)
        if not proposer or not target or proposer.id == target.id:
            return "monopoly-error-invalid-trade-target"
        if not any(
            (
                trade.offered_property_ids,
                trade.requested_property_ids,
                trade.offered_cash,
                trade.requested_cash,
                trade.offered_jail_card_ids,
                trade.requested_jail_card_ids,
            )
        ):
            return "monopoly-error-empty-trade"
        if trade.offered_cash and trade.requested_cash:
            return "monopoly-error-trade-cash-both-directions"
        if trade.offered_cash > proposer.cash or trade.requested_cash > target.cash:
            return "monopoly-error-trade-cash-changed"
        if len(set(trade.offered_property_ids)) != len(trade.offered_property_ids):
            return "monopoly-error-invalid-trade-assets"
        if len(set(trade.requested_property_ids)) != len(trade.requested_property_ids):
            return "monopoly-error-invalid-trade-assets"
        if len(set(trade.offered_jail_card_ids)) != len(trade.offered_jail_card_ids):
            return "monopoly-error-invalid-trade-assets"
        if len(set(trade.requested_jail_card_ids)) != len(
            trade.requested_jail_card_ids
        ):
            return "monopoly-error-invalid-trade-assets"
        if not all(
            self._property_is_tradeable(value, proposer.id)
            for value in trade.offered_property_ids
        ):
            return "monopoly-error-offered-property-changed"
        if not all(
            self._property_is_tradeable(value, target.id)
            for value in trade.requested_property_ids
        ):
            return "monopoly-error-requested-property-changed"
        if not all(
            value in proposer.jail_card_ids for value in trade.offered_jail_card_ids
        ):
            return "monopoly-error-offered-card-changed"
        if not all(
            value in target.jail_card_ids for value in trade.requested_jail_card_ids
        ):
            return "monopoly-error-requested-card-changed"
        proposer_interest = self._trade_transfer_interest(trade.requested_property_ids)
        target_interest = self._trade_transfer_interest(trade.offered_property_ids)
        proposer_after = (
            proposer.cash
            - trade.offered_cash
            + trade.requested_cash
            - proposer_interest
        )
        target_after = (
            target.cash - trade.requested_cash + trade.offered_cash - target_interest
        )
        if proposer_after < 0:
            locale = self._locale(listener or proposer)
            return (
                "monopoly-error-transfer-interest-cash",
                {
                    "player": proposer.name,
                    "amount": self._money(locale, -proposer_after),
                    "percent": self.board.rules.mortgage_interest_percent,
                },
            )
        if target_after < 0:
            locale = self._locale(listener or target)
            return (
                "monopoly-error-transfer-interest-cash",
                {
                    "player": target.name,
                    "amount": self._money(locale, -target_after),
                    "percent": self.board.rules.mortgage_interest_percent,
                },
            )
        return None

    def _action_trade_submit(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        error = self._validate_trade(player)
        trade = self.trade_state
        if error or not trade or not self._is_actor(player, PHASE_TRADE_BUILD):
            if error:
                if isinstance(error, tuple):
                    self._speak(player, error[0], **error[1])
                else:
                    self._speak(player, error)
            return
        target = self._alive_player_by_id(trade.target_id)
        if not target:
            return
        trade.submitted = True
        self.phase = PHASE_TRADE_RESPONSE
        self.decision_player_id = target.id
        self._announce_trade_submission(player, target)
        self.play_sound(game_audio.SOUND_TRADE_PROPOSED)
        self._focus_after_user_transition(player)
        self.refresh_menus()

    def _action_trade_review(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_trade_review_enabled(player):
            return
        self.live_status_box(
            player,
            "monopoly_trade_review",
            self._build_trade_review_status,
            focus_id="trade:summary",
        )

    def _action_trade_cancel(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        trade = self.trade_state
        if not trade or not self._is_actor(player, PHASE_TRADE_BUILD):
            return
        resume_phase = trade.resume_phase
        resume_actor = trade.resume_decision_player_id
        target = self._alive_player_by_id(trade.target_id)
        self.trade_state = None
        if target:
            self._broadcast_actor_target(
                player,
                target,
                "monopoly-you-cancel-trade",
                "monopoly-player-cancels-trade-with-you",
                "monopoly-player-cancels-trade",
                brief_personal_key="monopoly-you-cancel-trade-brief",
                brief_target_key="monopoly-player-cancels-trade-with-you-brief",
                brief_others_key="monopoly-player-cancels-trade-brief",
            )
        else:
            self._broadcast_actor(
                player,
                "monopoly-you-cancel-trade",
                "monopoly-player-cancels-trade",
                target="",
                brief_personal_key="monopoly-you-cancel-trade-brief",
                brief_others_key="monopoly-player-cancels-trade-brief",
            )
        self._restore_interrupted_phase(resume_phase, resume_actor)
        self._focus_after_user_transition(player)

    def _action_trade_reject(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        trade = self.trade_state
        if not trade or not self._is_actor(player, PHASE_TRADE_RESPONSE):
            return
        proposer = self._alive_player_by_id(trade.proposer_id)
        resume_phase = trade.resume_phase
        resume_actor = trade.resume_decision_player_id
        if proposer:
            self._remember_rejected_bot_trade(proposer, trade)
        self.trade_state = None
        if proposer:
            self._broadcast_actor_target(
                player,
                proposer,
                "monopoly-you-reject-trade",
                "monopoly-player-rejects-your-trade",
                "monopoly-player-rejects-trade",
                proposer=proposer.name,
                brief_personal_key="monopoly-you-reject-trade-brief",
                brief_target_key="monopoly-player-rejects-your-trade-brief",
                brief_others_key="monopoly-player-rejects-trade-brief",
            )
        self._restore_interrupted_phase(resume_phase, resume_actor)
        self._focus_after_user_transition(player)

    def _action_trade_accept(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        trade = self.trade_state
        error = self._validate_trade(player)
        if not trade or not self._is_actor(player, PHASE_TRADE_RESPONSE) or error:
            if error:
                if isinstance(error, tuple):
                    self._speak(player, error[0], **error[1])
                else:
                    self._speak(player, error)
            return
        proposer = self._alive_player_by_id(trade.proposer_id)
        target = self._alive_player_by_id(trade.target_id)
        if not proposer or not target:
            return
        for property_id in trade.requested_property_ids:
            proposer.bot_trade_cooldowns.pop(
                self._bot_trade_memory_key(target.id, property_id),
                None,
            )
        proposer_interest = self._trade_transfer_interest(trade.requested_property_ids)
        target_interest = self._trade_transfer_interest(trade.offered_property_ids)
        proposer.cash = proposer.cash - trade.offered_cash + trade.requested_cash
        target.cash = target.cash - trade.requested_cash + trade.offered_cash
        for property_id in trade.offered_property_ids:
            self.property_states[property_id].owner_id = target.id
        for property_id in trade.requested_property_ids:
            self.property_states[property_id].owner_id = proposer.id
        for card_id in trade.offered_jail_card_ids:
            proposer.jail_card_ids.remove(card_id)
            target.jail_card_ids.append(card_id)
        for card_id in trade.requested_jail_card_ids:
            target.jail_card_ids.remove(card_id)
            proposer.jail_card_ids.append(card_id)
        resume_phase = trade.resume_phase
        resume_actor = trade.resume_decision_player_id
        mortgaged_property_ids = [
            property_id
            for property_id in (
                trade.offered_property_ids + trade.requested_property_ids
            )
            if self.property_states[property_id].mortgaged
        ]
        self._announce_trade_acceptance(
            target,
            proposer,
            mortgaged="yes" if mortgaged_property_ids else "no",
            interest=proposer_interest + target_interest,
        )
        self.play_sound(game_audio.SOUND_TRADE_ACCEPTED)
        group_sound_played = self._announce_completed_groups(
            target, trade.offered_property_ids
        )
        self._announce_completed_groups(
            proposer,
            trade.requested_property_ids,
            play_sound=not group_sound_played,
        )
        self.trade_state = None
        self._start_mortgage_transfers(
            mortgaged_property_ids,
            resume_kind="trade",
            resume_phase=resume_phase,
            resume_decision_player_id=resume_actor,
        )
        self._focus_after_user_transition(player)

    def _trade_side_text(
        self,
        locale: str,
        property_ids: list[str],
        cash: int,
        jail_card_ids: list[str],
    ) -> str:
        parts = [
            self._space_name(locale, self.board.space(property_id))
            for property_id in property_ids
        ]
        if cash:
            parts.append(self._money(locale, cash))
        if jail_card_ids:
            parts.append(
                Localization.get(
                    locale,
                    "monopoly-jail-card-count",
                    count=len(jail_card_ids),
                )
            )
        return (
            Localization.format_list_and(locale, parts)
            if parts
            else Localization.get(locale, "monopoly-nothing")
        )

    def _trade_summary(self, locale: str, *, listener_id: str = "") -> str:
        trade = self.trade_state
        if not trade:
            return Localization.get(locale, "monopoly-no-trade")
        proposer = self.get_player_by_id(trade.proposer_id)
        target = self.get_player_by_id(trade.target_id)
        if listener_id == trade.proposer_id:
            key = "monopoly-trade-summary-proposer"
        elif listener_id == trade.target_id:
            key = "monopoly-trade-summary-target"
        else:
            key = "monopoly-trade-summary"
        return Localization.get(
            locale,
            key,
            proposer=proposer.name if proposer else "",
            offered=self._trade_side_text(
                locale,
                trade.offered_property_ids,
                trade.offered_cash,
                trade.offered_jail_card_ids,
            ),
            target=target.name if target else "",
            requested=self._trade_side_text(
                locale,
                trade.requested_property_ids,
                trade.requested_cash,
                trade.requested_jail_card_ids,
            ),
        )

    def _restore_interrupted_phase(self, phase: str, actor_id: str) -> None:
        self.phase = phase or PHASE_TURN_ACTIONS
        self.decision_player_id = actor_id
        self.refresh_menus()

    # ------------------------------------------------------------------
    # End turn and accessible information views
    # ------------------------------------------------------------------

    def _action_end_turn(self, player: MonopolyPlayer, action_id: str) -> None:
        del action_id
        if self._is_end_turn_enabled(player):
            return
        self._finish_turn()
        # This jump belongs only to the player who explicitly ended their turn.
        # Their disabled Roll control remains a stable anchor until their next
        # turn; passive turn changes never move another player's cursor.
        if not player.is_bot:
            self.request_menu_focus(player, "roll_dice")

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        del action_id
        user = self.get_user(player)
        if not user:
            return
        current = None if self.phase == PHASE_SETUP else self.current_player
        actor = self._decision_player()
        if not current:
            user.speak_l("game-no-turn", buffer="game")
            return
        phase = self._phase_name(user.locale)
        if actor and current.id == player.id and actor.id == player.id:
            user.speak_l(
                "monopoly-whose-turn-your-action",
                buffer="game",
                phase=phase,
            )
            return
        if actor and current.id == player.id:
            user.speak_l(
                "monopoly-whose-turn-your-turn-pending",
                buffer="game",
                decision_player=actor.name,
                phase=phase,
            )
            return
        if actor and actor.id == player.id:
            user.speak_l(
                "monopoly-whose-turn-other-turn-your-action",
                buffer="game",
                turn_player=current.name,
                phase=phase,
            )
            return
        if actor and actor.id == current.id:
            user.speak_l(
                "monopoly-whose-turn-player-action",
                buffer="game",
                turn_player=current.name,
                phase=phase,
            )
            return
        if actor:
            user.speak_l(
                "monopoly-whose-turn-pending",
                buffer="game",
                turn_player=current.name,
                decision_player=actor.name,
                phase=phase,
            )
            return
        self.speak_turn_l(player, current, buffer="game")

    def _action_read_board(self, player: Player, action_id: str) -> None:
        del action_id
        self.live_status_box(
            player,
            "monopoly_board",
            self._build_board_status,
            focus_id=f"space:{self.board.spaces[0].id}",
        )

    def _action_read_cash(self, player: Player, action_id: str) -> None:
        del action_id
        if not isinstance(player, MonopolyPlayer) or player.is_spectator:
            return
        user = self.get_user(player)
        if user:
            user.speak_l(
                "monopoly-your-cash",
                buffer="game",
                cash=self._money(user.locale, player.cash),
            )

    def _action_read_current_space(self, player: Player, action_id: str) -> None:
        del action_id
        if not isinstance(player, MonopolyPlayer) or player.is_spectator:
            return
        user = self.get_user(player)
        if not user:
            return
        space = self.board.spaces[player.position]
        occupants = [
            (
                Localization.get(user.locale, "monopoly-you")
                if table_player.id == player.id
                else table_player.name
            )
            for table_player in self.alive_players
            if table_player.position == player.position
        ]
        players_text = Localization.format_list_and(user.locale, occupants)
        if space.kind in OWNABLE_SPACE_KINDS:
            user.speak_l(
                "monopoly-current-space-ownable",
                buffer="game",
                position=player.position + 1,
                deed=self._property_description(user.locale, space.id),
                players=players_text,
            )
        else:
            user.speak_l(
                "monopoly-current-space-other",
                buffer="game",
                position=player.position + 1,
                space=self._space_name(user.locale, space),
                kind=self._space_kind_text(user.locale, space),
                players=players_text,
            )

    def _action_read_property_groups(self, player: Player, action_id: str) -> None:
        del action_id
        first_group = self.board.property_groups[0]
        self.live_status_box(
            player,
            "monopoly_property_groups",
            self._build_property_groups_status,
            focus_id=f"group:{first_group.id}",
        )

    def _action_read_portfolios(
        self,
        player: Player,
        input_value: str,
        action_id: str,
    ) -> None:
        del action_id
        owner = self.get_player_by_id(input_value)
        if not isinstance(owner, MonopolyPlayer):
            self._speak(player, "monopoly-error-portfolio-player-unavailable")
            return
        first_property_id = next(iter(self._owned_property_ids(owner.id)), "")
        focus_id = (
            f"selected:property:{first_property_id}"
            if first_property_id
            else f"selected:empty:{owner.id}"
        )
        self.live_status_box(
            player,
            f"monopoly_portfolio_{owner.id}",
            lambda viewer, user, owner_id=owner.id: (
                self._build_selected_portfolio_status(
                    viewer,
                    user,
                    owner_id,
                )
            ),
            focus_id=focus_id,
        )
        # The action-input handler performs one final framework refresh after
        # this nested view opens. Preserve the explicit, user-driven focus jump
        # across that repaint instead of letting the client choose an anchor.
        self.request_menu_focus(player, focus_id)

    def _action_read_my_portfolio(self, player: Player, action_id: str) -> None:
        del action_id
        if isinstance(player, MonopolyPlayer) and not player.is_spectator:
            self.live_status_box(
                player,
                "monopoly_my_portfolio",
                self._build_my_portfolio_status,
                focus_id=f"mine:summary:{player.id}",
            )

    def _action_read_status(self, player: Player, action_id: str) -> None:
        del action_id
        self.live_status_box(
            player,
            "monopoly_status",
            self._build_game_status,
            focus_id="turn",
        )

    def _build_board_status(self, player: Player, user) -> StatusBoxBuild:
        locale = user.locale
        items: list[MenuItem] = []
        for index, space in enumerate(self.board.spaces):
            occupants = [
                table_player.name
                for table_player in self.alive_players
                if table_player.position == index
            ]
            players_text = (
                Localization.format_list_and(locale, occupants)
                if occupants
                else Localization.get(locale, "monopoly-no-players")
            )
            if space.kind in OWNABLE_SPACE_KINDS:
                state = self.property_states[space.id]
                text = Localization.get(
                    locale,
                    "monopoly-board-ownable-row",
                    position=index + 1,
                    space=self._space_name(locale, space),
                    group=self._group_name(locale, space.group_id),
                    owner=self._owner_name(locale, state.owner_id),
                    state=self._property_state_text(locale, state, space),
                    players=players_text,
                )
            else:
                text = Localization.get(
                    locale,
                    "monopoly-board-space-row",
                    position=index + 1,
                    space=self._space_name(locale, space),
                    players=players_text,
                )
            items.append(MenuItem(text=text, id=f"space:{space.id}"))
        return StatusBoxBuild(items=items)

    def _build_property_groups_status(self, player: Player, user) -> StatusBoxBuild:
        del player
        locale = user.locale
        items: list[MenuItem] = []
        for group in self.board.property_groups:
            spaces = self.board.group_spaces(group.id)
            owners = {
                self.property_states[space.id].owner_id
                for space in spaces
                if self.property_states[space.id].owner_id
            }
            complete_owner = (
                self.get_player_by_id(next(iter(owners)))
                if len(owners) == 1
                and all(self.property_states[space.id].owner_id for space in spaces)
                else None
            )
            holdings = Localization.format_list_and(
                locale,
                [
                    Localization.get(
                        locale,
                        "monopoly-property-group-holding",
                        property=self._space_name(locale, space),
                        owner=self._owner_name(
                            locale, self.property_states[space.id].owner_id
                        ),
                        state=self._property_state_text(
                            locale, self.property_states[space.id], space
                        ),
                    )
                    for space in spaces
                ],
            )
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-property-group-row",
                        group=Localization.get(locale, group.name_key),
                        complete="yes" if complete_owner else "no",
                        owner=complete_owner.name if complete_owner else "",
                        holdings=holdings,
                    ),
                    id=f"group:{group.id}",
                )
            )
        return StatusBoxBuild(items=items)

    def _portfolio_summary_text(
        self,
        locale: str,
        owner: MonopolyPlayer,
    ) -> str:
        location = self.board.spaces[owner.position]
        status = Localization.get(
            locale,
            (
                "monopoly-status-bankrupt"
                if owner.bankrupt
                else (
                    "monopoly-player-jailed"
                    if owner.in_jail
                    else "monopoly-player-active"
                )
            ),
        )
        return Localization.get(
            locale,
            "monopoly-portfolio-player",
            player=owner.name,
            cash=self._money(locale, owner.cash),
            net_worth=self._money(locale, self._net_worth(owner)),
            space=self._space_name(locale, location),
            status=status,
            jail_cards=len(owner.jail_card_ids),
        )

    def _portfolio_player_options(self, player: Player) -> list[str]:
        del player
        return [
            owner.id
            for owner in self.get_active_players()
            if isinstance(owner, MonopolyPlayer)
        ]

    def _portfolio_player_label(self, player: Player, value: str) -> str:
        owner = self.get_player_by_id(value)
        if not isinstance(owner, MonopolyPlayer):
            return value
        return self._portfolio_summary_text(self._locale(player), owner)

    def _portfolio_property_items(
        self,
        locale: str,
        owner: MonopolyPlayer,
        *,
        prefix: str,
    ) -> list[MenuItem]:
        items: list[MenuItem] = []
        property_ids = self._owned_property_ids(owner.id)
        if not property_ids:
            return [
                MenuItem(
                    text=Localization.get(locale, "monopoly-portfolio-no-properties"),
                    id=f"{prefix}:empty:{owner.id}",
                )
            ]
        for property_id in property_ids:
            space = self.board.space(property_id)
            state = self.property_states[property_id]
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-portfolio-property",
                        property=self._space_name(locale, space),
                        group=self._group_name(locale, space.group_id),
                        state=self._property_state_text(locale, state, space),
                    ),
                    id=f"{prefix}:property:{property_id}",
                )
            )
        return items

    def _portfolio_items(
        self, locale: str, owner: MonopolyPlayer, *, prefix: str
    ) -> list[MenuItem]:
        items = [
            MenuItem(
                text=self._portfolio_summary_text(locale, owner),
                id=f"{prefix}:summary:{owner.id}",
            )
        ]
        if self.options.buy_after_passing_go:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-buying-eligibility",
                        eligible="yes" if owner.passed_go_once else "no",
                    ),
                    id=f"{prefix}:buying-eligibility:{owner.id}",
                )
            )
        items.extend(self._portfolio_property_items(locale, owner, prefix=prefix))
        return items

    def _build_selected_portfolio_status(
        self,
        player: Player,
        user,
        owner_id: str,
    ) -> StatusBoxBuild:
        del player
        owner = self.get_player_by_id(owner_id)
        if not isinstance(owner, MonopolyPlayer):
            return StatusBoxBuild(
                items=[
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "monopoly-portfolio-player-unavailable",
                        ),
                        id="selected:unavailable",
                    )
                ]
            )
        return StatusBoxBuild(
            items=self._portfolio_property_items(
                user.locale,
                owner,
                prefix="selected",
            )
        )

    def _build_my_portfolio_status(self, player: Player, user) -> StatusBoxBuild:
        if not isinstance(player, MonopolyPlayer):
            return StatusBoxBuild(items=[])
        return StatusBoxBuild(
            items=self._portfolio_items(user.locale, player, prefix="mine")
        )

    def _build_trade_review_status(self, player: Player, user) -> StatusBoxBuild:
        trade = self.trade_state
        if not trade:
            return StatusBoxBuild(
                items=[
                    MenuItem(
                        text=Localization.get(user.locale, "monopoly-no-trade"),
                        id="trade:summary",
                    )
                ]
            )
        proposer = self.get_player_by_id(trade.proposer_id)
        target = self.get_player_by_id(trade.target_id)
        items = [
            MenuItem(
                text=self._trade_summary(user.locale, listener_id=player.id),
                id="trade:summary",
            )
        ]
        for recipient, property_ids, side in (
            (target, trade.offered_property_ids, "offered"),
            (proposer, trade.requested_property_ids, "requested"),
        ):
            for property_id in property_ids:
                space = self.board.space(property_id)
                state = self.property_states[property_id]
                interest = (
                    transfer_mortgage_interest(
                        space.mortgage_value,
                        self.board.rules.mortgage_interest_percent,
                    )
                    if state.mortgaged
                    else 0
                )
                items.append(
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "monopoly-trade-review-property",
                            player=recipient.name if recipient else "",
                            deed=self._property_description(user.locale, property_id),
                            mortgaged="yes" if state.mortgaged else "no",
                            interest=self._money(user.locale, interest),
                        ),
                        id=f"trade:{side}:{property_id}",
                    )
                )
        return StatusBoxBuild(items=items)

    def _build_game_status(self, player: Player, user) -> StatusBoxBuild:
        locale = user.locale
        current = self.current_player
        actor = self._decision_player()
        items: list[MenuItem] = [
            MenuItem(
                text=Localization.get(
                    locale,
                    (
                        "monopoly-status-turn-you"
                        if current and current.id == player.id
                        else "monopoly-status-turn"
                    ),
                    player=(
                        current.name
                        if current
                        else Localization.get(locale, "monopoly-no-player")
                    ),
                    phase=self._phase_name(locale),
                ),
                id="turn",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    (
                        "monopoly-status-required-you"
                        if actor and actor.id == player.id
                        else "monopoly-status-required-player"
                    ),
                    player=(
                        actor.name
                        if actor
                        else Localization.get(locale, "monopoly-no-player")
                    ),
                    phase=self._phase_name(locale),
                ),
                id="required-player",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    self.board.development.bank_supply_key,
                    houses=self.bank_houses,
                    hotels=self.bank_hotels,
                ),
                id="bank-supply",
            ),
        ]
        if self.options.free_parking_cash:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-free-parking-pot",
                        space=self._space_name(
                            locale,
                            self._space_of_kind(SPACE_FREE_PARKING),
                        ),
                        amount=self._money(locale, self.free_parking_pot),
                    ),
                    id="free-parking-pot",
                )
            )
        if self.last_die_1 and self.last_die_2:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-status-last-roll",
                        die1=self.last_die_1,
                        die2=self.last_die_2,
                        total=self.last_die_1 + self.last_die_2,
                    ),
                    id="last-roll",
                )
            )
        if self.auction_state:
            leader = self.get_player_by_id(self.auction_state.highest_bidder_id)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-status-auction",
                        property=self._space_name(
                            locale, self.board.space(self.auction_state.property_id)
                        ),
                        bid=self._money(locale, self.auction_state.highest_bid),
                        leader=(
                            leader.name
                            if leader
                            else Localization.get(locale, "monopoly-no-bidder")
                        ),
                    ),
                    id="auction",
                )
            )
        if self.debt_state:
            debtor = self.get_player_by_id(self.debt_state.debtor_id)
            creditor = self.get_player_by_id(self.debt_state.creditor_id)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "monopoly-status-debt",
                        debtor=debtor.name if debtor else "",
                        creditor=(
                            creditor.name
                            if creditor
                            else Localization.get(locale, "monopoly-bank")
                        ),
                        amount=self._money(locale, self.debt_state.amount),
                    ),
                    id="debt",
                )
            )
        if self.trade_state:
            trade = self.trade_state
            proposer = self.get_player_by_id(trade.proposer_id)
            target = self.get_player_by_id(trade.target_id)
            can_see_terms = trade.submitted or player.id == trade.proposer_id
            items.append(
                MenuItem(
                    text=(
                        self._trade_summary(locale, listener_id=player.id)
                        if can_see_terms
                        else Localization.get(
                            locale,
                            "monopoly-status-trade-preparing",
                            proposer=proposer.name if proposer else "",
                            target=target.name if target else "",
                        )
                    ),
                    id="trade",
                )
            )
        return StatusBoxBuild(items=items)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        participants = [
            player
            for player in self.get_active_players()
            if isinstance(player, MonopolyPlayer)
        ]
        rankings = sorted(
            participants,
            key=lambda player: (
                0 if player.id == self.winner_id else 1,
                -player.bankruptcy_order,
                player.name.casefold(),
            ),
        )
        summaries = [
            {
                "player": player.name,
                "cash": player.cash,
                "net_worth": self._net_worth(player),
                "bankrupt": player.bankrupt,
            }
            for player in rankings
        ]
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in participants
            ],
            custom_data={
                "winner_name": self.winner.name if self.winner else None,
                "winner_ids": [self.winner_id] if self.winner_id else [],
                "board_id": self.board.id,
                "currency_key": self.board.currency_key,
                "rankings": summaries,
                "team_rankings": [
                    {
                        "index": index,
                        "members": [player.name],
                        "score": len(rankings) - index,
                        "is_individual": True,
                    }
                    for index, player in enumerate(rankings)
                ],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        winner = result.custom_data.get("winner_name")
        lines = [
            (
                Localization.get(locale, "monopoly-results-winner", player=winner)
                if winner
                else Localization.get(locale, "game-over")
            )
        ]
        for rank, summary in enumerate(result.custom_data.get("rankings", []), 1):
            lines.append(
                Localization.get(
                    locale,
                    "monopoly-results-place",
                    rank=rank,
                    player=summary["player"],
                    cash=self._result_money(result, locale, summary["cash"]),
                    net_worth=self._result_money(
                        result, locale, summary["net_worth"]
                    ),
                    bankrupt="yes" if summary["bankrupt"] else "no",
                )
            )
        return lines

    def _result_money(self, result: GameResult, locale: str, amount: int) -> str:
        currency_key = result.custom_data.get("currency_key")
        if not isinstance(currency_key, str) or not currency_key:
            currency_key = self.board.currency_key
        return Localization.get(locale, currency_key, amount=amount)

    # ------------------------------------------------------------------
    # Shared communication helpers
    # ------------------------------------------------------------------

    def _phase_name(self, locale: str) -> str:
        return Localization.get(
            locale, f"monopoly-phase-{self.phase.replace('_', '-')}"
        )

    def _space_kind_text(
        self,
        locale: str,
        space: BoardSpaceDefinition,
    ) -> str:
        themed_keys = {
            SPACE_STREET: self.board.terminology.street_kind_key,
            SPACE_TRANSIT: self.board.terminology.transit_kind_key,
            SPACE_UTILITY: self.board.terminology.utility_kind_key,
            SPACE_CHANCE: self.board.terminology.chance_kind_key,
            SPACE_COMMUNITY: self.board.terminology.community_kind_key,
        }
        key = themed_keys.get(
            space.kind, f"monopoly-space-kind-{space.kind.replace('_', '-')}"
        )
        return Localization.get(locale, key)

    def _development_level_text(self, locale: str, level: int) -> str:
        keys = self.board.development.level_keys
        if keys:
            if level <= 0:
                return Localization.get(locale, self.board.development.empty_key)
            return Localization.get(locale, keys[min(level, len(keys)) - 1])
        return Localization.get(
            locale,
            "monopoly-building-hotel"
            if level >= 5
            else "monopoly-building-house",
        )

    def _development_collective_text(self, locale: str) -> str:
        return Localization.get(locale, self.board.development.collective_key)

    def _building_text(self, locale: str, buildings: int) -> str:
        buildings = min(max(buildings, 0), 5)
        if self.board.development.level_keys:
            key = (
                self.board.development.empty_key
                if buildings <= 0
                else self.board.development.level_keys[
                    min(buildings, len(self.board.development.level_keys)) - 1
                ]
            )
            return Localization.get(locale, key)
        if buildings == 5:
            return Localization.get(locale, "monopoly-building-one-hotel")
        return Localization.get(
            locale, "monopoly-building-house-count", count=buildings
        )

    def _property_state_text(
        self,
        locale: str,
        state: PropertyState,
        space: BoardSpaceDefinition | None = None,
    ) -> str:
        if space and space.kind != SPACE_STREET:
            return Localization.get(
                locale,
                "monopoly-property-state-no-buildings",
                mortgaged="yes" if state.mortgaged else "no",
            )
        return Localization.get(
            locale,
            "monopoly-property-state",
            mortgaged="yes" if state.mortgaged else "no",
            buildings=self._building_text(locale, state.buildings),
        )

    def _building_sale_value(self, space: BoardSpaceDefinition) -> int:
        return space.building_cost * self.board.rules.building_sale_percent // 100

    def _group_building_sale_value(self, group_id: str) -> int:
        return sum(
            self.property_states[space.id].buildings * self._building_sale_value(space)
            for space in self.board.group_spaces(group_id)
        )

    def _net_worth(self, player: MonopolyPlayer) -> int:
        return net_worth(
            self.board,
            self.property_states,
            player.id,
            player.cash,
        )

    def _broadcast_actor(
        self,
        actor: MonopolyPlayer,
        personal_key: str,
        public_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        suppress_brief: bool = False,
        **kwargs: Any,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == actor.id
            key = personal_key if is_actor else public_key
            if self._wants_brief(user):
                if suppress_brief:
                    continue
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key
            payload = self._resolve_broadcast_kwargs(user.locale, kwargs)
            if not is_actor:
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_actor_target(
        self,
        actor: MonopolyPlayer,
        target_player: MonopolyPlayer,
        personal_key: str,
        target_key: str,
        public_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_target_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Broadcast an interaction with first-, second-, and third-person forms."""

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_brief = self._wants_brief(user)
            if listener.id == actor.id:
                key = personal_key
                if is_brief and brief_personal_key:
                    key = brief_personal_key
            elif listener.id == target_player.id:
                key = target_key
                if is_brief and brief_target_key:
                    key = brief_target_key
            else:
                key = public_key
                if is_brief and brief_others_key:
                    key = brief_others_key
            payload = self._resolve_broadcast_kwargs(user.locale, kwargs)
            payload["player"] = actor.name
            payload["target"] = target_player.name
            user.speak_l(key, buffer="game", **payload)

    def _announce_trade_submission(
        self,
        proposer: MonopolyPlayer,
        target: MonopolyPlayer,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == proposer.id:
                key = "monopoly-you-submit-trade"
                brief_key = "monopoly-you-submit-trade-brief"
            elif listener.id == target.id:
                key = "monopoly-player-submits-trade-to-you"
                brief_key = "monopoly-player-submits-trade-to-you-brief"
            else:
                key = "monopoly-player-submits-trade"
                brief_key = "monopoly-player-submits-trade-brief"
            user.speak_l(
                brief_key if self._wants_brief(user) else key,
                buffer="game",
                player=proposer.name,
                proposer=proposer.name,
                target=target.name,
                summary=self._trade_summary(
                    user.locale,
                    listener_id=listener.id,
                ),
            )

    def _announce_trade_acceptance(
        self,
        target: MonopolyPlayer,
        proposer: MonopolyPlayer,
        *,
        mortgaged: str,
        interest: int,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == target.id:
                key = "monopoly-you-accept-trade"
                brief_key = "monopoly-you-accept-trade-brief"
            elif listener.id == proposer.id:
                key = "monopoly-player-accepts-your-trade"
                brief_key = "monopoly-player-accepts-your-trade-brief"
            else:
                key = "monopoly-player-accepts-trade"
                brief_key = "monopoly-player-accepts-trade-brief"
            user.speak_l(
                brief_key if self._wants_brief(user) else key,
                buffer="game",
                player=target.name,
                proposer=proposer.name,
                target=target.name,
                summary=self._trade_summary(
                    user.locale,
                    listener_id=listener.id,
                ),
                mortgaged=mortgaged,
                interest=self._money(user.locale, interest),
            )

    def _broadcast_global(
        self, full_key: str, brief_key: str | None = None, **kwargs: Any
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(
                key,
                buffer="game",
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )

    def _wants_brief(self, user: Any) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _speak(self, player: Player, key: str, **kwargs: Any) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(key, buffer="game", **kwargs)

    def _alive_player_by_id(self, player_id: str) -> MonopolyPlayer | None:
        player = self.get_player_by_id(player_id) if player_id else None
        if isinstance(player, MonopolyPlayer) and not player.bankrupt:
            return player
        return None

    def _owned_property_ids(self, owner_id: str) -> list[str]:
        return [
            property_id
            for property_id, state in self.property_states.items()
            if state.owner_id == owner_id
        ]

    def _announce_completed_groups(
        self,
        owner: MonopolyPlayer,
        acquired_property_ids: list[str],
        *,
        play_sound: bool = True,
    ) -> bool:
        group_ids = list(
            dict.fromkeys(
                self.board.space(property_id).group_id
                for property_id in acquired_property_ids
                if property_id in self.property_states
            )
        )
        completed_group_ids = [
            group_id
            for group_id in group_ids
            if owns_group(self.board, self.property_states, owner.id, group_id)
        ]
        if completed_group_ids and play_sound:
            self.play_sound(
                game_audio.SOUND_COLOR_GROUP_COMPLETED,
                max_instances=1,
            )
        for group_id in completed_group_ids:
            self._broadcast_actor(
                owner,
                "monopoly-you-complete-property-group",
                "monopoly-player-completes-property-group",
                group=lambda locale, group_id=group_id: self._group_name(
                    locale, group_id
                ),
                properties=lambda locale, group_id=group_id: self._group_members_text(
                    locale, group_id
                ),
                brief_personal_key="monopoly-you-complete-property-group-brief",
                brief_others_key="monopoly-player-completes-property-group-brief",
            )
        return bool(completed_group_ids)

    def _owned_building_counts(self, owner_id: str) -> tuple[int, int]:
        houses = 0
        hotels = 0
        for property_id in self._owned_property_ids(owner_id):
            buildings = self.property_states[property_id].buildings
            if buildings == 5:
                hotels += 1
            else:
                houses += buildings
        return houses, hotels

    def _return_jail_cards(self, player: MonopolyPlayer) -> None:
        for card_id in player.jail_card_ids:
            deck_id = self.board.deck_id_for_card(card_id)
            deck = self.chance_deck if deck_id == "chance" else self.community_deck
            deck.append(card_id)
        player.jail_card_ids.clear()

    def _return_buildings_to_bank(self, state: PropertyState) -> None:
        if not self.board.development.finite_supply:
            return
        if state.buildings == 5:
            self.bank_hotels += 1
        else:
            self.bank_houses += state.buildings

    def _development_error_key(self, error_key: str) -> str:
        return self.board.development.error_key(error_key)

    def _check_for_winner(self) -> bool:
        alive = self.alive_players
        if len(alive) != 1:
            return False
        winner = alive[0]
        self.winner_id = winner.id
        self._finish_payment_batch()
        self.cancel_all_sequences()
        self.scheduled_sounds.clear()
        self.stop_music(fade_ms=0)
        self.play_sound(game_audio.SOUND_GAME_WON)
        self._broadcast_actor(
            winner,
            "monopoly-you-win",
            "monopoly-player-wins",
            cash=lambda locale: self._money(locale, winner.cash),
            net_worth=lambda locale: self._money(locale, self._net_worth(winner)),
            brief_personal_key="monopoly-you-win-brief",
            brief_others_key="monopoly-player-wins-brief",
        )
        self.finish_game()
        return True
