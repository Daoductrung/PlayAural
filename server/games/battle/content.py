"""Bundled content and typed registry helpers for Battle."""

from dataclasses import dataclass, field
import json
from functools import lru_cache
from pathlib import Path

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class BattleLocalizedName(DataClassJSONMixin):
    """Localized display text stored in the bundled registry."""

    en: str
    vi: str

    def for_locale(self, locale: str) -> str:
        if locale == "vi" and self.vi:
            return self.vi
        return self.en


@dataclass
class BattleEffectBlock(DataClassJSONMixin):
    """A single move effect block."""

    type: str
    min: int | None = None
    max: int | None = None
    change: int | None = None
    percent: int | None = None


@dataclass
class BattleMove(DataClassJSONMixin):
    """A built-in battle move definition."""

    id: str
    name: BattleLocalizedName
    targeting: str
    sound_path: str
    blocks: list[BattleEffectBlock] = field(default_factory=list)


@dataclass
class BattlePreset(DataClassJSONMixin):
    """A built-in fighter preset."""

    id: str
    name: BattleLocalizedName
    health: int
    attack: int
    defense: int
    speed: int
    move_ids: list[str] = field(default_factory=list)


@dataclass
class BattleRegistry(DataClassJSONMixin):
    """Bundled move and preset registry."""

    moves: list[BattleMove] = field(default_factory=list)
    presets: list[BattlePreset] = field(default_factory=list)


REGISTRY_PATH = Path(__file__).with_name("registry.json")


@lru_cache(maxsize=1)
def load_battle_registry() -> BattleRegistry:
    """Load bundled Battle content from disk."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
        return BattleRegistry.from_dict(json.load(handle))


@lru_cache(maxsize=1)
def get_move_map() -> dict[str, BattleMove]:
    """Return move definitions keyed by move id."""
    return {move.id: move for move in load_battle_registry().moves}


@lru_cache(maxsize=1)
def get_preset_map() -> dict[str, BattlePreset]:
    """Return preset definitions keyed by preset id."""
    return {preset.id: preset for preset in load_battle_registry().presets}

