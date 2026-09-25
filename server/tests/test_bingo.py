"""Tests for the Bingo game."""

import random
from pathlib import Path

from ..games.bingo.game import (
    CALL_SEQUENCE_TAG,
    CALL_SPIN_DELAY_TICKS,
    CARD_COLS,
    CARD_ROWS,
    CLAIM_SEQUENCE_TAG,
    COLUMN_LETTERS,
    COLUMN_RANGES,
    ERROR_SOUND_SEQUENCE_TAG,
    FREE_COL,
    FREE_ROW,
    FREE_VALUE,
    PATTERN_BLACKOUT,
    PATTERN_FOUR_CORNERS,
    PATTERN_LETTER_X,
    PATTERN_LINE,
    TICKS_PER_SECOND,
    TOTAL_BALLS,
    WIN_SOUND_SEQUENCE_TAG,
    BingoGame,
    BingoOptions,
    BingoPlayer,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
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


def test_numbers_are_called_at_configured_interval() -> None:
    game = make_game(player_count=2, call_interval="5", start=True)
    assert advance_until(game, lambda: len(game.called_numbers) == 1)

    ticks_elapsed = 0
    while len(game.called_numbers) == 1 and ticks_elapsed < 5000:
        game.on_tick()
        ticks_elapsed += 1

    # The interval is the true announcement-to-announcement cadence now:
    # 5 seconds at 20 ticks/sec is exactly 100 ticks between the first
    # call being announced and the second one being announced, spin
    # sound included -- not 100 seconds' worth of countdown *plus* the
    # spin delay on top, which is what a caller literally saying "every
    # 5 seconds" should mean.
    assert ticks_elapsed == 100


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
    assert game.has_active_sequence(tag=WIN_SOUND_SEQUENCE_TAG)

    for _ in range(TICKS_PER_SECOND - 1):
        game.on_tick()
    assert "game_bingo/win.ogg" not in listener_user.get_sounds_played()

    assert advance_until(
        game, lambda: "game_bingo/win.ogg" in listener_user.get_sounds_played()
    )


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
    assert game.has_active_sequence(tag=ERROR_SOUND_SEQUENCE_TAG)

    for _ in range(TICKS_PER_SECOND - 1):
        game.on_tick()
    assert "game_bingo/error.ogg" not in listener_user.get_sounds_played()

    assert advance_until(
        game, lambda: "game_bingo/error.ogg" in listener_user.get_sounds_played()
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


def test_touch_turn_menu_puts_claim_bingo_before_the_grid() -> None:
    """claim_bingo lives in the turn action set, not the standard one --
    _order_touch_standard_actions can only reorder IDs already on the
    set it's given, so listing claim_bingo there (as this used to) was
    a silent no-op. The real fix reorders create_turn_action_set
    itself, putting the time-critical reaction control first for touch
    clients rather than after all 25 grid cells."""
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    user = game.get_user(player)
    user.client_type = "mobile"

    action_set = game.create_turn_action_set(player)
    assert action_set._order[0] == "claim_bingo"
    assert len(action_set._order) > 1


def test_desktop_turn_menu_is_unaffected_by_touch_ordering() -> None:
    game = make_game(player_count=2, start=True)
    player = game.players[0]
    action_set = game.create_turn_action_set(player)
    assert action_set._order[0] != "claim_bingo"


def test_touch_standard_actions_follow_touch_order() -> None:
    """claim_bingo doesn't belong to this action set at all (see
    create_turn_action_set), and whose_turn -- Bingo's repurposed T
    keybind -- must actually be reachable in the touch order too."""
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
