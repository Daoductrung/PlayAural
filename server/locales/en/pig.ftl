game-name-pig = Pig

pig-roll = Roll the die
pig-hold = Hold { $points } points
pig-check-turn-status = Check turn status

pig-game-start =
    Pig begins. The first { $team ->
        [yes] team
       *[no] player
    } to hold { $target } points wins. The die has { $sides } sides, and rolling a 1 loses every unbanked point from that turn. { $minimum ->
        [0] You may hold after any scoring roll.
       *[other] You must collect at least { $minimum } turn points before holding.
    }
pig-game-start-brief =
    Pig begins. Target: { $target }. Die: { $sides } sides. Minimum hold: { $minimum }.{ $team ->
        [yes] Teams share scores.
       *[no] Individual scores.
    }
pig-round-start = Round { $round } begins. Every active player will take one turn.
pig-round-start-brief = Round { $round }.

pig-you-roll-result = You rolled { $roll }. Your turn total is now { $total } points.
pig-player-roll-result = { $player } rolled { $roll }. Their turn total is now { $total } points.
pig-you-roll-result-brief = You: { $roll }; turn total { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; turn total { $total }.

pig-you-bust = You rolled a 1 and lose all { $points } unbanked points. Your turn ends with no score.
pig-player-busts = { $player } rolled a 1 and loses all { $points } unbanked points. Their turn ends with no score.
pig-you-bust-brief = You rolled 1 and lose { $points } turn points.
pig-player-busts-brief = { $player } rolled 1 and loses { $points } turn points.

pig-you-hold =
    You hold { $points } points. { $team ->
        [yes] Your team now has { $total } points.
       *[no] Your total score is now { $total } points.
    }
pig-player-holds =
    { $player } holds { $points } points. { $team ->
        [yes] { $team_name } now has { $total } points.
       *[no] Their total score is now { $total } points.
    }
pig-you-hold-brief =
    You hold { $points };{ $team ->
        [yes] { $team_name } total { $total }.
       *[no] your total { $total }.
    }
pig-player-holds-brief =
    { $player } holds { $points };{ $team ->
        [yes] { $team_name } total { $total }.
       *[no] total { $total }.
    }

pig-you-win =
    { $team ->
        [yes] Your team, { $winner }, is the winner of Pig with { $score } points!
       *[no] You are the winner of Pig with { $score } points!
    }
pig-winner =
    { $team ->
        [yes] The winner is { $winner }, with { $score } points!
       *[no] The winner is { $winner }, with { $score } points!
    }
pig-you-win-brief =
    { $team ->
        [yes] Winner: your team, { $winner }, with { $score }.
       *[no] Winner: you, with { $score }.
    }
pig-winner-brief = Winner: { $winner }, with { $score }.

pig-confirm-risky-roll =
    Rolling again puts { $points } unbanked points at risk, with a { $risk } percent chance of losing them. { $winning ->
        [yes] Holding now would give you { $total } points and win the game.
       *[no] Holding now would give you { $total } of the { $target } points needed to win.
    } Press Roll again within { $seconds } seconds to confirm.

pig-action-resolving = The die is still rolling. Wait for the result.
pig-no-turn-points = Roll the die at least once before holding.
pig-need-more-points = You have { $current } turn points, but this table requires at least { $required } before holding.

pig-set-min-bank = Minimum hold: { $points }
pig-set-dice-sides = Die sides: { $sides }
pig-enter-min-bank = Enter the minimum turn points required to hold:
pig-enter-dice-sides = Enter the number of sides on the die:
pig-option-changed-min-bank = Minimum hold changed to { $points } points.
pig-option-changed-dice = The die now has { $sides } sides.
pig-desc-target-score = The first player or team to hold this many total points wins immediately.
pig-desc-min-bank = The number of turn points required before Hold becomes available. Set this to 0 for standard Pig.
pig-desc-dice-sides = The number of sides on the single die. Standard Pig uses a six-sided die; rolling 1 always loses the turn total.
pig-desc-team-mode = Play individually or share one score with teammates. A team wins immediately when a member holds enough points.

pig-error-target-out-of-range = Target score { $value } is invalid. Choose a value from { $min } to { $max }.
pig-error-min-bank-out-of-range = Minimum hold { $value } is invalid. Choose a value from { $min } to { $max }.
pig-error-dice-sides-out-of-range = A { $value }-sided die is unsupported. Choose from { $min } to { $max } sides.
pig-error-min-bank-too-high = Minimum hold { $minimum } must be lower than the target score of { $target }.

pig-status-target = Target score: { $target } points.
pig-status-round = Current round: { $round }.
pig-status-current-turn = { $player } is playing: { $banked } banked, { $turn } in this turn, { $potential } if held now.
pig-status-standing = { $rank }. { $team }: { $score } points.

pig-line-format = { $rank }. { $player }: { $points }
