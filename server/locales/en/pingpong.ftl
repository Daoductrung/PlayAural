game-name-pingpong = Table Tennis

pingpong-intro = Table Tennis begins. First to 11 points wins a game, with a two-point lead required. The match is best of { $best_of }. For every ball, use the arrow matching the sound and press X; immediately afterward, use an arrow to choose the destination. To serve, choose a direction and press C.
pingpong-aim-left = Left direction
pingpong-aim-right = Right direction
pingpong-aim-center = Center direction
pingpong-serve-announcement = { $player } to serve.
pingpong-serve-ball = Serve the ball
pingpong-hit-ball = Return the ball
pingpong-read-position = Read your position and the ball
pingpong-read-match = Read match status

pingpong-your-serve = Your serve. Press C.
pingpong-player-serves = { $player } serves.
pingpong-press-c-to-serve = It is time to serve. Press C, not X.
pingpong-serve-between-points = You can only serve when the next point begins.
pingpong-waiting-for-serve = Waiting for { $player } to serve.
pingpong-waiting-for-return = Waiting for { $player } to return the ball.
pingpong-point-resetting = The next point is being prepared.
pingpong-error-not-player = Only an active player can hit the ball.
pingpong-edge-of-court = You are at the edge of your playing area.

pingpong-position-left = left
pingpong-position-center = center
pingpong-position-right = right
pingpong-position-close = close to the table
pingpong-position-middle = at middle distance
pingpong-position-far = far from the table
pingpong-position-summary = You are { $horizontal }.
pingpong-ball-status = The ball is heading { $side }, { $depth }. { $bounced ->
    [true] It has bounced.
   *[false] It has not bounced yet.
}

pingpong-point-won = You win the point against { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-player-wins-point = { $player } wins the point. Score: { $points } to { $opponent_points }.
pingpong-score-announcement = Score: { $first }, { $first_points }; { $second }, { $second_points }.
pingpong-point-lost-early = You hit before the ball bounced. Point to { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-point-lost-out-of-reach = The ball was out of your paddle's reach. Point to { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-point-lost-net = Your return hit the net. Point to { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-point-lost-late = You swung too late. Point to { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-point-lost-passed = The ball passed you. Point to { $opponent }. Score: { $your_points } to { $opponent_points }.
pingpong-game-won = { $player } wins the game { $winner_points } to { $loser_points } and now has { $games } game wins.
pingpong-you-win-match = You win the match with { $games } games. Longest rally: { $longest } returns.
pingpong-player-wins-match = { $player } wins the match with { $games } games. Longest rally: { $longest } returns.

pingpong-match-summary = Game { $game } of a best-of-{ $best_of } match. Current rally: { $rally } returns.
pingpong-player-score = { $player }: { $games } games, { $points } points.
pingpong-end-player-line = { $player }: { $games } games won.
pingpong-end-longest-rally = Longest rally: { $count } returns.

pingpong-best-of-one = One game
pingpong-best-of-three = Best of three
pingpong-best-of-five = Best of five
pingpong-best-of-seven = Best of seven
pingpong-set-best-of = Match length: { $format }
pingpong-select-best-of = Select the match length.
pingpong-option-changed-best-of = Match length set to { $format }.
pingpong-desc-best-of = Choose one game or a best-of-three, five, or seven match.

pingpong-pace-relaxed = Relaxed
pingpong-pace-standard = Standard
pingpong-pace-fast = Fast
pingpong-set-pace = Ball pace: { $pace }
pingpong-select-pace = Select the ball pace.
pingpong-option-changed-pace = Ball pace set to { $pace }.
pingpong-desc-pace = Controls how much time the receiving player has to track and return the ball.

pingpong-bot-easy = Easy
pingpong-bot-normal = Normal
pingpong-bot-hard = Hard
pingpong-set-bot-difficulty = Bot difficulty: { $difficulty }
pingpong-select-bot-difficulty = Select bot difficulty.
pingpong-option-changed-bot-difficulty = Bot difficulty set to { $difficulty }.
pingpong-desc-bot-difficulty = Controls bot movement, timing, and return accuracy.

pingpong-language-en = English
pingpong-language-es = Spanish
pingpong-language-pt = Portuguese
pingpong-language-vi = Vietnamese
pingpong-language-fa = Persian
pingpong-set-language = Table language: { $language }
pingpong-select-language = Select the table language.
pingpong-option-changed-language = Table language set to { $language }.
pingpong-desc-language = Sets every spoken game message and control at this table to English, Spanish, Portuguese, Vietnamese, or Persian.

pingpong-desc-team-mode = Choose official singles for two players or official doubles for two teams of two.
pingpong-error-singles-players = Singles requires exactly two active players; there are currently { $count }.
pingpong-error-doubles-players = Doubles requires exactly four active players; there are currently { $count }.
pingpong-error-best-of = The selected match length is invalid.
pingpong-error-pace = The selected ball pace is invalid.
pingpong-error-bot-difficulty = The selected bot difficulty is invalid.
pingpong-error-language = The selected table language is invalid.
