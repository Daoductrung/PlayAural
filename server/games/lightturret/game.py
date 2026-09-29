"""Light Turret push-your-luck game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


UPGRADE_COST = 10
SHOT_MIN_GAIN = 1
SHOT_MAX_GAIN = 4
UPGRADE_POWER_MIN = 2
UPGRADE_POWER_MAX = 8
UPGRADE_ACCIDENT_LIGHT_MIN = 1
UPGRADE_ACCIDENT_LIGHT_MAX = 5
UPGRADE_ACCIDENT_CHANCE = 0.25
RISK_CONFIRM_TICKS = 200
RISK_CONFIRM_SECONDS = 10
ACTION_SEQUENCE_ID = "lightturret_action"
ACTION_SEQUENCE_TAG = "lightturret_action"
ACTION_SOUND_DELAY_TICKS = 5
RESULT_DELAY_TICKS = 4
OVERLOAD_SOUND_DELAY_TICKS = 6
END_REASON_MAX_ROUNDS = "max_rounds"
END_REASON_ALL_ELIMINATED = "all_eliminated"


@dataclass
class LightTurretPlayer(Player):
    """Per-player Light Turret state."""

    power: int = 10
    light: int = 0
    coins: int = 0
    alive: bool = True
    pending_risky_action: str = ""
    risky_confirm_ticks: int = 0


@dataclass
class LightTurretOptions(GameOptions):
    """Host-configurable Light Turret settings."""

    starting_power: int = option_field(
        IntOption(
            default=10,
            min_val=5,
            max_val=30,
            value_key="power",
            label="lightturret-set-starting-power",
            prompt="lightturret-enter-starting-power",
            change_msg="lightturret-option-changed-power",
            description="lightturret-desc-starting-power",
        )
    )
    max_rounds: int = option_field(
        IntOption(
            default=50,
            min_val=10,
            max_val=200,
            value_key="rounds",
            label="lightturret-set-max-rounds",
            prompt="lightturret-enter-max-rounds",
            change_msg="lightturret-option-changed-rounds",
            description="lightturret-desc-max-rounds",
        )
    )


@dataclass
@register_game
class LightTurretGame(Game):
    """A tactical score race built around capacity management and overload risk."""

    relevant_preferences = ["brief_announcements", "confirm_destructive_actions"]

    players: list[LightTurretPlayer] = field(default_factory=list)
    options: LightTurretOptions = field(default_factory=LightTurretOptions)
    score_unit_key = "game-score-unit-light"
    end_reason: str = ""
    pending_action_player_id: str = ""
    pending_action_kind: str = ""
    pending_action_resolved: bool = False
    # Backward-compatible completion flag for games saved by older releases.
    _pending_finish: bool = field(default=False, repr=False)

    @classmethod
    def get_name(cls) -> str:
        return "Light Turret"

    @classmethod
    def get_type(cls) -> str:
        return "lightturret"

    @classmethod
    def get_category(cls) -> str:
        return "arcade"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return [
            "wins",
            "total_score",
            "high_score",
            "rating",
            "games_played",
        ]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> LightTurretPlayer:
        return LightTurretPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _active_light_players(self) -> list[LightTurretPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, LightTurretPlayer)
        ]

    def _alive_players(self) -> list[LightTurretPlayer]:
        return [player for player in self._active_light_players() if player.alive]

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: LightTurretPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast an actor event with listener-specific perspective."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            is_actor = listener.id == actor.id
            key = personal_key if is_actor else others_key
            if self._wants_brief(user):
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key
            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = actor
            payload = self._resolve_broadcast_kwargs(user.locale, payload)
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _shot_overload_risk(self, player: LightTurretPlayer) -> int:
        """Return the exact overload percentage for a uniformly random shot."""
        headroom = player.power - player.light
        overload_results = sum(
            gain > headroom for gain in range(SHOT_MIN_GAIN, SHOT_MAX_GAIN + 1)
        )
        return int(overload_results * 100 / (SHOT_MAX_GAIN - SHOT_MIN_GAIN + 1))

    def _upgrade_overload_risk(self, player: LightTurretPlayer) -> int:
        """Return total overload risk from the 25% upgrade accident branch."""
        headroom = player.power - player.light
        overload_accidents = sum(
            gain > headroom
            for gain in range(
                UPGRADE_ACCIDENT_LIGHT_MIN, UPGRADE_ACCIDENT_LIGHT_MAX + 1
            )
        )
        accident_outcomes = (
            UPGRADE_ACCIDENT_LIGHT_MAX - UPGRADE_ACCIDENT_LIGHT_MIN + 1
        )
        return int(
            UPGRADE_ACCIDENT_CHANCE * overload_accidents * 100 / accident_outcomes
        )

    def _clear_risky_confirmation(self, player: LightTurretPlayer) -> None:
        player.pending_risky_action = ""
        player.risky_confirm_ticks = 0

    def _should_confirm_risky_shot(self, player: LightTurretPlayer) -> bool:
        risk = self._shot_overload_risk(player)
        if player.is_bot or risk < 50:
            self._clear_risky_confirmation(player)
            return False

        user = self.get_user(player)
        if not user or not user.preferences.get_effective(
            "confirm_destructive_actions", game_type=self.get_type()
        ):
            self._clear_risky_confirmation(player)
            return False

        signature = f"shoot:{player.light}:{player.power}:{self.round}"
        if (
            player.pending_risky_action == signature
            and player.risky_confirm_ticks > 0
        ):
            self._clear_risky_confirmation(player)
            return False

        player.pending_risky_action = signature
        player.risky_confirm_ticks = RISK_CONFIRM_TICKS
        user.speak_l(
            "lightturret-confirm-risky-shot",
            buffer="game",
            risk=risk,
            light=player.light,
            power=player.power,
            seconds=RISK_CONFIRM_SECONDS,
        )
        return True

    # ======================================================================
    # Actions and menus
    # ======================================================================

    def _turn_action_disabled_reason(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return "lightturret-you-are-eliminated"
        if self.is_sequence_gameplay_locked():
            return "lightturret-action-resolving"
        return None

    def _is_shoot_enabled(self, player: Player) -> str | None:
        return self._turn_action_disabled_reason(player)

    def _is_upgrade_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        reason = self._turn_action_disabled_reason(player)
        if reason:
            return reason
        assert isinstance(player, LightTurretPlayer)
        if player.coins < UPGRADE_COST:
            return (
                "lightturret-not-enough-coins",
                {"have": player.coins, "need": UPGRADE_COST},
            )
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_shoot_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, LightTurretPlayer):
            return Localization.get(self._player_locale(player), "lightturret-shoot")
        locale = self._player_locale(player)
        risk = self._shot_overload_risk(player)
        if risk:
            return Localization.get(
                locale, "lightturret-shoot-risk-label", risk=risk
            )
        return Localization.get(
            locale,
            "lightturret-shoot-safe-label",
            headroom=max(0, player.power - player.light),
        )

    def _get_upgrade_label(self, player: Player, action_id: str) -> str:
        coins = player.coins if isinstance(player, LightTurretPlayer) else 0
        return Localization.get(
            self._player_locale(player),
            "lightturret-upgrade-label",
            cost=UPGRADE_COST,
            coins=coins,
        )

    def _is_check_stats_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_stats_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
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

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def create_turn_action_set(self, player: LightTurretPlayer) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="shoot",
                label=Localization.get(locale, "lightturret-shoot"),
                handler="_action_shoot",
                is_enabled="_is_shoot_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_shoot_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="upgrade",
                label=Localization.get(
                    locale,
                    "lightturret-upgrade-label",
                    cost=UPGRADE_COST,
                    coins=0,
                ),
                handler="_action_upgrade",
                is_enabled="_is_upgrade_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_upgrade_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        action_set.add(
            Action(
                id="check_stats",
                label=Localization.get(
                    self._player_locale(player), "lightturret-check-stats"
                ),
                handler="_action_check_stats",
                is_enabled="_is_check_stats_enabled",
                is_hidden="_is_check_stats_hidden",
                include_spectators=True,
            )
        )
        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_stats",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
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
            "space",
            Localization.get(locale, "lightturret-shoot"),
            ["shoot"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "u",
            Localization.get(locale, "lightturret-upgrade"),
            ["upgrade"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get(locale, "lightturret-check-stats"),
            ["check_stats"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _status_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "lightturret-status-round",
                    round=self.round,
                    total=self.options.max_rounds,
                    alive=len(self._alive_players()),
                ),
                id="round",
            )
        ]
        for player in self._active_light_players():
            if player.alive:
                text = Localization.get(
                    locale,
                    "lightturret-stats-alive",
                    player=player.name,
                    power=player.power,
                    light=player.light,
                    coins=player.coins,
                    headroom=max(0, player.power - player.light),
                    risk=self._shot_overload_risk(player),
                )
            else:
                text = Localization.get(
                    locale,
                    "lightturret-stats-eliminated",
                    player=player.name,
                    power=player.power,
                    light=player.light,
                )
            items.append(MenuItem(text=text, id=f"player:{player.id}"))
        return items

    def _action_check_stats(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "lightturret_status",
            lambda _player, live_user: self._status_items(live_user.locale),
            focus_id="round",
        )

    # ======================================================================
    # Action resolution
    # ======================================================================

    def _set_pending_action(self, player: LightTurretPlayer, kind: str) -> None:
        self.pending_action_player_id = player.id
        self.pending_action_kind = kind
        self.pending_action_resolved = False

    def _clear_pending_action(self) -> None:
        self.pending_action_player_id = ""
        self.pending_action_kind = ""
        self.pending_action_resolved = False

    def _pending_actor(
        self, payload: dict, expected_kind: str
    ) -> LightTurretPlayer | None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, LightTurretPlayer):
            return None
        if player is not self.current_player or not player.alive:
            return None
        if (
            self.pending_action_player_id != player.id
            or self.pending_action_kind != expected_kind
        ):
            return None
        return player

    def _action_shoot(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return
        if self.has_active_sequence(tag=ACTION_SEQUENCE_TAG):
            return
        if self._should_confirm_risky_shot(player):
            return

        gain = random.randint(SHOT_MIN_GAIN, SHOT_MAX_GAIN)
        shoot_sound = f"game_lightturret/shoot{random.randint(1, 3)}.ogg"
        overloaded = player.light + gain > player.power
        payload = {
            "player_id": player.id,
            "gain": gain,
            "overloaded": overloaded,
        }
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(shoot_sound)],
                delay_after_ticks=ACTION_SOUND_DELAY_TICKS,
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("resolve_shoot", payload)],
                delay_after_ticks=RESULT_DELAY_TICKS,
            ),
        ]
        if overloaded:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            "game_lightturret/overpowered.ogg"
                        )
                    ],
                    delay_after_ticks=OVERLOAD_SOUND_DELAY_TICKS,
                )
            )
        beats.append(
            SequenceBeat(
                ops=[SequenceOperation.callback_op("complete_action", payload)]
            )
        )

        self._set_pending_action(player, "shoot")
        self.start_sequence(
            ACTION_SEQUENCE_ID,
            beats,
            tag=ACTION_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            replace_existing=False,
        )
        self.refresh_menus(player)

    def _action_upgrade(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return
        if self.has_active_sequence(tag=ACTION_SEQUENCE_TAG):
            return
        if player.coins < UPGRADE_COST:
            return

        self._clear_risky_confirmation(player)
        accident = random.random() < UPGRADE_ACCIDENT_CHANCE
        if accident:
            gain = random.randint(
                UPGRADE_ACCIDENT_LIGHT_MIN, UPGRADE_ACCIDENT_LIGHT_MAX
            )
            overloaded = player.light + gain > player.power
            payload = {
                "player_id": player.id,
                "accident": True,
                "gain": gain,
                "overloaded": overloaded,
            }
            beats = [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            "game_lightturret/upgrade.ogg"
                        )
                    ],
                    delay_after_ticks=ACTION_SOUND_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            "game_lightturret/upgrademerge.ogg"
                        ),
                        SequenceOperation.callback_op("resolve_upgrade", payload),
                    ],
                    delay_after_ticks=RESULT_DELAY_TICKS,
                ),
            ]
            if overloaded:
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(
                                "game_lightturret/overpowered.ogg"
                            )
                        ],
                        delay_after_ticks=OVERLOAD_SOUND_DELAY_TICKS,
                    )
                )
        else:
            gain = random.randint(UPGRADE_POWER_MIN, UPGRADE_POWER_MAX)
            payload = {
                "player_id": player.id,
                "accident": False,
                "gain": gain,
                "overloaded": False,
            }
            beats = [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            "game_lightturret/upgrade.ogg"
                        )
                    ],
                    delay_after_ticks=ACTION_SOUND_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("resolve_upgrade", payload)],
                    delay_after_ticks=RESULT_DELAY_TICKS,
                ),
            ]
        beats.append(
            SequenceBeat(
                ops=[SequenceOperation.callback_op("complete_action", payload)]
            )
        )

        self._set_pending_action(player, "upgrade")
        self.start_sequence(
            ACTION_SEQUENCE_ID,
            beats,
            tag=ACTION_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            replace_existing=False,
        )
        self.refresh_menus(player)

    def _resolve_shoot(self, player: LightTurretPlayer, payload: dict) -> bool:
        try:
            gain = int(payload.get("gain", 0))
        except (TypeError, ValueError):
            return False
        if not SHOT_MIN_GAIN <= gain <= SHOT_MAX_GAIN:
            return False

        coins_gained = gain * 2
        player.light += gain
        player.coins += coins_gained
        overloaded = player.light > player.power
        headroom = max(0, player.power - player.light)
        self._sync_team_scores()

        if overloaded:
            player.alive = False
            self._broadcast_actor_l(
                player,
                "lightturret-you-shoot-overload",
                "lightturret-player-shoots-overload",
                brief_personal_key="lightturret-you-shoot-overload-brief",
                brief_others_key="lightturret-player-shoots-overload-brief",
                gain=gain,
                coins=coins_gained,
                total_coins=player.coins,
                light=player.light,
                power=player.power,
                overload=player.light - player.power,
            )
        else:
            self._broadcast_actor_l(
                player,
                "lightturret-you-shoot",
                "lightturret-player-shoots",
                brief_personal_key="lightturret-you-shoot-brief",
                brief_others_key="lightturret-player-shoots-brief",
                gain=gain,
                coins=coins_gained,
                total_coins=player.coins,
                light=player.light,
                power=player.power,
                headroom=headroom,
            )
        self.refresh_menus()
        return True

    def _resolve_upgrade(self, player: LightTurretPlayer, payload: dict) -> bool:
        if player.coins < UPGRADE_COST:
            return False
        try:
            gain = int(payload.get("gain", 0))
        except (TypeError, ValueError):
            return False

        accident = bool(payload.get("accident", False))
        if accident and not (
            UPGRADE_ACCIDENT_LIGHT_MIN <= gain <= UPGRADE_ACCIDENT_LIGHT_MAX
        ):
            return False
        if not accident and not UPGRADE_POWER_MIN <= gain <= UPGRADE_POWER_MAX:
            return False

        player.coins -= UPGRADE_COST
        if accident:
            player.light += gain
            overloaded = player.light > player.power
            self._sync_team_scores()
            if overloaded:
                player.alive = False
                self._broadcast_actor_l(
                    player,
                    "lightturret-you-upgrade-overload",
                    "lightturret-player-upgrades-overload",
                    brief_personal_key="lightturret-you-upgrade-overload-brief",
                    brief_others_key="lightturret-player-upgrades-overload-brief",
                    cost=UPGRADE_COST,
                    coins=player.coins,
                    gain=gain,
                    light=player.light,
                    power=player.power,
                    overload=player.light - player.power,
                )
            else:
                self._broadcast_actor_l(
                    player,
                    "lightturret-you-upgrade-accident",
                    "lightturret-player-upgrades-accident",
                    brief_personal_key="lightturret-you-upgrade-accident-brief",
                    brief_others_key="lightturret-player-upgrades-accident-brief",
                    cost=UPGRADE_COST,
                    coins=player.coins,
                    gain=gain,
                    light=player.light,
                    power=player.power,
                    headroom=max(0, player.power - player.light),
                )
        else:
            player.power += gain
            self._broadcast_actor_l(
                player,
                "lightturret-you-upgrade",
                "lightturret-player-upgrades",
                brief_personal_key="lightturret-you-upgrade-brief",
                brief_others_key="lightturret-player-upgrades-brief",
                cost=UPGRADE_COST,
                coins=player.coins,
                gain=gain,
                power=player.power,
                light=player.light,
                headroom=max(0, player.power - player.light),
            )
        self.refresh_menus()
        return True

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id != ACTION_SEQUENCE_ID or self.status != "playing":
            return

        if callback_id == "resolve_shoot":
            player = self._pending_actor(payload, "shoot")
            if player and not self.pending_action_resolved:
                self.pending_action_resolved = self._resolve_shoot(player, payload)
            return

        if callback_id == "resolve_upgrade":
            player = self._pending_actor(payload, "upgrade")
            if player and not self.pending_action_resolved:
                self.pending_action_resolved = self._resolve_upgrade(player, payload)
            return

        if callback_id == "complete_action":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if (
                isinstance(player, LightTurretPlayer)
                and player is self.current_player
                and self.pending_action_player_id == player.id
                and self.pending_action_resolved
            ):
                self._clear_pending_action()
                self._on_turn_end()

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        self.cancel_sequences_by_tag(ACTION_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.end_reason = ""
        self._pending_finish = False
        self._clear_pending_action()

        active_players = self._active_light_players()
        self.team_manager.team_mode = "individual"
        self.team_manager.setup_teams([player.name for player in active_players])
        for player in active_players:
            player.power = self.options.starting_power
            player.light = 0
            player.coins = 0
            player.alive = True
            self._clear_risky_confirmation(player)
        self._sync_team_scores()
        self.set_turn_players(active_players)

        self.play_music("game_lightturret/music.ogg")
        self.play_sound("game_3cardpoker/roundstart.ogg")
        self._broadcast_global_l(
            "lightturret-intro",
            "lightturret-intro-brief",
            power=self.options.starting_power,
            rounds=self.options.max_rounds,
            cost=UPGRADE_COST,
        )
        self._start_round()

    def _start_round(self) -> None:
        alive_players = self._alive_players()
        if not alive_players:
            self._end_game(END_REASON_ALL_ELIMINATED)
            return

        self.round += 1
        self.set_turn_players(alive_players)
        self._broadcast_global_l(
            "lightturret-round-start",
            "lightturret-round-start-brief",
            round=self.round,
            total=self.options.max_rounds,
            alive=len(alive_players),
        )
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, LightTurretPlayer):
            self._end_game(END_REASON_ALL_ELIMINATED)
            return

        self._clear_risky_confirmation(player)
        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(12, 20))
        self.refresh_menus()

    def _on_turn_end(self) -> None:
        if not self._alive_players():
            self._end_game(END_REASON_ALL_ELIMINATED)
            return

        round_complete = self.turn_index >= len(self.turn_players) - 1
        if round_complete:
            if self.round >= self.options.max_rounds:
                self._end_game(END_REASON_MAX_ROUNDS)
            else:
                self._start_round()
            return

        self.advance_turn(announce=False)
        self._start_turn()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        # Complete games saved by older builds after their scheduled outro ends.
        if self._pending_finish and not self.scheduled_sounds:
            self._pending_finish = False
            self.game_active = False
            self.finish_game(show_end_screen=False)
            return

        for player in self._active_light_players():
            if player.risky_confirm_ticks > 0:
                player.risky_confirm_ticks -= 1
                if player.risky_confirm_ticks <= 0:
                    self._clear_risky_confirmation(player)

        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return None
        if self.round >= self.options.max_rounds:
            return "shoot"
        if player.coins < UPGRADE_COST:
            return "shoot"

        shot_risk = self._shot_overload_risk(player)
        leader_light = max(
            (opponent.light for opponent in self._active_light_players()),
            default=player.light,
        )
        trailing_by = leader_light - player.light
        rounds_remaining = self.options.max_rounds - self.round

        # Near the finish, a trailing bot must score rather than spend a turn
        # defending a position that cannot catch the leader.
        if rounds_remaining <= 1 or trailing_by >= 5:
            return "shoot"
        if shot_risk >= 50:
            return "upgrade"
        if shot_risk == 25 and player.light >= leader_light:
            return "upgrade"
        if (
            rounds_remaining >= 5
            and player.power - player.light <= SHOT_MAX_GAIN
            and self._upgrade_overload_risk(player) < shot_risk
        ):
            return "upgrade"
        return "shoot"

    def _winner_players(self) -> list[LightTurretPlayer]:
        players = self._active_light_players()
        if not players:
            return []
        top_light = max(player.light for player in players)
        return [player for player in players if player.light == top_light]

    def _announce_tie(self, winners: list[LightTurretPlayer]) -> None:
        winner_ids = {winner.id for winner in winners}
        winner_names = [winner.name for winner in winners]
        top_light = winners[0].light
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id in winner_ids:
                other_names = [
                    winner.name for winner in winners if winner.id != listener.id
                ]
                key = (
                    "lightturret-you-tie-brief"
                    if self._wants_brief(user)
                    else "lightturret-you-tie"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    players=Localization.format_list_and(user.locale, other_names),
                    light=top_light,
                )
            else:
                key = (
                    "lightturret-players-tie-brief"
                    if self._wants_brief(user)
                    else "lightturret-players-tie"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    players=Localization.format_list_and(user.locale, winner_names),
                    light=top_light,
                )

    def _end_game(self, reason: str) -> None:
        if self.status == "finished":
            return

        self.cancel_sequences_by_tag(ACTION_SEQUENCE_TAG)
        self._clear_pending_action()
        self.end_reason = reason
        self.status = "finished"
        self._sync_table_status()

        self._broadcast_global_l(
            f"lightturret-end-{reason.replace('_', '-')}",
            f"lightturret-end-{reason.replace('_', '-')}-brief",
            round=self.round,
            total=self.options.max_rounds,
        )
        winners = self._winner_players()
        if len(winners) == 1:
            winner = winners[0]
            self.play_sound("game_pig/win.ogg")
            self._broadcast_actor_l(
                winner,
                "lightturret-you-win",
                "lightturret-player-wins",
                brief_personal_key="lightturret-you-win-brief",
                brief_others_key="lightturret-player-wins-brief",
                light=winner.light,
                power=winner.power,
                survived=str(winner.alive).lower(),
            )
        elif winners:
            self._announce_tie(winners)

        self.refresh_menus()
        self.finish_game()

    # ======================================================================
    # Scores, validation, and results
    # ======================================================================

    def _sync_team_scores(self) -> None:
        for team in self.team_manager.teams:
            team.total_score = 0
        for player in self._active_light_players():
            team = self.team_manager.get_team(player.name)
            if team:
                team.total_score = player.light

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 5 <= self.options.starting_power <= 30:
            errors.append(
                (
                    "lightturret-error-starting-power-invalid",
                    {
                        "power": self.options.starting_power,
                        "min": 5,
                        "max": 30,
                    },
                )
            )
        if not 10 <= self.options.max_rounds <= 200:
            errors.append(
                (
                    "lightturret-error-max-rounds-invalid",
                    {
                        "rounds": self.options.max_rounds,
                        "min": 10,
                        "max": 200,
                    },
                )
            )
        return errors

    def _sorted_players(self) -> list[LightTurretPlayer]:
        return sorted(
            self._active_light_players(),
            key=lambda player: player.light,
            reverse=True,
        )

    def build_game_result(self) -> GameResult:
        sorted_players = self._sorted_players()
        winners = self._winner_players()
        winner_ids = {winner.id for winner in winners}
        rankings = []
        previous_light: int | None = None
        rank = 0
        for index, player in enumerate(sorted_players, 1):
            if player.light != previous_light:
                rank = index
                previous_light = player.light
            rankings.append(
                {
                    "members": [player.name],
                    "rank": rank,
                    "score": player.light,
                    "light": player.light,
                    "power": player.power,
                    "coins": player.coins,
                    "alive": player.alive,
                }
            )

        final_light = {player.name: player.light for player in sorted_players}
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
                for player in sorted_players
            ],
            custom_data={
                "winner_ids": [
                    player.id for player in sorted_players if player.id in winner_ids
                ],
                "winner_name": winners[0].name if len(winners) == 1 else None,
                "winner_light": winners[0].light if winners else 0,
                "final_scores": final_light,
                "final_light": final_light,
                "alive_status": {
                    player.name: player.alive for player in sorted_players
                },
                "rankings": rankings,
                "team_rankings": rankings,
                "rounds_played": self.round,
                "round_limit": self.options.max_rounds,
                "end_reason": self.end_reason,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        winner_ids = set(result.custom_data.get("winner_ids", []))
        winner_names = [
            player.player_name
            for player in result.player_results
            if player.player_id in winner_ids
        ]
        if len(winner_names) == 1:
            lines.append(
                Localization.get(
                    locale,
                    "lightturret-end-winner",
                    player=winner_names[0],
                    light=result.custom_data.get("winner_light", 0),
                )
            )
        elif winner_names:
            lines.append(
                Localization.get(
                    locale,
                    "lightturret-end-tie",
                    players=Localization.format_list_and(locale, winner_names),
                    light=result.custom_data.get("winner_light", 0),
                )
            )

        for index, entry in enumerate(result.custom_data.get("rankings", []), 1):
            members = entry.get("members", [])
            name = members[0] if members else Localization.get(locale, "unknown-player")
            status_key = (
                "lightturret-status-survived"
                if entry.get("alive", False)
                else "lightturret-status-eliminated"
            )
            lines.append(
                Localization.get(
                    locale,
                    "lightturret-line-format",
                    rank=entry.get("rank", index),
                    player=name,
                    light=entry.get("light", 0),
                    power=entry.get("power", 0),
                    coins=entry.get("coins", 0),
                    status=Localization.get(locale, status_key),
                )
            )
        return lines
