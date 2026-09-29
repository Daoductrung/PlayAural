game-name-leftrightcenter = Left Center Right

lrc-roll = Roll { $count } { $count ->
    [one] die
   *[other] dice
}
lrc-roll-label = Roll dice

lrc-face-left = Left
lrc-face-center = Center
lrc-face-right = Right
lrc-face-dot = Dot

lrc-you-roll = You roll { $results }.
lrc-player-rolls = { $player } rolls { $results }.
lrc-you-roll-brief = You: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = You pass { $count } { $count ->
    [one] chip
   *[other] chips
} left to { $target }. You have { $remaining } left; { $target } now has { $target_total }.
lrc-player-passes-left = { $player } passes { $count } { $count ->
    [one] chip
   *[other] chips
} left to { $target }. { $player } has { $remaining } left; { $target } now has { $target_total }.
lrc-you-pass-left-brief = You, left to { $target }: { $count }. Remaining: { $remaining }.
lrc-player-passes-left-brief = { $player }, left to { $target }: { $count }. Remaining: { $remaining }.

lrc-you-pass-right = You pass { $count } { $count ->
    [one] chip
   *[other] chips
} right to { $target }. You have { $remaining } left; { $target } now has { $target_total }.
lrc-player-passes-right = { $player } passes { $count } { $count ->
    [one] chip
   *[other] chips
} right to { $target }. { $player } has { $remaining } left; { $target } now has { $target_total }.
lrc-you-pass-right-brief = You, right to { $target }: { $count }. Remaining: { $remaining }.
lrc-player-passes-right-brief = { $player }, right to { $target }: { $count }. Remaining: { $remaining }.

lrc-you-pass-center = You put { $count } { $count ->
    [one] chip
   *[other] chips
} in the center. You have { $remaining } left; the center now holds { $center }.
lrc-player-passes-center = { $player } puts { $count } { $count ->
    [one] chip
   *[other] chips
} in the center. { $player } has { $remaining } left; the center now holds { $center }.
lrc-you-pass-center-brief = You, center: { $count }. Remaining: { $remaining }. Center total: { $center }.
lrc-player-passes-center-brief = { $player }, center: { $count }. Remaining: { $remaining }. Center total: { $center }.

lrc-you-keep-all = All of your dice are dots, so you keep all { $count } { $count ->
    [one] chip
   *[other] chips
}.
lrc-player-keeps-all = All of { $player }'s dice are dots, so { GENDER_TERM($player_gender, "subject-have") } all { $count } { $count ->
    [one] chip
   *[other] chips
} left.
lrc-you-keep-all-brief = You: no transfers; { $count } { $count ->
    [one] chip
   *[other] chips
}.
lrc-player-keeps-all-brief = { $player }: no transfers; { $count } { $count ->
    [one] chip
   *[other] chips
}.

lrc-you-skip-no-chips = You have no chips, so your turn is skipped. You remain in the game and can receive chips from either neighbor.
lrc-player-skips-no-chips = { $player } has no chips, so { GENDER_TERM($player_gender, "possessive-determiner") } turn is skipped. { GENDER_TERM($player_gender, "subject-be-capitalized") } still in the game and can receive chips from either neighbor.
lrc-you-skip-no-chips-brief = You: no chips; turn skipped.
lrc-player-skips-no-chips-brief = { $player }: no chips; turn skipped.

lrc-you-win = You are the last player with chips and win with { $count } remaining. You claim the { $center } { $center ->
    [one] chip
   *[other] chips
} in the center.
lrc-player-wins = { $player } is the last player with chips and wins with { $count } remaining. The { $center } { $center ->
    [one] chip
   *[other] chips
} in the center go to { GENDER_TERM($player_gender, "object") }.
lrc-you-win-brief = You win. Your chips: { $count }. Center: { $center }.
lrc-player-wins-brief = { $player } wins. Chips: { $count }. Center: { $center }.

lrc-roll-already-resolving = Your roll is already being resolved. Wait for the chip transfers to finish.
lrc-no-chips-to-roll = You have no chips to roll. Your turn will be skipped automatically.

lrc-center-pot = Center pot: { $count } { $count ->
    [one] chip
   *[other] chips
}.
lrc-check-center = Check center pot
lrc-check-last-roll = Check last roll
lrc-last-roll-none = No dice have been rolled yet.
lrc-last-roll-you = Your last roll was { $results }.
lrc-last-roll-player = { $player } last rolled { $results }.

lrc-set-starting-chips = Starting chips: { $count }
lrc-enter-starting-chips = Enter starting chips:
lrc-option-changed-starting-chips = Starting chips set to { $count }.
leftrightcenter-desc-starting-chips = How many chips each Left Right Center player starts with (default 3, range 1-10).
lrc-error-starting-chips-invalid = Starting chips must be between { $min } and { $max }; the current value is { $count }.

lrc-line-format = { $player }: { $chips } { $chips ->
    [one] chip
   *[other] chips
}
