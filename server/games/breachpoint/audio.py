"""Spatial audio profiles and listener transforms for Breach Point."""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from ...audio import (
    AudioSequenceSegment,
    DistanceAttenuation,
    distance_attenuation_gain,
)
from ...game_utils.audio_duration import measure_audio_duration_ticks
from ...game_utils.client_types import get_client_type
from .arsenal import EQUIPMENT, UTILITIES, WEAPONS, get_utility
from .maps import DEFAULT_MAP_ID, TACTICAL_MAPS, GridPoint, TacticalNode

if TYPE_CHECKING:
    from ...users.base import User
    from .arsenal import EquipmentProfile, UtilityProfile, WeaponProfile
    from .ground import DroppedWeapon
    from .player import BreachPointPlayer


TICKS_PER_SECOND = 20
AUDIO_ROOT = "game_breachpoint"
MAP_AMBIENCE_HANDLE = "breachpoint.map.ambience"
MAP_ZONE_AMBIENCE_HANDLE = "breachpoint.map.zone"
MOVEMENT_AUDIO_SEQUENCE_TAG = "breachpoint-movement"
UTILITY_AUDIO_SEQUENCE_TAG = "breachpoint-utility"
WEAPON_AUDIO_SEQUENCE_TAG = "breachpoint-weapon-fire"
BOMB_DETONATION_AUDIO_SEQUENCE_TAG = "breachpoint-bomb-detonation"
UTILITY_FLIGHT_HANDLE_PREFIX = "breachpoint.utility-flight."
MUSIC_CONTEXT_HANDLE = "breachpoint.music-context"
MUSIC_RESULT_HANDLE = "breachpoint.music-result"
MUSIC_ACTION_STOP_SEQUENCE_TAG = "breachpoint-music-action-stop"
MUSIC_CROSSFADE_MS = 800
RADIO_CUE_HANDLE = "breachpoint.radio-cue"
ROUND_STINGER_HANDLE = "breachpoint.round-stinger"
BOMB_EXPLOSION_HANDLE = "breachpoint.bomb-explosion"
FIRE_LOOP_ASSET = f"{AUDIO_ROOT}/utility/fire/loop.ogg"
FIRE_OUTRO_ASSET = f"{AUDIO_ROOT}/utility/fire/fadeout.ogg"
FIRE_EXTINGUISH_ASSET = f"{AUDIO_ROOT}/utility/fire/extinguish.ogg"
MOLOTOV_IDLE_ASSET = f"{AUDIO_ROOT}/utility/fire/molotov_idle.ogg"
FIRE_IGNITE_ASSETS = tuple(
    f"{AUDIO_ROOT}/utility/fire/ignite{index}.ogg" for index in range(1, 5)
)
FIRE_IGNITE_FAMILY = f"{AUDIO_ROOT}/utility/fire/ignite"
FIRE_LAYER_PREFIX = "fire."
FIRE_DAMAGE_ASSETS = tuple(
    f"{AUDIO_ROOT}/combat/burn_damage{index}.ogg" for index in range(1, 6)
)
FIRE_DAMAGE_FAMILY = f"{AUDIO_ROOT}/combat/burn_damage"
FLASH_TINNITUS_ASSET = f"{AUDIO_ROOT}/combat/flash_tinnitus.ogg"

LISTENER_EAR_HEIGHT_METERS = 1.6
WEAPON_SOURCE_HEIGHT_METERS = 1.35
UTILITY_SOURCE_HEIGHT_METERS = 1.15
FOOTSTEP_SOURCE_HEIGHT_METERS = 0.05
DISTANT_REPORT_THRESHOLD_METERS = 24.0
DISTANT_LAYER_VOLUME = 72
# Each bullet deliberately overlaps its close report, distant body, projectile,
# and impact. The shipped assets peak near full scale, so leave enough authored
# headroom on renderers that need it while retaining the established mix on
# other clients. New client-specific calibration belongs in this data table.
WEAPON_FIRE_LAYER_GAINS_BY_CLIENT = {"mobile": 0.4}
WEAPON_PROJECTILE_PRIORITY = 82
FOOTSTEP_STRIDE_METERS = 2.5
MINIMUM_FOOTSTEPS = 2
MAXIMUM_FOOTSTEPS = 12
MOVEMENT_AUDIO_SPEED_PERCENT = 150
GRENADE_TRAVEL_GRID_UNITS_PER_SECOND = 18.0
GRENADE_BOUNCE_SPACING_GRID_UNITS = 7.0
MINIMUM_GRENADE_TRAVEL_TICKS = 5

POSITIONAL_ATTENUATION = DistanceAttenuation(
    model="linear",
    reference_distance=10.0,
    max_distance=65.0,
    rolloff_factor=1.0,
    min_gain=0.0,
    max_gain=1.0,
)
FOOTSTEP_ATTENUATION = DistanceAttenuation(
    model="linear",
    reference_distance=10.0,
    max_distance=38.0,
    rolloff_factor=1.0,
    min_gain=0.0,
    max_gain=1.0,
)
DISTANT_ATTENUATION = DistanceAttenuation(
    model="inverse",
    reference_distance=10.0,
    max_distance=120.0,
    rolloff_factor=0.35,
    min_gain=0.06,
    max_gain=1.0,
)
FIRE_ATTENUATION = DistanceAttenuation(
    model="linear",
    reference_distance=10.0,
    max_distance=38.0,
    rolloff_factor=1.0,
    min_gain=0.0,
    max_gain=1.0,
)

FOOTSTEP_VARIANTS_BY_SURFACE = {
    "sand": 12,
    "concrete": 6,
    "gravel": 10,
}
FOOTSTEP_ASSETS_BY_SURFACE = {
    surface: tuple(
        f"{AUDIO_ROOT}/movement/{surface}_step{index}.ogg"
        for index in range(1, variant_count + 1)
    )
    for surface, variant_count in FOOTSTEP_VARIANTS_BY_SURFACE.items()
}
_UNSUPPORTED_MAP_FOOTSTEP_SURFACES = {
    node.footstep_surface
    for tactical_map in TACTICAL_MAPS.values()
    for node in tactical_map.nodes
    if node.footstep_surface not in FOOTSTEP_ASSETS_BY_SURFACE
}
if _UNSUPPORTED_MAP_FOOTSTEP_SURFACES:
    raise ValueError(
        "Missing Breach Point footstep audio profiles: "
        f"{sorted(_UNSUPPORTED_MAP_FOOTSTEP_SURFACES)}"
    )


def _numbered_assets(family: str, variant_count: int) -> tuple[str, ...]:
    """Return every shipped member of one client-discovered sound family."""

    return tuple(f"{family}{index}.ogg" for index in range(1, variant_count + 1))


TURN_NOTIFICATION_ASSET = f"{AUDIO_ROOT}/ui/turn.ogg"
BUY_ITEM_HOVER_ASSETS = _numbered_assets(f"{AUDIO_ROOT}/ui/buy_hover", 3)


CASING_VARIANT_COUNTS_BY_CALIBER_AND_SURFACE = {
    "9mm": {"sand": 6, "concrete": 5, "gravel": 9},
    "45acp": {"sand": 5, "concrete": 5, "gravel": 9},
    "50ae": {"sand": 8, "concrete": 5, "gravel": 5},
    "556": {"sand": 5, "concrete": 7, "gravel": 6},
    "762": {"sand": 5, "concrete": 5, "gravel": 6},
    "308": {"sand": 6, "concrete": 6, "gravel": 5},
    "12g": {"sand": 7, "concrete": 5, "gravel": 7},
}
CASING_FAMILIES_BY_CALIBER_AND_SURFACE = {
    caliber: {
        surface: f"{AUDIO_ROOT}/combat/casings/{caliber}/{surface}"
        for surface in surface_counts
    }
    for caliber, surface_counts in CASING_VARIANT_COUNTS_BY_CALIBER_AND_SURFACE.items()
}
CASING_ASSETS_BY_CALIBER_AND_SURFACE = {
    caliber: {
        surface: _numbered_assets(
            CASING_FAMILIES_BY_CALIBER_AND_SURFACE[caliber][surface],
            variant_count,
        )
        for surface, variant_count in surface_counts.items()
    }
    for caliber, surface_counts in CASING_VARIANT_COUNTS_BY_CALIBER_AND_SURFACE.items()
}

PROJECTILE_VARIANT_COUNTS = {
    "compact": 5,
    "subsonic": 7,
    "50ae": 8,
    "556": 8,
    "762": 8,
    "308": 8,
    "338": 8,
    "12g": 8,
}
PROJECTILE_ASSETS_BY_PROFILE = {
    profile_id: _numbered_assets(
        f"{AUDIO_ROOT}/combat/projectiles/{profile_id}/flyby",
        variant_count,
    )
    for profile_id, variant_count in PROJECTILE_VARIANT_COUNTS.items()
}
PROJECTILE_IMPACT_VARIANT_COUNTS = {
    "9mm": 6,
    "556": 6,
    "762": 6,
    "multiple": 6,
}
PROJECTILE_IMPACT_ASSETS_BY_PROFILE = {
    profile_id: _numbered_assets(
        f"{AUDIO_ROOT}/combat/projectile_impacts/{profile_id}/impact",
        variant_count,
    )
    for profile_id, variant_count in PROJECTILE_IMPACT_VARIANT_COUNTS.items()
}
BULLET_MISS_OVERSHOOT_GRID_UNITS = 3.0

IMPACT_FLESH_ASSETS = _numbered_assets(f"{AUDIO_ROOT}/combat/flesh_hit", 5)
IMPACT_ARMOR_ASSET = f"{AUDIO_ROOT}/combat/armor_hit.ogg"
HEADSHOT_ASSETS_BY_ARMOR = {
    False: _numbered_assets(f"{AUDIO_ROOT}/combat/headshot/no_armor", 5),
    True: _numbered_assets(f"{AUDIO_ROOT}/combat/headshot/armor", 3),
}
DEATH_VOICE_ASSETS = _numbered_assets(f"{AUDIO_ROOT}/combat/death/voice", 6)
BODY_FALL_VARIANT_COUNTS_BY_SURFACE = {
    "sand": 2,
    "concrete": 2,
    "gravel": 2,
}
BODY_FALL_ASSETS_BY_SURFACE = {
    surface: _numbered_assets(
        f"{AUDIO_ROOT}/combat/death/bodyfall/{surface}",
        variant_count,
    )
    for surface, variant_count in BODY_FALL_VARIANT_COUNTS_BY_SURFACE.items()
}

PICKUP_VARIANT_COUNTS = {
    "ammo": 2,
    "grenade": 3,
    "molotov": 4,
    "weapon": 2,
    "armor": 2,
}
PICKUP_FAMILIES = {
    item_kind: f"{AUDIO_ROOT}/items/{item_kind}"
    for item_kind in PICKUP_VARIANT_COUNTS
}
PICKUP_ASSETS = {
    item_kind: _numbered_assets(PICKUP_FAMILIES[item_kind], variant_count)
    for item_kind, variant_count in PICKUP_VARIANT_COUNTS.items()
}
PICKUP_DEFUSE_KIT_ASSET = f"{AUDIO_ROOT}/items/defuse_kit.ogg"

BOMB_PLANT_INITIATE_ASSET = f"{AUDIO_ROOT}/objective/bomb_plant_initiate.ogg"
BOMB_PLANT_QUIET_ASSET = f"{AUDIO_ROOT}/objective/bomb_plant_quiet.ogg"
BOMB_NVG_ON_ASSET = f"{AUDIO_ROOT}/objective/bomb_nvg_on.ogg"
BOMB_ARM_ASSET = f"{AUDIO_ROOT}/objective/bomb_arm.ogg"
BOMB_ARM_START_RATIO = 0.70
BOMB_KEYPAD_ASSETS = _numbered_assets(f"{AUDIO_ROOT}/objective/bomb_key", 7)
BOMB_KEYPAD_PRESS_COUNT_RANGE = (5, 6)
BOMB_PICKUP_BEEP_ASSETS = _numbered_assets(
    f"{AUDIO_ROOT}/objective/bomb_pickup_beep",
    2,
)
BOMB_DEFUSE_START_ASSET = f"{AUDIO_ROOT}/objective/bomb_defuse_start.ogg"
BOMB_DEFUSED_ASSET = f"{AUDIO_ROOT}/objective/bomb_defused.ogg"
BOMB_BEEP_ASSETS = tuple(
    f"{AUDIO_ROOT}/objective/bomb_beep{index}.ogg" for index in range(1, 4)
)
BOMB_EXPLOSION_ASSET = f"{AUDIO_ROOT}/objective/bomb_explode.ogg"
BUY_COUNTDOWN_ASSET = f"{AUDIO_ROOT}/round_cues/buy_countdown.ogg"
MATCH_VICTORY_ASSET = f"{AUDIO_ROOT}/round_cues/match_victory.ogg"
RADIO_BOMB_PLANTED_ASSET = f"{AUDIO_ROOT}/radio/bomb_planted.ogg"
RADIO_BOMB_DEFUSED_ASSET = f"{AUDIO_ROOT}/radio/bomb_defused.ogg"
RADIO_COUNTER_TERRORISTS_WIN_ASSET = (
    f"{AUDIO_ROOT}/radio/counter_terrorists_win.ogg"
)
RADIO_TERRORISTS_WIN_ASSET = f"{AUDIO_ROOT}/radio/terrorists_win.ogg"
LAST_ROUND_HALF_ASSET = f"{AUDIO_ROOT}/round_cues/last_round_half.ogg"
FINAL_ROUND_STINGER_ASSET = (
    f"{AUDIO_ROOT}/round_cues/final_round_stinger.ogg"
)
MUSIC_MATCH_START_ASSET = f"{AUDIO_ROOT}/music/match_start.ogg"
MUSIC_ROUND_START_ASSET = f"{AUDIO_ROOT}/music/round_start.ogg"
MUSIC_ACTION_START_ASSETS = tuple(
    f"{AUDIO_ROOT}/music/action_start{index}.ogg" for index in range(1, 3)
)
MUSIC_BOMB_PLANTED_ASSET = f"{AUDIO_ROOT}/music/bomb_planted.ogg"
MUSIC_BOMB_TEN_SECOND_ASSET = f"{AUDIO_ROOT}/music/bomb_ten_second.ogg"
MUSIC_ROUND_TEN_SECOND_ASSET = f"{AUDIO_ROOT}/music/round_ten_second.ogg"
MUSIC_ROUND_WON_ASSET = f"{AUDIO_ROOT}/music/round_won.ogg"
MUSIC_ROUND_LOST_ASSET = f"{AUDIO_ROOT}/music/round_lost.ogg"
MAP_AMBIENCE_ASSETS = tuple(
    sorted(
        {
            layer.asset
            for tactical_map in TACTICAL_MAPS.values()
            for layer in (
                (
                    ()
                    if tactical_map.global_ambience is None
                    else (tactical_map.global_ambience,)
                )
                + tactical_map.zone_ambience
            )
        }
    )
)
MAP_AMBIENT_STINGER_ASSETS = tuple(
    sorted(
        {
            asset
            for tactical_map in TACTICAL_MAPS.values()
            for emitter in tactical_map.ambient_emitters
            for asset in emitter.assets
        }
    )
)
_DEFAULT_MAP_AMBIENCE = TACTICAL_MAPS[DEFAULT_MAP_ID].global_ambience
if _DEFAULT_MAP_AMBIENCE is None:
    raise ValueError("The default Breach Point map requires global ambience")
MAP_AMBIENCE_ASSET = _DEFAULT_MAP_AMBIENCE.asset


@dataclass(frozen=True)
class WeaponAudioProfile:
    """Assets and cosmetic movement pacing for one firearm."""

    weapon_id: str
    fire_close_assets: tuple[str, ...]
    fire_distant: str
    reload_assets: tuple[str, ...]
    equip_asset: str
    footstep_cadence_percent: int
    shot_interval_ms: int
    projectile_assets: tuple[str, ...]
    projectile_impact_assets: tuple[str, ...]
    casing_caliber: str
    drop_asset: str
    hold_asset: str = ""
    shell_reload_assets: tuple[str, ...] = ()


@dataclass(frozen=True)
class UtilityAudioProfile:
    """Data-driven handling, flight, impact, and detonation audio."""

    utility_id: str
    draw_asset: str
    pin_assets: tuple[str, ...]
    release_asset: str
    flight_asset: str
    bounce_asset: str
    landing_asset: str
    detonate_close_assets: tuple[str, ...]
    detonate_close_family: str
    detonate_distant_assets: tuple[str, ...]
    detonate_distant_family: str
    detonate_overlay_assets: tuple[str, ...]
    detonate_overlay_family: str
    detonate_overlay_variants: tuple[str, ...]
    detonate_overlays_near_only: bool
    pickup_kind: str


@dataclass(frozen=True)
class UtilityAudioTiming:
    """Measured sequence timing and physical bounce positions for a throw."""

    handling_ticks: int
    travel_ticks: int
    impact_lead_ticks: int
    bounce_points: tuple[GridPoint, ...]


def _weapon_audio(
    weapon_id: str,
    *,
    footstep_cadence_percent: int,
    close_variants: int = 1,
    projectile_profile: str,
    projectile_impact_profile: str,
    casing_caliber: str,
    drop_profile: str,
    shot_interval_ms: int,
    hold: bool = False,
    shotgun: bool = False,
) -> WeaponAudioProfile:
    root = f"{AUDIO_ROOT}/weapons/{weapon_id}"
    close_family = f"{root}/fire_close" if close_variants > 1 else ""
    return WeaponAudioProfile(
        weapon_id=weapon_id,
        fire_close_assets=(
            tuple(
                f"{close_family}{index}.ogg" for index in range(1, close_variants + 1)
            )
            if close_family
            else (f"{root}/fire_close.ogg",)
        ),
        fire_distant=f"{root}/fire_distant.ogg",
        reload_assets=(
            f"{root}/reload_out.ogg",
            f"{root}/reload_in.ogg",
            f"{root}/reload_finish.ogg",
        )
        if not shotgun
        else (),
        equip_asset=f"{root}/equip.ogg",
        footstep_cadence_percent=footstep_cadence_percent,
        shot_interval_ms=max(1, shot_interval_ms),
        projectile_assets=PROJECTILE_ASSETS_BY_PROFILE[projectile_profile],
        projectile_impact_assets=PROJECTILE_IMPACT_ASSETS_BY_PROFILE[
            projectile_impact_profile
        ],
        casing_caliber=casing_caliber,
        drop_asset=f"{AUDIO_ROOT}/weapons/drop/{drop_profile}.ogg",
        hold_asset=f"{root}/hold.ogg" if hold else "",
        shell_reload_assets=(
            f"{root}/reload_shell1.ogg",
            f"{root}/reload_shell2.ogg",
            f"{root}/reload_finish.ogg",
        )
        if shotgun
        else (),
    )


WEAPON_AUDIO_PROFILES = {
    profile.weapon_id: profile
    for profile in (
        _weapon_audio(
            "glock",
            footstep_cadence_percent=108,
            close_variants=2,
            projectile_profile="compact",
            projectile_impact_profile="9mm",
            casing_caliber="9mm",
            drop_profile="pistol",
            shot_interval_ms=50,
        ),
        _weapon_audio(
            "usp_s",
            footstep_cadence_percent=108,
            close_variants=3,
            projectile_profile="subsonic",
            projectile_impact_profile="9mm",
            casing_caliber="45acp",
            drop_profile="pistol",
            shot_interval_ms=170,
        ),
        _weapon_audio(
            "desert_eagle",
            footstep_cadence_percent=103,
            close_variants=2,
            projectile_profile="50ae",
            projectile_impact_profile="762",
            casing_caliber="50ae",
            drop_profile="revolver",
            shot_interval_ms=225,
        ),
        _weapon_audio(
            "mac10",
            footstep_cadence_percent=108,
            close_variants=3,
            projectile_profile="compact",
            projectile_impact_profile="9mm",
            casing_caliber="45acp",
            drop_profile="sub_machine_gun",
            shot_interval_ms=75,
        ),
        _weapon_audio(
            "mp9",
            footstep_cadence_percent=108,
            close_variants=4,
            projectile_profile="compact",
            projectile_impact_profile="9mm",
            casing_caliber="9mm",
            drop_profile="sub_machine_gun",
            shot_interval_ms=70,
        ),
        _weapon_audio(
            "nova",
            footstep_cadence_percent=98,
            projectile_profile="12g",
            projectile_impact_profile="multiple",
            casing_caliber="12g",
            drop_profile="shotgun",
            shot_interval_ms=880,
            shotgun=True,
        ),
        _weapon_audio(
            "galil_ar",
            footstep_cadence_percent=96,
            close_variants=4,
            projectile_profile="556",
            projectile_impact_profile="556",
            casing_caliber="556",
            drop_profile="assault_rifle",
            shot_interval_ms=90,
        ),
        _weapon_audio(
            "famas",
            footstep_cadence_percent=98,
            close_variants=4,
            projectile_profile="556",
            projectile_impact_profile="556",
            casing_caliber="556",
            drop_profile="assault_rifle",
            shot_interval_ms=75,
        ),
        _weapon_audio(
            "ssg08",
            footstep_cadence_percent=103,
            projectile_profile="308",
            projectile_impact_profile="762",
            casing_caliber="308",
            drop_profile="marksman_rifle",
            shot_interval_ms=1250,
            hold=True,
        ),
        _weapon_audio(
            "ak47",
            footstep_cadence_percent=96,
            close_variants=4,
            projectile_profile="762",
            projectile_impact_profile="762",
            casing_caliber="762",
            drop_profile="assault_rifle",
            shot_interval_ms=100,
        ),
        _weapon_audio(
            "m4",
            footstep_cadence_percent=100,
            close_variants=4,
            projectile_profile="556",
            projectile_impact_profile="556",
            casing_caliber="556",
            drop_profile="assault_rifle",
            shot_interval_ms=90,
        ),
        _weapon_audio(
            "awp",
            footstep_cadence_percent=90,
            close_variants=2,
            projectile_profile="338",
            projectile_impact_profile="762",
            casing_caliber="308",
            drop_profile="sniper_rifle",
            shot_interval_ms=1455,
            hold=True,
        ),
    )
}


def _utility_audio(
    utility_id: str,
    *,
    close_variants: int = 1,
    distant_variants: int = 1,
    has_pin: bool = True,
    has_flight: bool = False,
    has_bounce: bool = False,
    has_landing: bool = False,
    detonate_overlay_assets: tuple[str, ...] = (),
    detonate_overlay_family: str = "",
    detonate_overlay_variants: tuple[str, ...] = (),
    detonate_overlays_near_only: bool = True,
    pickup_kind: str = "grenade",
) -> UtilityAudioProfile:
    root = f"{AUDIO_ROOT}/utility/{utility_id}"
    close_family = f"{root}/detonate_close" if close_variants > 1 else ""
    distant_family = f"{root}/detonate_distant" if distant_variants > 1 else ""
    return UtilityAudioProfile(
        utility_id=utility_id,
        draw_asset=f"{root}/draw.ogg",
        pin_assets=(f"{root}/pin_start.ogg", f"{root}/pin.ogg") if has_pin else (),
        release_asset=f"{root}/release.ogg",
        flight_asset=f"{root}/flight.ogg" if has_flight else "",
        bounce_asset=f"{root}/bounce.ogg" if has_bounce else "",
        landing_asset=f"{root}/landing.ogg" if has_landing else "",
        detonate_close_assets=(
            tuple(
                f"{close_family}{index}.ogg" for index in range(1, close_variants + 1)
            )
            if close_family
            else (f"{root}/detonate_close.ogg",)
        ),
        detonate_close_family=close_family,
        detonate_distant_assets=(
            tuple(
                f"{distant_family}{index}.ogg"
                for index in range(1, distant_variants + 1)
            )
            if distant_family
            else (f"{root}/detonate_distant.ogg",)
        ),
        detonate_distant_family=distant_family,
        detonate_overlay_assets=detonate_overlay_assets,
        detonate_overlay_family=detonate_overlay_family,
        detonate_overlay_variants=detonate_overlay_variants,
        detonate_overlays_near_only=detonate_overlays_near_only,
        pickup_kind=pickup_kind,
    )


UTILITY_AUDIO_PROFILES = {
    profile.utility_id: profile
    for profile in (
        _utility_audio(
            "smoke",
            has_landing=True,
            detonate_overlay_assets=(f"{AUDIO_ROOT}/utility/smoke/emit.ogg",),
            detonate_overlays_near_only=False,
        ),
        _utility_audio(
            "flashbang",
            close_variants=2,
            distant_variants=2,
            has_landing=True,
        ),
        _utility_audio(
            "he_grenade",
            close_variants=6,
            distant_variants=6,
            has_bounce=True,
        ),
        _utility_audio(
            "molotov",
            close_variants=3,
            distant_variants=3,
            has_pin=False,
            has_flight=True,
            pickup_kind="molotov",
            detonate_overlay_assets=(
                f"{AUDIO_ROOT}/utility/molotov/detonate_sweetener.ogg",
                MOLOTOV_IDLE_ASSET,
            ),
            detonate_overlay_family=FIRE_IGNITE_FAMILY,
            detonate_overlay_variants=FIRE_IGNITE_ASSETS,
        ),
        _utility_audio(
            "incendiary_grenade",
            close_variants=3,
            distant_variants=3,
            has_flight=True,
            has_bounce=True,
            pickup_kind="molotov",
            detonate_overlay_assets=(
                f"{AUDIO_ROOT}/utility/incendiary_grenade/detonate_sweetener.ogg",
            ),
        ),
    )
}
EQUIPMENT_PICKUP_KINDS = {"defuse_kit": "defuse_kit"}

_MISSING_WEAPON_AUDIO = set(WEAPONS) - set(WEAPON_AUDIO_PROFILES)
_EXTRA_WEAPON_AUDIO = set(WEAPON_AUDIO_PROFILES) - set(WEAPONS)
_MISSING_UTILITY_AUDIO = set(UTILITIES) - set(UTILITY_AUDIO_PROFILES)
_EXTRA_UTILITY_AUDIO = set(UTILITY_AUDIO_PROFILES) - set(UTILITIES)
_MISSING_EQUIPMENT_AUDIO = set(EQUIPMENT) - set(EQUIPMENT_PICKUP_KINDS)
_EXTRA_EQUIPMENT_AUDIO = set(EQUIPMENT_PICKUP_KINDS) - set(EQUIPMENT)
if any(
    (
        _MISSING_WEAPON_AUDIO,
        _EXTRA_WEAPON_AUDIO,
        _MISSING_UTILITY_AUDIO,
        _EXTRA_UTILITY_AUDIO,
        _MISSING_EQUIPMENT_AUDIO,
        _EXTRA_EQUIPMENT_AUDIO,
    )
):
    raise ValueError(
        "Breach Point arsenal/audio profile mismatch: "
        f"missing weapons={sorted(_MISSING_WEAPON_AUDIO)}, "
        f"extra weapons={sorted(_EXTRA_WEAPON_AUDIO)}, "
        f"missing utility={sorted(_MISSING_UTILITY_AUDIO)}, "
        f"extra utility={sorted(_EXTRA_UTILITY_AUDIO)}, "
        f"missing equipment={sorted(_MISSING_EQUIPMENT_AUDIO)}, "
        f"extra equipment={sorted(_EXTRA_EQUIPMENT_AUDIO)}"
    )

BREACHPOINT_ASSET_PATHS = tuple(
    sorted(
        {
            MAP_AMBIENCE_ASSET,
            *MAP_AMBIENCE_ASSETS,
            TURN_NOTIFICATION_ASSET,
            *BUY_ITEM_HOVER_ASSETS,
            FIRE_LOOP_ASSET,
            FIRE_OUTRO_ASSET,
            FIRE_EXTINGUISH_ASSET,
            MOLOTOV_IDLE_ASSET,
            *FIRE_IGNITE_ASSETS,
            *FIRE_DAMAGE_ASSETS,
            FLASH_TINNITUS_ASSET,
            *MAP_AMBIENT_STINGER_ASSETS,
            IMPACT_ARMOR_ASSET,
            *(
                asset
                for surface_assets in BODY_FALL_ASSETS_BY_SURFACE.values()
                for asset in surface_assets
            ),
            *DEATH_VOICE_ASSETS,
            *(
                asset
                for assets in HEADSHOT_ASSETS_BY_ARMOR.values()
                for asset in assets
            ),
            *(
                asset
                for surface_assets in CASING_ASSETS_BY_CALIBER_AND_SURFACE.values()
                for assets in surface_assets.values()
                for asset in assets
            ),
            *(
                asset for assets in PICKUP_ASSETS.values() for asset in assets
            ),
            PICKUP_DEFUSE_KIT_ASSET,
            *(
                asset
                for assets in FOOTSTEP_ASSETS_BY_SURFACE.values()
                for asset in assets
            ),
            *IMPACT_FLESH_ASSETS,
            BOMB_PLANT_INITIATE_ASSET,
            BOMB_PLANT_QUIET_ASSET,
            BOMB_NVG_ON_ASSET,
            BOMB_ARM_ASSET,
            *BOMB_KEYPAD_ASSETS,
            *BOMB_PICKUP_BEEP_ASSETS,
            BOMB_DEFUSE_START_ASSET,
            BOMB_DEFUSED_ASSET,
            BOMB_EXPLOSION_ASSET,
            *BOMB_BEEP_ASSETS,
            BUY_COUNTDOWN_ASSET,
            MATCH_VICTORY_ASSET,
            RADIO_BOMB_PLANTED_ASSET,
            RADIO_BOMB_DEFUSED_ASSET,
            RADIO_COUNTER_TERRORISTS_WIN_ASSET,
            RADIO_TERRORISTS_WIN_ASSET,
            LAST_ROUND_HALF_ASSET,
            MUSIC_MATCH_START_ASSET,
            MUSIC_ROUND_START_ASSET,
            *MUSIC_ACTION_START_ASSETS,
            MUSIC_BOMB_PLANTED_ASSET,
            MUSIC_BOMB_TEN_SECOND_ASSET,
            MUSIC_ROUND_TEN_SECOND_ASSET,
            MUSIC_ROUND_WON_ASSET,
            MUSIC_ROUND_LOST_ASSET,
            FINAL_ROUND_STINGER_ASSET,
            *(
                asset
                for profile in WEAPON_AUDIO_PROFILES.values()
                for asset in (
                    *profile.fire_close_assets,
                    profile.fire_distant,
                    profile.equip_asset,
                    profile.drop_asset,
                    profile.hold_asset,
                    *profile.projectile_assets,
                    *profile.projectile_impact_assets,
                    *profile.reload_assets,
                    *profile.shell_reload_assets,
                )
                if asset
            ),
            *(
                asset
                for profile in UTILITY_AUDIO_PROFILES.values()
                for asset in (
                    profile.draw_asset,
                    *profile.pin_assets,
                    profile.release_asset,
                    profile.flight_asset,
                    profile.bounce_asset,
                    profile.landing_asset,
                    *profile.detonate_close_assets,
                    *profile.detonate_distant_assets,
                    *profile.detonate_overlay_assets,
                    *profile.detonate_overlay_variants,
                )
                if asset
            ),
        }
    )
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)

# Server packages deliberately do not bundle the clients' sound files. Keep
# the measured timing metadata needed by authoritative gameplay alongside the
# game so a wheel-only deployment preserves the same pacing as a source tree.
# Tests require this table to match the shipped assets whenever they change.
SERVER_TIMING_ASSET_DURATIONS_MS = {
    "game_breachpoint/movement/concrete_step1.ogg": 540,
    "game_breachpoint/movement/concrete_step2.ogg": 624,
    "game_breachpoint/movement/concrete_step3.ogg": 851,
    "game_breachpoint/movement/concrete_step4.ogg": 643,
    "game_breachpoint/movement/concrete_step5.ogg": 543,
    "game_breachpoint/movement/concrete_step6.ogg": 841,
    "game_breachpoint/movement/gravel_step1.ogg": 520,
    "game_breachpoint/movement/gravel_step2.ogg": 579,
    "game_breachpoint/movement/gravel_step3.ogg": 868,
    "game_breachpoint/movement/gravel_step4.ogg": 561,
    "game_breachpoint/movement/gravel_step5.ogg": 868,
    "game_breachpoint/movement/gravel_step6.ogg": 660,
    "game_breachpoint/movement/gravel_step7.ogg": 874,
    "game_breachpoint/movement/gravel_step8.ogg": 563,
    "game_breachpoint/movement/gravel_step9.ogg": 869,
    "game_breachpoint/movement/gravel_step10.ogg": 576,
    "game_breachpoint/movement/sand_step1.ogg": 500,
    "game_breachpoint/movement/sand_step2.ogg": 500,
    "game_breachpoint/movement/sand_step3.ogg": 750,
    "game_breachpoint/movement/sand_step4.ogg": 750,
    "game_breachpoint/movement/sand_step5.ogg": 500,
    "game_breachpoint/movement/sand_step6.ogg": 500,
    "game_breachpoint/movement/sand_step7.ogg": 750,
    "game_breachpoint/movement/sand_step8.ogg": 750,
    "game_breachpoint/movement/sand_step9.ogg": 750,
    "game_breachpoint/movement/sand_step10.ogg": 1000,
    "game_breachpoint/movement/sand_step11.ogg": 750,
    "game_breachpoint/movement/sand_step12.ogg": 820,
    "game_breachpoint/objective/bomb_arm.ogg": 1240,
    "game_breachpoint/objective/bomb_nvg_on.ogg": 1758,
    "game_breachpoint/utility/flashbang/draw.ogg": 408,
    "game_breachpoint/utility/flashbang/landing.ogg": 385,
    "game_breachpoint/utility/flashbang/pin.ogg": 794,
    "game_breachpoint/utility/flashbang/pin_start.ogg": 580,
    "game_breachpoint/utility/he_grenade/draw.ogg": 438,
    "game_breachpoint/utility/he_grenade/pin.ogg": 794,
    "game_breachpoint/utility/he_grenade/pin_start.ogg": 580,
    "game_breachpoint/utility/incendiary_grenade/draw.ogg": 442,
    "game_breachpoint/utility/incendiary_grenade/pin.ogg": 794,
    "game_breachpoint/utility/incendiary_grenade/pin_start.ogg": 580,
    "game_breachpoint/utility/molotov/draw.ogg": 442,
    "game_breachpoint/utility/smoke/draw.ogg": 402,
    "game_breachpoint/utility/smoke/landing.ogg": 385,
    "game_breachpoint/utility/smoke/pin.ogg": 794,
    "game_breachpoint/utility/smoke/pin_start.ogg": 580,
}


@cache
def sound_ticks(sound: str) -> int:
    """Measure a shipped asset, retaining a safe development fallback."""

    relative_path = PurePosixPath(sound)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return 0
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=TICKS_PER_SECOND,
        )
        if measured is not None:
            return measured
    duration_ms = SERVER_TIMING_ASSET_DURATIONS_MS.get(sound)
    if duration_ms is not None:
        return math.ceil(duration_ms * TICKS_PER_SECOND / 1000)
    return 0


@cache
def sound_milliseconds(sound: str) -> int:
    """Measure an asset finely enough to align a server-timed atomic chain."""

    relative_path = PurePosixPath(sound)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return 0
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=1000,
        )
        if measured is not None:
            return measured
    duration_ms = SERVER_TIMING_ASSET_DURATIONS_MS.get(sound)
    if duration_ms is not None:
        return duration_ms
    return math.ceil(sound_ticks(sound) * 1000 / TICKS_PER_SECOND)


def bomb_detonation_warning_ticks() -> int:
    """Return the full NVG-to-arm warning window on the server tick clock."""

    duration_ms = (
        math.ceil(sound_milliseconds(BOMB_NVG_ON_ASSET) * BOMB_ARM_START_RATIO)
        + sound_milliseconds(BOMB_ARM_ASSET)
    )
    return math.ceil(duration_ms * TICKS_PER_SECOND / 1000)


def movement_audio_plan(
    origin: GridPoint,
    destination: GridPoint,
    weapon_id: str,
    *,
    surface_id: str = "sand",
    variant_offset: int = 0,
) -> tuple[tuple[str, ...], float, int, int]:
    """Return natural-pitch footsteps, onset ratio, and full sequence timing."""

    profile = WEAPON_AUDIO_PROFILES.get(weapon_id)
    authored_cadence = profile.footstep_cadence_percent if profile else 100
    cadence_percent = authored_cadence * MOVEMENT_AUDIO_SPEED_PERCENT / 100
    next_start_ratio = min(1.0, 100 / cadence_percent)
    footstep_assets = FOOTSTEP_ASSETS_BY_SURFACE[surface_id]
    distance = math.hypot(destination.x - origin.x, destination.y - origin.y)
    step_count = max(
        MINIMUM_FOOTSTEPS,
        min(MAXIMUM_FOOTSTEPS, math.ceil(distance / FOOTSTEP_STRIDE_METERS)),
    )
    assets = tuple(
        footstep_assets[(variant_offset + index) % len(footstep_assets)]
        for index in range(step_count)
    )
    asset_ticks = tuple(sound_ticks(asset) for asset in assets)
    duration_ticks = max(
        1,
        sum(math.ceil(ticks * next_start_ratio) for ticks in asset_ticks[:-1])
        + asset_ticks[-1],
    )
    duration_ms = math.ceil(duration_ticks * 1000 / TICKS_PER_SECOND)
    return assets, next_start_ratio, duration_ticks, duration_ms


def weapon_fire_delay_ticks(weapon_id: str, shot_index: int) -> int:
    """Quantize one CS cycle interval without accumulating scheduler drift.

    The authoritative CS cycle times are finer than the server's 50 ms tick.
    Rounding each cumulative onset independently produces alternating one- and
    two-tick gaps for 70-90 ms weapons instead of permanently making them too
    fast or too slow.
    """

    profile = WEAPON_AUDIO_PROFILES.get(weapon_id)
    if not profile:
        return 1
    current_onset = math.floor(
        shot_index * profile.shot_interval_ms * TICKS_PER_SECOND / 1000 + 0.5
    )
    next_onset = math.floor(
        (shot_index + 1) * profile.shot_interval_ms * TICKS_PER_SECOND / 1000 + 0.5
    )
    return max(1, next_onset - current_onset)


def utility_audio_timing(
    utility_id: str,
    origin: GridPoint,
    destination: GridPoint,
) -> UtilityAudioTiming:
    """Build measured handling/travel timing and physical bounce positions."""

    profile = UTILITY_AUDIO_PROFILES.get(utility_id)
    if not profile:
        return UtilityAudioTiming(0, 0, 0, ())
    handling_ticks = sum(
        sound_ticks(asset)
        for asset in (
            profile.draw_asset,
            *profile.pin_assets,
        )
        if asset
    )
    grid_distance = math.hypot(
        destination.x - origin.x,
        destination.y - origin.y,
    )
    travel_ticks = max(
        MINIMUM_GRENADE_TRAVEL_TICKS,
        math.ceil(
            grid_distance / GRENADE_TRAVEL_GRID_UNITS_PER_SECOND * TICKS_PER_SECOND
        ),
    )
    bounce_count = (
        max(1, math.ceil(grid_distance / GRENADE_BOUNCE_SPACING_GRID_UNITS))
        if profile.bounce_asset and grid_distance
        else 0
    )
    bounce_points = tuple(
        GridPoint(
            round(origin.x + (destination.x - origin.x) * index / (bounce_count + 1)),
            round(origin.y + (destination.y - origin.y) * index / (bounce_count + 1)),
        )
        for index in range(1, bounce_count + 1)
    )
    impact_lead_ticks = (
        min(travel_ticks, sound_ticks(profile.landing_asset))
        if profile.landing_asset
        else 0
    )
    return UtilityAudioTiming(
        handling_ticks=handling_ticks,
        travel_ticks=travel_ticks,
        impact_lead_ticks=impact_lead_ticks,
        bounce_points=bounce_points,
    )


def world_distance_meters(
    first: GridPoint,
    second: GridPoint,
    grid_unit_meters: float,
) -> float:
    """Return physical planar distance between two map coordinates."""

    return math.hypot(second.x - first.x, second.y - first.y) * grid_unit_meters


def listener_relative_position(
    source: GridPoint,
    listener: GridPoint,
    listener_heading_degrees: int,
    grid_unit_meters: float,
    *,
    source_height_meters: float = 0.0,
) -> tuple[float, float, float]:
    """Rotate a world point into a listener frame facing protocol ``+Y``."""

    delta_x = (source.x - listener.x) * grid_unit_meters
    delta_y = (source.y - listener.y) * grid_unit_meters
    heading = math.radians(listener_heading_degrees % 360)
    right = delta_x * math.cos(heading) - delta_y * math.sin(heading)
    forward = delta_x * math.sin(heading) + delta_y * math.cos(heading)
    return (
        round(right, 3),
        round(forward, 3),
        round(source_height_meters - LISTENER_EAR_HEIGHT_METERS, 3),
    )


class BreachPointAudioMixin:
    """Per-listener HRTF dispatch built on the shared audio protocol."""

    def attach_user(
        self,
        player_id: str,
        user: User,
        *,
        session_handover: bool = False,
    ) -> None:
        """Attach a listener and add any active private environmental layers."""

        super().attach_user(
            player_id,
            user,
            session_handover=session_handover,
        )
        if self.status != "playing":
            return
        listener = self._breach_player_by_id(player_id)
        if not listener:
            return
        for effect in self.area_effects:
            if effect.effect != "fire":
                continue
            handle = self._fire_audio_handle(effect.node_id)
            if any(
                state.kind == "ambience"
                and state.handle == handle
                and listener.id in state.recipient_ids
                for state in self.active_audio.values()
            ):
                continue
            self._start_fire_audio_for_listener(effect.node_id, listener)
        self._sync_listener_environment_audio(listener)
        self._replay_restored_finite_audio_for_listener(listener, user)

    def _prepare_restored_finite_audio_sequences(self) -> None:
        """Restart the current finite-audio stage after deserialization."""

        self._restored_finite_audio_sequence_ids.clear()
        if self.status != "playing":
            return
        for sequence in self.active_sequences:
            expected_index = (
                1
                if sequence.tag == MOVEMENT_AUDIO_SEQUENCE_TAG
                or sequence.tag == BOMB_DETONATION_AUDIO_SEQUENCE_TAG
                else sequence.current_index
                if sequence.tag
                in {UTILITY_AUDIO_SEQUENCE_TAG, WEAPON_AUDIO_SEQUENCE_TAG}
                else -1
            )
            if expected_index < 1 or sequence.current_index != expected_index:
                continue
            if (
                sequence.tag == UTILITY_AUDIO_SEQUENCE_TAG
                and str(sequence.metadata.get("audio_stage", ""))
                in {"flight", "bounce"}
                and any(
                    state.kind == "sfx"
                    and state.handle
                    == self._utility_flight_audio_handle(sequence.sequence_id)
                    for state in self.active_audio.values()
                )
            ):
                continue
            prior_beat_index = sequence.current_index - 1
            if not 0 <= prior_beat_index < len(sequence.beats):
                continue
            duration_ticks = sequence.beats[prior_beat_index].delay_after_ticks
            sequence.next_tick = self.sound_scheduler_tick + max(1, duration_ticks)
            if sequence.tag != WEAPON_AUDIO_SEQUENCE_TAG:
                self._restored_finite_audio_sequence_ids.add(sequence.sequence_id)
        for listener, user in self._audio_listeners():
            self._replay_restored_finite_audio_for_listener(listener, user)

    def _replay_restored_finite_audio_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
    ) -> None:
        for sequence in self.active_sequences:
            if sequence.sequence_id not in self._restored_finite_audio_sequence_ids:
                continue
            metadata = sequence.metadata
            payload = metadata.get("payload")
            if not isinstance(payload, dict):
                continue
            if sequence.tag == MOVEMENT_AUDIO_SEQUENCE_TAG:
                mover = self._breach_player_by_id(str(payload.get("player_id", "")))
                if not mover:
                    continue
                self._play_movement_audio_for_listener(
                    listener,
                    user,
                    mover,
                    GridPoint(
                        int(payload.get("origin_x", -1)),
                        int(payload.get("origin_y", -1)),
                    ),
                    GridPoint(
                        int(payload.get("destination_x", -1)),
                        int(payload.get("destination_y", -1)),
                    ),
                    tuple(str(asset) for asset in payload.get("assets", [])),
                    float(payload["next_start_ratio"]),
                )
                continue
            if sequence.tag == BOMB_DETONATION_AUDIO_SEQUENCE_TAG:
                self._play_bomb_detonation_warning_audio(
                    GridPoint(
                        int(payload.get("x", -1)),
                        int(payload.get("y", -1)),
                    )
                )
                continue
            if sequence.tag != UTILITY_AUDIO_SEQUENCE_TAG:
                continue
            thrower = self._breach_player_by_id(str(payload.get("player_id", "")))
            utility = get_utility(str(payload.get("utility_id", "")))
            if not thrower or not utility:
                continue
            stage = str(metadata.get("audio_stage", "handling"))
            node = self._node(str(payload.get("node_id", "")))
            profile = UTILITY_AUDIO_PROFILES.get(utility.id)
            if stage == "flight":
                continue
            if stage == "bounce" and profile and profile.bounce_asset:
                self._play_spatial_asset_for_listener(
                    listener,
                    user,
                    profile.bounce_asset,
                    GridPoint(
                        int(metadata.get("audio_x", -1)),
                        int(metadata.get("audio_y", -1)),
                    ),
                    source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                    volume=86,
                    priority=52,
                )
            elif stage == "impact" and node and profile and profile.landing_asset:
                self._play_spatial_asset_for_listener(
                    listener,
                    user,
                    profile.landing_asset,
                    node.anchor,
                    source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                    volume=90,
                    priority=56,
                )
            else:
                self._play_utility_handling_for_listener(
                    listener,
                    user,
                    thrower,
                    utility,
                    str(payload.get("node_id", "")),
                )

    def _audio_listener_frame(
        self,
        listener: BreachPointPlayer,
        *,
        point: GridPoint | None = None,
        heading: int | None = None,
    ) -> tuple[GridPoint, int]:
        if listener.is_spectator:
            return (
                self.tactical_map.spectator_anchor,
                self.tactical_map.spectator_heading,
            )
        resolved_point = point or self._player_grid_point(listener)
        resolved_heading = listener.facing_degrees if heading is None else heading
        return resolved_point, resolved_heading

    def _relative_audio_position(
        self,
        listener: BreachPointPlayer,
        source: GridPoint,
        *,
        source_height_meters: float,
        listener_point: GridPoint | None = None,
        listener_heading: int | None = None,
    ) -> tuple[float, float, float]:
        point, heading = self._audio_listener_frame(
            listener,
            point=listener_point,
            heading=listener_heading,
        )
        return listener_relative_position(
            source,
            point,
            heading,
            self.tactical_map.grid_unit_meters,
            source_height_meters=source_height_meters,
        )

    def _audio_listeners(self) -> list[tuple[BreachPointPlayer, User]]:
        listeners: list[tuple[BreachPointPlayer, User]] = []
        for player in self.players:
            listener = self._breach_player(player)
            user = self.get_user(player)
            if listener and user:
                listeners.append((listener, user))
        return listeners

    def _listener_spatialization(
        self,
        listener: BreachPointPlayer,
        source: GridPoint,
        *,
        actor_id: str = "",
        source_height_meters: float,
        attenuation: DistanceAttenuation,
    ) -> tuple[
        tuple[float, float, float] | None,
        DistanceAttenuation | None,
    ] | None:
        """Return audible spatial data without disclosing silent world positions."""

        if listener.id == actor_id:
            return None, None
        position = self._relative_audio_position(
            listener,
            source,
            source_height_meters=source_height_meters,
        )
        if distance_attenuation_gain(position, attenuation) <= 0:
            return None
        return position, attenuation

    def _listener_can_hear_path(
        self,
        listener: BreachPointPlayer,
        origin: GridPoint,
        destination: GridPoint,
        *,
        source_height_meters: float,
        attenuation: DistanceAttenuation,
    ) -> bool:
        """Return whether any point on a moving source's path is audible."""

        listener_point, _ = self._audio_listener_frame(listener)
        path_x = destination.x - origin.x
        path_y = destination.y - origin.y
        path_length_squared = path_x * path_x + path_y * path_y
        if path_length_squared:
            projection = (
                (listener_point.x - origin.x) * path_x
                + (listener_point.y - origin.y) * path_y
            ) / path_length_squared
            projection = max(0.0, min(1.0, projection))
        else:
            projection = 0.0
        closest_x = origin.x + path_x * projection
        closest_y = origin.y + path_y * projection
        scale = self.tactical_map.grid_unit_meters
        closest_position = (
            (closest_x - listener_point.x) * scale,
            (closest_y - listener_point.y) * scale,
            source_height_meters - LISTENER_EAR_HEIGHT_METERS,
        )
        return distance_attenuation_gain(closest_position, attenuation) > 0

    def _play_spatial_asset(
        self,
        asset: str,
        source: GridPoint,
        *,
        actor_id: str = "",
        source_height_meters: float = WEAPON_SOURCE_HEIGHT_METERS,
        attenuation: DistanceAttenuation = POSITIONAL_ATTENUATION,
        volume: int = 100,
        priority: int = 0,
    ) -> None:
        for listener, user in self._audio_listeners():
            self._play_spatial_asset_for_listener(
                listener,
                user,
                asset,
                source,
                actor_id=actor_id,
                source_height_meters=source_height_meters,
                attenuation=attenuation,
                volume=volume,
                priority=priority,
            )

    def _play_spatial_asset_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
        asset: str,
        source: GridPoint,
        *,
        actor_id: str = "",
        source_height_meters: float = WEAPON_SOURCE_HEIGHT_METERS,
        attenuation: DistanceAttenuation = POSITIONAL_ATTENUATION,
        volume: int = 100,
        priority: int = 0,
    ) -> None:
        spatialization = self._listener_spatialization(
            listener,
            source,
            actor_id=actor_id,
            source_height_meters=source_height_meters,
            attenuation=attenuation,
        )
        if spatialization is None:
            return
        position, curve = spatialization
        user.play_sound(
            asset,
            buffer="game",
            volume=volume,
            priority=priority,
            position=position,
            attenuation=curve,
        )

    def _play_spatial_family(
        self,
        family: str,
        source: GridPoint,
        *,
        actor_id: str = "",
        source_height_meters: float = WEAPON_SOURCE_HEIGHT_METERS,
        attenuation: DistanceAttenuation = POSITIONAL_ATTENUATION,
        volume: int = 100,
        priority: int = 0,
        max_instances: int = 0,
    ) -> None:
        """Play one dynamically discovered variant at a world-space source."""

        for listener, user in self._audio_listeners():
            spatialization = self._listener_spatialization(
                listener,
                source,
                actor_id=actor_id,
                source_height_meters=source_height_meters,
                attenuation=attenuation,
            )
            if spatialization is None:
                continue
            position, curve = spatialization
            user.play_sound_family(
                family,
                buffer="game",
                volume=volume,
                priority=priority,
                max_instances=max_instances,
                position=position,
                attenuation=curve,
            )

    @staticmethod
    def _play_variant(
        user: User,
        family: str,
        assets: tuple[str, ...],
        **kwargs: object,
    ) -> None:
        if family:
            user.play_sound_family(family, **kwargs)
        elif assets:
            user.play_sound(assets[0], **kwargs)

    def _play_layered_report_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
        source: GridPoint,
        *,
        actor_id: str,
        close_family: str,
        close_assets: tuple[str, ...],
        distant_family: str,
        distant_assets: tuple[str, ...],
        source_height_meters: float,
        priority: int,
        max_instances: int,
    ) -> None:
        """Play a near report plus its distance bed, or only the distance bed."""

        listener_point, _ = self._audio_listener_frame(listener)
        distance = world_distance_meters(
            listener_point,
            source,
            self.tactical_map.grid_unit_meters,
        )
        if listener.id == actor_id:
            position = None
            close_curve = None
            distant_curve = None
        else:
            position = self._relative_audio_position(
                listener,
                source,
                source_height_meters=source_height_meters,
            )
            close_curve = POSITIONAL_ATTENUATION
            distant_curve = DISTANT_ATTENUATION
        common = {
            "buffer": "game",
            "priority": priority,
            "max_instances": max_instances,
            "position": position,
        }
        if distance < DISTANT_REPORT_THRESHOLD_METERS:
            self._play_variant(
                user,
                close_family,
                close_assets,
                attenuation=close_curve,
                **common,
            )
        self._play_variant(
            user,
            distant_family,
            distant_assets,
            volume=DISTANT_LAYER_VOLUME,
            attenuation=distant_curve,
            **common,
        )

    def _play_weapon_bullet_audio(
        self,
        shooter: BreachPointPlayer,
        target: BreachPointPlayer,
        weapon: WeaponProfile,
        *,
        shot_index: int,
        rounds_on_target: int,
        rounds_evaded: int,
        health_damage: int,
        armor_absorbed: int,
        lethal: bool = False,
        target_had_armor: bool = False,
    ) -> None:
        """Emit one report and its corresponding projectile/impact event."""

        profile = WEAPON_AUDIO_PROFILES.get(weapon.id)
        if not profile:
            return
        source = self._player_grid_point(shooter)
        destination = self._player_grid_point(target)
        close_report_asset = self._spatial_rng.choice(profile.fire_close_assets)
        projectile_asset = self._spatial_rng.choice(profile.projectile_assets)
        hit_target = (
            shot_index < rounds_on_target and shot_index >= rounds_evaded
        )
        projectile_destination = (
            destination
            if hit_target
            else self._projectile_pass_point(source, destination, shooter.facing_degrees)
        )
        impact_asset = ""
        if hit_target:
            if armor_absorbed:
                impact_asset = IMPACT_ARMOR_ASSET
            elif health_damage:
                impact_asset = self._spatial_rng.choice(IMPACT_FLESH_ASSETS)
            else:
                impact_asset = self._spatial_rng.choice(
                    profile.projectile_impact_assets
                )
        else:
            impact_asset = self._spatial_rng.choice(profile.projectile_impact_assets)
        terminal_lethal_hit = (
            lethal and hit_target and shot_index == rounds_on_target - 1
        )
        if terminal_lethal_hit:
            impact_asset = self._spatial_rng.choice(
                HEADSHOT_ASSETS_BY_ARMOR[target_had_armor]
            )
        death_assets = self._death_audio_assets(target) if terminal_lethal_hit else None

        for listener, user in self._audio_listeners():
            fire_layer_gain = WEAPON_FIRE_LAYER_GAINS_BY_CLIENT.get(
                get_client_type(user),
                1.0,
            )
            listener_point, _ = self._audio_listener_frame(listener)
            distance = world_distance_meters(
                listener_point,
                source,
                self.tactical_map.grid_unit_meters,
            )
            if listener.id == shooter.id:
                report_position = None
                close_curve = None
                distant_curve = None
            else:
                report_position = self._relative_audio_position(
                    listener,
                    source,
                    source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                )
                close_curve = POSITIONAL_ATTENUATION
                distant_curve = DISTANT_ATTENUATION
            segments: list[AudioSequenceSegment] = []
            if distance < DISTANT_REPORT_THRESHOLD_METERS:
                segments.append(
                    AudioSequenceSegment(
                        close_report_asset,
                        position=report_position,
                        attenuation=close_curve,
                        gain=fire_layer_gain,
                        next_start_ratio=0.0,
                    )
                )
            segments.append(
                AudioSequenceSegment(
                    profile.fire_distant,
                    position=report_position,
                    attenuation=distant_curve,
                    gain=(DISTANT_LAYER_VOLUME / 100) * fire_layer_gain,
                    next_start_ratio=0.0,
                )
            )
            trajectory_start = self._relative_audio_position(
                listener,
                source,
                source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
            )
            trajectory_end = self._relative_audio_position(
                listener,
                projectile_destination,
                source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
            )
            segments.append(
                AudioSequenceSegment(
                    projectile_asset,
                    position=trajectory_start,
                    destination_position=trajectory_end,
                    attenuation=POSITIONAL_ATTENUATION,
                    gain=fire_layer_gain,
                    # CS resolves the bullet trace, impact, and tracer/whiz as
                    # one shot event. The authored flyby tail is presentation,
                    # not ballistic travel time, so it must not delay impact.
                    next_start_ratio=0.0,
                )
            )
            if impact_asset:
                impact_point = destination if hit_target else projectile_destination
                segments.append(
                    AudioSequenceSegment(
                        impact_asset,
                        position=self._relative_audio_position(
                            listener,
                            impact_point,
                            source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                        ),
                        attenuation=POSITIONAL_ATTENUATION,
                        gain=fire_layer_gain,
                        next_start_ratio=0.0 if death_assets else 1.0,
                    )
                )
            if death_assets:
                death_voice, body_fall = death_assets
                if listener.id == target.id:
                    voice_position = None
                    body_position = None
                    death_curve = None
                else:
                    voice_position = self._relative_audio_position(
                        listener,
                        destination,
                        source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                    )
                    body_position = self._relative_audio_position(
                        listener,
                        destination,
                        source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                    )
                    death_curve = POSITIONAL_ATTENUATION
                segments.extend(
                    (
                        AudioSequenceSegment(
                            death_voice,
                            position=voice_position,
                            attenuation=death_curve,
                        ),
                        AudioSequenceSegment(
                            body_fall,
                            position=body_position,
                            attenuation=death_curve,
                        ),
                    )
                )
            user.play_sound_chain(
                segments,
                buffer="game",
                priority=WEAPON_PROJECTILE_PRIORITY,
                max_instances=48,
            )

        self._play_casing_audio(shooter, profile)

    def _play_casing_audio(
        self,
        shooter: BreachPointPlayer,
        profile: WeaponAudioProfile,
    ) -> None:
        """Drop a caliber- and ground-specific casing at the muzzle position."""

        node = self._node(shooter.position_id)
        surface = node.footstep_surface if node else "sand"
        family = CASING_FAMILIES_BY_CALIBER_AND_SURFACE.get(
            profile.casing_caliber,
            {},
        ).get(surface)
        if family:
            self._play_spatial_family(
                family,
                self._player_grid_point(shooter),
                actor_id=shooter.id,
                source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                volume=42,
                priority=18,
                max_instances=12,
            )

    @staticmethod
    def _projectile_pass_point(
        source: GridPoint,
        target: GridPoint,
        fallback_heading_degrees: int,
    ) -> GridPoint:
        """Extend a miss beyond its target so the flyby audibly passes the listener."""

        delta_x = target.x - source.x
        delta_y = target.y - source.y
        distance = math.hypot(delta_x, delta_y)
        if distance:
            unit_x = delta_x / distance
            unit_y = delta_y / distance
        else:
            heading = math.radians(fallback_heading_degrees % 360)
            unit_x = math.sin(heading)
            unit_y = math.cos(heading)
        point = GridPoint(
            round(target.x + unit_x * BULLET_MISS_OVERSHOOT_GRID_UNITS),
            round(target.y + unit_y * BULLET_MISS_OVERSHOOT_GRID_UNITS),
        )
        if point != target:
            return point
        if abs(unit_x) >= abs(unit_y):
            return GridPoint(target.x + (1 if unit_x >= 0 else -1), target.y)
        return GridPoint(target.x, target.y + (1 if unit_y >= 0 else -1))

    def _play_death_audio(self, target: BreachPointPlayer) -> None:
        """Start one spatial death cry, then the correct surface body fall."""

        source = self._player_grid_point(target)
        death_assets = self._death_audio_assets(target)
        if not death_assets:
            return
        death_voice, body_fall = death_assets
        for listener, user in self._audio_listeners():
            if listener.id == target.id:
                voice_position = None
                body_position = None
                curve = None
            else:
                voice_position = self._relative_audio_position(
                    listener,
                    source,
                    source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                )
                body_position = self._relative_audio_position(
                    listener,
                    source,
                    source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                )
                curve = POSITIONAL_ATTENUATION
            user.play_sound_chain(
                [
                    AudioSequenceSegment(
                        death_voice,
                        position=voice_position,
                        attenuation=curve,
                    ),
                    AudioSequenceSegment(
                        body_fall,
                        position=body_position,
                        attenuation=curve,
                    ),
                ],
                buffer="game",
                priority=80,
                max_instances=10,
            )

    def _death_audio_assets(
        self,
        target: BreachPointPlayer,
    ) -> tuple[str, str] | None:
        """Choose one coherent death voice/body pair for every listener."""

        node = self._node(target.position_id)
        surface = node.footstep_surface if node else "sand"
        body_fall_assets = BODY_FALL_ASSETS_BY_SURFACE.get(surface)
        if not body_fall_assets:
            return None
        return (
            self._spatial_rng.choice(DEATH_VOICE_ASSETS),
            self._spatial_rng.choice(body_fall_assets),
        )

    def _play_weapon_equip_audio(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> None:
        profile = WEAPON_AUDIO_PROFILES.get(weapon.id)
        if profile:
            self._play_spatial_asset(
                profile.equip_asset,
                self._player_grid_point(player),
                actor_id=player.id,
                volume=80,
                priority=20,
            )

    def _play_weapon_drop_audio(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
        dropped_weapon: DroppedWeapon,
    ) -> None:
        """Emit category-correct drop Foley at the weapon's ground position."""

        profile = WEAPON_AUDIO_PROFILES.get(weapon.id)
        if not profile:
            return
        self._play_spatial_asset(
            profile.drop_asset,
            GridPoint(dropped_weapon.grid_x, dropped_weapon.grid_y),
            actor_id=player.id,
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
            volume=88,
            priority=22,
        )

    def _play_weapon_reload_audio(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
        loaded_rounds: int,
    ) -> None:
        profile = WEAPON_AUDIO_PROFILES.get(weapon.id)
        if not profile:
            return
        if profile.shell_reload_assets:
            insert_assets = profile.shell_reload_assets[:-1]
            assets = tuple(
                insert_assets[index % len(insert_assets)]
                for index in range(max(1, loaded_rounds))
            ) + (profile.shell_reload_assets[-1],)
        else:
            assets = profile.reload_assets
        source = self._player_grid_point(player)
        for listener, user in self._audio_listeners():
            spatialization = self._listener_spatialization(
                listener,
                source,
                actor_id=player.id,
                source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                attenuation=POSITIONAL_ATTENUATION,
            )
            if spatialization is None:
                continue
            position, curve = spatialization
            user.play_sound_chain(
                [
                    AudioSequenceSegment(
                        asset,
                        position=position,
                        attenuation=curve,
                    )
                    for asset in assets
                ],
                buffer="game",
                priority=25,
                max_instances=4,
            )

    def _play_hold_angle_audio(
        self,
        player: BreachPointPlayer,
        weapon: WeaponProfile,
    ) -> None:
        profile = WEAPON_AUDIO_PROFILES.get(weapon.id)
        if profile and profile.hold_asset:
            self._play_spatial_asset(
                profile.hold_asset,
                self._player_grid_point(player),
                actor_id=player.id,
                volume=75,
                priority=20,
            )

    def _play_utility_audio(
        self,
        thrower: BreachPointPlayer,
        utility: UtilityProfile,
        destination_node_id: str,
    ) -> None:
        for listener, user in self._audio_listeners():
            self._play_utility_handling_for_listener(
                listener,
                user,
                thrower,
                utility,
                destination_node_id,
            )

    def _play_utility_handling_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
        thrower: BreachPointPlayer,
        utility: UtilityProfile,
        destination_node_id: str,
    ) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility.id)
        destination_node = self._node(destination_node_id)
        if not profile or not destination_node:
            return
        source = self._player_grid_point(thrower)
        spatialization = self._listener_spatialization(
            listener,
            source,
            actor_id=thrower.id,
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            attenuation=POSITIONAL_ATTENUATION,
        )
        if spatialization is None:
            return
        source_position, source_curve = spatialization
        segments = [
            AudioSequenceSegment(
                asset,
                position=source_position,
                attenuation=source_curve,
            )
            for asset in (
                profile.draw_asset,
                *profile.pin_assets,
            )
            if asset
        ]
        user.play_sound_chain(
            segments,
            buffer="game",
            priority=55,
            max_instances=8,
        )

    def _play_utility_release(
        self,
        thrower: BreachPointPlayer,
        utility: UtilityProfile,
    ) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility.id)
        if not profile or not profile.release_asset:
            return
        self._play_spatial_asset(
            profile.release_asset,
            self._player_grid_point(thrower),
            actor_id=thrower.id,
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            volume=100,
            priority=55,
        )

    @staticmethod
    def _utility_flight_audio_handle(sequence_id: str) -> str:
        return f"{UTILITY_FLIGHT_HANDLE_PREFIX}{sequence_id}"

    def _start_utility_flight_audio(
        self,
        sequence_id: str,
        thrower: BreachPointPlayer,
        utility: UtilityProfile,
        destination_node_id: str,
        duration_ticks: int,
    ) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility.id)
        destination_node = self._node(destination_node_id)
        if not profile or not profile.flight_asset or not destination_node:
            return
        source = self._player_grid_point(thrower)
        destination = destination_node.anchor
        duration_ms = max(1, math.ceil(duration_ticks * 1000 / TICKS_PER_SECOND))
        handle = self._utility_flight_audio_handle(sequence_id)
        for listener, _ in self._audio_listeners():
            if not self._listener_can_hear_path(
                listener,
                source,
                destination,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                attenuation=POSITIONAL_ATTENUATION,
            ):
                continue
            origin_position = self._relative_audio_position(
                listener,
                source,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            )
            destination_position = self._relative_audio_position(
                listener,
                destination,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            )
            self.play_sound(
                profile.flight_asset,
                loop=True,
                handle=handle,
                audience=listener,
                persist=True,
                volume=88,
                priority=55,
                max_instances=4,
                position=origin_position,
                attenuation=POSITIONAL_ATTENUATION,
            )
            self.move_sound(
                handle,
                destination_position,
                duration_ms,
                audience=listener,
                easing="ease-out",
            )

    def _stop_utility_flight_audio(self, sequence_id: str) -> None:
        handle = self._utility_flight_audio_handle(sequence_id)
        if any(
            state.kind == "sfx" and state.handle == handle
            for state in self.active_audio.values()
        ):
            self.stop_sound(handle)

    def _stop_all_utility_flight_audio(self) -> None:
        handles = {
            state.handle
            for state in self.active_audio.values()
            if state.kind == "sfx"
            and state.handle.startswith(UTILITY_FLIGHT_HANDLE_PREFIX)
        }
        for handle in handles:
            self.stop_sound(handle)

    def _play_utility_bounce(self, utility_id: str, point: GridPoint) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility_id)
        if not profile or not profile.bounce_asset:
            return
        self._play_spatial_asset(
            profile.bounce_asset,
            point,
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
            volume=86,
            priority=52,
        )

    def _play_utility_impact(self, utility_id: str, destination_node_id: str) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility_id)
        node = self._node(destination_node_id)
        if not profile or not profile.landing_asset or not node:
            return
        self._play_spatial_asset(
            profile.landing_asset,
            node.anchor,
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
            volume=90,
            priority=56,
        )

    def _play_utility_detonation(
        self,
        utility_id: str,
        destination_node_id: str,
    ) -> None:
        profile = UTILITY_AUDIO_PROFILES.get(utility_id)
        destination_node = self._node(destination_node_id)
        if not profile or not destination_node:
            return
        destination = destination_node.anchor
        for listener, user in self._audio_listeners():
            self._play_utility_detonation_for_listener(
                listener,
                user,
                profile,
                destination,
            )

    def _play_utility_detonation_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
        profile: UtilityAudioProfile,
        destination: GridPoint,
    ) -> None:
        self._play_layered_report_for_listener(
            listener,
            user,
            destination,
            actor_id="",
            close_family=profile.detonate_close_family,
            close_assets=profile.detonate_close_assets,
            distant_family=profile.detonate_distant_family,
            distant_assets=profile.detonate_distant_assets,
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            priority=72,
            max_instances=12,
        )
        listener_point, _ = self._audio_listener_frame(listener)
        if profile.detonate_overlays_near_only and (
            world_distance_meters(
                listener_point,
                destination,
                self.tactical_map.grid_unit_meters,
            )
            >= DISTANT_REPORT_THRESHOLD_METERS
        ):
            return
        for asset in profile.detonate_overlay_assets:
            self._play_spatial_asset_for_listener(
                listener,
                user,
                asset,
                destination,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                volume=86,
                priority=73,
            )
        if profile.detonate_overlay_variants:
            kwargs = {
                "buffer": "game",
                "volume": 86,
                "priority": 73,
                "max_instances": 12,
                "position": self._relative_audio_position(
                    listener,
                    destination,
                    source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                ),
                "attenuation": POSITIONAL_ATTENUATION,
            }
            self._play_variant(
                user,
                profile.detonate_overlay_family,
                profile.detonate_overlay_variants,
                **kwargs,
            )

    def _play_bomb_audio(
        self,
        asset: str,
        node_id: str,
        *,
        actor_id: str = "",
        volume: int = 100,
        priority: int = 70,
        source: GridPoint | None = None,
    ) -> None:
        node = self._node(node_id)
        if node:
            self._play_spatial_asset(
                asset,
                source or node.anchor,
                actor_id=actor_id,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                volume=volume,
                priority=priority,
            )

    def _play_bomb_plant_audio(self, planter: BreachPointPlayer) -> None:
        """Start spatial plant foley and one coherent low-volume keypad sequence."""

        source = self._player_grid_point(planter)
        self._play_bomb_audio(
            BOMB_PLANT_INITIATE_ASSET,
            planter.position_id,
            actor_id=planter.id,
            volume=80,
            source=source,
        )
        press_count = self._spatial_rng.randint(*BOMB_KEYPAD_PRESS_COUNT_RANGE)
        keypad_assets: list[str] = []
        for _ in range(press_count):
            candidates = tuple(
                asset
                for asset in BOMB_KEYPAD_ASSETS
                if not keypad_assets or asset != keypad_assets[-1]
            )
            keypad_assets.append(self._spatial_rng.choice(candidates))
        for listener, user in self._audio_listeners():
            spatialization = self._listener_spatialization(
                listener,
                source,
                actor_id=planter.id,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                attenuation=POSITIONAL_ATTENUATION,
            )
            if spatialization is None:
                continue
            position, curve = spatialization
            user.play_sound_chain(
                [
                    AudioSequenceSegment(
                        asset,
                        position=position,
                        attenuation=curve,
                    )
                    for asset in keypad_assets
                ],
                buffer="game",
                volume=30,
                priority=64,
                max_instances=1,
            )

    def _play_bomb_planted_audio(
        self,
        planter: BreachPointPlayer,
        source: GridPoint,
    ) -> None:
        """Play only the physical placement confirmation at plant completion."""

        self._play_bomb_audio(
            BOMB_PLANT_QUIET_ASSET,
            planter.position_id,
            actor_id=planter.id,
            volume=40,
            priority=76,
            source=source,
        )

    def _play_bomb_detonation_warning_audio(self, source: GridPoint) -> None:
        """Play the irreversible CS-style device warning before detonation."""

        for listener, user in self._audio_listeners():
            position = self._relative_audio_position(
                listener,
                source,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            )
            user.play_sound_chain(
                [
                    AudioSequenceSegment(
                        BOMB_NVG_ON_ASSET,
                        position=position,
                        attenuation=POSITIONAL_ATTENUATION,
                        next_start_ratio=BOMB_ARM_START_RATIO,
                    ),
                    AudioSequenceSegment(
                        BOMB_ARM_ASSET,
                        position=position,
                        attenuation=POSITIONAL_ATTENUATION,
                    ),
                ],
                buffer="game",
                priority=76,
                max_instances=1,
            )

    def _play_item_pickup_audio(
        self,
        player: BreachPointPlayer,
        *item_kinds: str,
        local_only: bool,
    ) -> None:
        """Play local purchase feedback or an audible world pickup sequence."""

        kinds = tuple(
            item_kind
            for item_kind in item_kinds
            if item_kind in PICKUP_ASSETS or item_kind == "defuse_kit"
        )
        if not kinds:
            return
        if len(kinds) == 1:
            item_kind = kinds[0]
            if local_only:
                user = self.get_user(player)
                if not user:
                    return
                if item_kind == "defuse_kit":
                    user.play_sound(
                        PICKUP_DEFUSE_KIT_ASSET,
                        buffer="game",
                        priority=24,
                        max_instances=2,
                    )
                else:
                    user.play_sound_family(
                        PICKUP_FAMILIES[item_kind],
                        buffer="game",
                        priority=24,
                        max_instances=2,
                    )
                return
            if item_kind == "defuse_kit":
                self._play_spatial_asset(
                    PICKUP_DEFUSE_KIT_ASSET,
                    self._player_grid_point(player),
                    actor_id=player.id,
                    priority=24,
                )
            else:
                self._play_spatial_family(
                    PICKUP_FAMILIES[item_kind],
                    self._player_grid_point(player),
                    actor_id=player.id,
                    priority=24,
                    max_instances=4,
                )
            return

        selected_assets = tuple(
            PICKUP_DEFUSE_KIT_ASSET
            if item_kind == "defuse_kit"
            else self._spatial_rng.choice(PICKUP_ASSETS[item_kind])
            for item_kind in kinds
        )
        if local_only:
            user = self.get_user(player)
            if user:
                user.play_sound_chain(
                    [AudioSequenceSegment(asset) for asset in selected_assets],
                    buffer="game",
                    priority=24,
                    max_instances=2,
                )
            return

        source = self._player_grid_point(player)
        for listener, user in self._audio_listeners():
            spatialization = self._listener_spatialization(
                listener,
                source,
                actor_id=player.id,
                source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
                attenuation=POSITIONAL_ATTENUATION,
            )
            if spatialization is None:
                continue
            position, curve = spatialization
            user.play_sound_chain(
                [
                    AudioSequenceSegment(
                        asset,
                        position=position,
                        attenuation=curve,
                    )
                    for asset in selected_assets
                ],
                buffer="game",
                priority=24,
                max_instances=4,
            )

    def _play_bomb_pickup_audio(self, player: BreachPointPlayer) -> None:
        """Play CS-style weapon pickup Foley with its quiet C4 child beep."""

        self._play_item_pickup_audio(player, "weapon", local_only=False)
        self._play_spatial_asset(
            self._spatial_rng.choice(BOMB_PICKUP_BEEP_ASSETS),
            self._player_grid_point(player),
            actor_id=player.id,
            source_height_meters=UTILITY_SOURCE_HEIGHT_METERS,
            volume=3,
            priority=25,
        )

    def _play_utility_purchase_audio(
        self,
        player: BreachPointPlayer,
        utility: UtilityProfile,
    ) -> None:
        """Use the utility audio profile to select its local inventory cue."""

        profile = UTILITY_AUDIO_PROFILES.get(utility.id)
        if profile:
            self._play_item_pickup_audio(
                player,
                profile.pickup_kind,
                local_only=True,
            )

    def _play_equipment_purchase_audio(
        self,
        player: BreachPointPlayer,
        equipment: EquipmentProfile,
    ) -> None:
        """Use the equipment registry to select its local inventory cue."""

        pickup_kind = EQUIPMENT_PICKUP_KINDS.get(equipment.id)
        if pickup_kind:
            self._play_item_pickup_audio(
                player,
                pickup_kind,
                local_only=True,
            )

    def _play_global_asset(
        self,
        asset: str,
        *,
        handle: str = "",
        volume: int = 100,
        priority: int = 0,
        max_instances: int = 0,
    ) -> None:
        """Play one non-spatial event at every listener's local position."""

        for _, user in self._audio_listeners():
            user.play_sound(
                asset,
                handle=handle,
                buffer="game",
                volume=volume,
                priority=priority,
                max_instances=max_instances,
            )

    def _play_global_audio_chain(
        self,
        assets: tuple[str, ...],
        *,
        priority: int = 0,
    ) -> None:
        """Play an ordered, non-spatial radio sequence for the whole table."""

        if assets:
            self.play_sound_chain(
                [AudioSequenceSegment(asset) for asset in assets],
                handle=RADIO_CUE_HANDLE,
                buffer="game",
                bus="radio",
                priority=priority,
                max_instances=1,
            )

    def _stop_music_cues(self, *, fade_ms: int = 0) -> None:
        """Retire every Breach Point BGM layer without touching ambience."""

        self.cancel_sequences_by_tag(MUSIC_ACTION_STOP_SEQUENCE_TAG)
        for handle in (
            MUSIC_CONTEXT_HANDLE,
            MUSIC_RESULT_HANDLE,
        ):
            self.stop_music(handle=handle, fade_ms=fade_ms)

    def _stop_round_tail_audio(self) -> None:
        """Cut finite round-end handles before the new round is prepared."""

        self._stop_music_cues()
        for _, user in self._audio_listeners():
            user.stop_sound(RADIO_CUE_HANDLE)
            user.stop_sound(BOMB_EXPLOSION_HANDLE)

    def _play_music_cue(
        self,
        asset: str,
        *,
        looping: bool,
        priority: int,
    ) -> None:
        """Crossfade the main CS music context on the BGM channel."""

        self.cancel_sequences_by_tag(MUSIC_ACTION_STOP_SEQUENCE_TAG)
        self.play_music(
            asset,
            looping=looping,
            handle=MUSIC_CONTEXT_HANDLE,
            bus="music",
            fade_in_ms=MUSIC_CROSSFADE_MS,
            fade_out_ms=MUSIC_CROSSFADE_MS,
            priority=priority,
        )

    def _play_action_start_music(self) -> None:
        self._play_music_cue(
            self._spatial_rng.choice(MUSIC_ACTION_START_ASSETS),
            looping=True,
            priority=30,
        )

    def _play_round_stinger(self, asset: str, *, priority: int) -> None:
        """Overlay one finite, non-spatial round stinger on the SFX channel."""

        self._play_global_asset(
            asset,
            handle=ROUND_STINGER_HANDLE,
            volume=60,
            priority=priority,
            max_instances=1,
        )

    def _play_round_result_music(self, winning_squad_index: int) -> None:
        """Give competitors their win/loss cue and spectators the result cue."""

        self.cancel_sequences_by_tag(MUSIC_ACTION_STOP_SEQUENCE_TAG)
        self.stop_music(
            handle=MUSIC_CONTEXT_HANDLE,
            fade_ms=MUSIC_CROSSFADE_MS,
        )
        for _, user in self._audio_listeners():
            user.stop_sound(ROUND_STINGER_HANDLE)
        for listener, _ in self._audio_listeners():
            asset = (
                MUSIC_ROUND_WON_ASSET
                if listener.is_spectator
                or listener.squad_index == winning_squad_index
                else MUSIC_ROUND_LOST_ASSET
            )
            self.play_music(
                asset,
                looping=False,
                handle=MUSIC_RESULT_HANDLE,
                bus="music",
                fade_in_ms=MUSIC_CROSSFADE_MS,
                fade_out_ms=MUSIC_CROSSFADE_MS,
                priority=40,
                audience=listener,
            )

    @staticmethod
    def _fire_audio_handle(node_id: str) -> str:
        return f"breachpoint.fire.{node_id}"

    def _start_fire_audio(self, node_id: str) -> None:
        for listener, _ in self._audio_listeners():
            self._start_fire_audio_for_listener(node_id, listener)

    def _start_fire_audio_for_listener(
        self,
        node_id: str,
        listener: BreachPointPlayer,
    ) -> None:
        node = self._node(node_id)
        if not node:
            return
        position = self._relative_audio_position(
            listener,
            node.anchor,
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
        )
        self.play_ambience(
            FIRE_LOOP_ASSET,
            outro=FIRE_OUTRO_ASSET,
            handle=self._fire_audio_handle(node_id),
            audience=listener,
            scope="player",
            context=listener.id,
            layer=f"{FIRE_LAYER_PREFIX}{node_id}",
            fade_in_ms=0,
            fade_out_ms=0,
            volume=80,
            priority=50,
            position=position,
            attenuation=FIRE_ATTENUATION,
        )

    def _stop_fire_audio(self, node_id: str, *, extinguished: bool = False) -> None:
        handle = self._fire_audio_handle(node_id)
        if extinguished:
            self._play_fire_extinguish_audio(node_id)
        if not any(
            state.kind == "ambience" and state.handle == handle
            for state in self.active_audio.values()
        ):
            return
        self.stop_ambience(
            handle=handle,
            fade_ms=0,
            play_outro=not extinguished,
            outro_mode="immediate",
        )

    def _play_fire_extinguish_audio(self, node_id: str) -> None:
        node = self._node(node_id)
        if node:
            self._play_spatial_asset(
                FIRE_EXTINGUISH_ASSET,
                node.anchor,
                source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                priority=65,
            )

    def _play_fire_damage_audio(self, player: BreachPointPlayer) -> None:
        source = self._player_grid_point(player)
        for listener, user in self._audio_listeners():
            spatialization = self._listener_spatialization(
                listener,
                source,
                actor_id=player.id,
                source_height_meters=WEAPON_SOURCE_HEIGHT_METERS,
                attenuation=POSITIONAL_ATTENUATION,
            )
            if spatialization is None:
                continue
            position, curve = spatialization
            user.play_sound_family(
                FIRE_DAMAGE_FAMILY,
                buffer="game",
                priority=68,
                max_instances=5,
                position=position,
                attenuation=curve,
            )

    def _play_flash_tinnitus_audio(self, player: BreachPointPlayer) -> None:
        user = self.get_user(player)
        if user:
            user.play_sound(
                FLASH_TINNITUS_ASSET,
                buffer="game",
                priority=78,
                max_instances=1,
            )

    def _move_area_effect_audio_for_listener(
        self,
        listener: BreachPointPlayer,
        destination: GridPoint,
        destination_heading: int,
        duration_ms: int,
    ) -> None:
        for effect in self.area_effects:
            if effect.effect != "fire":
                continue
            handle = self._fire_audio_handle(effect.node_id)
            node = self._node(effect.node_id)
            if not node or not any(
                state.kind == "ambience"
                and state.handle == handle
                and listener.id in state.recipient_ids
                for state in self.active_audio.values()
            ):
                continue
            relative_destination = self._relative_audio_position(
                listener,
                node.anchor,
                source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                listener_point=destination,
                listener_heading=destination_heading,
            )
            self.move_ambience(
                handle,
                relative_destination,
                duration_ms,
                audience=listener,
            )

    def _start_map_ambience(self) -> None:
        self._initialize_ambient_stinger_schedule()
        self._sync_all_listener_environment_audio()

    def _initialize_ambient_stinger_schedule(self) -> None:
        valid_ids = {emitter.id for emitter in self.tactical_map.ambient_emitters}
        self.ambient_stinger_due_ticks = {
            emitter_id: due_tick
            for emitter_id, due_tick in self.ambient_stinger_due_ticks.items()
            if emitter_id in valid_ids and due_tick > self.sound_scheduler_tick
        }
        for emitter in self.tactical_map.ambient_emitters:
            if emitter.id not in self.ambient_stinger_due_ticks:
                self._schedule_ambient_stinger(emitter.id)

    def _schedule_ambient_stinger(self, emitter_id: str) -> None:
        emitter = next(
            (
                candidate
                for candidate in self.tactical_map.ambient_emitters
                if candidate.id == emitter_id
            ),
            None,
        )
        if not emitter:
            self.ambient_stinger_due_ticks.pop(emitter_id, None)
            return
        delay_seconds = self._spatial_rng.randint(
            emitter.minimum_interval_seconds,
            emitter.maximum_interval_seconds,
        )
        self.ambient_stinger_due_ticks[emitter.id] = (
            self.sound_scheduler_tick + delay_seconds * TICKS_PER_SECOND
        )

    def _process_ambient_stingers(self) -> None:
        if self.status != "playing":
            return
        for emitter in self.tactical_map.ambient_emitters:
            due_tick = self.ambient_stinger_due_ticks.get(emitter.id)
            if due_tick is None:
                self._schedule_ambient_stinger(emitter.id)
                continue
            if due_tick > self.sound_scheduler_tick:
                continue
            for listener, user in self._audio_listeners():
                node = self._audio_listener_node(listener)
                if emitter.audible_node_ids and (
                    not node or node.id not in emitter.audible_node_ids
                ):
                    continue
                position = self._relative_audio_position(
                    listener,
                    emitter.position,
                    source_height_meters=emitter.source_height_meters,
                )
                kwargs = {
                    "buffer": "game",
                    "volume": emitter.volume,
                    "priority": 3,
                    "max_instances": 2,
                    "position": position,
                    "attenuation": POSITIONAL_ATTENUATION,
                }
                self._play_variant(user, emitter.family, emitter.assets, **kwargs)
            self._schedule_ambient_stinger(emitter.id)

    def _audio_listener_node(
        self,
        listener: BreachPointPlayer,
    ) -> TacticalNode | None:
        if not listener.is_spectator:
            return self._node(listener.position_id)
        point = self.tactical_map.spectator_anchor
        return next(
            (
                candidate
                for candidate in self.tactical_map.nodes
                if candidate.footprint.contains(point)
            ),
            None,
        )

    def _sync_all_listener_environment_audio(self) -> None:
        for player in self.players:
            listener = self._breach_player(player)
            if listener:
                self._sync_listener_environment_audio(listener)

    def _sync_listener_environment_audio(
        self,
        listener: BreachPointPlayer,
    ) -> None:
        node = self._audio_listener_node(listener)
        zone_id = node.acoustic_zone if node else ""
        zone_ambience = next(
            (layer for layer in self.tactical_map.zone_ambience if layer.id == zone_id),
            None,
        )
        ambience = zone_ambience or self.tactical_map.global_ambience
        desired_handle = (
            MAP_ZONE_AMBIENCE_HANDLE if zone_ambience else MAP_AMBIENCE_HANDLE
        )
        other_handle = (
            MAP_AMBIENCE_HANDLE if zone_ambience else MAP_ZONE_AMBIENCE_HANDLE
        )
        other_states = [
            state
            for state in self.active_audio.values()
            if state.kind == "ambience"
            and state.handle == other_handle
            and listener.id in state.recipient_ids
        ]
        if other_states:
            self.stop_ambience(
                handle=other_handle,
                fade_ms=600,
                play_outro=False,
                audience=listener,
            )
        active_states = [
            state
            for state in self.active_audio.values()
            if state.kind == "ambience"
            and state.handle == desired_handle
            and listener.id in state.recipient_ids
        ]
        if ambience and any(state.asset == ambience.asset for state in active_states):
            return
        if active_states:
            self.stop_ambience(
                handle=desired_handle,
                fade_ms=600,
                play_outro=False,
                audience=listener,
            )
        if ambience:
            self.play_ambience(
                ambience.asset,
                handle=desired_handle,
                audience=listener,
                scope="player",
                context=listener.id,
                layer="environment" if zone_ambience else "map",
                fade_in_ms=600,
                fade_out_ms=600,
                volume=ambience.volume,
                priority=4,
            )

    def _play_movement_audio(
        self,
        mover: BreachPointPlayer,
        origin: GridPoint,
        destination: GridPoint,
        assets: tuple[str, ...],
        next_start_ratio: float,
    ) -> None:
        for listener, user in self._audio_listeners():
            self._play_movement_audio_for_listener(
                listener,
                user,
                mover,
                origin,
                destination,
                assets,
                next_start_ratio,
            )

    def _play_movement_audio_for_listener(
        self,
        listener: BreachPointPlayer,
        user: User,
        mover: BreachPointPlayer,
        origin: GridPoint,
        destination: GridPoint,
        assets: tuple[str, ...],
        next_start_ratio: float,
    ) -> None:
        segment_count = len(assets)
        if not segment_count:
            return
        if listener.id != mover.id and not self._listener_can_hear_path(
            listener,
            origin,
            destination,
            source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
            attenuation=FOOTSTEP_ATTENUATION,
        ):
            return
        segments: list[AudioSequenceSegment] = []
        for index, asset in enumerate(assets):
            start_ratio = index / segment_count
            end_ratio = (index + 1) / segment_count
            start = GridPoint(
                round(origin.x + (destination.x - origin.x) * start_ratio),
                round(origin.y + (destination.y - origin.y) * start_ratio),
            )
            end = GridPoint(
                round(origin.x + (destination.x - origin.x) * end_ratio),
                round(origin.y + (destination.y - origin.y) * end_ratio),
            )
            if listener.id == mover.id:
                position = None
                destination_position = None
                curve = None
            else:
                position = self._relative_audio_position(
                    listener,
                    start,
                    source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                )
                destination_position = self._relative_audio_position(
                    listener,
                    end,
                    source_height_meters=FOOTSTEP_SOURCE_HEIGHT_METERS,
                )
                curve = FOOTSTEP_ATTENUATION
            segments.append(
                AudioSequenceSegment(
                    asset,
                    position=position,
                    destination_position=destination_position,
                    attenuation=curve,
                    next_start_ratio=next_start_ratio,
                )
            )
        user.play_sound_chain(
            segments,
            buffer="game",
            pitch=100,
            priority=35,
            max_instances=4,
        )
