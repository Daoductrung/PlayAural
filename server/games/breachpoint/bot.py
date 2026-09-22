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


@dataclass(frozen=True)
class AttackStrategyProfile:
    """Roster requirements for one reusable attacking pattern."""

    id: str
    minimum_team_size: int


ATTACK_STRATEGIES = (
    AttackStrategyProfile(ATTACK_STRATEGY_DIRECT, 2),
    AttackStrategyProfile(ATTACK_STRATEGY_SPLIT, 2),
    AttackStrategyProfile(ATTACK_STRATEGY_FAKE, 5),
)


@dataclass(frozen=True)
class BotTacticsProfile:
    """Tunable strategic thresholds shared by every bot team."""

    contact_memory_tactical_rounds: int
    entry_minimum_team_size: int
    lurker_minimum_team_size: int
    lurker_commit_tactical_round: int
    pistol_lurker_commit_tactical_round: int
    low_health_percent: int
    attack_history_rounds: int
    successful_site_repeat_limit: int
    successful_site_repeat_percent: int
    successful_strategy_repeat_percent: int
    split_commit_tactical_round: int
    fake_commit_tactical_round: int
    fake_contact_commit_count: int
    close_range_primary_team_divisor: int
    pistol_flash_team_divisor: int
    flash_group_target_count: int
    damage_utility_group_target_count: int
    route_smoke_contact_count: int
    reinforcement_contact_count: int
    small_squad_full_rotation_size: int
    fallback_enemy_advantage: int
    maximum_duplicate_utility: int


STANDARD_BOT_TACTICS = BotTacticsProfile(
    contact_memory_tactical_rounds=2,
    entry_minimum_team_size=2,
    lurker_minimum_team_size=3,
    lurker_commit_tactical_round=4,
    pistol_lurker_commit_tactical_round=2,
    low_health_percent=35,
    attack_history_rounds=4,
    successful_site_repeat_limit=2,
    successful_site_repeat_percent=60,
    successful_strategy_repeat_percent=40,
    split_commit_tactical_round=4,
    fake_commit_tactical_round=3,
    fake_contact_commit_count=2,
    close_range_primary_team_divisor=2,
    pistol_flash_team_divisor=2,
    flash_group_target_count=2,
    damage_utility_group_target_count=2,
    route_smoke_contact_count=2,
    reinforcement_contact_count=2,
    small_squad_full_rotation_size=3,
    fallback_enemy_advantage=1,
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


@dataclass
class SquadMemory:
    """Bounded match-level strategy retained while one game instance lives."""

    attack_rounds: list[AttackRoundMemory] = field(default_factory=list)


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
    assignments: dict[str, TacticalAssignment] = field(default_factory=dict)
    roster_signature: tuple[str, ...] = ()
    completed_strategy_route_player_ids: set[str] = field(default_factory=set)


def _validate_tactics_profile(profile: BotTacticsProfile) -> None:
    if profile.contact_memory_tactical_rounds < 0:
        raise ValueError("Bot contact memory cannot be negative")
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
    if profile.successful_site_repeat_limit <= 0:
        raise ValueError("Bot site repetition must allow at least one attack")
    if not 0 <= profile.successful_site_repeat_percent <= 100:
        raise ValueError("Bot site repetition percentage must be between 0 and 100")
    if not 0 <= profile.successful_strategy_repeat_percent <= 100:
        raise ValueError("Bot strategy repetition percentage must be between 0 and 100")
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
    if profile.reinforcement_contact_count < 2:
        raise ValueError("Reinforcement tactics require at least two contacts")
    if profile.small_squad_full_rotation_size < 2:
        raise ValueError("Full-rotation tactics require at least two teammates")
    if profile.fallback_enemy_advantage <= 0:
        raise ValueError("Fallback requires a positive enemy advantage")
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

    def observe(self, game: BreachPointGame) -> None:
        """Refresh memory only from information the corresponding team can see."""

        self._ensure_current_round(game)
        for team_index in SIDE_INDEXES:
            plan = self.team_plans[team_index]
            if team_index == SIDE_TERRORISTS:
                self._remember_entry_commitment(game, plan)
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

            self._update_bomb_memory(game, plan)
            if team_index == SIDE_TERRORISTS:
                self._remember_strategy_route_progress(game, plan)
                self._update_attack_strategy(game, plan)
        self._refresh_assignments(game)

    def choose_action(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> str | None:
        """Return one legal action from the bot's current tactical context."""

        self.observe(game)
        if game.pending_weapon_donation:
            return self.weapon_donation_response_action(game, bot)
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
        objective_action = self._objective_action(game, bot)
        objective_is_urgent = self._objective_is_urgent(
            game,
            objective_action,
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

        if objective_is_urgent:
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

        fallback_action = self._defensive_fallback_action(
            game,
            bot,
            visible_enemies,
        )
        if fallback_action:
            return fallback_action

        flash_action = self._flash_action(game, bot, visible_enemies)
        if flash_action and not (
            bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state == BOMB_PLANTED
        ):
            return flash_action

        if objective_action and (
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

        if objective_action:
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
            or game.tactical_round < game.rules.preplant_tactical_round_limit
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
        if (
            last_attack.won
            and consecutive_site_attacks < self.profile.successful_site_repeat_limit
            and self._rng.randrange(100) < self.profile.successful_site_repeat_percent
        ):
            return last_attack.site_id
        last_index = site_ids.index(last_attack.site_id)
        return site_ids[(last_index + 1) % len(site_ids)]

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
        if (
            last_attack.won
            and self._rng.randrange(100)
            < self.profile.successful_strategy_repeat_percent
        ):
            return last_attack.strategy_id
        last_index = eligible_ids.index(last_attack.strategy_id)
        return eligible_ids[(last_index + 1) % len(eligible_ids)]

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
            if (
                assignment
                and assignment.role == ROLE_ROTATOR
                and assignment.anchor_node_id
                and bot.position_id == game.tactical_map.counter_terrorist_spawn
            ):
                return (assignment.anchor_node_id,)
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
                return (carrier.position_id,)
        return (attack_site,) if attack_site else game.tactical_map.bomb_site_ids()

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
        """Return a deterministic first edge toward any valid destination."""

        target_set = {node_id for node_id in target_nodes if game._node(node_id)}
        if not target_set or bot.position_id in target_set:
            return None
        for allow_known_fire in (False, True):
            queue: deque[tuple[str, str | None]] = deque([(bot.position_id, None)])
            visited = {bot.position_id}
            while queue:
                node_id, first_step = queue.popleft()
                node = game._node(node_id)
                if not node:
                    continue
                for neighbor_id in node.adjacent:
                    if neighbor_id in visited:
                        continue
                    if not allow_known_fire and game._team_knows_area_effect(
                        bot.team_index,
                        UTILITY_EFFECT_FIRE,
                        neighbor_id,
                    ):
                        continue
                    enemy = game._living_enemy_at(bot, neighbor_id)
                    known_enemy = bool(
                        enemy and game._team_can_see_player(bot.team_index, enemy)
                    )
                    if neighbor_id in target_set:
                        if (
                            known_enemy
                            and first_step is None
                            and not game.rules.allow_contested_entry
                        ):
                            return None
                        return first_step or neighbor_id
                    if known_enemy and not game.rules.allow_contested_entry:
                        continue
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, first_step or neighbor_id))
        return None

    def buy_action(self, game: BreachPointGame, bot: BreachPointPlayer) -> str | None:
        """Choose a legal deterministic buy within the squad's shared plan."""

        self._ensure_current_round(game)
        if game._buy_turn_error(bot) is not None:
            return None
        primary = game._primary_weapon(bot)
        if not primary:
            priority_equipment = self.team_priority_equipment(game, bot)
            if priority_equipment:
                action_id = f"buy_equipment_{priority_equipment.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            pistol_utility = self._pistol_round_utility(game, bot)
            if pistol_utility:
                action_id = f"buy_utility_{pistol_utility.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            preferred_weapon = self._preferred_primary_weapon(game, bot)
            if preferred_weapon:
                action_id = f"buy_weapon_{preferred_weapon.id}"
                if self._legal_buy_action(game, bot, action_id):
                    return action_id
            if (
                bot.cash <= game.economy.starting_cash
                and bot.armor < game.economy.maximum_armor
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
        for equipment in get_purchasable_equipment(bot.team_index):
            if (
                bot.equipment_counts.get(equipment.id, 0) < equipment.maximum_carry
                and bot.cash >= equipment.cost
                and not self._team_has_equipment(game, bot.team_index, equipment)
            ):
                action_id = f"buy_equipment_{equipment.id}"
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
        """Fund one objective-equipment carrier without duplicating squad gear."""

        if bot.cash != game.economy.starting_cash:
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
        """Assign one upgraded backup after the squad bot owns a primary."""

        if game._primary_weapon(bot) is None:
            return None
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
        eligible_bots = [
            teammate
            for teammate in teammates
            if teammate.is_bot
            and self.team_priority_equipment(game, teammate) is None
            and self._pistol_round_utility(game, teammate) is None
        ]
        if not eligible_bots or eligible_bots[0].id != bot.id:
            return None
        return max(
            purchasable,
            key=lambda weapon: (
                weapon.max_range,
                min(weapon.damage_by_range),
                -weapon.armor_reduction_percent,
                -weapon.cost,
            ),
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
        total_cost = (
            route_cost
            + game._defuse_action_point_cost(bot)
            + (contemplated_action_cost if lethal_target is not None else 0)
        )
        future_capacity = max(0, game.bomb_fuse_remaining - 1) * (
            game.rules.action_points_per_activation
        )
        capacity_after_optional_action = (
            bot.action_points + future_capacity - contemplated_action_cost
        )
        if lethal_target is not None:
            if total_cost <= bot.action_points + future_capacity:
                return None
        elif total_cost <= capacity_after_optional_action:
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
        """Smoke a publicly observed crossfire before the squad enters it."""

        assignment = self.assignment_for(bot.id)
        plan = self.team_plans.get(SIDE_TERRORISTS)
        if (
            bot.team_index != SIDE_TERRORISTS
            or game.bomb_state != BOMB_CARRIED
            or not assignment
            or assignment.role not in {ROLE_OBJECTIVE, ROLE_SUPPORT}
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
        execute_site = self._active_execute_site(plan)
        if (
            not next_node
            or not execute_site
            or next_node != execute_site
            or game._node_distance(bot.position_id, execute_site) != 1
        ):
            return None
        exposed_contacts = [
            contact
            for contact in plan.contacts.values()
            if not game._is_smoked(contact.node_id)
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
        if len(exposed_contacts) < self.profile.route_smoke_contact_count:
            return None
        contact_counts: dict[str, int] = {}
        for contact in exposed_contacts:
            contact_counts[contact.node_id] = (
                contact_counts.get(contact.node_id, 0) + 1
            )
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
            if game._is_smoked(node_id):
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
        if anchor_index == 0:
            return site_id

        site_spawn_distance = game._node_distance(
            site_id,
            game.tactical_map.counter_terrorist_spawn,
        )
        candidates: list[tuple[int, int, str]] = []
        for stable_order, node_id in enumerate(site.adjacent):
            spawn_distance = game._node_distance(
                node_id,
                game.tactical_map.counter_terrorist_spawn,
            )
            if spawn_distance is None or (
                site_spawn_distance is not None
                and spawn_distance >= site_spawn_distance
            ):
                continue
            candidates.append((spawn_distance, stable_order, node_id))
        if not candidates:
            return site_id
        ordered_positions = [candidate[2] for candidate in sorted(candidates)]
        return ordered_positions[min(anchor_index - 1, len(ordered_positions) - 1)]

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
            and game.tactical_round >= game.rules.preplant_tactical_round_limit
        )

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

        site_anchor_defense = bool(
            not weapon.requires_aim
            and bot.team_index == SIDE_COUNTER_TERRORISTS
            and game.bomb_state != BOMB_PLANTED
        )
        if site_anchor_defense:
            if bot.position_id in target_nodes:
                assignment = self.assignment_for(bot.id)
                watched_node_id = (
                    assignment.anchor_node_id
                    if assignment
                    and assignment.role == ROLE_ANCHOR
                    and assignment.anchor_node_id != bot.position_id
                    and game.tactical_map.has_sightline(
                        source.id,
                        assignment.anchor_node_id,
                    )
                    else bot.position_id
                )
                action_id = f"hold_angle_{watched_node_id}"
                return (
                    action_id
                    if game._is_hold_angle_enabled(bot, action_id=action_id) is None
                    else None
                )
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

    def _defensive_fallback_action(
        self,
        game: BreachPointGame,
        bot: BreachPointPlayer,
        visible_enemies: list[BreachPointPlayer],
    ) -> str | None:
        """Break a losing pre-plant sightline after firing instead of dying in place."""

        if (
            bot.team_index != SIDE_COUNTER_TERRORISTS
            or game.bomb_state == BOMB_PLANTED
            or bot.shots_fired_this_activation <= 0
            or bot.action_points < game.rules.move_cost
            or not visible_enemies
            or game._is_engaged(bot)
        ):
            return None
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
            and len(visible_enemies)
            < allies_at_node + self.profile.fallback_enemy_advantage
        ):
            return None
        source = game._node(bot.position_id)
        if not source:
            return None

        def exposure_count(node_id: str) -> int:
            if game._is_smoked(node_id):
                return 0
            return sum(
                enemy.position_id == node_id
                or (
                    not game._is_smoked(enemy.position_id)
                    and game.tactical_map.has_sightline(
                        enemy.position_id,
                        node_id,
                    )
                )
                for enemy in visible_enemies
            )

        current_exposure = exposure_count(bot.position_id)
        candidates: list[tuple[int, int, int, str]] = []
        for stable_order, node_id in enumerate(source.adjacent):
            if any(enemy.position_id == node_id for enemy in visible_enemies):
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
        return best[3] if best[0] < current_exposure else None

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
            or game.tactical_round >= game.rules.preplant_tactical_round_limit
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
