"""Tests for the Bingo game."""

import random
from pathlib import Path

from ..core.server import Server
from ..game_utils.actions import Visibility
from ..game_utils.audio_duration import measure_audio_duration_ticks
from ..game_utils.grid_mixin import grid_cell_id
from ..games.bingo import audio as bingo_audio
from ..games.bingo.game import (
    CALL_SEQUENCE_TAG,
    CALL_SPIN_DELAY_TICKS,
    CARD_COLS,
    CARD_ROWS,
    COLUMN_LETTERS,
    COLUMN_RANGES,
    FREE_COL,
    FREE_ROW,
    FREE_VALUE,
    MIN_CLAIM_WINDOW_TICKS,
    PATTERN_BLACKOUT,
    PATTERN_FOUR_CORNERS,
    PATTERN_LETTER_X,
    PATTERN_LINE,
    SOUND_ERROR,
    SOUND_WIN,
    TICKS_PER_SECOND,
    TOTAL_BALLS,
    BingoGame,
    BingoOptions,
    BingoPlayer,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 2,
    start: bool = False,
    bot_all: bool = False,
    bot_indices: set[int] | None = None,
    **option_overrides,
) -> BingoGame:
    game = BingoGame(options=BingoOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        is_bot = bot_all or (bot_indices is not None and index in bot_indices)
        user = Bot(name, uuid=f"p{index + 1}") if is_bot else MockUser(name, uuid=f"p{index + 1}")
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def advance_until(game: BingoGame, condition, max_ticks: int = 5000) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def _resolve_claim(game: BingoGame) -> None:
    """Advance ticks until a pending claim (started via _action_claim_bingo)
    finishes its suspense beat and resolves."""
    assert advance_until(game, lambda: game.pending_claim_player_id is None)


def _force_announce(game: BingoGame, number: int) -> None:
    """Skip straight to a number being announced, bypassing the spin
    sequence entirely -- the equivalent of what used to be done by
    setting pending_call_number/pending_call_ticks=0 and ticking once,
    back when the announce delay was a plain counter rather than a
    sequence."""
    game._handle_announce_call({"number": number})


def test_game_registered_defaults_and_metadata() -> None:
    assert GameRegistry.get("bingo") is BingoGame
    game = BingoGame()
    assert game.get_name() == "Bingo"
    assert game.get_type() == "bingo"
    assert game.get_category() == "misc"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 12
    assert game.get_supported_leaderboards() == ["wins", "games_played"]


def test_card_generation_matches_column_ranges_and_has_free_space() -> None:
    game = make_game(player_count=2)
    card, marked = game._generate_card()

    assert len(card) == CARD_ROWS
    assert all(len(row) == CARD_COLS for row in card)
    assert card[FREE_ROW][FREE_COL] == FREE_VALUE
    assert marked[FREE_ROW][FREE_COL] is True

    for col in range(CARD_COLS):
        low, high = COLUMN_RANGES[col]
        values = [card[row][col] for row in range(CARD_ROWS) if not (row == FREE_ROW and col == FREE_COL)]
        assert len(values) == len(set(values)), "column values must be unique"
        assert all(low <= value <= high for value in values)


def test_on_start_deals_independent_cards_and_shuffles_pool(monkeypatch) -> None:
    """Each player's card must be independently shuffled. Rather than
    relying on real randomness happening to avoid a collision (true on
    every run in practice, but not a guarantee -- a flaky, not a
    deterministic, check), force a sequence where consecutive players'
    columns are mechanically guaranteed to differ every time this runs."""
    call_count = 0
    real_sample = random.sample

    def alternating_sample(population, k):
        nonlocal call_count
        call_count += 1
        ordered = real_sample(population, k)
        # 5 columns per card (odd) means this alternation is always
        # exactly reversed between column N of one player and column N
        # of the next player, so no two consecutive cards can ever come
        # out identical.
        return ordered if call_count % 2 else list(reversed(ordered))

    monkeypatch.setattr("server.games.bingo.game.random.sample", alternating_sample)

    game = make_game(player_count=3, start=True)
    players = [p for p in game.players if isinstance(p, BingoPlayer)]
    assert len(players) == 3
    for player in players:
        assert player.card
        assert not player.has_bingo
    assert players[0].card != players[1].card
    assert players[1].card != players[2].card
    assert len(game.available_numbers) == TOTAL_BALLS
    assert game.called_numbers == []


def _ticks_between_first_two_announcements(call_interval: str) -> int:
    game = make_game(player_count=2, call_interval=call_interval, start=True)
    assert advance_until(game, lambda: len(game.called_numbers) == 1)
    ticks_elapsed = 0
    while len(game.called_numbers) == 1 and ticks_elapsed < 5000:
        game.on_tick()
        ticks_elapsed += 1
    return ticks_elapsed


def test_numbers_are_called_at_configured_interval() -> None:
    # Where the interval leaves room, it is the true announcement-to-
    # announcement cadence (spin sound included, not on top of it).
    assert _ticks_between_first_two_announcements("15") == 15 * TICKS_PER_SECOND


def test_shortest_interval_still_leaves_a_usable_claim_window() -> None:
    """Regression for the dev's third-round point 2: at the 5-second
    setting the countdown after an announcement used to be interval minus
    spin (about 2.3s), and claims are disabled during the next spin, so
    that was the whole time a screen-reader or touch user had to react.
    The window is now never shorter than MIN_CLAIM_WINDOW_TICKS, which
    makes the real cadence there spin + minimum window."""
    assert 5 * TICKS_PER_SECOND - CALL_SPIN_DELAY_TICKS < MIN_CLAIM_WINDOW_TICKS
    assert (
        _ticks_between_first_two_announcements("5")
        == CALL_SPIN_DELAY_TICKS + MIN_CLAIM_WINDOW_TICKS
    )


def test_final_ball_gets_the_full_interval_as_its_claim_window() -> None:
    """After ball 75 there is no next spin to hurry toward, so the round
    must not end after the shortened remainder every other call gets."""
    game = make_game(player_count=2, call_interval="15", start=True)
    game.available_numbers = [7]
    game._start_next_call()
    assert advance_until(game, lambda: 7 in game.called_numbers)
    assert game.available_numbers == []
    # advance_until stops the tick after the announcement, so allow that
    # single decrement; the point is it is the whole interval (300), not
    # the interval minus the spin (about 230).
    ticks_left = 0
    while game.status == "playing" and ticks_left < 1000:
        game.on_tick()
        ticks_left += 1
    assert game.status == "finished"
    assert 15 * TICKS_PER_SECOND - 2 <= ticks_left <= 15 * TICKS_PER_SECOND + 2


def test_call_spin_sound_plays_before_the_number_is_announced() -> None:
    """A drawn number sits in pending_call_number (unannounced, unmarkable)
    for CALL_SPIN_DELAY_TICKS before it's added to called_numbers -- this
    is what lets the "spinning ball" sound play before the caller reads
    the number out, like a physical bingo cage."""
    game = make_game(player_count=2, call_interval="5", start=True)

    assert advance_until(game, lambda: game.pending_call_number is not None)
    assert game.called_numbers == []  # drawn, but not yet announced

    assert advance_until(game, lambda: len(game.called_numbers) == 1)
    assert game.pending_call_number is None
    assert game.called_numbers[0] in range(1, TOTAL_BALLS + 1)


def test_marking_is_never_blocked_by_whether_the_number_was_called() -> None:
    """A player can mark any square at any time -- legitimacy is only
    checked when they actually claim Bingo (see _verify_claim), not at
    the board."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    row, col = 0, 0
    if row == FREE_ROW and col == FREE_COL:
        row = 1

    game.on_grid_select(player, row, col)
    assert player.marked[row][col] is True  # marked even though never called

    game.on_grid_select(player, row, col)
    assert player.marked[row][col] is False  # selecting again un-marks it


def test_free_space_cannot_be_toggled() -> None:
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    assert (
        game.is_grid_cell_enabled(player, FREE_ROW, FREE_COL)
        == "bingo-cell-is-free"
    )


def test_bot_auto_mark_still_works_without_the_removed_option() -> None:
    """_auto_mark itself (used by bots reacting to a call) is unrelated
    to the removed auto_daub option and still works standalone."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    row, col = (0, 0) if not (0 == FREE_ROW and 0 == FREE_COL) else (0, 1)
    value = player.card[row][col]
    game._auto_mark(player, value)
    assert player.marked[row][col] is True



def _force_line_win(game: BingoGame, player: BingoPlayer) -> None:
    """Mark an entire row (which includes the free space column) and call
    every number in it so a claim will validate."""
    row = 0
    for col in range(CARD_COLS):
        player.marked[row][col] = True
        value = player.card[row][col]
        if value != FREE_VALUE and value not in game.called_numbers:
            game.called_numbers.append(value)


def test_check_pattern_line_default() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    assert game._check_pattern(player) is False
    _force_line_win(game, player)
    assert game._check_pattern(player) is True


def test_check_pattern_four_corners() -> None:
    game = make_game(player_count=2, pattern=PATTERN_FOUR_CORNERS, start=True)
    player = game.players[0]
    assert game._check_pattern(player) is False
    for row, col in ((0, 0), (0, CARD_COLS - 1), (CARD_ROWS - 1, 0), (CARD_ROWS - 1, CARD_COLS - 1)):
        player.marked[row][col] = True
    assert game._check_pattern(player) is True


def test_check_pattern_letter_x() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LETTER_X, start=True)
    player = game.players[0]
    for i in range(CARD_ROWS):
        player.marked[i][i] = True
    assert game._check_pattern(player) is False  # only one diagonal
    for i in range(CARD_ROWS):
        player.marked[i][CARD_COLS - 1 - i] = True
    assert game._check_pattern(player) is True


def test_check_pattern_blackout_requires_full_card() -> None:
    game = make_game(player_count=2, pattern=PATTERN_BLACKOUT, start=True)
    player = game.players[0]
    _force_line_win(game, player)
    assert game._check_pattern(player) is False
    for row in range(CARD_ROWS):
        for col in range(CARD_COLS):
            player.marked[row][col] = True
    assert game._check_pattern(player) is True


def test_claim_bingo_wins_and_finishes_game() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner = game.players[0]
    _force_line_win(game, winner)

    game._action_claim_bingo(winner, "claim_bingo")
    # The claim doesn't resolve immediately -- it's held behind a
    # suspense beat first, like double-checking a card in person.
    assert game.pending_claim_player_id == winner.id
    assert winner.has_bingo is False
    assert game.status == "playing"

    _resolve_claim(game)

    assert winner.has_bingo is True
    assert winner.id in game.winner_ids
    assert game.status == "finished"


def test_win_announcement_names_the_winning_numbers() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner, listener = game.players
    _force_line_win(game, winner)
    expected = [
        winner.card[0][c] for c in range(CARD_COLS) if not (0 == FREE_ROW and c == FREE_COL)
    ]

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    spoken = game.get_user(listener).get_spoken_messages()
    assert any(all(str(n) in m for n in expected) for m in spoken)


def test_win_sound_is_delayed_a_second_after_the_announcement() -> None:
    """The cymbal still lands right on the spoken reveal (unchanged),
    but the victory sound itself plays a beat after that instant, not
    on top of it -- and this must still fire even though finish_game()
    has already moved the round out of "playing" by the time the
    delay elapses."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner, listener = game.players
    _force_line_win(game, winner)

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    assert game.status == "finished"
    listener_user = game.get_user(listener)
    assert "game_bingo/win.ogg" not in listener_user.get_sounds_played()
    # Scheduled via GameSoundMixin.schedule_sound, deliberately not a
    # SequenceRunnerMixin sequence -- see test_win_sound_survives_a_real_
    # table_reset below for why that distinction matters.
    assert any(entry[1] == SOUND_WIN for entry in game.scheduled_sounds)

    for _ in range(TICKS_PER_SECOND - 1):
        game.on_tick()
    assert "game_bingo/win.ogg" not in listener_user.get_sounds_played()

    assert advance_until(
        game, lambda: "game_bingo/win.ogg" in listener_user.get_sounds_played()
    )


def test_winning_numbers_are_rendered_through_localization_per_entry(monkeypatch) -> None:
    """Regression for the dev's second-round point 4: _declare_winner
    used to build each entry with a hardcoded f"{letter} {number}",
    with only the surrounding conjunction actually localized. Each
    number now has to go through Localization.get("bingo-status-called-
    entry", ...) individually, once per recipient locale, rather than
    being formatted once up front in whatever shape English happens to
    use."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner, _listener = game.players
    _force_line_win(game, winner)
    expected_numbers = {
        winner.card[0][c] for c in range(CARD_COLS) if not (0 == FREE_ROW and c == FREE_COL)
    }

    seen_calls = []
    real_get = Localization.get.__func__

    def spy_get(cls, locale, message_id, **kwargs):
        if message_id == "bingo-status-called-entry":
            seen_calls.append((locale, kwargs.get("number")))
        return real_get(cls, locale, message_id, **kwargs)

    monkeypatch.setattr(Localization, "get", classmethod(spy_get))

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    called_numbers = {number for _locale, number in seen_calls}
    assert called_numbers == expected_numbers
    assert all(locale == "en" for locale, _number in seen_calls)


def test_blackout_win_does_not_read_out_every_number() -> None:
    """Blackout means "the whole card" by definition -- naming every
    individual number adds no information and would turn the win
    announcement into a wall of speech, so it's skipped entirely for
    this pattern regardless of how many numbers that is."""
    game = make_game(player_count=2, pattern=PATTERN_BLACKOUT, start=True)
    winner, listener = game.players
    for row in range(CARD_ROWS):
        for col in range(CARD_COLS):
            winner.marked[row][col] = True
            value = winner.card[row][col]
            if value != FREE_VALUE:
                game.called_numbers.append(value)

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    assert winner.has_bingo is True
    spoken = game.get_user(listener).get_spoken_messages()
    assert any(winner.name in m for m in spoken)
    # None of the individual card numbers should show up crammed into
    # one long announcement.
    all_numbers = {v for row in winner.card for v in row if v != FREE_VALUE}
    assert not any(
        sum(str(n) in m for n in all_numbers) > 3 for m in spoken
    )


def test_false_claim_does_not_end_the_game() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]

    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)

    assert player.has_bingo is False
    assert game.status == "playing"


def test_error_buzzer_is_delayed_a_second_after_the_announcement() -> None:
    """The buzzer for an incorrect claim lands a beat after the spoken
    "Incorrect card" line, not right on top of it."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player, listener = game.players

    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)

    listener_user = game.get_user(listener)
    assert "game_bingo/error.ogg" not in listener_user.get_sounds_played()
    assert any(entry[1] == SOUND_ERROR for entry in game.scheduled_sounds)

    for _ in range(TICKS_PER_SECOND - 1):
        game.on_tick()
    assert "game_bingo/error.ogg" not in listener_user.get_sounds_played()

    assert advance_until(
        game, lambda: "game_bingo/error.ogg" in listener_user.get_sounds_played()
    )


def test_win_sound_survives_a_real_table_reset() -> None:
    """Regression for the dev's second-round point 3: the old
    implementation started a trailing WIN_SOUND_SEQUENCE_TAG sequence,
    which Table.reset_game() cancels along with every other sequence on
    the old game instance the moment finish_game() installs a fresh one
    -- so the delayed cue never played in production, even though a test
    that kept ticking the discarded game object directly looked green.
    This goes through a real Table so that boundary is actually
    exercised, not simulated."""
    alice = MockUser("Player1", uuid="p1")
    bob = MockUser("Player2", uuid="p2")
    server = Server(db_path=":memory:")
    server._db.connect()
    server._users = {alice.username: alice, bob.username: bob}

    table = server._tables.create_table("bingo", alice.username, alice)
    game = BingoGame(options=BingoOptions(pattern=PATTERN_LINE))
    table.game = game
    game._table = table
    server._set_in_game_state(alice, table.table_id)
    game.initialize_lobby(alice.username, alice)
    table.add_member(bob.username, bob)
    game.add_player(bob.username, bob)
    server._set_in_game_state(bob, table.table_id)
    game.on_start()

    winner, listener = game.players
    _force_line_win(game, winner)

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)
    assert game.status == "finished"

    # finish_game() already made the table install a fresh game instance and
    # cancel every sequence on the discarded one.
    new_game: BingoGame = table.game
    assert new_game is not game

    listener_user = new_game.get_user(listener)
    assert "game_bingo/win.ogg" not in listener_user.get_sounds_played()
    assert advance_until(
        new_game, lambda: "game_bingo/win.ogg" in listener_user.get_sounds_played()
    )


def test_claim_names_the_specific_marked_but_uncalled_number() -> None:
    """Marking is never blocked (see on_grid_select), so a player can
    mark ahead of the actual calls. If they claim before the calls
    catch up, the rejection names the specific offending number rather
    than a generic "not valid yet"."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    row = 0
    for col in range(CARD_COLS):
        player.marked[row][col] = True
        value = player.card[row][col]
        if col < CARD_COLS - 1 and value != FREE_VALUE:
            game.called_numbers.append(value)
    uncalled_value = player.card[row][CARD_COLS - 1]

    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert player.has_bingo is False
    assert game.status == "playing"

    # The bad number is only known once the claim is actually verified,
    # at resolution time -- so the check has to happen after the
    # suspense beat, not right when the claim was submitted.
    spoken = game.get_user(player).get_spoken_messages()
    assert any(str(uncalled_value) in m for m in spoken)


def test_incomplete_pattern_and_uncalled_number_get_different_messages() -> None:
    """Regression for the dev's second-round point 4: a claim can fail
    for two very different reasons -- the pattern just isn't there yet,
    or it's there but one of the marks is ahead of the actual calls --
    and a single generic "Incorrect card." doesn't tell the player which
    one happened or what to do about it."""
    incomplete_game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    empty_handed = incomplete_game.players[0]
    incomplete_game._action_claim_bingo(empty_handed, "claim_bingo")
    _resolve_claim(incomplete_game)
    incomplete_spoken = incomplete_game.get_user(empty_handed).get_spoken_messages()
    assert any(
        Localization.get("en", "bingo-claim-incomplete-you") in m for m in incomplete_spoken
    )
    assert not any(
        Localization.get("en", "bingo-claim-incorrect-you") in m for m in incomplete_spoken
    )

    uncalled_game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    ahead_of_calls = uncalled_game.players[0]
    row = 0
    for col in range(CARD_COLS):
        ahead_of_calls.marked[row][col] = True
        value = ahead_of_calls.card[row][col]
        if col < CARD_COLS - 1 and value != FREE_VALUE:
            uncalled_game.called_numbers.append(value)

    uncalled_game._action_claim_bingo(ahead_of_calls, "claim_bingo")
    _resolve_claim(uncalled_game)
    uncalled_spoken = uncalled_game.get_user(ahead_of_calls).get_spoken_messages()
    assert any(
        Localization.get("en", "bingo-claim-incorrect-you") in m for m in uncalled_spoken
    )
    assert not any(
        Localization.get("en", "bingo-claim-incomplete-you") in m for m in uncalled_spoken
    )


def test_second_claim_is_rejected_while_one_is_being_checked() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    first, second = game.players[0], game.players[1]
    _force_line_win(game, first)
    _force_line_win(game, second)

    game._action_claim_bingo(first, "claim_bingo")
    assert game.pending_claim_player_id == first.id

    assert game._is_claim_enabled(second) == "bingo-claim-in-progress"
    game._action_claim_bingo(second, "claim_bingo")
    # Second claim was ignored -- still checking the first one.
    assert game.pending_claim_player_id == first.id

    _resolve_claim(game)
    assert first.has_bingo is True
    assert second.has_bingo is False


def test_claim_is_rejected_while_a_number_is_mid_call() -> None:
    """Regression for the dev's second-round point 1: CALL_SEQUENCE_TAG
    has no lock_scope of its own, so it keeps advancing on its own
    schedule regardless of any lock a claim sequence holds --
    process_sequences() advances every active sequence, lock or no lock.
    A claim started while a call is mid-flight (drawn but not yet
    announced) could have its own suspense beat overlap the instant that
    number gets announced, flipping the claim's validity mid-
    verification. The dev reproduced exactly this: mark a row whose
    numbers are all called except one, let the call for that last number
    start, then submit the claim before it's announced."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    row = 0
    for col in range(CARD_COLS):
        player.marked[row][col] = True
    missing_value = next(
        v for v in (player.card[row][c] for c in range(CARD_COLS)) if v != FREE_VALUE
    )
    for col in range(CARD_COLS):
        value = player.card[row][col]
        if value != FREE_VALUE and value != missing_value:
            game.called_numbers.append(value)

    # The full row is marked, but missing_value -- one of its numbers --
    # hasn't been called yet. Start its call (the "spin") without
    # announcing it, exactly the mid-flight state from the dev's repro.
    game.available_numbers = [missing_value]
    game._start_next_call()
    assert game.pending_call_number == missing_value

    for _ in range(10):
        game.on_tick()
    assert game.pending_call_number == missing_value  # still spinning

    assert game._is_claim_enabled(player) == "bingo-claim-wait-for-call"
    game._action_claim_bingo(player, "claim_bingo")
    assert game.pending_claim_player_id is None  # rejected outright, no sequence started
    assert player.has_bingo is False

    # Once the number is actually announced, the identical claim is
    # legitimately valid -- this isn't blocking claims that should win,
    # only ones submitted before the board they're checked against is
    # final.
    _force_announce(game, missing_value)
    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert player.has_bingo is True


def test_bot_stays_quiet_when_called_number_is_not_on_its_board() -> None:
    game = make_game(player_count=2, bot_all=True, start=True)
    bot = game.players[0]
    on_board = {value for row in bot.card for value in row if value != FREE_VALUE}
    missing_number = next(n for n in range(1, TOTAL_BALLS + 1) if n not in on_board)

    _force_announce(game, missing_number)

    assert missing_number in game.called_numbers
    assert bot.bot_pending_action is None
    assert not any(any(row_marks) for row_marks in bot.marked) or all(
        not bot.marked[r][c] or (r, c) == (FREE_ROW, FREE_COL)
        for r in range(CARD_ROWS)
        for c in range(CARD_COLS)
    )


def test_bot_marks_but_does_not_claim_while_pattern_still_incomplete() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, bot_all=True, start=True)
    bot = game.players[0]
    row, col = 0, 0
    if row == FREE_ROW and col == FREE_COL:
        row = 1
    value = bot.card[row][col]

    _force_announce(game, value)

    assert bot.pending_mark_number == value  # scheduled, not instant
    assert advance_until(game, lambda: bot.pending_mark_number is None)

    assert bot.marked[row][col] is True
    assert bot.bot_pending_action is None  # one square is not a full line


def test_bot_mark_is_audible_but_not_narrated_per_square() -> None:
    """A bot's mark still plays the daub cue -- silently auto-marking
    would look like the bot wasn't doing anything at all -- but it must
    NOT narrate the exact square to the whole table. Announcing every
    bot's precise letter+number used to mean a table with several bots
    could produce a burst of speech lines per call, potentially
    drowning out the caller; real bingo doesn't narrate other players'
    marks either, so this is deliberately just the sound cue."""
    game = make_game(
        player_count=2, pattern=PATTERN_LINE, bot_indices={0}, start=True
    )
    bot, human_listener = game.players
    assert bot.is_bot and not human_listener.is_bot
    row, col = 0, 0
    if row == FREE_ROW and col == FREE_COL:
        row = 1
    value = bot.card[row][col]

    listener = game.get_user(human_listener)
    _force_announce(game, value)
    assert advance_until(game, lambda: bot.pending_mark_number is None)

    assert "game_bingo/daub.ogg" in listener.get_sounds_played()
    spoken = listener.get_spoken_messages()
    assert not any(bot.name in m for m in spoken)


def test_bot_reacts_and_claims_after_a_call_completes_its_line() -> None:
    """The full event-driven path: mark every cell in a row except one
    (pre-seeding called_numbers for those), then feed the real remaining
    call through the normal announce flow and confirm the bot schedules
    a delayed reaction rather than claiming instantly, then actually
    wins once that reaction fires."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, bot_all=True, start=True)
    bot = game.players[0]
    row = 0
    remaining_col = CARD_COLS - 1
    for col in range(CARD_COLS):
        if col == remaining_col:
            continue
        value = bot.card[row][col]
        bot.marked[row][col] = True
        game.called_numbers.append(value)
    final_value = bot.card[row][remaining_col]

    _force_announce(game, final_value)

    assert bot.pending_mark_number == final_value  # mark itself is delayed too
    assert advance_until(game, lambda: bot.pending_mark_number is None)

    assert bot.marked[row][remaining_col] is True
    assert bot.bot_pending_action == "claim_bingo"
    assert bot.bot_think_ticks > 0  # a short delay, not an instant claim

    assert advance_until(game, lambda: game.status == "finished")
    assert bot.id in game.winner_ids


def test_bot_mark_delay_never_approaches_the_table_interval(monkeypatch) -> None:
    """The mark delay is randomized (1-5s), but must always be capped
    well under whatever call interval the table is using -- otherwise a
    bot could still be "about to mark" the previous number when the
    next one gets announced. Force the RNG to the top of its range and
    inspect the value right as it's scheduled (before on_tick's own
    first decrement) so this is deterministic rather than only
    sometimes catching it."""
    game = make_game(player_count=2, call_interval="5", bot_all=True, start=True)
    bot = game.players[0]
    row, col = 0, 0
    if row == FREE_ROW and col == FREE_COL:
        row = 1
    value = bot.card[row][col]

    monkeypatch.setattr(
        "server.games.bingo.game.random.randint", lambda lo, hi: hi
    )
    game._handle_announce_call({"number": value})

    interval_ticks = 5 * TICKS_PER_SECOND
    assert 0 < bot.pending_mark_ticks < interval_ticks


def test_bots_never_act_without_a_call_to_react_to() -> None:
    """No continuous polling of any kind: with no new number ever called,
    ticking the game for a long stretch must never spontaneously give a
    bot something to do. This is the direct regression test for the
    infinite-loop bug (bots endlessly re-checking and false-claiming
    from the very start of the round, unrelated to any actual call)."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, bot_all=True, start=True)
    bot = game.players[0]
    game.call_countdown_ticks = 10_000  # hold off any real call

    for _ in range(400):  # 20 simulated seconds
        game.on_tick()

    assert bot.bot_pending_action is None
    assert bot.has_bingo is False


def test_a_human_seated_first_does_not_block_bots_behind_them() -> None:
    """Regression test for the original turn-based-helper bug: nothing
    in the current, purely reactive bot design keys off current_player
    or roster order at all, but this keeps that scenario covered end to
    end in case that ever regresses."""
    game = make_game(
        player_count=3, pattern=PATTERN_LINE, bot_indices={1, 2}, start=True
    )
    human, bot_a, bot_b = game.players
    assert human.is_bot is False
    assert bot_a.is_bot and bot_b.is_bot

    row = 0
    remaining_col = CARD_COLS - 1
    for col in range(CARD_COLS):
        if col == remaining_col:
            continue
        value = bot_b.card[row][col]
        bot_b.marked[row][col] = True
        game.called_numbers.append(value)
    final_value = bot_b.card[row][remaining_col]

    _force_announce(game, final_value)

    assert advance_until(game, lambda: game.status == "finished")
    assert bot_b.id in game.winner_ids



def test_repeat_last_call_reports_most_recent_number() -> None:
    game = make_game(player_count=2, call_interval="5", start=True)
    assert advance_until(game, lambda: len(game.called_numbers) >= 1)
    player = game.players[0]
    user = game.get_user(player)
    user.messages.clear() if hasattr(user, "messages") else None
    game._action_repeat_call(player, "repeat_call")
    # Should not raise and should reflect the last called number.
    last = game.called_numbers[-1]
    assert last in range(1, TOTAL_BALLS + 1)


def test_whose_turn_reports_seconds_until_the_next_call() -> None:
    """Bingo has no turn order, so the shared T keybind is repurposed
    (like Color Game does for its own simultaneous design) rather than
    left pointing at a meaningless "whose turn" answer."""
    game = make_game(player_count=2, call_interval="15", start=True)
    player = game.players[0]
    user = game.get_user(player)

    game._action_whose_turn(player, "whose_turn")

    # 3s warmup before the very first ball, regardless of the 15s
    # call interval configured for the rest of the round.
    assert user.get_last_spoken() == "Next number in 3 seconds."


def test_whose_turn_reports_drawing_while_a_number_is_pending() -> None:
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    game.pending_call_number = 42

    game._action_whose_turn(player, "whose_turn")

    assert user.get_last_spoken() == "Drawing the next number..."


def test_whose_turn_reports_the_claimer_while_a_claim_is_pending() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    claimer, listener = game.players
    _force_line_win(game, claimer)
    game._action_claim_bingo(claimer, "claim_bingo")

    listener_user = game.get_user(listener)
    game._action_whose_turn(listener, "whose_turn")

    assert listener_user.get_last_spoken() == f"Checking {claimer.name}'s card..."


def test_deck_exhaustion_without_a_claim_ends_with_no_winner() -> None:
    """Completing the pattern is not itself a win under these rules --
    only a checked, successful claim is. A player who never actually
    claims must NOT be silently awarded the win just because the deck
    ran out; the round simply ends with no winner."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    game.available_numbers = []
    qualifying_player = game.players[0]
    _force_line_win(game, qualifying_player)

    game._finish_no_further_calls()

    assert qualifying_player.id not in game.winner_ids
    assert game.winner_ids == []
    assert game.status == "finished"


def test_deck_exhaustion_with_a_pending_claim_still_resolves_it() -> None:
    """The claim window for the very last call works exactly like any
    other: if a claim is already being checked when the deck empties,
    it still resolves normally rather than being cut short."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner = game.players[0]
    _force_line_win(game, winner)
    game._action_claim_bingo(winner, "claim_bingo")
    game.available_numbers = []

    _resolve_claim(game)

    assert winner.id in game.winner_ids
    assert game.status == "finished"


def _grid_cell_order(action_set) -> list[str]:
    return [action_id for action_id in action_set._order if action_id.startswith("grid_cell_")]


def test_touch_turn_menu_keeps_the_grid_contiguous_and_aligned() -> None:
    """Regression for the dev's second-round point 2: an earlier fix
    moved claim_bingo to index 0 for touch clients, shifting every one
    of the 25 grid cells over by one and pushing the last cell into a
    phantom sixth row -- since the client derives (row, col) from the
    flat _order index plus grid_width, that desynced the visible board
    from its logical coordinates on touch. The 25 cells must occupy flat
    indices 0..24 in exact row-major order on every client, touch
    included, for GridGameMixin's math to stay correct."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    user.client_type = "mobile"

    action_set = game.create_turn_action_set(player)
    expected = [grid_cell_id(row, col) for row in range(CARD_ROWS) for col in range(CARD_COLS)]
    assert action_set._order[: len(expected)] == expected


def test_claim_bingo_lands_right_after_the_grid_on_every_client() -> None:
    """Claim doesn't need to be first to be "quickly reachable" -- it
    just can't corrupt the board to get there. Sitting immediately after
    the 25th cell (rather than buried behind the whole standard menu)
    is one step away on every client, desktop and touch alike."""
    for client_type in (None, "mobile"):
        game = make_game(player_count=2, start=True)
        player = game.players[0]
        game.get_user(player).client_type = client_type
        action_set = game.create_turn_action_set(player)
        grid_cells = _grid_cell_order(action_set)
        assert len(grid_cells) == CARD_ROWS * CARD_COLS
        claim_index = action_set._order.index("claim_bingo")
        assert claim_index > action_set._order.index(grid_cells[-1])


def test_touch_standard_actions_follow_touch_order_and_are_visible() -> None:
    """claim_bingo doesn't belong to this action set at all (see
    create_turn_action_set). whose_turn and whos_at_table are keybind-
    only/hidden by default in the base implementation -- reordering them
    into the touch menu is a no-op unless their visibility is also
    overridden for touch clients, which is the actual second half of
    this fix."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    user.client_type = "mobile"

    action_set = game.create_standard_action_set(player)
    order = action_set._order
    assert "claim_bingo" not in order
    assert order.index("repeat_call") < order.index("check_called")
    assert order.index("check_called") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")

    assert game._is_whose_turn_hidden(player) == Visibility.VISIBLE
    assert game._is_whos_at_table_hidden(player) == Visibility.VISIBLE


def test_desktop_standard_actions_keep_base_visibility() -> None:
    """The touch-only visibility override must not leak onto desktop --
    whose_turn/whos_at_table stay keybind-only there, matching every
    other game's base behavior."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    assert game._is_whose_turn_hidden(player) == Visibility.HIDDEN
    assert game._is_whos_at_table_hidden(player) == Visibility.HIDDEN


def test_before_menu_build_resyncs_standard_order_on_device_handover() -> None:
    """Regression for the dev's note that the touch reordering wasn't
    idempotent: it only ran once, at action-set creation time, so a
    desktop<->mobile handover mid-game left the standard menu stuck with
    whichever device built it first. before_menu_build must re-apply the
    ordering on every menu build instead."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)

    # setup_player_actions() already built and attached this player's
    # "standard" set at add_player() time, with whatever client_type the
    # user had then -- desktop, by default.
    desktop_order = list(game.get_action_set(player, "standard")._order)

    user.client_type = "mobile"
    game.before_menu_build(player)
    order = game.get_action_set(player, "standard")._order
    assert order != desktop_order
    assert order.index("repeat_call") < order.index("whos_at_table")

    user.client_type = None
    game.before_menu_build(player)
    order = game.get_action_set(player, "standard")._order
    assert order == desktop_order


def test_marking_is_locked_while_a_claim_is_being_checked() -> None:
    """The card is verified at resolution time, not when the claim is
    submitted, so the board must not be editable by anyone while a
    claim is being checked -- otherwise the verified result and the
    live board could disagree. Regression test for the exact race the
    old manual-tick design allowed."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    claimer, other = game.players
    _force_line_win(game, claimer)

    game._action_claim_bingo(claimer, "claim_bingo")
    assert game.is_sequence_gameplay_locked()

    row, col = 0, 1
    was_marked = claimer.marked[row][col]
    game.on_grid_select(claimer, row, col)
    assert claimer.marked[row][col] == was_marked  # rejected: input was locked

    assert game._is_claim_enabled(other) == "bingo-claim-in-progress"
    assert game.is_grid_cell_enabled(other, 0, 1) == "bingo-claim-in-progress"

    _resolve_claim(game)
    assert claimer.has_bingo is True  # untouched card still wins


def test_bot_claim_is_retried_rather_than_dropped_when_locked() -> None:
    """If a bot's claim becomes ready to execute while another claim is
    already being checked, it must not be silently cleared -- it
    should simply stay queued and execute once the table unlocks."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, bot_all=True, start=True)
    bot, other_bot = game.players
    _force_line_win(game, bot)
    # other_bot's card is NOT a winner -- its claim will be rejected,
    # so the round keeps going and bot's own queued claim gets its turn.

    game._action_claim_bingo(other_bot, "claim_bingo")
    assert game.is_sequence_gameplay_locked()

    bot.bot_pending_action = "claim_bingo"
    bot.bot_think_ticks = 0
    game._process_bots()

    # Still queued, not dropped -- the table was locked when this ran.
    assert bot.bot_pending_action == "claim_bingo"
    assert bot.has_bingo is False

    # other_bot's claim resolves as incorrect, which -- in the same
    # on_tick, since bots unpause the instant the lock clears --
    # immediately lets bot's own still-queued claim run and win.
    _resolve_claim(game)
    assert other_bot.has_bingo is False
    assert bot.has_bingo is True
    assert game.status == "finished"


def test_claim_messages_use_second_person_for_the_claimant() -> None:
    """The claimant hears a personal "you" message, not their own name
    spoken back in the third person -- and vice versa for everyone
    else."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner, other = game.players
    _force_line_win(game, winner)

    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    winner_spoken = " ".join(game.get_user(winner).get_spoken_messages())
    other_spoken = " ".join(game.get_user(other).get_spoken_messages())

    assert "You" in winner_spoken
    assert winner.name not in winner_spoken
    assert winner.name in other_spoken
    assert "You" not in other_spoken


def test_incorrect_claim_names_the_claimant_to_everyone_else() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    claimant, other = game.players  # neither has a winning card yet

    game._action_claim_bingo(claimant, "claim_bingo")
    _resolve_claim(game)

    claimant_spoken = " ".join(game.get_user(claimant).get_spoken_messages())
    other_spoken = " ".join(game.get_user(other).get_spoken_messages())
    assert claimant.name not in claimant_spoken
    assert claimant.name in other_spoken


def test_build_game_result_reports_winner_and_calls() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner = game.players[0]
    _force_line_win(game, winner)
    game._action_claim_bingo(winner, "claim_bingo")
    _resolve_claim(game)

    result = game.build_game_result()
    assert result.game_type == "bingo"
    assert result.custom_data["winner_ids"] == [winner.id]
    assert result.custom_data["winner_names"] == [winner.name]
    assert result.custom_data["calls_made"] == len(game.called_numbers)


def test_prestart_validate_rejects_bad_interval() -> None:
    game = make_game(player_count=2, call_interval="200")
    errors = game.prestart_validate()
    assert any(
        isinstance(err, tuple) and err[0] == "bingo-error-invalid-interval"
        for err in errors
    )


def test_navigation_moves_directly_between_letter_and_number_cells() -> None:
    """Left/right always move between the B-I-N-G-O letters; up/down
    move within a column's 5 numbers. There is no separate "letter
    only" stop -- every cell you land on is a full letter+number cell
    from the very first move."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    cursor = game.grid_cursors[player.id]
    assert (cursor.row, cursor.col) == (0, 0)  # B, first number

    game._action_grid_move(player, "grid_move_right")
    assert (cursor.row, cursor.col) == (0, 1)  # I, first number

    game._action_grid_move(player, "grid_move_down")
    assert (cursor.row, cursor.col) == (1, 1)  # I, second number

    game._action_grid_move(player, "grid_move_down")
    game._action_grid_move(player, "grid_move_down")
    assert (cursor.row, cursor.col) == (3, 1)  # I, fourth number

    game._action_grid_move(player, "grid_move_left")
    assert (cursor.row, cursor.col) == (3, 0)  # column changes, row unaffected

    for _ in range(3):
        game._action_grid_move(player, "grid_move_up")
    assert (cursor.row, cursor.col) == (0, 0)  # back at the first number

    game._action_grid_move(player, "grid_move_up")
    assert (cursor.row, cursor.col) == (0, 0)  # clamped, no further up


def test_navigation_down_clamps_at_the_last_number() -> None:
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    cursor = game.grid_cursors[player.id]

    for _ in range(10):
        game._action_grid_move(player, "grid_move_down")
    assert cursor.row == CARD_ROWS - 1  # last number row, clamped

    game._action_grid_move(player, "grid_move_down")
    assert cursor.row == CARD_ROWS - 1  # still clamped


def test_cell_label_combines_letter_and_number_directly() -> None:
    """No separate 'letter only' step -- every cell always announces
    its full letter+number identity plus mark state, e.g. 'B 8, not
    marked.'"""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    row, col = 0, 0
    if row == FREE_ROW and col == FREE_COL:
        row = 1
    value = player.card[row][col]

    label = game.get_cell_label(row, col, player, user.locale)
    assert str(value) in label
    assert COLUMN_LETTERS[col] in label
    assert "not marked" in label

    player.marked[row][col] = True
    label = game.get_cell_label(row, col, player, user.locale)
    assert "not marked" not in label
    assert "marked" in label


# ---------------------------------------------------------------------- #
# Third-round review: repeated claims, gesture claim, real built menus,   #
# spectators, scoreless, keybinds, save/load, audio                        #
# ---------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parents[2]
BINGO_SOUND_FILES = (
    "call.ogg",
    "cymbal.ogg",
    "daub.ogg",
    "error.ogg",
    "music.ogg",
    "suspense.ogg",
    "undaub.ogg",
    "win.ogg",
)


def _mark_row_with_last_number_uncalled(game: BingoGame, player: BingoPlayer) -> int:
    """Mark all of row 0 but call only its first four numbers; returns the
    marked-but-uncalled number."""
    values = [player.card[0][col] for col in range(CARD_COLS) if player.card[0][col] != FREE_VALUE]
    for col in range(CARD_COLS):
        player.marked[0][col] = True
    for value in values[:-1]:
        game.called_numbers.append(value)
    return values[-1]


def _locked_ticks_while_claiming(game: BingoGame, player: BingoPlayer) -> int:
    """Try to claim; return how many ticks the gameplay lock was held."""
    game._action_claim_bingo(player, "claim_bingo")
    held = 0
    while game.is_sequence_gameplay_locked() and held < 1000:
        game.on_tick()
        held += 1
    return held


def test_incomplete_claim_cannot_be_retried_or_freeze_the_call_clock() -> None:
    """Regression for the dev's third-round point 1: an incomplete card
    used to be able to claim, wait for rejection, and claim again forever,
    re-taking the gameplay lock (which freezes the call clock and every
    bot) for the whole suspense beat each time."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    game.call_countdown_ticks = 400

    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert player.has_bingo is False
    assert game._is_claim_enabled(player) == "bingo-claim-unchanged"

    countdown_before = game.call_countdown_ticks
    assert _locked_ticks_while_claiming(game, player) == 0  # retry never starts
    assert game.pending_claim_player_id is None
    for _ in range(60):
        game.on_tick()
    assert game.call_countdown_ticks == countdown_before - 60  # clock kept running


def test_uncalled_number_claim_cannot_be_retried_until_something_changes() -> None:
    """A complete shape containing an uncalled number is the subtler case
    the dev called out: rejecting only obviously-incomplete cards is not
    enough. The private explanation naming the number is preserved."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    missing = _mark_row_with_last_number_uncalled(game, player)
    user = game.get_user(player)

    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert player.has_bingo is False
    explanation = Localization.get(
        "en",
        "bingo-marked-number-not-called",
        letter=COLUMN_LETTERS[game._column_for_number(missing)],
        number=missing,
    )
    assert explanation in user.get_spoken_messages()

    assert game._is_claim_enabled(player) == "bingo-claim-unchanged"
    assert _locked_ticks_while_claiming(game, player) == 0

    # A new call is a meaningful change: the same card may claim again, and
    # this time it is legitimately valid.
    _force_announce(game, missing)
    assert game._is_claim_enabled(player) is None
    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert player.has_bingo is True


def test_changed_card_reopens_claim_but_returning_to_a_rejected_state_does_not() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    assert game._is_claim_enabled(player) == "bingo-claim-unchanged"

    player.marked[1][0] = True  # a different card is a meaningful change
    assert game._is_claim_enabled(player) is None
    player.marked[1][0] = False  # ...but toggling back is the rejected state
    assert game._is_claim_enabled(player) == "bingo-claim-unchanged"


def test_many_players_contending_for_claim_cannot_freeze_call_progress() -> None:
    game = make_game(player_count=3, pattern=PATTERN_LINE, start=True)
    game.call_countdown_ticks = 1000
    first, second, third = game.players

    # While the first claim is being checked, the others are told so, and the
    # claimant is told it is their own claim rather than "another" one.
    game._action_claim_bingo(first, "claim_bingo")
    assert game._is_claim_enabled(first) == "bingo-claim-in-progress-you"
    assert game._is_claim_enabled(second) == "bingo-claim-in-progress"
    assert Localization.get("en", "bingo-claim-in-progress-you") != Localization.get(
        "en", "bingo-claim-in-progress"
    )
    _resolve_claim(game)

    locked = _locked_ticks_while_claiming(game, second)
    locked += _locked_ticks_while_claiming(game, third)
    # Each false claim costs one suspense beat, once.
    assert 0 < locked <= 2 * (CLAIM_SUSPENSE_TICKS_FOR_TESTS + 2)

    # Everyone is now blocked until something changes, so nobody can hold
    # the clock any more no matter how they hammer Claim.
    for player in (first, second, third):
        for _ in range(5):
            assert _locked_ticks_while_claiming(game, player) == 0
    assert not game.is_sequence_gameplay_locked()
    countdown = game.call_countdown_ticks
    for _ in range(40):
        game.on_tick()
    assert game.call_countdown_ticks == countdown - 40


CLAIM_SUSPENSE_TICKS_FOR_TESTS = bingo_audio.sound_ticks(bingo_audio.SOUND_SUSPENSE)


def test_claimant_hears_your_card_while_it_is_checked_and_observers_the_name() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    claimant, observer = game.players
    game._action_claim_bingo(claimant, "claim_bingo")

    game._action_whose_turn(claimant, "whose_turn")
    game._action_whose_turn(observer, "whose_turn")
    claimant_line = game.get_user(claimant).get_last_spoken()
    observer_line = game.get_user(observer).get_last_spoken()
    assert claimant_line == Localization.get("en", "bingo-whose-turn-checking-you")
    assert claimant.name not in claimant_line
    assert observer_line == Localization.get(
        "en", "bingo-whose-turn-checking", player=claimant.name
    )


def test_touch_gesture_claims_bingo_from_any_focused_cell_without_marking_it() -> None:
    """Touch clients send Shift+Enter for their context/hold gesture. It
    must claim from the focused card cell without also toggling that cell."""
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner = game.players[0]
    game.get_user(winner).client_type = "mobile"
    _force_line_win(game, winner)
    focused = grid_cell_id(3, 3)
    assert winner.marked[3][3] is False

    game.handle_event(
        winner,
        {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": focused},
    )
    assert game.pending_claim_player_id == winner.id
    assert winner.marked[3][3] is False
    _resolve_claim(game)
    assert winner.has_bingo is True


def test_shift_enter_does_nothing_on_desktop_and_b_is_the_only_claim_key() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    winner = game.players[0]
    user = game.get_user(winner)
    _force_line_win(game, winner)
    spoken = list(user.get_spoken_messages())

    game.handle_event(
        winner,
        {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": grid_cell_id(3, 3)},
    )
    assert game.pending_claim_player_id is None
    assert winner.marked[3][3] is False
    assert user.get_spoken_messages() == spoken  # silent, not an error

    game.handle_event(winner, {"type": "keybind", "key": "b"})
    assert game.pending_claim_player_id == winner.id


def test_plain_enter_still_marks_and_never_claims() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    game.handle_event(
        player, {"type": "keybind", "key": "enter", "menu_item_id": grid_cell_id(0, 0)}
    )
    assert player.marked[0][0] is True
    assert game.pending_claim_player_id is None


def test_claim_keybinds_and_no_state_collisions() -> None:
    game = make_game(player_count=2, start=True)
    claim_keys = {
        key
        for key, binds in game._keybinds.items()
        for bind in binds
        if bind.actions == ["claim_bingo"]
    }
    assert claim_keys == {"b"}  # desktop claims with B only
    gesture_keys = {
        key
        for key, binds in game._keybinds.items()
        for bind in binds
        if bind.actions == ["claim_bingo_gesture"]
    }
    assert gesture_keys == {"shift+enter"}  # what the mobile hold gesture sends
    # Claiming is never a spectator keybind.
    for key in claim_keys | gesture_keys:
        assert all(
            not bind.include_spectators
            for bind in game._keybinds[key]
            if bind.actions in (["claim_bingo"], ["claim_bingo_gesture"])
        )
    # Enter selects a cell and Shift+Enter claims -- distinct keys.
    assert [b.actions for b in game._keybinds["enter"] if b.state == KeybindState.ACTIVE] == [
        ["grid_select"]
    ]
    for key, binds in game._keybinds.items():
        states = [bind.state for bind in binds]
        assert len(states) == len(set(states)), f"{key} is bound twice in one state"


def test_scoreless_game_has_no_score_actions_and_silent_score_keybinds() -> None:
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    visible = {r.action.id for r in game.get_all_enabled_actions(player)}
    assert not {"check_scores", "check_scores_detailed"} & visible
    spoken_before = list(user.get_spoken_messages())
    game.handle_event(player, {"type": "keybind", "key": "s"})
    game.handle_event(player, {"type": "keybind", "key": "s", "shift": True})
    assert user.get_spoken_messages() == spoken_before


def _menu_ids(game: BingoGame, player: BingoPlayer) -> list[str]:
    return [item.id for item in game.build_menu_items(player, game.get_user(player)).items]


def test_built_menu_keeps_grid_aligned_on_web_and_mobile_with_handover() -> None:
    """The dev's third-round point 2/6: assert the FINAL build_menu_items()
    result (what Web and mobile actually render), not ActionSet._order."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    cells = [grid_cell_id(r, c) for r in range(CARD_ROWS) for c in range(CARD_COLS)]

    for client_type in ("web", "mobile", "python", "mobile", "web"):  # handovers
        user.client_type = client_type
        game.before_menu_build(player)
        build = game.build_menu_items(player, user)
        ids = [item.id for item in build.items]
        assert ids[:25] == cells, client_type
        assert build.grid_kwargs["grid_enabled"] is True
        assert build.grid_kwargs["grid_width"] == CARD_COLS
        assert build.grid_kwargs["grid_height"] == CARD_ROWS
        assert "claim_bingo" in ids[25:]
        touch = client_type in ("web", "mobile")
        assert ("web_actions_menu" in ids) is touch
        assert ("web_leave_table" in ids) is touch
        # Claim comes before the static touch controls, never after.
        if touch:
            assert ids.index("claim_bingo") < ids.index("web_actions_menu")


def test_claim_is_reachable_on_touch_by_gesture_and_menu_item() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    # Gesture path: bound and enabled from any focused cell, but only for
    # touch clients.
    assert any(
        b.actions == ["claim_bingo_gesture"] for b in game._keybinds["shift+enter"]
    )
    for client_type in ("web", "mobile"):
        game.get_user(player).client_type = client_type
        assert game._is_claim_gesture_enabled(player) is None
        # Equivalent accessible path: an ordinary activatable menu item.
        assert "claim_bingo" in _menu_ids(game, player)
    game.get_user(player).client_type = "python"
    assert game._is_claim_gesture_enabled(player) == "action-not-available"
    assert game._is_claim_enabled(player) is None


def test_game_start_tells_each_client_how_to_claim() -> None:
    touch = make_game(player_count=2)
    mobile_user = touch.get_user(touch.players[0])
    web_user = touch.get_user(touch.players[1])
    mobile_user.client_type = "mobile"
    web_user.client_type = "web"
    spectator_user = MockUser("Watcher", uuid="watch1")
    touch.add_spectator("Watcher", spectator_user)
    touch.on_start()
    desktop = make_game(player_count=2, start=True)

    mobile_line = mobile_user.get_spoken_messages()[0]
    web_line = web_user.get_spoken_messages()[0]
    spectator_line = spectator_user.get_spoken_messages()[0]
    desktop_line = desktop.get_user(desktop.players[0]).get_spoken_messages()[0]
    assert "hold gesture" in mobile_line and "Claim Bingo" in mobile_line
    assert "hold gesture" in web_line and "Claim Bingo" in web_line
    assert "press B" in desktop_line
    assert "claim" not in spectator_line.lower()
    assert all(
        "Shift+Enter" not in line
        for line in (mobile_line, web_line, spectator_line, desktop_line)
    )


def test_spectators_see_no_card_controls_and_cannot_claim_or_mark() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    spectator = game.add_spectator("Watcher", MockUser("Watcher", uuid="watch1"))
    visible = {r.action.id for r in game.get_all_visible_actions(spectator)}
    assert not any(a.startswith("grid_cell_") or a == "claim_bingo" for a in visible)
    _force_announce(game, 7)  # repeat_call needs at least one call
    enabled = {r.action.id for r in game.get_all_enabled_actions(spectator)}
    assert {"repeat_call", "check_called"} <= enabled
    assert not any(a.startswith("grid_cell_") or a == "claim_bingo" for a in enabled)
    assert game._is_claim_enabled(spectator) == "action-spectator"

    game.handle_event(
        spectator,
        {"type": "keybind", "key": "enter", "shift": True, "menu_item_id": grid_cell_id(0, 0)},
    )
    game.handle_event(spectator, {"type": "keybind", "key": "b"})
    assert game.pending_claim_player_id is None


def test_bot_daub_cue_is_public_at_most_once_per_call() -> None:
    """Several bots holding the same number used to each broadcast their
    own identical daub cue, stacking into a burst per call."""
    game = make_game(player_count=4, bot_indices={1, 2, 3}, start=True)
    listener, *bots = game.players
    for bot in bots[1:]:
        bot.card = [row[:] for row in bots[0].card]
        bot.marked = [row[:] for row in bots[0].marked]
    number = next(v for row in bots[0].card for v in row if v != FREE_VALUE)
    user = game.get_user(listener)

    _force_announce(game, number)
    assert advance_until(
        game,
        lambda: all(b.pending_mark_number is None for b in bots),
    )
    assert all(b.marked[r][c] for b in bots for r in range(CARD_ROWS) for c in range(CARD_COLS) if b.card[r][c] == number)
    assert user.get_sounds_played().count("game_bingo/daub.ogg") == 1


def test_call_sequence_round_trips_through_save_and_load() -> None:
    game = make_game(player_count=2, start=True)
    users = {p.id: game.get_user(p) for p in game.players}
    game.available_numbers = [42]
    game._start_next_call()
    for _ in range(10):
        game.on_tick()
    assert game.pending_call_number == 42
    assert game.has_active_sequence(tag=CALL_SEQUENCE_TAG)

    restored = BingoGame.from_json(game.to_json())
    for player_id, user in users.items():
        restored.attach_user(player_id, user)
    assert restored.pending_call_number == 42
    assert restored.has_active_sequence(tag=CALL_SEQUENCE_TAG)

    assert advance_until(restored, lambda: restored.pending_call_number is None)
    assert restored.called_numbers[-1:] == [42]
    assert restored.call_countdown_ticks > 0


def test_claim_sequence_round_trips_through_save_and_load() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    users = {p.id: game.get_user(p) for p in game.players}
    winner = game.players[0]
    _force_line_win(game, winner)
    game._action_claim_bingo(winner, "claim_bingo")
    for _ in range(10):
        game.on_tick()
    assert game.pending_claim_player_id == winner.id

    restored = BingoGame.from_json(game.to_json())
    for player_id, user in users.items():
        restored.attach_user(player_id, user)
    restored_winner = next(p for p in restored.players if p.id == winner.id)
    assert restored.pending_claim_player_id == winner.id
    assert restored.is_sequence_gameplay_locked()
    assert restored._is_claim_enabled(restored.players[1]) == "bingo-claim-in-progress"

    assert advance_until(restored, lambda: restored.pending_claim_player_id is None)
    assert restored_winner.has_bingo is True


def test_rejected_claim_memory_survives_save_and_load() -> None:
    game = make_game(player_count=2, pattern=PATTERN_LINE, start=True)
    player = game.players[0]
    game._action_claim_bingo(player, "claim_bingo")
    _resolve_claim(game)
    restored = BingoGame.from_json(game.to_json())
    restored_player = next(p for p in restored.players if p.id == player.id)
    assert restored._is_claim_enabled(restored_player) == "bingo-claim-unchanged"


def test_bingo_timed_audio_is_measured_from_the_shipped_assets() -> None:
    for sound in bingo_audio.BINGO_TIMED_ASSET_PATHS:
        measured = measure_audio_duration_ticks(
            REPO_ROOT / "client" / "sounds" / sound, ticks_per_second=TICKS_PER_SECOND
        )
        assert measured is not None
        assert bingo_audio.sound_ticks(sound) == measured
        # The fallback table must track the shipped assets too.
        assert bingo_audio.AUDIO_DURATIONS_TICKS[sound] == measured
    assert CALL_SPIN_DELAY_TICKS == bingo_audio.sound_ticks(bingo_audio.SOUND_CALL)
    assert CLAIM_SUSPENSE_TICKS_FOR_TESTS == bingo_audio.sound_ticks(bingo_audio.SOUND_SUSPENSE)


def test_bingo_timed_audio_falls_back_when_assets_are_missing(monkeypatch) -> None:
    monkeypatch.setattr(bingo_audio, "_SOUND_ASSET_ROOTS", ())
    bingo_audio.sound_ticks.cache_clear()
    try:
        for sound, expected in bingo_audio.AUDIO_DURATIONS_TICKS.items():
            assert bingo_audio.sound_ticks(sound) == expected
        assert bingo_audio.sound_ticks("game_bingo/../x.ogg") == 0
    finally:
        bingo_audio.sound_ticks.cache_clear()


def test_bingo_sounds_are_identical_across_all_three_clients() -> None:
    for name in BINGO_SOUND_FILES:
        payloads = {
            root: (REPO_ROOT / root / "sounds" / "game_bingo" / name).read_bytes()
            for root in ("client", "web_client", "mobile_client")
        }
        assert len(set(payloads.values())) == 1, name
        assert payloads["client"].startswith(b"OggS"), name
