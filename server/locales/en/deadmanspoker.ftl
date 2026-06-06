game-name-deadmanspoker = Dead Man's Poker

deadmanspoker-call = Call
deadmanspoker-match-all-in = Match all-in
deadmanspoker-fold = Fold
deadmanspoker-coward-fold = Coward's Fold
deadmanspoker-switch-card = Switch card
deadmanspoker-all-in = All-in
deadmanspoker-read-hand = Read hand
deadmanspoker-read-community-cards = Read community cards
deadmanspoker-read-hand-value = Read hand strength
deadmanspoker-read-table = Read table
deadmanspoker-read-card-counts = Read card counts
deadmanspoker-read-revolvers = Read revolvers

deadmanspoker-action-sequence-running = Wait for the current sequence to finish.
deadmanspoker-action-eliminated = You have been eliminated.
deadmanspoker-action-folded = You are out of this hand.
deadmanspoker-not-decision-phase = You cannot do that during this phase.
deadmanspoker-max-bullets = You already have the maximum number of bullets committed.
deadmanspoker-no-opponents = There is no opponent left in this hand.
deadmanspoker-already-matched-all-in = You have already matched the all-in.
deadmanspoker-coward-used = You have already used Coward's Fold this match.
deadmanspoker-coward-first-decision-only = Coward's Fold is only available on your first decision of a hand.
deadmanspoker-fold-first-decision-use-coward = Normal Fold is not available on your first decision with one bullet. Only Coward's Fold can leave at that point.
deadmanspoker-all-in-too-early = All-in is available only from betting round 2, after the first three community cards are revealed.
deadmanspoker-switch-not-now = You cannot switch a card right now.
deadmanspoker-switch-used = You have already switched a card this hand.
deadmanspoker-switch-too-late = It is too late to switch a card.
deadmanspoker-switch-no-cards = You do not have a private card to switch.
deadmanspoker-switch-no-deck = The deck does not have enough replacement cards.
deadmanspoker-switch-choice-missing = That replacement card is no longer available.

deadmanspoker-match-start = Dead Man's Poker begins. Every bullet on the table is a bet with your life behind it.
deadmanspoker-hand-start = Hand { $hand }. Each active player commits the first bullet.
deadmanspoker-hand-start-all-alive = Hand { $hand }. Everyone commits the first bullet.
deadmanspoker-hand-start-survivors = Hand { $hand }. Each survivor commits the first bullet.
deadmanspoker-community-arrives = Five community cards arrive face down.
deadmanspoker-your-hand = Your private cards: { $cards }.
deadmanspoker-hand-empty = Your hand is empty.
deadmanspoker-round-stage = Betting round { $round_stage }.
deadmanspoker-community-revealed = Community cards revealed: { $cards }. Table: { $table }.
deadmanspoker-you-call = You call and place { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
} on the table. Total committed: { $total }.
deadmanspoker-player-calls = { $player } calls and places { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
} on the table. Total committed: { $total }.
deadmanspoker-you-match-all-in = You match the all-in with { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
}. Total committed: { $total }.
deadmanspoker-player-matches-all-in = { $player } matches the all-in with { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
}. Total committed: { $total }.
deadmanspoker-you-all-in = You go all-in and place { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
} on the table. Total committed: { $total }.
deadmanspoker-player-all-in = { $player } goes all-in and places { $added ->
    [one] 1 bullet
   *[other] { $added } bullets
} on the table. Total committed: { $total }.
deadmanspoker-you-fold = You fold and must face the revolver with { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-player-folds = { $player } folds and must face the revolver with { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-you-coward-fold = You use Coward's Fold and face the revolver with 1 bullet.
deadmanspoker-player-coward-folds = { $player } uses Coward's Fold and faces the revolver with 1 bullet.
deadmanspoker-switch-select-card = Choose the private card to switch.
deadmanspoker-switch-card-option = Switch { $card }
deadmanspoker-switch-candidates = Replacement choices: { $cards }.
deadmanspoker-choose-switch-placeholder = Replacement { $index }
deadmanspoker-choose-switch-card = Choose { $card }
deadmanspoker-you-switch = You switch one private card and discard { $card }.
deadmanspoker-player-switches = { $player } switches one private card and discards { $card }.
deadmanspoker-your-private-reveal = You reveal { $cards }. Best hand: { $hand }.
deadmanspoker-private-reveal = { $player } reveals { $cards }. Best hand: { $hand }.
deadmanspoker-showdown-you-win = You win the showdown with { $hand }.
deadmanspoker-showdown-you-tie-win = You tie for the showdown win with { $players } using { $hand }.
deadmanspoker-showdown-winners = { $players } win the showdown with { $hand }.
deadmanspoker-showdown-tie-no-penalty = The showdown is a tie. No one faces the revolver this hand.
deadmanspoker-you-win-showdown-hand = You win the hand at showdown.
deadmanspoker-player-wins-showdown-hand = { $player } wins the hand at showdown.
deadmanspoker-you-win-hand = You win the hand uncontested.
deadmanspoker-hand-winner = { $player } wins the hand uncontested.
deadmanspoker-hand-no-winner = No one wins this hand.

deadmanspoker-roulette-start = Roulette begins for { $players }.
deadmanspoker-you-load-bullets = You load { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-load-bullets = { $player } loads { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-you-roulette-survived = Empty chamber. You survive after risking { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-roulette-survived = Empty chamber. { $player } survives after risking { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-you-eliminated = The gun fires. You are eliminated after risking { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-player-eliminated = The gun fires. { $player } is eliminated after risking { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
}.
deadmanspoker-you-win-game = You are the last survivor and win Dead Man's Poker.
deadmanspoker-player-wins = { $player } is the last survivor and wins Dead Man's Poker.
deadmanspoker-no-winner = No winner could be determined.
deadmanspoker-you-are-eliminated = You have been eliminated from this game.

deadmanspoker-table-hand = Hand { $hand }, betting round { $round_stage }.
deadmanspoker-table-community = Community: { $cards }. Hidden: { $hidden }.
deadmanspoker-community-status = Community cards: { $cards }. Hidden: { $hidden }.
deadmanspoker-table-turn = Current turn: { $player }.
deadmanspoker-table-no-turn = No player currently has the turn.
deadmanspoker-table-player = { $player }: { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
} committed, { $status }.
deadmanspoker-community-none = none revealed
deadmanspoker-hidden-community = { $count ->
    [one] 1 hidden card
   *[other] { $count } hidden cards
}
deadmanspoker-status-active = active
deadmanspoker-status-folded = folded
deadmanspoker-status-eliminated = eliminated
deadmanspoker-status-waiting = waiting

deadmanspoker-card-count-line = { $player }: { $count ->
    [one] 1 card
   *[other] { $count } cards
}.
deadmanspoker-card-count-eliminated = { $player }: eliminated.

deadmanspoker-revolvers-header = Revolver risk
deadmanspoker-revolver-status = { $player }: { $bullets ->
    [one] 1 bullet
   *[other] { $bullets } bullets
} committed; { $risk }.
deadmanspoker-revolver-eliminated = { $player }: eliminated.
deadmanspoker-risk-none = no current roulette risk
deadmanspoker-risk-normal = death chance { $bullets } in 8
deadmanspoker-risk-eight = 95 percent death chance, 5 percent God Save survival

deadmanspoker-results-header = Dead Man's Poker results
deadmanspoker-results-winner = Winner: { $player }.
deadmanspoker-results-survived = survived
deadmanspoker-results-eliminated = eliminated
deadmanspoker-results-line = { $player }: { $status }, hands won { $hands }, all-ins started { $allins }, roulette survivals { $survivals }, bullets risked { $bullets }.
