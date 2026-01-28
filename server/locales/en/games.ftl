# Shared game messages for PlayAural
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Round { $round }.
game-round-end = Round { $round } complete.
game-turn-start = { $player }'s turn.
game-no-turn = No one's turn right now.

# Score display
game-scores-header = Current Scores:
game-score-line = { $player }: { $score } points
game-points = { $count } { $count ->
    [one] point
   *[other] points
}
game-final-scores-header = Final Scores:

# Win/loss
game-winner = { $player } wins!
game-winner-score = { $player } wins with { $score } points!
game-tiebreaker = It's a tie! Tiebreaker round!
game-tiebreaker-players = It's a tie between { $players }! Tiebreaker round!
game-eliminated = { $player } has been eliminated with { $score } points.

# Common options
game-set-target-score = Target score: { $score }
game-enter-target-score = Enter target score:
game-option-changed-target = Target score set to { $score }.

game-set-team-mode = Team mode: { $mode }
game-select-team-mode = Select team mode
game-option-changed-team = Team mode set to { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } teams of { $team_size }
game-team-name = Team { $index }

# Boolean option values
option-on = on
option-off = off

# Status box
status-box-closed = Status information closed.

# Game end
game-leave = Leave game

# Round timer
round-timer-paused = { $player } has paused the game (press p to start the next round).
round-timer-resumed = Round timer resumed.
round-timer-countdown = Next round in { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Keeping { $value }.
dice-rerolling = Rerolling { $value }.
dice-locked = That die is locked and cannot be changed.
dice-status-label-locked = { $value } (locked)
dice-status-label-kept = { $value } (kept)

# Dealing (card games)
game-deal-counter = Deal { $current }/{ $total }.
game-you-deal = You deal out the cards.
game-player-deals = { $player } deals out the cards.

# Card names
card-name = { $rank } of { $suit }
no-cards = No cards

# Suit names
suit-diamonds = diamonds
suit-clubs = clubs
suit-hearts = hearts
suit-spades = spades

# Rank names
rank-ace = ace
rank-ace-plural = aces
rank-two = 2
rank-two-plural = 2s
rank-three = 3
rank-three-plural = 3s
rank-four = 4
rank-four-plural = 4s
rank-five = 5
rank-five-plural = 5s
rank-six = 6
rank-six-plural = 6s
rank-seven = 7
rank-seven-plural = 7s
rank-eight = 8
rank-eight-plural = 8s
rank-nine = 9
rank-nine-plural = 9s
rank-ten = 10
rank-ten-plural = 10s
rank-jack = jack
rank-jack-plural = jacks
rank-queen = queen
rank-queen-plural = queens
rank-king = king
rank-king-plural = kings

# Poker hand descriptions
poker-high-card-with = { $high } high, with { $rest }
poker-high-card = { $high } high
poker-pair-with = Pair of { $pair }, with { $rest }
poker-pair = Pair of { $pair }
poker-two-pair-with = Two Pair, { $high } and { $low }, with { $kicker }
poker-two-pair = Two Pair, { $high } and { $low }
poker-trips-with = Three of a Kind, { $trips }, with { $rest }
poker-trips = Three of a Kind, { $trips }
poker-straight-high = { $high } high Straight
poker-flush-high-with = { $high } high Flush, with { $rest }
poker-full-house = Full House, { $trips } over { $pair }
poker-quads-with = Four of a Kind, { $quads }, with { $kicker }
poker-quads = Four of a Kind, { $quads }
poker-straight-flush-high = { $high } high Straight Flush
poker-unknown-hand = Unknown hand

# Validation errors (common across games)
game-error-invalid-team-mode = The selected team mode is not valid for the current number of players.
