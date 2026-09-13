"""Player state for Breach Point."""

from dataclasses import dataclass, field

from ..base import Player


@dataclass
class BreachPointPlayer(Player):
    """Serialized per-seat tactical state."""

    squad_index: int = -1
    team_index: int = -1
    position_id: str = ""
    health: int = 0
    eliminated: bool = False
    action_points: int = 0
    shots_fired_this_activation: int = 0
    weapon_shots_fired_this_activation: dict[str, int] = field(default_factory=dict)
    weapon_target_ids_this_activation: dict[str, list[str]] = field(
        default_factory=dict
    )
    guard_points: int = 0
    guard_anchor_node_id: str = ""
    stationary_guard_activations: int = 0
    flash_penalty: int = 0
    cash: int = 0
    primary_weapon_id: str = ""
    equipped_weapon_id: str = ""
    armor: int = 0
    utility_counts: dict[str, int] = field(default_factory=dict)
    equipment_counts: dict[str, int] = field(default_factory=dict)
    held_angle_node_id: str = ""
    held_angle_origin_id: str = ""
