# Humanity Cards - English localization

game-name-humanitycards = Cards Against Humanity

# Options
hc-set-winning-score = Winning score: { $score }
hc-enter-winning-score = Enter winning score:
hc-option-changed-winning-score = Winning score set to { $score }.
hc-desc-winning-score = The number of winning cards a player needs to collect to win the match (default 7, range 3-20).

hc-set-hand-size = Hand size: { $count }
hc-enter-hand-size = Enter hand size:
hc-option-changed-hand-size = Hand size set to { $count }.
hc-desc-hand-size = How many answer cards each player holds after each refill. Larger hands give more choices but make rounds take longer (default 10, range 5-15).

hc-set-card-language = Card language: { $language }
hc-select-card-language = Select the card language
hc-option-changed-card-language = Card language set to { $language }.
hc-desc-card-language = Sets the language of every prompt and answer card in the match. This is independent of each player's interface language (default English; choices English, Spanish, and Brazilian Portuguese).
hc-card-language-pt-br = Brazilian Portuguese
hc-card-blank = blank
hc-card-same-again = same card again

hc-set-card-packs = Card packs ({ $count } of { $total } selected)
hc-option-changed-card-packs = Card pack selection changed.
hc-desc-card-packs = Choose which English answer and prompt packs are shuffled into the game. Exact duplicate cards from overlapping packs are included only once. At least one pack must stay selected.
hc-pack-group-current = Current US main deck
hc-pack-group-main-decks = Main deck editions
hc-pack-group-official-add-ons = Official expansions and packs
hc-pack-group-family = Family Edition
hc-pack-group-community = Community packs
hc-pack-group-all = All packs

hc-set-czar-selection = Card Czar selection: { $mode }
hc-select-czar-selection = Select Card Czar selection mode
hc-option-changed-czar-selection = Card Czar selection set to { $mode }.
hc-desc-czar-selection = Controls who judges each round: rotating in seating order, randomly chosen, or the most recent round winner.

hc-set-num-judges = Number of judges: { $count }
hc-enter-num-judges = Enter number of judges:
hc-option-changed-num-judges = Number of judges set to { $count }.
hc-desc-num-judges = How many Card Czars judge each round. The count must be lower than the player count so at least one non-judge can submit; with multiple judges, any judge can pick the winner (default 1, range 1-3).

hc-czar-rotating = Rotating
hc-czar-random = Random
hc-czar-winner = Most Recent Winner

# Game flow
hc-game-starting = Shuffling the decks...
hc-dealing-cards = Dealing { $count } cards to each player.
hc-round-start = Round { $round }.

# Judge announcement
hc-judge-is = { $judges } { $count ->
    [1] is the Card Czar
   *[other] are the Card Czars
}.
hc-you-are-judge = You are the Card Czar this round.
hc-you-and-others-are-judges = You and { $judges } are the Card Czars this round.

# Black card
hc-black-card = The prompt is: { $text }
hc-black-card-draw = Draw { $count } extra { $count ->
    [one] card
   *[other] cards
} first.
hc-black-card-pick = Pick { $count }.
hc-view-black-card = View the question card
hc-no-question-card = There is no active question card right now.

# Submission phase
hc-select-cards = Select { $count } { $count ->
    [one] card
   *[other] cards
} from your hand.
hc-card-selected = { $text }, selected
hc-card-selected-position = { $text }, selected as answer { $position }
hc-card-not-selected = { $text }
hc-submit-cards = Submit ({ $selected } of { $required } selected)
hc-submission-progress = { $submitted } of { $total } players submitted.
hc-already-submitted = You already submitted your cards.
hc-you-submitted = You submitted your cards.
hc-player-submitted = { $player } submitted { GENDER_TERM($player_gender, "possessive-determiner") } cards.
hc-judge-cannot-submit = You are the Card Czar this round, so you cannot submit an answer.
hc-not-submission-phase = You can only select and submit white cards during the submission phase.
hc-card-not-in-hand = That card slot is not in your hand.
hc-judge-has-no-submission = The Card Czar does not have a submission to preview this round.
hc-no-submission-active = There is no active submission to preview right now.
hc-wrong-card-count = You need to select exactly { $count } { $count ->
    [one] card
   *[other] cards
}.
hc-selection-full = You already selected { $count } { $count ->
    [one] card
   *[other] cards
}. Deselect one before choosing another.

# Judging phase
hc-judging-start = All cards are in! Time to judge.
hc-choose-best-card = Choose the best card
hc-choose-best-card-for = Choose the best card that matches: { $prompt }
hc-card-number = Card { $number }
hc-submission-number = Submission { $number }
hc-only-judges-pick = Only the Card Czar can choose the winning submission.
hc-not-judging-phase = You can only choose a winning submission during the judging phase.
hc-submission-not-available = That submission is no longer available.

# Results
hc-you-win-round = You win the round! Your score is now { $score }.
hc-player-wins-round = { $player } wins the round! Score: { $score }.
hc-score-line = { $player }: { $score } { $score ->
    [one] point
   *[other] points
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] point
   *[other] points
}
hc-all-submissions = Other submissions:
hc-your-winning-answer = Your winning answer: { $text }
hc-winning-answer-player = { $player }'s winning answer: { $text }
hc-your-other-submission = Your other submission: { $text }
hc-other-submission-player = { $player }: { $text }

# View
hc-preview-submission = Preview your submission
hc-view-submission = View your submission
hc-preview-submission-text = Preview: { $text }
hc-your-submission = Your submission: { $text }
hc-select-cards-first = Select at least 1 card first.
hc-review-hand = Review your hand
hc-hand-empty = Your hand is empty.
hc-hand-card = { $number }. { $text }
hc-hand-card-selected = { $number }. { $text }, selected as answer { $position }
hc-review-answers = Review the answers
hc-answer-line = Answer { $number }: { $text }
hc-no-answers-to-review = There are no answers to review right now.

# Win
hc-game-winner = { $player } wins with { $score } points!
hc-you-win = You win with { $score } points!

# Deck management
hc-deck-reshuffled = White card discard pile reshuffled into the deck.
hc-black-deck-reshuffled = Black card discard pile reshuffled into the deck.
hc-not-enough-cards = Not enough cards. Try enabling more packs.
hc-error-too-many-judges = { $judges } judges require at least { $required } players, but this table has { $players }. Lower the number of judges or add more players.
hc-error-no-valid-packs = No valid card packs are selected. Select at least one pack before starting.
hc-error-no-black-cards = The selected card packs do not contain any black prompt cards. Select another pack before starting.
hc-error-not-enough-white-cards = { $players } players with a hand size of { $hand_size } need at least { $needed } white cards, but the selected packs only provide { $available }. Enable more packs or lower the hand size.
hc-error-pick-exceeds-hand-size = The selected packs include a prompt that requires { $pick } answers, but the hand size is only { $hand_size }. Increase the hand size or choose different packs.

# Hand management
hc-toggle-card-keybind = Toggle card { $number }
hc-submit-cards-keybind = Submit cards

# Whose turn / whose judge
hc-whose-judge = Who is judging
hc-waiting-for = Waiting for { $names } to submit.
hc-all-submitted-waiting-judge = All players have submitted. Waiting for { $judge } to judge.
