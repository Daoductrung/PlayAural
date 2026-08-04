"""Exact playing-card data for BANG! The Bullet, second edition."""

from __future__ import annotations

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin

from ...game_utils.cards import RANK_KEYS
from ...messages.localization import Localization

CLUBS = "clubs"
DIAMONDS = "diamonds"
HEARTS = "hearts"
SPADES = "spades"
SUITS = (CLUBS, DIAMONDS, HEARTS, SPADES)

BROWN = "brown"
BLUE = "blue"
GREEN = "green"

BASE = "base"
DODGE_CITY = "dodge_city"

BANG = "bang"
BARREL = "barrel"
BEER = "beer"
BIBLE = "bible"
BINOCULAR = "binocular"
BRAWL = "brawl"
BUFFALO_RIFLE = "buffalo_rifle"
CAN_CAN = "can_can"
CANTEEN = "canteen"
CAT_BALOU = "cat_balou"
CONESTOGA = "conestoga"
DERRINGER = "derringer"
DODGE = "dodge"
DUEL = "duel"
DYNAMITE = "dynamite"
GATLING = "gatling"
GENERAL_STORE = "general_store"
HIDEOUT = "hideout"
HOWITZER = "howitzer"
INDIANS = "indians"
IRON_PLATE = "iron_plate"
JAIL = "jail"
KNIFE = "knife"
MISSED = "missed"
MUSTANG = "mustang"
PANIC = "panic"
PEPPERBOX = "pepperbox"
PONY_EXPRESS = "pony_express"
PUNCH = "punch"
RAG_TIME = "rag_time"
REMINGTON = "remington"
REV_CARABINE = "rev_carabine"
SALOON = "saloon"
SCHOFIELD = "schofield"
SCOPE = "scope"
SOMBRERO = "sombrero"
SPRINGFIELD = "springfield"
STAGECOACH = "stagecoach"
TEN_GALLON_HAT = "ten_gallon_hat"
TEQUILA = "tequila"
VOLCANIC = "volcanic"
WELLS_FARGO = "wells_fargo"
WHISKY = "whisky"
WINCHESTER = "winchester"

WEAPON_RANGES = {
    VOLCANIC: 1,
    SCHOFIELD: 2,
    REMINGTON: 3,
    REV_CARABINE: 4,
    WINCHESTER: 5,
}
WEAPONS = frozenset(WEAPON_RANGES)

GREEN_MISSED_CARDS = frozenset(
    {BIBLE, IRON_PLATE, SOMBRERO, TEN_GALLON_HAT}
)
GREEN_ATTACK_CARDS = frozenset(
    {BUFFALO_RIFLE, DERRINGER, HOWITZER, KNIFE, PEPPERBOX}
)
EXTRA_COST_CARDS = frozenset({BRAWL, RAG_TIME, SPRINGFIELD, TEQUILA, WHISKY})
HEAL_CARDS = frozenset({BEER, CANTEEN, TEQUILA, WHISKY, SALOON})

RANK_ORDER = {
    rank: index
    for index, rank in enumerate(
        ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
    )
}
RANK_VALUES = {
    **{str(value): value for value in range(2, 11)},
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 1,
}
SUIT_KEYS = {
    CLUBS: "suit-clubs",
    DIAMONDS: "suit-diamonds",
    HEARTS: "suit-hearts",
    SPADES: "suit-spades",
}

CARD_SORT_ORDER = {
    BANG: 0,
    MISSED: 1,
    DODGE: 2,
    BEER: 3,
    DUEL: 4,
    INDIANS: 5,
    GATLING: 6,
    PANIC: 7,
    CAT_BALOU: 8,
    GENERAL_STORE: 9,
    SALOON: 10,
    STAGECOACH: 11,
    WELLS_FARGO: 12,
    BRAWL: 13,
    PUNCH: 14,
    RAG_TIME: 15,
    SPRINGFIELD: 16,
    TEQUILA: 17,
    WHISKY: 18,
    VOLCANIC: 30,
    SCHOFIELD: 31,
    REMINGTON: 32,
    REV_CARABINE: 33,
    WINCHESTER: 34,
    BARREL: 35,
    MUSTANG: 36,
    SCOPE: 37,
    BINOCULAR: 38,
    HIDEOUT: 39,
    JAIL: 40,
    DYNAMITE: 41,
    BIBLE: 50,
    IRON_PLATE: 51,
    SOMBRERO: 52,
    TEN_GALLON_HAT: 53,
    BUFFALO_RIFLE: 54,
    CAN_CAN: 55,
    CANTEEN: 56,
    CONESTOGA: 57,
    DERRINGER: 58,
    HOWITZER: 59,
    KNIFE: 60,
    PEPPERBOX: 61,
    PONY_EXPRESS: 62,
}


@dataclass(frozen=True)
class BangCard(DataClassJSONMixin):
    """One uniquely identifiable physical playing card."""

    id: int
    kind: str
    suit: str
    rank: str
    border: str
    expansion: str = BASE


@dataclass
class BangInPlayCard(DataClassJSONMixin):
    """A public blue/green card and its green-card readiness boundary."""

    card: BangCard
    usable_after_turn: int = 0


CardSpec = tuple[str, str, str, str]


def _expanded(
    kind: str,
    border: str,
    suit: str,
    ranks: tuple[str, ...],
) -> list[CardSpec]:
    return [(kind, suit, rank, border) for rank in ranks]


BASE_CARD_SPECS: list[CardSpec] = [
    (REMINGTON, CLUBS, "K", BLUE),
    (REV_CARABINE, CLUBS, "A", BLUE),
    *_expanded(SCHOFIELD, BLUE, CLUBS, ("J", "Q")),
    (SCHOFIELD, SPADES, "K", BLUE),
    (VOLCANIC, SPADES, "10", BLUE),
    (VOLCANIC, CLUBS, "10", BLUE),
    (WINCHESTER, SPADES, "8", BLUE),
    *_expanded(BARREL, BLUE, SPADES, ("Q", "K")),
    (DYNAMITE, HEARTS, "2", BLUE),
    (JAIL, SPADES, "J", BLUE),
    (JAIL, HEARTS, "4", BLUE),
    (JAIL, SPADES, "10", BLUE),
    *_expanded(MUSTANG, BLUE, HEARTS, ("8", "9")),
    (SCOPE, SPADES, "A", BLUE),
    *_expanded(INDIANS, BROWN, DIAMONDS, ("K", "A")),
    (BANG, SPADES, "A", BROWN),
    *_expanded(
        BANG,
        BROWN,
        DIAMONDS,
        ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"),
    ),
    *_expanded(BANG, BROWN, CLUBS, ("2", "3", "4", "5", "6", "7", "8", "9")),
    *_expanded(BANG, BROWN, HEARTS, ("Q", "K", "A")),
    *_expanded(BEER, BROWN, HEARTS, ("6", "7", "8", "9", "10", "J")),
    (CAT_BALOU, HEARTS, "K", BROWN),
    *_expanded(CAT_BALOU, BROWN, DIAMONDS, ("9", "10", "J")),
    (DUEL, DIAMONDS, "Q", BROWN),
    (DUEL, SPADES, "J", BROWN),
    (DUEL, CLUBS, "8", BROWN),
    (GATLING, HEARTS, "10", BROWN),
    (GENERAL_STORE, CLUBS, "9", BROWN),
    (GENERAL_STORE, SPADES, "Q", BROWN),
    *_expanded(MISSED, BROWN, CLUBS, ("10", "J", "Q", "K", "A")),
    *_expanded(MISSED, BROWN, SPADES, ("2", "3", "4", "5", "6", "7", "8")),
    *_expanded(PANIC, BROWN, HEARTS, ("J", "Q", "A")),
    (PANIC, DIAMONDS, "8", BROWN),
    (SALOON, HEARTS, "5", BROWN),
    (STAGECOACH, SPADES, "9", BROWN),
    (STAGECOACH, SPADES, "9", BROWN),
    (WELLS_FARGO, HEARTS, "3", BROWN),
]

DODGE_CITY_CARD_SPECS: list[CardSpec] = [
    (REMINGTON, DIAMONDS, "6", BLUE),
    (REV_CARABINE, SPADES, "5", BLUE),
    (BARREL, CLUBS, "A", BLUE),
    (BINOCULAR, DIAMONDS, "10", BLUE),
    (DYNAMITE, CLUBS, "10", BLUE),
    (HIDEOUT, DIAMONDS, "K", BLUE),
    (MUSTANG, HEARTS, "5", BLUE),
    (BANG, SPADES, "8", BROWN),
    (BANG, CLUBS, "5", BROWN),
    (BANG, CLUBS, "6", BROWN),
    (BANG, CLUBS, "K", BROWN),
    (BEER, HEARTS, "6", BROWN),
    (BEER, SPADES, "6", BROWN),
    (BRAWL, SPADES, "J", BROWN),
    (CAT_BALOU, CLUBS, "8", BROWN),
    (DODGE, DIAMONDS, "7", BROWN),
    (DODGE, HEARTS, "K", BROWN),
    (GENERAL_STORE, SPADES, "A", BROWN),
    (INDIANS, DIAMONDS, "5", BROWN),
    (MISSED, DIAMONDS, "8", BROWN),
    (PANIC, HEARTS, "J", BROWN),
    (PUNCH, SPADES, "10", BROWN),
    (RAG_TIME, HEARTS, "9", BROWN),
    (SPRINGFIELD, SPADES, "K", BROWN),
    (TEQUILA, CLUBS, "9", BROWN),
    (WHISKY, DIAMONDS, "Q", BROWN),
    (BIBLE, HEARTS, "10", GREEN),
    (BUFFALO_RIFLE, CLUBS, "Q", GREEN),
    (CAN_CAN, CLUBS, "J", GREEN),
    (CANTEEN, HEARTS, "7", GREEN),
    (CONESTOGA, DIAMONDS, "9", GREEN),
    (DERRINGER, SPADES, "7", GREEN),
    (HOWITZER, SPADES, "9", GREEN),
    (IRON_PLATE, DIAMONDS, "A", GREEN),
    (IRON_PLATE, SPADES, "Q", GREEN),
    (KNIFE, HEARTS, "8", GREEN),
    (PEPPERBOX, HEARTS, "A", GREEN),
    (PONY_EXPRESS, DIAMONDS, "Q", GREEN),
    (SOMBRERO, CLUBS, "7", GREEN),
    (TEN_GALLON_HAT, DIAMONDS, "J", GREEN),
]

assert len(BASE_CARD_SPECS) == 80
assert len(DODGE_CITY_CARD_SPECS) == 40


def build_deck(*, include_extended_cards: bool = True) -> list[BangCard]:
    """Build the exact Bullet playing deck with stable unique IDs."""

    specs: list[tuple[CardSpec, str]] = [
        (spec, BASE) for spec in BASE_CARD_SPECS
    ]
    if include_extended_cards:
        specs.extend((spec, DODGE_CITY) for spec in DODGE_CITY_CARD_SPECS)
    return [
        BangCard(
            id=index,
            kind=spec[0],
            suit=spec[1],
            rank=spec[2],
            border=spec[3],
            expansion=expansion,
        )
        for index, (spec, expansion) in enumerate(specs, 1)
    ]


def card_name(kind_or_card: str | BangCard, locale: str) -> str:
    kind = kind_or_card.kind if isinstance(kind_or_card, BangCard) else kind_or_card
    return Localization.get(locale, f"bang-card-{kind.replace('_', '-')}")


def suit_name(suit: str, locale: str) -> str:
    key = SUIT_KEYS.get(suit)
    return Localization.get(locale, key) if key else suit


def rank_name(rank: str, locale: str) -> str:
    """Return the platform-standard localized name for a playing-card rank."""

    key = RANK_KEYS.get(RANK_VALUES.get(rank, 0))
    return Localization.get(locale, key) if key else rank


def card_label(card: BangCard, locale: str) -> str:
    playing_card = Localization.get(
        locale,
        "card-name",
        rank=rank_name(card.rank, locale),
        suit=suit_name(card.suit, locale),
    )
    return Localization.get(
        locale,
        "bang-card-label",
        card=card_name(card, locale),
        playing_card=playing_card,
    )


def card_description(kind_or_card: str | BangCard, locale: str) -> str:
    """Return the localized rules text for a card kind."""

    kind = kind_or_card.kind if isinstance(kind_or_card, BangCard) else kind_or_card
    return Localization.get(
        locale,
        f"bang-card-{kind.replace('_', '-')}-description",
    )


def card_play_name(card: BangCard, locale: str) -> str:
    """Return concise action-aware identity without the rules description."""
    label = card_label(card, locale)
    if card.kind == BANG:
        return Localization.get(locale, "bang-card-play-bang", card=label)
    if card.kind in WEAPONS:
        return Localization.get(locale, "bang-card-play-weapon", card=label)
    return label


def sort_cards(cards: list[BangCard]) -> list[BangCard]:
    return sorted(
        cards,
        key=lambda card: (
            CARD_SORT_ORDER.get(card.kind, 99),
            RANK_ORDER.get(card.rank, 99),
            SUITS.index(card.suit) if card.suit in SUITS else 99,
            card.id,
        ),
    )
