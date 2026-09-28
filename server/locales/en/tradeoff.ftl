game-name-tradeoff = Tradeoff

tradeoff-round-start = Round { $round }.
tradeoff-iteration = Hand { $iteration } of 3.

tradeoff-you-rolled = You rolled: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = trading
tradeoff-trade-status-keeping = keeping
tradeoff-confirm-trades = Confirm trades ({ $count } dice)
tradeoff-keeping = Keeping { $value }.
tradeoff-trading = Trading { $value }.
tradeoff-you-traded = You traded { $count } dice into the pool: { $dice }.
tradeoff-player-traded = { $player } traded { $count } dice into the pool: { $dice }.
tradeoff-you-traded-brief = You traded { $count } dice.
tradeoff-player-traded-brief = { $player } traded { $count } dice.
tradeoff-you-traded-none = You kept all five dice from this hand, so you will not take from the pool this time.
tradeoff-player-traded-none = { $player } kept all five dice from this hand.

tradeoff-your-turn-take = Your turn to take a die from the pool.
tradeoff-take-die = Take a { $value } ({ $remaining } left)
tradeoff-you-take = You take a { $value }.
tradeoff-player-takes = { $player } takes a { $value }.

tradeoff-you-scored = You scored { $points } points with { $sets }.
tradeoff-player-scored = { $player } scored { $points } points with { $sets }.
tradeoff-you-scored-brief = You scored { $points } points this round.
tradeoff-player-scored-brief = { $player } scored { $points } points this round.
tradeoff-you-no-sets = You scored 0 points because your 15 dice did not form any scoring set.
tradeoff-no-sets = { $player } scored 0 points because { GENDER_TERM($player_gender, "possessive-determiner") } 15 dice did not form any scoring set.

tradeoff-set-triple = triple of { $value }s
tradeoff-set-group = group of { $value }s
tradeoff-set-mini-straight = mini straight { $low }-{ $high }
tradeoff-set-double-triple = double triple ({ $v1 }s and { $v2 }s)
tradeoff-set-straight = straight { $low }-{ $high }
tradeoff-set-double-group = double group ({ $v1 }s and { $v2 }s)
tradeoff-set-all-groups = all groups
tradeoff-set-all-triplets = all triplets

tradeoff-round-scores = Round { $round } scores:
tradeoff-round-scores-brief = Scores:
tradeoff-score-line = { $player }: +{ $round_points } (total: { $total })
tradeoff-score-line-brief = { $player}: +{ $round_points }, total { $total }.
tradeoff-leader = { $player } leads with { $score }.
tradeoff-leader-brief = Leader: { $player }, { $score }.

tradeoff-you-win = You win with { $score } points!
tradeoff-winner = { $player } wins with { $score } points!
tradeoff-you-tie-win = You tie for the win with { $players } at { $score } points!
tradeoff-winners-tie = It's a tie! { $players } tied with { $score } points!

tradeoff-view-hand = View your hand
tradeoff-view-pool = View the pool
tradeoff-view-players = View players
tradeoff-hand-state-empty = no kept dice yet
tradeoff-hand-empty = Your kept hand is empty. If you have just rolled, use the dice choices to decide what to keep before confirming trades.
tradeoff-hand-display = Your kept hand this round ({ $count } dice): { $dice }.
tradeoff-hand-display-with-roll = Your kept hand this round ({ $count } dice): { $dice }. Current roll: { $roll }. { $trade_count } dice are still marked for trading.
tradeoff-roll-die-status = position { $position}: { $value }, { $status }
tradeoff-die-count = { $value}: { $count }
tradeoff-pool-display = Pool ({ $count } dice): { $dice }.
tradeoff-pool-empty = The pool is empty.
tradeoff-player-info = { $player}: kept hand: { $hand }. Last traded: { $traded }.
tradeoff-player-info-no-trade = { $player}: kept hand: { $hand }. Last traded nothing.

tradeoff-not-trading-phase = You can only change or confirm trade choices while your newly rolled dice are waiting in the trading phase.
tradeoff-not-taking-phase = You can only take dice after every player has confirmed trades and the shared pool is open.
tradeoff-already-confirmed = You already confirmed this trade selection. Wait for the other players; if you traded dice, you will take from the pool when your turn comes.
tradeoff-no-die = There is no die available for that trade action.
tradeoff-no-die-position = Position { $position } is not available in your current roll.
tradeoff-no-rolled-dice = You do not currently have rolled dice waiting for trade choices.
tradeoff-no-more-takes = You already took back the same number of dice you traded in this hand.
tradeoff-not-in-pool = There is no { $value } in the shared pool right now. Choose one of the visible pool values instead.
tradeoff-not-your-take-turn = It is { $player }'s turn to take from the pool. Wait until your name is announced before choosing a die.
tradeoff-no-trading-die-value = You do not have a { $value } currently marked for trading.
tradeoff-no-kept-die-value = You do not have a kept { $value } to mark for trading.
tradeoff-value-trade-style-required = Shift+number trade controls are only used with the Dice values keeping style. Use the plain number keys by position, or change your personal dice keeping style.
tradeoff-use-plain-number-to-take = Use the plain number key, not Shift+number, to take a die from the pool.
tradeoff-no-dice-key-phase = Number keys are only used while choosing trades or taking dice from the pool.

tradeoff-set-target = Target score: { $score }
tradeoff-enter-target = Enter target score:
tradeoff-option-changed-target = Target score set to { $score }.
tradeoff-desc-target-score = The total score a player must reach or pass after a scoring round to win (default 60, range 30-500).
tradeoff-error-target-out-of-range = Target score { $score } is outside the allowed range of { $min } to { $max }.
