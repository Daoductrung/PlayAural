"""Truco for PlayAural.

One game with three variants chosen in the options: Argentine Truco (Spanish
40-card deck, envido, optional flor), Brazilian Truco (Paulista: French deck,
vira and manilhas, mão de onze) and Spanish Truco (Valencian Truc: 22-card
deck, envit, joc fora). Played in two sides, individuals at a two-player table
and alternating teams otherwise.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field

from ...game_utils.options import BoolOption, MenuOption, TeamModeOption, option_field
from ..base import GameOptions
from ..registry import register_game
from .engine import (  # noqa: F401
    Reveal,
    TablePlay,
    TrucoEngine,
    TrucoPlayer,
)
from .variants import (
    RULE_SETS,
    VARIANT_ARGENTINE,
    VARIANT_BRAZILIAN,
    VARIANT_CHOICES,
    VARIANT_SPANISH,
)

TARGET_CHOICES = ["15", "30"]
TARGET_LABELS = {"15": "truco-length-15", "30": "truco-length-30"}
SPANISH_TARGET_CHOICES = ["24", "18"]
SPANISH_TARGET_LABELS = {
    "18": "trucospanish-length-18",
    "24": "trucospanish-length-24",
}
VARIANT_LABELS = {
    VARIANT_ARGENTINE: "truco-variant-argentine",
    VARIANT_BRAZILIAN: "truco-variant-brazilian",
    VARIANT_SPANISH: "truco-variant-spanish",
}
TEAM_MODES = ["individual", "2v2", "3v3"]


@dataclass
class TrucoOptions(GameOptions):
    """Options for Truco."""

    variant: str = option_field(
        MenuOption(
            default=VARIANT_ARGENTINE,
            choices=VARIANT_CHOICES,
            choice_labels=VARIANT_LABELS,
            value_key="mode",
            label="truco-set-variant",
            prompt="truco-select-variant",
            change_msg="truco-option-changed-variant",
            description="truco-desc-variant",
        )
    )
    target_length: str = option_field(
        MenuOption(
            default="15",
            choices=TARGET_CHOICES,
            choice_labels=TARGET_LABELS,
            value_key="mode",
            label="truco-set-length",
            prompt="truco-select-length",
            change_msg="truco-option-changed-length",
            description="truco-desc-length",
        ),
        visible_when=("variant", lambda value: value == VARIANT_ARGENTINE),
    )
    spanish_length: str = option_field(
        MenuOption(
            default="24",
            choices=SPANISH_TARGET_CHOICES,
            choice_labels=SPANISH_TARGET_LABELS,
            value_key="mode",
            label="trucospanish-set-length",
            prompt="trucospanish-select-length",
            change_msg="trucospanish-option-changed-length",
            description="trucospanish-desc-length",
        ),
        visible_when=("variant", lambda value: value == VARIANT_SPANISH),
    )
    flor: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="truco-set-flor",
            change_msg="truco-option-changed-flor",
            description="truco-desc-flor",
        ),
        visible_when=("variant", lambda value: value == VARIANT_ARGENTINE),
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            choices=TEAM_MODES,
            value_key="mode",
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
            description="truco-desc-team-mode",
        )
    )


def _rule_attributes() -> set[str]:
    names: set[str] = set()
    for rule_set in RULE_SETS.values():
        names |= {name for name in vars(rule_set) if not name.startswith("__")}
    return names


_RULE_ATTRIBUTES = frozenset(_rule_attributes())
_MISSING = object()


@register_game
@dataclass
class TrucoGame(TrucoEngine):
    """Truco, with the variant chosen in the options."""

    options: TrucoOptions = field(default_factory=TrucoOptions)

    @classmethod
    def get_name(cls) -> str:
        return "Truco"

    @classmethod
    def get_type(cls) -> str:
        return "truco"

    def __getattribute__(self, name: str):
        # Variant configuration and hooks resolve through the selected rule set.
        if name in _RULE_ATTRIBUTES:
            try:
                variant = object.__getattribute__(self, "options").variant
            except AttributeError:
                variant = VARIANT_ARGENTINE
            rule_set = RULE_SETS.get(variant)
            if rule_set is not None:
                found = inspect.getattr_static(rule_set, name, _MISSING)
                if found is not _MISSING:
                    if inspect.isfunction(found):
                        return found.__get__(self, type(self))
                    return found
        return super().__getattribute__(name)
