"""High Noon and A Fistful of Cards event definitions."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ...messages.localization import Localization

NO_EVENTS = "none"
HIGH_NOON_SET = "high_noon"
FISTFUL_SET = "fistful"
COMBINED_EVENTS = "combined"
EVENT_MODES = (NO_EVENTS, HIGH_NOON_SET, FISTFUL_SET, COMBINED_EVENTS)

HIGH_NOON = "high_noon"
FISTFUL_OF_CARDS = "fistful_of_cards"


@dataclass(frozen=True)
class EventDefinition:
    id: str
    set_id: str
    final: bool = False


HIGH_NOON_EVENTS = (
    EventDefinition("blessing", HIGH_NOON_SET),
    EventDefinition("curse", HIGH_NOON_SET),
    EventDefinition("ghost_town", HIGH_NOON_SET),
    EventDefinition("gold_rush", HIGH_NOON_SET),
    EventDefinition("hangover", HIGH_NOON_SET),
    EventDefinition(HIGH_NOON, HIGH_NOON_SET, True),
    EventDefinition("shootout", HIGH_NOON_SET),
    EventDefinition("the_daltons", HIGH_NOON_SET),
    EventDefinition("the_doctor", HIGH_NOON_SET),
    EventDefinition("the_reverend", HIGH_NOON_SET),
    EventDefinition("the_sermon", HIGH_NOON_SET),
    EventDefinition("thirst", HIGH_NOON_SET),
    EventDefinition("train_arrival", HIGH_NOON_SET),
    EventDefinition("handcuffs", HIGH_NOON_SET),
    EventDefinition("new_identity", HIGH_NOON_SET),
)

FISTFUL_EVENTS = (
    EventDefinition(FISTFUL_OF_CARDS, FISTFUL_SET, True),
    EventDefinition("abandoned_mine", FISTFUL_SET),
    EventDefinition("ambush", FISTFUL_SET),
    EventDefinition("blood_brothers", FISTFUL_SET),
    EventDefinition("dead_man", FISTFUL_SET),
    EventDefinition("hard_liquor", FISTFUL_SET),
    EventDefinition("lasso", FISTFUL_SET),
    EventDefinition("law_of_the_west", FISTFUL_SET),
    EventDefinition("peyote", FISTFUL_SET),
    EventDefinition("ranch", FISTFUL_SET),
    EventDefinition("ricochet", FISTFUL_SET),
    EventDefinition("russian_roulette", FISTFUL_SET),
    EventDefinition("sniper", FISTFUL_SET),
    EventDefinition("the_judge", FISTFUL_SET),
    EventDefinition("vendetta", FISTFUL_SET),
)

ALL_EVENTS = HIGH_NOON_EVENTS + FISTFUL_EVENTS
EVENTS = {event.id: event for event in ALL_EVENTS}

assert len(HIGH_NOON_EVENTS) == 15
assert len(FISTFUL_EVENTS) == 15


def build_event_deck(mode: str) -> list[str]:
    """Build a reveal-order event deck, ending in its permanent final event."""

    if mode == NO_EVENTS:
        return []
    if mode == HIGH_NOON_SET:
        regular = [event.id for event in HIGH_NOON_EVENTS if not event.final]
        random.shuffle(regular)
        return [*regular, HIGH_NOON]
    if mode == FISTFUL_SET:
        regular = [event.id for event in FISTFUL_EVENTS if not event.final]
        random.shuffle(regular)
        return [*regular, FISTFUL_OF_CARDS]
    if mode == COMBINED_EVENTS:
        regular = [event.id for event in ALL_EVENTS if not event.final]
        random.shuffle(regular)
        final = random.choice((HIGH_NOON, FISTFUL_OF_CARDS))
        return [*regular[:12], final]
    return []


def event_name(event_id: str, locale: str) -> str:
    return Localization.get(locale, f"bang-event-{event_id.replace('_', '-')}")


def event_description(event_id: str, locale: str) -> str:
    return Localization.get(
        locale,
        f"bang-event-{event_id.replace('_', '-')}-description",
    )
