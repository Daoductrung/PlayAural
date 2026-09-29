# Blackjack

game-name-blackjack = Blackjack

blackjack-set-rules-profile = Rules profile: { $profile }
blackjack-select-rules-profile = Select rules profile
blackjack-option-changed-rules-profile = Rules profile set to { $profile }.
blackjack-desc-rules-profile = Applies a preset Blackjack rules package: Vegas, European, or Friendly.

blackjack-set-starting-chips = Starting chips: { $count }
blackjack-enter-starting-chips = Enter starting chips
blackjack-option-changed-starting-chips = Starting chips set to { $count }.
blackjack-desc-starting-chips = How many chips each player starts with at the Blackjack table (default 500, range 50-1000000).

blackjack-set-base-bet = Base bet: { $count }
blackjack-enter-base-bet = Enter base bet
blackjack-option-changed-base-bet = Base bet set to { $count }.
blackjack-desc-base-bet = The default bet offered between Blackjack hands (default 10, range 1-100000).
blackjack-enter-bet = Enter your chip bet
blackjack-option-changed-bet = Bet set to { $count } chips.

blackjack-set-table-min-bet = Table minimum bet: { $count }
blackjack-enter-table-min-bet = Enter table minimum bet
blackjack-option-changed-table-min-bet = Table minimum bet set to { $count }.
blackjack-desc-table-min-bet = The smallest allowed Blackjack bet (default 5, range 1-100000).

blackjack-set-table-max-bet = Table maximum bet: { $count }
blackjack-enter-table-max-bet = Enter table maximum bet
blackjack-option-changed-table-max-bet = Table maximum bet set to { $count }.
blackjack-desc-table-max-bet = The largest allowed Blackjack bet (default 100, range 1-100000).

blackjack-set-deck-count = Deck count: { $count }
blackjack-enter-deck-count = Enter deck count
blackjack-option-changed-deck-count = Deck count set to { $count }.
blackjack-desc-deck-count = How many standard 52-card decks are shuffled into the Blackjack shoe (default 4, range 1-8).

blackjack-set-dealer-soft-17 = Dealer hits soft 17: { $enabled }
blackjack-option-changed-dealer-soft-17 = Dealer hits soft 17 set to { $enabled }.
blackjack-desc-dealer-hits-soft-17 = Controls whether the dealer must draw on soft 17, such as Ace plus 6.

blackjack-set-dealer-peek-blackjack = Dealer peeks for blackjack: { $enabled }
blackjack-option-changed-dealer-peek-blackjack = Dealer peek for blackjack set to { $enabled }.
blackjack-desc-dealer-peeks-blackjack = Controls whether the dealer checks for Blackjack when showing an Ace or ten-value card.

blackjack-set-players-cards-face-up = Player cards face up: { $enabled }
blackjack-option-changed-players-cards-face-up = Player cards face up set to { $enabled }.
blackjack-desc-players-cards-face-up = Controls whether player cards are public to the whole table.

blackjack-set-allow-insurance = Offer insurance and even money: { $enabled }
blackjack-option-changed-allow-insurance = Insurance and even money set to { $enabled }.
blackjack-desc-allow-insurance = Controls whether insurance and even-money choices are offered when the dealer shows an Ace.

blackjack-set-allow-late-surrender = Allow late surrender: { $enabled }
blackjack-option-changed-allow-late-surrender = Late surrender set to { $enabled }.
blackjack-desc-allow-late-surrender = Controls whether players may surrender before hitting; this requires dealer peek rules.

blackjack-set-blackjack-payout = Blackjack payout: { $mode }
blackjack-select-blackjack-payout = Select blackjack payout
blackjack-option-changed-blackjack-payout = Blackjack payout set to { $mode }.
blackjack-desc-blackjack-payout = Sets the payout for a natural Blackjack: 3 to 2, 6 to 5, or even money.

blackjack-set-double-down-rule = Double down rule: { $mode }
blackjack-select-double-down-rule = Select double down rule
blackjack-option-changed-double-down-rule = Double down rule set to { $mode }.
blackjack-desc-double-down-rule = Controls which starting totals may double down: any two cards, 9-11 only, or 10-11 only.

blackjack-set-allow-double-after-split = Double after split: { $enabled }
blackjack-option-changed-allow-double-after-split = Double after split set to { $enabled }.
blackjack-desc-allow-double-after-split = Controls whether split hands may double down.

blackjack-set-split-rule = Split rule: { $mode }
blackjack-select-split-rule = Select split rule
blackjack-option-changed-split-rule = Split rule set to { $mode }.
blackjack-desc-split-rule = Controls whether a split requires the same exact rank or only the same card value.

blackjack-set-max-split-hands = Maximum split hands: { $count }
blackjack-enter-max-split-hands = Enter maximum split hands
blackjack-option-changed-max-split-hands = Maximum split hands set to { $count }.
blackjack-desc-max-split-hands = Maximum number of hands a player may create by splitting (default 2, range 1-2).

blackjack-set-split-aces-one-card = Split aces draw one card only: { $enabled }
blackjack-option-changed-split-aces-one-card = Split aces one-card rule set to { $enabled }.
blackjack-desc-split-aces-one-card-only = Controls whether each split Ace receives exactly one card and then stands.

blackjack-set-split-aces-blackjack = Split aces can count as blackjack: { $enabled }
blackjack-option-changed-split-aces-blackjack = Split aces blackjack rule set to { $enabled }.
blackjack-desc-split-aces-count-as-blackjack = Controls whether Ace plus ten-value after splitting Aces counts as a natural Blackjack.

blackjack-set-turn-timer = Turn timer: { $mode }
blackjack-select-turn-timer = Select turn timer
blackjack-option-changed-turn-timer = Turn timer set to { $mode }.
blackjack-desc-turn-timer = Optional time limit for each Blackjack decision; choose Unlimited for no timer.

blackjack-rules-profile-vegas = Vegas
blackjack-rules-profile-european = European
blackjack-rules-profile-friendly = Friendly
blackjack-payout-3-to-2 = 3 to 2
blackjack-payout-6-to-5 = 6 to 5
blackjack-payout-1-to-1 = 1 to 1
blackjack-double-rule-any-two = Any two cards
blackjack-double-rule-9-to-11 = Totals 9 to 11
blackjack-double-rule-10-to-11 = Totals 10 to 11
blackjack-split-rule-same-value = Same value
blackjack-split-rule-same-rank = Same rank

blackjack-hit = Hit
blackjack-stand = Stand
blackjack-double-down = Double down
blackjack-split = Split
blackjack-surrender = Surrender
blackjack-take-insurance = Take insurance
blackjack-decline-insurance = Decline insurance
blackjack-even-money = Take even money
blackjack-read-hand = Read hand
blackjack-read-dealer = Read dealer
blackjack-read-bets = Read bets
blackjack-table-status = Table status
blackjack-read-rules = Read rules

blackjack-not-player-phase = Players are not taking actions right now.
blackjack-not-insurance-phase = Insurance decisions are not active right now.
blackjack-hand-complete = Your hand is complete.
blackjack-error-bet-too-high = Base bet cannot be higher than starting chips.
blackjack-error-starting-chips-below-min = Starting chips cannot be lower than the table minimum bet.
blackjack-error-table-limits-invalid = Table minimum bet cannot be higher than table maximum bet.
blackjack-error-bet-below-min = Bet cannot be lower than the table minimum bet.
blackjack-error-bet-above-max = Bet cannot be higher than the table maximum bet.
blackjack-error-bet-above-chips = You cannot bet more chips than you have.
blackjack-error-late-surrender-requires-peek = Late surrender requires dealer peek for blackjack to be enabled.
blackjack-cannot-split = You cannot split this hand.
blackjack-cannot-double-down = You cannot double down right now.
blackjack-cannot-surrender = You cannot surrender this hand.
blackjack-insurance-closed = You cannot make an insurance decision right now.
blackjack-cannot-insure = You cannot take insurance right now.
blackjack-cannot-even-money = You cannot take even money right now.
blackjack-bet-already-locked = Your bet is already locked for this hand.
blackjack-out-of-chips = You are out of chips.

blackjack-hand-start = Hand { $hand }. Place your bets.
blackjack-you-bet = You bet { $amount }.
blackjack-player-bets = { $player } bets { $amount }.
blackjack-bet-locked = Bet locked at { $amount } chips.
blackjack-insurance-offer = Insurance is open.
blackjack-insurance-prompt = Insurance available. You may insure for { $amount } chips or decline.
blackjack-insurance-prompt-player = Insurance decision for { $player }.
blackjack-insurance-prompt-even-money = You can take even money now.
blackjack-insurance-prompt-even-money-player = { $player } can take even money.

blackjack-dealer-shows = Dealer shows { $card }.
blackjack-dealer-reveals = Dealer reveals { $card }, for a total of { $total }.
blackjack-dealer-hits = Dealer draws { $card }, for a total of { $total }.
blackjack-dealer-stands = Dealer stands with { $total }.
blackjack-dealer-bust = Dealer busts with { $total }.
blackjack-dealer-blackjack = Dealer has blackjack.

blackjack-you-have = You have { $cards } ({ $total }).
blackjack-player-has = { $player } has { $cards } ({ $total }).
blackjack-you-blackjack = You have blackjack.
blackjack-player-blackjack = { $player } has blackjack.

blackjack-you-hit = You draw { $card }.
blackjack-player-hits = { $player } draws { $card }.
blackjack-you-stand = You stand.
blackjack-player-stands = { $player } stands.
blackjack-you-double-down = You double down by { $amount } chips.
blackjack-player-double-downs = { $player } doubles down by { $amount } chips.
blackjack-you-split = You split your hand and add { $amount } chips.
blackjack-player-splits = { $player } splits { GENDER_TERM($player_gender, "possessive-determiner") } hand and adds { $amount } chips.
blackjack-you-surrender = You surrender and lose { $amount } chips.
blackjack-player-surrenders = { $player } surrenders and loses { $amount } chips.
blackjack-you-take-insurance = You place an insurance bet of { $amount } chips.
blackjack-player-takes-insurance = { $player } places an insurance bet of { $amount } chips.
blackjack-you-decline-insurance = You decline insurance.
blackjack-player-declines-insurance = { $player } declines insurance.
blackjack-you-take-even-money = You take even money.
blackjack-player-takes-even-money = { $player } takes even money.
blackjack-you-split-aces-auto-stand = Split aces draw one card each and stand automatically.
blackjack-player-splits-aces-auto-stand = { $player } splits aces and both hands stand.
blackjack-you-stand-auto = You stand on 21.
blackjack-player-stands-auto = { $player } stands on 21.
blackjack-you-bust = You bust with { $total }.
blackjack-player-bust = { $player } busts with { $total }.
blackjack-your-total = Your total is { $total }.
blackjack-player-total = { $player } has { $total }.
blackjack-your-total-hand = Hand { $hand }: { $total }.
blackjack-player-total-hand = { $player } hand { $hand }: { $total }.

blackjack-you-win = You win { $amount } chips.
blackjack-player-wins = { $player } wins { $amount } chips.
blackjack-you-even-money-win = Even money pays { $amount } chips.
blackjack-player-even-money-win = { $player } is paid { $amount } chips for even money.
blackjack-you-lose = You lose { $amount } chips.
blackjack-player-loses = { $player } loses { $amount } chips.
blackjack-you-push = Push.
blackjack-player-push = { $player } pushes.
blackjack-you-win-hand = Hand { $hand }: You win { $amount } chips.
blackjack-player-wins-hand = { $player } hand { $hand } wins { $amount } chips.
blackjack-you-lose-hand = Hand { $hand }: You lose { $amount } chips.
blackjack-player-loses-hand = { $player } hand { $hand } loses { $amount } chips.
blackjack-you-push-hand = Hand { $hand }: Push.
blackjack-player-push-hand = { $player } hand { $hand } pushes.
blackjack-you-insurance-wins = Insurance wins { $amount } chips.
blackjack-player-insurance-wins = { $player } wins { $amount } chips from insurance.
blackjack-you-insurance-loses = Insurance loses { $amount } chips.
blackjack-player-insurance-loses = { $player } loses an insurance bet of { $amount } chips.
blackjack-you-broke = You are out of chips.
blackjack-player-broke = { $player } is out of chips.
blackjack-you-win-game = You win the game with { $chips } chips.
blackjack-player-wins-game = { $player } wins the game with { $chips } chips.

blackjack-total-soft = { $total } soft
blackjack-total-hard = { $total }

blackjack-read-hand-response = Your hand is { $cards } ({ $total }).
blackjack-read-hand-response-split = Hand 1: { $hand1 } ({ $total1 }). Hand 2: { $hand2 } ({ $total2 }). Active hand: { $active }.
blackjack-no-hand = You are not in the current hand.
blackjack-no-dealer-cards = The dealer has no cards yet.
blackjack-read-dealer-up = Dealer shows { $card }.
blackjack-read-dealer-full = Dealer has { $cards } ({ $total }).
blackjack-rule-yes = yes
blackjack-rule-no = no
blackjack-rules-readout = Rules: profile { $profile }. Table limits { $min_bet } to { $max_bet }, base bet { $base_bet }. Dealer hits soft 17: { $soft_17 }. Dealer peeks blackjack: { $peek }. Player cards face up: { $players_cards_face_up }. Insurance and even money: { $insurance }. Late surrender: { $surrender }. Blackjack payout: { $payout }. Double-down rule: { $double_rule }. Double after split: { $das }. Split rule: { $split_rule }. Max split hands: { $split_hands }. Split aces one-card rule: { $split_aces_one }. Split aces blackjack: { $split_aces_blackjack }.

blackjack-status-line = { $player }: { $chips } chips
blackjack-status-line-out = { $player }: out of chips
blackjack-status-line-bet = { $player }: { $chips } chips, bet { $bet }
blackjack-status-line-hand = { $player }: { $chips } chips, bet { $bet }, total { $total }
blackjack-status-line-hands = { $player }: { $chips } chips, hand 1 bet { $bet1 } total { $total1 }, hand 2 bet { $bet2 } total { $total2 }
blackjack-status-dealer = Dealer: { $cards } ({ $total })
blackjack-status-dealer-up = Dealer: showing { $card }
blackjack-no-active-players = No active players.
blackjack-waiting-for-bets = Waiting for bets from { $players }.
blackjack-bet-previous-label = Bet { $amount }
blackjack-end-screen-line = { $rank }. { $player }: { $chips } { $chips ->
    [one] chip
   *[other] chips
}
blackjack-change-bet = Change bet
