# Humanity Cards - English localization

game-name-humanitycards = Cards Against Humanity

# Options
hc-set-winning-score = Winning score: { $score }
hc-desc-winning-score = The number of winning cards a player needs to collect to win the match.
hc-enter-winning-score = Enter winning score:
hc-option-changed-winning-score = Winning score set to { $score }.

hc-set-hand-size = Hand size: { $count }
hc-desc-hand-size = How many answer cards each player holds after each refill. Larger hands give more choices but make rounds take longer.
hc-enter-hand-size = Enter hand size:
hc-option-changed-hand-size = Hand size set to { $count }.

hc-set-card-packs = Card packs ({ $count } of { $total } selected)
hc-desc-card-packs = Choose which answer and prompt packs are shuffled into the game. At least one pack must stay selected.
hc-option-changed-card-packs = Card pack selection changed.

hc-set-czar-selection = Card Czar selection: { $mode }
hc-desc-czar-selection = Controls who judges each round: rotating in seating order, randomly chosen, or the most recent round winner.
hc-select-czar-selection = Select Card Czar selection mode
hc-option-changed-czar-selection = Card Czar selection set to { $mode }.

hc-set-num-judges = Number of judges: { $count }
hc-desc-num-judges = How many Card Czars judge each round. Multiple judges must agree through the game's judge flow before a winner is chosen.
hc-enter-num-judges = Enter number of judges:
hc-option-changed-num-judges = Number of judges set to { $count }.

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
hc-you-are-not-judge = You are not the Card Czar this round.

# Black card
hc-black-card = The prompt is: { $text }
hc-black-card-pick = Pick { $count }.
hc-view-black-card = View the question card

# Submission phase
hc-select-cards = Select { $count } { $count ->
    [one] card
   *[other] cards
} from your hand.
hc-card-selected = { $text }, selected
hc-card-not-selected = { $text }
hc-submit-cards = Submit ({ $selected } of { $required } selected)
hc-submission-progress = { $submitted } of { $total } players submitted.
hc-waiting-for-submissions = Waiting for submissions...
hc-already-submitted = You already submitted your cards.
hc-you-submitted = You submitted your cards.
hc-player-submitted = { $player } submitted their cards.
hc-judge-cannot-submit = You are the Card Czar this round, so you cannot submit an answer.
hc-not-submission-phase = You can only select and submit white cards during the submission phase.
hc-card-not-in-hand = That card slot is not in your hand.
hc-judge-has-no-submission = The Card Czar does not have a submission to preview this round.
hc-no-submission-active = There is no active submission to preview right now.
hc-wrong-card-count = You need to select exactly { $count } { $count ->
    [one] card
   *[other] cards
}.

# Judging phase
hc-judging-start = All cards are in! Time to judge.
hc-choose-best-card = Choose the best card
hc-choose-best-card-for = Choose the best card that matches: { $prompt }
hc-select-winner-prompt = Select the winning submission
hc-card-number = Card { $number }
hc-submission-number = Submission { $number }
hc-submission-option = { $text }
hc-only-judges-pick = Only the Card Czar can choose the winning submission.
hc-not-judging-phase = You can only choose a winning submission during the judging phase.
hc-submission-not-available = That submission is no longer available.

# Results
hc-you-win-round = You win the round! Your score is now { $score }.
hc-player-wins-round = { $player } wins the round! Score: { $score }.
hc-round-scores = Scores after round { $round }:
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

# Win
hc-game-winner = { $player } wins with { $score } points!
hc-you-win = You win with { $score } points!
hc-english-content-note = Note: the question and answer card text currently supports English only.

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
hc-view-hand = View hand
hc-toggle-card-keybind = Toggle card { $number }
hc-submit-cards-keybind = Submit cards

# Scores
hc-view-scores = View scores
hc-no-scores = No scores yet.

# Whose turn / whose judge
hc-whose-judge = Who is judging
hc-waiting-for = Waiting for { $names } to submit.
hc-all-submitted-waiting-judge = All players have submitted. Waiting for { $judge } to judge.
