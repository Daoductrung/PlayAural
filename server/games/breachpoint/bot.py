"""Stateful, information-safe team strategy for Breach Point bots."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .arsenal import (
    PURCHASE_ROLE_ANTI_ECO,
    PURCHASE_ROLE_BUDGET,
    PURCHASE_ROLE_PRECISION,
    PURCHASE_ROLE_STANDARD,
    SIDE_COUNTER_TERRORISTS,
    SIDE_INDEXES,
    SIDE_TERRORISTS,
    UTILITY_EFFECT_EXPLOSIVE,
    UTILITY_EFFECT_FIRE,
    UTILITY_EFFECT_FLASH,
    UTILITY_EFFECT_SMOKE,
    WEAPON_SLOT_PRIMARY,
    WEAPON_SLOT_SIDEARM,
    EquipmentProfile,
    UtilityProfile,
    WeaponProfile,
    get_purchasable_equipment,
    get_purchasable_utilities,
    get_purchasable_weapons,
    get_weapon,
)
from .player import BreachPointPlayer
from .state import (
    BOMB_CARRIED,
    BOMB_DROPPED,
    BOMB_PLANTED,
    BOMB_PLANTING,
    PHASE_BUY,
    REACTION_DEFUSE,
    REACTION_PLANT,
)

if TYPE_CHECKING:
    from .game import BreachPointGame


ROLE_OBJECTIVE = "objective"
ROLE_ENTRY = "entry"
ROLE_SUPPORT = "support"
ROLE_LURKER = "lurker"
ROLE_ANCHOR = "anchor"
ROLE_ROTATOR = "rotator"

ATTACK_STRATEGY_DIRECT = "direct"
ATTACK_STRATEGY_SPLIT = "split"
ATTACK_STRATEGY_FAKE = "fake"

ACOUSTIC_CUE_FOOTSTEPS = "footsteps"
ACOUSTIC_CUE_WEAPON_FIRE = "weapon_fire"
ACOUSTIC_CUE_WEAPON_DROP = "weapon_drop"
ACOUSTIC_CUE_UTILITY = "utility"
HIGH_CONFIDENCE_ACOUSTIC_CUES = frozenset(
    {ACOUSTIC_CUE_WEAPON_FIRE, ACOUSTIC_CUE_UTILITY}
)


@dataclass(frozen=True)
class AttackStrategyProfile:
    """Roster requirements for one reusable attacking pattern."""

    id: str
    minimum_team_size: int


ATTACK_STRATEGIES = (
    AttackStrategyProfile(ATTACK_STRATEGY_DIRECT, 2),
    AttackStrategyProfile(ATTACK_STRATEGY_SPLIT, 3),
    AttackStrategyProfile(ATTACK_STRATEGY_FAKE, 5),
)


@dataclass(frozen=True)
class BotTacticsProfile:
    """Tunable strategic thresholds shared by every bot team."""

    contact_memory_tactical_rounds: int
    threat_memory_tactical_rounds: int
    entry_minimum_team_size: int
    lurker_minimum_team_size: int
    lurker_commit_tactical_round: int
    pistol_lurker_commit_tactical_round: int
    low_health_percent: int
    attack_history_rounds: int
    elimination_memory_rounds: int
    failed_position_repeat_count: int
    successful_site_repeat_limit: int
    successful_site_repeat_percent: int
    failed_site_repeat_percent: int
    successful_strategy_repeat_percent: int
    failed_strategy_repeat_percent: int
    split_commit_tactical_round: int
    fake_commit_tactical_round: int
    fake_contact_commit_count: int
    close_range_primary_team_divisor: int
    pistol_flash_team_divisor: int
    flash_group_target_count: int
    damage_utility_group_target_count: int
    route_smoke_contact_count: int
    adaptive_smoke_elimination_count: int
    reinforcement_contact_count: int
    small_squad_full_rotation_size: int
    small_squad_cohesion_size: int
    solo_contact_commitment_tactical_rounds: int
    fallback_commitment_tactical_rounds: int
    fallback_enemy_advantage: int
    precision_position_variants: int
    acoustic_memory_tactical_rounds: int
    repeated_acoustic_rotation_count: int
    maximum_duplicate_utility: int


STANDARD_BOT_TACTICS = BotTacticsProfile(
    contact_memory_tactical_rounds=2,
    threat_memory_tactical_rounds=2,
    entry_minimum_team_size=2,
    lurker_minimum_team_size=3,
    lurker_commit_tactical_round=4,
    pistol_lurker_commit_tactical_round=2,
    low_health_percent=35,
    attack_history_rounds=4,
    elimination_memory_rounds=3,
    failed_position_repeat_count=1,
    successful_site_repeat_limit=2,
    successful_site_repeat_percent=60,
    failed_site_repeat_percent=20,
    successful_strategy_repeat_percent=40,
    failed_strategy_repeat_percent=20,
    split_commit_tactical_round=4,
    fake_commit_tactical_round=3,
    fake_contact_commit_count=2,
    close_range_primary_team_divisor=2,
    pistol_flash_team_divisor=2,
    flash_group_target_count=2,
    damage_utility_group_target_count=2,
    route_smoke_contact_count=2,
    adaptive_smoke_elimination_count=2,
    reinforcement_contact_count=2,
    small_squad_full_rotation_size=3,
    small_squad_cohesion_size=2,
    solo_contact_commitment_tactical_rounds=2,
    fallback_commitment_tactical_rounds=2,
    fallback_enemy_advantage=1,
    precision_position_variants=2,
    acoustic_memory_tactical_rounds=1,
    repeated_acoustic_rotation_count=2,
    maximum_duplicate_utility=1,
)


@dataclass(frozen=True)
class EnemyContact:
    """One team-shared observation captured while an enemy was visible."""

    player_id: str
    node_id: str
    observed_tactical_round: int
    health: int
    armor: int
    carried_bomb: bool


@dataclass(frozen=True)
class RecentThreat:
    """One recent, team-legal record of damage dealt to a squad member."""

    target_player_id: str
    target_node_id: str
    source_player_id: str
    source_node_id: str
    observed_tactical_round: int
    damage: int


@dataclass(frozen=True)
class AcousticCue:
    """Anonymous sound evidence heard by at least one living bot teammate."""

    node_id: str
    cue_kind: str
    observed_tactical_round: int
    origin_node_id: str = ""
    observation_count: int = 1


@dataclass(frozen=True)
class TacticalRoute:
    """A chosen path retained until its tactical destination changes."""

    target_node_id: str
    node_ids: tuple[str, ...]
    allows_known_fire: bool


@dataclass(frozen=True)
class DefensiveCommitment:
    """A solo defender's bounded commitment to one last-known contact."""

    target_node_id: str
    observed_tactical_round: int


@dataclass(frozen=True)
class FallbackCommitment:
    """A safe hold retained after breaking a losing firing lane."""

    hold_node_id: str
    watch_node_id: str
    observed_tactical_round: int


@dataclass(frozen=True)
class TacticalAssignment:
    """A stable team role and opening destination for one combat round."""

    player_id: str
    role: str
    anchor_node_id: str = ""


@dataclass(frozen=True)
class AttackRoundMemory:
    """One public attacking result retained for later strategic planning."""

    round_marker: tuple[int, int, int, tuple[int, ...]]
    site_id: str
    strategy_id: str
    won: bool


@dataclass(frozen=True)
class EliminationMemory:
    """One public death retained so a squad can vary a failed setup."""

    round_marker: tuple[int, int, int, tuple[int, ...]]
    victim_side_index: int
    victim_player_id: str
    victim_node_id: str
    source_node_id: str
    source_name_key: str


@dataclass
class SquadMemory:
    """Bounded match-level strategy retained while one game instance lives."""

    attack_rounds: list[AttackRoundMemory] = field(default_factory=list)
    eliminations: list[EliminationMemory] = field(default_factory=list)


@dataclass
class TeamPlan:
    """Bounded runtime-only observations and assignments for one side."""

    team_index: int
    round_marker: tuple[int, int, int, tuple[int, ...]]
    attack_site_id: str = ""
    attack_strategy_id: str = ATTACK_STRATEGY_DIRECT
    decoy_site_id: str = ""
    primary_staging_node_id: str = ""
    split_staging_node_id: str = ""
    strategy_committed: bool = True
    objective_player_id: str = ""
    known_bomb_node_id: str = ""
    entry_commit_node_id: str = ""
    entry_commit_tactical_round: int = 0
    contacts: dict[str, EnemyContact] = field(default_factory=dict)
    recent_threats: dict[str, RecentThreat] = field(default_factory=dict)
    acoustic_cues: dict[str, AcousticCue] = field(default_factory=dict)
    assignments: dict[str, TacticalAssignment] = field(default_factory=dict)
    routes: dict[str, TacticalRoute] = field(default_factory=dict)
    defensive_commitments: dict[str, DefensiveCommitment] = field(
        default_factory=dict
    )
    fallback_commitments: dict[str, FallbackCommitment] = field(
        default_factory=dict
    )
    roster_signature: tuple[str, ...] = ()
    completed_strategy_route_player_ids: set[str] = field(default_factory=set)


def _validate_tactics_profile(profile: BotTacticsProfile) -> None:
    if profile.contact_memory_tactical_rounds < 0:
        raise ValueError("Bot contact memory cannot be negative")
    if profile.threat_memory_tactical_rounds < 0:
        raise ValueError("Bot threat memory cannot be negative")
    if profile.entry_minimum_team_size < 2:
        raise ValueError("An entry role requires at least two teammates")
    if profile.lurker_minimum_team_size < 2:
        raise ValueError("A lurker role requires at least two teammates")
    if profile.lurker_commit_tactical_round <= 1:
        raise ValueError("The lurker commit round must follow the opening round")
    if profile.pistol_lurker_commit_tactical_round <= 1:
        raise ValueError("The pistol lurker commit must follow the opening round")
    if not 0 < profile.low_health_percent <= 100:
        raise ValueError("The low-health percentage must be between 1 and 100")
    if profile.attack_history_rounds <= 0:
        raise ValueError("Bot attack history must retain at least one round")
    if profile.elimination_memory_rounds <= 0:
        raise ValueError("Bot elimination memory must retain at least one round")
    if profile.failed_position_repeat_count <= 0:
        raise ValueError("Failed-position adaptation requires a positive threshold")
    if profile.successful_site_repeat_limit <= 0:
        raise ValueError("Bot site repetition must allow at least one attack")
    if not 0 <= profile.successful_site_repeat_percent <= 100:
        raise ValueError("Bot site repetition percentage must be between 0 and 100")
    if not 0 <= profile.failed_site_repeat_percent <= 100:
        raise ValueError("Failed-site repetition percentage must be between 0 and 100")
    if not 0 <= profile.successful_strategy_repeat_percent <= 100:
        raise ValueError("Bot strategy repetition percentage must be between 0 and 100")
    if not 0 <= profile.failed_strategy_repeat_percent <= 100:
        raise ValueError(
            "Failed-strategy repetition percentage must be between 0 and 100"
        )
    if profile.split_commit_tactical_round <= 0:
        raise ValueError("The split commit round must be positive")
    if profile.fake_commit_tactical_round <= 0:
        raise ValueError("The fake commit round must be positive")
    if profile.fake_contact_commit_count <= 0:
        raise ValueError("A fake requires a positive contact threshold")
    if profile.close_range_primary_team_divisor <= 0:
        raise ValueError("Close-range primary coordination requires a positive divisor")
    if profile.pistol_flash_team_divisor <= 0:
        raise ValueError("Pistol-round flash coordination requires a positive divisor")
    if profile.flash_group_target_count < 2:
        raise ValueError("Grouped flash tactics require at least two targets")
    if profile.damage_utility_group_target_count < 2:
        raise ValueError("Grouped damage utility requires at least two targets")
    if profile.route_smoke_contact_count <= 0:
        raise ValueError("Route smoke tactics require a positive contact count")
    if profile.adaptive_smoke_elimination_count <= 0:
        raise ValueError("Adaptive smoke tactics require a positive death count")
    if profile.reinforcement_contact_count < 2:
        raise ValueError("Reinforcement tactics require at least two contacts")
    if profile.small_squad_full_rotation_size < 2:
        raise ValueError("Full-rotation tactics require at least two teammates")
    if profile.small_squad_cohesion_size < 2:
        raise ValueError("Small-squad cohesion requires at least two teammates")
    if profile.solo_contact_commitment_tactical_rounds <= 0:
        raise ValueError("Solo contact commitment must last at least one round")
    if profile.fallback_commitment_tactical_rounds <= 0:
        raise ValueError("Fallback commitment must last at least one round")
    if profile.fallback_enemy_advantage <= 0:
        raise ValueError("Fallback requires a positive enemy advantage")
    if profile.precision_position_variants <= 0:
        raise ValueError("Precision positioning requires at least one variant")
    if profile.acoustic_memory_tactical_rounds < 0:
        raise ValueError("Bot acoustic memory cannot be negative")
    if profile.repeated_acoustic_rotation_count <= 0:
        raise ValueError("Acoustic rotation requires a positive cue count")
    if profile.maximum_duplicate_utility <= 0:
        raise ValueError("Bot utility duplication limit must be positive")


_validate_tactics_profile(STANDARD_BOT_TACTICS)


def _validate_attack_strategies(
    strategies: tuple[AttackStrategyProfile, ...],
) -> None:
    if not strategies:
        raise ValueError("At least one attack strategy is required")
    strategy_ids = [strategy.id for strategy in strategies]
    if len(strategy_ids) != len(set(strategy_ids)):
        raise ValueError("Attack strategy ids must be unique")
    if strategies[0].id != ATTACK_STRATEGY_DIRECT:
        raise ValueError("The direct strategy must be the baseline attack")
    if any(not strategy.id for strategy in strategies):
        raise ValueError("Attack strategies require stable ids")
    if any(strategy.minimum_team_size < 2 for strategy in strategies):
        raise ValueError("Attack strategies require at least two teammates")


_validate_attack_strategies(ATTACK_STRATEGIES)


class BreachPointBotCoordinator:
    """Coordinate bots through legal observations and stable round plans.

    This object is deliberately not a dataclass field on the game. Its memory is
    session-scoped, never serialized, and rebuilt empty after restoration.
    """

    def __init__(
        self,
        profile: BotTacticsProfile = STANDARD_BOT_TACTICS,
        rng: random.Random | None = None,
    ) -> None:
        self.profile = profile
        self._rng = rng or random.Random()  # nosec B311 - non-security game strategy
        self.team_plans: dict[int, TeamPlan] = {}
        self.squad_memories: dict[int, SquadMemory] = {}

    def seed_strategy(self, seed: int) -> None:
        """Seed tactical variation for reproducible diagnostics and tests."""

        self._rng.seed(seed)

    def clear(self) -> None:
        """Release all match-scoped observations and assignments."""

        self.team_plans.clear()
        self.squad_memories.clear()

    def begin_combat_round(self, game: BreachPointGame) -> None:
        """Start fresh plans after spawn, side, and carrier selection."""

        self.team_plans.clear()
        marker = self._round_marker(game)
        attack_site = self.planned_attack_site(game) or ""
        attackers = game._turn_order_players_on_team(
            SIDE_TERRORISTS,
            alive_only=True,
        )
        attack_strategy = (
            ATTACK_STRATEGY_DIRECT
            if self._is_regulation_pistol_round(game)
            else self.planned_attack_strategy(game, len(attackers))
        )
        decoy_site = self._alternate_site(game, attack_site)
        primary_staging_node = self._primary_staging_node(game, attack_site)
        split_staging_node = self._split_staging_node(game)
        for team_index in SIDE_INDEXES:
            self.team_plans[team_index] = TeamPlan(
                team_index=team_index,
                round_marker=marker,
                attack_site_id=attack_site,
                attack_strategy_id=(
                    attack_strategy
                    if team_index == SIDE_TERRORISTS
                    else ATTACK_STRATEGY_DIRECT
                ),
                decoy_site_id=(decoy_site if team_index == SIDE_TERRORISTS else ""),
                primary_staging_node_id=(
                    primary_staging_node if team_index == SIDE_TERRORISTS else ""
                ),
                split_staging_node_id=(
                    split_staging_node if team_index == SIDE_TERRORISTS else ""
                ),
                strategy_committed=(
                    team_index != SIDE_TERRORISTS
                    or attack_strategy == ATTACK_STRATEGY_DIRECT
                ),
                objective_player_id=(
                    game.bomb_carrier_id if team_index == SIDE_TERRORISTS else ""
                ),
            )
        self._refresh_assignments(game)
        self.observe(game)

    def record_round_result(
        self,
        game: BreachPointGame,
        winning_side_index: int,
    ) -> None:
        """Remember one public result without retaining hidden round state."""

        plan = self.team_plans.get(SIDE_TERRORISTS)
        attack_site_id = plan.attack_site_id if plan else ""
        if attack_site_id not in game.tactical_map.bomb_site_ids():
            return
        strategy_id = plan.attack_strategy_id if plan else ATTACK_STRATEGY_DIRECT
        squad_index = game._squad_for_side(SIDE_TERRORISTS)
        memory = self.squad_memories.setdefault(squad_index, SquadMemory())
        marker = self._round_marker(game)
        if memory.attack_rounds and memory.attack_rounds[-1].round_marker == marker:
            return
        memory.attack_rounds.append(
            AttackRoundMemory(
                round_marker=marker,
                site_id=attack_site_id,
                strategy_id=strategy_id,
                won=winning_side_index == SIDE_TERRORISTS,
            )
        )
        del memory.attack_rounds[: -self.profile.attack_history_rounds]

    def record_elimination(
        self,
        game: BreachPointGame,
        target: BreachPointPlayer,
        source: BreachPointPlayer,
        *,
        source_name_key: str,
    ) -> None:
        """Retain a bounded public death without preserving hidden observations."""

        if (
            target.team_index == source.team_index
            or target.squad_index not in SIDE_INDEXES
            or not target.position_id
            or not source.position_id
        ):
            return
        memory = self.squad_memories.setdefault(target.squad_index, SquadMemory())
        elimination = EliminationMemory(
            round_marker=self._round_marker(game),
            victim_side_index=target.team_index,
            victim_player_id=target.id,
            victim_node_id=target.position_id,
            source_node_id=source.position_id,
            source_name_key=source_name_key,
        )
        if elimination in memory.eliminations:
            return
        memory.eliminations.append(elimination)
        retained_markers: list[tuple[int, int, int, tuple[int, ...]]] = []
        for remembered in reversed(memory.eliminations):
            if remembered.round_marker not in retained_markers:
                retained_markers.append(remembered.round_marker)
            if len(retained_markers) == self.profile.elimination_memory_rounds:
                break
        retained = set(retained_markers)
        memory.eliminations[:] = [
            remembered
            for remembered in memory.eliminations
            if remembered.round_marker in retained
        ]

    def observe(self, game: BreachPointGame) -> None:
        """Refresh memory only from information the corresponding team can see."""

        self._ensure_current_round(game)
        for team_index in SIDE_INDEXES:
            plan = self.team_plans[team_index]
            if team_index == SIDE_TERRORISTS:
                self._remember_entry_commitment(game, plan)
                self._follow_small_squad_human_route(game, plan)
            opposing_team_index = next(
                index for index in SIDE_INDEXES if index != team_index
            )
            enemies = game._players_on_team(opposing_team_index, alive_only=True)
            visible_enemy_ids: set[str] = set()
            for enemy in enemies:
                if not game._team_can_see_player(team_index, enemy):
                    continue
                visible_enemy_ids.add(enemy.id)
                carries_bomb = bool(
                    team_index == SIDE_COUNTER_TERRORISTS
                    and game.bomb_state in {BOMB_CARRIED, BOMB_PLANTING}
                    and game.bomb_carrier_id == enemy.id
                )
                plan.contacts[enemy.id] = EnemyContact(
                    player_id=enemy.id,
                    node_id=enemy.position_id,
                    observed_tactical_round=game.tactical_round,
                    health=enemy.health,
                    armor=enemy.armor,
                    carried_bomb=carries_bomb,
                )

            for player_id, contact in list(plan.contacts.items()):
                enemy = game._breach_player_by_id(player_id)
                age = game.tactical_round - contact.observed_tactical_round
                visible_empty_node = bool(
                    player_id not in visible_enemy_ids
                    and game._team_can_see_node(team_index, contact.node_id)
                )
                if (
                    not enemy
                    or enemy.eliminated
                    or age > self.profile.contact_memory_tactical_rounds
                    or visible_empty_node
                ):
                    del plan.contacts[player_id]

            for player_id, threat in list(plan.recent_threats.items()):
                target = game._breach_player_by_id(player_id)
                age = game.tactical_round - threat.observed_tactical_round
                if (
                    not target
                    or target.eliminated
                    or age > self.profile.threat_memory_tactical_rounds
                ):
                    del plan.recent_threats[player_id]

            for node_id, cue in list(plan.acoustic_cues.items()):
                age = game.tactical_round - cue.observed_tactical_round
                if (
                    age > self.profile.acoustic_memory_tactical_rounds
                    or game._team_can_see_node(team_index, node_id)
                ):
                    del plan.acoustic_cues[node_id]

            for player_id, commitment in list(plan.fallback_commitments.items()):
                defender = game._breach_player_by_id(player_id)
                lane_still_active = any(
                    contact.observed_tactical_round == game.tactical_round
                    and (
                        contact.node_id == commitment.watch_node_id
                        or game.tactical_map.has_sightline(
                            contact.node_id,
                            commitment.watch_node_id,
                        )
                    )
                    for contact in plan.contacts.values()
                )
                if lane_still_active:
                    commitment = FallbackCommitment(
                        hold_node_id=commitment.hold_node_id,
                        watch_node_id=commitment.watch_node_id,
                        observed_tactical_round=game.tactical_round,
                    )
                    plan.fallback_commitments[player_id] = commitment
                age = game.tactical_round - commitment.observed_tactical_round
                if (
                    not defender
                    or defender.eliminated
                    or age > self.profile.fallback_commitment_tactical_rounds
                ):
                    del plan.fallback_commitments[player_id]

            self._update_bomb_memory(game, plan)
            if team_index == SIDE_TERRORISTS:
                self._remember_strategy_route_progress(game, plan)
                self._update_attack_strategy(game, plan)
        self._refresh_assignments(game)

    def _follow_small_squad_human_route(
        self,
        game: BreachPointGame,
        plan: TeamPlan,
    ) -> None:
        """Make a lone T bot support the route chosen by its human teammate."""

        teammates = game._players_on_team(SIDE_TERRORISTS, alive_only=True)
        if (
            game.bomb_state != BOMB_CARRIED
            or len(teammates) != self.profile.small_squad_cohesion_size
        ):
            return
        human_teammates = [teammate for teammate in teammates if not teammate.is_bot]
        bot_teammates = [teammate for teammate in teammates if teammate.is_bot]
        if len(human_teammates) != 1 or len(bot_teammates) != 1:
            return
        human = human_teammates[0]
        if human.position_id == game.tactical_map.terrorist_spawn:
            return
        site_distances = [
            (distance, site_id)
            for site_id in game.tactical_map.bomb_site_ids()
            if (distance := game._node_distance(human.position_id, site_id)) is not None
        ]
        if not site_distances:
            return
        nearest_distance = min(distance for distance, _site_id in site_distances)
        nearest_sites = [
            site_id
            for distance, site_id in site_distances
            if distance == nearest_distance
        ]
        if len(nearest_sites) != 1 or nearest_sites[0] == plan.attack_site_id:
            return
        plan.attack_site_id = nearest_sites[0]
        plan.attack_strategy_id = ATTACK_STRATEGY_DIRECT
        plan.decoy_site_id = self._alternate_site(game, plan.attack_site_id)
        plan.primary_staging_node_id = self._primary_staging_node(
            game,
            plan.attack_site_id,
        )
        plan.strategy_committed = True

    def record_damage(
        self,
        game: BreachPointGame,
        target: BreachPointPlayer,
        source: BreachPointPlayer,
        damage: int,
    ) -> None:
        """Remember a damaging contact without granting information through fog."""

        if (
            damage <= 0
            or target.team_index == source.team_index
            or target.team_index not in SIDE_INDEXES
            or source.eliminated
        ):
            return
        self._ensure_current_round(game)
        plan = self.team_plans[target.team_index]
        if not game._team_can_see_player(target.team_index, source):
            return
        plan.contacts[source.id] = EnemyContact(
            player_id=source.id,
            node_id=source.position_id,
            observed_tactical_round=game.tactical_round,
            health=source.health,
            armor=source.armor,
            carried_bomb=bool(
                target.team_index == SIDE_COUNTER_TERRORISTS
                and game.bomb_state in {BOMB_CARRIED, BOMB_PLANTING}
                and game.bomb_carrier_id == source.id
            ),
        )
        plan.recent_threats[target.id] = RecentThreat(
            target_player_id=target.id,
            target_node_id=target.position_id,
            source_player_id=source.id,
            source_node_id=source.position_id,
            observed_tactical_round=game.tactical_round,
            damage=damage,
        )

    def record_acoustic_cue(
        self,
        game: BreachPointGame,
        *,
        source_team_index: int,
        node_id: str,
        cue_kind: str,
        audible_team_indexes: set[int],
        origin_node_id: str = "",
    ) -> None:
        """Remember an anonymous cue only for enemy bots that actually heard it."""

        if source_team_index not in SIDE_INDEXES or not game._node(node_id):
            return
        if origin_node_id and not game._node(origin_node_id):
            origin_node_id = ""
        self._ensure_current_round(game)
        for team_index in audible_team_indexes:
            if team_index not in SIDE_INDEXES or team_index == source_team_index:
                continue
            plan = self.team_plans[team_index]
            previous = plan.acoustic_cues.get(node_id)
            previous_is_fresh = bool(
                previous
                and game.tactical_round - previous.observed_tactical_round
                <= self.profile.acoustic_memory_tactical_rounds
            )
            plan.acoustic_cues[node_id] = AcousticCue(
                node_id=node_id,
                cue_kind=cue_kind,
                observed_tactical_round=game.tactical_round,
                origin_node_id=origin_node_id,
                observation_count=(
                    previous.observation_count + 1 if previous_is_fresh else 1
                ),
            )

    def choose_action(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> str | None:
        """Return one legal action from the bot's current tactical context."""

        self.observe(game)
        if game.pending_weapon_donation:
            response = self.weapon_donation_response_action(game, bot)
            if response:
                return response
        if game.phase == PHASE_BUY:
            return self.buy_action(game, bot)
        if game.round_recovery_player_id:
            if game.round_recovery_player_id != bot.id:
                return None
            return self.pickup_weapon_action(game, bot, postround=True) or "end_turn"
        if game._is_watched_entry_reaction():
            if game.reaction_window.responding_player_id != bot.id:
                return None
            if game._is_reaction_shoot_enabled(bot) is None:
                return "reaction_shoot"
            return "reaction_pass"
        if game._turn_error(bot) is not None:
            return None

        visible_enemies = self._visible_enemies(game, bot)
        objective_response_action = self._objective_response_action(
            game,
            bot,
            visible_enemies,
        )
        if objective_response_action:
            return objective_response_action
        objective_action = self._objective_action(game, bot)
        objective_is_urgent = self._objective_is_urgent(
            game,
            objective_action,
        )
        objective_is_safe = self._objective_is_safe(
            game,
            bot,
            objective_action,
            visible_enemies,
        )
        shootable_enemies = [
            enemy
            for enemy in visible_enemies
            if game._is_shoot_enabled(bot, action_id=f"shoot_{enemy.id}") is None
        ]
        lethal_target = next(
            (
                enemy
                for enemy in shootable_enemies
                if self._attack_would_eliminate(game, bot, enemy)
            ),
            None,
        )
        route_opening_target = self._route_opening_target(
            game,
            bot,
            shootable_enemies,
        )

        if objective_is_urgent and objective_is_safe:
            return objective_action

        urgent_plant_route = self._urgent_plant_route_action(game, bot)
        if urgent_plant_route:
            return urgent_plant_route

        route_smoke_action = self._attacking_route_smoke_action(game, bot)
        if route_smoke_action:
            return route_smoke_action

        equipped_weapon = game._equipped_weapon(bot)
        disengage_action = self.objective_disengage_action(
            game,
            bot,
            lethal_target=route_opening_target,
            contemplated_action_cost=(
                equipped_weapon.action_point_cost
                if shootable_enemies and equipped_weapon
                else 0
            ),
        )
        if route_opening_target:
            return f"shoot_{route_opening_target.id}"
        if disengage_action:
            next_node = disengage_action.removeprefix("move_")
            smoke_action = self.objective_smoke_action(
                game,
                bot,
                next_node,
                (game.bomb_location_id,),
            )
            if smoke_action:
                return smoke_action
            return disengage_action
        if lethal_target:
            return f"shoot_{lethal_target.id}"

        hazard_escape_action = self._hazard_escape_action(game, bot)
        if hazard_escape_action:
            return hazard_escape_action

        blast_escape_action = self._postplant_blast_escape_action(game, bot)
        if blast_escape_action:
            return blast_escape_action

        lost_postplant_action = self._lost_postplant_action(
            game,
            bot,
            shootable_enemies,
        )
        if lost_postplant_action:
            return lost_postplant_action

        if visible_enemies and equipped_weapon:
            loaded = game._loaded_ammunition(bot, equipped_weapon)
            if loaded <= 0:
                switch_action = self.weapon_switch_action(
                    game,
                    bot,
                    visible_enemies,
                )
                if switch_action:
                    return switch_action
                if game._is_reload_enabled(bot) is None:
                    return "reload"

        damage_utility_action = self._damage_utility_action(
            game,
            bot,
            visible_enemies,
        )
        if damage_utility_action:
            return damage_utility_action

        entry_breach_action = self._entry_breach_action(
            game,
            bot,
            visible_enemies,
        )
        if entry_breach_action:
            return entry_breach_action

        trade_entry_action = self._trade_entry_action(game, bot)
        if trade_entry_action:
            return trade_entry_action

        supported_return_fire = self._supported_return_fire_target(
            game,
            bot,
            shootable_enemies,
        )
        if supported_return_fire:
            return f"shoot_{supported_return_fire.id}"

        fallback_action = self._defensive_fallback_action(
            game,
            bot,
            visible_enemies,
        )
        if fallback_action:
            return fallback_action

        under_fire_action = self._under_fire_response_action(
            game,
            bot,
            visible_enemies,
        )
        if under_fire_action:
            return under_fire_action

        flash_action = self._flash_action(game, bot, visible_enemies)
        if flash_action and not (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state == BOMB_PLANTED
        ):
            return flash_action

        if objective_action and objective_is_safe and (
            not visible_enemies or bot.shots_fired_this_activation
        ):
            return objective_action

        if bot.shots_fired_this_activation and visible_enemies:
            preferred_target = visible_enemies[0]
            if preferred_target not in shootable_enemies:
                switch_action = self.weapon_switch_action(
                    game,
                    bot,
                    [preferred_target],
                )
                if switch_action:
                    return switch_action
        if shootable_enemies:
            return f"shoot_{shootable_enemies[0].id}"

        angle_action = (
            None
            if bot.held_angle_node_id
            else self._angle_action(game, bot, visible_enemies)
        )
        if angle_action:
            return angle_action

        switch_action = self.weapon_switch_action(game, bot, visible_enemies)
        if switch_action:
            return switch_action

        if objective_action and objective_is_safe:
            return objective_action

        pickup_action = self.pickup_weapon_action(game, bot)
        if pickup_action:
            return pickup_action

        reload_action = self.reload_action(game, bot)
        if reload_action:
            return reload_action

        if self._should_maintain_prepared_angle(game, bot):
            return "end_turn"

        # An attacking sniper that already covered one reaction window must
        # advance when that angle no longer serves its route. Re-aiming at a
        # different long lane here would let richer map geometry trap it in an
        # endless sequence of holds.
        proactive_angle_action = (
            None if bot.held_angle_node_id else self._proactive_angle_action(game, bot)
        )
        if proactive_angle_action:
            return proactive_angle_action

        if self._should_stage_bomb_carrier(game, bot):
            return "end_turn"

        if bot.action_points >= game._movement_action_point_cost(bot):
            target_nodes = self.target_nodes(game, bot)
            next_node = self.shortest_path_step(game, bot, target_nodes)
            if next_node:
                smoke_action = self.objective_smoke_action(
                    game,
                    bot,
                    next_node,
                    target_nodes,
                )
                if smoke_action:
                    return smoke_action
                action_id = f"move_{next_node}"
                if game._is_move_enabled(bot, action_id=action_id) is None:
                    return action_id
        return "end_turn"

    def _objective_response_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Use a plant or defuse response to contest the objective immediately.

        The responder may act with a reduced AP budget, so an unprepared AWP
        angle is not useful: the objective would complete before the bot could
        fire. Prefer legal damage, a ready sidearm, or progress toward the
        publicly known objective instead.
        """

        window = game.reaction_window
        if (
            not window.is_open
            or window.kind not in {REACTION_PLANT, REACTION_DEFUSE}
            or window.responding_player_id != bot.id
        ):
            return None

        objective_actor = game._breach_player_by_id(window.target_player_id)
        actor_is_visible = bool(
            objective_actor
            and not objective_actor.eliminated
            and objective_actor in visible_enemies
        )
        prioritized_enemies = sorted(
            visible_enemies,
            key=lambda enemy: (
                enemy is not objective_actor,
                not self._attack_would_eliminate(game, bot, enemy),
                enemy.health + enemy.armor,
                enemy.id,
            ),
        )
        for enemy in prioritized_enemies:
            action_id = f"shoot_{enemy.id}"
            if game._is_shoot_enabled(bot, action_id=action_id) is None:
                return action_id

        if prioritized_enemies:
            utility_action = self._damage_utility_action(
                game,
                bot,
                prioritized_enemies,
            )
            if utility_action:
                return utility_action
            switch_action = self._immediate_fire_weapon_switch_action(
                game,
                bot,
                prioritized_enemies,
            )
            if switch_action:
                return switch_action

        objective_node_id = ""
        if window.kind == REACTION_DEFUSE:
            objective_node_id = game.bomb_location_id
        elif actor_is_visible and objective_actor:
            objective_node_id = objective_actor.position_id
        else:
            plan = self.team_plans.get(bot.team_index)
            objective_node_id = plan.known_bomb_node_id if plan else ""

        movement_cost = game._movement_action_point_cost(bot)
        if objective_node_id and bot.action_points >= movement_cost:
            next_node_id = self.shortest_path_step(
                game,
                bot,
                (objective_node_id,),
            )
            action_id = f"move_{next_node_id}" if next_node_id else ""
            if action_id and game._is_move_enabled(bot, action_id=action_id) is None:
                return action_id

        # If damage and useful objective progress are both impossible, a bot
        # under observed fire should still preserve itself rather than pass in
        # the exposed lane. Hidden plants do not grant the responder the site.
        plan = self.team_plans.get(bot.team_index)
        recent_threat = plan.recent_threats.get(bot.id) if plan else None
        if recent_threat and recent_threat.target_node_id == bot.position_id:
            return self._safest_retreat_action(
                game,
                bot,
                away_from_node=recent_threat.source_node_id,
            )
        return None

    def _under_fire_response_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Answer fresh fire when the equipped weapon cannot shoot this turn."""

        plan = self.team_plans.get(bot.team_index)
        recent_threat = plan.recent_threats.get(bot.id) if plan else None
        if (
            not recent_threat
            or recent_threat.observed_tactical_round != game.tactical_round
            or recent_threat.target_node_id != bot.position_id
            or bot.shots_fired_this_activation
        ):
            return None
        source = next(
            (
                enemy
                for enemy in visible_enemies
                if enemy.id == recent_threat.source_player_id
            ),
            None,
        )
        if source:
            if game._is_shoot_enabled(
                bot,
                action_id=f"shoot_{source.id}",
            ) is None:
                return None
            switch_action = self._immediate_fire_weapon_switch_action(
                game,
                bot,
                [source],
            )
            if switch_action:
                return switch_action
        if bot.action_points < game._movement_action_point_cost(bot):
            return None
        return self._safest_retreat_action(
            game,
            bot,
            away_from_node=recent_threat.source_node_id,
        )

    def _urgent_plant_route_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Spend the final viable activation reaching a site before fighting."""

        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or game.bomb_carrier_id != bot.id
            or game.tactical_round < game.preplant_tactical_round_limit
        ):
            return None
        movement_cost = game._movement_action_point_cost(bot)
        if bot.action_points < movement_cost + game.rules.plant_cost:
            return None
        plan = self.team_plans.get(SIDE_TERRORISTS)
        if not plan or not plan.attack_site_id:
            return None
        next_node = self.shortest_path_step(game, bot, (plan.attack_site_id,))
        if next_node != plan.attack_site_id:
            return None
        action_id = f"move_{next_node}"
        return (
            action_id
            if game._is_move_enabled(bot, action_id=action_id) is None
            else None
        )

    def contacts_for_team(self, team_index: int) -> tuple[EnemyContact, ...]:
        """Expose an immutable observation snapshot for diagnostics and tests."""

        plan = self.team_plans.get(team_index)
        if not plan:
            return ()
        return tuple(plan.contacts.values())

    def acoustic_cues_for_team(self, team_index: int) -> tuple[AcousticCue, ...]:
        """Expose anonymous audible evidence for diagnostics and tests."""

        plan = self.team_plans.get(team_index)
        if not plan:
            return ()
        return tuple(plan.acoustic_cues.values())

    def assignment_for(self, player_id: str) -> TacticalAssignment | None:
        """Return a player's current round assignment, if one exists."""

        for plan in self.team_plans.values():
            assignment = plan.assignments.get(player_id)
            if assignment:
                return assignment
        return None

    def planned_attack_site(self, game: BreachPointGame) -> str | None:
        """Choose a site from bounded results instead of a fixed alternation."""

        site_ids = game.tactical_map.bomb_site_ids()
        if not site_ids:
            return None
        attacking_squad_index = game._squad_for_side(SIDE_TERRORISTS)
        memory = self.squad_memories.get(attacking_squad_index)
        attack_rounds = memory.attack_rounds if memory else []
        if not attack_rounds:
            return self._rng.choice(site_ids)

        last_attack = attack_rounds[-1]
        consecutive_site_attacks = 0
        for attack in reversed(attack_rounds):
            if attack.site_id != last_attack.site_id:
                break
            consecutive_site_attacks += 1
        may_repeat = bool(
            not last_attack.won
            or consecutive_site_attacks < self.profile.successful_site_repeat_limit
        )
        repeat_percent = (
            self.profile.successful_site_repeat_percent
            if last_attack.won
            else self.profile.failed_site_repeat_percent
        )
        if may_repeat and self._rng.randrange(100) < repeat_percent:
            return last_attack.site_id
        alternatives = tuple(
            site_id for site_id in site_ids if site_id != last_attack.site_id
        )
        return self._rng.choice(alternatives) if alternatives else last_attack.site_id

    def planned_attack_strategy(
        self,
        game: BreachPointGame,
        attacker_count: int,
    ) -> str:
        """Choose a legal pattern from bounded public round results."""

        eligible = tuple(
            strategy
            for strategy in ATTACK_STRATEGIES
            if attacker_count >= strategy.minimum_team_size
        )
        if not eligible:
            return ATTACK_STRATEGY_DIRECT
        attacking_squad_index = game._squad_for_side(SIDE_TERRORISTS)
        memory = self.squad_memories.get(attacking_squad_index)
        attack_rounds = memory.attack_rounds if memory else []
        if not attack_rounds:
            return self._rng.choice(eligible).id

        last_attack = attack_rounds[-1]
        eligible_ids = tuple(strategy.id for strategy in eligible)
        if last_attack.strategy_id not in eligible_ids:
            return eligible[0].id
        repeat_percent = (
            self.profile.successful_strategy_repeat_percent
            if last_attack.won
            else self.profile.failed_strategy_repeat_percent
        )
        if self._rng.randrange(100) < repeat_percent:
            return last_attack.strategy_id
        alternatives = tuple(
            strategy_id
            for strategy_id in eligible_ids
            if strategy_id != last_attack.strategy_id
        )
        return (
            self._rng.choice(alternatives)
            if alternatives
            else last_attack.strategy_id
        )

    def assigned_bomb_site(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> str | None:
        """Return an anchor's assigned site; rotators have no site assignment."""

        self._ensure_current_round(game)
        assignment = self.assignment_for(bot.id)
        if not assignment or assignment.role != ROLE_ANCHOR:
            return None
        return assignment.anchor_node_id or None

    def target_nodes(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> tuple[str, ...]:
        """Return the bot's coherent objective without consulting hidden state."""

        self.observe(game)
        plan = self.team_plans[bot.team_index]
        if bot.team_index == SIDE_COUNTER_TERRORISTS:
            if game.bomb_state == BOMB_PLANTED:
                return (game.bomb_location_id,)
            if plan.known_bomb_node_id:
                return (plan.known_bomb_node_id,)
            assignment = plan.assignments.get(bot.id)
            fallback_commitment = plan.fallback_commitments.get(bot.id)
            if fallback_commitment:
                return (fallback_commitment.hold_node_id,)
            recent_threat = plan.recent_threats.get(bot.id)
            if (
                recent_threat
                and recent_threat.target_node_id != bot.position_id
            ):
                return (bot.position_id,)
            active_route = plan.routes.get(bot.id)
            active_route_is_valid = bool(
                active_route
                and active_route.target_node_id != bot.position_id
                and game._node(active_route.target_node_id)
            )
            route_is_tactical_commitment = bool(
                active_route_is_valid
                and active_route
                and (
                    not assignment
                    or active_route.target_node_id != assignment.anchor_node_id
                )
            )
            if route_is_tactical_commitment and active_route:
                # Finish a legal rotation once it has started. Re-evaluating
                # softer contact and anchor priorities after every edge can
                # otherwise send a defender straight back over the edge it
                # just crossed. A fresh sound may redirect the opening setup,
                # but not a committed acoustic reinforcement route. Bomb
                # state, known bomb information, damage retreats, and fallback
                # commitments above still interrupt immediately.
                return (active_route.target_node_id,)
            acoustic_target = self._acoustic_rotation_target(
                game,
                bot,
                plan,
            )
            if acoustic_target:
                return (acoustic_target,)
            if active_route_is_valid and active_route:
                return (active_route.target_node_id,)
            solo_contact_node_id = self._solo_defender_contact_target(
                game,
                bot,
                plan,
            )
            if solo_contact_node_id:
                return (solo_contact_node_id,)
            if (
                assignment
                and assignment.role == ROLE_ROTATOR
                and assignment.anchor_node_id
                and bot.position_id == game.tactical_map.counter_terrorist_spawn
            ):
                return (assignment.anchor_node_id,)
            teammate_support_target = self._small_squad_support_target(
                game,
                bot,
                plan,
            )
            if teammate_support_target:
                return (teammate_support_target,)
            carrier_contact = next(
                (contact for contact in plan.contacts.values() if contact.carried_bomb),
                None,
            )
            if carrier_contact and self._should_answer_carrier_contact(
                game,
                bot,
                assignment,
                carrier_contact,
            ):
                return (carrier_contact.node_id,)
            reinforcement_contact = self._reinforcement_contact(
                game,
                bot,
                assignment,
                plan,
            )
            if reinforcement_contact:
                return (reinforcement_contact.node_id,)
            freshest_contact = self._freshest_contact(plan)
            if freshest_contact and (
                assignment is None
                or (
                    assignment.role == ROLE_ROTATOR
                    and self._should_rotate_to_unconfirmed_contacts(game, plan)
                )
                or assignment.anchor_node_id == freshest_contact.node_id
            ):
                return (freshest_contact.node_id,)
            if assignment and assignment.anchor_node_id:
                anchor_position = self._defensive_anchor_position(
                    game,
                    bot,
                    assignment,
                )
                return (anchor_position,) if anchor_position else ()
            return ()

        if game.bomb_state in {BOMB_PLANTING, BOMB_PLANTED}:
            location_id = (
                game.planting_location_id
                if game.bomb_state == BOMB_PLANTING
                else game.bomb_location_id
            )
            if game.bomb_state == BOMB_PLANTED:
                return (self._terrorist_postplant_node(game, plan, bot, location_id),)
            return (location_id,)
        if game.bomb_state == BOMB_DROPPED:
            return (game.bomb_location_id,)

        attack_site = plan.attack_site_id
        assignment = plan.assignments.get(bot.id)
        flexible_staging_target = self._human_carrier_staging_target(
            game,
            bot,
            plan,
        )
        if flexible_staging_target:
            return (flexible_staging_target,)
        cohesion_target = self._small_squad_cohesion_target(game, bot, attack_site)
        if cohesion_target:
            return (cohesion_target,)
        strategy_target = self._strategy_target_node(
            game,
            plan,
            bot,
            assignment,
        )
        if strategy_target:
            return (strategy_target,)
        if bot.id == game.bomb_carrier_id:
            return (attack_site,) if attack_site else ()
        if assignment and assignment.role == ROLE_LURKER:
            pistol_round = self._is_regulation_pistol_round(game)
            commit_tactical_round = (
                self.profile.pistol_lurker_commit_tactical_round
                if pistol_round
                else self.profile.lurker_commit_tactical_round
            )
            if game.tactical_round < commit_tactical_round:
                staging_node_id = (
                    plan.primary_staging_node_id
                    if pistol_round
                    else self._alternate_site(game, attack_site)
                )
                return (
                    (staging_node_id,)
                    if staging_node_id
                    else ((attack_site,) if attack_site else ())
                )
            return (attack_site,) if attack_site else ()
        carrier = game._breach_player_by_id(game.bomb_carrier_id)
        if (
            assignment
            and assignment.role == ROLE_SUPPORT
            and carrier
            and carrier.position_id != bot.position_id
        ):
            support_distance = game._node_distance(bot.position_id, attack_site)
            carrier_distance = game._node_distance(
                carrier.position_id,
                attack_site,
            )
            if (
                support_distance is not None
                and carrier_distance is not None
                and support_distance > carrier_distance
            ):
                spacing_target = self._support_spacing_target(
                    game,
                    bot,
                    carrier,
                    attack_site,
                )
                return (spacing_target or carrier.position_id,)
        return (attack_site,) if attack_site else game.tactical_map.bomb_site_ids()

    def _small_squad_cohesion_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        attack_site_id: str,
    ) -> str:
        """Keep a two-player attack within trading distance of its human leader."""

        teammates = game._players_on_team(SIDE_TERRORISTS, alive_only=True)
        if (
            bot.team_index != SIDE_TERRORISTS
            or len(teammates) > self.profile.small_squad_cohesion_size
            or game.tactical_round >= game.preplant_tactical_round_limit - 1
        ):
            return ""
        human_teammate = next(
            (
                teammate
                for teammate in teammates
                if teammate.id != bot.id and not teammate.is_bot
            ),
            None,
        )
        if not human_teammate:
            return ""
        team_order = game._turn_order_players_on_team(
            SIDE_TERRORISTS,
            alive_only=True,
        )
        order_by_id = {player.id: index for index, player in enumerate(team_order)}
        bot_leads_unacted_human = bool(
            bot.id == game.bomb_carrier_id
            and human_teammate.id not in game.round_acted_player_ids
            and order_by_id.get(bot.id, len(team_order))
            < order_by_id.get(human_teammate.id, -1)
        )
        if bot_leads_unacted_human:
            return attack_site_id
        spacing_target = self._support_spacing_target(
            game,
            bot,
            human_teammate,
            attack_site_id,
        )
        return spacing_target or attack_site_id

    def _human_carrier_staging_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        plan: TeamPlan,
    ) -> str:
        """Stage early bots at flexible exits until a human carrier declares a lane."""

        carrier = game._breach_player_by_id(game.bomb_carrier_id)
        if (
            bot.team_index != SIDE_TERRORISTS
            or not bot.is_bot
            or game.bomb_state != BOMB_CARRIED
            or game.tactical_round != 1
            or not carrier
            or carrier.is_bot
            or carrier.position_id != game.tactical_map.terrorist_spawn
            or carrier.id in game.round_acted_player_ids
        ):
            return ""
        team_order = game._turn_order_players_on_team(
            SIDE_TERRORISTS,
            alive_only=True,
        )
        order_by_id = {player.id: index for index, player in enumerate(team_order)}
        if order_by_id.get(bot.id, len(team_order)) >= order_by_id.get(
            carrier.id,
            -1,
        ):
            return ""
        staging_nodes = self._flexible_attack_staging_nodes(game)
        if not staging_nodes:
            return plan.primary_staging_node_id
        leading_bots = [
            player
            for player in team_order
            if player.is_bot
            and order_by_id[player.id] < order_by_id[carrier.id]
        ]
        slot = next(
            (
                index
                for index, teammate in enumerate(leading_bots)
                if teammate.id == bot.id
            ),
            0,
        )
        target = staging_nodes[slot % len(staging_nodes)]
        if bot.position_id not in {game.tactical_map.terrorist_spawn, target}:
            return ""
        return target

    def _flexible_attack_staging_nodes(
        self,
        game: BreachPointGame,
    ) -> tuple[str, ...]:
        """Rank spawn exits by their ability to pivot toward either bombsite."""

        spawn = game._node(game.tactical_map.terrorist_spawn)
        sites = game.tactical_map.bomb_site_ids()
        if not spawn or not sites:
            return ()
        map_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        candidates: list[tuple[tuple[int, int, int], str]] = []
        for node_id in spawn.adjacent:
            distances = [game._node_distance(node_id, site_id) for site_id in sites]
            if any(distance is None for distance in distances):
                continue
            numeric_distances = [
                int(distance) for distance in distances if distance is not None
            ]
            candidates.append(
                (
                    (
                        max(numeric_distances) - min(numeric_distances),
                        sum(numeric_distances),
                        map_order.get(node_id, len(map_order)),
                    ),
                    node_id,
                )
            )
        return tuple(node_id for _rank, node_id in sorted(candidates))

    @staticmethod
    def _support_spacing_target(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        leader: BreachPointPlayer,
        attack_site_id: str,
    ) -> str:
        """Choose an adjacent trade lane without occupying the leader's node."""

        leader_node = game._node(leader.position_id)
        if not leader_node:
            return ""
        separation = game._node_distance(bot.position_id, leader.position_id)
        if separation is not None and separation > 1:
            route = BreachPointBotCoordinator._topology_path(
                game,
                bot.position_id,
                leader.position_id,
            )
            if len(route) >= 3:
                return route[-2]
        occupied_nodes = {
            teammate.position_id
            for teammate in game._players_on_team(
                SIDE_TERRORISTS,
                alive_only=True,
            )
            if teammate.id != bot.id
        }
        map_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        candidates = [
            node_id
            for node_id in leader_node.adjacent
            if node_id != bot.position_id and node_id not in occupied_nodes
        ]
        if not candidates:
            return ""
        return min(
            candidates,
            key=lambda node_id: (
                game._node_distance(node_id, attack_site_id)
                if game._node_distance(node_id, attack_site_id) is not None
                else len(game.tactical_map.nodes),
                game._node_distance(bot.position_id, node_id)
                if game._node_distance(bot.position_id, node_id) is not None
                else len(game.tactical_map.nodes),
                map_order.get(node_id, len(map_order)),
            ),
        )

    def _small_squad_support_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        plan: TeamPlan,
    ) -> str:
        """Reinforce a two-player defense without pathing into enemy fire."""

        teammates = game._players_on_team(SIDE_COUNTER_TERRORISTS, alive_only=True)
        if len(teammates) > self.profile.small_squad_cohesion_size:
            return ""
        supporting_teammates = [
            teammate for teammate in teammates if teammate.id != bot.id
        ]
        if not supporting_teammates:
            return ""
        contacts = sorted(
            plan.contacts.values(),
            key=lambda contact: (
                -contact.observed_tactical_round,
                contact.health + contact.armor,
                contact.player_id,
            ),
        )
        for contact in contacts:
            enemy = game._breach_player_by_id(contact.player_id)
            if not enemy or enemy.eliminated:
                continue
            if game._can_see(bot, enemy):
                continue
            if any(
                teammate.position_id == contact.node_id
                or game._can_see(teammate, enemy)
                for teammate in supporting_teammates
            ):
                threatened_teammate = next(
                    teammate
                    for teammate in supporting_teammates
                    if teammate.position_id == contact.node_id
                    or game._can_see(teammate, enemy)
                )
                current_contacts = [
                    remembered
                    for remembered in plan.contacts.values()
                    if remembered.observed_tactical_round == game.tactical_round
                    and (
                        remembered.node_id == threatened_teammate.position_id
                        or game.tactical_map.has_sightline(
                            remembered.node_id,
                            threatened_teammate.position_id,
                        )
                    )
                ]
                teammate_needs_help = bool(
                    contact.carried_bomb
                    or len(current_contacts)
                    >= self.profile.reinforcement_contact_count
                    or threatened_teammate.health * 100
                    <= game.rules.max_health * self.profile.low_health_percent
                )
                if not teammate_needs_help:
                    continue
                fallback = plan.fallback_commitments.get(threatened_teammate.id)
                return (
                    fallback.hold_node_id
                    if fallback
                    else threatened_teammate.position_id
                )
        return ""

    def _solo_defender_contact_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        plan: TeamPlan,
    ) -> str:
        """Keep a lone CT committed long enough to clear one contact route."""

        living_defenders = game._players_on_team(
            SIDE_COUNTER_TERRORISTS,
            alive_only=True,
        )
        if len(living_defenders) != 1 or living_defenders[0].id != bot.id:
            plan.defensive_commitments.pop(bot.id, None)
            return ""

        freshest = self._freshest_contact(plan)
        commitment = plan.defensive_commitments.get(bot.id)
        if freshest:
            enemy = game._breach_player_by_id(freshest.player_id)
            currently_visible = bool(
                enemy
                and not enemy.eliminated
                and game._team_can_see_player(bot.team_index, enemy)
            )
            if (
                commitment is None
                or freshest.observed_tactical_round
                > commitment.observed_tactical_round
                or currently_visible
                and freshest.node_id != commitment.target_node_id
            ):
                commitment = DefensiveCommitment(
                    target_node_id=freshest.node_id,
                    observed_tactical_round=freshest.observed_tactical_round,
                )
                plan.defensive_commitments[bot.id] = commitment

        if not commitment:
            return ""
        age = game.tactical_round - commitment.observed_tactical_round
        if (
            age > self.profile.solo_contact_commitment_tactical_rounds
            or bot.position_id == commitment.target_node_id
            and freshest is None
        ):
            plan.defensive_commitments.pop(bot.id, None)
            plan.routes.pop(bot.id, None)
            return ""
        return commitment.target_node_id

    def _strategy_target_node(
        self,
        game: BreachPointGame,
        plan: TeamPlan,
        bot: BreachPointPlayer,
        assignment: TacticalAssignment | None,
    ) -> str:
        """Return a temporary route target for the current attack pattern."""

        if plan.attack_strategy_id == ATTACK_STRATEGY_FAKE:
            if plan.strategy_committed:
                return plan.attack_site_id
            if assignment and assignment.role in {ROLE_ENTRY, ROLE_LURKER}:
                return plan.decoy_site_id
            return plan.primary_staging_node_id or plan.attack_site_id

        if plan.attack_strategy_id == ATTACK_STRATEGY_SPLIT and assignment:
            if plan.strategy_committed:
                return plan.attack_site_id
            if self._uses_split_route(plan, assignment):
                return plan.split_staging_node_id
            return plan.primary_staging_node_id or plan.attack_site_id
        return ""

    @staticmethod
    def _uses_split_route(
        plan: TeamPlan,
        assignment: TacticalAssignment,
    ) -> bool:
        support_count = sum(
            candidate.role == ROLE_SUPPORT for candidate in plan.assignments.values()
        )
        if support_count >= 2:
            return assignment.role == ROLE_SUPPORT
        if support_count == 1:
            return assignment.role in {ROLE_SUPPORT, ROLE_LURKER}
        if any(
            candidate.role == ROLE_LURKER for candidate in plan.assignments.values()
        ):
            return assignment.role == ROLE_LURKER
        return assignment.role == ROLE_ENTRY

    def shortest_path_step(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        target_nodes: tuple[str, ...],
    ) -> str | None:
        """Return a stable next edge instead of recalculating into ping-pong."""

        target_set = {node_id for node_id in target_nodes if game._node(node_id)}
        if not target_set or bot.position_id in target_set:
            plan = self.team_plans.get(bot.team_index)
            if plan:
                plan.routes.pop(bot.id, None)
            return None

        plan = self.team_plans.get(bot.team_index)
        route = plan.routes.get(bot.id) if plan else None
        if route and route.target_node_id in target_set:
            try:
                current_index = route.node_ids.index(bot.position_id)
            except ValueError:
                current_index = -1
            if current_index >= 0 and current_index + 1 < len(route.node_ids):
                next_node_id = route.node_ids[current_index + 1]
                if self._route_step_is_available(
                    game,
                    bot,
                    next_node_id,
                    allows_known_fire=route.allows_known_fire,
                ):
                    return next_node_id
            plan.routes.pop(bot.id, None)

        for allow_known_fire in (False, True):
            queue: deque[tuple[str, tuple[str, ...]]] = deque(
                [(bot.position_id, (bot.position_id,))]
            )
            visited = {bot.position_id}
            while queue:
                node_id, path = queue.popleft()
                node = game._node(node_id)
                if not node:
                    continue
                for neighbor_id in node.adjacent:
                    if neighbor_id in visited:
                        continue
                    if not self._route_step_is_available(
                        game,
                        bot,
                        neighbor_id,
                        allows_known_fire=allow_known_fire,
                    ):
                        continue
                    next_path = (*path, neighbor_id)
                    if neighbor_id in target_set:
                        if plan:
                            plan.routes[bot.id] = TacticalRoute(
                                target_node_id=neighbor_id,
                                node_ids=next_path,
                                allows_known_fire=allow_known_fire,
                            )
                        return next_path[1]
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, next_path))
        if plan:
            plan.routes.pop(bot.id, None)
        return None

    def _route_step_is_available(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        node_id: str,
        *,
        allows_known_fire: bool,
    ) -> bool:
        """Check only information the bot's team may legally use for routing."""

        if not allows_known_fire and game._team_knows_area_effect(
            bot.team_index,
            UTILITY_EFFECT_FIRE,
            node_id,
        ):
            return False
        if not allows_known_fire and self._is_repeatedly_failed_route_node(
            game,
            bot,
            node_id,
        ):
            return False
        enemy = game._living_enemy_at(bot, node_id)
        return not (
            enemy
            and game._team_can_see_player(bot.team_index, enemy)
            and not game.rules.allow_contested_entry
        )

    def _is_repeatedly_failed_route_node(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        node_id: str,
    ) -> bool:
        """Avoid a repeatedly lost entry on the safe pathfinding pass.

        The second pathfinding pass may still use the node when it is the only
        route. This makes learning adaptive without allowing memory to make an
        objective unreachable.
        """

        memory = self.squad_memories.get(bot.squad_index)
        if not memory:
            return False
        failures: dict[str, int] = {}
        for remembered in memory.eliminations:
            if (
                remembered.victim_side_index != bot.team_index
                or remembered.victim_node_id != node_id
                or not 0
                <= game.round - remembered.round_marker[0]
                < self.profile.elimination_memory_rounds
            ):
                continue
            failures[remembered.source_node_id] = (
                failures.get(remembered.source_node_id, 0) + 1
            )
        return max(failures.values(), default=0) >= (
            self.profile.adaptive_smoke_elimination_count
        )

    def buy_action(self, game: BreachPointGame, bot: BreachPointPlayer) -> str | None:
        """Choose a legal deterministic buy within the squad's shared plan."""

        self._ensure_current_round(game)
        if game._buy_turn_error(bot) is not None:
            return None
        primary = game._primary_weapon(bot)
        if not primary:
            preferred_weapon = self._preferred_primary_weapon(game, bot)
            if preferred_weapon:
                action_id = f"buy_weapon_{preferred_weapon.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            preferred_sidearm = self._preferred_sidearm_weapon(game, bot)
            if preferred_sidearm:
                action_id = f"buy_weapon_{preferred_sidearm.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            pistol_utility = self._pistol_round_utility(game, bot)
            if pistol_utility:
                action_id = f"buy_utility_{pistol_utility.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            if (
                bot.armor < game.economy.maximum_armor
                and bot.cash <= game.economy.starting_cash
                and bot.cash >= game.economy.armor_cost
                and self._legal_buy_action(game, bot, "buy_armor")
            ):
                return "buy_armor"
            return "finish_buy"
        preferred_weapon = self._preferred_primary_weapon(game, bot)
        if preferred_weapon:
            action_id = f"buy_weapon_{preferred_weapon.id}"
            if self._legal_buy_action(game, bot, action_id):
                return action_id
        if (
            bot.armor < game.economy.maximum_armor
            and bot.cash >= game.economy.armor_cost
            and self._legal_buy_action(game, bot, "buy_armor")
        ):
            return "buy_armor"
        priority_equipment = self.team_priority_equipment(game, bot)
        if priority_equipment:
            action_id = f"buy_equipment_{priority_equipment.id}"
            if self._legal_buy_action(game, bot, action_id):
                return action_id
        preferred_sidearm = self._preferred_sidearm_weapon(game, bot)
        if preferred_sidearm:
            action_id = f"buy_weapon_{preferred_sidearm.id}"
            if self._legal_buy_action(game, bot, action_id):
                return action_id
        for utility in get_purchasable_utilities(bot.team_index):
            action_id = f"buy_utility_{utility.id}"
            if (
                bot.utility_counts.get(utility.id, 0)
                < min(utility.maximum_carry, self.profile.maximum_duplicate_utility)
                and game._is_buy_utility_enabled(bot, action_id=action_id) is None
            ):
                return action_id
        return "finish_buy"

    @staticmethod
    def weapon_donation_response_action(
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Accept a real slot upgrade; decline wasteful equal or weaker offers."""

        donation = game.pending_weapon_donation
        if (
            not donation
            or donation.recipient_id != bot.id
            or game._is_weapon_donation_response_enabled(bot) is not None
        ):
            return None
        weapon = get_weapon(donation.weapon_id)
        if not weapon:
            return "decline_weapon_donation"
        owned = (
            game._primary_weapon(bot)
            if weapon.slot == WEAPON_SLOT_PRIMARY
            else game._sidearm(bot)
        )
        if owned is None or weapon.cost > owned.cost:
            return "accept_weapon_donation"
        return "decline_weapon_donation"

    @staticmethod
    def _legal_buy_action(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        action_id: str,
    ) -> bool:
        """Keep strategy recommendations behind authoritative buy validation."""

        if action_id.startswith("buy_weapon_"):
            return game._is_buy_weapon_enabled(bot, action_id=action_id) is None
        if action_id.startswith("buy_utility_"):
            return game._is_buy_utility_enabled(bot, action_id=action_id) is None
        if action_id.startswith("buy_equipment_"):
            return game._is_buy_equipment_enabled(bot, action_id=action_id) is None
        if action_id == "buy_armor":
            return game._is_buy_armor_enabled(bot) is None
        return action_id == "finish_buy" and game._is_finish_buy_enabled(bot) is None

    def _pistol_round_utility(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> UtilityProfile | None:
        """Coordinate one smoke and flash package on a fresh side economy."""

        if (
            not self._is_regulation_pistol_round(game)
            or bot.cash > game.economy.starting_cash
            or bot.armor
        ):
            return None
        assignment = self.assignment_for(bot.id)
        if not assignment:
            return None
        is_utility_role = bool(
            bot.team_index == SIDE_TERRORISTS
            and assignment.role != ROLE_ENTRY
            or bot.team_index == SIDE_COUNTER_TERRORISTS
            and bool(bot.equipment_counts)
        )
        if not is_utility_role:
            return None
        teammates = game._players_on_team(bot.team_index, alive_only=True)
        utilities = list(get_purchasable_utilities(bot.team_index))
        if bot.team_index == SIDE_COUNTER_TERRORISTS and bot.equipment_counts:
            utilities.sort(key=lambda utility: utility.effect != UTILITY_EFFECT_FLASH)
        for utility in utilities:
            if utility.effect not in {UTILITY_EFFECT_SMOKE, UTILITY_EFFECT_FLASH}:
                continue
            team_target = (
                max(
                    1,
                    len(teammates) // self.profile.pistol_flash_team_divisor,
                )
                if bot.team_index == SIDE_TERRORISTS
                and utility.effect == UTILITY_EFFECT_FLASH
                else 1
            )
            if (
                bot.cash >= utility.cost
                and bot.utility_counts.get(utility.id, 0) < utility.maximum_carry
                and game._is_buy_utility_enabled(
                    bot,
                    action_id=f"buy_utility_{utility.id}",
                )
                is None
                and sum(
                    teammate.utility_counts.get(utility.id, 0) for teammate in teammates
                )
                < team_target
            ):
                return utility
        return None

    @staticmethod
    def _is_regulation_pistol_round(game: BreachPointGame) -> bool:
        """Return whether the current round starts a regulation half."""

        return bool(
            game.overtime_period == 0
            and game.round in {1, game.match_format.rounds_per_half + 1}
        )

    def team_priority_equipment(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> EquipmentProfile | None:
        """Fund objective equipment only after the core combat kit is protected."""

        if (
            self._is_regulation_pistol_round(game)
            or game._primary_weapon(bot) is None
            or bot.armor < game.economy.maximum_armor
        ):
            return None
        squad_bots = [
            teammate
            for teammate in game._turn_order_players_on_team(bot.team_index)
            if teammate.is_bot
        ]
        rotators = [
            teammate
            for teammate in squad_bots
            if (assignment := self.assignment_for(teammate.id)) is not None
            and assignment.role == ROLE_ROTATOR
        ]
        designated = rotators[0] if rotators else squad_bots[-1] if squad_bots else None
        if not designated or designated.id != bot.id:
            return None
        return next(
            (
                equipment
                for equipment in get_purchasable_equipment(bot.team_index)
                if equipment.action_point_modifiers
                and bot.equipment_counts.get(equipment.id, 0) < equipment.maximum_carry
                and bot.cash >= equipment.cost
                and not self._team_has_equipment(game, bot.team_index, equipment)
            ),
            None,
        )

    def _preferred_primary_weapon(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> WeaponProfile | None:
        """Choose one affordable primary while coordinating specialist roles."""

        purchasable = get_purchasable_weapons(
            bot.team_index,
            WEAPON_SLOT_PRIMARY,
        )
        owned_primary = game._primary_weapon(bot)
        if (
            owned_primary
            and owned_primary.purchase_role == PURCHASE_ROLE_ANTI_ECO
            and self._should_buy_close_range_primary(game, bot)
        ):
            return None
        if owned_primary:
            purchasable = tuple(
                weapon for weapon in purchasable if weapon.cost > owned_primary.cost
            )
        precision_weapons = tuple(
            weapon
            for weapon in purchasable
            if weapon.purchase_role == PURCHASE_ROLE_PRECISION
        )
        affordable_precision = tuple(
            weapon for weapon in precision_weapons if bot.cash >= weapon.cost
        )
        precision_weapon = max(
            affordable_precision,
            key=lambda weapon: weapon.cost,
            default=None,
        )
        non_precision_costs = [
            weapon.cost
            for weapon in purchasable
            if weapon.purchase_role != PURCHASE_ROLE_PRECISION
        ]
        premium_precision = bool(
            precision_weapon
            and non_precision_costs
            and precision_weapon.cost > max(non_precision_costs)
        )
        if (
            precision_weapon
            and premium_precision
            and self._is_designated_precision_user(game, bot)
            and not any(
                (weapon := game._primary_weapon(teammate)) and weapon.requires_aim
                for teammate in game._players_on_team(bot.team_index, alive_only=True)
                if teammate.id != bot.id
            )
        ):
            return precision_weapon
        affordable = tuple(
            weapon
            for weapon in purchasable
            if weapon.purchase_role != PURCHASE_ROLE_PRECISION
            and bot.cash >= weapon.cost
        )
        close_range = tuple(
            weapon
            for weapon in affordable
            if weapon.purchase_role == PURCHASE_ROLE_ANTI_ECO
        )
        budget = tuple(
            weapon
            for weapon in affordable
            if weapon.purchase_role == PURCHASE_ROLE_BUDGET
        )
        standard = tuple(
            weapon
            for weapon in affordable
            if weapon.purchase_role == PURCHASE_ROLE_STANDARD
        )
        if close_range and self._should_buy_close_range_primary(game, bot):
            return self._preferred_close_range_weapon(bot, close_range)
        elif standard:
            affordable = standard
        elif budget:
            affordable = tuple(
                weapon
                for weapon in budget
                if bot.armor >= game.economy.maximum_armor
                or bot.cash - weapon.cost >= game.economy.armor_cost
            )
        else:
            affordable = ()
        if not affordable and (
            precision_weapon
            and self._is_designated_precision_user(game, bot)
            and (
                bot.armor >= game.economy.maximum_armor
                or bot.cash - precision_weapon.cost >= game.economy.armor_cost
            )
        ):
            affordable = (precision_weapon,)
        if not affordable:
            return None
        return max(
            affordable,
            key=lambda weapon: (
                weapon.cost,
                weapon.max_range,
                max(weapon.damage_by_range),
            ),
            default=None,
        )

    def _preferred_close_range_weapon(
        self,
        bot: BreachPointPlayer,
        weapons: tuple[WeaponProfile, ...],
    ) -> WeaponProfile | None:
        """Match close-range weapon traits to the bot's assigned squad role."""

        assignment = self.assignment_for(bot.id)
        if assignment and assignment.role == ROLE_ENTRY:
            return max(
                weapons,
                key=lambda weapon: (
                    weapon.damage_at_range(0),
                    -weapon.armor_reduction_percent,
                    weapon.kill_reward,
                    -weapon.cost,
                ),
                default=None,
            )
        return max(
            weapons,
            key=lambda weapon: (
                weapon.shots_per_activation,
                weapon.followup_damage_percent,
                weapon.damage_at_range(weapon.max_range),
                -weapon.cost,
            ),
            default=None,
        )

    def _is_designated_close_range_user(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> bool:
        """Limit short-range force-buys to bots whose round roles can exploit them."""

        role_priority = (
            {
                ROLE_ENTRY: 0,
                ROLE_LURKER: 1,
                ROLE_SUPPORT: 2,
                ROLE_OBJECTIVE: 3,
            }
            if bot.team_index == SIDE_TERRORISTS
            else {ROLE_ROTATOR: 0, ROLE_ANCHOR: 1}
        )
        squad_bots = [
            teammate
            for teammate in game._turn_order_players_on_team(bot.team_index)
            if teammate.is_bot
        ]
        turn_order = {teammate.id: index for index, teammate in enumerate(squad_bots)}

        def candidate_rank(teammate: BreachPointPlayer) -> tuple[int, int]:
            assignment = self.assignment_for(teammate.id)
            return (
                role_priority.get(
                    assignment.role if assignment else "",
                    len(role_priority),
                ),
                turn_order[teammate.id],
            )

        candidates = sorted(
            squad_bots,
            key=candidate_rank,
        )
        designated_count = max(
            1,
            len(candidates) // self.profile.close_range_primary_team_divisor,
        )
        return bot.id in {teammate.id for teammate in candidates[:designated_count]}

    def _should_buy_close_range_primary(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> bool:
        """Use a close-range primary for the conversion after the first loss."""

        if not 0 <= bot.squad_index < len(game.squad_loss_streaks):
            return False
        opposing_side = next(
            side_index for side_index in SIDE_INDEXES if side_index != bot.team_index
        )
        opposing_squad = game._squad_for_side(opposing_side)
        if not 0 <= opposing_squad < len(game.squad_loss_streaks):
            return False
        conversion_loss_count = min(
            game.economy.maximum_loss_count,
            game.economy.initial_loss_count + 1,
        )
        return bool(
            game.squad_loss_streaks[bot.squad_index] == 0
            and game.squad_loss_streaks[opposing_squad] == conversion_loss_count
            and self._is_designated_close_range_user(game, bot)
        )

    def _preferred_sidearm_weapon(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> WeaponProfile | None:
        """Assign one range-capable sidearm to the squad's best-suited role."""

        purchasable = tuple(
            weapon
            for weapon in get_purchasable_weapons(
                bot.team_index,
                WEAPON_SLOT_SIDEARM,
            )
            if bot.cash >= weapon.cost and bot.sidearm_weapon_id != weapon.id
        )
        if not purchasable:
            return None
        teammates = game._turn_order_players_on_team(bot.team_index)
        if any(
            (sidearm := game._sidearm(teammate)) is not None and sidearm.cost > 0
            for teammate in teammates
            if teammate.id != bot.id
        ):
            return None
        preferred_weapon = max(
            purchasable,
            key=lambda weapon: (
                weapon.max_range,
                min(weapon.damage_by_range),
                -weapon.armor_reduction_percent,
                -weapon.cost,
            ),
        )
        eligible_bots = [
            teammate
            for teammate in teammates
            if teammate.is_bot
            and (
                game._primary_weapon(teammate) is not None
                or self._pistol_round_utility(game, teammate) is None
            )
        ]
        eligible_bots.sort(
            key=lambda teammate: self._sidearm_upgrade_rank(
                game,
                teammate,
                preferred_weapon,
            )
        )
        if not eligible_bots or eligible_bots[0].id != bot.id:
            return None
        return preferred_weapon

    def _sidearm_upgrade_rank(
        self,
        game: BreachPointGame,
        teammate: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> tuple[int, int, int, int]:
        """Prefer a sidearm user whose assignment benefits from its extra range."""

        teammates = game._turn_order_players_on_team(teammate.team_index)
        turn_order = {player.id: index for index, player in enumerate(teammates)}
        assignment = self.assignment_for(teammate.id)
        if teammate.team_index == SIDE_TERRORISTS:
            role_order = {
                ROLE_ENTRY: 0,
                ROLE_LURKER: 1,
                ROLE_SUPPORT: 2,
                ROLE_OBJECTIVE: 3,
            }
            return (
                role_order.get(assignment.role if assignment else "", len(role_order)),
                0,
                0,
                turn_order[teammate.id],
            )
        site = game._node(assignment.anchor_node_id) if assignment else None
        ingress_ids = site.attacker_approach_ids if site else ()
        defender_ids = site.defender_position_ids if site else ()
        useful_lane_count = sum(
            (distance := game._combat_distance(position_id, ingress_id)) is not None
            and 0 < distance <= weapon.max_range
            for position_id in defender_ids
            for ingress_id in ingress_ids
        )
        return (
            0 if assignment and assignment.role == ROLE_ANCHOR else 1,
            len(ingress_ids) if ingress_ids else len(game.tactical_map.nodes),
            -useful_lane_count,
            turn_order[teammate.id],
        )

    def _is_designated_precision_user(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> bool:
        assignment = self.assignment_for(bot.id)
        preferred_role = (
            ROLE_ROTATOR if bot.team_index == SIDE_COUNTER_TERRORISTS else ROLE_SUPPORT
        )
        eligible_bots = [
            teammate
            for teammate in game._turn_order_players_on_team(bot.team_index)
            if teammate.is_bot
            and (
                (teammate_assignment := self.assignment_for(teammate.id)) is not None
                and teammate_assignment.role == preferred_role
            )
        ]
        if not eligible_bots:
            eligible_bots = [
                teammate
                for teammate in game._turn_order_players_on_team(bot.team_index)
                if teammate.is_bot
            ]
        return bool(assignment and eligible_bots and eligible_bots[0].id == bot.id)

    def weapon_switch_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Switch freely when another owned weapon can use the remaining AP."""

        equipped = game._equipped_weapon(bot)
        if not equipped or bot.action_points <= 0 or not visible_enemies:
            return None
        for weapon, action_id in (
            (game._primary_weapon(bot), "equip_primary"),
            (game._sidearm(bot), "equip_sidearm"),
        ):
            if (
                not weapon
                or weapon.id == equipped.id
                or game._loaded_ammunition(bot, weapon) <= 0
                or bot.weapon_shots_fired_this_activation.get(weapon.id, 0)
                >= weapon.shots_per_activation
                or game._is_equip_weapon_enabled(bot, action_id=action_id) is not None
            ):
                continue
            if weapon.requires_aim:
                if bot.action_points >= weapon.hold_action_point_cost and any(
                    game._can_hold_angle(bot, enemy.position_id, weapon)
                    for enemy in visible_enemies
                ):
                    return action_id
                continue
            if bot.action_points >= weapon.action_point_cost and any(
                game._weapon_can_reach(bot, enemy, weapon) for enemy in visible_enemies
            ):
                return action_id
        return None

    @staticmethod
    def _immediate_fire_weapon_switch_action(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Switch only when the new weapon can fire during this activation."""

        equipped = game._equipped_weapon(bot)
        if not equipped or bot.action_points <= 0 or not visible_enemies:
            return None
        for weapon, action_id in (
            (game._primary_weapon(bot), "equip_primary"),
            (game._sidearm(bot), "equip_sidearm"),
        ):
            if (
                not weapon
                or weapon.id == equipped.id
                or weapon.requires_aim
                or game._loaded_ammunition(bot, weapon) <= 0
                or bot.weapon_shots_fired_this_activation.get(weapon.id, 0)
                >= weapon.shots_per_activation
                or bot.action_points < weapon.action_point_cost
                or game._is_equip_weapon_enabled(bot, action_id=action_id) is not None
                or not any(
                    game._weapon_can_reach(bot, enemy, weapon)
                    for enemy in visible_enemies
                )
            ):
                continue
            return action_id
        return None

    def objective_disengage_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        *,
        lethal_target: BreachPointPlayer | None = None,
        contemplated_action_cost: int = 0,
    ) -> str | None:
        """Rotate when spending another AP would miss the defuse deadline."""

        if lethal_target is None:
            shootable_enemies = [
                enemy
                for enemy in self._visible_enemies(game, bot)
                if game._is_shoot_enabled(bot, action_id=f"shoot_{enemy.id}") is None
            ]
            lethal_target = self._route_opening_target(
                game,
                bot,
                shootable_enemies,
            )
            weapon = game._equipped_weapon(bot)
            contemplated_action_cost = (
                weapon.action_point_cost if shootable_enemies and weapon else 0
            )

        if (
            bot.team_index != SIDE_COUNTER_TERRORISTS
            or game.bomb_state != BOMB_PLANTED
            or bot.position_id == game.bomb_location_id
        ):
            return None
        distance = game._node_distance(bot.position_id, game.bomb_location_id)
        if distance is None or distance <= 0:
            return None
        first_move_cost = (
            game.rules.move_cost
            if lethal_target is not None
            else game._movement_action_point_cost(bot)
        )
        route_cost = first_move_cost + max(0, distance - 1) * game.rules.move_cost
        required_objective_cost = route_cost + game._defuse_action_point_cost(bot)
        future_capacity = max(0, game.bomb_fuse_remaining - 1) * (
            game.rules.action_points_per_activation
        )
        available_capacity = bot.action_points + future_capacity
        if required_objective_cost > available_capacity:
            return None
        if required_objective_cost + contemplated_action_cost <= available_capacity:
            return None
        if bot.action_points < first_move_cost:
            return None
        next_node = self.shortest_path_step(game, bot, (game.bomb_location_id,))
        action_id = f"move_{next_node}" if next_node else ""
        if action_id and game._is_move_enabled(bot, action_id=action_id) is None:
            return action_id
        return None

    def _route_opening_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        shootable_enemies: list[BreachPointPlayer],
    ) -> BreachPointPlayer | None:
        """Return a lethal shared-node target whose removal permits a rotation."""

        engaged_enemies = [
            enemy for enemy in shootable_enemies if enemy.position_id == bot.position_id
        ]
        if len(engaged_enemies) != 1:
            return None
        target = engaged_enemies[0]
        return target if self._attack_would_eliminate(game, bot, target) else None

    def objective_smoke_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        next_node: str,
        target_nodes: tuple[str, ...],
    ) -> str | None:
        """Use smoke before entering a known objective when it preserves tempo."""

        if next_node not in target_nodes or (
            game._is_smoked(next_node)
            and game._team_knows_smoke(bot.team_index, next_node)
        ):
            return None
        if bot.team_index == SIDE_TERRORISTS:
            valid_smoke_nodes = (
                {game.bomb_location_id}
                if game.bomb_state == BOMB_DROPPED
                else set(game.tactical_map.bomb_site_ids())
            )
            if next_node not in valid_smoke_nodes:
                return None
        objective_is_live = bool(
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state == BOMB_PLANTED
            or bot.team_index == SIDE_TERRORISTS
            and game.bomb_state in {BOMB_CARRIED, BOMB_DROPPED}
        )
        if not objective_is_live:
            return None
        if (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and next_node == game.bomb_location_id
            and bot.action_points - game._movement_action_point_cost(bot)
            >= game._defuse_action_point_cost(bot)
        ):
            return None
        smoke = next(
            (
                utility
                for utility in get_purchasable_utilities(bot.team_index)
                if utility.effect == UTILITY_EFFECT_SMOKE
                and bot.utility_counts.get(utility.id, 0) > 0
            ),
            None,
        )
        if not smoke:
            return None
        if (
            bot.action_points
            < smoke.action_point_cost + game._movement_action_point_cost(bot)
        ):
            return None
        action_id = f"throw_{smoke.id}_{next_node}"
        if game._is_throw_utility_enabled(bot, action_id=action_id) is None:
            return action_id
        return None

    def _attacking_route_smoke_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Smoke a known or repeatedly lethal crossfire before entering it."""

        assignment = self.assignment_for(bot.id)
        plan = self.team_plans.get(SIDE_TERRORISTS)
        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or not assignment
            or assignment.role not in {ROLE_OBJECTIVE, ROLE_ENTRY, ROLE_SUPPORT}
            or not plan
            or game._is_engaged(bot)
        ):
            return None
        smoke = next(
            (
                utility
                for utility in get_purchasable_utilities(bot.team_index)
                if utility.effect == UTILITY_EFFECT_SMOKE
                and bot.utility_counts.get(utility.id, 0) > 0
            ),
            None,
        )
        movement_cost = game._movement_action_point_cost(bot)
        if (
            not smoke
            or bot.action_points < smoke.action_point_cost + movement_cost
        ):
            return None
        target_nodes = self.target_nodes(game, bot)
        next_node = self.shortest_path_step(game, bot, target_nodes)
        if not next_node:
            return None
        exposed_contacts = [
            contact
            for contact in plan.contacts.values()
            if not game._team_knows_smoke(bot.team_index, contact.node_id)
            and (
                contact.node_id in {bot.position_id, next_node}
                or game.tactical_map.has_sightline(
                    contact.node_id,
                    bot.position_id,
                )
                or game.tactical_map.has_sightline(
                    contact.node_id,
                    next_node,
                )
            )
        ]
        contact_counts: dict[str, int] = {}
        for contact in exposed_contacts:
            contact_counts[contact.node_id] = (
                contact_counts.get(contact.node_id, 0) + 1
            )
        remembered_counts: dict[str, int] = {}
        memory = self.squad_memories.get(bot.squad_index)
        for remembered in memory.eliminations if memory else ():
            if (
                remembered.victim_side_index != bot.team_index
                or remembered.victim_node_id != next_node
                or not 0
                <= game.round - remembered.round_marker[0]
                < self.profile.elimination_memory_rounds
                or game._team_knows_smoke(
                    bot.team_index,
                    remembered.source_node_id,
                )
            ):
                continue
            remembered_counts[remembered.source_node_id] = (
                remembered_counts.get(remembered.source_node_id, 0) + 1
            )
        repeated_lanes = {
            node_id: count
            for node_id, count in remembered_counts.items()
            if count >= self.profile.adaptive_smoke_elimination_count
        }
        if (
            len(exposed_contacts) < self.profile.route_smoke_contact_count
            and not repeated_lanes
        ):
            return None
        for node_id, count in repeated_lanes.items():
            contact_counts[node_id] = max(contact_counts.get(node_id, 0), count)
        stable_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        candidate_nodes = sorted(
            contact_counts,
            key=lambda node_id: (
                -contact_counts[node_id],
                stable_order.get(node_id, len(stable_order)),
            ),
        )
        candidate_nodes.extend(
            node_id
            for node_id in (next_node, bot.position_id)
            if node_id not in candidate_nodes
        )
        for node_id in candidate_nodes:
            if game._team_knows_smoke(bot.team_index, node_id):
                continue
            action_id = f"throw_{smoke.id}_{node_id}"
            if game._is_throw_utility_enabled(bot, action_id=action_id) is None:
                return action_id
        return None

    @staticmethod
    def pickup_weapon_action(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        *,
        postround: bool = False,
    ) -> str | None:
        """Recover a strictly better usable weapon without abandoning objectives."""

        if (
            (not postround and game.bomb_state == BOMB_PLANTED)
            or (not postround and bot.held_angle_node_id)
            or bot.action_points < game.rules.weapon_pickup_cost
            or (
                not postround
                and bot.team_index == SIDE_TERRORISTS
                and game.bomb_carrier_id == bot.id
            )
        ):
            return None

        candidates: list[tuple[tuple[int, int, int], str]] = []
        for dropped_weapon in game._dropped_weapons_at(bot.position_id):
            weapon = get_weapon(dropped_weapon.weapon_id)
            if not weapon:
                continue
            action_id = game._dropped_weapon_action_id(dropped_weapon)
            if game._is_pick_up_weapon_enabled(bot, action_id=action_id) is not None:
                continue
            total_ammunition = (
                dropped_weapon.magazine_ammo
                + dropped_weapon.reserve_units * weapon.reload_rounds_per_unit
            )
            if total_ammunition <= 0:
                continue
            current = (
                game._primary_weapon(bot)
                if weapon.slot == WEAPON_SLOT_PRIMARY
                else game._sidearm(bot)
            )
            if current:
                current_loaded_ammunition = game._loaded_ammunition(bot, current)
                current_ammunition = (
                    current_loaded_ammunition
                    + game._reserve_ammunition_units(bot, current)
                    * current.reload_rounds_per_unit
                )
                current_score = (
                    int(current_loaded_ammunition > 0),
                    current.cost,
                    current_ammunition,
                )
            else:
                current_score = (-1, -1, -1)
            candidate_score = (
                int(dropped_weapon.magazine_ammo > 0),
                weapon.cost,
                total_ammunition,
            )
            if candidate_score > current_score:
                candidates.append((candidate_score, action_id))
        if not candidates:
            return None
        return max(candidates, key=lambda candidate: candidate[0])[1]

    @staticmethod
    def reload_action(
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Reload only when the current weapon cannot make its next full attack."""

        weapon = game._equipped_weapon(bot)
        if (
            not weapon
            or game._loaded_ammunition(bot, weapon) >= weapon.ammunition_per_attack
            or game._is_reload_enabled(bot) is not None
        ):
            return None
        return "reload"

    def _ensure_current_round(self, game: BreachPointGame) -> None:
        marker = self._round_marker(game)
        if any(
            team_index not in self.team_plans
            or self.team_plans[team_index].round_marker != marker
            for team_index in SIDE_INDEXES
        ):
            self.begin_combat_round(game)

    @staticmethod
    def _round_marker(
        game: BreachPointGame,
    ) -> tuple[int, int, int, tuple[int, ...]]:
        return (
            game.round,
            game.overtime_period,
            game.overtime_round,
            tuple(game.side_squad_indexes),
        )

    def _refresh_assignments(self, game: BreachPointGame) -> None:
        for team_index in SIDE_INDEXES:
            plan = self.team_plans.get(team_index)
            if not plan:
                continue
            teammates = game._turn_order_players_on_team(team_index, alive_only=True)
            signature = tuple(player.id for player in teammates) + (
                plan.objective_player_id if team_index == SIDE_TERRORISTS else "",
            )
            if signature == plan.roster_signature:
                continue
            plan.roster_signature = signature
            proposed = self._build_assignments(
                game,
                team_index,
                teammates,
                objective_player_id=plan.objective_player_id,
            )
            surviving_ids = {player.id for player in teammates}
            plan.routes = {
                player_id: route
                for player_id, route in plan.routes.items()
                if player_id in surviving_ids
            }
            plan.defensive_commitments = {
                player_id: commitment
                for player_id, commitment in plan.defensive_commitments.items()
                if player_id in surviving_ids
            }
            plan.fallback_commitments = {
                player_id: commitment
                for player_id, commitment in plan.fallback_commitments.items()
                if player_id in surviving_ids
            }
            stable_assignments = {
                player_id: assignment
                for player_id, assignment in plan.assignments.items()
                if player_id in surviving_ids
            }
            for player_id, assignment in proposed.items():
                stable_assignments.setdefault(player_id, assignment)
            if team_index == SIDE_TERRORISTS:
                for player_id, assignment in list(stable_assignments.items()):
                    if (
                        assignment.role == ROLE_OBJECTIVE
                        and player_id != plan.objective_player_id
                    ):
                        stable_assignments[player_id] = proposed.get(
                            player_id,
                            TacticalAssignment(player_id, ROLE_SUPPORT),
                        )
                if plan.objective_player_id:
                    carrier_assignment = proposed.get(plan.objective_player_id)
                    stable_assignments[plan.objective_player_id] = TacticalAssignment(
                        player_id=plan.objective_player_id,
                        role=ROLE_OBJECTIVE,
                        anchor_node_id=(
                            carrier_assignment.anchor_node_id
                            if carrier_assignment
                            else ""
                        ),
                    )
            plan.assignments = stable_assignments

    def _build_assignments(
        self,
        game: BreachPointGame,
        team_index: int,
        teammates: list[BreachPointPlayer],
        *,
        objective_player_id: str = "",
    ) -> dict[str, TacticalAssignment]:
        assignments: dict[str, TacticalAssignment] = {}
        if team_index == SIDE_TERRORISTS:
            non_carriers = [
                player for player in teammates if player.id != objective_player_id
            ]
            entry_id = (
                non_carriers[0].id
                if len(teammates) >= self.profile.entry_minimum_team_size
                and non_carriers
                else ""
            )
            lurker_id = ""
            if len(teammates) >= self.profile.lurker_minimum_team_size:
                candidate = non_carriers[-1] if non_carriers else None
                lurker_id = (
                    candidate.id if candidate and candidate.id != entry_id else ""
                )
            for teammate in teammates:
                if teammate.id == objective_player_id:
                    role = ROLE_OBJECTIVE
                elif teammate.id == entry_id:
                    role = ROLE_ENTRY
                elif teammate.id == lurker_id:
                    role = ROLE_LURKER
                else:
                    role = ROLE_SUPPORT
                assignments[teammate.id] = TacticalAssignment(teammate.id, role)
            return assignments

        site_ids = game.tactical_map.bomb_site_ids()
        site_rotation = self._site_assignment_rotation(game, len(site_ids))
        staging_nodes = self._central_staging_nodes(game)
        extra_players = max(0, len(teammates) - len(site_ids))
        # A partial extra site layer becomes mobile coverage. When the layer is
        # complete, keep one rotator per site so an even roster does not become
        # a static stack with no one able to answer mid or the opposite site.
        evenly_distributed_extras = extra_players % len(site_ids) if site_ids else 0
        preferred_rotators = (
            evenly_distributed_extras
            if evenly_distributed_extras
            else min(extra_players, len(site_ids))
        )
        rotator_count = min(
            extra_players,
            preferred_rotators,
            len(staging_nodes),
        )
        for index, teammate in enumerate(teammates):
            if index < len(site_ids):
                role = ROLE_ANCHOR
                anchor = site_ids[(index + site_rotation) % len(site_ids)]
            elif index - len(site_ids) < rotator_count:
                role = ROLE_ROTATOR
                anchor = staging_nodes[index - len(site_ids)]
            else:
                role = ROLE_ANCHOR
                anchor_index = index - len(site_ids) - rotator_count
                anchor = (
                    site_ids[(anchor_index + site_rotation) % len(site_ids)]
                    if site_ids
                    else ""
                )
            assignments[teammate.id] = TacticalAssignment(
                teammate.id,
                role,
                anchor,
            )
        return assignments

    @staticmethod
    def _site_assignment_rotation(game: BreachPointGame, site_count: int) -> int:
        """Rotate defender seats within each half so both sides open alike."""

        if site_count <= 0:
            return 0
        if game.overtime_period > 0:
            round_in_half = (
                max(0, game.overtime_round - 1) % game.rules.overtime_half_rounds
            ) + 1
        else:
            round_in_half = (
                max(0, game.round - 1) % game.match_format.rounds_per_half
            ) + 1
        return (round_in_half - 1) % site_count

    def _central_staging_nodes(self, game: BreachPointGame) -> tuple[str, ...]:
        sites = game.tactical_map.bomb_site_ids()
        excluded = {
            *sites,
            game.tactical_map.terrorist_spawn,
            game.tactical_map.counter_terrorist_spawn,
            *(
                position_id
                for site_id in sites
                if (site := game._node(site_id)) is not None
                for position_id in site.defender_position_ids
            ),
        }
        candidates: list[tuple[int, int, int, str]] = []
        for order, node in enumerate(game.tactical_map.nodes):
            if node.id in excluded:
                continue
            distances = [game._node_distance(node.id, site_id) for site_id in sites]
            if any(distance is None for distance in distances):
                continue
            numeric_distances = [
                int(distance) for distance in distances if distance is not None
            ]
            candidates.append(
                (max(numeric_distances), sum(numeric_distances), order, node.id)
            )
        return tuple(candidate[3] for candidate in sorted(candidates))

    def _defensive_anchor_position(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        assignment: TacticalAssignment,
    ) -> str:
        """Spread surplus site anchors across defender-side crossfire positions."""

        site_id = assignment.anchor_node_id
        site = game._node(site_id)
        if assignment.role != ROLE_ANCHOR or not site:
            return site_id
        weapon = game._primary_weapon(bot)
        if weapon and weapon.requires_aim:
            precision_position = self._precision_defensive_position(
                game,
                bot,
                site_id,
                weapon,
            )
            if precision_position:
                return precision_position
        home_anchors = [
            teammate
            for teammate in game._turn_order_players_on_team(
                SIDE_COUNTER_TERRORISTS,
                alive_only=True,
            )
            if (teammate_assignment := self.assignment_for(teammate.id)) is not None
            and teammate_assignment.role == ROLE_ANCHOR
            and teammate_assignment.anchor_node_id == site_id
        ]
        anchor_index = next(
            (
                index
                for index, teammate in enumerate(home_anchors)
                if teammate.id == bot.id
            ),
            -1,
        )
        if anchor_index < 0:
            return site_id
        preferred_positions = site.defender_position_ids or (site_id,)
        position_rotation = self._site_assignment_rotation(
            game,
            len(preferred_positions),
        )
        default_index = (anchor_index + position_rotation) % len(
            preferred_positions
        )
        failure_counts = {
            node_id: self._failed_position_count(game, bot, node_id)
            for node_id in preferred_positions
        }
        default_position = preferred_positions[default_index]
        if (
            failure_counts[default_position]
            < self.profile.failed_position_repeat_count
        ):
            return default_position
        return min(
            enumerate(preferred_positions),
            key=lambda candidate: (
                failure_counts[candidate[1]],
                abs(candidate[0] - default_index),
                candidate[0],
            ),
        )[1]

    def _failed_position_count(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        node_id: str,
    ) -> int:
        """Count recent public squad deaths at one defensive position."""

        memory = self.squad_memories.get(bot.squad_index)
        if not memory:
            return 0
        repeated_failures: dict[tuple[str, str], int] = {}
        for remembered in memory.eliminations:
            if not (
                remembered.victim_side_index == bot.team_index
                and remembered.victim_node_id == node_id
                and 0
                <= game.round - remembered.round_marker[0]
                < self.profile.elimination_memory_rounds
            ):
                continue
            signature = (remembered.source_node_id, remembered.source_name_key)
            repeated_failures[signature] = repeated_failures.get(signature, 0) + 1
        return max(repeated_failures.values(), default=0)

    def _precision_defensive_position(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        site_id: str,
        weapon: WeaponProfile,
    ) -> str:
        """Choose a deep position that turns a precision weapon into site denial."""

        site = game._node(site_id)
        if not site:
            return ""
        terrorist_spawn = game.tactical_map.terrorist_spawn
        ingress_nodes = self._site_ingress_nodes(game, site_id)
        stable_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        candidates: list[tuple[tuple[int, int, int, int, int], str]] = []
        candidate_node_ids = site.defender_position_ids or tuple(
            node.id for node in game.tactical_map.nodes
        )
        for node_id in candidate_node_ids:
            node = game._node(node_id)
            if not node:
                continue
            site_distance = game._node_distance(node.id, site_id)
            travel_distance = game._node_distance(bot.position_id, node.id)
            if (
                site_distance is None
                or site_distance > weapon.max_range - 1
                or travel_distance is None
            ):
                continue
            covered_bands = [
                distance
                for ingress_id in ingress_nodes
                if (distance := game._combat_distance(node.id, ingress_id)) is not None
                and 0 < distance <= weapon.max_range
            ]
            if not covered_bands:
                continue
            attacker_distance = game._node_distance(node.id, terrorist_spawn)
            candidates.append(
                (
                    (
                        max(covered_bands),
                        len(covered_bands),
                        attacker_distance if attacker_distance is not None else 0,
                        -travel_distance,
                        -stable_order[node.id],
                    ),
                    node.id,
                )
            )
        ranked_positions = sorted(candidates, reverse=True)
        if not ranked_positions:
            return site_id
        variant_count = min(
            len(ranked_positions),
            self.profile.precision_position_variants,
        )
        variant_index = self._site_assignment_rotation(game, variant_count)
        return ranked_positions[variant_index][1]

    @staticmethod
    def _site_ingress_nodes(
        game: BreachPointGame,
        site_id: str,
    ) -> tuple[str, ...]:
        """Return map-authored attack lanes feeding a bombsite."""

        site = game._node(site_id)
        return site.attacker_approach_ids if site else ()

    def _split_staging_node(self, game: BreachPointGame) -> str:
        """Choose covered staging one edge before a cross-map junction."""

        site_ids = game.tactical_map.bomb_site_ids()
        excluded = {
            *site_ids,
            game.tactical_map.terrorist_spawn,
            game.tactical_map.counter_terrorist_spawn,
        }
        candidates = [
            node.id
            for node in game.tactical_map.nodes
            if node.id not in excluded
            and all(
                game.tactical_map.has_sightline(node.id, site_id)
                for site_id in site_ids
            )
        ]
        if not candidates:
            candidates = list(self._central_staging_nodes(game))
        stable_order = {
            node.id: order for order, node in enumerate(game.tactical_map.nodes)
        }

        def route_rank(node_id: str) -> tuple[int, int, int]:
            defender_distance = game._node_distance(
                node_id,
                game.tactical_map.counter_terrorist_spawn,
            )
            attacker_distance = game._node_distance(
                node_id,
                game.tactical_map.terrorist_spawn,
            )
            unreachable = len(game.tactical_map.nodes)
            return (
                -(defender_distance if defender_distance is not None else -1),
                attacker_distance if attacker_distance is not None else unreachable,
                stable_order[node_id],
            )

        if not candidates:
            return ""
        junction = min(candidates, key=route_rank)
        approach = self._topology_path(
            game,
            game.tactical_map.terrorist_spawn,
            junction,
        )
        if len(approach) >= 3:
            return approach[-2]
        return junction

    def _primary_staging_node(
        self,
        game: BreachPointGame,
        attack_site_id: str,
    ) -> str:
        """Return a covered approach node with travel left before the site."""

        path = self._topology_path(
            game,
            game.tactical_map.terrorist_spawn,
            attack_site_id,
        )
        if len(path) <= 1:
            return game.tactical_map.terrorist_spawn
        for node_id in reversed(path[1:-1]):
            remaining_distance = game._node_distance(node_id, attack_site_id)
            if remaining_distance is not None and remaining_distance >= 2:
                return node_id
        return path[1]

    @staticmethod
    def _topology_path(
        game: BreachPointGame,
        start_node_id: str,
        target_node_id: str,
    ) -> tuple[str, ...]:
        """Return a deterministic topology-only path for round planning."""

        if not game._node(start_node_id) or not game._node(target_node_id):
            return ()
        frontier = deque([start_node_id])
        predecessor: dict[str, str] = {}
        visited = {start_node_id}
        while frontier:
            node_id = frontier.popleft()
            if node_id == target_node_id:
                path = [node_id]
                while path[-1] != start_node_id:
                    path.append(predecessor[path[-1]])
                return tuple(reversed(path))
            node = game._node(node_id)
            if not node:
                continue
            for neighbor_id in node.adjacent:
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                predecessor[neighbor_id] = node_id
                frontier.append(neighbor_id)
        return ()

    @staticmethod
    def _remember_strategy_route_progress(
        game: BreachPointGame,
        plan: TeamPlan,
    ) -> None:
        if (
            plan.attack_strategy_id != ATTACK_STRATEGY_SPLIT
            or not plan.split_staging_node_id
        ):
            return
        for player_id, assignment in plan.assignments.items():
            player = game._breach_player_by_id(player_id)
            if (
                player
                and not player.eliminated
                and BreachPointBotCoordinator._uses_split_route(plan, assignment)
                and player.position_id == plan.split_staging_node_id
            ):
                plan.completed_strategy_route_player_ids.add(player_id)

    def _update_attack_strategy(
        self,
        game: BreachPointGame,
        plan: TeamPlan,
    ) -> None:
        if plan.strategy_committed:
            return
        if plan.attack_strategy_id == ATTACK_STRATEGY_SPLIT:
            if game.tactical_round >= self.profile.split_commit_tactical_round:
                plan.strategy_committed = True
                return
            living_assignments = [
                (player, assignment)
                for player_id, assignment in plan.assignments.items()
                if (player := game._breach_player_by_id(player_id)) is not None
                and not player.eliminated
            ]
            route_players = [
                player
                for player, assignment in living_assignments
                if self._uses_split_route(plan, assignment)
            ]
            core_players = [
                player
                for player, assignment in living_assignments
                if not self._uses_split_route(plan, assignment)
            ]
            route_ready = not route_players or all(
                player.id in plan.completed_strategy_route_player_ids
                for player in route_players
            )
            core_ready = not core_players or all(
                player.position_id == plan.primary_staging_node_id
                for player in core_players
            )
            if route_ready and core_ready:
                plan.strategy_committed = True
            return
        if plan.attack_strategy_id != ATTACK_STRATEGY_FAKE:
            return
        decoy = game._node(plan.decoy_site_id)
        decoy_contact_nodes = (
            {
                plan.decoy_site_id,
                *game.tactical_map.visible_node_ids(plan.decoy_site_id),
            }
            if decoy
            else set()
        )
        confirmed_contacts = sum(
            contact.node_id in decoy_contact_nodes for contact in plan.contacts.values()
        )
        living_diversion_players = any(
            assignment.role in {ROLE_ENTRY, ROLE_LURKER}
            and (player := game._breach_player_by_id(player_id)) is not None
            and not player.eliminated
            for player_id, assignment in plan.assignments.items()
        )
        if (
            game.tactical_round >= self.profile.fake_commit_tactical_round
            or confirmed_contacts >= self.profile.fake_contact_commit_count
            or not living_diversion_players
        ):
            plan.strategy_committed = True

    @staticmethod
    def _active_execute_site(plan: TeamPlan) -> str:
        if (
            plan.attack_strategy_id == ATTACK_STRATEGY_FAKE
            and not plan.strategy_committed
        ):
            return plan.decoy_site_id
        if (
            plan.attack_strategy_id == ATTACK_STRATEGY_SPLIT
            and not plan.strategy_committed
        ):
            return ""
        return plan.attack_site_id

    def _update_bomb_memory(self, game: BreachPointGame, plan: TeamPlan) -> None:
        if plan.team_index == SIDE_TERRORISTS:
            if game.bomb_state in {BOMB_CARRIED, BOMB_PLANTING}:
                plan.objective_player_id = game.bomb_carrier_id
            elif game.bomb_state == BOMB_DROPPED:
                plan.objective_player_id = ""
            if game.bomb_state in {BOMB_DROPPED, BOMB_PLANTED}:
                plan.known_bomb_node_id = game.bomb_location_id
            elif game.bomb_state == BOMB_PLANTING:
                plan.known_bomb_node_id = game.planting_location_id
            else:
                plan.known_bomb_node_id = ""
            return
        if game.bomb_state == BOMB_PLANTED:
            plan.known_bomb_node_id = game.bomb_location_id
        elif game.bomb_state == BOMB_PLANTING and game._team_can_see_node(
            plan.team_index, game.planting_location_id
        ):
            plan.known_bomb_node_id = game.planting_location_id
        elif game.bomb_state == BOMB_DROPPED and game._team_can_see_node(
            plan.team_index, game.bomb_location_id
        ):
            plan.known_bomb_node_id = game.bomb_location_id
        elif (
            plan.known_bomb_node_id
            and game._team_can_see_node(plan.team_index, plan.known_bomb_node_id)
            and game.bomb_state not in {BOMB_DROPPED, BOMB_PLANTED, BOMB_PLANTING}
        ):
            plan.known_bomb_node_id = ""

    def _visible_enemies(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> list[BreachPointPlayer]:
        enemies = [
            enemy
            for enemy in game.get_active_players()
            if isinstance(enemy, BreachPointPlayer)
            and enemy.team_index != bot.team_index
            and not enemy.eliminated
            and game._can_see(bot, enemy)
        ]
        turn_positions = {
            player_id: index for index, player_id in enumerate(game.turn_player_ids)
        }
        enemies.sort(
            key=lambda enemy: (
                enemy.id != game.defusing_player_id,
                enemy.id != game.planting_player_id,
                enemy.position_id != bot.position_id,
                enemy.health * 100
                > game.rules.max_health * self.profile.low_health_percent,
                enemy.health + enemy.armor,
                not (
                    bot.team_index == SIDE_COUNTER_TERRORISTS
                    and enemy.id == game.bomb_carrier_id
                ),
                enemy.health,
                turn_positions.get(enemy.id, len(turn_positions)),
            )
        )
        return enemies

    @staticmethod
    def _objective_action(game: BreachPointGame, bot: BreachPointPlayer) -> str | None:
        return next(
            (
                action_id
                for action_id, error in (
                    ("defuse", game._is_defuse_enabled(bot)),
                    ("pick_up_bomb", game._is_pick_up_bomb_enabled(bot)),
                    ("plant", game._is_plant_enabled(bot)),
                )
                if error is None
            ),
            None,
        )

    @staticmethod
    def _objective_is_urgent(
        game: BreachPointGame,
        objective_action: str | None,
    ) -> bool:
        return bool(
            objective_action == "defuse"
            and game.bomb_fuse_remaining <= 1
            or objective_action == "plant"
            and game.tactical_round >= game.preplant_tactical_round_limit
        )

    @staticmethod
    def _objective_is_safe(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        objective_action: str | None,
        visible_enemies: list[BreachPointPlayer],
    ) -> bool:
        """Reject an objective attempt that a known responder can trivially stop."""

        if objective_action not in {"plant", "defuse"}:
            return True
        if game._is_burning(bot.position_id):
            return False
        for enemy in visible_enemies:
            weapon = game._equipped_weapon(enemy)
            if (
                not weapon
                or game._loaded_ammunition(enemy, weapon) <= 0
                or not game._weapon_can_reach(enemy, bot, weapon)
            ):
                continue
            if not weapon.requires_aim or (
                enemy.held_angle_origin_id == enemy.position_id
                and enemy.held_angle_node_id == bot.position_id
            ):
                return False
        return True

    @staticmethod
    def _attack_would_eliminate(
        game: BreachPointGame,
        bot: BreachPointPlayer,
        target: BreachPointPlayer,
    ) -> bool:
        weapon = game._equipped_weapon(bot)
        distance = game._combat_distance(bot.position_id, target.position_id)
        if not weapon or distance is None:
            return False
        damage_percent = (
            100
            if bot.shots_fired_this_activation == 0
            else weapon.followup_damage_percent
        )
        return (
            game._preview_attack(
                target,
                weapon,
                distance,
                damage_percent=damage_percent,
                ammunition_used=min(
                    weapon.ammunition_per_attack,
                    game._loaded_ammunition(bot, weapon),
                ),
            ).health_damage
            >= target.health
        )

    def _angle_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        weapon = game._equipped_weapon(bot)
        if not weapon or not weapon.requires_aim:
            return None
        targets = [
            enemy
            for enemy in visible_enemies
            if enemy.position_id
            not in {
                game.tactical_map.terrorist_spawn,
                game.tactical_map.counter_terrorist_spawn,
            }
            and game._can_hold_angle(bot, enemy.position_id, weapon)
            and game._is_hold_angle_enabled(
                bot,
                action_id=f"hold_angle_{enemy.position_id}",
            )
            is None
        ]
        if not targets:
            return None
        target = min(targets, key=lambda enemy: enemy.health)
        return f"hold_angle_{target.position_id}"

    def _proactive_angle_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Prepare one relevant lane without replacing objective movement."""

        weapon = game._equipped_weapon(bot)
        if (
            not weapon
            or weapon.hold_action_point_cost <= 0
            or bot.action_points < weapon.hold_action_point_cost
            or bot.shots_fired_this_activation
        ):
            return None
        plan = self.team_plans.get(SIDE_TERRORISTS)
        execute_site = self._active_execute_site(plan) if plan else ""
        assignment = self.assignment_for(bot.id)
        attacking_site_control = bool(
            bot.team_index == SIDE_TERRORISTS
            and (
                game.bomb_state == BOMB_CARRIED
                and execute_site
                and bot.position_id == execute_site
                or game.bomb_state == BOMB_PLANTED
                and bot.position_id == game.bomb_location_id
                and assignment is not None
                and assignment.role in {ROLE_OBJECTIVE, ROLE_SUPPORT}
            )
        )
        if attacking_site_control:
            action_id = f"hold_angle_{bot.position_id}"
            return (
                action_id
                if game._is_hold_angle_enabled(bot, action_id=action_id) is None
                else None
            )
        if not weapon.requires_aim and (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state == BOMB_PLANTED
            or bot.team_index == SIDE_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
        ):
            return None
        target_nodes = self.target_nodes(game, bot)
        source = game._node(bot.position_id)
        if not source:
            return None

        defensive_plan = self.team_plans.get(bot.team_index)
        fallback_commitment = (
            defensive_plan.fallback_commitments.get(bot.id)
            if defensive_plan and bot.team_index == SIDE_COUNTER_TERRORISTS
            else None
        )
        if (
            fallback_commitment
            and bot.position_id == fallback_commitment.hold_node_id
            and game._can_hold_angle(bot, fallback_commitment.watch_node_id, weapon)
        ):
            action_id = f"hold_angle_{fallback_commitment.watch_node_id}"
            if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                return action_id
        recent_threat = (
            defensive_plan.recent_threats.get(bot.id)
            if defensive_plan and bot.team_index == SIDE_COUNTER_TERRORISTS
            else None
        )
        if (
            recent_threat
            and recent_threat.target_node_id != bot.position_id
            and game._can_hold_angle(bot, recent_threat.target_node_id, weapon)
        ):
            action_id = f"hold_angle_{recent_threat.target_node_id}"
            if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                return action_id

        defensive_assignment = self.assignment_for(bot.id)
        if (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
            and defensive_assignment
            and defensive_assignment.role == ROLE_ANCHOR
            and bot.position_id in target_nodes
        ):
            for node_id in self._defensive_angle_nodes(
                game,
                bot,
                defensive_assignment.anchor_node_id,
                weapon,
            ):
                action_id = f"hold_angle_{node_id}"
                if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                    return action_id

        if (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
            and defensive_assignment
            and defensive_assignment.role == ROLE_ANCHOR
        ):
            # Finish deploying to the authored crossfire position. In
            # particular, an AWP at CT spawn must not waste a full activation
            # holding the bombsite itself when Long or Short is the real entry.
            return None

        site_anchor_defense = bool(
            not weapon.requires_aim
            and bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
        )
        if site_anchor_defense:
            if bot.position_id in target_nodes:
                return None
            assignment = self.assignment_for(bot.id)
            plan = self.team_plans.get(bot.team_index)
            next_node_id = self.shortest_path_step(game, bot, target_nodes)
            next_node = game._node(next_node_id) if next_node_id else None
            if (
                assignment
                and assignment.role == ROLE_ROTATOR
                and plan
                and len(
                    game._players_on_team(
                        SIDE_COUNTER_TERRORISTS,
                        alive_only=True,
                    )
                )
                <= self.profile.small_squad_full_rotation_size
                and next_node
                and next_node.bomb_site
                and any(
                    contact.node_id == next_node.id
                    or game.tactical_map.has_sightline(
                        next_node.id,
                        contact.node_id,
                    )
                    for contact in plan.contacts.values()
                )
            ):
                action_id = f"hold_angle_{next_node.id}"
                if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                    return action_id
            return None

        for node_id in target_nodes:
            if node_id == bot.position_id or not game.tactical_map.has_sightline(
                source.id,
                node_id,
            ):
                continue
            action_id = f"hold_angle_{node_id}"
            if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                return action_id
        if bot.position_id not in target_nodes:
            return None

        for node_id in self._predictive_angle_nodes(game, bot, source.id):
            action_id = f"hold_angle_{node_id}"
            if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                return action_id
        return None

    def _defensive_angle_nodes(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        site_id: str,
        weapon: WeaponProfile,
    ) -> tuple[str, ...]:
        """Rank visible site approaches by the weapon's useful range."""

        stable_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        candidates: list[tuple[tuple[int, int, int], str]] = []
        for node_id in self._site_ingress_nodes(game, site_id):
            distance = game._combat_distance(bot.position_id, node_id)
            route_distance = game._node_distance(node_id, site_id)
            if (
                distance is None
                or not 0 < distance <= weapon.max_range
                or route_distance is None
            ):
                continue
            candidates.append(
                (
                    (
                        distance,
                        -route_distance,
                        -stable_order.get(node_id, len(stable_order)),
                    ),
                    node_id,
                )
            )
        candidates.sort(reverse=True)
        ranked = [candidate[1] for candidate in candidates]
        if ranked:
            rotation = self._site_assignment_rotation(game, len(ranked))
            ranked = ranked[rotation:] + ranked[:rotation]

        spawn_nodes = {
            game.tactical_map.terrorist_spawn,
            game.tactical_map.counter_terrorist_spawn,
        }
        plan = self.team_plans.get(bot.team_index)
        heard_lanes: list[str] = []
        for cue in sorted(
            plan.acoustic_cues.values() if plan else (),
            key=lambda cue: (
                -cue.observed_tactical_round,
                -cue.observation_count,
                cue.node_id,
            ),
        ):
            for node_id in self._acoustic_prediction_nodes(game, plan, cue):
                if (
                    node_id not in spawn_nodes
                    and node_id != bot.position_id
                    and node_id not in heard_lanes
                    and game._can_hold_angle(bot, node_id, weapon)
                ):
                    heard_lanes.append(node_id)
        remembered_lanes: list[str] = []
        memory = self.squad_memories.get(bot.squad_index)
        site = game._node(site_id)
        defensive_nodes = {site_id, *(site.defender_position_ids if site else ())}
        for elimination in reversed(memory.eliminations if memory else ()):
            if (
                elimination.victim_side_index != bot.team_index
                or elimination.victim_node_id not in defensive_nodes
                or not 0
                <= game.round - elimination.round_marker[0]
                < self.profile.elimination_memory_rounds
                or elimination.source_node_id in remembered_lanes
                or elimination.source_node_id in spawn_nodes
                or not game._can_hold_angle(
                    bot,
                    elimination.source_node_id,
                    weapon,
                )
            ):
                continue
            remembered_lanes.append(elimination.source_node_id)
        return tuple(
            heard_lanes
            + [node_id for node_id in remembered_lanes if node_id not in heard_lanes]
            + [
                node_id
                for node_id in ranked
                if node_id not in heard_lanes and node_id not in remembered_lanes
            ]
        )

    def _predictive_angle_nodes(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        source_node_id: str,
    ) -> tuple[str, ...]:
        """Rank legal ingress areas using only public team observations."""

        opposing_team_index = next(
            index for index in SIDE_INDEXES if index != bot.team_index
        )
        opposing_spawn = game._spawn_for_team(opposing_team_index)
        spawn_nodes = {
            game.tactical_map.terrorist_spawn,
            game.tactical_map.counter_terrorist_spawn,
        }
        visible_nodes = set(game.tactical_map.visible_node_ids(source_node_id))
        candidates: list[str] = []
        plan = self.team_plans.get(bot.team_index)
        heard_nodes = sorted(
            plan.acoustic_cues.values() if plan else (),
            key=lambda cue: (
                -cue.observed_tactical_round,
                -cue.observation_count,
                cue.node_id,
            ),
        )
        for cue in heard_nodes:
            for node_id in self._acoustic_prediction_nodes(game, plan, cue):
                if (
                    node_id in visible_nodes
                    and node_id not in spawn_nodes
                    and node_id != source_node_id
                    and node_id not in candidates
                ):
                    candidates.append(node_id)
        contacts = sorted(
            plan.contacts.values() if plan else (),
            key=lambda contact: (-contact.observed_tactical_round, contact.player_id),
        )
        for contact in contacts:
            contact_node = game._node(contact.node_id)
            contact_distance = game._node_distance(
                contact.node_id,
                opposing_spawn,
            )
            if not contact_node or contact_distance is None:
                continue
            projected = sorted(
                enumerate(contact_node.adjacent),
                key=lambda entry: self._approach_sort_key(
                    game,
                    entry[1],
                    opposing_spawn,
                    entry[0],
                ),
            )
            for _order, node_id in projected:
                node_distance = game._node_distance(node_id, opposing_spawn)
                if (
                    node_id in visible_nodes
                    and node_id not in spawn_nodes
                    and node_id != source_node_id
                    and node_distance is not None
                    and node_distance > contact_distance
                    and node_id not in candidates
                ):
                    candidates.append(node_id)

        map_order = {
            node.id: index for index, node in enumerate(game.tactical_map.nodes)
        }
        remaining = sorted(
            (
                node_id
                for node_id in visible_nodes
                if node_id not in spawn_nodes
                and node_id != source_node_id
                and node_id not in candidates
            ),
            key=lambda node_id: self._approach_sort_key(
                game,
                node_id,
                opposing_spawn,
                map_order.get(node_id, len(map_order)),
            ),
        )
        candidates.extend(remaining)
        return tuple(candidates)

    def _should_maintain_prepared_angle(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> bool:
        """Keep a useful setup until contact or a changed objective breaks it."""

        if (
            not bot.held_angle_node_id
            or bot.held_angle_origin_id != bot.position_id
            or bot.action_points <= 0
            or bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state == BOMB_PLANTED
        ):
            return False
        weapon = game._equipped_weapon(bot)
        if not game._can_hold_angle(bot, bot.held_angle_node_id, weapon):
            return False
        target_nodes = self.target_nodes(game, bot)
        if (
            bot.team_index == SIDE_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
            and bot.position_id not in target_nodes
        ):
            # An attacking angle buys one reaction window; it must not replace
            # forward objective movement on every later activation.
            return False
        return bool(
            bot.held_angle_node_id in target_nodes or bot.position_id in target_nodes
        )

    def _flash_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        flash = next(
            (
                utility
                for utility in get_purchasable_utilities(bot.team_index)
                if utility.effect == UTILITY_EFFECT_FLASH
                and bot.utility_counts.get(utility.id, 0) > 0
            ),
            None,
        )
        if not flash:
            return None
        assignment = self.assignment_for(bot.id)
        plan = self.team_plans.get(SIDE_TERRORISTS)
        execute_site = self._active_execute_site(plan) if plan else ""
        if bot.action_points < flash.action_point_cost:
            return None
        execute_node = game._node(execute_site)
        defending_assigned_site = bool(
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and assignment
            and assignment.role == ROLE_ANCHOR
            and assignment.anchor_node_id == bot.position_id
        )
        attacking_execute_nodes = (
            {
                execute_site,
                *game.tactical_map.visible_node_ids(execute_site),
            }
            if bot.team_index == SIDE_TERRORISTS
            and assignment
            and assignment.role in {ROLE_OBJECTIVE, ROLE_ENTRY, ROLE_SUPPORT}
            and execute_node
            else set()
        )
        flash_nodes = {
            enemy.position_id
            for enemy in visible_enemies
            if (
                enemy.flash_penalty < flash.activation_penalty
                and (
                    defending_assigned_site
                    or enemy.position_id in attacking_execute_nodes
                    or sum(
                        other.position_id == enemy.position_id
                        and other.flash_penalty < flash.activation_penalty
                        for other in visible_enemies
                    )
                    >= self.profile.flash_group_target_count
                )
            )
            and not any(
                teammate.position_id == enemy.position_id
                for teammate in game._players_on_team(bot.team_index, alive_only=True)
            )
        }
        for node_id in sorted(flash_nodes):
            action_id = f"throw_{flash.id}_{node_id}"
            if game._is_throw_utility_enabled(bot, action_id=action_id) is None:
                return action_id
        return None

    def _damage_utility_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Use lethal utility for a finish, a group, or objective-area denial."""

        if not visible_enemies:
            return None
        allied_nodes = {
            teammate.position_id
            for teammate in game._players_on_team(bot.team_index, alive_only=True)
        }
        objective_nodes = set(game.tactical_map.bomb_site_ids())
        if game.bomb_state == BOMB_PLANTED:
            objective_nodes = {game.bomb_location_id}
        candidates: list[tuple[tuple[int, int, int, int], str]] = []
        for utility in get_purchasable_utilities(bot.team_index):
            if (
                utility.effect not in {UTILITY_EFFECT_EXPLOSIVE, UTILITY_EFFECT_FIRE}
                or bot.utility_counts.get(utility.id, 0) <= 0
                or bot.action_points < utility.action_point_cost
            ):
                continue
            for node_id in sorted({enemy.position_id for enemy in visible_enemies}):
                targets = [
                    enemy for enemy in visible_enemies if enemy.position_id == node_id
                ]
                if node_id in allied_nodes:
                    continue
                if utility.effect == UTILITY_EFFECT_FIRE and (
                    game._is_smoked(node_id) or game._is_burning(node_id)
                ):
                    continue
                action_id = f"throw_{utility.id}_{node_id}"
                if game._is_throw_utility_enabled(bot, action_id=action_id) is not None:
                    continue
                outcomes = [
                    game._preview_utility_damage(enemy, utility) for enemy in targets
                ]
                eliminations = sum(
                    outcome.health_damage >= enemy.health
                    for enemy, outcome in zip(targets, outcomes, strict=True)
                )
                grouped = len(targets) >= self.profile.damage_utility_group_target_count
                objective_denial = bool(
                    utility.effect == UTILITY_EFFECT_FIRE
                    and node_id in objective_nodes
                    and not (
                        bot.team_index == SIDE_COUNTER_TERRORISTS
                        and game.bomb_state == BOMB_PLANTED
                    )
                )
                if not eliminations and not grouped and not objective_denial:
                    continue
                candidates.append(
                    (
                        (
                            eliminations,
                            len(targets),
                            sum(outcome.health_damage for outcome in outcomes),
                            int(utility.effect == UTILITY_EFFECT_FIRE),
                        ),
                        action_id,
                    )
                )
        return max(candidates, default=((), None))[1]

    @staticmethod
    def _freshest_contact(plan: TeamPlan) -> EnemyContact | None:
        if not plan.contacts:
            return None
        return max(
            plan.contacts.values(),
            key=lambda contact: (
                contact.observed_tactical_round,
                -(contact.health + contact.armor),
                contact.player_id,
            ),
        )

    @staticmethod
    def _freshest_acoustic_cue(plan: TeamPlan) -> AcousticCue | None:
        if not plan.acoustic_cues:
            return None
        return max(
            plan.acoustic_cues.values(),
            key=lambda cue: (
                cue.observed_tactical_round,
                cue.observation_count,
                cue.cue_kind in HIGH_CONFIDENCE_ACOUSTIC_CUES,
                cue.node_id,
            ),
        )

    def _acoustic_prediction_nodes(
        self,
        game: BreachPointGame,
        plan: TeamPlan,
        cue: AcousticCue,
    ) -> tuple[str, ...]:
        """Project one audible movement edge into plausible next approach nodes.

        Footsteps reveal a direction to human listeners, not merely a named
        destination. Bots use the same origin-to-destination evidence to rank
        forward neighboring areas, while retaining the heard area itself as a
        fallback. Point sounds have no travel direction and therefore cannot
        support this inference.
        """

        predictions: list[str] = []
        destination = game._node(cue.node_id)
        origin = game._node(cue.origin_node_id)
        if (
            cue.cue_kind == ACOUSTIC_CUE_FOOTSTEPS
            and destination
            and origin
            and cue.origin_node_id in destination.adjacent
        ):
            enemy_side_index = next(
                side_index
                for side_index in SIDE_INDEXES
                if side_index != plan.team_index
            )
            enemy_spawn = game._spawn_for_team(enemy_side_index)
            current_progress = game._node_distance(cue.node_id, enemy_spawn)
            objective_node_ids = (
                game.tactical_map.bomb_site_ids()
                if enemy_side_index == SIDE_TERRORISTS
                else (game.bomb_location_id,)
                if game.bomb_state == BOMB_PLANTED and game.bomb_location_id
                else ()
            )
            stable_order = {
                node.id: index for index, node in enumerate(game.tactical_map.nodes)
            }
            ranked: list[tuple[tuple[int, int, int], str]] = []
            for node_id in destination.adjacent:
                if node_id == cue.origin_node_id:
                    continue
                progress = game._node_distance(node_id, enemy_spawn)
                if (
                    current_progress is not None
                    and progress is not None
                    and progress < current_progress
                ):
                    continue
                objective_distances = [
                    distance
                    for target_id in objective_node_ids
                    if (
                        distance := game._node_distance(node_id, target_id)
                    )
                    is not None
                ]
                ranked.append(
                    (
                        (
                            min(objective_distances)
                            if objective_distances
                            else len(game.tactical_map.nodes),
                            -(progress if progress is not None else -1),
                            stable_order.get(node_id, len(stable_order)),
                        ),
                        node_id,
                    )
                )
            predictions.extend(node_id for _rank, node_id in sorted(ranked))
        if cue.node_id not in predictions:
            predictions.append(cue.node_id)
        return tuple(predictions)

    def _acoustic_rotation_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        plan: TeamPlan,
    ) -> str:
        """Investigate heard pressure without pulling every anchor off its site."""

        cue = self._freshest_acoustic_cue(plan)
        assignment = plan.assignments.get(bot.id)
        if not cue or cue.node_id == bot.position_id or not assignment:
            return ""
        living_defenders = game._players_on_team(
            SIDE_COUNTER_TERRORISTS,
            alive_only=True,
        )
        site_distances = {
            site_id: game._node_distance(cue.node_id, site_id)
            for site_id in game.tactical_map.bomb_site_ids()
        }
        reachable_distances = [
            distance for distance in site_distances.values() if distance is not None
        ]
        if not reachable_distances:
            return ""
        closest_distance = min(reachable_distances)
        closest_sites = [
            site_id
            for site_id, distance in site_distances.items()
            if distance == closest_distance
        ]
        cue_is_confirmed_pressure = bool(
            cue.cue_kind in HIGH_CONFIDENCE_ACOUSTIC_CUES
            or cue.observation_count >= self.profile.repeated_acoustic_rotation_count
        )
        if assignment.role == ROLE_ROTATOR or len(living_defenders) == 1:
            covering_rotators = [
                teammate
                for teammate in game._turn_order_players_on_team(
                    SIDE_COUNTER_TERRORISTS,
                    alive_only=True,
                )
                if (
                    teammate_assignment := plan.assignments.get(teammate.id)
                ) is not None
                and teammate_assignment.role == ROLE_ROTATOR
                and teammate_assignment.anchor_node_id
                and game.tactical_map.has_sightline(
                    teammate_assignment.anchor_node_id,
                    cue.node_id,
                )
            ]
            if covering_rotators:
                response_target = min(
                    (
                        plan.assignments[teammate.id].anchor_node_id
                        for teammate in covering_rotators
                    ),
                    key=lambda node_id: (
                        game._node_distance(node_id, cue.node_id)
                        if game._node_distance(node_id, cue.node_id) is not None
                        else len(game.tactical_map.nodes),
                        node_id,
                    ),
                )
            elif len(closest_sites) == 1:
                site = game._node(closest_sites[0])
                response_target = (
                    site.defender_position_ids[0]
                    if site and site.defender_position_ids
                    else closest_sites[0]
                )
            else:
                response_target = cue.node_id
            if len(living_defenders) == 1:
                return response_target
            rotators = [
                teammate
                for teammate in game._turn_order_players_on_team(
                    SIDE_COUNTER_TERRORISTS,
                    alive_only=True,
                )
                if (teammate_assignment := plan.assignments.get(teammate.id))
                is not None
                and teammate_assignment.role == ROLE_ROTATOR
            ]
            responder = min(
                enumerate(rotators),
                key=lambda entry: (
                    game._node_distance(entry[1].position_id, response_target)
                    if game._node_distance(entry[1].position_id, response_target)
                    is not None
                    else len(game.tactical_map.nodes),
                    entry[0],
                ),
                default=(-1, None),
            )[1]
            return response_target if responder and responder.id == bot.id else ""
        if assignment.role != ROLE_ANCHOR or not assignment.anchor_node_id:
            return ""
        if (
            cue_is_confirmed_pressure
            and len(closest_sites) == 1
            and closest_sites[0] == assignment.anchor_node_id
        ):
            return self._defensive_anchor_position(game, bot, assignment)
        return ""

    @staticmethod
    def _alternate_site(game: BreachPointGame, attack_site_id: str) -> str:
        return next(
            (
                site_id
                for site_id in game.tactical_map.bomb_site_ids()
                if site_id != attack_site_id
            ),
            attack_site_id,
        )

    def _should_answer_carrier_contact(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        assignment: TacticalAssignment | None,
        contact: EnemyContact,
    ) -> bool:
        """Commit only the relevant anchor and rotators to a spotted bomb."""

        if not assignment or assignment.role == ROLE_ROTATOR:
            return True
        if assignment.role != ROLE_ANCHOR or not assignment.anchor_node_id:
            return False
        plan = self.team_plans.get(bot.team_index)
        living_attackers = game._players_on_team(SIDE_TERRORISTS, alive_only=True)
        if plan and (
            len(plan.contacts) >= len(living_attackers)
            or len(living_attackers) <= self.profile.small_squad_full_rotation_size
            and len(plan.contacts) >= self.profile.reinforcement_contact_count
        ):
            return True
        has_living_rotator = bool(
            plan
            and any(
                teammate_assignment.role == ROLE_ROTATOR
                and (teammate := game._breach_player_by_id(player_id)) is not None
                and not teammate.eliminated
                for player_id, teammate_assignment in plan.assignments.items()
            )
        )
        if not has_living_rotator:
            return True
        site_distances = {
            site_id: game._node_distance(contact.node_id, site_id)
            for site_id in game.tactical_map.bomb_site_ids()
        }
        reachable_distances = [
            distance for distance in site_distances.values() if distance is not None
        ]
        if not reachable_distances:
            return False
        closest_distance = min(reachable_distances)
        closest_sites = [
            site_id
            for site_id, distance in site_distances.items()
            if distance == closest_distance
        ]
        if len(closest_sites) > 1:
            return False
        return len(closest_sites) == 1 and assignment.anchor_node_id == closest_sites[0]

    def _reinforcement_contact(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        assignment: TacticalAssignment | None,
        plan: TeamPlan,
    ) -> EnemyContact | None:
        """Release only surplus anchors when another site reports a stack."""

        if (
            not assignment
            or assignment.role != ROLE_ANCHOR
            or not assignment.anchor_node_id
        ):
            return None
        if not self._should_rotate_to_unconfirmed_contacts(game, plan):
            return None
        home_anchors = [
            teammate
            for teammate in game._turn_order_players_on_team(
                SIDE_COUNTER_TERRORISTS,
                alive_only=True,
            )
            if (teammate_assignment := plan.assignments.get(teammate.id)) is not None
            and teammate_assignment.role == ROLE_ANCHOR
            and teammate_assignment.anchor_node_id == assignment.anchor_node_id
        ]
        if len(home_anchors) <= 1 or bot.id == home_anchors[0].id:
            return None

        contacts_by_site: dict[str, list[EnemyContact]] = {
            site_id: [] for site_id in game.tactical_map.bomb_site_ids()
        }
        for contact in plan.contacts.values():
            distances = {
                site_id: game._node_distance(contact.node_id, site_id)
                for site_id in contacts_by_site
            }
            reachable = [
                distance for distance in distances.values() if distance is not None
            ]
            if not reachable:
                continue
            closest_distance = min(reachable)
            closest_sites = [
                site_id
                for site_id, distance in distances.items()
                if distance == closest_distance
            ]
            if len(closest_sites) == 1:
                contacts_by_site[closest_sites[0]].append(contact)

        if contacts_by_site.get(assignment.anchor_node_id):
            return None
        threatened_sites = [
            (len(contacts), site_id, contacts)
            for site_id, contacts in contacts_by_site.items()
            if site_id != assignment.anchor_node_id
            and len(contacts) >= self.profile.reinforcement_contact_count
        ]
        if not threatened_sites:
            return None
        _count, _site_id, contacts = max(
            threatened_sites,
            key=lambda entry: (entry[0], entry[1]),
        )
        return max(
            contacts,
            key=lambda contact: (
                contact.observed_tactical_round,
                -(contact.health + contact.armor),
                contact.player_id,
            ),
        )

    @staticmethod
    def _should_rotate_to_unconfirmed_contacts(
        game: BreachPointGame,
        plan: TeamPlan,
    ) -> bool:
        """Rotate on a strict majority while the bomb remains unidentified."""

        living_attackers = game._players_on_team(
            SIDE_TERRORISTS,
            alive_only=True,
        )
        return bool(living_attackers and len(plan.contacts) * 2 > len(living_attackers))

    def _hazard_escape_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Leave known fire before attempting a static tactical action."""

        if (
            not game._is_burning(bot.position_id)
            or bot.action_points < game._movement_action_point_cost(bot)
        ):
            return None
        return self._safest_retreat_action(game, bot, away_from_node=bot.position_id)

    def _lost_postplant_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        shootable_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Save a premium gun, or trade enemy economy, when defusal is impossible."""

        if (
            bot.team_index != SIDE_COUNTER_TERRORISTS
            or game.bomb_state != BOMB_PLANTED
            or bot.position_id == game.bomb_location_id
        ):
            return None
        distance = game._node_distance(bot.position_id, game.bomb_location_id)
        if distance is None:
            return None
        route_cost = (
            game._movement_action_point_cost(bot)
            + max(0, distance - 1) * game.rules.move_cost
            + game._defuse_action_point_cost(bot)
        )
        available_capacity = bot.action_points + max(
            0,
            game.bomb_fuse_remaining - 1,
        ) * game.rules.action_points_per_activation
        if route_cost <= available_capacity:
            return None

        primary = game._primary_weapon(bot)
        worth_saving = bool(
            primary
            and primary.purchase_role
            in {PURCHASE_ROLE_STANDARD, PURCHASE_ROLE_PRECISION}
        )
        if worth_saving:
            return (
                self._safest_retreat_action(
                    game,
                    bot,
                    away_from_node=game.bomb_location_id,
                )
                or "end_turn"
            )
        if shootable_enemies:
            return f"shoot_{shootable_enemies[0].id}"
        plan = self.team_plans.get(bot.team_index)
        contact = self._freshest_contact(plan) if plan else None
        if contact and bot.action_points >= game._movement_action_point_cost(bot):
            next_node = self.shortest_path_step(game, bot, (contact.node_id,))
            action_id = f"move_{next_node}" if next_node else ""
            if action_id and game._is_move_enabled(bot, action_id=action_id) is None:
                return action_id
        return "end_turn"

    def _postplant_blast_escape_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Leave blast range only after the defuse window is certainly closed."""

        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_PLANTED
            or not self._bomb_defusal_is_mathematically_closed(game)
            or bot.action_points < game._movement_action_point_cost(bot)
        ):
            return None
        distance = game._node_distance(bot.position_id, game.bomb_location_id)
        maximum_blast_distance = len(
            game.rules.bomb_blast.damage_by_node_distance
        ) - 1
        if distance is None or distance > maximum_blast_distance:
            return None
        return self._blast_escape_action(
            game,
            bot,
        )

    def _blast_escape_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Increase bomb distance even when every exit crosses known fire."""

        source = game._node(bot.position_id)
        current_distance = game._node_distance(
            bot.position_id,
            game.bomb_location_id,
        )
        if not source or current_distance is None:
            return None
        plan = self.team_plans.get(bot.team_index)
        threat_nodes = {
            contact.node_id for contact in plan.contacts.values()
        } if plan else set()
        candidates: list[tuple[int, int, int, str]] = []
        for stable_order, node_id in enumerate(source.adjacent):
            action_id = f"move_{node_id}"
            if game._is_move_enabled(bot, action_id=action_id) is not None:
                continue
            distance = game._node_distance(node_id, game.bomb_location_id)
            if distance is None or distance <= current_distance:
                continue
            exposure = sum(
                threat_node == node_id
                or (
                    not game._is_smoked(threat_node)
                    and not game._is_smoked(node_id)
                    and game.tactical_map.has_sightline(threat_node, node_id)
                )
                for threat_node in threat_nodes
            )
            candidates.append((-distance, exposure, stable_order, action_id))
        return min(candidates)[3] if candidates else None

    @staticmethod
    def _bomb_defusal_is_mathematically_closed(game: BreachPointGame) -> bool:
        """Use only public turn state to prove that no CT can still defuse."""

        if game.defusing_player_id or game.bomb_fuse_remaining > 1:
            return False
        defenders = game._players_on_team(
            SIDE_COUNTER_TERRORISTS,
            alive_only=True,
        )
        return not defenders or all(
            defender.id in game.round_acted_player_ids for defender in defenders
        )

    def _supported_return_fire_target(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        shootable_enemies: list[BreachPointPlayer],
    ) -> BreachPointPlayer | None:
        """Take a coordinated trade shot before breaking a threatened lane."""

        if (
            bot.team_index != SIDE_COUNTER_TERRORISTS
            or game.bomb_state == BOMB_PLANTED
            or not shootable_enemies
            or bot.shots_fired_this_activation
            or bot.health * 100
            <= game.rules.max_health * self.profile.low_health_percent
        ):
            return None
        plan = self.team_plans.get(bot.team_index)
        if not plan or bot.id not in plan.recent_threats:
            return None
        supported = [
            enemy
            for enemy in shootable_enemies
            if any(
                teammate.id != bot.id and game._can_see(teammate, enemy)
                for teammate in game._players_on_team(
                    SIDE_COUNTER_TERRORISTS,
                    alive_only=True,
                )
            )
        ]
        return min(
            supported,
            key=lambda enemy: (enemy.health + enemy.armor, enemy.id),
            default=None,
        )

    def _safest_retreat_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        *,
        away_from_node: str,
    ) -> str | None:
        """Choose a legal neighboring area with less known exposure."""

        source = game._node(bot.position_id)
        if not source:
            return None
        plan = self.team_plans.get(bot.team_index)
        threat_nodes = {
            contact.node_id for contact in plan.contacts.values()
        } if plan else set()

        def exposure_count(node_id: str) -> int:
            if game._is_smoked(node_id):
                return 0
            return sum(
                threat_node == node_id
                or game.tactical_map.has_sightline(threat_node, node_id)
                for threat_node in threat_nodes
            )

        current_distance = game._node_distance(bot.position_id, away_from_node)
        current_exposure = exposure_count(bot.position_id)
        candidates: list[tuple[int, int, int, str]] = []
        for stable_order, node_id in enumerate(source.adjacent):
            if game._team_knows_area_effect(
                bot.team_index,
                UTILITY_EFFECT_FIRE,
                node_id,
            ):
                continue
            action_id = f"move_{node_id}"
            if game._is_move_enabled(bot, action_id=action_id) is not None:
                continue
            retreat_distance = game._node_distance(node_id, away_from_node)
            candidates.append(
                (
                    exposure_count(node_id),
                    -(retreat_distance if retreat_distance is not None else 0),
                    stable_order,
                    action_id,
                )
            )
        if not candidates:
            return None
        best = min(candidates)
        best_distance = -best[1]
        if (
            best[0] > current_exposure
            or best[0] == current_exposure
            and current_distance is not None
            and best_distance <= current_distance
        ):
            return None
        return best[3]

    def _defensive_fallback_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Break a losing pre-plant sightline after firing instead of dying in place."""

        plan = self.team_plans.get(bot.team_index)
        recent_threat = plan.recent_threats.get(bot.id) if plan else None
        if (
            not plan
            or
            bot.team_index != SIDE_COUNTER_TERRORISTS
            or game.bomb_state == BOMB_PLANTED
            or not (bot.shots_fired_this_activation or recent_threat)
            or bot.action_points < game._movement_action_point_cost(bot)
            or game._is_engaged(bot)
        ):
            return None
        weapon = game._equipped_weapon(bot)
        if (
            recent_threat
            and recent_threat.target_node_id == bot.position_id
            and weapon
            and weapon.requires_aim
        ):
            precision_retreat = self._safest_retreat_action(
                game,
                bot,
                away_from_node=recent_threat.source_node_id,
            )
            if precision_retreat:
                return self._remember_fallback(
                    plan,
                    bot,
                    precision_retreat,
                    game.tactical_round,
                )
        allies_at_node = sum(
            teammate.position_id == bot.position_id
            for teammate in game._players_on_team(
                SIDE_COUNTER_TERRORISTS,
                alive_only=True,
            )
        )
        low_health = (
            bot.health * 100 <= game.rules.max_health * self.profile.low_health_percent
        )
        if (
            not low_health
            and not (
                recent_threat and recent_threat.target_node_id == bot.position_id
            )
            and len(visible_enemies)
            < allies_at_node + self.profile.fallback_enemy_advantage
        ):
            return None
        source = game._node(bot.position_id)
        if not source:
            return None
        fallback_commitment = plan.fallback_commitments.get(bot.id)
        if (
            fallback_commitment
            and bot.position_id == fallback_commitment.hold_node_id
            and not bot.shots_fired_this_activation
            and not (
                recent_threat
                and recent_threat.target_node_id == bot.position_id
            )
        ):
            # Reaching a fallback point is a commitment to contest the lane
            # from cover. Low health and an older damage record must not make
            # the bot retreat back over the same edge on its next activation.
            return None

        def exposure_count(node_id: str) -> int:
            if game._is_smoked(node_id):
                return 0
            threat_node_ids = {
                enemy.position_id for enemy in visible_enemies
            }
            if recent_threat:
                threat_node_ids.add(recent_threat.source_node_id)
            return sum(
                threat_node_id == node_id
                or (
                    not game._is_smoked(threat_node_id)
                    and game.tactical_map.has_sightline(
                        threat_node_id,
                        node_id,
                    )
                )
                for threat_node_id in threat_node_ids
            )

        current_exposure = exposure_count(bot.position_id)
        candidates: list[tuple[int, int, int, str]] = []
        for stable_order, node_id in enumerate(source.adjacent):
            if any(enemy.position_id == node_id for enemy in visible_enemies):
                continue
            if (
                fallback_commitment
                and node_id == fallback_commitment.watch_node_id
            ):
                continue
            action_id = f"move_{node_id}"
            if game._is_move_enabled(bot, action_id=action_id) is not None:
                continue
            spawn_distance = game._node_distance(
                node_id,
                game.tactical_map.counter_terrorist_spawn,
            )
            candidates.append(
                (
                    exposure_count(node_id),
                    spawn_distance
                    if spawn_distance is not None
                    else len(game.tactical_map.nodes),
                    stable_order,
                    action_id,
                )
            )
        if not candidates:
            return None
        best = min(candidates)
        if best[0] >= current_exposure:
            return None
        return self._remember_fallback(
            plan,
            bot,
            best[3],
            game.tactical_round,
        )

    @staticmethod
    def _remember_fallback(
        plan: TeamPlan,
        bot: BreachPointPlayer,
        action_id: str,
        tactical_round: int,
    ) -> str:
        """Bind a retreat to one hold point so the bot cannot reverse course."""

        hold_node_id = action_id.removeprefix("move_")
        plan.fallback_commitments[bot.id] = FallbackCommitment(
            hold_node_id=hold_node_id,
            watch_node_id=bot.position_id,
            observed_tactical_round=tactical_round,
        )
        plan.routes.pop(bot.id, None)
        return action_id

    def _entry_breach_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Take a flashed site instead of surrendering the utility advantage."""

        assignment = self.assignment_for(bot.id)
        plan = self.team_plans.get(SIDE_TERRORISTS)
        execute_site = self._active_execute_site(plan) if plan else ""
        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or not assignment
            or assignment.role != ROLE_ENTRY
            or not plan
            or not execute_site
            or bot.position_id == execute_site
        ):
            return None
        site_defenders = [
            enemy for enemy in visible_enemies if enemy.position_id == execute_site
        ]
        if not site_defenders or any(
            enemy.flash_penalty <= 0 for enemy in site_defenders
        ):
            return None
        next_node = self.shortest_path_step(game, bot, (execute_site,))
        if next_node != execute_site:
            return None
        action_id = f"move_{next_node}"
        return (
            action_id
            if game._is_move_enabled(bot, action_id=action_id) is None
            else None
        )

    def _trade_entry_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> str | None:
        """Follow a committed entry player onto a contested attack site."""

        assignment = self.assignment_for(bot.id)
        plan = self.team_plans.get(SIDE_TERRORISTS)
        execute_site = self._active_execute_site(plan) if plan else ""
        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or not assignment
            or assignment.role != ROLE_SUPPORT
            or not plan
            or not execute_site
            or bot.position_id == execute_site
            or plan.entry_commit_node_id != execute_site
            or plan.entry_commit_tactical_round != game.tactical_round
            or (
                plan.attack_strategy_id == ATTACK_STRATEGY_FAKE
                and not plan.strategy_committed
            )
            or not any(
                contact.node_id == execute_site for contact in plan.contacts.values()
            )
        ):
            return None
        next_node = self.shortest_path_step(game, bot, (execute_site,))
        if next_node != execute_site:
            return None
        action_id = f"move_{next_node}"
        return (
            action_id
            if game._is_move_enabled(bot, action_id=action_id) is None
            else None
        )

    @staticmethod
    def _remember_entry_commitment(
        game: BreachPointGame,
        plan: TeamPlan,
    ) -> None:
        """Remember an entry reaching the called site for immediate trades."""

        execute_site = BreachPointBotCoordinator._active_execute_site(plan)
        if not execute_site:
            return
        entry = next(
            (
                game._breach_player_by_id(player_id)
                for player_id, assignment in plan.assignments.items()
                if assignment.role == ROLE_ENTRY
            ),
            None,
        )
        if entry and not entry.eliminated and entry.position_id == execute_site:
            plan.entry_commit_node_id = execute_site
            plan.entry_commit_tactical_round = game.tactical_round

    def _should_stage_bomb_carrier(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
    ) -> bool:
        """Keep the objective one step behind a living entry player."""

        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or game.bomb_carrier_id != bot.id
            or bot.action_points <= 0
            or bot.action_points == game.rules.action_points_per_activation
            or game.tactical_round >= game.preplant_tactical_round_limit
        ):
            return False
        plan = self.team_plans.get(SIDE_TERRORISTS)
        if not plan or not plan.attack_site_id:
            return False
        entry = next(
            (
                teammate
                for teammate in game._turn_order_players_on_team(
                    SIDE_TERRORISTS,
                    alive_only=True,
                )
                if teammate.id != bot.id
                and (assignment := plan.assignments.get(teammate.id)) is not None
                and assignment.role == ROLE_ENTRY
            ),
            None,
        )

        if not entry:
            return False
        team_order = game._turn_order_players_on_team(
            SIDE_TERRORISTS,
            alive_only=True,
        )
        order_by_id = {player.id: index for index, player in enumerate(team_order)}
        if (
            not entry.is_bot
            and entry.id not in game.round_acted_player_ids
            and order_by_id.get(bot.id, len(team_order))
            < order_by_id.get(entry.id, -1)
        ):
            return False
        carrier_distance = game._node_distance(bot.position_id, plan.attack_site_id)
        entry_distance = game._node_distance(entry.position_id, plan.attack_site_id)
        return bool(
            carrier_distance is not None
            and entry_distance is not None
            and entry_distance >= carrier_distance
        )

    @staticmethod
    def _terrorist_postplant_node(
        game: BreachPointGame,
        plan: TeamPlan,
        bot: BreachPointPlayer,
        bomb_site_id: str,
    ) -> str:
        """Spread specialist roles across likely CT approaches after planting."""

        assignment = plan.assignments.get(bot.id)
        if not assignment or assignment.role in {ROLE_OBJECTIVE, ROLE_SUPPORT}:
            return bomb_site_id
        site = game._node(bomb_site_id)
        if not site:
            return bomb_site_id
        approach_nodes = sorted(
            enumerate(site.adjacent),
            key=lambda entry: BreachPointBotCoordinator._approach_sort_key(
                game,
                entry[1],
                game.tactical_map.counter_terrorist_spawn,
                entry[0],
            ),
        )
        if not approach_nodes:
            return bomb_site_id
        approach_index = 1 if assignment.role == ROLE_LURKER else 0
        return approach_nodes[min(approach_index, len(approach_nodes) - 1)][1]

    @staticmethod
    def _approach_sort_key(
        game: BreachPointGame,
        node_id: str,
        opposing_spawn_id: str,
        stable_order: int,
    ) -> tuple[int, int]:
        distance = game._node_distance(node_id, opposing_spawn_id)
        return (
            distance if distance is not None else len(game.tactical_map.nodes) + 1,
            stable_order,
        )

    @staticmethod
    def _team_has_equipment(
        game: BreachPointGame,
        team_index: int,
        equipment: EquipmentProfile,
    ) -> bool:
        return any(
            teammate.equipment_counts.get(equipment.id, 0) > 0
            for teammate in game._players_on_team(team_index, alive_only=True)
        )
