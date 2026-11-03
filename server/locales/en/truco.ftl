game-name-truco = Truco

# Options
truco-set-variant = Variant: { $mode }
truco-select-variant = Select the Truco variant:
truco-option-changed-variant = The variant is now { $mode }.
truco-desc-variant = Argentine Truco uses the Spanish 40-card deck, with envido and an optional flor. Brazilian Truco (Paulista) uses a French deck with a turned-up card, the vira, that decides the strongest cards, and raises worth 3, 6, 9 and 12 points. Spanish Truco (Valencian Truc) uses a 22-card deck with envit and the Joc fora, which is worth the whole game.
truco-variant-argentine = Argentine Truco
truco-variant-brazilian = Brazilian Truco
truco-variant-spanish = Spanish Truco
truco-length-15 = 15 points
truco-length-30 = 30 points
truco-set-length = Game length: { $mode }
truco-select-length = Select the game length:
truco-option-changed-length = The game length is now { $mode }.
truco-desc-length = In a 15-point game the first side to reach 15 points wins. In a 30-point game, points 1 to 15 are the malas (first half) and points 16 to 30 are the buenas (second half); the first side to reach 30 wins.
truco-set-flor = Flor: { $enabled }
truco-option-changed-flor = Flor is now { $enabled }.
truco-desc-flor = When on, a player dealt three cards of the same suit has a flor. It is announced automatically and cancels the envido. Flor is worth 3 points, Contraflor 6, and Contraflor al resto is worth what the leading side still needs to win. Only a player with a flor can answer or raise. A flor counts 20 plus the values of all three cards (figures are worth zero), so 7, 6 and 5 of one suit make 38; the higher flor wins. When off, three cards of one suit have no special value.
truco-desc-team-mode = Individual is a one-on-one game for 2 players. 2v2 uses 4 players and 3v3 uses 6 players; partners share the score and may call for the whole team.

# Spanish deck
truco-suit-oros = Coins
truco-suit-copas = Cups
truco-suit-espadas = Swords
truco-suit-bastos = Clubs
truco-card-name = { $rank } of { $suit }

# Calls
truco-call-truco = Truco
truco-call-retruco = Retruco
truco-call-valecuatro = Vale cuatro
truco-call-envido = Envido
truco-call-real-envido = Real envido
truco-call-falta-envido = Falta envido
truco-call-flor = Flor
truco-call-contraflor = Contraflor
truco-call-contraflor-al-resto = Contraflor al resto

# Actions
truco-action-play-card = { $card }
truco-action-accept = Quiero (accept)
truco-action-decline = No quiero (decline)
truco-action-mazo = Me voy al mazo (fold your cards)
truco-read-hand = Read your cards
truco-read-table = Read cards on the table
truco-read-calls = Read current calls

# Game and hand flow
truco-game-start-flor = Truco begins with flor. The first side to reach { $points } points wins.
truco-game-start-no-flor = Truco begins without flor. The first side to reach { $points } points wins.
truco-hand-start = Hand { $hand } begins. The cards are dealt.
truco-dealer-you = You deal.
truco-dealer-player = { $player } deals.
truco-mano-you = You are mano and play first.
truco-mano-player = { $player } is mano and plays first.
truco-your-cards = Your cards: { $cards }.
truco-no-cards = You have no cards left.
truco-your-turn = Your turn to play a card.

# Playing cards and tricks
truco-play-you = You play { $card }.
truco-play-player = { $player } plays { $card }.
truco-trick-win-you = Trick { $trick }: you win with { $card }.
truco-trick-win-teammate = Trick { $trick }: your teammate { $player } wins with { $card }.
truco-trick-win-opponent = Trick { $trick }: { $player } wins with { $card } for { $team }.
truco-trick-tie = Trick { $trick } is a tie, called parda.

# Calling and answering
truco-call-you = You call { $call }.
truco-call-player = { $player } calls { $call }.
truco-call-goes-first-you = You call { $call }. Envido goes first, before the Truco is answered.
truco-call-goes-first-player = { $player } calls { $call }. Envido goes first, before the Truco is answered.
truco-pending-answer = { $player } called { $call }. Answer with Quiero or No quiero, or raise.
truco-pending-wait = Waiting for { $team } to answer { $call }.
truco-accept-you = You say Quiero to { $call }.
truco-accept-player = { $player } says Quiero to { $call }.
truco-decline-you = You say No quiero to { $call }.
truco-decline-player = { $player } says No quiero to { $call }.
truco-mazo-you = You say Me voy al mazo and fold your cards.
truco-mazo-player = { $player } says Me voy al mazo and folds their cards.
truco-team-folded-your-team = Everyone on your team has folded.
truco-team-folded-team = Everyone on { $team } has folded.
truco-flor-announce-you = You have a flor.
truco-flor-announce-player = { $player } has a flor.
truco-flor-cancels-envido = The envido is cancelled because of the flor.
truco-reveal-envido-you = The envido was won with your cards: { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.
truco-reveal-envido-player = The envido was won by { $player } with { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.
truco-reveal-flor-you = The flor was won with your cards: { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.
truco-reveal-flor-player = The flor was won by { $player } with { $cards }, worth { $value } { $value ->
    [one] point
   *[other] points
}.

# Envido and flor
truco-falta-envido-value = Falta envido is worth { $points } { $points ->
    [one] point
   *[other] points
}.
truco-falta-envido-game = Falta envido: both sides are in the malas, so the winner wins the whole game.

# Points and score
truco-reason-truco = the Truco
truco-reason-envido = the Envido
truco-reason-flor = the Flor
truco-reason-hand = the hand
truco-points-your-team = Your team scores { $points } { $points ->
    [one] point
   *[other] points
} for { $reason }.
truco-points-team = { $team } scores { $points } { $points ->
    [one] point
   *[other] points
} for { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] point
   *[other] points
}.
truco-half-buenas-your-team = Your team enters the buenas, the second half.
truco-half-buenas-team = { $team } enters the buenas, the second half.

# Information
truco-status-no-truco = No Truco has been called. The hand is worth { $points } { $points ->
    [one] point
   *[other] points
}.
truco-status-truco = The hand is at { $call }, worth { $points } { $points ->
    [one] point
   *[other] points
}.
truco-status-truco-pending = { $call } is waiting for an answer from { $team }.
truco-status-envido-open = Envido can still be called this hand.
truco-status-envido-closed = Envido is closed for this hand.
truco-table-empty = No cards have been played yet.
truco-table-trick = Trick { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Errors and disabled-action reasons
truco-error-bad-count = Truco needs 2, 4, or 6 players, but there are { $count }.
truco-error-team-mode-count = Team mode { $mode } cannot be used with { $count } players. Use Individual for 2 players, 2v2 for 4 players, or 3v3 for 6 players.
truco-error-not-your-turn = It is { $player }'s turn to play a card.
truco-error-answer-first = You must answer { $call } before doing anything else. Choose Quiero or No quiero, or raise.
truco-error-nothing-to-answer = There is no call waiting for your answer.
truco-error-own-team-call = Your team made that call. Wait for { $team } to answer { $call }.
truco-error-envido-late = Envido can only be called before you play your first card.
truco-error-envido-closed = Envido is closed because the Truco has already been accepted.
truco-error-envido-done = Envido has already been played this hand.
truco-error-raise-max = The Truco is already at Vale cuatro and cannot be raised.
truco-error-raise-holder = Your team made the last Truco call. Only { $team } can raise it now.
truco-error-flor-none = You have folded this hand, so you cannot call or answer.
truco-error-flor-holders-only = Only a player with a flor can answer or raise a flor.
truco-error-card-not-held = You do not hold that card.
truco-error-hand-over = The hand is already over.

# Game end
truco-game-win-you = You win the game with { $score } { $score ->
    [one] point
   *[other] points
}!
truco-game-win-player = { $player } wins the game with { $score } { $score ->
    [one] point
   *[other] points
}!
truco-game-win-your-team = Your team wins the game with { $score } { $score ->
    [one] point
   *[other] points
}!
truco-game-win-team = { $team } wins the game with { $score } { $score ->
    [one] point
   *[other] points
}!
truco-end-title = Truco results
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] point
   *[other] points
}.

# Additional errors and individual-mode messages
truco-error-flor-off = Flor is turned off in this game, so there is nothing to call or answer.
truco-error-flor-window = The flor has to be settled first. Truco cannot be called until the first card is played.
truco-error-flor-window-closed = Contraflor can only be called while both sides have a flor and before the first card is played.
truco-error-envido-flor = Envido is cancelled this hand because a player has a flor.
truco-error-envido-cannot-raise = { $call } cannot be added to the envido that is being played.
truco-points-you = You score { $points } { $points ->
    [one] point
   *[other] points
} for { $reason }.
truco-points-player = { $player } scores { $points } { $points ->
    [one] point
   *[other] points
} for { $reason }.
truco-half-buenas-you = You enter the buenas, the second half.
truco-half-buenas-player = { $player } enters the buenas, the second half.

# Card information, descriptions and touch gestures
truco-card-info-label = Item information
truco-card-info = { $card }: beats { $beats } of the other { $total } cards in this deck.
truco-card-info-envido = { $card }: beats { $beats } of the other { $total } cards in this deck. Envido value: { $value }.
truco-desc-call-ladder = { $call }: raises the hand to { $points } { $points ->
    [one] point
   *[other] points
}. If it is refused, the side that called wins { $refused } { $refused ->
    [one] point
   *[other] points
}.
truco-desc-call-envido = { $call }: both sides compare their envido. If it is accepted, the winner scores { $points } { $points ->
    [one] point
   *[other] points
}. If it is refused, the side that called scores { $refused } { $refused ->
    [one] point
   *[other] points
}.
truco-desc-call-flor = { $call }: the flor holders compare their flor. If it is accepted, the winner scores { $points } { $points ->
    [one] point
   *[other] points
}. If it is refused, the side that called scores { $refused } { $refused ->
    [one] point
   *[other] points
}.
truco-desc-accept = Accept { $call } and keep playing.
truco-desc-decline = Refuse { $call }. The other side scores { $points } { $points ->
    [one] point
   *[other] points
} and the hand ends.
truco-desc-mazo = Fold your cards. If everyone on your team has folded, the other side wins the hand.
truco-trick-tie-neutral = Trick { $trick } is tied.
