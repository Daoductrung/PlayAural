# 1-4-24 (Midnight) game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-midnight = 1-4-24
midnight-category = Dice Games

# Actions
midnight-roll = Roll the dice
midnight-keep-die = Keep { $value }
midnight-bank = Bank

# Game events
midnight-turn-start = { $player }'s turn.
midnight-you-rolled = You rolled: { $dice }.
midnight-player-rolled = { $player } rolled: { $dice }.

# Keeping dice
midnight-you-keep = You keep { $die }.
midnight-player-keeps = { $player } keeps { $die }.
midnight-you-unkeep = You unkeep { $die }.
midnight-player-unkeeps = { $player } unkeeps { $die }.

# Turn status
midnight-you-have-kept = Kept dice: { $kept }. Remaining rolls: { $remaining }.
midnight-player-has-kept = { $player } has kept: { $kept }. { $remaining } dice remaining.

# Scoring
midnight-you-scored = You scored { $score } points.
midnight-scored = { $player } scored { $score } points.
midnight-you-disqualified = You don't have both 1 and 4. Disqualified!
midnight-player-disqualified = { $player } doesn't have both 1 and 4. Disqualified!

# Round results
midnight-round-winner = { $player } wins the round!
midnight-round-tie = Round tied between { $players }.
midnight-all-disqualified = All players disqualified! No winner this round.

# Game winner
midnight-game-winner = { $player } wins the game with { $wins } round wins!
midnight-game-tie = It's a tie! { $players } each won { $wins } rounds.

# Options
midnight-set-rounds = Rounds to play: { $rounds }
midnight-enter-rounds = Enter number of rounds to play:
midnight-option-changed-rounds = Rounds to play changed to { $rounds }

# Disabled reasons
midnight-need-to-roll = You need to roll the dice first.
midnight-no-dice-to-keep = No available dice to keep.
midnight-must-keep-one = You must keep at least one die per roll.
midnight-must-roll-first = You must roll the dice first.
midnight-must-roll-first = You must roll the dice first.
midnight-keep-all-first = You must keep all dice before banking.

# Dice labels
midnight-die-locked = { $value } (Locked)
midnight-die-kept = { $value } (Kept)
midnight-die-value = { $value }

# End Screen
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] round win
   *[other] round wins
}

midnight-die-index = Die { $index }
