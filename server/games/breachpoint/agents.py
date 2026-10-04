"""Cosmetic Counter-Strike-style agent personas for Breach Point."""

from __future__ import annotations

from dataclasses import dataclass

from .arsenal import (
    FLASHBANG,
    HE_GRENADE,
    INCENDIARY_GRENADE,
    MOLOTOV,
    SIDE_COUNTER_TERRORISTS,
    SIDE_INDEXES,
    SIDE_TERRORISTS,
    SMOKE_GRENADE,
)


AGENT_GENDER_FEMALE = "female"
AGENT_GENDER_MALE = "male"
AGENT_GENDERS = frozenset({AGENT_GENDER_FEMALE, AGENT_GENDER_MALE})

AGENT_VOICE_ROUND_START = "round_start"
AGENT_VOICE_THROW_SMOKE = "throw_smoke"
AGENT_VOICE_THROW_FLASHBANG = "throw_flashbang"
AGENT_VOICE_THROW_HE_GRENADE = "throw_he_grenade"
AGENT_VOICE_THROW_MOLOTOV = "throw_molotov"
AGENT_VOICE_THROW_INCENDIARY = "throw_incendiary"
AGENT_VOICE_PLANT = "plant"
AGENT_VOICE_PLANT_SITE_EVENTS = ("plant_site_a", "plant_site_b")
AGENT_VOICE_DEFUSE = "defuse"
AGENT_VOICE_VARIANTS_PER_EVENT = 3
AGENT_VOICE_EVENTS = frozenset(
    {
        AGENT_VOICE_ROUND_START,
        AGENT_VOICE_THROW_SMOKE,
        AGENT_VOICE_THROW_FLASHBANG,
        AGENT_VOICE_THROW_HE_GRENADE,
        AGENT_VOICE_THROW_MOLOTOV,
        AGENT_VOICE_THROW_INCENDIARY,
        AGENT_VOICE_PLANT,
        AGENT_VOICE_DEFUSE,
    }
)

AGENT_AUDIO_ROOT = "game_breachpoint/agents"
AGENT_RADIO_CLICK_ASSET = f"{AGENT_AUDIO_ROOT}/radio_click.ogg"


@dataclass(frozen=True)
class AgentPersona:
    """One side-specific voice persona with a deliberately small callout set."""

    id: str
    display_name: str
    gender: str
    side_index: int
    voice_assets: tuple[tuple[str, tuple[str, ...]], ...]

    def assets_for(self, event: str) -> tuple[str, ...]:
        """Return the authored variants for one semantic callout."""

        return next(
            (assets for event_id, assets in self.voice_assets if event_id == event),
            (),
        )

    @property
    def all_assets(self) -> tuple[str, ...]:
        return tuple(
            asset
            for _, assets in self.voice_assets
            for asset in assets
        )


def _voice_assets(
    persona_id: str,
    *events: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Build canonical destination paths for a persona's selected callouts."""

    return tuple(
        (
            event,
            tuple(
                f"{AGENT_AUDIO_ROOT}/{persona_id}/{event}{variant}.ogg"
                for variant in range(1, AGENT_VOICE_VARIANTS_PER_EVENT + 1)
            ),
        )
        for event in events
    )


_COMMON_EVENTS = (
    AGENT_VOICE_ROUND_START,
    AGENT_VOICE_THROW_SMOKE,
    AGENT_VOICE_THROW_FLASHBANG,
    AGENT_VOICE_THROW_HE_GRENADE,
)
_TERRORIST_EVENTS = (*_COMMON_EVENTS, AGENT_VOICE_THROW_MOLOTOV)
_COUNTER_TERRORIST_EVENTS = (*_COMMON_EVENTS, AGENT_VOICE_THROW_INCENDIARY)

AGENT_PERSONAS = (
    AgentPersona(
        id="doctor_romanov",
        display_name="The 'Doctor' Romanov",
        gender=AGENT_GENDER_MALE,
        side_index=SIDE_TERRORISTS,
        voice_assets=_voice_assets(
            "doctor_romanov",
            *_TERRORIST_EVENTS,
            *AGENT_VOICE_PLANT_SITE_EVENTS,
        ),
    ),
    AgentPersona(
        id="sir_bloody_darryl",
        display_name="Sir Bloody Darryl",
        gender=AGENT_GENDER_MALE,
        side_index=SIDE_TERRORISTS,
        voice_assets=_voice_assets(
            "sir_bloody_darryl",
            *_TERRORIST_EVENTS,
            AGENT_VOICE_PLANT,
        ),
    ),
    AgentPersona(
        id="safecracker_voltzmann",
        display_name="Safecracker Voltzmann",
        gender=AGENT_GENDER_FEMALE,
        side_index=SIDE_TERRORISTS,
        voice_assets=_voice_assets(
            "safecracker_voltzmann",
            *_TERRORIST_EVENTS,
            AGENT_VOICE_PLANT,
        ),
    ),
    AgentPersona(
        id="crasswater",
        display_name="Crasswater The Forgotten",
        gender=AGENT_GENDER_MALE,
        side_index=SIDE_TERRORISTS,
        voice_assets=_voice_assets(
            "crasswater",
            *_TERRORIST_EVENTS,
            AGENT_VOICE_PLANT,
        ),
    ),
    AgentPersona(
        id="vypa_sista",
        display_name="Vypa Sista of the New Revolution",
        gender=AGENT_GENDER_FEMALE,
        side_index=SIDE_TERRORISTS,
        voice_assets=_voice_assets(
            "vypa_sista",
            *_TERRORIST_EVENTS,
            AGENT_VOICE_PLANT,
        ),
    ),
    AgentPersona(
        id="special_agent_ava",
        display_name="Special Agent Ava",
        gender=AGENT_GENDER_FEMALE,
        side_index=SIDE_COUNTER_TERRORISTS,
        voice_assets=_voice_assets(
            "special_agent_ava",
            *_COUNTER_TERRORIST_EVENTS,
            AGENT_VOICE_DEFUSE,
        ),
    ),
    AgentPersona(
        id="lt_commander_ricksaw",
        display_name="Lt. Commander Ricksaw",
        gender=AGENT_GENDER_MALE,
        side_index=SIDE_COUNTER_TERRORISTS,
        voice_assets=_voice_assets(
            "lt_commander_ricksaw",
            *_COUNTER_TERRORIST_EVENTS,
            AGENT_VOICE_DEFUSE,
        ),
    ),
    AgentPersona(
        id="cmdr_davida_fernandez",
        display_name="Skipper Davida 'Goggles' Fernandez",
        gender=AGENT_GENDER_FEMALE,
        side_index=SIDE_COUNTER_TERRORISTS,
        voice_assets=_voice_assets(
            "cmdr_davida_fernandez",
            *_COUNTER_TERRORIST_EVENTS,
            AGENT_VOICE_DEFUSE,
        ),
    ),
    AgentPersona(
        id="chef_rouchard",
        display_name="Chef d'Escadron Rouchard",
        gender=AGENT_GENDER_FEMALE,
        side_index=SIDE_COUNTER_TERRORISTS,
        voice_assets=_voice_assets(
            "chef_rouchard",
            *_COUNTER_TERRORIST_EVENTS,
            AGENT_VOICE_DEFUSE,
        ),
    ),
    AgentPersona(
        id="lieutenant_rex_krikey",
        display_name="Lieutenant Rex Krikey",
        gender=AGENT_GENDER_MALE,
        side_index=SIDE_COUNTER_TERRORISTS,
        voice_assets=_voice_assets(
            "lieutenant_rex_krikey",
            *_COUNTER_TERRORIST_EVENTS,
            AGENT_VOICE_DEFUSE,
        ),
    ),
)

AGENT_PERSONAS_BY_ID = {persona.id: persona for persona in AGENT_PERSONAS}
AGENT_PERSONAS_BY_SIDE = {
    side_index: tuple(
        persona for persona in AGENT_PERSONAS if persona.side_index == side_index
    )
    for side_index in SIDE_INDEXES
}
AGENT_VOICE_ASSETS = tuple(
    asset for persona in AGENT_PERSONAS for asset in persona.all_assets
)

AGENT_VOICE_EVENT_BY_UTILITY_ID = {
    SMOKE_GRENADE.id: AGENT_VOICE_THROW_SMOKE,
    FLASHBANG.id: AGENT_VOICE_THROW_FLASHBANG,
    HE_GRENADE.id: AGENT_VOICE_THROW_HE_GRENADE,
    MOLOTOV.id: AGENT_VOICE_THROW_MOLOTOV,
    INCENDIARY_GRENADE.id: AGENT_VOICE_THROW_INCENDIARY,
}


def get_agent_persona(persona_id: str) -> AgentPersona | None:
    return AGENT_PERSONAS_BY_ID.get(persona_id)


def get_agent_personas_for_side(side_index: int) -> tuple[AgentPersona, ...]:
    return AGENT_PERSONAS_BY_SIDE.get(side_index, ())


def get_utility_voice_event(utility_id: str) -> str:
    return AGENT_VOICE_EVENT_BY_UTILITY_ID.get(utility_id, "")


def _validate_agent_personas() -> None:
    if len(AGENT_PERSONAS_BY_ID) != len(AGENT_PERSONAS):
        raise ValueError("Breach Point agent persona ids must be unique")
    if set(AGENT_PERSONAS_BY_SIDE) != set(SIDE_INDEXES):
        raise ValueError("Breach Point requires an agent roster for every side")
    all_assets: list[str] = []
    for persona in AGENT_PERSONAS:
        if not persona.id or not persona.display_name:
            raise ValueError("Breach Point agent personas require ids and names")
        if persona.gender not in AGENT_GENDERS:
            raise ValueError(f"Invalid gender for agent persona {persona.id}")
        if persona.side_index not in SIDE_INDEXES:
            raise ValueError(f"Invalid side for agent persona {persona.id}")
        event_ids = [event for event, _ in persona.voice_assets]
        if len(set(event_ids)) != len(event_ids):
            raise ValueError(f"Duplicate voice event for agent persona {persona.id}")
        unknown_events = {
            event
            for event in event_ids
            if event not in AGENT_VOICE_EVENTS
            and event not in AGENT_VOICE_PLANT_SITE_EVENTS
        }
        if unknown_events:
            raise ValueError(
                f"Unknown voice events for agent persona {persona.id}: "
                f"{sorted(unknown_events)}"
            )
        required_events = set(
            _TERRORIST_EVENTS
            if persona.side_index == SIDE_TERRORISTS
            else _COUNTER_TERRORIST_EVENTS
        )
        required_events.add(
            AGENT_VOICE_PLANT
            if persona.side_index == SIDE_TERRORISTS
            else AGENT_VOICE_DEFUSE
        )
        has_site_specific_plant = (
            persona.side_index == SIDE_TERRORISTS
            and set(AGENT_VOICE_PLANT_SITE_EVENTS).issubset(event_ids)
        )
        missing = required_events - set(event_ids)
        if missing == {AGENT_VOICE_PLANT} and has_site_specific_plant:
            missing.clear()
        if missing:
            raise ValueError(
                f"Agent persona {persona.id} is missing voice events: {sorted(missing)}"
            )
        for _, assets in persona.voice_assets:
            if not assets:
                raise ValueError(f"Empty voice event for agent persona {persona.id}")
            all_assets.extend(assets)
    if len(set(all_assets)) != len(all_assets):
        raise ValueError("Breach Point agent voice assets must be unique")
    if set(AGENT_VOICE_EVENT_BY_UTILITY_ID) != {
        SMOKE_GRENADE.id,
        FLASHBANG.id,
        HE_GRENADE.id,
        MOLOTOV.id,
        INCENDIARY_GRENADE.id,
    }:
        raise ValueError("Breach Point utility voice mapping is incomplete")


_validate_agent_personas()
