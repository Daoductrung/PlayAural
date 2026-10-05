game-name-zombiedice = Zombie Dice

zombiedice-set-target-score = Brains needed to win: { $score }
zombiedice-enter-target-score = Enter a winning target from 5 to 50 brains:
zombiedice-option-changed-target-score = The winning target is now { $score } brains.
zombiedice-desc-target-score = Reaching this score starts the final round for any players still waiting to act. The official target is 13 brains; lower or higher targets make the match shorter or longer.

zombiedice-roll-first = Roll 3 dice
zombiedice-roll-first-description = Draw three hidden dice from the cup and roll them.
zombiedice-roll-again = Roll again — { $brains } { $brains ->
    [one] brain
   *[other] brains
} at stake
zombiedice-roll-again-description = Reroll { $footprints } footprint { $footprints ->
    [one] die
   *[other] dice
} and draw { $draw } new { $draw ->
    [one] die
   *[other] dice
} to make three. A third shotgun wipes out all { $brains } unbanked { $brains ->
    [one] brain
   *[other] brains
}.
zombiedice-bank = Stop and score { $brains } { $brains ->
    [one] brain
   *[other] brains
}
zombiedice-bank-keybind = Stop and score
zombiedice-bank-description = End your turn and bank { $brains } { $brains ->
    [one] brain
   *[other] brains
}.
zombiedice-check-turn-totals = Check turn totals
zombiedice-check-turn-totals-description = Hear the current brains, shotguns, and footprints.
zombiedice-review-turn = Review current turn
zombiedice-review-turn-description = Review every public die, the cup count, the latest roll, and unbanked brains.
zombiedice-review-table = Review table
zombiedice-review-table-description = Review the target, match phase, turn order, current turn, and scores.

zombiedice-game-start = Zombie Dice begins. Target: { $target } brains. { $first } goes first. Order: { $order }.
zombiedice-your-turn = Your turn. Banked: { $score } { $score ->
    [one] brain
   *[other] brains
}. Roll three dice.
zombiedice-player-turn = { $player }'s turn. Banked: { $score } { $score ->
    [one] brain
   *[other] brains
}.
zombiedice-you-refill-cup = Cup low: you return { $count } brain { $count ->
    [one] die
   *[other] dice
}. Your { $brains } turn { $brains ->
    [one] brain stays
   *[other] brains stay
} counted.
zombiedice-player-refills-cup = Cup low: { $player } returns { $count } brain { $count ->
    [one] die
   *[other] dice
}. Their { $brains } turn { $brains ->
    [one] brain stays
   *[other] brains stay
} counted.
zombiedice-you-roll = You roll: { $results }.
zombiedice-player-rolls = { $player } rolls: { $results }.
zombiedice-you-bust = You roll: { $results }. { $shotguns } shotguns—blasted. You lose { $brains } unbanked { $brains ->
    [one] brain
   *[other] brains
}.
zombiedice-player-busts = { $player } rolls: { $results }. { $shotguns } shotguns—blasted. { $player } loses { $brains } unbanked { $brains ->
    [one] brain
   *[other] brains
}.
zombiedice-you-bank = You bank { $brains } { $brains ->
    [one] brain
   *[other] brains
}. Total: { $total }.
zombiedice-player-banks = { $player } banks { $brains } { $brains ->
    [one] brain
   *[other] brains
}. Total: { $total }.
zombiedice-you-trigger-final-round = You reach { $score } brains. { $remaining } { $remaining ->
    [one] player remains
   *[other] players remain
} in the final round.
zombiedice-player-triggers-final-round = { $player } reaches { $score } brains. { $remaining } { $remaining ->
    [one] player remains
   *[other] players remain
} in the final round.
zombiedice-tiebreak-start = Tiebreak { $round }: { $players }, tied at { $score } brains. One turn each.
zombiedice-you-win = You win Zombie Dice with { $score } brains.
zombiedice-player-wins = { $player } wins Zombie Dice with { $score } brains.

zombiedice-error-roll-before-stopping = Roll once before stopping. After any safe roll, stopping at 0 brains is legal.
zombiedice-error-roll-resolving = The dice are still rolling.
zombiedice-error-target-score-range = The winning target must be from { $min } to { $max } brains; the current value is { $value }.

zombiedice-color-green = green
zombiedice-color-yellow = yellow
zombiedice-color-red = red
zombiedice-face-brain = brain
zombiedice-face-footprint = footprint
zombiedice-face-shotgun = shotgun
zombiedice-roll-result = { $color } { $face }
zombiedice-pool-color = { $count } { $color } { $count ->
    [one] die
   *[other] dice
}
zombiedice-no-dice = none

zombiedice-status-no-turn = No Zombie Dice turn is active.
zombiedice-your-turn-totals = You: { $brains } { $brains ->
    [one] brain
   *[other] brains
}, { $shotguns } { $shotguns ->
    [one] shotgun
   *[other] shotguns
}, and { $footprints } { $footprints ->
    [one] footprint
   *[other] footprints
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] brain
   *[other] brains
}, { $shotguns } { $shotguns ->
    [one] shotgun
   *[other] shotguns
}, and { $footprints } { $footprints ->
    [one] footprint
   *[other] footprints
}.
zombiedice-status-turn-you = Your turn — banked: { $score } { $score ->
    [one] brain
   *[other] brains
}.
zombiedice-status-turn-player = { $player }'s turn — banked: { $score } { $score ->
    [one] brain
   *[other] brains
}.
zombiedice-status-turn-totals = This turn: { $brains } { $brains ->
    [one] brain
   *[other] brains
}, { $shotguns } { $shotguns ->
    [one] shotgun
   *[other] shotguns
}, and { $footprints } { $footprints ->
    [one] footprint
   *[other] footprints
}.
zombiedice-status-cup = Cup: { $count } { $count ->
    [one] die
   *[other] dice
}.
zombiedice-status-footprints = Footprints to reroll: { $dice }.
zombiedice-status-brain-dice = Brain dice set aside: { $dice }.
zombiedice-status-shotgun-dice = Shotgun dice set aside: { $dice }.
zombiedice-status-last-roll = Last roll: { $results }.
zombiedice-status-awaiting-roll = No roll yet this turn.
zombiedice-status-table-header = Zombie Dice — round { $round }; target: { $target } brains.
zombiedice-status-table-header-tiebreak = Zombie Dice — target: { $target } brains.
zombiedice-status-main-round = Phase: main game.
zombiedice-status-final-round = Final round — { $player } reached the target.
zombiedice-status-tiebreak = Tiebreak { $round }: { $players }.
zombiedice-status-current-you = Your turn.
zombiedice-status-current-player = { $player }'s turn.
zombiedice-status-turn-order = Turn order: { $players }.
zombiedice-status-score-you = You: { $score } { $score ->
    [one] brain
   *[other] brains
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] brain
   *[other] brains
}.

zombiedice-score-unit-brains = { $count ->
    [one] brain
   *[other] brains
}
zombiedice-results-header = Zombie Dice results
zombiedice-results-winner = Winner: { $player } with { $score } brains.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] brain
   *[other] brains
}.
