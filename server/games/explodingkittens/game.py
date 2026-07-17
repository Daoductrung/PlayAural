"""Accessible Original Edition implementation of Exploding Kittens."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_CARDS
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.menu_management_mixin import StatusBoxBuild
from ...game_utils.options import BoolOption, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from .cards import (
    ACTION_KINDS,
    ATTACK,
    CAT_KINDS,
    DEFUSE,
    EXPLODING_KITTEN,
    FAVOR,
    NOPE,
    REQUESTABLE_KINDS,
    SEE_FUTURE,
    SHUFFLE,
    SKIP,
    ExplodingKittensCard,
    build_full_deck,
    card_name,
    sort_cards,
)
from .player import ExplodingKittensPlayer
from .bot import bot_think as _bot_think
from .state import (
    ACTION_ATTACK,
    ACTION_FAVOR,
    ACTION_PAIR,
    ACTION_SEE_FUTURE,
    ACTION_SHUFFLE,
    ACTION_SKIP,
    ACTION_TRIPLE,
    PHASE_COMBO,
    PHASE_DEFUSE,
    PHASE_FAVOR_GIVE,
    PHASE_GAME_OVER,
    PHASE_NOPE,
    PHASE_NORMAL,
    PHASE_REINSERT,
    PHASE_REQUEST,
    PHASE_RESOLVING,
    PHASE_STARTING,
    PHASE_TARGET,
    PendingAction,
)


INITIAL_ACTION_CARDS = 7
TICKS_PER_SECOND = 20
DEFAULT_NOPE_RESPONSE_SECONDS = "10"
NOPE_RESPONSE_CHOICES = ["5", "10", "15", "20"]
NOPE_RESPONSE_LABELS = {
    value: f"explodingkittens-nope-response-{value}"
    for value in NOPE_RESPONSE_CHOICES
}
NOPE_WINDOW_TICKS = int(DEFAULT_NOPE_RESPONSE_SECONDS) * TICKS_PER_SECOND
FAST_GAME_PLAYER_COUNTS = (2, 3)
GAME_START_DELAY_TICKS = 10 * TICKS_PER_SECOND
KITTEN_REVEAL_DELAY_TICKS = 18  # 900ms at the server's 20Hz tick rate.
CARD_PLAY_INTERVAL_DIVISOR = 3

SOUND_MUSIC = "game_ninetynine/mus.ogg"
SOUND_TURN = "turn.ogg"
SOUND_GAME_START = "game_explodingkittens/game_start.ogg"
SOUND_GAME_OVER = "game_explodingkittens/game_over.ogg"
SOUND_ACTION_CANCELED = "game_explodingkittens/action_canceled.ogg"
SOUND_ATTACK = "game_explodingkittens/attack.ogg"
SOUND_COMBO_MISS = "game_explodingkittens/combo_miss.ogg"
SOUND_DEFUSE = "game_explodingkittens/defuse.ogg"
SOUND_FUSE = "game_explodingkittens/fuse.ogg"
SOUND_KITTEN_REVEAL = "game_explodingkittens/kitten_reveal.ogg"
SOUND_REINSERT = "game_explodingkittens/reinsert.ogg"
SOUND_SEE_FUTURE = "game_explodingkittens/see_future.ogg"
SOUND_SKIP = "game_explodingkittens/skip.ogg"
SOUND_EXPLOSIONS = [
    "game_explodingkittens/explosion1.ogg",
    "game_explodingkittens/explosion2.ogg",
]
SOUND_NOPES = [
    "game_explodingkittens/nope1.ogg",
    "game_explodingkittens/nope2.ogg",
    "game_explodingkittens/nope3.ogg",
]
SOUND_DRAWS = [
    "game_explodingkittens/draw1.ogg",
    "game_explodingkittens/draw2.ogg",
]
SOUND_PLAYS = [
    "game_explodingkittens/play1.ogg",
    "game_explodingkittens/play2.ogg",
]
SOUND_SHUFFLES = [
    "game_explodingkittens/shuffle1.ogg",
    "game_explodingkittens/shuffle2.ogg",
    "game_explodingkittens/shuffle3.ogg",
]

# Ceiling-rounded from the actual OGG Vorbis granule durations at 20 ticks/second.
AUDIO_DURATIONS_TICKS = {
    SOUND_ACTION_CANCELED: 14,
    SOUND_ATTACK: 75,
    SOUND_COMBO_MISS: 30,
    SOUND_DEFUSE: 37,
    SOUND_EXPLOSIONS[0]: 79,
    SOUND_EXPLOSIONS[1]: 218,
    SOUND_FUSE: 14,
    SOUND_GAME_OVER: 72,
    SOUND_GAME_START: 271,
    SOUND_KITTEN_REVEAL: 68,
    SOUND_NOPES[0]: 21,
    SOUND_NOPES[1]: 21,
    SOUND_NOPES[2]: 21,
    SOUND_REINSERT: 31,
    SOUND_SEE_FUTURE: 107,
    SOUND_SKIP: 29,
    SOUND_DRAWS[0]: 11,
    SOUND_DRAWS[1]: 7,
    SOUND_PLAYS[0]: 9,
    SOUND_PLAYS[1]: 13,
    SOUND_SHUFFLES[0]: 15,
    SOUND_SHUFFLES[1]: 11,
    SOUND_SHUFFLES[2]: 14,
}
ACTION_BY_CARD_KIND = {
    ATTACK: ACTION_ATTACK,
    SKIP: ACTION_SKIP,
    FAVOR: ACTION_FAVOR,
    SHUFFLE: ACTION_SHUFFLE,
    SEE_FUTURE: ACTION_SEE_FUTURE,
}
CARD_KIND_BY_ACTION = {
    action_kind: card_kind for card_kind, action_kind in ACTION_BY_CARD_KIND.items()
}


@dataclass
class ExplodingKittensOptions(GameOptions):
    """Official setup options."""

    fast_game: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="explodingkittens-set-fast-game",
            change_msg="explodingkittens-option-changed-fast-game",
            description="explodingkittens-option-fast-game-description",
        )
    )
    advanced_combos: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="explodingkittens-set-advanced-combos",
            change_msg="explodingkittens-option-changed-advanced-combos",
            description="explodingkittens-option-advanced-combos-description",
        )
    )
    nope_response_seconds: str = option_field(
        MenuOption(
            choices=NOPE_RESPONSE_CHOICES,
            default=DEFAULT_NOPE_RESPONSE_SECONDS,
            value_key="time",
            label="explodingkittens-set-nope-response",
            prompt="explodingkittens-select-nope-response",
            change_msg="explodingkittens-option-changed-nope-response",
            choice_labels=NOPE_RESPONSE_LABELS,
            description="explodingkittens-option-nope-response-description",
        )
    )


@dataclass
@register_game
class ExplodingKittensGame(Game):
    """Turn-based, audio-first Exploding Kittens game."""

    players: list[ExplodingKittensPlayer] = field(default_factory=list)
    options: ExplodingKittensOptions = field(default_factory=ExplodingKittensOptions)
    deck: list[ExplodingKittensCard] = field(default_factory=list)
    discard_pile: list[ExplodingKittensCard] = field(default_factory=list)
    removed_cards: list[ExplodingKittensCard] = field(default_factory=list)
    phase: str = PHASE_NORMAL
    pending_action: PendingAction | None = None
    drawn_kitten: ExplodingKittensCard | None = None
    decision_player_id: str = ""
    turns_remaining: int = 1
    attack_obligation: bool = False
    winner_id: str = ""
    elimination_counter: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Exploding Kittens"

    @classmethod
    def get_type(cls) -> str:
        return "explodingkittens"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_CARDS

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def supports_score_actions(self) -> bool:
        return False

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ExplodingKittensPlayer:
        return ExplodingKittensPlayer(id=player_id, name=name, is_bot=is_bot)

    @property
    def alive_players(self) -> list[ExplodingKittensPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, ExplodingKittensPlayer) and not player.eliminated
        ]

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = []
        if self.options.fast_game and self.get_active_player_count() not in FAST_GAME_PLAYER_COUNTS:
            errors.append("explodingkittens-error-fast-game-player-count")
        if self.options.nope_response_seconds not in NOPE_RESPONSE_CHOICES:
            errors.append("explodingkittens-error-invalid-nope-response")
        return errors

    def _nope_window_ticks(self) -> int:
        seconds = self.options.nope_response_seconds
        if seconds not in NOPE_RESPONSE_CHOICES:
            seconds = DEFAULT_NOPE_RESPONSE_SECONDS
        return int(seconds) * TICKS_PER_SECOND

    def _sound_ticks(self, sound: str) -> int:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)

    def _random_draw_sound(self) -> str:
        return random.choice(SOUND_DRAWS)  # nosec B311 - cosmetic variation

    def _random_play_sound(self) -> str:
        return random.choice(SOUND_PLAYS)  # nosec B311 - cosmetic variation

    def _random_shuffle_sound(self) -> str:
        return random.choice(SOUND_SHUFFLES)  # nosec B311 - cosmetic variation

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1
        self.phase = PHASE_STARTING
        self.pending_action = None
        self.drawn_kitten = None
        self.decision_player_id = ""
        self.turns_remaining = 1
        self.attack_obligation = False
        self.winner_id = ""
        self.elimination_counter = 0
        self.deck.clear()
        self.discard_pile.clear()
        self.removed_cards.clear()
        self.set_turn_players([])
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, ExplodingKittensPlayer)
        ]
        for player in active:
            player.hand.clear()
            player.selected_card_ids.clear()
            player.known_future_card_ids.clear()
            player.eliminated = False
            player.elimination_order = 0
            self._clear_bot_plan(player)

        shuffle_sound = self._random_shuffle_sound()
        self.start_sequence(
            "explodingkittens_game_start",
            [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_GAME_START)],
                    delay_after_ticks=GAME_START_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op("prepare_match"),
                        SequenceOperation.callback_op(
                            "announce_match_start",
                            {"shuffle_sound": shuffle_sound},
                        ),
                    ],
                ),
            ],
            tag="explodingkittens_start",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.refresh_menus()

    def _prepare_match(self) -> None:
        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, ExplodingKittensPlayer)
        ]
        if not active:
            return
        self._prepare_deck(active)
        self.set_turn_players(active)
        self.turn_index = random.randrange(len(active))

    def _announce_match_start(self, shuffle_sound: str) -> None:
        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, ExplodingKittensPlayer)
        ]
        if not active or not self.turn_player_ids:
            return
        self.phase = PHASE_NORMAL
        resolved_shuffle = (
            shuffle_sound
            if shuffle_sound in SOUND_SHUFFLES
            else self._random_shuffle_sound()
        )
        self.play_sound(resolved_shuffle)
        self.play_music(SOUND_MUSIC)
        self.broadcast_l(
            "explodingkittens-game-started",
            buffer="game",
            players=len(active),
            cards=len(self.deck),
        )
        for player in active:
            if not player.is_bot:
                self._speak_hand(player)
        self.announce_turn(turn_sound=SOUND_TURN)
        BotHelper.jolt_bots(self)
        self.refresh_menus()

    def _prepare_deck(self, players: list[ExplodingKittensPlayer]) -> None:
        full_deck = build_full_deck()
        kittens = [card for card in full_deck if card.kind == EXPLODING_KITTEN]
        defuses = [card for card in full_deck if card.kind == DEFUSE]
        working = [
            card
            for card in full_deck
            if card.kind not in (EXPLODING_KITTEN, DEFUSE)
        ]
        random.shuffle(working)

        for player in players:
            player.hand.extend(working[:INITIAL_ACTION_CARDS])
            del working[:INITIAL_ACTION_CARDS]
            player.hand.append(defuses.pop())
            player.hand[:] = sort_cards(player.hand)

        extra_defuses = 1 if len(players) == 5 else 2
        working.extend(defuses[:extra_defuses])
        self.removed_cards.extend(defuses[extra_defuses:])

        if self.options.fast_game:
            random.shuffle(working)
            remove_count = len(working) // 3
            self.removed_cards.extend(working[:remove_count])
            del working[:remove_count]

        working.extend(kittens[: len(players) - 1])
        self.removed_cards.extend(kittens[len(players) - 1 :])
        random.shuffle(working)
        self.deck = working

    def on_tick(self) -> None:
        nope_pending_at_tick_start = (
            self.pending_action if self.phase == PHASE_NOPE else None
        )
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.game_active or self.is_sequence_bot_paused():
            return

        if (
            self.phase == PHASE_NOPE
            and self.pending_action is nope_pending_at_tick_start
        ):
            if self.pending_action.timer_ticks > 0:
                self.pending_action.timer_ticks -= 1
            if self.pending_action.timer_ticks <= 0:
                self._resolve_nope_window()
                return
        self._process_one_bot()

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        del sequence_id
        if callback_id == "prepare_match":
            self._prepare_match()
        elif callback_id == "announce_match_start":
            self._announce_match_start(str(payload.get("shuffle_sound", "")))
        elif callback_id == "finish_kitten_reveal":
            self._finish_kitten_reveal(payload)
        elif callback_id == "eliminate_for_final_explosion":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, ExplodingKittensPlayer) and not player.eliminated:
                self._eliminate_player(player, defer_game_over=True)
        elif callback_id == "resolve_final_explosion":
            alive = self.alive_players
            if len(alive) <= 1:
                self._end_game(alive[0] if alive else None)
            else:
                self.phase = PHASE_NORMAL
                self.refresh_menus()

    # ------------------------------------------------------------------
    # Action sets and menu state
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: Player) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        for action_id, label, handler, enabled, hidden in (
            ("play_nope", "explodingkittens-action-nope", "_action_play_nope", "_is_nope_enabled", "_is_nope_hidden"),
            (
                "pass_nope",
                "explodingkittens-action-pass",
                "_action_pass_nope",
                "_is_pass_nope_enabled",
                "_is_nope_hidden",
            ),
            ("draw_card", "explodingkittens-action-draw", "_action_draw_card", "_is_draw_enabled", "_is_draw_hidden"),
            (
                "start_combo",
                "explodingkittens-action-start-combo",
                "_action_start_combo",
                "_is_start_combo_enabled",
                "_is_start_combo_hidden",
            ),
            (
                "confirm_combo",
                "explodingkittens-action-confirm-combo",
                "_action_confirm_combo",
                "_is_confirm_combo_enabled",
                "_is_confirm_combo_hidden",
            ),
            (
                "combo_command",
                "explodingkittens-action-start-combo",
                "_action_combo_command",
                "_is_combo_command_enabled",
                "_is_combo_command_hidden",
            ),
            (
                "cancel_selection",
                "explodingkittens-action-cancel",
                "_action_cancel_selection",
                "_is_cancel_enabled",
                "_is_cancel_hidden",
            ),
            (
                "use_defuse",
                "explodingkittens-action-use-defuse",
                "_action_use_defuse",
                "_is_use_defuse_enabled",
                "_is_defuse_choice_hidden",
            ),
            (
                "accept_explosion",
                "explodingkittens-action-accept-explosion",
                "_action_accept_explosion",
                "_is_accept_explosion_enabled",
                "_is_defuse_choice_hidden",
            ),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label),
                    handler=handler,
                    is_enabled=enabled,
                    is_hidden=hidden,
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
        for action_id, label, handler, enabled, hidden, spectators in (
            (
                "read_hand",
                "explodingkittens-action-read-hand",
                "_action_read_hand",
                "_is_private_info_enabled",
                "_is_private_info_hidden",
                False,
            ),
            (
                "read_piles",
                "explodingkittens-action-read-piles",
                "_action_read_piles",
                "_is_public_info_enabled",
                "_is_public_info_hidden",
                True,
            ),
            (
                "read_table",
                "explodingkittens-action-read-table",
                "_action_read_table",
                "_is_public_info_enabled",
                "_is_public_info_hidden",
                True,
            ),
            (
                "check_nope_timer",
                "explodingkittens-action-check-nope-timer",
                "_action_check_nope_timer",
                "_is_nope_timer_enabled",
                "_is_nope_timer_hidden",
                True,
            ),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label),
                    handler=handler,
                    is_enabled=enabled,
                    is_hidden=hidden,
                    include_spectators=spectators,
                )
            )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_hand",
                    "read_piles",
                    "read_table",
                    "check_nope_timer",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Draw a card", ["draw_card"], state=KeybindState.ACTIVE)
        self.define_keybind("n", "Play Nope", ["play_nope"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass_nope"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "c",
            "Build or play a combo",
            ["combo_command"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind("x", "Cancel selection", ["cancel_selection"], state=KeybindState.ACTIVE)
        self.define_keybind("h", "Read hand", ["read_hand"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Read piles", ["read_piles"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("v", "Read table", ["read_table"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind(
            "shift+t",
            "Check Nope timer",
            ["check_nope_timer"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def _sync_turn_actions(
        self, player: Player, action_set: ActionSet | None = None
    ) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        if action_set is None:
            action_set = self.get_action_set(player, "turn")
        if action_set is None:
            return
        for prefix in ("play_card_", "target_", "request_", "insert_"):
            action_set.remove_by_prefix(prefix)

        user = self.get_user(player)
        locale = user.locale if user else "en"
        player.hand[:] = sort_cards(player.hand)
        for card in player.hand:
            action_set.add(
                Action(
                    id=f"play_card_{card.id}",
                    label=self._card_action_label(player, card, locale),
                    handler="_action_play_card",
                    is_enabled="_is_play_card_enabled",
                    is_hidden="_is_play_card_hidden",
                    get_label="_get_play_card_label",
                    show_in_actions_menu=False,
                )
            )

        if self.phase == PHASE_TARGET and self.pending_action and player.id == self.pending_action.actor_id:
            for target in self._valid_targets(player):
                action_set.add(
                    Action(
                        id=f"target_{target.id}",
                        label=Localization.get(
                            locale,
                            "explodingkittens-target-player",
                            player=target.name,
                            cards=len(target.hand),
                        ),
                        handler="_action_choose_target",
                        is_enabled="_is_target_enabled",
                        is_hidden="_is_target_hidden",
                        show_in_actions_menu=False,
                    )
                )

        if self.phase == PHASE_REQUEST and self.pending_action and player.id == self.pending_action.actor_id:
            for kind in REQUESTABLE_KINDS:
                action_set.add(
                    Action(
                        id=f"request_{kind}",
                        label=card_name(kind, locale),
                        handler="_action_choose_request",
                        is_enabled="_is_request_enabled",
                        is_hidden="_is_request_hidden",
                        show_in_actions_menu=False,
                    )
                )

        if self.phase == PHASE_REINSERT and player.id == self.decision_player_id:
            for position in range(len(self.deck) + 1):
                action_set.add(
                    Action(
                        id=f"insert_{position}",
                        label=self._insertion_label(locale, position),
                        handler="_action_reinsert_kitten",
                        is_enabled="_is_reinsert_enabled",
                        is_hidden="_is_reinsert_hidden",
                        show_in_actions_menu=False,
                    )
                )

        card_ids = [f"play_card_{card.id}" for card in player.hand]
        special_ids = [
            action_id
            for action_id in action_set._order
            if action_id.startswith(("target_", "request_", "insert_"))
        ]
        if special_ids:
            action_set._order = special_ids + ["cancel_selection"]
        elif self.phase == PHASE_DEFUSE and player.id == self.decision_player_id:
            action_set._order = ["use_defuse", "accept_explosion"]
        elif self.phase == PHASE_FAVOR_GIVE and self.pending_action and player.id == self.pending_action.target_id:
            action_set._order = card_ids
        elif self.phase == PHASE_COMBO and self.current_player == player:
            action_set._order = card_ids + ["confirm_combo", "cancel_selection"]
        elif self.phase == PHASE_NOPE and self._is_nope_responder(player):
            reactions = ["play_nope", "pass_nope"] if self.is_touch_client(user) else []
            action_set._order = reactions + card_ids
        else:
            action_set._order = card_ids + ["start_combo", "draw_card"]

    # ------------------------------------------------------------------
    # Visibility and validation
    # ------------------------------------------------------------------

    def _is_alive_player(self, player: Player) -> bool:
        return (
            isinstance(player, ExplodingKittensPlayer)
            and not player.is_spectator
            and not player.eliminated
        )

    def _base_play_error(self, player: Player) -> str | None:
        if self.status != "playing" or not self.game_active:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if not self._is_alive_player(player):
            return "explodingkittens-error-eliminated"
        return None

    def _card_for_action(
        self, player: Player, action_id: str | None
    ) -> ExplodingKittensCard | None:
        if not isinstance(player, ExplodingKittensPlayer) or not action_id:
            return None
        try:
            card_id = int(action_id.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            return None
        return next((card for card in player.hand if card.id == card_id), None)

    def _is_play_card_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if self.status != "playing" or not self._is_alive_player(player):
            return Visibility.HIDDEN
        if self.phase in (PHASE_TARGET, PHASE_REQUEST) and self.pending_action:
            if player.id == self.pending_action.actor_id:
                return Visibility.HIDDEN
        if self.phase in (PHASE_DEFUSE, PHASE_REINSERT) and player.id == self.decision_player_id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_card_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        error = self._base_play_error(player)
        if error:
            return error
        card = self._card_for_action(player, action_id)
        if card is None:
            return "explodingkittens-error-card-missing"

        if self.phase == PHASE_COMBO and self.current_player == player:
            if card.kind == EXPLODING_KITTEN:
                return "explodingkittens-error-card-not-combo"
            if not self.options.advanced_combos and card.kind not in CAT_KINDS:
                return "explodingkittens-error-advanced-combo-required"
            selected = player.selected_card_ids  # type: ignore[attr-defined]
            selected_kinds = {
                held.kind for held in player.hand if held.id in selected
            }
            if card.id not in selected and selected_kinds and card.kind not in selected_kinds:
                return "explodingkittens-error-combo-name-mismatch"
            combo_limit = 3 if self.options.advanced_combos else 2
            if card.id not in selected and len(selected) >= combo_limit:
                if self.options.advanced_combos:
                    return "explodingkittens-error-combo-too-large"
                return "explodingkittens-error-basic-combo-pair-only"
            return None

        if (
            self.phase == PHASE_FAVOR_GIVE
            and self.pending_action
            and player.id == self.pending_action.target_id
        ):
            return None

        if self.phase == PHASE_NOPE and card.kind == NOPE:
            return self._is_nope_enabled(player)

        if self.phase != PHASE_NORMAL:
            return "explodingkittens-error-action-in-progress"
        if self.current_player != player:
            return "action-not-your-turn"
        if card.kind == DEFUSE:
            return "explodingkittens-error-defuse-only-after-kitten"
        if card.kind == NOPE:
            return "explodingkittens-error-nope-only-in-response"
        if card.kind in CAT_KINDS:
            if self.options.advanced_combos:
                return "explodingkittens-error-cat-needs-combo"
            return "explodingkittens-error-cat-needs-pair"
        if card.kind == FAVOR and not self._valid_targets(player):
            return "explodingkittens-error-no-target-with-cards"
        if card.kind not in ACTION_KINDS:
            return "explodingkittens-error-card-not-playable"
        return None

    def _get_play_card_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        card = self._card_for_action(player, action_id)
        if card is None:
            return Localization.get(locale, "explodingkittens-card-unknown")
        return self._card_action_label(player, card, locale)

    def _card_action_label(
        self,
        player: ExplodingKittensPlayer,
        card: ExplodingKittensCard,
        locale: str,
    ) -> str:
        name = card_name(card, locale)
        if self.phase == PHASE_COMBO and self.current_player == player:
            key = (
                "explodingkittens-card-selected"
                if card.id in player.selected_card_ids
                else "explodingkittens-card-not-selected"
            )
            return Localization.get(locale, key, card=name)
        if (
            self.phase == PHASE_FAVOR_GIVE
            and self.pending_action
            and player.id == self.pending_action.target_id
        ):
            return Localization.get(locale, "explodingkittens-give-card-label", card=name)
        return name

    def _is_draw_enabled(self, player: Player) -> str | None:
        error = self._base_play_error(player)
        if error:
            return error
        if self.phase != PHASE_NORMAL:
            return "explodingkittens-error-action-in-progress"
        if self.current_player != player:
            return "action-not-your-turn"
        if not self.deck:
            return "explodingkittens-error-deck-empty"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if (
            self.status == "playing"
            and self.phase == PHASE_NORMAL
            and self._is_alive_player(player)
            and self.current_player == player
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _combo_kinds(self, player: ExplodingKittensPlayer) -> set[str]:
        counts: dict[str, int] = {}
        for card in player.hand:
            if card.kind != EXPLODING_KITTEN and (
                self.options.advanced_combos or card.kind in CAT_KINDS
            ):
                counts[card.kind] = counts.get(card.kind, 0) + 1
        return {kind for kind, count in counts.items() if count >= 2}

    def _has_combo(self, player: ExplodingKittensPlayer) -> bool:
        return bool(self._combo_kinds(player))

    def _is_start_combo_enabled(self, player: Player) -> str | None:
        error = self._is_draw_enabled(player)
        if error:
            return error
        if not self._valid_targets(player):
            return "explodingkittens-error-no-target-with-cards"
        if not isinstance(player, ExplodingKittensPlayer) or not self._has_combo(player):
            if self.options.advanced_combos:
                return "explodingkittens-error-no-combo"
            return "explodingkittens-error-no-cat-pair"
        return None

    def _is_start_combo_hidden(self, player: Player) -> Visibility:
        if self._is_draw_hidden(player) is Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, ExplodingKittensPlayer):
            return Visibility.HIDDEN
        if not self._has_combo(player) or not self._valid_targets(player):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_confirm_combo_enabled(self, player: Player) -> str | None:
        error = self._base_play_error(player)
        if error:
            return error
        if self.phase != PHASE_COMBO or self.current_player != player:
            return "explodingkittens-error-action-in-progress"
        if not isinstance(player, ExplodingKittensPlayer):
            return "explodingkittens-error-invalid-combo"
        cards = [card for card in player.hand if card.id in player.selected_card_ids]
        if len(cards) not in (2, 3) or len({card.kind for card in cards}) != 1:
            if not self.options.advanced_combos:
                return "explodingkittens-error-invalid-cat-pair"
            return "explodingkittens-error-invalid-combo"
        if not self.options.advanced_combos and (
            len(cards) != 2 or cards[0].kind not in CAT_KINDS
        ):
            return "explodingkittens-error-advanced-combo-required"
        return None

    def _is_confirm_combo_hidden(self, player: Player) -> Visibility:
        if self.phase == PHASE_COMBO and self.current_player == player:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_combo_command_enabled(self, player: Player) -> str | None:
        """Validate the phase-specific combo operation bound to C."""
        if self.phase == PHASE_COMBO and self.current_player == player:
            return self._is_confirm_combo_enabled(player)
        return self._is_start_combo_enabled(player)

    def _is_combo_command_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_cancel_enabled(self, player: Player) -> str | None:
        if self.pending_action and player.id == self.pending_action.actor_id:
            return None
        if self.phase == PHASE_COMBO and self.current_player == player:
            return None
        return "explodingkittens-error-action-in-progress"

    def _is_cancel_hidden(self, player: Player) -> Visibility:
        if self.phase == PHASE_COMBO and self.current_player == player:
            return Visibility.VISIBLE
        if (
            self.phase in (PHASE_TARGET, PHASE_REQUEST)
            and self.pending_action
            and player.id == self.pending_action.actor_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _nope_response_error(self, player: Player) -> str | None:
        error = self._base_play_error(player)
        if error:
            return error
        if self.phase != PHASE_NOPE or not self.pending_action:
            return "explodingkittens-error-not-nope-window"
        if player.id in self.pending_action.passed_player_ids:
            return "explodingkittens-error-already-passed-nope"
        if self.pending_action.nope_count == 0:
            if player.id == self.pending_action.actor_id:
                return "explodingkittens-error-nope-own-action"
        elif player.id == self.pending_action.last_nope_player_id:
            return "explodingkittens-error-nope-own-nope"
        return None

    def _is_nope_responder(self, player: Player) -> bool:
        return self._nope_response_error(player) is None

    def _is_nope_enabled(self, player: Player) -> str | None:
        error = self._nope_response_error(player)
        if error:
            return error
        if not isinstance(player, ExplodingKittensPlayer) or not any(card.kind == NOPE for card in player.hand):
            return "explodingkittens-error-no-nope"
        return None

    def _is_pass_nope_enabled(self, player: Player) -> str | None:
        return self._nope_response_error(player)

    def _is_nope_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self._is_nope_responder(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _defuse_decision_error(self, player: Player) -> str | None:
        error = self._base_play_error(player)
        if error:
            return error
        if self.phase != PHASE_DEFUSE or player.id != self.decision_player_id:
            return "explodingkittens-error-action-in-progress"
        return None

    def _is_use_defuse_enabled(self, player: Player) -> str | None:
        error = self._defuse_decision_error(player)
        if error:
            return error
        if not isinstance(player, ExplodingKittensPlayer):
            return "explodingkittens-error-card-missing"
        if not any(card.kind == DEFUSE for card in player.hand):
            return "explodingkittens-error-no-defuse"
        return None

    def _is_accept_explosion_enabled(self, player: Player) -> str | None:
        return self._defuse_decision_error(player)

    def _is_defuse_choice_hidden(self, player: Player) -> Visibility:
        if self.phase == PHASE_DEFUSE and player.id == self.decision_player_id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_target_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.phase != PHASE_TARGET or not self.pending_action or player.id != self.pending_action.actor_id:
            return "explodingkittens-error-action-in-progress"
        target = self._target_for_action(action_id)
        if target is None or target not in self._valid_targets(player):
            return "explodingkittens-error-invalid-target"
        return None

    def _is_target_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.phase == PHASE_TARGET and self.pending_action and player.id == self.pending_action.actor_id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_request_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.phase != PHASE_REQUEST or not self.pending_action or player.id != self.pending_action.actor_id:
            return "explodingkittens-error-action-in-progress"
        kind = self._kind_for_request_action(action_id)
        if kind not in REQUESTABLE_KINDS:
            return "explodingkittens-error-invalid-request"
        return None

    def _is_request_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.phase == PHASE_REQUEST and self.pending_action and player.id == self.pending_action.actor_id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_reinsert_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.phase != PHASE_REINSERT or player.id != self.decision_player_id or self.drawn_kitten is None:
            return "explodingkittens-error-action-in-progress"
        position = self._position_for_action(action_id)
        if position is None or not 0 <= position <= len(self.deck):
            return "explodingkittens-error-invalid-position"
        return None

    def _is_reinsert_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.phase == PHASE_REINSERT and player.id == self.decision_player_id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ------------------------------------------------------------------
    # Player actions and private selection flows
    # ------------------------------------------------------------------

    def _action_play_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        card = self._card_for_action(player, action_id)
        if card is None:
            return

        if self.phase == PHASE_NOPE and card.kind == NOPE:
            self._play_nope_card(player, card)
            return

        if self.phase == PHASE_COMBO:
            if card.id in player.selected_card_ids:
                player.selected_card_ids.remove(card.id)
            else:
                player.selected_card_ids.append(card.id)
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "explodingkittens-combo-selection-count",
                    buffer="game",
                    count=len(player.selected_card_ids),
                )
            self.request_menu_focus(player, action_id)
            return

        if self.phase == PHASE_FAVOR_GIVE and self.pending_action:
            self._give_favor_card(player, card)
            return

        if card.kind == FAVOR:
            self.pending_action = PendingAction(
                kind=ACTION_FAVOR,
                actor_id=player.id,
                card_ids=[card.id],
            )
            self.phase = PHASE_TARGET
            self._focus_first_target(player)
            return

        self.pending_action = PendingAction(
            kind=ACTION_BY_CARD_KIND[card.kind],
            actor_id=player.id,
            card_ids=[card.id],
        )
        self._commit_pending_action()

    def _action_start_combo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        self.phase = PHASE_COMBO
        self.pending_action = None
        player.selected_card_ids.clear()
        self._clear_bot_plan(player, keep_combo=True)
        combo_kinds = self._combo_kinds(player)
        first = next(
            (
                card
                for card in player.hand
                if card.kind in combo_kinds
            ),
            None,
        )
        if first:
            self.request_menu_focus(player, f"play_card_{first.id}")
        else:
            self.refresh_menus(player)

    def _action_combo_command(self, player: Player, action_id: str) -> None:
        """Route the C key to exactly one operation for the current phase."""
        if self.phase == PHASE_COMBO and self.current_player == player:
            self._action_confirm_combo(player, action_id)
        else:
            self._action_start_combo(player, action_id)

    def _action_confirm_combo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        cards = [card for card in player.hand if card.id in player.selected_card_ids]
        if len(cards) not in (2, 3) or len({card.kind for card in cards}) != 1:
            self._speak_error(player, "explodingkittens-error-invalid-combo")
            return
        self.pending_action = PendingAction(
            kind=ACTION_PAIR if len(cards) == 2 else ACTION_TRIPLE,
            actor_id=player.id,
            card_ids=[card.id for card in cards],
        )
        self.phase = PHASE_TARGET
        self._focus_first_target(player)

    def _action_cancel_selection(self, player: Player, action_id: str) -> None:
        if isinstance(player, ExplodingKittensPlayer):
            player.selected_card_ids.clear()
            self._clear_bot_plan(player)
        self.pending_action = None
        self.phase = PHASE_NORMAL
        focus = (
            f"play_card_{player.hand[0].id}"
            if isinstance(player, ExplodingKittensPlayer) and player.hand
            else "draw_card"
        )
        self.request_menu_focus(player, focus)

    def _action_choose_target(self, player: Player, action_id: str) -> None:
        if not self.pending_action:
            return
        target = self._target_for_action(action_id)
        if target is None:
            return
        self.pending_action.target_id = target.id
        if self.pending_action.kind == ACTION_TRIPLE:
            self.phase = PHASE_REQUEST
            self.request_menu_focus(player, f"request_{REQUESTABLE_KINDS[0]}")
            return
        self._commit_pending_action()

    def _action_choose_request(self, player: Player, action_id: str) -> None:
        if not self.pending_action:
            return
        kind = self._kind_for_request_action(action_id)
        if kind not in REQUESTABLE_KINDS:
            return
        self.pending_action.requested_kind = kind
        self._commit_pending_action()

    def _action_play_nope(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        self._play_nope_card(player)

    def _play_nope_card(
        self,
        player: ExplodingKittensPlayer,
        card: ExplodingKittensCard | None = None,
    ) -> None:
        """Consume one legal Nope, regardless of how the player activated it."""
        error = self._is_nope_enabled(player)
        if error:
            self._speak_error(player, error)
            return
        if card is None:
            card = next((held for held in player.hand if held.kind == NOPE), None)
        if card is None or card.kind != NOPE or card not in player.hand:
            self._speak_error(player, "explodingkittens-error-card-missing")
            return
        pending = self.pending_action
        if pending is None:
            self._speak_error(player, "explodingkittens-error-not-nope-window")
            return
        player.hand.remove(card)
        self.discard_pile.append(card)
        pending.nope_count += 1
        pending.last_nope_player_id = player.id
        pending.passed_player_ids.clear()
        pending.timer_ticks = self._nope_window_ticks()
        self.play_sound(random.choice(SOUND_NOPES))  # nosec B311 - cosmetic variation
        self._broadcast_actor(
            player,
            "explodingkittens-you-play-nope",
            "explodingkittens-player-plays-nope",
        )
        BotHelper.jolt_bots(self)
        self.refresh_menus()

    def _action_pass_nope(self, player: Player, action_id: str) -> None:
        error = self._is_pass_nope_enabled(player)
        if error:
            self._speak_error(player, error)
            return
        if not self.pending_action:
            return
        self.pending_action.passed_player_ids.append(player.id)
        user = self.get_user(player)
        if user:
            user.speak_l("explodingkittens-you-pass-nope", buffer="game")
        if self._all_nope_responders_passed():
            self._resolve_nope_window()
        else:
            self.refresh_menus(player)

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer) or not self.deck:
            return
        card = self.deck.pop(0)
        self._consume_known_top(card)
        self.play_sound(self._random_draw_sound())
        if card.kind == EXPLODING_KITTEN:
            self.drawn_kitten = card
            self.decision_player_id = player.id
            self.phase = PHASE_RESOLVING
            self.play_sound(SOUND_KITTEN_REVEAL)
            self._broadcast_actor(
                player,
                "explodingkittens-you-draw-kitten",
                "explodingkittens-player-draws-kitten",
            )
            self.start_sequence(
                "explodingkittens_kitten_reveal",
                [
                    SequenceBeat.pause(KITTEN_REVEAL_DELAY_TICKS),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "finish_kitten_reveal",
                                {"player_id": player.id},
                            )
                        ]
                    ),
                ],
                tag="explodingkittens_kitten_reveal",
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            self.refresh_menus()
            return

        player.hand.append(card)
        player.hand[:] = sort_cards(player.hand)
        user = self.get_user(player)
        if user:
            user.speak_l(
                "explodingkittens-you-draw-card",
                buffer="game",
                card=card_name(card, user.locale),
            )
        for observer in self.players:
            if observer.id == player.id:
                continue
            observer_user = self.get_user(observer)
            if observer_user:
                observer_user.speak_l(
                    "explodingkittens-player-draws-card",
                    buffer="game",
                    player=player.name,
                )
        self._complete_one_turn(player)

    def _finish_kitten_reveal(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if (
            not isinstance(player, ExplodingKittensPlayer)
            or self.drawn_kitten is None
            or self.decision_player_id != player.id
        ):
            self._cancel_stale_action()
            return
        if any(held.kind == DEFUSE for held in player.hand):
            self.phase = PHASE_DEFUSE
            self.request_menu_focus(player, "use_defuse")
            self.refresh_menus()
            return
        self._start_explosion_sequence(player)

    def _action_use_defuse(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        error = self._is_use_defuse_enabled(player)
        if error:
            self._speak_error(player, error)
            return
        defuse = next((card for card in player.hand if card.kind == DEFUSE), None)
        if defuse is None:
            return
        self.play_sound(SOUND_DEFUSE)
        self._finish_defuse({"player_id": player.id, "card_id": defuse.id})

    def _finish_defuse(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        card_id = int(payload.get("card_id", 0))
        if (
            not isinstance(player, ExplodingKittensPlayer)
            or self.drawn_kitten is None
            or self.decision_player_id != player.id
        ):
            self._cancel_stale_action()
            return
        defuse = next((card for card in player.hand if card.id == card_id), None)
        if defuse is None or defuse.kind != DEFUSE:
            self._cancel_stale_action()
            return
        player.hand.remove(defuse)
        self.discard_pile.append(defuse)
        self._broadcast_actor(
            player,
            "explodingkittens-you-defuse",
            "explodingkittens-player-defuses",
        )
        if not self.deck:
            self._reinsert_kitten(player, 0)
            return
        self.phase = PHASE_REINSERT
        self.request_menu_focus(player, "insert_0")
        self.refresh_menus()

    def _action_accept_explosion(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer):
            return
        error = self._is_accept_explosion_enabled(player)
        if error:
            self._speak_error(player, error)
            return
        self._start_explosion_sequence(player)

    def _action_reinsert_kitten(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ExplodingKittensPlayer) or self.drawn_kitten is None:
            return
        position = self._position_for_action(action_id)
        if position is None or not 0 <= position <= len(self.deck):
            return
        self._reinsert_kitten(player, position)

    def _start_explosion_sequence(self, player: ExplodingKittensPlayer) -> None:
        if self.drawn_kitten is None or self.decision_player_id != player.id:
            self._cancel_stale_action()
            return
        explosion_sound = random.choice(SOUND_EXPLOSIONS)  # nosec B311
        if len(self.alive_players) <= 2:
            self.phase = PHASE_RESOLVING
            self.start_sequence(
                "explodingkittens_final_explosion",
                [
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(SOUND_FUSE),
                            SequenceOperation.callback_op(
                                "eliminate_for_final_explosion",
                                {"player_id": player.id},
                            ),
                        ],
                        delay_after_ticks=self._sound_ticks(SOUND_FUSE),
                    ),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(explosion_sound),
                            SequenceOperation.callback_op("resolve_final_explosion"),
                        ]
                    ),
                ],
                tag="explodingkittens_final_explosion",
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            self.refresh_menus()
            return
        self.play_sound(SOUND_FUSE)
        self.schedule_sound(
            explosion_sound,
            delay_ticks=max(0, self._sound_ticks(SOUND_FUSE) - 1),
        )
        self._eliminate_player(player)

    def _reinsert_kitten(self, player: ExplodingKittensPlayer, position: int) -> None:
        if self.drawn_kitten is None:
            return
        self.play_sound(SOUND_REINSERT)
        self.deck.insert(position, self.drawn_kitten)
        self.drawn_kitten = None
        self.decision_player_id = ""
        self._clear_future_knowledge()
        self._broadcast_actor(
            player,
            "explodingkittens-you-reinsert-kitten",
            "explodingkittens-player-reinserts-kitten",
        )
        self._complete_one_turn(player)

    def _commit_pending_action(self) -> None:
        pending = self.pending_action
        if pending is None:
            return
        actor = self.get_player_by_id(pending.actor_id)
        if not isinstance(actor, ExplodingKittensPlayer) or actor.eliminated:
            self._cancel_stale_action()
            return
        cards = [card for card in actor.hand if card.id in pending.card_ids]
        if len(cards) != len(pending.card_ids):
            self._cancel_stale_action()
            return
        for card in cards:
            actor.hand.remove(card)
            self.discard_pile.append(card)
        actor.selected_card_ids.clear()
        self._clear_bot_plan(actor)
        self._play_committed_cards(len(cards))
        self._begin_nope_window()

    def _play_committed_cards(self, count: int) -> None:
        sounds = [self._random_play_sound() for _ in range(max(1, count))]
        self.play_sound(sounds[0])
        elapsed_ticks = self._card_play_interval_ticks(sounds[0])
        for sound in sounds[1:]:
            self.schedule_sound(sound, delay_ticks=max(0, elapsed_ticks - 1))
            elapsed_ticks += self._card_play_interval_ticks(sound)

    def _card_play_interval_ticks(self, sound: str) -> int:
        duration = self._sound_ticks(sound)
        return max(
            1,
            (duration + CARD_PLAY_INTERVAL_DIVISOR - 1)
            // CARD_PLAY_INTERVAL_DIVISOR,
        )

    def _begin_nope_window(self) -> None:
        pending = self.pending_action
        if pending is None:
            self._cancel_stale_action()
            return
        actor = self.get_player_by_id(pending.actor_id)
        cards = [
            card
            for card in self.discard_pile
            if card.id in pending.card_ids
        ]
        if not isinstance(actor, ExplodingKittensPlayer) or not cards:
            self._cancel_stale_action()
            return
        if pending.kind in (ACTION_PAIR, ACTION_TRIPLE):
            target = self.get_player_by_id(pending.target_id)
            self._broadcast_combo(actor, target, cards[0], pending.requested_kind)
        else:
            self._broadcast_card_play(actor, cards[0])
        self.phase = PHASE_NOPE
        pending.timer_ticks = self._nope_window_ticks()
        pending.passed_player_ids.clear()
        pending.last_nope_player_id = ""
        BotHelper.jolt_bots(self)
        self.refresh_menus()

    # ------------------------------------------------------------------
    # Nope and action resolution
    # ------------------------------------------------------------------

    def _nope_responder_ids(self) -> set[str]:
        if not self.pending_action:
            return set()
        excluded_id = (
            self.pending_action.actor_id
            if self.pending_action.nope_count == 0
            else self.pending_action.last_nope_player_id
        )
        return {player.id for player in self.alive_players if player.id != excluded_id}

    def _all_nope_responders_passed(self) -> bool:
        if not self.pending_action:
            return True
        return self._nope_responder_ids().issubset(set(self.pending_action.passed_player_ids))

    def _resolve_nope_window(self) -> None:
        if self.phase != PHASE_NOPE or self.pending_action is None:
            return
        pending = self.pending_action
        for player in self.alive_players:
            if player.is_bot:
                player.bot_pending_action = None
        pending.timer_ticks = 0
        self.phase = PHASE_RESOLVING
        if pending.nope_count % 2:
            actor = self.get_player_by_id(pending.actor_id)
            self.play_sound(SOUND_ACTION_CANCELED)
            if isinstance(actor, ExplodingKittensPlayer):
                self._announce_action_canceled(actor, pending)
            self.pending_action = None
            self.phase = PHASE_NORMAL
            self.refresh_menus()
            return

        actor = self.get_player_by_id(pending.actor_id)
        if not isinstance(actor, ExplodingKittensPlayer) or actor.eliminated:
            self._cancel_stale_action()
            return
        if pending.kind == ACTION_ATTACK:
            self.play_sound(SOUND_ATTACK)
            self._resolve_attack(actor, pending)
        elif pending.kind == ACTION_SKIP:
            self.play_sound(SOUND_SKIP)
            self._resolve_skip(actor, pending)
        elif pending.kind == ACTION_SHUFFLE:
            self.play_sound(self._random_shuffle_sound())
            self._resolve_shuffle(actor, pending)
        elif pending.kind == ACTION_SEE_FUTURE:
            self.play_sound(SOUND_SEE_FUTURE)
            self._resolve_see_future(actor, pending)
        elif pending.kind == ACTION_FAVOR:
            self._resolve_favor_request(actor, pending)
        elif pending.kind == ACTION_PAIR:
            target = self.get_player_by_id(pending.target_id)
            if not isinstance(target, ExplodingKittensPlayer) or not target.hand:
                self._cancel_stale_action()
                return
            card_id = random.choice(target.hand).id  # nosec B311
            self.play_sound(self._random_draw_sound())
            self._resolve_pair(actor, pending, card_id=card_id)
        elif pending.kind == ACTION_TRIPLE:
            target = self.get_player_by_id(pending.target_id)
            if not isinstance(target, ExplodingKittensPlayer):
                self._cancel_stale_action()
                return
            requested = next(
                (card for card in target.hand if card.kind == pending.requested_kind),
                None,
            )
            self.play_sound(
                self._random_draw_sound() if requested else SOUND_COMBO_MISS
            )
            self._resolve_triple(
                actor,
                pending,
                card_id=requested.id if requested else 0,
            )
        else:
            self._cancel_stale_action()

    def _resolve_attack(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        turns = self.turns_remaining + 2 if self.attack_obligation else 2
        self.pending_action = None
        self.phase = PHASE_NORMAL
        next_player = self._advance_to_next_alive()
        self.turns_remaining = turns
        self.attack_obligation = True
        if next_player:
            self._play_turn_sound(next_player)
            self._announce_attack_resolution(actor, next_player, turns)
        self.refresh_menus()

    def _resolve_skip(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        self._announce_action_resolved(actor, pending)
        self.pending_action = None
        self._complete_one_turn(actor)

    def _resolve_shuffle(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        random.shuffle(self.deck)
        self._clear_future_knowledge()
        self._announce_shuffle_resolved(actor)
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.refresh_menus()

    def _resolve_see_future(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        cards = self.deck[:3]
        actor.known_future_card_ids = [card.id for card in cards]
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == actor.id:
                names = [card_name(card, user.locale) for card in cards]
                user.speak_l(
                    "explodingkittens-future-cards",
                    buffer="game",
                    cards=Localization.format_list_and(user.locale, names),
                )
            else:
                user.speak_l(
                    "explodingkittens-player-see-future-resolves",
                    buffer="game",
                    player=actor.name,
                )
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.refresh_menus()

    def _resolve_favor_request(
        self, actor: ExplodingKittensPlayer, pending: PendingAction
    ) -> None:
        target = self.get_player_by_id(pending.target_id)
        if not isinstance(target, ExplodingKittensPlayer) or target.eliminated or not target.hand:
            self._cancel_stale_action()
            return
        if len(target.hand) == 1:
            self._give_favor_card(target, target.hand[0])
            return
        self.phase = PHASE_FAVOR_GIVE
        self._announce_favor_choice(actor, target)
        self.request_menu_focus(target, f"play_card_{sort_cards(target.hand)[0].id}")
        self.refresh_menus()

    def _give_favor_card(
        self, target: ExplodingKittensPlayer, card: ExplodingKittensCard
    ) -> None:
        pending = self.pending_action
        if pending is None or target.id != pending.target_id:
            return
        actor = self.get_player_by_id(pending.actor_id)
        if not isinstance(actor, ExplodingKittensPlayer) or actor.eliminated:
            self._cancel_stale_action()
            return
        if card not in target.hand:
            self._cancel_stale_action()
            return
        self.play_sound(self._random_draw_sound())
        self._finish_transfer(actor, target, card, "favor")

    def _finish_transfer(
        self,
        actor: ExplodingKittensPlayer,
        target: ExplodingKittensPlayer,
        card: ExplodingKittensCard,
        method: str,
    ) -> None:
        if card not in target.hand:
            self._cancel_stale_action()
            return
        target.hand.remove(card)
        actor.hand.append(card)
        actor.hand[:] = sort_cards(actor.hand)
        self._announce_transfer(actor, target, card, method)
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.refresh_menus()

    def _resolve_pair(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
        *,
        card_id: int = 0,
    ) -> None:
        target = self.get_player_by_id(pending.target_id)
        if not isinstance(target, ExplodingKittensPlayer) or target.eliminated or not target.hand:
            self._cancel_stale_action()
            return
        card = next((held for held in target.hand if held.id == card_id), None)
        if card is None and not card_id:
            card = random.choice(target.hand)  # nosec B311 - direct-call fallback
        if card is None:
            self._cancel_stale_action()
            return
        self._finish_transfer(actor, target, card, "pair")

    def _resolve_triple(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
        *,
        card_id: int = 0,
    ) -> None:
        target = self.get_player_by_id(pending.target_id)
        if not isinstance(target, ExplodingKittensPlayer) or target.eliminated:
            self._cancel_stale_action()
            return
        card = next((held for held in target.hand if held.id == card_id), None)
        if card is None and not card_id:
            card = next(
                (held for held in target.hand if held.kind == pending.requested_kind),
                None,
            )
        if card:
            self._finish_transfer(actor, target, card, "triple")
        else:
            self._announce_triple_miss(actor, target, pending.requested_kind)
            self.pending_action = None
            self.phase = PHASE_NORMAL
            self.refresh_menus()

    # ------------------------------------------------------------------
    # Turns, Defusing, elimination, and knowledge
    # ------------------------------------------------------------------

    def _complete_one_turn(self, player: ExplodingKittensPlayer) -> None:
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.decision_player_id = ""
        if self.turns_remaining > 1:
            self.turns_remaining -= 1
            self._play_turn_sound(player)
            self._announce_turns(player, self.turns_remaining)
        else:
            self.turns_remaining = 1
            self.attack_obligation = False
            next_player = self._advance_to_next_alive()
            if next_player:
                self.announce_turn(turn_sound=SOUND_TURN)
        BotHelper.jolt_bots(self)
        self.refresh_menus()

    def _play_turn_sound(self, player: ExplodingKittensPlayer) -> None:
        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound(SOUND_TURN)

    def _advance_to_next_alive(self) -> ExplodingKittensPlayer | None:
        if not self.turn_player_ids:
            return None
        for _ in range(len(self.turn_player_ids)):
            self.turn_index = (self.turn_index + 1) % len(self.turn_player_ids)
            candidate = self.current_player
            if isinstance(candidate, ExplodingKittensPlayer) and not candidate.eliminated:
                return candidate
        return None

    def _announce_turns(self, player: ExplodingKittensPlayer, turns: int) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == player.id:
                user.speak_l("explodingkittens-you-have-turns", buffer="game", turns=turns)
            else:
                user.speak_l(
                    "explodingkittens-player-has-turns",
                    buffer="game",
                    player=player.name,
                    turns=turns,
                )

    def _eliminate_player(
        self,
        player: ExplodingKittensPlayer,
        *,
        defer_game_over: bool = False,
    ) -> None:
        kitten = self.drawn_kitten
        self.drawn_kitten = None
        self.decision_player_id = ""
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.removed_cards.extend(player.hand)
        player.hand.clear()
        if kitten:
            self.removed_cards.append(kitten)
        player.selected_card_ids.clear()
        player.known_future_card_ids.clear()
        player.eliminated = True
        self.elimination_counter += 1
        player.elimination_order = self.elimination_counter
        self._broadcast_actor(
            player,
            "explodingkittens-you-explode",
            "explodingkittens-player-explodes",
        )

        alive = self.alive_players
        if len(alive) <= 1:
            if defer_game_over:
                self.phase = PHASE_RESOLVING
                self.refresh_menus()
                return
            self._end_game(alive[0] if alive else None)
            return

        self.turns_remaining = 1
        self.attack_obligation = False
        next_player = self._advance_to_next_alive()
        if next_player:
            self.announce_turn(turn_sound=SOUND_TURN)
        BotHelper.jolt_bots(self)
        self.refresh_menus()

    def _consume_known_top(self, drawn: ExplodingKittensCard) -> None:
        for player in self.alive_players:
            if player.known_future_card_ids and player.known_future_card_ids[0] == drawn.id:
                player.known_future_card_ids.pop(0)
            elif player.known_future_card_ids:
                player.known_future_card_ids.clear()

    def _clear_future_knowledge(self) -> None:
        for player in self.alive_players:
            player.known_future_card_ids.clear()

    def _known_future_cards(
        self, player: ExplodingKittensPlayer
    ) -> list[ExplodingKittensCard]:
        known: list[ExplodingKittensCard] = []
        for index, card_id in enumerate(player.known_future_card_ids):
            if index >= len(self.deck) or self.deck[index].id != card_id:
                return []
            known.append(self.deck[index])
        return known

    def _end_game(self, winner: ExplodingKittensPlayer | None) -> None:
        if self.phase == PHASE_GAME_OVER or self.status == "finished":
            return
        self.phase = PHASE_GAME_OVER
        self.winner_id = winner.id if winner else ""
        self.play_sound(SOUND_GAME_OVER)
        if winner:
            self._broadcast_actor(
                winner,
                "explodingkittens-you-win",
                "explodingkittens-player-wins",
            )
        self.finish_game()

    def _cancel_stale_action(self) -> None:
        for player in self.alive_players:
            player.selected_card_ids.clear()
            self._clear_bot_plan(player)
        self.pending_action = None
        self.phase = PHASE_NORMAL
        self.refresh_menus()

    # ------------------------------------------------------------------
    # Information actions
    # ------------------------------------------------------------------

    def _is_public_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_private_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_public_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_private_info_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_public_info_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_nope_timer_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != PHASE_NOPE or self.pending_action is None:
            return "action-not-available"
        return None

    def _is_nope_timer_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.phase == PHASE_NOPE and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if isinstance(player, ExplodingKittensPlayer):
            self._speak_hand(player)

    def _speak_hand(self, player: ExplodingKittensPlayer) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not player.hand:
            user.speak_l("explodingkittens-hand-empty", buffer="game")
            return
        names = [card_name(card, user.locale) for card in sort_cards(player.hand)]
        user.speak_l(
            "explodingkittens-hand",
            buffer="game",
            count=len(names),
            cards=Localization.format_list_and(user.locale, names),
        )

    def _action_read_piles(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        top = (
            card_name(self.discard_pile[-1], user.locale)
            if self.discard_pile
            else Localization.get(user.locale, "explodingkittens-no-discard")
        )
        user.speak_l(
            "explodingkittens-piles",
            buffer="game",
            deck=len(self.deck),
            discard=len(self.discard_pile),
            top=top,
        )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        self.live_status_box(player, "explodingkittens_table", self._build_table_status)

    def _action_check_nope_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not self.pending_action:
            return
        seconds = max(0, (self.pending_action.timer_ticks + 19) // 20)
        user.speak_l(
            "explodingkittens-nope-time-remaining",
            buffer="game",
            seconds=seconds,
        )

    def _build_table_status(self, player: Player, user) -> StatusBoxBuild:
        locale = user.locale
        items: list[MenuItem] = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "explodingkittens-table-piles",
                    deck=len(self.deck),
                    discard=len(self.discard_pile),
                ),
                id="piles",
            )
        ]
        current = self.current_player
        if current:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "explodingkittens-table-turn",
                        player=current.name,
                        turns=self.turns_remaining,
                    ),
                    id="turn",
                )
            )
        visible_phase = self.phase
        private_owner_id = ""
        if self.phase == PHASE_COMBO and self.current_player:
            private_owner_id = self.current_player.id
        elif self.phase in (PHASE_TARGET, PHASE_REQUEST) and self.pending_action:
            private_owner_id = self.pending_action.actor_id
        if private_owner_id and player.id != private_owner_id:
            visible_phase = PHASE_NORMAL
        items.append(
            MenuItem(
                text=Localization.get(locale, f"explodingkittens-phase-{visible_phase.replace('_', '-')}"),
                id="phase",
            )
        )
        for table_player in self.get_active_players():
            if not isinstance(table_player, ExplodingKittensPlayer):
                continue
            status = Localization.get(
                locale,
                "explodingkittens-status-eliminated" if table_player.eliminated else "explodingkittens-status-alive",
            )
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "explodingkittens-table-player",
                        player=table_player.name,
                        cards=len(table_player.hand),
                        status=status,
                    ),
                    id=f"player:{table_player.id}",
                )
            )
        return StatusBoxBuild(items=items)

    # ------------------------------------------------------------------
    # Bots
    # ------------------------------------------------------------------

    def _bot_candidates(self) -> list[ExplodingKittensPlayer]:
        if self.phase == PHASE_NOPE:
            return [player for player in self.alive_players if player.is_bot and self._is_nope_responder(player)]
        owner: Player | None = None
        if self.phase in (PHASE_NORMAL, PHASE_COMBO):
            owner = self.current_player
        elif self.phase in (PHASE_TARGET, PHASE_REQUEST) and self.pending_action:
            owner = self.get_player_by_id(self.pending_action.actor_id)
        elif self.phase == PHASE_FAVOR_GIVE and self.pending_action:
            owner = self.get_player_by_id(self.pending_action.target_id)
        elif self.phase in (PHASE_DEFUSE, PHASE_REINSERT):
            owner = self.get_player_by_id(self.decision_player_id)
        if isinstance(owner, ExplodingKittensPlayer) and owner.is_bot and not owner.eliminated:
            return [owner]
        return []

    def _process_one_bot(self) -> None:
        for bot in self._bot_candidates():
            self._sync_turn_actions(bot)
            acted = BotHelper.process_bot_action(
                bot,
                lambda bot=bot: self.bot_think(bot),
                lambda action_id, bot=bot: self.execute_action(bot, action_id),
            )
            if acted:
                return

    def bot_think(self, player: ExplodingKittensPlayer) -> str | None:
        return _bot_think(self, player)

    def _clear_bot_plan(
        self, player: ExplodingKittensPlayer, *, keep_combo: bool = False
    ) -> None:
        if not keep_combo:
            player.bot_combo_kind = ""
            player.bot_combo_card_ids.clear()
        player.bot_planned_target_id = ""
        player.bot_requested_kind = ""

    # ------------------------------------------------------------------
    # Localization-aware communication and parsing helpers
    # ------------------------------------------------------------------

    def _speak_error(self, player: Player, key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(key, buffer="game", **kwargs)

    def _broadcast_actor(self, actor: Player, personal_key: str, public_key: str, **kwargs) -> None:
        self.broadcast_personal_l(actor, personal_key, public_key, buffer="game", **kwargs)

    def _pending_action_name(self, pending: PendingAction, locale: str) -> str:
        if pending.kind == ACTION_PAIR:
            return Localization.get(locale, "explodingkittens-action-name-pair")
        if pending.kind == ACTION_TRIPLE:
            return Localization.get(locale, "explodingkittens-action-name-triple")
        return card_name(CARD_KIND_BY_ACTION.get(pending.kind, pending.kind), locale)

    def _announce_action_canceled(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            action = self._pending_action_name(pending, user.locale)
            if listener.id == actor.id:
                user.speak_l(
                    "explodingkittens-your-action-canceled",
                    buffer="game",
                    action=action,
                )
            else:
                user.speak_l(
                    "explodingkittens-player-action-canceled",
                    buffer="game",
                    player=actor.name,
                    action=action,
                )

    def _announce_action_resolved(
        self,
        actor: ExplodingKittensPlayer,
        pending: PendingAction,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            action = self._pending_action_name(pending, user.locale)
            if listener.id == actor.id:
                user.speak_l(
                    "explodingkittens-your-action-resolves",
                    buffer="game",
                    action=action,
                )
            else:
                user.speak_l(
                    "explodingkittens-player-action-resolves",
                    buffer="game",
                    player=actor.name,
                    action=action,
                )

    def _announce_shuffle_resolved(self, actor: ExplodingKittensPlayer) -> None:
        self._broadcast_actor(
            actor,
            "explodingkittens-your-shuffle-resolves",
            "explodingkittens-player-shuffle-resolves",
        )

    def _announce_attack_resolution(
        self,
        actor: ExplodingKittensPlayer,
        target: ExplodingKittensPlayer,
        turns: int,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == actor.id:
                key = "explodingkittens-your-attack-resolves"
            elif listener.id == target.id:
                key = "explodingkittens-attack-resolves-target"
            else:
                key = "explodingkittens-player-attack-resolves"
            user.speak_l(
                key,
                buffer="game",
                player=actor.name,
                target=target.name,
                turns=turns,
            )

    def _announce_favor_choice(
        self,
        actor: ExplodingKittensPlayer,
        target: ExplodingKittensPlayer,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == actor.id:
                key = "explodingkittens-your-favor-resolves"
            elif listener.id == target.id:
                key = "explodingkittens-favor-resolves-target"
            else:
                key = "explodingkittens-player-favor-resolves"
            user.speak_l(
                key,
                buffer="game",
                player=actor.name,
                target=target.name,
            )

    def _broadcast_card_play(
        self, actor: ExplodingKittensPlayer, card: ExplodingKittensCard
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            name = card_name(card, user.locale)
            if listener.id == actor.id:
                user.speak_l("explodingkittens-you-play-card", buffer="game", card=name)
            else:
                user.speak_l(
                    "explodingkittens-player-plays-card",
                    buffer="game",
                    player=actor.name,
                    card=name,
                )

    def _broadcast_combo(
        self,
        actor: ExplodingKittensPlayer,
        target: Player | None,
        card: ExplodingKittensCard,
        requested_kind: str,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {
                "card": card_name(card, user.locale),
                "target": target.name if target else "",
            }
            if requested_kind:
                kwargs["request"] = card_name(requested_kind, user.locale)
            suffix = "triple" if requested_kind else "pair"
            if listener.id == actor.id:
                user.speak_l(f"explodingkittens-you-play-{suffix}", buffer="game", **kwargs)
            else:
                user.speak_l(
                    f"explodingkittens-player-plays-{suffix}",
                    buffer="game",
                    player=actor.name,
                    **kwargs,
                )

    def _announce_transfer(
        self,
        actor: ExplodingKittensPlayer,
        target: ExplodingKittensPlayer,
        card: ExplodingKittensCard,
        method: str,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            localized_card = card_name(card, user.locale)
            if listener.id == actor.id:
                user.speak_l(
                    f"explodingkittens-{method}-transfer-you",
                    buffer="game",
                    target=target.name,
                    card=localized_card,
                )
            elif listener.id == target.id:
                user.speak_l(
                    f"explodingkittens-{method}-transfer-target",
                    buffer="game",
                    player=actor.name,
                    card=localized_card,
                )
            else:
                user.speak_l(
                    f"explodingkittens-{method}-transfer-public",
                    buffer="game",
                    player=actor.name,
                    target=target.name,
                )

    def _announce_triple_miss(
        self,
        actor: ExplodingKittensPlayer,
        target: ExplodingKittensPlayer,
        requested_kind: str,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            request = card_name(requested_kind, user.locale)
            if listener.id == actor.id:
                key = "explodingkittens-triple-miss-you"
            elif listener.id == target.id:
                key = "explodingkittens-triple-miss-target"
            else:
                key = "explodingkittens-triple-miss-public"
            user.speak_l(key, buffer="game", player=actor.name, target=target.name, card=request)

    def _valid_targets(self, actor: Player) -> list[ExplodingKittensPlayer]:
        return [player for player in self.alive_players if player.id != actor.id and bool(player.hand)]

    def _focus_first_target(self, actor: Player) -> None:
        targets = self._valid_targets(actor)
        if not targets:
            self._cancel_stale_action()
            return
        if len(targets) == 1 and self.pending_action:
            self.pending_action.target_id = targets[0].id
            if self.pending_action.kind == ACTION_TRIPLE:
                self.phase = PHASE_REQUEST
                self.request_menu_focus(actor, f"request_{REQUESTABLE_KINDS[0]}")
            else:
                self._commit_pending_action()
            return
        self.request_menu_focus(actor, f"target_{targets[0].id}")

    def _target_for_action(self, action_id: str | None) -> ExplodingKittensPlayer | None:
        if not action_id or not action_id.startswith("target_"):
            return None
        player = self.get_player_by_id(action_id[len("target_") :])
        return player if isinstance(player, ExplodingKittensPlayer) else None

    @staticmethod
    def _kind_for_request_action(action_id: str | None) -> str:
        if not action_id or not action_id.startswith("request_"):
            return ""
        return action_id[len("request_") :]

    @staticmethod
    def _position_for_action(action_id: str | None) -> int | None:
        if not action_id or not action_id.startswith("insert_"):
            return None
        try:
            return int(action_id[len("insert_") :])
        except ValueError:
            return None

    def _insertion_label(self, locale: str, position: int) -> str:
        if position == 0:
            return Localization.get(locale, "explodingkittens-insert-top")
        if position == len(self.deck):
            return Localization.get(locale, "explodingkittens-insert-bottom")
        return Localization.get(locale, "explodingkittens-insert-position", cards=position)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, ExplodingKittensPlayer)
        ]
        rankings = sorted(
            active,
            key=lambda player: (
                0 if player.id == self.winner_id else 1,
                -player.elimination_order,
                player.name,
            ),
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
                "winner_name": next((player.name for player in active if player.id == self.winner_id), None),
                "winner_ids": [self.winner_id] if self.winner_id else [],
                "team_rankings": [
                    {
                        "index": index,
                        "members": [player.name],
                        "score": len(rankings) - index,
                        "is_individual": True,
                    }
                    for index, player in enumerate(rankings)
                ],
                "rankings": [player.name for player in rankings],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        winner = result.custom_data.get("winner_name")
        lines = [
            Localization.get(locale, "explodingkittens-results-winner", player=winner)
            if winner
            else Localization.get(locale, "game-over")
        ]
        for rank, name in enumerate(result.custom_data.get("rankings", []), 1):
            lines.append(
                Localization.get(
                    locale,
                    "explodingkittens-results-place",
                    rank=rank,
                    player=name,
                )
            )
        return lines
