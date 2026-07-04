game-name-tienlen = Tien Len

tienlen-set-variant = Variant: { $choice }
tienlen-select-variant = Select Tien Len variant:
tienlen-option-changed-variant = Variant set to { $choice }.
tienlen-desc-variant = Chooses Southern or Northern Tiến Lên rules.

tienlen-set-coin-target = Starting coins: { $choice }
tienlen-select-coin-target = Select starting coins:
tienlen-option-changed-coin-target = Starting coins set to { $choice }.
tienlen-desc-match-length = Starting bankroll for each player. Settlements use 10-coin stake units; players at 0 coins are eliminated.

tienlen-set-turn-timer = Turn Timer: { $choice }
tienlen-select-turn-timer = Select turn timer duration:
tienlen-option-changed-turn-timer = Turn timer set to { $choice }.
tienlen-desc-turn-timer = Optional time limit for each Tiến Lên turn: Unlimited, 10, 15, 20, 30, 45, 60, or 90 seconds (default Unlimited).

tienlen-variant-south = Southern Tien Len
tienlen-variant-north = Northern Tien Len
tienlen-target-20 = 20 coins
tienlen-target-50 = 50 coins
tienlen-target-100 = 100 coins
tienlen-target-200 = 200 coins

tienlen-timer-10 = 10 Seconds
tienlen-timer-15 = 15 Seconds
tienlen-timer-20 = 20 Seconds
tienlen-timer-30 = 30 Seconds
tienlen-timer-45 = 45 Seconds
tienlen-timer-60 = 60 Seconds
tienlen-timer-90 = 90 Seconds
tienlen-timer-unlimited = Unlimited

tienlen-game-start = Starting Tien Len.
tienlen-new-hand = Hand { $round }.
tienlen-dealt = Dealt 13 cards: { $cards }.
tienlen-variant-status = This table is playing { $variant }.

tienlen-card-unselected = { $card }
tienlen-card-selected = { $card } (selected)

tienlen-play-none = Select cards to play.
tienlen-play-invalid = Invalid combination.
tienlen-play-combo = Play { $combo }

tienlen-pass = Pass
tienlen-confirm-pass = Passing locks you out of the current trick. Press Pass again within 10 seconds to confirm.
tienlen-check-trick = Check trick
tienlen-read-hand = Read hand
tienlen-read-card-counts = Read card counts
tienlen-check-variant = Check variant
tienlen-check-turn-timer = Check turn timer
tienlen-timer-disabled = The turn timer is disabled.
tienlen-timer-remaining = { $seconds } seconds remaining.

tienlen-error-no-cards = You have not selected any cards.
tienlen-error-invalid-combo = The selected cards do not form a valid Tien Len combination for this variant.
tienlen-error-pass-lock = You already passed on this trick and must wait until the table clears.
tienlen-error-pass-lock-chop = You already passed on this trick. You may only return with a legal chop against the current 2s or chopping combination.
tienlen-error-wrong-length = You must play exactly { $count } cards to answer the current trick.
tienlen-error-must-match-type = Your play must match the current trick's combination type unless it is a legal chop.
tienlen-error-structure-mismatch = In Northern Tien Len, your play must match the suit or color structure of the current trick.
tienlen-error-lower-combo = Your combination does not beat the current trick.
tienlen-error-must-play = You cannot pass when starting a new trick.
tienlen-error-cannot-finish-on-two = In Northern Tien Len, you cannot finish the hand with 2s or leave only 2s behind.
tienlen-error-not-your-turn-chop = It is not your turn. In Southern Tien Len you may only jump in with a selected legal chop.
tienlen-error-already-finished = You have already finished this hand.
tienlen-error-opening-card-required = The opening play must include { $card }.
tienlen-error-invalid-variant = Select a supported Tien Len variant.
tienlen-error-invalid-starting-coins = Select a supported starting coin amount.
tienlen-error-invalid-turn-timer = Select a supported turn timer.

tienlen-you-play-single = You play { $card }.
tienlen-player-plays-single = { $player } plays { $card }.
tienlen-you-play-combo = You play { $combo }: { $cards }.
tienlen-player-plays-combo = { $player } plays { $combo }: { $cards }.
tienlen-you-one-card = You have one card left.
tienlen-one-card = { $player } has one card left.
tienlen-you-pass = You pass and are locked out until this trick clears.
tienlen-player-passes = { $player } passes and is locked out until this trick clears.
tienlen-you-chop-payment = You chop { $player }. { $amount } coins pending.
tienlen-you-are-chopped-payment = { $player } chops you. { $amount } coins pending.
tienlen-player-chop-payment = { $chopper } chops { $chopped }. { $amount } coins pending.
tienlen-you-leftover-penalty = You pay { $amount } coins for leftover 2s or chopping cards.
tienlen-player-leftover-penalty = { $player } pays { $amount } coins for leftover 2s or chopping cards.
tienlen-you-finish-place = You emptied your hand and take place { $place } for this hand.
tienlen-player-finishes-place = { $player } empties their hand and takes place { $place } for this hand.
tienlen-trick-empty = The trick is empty.
tienlen-trick-status = { $player } is leading with { $combo }: { $cards }.
tienlen-your-hand = Your hand: { $cards }.
tienlen-card-count-line = { $player } has { $count } cards
tienlen-card-count-eliminated-line = { $player } is eliminated

tienlen-combo-single = single
tienlen-combo-pair = pair
tienlen-combo-triple = triple
tienlen-combo-four_of_a_kind = four of a kind
tienlen-combo-straight = straight
tienlen-combo-consecutive_pairs = consecutive pairs

tienlen-instant-six-pairs = six pairs
tienlen-instant-five-consecutive-pairs = five consecutive pairs
tienlen-instant-three-consecutive-triples = three consecutive triples
tienlen-instant-four-twos = four 2s
tienlen-instant-dragon = dragon straight
tienlen-instant-six-consecutive-pairs = six consecutive pairs
tienlen-instant-four-triples = four triples
tienlen-instant-two-four-of-a-kind = two four-of-a-kind sets
tienlen-instant-same-color = 12 cards of one color
tienlen-you-instant-win = You have an instant win with { $reason }.
tienlen-player-instant-wins = { $player } has an instant win with { $reason }.
tienlen-you-win-hand = You take first place for this hand. Coin settlement follows.
tienlen-player-wins-hand = { $player } takes first place for this hand. Coin settlement follows.
tienlen-hand-settlement-line = Place { $place }: { $player } { $change } coins, now { $total } coins.
tienlen-you-eliminated = You are out of coins and eliminated.
tienlen-player-eliminated = { $player } is out of coins and eliminated.
tienlen-players-remaining = { $count ->
    [one] 1 player remains.
   *[other] { $count } players remain.
}
tienlen-you-win-match = You win the Tien Len match with { $coins } coins left.
tienlen-player-wins-match = { $player } wins the Tien Len match with { $coins } coins left.
tienlen-line-format = { $rank }. { $player }: { $score ->
    [one] 1 coin
   *[other] { $score } coins
}

tienlen-south-card-name = { $rank } of { $suit }
tienlen-south-rank-1 = Ace
tienlen-south-rank-2 = 2
tienlen-south-rank-3 = 3
tienlen-south-rank-4 = 4
tienlen-south-rank-5 = 5
tienlen-south-rank-6 = 6
tienlen-south-rank-7 = 7
tienlen-south-rank-8 = 8
tienlen-south-rank-9 = 9
tienlen-south-rank-10 = 10
tienlen-south-rank-11 = Jack
tienlen-south-rank-12 = Queen
tienlen-south-rank-13 = King
tienlen-south-suit-1 = Diamonds
tienlen-south-suit-2 = Clubs
tienlen-south-suit-3 = Hearts
tienlen-south-suit-4 = Spades
