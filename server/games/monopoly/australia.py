"""Classic Australian Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition, BoardTerminology
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("todd_street", "monopoly-space-australia-todd-street"),
        ("community_1", "monopoly-space-community-chest"),
        ("smith_street", "monopoly-space-australia-smith-street"),
        ("income_tax", "monopoly-space-income-tax"),
        ("perth_station", "monopoly-space-australia-perth-station"),
        ("salamanca_place", "monopoly-space-australia-salamanca-place"),
        ("chance_1", "monopoly-space-chance"),
        ("davey_street", "monopoly-space-australia-davey-street"),
        ("macquarie_street", "monopoly-space-australia-macquarie-street"),
        ("jail", "monopoly-space-jail"),
        ("william_street", "monopoly-space-australia-william-street"),
        ("australia_post", "monopoly-space-australia-australia-post"),
        ("barrack_street", "monopoly-space-australia-barrack-street"),
        ("hay_street", "monopoly-space-australia-hay-street"),
        ("adelaide_station", "monopoly-space-australia-adelaide-station"),
        ("north_terrace", "monopoly-space-australia-north-terrace"),
        ("community_2", "monopoly-space-community-chest"),
        ("victoria_square", "monopoly-space-australia-victoria-square"),
        ("rundle_mall", "monopoly-space-australia-rundle-mall"),
        ("free_parking", "monopoly-space-free-parking"),
        ("stanley_street", "monopoly-space-australia-stanley-street"),
        ("chance_2", "monopoly-space-chance"),
        ("petries_bight", "monopoly-space-australia-petries-bight"),
        ("wickham_terrace", "monopoly-space-australia-wickham-terrace"),
        (
            "flinders_street_station",
            "monopoly-space-australia-flinders-street-station",
        ),
        ("collins_street", "monopoly-space-australia-collins-street"),
        ("elizabeth_street", "monopoly-space-australia-elizabeth-street"),
        ("telecom_australia", "monopoly-space-australia-telecom-australia"),
        ("bourke_street", "monopoly-space-australia-bourke-street"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("castlereagh_street", "monopoly-space-australia-castlereagh-street"),
        ("george_street", "monopoly-space-australia-george-street"),
        ("community_3", "monopoly-space-community-chest"),
        ("pitt_street", "monopoly-space-australia-pitt-street"),
        ("sydney_station", "monopoly-space-australia-sydney-station"),
        ("chance_3", "monopoly-space-chance"),
        ("flinders_way", "monopoly-space-australia-flinders-way"),
        ("super_tax", "monopoly-space-australia-super-tax"),
        ("kings_avenue", "monopoly-space-australia-kings-avenue"),
    )
)

AUSTRALIA_BOARD = BoardDefinition(
    id="australia",
    name_key="monopoly-board-australia",
    description_key="monopoly-board-australia-description",
    currency_key="monopoly-currency-aud",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="kings_avenue",
        red_property_id="wickham_terrace",
        pink_property_id="william_street",
        named_transit_id="perth_station",
    ),
    community_cards=standard_community_cards(),
    terminology=BoardTerminology(transit_kind_key="monopoly-space-kind-station"),
)

register_board(AUSTRALIA_BOARD)
