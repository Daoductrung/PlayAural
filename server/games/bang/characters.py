"""Character definitions included in BANG! The Bullet."""

from __future__ import annotations

from dataclasses import dataclass

from ...messages.localization import Localization
from .cards import BASE, DODGE_CITY


@dataclass(frozen=True)
class CharacterDefinition:
    id: str
    life: int
    expansion: str = BASE


BASE_CHARACTERS = (
    CharacterDefinition("bart_cassidy", 4),
    CharacterDefinition("black_jack", 4),
    CharacterDefinition("calamity_janet", 4),
    CharacterDefinition("el_gringo", 3),
    CharacterDefinition("jesse_jones", 4),
    CharacterDefinition("jourdonnais", 4),
    CharacterDefinition("kit_carlson", 4),
    CharacterDefinition("lucky_duke", 4),
    CharacterDefinition("paul_regret", 3),
    CharacterDefinition("pedro_ramirez", 4),
    CharacterDefinition("rose_doolan", 4),
    CharacterDefinition("sid_ketchum", 4),
    CharacterDefinition("slab_the_killer", 4),
    CharacterDefinition("suzy_lafayette", 4),
    CharacterDefinition("vulture_sam", 4),
    CharacterDefinition("willy_the_kid", 4),
)

DODGE_CITY_CHARACTERS = (
    CharacterDefinition("apache_kid", 3, DODGE_CITY),
    CharacterDefinition("belle_star", 4, DODGE_CITY),
    CharacterDefinition("bill_noface", 4, DODGE_CITY),
    CharacterDefinition("chuck_wengam", 4, DODGE_CITY),
    CharacterDefinition("doc_holyday", 4, DODGE_CITY),
    CharacterDefinition("elena_fuente", 3, DODGE_CITY),
    CharacterDefinition("greg_digger", 4, DODGE_CITY),
    CharacterDefinition("herb_hunter", 4, DODGE_CITY),
    CharacterDefinition("jose_delgado", 4, DODGE_CITY),
    CharacterDefinition("molly_stark", 4, DODGE_CITY),
    CharacterDefinition("pat_brennan", 4, DODGE_CITY),
    CharacterDefinition("pixie_pete", 3, DODGE_CITY),
    CharacterDefinition("sean_mallory", 3, DODGE_CITY),
    CharacterDefinition("tequila_joe", 4, DODGE_CITY),
    CharacterDefinition("vera_custer", 3, DODGE_CITY),
)

PROMO_CHARACTERS = (
    CharacterDefinition("claus_the_saint", 3, "bullet_promo"),
    CharacterDefinition("johnny_kisch", 4, "bullet_promo"),
    CharacterDefinition("uncle_will", 4, "bullet_promo"),
)

ALL_CHARACTERS = BASE_CHARACTERS + DODGE_CITY_CHARACTERS + PROMO_CHARACTERS
CHARACTERS = {definition.id: definition for definition in ALL_CHARACTERS}

assert len(ALL_CHARACTERS) == 34


def character_name(character_id: str, locale: str) -> str:
    return Localization.get(
        locale,
        f"bang-character-{character_id.replace('_', '-')}",
    )


def character_ability(character_id: str, locale: str) -> str:
    return Localization.get(
        locale,
        f"bang-character-{character_id.replace('_', '-')}-ability",
    )
