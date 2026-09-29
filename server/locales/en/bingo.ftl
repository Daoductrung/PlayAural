game-name-bingo = Bingo

bingo-pattern-line = Any Line
bingo-pattern-four-corners = Four Corners
bingo-pattern-letter-x = Letter X
bingo-pattern-blackout = Blackout

bingo-call-interval-5 = 5 seconds
bingo-call-interval-15 = 15 seconds
bingo-call-interval-30 = 30 seconds
bingo-call-interval-45 = 45 seconds
bingo-call-interval-60 = 60 seconds

bingo-set-pattern = Winning pattern: { $pattern }
bingo-select-pattern = Select the winning pattern:
bingo-option-changed-pattern = The winning pattern is now { $pattern }.
bingo-desc-pattern = The shape needed to win. Any Line means a complete row, column, or diagonal. Four Corners requires all four corner squares. Letter X requires both diagonals. Blackout requires the entire card.

bingo-set-call-interval = Calling pace: { $seconds }
bingo-select-call-interval = Select the calling pace:
bingo-option-changed-interval = The target calling pace is now { $seconds }.
bingo-desc-call-interval = The target time from one announced number to the next. The game always leaves a short window to call Bingo, so the fastest pace may take a little longer.

bingo-cell-free = Free center, marked automatically.
bingo-cell-marked = { $letter } { $number }, marked.
bingo-cell-unmarked = { $letter } { $number }, not marked.
bingo-cell-is-free = The free center is already marked.
bingo-you-already-won = You already have Bingo this round.

bingo-you-mark = Marked { $letter } { $number }.
bingo-you-unmark = Unmarked { $letter } { $number }.

bingo-claim-bingo = Call Bingo!
bingo-repeat-call = Repeat the last number
bingo-check-called = View called numbers
bingo-no-calls-yet = No numbers have been called yet.
bingo-claim-in-progress = Another Bingo call is being checked. Try again in a moment.
bingo-claim-in-progress-you = Your Bingo call is already being checked.
bingo-claim-wait-for-call = Wait until the number being drawn is announced, then try again.
bingo-claim-unchanged = Your card has not changed since its last unsuccessful check. Change a mark or wait for the next number before calling Bingo again.
bingo-checking-claim-you = You call Bingo! Checking your card...
bingo-checking-claim = { $player } calls Bingo! Checking the card...
bingo-whose-turn-checking = Checking { $player }'s card...
bingo-whose-turn-checking-you = Your card is being checked...
bingo-whose-turn-checking-card = A Bingo card is being checked...
bingo-whose-turn-drawing = The next number is being drawn...
bingo-whose-turn-waiting = { $seconds ->
    [one] Next number in { $seconds } second.
   *[other] Next number in { $seconds } seconds.
}
bingo-claim-incorrect-you = Your card does not have a valid Bingo yet.
bingo-claim-incorrect = { $player }'s card does not have a valid Bingo yet.
bingo-claim-incomplete-you = Your card does not complete the winning pattern yet.
bingo-claim-incomplete = { $player }'s card does not complete the winning pattern yet.
bingo-marked-number-not-called = You marked { $letter } { $number }, but that number has not been called yet.

bingo-last-call = Last number: { $letter } { $number }

bingo-status-called-count = Called: { $count } of { $total } numbers.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = Bingo begins! The winning pattern is { $pattern }. Numbers follow a target pace of one every { $interval } seconds, with time left after each call to call Bingo. Mark your card, then press B when you are ready.
bingo-game-start-touch = Bingo begins! The winning pattern is { $pattern }. Numbers follow a target pace of one every { $interval } seconds, with time left after each call to call Bingo. Mark your card, then use your device's hold gesture on the card or choose Call Bingo.
bingo-game-start-spectator = Bingo begins! The winning pattern is { $pattern }. Numbers follow a target pace of one every { $interval } seconds, with time left after each call for players to call Bingo.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = Bingo! You win with { $numbers }!
bingo-claim-correct = Bingo! { $player } wins with { $numbers }!
bingo-claim-correct-no-numbers-you = Bingo! You win!
bingo-claim-correct-no-numbers = Bingo! { $player } wins!
bingo-deck-exhausted = All 75 numbers have been called, and no one called a valid Bingo. The round ends without a winner.

bingo-error-invalid-interval = "{ $value }" is not a valid calling pace.
bingo-error-invalid-pattern = { $value } is not a recognized winning pattern.

bingo-end-calls = { $count ->
    [one] { $count } number was called this round.
   *[other] { $count } numbers were called this round.
}
bingo-end-winner-line = Winner: { $player }
bingo-end-no-winner = No one called a valid Bingo this round.
