game-name-chess = Chess

chess-set-time-control = Time control: { $control }
chess-select-time-control = Choose a time control
chess-option-changed-time-control = Time control set to { $control }.
chess-desc-time-control = Chooses the chess clock, from untimed play to bullet, blitz, rapid, or classical controls.
chess-time-untimed = Untimed
chess-time-bullet-1-0 = Bullet 1+0
chess-time-bullet-2-1 = Bullet 2+1
chess-time-blitz-3-0 = Blitz 3+0
chess-time-blitz-3-2 = Blitz 3+2
chess-time-blitz-5-0 = Blitz 5+0
chess-time-rapid-10-0 = Rapid 10+0
chess-time-rapid-10-5 = Rapid 10+5
chess-time-classical-30-0 = Classical 30+0

chess-set-draw-handling = Draw handling: { $mode }
chess-select-draw-handling = Choose draw handling
chess-option-changed-draw-handling = Draw handling set to { $mode }.
chess-desc-draw-handling = Chooses whether automatic draw rules end the game immediately or require a player to claim the draw.
chess-draw-handling-automatic = Automatic
chess-draw-handling-claim-required = Claim required

chess-toggle-draw-offers = Allow draw offers: { $enabled }
chess-option-changed-draw-offers = Allow draw offers set to { $enabled }.
chess-desc-allow-draw-offers = Controls whether players may offer and respond to agreed draws.
chess-toggle-undo-requests = Allow undo requests: { $enabled }
chess-option-changed-undo-requests = Allow undo requests set to { $enabled }.
chess-desc-allow-undo-requests = Controls whether players may request takebacks that the opponent can accept or decline.
chess-error-invalid-time-control = The selected time control "{ $control }" is not supported for Chess.
chess-error-invalid-draw-handling = The selected draw handling mode "{ $mode }" is not supported for Chess.

chess-read-board = Read board
chess-check-status = Check status
chess-flip-board = Flip board
chess-check-clock = Check clock
chess-claim-draw = Claim draw
chess-offer-draw = Offer draw
chess-accept-draw = Accept draw
chess-decline-draw = Decline draw
chess-request-undo = Request undo
chess-accept-undo = Accept undo
chess-decline-undo = Decline undo
chess-type-move = Type move
chess-enter-move = Type your move, such as e2e4, Nf3, O-O, or e8=Q

chess-promote-queen = Promote to queen
chess-promote-rook = Promote to rook
chess-promote-bishop = Promote to bishop
chess-promote-knight = Promote to knight

chess-color-white = white
chess-color-black = black

chess-piece-pawn = pawn
chess-piece-knight = knight
chess-piece-bishop = bishop
chess-piece-rook = rook
chess-piece-queen = queen
chess-piece-king = king
chess-piece-with-color = { $color } { $piece }

chess-square-empty-label = { $square }, empty
chess-square-piece-label = { $square }, { $piece }
chess-square-selected-label = selected, { $label }
chess-square-move-target = { $square }, legal move
chess-square-capture-target = { $square }, capture { $piece }
chess-square-empty = { $square } is empty.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = Select one of your own pieces first.
chess-piece-no-legal-moves = That piece has no legal moves.
chess-piece-selected = Selected { $piece } on { $square }. { $count } legal moves available.
chess-selection-cleared = Selection cleared.
chess-illegal-move = Illegal move.
chess-invalid-castle = Castling is not legal there.
chess-promotion-pending = Choose a piece for promotion first.
chess-choose-promotion = Choose a promotion piece.
chess-typed-move-empty = Type a move before submitting.
chess-typed-move-parse-error = I could not understand "{ $move }" as a chess move. Try coordinate notation like e2e4, algebraic notation like Nf3, castling like O-O, or promotion like e8=Q.
chess-typed-move-ambiguous = "{ $move }" matches more than one legal move. Add the starting file, rank, or full starting square, such as Nbd2 or Rae1.
chess-typed-move-illegal = "{ $move }" is not legal in the current position.
chess-typed-move-bad-promotion = "{ $move }" includes a promotion piece, but promotion only works when one of your pawns reaches the final rank. Use queen, rook, bishop, or knight.

chess-game-started = Chess begins. { $white } has white. { $black } has black.
chess-you-win-checkmate = Checkmate. You win.
chess-player-wins-checkmate = Checkmate. { $player } wins.
chess-draw = Draw.
chess-draw-stalemate = Draw by stalemate.
chess-draw-fifty-move = Draw by the fifty-move rule.
chess-draw-seventy-five-move = Draw by the mandatory seventy-five-move rule.
chess-draw-threefold = Draw by threefold repetition.
chess-draw-fivefold = Draw by mandatory fivefold repetition.
chess-draw-insufficient-material = Draw by insufficient material.
chess-draw-agreement = Draw by agreement.
chess-draw-timeout-insufficient = Draw. The opponent flagged, but there was not enough mating material.
chess-you-are-in-check = Your king is in check.
chess-player-is-in-check = { $player }'s king is in check.
chess-you-lose-on-time = You run out of time. { $winner } wins on time.
chess-player-loses-on-time = { $player } runs out of time. { $winner } wins on time.

chess-you-en-passant = You move your { $piece } from { $from_square } to { $to_square } and capture en passant.
chess-player-en-passant = { $player } moves { GENDER_TERM($player_gender, "possessive-determiner") } { $piece } from { $from_square } to { $to_square } and captures en passant.
chess-you-en-passant-brief = You { $from_square } x { $to_square } e.p.
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } e.p.
chess-you-capture = You move your { $piece } from { $from_square } to { $to_square }, capturing the { $captured_piece }.
chess-player-captures = { $player } moves { GENDER_TERM($player_gender, "possessive-determiner") } { $piece } from { $from_square } to { $to_square }, capturing the { $captured_piece }.
chess-you-capture-brief = You { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = You castle kingside.
chess-player-castles-kingside = { $player } castles kingside.
chess-you-castle-kingside-brief = You O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = You castle queenside.
chess-player-castles-queenside = { $player } castles queenside.
chess-you-castle-queenside-brief = You O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = You move your { $piece } from { $from_square } to { $to_square }.
chess-player-moves = { $player } moves { GENDER_TERM($player_gender, "possessive-determiner") } { $piece } from { $from_square } to { $to_square }.
chess-you-move-brief = You { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = You promote on { $square }.
chess-player-promotes = { $player } promotes on { $square }.
chess-you-promote-to = You promote the pawn on { $square } to a { $piece }.
chess-player-promotes-to = { $player } promotes the pawn on { $square } to a { $piece }.
chess-you-promote-to-brief = You promote { $square } to { $piece }.
chess-player-promotes-to-brief = { $player } promotes { $square } to { $piece }.
chess-you-offer-draw = You offer a draw.
chess-player-offers-draw = { $player } offers a draw.
chess-you-accept-draw = You accept the draw.
chess-player-accepts-draw = { $player } accepts the draw.
chess-you-decline-draw = You decline the draw.
chess-player-declines-draw = { $player } declines the draw.
chess-you-request-undo = You request an undo.
chess-player-requests-undo = { $player } requests an undo.
chess-you-accept-undo = You accept the undo request.
chess-player-accepts-undo = { $player } accepts the undo request.
chess-you-decline-undo = You decline the undo request.
chess-player-declines-undo = { $player } declines the undo request.
chess-draw-offer-too-early = Draw offers are available only after both players have made at least one move.
chess-claim-available-fifty-move = The fifty-move draw can be claimed now.
chess-claim-available-threefold = A draw by threefold repetition can be claimed now.
chess-you-claim-draw-fifty-move = You claim a draw by the fifty-move rule.
chess-draw-claimed-fifty-move = { $player } claims a draw by the fifty-move rule.
chess-you-claim-draw-threefold = You claim a draw by threefold repetition.
chess-draw-claimed-threefold = { $player } claims a draw by threefold repetition.

chess-status-white = White: { $player }
chess-status-black = Black: { $player }
chess-status-turn = Turn: { $color } ({ $player })
chess-status-move-count = Completed full moves: { $count }. Half-moves played: { $plies }.
chess-status-promotion-pending = A promotion choice is pending.
chess-status-check = The side to move is in check.
chess-status-time-control = Time control: { $control }
chess-status-draw-offer = Draw offer waiting from { $player }.
chess-status-undo-request = Undo request waiting from { $player }.
chess-clock-line = { $color } clock: { $time }
chess-clock-untimed = unlimited
chess-clock-announcement = White { $white }. Black { $black }.
chess-clock-announcement-untimed = This game is untimed.

chess-board-flipped = Board flipped to the { $color } side.
chess-empty = empty
chess-board-rank-line = Rank { $rank }: { $pieces }

chess-end-winner = { $player } wins as { $color }.
chess-end-move-count = Completed full moves: { $count }. Half-moves played: { $plies }.
