game-name-backgammon = Backgammon

backgammon-set-match-length = Match length: { $points }
backgammon-enter-match-length = Enter the match length (1-25)
backgammon-option-changed-match-length = Match length set to { $points }.
backgammon-set-bot-strategy = Bot strategy: { $strategy }
backgammon-select-bot-strategy = Select a bot strategy
backgammon-option-changed-bot-strategy = Bot strategy set to { $strategy }.
backgammon-bot-simple = Simple
backgammon-bot-smart = Smart
backgammon-bot-random = Random

backgammon-roll-dice = Roll dice
backgammon-offer-double = Offer double
backgammon-accept-double = Accept double
backgammon-drop-double = Drop double
backgammon-undo-move = Undo last move
backgammon-read-board = Read board
backgammon-check-status = Check status
backgammon-check-pip = Check pip count
backgammon-check-cube = Check cube
backgammon-check-dice = Check dice

backgammon-opening-roll = Opening roll: { $red } rolls { $red_die }, { $white } rolls { $white_die }.
backgammon-opening-tie = Both players rolled { $die }. Rolling again.
backgammon-opening-winner = { $player } goes first with { $die1 } and { $die2 }.
backgammon-roll = { $player } rolls { $die1 } and { $die2 }.
backgammon-no-moves = { $player } has no legal moves.
backgammon-double-offered = { $player } offers a double to { $value }.
backgammon-double-accepted = { $player } accepts. The cube is now { $value }.
backgammon-double-dropped = { $player } drops the double.
backgammon-game-won = { $player } wins this game for { $points } point{ $points ->
    [one] {""}
   *[other] s
}.
backgammon-new-game = Starting game { $number }.
backgammon-crawford = Crawford game. The doubling cube is disabled this game.
backgammon-match-winner = { $player } wins the match.
backgammon-end-score = { $red } { $red_score }, { $white } { $white_score }. Match to { $match_length }.

backgammon-announcement-move = { $player } moves from { $source } to { $dest } using { $die }.
backgammon-announcement-hit = { $player } moves from { $source } to hit on { $dest } using { $die }.
backgammon-announcement-bear-off = { $player } bears off from { $source } using { $die }.
backgammon-move-undone = Move undone.

backgammon-move-label = Move { $source } to { $dest } using { $die }
backgammon-move-label-hit = Hit from { $source } to { $dest } using { $die }
backgammon-move-label-bear-off = Bear off from { $source } using { $die }

backgammon-bar = bar
backgammon-board-header = Backgammon board
backgammon-board-point = Point { $point }: { $state }.
backgammon-point-empty = empty
backgammon-point-occupied = { $player } { $count }

backgammon-status-line = { $red }: bar { $red_bar }, borne off { $red_off }. { $white }: bar { $white_bar }, borne off { $white_off }.
backgammon-pip-line = Pip count. { $red }: { $red_pip }. { $white }: { $white_pip }.
backgammon-cube-centered = centered
backgammon-cube-yes = available
backgammon-cube-no = unavailable
backgammon-cube-line = Cube at { $value }, owner: { $owner }. Doubling is { $can_double }.
backgammon-dice-line = Remaining dice: { $dice }.
backgammon-dice-none = No dice remain.
backgammon-score-line = Score: { $red } { $red_score }, { $white } { $white_score }. Match to { $match_length }.
backgammon-scores-header = Match score
backgammon-score-detail = { $player }: { $score }
backgammon-score-target = Target: { $points }
backgammon-turn-preroll = { $player } is up and has not rolled yet.
backgammon-waiting-for-double-response = { $player } offered a double. Waiting for { $responder }.

backgammon-cannot-roll = You cannot roll right now.
backgammon-cannot-double = You cannot offer a double right now.
backgammon-no-double-pending = There is no double to respond to.
backgammon-no-move-to-undo = There is no move to undo.
backgammon-illegal-move = That move is not legal.
