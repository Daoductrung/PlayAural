"""Official-rule Skip-Bo implementation for PlayAural."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.menu_management_mixin import MenuBuild
from ...game_utils.options import IntOption, MenuOption, TeamModeOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...game_utils.teams import Team
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, GameOptions, Player
from ..registry import register_game
from . import cards
from .bot import choose_action as bot_choose_action
from .bot import choose_discard_pile, choose_play
from .cards import SkipBoCard

STOCK_STANDARD = "standard"
STOCK_SHORT = "short10"
STOCK_SHORT_FIFTEEN = "short15"
STOCK_MODES = [STOCK_STANDARD, STOCK_SHORT, STOCK_SHORT_FIFTEEN]
STOCK_MODE_LABELS = {
    STOCK_STANDARD: "skipbo-stock-mode-standard",
    STOCK_SHORT: "skipbo-stock-mode-short",
    STOCK_SHORT_FIFTEEN: "skipbo-stock-mode-short-15",
}

SCORING_SINGLE = "single"
SCORING_MATCH = "match"
SCORING_MODES = [SCORING_SINGLE, SCORING_MATCH]
SCORING_MODE_LABELS = {
    SCORING_SINGLE: "skipbo-scoring-single",
    SCORING_MATCH: "skipbo-scoring-match",
}

PARTNERSHIP_MODES = ["individual", "2v2", "2v2v2"]
DISCARD_PILE_COUNT = 4
BUILDING_PILE_COUNT = 4
HAND_SIZE = 5
OFFICIAL_MATCH_TARGET = 500
MIN_MATCH_TARGET = 25
MAX_MATCH_TARGET = 5000
STANDARD_STOCK_SMALL_TABLE = 30
STANDARD_STOCK_LARGE_TABLE = 20
STANDARD_STOCK_PLAYER_CUTOFF = 4
QUICK_STOCK_TEN = 10
QUICK_STOCK_FIFTEEN = 15
WIN_BONUS_POINTS = 25
REMAINING_STOCK_CARD_POINTS = 5
NEXT_ROUND_SEQUENCE_ID = "skipbo_next_round"
NEXT_ROUND_SEQUENCE_TAG = "skipbo_round_transition"
NEXT_ROUND_DELAY_TICKS = 3 * 20
SOUND_DRAW_FAMILY = "game_cards/draw"
SOUND_PLAY_FAMILY = "game_cards/play"
SOUND_DISCARD_FAMILY = "game_cards/discard"
SOUND_SHUFFLE_FAMILY = "game_cards/shuffle"
SOUND_RECYCLE = "game_cards/small_shuffle.ogg"
SOUND_GAME_WIN = "gamewin.ogg"
CARD_ACTION_PREFIX = "use_"
BUILDING_MOVE_PREFIX = "building_"
DISCARD_MOVE_PREFIX = "discard_"


@dataclass
class SkipBoOptions(GameOptions):
    """Official variants and match settings for Skip-Bo."""

    stock_mode: str = option_field(
        MenuOption(
            default=STOCK_STANDARD,
            choices=STOCK_MODES,
            choice_labels=STOCK_MODE_LABELS,
            value_key="mode",
            label="skipbo-set-stock-mode",
            prompt="skipbo-select-stock-mode",
            change_msg="skipbo-option-changed-stock-mode",
            description="skipbo-desc-stock-mode",
        )
    )
    scoring_mode: str = option_field(
        MenuOption(
            default=SCORING_SINGLE,
            choices=SCORING_MODES,
            choice_labels=SCORING_MODE_LABELS,
            value_key="mode",
            label="skipbo-set-scoring-mode",
            prompt="skipbo-select-scoring-mode",
            change_msg="skipbo-option-changed-scoring-mode",
            description="skipbo-desc-scoring-mode",
        )
    )
    winning_score: int = option_field(
        IntOption(
            default=OFFICIAL_MATCH_TARGET,
            min_val=MIN_MATCH_TARGET,
            max_val=MAX_MATCH_TARGET,
            value_key="score",
            label="skipbo-set-winning-score",
            prompt="skipbo-enter-winning-score",
            change_msg="skipbo-option-changed-winning-score",
            description="skipbo-desc-winning-score",
        ),
        visible_when=("scoring_mode", lambda value: value == SCORING_MATCH),
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            choices=PARTNERSHIP_MODES,
            value_key="mode",
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
            description="skipbo-desc-team-mode",
        )
    )


@dataclass
class SkipBoPlayer(Player):
    hand: list[SkipBoCard] = field(default_factory=list)
    stock_pile: list[SkipBoCard] = field(default_factory=list)
    discard_piles: list[list[SkipBoCard]] = field(
        default_factory=lambda: [[] for _ in range(DISCARD_PILE_COUNT)]
    )
    score: int = 0


@dataclass(frozen=True)
class CardSource:
    action_id: str
    source_kind: str
    owner: SkipBoPlayer
    source_pile_index: int
    card: SkipBoCard


@dataclass(frozen=True)
class PlayChoice:
    source: CardSource
    building_pile_index: int
    needed_value: int

    @property
    def action_id(self) -> str:
        return self.source.action_id

    @property
    def source_kind(self) -> str:
        return self.source.source_kind

    @property
    def owner(self) -> SkipBoPlayer:
        return self.source.owner

    @property
    def source_pile_index(self) -> int:
        return self.source.source_pile_index

    @property
    def card(self) -> SkipBoCard:
        return self.source.card


@register_game
@dataclass
class SkipBoGame(Game):
    """A faithful, accessible implementation of the classic sequencing game."""

    players: list[SkipBoPlayer] = field(default_factory=list)
    options: SkipBoOptions = field(default_factory=SkipBoOptions)
    deck: list[SkipBoCard] = field(default_factory=list)
    completed_cards: list[SkipBoCard] = field(default_factory=list)
    building_piles: list[list[SkipBoCard]] = field(
        default_factory=lambda: [[] for _ in range(BUILDING_PILE_COUNT)]
    )
    building_values: list[int] = field(
        default_factory=lambda: [0 for _ in range(BUILDING_PILE_COUNT)]
    )
    dealer_index: int = -1
    winner_team_index: int = -1

    @classmethod
    def get_name(cls) -> str:
        return "Skip-Bo"

    @classmethod
    def get_type(cls) -> str:
        return "skipbo"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> SkipBoPlayer:
        return SkipBoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ------------------------------------------------------------------
    # Actions and menus
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: SkipBoPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        self._populate_turn_actions(action_set, player)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        def add_info_action(
            action_id: str,
            label_key: str,
            handler: str,
            *,
            private: bool = False,
        ) -> None:
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label_key),
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

        add_info_action(
            "read_building_piles",
            "skipbo-read-building-piles",
            "_action_read_building_piles",
        )
        add_info_action(
            "read_stock_piles",
            "skipbo-read-stock-piles",
            "_action_read_stock_piles",
        )
        add_info_action(
            "read_own_discard_piles",
            "skipbo-read-own-discard-piles",
            "_action_read_own_discard_piles",
            private=True,
        )
        action_set.add(
            Action(
                id="read_discard_piles",
                label=Localization.get(locale, "skipbo-read-discard-piles"),
                handler="_action_read_discard_piles",
                is_enabled="_is_other_discard_info_enabled",
                is_hidden="_is_touch_public_info_hidden",
                input_request=MenuInput(
                    prompt="skipbo-select-discard-owner",
                    options="_discard_owner_options",
                    option_label="_discard_owner_option_label",
                ),
                include_spectators=True,
            )
        )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_building_piles",
                    "read_stock_piles",
                    "read_own_discard_piles",
                    "read_discard_piles",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "c",
            "View building piles",
            ["read_building_piles"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            "View stock piles",
            ["read_stock_piles"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "v",
            "View your discard piles",
            ["read_own_discard_piles"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "shift+v",
            "View another player's discard piles",
            ["read_discard_piles"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def build_menu_items(self, player: Player, user) -> MenuBuild:
        menu = super().build_menu_items(player, user)
        if (
            self.status != "playing"
            or self.is_sequence_gameplay_locked()
            or not isinstance(player, SkipBoPlayer)
            or player.is_spectator
            or self.current_player == player
            or player.hand
        ):
            return menu

        menu.items.insert(
            0,
            MenuItem(
                text=Localization.get(user.locale, "skipbo-hand-empty"),
                id="skipbo_hand_empty",
                read_only=True,
            ),
        )
        return menu

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, SkipBoPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        turn_set.remove_by_prefix(CARD_ACTION_PREFIX)
        turn_set.remove("end_turn_empty")
        self._populate_turn_actions(turn_set, player)

    def _populate_turn_actions(self, turn_set: ActionSet, player: SkipBoPlayer) -> None:
        if self.status != "playing" or player.is_spectator:
            return
        if self.is_sequence_gameplay_locked():
            return

        sources = self._card_sources(player)
        legal_source_ids = {
            choice.action_id for choice in self._legal_play_choices(player)
        }
        for source in sources:
            if (
                source.source_kind != "hand"
                and source.action_id not in legal_source_ids
            ):
                continue
            move_count = len(self._move_options_for_source(player, source))
            input_request = None
            if self.current_player == player and move_count > 1:
                input_request = MenuInput(
                    prompt="skipbo-select-card-move",
                    options="_move_options_for_pending_card",
                    option_label="_card_move_option_label",
                    bot_select="_bot_select_card_move",
                    locks_gameplay=True,
                )
            turn_set.add(
                Action(
                    id=source.action_id,
                    label="",
                    handler="_action_use_card",
                    is_enabled="_is_card_action_enabled",
                    is_hidden="_is_card_action_hidden",
                    get_label="_get_card_action_label",
                    get_description="_get_card_action_description",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )

        if not player.hand and not self._draw_available():
            turn_set.add(
                Action(
                    id="end_turn_empty",
                    label=self._localize(player, "skipbo-end-turn-empty"),
                    handler="_action_end_turn_empty",
                    is_enabled="_is_end_turn_empty_enabled",
                    is_hidden="_is_turn_action_hidden",
                    description=self._localize(player, "skipbo-end-turn-empty-desc"),
                    show_in_actions_menu=False,
                )
            )

    # ------------------------------------------------------------------
    # Setup and lifecycle
    # ------------------------------------------------------------------

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        if self.options.stock_mode not in STOCK_MODES:
            errors.append("skipbo-error-invalid-stock-mode")
        if self.options.scoring_mode not in SCORING_MODES:
            errors.append("skipbo-error-invalid-scoring-mode")
        if self.options.scoring_mode == SCORING_MATCH and (
            not isinstance(self.options.winning_score, int)
            or isinstance(self.options.winning_score, bool)
            or not MIN_MATCH_TARGET <= self.options.winning_score <= MAX_MATCH_TARGET
        ):
            errors.append(
                (
                    "skipbo-error-winning-score-range",
                    {
                        "value": self.options.winning_score,
                        "min": MIN_MATCH_TARGET,
                        "max": MAX_MATCH_TARGET,
                    },
                )
            )

        if self.options.team_mode not in PARTNERSHIP_MODES or self._validate_team_mode(
            self.options.team_mode
        ):
            errors.append("skipbo-error-partnership-player-count")
        return errors

    def on_start(self) -> None:
        self.cancel_sequences_by_tag(NEXT_ROUND_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self.game_active = True
        self.round = 0
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.winner_team_index = -1
        self._sync_table_status()

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, SkipBoPlayer)
        ]
        self._setup_team_manager_for_start(self.options.team_mode, active_players)
        self._team_manager.reset_all_scores()
        for player in active_players:
            player.score = 0

        ordered_players = self._get_team_turn_players(active_players)
        self.set_turn_players(ordered_players)
        self.dealer_index = random.randrange(len(ordered_players))
        self._start_new_round(rotate_dealer=False)

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if (
            self.game_active
            and self.status == "playing"
            and not self.is_sequence_bot_paused()
        ):
            BotHelper.on_tick(self)

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id == NEXT_ROUND_SEQUENCE_ID and callback_id == "start_next_round":
            self._start_new_round(rotate_dealer=True)

    def _start_new_round(self, *, rotate_dealer: bool) -> None:
        self.cancel_sequences_by_tag(NEXT_ROUND_SEQUENCE_TAG)
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, SkipBoPlayer)
        ]
        if not active_players or not self.turn_player_ids:
            return

        self.round += 1
        if rotate_dealer:
            self.dealer_index = (self.dealer_index + 1) % len(self.turn_player_ids)

        self.deck = cards.build_deck()
        cards.shuffle(self.deck)
        self.play_sound_family(SOUND_SHUFFLE_FAMILY)
        self.completed_cards = []
        self.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
        self.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
        stock_count = self._stock_size(len(active_players))

        for player in active_players:
            player.hand = []
            player.stock_pile = []
            player.discard_piles = [[] for _ in range(DISCARD_PILE_COUNT)]
            player.bot_pending_action = None
            player.bot_think_ticks = 0

        for _ in range(stock_count):
            for player in active_players:
                player.stock_pile.append(self.deck.pop())

        self.turn_index = (self.dealer_index + 1) % len(self.turn_player_ids)
        quick = self.options.stock_mode in (STOCK_SHORT, STOCK_SHORT_FIFTEEN)
        if self.options.scoring_mode == SCORING_MATCH:
            start_key = (
                "skipbo-match-game-start-quick" if quick else "skipbo-match-game-start"
            )
            self.broadcast_l(
                start_key,
                buffer="game",
                game=self.round,
                stock_count=stock_count,
            )
        else:
            start_key = "skipbo-game-start-quick" if quick else "skipbo-game-start"
            self.broadcast_l(start_key, buffer="game", stock_count=stock_count)
        for owner in active_players:
            top = owner.stock_pile[-1]
            self.broadcast_personal_l(
                owner,
                "skipbo-initial-stock-you",
                "skipbo-initial-stock-player",
                buffer="game",
                card=lambda locale, top=top: cards.format_card(top, locale),
            )
        self._start_turn()

    def _stock_size(self, player_count: int) -> int:
        if self.options.stock_mode == STOCK_SHORT:
            return QUICK_STOCK_TEN
        if self.options.stock_mode == STOCK_SHORT_FIFTEEN:
            return QUICK_STOCK_FIFTEEN
        return (
            STANDARD_STOCK_SMALL_TABLE
            if player_count <= STANDARD_STOCK_PLAYER_CUTOFF
            else STANDARD_STOCK_LARGE_TABLE
        )

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, SkipBoPlayer):
            return
        self.announce_turn()
        self._draw_to_five(player, reason="turn")
        BotHelper.jolt_bot(player)
        self.refresh_menus()

    def _advance_to_next_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    # ------------------------------------------------------------------
    # Cards, sources, and legal plays
    # ------------------------------------------------------------------

    def _draw_available(self) -> bool:
        return bool(self.deck or self.completed_cards)

    def _replenish_draw_pile(self) -> bool:
        if self.deck:
            return False

        if not self.completed_cards:
            return False

        count = len(self.completed_cards)
        self.deck = self.completed_cards
        self.completed_cards = []

        cards.shuffle(self.deck)
        self.play_sound(SOUND_RECYCLE)
        self.broadcast_l("skipbo-recycle-completed", buffer="game", count=count)
        return True

    def _take_draw_card(self) -> SkipBoCard | None:
        if not self.deck:
            self._replenish_draw_pile()
        return self.deck.pop() if self.deck else None

    def _draw_to_five(self, player: SkipBoPlayer, *, reason: str) -> int:
        drawn: list[SkipBoCard] = []
        while len(player.hand) < HAND_SIZE:
            card = self._take_draw_card()
            if card is None:
                break
            player.hand.append(card)
            drawn.append(card)

        if drawn:
            self.play_sound_family(SOUND_DRAW_FAMILY)
            personal_key = (
                "skipbo-refill-you" if reason == "refill" else "skipbo-draw-turn-you"
            )
            public_key = (
                "skipbo-refill-player"
                if reason == "refill"
                else "skipbo-draw-turn-player"
            )
            self.broadcast_personal_l(
                player,
                personal_key,
                public_key,
                buffer="game",
                count=len(drawn),
                hand=lambda locale: self._format_hand(player, locale),
            )
        elif reason == "refill" and not player.hand:
            self.broadcast_personal_l(
                player,
                "skipbo-no-refill-you",
                "skipbo-no-refill-player",
                buffer="game",
            )
        return len(drawn)

    def _playable_source_owners(self, player: SkipBoPlayer) -> list[SkipBoPlayer]:
        team = self._team_manager.get_team(player.name)
        if not team or self.options.team_mode == "individual":
            return [player]
        members = set(team.members)
        return [
            candidate
            for candidate in self.get_active_players()
            if isinstance(candidate, SkipBoPlayer) and candidate.name in members
        ]

    @staticmethod
    def _source_action_id(
        source_kind: str,
        owner: SkipBoPlayer,
        source_pile_index: int,
        card: SkipBoCard,
    ) -> str:
        source_id = {
            "hand": f"h_{card.id}",
            "stock": f"s_{owner.id}_{card.id}",
            "discard": f"d_{owner.id}_{source_pile_index}_{card.id}",
        }[source_kind]
        return f"{CARD_ACTION_PREFIX}{source_id}"

    def _make_card_source(
        self,
        source_kind: str,
        owner: SkipBoPlayer,
        source_pile_index: int,
        card: SkipBoCard,
    ) -> CardSource:
        return CardSource(
            action_id=self._source_action_id(
                source_kind, owner, source_pile_index, card
            ),
            source_kind=source_kind,
            owner=owner,
            source_pile_index=source_pile_index,
            card=card,
        )

    def _card_sources(self, player: SkipBoPlayer) -> list[CardSource]:
        sources: list[CardSource] = []
        if self.current_player == player:
            owners = self._playable_source_owners(player)
            for owner in owners:
                if owner.stock_pile:
                    sources.append(
                        self._make_card_source("stock", owner, -1, owner.stock_pile[-1])
                    )
            for owner in owners:
                for pile_index, pile in enumerate(owner.discard_piles):
                    if pile:
                        sources.append(
                            self._make_card_source(
                                "discard", owner, pile_index, pile[-1]
                            )
                        )
        for card in sorted(player.hand, key=cards.sort_key):
            sources.append(self._make_card_source("hand", player, -1, card))
        return sources

    def _building_needed(self, pile_index: int) -> int:
        return self.building_values[pile_index] + 1

    def _legal_targets(self, card: SkipBoCard) -> list[int]:
        return [
            index
            for index in range(BUILDING_PILE_COUNT)
            if card.is_wild or card.value == self._building_needed(index)
        ]

    def _legal_play_choices(self, player: SkipBoPlayer) -> list[PlayChoice]:
        if self.status != "playing" or self.current_player != player:
            return []
        choices: list[PlayChoice] = []
        for source in self._card_sources(player):
            for building_index in self._legal_targets(source.card):
                choices.append(
                    PlayChoice(
                        source=source,
                        building_pile_index=building_index,
                        needed_value=self._building_needed(building_index),
                    )
                )
        return choices

    def _source_for_action(
        self, player: SkipBoPlayer, action_id: str
    ) -> CardSource | None:
        return next(
            (
                source
                for source in self._card_sources(player)
                if source.action_id == action_id
            ),
            None,
        )

    def _building_choices_for_source(
        self, player: SkipBoPlayer, source: CardSource
    ) -> list[PlayChoice]:
        return [
            choice
            for choice in self._legal_play_choices(player)
            if choice.action_id == source.action_id
        ]

    def _choice_for_move(
        self, player: SkipBoPlayer, source: CardSource, move_id: str
    ) -> PlayChoice | None:
        pile_index = self._move_index(move_id, BUILDING_MOVE_PREFIX)
        if pile_index is None:
            return None
        return next(
            (
                choice
                for choice in self._building_choices_for_source(player, source)
                if choice.building_pile_index == pile_index
            ),
            None,
        )

    def _remove_source_card(self, player: SkipBoPlayer, choice: PlayChoice) -> bool:
        if choice.source_kind == "hand":
            for index, card in enumerate(player.hand):
                if card.id == choice.card.id:
                    player.hand.pop(index)
                    return True
            return False
        if choice.source_kind == "stock":
            pile = choice.owner.stock_pile
        else:
            pile = choice.owner.discard_piles[choice.source_pile_index]
        if not pile or pile[-1].id != choice.card.id:
            return False
        pile.pop()
        return True

    # ------------------------------------------------------------------
    # Gameplay action handlers
    # ------------------------------------------------------------------

    def _action_use_card(self, player: Player, *args: str) -> None:
        if not isinstance(player, SkipBoPlayer):
            return
        input_value = args[0] if len(args) == 2 else None
        action_id = args[-1] if args else ""
        source = self._source_for_action(player, action_id)
        if source is None:
            return

        options = self._move_options_for_source(player, source)
        if input_value is None:
            if len(options) != 1:
                return
            input_value = options[0]
        if input_value not in options:
            return

        choice = self._choice_for_move(player, source, input_value)
        if choice is not None:
            self._execute_building_play(player, choice)
            return

        pile_index = self._move_index(input_value, DISCARD_MOVE_PREFIX)
        if source.source_kind != "hand" or pile_index is None:
            return
        self._execute_discard(player, source.card, pile_index)

    def _execute_building_play(self, player: SkipBoPlayer, choice: PlayChoice) -> None:
        if not self._remove_source_card(player, choice):
            return

        building = self.building_piles[choice.building_pile_index]
        building.append(choice.card)
        self.building_values[choice.building_pile_index] = choice.needed_value
        self.play_sound_family(SOUND_PLAY_FAMILY)
        self._broadcast_play(player, choice)

        completed = choice.needed_value == cards.MAX_NUMBER
        if completed:
            self.completed_cards.extend(building)
            self.building_piles[choice.building_pile_index] = []
            self.building_values[choice.building_pile_index] = 0
            self.broadcast_personal_l(
                player,
                "skipbo-complete-building-you",
                "skipbo-complete-building-player",
                buffer="game",
                pile=choice.building_pile_index + 1,
            )

        if choice.source_kind == "stock":
            if choice.owner.stock_pile:
                self._announce_stock_top(choice.owner)
            else:
                winning_team = self._team_manager.get_team(choice.owner.name)
                if winning_team and self._team_has_empty_stock(winning_team):
                    self._finish_round(winning_team)
                    return
                self.broadcast_personal_l(
                    choice.owner,
                    "skipbo-stock-cleared-you",
                    "skipbo-stock-cleared-player",
                    buffer="game",
                )

        if not player.hand:
            self._draw_to_five(player, reason="refill")

        self._focus_after_play(player, choice.building_pile_index)
        BotHelper.jolt_bot(player)
        self.refresh_menus()

    def _execute_discard(
        self, player: SkipBoPlayer, card: SkipBoCard, pile_index: int
    ) -> None:
        if card not in player.hand or pile_index not in range(DISCARD_PILE_COUNT):
            return

        player.hand.remove(card)
        player.discard_piles[pile_index].append(card)
        self.play_sound_family(SOUND_DISCARD_FAMILY)
        self.broadcast_personal_l(
            player,
            "skipbo-discard-you",
            "skipbo-discard-player",
            buffer="game",
            card=lambda locale: cards.format_card(card, locale),
            pile=pile_index + 1,
        )
        self._advance_to_next_turn()
        self._focus_after_discard(player, card)

    def _action_end_turn_empty(self, player: Player, action_id: str) -> None:
        if self._is_end_turn_empty_enabled(player) is not None:
            return
        self.broadcast_personal_l(
            player,
            "skipbo-empty-end-you",
            "skipbo-empty-end-player",
            buffer="game",
        )
        self._advance_to_next_turn()

    # ------------------------------------------------------------------
    # Action labels, inputs, and guards
    # ------------------------------------------------------------------

    def _localize(self, player: Player, key: str, **kwargs) -> str:
        user = self.get_user(player)
        return Localization.get(user.locale if user else "en", key, **kwargs)

    def _source_label(
        self,
        listener: Player,
        source_kind: str,
        owner: SkipBoPlayer,
        source_pile_index: int,
        locale: str,
    ) -> str:
        is_owner = listener.id == owner.id
        if source_kind == "hand":
            key = "skipbo-source-your-hand" if is_owner else "skipbo-source-player-hand"
            return Localization.get(locale, key, owner=owner.name)
        if source_kind == "stock":
            key = (
                "skipbo-source-your-stock" if is_owner else "skipbo-source-player-stock"
            )
            return Localization.get(locale, key, owner=owner.name)
        key = (
            "skipbo-source-your-discard" if is_owner else "skipbo-source-player-discard"
        )
        return Localization.get(
            locale, key, owner=owner.name, pile=source_pile_index + 1
        )

    def _get_card_action_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, SkipBoPlayer):
            return ""
        source = self._source_for_action(player, action_id)
        if source is None:
            return self._localize(player, "skipbo-error-card-changed")
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if self.current_player != player:
            return Localization.get(
                locale,
                "skipbo-hand-menu-card",
                card=cards.format_card(source.card, locale),
            )

        choices = self._building_choices_for_source(player, source)
        if source.source_kind != "hand" and len(choices) == 1:
            choice = choices[0]
            return Localization.get(
                locale,
                "skipbo-play-action",
                card=cards.format_card(
                    source.card, locale, wild_as=choice.needed_value
                ),
                source=self._compact_source_label(player, source, locale),
                pile=choice.building_pile_index + 1,
            )
        return Localization.get(
            locale,
            "skipbo-card-action",
            card=cards.format_card(source.card, locale),
            source=self._compact_source_label(player, source, locale),
        )

    def _compact_source_label(
        self, player: SkipBoPlayer, source: CardSource, locale: str
    ) -> str:
        if source.source_kind == "hand":
            return Localization.get(locale, "skipbo-action-source-hand")
        is_owner = player.id == source.owner.id
        if source.source_kind == "stock":
            key = (
                "skipbo-action-source-stock"
                if is_owner
                else "skipbo-action-source-player-stock"
            )
            return Localization.get(locale, key, owner=source.owner.name)
        key = (
            "skipbo-action-source-discard"
            if is_owner
            else "skipbo-action-source-player-discard"
        )
        return Localization.get(
            locale,
            key,
            owner=source.owner.name,
            pile=source.source_pile_index + 1,
        )

    def _get_card_action_description(
        self, player: Player, action_id: str
    ) -> str | None:
        if not isinstance(player, SkipBoPlayer) or self.current_player != player:
            return None
        source = self._source_for_action(player, action_id)
        if source is None:
            return None
        choices = self._building_choices_for_source(player, source)
        if source.source_kind != "hand" and len(choices) <= 1:
            return None

        user = self.get_user(player)
        piles = Localization.format_list_and(
            user.locale if user else "en",
            [str(choice.building_pile_index + 1) for choice in choices],
        )
        if source.source_kind == "hand" and choices:
            return self._localize(
                player, "skipbo-card-desc-play-or-discard", piles=piles
            )
        if source.source_kind == "hand":
            return self._localize(player, "skipbo-card-desc-discard-only")
        return self._localize(player, "skipbo-card-desc-choose-building", piles=piles)

    def _focus_after_play(self, player: SkipBoPlayer, building_pile_index: int) -> None:
        """Keep the actor on a useful, deterministic continuation."""

        if player.is_bot:
            return
        choices = self._legal_play_choices(player)
        next_choice = next(
            (
                candidate
                for candidate in choices
                if candidate.building_pile_index == building_pile_index
            ),
            choices[0] if choices else None,
        )
        if next_choice is not None:
            self.request_menu_focus(player, next_choice.action_id)
            return
        ordered_hand = sorted(player.hand, key=cards.sort_key)
        if ordered_hand:
            self.request_menu_focus(
                player,
                self._source_action_id("hand", player, -1, ordered_hand[0]),
            )
        elif not self._draw_available():
            self.request_menu_focus(player, "end_turn_empty")

    def _focus_after_discard(self, player: SkipBoPlayer, discarded: SkipBoCard) -> None:
        """Move focus to the nearest surviving private hand row."""

        if player.is_bot:
            return
        ordered_hand = sorted(player.hand, key=cards.sort_key)
        if not ordered_hand:
            self.request_menu_focus(player, "skipbo_hand_empty")
            return

        discarded_key = cards.sort_key(discarded)
        next_card = next(
            (card for card in ordered_hand if cards.sort_key(card) > discarded_key),
            ordered_hand[-1],
        )
        self.request_menu_focus(
            player, self._source_action_id("hand", player, -1, next_card)
        )

    def _should_prompt_for_action_input(self, action: Action, player: Player) -> bool:
        if action.id == "read_discard_piles" and isinstance(
            action.input_request, MenuInput
        ):
            return len(self._discard_owner_options(player)) > 1
        return super()._should_prompt_for_action_input(action, player)

    @staticmethod
    def _move_index(move_id: str, prefix: str) -> int | None:
        if not move_id.startswith(prefix):
            return None
        try:
            index = int(move_id.removeprefix(prefix))
        except ValueError:
            return None
        return index

    def _move_options_for_source(
        self, player: SkipBoPlayer, source: CardSource
    ) -> list[str]:
        options = [
            f"{BUILDING_MOVE_PREFIX}{choice.building_pile_index}"
            for choice in self._building_choices_for_source(player, source)
        ]
        if source.source_kind == "hand":
            options.extend(
                f"{DISCARD_MOVE_PREFIX}{index}" for index in range(DISCARD_PILE_COUNT)
            )
        return options

    def _move_options_for_pending_card(self, player: Player) -> list[str]:
        if not isinstance(player, SkipBoPlayer):
            return []
        source = self._source_for_action(
            player, self._pending_actions.get(player.id, "")
        )
        return self._move_options_for_source(player, source) if source else []

    def _card_move_option_label(self, player: Player, move_id: str) -> str:
        if not isinstance(player, SkipBoPlayer):
            return move_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        source = self._source_for_action(
            player, self._pending_actions.get(player.id, "")
        )
        if source is None:
            return self._localize(player, "skipbo-error-card-changed")

        choice = self._choice_for_move(player, source, move_id)
        if choice is not None:
            card = cards.format_card(source.card, locale, wild_as=choice.needed_value)
            pile = self.building_piles[choice.building_pile_index]
            key = "skipbo-move-building-top" if pile else "skipbo-move-building-empty"
            return Localization.get(
                locale,
                key,
                pile=choice.building_pile_index + 1,
                current=self.building_values[choice.building_pile_index],
                card=card,
            )

        pile_index = self._move_index(move_id, DISCARD_MOVE_PREFIX)
        if pile_index is None or pile_index not in range(DISCARD_PILE_COUNT):
            return self._localize(player, "skipbo-error-card-changed")
        pile = player.discard_piles[pile_index]
        key = "skipbo-move-discard-top" if pile else "skipbo-move-discard-empty"
        return Localization.get(
            locale,
            key,
            pile=pile_index + 1,
            top=cards.format_card(pile[-1], locale) if pile else "",
        )

    def _bot_select_card_move(self, player: Player, options: list[str]) -> str | None:
        if not isinstance(player, SkipBoPlayer):
            return options[0] if options else None
        source = self._source_for_action(
            player, self._pending_actions.get(player.id, "")
        )
        if source is None:
            return options[0] if options else None
        building_choices = self._building_choices_for_source(player, source)
        if building_choices:
            selected = choose_play(self, player, building_choices)
            return f"{BUILDING_MOVE_PREFIX}{selected.building_pile_index}"
        return f"{DISCARD_MOVE_PREFIX}{choose_discard_pile(self, player, source.card)}"

    def _turn_action_guard(
        self, player: Player, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing" or not self.game_active:
            return "skipbo-error-game-not-active"
        if self.is_sequence_gameplay_locked():
            return "skipbo-error-round-transition"
        if self.current_player != player:
            return "action-not-your-turn"
        input_owner = self._gameplay_input_lock_owner()
        if input_owner and self._pending_actions.get(player.id) != action_id:
            return "skipbo-error-card-move-selection-you"
        return None

    def _is_card_action_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | tuple[str, dict] | None:
        guard = self._turn_action_guard(player, action_id)
        if guard:
            return guard
        if not isinstance(player, SkipBoPlayer) or not action_id:
            return "skipbo-error-card-changed"
        source = self._source_for_action(player, action_id)
        if source is None:
            return "skipbo-error-card-changed"
        if source.source_kind == "hand" or self._building_choices_for_source(
            player, source
        ):
            return None
        return "skipbo-error-play-changed"

    def _is_end_turn_empty_enabled(self, player: Player) -> str | None:
        guard = self._turn_action_guard(player, "end_turn_empty")
        if guard:
            return guard[0] if isinstance(guard, tuple) else guard
        if (
            isinstance(player, SkipBoPlayer)
            and not player.hand
            and not self._draw_available()
        ):
            return None
        return "skipbo-error-cards-available"

    def _is_turn_action_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        return (
            Visibility.VISIBLE
            if self.status == "playing" and self.current_player == player
            else Visibility.HIDDEN
        )

    def _is_card_action_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if (
            self.status != "playing"
            or self.is_sequence_gameplay_locked()
            or not isinstance(player, SkipBoPlayer)
            or player.is_spectator
            or not action_id
        ):
            return Visibility.HIDDEN
        source = self._source_for_action(player, action_id)
        if source is None:
            return Visibility.HIDDEN
        if source.source_kind == "hand" or self._building_choices_for_source(
            player, source
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ------------------------------------------------------------------
    # Public and private information
    # ------------------------------------------------------------------

    def _is_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "skipbo-error-game-not-active"

    def _is_private_info_enabled(self, player: Player) -> str | None:
        if not isinstance(player, SkipBoPlayer) or player.is_spectator:
            return "action-not-available"
        return self._is_info_enabled(player)

    def _is_other_discard_info_enabled(self, player: Player) -> str | None:
        error = self._is_info_enabled(player)
        if error:
            return error
        if not self._discard_owner_options(player):
            return "skipbo-error-no-discard-targets"
        return None

    def _is_touch_public_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_touch_private_info_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_touch_public_info_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        if self.options.scoring_mode != SCORING_MATCH:
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        if self.options.scoring_mode != SCORING_MATCH:
            return Visibility.HIDDEN
        return super()._is_check_scores_detailed_hidden(player)

    def get_score_target(self) -> int | None:
        return (
            self.options.winning_score
            if self.options.scoring_mode == SCORING_MATCH
            else None
        )

    def _action_read_building_piles(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            self.live_status_box(
                player,
                "skipbo_building_piles",
                lambda _player, live_user: self._building_status_lines(
                    live_user.locale
                ),
            )

    def _building_status_lines(self, locale: str) -> list[MenuItem]:
        lines: list[MenuItem] = []
        for index, pile in enumerate(self.building_piles):
            if not pile:
                lines.append(
                    MenuItem(
                        id=f"skipbo_building_{index}",
                        text=Localization.get(
                            locale, "skipbo-building-empty", pile=index + 1
                        ),
                    )
                )
            else:
                value = self.building_values[index]
                lines.append(
                    MenuItem(
                        id=f"skipbo_building_{index}",
                        text=Localization.get(
                            locale,
                            "skipbo-building-top",
                            pile=index + 1,
                            value=value,
                            needed=value + 1,
                        ),
                    )
                )
        lines.append(
            MenuItem(
                id="skipbo_draw_pool",
                text=Localization.get(
                    locale,
                    "skipbo-draw-count",
                    draw_count=len(self.deck),
                    recycle_count=len(self.completed_cards),
                ),
            )
        )
        return lines

    def _action_read_stock_piles(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            self.live_status_box(
                player,
                "skipbo_stock_piles",
                lambda _player, live_user: self._stock_status_lines(live_user.locale),
            )

    def _stock_status_lines(self, locale: str) -> list[MenuItem]:
        lines: list[MenuItem] = []
        for owner in self.get_active_players():
            if not isinstance(owner, SkipBoPlayer) or not owner.stock_pile:
                lines.append(
                    MenuItem(
                        id=f"skipbo_stock_{owner.id}",
                        text=Localization.get(
                            locale, "skipbo-stock-empty", player=owner.name
                        ),
                    )
                )
                continue
            lines.append(
                MenuItem(
                    id=f"skipbo_stock_{owner.id}",
                    text=Localization.get(
                        locale,
                        "skipbo-stock-status",
                        player=owner.name,
                        card=cards.format_card(owner.stock_pile[-1], locale),
                        count=len(owner.stock_pile),
                    ),
                )
            )
        return lines

    def _discard_owner_options(self, player: Player) -> list[str]:
        return [
            owner.id
            for owner in self.get_active_players()
            if isinstance(owner, SkipBoPlayer)
            and (player.is_spectator or owner.id != player.id)
        ]

    def _discard_owner_option_label(self, player: Player, owner_id: str) -> str:
        owner = self.get_player_by_id(owner_id)
        if isinstance(owner, SkipBoPlayer):
            return owner.name
        return self._localize(player, "skipbo-discard-owner-unavailable")

    def _action_read_own_discard_piles(self, player: Player, action_id: str) -> None:
        if isinstance(player, SkipBoPlayer) and not player.is_spectator:
            self._open_discard_piles(player, player)

    def _action_read_discard_piles(
        self, player: Player, input_value: str, action_id: str
    ) -> None:
        owner = self.get_player_by_id(input_value)
        if not isinstance(
            owner, SkipBoPlayer
        ) or input_value not in self._discard_owner_options(player):
            user = self.get_user(player)
            if user:
                user.speak_l("skipbo-error-discard-target-changed", buffer="game")
            return
        self._open_discard_piles(player, owner)

    def _open_discard_piles(self, viewer: Player, owner: SkipBoPlayer) -> None:
        if not self.get_user(viewer):
            return
        self.live_status_box(
            viewer,
            f"skipbo_discard_piles_{owner.id}",
            lambda live_viewer, live_user, owner_id=owner.id: (
                self._discard_status_lines_for_viewer(
                    live_viewer, owner_id, live_user.locale
                )
            ),
        )

    def _discard_status_lines_for_viewer(
        self, viewer: Player, owner_id: str, locale: str
    ) -> list[MenuItem]:
        owner = self.get_player_by_id(owner_id)
        active_ids = {player.id for player in self.get_active_players()}
        if not isinstance(owner, SkipBoPlayer) or owner_id not in active_ids:
            return [
                MenuItem(
                    id="skipbo_discard_owner_unavailable",
                    text=Localization.get(locale, "skipbo-discard-owner-unavailable"),
                )
            ]
        return self._discard_status_lines(
            owner,
            locale,
            own=viewer.id == owner.id,
        )

    def _discard_status_lines(
        self, owner: SkipBoPlayer, locale: str, *, own: bool = False
    ) -> list[MenuItem]:
        header_key = (
            "skipbo-discard-your-header" if own else "skipbo-discard-player-header"
        )
        lines = [
            MenuItem(
                id=f"skipbo_discard_header_{owner.id}",
                text=Localization.get(locale, header_key, player=owner.name),
            )
        ]
        for index, pile in enumerate(owner.discard_piles):
            if not pile:
                lines.append(
                    MenuItem(
                        id=f"skipbo_discard_{owner.id}_{index}",
                        text=Localization.get(
                            locale, "skipbo-discard-empty", pile=index + 1
                        ),
                    )
                )
            else:
                lines.append(
                    MenuItem(
                        id=f"skipbo_discard_{owner.id}_{index}",
                        text=Localization.get(
                            locale,
                            "skipbo-discard-top",
                            pile=index + 1,
                            card=cards.format_card(pile[-1], locale),
                            count=len(pile),
                        ),
                    )
                )
        return lines

    def _format_hand(self, player: SkipBoPlayer, locale: str) -> str:
        return Localization.format_list_and(
            locale,
            [
                cards.format_card(card, locale)
                for card in sorted(player.hand, key=cards.sort_key)
            ],
        )

    # ------------------------------------------------------------------
    # Announcements, scoring, and results
    # ------------------------------------------------------------------

    def _broadcast_play(self, actor: SkipBoPlayer, choice: PlayChoice) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            locale = user.locale
            key = "skipbo-play-you" if listener.id == actor.id else "skipbo-play-player"
            kwargs = {
                "card": cards.format_card(
                    choice.card, locale, wild_as=choice.needed_value
                ),
                "source": self._source_label(
                    listener,
                    choice.source_kind,
                    choice.owner,
                    choice.source_pile_index,
                    locale,
                ),
                "pile": choice.building_pile_index + 1,
            }
            if listener.id != actor.id:
                kwargs["player"] = actor
            user.speak_l(
                key,
                buffer="game",
                **self._resolve_broadcast_kwargs(locale, kwargs),
            )

    def _announce_stock_top(self, owner: SkipBoPlayer) -> None:
        if not owner.stock_pile:
            return
        top = owner.stock_pile[-1]
        self.broadcast_personal_l(
            owner,
            "skipbo-next-stock-you",
            "skipbo-next-stock-player",
            buffer="game",
            card=lambda locale: cards.format_card(top, locale),
            count=len(owner.stock_pile),
        )

    def _team_has_empty_stock(self, team: Team) -> bool:
        members = set(team.members)
        team_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, SkipBoPlayer) and player.name in members
        ]
        return bool(team_players) and all(
            not player.stock_pile for player in team_players
        )

    def _finish_round(self, winner: Team) -> None:
        remaining = sum(
            len(player.stock_pile)
            for player in self.get_active_players()
            if isinstance(player, SkipBoPlayer) and player.name not in winner.members
        )
        points = WIN_BONUS_POINTS + (remaining * REMAINING_STOCK_CARD_POINTS)
        winner.total_score += points
        for player in self.get_active_players():
            if isinstance(player, SkipBoPlayer):
                team = self._team_manager.get_team(player.name)
                player.score = team.total_score if team else 0

        if self.options.scoring_mode == SCORING_SINGLE:
            self.winner_team_index = winner.index
            self._finish_single_game(winner)
            return

        self._announce_scored_game_winner(
            winner,
            points=points,
            remaining=remaining,
        )
        if winner.total_score >= self.options.winning_score:
            self.winner_team_index = winner.index
            self._finish_match(winner)
            return

        self.broadcast_l("skipbo-next-round", buffer="game")
        self.start_sequence(
            NEXT_ROUND_SEQUENCE_ID,
            [
                SequenceBeat.pause(NEXT_ROUND_DELAY_TICKS),
                SequenceBeat(ops=[SequenceOperation.callback_op("start_next_round")]),
            ],
            tag=NEXT_ROUND_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.refresh_menus()

    def _announce_scored_game_winner(
        self, winner: Team, *, points: int, remaining: int
    ) -> None:
        winner_members = set(winner.members)
        individual = self.options.team_mode == "individual"
        winner_player = (
            self.get_player_by_name(winner.members[0]) if winner.members else None
        )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            on_winner_team = listener.name in winner_members
            if individual:
                if on_winner_team:
                    key = "skipbo-scored-game-win-you"
                    kwargs = {}
                else:
                    key = "skipbo-scored-game-win-player"
                    kwargs = {"player": winner_player or winner.members[0]}
            elif on_winner_team:
                key = "skipbo-scored-game-win-team-you"
                kwargs = {}
            else:
                key = "skipbo-scored-game-win-team"
                kwargs = {"team": winner.index + 1}
            user.speak_l(
                key,
                buffer="game",
                game=self.round,
                points=points,
                remaining=remaining,
                total=winner.total_score,
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )

    def _announce_winner(self, winner: Team, *, match: bool) -> None:
        self.play_sound(SOUND_GAME_WIN)
        winner_members = set(winner.members)
        individual = self.options.team_mode == "individual"
        winner_player = (
            self.get_player_by_name(winner.members[0]) if winner.members else None
        )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            on_winner_team = listener.name in winner_members
            if individual:
                if on_winner_team:
                    key = "skipbo-match-win-you" if match else "skipbo-single-win-you"
                    kwargs = {}
                else:
                    key = (
                        "skipbo-match-win-player"
                        if match
                        else "skipbo-single-win-player"
                    )
                    kwargs = {"player": winner_player or winner.members[0]}
            elif on_winner_team:
                key = (
                    "skipbo-match-win-team-you"
                    if match
                    else "skipbo-single-win-team-you"
                )
                kwargs = {}
            else:
                key = "skipbo-match-win-team" if match else "skipbo-single-win-team"
                kwargs = {"team": winner.index + 1}
            if match:
                kwargs["score"] = winner.total_score
            user.speak_l(
                key,
                buffer="game",
                **self._resolve_broadcast_kwargs(user.locale, kwargs),
            )

    def _finish_single_game(self, winner: Team) -> None:
        self._announce_winner(winner, match=False)
        self.finish_game()

    def _finish_match(self, winner: Team) -> None:
        self._announce_winner(winner, match=True)
        self.finish_game()

    def bot_think(self, player: SkipBoPlayer) -> str | None:
        return bot_choose_action(self, player)

    def build_game_result(self) -> GameResult:
        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )
        winner = next(
            (team for team in sorted_teams if team.index == self.winner_team_index),
            sorted_teams[0] if sorted_teams else None,
        )
        active_players = self.get_active_players()
        name_to_id = {player.name: player.id for player in active_players}
        team_rankings = [
            {
                "index": team.index,
                "members": list(team.members),
                "score": team.total_score,
                "is_individual": self.options.team_mode == "individual",
            }
            for team in sorted_teams
        ]
        winner_ids = [
            name_to_id[name]
            for name in (winner.members if winner else [])
            if name in name_to_id
        ]
        rating_competitors = rating_competitors_from_scores(
            (
                [name_to_id[name] for name in team.members if name in name_to_id],
                team.total_score,
            )
            for team in sorted_teams
        )
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(player) for player in active_players
            ],
            custom_data={
                "winner_name": (
                    self._team_manager.get_team_name(winner) if winner else None
                ),
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "team_rankings": team_rankings,
                RATING_COMPETITORS_KEY: rating_competitors,
                "rounds_played": self.round,
                "target_score": self.get_score_target(),
                "team_mode": self.options.team_mode,
                "stock_mode": self.options.stock_mode,
                "scoring_mode": self.options.scoring_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        for rank, team in enumerate(result.custom_data.get("team_rankings", []), 1):
            members = team.get("members", [])
            if team.get("is_individual") and members:
                name = members[0]
            else:
                name = Localization.get(
                    locale, "game-team-name", index=team.get("index", 0) + 1
                )
            points = Localization.get(locale, "game-points", count=team.get("score", 0))
            lines.append(
                Localization.get(
                    locale,
                    "skipbo-result-line",
                    rank=rank,
                    player=name,
                    points=points,
                )
            )
        return lines
