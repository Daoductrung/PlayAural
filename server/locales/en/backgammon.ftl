# Backgammon localization

game-name-backgammon = Backgammon

# Colors
backgammon-color-red = red
backgammon-color-white = white

# Game start
backgammon-game-started = { $red } plays Red, { $white } plays White.
backgammon-game-started-you-red = You play Red. { $opponent } plays White.
backgammon-game-started-you-white = You play White. { $opponent } plays Red.
backgammon-opening-roll = Opening roll: { $red } rolls { $red_die }, { $white } rolls { $white_die }.
backgammon-opening-roll-you = Opening roll: You roll { $your_die }, { $opponent } rolls { $opponent_die }.
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
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } selected
backgammon-point-occupied-selected-bearoff = { $point } { $color }, { $count } selected; activate again to bear off

# Action labels
backgammon-label-double = Double
backgammon-label-roll = Roll dice
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
backgammon-bearoff-outside-home-point = Point { $point } is outside your home board. Only checkers on points 1 through 6 can bear off.
backgammon-bearoff-blocked = You can't bear off from the { $point }-point with a { $die }, because there are checkers on your { $blocking_point }-point.
backgammon-bearoff-no-die = You can't bear off from the { $point }-point with your remaining dice ({ $die }).
backgammon-nothing-to-undo = Nothing to undo.
backgammon-undo-move = { $listener ->
    [actor] You undo your move from { $source } to { $destination }.
    *[observer] { $player } undoes their move from { $source } to { $destination }.
}
backgammon-undo-hit = { $listener ->
    [actor] You undo your move from { $source } to { $destination }, restoring { $opponent }'s checker.
    [target] { $player } undoes their move from { $source } to { $destination }, restoring your checker.
    *[observer] { $player } undoes their move from { $source } to { $destination }, restoring { $opponent }'s checker.
}
backgammon-selection-cleared = Checker selection cleared.
backgammon-no-selection = No checker is selected.
backgammon-cannot-double = You can't double right now.
backgammon-double-single-game = The doubling cube is not used in a single game.
backgammon-double-crawford = This is the Crawford game, so the doubling cube is unavailable.
backgammon-double-dead-cube = You would already win the match by winning at the cube's current value, so the cube is dead for you and may not be doubled.
backgammon-double-cube-owned = Your opponent owns the cube, so only they may offer the next double.
backgammon-double-before-roll-only = You may offer a double only at the start of your turn, before rolling.
backgammon-cannot-undo = Nothing to undo.
backgammon-not-doubling-phase = No double to respond to.
backgammon-need-roll-first = You need to roll the dice before moving a checker.
backgammon-roll-before-moving-only = You may roll only at the start of your turn, before moving.
backgammon-confirm-drop-double = Dropping concedes this game at the current cube value. Press Drop again within { $seconds } seconds to confirm.

# Info keybinds
backgammon-check-status = Status
backgammon-check-cube = Cube
backgammon-check-pip = Pip count
backgammon-check-dice = Dice
backgammon-check-legal-moves = Legal moves
backgammon-status = { $red_self ->
    [yes] You, Red
    *[no] { $red }, Red
} — bar: { $bar_red }, outside home: { $outside_red }, borne off: { $off_red }. { $white_self ->
    [yes] You, White
    *[no] { $white }, White
} — bar: { $bar_white }, outside home: { $outside_white }, borne off: { $off_white }.
backgammon-dice = { $is_self ->
    [yes] Your remaining dice: { $dice }.
    *[no] { $player }'s remaining dice: { $dice }.
}
backgammon-dice-none = No dice.
backgammon-no-dice-list = none
backgammon-cube-status = Cube at { $value }. { $owner ->
    [center] Centered, either player may double.
    [self] You own the cube.
    *[other] Owned by { $owner }.
} { $can_double ->
    [yes] Doubling is available now.
    [crawford] This is a Crawford game, no doubling allowed.
    [dead] The cube is dead for the current player because its value is already enough to win the match.
    *[no] Doubling is not available right now.
}
backgammon-cube-no-match = No doubling cube in single games.
backgammon-pip-count = { $red_self ->
    [yes] You, Red
    *[no] { $red }, Red
}: { $red_pip } pips. { $white_self ->
    [yes] You, White
    *[no] { $white }, White
}: { $white_pip } pips.
backgammon-match-score-line = { $is_self ->
    [yes] You: { $score } of { $match_length }.
    *[no] { $player }: { $score } of { $match_length }.
}
backgammon-match-score-cube-line = Cube: { $cube }.

# Legal move status
backgammon-legal-moves-awaiting-roll = { $is_self ->
    [yes] You must roll before any checker moves are available.
    *[no] { $player } must roll before any checker moves are available.
}
backgammon-legal-moves-awaiting-double-response = { $is_self ->
    [yes] You must accept or drop the offered double before play continues.
    *[no] { $player } must accept or drop the offered double before play continues.
}
backgammon-legal-moves-none = { $is_self ->
    [yes] You have no legal checker moves.
    *[no] { $player } has no legal checker moves.
}
backgammon-move-source-bar = bar
backgammon-move-destination-off = off the board
backgammon-legal-move-line = { $is_self ->
    [yes] You: { $source } to { $destination } using { $die }
    *[no] { $player }: { $source } to { $destination } using { $die }
}{ $hit ->
    [yes] , hitting a blot.
    *[no] .
}

backgammon-wins-game-you = You win { $points } point{ $points ->
    [one] {""}
    *[other] s
}. { $result ->
    [single] Normal win at cube { $cube }.
    [gammon] Gammon at cube { $cube }.
    [backgammon] Backgammon at cube { $cube }.
    *[drop] Your opponent dropped the double at cube { $cube }.
}
backgammon-wins-game-player = { $player } wins { $points } point{ $points ->
    [one] {""}
    *[other] s
}. { $result ->
    [single] Normal win at cube { $cube }.
    [gammon] Gammon at cube { $cube }.
    [backgammon] Backgammon at cube { $cube }.
    *[drop] Their opponent dropped the double at cube { $cube }.
}
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
