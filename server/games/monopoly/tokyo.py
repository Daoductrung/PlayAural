"""Contemporary Tokyo Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("hachioji", "monopoly-space-tokyo-hachioji"),
        ("community_1", "monopoly-space-community-chest"),
        ("tachikawa", "monopoly-space-tokyo-tachikawa"),
        ("income_tax", "monopoly-space-income-tax"),
        ("shinjuku_station", "monopoly-space-tokyo-shinjuku-station"),
        ("yotsuya", "monopoly-space-tokyo-yotsuya"),
        ("chance_1", "monopoly-space-chance"),
        ("yoyogi", "monopoly-space-tokyo-yoyogi"),
        ("ichigaya", "monopoly-space-tokyo-ichigaya"),
        ("jail", "monopoly-space-jail"),
        ("akihabara", "monopoly-space-tokyo-akihabara"),
        ("electric_company", "monopoly-space-electric-company"),
        ("ueno", "monopoly-space-tokyo-ueno"),
        ("ikebukuro", "monopoly-space-tokyo-ikebukuro"),
        ("shinagawa_station", "monopoly-space-tokyo-shinagawa-station"),
        ("odaiba", "monopoly-space-tokyo-odaiba"),
        ("community_2", "monopoly-space-community-chest"),
        ("hibiya", "monopoly-space-tokyo-hibiya"),
        ("shimbashi", "monopoly-space-tokyo-shimbashi"),
        ("free_parking", "monopoly-space-free-parking"),
        ("ebisu", "monopoly-space-tokyo-ebisu"),
        ("chance_2", "monopoly-space-chance"),
        ("harajuku", "monopoly-space-tokyo-harajuku"),
        ("omotesando", "monopoly-space-tokyo-omotesando"),
        ("shibuya_station", "monopoly-space-tokyo-shibuya-station"),
        ("akasaka", "monopoly-space-tokyo-akasaka"),
        ("roppongi", "monopoly-space-tokyo-roppongi"),
        ("water_works", "monopoly-space-water-works"),
        ("toranomon", "monopoly-space-tokyo-toranomon"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("yurakucho", "monopoly-space-tokyo-yurakucho"),
        ("nihonbashi", "monopoly-space-tokyo-nihonbashi"),
        ("community_3", "monopoly-space-community-chest"),
        ("otemachi", "monopoly-space-tokyo-otemachi"),
        ("tokyo_station", "monopoly-space-tokyo-tokyo-station"),
        ("chance_3", "monopoly-space-chance"),
        ("marunouchi", "monopoly-space-tokyo-marunouchi"),
        ("luxury_tax", "monopoly-space-luxury-tax"),
        ("ginza", "monopoly-space-tokyo-ginza"),
    )
)

TOKYO_BOARD = BoardDefinition(
    id="tokyo",
    name_key="monopoly-board-tokyo",
    description_key="monopoly-board-tokyo-description",
    currency_key="monopoly-currency-monopoly-dollar",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="ginza",
        red_property_id="omotesando",
        pink_property_id="akihabara",
        named_transit_id="shinjuku_station",
    ),
    community_cards=standard_community_cards(),
    transit_kind_key="monopoly-space-kind-station",
)

register_board(TOKYO_BOARD)
