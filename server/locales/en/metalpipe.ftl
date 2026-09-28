# Metal Pipe game messages

game-name-metalpipe = Metal Pipe

metalpipe-mode-single = Single bonk
metalpipe-mode-multiple = Multiple bonks
metalpipe-self-bonk-allowed = self-bonks allowed
metalpipe-self-bonk-blocked = self-bonks blocked

metalpipe-game-start = Metal Pipe begins in { $mode } mode. The pipe will choose everything automatically.
metalpipe-game-start-brief = Metal Pipe: { $mode }.

metalpipe-you-hit-other = You swing the metal pipe and hit { $bonked }. { $bonked } is eliminated.
metalpipe-player-hits-you = { $bonker } swings the metal pipe and hits you. You are eliminated.
metalpipe-player-hits-other = { $bonker } swings the metal pipe and hits { $bonked }. { $bonked } is eliminated.
metalpipe-you-hit-self = You somehow hit yourself with the metal pipe and are eliminated.
metalpipe-player-hits-self = { $bonker } somehow hits { GENDER_TERM($bonker_gender, "reflexive") } with the metal pipe and is eliminated.

metalpipe-you-hit-other-brief = You hit { $bonked }. { $bonked } out.
metalpipe-player-hits-you-brief = { $bonker } hits you. You are out.
metalpipe-player-hits-other-brief = { $bonker } hits { $bonked }. { $bonked } out.
metalpipe-you-hit-self-brief = You self-bonk. Out.
metalpipe-player-hits-self-brief = { $bonker } self-bonks. Out.

metalpipe-you-win = You win. The metal pipe has spoken.
metalpipe-you-win-with-others = You win along with { $players }. The metal pipe has spoken.
metalpipe-players-win = { $players } win. The metal pipe has spoken.
metalpipe-you-win-brief = You win.
metalpipe-you-win-with-others-brief = You and { $players } win.
metalpipe-players-win-brief = Winners: { $players }.
metalpipe-no-winner = The metal pipe leaves no winner.
metalpipe-no-winner-brief = No winner.

metalpipe-check-status = View pipe status
metalpipe-status-mode = Mode: { $mode }; { $self_bonk }.
metalpipe-status-progress = Bonks resolved: { $count }. Players still standing: { $alive } of { $total }.
metalpipe-status-awaiting = The pipe has not landed yet.
metalpipe-status-last-other = Last bonk: { $bonker } hit { $bonked }.
metalpipe-status-last-self = Last bonk: { $bonker } hit { GENDER_TERM($bonker_gender, "reflexive") }.
metalpipe-status-player = { $player}: { $status }.
metalpipe-status-alive = Standing
metalpipe-status-eliminated = Eliminated
metalpipe-no-turn-automatic = Metal Pipe is resolving automatically. There are { $alive } players still standing, and no player has a manual turn.

metalpipe-final-results = Metal Pipe results
metalpipe-end-winner = Winner: { $player }.
metalpipe-end-winners = Winners: { $players }.
metalpipe-line-format = { $player}: { $status }

metalpipe-set-multiple-bonks = Multiple bonks: { $enabled }
metalpipe-option-changed-multiple-bonks = Multiple bonks set to { $enabled }.
metalpipe-desc-multiple-bonks = When enabled, the pipe keeps choosing bonkers and targets until only one player remains (default off).
metalpipe-set-allow-self-bonk = Allow self-bonk: { $enabled }
metalpipe-option-changed-allow-self-bonk = Allow self-bonk set to { $enabled }.
metalpipe-desc-allow-self-bonk = When enabled, the randomly chosen bonker can also become the target (default on).
