"""Metal Pipe automatic luck game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import BoolOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


BONK_SEQUENCE_ID = "metalpipe_bonks"
BONK_SEQUENCE_TAG = "metalpipe_bonks"
BONK_START_DELAY_TICKS = 5
BONK_DELAY_TICKS = 5
WINNER_DELAY_TICKS = 30


@dataclass
class MetalPipePlayer(Player):
    """Per-player Metal Pipe state."""

    alive: bool = True


@dataclass
class MetalPipeOptions(GameOptions):
    """Host-configurable Metal Pipe settings."""

    multiple_bonks: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="metalpipe-set-multiple-bonks",
            change_msg="metalpipe-option-changed-multiple-bonks",
            description="metalpipe-desc-multiple-bonks",
        )
    )
    allow_self_bonk: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="metalpipe-set-allow-self-bonk",
            change_msg="metalpipe-option-changed-allow-self-bonk",
            description="metalpipe-desc-allow-self-bonk",
        )
    )


@dataclass
@register_game
class MetalPipeGame(Game):
    """A short automatic party-luck spectacle."""

    relevant_preferences = ["brief_announcements"]

    players: list[MetalPipePlayer] = field(default_factory=list)
    options: MetalPipeOptions = field(default_factory=MetalPipeOptions)

    winner_ids: list[str] = field(default_factory=list)
    winner_names: list[str] = field(default_factory=list)
    last_bonker_id: str = ""
    last_bonked_id: str = ""
    last_bonk_was_self: bool = False
    bonk_count: int = 0
    # Backward-compatible field for saves/end screens produced by older builds.
    _winner_names: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Metal Pipe"

    @classmethod
    def get_type(cls) -> str:
        return "metalpipe"

    @classmethod
    def get_category(cls) -> str:
        return "misc"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return []

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> MetalPipePlayer:
        return MetalPipePlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _active_metalpipe_players(self) -> list[MetalPipePlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, MetalPipePlayer)
        ]

    def _alive_players(self) -> list[MetalPipePlayer]:
        return [player for player in self._active_metalpipe_players() if player.alive]

    def _active_player_by_id(self, player_id: str) -> MetalPipePlayer | None:
        for player in self._active_metalpipe_players():
            if player.id == player_id:
                return player
        return None

    def _mode_key(self) -> str:
        if self.options.multiple_bonks:
            return "metalpipe-mode-multiple"
        return "metalpipe-mode-single"

    def _self_bonk_key(self) -> str:
        if self.options.allow_self_bonk:
            return "metalpipe-self-bonk-allowed"
        return "metalpipe-self-bonk-blocked"

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _broadcast_bonk(
        self,
        bonker: MetalPipePlayer,
        bonked: MetalPipePlayer,
        *,
        is_self: bool,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            payload = self._resolve_broadcast_kwargs(
                user.locale,
                {"bonker": bonker, "bonked": bonked},
            )
            if is_self:
                if listener.id == bonker.id:
                    key = "metalpipe-you-hit-self"
                    brief_key = "metalpipe-you-hit-self-brief"
                else:
                    key = "metalpipe-player-hits-self"
                    brief_key = "metalpipe-player-hits-self-brief"
            elif listener.id == bonker.id:
                key = "metalpipe-you-hit-other"
                brief_key = "metalpipe-you-hit-other-brief"
            elif listener.id == bonked.id:
                key = "metalpipe-player-hits-you"
                brief_key = "metalpipe-player-hits-you-brief"
            else:
                key = "metalpipe-player-hits-other"
                brief_key = "metalpipe-player-hits-other-brief"

            if self._wants_brief(user):
                key = brief_key
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_winners(self) -> None:
        winners = [self._active_player_by_id(player_id) for player_id in self.winner_ids]
        winners = [winner for winner in winners if winner is not None]
        winner_names = [winner.name for winner in winners]
        if not winner_names:
            self._broadcast_global_l(
                "metalpipe-no-winner",
                "metalpipe-no-winner-brief",
            )
            return

        winner_id_set = {winner.id for winner in winners}
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            brief = self._wants_brief(user)
            if listener.id in winner_id_set:
                others = [winner.name for winner in winners if winner.id != listener.id]
                if others:
                    key = (
                        "metalpipe-you-win-with-others-brief"
                        if brief
                        else "metalpipe-you-win-with-others"
                    )
                    user.speak_l(
                        key,
                        buffer="game",
                        players=Localization.format_list_and(user.locale, others),
                    )
                else:
                    key = "metalpipe-you-win-brief" if brief else "metalpipe-you-win"
                    user.speak_l(key, buffer="game")
            else:
                key = (
                    "metalpipe-players-win-brief"
                    if brief
                    else "metalpipe-players-win"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    players=Localization.format_list_and(user.locale, winner_names),
                )

    # ======================================================================
    # Actions and menus
    # ======================================================================

    def _is_status_action_enabled(self, player: Player) -> str | None:
        if self.status not in {"playing", "finished"}:
            return "action-not-playing"
        return None

    def _is_status_action_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return (
                Visibility.VISIBLE
                if self.status in {"playing", "finished"}
                else Visibility.HIDDEN
            )
        return Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(
                    self._player_locale(player),
                    "metalpipe-check-status",
                ),
                handler="_action_check_status",
                is_enabled="_is_status_action_enabled",
                is_hidden="_is_status_action_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                ["check_status", "whose_turn", "whos_at_table"],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        host_user = None
        if self.host:
            host_player = self.get_player_by_name(self.host)
            if host_player:
                host_user = self.get_user(host_player)
        locale = host_user.locale if host_user else "en"
        self.define_keybind(
            "c",
            Localization.get(locale, "metalpipe-check-status"),
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _status_items(self, locale: str) -> list[MenuItem]:
        mode = Localization.get(locale, self._mode_key())
        self_bonk = Localization.get(locale, self._self_bonk_key())
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "metalpipe-status-mode",
                    mode=mode,
                    self_bonk=self_bonk,
                ),
                id="mode",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "metalpipe-status-progress",
                    count=self.bonk_count,
                    alive=len(self._alive_players()),
                    total=len(self._active_metalpipe_players()),
                ),
                id="progress",
            ),
        ]
        if self.last_bonker_id and self.last_bonked_id:
            bonker = self._active_player_by_id(self.last_bonker_id)
            bonked = self._active_player_by_id(self.last_bonked_id)
            if bonker and bonked:
                key = (
                    "metalpipe-status-last-self"
                    if self.last_bonk_was_self
                    else "metalpipe-status-last-other"
                )
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            key,
                            **self._resolve_broadcast_kwargs(
                                locale,
                                {"bonker": bonker, "bonked": bonked},
                            ),
                        ),
                        id="last_bonk",
                    )
                )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "metalpipe-status-awaiting"),
                    id="last_bonk",
                )
            )

        for player in self._active_metalpipe_players():
            status_key = (
                "metalpipe-status-alive"
                if player.alive
                else "metalpipe-status-eliminated"
            )
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "metalpipe-status-player",
                        player=player.name,
                        status=Localization.get(locale, status_key),
                    ),
                    id=f"player:{player.id}",
                )
            )
        return items

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "metalpipe_status",
            lambda _player, live_user: self._status_items(live_user.locale),
            focus_id="mode",
        )

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.status == "playing":
            user.speak_l(
                "metalpipe-no-turn-automatic",
                buffer="game",
                alive=len(self._alive_players()),
            )
        else:
            super()._action_whose_turn(player, action_id)

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        """Start the automatic bonk sequence."""
        self.cancel_sequences_by_tag(BONK_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.winner_ids = []
        self.winner_names = []
        self._winner_names = []
        self.last_bonker_id = ""
        self.last_bonked_id = ""
        self.last_bonk_was_self = False
        self.bonk_count = 0

        active_players = self._active_metalpipe_players()
        for player in active_players:
            player.alive = True

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = (
                "metalpipe-game-start-brief"
                if self._wants_brief(user)
                else "metalpipe-game-start"
            )
            user.speak_l(
                key,
                buffer="game",
                mode=Localization.get(user.locale, self._mode_key()),
            )
        self._run_bonks(active_players)
        self.refresh_menus()

    def _run_bonks(self, players: list[MetalPipePlayer]) -> None:
        """Pre-calculate all bonk outcomes and schedule them as a sequence."""
        single = not self.options.multiple_bonks
        alive_ids = [player.id for player in players]
        winner_ids: list[str] = []
        beats: list[SequenceBeat] = []

        while len(alive_ids) > 1:
            bonker_id = random.choice(alive_ids)  # nosec B311

            if self.options.allow_self_bonk:
                bonked_id = random.choice(alive_ids)  # nosec B311
            else:
                others = [player_id for player_id in alive_ids if player_id != bonker_id]
                if not others:
                    break
                bonked_id = random.choice(others)  # nosec B311

            is_self = bonker_id == bonked_id
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op("lsmack.ogg"),
                        SequenceOperation.callback_op(
                            "bonk",
                            {
                                "bonker_id": bonker_id,
                                "bonked_id": bonked_id,
                                "is_self": is_self,
                            },
                        ),
                    ],
                    delay_after_ticks=BONK_DELAY_TICKS,
                )
            )

            alive_ids = [player_id for player_id in alive_ids if player_id != bonked_id]

            if single:
                if is_self:
                    winner_ids = [player.id for player in players if player.id != bonker_id]
                else:
                    winner_ids = [bonker_id]
                break

        if not single and not winner_ids:
            winner_ids = list(alive_ids)
            if len(winner_ids) > 1:
                winner_ids = [random.choice(winner_ids)]  # nosec B311

        if beats:
            beats[-1].delay_after_ticks = WINNER_DELAY_TICKS

        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.sound_op("gamewin.ogg"),
                    SequenceOperation.callback_op(
                        "winner",
                        {"winner_ids": winner_ids},
                    ),
                ]
            )
        )

        self.start_sequence(
            BONK_SEQUENCE_ID,
            beats,
            start_delay=BONK_START_DELAY_TICKS,
            tag=BONK_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        """Handle scheduled sequence callbacks."""
        if sequence_id != BONK_SEQUENCE_ID:
            return

        if callback_id == "bonk":
            bonker = self._active_player_by_id(str(payload.get("bonker_id", "")))
            bonked = self._active_player_by_id(str(payload.get("bonked_id", "")))
            if not bonker or not bonked:
                return

            bonked.alive = False
            self.bonk_count += 1
            self.last_bonker_id = bonker.id
            self.last_bonked_id = bonked.id
            self.last_bonk_was_self = bool(payload.get("is_self", False))
            self._broadcast_bonk(
                bonker,
                bonked,
                is_self=self.last_bonk_was_self,
            )
            self.refresh_menus()
            return

        if callback_id == "winner":
            winner_ids = [
                str(player_id)
                for player_id in payload.get("winner_ids", [])
                if self._active_player_by_id(str(player_id))
            ]
            self.winner_ids = winner_ids
            self.winner_names = [
                player.name
                for player_id in winner_ids
                if (player := self._active_player_by_id(player_id))
            ]
            self._winner_names = list(self.winner_names)
            self._broadcast_winners()
            self.status = "finished"
            self._sync_table_status()
            self.refresh_menus()
            self.finish_game()

    def on_tick(self) -> None:
        """Advance timed bonk callbacks."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

    # ======================================================================
    # Results
    # ======================================================================

    def build_game_result(self) -> GameResult:
        """Build the game result."""
        all_players = self._active_metalpipe_players()
        winner_names = self.winner_names or self._winner_names

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(player)
                for player in all_players
            ],
            custom_data={
                "winner_ids": list(self.winner_ids),
                "winner_names": list(winner_names),
                "multiple_bonks": self.options.multiple_bonks,
                "allow_self_bonk": self.options.allow_self_bonk,
                "bonk_count": self.bonk_count,
                "alive_status": {player.name: player.alive for player in all_players},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        winner_names = result.custom_data.get("winner_names", [])
        lines = [Localization.get(locale, "metalpipe-final-results")]
        if winner_names:
            if len(winner_names) == 1:
                lines.append(
                    Localization.get(
                        locale,
                        "metalpipe-end-winner",
                        player=winner_names[0],
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        locale,
                        "metalpipe-end-winners",
                        players=Localization.format_list_and(locale, winner_names),
                    )
                )
        else:
            lines.append(Localization.get(locale, "metalpipe-no-winner"))

        alive_status = result.custom_data.get("alive_status", {})
        for player in result.player_results:
            status_key = (
                "metalpipe-status-alive"
                if alive_status.get(player.player_name, False)
                else "metalpipe-status-eliminated"
            )
            lines.append(
                Localization.get(
                    locale,
                    "metalpipe-line-format",
                    player=player.player_name,
                    status=Localization.get(locale, status_key),
                )
            )
        return lines
