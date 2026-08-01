"""Mashumaro-safe committed and private state for BANG!."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro.mixins.json import DataClassJSONMixin

from .cards import BangCard

PHASE_STARTING = "starting"
PHASE_START_TURN = "start_turn"
PHASE_DRAW = "draw"
PHASE_PLAY = "play"
PHASE_DISCARD = "discard"
PHASE_RESOLVING = "resolving"
PHASE_GAME_OVER = "game_over"


@dataclass
class DamageSource(DataClassJSONMixin):
    """Attribution preserved across nested defense and death resolution."""

    player_id: str = ""
    kind: str = ""
    card_kind: str = ""


@dataclass
class BangEffect(DataClassJSONMixin):
    """One frame in the serialized rules interpreter."""

    kind: str
    stage: str = "start"
    actor_id: str = ""
    target_id: str = ""
    player_ids: list[str] = field(default_factory=list)
    card_ids: list[int] = field(default_factory=list)
    index: int = 0
    amount: int = 0
    required: int = 0
    source: DamageSource = field(default_factory=DamageSource)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class BangDecision(DataClassJSONMixin):
    """Exactly one player's current semantic choice."""

    kind: str
    player_id: str
    prompt_key: str = ""
    card_ids: list[int] = field(default_factory=list)
    player_ids: list[str] = field(default_factory=list)
    item_ids: list[str] = field(default_factory=list)
    selected_card_ids: list[int] = field(default_factory=list)
    required: int = 0
    allow_skip: bool = False
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class BangPlayIntent(DataClassJSONMixin):
    """A reversible card/ability selection before costs are committed."""

    kind: str
    actor_id: str
    card_id: int = 0
    selected_card_ids: list[int] = field(default_factory=list)
    target_id: str = ""
    in_play_card_id: int = 0
    required: int = 0
    stage: str = "start"
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolvingCard(DataClassJSONMixin):
    """The main play held out of the discard pile until its effect ends."""

    card: BangCard
    actor_id: str
    from_in_play: bool = False
