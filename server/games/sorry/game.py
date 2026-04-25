from dataclasses import dataclass, field
from datetime import datetime
import random

from ...messages.localization import Localization
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import BoolOption, GameOptions, MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ..base import Game, Player
from ..registry import register_game
from .bot import choose_move
from .moves import CaptureEvent, SorryMove, apply_move, generate_legal_moves, generate_split_options_for_pair
from .rules import RULES_PROFILES, get_rules_profile_by_id, get_supported_profile_ids
from .state import (
    SorryGameState,
    SorryPlayerState,
    TRACK_LENGTH,
    build_initial_game_state,
    discard_current_card,
    draw_next_card,
    normalize_track_position,
)
from ...ui.keybinds import KeybindState


PLAYER_COLORS = ("red", "blue", "yellow", "green")
RULES_PROFILE_CHOICES = list(get_supported_profile_ids())
RULES_PROFILE_LABELS = {
    "classic_00390": "sorry-rules-profile-classic-00390",
    "a5065_core": "sorry-rules-profile-a5065-core",
}


@dataclass
class SorryPlayer(Player):
    color: str = ""
    pawns_in_start: int = 0
    pawns_in_home: int = 0


@dataclass
class SorryOptions(GameOptions):
    rules_profile: str = option_field(
        MenuOption(
            default="classic_00390",
            choices=RULES_PROFILE_CHOICES,
            value_key="profile",
            label="sorry-set-rules-profile",
            prompt="sorry-select-rules-profile",
            change_msg="sorry-option-changed-rules-profile",
            choice_labels=RULES_PROFILE_LABELS,
        )
    )
    auto_apply_single_move: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="sorry-toggle-auto-apply-single-move",
            change_msg="sorry-option-changed-auto-apply-single-move",
        )
    )
    faster_setup_one_pawn_out: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="sorry-toggle-faster-setup-one-pawn-out",
            change_msg="sorry-option-changed-faster-setup-one-pawn-out",
        )
    )


@register_game
@dataclass
class SorryGame(Game):
    players: list[SorryPlayer] = field(default_factory=list)
    options: SorryOptions = field(default_factory=SorryOptions)

    game_state: SorryGameState = field(default_factory=SorryGameState)
    winner_name: str = ""
    ended_due_to_empty_deck: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Sorry!"

    @classmethod
    def get_type(cls) -> str:
        return "sorry"

    @classmethod
    def get_category(cls) -> str:
        return "board"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, id: str, name: str, is_bot: bool) -> SorryPlayer:
        return SorryPlayer(id=id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_rules_profile(self):
        return get_rules_profile_by_id(self.options.rules_profile) or RULES_PROFILES["classic_00390"]

    def _get_player_state(self, player: Player) -> SorryPlayerState | None:
        return self.game_state.player_states.get(player.id)

    def _parse_move_slot(self, action_id: str) -> int | None:
        prefix = "move_slot_"
        if not action_id.startswith(prefix):
            return None
        try:
            return int(action_id[len(prefix):])
        except ValueError:
            return None

    def _card_display_text(self, locale: str, card_face: str | None) -> str:
        if not card_face:
            return Localization.get(locale, "sorry-card-none")
        if card_face == "sorry":
            return Localization.get(locale, "sorry-card-sorry")
        return card_face

    def _phase_message_key(self) -> str:
        return {
            "draw": "sorry-phase-draw",
            "choose_move": "sorry-phase-choose-move",
            "choose_split": "sorry-phase-choose-split",
            "resolving": "sorry-phase-resolving",
        }.get(self.game_state.turn_phase, "sorry-phase-resolving")

    def create_turn_action_set(self, player: SorryPlayer) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="draw_card",
                label=Localization.get(locale, "sorry-draw-card"),
                handler="_action_draw_card",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                show_in_actions_menu=False,
            )
        )
        self._sync_turn_actions(player, action_set)
        return action_set

    def create_standard_action_set(self, player: SorryPlayer) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        for action in [
            Action(
                id="check_board",
                label=Localization.get(locale, "sorry-check-board"),
                handler="_action_check_board",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_board_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_pawns",
                label=Localization.get(locale, "sorry-check-pawns"),
                handler="_action_check_pawns",
                is_enabled="_is_player_info_enabled",
                is_hidden="_is_check_pawns_hidden",
            ),
            Action(
                id="check_card",
                label=Localization.get(locale, "sorry-check-card"),
                handler="_action_check_card",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_card_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_status",
                label=Localization.get(locale, "sorry-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            ),
        ]:
            action_set.add(action)

        user = self.get_user(player)
        if self.is_touch_client(user):
            target_order = [
                "check_board",
                "check_pawns",
                "check_card",
                "check_status",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("d", "Draw card", ["draw_card"], state=KeybindState.ACTIVE)
        self.define_keybind("space", "Draw card", ["draw_card"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "v",
            "Read board",
            ["check_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind("p", "Check your pawns", ["check_pawns"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "c",
            "Check current card",
            ["check_card"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        for slot in range(1, 10):
            self.define_keybind(
                str(slot),
                f"Choose move {slot}",
                [f"move_slot_{slot}"],
                state=KeybindState.ACTIVE,
            )

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

    def _sync_turn_actions(
        self,
        player: Player,
        action_set: ActionSet | None = None,
    ) -> None:
        turn_set = action_set or self.get_action_set(player, "turn")
        if turn_set is None:
            return

        locale = self._player_locale(player)
        turn_set.remove_by_prefix("move_slot_")
        active_moves = self._active_move_list(player)
        for index in range(1, len(active_moves) + 1):
            turn_set.add(
                Action(
                    id=f"move_slot_{index}",
                    label=Localization.get(locale, "sorry-move-slot", slot=index),
                    handler="_action_choose_move",
                    is_enabled="_is_move_slot_enabled",
                    is_hidden="_is_move_slot_hidden",
                    get_label="_get_move_slot_label",
                    show_in_actions_menu=False,
                )
            )

        order = ["draw_card"]
        order.extend(aid for aid in turn_set._order if aid.startswith("move_slot_"))
        turn_set._order = [aid for aid in order if turn_set.get_action(aid)]

    def _sync_standard_actions(self, player: Player) -> None:
        action_set = self.get_action_set(player, "standard")
        if action_set is None:
            return
        user = self.get_user(player)
        if self.is_touch_client(user):
            target_order = [
                "check_board",
                "check_pawns",
                "check_card",
                "check_status",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_player_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-not-available"
        return None

    def _web_visibility(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_board_hidden(self, player: Player) -> Visibility:
        return self._web_visibility(player)

    def _is_check_pawns_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._web_visibility(player)

    def _is_check_card_hidden(self, player: Player) -> Visibility:
        return self._web_visibility(player)

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        return self._web_visibility(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        if self.game_state.turn_phase != "draw":
            return "action-not-available"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        if self.game_state.turn_phase != "draw":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _active_move_list(self, player: Player) -> list[SorryMove]:
        if self.game_state.turn_phase == "choose_split":
            return self._get_current_split_options(player)
        return self._get_current_legal_moves(player)

    def _is_move_slot_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "action-not-available"
        if self.game_state.turn_phase not in {"choose_move", "choose_split"}:
            return "action-not-available"
        slot = self._parse_move_slot(action_id)
        if slot is None or slot > len(self._active_move_list(player)):
            return "action-not-available"
        return None

    def _is_move_slot_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.current_player != player:
            return Visibility.HIDDEN
        if self.is_sequence_gameplay_locked():
            return Visibility.HIDDEN
        if self.game_state.turn_phase not in {"choose_move", "choose_split"}:
            return Visibility.HIDDEN
        slot = self._parse_move_slot(action_id)
        if slot is None or slot > len(self._active_move_list(player)):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_move_slot_label(self, player: Player, action_id: str) -> str:
        slot = self._parse_move_slot(action_id)
        locale = self._player_locale(player)
        if slot is None:
            return Localization.get(locale, "sorry-move-slot-fallback")
        active_moves = self._active_move_list(player)
        if 1 <= slot <= len(active_moves):
            return self._move_label(locale, active_moves[slot - 1])
        return Localization.get(locale, "sorry-move-slot", slot=slot)

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.round = 1
        self.winner_name = ""
        self.ended_due_to_empty_deck = False
        self.cancel_all_sequences()
        self._sync_table_status()

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([player.name for player in active_players])
        self._team_manager.reset_all_scores()

        rules = self._get_rules_profile()
        self.game_state = build_initial_game_state(
            [player.id for player in active_players],
            pawns_per_player=rules.pawns_per_player,
            faster_setup_one_pawn_out=self.options.faster_setup_one_pawn_out,
        )

        for index, player in enumerate(active_players):
            player.color = PLAYER_COLORS[index]
            player_state = self._get_player_state(player)
            if player_state:
                player.pawns_in_start = sum(1 for pawn in player_state.pawns if pawn.zone == "start")
                player.pawns_in_home = sum(1 for pawn in player_state.pawns if pawn.zone == "home")

        self._sync_player_counts()
        self.play_music("game_pig/mus.ogg")
        player_names = [p.name for p in active_players]
        for player in self.players:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "sorry-game-started",
                    buffer="game",
                    players=Localization.format_list_and(user.locale, player_names),
                )
        self._start_turn(announce=True)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        self.process_sequences()
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        if self.game_state.turn_phase == "draw":
            return "draw_card"

        if self.game_state.turn_phase == "choose_split":
            return self._choose_bot_move_slot(player, self._get_current_split_options(player))

        if self.game_state.turn_phase == "choose_move":
            return self._choose_bot_move_slot(player, self._get_current_legal_moves(player))

        return None

    def _choose_bot_move_slot(
        self,
        player: Player,
        options: list[SorryMove],
    ) -> str | None:
        self._sync_turn_actions(player)
        player_state = self._get_player_state(player)
        if not options or player_state is None:
            return None
        selected = choose_move(self.game_state, player_state, options, self._get_rules_profile())
        if selected is None:
            return None
        slot_index = next(
            (idx for idx, move in enumerate(options, start=1) if move.action_id == selected.action_id),
            None,
        )
        return f"move_slot_{slot_index}" if slot_index is not None else None

    def _start_turn(self, announce: bool = True) -> None:
        self.cancel_sequences_by_tag("turn_flow")
        self.game_state.turn_phase = "draw"
        self.game_state.current_card = None
        self.game_state.split_pawn_a = None
        self.game_state.split_pawn_b = None
        if announce:
            self.announce_turn()
        self.rebuild_all_menus()
        self._queue_current_bot()

    def _end_turn_after_card(self, card_face: str) -> None:
        self.cancel_sequences_by_tag("turn_flow")
        self.game_state.turn_number += 1
        self.game_state.turn_phase = "draw"
        self.game_state.current_card = None
        self.game_state.split_pawn_a = None
        self.game_state.split_pawn_b = None
        if card_face == "2" and self._get_rules_profile().card_two_grants_extra_turn():
            current = self.current_player
            if current:
                self.broadcast_personal_l(
                    current,
                    "sorry-you-extra-turn",
                    "sorry-player-extra-turn",
                    buffer="game",
                )
            self.announce_turn()
            self.rebuild_all_menus()
            self._queue_current_bot()
            return
        self.advance_turn(announce=True)
        self._queue_current_bot()

    def _queue_current_bot(self) -> None:
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(12, 20))

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        _ = sequence_id
        if callback_id == "after_draw":
            player = self.get_player_by_id(payload["player_id"])
            if player is not None:
                self._handle_after_draw(player, payload["card_face"])
            return

        if callback_id == "resolve_move":
            player = self.get_player_by_id(payload["player_id"])
            if player is None:
                return
            move = SorryMove.from_dict(payload["move"])
            captures = [CaptureEvent.from_dict(item) for item in payload["captures"]]
            self._resolve_selected_move(player, move, payload["card_face"], captures)

    def _broadcast_personal_card_message(
        self,
        player: Player,
        personal_message_id: str,
        others_message_id: str,
        card_face: str,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            card_text = self._card_display_text(user.locale, card_face)
            if listener.id == player.id:
                user.speak_l(personal_message_id, buffer="game", card=card_text)
            else:
                user.speak_l(
                    others_message_id,
                    buffer="game",
                    player=player.name,
                    card=card_text,
                )

    def _handle_deck_exhaustion(self) -> None:
        self.ended_due_to_empty_deck = True
        self.game_state.turn_phase = "resolving"
        self.broadcast_l("sorry-deck-exhausted", buffer="game")
        self.finish_game()

    def _get_current_legal_moves(self, player: Player) -> list[SorryMove]:
        if self.game_state.turn_phase != "choose_move":
            return []
        player_state = self._get_player_state(player)
        card_face = self.game_state.current_card
        if player_state is None or card_face is None:
            return []
        return generate_legal_moves(self.game_state, player_state, card_face, self._get_rules_profile())

    def _get_current_split_options(self, player: Player) -> list[SorryMove]:
        if self.game_state.turn_phase != "choose_split":
            return []
        if self.game_state.split_pawn_a is None or self.game_state.split_pawn_b is None:
            return []
        player_state = self._get_player_state(player)
        if player_state is None:
            return []
        return generate_split_options_for_pair(
            player_state,
            self.game_state.split_pawn_a,
            self.game_state.split_pawn_b,
        )

    def _sync_player_counts(self) -> None:
        for player in self.get_active_players():
            player_state = self._get_player_state(player)
            if player_state is None:
                continue
            player.pawns_in_start = sum(1 for pawn in player_state.pawns if pawn.zone == "start")
            player.pawns_in_home = sum(1 for pawn in player_state.pawns if pawn.zone == "home")
            team = self._team_manager.get_team(player.name)
            if team is not None:
                team.total_score = player.pawns_in_home

    def _has_player_won(self, player: Player) -> bool:
        player_state = self._get_player_state(player)
        return bool(player_state and all(pawn.zone == "home" for pawn in player_state.pawns))

    def _build_draw_sequence(self, player: Player, card_face: str) -> list[SequenceBeat]:
        draw_sound = f"game_squares/draw{random.randint(1, 3)}.ogg"
        return [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(draw_sound)],
                delay_after_ticks=6,
            ),
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "after_draw",
                        {"player_id": player.id, "card_face": card_face},
                    )
                ]
            ),
        ]

    def _build_move_sequence(
        self,
        player: Player,
        move: SorryMove,
        card_face: str,
        captures: list[CaptureEvent],
    ) -> list[SequenceBeat]:
        beats: list[SequenceBeat] = []

        if move.move_type in {"forward", "backward", "split7", "sorry_fallback_forward"}:
            step_count = 1
            if move.move_type == "split7":
                step_count = (move.steps or 0) + (move.secondary_steps or 0)
            else:
                step_count = max(1, move.steps or 0)
            for _ in range(step_count):
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(
                                f"game_squares/token{random.randint(1, 10)}.ogg"
                            )
                        ],
                        delay_after_ticks=2,
                    )
                )
        elif move.move_type in {"start", "swap"}:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op("game_squares/token1.ogg")],
                    delay_after_ticks=2,
                )
            )
        elif move.move_type == "sorry":
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op("game_chess/capture1.ogg")],
                    delay_after_ticks=2,
                )
            )

        if captures:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            f"game_chess/capture{random.randint(1, 2)}.ogg"
                        )
                    ],
                    delay_after_ticks=2,
                )
            )

        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "resolve_move",
                        {
                            "player_id": player.id,
                            "move": move.to_dict(),
                            "card_face": card_face,
                            "captures": [capture.to_dict() for capture in captures],
                        },
                    )
                ]
            )
        )
        return beats

    def _move_label(self, locale: str, move: SorryMove) -> str:
        if move.move_type == "start":
            return Localization.get(locale, "sorry-move-start", pawn=move.pawn_index)
        if move.move_type in {"forward", "sorry_fallback_forward"}:
            return Localization.get(
                locale,
                "sorry-move-forward",
                pawn=move.pawn_index,
                steps=move.steps or 0,
            )
        if move.move_type == "backward":
            return Localization.get(
                locale,
                "sorry-move-backward",
                pawn=move.pawn_index,
                steps=move.steps or 0,
            )
        if move.move_type == "swap":
            target_name = self._target_player_name(locale, move.target_player_id)
            return Localization.get(
                locale,
                "sorry-move-swap",
                pawn=move.pawn_index,
                target_player=target_name,
                target_pawn=move.target_pawn_index,
            )
        if move.move_type == "sorry":
            target_name = self._target_player_name(locale, move.target_player_id)
            return Localization.get(
                locale,
                "sorry-move-sorry",
                pawn=move.pawn_index,
                target_player=target_name,
                target_pawn=move.target_pawn_index,
            )
        if move.move_type == "split7_pick":
            return Localization.get(
                locale,
                "sorry-move-split7-pick",
                pawn_a=move.pawn_index,
                pawn_b=move.secondary_pawn_index,
            )
        if move.move_type == "split7":
            return Localization.get(
                locale,
                "sorry-move-split7-option",
                pawn_a=move.pawn_index,
                steps_a=move.steps or 0,
                pawn_b=move.secondary_pawn_index,
                steps_b=move.secondary_steps or 0,
            )
        return Localization.get(locale, "sorry-move-slot-fallback")

    def _target_player_name(self, locale: str, player_id: str | None) -> str:
        target = self.get_player_by_id(player_id) if player_id else None
        return target.name if target else Localization.get(locale, "unknown-player")

    def _describe_pawn(self, locale: str, player_state: SorryPlayerState, pawn_index: int) -> str:
        pawn = player_state.pawns[pawn_index - 1]
        if pawn.zone == "start":
            return Localization.get(locale, "sorry-zone-start")
        if pawn.zone == "track":
            return Localization.get(locale, "sorry-zone-track", position=(pawn.track_position or 0) + 1)
        if pawn.zone == "home_path":
            return Localization.get(locale, "sorry-zone-home-path", steps=pawn.home_steps)
        return Localization.get(locale, "sorry-zone-home")

    def _move_destination(self, locale: str, player: Player, pawn_index: int | None) -> str:
        player_state = self._get_player_state(player)
        if player_state is None or pawn_index is None:
            return Localization.get(locale, "sorry-location-start")
        pawn = player_state.pawns[pawn_index - 1]
        if pawn.zone == "start":
            return Localization.get(locale, "sorry-location-start")
        if pawn.zone == "track":
            return Localization.get(
                locale,
                "sorry-location-track",
                position=(pawn.track_position or 0) + 1,
            )
        if pawn.zone == "home_path":
            return Localization.get(
                locale,
                "sorry-location-home-path",
                steps=pawn.home_steps,
            )
        return Localization.get(locale, "sorry-location-home")

    def _color_name(self, locale: str, color: str) -> str:
        return Localization.get(locale, f"sorry-color-{color}")

    def _player_color_label(self, locale: str, player: SorryPlayer) -> str:
        return Localization.get(
            locale,
            "sorry-board-player-color",
            player=player.name,
            color=self._color_name(locale, player.color),
        )

    def _describe_pawn_compact(
        self,
        locale: str,
        player: SorryPlayer,
        pawn_index: int,
    ) -> str:
        return Localization.get(
            locale,
            "sorry-board-summary-item",
            pawn=pawn_index,
            location=self._move_destination(locale, player, pawn_index),
        )

    def _slide_owner_color(self, square: int) -> str | None:
        normalized_square = normalize_track_position(square)
        for seat_index, color in enumerate(PLAYER_COLORS):
            base = seat_index * 15
            for offset, length in ((1, 3), (9, 4)):
                start = normalize_track_position(base + offset)
                slide_positions = {
                    normalize_track_position(start + step) for step in range(length + 1)
                }
                if normalized_square in slide_positions:
                    return color
        return None

    def _area_pawn_labels(self, locale: str, pawns: list[int]) -> str:
        if not pawns:
            return Localization.get(locale, "sorry-board-area-empty")
        return Localization.format_list_and(
            locale,
            [
                Localization.get(locale, "sorry-board-area-pawn", pawn=pawn_index)
                for pawn_index in pawns
            ],
        )

    def _announce_move(self, player: Player, move: SorryMove) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            locale = user.locale
            kwargs = {}
            personal_message_id = ""
            others_message_id = ""
            if move.move_type == "start":
                personal_message_id = "sorry-you-play-start"
                others_message_id = "sorry-play-start"
                kwargs = {
                    "pawn": move.pawn_index,
                    "destination": self._move_destination(locale, player, move.pawn_index),
                }
            elif move.move_type in {"forward", "sorry_fallback_forward"}:
                personal_message_id = "sorry-you-play-forward"
                others_message_id = "sorry-play-forward"
                kwargs = {
                    "pawn": move.pawn_index,
                    "steps": move.steps or 0,
                    "destination": self._move_destination(locale, player, move.pawn_index),
                }
            elif move.move_type == "backward":
                personal_message_id = "sorry-you-play-backward"
                others_message_id = "sorry-play-backward"
                kwargs = {
                    "pawn": move.pawn_index,
                    "steps": move.steps or 0,
                    "destination": self._move_destination(locale, player, move.pawn_index),
                }
            elif move.move_type == "swap":
                personal_message_id = "sorry-you-play-swap"
                others_message_id = "sorry-play-swap"
                kwargs = {
                    "pawn": move.pawn_index,
                    "target_player": self._target_player_name(locale, move.target_player_id),
                    "target_pawn": move.target_pawn_index,
                    "destination": self._move_destination(locale, player, move.pawn_index),
                }
            elif move.move_type == "sorry":
                personal_message_id = "sorry-you-play-sorry"
                others_message_id = "sorry-play-sorry"
                kwargs = {
                    "pawn": move.pawn_index,
                    "target_player": self._target_player_name(locale, move.target_player_id),
                    "target_pawn": move.target_pawn_index,
                    "destination": self._move_destination(locale, player, move.pawn_index),
                }
            elif move.move_type == "split7":
                personal_message_id = "sorry-you-play-split7"
                others_message_id = "sorry-play-split7"
                kwargs = {
                    "pawn_a": move.pawn_index,
                    "steps_a": move.steps or 0,
                    "destination_a": self._move_destination(locale, player, move.pawn_index),
                    "pawn_b": move.secondary_pawn_index,
                    "steps_b": move.secondary_steps or 0,
                    "destination_b": self._move_destination(locale, player, move.secondary_pawn_index),
                }
            else:
                continue

            if listener.id == player.id:
                user.speak_l(personal_message_id, buffer="game", **kwargs)
            else:
                user.speak_l(others_message_id, buffer="game", player=player.name, **kwargs)
        return

    def _announce_captures(self, mover: Player, captures: list[CaptureEvent]) -> None:
        for capture in captures:
            target = self.get_player_by_id(capture.captured_player_id)
            if target is None:
                continue
            if target.id == mover.id:
                mover_user = self.get_user(mover)
                if mover_user:
                    mover_user.speak_l(
                        "sorry-you-bumped-own-pawn",
                        buffer="game",
                        pawn=capture.captured_pawn_index,
                    )
                for player in self.players:
                    if player.id == mover.id:
                        continue
                    user = self.get_user(player)
                    if user:
                        user.speak_l(
                            "sorry-player-bumped-own-pawn",
                            buffer="game",
                            player=mover.name,
                            pawn=capture.captured_pawn_index,
                        )
                continue
            target_user = self.get_user(target)
            if target_user:
                target_user.speak_l(
                    "sorry-your-pawn-captured",
                    buffer="game",
                    pawn=capture.captured_pawn_index,
                    by_player=mover.name,
                )
            mover_user = self.get_user(mover)
            if mover_user:
                mover_user.speak_l(
                    "sorry-you-captured-pawn",
                    buffer="game",
                    target_player=target.name,
                    pawn=capture.captured_pawn_index,
                )
            for player in self.players:
                if player.id in {mover.id, capture.captured_player_id}:
                    continue
                user = self.get_user(player)
                if user:
                    user.speak_l(
                        "sorry-pawn-captured",
                        buffer="game",
                        player=mover.name,
                        target_player=target.name,
                        pawn=capture.captured_pawn_index,
                    )

    def _announce_home_arrivals(self, player: Player, move: SorryMove) -> None:
        player_state = self._get_player_state(player)
        if player_state is None:
            return
        for pawn_index in [move.pawn_index, move.secondary_pawn_index]:
            if pawn_index is None or pawn_index < 1 or pawn_index > len(player_state.pawns):
                continue
            pawn = player_state.pawns[pawn_index - 1]
            if pawn.zone != "home":
                continue
            self.play_sound("mention.ogg")
            self.broadcast_personal_l(
                player,
                "sorry-you-pawn-home",
                "sorry-pawn-home",
                buffer="game",
                pawn=pawn_index,
            )

    def _apply_selected_move(self, player: Player, move: SorryMove, card_face: str) -> None:
        player_state = self._get_player_state(player)
        if player_state is None:
            return
        captures = apply_move(self.game_state, player_state, move, self._get_rules_profile())
        self._sync_player_counts()
        self.game_state.turn_phase = "resolving"
        self.rebuild_all_menus()
        self.start_sequence(
            "turn_flow",
            self._build_move_sequence(player, move, card_face, captures),
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _resolve_selected_move(
        self,
        player: Player,
        move: SorryMove,
        card_face: str,
        captures: list[CaptureEvent],
    ) -> None:
        self._announce_move(player, move)
        self._announce_captures(player, captures)
        self._announce_home_arrivals(player, move)
        if self._has_player_won(player):
            self.winner_name = player.name
            self.play_sound("game_pig/wingame.ogg")
            self.broadcast_l("game-winner", buffer="game", player=player.name)
            self.finish_game()
            return
        discard_current_card(self.game_state)
        self._end_turn_after_card(card_face)

    def _enter_choose_split(self, player: Player, move: SorryMove) -> None:
        self.game_state.turn_phase = "choose_split"
        self.game_state.split_pawn_a = move.pawn_index
        self.game_state.split_pawn_b = move.secondary_pawn_index
        options = self._get_current_split_options(player)
        if len(options) == 1 and self.options.auto_apply_single_move:
            card_face = self.game_state.current_card or "0"
            self._apply_selected_move(player, options[0], card_face)
            return
        user = self.get_user(player)
        if user:
            user.speak_l("sorry-choose-split", buffer="game")
        self.rebuild_all_menus()
        self._queue_current_bot()

    def _enter_choose_move(self, player: Player, legal_moves: list[SorryMove]) -> None:
        if len(legal_moves) == 1 and self.options.auto_apply_single_move:
            only_move = legal_moves[0]
            if only_move.move_type == "split7_pick":
                self._enter_choose_split(player, only_move)
                return
            self._apply_selected_move(player, only_move, self.game_state.current_card or "0")
            return
        self.game_state.turn_phase = "choose_move"
        user = self.get_user(player)
        if user:
            user.speak_l("sorry-choose-move", buffer="game")
        self.rebuild_all_menus()
        self._queue_current_bot()

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        _ = action_id
        if self._is_draw_enabled(player) is not None:
            return

        card_face = draw_next_card(self.game_state)
        if card_face is None:
            self._handle_deck_exhaustion()
            return

        self.game_state.turn_phase = "resolving"
        self.rebuild_all_menus()
        self.start_sequence(
            "turn_flow",
            self._build_draw_sequence(player, card_face),
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _handle_after_draw(self, player: Player, card_face: str) -> None:
        self._broadcast_personal_card_message(
            player,
            "sorry-you-draw-announcement",
            "sorry-draw-announcement",
            card_face,
        )

        player_state = self._get_player_state(player)
        legal_moves = (
            generate_legal_moves(
                self.game_state,
                player_state,
                card_face,
                self._get_rules_profile(),
            )
            if player_state is not None
            else []
        )

        if not legal_moves:
            self._broadcast_personal_card_message(
                player,
                "sorry-you-no-legal-moves",
                "sorry-no-legal-moves",
                card_face,
            )
            discard_current_card(self.game_state)
            self._end_turn_after_card(card_face)
            return

        self._enter_choose_move(player, legal_moves)

    def _action_choose_move(self, player: Player, action_id: str) -> None:
        if self._is_move_slot_enabled(player, action_id=action_id) is not None:
            return

        slot = self._parse_move_slot(action_id)
        if slot is None:
            return

        active_moves = self._active_move_list(player)
        if slot < 1 or slot > len(active_moves):
            return
        move = active_moves[slot - 1]

        if move.move_type == "split7_pick":
            self._enter_choose_split(player, move)
            return

        self._apply_selected_move(player, move, self.game_state.current_card or "0")

    def _action_check_board(self, player: Player, action_id: str) -> None:
        _ = action_id
        locale = self._player_locale(player)
        lines: list[str] = []
        if isinstance(player, SorryPlayer) and not player.is_spectator and player.color:
            lines.append(
                Localization.get(
                    locale,
                    "sorry-board-your-color",
                    color=self._color_name(locale, player.color),
                )
            )
        lines.append(Localization.get(locale, "sorry-board-summary-heading"))
        for ordered_id in self.game_state.player_order:
            player_state = self.game_state.player_states.get(ordered_id)
            target_player = self.get_player_by_id(ordered_id)
            if player_state is None or target_player is None or not isinstance(target_player, SorryPlayer):
                continue
            pawn_summaries = [
                self._describe_pawn_compact(locale, target_player, pawn.pawn_index)
                for pawn in player_state.pawns
            ]
            lines.append(
                Localization.get(
                    locale,
                    "sorry-board-summary-line",
                    player=target_player.name,
                    color=self._color_name(locale, target_player.color),
                    pawns=Localization.format_list_and(locale, pawn_summaries),
                )
            )

        lines.append(Localization.get(locale, "sorry-board-track-heading"))
        for square in range(TRACK_LENGTH):
            status_parts: list[str] = []
            slide_owner = self._slide_owner_color(square)
            if slide_owner:
                status_parts.append(
                    Localization.get(
                        locale,
                        "sorry-board-square-slide",
                        color=self._color_name(locale, slide_owner),
                    )
                )
            status_parts.extend(self._board_square_tokens(locale, square))
            if not status_parts:
                status = Localization.get(locale, "sorry-board-square-empty")
            else:
                status = ", ".join(status_parts)
            lines.append(
                Localization.get(
                    locale,
                    "sorry-board-square-line",
                    square=square + 1,
                    status=status,
                )
            )

        lines.append(Localization.get(locale, "sorry-board-private-areas-heading"))
        for ordered_id in self.game_state.player_order:
            player_state = self.game_state.player_states.get(ordered_id)
            target_player = self.get_player_by_id(ordered_id)
            if player_state is None or target_player is None or not isinstance(target_player, SorryPlayer):
                continue
            lines.append(
                Localization.get(
                    locale,
                    "sorry-board-start-line",
                    player=target_player.name,
                    color=self._color_name(locale, target_player.color),
                    pawns=self._area_pawn_labels(
                        locale,
                        [pawn.pawn_index for pawn in player_state.pawns if pawn.zone == "start"],
                    ),
                )
            )
            for safety_space in range(1, 6):
                lines.append(
                    Localization.get(
                        locale,
                        "sorry-board-safety-line",
                        player=target_player.name,
                        color=self._color_name(locale, target_player.color),
                        space=safety_space,
                        pawns=self._area_pawn_labels(
                            locale,
                            [
                                pawn.pawn_index
                                for pawn in player_state.pawns
                                if pawn.zone == "home_path" and pawn.home_steps == safety_space
                            ],
                        ),
                    )
                )
            lines.append(
                Localization.get(
                    locale,
                    "sorry-board-home-line",
                    player=target_player.name,
                    color=self._color_name(locale, target_player.color),
                    pawns=self._area_pawn_labels(
                        locale,
                        [pawn.pawn_index for pawn in player_state.pawns if pawn.zone == "home"],
                    ),
                )
            )
        self.status_box(player, lines)

    def _board_square_tokens(self, locale: str, square: int) -> list[str]:
        tokens: list[str] = []
        normalized_square = normalize_track_position(square)
        for ordered_id in self.game_state.player_order:
            player_state = self.game_state.player_states.get(ordered_id)
            target_player = self.get_player_by_id(ordered_id)
            if player_state is None or target_player is None:
                continue
            for pawn in player_state.pawns:
                if pawn.zone != "track" or pawn.track_position is None:
                    continue
                if normalize_track_position(pawn.track_position) != normalized_square:
                    continue
                tokens.append(
                    Localization.get(
                        locale,
                        "sorry-board-square-token",
                        pawn=pawn.pawn_index,
                        player=target_player.name,
                    )
                )
        return tokens

    def _action_check_pawns(self, player: Player, action_id: str) -> None:
        _ = action_id
        player_state = self._get_player_state(player)
        if player_state is None:
            return
        user = self.get_user(player)
        if not user:
            return
        for pawn in player_state.pawns:
            user.speak_l(
                "sorry-view-your-pawn",
                buffer="game",
                pawn=pawn.pawn_index,
                zone=self._describe_pawn(user.locale, player_state, pawn.pawn_index),
            )

    def _action_check_card(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "sorry-current-card",
            buffer="game",
            card=self._card_display_text(user.locale, self.game_state.current_card),
        )

    def _action_check_status(self, player: Player, action_id: str) -> None:
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        locale = self._player_locale(player)
        current = self.current_player
        lines = [
            Localization.get(locale, "sorry-status-turn-number", count=self.game_state.turn_number),
            Localization.get(
                locale,
                "sorry-status-phase",
                phase=Localization.get(locale, self._phase_message_key()),
            ),
            Localization.get(
                locale,
                "sorry-status-current-card",
                card=self._card_display_text(locale, self.game_state.current_card),
            ),
        ]
        if current:
            lines.append(Localization.get(locale, "sorry-status-current-player", player=current.name))
        for line in lines:
            user.speak(line, buffer="game")

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
        for index, (name, score) in enumerate(sorted_scores, 1):
            lines.append(
                Localization.get(
                    locale,
                    "sorry-end-score-line",
                    index=index,
                    player=name,
                    count=score,
                )
            )
        return lines

    def build_game_result(self) -> GameResult:
        final_scores = {player.name: player.pawns_in_home for player in self.get_active_players()}
        winner = max(self.get_active_players(), key=lambda player: player.pawns_in_home, default=None)
        winner_name = None if self.ended_due_to_empty_deck else (self.winner_name or (winner.name if winner else None))
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
                for player in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner_name,
                "final_scores": final_scores,
                "ended_due_to_empty_deck": self.ended_due_to_empty_deck,
            },
        )
