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
dominos-set-double12 = Double-12

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
dominos-open-with-tile = Open with { $tile }
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
dominos-opening-must-play = The round has not been opened yet. You must choose a tile to start the chain.
dominos-error-set-too-small = { $players } players cannot be dealt enough tiles from a Double-{ $selected_pip } set. Choose at least Double-{ $required_pip } for this table size.

# Gameplay
dominos-you-open-round = You lead this round. Choose any tile from your hand to open the chain.
dominos-player-opens-round = { $player } leads this round and is choosing the opening tile.
dominos-you-opened = You opened the round with { $tile }.
dominos-player-opened = { $player } opened the round with { $tile }.
dominos-you-opened-spinner = You opened the round with { $tile }, creating a four-way spinner.
dominos-player-opened-spinner = { $player } opened the round with { $tile }, creating a four-way spinner.
dominos-you-drew-single = You drew { $tile } from the boneyard.
dominos-you-drew-many = You drew { $count } tiles from the boneyard.
dominos-player-drew-single = { $player } drew 1 tile from the boneyard.
dominos-player-drew-many = { $player } drew { $count } tiles from the boneyard.
dominos-you-played = You played { $tile } on the { $side } branch.
dominos-you-played-drawn = You drew and played { $tile } on the { $side } branch.
dominos-player-played = { $player } played { $tile } on the { $side } branch.
dominos-you-knock = You knock because you have no legal tile to play.
dominos-player-knocks = { $player } knocks.
dominos-you-won-round = You emptied your hand and scored { $points } points from opposing tiles.
dominos-player-won-round = { $player } emptied their hand and scored { $points } points from opposing tiles.
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
dominos-hand-line-opening-playable = { $tile } worth { $points } points. You can use it to open this round.
dominos-hand-total = Total pips in hand: { $pips }.
dominos-player-count = { $player } has { $count } tiles
dominos-no-other-players = No other players.

# End screen
dominos-line-format = { $rank }. { $player }: { $points }
