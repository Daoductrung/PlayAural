"""Battle game implementation for PlayAural."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import BoolOption, IntOption, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .content import (
    BattleEffectBlock,
    BattleLocalizedName,
    BattleMove,
    BattlePreset,
    get_move_map,
    get_preset_map,
    load_battle_registry,
)


PHASE_SELECTION = "selection"
PHASE_COMBAT = "combat"

TURN_MODE_INITIATIVE = "initiative"
TURN_MODE_ROUND_ROBIN = "round_robin"

MODE_FREE_FOR_ALL = "free_for_all"
MODE_ONE_EACH = "one_each"
MODE_TWO_EACH = "two_each"
MODE_THREE_EACH = "three_each"
MODE_SPITTING_IMAGE = "spitting_image"
MODE_CLASSIC_ARENA = "classic_arena"
MODE_MIXED_ARENA = "mixed_arena"
MODE_CLASSIC_SURVIVAL = "classic_survival"
MODE_MIXED_SURVIVAL = "mixed_survival"
MODE_CLASSIC_WAVES = "classic_waves"
MODE_MIXED_WAVES = "mixed_waves"

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"
DIFFICULTY_INSANE = "insane"
DIFFICULTY_PROFESSIONAL = "professional"
DIFFICULTY_ULTIMATE = "ultimate"

TARGET_SELF_ONLY = "self_only"
TARGET_TEAM_ONLY = "team_only"
TARGET_TEAM_EXCEPT_SELF = "team_except_self"
TARGET_ALL_EXCEPT_SELF = "all_except_self"
TARGET_ENEMIES_ONLY = "enemies_only"
TARGET_ALL = "all"

SEQUENCE_TAG_BATTLE_INTRO = "battle_intro"
SEQUENCE_TAG_BATTLE_TURN = "battle_turn"
SEQUENCE_TAG_BATTLE_MOVE = "battle_move"
SEQUENCE_TAG_BATTLE_SPAWN = "battle_spawn"

MIN_ACTIVE_SPEED = 30
CRIT_DENOMINATOR = 20
PACE_RATIO_NUMERATOR = 7
PACE_RATIO_DENOMINATOR = 10
DEFAULT_SOUND_DURATION_TICKS = 22

STATIC_SOUND_DURATIONS_TICKS = {
    "battle/arena.ogg": 54,
    "battle/initiative.ogg": 24,
    "battle/turn.ogg": 20,
    "battle/statdown.ogg": 18,
    "battle/statup.ogg": 18,
    "battle/appear1.ogg": 18,
    "battle/appear2.ogg": 18,
    "battle/appear3.ogg": 18,
    "battle/appear4.ogg": 18,
    "battle/crowds/oneshot1.ogg": 22,
    "battle/crowds/oneshot2.ogg": 22,
    "battle/crowds/cheer30.1.ogg": 24,
    "battle/crowds/cheer30.2.ogg": 24,
    "battle/crowds/cheer30.3.ogg": 24,
    "battle/crowds/cheer30.4.ogg": 24,
}

GAME_MODE_CHOICE_LABELS = {
    MODE_FREE_FOR_ALL: "battle-mode-free-for-all",
    MODE_ONE_EACH: "battle-mode-one-each",
    MODE_TWO_EACH: "battle-mode-two-each",
    MODE_THREE_EACH: "battle-mode-three-each",
    MODE_SPITTING_IMAGE: "battle-mode-spitting-image",
    MODE_CLASSIC_ARENA: "battle-mode-classic-arena",
    MODE_MIXED_ARENA: "battle-mode-mixed-arena",
    MODE_CLASSIC_SURVIVAL: "battle-mode-classic-survival",
    MODE_MIXED_SURVIVAL: "battle-mode-mixed-survival",
    MODE_CLASSIC_WAVES: "battle-mode-classic-waves",
    MODE_MIXED_WAVES: "battle-mode-mixed-waves",
}

TURN_MODE_CHOICE_LABELS = {
    TURN_MODE_INITIATIVE: "battle-turn-mode-initiative",
    TURN_MODE_ROUND_ROBIN: "battle-turn-mode-round-robin",
}

ARENA_DIFFICULTY_CHOICE_LABELS = {
    DIFFICULTY_EASY: "battle-difficulty-easy",
    DIFFICULTY_NORMAL: "battle-difficulty-normal",
    DIFFICULTY_HARD: "battle-difficulty-hard",
    DIFFICULTY_INSANE: "battle-difficulty-insane",
    DIFFICULTY_PROFESSIONAL: "battle-difficulty-professional",
    DIFFICULTY_ULTIMATE: "battle-difficulty-ultimate",
}

CLASSIC_PRESET_CHOICE_LABELS = {
    preset.id: f"battle-classic-preset-{preset.id.replace('_', '-')}" for preset in load_battle_registry().presets
}

ARENA_DIFFICULTIES = {
    DIFFICULTY_EASY: {"health_mult": 0.5, "health_add": 0, "attack_add": 0, "defense_add": 0, "speed_add": 0},
    DIFFICULTY_NORMAL: {"health_mult": 1.0, "health_add": 0, "attack_add": 0, "defense_add": 0, "speed_add": 0},
    DIFFICULTY_HARD: {"health_mult": 1.0, "health_add": 10, "attack_add": 0, "defense_add": 0, "speed_add": 0},
    DIFFICULTY_INSANE: {"health_mult": 1.0, "health_add": 25, "attack_add": 0, "defense_add": 0, "speed_add": 0},
    DIFFICULTY_PROFESSIONAL: {"health_mult": 1.0, "health_add": 50, "attack_add": 1, "defense_add": 1, "speed_add": 30},
    DIFFICULTY_ULTIMATE: {"health_mult": 1.0, "health_add": 65, "attack_add": 2, "defense_add": 2, "speed_add": 40},
}


def classic_preset_choices(game=None, player=None) -> list[str]:
    return list(get_preset_map().keys())


@dataclass
class BattlePlayer(Player):
    selected_preset_ids: list[str] = field(default_factory=list)
    selection_locked: bool = False


@dataclass
class BattleFighter(DataClassJSONMixin):
    id: str
    base_name: BattleLocalizedName
    owner_player_id: str = ""
    team_id: str = ""
    max_health: int = 50
    health: int = 50
    attack: int = 0
    defense: int = 0
    speed: int = 100
    move_ids: list[str] = field(default_factory=list)
    eliminated: bool = False
    elimination_reason: str = ""
    controller: str = "human"
    is_clone: bool = False
    is_arena_enemy: bool = False
    since_turn: int = 1
    display_number: int = 0


@dataclass
class BattleOptions(GameOptions):
    game_mode: str = option_field(
        MenuOption(
            default=MODE_ONE_EACH,
            choices=[
                MODE_FREE_FOR_ALL,
                MODE_ONE_EACH,
                MODE_TWO_EACH,
                MODE_THREE_EACH,
                MODE_SPITTING_IMAGE,
                MODE_CLASSIC_ARENA,
                MODE_MIXED_ARENA,
                MODE_CLASSIC_SURVIVAL,
                MODE_MIXED_SURVIVAL,
                MODE_CLASSIC_WAVES,
                MODE_MIXED_WAVES,
            ],
            value_key="mode",
            label="battle-set-game-mode",
            prompt="battle-select-game-mode",
            change_msg="battle-option-changed-game-mode",
            choice_labels=GAME_MODE_CHOICE_LABELS,
        )
    )
    turn_mode: str = option_field(
        MenuOption(
            default=TURN_MODE_INITIATIVE,
            choices=[TURN_MODE_INITIATIVE, TURN_MODE_ROUND_ROBIN],
            value_key="mode",
            label="battle-set-turn-mode",
            prompt="battle-select-turn-mode",
            change_msg="battle-option-changed-turn-mode",
            choice_labels=TURN_MODE_CHOICE_LABELS,
        )
    )
    balance_mode: bool = option_field(
        BoolOption(default=False, label="battle-set-balance-mode", change_msg="battle-option-changed-balance-mode")
    )
    unlimited_selection_limit: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=6,
            value_key="count",
            label="battle-set-unlimited-selection-limit",
            prompt="battle-enter-unlimited-selection-limit",
            change_msg="battle-option-changed-unlimited-selection-limit",
        )
    )
    classic_enemy_preset: str = option_field(
        MenuOption(
            default="novice_boxer",
            choices=classic_preset_choices,
            value_key="preset",
            label="battle-set-classic-enemy-preset",
            prompt="battle-select-classic-enemy-preset",
            change_msg="battle-option-changed-classic-enemy-preset",
            choice_labels=CLASSIC_PRESET_CHOICE_LABELS,
        )
    )
    arena_difficulty: str = option_field(
        MenuOption(
            default=DIFFICULTY_NORMAL,
            choices=list(ARENA_DIFFICULTIES.keys()),
            value_key="difficulty",
            label="battle-set-arena-difficulty",
            prompt="battle-select-arena-difficulty",
            change_msg="battle-option-changed-arena-difficulty",
            choice_labels=ARENA_DIFFICULTY_CHOICE_LABELS,
        )
    )
    survival_target: int = option_field(
        IntOption(default=0, min_val=0, max_val=10000, value_key="count", label="battle-set-survival-target", prompt="battle-enter-survival-target", change_msg="battle-option-changed-survival-target")
    )
    survival_heal_percent: int = option_field(
        IntOption(default=0, min_val=0, max_val=100, value_key="percent", label="battle-set-survival-heal-percent", prompt="battle-enter-survival-heal-percent", change_msg="battle-option-changed-survival-heal-percent")
    )


@register_game
@dataclass
class BattleGame(Game):
    players: list[BattlePlayer] = field(default_factory=list)
    options: BattleOptions = field(default_factory=BattleOptions)
    phase: str = PHASE_SELECTION
    fighters: list[BattleFighter] = field(default_factory=list)
    acting_player_id: str = ""
    acting_fighter_id: str = ""
    round_robin_order_ids: list[str] = field(default_factory=list)
    round_robin_index: int = -1
    survival_kills: int = 0
    survival_wave: int = 1
    survival_enemy_count: int = 0
    enemy_name_counts: dict[str, int] = field(default_factory=dict)
    turn_number: int = 0
    bot_wait_ticks: int = 0
    winning_team_id: str = ""
    last_action_message_key: str = ""
    last_action_payload: dict[str, str | int] = field(default_factory=dict)

    @classmethod
    def get_name(cls) -> str:
        return "Battle"

    @classmethod
    def get_type(cls) -> str:
        return "battle"

    @classmethod
    def get_category(cls) -> str:
        return "category-rb-play-center"

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["games_played"]

    @classmethod
    def get_leaderboard_types(cls) -> list[dict]:
        return [
            {
                "id": "most_enemies_defeated",
                "path": "player_stats.{player_id}.survival_kills",
                "aggregate": "max",
                "format": "score",
            },
            {
                "id": "deepest_wave_reached",
                "path": "player_stats.{player_id}.deepest_wave",
                "aggregate": "max",
                "format": "score",
            },
        ]

    @property
    def current_player(self) -> BattlePlayer | None:
        return self._as_battle_player(self.get_player_by_id(self.acting_player_id))

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> BattlePlayer:
        return BattlePlayer(id=player_id, name=name, is_bot=is_bot)

    def _as_battle_player(self, player: Player | None) -> BattlePlayer | None:
        return player if isinstance(player, BattlePlayer) else None

    def _player_locale(self, player: Player | None) -> str:
        if not player:
            return "en"
        user = self.get_user(player)
        return user.locale if user else "en"

    def _locale_name(self, name: BattleLocalizedName, locale: str) -> str:
        return name.for_locale(locale)

    def _move_label(self, locale: str, move_id: str) -> str:
        move = get_move_map()[move_id]
        return self._locale_name(move.name, locale)

    def _preset_label(self, locale: str, preset_id: str) -> str:
        preset = get_preset_map()[preset_id]
        return self._locale_name(preset.name, locale)

    def _fighter_name(self, fighter: BattleFighter, locale: str) -> str:
        base = self._locale_name(fighter.base_name, locale)
        if fighter.display_number > 0:
            return Localization.get(locale, "battle-fighter-name-numbered", name=base, number=fighter.display_number)
        return base

    def _fighter_owner(self, fighter: BattleFighter) -> BattlePlayer | None:
        return self._as_battle_player(self.get_player_by_id(fighter.owner_player_id))

    def _fighter_for_player(self, player: BattlePlayer | None) -> BattleFighter | None:
        current = self.current_fighter
        if current and player and current.owner_player_id == player.id:
            return current
        return None

    @property
    def current_fighter(self) -> BattleFighter | None:
        return self._fighter_by_id(self.acting_fighter_id)

    def _fighter_by_id(self, fighter_id: str) -> BattleFighter | None:
        if not fighter_id:
            return None
        for fighter in self.fighters:
            if fighter.id == fighter_id:
                return fighter
        return None

    def _difficulty_config(self) -> dict[str, float | int]:
        return ARENA_DIFFICULTIES[self.options.arena_difficulty]

    def _is_arena_mode(self) -> bool:
        return self.options.game_mode in {
            MODE_CLASSIC_ARENA,
            MODE_MIXED_ARENA,
            MODE_CLASSIC_SURVIVAL,
            MODE_MIXED_SURVIVAL,
            MODE_CLASSIC_WAVES,
            MODE_MIXED_WAVES,
        }

    def _is_survival_mode(self) -> bool:
        return self.options.game_mode in {MODE_CLASSIC_SURVIVAL, MODE_MIXED_SURVIVAL}

    def _is_wave_mode(self) -> bool:
        return self.options.game_mode in {MODE_CLASSIC_WAVES, MODE_MIXED_WAVES}

    def _is_classic_enemy_mode(self) -> bool:
        return self.options.game_mode in {MODE_CLASSIC_ARENA, MODE_CLASSIC_SURVIVAL, MODE_CLASSIC_WAVES}

    def _mode_requires_multiple_players(self) -> bool:
        return self.options.game_mode in {MODE_ONE_EACH, MODE_TWO_EACH, MODE_THREE_EACH}

    def _selection_limit_for_mode(self) -> int:
        if self.options.game_mode == MODE_ONE_EACH:
            return 1
        if self.options.game_mode == MODE_TWO_EACH:
            return 2
        if self.options.game_mode == MODE_THREE_EACH:
            return 3
        return self.options.unlimited_selection_limit

    def _mode_allows_manual_done(self) -> bool:
        return self.options.game_mode in {
            MODE_FREE_FOR_ALL,
            MODE_SPITTING_IMAGE,
            MODE_CLASSIC_ARENA,
            MODE_MIXED_ARENA,
            MODE_CLASSIC_SURVIVAL,
            MODE_MIXED_SURVIVAL,
            MODE_CLASSIC_WAVES,
            MODE_MIXED_WAVES,
        }

    def _mode_min_players(self) -> int:
        return 2 if self._mode_requires_multiple_players() else 1

    def _survival_options_are_active(self) -> bool:
        return self._is_survival_mode() or self._is_wave_mode()

    def _survival_target_is_endless(self) -> bool:
        return self.options.survival_target <= 0

    def _uses_team_context(self) -> bool:
        return self.options.game_mode != MODE_FREE_FOR_ALL

    def _paced_delay_ticks(self, sound_path: str) -> int:
        duration = STATIC_SOUND_DURATIONS_TICKS.get(sound_path, DEFAULT_SOUND_DURATION_TICKS)
        return max(6, (duration * PACE_RATIO_NUMERATOR) // PACE_RATIO_DENOMINATOR)

    def _queue_bot_turn_if_needed(self) -> None:
        fighter = self.current_fighter
        if fighter and self._fighter_is_bot_controlled(fighter):
            self.bot_wait_ticks = random.randint(12, 24)
        else:
            self.bot_wait_ticks = 0

    def _fighter_is_bot_controlled(self, fighter: BattleFighter) -> bool:
        owner = self._fighter_owner(fighter)
        return fighter.controller == "ai" or bool(owner and owner.is_bot)

    def _is_fighter_active(self, fighter: BattleFighter) -> bool:
        return not fighter.eliminated and fighter.health > 0 and fighter.speed >= MIN_ACTIVE_SPEED

    def _alive_fighters(self) -> list[BattleFighter]:
        return [fighter for fighter in self.fighters if self._is_fighter_active(fighter)]

    def _alive_team_ids(self) -> list[str]:
        return sorted({fighter.team_id for fighter in self._alive_fighters()})

    def _team_display_name(self, locale: str, team_id: str, viewer: Player | None = None) -> str:
        if viewer and viewer.is_spectator:
            if team_id == "ally":
                return Localization.get(locale, "battle-team-contestants")
            if team_id == "enemy":
                return Localization.get(locale, "battle-team-arena")
        if team_id == "ally":
            return Localization.get(locale, "battle-team-allies")
        if team_id == "enemy":
            return Localization.get(locale, "battle-team-enemies")
        team_fighter = next((fighter for fighter in self.fighters if fighter.team_id == team_id), None)
        if team_fighter:
            owner = self._fighter_owner(team_fighter)
            if owner and self.options.game_mode != MODE_FREE_FOR_ALL:
                return Localization.get(locale, "battle-team-owned", player=owner.name)
            return Localization.get(locale, "battle-team-owned", player=self._fighter_name(team_fighter, locale))
        owner = self._as_battle_player(self.get_player_by_id(team_id))
        if owner:
            return Localization.get(locale, "battle-team-owned", player=owner.name)
        return team_id

    def _result_team_display_name(self, locale: str, team_id: str) -> str:
        if team_id == "ally":
            return Localization.get(locale, "battle-team-contestants")
        if team_id == "enemy":
            return Localization.get(locale, "battle-team-arena")
        return self._team_display_name(locale, team_id)

    def _selection_summary(self, locale: str, player: BattlePlayer) -> str:
        if not player.selected_preset_ids:
            return Localization.get(locale, "battle-selection-none")
        labels = [
            self._preset_label(locale, preset_id)
            for preset_id in player.selected_preset_ids
            if preset_id in get_preset_map()
        ]
        return Localization.format_list_and(locale, labels) if labels else Localization.get(locale, "battle-selection-none")

    def _fighter_summary_line(self, locale: str, fighter: BattleFighter, viewer: Player | None = None) -> str:
        move_list = Localization.format_list_and(locale, [self._move_label(locale, move_id) for move_id in fighter.move_ids]) if fighter.move_ids else Localization.get(locale, "battle-no-moves")
        key = "battle-fighter-summary-line" if self._uses_team_context() else "battle-fighter-summary-line-no-team"
        kwargs = {
            "fighter": self._fighter_name(fighter, locale),
            "health": fighter.health,
            "attack": fighter.attack,
            "defense": fighter.defense,
            "speed": fighter.speed,
            "moves": move_list,
        }
        if self._uses_team_context():
            kwargs["team"] = self._team_display_name(locale, fighter.team_id, viewer)
        return Localization.get(
            locale,
            key,
            **kwargs,
        )

    def _team_ids_for_player(self, player: Player) -> set[str]:
        return {
            fighter.team_id
            for fighter in self.fighters
            if fighter.owner_player_id == player.id and fighter.team_id
        }

    def _mode_progress_line(self, locale: str, *, kills: int, wave: int) -> str:
        if self._is_survival_mode():
            if self._survival_target_is_endless():
                return Localization.get(locale, "battle-survival-progress-endless", kills=kills)
            return Localization.get(
                locale,
                "battle-survival-progress-target",
                kills=kills,
                target=self.options.survival_target,
            )
        if self._is_wave_mode():
            if self._survival_target_is_endless():
                return Localization.get(locale, "battle-wave-progress-endless", kills=kills, wave=wave)
            return Localization.get(
                locale,
                "battle-wave-progress-target",
                kills=kills,
                target=self.options.survival_target,
                wave=wave,
            )
        if self._survival_target_is_endless():
            return Localization.get(locale, "battle-survival-progress-endless", kills=kills)
        return Localization.get(
            locale,
            "battle-survival-progress-target",
            kills=kills,
            target=self.options.survival_target,
        )

    def _broadcast_game_localized(self, key: str, **builder_kwargs) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            locale = user.locale
            kwargs = {
                name: value(locale) if callable(value) else value
                for name, value in builder_kwargs.items()
            }
            user.speak_l(key, buffer="game", **kwargs)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = super().prestart_validate()
        active_players = self.get_active_players()
        if not get_move_map() or not get_preset_map():
            errors.append("battle-error-no-registry")
        min_players = self._mode_min_players()
        if len(active_players) < min_players:
            errors.append(("battle-error-mode-min-players", {"count": min_players}))
        if not self._survival_options_are_active():
            if self.options.survival_target > 0:
                errors.append("battle-error-survival-target-mode")
            if self.options.survival_heal_percent > 0:
                errors.append("battle-error-survival-heal-mode")
        if self.options.unlimited_selection_limit < 1:
            errors.append("battle-error-selection-limit")
        if self._is_classic_enemy_mode() and self.options.classic_enemy_preset not in get_preset_map():
            errors.append("battle-error-invalid-classic-preset")
        return errors

    def on_start(self) -> None:
        self.status = "playing"
        self.phase = PHASE_SELECTION
        self.game_active = True
        self._sync_table_status()
        self.cancel_all_sequences()
        self.fighters = []
        self.acting_player_id = ""
        self.acting_fighter_id = ""
        self.round_robin_order_ids = []
        self.round_robin_index = -1
        self.survival_kills = 0
        self.survival_wave = 1
        self.survival_enemy_count = 0
        self.enemy_name_counts = {}
        self.turn_number = 0
        self.winning_team_id = ""
        self.last_action_message_key = ""
        self.last_action_payload = {}
        for player in self.get_active_players():
            battle_player = self._as_battle_player(player)
            if battle_player:
                battle_player.selected_preset_ids = []
                battle_player.selection_locked = False
        self.play_music("battle/fightmus.ogg")
        self.play_ambience("battle/crowds/ambience_reserves_selections.ogg")
        self.broadcast_l("battle-selection-start", buffer="game")
        self._auto_select_for_bots()
        self.rebuild_all_menus()

    def _auto_select_for_bots(self) -> None:
        for player in self.get_active_players():
            battle_player = self._as_battle_player(player)
            if not battle_player or not battle_player.is_bot or battle_player.selection_locked:
                continue
            self._auto_fill_selection(battle_player)

    def _auto_fill_selection(self, player: BattlePlayer) -> None:
        preset_ids = list(get_preset_map().keys())
        limit = self._selection_limit_for_mode()
        selection_count = limit if not self._mode_allows_manual_done() else random.randint(1, limit)
        player.selected_preset_ids = random.sample(preset_ids, k=min(selection_count, len(preset_ids)))
        player.selection_locked = True
        for preset_id in player.selected_preset_ids:
            self._announce_selected_fighter(player, preset_id)
        self.broadcast_l("battle-selection-locked", buffer="game", player=player.name)

    def _all_selection_locked(self) -> bool:
        active = [self._as_battle_player(player) for player in self.get_active_players()]
        active = [player for player in active if player]
        return bool(active) and all(player.selection_locked for player in active)

    def _build_selected_fighters(self) -> None:
        self.fighters = []
        next_index = 1
        for player in self.get_active_players():
            battle_player = self._as_battle_player(player)
            if not battle_player:
                continue
            for preset_id in battle_player.selected_preset_ids:
                preset = get_preset_map().get(preset_id)
                if not preset:
                    continue
                fighter = BattleFighter(
                    id=f"fighter_{next_index}",
                    base_name=preset.name,
                    owner_player_id=battle_player.id,
                    team_id=self._team_for_player_fighter(battle_player, preset_id, next_index),
                    max_health=preset.health,
                    health=preset.health,
                    attack=preset.attack,
                    defense=preset.defense,
                    speed=preset.speed,
                    move_ids=list(preset.move_ids),
                    controller="ai" if battle_player.is_bot else "human",
                )
                self._enforce_balance_if_needed(fighter)
                self.fighters.append(fighter)
                next_index += 1
        self._apply_mode_effects(next_index)
        self._assign_display_numbers()

    def _team_for_player_fighter(self, player: BattlePlayer, preset_id: str, fighter_index: int) -> str:
        if self.options.game_mode == MODE_FREE_FOR_ALL:
            return f"{player.id}:{preset_id}:{fighter_index}"
        if self.options.game_mode == MODE_SPITTING_IMAGE or self._is_arena_mode():
            return "ally"
        return player.id

    def _calculate_balance(self, fighter: BattleFighter) -> int:
        return (fighter.health * 2) + (fighter.attack * 6) + (fighter.defense * 6) + fighter.speed

    def _enforce_balance_if_needed(self, fighter: BattleFighter) -> None:
        if not self.options.balance_mode:
            return
        if self._calculate_balance(fighter) != 200:
            fighter.max_health = 50
            fighter.health = 50
            fighter.attack = 0
            fighter.defense = 0
            fighter.speed = 100

    def _apply_mode_effects(self, next_index: int) -> None:
        if self.options.game_mode == MODE_SPITTING_IMAGE:
            self._spawn_spitting_image_clones(next_index)
            return
        if self._is_arena_mode():
            self._spawn_initial_arena_enemies(next_index)

    def _spawn_spitting_image_clones(self, next_index: int) -> None:
        originals = list(self.fighters)
        for fighter in originals:
            clone = BattleFighter(
                id=f"fighter_{next_index}",
                base_name=fighter.base_name,
                owner_player_id="",
                team_id="enemy",
                max_health=fighter.max_health,
                health=fighter.health,
                attack=fighter.attack,
                defense=fighter.defense,
                speed=fighter.speed,
                move_ids=list(fighter.move_ids),
                controller="ai",
                is_clone=True,
            )
            self.fighters.append(clone)
            next_index += 1

    def _spawn_initial_arena_enemies(self, next_index: int) -> None:
        self.enemy_name_counts = {}
        self.survival_enemy_count = 0
        for _ in range(len(self.fighters)):
            enemy = self._build_arena_enemy(next_index)
            self.fighters.append(enemy)
            next_index += 1

    def _wave_bonus(self) -> dict[str, int]:
        wave_index = max(1, self.survival_wave)
        return {
            "health_add": (wave_index - 1) * 10,
            "attack_add": ((wave_index - 1) * 2) // 3,
            "defense_add": ((wave_index - 1) * 2) // 3,
            "speed_add": (wave_index - 1) * 5,
        }

    def _choose_arena_preset(self) -> BattlePreset:
        if self._is_classic_enemy_mode():
            return get_preset_map()[self.options.classic_enemy_preset]
        return random.choice(list(get_preset_map().values()))

    def _build_arena_enemy(self, next_index: int) -> BattleFighter:
        preset = self._choose_arena_preset()
        difficulty = self._difficulty_config()
        wave_bonus = self._wave_bonus() if (self._is_survival_mode() or self._is_wave_mode()) else {"health_add": 0, "attack_add": 0, "defense_add": 0, "speed_add": 0}
        health = int(preset.health * difficulty["health_mult"]) + int(difficulty["health_add"]) + wave_bonus["health_add"]
        attack = preset.attack + int(difficulty["attack_add"]) + wave_bonus["attack_add"]
        defense = preset.defense + int(difficulty["defense_add"]) + wave_bonus["defense_add"]
        speed = preset.speed + int(difficulty["speed_add"]) + wave_bonus["speed_add"]
        if self._is_survival_mode() or self._is_wave_mode():
            health = max(1, health // 3)
            attack = attack // 3
            defense = defense // 3
            speed = max(1, int(speed / 1.5))
        self.survival_enemy_count += 1
        self.enemy_name_counts[preset.id] = self.enemy_name_counts.get(preset.id, 0) + 1
        return BattleFighter(
            id=f"fighter_{next_index}",
            base_name=preset.name,
            owner_player_id="",
            team_id="enemy",
            max_health=health,
            health=health,
            attack=attack,
            defense=defense,
            speed=speed,
            move_ids=list(preset.move_ids),
            controller="ai",
            is_arena_enemy=True,
            display_number=self.enemy_name_counts[preset.id],
        )

    def _assign_display_numbers(self) -> None:
        counts: dict[str, int] = {}
        for fighter in self.fighters:
            key = fighter.base_name.en
            counts[key] = counts.get(key, 0) + 1
        seen: dict[str, int] = {}
        for fighter in self.fighters:
            key = fighter.base_name.en
            seen[key] = seen.get(key, 0) + 1
            fighter.display_number = seen[key] if counts[key] > 1 or fighter.is_arena_enemy else 0

    def _start_combat(self) -> None:
        self._build_selected_fighters()
        if len(self._alive_team_ids()) < 2:
            self.broadcast_l("battle-no-fight-same-team", buffer="game")
            self._finish_with_team_result("")
            return
        self.phase = PHASE_COMBAT
        self.stop_ambience()
        self.play_ambience("battle/crowds/ambiencefight.ogg")
        self.start_sequence(
            "battle_intro",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op("battle/arena.ogg", volume=70),
                        SequenceOperation.callback_op("battle_intro_announce"),
                    ],
                    delay_after_ticks=self._paced_delay_ticks("battle/arena.ogg"),
                ),
                SequenceBeat(ops=[SequenceOperation.callback_op("battle_begin_next_turn")]),
            ],
            tag=SEQUENCE_TAG_BATTLE_INTRO,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _begin_next_turn(self) -> None:
        if self.options.turn_mode == TURN_MODE_INITIATIVE:
            for fighter in self._alive_fighters():
                fighter.since_turn += 1
        next_fighter = self._select_next_fighter()
        if not next_fighter:
            self._finish_with_team_result("")
            return
        if self.options.turn_mode == TURN_MODE_INITIATIVE:
            next_fighter.since_turn = 0
        owner = self._fighter_owner(next_fighter)
        self.acting_fighter_id = next_fighter.id
        self.acting_player_id = owner.id if owner else ""
        self.turn_number += 1
        sound_path = "battle/initiative.ogg" if self.options.turn_mode == TURN_MODE_INITIATIVE else "battle/turn.ogg"
        self.start_sequence(
            f"battle_turn_{self.turn_number}",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(sound_path, volume=70),
                        SequenceOperation.callback_op("battle_announce_turn", {"fighter_id": next_fighter.id}),
                    ],
                    delay_after_ticks=self._paced_delay_ticks(sound_path),
                ),
            ],
            tag=SEQUENCE_TAG_BATTLE_TURN,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _select_next_fighter(self) -> BattleFighter | None:
        alive = self._alive_fighters()
        if not alive:
            return None
        if self.options.turn_mode == TURN_MODE_INITIATIVE:
            best_score = -1
            best_fighter: BattleFighter | None = None
            for fighter in alive:
                roll = random.randint(1, max(1, 50 + fighter.speed))
                score = int(roll * (fighter.since_turn * 0.75))
                if score > best_score or (score == best_score and random.choice([True, False])):
                    best_score = score
                    best_fighter = fighter
            return best_fighter
        alive_ids = [fighter.id for fighter in self.fighters if self._is_fighter_active(fighter)]
        if alive_ids != self.round_robin_order_ids or self.round_robin_index >= len(alive_ids) - 1:
            self.round += 1
            self.round_robin_order_ids = alive_ids
            self.round_robin_index = 0
        else:
            self.round_robin_index += 1
        return self._fighter_by_id(self.round_robin_order_ids[self.round_robin_index])

    def _valid_targets(self, launcher: BattleFighter, move: BattleMove) -> list[BattleFighter]:
        active = self._alive_fighters()
        if move.targeting == TARGET_SELF_ONLY:
            return [launcher] if self._is_fighter_active(launcher) else []
        if move.targeting == TARGET_TEAM_ONLY:
            return [fighter for fighter in active if fighter.team_id == launcher.team_id]
        if move.targeting == TARGET_TEAM_EXCEPT_SELF:
            return [fighter for fighter in active if fighter.team_id == launcher.team_id and fighter.id != launcher.id]
        if move.targeting == TARGET_ALL_EXCEPT_SELF:
            return [fighter for fighter in active if fighter.id != launcher.id]
        if move.targeting == TARGET_ENEMIES_ONLY:
            return [fighter for fighter in active if fighter.team_id != launcher.team_id]
        return active

    def _begin_move_resolution(self, launcher: BattleFighter, target: BattleFighter, move: BattleMove) -> None:
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "battle_announce_move",
                        {"launcher_id": launcher.id, "target_id": target.id, "move_id": move.id},
                    ),
                    SequenceOperation.sound_op(move.sound_path, volume=75),
                ],
                delay_after_ticks=self._paced_delay_ticks(move.sound_path),
            )
        ]
        for index, _ in enumerate(move.blocks):
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "battle_apply_block",
                            {
                                "launcher_id": launcher.id,
                                "target_id": target.id,
                                "move_id": move.id,
                                "block_index": index,
                            },
                        )
                    ],
                    delay_after_ticks=12,
                )
            )
        beats.append(SequenceBeat(ops=[SequenceOperation.callback_op("battle_finalize_move")]))
        self.start_sequence(
            f"battle_move_{self.turn_number}",
            beats,
            tag=SEQUENCE_TAG_BATTLE_MOVE,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _resolve_damage(self, launcher: BattleFighter, target: BattleFighter, block: BattleEffectBlock) -> int:
        base_damage = random.randint(block.min or 0, block.max or 0)
        damage = max(0, base_damage + launcher.attack - target.defense)
        if random.randint(1, CRIT_DENOMINATOR) == 1:
            damage *= 2
            self.broadcast_l("battle-critical-hit", buffer="game")
        health_before = target.health
        target.health = max(0, target.health - damage)
        self._broadcast_game_localized(
            "battle-damage",
            target=lambda locale: self._fighter_name(target, locale),
            amount=damage,
        )
        if health_before * 100 >= max(1, target.max_health) * 70 and target.health <= 0:
            self.play_sound(f"battle/crowds/oneshot{random.randint(1, 2)}.ogg", volume=70)
        elif damage >= 30:
            self.play_sound(f"battle/crowds/cheer30.{random.randint(1, 4)}.ogg", volume=70)
        return damage

    def _resolve_healing(self, target: BattleFighter, block: BattleEffectBlock) -> None:
        healing = random.randint(block.min or 0, block.max or 0)
        target.health = min(target.max_health, target.health + healing)
        self._broadcast_game_localized(
            "battle-healing",
            target=lambda locale: self._fighter_name(target, locale),
            amount=healing,
        )

    def _resolve_drain(self, launcher: BattleFighter, target: BattleFighter, block: BattleEffectBlock) -> None:
        damage = self._resolve_damage(launcher, target, block)
        healing = (damage * (block.percent or 50)) // 100
        if healing > 0:
            launcher.health = min(launcher.max_health, launcher.health + healing)
            self._broadcast_game_localized(
                "battle-healing",
                target=lambda locale: self._fighter_name(launcher, locale),
                amount=healing,
            )

    def _resolve_stat_change(self, fighter: BattleFighter, stat: str, change: int, announce_target: BattleFighter) -> None:
        if change == 0:
            return
        setattr(fighter, stat, getattr(fighter, stat) + change)
        self.play_sound("battle/statup.ogg" if change > 0 else "battle/statdown.ogg", volume=70)
        self._broadcast_game_localized(
            "battle-stat-change",
            target=lambda locale: self._fighter_name(announce_target, locale),
            stat=lambda locale: Localization.get(locale, f"battle-stat-{stat}"),
            amount=change,
        )

    def _apply_block(self, launcher: BattleFighter, target: BattleFighter, block: BattleEffectBlock) -> None:
        if block.type == "damage":
            self._resolve_damage(launcher, target, block)
        elif block.type == "healing":
            self._resolve_healing(target, block)
        elif block.type == "drain":
            self._resolve_drain(launcher, target, block)
        elif block.type == "launcher_attack":
            self._resolve_stat_change(launcher, "attack", block.change or 0, launcher)
        elif block.type == "launcher_defense":
            self._resolve_stat_change(launcher, "defense", block.change or 0, launcher)
        elif block.type == "launcher_speed":
            self._resolve_stat_change(launcher, "speed", block.change or 0, launcher)
        elif block.type == "target_attack":
            self._resolve_stat_change(target, "attack", block.change or 0, target)
        elif block.type == "target_defense":
            self._resolve_stat_change(target, "defense", block.change or 0, target)
        elif block.type == "target_speed":
            self._resolve_stat_change(target, "speed", block.change or 0, target)

    def _resolve_eliminations(self) -> tuple[list[BattleFighter], list[BattleFighter]]:
        newly_defeated: list[BattleFighter] = []
        newly_defeated_enemies: list[BattleFighter] = []
        for fighter in self.fighters:
            if fighter.eliminated:
                continue
            if fighter.health <= 0:
                fighter.eliminated = True
                fighter.elimination_reason = "health"
            elif fighter.speed < MIN_ACTIVE_SPEED:
                fighter.eliminated = True
                fighter.elimination_reason = "speed"
            else:
                continue
            newly_defeated.append(fighter)
            message_key = "battle-fighter-defeated" if fighter.elimination_reason == "health" else "battle-fighter-incapacitated"
            self._broadcast_game_localized(
                message_key,
                fighter=lambda locale, defeated=fighter: self._fighter_name(defeated, locale),
            )
            if fighter.is_arena_enemy:
                newly_defeated_enemies.append(fighter)
                self.survival_kills += 1
        return newly_defeated, newly_defeated_enemies

    def _check_for_winner(self) -> bool:
        if self._survival_options_are_active() and self.options.survival_target > 0 and self.survival_kills >= self.options.survival_target:
            self._finish_with_team_result("ally")
            return True
        if self._survival_options_are_active():
            allies_alive = any(self._is_fighter_active(fighter) and not fighter.is_arena_enemy for fighter in self.fighters)
            if not allies_alive:
                self._finish_with_team_result("enemy")
                return True
            return False
        alive_teams = self._alive_team_ids()
        if len(alive_teams) == 1:
            self._finish_with_team_result(alive_teams[0])
            return True
        if not alive_teams:
            self._finish_with_team_result("")
            return True
        return False

    def _heal_players_between_waves(self) -> None:
        if self.options.survival_heal_percent <= 0:
            return
        for fighter in self.fighters:
            if fighter.is_arena_enemy or fighter.eliminated:
                continue
            missing = fighter.max_health - fighter.health
            if missing <= 0:
                continue
            amount = min(missing, (fighter.max_health * self.options.survival_heal_percent) // 100)
            if amount > 0:
                fighter.health += amount
                self._broadcast_game_localized(
                    "battle-healing",
                    target=lambda locale, healed=fighter: self._fighter_name(healed, locale),
                    amount=amount,
                )

    def _start_spawn_sequence(self, enemy_count: int) -> None:
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.sound_op("battle/arena.ogg", volume=70),
                    SequenceOperation.callback_op("battle_spawn_intro", {"count": enemy_count}),
                ],
                delay_after_ticks=self._paced_delay_ticks("battle/arena.ogg"),
            ),
            SequenceBeat(ops=[SequenceOperation.callback_op("battle_begin_next_turn")]),
        ]
        self.start_sequence(
            f"battle_spawn_{self.turn_number}",
            beats,
            tag=SEQUENCE_TAG_BATTLE_SPAWN,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _post_move_progression(self) -> None:
        _, defeated_enemies = self._resolve_eliminations()
        if self._check_for_winner():
            return
        if self._is_survival_mode() and defeated_enemies:
            self._heal_players_between_waves()
            next_index = len(self.fighters) + 1
            for _ in defeated_enemies:
                self.fighters.append(self._build_arena_enemy(next_index))
                next_index += 1
            self._assign_display_numbers()
            self._start_spawn_sequence(len(defeated_enemies))
            return
        if self._is_wave_mode():
            enemies_alive = any(self._is_fighter_active(fighter) and fighter.is_arena_enemy for fighter in self.fighters)
            players_alive = any(self._is_fighter_active(fighter) and not fighter.is_arena_enemy for fighter in self.fighters)
            if players_alive and not enemies_alive:
                self.survival_wave += 1
                self._heal_players_between_waves()
                next_index = len(self.fighters) + 1
                spawn_count = sum(1 for fighter in self.fighters if self._is_fighter_active(fighter) and not fighter.is_arena_enemy)
                for _ in range(spawn_count):
                    self.fighters.append(self._build_arena_enemy(next_index))
                    next_index += 1
                self._assign_display_numbers()
                self._start_spawn_sequence(spawn_count)
                return
        self._begin_next_turn()

    def on_sequence_callback(self, sequence_id: str, callback_id: str, payload: dict) -> None:
        if callback_id == "battle_intro_announce":
            self.broadcast_l("battle-combat-start", buffer="game")
        elif callback_id == "battle_begin_next_turn":
            self._begin_next_turn()
        elif callback_id == "battle_announce_turn":
            fighter = self._fighter_by_id(str(payload.get("fighter_id", "")))
            if fighter:
                self._announce_current_turn(fighter)
        elif callback_id == "battle_announce_move":
            fighter = self._fighter_by_id(str(payload.get("launcher_id", "")))
            target = self._fighter_by_id(str(payload.get("target_id", "")))
            move = get_move_map().get(str(payload.get("move_id", "")))
            if fighter and target and move:
                self.last_action_message_key = "battle-used-move"
                self.last_action_payload = {
                    "fighter": self._fighter_name(fighter, "en"),
                    "move": self._locale_name(move.name, "en"),
                    "target": self._fighter_name(target, "en"),
                }
                self._announce_move(fighter, target, move)
        elif callback_id == "battle_apply_block":
            fighter = self._fighter_by_id(str(payload.get("launcher_id", "")))
            target = self._fighter_by_id(str(payload.get("target_id", "")))
            move = get_move_map().get(str(payload.get("move_id", "")))
            block_index = int(payload.get("block_index", 0))
            if fighter and target and move and 0 <= block_index < len(move.blocks):
                self._apply_block(fighter, target, move.blocks[block_index])
        elif callback_id == "battle_finalize_move":
            self._post_move_progression()
        elif callback_id == "battle_spawn_intro":
            self.broadcast_l("battle-enemies-arrive", buffer="game", count=int(payload.get("count", 0)))

    def _announce_current_turn(self, fighter: BattleFighter) -> None:
        locale_fighter_names = {player.id: self._fighter_name(fighter, self._player_locale(player)) for player in self.players}
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            if player.id == fighter.owner_player_id and user.preferences.play_turn_sound:
                user.play_sound("turn.ogg")
            user.speak_l("battle-turn-start", buffer="game", fighter=locale_fighter_names[player.id])
        self._queue_bot_turn_if_needed()

    def _announce_move(self, fighter: BattleFighter, target: BattleFighter, move: BattleMove) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            if self._uses_team_context():
                user.speak_l(
                    "battle-used-move-with-teams",
                    buffer="game",
                    fighter=self._fighter_name(fighter, user.locale),
                    fighter_team=self._team_display_name(user.locale, fighter.team_id, player),
                    move=self._locale_name(move.name, user.locale),
                    target=self._fighter_name(target, user.locale),
                    target_team=self._team_display_name(user.locale, target.team_id, player),
                )
            else:
                user.speak_l(
                    "battle-used-move",
                    buffer="game",
                    fighter=self._fighter_name(fighter, user.locale),
                    move=self._locale_name(move.name, user.locale),
                    target=self._fighter_name(target, user.locale),
                )

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status != "playing":
            return
        if self.phase == PHASE_SELECTION:
            if self._all_selection_locked():
                self._start_combat()
            return
        if self.is_sequence_bot_paused():
            return
        fighter = self.current_fighter
        if not fighter or not self._fighter_is_bot_controlled(fighter):
            return
        if self.bot_wait_ticks > 0:
            self.bot_wait_ticks -= 1
            return
        self._perform_bot_turn(fighter)

    def _perform_bot_turn(self, fighter: BattleFighter) -> None:
        move = self._choose_bot_move(fighter)
        if not move:
            self._begin_next_turn()
            return
        targets = self._valid_targets(fighter, move)
        if not targets:
            self._begin_next_turn()
            return
        target = self._choose_bot_target(fighter, move, targets)
        self._begin_move_resolution(fighter, target, move)

    def _choose_bot_move(self, fighter: BattleFighter) -> BattleMove | None:
        moves = [get_move_map()[move_id] for move_id in fighter.move_ids if move_id in get_move_map()]
        if not moves:
            return None
        for move in moves:
            if any(block.type == "healing" for block in move.blocks):
                for target in self._valid_targets(fighter, move):
                    if target.health < target.max_health // 2:
                        return move
        for move in moves:
            for target in self._valid_targets(fighter, move):
                estimated_damage = 0
                for block in move.blocks:
                    if block.type in {"damage", "drain"}:
                        estimated_damage += ((block.min or 0) + (block.max or 0)) // 2 + fighter.attack - target.defense
                if estimated_damage >= target.health:
                    return move
        return random.choice(moves)

    def _choose_bot_target(self, fighter: BattleFighter, move: BattleMove, targets: list[BattleFighter]) -> BattleFighter:
        if any(block.type == "healing" for block in move.blocks):
            return min(targets, key=lambda candidate: candidate.health / max(1, candidate.max_health))
        enemies = [target for target in targets if target.team_id != fighter.team_id]
        if enemies:
            return min(enemies, key=lambda candidate: (candidate.health, candidate.defense))
        return random.choice(targets)

    def create_turn_action_set(self, player: Player) -> ActionSet:
        return ActionSet(name="turn")

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if action_set.get_action("check_scores"):
            action_set.remove("check_scores")
        if action_set.get_action("check_scores_detailed"):
            action_set.remove("check_scores_detailed")
        action_set.add(Action(id="battle_read_status", label=Localization.get(locale, "battle-read-status"), handler="_action_battle_read_status", is_enabled="_is_battle_read_status_enabled", is_hidden="_is_battle_read_status_hidden", include_spectators=True))
        action_set.add(Action(id="battle_read_status_detailed", label=Localization.get(locale, "battle-read-status-detailed"), handler="_action_battle_read_status_detailed", is_enabled="_is_battle_read_status_enabled", is_hidden="_is_battle_read_status_hidden", include_spectators=True))
        action_set.add(Action(id="battle_read_roster", label=Localization.get(locale, "battle-read-roster"), handler="_action_battle_read_roster", is_enabled="_is_battle_read_roster_enabled", is_hidden="_is_battle_read_roster_hidden", include_spectators=True))
        action_set.add(Action(id="battle_read_allied_fighters", label=Localization.get(locale, "battle-read-allied-fighters"), handler="_action_battle_read_allied_fighters", is_enabled="_is_battle_team_roster_enabled", is_hidden="_is_battle_team_roster_hidden"))
        action_set.add(Action(id="battle_read_enemy_fighters", label=Localization.get(locale, "battle-read-enemy-fighters"), handler="_action_battle_read_enemy_fighters", is_enabled="_is_battle_team_roster_enabled", is_hidden="_is_battle_team_roster_hidden"))
        self._apply_standard_action_order(action_set, user)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []
        self.define_keybind("s", Localization.get("en", "battle-read-status"), ["battle_read_status"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+s", Localization.get("en", "battle-read-status-detailed"), ["battle_read_status_detailed"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("v", Localization.get("en", "battle-read-roster"), ["battle_read_roster"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("a", Localization.get("en", "battle-read-allied-fighters"), ["battle_read_allied_fighters"], state=KeybindState.ACTIVE)
        self.define_keybind("e", Localization.get("en", "battle-read-enemy-fighters"), ["battle_read_enemy_fighters"], state=KeybindState.ACTIVE)
        self.define_keybind("u", Localization.get("en", "battle-undo-selection"), ["battle_undo_selection"], state=KeybindState.ACTIVE)
        self.define_keybind("d", Localization.get("en", "battle-done-selecting"), ["battle_done_selecting"], state=KeybindState.ACTIVE)

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
            self._sync_standard_actions(player)
        super().rebuild_all_menus()

    def _sync_standard_actions(self, player: Player) -> None:
        action_set = self.get_action_set(player, "standard")
        if not action_set:
            return
        self._apply_standard_action_order(action_set, self.get_user(player))

    def _apply_standard_action_order(self, action_set: ActionSet, user) -> None:
        custom_ids = ["battle_read_status", "battle_read_status_detailed", "battle_read_roster", "battle_read_allied_fighters", "battle_read_enemy_fighters"]
        action_set._order = [aid for aid in action_set._order if aid not in custom_ids] + [aid for aid in custom_ids if action_set.get_action(aid)]
        if self.is_touch_client(user):
            target_order = ["battle_read_status", "battle_read_status_detailed", "battle_read_roster", "battle_read_allied_fighters", "battle_read_enemy_fighters", "whose_turn", "whos_at_table"]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

    def _sync_turn_actions(self, player: Player) -> None:
        battle_player = self._as_battle_player(player)
        turn_set = self.get_action_set(player, "turn")
        if not battle_player or not turn_set:
            return
        turn_set._actions.clear()
        turn_set._order.clear()
        locale = self._player_locale(battle_player)
        if self.status != "playing" or battle_player.is_spectator:
            return
        if self.phase == PHASE_SELECTION and not battle_player.selection_locked:
            for preset in load_battle_registry().presets:
                turn_set.add(Action(id=f"battle_toggle_preset_{preset.id}", label="", handler="_action_battle_toggle_preset", is_enabled="_is_battle_toggle_preset_enabled", is_hidden="_is_battle_selection_action_hidden", get_label="_get_battle_preset_toggle_label", show_in_actions_menu=False))
            turn_set.add(Action(id="battle_submit_selection", label="", handler="_action_battle_submit_selection", is_enabled="_is_battle_submit_selection_enabled", is_hidden="_is_battle_selection_action_hidden", get_label="_get_battle_submit_selection_label", show_in_actions_menu=False))
            turn_set.add(Action(id="battle_undo_selection", label=Localization.get(locale, "battle-undo-selection"), handler="_action_battle_undo_selection", is_enabled="_is_battle_undo_selection_enabled", is_hidden="_is_hidden", show_in_actions_menu=False))
            turn_set.add(Action(id="battle_done_selecting", label=Localization.get(locale, "battle-done-selecting"), handler="_action_battle_done_selecting", is_enabled="_is_battle_done_selecting_enabled", is_hidden="_is_hidden", show_in_actions_menu=False))
            return
        fighter = self._fighter_for_player(battle_player)
        if not fighter or self.is_sequence_gameplay_locked():
            return
        for move_id in fighter.move_ids:
            move = get_move_map().get(move_id)
            if move:
                input_request = None
                if len(self._valid_targets(fighter, move)) > 1 and not battle_player.is_bot:
                    input_request = MenuInput(
                        prompt="battle-select-target",
                        options="_target_options_for_move",
                        bot_select="_bot_select_target_for_move",
                    )
                turn_set.add(Action(id=f"battle_move_{move_id}", label=self._move_label(locale, move_id), handler="_action_battle_choose_move", is_enabled="_is_battle_choose_move_enabled", is_hidden="_is_battle_choose_move_hidden", input_request=input_request, show_in_actions_menu=False))

    def _is_battle_selection_action_hidden(self, player: Player) -> Visibility:
        battle_player = self._as_battle_player(player)
        if not battle_player or self.status != "playing" or self.phase != PHASE_SELECTION or battle_player.selection_locked:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_battle_toggle_preset_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        battle_player = self._as_battle_player(player)
        if not battle_player or battle_player.selection_locked:
            return "action-not-available"
        return None

    def _is_battle_submit_selection_enabled(self, player: Player) -> str | None:
        battle_player = self._as_battle_player(player)
        if not battle_player or battle_player.selection_locked or self.phase != PHASE_SELECTION:
            return "action-not-available"
        return None

    def _battle_selection_submit_error(self, player: Player) -> str | None:
        battle_player = self._as_battle_player(player)
        if not battle_player:
            return "action-not-available"
        selected_count = len(battle_player.selected_preset_ids)
        required_count = self._selection_limit_for_mode()
        if self._mode_allows_manual_done():
            if selected_count == 0:
                return "battle-selection-none"
            return None
        if selected_count != required_count:
            return "battle-selection-required-count"
        return None

    def _is_battle_undo_selection_enabled(self, player: Player) -> str | None:
        battle_player = self._as_battle_player(player)
        if not battle_player or not battle_player.selected_preset_ids:
            return "battle-selection-none"
        return None

    def _is_battle_done_selecting_enabled(self, player: Player) -> str | None:
        return self._is_battle_submit_selection_enabled(player)

    def _get_battle_preset_toggle_label(self, player: Player, action_id: str) -> str:
        battle_player = self._as_battle_player(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        preset_id = action_id.removeprefix("battle_toggle_preset_")
        preset = get_preset_map().get(preset_id)
        if not preset:
            return action_id
        label = Localization.get(locale, "battle-pick-preset-label", preset=self._preset_label(locale, preset_id), health=preset.health, attack=preset.attack, defense=preset.defense, speed=preset.speed)
        if battle_player and preset_id in battle_player.selected_preset_ids:
            return Localization.get(locale, "battle-fighter-selected", fighter=label)
        return Localization.get(locale, "battle-fighter-unselected", fighter=label)

    def _get_battle_submit_selection_label(self, player: Player, action_id: str) -> str:
        battle_player = self._as_battle_player(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        selected_count = len(battle_player.selected_preset_ids) if battle_player else 0
        required_count = self._selection_limit_for_mode()
        if self._mode_allows_manual_done():
            return Localization.get(locale, "battle-submit-selection", count=selected_count, limit=required_count)
        return Localization.get(locale, "battle-submit-selection-required", count=selected_count, required=required_count)

    def _is_battle_choose_move_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        battle_player = self._as_battle_player(player)
        fighter = self._fighter_for_player(battle_player) if battle_player else None
        if not fighter or self.phase != PHASE_COMBAT:
            return "action-not-available"
        return None

    def _is_battle_choose_move_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE if self.phase == PHASE_COMBAT and self._fighter_for_player(self._as_battle_player(player)) else Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)) and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_battle_read_status_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_battle_read_status_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_battle_read_roster_enabled(self, player: Player) -> str | None:
        if self.phase == PHASE_SELECTION:
            return "battle-roster-unavailable-selection"
        return None if self.status == "playing" else "action-not-playing"

    def _is_battle_read_roster_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_battle_team_roster_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase == PHASE_SELECTION:
            return "battle-roster-unavailable-selection"
        if player.is_spectator or not self._uses_team_context() or not self._team_ids_for_player(player):
            return "battle-team-action-unavailable"
        return None

    def _is_battle_team_roster_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.phase == PHASE_SELECTION or player.is_spectator or not self._uses_team_context() or not self._team_ids_for_player(player):
            return Visibility.HIDDEN
        if self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _announce_selected_fighter(self, player: Player, preset_id: str) -> None:
        self.play_sound(f"battle/appear{random.randint(1, 4)}.ogg", volume=70)
        self._broadcast_game_localized(
            "battle-selected-fighter",
            player=player.name,
            fighter=lambda locale: self._preset_label(locale, preset_id),
        )

    def _action_battle_toggle_preset(self, player: Player, action_id: str) -> None:
        battle_player = self._as_battle_player(player)
        if not battle_player:
            return
        preset_id = action_id.removeprefix("battle_toggle_preset_")
        if preset_id not in get_preset_map():
            return
        if preset_id in battle_player.selected_preset_ids:
            battle_player.selected_preset_ids.remove(preset_id)
        elif len(battle_player.selected_preset_ids) < self._selection_limit_for_mode():
            battle_player.selected_preset_ids.append(preset_id)
        else:
            user = self.get_user(player)
            if user:
                user.speak_l("battle-selection-limit-reached", buffer="game")
        self.rebuild_all_menus()

    def _action_battle_undo_selection(self, player: Player, action_id: str) -> None:
        battle_player = self._as_battle_player(player)
        if battle_player and battle_player.selected_preset_ids:
            battle_player.selected_preset_ids.pop()
            self.rebuild_all_menus()

    def _action_battle_done_selecting(self, player: Player, action_id: str) -> None:
        self._action_battle_submit_selection(player, action_id)

    def _action_battle_submit_selection(self, player: Player, action_id: str) -> None:
        battle_player = self._as_battle_player(player)
        if not battle_player:
            return
        error_key = self._battle_selection_submit_error(player)
        if error_key:
            user = self.get_user(player)
            if user:
                user.speak_l(error_key, buffer="game")
            return
        if not battle_player.is_bot:
            for preset_id in battle_player.selected_preset_ids:
                self._announce_selected_fighter(player, preset_id)
        battle_player.selection_locked = True
        self.broadcast_l("battle-selection-locked", buffer="game", player=player.name)
        self.rebuild_all_menus()

    def _target_option_label(self, locale: str, target: BattleFighter) -> str:
        return self._target_option_label_for_player(locale, target, None)

    def _target_option_label_for_player(self, locale: str, target: BattleFighter, viewer: Player | None) -> str:
        return Localization.get(
            locale,
            "battle-target-option" if self._uses_team_context() else "battle-target-option-no-team",
            fighter=self._fighter_name(target, locale),
            team=self._team_display_name(locale, target.team_id, viewer),
            health=target.health,
        )

    def _target_options_for_move(self, player: Player) -> list[str]:
        fighter = self._fighter_for_player(self._as_battle_player(player))
        action_id = self._pending_actions.get(player.id, "")
        move = get_move_map().get(action_id.removeprefix("battle_move_"))
        if not fighter or not move:
            return []
        locale = self._player_locale(player)
        return [self._target_option_label_for_player(locale, target, player) for target in self._valid_targets(fighter, move)]

    def _bot_select_target_for_move(self, player: Player, options: list[str]) -> str | None:
        return options[0] if options else None

    def _target_from_input(self, input_value: str, locale: str, targets: list[BattleFighter]) -> BattleFighter | None:
        for target in targets:
            if self._target_option_label(locale, target) == input_value:
                return target
        return None

    def _action_battle_choose_move(self, player: Player, *args) -> None:
        fighter = self._fighter_for_player(self._as_battle_player(player))
        if not fighter:
            return
        input_value: str | None = None
        if len(args) == 1:
            action_id = args[0]
        elif len(args) == 2:
            input_value, action_id = args
        else:
            return
        move_id = action_id.removeprefix("battle_move_")
        move = get_move_map().get(move_id)
        if not move:
            return
        targets = self._valid_targets(fighter, move)
        if not targets:
            user = self.get_user(player)
            if user:
                user.speak_l("battle-no-valid-targets", buffer="game")
            return
        if len(targets) == 1:
            self._begin_move_resolution(fighter, targets[0], move)
            return
        if input_value is not None:
            target = self._target_from_input(input_value, self._player_locale(player), targets)
            if target:
                self._begin_move_resolution(fighter, target, move)
            return
        self.rebuild_all_menus()

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        fighter = self.current_fighter
        if not user:
            return
        if self.phase == PHASE_SELECTION:
            user.speak_l("battle-whose-turn-selection", buffer="game")
            return
        if fighter:
            user.speak_l(
                "battle-whose-turn-combat",
                buffer="game",
                fighter=self._fighter_name(fighter, user.locale),
                health=fighter.health,
                team=self._team_display_name(user.locale, fighter.team_id, player),
            )
        else:
            user.speak_l("game-no-turn", buffer="game")

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        self._action_battle_read_status(player, action_id)

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        self._action_battle_read_status_detailed(player, action_id)

    def _battle_status_lines(self, locale: str, *, detailed: bool, viewer: Player | None = None) -> list[str]:
        lines = [Localization.get(locale, "battle-status-header")]
        if self.phase == PHASE_SELECTION:
            lines.append(Localization.get(locale, "battle-selection-phase"))
            for active_player in self.get_active_players():
                battle_player = self._as_battle_player(active_player)
                if battle_player:
                    lines.append(Localization.get(locale, "battle-selection-score-line", player=active_player.name, picks=self._selection_summary(locale, battle_player)))
            return lines
        current = self.current_fighter
        if current:
            lines.append(Localization.get(locale, "battle-turn-start", fighter=self._fighter_name(current, locale)))
        lines.append(Localization.get(locale, "battle-score-summary", fighters=len(self._alive_fighters()), teams=len(self._alive_team_ids()), kills=self.survival_kills))
        if self._survival_options_are_active():
            lines.append(self._mode_progress_line(locale, kills=self.survival_kills, wave=self.survival_wave))
        if detailed:
            lines.append(Localization.get(locale, "battle-roster-header"))
            for fighter in self.fighters:
                lines.append(self._fighter_summary_line(locale, fighter, viewer))
        return lines

    def _action_battle_read_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = self._battle_status_lines(user.locale, detailed=False, viewer=player)
        for line in lines:
            user.speak(line, buffer="game")

    def _action_battle_read_status_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.status_box(player, self._battle_status_lines(user.locale, detailed=True, viewer=player))

    def _action_battle_read_roster(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "battle-roster-header")]
        for fighter in self.fighters:
            lines.append(self._fighter_summary_line(user.locale, fighter, player))
        self.status_box(player, lines)

    def _team_filtered_roster(self, player: Player, *, allies: bool) -> list[BattleFighter]:
        player_team_ids = self._team_ids_for_player(player)
        if allies:
            return [
                fighter
                for fighter in self.fighters
                if fighter.team_id in player_team_ids and self._is_fighter_active(fighter)
            ]
        return [
            fighter
            for fighter in self.fighters
            if fighter.team_id not in player_team_ids and self._is_fighter_active(fighter)
        ]

    def _show_team_filtered_roster(self, player: Player, *, allies: bool) -> None:
        user = self.get_user(player)
        if not user:
            return
        header = "battle-allied-roster-header" if allies else "battle-enemy-roster-header"
        lines = [Localization.get(user.locale, header)]
        for fighter in self._team_filtered_roster(player, allies=allies):
            lines.append(self._fighter_summary_line(user.locale, fighter, player))
        if len(lines) == 1:
            lines.append(Localization.get(user.locale, "battle-no-fighters-in-list"))
        self.status_box(player, lines)

    def _action_battle_read_allied_fighters(self, player: Player, action_id: str) -> None:
        self._show_team_filtered_roster(player, allies=True)

    def _action_battle_read_enemy_fighters(self, player: Player, action_id: str) -> None:
        self._show_team_filtered_roster(player, allies=False)

    def build_game_result(self) -> GameResult:
        winner_ids = []
        if self.winning_team_id:
            winner_ids = [player.id for player in self.get_active_players() if any(fighter.owner_player_id == player.id and fighter.team_id == self.winning_team_id for fighter in self.fighters)]
        custom_data = {
            "winning_team_id": self.winning_team_id,
            "winner_ids": winner_ids,
        }
        if self._survival_options_are_active():
            custom_data["survival_kills"] = self.survival_kills
            custom_data["survival_wave"] = self.survival_wave
            player_stats: dict[str, dict[str, int]] = {}
            for player in self.get_active_players():
                stats = {"survival_kills": self.survival_kills}
                if self._is_wave_mode():
                    stats["deepest_wave"] = self.survival_wave
                player_stats[player.id] = stats
            custom_data["player_stats"] = player_stats
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[PlayerResult(player_id=player.id, player_name=player.name, is_bot=player.is_bot and not player.replaced_human) for player in self.get_active_players()],
            custom_data=custom_data,
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "battle-end-header")]
        team_id = result.custom_data.get("winning_team_id", "")
        if team_id:
            lines.append(Localization.get(locale, "battle-end-winner", team=self._result_team_display_name(locale, team_id)))
        else:
            lines.append(Localization.get(locale, "battle-end-draw"))
        if self._survival_options_are_active():
            lines.append(
                self._mode_progress_line(
                    locale,
                    kills=result.custom_data.get("survival_kills", 0),
                    wave=result.custom_data.get("survival_wave", 1),
                )
            )
        return lines

    def _finish_with_team_result(self, team_id: str) -> None:
        self.winning_team_id = team_id
        self.finish_game()
