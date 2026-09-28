game-name-threes = Threes

threes-roll = Roll the dice
threes-bank = Bank and end turn
threes-check-hand = Check dice

threes-you-rolled = You rolled: { $dice }.
threes-you-rolled-brief = Rolled { $dice }.
threes-player-rolled = { $player } rolled: { $dice }.
threes-player-rolled-brief = { $player }: { $dice }.

threes-turn-you = Your turn in round { $round } of { $total }. Your current total is { $score }; lowest total wins.
threes-turn-you-brief = Your turn. Total { $score }.
threes-turn-other = { $player }'s turn in round { $round } of { $total }. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } current total is { $score }.
threes-turn-other-brief = { $player}'s turn. Total { $score }.

threes-you-keep = You keep die { $index }, showing { $die }.
threes-you-keep-brief = Keep { $die }.
threes-player-keeps = { $player } keeps die { $index }, showing { $die }.
threes-player-keeps-brief = { $player } keeps { $die }.
threes-you-unkeep = You release die { $index }, showing { $die }, so it can be rerolled.
threes-you-unkeep-brief = Reroll { $die }.
threes-player-unkeeps = { $player } releases die { $index }, showing { $die }, so it can be rerolled.
threes-player-unkeeps-brief = { $player } rerolls { $die }.

threes-your-dice = Your dice are { $dice }. If scored now, this turn is worth { $score } points, with { $remaining } dice still unlocked.
threes-player-dice = { $player }'s dice are { $dice }. If scored now, this turn is worth { $score } points, with { $remaining } dice still unlocked.
threes-no-dice-yet = You have not rolled dice in this turn yet.
threes-dice-locked = locked
threes-dice-kept = kept
threes-dice-format-status = { $value } ({ $status })
threes-die-index = Die { $index }
threes-die-value = Keep { $value }
threes-die-kept-label = Reroll { $value }
threes-die-locked-label = { $value } locked

threes-you-scored = You score { $score } points this turn. Your total is now { $total }.
threes-you-scored-brief = Scored { $score }. Total { $total }.
threes-scored = { $player } scores { $score } points this turn. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } total is now { $total }.
threes-scored-brief = { $player }: { $score }, total { $total }.
threes-you-shot-moon = You shot the moon with five sixes and score { $score } points. Your total is now { $total }.
threes-you-shot-moon-brief = Shot the moon: { $score }. Total { $total }.
threes-shot-moon = { $player } shot the moon with five sixes and scores { $score } points. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } total is now { $total }.
threes-shot-moon-brief = { $player } shot the moon: { $score }, total { $total }.

threes-round-start = Round { $round } of { $total } begins.
threes-round-start-brief = Round { $round }.
threes-round-scores-header = Round { $round } scores:
threes-round-scores-header-brief = Scores after round { $round }:
threes-score-pair = { $player }: { $score }

threes-winner = { $player } wins with { $score } points!
threes-winner-you = You win Threes with { $score } points!
threes-winner-you-brief = You win with { $score }.
threes-winner-other = { $player } wins Threes with { $score } points!
threes-winner-other-brief = { $player } wins with { $score }.
threes-tie = { $players } tie for the lowest total with { $score } points!
threes-tie-brief = Tie: { $players }, { $score }.
threes-tie-you = You tie with { $players } for the lowest total at { $score } points!
threes-tie-you-brief = You tie with { $players } at { $score }.

threes-set-rounds = Rounds: { $rounds }
threes-enter-rounds = Enter number of rounds:
threes-option-changed-rounds = Number of rounds set to { $rounds }.
threes-desc-rounds = Number of rounds to play. Each player takes one turn per round, and the lowest total score wins (default 10, range 1-20).

threes-error-roll-not-playing = You cannot roll because Threes has not started.
threes-error-roll-no-turn = You cannot roll because no active turn is available right now.
threes-error-roll-not-your-turn = You cannot roll right now because it is { $player }'s turn.
threes-error-roll-last-die = You cannot roll again because only one die remains unlocked; the turn must be scored now.
threes-error-roll-must-keep = Keep at least one unlocked die before rolling again.
threes-error-bank-not-playing = You cannot bank because Threes has not started.
threes-error-bank-no-turn = You cannot bank because no active turn is available right now.
threes-error-bank-not-your-turn = You cannot bank right now because it is { $player }'s turn.
threes-error-bank-roll-first = Roll the dice before trying to bank your turn score.
threes-error-bank-keep-all = Keep every unlocked die before banking, so the full turn score is decided.
threes-error-check-not-playing = Dice can only be checked after Threes has started.
threes-error-check-no-turn = Dice cannot be checked because no active turn is available right now.
threes-error-check-your-dice-not-rolled = You have not rolled yet, so there are no current dice to check.
threes-error-check-player-dice-not-rolled = { $player } has not rolled yet, so there are no current dice to check.
threes-error-toggle-last-die = You cannot change the last unlocked die; the turn must be scored from here.
threes-error-rounds-out-of-range = Threes cannot start with { $rounds } rounds. Choose a value from { $min } to { $max }.
threes-invalid-die-index = That die is not available in this Threes turn.

threes-must-keep = You must keep at least one die before rolling again.
threes-must-bank = You must bank now.
threes-roll-first = You need to roll first.
threes-keep-all-first = Keep all dice first to bank.
threes-last-die = This is your last die.

threes-line-format = { $rank }. { $player }: { $points }
