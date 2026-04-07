from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin

from ...game_utils.cards import Card


SOUTHERN_VARIANT = "south"
NORTHERN_VARIANT = "north"


def get_rank_strength(rank: int) -> int:
    if rank == 1:
        return 12
    if rank == 2:
        return 13
    return rank - 2


def get_suit_strength(suit: int) -> int:
    if suit == 4:
        return 1
    if suit == 2:
        return 2
    if suit == 1:
        return 3
    if suit == 3:
        return 4
    return 0


def card_strength(card: Card) -> int:
    return get_rank_strength(card.rank) * 10 + get_suit_strength(card.suit)


def sort_cards(cards: list[Card]) -> list[Card]:
    return sorted(cards, key=card_strength)


def is_red_suit(suit: int) -> bool:
    return suit in (1, 3)


def cards_contain_two(cards: list[Card]) -> bool:
    return any(card.rank == 2 for card in cards)


@dataclass
class TienLenCombo(DataClassJSONMixin):
    type_name: str
    cards: list[Card]
    rank_strength: int
    suit_strength: int
    pair_count: int = 0
    structure_signature: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.cards = sort_cards(self.cards)
        if not self.structure_signature:
            self.structure_signature = [get_suit_strength(card.suit) for card in self.cards]

    @property
    def card_count(self) -> int:
        return len(self.cards)


def _straight_signature(cards: list[Card]) -> tuple[bool, int, int]:
    ordered = sort_cards(cards)
    ranks = [get_rank_strength(card.rank) for card in ordered]
    if len(set(ranks)) != len(ranks):
        return False, 0, 0
    if ranks != list(range(ranks[0], ranks[0] + len(ranks))):
        return False, 0, 0
    return True, ranks[-1], get_suit_strength(ordered[-1].suit)


def _same_rank(cards: list[Card]) -> bool:
    return len({card.rank for card in cards}) == 1


def _evaluate_southern(cards: list[Card]) -> TienLenCombo | None:
    ordered = sort_cards(cards)
    count = len(ordered)

    if count == 1:
        card = ordered[0]
        return TienLenCombo("single", ordered, get_rank_strength(card.rank), get_suit_strength(card.suit))

    if count == 2 and _same_rank(ordered):
        return TienLenCombo(
            "pair",
            ordered,
            get_rank_strength(ordered[0].rank),
            max(get_suit_strength(card.suit) for card in ordered),
        )

    if count == 3:
        if _same_rank(ordered):
            return TienLenCombo(
                "triple",
                ordered,
                get_rank_strength(ordered[0].rank),
                max(get_suit_strength(card.suit) for card in ordered),
            )
        if not cards_contain_two(ordered):
            is_straight, high_rank, high_suit = _straight_signature(ordered)
            if is_straight:
                return TienLenCombo("straight", ordered, high_rank, high_suit)
        return None

    if count == 4:
        if _same_rank(ordered):
            return TienLenCombo(
                "four_of_a_kind",
                ordered,
                get_rank_strength(ordered[0].rank),
                max(get_suit_strength(card.suit) for card in ordered),
            )
        if not cards_contain_two(ordered):
            is_straight, high_rank, high_suit = _straight_signature(ordered)
            if is_straight:
                return TienLenCombo("straight", ordered, high_rank, high_suit)
        return None

    if count >= 5 and not cards_contain_two(ordered):
        is_straight, high_rank, high_suit = _straight_signature(ordered)
        if is_straight:
            return TienLenCombo("straight", ordered, high_rank, high_suit)

    if count >= 6 and count % 2 == 0:
        rank_groups: list[tuple[int, list[Card]]] = []
        for rank in sorted({card.rank for card in ordered}, key=get_rank_strength):
            group = [card for card in ordered if card.rank == rank]
            if len(group) != 2 or rank == 2:
                rank_groups = []
                break
            rank_groups.append((rank, sort_cards(group)))
        if rank_groups and len(rank_groups) >= 3:
            strengths = [get_rank_strength(rank) for rank, _ in rank_groups]
            if strengths == list(range(strengths[0], strengths[0] + len(strengths))):
                high_pair = rank_groups[-1][1]
                return TienLenCombo(
                    "consecutive_pairs",
                    ordered,
                    strengths[-1],
                    max(get_suit_strength(card.suit) for card in high_pair),
                    pair_count=len(rank_groups),
                )

    return None


def _evaluate_northern(cards: list[Card]) -> TienLenCombo | None:
    ordered = sort_cards(cards)
    count = len(ordered)

    if count == 1:
        card = ordered[0]
        return TienLenCombo(
            "single",
            ordered,
            get_rank_strength(card.rank),
            get_suit_strength(card.suit),
            structure_signature=[get_suit_strength(card.suit)],
        )

    if count == 2 and _same_rank(ordered):
        if ordered[0].rank != 2 and is_red_suit(ordered[0].suit) != is_red_suit(ordered[1].suit):
            return None
        suits = sorted(get_suit_strength(card.suit) for card in ordered)
        return TienLenCombo(
            "pair",
            ordered,
            get_rank_strength(ordered[0].rank),
            max(suits),
            structure_signature=suits,
        )

    if count == 3:
        if _same_rank(ordered):
            suits = sorted(get_suit_strength(card.suit) for card in ordered)
            return TienLenCombo(
                "triple",
                ordered,
                get_rank_strength(ordered[0].rank),
                max(suits),
                structure_signature=suits,
            )
        if len({card.suit for card in ordered}) == 1:
            is_straight, high_rank, high_suit = _straight_signature(ordered)
            if is_straight:
                return TienLenCombo(
                    "straight",
                    ordered,
                    high_rank,
                    high_suit,
                    structure_signature=[get_suit_strength(ordered[0].suit)] * count,
                )
        return None

    if count == 4 and _same_rank(ordered):
        suits = sorted(get_suit_strength(card.suit) for card in ordered)
        return TienLenCombo(
            "four_of_a_kind",
            ordered,
            get_rank_strength(ordered[0].rank),
            max(suits),
            structure_signature=suits,
        )

    if count >= 3 and len({card.suit for card in ordered}) == 1:
        is_straight, high_rank, high_suit = _straight_signature(ordered)
        if is_straight:
            return TienLenCombo(
                "straight",
                ordered,
                high_rank,
                high_suit,
                structure_signature=[get_suit_strength(ordered[0].suit)] * count,
            )

    return None


def evaluate_combo(cards: list[Card], variant: str) -> TienLenCombo | None:
    if not cards:
        return None
    if variant == NORTHERN_VARIANT:
        return _evaluate_northern(cards)
    return _evaluate_southern(cards)
