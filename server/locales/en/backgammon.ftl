# Backgammon localization

game-name-backgammon = Backgammon

# Colors
backgammon-color-red = red
backgammon-color-white = white

# Game start
backgammon-game-started = { $red } plays Red, { $white } plays White.
backgammon-opening-roll = Opening roll: { $red } rolls { $red_die }, { $white } rolls { $white_die }.
backgammon-opening-tie = Both rolled { $die }, re-rolling.
backgammon-opening-winner-you = You go first with { $die1 } and { $die2 }.
backgammon-opening-winner-player = { $player } goes first with { $die1 } and { $die2 }.

# Dice
backgammon-roll-you = You roll { $die1 } and { $die2 }.
backgammon-roll-player = { $player } rolls { $die1 } and { $die2 }.

# No moves
backgammon-no-moves-you = You have no legal moves, so your turn ends.
backgammon-no-moves-player = { $player } has no legal moves, so their turn ends.

# Brief move commentary
backgammon-brief-move-normal = { $is_self ->
    [yes] You: { $src } to { $dest }.
    *[no] { $player }: { $src } to { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] You: { $src } to { $dest }, hit { $opponent }.
    [spectator] { $player }: { $src } to { $dest }, hit { $opponent }.
    *[no] { $player }: { $src } to { $dest }, hit you.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] You: bar to { $dest }.
    *[no] { $player }: bar to { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] You: bar to { $dest }, hit { $opponent }.
    [spectator] { $player }: bar to { $dest }, hit { $opponent }.
    *[no] { $player }: bar to { $dest }, hit you.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] You: { $src } off.
    *[no] { $player }: { $src } off.
}

# Verbose move commentary
backgammon-verbose-move-normal = { $is_self ->
    [yes] You move a checker from point { $src } to point { $dest }.
    *[no] { $player } moves a checker from point { $src } to point { $dest }.
} { $src_count ->
    [0] Point { $src } is now empty, { $dest_count } on point { $dest }.
    *[other] { $src_count } now on point { $src }, { $dest_count } on point { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] You move a checker from point { $src } to capture { $opponent }'s checker on point { $dest }.
    [spectator] { $player } moves a checker from point { $src } to capture { $opponent }'s checker on point { $dest }.
    *[no] { $player } moves a checker from point { $src } to capture your checker on point { $dest }.
} { $src_count ->
    [0] Point { $src } is now empty.
    *[other] { $src_count } remaining on point { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] You enter from the bar to point { $dest }.
    *[no] { $player } enters from the bar to point { $dest }.
} { $dest_count } now on point { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] You enter from the bar to capture { $opponent }'s checker on point { $dest }.
    [spectator] { $player } enters from the bar to capture { $opponent }'s checker on point { $dest }.
    *[no] { $player } enters from the bar to capture your checker on point { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] You bear off from point { $src }.
    *[no] { $player } bears off from point { $src }.
} { $src_count ->
    [0] Point { $src } is now empty.
    *[other] { $src_count } remaining on point { $src }.
}

# Doubling
backgammon-doubles-you = You offer to double the cube to { $value }.
backgammon-doubles-player = { $player } offers to double the cube to { $value }.
backgammon-accepts-you = You accept the double and take ownership of the cube.
backgammon-accepts-player = { $player } accepts the double and takes ownership of the cube.
backgammon-drops-you = You drop the double and concede the current cube value.
backgammon-drops-player = { $player } drops the double and concedes the current cube value.
backgammon-accept = Accept
backgammon-drop = Drop

# Point labels
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } selected
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } selected
backgammon-point-occupied-selected-bearoff = { $point } { $color }, { $count } selected; activate again to bear off

# Action labels
backgammon-label-double = Double
backgammon-label-undo = Undo
backgammon-label-deselect = Deselect
backgammon-label-next-destination = Next destination
backgammon-label-previous-destination = Previous destination

# Selection feedback
backgammon-no-checkers-there = No checkers there.
backgammon-not-your-checkers = Those are not your checkers.
backgammon-no-moves-from-here = No legal moves from here.
backgammon-must-enter-from-bar = Must enter from bar first.
backgammon-illegal-move = Illegal move.
backgammon-no-dice-remaining = You have no dice left to use this turn.
backgammon-no-checkers-on-bar = You have no checkers on the bar to enter.
backgammon-invalid-destination = That destination is not a playable backgammon point.
backgammon-source-empty = Point { $point } has no checker to move.
backgammon-source-opponent = Point { $point } contains your opponent's checkers.
backgammon-destination-blocked = Point { $point } is blocked by { $count } opposing checkers.
backgammon-bar-entry-blocked = You cannot enter on point { $point }; it is blocked by { $count } opposing checkers.
backgammon-no-die-for-bar-entry = None of your remaining dice ({ $dice }) enters on point { $point }.
backgammon-no-die-for-destination = None of your remaining dice ({ $dice }) moves from point { $src } to point { $dest }.
backgammon-must-use-forced-die = You must use { $dice } now because backgammon requires both dice when possible, or the higher die when only one die can be played.
backgammon-move-would-waste-die = That move would prevent you from using as many dice as the rules require. Choose another legal move.
backgammon-bearoff-not-home = You cannot bear off yet. Checkers outside your home board: { $outside }. Checkers on the bar: { $bar }. Bring every checker into points 1 through 6 and clear the bar first.
backgammon-bearoff-blocked = You can't bear off from the { $point }-point with a { $die }, because there are checkers on your { $blocking_point }-point.
backgammon-bearoff-no-die = You can't bear off from the { $point }-point with your remaining dice ({ $die }).
backgammon-nothing-to-undo = Nothing to undo.
backgammon-undone = Move undone.
backgammon-cannot-double = You can't double right now.
backgammon-double-single-game = The doubling cube is not used in a single game.
backgammon-double-crawford = This is the Crawford game, so the doubling cube is unavailable.
backgammon-double-cube-owned = Your opponent owns the cube, so only they may offer the next double.
backgammon-double-before-roll-only = You may offer a double only at the start of your turn, before rolling.
backgammon-cannot-undo = Nothing to undo.
backgammon-not-doubling-phase = No double to respond to.
backgammon-need-roll-first = You need to roll the dice before moving a checker.
backgammon-confirm-drop-double = Dropping concedes this game at the current cube value. Press Drop again within { $seconds } seconds to confirm.

# Info keybinds
backgammon-check-status = Status
backgammon-check-cube = Cube
backgammon-check-pip = Pip count
backgammon-check-score = Score
backgammon-check-score-detailed = Detailed score
backgammon-check-dice = Dice
backgammon-status = Red — bar: { $bar_red }, outside home: { $outside_red }, borne off: { $off_red }. White — bar: { $bar_white }, outside home: { $outside_white }, borne off: { $off_white }.
backgammon-dice = { $dice }
backgammon-dice-none = No dice.
backgammon-cube-status = Cube at { $value }. { $owner ->
    [center] Centered, either player may double.
    *[other] Owned by { $owner }.
} { $can_double ->
    [yes] Doubling is available now.
    [crawford] This is a Crawford game, no doubling allowed.
    *[no] Doubling is not available right now.
}
backgammon-cube-no-match = No doubling cube in single games.
backgammon-pip-count = Red pip count: { $red_pip }. White pip count: { $white_pip }.
backgammon-match-score-line = { $player }: { $score } of { $match_length }.
backgammon-match-score-cube-line = Cube: { $cube }.

# Scoring
backgammon-wins-game-you = You win { $points } point{ $points ->
    [one] {""}
    *[other] s
}.
backgammon-wins-game-player = { $player } wins { $points } point{ $points ->
    [one] {""}
    *[other] s
}.
backgammon-new-game = Starting game { $number }.
backgammon-match-winner-you = You win the match!
backgammon-match-winner-player = { $player } wins the match!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. Match to { $match_length }.
backgammon-crawford = Crawford game: no doubling this game.

# Difficulty levels
backgammon-difficulty-random = Random
backgammon-difficulty-simple = Simple

# Options
backgammon-option-match-length = Match length: { $match_length }
backgammon-option-select-match-length = Set match length (1-25)
backgammon-option-changed-match-length = Match length set to { $match_length }.
backgammon-desc-match-length = Points needed to win the Backgammon match. A value of 1 is a single game with no doubling cube (default 1, range 1-25).
backgammon-option-bot-difficulty = Bot difficulty: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Select bot difficulty
backgammon-option-changed-bot-difficulty = Bot difficulty set to { $bot_difficulty }.
backgammon-desc-bot-difficulty = Chooses how bots make moves: Random plays legal moves loosely, while Simple prefers stronger tactical moves.
