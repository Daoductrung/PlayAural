game-name-ludo = Ludo

ludo-roll-die = Roll die
ludo-move-token = Move token
ludo-move-token-n = Move token { $token }
ludo-check-board = View board status
ludo-select-token = Select token to move:

ludo-roll = { $player } rolls a { $roll }.
ludo-you-roll = You roll a { $roll }.
ludo-no-moves = { $player } has no valid moves.
ludo-you-no-moves = You have no valid moves.
ludo-enter-board = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) enters token { $token } onto the board.
ludo-move-track = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) moves token { $token } to position { $position }.
ludo-enter-home = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) moves token { $token } into the home column.
ludo-home-finish = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) token { $token } reaches home. ({ $finished }/4 finished)
ludo-move-home = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) moves token { $token } in home column ({ $position }/{ $total }).
ludo-captures = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) captures { $count ->
    [one] 1 token
   *[other] { $count } tokens
} of { $captured_player } ({ $captured_color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $captured_color }
}). Sent back to yard.
ludo-extra-turn = { $player } rolled a 6. Extra turn.
ludo-you-extra-turn = You rolled a 6. Extra turn.
ludo-too-many-sixes = { $player } rolled { $count } sixes in a row. Moves undone. Turn ends.
ludo-winner = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) wins! All 4 tokens are home.

ludo-board-player = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}): { $finished }/4 finished
ludo-token-yard = Token { $token } (yard)
ludo-token-track = Token { $token } (position { $position })
ludo-token-home = Token { $token } (home column { $position }/{ $total })
ludo-token-finished = Token { $token } (finished)
ludo-last-roll = Last roll: { $roll }

ludo-set-max-sixes = Max consecutive sixes: { $max_consecutive_sixes }
ludo-enter-max-sixes = Enter max consecutive sixes
ludo-option-changed-max-sixes = Max consecutive sixes set to { $max_consecutive_sixes }.
ludo-set-safe-start-squares = Safe start squares: { $enabled }
ludo-option-changed-safe-start-squares = Safe start squares set to { $enabled }.
