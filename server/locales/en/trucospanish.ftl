# Options
trucospanish-length-18 = 18 points per came
trucospanish-length-24 = 24 points per came
trucospanish-set-length = Came length: { $mode }
trucospanish-select-length = Select the came length:
trucospanish-option-changed-length = The came length is now { $mode }.
trucospanish-desc-length = The game is won by winning two cames. A came is played to the chosen number of points: 24 as in the Falles championship of València and the Universitat Politècnica de València tournament, or 18 as in the Torrent tournament and the Museu d'Història de València description. When a side reaches it, that side wins the came and both scores start again from zero. La falta is worth what the leader still needs to finish the came, and Joc fora wins the whole game.
trucospanish-desc-team-mode = Individual is a one-on-one game for 2 players. 2v2 uses 4 players; partners share the score and may call for the whole team.

# Calls
trucospanish-call-truc = Truc
trucospanish-call-retruc = Retruc
trucospanish-call-quatre-val = Quatre val
trucospanish-call-joc-fora = Joc fora
trucospanish-call-envit = Envit
trucospanish-call-torna = Torna
trucospanish-call-la-falta = La falta

# Actions and messages
trucospanish-action-accept = Vull (accept)
trucospanish-action-decline = No vull (refuse)
trucospanish-action-mazo = Me'n vaig (leave the hand)
trucospanish-accept-you = You say Vull to { $call }.
trucospanish-accept-player = { $player } says Vull to { $call }.
trucospanish-decline-you = You say No vull to { $call }.
trucospanish-decline-player = { $player } says No vull to { $call }.
trucospanish-mazo-you = You say Me'n vaig and give up the hand for your whole team.
trucospanish-mazo-player = { $player } says Me'n vaig and gives up the hand for the whole team.
trucospanish-reason-truc = the Truc
trucospanish-reason-envit = the Envit
trucospanish-game-start = Spanish Truco begins. Win two cames of { $points } points to win the game.
trucospanish-desc-mazo = Give up the hand for your whole team. The other side scores the hand's current value.
trucospanish-came-you = You win a came! You have { $cames } { $cames ->
    [one] came
   *[other] cames
}. The score starts again from zero.
trucospanish-came-player = { $player } wins a came and has { $cames } { $cames ->
    [one] came
   *[other] cames
}. The score starts again from zero.
trucospanish-came-your-team = Your team wins a came! You have { $cames } { $cames ->
    [one] came
   *[other] cames
}. The score starts again from zero.
trucospanish-came-team = { $team } wins a came and has { $cames } { $cames ->
    [one] came
   *[other] cames
}. The score starts again from zero.

trucospanish-pending-answer = { $player } called { $call }. Answer with Vull or No vull, or raise.
trucospanish-error-answer-first = You must answer { $call } before doing anything else. Choose Vull or No vull, or raise.
trucospanish-error-raise-max = Joc fora is already the highest call and cannot be raised.
trucospanish-error-bad-count = Spanish Truco needs 2 or 4 players, but there are { $count }.
trucospanish-error-team-mode-count = Team mode { $mode } cannot be used with { $count } players. Use Individual for 2 players or 2v2 for 4 players.
trucospanish-status-envit-open = Envit can still be called this hand.
trucospanish-status-envit-closed = Envit is closed for this hand.
trucospanish-status-no-truc = No Truc has been called. The hand is worth { $points } { $points ->
    [one] point
   *[other] points
}.
trucospanish-falta-value = La falta is worth { $points } { $points ->
    [one] point
   *[other] points
}.
trucospanish-reveal-envit-you = The envit was won with your cards: { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.
trucospanish-reveal-envit-player = The envit was won by { $player } with { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.
trucospanish-error-envit-late = Envit can only be called before you play your first card.
trucospanish-error-envit-closed = Envit is closed because the Truc has already been accepted.
trucospanish-error-envit-done = Envit has already been played this hand.
trucospanish-error-envit-cannot-raise = { $call } cannot be added to the envit that is being played.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] point
   *[other] points
} in this came, { $cames } { $cames ->
    [one] came
   *[other] cames
} won
trucospanish-game-win-you = You win the game with { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-player = { $player } wins the game with { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-game-win-your-team = Your team wins the game with { $cames } { $cames ->
    [one] came
   *[other] cames
}!
trucospanish-game-win-team = { $team } wins the game with { $cames } { $cames ->
    [one] came
   *[other] cames
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] came
   *[other] cames
}
trucospanish-cames-line = { $team }: { $cames } { $cames ->
    [one] came
   *[other] cames
} won
