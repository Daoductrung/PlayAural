game-name-scopa = Scopa

scopa-initial-table = Table cards: { $cards }
scopa-no-initial-table = No cards on the table to start.
scopa-you-collect = You collect { $cards } with { $card }
scopa-player-collects = { $player } collects { $cards } with { $card }
scopa-you-put-down = You put down { $card }.
scopa-player-puts-down = { $player } puts down { $card }.
scopa-scopa-suffix =  - SCOPA!
scopa-clear-table-suffix = , clearing the table.
scopa-remaining-cards = { $player } gets the remaining table cards.
scopa-scoring-round = Scoring round...
scopa-most-cards = { $player } scores 1 point for most cards ({ $count } cards).
scopa-most-cards-tie = Most cards is a tie - no point awarded.
scopa-most-diamonds = { $player } scores 1 point for most diamonds ({ $count } diamonds).
scopa-most-diamonds-tie = Most diamonds is a tie - no point awarded.
scopa-seven-diamonds = { $player } scores 1 point for the 7 of diamonds.
scopa-seven-diamonds-multi = { $player } scores 1 point for most 7 of diamonds ({ $count } × 7 of diamonds).
scopa-seven-diamonds-tie = 7 of diamonds is a tie - no point awarded.
scopa-most-sevens = { $player } scores 1 point for most sevens ({ $count } sevens).
scopa-most-sevens-tie = Most sevens is a tie - no point awarded.
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
scopa-set-cards-per-deal = Cards per deal: { $cards }
scopa-enter-cards-per-deal = Enter cards per deal (1-10)
scopa-set-decks = Number of decks: { $decks }
scopa-enter-decks = Enter number of decks (1-6)
scopa-toggle-escoba = Escoba (sum to 15): { $enabled }
scopa-toggle-hints = Show capture hints: { $enabled }
scopa-set-mechanic = Scopa mechanic: { $mechanic }
scopa-select-mechanic = Select scopa mechanic
scopa-toggle-instant-win = Instant win on scopa: { $enabled }
scopa-toggle-team-scoring = Pool team cards for scoring: { $enabled }
scopa-toggle-inverse = Inverse mode (reach target = elimination): { $enabled }

scopa-option-changed-cards = Cards per deal set to { $cards }.
scopa-option-changed-decks = Number of decks set to { $decks }.
scopa-option-changed-escoba = Escoba { $enabled }.
scopa-option-changed-hints = Capture hints { $enabled }.
scopa-option-changed-mechanic = Scopa mechanic set to { $mechanic }.
scopa-option-changed-instant = Instant win on scopa { $enabled }.
scopa-option-changed-team-scoring = Team card scoring { $enabled }.
scopa-option-changed-inverse = Inverse mode { $enabled }.

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
