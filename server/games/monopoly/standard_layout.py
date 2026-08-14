"""Shared data builders for the standard 40-space regional board layout."""

from __future__ import annotations

from .models import (
    SPACE_CHANCE,
    SPACE_COMMUNITY,
    SPACE_FREE_PARKING,
    SPACE_GO,
    SPACE_GO_TO_JAIL,
    SPACE_JAIL,
    SPACE_STREET,
    SPACE_TAX,
    SPACE_TRANSIT,
    SPACE_UTILITY,
    BoardSpaceDefinition,
    PropertyGroupDefinition,
)

_STANDARD_STREETS: dict[
    int,
    tuple[str, int, int, tuple[int, int, int, int, int, int], int],
] = {
    1: ("brown", 60, 30, (2, 10, 30, 90, 160, 250), 50),
    3: ("brown", 60, 30, (4, 20, 60, 180, 320, 450), 50),
    6: ("light_blue", 100, 50, (6, 30, 90, 270, 400, 550), 50),
    8: ("light_blue", 100, 50, (6, 30, 90, 270, 400, 550), 50),
    9: ("light_blue", 120, 60, (8, 40, 100, 300, 450, 600), 50),
    11: ("pink", 140, 70, (10, 50, 150, 450, 625, 750), 100),
    13: ("pink", 140, 70, (10, 50, 150, 450, 625, 750), 100),
    14: ("pink", 160, 80, (12, 60, 180, 500, 700, 900), 100),
    16: ("orange", 180, 90, (14, 70, 200, 550, 750, 950), 100),
    18: ("orange", 180, 90, (14, 70, 200, 550, 750, 950), 100),
    19: ("orange", 200, 100, (16, 80, 220, 600, 800, 1000), 100),
    21: ("red", 220, 110, (18, 90, 250, 700, 875, 1050), 150),
    23: ("red", 220, 110, (18, 90, 250, 700, 875, 1050), 150),
    24: ("red", 240, 120, (20, 100, 300, 750, 925, 1100), 150),
    26: ("yellow", 260, 130, (22, 110, 330, 800, 975, 1150), 150),
    27: ("yellow", 260, 130, (22, 110, 330, 800, 975, 1150), 150),
    29: ("yellow", 280, 140, (24, 120, 360, 850, 1025, 1200), 150),
    31: ("green", 300, 150, (26, 130, 390, 900, 1100, 1275), 200),
    32: ("green", 300, 150, (26, 130, 390, 900, 1100, 1275), 200),
    34: ("green", 320, 160, (28, 150, 450, 1000, 1200, 1400), 200),
    37: ("dark_blue", 350, 175, (35, 175, 500, 1100, 1300, 1500), 200),
    39: ("dark_blue", 400, 200, (50, 200, 600, 1400, 1700, 2000), 200),
}

_STANDARD_TRANSIT_POSITIONS = {5, 15, 25, 35}
_STANDARD_UTILITY_POSITIONS = {12, 28}
_STANDARD_TAX_AMOUNTS = {4: 200, 38: 100}
_STANDARD_SPACE_KINDS = {
    0: SPACE_GO,
    2: SPACE_COMMUNITY,
    7: SPACE_CHANCE,
    10: SPACE_JAIL,
    17: SPACE_COMMUNITY,
    20: SPACE_FREE_PARKING,
    22: SPACE_CHANCE,
    30: SPACE_GO_TO_JAIL,
    33: SPACE_COMMUNITY,
    36: SPACE_CHANCE,
}


def standard_property_groups(
    transit_name_key: str,
) -> tuple[PropertyGroupDefinition, ...]:
    """Return the standard groups with a board-specific transit label."""

    return (
        PropertyGroupDefinition("brown", "monopoly-group-brown"),
        PropertyGroupDefinition("light_blue", "monopoly-group-light-blue"),
        PropertyGroupDefinition("pink", "monopoly-group-pink"),
        PropertyGroupDefinition("orange", "monopoly-group-orange"),
        PropertyGroupDefinition("red", "monopoly-group-red"),
        PropertyGroupDefinition("yellow", "monopoly-group-yellow"),
        PropertyGroupDefinition("green", "monopoly-group-green"),
        PropertyGroupDefinition("dark_blue", "monopoly-group-dark-blue"),
        PropertyGroupDefinition("transit", transit_name_key),
        PropertyGroupDefinition("utility", "monopoly-group-utilities"),
    )


def build_standard_spaces(
    names: tuple[tuple[str, str], ...],
) -> tuple[BoardSpaceDefinition, ...]:
    """Build one regional edition using the standard layout and deed economy.

    ``names`` contains a stable id and localized name key for each space in
    travel order. Regional boards with different rules remain free to define
    their spaces directly instead of using this template.
    """

    if len(names) != 40:
        raise ValueError("A standard Monopoly layout needs exactly 40 space names")
    spaces: list[BoardSpaceDefinition] = []
    for position, (space_id, name_key) in enumerate(names):
        street = _STANDARD_STREETS.get(position)
        if street:
            group_id, price, mortgage, rents, building_cost = street
            spaces.append(
                BoardSpaceDefinition(
                    id=space_id,
                    name_key=name_key,
                    kind=SPACE_STREET,
                    price=price,
                    mortgage_value=mortgage,
                    group_id=group_id,
                    rents=rents,
                    building_cost=building_cost,
                )
            )
            continue
        if position in _STANDARD_TRANSIT_POSITIONS:
            spaces.append(
                BoardSpaceDefinition(
                    id=space_id,
                    name_key=name_key,
                    kind=SPACE_TRANSIT,
                    price=200,
                    mortgage_value=100,
                    group_id="transit",
                    rents=(25, 50, 100, 200),
                )
            )
            continue
        if position in _STANDARD_UTILITY_POSITIONS:
            spaces.append(
                BoardSpaceDefinition(
                    id=space_id,
                    name_key=name_key,
                    kind=SPACE_UTILITY,
                    price=150,
                    mortgage_value=75,
                    group_id="utility",
                )
            )
            continue
        if position in _STANDARD_TAX_AMOUNTS:
            spaces.append(
                BoardSpaceDefinition(
                    space_id,
                    name_key,
                    SPACE_TAX,
                    tax_amount=_STANDARD_TAX_AMOUNTS[position],
                )
            )
            continue
        spaces.append(
            BoardSpaceDefinition(
                space_id,
                name_key,
                _STANDARD_SPACE_KINDS[position],
            )
        )
    return tuple(spaces)
