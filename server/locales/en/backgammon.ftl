# Backgammon localization

game-name-backgammon = Backgammon

# Colors
backgammon-color-red = red
backgammon-color-white = white

# Menu helpers
backgammon-unavailable = unavailable

# Game start
backgammon-game-started = { $red } plays Red, { $white } plays White.
backgammon-opening-roll = Opening roll: { $red } rolls { $red_die }, { $white } rolls { $white_die }.
backgammon-opening-tie = Both rolled { $die }, re-rolling.
backgammon-opening-winner = { $player } goes first with { $die1 } and { $die2 }.

# Dice
backgammon-roll = { $player } rolls { $die1 } and { $die2 }.

# No moves
backgammon-no-moves = { $player } has no legal moves.

# Move commentary (shorthand)
backgammon-move-normal = { $src } to { $dest }, { $remain } { $count }.
backgammon-move-emptying = Emptying { $src } to { $dest }, { $count }.
backgammon-move-hit = { $src } to capture on { $dest }, { $remain }.
backgammon-move-emptying-hit = Emptying { $src } to capture on { $dest }.
backgammon-move-bar = Bar to { $dest }, { $count }.
backgammon-move-bar-hit = Bar to capture on { $dest }, { $count }.
backgammon-move-bearoff = Bearing off from { $src }, { $remain }.

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
backgammon-doubles = { $player } doubles to { $value }.
backgammon-accepts = { $player } accepts.
backgammon-drops = { $player } drops.
backgammon-accept = Accept
backgammon-drop = Drop

# Point labels
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } selected
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } selected

# Action labels
backgammon-label-double = Double
backgammon-label-undo = Undo

# Selection feedback
backgammon-selected-point = Selected point { $point }, { $count } checkers.
backgammon-selected-bar = Selected bar.
backgammon-deselected = Deselected.
backgammon-no-checkers-there = No checkers there.
backgammon-not-your-checkers = Those are not your checkers.
backgammon-no-moves-from-here = No legal moves from here.
backgammon-must-enter-from-bar = Must enter from bar first.
backgammon-illegal-move = Illegal move.
backgammon-bearoff-blocked = You can't bear off from the { $point }-point with a { $die }, because there are checkers on your { $blocking_point }-point.
backgammon-bearoff-no-die = You can't bear off from the { $point }-point with your remaining dice ({ $die }).
backgammon-nothing-to-undo = Nothing to undo.
backgammon-undone = Move undone.
backgammon-cannot-double = You can't double right now.
backgammon-cannot-undo = Nothing to undo.
backgammon-not-doubling-phase = No double to respond to.

# Info keybinds
backgammon-check-status = Status
backgammon-check-cube = Cube
backgammon-check-pip = Pip count
backgammon-check-score = Score
backgammon-check-dice = Dice
backgammon-status = Red bar: { $bar_red }. White bar: { $bar_white }. Red off: { $off_red }. White off: { $off_white }.
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
backgammon-match-score = { $red } { $red_score }, { $white } { $white_score }. Match to { $match_length }. Cube: { $cube }.

# Scoring
backgammon-wins-game = { $player } wins { $points } point{ $points ->
    [one] {""}
    *[other] s
}.
backgammon-new-game = Starting game { $number }.
backgammon-match-winner = { $player } wins the match!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. Match to { $match_length }.
backgammon-crawford = Crawford game: no doubling this game.

# Difficulty levels
backgammon-difficulty-random = Random
backgammon-difficulty-simple = Simple

# Options
backgammon-option-match-length = Match length: { $match_length }
backgammon-option-select-match-length = Set match length (1-25)
backgammon-option-changed-match-length = Match length set to { $match_length }.
backgammon-option-bot-difficulty = Bot difficulty: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Select bot difficulty
backgammon-option-changed-bot-difficulty = Bot difficulty set to { $bot_difficulty }.
