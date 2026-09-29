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
bingo-desc-pattern = The pattern a card must complete to win. Any Line accepts a full row, column, or diagonal. Four Corners requires all four corner squares. Letter X requires both diagonals. Blackout requires the entire card.

bingo-set-call-interval = Call every { $seconds }
bingo-select-call-interval = Select the call interval:
bingo-option-changed-interval = Numbers will now be called every { $seconds }.
bingo-desc-call-interval = How long the caller waits between announcing each number (default 15, range 5-60 seconds).

bingo-cell-free = Free space.
bingo-cell-marked = { $letter } { $number }, marked.
bingo-cell-unmarked = { $letter } { $number }, not marked.
bingo-cell-is-free = This square is already free.
bingo-you-already-won = You already have Bingo this round.

bingo-you-mark = Marked { $letter } { $number }.
bingo-you-unmark = Unmarked { $letter } { $number }.

bingo-claim-bingo = Claim Bingo!
bingo-repeat-call = Repeat last number
bingo-check-called = Check called numbers
bingo-no-calls-yet = No numbers have been called yet.
bingo-claim-in-progress = Another claim is currently being checked. Try again in a moment.
bingo-claim-in-progress-you = Your claim is already being checked.
bingo-claim-wait-for-call = Wait for the number being drawn to be announced, then try again.
bingo-claim-unchanged = Your card hasn't changed since it was last rejected. Mark another number or wait for the next call before claiming again.
bingo-checking-claim-you = You call Bingo. Checking your card...
bingo-checking-claim = { $player } calls Bingo. Checking the card...
bingo-whose-turn-checking = Checking { $player }'s card...
bingo-whose-turn-checking-you = Your card is being checked...
bingo-whose-turn-drawing = Drawing the next number...
bingo-whose-turn-waiting = { $seconds ->
    [one] Next number in { $seconds } second.
   *[other] Next number in { $seconds } seconds.
}
bingo-claim-incorrect-you = Incorrect card.
bingo-claim-incorrect = { $player }'s card is incorrect.
bingo-claim-incomplete-you = You don't have the pattern yet.
bingo-claim-incomplete = { $player } doesn't have the pattern yet.
bingo-marked-number-not-called = You marked { $letter } { $number }, but it hasn't been called yet.

bingo-last-call = { $letter } { $number }

bingo-status-called-count = { $count } of { $total } numbers called.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = Bingo begins! Pattern: { $pattern }. A new number will be called every { $interval } seconds. Mark your card, then press B to claim Bingo when you have it.
bingo-game-start-touch = Bingo begins! Pattern: { $pattern }. A new number will be called every { $interval } seconds. Mark your card, then use your client's hold gesture anywhere on it, or choose Claim Bingo, to claim Bingo when you have it.
bingo-game-start-spectator = Bingo begins! Pattern: { $pattern }. A new number will be called every { $interval } seconds.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = Yes! Correct card. You win with { $numbers }!
bingo-claim-correct = Yes! Correct card. { $player } wins with { $numbers }!
bingo-claim-correct-no-numbers-you = Yes! Correct card. You win!
bingo-claim-correct-no-numbers = Yes! Correct card. { $player } wins!
bingo-deck-exhausted = All 75 numbers have been called. The round ends here.

bingo-error-invalid-interval = "{ $value }" is not a valid call interval.
bingo-error-invalid-pattern = { $value } is not a recognized winning pattern.

bingo-end-calls = { $count ->
    [one] { $count } number was called this round.
   *[other] { $count } numbers were called this round.
}
bingo-end-winner-line = Winner: { $player }
bingo-end-no-winner = No valid Bingo claim was made this round.
