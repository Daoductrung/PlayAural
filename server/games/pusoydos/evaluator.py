from typing import List, Tuple, Optional
from ...game_utils.cards import Card
from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, field


def get_rank_value(rank: int) -> int:
    """
    Returns the Big Two relative rank value.
    3 is lowest (3), 2 is highest (15).
    """
    if rank == 2:
        return 15
    if rank == 1: # Ace
        return 14
    return rank


def get_suit_value(suit: int) -> int:
    """
    Returns the Big Two suit value.
    Diamonds (1) = 4 (highest)
    Hearts (3) = 3
    Spades (4) = 2
    Clubs (2) = 1 (lowest)
    """
    if suit == 1: return 4 # Diamonds
    if suit == 3: return 3 # Hearts
    if suit == 4: return 2 # Spades
    if suit == 2: return 1 # Clubs
    return 0


def card_value(card: Card) -> int:
    """
    Returns a combined value for sorting individual cards.
    """
    return get_rank_value(card.rank) * 10 + get_suit_value(card.suit)


def sort_cards(cards: List[Card]) -> List[Card]:
    """Sorts cards by Big Two rank then suit."""
    return sorted(cards, key=card_value)


@dataclass
class Combo(DataClassJSONMixin):
    type_name: str
    cards: List[Card]
    rank_value: int
    suit_value: int
    tier: int = 0

    def __post_init__(self):
        self.cards = sort_cards(self.cards)
        if self.type_name == "straight": self.tier = 1
        elif self.type_name == "flush": self.tier = 2
        elif self.type_name == "full_house": self.tier = 3
        elif self.type_name == "four_of_a_kind": self.tier = 4
        elif self.type_name == "straight_flush": self.tier = 5

    def beats(self, other: "Combo") -> bool:
        """Returns True if this combo beats the other combo."""
        if len(self.cards) != len(other.cards):
            return False

        if len(self.cards) == 5:
            if self.tier != other.tier:
                return self.tier > other.tier
            # Same tier
            if self.type_name in ["straight", "straight_flush"]:
                # Compare rank, then suit of the highest card
                if self.rank_value != other.rank_value:
                    return self.rank_value > other.rank_value
                return self.suit_value > other.suit_value
            elif self.type_name == "flush":
                # Compare highest suit, then highest rank
                if self.suit_value != other.suit_value:
                    return self.suit_value > other.suit_value
                return self.rank_value > other.rank_value
            elif self.type_name in ["full_house", "four_of_a_kind"]:
                # Only compare the main rank value
                return self.rank_value > other.rank_value

        # 1, 2, or 3 cards
        if self.rank_value != other.rank_value:
            return self.rank_value > other.rank_value
        return self.suit_value > other.suit_value


def evaluate_combo(cards: List[Card]) -> Optional[Combo]:
    """
    Evaluates a list of cards and returns a Combo object if valid, else None.
    """
    n = len(cards)
    if n not in [1, 2, 3, 5]:
        return None

    sorted_c = sort_cards(cards)

    if n == 1:
        return Combo("single", cards, get_rank_value(sorted_c[0].rank), get_suit_value(sorted_c[0].suit))

    elif n == 2:
        if sorted_c[0].rank == sorted_c[1].rank:
            # Highest suit determines the strength
            return Combo("pair", cards, get_rank_value(sorted_c[0].rank), max(get_suit_value(sorted_c[0].suit), get_suit_value(sorted_c[1].suit)))
        return None

    elif n == 3:
        if sorted_c[0].rank == sorted_c[1].rank == sorted_c[2].rank:
            return Combo("three_of_a_kind", cards, get_rank_value(sorted_c[0].rank), 0)
        return None

    elif n == 5:
        is_flush = len(set(c.suit for c in cards)) == 1

        # Check for straight
        ranks = [get_rank_value(c.rank) for c in sorted_c]
        is_straight = False
        straight_high_rank = 0
        straight_high_suit = 0

        # Standard straight check
        if ranks == [ranks[0], ranks[0]+1, ranks[0]+2, ranks[0]+3, ranks[0]+4]:
            is_straight = True
            straight_high_rank = ranks[4]
            straight_high_suit = get_suit_value(sorted_c[4].suit)

        # A 2 3 4 5
        # Standard sorted ranks: 3 4 5 14(A) 15(2)
        elif ranks == [3, 4, 5, 14, 15]:
            is_straight = True
            straight_high_rank = 5 # 5 is the highest card in this straight
            # Find the suit of the 5
            for c in sorted_c:
                if get_rank_value(c.rank) == 5:
                    straight_high_suit = get_suit_value(c.suit)
                    break

        # 2 3 4 5 6
        # Standard sorted ranks: 3 4 5 6 15(2)
        elif ranks == [3, 4, 5, 6, 15]:
            is_straight = True
            straight_high_rank = 6 # 6 is highest
            for c in sorted_c:
                if get_rank_value(c.rank) == 6:
                    straight_high_suit = get_suit_value(c.suit)
                    break

        # J Q K A 2
        # Ranks: 11 12 13 14 15
        elif ranks == [11, 12, 13, 14, 15]:
            is_straight = True
            straight_high_rank = 15 # 2 is highest
            for c in sorted_c:
                if get_rank_value(c.rank) == 15:
                    straight_high_suit = get_suit_value(c.suit)
                    break

        # Check four of a kind
        rank_counts = {}
        for c in cards:
            rank_counts[c.rank] = rank_counts.get(c.rank, 0) + 1

        counts = sorted(rank_counts.values())
        if counts == [1, 4]:
            four_rank = [r for r, count in rank_counts.items() if count == 4][0]
            return Combo("four_of_a_kind", cards, get_rank_value(four_rank), 0)

        if counts == [2, 3]:
            three_rank = [r for r, count in rank_counts.items() if count == 3][0]
            return Combo("full_house", cards, get_rank_value(three_rank), 0)

        if is_straight and is_flush:
            return Combo("straight_flush", cards, straight_high_rank, straight_high_suit)

        if is_flush:
            return Combo("flush", cards, get_rank_value(sorted_c[4].rank), get_suit_value(sorted_c[4].suit))

        if is_straight:
            return Combo("straight", cards, straight_high_rank, straight_high_suit)

    return None
