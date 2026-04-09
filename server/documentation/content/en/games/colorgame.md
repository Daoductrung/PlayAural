\*\*Color Game\*\*

Color Game is PlayAural's adaptation of the traditional Filipino \*perya\* color-dice betting game. Everyone bets on one or more colors, three color dice are rolled together, and each color bet is paid strictly according to how many dice showed that same color.

\*\*Gameplay\*\*

\* The board has \*\*6 betting colors\*\*: red, blue, yellow, green, white, and orange.
\* Every round uses \*\*3 color dice\*\*.
\* Each die contains the same 6 colors, so a color may appear \*\*0, 1, 2, or 3 times\*\* in a round.
\* At the start of the match, every player receives a \*\*starting bankroll\*\* based on the host setting.
\* A round opens with a \*\*shared betting phase\*\*. This is not a strict one-player turn. All live players may place or change bets during the same timer window.
\* A \*\*live player\*\* in this implementation means a player whose bankroll is still above 0.
\* During betting, you may place chips on \*\*one color\*\* or split your total across \*\*multiple colors\*\*.
\* Every color bet is treated independently. You are not choosing one overall winning color for the whole round.
\* When you are satisfied with your bets, use \*\*Lock bets\*\*.
\* If all live players lock their bets before the timer expires, the dice roll immediately.
\* If the timer expires first, every remaining live player is automatically locked with their current bet sheet, including the possibility of locking \*\*no bet at all\*\*.
\* After the roll resolves, bankrolls are updated, the standings are announced, and a new betting round begins unless the match is over.

\*\*Special Mechanics\*\*

\* \*\*Shared betting phase:\*\* all live players may act during the same betting window.
\* \*\*Locked bets:\*\* once you lock your bets for the round, you cannot edit them again until the next round.
\* \*\*Sitting out:\*\* you may lock an empty bet sheet. In that case, you neither win nor lose chips in that round.
\* \*\*Bankrupt players:\*\* if your bankroll reaches 0, you remain on the standings but cannot place new bets.
\* \*\*Round timer:\*\* the timer does not discard your current bets. It simply locks whatever you already have when time runs out.

\*\*Scoring\*\*

Color Game is fundamentally about \*\*bankroll management\*\*.

\* Your main competitive value is your current \*\*bankroll\*\*.
\* The standings also track:
\* \*\*Profitable rounds:\*\* how many rounds ended with a positive net gain
\* \*\*Biggest win:\*\* your single largest one-round profit

\*\*Payout Logic\*\*

The code uses the following exact payout model for \*\*each individual color bet\*\*:

\* \*\*0 matches:\*\* net change is \*\*-stake\*\*
\* \*\*1 match:\*\* net change is \*\*+stake\*\*
\* \*\*2 matches:\*\* net change is \*\*+2 × stake\*\*
\* \*\*3 matches:\*\* net change is \*\*+3 × stake\*\*

This corresponds to the traditional \*\*1:1, 2:1, 3:1\*\* Color Game structure.

Example:

\* You place 5 chips on red and 3 chips on blue.
\* The dice come up red, red, green.
\* Your red bet matched \*\*2 dice\*\*, so its net result is \*\*+10\*\*.
\* Your blue bet matched \*\*0 dice\*\*, so its net result is \*\*-3\*\*.
\* Your total net result for the round is therefore \*\*+7 chips\*\*.

\*\*Winning The Match\*\*

The game supports two win conditions:

\* \*\*Last Player Standing\*\*
\* \*\*Highest Bankroll At The Round Limit\*\*

However, the current code also contains one shared early-end rule:

\* If only \*\*one live player\*\* remains, the match ends immediately, even if the round limit has not been reached yet.

That means the exact behavior is:

\* \*\*Last Player Standing:\*\*
\* If only one player still has chips, that player wins immediately.
\* If the round limit is reached first, the player with the highest bankroll wins.
\* \*\*Highest Bankroll At The Round Limit:\*\*
\* The intended focus is bankroll at the end of the limit.
\* But if only one player still has chips before the limit, the current implementation also ends immediately at that point.

If players are tied at the top, ranking is broken in this exact order:

\* higher bankroll
\* more profitable rounds
\* bigger single-round win
\* if still tied, the result remains tied

\*\*Customizable Options\*\*

\* \*\*Starting Bankroll:\*\* Default \*\*100\*\*. Valid range: \*\*10 to 1000\*\*.
\* Every player starts the match with this many chips.

\* \*\*Minimum Bet:\*\* Default \*\*1\*\*. Valid range: \*\*1 to 100\*\*.
\* Every non-zero color bet must be at least this amount.

\* \*\*Maximum Total Bet Per Round:\*\* Default \*\*20\*\*. Valid range in the option control: \*\*1 to 1000\*\*.
\* Additional validation in the game logic requires it to be:
\* at least the Minimum Bet
\* no greater than the Starting Bankroll
\* A player's real per-round cap is the smaller of:
\* their current bankroll
\* this option value

\* \*\*Betting Timer:\*\* Default \*\*15 seconds\*\*. Valid range: \*\*5 to 60 seconds\*\*.
\* This is the shared timer for the betting phase of each round.

\* \*\*Round Limit:\*\* Default \*\*20\*\*. Valid range: \*\*1 to 100\*\*.
\* Once this many rounds have been completed, the game ends and standings are finalized.

\* \*\*Win Condition:\*\* Default \*\*Last Player Standing\*\*.
\* Choices:
\* \*\*Last Player Standing\*\*
\* \*\*Highest Bankroll At The Round Limit\*\*

\*\*Keyboard Shortcuts\*\*

\* \*\*R:\*\* Set the red bet.
\* \*\*U:\*\* Set the blue bet.
\* \*\*Y:\*\* Set the yellow bet.
\* \*\*G:\*\* Set the green bet.
\* \*\*W:\*\* Set the white bet.
\* \*\*O:\*\* Set the orange bet.
\* \*\*C:\*\* Clear your current bets.
\* \*\*Space:\*\* Lock your bets for the current round.
\* \*\*E:\*\* Hear the current phase, timer, bankroll, lock state, and leader.
\* \*\*V:\*\* Hear every player's current bet sheet.
\* \*\*D:\*\* Hear the previous roll and each player's result from that roll.
\* \*\*T:\*\* Hear the current phase prompt.
\* \*\*S:\*\* Hear the standings.
\* \*\*Ctrl+U:\*\* Hear who is at the table.
