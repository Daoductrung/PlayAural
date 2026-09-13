"""Stateful, information-safe team strategy for Breach Point bots."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .arsenal import (
    SIDE_COUNTER_TERRORISTS,
    SIDE_INDEXES,
    SIDE_TERRORISTS,
    UTILITY_EFFECT_FLASH,
    UTILITY_EFFECT_SMOKE,
    EquipmentProfile,
    WeaponProfile,
    get_purchasable_equipment,
    get_purchasable_utilities,
    get_purchasable_weapons,
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


@dataclass(frozen=True)
class BotTacticsProfile:
    """Tunable strategic thresholds shared by every bot team."""

    contact_memory_tactical_rounds: int
    entry_minimum_team_size: int
    lurker_minimum_team_size: int
    lurker_commit_tactical_round: int
    low_health_percent: int


STANDARD_BOT_TACTICS = BotTacticsProfile(
    contact_memory_tactical_rounds=2,
    entry_minimum_team_size=3,
    lurker_minimum_team_size=4,
    lurker_commit_tactical_round=4,
    low_health_percent=35,
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


@dataclass
class TeamPlan:
    """Bounded runtime-only observations and assignments for one side."""

    team_index: int
    round_marker: tuple[int, int, int, tuple[int, ...]]
    attack_site_id: str = ""
    objective_player_id: str = ""
    known_bomb_node_id: str = ""
    contacts: dict[str, EnemyContact] = field(default_factory=dict)
    assignments: dict[str, TacticalAssignment] = field(default_factory=dict)
    roster_signature: tuple[str, ...] = ()


def _validate_tactics_profile(profile: BotTacticsProfile) -> None:
    if profile.contact_memory_tactical_rounds < 0:
        raise ValueError("Bot contact memory cannot be negative")
    if profile.entry_minimum_team_size < 2:
        raise ValueError("An entry role requires at least two teammates")
    if profile.lurker_minimum_team_size < 2:
        raise ValueError("A lurker role requires at least two teammates")
    if profile.lurker_commit_tactical_round <= 0:
        raise ValueError("The lurker commit round must be positive")
    if not 0 < profile.low_health_percent <= 100:
        raise ValueError("The low-health percentage must be between 1 and 100")


_validate_tactics_profile(STANDARD_BOT_TACTICS)


class BreachPointBotCoordinator:
    """Coordinate bots through legal observations and stable round plans.

    This object is deliberately not a dataclass field on the game. Its memory is
    session-scoped, never serialized, and rebuilt empty after restoration.
    """

    def __init__(self, profile: BotTacticsProfile = STANDARD_BOT_TACTICS) -> None:
        self.profile = profile
        self.team_plans: dict[int, TeamPlan] = {}

    def clear(self) -> None:
        """Release all match-scoped observations and assignments."""

        self.team_plans.clear()

    def begin_combat_round(self, game: BreachPointGame) -> None:
        """Start fresh plans after spawn, side, and carrier selection."""

        self.clear()
        marker = self._round_marker(game)
        attack_site = self.planned_attack_site(game) or ""
        for team_index in SIDE_INDEXES:
            self.team_plans[team_index] = TeamPlan(
                team_index=team_index,
                round_marker=marker,
                attack_site_id=attack_site,
                objective_player_id=(
                    game.bomb_carrier_id if team_index == SIDE_TERRORISTS else ""
                ),
            )
        self._refresh_assignments(game)
        self.observe(game)

    def observe(self, game: BreachPointGame) -> None:
        """Refresh memory only from information the corresponding team can see."""

        self._ensure_current_round(game)
        for team_index in SIDE_INDEXES:
            plan = self.team_plans[team_index]
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
        self._refresh_assignments(game)

    def choose_action(
        self, game: BreachPointGame, bot: BreachPointPlayer
    ) -> str | None:
        """Return one legal action from the bot's current tactical context."""

        self.observe(game)
        if game.phase == PHASE_BUY:
            return self.buy_action(game, bot)
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

        angle_action = self._angle_action(game, bot, visible_enemies)
        if angle_action:
            return angle_action

        switch_action = self.weapon_switch_action(game, bot, visible_enemies)
        if switch_action:
            return switch_action

        flash_action = self._flash_action(game, bot, visible_enemies)
        if flash_action:
            return flash_action

        if objective_action:
            return objective_action

        proactive_angle_action = self._proactive_angle_action(game, bot)
        if proactive_angle_action:
            return proactive_angle_action

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
        """Rotate executes across every bombsite registered by the map."""

        site_ids = game.tactical_map.bomb_site_ids()
        if not site_ids:
            return None
        if game.overtime_period:
            half_rounds = game.rules.overtime_half_rounds
            period_round = max(1, game.overtime_round)
        else:
            half_rounds = game.match_format.rounds_per_half
            period_round = (max(1, game.round) - 1) % half_rounds + 1
        round_in_half = (period_round - 1) % half_rounds
        return site_ids[round_in_half % len(site_ids)]

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
            carrier_contact = next(
                (contact for contact in plan.contacts.values() if contact.carried_bomb),
                None,
            )
            if carrier_contact:
                return (carrier_contact.node_id,)
            assignment = plan.assignments.get(bot.id)
            freshest_contact = self._freshest_contact(plan)
            if freshest_contact and (
                assignment is None
                or assignment.role == ROLE_ROTATOR
                or assignment.anchor_node_id == freshest_contact.node_id
            ):
                return (freshest_contact.node_id,)
            if assignment and assignment.anchor_node_id:
                return (assignment.anchor_node_id,)
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
        if bot.id == game.bomb_carrier_id:
            return (attack_site,) if attack_site else ()
        assignment = plan.assignments.get(bot.id)
        if assignment and assignment.role == ROLE_LURKER:
            if game.tactical_round < self.profile.lurker_commit_tactical_round:
                alternate = self._alternate_site(game, attack_site)
                return (alternate,) if alternate else ()
            return (attack_site,) if attack_site else ()
        carrier = game._breach_player_by_id(game.bomb_carrier_id)
        if (
            assignment
            and assignment.role == ROLE_SUPPORT
            and carrier
            and carrier.position_id != bot.position_id
        ):
            return (carrier.position_id,)
        return (attack_site,) if attack_site else game.tactical_map.bomb_site_ids()

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
                enemy = game._living_enemy_at(bot, neighbor_id)
                if neighbor_id in target_set:
                    if (
                        enemy
                        and first_step is None
                        and not game.rules.allow_contested_entry
                    ):
                        return None
                    return first_step or neighbor_id
                if enemy and not game.rules.allow_contested_entry:
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
                return f"buy_equipment_{priority_equipment.id}"
            preferred_weapon = self._preferred_primary_weapon(game, bot)
            if preferred_weapon:
                return f"buy_weapon_{preferred_weapon.id}"
            if (
                bot.cash <= game.economy.starting_cash
                and bot.armor < game.economy.maximum_armor
                and bot.cash >= game.economy.armor_cost
            ):
                return "buy_armor"
            return "finish_buy"
        if (
            bot.armor < game.economy.maximum_armor
            and bot.cash >= game.economy.armor_cost
        ):
            return "buy_armor"
        for equipment in get_purchasable_equipment(bot.team_index):
            if (
                bot.equipment_counts.get(equipment.id, 0) < equipment.maximum_carry
                and bot.cash >= equipment.cost
                and not self._team_has_equipment(game, bot.team_index, equipment)
            ):
                return f"buy_equipment_{equipment.id}"
        for utility in get_purchasable_utilities(bot.team_index):
            if (
                bot.utility_counts.get(utility.id, 0) < utility.maximum_carry
                and bot.cash >= utility.cost
            ):
                return f"buy_utility_{utility.id}"
        return "finish_buy"

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
        if not squad_bots or squad_bots[0].id != bot.id:
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
        """Choose one affordable rifle while limiting precision weapons."""

        purchasable = get_purchasable_weapons(bot.team_index)
        precision_weapon = next(
            (
                weapon
                for weapon in purchasable
                if weapon.requires_aim and bot.cash >= weapon.cost
            ),
            None,
        )
        if (
            precision_weapon
            and self._is_designated_precision_user(game, bot)
            and not any(
                (weapon := game._primary_weapon(teammate)) and weapon.requires_aim
                for teammate in game._players_on_team(bot.team_index, alive_only=True)
                if teammate.id != bot.id
            )
        ):
            return precision_weapon
        return next(
            (
                weapon
                for weapon in purchasable
                if not weapon.requires_aim and bot.cash >= weapon.cost
            ),
            None,
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
                or bot.weapon_shots_fired_this_activation.get(weapon.id, 0)
                >= weapon.shots_per_activation
                or game._is_equip_weapon_enabled(bot, action_id=action_id) is not None
            ):
                continue
            if weapon.requires_aim:
                if bot.action_points >= weapon.aim_action_point_cost and any(
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

        if next_node not in target_nodes or game._is_smoked(next_node):
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
        staging_nodes = self._central_staging_nodes(game)
        extra_players = max(0, len(teammates) - len(site_ids))
        preferred_rotators = 2 if len(teammates) % 2 == 0 else 1
        rotator_count = min(extra_players, preferred_rotators, len(staging_nodes))
        for index, teammate in enumerate(teammates):
            if index < len(site_ids):
                role = ROLE_ANCHOR
                anchor = site_ids[index]
            elif index - len(site_ids) < rotator_count:
                role = ROLE_ROTATOR
                anchor = staging_nodes[index - len(site_ids)]
            else:
                role = ROLE_ANCHOR
                anchor_index = index - len(site_ids) - rotator_count
                anchor = site_ids[anchor_index % len(site_ids)] if site_ids else ""
            assignments[teammate.id] = TacticalAssignment(
                teammate.id,
                role,
                anchor,
            )
        return assignments

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
                not (
                    bot.team_index == SIDE_COUNTER_TERRORISTS
                    and enemy.id == game.bomb_carrier_id
                ),
                enemy.position_id != bot.position_id,
                enemy.health * 100
                > game.rules.max_health * self.profile.low_health_percent,
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
        distance = game._node_distance(bot.position_id, target.position_id)
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
            ).health_damage
            >= target.health
        )

    @staticmethod
    def _angle_action(
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
            if game._can_hold_angle(bot, enemy.position_id, weapon)
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
        """Prepare an AWP on a likely ingress lane after reaching an assignment."""

        weapon = game._equipped_weapon(bot)
        if not weapon or not weapon.requires_aim:
            return None
        target_nodes = self.target_nodes(game, bot)
        if bot.position_id not in target_nodes:
            return None
        source = game._node(bot.position_id)
        if not source:
            return None
        opposing_team_index = next(
            index for index in SIDE_INDEXES if index != bot.team_index
        )
        opposing_spawn = game._spawn_for_team(opposing_team_index)
        ordered_candidates = sorted(
            enumerate(source.sightlines),
            key=lambda entry: self._approach_sort_key(
                game,
                entry[1],
                opposing_spawn,
                entry[0],
            ),
        )
        for _order, node_id in ordered_candidates:
            action_id = f"hold_angle_{node_id}"
            if game._is_hold_angle_enabled(bot, action_id=action_id) is None:
                return action_id
        return None

    @staticmethod
    def _flash_action(
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
        flash_nodes = {
            enemy.position_id
            for enemy in visible_enemies
            if (
                enemy.held_angle_node_id
                or sum(
                    other.position_id == enemy.position_id for other in visible_enemies
                )
                > 1
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
