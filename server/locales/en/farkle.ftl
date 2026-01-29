# Farkle game messages

# Game info
game-name-farkle = Farkle

# Actions - Roll and Bank
farkle-roll = Roll { $count } { $count ->
    [one] die
   *[other] dice
}
farkle-bank = Bank { $points } points

# Scoring combination actions (matching v10 exactly)
farkle-take-single-one = Single 1 for { $points } points
farkle-take-single-five = Single 5 for { $points } points
farkle-take-three-kind = Three { $number }s for { $points } points
farkle-take-four-kind = Four { $number }s for { $points } points
farkle-take-five-kind = Five { $number }s for { $points } points
farkle-take-six-kind = Six { $number }s for { $points } points
farkle-take-small-straight = Small Straight for { $points } points
farkle-take-large-straight = Large Straight for { $points } points
farkle-take-three-pairs = Three pairs for { $points } points
farkle-take-double-triplets = Double triplets for { $points } points
farkle-take-full-house = Full house for { $points } points

# Game events (matching v10 exactly)
farkle-rolls = { $player } rolls { $count } { $count ->
    [one] die
   *[other] dice
}...
farkle-roll-result = { $dice }
farkle-farkle = FARKLE! { $player } loses { $points } points
farkle-takes-combo = { $player } takes { $combo } for { $points } points
farkle-you-take-combo = You take { $combo } for { $points } points
farkle-hot-dice = Hot dice!
farkle-banks = { $player } banks { $points } points for a total of { $total }
farkle-winner = { $player } wins with { $score } points!
farkle-winners-tie = We have a tie! Winners: { $players }

# Check turn score action
farkle-turn-score = { $player } has { $points } points this turn.
farkle-no-turn = No one is currently taking a turn.

# Farkle-specific options
farkle-set-target-score = Target score: { $score }
farkle-enter-target-score = Enter target score (500-5000):
farkle-option-changed-target = Target score set to { $score }.

# Disabled action reasons
farkle-must-take-combo = You must take a scoring combination first.
farkle-cannot-bank = You cannot bank right now.

# Combo names (for announcements)
farkle-combo-single-1 = Single 1
farkle-combo-single-5 = Single 5
farkle-combo-three-kind = Three { $number }s
farkle-combo-four-kind = Four { $number }s
farkle-combo-five-kind = Five { $number }s
farkle-combo-six-kind = Six { $number }s
farkle-combo-small-straight = Small Straight
farkle-combo-large-straight = Large Straight
farkle-combo-three-pairs = Three pairs
farkle-combo-double-triplets = Double triplets
farkle-combo-full-house = Full house

# Formatting
farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } for { $points } points
