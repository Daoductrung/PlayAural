# Nine game messages

# Game name and description
game-name-nine = Nine
nine-description = A popular Russian card game in which players build suit sequences.

# Player count validation
nine-error-invalid-player-count = Nine uses a 36-card deck and seats exactly 3, 4, or 6 players.
nine-error-starting-nine-missing = The nine of diamonds was not found in any hand. The game cannot continue.

# Dealing messages
nine-player-nine-deal = Dealing { $cards } cards to each player.

# Game start
nine-you-start-player-announcement = You have the nine of diamonds and start the game.
nine-player-start-player-announcement = { $player } has the nine of diamonds and starts the game.
nine-you-start-player-announcement-brief = You start with the nine of diamonds.
nine-player-start-player-announcement-brief = { $player } starts with the nine of diamonds.

# Turn actions
nine-you-plays-starting-nine = You play the { $card } to open the table.
nine-player-plays-starting-nine = { $player } plays the { $card } to open the table.
nine-you-plays-starting-nine-brief = You play { $card }.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = You play the { $card } to start the { $suit } sequence.
nine-player-plays-nine-suit = { $player } plays the { $card } to start the { $suit } sequence.
nine-you-plays-nine-suit-brief = You start { $suit } with { $card }.
nine-player-plays-nine-suit-brief = { $player } starts { $suit } with { $card }.

nine-you-extend-sequence = You extend the { $suit } sequence with the { $card }.
nine-player-extend-sequence = { $player } extends the { $suit } sequence with the { $card }.
nine-you-extend-sequence-brief = You play { $card } on { $suit }.
nine-player-extend-sequence-brief = { $player }: { $card } on { $suit }.

nine-you-skips-turn = You have no legal card to play, so your turn is skipped.
nine-player-skips-turn = { $player } has no legal card to play, so { GENDER_TERM($player_gender, "possessive-determiner") } turn is skipped.
nine-you-skips-turn-brief = You skip; no legal card.
nine-player-skips-turn-brief = { $player } skips; no legal card.

# Reasons for not being able to play a card
nine-reason-not-your-turn = It is not your turn.
nine-reason-card-slot-gone = That card is no longer in your hand. Your hand menu has been refreshed.
nine-reason-must-play-starting-nine = The first play must be the { $starting_card }. { $card } cannot be played until the table is opened.
nine-reason-nine-already-started = { $card } cannot be played because the { $suit } sequence is already open.
nine-reason-cannot-extend = { $card } cannot extend the { $suit } sequence. Play the next lower or next higher card at one of that sequence's ends.
nine-reason-unopened-suit = { $card } cannot be played because the { $suit } sequence has not been opened yet. Start that suit with its 9 first.
nine-reason-must-skip = You have no legal card to play; your turn will be skipped automatically.
# Winning
nine-you-wins-game = You have no cards left and win the game!
nine-player-wins-game = { $player } has no cards left and wins the game!
nine-you-wins-game-brief = You win!
nine-player-wins-game-brief = { $player } wins!
nine-player-game-ended = The game of Nine has ended.
nine-you-game-ended = The game of Nine has ended.

nine-you-win = You win!
nine-you-lose = You lose!
nine-final-score = Cards left: { $score }

# Status
nine-status = { $name }: { $cards_left } cards left.
nine-status-sequence = { $suit } sequence: { $sequence }.
nine-status-no-sequence = No { $suit } sequence started yet.
nine-sequence-range = { $low } through { $high }
nine-none = none
nine-action-check-sequences = Check Sequences
nine-action-check-hand-counts = Check Hand Counts
nine-status-player-hand-count = { $player }: { $count } cards
