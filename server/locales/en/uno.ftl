game-name-uno = UNO

# Colors
uno-color-red = Red
uno-color-yellow = Yellow
uno-color-green = Green
uno-color-blue = Blue
uno-color-wild = Wild

# Card names
uno-card-number = { $color } { $value }
uno-card-skip = { $color } Skip
uno-card-reverse = { $color } Reverse
uno-card-draw-two = { $color } Draw Two
uno-card-wild = Wild
uno-card-wild-four = Wild Draw Four

# Options
uno-set-winning-score = Score limit: { $score }
uno-enter-winning-score = Enter score limit
uno-option-changed-winning-score = Score limit set to { $score }.
uno-desc-winning-score = Score limit used by the selected UNO scoring mode (default 300, range 10-2000).

uno-set-scoring-mode = Scoring: { $mode }
uno-select-scoring-mode = Select scoring mode
uno-option-changed-scoring-mode = Scoring set to { $mode }.
uno-desc-scoring-mode = Chooses whether the first player to reach the limit wins, or players at the limit are eliminated.
uno-scoring-first = First to limit wins
uno-scoring-elimination = Elimination

uno-set-skip-after-draw = Draw penalties skip turn: { $enabled }
uno-option-changed-skip-after-draw = Draw penalties skip turn { $enabled }.
uno-desc-skip-after-draw = Controls whether Draw Two and Wild Draw Four penalties also skip the target's turn.

uno-set-responses = Stacking responses: { $enabled }
uno-option-changed-responses = Stacking responses { $enabled }.
uno-desc-responses = Allows players to stack draw cards in response to Draw Two or Wild Draw Four penalties.

uno-set-advanced-responses = Advanced responses: { $enabled }
uno-option-changed-advanced-responses = Advanced responses { $enabled }.
uno-desc-advanced-responses = Allows extra defensive responses to draw stacks, such as matching Skip, Reverse, or Wild cards. Requires Stacking responses.

uno-set-wait-for-draw-responses = Wait for draw responses: { $enabled }
uno-option-changed-wait-for-draw-responses = Wait for draw responses { $enabled }.
uno-desc-wait-for-draw-responses = If the last card creates a draw stack, waits for the next player to respond or draw before scoring the round. Requires Stacking responses.

uno-set-bluff = Wild Draw Four challenges: { $enabled }
uno-option-changed-bluff = Wild Draw Four challenges { $enabled }.
uno-desc-bluff = Enables Wild Draw Four challenge rules for illegal plays.

uno-set-straights = Straights: { $enabled }
uno-option-changed-straights = Straights { $enabled }.
uno-desc-straights = Lets a player continue out of turn with the next or previous number of the same color after a number card.

uno-set-interceptions = Interceptions: { $enabled }
uno-option-changed-interceptions = Interceptions { $enabled }.
uno-desc-interceptions = Lets players jump in out of turn with an exact matching card. Invalid attempts add 3 penalty points.

uno-set-super-interceptions = Super interceptions: { $enabled }
uno-option-changed-super-interceptions = Super interceptions { $enabled }.
uno-desc-super-interceptions = Expands interceptions to match number or action symbol even when the color differs. Requires Interceptions.

uno-set-zero-seven = Zero / seven rule: { $enabled }
uno-option-changed-zero-seven = Zero / seven rule { $enabled }.
uno-desc-zero-seven-rule = Enables the house rule where 0 rotates everyone's hands and 7 lets the player swap hands or decline.

uno-set-free-draws = Free draws per turn: { $count }
uno-enter-free-draws = Enter free draws per turn
uno-option-changed-free-draws = Free draws per turn set to { $count }.
uno-desc-free-draws = How many times a human player may draw despite holding a playable card (default 0, range 0-999).

# Option validation
uno-error-advanced-responses-require-responses = Advanced responses require Stacking responses to be enabled.
uno-error-wait-responses-require-responses = Wait for draw responses requires Stacking responses to be enabled.
uno-error-super-interceptions-require-interceptions = Super interceptions require Interceptions to be enabled.

# Actions
uno-draw = Draw
uno-say-uno = UNO
uno-read-top = Read top card
uno-read-color = Read current color
uno-read-counts = Read card counts
uno-read-hand = Read your hand value
uno-sort-color = Sort by color
uno-sort-number = Sort by number

# Gameplay announcements
uno-new-hand = Round { $round }.
uno-start-card = { $player } turns up { $card }.
uno-you-start-card = You turn up { $card }.
uno-current-color = Current color: { $color }.
uno-dealt-cards = Everyone is dealt { $cards } cards.
uno-choose-opening-color-you = Choose the opening color.
uno-choose-opening-color-player = { $player } must choose the opening color.
uno-direction-reversed = The direction is reversed.
uno-player-plays = { $player } plays { $card }.
uno-you-play = You play { $card }.
uno-player-chooses-color = { $player } chooses { $color }.
uno-you-choose-color = You choose { $color }.
uno-player-draws-one = { $player } draws a card.
uno-player-draws-many = { $player } draws { $count } cards.
uno-you-draw-one = You draw a card.
uno-you-draw-many = You draw { $count } cards.
uno-cant-play = { $player } can't play.
uno-you-cant-play = You can't play.
uno-you-skipped = You are skipped.
uno-says-uno = { $player } says UNO!
uno-you-say-uno = You say UNO!
uno-callout = { $caller } calls out { $player } for not saying UNO! { $player } draws { $count } { $count ->
    [one] card
   *[other] cards
}.
uno-you-callout = You call out { $player } for not saying UNO! { $player } draws { $count } { $count ->
    [one] card
   *[other] cards
}.
uno-callout-you = { $caller } calls you out for not saying UNO! You draw { $count } { $count ->
    [one] card
   *[other] cards
}.
uno-error-already-said-uno = You have already said UNO.
uno-error-no-uno-call = No UNO call is available right now.
uno-cannot-play-that = You cannot play { $card }. { $reason }
uno-reshuffle = Reshuffling the discard pile.
uno-hand-blocked = No one can play. The round ends.
uno-error-choose-color-first = Choose a color for your Wild card before playing another card.
uno-error-wait-color-choice = Wait for the Wild card's player to choose a color before playing.
uno-error-wild-transition = Wait for the chosen color to take effect before playing another card.
uno-error-choose-swap-first = Choose a hand-swap target or decline before taking another action.
uno-error-wait-swap-choice = Wait for the seven hand-swap choice to finish before playing.
uno-error-wait-next-hand = Wait for the next round to begin before playing a card.
uno-error-wait-intro = Wait for the round setup to finish before playing a card.
uno-reason-draw-stack-response = There is a draw stack of { $count } { $count ->
    [one] card
   *[other] cards
} against you; play a valid response card or draw the penalty.
uno-reason-draw-stack-no-response = There is a draw penalty of { $count } { $count ->
    [one] card
   *[other] cards
} against you, and stacking responses are off; draw the penalty instead.
uno-reason-match-required = The top card is { $top }, and the active color is { $color }; match the color, match the number or action symbol, or play a Wild card.
uno-reason-card-not-available = That card is not available in the current state.

# Bluff challenge
uno-bluff-challenge = Challenge Wild Draw Four
uno-bluff-caught = { $player } played an illegal Wild Draw Four and draws { $count } cards!
uno-you-bluff-caught = You played an illegal Wild Draw Four and draw { $count } cards!
uno-bluff-wrong = { $player } challenged the Wild Draw Four incorrectly and draws { $count } cards!
uno-you-bluff-wrong = You challenged the Wild Draw Four incorrectly and draw { $count } cards!

# Zero / seven rule
uno-rotate-hands = Everyone passes their hand!
uno-swap-hands = { $player } swaps hands with { $target }!
uno-you-swap = You swap hands with { $target }!
uno-swap-with-you = { $player } swaps hands with you!
uno-swap-with = Swap hands with { $player }
uno-choose-swap = Choose a player to swap hands with, or decline.
uno-swap-none = Don't swap
uno-you-swap-none = You keep your hand.
uno-swap-none-other = { $player } keeps { GENDER_TERM($player_gender, "possessive-determiner") } hand.

# Interceptions / straights
uno-player-intercepts = { $player } intercepts with { $card }!
uno-you-intercept = You intercept with { $card }!
uno-bad-intercept = Invalid interception. { $points } penalty points.
uno-not-your-turn = It's not your turn.

# Info
uno-no-top = There is no top card yet.
uno-top-card = { $card }.
uno-color-is = { $color }.
uno-count-you = You { $count }
uno-count-player = { $player } { $count }
uno-deck-count = deck { $count }
uno-sorting-color = Sorting by color.
uno-sorting-number = Sorting by number.

# Round / game end
uno-round-winner = { $player } wins the round!
uno-you-win-round = You win the round!
uno-round-points-from = { $points } from { $player }
uno-round-points-from-you = { $points } from you
uno-round-points-from-with-interception = { $points } from { $player } ({ $hand_points } hand + { $penalty } interception penalty)
uno-round-points-from-you-with-interception = { $points } from you ({ $hand_points } hand + { $penalty } interception penalty)
uno-round-details-none = No points were taken from opponents.
uno-round-summary = { $details }. { $player } gains { $total }.
uno-round-summary-you = { $details }. You gain { $total }.
uno-you-add-penalty-points = You add { $points } penalty points to your total for this round.
uno-player-adds-penalty-points = { $player } adds { $points } penalty points to { GENDER_TERM($player_gender, "possessive-determiner") } total for this round.
uno-you-add-penalty-points-with-interception = You add { $points } penalty points to your total for this round ({ $hand_points } from your hand plus { $penalty } interception penalty).
uno-player-adds-penalty-points-with-interception = { $player } adds { $points } penalty points to { GENDER_TERM($player_gender, "possessive-determiner") } total for this round ({ $hand_points } from { GENDER_TERM($player_gender, "possessive-determiner") } hand plus { $penalty } interception penalty).
uno-you-are-eliminated = You have reached the { $limit }-point elimination limit and are out of the game.
uno-player-is-eliminated = { $player } has reached the { $limit }-point elimination limit and is out of the game.
uno-you-win-game =
    { $mode ->
        [elimination] You are the last player remaining and win with { $score } penalty points.
       *[first_to_limit] You win the game with { $score } points!
    }
uno-player-wins-game =
    { $mode ->
        [elimination] { $player } is the last player remaining and wins with { $score } penalty points.
       *[first_to_limit] { $player } wins the game with { $score } points!
    }
uno-game-tie = Everyone has been eliminated. The game is a tie!
uno-line-format = { $rank }. { $player }: { $score }
uno-score-line-first = { $player }: { $score }/{ $target } points.
uno-score-line-elimination = { $player }: { $score }/{ $target } penalty points.

# Hand value (d key)
uno-read-hand-value = { $count ->
    [one] { $count } card
   *[other] { $count } cards
 } worth { $points ->
    [one] { $points } point
   *[other] { $points } points
 }.
