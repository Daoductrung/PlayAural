game-name-flip7 = Flip 7

# Options
flip7-set-target-score = Target score: { $score }
flip7-enter-target-score = Enter target score
flip7-option-changed-target = Target score set to { $score }.
flip7-desc-target-score = How many points are needed to win the match. Default: 200, range 50-1000.

# Cards
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Double
flip7-card-second-chance = Second Chance
flip7-card-freeze = Freeze
flip7-card-flip-three = Flip Three

# Turn actions
flip7-hit = Draw a card
flip7-stay = Stop and bank { $points } points
flip7-you-stay = You stop and bank { $points } points.
flip7-player-stays = { $player } stops and banks { $points } points.

# Round
flip7-round-start = Round { $round }. { $dealer } deals.
flip7-round-end = Round { $round } is over.
flip7-round-end-deck = The deck ran out. The round is over.
flip7-round-score = { $player } banks { $points } points, total { $total }.
flip7-round-score-you = You bank { $points } points, total { $total }.
flip7-round-bust = { $player } busted and scores nothing.
flip7-round-bust-you = You busted and score nothing this round.
flip7-match-win = { $player } wins the match!
flip7-match-win-you = You win the match!
flip7-deck-reshuffled = The discard pile was reshuffled into the deck.
flip7-you-pending-discarded = You are no longer playing this round, so your held action cards are discarded.
flip7-player-pending-discarded = { $player } is no longer playing this round, so the held action cards are discarded.
flip7-you-pending-bust-discarded = You busted, so your held action cards are discarded.
flip7-player-pending-bust-discarded = { $player } busted, so the held action cards are discarded.

# Drawing cards
flip7-you-turn-card = You turn over a card.
flip7-player-turns-card = { $player } turns over a card.
flip7-your-card-is = Card: { $card }.
flip7-player-card-is = { $player }'s card: { $card }.
flip7-you-stop-alone = You were the only one still playing, so you stopped yourself and banked { $points } points.
flip7-player-stops-alone = { $player } was the only one still playing, so they stopped and banked { $points } points.
flip7-you-set-second-chance = You set a Second Chance aside.
flip7-player-sets-second-chance = { $player } sets a Second Chance aside.
flip7-second-chance-saves = Second Chance saves { $player } from the repeated { $value }.
flip7-second-chance-saves-you = Second Chance saves you from the repeated { $value }.
flip7-you-bust = You turn over { $value } again and bust. The round is lost for you.
flip7-player-busts = { $player } turns over { $value } again and busts.
flip7-flip-seven = { $player } flips 7 and scores the 15 point bonus!
flip7-flip-seven-you = You flip 7 and score the 15 point bonus!

# Targeted choices
flip7-target-freeze = Make { $target } freeze ({ $points } points)
flip7-target-flip-three = Make { $target } flip three cards
flip7-target-second-chance = Give a Second Chance to { $target }
flip7-you-stop-player = You make { $target } stop with { $points } points.
flip7-player-stops-player = { $player } makes { $target } stop with { $points } points.
flip7-you-stop-yourself = You stop yourself and keep { $points } points.
flip7-player-stops-themself = { $player } stops themself and keeps { $points } points.
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
flip7-check-area = Check my area
flip7-check-table = Check the table
flip7-check-deck = Check the deck
flip7-you-label = You
flip7-area-status-stayed = , stopped this round
flip7-area-status-busted = , busted this round
flip7-area-numbers-none = No number cards yet
flip7-area-inline = { $who }{ $status }: { $numbers }. Total { $points } points.{ $bonus }
flip7-area-bonus-suffix = Bonuses: { $bonuses }.
flip7-check-round = Round { $round }. Target score { $target }.
flip7-status-playing = still playing
flip7-status-stayed = stopped
flip7-status-busted = busted
flip7-table-line = { $player }: { $status }, { $points } this round, { $total } total
flip7-deck-line = Deck: { $count ->
        [one] { $count } card
       *[other] { $count } cards
    }
flip7-discard-line = Discard pile: { $count ->
        [one] { $count } card
       *[other] { $count } cards
    }

# Blocking reasons
flip7-error-wait-card = Wait until the revealed card is resolved.
flip7-error-wait-choice = Wait until the current card choice is resolved.
flip7-error-wait-flip-three = Wait until the Flip Three finishes.
flip7-error-wait-dealing = Wait until the cards are dealt.
flip7-error-not-playing-round = You are no longer playing this round.
flip7-error-no-cards-left = There are no cards left to draw.
flip7-error-no-cards-to-bank = You have no cards to bank yet.
flip7-error-no-choice = There is no card choice to answer.

# End screen
flip7-line-format = { $rank }. { $player }: { $points }
