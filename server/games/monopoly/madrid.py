"""Classic Madrid Monopoly board content."""

from __future__ import annotations

from .boards import register_board
from .models import BoardDefinition, BoardTerminology
from .standard_cards import standard_chance_cards, standard_community_cards
from .standard_layout import build_standard_spaces, standard_property_groups

PROPERTY_GROUPS = standard_property_groups("monopoly-group-stations")

SPACES = build_standard_spaces(
    (
        ("go", "monopoly-space-go"),
        ("ronda_valencia", "monopoly-space-madrid-ronda-valencia"),
        ("community_1", "monopoly-space-community-chest"),
        ("plaza_lavapies", "monopoly-space-madrid-plaza-lavapies"),
        ("income_tax", "monopoly-space-madrid-income-tax"),
        ("estacion_goya", "monopoly-space-madrid-estacion-goya"),
        ("glorieta_cuatro_caminos", "monopoly-space-madrid-cuatro-caminos"),
        ("chance_1", "monopoly-space-chance"),
        ("avenida_reina_victoria", "monopoly-space-madrid-reina-victoria"),
        ("calle_bravo_murillo", "monopoly-space-madrid-bravo-murillo"),
        ("jail", "monopoly-space-jail"),
        ("glorieta_bilbao", "monopoly-space-madrid-glorieta-bilbao"),
        ("electric_company", "monopoly-space-madrid-electric-company"),
        ("calle_alberto_aguilera", "monopoly-space-madrid-alberto-aguilera"),
        ("calle_fuencarral", "monopoly-space-madrid-fuencarral"),
        ("estacion_delicias", "monopoly-space-madrid-estacion-delicias"),
        ("avenida_felipe_ii", "monopoly-space-madrid-felipe-ii"),
        ("community_2", "monopoly-space-community-chest"),
        ("calle_velazquez", "monopoly-space-madrid-velazquez"),
        ("calle_serrano", "monopoly-space-madrid-serrano"),
        ("free_parking", "monopoly-space-free-parking"),
        ("avenida_america", "monopoly-space-madrid-avenida-america"),
        ("chance_2", "monopoly-space-chance"),
        ("calle_maria_molina", "monopoly-space-madrid-maria-molina"),
        ("calle_cea_bermudez", "monopoly-space-madrid-cea-bermudez"),
        ("estacion_mediodia", "monopoly-space-madrid-estacion-mediodia"),
        ("avenida_reyes_catolicos", "monopoly-space-madrid-reyes-catolicos"),
        ("calle_bailen", "monopoly-space-madrid-bailen"),
        ("water_works", "monopoly-space-madrid-water-works"),
        ("plaza_espana", "monopoly-space-madrid-plaza-espana"),
        ("go_to_jail", "monopoly-space-go-to-jail"),
        ("puerta_sol", "monopoly-space-madrid-puerta-sol"),
        ("calle_alcala", "monopoly-space-madrid-alcala"),
        ("community_3", "monopoly-space-community-chest"),
        ("gran_via", "monopoly-space-madrid-gran-via"),
        ("estacion_norte", "monopoly-space-madrid-estacion-norte"),
        ("chance_3", "monopoly-space-chance"),
        ("paseo_castellana", "monopoly-space-madrid-paseo-castellana"),
        ("luxury_tax", "monopoly-space-madrid-luxury-tax"),
        ("paseo_prado", "monopoly-space-madrid-paseo-prado"),
    )
)

MADRID_BOARD = BoardDefinition(
    id="madrid",
    name_key="monopoly-board-madrid",
    description_key="monopoly-board-madrid-description",
    currency_key="monopoly-currency-eur",
    property_groups=PROPERTY_GROUPS,
    spaces=SPACES,
    chance_cards=standard_chance_cards(
        top_property_id="paseo_prado",
        red_property_id="calle_cea_bermudez",
        pink_property_id="glorieta_bilbao",
        named_transit_id="estacion_goya",
    ),
    community_cards=standard_community_cards(),
    terminology=BoardTerminology(transit_kind_key="monopoly-space-kind-station"),
)

register_board(MADRID_BOARD)
