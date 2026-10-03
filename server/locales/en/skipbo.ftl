game-name-skipbo = Skip-Bo

skipbo-stock-mode-standard = Standard (30 or 20 cards)
skipbo-stock-mode-short = Quick 10 cards
skipbo-stock-mode-short-15 = Quick 15 cards
skipbo-scoring-single = Single game
skipbo-scoring-match = Scored match

skipbo-set-stock-mode = Stock piles: { $mode }
skipbo-select-stock-mode = Select the stock pile length:
skipbo-option-changed-stock-mode = Stock piles now use { $mode }.
skipbo-desc-stock-mode = Standard uses 30 stock cards with 2 to 4 players and 20 with 5 or 6 players. Quick games use 10 or 15 stock cards for every player.

skipbo-set-scoring-mode = Match format: { $mode }
skipbo-select-scoring-mode = Select the match format:
skipbo-option-changed-scoring-mode = The match format is now { $mode }.
skipbo-desc-scoring-mode = Single game ends when one player or partnership empties its stock piles. Scored match continues across games until someone reaches the target score.

skipbo-set-winning-score = Match target: { $score } points
skipbo-enter-winning-score = Enter the match target from 25 to 5000 points:
skipbo-option-changed-winning-score = The match target is now { $score } points.
skipbo-desc-winning-score = Points needed to win a scored match. The official target is 500 points.
skipbo-desc-team-mode = Individual gives every player a separate stock pile and score. Official partnerships use teams of two; partners may play from either partner's stock and discard piles, but never from each other's hands.

skipbo-card-number = { $value }
skipbo-card-wild = Skip-Bo wild
skipbo-card-wild-as = Skip-Bo as { $value }

skipbo-source-your-hand = your hand
skipbo-source-player-hand = { $owner }'s hand
skipbo-source-your-stock = your stock pile
skipbo-source-player-stock = { $owner }'s stock pile
skipbo-source-your-discard = your discard pile { $pile }
skipbo-source-player-discard = { $owner }'s discard pile { $pile }

skipbo-action-source-hand = hand
skipbo-action-source-stock = stock
skipbo-action-source-player-stock = { $owner }'s stock
skipbo-action-source-discard = discard pile { $pile }
skipbo-action-source-player-discard = { $owner }'s discard pile { $pile }

skipbo-play-action = { $card } — { $source } to pile { $pile }
skipbo-card-action = { $card } — { $source }
skipbo-card-desc-play-or-discard = Available building piles: { $piles }. Choose the card to play it or discard it and end your turn.
skipbo-card-desc-discard-only = Choose the card to discard it and end your turn.
skipbo-card-desc-choose-building = Available building piles: { $piles }. Choose the card to select one.
skipbo-end-turn-empty = End turn without discarding
skipbo-end-turn-empty-desc = Your hand is empty and no cards can be drawn, so no discard is possible.
skipbo-select-card-move = Choose where to move this card:
skipbo-move-building-empty = Building pile { $pile}: empty; play { $card }
skipbo-move-building-top = Building pile { $pile}: { $current } on top; play { $card }
skipbo-move-discard-empty = Discard pile { $pile}: empty; discard here and end turn
skipbo-move-discard-top = Discard pile { $pile}: { $top } on top; discard here and end turn

skipbo-read-building-piles = View building piles
skipbo-read-stock-piles = View stock piles
skipbo-read-own-discard-piles = View your discard piles
skipbo-read-discard-piles = View another player's discard piles
skipbo-select-discard-owner = Choose whose discard piles to view:

skipbo-game-start = The game begins. Each stock pile has { $stock_count } cards.
skipbo-game-start-quick = The quick game begins. Each stock pile has { $stock_count } cards.
skipbo-match-game-start = Scored game { $game } begins. Each stock pile has { $stock_count } cards.
skipbo-match-game-start-quick = Quick scored game { $game } begins. Each stock pile has { $stock_count } cards.
skipbo-initial-stock-you = Your face-up stock card is { $card }.
skipbo-initial-stock-player = { $player }'s face-up stock card is { $card }.
skipbo-draw-turn-you = You draw { $count } { $count ->
    [one] card
   *[other] cards
} to begin your turn. Your hand is { $hand }.
skipbo-draw-turn-player = { $player } draws { $count } { $count ->
    [one] card
   *[other] cards
} to begin { GENDER_TERM($player_gender, "possessive-determiner") } turn.
skipbo-refill-you = You used every card in your hand, so you immediately draw { $count } { $count ->
    [one] card
   *[other] cards
}. Your hand is { $hand }.
skipbo-refill-player = { $player } used every card in { GENDER_TERM($player_gender, "possessive-determiner") } hand and immediately draws { $count } { $count ->
    [one] card
   *[other] cards
}.
skipbo-no-refill-you = Your hand is empty, and no cards are available to draw.
skipbo-no-refill-player = { $player } has an empty hand, but no cards are available to draw.
skipbo-recycle-completed = The draw pile is empty. Completed building piles are shuffled to make a new draw pile with { $count } cards.

skipbo-play-you = You play { $card } from { $source } to building pile { $pile }.
skipbo-play-player = { $player } plays { $card } from { $source } to building pile { $pile }.
skipbo-complete-building-you = You complete building pile { $pile } at 12. Its cards are set aside for reshuffling, and the building slot is empty again.
skipbo-complete-building-player = { $player } completes building pile { $pile } at 12. Its cards are set aside for reshuffling, and the building slot is empty again.
skipbo-next-stock-you = Your next face-up stock card is { $card }; { $count } { $count ->
    [one] card remains
   *[other] cards remain
} in your stock pile.
skipbo-next-stock-player = { $player }'s next face-up stock card is { $card }; that stock pile has { $count } { $count ->
    [one] card remains
   *[other] cards remain
}.
skipbo-stock-cleared-you = Your stock pile is now empty. Your partnership still needs to empty the other stock pile.
skipbo-stock-cleared-player = { $player }'s stock pile is now empty. The partnership still needs to empty its other stock pile.
skipbo-discard-you = You discard { $card } onto discard pile { $pile } and end your turn.
skipbo-discard-player = { $player } discards { $card } onto discard pile { $pile } and ends { GENDER_TERM($player_gender, "possessive-determiner") } turn.
skipbo-empty-end-you = You have no card available to discard, so you end your turn without one.
skipbo-empty-end-player = { $player } has no card available to discard and ends { GENDER_TERM($player_gender, "possessive-determiner") } turn without one.

skipbo-single-win-you = You empty your stock pile and win the game.
skipbo-single-win-player = { $player } empties { GENDER_TERM($player_gender, "possessive-determiner") } stock pile and wins the game.
skipbo-single-win-team-you = Your partnership empties both stock piles and wins the game.
skipbo-single-win-team = Team { $team } empties both stock piles and wins the game.
skipbo-scored-game-win-you = You empty your stock pile and win scored game { $game }, earning { $points } points with { $remaining } left across opposing stock piles. Your match total is { $total }.
skipbo-scored-game-win-player = { $player } empties { GENDER_TERM($player_gender, "possessive-determiner") } stock pile and wins scored game { $game }, earning { $points } points with { $remaining } left across opposing stock piles. The match total is { $total }.
skipbo-scored-game-win-team-you = Your partnership empties both stock piles and wins scored game { $game }, earning { $points } points with { $remaining } left across opposing stock piles. Your match total is { $total }.
skipbo-scored-game-win-team = Team { $team } empties both stock piles and wins scored game { $game }, earning { $points } points with { $remaining } left across opposing stock piles. The team's match total is { $total }.
skipbo-next-round = The next scored game will begin shortly. The starting position moves one seat forward.
skipbo-match-win-you = You win the Skip-Bo match with { $score } points.
skipbo-match-win-player = { $player } wins the Skip-Bo match with { $score } points.
skipbo-match-win-team-you = Your partnership wins the Skip-Bo match with { $score } points.
skipbo-match-win-team = Team { $team } wins the Skip-Bo match with { $score } points.

skipbo-building-empty = Building pile { $pile }: empty; needs 1.
skipbo-building-top = Building pile { $pile }: { $value } on top; needs { $needed }.
skipbo-draw-count = Draw pile: { $draw_count } cards. Completed building cards waiting to be reshuffled: { $recycle_count }.
skipbo-stock-empty = { $player }'s stock pile: empty.
skipbo-stock-status = { $player }'s stock pile: { $card } face up, { $count } { $count ->
    [one] card total
   *[other] cards total
}.
skipbo-discard-your-header = Your discard piles:
skipbo-discard-player-header = { $player }'s discard piles:
skipbo-discard-empty = Discard pile { $pile }: empty.
skipbo-discard-top = Discard pile { $pile }: { $card } on top, { $count } { $count ->
    [one] card total
   *[other] cards total
}.
skipbo-hand-empty = You do not have any cards in hand yet.
skipbo-hand-menu-card = Hand: { $card }

skipbo-error-invalid-stock-mode = The selected stock pile length is not supported. Choose Standard, Quick 10, or Quick 15.
skipbo-error-invalid-scoring-mode = The selected match format is not supported. Choose Single game or Scored match.
skipbo-error-winning-score-range = The match target must be from { $min } to { $max } points; it is currently { $value }.
skipbo-error-partnership-player-count = Partnerships require exactly 4 players for two partnerships or 6 players for three partnerships.
skipbo-error-game-not-active = This Skip-Bo game is not currently active.
skipbo-error-round-transition = The current game has ended. Wait for the next game to begin.
skipbo-error-card-move-selection-you = Choose where to move the selected card first.
skipbo-error-play-changed = That play is no longer available because the card or building pile changed. Choose a current turn-menu action.
skipbo-error-card-changed = That card is no longer available. Choose a current turn-menu action.
skipbo-error-cards-available = You still have a card available to discard. End your turn by choosing that card and one of your four discard piles.
skipbo-error-no-discard-targets = No other player's discard piles are available.
skipbo-error-discard-target-changed = That player's discard piles are no longer available. Choose a current player.
skipbo-discard-owner-unavailable = Player no longer available

skipbo-result-line = { $rank }. { $player }: { $points }
