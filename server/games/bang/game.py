"""Audio-first implementation of BANG! The Bullet, second edition."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.menu_management_mixin import StatusBoxBuild
from ...game_utils.options import BoolOption, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_CARDS
from ..registry import register_game
from . import audio as game_audio
from . import cards
from .bot import choose_action as choose_bot_action
from .cards import (
    BangCard,
    BangInPlayCard,
    card_description,
    card_label,
    card_name,
    card_play_name,
    sort_cards,
)
from .characters import (
    ALL_CHARACTERS,
    CHARACTERS,
    character_ability,
    character_name,
)
from .events import (
    COMBINED_EVENTS,
    EVENT_MODES,
    FISTFUL_OF_CARDS,
    HIGH_NOON,
    NO_EVENTS,
    build_event_deck,
    event_description,
    event_name,
)
from .player import BangPlayer
from .state import (
    PHASE_DISCARD,
    PHASE_DRAW,
    PHASE_GAME_OVER,
    PHASE_PLAY,
    PHASE_RESOLVING,
    PHASE_START_TURN,
    PHASE_STARTING,
    BangDecision,
    BangEffect,
    BangPlayIntent,
    DamageSource,
    ResolvingCard,
)

ROLE_SHERIFF = "sheriff"
ROLE_DEPUTY = "deputy"
ROLE_OUTLAW = "outlaw"
ROLE_RENEGADE = "renegade"

EVENT_RULE_LABELS = {
    NO_EVENTS: "bang-event-mode-none",
    "high_noon": "bang-event-mode-high-noon",
    "fistful": "bang-event-mode-fistful",
    COMBINED_EVENTS: "bang-event-mode-combined",
}

MAX_EFFECT_STEPS = 200
BOT_TURN_DELAY_TICKS = (22, 36)
BOT_CHOICE_DELAY_TICKS = (12, 22)


@dataclass
class BangOptions(GameOptions):
    """Player-facing content and event-rule options."""

    expanded_cards: bool = option_field(
        BoolOption(
            default=True,
            label="bang-option-expanded-cards",
            change_msg="bang-option-changed-expanded-cards",
            description="bang-option-expanded-cards-description",
        )
    )
    event_rules: str = option_field(
        MenuOption(
            choices=list(EVENT_MODES),
            default=COMBINED_EVENTS,
            value_key="mode",
            label="bang-option-event-rules",
            prompt="bang-option-event-rules-prompt",
            change_msg="bang-option-changed-event-rules",
            choice_labels=EVENT_RULE_LABELS,
            description="bang-option-event-rules-description",
        )
    )


@register_game
@dataclass
class BangGame(Game):
    """BANG! with every rule component included in The Bullet."""

    players: list[BangPlayer] = field(default_factory=list)
    options: BangOptions = field(default_factory=BangOptions)
    deck: list[BangCard] = field(default_factory=list)
    discard_pile: list[BangCard] = field(default_factory=list)
    event_deck: list[str] = field(default_factory=list)
    current_event: str = ""
    phase: str = PHASE_STARTING
    effect_stack: list[BangEffect] = field(default_factory=list)
    decision: BangDecision | None = None
    play_intent: BangPlayIntent | None = None
    resolving_card: ResolvingCard | None = None
    revealed_cards: list[BangCard] = field(default_factory=list)
    general_store_cards: list[BangCard] = field(default_factory=list)
    turn_serial: int = 0
    sheriff_turns_started: int = 0
    elimination_counter: int = 0
    first_eliminated_id: str = ""
    dead_man_used: bool = False
    three_player_last_standing: bool = False
    winner_ids: list[str] = field(default_factory=list)
    winning_side: str = ""
    audio_sequence_serial: int = 0
    last_elimination_fall_tick: int = -1
    final_showdown_music_started: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "BANG! The Bullet"

    @classmethod
    def get_type(cls) -> str:
        return "bang"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_CARDS

    @classmethod
    def get_min_players(cls) -> int:
        return 3

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def supports_score_actions(self) -> bool:
        return False

    def create_player(
        self,
        player_id: str,
        name: str,
        is_bot: bool = False,
    ) -> BangPlayer:
        return BangPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = []
        count = self.get_active_player_count()
        if not self.options.expanded_cards and count not in range(4, 8):
            errors.append("bang-error-base-player-count")
        if self.options.event_rules not in EVENT_MODES:
            errors.append("bang-error-event-mode")
        return errors

    def rebuild_runtime_state(self) -> None:
        super().rebuild_runtime_state()
        self._repair_restored_state()

    @property
    def seated_players(self) -> list[BangPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, BangPlayer)
        ]

    @property
    def players_in_play(self) -> list[BangPlayer]:
        return [
            player
            for player in self.seated_players
            if not player.eliminated or player.ghost_active
        ]

    def _player_in_play(self, player: Player | None) -> bool:
        return (
            isinstance(player, BangPlayer)
            and not player.is_spectator
            and (not player.eliminated or player.ghost_active)
        )

    def _roles_for_count(self, count: int) -> list[str]:
        if count == 3:
            return [ROLE_DEPUTY, ROLE_OUTLAW, ROLE_RENEGADE]
        distributions = {
            4: [ROLE_SHERIFF, ROLE_RENEGADE, ROLE_OUTLAW, ROLE_OUTLAW],
            5: [
                ROLE_SHERIFF,
                ROLE_RENEGADE,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_DEPUTY,
            ],
            6: [
                ROLE_SHERIFF,
                ROLE_RENEGADE,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_DEPUTY,
            ],
            7: [
                ROLE_SHERIFF,
                ROLE_RENEGADE,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_DEPUTY,
                ROLE_DEPUTY,
            ],
            8: [
                ROLE_SHERIFF,
                ROLE_RENEGADE,
                ROLE_RENEGADE,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_OUTLAW,
                ROLE_DEPUTY,
                ROLE_DEPUTY,
            ],
        }
        return list(distributions.get(count, []))

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1
        self.phase = PHASE_STARTING
        self.effect_stack.clear()
        self.decision = None
        self.play_intent = None
        self.resolving_card = None
        self.revealed_cards.clear()
        self.general_store_cards.clear()
        self.discard_pile.clear()
        self.current_event = ""
        self.turn_serial = 0
        self.sheriff_turns_started = 0
        self.elimination_counter = 0
        self.first_eliminated_id = ""
        self.dead_man_used = False
        self.three_player_last_standing = False
        self.winner_ids.clear()
        self.winning_side = ""
        self.audio_sequence_serial = 0
        self.last_elimination_fall_tick = -1
        self.final_showdown_music_started = False
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        active = self.seated_players
        roles = self._roles_for_count(len(active))
        random.shuffle(roles)
        characters = [
            definition
            for definition in ALL_CHARACTERS
            if self.options.expanded_cards
            or definition.expansion != cards.DODGE_CITY
        ]
        if self.options.expanded_cards:
            characters = list(ALL_CHARACTERS)
        random.shuffle(characters)

        for player, role in zip(active, roles):
            player.role = role
            player.role_revealed = len(active) == 3 or role == ROLE_SHERIFF
            player.character = characters.pop().id
            player.alternate_character = characters.pop().id
            player.copied_character = ""
            player.hand.clear()
            player.in_play.clear()
            player.eliminated = False
            player.ghost_active = False
            player.elimination_order = 0
            player.molly_deferred_draws = 0
            player.vendetta_extra_turn = False
            player.bot_role_suspicion.clear()
            self._reset_turn_counters(player)
            base_life = CHARACTERS[player.character].life
            player.max_life = base_life + int(role == ROLE_SHERIFF)
            player.life = player.max_life

        self.deck = cards.build_deck(
            include_extended_cards=self.options.expanded_cards
        )
        random.shuffle(self.deck)
        self.event_deck = build_event_deck(self.options.event_rules)

        for player in active:
            player.hand = sort_cards(
                [card for _ in range(player.life) if (card := self._draw_one())]
            )

        self.set_turn_players(active)
        starter_role = ROLE_DEPUTY if len(active) == 3 else ROLE_SHERIFF
        starter = next(player for player in active if player.role == starter_role)
        self.current_player = starter
        self.play_ambience(game_audio.SOUND_AMBIENCE_WESTERN)
        self.start_sequence(
            self._next_audio_sequence_id("game_intro"),
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            game_audio.SOUND_GAME_INTRO
                        )
                    ],
                    delay_after_ticks=game_audio.GAME_START_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "finish_game_start"
                        )
                    ]
                ),
            ],
            tag="bang_game_intro",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.broadcast_l(
            "bang-intro-history",
            buffer="game",
        )
        self.refresh_menus()

    def _finish_game_start(self) -> None:
        """Begin the first turn after the opening audio has established the scene."""

        if (
            not self.game_active
            or self.status != "playing"
            or self.phase != PHASE_STARTING
        ):
            return
        self.phase = PHASE_START_TURN
        self.play_music(game_audio.SOUND_MUSIC_GAMEPLAY)
        self.broadcast_l(
            "bang-game-started",
            buffer="game",
        )
        self._announce_public_roles()
        for player in self.seated_players:
            self._speak_setup(player)
        self.announce_turn()
        self._begin_turn()
        self._pace_bots()
        self.refresh_menus()

    def _speak_setup(self, player: BangPlayer) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "bang-your-setup",
            buffer="game",
            role=self._role_name(player.role, user.locale),
            character=character_name(player.character, user.locale),
            life=player.life,
            objective=Localization.get(
                user.locale,
                self._starting_objective_key(player),
            ),
        )

    def _announce_public_roles(self) -> None:
        public_players = [
            player for player in self.seated_players if player.role_revealed
        ]
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            entries = [
                Localization.get(
                    user.locale,
                    "bang-public-role-entry",
                    player=player.name,
                    role=self._role_name(player.role, user.locale),
                )
                for player in public_players
            ]
            user.speak_l(
                "bang-public-roles",
                buffer="game",
                count=len(entries),
                roles=Localization.format_list_and(user.locale, entries),
            )

    def _starting_objective_key(self, player: BangPlayer) -> str:
        mode = "three" if len(self.seated_players) == 3 else "standard"
        return f"bang-objective-{mode}-{player.role}"

    # ------------------------------------------------------------------
    # Audio routing
    # ------------------------------------------------------------------

    @staticmethod
    def _random_sound(sounds: tuple[str, ...]) -> str:
        return random.choice(sounds)  # nosec B311 - cosmetic variation

    def _next_audio_sequence_id(self, kind: str) -> str:
        self.audio_sequence_serial += 1
        return f"bang_{kind}_{self.audio_sequence_serial}"

    def _stagger_effect_audio(
        self,
        duration_ticks: int,
        *,
        wait_ratio: float,
    ) -> None:
        """Resume effects after the context-appropriate portion of a cue."""

        self.start_sequence(
            self._next_audio_sequence_id("effect_gap"),
            [
                SequenceBeat.after_audio(
                    max(0, duration_ticks),
                    wait_ratio=wait_ratio,
                ),
                SequenceBeat(),
            ],
            tag="bang_effect_gap",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _wait_until_effect_tick(self, target_tick: int) -> bool:
        """Lock effect resolution until a previously computed audio deadline."""

        remaining_ticks = max(0, target_tick - self.sound_scheduler_tick)
        if not remaining_ticks:
            return False
        self.start_sequence(
            self._next_audio_sequence_id("effect_deadline"),
            [
                SequenceBeat.pause(remaining_ticks),
                SequenceBeat(),
            ],
            tag="bang_effect_gap",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        return True

    def _play_or_schedule_elimination_fall(self) -> None:
        """Emit a fall without blocking, spacing concurrent deaths by one tick."""

        fall_sound = self._random_sound(game_audio.SOUND_ELIMINATION_FALLS)
        current_tick = self.sound_scheduler_tick
        target_tick = max(
            current_tick,
            self.last_elimination_fall_tick
            + game_audio.ELIMINATION_FALL_STAGGER_TICKS,
        )
        self.last_elimination_fall_tick = target_tick
        delay_ticks = target_tick - current_tick
        if delay_ticks:
            self.schedule_sound(fall_sound, delay_ticks=delay_ticks)
        else:
            self.play_sound(fall_sound)

    def _effective_weapon_kind(self, player: BangPlayer) -> str:
        weapon = self._equipped_weapon(player)
        if weapon and self._in_play_effects_active(player):
            return weapon.kind
        return "colt45"

    def _attack_fire_sounds(
        self,
        actor: BangPlayer | None,
        source_kind: str,
    ) -> tuple[str, ...]:
        dedicated = game_audio.ATTACK_FIRE_SOUNDS.get(source_kind)
        if dedicated:
            return dedicated
        if actor:
            weapon_kind = self._effective_weapon_kind(actor)
            if weapon_kind != "colt45":
                return game_audio.WEAPON_FIRE_SOUNDS[weapon_kind]
        return game_audio.SOUND_FIRE_COLT45

    def _play_attack_sound(
        self,
        actor: BangPlayer | None,
        source_kind: str,
        *,
        schedule_casing: bool = True,
    ) -> int:
        sound = self._random_sound(
            self._attack_fire_sounds(actor, source_kind)
        )
        self.play_sound(sound)
        sound_duration = game_audio.sound_ticks(sound)
        if (
            schedule_casing
            and source_kind not in game_audio.NON_FIREARM_ATTACKS
        ):
            casing = self._random_sound(game_audio.SOUND_CASING_DROPS)
            casing_delay = SequenceBeat.audio_delay_ticks(
                sound_duration,
                wait_ratio=game_audio.WAIT_RATIO_CASING,
            )
            self.schedule_sound(
                casing,
                delay_ticks=casing_delay,
            )
        return sound_duration

    @staticmethod
    def _attack_wait_ratio(source_kind: str) -> float:
        if source_kind in game_audio.NON_FIREARM_ATTACKS:
            return game_audio.WAIT_RATIO_SHORT_CUE
        if source_kind == cards.HOWITZER:
            return game_audio.WAIT_RATIO_LONG_EFFECT
        return game_audio.WAIT_RATIO_GUNSHOT

    @staticmethod
    def _impact_wait_ratio(source: DamageSource) -> float:
        if source.kind == cards.PUNCH:
            return game_audio.WAIT_RATIO_SHORT_CUE
        return game_audio.WAIT_RATIO_IMPACT

    def _play_equipment_sound(self, card_kind: str) -> None:
        sound = game_audio.EQUIPMENT_SOUNDS.get(card_kind)
        if sound:
            self.play_sound(sound)

    def _play_consumable_sound(self, card_kind: str) -> None:
        sound = game_audio.CONSUMABLE_SOUNDS.get(card_kind)
        if sound:
            self.play_sound(sound)

    def _play_card_draw_sound(self) -> None:
        self.play_sound(self._random_sound(game_audio.SOUND_CARD_DRAW))

    def _play_card_discard_sound(self) -> None:
        self.play_sound(self._random_sound(game_audio.SOUND_CARD_DISCARD))

    @staticmethod
    def _card_has_immediate_sound(
        card: BangCard,
        *,
        as_bang: bool,
    ) -> bool:
        if card.kind == cards.BANG or as_bang:
            return True
        if card.border in {cards.BLUE, cards.GREEN}:
            return card.kind in game_audio.EQUIPMENT_SOUNDS
        return (
            card.kind in game_audio.CONSUMABLE_SOUNDS
            or card.kind in game_audio.ATTACK_FIRE_SOUNDS
        )

    def _play_defense_sound(
        self,
        card: BangCard | None = None,
        *,
        russian_roulette: bool = False,
        source_kind: str = "",
    ) -> int:
        if russian_roulette and (
            card is None
            or card.kind
            not in {
                cards.BIBLE,
                cards.IRON_PLATE,
                cards.SOMBRERO,
                cards.TEN_GALLON_HAT,
            }
        ):
            self.play_sound(game_audio.SOUND_WEAPON_EMPTY)
            casing = self._random_sound(game_audio.SOUND_ROULETTE_CASINGS)
            casing_delay = game_audio.sound_ticks(
                game_audio.SOUND_WEAPON_EMPTY
            )
            self.schedule_sound(
                casing,
                delay_ticks=casing_delay,
            )
            return max(
                casing_delay,
                casing_delay + game_audio.sound_ticks(casing),
            )
        sounds = (
            game_audio.DEFENSE_CARD_SOUNDS.get(card.kind)
            if card
            else None
        )
        if sounds:
            sound = self._random_sound(sounds)
        elif source_kind == cards.KNIFE:
            sound = game_audio.SOUND_DEFENSE_BLADE_DODGE
        elif source_kind == cards.PUNCH:
            sound = game_audio.SOUND_DEFENSE_BLUNT_DODGE
        else:
            sound = self._random_sound(game_audio.SOUND_DEFENSE_DODGE)
        self.play_sound(sound)
        return game_audio.sound_ticks(sound)

    def _play_damage_impact(self, source: DamageSource) -> int:
        if source.kind == "dynamite":
            return 0
        if source.kind == "russian_roulette":
            sounds = (game_audio.SOUND_ROULETTE_BULLET_HIT,)
        elif source.kind == "indians":
            sounds = (game_audio.SOUND_IMPACT_GENERIC,)
        elif source.kind == cards.HOWITZER:
            sounds = (game_audio.SOUND_IMPACT_HOWITZER,)
        elif source.kind == cards.KNIFE:
            sounds = game_audio.SOUND_IMPACT_KNIFE
        elif source.kind == cards.PUNCH:
            sounds = game_audio.SOUND_IMPACT_PUNCH
        elif source.kind == "sniper":
            sounds = game_audio.SOUND_IMPACT_SNIPER
        elif source.kind in {
            "bang_card",
            "missed_as_bang",
            "doc_holyday",
            cards.BUFFALO_RIFLE,
            cards.DERRINGER,
            cards.GATLING,
            cards.PEPPERBOX,
            cards.SPRINGFIELD,
            "fistful_of_cards",
            "duel",
        }:
            sounds = game_audio.SOUND_IMPACT_BULLET_BODY
        else:
            sounds = (game_audio.SOUND_IMPACT_GENERIC,)
        sound = self._random_sound(sounds)
        self.play_sound(sound)
        return game_audio.sound_ticks(sound)

    # ------------------------------------------------------------------
    # Actions and menu projection
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: Player) -> ActionSet:
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="input_prompt",
                label=Localization.get(locale, "bang-prompt-play-turn"),
                handler="_action_repeat_input_prompt",
                is_enabled="_is_input_prompt_enabled",
                is_hidden="_is_input_prompt_hidden",
                get_label="_get_input_prompt_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="end_or_confirm",
                label=Localization.get(locale, "bang-keybind-end-or-confirm"),
                handler="_action_end_or_confirm",
                is_enabled="_is_end_or_confirm_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )
        fixed = (
            (
                "confirm_selection",
                "bang-action-confirm",
                "_action_confirm_selection",
                "_is_confirm_enabled",
                "_is_confirm_hidden",
            ),
            (
                "cancel_selection",
                "bang-action-cancel",
                "_action_cancel_selection",
                "_is_cancel_enabled",
                "_is_cancel_hidden",
            ),
            (
                "end_turn",
                "bang-action-end-turn",
                "_action_end_turn",
                "_is_end_turn_enabled",
                "_is_end_turn_hidden",
            ),
            (
                "sid_ketchum",
                "bang-action-sid-ketchum",
                "_action_sid_ketchum",
                "_is_sid_enabled",
                "_is_sid_hidden",
            ),
            (
                "doc_holyday",
                "bang-action-doc-holyday",
                "_action_doc_holyday",
                "_is_doc_enabled",
                "_is_doc_hidden",
            ),
            (
                "chuck_wengam",
                "bang-action-chuck-wengam",
                "_action_chuck_wengam",
                "_is_chuck_enabled",
                "_is_chuck_hidden",
            ),
            (
                "jose_delgado",
                "bang-action-jose-delgado",
                "_action_jose_delgado",
                "_is_jose_enabled",
                "_is_jose_hidden",
            ),
            (
                "uncle_will",
                "bang-action-uncle-will",
                "_action_uncle_will",
                "_is_uncle_enabled",
                "_is_uncle_hidden",
            ),
            (
                "sniper",
                "bang-action-sniper",
                "_action_sniper",
                "_is_sniper_enabled",
                "_is_sniper_hidden",
            ),
            (
                "ricochet",
                "bang-action-ricochet",
                "_action_ricochet",
                "_is_ricochet_enabled",
                "_is_ricochet_hidden",
            ),
        )
        for action_id, label, handler, enabled, hidden in fixed:
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label),
                    handler=handler,
                    is_enabled=enabled,
                    is_hidden=hidden,
                    get_label=(
                        "_get_confirm_selection_label"
                        if action_id == "confirm_selection"
                        else None
                    ),
                    show_in_actions_menu=False,
                )
            )
        self._sync_turn_actions(player, action_set)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        action_set.remove("check_scores")
        action_set.remove("check_scores_detailed")
        user = self.get_user(player)
        locale = user.locale if user else "en"
        specs = (
            (
                "read_life",
                "bang-action-read-life",
                "_action_read_life",
                "_is_private_info_enabled",
                False,
            ),
            (
                "read_role",
                "bang-action-read-role",
                "_action_read_role",
                "_is_private_info_enabled",
                False,
            ),
            (
                "read_distances",
                "bang-action-read-distances",
                "_action_read_distances",
                "_is_private_info_enabled",
                False,
            ),
            (
                "read_piles",
                "bang-action-read-piles",
                "_action_read_piles",
                "_is_public_info_enabled",
                True,
            ),
            (
                "read_event",
                "bang-action-read-event",
                "_action_read_event",
                "_is_public_info_enabled",
                True,
            ),
            (
                "read_table",
                "bang-action-read-table",
                "_action_read_table",
                "_is_public_info_enabled",
                True,
            ),
            (
                "read_hand",
                "bang-action-read-hand",
                "_action_read_hand",
                "_is_private_info_enabled",
                False,
            ),
        )
        for action_id, label, handler, enabled, spectators in specs:
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label),
                    handler=handler,
                    is_enabled=enabled,
                    is_hidden="_is_info_hidden",
                    include_spectators=spectators,
                )
            )
        if self.is_touch_client(user):
            info_action_ids = [action_id for action_id, *_ in specs]
            self._order_touch_standard_actions(
                action_set,
                [
                    *info_action_ids,
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "h",
            Localization.get("en", "bang-action-read-hand"),
            ["read_hand"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "r",
            Localization.get("en", "bang-action-read-role"),
            ["read_role"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "l",
            Localization.get("en", "bang-action-read-life"),
            ["read_life"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "d",
            Localization.get("en", "bang-action-read-distances"),
            ["read_distances"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "p",
            Localization.get("en", "bang-action-read-piles"),
            ["read_piles"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            Localization.get("en", "bang-action-read-event"),
            ["read_event"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "v",
            Localization.get("en", "bang-action-read-table"),
            ["read_table"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "space",
            Localization.get("en", "bang-keybind-end-or-confirm"),
            ["end_or_confirm"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "x",
            Localization.get("en", "bang-action-cancel"),
            ["cancel_selection"],
            state=KeybindState.ACTIVE,
        )

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def _sync_turn_actions(
        self,
        player: Player,
        action_set: ActionSet | None = None,
    ) -> None:
        if not isinstance(player, BangPlayer):
            return
        if action_set is None:
            action_set = self.get_action_set(player, "turn")
        if action_set is None:
            return
        for prefix in ("play_card_", "use_in_play_", "choose_player_", "choice_"):
            action_set.remove_by_prefix(prefix)

        user = self.get_user(player)
        locale = user.locale if user else "en"
        player.hand[:] = sort_cards(player.hand)
        for card in player.hand:
            action_set.add(
                Action(
                    id=f"play_card_{card.id}",
                    label=card_play_name(card, locale),
                    handler="_action_play_card",
                    is_enabled="_is_play_card_enabled",
                    is_hidden="_is_play_card_hidden",
                    get_label="_get_play_card_label",
                    get_description="_get_card_action_description",
                    show_in_actions_menu=False,
                )
            )
        for in_play in player.in_play:
            action_set.add(
                Action(
                    id=f"use_in_play_{in_play.card.id}",
                    label=Localization.get(
                        locale,
                        "bang-use-card",
                        card=card_label(in_play.card, locale),
                    ),
                    handler="_action_use_in_play",
                    is_enabled="_is_use_in_play_enabled",
                    is_hidden="_is_use_in_play_hidden",
                    get_description="_get_card_action_description",
                    show_in_actions_menu=False,
                )
            )

        owner = self._private_choice_owner()
        if owner and owner.id == player.id:
            player_ids: list[str] = []
            item_ids: list[str] = []
            if self.decision and self.decision.player_id == player.id:
                player_ids = list(self.decision.player_ids)
                item_ids = list(self.decision.item_ids)
            elif self.play_intent and self.play_intent.actor_id == player.id:
                if self.play_intent.stage == "target":
                    player_ids = [
                        target.id
                        for target in self._targets_for_intent(self.play_intent)
                    ]
                if self.play_intent.stage == "in_play_target":
                    item_ids = self._in_play_choice_ids(
                        self.play_intent.data.get("mode", ""),
                    )
            for player_id in player_ids:
                target = self.get_player_by_id(player_id)
                if not isinstance(target, BangPlayer):
                    continue
                action_set.add(
                    Action(
                        id=f"choose_player_{target.id}",
                        label=Localization.get(
                            locale,
                            "bang-choose-player",
                            player=target.name,
                            life=target.life,
                            cards=len(target.hand),
                            character=character_name(
                                target.character,
                                locale,
                            ),
                        ),
                        handler="_action_choose_player",
                        is_enabled="_is_choice_enabled",
                        is_hidden="_is_choice_hidden",
                        get_label="_get_choose_player_label",
                        show_in_actions_menu=False,
                    )
                )
            for item_id in item_ids:
                action_set.add(
                    Action(
                        id=f"choice_{item_id}",
                        label=self._choice_label(player, item_id, locale),
                        handler="_action_choose_item",
                        is_enabled="_is_choice_enabled",
                        is_hidden="_is_choice_hidden",
                        get_label="_get_choice_item_label",
                        get_description="_get_card_action_description",
                        show_in_actions_menu=False,
                    )
                )

        hand_ids = [f"play_card_{card.id}" for card in player.hand]
        green_ids = [
            f"use_in_play_{in_play.card.id}" for in_play in player.in_play
        ]
        choice_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith(("choose_player_", "choice_"))
        ]
        selection_controls = [
            action_id
            for action_id, visibility in (
                ("confirm_selection", self._is_confirm_hidden(player)),
                ("cancel_selection", self._is_cancel_hidden(player)),
            )
            if visibility is Visibility.VISIBLE
        ]
        if self.phase == PHASE_STARTING:
            action_set._order = []
        elif (
            self.decision
            and self.decision.player_id == player.id
            and self.decision.kind == "elimination_discard"
        ):
            action_set._order = ["input_prompt"] + hand_ids + choice_ids
        elif choice_ids:
            action_set._order = (
                ["input_prompt"]
                + hand_ids
                + green_ids
                + choice_ids
                + selection_controls
            )
        elif self.decision and self.decision.player_id == player.id:
            action_set._order = (
                ["input_prompt"]
                + hand_ids
                + green_ids
                + selection_controls
            )
        elif self.play_intent and self.play_intent.actor_id == player.id:
            action_set._order = (
                ["input_prompt"] + hand_ids + selection_controls
            )
        else:
            utilities = [
                "sid_ketchum",
                "doc_holyday",
                "chuck_wengam",
                "jose_delgado",
                "uncle_will",
                "sniper",
                "ricochet",
            ]
            prefix = (
                ["input_prompt"]
                if (
                    self.phase == PHASE_PLAY
                    and self.current_player is player
                    and self._player_in_play(player)
                    and not self.effect_stack
                )
                else []
            )
            action_set._order = (
                prefix + hand_ids + green_ids + utilities + ["end_turn"]
            )

    def _private_choice_owner(self) -> BangPlayer | None:
        player_id = ""
        if self.decision:
            player_id = self.decision.player_id
        elif self.play_intent:
            player_id = self.play_intent.actor_id
        player = self.get_player_by_id(player_id)
        return player if isinstance(player, BangPlayer) else None

    # ------------------------------------------------------------------
    # Visibility, validation, and labels
    # ------------------------------------------------------------------

    def _card_id_from_action(self, action_id: str | None) -> int:
        if not action_id:
            return 0
        try:
            return int(action_id.rsplit("_", 1)[-1])
        except (TypeError, ValueError):
            return 0

    def _card_in_hand(
        self,
        player: BangPlayer,
        card_id: int,
    ) -> BangCard | None:
        return next((card for card in player.hand if card.id == card_id), None)

    def _in_play_by_id(
        self,
        card_id: int,
    ) -> tuple[BangPlayer, BangInPlayCard] | None:
        for owner in self.seated_players:
            for in_play in owner.in_play:
                if in_play.card.id == card_id:
                    return owner, in_play
        return None

    def _active_decision_for(self, player: Player) -> bool:
        return bool(self.decision and self.decision.player_id == player.id)

    def _source_context(self, frame: BangEffect, locale: str) -> str:
        source = Localization.get(
            locale,
            f"bang-source-{frame.source.kind.replace('_', '-')}",
        )
        actor = self.get_player_by_id(
            frame.source.player_id or frame.actor_id
        )
        if isinstance(actor, BangPlayer):
            return Localization.get(
                locale,
                "bang-source-by-player",
                player=actor.name,
                source=source,
            )
        return source

    def _decision_prompt(
        self,
        player: BangPlayer,
        locale: str,
    ) -> tuple[str, dict[str, Any]] | None:
        decision = self.decision
        if not decision or decision.player_id != player.id:
            return None
        kwargs: dict[str, Any] = {}
        frame = self._top_effect() if self.effect_stack else None
        if decision.kind in {"barrel", "missed"} and frame:
            kwargs = {
                "source": self._source_context(frame, locale),
                "remaining": int(frame.data.get("misses_remaining", 1)),
                "damage": int(frame.data.get("damage_amount", 1)),
            }
        elif decision.kind == "indians" and frame:
            kwargs = {"source": self._source_context(frame, locale)}
        elif decision.kind == "duel" and frame:
            other_id = (
                frame.actor_id
                if player.id == frame.target_id
                else frame.target_id
            )
            opponent = self.get_player_by_id(other_id)
            kwargs = {
                "opponent": opponent.name if opponent else "",
            }
        elif decision.kind == "general_store":
            kwargs = {"count": len(self.general_store_cards)}
        elif decision.kind == "target_card":
            target = self.get_player_by_id(
                str(decision.data.get("target_id", ""))
            )
            mode = str(decision.data.get("mode", "discard"))
            kwargs = {
                "target": target.name if target else "",
                "mode": Localization.get(
                    locale,
                    f"bang-target-mode-{mode.replace('_', '-')}",
                ),
            }
        elif decision.kind == "ricochet" and frame:
            found = (
                self._in_play_by_id(frame.card_ids[0])
                if frame.card_ids
                else None
            )
            kwargs = {
                "source": self._source_context(frame, locale),
                "card": (
                    card_label(found[1].card, locale)
                    if found
                    else Localization.get(locale, "bang-no-in-play")
                ),
            }
        elif decision.kind == "vulture":
            victim = self.get_player_by_id(
                str(decision.data.get("victim_id", ""))
            )
            kwargs = {"player": victim.name if victim else ""}
        elif decision.kind == "elimination_discard":
            kwargs = {
                "remaining": len(decision.card_ids)
                + sum(
                    item_id.startswith("in_play_")
                    for item_id in decision.item_ids
                ),
            }
        elif decision.kind == "lethal_recovery":
            kwargs = {"life": player.life}
        elif decision.kind == "draw_check":
            purpose = str(
                decision.data.get(
                    "purpose",
                    frame.data.get("draw_purpose", "") if frame else "",
                )
            )
            kwargs = {
                "requirement": Localization.get(
                    locale,
                    f"bang-draw-requirement-{purpose.replace('_', '-')}",
                )
            }
        elif decision.kind in {"kit_keep", "kit_return"}:
            kwargs = {
                "action": Localization.get(
                    locale,
                    (
                        "bang-kit-action-keep"
                        if decision.kind == "kit_keep"
                        else "bang-kit-action-return"
                    ),
                )
            }
        elif decision.kind == "claus_give":
            target = self.get_player_by_id(
                str(decision.data.get("target_id", ""))
            )
            kwargs = {"target": target.name if target else ""}
        elif decision.kind == "ranch":
            kwargs = {"selected": len(decision.selected_card_ids)}
        elif decision.kind == "discard_excess":
            if decision.required == 1:
                return "bang-prompt-discard-single", {}
            selected = len(decision.selected_card_ids)
            if selected >= decision.required:
                return (
                    "bang-prompt-discard-ready",
                    {
                        "required": decision.required,
                    },
                )
            kwargs = {
                "selected": selected,
                "required": decision.required,
                "remaining": max(0, decision.required - selected),
            }
        return decision.prompt_key, kwargs

    def _intent_action_label(
        self,
        intent: BangPlayIntent,
        locale: str,
    ) -> str:
        actor = self.get_player_by_id(intent.actor_id)
        if isinstance(actor, BangPlayer):
            if intent.kind == "card":
                card = self._card_in_hand(actor, intent.card_id)
                if card:
                    return card_name(card, locale)
            if intent.kind == "green":
                found = self._in_play_by_id(intent.card_id)
                if found:
                    return card_name(found[1].card, locale)
        ability_keys = {
            "sid_ketchum": "bang-action-sid-ketchum",
            "doc_holyday": "bang-action-doc-holyday",
            "jose_delgado": "bang-action-jose-delgado",
            "uncle_will": "bang-action-uncle-will",
            "sniper": "bang-action-sniper",
            "ricochet": "bang-action-ricochet",
        }
        key = ability_keys.get(intent.kind)
        return Localization.get(locale, key or "bang-action-unknown")

    def _intent_prompt(
        self,
        player: BangPlayer,
        locale: str,
    ) -> tuple[str, dict[str, Any]] | None:
        intent = self.play_intent
        if not intent or intent.actor_id != player.id:
            return None
        action = self._intent_action_label(intent, locale)
        if intent.stage == "cost":
            if intent.required == 1:
                return (
                    "bang-prompt-select-single-cost",
                    {"action": action},
                )
            selected = len(intent.selected_card_ids)
            if selected >= intent.required:
                return (
                    "bang-prompt-cost-ready",
                    {
                        "action": action,
                        "selected": selected,
                        "required": intent.required,
                    },
                )
            return (
                "bang-prompt-select-cost",
                {
                    "action": action,
                    "selected": selected,
                    "required": intent.required,
                    "remaining": max(0, intent.required - selected),
                },
            )
        if intent.stage == "target":
            if intent.kind == "ricochet":
                return "bang-prompt-select-ricochet-owner", {"action": action}
            return "bang-prompt-select-target", {"action": action}
        if intent.stage == "in_play_target":
            target = self.get_player_by_id(intent.target_id)
            return (
                "bang-prompt-select-in-play",
                {
                    "action": action,
                    "target": target.name if target else "",
                },
            )
        return None

    def _input_prompt(
        self,
        player: Player,
        locale: str,
    ) -> tuple[str, dict[str, Any]] | None:
        if not isinstance(player, BangPlayer):
            return None
        prompt = self._decision_prompt(player, locale)
        if prompt:
            return prompt
        prompt = self._intent_prompt(player, locale)
        if prompt:
            return prompt
        if (
            self.status == "playing"
            and self.phase == PHASE_PLAY
            and self.current_player is player
            and self._player_in_play(player)
            and not self.effect_stack
        ):
            forced = self._forced_law_card(player)
            if forced and self._can_normally_play(player, forced):
                return (
                    "bang-prompt-law-required",
                    {"card": card_label(forced, locale)},
                )
            if self.current_event == "handcuffs" and player.handcuffs_suit:
                return (
                    "bang-prompt-play-handcuffs-suit",
                    {
                        "suit": cards.suit_name(
                            player.handcuffs_suit,
                            locale,
                        )
                    },
                )
            return "bang-prompt-play-turn", {}
        return None

    def _is_input_prompt_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return (
            Visibility.VISIBLE
            if self._input_prompt(player, locale)
            else Visibility.HIDDEN
        )

    def _is_input_prompt_enabled(self, player: Player) -> str | None:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return None if self._input_prompt(player, locale) else "action-not-available"

    def _is_end_or_confirm_enabled(self, player: Player) -> str | None:
        return (
            None
            if isinstance(player, BangPlayer) and self.status == "playing"
            else "action-not-available"
        )

    def _is_always_hidden(self, player: Player) -> Visibility:
        del player
        return Visibility.HIDDEN

    def _get_input_prompt_label(self, player: Player, action_id: str) -> str:
        del action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        prompt = self._input_prompt(player, locale)
        if not prompt:
            return Localization.get(locale, "bang-prompt-play-turn")
        key, kwargs = prompt
        return Localization.get(
            locale,
            "bang-menu-instruction",
            instruction=Localization.get(locale, key, **kwargs),
        )

    def _get_confirm_selection_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        del action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        intent = self.play_intent
        if intent and intent.actor_id == player.id:
            selected = len(intent.selected_card_ids)
            remaining = max(0, intent.required - selected)
            return Localization.get(
                locale,
                (
                    "bang-confirm-required-ready"
                    if not remaining
                    else "bang-confirm-required-pending"
                ),
                selected=selected,
                remaining=remaining,
            )
        if self.decision and self.decision.player_id == player.id:
            if self.decision.kind == "discard_excess":
                selected = len(self.decision.selected_card_ids)
                remaining = max(0, self.decision.required - selected)
                return Localization.get(
                    locale,
                    (
                        "bang-confirm-discard-ready"
                        if not remaining
                        else "bang-confirm-discard-pending"
                    ),
                    selected=selected,
                    remaining=remaining,
                )
            if self.decision.kind == "ranch":
                return Localization.get(
                    locale,
                    "bang-confirm-ranch",
                    selected=len(self.decision.selected_card_ids),
                )
        return Localization.get(locale, "bang-action-confirm")

    def _get_choose_player_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        target = self.get_player_by_id(
            action_id.removeprefix("choose_player_")
        )
        if not isinstance(target, BangPlayer):
            user = self.get_user(player)
            return Localization.get(
                user.locale if user else "en",
                "bang-choice-unavailable",
            )
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target_label = Localization.get(
            locale,
            "bang-choose-player",
            player=target.name,
            life=target.life,
            cards=len(target.hand),
            character=character_name(target.character, locale),
        )
        return target_label

    def _get_choice_item_label(
        self,
        player: Player,
        action_id: str,
    ) -> str:
        if not isinstance(player, BangPlayer):
            return action_id
        item_id = action_id.removeprefix("choice_")
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._choice_label(player, item_id, locale)

    def _is_play_card_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        if not isinstance(player, BangPlayer):
            return Visibility.HIDDEN
        card_id = self._card_id_from_action(action_id)
        if not self._card_in_hand(player, card_id):
            return Visibility.HIDDEN
        if self.status != "playing" or self.phase == PHASE_STARTING:
            return Visibility.HIDDEN
        if self.decision and self.decision.player_id == player.id:
            return (
                Visibility.VISIBLE
                if card_id in self.decision.card_ids
                else Visibility.HIDDEN
            )
        if not self._player_in_play(player):
            return Visibility.HIDDEN
        if self.play_intent:
            if self.play_intent.actor_id != player.id:
                return Visibility.VISIBLE
            allowed_ids = self.play_intent.data.get("allowed_card_ids")
            return (
                Visibility.VISIBLE
                if self.play_intent.stage == "cost"
                and card_id != self.play_intent.card_id
                and not self._law_card_must_be_played(player, card_id)
                and (
                    not isinstance(allowed_ids, list)
                    or card_id in allowed_ids
                )
                else Visibility.HIDDEN
            )
        return Visibility.VISIBLE

    def _is_play_card_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        card_id = self._card_id_from_action(action_id)
        card = self._card_in_hand(player, card_id)
        if not card:
            return "bang-error-card-missing"
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        if self.decision and self.decision.player_id == player.id:
            if card_id not in self.decision.card_ids:
                return "bang-error-card-not-response"
            return None
        if self.play_intent and self.play_intent.actor_id == player.id:
            if self.play_intent.stage != "cost":
                return "bang-error-finish-selection"
            if card_id == self.play_intent.card_id:
                return "bang-error-card-is-main-cost"
            if self._law_card_must_be_played(player, card_id):
                return "bang-error-law-card-as-cost"
            allowed_ids = self.play_intent.data.get("allowed_card_ids")
            if isinstance(allowed_ids, list) and card_id not in allowed_ids:
                return "bang-error-card-not-valid-cost"
            return None
        if self.play_intent:
            return self._phase_error(player)
        if self.phase == PHASE_DISCARD and self.current_player is player:
            return None
        if self.phase != PHASE_PLAY:
            return self._phase_error(player)
        if self.current_player is not player:
            return self._not_your_turn_error()
        return self._normal_card_error(player, card)

    def _get_play_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, BangPlayer):
            return action_id
        card = self._card_in_hand(player, self._card_id_from_action(action_id))
        if not card:
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        concise_label = card_label(card, locale)
        if (
            self.decision
            and self.decision.player_id == player.id
            and self.decision.kind == "elimination_discard"
        ):
            return Localization.get(
                locale,
                "bang-elimination-discard-next",
                card=concise_label,
            )
        selected = bool(
            self.play_intent and card.id in self.play_intent.selected_card_ids
        ) or bool(self.decision and card.id in self.decision.selected_card_ids)
        if self.phase == PHASE_DISCARD and self.current_player is player:
            return Localization.get(
                locale,
                (
                    "bang-discard-card-selected"
                    if selected
                    else "bang-discard-card-unselected"
                ),
                card=concise_label,
            )
        if (
            self.play_intent
            and self.play_intent.actor_id == player.id
            and self.play_intent.stage == "cost"
        ) or (
            self.decision
            and self.decision.player_id == player.id
            and self.decision.kind == "ranch"
        ):
            return Localization.get(
                locale,
                (
                    "bang-selected-card"
                    if selected
                    else "bang-unselected-card"
                ),
                card=concise_label,
            )
        if self.decision and self.decision.player_id == player.id:
            return Localization.get(
                locale,
                "bang-response-card",
                card=concise_label,
            )
        return card_play_name(card, locale)

    def _choice_card(self, item_id: str) -> BangCard | None:
        """Return the card represented by a dynamic choice row."""
        if item_id.startswith(("store_", "claus_", "kit_")):
            card_id = self._card_id_from_action(item_id)
            pools = self.general_store_cards + self.revealed_cards
            return next((card for card in pools if card.id == card_id), None)
        if item_id.startswith("draw_result_"):
            index = self._card_id_from_action(item_id)
            if 0 <= index < len(self.revealed_cards):
                return self.revealed_cards[index]
        if item_id.startswith("in_play_"):
            found = self._in_play_by_id(self._card_id_from_action(item_id))
            return found[1].card if found else None
        return None

    def _get_card_action_description(
        self,
        player: Player,
        action_id: str,
    ) -> str | None:
        """Resolve card rules text for any hand, in-play, or choice row."""
        if not isinstance(player, BangPlayer):
            return None
        card: BangCard | None = None
        if action_id.startswith("play_card_"):
            card = self._card_in_hand(
                player,
                self._card_id_from_action(action_id),
            )
        elif action_id.startswith("use_in_play_"):
            card_id = self._card_id_from_action(action_id)
            card = next(
                (
                    in_play.card
                    for in_play in player.in_play
                    if in_play.card.id == card_id
                ),
                None,
            )
        elif action_id.startswith("choice_"):
            card = self._choice_card(action_id.removeprefix("choice_"))
        if not card:
            return None
        user = self.get_user(player)
        return card_description(card, user.locale if user else "en")

    def _is_use_in_play_hidden(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> Visibility:
        if not isinstance(player, BangPlayer):
            return Visibility.HIDDEN
        card_id = self._card_id_from_action(action_id)
        in_play = next(
            (held for held in player.in_play if held.card.id == card_id),
            None,
        )
        if not in_play or in_play.card.border != cards.GREEN:
            return Visibility.HIDDEN
        if self.decision and self.decision.player_id == player.id:
            allowed = self.decision.data.get("green_card_ids", [])
            return (
                Visibility.VISIBLE
                if (
                    card_id in allowed
                    and self._response_frame_for_decision(
                        player,
                        self.decision,
                    )
                    is not None
                )
                else Visibility.HIDDEN
            )
        if (
            self.phase == PHASE_PLAY
            and self.current_player is player
            and not self.effect_stack
            and not self.play_intent
        ):
            return (
                Visibility.HIDDEN
                if in_play.card.kind in cards.GREEN_MISSED_CARDS
                else Visibility.VISIBLE
            )
        return Visibility.HIDDEN

    def _is_use_in_play_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | tuple[str, dict] | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        card_id = self._card_id_from_action(action_id)
        found = next(
            (held for held in player.in_play if held.card.id == card_id),
            None,
        )
        if not found:
            return "bang-error-card-missing"
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        if found.card.border != cards.GREEN:
            return "bang-error-not-green"
        if not self._in_play_effects_active(player):
            return "bang-error-in-play-disabled"
        if found.usable_after_turn > self.turn_serial:
            return "bang-error-green-not-ready"
        if self.decision and self.decision.player_id == player.id:
            if (
                card_id not in self.decision.data.get("green_card_ids", [])
                or self._response_frame_for_decision(
                    player,
                    self.decision,
                )
                is None
            ):
                return "bang-error-card-not-response"
            return None
        if self.phase != PHASE_PLAY or self.current_player is not player:
            return self._phase_error(player)
        return self._green_card_error(player, found.card)

    def _is_choice_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._private_choice_owner() is player
            else Visibility.HIDDEN
        )

    def _is_choice_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        if self._private_choice_owner() is player:
            return None
        return self._phase_error(player)

    def _is_confirm_hidden(self, player: Player) -> Visibility:
        if not isinstance(player, BangPlayer):
            return Visibility.HIDDEN
        if self.play_intent and self.play_intent.actor_id == player.id:
            return (
                Visibility.VISIBLE
                if self.play_intent.stage == "cost"
                and self.play_intent.required >= 2
                else Visibility.HIDDEN
            )
        if self.decision and self.decision.player_id == player.id:
            if self.decision.kind == "ranch":
                return Visibility.VISIBLE
            if (
                self.decision.kind == "discard_excess"
                and self.decision.required >= 2
            ):
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_confirm_enabled(self, player: Player) -> str | None:
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        intent = self.play_intent
        if intent and intent.actor_id == player.id:
            if intent.stage == "cost":
                if len(intent.selected_card_ids) != intent.required:
                    return "bang-error-select-more-cards"
                return None
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return self._input_prompt(player, locale) or "bang-error-confirm-not-open"
        if self.decision and self.decision.player_id == player.id:
            if self.decision.kind == "discard_excess":
                if (
                    len(self.decision.selected_card_ids)
                    < self.decision.required
                ):
                    return "bang-error-select-more-cards"
                return None
            if self.decision.kind == "ranch":
                return None
        return "bang-error-confirm-not-open"

    def _is_cancel_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self.play_intent and self.play_intent.actor_id == player.id
            else Visibility.HIDDEN
        )

    def _is_cancel_enabled(self, player: Player) -> str | None:
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        return (
            None
            if self.play_intent and self.play_intent.actor_id == player.id
            else "bang-error-nothing-to-cancel"
        )

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if isinstance(player, BangPlayer)
            and self.phase == PHASE_PLAY
            and self.current_player is player
            and not self.effect_stack
            and not self.decision
            and not self.play_intent
            else Visibility.HIDDEN
        )

    def _is_end_turn_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        if not isinstance(player, BangPlayer) or self.current_player is not player:
            return self._not_your_turn_error()
        if self.phase != PHASE_PLAY:
            return self._phase_error(player)
        forced = self._forced_law_card(player)
        if forced and self._can_normally_play(player, forced):
            user = self.get_user(player)
            locale = user.locale if user else "en"
            return (
                "bang-error-law-card-required",
                {"card": card_label(forced, locale)},
            )
        return None

    def _not_your_turn_error(self) -> str | tuple[str, dict]:
        current = self.current_player
        if isinstance(current, BangPlayer):
            return (
                "bang-error-not-your-turn",
                {"player": current.name},
            )
        return "bang-error-no-active-turn"

    def _waiting_for_input_error(
        self,
        owner: Player,
        locale: str,
    ) -> tuple[str, dict[str, str]]:
        prompt = self._input_prompt(owner, locale)
        instruction = (
            Localization.get(locale, prompt[0], **prompt[1])
            if prompt
            else Localization.get(locale, "bang-waiting-action-choice")
        )
        return (
            "bang-error-waiting-for-player",
            {
                "player": owner.name,
                "action": instruction,
            },
        )

    def _waiting_for_intent_error(
        self,
        owner: Player,
        locale: str,
    ) -> tuple[str, dict[str, str]]:
        intent = self.play_intent
        if not intent:
            return self._waiting_for_input_error(owner, locale)
        if intent.stage == "cost":
            selected = len(intent.selected_card_ids)
            remaining = max(0, intent.required - selected)
            if remaining:
                key = "bang-waiting-intent-cost"
                kwargs = {"remaining": remaining}
            else:
                key = "bang-waiting-intent-cost-ready"
                kwargs = {"selected": selected}
        elif intent.stage == "target":
            key = "bang-waiting-intent-target"
            kwargs = {}
        elif intent.stage == "in_play_target":
            key = "bang-waiting-intent-in-play"
            kwargs = {}
        else:
            key = "bang-waiting-action-choice"
            kwargs = {}
        instruction = Localization.get(locale, key, **kwargs)
        return (
            "bang-error-waiting-for-player",
            {
                "player": owner.name,
                "action": instruction,
            },
        )

    def _phase_error(
        self,
        player: Player,
    ) -> str | tuple[str, dict]:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if self.decision:
            owner = self.get_player_by_id(self.decision.player_id)
            if owner is player:
                prompt = self._input_prompt(player, locale)
                return prompt if prompt else "bang-error-finish-decision"
            if owner:
                return self._waiting_for_input_error(owner, locale)
        if self.play_intent:
            owner = self.get_player_by_id(self.play_intent.actor_id)
            if owner is player:
                prompt = self._input_prompt(player, locale)
                return prompt if prompt else "bang-error-finish-selection"
            if owner:
                return self._waiting_for_intent_error(owner, locale)
        if self.phase == PHASE_STARTING:
            return "bang-error-intro-playing"
        current = self.current_player
        if self.phase == PHASE_START_TURN:
            if current is player:
                return "bang-error-your-turn-start"
            if isinstance(current, BangPlayer):
                return (
                    "bang-error-player-turn-start",
                    {"player": current.name},
                )
        if self.phase == PHASE_DRAW:
            if current is player:
                return "bang-error-your-draw-resolving"
            if isinstance(current, BangPlayer):
                return (
                    "bang-error-player-draw-resolving",
                    {"player": current.name},
                )
        if self.phase == PHASE_DISCARD:
            if current is player:
                return "bang-error-must-discard"
            if isinstance(current, BangPlayer):
                return (
                    "bang-error-player-must-discard",
                    {"player": current.name},
                )
        frame = self._top_effect() if self.effect_stack else None
        if frame and frame.source.kind:
            return (
                "bang-error-effect-resolving-source",
                {"source": self._source_context(frame, locale)},
            )
        return "bang-error-effect-resolving"

    def _normal_card_error(
        self,
        player: BangPlayer,
        card: BangCard,
        *,
        protect_law_cost: bool = True,
    ) -> str | tuple[str, dict] | None:
        as_bang = (
            card.kind == cards.MISSED
            and self._has_ability(player, "calamity_janet")
        )
        if card.kind in {cards.MISSED, cards.DODGE} and not as_bang:
            return (
                "bang-error-response-only",
                {"card": self._card_name_for(player, card)},
            )
        if not self._handcuffs_allows_card(player, card):
            return (
                "bang-error-handcuffs-suit",
                {
                    "card": self._card_name_for(player, card),
                    "suit": self._suit_name_for(player, player.handcuffs_suit),
                },
            )
        if card.kind == cards.BANG or as_bang:
            if self.current_event == "the_sermon":
                return "bang-error-sermon-bang"
            limit = self._bang_limit(player)
            if limit is not None and player.bangs_played >= limit:
                return (
                    "bang-error-bang-limit",
                    {"limit": limit},
                )
        if card.kind == cards.BEER and self.current_event == "the_reverend":
            return "bang-error-reverend-beer"
        if card.border in {cards.BLUE, cards.GREEN}:
            if self.current_event == "the_judge":
                return "bang-error-judge-in-play"
            target = player
            if card.kind == cards.JAIL:
                target = None
            if (
                target
                and card.kind not in cards.WEAPONS
                and any(
                    in_play.card.kind == card.kind
                    for in_play in target.in_play
                )
            ):
                return (
                    "bang-error-duplicate-in-play",
                    {"card": self._card_name_for(player, card)},
                )
        if card.kind == cards.DYNAMITE and any(
            in_play.card.kind == cards.DYNAMITE for in_play in player.in_play
        ):
            return "bang-error-duplicate-dynamite"
        targets = self._legal_targets_for_card(player, card)
        if self._card_requires_immediate_target(card, as_bang=as_bang) and not targets:
            return (
                "bang-error-no-legal-target",
                {"card": self._card_name_for(player, card)},
            )
        if (
            card.kind in cards.EXTRA_COST_CARDS
            and (
                (
                    protect_law_cost
                    and not any(
                        held.id != card.id
                        for held in self._eligible_cost_cards(player)
                    )
                )
                or (not protect_law_cost and len(player.hand) < 2)
            )
        ):
            return (
                "bang-error-extra-cost",
                {"card": self._card_name_for(player, card)},
            )
        return None

    def _handcuffs_allows_card(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> bool:
        """Return whether a hand card matches the active player's declared suit."""

        return not (
            self.current_event == "handcuffs"
            and self.current_player is player
            and player.handcuffs_suit
            and self._effective_suit(card) != player.handcuffs_suit
        )

    def _green_card_error(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> str | tuple[str, dict] | None:
        if card.kind in cards.GREEN_MISSED_CARDS:
            return (
                "bang-error-response-only",
                {"card": self._card_name_for(player, card)},
            )
        targets = self._legal_targets_for_card(player, card)
        if self._card_requires_target(card.kind) and not targets:
            return (
                "bang-error-no-legal-target",
                {"card": self._card_name_for(player, card)},
            )
        return None

    def _card_name_for(self, player: Player, card: BangCard) -> str:
        user = self.get_user(player)
        return card_name(card, user.locale if user else "en")

    def _suit_name_for(self, player: Player, suit: str) -> str:
        user = self.get_user(player)
        return cards.suit_name(suit, user.locale if user else "en")

    def _ability_visibility(
        self,
        player: Player,
        character_id: str,
        *,
        event: str = "",
    ) -> Visibility:
        if not isinstance(player, BangPlayer):
            return Visibility.HIDDEN
        if not self._has_ability(player, character_id):
            return Visibility.HIDDEN
        if event and self.current_event != event:
            return Visibility.HIDDEN
        if self.phase != PHASE_PLAY or self.current_player is not player:
            return Visibility.HIDDEN
        if self.effect_stack or self.decision or self.play_intent:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_sid_hidden(self, player: Player) -> Visibility:
        if not isinstance(player, BangPlayer):
            return Visibility.HIDDEN
        if self._has_ability(
            player,
            "sid_ketchum",
        ) and self._sid_timing_is_open(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _sid_timing_is_open(self, player: BangPlayer) -> bool:
        if (
            not self.game_active
            or self.status != "playing"
            or self.is_sequence_gameplay_locked()
        ):
            return False
        if (
            self.decision
            and self.decision.player_id == player.id
            and self.decision.kind == "lethal_recovery"
        ):
            return True
        return (
            self.phase == PHASE_PLAY
            and self._player_in_play(player)
            and not self.effect_stack
            and not self.decision
            and not self.play_intent
        )

    def _is_sid_enabled(
        self,
        player: Player,
    ) -> str | tuple[str, dict] | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if not self._has_ability(player, "sid_ketchum"):
            return "bang-error-sid-character-only"
        if self.is_sequence_gameplay_locked():
            return "bang-error-audio-sequence"
        if not self._sid_timing_is_open(player):
            if self.status == "playing":
                return self._phase_error(player)
            return "bang-error-sid-timing"
        if len(self._eligible_cost_cards(player)) < 2:
            return "bang-error-sid-needs-two"
        if player.life >= player.max_life and player.life > 0:
            return "bang-error-full-life"
        return None

    def _is_doc_hidden(self, player: Player) -> Visibility:
        return self._ability_visibility(player, "doc_holyday")

    def _is_doc_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if player.doc_holyday_used:
            return "bang-error-doc-used"
        if len(self._eligible_cost_cards(player)) < 2:
            return "bang-error-doc-needs-two"
        if not self._reachable_targets(player):
            return "bang-error-no-reachable-target"
        return None

    def _is_chuck_hidden(self, player: Player) -> Visibility:
        return self._ability_visibility(player, "chuck_wengam")

    def _is_chuck_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if player.life <= 0 or (player.life == 1 and not player.ghost_active):
            return "bang-error-chuck-last-life"
        return None

    def _is_jose_hidden(self, player: Player) -> Visibility:
        return self._ability_visibility(player, "jose_delgado")

    def _is_jose_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if player.jose_delgado_uses >= 2:
            return "bang-error-jose-used"
        if not any(
            card.border == cards.BLUE
            for card in self._eligible_cost_cards(player)
        ):
            return "bang-error-jose-needs-blue"
        return None

    def _is_uncle_hidden(self, player: Player) -> Visibility:
        return self._ability_visibility(player, "uncle_will")

    def _is_uncle_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if player.uncle_will_used:
            return "bang-error-uncle-used"
        if not self._eligible_cost_cards(player):
            return "bang-error-empty-hand"
        return None

    def _is_sniper_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if isinstance(player, BangPlayer)
            and self.current_event == "sniper"
            and self.phase == PHASE_PLAY
            and self.current_player is player
            and not self.effect_stack
            and not self.decision
            and not self.play_intent
            else Visibility.HIDDEN
        )

    def _is_sniper_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if sum(
            self._card_can_be_bang_response(player, card)
            for card in self._eligible_cost_cards(player)
        ) < 2:
            return "bang-error-sniper-needs-two"
        if not self._reachable_targets(player):
            return "bang-error-no-reachable-target"
        return None

    def _is_ricochet_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if isinstance(player, BangPlayer)
            and self.current_event == "ricochet"
            and self.phase == PHASE_PLAY
            and self.current_player is player
            and not self.effect_stack
            and not self.decision
            and not self.play_intent
            else Visibility.HIDDEN
        )

    def _is_ricochet_enabled(self, player: Player) -> str | None:
        if not isinstance(player, BangPlayer):
            return "bang-error-not-player"
        if not any(
            self._card_can_be_bang_response(player, card)
            for card in self._eligible_cost_cards(player)
        ):
            return "bang-error-ricochet-needs-bang"
        if not any(owner.in_play for owner in self.players_in_play):
            return "bang-error-no-in-play-card"
        return None

    # ------------------------------------------------------------------
    # Action handlers and reversible play intents
    # ------------------------------------------------------------------

    def _speak_input_prompt(self, player: BangPlayer) -> None:
        if player.is_bot:
            return
        user = self.get_user(player)
        if not user:
            return
        prompt = self._input_prompt(player, user.locale)
        if prompt:
            key, kwargs = prompt
            user.speak_l(key, buffer="game", **kwargs)

    def _action_repeat_input_prompt(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        del action_id
        if isinstance(player, BangPlayer):
            self._speak_input_prompt(player)

    def _toggle_card_selection(
        self,
        player: BangPlayer,
        card: BangCard,
        selected_ids: list[int],
        *,
        limit: int = 0,
        discard: bool = False,
    ) -> bool:
        user = self.get_user(player)
        if card.id in selected_ids:
            selected_ids.remove(card.id)
            if limit:
                message = (
                    "bang-card-removed-from-discard"
                    if discard
                    else "bang-card-unselected-progress"
                )
            else:
                message = "bang-card-unselected"
        else:
            if limit and len(selected_ids) >= limit:
                if user:
                    user.speak_l(
                        "bang-error-selection-limit",
                        buffer="game",
                        required=limit,
                    )
                return False
            selected_ids.append(card.id)
            if limit:
                message = (
                    "bang-card-selected-for-discard"
                    if discard
                    else "bang-card-selected-progress"
                )
            else:
                message = "bang-card-selected"
        if user:
            user.speak_l(
                message,
                buffer="game",
                card=card_label(card, user.locale),
                remaining=max(0, limit - len(selected_ids)),
            )
        self.refresh_menus(player)
        return True

    def _action_play_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BangPlayer):
            return
        card = self._card_in_hand(
            player,
            self._card_id_from_action(action_id),
        )
        if not card:
            return
        if self.decision and self.decision.player_id == player.id:
            self._use_decision_card(player, card)
            return
        if self.play_intent and self.play_intent.actor_id == player.id:
            if self.play_intent.stage == "cost":
                if self._law_card_must_be_played(player, card.id):
                    self._speak_action_disabled_reason(
                        player,
                        "bang-error-law-card-as-cost",
                    )
                    return
                allowed_ids = self.play_intent.data.get("allowed_card_ids")
                if (
                    isinstance(allowed_ids, list)
                    and card.id not in allowed_ids
                ):
                    self._speak_action_disabled_reason(
                        player,
                        "bang-error-card-not-valid-cost",
                    )
                    return
                if self.play_intent.required == 1:
                    self.play_intent.selected_card_ids = [card.id]
                    self._advance_cost_intent(player)
                    return
                self._toggle_card_selection(
                    player,
                    card,
                    self.play_intent.selected_card_ids,
                    limit=self.play_intent.required,
                )
            return
        if self.phase == PHASE_DISCARD and self.current_player is player:
            self._select_discard_card(player, card)
            return
        error = self._normal_card_error(player, card)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        self._start_card_intent(player, card)

    def _action_use_in_play(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BangPlayer):
            return
        card_id = self._card_id_from_action(action_id)
        in_play = next(
            (held for held in player.in_play if held.card.id == card_id),
            None,
        )
        if not in_play:
            return
        error = self._is_use_in_play_enabled(player, action_id=action_id)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if self.decision and self.decision.player_id == player.id:
            self._use_green_response(player, in_play)
            return
        intent = BangPlayIntent(
            kind="green",
            actor_id=player.id,
            card_id=in_play.card.id,
        )
        if self._card_requires_target(in_play.card.kind):
            intent.stage = "target"
            self.play_intent = intent
            self._focus_first_target(player)
            return
        self.play_intent = intent
        self._commit_intent()

    def _action_choose_player(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BangPlayer):
            return
        target_id = action_id.removeprefix("choose_player_")
        target = self.get_player_by_id(target_id)
        if not isinstance(target, BangPlayer):
            return
        if self.decision and self.decision.player_id == player.id:
            if target.id not in self.decision.player_ids:
                return
            self._resolve_player_decision(player, target)
            return
        if (
            self.play_intent
            and self.play_intent.actor_id == player.id
            and self.play_intent.stage == "target"
        ):
            intent = self.play_intent
            if target not in self._targets_for_intent(intent):
                return
            intent.target_id = target.id
            if intent.kind == "ricochet":
                intent.stage = "in_play_target"
                self._focus_first_in_play(player)
                return
            self._commit_intent()

    def _action_choose_item(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BangPlayer):
            return
        item_id = action_id.removeprefix("choice_")
        if self.decision and self.decision.player_id == player.id:
            if item_id not in self.decision.item_ids:
                return
            self._resolve_item_decision(player, item_id)
            return
        if (
            self.play_intent
            and self.play_intent.actor_id == player.id
            and self.play_intent.stage == "in_play_target"
        ):
            if not item_id.startswith("in_play_"):
                return
            card_id = self._card_id_from_action(item_id)
            found = self._in_play_by_id(card_id)
            if (
                not found
                or (
                    self.play_intent.kind == "ricochet"
                    and found[0].id != self.play_intent.target_id
                )
            ):
                return
            intent = self.play_intent
            intent.in_play_card_id = card_id
            self._commit_intent()

    def _action_confirm_selection(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        del action_id
        error = self._is_confirm_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        if self.play_intent and self.play_intent.actor_id == player.id:
            self._advance_cost_intent(player)
            return
        if self.decision and self.decision.player_id == player.id:
            if self.decision.kind == "ranch":
                self._finish_ranch_selection(player)
            elif self.decision.kind == "discard_excess":
                self._finish_discard_selection(player)

    def _action_end_or_confirm(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        del action_id
        if self._is_confirm_hidden(player) is Visibility.VISIBLE:
            self._action_confirm_selection(player, "confirm_selection")
            return
        if self._is_end_turn_hidden(player) is Visibility.VISIBLE:
            self._action_end_turn(player, "end_turn")
            return
        if isinstance(player, BangPlayer):
            user = self.get_user(player)
            if self._input_prompt(player, user.locale if user else "en"):
                self._speak_input_prompt(player)
                return
        self._speak_action_disabled_reason(
            player,
            self._is_end_turn_enabled(player),
        )

    def _advance_cost_intent(self, player: BangPlayer) -> None:
        intent = self.play_intent
        if (
            not intent
            or intent.actor_id != player.id
            or intent.stage != "cost"
        ):
            return
        if len(intent.selected_card_ids) != intent.required:
            self._speak_action_disabled_reason(
                player,
                "bang-error-select-more-cards",
            )
            return
        intent.selected_card_ids = intent.selected_card_ids[: intent.required]
        if intent.kind in {"doc_holyday", "sniper", "ricochet"}:
            intent.stage = "target"
            self._focus_first_target(player)
            return
        card = self._card_in_hand(player, intent.card_id)
        if card and self._card_requires_target(card.kind):
            intent.stage = "target"
            self._focus_first_target(player)
            return
        self._commit_intent()

    def _action_cancel_selection(
        self,
        player: Player,
        action_id: str,
    ) -> None:
        del action_id
        if not isinstance(player, BangPlayer):
            return
        if self.play_intent and self.play_intent.actor_id == player.id:
            intent = self.play_intent
            self.play_intent = None
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "bang-action-canceled",
                    buffer="game",
                    action=self._intent_action_label(intent, user.locale),
                )
            first = (
                f"play_card_{player.hand[0].id}"
                if player.hand
                else "end_turn"
            )
            self.request_menu_focus(player, first)
            self.refresh_menus(player)

    def _action_end_turn(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_end_turn_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if isinstance(player, BangPlayer):
            self._start_discard_phase(player)

    def _action_sid_ketchum(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_sid_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        self._start_sid_intent(player, lethal_recovery=False)

    def _start_sid_intent(
        self,
        player: BangPlayer,
        *,
        lethal_recovery: bool,
    ) -> None:
        """Open Sid Ketchum's payment after validating its timing."""

        self.play_intent = BangPlayIntent(
            kind="sid_ketchum",
            actor_id=player.id,
            required=2,
            stage="cost",
            data={
                "allowed_card_ids": [
                    card.id for card in self._eligible_cost_cards(player)
                ],
                "lethal_recovery": lethal_recovery,
            },
        )
        self._focus_first_cost(player)

    def _action_doc_holyday(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_doc_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        eligible_ids = [
            card.id for card in self._eligible_cost_cards(player)
        ]
        self.play_intent = BangPlayIntent(
            kind="doc_holyday",
            actor_id=player.id,
            required=2,
            stage="cost",
            data={"allowed_card_ids": eligible_ids},
        )
        self._focus_first_cost(player, eligible_ids)

    def _action_chuck_wengam(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_chuck_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        player.life -= 1
        self._draw_cards(player, 2)
        self.broadcast_personal_l(
            player,
            "bang-you-use-chuck",
            "bang-player-uses-chuck",
            buffer="game",
            life=player.life,
        )
        self.refresh_menus()

    def _action_jose_delgado(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_jose_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        blue_ids = [
            card.id
            for card in self._eligible_cost_cards(player)
            if card.border == cards.BLUE
        ]
        self.play_intent = BangPlayIntent(
            kind="jose_delgado",
            actor_id=player.id,
            required=1,
            stage="cost",
            data={"allowed_card_ids": blue_ids},
        )
        self._focus_first_cost(player, blue_ids)

    def _action_uncle_will(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_uncle_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        eligible = self._eligible_cost_cards(player)
        self.play_intent = BangPlayIntent(
            kind="uncle_will",
            actor_id=player.id,
            required=1,
            stage="cost",
            data={"allowed_card_ids": [card.id for card in eligible]},
        )
        self._focus_first_cost(player, [card.id for card in eligible])

    def _action_sniper(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_sniper_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        bang_ids = [
            card.id
            for card in self._eligible_cost_cards(player)
            if self._card_can_be_bang_response(player, card)
        ]
        self.play_intent = BangPlayIntent(
            kind="sniper",
            actor_id=player.id,
            required=2,
            stage="cost",
            data={"allowed_card_ids": bang_ids},
        )
        self._focus_first_cost(player, bang_ids)

    def _action_ricochet(self, player: Player, action_id: str) -> None:
        del action_id
        error = self._is_ricochet_enabled(player)
        if error:
            self._speak_action_disabled_reason(player, error)
            return
        if not isinstance(player, BangPlayer):
            return
        bang_ids = [
            card.id
            for card in self._eligible_cost_cards(player)
            if self._card_can_be_bang_response(player, card)
        ]
        self.play_intent = BangPlayIntent(
            kind="ricochet",
            actor_id=player.id,
            required=1,
            stage="cost",
            data={"allowed_card_ids": bang_ids, "mode": "ricochet"},
        )
        self._focus_first_cost(player, bang_ids)

    def _start_card_intent(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> None:
        intent = BangPlayIntent(
            kind="card",
            actor_id=player.id,
            card_id=card.id,
        )
        if (
            card.kind == cards.MISSED
            and self._has_ability(player, "calamity_janet")
        ):
            intent.data["as_bang"] = True
        if card.kind in cards.EXTRA_COST_CARDS:
            intent.required = 1
            intent.stage = "cost"
            intent.data["allowed_card_ids"] = [
                held.id
                for held in self._eligible_cost_cards(player)
                if held.id != card.id
            ]
            self.play_intent = intent
            self._focus_first_cost(
                player,
                intent.data["allowed_card_ids"],
            )
            return
        if self._card_requires_immediate_target(
            card,
            as_bang=bool(intent.data.get("as_bang")),
        ):
            intent.stage = "target"
            self.play_intent = intent
            self._focus_first_target(player)
            return
        self.play_intent = intent
        self._commit_intent()

    def _focus_first_cost(
        self,
        player: BangPlayer,
        allowed_ids: list[int] | None = None,
    ) -> None:
        if allowed_ids is None:
            allowed_ids = [
                card.id
                for card in self._eligible_cost_cards(player)
                if not self.play_intent or card.id != self.play_intent.card_id
            ]
        if allowed_ids:
            self.request_menu_focus(player, f"play_card_{allowed_ids[0]}")
        else:
            self.refresh_menus(player)
        self._speak_input_prompt(player)
        self._pace_bot(player, choice=True)

    def _focus_first_target(self, player: BangPlayer) -> None:
        intent = self.play_intent
        if not intent:
            return
        targets = self._targets_for_intent(intent)
        if len(targets) == 1:
            intent.target_id = targets[0].id
            if intent.kind == "ricochet":
                intent.stage = "in_play_target"
                self._focus_first_in_play(player)
            else:
                self._commit_intent()
            return
        if targets:
            self.request_menu_focus(player, f"choose_player_{targets[0].id}")
        else:
            self.refresh_menus(player)
        self._speak_input_prompt(player)
        self._pace_bot(player, choice=True)

    def _focus_first_in_play(self, player: BangPlayer) -> None:
        intent = self.play_intent
        if not intent:
            return
        choices = self._in_play_choice_ids(
            intent.data.get("mode", ""),
        )
        if len(choices) == 1:
            intent.in_play_card_id = self._card_id_from_action(choices[0])
            self._commit_intent()
            return
        if choices:
            self.request_menu_focus(player, f"choice_{choices[0]}")
        else:
            self.refresh_menus(player)
        self._speak_input_prompt(player)
        self._pace_bot(player, choice=True)

    def _commit_intent(self) -> None:
        intent = self.play_intent
        if not intent:
            return
        actor = self.get_player_by_id(intent.actor_id)
        if not isinstance(actor, BangPlayer):
            self.play_intent = None
            return
        if intent.required:
            selected = self._cards_from_ids(actor, intent.selected_card_ids)
            allowed_ids = intent.data.get("allowed_card_ids")
            invalid_cost = (
                len(selected) != intent.required
                or len(set(intent.selected_card_ids)) != intent.required
                or intent.card_id in intent.selected_card_ids
                or (
                    isinstance(allowed_ids, list)
                    and any(card.id not in allowed_ids for card in selected)
                )
            )
            if invalid_cost:
                self.play_intent = None
                self._speak_action_disabled_reason(
                    actor,
                    "bang-error-card-not-valid-cost",
                )
                self.refresh_menus(actor)
                return
        if intent.stage == "target":
            target = self.get_player_by_id(intent.target_id)
            if (
                not isinstance(target, BangPlayer)
                or target not in self._targets_for_intent(intent)
            ):
                self._speak_action_disabled_reason(
                    actor,
                    "bang-error-select-target",
                )
                self.refresh_menus(actor)
                return
        if intent.stage == "in_play_target":
            choices = self._in_play_choice_ids(
                intent.data.get("mode", ""),
            )
            if f"in_play_{intent.in_play_card_id}" not in choices:
                self._speak_action_disabled_reason(
                    actor,
                    "bang-error-select-in-play-target",
                )
                self.refresh_menus(actor)
                return
        if intent.kind == "sid_ketchum":
            self._discard_selected_costs(actor, intent.selected_card_ids)
            self._heal(
                actor,
                1,
                allow_from_zero=bool(intent.data.get("lethal_recovery")),
                announce=False,
            )
            self.play_intent = None
            self.broadcast_personal_l(
                actor,
                "bang-you-use-sid",
                "bang-player-uses-sid",
                buffer="game",
                life=actor.life,
            )
            if bool(intent.data.get("lethal_recovery")):
                self._finish_lethal_recovery_attempt(actor)
            self.refresh_menus()
            return
        if intent.kind == "doc_holyday":
            costs = self._cards_from_ids(actor, intent.selected_card_ids)
            self._discard_selected_costs(actor, intent.selected_card_ids)
            actor.doc_holyday_used = 1
            target = self.get_player_by_id(intent.target_id)
            self.play_intent = None
            if isinstance(target, BangPlayer):
                if (
                    self._has_ability(target, "apache_kid")
                    and costs
                    and all(
                        self._effective_suit(card) == cards.DIAMONDS
                        for card in costs
                    )
                ):
                    self._announce_unaffected(actor, target, "doc_holyday")
                else:
                    self._start_shot(
                        actor,
                        target,
                        source_kind="doc_holyday",
                        required=1,
                    )
            return
        if intent.kind == "sniper":
            costs = self._cards_from_ids(actor, intent.selected_card_ids)
            self._discard_selected_costs(actor, intent.selected_card_ids)
            target = self.get_player_by_id(intent.target_id)
            self.play_intent = None
            if isinstance(target, BangPlayer):
                if (
                    self._has_ability(target, "apache_kid")
                    and costs
                    and all(
                        self._effective_suit(card) == cards.DIAMONDS
                        for card in costs
                    )
                ):
                    self._announce_unaffected(actor, target, "sniper")
                    self._finish_atomic_effect()
                else:
                    self._start_shot(
                        actor,
                        target,
                        source_kind="sniper",
                        required=2,
                    )
            return
        if intent.kind == "ricochet":
            self._discard_selected_costs(actor, intent.selected_card_ids)
            target_card = self._in_play_by_id(intent.in_play_card_id)
            self.play_intent = None
            if target_card:
                owner, in_play = target_card
                self._start_ricochet(actor, owner, in_play.card.id)
            return
        if intent.kind == "jose_delgado":
            costs = self._cards_from_ids(actor, intent.selected_card_ids)
            if not costs or costs[0].border != cards.BLUE:
                self.play_intent = None
                return
            self._discard_selected_costs(actor, intent.selected_card_ids)
            actor.jose_delgado_uses += 1
            self.play_intent = None
            self._draw_cards(actor, 2)
            self.broadcast_personal_l(
                actor,
                "bang-you-use-jose",
                "bang-player-uses-jose",
                buffer="game",
            )
            self._finish_atomic_effect()
            return
        if intent.kind == "uncle_will":
            costs = self._cards_from_ids(actor, intent.selected_card_ids)
            if not costs:
                self.play_intent = None
                return
            self._discard_selected_costs(actor, intent.selected_card_ids)
            actor.uncle_will_used = 1
            self.play_intent = None
            self._announce_ability(actor, "uncle-will")
            self._start_general_store(actor)
            return
        if intent.kind == "green":
            found = next(
                (
                    in_play
                    for in_play in actor.in_play
                    if in_play.card.id == intent.card_id
                ),
                None,
            )
            if not found:
                self.play_intent = None
                return
            actor.in_play.remove(found)
            self.resolving_card = ResolvingCard(
                card=found.card,
                actor_id=actor.id,
                from_in_play=True,
            )
            target = self.get_player_by_id(intent.target_id)
            self.play_intent = None
            self._announce_card_play(actor, found.card, target)
            self._resolve_committed_card(actor, found.card, target)
            return

        card = self._card_in_hand(actor, intent.card_id)
        if not card:
            self.play_intent = None
            return
        target = self.get_player_by_id(intent.target_id)
        target_player = target if isinstance(target, BangPlayer) else None
        actor.hand.remove(card)
        self._discard_selected_costs(actor, intent.selected_card_ids)
        self.play_intent = None
        as_bang = bool(intent.data.get("as_bang"))
        if not self._card_has_immediate_sound(card, as_bang=as_bang):
            self.play_sound(self._random_sound(game_audio.SOUND_CARD_PLAY))
        self._announce_card_play(
            actor,
            card,
            target_player,
            as_bang=as_bang,
        )
        if card.kind == cards.BANG or as_bang:
            actor.bangs_played += 1

        if card.border in {cards.BLUE, cards.GREEN}:
            self._put_card_in_play(actor, card, target_player)
            self._finish_atomic_effect()
            return
        self.resolving_card = ResolvingCard(card=card, actor_id=actor.id)
        if as_bang and target_player:
            self._start_shot(
                actor,
                target_player,
                source_kind="missed_as_bang",
                required=1,
            )
            return
        self._resolve_committed_card(actor, card, target_player)

    def _cards_from_ids(
        self,
        player: BangPlayer,
        card_ids: list[int],
    ) -> list[BangCard]:
        by_id = {card.id: card for card in player.hand}
        return [by_id[card_id] for card_id in card_ids if card_id in by_id]

    def _discard_selected_costs(
        self,
        player: BangPlayer,
        card_ids: list[int],
    ) -> None:
        for card in self._cards_from_ids(player, card_ids):
            player.hand.remove(card)
            self._discard(card)

    # ------------------------------------------------------------------
    # Targeting, distance, and card commitment
    # ------------------------------------------------------------------

    @staticmethod
    def _card_requires_target(kind: str) -> bool:
        return kind in {
            cards.BANG,
            cards.CAT_BALOU,
            cards.DUEL,
            cards.JAIL,
            cards.PANIC,
            cards.PUNCH,
            cards.RAG_TIME,
            cards.SPRINGFIELD,
            cards.TEQUILA,
            cards.BUFFALO_RIFLE,
            cards.CAN_CAN,
            cards.CONESTOGA,
            cards.DERRINGER,
            cards.KNIFE,
            cards.PEPPERBOX,
        }

    @classmethod
    def _card_requires_immediate_target(
        cls,
        card: BangCard,
        *,
        as_bang: bool = False,
    ) -> bool:
        """Return whether playing this hand card needs a target now.

        Green-bordered cards are placed without a target. Their target, if any,
        is selected only when their delayed effect is used on a later turn.
        """

        return card.border != cards.GREEN and (
            cls._card_requires_target(card.kind) or as_bang
        )

    def _targets_for_intent(
        self,
        intent: BangPlayIntent,
    ) -> list[BangPlayer]:
        actor = self.get_player_by_id(intent.actor_id)
        if not isinstance(actor, BangPlayer):
            return []
        if intent.kind in {"doc_holyday", "sniper"}:
            return self._reachable_targets(actor)
        if intent.kind == "ricochet":
            return [
                player
                for player in self.players_in_play
                if player.in_play
            ]
        if intent.kind == "green":
            found = self._in_play_by_id(intent.card_id)
            return (
                self._legal_targets_for_card(
                    actor,
                    found[1].card,
                )
                if found
                else []
            )
        card = self._card_in_hand(actor, intent.card_id)
        return self._legal_targets_for_card(actor, card) if card else []

    def _legal_targets_for_card(
        self,
        actor: BangPlayer,
        card: BangCard,
    ) -> list[BangPlayer]:
        others = [
            player
            for player in self.players_in_play
            if player.id != actor.id
        ]
        if card.kind == cards.BANG or (
            card.kind == cards.MISSED
            and self._has_ability(actor, "calamity_janet")
        ):
            return [
                target
                for target in others
                if self.distance(actor, target) <= self.weapon_range(actor)
            ]
        if card.kind in {cards.DUEL, cards.SPRINGFIELD, cards.BUFFALO_RIFLE}:
            return others
        if card.kind == cards.JAIL:
            return [
                target
                for target in others
                if (len(self.seated_players) == 3 or target.role != ROLE_SHERIFF)
                and not any(
                    in_play.card.kind == cards.JAIL
                    for in_play in target.in_play
                )
            ]
        if card.kind in {cards.PANIC, cards.PUNCH, cards.DERRINGER, cards.KNIFE}:
            return [
                target
                for target in others
                if self.distance(actor, target) <= 1
                and (
                    card.kind not in {cards.PANIC}
                    or bool(target.hand or target.in_play)
                )
            ]
        if card.kind == cards.PEPPERBOX:
            return [
                target
                for target in others
                if self.distance(actor, target) <= self.weapon_range(actor)
            ]
        if card.kind in {
            cards.CAT_BALOU,
            cards.RAG_TIME,
            cards.CAN_CAN,
            cards.CONESTOGA,
        }:
            return [
                target for target in others if target.hand or target.in_play
            ]
        if card.kind == cards.TEQUILA:
            return list(self.players_in_play)
        return []

    def _reachable_targets(self, actor: BangPlayer) -> list[BangPlayer]:
        return [
            target
            for target in self.players_in_play
            if target.id != actor.id
            and self.distance(actor, target) <= self.weapon_range(actor)
        ]

    def _seat_distance(
        self,
        actor: BangPlayer,
        target: BangPlayer,
    ) -> int:
        active_ids = [player.id for player in self.players_in_play]
        if actor.id not in active_ids or target.id not in active_ids:
            return 99
        if len(active_ids) <= 2:
            return 1
        first = active_ids.index(actor.id)
        second = active_ids.index(target.id)
        clockwise = (second - first) % len(active_ids)
        counter = (first - second) % len(active_ids)
        return min(clockwise, counter)

    def distance(self, actor: BangPlayer, target: BangPlayer) -> int:
        base = (
            1
            if self.current_event == "ambush"
            else self._seat_distance(actor, target)
        )
        target_visibility = 0
        actor_sight = 0
        for in_play in target.in_play:
            if not self._in_play_effects_active(target):
                continue
            if in_play.card.kind in {cards.MUSTANG, cards.HIDEOUT}:
                target_visibility += 1
        for in_play in actor.in_play:
            if not self._in_play_effects_active(actor):
                continue
            if in_play.card.kind in {cards.SCOPE, cards.BINOCULAR}:
                actor_sight += 1
        if self._has_ability(target, "paul_regret"):
            target_visibility += 1
        if self._has_ability(actor, "rose_doolan"):
            actor_sight += 1
        return max(1, base + target_visibility - actor_sight)

    @staticmethod
    def _equipped_weapon(player: BangPlayer) -> BangCard | None:
        return next(
            (
                in_play.card
                for in_play in player.in_play
                if in_play.card.kind in cards.WEAPONS
            ),
            None,
        )

    def weapon_range(self, player: BangPlayer) -> int:
        weapon = self._equipped_weapon(player)
        if weapon and self._in_play_effects_active(player):
            return cards.WEAPON_RANGES[weapon.kind]
        return 1

    def _weapon_status(self, player: BangPlayer, locale: str) -> str:
        weapon = self._equipped_weapon(player)
        if not weapon:
            return Localization.get(locale, "bang-weapon-status-default")
        if not self._in_play_effects_active(player):
            return Localization.get(
                locale,
                "bang-weapon-status-inactive",
                weapon=card_name(weapon, locale),
            )
        return Localization.get(
            locale,
            "bang-weapon-status-equipped",
            weapon=card_name(weapon, locale),
            range=cards.WEAPON_RANGES[weapon.kind],
        )

    def _bang_limit(self, player: BangPlayer) -> int | None:
        if self._has_ability(player, "willy_the_kid"):
            return None
        if any(
            in_play.card.kind == cards.VOLCANIC
            and self._in_play_effects_active(player)
            for in_play in player.in_play
        ):
            return None
        return 2 if self.current_event == "shootout" else 1

    def _in_play_effects_active(self, owner: BangPlayer) -> bool:
        if self.current_event == "lasso":
            return False
        current = self.current_player
        return not (
            isinstance(current, BangPlayer)
            and current.id != owner.id
            and self._has_ability(current, "belle_star")
        )

    def _has_ability(self, player: BangPlayer, character_id: str) -> bool:
        if self.current_event == "hangover":
            return False
        effective = (
            player.copied_character
            if player.character == "vera_custer" and player.copied_character
            else player.character
        )
        return effective == character_id

    def _effective_suit(self, card: BangCard) -> str:
        if self.current_event == "blessing":
            return cards.HEARTS
        if self.current_event == "curse":
            return cards.SPADES
        return card.suit

    def _put_card_in_play(
        self,
        actor: BangPlayer,
        card: BangCard,
        target: BangPlayer | None,
    ) -> None:
        owner = target if card.kind == cards.JAIL and target else actor
        old_weapon: BangInPlayCard | None = None
        if card.kind in cards.WEAPONS:
            old_weapon = next(
                (
                    in_play
                    for in_play in actor.in_play
                    if in_play.card.kind in cards.WEAPONS
                ),
                None,
            )
            if old_weapon:
                actor.in_play.remove(old_weapon)
                self._discard(old_weapon.card)
        usable_after = self.turn_serial + 1 if card.border == cards.GREEN else 0
        owner.in_play.append(
            BangInPlayCard(card=card, usable_after_turn=usable_after)
        )
        self._play_equipment_sound(card.kind)
        if card.kind in cards.WEAPONS:
            self._announce_weapon_equipped(
                actor,
                card,
                old_weapon.card if old_weapon else None,
            )
        if self._has_ability(actor, "johnny_kisch"):
            for table_player in self.players_in_play:
                for other in list(table_player.in_play):
                    if other.card.id != card.id and other.card.kind == card.kind:
                        table_player.in_play.remove(other)
                        self._discard(other.card)
                        for listener in self.players:
                            user = self.get_user(listener)
                            if user:
                                if listener.id == actor.id:
                                    key = "bang-you-johnny-discard-copy"
                                elif listener.id == table_player.id:
                                    key = "bang-johnny-discards-your-copy"
                                else:
                                    key = "bang-johnny-discards-copy"
                                user.speak_l(
                                    key,
                                    buffer="game",
                                    actor=actor.name,
                                    player=table_player.name,
                                    card=card_name(card.kind, user.locale),
                                )
                        self._announce_colt_after_weapon_loss(
                            table_player,
                            other.card,
                        )

    def _resolve_committed_card(
        self,
        actor: BangPlayer,
        card: BangCard,
        target: BangPlayer | None,
    ) -> None:
        if (
            target
            and target.id != actor.id
            and self._apache_ignores(
                target,
                actor,
                card,
                duel=card.kind == cards.DUEL,
            )
        ):
            self._announce_unaffected(actor, target, card)
            self._finish_resolving_card()
            return
        kind = card.kind
        if kind == cards.BANG and target:
            self._start_shot(
                actor,
                target,
                source_kind="bang_card",
                required=(
                    2 if self._has_ability(actor, "slab_the_killer") else 1
                ),
            )
        elif kind == cards.DUEL and target:
            self._start_duel(actor, target)
        elif kind == cards.GATLING:
            self._start_multi_shot(actor, kind="gatling")
        elif kind == cards.INDIANS:
            self._start_indians(actor)
        elif kind == cards.GENERAL_STORE:
            self._start_general_store(actor)
        elif kind in {cards.CAT_BALOU, cards.PANIC} and target:
            self._start_target_card_choice(
                actor,
                target,
                mode="discard" if kind == cards.CAT_BALOU else "steal",
            )
        elif kind == cards.BRAWL:
            self._start_brawl(actor)
        elif kind in {cards.RAG_TIME, cards.CONESTOGA} and target:
            self._start_target_card_choice(actor, target, mode="steal")
        elif kind in {cards.CAN_CAN} and target:
            self._start_target_card_choice(actor, target, mode="discard")
        elif kind in {
            cards.PUNCH,
            cards.SPRINGFIELD,
            cards.BUFFALO_RIFLE,
            cards.KNIFE,
            cards.PEPPERBOX,
            cards.DERRINGER,
        } and target:
            self._start_shot(
                actor,
                target,
                source_kind=kind,
                required=1,
                draw_after=1 if kind == cards.DERRINGER else 0,
            )
        elif kind in {cards.HOWITZER}:
            self._start_multi_shot(actor, kind=kind)
        elif kind == cards.BEER:
            self._apply_beer(actor)
            self._finish_resolving_card()
        elif kind == cards.SALOON:
            self._start_saloon_sequence(actor)
        elif kind == cards.TEQUILA and target:
            self._play_consumable_sound(kind)
            if not self._heal(target, 1, actor=actor):
                self._announce_heal_card_no_effect(actor, target, card)
            self._finish_resolving_card()
        elif kind == cards.WHISKY:
            self._play_consumable_sound(kind)
            if not self._heal(actor, 2):
                self._announce_heal_card_no_effect(actor, actor, card)
            self._finish_resolving_card()
        elif kind == cards.CANTEEN:
            self._play_consumable_sound(kind)
            if not self._heal(actor, 1):
                self._announce_heal_card_no_effect(actor, actor, card)
            self._finish_resolving_card()
        elif kind == cards.STAGECOACH:
            self._draw_cards(actor, 2)
            self._finish_resolving_card()
        elif kind in {cards.WELLS_FARGO, cards.PONY_EXPRESS}:
            self._draw_cards(actor, 3)
            self._finish_resolving_card()
        elif kind == cards.BIBLE:
            self._draw_cards(actor, 1)
            self._finish_resolving_card()
        else:
            self._finish_resolving_card()

    def _apache_ignores(
        self,
        target: BangPlayer,
        actor: BangPlayer,
        card: BangCard,
        *,
        duel: bool,
    ) -> bool:
        return (
            not duel
            and actor.id != target.id
            and self._has_ability(target, "apache_kid")
            and self._effective_suit(card) == cards.DIAMONDS
        )

    def _forced_law_card(self, player: BangPlayer) -> BangCard | None:
        if not player.law_card_id:
            return None
        return self._card_in_hand(player, player.law_card_id)

    def _law_card_must_be_played(
        self,
        player: BangPlayer,
        card_id: int,
    ) -> bool:
        if self.current_player is not player or self.phase != PHASE_PLAY:
            return False
        forced = self._forced_law_card(player)
        return bool(
            forced
            and forced.id == card_id
            and self._can_normally_play(player, forced)
        )

    def _eligible_cost_cards(self, player: BangPlayer) -> list[BangCard]:
        return [
            card
            for card in player.hand
            if not self._law_card_must_be_played(player, card.id)
        ]

    def _can_normally_play(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> bool:
        return (
            self._normal_card_error(
                player,
                card,
                protect_law_cost=False,
            )
            is None
        )

    # ------------------------------------------------------------------
    # Serialized effect interpreter
    # ------------------------------------------------------------------

    def _top_effect(self) -> BangEffect:
        return self.effect_stack[-1]

    def _push_effect(self, effect: BangEffect) -> None:
        self.effect_stack.append(effect)
        self.phase = PHASE_RESOLVING

    def _pop_effect(self) -> None:
        if self.effect_stack:
            self.effect_stack.pop()

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict[str, Any],
    ) -> None:
        del sequence_id
        if callback_id == "finish_game_start":
            self._finish_game_start()
            return
        if callback_id == "announce_sniper_aim":
            actor = self.get_player_by_id(str(payload.get("actor_id", "")))
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            if isinstance(actor, BangPlayer) and isinstance(target, BangPlayer):
                self._announce_sniper_aim(actor, target)
            return
        if callback_id == "start_shot":
            actor = self.get_player_by_id(str(payload.get("actor_id", "")))
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            if not isinstance(target, BangPlayer) or not self._player_in_play(target):
                self._finish_effect_chain()
                return
            self._resolve_shot_now(
                actor if isinstance(actor, BangPlayer) else None,
                target,
                source_kind=str(payload.get("source_kind", "")),
                required=int(payload.get("required", 1)),
                source_player_id=str(payload.get("source_player_id", "")),
                card_kind=str(payload.get("card_kind", "")),
                draw_after=int(payload.get("draw_after", 0)),
                damage_amount=int(payload.get("damage_amount", 1)),
                stop_parent_on_hit=bool(
                    payload.get("stop_parent_on_hit", False)
                ),
                play_attack_sound=False,
            )
            return
        if callback_id == "start_russian_roulette":
            player_ids = payload.get("player_ids", [])
            if isinstance(player_ids, list):
                self._push_effect(
                    BangEffect(
                        kind="russian_roulette",
                        player_ids=[
                            str(player_id) for player_id in player_ids
                        ],
                    )
                )
            return
        if callback_id == "saloon_heal":
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            if (
                isinstance(target, BangPlayer)
                and self._player_in_play(target)
                and self._can_receive_heal(target)
            ):
                self._heal(target, 1, play_success_sound=False)
            return
        if callback_id == "finish_saloon":
            actor_id = str(payload.get("actor_id", ""))
            if (
                self.resolving_card
                and self.resolving_card.actor_id == actor_id
                and self.resolving_card.card.kind == cards.SALOON
            ):
                self._finish_resolving_card()
            return
        if callback_id == "dynamite_transfers":
            frame = self._top_effect() if self.effect_stack else None
            if frame and frame.kind == "turn_start":
                card_id = int(payload.get("card_id", 0))
                found = self._in_play_by_id(card_id)
                recipient = self.get_player_by_id(
                    str(payload.get("recipient_id", ""))
                )
                if (
                    found
                    and found[0].id == str(payload.get("owner_id", ""))
                    and found[1].card.kind == cards.DYNAMITE
                    and isinstance(recipient, BangPlayer)
                    and self._player_in_play(recipient)
                    and not any(
                        in_play.card.kind == cards.DYNAMITE
                        for in_play in recipient.in_play
                    )
                ):
                    owner, dynamite = found
                    owner.in_play.remove(dynamite)
                    recipient.in_play.append(dynamite)
                    self._broadcast_actor_target_l(
                        owner,
                        recipient,
                        "bang-your-dynamite-passes",
                        "bang-dynamite-passes-to-you",
                        "bang-dynamite-passes",
                    )
                frame.stage = "jail"
            return
        if callback_id == "dynamite_explodes":
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            found = self._in_play_by_id(int(payload.get("card_id", 0)))
            if not found or found[1].card.kind != cards.DYNAMITE:
                return
            owner, dynamite = found
            owner.in_play.remove(dynamite)
            self.discard_pile.append(dynamite.card)
            if isinstance(target, BangPlayer) and self._player_in_play(target):
                damage = BangEffect(
                    kind="damage",
                    target_id=target.id,
                    amount=3,
                    source=DamageSource(
                        kind="dynamite",
                        card_kind=cards.DYNAMITE,
                    ),
                    data={
                        "fall_trigger_tick": (
                            self.sound_scheduler_tick
                            + SequenceBeat.audio_delay_ticks(
                                game_audio.sound_ticks(
                                    game_audio.SOUND_DYNAMITE_AFTERMATH
                                ),
                                wait_ratio=(
                                    game_audio.LETHAL_FALL_TRIGGER_RATIO
                                ),
                            )
                        )
                    },
                )
                self._push_effect(damage)
                self._continue_damage(damage)
            return

    def _start_shot(
        self,
        actor: BangPlayer | None,
        target: BangPlayer,
        *,
        source_kind: str,
        required: int,
        source_player_id: str | None = None,
        draw_after: int = 0,
        damage_amount: int = 1,
        stop_parent_on_hit: bool = False,
    ) -> None:
        source_id = (
            source_player_id
            if source_player_id is not None
            else actor.id if actor else ""
        )
        card_kind = (
            self.resolving_card.card.kind if self.resolving_card else source_kind
        )
        payload = {
            "actor_id": actor.id if actor else "",
            "target_id": target.id,
            "source_kind": source_kind,
            "required": required,
            "source_player_id": source_id,
            "card_kind": card_kind,
            "draw_after": draw_after,
            "damage_amount": damage_amount,
            "stop_parent_on_hit": stop_parent_on_hit,
        }
        if source_kind == "sniper":
            fire_sound = self._random_sound(game_audio.SOUND_FIRE_SNIPER)
            casing_sound = self._random_sound(
                game_audio.SOUND_CASING_DROPS
            )
            self.phase = PHASE_RESOLVING
            self.start_sequence(
                self._next_audio_sequence_id("sniper"),
                [
                    SequenceBeat.after_audio(
                        game_audio.sound_ticks(
                            game_audio.SOUND_SNIPER_AIM
                        ),
                        wait_ratio=game_audio.WAIT_RATIO_SHORT_CUE,
                        ops=[
                            SequenceOperation.sound_op(
                                game_audio.SOUND_SNIPER_AIM
                            ),
                            SequenceOperation.callback_op(
                                "announce_sniper_aim",
                                {
                                    "actor_id": actor.id if actor else "",
                                    "target_id": target.id,
                                },
                            ),
                        ],
                    ),
                    SequenceBeat.after_audio(
                        game_audio.sound_ticks(fire_sound),
                        wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
                        ops=[
                            SequenceOperation.sound_op(fire_sound),
                            SequenceOperation.callback_op(
                                "start_shot",
                                payload,
                            ),
                        ],
                    ),
                    SequenceBeat.after_audio(
                        game_audio.sound_ticks(casing_sound),
                        wait_ratio=game_audio.WAIT_RATIO_LONG_EFFECT,
                        ops=[
                            SequenceOperation.sound_op(casing_sound)
                        ],
                    ),
                    SequenceBeat(),
                ],
                tag="bang_combat",
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            return
        self._resolve_shot_now(
            actor,
            target,
            source_kind=source_kind,
            required=required,
            source_player_id=source_id,
            card_kind=card_kind,
            draw_after=draw_after,
            damage_amount=damage_amount,
            stop_parent_on_hit=stop_parent_on_hit,
            play_attack_sound=source_kind != "russian_roulette",
        )

    def _resolve_shot_now(
        self,
        actor: BangPlayer | None,
        target: BangPlayer,
        *,
        source_kind: str,
        required: int,
        source_player_id: str,
        card_kind: str,
        draw_after: int,
        damage_amount: int,
        stop_parent_on_hit: bool,
        play_attack_sound: bool,
    ) -> None:
        attack_ticks = 0
        if play_attack_sound:
            attack_ticks = self._play_attack_sound(actor, source_kind)
        impact_not_before_tick = (
            self.sound_scheduler_tick
            + SequenceBeat.audio_delay_ticks(
                attack_ticks,
                wait_ratio=self._attack_wait_ratio(source_kind),
            )
            if attack_ticks
            else 0
        )
        self._push_effect(
            BangEffect(
                kind="shot",
                actor_id=actor.id if actor else "",
                target_id=target.id,
                required=required,
                source=DamageSource(
                    player_id=source_player_id,
                    kind=source_kind,
                    card_kind=card_kind,
                ),
                data={
                    **({"draw_after": draw_after} if draw_after else {}),
                    **(
                        {"damage_amount": damage_amount}
                        if damage_amount != 1
                        else {}
                    ),
                    **(
                        {"stop_parent_on_hit": True}
                        if stop_parent_on_hit
                        else {}
                    ),
                    **(
                        {"impact_not_before_tick": impact_not_before_tick}
                        if impact_not_before_tick
                        else {}
                    ),
                },
            )
        )
        self._announce_shot(
            actor,
            target,
            source_kind,
        )
        self._continue_effects()

    def _start_multi_shot(self, actor: BangPlayer, *, kind: str) -> None:
        targets = self._clockwise_after(actor, exclude_actor=True)
        self._push_effect(
            BangEffect(
                kind="multi_shot",
                actor_id=actor.id,
                player_ids=[target.id for target in targets],
                source=DamageSource(
                    player_id=actor.id,
                    kind=kind,
                    card_kind=kind,
                ),
            )
        )
        if kind in game_audio.SINGLE_FIRE_MULTI_ATTACKS:
            attack_ticks = self._play_attack_sound(actor, kind)
            self._stagger_effect_audio(
                attack_ticks,
                wait_ratio=(
                    game_audio.WAIT_RATIO_BARRAGE_LEAD
                    if kind == cards.GATLING
                    else self._attack_wait_ratio(kind)
                ),
            )
        self._continue_effects()

    def _start_indians(self, actor: BangPlayer) -> None:
        targets = self._clockwise_after(actor, exclude_actor=True)
        self._push_effect(
            BangEffect(
                kind="indians",
                actor_id=actor.id,
                player_ids=[target.id for target in targets],
                source=DamageSource(
                    player_id=actor.id,
                    kind="indians",
                    card_kind=cards.INDIANS,
                ),
            )
        )
        self._continue_effects()

    def _start_duel(self, actor: BangPlayer, target: BangPlayer) -> None:
        self._push_effect(
            BangEffect(
                kind="duel",
                actor_id=actor.id,
                target_id=target.id,
                source=DamageSource(
                    player_id=actor.id,
                    kind="duel",
                    card_kind=cards.DUEL,
                ),
                data={"responder_id": target.id},
            )
        )
        self._continue_effects()

    def _start_general_store(self, actor: BangPlayer) -> None:
        order = [actor, *self._clockwise_after(actor, exclude_actor=True)]
        self._push_effect(
            BangEffect(
                kind="general_store",
                actor_id=actor.id,
                player_ids=[player.id for player in order],
            )
        )
        self._continue_effects()

    def _start_saloon_sequence(self, actor: BangPlayer) -> None:
        healable = [
            player
            for player in self.players_in_play
            if self._can_receive_heal(player)
        ]
        if not healable:
            self.broadcast_personal_l(
                actor,
                "bang-your-saloon-no-effect",
                "bang-player-saloon-no-effect",
                buffer="game",
            )
            self._finish_resolving_card()
            return

        drinks = [game_audio.SOUND_DRINK_BEER]
        if len(healable) > 1:
            drinks.append(game_audio.SOUND_DRINK_WHISKY)
        drinks.extend(
            self._random_sound(
                (
                    game_audio.SOUND_DRINK_BEER,
                    game_audio.SOUND_DRINK_WHISKY,
                )
            )
            for _ in range(len(healable) - len(drinks))
        )
        random.shuffle(drinks)  # nosec B311 - cosmetic sound placement

        if len(healable) == 1:
            pans = [0]
        else:
            pan_span = (
                game_audio.SALOON_PAN_RIGHT
                - game_audio.SALOON_PAN_LEFT
            )
            pans = [
                round(
                    game_audio.SALOON_PAN_LEFT
                    + pan_span * index / (len(healable) - 1)
                )
                for index in range(len(healable))
            ]

        beats: list[SequenceBeat] = []
        for index, (target, drink, pan) in enumerate(
            zip(healable, drinks, pans)
        ):
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(drink, pan=pan),
                        SequenceOperation.sound_op(
                            game_audio.SOUND_HEAL_SUCCESS,
                            pan=pan,
                        ),
                        SequenceOperation.callback_op(
                            "saloon_heal",
                            {"target_id": target.id},
                        ),
                    ],
                    delay_after_ticks=(
                        random.randint(  # nosec B311 - cosmetic timing
                            game_audio.SALOON_STAGGER_MIN_TICKS,
                            game_audio.SALOON_STAGGER_MAX_TICKS,
                        )
                        if index < len(healable) - 1
                        else 0
                    ),
                )
            )
        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "finish_saloon",
                        {"actor_id": actor.id},
                    )
                ]
            )
        )
        self.start_sequence(
            self._next_audio_sequence_id("saloon"),
            beats,
            tag="bang_saloon",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _start_target_card_choice(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        *,
        mode: str,
    ) -> None:
        self._push_effect(
            BangEffect(
                kind="target_card",
                actor_id=actor.id,
                target_id=target.id,
                data={"mode": mode},
            )
        )
        self._continue_effects()

    def _start_brawl(self, actor: BangPlayer) -> None:
        targets = self._clockwise_after(actor, exclude_actor=True)
        self._push_effect(
            BangEffect(
                kind="brawl",
                actor_id=actor.id,
                player_ids=[target.id for target in targets],
            )
        )
        self._continue_effects()

    def _start_ricochet(
        self,
        actor: BangPlayer,
        owner: BangPlayer,
        in_play_card_id: int,
    ) -> None:
        attack_ticks = self._play_attack_sound(actor, "ricochet")
        impact_not_before_tick = (
            self.sound_scheduler_tick
            + SequenceBeat.audio_delay_ticks(
                attack_ticks,
                wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
            )
        )
        self._push_effect(
            BangEffect(
                kind="ricochet",
                actor_id=actor.id,
                target_id=owner.id,
                card_ids=[in_play_card_id],
                required=1,
                source=DamageSource(
                    player_id=actor.id,
                    kind="ricochet",
                    card_kind=cards.BANG,
                ),
                data={"impact_not_before_tick": impact_not_before_tick},
            )
        )
        self._continue_effects()

    def _continue_effects(self) -> None:
        steps = 0
        while (
            self.game_active
            and self.effect_stack
            and self.decision is None
            and not self.is_sequence_gameplay_locked()
            and steps < MAX_EFFECT_STEPS
        ):
            steps += 1
            frame = self._top_effect()
            handler = getattr(self, f"_continue_{frame.kind}", None)
            if not handler:
                self._pop_effect()
                continue
            handler(frame)
        if steps >= MAX_EFFECT_STEPS and self.effect_stack:
            raise RuntimeError("BANG! effect interpreter exceeded transition limit")
        if not self.effect_stack and self.decision is None:
            self._finish_effect_chain()
        self.refresh_menus()

    def _finish_effect_chain(self) -> None:
        if self.resolving_card:
            self._finish_resolving_card()
            return
        self._finish_atomic_effect()

    def _finish_resolving_card(self) -> None:
        if self.resolving_card:
            self._discard(self.resolving_card.card)
            self.resolving_card = None
        self._finish_atomic_effect()

    def _finish_atomic_effect(self) -> None:
        if not self.game_active:
            return
        self._resolve_deferred_character_draws()
        current = self.current_player
        if (
            isinstance(current, BangPlayer)
            and not self._player_in_play(current)
            and self.phase == PHASE_RESOLVING
        ):
            self._advance_to_next_eligible()
            return
        if (
            isinstance(current, BangPlayer)
            and self._player_in_play(current)
            and self.phase not in {
                PHASE_START_TURN,
                PHASE_DRAW,
                PHASE_DISCARD,
                PHASE_GAME_OVER,
            }
        ):
            self.phase = PHASE_PLAY
        self.refresh_menus()
        self._pace_bots()

    def _continue_shot(self, frame: BangEffect) -> None:
        target = self.get_player_by_id(frame.target_id)
        actor = self.get_player_by_id(frame.actor_id)
        if not isinstance(target, BangPlayer) or not self._player_in_play(target):
            self._pop_effect()
            return
        if frame.stage == "start":
            if (
                isinstance(actor, BangPlayer)
                and self.resolving_card
                and self._apache_ignores(
                    target,
                    actor,
                    self.resolving_card.card,
                    duel=False,
                )
            ):
                self._announce_unaffected(actor, target, frame.source.kind)
                self._pop_effect()
                return
            frame.data["misses_remaining"] = frame.required or 1
            frame.data["barrels_remaining"] = self._barrel_chances(target)
            frame.stage = "barrel"
            return
        if frame.stage == "barrel":
            if int(frame.data.get("misses_remaining", 0)) <= 0:
                self._complete_shot(frame)
                return
            if int(frame.data.get("barrels_remaining", 0)) > 0:
                self.decision = BangDecision(
                    kind="barrel",
                    player_id=target.id,
                    prompt_key="bang-prompt-barrel",
                    item_ids=["use_barrel", "skip_barrels"],
                    data={"effect_depth": len(self.effect_stack)},
                )
                self._focus_decision(target)
                return
            frame.stage = "response"
            return
        if frame.stage == "barrel_draw":
            result = self._draw_check_result(
                frame,
                target,
                purpose="barrel",
                suit=cards.HEARTS,
            )
            if result is None:
                return
            if result:
                frame.data["misses_remaining"] = max(
                    0,
                    int(frame.data.get("misses_remaining", 1)) - 1,
                )
                sound = self._random_sound(
                    game_audio.SOUND_IMPACT_WOOD_BARREL
                )
                self.play_sound(sound)
                self._announce_barrel_result(target, frame, succeeded=True)
            else:
                sound = self._random_sound(
                    game_audio.SOUND_DEFENSE_BARREL_FAIL
                )
                self.play_sound(sound)
                self._announce_barrel_result(target, frame, succeeded=False)
            frame.stage = "barrel"
            self._stagger_effect_audio(
                game_audio.sound_ticks(sound),
                wait_ratio=(
                    game_audio.WAIT_RATIO_SHORT_CUE
                    if result
                    else game_audio.WAIT_RATIO_FAILED_DEFENSE
                ),
            )
            return
        if frame.stage == "response":
            if int(frame.data.get("misses_remaining", 0)) <= 0:
                self._complete_shot(frame)
                return
            if "response_hand_ids" not in frame.data:
                frame.data["response_hand_ids"] = [
                    card.id
                    for card in target.hand
                    if self._card_can_miss(target, card)
                    and self._handcuffs_allows_card(target, card)
                ]
                frame.data["response_green_ids"] = [
                    in_play.card.id
                    for in_play in target.in_play
                    if in_play.card.kind in cards.GREEN_MISSED_CARDS
                    and in_play.usable_after_turn <= self.turn_serial
                    and self._in_play_effects_active(target)
                ]
            hand_ids = [
                card_id
                for card_id in frame.data.get("response_hand_ids", [])
                if (
                    (card := self._card_in_hand(target, card_id))
                    and self._card_can_miss(target, card)
                    and self._handcuffs_allows_card(target, card)
                )
            ]
            green_ids = [
                card_id
                for card_id in frame.data.get("response_green_ids", [])
                if (
                    (found := self._in_play_by_id(card_id))
                    and found[0].id == target.id
                    and found[1].card.kind in cards.GREEN_MISSED_CARDS
                    and found[1].usable_after_turn <= self.turn_serial
                    and self._in_play_effects_active(target)
                )
            ]
            if not hand_ids and not green_ids:
                frame.stage = "damage"
                return
            self.decision = BangDecision(
                kind="missed",
                player_id=target.id,
                prompt_key="bang-prompt-missed",
                card_ids=hand_ids,
                item_ids=["take_hit"],
                data={
                    "green_card_ids": green_ids,
                    "misses_remaining": int(
                        frame.data.get("misses_remaining", 1)
                    ),
                    "effect_depth": len(self.effect_stack),
                },
            )
            self._focus_decision(target)
            return
        if frame.stage == "damage":
            impact_not_before = int(
                frame.data.get("impact_not_before_tick", 0)
            )
            if self._wait_until_effect_tick(impact_not_before):
                return
            frame.stage = "after_damage"
            if frame.data.get("stop_parent_on_hit") and len(self.effect_stack) >= 2:
                self.effect_stack[-2].data["stop"] = True
            self._push_effect(
                BangEffect(
                    kind="damage",
                    target_id=target.id,
                    amount=int(frame.data.get("damage_amount", 1)),
                    source=frame.source,
                )
            )
            return
        if frame.stage == "after_damage":
            self._complete_shot(frame)

    def _complete_shot(self, frame: BangEffect) -> None:
        draw_after = int(frame.data.get("draw_after", 0))
        actor = self.get_player_by_id(frame.actor_id)
        self._pop_effect()
        if draw_after and isinstance(actor, BangPlayer):
            self._draw_cards(actor, draw_after)

    def _continue_multi_shot(self, frame: BangEffect) -> None:
        while frame.index < len(frame.player_ids):
            target = self.get_player_by_id(frame.player_ids[frame.index])
            frame.index += 1
            if not isinstance(target, BangPlayer) or not self._player_in_play(target):
                continue
            actor = self.get_player_by_id(frame.actor_id)
            if not isinstance(actor, BangPlayer):
                continue
            if (
                self.resolving_card
                and self._apache_ignores(
                    target,
                    actor,
                    self.resolving_card.card,
                    duel=False,
                )
            ):
                self._announce_unaffected(
                    actor,
                    target,
                    self.resolving_card.card,
                )
                continue
            if frame.source.kind not in game_audio.SINGLE_FIRE_MULTI_ATTACKS:
                attack_ticks = self._play_attack_sound(
                    actor,
                    frame.source.kind,
                )
                self._stagger_effect_audio(
                    attack_ticks,
                    wait_ratio=self._attack_wait_ratio(frame.source.kind),
                )
            self._announce_shot(
                actor,
                target,
                frame.source.kind,
            )
            self._push_effect(
                BangEffect(
                    kind="shot",
                    actor_id=actor.id,
                    target_id=target.id,
                    required=1,
                    source=frame.source,
                )
            )
            return
        self._pop_effect()

    def _continue_indians(self, frame: BangEffect) -> None:
        if frame.stage == "waiting":
            frame.stage = "start"
        while frame.index < len(frame.player_ids):
            target = self.get_player_by_id(frame.player_ids[frame.index])
            frame.index += 1
            if not isinstance(target, BangPlayer) or not self._player_in_play(target):
                continue
            actor = self.get_player_by_id(frame.actor_id)
            if (
                isinstance(actor, BangPlayer)
                and self.resolving_card
                and self._apache_ignores(
                    target,
                    actor,
                    self.resolving_card.card,
                    duel=False,
                )
            ):
                self._announce_unaffected(
                    actor,
                    target,
                    self.resolving_card.card,
                )
                continue
            bang_ids = [
                card.id
                for card in target.hand
                if self._card_can_be_bang_response(target, card)
                and self._handcuffs_allows_card(target, card)
            ]
            if not bang_ids:
                frame.stage = "waiting"
                self._push_effect(
                    BangEffect(
                        kind="damage",
                        target_id=target.id,
                        amount=1,
                        source=frame.source,
                    )
                )
                return
            frame.data["current_target_id"] = target.id
            self.decision = BangDecision(
                kind="indians",
                player_id=target.id,
                prompt_key="bang-prompt-indians",
                card_ids=bang_ids,
                item_ids=["take_hit"],
            )
            self._focus_decision(target)
            return
        self._pop_effect()

    def _continue_duel(self, frame: BangEffect) -> None:
        responder = self.get_player_by_id(str(frame.data.get("responder_id", "")))
        if not isinstance(responder, BangPlayer) or not self._player_in_play(responder):
            self._pop_effect()
            return
        bang_ids = [
            card.id
            for card in responder.hand
            if self._card_can_be_bang_response(responder, card)
            and self._handcuffs_allows_card(responder, card)
            and not (
                self.current_event == "the_sermon"
                and self.current_player is responder
            )
        ]
        self.decision = BangDecision(
            kind="duel",
            player_id=responder.id,
            prompt_key="bang-prompt-duel",
            card_ids=bang_ids,
            item_ids=["lose_duel"],
        )
        self._focus_decision(responder)

    def _continue_general_store(self, frame: BangEffect) -> None:
        if frame.stage == "start":
            self.general_store_cards = [
                card
                for _ in range(len(self.players_in_play))
                if (card := self._draw_one())
            ]
            for listener in self.players:
                user = self.get_user(listener)
                if user:
                    user.speak_l(
                        "bang-general-store-reveals",
                        buffer="game",
                        count=len(self.general_store_cards),
                        cards=Localization.format_list_and(
                            user.locale,
                            [
                                card_label(card, user.locale)
                                for card in self.general_store_cards
                            ],
                        ),
                    )
            frame.stage = "choose"
        while frame.index < len(frame.player_ids):
            chooser = self.get_player_by_id(frame.player_ids[frame.index])
            if (
                not isinstance(chooser, BangPlayer)
                or not self._player_in_play(chooser)
            ):
                frame.index += 1
                continue
            if not self.general_store_cards:
                break
            self.decision = BangDecision(
                kind="general_store",
                player_id=chooser.id,
                prompt_key="bang-prompt-general-store",
                item_ids=[
                    f"store_{card.id}" for card in self.general_store_cards
                ],
            )
            self._focus_decision(chooser)
            return
        for card in self.general_store_cards:
            self._discard(card)
        self.general_store_cards.clear()
        self._pop_effect()

    def _continue_target_card(self, frame: BangEffect) -> None:
        actor = self.get_player_by_id(frame.actor_id)
        target = self.get_player_by_id(frame.target_id)
        if (
            not isinstance(actor, BangPlayer)
            or not isinstance(target, BangPlayer)
            or not self._player_in_play(target)
            or not (target.hand or target.in_play)
        ):
            self._pop_effect()
            return
        item_ids = []
        if target.hand:
            item_ids.append("random_hand")
        item_ids.extend(
            f"in_play_{in_play.card.id}" for in_play in target.in_play
        )
        self.decision = BangDecision(
            kind="target_card",
            player_id=actor.id,
            prompt_key="bang-prompt-target-card",
            item_ids=item_ids,
            data={
                "target_id": target.id,
                "mode": frame.data.get("mode", "discard"),
            },
        )
        if len(item_ids) == 1:
            self._resolve_target_card_item(actor, self.decision, item_ids[0])
            return
        self._focus_decision(actor)

    def _continue_brawl(self, frame: BangEffect) -> None:
        while frame.index < len(frame.player_ids):
            target = self.get_player_by_id(frame.player_ids[frame.index])
            frame.index += 1
            if (
                not isinstance(target, BangPlayer)
                or not self._player_in_play(target)
                or not (target.hand or target.in_play)
            ):
                continue
            actor = self.get_player_by_id(frame.actor_id)
            if not isinstance(actor, BangPlayer):
                continue
            self._push_effect(
                BangEffect(
                    kind="target_card",
                    actor_id=actor.id,
                    target_id=target.id,
                    data={"mode": "discard"},
                )
            )
            return
        self._pop_effect()

    def _continue_ricochet(self, frame: BangEffect) -> None:
        actor = self.get_player_by_id(frame.actor_id)
        target = self.get_player_by_id(frame.target_id)
        found = self._in_play_by_id(frame.card_ids[0]) if frame.card_ids else None
        if (
            not isinstance(actor, BangPlayer)
            or not isinstance(target, BangPlayer)
            or not found
            or found[0].id != target.id
        ):
            self._pop_effect()
            return
        if frame.stage == "start":
            frame.data["barrels_remaining"] = self._barrel_chances(target)
            frame.stage = "barrel"
        if frame.stage == "barrel":
            if int(frame.data.get("barrels_remaining", 0)) > 0:
                self.decision = BangDecision(
                    kind="barrel",
                    player_id=target.id,
                    prompt_key="bang-prompt-barrel",
                    item_ids=["use_barrel", "skip_barrels"],
                    data={"effect_depth": len(self.effect_stack)},
                )
                self._focus_decision(target)
                return
            frame.stage = "response"
        if frame.stage == "barrel_draw":
            result = self._draw_check_result(
                frame,
                target,
                purpose="barrel",
                suit=cards.HEARTS,
            )
            if result is None:
                return
            if result:
                sound = self._random_sound(
                    game_audio.SOUND_IMPACT_WOOD_BARREL
                )
                self.play_sound(sound)
                self._announce_ricochet_saved(target, cards.BARREL, frame)
                self._pop_effect()
            else:
                sound = self._random_sound(
                    game_audio.SOUND_DEFENSE_BARREL_FAIL
                )
                self.play_sound(sound)
                self._announce_barrel_result(target, frame, succeeded=False)
                frame.stage = "barrel"
            self._stagger_effect_audio(
                game_audio.sound_ticks(sound),
                wait_ratio=(
                    game_audio.WAIT_RATIO_SHORT_CUE
                    if result
                    else game_audio.WAIT_RATIO_FAILED_DEFENSE
                ),
            )
            return
        if frame.stage == "response":
            hand_ids = [
                card.id
                for card in target.hand
                if self._card_can_miss(target, card)
                and self._handcuffs_allows_card(target, card)
            ]
            green_ids = [
                in_play.card.id
                for in_play in target.in_play
                if in_play.card.kind in cards.GREEN_MISSED_CARDS
                and in_play.usable_after_turn <= self.turn_serial
                and self._in_play_effects_active(target)
            ]
            if not hand_ids and not green_ids:
                frame.stage = "discard"
                return
            self.decision = BangDecision(
                kind="ricochet",
                player_id=target.id,
                prompt_key="bang-prompt-ricochet",
                card_ids=hand_ids,
                item_ids=["lose_in_play"],
                data={
                    "green_card_ids": green_ids,
                    "effect_depth": len(self.effect_stack),
                },
            )
            self._focus_decision(target)
            return
        if frame.stage == "discard":
            impact_not_before = int(
                frame.data.get("impact_not_before_tick", 0)
            )
            if self._wait_until_effect_tick(impact_not_before):
                return
            current = self._in_play_by_id(frame.card_ids[0])
            if current:
                owner, in_play = current
                owner.in_play.remove(in_play)
                self._discard(in_play.card)
                impact = self._random_sound(
                    game_audio.SOUND_IMPACT_RICOCHET
                )
                self.play_sound(impact)
                self._announce_ricochet_discarded(
                    actor,
                    owner,
                    in_play.card,
                )
                self._announce_colt_after_weapon_loss(owner, in_play.card)
                self._stagger_effect_audio(
                    game_audio.sound_ticks(impact),
                    wait_ratio=game_audio.WAIT_RATIO_SHORT_CUE,
                )
            self._pop_effect()

    def _continue_damage(self, frame: BangEffect) -> None:
        target = self.get_player_by_id(frame.target_id)
        if not isinstance(target, BangPlayer) or not self._player_in_play(target):
            self._pop_effect()
            return
        if frame.stage == "start":
            if target.ghost_active:
                defense_ticks = self._play_defense_sound(
                    source_kind=frame.source.kind
                )
                self.broadcast_personal_l(
                    target,
                    "bang-you-ghost-ignore-damage",
                    "bang-player-ghost-ignores-damage",
                    buffer="game",
                )
                self._pop_effect()
                self._stagger_effect_audio(
                    defense_ticks,
                    wait_ratio=game_audio.WAIT_RATIO_REACTION,
                )
                return
            if frame.source.kind == "russian_roulette":
                self.play_sound(game_audio.SOUND_ROULETTE_GUNSHOT)
                frame.stage = "roulette_impact"
                self._stagger_effect_audio(
                    game_audio.sound_ticks(
                        game_audio.SOUND_ROULETTE_GUNSHOT
                    ),
                    wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
                )
                return
        if frame.stage in {"start", "roulette_impact"}:
            target.life -= frame.amount
            impact_ticks = self._play_damage_impact(frame.source)
            if impact_ticks:
                frame.data["fall_trigger_tick"] = (
                    self.sound_scheduler_tick
                    + SequenceBeat.audio_delay_ticks(
                        impact_ticks,
                        wait_ratio=game_audio.LETHAL_FALL_TRIGGER_RATIO,
                    )
                )
            self._announce_damage(target, frame.amount, frame.source)
            frame.stage = "lethal" if target.life <= 0 else "survived"
            if impact_ticks:
                self._stagger_effect_audio(
                    impact_ticks,
                    wait_ratio=self._impact_wait_ratio(frame.source),
                )
            return
        if frame.stage == "lethal":
            if target.life > 0:
                frame.stage = "survived"
                return
            if self._open_lethal_recovery(target):
                return
            frame.stage = "eliminate"
            return
        if frame.stage == "survived":
            self._apply_survived_damage_triggers(target, frame)
            self._pop_effect()
            return
        if frame.stage == "eliminate":
            frame.stage = "after_elimination"
            self._push_effect(
                BangEffect(
                    kind="elimination",
                    target_id=target.id,
                    source=frame.source,
                    data={
                        "fall_trigger_tick": int(
                            frame.data.get(
                                "fall_trigger_tick",
                                # Backward compatibility for an in-flight save
                                # created before proportional fall triggering.
                                frame.data.get("impact_finished_tick", 0),
                            )
                        )
                    },
                )
            )
            return
        if frame.stage == "after_elimination":
            self._pop_effect()

    def _continue_elimination(self, frame: BangEffect) -> None:
        victim = self.get_player_by_id(frame.target_id)
        if not isinstance(victim, BangPlayer):
            self._pop_effect()
            return
        if frame.stage == "start":
            if self._wait_until_effect_tick(
                int(
                    frame.data.get(
                        "fall_trigger_tick",
                        # Backward compatibility for an elimination frame
                        # saved under the former full-impact wait.
                        frame.data.get("fall_not_before_tick", 0),
                    )
                )
            ):
                return
            victim.life = 0
            victim.ghost_active = False
            victim.eliminated = True
            victim.role_revealed = True
            self.elimination_counter += 1
            victim.elimination_order = self.elimination_counter
            if not self.first_eliminated_id:
                self.first_eliminated_id = victim.id
            killer = self.get_player_by_id(frame.source.player_id)
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                if listener.id == victim.id:
                    key = "bang-you-are-eliminated"
                elif (
                    isinstance(killer, BangPlayer)
                    and killer.id != victim.id
                    and listener.id == killer.id
                ):
                    key = "bang-you-eliminate-player"
                else:
                    key = "bang-player-is-eliminated"
                user.speak_l(
                    key,
                    buffer="game",
                    player=victim.name,
                    target=victim.name,
                    role=self._role_name(victim.role, user.locale),
                )
            collectors = self._vulture_collectors(victim)
            frame.player_ids = [collector.id for collector in collectors]
            frame.index = 0
            frame.data["after_fall_stage"] = (
                "vulture" if collectors else "discard"
            )
            if frame.source.kind == "ghost_town":
                frame.stage = str(frame.data["after_fall_stage"])
                self.refresh_menus()
                return
            self._play_or_schedule_elimination_fall()
            frame.stage = str(frame.data["after_fall_stage"])
            self.refresh_menus()
            # Fall playback is deliberately fire-and-forget. Continue through
            # card disposal, rewards, penalties, and victory in this same
            # interpreter pass.
        if frame.stage == "fall":
            # Backward compatibility for saves made while the former blocking
            # fall sequence was active.
            frame.stage = str(
                frame.data.get("after_fall_stage", "discard")
            )
            return
        if frame.stage == "discard":
            if victim.hand or victim.in_play:
                self.decision = BangDecision(
                    kind="elimination_discard",
                    player_id=victim.id,
                    prompt_key="bang-prompt-elimination-discard",
                    card_ids=[card.id for card in victim.hand],
                    item_ids=[
                        f"in_play_{in_play.card.id}"
                        for in_play in victim.in_play
                    ]
                    + ["finish_elimination_discard"],
                )
                self._focus_decision(victim)
                return
            frame.stage = "after_cards"
            return
        if frame.stage == "vulture":
            if not (victim.hand or victim.in_play):
                frame.stage = "after_cards"
                return
            collectors = [
                collector
                for player_id in frame.player_ids
                if isinstance(
                    collector := self.get_player_by_id(player_id),
                    BangPlayer,
                )
                and self._player_in_play(collector)
                and self._has_ability(collector, "vulture_sam")
            ]
            if not collectors:
                frame.stage = "discard"
                return
            collector = collectors[frame.index % len(collectors)]
            frame.index += 1
            items = []
            if victim.hand:
                items.append("random_hand")
            items.extend(
                f"in_play_{in_play.card.id}" for in_play in victim.in_play
            )
            self.decision = BangDecision(
                kind="vulture",
                player_id=collector.id,
                prompt_key="bang-prompt-vulture",
                item_ids=items,
                data={"victim_id": victim.id},
            )
            self._focus_decision(collector)
            return
        if frame.stage == "after_cards":
            self._apply_elimination_triggers(victim, frame.source)
            if not self.game_active:
                return
            frame.stage = "done"
            return
        if frame.stage == "done":
            self._pop_effect()

    def _open_lethal_recovery(self, player: BangPlayer) -> bool:
        beer_ids = []
        if len(self.players_in_play) > 2 and self.current_event != "the_reverend":
            beer_ids = [
                card.id
                for card in player.hand
                if card.kind == cards.BEER
                and self._handcuffs_allows_card(player, card)
            ]
        items = ["accept_death"]
        if (
            self._has_ability(player, "sid_ketchum")
            and len(self._eligible_cost_cards(player)) >= 2
        ):
            items.insert(0, "use_sid")
        if not beer_ids and items == ["accept_death"]:
            return False
        self.decision = BangDecision(
            kind="lethal_recovery",
            player_id=player.id,
            prompt_key="bang-prompt-lethal-recovery",
            card_ids=beer_ids,
            item_ids=items,
            data={"life": player.life},
        )
        self._focus_decision(player)
        return True

    def _finish_lethal_recovery_attempt(self, player: BangPlayer) -> None:
        self.decision = None
        if player.life > 0:
            top = self._top_effect()
            if top.kind == "damage":
                top.stage = "survived"
            self._continue_effects()
            return
        if self._open_lethal_recovery(player):
            return
        top = self._top_effect()
        if top.kind == "damage":
            top.stage = "eliminate"
        self._continue_effects()

    def _barrel_chances(self, player: BangPlayer) -> int:
        chances = int(self._has_ability(player, "jourdonnais"))
        chances += sum(
            in_play.card.kind == cards.BARREL
            and self._in_play_effects_active(player)
            for in_play in player.in_play
        )
        return chances

    def _card_can_miss(self, player: BangPlayer, card: BangCard) -> bool:
        if card.kind in {cards.MISSED, cards.DODGE}:
            return True
        if self._has_ability(player, "calamity_janet") and card.kind == cards.BANG:
            return True
        return self._has_ability(player, "elena_fuente")

    def _card_can_be_bang_response(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> bool:
        if card.kind == cards.BANG:
            return True
        return (
            self._has_ability(player, "calamity_janet")
            and card.kind == cards.MISSED
        )

    def _response_frame_for_decision(
        self,
        player: BangPlayer,
        decision: BangDecision,
    ) -> BangEffect | None:
        if decision.player_id != player.id or decision.kind not in {
            "missed",
            "ricochet",
        }:
            return None
        effect_depth = decision.data.get("effect_depth")
        if (
            isinstance(effect_depth, int)
            and effect_depth != len(self.effect_stack)
        ):
            return None
        if not self.effect_stack:
            return None
        frame = self._top_effect()
        if frame.target_id != player.id or frame.stage != "response":
            return None
        if decision.kind == "missed":
            misses_remaining = frame.data.get("misses_remaining", 0)
            if (
                frame.kind != "shot"
                or not isinstance(misses_remaining, int)
                or misses_remaining <= 0
            ):
                return None
            return frame
        return frame if frame.kind == "ricochet" else None

    def _use_decision_card(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> None:
        decision = self.decision
        if not decision or decision.player_id != player.id:
            return
        if card.id not in decision.card_ids:
            return
        if decision.kind == "lethal_recovery":
            player.hand.remove(card)
            self._discard(card)
            self._apply_beer(player, allow_from_zero=True)
            self._record_molly_response(player, card, defer=False)
            self._finish_lethal_recovery_attempt(player)
            return
        if decision.kind in {"missed", "ricochet"}:
            frame = self._response_frame_for_decision(player, decision)
            if frame is None:
                self._speak_action_disabled_reason(
                    player,
                    "bang-error-card-not-response",
                )
                return
            player.hand.remove(card)
            self._discard(card)
            defense_ticks = self._play_defense_sound(
                card,
                russian_roulette=(
                    frame.source.kind == "russian_roulette"
                ),
                source_kind=frame.source.kind,
            )
            remaining = 0
            if decision.kind == "ricochet":
                self._announce_ricochet_saved(player, card, frame)
            else:
                remaining = max(
                    0,
                    int(frame.data.get("misses_remaining", 1)) - 1,
                )
                frame.data["misses_remaining"] = remaining
                self._announce_shot_response(
                    player,
                    card,
                    frame,
                    remaining=remaining,
                )
            drawn: list[BangCard] = []
            if card.kind == cards.DODGE:
                drawn = self._draw_cards(player, 1)
            self._record_molly_response(player, card, defer=False)
            self.decision = None
            if decision.kind == "ricochet":
                self._pop_effect()
            else:
                response_ids = frame.data.get("response_hand_ids")
                if isinstance(response_ids, list):
                    response_ids.extend(
                        drawn_card.id
                        for drawn_card in drawn
                        if self._card_can_miss(player, drawn_card)
                    )
                frame.stage = "response" if remaining else "done"
                if not remaining:
                    self._complete_shot(frame)
            self._stagger_effect_audio(
                defense_ticks,
                wait_ratio=game_audio.WAIT_RATIO_REACTION,
            )
            self._continue_effects()
            return
        if decision.kind == "indians":
            player.hand.remove(card)
            self._discard(card)
            attack_ticks = self._play_attack_sound(
                player,
                "indians_response",
            )
            self._announce_indians_response(
                player,
                card,
                self._top_effect(),
            )
            self._record_molly_response(player, card, defer=False)
            self.decision = None
            self._stagger_effect_audio(
                attack_ticks,
                wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
            )
            self._continue_effects()
            return
        if decision.kind == "duel":
            player.hand.remove(card)
            self._discard(card)
            frame = self._top_effect()
            attack_ticks = self._play_attack_sound(
                player,
                "duel_response",
            )
            frame.data["last_shot_player_id"] = player.id
            self._announce_duel_response(player, card, frame)
            self._record_molly_response(player, card, defer=True)
            self.decision = None
            other_id = (
                frame.actor_id
                if player.id == frame.target_id
                else frame.target_id
            )
            frame.data["responder_id"] = other_id
            self._stagger_effect_audio(
                attack_ticks,
                wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
            )
            self._continue_effects()
            return
        if decision.kind == "discard_excess":
            self._select_discard_card(player, card)
            return
        if decision.kind == "ranch":
            self._toggle_card_selection(
                player,
                card,
                decision.selected_card_ids,
            )
            return
        if decision.kind == "elimination_discard":
            self._discard_next_elimination_card(player, card)

    def _use_green_response(
        self,
        player: BangPlayer,
        in_play: BangInPlayCard,
    ) -> None:
        decision = self.decision
        if (
            not decision
            or decision.player_id != player.id
            or in_play.card.id not in decision.data.get("green_card_ids", [])
        ):
            return
        frame = self._response_frame_for_decision(player, decision)
        if (
            frame is None
            or in_play not in player.in_play
            or in_play.card.border != cards.GREEN
            or in_play.card.kind not in cards.GREEN_MISSED_CARDS
            or in_play.usable_after_turn > self.turn_serial
            or not self._in_play_effects_active(player)
        ):
            self._speak_action_disabled_reason(
                player,
                "bang-error-card-not-response",
            )
            return
        player.in_play.remove(in_play)
        self._discard(in_play.card)
        defense_ticks = self._play_defense_sound(
            in_play.card,
            russian_roulette=(
                frame.source.kind == "russian_roulette"
            ),
            source_kind=frame.source.kind,
        )
        remaining = 0
        if decision.kind == "ricochet":
            self._announce_ricochet_saved(player, in_play.card, frame)
        else:
            remaining = max(
                0,
                int(frame.data.get("misses_remaining", 1)) - 1,
            )
            frame.data["misses_remaining"] = remaining
            self._announce_shot_response(
                player,
                in_play.card,
                frame,
                remaining=remaining,
            )
        drawn: list[BangCard] = []
        if in_play.card.kind == cards.BIBLE:
            drawn = self._draw_cards(player, 1)
        self.decision = None
        if decision.kind == "ricochet":
            self._pop_effect()
        else:
            response_ids = frame.data.get("response_hand_ids")
            if isinstance(response_ids, list):
                response_ids.extend(
                    drawn_card.id
                    for drawn_card in drawn
                    if self._card_can_miss(player, drawn_card)
                )
            frame.stage = "response" if remaining else "done"
            if not remaining:
                self._complete_shot(frame)
        self._stagger_effect_audio(
            defense_ticks,
            wait_ratio=game_audio.WAIT_RATIO_REACTION,
        )
        self._continue_effects()

    def _resolve_item_decision(
        self,
        player: BangPlayer,
        item_id: str,
    ) -> None:
        decision = self.decision
        if not decision:
            return
        if decision.kind == "barrel":
            frame = self._top_effect()
            self.decision = None
            if item_id == "use_barrel":
                frame.data["barrels_remaining"] = max(
                    0,
                    int(frame.data.get("barrels_remaining", 1)) - 1,
                )
                frame.stage = "barrel_draw"
            else:
                frame.data["barrels_remaining"] = 0
                frame.stage = "response"
            self._continue_effects()
            return
        if decision.kind in {"missed", "indians"} and item_id == "take_hit":
            self.decision = None
            frame = self._top_effect()
            if frame.kind == "shot":
                frame.stage = "damage"
            else:
                target_id = decision.player_id
                frame.stage = "waiting"
                self._push_effect(
                    BangEffect(
                        kind="damage",
                        target_id=target_id,
                        amount=1,
                        source=frame.source,
                    )
                )
            self._continue_effects()
            return
        if decision.kind == "ricochet" and item_id == "lose_in_play":
            self.decision = None
            self._top_effect().stage = "discard"
            self._continue_effects()
            return
        if decision.kind == "duel" and item_id == "lose_duel":
            frame = self._top_effect()
            loser_id = decision.player_id
            winner_id = (
                frame.actor_id
                if loser_id == frame.target_id
                else frame.target_id
            )
            winner = self.get_player_by_id(winner_id)
            self.decision = None
            self._pop_effect()
            self._push_effect(
                BangEffect(
                    kind="damage",
                    target_id=loser_id,
                    amount=1,
                    source=frame.source,
                )
            )
            if (
                isinstance(winner, BangPlayer)
                and self._player_in_play(winner)
                and frame.data.get("last_shot_player_id") != winner.id
            ):
                attack_ticks = self._play_attack_sound(
                    winner,
                    "duel_resolution",
                )
                self._stagger_effect_audio(
                    attack_ticks,
                    wait_ratio=game_audio.WAIT_RATIO_GUNSHOT,
                )
            self._continue_effects()
            return
        if decision.kind == "lethal_recovery":
            if item_id == "use_sid":
                error = self._is_sid_enabled(player)
                if error:
                    self._speak_action_disabled_reason(player, error)
                    return
                self.decision = None
                self._start_sid_intent(player, lethal_recovery=True)
                return
            if item_id == "accept_death":
                self.decision = None
                frame = self._top_effect()
                if frame.kind == "damage":
                    frame.stage = "eliminate"
                self._continue_effects()
                return
        if decision.kind == "general_store" and item_id.startswith("store_"):
            card_id = self._card_id_from_action(item_id)
            card = next(
                (
                    held
                    for held in self.general_store_cards
                    if held.id == card_id
                ),
                None,
            )
            if card:
                self.general_store_cards.remove(card)
                player.hand.append(card)
                player.hand[:] = sort_cards(player.hand)
                self._play_card_draw_sound()
                self.broadcast_personal_l(
                    player,
                    "bang-you-take-general-store-card",
                    "bang-player-takes-general-store-card",
                    buffer="game",
                    card=lambda locale: card_label(card, locale),
                )
            self.decision = None
            self._top_effect().index += 1
            self._continue_effects()
            return
        if decision.kind == "target_card":
            self._resolve_target_card_item(player, decision, item_id)
            return
        if decision.kind == "vulture":
            self._resolve_vulture_item(player, decision, item_id)
            return
        if decision.kind == "elimination_discard":
            if item_id == "finish_elimination_discard":
                self._discard_remaining_elimination_cards(player)
                return
            if item_id.startswith("in_play_"):
                found = self._in_play_by_id(
                    self._card_id_from_action(item_id)
                )
                if found and found[0].id == player.id:
                    owner, in_play = found
                    owner.in_play.remove(in_play)
                    self._discard(in_play.card)
                    self._announce_elimination_discard_card(
                        player,
                        in_play.card,
                    )
                    self._announce_colt_after_weapon_loss(
                        owner,
                        in_play.card,
                    )
                    self._advance_elimination_discard(player)
            return
        if decision.kind == "draw_check" and item_id.startswith("draw_result_"):
            index = self._card_id_from_action(item_id)
            frame = self._top_effect()
            frame.data["draw_choice"] = index
            frame.data["draw_ready"] = True
            self.decision = None
            self._continue_effects()
            return
        self._resolve_turn_choice_item(player, decision, item_id)

    def _resolve_player_decision(
        self,
        player: BangPlayer,
        target: BangPlayer,
    ) -> None:
        decision = self.decision
        if not decision:
            return
        self._resolve_turn_player_choice(player, target, decision)

    def _resolve_target_card_item(
        self,
        actor: BangPlayer,
        decision: BangDecision,
        item_id: str,
    ) -> None:
        target = self.get_player_by_id(str(decision.data.get("target_id", "")))
        if not isinstance(target, BangPlayer):
            self.decision = None
            self._continue_effects()
            return
        chosen: BangCard | None = None
        in_play: BangInPlayCard | None = None
        if item_id == "random_hand" and target.hand:
            chosen = random.choice(target.hand)  # nosec B311 - game randomness
            target.hand.remove(chosen)
        elif item_id.startswith("in_play_"):
            found = self._in_play_by_id(self._card_id_from_action(item_id))
            if found and found[0].id == target.id:
                _, in_play = found
                target.in_play.remove(in_play)
                chosen = in_play.card
        if chosen:
            mode = str(decision.data.get("mode", "discard"))
            if mode == "steal":
                actor.hand.append(chosen)
                actor.hand[:] = sort_cards(actor.hand)
                self._play_card_draw_sound()
                self._announce_card_transfer(
                    actor,
                    target,
                    chosen,
                    public=in_play is not None,
                )
            else:
                self._discard(chosen)
                self._announce_forced_discard(
                    actor,
                    target,
                    chosen,
                    in_play is not None,
                )
            if in_play:
                self._announce_colt_after_weapon_loss(target, chosen)
        self.decision = None
        self._pop_effect()
        self._continue_effects()

    def _resolve_vulture_item(
        self,
        collector: BangPlayer,
        decision: BangDecision,
        item_id: str,
    ) -> None:
        victim = self.get_player_by_id(str(decision.data.get("victim_id", "")))
        if not isinstance(victim, BangPlayer):
            self.decision = None
            self._continue_effects()
            return
        chosen: BangCard | None = None
        if item_id == "random_hand" and victim.hand:
            chosen = random.choice(victim.hand)  # nosec B311
            victim.hand.remove(chosen)
        elif item_id.startswith("in_play_"):
            found = self._in_play_by_id(self._card_id_from_action(item_id))
            if found and found[0].id == victim.id:
                owner, in_play = found
                owner.in_play.remove(in_play)
                chosen = in_play.card
        if chosen:
            collector.hand.append(chosen)
            collector.hand[:] = sort_cards(collector.hand)
            self._play_card_draw_sound()
            self._announce_vulture_transfer(
                collector,
                victim,
                chosen,
                public=item_id.startswith("in_play_"),
            )
        self.decision = None
        self._continue_effects()

    def _draw_check_result(
        self,
        frame: BangEffect,
        player: BangPlayer,
        *,
        purpose: str,
        suit: str,
        minimum_rank: str = "",
        maximum_rank: str = "",
    ) -> bool | None:
        if not frame.data.get("draw_started"):
            count = 2 if self._has_ability(player, "lucky_duke") else 1
            self.revealed_cards = [
                card for _ in range(count) if (card := self._draw_one())
            ]
            frame.data["draw_started"] = True
            frame.data["draw_purpose"] = purpose
            if not self.revealed_cards:
                frame.data["draw_ready"] = True
                frame.data["draw_choice"] = 0
            elif count == 2:
                self._announce_draw_check(player, self.revealed_cards)
                self.decision = BangDecision(
                    kind="draw_check",
                    player_id=player.id,
                    prompt_key="bang-prompt-lucky-duke",
                    item_ids=[
                        f"draw_result_{index}"
                        for index in range(len(self.revealed_cards))
                    ],
                    data={"purpose": purpose},
                )
                self._focus_decision(player)
                return None
            else:
                frame.data["draw_ready"] = True
                frame.data["draw_choice"] = 0
                self._announce_draw_check(player, self.revealed_cards)
        if not frame.data.get("draw_ready"):
            return None
        selected_index = int(frame.data.get("draw_choice", 0))
        selected = (
            self.revealed_cards[selected_index]
            if 0 <= selected_index < len(self.revealed_cards)
            else None
        )
        result = False
        if selected:
            result = self._effective_suit(selected) == suit
            if result and minimum_rank:
                rank = cards.RANK_ORDER.get(selected.rank, -1)
                result = rank >= cards.RANK_ORDER.get(minimum_rank, 99)
            if result and maximum_rank:
                rank = cards.RANK_ORDER.get(selected.rank, 99)
                result = rank <= cards.RANK_ORDER.get(maximum_rank, -1)
        for revealed in self.revealed_cards:
            self._discard(revealed)
        self.revealed_cards.clear()
        for key in (
            "draw_started",
            "draw_purpose",
            "draw_ready",
            "draw_choice",
        ):
            frame.data.pop(key, None)
        return result

    def _apply_survived_damage_triggers(
        self,
        target: BangPlayer,
        frame: BangEffect,
    ) -> None:
        if self._has_ability(target, "bart_cassidy"):
            self._draw_cards(target, frame.amount)
        if (
            self._has_ability(target, "el_gringo")
            and frame.source.player_id
            and frame.source.player_id != target.id
        ):
            source_player = self.get_player_by_id(frame.source.player_id)
            if isinstance(source_player, BangPlayer):
                for _ in range(frame.amount):
                    if not source_player.hand:
                        break
                    stolen = random.choice(source_player.hand)  # nosec B311
                    source_player.hand.remove(stolen)
                    target.hand.append(stolen)
                    self._play_card_draw_sound()
                    self._announce_card_transfer(target, source_player, stolen)
                target.hand[:] = sort_cards(target.hand)

    def _vulture_collectors(self, victim: BangPlayer) -> list[BangPlayer]:
        candidates = [
            player
            for player in self.players_in_play
            if player.id != victim.id and self._has_ability(player, "vulture_sam")
        ]
        return sorted(
            candidates,
            key=lambda player: self._clockwise_steps(victim, player),
        )

    def _apply_elimination_triggers(
        self,
        victim: BangPlayer,
        source: DamageSource,
    ) -> None:
        for player in self.players_in_play:
            if player.id == victim.id:
                continue
            if self._has_ability(player, "greg_digger"):
                self._heal(player, 2)
            if self._has_ability(player, "herb_hunter"):
                self._draw_cards(player, 2)

        killer = self.get_player_by_id(source.player_id)
        personal_kill = (
            isinstance(killer, BangPlayer)
            and killer.id != victim.id
            and self._player_in_play(killer)
        )
        if len(self.seated_players) == 3:
            if personal_kill:
                if self._three_player_goal_hit(killer, victim):
                    self._end_game([killer], killer.role)
                    return
                self._draw_cards(killer, 3)
            self.three_player_last_standing = True
        else:
            if personal_kill and victim.role == ROLE_OUTLAW:
                self._draw_cards(killer, 3)
                self.broadcast_personal_l(
                    killer,
                    "bang-you-claim-outlaw-reward",
                    "bang-player-claims-outlaw-reward",
                    buffer="game",
                )
            if (
                personal_kill
                and killer.role == ROLE_SHERIFF
                and victim.role == ROLE_DEPUTY
            ):
                self._discard_all_cards(killer)
                self.broadcast_personal_l(
                    killer,
                    "bang-you-suffer-sheriff-penalty",
                    "bang-player-suffers-sheriff-penalty",
                    buffer="game",
                )
        self._check_victory()
        if (
            self.game_active
            and not self.final_showdown_music_started
            and len(self.players_in_play) <= 2
        ):
            self.final_showdown_music_started = True
            self.play_music(game_audio.SOUND_MUSIC_FINAL_SHOWDOWN)

    def _three_player_goal_hit(
        self,
        killer: BangPlayer,
        victim: BangPlayer,
    ) -> bool:
        target_role = {
            ROLE_DEPUTY: ROLE_RENEGADE,
            ROLE_RENEGADE: ROLE_OUTLAW,
            ROLE_OUTLAW: ROLE_DEPUTY,
        }.get(killer.role)
        return not self.three_player_last_standing and victim.role == target_role

    def _check_victory(self) -> None:
        in_play = self.players_in_play
        if len(self.seated_players) == 3:
            if self.three_player_last_standing and len(in_play) <= 1:
                self._end_game(in_play, in_play[0].role if in_play else "")
            return
        sheriff = next(
            (
                player
                for player in self.seated_players
                if player.role == ROLE_SHERIFF
            ),
            None,
        )
        if sheriff and sheriff.eliminated and not sheriff.ghost_active:
            if len(in_play) == 1 and in_play[0].role == ROLE_RENEGADE:
                self._end_game([in_play[0]], ROLE_RENEGADE)
            else:
                winners = [
                    player
                    for player in self.seated_players
                    if player.role == ROLE_OUTLAW
                ]
                self._end_game(winners, ROLE_OUTLAW)
            return
        enemies = [
            player
            for player in in_play
            if player.role in {ROLE_OUTLAW, ROLE_RENEGADE}
        ]
        if not enemies:
            winners = [
                player
                for player in self.seated_players
                if player.role in {ROLE_SHERIFF, ROLE_DEPUTY}
            ]
            self._end_game(winners, ROLE_SHERIFF)

    def _end_game(
        self,
        winners: list[BangPlayer],
        side: str,
    ) -> None:
        if not self.game_active:
            return
        self.winner_ids = [winner.id for winner in winners]
        self.winning_side = side
        self.phase = PHASE_GAME_OVER
        self.effect_stack.clear()
        self.decision = None
        self.play_intent = None
        if self.resolving_card:
            self._discard(self.resolving_card.card)
            self.resolving_card = None
        pending_elimination_falls = [
            scheduled
            for scheduled in self.scheduled_sounds
            if len(scheduled) > 1
            and scheduled[1] in game_audio.SOUND_ELIMINATION_FALLS
        ]
        self.clear_scheduled_sounds()
        self.scheduled_sounds.extend(pending_elimination_falls)
        self.cancel_all_sequences()
        self.play_sound(game_audio.SOUND_WIN)
        winner_names = [winner.name for winner in winners]
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                if listener.id in self.winner_ids:
                    key = "bang-you-win-game"
                elif listener.is_spectator:
                    key = "bang-game-over"
                else:
                    key = "bang-you-lose-game"
                user.speak_l(
                    key,
                    buffer="game",
                    side=self._role_name(side, user.locale),
                    winners=Localization.format_list_and(
                        user.locale,
                        winner_names,
                    ),
                )
        self.finish_game()

    def _discard_all_cards(self, player: BangPlayer) -> None:
        for card in list(player.hand):
            player.hand.remove(card)
            self._discard(card)
        for in_play in list(player.in_play):
            player.in_play.remove(in_play)
            self._discard(in_play.card)
            self._announce_colt_after_weapon_loss(player, in_play.card)

    def _announce_elimination_discard_card(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> None:
        self.broadcast_personal_l(
            player,
            "bang-you-order-elimination-card",
            "bang-player-orders-elimination-card",
            buffer="game",
            card=lambda locale: card_label(card, locale),
        )

    def _discard_next_elimination_card(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> None:
        decision = self.decision
        if (
            not decision
            or decision.kind != "elimination_discard"
            or card.id not in decision.card_ids
            or card not in player.hand
        ):
            return
        player.hand.remove(card)
        self._discard(card)
        self._announce_elimination_discard_card(player, card)
        self._advance_elimination_discard(player)

    def _advance_elimination_discard(self, player: BangPlayer) -> None:
        decision = self.decision
        if not decision or decision.kind != "elimination_discard":
            return
        decision.card_ids = [card.id for card in player.hand]
        decision.item_ids = [
            f"in_play_{in_play.card.id}" for in_play in player.in_play
        ]
        if not decision.card_ids and not decision.item_ids:
            self.decision = None
            self._continue_effects()
            return
        decision.item_ids.append("finish_elimination_discard")
        decision.selected_card_ids.clear()
        self.refresh_menus(player)
        if decision.card_ids:
            focus = f"play_card_{decision.card_ids[0]}"
        else:
            focus = f"choice_{decision.item_ids[0]}"
        self.request_menu_focus(player, focus)
        self._pace_bot(player, choice=True)

    def _discard_remaining_elimination_cards(
        self,
        player: BangPlayer,
    ) -> None:
        decision = self.decision
        if not decision or decision.kind != "elimination_discard":
            return
        discarded: list[BangCard] = []
        for card in list(player.hand):
            player.hand.remove(card)
            self._discard(card)
            discarded.append(card)
        for in_play in list(player.in_play):
            player.in_play.remove(in_play)
            self._discard(in_play.card)
            discarded.append(in_play.card)
            self._announce_colt_after_weapon_loss(player, in_play.card)
        if discarded:
            self.broadcast_personal_l(
                player,
                "bang-you-finish-elimination-discard",
                "bang-player-finishes-elimination-discard",
                buffer="game",
                cards=lambda locale: Localization.format_list_and(
                    locale,
                    [card_label(card, locale) for card in discarded],
                ),
            )
        self.decision = None
        self._continue_effects()

    def _record_molly_response(
        self,
        player: BangPlayer,
        card: BangCard,
        *,
        defer: bool,
    ) -> None:
        if not self._has_ability(player, "molly_stark"):
            return
        if self.current_player is player:
            return
        if card.kind not in {cards.MISSED, cards.BEER, cards.BANG}:
            return
        if defer:
            player.molly_deferred_draws += 1
        else:
            self._draw_cards(player, 1)

    def _resolve_deferred_character_draws(self) -> None:
        for player in self.players_in_play:
            if player.molly_deferred_draws:
                count = player.molly_deferred_draws
                player.molly_deferred_draws = 0
                self._draw_cards(player, count)
            if self._has_ability(player, "suzy_lafayette") and not player.hand:
                self._draw_cards(player, 1)

    # ------------------------------------------------------------------
    # Start turn, events, draw phase, and discard phase
    # ------------------------------------------------------------------

    def _reset_turn_counters(self, player: BangPlayer) -> None:
        player.bangs_played = 0
        player.doc_holyday_used = 0
        player.jose_delgado_uses = 0
        player.uncle_will_used = 0
        player.law_card_id = 0
        player.handcuffs_suit = ""
        player.abandoned_mine_draw_from_discard = False

    def _begin_turn(self) -> None:
        current = self.current_player
        if not isinstance(current, BangPlayer):
            return
        self.phase = PHASE_START_TURN
        self.turn_serial += 1
        self._reset_turn_counters(current)
        if current.character == "vera_custer":
            current.copied_character = ""
        self._push_effect(
            BangEffect(
                kind="turn_start",
                actor_id=current.id,
            )
        )
        self._continue_effects()

    def _event_anchor(self) -> BangPlayer | None:
        anchor_role = (
            ROLE_DEPUTY
            if len(self.seated_players) == 3
            else ROLE_SHERIFF
        )
        return next(
            (
                player
                for player in self.seated_players
                if player.role == anchor_role
            ),
            None,
        )

    def _continue_turn_start(self, frame: BangEffect) -> None:
        player = self.get_player_by_id(frame.actor_id)
        if not isinstance(player, BangPlayer):
            self._pop_effect()
            return
        if frame.stage == "start":
            event_anchor = self._event_anchor()
            if event_anchor and player.id == event_anchor.id:
                reveal_event = (
                    self.sheriff_turns_started > 0
                    and bool(self.event_deck)
                )
                self.sheriff_turns_started += 1
                if reveal_event:
                    revealed = self.event_deck.pop(0)
                    self.current_event = revealed
                    self.turn_direction = -1 if revealed == "gold_rush" else 1
                    frame.stage = "after_reveal"
                    self._announce_event_revealed(revealed)
                    if revealed == "russian_roulette":
                        anchor = self._event_anchor()
                        order = (
                            [
                                anchor,
                                *self._clockwise_after(
                                    anchor,
                                    exclude_actor=True,
                                ),
                            ]
                            if anchor and self._player_in_play(anchor)
                            else []
                        )
                        self.start_sequence(
                            self._next_audio_sequence_id(
                                "russian_roulette"
                            ),
                            [
                                SequenceBeat.after_audio(
                                    game_audio.sound_ticks(
                                        game_audio.SOUND_ROULETTE_LOAD
                                    ),
                                    wait_ratio=game_audio.WAIT_RATIO_FULL_CUE,
                                    ops=[
                                        SequenceOperation.sound_op(
                                            game_audio.SOUND_ROULETTE_LOAD
                                        ),
                                    ],
                                ),
                                SequenceBeat.after_audio(
                                    game_audio.sound_ticks(
                                        game_audio.SOUND_ROULETTE_SPIN
                                    ),
                                    wait_ratio=game_audio.WAIT_RATIO_FULL_CUE,
                                    ops=[
                                        SequenceOperation.sound_op(
                                            game_audio.SOUND_ROULETTE_SPIN
                                        ),
                                    ],
                                ),
                                SequenceBeat.after_audio(
                                    game_audio.sound_ticks(
                                        game_audio.SOUND_ROULETTE_COCK
                                    ),
                                    wait_ratio=game_audio.WAIT_RATIO_FULL_CUE,
                                    ops=[
                                        SequenceOperation.sound_op(
                                            game_audio.SOUND_ROULETTE_COCK
                                        ),
                                    ],
                                ),
                                SequenceBeat(
                                    ops=[
                                        SequenceOperation.callback_op(
                                            "start_russian_roulette",
                                            {
                                                "player_ids": [
                                                    target.id
                                                    for target in order
                                                ]
                                            },
                                        )
                                    ]
                                ),
                            ],
                            tag="bang_event",
                            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                            pause_bots=True,
                        )
                        return
                    if revealed == "the_daltons":
                        eligible = [
                            seated.id
                            for seated in self.players_in_play
                            if any(
                                in_play.card.border == cards.BLUE
                                for in_play in seated.in_play
                            )
                        ]
                        if eligible:
                            self._push_effect(
                                BangEffect(
                                    kind="daltons",
                                    player_ids=eligible,
                                )
                            )
                            return
                    elif revealed == "the_doctor":
                        living = self.players_in_play
                        if living:
                            minimum = min(target.life for target in living)
                            for target in living:
                                if target.life == minimum:
                                    self._heal(target, 1)
            frame.stage = "event_start"
            return
        if frame.stage == "after_reveal":
            frame.stage = "event_start"
            return
        if frame.stage == "event_start":
            frame.stage = "after_event_start"
            if self.current_event == HIGH_NOON and self._player_in_play(player):
                self._push_effect(
                    BangEffect(
                        kind="damage",
                        target_id=player.id,
                        amount=1,
                        source=DamageSource(
                            kind="high_noon",
                            card_kind=HIGH_NOON,
                        ),
                    )
                )
                return
            if (
                self.current_event == FISTFUL_OF_CARDS
                and self._player_in_play(player)
            ):
                count = len(player.hand)
                if count:
                    self._push_effect(
                        BangEffect(
                            kind="fistful",
                            target_id=player.id,
                            amount=count,
                        )
                    )
                    return
            if (
                self.current_event == "blood_brothers"
                and self._player_in_play(player)
                and player.life > 1
            ):
                injured_targets = [
                    target.id
                    for target in self.players_in_play
                    if target.id != player.id and target.life < target.max_life
                ]
                if injured_targets:
                    self.decision = BangDecision(
                        kind="blood_brothers",
                        player_id=player.id,
                        prompt_key="bang-prompt-blood-brothers",
                        player_ids=injured_targets,
                        item_ids=["skip_blood_brothers"],
                    )
                    self._focus_decision(player)
                    return
            if (
                self.current_event == "new_identity"
                and self._player_in_play(player)
                and player.alternate_character
            ):
                self.decision = BangDecision(
                    kind="new_identity",
                    player_id=player.id,
                    prompt_key="bang-prompt-new-identity",
                    item_ids=["keep_identity", "change_identity"],
                )
                self._focus_decision(player)
                return
            return
        if frame.stage == "after_event_start":
            if not self._player_in_play(player):
                if (
                    self.current_event == "dead_man"
                    and not self.dead_man_used
                    and player.id == self.first_eliminated_id
                ):
                    self.dead_man_used = True
                    player.eliminated = False
                    player.role_revealed = True
                    player.life = 2
                    player.hand.clear()
                    player.in_play.clear()
                    self._draw_cards(player, 2)
                    self.broadcast_personal_l(
                        player,
                        "bang-you-return-dead-man",
                        "bang-dead-man-returns",
                        buffer="game",
                    )
                elif self.current_event == "ghost_town":
                    player.ghost_active = True
                    player.life = 0
                    player.hand.clear()
                    player.in_play.clear()
                    self.broadcast_personal_l(
                        player,
                        "bang-you-return-ghost",
                        "bang-ghost-returns",
                        buffer="game",
                    )
                else:
                    self._pop_effect()
                    self._advance_to_next_eligible()
                    return
            frame.stage = "dynamite"
            return
        if frame.stage == "dynamite":
            if not self._in_play_effects_active(player):
                frame.stage = "jail"
                return
            dynamite = next(
                (
                    in_play
                    for in_play in player.in_play
                    if in_play.card.kind == cards.DYNAMITE
                ),
                None,
            )
            if not dynamite:
                frame.stage = "jail"
                return
            frame.data["dynamite_id"] = dynamite.card.id
            frame.stage = "dynamite_check"
            return
        if frame.stage == "dynamite_check":
            result = self._draw_check_result(
                frame,
                player,
                purpose="dynamite",
                suit=cards.SPADES,
                minimum_rank="2",
                maximum_rank="9",
            )
            if result is None:
                return
            found = self._in_play_by_id(int(frame.data.pop("dynamite_id", 0)))
            if not found:
                frame.stage = "jail"
                return
            owner, dynamite = found
            if result:
                frame.stage = "after_dynamite"
                self.start_sequence(
                    self._next_audio_sequence_id("dynamite_explosion"),
                    [
                        SequenceBeat.after_audio(
                            game_audio.sound_ticks(
                                game_audio.SOUND_DYNAMITE_EXPLOSION
                            ),
                            wait_ratio=game_audio.WAIT_RATIO_LONG_EFFECT,
                            ops=[
                                SequenceOperation.sound_op(
                                    game_audio.SOUND_DYNAMITE_EXPLOSION
                                ),
                            ],
                        ),
                        SequenceBeat.after_audio(
                            game_audio.sound_ticks(
                                game_audio.SOUND_DYNAMITE_AFTERMATH
                            ),
                            wait_ratio=game_audio.WAIT_RATIO_LONG_EFFECT,
                            ops=[
                                SequenceOperation.sound_op(
                                    game_audio.SOUND_DYNAMITE_AFTERMATH
                                ),
                                SequenceOperation.callback_op(
                                    "dynamite_explodes",
                                    {
                                        "target_id": player.id,
                                        "card_id": dynamite.card.id,
                                    },
                                ),
                            ],
                        ),
                        SequenceBeat(),
                    ],
                    tag="bang_dynamite",
                    lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                    pause_bots=True,
                    start_immediately=False,
                )
                return
            recipient = self._next_clockwise_without(
                player,
                cards.DYNAMITE,
            )
            if recipient:
                frame.stage = "dynamite_transfer"
                self.start_sequence(
                    self._next_audio_sequence_id("dynamite_transfer"),
                    [
                        SequenceBeat.after_audio(
                            game_audio.sound_ticks(
                                game_audio.SOUND_DYNAMITE_FUSE
                            ),
                            wait_ratio=game_audio.WAIT_RATIO_SHORT_CUE,
                            ops=[
                                SequenceOperation.sound_op(
                                    game_audio.SOUND_DYNAMITE_FUSE
                                ),
                                SequenceOperation.callback_op(
                                    "dynamite_transfers",
                                    {
                                        "owner_id": owner.id,
                                        "recipient_id": recipient.id,
                                        "card_id": dynamite.card.id,
                                    },
                                ),
                            ],
                        ),
                        SequenceBeat(),
                    ],
                    tag="bang_dynamite",
                    lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                    pause_bots=True,
                    start_immediately=False,
                )
                return
            frame.stage = "jail"
            return
        if frame.stage == "after_dynamite":
            if not self._player_in_play(player):
                self._pop_effect()
                if self.game_active:
                    self._advance_to_next_eligible()
                return
            frame.stage = "jail"
            return
        if frame.stage == "jail":
            if not self._in_play_effects_active(player):
                frame.stage = "vera"
                return
            jail = next(
                (
                    in_play
                    for in_play in player.in_play
                    if in_play.card.kind == cards.JAIL
                ),
                None,
            )
            if not jail:
                frame.stage = "vera"
                return
            player.in_play.remove(jail)
            self._discard(jail.card)
            frame.stage = "jail_check"
            return
        if frame.stage == "jail_check":
            result = self._draw_check_result(
                frame,
                player,
                purpose="jail",
                suit=cards.HEARTS,
            )
            if result is None:
                return
            if not result:
                self.broadcast_personal_l(
                    player,
                    "bang-you-skip-jail-turn",
                    "bang-player-skips-jail-turn",
                    buffer="game",
                )
                self._pop_effect()
                self._advance_to_next_eligible()
                return
            self.play_sound(game_audio.SOUND_JAIL_OPEN)
            frame.stage = "vera"
            return
        if frame.stage == "vera":
            if self._has_ability(player, "vera_custer"):
                choices = [
                    target.id
                    for target in self.players_in_play
                    if target.id != player.id
                ]
                if choices:
                    self.decision = BangDecision(
                        kind="vera_custer",
                        player_id=player.id,
                        prompt_key="bang-prompt-vera-custer",
                        player_ids=choices,
                    )
                    self._focus_decision(player)
                    frame.stage = "after_vera"
                    return
            frame.stage = "draw"
            return
        if frame.stage == "after_vera":
            frame.stage = "draw"
            return
        if frame.stage == "draw":
            self._pop_effect()
            self._start_draw_phase(player)

    def _continue_daltons(self, frame: BangEffect) -> None:
        while frame.index < len(frame.player_ids):
            player = self.get_player_by_id(frame.player_ids[frame.index])
            frame.index += 1
            if not isinstance(player, BangPlayer) or not self._player_in_play(player):
                continue
            blue = [
                in_play
                for in_play in player.in_play
                if in_play.card.border == cards.BLUE
            ]
            if not blue:
                continue
            self.decision = BangDecision(
                kind="daltons",
                player_id=player.id,
                prompt_key="bang-prompt-daltons",
                item_ids=[
                    f"in_play_{in_play.card.id}" for in_play in blue
                ],
            )
            self._focus_decision(player)
            return
        self._pop_effect()

    def _continue_russian_roulette(self, frame: BangEffect) -> None:
        if frame.data.get("stop"):
            self._pop_effect()
            return
        if not any(
            isinstance(player := self.get_player_by_id(player_id), BangPlayer)
            and self._player_in_play(player)
            for player_id in frame.player_ids
        ):
            self._pop_effect()
            return
        while True:
            if frame.index >= len(frame.player_ids):
                frame.index = 0
            target = self.get_player_by_id(frame.player_ids[frame.index])
            frame.index += 1
            if not isinstance(target, BangPlayer) or not self._player_in_play(target):
                continue
            self._start_shot(
                None,
                target,
                source_kind="russian_roulette",
                required=1,
                damage_amount=2,
                stop_parent_on_hit=True,
            )
            return

    def _continue_fistful(self, frame: BangEffect) -> None:
        target = self.get_player_by_id(frame.target_id)
        if not isinstance(target, BangPlayer) or not self._player_in_play(target):
            self._pop_effect()
            return
        if frame.index >= frame.amount:
            self._pop_effect()
            return
        frame.index += 1
        self._start_shot(
            None,
            target,
            source_kind="fistful_of_cards",
            required=1,
        )

    def _start_draw_phase(self, player: BangPlayer) -> None:
        self.phase = PHASE_DRAW
        player.abandoned_mine_draw_from_discard = (
            self.current_event == "abandoned_mine"
        )
        self._push_effect(
            BangEffect(
                kind="draw_phase",
                actor_id=player.id,
            )
        )
        self._continue_effects()

    def _continue_draw_phase(self, frame: BangEffect) -> None:
        player = self.get_player_by_id(frame.actor_id)
        if not isinstance(player, BangPlayer) or not self._player_in_play(player):
            self._pop_effect()
            return
        if frame.stage == "start":
            if self.current_event == "hard_liquor":
                self.decision = BangDecision(
                    kind="hard_liquor",
                    player_id=player.id,
                    prompt_key="bang-prompt-hard-liquor",
                    item_ids=["draw_normally", "skip_draw_heal"],
                )
                self._focus_decision(player)
                frame.stage = "after_hard_liquor"
                return
            frame.stage = "choose_draw"
            return
        if frame.stage == "after_hard_liquor":
            if frame.data.get("skip_draw"):
                frame.stage = "after_draw"
            else:
                frame.stage = "choose_draw"
            return
        if frame.stage == "choose_draw":
            if self.current_event == "peyote":
                self.decision = BangDecision(
                    kind="peyote",
                    player_id=player.id,
                    prompt_key="bang-prompt-peyote",
                    item_ids=["guess_red", "guess_black"],
                )
                self._focus_decision(player)
                frame.stage = "peyote"
                return
            if self._has_ability(player, "jesse_jones"):
                choices = [
                    target.id
                    for target in self.players_in_play
                    if target.id != player.id and target.hand
                ]
                self.decision = BangDecision(
                    kind="jesse_jones",
                    player_id=player.id,
                    prompt_key="bang-prompt-jesse-jones",
                    player_ids=choices,
                    item_ids=["draw_normally"],
                )
                self._focus_decision(player)
                frame.stage = "after_special_first"
                return
            if (
                self._has_ability(player, "pedro_ramirez")
                and self.discard_pile
                and not player.abandoned_mine_draw_from_discard
            ):
                self.decision = BangDecision(
                    kind="pedro_ramirez",
                    player_id=player.id,
                    prompt_key="bang-prompt-pedro-ramirez",
                    item_ids=["draw_from_discard", "draw_from_deck"],
                )
                self._focus_decision(player)
                frame.stage = "after_special_first"
                return
            if (
                self._has_ability(player, "pat_brennan")
                and self.current_event != "abandoned_mine"
            ):
                item_ids = ["draw_normally"]
                item_ids.extend(
                    f"in_play_{in_play.card.id}"
                    for owner in self.players_in_play
                    for in_play in owner.in_play
                )
                self.decision = BangDecision(
                    kind="pat_brennan",
                    player_id=player.id,
                    prompt_key="bang-prompt-pat-brennan",
                    item_ids=item_ids,
                )
                self._focus_decision(player)
                frame.stage = "after_special_first"
                return
            frame.stage = "draw_cards"
            return
        if frame.stage == "peyote":
            return
        if frame.stage == "after_special_first":
            if frame.data.get("pat_done"):
                for _ in range(max(0, self._phase_one_draw_modifier())):
                    card = self._draw_phase_one(player, frame)
                    if card:
                        self._give_drawn_card(player, card, frame)
                player.hand[:] = sort_cards(player.hand)
                frame.stage = "after_draw"
                return
            frame.stage = "draw_cards"
            return
        if frame.stage == "draw_cards":
            count = self._phase_one_draw_count(player)
            already = int(frame.data.get("drawn_count", 0))
            if (
                self._has_ability(player, "kit_carlson")
                and not player.abandoned_mine_draw_from_discard
            ):
                inspect = [
                    card
                    for _ in range(3)
                    if (card := self._draw_phase_one(player, frame))
                ]
                self.revealed_cards = inspect
                if count >= len(inspect):
                    for card in inspect:
                        self._give_drawn_card(player, card, frame)
                    self.revealed_cards.clear()
                    frame.stage = "after_draw"
                    return
                if inspect:
                    mode = "kit_keep" if count == 1 else "kit_return"
                    self.decision = BangDecision(
                        kind=mode,
                        player_id=player.id,
                        prompt_key="bang-prompt-kit-carlson",
                        item_ids=[
                            f"kit_{card.id}" for card in inspect
                        ],
                        data={"draw_count": count},
                    )
                    self._focus_decision(player)
                    frame.stage = "after_kit"
                    return
            if self._has_ability(player, "claus_the_saint"):
                self.general_store_cards = [
                    card
                    for _ in range(self._phase_one_cards_to_take(player))
                    if (card := self._draw_phase_one(player, frame))
                ]
                targets = self._clockwise_after(player, exclude_actor=True)
                frame.player_ids = [target.id for target in targets]
                frame.index = 0
                frame.stage = "claus_give"
                return
            for _ in range(max(0, count - already)):
                card = self._draw_phase_one(player, frame)
                if card:
                    self._give_drawn_card(player, card, frame)
            if (
                self._has_ability(player, "black_jack")
                and len(frame.card_ids) >= 2
            ):
                second = self._card_in_hand(player, frame.card_ids[1])
                if second:
                    self.broadcast_personal_l(
                        player,
                        "bang-your-black-jack-reveals",
                        "bang-black-jack-reveals",
                        buffer="game",
                        card=lambda locale: card_label(second, locale),
                    )
                if second and self._effective_suit(second) in {
                    cards.HEARTS,
                    cards.DIAMONDS,
                }:
                    bonus = self._draw_phase_one(player, frame)
                    if bonus:
                        self._give_drawn_card(player, bonus, frame)
                        self.broadcast_personal_l(
                            player,
                            "bang-your-black-jack-succeeds",
                            "bang-player-black-jack-succeeds",
                            buffer="game",
                        )
            player.hand[:] = sort_cards(player.hand)
            frame.stage = "after_draw"
            return
        if frame.stage == "after_kit":
            frame.stage = "after_draw"
            return
        if frame.stage == "claus_give":
            if frame.index < len(frame.player_ids) and self.general_store_cards:
                target = self.get_player_by_id(frame.player_ids[frame.index])
                if isinstance(target, BangPlayer):
                    self.decision = BangDecision(
                        kind="claus_give",
                        player_id=player.id,
                        prompt_key="bang-prompt-claus-give",
                        item_ids=[
                            f"claus_{card.id}"
                            for card in self.general_store_cards
                        ],
                        data={"target_id": target.id},
                    )
                    self._focus_decision(player)
                    return
                frame.index += 1
                return
            for card in self.general_store_cards:
                self._give_drawn_card(player, card, frame)
            self.general_store_cards.clear()
            player.hand[:] = sort_cards(player.hand)
            frame.stage = "after_draw"
            return
        if frame.stage == "after_draw":
            self._announce_phase_draw(player, frame)
            if (
                self.current_event == "law_of_the_west"
                and len(frame.card_ids) >= 2
            ):
                player.law_card_id = frame.card_ids[1]
                law_card = self._card_in_hand(player, player.law_card_id)
                if law_card:
                    self.broadcast_personal_l(
                        player,
                        "bang-your-law-card-revealed",
                        "bang-law-card-revealed",
                        buffer="game",
                        card=lambda locale: card_label(law_card, locale),
                    )
            if self.current_event == "handcuffs":
                self.decision = BangDecision(
                    kind="handcuffs",
                    player_id=player.id,
                    prompt_key="bang-prompt-handcuffs",
                    item_ids=[f"suit_{suit}" for suit in cards.SUITS],
                )
                self._focus_decision(player)
                frame.stage = "after_handcuffs"
                return
            frame.stage = "ranch"
            return
        if frame.stage == "after_handcuffs":
            frame.stage = "ranch"
            return
        if frame.stage == "ranch":
            if self.current_event == "ranch" and player.hand:
                self.decision = BangDecision(
                    kind="ranch",
                    player_id=player.id,
                    prompt_key="bang-prompt-ranch",
                    card_ids=[card.id for card in player.hand],
                    allow_skip=True,
                )
                self._focus_decision(player)
                frame.stage = "after_ranch"
                return
            frame.stage = "done"
            return
        if frame.stage == "after_ranch":
            frame.stage = "done"
            return
        if frame.stage == "done":
            self._pop_effect()
            self.phase = PHASE_PLAY
            self.broadcast_personal_l(
                player,
                "bang-your-play-phase",
                "bang-player-play-phase",
                buffer="game",
            )
            self._resolve_deferred_character_draws()
            self.refresh_menus()
            self._pace_bots()

    def _phase_one_draw_count(self, player: BangPlayer) -> int:
        if player.ghost_active:
            if self._has_ability(player, "bill_noface"):
                base = 5
            elif self._has_ability(player, "pixie_pete"):
                base = 3
            else:
                base = 3
        elif self._has_ability(player, "bill_noface"):
            base = 1 + max(0, player.max_life - player.life)
        elif self._has_ability(player, "pixie_pete"):
            base = 3
        else:
            base = 2
        return max(0, base + self._phase_one_draw_modifier())

    def _phase_one_draw_modifier(self) -> int:
        if self.current_event == "thirst":
            return -1
        if self.current_event == "train_arrival":
            return 1
        return 0

    def _phase_one_cards_to_take(self, player: BangPlayer) -> int:
        if self._has_ability(player, "claus_the_saint"):
            return max(
                0,
                len(self.players_in_play)
                + 1
                + self._phase_one_draw_modifier(),
            )
        return self._phase_one_draw_count(player)

    def _give_drawn_card(
        self,
        player: BangPlayer,
        card: BangCard,
        frame: BangEffect,
    ) -> None:
        player.hand.append(card)
        frame.card_ids.append(card.id)
        frame.data["drawn_count"] = int(frame.data.get("drawn_count", 0)) + 1
        self._play_card_draw_sound()

    def _draw_phase_one(
        self,
        player: BangPlayer,
        frame: BangEffect,
    ) -> BangCard | None:
        if player.abandoned_mine_draw_from_discard and self.discard_pile:
            card = self.discard_pile.pop()
            self._mark_public_draw(frame, card)
            return card
        return self._draw_one()

    @staticmethod
    def _public_draw_card_ids(frame: BangEffect) -> list[int]:
        public_ids = frame.data.get("public_draw_card_ids", [])
        return public_ids if isinstance(public_ids, list) else []

    @classmethod
    def _mark_public_draw(cls, frame: BangEffect, card: BangCard) -> None:
        public_ids = cls._public_draw_card_ids(frame)
        frame.data["public_draw_card_ids"] = public_ids
        if card.id not in public_ids:
            public_ids.append(card.id)

    def _start_discard_phase(self, player: BangPlayer) -> None:
        limit = (
            10
            if self._has_ability(player, "sean_mallory")
            else max(0, player.life)
        )
        excess = max(0, len(player.hand) - limit)
        if excess:
            self.phase = PHASE_DISCARD
            self.decision = BangDecision(
                kind="discard_excess",
                player_id=player.id,
                prompt_key="bang-prompt-discard-excess",
                card_ids=[card.id for card in player.hand],
                required=excess,
            )
            self._focus_decision(player)
            return
        self._finish_turn(player)

    def _select_discard_card(
        self,
        player: BangPlayer,
        card: BangCard,
    ) -> None:
        if not self.decision or self.decision.kind != "discard_excess":
            return
        if self.decision.required == 1:
            self.decision.selected_card_ids = [card.id]
            self._finish_discard_selection(player)
            return
        self._toggle_card_selection(
            player,
            card,
            self.decision.selected_card_ids,
            limit=self.decision.required,
            discard=True,
        )

    def _finish_discard_selection(self, player: BangPlayer) -> None:
        decision = self.decision
        if not decision or decision.kind != "discard_excess":
            return
        selected = decision.selected_card_ids[: decision.required]
        discarded: list[BangCard] = []
        for card_id in selected:
            card = self._card_in_hand(player, card_id)
            if not card:
                continue
            player.hand.remove(card)
            discarded.append(card)
            if player.abandoned_mine_draw_from_discard:
                self.deck.insert(0, card)
                self._play_card_discard_sound()
            else:
                self._discard(card)
        if discarded:
            self.broadcast_personal_l(
                player,
                "bang-you-discard-excess",
                "bang-player-discards-excess",
                buffer="game",
                count=len(discarded),
                cards=lambda locale: Localization.format_list_and(
                    locale,
                    [card_label(card, locale) for card in discarded],
                ),
            )
        self.decision = None
        self._finish_turn(player)

    def _finish_ranch_selection(self, player: BangPlayer) -> None:
        decision = self.decision
        if not decision or decision.kind != "ranch":
            return
        count = 0
        for card_id in list(decision.selected_card_ids):
            card = self._card_in_hand(player, card_id)
            if not card:
                continue
            player.hand.remove(card)
            self._discard(card)
            count += 1
        self.decision = None
        self._draw_cards(player, count)
        self._continue_effects()

    def _finish_turn(self, player: BangPlayer) -> None:
        player.abandoned_mine_draw_from_discard = False
        self.phase = PHASE_RESOLVING
        self._push_effect(
            BangEffect(
                kind="end_turn",
                actor_id=player.id,
            )
        )
        self._continue_effects()

    def _continue_end_turn(self, frame: BangEffect) -> None:
        player = self.get_player_by_id(frame.actor_id)
        if not isinstance(player, BangPlayer):
            self._pop_effect()
            return
        if frame.stage == "start":
            if player.ghost_active:
                frame.stage = "after_ghost"
                self._push_effect(
                    BangEffect(
                        kind="elimination",
                        target_id=player.id,
                        source=DamageSource(kind="ghost_town"),
                    )
                )
                return
            frame.stage = "vendetta"
            return
        if frame.stage == "after_ghost":
            frame.stage = "vendetta"
            return
        if frame.stage == "vendetta":
            if player.vendetta_extra_turn:
                player.vendetta_extra_turn = False
            elif self.current_event == "vendetta":
                result = self._draw_check_result(
                    frame,
                    player,
                    purpose="vendetta",
                    suit=cards.HEARTS,
                )
                if result is None:
                    return
                frame.data["extra_turn"] = result
            frame.stage = "done"
            return
        if frame.stage == "done":
            extra = bool(frame.data.get("extra_turn"))
            self._pop_effect()
            if not self.game_active:
                return
            if extra and self._player_in_play(player):
                player.vendetta_extra_turn = True
                self.broadcast_personal_l(
                    player,
                    "bang-you-gain-extra-turn",
                    "bang-player-gains-extra-turn",
                    buffer="game",
                )
                self.announce_turn()
                self._begin_turn()
            else:
                self._advance_to_next_eligible()

    def _resolve_turn_player_choice(
        self,
        player: BangPlayer,
        target: BangPlayer,
        decision: BangDecision,
    ) -> None:
        frame = self._top_effect()
        if decision.kind == "vera_custer":
            player.copied_character = target.character
            self.decision = None
            for listener in self.players:
                user = self.get_user(listener)
                if user:
                    user.speak_l(
                        (
                            "bang-you-copy-character"
                            if listener.id == player.id
                            else "bang-player-copies-character"
                        ),
                        buffer="game",
                        player=player.name,
                        character=character_name(
                            target.character,
                            user.locale,
                        ),
                    )
            self._continue_effects()
            return
        if decision.kind == "blood_brothers":
            player.life -= 1
            self._heal(target, 1, announce=False)
            self.decision = None
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                if listener.id == player.id:
                    key = "bang-you-give-blood-brother-life"
                elif listener.id == target.id:
                    key = "bang-player-gives-you-blood-brother-life"
                else:
                    key = "bang-blood-brothers-gift"
                user.speak_l(
                    key,
                    buffer="game",
                    player=player.name,
                    target=target.name,
                    life=player.life,
                )
            self._continue_effects()
            return
        if decision.kind == "jesse_jones" and target.hand:
            card = random.choice(target.hand)  # nosec B311
            target.hand.remove(card)
            player.hand.append(card)
            player.hand[:] = sort_cards(player.hand)
            self._play_card_draw_sound()
            frame.card_ids.append(card.id)
            frame.data["drawn_count"] = 1
            self.decision = None
            self._announce_card_transfer(player, target, card)
            self._continue_effects()

    def _resolve_turn_choice_item(
        self,
        player: BangPlayer,
        decision: BangDecision,
        item_id: str,
    ) -> None:
        frame = self._top_effect()
        if decision.kind == "blood_brothers":
            self.decision = None
            self._continue_effects()
            return
        if decision.kind == "new_identity":
            if item_id == "change_identity":
                old = player.character
                player.character = player.alternate_character
                player.alternate_character = old
                player.copied_character = ""
                player.max_life = CHARACTERS[player.character].life + int(
                    player.role == ROLE_SHERIFF
                )
                player.life = min(2, player.max_life)
                self.broadcast_personal_l(
                    player,
                    "bang-you-change-identity",
                    "bang-new-identity-changed",
                    buffer="game",
                    character=lambda locale: character_name(
                        player.character,
                        locale,
                    ),
                )
            self.decision = None
            self._continue_effects()
            return
        if decision.kind == "hard_liquor":
            if item_id == "skip_draw_heal":
                frame.data["skip_draw"] = True
                if not self._heal(player, 1):
                    self.broadcast_personal_l(
                        player,
                        "bang-your-hard-liquor-no-effect",
                        "bang-player-hard-liquor-no-effect",
                        buffer="game",
                    )
            self.decision = None
            self._continue_effects()
            return
        if decision.kind in {"jesse_jones", "pedro_ramirez"}:
            card: BangCard | None = None
            if (
                decision.kind == "pedro_ramirez"
                and item_id == "draw_from_discard"
                and self.discard_pile
            ):
                card = self.discard_pile.pop()
            elif decision.kind == "pedro_ramirez":
                card = self._draw_one()
            else:
                card = self._draw_phase_one(player, frame)
            if card:
                self._give_drawn_card(player, card, frame)
                if (
                    decision.kind == "pedro_ramirez"
                    and item_id == "draw_from_discard"
                ):
                    self._mark_public_draw(frame, card)
            self.decision = None
            self._continue_effects()
            return
        if decision.kind == "pat_brennan":
            if item_id == "draw_normally":
                frame.data["pat_done"] = False
            elif item_id.startswith("in_play_"):
                found = self._in_play_by_id(self._card_id_from_action(item_id))
                if found:
                    owner, in_play = found
                    owner.in_play.remove(in_play)
                    player.hand.append(in_play.card)
                    player.hand[:] = sort_cards(player.hand)
                    self._play_card_draw_sound()
                    frame.card_ids.append(in_play.card.id)
                    frame.data["pat_done"] = True
                    for listener in self.players:
                        user = self.get_user(listener)
                        if user:
                            if listener.id == player.id:
                                key = "bang-you-use-pat"
                            elif listener.id == owner.id:
                                key = "bang-pat-takes-your-card"
                            else:
                                key = "bang-player-uses-pat"
                            user.speak_l(
                                key,
                                buffer="game",
                                player=player.name,
                                owner=owner.name,
                                card=card_label(in_play.card, user.locale),
                            )
                    self._announce_colt_after_weapon_loss(owner, in_play.card)
            self.decision = None
            self._continue_effects()
            return
        if decision.kind in {"kit_keep", "kit_return"}:
            card_id = self._card_id_from_action(item_id)
            selected = next(
                (card for card in self.revealed_cards if card.id == card_id),
                None,
            )
            if selected:
                if decision.kind == "kit_keep":
                    keep = [selected]
                    returned = [
                        card for card in self.revealed_cards if card.id != card_id
                    ]
                else:
                    keep = [
                        card for card in self.revealed_cards if card.id != card_id
                    ]
                    returned = [selected]
                for card in keep:
                    self._give_drawn_card(player, card, frame)
                self.deck = returned + self.deck
                self.revealed_cards.clear()
                player.hand[:] = sort_cards(player.hand)
            self.decision = None
            self._continue_effects()
            return
        if decision.kind == "claus_give":
            card_id = self._card_id_from_action(item_id)
            card = next(
                (
                    held
                    for held in self.general_store_cards
                    if held.id == card_id
                ),
                None,
            )
            target = self.get_player_by_id(
                str(decision.data.get("target_id", ""))
            )
            if card and isinstance(target, BangPlayer):
                self.general_store_cards.remove(card)
                target.hand.append(card)
                target.hand[:] = sort_cards(target.hand)
                self._play_card_draw_sound()
                self._announce_claus_gift(
                    player,
                    target,
                    card,
                    public=card.id in self._public_draw_card_ids(frame),
                )
            frame.index += 1
            self.decision = None
            self._continue_effects()
            return
        if decision.kind == "peyote":
            guessed_red = item_id == "guess_red"
            card = self._draw_one()
            correct = False
            if card:
                red = self._effective_suit(card) in {
                    cards.HEARTS,
                    cards.DIAMONDS,
                }
                correct = red == guessed_red
                self._announce_peyote(player, card, correct)
                if correct:
                    player.hand.append(card)
                    frame.card_ids.append(card.id)
                    player.hand[:] = sort_cards(player.hand)
                    self._play_card_draw_sound()
                else:
                    self._discard(card)
            self.decision = None
            if correct:
                self.decision = BangDecision(
                    kind="peyote",
                    player_id=player.id,
                    prompt_key="bang-prompt-peyote",
                    item_ids=["guess_red", "guess_black"],
                )
                self._focus_decision(player)
            else:
                frame.stage = "after_draw"
                self._continue_effects()
            return
        if decision.kind == "handcuffs" and item_id.startswith("suit_"):
            player.handcuffs_suit = item_id.removeprefix("suit_")
            self.decision = None
            self.broadcast_personal_l(
                player,
                "bang-you-declare-handcuffs",
                "bang-handcuffs-declared",
                buffer="game",
                suit=lambda locale: cards.suit_name(
                    player.handcuffs_suit,
                    locale,
                ),
            )
            self._continue_effects()
            return
        if decision.kind == "daltons" and item_id.startswith("in_play_"):
            found = self._in_play_by_id(self._card_id_from_action(item_id))
            if found and found[0].id == player.id:
                owner, in_play = found
                owner.in_play.remove(in_play)
                self._discard(in_play.card)
                self.broadcast_personal_l(
                    owner,
                    "bang-you-discard-daltons",
                    "bang-player-discards-daltons",
                    buffer="game",
                    card=lambda locale: card_label(in_play.card, locale),
                )
                self._announce_colt_after_weapon_loss(owner, in_play.card)
            self.decision = None
            self._continue_effects()
            return

    def _advance_to_next_eligible(self) -> None:
        if not self.game_active or not self.turn_player_ids:
            return
        for _ in range(len(self.turn_player_ids)):
            self.turn_index = (
                self.turn_index + self.turn_direction
            ) % len(self.turn_player_ids)
            candidate = self.current_player
            if not isinstance(candidate, BangPlayer):
                continue
            if self._player_in_play(candidate):
                self.announce_turn()
                self._begin_turn()
                return
            if (
                self.current_event == "ghost_town"
                or (
                    self.current_event == "dead_man"
                    and not self.dead_man_used
                    and candidate.id == self.first_eliminated_id
                )
            ):
                self.announce_turn()
                self._begin_turn()
                return

    # ------------------------------------------------------------------
    # Card piles, seating, communication, and menu labels
    # ------------------------------------------------------------------

    def _draw_one(self) -> BangCard | None:
        if not self.deck and self.discard_pile:
            self.deck = list(self.discard_pile)
            self.discard_pile.clear()
            random.shuffle(self.deck)
            self.play_sound(self._random_sound(game_audio.SOUND_CARD_SHUFFLE))
            self.broadcast_l("bang-discard-reshuffled", buffer="game")
        if not self.deck:
            return None
        return self.deck.pop(0)

    def _draw_cards(self, player: BangPlayer, count: int) -> list[BangCard]:
        drawn: list[BangCard] = []
        for _ in range(max(0, count)):
            card = self._draw_one()
            if not card:
                break
            player.hand.append(card)
            drawn.append(card)
            self._play_card_draw_sound()
        player.hand[:] = sort_cards(player.hand)
        if drawn:
            self._announce_drawn_cards(player, drawn)
        return drawn

    def _discard(self, card: BangCard) -> None:
        self.discard_pile.append(card)
        self._play_card_discard_sound()

    @staticmethod
    def _can_receive_heal(
        player: BangPlayer,
        *,
        allow_from_zero: bool = False,
    ) -> bool:
        return (
            player.life < player.max_life
            and (
                player.life > 0
                or allow_from_zero
                or player.ghost_active
            )
        )

    def _heal(
        self,
        player: BangPlayer,
        amount: int,
        *,
        allow_from_zero: bool = False,
        actor: BangPlayer | None = None,
        announce: bool = True,
        play_success_sound: bool = True,
    ) -> int:
        if not self._can_receive_heal(
            player,
            allow_from_zero=allow_from_zero,
        ):
            return 0
        old = player.life
        player.life = min(player.max_life, player.life + max(0, amount))
        gained = player.life - old
        if gained and play_success_sound:
            self.play_sound(game_audio.SOUND_HEAL_SUCCESS)
        if gained and announce:
            if isinstance(actor, BangPlayer) and actor.id != player.id:
                self._broadcast_actor_target_l(
                    actor,
                    player,
                    "bang-your-target-heals",
                    "bang-player-heals-you",
                    "bang-player-heals-target",
                    amount=gained,
                    life=player.life,
                )
            else:
                self.broadcast_personal_l(
                    player,
                    "bang-you-heal",
                    "bang-player-heals",
                    buffer="game",
                    amount=gained,
                    life=player.life,
                )
        return gained

    def _announce_heal_card_no_effect(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        card: BangCard,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {
                "player": actor.name,
                "target": target.name,
                "card": card_name(card, user.locale),
            }
            if actor.id == target.id:
                key = (
                    "bang-your-heal-card-no-effect"
                    if listener.id == actor.id
                    else "bang-player-heal-card-no-effect"
                )
            elif listener.id == actor.id:
                key = "bang-your-target-heal-card-no-effect"
            elif listener.id == target.id:
                key = "bang-player-heal-card-no-effect-on-you"
            else:
                key = "bang-player-target-heal-card-no-effect"
            user.speak_l(key, buffer="game", **kwargs)

    def _apply_beer(
        self,
        player: BangPlayer,
        *,
        allow_from_zero: bool = False,
    ) -> None:
        self._play_consumable_sound(cards.BEER)
        if len(self.players_in_play) <= 2:
            self.broadcast_personal_l(
                player,
                "bang-your-beer-no-effect-two-players",
                "bang-player-beer-no-effect-two-players",
                buffer="game",
            )
            return
        old_life = player.life
        amount = 2 if self._has_ability(player, "tequila_joe") else 1
        self._heal(player, amount, allow_from_zero=allow_from_zero)
        if player.life == old_life:
            self.broadcast_personal_l(
                player,
                "bang-your-beer-no-effect-full-life",
                "bang-player-beer-no-effect-full-life",
                buffer="game",
            )

    def _clockwise_steps(
        self,
        start: BangPlayer,
        target: BangPlayer,
    ) -> int:
        ids = list(self.turn_player_ids)
        if start.id not in ids or target.id not in ids:
            return len(ids) + 1
        return (ids.index(target.id) - ids.index(start.id)) % len(ids)

    def _clockwise_after(
        self,
        start: BangPlayer,
        *,
        exclude_actor: bool,
    ) -> list[BangPlayer]:
        candidates = [
            player
            for player in self.players_in_play
            if not exclude_actor or player.id != start.id
        ]
        return sorted(
            candidates,
            key=lambda player: self._clockwise_steps(start, player),
        )

    def _next_clockwise_without(
        self,
        start: BangPlayer,
        card_kind: str,
    ) -> BangPlayer | None:
        for candidate in self._clockwise_after(start, exclude_actor=True):
            if not any(
                in_play.card.kind == card_kind
                for in_play in candidate.in_play
            ):
                return candidate
        if not any(
            in_play.card.kind == card_kind for in_play in start.in_play
        ):
            return start
        return None

    def _in_play_choice_ids(self, mode: str) -> list[str]:
        target_id = ""
        if (
            mode == "ricochet"
            and self.play_intent
            and self.play_intent.kind == "ricochet"
        ):
            target_id = self.play_intent.target_id
        return [
            f"in_play_{in_play.card.id}"
            for owner in self.players_in_play
            if not target_id or owner.id == target_id
            for in_play in owner.in_play
        ]

    def _focus_decision(self, player: BangPlayer) -> None:
        if not self.decision:
            return
        focus = ""
        if (
            self.decision.kind == "elimination_discard"
            and self.decision.card_ids
        ):
            focus = f"play_card_{self.decision.card_ids[0]}"
        elif self.decision.player_ids:
            focus = f"choose_player_{self.decision.player_ids[0]}"
        elif self.decision.card_ids:
            focus = f"play_card_{self.decision.card_ids[0]}"
        else:
            green_ids = self.decision.data.get("green_card_ids")
            if isinstance(green_ids, list) and green_ids:
                focus = f"use_in_play_{green_ids[0]}"
            elif self.decision.item_ids:
                focus = f"choice_{self.decision.item_ids[0]}"
        if focus:
            self.request_menu_focus(player, focus)
        else:
            self.refresh_menus(player)
        self._speak_input_prompt(player)
        self._pace_bot(player, choice=True)

    def _choice_label(
        self,
        player: BangPlayer,
        item_id: str,
        locale: str,
    ) -> str:
        simple = {
            "use_barrel": "bang-choice-use-barrel",
            "skip_barrels": "bang-choice-skip-barrel",
            "take_hit": "bang-choice-take-hit",
            "lose_duel": "bang-choice-lose-duel",
            "lose_in_play": "bang-choice-lose-in-play",
            "accept_death": "bang-choice-accept-death",
            "use_sid": "bang-choice-use-sid",
            "random_hand": "bang-choice-random-hand",
            "skip_blood_brothers": "bang-choice-skip",
            "keep_identity": "bang-choice-keep-identity",
            "change_identity": "bang-choice-change-identity",
            "draw_normally": "bang-choice-draw-normally",
            "skip_draw_heal": "bang-choice-skip-draw-heal",
            "draw_from_deck": "bang-choice-draw-deck",
            "draw_from_discard": "bang-choice-draw-discard",
            "guess_red": "bang-choice-red",
            "guess_black": "bang-choice-black",
            "finish_elimination_discard": (
                "bang-choice-finish-elimination-discard"
            ),
        }
        if item_id in simple:
            return Localization.get(locale, simple[item_id])
        if item_id.startswith("suit_"):
            return cards.suit_name(item_id.removeprefix("suit_"), locale)
        if item_id.startswith(("store_", "claus_", "kit_")):
            card = self._choice_card(item_id)
            return card_label(card, locale) if card else item_id
        if item_id.startswith("draw_result_"):
            card = self._choice_card(item_id)
            if card:
                return card_label(card, locale)
        if item_id.startswith("in_play_"):
            found = self._in_play_by_id(self._card_id_from_action(item_id))
            if found:
                owner, in_play = found
                if (
                    self.decision
                    and self.decision.player_id == player.id
                    and self.decision.kind == "elimination_discard"
                ):
                    return Localization.get(
                        locale,
                        "bang-elimination-discard-next-in-play",
                        card=card_label(in_play.card, locale),
                    )
                return Localization.get(
                    locale,
                    "bang-in-play-choice",
                    player=owner.name,
                    card=card_label(in_play.card, locale),
                )
        return Localization.get(locale, "bang-choice-unavailable")

    def _role_name(self, role: str, locale: str) -> str:
        return Localization.get(locale, f"bang-role-{role.replace('_', '-')}")

    def _announce_event_revealed(self, event_id: str) -> None:
        if not event_id:
            return
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l(
                    "bang-event-revealed",
                    buffer="game",
                    event=event_name(event_id, user.locale),
                )

    def _broadcast_actor_target_l(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        actor_key: str,
        target_key: str,
        public_key: str,
        **kwargs: Any,
    ) -> None:
        """Broadcast one event from actor, target, and observer perspectives."""

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            localized = self._resolve_broadcast_kwargs(user.locale, kwargs)
            localized.update(
                actor=actor.name,
                player=target.name,
                target=target.name,
            )
            if listener.id == actor.id:
                key = actor_key
            elif listener.id == target.id:
                key = target_key
            else:
                key = public_key
            user.speak_l(key, buffer="game", **localized)

    def _announce_sniper_aim(
        self,
        actor: BangPlayer,
        target: BangPlayer,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == actor.id:
                key = "bang-you-aim-sniper"
            elif listener.id == target.id:
                key = "bang-sniper-aims-at-you"
            else:
                key = "bang-player-aims-sniper"
            user.speak_l(
                key,
                buffer="game",
                player=actor.name,
                target=target.name,
            )

    def _announce_card_play(
        self,
        actor: BangPlayer,
        card: BangCard,
        target: BangPlayer | None,
        *,
        as_bang: bool = False,
    ) -> None:
        if card.kind in cards.WEAPONS or card.kind == cards.BANG or as_bang:
            return
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {"card": card_name(card, user.locale)}
            if target:
                kwargs["target"] = target.name
            if listener.id == actor.id:
                key = (
                    "bang-you-play-card-target"
                    if target
                    else "bang-you-play-card"
                )
            elif target and listener.id == target.id:
                key = "bang-player-plays-card-on-you"
                kwargs["player"] = actor.name
            else:
                key = (
                    "bang-player-plays-card-target"
                    if target
                    else "bang-player-plays-card"
                )
                kwargs["player"] = actor.name
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_weapon_equipped(
        self,
        actor: BangPlayer,
        weapon: BangCard,
        replaced: BangCard | None,
    ) -> None:
        disabled = not self._in_play_effects_active(actor)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {
                "player": actor.name,
                "weapon": card_name(weapon, user.locale),
                "range": (
                    self.weapon_range(actor)
                    if disabled
                    else cards.WEAPON_RANGES[weapon.kind]
                ),
                "event": event_name(self.current_event, user.locale),
            }
            if replaced:
                kwargs["old_weapon"] = card_name(replaced, user.locale)
                if disabled:
                    key = (
                        "bang-you-replace-weapon-disabled"
                        if listener.id == actor.id
                        else "bang-player-replaces-weapon-disabled"
                    )
                else:
                    key = (
                        "bang-you-replace-weapon"
                        if listener.id == actor.id
                        else "bang-player-replaces-weapon"
                    )
            else:
                if disabled:
                    key = (
                        "bang-you-equip-weapon-disabled"
                        if listener.id == actor.id
                        else "bang-player-equips-weapon-disabled"
                    )
                else:
                    key = (
                        "bang-you-equip-weapon"
                        if listener.id == actor.id
                        else "bang-player-equips-weapon"
                    )
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_colt_after_weapon_loss(
        self,
        owner: BangPlayer,
        removed: BangCard,
    ) -> None:
        if removed.kind not in cards.WEAPONS or not self._player_in_play(owner):
            return
        self.play_sound(game_audio.SOUND_EQUIP_COLT45)
        self.broadcast_personal_l(
            owner,
            "bang-your-colt-is-current",
            "bang-player-colt-is-current",
            buffer="game",
            weapon=lambda locale: card_name(removed, locale),
        )

    def _announce_shot_response(
        self,
        player: BangPlayer,
        card: BangCard,
        frame: BangEffect,
        *,
        remaining: int,
    ) -> None:
        kwargs: dict[str, Any] = {
            "card": lambda locale: card_label(card, locale),
            "source": lambda locale: self._source_context(frame, locale),
        }
        if remaining:
            kwargs["response"] = lambda locale: Localization.get(
                locale,
                "bang-missed-effect-count",
                count=remaining,
            )
            personal_key = "bang-you-answer-shot"
            actor_key = "bang-your-target-answers-shot"
            public_key = "bang-player-answers-shot"
        else:
            personal_key = "bang-you-avoid-shot"
            actor_key = "bang-your-target-avoids-shot"
            public_key = "bang-player-avoids-shot"
        attacker = self.get_player_by_id(
            frame.source.player_id or frame.actor_id
        )
        if isinstance(attacker, BangPlayer) and attacker.id != player.id:
            self._broadcast_actor_target_l(
                attacker,
                player,
                actor_key,
                personal_key,
                public_key,
                **kwargs,
            )
        else:
            self.broadcast_personal_l(
                player,
                personal_key,
                public_key,
                buffer="game",
                **kwargs,
            )

    def _announce_indians_response(
        self,
        player: BangPlayer,
        card: BangCard,
        frame: BangEffect,
    ) -> None:
        attacker = self.get_player_by_id(frame.actor_id)
        kwargs = {
            "card": lambda locale: card_label(card, locale),
            "source": lambda locale: self._source_context(frame, locale),
        }
        if isinstance(attacker, BangPlayer) and attacker.id != player.id:
            self._broadcast_actor_target_l(
                attacker,
                player,
                "bang-your-target-answers-indians",
                "bang-you-answer-indians",
                "bang-player-answers-indians",
                **kwargs,
            )
        else:
            self.broadcast_personal_l(
                player,
                "bang-you-answer-indians",
                "bang-player-answers-indians",
                buffer="game",
                **kwargs,
            )

    def _announce_duel_response(
        self,
        player: BangPlayer,
        card: BangCard,
        frame: BangEffect,
    ) -> None:
        opponent_id = (
            frame.actor_id
            if player.id == frame.target_id
            else frame.target_id
        )
        opponent = self.get_player_by_id(opponent_id)
        kwargs = {"card": lambda locale: card_label(card, locale)}
        if isinstance(opponent, BangPlayer) and opponent.id != player.id:
            self._broadcast_actor_target_l(
                player,
                opponent,
                "bang-you-answer-duel",
                "bang-your-opponent-answers-duel",
                "bang-player-answers-duel",
                **kwargs,
            )
        else:
            self.broadcast_personal_l(
                player,
                "bang-you-answer-duel",
                "bang-player-answers-duel",
                buffer="game",
                **kwargs,
            )

    def _announce_ricochet_saved(
        self,
        player: BangPlayer,
        response: BangCard | str,
        frame: BangEffect,
    ) -> None:
        found = self._in_play_by_id(frame.card_ids[0]) if frame.card_ids else None
        attacker = self.get_player_by_id(frame.actor_id)
        if not found or not isinstance(attacker, BangPlayer):
            return
        self._broadcast_actor_target_l(
            attacker,
            player,
            "bang-your-target-saves-ricochet-card",
            "bang-you-save-ricochet-card",
            "bang-player-saves-ricochet-card",
            attacker=attacker.name,
            card=lambda locale: card_label(found[1].card, locale),
            response=lambda locale: (
                card_label(response, locale)
                if isinstance(response, BangCard)
                else card_name(response, locale)
            ),
        )

    def _announce_barrel_result(
        self,
        target: BangPlayer,
        frame: BangEffect,
        *,
        succeeded: bool,
    ) -> None:
        keys = (
            (
                "bang-your-target-barrel-succeeds",
                "bang-your-barrel-succeeds",
                "bang-player-barrel-succeeds",
            )
            if succeeded
            else (
                "bang-your-target-barrel-fails",
                "bang-your-barrel-fails",
                "bang-player-barrel-fails",
            )
        )
        attacker = self.get_player_by_id(
            frame.source.player_id or frame.actor_id
        )
        def source(locale: str) -> str:
            return Localization.get(
                locale,
                f"bang-source-{frame.source.kind.replace('_', '-')}",
            )

        def source_context(locale: str) -> str:
            return self._source_context(frame, locale)
        if isinstance(attacker, BangPlayer) and attacker.id != target.id:
            self._broadcast_actor_target_l(
                attacker,
                target,
                *keys,
                source=source,
                source_context=source_context,
            )
            return
        self.broadcast_personal_l(
            target,
            keys[1],
            keys[2],
            buffer="game",
            source=source,
            source_context=source_context,
        )

    def _announce_ricochet_discarded(
        self,
        attacker: BangPlayer,
        target: BangPlayer,
        card: BangCard,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == attacker.id:
                key = "bang-your-ricochet-discards-card"
            elif listener.id == target.id:
                key = "bang-ricochet-discards-your-card"
            else:
                key = "bang-player-ricochet-discards-card"
            user.speak_l(
                key,
                buffer="game",
                attacker=attacker.name,
                target=target.name,
                card=card_label(card, user.locale),
            )

    def _announce_shot(
        self,
        actor: BangPlayer | None,
        target: BangPlayer,
        source_kind: str,
    ) -> None:
        bang_shot = source_kind in {"bang_card", "missed_as_bang"}
        if actor:
            delta = 0
            if target.role_revealed and target.role == ROLE_SHERIFF:
                delta = 2
            elif target.role_revealed and target.role in {
                ROLE_OUTLAW,
                ROLE_RENEGADE,
            }:
                delta = -1
            if delta:
                for observer in self.players_in_play:
                    if observer.is_bot and observer.id != actor.id:
                        observer.bot_role_suspicion[actor.id] = (
                            observer.bot_role_suspicion.get(actor.id, 0)
                            + delta
                        )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            source = Localization.get(
                user.locale,
                f"bang-source-{source_kind.replace('_', '-')}",
            )
            if actor is None:
                user.speak_l(
                    (
                        "bang-event-targets-you"
                        if listener.id == target.id
                        else "bang-event-targets-player"
                    ),
                    buffer="game",
                    player=target.name,
                    source=source,
                )
            elif listener.id == actor.id:
                user.speak_l(
                    (
                        "bang-you-fire-bang"
                        if bang_shot
                        else "bang-you-shoot"
                    ),
                    buffer="game",
                    target=target.name,
                    source=source,
                )
            elif listener.id == target.id:
                user.speak_l(
                    (
                        "bang-bang-fired-at-you"
                        if bang_shot
                        else "bang-you-are-shot"
                    ),
                    buffer="game",
                    player=actor.name,
                    source=source,
                )
            else:
                user.speak_l(
                    (
                        "bang-player-fires-bang"
                        if bang_shot
                        else "bang-player-shoots"
                    ),
                    buffer="game",
                    player=actor.name,
                    target=target.name,
                    source=source,
                )

    def _announce_damage(
        self,
        target: BangPlayer,
        amount: int,
        source: DamageSource,
    ) -> None:
        source_player = self.get_player_by_id(source.player_id)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            source_name = Localization.get(
                user.locale,
                f"bang-source-{source.kind.replace('_', '-')}",
            )
            attributed_source = source_name
            if isinstance(source_player, BangPlayer):
                attributed_source = Localization.get(
                    user.locale,
                    "bang-source-by-player",
                    player=source_player.name,
                    source=source_name,
                )
            if listener.id == target.id:
                user.speak_l(
                    "bang-you-lose-life",
                    buffer="game",
                    amount=amount,
                    life=target.life,
                    source=attributed_source,
                )
            elif (
                isinstance(source_player, BangPlayer)
                and listener.id == source_player.id
            ):
                user.speak_l(
                    "bang-your-attack-costs-life",
                    buffer="game",
                    target=target.name,
                    amount=amount,
                    life=target.life,
                    source=source_name,
                )
            else:
                user.speak_l(
                    "bang-player-loses-life",
                    buffer="game",
                    player=target.name,
                    amount=amount,
                    life=target.life,
                    source=attributed_source,
                )

    def _announce_unaffected(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        source: BangCard | str,
    ) -> None:
        def localized_source(locale: str) -> str:
            if isinstance(source, BangCard):
                return card_name(source, locale)
            return Localization.get(
                locale,
                f"bang-source-{source.replace('_', '-')}",
            )

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {
                "attacker": actor.name,
                "player": target.name,
                "source": localized_source(user.locale),
            }
            if listener.id == target.id:
                key = "bang-you-are-unaffected"
            elif listener.id == actor.id:
                key = "bang-your-card-is-unaffected"
            else:
                key = "bang-player-is-unaffected"
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_draw_check(
        self,
        player: BangPlayer,
        revealed: list[BangCard],
    ) -> None:
        self.broadcast_personal_l(
            player,
            "bang-you-reveal-draw-check",
            "bang-draw-check-reveals",
            buffer="game",
            cards=lambda locale: Localization.format_list_and(
                locale,
                [card_label(card, locale) for card in revealed],
            ),
        )

    def _announce_phase_draw(
        self,
        player: BangPlayer,
        frame: BangEffect,
    ) -> None:
        drawn = [
            card
            for card_id in frame.card_ids
            if (card := self._card_in_hand(player, card_id))
        ]
        if not drawn:
            return
        self._announce_drawn_cards(
            player,
            drawn,
            public_card_ids=self._public_draw_card_ids(frame),
        )

    def _announce_drawn_cards(
        self,
        player: BangPlayer,
        drawn: list[BangCard],
        *,
        public_card_ids: Sequence[int] = (),
    ) -> None:
        public_id_set = set(public_card_ids)
        public_cards = [card for card in drawn if card.id in public_id_set]
        hidden_count = len(drawn) - len(public_cards)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == player.id:
                user.speak_l(
                    "bang-you-draw-cards",
                    buffer="game",
                    count=len(drawn),
                    cards=Localization.format_list_and(
                        user.locale,
                        [card_label(card, user.locale) for card in drawn],
                    ),
                )
                continue
            if public_cards:
                user.speak_l(
                    "bang-player-draws-public-cards",
                    buffer="game",
                    player=player.name,
                    count=len(public_cards),
                    cards=Localization.format_list_and(
                        user.locale,
                        [
                            card_label(card, user.locale)
                            for card in public_cards
                        ],
                    ),
                )
            if hidden_count:
                user.speak_l(
                    "bang-player-draws-cards",
                    buffer="game",
                    player=player.name,
                    count=hidden_count,
                )

    def _announce_card_transfer(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        card: BangCard,
        *,
        public: bool = False,
    ) -> None:
        actor_user = self.get_user(actor)
        if actor_user:
            actor_user.speak_l(
                "bang-you-steal-card",
                buffer="game",
                target=target.name,
                card=card_label(card, actor_user.locale),
            )
        target_user = self.get_user(target)
        if target_user:
            target_user.speak_l(
                "bang-player-steals-your-card",
                buffer="game",
                player=actor.name,
                card=card_label(card, target_user.locale),
            )
        for observer in self.players:
            if observer.id in {actor.id, target.id}:
                continue
            user = self.get_user(observer)
            if user:
                if public:
                    user.speak_l(
                        "bang-player-steals-public-card",
                        buffer="game",
                        player=actor.name,
                        target=target.name,
                        card=card_label(card, user.locale),
                    )
                else:
                    user.speak_l(
                        "bang-player-steals-hidden-card",
                        buffer="game",
                        player=actor.name,
                        target=target.name,
                    )

    def _announce_forced_discard(
        self,
        actor: BangPlayer,
        target: BangPlayer,
        card: BangCard,
        public: bool,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs: dict[str, Any] = {
                "player": actor.name,
                "target": target.name,
            }
            if listener.id == actor.id:
                kwargs["card"] = card_label(card, user.locale)
                key = "bang-you-force-card-discard"
            elif listener.id == target.id:
                kwargs["card"] = card_label(card, user.locale)
                key = "bang-player-forces-your-card-discard"
            elif public:
                kwargs["card"] = card_label(card, user.locale)
                key = "bang-player-forces-card-discard"
            else:
                key = "bang-player-forces-hidden-discard"
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_vulture_transfer(
        self,
        collector: BangPlayer,
        victim: BangPlayer,
        card: BangCard,
        *,
        public: bool,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs: dict[str, Any] = {
                "player": collector.name,
                "target": victim.name,
            }
            if listener.id == collector.id:
                key = "bang-you-collect-vulture-card"
                kwargs["card"] = card_label(card, user.locale)
            elif listener.id == victim.id:
                key = "bang-player-collects-your-vulture-card"
                kwargs["card"] = card_label(card, user.locale)
            elif public:
                key = "bang-player-collects-vulture-card"
                kwargs["card"] = card_label(card, user.locale)
            else:
                key = "bang-player-collects-hidden-vulture-card"
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_claus_gift(
        self,
        claus: BangPlayer,
        target: BangPlayer,
        card: BangCard,
        *,
        public: bool,
    ) -> None:
        target_user = self.get_user(target)
        if target_user:
            target_user.speak_l(
                "bang-claus-gives-you-card",
                buffer="game",
                player=claus.name,
                card=card_label(card, target_user.locale),
            )
        claus_user = self.get_user(claus)
        if claus_user:
            claus_user.speak_l(
                "bang-you-give-claus-card",
                buffer="game",
                target=target.name,
                card=card_label(card, claus_user.locale),
            )
        for observer in self.players:
            if observer.id in {claus.id, target.id}:
                continue
            user = self.get_user(observer)
            if user:
                kwargs = {
                    "player": claus.name,
                    "target": target.name,
                }
                if public:
                    kwargs["card"] = card_label(card, user.locale)
                user.speak_l(
                    (
                        "bang-claus-gives-public-card"
                        if public
                        else "bang-claus-gives-hidden-card"
                    ),
                    buffer="game",
                    **kwargs,
                )

    def _announce_peyote(
        self,
        player: BangPlayer,
        card: BangCard,
        correct: bool,
    ) -> None:
        self.broadcast_personal_l(
            player,
            "bang-your-peyote-result",
            "bang-peyote-result",
            buffer="game",
            card=lambda locale: card_label(card, locale),
            correct="yes" if correct else "no",
        )

    def _announce_ability(self, player: BangPlayer, ability: str) -> None:
        self.broadcast_personal_l(
            player,
            f"bang-you-use-{ability}",
            f"bang-player-uses-{ability}",
            buffer="game",
        )

    # ------------------------------------------------------------------
    # Information actions, restore repair, bots, and results
    # ------------------------------------------------------------------

    def _pace_bot(
        self,
        player: BangPlayer,
        *,
        choice: bool = False,
    ) -> None:
        delay = BOT_CHOICE_DELAY_TICKS if choice else BOT_TURN_DELAY_TICKS
        BotHelper.jolt_bot(
            player,
            ticks=random.randint(*delay),  # nosec B311 - presentation pacing
        )

    def _pace_bots(self) -> None:
        for player in self.seated_players:
            if player.is_bot:
                self._pace_bot(player)

    def _is_public_info_enabled(self, player: Player) -> str | None:
        del player
        return None if self.status == "playing" else "action-not-playing"

    def _is_private_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_info_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        return (
            Visibility.VISIBLE
            if self.is_touch_client(user)
            else Visibility.HIDDEN
        )

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return (
                Visibility.VISIBLE
                if self.status == "playing"
                else Visibility.HIDDEN
            )
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        """Report the active turn and any player who currently owes a choice."""

        super()._action_whose_turn(player, action_id)
        user = self.get_user(player)
        owner = self._private_choice_owner()
        if not user or not owner:
            return
        pending = (
            self._waiting_for_intent_error(owner, user.locale)
            if self.play_intent
            else self._waiting_for_input_error(owner, user.locale)
        )
        key, kwargs = pending
        user.speak_l(key, buffer="game", **kwargs)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        del action_id
        if isinstance(player, BangPlayer):
            self._speak_hand(player)

    def _speak_hand(self, player: BangPlayer) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not player.hand:
            user.speak_l("bang-hand-empty", buffer="game")
        else:
            labels = [
                card_label(card, user.locale)
                for card in sort_cards(player.hand)
            ]
            user.speak_l(
                "bang-your-hand",
                buffer="game",
                count=len(labels),
                cards=Localization.format_list_and(user.locale, labels),
            )
        in_play_labels = [
            card_label(in_play.card, user.locale)
            for in_play in player.in_play
        ]
        if in_play_labels:
            user.speak_l(
                "bang-your-in-play",
                buffer="game",
                cards=Localization.format_list_and(
                    user.locale,
                    in_play_labels,
                ),
            )
        else:
            user.speak_l("bang-in-play-empty", buffer="game")

    def _action_read_role(self, player: Player, action_id: str) -> None:
        del action_id
        if not isinstance(player, BangPlayer):
            return
        user = self.get_user(player)
        if user:
            ability = character_ability(player.character, user.locale)
            if player.character == "vera_custer" and player.copied_character:
                ability = Localization.get(
                    user.locale,
                    "bang-vera-active-copy",
                    character=character_name(
                        player.copied_character,
                        user.locale,
                    ),
                    ability=character_ability(
                        player.copied_character,
                        user.locale,
                    ),
                )
            user.speak_l(
                "bang-your-role-and-character",
                buffer="game",
                role=self._role_name(player.role, user.locale),
                character=character_name(player.character, user.locale),
                ability=ability,
                alternate=character_name(
                    player.alternate_character,
                    user.locale,
                ),
                life=player.life,
                maximum=player.max_life,
                weapon=self._weapon_status(player, user.locale),
            )

    def _action_read_life(self, player: Player, action_id: str) -> None:
        del action_id
        if not isinstance(player, BangPlayer):
            return
        user = self.get_user(player)
        if user:
            user.speak_l(
                "bang-your-life",
                buffer="game",
                life=player.life,
                maximum=player.max_life,
            )

    def _action_read_distances(self, player: Player, action_id: str) -> None:
        del action_id
        if not isinstance(player, BangPlayer):
            return
        self.live_status_box(
            player,
            "bang_distances",
            self._build_distance_status,
        )

    def _build_distance_status(
        self,
        player: Player,
        user,
    ) -> StatusBoxBuild:
        if not isinstance(player, BangPlayer):
            return StatusBoxBuild(items=[])
        locale = user.locale
        items = [
            MenuItem(
                id="weapon",
                text=Localization.get(
                    locale,
                    "bang-distance-weapon",
                    weapon=self._weapon_status(player, locale),
                ),
            )
        ]
        items.extend(
            MenuItem(
                id=f"player:{target.id}",
                text=Localization.get(
                    locale,
                    "bang-distance-line",
                    player=target.name,
                    distance=self.distance(player, target),
                ),
            )
            for target in self.players_in_play
            if target.id != player.id
        )
        return StatusBoxBuild(items=items)

    def _action_read_piles(self, player: Player, action_id: str) -> None:
        del action_id
        user = self.get_user(player)
        if not user:
            return
        top = (
            card_label(self.discard_pile[-1], user.locale)
            if self.discard_pile
            else Localization.get(user.locale, "bang-no-discard")
        )
        user.speak_l(
            "bang-piles",
            buffer="game",
            deck=len(self.deck),
            discard=len(self.discard_pile),
            top=top,
        )

    def _action_read_event(self, player: Player, action_id: str) -> None:
        del action_id
        user = self.get_user(player)
        if not user:
            return
        if not self.current_event:
            user.speak_l(
                "bang-no-current-event",
                buffer="game",
                remaining=len(self.event_deck),
            )
            return
        user.speak_l(
            "bang-current-event",
            buffer="game",
            event=event_name(self.current_event, user.locale),
            description=event_description(self.current_event, user.locale),
            remaining=len(self.event_deck),
        )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        del action_id
        self.live_status_box(player, "bang_table", self._build_table_status)

    def _build_table_status(self, player: Player, user) -> StatusBoxBuild:
        del player
        locale = user.locale
        items: list[MenuItem] = []
        if self.current_event:
            items.append(
                MenuItem(
                    id="event",
                    text=Localization.get(
                        locale,
                        "bang-status-event",
                        event=event_name(self.current_event, locale),
                    ),
                )
            )
        current = self.current_player
        if current:
            items.append(
                MenuItem(
                    id="turn",
                    text=Localization.get(
                        locale,
                        "bang-status-turn",
                        player=current.name,
                    ),
                )
            )
        for table_player in self.seated_players:
            role = (
                self._role_name(table_player.role, locale)
                if table_player.role_revealed
                else Localization.get(locale, "bang-role-hidden")
            )
            in_play = [
                card_name(in_play.card, locale)
                for in_play in table_player.in_play
            ]
            public_character = character_name(
                table_player.character,
                locale,
            )
            if (
                table_player.character == "vera_custer"
                and table_player.copied_character
            ):
                public_character = Localization.get(
                    locale,
                    "bang-character-with-copy",
                    character=public_character,
                    copied=character_name(
                        table_player.copied_character,
                        locale,
                    ),
                )
            items.append(
                MenuItem(
                    id=f"player:{table_player.id}",
                    text=Localization.get(
                        locale,
                        "bang-status-player",
                        player=table_player.name,
                        role=role,
                        character=public_character,
                        alternate=character_name(
                            table_player.alternate_character,
                            locale,
                        ),
                        life=table_player.life,
                        maximum=table_player.max_life,
                        hand=len(table_player.hand),
                        weapon=self._weapon_status(table_player, locale),
                        inplay=(
                            Localization.format_list_and(locale, in_play)
                            if in_play
                            else Localization.get(locale, "bang-no-in-play")
                        ),
                        state=(
                            "ghost"
                            if table_player.ghost_active
                            else (
                                "eliminated"
                                if table_player.eliminated
                                else "active"
                            )
                        ),
                    ),
                )
            )
        return StatusBoxBuild(items=items)

    def _repair_restored_state(self) -> None:
        active_ids = {player.id for player in self.seated_players}
        if self.play_intent:
            intent = self.play_intent
            actor = self.get_player_by_id(intent.actor_id)
            intent_valid = (
                intent.actor_id in active_ids
                and isinstance(actor, BangPlayer)
            )
            if intent_valid and intent.kind == "card":
                intent_valid = self._card_in_hand(actor, intent.card_id) is not None
            elif intent_valid and intent.kind == "green":
                intent_valid = any(
                    held.card.id == intent.card_id for held in actor.in_play
                )
            if intent_valid:
                hand_ids = {card.id for card in actor.hand}
                selected_ids = intent.selected_card_ids
                allowed_ids = intent.data.get("allowed_card_ids")
                intent_valid = (
                    len(selected_ids) == len(set(selected_ids))
                    and all(card_id in hand_ids for card_id in selected_ids)
                    and intent.card_id not in selected_ids
                    and (
                        not isinstance(allowed_ids, list)
                        or all(card_id in allowed_ids for card_id in selected_ids)
                    )
                )
            if intent_valid and intent.target_id:
                target = self.get_player_by_id(intent.target_id)
                intent_valid = (
                    isinstance(target, BangPlayer)
                    and (
                        intent.stage != "target"
                        or target in self._targets_for_intent(intent)
                    )
                )
            if intent_valid and intent.stage == "in_play_target":
                choices = self._in_play_choice_ids(
                    intent.data.get("mode", ""),
                )
                intent_valid = bool(choices) and (
                    not intent.in_play_card_id
                    or f"in_play_{intent.in_play_card_id}" in choices
                )
            if not intent_valid:
                self.play_intent = None
        if self.decision and self.decision.player_id not in active_ids:
            self.decision = None
        if self.decision and self.decision.kind == "elimination_discard":
            owner = self.get_player_by_id(self.decision.player_id)
            if isinstance(owner, BangPlayer):
                self.decision.card_ids = [card.id for card in owner.hand]
                self.decision.item_ids = [
                    f"in_play_{in_play.card.id}" for in_play in owner.in_play
                ]
                if self.decision.card_ids or self.decision.item_ids:
                    self.decision.item_ids.append(
                        "finish_elimination_discard"
                    )
                    self.decision.selected_card_ids.clear()
                else:
                    self.decision = None
        self.effect_stack = [
            frame
            for frame in self.effect_stack
            if not frame.actor_id or frame.actor_id in active_ids
        ]
        if self.revealed_cards and not any(
            frame.data.get("draw_started") for frame in self.effect_stack
        ):
            for card in self.revealed_cards:
                self.discard_pile.append(card)
            self.revealed_cards.clear()
        if self.general_store_cards and not any(
            frame.kind in {"general_store", "draw_phase"}
            for frame in self.effect_stack
        ):
            for card in self.general_store_cards:
                self.discard_pile.append(card)
            self.general_store_cards.clear()
        if self.decision is None and self.effect_stack:
            self._continue_effects()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if (
            not self.game_active
            or self.is_sequence_bot_paused()
            or self.decision
            and not self.get_player_by_id(self.decision.player_id)
        ):
            return
        if (
            self.effect_stack
            and self.decision is None
            and self.play_intent is None
        ):
            self._continue_effects()
            return
        self._process_one_bot()

    def _bot_candidate(self) -> BangPlayer | None:
        owner = self._private_choice_owner()
        if isinstance(owner, BangPlayer) and owner.is_bot:
            return owner
        current = self.current_player
        if (
            isinstance(current, BangPlayer)
            and current.is_bot
            and self.phase in {PHASE_PLAY, PHASE_DISCARD}
        ):
            return current
        return None

    def _process_one_bot(self) -> None:
        bot = self._bot_candidate()
        if not bot:
            return
        self._sync_turn_actions(bot)
        BotHelper.process_bot_action(
            bot,
            lambda: self.bot_think(bot),
            lambda action_id: self.execute_action(bot, action_id),
        )

    def bot_think(self, player: BangPlayer) -> str | None:
        return choose_bot_action(self, player)

    def build_game_result(self) -> GameResult:
        active = self.seated_players
        winners = set(self.winner_ids)
        ordered = sorted(
            active,
            key=lambda player: (
                player.id in winners,
                not player.eliminated or player.ghost_active,
                player.elimination_order,
            ),
            reverse=True,
        )
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in active
            ],
            custom_data={
                "winner_ids": list(self.winner_ids),
                "winner_score": 1,
                "winning_side": self.winning_side,
                "rankings": [
                    {
                        "name": player.name,
                        "role": player.role,
                        "character": player.character,
                        "winner": player.id in winners,
                        "elimination_order": player.elimination_order,
                    }
                    for player in ordered
                ],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [
            Localization.get(
                locale,
                "bang-end-side",
                side=self._role_name(
                    str(result.custom_data.get("winning_side", "")),
                    locale,
                ),
            )
        ]
        for rank, entry in enumerate(
            result.custom_data.get("rankings", []),
            1,
        ):
            lines.append(
                Localization.get(
                    locale,
                    "bang-end-player",
                    rank=rank,
                    player=entry["name"],
                    role=self._role_name(entry["role"], locale),
                    character=character_name(entry["character"], locale),
                    winner="yes" if entry["winner"] else "no",
                )
            )
        return lines
