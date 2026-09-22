"""Serialized spatial effects for Breach Point tactical areas."""

from dataclasses import dataclass, field


@dataclass
class AreaEffectState:
    """One bounded, observable effect occupying a named tactical area."""

    effect: str
    utility_id: str
    node_id: str
    source_player_id: str
    expires_at_tactical_round: int
    known_team_indexes: list[int] = field(default_factory=list)
    affected_player_rounds: dict[str, int] = field(default_factory=dict)
