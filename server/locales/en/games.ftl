game-round-start = Round { $round }.
game-round-end = Round { $round } complete.
game-turn-start = { $player }'s turn.
game-no-turn = No one's turn right now.

game-score-line = { $player }: { $score } points
game-score-line-target = { $player }: { $score }/{ $target } points
game-points = { $count } { $count ->
    [one] point
   *[other] points
}
game-final-scores-header = Final Scores:

game-winner = { $player } wins!
game-winner-score = { $player } wins with { $score } points!
game-tiebreaker = It's a tie! Tiebreaker round!
game-tiebreaker-players = It's a tie between { $players }! Tiebreaker round!
game-eliminated = { $player } has been eliminated with { $score } points.

game-set-target-score = Target score: { $score }
game-enter-target-score = Enter target score:
game-option-changed-target = Target score set to { $score }.

game-set-team-mode = Team mode: { $mode }
game-select-team-mode = Select team mode
game-option-changed-team = Team mode set to { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } teams of { $team_size }
game-team-name = Team { $index }

option-on = on
option-off = off

status-box-closed = Status information closed.

game-leave = Leave game

round-timer-paused = { $player } has paused the game (press p to start the next round).
round-timer-resumed = Round timer resumed.
round-timer-countdown = Next round in { $seconds }...

dice-keeping = Keeping { $value }.
dice-rerolling = Rerolling { $value }.
dice-locked = That die is locked and cannot be changed.
dice-status-label-locked = { $value } (locked)
dice-status-label-kept = { $value } (kept)

game-deal-counter = Deal { $current }/{ $total }.
game-you-deal = You deal out the cards.
game-player-deals = { $player } deals out the cards.

card-name = { $rank } of { $suit }
no-cards = No cards

suit-diamonds = diamonds
suit-clubs = clubs
suit-hearts = hearts
suit-spades = spades

rank-ace = ace
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = jack
rank-queen = queen
rank-king = king

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

game-error-invalid-team-mode = The selected team mode is not valid for the current number of players.

documentation-menu = Documentation
introduction = Introduction
community-rules = Community Rules
global-keys = Global Keybinds
game-rules = Game Rules
document-not-found = Document not found.
help = Help
