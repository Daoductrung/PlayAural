game-name-leftrightcenter = Left Right Center

lrc-roll = Roll { $count } { $count ->
    [one] die
   *[other] dice
}

lrc-face-left = Left
lrc-face-right = Right
lrc-face-center = Center
lrc-face-dot = Dot

lrc-roll-results = { $player } rolls { $results }.
lrc-pass-left = { $player } passes { $count } { $count ->
    [one] chip
   *[other] chips
} to { $target }.
lrc-pass-right = { $player } passes { $count } { $count ->
    [one] chip
   *[other] chips
} to { $target }.
lrc-pass-center = { $player } puts { $count } { $count ->
    [one] chip
   *[other] chips
} in the center.
lrc-no-chips = { $player } has no chips to roll.
lrc-center-pot = { $count } { $count ->
    [one] chip
   *[other] chips
} in the center.
lrc-player-chips = { $player } now has { $count } { $count ->
    [one] chip
   *[other] chips
}.
lrc-winner = { $player } wins with { $count } { $count ->
    [one] chip
   *[other] chips
}!

lrc-set-starting-chips = Starting chips: { $count }
lrc-enter-starting-chips = Enter starting chips:
lrc-option-changed-starting-chips = Starting chips set to { $count }.

lrc-line-format = { $player }: { $chips }
lrc-check-center = Check center pot
lrc-roll-label = Roll dice
