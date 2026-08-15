"""Hanoi, Vietnam board content."""

from __future__ import annotations

from .boards import register_board
from .models import (
    SPACE_COMMUNITY,
    BoardDefinition,
    BoardTerminology,
    DevelopmentDefinition,
    RuleDefinition,
)
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups(
    "monopoly-group-hanoi-bus-stations",
    "monopoly-group-hanoi-landmarks",
)

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-hanoi-hoan-kiem-lake"),
        ("dinh_liet", "monopoly-space-hanoi-dinh-liet"),
        ("social_insurance", "monopoly-space-hanoi-social-insurance"),
        ("trang_tien", "monopoly-space-hanoi-trang-tien"),
        ("lottery_1", "monopoly-space-hanoi-lottery"),
        ("my_dinh_bus_station", "monopoly-space-hanoi-my-dinh-bus-station"),
        ("hang_khay", "monopoly-space-hanoi-hang-khay"),
        ("lucky_draw_1", "monopoly-space-hanoi-lucky-draw"),
        ("nguyen_huu_huan", "monopoly-space-hanoi-nguyen-huu-huan"),
        ("ngo_tat_to", "monopoly-space-hanoi-ngo-tat-to"),
        ("jail", "monopoly-space-hanoi-hoa-lo-prison"),
        ("hang_ga", "monopoly-space-hanoi-hang-ga"),
        ("lottery_2", "monopoly-space-hanoi-lottery"),
        ("hang_gai", "monopoly-space-hanoi-hang-gai"),
        ("hang_ca", "monopoly-space-hanoi-hang-ca"),
        ("nuoc_ngam_bus_station", "monopoly-space-hanoi-nuoc-ngam-bus-station"),
        ("cau_go", "monopoly-space-hanoi-cau-go"),
        ("one_pillar_pagoda", "monopoly-space-hanoi-one-pillar-pagoda"),
        ("bat_dan", "monopoly-space-hanoi-bat-dan"),
        ("thanh_nien", "monopoly-space-hanoi-thanh-nien"),
        ("free_parking", "monopoly-space-hanoi-west-lake"),
        ("nha_tho", "monopoly-space-hanoi-nha-tho"),
        ("lucky_draw_2", "monopoly-space-hanoi-lucky-draw"),
        ("ngu_xa", "monopoly-space-hanoi-ngu-xa"),
        ("hang_hanh", "monopoly-space-hanoi-hang-hanh"),
        ("giap_bat_bus_station", "monopoly-space-hanoi-giap-bat-bus-station"),
        ("ngo_huyen", "monopoly-space-hanoi-ngo-huyen"),
        ("nam_ngu", "monopoly-space-hanoi-nam-ngu"),
        ("long_bien_bridge", "monopoly-space-hanoi-long-bien-bridge"),
        ("hang_manh", "monopoly-space-hanoi-hang-manh"),
        ("go_to_jail", "monopoly-space-hanoi-go-to-hoa-lo"),
        ("le_van_huu", "monopoly-space-hanoi-le-van-huu"),
        ("giang_vo", "monopoly-space-hanoi-giang-vo"),
        ("lottery_3", "monopoly-space-hanoi-lottery"),
        ("hang_chao", "monopoly-space-hanoi-hang-chao"),
        ("gia_lam_bus_station", "monopoly-space-hanoi-gia-lam-bus-station"),
        ("lucky_draw_3", "monopoly-space-hanoi-lucky-draw"),
        ("nha_chung", "monopoly-space-hanoi-nha-chung"),
        ("excise_tax", "monopoly-space-hanoi-excise-tax"),
        ("lo_duc", "monopoly-space-hanoi-lo-duc"),
    ),
    money_scale=1_000,
    special_space_kinds={4: SPACE_COMMUNITY, 12: SPACE_COMMUNITY},
    tax_amounts={2: 200, 38: 100},
    utility_economy={17: (150, 75), 28: (280, 140)},
)

TERMINOLOGY = BoardTerminology(
    street_kind_key="monopoly-space-kind-hanoi-vendor",
    transit_kind_key="monopoly-space-kind-hanoi-bus-station",
    utility_kind_key="monopoly-space-kind-hanoi-landmark",
    chance_kind_key="monopoly-space-kind-hanoi-lucky-draw",
    community_kind_key="monopoly-space-kind-hanoi-lottery",
    chance_deck_key="monopoly-deck-hanoi-lucky-draw",
    community_deck_key="monopoly-deck-hanoi-lottery",
    utility_rent_schedule_key="monopoly-hanoi-landmark-rent-schedule",
)

DEVELOPMENT = DevelopmentDefinition(
    level_keys=(
        "monopoly-hanoi-development-level-1",
        "monopoly-hanoi-development-level-2",
        "monopoly-hanoi-development-level-3",
        "monopoly-hanoi-development-level-4",
        "monopoly-hanoi-development-level-5",
    ),
    empty_key="monopoly-hanoi-development-none",
    collective_key="monopoly-hanoi-development-collective",
    build_selector_key="monopoly-hanoi-action-upgrade-business",
    sell_selector_key="monopoly-hanoi-action-sell-business-upgrade",
    rent_schedule_key="monopoly-hanoi-rent-schedule",
    bank_supply_key="monopoly-hanoi-development-supply",
    finite_supply=False,
    error_key_overrides=(
        ("monopoly-error-not-your-street", "monopoly-hanoi-error-not-your-vendor"),
        ("monopoly-error-need-color-set", "monopoly-hanoi-error-need-color-set"),
        ("monopoly-error-already-hotel", "monopoly-hanoi-error-fully-developed"),
        (
            "monopoly-error-hotels-require-four-each",
            "monopoly-hanoi-error-final-level-requires-four-each",
        ),
        ("monopoly-error-build-evenly", "monopoly-hanoi-error-build-evenly"),
        (
            "monopoly-error-no-building-to-sell",
            "monopoly-hanoi-error-no-development-to-sell",
        ),
        ("monopoly-error-sell-evenly", "monopoly-hanoi-error-sell-evenly"),
        (
            "monopoly-error-no-sellable-buildings",
            "monopoly-hanoi-error-no-sellable-development",
        ),
        (
            "monopoly-error-no-group-buildings",
            "monopoly-hanoi-error-no-group-development",
        ),
        (
            "monopoly-error-sell-group-buildings-first",
            "monopoly-hanoi-error-sell-group-development-first",
        ),
        (
            "monopoly-error-build-none-no-streets",
            "monopoly-hanoi-error-build-none-no-businesses",
        ),
        (
            "monopoly-error-build-none-no-color-set",
            "monopoly-hanoi-error-build-none-no-color-set",
        ),
        (
            "monopoly-error-build-none-groups-mortgaged",
            "monopoly-hanoi-error-build-none-groups-mortgaged",
        ),
        (
            "monopoly-error-build-none-fully-developed",
            "monopoly-hanoi-error-build-none-fully-developed",
        ),
        (
            "monopoly-error-build-none-developed-or-mortgaged",
            "monopoly-hanoi-error-build-none-developed-or-mortgaged",
        ),
        (
            "monopoly-error-build-none-needs-cash",
            "monopoly-hanoi-error-build-none-needs-cash",
        ),
    ),
)

HANOI_BOARD = BoardDefinition(
    id="hanoi",
    name_key="monopoly-board-hanoi",
    description_key="monopoly-board-hanoi-description",
    currency_key="monopoly-currency-vnd",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="lo_duc",
        red_property_id="hang_hanh",
        pink_property_id="hang_ga",
        named_transit_id="my_dinh_bus_station",
        money_scale=1_000,
        repairs_text_key="monopoly-card-hanoi-lucky-draw-repairs",
    ),
    community_cards=standard_community_cards(
        money_scale=1_000,
        repairs_text_key="monopoly-card-hanoi-lottery-repairs",
    ),
    starting_cash=1_500_000,
    go_salary=200_000,
    snake_eyes_bonus=500_000,
    jail_fine=100_000,
    bank_houses=0,
    bank_hotels=0,
    terminology=TERMINOLOGY,
    development=DEVELOPMENT,
    rules=RuleDefinition(
        auction_opening_bid=10_000,
        auction_bid_increment=5_000,
    ),
)

register_board(HANOI_BOARD)
