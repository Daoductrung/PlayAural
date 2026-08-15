"""Registry for immutable Monopoly board definitions."""

from __future__ import annotations

from .models import (
    CARD_BACK,
    CARD_COLLECT,
    CARD_COLLECT_EACH,
    CARD_GO_TO_JAIL,
    CARD_JAIL_FREE,
    CARD_MOVE,
    CARD_NEAREST,
    CARD_PAY,
    CARD_PAY_EACH,
    CARD_REPAIRS,
    OWNABLE_SPACE_KINDS,
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
    BoardDefinition,
)

_BOARDS: dict[str, BoardDefinition] = {}
DEFAULT_BOARD_ID = "standard"


def register_board(board: BoardDefinition) -> BoardDefinition:
    """Validate and register a board by stable id."""
    validate_board(board)
    existing = _BOARDS.get(board.id)
    if existing is not None:
        if existing != board:
            raise ValueError(f"Monopoly board id already registered: {board.id}")
        return existing
    for registered in _BOARDS.values():
        if registered.name_key == board.name_key:
            raise ValueError(
                f"Monopoly board name key already registered: {board.name_key}"
            )
        if registered.description_key == board.description_key:
            raise ValueError(
                "Monopoly board description key already registered: "
                f"{board.description_key}"
            )
    _BOARDS[board.id] = board
    return board


def get_board(board_id: str) -> BoardDefinition:
    """Return a registered board definition."""
    try:
        return _BOARDS[board_id]
    except KeyError as error:
        raise ValueError(f"Unsupported Monopoly board: {board_id}") from error


def get_board_ids() -> tuple[str, ...]:
    """Return stable board ids independently of module import order."""
    return tuple(sorted(_BOARDS))


def validate_board(board: BoardDefinition) -> None:
    """Fail fast when a regional board is structurally unsafe."""
    terminology_keys = (
        board.terminology.street_kind_key,
        board.terminology.transit_kind_key,
        board.terminology.utility_kind_key,
        board.terminology.chance_kind_key,
        board.terminology.community_kind_key,
        board.terminology.chance_deck_key,
        board.terminology.community_deck_key,
        board.terminology.utility_rent_schedule_key,
    )
    if not all(
        (
            board.id,
            board.name_key,
            board.description_key,
            board.currency_key,
            *terminology_keys,
        )
    ):
        raise ValueError("A Monopoly board needs stable localized metadata")
    if len(board.spaces) < 4:
        raise ValueError("A Monopoly board must contain at least four spaces")
    space_ids = [space.id for space in board.spaces]
    if any(not space.id or not space.name_key for space in board.spaces) or len(
        space_ids
    ) != len(set(space_ids)):
        raise ValueError("Monopoly board spaces need unique ids and localized names")
    if board.go_space_id not in space_ids or board.jail_space_id not in space_ids:
        raise ValueError("A Monopoly board must define GO and Jail spaces")
    if board.space(board.go_space_id).kind != SPACE_GO:
        raise ValueError("A Monopoly board's GO id must identify a GO space")
    if board.space(board.jail_space_id).kind != SPACE_JAIL:
        raise ValueError("A Monopoly board's Jail id must identify a Jail space")
    if sum(space.kind == SPACE_GO for space in board.spaces) != 1:
        raise ValueError("A Monopoly board must contain exactly one GO space")
    if sum(space.kind == SPACE_JAIL for space in board.spaces) != 1:
        raise ValueError("A Monopoly board must contain exactly one Jail space")
    if sum(space.kind == SPACE_FREE_PARKING for space in board.spaces) != 1:
        raise ValueError(
            "A Monopoly board must contain exactly one Free Parking space"
        )
    if sum(space.kind == SPACE_GO_TO_JAIL for space in board.spaces) != 1:
        raise ValueError(
            "A Monopoly board must contain exactly one Go to Jail space"
        )
    if (
        board.starting_cash <= 0
        or board.go_salary < 0
        or board.snake_eyes_bonus < 0
        or board.jail_fine < 0
    ):
        raise ValueError("Monopoly cash values cannot be invalid")
    if board.bank_houses < 0 or board.bank_hotels < 0:
        raise ValueError("Monopoly building supplies cannot be negative")
    development = board.development
    if development.level_keys and (
        len(development.level_keys) != 5
        or not development.empty_key
        or any(not key for key in development.level_keys)
    ):
        raise ValueError(
            "Named Monopoly development systems need an empty state and five levels"
        )
    if not all(
        (
            development.collective_key,
            development.build_selector_key,
            development.sell_selector_key,
            development.rent_schedule_key,
            development.bank_supply_key,
            development.group_sale_description_key,
        )
    ):
        raise ValueError("A Monopoly development system needs localized metadata")
    error_keys = [key for key, _ in development.error_key_overrides]
    if (
        len(error_keys) != len(set(error_keys))
        or any(
            not key or not replacement
            for key, replacement in development.error_key_overrides
        )
    ):
        raise ValueError(
            "Monopoly development error overrides must be unique and localized"
        )
    if development.finite_supply and (
        board.bank_houses <= 0 or board.bank_hotels <= 0
    ):
        raise ValueError("A finite Monopoly development supply must contain pieces")
    rules = board.rules
    if (
        rules.auction_opening_bid <= 0
        or rules.auction_bid_increment <= 0
        or rules.consecutive_doubles_to_jail < 2
        or rules.failed_jail_rolls_before_fine < 1
        or not 0 <= rules.mortgage_interest_percent <= 100
        or not 0 <= rules.building_sale_percent <= 100
        or rules.utility_single_multiplier <= 0
        or rules.utility_complete_group_multiplier <= 0
    ):
        raise ValueError("Monopoly rule values are outside their safe ranges")
    group_ids = [group.id for group in board.property_groups]
    if (
        not group_ids
        or len(group_ids) != len(set(group_ids))
        or any(not group.id or not group.name_key for group in board.property_groups)
    ):
        raise ValueError("Monopoly property groups must have unique ids and names")
    valid_kinds = {
        SPACE_GO,
        SPACE_STREET,
        SPACE_TRANSIT,
        SPACE_UTILITY,
        SPACE_CHANCE,
        SPACE_COMMUNITY,
        SPACE_TAX,
        SPACE_JAIL,
        SPACE_FREE_PARKING,
        SPACE_GO_TO_JAIL,
    }
    valid_actions = {
        CARD_MOVE,
        CARD_NEAREST,
        CARD_COLLECT,
        CARD_PAY,
        CARD_COLLECT_EACH,
        CARD_PAY_EACH,
        CARD_REPAIRS,
        CARD_JAIL_FREE,
        CARD_GO_TO_JAIL,
        CARD_BACK,
    }
    for deck_name, cards in (
        ("chance", board.chance_cards),
        ("community", board.community_cards),
    ):
        card_ids = [card.id for card in cards]
        if (
            not card_ids
            or any(not card.id or not card.text_key for card in cards)
            or len(card_ids) != len(set(card_ids))
        ):
            raise ValueError(
                f"Monopoly {deck_name} cards need unique ids and localized text"
            )
        for card in cards:
            if card.action not in valid_actions:
                raise ValueError(f"Monopoly card {card.id} has an invalid action")
            if card.destination_id and card.destination_id not in space_ids:
                raise ValueError(
                    f"Monopoly card {card.id} targets missing space {card.destination_id}"
                )
            if card.action == CARD_MOVE and not card.destination_id:
                raise ValueError(f"Monopoly move card {card.id} needs a destination")
            if card.destination_id and card.action != CARD_MOVE:
                raise ValueError(f"Monopoly card {card.id} has an unused destination")
            if card.collect_go and card.action != CARD_MOVE:
                raise ValueError(f"Monopoly card {card.id} has unused collect-Go data")
            if card.action == CARD_NEAREST:
                if card.nearest_kind not in OWNABLE_SPACE_KINDS:
                    raise ValueError(
                        f"Monopoly nearest card {card.id} needs an ownable kind"
                    )
                if not any(space.kind == card.nearest_kind for space in board.spaces):
                    raise ValueError(
                        f"Monopoly nearest card {card.id} has no target space"
                    )
                if card.rent_multiplier <= 0:
                    raise ValueError(
                        f"Monopoly nearest card {card.id} needs a positive rent multiplier"
                    )
            elif card.nearest_kind or card.rent_multiplier != 1:
                raise ValueError(
                    f"Monopoly card {card.id} has unused nearest-space data"
                )
            if card.action == CARD_BACK and card.amount <= 0:
                raise ValueError(
                    f"Monopoly back card {card.id} needs a positive distance"
                )
            if (
                card.action
                in {
                    CARD_COLLECT,
                    CARD_PAY,
                    CARD_COLLECT_EACH,
                    CARD_PAY_EACH,
                }
                and card.amount <= 0
            ):
                raise ValueError(
                    f"Monopoly money card {card.id} needs a positive amount"
                )
            if card.action == CARD_REPAIRS and not (
                card.per_house > 0 or card.per_hotel > 0
            ):
                raise ValueError(f"Monopoly repair card {card.id} needs a positive fee")
            if card.action != CARD_REPAIRS and (card.per_house or card.per_hotel):
                raise ValueError(f"Monopoly card {card.id} has unused repair fees")
            if card.amount and card.action not in {
                CARD_BACK,
                CARD_COLLECT,
                CARD_PAY,
                CARD_COLLECT_EACH,
                CARD_PAY_EACH,
            }:
                raise ValueError(f"Monopoly card {card.id} has an unused amount")
            if card.amount < 0 or card.per_house < 0 or card.per_hotel < 0:
                raise ValueError(f"Monopoly card {card.id} has a negative amount")
    all_card_ids = [card.id for card in board.chance_cards + board.community_cards]
    if len(all_card_ids) != len(set(all_card_ids)):
        raise ValueError("Monopoly card ids must be unique across both decks")
    for space in board.spaces:
        if space.kind not in valid_kinds:
            raise ValueError(f"Space {space.id} has an invalid kind")
        if space.kind == SPACE_STREET and len(space.rents) != 6:
            raise ValueError(f"Street {space.id} must define six rent levels")
        if space.kind in OWNABLE_SPACE_KINDS and (
            not space.group_id
            or space.group_id not in group_ids
            or space.price <= 0
            or space.mortgage_value <= 0
        ):
            raise ValueError(f"Ownable space {space.id} has incomplete deed data")
        if space.kind in OWNABLE_SPACE_KINDS and space.mortgage_value >= space.price:
            raise ValueError(
                f"Ownable space {space.id} must mortgage for less than its price"
            )
        if space.kind not in OWNABLE_SPACE_KINDS and (
            space.price
            or space.mortgage_value
            or space.group_id
            or space.rents
            or space.building_cost
        ):
            raise ValueError(f"Non-ownable space {space.id} has unused deed data")
        if space.kind == SPACE_STREET and space.building_cost <= 0:
            raise ValueError(f"Street {space.id} needs a positive building cost")
        if space.kind != SPACE_STREET and space.building_cost:
            raise ValueError(f"Space {space.id} has an unused building cost")
        if space.kind == SPACE_TAX and space.tax_amount <= 0:
            raise ValueError(f"Tax space {space.id} needs a positive amount")
        if space.kind != SPACE_TAX and space.tax_amount:
            raise ValueError(f"Space {space.id} has an unused tax amount")
        if any(rent <= 0 for rent in space.rents):
            raise ValueError(f"Space {space.id} needs positive rent levels")
        if space.kind == SPACE_UTILITY and space.rents:
            raise ValueError(
                f"Utility {space.id} uses board multipliers, not fixed rent levels"
            )
    for group in board.property_groups:
        spaces = board.group_spaces(group.id)
        if not spaces:
            raise ValueError(f"Property group {group.id} has no spaces")
        kinds = {space.kind for space in spaces}
        if len(kinds) != 1 or not kinds.issubset(OWNABLE_SPACE_KINDS):
            raise ValueError(
                f"Property group {group.id} must contain one ownable space kind"
            )
        if (
            SPACE_STREET in kinds
            and len({space.building_cost for space in spaces}) != 1
        ):
            raise ValueError(f"Street group {group.id} must use one building cost")
        if SPACE_TRANSIT in kinds and any(
            len(space.rents) != len(spaces) for space in spaces
        ):
            raise ValueError(f"Transit group {group.id} needs one rent level per space")
