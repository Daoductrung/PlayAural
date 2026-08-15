"""Standard Paris Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition, BoardTerminology
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("boulevard_belleville", "monopoly-space-paris-boulevard-belleville"),
        ("community_1", "monopoly-space-community-chest"),
        ("rue_lecourbe", "monopoly-space-paris-rue-lecourbe"),
        ("income_tax", "monopoly-space-income-tax"),
        ("gare_montparnasse", "monopoly-space-paris-gare-montparnasse"),
        ("rue_vaugirard", "monopoly-space-paris-rue-vaugirard"),
        ("chance_1", "monopoly-space-chance"),
        ("rue_courcelles", "monopoly-space-paris-rue-courcelles"),
        ("avenue_republique", "monopoly-space-paris-avenue-republique"),
        ("jail", "monopoly-space-jail"),
        ("boulevard_villette", "monopoly-space-paris-boulevard-villette"),
        ("electric_company", "monopoly-space-paris-electric-company"),
        ("avenue_neuilly", "monopoly-space-paris-avenue-neuilly"),
        ("rue_paradis", "monopoly-space-paris-rue-paradis"),
        ("gare_lyon", "monopoly-space-paris-gare-lyon"),
        ("avenue_mozart", "monopoly-space-paris-avenue-mozart"),
        ("community_2", "monopoly-space-community-chest"),
        ("boulevard_saint_michel", "monopoly-space-paris-boulevard-saint-michel"),
        ("place_pigalle", "monopoly-space-paris-place-pigalle"),
        ("free_parking", "monopoly-space-free-parking"),
        ("avenue_matignon", "monopoly-space-paris-avenue-matignon"),
        ("chance_2", "monopoly-space-chance"),
        ("boulevard_malesherbes", "monopoly-space-paris-boulevard-malesherbes"),
        ("avenue_henri_martin", "monopoly-space-paris-avenue-henri-martin"),
        ("gare_nord", "monopoly-space-paris-gare-nord"),
        ("faubourg_saint_honore", "monopoly-space-paris-faubourg-saint-honore"),
        ("place_bourse", "monopoly-space-paris-place-bourse"),
        ("water_company", "monopoly-space-paris-water-company"),
        ("rue_la_fayette", "monopoly-space-paris-rue-la-fayette"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("avenue_breteuil", "monopoly-space-paris-avenue-breteuil"),
        ("avenue_foch", "monopoly-space-paris-avenue-foch"),
        ("community_3", "monopoly-space-community-chest"),
        ("boulevard_capucines", "monopoly-space-paris-boulevard-capucines"),
        ("gare_saint_lazare", "monopoly-space-paris-gare-saint-lazare"),
        ("chance_3", "monopoly-space-chance"),
        ("avenue_champs_elysees", "monopoly-space-paris-avenue-champs-elysees"),
        ("luxury_tax", "monopoly-space-luxury-tax"),
        ("rue_paix", "monopoly-space-paris-rue-paix"),
    )
)

PARIS_BOARD = BoardDefinition(
    id="paris",
    name_key="monopoly-board-paris",
    description_key="monopoly-board-paris-description",
    currency_key="monopoly-currency-eur",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="rue_paix",
        red_property_id="avenue_henri_martin",
        pink_property_id="boulevard_villette",
        named_transit_id="gare_lyon",
    ),
    community_cards=standard_community_cards(),
    terminology=BoardTerminology(transit_kind_key="monopoly-space-kind-station"),
)

register_board(PARIS_BOARD)
