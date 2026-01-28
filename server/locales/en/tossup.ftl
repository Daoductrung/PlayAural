# Toss Up game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-tossup = Toss Up
tossup-category = Dice Games

# Actions
tossup-roll-first = Roll { $count } dice
tossup-roll-remaining = Roll { $count } remaining dice
tossup-bank = Bank { $points } points

# Game events
tossup-turn-start = { $player }'s turn. Score: { $score }
tossup-you-roll = You rolled: { $results }.
tossup-player-rolls = { $player } rolled: { $results }.

tossup-result-green = { $count } green
tossup-result-yellow = { $count } yellow
tossup-result-red = { $count } red

# Turn status
tossup-you-have-points = Turn points: { $turn_points }. Dice remaining: { $dice_count }.
tossup-player-has-points = { $player } has { $turn_points } turn points. { $dice_count } dice remaining.

# Fresh dice
tossup-you-get-fresh = No dice left! Getting { $count } fresh dice.
tossup-player-gets-fresh = { $player } gets { $count } fresh dice.

# Bust
tossup-you-bust = Bust! You lose { $points } points for this turn.
tossup-player-busts = { $player } busts and loses { $points } points!

# Bank
tossup-you-bank = You bank { $points } points. Total score: { $total }.
tossup-player-banks = { $player } banks { $points } points. Total score: { $total }.

# Winner
tossup-winner = { $player } wins with { $score } points!
tossup-tie-tiebreaker = It's a tie between { $players }! Tiebreaker round!

# Options
tossup-set-rules-variant = Rules variant: { $variant }
tossup-select-rules-variant = Select rules variant:
tossup-option-changed-rules = Rules variant changed to { $variant }

tossup-set-starting-dice = Starting dice: { $count }
tossup-enter-starting-dice = Enter the number of starting dice:
tossup-option-changed-dice = Starting dice changed to { $count }

# Rules variants
tossup-rules-standard = Standard
tossup-rules-PlayAural = PlayAural

# Rules explanations
tossup-rules-standard-desc = 3 green, 2 yellow, 1 red per die. Bust if no greens and at least one red.
tossup-rules-PlayAural-desc = Equal distribution. Bust if all dice are red.

# Disabled reasons
tossup-need-points = You need points to bank.

# Formatting
tossup-line-format = {  }. {  }: {  }
