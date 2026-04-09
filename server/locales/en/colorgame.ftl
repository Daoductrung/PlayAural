game-name-colorgame = Color Game

colorgame-set-starting-bankroll = Starting bankroll: { $amount }
colorgame-enter-starting-bankroll = Enter starting bankroll:
colorgame-option-changed-starting-bankroll = Starting bankroll set to { $amount }.

colorgame-set-minimum-bet = Minimum bet: { $amount }
colorgame-enter-minimum-bet = Enter minimum bet:
colorgame-option-changed-minimum-bet = Minimum bet set to { $amount }.

colorgame-set-maximum-total-bet = Maximum total bet per round: { $amount }
colorgame-enter-maximum-total-bet = Enter the maximum total bet per round:
colorgame-option-changed-maximum-total-bet = Maximum total bet per round set to { $amount }.

colorgame-set-betting-timer = Betting timer: { $seconds } seconds
colorgame-enter-betting-timer = Enter betting timer in seconds:
colorgame-option-changed-betting-timer = Betting timer set to { $seconds } seconds.

colorgame-set-round-limit = Round limit: { $count }
colorgame-enter-round-limit = Enter round limit:
colorgame-option-changed-round-limit = Round limit set to { $count }.

colorgame-set-win-condition = Win condition: { $mode }
colorgame-select-win-condition = Select the win condition:
colorgame-option-changed-win-condition = Win condition set to { $mode }.
colorgame-win-condition-last-player = Last player standing
colorgame-win-condition-highest-bankroll = Highest bankroll at the round limit

colorgame-color-red = red
colorgame-color-blue = blue
colorgame-color-yellow = yellow
colorgame-color-green = green
colorgame-color-white = white
colorgame-color-orange = orange

colorgame-game-start = Color Game begins. Players: { $players }.
colorgame-round-start = Round { $round } of { $limit }. Betting is open for { $seconds } seconds.
colorgame-roll-result = The dice show { $colors }.
colorgame-player-locked-bets = { $player } locks in { $total } chips.
colorgame-player-sits-out = { $player } sits this round out.
colorgame-player-sat-out = { $player } sat out and remains on { $bankroll } chips.
colorgame-player-won = { $player } wins { $amount } chips and rises to { $bankroll }.
colorgame-player-even = { $player } breaks even and remains on { $bankroll } chips.
colorgame-player-lost = { $player } loses { $amount } chips and drops to { $bankroll }.

colorgame-set-bet-color = Set { $color } bet: { $amount }
colorgame-clear-bets = Clear bets
colorgame-confirm-bets = Lock bets ({ $total })
colorgame-confirm-sit-out = Lock no bet
colorgame-check-status = Check status
colorgame-check-bets = Check bets
colorgame-check-last-roll = Check last roll

colorgame-enter-bet-amount = Enter the bet amount for this color. Enter 0 to clear it.
colorgame-invalid-bet-amount = Enter a valid whole number bet.
colorgame-bet-below-minimum = Each color bet must be at least { $amount }.
colorgame-bet-exceeds-bankroll = Your total bets cannot exceed { $amount }.
colorgame-bet-updated = { $color } is now set to { $amount }. Total committed this round: { $total }.
colorgame-bets-cleared = All of your bets have been cleared.
colorgame-bankrupt = You are out of chips.
colorgame-bets-already-locked = Your bets are already locked for this round.
colorgame-no-bets-placed = You have not placed any bets.

colorgame-no-bets = no bet
colorgame-bet-entry = { $color } { $amount }
colorgame-bets-header = Current bets:
colorgame-bets-line = { $player }: { $bets }. Total { $total }. { $locked }.
colorgame-bets-open-status = Bets are still open
colorgame-bets-locked-status = Bets are locked

colorgame-last-roll-none = No roll has been recorded yet.
colorgame-last-roll-header = Last roll: { $colors }.
colorgame-last-roll-line = { $player }: { $bets }. Net { $net }. Bankroll { $bankroll }.

colorgame-status-betting = Betting phase. Round { $round } of { $limit }. { $seconds } seconds left. Win condition: { $win_mode }.
colorgame-status-rolling = The dice are rolling for round { $round } of { $limit }. Win condition: { $win_mode }.
colorgame-status-resolving = Round { $round } of { $limit } is resolving. Win condition: { $win_mode }.
colorgame-status-bankroll = Your bankroll is { $bankroll }. You have committed { $total } this round. Your cap this round is { $cap }.
colorgame-status-bet-lock = Your bet state: { $state }.
colorgame-status-leader = The current leader is { $player } with { $bankroll } chips.

colorgame-whose-turn-betting = Betting phase. All live players may act. { $seconds } seconds remain.
colorgame-whose-turn-rolling = The dice are rolling now.
colorgame-whose-turn-resolving = The round is resolving now.

colorgame-standings-header = Standings:
colorgame-standing-live = still in
colorgame-standing-bust = busted
colorgame-score-line = { $rank }. { $player }: { $bankroll } chips, { $profitable_rounds } profitable rounds, biggest win { $biggest_win }, { $status }.

colorgame-error-max-bet-too-small = Maximum total bet must be at least the minimum bet.
colorgame-error-max-bet-too-large = Maximum total bet cannot exceed the starting bankroll.
