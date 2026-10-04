game-name-scopa = Scopa

scopa-initial-table = Table cards: { $cards }
scopa-no-initial-table = No cards on the table to start.
scopa-you-capture = You capture { $cards } with { $card }.
scopa-player-captures = { $player } captures { $cards } with { $card }.
scopa-you-capture-scopa = You capture { $cards } with { $card } and score a scopa!
scopa-player-captures-scopa = { $player } captures { $cards } with { $card } and scores a scopa!
scopa-you-capture-clear = You capture { $cards } with { $card }, clearing the table.
scopa-player-captures-clear = { $player } captures { $cards } with { $card }, clearing the table.
scopa-you-put-down = You put down { $card }.
scopa-player-puts-down = { $player } puts down { $card }.
scopa-clear-table-suffix = , clearing the table.
scopa-you-get-remaining-cards = You get the remaining table cards: { $cards }.
scopa-player-gets-remaining-cards = { $player } gets the remaining table cards: { $cards }.
scopa-you-instant-win = You win immediately with a scopa!
scopa-your-team-instant-win = Your team wins immediately with a scopa!
scopa-instant-win = { $player } wins immediately with a scopa!
scopa-scoring-round = Scoring round...
scopa-you-most-cards = You score 1 point for most cards ({ $count } cards).
scopa-your-team-most-cards = Your team scores 1 point for most cards ({ $count } cards).
scopa-most-cards = { $player } scores 1 point for most cards ({ $count } cards).
scopa-most-cards-tie = Most cards is a tie - no point awarded.
scopa-you-most-diamonds = You score 1 point for most diamonds ({ $count } diamonds).
scopa-your-team-most-diamonds = Your team scores 1 point for most diamonds ({ $count } diamonds).
scopa-most-diamonds = { $player } scores 1 point for most diamonds ({ $count } diamonds).
scopa-most-diamonds-tie = Most diamonds is a tie - no point awarded.
scopa-you-seven-diamonds = You score 1 point for the 7 of diamonds.
scopa-your-team-seven-diamonds = Your team scores 1 point for the 7 of diamonds.
scopa-seven-diamonds = { $player } scores 1 point for the 7 of diamonds.
scopa-you-seven-diamonds-multi = You score 1 point for most 7 of diamonds ({ $count } x 7 of diamonds).
scopa-your-team-seven-diamonds-multi = Your team scores 1 point for most 7 of diamonds ({ $count } x 7 of diamonds).
scopa-seven-diamonds-multi = { $player } scores 1 point for most 7 of diamonds ({ $count } × 7 of diamonds).
scopa-seven-diamonds-tie = 7 of diamonds is a tie - no point awarded.
scopa-you-most-sevens = You score 1 point for most sevens ({ $count } sevens).
scopa-your-team-most-sevens = Your team scores 1 point for most sevens ({ $count } sevens).
scopa-most-sevens = { $player } scores 1 point for most sevens ({ $count } sevens).
scopa-most-sevens-tie = Most sevens is a tie - no point awarded.
scopa-you-primiera = You score 1 point for primiera ({ $score } points).
scopa-your-team-primiera = Your team scores 1 point for primiera ({ $score } points).
scopa-primiera = { $player } scores 1 point for primiera ({ $score } points).
scopa-primiera-tie = Primiera is a tie - no point awarded.
scopa-primiera-none = No one has captured cards in all four suits, so no primiera point is awarded.
scopa-you-napola = You score { $points } points for napola.
scopa-your-team-napola = Your team scores { $points } points for napola.
scopa-napola = { $player } scores { $points } points for napola.

scopa-manual-select-prompt = You must choose which cards to capture.

scopa-capture-option = Capture { $cards }

scopa-error-conflict-escoba-asso = Escoba and Asso Piglia Tutto cannot be enabled at the same time.
scopa-error-conflict-instant-inverse = Instant win on scopa cannot be enabled with inverse mode.
scopa-error-conflict-instant-no-scopas = Instant win on scopa cannot be enabled when scopas do not score.

scopa-score-line-target-pending = { $player }: { $score }/{ $target } { $unit } (+{ $round_score } pending Scopa { $pending_unit } this round)
scopa-score-line-pending = { $player }: { $score } { $unit } (+{ $round_score } pending Scopa { $pending_unit } this round)
scopa-target-tie-continue = Multiple sides are tied at { $score } { $score ->
    [one] point
   *[other] points
}, so Scopa continues past the target of { $target } { $target ->
    [one] point
   *[other] points
} until the tie is broken.
scopa-round-scores = Round scores:
scopa-round-score-line = { $player }: +{ $round_score } (total: { $total_score })
scopa-table-empty = There are no cards on the table.
scopa-no-such-card = No card at that position.
scopa-captured-count = You have captured { $count } cards

scopa-view-table = View table
scopa-view-captured = View captured
scopa-view-table-card = View table card { $index }
scopa-pause-timer = Pause timer

scopa-hint-match =  -> { $card }
scopa-hint-multi =  -> { $count } cards

scopa-enter-target-score = Enter target score (1-121)
scopa-desc-target-score = Score needed to win Scopa (default 11, range 1-121).
scopa-set-cards-per-deal = Cards per deal: { $cards }
scopa-enter-cards-per-deal = Enter cards per deal (1-10)
scopa-set-decks = Number of decks: { $decks }
scopa-enter-decks = Enter number of decks (1-6)
scopa-toggle-escoba = Escoba (sum to 15): { $enabled }
scopa-toggle-hints = Show capture hints: { $enabled }
scopa-set-mechanic = Scopa mechanic: { $mechanic }
scopa-select-mechanic = Select scopa mechanic
scopa-toggle-instant-win = Instant win on scopa: { $enabled }
scopa-desc-team-mode = Chooses individual play or fixed team sizes for Scopa.
scopa-toggle-team-scoring = Pool team cards for scoring: { $enabled }
scopa-toggle-inverse = Inverse mode (reach target = elimination): { $enabled }
scopa-toggle-manual = Manual capture selection: { $enabled }
scopa-toggle-asso = Asso piglia tutto (Ace takes all): { $enabled }
scopa-toggle-primiera = Traditional Primiera scoring: { $enabled }
scopa-toggle-napola = Napola (Diamond sequence): { $enabled }

scopa-option-changed-cards = Cards per deal set to { $cards }.
scopa-desc-cards-per-deal = How many cards each player receives per Scopa deal (default 3, range 1-10).
scopa-option-changed-decks = Number of decks set to { $decks }.
scopa-desc-number-of-decks = How many 40-card Scopa decks are shuffled together (default 1, range 1-6).
scopa-option-changed-escoba = Escoba { $enabled }.
scopa-desc-escoba = Switches captures to Escoba rules, where the played card and captured table cards must total 15.
scopa-option-changed-hints = Capture hints { $enabled }.
scopa-desc-show-capture-hints = Shows which table cards each hand card can capture.
scopa-option-changed-mechanic = Scopa mechanic set to { $mechanic }.
scopa-desc-scopa-mechanic = Chooses normal sweep scoring, no Scopa points, or Only Scopas scoring.
scopa-option-changed-instant = Instant win on scopa { $enabled }.
scopa-desc-instant-win-scopas = When enabled, a valid Scopa immediately wins the game. This cannot be combined with No Scopas or Inverse Scopa.
scopa-option-changed-team-scoring = Team card scoring { $enabled }.
scopa-desc-team-card-scoring = Controls whether teammates combine captured cards for end-of-round scoring. If disabled in a team game, each player's captures are evaluated separately and any points won are added to that player's team.
scopa-option-changed-inverse = Inverse mode { $enabled }.
scopa-desc-inverse-scopa = Inverts the goal so reaching the target score eliminates a player or team.
scopa-option-changed-manual = Manual capture selection { $enabled }.
scopa-desc-manual-selection = Lets players choose a capture combination manually when more than one legal capture exists.
scopa-option-changed-asso = Asso piglia tutto { $enabled }.
scopa-desc-asso-piglia-tutto = Enables Ace takes all: an Ace sweeps the table and scores a scopa unless another Ace is already present. This cannot be combined with Escoba.
scopa-option-changed-primiera = Traditional Primiera scoring { $enabled }.
scopa-desc-primiera-scoring = Enables traditional Primiera scoring; when off, the game uses the simpler Most Sevens variant.
scopa-option-changed-napola = Napola { $enabled }.
scopa-desc-napola = Awards bonus points for capturing a continuous Diamond sequence starting with the Ace.

scopa-mechanic-normal = Normal
scopa-mechanic-no_scopas = No Scopas
scopa-mechanic-only_scopas = Scopas Only

scopa-timer-not-active = The round timer is not active.

scopa-error-not-enough-cards = Not enough cards in { $decks } { $decks ->
    [one] deck
    *[other] decks
} for { $players } { $players ->
    [one] player
    *[other] players
} with { $cards_per_deal } cards each. (Need { $cards_per_deal } × { $players } = { $cards_needed } cards, but only have { $total_cards }.)

scopa-line-format = { $rank }. { $player }: { $points }
