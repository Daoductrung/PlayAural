"""Deck, hierarchy, envido, flor, and call-value coverage for Argentine Truco."""

import itertools

import pytest

from ..games.truco import cards, rules
from ..games.truco.cards import TrucoCard


def card(rank: int, suit: str, card_id: int = 0) -> TrucoCard:
    return TrucoCard(id=card_id, rank=rank, suit=suit)


def test_deck_has_forty_unique_cards_without_eights_and_nines():
    deck = cards.build_deck()
    assert len(deck) == cards.DECK_SIZE == 40
    assert len({c.id for c in deck}) == 40
    assert {(c.rank, c.suit) for c in deck} == set(
        itertools.product(cards.RANKS, cards.SUITS)
    )
    assert all(c.rank not in (8, 9) for c in deck)


def test_hierarchy_matches_the_traditional_order():
    # Strongest to weakest; cards on the same line are equal in strength.
    tiers = [
        [(1, cards.SUIT_ESPADAS)],
        [(1, cards.SUIT_BASTOS)],
        [(7, cards.SUIT_ESPADAS)],
        [(7, cards.SUIT_OROS)],
        [(3, s) for s in cards.SUITS],
        [(2, s) for s in cards.SUITS],
        [(1, cards.SUIT_COPAS), (1, cards.SUIT_OROS)],
        [(12, s) for s in cards.SUITS],
        [(11, s) for s in cards.SUITS],
        [(10, s) for s in cards.SUITS],
        [(7, cards.SUIT_COPAS), (7, cards.SUIT_BASTOS)],
        [(6, s) for s in cards.SUITS],
        [(5, s) for s in cards.SUITS],
        [(4, s) for s in cards.SUITS],
    ]
    # Every card of the deck appears in exactly one tier.
    assert sorted(x for tier in tiers for x in tier) == sorted(
        itertools.product(cards.RANKS, cards.SUITS)
    )
    for index, tier in enumerate(tiers):
        powers = {card(r, s).power for r, s in tier}
        assert len(powers) == 1, f"tier {index} is not uniform"
    tier_powers = [card(*tier[0]).power for tier in tiers]
    assert tier_powers == sorted(tier_powers, reverse=True)
    assert len(set(tier_powers)) == len(tiers)


def test_compare_cards_returns_winner_and_parda():
    ancho = card(1, cards.SUIT_ESPADAS)
    siete = card(7, cards.SUIT_ESPADAS)
    assert rules.compare_cards(ancho, siete) == 1
    assert rules.compare_cards(siete, ancho) == -1
    assert rules.compare_cards(card(3, cards.SUIT_OROS), card(3, cards.SUIT_COPAS)) == 0
    # The seven of cups is a plain seven: it still beats a six.
    assert rules.compare_cards(card(7, cards.SUIT_COPAS), card(6, cards.SUIT_OROS)) == 1


@pytest.mark.parametrize(
    ("hand", "expected"),
    [
        ([(7, "espadas"), (6, "espadas"), (1, "oros")], 33),
        ([(12, "oros"), (11, "oros"), (10, "copas")], 20),
        ([(12, "espadas"), (5, "copas"), (4, "oros")], 5),
        ([(12, "espadas"), (11, "copas"), (10, "oros")], 0),
        ([(7, "copas"), (6, "copas"), (5, "copas")], 33),
        ([(1, "bastos"), (12, "bastos"), (3, "oros")], 21),
        ([(4, "oros"), (5, "oros"), (6, "bastos")], 29),
    ],
)
def test_envido_score(hand, expected):
    assert (
        rules.envido_score([card(r, s, i) for i, (r, s) in enumerate(hand)]) == expected
    )


def test_envido_uses_two_cards_but_flor_uses_all_three():
    hand = [card(7, "oros", 0), card(6, "oros", 1), card(5, "oros", 2)]
    assert rules.has_flor(hand)
    # The envido counts the best two cards of the suit: 7 + 6 + 20.
    assert rules.envido_score(hand) == 33
    # The flor counts all three cards (Juegos Bonaerenses 6.16): 7 + 6 + 5 + 20.
    assert rules.flor_score(hand) == 38


def test_flor_requires_three_cards_of_one_suit():
    assert not rules.has_flor(
        [card(7, "oros", 0), card(6, "oros", 1), card(5, "copas", 2)]
    )
    assert (
        rules.flor_score([card(7, "oros", 0), card(6, "oros", 1), card(5, "copas", 2)])
        == 0
    )
    assert not rules.has_flor([card(7, "oros", 0), card(6, "oros", 1)])
    assert (
        rules.flor_score(
            [card(12, "bastos", 0), card(11, "bastos", 1), card(10, "bastos", 2)]
        )
        == 20
    )
    assert (
        rules.flor_score(
            [card(1, "bastos", 0), card(5, "bastos", 1), card(12, "bastos", 2)]
        )
        == 26
    )
    assert (
        rules.flor_score(
            [card(7, "copas", 0), card(12, "copas", 1), card(11, "copas", 2)]
        )
        == 27
    )
    assert (
        rules.flor_score(
            [card(4, "copas", 0), card(5, "copas", 1), card(6, "copas", 2)]
        )
        == 35
    )


def test_truco_chain_levels_and_values():
    assert rules.next_truco_level(None) == "truco"
    assert rules.next_truco_level("truco") == "retruco"
    assert rules.next_truco_level("retruco") == "valecuatro"
    assert rules.next_truco_level("valecuatro") is None
    assert rules.can_raise_truco(None) and rules.can_raise_truco("retruco")
    assert not rules.can_raise_truco("valecuatro")
    assert [rules.truco_points(None)] == [1]
    assert [rules.truco_points(level) for level in rules.TRUCO_LEVELS] == [2, 3, 4]
    assert [
        rules.truco_points(level, accepted=False) for level in rules.TRUCO_LEVELS
    ] == [1, 2, 3]


@pytest.mark.parametrize(
    ("chain", "call", "allowed"),
    [
        ([], "envido", True),
        ([], "real_envido", True),
        ([], "falta_envido", True),
        (["envido"], "envido", True),
        (["envido", "envido"], "envido", False),
        (["envido"], "real_envido", True),
        (["real_envido"], "envido", False),
        (["real_envido"], "real_envido", False),
        (["real_envido"], "falta_envido", True),
        (["envido", "real_envido"], "falta_envido", True),
        (["falta_envido"], "falta_envido", False),
        (["falta_envido"], "real_envido", False),
        ([], "bogus", False),
    ],
)
def test_envido_chain_validity(chain, call, allowed):
    assert rules.can_add_envido_call(chain, call) is allowed


def test_envido_accepted_and_declined_values():
    assert rules.envido_accepted_points(["envido"], 9) == 2
    assert rules.envido_accepted_points(["envido", "envido"], 9) == 4
    assert rules.envido_accepted_points(["envido", "real_envido"], 9) == 5
    assert rules.envido_accepted_points(["real_envido"], 9) == 3
    assert rules.envido_accepted_points(["envido", "falta_envido"], 9) == 9
    # A single refused call pays 1; later refusals pay the accepted calls before it.
    assert rules.envido_declined_points(["envido"]) == 1
    assert rules.envido_declined_points(["real_envido"]) == 1
    assert rules.envido_declined_points(["falta_envido"]) == 1
    assert rules.envido_declined_points(["envido", "envido"]) == 2
    assert rules.envido_declined_points(["envido", "real_envido"]) == 2
    assert rules.envido_declined_points(["envido", "envido", "real_envido"]) == 4
    assert rules.envido_declined_points(["envido", "real_envido", "falta_envido"]) == 5


def test_falta_envido_decides_the_game_while_both_sides_are_in_the_malas():
    assert rules.falta_decides_game([0, 0], 30)
    assert rules.falta_decides_game([14, 3], 30)
    # The winner receives exactly what is needed to reach the target.
    assert rules.falta_envido_points([0, 0], 30, winner_score=0) == 30
    assert rules.falta_envido_points([9, 4], 30, winner_score=4) == 26
    assert rules.falta_envido_points([9, 4], 30, winner_score=9) == 21


def test_falta_envido_in_the_buenas_is_what_the_leader_still_needs():
    assert not rules.falta_decides_game([15, 3], 30)
    assert rules.falta_envido_points([20, 11], 30, winner_score=11) == 10
    assert rules.falta_envido_points([15, 3], 30, winner_score=3) == 15
    assert rules.falta_envido_points([29, 29], 30, winner_score=29) == 1
    # In the buenas the value does not depend on who wins the envido: it is what the
    # leading side still needs, whether the leader or the trailing side collects it.
    assert rules.falta_envido_points([20, 11], 30, winner_score=20) == 10
    assert rules.falta_envido_points([20, 11], 30, winner_score=11) == 10
    assert rules.falta_envido_points([11, 22], 30, winner_score=11) == 8
    assert rules.falta_envido_points([11, 22], 30, winner_score=22) == 8


def test_falta_envido_in_a_fifteen_point_game_has_no_malas():
    assert not rules.falta_decides_game([0, 0], 15)
    assert rules.falta_envido_points([4, 2], 15, winner_score=2) == 11
    assert rules.falta_envido_points([14, 14], 15, winner_score=14) == 1


@pytest.mark.parametrize(
    ("results", "mano_team", "expected"),
    [
        ([], 0, None),
        ([0], 1, None),
        ([None], 0, None),
        ([0, 0], 1, 0),
        ([1, 1], 0, 1),
        ([0, 1], 0, None),
        ([0, None], 1, 0),
        ([1, None], 0, 1),
        ([None, 1], 0, 1),
        ([None, 0], 1, 0),
        ([None, None], 1, None),
        ([0, 1, 1], 0, 1),
        ([0, 1, 0], 1, 0),
        ([0, 1, None], 1, 0),
        ([1, 0, None], 0, 1),
        ([None, None, 0], 1, 0),
        ([None, None, None], 1, 1),
        ([None, None, None], 0, 0),
    ],
)
def test_decide_hand(results, mano_team, expected):
    assert rules.decide_hand(results, mano_team) == expected


def test_flor_point_values():
    assert rules.FLOR_POINTS == 3
    assert rules.CONTRAFLOR_POINTS == 6


def test_format_card_uses_localized_names():
    ace = card(1, cards.SUIT_ESPADAS)
    assert cards.format_card(ace, "en") == "1 of Swords"
    assert cards.format_card(ace, "es") == "1 de espadas"
    assert cards.format_card(card(12, cards.SUIT_OROS), "es") == "12 de oros"
    assert cards.format_card(card(7, cards.SUIT_BASTOS), "pt") == "7 de paus"


def test_sort_key_orders_hand_strongest_first():
    hand = [card(4, "oros", 0), card(1, "espadas", 1), card(7, "copas", 2)]
    assert [c.id for c in sorted(hand, key=cards.sort_key)] == [1, 2, 0]


def test_envido_cards_and_flor_cards():
    from ..games.truco.cards import TrucoCard

    def card(card_id, rank, suit):
        return TrucoCard(id=card_id, rank=rank, suit=suit)

    pair = [card(1, 7, "espadas"), card(2, 6, "espadas"), card(3, 1, "oros")]
    assert {c.id for c in rules.envido_cards(pair)} == {1, 2}
    singles = [card(1, 7, "espadas"), card(2, 6, "oros"), card(3, 12, "copas")]
    assert [c.id for c in rules.envido_cards(singles)] == [1]
    flor = [card(1, 7, "oros"), card(2, 4, "oros"), card(3, 12, "oros")]
    assert {c.id for c in rules.flor_cards(flor)} == {1, 2, 3}
    assert rules.flor_cards(pair) == []


def test_flor_declined_points():
    assert rules.flor_declined_points([rules.CONTRAFLOR]) == 4
    assert rules.flor_declined_points([rules.CONTRAFLOR_AL_RESTO]) == 4
    assert (
        rules.flor_declined_points([rules.CONTRAFLOR, rules.CONTRAFLOR_AL_RESTO]) == 6
    )
