"""Reusable contemporary card decks for standard regional boards."""

from __future__ import annotations

from dataclasses import replace

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
    SPACE_TRANSIT,
    SPACE_UTILITY,
    CardDefinition,
)

_MONEY_ACTIONS = {
    CARD_COLLECT,
    CARD_COLLECT_EACH,
    CARD_PAY,
    CARD_PAY_EACH,
}


def _scale_card_money(
    cards: tuple[CardDefinition, ...], money_scale: int
) -> tuple[CardDefinition, ...]:
    """Scale currency fields without changing movement distances."""

    if (
        not isinstance(money_scale, int)
        or isinstance(money_scale, bool)
        or money_scale <= 0
    ):
        raise ValueError("Standard Monopoly cards need a positive money scale")
    if money_scale == 1:
        return cards
    scaled: list[CardDefinition] = []
    for card in cards:
        changes: dict[str, int] = {}
        if card.action in _MONEY_ACTIONS:
            changes["amount"] = card.amount * money_scale
        if card.action == CARD_REPAIRS:
            changes["per_house"] = card.per_house * money_scale
            changes["per_hotel"] = card.per_hotel * money_scale
        scaled.append(replace(card, **changes) if changes else card)
    return tuple(scaled)


def standard_chance_cards(
    *,
    top_property_id: str,
    red_property_id: str,
    pink_property_id: str,
    named_transit_id: str,
    money_scale: int = 1,
    repairs_text_key: str = "monopoly-card-chance-repairs",
) -> tuple[CardDefinition, ...]:
    """Build the contemporary Chance deck with regional destinations."""

    cards = (
        CardDefinition(
            "chance_top_property",
            "monopoly-card-chance-top-property",
            CARD_MOVE,
            destination_id=top_property_id,
            collect_go=False,
        ),
        CardDefinition(
            "chance_go",
            "monopoly-card-chance-go",
            CARD_MOVE,
            destination_id="go",
            collect_go=True,
        ),
        CardDefinition(
            "chance_red_property",
            "monopoly-card-chance-red-property",
            CARD_MOVE,
            destination_id=red_property_id,
            collect_go=True,
        ),
        CardDefinition(
            "chance_pink_property",
            "monopoly-card-chance-pink-property",
            CARD_MOVE,
            destination_id=pink_property_id,
            collect_go=True,
        ),
        CardDefinition(
            "chance_transit_1",
            "monopoly-card-chance-nearest-transit",
            CARD_NEAREST,
            nearest_kind=SPACE_TRANSIT,
            rent_multiplier=2,
        ),
        CardDefinition(
            "chance_transit_2",
            "monopoly-card-chance-nearest-transit",
            CARD_NEAREST,
            nearest_kind=SPACE_TRANSIT,
            rent_multiplier=2,
        ),
        CardDefinition(
            "chance_utility",
            "monopoly-card-chance-nearest-utility",
            CARD_NEAREST,
            nearest_kind=SPACE_UTILITY,
            rent_multiplier=10,
        ),
        CardDefinition(
            "chance_dividend",
            "monopoly-card-chance-dividend",
            CARD_COLLECT,
            amount=50,
        ),
        CardDefinition(
            "chance_jail_free",
            "monopoly-card-chance-jail-free",
            CARD_JAIL_FREE,
        ),
        CardDefinition(
            "chance_back_three",
            "monopoly-card-chance-back-three",
            CARD_BACK,
            amount=3,
        ),
        CardDefinition(
            "chance_go_jail",
            "monopoly-card-chance-go-jail",
            CARD_GO_TO_JAIL,
        ),
        CardDefinition(
            "chance_repairs",
            repairs_text_key,
            CARD_REPAIRS,
            per_house=25,
            per_hotel=100,
        ),
        CardDefinition(
            "chance_speeding",
            "monopoly-card-chance-speeding",
            CARD_PAY,
            amount=15,
        ),
        CardDefinition(
            "chance_named_transit",
            "monopoly-card-chance-named-transit",
            CARD_MOVE,
            destination_id=named_transit_id,
            collect_go=True,
        ),
        CardDefinition(
            "chance_chairperson",
            "monopoly-card-chance-chairperson",
            CARD_PAY_EACH,
            amount=50,
        ),
        CardDefinition(
            "chance_loan",
            "monopoly-card-chance-loan",
            CARD_COLLECT,
            amount=150,
        ),
    )
    return _scale_card_money(cards, money_scale)


def standard_community_cards(
    *,
    money_scale: int = 1,
    repairs_text_key: str = "monopoly-card-community-repairs",
) -> tuple[CardDefinition, ...]:
    """Build the contemporary Community Chest deck."""

    cards = (
        CardDefinition(
            "community_neighbor",
            "monopoly-card-community-neighbor",
            CARD_COLLECT,
            amount=100,
        ),
        CardDefinition(
            "community_path",
            "monopoly-card-community-path",
            CARD_COLLECT,
            amount=50,
        ),
        CardDefinition(
            "community_blood",
            "monopoly-card-community-blood",
            CARD_COLLECT,
            amount=10,
        ),
        CardDefinition(
            "community_bake_buy",
            "monopoly-card-community-bake-buy",
            CARD_PAY,
            amount=50,
        ),
        CardDefinition(
            "community_jail_free",
            "monopoly-card-community-jail-free",
            CARD_JAIL_FREE,
        ),
        CardDefinition(
            "community_party",
            "monopoly-card-community-party",
            CARD_COLLECT_EACH,
            amount=10,
        ),
        CardDefinition(
            "community_go_jail",
            "monopoly-card-community-go-jail",
            CARD_GO_TO_JAIL,
        ),
        CardDefinition(
            "community_groceries",
            "monopoly-card-community-groceries",
            CARD_COLLECT,
            amount=20,
        ),
        CardDefinition(
            "community_playground",
            "monopoly-card-community-playground",
            CARD_COLLECT,
            amount=100,
        ),
        CardDefinition(
            "community_hospital",
            "monopoly-card-community-hospital",
            CARD_COLLECT,
            amount=100,
        ),
        CardDefinition(
            "community_car_wash",
            "monopoly-card-community-car-wash",
            CARD_PAY,
            amount=100,
        ),
        CardDefinition(
            "community_race",
            "monopoly-card-community-race",
            CARD_MOVE,
            destination_id="go",
            collect_go=True,
        ),
        CardDefinition(
            "community_storm",
            "monopoly-card-community-storm",
            CARD_COLLECT,
            amount=200,
        ),
        CardDefinition(
            "community_shelter",
            "monopoly-card-community-shelter",
            CARD_PAY,
            amount=50,
        ),
        CardDefinition(
            "community_repairs",
            repairs_text_key,
            CARD_REPAIRS,
            per_house=40,
            per_hotel=115,
        ),
        CardDefinition(
            "community_bake_sale",
            "monopoly-card-community-bake-sale",
            CARD_COLLECT,
            amount=25,
        ),
    )
    return _scale_card_money(cards, money_scale)
