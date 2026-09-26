"""Rule and match profiles for Breach Point."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TacticalTimingProfile:
    """Round clocks tuned for one inclusive range of squad sizes."""

    minimum_team_size: int
    maximum_team_size: int
    preplant_tactical_round_limit: int
    bomb_fuse_tactical_rounds: int

    def supports(self, team_size: int) -> bool:
        return self.minimum_team_size <= team_size <= self.maximum_team_size


@dataclass(frozen=True)
class BombBlastProfile:
    """Node-distance damage and armor behavior for a planted bomb."""

    damage_by_node_distance: tuple[int, ...]
    lethal_node_distance: int
    armor_reduction_percent: int


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
    tactical_timing_profiles: tuple[TacticalTimingProfile, ...]
    bomb_blast: BombBlastProfile
    overtime_half_rounds: int

    def timing_for_team_size(self, team_size: int) -> TacticalTimingProfile:
        """Return the registered clock profile for an equal squad size."""

        profile = next(
            (
                candidate
                for candidate in self.tactical_timing_profiles
                if candidate.supports(team_size)
            ),
            None,
        )
        if profile is None:
            raise ValueError(
                f"No Breach Point timing profile supports {team_size}v{team_size}"
            )
        return profile


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
    tactical_timing_profiles=(
        TacticalTimingProfile(
            minimum_team_size=2,
            maximum_team_size=2,
            preplant_tactical_round_limit=8,
            bomb_fuse_tactical_rounds=4,
        ),
        TacticalTimingProfile(
            minimum_team_size=3,
            maximum_team_size=3,
            preplant_tactical_round_limit=7,
            bomb_fuse_tactical_rounds=3,
        ),
        TacticalTimingProfile(
            minimum_team_size=4,
            maximum_team_size=5,
            preplant_tactical_round_limit=6,
            bomb_fuse_tactical_rounds=3,
        ),
    ),
    bomb_blast=BombBlastProfile(
        damage_by_node_distance=(100, 50),
        lethal_node_distance=0,
        armor_reduction_percent=20,
    ),
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
        rules.overtime_half_rounds,
    )
    if any(value <= 0 for value in positive_values):
        raise ValueError("Breach Point action and timing values must be positive")
    if not rules.tactical_timing_profiles:
        raise ValueError("Breach Point requires at least one tactical timing profile")
    previous_maximum: int | None = None
    for profile in rules.tactical_timing_profiles:
        if (
            profile.minimum_team_size <= 0
            or profile.maximum_team_size < profile.minimum_team_size
            or profile.preplant_tactical_round_limit <= 0
            or profile.bomb_fuse_tactical_rounds <= 0
            or previous_maximum is not None
            and profile.minimum_team_size != previous_maximum + 1
        ):
            raise ValueError("Breach Point tactical timing profiles must be contiguous")
        previous_maximum = profile.maximum_team_size
    blast = rules.bomb_blast
    if (
        not blast.damage_by_node_distance
        or any(damage <= 0 for damage in blast.damage_by_node_distance)
        or not 0 <= blast.lethal_node_distance < len(blast.damage_by_node_distance)
        or not 0 <= blast.armor_reduction_percent <= 100
    ):
        raise ValueError("Breach Point bomb blast values are invalid")
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
