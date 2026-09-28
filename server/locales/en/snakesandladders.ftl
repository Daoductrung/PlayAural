game-name-snakesandladders = Snakes and Ladders
game-snakesandladders-desc = Race from the starting area to square 100. Climb ladders, slide down snakes, and be the first to reach the finish.

snakes-roll = Roll die
snakes-check-positions = Check positions

snakes-turn-start-you = Your turn. Your piece is in the starting area before square 1.
snakes-turn-start-other = { $player }'s turn. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } piece is in the starting area before square 1.
snakes-turn-you = Your turn. You are on square { $position }.
snakes-turn-other = { $player }'s turn. { GENDER_TERM($player_gender, "subject-be-capitalized") } on square { $position }.

snakes-roll-you = You roll { $roll }.
snakes-roll-other = { $player } rolls { $roll }.
snakes-enter-you = You move from the starting area onto square { $position }.
snakes-enter-other = { $player } moves from the starting area onto square { $position }.
snakes-enter-you-brief = You: square { $position }.
snakes-enter-other-brief = { $player }: square { $position }.
snakes-move-you = You move { $roll } squares from square { $start } to square { $position }.
snakes-move-other = { $player } moves { $roll } squares from square { $start } to square { $position }.
snakes-move-you-brief = You: square { $position }.
snakes-move-other-brief = { $player }: square { $position }.
snakes-bounce-you = From square { $start }, your roll of { $roll } passes square { $target }, so you bounce back from the finish to square { $position }.
snakes-bounce-other = From square { $start }, { $player } rolls { $roll }, passes square { $target }, and bounces back from the finish to square { $position }.
snakes-bounce-you-brief = You bounce back to square { $position }.
snakes-bounce-other-brief = { $player } bounces back to square { $position }.
snakes-restored-bounce-you = Your saved roll finishes by bouncing you back to square { $position }.
snakes-restored-bounce-other = { $player }'s saved roll finishes by bouncing { GENDER_TERM($player_gender, "object") } back to square { $position }.
snakes-exact-miss-you = You need { $needed } to reach square { $target }, but you rolled { $roll }, so you stay on square { $position }.
snakes-exact-miss-other = { $player } needs { $needed } to reach square { $target }, but rolls { $roll }, leaving { GENDER_TERM($player_gender, "object") } on square { $position }.
snakes-exact-miss-you-brief = You need { $needed }, rolled { $roll }, and stay on square { $position }.
snakes-exact-miss-other-brief = { $player } needs { $needed }, rolls { $roll }, and stays on square { $position }.
snakes-ladder-you = You land at the foot of a ladder on square { $start } and climb to square { $end }, gaining { $distance } squares.
snakes-ladder-other = { $player } lands at the foot of a ladder on square { $start } and climbs to square { $end }, gaining { $distance } squares.
snakes-ladder-you-brief = You climb from square { $start } to { $end }.
snakes-ladder-other-brief = { $player } climbs from square { $start } to { $end }.
snakes-snake-you = You land on a snake's head on square { $start } and slide to its tail on square { $end }, losing { $distance } squares.
snakes-snake-other = { $player } lands on a snake's head on square { $start } and slides to its tail on square { $end }, losing { $distance } squares.
snakes-snake-you-brief = You slide from square { $start } to { $end }.
snakes-snake-other-brief = { $player } slides from square { $start } to { $end }.
snakes-extra-turn-you = You rolled 6, so you take another turn from square { $position }.
snakes-extra-turn-other = { $player } rolled 6, earning { GENDER_TERM($player_gender, "object") } another turn from square { $position }.
snakes-win-you = You reach square { $position } and win the game!
snakes-win-other = { $player } reaches square { $position } and wins the game!

snakes-status-goal = Goal: square { $target }. Finish rule: { $rule }.
snakes-status-current-start = { $player }: starting area before square 1. Current turn.
snakes-status-player-start = { $player }: starting area before square 1.
snakes-status-current-position = { $player }: square { $position }, { $remaining } remaining. Current turn.
snakes-status-player-position = { $player }: square { $position }, { $remaining } remaining.
snakes-status-player-finished = { $player }: square { $position }, finished.

snakes-finish-bounce-back = Bounce back
snakes-finish-exact-stay = Exact roll; stay put after an overshoot
snakes-set-finish-rule = Finish rule: { $rule }
snakes-select-finish-rule = Select the finish rule
snakes-option-changed-finish-rule = Finish rule changed to { $rule }.
snakesandladders-desc-finish-rule = Chooses whether overshooting square 100 bounces backward or leaves the player waiting for an exact roll.
snakes-set-extra-turn-six = Extra turn on 6: { $enabled }
snakes-option-changed-extra-turn-six = Extra turn on 6 changed to { $enabled }.
snakesandladders-desc-extra-turn-on-six = Controls whether rolling a six grants another turn.

snakes-error-roll-not-playing = You can roll the die only after a Snakes and Ladders game has started.
snakes-error-roll-not-your-turn = You cannot roll yet because another player is taking their turn. Wait until the turn passes to you.
snakes-error-roll-resolving = Your previous die roll is still resolving. Wait for the movement, snake, or ladder sequence to finish before rolling again.
snakes-error-positions-not-playing = Positions are available only while a Snakes and Ladders game is in progress.
snakes-error-invalid-finish-rule = The selected finish rule, { $rule }, is not supported. Choose Bounce back or Exact roll; stay put after an overshoot.

snakes-end-score = { $rank }. { $player }: square { $position }
snakes-end-score-start = { $rank }. { $player }: starting area before square 1
