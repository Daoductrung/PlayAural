# Tradeoff game messages

# Game info
game-name-tradeoff = Tradeoff

# Round and iteration flow
tradeoff-round-start = Round { $round }.
tradeoff-iteration = Hand { $iteration } of 3.

# Phase 1: Trading
tradeoff-you-rolled = You rolled: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = trading
tradeoff-trade-status-keeping = keeping
tradeoff-confirm-trades = Confirm trades ({ $count } dice)
tradeoff-keeping = Keeping { $value }.
tradeoff-trading = Trading { $value }.
tradeoff-player-traded = { $player } traded: { $dice }.
tradeoff-player-traded-none = { $player } kept all dice.

# Phase 2: Taking from pool
tradeoff-your-turn-take = Your turn to take a die from the pool.
tradeoff-take-die = Take a { $value } ({ $remaining } left)
tradeoff-you-take = You take a { $value }.
tradeoff-player-takes = { $player } takes a { $value }.

# Phase 3: Scoring
tradeoff-player-scored = { $player } ({ $points } pts): { $sets }.
tradeoff-no-sets = { $player }: no sets.

# Set descriptions (concise)
tradeoff-set-triple = triple of { $value }s
tradeoff-set-group = group of { $value }s
tradeoff-set-mini-straight = mini straight { $low }-{ $high }
tradeoff-set-double-triple = double triple ({ $v1 }s and { $v2 }s)
tradeoff-set-straight = straight { $low }-{ $high }
tradeoff-set-double-group = double group ({ $v1 }s and { $v2 }s)
tradeoff-set-all-groups = all groups
tradeoff-set-all-triplets = all triplets

# Round end
tradeoff-round-scores = Round { $round } scores:
tradeoff-score-line = { $player }: +{ $round_points } (total: { $total })
tradeoff-leader = { $player } leads with { $score }.

# Game end
tradeoff-winner = { $player } wins with { $score } points!
tradeoff-winners-tie = It's a tie! { $players } tied with { $score } points!

# Status checks
tradeoff-view-hand = View your hand
tradeoff-view-pool = View the pool
tradeoff-view-players = View players
tradeoff-hand-display = Your hand ({ $count } dice): { $dice }
tradeoff-pool-display = Pool ({ $count } dice): { $dice }
tradeoff-player-info = { $player }: { $hand }. Traded: { $traded }.
tradeoff-player-info-no-trade = { $player }: { $hand }. Traded nothing.

# Error messages
tradeoff-not-trading-phase = Not in the trading phase.
tradeoff-not-taking-phase = Not in the taking phase.
tradeoff-already-confirmed = Already confirmed.
tradeoff-no-die = No die to toggle.
tradeoff-no-more-takes = No more takes available.
tradeoff-not-in-pool = That die is not in the pool.

# Options
tradeoff-set-target = Target score: { $score }
tradeoff-enter-target = Enter target score:
tradeoff-option-changed-target = Target score set to { $score }.
