from server.game_utils.cards import (
    Card,
    SUIT_CLUBS,
    SUIT_DIAMONDS,
    SUIT_HEARTS,
    SUIT_SPADES,
)
from server.game_utils.poker_evaluator import (
    HIGH_CARD,
    ONE_PAIR,
    TWO_PAIR,
    THREE_OF_A_KIND,
    STRAIGHT,
    FLUSH,
    FULL_HOUSE,
    FOUR_OF_A_KIND,
    STRAIGHT_FLUSH,
    best_hand,
    describe_best_hand,
    describe_hand,
    score_5_cards,
)


def _cards(specs):
    cards = []
    for idx, (rank, suit) in enumerate(specs):
        cards.append(Card(id=idx, rank=rank, suit=suit))
    return cards


def test_high_card():
    hand = _cards(
        [
            (1, SUIT_SPADES),  # A
            (13, SUIT_DIAMONDS),  # K
            (9, SUIT_CLUBS),
            (6, SUIT_HEARTS),
            (3, SUIT_DIAMONDS),
        ]
    )
    score = score_5_cards(hand)
    assert score == (HIGH_CARD, (14, 13, 9, 6, 3))


def test_one_pair_kickers():
    hand_a = _cards([(1, SUIT_SPADES), (1, SUIT_DIAMONDS), (9, SUIT_CLUBS), (7, SUIT_HEARTS), (4, SUIT_DIAMONDS)])
    hand_b = _cards([(1, SUIT_CLUBS), (1, SUIT_HEARTS), (12, SUIT_SPADES), (6, SUIT_CLUBS), (2, SUIT_DIAMONDS)])
    score_a = score_5_cards(hand_a)
    score_b = score_5_cards(hand_b)
    assert score_a[0] == ONE_PAIR
    assert score_b[0] == ONE_PAIR
    assert score_b > score_a


def test_two_pair_ordering():
    hand = _cards([(13, SUIT_SPADES), (13, SUIT_DIAMONDS), (5, SUIT_CLUBS), (5, SUIT_HEARTS), (9, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    assert score == (TWO_PAIR, (13, 5, 9))


def test_three_of_a_kind():
    hand = _cards([(12, SUIT_SPADES), (12, SUIT_DIAMONDS), (12, SUIT_CLUBS), (9, SUIT_HEARTS), (2, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    assert score == (THREE_OF_A_KIND, (12, 9, 2))


def test_straight_high_and_wheel():
    straight = _cards([(10, SUIT_SPADES), (11, SUIT_DIAMONDS), (12, SUIT_CLUBS), (13, SUIT_HEARTS), (9, SUIT_DIAMONDS)])
    wheel = _cards([(1, SUIT_SPADES), (2, SUIT_DIAMONDS), (3, SUIT_CLUBS), (4, SUIT_HEARTS), (5, SUIT_DIAMONDS)])
    score_straight = score_5_cards(straight)
    score_wheel = score_5_cards(wheel)
    assert score_straight == (STRAIGHT, (13,))
    assert score_wheel == (STRAIGHT, (5,))
    assert score_straight > score_wheel


def test_flush():
    hand = _cards([(1, SUIT_SPADES), (12, SUIT_SPADES), (9, SUIT_SPADES), (6, SUIT_SPADES), (3, SUIT_SPADES)])
    score = score_5_cards(hand)
    assert score == (FLUSH, (14, 12, 9, 6, 3))


def test_full_house():
    hand = _cards([(10, SUIT_SPADES), (10, SUIT_DIAMONDS), (10, SUIT_CLUBS), (4, SUIT_HEARTS), (4, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    assert score == (FULL_HOUSE, (10, 4))


def test_full_house_tiebreaker():
    hand_a = _cards([(9, SUIT_SPADES), (9, SUIT_DIAMONDS), (9, SUIT_CLUBS), (6, SUIT_HEARTS), (6, SUIT_DIAMONDS)])
    hand_b = _cards([(9, SUIT_SPADES), (9, SUIT_DIAMONDS), (9, SUIT_CLUBS), (5, SUIT_HEARTS), (5, SUIT_DIAMONDS)])
    score_a = score_5_cards(hand_a)
    score_b = score_5_cards(hand_b)
    assert score_a > score_b


def test_four_of_a_kind():
    hand = _cards([(7, SUIT_SPADES), (7, SUIT_DIAMONDS), (7, SUIT_CLUBS), (7, SUIT_HEARTS), (1, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    assert score == (FOUR_OF_A_KIND, (7, 14))


def test_straight_flush():
    hand = _cards([(9, SUIT_HEARTS), (10, SUIT_HEARTS), (11, SUIT_HEARTS), (12, SUIT_HEARTS), (13, SUIT_HEARTS)])
    score = score_5_cards(hand)
    assert score == (STRAIGHT_FLUSH, (13,))


def test_best_hand_from_seven_cards():
    cards = _cards(
        [
            (1, SUIT_SPADES),
            (13, SUIT_SPADES),
            (12, SUIT_SPADES),
            (11, SUIT_SPADES),
            (10, SUIT_SPADES),
            (9, SUIT_DIAMONDS),
            (2, SUIT_CLUBS),
        ]
    )
    score, best = best_hand(cards)
    assert score == (STRAIGHT_FLUSH, (14,))
    assert len(best) == 5


def test_two_pair_kicker_tiebreaker():
    hand_a = _cards([(13, SUIT_SPADES), (13, SUIT_DIAMONDS), (5, SUIT_CLUBS), (5, SUIT_HEARTS), (9, SUIT_DIAMONDS)])
    hand_b = _cards([(13, SUIT_CLUBS), (13, SUIT_HEARTS), (5, SUIT_SPADES), (5, SUIT_DIAMONDS), (8, SUIT_CLUBS)])
    score_a = score_5_cards(hand_a)
    score_b = score_5_cards(hand_b)
    assert score_a > score_b


def test_category_ordering():
    straight = _cards([(9, SUIT_SPADES), (10, SUIT_DIAMONDS), (11, SUIT_CLUBS), (12, SUIT_HEARTS), (13, SUIT_DIAMONDS)])
    flush = _cards([(2, SUIT_SPADES), (5, SUIT_SPADES), (9, SUIT_SPADES), (12, SUIT_SPADES), (13, SUIT_SPADES)])
    trips = _cards([(8, SUIT_SPADES), (8, SUIT_DIAMONDS), (8, SUIT_CLUBS), (4, SUIT_HEARTS), (2, SUIT_DIAMONDS)])
    assert score_5_cards(flush) > score_5_cards(straight)
    assert score_5_cards(straight) > score_5_cards(trips)


def test_best_hand_excludes_high_off_suit_card():
    cards = _cards(
        [
            (1, SUIT_SPADES),   # A off-suit
            (10, SUIT_HEARTS),
            (11, SUIT_HEARTS),
            (12, SUIT_HEARTS),
            (13, SUIT_HEARTS),
            (9, SUIT_HEARTS),
            (2, SUIT_CLUBS),
        ]
    )
    score, best = best_hand(cards)
    assert score == (STRAIGHT_FLUSH, (13,))
    assert len(best) == 5


def test_tie_scores_equal():
    hand_a = _cards([(1, SUIT_SPADES), (13, SUIT_DIAMONDS), (12, SUIT_CLUBS), (11, SUIT_HEARTS), (10, SUIT_DIAMONDS)])
    hand_b = _cards([(1, SUIT_CLUBS), (13, SUIT_HEARTS), (12, SUIT_DIAMONDS), (11, SUIT_SPADES), (10, SUIT_CLUBS)])
    score_a = score_5_cards(hand_a)
    score_b = score_5_cards(hand_b)
    assert score_a == score_b


def test_describe_hand_pair():
    hand = _cards([(1, SUIT_SPADES), (1, SUIT_DIAMONDS), (9, SUIT_CLUBS), (7, SUIT_HEARTS), (4, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    assert describe_hand(score) == "Pair of Aces, with 9, 7, and 4"


def test_describe_best_hand_straight_flush():
    cards = _cards(
        [
            (1, SUIT_SPADES),
            (13, SUIT_SPADES),
            (12, SUIT_SPADES),
            (11, SUIT_SPADES),
            (10, SUIT_SPADES),
            (9, SUIT_DIAMONDS),
            (2, SUIT_CLUBS),
        ]
    )
    description, best = describe_best_hand(cards)
    assert description == "Ace high Straight Flush"
    assert len(best) == 5


def test_describe_hand_localized_pt():
    hand = _cards([(1, SUIT_SPADES), (1, SUIT_DIAMONDS), (9, SUIT_CLUBS), (7, SUIT_HEARTS), (4, SUIT_DIAMONDS)])
    score = score_5_cards(hand)
    description = describe_hand(score, locale="pt")
    assert "Par de" in description


def test_describe_hand_localized_zh():
    hand = _cards([(13, SUIT_SPADES), (12, SUIT_SPADES), (11, SUIT_SPADES), (10, SUIT_SPADES), (9, SUIT_SPADES)])
    score = score_5_cards(hand)
    description = describe_hand(score, locale="zh")
    assert "同花顺" in description
