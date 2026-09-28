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

yahtzee-you-rolled = You rolled: { $dice }. { $remaining ->
    [0] Choose a scoring category.
   *[other] { $remaining } { $remaining ->
        [one] roll
       *[other] rolls
    } left.
}
yahtzee-player-rolled = { $player } rolled: { $dice }. { $remaining ->
    [0] { GENDER_TERM($player_gender, "subject-capitalized") } must choose a scoring category.
   *[other] { $remaining } { $remaining ->
        [one] roll
       *[other] rolls
    } left.
}
yahtzee-you-rolled-brief = You rolled: { $dice }.
yahtzee-player-rolled-brief = { $player } rolled: { $dice }.

yahtzee-you-scored = You scored { $points } { $points ->
    [one] point
   *[other] points
} in { $category }.
yahtzee-player-scored = { $player } scored { $points } { $points ->
    [one] point
   *[other] points
} in { $category }.
yahtzee-you-scored-brief = { $points } in { $category }.
yahtzee-player-scored-brief = { $player }: { $points } in { $category }.

yahtzee-you-bonus = Yahtzee bonus! +100 points
yahtzee-player-bonus = { $player } got a Yahtzee bonus! +100 points
yahtzee-you-bonus-brief = Yahtzee bonus, +100.
yahtzee-player-bonus-brief = { $player }: Yahtzee bonus, +100.

yahtzee-you-upper-bonus = Upper section bonus! +35 points ({ $total } in upper section)
yahtzee-player-upper-bonus = { $player } earned the upper section bonus! +35 points ({ $total } in upper section)
yahtzee-you-upper-bonus-brief = Upper bonus, +35.
yahtzee-player-upper-bonus-brief = { $player }: upper bonus, +35.
yahtzee-you-upper-bonus-missed = Upper section bonus missed. You scored { $total }; you needed { $needed } more.
yahtzee-player-upper-bonus-missed = { $player } missed the upper section bonus with { $total } in the upper section, { $needed } short.
yahtzee-you-upper-bonus-missed-brief = Upper bonus missed; { $needed } short.
yahtzee-player-upper-bonus-missed-brief = { $player }: upper bonus missed, { $needed } short.

yahtzee-check-scoresheet = Check scorecard
yahtzee-check-all-scorecards = Check scorecard for all players
yahtzee-select-scorecard-player = Choose a player's scorecard.
yahtzee-scorecard-no-players = No active players have scorecards in this game yet.
yahtzee-scorecard-player-unavailable = That player is no longer available to view. Open the scorecard list again and choose an active player.
yahtzee-view-dice = Check hand
yahtzee-your-dice = Your dice: { $dice }.
yahtzee-your-dice-kept = Your dice: { $dice }. Keeping: { $kept }.
yahtzee-current-dice = { $player }'s dice: { $dice }.
yahtzee-current-dice-kept = { $player }'s dice: { $dice }. Keeping: { $kept }.
yahtzee-not-rolled = The current player hasn't rolled yet.

yahtzee-scoresheet-header = { $player }'s Scorecard
yahtzee-scoresheet-upper = Upper Section:
yahtzee-scoresheet-lower = Lower Section:
yahtzee-scoresheet-upper-total-bonus = Upper total: { $total } (bonus: +35)
yahtzee-scoresheet-upper-total-needed = Upper total: { $total } ({ $needed } more for bonus)
yahtzee-scoresheet-yahtzee-bonus = Yahtzee bonuses: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = Total score: { $total }

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

yahtzee-you-win = You win with { $score } { $score ->
    [one] point
   *[other] points
}!
yahtzee-player-wins = { $player } wins with { $score } { $score ->
    [one] point
   *[other] points
}!
yahtzee-winners-tie = It's a tie! { $players } all scored { $score } points!

yahtzee-set-rounds = Number of games: { $rounds }
yahtzee-enter-rounds = Enter number of games (1-10):
yahtzee-option-changed-rounds = Number of games set to { $rounds }.
yahtzee-desc-num-games = How many complete Yahtzee scorecards are played before final totals are compared (default 1, range 1-10).

yahtzee-no-rolls-left = You have no rolls left; choose an open scoring category to finish your turn.
yahtzee-roll-first = Roll the dice before choosing a scoring category.
yahtzee-category-filled = That category already has a score. Choose a category that is still open on your scorecard.
yahtzee-joker-upper-required = Joker rule: because this Yahtzee shows { $face }, you must score the upper-section box for { $face } before any other category.
yahtzee-joker-lower-required = Joker rule: the upper-section box for { $face } is already filled, so you must choose an open lower-section category before using another upper-section box.
