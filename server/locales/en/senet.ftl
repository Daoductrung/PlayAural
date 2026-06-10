# Senet localization

game-name-senet = Senet

# Game start
senet-game-started = { $p1 } is player 1, { $p2 } is player 2. { $first } goes first.

# Throwing sticks
senet-throw-you = You throw { $result }.{ $bonus ->
    [yes] {" "}Bonus throw!
   *[no] {""}
}
senet-throw-other = { $player } throws { $result }.{ $bonus ->
    [yes] {" "}Bonus throw!
   *[no] {""}
}

# Movement
senet-move-you = You move from square { $from } to square { $to }.
senet-move-other = { $player } moves from square { $from } to square { $to }.
senet-swap-you = You swap with { $opponent } on square { $to }. { $opponent } goes back to square { $from }.
senet-swap-other = { $player } swaps with { $opponent } on square { $to }. { $opponent } goes back to square { $from }.
senet-bearoff-you = You bear off from square { $from }. { $remaining } remaining.
senet-bearoff-other = { $player } bears off from square { $from }. { $remaining } remaining.
senet-water-you = You landed in the House of Water! Piece sent to square { $dest }.
senet-water-other = { $player } landed in the House of Water! Piece sent to square { $dest }.
senet-happiness-you = You reached the House of Happiness.
senet-happiness-other = { $player } reached the House of Happiness.
senet-horus-auto-you = Your piece leaves the House of Horus because your first row is clear. { $remaining } remaining.
senet-horus-auto-other = { $player }'s piece leaves the House of Horus because their first row is clear. { $remaining } remaining.

# No moves
senet-no-moves-you = You have no legal moves.
senet-no-moves-other = { $player } has no legal moves.

# Square labels
senet-sq-empty = { $sq }
senet-sq-own = { $sq }, yours
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }, yours
senet-sq-opponent-special = { $sq }, { $name }, { $owner }

# Special square names
senet-house-rebirth = Rebirth
senet-house-happiness = Happiness
senet-house-water = Water
senet-house-three-truths = Three Truths
senet-house-re-atum = Re-Atum
senet-house-horus = Horus

# Status
senet-status = { $p1 }: { $off1 } off. { $p2 }: { $off2 } off.{ $phase ->
    [throwing] {" "}Waiting to throw.
   *[moving] {" "}Roll: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = No throw yet.

# Win
senet-wins-you = You win! All of your pieces have crossed the final house.
senet-wins-other = { $player } wins! All of their pieces have crossed the final house.

# Action labels
senet-check-status = Status
senet-check-sticks = Sticks
senet-next-piece = Next piece
senet-previous-piece = Previous piece
senet-score = { $p1 }: { $off1 } off. { $p2 }: { $off2 } off.

# Errors
senet-not-your-piece = Not your piece.
senet-no-piece-there = No piece there.
senet-no-moves-from-here = No legal moves from this square.
senet-need-throw-first = You need to throw the sticks before choosing a piece to move.
senet-no-movable-pieces = None of your pieces can move with the current throw.
senet-error-exactly-two-players = Senet requires exactly 2 active players. Current active players: { $count }.

# Options
senet-option-bot-difficulty = Bot difficulty: { $bot_difficulty }
senet-option-select-bot-difficulty = Select bot difficulty
senet-option-changed-bot-difficulty = Bot difficulty set to { $bot_difficulty }.
senet-difficulty-random = Random
senet-difficulty-simple = Simple
