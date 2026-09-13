"""Data-driven economy and weapon profiles for Breach Point."""

from __future__ import annotations

from dataclasses import dataclass

SIDE_TERRORISTS = 0
SIDE_COUNTER_TERRORISTS = 1
SIDE_INDEXES = (SIDE_TERRORISTS, SIDE_COUNTER_TERRORISTS)

WEAPON_SLOT_SIDEARM = "sidearm"
WEAPON_SLOT_PRIMARY = "primary"
WEAPON_SLOTS = frozenset({WEAPON_SLOT_SIDEARM, WEAPON_SLOT_PRIMARY})


@dataclass(frozen=True)
class WeaponProfile:
    """One deterministic weapon available to a tactical rules profile."""

    id: str
    name_key: str
    slot: str
    allowed_sides: tuple[int, ...]
    cost: int
    max_range: int
    rounds_per_attack: int
    hits_by_range: tuple[int, ...]
    damage_by_range: tuple[int, ...]
    minimum_hits_after_evasion: int
    evasion_points_per_hit: int
    evasion_damage_reduction_per_point: int
    armor_reduction_percent: int
    action_point_cost: int
    shots_per_activation: int
    followup_damage_percent: int
    can_repeat_target: bool
    requires_aim: bool
    aim_action_point_cost: int
    kill_reward: int

    def hits_at_range(self, distance: int) -> int:
        """Return deterministic on-target rounds at a validated graph distance."""

        return self.hits_by_range[distance]

    def damage_at_range(self, distance: int) -> int:
        """Return damage before evasion and armor at a validated graph distance."""

        return self.damage_by_range[distance]


UTILITY_EFFECT_SMOKE = "smoke"
UTILITY_EFFECT_FLASH = "flash"
UTILITY_EFFECTS = frozenset({UTILITY_EFFECT_SMOKE, UTILITY_EFFECT_FLASH})


@dataclass(frozen=True)
class UtilityProfile:
    """One purchasable tactical item and its deterministic effect."""

    id: str
    name_key: str
    allowed_sides: tuple[int, ...]
    cost: int
    maximum_carry: int
    action_point_cost: int
    throw_range: int
    effect: str
    duration_tactical_rounds: int = 0
    activation_penalty: int = 0
    affects_thrower: bool = True


@dataclass(frozen=True)
class EquipmentProfile:
    """Persistent purchasable gear with data-driven action-cost modifiers."""

    id: str
    name_key: str
    allowed_sides: tuple[int, ...]
    cost: int
    maximum_carry: int
    action_point_modifiers: tuple[tuple[str, int], ...] = ()

    def action_point_modifier(self, action_id: str) -> int:
        """Return this equipment's modifier for one stable action id."""

        return sum(
            modifier
            for target_action_id, modifier in self.action_point_modifiers
            if target_action_id == action_id
        )


@dataclass(frozen=True)
class EconomyProfile:
    """Cash, armor, and round-income values for one competitive ruleset."""

    starting_cash: int
    overtime_cash: int
    maximum_cash: int
    armor_name_key: str
    armor_cost: int
    maximum_armor: int
    round_win_rewards: tuple[tuple[str, int], ...]
    loss_rewards: tuple[int, ...]
    initial_loss_count: int
    plant_team_bonus: int
    planter_reward: int
    defuser_reward: int

    @property
    def maximum_loss_count(self) -> int:
        """Return the highest loss-counter index represented by the profile."""

        return max(0, len(self.loss_rewards) - 1)

    def win_reward(self, reason: str) -> int:
        """Return the configured round-win reward for one outcome."""

        for configured_reason, reward in self.round_win_rewards:
            if configured_reason == reason:
                return reward
        raise KeyError(f"No round-win reward is configured for {reason}")

    def loss_reward(self, loss_count: int) -> int:
        """Return the bounded reward at the squad's current loss counter."""

        if not self.loss_rewards:
            return 0
        index = max(0, min(self.maximum_loss_count, loss_count))
        return self.loss_rewards[index]


GLOCK = WeaponProfile(
    id="glock",
    name_key="breachpoint-weapon-glock",
    slot=WEAPON_SLOT_SIDEARM,
    allowed_sides=(SIDE_TERRORISTS,),
    cost=0,
    max_range=1,
    rounds_per_attack=1,
    hits_by_range=(1, 1),
    damage_by_range=(38, 30),
    minimum_hits_after_evasion=0,
    evasion_points_per_hit=2,
    evasion_damage_reduction_per_point=8,
    armor_reduction_percent=40,
    action_point_cost=1,
    shots_per_activation=2,
    followup_damage_percent=75,
    can_repeat_target=True,
    requires_aim=False,
    aim_action_point_cost=0,
    kill_reward=300,
)

USP_S = WeaponProfile(
    id="usp_s",
    name_key="breachpoint-weapon-usp-s",
    slot=WEAPON_SLOT_SIDEARM,
    allowed_sides=(SIDE_COUNTER_TERRORISTS,),
    cost=0,
    max_range=1,
    rounds_per_attack=1,
    hits_by_range=(1, 1),
    damage_by_range=(36, 32),
    minimum_hits_after_evasion=0,
    evasion_points_per_hit=2,
    evasion_damage_reduction_per_point=8,
    armor_reduction_percent=40,
    action_point_cost=1,
    shots_per_activation=2,
    followup_damage_percent=75,
    can_repeat_target=True,
    requires_aim=False,
    aim_action_point_cost=0,
    kill_reward=300,
)

AK47 = WeaponProfile(
    id="ak47",
    name_key="breachpoint-weapon-ak47",
    slot=WEAPON_SLOT_PRIMARY,
    allowed_sides=(SIDE_TERRORISTS,),
    cost=2700,
    max_range=2,
    rounds_per_attack=12,
    hits_by_range=(4, 3, 2),
    damage_by_range=(92, 69, 46),
    minimum_hits_after_evasion=1,
    evasion_points_per_hit=1,
    evasion_damage_reduction_per_point=8,
    armor_reduction_percent=15,
    action_point_cost=1,
    shots_per_activation=1,
    followup_damage_percent=65,
    can_repeat_target=True,
    requires_aim=False,
    aim_action_point_cost=0,
    kill_reward=300,
)

M4 = WeaponProfile(
    id="m4",
    name_key="breachpoint-weapon-m4",
    slot=WEAPON_SLOT_PRIMARY,
    allowed_sides=(SIDE_COUNTER_TERRORISTS,),
    cost=2900,
    max_range=2,
    rounds_per_attack=12,
    hits_by_range=(4, 3, 2),
    damage_by_range=(72, 54, 36),
    minimum_hits_after_evasion=1,
    evasion_points_per_hit=1,
    evasion_damage_reduction_per_point=6,
    armor_reduction_percent=25,
    action_point_cost=1,
    shots_per_activation=2,
    followup_damage_percent=75,
    can_repeat_target=False,
    requires_aim=False,
    aim_action_point_cost=0,
    kill_reward=300,
)

AWP = WeaponProfile(
    id="awp",
    name_key="breachpoint-weapon-awp",
    slot=WEAPON_SLOT_PRIMARY,
    allowed_sides=SIDE_INDEXES,
    cost=4750,
    max_range=3,
    rounds_per_attack=1,
    hits_by_range=(1, 1, 1, 1),
    damage_by_range=(125, 120, 115, 110),
    minimum_hits_after_evasion=1,
    evasion_points_per_hit=1,
    evasion_damage_reduction_per_point=10,
    armor_reduction_percent=5,
    action_point_cost=2,
    shots_per_activation=1,
    followup_damage_percent=100,
    can_repeat_target=True,
    requires_aim=True,
    aim_action_point_cost=1,
    kill_reward=100,
)

SMOKE_GRENADE = UtilityProfile(
    id="smoke",
    name_key="breachpoint-utility-smoke",
    allowed_sides=SIDE_INDEXES,
    cost=300,
    maximum_carry=1,
    action_point_cost=1,
    throw_range=1,
    effect=UTILITY_EFFECT_SMOKE,
    duration_tactical_rounds=2,
)

FLASHBANG = UtilityProfile(
    id="flashbang",
    name_key="breachpoint-utility-flashbang",
    allowed_sides=SIDE_INDEXES,
    cost=200,
    maximum_carry=2,
    action_point_cost=1,
    throw_range=1,
    effect=UTILITY_EFFECT_FLASH,
    activation_penalty=1,
    affects_thrower=False,
)


DEFUSE_KIT = EquipmentProfile(
    id="defuse_kit",
    name_key="breachpoint-equipment-defuse-kit",
    allowed_sides=(SIDE_COUNTER_TERRORISTS,),
    cost=400,
    maximum_carry=1,
    action_point_modifiers=(("defuse", -1),),
)


WEAPONS = {
    weapon.id: weapon
    for weapon in (
        GLOCK,
        USP_S,
        AK47,
        M4,
        AWP,
    )
}

UTILITIES = {utility.id: utility for utility in (SMOKE_GRENADE, FLASHBANG)}
EQUIPMENT = {equipment.id: equipment for equipment in (DEFUSE_KIT,)}

DEFAULT_SIDEARMS = {
    SIDE_TERRORISTS: GLOCK.id,
    SIDE_COUNTER_TERRORISTS: USP_S.id,
}

STANDARD_ECONOMY = EconomyProfile(
    starting_cash=800,
    overtime_cash=10_000,
    maximum_cash=16_000,
    armor_name_key="breachpoint-armor-kevlar",
    armor_cost=650,
    maximum_armor=100,
    round_win_rewards=(
        ("elimination", 3_250),
        ("defused", 3_500),
        ("detonated", 3_500),
        ("time", 3_250),
    ),
    loss_rewards=(1_400, 1_900, 2_400, 2_900, 3_400),
    initial_loss_count=1,
    plant_team_bonus=600,
    planter_reward=300,
    defuser_reward=300,
)


def _validate_weapon(weapon: WeaponProfile) -> None:
    """Reject an incomplete weapon profile during module initialization."""

    if not weapon.id or not weapon.name_key:
        raise ValueError("Weapons require stable ids and localized names")
    if weapon.slot not in WEAPON_SLOTS:
        raise ValueError(f"Weapon {weapon.id} has an invalid slot")
    if not weapon.allowed_sides or any(
        side not in SIDE_INDEXES for side in weapon.allowed_sides
    ):
        raise ValueError(f"Weapon {weapon.id} has invalid side availability")
    range_value_count = weapon.max_range + 1
    if (
        weapon.cost < 0
        or weapon.max_range < 0
        or len(weapon.hits_by_range) != range_value_count
        or len(weapon.damage_by_range) != range_value_count
        or weapon.minimum_hits_after_evasion < 0
        or weapon.evasion_damage_reduction_per_point < 0
        or not 0 <= weapon.armor_reduction_percent <= 100
        or not 1 <= weapon.followup_damage_percent <= 100
        or any(
            value <= 0
            for value in (
                weapon.rounds_per_attack,
                weapon.evasion_points_per_hit,
                weapon.action_point_cost,
                weapon.shots_per_activation,
                weapon.kill_reward,
            )
        )
        or any(value <= 0 for value in weapon.hits_by_range)
        or any(value <= 0 for value in weapon.damage_by_range)
    ):
        raise ValueError(f"Weapon {weapon.id} has invalid combat values")
    if any(hits > weapon.rounds_per_attack for hits in weapon.hits_by_range):
        raise ValueError(f"Weapon {weapon.id} hits more rounds than it fires")
    if weapon.minimum_hits_after_evasion > min(weapon.hits_by_range):
        raise ValueError(f"Weapon {weapon.id} has an invalid evasion hit floor")
    if tuple(sorted(weapon.hits_by_range, reverse=True)) != weapon.hits_by_range:
        raise ValueError(f"Weapon {weapon.id} hit profile must not rise with range")
    if tuple(sorted(weapon.damage_by_range, reverse=True)) != weapon.damage_by_range:
        raise ValueError(f"Weapon {weapon.id} damage must not rise with range")
    if weapon.requires_aim != (weapon.aim_action_point_cost > 0):
        raise ValueError(f"Weapon {weapon.id} has inconsistent aim requirements")


def _validate_utility(utility: UtilityProfile) -> None:
    """Reject an incomplete utility profile during module initialization."""

    if not utility.id or not utility.name_key:
        raise ValueError("Utility items require stable ids and localized names")
    if not utility.allowed_sides or any(
        side not in SIDE_INDEXES for side in utility.allowed_sides
    ):
        raise ValueError(f"Utility {utility.id} has invalid side availability")
    if utility.effect not in UTILITY_EFFECTS:
        raise ValueError(f"Utility {utility.id} has an unsupported effect")
    if any(
        value <= 0
        for value in (
            utility.cost,
            utility.maximum_carry,
            utility.action_point_cost,
            utility.throw_range,
        )
    ):
        raise ValueError(f"Utility {utility.id} has invalid action values")
    if utility.effect == UTILITY_EFFECT_SMOKE:
        if utility.duration_tactical_rounds <= 0 or utility.activation_penalty != 0:
            raise ValueError(f"Smoke utility {utility.id} has invalid effect values")
    elif utility.duration_tactical_rounds != 0 or utility.activation_penalty <= 0:
        raise ValueError(f"Flash utility {utility.id} has invalid effect values")


def _validate_equipment(equipment: EquipmentProfile) -> None:
    """Reject invalid persistent gear during module initialization."""

    if not equipment.id or not equipment.name_key:
        raise ValueError("Equipment requires stable ids and localized names")
    if not equipment.allowed_sides or any(
        side not in SIDE_INDEXES for side in equipment.allowed_sides
    ):
        raise ValueError(f"Equipment {equipment.id} has invalid side availability")
    if equipment.cost <= 0 or equipment.maximum_carry <= 0:
        raise ValueError(f"Equipment {equipment.id} has invalid economy values")
    if any(
        not action_id or modifier >= 0
        for action_id, modifier in equipment.action_point_modifiers
    ):
        raise ValueError(f"Equipment {equipment.id} has invalid action modifiers")
    action_ids = [
        action_id for action_id, _modifier in equipment.action_point_modifiers
    ]
    if len(action_ids) != len(set(action_ids)):
        raise ValueError(f"Equipment {equipment.id} repeats an action modifier")


def _validate_economy(economy: EconomyProfile) -> None:
    """Reject an invalid economy profile during module initialization."""

    if not economy.loss_rewards:
        raise ValueError("Economy profiles require at least one loss reward")
    if not economy.round_win_rewards:
        raise ValueError("Economy profiles require round-win rewards")
    if not economy.armor_name_key:
        raise ValueError("Economy profiles require a localized armor name")
    win_reasons = [reason for reason, _reward in economy.round_win_rewards]
    if any(not reason for reason in win_reasons) or len(win_reasons) != len(
        set(win_reasons)
    ):
        raise ValueError("Economy profiles require unique round-win reasons")
    values = (
        economy.starting_cash,
        economy.overtime_cash,
        economy.maximum_cash,
        economy.armor_cost,
        economy.maximum_armor,
        *(reward for _reason, reward in economy.round_win_rewards),
        *economy.loss_rewards,
        economy.initial_loss_count,
        economy.plant_team_bonus,
        economy.planter_reward,
        economy.defuser_reward,
    )
    if any(value < 0 for value in values):
        raise ValueError("Economy values cannot be negative")
    if economy.maximum_cash < max(economy.starting_cash, economy.overtime_cash):
        raise ValueError("Maximum cash must cover regulation and overtime starts")
    if tuple(sorted(economy.loss_rewards)) != economy.loss_rewards:
        raise ValueError("Loss rewards must be nondecreasing")
    if economy.initial_loss_count > economy.maximum_loss_count:
        raise ValueError("Initial loss counter exceeds the configured reward ladder")


for _weapon in WEAPONS.values():
    _validate_weapon(_weapon)
for _utility in UTILITIES.values():
    _validate_utility(_utility)
for _equipment in EQUIPMENT.values():
    _validate_equipment(_equipment)
_validate_economy(STANDARD_ECONOMY)


def get_weapon(weapon_id: str) -> WeaponProfile | None:
    """Return a registered weapon by stable id."""

    return WEAPONS.get(weapon_id)


def get_default_sidearm(side_index: int) -> WeaponProfile | None:
    """Return the standard-issue sidearm for a side."""

    return get_weapon(DEFAULT_SIDEARMS.get(side_index, ""))


def get_purchasable_weapons(side_index: int) -> tuple[WeaponProfile, ...]:
    """Return purchasable weapons available to a side in registry order."""

    return tuple(
        weapon
        for weapon in WEAPONS.values()
        if weapon.cost > 0 and side_index in weapon.allowed_sides
    )


def get_utility(utility_id: str) -> UtilityProfile | None:
    """Return a registered utility item by stable id."""

    return UTILITIES.get(utility_id)


def get_utilities() -> tuple[UtilityProfile, ...]:
    """Return every registered utility item in menu order."""

    return tuple(UTILITIES.values())


def get_purchasable_utilities(side_index: int) -> tuple[UtilityProfile, ...]:
    """Return utility items available to a side in registry order."""

    return tuple(
        utility for utility in UTILITIES.values() if side_index in utility.allowed_sides
    )


def get_equipment(equipment_id: str) -> EquipmentProfile | None:
    """Return registered persistent gear by stable id."""

    return EQUIPMENT.get(equipment_id)


def get_purchasable_equipment(side_index: int) -> tuple[EquipmentProfile, ...]:
    """Return persistent gear available to a side in registry order."""

    return tuple(
        equipment
        for equipment in EQUIPMENT.values()
        if side_index in equipment.allowed_sides
    )
