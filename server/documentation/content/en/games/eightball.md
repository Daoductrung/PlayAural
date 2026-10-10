**Pool**

Pool offers published rules for two-player Eight-Ball, four-player Eight-Ball Doubles, and five-player Cutthroat. A new table automatically uses the creator's PlayAural language when it is English, Spanish, or Portuguese; every other language falls back to English. The creator can then change the shared table language before play.

**Modes**

* **Eight-Ball Singles, 2 players:** One against one under WPA Eight-Ball rules. Each player pockets a group of seven balls and then legally pockets the 8 ball in the called pocket.
* **Eight-Ball Doubles, 4 players:** Two against two under WPA Eight-Ball rules. Partners alternate shots. Before the match, the host may review the two teams and swap players between them.
* **Cutthroat, 5 players:** Published BCA Cutthroat rules. In playing order, players protect balls 1 through 3, 4 through 6, 7 through 9, 10 through 12, and 13 through 15. Pocket opponents' balls; the last player with a protected ball on the table wins. This table uses the rules' permitted no-call option, so B, P, and safety declarations are not used in Cutthroat.

In Cutthroat, the cue ball must contact an opponent's ball first. A legal pot continues the turn. A foul restores one previously pocketed ball for every opponent; an opponent's ball pocketed illegally is also spotted. A player whose last protected ball falls is eliminated, but returns if a later foul restores one of those balls. The next rack starts in elimination order, with the previous winner last.

**The Table and Balls**

The creation menu names the choices Compact Bar Table, Tournament Table, and Professional Table without speaking feet. Internally their playing surfaces are 78 by 39, 92 by 46, and 100 by 50 inches. Every pocket uses one concrete WPA-compliant profile: midpoint legal mouths, 1.625-inch corner shelves, 0.1875-inch side shelves, 142- and 104-degree horizontal cuts, and 13.5-degree back draft. Pocket facings are collision surfaces, and a ball is captured only after crossing the shelf.

The table starts open. Groups are not decided on the break. After the break, the first player to legally pocket the called ball in the called pocket receives that group; the opponent receives the other group.

**The Break**

Before the first rack, the players lag for the break. Each player adjusts power with X and Shift+X, then presses Space. The ball must touch the foot cushion once and return without touching a side cushion or the head cushion. The valid ball stopping closest to the head cushion wins. Every player receives the same tiny natural stroke variation, so choosing the same displayed power does not force an artificial tie. Equal or doubly invalid lags are repeated. The winner chooses who takes the first break with the arrows and Enter. Later breaks alternate.

No ball or pocket is called on the break. A break is legal when a numbered ball is pocketed or at least four numbered balls reach cushions. The table remains open after the break.

After an illegal break, the incoming player may accept the table, rerack and break, or rerack and let the offender break again. If the 8 ball falls on a legal break, the breaker may spot it and continue or rerack. Fouled breaks use the head-string choices. Press 1, 2, or, when offered, 3 to answer the announced decision.

**Called Shots**

Before every shot other than the break, press M to open the ball list and Enter to go directly to one, or use Shift+M to cycle quickly. These shortcuts only move focus; press B once to call the focused ball. Walking around the table remains available. Then press P to open all six pockets. Use the arrow keys to browse them; every item reports the pocket number and the real travel distance from the called ball. Press Enter to confirm.

Once your group is clear, call the 8 ball and its pocket. Pocketing the 8 early, in the wrong pocket, or during a foul loses the rack.

Press Shift+Y before shooting to declare a safety under the official WPA safety-shot rule. A safety replaces the ball-and-pocket call for that shot, so B and P are not required. The shot must still be legal: the cue ball must contact a legal object ball first and, after contact, a ball must be pocketed or reach a cushion. Play passes to the opponent even if a ball is legally pocketed, and every pocketed object ball remains down. A foul on the safety also gives the incoming opponent cue-ball in hand. Press Shift+Y again before shooting to cancel the declaration.

This implementation follows the safety-shot and foul provisions in the [official WPA Eight-Ball rules](https://wpapool.com/rules/).

**Legal Shots and Fouls**

On a legal shot, the cue ball must first contact a legal object ball. After contact, a ball must be pocketed or any ball must reach a cushion.

It is a foul if the cue ball is pocketed, no object ball is contacted, the wrong ball is contacted first, or no ball reaches a cushion or pocket after contact. After a foul, the opponent receives ball in hand and may position the cue ball before confirming with Space or Enter.

The game announces the exact reason for every foul. A legal shot that misses the called ball ends the turn but is not announced as a foul.

Player events follow the standard PlayAural perspective: the acting player hears "you", while everyone else hears that player's name. This applies to turns, the first break, assigned groups, pocketed balls, continued turns, fouls, cue-ball placement, Cutthroat status changes, and wins. Neutral table events remain identical for everyone.

**Aiming and Three-Dimensional Physics**

The arrow keys move your position continuously around the table: Up and Down move forward and backward, while Left and Right strafe. A ball number is announced once when that ball enters focus. Shift+Left and Shift+Right rotate 45 degrees, Ctrl+Shift+Left and Ctrl+Shift+Right rotate 10 degrees, and Ctrl+Left and Ctrl+Right refine by one degree. After calling a ball and pocket, every adjustment reports the remaining direction. Reaching the called pocket snaps the cursor to its real coordinate instead of oscillating across it.

Optional power assistance uses the same mouths, shelves, facings, friction, and collisions as the real shot. While aiming, it instantly reports the physical reach minimum without blocking arrow input. X and Shift+X search for the first five-percent step actually potted by the simulation and check the selected force on the complete table. “Sufficient” therefore means the called ball entered the called pocket in that simulation; a reach-only value is never presented as a guaranteed pot.

Cue elevation and the contact point on the cue ball change its path. Follow, draw, and side spin continue to act after contacts and at cushions. An elevated stroke can lift the cue ball above the cloth. Collisions, jumps, cushions, friction, and pockets are resolved before the result is applied.

**Keyboard Shortcuts**

* **Up and Down Arrow:** Walk forward or backward in the current direction.
* **Shift+Up and Shift+Down:** Walk five units.
* **Left and Right Arrow:** Strafe across the table.
* **Shift+Left and Shift+Right:** Turn the aim 45 degrees quickly.
* **Ctrl+Left and Ctrl+Right:** Turn the aim one degree and, after a call, hear the remaining error.
* **Ctrl+Shift+Left and Ctrl+Shift+Right:** Turn the aim ten degrees.
* **Ctrl+Up and Ctrl+Down:** Raise or lower the cue.
* **Page Up and Page Down:** Apply follow or draw.
* **Home and End:** Apply left or right English.
* **X and Shift+X:** Increase or decrease power and hear its current value. Power is not announced when the shot is taken.
* **B:** In Eight-Ball, immediately call the focused ball.
* **M:** Open the ball list and press Enter to go directly to one without calling it.
* **Shift+M:** Move quickly to the next ball without calling it.
* **P:** In Eight-Ball, open the six-pocket list; browse with the arrows and confirm with Enter.
* **Shift+Y:** In Eight-Ball, declare or cancel a safety.
* **L:** Check which ball lies on the aim line.
* **C:** Repeat the relative direction, distance, and sound of the called pocket. Before a pocket is called, each press cycles through all six pockets.
* **V:** Read the table overview.
* **E:** Read position, direction, power, spin, elevation, and the current call.
* **Space or Enter:** Shoot or confirm cue-ball placement.

**Customizable Options**

* **Mode:** Eight-Ball Singles, Eight-Ball Doubles, or five-player Cutthroat.
* **Table language:** English, Spanish, or Portuguese. It initially follows the creator's supported PlayAural language, otherwise English. The selection applies to the spoken game messages for everyone at the table.
* **Table size:** Compact Bar Table, Tournament Table, or Professional Table. Geometry, rack positions, rails, pockets, aiming, and bots all use the selected surface.
* **Power assistance:** When enabled, all human players hear whether the current power is sufficient for a calculable direct called shot. When disabled, all human players hear only the selected percentage.
* **Racks to win:** Sets the number of racks required to win the match, from 1 to 10.
* **Bot difficulty:** Changes aiming accuracy, power control, and shot selection.
