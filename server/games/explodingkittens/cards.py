"""Card definitions and deck construction for Exploding Kittens."""

from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin

from ...messages.localization import Localization


EXPLODING_KITTEN = "exploding_kitten"
DEFUSE = "defuse"
NOPE = "nope"
ATTACK = "attack"
SKIP = "skip"
FAVOR = "favor"
SHUFFLE = "shuffle"
SEE_FUTURE = "see_future"
BEARD_CAT = "beard_cat"
CATTERMELON = "cattermelon"
HAIRY_POTATO_CAT = "hairy_potato_cat"
RAINBOW_RALPHING_CAT = "rainbow_ralphing_cat"
TACOCAT = "tacocat"

CAT_KINDS = (
    BEARD_CAT,
    CATTERMELON,
    HAIRY_POTATO_CAT,
    RAINBOW_RALPHING_CAT,
    TACOCAT,
)
ACTION_KINDS = (ATTACK, SKIP, FAVOR, SHUFFLE, SEE_FUTURE)
REQUESTABLE_KINDS = (DEFUSE, NOPE, ATTACK, SKIP, FAVOR, SHUFFLE, SEE_FUTURE, *CAT_KINDS)

CARD_COUNTS = {
    EXPLODING_KITTEN: 4,
    DEFUSE: 6,
    NOPE: 5,
    ATTACK: 4,
    SKIP: 4,
    FAVOR: 4,
    SHUFFLE: 4,
    SEE_FUTURE: 5,
    BEARD_CAT: 4,
    CATTERMELON: 4,
    HAIRY_POTATO_CAT: 4,
    RAINBOW_RALPHING_CAT: 4,
    TACOCAT: 4,
}

CARD_SORT_ORDER = {
    DEFUSE: 0,
    ATTACK: 1,
    SKIP: 2,
    FAVOR: 3,
    SHUFFLE: 4,
    SEE_FUTURE: 5,
    NOPE: 6,
    **{kind: 7 + index for index, kind in enumerate(CAT_KINDS)},
    EXPLODING_KITTEN: 99,
}


@dataclass(frozen=True)
class ExplodingKittensCard(DataClassJSONMixin):
    """A uniquely identifiable card."""

    id: int
    kind: str


def build_full_deck() -> list[ExplodingKittensCard]:
    """Return the complete 56-card Original Edition deck."""
    cards: list[ExplodingKittensCard] = []
    card_id = 1
    for kind, count in CARD_COUNTS.items():
        for _ in range(count):
            cards.append(ExplodingKittensCard(id=card_id, kind=kind))
            card_id += 1
    return cards


def card_name(kind_or_card: str | ExplodingKittensCard, locale: str) -> str:
    """Return a localized card name."""
    kind = kind_or_card.kind if isinstance(kind_or_card, ExplodingKittensCard) else kind_or_card
    return Localization.get(locale, f"explodingkittens-card-{kind.replace('_', '-')}")


def sort_cards(cards: list[ExplodingKittensCard]) -> list[ExplodingKittensCard]:
    """Return cards in a stable, useful hand order."""
    return sorted(cards, key=lambda card: (CARD_SORT_ORDER.get(card.kind, 98), card.id))
