"""Standard United States Monopoly board content and implementation template."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-railroads")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("mediterranean", "monopoly-space-mediterranean"),
        ("community_1", "monopoly-space-community-chest"),
        ("baltic", "monopoly-space-baltic"),
        ("income_tax", "monopoly-space-income-tax"),
        ("reading_railroad", "monopoly-space-reading-railroad"),
        ("oriental", "monopoly-space-oriental"),
        ("chance_1", "monopoly-space-chance"),
        ("vermont", "monopoly-space-vermont"),
        ("connecticut", "monopoly-space-connecticut"),
        ("jail", "monopoly-space-jail"),
        ("st_charles", "monopoly-space-st-charles"),
        ("electric_company", "monopoly-space-electric-company"),
        ("states", "monopoly-space-states"),
        ("virginia", "monopoly-space-virginia"),
        ("pennsylvania_railroad", "monopoly-space-pennsylvania-railroad"),
        ("st_james", "monopoly-space-st-james"),
        ("community_2", "monopoly-space-community-chest"),
        ("tennessee", "monopoly-space-tennessee"),
        ("new_york", "monopoly-space-new-york"),
        ("free_parking", "monopoly-space-free-parking"),
        ("kentucky", "monopoly-space-kentucky"),
        ("chance_2", "monopoly-space-chance"),
        ("indiana", "monopoly-space-indiana"),
        ("illinois", "monopoly-space-illinois"),
        ("bo_railroad", "monopoly-space-bo-railroad"),
        ("atlantic", "monopoly-space-atlantic"),
        ("ventnor", "monopoly-space-ventnor"),
        ("water_works", "monopoly-space-water-works"),
        ("marvin_gardens", "monopoly-space-marvin-gardens"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("pacific", "monopoly-space-pacific"),
        ("north_carolina", "monopoly-space-north-carolina"),
        ("community_3", "monopoly-space-community-chest"),
        ("pennsylvania_avenue", "monopoly-space-pennsylvania-avenue"),
        ("short_line", "monopoly-space-short-line"),
        ("chance_3", "monopoly-space-chance"),
        ("park_place", "monopoly-space-park-place"),
        ("luxury_tax", "monopoly-space-luxury-tax"),
        ("boardwalk", "monopoly-space-boardwalk"),
    )
)

STANDARD_BOARD = BoardDefinition(
    id="standard",
    name_key="monopoly-board-standard",
    description_key="monopoly-board-standard-description",
    currency_key="monopoly-currency-usd",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="boardwalk",
        red_property_id="illinois",
        pink_property_id="st_charles",
        named_transit_id="reading_railroad",
    ),
    community_cards=standard_community_cards(),
)

register_board(STANDARD_BOARD)
