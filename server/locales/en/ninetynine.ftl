# Ninety Nine - English Localization
# Messages match v10 exactly

# Game info
ninetynine-name = Ninety Nine
ninetynine-description = A card game where players try to avoid pushing the running total over 99. Last player standing wins!

# Round
ninetynine-round = Round { $round }.

# Turn
ninetynine-player-turn = { $player }'s turn.

# Playing cards - match v10 exactly
ninetynine-you-play = You play { $card }. The count is now { $count }.
ninetynine-player-plays = { $player } plays { $card }. The count is now { $count }.

# Direction reverse
ninetynine-direction-reverses = The direction of play reverses!

# Skip
ninetynine-player-skipped = { $player } is skipped.

# Token loss - match v10 exactly
ninetynine-you-lose-tokens = You lose { $amount } { $amount ->
    [one] token
    *[other] tokens
}.
ninetynine-player-loses-tokens = { $player } loses { $amount } { $amount ->
    [one] token
    *[other] tokens
}.

# Elimination
ninetynine-player-eliminated = { $player } has been eliminated!

# Game end
ninetynine-player-wins = { $player } wins the game!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] token
   *[other] tokens
}

# Dealing
ninetynine-you-deal = You deal out the cards.
ninetynine-player-deals = { $player } deals out the cards.

# Drawing cards
ninetynine-you-draw = You draw { $card }.
ninetynine-player-draws = { $player } draws a card.

# No valid cards
ninetynine-no-valid-cards = { $player } has no cards that won't go over 99!

# Status - for C key
ninetynine-current-count = The count is { $count }.

# Ace choice
ninetynine-ace-choice = Play Ace as +1 or +11?
ninetynine-ace-add-eleven = Add 11
ninetynine-ace-add-one = Add 1

# Ten choice
ninetynine-ten-choice = Play 10 as +10 or -10?
ninetynine-ten-add = Add 10
ninetynine-ten-subtract = Subtract 10
ninetynine-choice-1 = Choice 1
ninetynine-choice-2 = Choice 2

# Manual draw
ninetynine-draw-card = Draw card
ninetynine-draw-prompt = Please draw a card.

# Options
ninetynine-set-tokens = Starting tokens: { $tokens }
ninetynine-enter-tokens = Enter number of starting tokens:
ninetynine-option-changed-tokens = Starting tokens set to { $tokens }.
ninetynine-set-rules = Rules variant: { $rules }
ninetynine-select-rules = Select rules variant
ninetynine-option-changed-rules = Rules variant set to { $rules }.
ninetynine-set-hand-size = Hand size: { $size }
ninetynine-enter-hand-size = Enter hand size:
ninetynine-option-changed-hand-size = Hand size set to { $size }.
ninetynine-set-autodraw = Automatic drawing: { $enabled }
ninetynine-option-changed-autodraw = Automatic drawing set to { $enabled }.

# Rules variant announcements (shown at game start)
ninetynine-rules-quentin = Quentin C rules.
ninetynine-rules-rsgames = RS Games rules.

# Rules variant choices (for menu display)
ninetynine-rules-variant-quentin_c = Quentin C
ninetynine-rules-variant-rs_games = RS Games

# Disabled action reasons
ninetynine-choose-first = You need to make a choice first.
ninetynine-draw-first = You need to draw a card first.
ninetynine-check-count = Check count
