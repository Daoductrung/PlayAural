game-name-ninetynine = Ninety Nine
ninetynine-description = A card game where players try to avoid pushing the running total over 99. Last player standing wins!

ninetynine-round = Round { $round }.

ninetynine-player-turn = { $player }'s turn.

ninetynine-you-play = You play { $card }. The count is now { $count }.
ninetynine-player-plays = { $player } plays { $card }. The count is now { $count }.

ninetynine-direction-reverses = The direction of play reverses!

ninetynine-you-skipped = You are skipped.
ninetynine-player-skipped = { $player } is skipped.

n99-card-plus-10 = +10
n99-card-minus-10 = -10
n99-card-pass = Pass
n99-card-reverse = Reverse
n99-card-skip = Skip
n99-card-ninety-nine = Ninety Nine

ninetynine-you-lose-tokens = You lose { $amount } { $amount ->
    [one] token
    *[other] tokens
}.
ninetynine-player-loses-tokens = { $player } loses { $amount } { $amount ->
    [one] token
    *[other] tokens
}.

ninetynine-you-eliminated = You have been eliminated!
ninetynine-player-eliminated = { $player } has been eliminated!

ninetynine-you-win = You win the game!
ninetynine-player-wins = { $player } wins the game!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] token
   *[other] tokens
}

ninetynine-you-deal = You deal out the cards.
ninetynine-player-deals = { $player } deals out the cards.

ninetynine-you-draw = You draw { $card }.
ninetynine-player-draws = { $player } draws a card.

ninetynine-you-no-valid-cards = You have no cards that won't go over 99!
ninetynine-player-no-valid-cards = { $player } has no cards that won't go over 99!
ninetynine-no-valid-cards = { $player } has no cards that won't go over 99!

ninetynine-current-count = The count is { $count }.
ninetynine-next-round-wait = The next round will start in { $seconds } seconds.

ninetynine-ace-choice = Play Ace as +1 or +11?
ninetynine-ace-add-eleven = Add 11
ninetynine-ace-add-one = Add 1

ninetynine-ten-choice = Play 10 as +10 or -10?
ninetynine-ten-add = Add 10
ninetynine-ten-subtract = Subtract 10
ninetynine-select-card-choice = Choose how to play this card.
ninetynine-choice-1 = Choice 1
ninetynine-choice-2 = Choice 2

ninetynine-draw-card = Draw card
ninetynine-draw-prompt = Please draw a card.
ninetynine-no-card-to-draw = No card is available to draw. Continue with your current hand.

ninetynine-set-tokens = Starting tokens: { $tokens }
ninetynine-enter-tokens = Enter number of starting tokens:
ninetynine-option-changed-tokens = Starting tokens set to { $tokens }.
ninetynine-desc-starting-tokens = How many survival tokens each Ninety Nine player begins with. A player is eliminated after losing all tokens (default 9, range 1-50).
ninetynine-set-rules = Rules variant: { $rules }
ninetynine-select-rules = Select rules variant
ninetynine-option-changed-rules = Rules variant set to { $rules }.
ninetynine-desc-rules-variant = Chooses the standard 52-card Ninety Nine deck or the special action-cards deck.
ninetynine-set-hand-size = Hand size: { $size }
ninetynine-enter-hand-size = Enter hand size:
ninetynine-option-changed-hand-size = Hand size set to { $size }.
ninetynine-desc-hand-size = How many cards each player is dealt at the start of each Ninety Nine round (default 3, range 1-13).
ninetynine-set-autodraw = Automatic drawing: { $enabled }
ninetynine-option-changed-autodraw = Automatic drawing set to { $enabled }.
ninetynine-desc-autodraw = When enabled, players automatically draw a replacement card after playing. When off, players must draw manually.

ninetynine-rules-standard = Standard rules.
ninetynine-rules-action-cards = Action cards rules.

ninetynine-rules-variant-standard = Standard
ninetynine-rules-variant-action-cards = Action Cards

ninetynine-choose-first = You need to make a choice first.
ninetynine-round-transition-waiting = Waiting for the next round to start.
ninetynine-pause-timer = Pause timer
ninetynine-timer-not-active = The round timer is not active.
ninetynine-error-too-many-cards = Too many cards needed: { $players } players × { $hand_size } cards exceeds the { $deck_size }-card deck.
ninetynine-check-count = Check count
