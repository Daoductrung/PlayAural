game-name-dominos = Dominos

# Options
dominos-set-target-score = Target score: { $score }
dominos-enter-target-score = Enter target score
dominos-option-changed-target-score = Target score set to { $score }.

dominos-set-draw-mode = Mode: { $mode }
dominos-select-draw-mode = Select mode
dominos-option-changed-draw-mode = Mode set to { $mode }.

dominos-set-domino-set = Domino set: { $domino_set }
dominos-select-domino-set = Select domino set
dominos-option-changed-domino-set = Domino set changed to { $domino_set }.

dominos-set-spinner = Spinner: { $enabled }
dominos-option-changed-spinner = Spinner set to { $enabled }.

dominos-set-opening-rule = Opening rule: { $opening_rule }
dominos-select-opening-rule = Select opening rule
dominos-option-changed-opening-rule = Opening rule set to { $opening_rule }.

# Option choice labels
dominos-mode-draw = Draw
dominos-mode-block = Block

dominos-set-double6 = Double-6
dominos-set-double9 = Double-9

dominos-opening-highest-double = Highest double
dominos-opening-highest-tile = Highest tile
dominos-opening-set-max-double = Highest set double
dominos-opening-random-player = Random player
dominos-opening-round-winner = Previous round winner

# Actions
dominos-draw = Draw
dominos-knock = Knock
dominos-view-chain = View chain
dominos-read-ends = Read ends
dominos-read-hand = Read hand
dominos-read-counts = Read counts
dominos-play-tile = { $tile }
dominos-play-tile-at = Play { $tile } to { $side }
dominos-play-tile-multi = Play { $tile } to { $sides }
dominos-select-side = Select a side

# Board sides
dominos-side-left = left
dominos-side-right = right
dominos-side-up = up
dominos-side-down = down

# Validation and disabled reasons
dominos-draw-only-mode = Drawing is only available in Draw mode.
dominos-must-play = You already have a playable tile.
dominos-boneyard-empty = The boneyard is empty.
dominos-must-draw = You must draw before knocking.
dominos-illegal-side = That side is not legal for the selected tile.
dominos-no-play-for-tile = { $tile } cannot be played right now.
dominos-choose-side-keybind = Choose a side with the direction keybind. Legal sides: { $sides }.

# Gameplay
dominos-opening-play = { $player } opens with { $tile }.
dominos-opening-spinner = { $player } opens a spinner with { $tile }.
dominos-player-draws = { $player } draws { $count } { $count ->
    [one] tile
   *[other] tiles
}.
dominos-you-drew-single = You drew { $tile }.
dominos-you-drew-many = You drew { $count } tiles.
dominos-you-played = You played { $tile } to { $side }.
dominos-you-played-drawn = You drew and played { $tile } to { $side }.
dominos-player-played = { $player } played { $tile } to { $side }.
dominos-player-knocks = { $player } knocks.
dominos-round-won = { $player } wins the round and scores { $points } points.
dominos-round-blocked-tie = The round is blocked. Lowest pip total is { $pips }, but it is tied. No points are scored.
dominos-round-blocked-winner = The round is blocked. { $team } has the lowest pip total with { $pips } and scores { $points } points.
dominos-match-tied-continue = Multiple teams reached { $score } points. The game continues until the tie is broken.
dominos-match-winner = { $team } wins the game with { $score } points.

# Status boxes
dominos-chain-header = Chain
dominos-chain-empty = The chain is empty.
dominos-chain-center = Center: { $tile }
dominos-branch-empty = no tiles
dominos-chain-branch = { $side }: { $tiles }. Open end { $open_end }.
dominos-boneyard-count = Boneyard: { $count } tiles remaining.
dominos-end-info = { $side } { $value }

dominos-hand-header = Your hand
dominos-hand-line = { $tile } worth { $points } points.
dominos-hand-line-playable = { $tile } worth { $points } points. Playable on { $sides }.
dominos-hand-total = Total pips in hand: { $pips }.
dominos-player-count = { $player } has { $count } tiles
dominos-no-other-players = No other players.

# End screen
dominos-line-format = { $rank }. { $player }: { $points }
