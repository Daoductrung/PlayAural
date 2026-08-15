"""Deterministic, board-agnostic Monopoly bot valuation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from functools import lru_cache

from .models import (
    CARD_BACK,
    CARD_GO_TO_JAIL,
    CARD_MOVE,
    CARD_NEAREST,
    SPACE_CHANCE,
    SPACE_COMMUNITY,
    SPACE_GO_TO_JAIL,
    SPACE_STREET,
    SPACE_TRANSIT,
    SPACE_UTILITY,
    BoardDefinition,
    BoardSpaceDefinition,
    PropertyState,
)
from .rules import calculate_rent, owns_group

_DICE_TOTALS = (
    (2, 1),
    (3, 2),
    (4, 3),
    (5, 4),
    (6, 5),
    (7, 6),
    (8, 5),
    (9, 4),
    (10, 3),
    (11, 2),
    (12, 1),
)


def _nearest_space_index(
    board: BoardDefinition,
    start: int,
    kind: str,
) -> int:
    for offset in range(1, len(board.spaces) + 1):
        index = (start + offset) % len(board.spaces)
        if board.spaces[index].kind == kind:
            return index
    return start


def _card_destinations(
    board: BoardDefinition,
    position: int,
    *,
    deck_id: str,
    depth: int,
) -> tuple[tuple[int, float], ...]:
    """Return the board positions produced by one uniformly drawn card.

    This deliberately models only movement because it is used to estimate
    traffic, not to simulate money or deck order. The standard decks contain
    repeated non-movement outcomes as separate cards, so their probability is
    retained automatically. A backwards move may resolve the square it reaches
    (notably Chance's "back three" into Community Chest).
    """

    cards = board.chance_cards if deck_id == "chance" else board.community_cards
    if not cards:
        return ((position, 1.0),)
    weight = 1.0 / len(cards)
    destinations: list[tuple[int, float]] = []
    for card in cards:
        destination = position
        if card.action == CARD_MOVE and card.destination_id:
            destination = board.space_index(card.destination_id)
        elif card.action == CARD_BACK:
            destination = (position - card.amount) % len(board.spaces)
        elif card.action == CARD_NEAREST:
            destination = _nearest_space_index(board, position, card.nearest_kind)
        elif card.action == CARD_GO_TO_JAIL:
            destination = board.space_index(board.jail_space_id)

        reached = board.spaces[destination]
        if card.action in {CARD_MOVE, CARD_BACK, CARD_NEAREST} and reached.kind in {
            SPACE_CHANCE,
            SPACE_COMMUNITY,
            SPACE_GO_TO_JAIL,
        }:
            for final, nested_weight in _resolved_destinations(
                board,
                destination,
                depth=depth + 1,
            ):
                destinations.append((final, weight * nested_weight))
        else:
            destinations.append((destination, weight))
    return tuple(destinations)


def _resolved_destinations(
    board: BoardDefinition,
    position: int,
    *,
    depth: int = 0,
) -> tuple[tuple[int, float], ...]:
    if depth >= 4:
        return ((position, 1.0),)
    space = board.spaces[position]
    if space.kind == SPACE_GO_TO_JAIL:
        return ((board.space_index(board.jail_space_id), 1.0),)
    if space.kind == SPACE_CHANCE:
        return _card_destinations(board, position, deck_id="chance", depth=depth)
    if space.kind == SPACE_COMMUNITY:
        return _card_destinations(board, position, deck_id="community", depth=depth)
    return ((position, 1.0),)


@lru_cache(maxsize=16)
def board_landing_weights(board: BoardDefinition) -> tuple[float, ...]:
    """Estimate long-run landing traffic from board and card definitions.

    The compact Markov model is intentionally board-agnostic: future regional
    boards get useful valuations from their own layout and movement cards with
    no color-group or street-name special cases. It is a strategy heuristic,
    not authoritative gameplay state, so deck order and jail choices remain in
    the game engine rather than this calculation.
    """

    size = len(board.spaces)
    if not size:
        return ()
    probabilities = [0.0] * size
    probabilities[board.space_index(board.go_space_id)] = 1.0
    for _ in range(256):
        next_probabilities = [0.0] * size
        for start, probability in enumerate(probabilities):
            if not probability:
                continue
            for total, combinations in _DICE_TOTALS:
                rolled = (start + total) % size
                for destination, resolution_weight in _resolved_destinations(
                    board, rolled
                ):
                    next_probabilities[destination] += (
                        probability * combinations * resolution_weight / 36.0
                    )
        if (
            max(
                abs(left - right)
                for left, right in zip(probabilities, next_probabilities, strict=True)
            )
            < 1e-12
        ):
            probabilities = next_probabilities
            break
        probabilities = next_probabilities
    total_probability = sum(probabilities)
    if not total_probability:
        return tuple(1.0 for _ in board.spaces)
    # One is average traffic. This makes the score comparable across boards
    # with different numbers of spaces.
    return tuple(
        probability * size / total_probability for probability in probabilities
    )


def landing_weight(board: BoardDefinition, property_id: str) -> float:
    """Return relative traffic for one space; 1.0 is the board average."""

    weights = board_landing_weights(board)
    return weights[board.space_index(property_id)] if weights else 1.0


def cash_reserve(board: BoardDefinition) -> int:
    """Return the baseline safety buffer for the selected board's economy."""

    return max(1, board.starting_cash // 6)


def acquisition_cash_reserve(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
    *,
    completes_group: bool,
) -> int:
    """Return the liquidity a bot keeps after buying a deed.

    Completing a group justifies taking more risk, but never spending the
    baseline emergency reserve.  This prevents an auction win from forcing an
    immediate mortgage while remaining board-agnostic across currencies.
    """

    risk_reserve = risk_adjusted_cash_reserve(board, states, player_id)
    if not completes_group:
        return risk_reserve
    return max(cash_reserve(board), risk_reserve * 3 // 4)


def risk_adjusted_cash_reserve(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
) -> int:
    """Keep enough liquidity for the strongest developed opposing rent.

    The cap prevents one exceptional deed from making a bot permanently idle,
    while the floor keeps undeveloped-board behavior stable across regional
    boards with different currency scales.
    """

    highest_rent = 0
    for space in board.spaces:
        state = states.get(space.id)
        if not state or not state.owner_id or state.owner_id == player_id:
            continue
        highest_rent = max(
            highest_rent,
            calculate_rent(board, states, space, 7),
        )
    return max(
        cash_reserve(board),
        min(highest_rent, max(1, board.starting_cash // 2)),
    )


def opponent_rent_pressure(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
) -> int:
    """Return the strongest traffic-adjusted opposing rent exposure."""

    return max(
        (
            round(
                calculate_rent(board, states, space, 7)
                * landing_weight(board, space.id)
            )
            for space in board.spaces
            if (state := states.get(space.id))
            and state.owner_id
            and state.owner_id != player_id
        ),
        default=0,
    )


def _completed_group_bonus(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
    group_id: str,
) -> int:
    """Estimate the strategic option value of controlling a complete group."""

    group = board.group_spaces(group_id)
    if not group or not owns_group(board, states, player_id, group_id):
        return 0
    purchase_value = sum(space.price for space in group)
    first = group[0]
    if first.kind == SPACE_STREET:
        three_house_rent = sum(
            round(
                space.rents[min(3, len(space.rents) - 1)]
                * landing_weight(board, space.id)
            )
            for space in group
        )
        return max(purchase_value // 2, three_house_rent)
    if first.kind == SPACE_TRANSIT:
        return max(purchase_value // 3, sum(space.rents[-1] for space in group))
    if first.kind == SPACE_UTILITY:
        return purchase_value // 4
    return 0


def strategic_portfolio_value(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
) -> int:
    """Value deeds, development, group progress, and completed groups."""

    total = 0
    seen_groups: set[str] = set()
    for space in board.spaces:
        state = states.get(space.id)
        if not state or state.owner_id != player_id:
            continue
        total += space.mortgage_value if state.mortgaged else space.price
        total += state.buildings * space.building_cost
        if space.group_id in seen_groups:
            continue
        seen_groups.add(space.group_id)
        group = board.group_spaces(space.group_id)
        owned = sum(
            1
            for member in group
            if states.get(member.id, PropertyState()).owner_id == player_id
        )
        if owned == len(group):
            total += _completed_group_bonus(
                board,
                states,
                player_id,
                space.group_id,
            )
        elif len(group) > 1:
            # Partial sets have negotiating and blocking value without being
            # treated like income-producing monopolies.
            total += sum(member.price for member in group) * owned // (len(group) * 10)
    return total


def _states_after_transfer(
    states: Mapping[str, PropertyState],
    *,
    proposer_id: str,
    target_id: str,
    offered_property_ids: list[str],
    requested_property_ids: list[str],
) -> dict[str, PropertyState]:
    projected = {property_id: replace(state) for property_id, state in states.items()}
    for property_id in offered_property_ids:
        if property_id in projected:
            projected[property_id].owner_id = target_id
    for property_id in requested_property_ids:
        if property_id in projected:
            projected[property_id].owner_id = proposer_id
    return projected


def trade_value_delta(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    *,
    player_id: str,
    proposer_id: str,
    target_id: str,
    offered_property_ids: list[str],
    requested_property_ids: list[str],
    offered_cash: int = 0,
    requested_cash: int = 0,
    offered_jail_cards: int = 0,
    requested_jail_cards: int = 0,
) -> int:
    """Return one player's projected strategic gain from a complete trade."""

    projected = _states_after_transfer(
        states,
        proposer_id=proposer_id,
        target_id=target_id,
        offered_property_ids=offered_property_ids,
        requested_property_ids=requested_property_ids,
    )
    delta = strategic_portfolio_value(board, projected, player_id) - (
        strategic_portfolio_value(board, states, player_id)
    )
    if player_id == proposer_id:
        delta += requested_cash - offered_cash
        delta += (requested_jail_cards - offered_jail_cards) * board.jail_fine
    elif player_id == target_id:
        delta += offered_cash - requested_cash
        delta += (offered_jail_cards - requested_jail_cards) * board.jail_fine
    return delta


def strategic_position_value(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    player_id: str,
    cash: int,
) -> int:
    """Return cash plus the strategic value of one player's portfolio."""

    return cash + strategic_portfolio_value(board, states, player_id)


def required_counterparty_trade_gain(
    proposer_strength: int,
    counterparty_strength: int,
    proposer_gain: int,
) -> int:
    """Return the minimum gain that makes a deal competitively reasonable.

    A balanced deal gives the counterparty at least half as much strategic
    value as the proposer.  A trailing counterparty demands more; a leader may
    concede part of an existing advantage.  The calculation uses only relative,
    board-scaled values.
    """

    if proposer_gain <= 0:
        return 0
    balanced_gain = max(1, (proposer_gain + 1) // 2)
    strength_gap = counterparty_strength - proposer_strength
    if strength_gap > 0:
        return max(1, balanced_gain - strength_gap // 8)
    if strength_gap < 0:
        return min(proposer_gain, balanced_gain + (-strength_gap) // 8)
    return balanced_gain


def property_value(
    board: BoardDefinition,
    states: dict[str, PropertyState],
    space: BoardSpaceDefinition,
    player_id: str,
) -> int:
    """Estimate the incremental strategic value of acquiring one deed."""

    before = strategic_portfolio_value(board, states, player_id)
    projected = {property_id: replace(state) for property_id, state in states.items()}
    if space.id not in projected:
        return space.price
    projected[space.id].owner_id = player_id
    projected[space.id].mortgaged = False
    projected[space.id].buildings = 0
    gain = strategic_portfolio_value(board, projected, player_id) - before
    return max(space.price // 2, gain)


def opponent_blocking_value(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    space: BoardSpaceDefinition,
    player_id: str,
) -> int:
    """Value denying a deed that would complete an opponent's group."""

    if not space.group_id:
        return 0
    opponents = {
        state.owner_id
        for state in states.values()
        if state.owner_id and state.owner_id != player_id
    }
    for opponent_id in opponents:
        if _completes_group(board, states, space, opponent_id):
            return max(
                space.price // 2,
                round(space.price * landing_weight(board, space.id) / 2),
            )
    return 0


def _completes_group(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    space: BoardSpaceDefinition,
    player_id: str,
) -> bool:
    group = board.group_spaces(space.group_id)
    return bool(group) and all(
        member.id == space.id
        or states.get(member.id, PropertyState()).owner_id == player_id
        for member in group
    )


def should_buy_property(
    board: BoardDefinition,
    states: dict[str, PropertyState],
    space: BoardSpaceDefinition,
    player_id: str,
    cash: int,
) -> bool:
    """Buy broadly, but preserve less cash when the deed completes a group."""

    reserve = acquisition_cash_reserve(
        board,
        states,
        player_id,
        completes_group=_completes_group(board, states, space, player_id),
    )
    return cash >= space.price + reserve


def maximum_auction_bid(
    board: BoardDefinition,
    states: dict[str, PropertyState],
    space: BoardSpaceDefinition,
    player_id: str,
    cash: int,
) -> int:
    """Cap an auction by both strategic value and risk-adjusted liquidity."""

    value = property_value(board, states, space, player_id) + opponent_blocking_value(
        board, states, space, player_id
    )
    reserve = acquisition_cash_reserve(
        board,
        states,
        player_id,
        completes_group=_completes_group(board, states, space, player_id),
    )
    return min(max(0, cash - reserve), value)


def development_score(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    property_id: str,
) -> int:
    """Rank a legal next building by rent gain, cost, and useful house levels."""

    space = board.space(property_id)
    state = states[property_id]
    if space.kind != SPACE_STREET or state.buildings >= 5:
        return -1
    projected = {key: replace(value) for key, value in states.items()}
    projected[property_id].buildings += 1
    current_rent = calculate_rent(board, states, space, 7)
    next_rent = calculate_rent(board, projected, space, 7)
    gain = max(0, next_rent - current_rent)
    next_level = state.buildings + 1
    level_bonus = {1: 20, 2: 45, 3: 90, 4: 30, 5: -20}.get(next_level, 0)
    traffic_adjusted_gain = round(gain * landing_weight(board, property_id))
    return traffic_adjusted_gain * 1_000 // max(1, space.building_cost) + level_bonus


def building_sale_damage(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    property_id: str,
) -> int:
    """Estimate strategic damage per unit of cash raised by one sale."""

    space = board.space(property_id)
    state = states[property_id]
    if space.kind != SPACE_STREET or state.buildings <= 0:
        return 10**9
    projected = {key: replace(value) for key, value in states.items()}
    projected[property_id].buildings = (
        4 if state.buildings == 5 else state.buildings - 1
    )
    current_rent = calculate_rent(board, states, space, 7)
    reduced_rent = calculate_rent(board, projected, space, 7)
    lost_income = round(
        max(0, current_rent - reduced_rent) * landing_weight(board, property_id)
    )
    sale_value = max(1, space.building_cost * board.rules.building_sale_percent // 100)
    return lost_income * 1_000 // sale_value


def group_building_sale_damage(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    group_id: str,
) -> int:
    """Estimate strategic damage per unit of cash from clearing a group."""

    spaces = board.group_spaces(group_id)
    projected = {key: replace(value) for key, value in states.items()}
    sale_value = 0
    for space in spaces:
        state = projected[space.id]
        sale_value += (
            state.buildings
            * space.building_cost
            * board.rules.building_sale_percent
            // 100
        )
        state.buildings = 0
    if sale_value <= 0:
        return 10**9
    lost_income = sum(
        round(
            max(
                0,
                calculate_rent(board, states, space, 7)
                - calculate_rent(board, projected, space, 7),
            )
            * landing_weight(board, space.id)
        )
        for space in spaces
    )
    return lost_income * 1_000 // sale_value


def mortgage_damage(
    board: BoardDefinition,
    states: Mapping[str, PropertyState],
    property_id: str,
) -> int:
    """Estimate strategic damage per unit of mortgage cash raised."""

    space = board.space(property_id)
    state = states[property_id]
    if state.mortgaged or not state.owner_id:
        return 10**9
    current_rent = calculate_rent(board, states, space, 7)
    income_loss = round(current_rent * landing_weight(board, property_id))
    deed_loss = max(0, space.price - space.mortgage_value)
    group_penalty = 0
    if owns_group(board, states, state.owner_id, space.group_id):
        group_penalty = _completed_group_bonus(
            board, states, state.owner_id, space.group_id
        ) // max(1, len(board.group_spaces(space.group_id)))
    damage = deed_loss + income_loss * 4 + group_penalty
    return damage * 1_000 // max(1, space.mortgage_value)
