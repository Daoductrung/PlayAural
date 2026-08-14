"""Standard London Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("old_kent_road", "monopoly-space-london-old-kent-road"),
        ("community_1", "monopoly-space-community-chest"),
        ("whitechapel_road", "monopoly-space-london-whitechapel-road"),
        ("income_tax", "monopoly-space-income-tax"),
        ("kings_cross_station", "monopoly-space-london-kings-cross-station"),
        ("angel_islington", "monopoly-space-london-angel-islington"),
        ("chance_1", "monopoly-space-chance"),
        ("euston_road", "monopoly-space-london-euston-road"),
        ("pentonville_road", "monopoly-space-london-pentonville-road"),
        ("jail", "monopoly-space-jail"),
        ("pall_mall", "monopoly-space-london-pall-mall"),
        ("electric_company", "monopoly-space-electric-company"),
        ("whitehall", "monopoly-space-london-whitehall"),
        ("northumberland_avenue", "monopoly-space-london-northumberland-avenue"),
        ("marylebone_station", "monopoly-space-london-marylebone-station"),
        ("bow_street", "monopoly-space-london-bow-street"),
        ("community_2", "monopoly-space-community-chest"),
        ("marlborough_street", "monopoly-space-london-marlborough-street"),
        ("vine_street", "monopoly-space-london-vine-street"),
        ("free_parking", "monopoly-space-free-parking"),
        ("strand", "monopoly-space-london-strand"),
        ("chance_2", "monopoly-space-chance"),
        ("fleet_street", "monopoly-space-london-fleet-street"),
        ("trafalgar_square", "monopoly-space-london-trafalgar-square"),
        ("fenchurch_station", "monopoly-space-london-fenchurch-street-station"),
        ("leicester_square", "monopoly-space-london-leicester-square"),
        ("coventry_street", "monopoly-space-london-coventry-street"),
        ("water_works", "monopoly-space-water-works"),
        ("piccadilly", "monopoly-space-london-piccadilly"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("regent_street", "monopoly-space-london-regent-street"),
        ("oxford_street", "monopoly-space-london-oxford-street"),
        ("community_3", "monopoly-space-community-chest"),
        ("bond_street", "monopoly-space-london-bond-street"),
        ("liverpool_street_station", "monopoly-space-london-liverpool-street-station"),
        ("chance_3", "monopoly-space-chance"),
        ("park_lane", "monopoly-space-london-park-lane"),
        ("super_tax", "monopoly-space-london-super-tax"),
        ("mayfair", "monopoly-space-london-mayfair"),
    )
)

LONDON_BOARD = BoardDefinition(
    id="london",
    name_key="monopoly-board-london",
    description_key="monopoly-board-london-description",
    currency_key="monopoly-currency-gbp",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="mayfair",
        red_property_id="trafalgar_square",
        pink_property_id="pall_mall",
        named_transit_id="kings_cross_station",
    ),
    community_cards=standard_community_cards(),
    transit_kind_key="monopoly-space-kind-station",
)

register_board(LONDON_BOARD)
