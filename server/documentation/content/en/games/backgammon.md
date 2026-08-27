\*\*Backgammon\*\*

Backgammon is a race for exactly two players. Each player controls fifteen checkers on a board of twenty-four numbered points. Your goal is to move every checker into your home board and then bear all fifteen off before your opponent does.

PlayAural assigns one player Red and the other White. The colors keep the same checkers throughout a match, but both players hear point numbers from their own direction of travel.

\*\*The Board\*\*

The board is a track folded into two rows. It contains:

\* \*\*24 points:\*\* The spaces where checkers rest. From your perspective, point 24 is farthest from home and point 1 is closest to bearing off.
\* \*\*Your home board:\*\* Points 1 through 6. All fifteen of your checkers must reach these six points before you may bear off.
\* \*\*The bar:\*\* The divider in the middle of a physical board. A checker that is hit waits here until it can re-enter.
\* \*\*Off the board:\*\* The destination for checkers you have successfully borne off.

The accessible board is a stable two-by-twelve grid. Your home board is at the bottom-right. The bottom row runs from point 12 down to point 1, and the top row runs from point 13 up to point 24. Your checkers travel from high point numbers toward low ones; your opponent travels the opposite way.

\*\*Starting Position\*\*

Each player begins with the standard fifteen-checker arrangement:

\* 2 checkers on their 24-point.
\* 5 checkers on their 13-point.
\* 3 checkers on their 8-point.
\* 5 checkers on their 6-point.

Because the two sides move in opposite directions, your opponent's point numbers are the reverse of yours.

\*\*Beginning a Game\*\*

Each player rolls one die. Ties are rolled again. The player with the higher number takes the first turn and uses both opening numbers as that turn's dice. A new opening roll is made at the start of every game in a match.

After the opening turn, the players alternate turns and roll two dice each time. On a touch client, tap any point on the board to roll. On desktop, press Enter on any board point or press R. Rolling leaves your board focus where it was, so you can continue examining the same point.

\*\*Using the Dice\*\*

Each die normally moves one checker by that many points. You may move two different checkers, or move one checker twice if the intermediate point is open. The order can matter: a route may be legal with one die first and blocked with the other die first.

You must use as much of the roll as the rules allow:

\* If both dice can be played, you must play both.
\* If only one die can be played, you must play the higher die when the higher die has a legal move.
\* If you roll doubles, you play that number four times and must use as many of the four moves as possible.
\* If no die can be played, the game announces that the turn is over.

PlayAural evaluates the complete remaining roll, so it will reject a move that would unnecessarily prevent you from using another required die. The turn ends automatically after every legally usable die has been spent.

\*\*Selecting and Moving a Checker\*\*

Activate a point containing one of your checkers to select it, then activate a legal destination. PlayAural chooses the matching unused die. Activate Deselect to cancel the current selection. If nothing is selected, Deselect confirms that there is no selected checker.

On a touch client, activate Next destination or Previous destination when you want PlayAural to move focus through your legal choices. Before selecting a checker, these actions visit legal source points, or legal entry points when you have a checker on the bar. After selecting a checker, they visit its legal destinations. They are the only move controls that intentionally shift your board focus.

The Legal moves action opens a live list of every move allowed by the complete remaining roll. Point numbers in that list use your perspective. Undo reverses the most recent sub-move from the current turn, including restoring an opposing checker if that move hit it. Once the turn ends, its moves can no longer be undone.

You may land on:

\* An empty point.
\* A point occupied by any number of your own checkers.
\* A point occupied by exactly one opposing checker.

A point containing two or more opposing checkers is closed, so you cannot land there.

\*\*Blots, Hitting, and the Bar\*\*

A single checker standing alone on a point is called a blot. When an opposing checker lands on that point, the blot is hit and moved to the bar.

If you have one or more checkers on the bar, you must re-enter all of them before moving any checker already on the board. To re-enter, activate an open destination in your opponent's home board. The die determines the entry point: a 1 enters on the opponent's 1-point from their perspective, a 6 on their 6-point, and so on. PlayAural announces these destinations using your own point numbers.

An entry point is open if it is empty, contains your own checkers, or contains one opposing blot. If several checkers are on the bar, you must re-enter as many as the dice allow. After the last one re-enters, any unused die may move that checker again or move another checker. If every entry allowed by the remaining dice is closed, you cannot move and lose the rest of the turn.

\*\*Bearing Off\*\*

You may bear off only when all fifteen of your checkers are in your home board and none are on the bar.

\* Use a die equal to a checker's point number to bear that checker off exactly.
\* A die higher than the highest occupied point may bear off one checker from that highest occupied point.
\* You may not use an oversized die on a lower checker while any of your checkers remain on a higher point.

If bearing off is a checker's only legal destination, activate its point once. If the checker could either move within the board or bear off, activate it once to select it and activate the same point again to bear it off. This leaves the on-board destination available when that move is strategically better.

If a repeated activation cannot bear off, PlayAural explains why and clears the selection. If one of your remaining checkers is hit, you must re-enter it and return it to your home board before bearing off can continue.

\*\*Winning a Game\*\*

The first player to bear off all fifteen checkers wins the game. The basic result is then multiplied by the doubling cube, if the cube is in use:

\* \*\*Single game, 1 times the cube:\*\* The loser has borne off at least one checker.
\* \*\*Gammon, 2 times the cube:\*\* The loser has not borne off any checker.
\* \*\*Backgammon, 3 times the cube:\*\* The loser has not borne off any checker and still has a checker on the bar or in the winner's home board.

In a match, the result is added to the winner's match score. The first player to reach or exceed the target score wins the match.

\*\*The Doubling Cube\*\*

Matches longer than one point use a doubling cube, which begins centered at 1. At the start of your turn, before rolling, you may offer to double the value of the current game.

The opening turn cannot be doubled because its dice have already been rolled to decide who goes first.

The opponent must choose one response:

\* \*\*Accept:\*\* The cube value doubles. The accepting player takes ownership of the cube and is the only player who may offer the next double.
\* \*\*Drop:\*\* The current game ends immediately. The player who offered the double wins the cube's value before the proposed increase.

Dropping can require a second confirmation when destructive-action confirmation is enabled. A player cannot offer a double when the opponent owns the cube, after rolling, during a Crawford game, or when increasing the cube cannot improve that player's match result because the current value already wins the match. Single-point games do not use the cube.

\*\*The Crawford Rule\*\*

When either player first begins a game exactly one point short of winning the match, that game is the Crawford game. The doubling cube is disabled for that one game. If the match continues, the cube becomes available again in every later game. PlayAural applies this rule automatically.

\*\*Customizable Options\*\*

\* \*\*Match Length:\*\* The target score for the match, from 1 to 25. The default is 1. A match length of 1 plays a single game without the doubling cube.
\* \*\*Bot Difficulty:\*\* Simple, the default, prefers useful tactical moves. Random chooses among legal moves without that tactical preference.

\*\*Personal Game Options\*\*

\* \*\*Brief announcements:\*\* Uses shorter checker-move messages while retaining the mover, source, destination, and whether a checker was hit, entered from the bar, or borne off.
\* \*\*Confirm risky actions:\*\* Requires Drop to be activated a second time within 10 seconds before conceding a game in response to a double.

\*\*Information Actions\*\*

\* \*\*Status:\*\* Reports each player's checkers on the bar, outside the home board, and borne off.
\* \*\*Pip count:\*\* Reports the total distance each side still needs to move its checkers home and off. A lower count is usually better in a pure race, but it does not measure blocking or hitting chances.
\* \*\*Dice:\*\* Reports the unused dice for the current turn.
\* \*\*Legal moves:\*\* Opens a live list of moves allowed by the remaining dice.
\* \*\*Cube:\*\* Reports the cube's value, owner, and whether a double is currently possible.
\* \*\*Check scores:\*\* Reads the current match score. Detailed scores opens a live score panel.
\* \*\*Whose turn\*\* and \*\*Who's at the table:\*\* Report the active player and the table roster.

The commonly needed information actions are available directly on touch clients. Other actions remain in the Actions menu.

\*\*Keyboard Shortcuts\*\*

\* \*\*Enter on a board point:\*\* Roll before moving, select a checker, or choose a destination.
\* \*\*R:\*\* Roll at the start of your turn.
\* \*\*Ctrl+Backspace:\*\* Deselect the current checker.
\* \*\*Ctrl+Down or Ctrl+Right:\*\* Cycle forward through legal source points, or through legal destinations after selecting a checker. Opposing blots are offered first.
\* \*\*Ctrl+Up or Ctrl+Left:\*\* Cycle backward through the same choices.
\* \*\*Shift+D:\*\* Offer a double before rolling.
\* \*\*Y:\*\* Accept an offered double.
\* \*\*N:\*\* Drop an offered double.
\* \*\*U:\*\* Undo the latest sub-move of the current turn.
\* \*\*E:\*\* Read checker status.
\* \*\*P:\*\* Read both pip counts.
\* \*\*D:\*\* Read the doubling cube.
\* \*\*S:\*\* Read the match score.
\* \*\*Shift+S:\*\* Open detailed scores.
\* \*\*C:\*\* Read the remaining dice.
\* \*\*M:\*\* Open Legal moves.

\*\*Beginner Strategy\*\*

Try not to leave blots within easy reach of the opponent. Two or more checkers on a point make it safe from landing. Blocks are especially valuable when they slow an opposing checker that is trying to leave your home board.

When you have a checker on the bar, first look at which entry points are open. In a race with no further contact possible, use pip count to compare who is ahead. During bearing off, consider the whole roll before choosing the first checker, because one order may use more dice than another.
