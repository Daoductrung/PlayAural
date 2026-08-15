"""Serializable Monopoly state and immutable board content models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import cached_property
from types import MappingProxyType

from mashumaro.mixins.json import DataClassJSONMixin

SPACE_GO = "go"
SPACE_STREET = "street"
SPACE_TRANSIT = "transit"
SPACE_UTILITY = "utility"
SPACE_CHANCE = "chance"
SPACE_COMMUNITY = "community"
SPACE_TAX = "tax"
SPACE_JAIL = "jail"
SPACE_FREE_PARKING = "free_parking"
SPACE_GO_TO_JAIL = "go_to_jail"

OWNABLE_SPACE_KINDS = {SPACE_STREET, SPACE_TRANSIT, SPACE_UTILITY}

CARD_MOVE = "move"
CARD_NEAREST = "nearest"
CARD_COLLECT = "collect"
CARD_PAY = "pay"
CARD_COLLECT_EACH = "collect_each"
CARD_PAY_EACH = "pay_each"
CARD_REPAIRS = "repairs"
CARD_JAIL_FREE = "jail_free"
CARD_GO_TO_JAIL = "go_to_jail"
CARD_BACK = "back"


@dataclass(frozen=True)
class BoardSpaceDefinition:
    """One immutable square in a registered Monopoly board."""

    id: str
    name_key: str
    kind: str
    price: int = 0
    mortgage_value: int = 0
    group_id: str = ""
    rents: tuple[int, ...] = ()
    building_cost: int = 0
    tax_amount: int = 0


@dataclass(frozen=True)
class PropertyGroupDefinition:
    """Localized metadata for one board-specific property group."""

    id: str
    name_key: str


@dataclass(frozen=True)
class CardDefinition:
    """One immutable Chance or Community Chest instruction."""

    id: str
    text_key: str
    action: str
    amount: int = 0
    destination_id: str = ""
    collect_go: bool = False
    nearest_kind: str = ""
    rent_multiplier: int = 1
    per_house: int = 0
    per_hotel: int = 0


@dataclass(frozen=True)
class RuleDefinition:
    """Declarative rule values that a regional board may customize."""

    auction_opening_bid: int = 1
    auction_bid_increment: int = 1
    consecutive_doubles_to_jail: int = 3
    failed_jail_rolls_before_fine: int = 3
    mortgage_interest_percent: int = 10
    building_sale_percent: int = 50
    utility_single_multiplier: int = 4
    utility_complete_group_multiplier: int = 10


@dataclass(frozen=True)
class BoardTerminology:
    """Localized names for concepts that themed boards rename."""

    street_kind_key: str = "monopoly-space-kind-street"
    transit_kind_key: str = "monopoly-space-kind-railroad"
    utility_kind_key: str = "monopoly-space-kind-utility"
    chance_kind_key: str = "monopoly-space-kind-chance"
    community_kind_key: str = "monopoly-space-kind-community"
    chance_deck_key: str = "monopoly-deck-chance"
    community_deck_key: str = "monopoly-deck-community"
    utility_rent_schedule_key: str = "monopoly-utility-rent-schedule"


@dataclass(frozen=True)
class DevelopmentDefinition:
    """Board-specific presentation and supply policy for building levels."""

    level_keys: tuple[str, ...] = ()
    empty_key: str = ""
    collective_key: str = "monopoly-development-collective"
    build_selector_key: str = "monopoly-action-choose-build-property"
    sell_selector_key: str = "monopoly-action-choose-sell-property"
    rent_schedule_key: str = "monopoly-street-rent-schedule"
    bank_supply_key: str = "monopoly-bank-supply"
    group_sale_description_key: str = "monopoly-sell-group-option-description"
    finite_supply: bool = True
    error_key_overrides: tuple[tuple[str, str], ...] = ()

    @cached_property
    def _error_key_lookup(self) -> Mapping[str, str]:
        return MappingProxyType(dict(self.error_key_overrides))

    def error_key(self, default_key: str) -> str:
        """Return a board-specific rule explanation when one is configured."""

        return self._error_key_lookup.get(default_key, default_key)


@dataclass(frozen=True)
class BoardDefinition:
    """All data that varies between regional or themed Monopoly boards."""

    id: str
    name_key: str
    description_key: str
    currency_key: str
    property_groups: tuple[PropertyGroupDefinition, ...]
    spaces: tuple[BoardSpaceDefinition, ...]
    chance_cards: tuple[CardDefinition, ...]
    community_cards: tuple[CardDefinition, ...]
    starting_cash: int = 1_500
    go_salary: int = 200
    snake_eyes_bonus: int = 500
    jail_fine: int = 50
    bank_houses: int = 32
    bank_hotels: int = 12
    jail_space_id: str = "jail"
    go_space_id: str = "go"
    terminology: BoardTerminology = field(default_factory=BoardTerminology)
    development: DevelopmentDefinition = field(default_factory=DevelopmentDefinition)
    rules: RuleDefinition = field(default_factory=RuleDefinition)

    @cached_property
    def _space_lookup(self) -> Mapping[str, tuple[int, BoardSpaceDefinition]]:
        return MappingProxyType(
            {space.id: (index, space) for index, space in enumerate(self.spaces)}
        )

    @cached_property
    def _card_lookup(self) -> Mapping[str, tuple[str, CardDefinition]]:
        return MappingProxyType(
            {
                card.id: (deck_id, card)
                for deck_id, cards in (
                    ("chance", self.chance_cards),
                    ("community", self.community_cards),
                )
                for card in cards
            }
        )

    @cached_property
    def _group_space_lookup(
        self,
    ) -> Mapping[str, tuple[BoardSpaceDefinition, ...]]:
        return MappingProxyType(
            {
                group.id: tuple(
                    space for space in self.spaces if space.group_id == group.id
                )
                for group in self.property_groups
            }
        )

    @cached_property
    def _property_group_lookup(self) -> Mapping[str, PropertyGroupDefinition]:
        return MappingProxyType({group.id: group for group in self.property_groups})

    def space(self, space_id: str) -> BoardSpaceDefinition:
        try:
            return self._space_lookup[space_id][1]
        except KeyError:
            raise KeyError(space_id) from None

    def space_index(self, space_id: str) -> int:
        try:
            return self._space_lookup[space_id][0]
        except KeyError:
            raise KeyError(space_id) from None

    def card(self, deck_id: str, card_id: str) -> CardDefinition:
        if deck_id not in {"chance", "community"}:
            raise KeyError(deck_id)
        try:
            card_deck_id, card = self._card_lookup[card_id]
        except KeyError:
            raise KeyError(card_id) from None
        if card_deck_id != deck_id:
            raise KeyError(card_id)
        return card

    def deck_id_for_card(self, card_id: str) -> str:
        try:
            return self._card_lookup[card_id][0]
        except KeyError:
            raise KeyError(card_id) from None

    def group_spaces(self, group_id: str) -> tuple[BoardSpaceDefinition, ...]:
        return self._group_space_lookup.get(group_id, ())

    def property_group(self, group_id: str) -> PropertyGroupDefinition:
        try:
            return self._property_group_lookup[group_id]
        except KeyError:
            raise KeyError(group_id) from None


@dataclass
class PropertyState(DataClassJSONMixin):
    owner_id: str = ""
    mortgaged: bool = False
    buildings: int = 0  # Board-defined development level from 0 through 5.


@dataclass
class RentState(DataClassJSONMixin):
    tenant_id: str
    owner_id: str
    property_id: str
    amount: int


@dataclass
class AuctionState(DataClassJSONMixin):
    property_id: str
    bidder_ids: list[str] = field(default_factory=list)
    active_bidder_ids: list[str] = field(default_factory=list)
    highest_bidder_id: str = ""
    highest_bid: int = 0
    minimum_bid: int = 1
    resume_kind: str = "landing"


@dataclass
class DebtState(DataClassJSONMixin):
    debtor_id: str
    creditor_id: str
    amount: int
    reason_key: str
    continuation: str = "finish_landing"


@dataclass
class QueuedPayment(DataClassJSONMixin):
    payer_id: str
    payee_id: str
    amount: int
    reason_key: str


@dataclass
class TradeState(DataClassJSONMixin):
    proposer_id: str
    target_id: str
    offered_property_ids: list[str] = field(default_factory=list)
    requested_property_ids: list[str] = field(default_factory=list)
    offered_cash: int = 0
    requested_cash: int = 0
    offered_jail_card_ids: list[str] = field(default_factory=list)
    requested_jail_card_ids: list[str] = field(default_factory=list)
    resume_phase: str = "await_roll"
    resume_decision_player_id: str = ""
    submitted: bool = False


@dataclass
class MortgageTransferState(DataClassJSONMixin):
    """Required choices for mortgaged deeds received from another player."""

    property_ids: list[str] = field(default_factory=list)
    resume_kind: str = "trade"
    resume_phase: str = "turn_actions"
    resume_decision_player_id: str = ""
    resume_continuation: str = "finish_landing"
    resume_was_current: bool = False


@dataclass
class BankruptcyState(DataClassJSONMixin):
    was_current_player: bool
    resume_continuation: str
    property_auction_ids: list[str] = field(default_factory=list)
