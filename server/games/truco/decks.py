"""Decks and card strength for the Paulista and Valencian variants."""

from __future__ import annotations

from ...messages.localization import Localization
from .cards import SUIT_BASTOS, SUIT_COPAS, SUIT_ESPADAS, SUIT_OROS, TrucoCard

# ---------------------------------------------------------------------------
# Truco Paulista: French 40-card deck (no 8, 9, 10), vira and manilhas
# ---------------------------------------------------------------------------

SUIT_CLUBS = "clubs"
SUIT_HEARTS = "hearts"
SUIT_SPADES = "spades"
SUIT_DIAMONDS = "diamonds"
FRENCH_SUITS = (
    SUIT_DIAMONDS,
    SUIT_SPADES,
    SUIT_HEARTS,
    SUIT_CLUBS,
)  # weakest to strongest
FRENCH_RANKS = (1, 2, 3, 4, 5, 6, 7, 11, 12, 13)  # ace, 2-7, jack, queen, king
# Circular order used to find the manilha from the vira.
MANILHA_SEQUENCE = (4, 5, 6, 7, 12, 11, 13, 1, 2, 3)
# Natural strength of ordinary cards: 3 > 2 > A > K > J > Q > 7 > 6 > 5 > 4.
NATURAL_POWER = {3: 10, 2: 9, 1: 8, 13: 7, 11: 6, 12: 5, 7: 4, 6: 3, 5: 2, 4: 1}
MANILHA_BASE = 20
FRENCH_RANK_KEYS = {
    1: "trucobrazilian-rank-ace",
    11: "trucobrazilian-rank-jack",
    12: "trucobrazilian-rank-queen",
    13: "trucobrazilian-rank-king",
}


def build_french_deck() -> list[TrucoCard]:
    deck: list[TrucoCard] = []
    card_id = 0
    for suit in FRENCH_SUITS:
        for rank in FRENCH_RANKS:
            deck.append(TrucoCard(id=card_id, rank=rank, suit=suit))
            card_id += 1
    return deck


def manilha_rank(vira: TrucoCard) -> int:
    index = MANILHA_SEQUENCE.index(vira.rank)
    return MANILHA_SEQUENCE[(index + 1) % len(MANILHA_SEQUENCE)]


def brazilian_power(card: TrucoCard, vira: TrucoCard | None) -> int:
    if vira is not None and card.rank == manilha_rank(vira):
        return MANILHA_BASE + FRENCH_SUITS.index(card.suit)
    return NATURAL_POWER[card.rank]


def format_french_card(card: TrucoCard, locale: str) -> str:
    rank_key = FRENCH_RANK_KEYS.get(card.rank)
    rank = Localization.get(locale, rank_key) if rank_key else str(card.rank)
    suit = Localization.get(locale, f"trucobrazilian-suit-{card.suit}")
    return Localization.get(locale, "trucobrazilian-card-name", rank=rank, suit=suit)


# ---------------------------------------------------------------------------
# Truc Valencià: 22-card Spanish deck
# ---------------------------------------------------------------------------

SPANISH_RANKS = (3, 4, 5, 6, 7)
_SPANISH_SPECIAL = {
    (1, SUIT_ESPADAS): 12,
    (1, SUIT_BASTOS): 11,
    (7, SUIT_ESPADAS): 10,
    (7, SUIT_OROS): 9,
    (7, SUIT_COPAS): 7,
    (7, SUIT_BASTOS): 7,
}
_SPANISH_RANK = {3: 8, 6: 6, 5: 5, 4: 4}
SPANISH_SUITS = (SUIT_OROS, SUIT_COPAS, SUIT_ESPADAS, SUIT_BASTOS)


def build_spanish_deck() -> list[TrucoCard]:
    deck: list[TrucoCard] = []
    card_id = 0
    for suit in SPANISH_SUITS:
        for rank in SPANISH_RANKS:
            deck.append(TrucoCard(id=card_id, rank=rank, suit=suit))
            card_id += 1
    deck.append(TrucoCard(id=card_id, rank=1, suit=SUIT_ESPADAS))
    deck.append(TrucoCard(id=card_id + 1, rank=1, suit=SUIT_BASTOS))
    return deck


def spanish_power(card: TrucoCard) -> int:
    special = _SPANISH_SPECIAL.get((card.rank, card.suit))
    if special is not None:
        return special
    return _SPANISH_RANK[card.rank]
