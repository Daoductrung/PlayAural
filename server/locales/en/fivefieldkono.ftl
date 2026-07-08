# Five Field Kono localization

game-name-fivefieldkono = Five Field Kono

# Game start
ffk-game-started = { $p1 } is player 1 (south), { $p2 } is player 2 (north). { $first } goes first.

# Cell labels (grid)
ffk-cell-empty = { $coord }, empty.
ffk-cell-own = { $coord }, your piece.
ffk-cell-opponent = { $coord }, { $owner }'s piece.
ffk-cell-selected = { $label } Selected.
ffk-cell-move-target = { $coord }, move here.

# Selection & movement
ffk-select-own-piece = Select one of your own pieces first.
ffk-piece-no-moves = That piece has no legal moves.
ffk-piece-selected = Selected { $coord }. { $count } { $count ->
    [one] move
   *[other] moves
} available.
ffk-selection-cleared = Selection cleared.
ffk-illegal-move = That is not a legal move for the selected piece.
ffk-move-you = You move from { $from } to { $to }.
ffk-move-other = { $player } moves from { $from } to { $to }.

# Win / loss
ffk-win-you = You moved all your pieces home and won!
ffk-win-other = { $player } moved all their pieces home and won.
ffk-win-stuck-you = Your opponent has no legal moves. You win!
ffk-win-stuck-other = { $player } wins: you have no legal moves left.

# Info actions
ffk-check-board = Review board
ffk-check-progress = My progress
ffk-check-last-move = Last move
ffk-progress = { $home } of { $total } pieces home.
ffk-last-move = Last move: { $from } to { $to }.
ffk-last-move-none = No moves have been made yet.
