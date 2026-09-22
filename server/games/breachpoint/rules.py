"""Rule and match profiles for Breach Point."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BreachPointRules:
    """Numbers that define one reusable tactical rules profile."""

    max_health: int
    action_points_per_activation: int
    maximum_evasion_points: int
    stationary_evasion_decay_per_activation: int
    allow_contested_entry: bool
    move_cost: int
    disengage_cost: int
    plant_cost: int
    defuse_cost: int
    bomb_pickup_cost: int
    weapon_pickup_cost: int
    maximum_utility_items: int
    repeat_objective_response_action_points: int
    preplant_tactical_round_limit: int
    bomb_fuse_tactical_rounds: int
    overtime_half_rounds: int


@dataclass(frozen=True)
class MatchFormat:
    """One regulation match length expressed as rounds per half."""

    id: str
    rounds_per_half: int

    @property
    def regulation_rounds(self) -> int:
        return self.rounds_per_half * 2

    @property
    def rounds_to_win(self) -> int:
        return self.rounds_per_half + 1


STANDARD_RULES = BreachPointRules(
    max_health=100,
    action_points_per_activation=2,
    maximum_evasion_points=2,
    stationary_evasion_decay_per_activation=1,
    allow_contested_entry=True,
    move_cost=1,
    disengage_cost=2,
    plant_cost=1,
    defuse_cost=2,
    bomb_pickup_cost=1,
    weapon_pickup_cost=1,
    maximum_utility_items=4,
    repeat_objective_response_action_points=1,
    preplant_tactical_round_limit=6,
    bomb_fuse_tactical_rounds=3,
    overtime_half_rounds=3,
)


_MATCH_FORMAT_PROFILES = (
    MatchFormat(id="mr7", rounds_per_half=7),
    MatchFormat(id="mr12", rounds_per_half=12),
    MatchFormat(id="mr15", rounds_per_half=15),
)
MATCH_FORMATS = {
    match_format.id: match_format for match_format in _MATCH_FORMAT_PROFILES
}
DEFAULT_MATCH_FORMAT_ID = "mr12"

OVERTIME_DRAW = "draw"
OVERTIME_MR3 = "mr3"
OVERTIME_MODES = (OVERTIME_DRAW, OVERTIME_MR3)
DEFAULT_OVERTIME_MODE = OVERTIME_MR3


def _validate_rules(rules: BreachPointRules) -> None:
    """Reject internally inconsistent tactical rules at import time."""

    positive_values = (
        rules.max_health,
        rules.action_points_per_activation,
        rules.move_cost,
        rules.disengage_cost,
        rules.plant_cost,
        rules.defuse_cost,
        rules.bomb_pickup_cost,
        rules.weapon_pickup_cost,
        rules.maximum_utility_items,
        rules.repeat_objective_response_action_points,
        rules.preplant_tactical_round_limit,
        rules.bomb_fuse_tactical_rounds,
        rules.overtime_half_rounds,
    )
    if any(value <= 0 for value in positive_values):
        raise ValueError("Breach Point action and timing values must be positive")
    if (
        rules.maximum_evasion_points < 0
        or rules.stationary_evasion_decay_per_activation < 0
    ):
        raise ValueError("Breach Point evasion values cannot be negative")
    if rules.maximum_evasion_points > rules.action_points_per_activation:
        raise ValueError("Maximum evasion cannot exceed activation action points")
    if (
        rules.repeat_objective_response_action_points
        > rules.action_points_per_activation
    ):
        raise ValueError("Repeat objective responses cannot exceed activation AP")
    if rules.disengage_cost < rules.move_cost:
        raise ValueError("Disengaging cannot cost less than ordinary movement")
    if any(
        cost > rules.action_points_per_activation
        for cost in (
            rules.move_cost,
            rules.disengage_cost,
            rules.plant_cost,
            rules.defuse_cost,
            rules.bomb_pickup_cost,
            rules.weapon_pickup_cost,
        )
    ):
        raise ValueError("Every base action cost must fit within one activation")


def _validate_match_formats(match_formats: tuple[MatchFormat, ...]) -> None:
    """Reject duplicate or unusable match profiles at import time."""

    ids = [match_format.id for match_format in match_formats]
    if any(
        not match_format.id or match_format.rounds_per_half <= 0
        for match_format in match_formats
    ):
        raise ValueError("Match formats require stable ids and positive half lengths")
    if len(ids) != len(set(ids)):
        raise ValueError("Match format ids must be unique")


_validate_rules(STANDARD_RULES)
_validate_match_formats(_MATCH_FORMAT_PROFILES)


def get_match_format(match_format_id: str) -> MatchFormat | None:
    """Return a registered regulation format by stable id."""

    return MATCH_FORMATS.get(match_format_id)
