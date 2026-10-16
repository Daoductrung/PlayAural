game-name-pusoydos = Pusoy Dos

# =============================================================================
# =============================================================================


# =============================================================================
# Option labels and prompts
# =============================================================================

pusoydos-set-game-mode = Game Mode: { $choice }
pusoydos-select-game-mode = Select game mode:
pusoydos-option-changed-game-mode = Game mode set to { $choice }.
pusoydos-desc-game-mode = Elimination: win rounds to go out, last player is the loser. Losses: last-place finishers accumulate strikes, first to the limit loses. Points: round winner collects penalty points from losers, first to the target wins. Points Elimination: losers collect their own penalty points, hit the limit and you're out, last one standing wins.

pusoydos-mode-elimination = Elimination
pusoydos-mode-losses = Losses
pusoydos-mode-points = Points
pusoydos-mode-points-elimination = Points Elimination

pusoydos-set-rounds-to-win = Rounds to Win: { $count }
pusoydos-enter-rounds-to-win = Enter rounds needed to be eliminated (min: 1, max: 10):
pusoydos-option-changed-rounds-to-win = Rounds to win set to { $count }.
pusoydos-desc-rounds-to-win = Elimination mode only: how many rounds a player must win before leaving the game as a winner (default 2, range 1-10).

pusoydos-set-losses-to-lose = Losses to Lose: { $count }
pusoydos-enter-losses-to-lose = Enter losses needed to lose (min: 1, max: 10):
pusoydos-option-changed-losses-to-lose = Losses to lose set to { $count }.
pusoydos-desc-losses-to-lose = Losses mode only: how many last-place finishes a player can take before losing the game (default 3, range 1-10).

pusoydos-set-target-score = Target Score: { $score }
pusoydos-enter-target-score = Enter target score (min: 10, max: 10000):
pusoydos-option-changed-target-score = Target score set to { $score }.
pusoydos-desc-target-score = Points modes only: score threshold for winning in Points mode, or elimination in Points Elimination mode (default 100, range 10-10000).

pusoydos-set-turn-timer = Turn Timer: { $choice }
pusoydos-select-turn-timer = Select turn timer duration:
pusoydos-option-changed-turn-timer = Turn timer set to { $choice }.
pusoydos-desc-turn-timer = Per-turn time limit: Unlimited, 10, 15, 20, 30, 45, 60, or 90 seconds (default Unlimited).

pusoydos-timer-10 = 10 Seconds
pusoydos-timer-15 = 15 Seconds
pusoydos-timer-20 = 20 Seconds
pusoydos-timer-30 = 30 Seconds
pusoydos-timer-45 = 45 Seconds
pusoydos-timer-60 = 60 Seconds
pusoydos-timer-90 = 90 Seconds
pusoydos-timer-unlimited = Unlimited

pusoydos-set-allow-2-in-straights = Allow 2 in Straights: { $enabled }
pusoydos-option-changed-allow-2-in-straights = Allow 2 in straights set to { $enabled }.
pusoydos-desc-allow-2-in-straights = Whether the 2 can be used in straights (e.g. A-2-3-4-5).

pusoydos-set-instant-wins = Instant Wins: { $enabled }
pusoydos-option-changed-instant-wins = Instant wins set to { $enabled }.
pusoydos-desc-instant-wins = Whether special dealt hands (Dragon, Four 2s, Six Pairs) win the round instantly. This cannot be combined with card passing.

pusoydos-set-card-passing = Card Passing: { $choice }
pusoydos-select-card-passing = Select card passing mode:
pusoydos-option-changed-card-passing = Card passing set to { $choice }.
pusoydos-desc-card-passing = Card exchange between winners and losers after dealing: Off, Simple, or Full. Full passing requires exactly 2 or 4 players, and passing cannot be combined with instant wins.

pusoydos-passing-off = Off
pusoydos-passing-simple = Simple (1st and last swap 1 card)
pusoydos-passing-full = Full (1st/last swap 2, 2nd/3rd swap 1)

pusoydos-set-penalty-tier = Penalty Tier: { $choice }
pusoydos-select-penalty-tier = Select penalty tier:
pusoydos-option-changed-penalty-tier = Penalty tier set to { $choice }.
pusoydos-desc-penalty-tier = Points modes only: how aggressively remaining cards are penalized at the end of a round.

pusoydos-penalty-standard = Standard (10+ cards: x2, 13 cards: x3)
pusoydos-penalty-aggressive = Aggressive (8-9: x2, 10-12: x3, 13: x4)
pusoydos-penalty-flat = Flat (1 point per card, no multiplier)

pusoydos-set-penalty-per-two = Penalty per 2 Held: { $enabled }
pusoydos-option-changed-penalty-per-two = Penalty per 2 held set to { $enabled }.
pusoydos-desc-penalty-per-two = Points modes only: each 2 left in a losing hand doubles that hand's penalty.

# =============================================================================
# Game flow announcements
# =============================================================================


pusoydos-new-hand = Round { $round }.
pusoydos-dealt = Dealt { $count } cards: { $cards }.

pusoydos-you-first-player = You have the 3 of Clubs and go first.
pusoydos-first-player = { $player } has the 3 of Clubs and goes first.
pusoydos-you-first-player-lowest = You have the lowest card and go first.
pusoydos-first-player-lowest = { $player } has the lowest card and goes first.

# Elimination mode
pusoydos-you-eliminated = You win { $count } rounds and are out! Well played.
pusoydos-player-eliminated = { $player } wins { $count } rounds and is out! Well played.
pusoydos-you-last-player = You are the last player remaining. Game over!
pusoydos-last-player = { $player } is the last player remaining. Game over!
pusoydos-players-remaining = { $count } { $count ->
    [one] player
   *[other] players
} remaining.

# Losses mode
pusoydos-you-round-loser = You finish last and take a loss! ({ $count } { $count ->
    [one] loss
   *[other] losses
} total.)
pusoydos-round-loser = { $player } finishes last and takes a loss! ({ $count } { $count ->
    [one] loss
   *[other] losses
} total.)
pusoydos-you-losses-game-over = You reach { $count } losses and lose the game!
pusoydos-losses-game-over = { $player } reaches { $count } losses and loses the game!

# Points mode
pusoydos-penalty-entry = { $points } { $points ->
    [one] point
   *[other] points
} from { $player }
pusoydos-you-penalty-summary = You win the round: { $breakdown }. ({ $gained } this round, { $total } total.)
pusoydos-penalty-summary = { $player } wins the round: { $breakdown }. ({ $gained } this round, { $total } total.)
pusoydos-you-win-round = You win the round!
pusoydos-round-winner = { $player } wins the round!
pusoydos-you-go-out = You go out!
pusoydos-player-goes-out = { $player } goes out!
pusoydos-you-points-winner = You reach { $score } points and win the game!
pusoydos-points-winner = { $player } reaches { $score } points and wins the game!

# Points elimination mode
pusoydos-you-points-elim-penalty = You get { $points } points. ({ $total } total.)
pusoydos-points-elim-penalty = { $player } gets { $points } points. ({ $total } total.)
pusoydos-you-points-elim-eliminated = You reach { $score } points and are eliminated!
pusoydos-points-elim-eliminated = { $player } reaches { $score } points and is eliminated!
pusoydos-you-points-elim-winner = You are the last player standing. You win!
pusoydos-points-elim-winner = { $player } is the last player standing. { $player } wins!

# Instant wins
pusoydos-you-instant-win-dragon = You have a Dragon (13-card straight)! Instant win!
pusoydos-instant-win-dragon = { $player } has a Dragon (13-card straight)! Instant win!
pusoydos-you-instant-win-four-twos = You have all four 2s! Instant win!
pusoydos-instant-win-four-twos = { $player } has all four 2s! Instant win!
pusoydos-you-instant-win-six-pairs = You have six pairs! Instant win!
pusoydos-instant-win-six-pairs = { $player } has six pairs! Instant win!
pusoydos-checking-instant-wins = Checking for instant win hands...
pusoydos-no-instant-wins = No instant wins this round.

# Card passing
pusoydos-passing-phase = Card passing phase.
pusoydos-loser-gives = { $loser } gives { $count ->
    [one] { GENDER_TERM($loser_gender, "possessive-determiner") } highest card
   *[other] { GENDER_TERM($loser_gender, "possessive-determiner") } { $count } highest cards
} to { $winner }.
pusoydos-you-give-highest = You give { $count ->
    [one] your highest card
   *[other] your { $count } highest cards
} to { $winner }.
pusoydos-winner-gives-back = { $winner } gives { $count ->
    [one] a card
   *[other] { $count } cards
} back to { $loser }.
pusoydos-select-cards-to-give = Select { $count ->
    [one] 1 card
   *[other] { $count } cards
} to give back to { $recipient }:
pusoydos-cards-exchanged = Cards exchanged.
pusoydos-passed-cards = You gave { $cards } to { $recipient }.
pusoydos-received-cards = You received { $cards } from { $sender }.

# =============================================================================
# Card interaction and actions
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (selected)

pusoydos-play-none = Select cards to play.
pusoydos-play-invalid = Invalid combination.
pusoydos-play-combo = Play { $combo }

pusoydos-pass = Pass
pusoydos-check-trick = Check trick
pusoydos-read-hand = Read hand
pusoydos-check-turn-timer = Check turn timer
pusoydos-read-card-counts = Card counts
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] card
   *[other] cards
}
pusoydos-card-counts-empty = No active players have cards to count.
pusoydos-timer-disabled = The turn timer is disabled.
pusoydos-timer-remaining = { $seconds } seconds remaining.

# Keybind labels
pusoydos-key-play = Play selected cards
pusoydos-key-pass = Pass
pusoydos-key-trick = Check current trick
pusoydos-key-hand = Read your hand
pusoydos-key-counts = Card counts
pusoydos-key-timer = Turn timer

# =============================================================================
# Errors
# =============================================================================

pusoydos-error-full-passing-players = Full card passing requires exactly 2 or 4 players.
pusoydos-error-instant-wins-card-passing = Instant wins and card passing conflict. Disable one of them before starting the game.
pusoydos-error-no-cards = You have not selected any cards.
pusoydos-error-invalid-combo = The selected cards do not form a valid combination.
pusoydos-error-first-turn-3c = You must include the 3 of Clubs in the first play.
pusoydos-error-wrong-length = You must play exactly { $count } { $count ->
    [one] card
   *[other] cards
} to beat the current trick.
pusoydos-error-lower-combo = Your combination is lower than the current trick.
pusoydos-error-must-play = You cannot pass when starting a new trick.
pusoydos-error-select-cards-to-give = Select exactly { $count } { $count ->
    [one] card
   *[other] cards
} to give back to { $recipient }.
pusoydos-error-select-required-give-cards = Select the required number of cards before confirming the exchange.
pusoydos-error-eliminated = You are already out of this game.
pusoydos-confirm-pass = Use the pass action again to confirm.

# =============================================================================
# Broadcasts
# =============================================================================

pusoydos-you-play-single = You play { $card }.
pusoydos-player-plays-single = { $player } plays { $card }.
pusoydos-you-play-combo = You play a { $combo } of { $cards }.
pusoydos-player-plays-combo = { $player } plays a { $combo } of { $cards }.
pusoydos-you-pass = You pass.
pusoydos-player-passes = { $player } passes.
pusoydos-you-win-trick = You win the trick.
pusoydos-trick-won = { $player } wins the trick.

pusoydos-trick-empty = The trick is empty.
pusoydos-trick-status = { $player } played a { $combo } of { $cards }.
pusoydos-your-hand = Your hand: { $cards }.

pusoydos-score-no-scores = No scores yet.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] win
   *[other] wins
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] loss
   *[other] losses
}
pusoydos-score-points = { $player }: { $score } points

pusoydos-you-one-card = You have one card left!
pusoydos-one-card = { $player } has one card left!

# =============================================================================
# Combo names
# =============================================================================

pusoydos-combo-single = Single
pusoydos-combo-pair = Pair
pusoydos-combo-three_of_a_kind = Three of a Kind
pusoydos-combo-straight = Straight
pusoydos-combo-flush = Flush
pusoydos-combo-full_house = Full House
pusoydos-combo-four_of_a_kind = Four of a Kind
pusoydos-combo-straight_flush = Straight Flush

# Instant win hand names
pusoydos-combo-dragon = Dragon
pusoydos-combo-four_twos = Four 2s
pusoydos-combo-six_pairs = Six Pairs

# =============================================================================
# End screen
# =============================================================================

pusoydos-game-over = The game is over! { $player } lost!
pusoydos-game-over-points = The game is over! { $player } wins with { $score } points!
pusoydos-game-over-losses = The game is over! { $player } loses with { $count } losses!
pusoydos-line-format = { $rank }. { $player }: { $score } points
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] win
   *[other] wins
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] loss
   *[other] losses
}
