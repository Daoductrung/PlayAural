"""Classic 75-ball Bingo.

Standard American Bingo: each player gets an independently-shuffled 5x5
card (columns B-I-N-G-O, free center space), the game calls one number
at a time from the full 1-75 pool at a configurable interval, and
players mark their card as numbers are called. The first player to
claim a valid pattern wins.

Unlike turn-based games, Bingo has no concept of "whose turn it is" --
every active player can mark their card and claim Bingo at any time
during play. This mirrors the structure used by Color Game, where
``set_turn_players`` registers the active roster once at start but the
turn action set is available to every player simultaneously, gated by
game phase rather than a current player.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_MISC
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.grid_mixin import GridGameMixin, GridCursor
from ...game_utils.options import MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


# --------------------------------------------------------------------- #
# Constants                                                              #
# --------------------------------------------------------------------- #

TICKS_PER_SECOND = 20

CARD_ROWS = 5
CARD_COLS = 5
FREE_ROW = 2
FREE_COL = 2
FREE_VALUE = 0  # sentinel: never a real ball number (1-75)

COLUMN_LETTERS = ("B", "I", "N", "G", "O")
COLUMN_RANGES = ((1, 15), (16, 30), (31, 45), (46, 60), (61, 75))
TOTAL_BALLS = 75

PATTERN_LINE = "line"
PATTERN_FOUR_CORNERS = "four_corners"
PATTERN_LETTER_X = "letter_x"
PATTERN_BLACKOUT = "blackout"
PATTERN_CHOICES = [
    PATTERN_LINE,
    PATTERN_FOUR_CORNERS,
    PATTERN_LETTER_X,
    PATTERN_BLACKOUT,
]
PATTERN_LABELS = {
    PATTERN_LINE: "bingo-pattern-line",
    PATTERN_FOUR_CORNERS: "bingo-pattern-four-corners",
    PATTERN_LETTER_X: "bingo-pattern-letter-x",
    PATTERN_BLACKOUT: "bingo-pattern-blackout",
}

DEFAULT_CALL_INTERVAL_SECONDS = "15"
CALL_INTERVAL_CHOICES = ["5", "15", "30", "45", "60"]
CALL_INTERVAL_LABELS = {
    "5": "bingo-call-interval-5",
    "15": "bingo-call-interval-15",
    "30": "bingo-call-interval-30",
    "45": "bingo-call-interval-45",
    "60": "bingo-call-interval-60",
}
CALL_WARMUP_TICKS = 3 * TICKS_PER_SECOND  # pause before the first ball is drawn

# A called number is announced in two beats, like a real caller pulling a
# ball from the cage: the "spin" sound (call.ogg, 2.46s) plays first, and
# the number is only added to called_numbers and read aloud once that
# sound has actually finished, plus a small buffer so the two never
# overlap. Nothing can be marked or claimed against it before that.
CALL_SPIN_DELAY_SECONDS = 2.7
CALL_SPIN_DELAY_TICKS = int(CALL_SPIN_DELAY_SECONDS * TICKS_PER_SECOND)
# When a player claims Bingo, the game holds the result behind a drum-roll
# suspense beat before revealing whether the claim is valid, instead of
# resolving it instantly. suspense.ogg is now JUST the roll (2.51s of
# actual content, no trailing silence) -- the cymbal crash that used to
# be baked into the end of that file is now its own separate sound,
# cymbal.ogg, with an essentially instant attack (already loud within
# ~50ms of its own start). That split means the reveal no longer has to
# guess where a mid-file hit lands or compensate for TTS startup
# latency against it: the game just waits out the roll's own measured
# duration, then plays cymbal.ogg and speaks the result in the same
# instant -- the same "fire together, zero delay" trick the Dead Man's
# Deck gunshot/empty-chamber reveal uses, which works precisely because
# cymbal.ogg's hit is at its own sample 0, not somewhere mid-clip.
CLAIM_SUSPENSE_SECONDS = 2.5
CLAIM_SUSPENSE_TICKS = int(CLAIM_SUSPENSE_SECONDS * TICKS_PER_SECOND)

STATUS_RECENT_CALLS_SHOWN = 10

# Bots react only to the specific number that was just called, like a
# real remote player glancing at their own board: if it's not on their
# board they do nothing at all, and if it is, they mark it (and claim
# Bingo, if that mark just completed their pattern) after a short,
# randomized "reaction time" rather than instantly. There is no
# continuous polling or standing chance of acting outside of that
# single reaction window per call.
#
# Two separate delays are chained: first the mark itself (a bot
# shouldn't place its chip in the exact same instant the number is
# announced), then -- only once that mark has actually happened -- a
# further delay before claiming, if it just completed the pattern.
BOT_MARK_DELAY_MIN_SECONDS = 1
BOT_MARK_DELAY_MAX_SECONDS = 5
BOT_REACTION_MIN_TICKS = 10
BOT_REACTION_MAX_TICKS = 40

SOUND_CALL = "game_bingo/call.ogg"
SOUND_DAUB = "game_bingo/daub.ogg"
SOUND_UNDAUB = "game_bingo/undaub.ogg"
SOUND_ERROR = "game_bingo/error.ogg"
SOUND_WIN = "game_bingo/win.ogg"
SOUND_SUSPENSE = "game_bingo/suspense.ogg"
SOUND_CYMBAL = "game_bingo/cymbal.ogg"
SOUND_MUSIC = "game_bingo/music.ogg"


# --------------------------------------------------------------------- #
# Player / options                                                       #
# --------------------------------------------------------------------- #


@dataclass
class BingoPlayer(Player):
    """Per-player Bingo state: one card, marks, and win flag."""

    card: list[list[int]] = field(default_factory=list)
    marked: list[list[bool]] = field(default_factory=list)
    has_bingo: bool = False

    # A bot's chip placement is itself delayed (see BOT_MARK_DELAY_*)
    # rather than happening the instant a number is announced.
    pending_mark_number: int | None = None
    pending_mark_ticks: int = 0


@dataclass
class BingoOptions(GameOptions):
    """Host-configurable Bingo settings."""

    pattern: str = option_field(
        MenuOption(
            default=PATTERN_LINE,
            choices=PATTERN_CHOICES,
            value_key="pattern",
            label="bingo-set-pattern",
            prompt="bingo-select-pattern",
            change_msg="bingo-option-changed-pattern",
            description="bingo-desc-pattern",
            choice_labels=PATTERN_LABELS,
        )
    )
    call_interval: str = option_field(
        MenuOption(
            choices=CALL_INTERVAL_CHOICES,
            default=DEFAULT_CALL_INTERVAL_SECONDS,
            value_key="seconds",
            label="bingo-set-call-interval",
            prompt="bingo-select-call-interval",
            change_msg="bingo-option-changed-interval",
            description="bingo-desc-call-interval",
            choice_labels=CALL_INTERVAL_LABELS,
        )
    )


# --------------------------------------------------------------------- #
# Game                                                                   #
# --------------------------------------------------------------------- #


@register_game
@dataclass
class BingoGame(GridGameMixin, Game):
    """Classic 75-ball Bingo with configurable winning patterns."""

    relevant_preferences = ["brief_announcements"]

    players: list[BingoPlayer] = field(default_factory=list)
    options: BingoOptions = field(default_factory=BingoOptions)

    # Grid mixin fields: every player navigates their OWN board with
    # the shared up/down/left/right + enter keybinds. Left/right move
    # between the B-I-N-G-O columns; up/down move within a column's 5
    # numbers. Every cell always announces its full "letter+number"
    # identity directly (e.g. "B2") -- there is no separate step where
    # you're "on a letter" without a number attached.
    grid_rows: int = CARD_ROWS
    grid_cols: int = CARD_COLS
    grid_cursors: dict[str, GridCursor] = field(default_factory=dict)
    grid_row_labels: list[str] = field(default_factory=list)
    grid_col_labels: list[str] = field(default_factory=list)

    available_numbers: list[int] = field(default_factory=list)
    called_numbers: list[int] = field(default_factory=list)
    call_countdown_ticks: int = 0
    winner_ids: list[str] = field(default_factory=list)

    # Two-phase call: a number is drawn and its "spin" sound starts
    # playing, but it isn't announced (added to called_numbers) until
    # pending_call_ticks reaches zero.
    pending_call_number: int | None = None
    pending_call_ticks: int = 0

    # A claim is held behind a suspense beat before being resolved.
    pending_claim_player_id: str | None = None
    pending_claim_valid: bool = False
    pending_claim_bad_number: int | None = None
    pending_claim_winning_numbers: list[int] | None = None
    pending_claim_ticks: int = 0

    # A claim resolved as incorrect delays the buzzer a beat after the
    # spoken "Incorrect card" line, rather than playing right on top of
    # it.
    pending_error_sound_ticks: int | None = None

    # Same idea for a correct claim: the cymbal crash still lands right
    # on the announcement (unchanged), but the victory sound itself is
    # delayed a beat after that instant instead of playing on top of it
    # too. This has to be processed even after the round ends (see
    # on_tick), since finish_game() runs in the same call that
    # schedules it.
    pending_win_sound_ticks: int | None = None

    # ------------------------------------------------------------------ #
    # Metadata                                                            #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_name(cls) -> str:
        return "Bingo"

    @classmethod
    def get_type(cls) -> str:
        return "bingo"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_MISC

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 12

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> BingoPlayer:
        return BingoPlayer(id=player_id, name=name, is_bot=is_bot)

    def _locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    # ------------------------------------------------------------------ #
    # Card generation / lookups                                          #
    # ------------------------------------------------------------------ #

    def _generate_card(self) -> tuple[list[list[int]], list[list[bool]]]:
        """Build one independent 5x5 card: 5 unique numbers per column."""
        columns = [
            random.sample(range(low, high + 1), CARD_ROWS)
            for low, high in COLUMN_RANGES
        ]
        card = [
            [columns[col][row] for col in range(CARD_COLS)]
            for row in range(CARD_ROWS)
        ]
        card[FREE_ROW][FREE_COL] = FREE_VALUE
        marked = [[False] * CARD_COLS for _ in range(CARD_ROWS)]
        marked[FREE_ROW][FREE_COL] = True
        return card, marked

    def _column_for_number(self, number: int) -> int:
        for index, (low, high) in enumerate(COLUMN_RANGES):
            if low <= number <= high:
                return index
        return 0  # unreachable for valid balls, kept defensive

    # ------------------------------------------------------------------ #
    # Grid mixin overrides (the player's board)                          #
    # ------------------------------------------------------------------ #

    def get_cell_label(
        self, row: int, col: int, player: Player, locale: str
    ) -> str:
        if not isinstance(player, BingoPlayer) or not player.card:
            return ""
        letter = COLUMN_LETTERS[col]
        if row == FREE_ROW and col == FREE_COL:
            return Localization.get(locale, "bingo-cell-free")
        value = player.card[row][col]
        key = "bingo-cell-marked" if player.marked[row][col] else "bingo-cell-unmarked"
        return Localization.get(locale, key, letter=letter, number=value)

    def is_grid_cell_enabled(
        self, player: Player, row: int, col: int
    ) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if isinstance(player, BingoPlayer) and player.has_bingo:
            return "bingo-you-already-won"
        if row == FREE_ROW and col == FREE_COL:
            return "bingo-cell-is-free"
        return None

    def is_grid_cell_hidden(
        self, player: Player, row: int, col: int
    ) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def on_grid_select(self, player: Player, row: int, col: int) -> None:
        if not isinstance(player, BingoPlayer):
            return
        if self.is_grid_cell_enabled(player, row, col) is not None:
            return

        # Marking is never blocked by whether the number was actually
        # called -- a player can mark whatever they like. That only
        # gets checked when they claim Bingo (see _verify_claim): if a
        # mark that's part of an otherwise-complete pattern turns out
        # to be for a number that was never called, the claim itself
        # is rejected and says so specifically.
        value = player.card[row][col]
        player.marked[row][col] = not player.marked[row][col]
        user = self.get_user(player)
        if user:
            self.play_sound(SOUND_DAUB if player.marked[row][col] else SOUND_UNDAUB)
            key = "bingo-you-mark" if player.marked[row][col] else "bingo-you-unmark"
            user.speak_l(
                key, buffer="game", letter=COLUMN_LETTERS[col], number=value
            )
        self.refresh_menus(player)

    # ------------------------------------------------------------------ #
    # Keybinds                                                            #
    # ------------------------------------------------------------------ #

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.setup_grid_keybinds()
        self.define_keybind(
            "b",
            Localization.get("en", "bingo-claim-bingo"),
            ["claim_bingo"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "r",
            Localization.get("en", "bingo-repeat-call"),
            ["repeat_call"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "bingo-check-called"),
            ["check_called"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ------------------------------------------------------------------ #
    # Actions and menus                                                   #
    # ------------------------------------------------------------------ #

    def create_turn_action_set(self, player: BingoPlayer) -> ActionSet:
        """Every active player gets the same action set at all times --
        Bingo has no per-player turn order, only a shared game phase."""
        action_set = ActionSet(name="turn")

        for action in self.build_grid_actions(player):
            action_set.add(action)
        for action in self.build_grid_nav_actions():
            action_set.add(action)

        action_set.add(
            Action(
                id="claim_bingo",
                label=Localization.get(self._locale(player), "bingo-claim-bingo"),
                handler="_action_claim_bingo",
                is_enabled="_is_claim_enabled",
                is_hidden="_is_claim_hidden",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._locale(player)

        action_set.add(
            Action(
                id="repeat_call",
                label=Localization.get(locale, "bingo-repeat-call"),
                handler="_action_repeat_call",
                is_enabled="_is_repeat_call_enabled",
                is_hidden="_is_repeat_call_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_called",
                label=Localization.get(locale, "bingo-check-called"),
                handler="_action_check_called",
                is_enabled="_is_check_called_enabled",
                is_hidden="_is_check_called_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "claim_bingo",
                    "repeat_call",
                    "check_called",
                    "check_scores",
                    "whos_at_table",
                ],
            )
        return action_set

    def _is_claim_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if isinstance(player, BingoPlayer) and player.has_bingo:
            return "bingo-you-already-won"
        if self.pending_claim_player_id is not None:
            return "bingo-claim-in-progress"
        return None

    def _is_claim_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_repeat_call_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not self.called_numbers:
            return "bingo-no-calls-yet"
        return None

    def _is_repeat_call_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN if self.status != "playing" else Visibility.VISIBLE

    def _is_check_called_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_check_called_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN if self.status != "playing" else Visibility.VISIBLE

    # ------------------------------------------------------------------ #
    # Action handlers                                                     #
    # ------------------------------------------------------------------ #

    def _action_claim_bingo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BingoPlayer):
            return
        if self._is_claim_enabled(player) is not None:
            return

        self.pending_claim_player_id = player.id
        (
            self.pending_claim_valid,
            self.pending_claim_bad_number,
            self.pending_claim_winning_numbers,
        ) = self._verify_claim(player)
        self.pending_claim_ticks = CLAIM_SUSPENSE_TICKS
        self.play_sound(SOUND_SUSPENSE)
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l("bingo-checking-claim", buffer="game", player=player.name)
        self.refresh_menus()

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        """Bingo has no turn order, so the shared "T" keybind (normally
        "whose turn is it") is repurposed the same way Color Game does
        for its own simultaneous-play design: instead of a meaningless
        answer, it reports whatever's actually happening in the round
        right now."""
        _ = action_id
        user = self.get_user(player)
        if not user:
            return
        if self.pending_claim_player_id is not None:
            claimer = next(
                (p for p in self.get_active_players() if p.id == self.pending_claim_player_id),
                None,
            )
            user.speak_l(
                "bingo-whose-turn-checking",
                buffer="game",
                player=claimer.name if claimer else "",
            )
        elif self.pending_call_number is not None:
            user.speak_l("bingo-whose-turn-drawing", buffer="game")
        else:
            seconds_left = -(-self.call_countdown_ticks // TICKS_PER_SECOND)  # ceil
            user.speak_l(
                "bingo-whose-turn-waiting", buffer="game", seconds=seconds_left
            )

    def _action_repeat_call(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not self.called_numbers:
            return
        last = self.called_numbers[-1]
        col = self._column_for_number(last)
        user.speak_l(
            "bingo-last-call",
            buffer="game",
            letter=COLUMN_LETTERS[col],
            number=last,
        )

    def _action_check_called(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player, "bingo_called", self._called_numbers_items, focus_id="called_count"
        )

    def _called_numbers_items(self, player: Player, user) -> list[MenuItem]:
        locale = user.locale
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "bingo-status-called-count",
                    count=len(self.called_numbers),
                    total=TOTAL_BALLS,
                ),
                id="called_count",
            )
        ]
        recent = self.called_numbers[-STATUS_RECENT_CALLS_SHOWN:]
        for number in reversed(recent):
            col = self._column_for_number(number)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "bingo-status-called-entry",
                        letter=COLUMN_LETTERS[col],
                        number=number,
                    ),
                    id=f"call:{number}",
                )
            )
        return items

    # ------------------------------------------------------------------ #
    # Pattern checking                                                    #
    # ------------------------------------------------------------------ #

    def _is_free_cell(self, row: int, col: int) -> bool:
        return row == FREE_ROW and col == FREE_COL

    def _pattern_candidate_cells(self, pattern: str) -> list[list[tuple[int, int]]]:
        """Every distinct shape of cells that would satisfy the given
        pattern. "Any line" has 12 (5 rows + 5 columns + 2 diagonals);
        every other pattern has exactly one fixed shape."""
        if pattern == PATTERN_BLACKOUT:
            return [
                [(r, c) for r in range(CARD_ROWS) for c in range(CARD_COLS)]
            ]
        if pattern == PATTERN_FOUR_CORNERS:
            return [
                [
                    (0, 0),
                    (0, CARD_COLS - 1),
                    (CARD_ROWS - 1, 0),
                    (CARD_ROWS - 1, CARD_COLS - 1),
                ]
            ]
        if pattern == PATTERN_LETTER_X:
            cells = {(i, i) for i in range(CARD_ROWS)} | {
                (i, CARD_COLS - 1 - i) for i in range(CARD_ROWS)
            }
            return [sorted(cells)]

        # PATTERN_LINE (default): any single row, column, or diagonal.
        candidates = [[(r, c) for c in range(CARD_COLS)] for r in range(CARD_ROWS)]
        candidates += [[(r, c) for r in range(CARD_ROWS)] for c in range(CARD_COLS)]
        candidates.append([(i, i) for i in range(CARD_ROWS)])
        candidates.append([(i, CARD_COLS - 1 - i) for i in range(CARD_ROWS)])
        return candidates

    def _check_pattern(self, player: BingoPlayer) -> bool:
        """True if some candidate shape is fully marked, regardless of
        whether every mark is for a number that was actually called.
        Bots can only ever mark numbers that were genuinely called (see
        _announce_pending_call), so this is always equivalent to a
        legitimate win for them. Human claims go through _verify_claim
        instead, which also checks legitimacy and can name the specific
        offending number."""
        for cells in self._pattern_candidate_cells(self.options.pattern):
            if all(
                self._is_free_cell(r, c) or player.marked[r][c] for r, c in cells
            ):
                return True
        return False

    def _verify_claim(
        self, player: BingoPlayer
    ) -> tuple[bool, int | None, list[int] | None]:
        """Like _check_pattern, but also requires every marked cell in
        the completed shape to be a number that was actually called --
        marking is never blocked at the board (see on_grid_select), so
        a player is free to mark ahead of the caller, but that only
        pays off if the real calls catch up before they claim. Returns
        (True, None, winning_numbers) on a genuine win, where
        winning_numbers is every called number in the completed shape
        (free space excluded), in the shape's own left-to-right,
        top-to-bottom order. Otherwise returns (False, X, None) where X
        is the first illegitimately-marked number found on an
        otherwise-complete shape, or (False, None, None) if no shape is
        even fully marked yet."""
        first_bad_number: int | None = None
        for cells in self._pattern_candidate_cells(self.options.pattern):
            if not all(
                self._is_free_cell(r, c) or player.marked[r][c] for r, c in cells
            ):
                continue
            uncalled = [
                (r, c)
                for r, c in cells
                if not self._is_free_cell(r, c)
                and player.card[r][c] not in self.called_numbers
            ]
            if not uncalled:
                winning_numbers = [
                    player.card[r][c] for r, c in cells if not self._is_free_cell(r, c)
                ]
                return True, None, winning_numbers
            if first_bad_number is None:
                bad_row, bad_col = uncalled[0]
                first_bad_number = player.card[bad_row][bad_col]
        return False, first_bad_number, None

    # ------------------------------------------------------------------ #
    # Game flow                                                           #
    # ------------------------------------------------------------------ #

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if self.options.call_interval not in CALL_INTERVAL_CHOICES:
            errors.append(
                ("bingo-error-invalid-interval", {"value": self.options.call_interval})
            )
        if self.options.pattern not in PATTERN_CHOICES:
            errors.append(("bingo-error-invalid-pattern", {"value": self.options.pattern}))
        return errors

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.called_numbers = []
        self.available_numbers = list(range(1, TOTAL_BALLS + 1))
        random.shuffle(self.available_numbers)
        self.winner_ids = []
        self.call_countdown_ticks = CALL_WARMUP_TICKS

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, BingoPlayer)
        ]
        self.set_turn_players(active_players)
        self._init_grid()
        self.grid_col_labels = list(COLUMN_LETTERS)
        self.grid_row_labels = [str(i + 1) for i in range(CARD_ROWS)]

        for player in active_players:
            player.card, player.marked = self._generate_card()
            player.has_bingo = False
            self.grid_cursors[player.id] = GridCursor(row=0, col=0)

        # Background music loops quietly under the whole calling phase.
        # Keep it a low, non-intrusive bed if you ever swap this track:
        # number calls via TTS/screen reader need to stay clearly audible
        # over it.
        self.play_music(SOUND_MUSIC)
        pattern_label = Localization.get(
            "en", PATTERN_LABELS.get(self.options.pattern, PATTERN_LABELS[PATTERN_LINE])
        )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                "bingo-game-start",
                buffer="game",
                pattern=Localization.get(
                    user.locale,
                    PATTERN_LABELS.get(self.options.pattern, PATTERN_LABELS[PATTERN_LINE]),
                ),
                interval=self.options.call_interval,
            )
        self.refresh_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

        # This has to run even once the round has finished (status is
        # no longer "playing"): _declare_winner schedules it and then
        # immediately calls finish_game(), so gating this on "playing"
        # like everything below would mean the win sound could never
        # actually fire.
        if self.pending_win_sound_ticks is not None:
            if self.pending_win_sound_ticks > 0:
                self.pending_win_sound_ticks -= 1
            else:
                self.play_sound(SOUND_WIN)
                self.pending_win_sound_ticks = None

        if self.status != "playing":
            return

        if self.pending_error_sound_ticks is not None:
            if self.pending_error_sound_ticks > 0:
                self.pending_error_sound_ticks -= 1
            else:
                self.play_sound(SOUND_ERROR)
                self.pending_error_sound_ticks = None

        # A pending claim takes priority over everything else: the whole
        # table pauses on the drum roll until it resolves.
        if self.pending_claim_player_id is not None:
            if self.pending_claim_ticks > 0:
                self.pending_claim_ticks -= 1
            else:
                self._resolve_pending_claim()
        elif self.pending_call_number is not None:
            if self.pending_call_ticks > 0:
                self.pending_call_ticks -= 1
            else:
                self._announce_pending_call()
        elif self.call_countdown_ticks > 0:
            self.call_countdown_ticks -= 1
        else:
            self._start_next_call()

        if self.game_active and self.status == "playing":
            self._process_bots()

    def _process_bots(self) -> None:
        """Bots never poll themselves speculatively -- they only ever
        react the instant a number they needed gets called (see
        _announce_pending_call). This counts down and executes whatever
        is scheduled for them: first the mark itself (delayed a beat,
        see BOT_MARK_DELAY_*), and only once that's actually happened,
        a claim -- if marking just completed their pattern."""
        for player in self.get_active_players():
            if not isinstance(player, BingoPlayer) or not player.is_bot:
                continue

            if player.pending_mark_number is not None:
                if player.pending_mark_ticks > 0:
                    player.pending_mark_ticks -= 1
                else:
                    self._execute_bot_mark(player)
                continue  # mark first; claiming (if any) is next tick at the earliest

            if not player.bot_pending_action:
                continue
            if player.bot_think_ticks > 0:
                player.bot_think_ticks -= 1
                continue
            action_id = player.bot_pending_action
            player.bot_pending_action = None
            self.execute_action(player, action_id)

    def _execute_bot_mark(self, player: BingoPlayer) -> None:
        number = player.pending_mark_number
        player.pending_mark_number = None
        if number is None or player.has_bingo:
            return

        self._auto_mark(player, number)
        # A human's own manual mark already broadcasts this sound to the
        # whole table (see on_grid_select) -- a silent bot mark would
        # look like the bot wasn't doing anything at all. Match that
        # same broadcast, plus a spoken line naming who marked what,
        # since the sound alone doesn't say which bot or which square.
        self.play_sound(SOUND_DAUB)
        letter = COLUMN_LETTERS[self._column_for_number(number)]
        for listener in self.players:
            listener_user = self.get_user(listener)
            if listener_user:
                listener_user.speak_l(
                    "bingo-bot-marked",
                    buffer="game",
                    player=player.name,
                    letter=letter,
                    number=number,
                )

        if self._check_pattern(player) and not player.bot_pending_action:
            player.bot_pending_action = "claim_bingo"
            player.bot_think_ticks = random.randint(
                BOT_REACTION_MIN_TICKS, BOT_REACTION_MAX_TICKS
            )

    def _start_next_call(self) -> None:
        """Draw the next ball and play its "spin" sound. The number isn't
        announced or added to called_numbers until _announce_pending_call
        runs a beat later -- mirrors a real caller pulling a ball from the
        cage before reading it out."""
        if not self.available_numbers:
            self._finish_no_further_calls()
            return

        self.pending_call_number = self.available_numbers.pop()
        self.pending_call_ticks = CALL_SPIN_DELAY_TICKS
        self.play_sound(SOUND_CALL)

    def _announce_pending_call(self) -> None:
        number = self.pending_call_number
        self.pending_call_number = None
        if number is None:
            return

        self.called_numbers.append(number)
        col = self._column_for_number(number)
        self.call_countdown_ticks = int(self.options.call_interval) * TICKS_PER_SECOND

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                "bingo-number-called",
                buffer="game",
                letter=COLUMN_LETTERS[col],
                number=number,
            )

        for player in self.get_active_players():
            if not isinstance(player, BingoPlayer) or player.has_bingo:
                continue
            had_number = self._card_has_number(player, number)
            if not (player.is_bot and had_number):
                continue
            # A bot reacts to THIS call and nothing else: if the number
            # wasn't on its board, it stays completely quiet, exactly
            # like a real player who just glances at their board and
            # sees nothing to mark. When it does have the number, the
            # mark itself is delayed a beat -- a real player doesn't
            # place their chip in the exact instant the number is
            # announced either -- capped so it always resolves well
            # before the *next* call, no matter how short the table's
            # interval is set to.
            interval_seconds = int(self.options.call_interval)
            max_delay_seconds = max(
                BOT_MARK_DELAY_MIN_SECONDS,
                min(BOT_MARK_DELAY_MAX_SECONDS, interval_seconds - 1),
            )
            player.pending_mark_number = number
            player.pending_mark_ticks = random.randint(
                BOT_MARK_DELAY_MIN_SECONDS * TICKS_PER_SECOND,
                max_delay_seconds * TICKS_PER_SECOND,
            )

        self.refresh_menus()

    def _card_has_number(self, player: BingoPlayer, number: int) -> bool:
        return any(number in row for row in player.card)

    def _auto_mark(self, player: BingoPlayer, number: int) -> None:
        for row in range(CARD_ROWS):
            for col in range(CARD_COLS):
                if player.card[row][col] == number:
                    player.marked[row][col] = True
                    return

    def _resolve_pending_claim(self) -> None:
        player_id = self.pending_claim_player_id
        is_valid = self.pending_claim_valid
        bad_number = self.pending_claim_bad_number
        winning_numbers = self.pending_claim_winning_numbers
        self.pending_claim_player_id = None
        self.pending_claim_bad_number = None
        self.pending_claim_winning_numbers = None

        player = next(
            (p for p in self.get_active_players() if p.id == player_id), None
        )
        if not isinstance(player, BingoPlayer):
            return

        # Cymbal and the result reveal fire in the same instant -- same
        # trick as the Dead Man's Deck gunshot/empty-chamber reveal,
        # made possible here by cymbal.ogg's own near-instant attack.
        self.play_sound(SOUND_CYMBAL)

        if is_valid:
            self._declare_winner(player, winning_numbers or [])
        else:
            for listener in self.players:
                listener_user = self.get_user(listener)
                if listener_user:
                    listener_user.speak_l("bingo-claim-incorrect", buffer="game")
            # The buzzer lands a beat after the announcement instead of
            # right on top of it.
            self.pending_error_sound_ticks = TICKS_PER_SECOND
            if bad_number is not None:
                # They had a complete shape marked, but one of those
                # marks was ahead of the actual calls -- tell them
                # specifically which one, privately (nobody else needs
                # to hear the details of their card).
                user = self.get_user(player)
                if user:
                    col = self._column_for_number(bad_number)
                    user.speak_l(
                        "bingo-marked-number-not-called",
                        buffer="game",
                        letter=COLUMN_LETTERS[col],
                        number=bad_number,
                    )
            self.refresh_menus()

    def _declare_winner(self, player: BingoPlayer, winning_numbers: list[int]) -> None:
        player.has_bingo = True
        self.winner_ids.append(player.id)
        # The cymbal (played by the caller, right before this) still
        # lands exactly on the spoken reveal below -- that part is
        # unchanged. The victory sound itself is delayed a beat after
        # that instant instead of playing on top of everything else at
        # once.
        self.pending_win_sound_ticks = TICKS_PER_SECOND
        # Reading out the specific numbers makes sense for a line, the
        # corners, or the X -- it tells everyone exactly what happened.
        # For Blackout it would just be a wall of speech, and it's also
        # redundant: Blackout already means "the whole card," so naming
        # every number adds no information.
        if winning_numbers and self.options.pattern != PATTERN_BLACKOUT:
            numbers_text = ", ".join(
                f"{COLUMN_LETTERS[self._column_for_number(n)]} {n}"
                for n in winning_numbers
            )
            message_key = "bingo-claim-correct"
        else:
            numbers_text = ""
            message_key = "bingo-claim-correct-no-numbers"
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l(
                    message_key,
                    buffer="game",
                    player=player.name,
                    numbers=numbers_text,
                )
        self.finish_game()

    def _finish_no_further_calls(self) -> None:
        """Safety net: all 75 balls drawn with nobody claiming. Award the
        pattern to anyone who already qualifies (this always happens for
        Blackout, since every card's numbers are exhausted by ball 75)."""
        if self.status != "playing":
            return
        for player in self.get_active_players():
            if (
                isinstance(player, BingoPlayer)
                and not player.has_bingo
                and self._check_pattern(player)
            ):
                player.has_bingo = True
                self.winner_ids.append(player.id)
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l("bingo-deck-exhausted", buffer="game")
        self.finish_game()

    # ------------------------------------------------------------------ #
    # Results                                                             #
    # ------------------------------------------------------------------ #

    def build_game_result(self) -> GameResult:
        active_players = self.get_active_players()
        winner_names = [
            player.name for player in active_players if player.id in self.winner_ids
        ]
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
                for player in active_players
            ],
            custom_data={
                "winner_ids": self.winner_ids,
                "winner_names": winner_names,
                "pattern": self.options.pattern,
                "calls_made": len(self.called_numbers),
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [
            Localization.get(
                locale, "bingo-end-calls", count=result.custom_data.get("calls_made", 0)
            )
        ]
        winners = result.custom_data.get("winner_names") or []
        if winners:
            for name in winners:
                lines.append(Localization.get(locale, "bingo-end-winner-line", player=name))
        else:
            lines.append(Localization.get(locale, "bingo-end-no-winner"))
        return lines
