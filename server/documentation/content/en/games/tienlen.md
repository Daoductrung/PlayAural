\*\*Tien Len\*\*

Tien Len is a Vietnamese climbing card game built around pressure, timing, and hand control. You are not trying to take tricks for points. Instead, you are trying to empty your hand before everyone else while deciding when to release your weak cards, when to protect powerful 2s, and when to save chopping combinations for a critical moment.

The table can be played in two distinct forms:

\* \*\*Southern Tien Len\*\* (`Tiến Lên Miền Nam`), which is looser and more tactical.
\* \*\*Northern Tien Len\*\* (`Tiến Lên Miền Bắc`, also known as `Tú Lơ Khơ`), which is much stricter about suit and color structure.

\*\*Gameplay\*\*

Tien Len uses a standard 52-card deck. Each player receives 13 cards.

\* \*\*Card ranking:\*\* 3 is the lowest card. Then come 4, 5, 6, 7, 8, 9, 10, J, Q, K, A, and 2 is the highest card.
\* \*\*Suit ranking:\*\* Spades are lowest, then Clubs, then Diamonds, and Hearts are highest.
\* \*\*Opening play:\*\* The player who holds the \*\*3 of Spades\*\* leads the first hand, and that opening play must include the 3 of Spades.
\* \*\*Later hands:\*\* After that, the winner of the previous hand leads the next one.
\* \*\*On your turn:\*\* You either play a legal combination that beats the current trick, or you pass.
\* \*\*Locked pass:\*\* If you pass, you are out of that trick until the trick resets.
\* \*\*Trick reset:\*\* When all other players pass, the last player who made a successful play wins the trick and may start a fresh one with any legal lead.
\* \*\*Winning a hand:\*\* A hand ends immediately when one player gets rid of all their cards.

In PlayAural, you select one or more cards from your hand, then use \*\*Play Selected Cards\*\* to commit that combination.

\*\*Valid Combinations\*\*

Both variants allow the following core combinations:

\* \*\*Single:\*\* one card.
\* \*\*Pair:\*\* two cards of the same rank.
\* \*\*Triple:\*\* three cards of the same rank.
\* \*\*Four of a Kind:\*\* four cards of the same rank.
\* \*\*Straight:\*\* a run of consecutive ranks.

The exact rules for pairs and straights depend on the selected variant.

\*\*Southern Tien Len Rules\*\*

Southern Tien Len is the more flexible form.

\* Pairs only need to share the same rank.
\* Straights may mix suits.
\* 2s may not be used inside a straight.
\* A sequence of consecutive pairs is legal. Three or more consecutive pairs are called \*\*consecutive pairs\*\* (`đôi thông`).

Examples of legal Southern plays:

\* A pair of 8s in any two suits.
\* A straight like 5-6-7, even if all three cards have different suits.
\* Three consecutive pairs such as 5-5, 6-6, 7-7.

\*\*Southern Chopping Rules\*\*

Southern Tien Len includes the famous chopping system for beating 2s and certain power combinations.

\* \*\*Single 2:\*\*
\* A \*\*four of a kind\*\* can chop a single 2.
\* \*\*Three consecutive pairs\*\* can chop a single 2.

\* \*\*Pair of 2s:\*\*
\* \*\*Four consecutive pairs\*\* can chop a pair of 2s.

\* \*\*Triple 2s:\*\*
\* \*\*Five consecutive pairs\*\* can chop three 2s.

\* \*\*Three consecutive pairs:\*\*
\* A higher three-consecutive-pairs set can beat a lower one.
\* A \*\*four of a kind\*\* can also chop a three-consecutive-pairs set.
\* \*\*Four consecutive pairs\*\* can also beat a lower three-consecutive-pairs set.

\* \*\*Four of a kind:\*\*
\* \*\*Four consecutive pairs\*\* can chop a four of a kind.

Important PlayAural rule choice:

\* In this implementation, \*\*three consecutive pairs cannot be used to open a fresh trick\*\*. They are treated as a reactive chopping combination, not an opening lead.

\*\*Northern Tien Len Rules\*\*

Northern Tien Len is stricter and more formal.

\* Pairs must be the same rank and the same \*\*color\*\*.
\* That means a black pair must be Spades plus Clubs, and a red pair must be Diamonds plus Hearts.
\* Straights must be \*\*one suit only\*\*.
\* In other words, Northern straights are \*\*same-suit straights\*\*, not mixed-suit runs.
\* In this implementation, high-end same-suit series such as \*\*Q-K-A-2\*\* and \*\*J-Q-K-A-2\*\* are legal in Northern mode, but sequences do not wrap downward, so \*\*A-2-3\*\* is still illegal.
\* When answering an existing trick, your play must keep the same suit structure as the trick on the table. This is one of the main reasons Northern play is tighter.

Examples of legal Northern plays:

\* A black pair of 9s: 9 of Spades plus 9 of Clubs.
\* A red pair of Queens: Queen of Diamonds plus Queen of Hearts.
\* A straight like 7-8-9 of Hearts.

Examples of illegal Northern plays:

\* A pair made from one red card and one black card of the same rank.
\* A mixed-suit straight such as 7 of Hearts, 8 of Clubs, 9 of Hearts.

\*\*Northern Chopping Rules\*\*

Northern chopping is much narrower in this implementation.

\* A \*\*single 2\*\* may be chopped by a \*\*four of a kind\*\*.
\* A \*\*pair of 2s\*\* is a special high pair. It can beat any pair of another rank, and this implementation follows the stricter Northern handling rather than Southern-style double-sequence chopping.
\* A pair of 2s may be made from \*\*any two suits\*\*. When comparing two such pairs, the one containing the higher deuce suit has priority.
\* Southern-style consecutive-pairs chopping does \*\*not\*\* apply in Northern mode.

\*\*Northern Restriction On 2s\*\*

Northern Tien Len has one very important extra restriction:

\* You \*\*cannot finish the hand by playing 2s\*\*.
\* You also \*\*cannot make a play that leaves only 2s in your hand\*\*.

This means that in Northern mode, 2s are powerful but awkward. They can save you in the middle of a hand, but they are not safe final escape cards.

\*\*Passing And Trick Flow\*\*

\* If you pass, you are locked out of the current trick.
\* You cannot jump back into that trick just because you later find a normal response.
\* In Southern mode, the special chopping exceptions still matter when a 2 is on the table, so powerful chopping combinations remain tactically important.
\* Once the trick resets, every player's pass lock is cleared.

\*\*Scoring\*\*

This PlayAural version scores by \*\*hand wins\*\* rather than money penalties.

\* The winner of each hand earns \*\*1 hand win\*\*.
\* The match ends when a player reaches the selected target:
\* \*\*Single Hand:\*\* first hand decides the match.
\* \*\*Best of 3:\*\* first player to 2 hand wins.
\* \*\*Best of 5:\*\* first player to 3 hand wins.

\*\*Customizable Options\*\*

\* \*\*Variant:\*\* `Southern Tien Len` or `Northern Tien Len`.
\* \*\*Match Length:\*\* `Single Hand`, `Best of 3`, or `Best of 5`.
\* \*\*Turn Timer:\*\* `10`, `15`, `20`, `30`, `45`, `60`, `90` seconds, or `Unlimited`.

\*\*Keyboard Shortcuts\*\*

\* \*\*Space:\*\* Play the currently selected cards.
\* \*\*P:\*\* Pass.
\* \*\*C:\*\* Check the current trick.
\* \*\*H:\*\* Read your hand.
\* \*\*E:\*\* Read how many cards each player has left.
\* \*\*V:\*\* Hear which variant the table is using.
\* \*\*Shift+T:\*\* Check the turn timer.
