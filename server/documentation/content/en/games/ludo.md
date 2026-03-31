\*\*Ludo\*\*



Ludo is PlayAural's race game based on the familiar four-color cross-and-circle format. Each player controls four tokens, brings them out from the yard, moves them around the shared outer track, then guides them into a private home lane. The first player to finish all four tokens wins the game immediately.



\*\*Gameplay\*\*



Ludo supports 2 to 4 players. At the start of the game, each player is assigned one color in seating order: Red, Blue, Green, then Yellow. Every player begins with four tokens in their own yard.



On your turn, you first roll the die.



\* If no token can move with that roll, your turn ends automatically after the roll announcement.

\* If exactly one token can move, the game moves that token automatically.

\* If multiple tokens can move, the game prompts you to choose which token to move.



The score display tracks how many of each player's four tokens have already reached home, but this is still a single-race game rather than a multi-round match. As soon as one player gets all four tokens home, that player wins.



\*\*Movement Rules\*\*



\* \*\*Leaving the yard:\*\* A token can only leave the yard on a roll of 6. When that happens, it enters the board on that color's starting square.

\* \*\*Outer track:\*\* Once a token is on the board, it moves forward around the 52-square shared track according to the die roll. The track wraps around, so tokens can pass the starting side and continue toward home.

\* \*\*Home entry:\*\* Each color has its own entry point near the end of a full lap. When a token passes that entry point, it leaves the shared track and enters its private home lane.

\* \*\*Home lane:\*\* The home lane is 6 spaces long. A token can only move in the lane if the roll does not overshoot the end.

\* \*\*Finishing:\*\* A token that reaches the end of the home lane is marked as finished and no longer moves.



\*\*Safe Squares And Stacks\*\*



Certain squares are safe and cannot be used for captures. In this implementation, squares 9, 22, 35, and 48 are always safe.



The host can also enable an option that makes all four color starting squares safe. When that option is on, entering on a starting square is protected even if an opposing token is already there.



Tokens are allowed to stack on the same square. Stacking can happen with your own tokens, with opposing tokens on safe squares, or in other situations where no capture occurs.



\*\*Captures\*\*



If your token lands on an unsafe outer-track square occupied by an opponent, you capture that opponent's token and send it back to the yard.



If that square contains a stack of one opponent's tokens, you capture all of that opponent's tokens on the square at once. Your own tokens are never captured by your own move, even if you land on a square where your own tokens are already stacked.



Captures do not happen inside the home lane, and they do not happen on safe squares.



\*\*Rolling A 6\*\*



Rolling a 6 normally grants an extra turn after the move is resolved.



However, the host can limit how many 6s may be rolled consecutively in the same turn sequence. By default, the limit is 3.



If the limit is reached, the penalty is severe: all moves made during that turn sequence are undone, the extra-turn chain ends, and play passes to the next player. Setting the limit to 0 disables this penalty entirely.



\*\*Scoring\*\*



Ludo in PlayAural uses straightforward race scoring:



\* The first player to finish all four tokens wins the game.

\* During play, the score system tracks how many tokens each player has already brought home.

\* There are no round points, pip totals, or carry-over scores between races in the current implementation.



\*\*Customizable Options\*\*



The host can adjust the following options before the game starts:



\* \*\*Max Consecutive Sixes:\*\* The number of 6s a player may roll in a row before the rollback penalty applies. Default: 3. Range: 0 to 5. Setting it to 0 disables the penalty.

\* \*\*Safe Start Squares:\*\* When enabled, all color starting squares count as safe squares and cannot be used for captures. Default: On.



\*\*Keyboard Shortcuts\*\*



\* \*\*R:\*\* Roll the die.

\* \*\*1-4:\*\* Move token 1 through 4 when the game asks you to choose a token.

\* \*\*V:\*\* Read the full board status, including each player's color, finished-token count, and the location of every token.

\* \*\*T:\*\* Check whose turn it is.

\* \*\*S:\*\* Check the current score display.
