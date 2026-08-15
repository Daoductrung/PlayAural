"""Standard Italian Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition, BoardTerminology
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("vicolo_corto", "monopoly-space-italy-vicolo-corto"),
        ("community_1", "monopoly-space-community-chest"),
        ("vicolo_stretto", "monopoly-space-italy-vicolo-stretto"),
        ("income_tax", "monopoly-space-italy-income-tax"),
        ("stazione_sud", "monopoly-space-italy-stazione-sud"),
        ("bastioni_gran_sasso", "monopoly-space-italy-bastioni-gran-sasso"),
        ("chance_1", "monopoly-space-chance"),
        ("viale_monterosa", "monopoly-space-italy-viale-monterosa"),
        ("viale_vesuvio", "monopoly-space-italy-viale-vesuvio"),
        ("jail", "monopoly-space-jail"),
        ("via_accademia", "monopoly-space-italy-via-accademia"),
        ("electric_company", "monopoly-space-italy-electric-company"),
        ("corso_ateneo", "monopoly-space-italy-corso-ateneo"),
        ("piazza_universita", "monopoly-space-italy-piazza-universita"),
        ("stazione_ovest", "monopoly-space-italy-stazione-ovest"),
        ("via_verdi", "monopoly-space-italy-via-verdi"),
        ("community_2", "monopoly-space-community-chest"),
        ("corso_raffaello", "monopoly-space-italy-corso-raffaello"),
        ("piazza_dante", "monopoly-space-italy-piazza-dante"),
        ("free_parking", "monopoly-space-free-parking"),
        ("via_marco_polo", "monopoly-space-italy-via-marco-polo"),
        ("chance_2", "monopoly-space-chance"),
        ("corso_magellano", "monopoly-space-italy-corso-magellano"),
        ("largo_colombo", "monopoly-space-italy-largo-colombo"),
        ("stazione_nord", "monopoly-space-italy-stazione-nord"),
        ("viale_costantino", "monopoly-space-italy-viale-costantino"),
        ("viale_traiano", "monopoly-space-italy-viale-traiano"),
        ("water_works", "monopoly-space-italy-water-works"),
        ("piazza_giulio_cesare", "monopoly-space-italy-piazza-giulio-cesare"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("via_roma", "monopoly-space-italy-via-roma"),
        ("corso_impero", "monopoly-space-italy-corso-impero"),
        ("community_3", "monopoly-space-community-chest"),
        ("largo_augusto", "monopoly-space-italy-largo-augusto"),
        ("stazione_est", "monopoly-space-italy-stazione-est"),
        ("chance_3", "monopoly-space-chance"),
        ("viale_dei_giardini", "monopoly-space-italy-viale-dei-giardini"),
        ("luxury_tax", "monopoly-space-italy-luxury-tax"),
        ("parco_della_vittoria", "monopoly-space-italy-parco-della-vittoria"),
    )
)

ITALY_BOARD = BoardDefinition(
    id="italy",
    name_key="monopoly-board-italy",
    description_key="monopoly-board-italy-description",
    currency_key="monopoly-currency-eur",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="parco_della_vittoria",
        red_property_id="largo_colombo",
        pink_property_id="via_accademia",
        named_transit_id="stazione_sud",
    ),
    community_cards=standard_community_cards(),
    terminology=BoardTerminology(transit_kind_key="monopoly-space-kind-station"),
)

register_board(ITALY_BOARD)
