game-name-yahtzee = Yahtzee

yahtzee-roll = Re-roll ({ $count } left)
yahtzee-roll-all = Roll dice

yahtzee-score-ones = Ones for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-twos = Twos for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-threes = Threes for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-fours = Fours for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-fives = Fives for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-sixes = Sixes for { $points } { $points ->
    [one] point
   *[other] points
}

yahtzee-score-three-kind = Three of a Kind for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-four-kind = Four of a Kind for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-full-house = Full House for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-small-straight = Small Straight for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-large-straight = Large Straight for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-yahtzee = Yahtzee for { $points } { $points ->
    [one] point
   *[other] points
}
yahtzee-score-chance = Chance for { $points } { $points ->
    [one] point
   *[other] points
}

yahtzee-you-rolled = You rolled: { $dice }. Rolls remaining: { $remaining }
yahtzee-player-rolled = { $player } rolled: { $dice }. Rolls remaining: { $remaining }

yahtzee-you-scored = You scored { $points } { $points ->
    [one] point
   *[other] points
} in { $category }.
yahtzee-player-scored = { $player } scored { $points } { $points ->
    [one] point
   *[other] points
} in { $category }.

yahtzee-you-bonus = Yahtzee bonus! +100 points
yahtzee-player-bonus = { $player } got a Yahtzee bonus! +100 points

yahtzee-you-upper-bonus = Upper section bonus! +35 points ({ $total } in upper section)
yahtzee-player-upper-bonus = { $player } earned the upper section bonus! +35 points
yahtzee-you-upper-bonus-missed = You missed the upper section bonus ({ $total } in upper section, needed 63).
yahtzee-player-upper-bonus-missed = { $player } missed the upper section bonus.

yahtzee-choose-category = Choose a category to score in.
yahtzee-continuing = Continuing turn.

yahtzee-check-scoresheet = Check scorecard
yahtzee-view-dice = Check hand
yahtzee-your-dice = Your dice: { $dice }.
yahtzee-your-dice-kept = Your dice: { $dice }. Keeping: { $kept }
yahtzee-not-rolled = You haven't rolled yet.

yahtzee-scoresheet-header = === { $player }'s Scorecard ===
yahtzee-scoresheet-upper = Upper Section:
yahtzee-scoresheet-lower = Lower Section:
yahtzee-scoresheet-category-filled = { $category }: { $points }
yahtzee-scoresheet-category-open = { $category }: -
yahtzee-scoresheet-upper-total-bonus = Upper Total: { $total } (BONUS: +35)
yahtzee-scoresheet-upper-total-needed = Upper Total: { $total } ({ $needed } more for bonus)
yahtzee-scoresheet-yahtzee-bonus = Yahtzee Bonuses: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = TOTAL SCORE: { $total }

yahtzee-category-ones = Ones
yahtzee-category-twos = Twos
yahtzee-category-threes = Threes
yahtzee-category-fours = Fours
yahtzee-category-fives = Fives
yahtzee-category-sixes = Sixes
yahtzee-category-three-kind = Three of a Kind
yahtzee-category-four-kind = Four of a Kind
yahtzee-category-full-house = Full House
yahtzee-category-small-straight = Small Straight
yahtzee-category-large-straight = Large Straight
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Chance

yahtzee-winner = { $player } wins with { $score } { $score ->
    [one] point
   *[other] points
}!
yahtzee-winners-tie = It's a tie! { $players } all scored { $score } points!

yahtzee-set-rounds = Number of games: { $rounds }
yahtzee-enter-rounds = Enter number of games (1-10):
yahtzee-option-changed-rounds = Number of games set to { $rounds }.

yahtzee-no-rolls-left = You have no rolls left.
yahtzee-roll-first = You need to roll first.
yahtzee-category-filled = That category is already filled.
