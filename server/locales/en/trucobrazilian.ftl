# Options
trucobrazilian-desc-team-mode = Individual is a one-on-one game for 2 players. 2v2 uses 4 players and 3v3 uses 6 players; partners share the score and may call for the whole team.

# French deck
trucobrazilian-rank-ace = Ace
trucobrazilian-rank-jack = Jack
trucobrazilian-rank-queen = Queen
trucobrazilian-rank-king = King
trucobrazilian-suit-diamonds = Diamonds
trucobrazilian-suit-spades = Spades
trucobrazilian-suit-hearts = Hearts
trucobrazilian-suit-clubs = Clubs
trucobrazilian-card-name = { $rank } of { $suit }

# Calls
trucobrazilian-call-truco = Truco
trucobrazilian-call-seis = Seis
trucobrazilian-call-nove = Nove
trucobrazilian-call-doze = Doze
trucobrazilian-call-onze = Mão de onze

# Actions and information
trucobrazilian-action-onze-play = Jogar (play the hand)
trucobrazilian-action-onze-run = Correr (run and give up the hand)
trucobrazilian-read-vira = Read the vira and manilha
trucobrazilian-no-vira = No vira has been turned up yet.
trucobrazilian-vira = The vira is { $card }. The manilha is { $manilha }.
trucobrazilian-vira-is = The vira is { $card }. The manilha is { $manilha }.

# Game flow
trucobrazilian-game-start = Brazilian Truco begins. The first side to reach { $points } points wins. Each hand, a turned-up card called the vira decides the manilhas.
trucobrazilian-onze-your-team = Your team has 11 points: mão de onze. Choose Jogar to play the hand for 3 points with no calls, or Correr to give the other side 1 point.
trucobrazilian-onze-team = { $team } has 11 points and is deciding whether to play the mão de onze.
trucobrazilian-onze-play-you = You play the mão de onze. The hand is worth 3 points and no calls are allowed.
trucobrazilian-onze-play-player = { $player } plays the mão de onze. The hand is worth 3 points and no calls are allowed.
trucobrazilian-onze-run-you = You run. The other side scores 1 point.
trucobrazilian-onze-run-player = { $player } runs. The other side scores 1 point.
trucobrazilian-ferro = Both sides have 11 points: mão de ferro. No calls are allowed and whoever wins the hand wins the game.
trucobrazilian-reason-onze-run = the run in the mão de onze
trucobrazilian-hand-annulled = All three tricks were tied. The hand is annulled and nobody scores.

# Errors and descriptions
trucobrazilian-error-onze-pending = { $team } must first decide whether to play the mão de onze.
trucobrazilian-error-no-calls = Calling is not allowed in this hand because it is a mão de onze or a mão de ferro.
trucobrazilian-desc-onze-play = Play the hand. It is worth { $points } { $points ->
    [one] point
   *[other] points
} and no calls are allowed.
trucobrazilian-desc-onze-run = Run and give up the hand. The other side scores 1 point.

trucobrazilian-action-accept = Aceito (accept)
trucobrazilian-action-decline = Correr (refuse and run)
trucobrazilian-accept-you = You say Aceito to { $call }.
trucobrazilian-accept-player = { $player } says Aceito to { $call }.
trucobrazilian-decline-you = You run from { $call }.
trucobrazilian-decline-player = { $player } runs from { $call }.
trucobrazilian-pending-answer = { $player } called { $call }. Answer with Aceito or Correr, or raise.
trucobrazilian-error-answer-first = You must answer { $call } before doing anything else. Choose Aceito or Correr, or raise.
trucobrazilian-error-raise-max = Doze is already the highest call and cannot be raised.
trucobrazilian-status-onze-pending = { $team } must decide whether to play the mão de onze.
trucobrazilian-status-no-calls = Calls are not allowed in this hand. The hand is worth { $points } { $points ->
    [one] point
   *[other] points
}.

# Mão de ferro (both sides at 11) is played face down; mão de onze partners see each other's cards
trucobrazilian-blind-cards = Mão de ferro: your { $count } cards are face down and you cannot see them. Choose them by position; each one is revealed when it is played.
trucobrazilian-blind-hand = Mão de ferro: you hold { $count } face-down { $count ->
    [one] card
   *[other] cards
}, and you cannot see { $count ->
    [one] it
   *[other] them
}.
trucobrazilian-action-play-blind = Play face-down card { $number }
trucobrazilian-desc-blind-card = A face-down card. You will not see it until it is played.
trucobrazilian-onze-partner-cards = Your partner { $partner } shows you their cards: { $cards }.
