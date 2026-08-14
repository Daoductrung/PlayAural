"""Standard German Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("badstrasse", "monopoly-space-germany-badstrasse"),
        ("community_1", "monopoly-space-community-chest"),
        ("turmstrasse", "monopoly-space-germany-turmstrasse"),
        ("income_tax", "monopoly-space-income-tax"),
        ("suedbahnhof", "monopoly-space-germany-suedbahnhof"),
        ("chausseestrasse", "monopoly-space-germany-chausseestrasse"),
        ("chance_1", "monopoly-space-chance"),
        ("elisenstrasse", "monopoly-space-germany-elisenstrasse"),
        ("poststrasse", "monopoly-space-germany-poststrasse"),
        ("jail", "monopoly-space-jail"),
        ("seestrasse", "monopoly-space-germany-seestrasse"),
        ("elektrizitaetswerk", "monopoly-space-germany-elektrizitaetswerk"),
        ("hafenstrasse", "monopoly-space-germany-hafenstrasse"),
        ("neue_strasse", "monopoly-space-germany-neue-strasse"),
        ("westbahnhof", "monopoly-space-germany-westbahnhof"),
        ("muenchner_strasse", "monopoly-space-germany-muenchner-strasse"),
        ("community_2", "monopoly-space-community-chest"),
        ("wiener_strasse", "monopoly-space-germany-wiener-strasse"),
        ("berliner_strasse", "monopoly-space-germany-berliner-strasse"),
        ("free_parking", "monopoly-space-free-parking"),
        ("theaterstrasse", "monopoly-space-germany-theaterstrasse"),
        ("chance_2", "monopoly-space-chance"),
        ("museumstrasse", "monopoly-space-germany-museumstrasse"),
        ("opernplatz", "monopoly-space-germany-opernplatz"),
        ("nordbahnhof", "monopoly-space-germany-nordbahnhof"),
        ("lessingstrasse", "monopoly-space-germany-lessingstrasse"),
        ("schillerstrasse", "monopoly-space-germany-schillerstrasse"),
        ("wasserwerk", "monopoly-space-germany-wasserwerk"),
        ("goethestrasse", "monopoly-space-germany-goethestrasse"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("rathausplatz", "monopoly-space-germany-rathausplatz"),
        ("hauptstrasse", "monopoly-space-germany-hauptstrasse"),
        ("community_3", "monopoly-space-community-chest"),
        ("bahnhofstrasse", "monopoly-space-germany-bahnhofstrasse"),
        ("hauptbahnhof", "monopoly-space-germany-hauptbahnhof"),
        ("chance_3", "monopoly-space-chance"),
        ("parkstrasse", "monopoly-space-germany-parkstrasse"),
        ("additional_tax", "monopoly-space-germany-additional-tax"),
        ("schlossallee", "monopoly-space-germany-schlossallee"),
    )
)

GERMANY_BOARD = BoardDefinition(
    id="germany",
    name_key="monopoly-board-germany",
    description_key="monopoly-board-germany-description",
    currency_key="monopoly-currency-eur",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="schlossallee",
        red_property_id="opernplatz",
        pink_property_id="seestrasse",
        named_transit_id="suedbahnhof",
    ),
    community_cards=standard_community_cards(),
    transit_kind_key="monopoly-space-kind-station",
)

register_board(GERMANY_BOARD)
