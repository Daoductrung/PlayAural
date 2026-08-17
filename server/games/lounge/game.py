"""Lounge chat room implementation.

The Lounge is a table whose whole point is talking. It has no play phase: it
stays in its open room state from the moment it is created until the last
person leaves, so anyone can walk in as a seated participant at any time,
table chat keeps working, and the room tools (emotes, nudges, topic, away,
dice and coin) are available immediately.
"""

from dataclasses import dataclass, field
import math
import random
import re

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, EditboxInput, MenuInput, Visibility
from ...game_utils.options import BoolOption, IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem, User


TICKS_PER_SECOND = 20
MAX_TOPIC_LENGTH = 120
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")

# Emote id -> sound asset. Every asset below already ships in the shared sound
# pack, so the Lounge needs no pack bump and no mandatory client update.
EMOTE_SOUNDS = {
    "wave": "join.ogg",
    "laugh": "game_citadels/thief_laugh1.ogg",
    "applaud": "game_uno/winround.ogg",
    "boo": "game_uno/buzzerplay.ogg",
    "toast": "game_bang/drink_beer.ogg",
    "facepalm": "lsmack.ogg",
    "think": "game_pirates/instinct1.ogg",
    "celebrate": "gamewin.ogg",
}
EMOTE_ORDER = (
    "wave",
    "laugh",
    "applaud",
    "boo",
    "toast",
    "facepalm",
    "think",
    "celebrate",
)

DICE_SOUND = "game_dice/dieThrow1.ogg"
COIN_SOUND = "game_citadels/coins_small.ogg"
NUDGE_SOUND = "mention.ogg"

ROOM_ACTION_LABELS = {
    "nudge": "lounge-nudge",
    "roll_dice": "lounge-roll-dice",
    "flip_coin": "lounge-flip-coin",
    "change_topic": "lounge-set-topic",
    "read_topic": "lounge-read-topic",
    "room_info": "lounge-room-info",
}
ROOM_ACTION_DESCRIPTIONS = {
    "nudge": "lounge-nudge-description",
    "roll_dice": "lounge-roll-dice-description",
    "flip_coin": "lounge-flip-coin-description",
    "toggle_away": "lounge-away-description",
    "change_topic": "lounge-set-topic-description",
    "read_topic": "lounge-read-topic-description",
    "room_info": "lounge-room-info-description",
}


@dataclass
class LoungePlayer(Player):
    """Per-person Lounge state."""

    away: bool = False
    cooldown_ticks: int = 0


@dataclass
class LoungeOptions(GameOptions):
    """Host-configurable Lounge settings."""

    allow_emotes: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lounge-set-allow-emotes",
            change_msg="lounge-option-changed-allow-emotes",
            description="lounge-desc-allow-emotes",
        )
    )
    allow_nudges: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lounge-set-allow-nudges",
            change_msg="lounge-option-changed-allow-nudges",
            description="lounge-desc-allow-nudges",
        )
    )
    allow_party_tools: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lounge-set-allow-party-tools",
            change_msg="lounge-option-changed-allow-party-tools",
            description="lounge-desc-allow-party-tools",
        )
    )
    action_cooldown: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=60,
            value_key="seconds",
            label="lounge-set-action-cooldown",
            change_msg="lounge-option-changed-action-cooldown",
            prompt="lounge-prompt-action-cooldown",
            description="lounge-desc-action-cooldown",
        )
    )


@dataclass
@register_game
class LoungeGame(Game):
    """A table dedicated to talking rather than playing."""

    players: list[LoungePlayer] = field(default_factory=list)
    options: LoungeOptions = field(default_factory=LoungeOptions)

    topic: str = ""
    topic_author: str = ""
    emote_count: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Lounge"

    @classmethod
    def get_type(cls) -> str:
        return "lounge"

    @classmethod
    def get_category(cls) -> str:
        return "misc"

    @classmethod
    def has_play_phase(cls) -> bool:
        """The room is live while it waits; it never starts anything."""
        return False

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return []

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> LoungePlayer:
        return LoungePlayer(id=player_id, name=name, is_bot=is_bot)

    # ======================================================================
    # Room lifecycle
    # ======================================================================

    def on_start(self) -> None:
        """The Lounge has no play phase, so starting keeps the room open.

        Nothing normally reaches this hook: ``_is_start_game_enabled`` and
        ``prestart_validate`` both refuse a start. It stays defensive so a
        direct call cannot leave the table in a gameplay status that would
        turn later arrivals into spectators.
        """
        self.status = "waiting"
        self.game_active = False
        self._sync_table_status()
        self.refresh_menus()

    def prestart_validate(self) -> list[str]:
        return ["lounge-cannot-start"]

    def on_tick(self) -> None:
        """Count down each person's room-action cooldown."""
        super().on_tick()
        for player in self.players:
            if player.cooldown_ticks > 0:
                player.cooldown_ticks -= 1

    def add_player(self, name: str, user: User) -> LoungePlayer:
        player = super().add_player(name, user)
        self._greet(player)
        return player

    def add_spectator(self, name: str, user: User) -> LoungePlayer:
        player = super().add_spectator(name, user)
        self._greet(player)
        return player

    def _greet(self, player: Player) -> None:
        """Tell one arrival what this table is and what it is talking about."""
        user = self.get_user(player)
        if not user or player.is_bot:
            return
        key = "lounge-welcome-spectator" if player.is_spectator else "lounge-welcome"
        user.speak_l(key, buffer="game")
        if self.topic:
            user.speak_l(
                "lounge-topic-current",
                buffer="game",
                player=self.topic_author,
                topic=self.topic,
            )

    # ======================================================================
    # Framework affordances the Lounge deliberately turns off
    # ======================================================================

    def _is_start_game_enabled(self, player: Player) -> str | None:
        """There is no game to start, so explain that instead of starting one."""
        return "lounge-cannot-start"

    def _is_start_game_hidden(self, player: Player) -> Visibility:
        """Keep the dead Start row out of the room menu.

        This is not readiness gating: the Lounge has no play phase at all, so a
        permanently disabled Start row would only add noise to the menu that is
        the room's main interface. Attempts through the Enter keybind still
        reach ``_is_start_game_enabled`` and hear the explanation.
        """
        return Visibility.HIDDEN

    def _is_add_bot_enabled(self, player: Player) -> str | None:
        return "lounge-no-bots"

    def _is_save_table_enabled(self, player: Player) -> str | None:
        return "lounge-no-save"

    def supports_score_actions(self) -> bool:
        """The Lounge keeps no scores."""
        return False

    # ======================================================================
    # Shared helpers
    # ======================================================================

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _seated_players(self) -> list[LoungePlayer]:
        return [player for player in self.players if not player.is_spectator]

    def _spectators(self) -> list[LoungePlayer]:
        return [player for player in self.players if player.is_spectator]

    def _cooldown_ticks(self) -> int:
        return max(0, int(self.options.action_cooldown)) * TICKS_PER_SECOND

    def _start_cooldown(self, player: Player) -> None:
        player.cooldown_ticks = self._cooldown_ticks()

    def _cooldown_reason(self, player: Player) -> tuple[str, dict] | None:
        """Return the remaining wait, in whole seconds, when one is running."""
        remaining = getattr(player, "cooldown_ticks", 0)
        if remaining <= 0:
            return None
        seconds = max(1, math.ceil(remaining / TICKS_PER_SECOND))
        return ("lounge-cooldown-wait", {"seconds": seconds})

    def _room_action_blocked(self, player: Player) -> str | tuple[str, dict] | None:
        """Shared guard for every seated-only room action."""
        if player.is_spectator:
            return "lounge-spectator-blocked"
        return self._cooldown_reason(player)

    def _is_room_action_hidden(self, player: Player) -> Visibility:
        """Room tools stay in the menu even while a cooldown is running.

        The room menu is a persistent list. Dropping rows while a cooldown
        ticks would destroy every client's focus anchor, so the rows remain
        visible and simply resolve as disabled.
        """
        return Visibility.HIDDEN if player.is_spectator else Visibility.VISIBLE

    def _is_emote_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if not self.options.allow_emotes:
            return "lounge-emotes-disabled"
        return self._room_action_blocked(player)

    def _is_nudge_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if not self.options.allow_nudges:
            return "lounge-nudges-disabled"
        return self._room_action_blocked(player)

    def _is_party_tool_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if not self.options.allow_party_tools:
            return "lounge-party-tools-disabled"
        return self._room_action_blocked(player)

    def _is_toggle_away_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "lounge-spectator-blocked"
        return None

    def _is_change_topic_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if player.is_spectator:
            return "lounge-spectator-blocked"
        if player.name != self.host:
            return ("lounge-topic-not-host", {"host": self.host})
        return None

    def _is_read_topic_enabled(self, player: Player) -> str | None:
        return None

    def _is_room_info_enabled(self, player: Player) -> str | None:
        return None

    def _is_touch_only_hidden(self, player: Player) -> Visibility:
        """Standard info rows are turn-menu buttons on touch clients only."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _get_room_action_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if action_id.startswith("emote_"):
            emote_id = action_id.removeprefix("emote_")
            return Localization.get(locale, f"lounge-emote-{emote_id}")
        if action_id == "toggle_away":
            key = (
                "lounge-mark-back"
                if getattr(player, "away", False)
                else "lounge-mark-away"
            )
            return Localization.get(locale, key)
        return Localization.get(locale, ROOM_ACTION_LABELS[action_id])

    def _get_room_action_description(self, player: Player, action_id: str) -> str | None:
        locale = self._player_locale(player)
        if action_id.startswith("emote_"):
            return Localization.get(locale, "lounge-emote-description")
        description_key = ROOM_ACTION_DESCRIPTIONS.get(action_id)
        if not description_key:
            return None
        return Localization.get(locale, description_key)

    # ======================================================================
    # Actions and menus
    # ======================================================================

    def create_turn_action_set(self, player: Player) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")

        for emote_id in EMOTE_ORDER:
            action_set.add(
                Action(
                    id=f"emote_{emote_id}",
                    label=Localization.get(locale, f"lounge-emote-{emote_id}"),
                    handler="_action_emote",
                    is_enabled="_is_emote_enabled",
                    is_hidden="_is_room_action_hidden",
                    get_label="_get_room_action_label",
                    get_description="_get_room_action_description",
                )
            )

        action_set.add(
            Action(
                id="nudge",
                label=Localization.get(locale, "lounge-nudge"),
                handler="_action_nudge",
                is_enabled="_is_nudge_enabled",
                is_hidden="_is_room_action_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
                input_request=MenuInput(
                    prompt="lounge-nudge-prompt",
                    options="_nudge_options",
                    option_label="_nudge_option_label",
                    pre_input_check="_nudge_pre_input_check",
                ),
            )
        )
        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "lounge-roll-dice"),
                handler="_action_roll_dice",
                is_enabled="_is_party_tool_enabled",
                is_hidden="_is_room_action_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
            )
        )
        action_set.add(
            Action(
                id="flip_coin",
                label=Localization.get(locale, "lounge-flip-coin"),
                handler="_action_flip_coin",
                is_enabled="_is_party_tool_enabled",
                is_hidden="_is_room_action_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
            )
        )
        action_set.add(
            Action(
                id="toggle_away",
                label=Localization.get(locale, "lounge-mark-away"),
                handler="_action_toggle_away",
                is_enabled="_is_toggle_away_enabled",
                is_hidden="_is_room_action_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
            )
        )
        action_set.add(
            Action(
                id="change_topic",
                label=Localization.get(locale, "lounge-set-topic"),
                handler="_action_change_topic",
                is_enabled="_is_change_topic_enabled",
                is_hidden="_is_room_action_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
                input_request=EditboxInput(
                    prompt="lounge-set-topic-prompt",
                    default="",
                ),
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)

        action_set.add(
            Action(
                id="read_topic",
                label=Localization.get(locale, "lounge-read-topic"),
                handler="_action_read_topic",
                is_enabled="_is_read_topic_enabled",
                is_hidden="_is_touch_only_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="room_info",
                label=Localization.get(locale, "lounge-room-info"),
                handler="_action_room_info",
                is_enabled="_is_room_info_enabled",
                is_hidden="_is_touch_only_hidden",
                get_label="_get_room_action_label",
                get_description="_get_room_action_description",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                ["read_topic", "room_info", "whos_at_table"],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        # The Lounge never leaves its open room state, so every room key is an
        # IDLE binding. "t", "s" and similar single letters are ACTIVE-only in
        # the base game class, so reusing "t" here cannot overlap with it.
        self.define_keybind(
            "t",
            "Read room topic",
            ["read_topic"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+t",
            "Set room topic",
            ["change_topic"],
            state=KeybindState.IDLE,
        )
        self.define_keybind(
            "r",
            "Room information",
            ["room_info"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "a",
            "Away or back",
            ["toggle_away"],
            state=KeybindState.IDLE,
        )
        self.define_keybind(
            "n",
            "Nudge someone",
            ["nudge"],
            state=KeybindState.IDLE,
        )
        self.define_keybind(
            "d",
            "Roll two dice",
            ["roll_dice"],
            state=KeybindState.IDLE,
        )
        self.define_keybind(
            "f",
            "Flip a coin",
            ["flip_coin"],
            state=KeybindState.IDLE,
        )

    # ======================================================================
    # Emotes
    # ======================================================================

    def _action_emote(self, player: Player, action_id: str) -> None:
        emote_id = action_id.removeprefix("emote_")
        sound = EMOTE_SOUNDS.get(emote_id)
        if not sound:
            return

        self.emote_count += 1
        self._start_cooldown(player)
        self.broadcast_sound(sound)
        self.broadcast_personal_l(
            player,
            f"lounge-emote-{emote_id}-you",
            f"lounge-emote-{emote_id}-other",
            buffer="game",
        )
        # Public room event: the emote counter and any open room information
        # box change for everyone present.
        self.refresh_menus()

    # ======================================================================
    # Nudges
    # ======================================================================

    def _nudge_candidates(self, player: Player) -> list[LoungePlayer]:
        return [
            other
            for other in self.players
            if other.id != player.id and not other.is_bot
        ]

    def _nudge_options(self, player: Player) -> list[str]:
        return [other.id for other in self._nudge_candidates(player)]

    def _nudge_option_label(self, player: Player, target_id: str) -> str:
        target = self.get_player_by_id(target_id)
        return target.name if target else target_id

    def _nudge_pre_input_check(self, player: Player, action_id: str) -> str | None:
        if not self._nudge_candidates(player):
            return "lounge-nudge-no-targets"
        return None

    def _action_nudge(self, player: Player, target_id: str, action_id: str) -> None:
        user = self.get_user(player)
        if target_id == player.id:
            if user:
                user.speak_l("lounge-nudge-self", buffer="game")
            return

        target = self.get_player_by_id(target_id)
        if not target:
            if user:
                user.speak_l(
                    "lounge-nudge-target-left",
                    buffer="game",
                    target=self._nudge_option_label(player, target_id),
                )
            return

        self._start_cooldown(player)
        target_user = self.get_user(target)
        if target_user:
            self.broadcast_sound(NUDGE_SOUND, audience=[target])
            target_user.speak_l(
                "lounge-nudge-target",
                buffer="game",
                player=player.name,
            )
        if user:
            user.speak_l("lounge-nudge-you", buffer="game", target=target.name)

        for listener in self.players:
            if listener.id in {player.id, target.id}:
                continue
            listener_user = self.get_user(listener)
            if not listener_user:
                continue
            listener_user.speak_l(
                "lounge-nudge-other",
                buffer="game",
                player=player.name,
                target=target.name,
            )

    # ======================================================================
    # Dice and coin
    # ======================================================================

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        first = random.randint(1, 6)  # nosec B311
        second = random.randint(1, 6)  # nosec B311
        self._start_cooldown(player)
        self.broadcast_sound(DICE_SOUND)
        self.broadcast_personal_l(
            player,
            "lounge-roll-you",
            "lounge-roll-other",
            buffer="game",
            first=first,
            second=second,
            total=first + second,
        )

    def _action_flip_coin(self, player: Player, action_id: str) -> None:
        heads = random.choice([True, False])  # nosec B311
        side_key = "lounge-coin-heads" if heads else "lounge-coin-tails"
        self._start_cooldown(player)
        self.broadcast_sound(COIN_SOUND)
        self.broadcast_personal_l(
            player,
            "lounge-flip-you",
            "lounge-flip-other",
            buffer="game",
            side=lambda locale: Localization.get(locale, side_key),
        )

    # ======================================================================
    # Away
    # ======================================================================

    def _action_toggle_away(self, player: Player, action_id: str) -> None:
        player.away = not getattr(player, "away", False)
        if player.away:
            self.broadcast_personal_l(
                player,
                "lounge-away-you",
                "lounge-away-other",
                buffer="game",
            )
        else:
            self.broadcast_personal_l(
                player,
                "lounge-back-you",
                "lounge-back-other",
                buffer="game",
            )
        # Public room state: the actor's own row label flips, and everyone
        # else's room information listing changes.
        self.refresh_menus()

    # ======================================================================
    # Topic
    # ======================================================================

    def _sanitize_topic(self, raw: str) -> str:
        """Collapse a submitted topic into one plain, speakable line."""
        cleaned = _CONTROL_CHARACTERS.sub(" ", str(raw or ""))
        return " ".join(cleaned.split())

    def _action_change_topic(
        self, player: Player, input_value: str, action_id: str
    ) -> None:
        user = self.get_user(player)
        if player.name != self.host:
            if user:
                user.speak_l("lounge-topic-not-host", buffer="game", host=self.host)
            return

        submitted = str(input_value or "")
        topic = self._sanitize_topic(submitted)

        if not topic:
            if submitted.strip():
                if user:
                    user.speak_l("lounge-topic-unreadable", buffer="game")
                return
            if not self.topic:
                if user:
                    user.speak_l("lounge-topic-already-empty", buffer="game")
                return
            self.topic = ""
            self.topic_author = ""
            self.broadcast_personal_l(
                player,
                "lounge-topic-cleared-you",
                "lounge-topic-cleared-other",
                buffer="game",
            )
            self.refresh_menus()
            return

        if len(topic) > MAX_TOPIC_LENGTH:
            if user:
                user.speak_l(
                    "lounge-topic-too-long",
                    buffer="game",
                    max=MAX_TOPIC_LENGTH,
                    count=len(topic),
                )
            return

        if topic == self.topic:
            if user:
                user.speak_l("lounge-topic-unchanged", buffer="game")
            return

        self.topic = topic
        self.topic_author = player.name
        self.broadcast_personal_l(
            player,
            "lounge-topic-set-you",
            "lounge-topic-set-other",
            buffer="game",
            topic=topic,
        )
        self.refresh_menus()

    def _action_read_topic(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not self.topic:
            user.speak_l("lounge-topic-none", buffer="game")
            return
        user.speak_l(
            "lounge-topic-current",
            buffer="game",
            player=self.topic_author,
            topic=self.topic,
        )

    # ======================================================================
    # Room information
    # ======================================================================

    def _room_info_items(self, viewer: Player, user: User) -> list[MenuItem]:
        locale = user.locale
        items: list[MenuItem] = [
            MenuItem(
                text=Localization.get(locale, "lounge-info-host", host=self.host),
                id="host",
            )
        ]

        if self.topic:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale, "lounge-info-topic", topic=self.topic
                    ),
                    id="topic",
                )
            )
            if self.topic_author:
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "lounge-info-topic-author",
                            player=self.topic_author,
                        ),
                        id="topic_author",
                    )
                )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "lounge-info-topic-none"),
                    id="topic",
                )
            )

        seated = self._seated_players()
        spectators = self._spectators()
        away_count = sum(1 for person in seated if person.away)

        items.append(
            MenuItem(
                text=Localization.get(
                    locale, "lounge-info-people", count=len(seated)
                ),
                id="people",
            )
        )
        if spectators:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale, "lounge-info-spectators", count=len(spectators)
                    ),
                    id="spectators",
                )
            )
        if away_count:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale, "lounge-info-away", count=away_count
                    ),
                    id="away",
                )
            )
        items.append(
            MenuItem(
                text=Localization.get(
                    locale, "lounge-info-emotes", count=self.emote_count
                ),
                id="emotes",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(
                    locale,
                    "lounge-info-settings",
                    emotes=self._on_off(locale, self.options.allow_emotes),
                    nudges=self._on_off(locale, self.options.allow_nudges),
                    party=self._on_off(locale, self.options.allow_party_tools),
                    cooldown=self.options.action_cooldown,
                ),
                id="settings",
            )
        )

        for person in seated:
            is_host = person.name == self.host
            if is_host and person.away:
                key = "lounge-info-person-host-away"
            elif is_host:
                key = "lounge-info-person-host"
            elif person.away:
                key = "lounge-info-person-away"
            else:
                key = "lounge-info-person"
            items.append(
                MenuItem(
                    text=Localization.get(locale, key, player=person.name),
                    id=f"player:{person.id}",
                )
            )

        for person in spectators:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale, "lounge-info-person-spectator", player=person.name
                    ),
                    id=f"player:{person.id}",
                )
            )

        return items

    @staticmethod
    def _on_off(locale: str, value: bool) -> str:
        return Localization.get(locale, "option-on" if value else "option-off")

    def _action_room_info(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "lounge_room_info",
            lambda viewer, viewer_user: self._room_info_items(viewer, viewer_user),
            focus_id="host",
        )
