"""Centralized sound routing and measured timing for BANG!."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path, PurePosixPath

from ...game_utils.audio_duration import measure_audio_duration_ticks
from . import cards

TICKS_PER_SECOND = 20
GAME_START_DELAY_TICKS = 10 * TICKS_PER_SECOND

# Playback overlap profiles. SequenceBeat scales these ratios against each
# asset's measured duration, so replacement files automatically keep the same
# pacing intent without fixed inter-cue delays.
WAIT_RATIO_LONG_EFFECT = 0.10
WAIT_RATIO_GUNSHOT = 0.15
WAIT_RATIO_CASING = 0.15
WAIT_RATIO_BARRAGE_LEAD = 0.00
WAIT_RATIO_REACTION = 0.10
# Failed Barrel cues have a long, dense break transient that can mask the
# following body impact. Let that transient clear while retaining tail overlap.
WAIT_RATIO_FAILED_DEFENSE = 0.55
WAIT_RATIO_IMPACT = 0.10
WAIT_RATIO_SHORT_CUE = 0.05
WAIT_RATIO_FULL_CUE = 1.00
LETHAL_FALL_TRIGGER_RATIO = 0.30

# SequenceRunner ticks at 20 Hz, so one or two ticks gives Saloon a compact
# 50-100 ms human stagger while remaining save/load deterministic.
SALOON_STAGGER_MIN_TICKS = 1
SALOON_STAGGER_MAX_TICKS = 2
SALOON_PAN_LEFT = -70
SALOON_PAN_RIGHT = 70
# Consecutive eliminations keep their falls 50 ms apart without blocking the
# rules interpreter or depending on the duration of any fall asset.
ELIMINATION_FALL_STAGGER_TICKS = 1

SOUND_CARD_DRAW = tuple(f"game_cards/draw{index}.ogg" for index in range(1, 5))
SOUND_CARD_PLAY = tuple(f"game_cards/play{index}.ogg" for index in range(1, 5))
SOUND_CARD_DISCARD = tuple(
    f"game_cards/discard{index}.ogg" for index in range(1, 4)
)
SOUND_CARD_SHUFFLE = tuple(
    f"game_cards/shuffle{index}.ogg" for index in range(1, 4)
)

SOUND_GAME_INTRO = "game_bang/game_intro.ogg"
SOUND_AMBIENCE_WESTERN = "game_bang/ambience_western_loop.ogg"
SOUND_MUSIC_GAMEPLAY = "game_bang/music_gameplay.ogg"
SOUND_MUSIC_FINAL_SHOWDOWN = "game_bang/music_final_showdown.ogg"
SOUND_WIN = "game_chaosbear/wingame.ogg"

SOUND_CASING_DROPS = (
    "game_bang/casing_drop_1.ogg",
    "game_bang/casing_drop_2.ogg",
)
SOUND_WEAPON_EMPTY = "game_deadmansdeck/empty_click.ogg"
SOUND_ROULETTE_LOAD = "game_deadmanspoker/load_bullet.ogg"
SOUND_ROULETTE_COCK = "game_deadmansdeck/cock.ogg"
SOUND_ROULETTE_SPIN = "game_deadmansdeck/revolver_spin.ogg"
SOUND_ROULETTE_GUNSHOT = "game_deadmansdeck/gunshot.ogg"
SOUND_ROULETTE_BULLET_HIT = "game_deadmansdeck/bullet_hit.ogg"
SOUND_ROULETTE_CASINGS = (
    "game_deadmansdeck/empty_casing1.ogg",
    "game_deadmansdeck/empty_casing2.ogg",
    "game_deadmansdeck/empty_casing3.ogg",
)
SOUND_ELIMINATION_FALLS = tuple(
    f"battle/fall{index}.ogg" for index in range(1, 4)
)
SOUND_DYNAMITE_FUSE = "game_explodingkittens/fuse.ogg"
SOUND_DYNAMITE_PLACE = "game_bang/dynamite_place.ogg"
SOUND_DYNAMITE_EXPLOSION = "game_bang/dynamite_explosion.ogg"
SOUND_DYNAMITE_AFTERMATH = "game_bang/dynamite_aftermath.ogg"

SOUND_IMPACT_BULLET_BODY = (
    "game_bang/impact_bullet_body_1.ogg",
    "game_bang/impact_bullet_body_2.ogg",
)
SOUND_IMPACT_GENERIC = "game_bang/impact_damage_generic.ogg"
SOUND_IMPACT_HOWITZER = "game_bang/impact_howitzer.ogg"
SOUND_IMPACT_KNIFE = (
    "game_bang/impact_knife_flesh_1.ogg",
    "game_bang/impact_knife_flesh_2.ogg",
)
SOUND_IMPACT_PUNCH = (
    "game_bang/impact_punch_body_1.ogg",
    "game_bang/impact_punch_body_2.ogg",
)
SOUND_IMPACT_RICOCHET = (
    "game_bang/impact_ricochet_metal_1.ogg",
    "game_bang/impact_ricochet_metal_2.ogg",
)
SOUND_IMPACT_SNIPER = (
    "game_bang/impact_sniper_1.wav",
    "game_bang/impact_sniper_2.wav",
)
SOUND_IMPACT_WOOD_BARREL = (
    "game_bang/impact_wood_barrel_1.ogg",
    "game_bang/impact_wood_barrel_2.ogg",
)

SOUND_DEFENSE_BARREL_FAIL = (
    "game_bang/defense_barrel_fail_1.ogg",
    "game_bang/defense_barrel_fail_2.ogg",
)
SOUND_DEFENSE_DODGE = (
    "game_bang/defense_dodge_1.ogg",
    "game_bang/defense_dodge_2.ogg",
)
SOUND_DEFENSE_HAT = (
    "game_bang/impact_hat_1.ogg",
    "game_bang/impact_hat_2.ogg",
)
SOUND_DEFENSE_BIBLE = "game_bang/defense_bible.ogg"
SOUND_DEFENSE_IRON_PLATE = "game_bang/defense_iron_plate.ogg"
SOUND_DEFENSE_BLADE_DODGE = "game_bang/defense_blade_dodge.ogg"
SOUND_DEFENSE_BLUNT_DODGE = "game_bang/defense_blunt_dodge.ogg"

SOUND_DRINK_BEER = "game_bang/drink_beer.ogg"
SOUND_DRINK_CANTEEN = "game_bang/drink_canteen.ogg"
SOUND_DRINK_TEQUILA = "game_bang/drink_tequila.ogg"
SOUND_DRINK_WHISKY = "game_bang/drink_whisky.ogg"
SOUND_HEAL_SUCCESS = "game_bang/heal_success.ogg"

SOUND_EQUIP_BARREL = "game_bang/equipment_barrel_place.ogg"
SOUND_EQUIP_BINOCULARS = "game_bang/equipment_binoculars_equip.ogg"
SOUND_JAIL_CLOSE = "game_bang/jail_close.ogg"
SOUND_JAIL_OPEN = "game_bang/jail_open.ogg"
SOUND_EQUIP_COLT45 = "game_bang/weapon_colt45_draw.ogg"
SOUND_EQUIP_REMINGTON = "game_bang/weapon_remington_equip.ogg"
SOUND_EQUIP_REV_CARABINE = "game_bang/weapon_rev_carabine_equip.ogg"
SOUND_EQUIP_SCHOFIELD = "game_bang/weapon_schofield_equip.ogg"
SOUND_EQUIP_VOLCANIC = "game_bang/weapon_volcanic_equip.ogg"
SOUND_EQUIP_WINCHESTER = "game_bang/weapon_winchester_equip.ogg"

SOUND_FIRE_BUFFALO_RIFLE = (
    "game_bang/weapon_buffalo_rifle_fire_1.ogg",
    "game_bang/weapon_buffalo_rifle_fire_2.ogg",
)
SOUND_FIRE_COLT45 = ("game_bang/weapon_colt45_fire.ogg",)
SOUND_FIRE_DERRINGER = ("game_bang/weapon_derringer_fire.ogg",)
SOUND_FIRE_GATLING = ("game_bang/weapon_gatling_fire.ogg",)
SOUND_FIRE_HOWITZER = ("game_bang/weapon_howitzer_fire.ogg",)
SOUND_FIRE_KNIFE = (
    "game_bang/weapon_knife_throw_1.ogg",
    "game_bang/weapon_knife_throw_2.ogg",
)
SOUND_FIRE_PEPPERBOX = ("game_bang/weapon_pepperbox_fire.ogg",)
SOUND_FIRE_PUNCH = (
    "game_bang/weapon_punch_swing_1.ogg",
    "game_bang/weapon_punch_swing_2.ogg",
)
SOUND_FIRE_REMINGTON = ("game_bang/weapon_remington_fire.ogg",)
SOUND_FIRE_REV_CARABINE = ("game_bang/weapon_rev_carabine_fire.ogg",)
SOUND_FIRE_SCHOFIELD = ("game_bang/weapon_schofield_fire.ogg",)
SOUND_FIRE_SNIPER = ("game_bang/weapon_sniper_fire.ogg",)
SOUND_FIRE_SPRINGFIELD = ("game_bang/weapon_springfield_fire.ogg",)
SOUND_FIRE_VOLCANIC = ("game_bang/weapon_volcanic_fire.ogg",)
SOUND_FIRE_WINCHESTER = ("game_bang/weapon_winchester_fire.ogg",)
SOUND_SNIPER_AIM = "game_bang/weapon_sniper_aim.ogg"

WEAPON_EQUIP_SOUNDS = {
    cards.VOLCANIC: SOUND_EQUIP_VOLCANIC,
    cards.SCHOFIELD: SOUND_EQUIP_SCHOFIELD,
    cards.REMINGTON: SOUND_EQUIP_REMINGTON,
    cards.REV_CARABINE: SOUND_EQUIP_REV_CARABINE,
    cards.WINCHESTER: SOUND_EQUIP_WINCHESTER,
}

WEAPON_FIRE_SOUNDS = {
    cards.VOLCANIC: SOUND_FIRE_VOLCANIC,
    cards.SCHOFIELD: SOUND_FIRE_SCHOFIELD,
    cards.REMINGTON: SOUND_FIRE_REMINGTON,
    cards.REV_CARABINE: SOUND_FIRE_REV_CARABINE,
    cards.WINCHESTER: SOUND_FIRE_WINCHESTER,
}

ATTACK_FIRE_SOUNDS = {
    cards.BUFFALO_RIFLE: SOUND_FIRE_BUFFALO_RIFLE,
    cards.DERRINGER: SOUND_FIRE_DERRINGER,
    cards.GATLING: SOUND_FIRE_GATLING,
    cards.HOWITZER: SOUND_FIRE_HOWITZER,
    cards.KNIFE: SOUND_FIRE_KNIFE,
    cards.PEPPERBOX: SOUND_FIRE_PEPPERBOX,
    cards.PUNCH: SOUND_FIRE_PUNCH,
    cards.SPRINGFIELD: SOUND_FIRE_SPRINGFIELD,
    "sniper": SOUND_FIRE_SNIPER,
}

EQUIPMENT_SOUNDS = {
    cards.BARREL: SOUND_EQUIP_BARREL,
    cards.BINOCULAR: SOUND_EQUIP_BINOCULARS,
    cards.DYNAMITE: SOUND_DYNAMITE_PLACE,
    cards.JAIL: SOUND_JAIL_CLOSE,
    **WEAPON_EQUIP_SOUNDS,
}

CONSUMABLE_SOUNDS = {
    cards.BEER: SOUND_DRINK_BEER,
    cards.CANTEEN: SOUND_DRINK_CANTEEN,
    cards.TEQUILA: SOUND_DRINK_TEQUILA,
    cards.WHISKY: SOUND_DRINK_WHISKY,
}

DEFENSE_CARD_SOUNDS = {
    cards.BIBLE: (SOUND_DEFENSE_BIBLE,),
    cards.IRON_PLATE: (SOUND_DEFENSE_IRON_PLATE,),
    cards.SOMBRERO: SOUND_DEFENSE_HAT,
    cards.TEN_GALLON_HAT: SOUND_DEFENSE_HAT,
}

NON_FIREARM_ATTACKS = frozenset({cards.KNIFE, cards.PUNCH})
SINGLE_FIRE_MULTI_ATTACKS = frozenset({cards.GATLING, cards.HOWITZER})

# Ceiling-rounded from the shipped files' OGG granules or WAV frames.
# Shared-library entries are included whenever BANG! uses their duration to
# sequence another cue; keeping the measurements here makes those transitions
# deterministic across desktop, web, mobile, and save restoration.
AUDIO_DURATIONS_TICKS = {
    SOUND_GAME_INTRO: 164,
    SOUND_AMBIENCE_WESTERN: 407,
    SOUND_MUSIC_GAMEPLAY: 3229,
    SOUND_MUSIC_FINAL_SHOWDOWN: 3426,
    SOUND_CASING_DROPS[0]: 47,
    SOUND_CASING_DROPS[1]: 46,
    SOUND_IMPACT_BULLET_BODY[0]: 33,
    SOUND_IMPACT_BULLET_BODY[1]: 35,
    SOUND_IMPACT_GENERIC: 30,
    SOUND_IMPACT_HOWITZER: 56,
    SOUND_IMPACT_KNIFE[0]: 42,
    SOUND_IMPACT_KNIFE[1]: 34,
    SOUND_IMPACT_PUNCH[0]: 15,
    SOUND_IMPACT_PUNCH[1]: 16,
    SOUND_IMPACT_RICOCHET[0]: 21,
    SOUND_IMPACT_RICOCHET[1]: 18,
    SOUND_IMPACT_SNIPER[0]: 30,
    SOUND_IMPACT_SNIPER[1]: 27,
    SOUND_IMPACT_WOOD_BARREL[0]: 20,
    SOUND_IMPACT_WOOD_BARREL[1]: 20,
    SOUND_DEFENSE_BARREL_FAIL[0]: 76,
    SOUND_DEFENSE_BARREL_FAIL[1]: 67,
    SOUND_DEFENSE_DODGE[0]: 44,
    SOUND_DEFENSE_DODGE[1]: 35,
    SOUND_DEFENSE_HAT[0]: 24,
    SOUND_DEFENSE_HAT[1]: 9,
    SOUND_DEFENSE_BIBLE: 21,
    SOUND_DEFENSE_IRON_PLATE: 52,
    SOUND_DEFENSE_BLADE_DODGE: 12,
    SOUND_DEFENSE_BLUNT_DODGE: 9,
    SOUND_DRINK_BEER: 101,
    SOUND_DRINK_CANTEEN: 39,
    SOUND_DRINK_TEQUILA: 37,
    SOUND_DRINK_WHISKY: 40,
    SOUND_HEAL_SUCCESS: 18,
    SOUND_EQUIP_BARREL: 15,
    SOUND_EQUIP_BINOCULARS: 15,
    SOUND_DYNAMITE_PLACE: 16,
    SOUND_JAIL_CLOSE: 22,
    SOUND_JAIL_OPEN: 18,
    SOUND_EQUIP_COLT45: 18,
    SOUND_EQUIP_REMINGTON: 16,
    SOUND_EQUIP_REV_CARABINE: 19,
    SOUND_EQUIP_SCHOFIELD: 36,
    SOUND_EQUIP_VOLCANIC: 17,
    SOUND_EQUIP_WINCHESTER: 16,
    SOUND_FIRE_BUFFALO_RIFLE[0]: 55,
    SOUND_FIRE_BUFFALO_RIFLE[1]: 58,
    SOUND_FIRE_COLT45[0]: 43,
    SOUND_FIRE_DERRINGER[0]: 20,
    SOUND_FIRE_GATLING[0]: 82,
    SOUND_FIRE_HOWITZER[0]: 39,
    SOUND_FIRE_KNIFE[0]: 9,
    SOUND_FIRE_KNIFE[1]: 8,
    SOUND_FIRE_PEPPERBOX[0]: 31,
    SOUND_FIRE_PUNCH[0]: 7,
    SOUND_FIRE_PUNCH[1]: 8,
    SOUND_FIRE_REMINGTON[0]: 40,
    SOUND_FIRE_REV_CARABINE[0]: 22,
    SOUND_FIRE_SCHOFIELD[0]: 48,
    SOUND_FIRE_SNIPER[0]: 75,
    SOUND_FIRE_SPRINGFIELD[0]: 100,
    SOUND_FIRE_VOLCANIC[0]: 20,
    SOUND_FIRE_WINCHESTER[0]: 36,
    SOUND_SNIPER_AIM: 22,
    SOUND_WEAPON_EMPTY: 13,
    SOUND_ROULETTE_LOAD: 3,
    SOUND_ROULETTE_COCK: 14,
    SOUND_ROULETTE_SPIN: 68,
    SOUND_ROULETTE_GUNSHOT: 21,
    SOUND_ROULETTE_BULLET_HIT: 30,
    SOUND_ROULETTE_CASINGS[0]: 69,
    SOUND_ROULETTE_CASINGS[1]: 64,
    SOUND_ROULETTE_CASINGS[2]: 70,
    SOUND_ELIMINATION_FALLS[0]: 37,
    SOUND_ELIMINATION_FALLS[1]: 30,
    SOUND_ELIMINATION_FALLS[2]: 34,
    SOUND_DYNAMITE_FUSE: 14,
    SOUND_DYNAMITE_EXPLOSION: 97,
    SOUND_DYNAMITE_AFTERMATH: 383,
}

BANG_ASSET_PATHS = tuple(
    path
    for path in AUDIO_DURATIONS_TICKS
    if path.startswith("game_bang/")
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_SOUND_ASSET_ROOTS = (
    _REPOSITORY_ROOT / "client" / "sounds",
    _REPOSITORY_ROOT / "web_client" / "sounds",
    _REPOSITORY_ROOT / "mobile_client" / "sounds",
)


@lru_cache(maxsize=None)
def sound_ticks(sound: str) -> int:
    """Return this server run's asset duration, with metadata as fallback."""

    relative_path = PurePosixPath(sound)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)
    for asset_root in _SOUND_ASSET_ROOTS:
        measured = measure_audio_duration_ticks(
            asset_root.joinpath(*relative_path.parts),
            ticks_per_second=TICKS_PER_SECOND,
        )
        if measured is not None:
            return measured
    return AUDIO_DURATIONS_TICKS.get(sound, 0)
