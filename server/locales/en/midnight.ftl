game-name-midnight = 1-4-24

midnight-roll = Roll the dice
midnight-bank = Bank
midnight-check-dice = Read current dice
midnight-check-round-status = View round status

midnight-round-start = Round { $round } of { $total }.
midnight-round-start-brief = Round { $round }/{ $total }.

midnight-you-rolled = You rolled: { $dice }.
midnight-player-rolled = { $player } rolled: { $dice }.
midnight-you-rolled-brief = You roll { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = You keep die { $index }, showing { $die }.
midnight-player-keeps = { $player } keeps die { $index }, showing { $die }.
midnight-you-keep-brief = You keep { $die }.
midnight-player-keeps-brief = { $player } keeps { $die }.
midnight-you-unkeep = You return die { $index }, showing { $die }, to the reroll pool.
midnight-player-unkeeps = { $player } returns die { $index }, showing { $die }, to the reroll pool.
midnight-you-unkeep-brief = You reroll { $die }.
midnight-player-unkeeps-brief = { $player } rerolls { $die }.

midnight-you-scored = You qualify with 1 and 4, scoring { $score } from { $scoring_dice }.
midnight-scored = { $player } qualifies with 1 and 4, scoring { $score } from { $scoring_dice }.
midnight-you-scored-brief = You score { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = You do not qualify because you are missing { $missing }.
midnight-player-disqualified = { $player } does not qualify because { GENDER_TERM($player_gender, "subject-be") } missing { $missing }.
midnight-you-disqualified-brief = You miss { $missing }.
midnight-player-disqualified-brief = { $player } misses { $missing }.

midnight-you-win-round = You win round { $round } with { $score }.
midnight-round-winner = { $player } wins round { $round } with { $score }.
midnight-you-win-round-brief = You win R{ $round }: { $score }.
midnight-round-winner-brief = { $player } wins R{ $round }: { $score }.
midnight-round-tie = Round tied at { $score } between { $players }. No round win is awarded.
midnight-all-disqualified = All players missed the required 1 and 4. No round win is awarded.
midnight-all-disqualified-brief = Nobody qualifies.

midnight-you-win-game = You win the game with { $wins } { $wins ->
    [one] round win
   *[other] round wins
}!
midnight-game-winner = { $player } wins the game with { $wins } { $wins ->
    [one] round win
   *[other] round wins
}!
midnight-you-win-game-brief = You win: { $wins }.
midnight-game-winner-brief = { $player } wins: { $wins }.
midnight-game-tie = It is a game tie. { $players } each finished with { $wins } { $wins ->
    [one] round win
   *[other] round wins
}.

midnight-set-rounds = Rounds to play: { $rounds }
midnight-enter-rounds = Enter number of rounds to play:
midnight-option-changed-rounds = Rounds to play changed to { $rounds }
midnight-desc-rounds = Number of Midnight rounds to play before final scoring (default 5, range 1-20).
midnight-error-rounds-out-of-range = Midnight supports { $min } to { $max } rounds. Current setting: { $rounds }.

midnight-need-to-roll = Roll the dice before choosing dice to keep.
midnight-no-dice-to-keep = No dice remain to roll or keep.
midnight-must-keep-one = Keep at least one newly rolled die before rolling again.
midnight-must-roll-first = Roll the dice before banking your turn.
midnight-keep-all-first = Decide every die before banking. Keep or return all unlocked dice first.
midnight-invalid-die-index = That die is not available in this roll.

midnight-die-locked = { $value } (locked)
midnight-die-kept = { $value } (kept)
midnight-die-value = { $value }
midnight-die-index = Die { $index }

midnight-your-dice-not-rolled = You have not rolled yet this turn.
midnight-player-dice-not-rolled = { $player } has not rolled yet this turn.
midnight-your-dice-status =
    { $qualified ->
        [yes] Your dice: { $dice }. Locked: { $locked }; kept for next roll: { $kept }; dice still live: { $remaining }. Current qualifying score would be { $score } from { $scoring_dice }.
       *[no] Your dice: { $dice }. Locked: { $locked }; kept for next roll: { $kept }; dice still live: { $remaining }. You still need { $missing } to qualify.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] { $player }'s dice: { $dice }. Locked: { $locked }; kept for next roll: { $kept }; dice still live: { $remaining }. Current qualifying score would be { $score } from { $scoring_dice }.
       *[no] { $player }'s dice: { $dice }. Locked: { $locked }; kept for next roll: { $kept }; dice still live: { $remaining }. The remaining requirement for { GENDER_TERM($player_gender, "object") } is { $missing }.
    }

midnight-status-round = Round { $round } of { $total }
midnight-status-current-player = Current turn: { $player }
midnight-status-current-not-rolled = { $player } has not rolled yet.
midnight-status-current-dice =
    { $qualified ->
        [yes] Current dice for { $player }: { $dice }. Potential score: { $score } from { $scoring_dice }. Locked { $locked }, kept { $kept}, live { $remaining}.
       *[no] Current dice for { $player }: { $dice }. Missing { $missing}. Locked { $locked }, kept { $kept}, live { $remaining}.
    }
midnight-status-dice-not-rolled = not rolled
midnight-status-last-qualified = Last turn: { $player } rolled { $dice } and scored { $score }.
midnight-status-last-disqualified = Last turn: { $player } rolled { $dice } and did not qualify.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } round wins; current round { $current}, qualified.
       *[no] { $rank }. { $player }: { $wins } round wins; current round { $current}, not qualified.
    }

midnight-score-unit-round-wins = { $count ->
    [one] round win
   *[other] round wins
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] round win
   *[other] round wins
}
