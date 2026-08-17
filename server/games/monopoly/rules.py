"""Pure Monopoly economic and building-rule helpers."""

from __future__ import annotations

from collections.abc import Mapping

from .models import (
    SPACE_STREET,
    SPACE_TRANSIT,
    SPACE_UTILITY,
    BoardDefinition,
    BoardSpaceDefinition,
    PropertyState,
)


def unmortgage_cost(mortgage_value: int, interest_percent: int = 10) -> int:
    """Return principal plus the configured interest."""
    return (mortgage_value * (100 + interest_percent) + 99) // 100


def transfer_mortgage_interest(mortgage_value: int, interest_percent: int = 10) -> int:
    """Return configured interest due when mortgaged property changes owner."""
    return (mortgage_value * interest_percent + 99) // 100


def owns_group(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    owner_id: str,
    group_id: str,
) -> bool:
    spaces = board.group_spaces(group_id)
    return bool(spaces) and all(
        property_states.get(space.id, PropertyState()).owner_id == owner_id
        for space in spaces
    )


def calculate_rent(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    space: BoardSpaceDefinition,
    dice_total: int,
    *,
    rent_multiplier: int = 1,
    utility_override: bool = False,
) -> int:
    state = property_states[space.id]
    if not state.owner_id or state.mortgaged:
        return 0

    if space.kind == SPACE_STREET:
        if state.buildings:
            rent = space.rents[state.buildings]
        else:
            rent = space.rents[0]
            if owns_group(board, property_states, state.owner_id, space.group_id):
                rent *= 2
        return rent * max(1, rent_multiplier)

    owned_count = sum(
        1
        for group_space in board.group_spaces(space.group_id)
        if property_states[group_space.id].owner_id == state.owner_id
    )
    if space.kind == SPACE_TRANSIT:
        return space.rents[max(0, owned_count - 1)] * max(1, rent_multiplier)
    if space.kind == SPACE_UTILITY:
        factor = (
            max(1, rent_multiplier)
            if utility_override
            else (
                board.rules.utility_complete_group_multiplier
                if owned_count == len(board.group_spaces(space.group_id))
                else board.rules.utility_single_multiplier
            )
        )
        return max(0, dice_total) * factor * board.rules.utility_dice_unit
    return 0


def can_build(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    property_id: str,
    owner_id: str,
    bank_houses: int,
    bank_hotels: int,
) -> str | None:
    space = board.space(property_id)
    state = property_states[property_id]
    if space.kind != SPACE_STREET or state.owner_id != owner_id:
        return "monopoly-error-not-your-street"
    group = board.group_spaces(space.group_id)
    if not owns_group(board, property_states, owner_id, space.group_id):
        return "monopoly-error-need-color-set"
    if any(property_states[item.id].mortgaged for item in group):
        return "monopoly-error-group-mortgaged"
    levels = [property_states[item.id].buildings for item in group]
    if state.buildings >= 5:
        return "monopoly-error-already-hotel"
    if state.buildings == 4:
        if any(level < 4 for level in levels):
            return "monopoly-error-hotels-require-four-each"
        if board.development.finite_supply and bank_hotels < 1:
            return "monopoly-error-no-hotels"
        return None
    if state.buildings != min(levels):
        return "monopoly-error-build-evenly"
    if board.development.finite_supply and bank_houses < 1:
        return "monopoly-error-no-houses"
    return None


def can_sell_building(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    property_id: str,
    owner_id: str,
    bank_houses: int,
) -> str | None:
    space = board.space(property_id)
    state = property_states[property_id]
    if space.kind != SPACE_STREET or state.owner_id != owner_id:
        return "monopoly-error-not-your-street"
    if state.buildings <= 0:
        return "monopoly-error-no-building-to-sell"
    levels = [
        property_states[item.id].buildings
        for item in board.group_spaces(space.group_id)
    ]
    if state.buildings != max(levels):
        return "monopoly-error-sell-evenly"
    if (
        board.development.finite_supply
        and state.buildings == 5
        and bank_houses < 4
    ):
        return "monopoly-error-bank-needs-four-houses"
    return None


def can_mortgage(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    property_id: str,
    owner_id: str,
) -> str | None:
    space = board.space(property_id)
    state = property_states[property_id]
    if state.owner_id != owner_id:
        return "monopoly-error-not-your-property"
    if state.mortgaged:
        return "monopoly-error-already-mortgaged"
    if space.kind == SPACE_STREET and any(
        property_states[item.id].buildings
        for item in board.group_spaces(space.group_id)
    ):
        return "monopoly-error-sell-group-buildings-first"
    return None


def liquid_assets(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    owner_id: str,
    cash: int,
) -> int:
    """Return cash plus money still available from buildings and mortgages."""
    total = cash
    for space in board.spaces:
        state = property_states.get(space.id)
        if not state or state.owner_id != owner_id:
            continue
        if not state.mortgaged:
            total += space.mortgage_value
        if state.buildings:
            total += state.buildings * (
                space.building_cost * board.rules.building_sale_percent // 100
            )
    return total


def net_worth(
    board: BoardDefinition,
    property_states: Mapping[str, PropertyState],
    owner_id: str,
    cash: int,
) -> int:
    """Return the standard purchase-price valuation used for summaries."""
    total = cash
    for space in board.spaces:
        state = property_states.get(space.id)
        if not state or state.owner_id != owner_id:
            continue
        total += space.mortgage_value if state.mortgaged else space.price
        total += state.buildings * space.building_cost
    return total
