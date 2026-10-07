game-name-flip7 = Flip 7

# Options
flip7-set-target-score = Target score: { $score }
flip7-enter-target-score = Enter target score
flip7-option-changed-target = Target score set to { $score }.
flip7-desc-target-score = The score that triggers a win check after a round. The highest total wins; a tied lead continues the match. Default: 200, range 50-1000.

# Cards
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Double
flip7-card-second-chance = Second Chance
flip7-card-freeze = Freeze
flip7-card-flip-three = Flip Three

# Turn actions
flip7-hit = Flip a card
flip7-stay = Stop and bank { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }
flip7-stay-base = Stop and bank
flip7-stay-banked = Stop and bank (already stopped)
flip7-you-stay = You stop and bank { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stays = { $player } stops and banks { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.

# Round
flip7-round-start = Round { $round }. { $dealer } deals.
flip7-round-start-you = Round { $round }. You deal.
flip7-round-end = Round { $round } is over.
flip7-round-score = { $player } scores { $points } point{ $points ->
        [one] { "" }
       *[other] s
    } this round. Match total: { $total } point{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-score-you = You score { $points } point{ $points ->
        [one] { "" }
       *[other] s
    } this round. Match total: { $total } point{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-round-bust = { $player } busted and scores nothing.
flip7-round-bust-you = You busted and score nothing this round.
flip7-match-win = { $player } wins the match!
flip7-match-win-you = You win the match!
flip7-deck-reshuffled = The discard pile was shuffled into a new draw pile.
flip7-you-pending-bust-discarded = You busted, so your held action cards are discarded.
flip7-player-pending-bust-discarded = { $player } busted, so the held action cards are discarded.

# Drawing cards
flip7-you-turn-card = You flip a card.
flip7-player-turns-card = { $player } flips a card.
flip7-your-card-is = Card: { $card }.
flip7-player-card-is = { $player }'s card: { $card }.
flip7-you-stop-alone = You are the only player left, so you stop and bank { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-alone = { $player } is the only player left, so they stop and bank { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-set-second-chance = You set a Second Chance aside.
flip7-player-sets-second-chance = { $player } sets a Second Chance aside.
flip7-second-chance-saves = Second Chance saves { $player } from the repeated { $value }.
flip7-second-chance-saves-you = Second Chance saves you from the repeated { $value }.
flip7-you-bust = You flip another { $value } and bust. You score nothing this round.
flip7-player-busts = { $player } flips another { $value } and busts, scoring nothing this round.
flip7-flip-seven = { $player } completes Flip 7 and scores the { $bonus }-point bonus!
flip7-flip-seven-you = You complete Flip 7 and score the { $bonus }-point bonus!

# Targeted choices
flip7-choice-required = Choose a target for { $action }.
flip7-target-freeze = Freeze { $target } ({ $points } point{ $points ->
        [one] { "" }
       *[other] s
    })
flip7-target-flip-three = Make { $target } flip three cards
flip7-target-second-chance-self = Keep Second Chance
flip7-target-second-chance = Give a Second Chance to { $target }
flip7-you-stop-player = You freeze { $target } at { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-player = { $player } freezes { $target } at { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-stop-yourself = You freeze yourself at { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-player-stops-themself = { $player } freezes themself at { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-you-flip-three = You make { $target } flip three cards.
flip7-player-flip-three = { $player } makes { $target } flip three cards.
flip7-you-flip-three-self = You flip three cards.
flip7-player-flips-three-self = { $player } flips three cards.
flip7-you-give-second-chance = You give a Second Chance to { $target }.
flip7-player-gives-second-chance = { $player } gives a Second Chance to { $target }.
flip7-you-discard-second-chance = Nobody can take it, so the Second Chance is discarded.
flip7-player-discards-second-chance = { $player } cannot give the Second Chance away, so it is discarded.
flip7-you-discard-action = Nobody can be targeted, so { $action } is discarded.
flip7-player-discards-action = { $player } has nobody to target, so { $action } is discarded.

# Information actions
flip7-check-area = Review my area
flip7-check-area-description = Hear your face-up cards, round status, and current round score.
flip7-check-table = Review table
flip7-check-table-description = Open a live view of the round, current phase, and every player's public cards and scores.
flip7-check-deck = Check deck
flip7-check-deck-description = Hear how many cards remain in the deck and discard pile.
flip7-check-scores = Check scores
flip7-review-scores = Detailed scores
flip7-you-label = You
flip7-area-status-playing = still playing
flip7-area-status-scored = scored
flip7-area-status-stayed = stopped
flip7-area-status-busted = busted
flip7-area-numbers-none = none
flip7-area-inline = { $who}, { $status }. Number cards: { $numbers }. Round score: { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-inline-with-specials = { $who}, { $status }. Number cards: { $numbers }. Other cards: { $specials }. Round score: { $points } point{ $points ->
        [one] { "" }
       *[other] s
    }.
flip7-area-resolving-card = { $area } Resolving card: { $card }.
flip7-check-round = Round { $round }. Target score { $target }.
flip7-table-line = { $area } Match total: { $total } point{ $total ->
        [one] { "" }
       *[other] s
    }.
flip7-deck-line = Draw pile: { $count ->
        [one] { $count } card
       *[other] { $count } cards
    }
flip7-discard-line = Discard pile: { $count ->
        [one] { $count } card
       *[other] { $count } cards
    }

# Turn and sequence status
flip7-whose-turn-choice-you = You are choosing a target for { $action }.
flip7-whose-turn-choice-player = { $player } is choosing a target for { $action }.
flip7-whose-turn-dealing-you = Round { $round }: you are dealing.
flip7-whose-turn-dealing-player = Round { $round }: { $player } is dealing.
flip7-whose-turn-deal-card-you = Round { $round }: your opening card is resolving.
flip7-whose-turn-deal-card-player = Round { $round }: { $player }'s opening card is resolving.
flip7-whose-turn-card-you = Your card is resolving.
flip7-whose-turn-card-player = { $player }'s card is resolving.
flip7-whose-turn-flip-three-you = You are flipping three cards.
flip7-whose-turn-flip-three-player = { $player } is flipping three cards.
flip7-whose-turn-banking-you = You are stopping and banking.
flip7-whose-turn-banking-player = { $player } is stopping and banking.
flip7-whose-turn-round-end = Round { $round } is settling.
flip7-whose-turn-match-end = The winner is being announced.
flip7-whose-turn-resolving = A card sequence is resolving.

# Blocking reasons
flip7-error-wait-card = Wait until the current card is resolved.
flip7-error-make-choice = Choose a target before flipping or stopping.
flip7-error-wait-choice = Wait until the current target choice is resolved.
flip7-error-wait-flip-three = Wait until the Flip Three finishes.
flip7-error-wait-dealing = Wait until the cards are dealt.
flip7-error-not-playing-round = You are no longer playing this round.
flip7-error-no-cards-to-bank = You need at least one card in your area before you can stop.
flip7-error-no-choice = There is no card choice to answer.
flip7-error-wait-banking = Wait until the current points are banked.
flip7-error-choice-not-ready = Wait until the target choice opens.

# End screen
flip7-line-format = { $rank }. { $player }: { $points }
