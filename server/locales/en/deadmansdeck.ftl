game-name-deadmansdeck = Dead Man's Deck

deadmansdeck-call-liar = Call liar
deadmansdeck-play-selected = Play selected cards
deadmansdeck-clear-selection = Clear selection
deadmansdeck-read-hand = Read hand
deadmansdeck-read-table = Read table
deadmansdeck-read-revolvers = Read revolvers
deadmansdeck-read-card-counts = Read card counts

deadmansdeck-rank-ace = Ace
deadmansdeck-rank-ace-plural = Aces
deadmansdeck-rank-king = King
deadmansdeck-rank-king-plural = Kings
deadmansdeck-rank-queen = Queen
deadmansdeck-rank-queen-plural = Queens
deadmansdeck-rank-joker = Joker
deadmansdeck-rank-joker-plural = Jokers
deadmansdeck-claim-text = { $count } { $rank }

deadmansdeck-card-label = { $card }
deadmansdeck-selected-card-label = Selected: { $card }
deadmansdeck-card-selected = Selected { $card }.
deadmansdeck-card-unselected = Unselected { $card }.
deadmansdeck-selection-cleared = Selection cleared.
deadmansdeck-card-not-found = That card is no longer available.
deadmansdeck-too-many-selected = You can claim at most three cards.
deadmansdeck-select-card-first = Select one to three cards first.
deadmansdeck-no-claim-to-challenge = There is no claim to challenge.
deadmansdeck-cannot-challenge-self = You cannot challenge your own claim.
deadmansdeck-action-sequence-running = Wait for the current sequence to finish.
deadmansdeck-action-eliminated = You have been eliminated.

deadmansdeck-prepare-revolver = The revolvers are being prepared.
deadmansdeck-round-start = Round { $round }. The table card is { $target }.
deadmansdeck-turn-order = Turn order this round: { $order }.
deadmansdeck-your-hand = Your hand: { $cards }.
deadmansdeck-hand-empty = Your hand is empty.
deadmansdeck-no-cards = no cards
deadmansdeck-you-skipped-no-cards = You have no cards and are skipped.
deadmansdeck-player-skipped-no-cards = { $player } has no cards and is skipped.
deadmansdeck-you-out-of-cards = You have no cards left.
deadmansdeck-player-out-of-cards = { $player } has no cards left.
deadmansdeck-you-forced-challenge = You must challenge because the round cannot continue.
deadmansdeck-forced-challenge = { $player } must challenge because the round cannot continue.
deadmansdeck-you-claim = You claim { $claim }.
deadmansdeck-player-claims = { $player } claims { $claim }.
deadmansdeck-you-call-liar = You call { $accused } a liar.
deadmansdeck-player-calls-liar = { $challenger } calls { $accused } a liar.
deadmansdeck-player-calls-you-liar = { $challenger } calls you a liar.
deadmansdeck-you-forced-liar-call = You are forced to call { $accused } a liar.
deadmansdeck-forced-liar-call = { $challenger } is forced to call { $accused } a liar.
deadmansdeck-forced-liar-call-you = { $challenger } is forced to call you a liar.
deadmansdeck-your-revealed-cards = Your revealed cards: { $cards }.
deadmansdeck-revealed-cards = { $player } revealed: { $cards }.
deadmansdeck-you-caught-bluff = You caught { $accused } bluffing. { $accused } must pull.
deadmansdeck-your-bluff-caught = { $challenger } caught your bluff. You must pull.
deadmansdeck-bluff-caught = { $challenger } caught { $accused } bluffing. { $accused } must pull.
deadmansdeck-you-wrong-challenge = { $accused } was truthful. You must pull.
deadmansdeck-your-truthful-claim = Your claim was truthful. { $challenger } must pull.
deadmansdeck-truthful-claim = { $accused } was truthful. { $challenger } must pull.
deadmansdeck-you-face-revolver = You face the revolver.
deadmansdeck-roulette-start = { $player } faces the revolver.
deadmansdeck-you-roulette-survived = Empty chamber. You survive. Your next pull has 1 in { $remaining } risk.
deadmansdeck-roulette-survived = Empty chamber. { $player } survives. { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } next pull has 1 in { $remaining } risk.
deadmansdeck-you-eliminated-by-gun = The gun fires. You have been eliminated.
deadmansdeck-player-eliminated = The gun fires. { $player } has been eliminated.
deadmansdeck-you-win-game = You are the last player standing and win Dead Man's Deck.
deadmansdeck-player-wins = { $player } is the last player standing and wins Dead Man's Deck.
deadmansdeck-no-winner = No winner could be determined.
deadmansdeck-you-are-eliminated = You have been eliminated from this game.

deadmansdeck-table-round = Round { $round }. Target: { $target }.
deadmansdeck-table-target-pending = not set yet
deadmansdeck-table-current-turn = Current turn: { $player }.
deadmansdeck-table-last-claim = Last claim: { $player } claimed { $claim }.
deadmansdeck-table-no-claim = There is no active claim.
deadmansdeck-table-alive = Still alive: { $players }.
deadmansdeck-table-eliminated = Eliminated: { $players }.

deadmansdeck-card-count-line = { $player }: { $count ->
    [one] 1 card
   *[other] { $count } cards
} left.
deadmansdeck-card-count-eliminated = { $player }: eliminated.

deadmansdeck-revolvers-header = Revolver status
deadmansdeck-revolver-status = { $player }: { $survived } empty chambers used; next pull is 1 in { $remaining }.
deadmansdeck-revolver-eliminated = { $player }: eliminated.

deadmansdeck-results-header = Dead Man's Deck results
deadmansdeck-results-winner = Winner: { $player }.
deadmansdeck-results-survived = survived
deadmansdeck-results-eliminated = eliminated
deadmansdeck-results-line = { $player }: { $status }, correct calls { $correct }, successful bluffs { $bluffs }, roulette survivals { $survivals }.
