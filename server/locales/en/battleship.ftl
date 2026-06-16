game-name-battleship = Battleship

# Options
battleship-set-grid-size = Combat zone: { $size }
battleship-select-grid-size = Select combat zone size
battleship-option-changed-grid-size = Combat zone set to { $size }.

battleship-set-placement-mode = Deployment: { $mode }
battleship-select-placement-mode = Select deployment mode
battleship-option-changed-placement-mode = Deployment mode set to { $mode }.

battleship-set-replay-on-hit = Extra salvo on hit: { $enabled }
battleship-option-changed-replay-on-hit = Extra salvo on hit set to { $enabled }.

battleship-set-turn-timer = Turn timer: { $seconds }
battleship-select-turn-timer = Select turn timer
battleship-option-changed-turn-timer = Turn timer set to { $seconds }.

# Option choice labels
battleship-grid-6x6 = 6 by 6
battleship-grid-8x8 = 8 by 8
battleship-grid-10x10 = 10 by 10
battleship-grid-12x12 = 12 by 12

battleship-placement-auto = Automatic
battleship-placement-manual = Manual

battleship-timer-off = Off
battleship-timer-30 = 30 seconds
battleship-timer-45 = 45 seconds
battleship-timer-60 = 60 seconds

# Setup validation
battleship-error-invalid-grid-size = Combat zone size { $size } is not supported.
battleship-error-grid-too-small = The { $size } by { $size } combat zone is too small for the full fleet. Use at least { $minimum } by { $minimum }.
battleship-error-invalid-placement-mode = Deployment mode { $mode } is not supported.
battleship-error-invalid-turn-timer = Turn timer { $seconds } is not supported.

# Ship names
battleship-ship-carrier = Carrier
battleship-ship-battleship = Battleship
battleship-ship-destroyer = Destroyer
battleship-ship-submarine = Submarine
battleship-ship-patrol = Patrol Boat
battleship-ship-unknown = Vessel

# Orientations
battleship-horizontal = Horizontal
battleship-vertical = Vertical

# Actions
battleship-orient-horizontal = Deploy Horizontal
battleship-orient-vertical = Deploy Vertical
battleship-orient-horizontal-at = Deploy { $ship } horizontally at { $coord }
battleship-orient-vertical-at = Deploy { $ship } vertically at { $coord }
battleship-toggle-view = Switch Grid
battleship-read-fleet = Fleet Status
battleship-read-enemy-fleet = Enemy Fleet Intel

# Deployment phase
battleship-deploy-start = Deployment phase. Position your { $ship }, { $size } sectors long. Select a coordinate, then choose bearing.
battleship-choose-orientation = Deploying { $ship } at { $coord }, { $size } sectors. Select bearing.
battleship-ship-placed = { $ship } deployed at { $coord }, bearing { $orientation }.
battleship-cannot-place = Cannot deploy { $ship } at { $coord } { $orientation }. Vessel does not fit or overlaps another ship.
battleship-place-next-ship = Next vessel: { $ship }, { $size } sectors.
battleship-deploy-done = Fleet deployed. Standing by for the enemy.
battleship-deploy-complete = Deployment complete.
battleship-select-cell-first = Select a coordinate on the grid first.
battleship-deploy-in-progress = Deployment still in progress.
battleship-deploy-status-header = Ship placement phase.
battleship-deploy-status-ready-self = You are ready.
battleship-deploy-status-ready-other = { $player } is ready.
battleship-deploy-status-not-ready-self = You are not ready yet.
battleship-deploy-status-not-ready-other = { $player } is not ready yet.

# Battle phase
battleship-battle-start = All ships in position. Commence firing!

# Hit — first-person (shooter), second-person (target), third-person (spectator)
battleship-hit-self = You fire on { $coord }. Direct hit!
battleship-hit-target = { $player } fires on your { $coord }. Direct hit!
battleship-hit-spectator = { $player } fires on { $target }'s { $coord }. Direct hit!

# Miss — first/second/third
battleship-miss-self = You fire on { $coord }. Missed.
battleship-miss-target = { $player } fires on your { $coord }. Missed.
battleship-miss-spectator = { $player } fires on { $target }'s { $coord }. Missed.

# Sunk — first/second/third
battleship-sunk-self = You sank the enemy { $ship }!
battleship-sunk-target = { $player } sank your { $ship }!
battleship-sunk-spectator = { $player } sank { $target }'s { $ship }!

# Victory — first/second/third
battleship-victory-self = You win! All enemy vessels have been sunk.
battleship-victory-target = { $player } wins! All your vessels have been sunk.
battleship-victory-spectator = { $player } wins! All of { $target }'s vessels have been sunk.

battleship-shot-in-flight = A shell is still in flight. Wait for the result before firing again.
battleship-not-your-turn = It is not your turn to fire. Wait for { $player } to choose a coordinate.
battleship-wait-for-turn = Wait for the next firing order before choosing a coordinate.
battleship-already-shot = You already fired on { $coord }. Choose an uncharted coordinate.
battleship-switch-to-shots = You are viewing your own waters, so firing is blocked. Press V to switch to the target grid.
battleship-timeout-fire = Time's up! Auto-firing on { $coord }.

# View toggle
battleship-view-own = Viewing your waters.
battleship-view-shots = Viewing target grid.

# Cell labels
battleship-cell-empty = { $coord }, open water.
battleship-cell-ship-placed = { $coord }, { $ship }.
battleship-cell-unknown = { $coord }, uncharted.
battleship-cell-hit = { $coord }, hit.
battleship-cell-sunk = { $coord }, { $ship }, sunk.
battleship-cell-miss = { $coord }, miss.
battleship-cell-own-ship = { $coord }, your { $ship }.
battleship-cell-own-hit = { $coord }, your { $ship }, hit.
battleship-cell-own-sunk = { $coord }, your { $ship }, sunk.
battleship-cell-own-miss = { $coord }, incoming miss.

# Fleet status
battleship-fleet-header = Your Fleet
battleship-status-intact = Battle-ready
battleship-status-damaged = Damaged ({ $hits } of { $size } hit)
battleship-status-sunk = Sunk

battleship-enemy-fleet-header = Enemy Fleet
battleship-enemy-fleet-summary = { $sunk } of { $total } enemy vessels sunk.
battleship-enemy-ship-sunk = { $ship } (size { $size }): Sunk

# End screen
battleship-winner-line = { $player } wins!
battleship-stats-line = { $player }: { $shots } shots fired, { $hits } hits, { $accuracy }% accuracy
