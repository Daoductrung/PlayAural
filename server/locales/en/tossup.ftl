game-name-tossup = Toss Up

tossup-roll-first =
    Roll { $count } { $count ->
        [one] die
       *[other] dice
    }
tossup-roll-remaining =
    Roll { $count } remaining { $count ->
        [one] die
       *[other] dice
    }
tossup-bank =
    Bank { $points } { $points ->
        [one] point
       *[other] points
    }
tossup-check-turn-status = Check turn status

tossup-game-start = Toss Up begins with { $rules } rules, { $dice } dice per set, and a target threshold of { $target }. Exceed the threshold and finish the remaining turns to win.
tossup-game-start-brief = Toss Up begins. Exceed { $target }.
tossup-round-start = Round { $round } begins.
tossup-round-start-brief = Round { $round }.

tossup-your-turn =
    Your turn. Your banked score is { $score }; roll { $dice } { $dice ->
        [one] die
       *[other] dice
    } to begin.
tossup-player-turn =
    { $player }'s turn with { $score } banked points and { $dice } { $dice ->
        [one] die
       *[other] dice
    }.
tossup-your-turn-brief = Your turn: { $score } points.
tossup-player-turn-brief = { $player }'s turn: { $score } points.

tossup-you-roll = You rolled { $results }.
tossup-player-rolls = { $player } rolled { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] You: { $results }; turn total { $turn_points }; fresh set of { $dice_count }.
       *[no] You: { $results }; turn total { $turn_points }; { $dice_count } left.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; turn total { $turn_points }; fresh set of { $dice_count }.
       *[no] { $player }: { $results }; turn total { $turn_points }; { $dice_count } left.
    }

tossup-result-green = { $count } green
tossup-result-yellow = { $count } yellow
tossup-result-red = { $count } red

tossup-you-have-points =
    You set aside { $gained } green { $gained ->
        [one] die
       *[other] dice
    }. Your turn total is { $turn_points }, with { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } remaining.
tossup-player-has-points =
    { $player } sets aside { $gained } green { $gained ->
        [one] die
       *[other] dice
    } and has { $turn_points } turn points, with { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } remaining.

tossup-you-get-fresh = Every die is green. You receive a fresh set of { $count } dice and may roll again or bank.
tossup-player-gets-fresh = Every die is green. { $player } receives a fresh set of { $count } dice.

tossup-you-bust =
    { $variant ->
        [Standard] Red light: you rolled no green and at least one red. Your turn ends and you lose { $points } unbanked points.
       *[PlayAural] All rolled dice are red. Your turn ends and you lose { $points } unbanked points.
    }
tossup-player-busts =
    { $variant ->
        [Standard] Red light: { $player } rolled no green and at least one red, ending the turn and losing { $points } unbanked points.
       *[PlayAural] All of { $player }'s rolled dice are red, ending the turn and losing { $points } unbanked points.
    }
tossup-you-bust-brief = You: { $results }; bust; lose { $points }.
tossup-player-busts-brief = { $player }: { $results }; bust; loses { $points }.

tossup-you-bank = You bank { $points } points, bringing your total score to { $total }.
tossup-player-banks = { $player } banks { $points } points, bringing { GENDER_TERM($player_gender, "possessive-determiner") } total score to { $total }.
tossup-you-bank-brief = You bank { $points }; total { $total }.
tossup-player-banks-brief = { $player } banks { $points }; total { $total }.

tossup-you-trigger-final-turns =
    You exceed the { $target }-point threshold with { $score }.
    { $count ->
        [one] The remaining player receives one final turn.
       *[other] The remaining { $count } players each receive one final turn.
    }
tossup-player-triggers-final-turns =
    { $player } exceeds the { $target }-point threshold with { $score }.
    { $count ->
        [one] The remaining player receives one final turn.
       *[other] The remaining { $count } players each receive one final turn.
    }
tossup-you-trigger-final-turns-brief =
    You set the score to beat at { $score }; { $count } { $count ->
        [one] turn remains.
       *[other] turns remain.
    }
tossup-player-triggers-final-turns-brief =
    { $player } sets the score to beat at { $score }; { $count } { $count ->
        [one] turn remains.
       *[other] turns remain.
    }

tossup-you-win = You win Toss Up with { $score } points.
tossup-winner = { $player } wins Toss Up with { $score } points.
tossup-you-win-brief = You win: { $score }.
tossup-winner-brief = { $player } wins: { $score }.
tossup-tie-tiebreaker = { $players } are tied for the highest score above the target. Only those players continue into a tiebreaker round.
tossup-tie-tiebreaker-brief = Tiebreaker: { $players }.
tossup-tiebreaker-round-start = Tiebreaker round { $round } begins for { $players }.
tossup-tiebreaker-round-start-brief = Tiebreaker round { $round }: { $players }.

tossup-your-turn-awaiting-roll =
    Your turn has not started rolling yet. You have { $score } banked points and { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } ready.
tossup-player-turn-awaiting-roll =
    { $player } has not rolled yet. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $score } banked points and { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } ready.
tossup-your-turn-status =
    Your last roll was { $results }. You have { $turn_points } unbanked turn points, { $score } banked points, and { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } ready to roll.
tossup-player-turn-status =
    { $player } last rolled { $results }. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $turn_points } unbanked turn points, { $score } banked points, and { $dice_count } { $dice_count ->
        [one] die
       *[other] dice
    } ready to roll.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] Banking now would put you ahead with { $total } points, above the { $target }-point threshold.
       *[no] You currently have { $points } unbanked turn points.
    }
    Rolling { $dice } { $dice ->
        [one] die
       *[other] dice
    } has about a { $risk } percent chance of a bust. Press Roll again within { $seconds } seconds to confirm, or bank to protect the points.

tossup-set-rules-variant = Rules: { $variant }
tossup-select-rules-variant = Select the dice and bust rules:
tossup-option-changed-rules = Rules changed to { $variant }.
tossup-desc-rules-variant = Classic uses three green faces, two yellow faces, and one red face per die; a roll with no green and at least one red is a bust. Forgiving gives all three colors equal odds and busts only on all red.

tossup-desc-target-score = The game enters its final response turns after a player banks more than this score (default 100, range 20-500).
tossup-set-starting-dice = Dice per set: { $count }
tossup-enter-starting-dice = Enter the number of dice in each fresh set:
tossup-option-changed-dice = Dice per set changed to { $count }.
tossup-desc-starting-dice = Choose how many dice begin each turn and return after every die becomes green (default 10, range 5-20).


tossup-rules-standard = Classic
tossup-rules-PlayAural = Forgiving
tossup-rules-standard-desc = Three green faces, two yellow faces, and one red face. Bust on no green with at least one red.
tossup-rules-PlayAural-desc = Equal odds for all three colors. Bust only when every rolled die is red.

tossup-error-roll-not-playing = You cannot roll because Toss Up is not currently in progress.
tossup-error-roll-no-turn = You cannot roll because Toss Up has no active turn right now.
tossup-error-roll-not-your-turn = You cannot roll during { $player }'s turn. Wait until the turn reaches you.
tossup-error-bank-not-playing = You cannot bank because Toss Up is not currently in progress.
tossup-error-bank-no-turn = You cannot bank because Toss Up has no active turn right now.
tossup-error-bank-not-your-turn = You cannot bank during { $player }'s turn. Wait until the turn reaches you.
tossup-error-bank-roll-first = Roll at least once before banking. An all-yellow roll may be banked for zero points to end your turn.
tossup-error-spectator-action = Spectators can check public Toss Up status, but cannot roll or bank points.
tossup-error-status-not-playing = Turn status is unavailable because Toss Up is not currently in progress.
tossup-error-status-no-turn = Turn status is unavailable because Toss Up has no active player right now.
tossup-error-target-out-of-range = The target threshold is { $value }; it must be from { $min } through { $max } points.
tossup-error-dice-out-of-range = The fresh-set size is { $value }; it must be from { $min } through { $max } dice.
tossup-error-rules-variant = The rules value “{ $variant }” is unsupported. Choose Classic or Forgiving.

tossup-line-format = { $rank }. { $player }: { $points }
