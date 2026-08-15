"""New Zealand national Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition, BoardTerminology
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("palmerston_street", "monopoly-space-new-zealand-palmerston-street"),
        ("community_1", "monopoly-space-community-chest"),
        ("mackay_street", "monopoly-space-new-zealand-mackay-street"),
        ("income_tax", "monopoly-space-income-tax"),
        ("balclutha_station", "monopoly-space-new-zealand-balclutha-station"),
        ("east_street", "monopoly-space-new-zealand-east-street"),
        ("chance_1", "monopoly-space-chance"),
        ("stafford_street", "monopoly-space-new-zealand-stafford-street"),
        ("thames_street", "monopoly-space-new-zealand-thames-street"),
        ("jail", "monopoly-space-jail"),
        ("gladstone_road", "monopoly-space-new-zealand-gladstone-road"),
        ("electric_company", "monopoly-space-electric-company"),
        ("marine_parade", "monopoly-space-new-zealand-marine-parade"),
        ("bank_street", "monopoly-space-new-zealand-bank-street"),
        ("taumarunui_station", "monopoly-space-new-zealand-taumarunui-station"),
        ("devon_street", "monopoly-space-new-zealand-devon-street"),
        ("community_2", "monopoly-space-community-chest"),
        ("rangitikei_street", "monopoly-space-new-zealand-rangitikei-street"),
        ("victoria_avenue", "monopoly-space-new-zealand-victoria-avenue"),
        ("free_parking", "monopoly-space-free-parking"),
        ("high_street", "monopoly-space-new-zealand-high-street"),
        ("chance_2", "monopoly-space-chance"),
        ("market_street", "monopoly-space-new-zealand-market-street"),
        ("trafalgar_street", "monopoly-space-new-zealand-trafalgar-street"),
        ("kaikoura_station", "monopoly-space-new-zealand-kaikoura-station"),
        ("cameron_road", "monopoly-space-new-zealand-cameron-road"),
        ("fenton_street", "monopoly-space-new-zealand-fenton-street"),
        ("water_works", "monopoly-space-water-works"),
        ("garden_place", "monopoly-space-new-zealand-garden-place"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("dee_street", "monopoly-space-new-zealand-dee-street"),
        ("princes_street", "monopoly-space-new-zealand-princes-street"),
        ("community_3", "monopoly-space-community-chest"),
        ("cathedral_square", "monopoly-space-new-zealand-cathedral-square"),
        ("frankton_junction", "monopoly-space-new-zealand-frankton-junction"),
        ("chance_3", "monopoly-space-chance"),
        ("lambton_quay", "monopoly-space-new-zealand-lambton-quay"),
        ("super_tax", "monopoly-space-new-zealand-super-tax"),
        ("queen_street", "monopoly-space-new-zealand-queen-street"),
    )
)

NEW_ZEALAND_BOARD = BoardDefinition(
    id="new_zealand",
    name_key="monopoly-board-new-zealand",
    description_key="monopoly-board-new-zealand-description",
    currency_key="monopoly-currency-nzd",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="queen_street",
        red_property_id="trafalgar_street",
        pink_property_id="gladstone_road",
        named_transit_id="balclutha_station",
    ),
    community_cards=standard_community_cards(),
    terminology=BoardTerminology(transit_kind_key="monopoly-space-kind-station"),
)

register_board(NEW_ZEALAND_BOARD)
