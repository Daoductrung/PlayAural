"""Shared engine for the Truco family: Argentine, Paulista, and Valencian.

A variant subclasses ``TrucoEngine`` and sets the class-level configuration
(ladder, calls, deck, scoring structure) and the few hooks that differ.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar

from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ..base import Game, GameOptions, Player
from . import audio, cards, rules
from .bot import choose_action as bot_choose_action
from .cards import TrucoCard

HAND_SIZE = 3
NEXT_HAND_SEQUENCE_ID = "truco_next_hand"
NEXT_HAND_SEQUENCE_TAG = "truco_hand_transition"
NEXT_HAND_DELAY_TICKS = 3 * 20
BOT_THINK_TICKS = 16
BOT_FLOR_WINDOW_TICKS = 60

CARD_ACTION_PREFIX = "play_"
ENVIDO_CALLS = (rules.ENVIDO, rules.REAL_ENVIDO, rules.FALTA_ENVIDO)
FLOR_CALLS = (rules.CONTRAFLOR, rules.CONTRAFLOR_AL_RESTO)
ANSWER_ACTIONS = ["accept", "decline"]
CARD_INFO_GESTURE = "card_info_gesture"
ONZE = "onze"

CALL_ACTIONS = {
    "call_truco": "truco",
    "call_envido": rules.ENVIDO,
    "call_real_envido": rules.REAL_ENVIDO,
    "call_falta_envido": rules.FALTA_ENVIDO,
    "call_contraflor": rules.CONTRAFLOR,
    "call_contraflor_al_resto": rules.CONTRAFLOR_AL_RESTO,
}
CALL_ACTION_ORDER = [
    "call_envido",
    "call_real_envido",
    "call_falta_envido",
    "call_contraflor",
    "call_contraflor_al_resto",
    "call_truco",
]

# Calls shared by every variant; a variant may extend or override these maps.
BASE_CALL_KEYS = {
    "truco": "truco-call-truco",
    "retruco": "truco-call-retruco",
    "valecuatro": "truco-call-valecuatro",
    rules.ENVIDO: "truco-call-envido",
    rules.REAL_ENVIDO: "truco-call-real-envido",
    rules.FALTA_ENVIDO: "truco-call-falta-envido",
    rules.CONTRAFLOR: "truco-call-contraflor",
    rules.CONTRAFLOR_AL_RESTO: "truco-call-contraflor-al-resto",
}


@dataclass
class TrucoPlayer(Player):
    hand: list[TrucoCard] = field(default_factory=list)
    dealt: list[TrucoCard] = field(default_factory=list)
    folded: bool = False
    has_flor: bool = False


@dataclass
class TablePlay:
    player_id: str
    card: TrucoCard


@dataclass
class Reveal:
    kind: str
    player_id: str
    card_ids: list[int] = field(default_factory=list)
    value: int = 0


@dataclass
class TrucoEngine(Game):
    """Shared Truco engine.

    A variant subclasses this, declares its options, identity and deck, and
    overrides the class-level rules and hooks below. The attributes in capitals
    are configuration, not saved state.
    """

    PLAYER_MODES: ClassVar[dict] = {2: "individual", 4: "2v2", 6: "3v3"}
    LADDER = ("truco", "retruco", "valecuatro")
    LEVEL_POINTS: ClassVar[dict] = {"truco": 2, "retruco": 3, "valecuatro": 4}
    LEVEL_DECLINED: ClassVar[dict] = {"truco": 1, "retruco": 2, "valecuatro": 3}
    CALL_KEYS: ClassVar[dict] = dict(BASE_CALL_KEYS)
    CALL_ACTIONS = CALL_ACTIONS
    CALL_ACTION_ORDER = CALL_ACTION_ORDER
    MSG: ClassVar[dict] = {}
    ENVIDO_ENABLED = True
    HAS_MAZO = True
    FOLD_SCOPE = "player"
    USES_VIRA = False
    MAO_DE_ONZE = False
    MUSIC = audio.MUSIC_ARGENTINE

    players: list[TrucoPlayer] = field(default_factory=list)
    options: GameOptions = field(default_factory=GameOptions)
    deck: list[TrucoCard] = field(default_factory=list)
    vira: TrucoCard | None = None
    dealer_index: int = -1
    mano_index: int = 0
    trick_leader_index: int = 0
    hand_active: bool = False
    hand_base: int = 1
    no_calls: bool = False
    onze_pending: bool = False
    blind_hand: bool = False
    onze_team: int = -1
    plays: list[list[TablePlay]] = field(default_factory=list)
    trick_results: list[int | None] = field(default_factory=list)
    truco_level: str = ""
    truco_pending: str = ""
    truco_pending_team: int = -1
    truco_pending_by: str = ""
    truco_raiser_team: int = -1
    envido_chain: list[str] = field(default_factory=list)
    envido_pending: bool = False
    envido_pending_team: int = -1
    envido_done: bool = False
    envido_flor: bool = False
    flor_window: bool = False
    flor_pending: str = ""
    flor_pending_team: int = -1
    flor_chain: list[str] = field(default_factory=list)
    reveals: list[Reveal] = field(default_factory=list)
    winner_team_index: int = -1
    came_wins: list[int] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Variant hooks
    # ------------------------------------------------------------------

    def _m(self, key: str) -> str:
        """Message key, replaced when the variant words it differently."""

        return self.MSG.get(key, key)

    def _mr(self, reason):
        """Apply the variant wording to a disabled-action reason (key or key+args)."""

        if isinstance(reason, str):
            return self._m(reason)
        if isinstance(reason, tuple):
            return (self._m(reason[0]), *reason[1:])
        return reason

    def _target_value(self) -> int:
        return int(self.options.target_length)  # type: ignore[attr-defined]

    def _flor_enabled(self) -> bool:
        return False

    def _build_deck(self) -> list[TrucoCard]:
        return cards.build_deck()

    def _power(self, card: TrucoCard) -> int:
        return card.power

    def _bot_strength(self, card: TrucoCard) -> float:
        """Card strength on the Argentine 1-14 scale, for the bot's heuristics."""

        full = self._build_deck()
        beaten = sum(1 for other in full if self._power(other) < self._power(card))
        return 14 * beaten / max(1, len(full) - 1)

    def _sort_card(self, card: TrucoCard) -> tuple:
        return cards.sort_key(card)

    def _format_card(self, card: TrucoCard, locale: str) -> str:
        return cards.format_card(card, locale)

    def _tie_break_team(self, top_plays: list[TablePlay], mano_team: int) -> int:
        """Team that wins a hand whose three tricks are all tied (default: the mano's)."""

        return mano_team

    def _decide_hand(self, mano_team: int) -> int | None:
        return rules.decide_hand(self.trick_results, mano_team)

    def _next_level(self, current: str | None) -> str | None:
        if current is None:
            return self.LADDER[0]
        index = self.LADDER.index(current)
        return self.LADDER[index + 1] if index + 1 < len(self.LADDER) else None

    def _level_points(self, level: str | None, *, accepted: bool = True) -> int:
        if level is None:
            return self.hand_base
        table = self.LEVEL_POINTS if accepted else self.LEVEL_DECLINED
        value = table[level]
        return self._whole_game_points() if value < 0 else value

    def _can_add_envido(self, chain: list[str], call: str) -> bool:
        return rules.can_add_envido_call(chain, call)

    def _envido_accepted_points(self, chain: list[str], falta: int) -> int:
        return rules.envido_accepted_points(chain, falta)

    def _envido_declined_points(self, chain: list[str]) -> int:
        return rules.envido_declined_points(chain)

    def _falta_decides_game(self) -> bool:
        return rules.falta_decides_game(self._scores(), self.target)

    def _falta_points(self, winner_score: int = 0) -> int:
        return rules.falta_envido_points(self._scores(), self.target, winner_score)

    def _extra_info_actions(self) -> list[tuple[str, str, str, bool]]:
        """Extra (id, label key, handler, private) information actions."""

        return []

    def _extra_keybinds(self) -> None:
        return None

    # Games decided over several "cames" (Valencian Truc) override these.
    CAMES_TO_WIN = 1

    def _whole_game_points(self) -> int:
        """Points that stand for the whole game (a joc fora)."""

        return self.target * self.CAMES_TO_WIN

    def _cames(self, team_index: int) -> int:
        if 0 <= team_index < len(self.came_wins):
            return self.came_wins[team_index]
        return 0

    def _final_score(self, team) -> int:
        """Score used for rankings and ratings once the game is over."""

        return team.total_score

    def _on_points_awarded(self, team_index: int, old: int, new: int) -> None:
        """Hook for milestones such as the half-way "buenas" or a Valencian came."""

        if (
            self.target > rules.HALF_POINTS
            and old <= rules.HALF_POINTS < new < self.target
        ):
            self._announce_buenas(team_index)

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return min(cls.PLAYER_MODES)

    @classmethod
    def get_max_players(cls) -> int:
        return max(cls.PLAYER_MODES)

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> TrucoPlayer:
        return TrucoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------

    @property
    def target(self) -> int:
        return self._target_value()

    def _localize(self, player: Player, key: str, **kwargs) -> str:
        user = self.get_user(player)
        return Localization.get(user.locale if user else "en", key, **kwargs)

    def _live(self, player: Player | None) -> bool:
        return (
            isinstance(player, TrucoPlayer)
            and not player.is_spectator
            and not player.folded
        )

    def _order_from(self, start_index: int) -> list[TrucoPlayer]:
        ids = self.turn_player_ids
        count = len(ids)
        result: list[TrucoPlayer] = []
        for offset in range(count):
            player = self.get_player_by_id(ids[(start_index + offset) % count])
            if isinstance(player, TrucoPlayer):
                result.append(player)
        return result

    def _team_index(self, player: Player) -> int:
        return self._team_manager.get_team_index(player.name)

    def _team(self, index: int):
        for team in self._team_manager.teams:
            if team.index == index:
                return team
        return self._team_manager.teams[index]

    def _team_players(
        self, index: int, *, live_only: bool = False
    ) -> list[TrucoPlayer]:
        return [
            player
            for player in self._order_from(self.mano_index)
            if not player.is_spectator
            and self._team_index(player) == index
            and (not live_only or not player.folded)
        ]

    def _scores(self) -> list[int]:
        return [team.total_score for team in self._team_manager.teams]

    @staticmethod
    def _other_team(index: int) -> int:
        return 1 - index

    def _team_label(self, index: int):
        def label(locale: str, index: int = index) -> str:
            return self._team_manager.get_team_name(self._team(index), locale)

        return label

    def _call_text(self, locale: str, call: str) -> str:
        return Localization.get(locale, self.CALL_KEYS[call])

    def _call_arg(self, call: str):
        return lambda locale, call=call: self._call_text(locale, call)

    def _format_cards(self, card_list: list[TrucoCard], locale: str) -> str:
        return ", ".join(self._format_card(card, locale) for card in card_list)

    def _individual(self) -> bool:
        return self.options.team_mode == "individual"

    def _sync_scores(self) -> None:
        for player in self.players:
            if isinstance(player, TrucoPlayer):
                team = self._team_manager.get_team(player.name)
                player.score = team.total_score if team else 0

    def _jolt(self) -> None:
        ticks = BOT_THINK_TICKS
        if self.flor_window:
            ticks = BOT_FLOR_WINDOW_TICKS
        BotHelper.jolt_bots(self, ticks=ticks)

    # ------------------------------------------------------------------
    # Pending calls
    # ------------------------------------------------------------------

    def _pending_kind(self) -> str:
        if self.onze_pending:
            return ONZE
        if self.flor_pending:
            return "flor"
        if self.envido_pending:
            return "envido"
        if self.truco_pending:
            return "truco"
        return ""

    def _pending_call(self) -> str:
        kind = self._pending_kind()
        if kind == ONZE:
            return ONZE
        if kind == "flor":
            return self.flor_chain[-1]
        if kind == "envido":
            return self.envido_chain[-1]
        return self.truco_pending

    def _pending_caller_team(self) -> int:
        kind = self._pending_kind()
        if kind == ONZE:
            return self._other_team(self.onze_team)
        if kind == "flor":
            return self.flor_pending_team
        if kind == "envido":
            return self.envido_pending_team
        return self.truco_pending_team

    def _can_answer(self, player: Player) -> bool:
        kind = self._pending_kind()
        if not kind or not self._live(player):
            return False
        if self._team_index(player) == self._pending_caller_team():
            return False
        return kind != "flor" or player.has_flor  # type: ignore[union-attr]

    def _responders(self) -> list[TrucoPlayer]:
        return [
            player
            for player in self._order_from(self.mano_index)
            if self._can_answer(player)
        ]

    def _pending_block_reason(self, player: Player):
        """Why a player cannot do anything else while a call is waiting."""

        call = self._pending_call()
        if self._can_answer(player):
            return ("truco-error-answer-first", {"call": self._call_arg(call)})
        kind = self._pending_kind()
        if kind == ONZE:
            return (
                "trucobrazilian-error-onze-pending",
                {"team": self._team_label(self.onze_team)},
            )
        team = self._team_index(player)
        caller = self._pending_caller_team()
        if kind == "flor" and team != caller and not getattr(player, "has_flor", False):
            return "truco-error-flor-holders-only"
        return (
            "truco-error-own-team-call",
            {
                "team": self._team_label(self._other_team(caller)),
                "call": self._call_arg(call),
            },
        )

    # ------------------------------------------------------------------
    # Action sets
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: TrucoPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        self._populate_turn_actions(action_set, player)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        def add_info(action_id: str, key: str, handler: str, private: bool) -> None:
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, key),
                    handler=handler,
                    is_enabled=(
                        "_is_private_info_enabled" if private else "_is_info_enabled"
                    ),
                    is_hidden=(
                        "_is_touch_private_info_hidden"
                        if private
                        else "_is_touch_public_info_hidden"
                    ),
                    include_spectators=not private,
                )
            )

        add_info("read_hand", "truco-read-hand", "_action_read_hand", True)
        add_info("read_table", "truco-read-table", "_action_read_table", False)
        add_info("read_calls", "truco-read-calls", "_action_read_calls", False)
        extras = self._extra_info_actions()
        for action_id, key, handler, private in extras:
            add_info(action_id, key, handler, private)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_hand",
                    "read_table",
                    "read_calls",
                    *[extra[0] for extra in extras],
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        active = KeybindState.ACTIVE
        self.define_keybind("h", "Read your cards", ["read_hand"], state=active)
        self.define_keybind(
            "c",
            "Read cards on the table",
            ["read_table"],
            state=active,
            include_spectators=True,
        )
        self.define_keybind(
            "x",
            "Read current calls",
            ["read_calls"],
            state=active,
            include_spectators=True,
        )
        self.define_keybind("q", "Accept", ["accept"], state=active)
        self.define_keybind("n", "Decline", ["decline"], state=active)
        if self.HAS_MAZO:
            self.define_keybind("m", "Fold the hand", ["mazo"], state=active)
        self.define_keybind("u", "Truco and raises", ["call_truco"], state=active)
        if self.ENVIDO_ENABLED:
            self.define_keybind("e", "Envido", ["call_envido"], state=active)
            self.define_keybind("r", "Real envido", ["call_real_envido"], state=active)
            self.define_keybind(
                "a", "Falta envido", ["call_falta_envido"], state=active
            )
        if self._flor_enabled():
            self.define_keybind("f", "Contraflor", ["call_contraflor"], state=active)
            self.define_keybind(
                "shift+f",
                "Contraflor al resto",
                ["call_contraflor_al_resto"],
                state=active,
            )
        self._extra_keybinds()
        # Touch clients send Shift+Enter for press-and-hold / double-tap-and-hold
        # on the focused menu row. The hidden action below is touch-only, so the
        # key is a silent no-op on desktop.
        self.define_keybind(
            "shift+enter", "Card information", [CARD_INFO_GESTURE], state=active
        )

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, TrucoPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        for action_id in list(turn_set._order):
            turn_set.remove(action_id)
        self._populate_turn_actions(turn_set, player)

    def _make_action(self, action_id: str, handler: str, **kwargs) -> Action:
        # Turn actions change with the state of the hand, so none of them
        # belongs in the Escape menu, which lists only the fixed actions.
        return Action(
            id=action_id,
            label=kwargs.pop("label", ""),
            handler=handler,
            is_enabled=kwargs.pop("is_enabled"),
            is_hidden=kwargs.pop("is_hidden"),
            show_in_actions_menu=False,
            **kwargs,
        )

    def _populate_turn_actions(self, turn_set: ActionSet, player: TrucoPlayer) -> None:
        if self.status != "playing" or player.is_spectator or player.folded:
            return
        pending = bool(self._pending_kind())

        def answers() -> None:
            onze = self.onze_pending
            accept_key = (
                "trucobrazilian-action-onze-play"
                if onze
                else self._m("truco-action-accept")
            )
            decline_key = (
                "trucobrazilian-action-onze-run"
                if onze
                else self._m("truco-action-decline")
            )
            turn_set.add(
                self._make_action(
                    "accept",
                    "_action_accept",
                    label=self._localize(player, accept_key),
                    is_enabled="_is_answer_enabled",
                    is_hidden="_is_answer_hidden",
                    get_description="_get_action_description",
                )
            )
            turn_set.add(
                self._make_action(
                    "decline",
                    "_action_decline",
                    label=self._localize(player, decline_key),
                    is_enabled="_is_answer_enabled",
                    is_hidden="_is_answer_hidden",
                    get_description="_get_action_description",
                )
            )

        def hand_cards() -> None:
            for card in self._ordered_hand(player):
                turn_set.add(
                    self._make_action(
                        f"{CARD_ACTION_PREFIX}{card.id}",
                        "_action_play_card",
                        is_enabled="_is_card_enabled",
                        is_hidden="_is_card_hidden",
                        get_label="_get_card_label",
                        get_description="_get_action_description",
                    )
                )

        def calls() -> None:
            for action_id in self.CALL_ACTION_ORDER:
                turn_set.add(
                    self._make_action(
                        action_id,
                        "_action_call",
                        is_enabled="_is_call_enabled",
                        is_hidden="_is_call_hidden",
                        get_label="_get_call_label",
                        get_description="_get_action_description",
                    )
                )

        def mazo() -> None:
            turn_set.add(
                self._make_action(
                    "mazo",
                    "_action_mazo",
                    label=self._localize(player, self._m("truco-action-mazo")),
                    is_enabled="_is_mazo_enabled",
                    is_hidden="_is_mazo_hidden",
                    get_description="_get_action_description",
                )
            )

        def gesture() -> None:
            turn_set.add(
                self._make_action(
                    CARD_INFO_GESTURE,
                    "_action_card_info",
                    label=self._localize(player, "truco-card-info-label"),
                    is_enabled="_is_card_info_enabled",
                    is_hidden="_is_card_info_hidden",
                )
            )

        if pending:
            answers()
            calls()
            if self.HAS_MAZO:
                mazo()
        else:
            hand_cards()
            calls()
            if self.HAS_MAZO:
                mazo()
        gesture()

    # ------------------------------------------------------------------
    # Guards (enabled / hidden callbacks)
    # ------------------------------------------------------------------

    def _hand_guard(self, player: Player):
        if self.status != "playing" or not self.game_active or not self.hand_active:
            return "truco-error-hand-over"
        if not isinstance(player, TrucoPlayer) or player.is_spectator:
            return "action-not-available"
        if player.folded:
            return "truco-error-flor-none"
        return None

    def _answer_error(self, player: Player):
        return self._mr(self._answer_error_raw(player))

    def _answer_error_raw(self, player: Player):
        guard = self._hand_guard(player)
        if guard:
            return guard
        if not self._pending_kind():
            return "truco-error-nothing-to-answer"
        if not self._can_answer(player):
            return self._pending_block_reason(player)
        return None

    def _is_answer_enabled(self, player: Player):
        return self._answer_error(player)

    def _is_answer_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._answer_error(player) is None
            else Visibility.HIDDEN
        )

    def _card_error(self, player: Player, action_id: str):
        return self._mr(self._card_error_raw(player, action_id))

    def _card_error_raw(self, player: Player, action_id: str):
        guard = self._hand_guard(player)
        if guard:
            return guard
        if self._pending_kind():
            return self._pending_block_reason(player)
        current = self.current_player
        if current is not player:
            return (
                "truco-error-not-your-turn",
                {"player": current.name if current else ""},
            )
        if self._card_for_action(player, action_id) is None:
            return "truco-error-card-not-held"
        return None

    def _card_for_action(
        self, player: Player, action_id: str | None
    ) -> TrucoCard | None:
        if not action_id or not action_id.startswith(CARD_ACTION_PREFIX):
            return None
        try:
            card_id = int(action_id[len(CARD_ACTION_PREFIX) :])
        except ValueError:
            return None
        if not isinstance(player, TrucoPlayer):
            return None
        return next((card for card in player.hand if card.id == card_id), None)

    def _is_card_enabled(self, player: Player, *, action_id: str | None = None):
        return self._card_error(player, action_id or "")

    def _is_card_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if (
            self.status != "playing"
            or not self.hand_active
            or not isinstance(player, TrucoPlayer)
            or player.is_spectator
            or player.folded
            or self._pending_kind()
            or self._card_for_action(player, action_id) is None
        ):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _ordered_hand(self, player: TrucoPlayer) -> list[TrucoCard]:
        """Menu order: by strength, or by deal position when the hand is face down."""

        if self.blind_hand:
            order = {card.id: index for index, card in enumerate(player.dealt)}
            return sorted(player.hand, key=lambda card: order.get(card.id, 0))
        return sorted(player.hand, key=self._sort_card)

    def _blind_number(self, player: TrucoPlayer, card: TrucoCard) -> int:
        return next(
            (index for index, held in enumerate(player.dealt, 1) if held.id == card.id),
            0,
        )

    def _get_card_label(self, player: Player, action_id: str) -> str:
        card = self._card_for_action(player, action_id)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if card is None:
            return action_id
        if self.blind_hand and isinstance(player, TrucoPlayer):
            return Localization.get(
                locale,
                "trucobrazilian-action-play-blind",
                number=self._blind_number(player, card),
            )
        return Localization.get(
            locale, "truco-action-play-card", card=self._format_card(card, locale)
        )

    def _envido_open(self) -> bool:
        return (
            self.ENVIDO_ENABLED
            and not self.no_calls
            and not self.envido_done
            and not self.envido_flor
            and not self.truco_level
            and not self.trick_results
        )

    def _call_error(self, player: Player, action_id: str):
        return self._mr(self._call_error_raw(player, action_id))

    def _call_error_raw(self, player: Player, action_id: str):
        guard = self._hand_guard(player)
        if guard:
            return guard
        call = self.CALL_ACTIONS.get(action_id)
        if call is None:
            return "action-not-available"
        assert isinstance(player, TrucoPlayer)
        if self.onze_pending:
            return self._pending_block_reason(player)
        if self.no_calls:
            return "trucobrazilian-error-no-calls"
        team = self._team_index(player)
        if call == "truco":
            return self._truco_call_error(player, team)
        if call in ENVIDO_CALLS:
            return self._envido_call_error(player, team, call)
        return self._flor_call_error(player, team, call)

    def _truco_call_error(self, player: TrucoPlayer, team: int):
        if self.flor_window:
            return "truco-error-flor-window"
        if self.flor_pending or self.envido_pending:
            return self._pending_block_reason(player)
        if self.truco_pending:
            if team == self.truco_pending_team:
                return self._pending_block_reason(player)
            if self._next_level(self.truco_pending) is None:
                return "truco-error-raise-max"
            return None
        if self._next_level(self.truco_level or None) is None:
            return "truco-error-raise-max"
        if self.truco_level and self.truco_raiser_team != team:
            return (
                "truco-error-raise-holder",
                {"team": self._team_label(self.truco_raiser_team)},
            )
        return None

    def _envido_call_error(self, player: TrucoPlayer, team: int, call: str):
        if self.flor_pending:
            return self._pending_block_reason(player)
        if self.envido_pending:
            if team == self.envido_pending_team:
                return self._pending_block_reason(player)
            if not self._can_add_envido(self.envido_chain, call):
                return (
                    "truco-error-envido-cannot-raise",
                    {"call": self._call_arg(call)},
                )
            return None
        if self.envido_flor:
            return "truco-error-envido-flor"
        if self.envido_done:
            return "truco-error-envido-done"
        if self.truco_level:
            return "truco-error-envido-closed"
        if len(player.dealt) - len(player.hand) > 0 or self.trick_results:
            return "truco-error-envido-late"
        if self.truco_pending and team == self.truco_pending_team:
            return self._pending_block_reason(player)
        return None

    def _flor_call_error(self, player: TrucoPlayer, team: int, call: str):
        if not self._flor_enabled():
            return "truco-error-flor-off"
        if not player.has_flor:
            return "truco-error-flor-holders-only"
        if self.flor_pending:
            if team == self.flor_pending_team:
                return self._pending_block_reason(player)
            if (
                call == rules.CONTRAFLOR_AL_RESTO
                and self.flor_pending == rules.CONTRAFLOR
            ):
                return None
            return "action-not-available"
        if not self.flor_window:
            return "truco-error-flor-window-closed"
        return None

    def _is_call_enabled(self, player: Player, *, action_id: str | None = None):
        return self._call_error(player, action_id or "")

    def _is_call_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if self._call_error(player, action_id or "") is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _get_call_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        call = self.CALL_ACTIONS.get(action_id, "truco")
        if call == "truco":
            base = self.truco_pending or self.truco_level or None
            call = self._next_level(base) or self.LADDER[-1]
        return self._call_text(locale, call)

    def _mazo_error(self, player: Player):
        return self._mr(self._mazo_error_raw(player))

    def _mazo_error_raw(self, player: Player):
        guard = self._hand_guard(player)
        if guard:
            return guard
        if not self.HAS_MAZO:
            return "action-not-available"
        if self._pending_kind():
            return self._pending_block_reason(player)
        return None

    def _is_mazo_enabled(self, player: Player):
        return self._mazo_error(player)

    def _is_mazo_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self._mazo_error(player) is None
            else Visibility.HIDDEN
        )

    # Information actions

    def _is_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "truco-error-hand-over"

    def _is_private_info_enabled(self, player: Player) -> str | None:
        if not isinstance(player, TrucoPlayer) or player.is_spectator:
            return "action-not-available"
        return self._is_info_enabled(player)

    def _is_touch_public_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_touch_private_info_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_touch_public_info_hidden(player)

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

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def get_score_target(self) -> int | None:
        return self.target

    # Touch gestures and descriptions

    def _is_card_info_enabled(self, player: Player):
        # Silent no-op on non-touch clients, so Shift+Enter never speaks on desktop.
        if not self.is_touch_client(self.get_user(player)):
            return "action-not-available"
        if (
            self.status != "playing"
            or not isinstance(player, TrucoPlayer)
            or player.is_spectator
            or player.folded
        ):
            return "action-not-available"
        return None

    def _is_card_info_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _card_strength_text(self, card: TrucoCard, locale: str, key: str) -> str:
        full = self._build_deck()
        power = self._power(card)
        beaten = sum(1 for other in full if self._power(other) < power)
        kwargs: dict = {
            "card": self._format_card(card, locale),
            "beats": beaten,
            "total": len(full) - 1,
        }
        if key.endswith("-envido"):
            kwargs["value"] = card.envido_value
        return Localization.get(locale, key, **kwargs)

    def _card_info_text(self, card: TrucoCard, locale: str) -> str:
        key = "truco-card-info-envido" if self.ENVIDO_ENABLED else "truco-card-info"
        return self._card_strength_text(card, locale, key)

    def _action_card_info(self, player: Player, action_id: str) -> None:
        """Touch gesture: speak what the focused turn-menu item is or does.

        Works on cards (strength), calls (value and refusal cost), the answers,
        and the fold. Anything else is a silent no-op.
        """

        user = self.get_user(player)
        if not user or self._is_card_info_enabled(player):
            return
        item_id = self.get_action_context(player).menu_item_id
        if not item_id or item_id == CARD_INFO_GESTURE:
            return
        text = self._get_action_description(player, item_id)
        if text:
            user.speak(text, buffer="game")

    def _call_description(self, locale: str, call: str) -> str | None:
        call_text = self._call_text(locale, call)
        if call in self.LADDER:
            return Localization.get(
                locale,
                "truco-desc-call-ladder",
                call=call_text,
                points=self._level_points(call),
                refused=self._level_points(call, accepted=False),
            )
        if call in ENVIDO_CALLS:
            chain = [*self.envido_chain, call]
            falta = 0
            if call == rules.FALTA_ENVIDO:
                falta = self._falta_points()
            return Localization.get(
                locale,
                "truco-desc-call-envido",
                call=call_text,
                points=self._envido_accepted_points(chain, falta),
                refused=self._envido_declined_points(chain),
            )
        if call in FLOR_CALLS:
            chain = [*self.flor_chain, call]
            return Localization.get(
                locale,
                "truco-desc-call-flor",
                call=call_text,
                points=(
                    self._falta_points()
                    if call == rules.CONTRAFLOR_AL_RESTO
                    else rules.CONTRAFLOR_POINTS
                ),
                refused=rules.flor_declined_points(chain),
            )
        return None

    def _answer_description(self, locale: str, accept: bool) -> str | None:
        kind = self._pending_kind()
        if not kind:
            return None
        if kind == ONZE:
            key = (
                "trucobrazilian-desc-onze-play"
                if accept
                else "trucobrazilian-desc-onze-run"
            )
            return Localization.get(locale, key, points=self._onze_value())
        call = self._pending_call()
        call_text = self._call_text(locale, call)
        if accept:
            return Localization.get(locale, "truco-desc-accept", call=call_text)
        if kind == "truco":
            refused = self._level_points(self.truco_pending, accepted=False)
        elif kind == "envido":
            refused = self._envido_declined_points(self.envido_chain)
        else:
            refused = rules.flor_declined_points(self.flor_chain)
        return Localization.get(
            locale, "truco-desc-decline", call=call_text, points=refused
        )

    def _onze_value(self) -> int:
        return 3

    def _get_action_description(self, player: Player, action_id: str) -> str | None:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if action_id == "accept":
            return self._answer_description(locale, True)
        if action_id == "decline":
            return self._answer_description(locale, False)
        if action_id == "mazo":
            return Localization.get(locale, self._m("truco-desc-mazo"))
        card = self._card_for_action(player, action_id)
        if card is not None:
            if self.blind_hand:
                return Localization.get(locale, "trucobrazilian-desc-blind-card")
            return self._card_info_text(card, locale)
        call = self.CALL_ACTIONS.get(action_id)
        if call is None:
            return None
        if call == "truco":
            base = self.truco_pending or self.truco_level or None
            call = self._next_level(base) or self.LADDER[-1]
        return self._call_description(locale, call)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not isinstance(player, TrucoPlayer):
            return
        if not player.hand:
            user.speak_l("truco-no-cards", buffer="game")
            return
        if self.blind_hand:
            user.speak_l(
                "trucobrazilian-blind-hand", buffer="game", count=len(player.hand)
            )
            return
        user.speak_l(
            "truco-your-cards",
            buffer="game",
            cards=self._format_cards(
                sorted(player.hand, key=self._sort_card), user.locale
            ),
        )
        if self.onze_pending:
            self._speak_partner_cards(player, user)

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        super()._action_check_scores(player, action_id)
        user = self.get_user(player)
        if not user or self.CAMES_TO_WIN <= 1:
            return
        for team in self._team_manager.teams:
            user.speak_l(
                "trucospanish-cames-line",
                buffer="game",
                team=self._team_manager.get_team_name(team, user.locale),
                cames=self._cames(team.index),
            )

    def _speak_partner_cards(self, player: TrucoPlayer, user) -> None:
        """Mão de onze: the side holding 11 may look at each other's cards."""

        if self._team_index(player) != self.onze_team:
            return
        for mate in self._team_players(self.onze_team, live_only=True):
            if mate.id == player.id or not mate.hand:
                continue
            user.speak_l(
                "trucobrazilian-onze-partner-cards",
                buffer="game",
                partner=mate.name,
                cards=self._format_cards(
                    sorted(mate.hand, key=self._sort_card), user.locale
                ),
            )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not any(self.plays):
            user.speak_l("truco-table-empty", buffer="game")
            return
        for number, trick in enumerate(self.plays, 1):
            if not trick:
                continue
            parts = []
            for play in trick:
                owner = self.get_player_by_id(play.player_id)
                parts.append(
                    Localization.get(
                        user.locale,
                        "truco-table-played",
                        player=owner.name if owner else "",
                        card=self._format_card(play.card, user.locale),
                    )
                )
            user.speak_l(
                "truco-table-trick",
                buffer="game",
                trick=number,
                cards=", ".join(parts),
            )

    def _action_read_calls(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.onze_pending:
            user.speak_l(
                "trucobrazilian-status-onze-pending",
                buffer="game",
                team=self._team_manager.get_team_name(
                    self._team(self.onze_team), user.locale
                ),
            )
            return
        if self.no_calls:
            user.speak_l(
                "trucobrazilian-status-no-calls", buffer="game", points=self.hand_base
            )
            return
        if self.truco_pending:
            user.speak_l(
                "truco-status-truco-pending",
                buffer="game",
                call=self._call_text(user.locale, self.truco_pending),
                team=self._team_manager.get_team_name(
                    self._team(self._other_team(self.truco_pending_team)), user.locale
                ),
            )
        elif self.truco_level:
            user.speak_l(
                "truco-status-truco",
                buffer="game",
                call=self._call_text(user.locale, self.truco_level),
                points=self._level_points(self.truco_level),
            )
        else:
            user.speak_l(
                self._m("truco-status-no-truco"), buffer="game", points=self.hand_base
            )
        if self.ENVIDO_ENABLED:
            user.speak_l(
                self._m(
                    "truco-status-envido-open"
                    if self._envido_open()
                    else "truco-status-envido-closed"
                ),
                buffer="game",
            )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        count = len(self.get_active_players())
        expected = self.PLAYER_MODES.get(count)
        if expected is None:
            errors.append((self._m("truco-error-bad-count"), {"count": count}))
        elif self.options.team_mode != expected:
            errors.append(
                (
                    self._m("truco-error-team-mode-count"),
                    {
                        "mode": lambda locale: TeamManager.format_team_mode_for_display(
                            self.options.team_mode, locale
                        ),
                        "count": count,
                    },
                )
            )
        return errors

    def on_start(self) -> None:
        self.cancel_sequences_by_tag(NEXT_HAND_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self.game_active = True
        self.round = 0
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.winner_team_index = -1
        self.came_wins = [0] * len(self._team_manager.teams)
        self.hand_active = False
        self._sync_table_status()
        self.play_music(self.MUSIC)

        active = [p for p in self.get_active_players() if isinstance(p, TrucoPlayer)]
        self._setup_team_manager_for_start(self.options.team_mode, active)
        self._team_manager.reset_all_scores()
        for player in active:
            player.score = 0
            player.folded = False
            player.has_flor = False
            player.hand = []
            player.dealt = []
        self.set_turn_players(self._get_team_turn_players(active))
        self.dealer_index = random.randrange(len(self.turn_player_ids))
        self._announce_game_start()
        self._start_hand(rotate_dealer=False)

    def _announce_game_start(self) -> None:
        if self._flor_enabled():
            key = "truco-game-start-flor"
        else:
            key = self._m("truco-game-start-no-flor")
        self.broadcast_l(key, buffer="game", points=self.target)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if (
            self.game_active
            and self.status == "playing"
            and self.hand_active
            and not self.is_sequence_bot_paused()
        ):
            bot = self._bot_actor()
            if bot is not None:
                BotHelper.process_bot_action(
                    bot,
                    think_fn=lambda: self.bot_think(bot),
                    execute_fn=lambda action_id: self.execute_action(bot, action_id),
                )

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id == NEXT_HAND_SEQUENCE_ID and callback_id == "start_next_hand":
            self._start_hand(rotate_dealer=True)

    def _bot_actor(self) -> TrucoPlayer | None:
        if self._pending_kind():
            responders = self._responders()
            if not responders or any(not p.is_bot for p in responders):
                return None
            return responders[0]
        current = self.current_player
        if isinstance(current, TrucoPlayer) and current.is_bot and self._live(current):
            return current
        return None

    def bot_think(self, player: TrucoPlayer) -> str | None:
        return bot_choose_action(self, player)

    # ------------------------------------------------------------------
    # Hands
    # ------------------------------------------------------------------

    def _reset_hand_state(self) -> None:
        self.plays = [[]]
        self.trick_results = []
        self.truco_level = ""
        self.truco_pending = ""
        self.truco_pending_team = -1
        self.truco_pending_by = ""
        self.truco_raiser_team = -1
        self.envido_chain = []
        self.envido_pending = False
        self.envido_pending_team = -1
        self.envido_done = False
        self.envido_flor = False
        self.flor_window = False
        self.flor_pending = ""
        self.flor_pending_team = -1
        self.flor_chain = []
        self.reveals = []
        self.vira = None
        self.hand_base = 1
        self.no_calls = False
        self.onze_pending = False
        self.onze_team = -1
        self.blind_hand = False

    def _start_hand(self, *, rotate_dealer: bool) -> None:
        self.cancel_sequences_by_tag(NEXT_HAND_SEQUENCE_TAG)
        count = len(self.turn_player_ids)
        if not count:
            return
        if rotate_dealer:
            self.dealer_index = (self.dealer_index + 1) % count
        self.round += 1
        self._reset_hand_state()
        self.blind_hand = self._blind_hand()
        self.mano_index = (self.dealer_index + 1) % count
        self.trick_leader_index = self.mano_index
        self.turn_index = self.mano_index

        self.deck = self._build_deck()
        cards.shuffle(self.deck)
        self.play_sound_family(audio.SHUFFLE_FAMILY)
        order = self._order_from(self.mano_index)
        dealt_count = 0
        for player in order:
            player.folded = False
            dealt = [self.deck.pop() for _ in range(HAND_SIZE)]
            # A face-down hand keeps the random deal order so position reveals nothing.
            player.hand = (
                dealt if self.blind_hand else sorted(dealt, key=self._sort_card)
            )
            player.dealt = list(player.hand)
            player.has_flor = self._flor_enabled() and rules.has_flor(player.hand)
            player.bot_pending_action = None
            dealt_count += 1
        # One staggered draw sound per player makes the deal audible as a sequence.
        for index in range(dealt_count):
            self.schedule_sound(
                f"{audio.DEAL_FAMILY}{index % 4 + 1}.ogg",
                delay_ticks=2 + index * audio.DEAL_STAGGER_TICKS,
            )
        if self.USES_VIRA:
            self.vira = self.deck.pop()
        self.hand_active = True

        self.broadcast_l("truco-hand-start", buffer="game", hand=self.round)
        dealer = self.get_player_by_id(self.turn_player_ids[self.dealer_index])
        mano = self.get_player_by_id(self.turn_player_ids[self.mano_index])
        if dealer:
            self.broadcast_personal_l(
                dealer, "truco-dealer-you", "truco-dealer-player", buffer="game"
            )
        if mano:
            self.broadcast_personal_l(
                mano, "truco-mano-you", "truco-mano-player", buffer="game"
            )
        for player in order:
            user = self.get_user(player)
            if not user:
                continue
            if self.blind_hand:
                user.speak_l(
                    "trucobrazilian-blind-cards", buffer="game", count=len(player.hand)
                )
            else:
                user.speak_l(
                    "truco-your-cards",
                    buffer="game",
                    cards=self._format_cards(player.hand, user.locale),
                )
        if self.vira is not None:
            self._announce_vira()
        if self.MAO_DE_ONZE and self._start_onze():
            return
        if self._flor_enabled() and self._announce_flores(order):
            return
        self._jolt()
        self.announce_turn()
        self.refresh_menus()

    def _announce_vira(self) -> None:
        """Hook: variants with a turned-up card announce it here."""

    def _blind_hand(self) -> bool:
        """Hook: True when every hand is played face down (Paulista mão de ferro)."""

        return False

    def _start_onze(self) -> bool:
        """Hook: variants with a "mão de onze" decide here. True waits for an answer."""

        return False

    def _announce_flores(self, order: list[TrucoPlayer]) -> bool:
        """Announce flores. Returns True if the game ended while scoring them."""

        holders = [p for p in order if p.has_flor]
        for holder in holders:
            self.broadcast_personal_l(
                holder,
                "truco-flor-announce-you",
                "truco-flor-announce-player",
                buffer="game",
            )
        if not holders:
            return False
        self.envido_flor = True
        self.envido_done = True
        self.broadcast_l("truco-flor-cancels-envido", buffer="game")
        teams = {self._team_index(p) for p in holders}
        if len(teams) == 1:
            team = teams.pop()
            return bool(
                self._award(team, rules.FLOR_POINTS * len(holders), "truco-reason-flor")
            )
        self.flor_window = True
        return False

    def _close_flor_window(self) -> bool:
        """Score flores nobody contested. Returns True if the game ended."""

        if not self.flor_window:
            return False
        self.flor_window = False
        for team in range(2):
            holders = [
                p for p in self._team_players(team, live_only=True) if p.has_flor
            ]
            if holders and self._award(
                team, rules.FLOR_POINTS * len(holders), "truco-reason-flor"
            ):
                return True
        return False

    # ------------------------------------------------------------------
    # Playing cards and tricks
    # ------------------------------------------------------------------

    def _action_play_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TrucoPlayer) or self._card_error(player, action_id):
            return
        card = self._card_for_action(player, action_id)
        if card is None:
            return
        if self.flor_window and self._close_flor_window():
            return
        player.hand = [c for c in player.hand if c.id != card.id]
        self.plays[-1].append(TablePlay(player.id, card))
        self.play_sound_family(audio.PLAY_FAMILY)
        self.broadcast_personal_l(
            player,
            "truco-play-you",
            "truco-play-player",
            buffer="game",
            card=lambda locale: self._format_card(card, locale),
        )
        self._after_play()

    def _next_to_play(self) -> TrucoPlayer | None:
        played = {play.player_id for play in self.plays[-1]}
        for player in self._order_from(self.trick_leader_index):
            if self._live(player) and player.id not in played:
                return player
        return None

    def _after_play(self) -> None:
        nxt = self._next_to_play()
        if nxt is None:
            self._resolve_trick()
            return
        self.turn_index = self.turn_player_ids.index(nxt.id)
        self._jolt()
        self.announce_turn()
        self.refresh_menus()

    def _resolve_trick(self) -> None:
        trick = self.plays[-1]
        best = max(self._power(play.card) for play in trick)
        top = [play for play in trick if self._power(play.card) == best]
        winners = {
            self._team_index(self.get_player_by_id(play.player_id)) for play in top
        }
        number = len(self.trick_results) + 1
        if len(winners) == 1:
            winner_team = next(iter(winners))
            winner_play = top[0]
            self.trick_results.append(winner_team)
            self._announce_trick_winner(number, winner_play)
            next_leader_id = winner_play.player_id
        else:
            self.trick_results.append(None)
            self.broadcast_l(self._m("truco-trick-tie"), buffer="game", trick=number)
            next_leader_id = trick[0].player_id

        mano_player = self.get_player_by_id(self.turn_player_ids[self.mano_index])
        mano_team = self._team_index(mano_player) if mano_player else 0
        decided = self._decide_hand(self._tie_break_team(top, mano_team))
        if decided == rules.ANNULLED:
            self._annul_hand()
            return
        if decided is not None:
            self._finish_by_tricks(decided)
            return

        leader = self.get_player_by_id(next_leader_id)
        if not self._live(leader):
            start = self.turn_player_ids.index(next_leader_id)
            leader = next(p for p in self._order_from(start) if self._live(p))
        self.trick_leader_index = self.turn_player_ids.index(leader.id)
        self.turn_index = self.trick_leader_index
        self.plays.append([])
        self._jolt()
        self.announce_turn()
        self.refresh_menus()

    def _announce_trick_winner(self, number: int, play: TablePlay) -> None:
        winner = self.get_player_by_id(play.player_id)
        if winner is None:
            return
        winner_team = self._team_index(winner)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            card_text = self._format_card(play.card, user.locale)
            if listener.id == winner.id:
                user.speak_l(
                    "truco-trick-win-you", buffer="game", trick=number, card=card_text
                )
            elif (
                not listener.is_spectator and self._team_index(listener) == winner_team
            ):
                user.speak_l(
                    "truco-trick-win-teammate",
                    buffer="game",
                    trick=number,
                    card=card_text,
                    **self._resolve_broadcast_kwargs(user.locale, {"player": winner}),
                )
            else:
                user.speak_l(
                    "truco-trick-win-opponent",
                    buffer="game",
                    trick=number,
                    card=card_text,
                    **self._resolve_broadcast_kwargs(
                        user.locale,
                        {"player": winner, "team": self._team_label(winner_team)},
                    ),
                )

    # ------------------------------------------------------------------
    # Calls and answers
    # ------------------------------------------------------------------

    def _announce_call(
        self, actor: TrucoPlayer, call: str, *, goes_first: bool = False
    ) -> None:
        responder_ids = {p.id for p in self._responders()}
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            kwargs = {"call": self._call_text(user.locale, call)}
            if listener.id == actor.id:
                key = "truco-call-goes-first-you" if goes_first else "truco-call-you"
            elif listener.id in responder_ids:
                key = self._m("truco-pending-answer")
                kwargs["player"] = actor
            else:
                key = (
                    "truco-call-goes-first-player"
                    if goes_first
                    else "truco-call-player"
                )
                kwargs["player"] = actor
            user.speak_l(
                key,
                buffer="game",
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )

    def _call_sound(self, call: str) -> None:
        if call in self.LADDER:
            level = self.LADDER.index(call)
            self.play_sound(audio.TRUCO_CALL, pitch=100 + 8 * level)
        elif call in FLOR_CALLS:
            self.play_sound(audio.FLOR_CALL)
        else:
            self.play_sound(audio.ENVIDO_CALL)

    def _action_call(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TrucoPlayer) or self._call_error(player, action_id):
            return
        call = self.CALL_ACTIONS[action_id]
        team = self._team_index(player)
        if call == "truco":
            level = self._next_level(self.truco_pending or self.truco_level or None)
            if level is None:
                return
            self.truco_pending = level
            self.truco_pending_team = team
            self.truco_pending_by = player.id
            self._call_sound(level)
            self._announce_call(player, level)
        elif call in ENVIDO_CALLS:
            goes_first = bool(self.truco_pending) and not self.envido_pending
            self.envido_chain.append(call)
            self.envido_pending = True
            self.envido_pending_team = team
            self._call_sound(call)
            self._announce_call(player, call, goes_first=goes_first)
            if call == rules.FALTA_ENVIDO:
                self._announce_falta_value()
        else:
            self.flor_chain.append(call)
            self.flor_pending = call
            self.flor_pending_team = team
            self._call_sound(call)
            self._announce_call(player, call)
        self._jolt()
        self.refresh_menus()

    def _announce_falta_value(self) -> None:
        if self._falta_decides_game():
            self.broadcast_l("truco-falta-envido-game", buffer="game")
        else:
            self.broadcast_l(
                self._m("truco-falta-envido-value"),
                buffer="game",
                points=self._falta_points(),
            )

    def _broadcast_answer(self, player: TrucoPlayer, accepted: bool) -> None:
        if self.onze_pending:
            word = "play" if accepted else "run"
            you = f"trucobrazilian-onze-{word}-you"
            other = f"trucobrazilian-onze-{word}-player"
        else:
            you = self._m("truco-accept-you" if accepted else "truco-decline-you")
            other = self._m(
                "truco-accept-player" if accepted else "truco-decline-player"
            )
        self.play_sound(audio.ACCEPT if accepted else audio.DECLINE)
        self.broadcast_personal_l(
            player, you, other, buffer="game", call=self._call_arg(self._pending_call())
        )

    def _action_accept(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TrucoPlayer) or self._answer_error(player):
            return
        kind = self._pending_kind()
        self._broadcast_answer(player, True)
        if kind == ONZE:
            self.onze_pending = False
            self.no_calls = True
            self.hand_base = self._onze_value()
            self._jolt()
            self.announce_turn()
            self.refresh_menus()
        elif kind == "truco":
            self.truco_level = self.truco_pending
            self.truco_pending = ""
            self.truco_raiser_team = self._team_index(player)
            self._jolt()
            self.announce_turn()
            self.refresh_menus()
        elif kind == "envido":
            self._resolve_envido()
        else:
            self._resolve_flor()

    def _action_decline(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TrucoPlayer) or self._answer_error(player):
            return
        kind = self._pending_kind()
        self._broadcast_answer(player, False)
        if kind == ONZE:
            self.onze_pending = False
            self._conclude_hand(
                self._other_team(self.onze_team), 1, "trucobrazilian-reason-onze-run"
            )
        elif kind == "truco":
            caller = self.truco_pending_team
            points = self._level_points(self.truco_pending, accepted=False)
            self.truco_pending = ""
            self._conclude_hand(caller, points, self._m("truco-reason-truco"))
        elif kind == "envido":
            caller = self.envido_pending_team
            points = self._envido_declined_points(self.envido_chain)
            self._finish_envido()
            if self._award(caller, points, self._m("truco-reason-envido")):
                return
            self._after_envido_or_flor()
        else:
            caller = self.flor_pending_team
            points = rules.flor_declined_points(self.flor_chain)
            self._finish_flor()
            if self._award(caller, points, "truco-reason-flor"):
                return
            self._after_envido_or_flor()

    def _finish_envido(self) -> None:
        self.envido_pending = False
        self.envido_done = True

    def _finish_flor(self) -> None:
        self.flor_pending = ""
        self.flor_window = False

    def _after_envido_or_flor(self) -> None:
        """Resume play after a side call; re-prompt a truco still waiting."""

        self._jolt()
        if self.truco_pending:
            by = self.get_player_by_id(self.truco_pending_by)
            for responder in self._responders():
                user = self.get_user(responder)
                if user:
                    user.speak_l(
                        self._m("truco-pending-answer"),
                        buffer="game",
                        call=self._call_text(user.locale, self.truco_pending),
                        **self._resolve_broadcast_kwargs(
                            user.locale, {"player": by.name if by else ""}
                        ),
                    )
        else:
            self.announce_turn()
        self.refresh_menus()

    def _best_by_score(self, candidates: list[TrucoPlayer], score_of) -> TrucoPlayer:
        best: TrucoPlayer | None = None
        best_value = -1
        for player in candidates:
            value = score_of(player)
            if value > best_value:
                best, best_value = player, value
        assert best is not None
        return best

    def _resolve_envido(self) -> None:
        chain = list(self.envido_chain)
        live = [p for p in self._order_from(self.mano_index) if self._live(p)]
        winner = self._best_by_score(live, lambda p: rules.envido_score(p.dealt))
        value = rules.envido_score(winner.dealt)
        team = self._team_index(winner)
        falta = 0
        if rules.FALTA_ENVIDO in chain:
            falta = self._falta_points(self._team(team).total_score)
        points = self._envido_accepted_points(chain, falta)
        self._finish_envido()
        self.reveals.append(
            Reveal(
                "envido",
                winner.id,
                [c.id for c in rules.envido_cards(winner.dealt)],
                value,
            )
        )
        if self._award(team, points, self._m("truco-reason-envido")):
            return
        self._after_envido_or_flor()

    def _resolve_flor(self) -> None:
        chain = list(self.flor_chain)
        holders = [
            p for p in self._order_from(self.mano_index) if self._live(p) and p.has_flor
        ]
        winner = self._best_by_score(holders, lambda p: rules.flor_score(p.dealt))
        value = rules.flor_score(winner.dealt)
        team = self._team_index(winner)
        if chain[-1] == rules.CONTRAFLOR_AL_RESTO:
            points = self._falta_points(self._team(team).total_score)
        else:
            points = rules.CONTRAFLOR_POINTS
        self._finish_flor()
        self.reveals.append(
            Reveal(
                "flor",
                winner.id,
                [c.id for c in rules.flor_cards(winner.dealt)],
                value,
            )
        )
        if self._award(team, points, "truco-reason-flor"):
            return
        self._after_envido_or_flor()

    # ------------------------------------------------------------------
    # Me voy al mazo
    # ------------------------------------------------------------------

    def _action_mazo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TrucoPlayer) or self._mazo_error(player):
            return
        was_current = self.current_player is player
        player.folded = True
        player.hand = []
        self.play_sound(audio.FOLD)
        self.broadcast_personal_l(
            player,
            self._m("truco-mazo-you"),
            self._m("truco-mazo-player"),
            buffer="game",
        )
        team = self._team_index(player)
        if self.FOLD_SCOPE == "team":
            for mate in self._team_players(team, live_only=True):
                mate.folded = True
                mate.hand = []
        if not self._team_players(team, live_only=True):
            self._team_folded(team)
            return
        if (
            self.flor_window
            and not self._flor_holders_on_both_sides()
            and self._close_flor_window()
        ):
            return
        if was_current or self._next_to_play() is None:
            self._after_play()
        else:
            self.refresh_menus()

    def _flor_holders_on_both_sides(self) -> bool:
        return all(
            any(p.has_flor for p in self._team_players(team, live_only=True))
            for team in range(2)
        )

    def _team_folded(self, team: int) -> None:
        opponent = self._other_team(team)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if not listener.is_spectator and self._team_index(listener) == team:
                user.speak_l("truco-team-folded-your-team", buffer="game")
            else:
                user.speak_l(
                    "truco-team-folded-team",
                    buffer="game",
                    **self._resolve_broadcast_kwargs(
                        user.locale, {"team": self._team_label(team)}
                    ),
                )
        if self.flor_window:
            self.flor_window = False
            holders = [
                p for p in self._team_players(opponent, live_only=True) if p.has_flor
            ]
            if holders and self._award(
                opponent, rules.FLOR_POINTS * len(holders), "truco-reason-flor"
            ):
                return
        if self._envido_open() and self._award(
            opponent, 1, self._m("truco-reason-envido")
        ):
            return
        if self.truco_level:
            self._conclude_hand(
                opponent,
                self._level_points(self.truco_level),
                self._m("truco-reason-truco"),
            )
        else:
            self._conclude_hand(opponent, self.hand_base, "truco-reason-hand")

    # ------------------------------------------------------------------
    # Scoring and the end of hands and games
    # ------------------------------------------------------------------

    def _finish_by_tricks(self, winner_team: int) -> None:
        if self.truco_level:
            self._conclude_hand(
                winner_team,
                self._level_points(self.truco_level),
                self._m("truco-reason-truco"),
            )
        else:
            self._conclude_hand(winner_team, self.hand_base, "truco-reason-hand")

    def _award(self, team_index: int, points: int, reason_key: str) -> bool:
        """Add points to a side. Returns True when this ended the game."""

        team = self._team(team_index)
        old = team.total_score
        new = min(self.target, old + max(0, points))
        gained = new - old
        team.total_score = new
        self._sync_scores()
        members = set(team.members)
        if gained > 0:
            self.play_sound(audio.POINTS, pitch=min(160, 90 + gained * 6))
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                reason = Localization.get(user.locale, reason_key)
                mine = listener.name in members
                if self._individual():
                    key = "truco-points-you" if mine else "truco-points-player"
                    kwargs: dict = {} if mine else {"player": team.members[0]}
                else:
                    key = "truco-points-your-team" if mine else "truco-points-team"
                    kwargs = {} if mine else {"team": self._team_label(team_index)}
                user.speak_l(
                    key,
                    buffer="game",
                    points=gained,
                    reason=reason,
                    **self._resolve_broadcast_kwargs(user.locale, kwargs),
                )
            self._on_points_awarded(team_index, old, new)
        if new >= self.target:
            return self._close_came(team_index, points >= self._whole_game_points())
        return False

    def _close_came(self, team_index: int, whole_game: bool) -> bool:
        """A side reached the target. Ends the game, or the came when more remain."""

        if self.CAMES_TO_WIN <= 1:
            self._finish_game(team_index)
            return True
        if len(self.came_wins) < len(self._team_manager.teams):
            self.came_wins = [0] * len(self._team_manager.teams)
        self.came_wins[team_index] = (
            self.CAMES_TO_WIN if whole_game else self.came_wins[team_index] + 1
        )
        if self.came_wins[team_index] >= self.CAMES_TO_WIN:
            self._finish_game(team_index)
            return True
        self.play_sound(audio.CAME_WIN)
        self._announce_buenas(
            team_index, "trucospanish-came", cames=self._cames(team_index)
        )
        for team in self._team_manager.teams:
            team.total_score = 0
        self._sync_scores()
        return False

    def _announce_buenas(
        self, team_index: int, prefix: str = "truco-half-buenas", **extra
    ) -> None:
        team = self._team(team_index)
        members = set(team.members)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            mine = listener.name in members
            if self._individual():
                key = f"{prefix}-you" if mine else f"{prefix}-player"
                kwargs: dict = {} if mine else {"player": team.members[0]}
            else:
                key = f"{prefix}-your-team" if mine else f"{prefix}-team"
                kwargs = {} if mine else {"team": self._team_label(team_index)}
            user.speak_l(
                key,
                buffer="game",
                **extra,
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )

    def _announce_reveals(self) -> None:
        reveals, self.reveals = self.reveals, []
        for reveal in reveals:
            owner = self.get_player_by_id(reveal.player_id)
            if owner is None:
                continue
            shown = [c for c in owner.dealt if c.id in reveal.card_ids]  # type: ignore[attr-defined]
            for listener in self.players:
                user = self.get_user(listener)
                if not user:
                    continue
                mine = listener.id == owner.id
                key = self._m(
                    f"truco-reveal-{reveal.kind}-{'you' if mine else 'player'}"
                )
                kwargs: dict = {} if mine else {"player": owner}
                user.speak_l(
                    key,
                    buffer="game",
                    cards=self._format_cards(shown, user.locale),
                    value=reveal.value,
                    **self._resolve_broadcast_kwargs(user.locale, kwargs),
                )

    def _conclude_hand(self, winner_team: int, points: int, reason_key: str) -> None:
        self.hand_active = False
        self._announce_reveals()
        for listener in self.players:
            user = self.get_user(listener)
            if user and not listener.is_spectator:
                won = self._team_index(listener) == winner_team
                user.play_sound(audio.HAND_WIN if won else audio.HAND_LOSE)
        if self._award(winner_team, points, reason_key):
            return
        self._show_score_lines()
        self._schedule_next_hand()

    def _annul_hand(self) -> None:
        """A hand nobody won (Paulista, three tied tricks): no points, new deal."""

        self.hand_active = False
        self._announce_reveals()
        self.play_sound(audio.HAND_ANNULLED)
        self.broadcast_l("trucobrazilian-hand-annulled", buffer="game")
        self._show_score_lines()
        self._schedule_next_hand()

    def _show_score_lines(self) -> None:
        for team in self._team_manager.teams:
            self.broadcast_l(
                self._m("truco-score-line"),
                buffer="game",
                team=self._team_label(team.index),
                score=team.total_score,
                cames=self._cames(team.index),
            )

    def _schedule_next_hand(self) -> None:
        self.start_sequence(
            NEXT_HAND_SEQUENCE_ID,
            [
                SequenceBeat.pause(NEXT_HAND_DELAY_TICKS),
                SequenceBeat(ops=[SequenceOperation.callback_op("start_next_hand")]),
            ],
            tag=NEXT_HAND_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.refresh_menus()

    def _finish_game(self, team_index: int) -> None:
        self.hand_active = False
        self.winner_team_index = team_index
        self.cancel_sequences_by_tag(NEXT_HAND_SEQUENCE_TAG)
        self._announce_reveals()
        team = self._team(team_index)
        members = set(team.members)
        self.play_sound(audio.GAME_WIN)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            mine = listener.name in members
            if self._individual():
                key = self._m("truco-game-win-you" if mine else "truco-game-win-player")
                kwargs: dict = {} if mine else {"player": team.members[0]}
            else:
                key = self._m(
                    "truco-game-win-your-team" if mine else "truco-game-win-team"
                )
                kwargs = {} if mine else {"team": self._team_label(team_index)}
            user.speak_l(
                key,
                buffer="game",
                score=team.total_score,
                cames=self._cames(team_index),
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )
        self.finish_game()

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        sorted_teams = sorted(
            self._team_manager.teams,
            key=lambda t: (self._final_score(t), t.total_score),
            reverse=True,
        )
        winner = next(
            (t for t in sorted_teams if t.index == self.winner_team_index),
            sorted_teams[0] if sorted_teams else None,
        )
        active = self.get_active_players()
        name_to_id = {p.name: p.id for p in active}
        rankings = [
            {
                "index": team.index,
                "members": list(team.members),
                "score": self._final_score(team),
                "is_individual": self._individual(),
            }
            for team in sorted_teams
        ]
        winner_ids = [
            name_to_id[name]
            for name in (winner.members if winner else [])
            if name in name_to_id
        ]
        competitors = rating_competitors_from_scores(
            (
                [name_to_id[name] for name in team.members if name in name_to_id],
                self._final_score(team),
            )
            for team in sorted_teams
        )
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(UTC).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[PlayerResult.from_player(p) for p in active],
            custom_data={
                "winner_name": (
                    self._team_manager.get_team_name(winner) if winner else None
                ),
                "winner_ids": winner_ids,
                "winner_score": self._final_score(winner) if winner else 0,
                "team_rankings": rankings,
                RATING_COMPETITORS_KEY: competitors,
                "hands_played": self.round,
                "target_score": self.target,
                "team_mode": self.options.team_mode,
                "flor": self._flor_enabled(),
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "truco-end-title")]
        for rank, team in enumerate(result.custom_data.get("team_rankings", []), 1):
            members = team.get("members", [])
            if team.get("is_individual") and members:
                name = members[0]
            else:
                name = Localization.get(
                    locale, "game-team-name", index=team.get("index", 0) + 1
                )
            lines.append(
                Localization.get(
                    locale,
                    self._m("truco-end-line"),
                    rank=rank,
                    team=name,
                    score=team.get("score", 0),
                )
            )
        return lines
