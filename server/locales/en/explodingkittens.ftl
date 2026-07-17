game-name-explodingkittens = Exploding Kittens

explodingkittens-set-fast-game = Faster game: { $enabled }
explodingkittens-option-changed-fast-game = Faster game set to { $enabled }.
explodingkittens-option-fast-game-description = For two or three players, removes one third of the draw pile before adding the Exploding Kittens.
explodingkittens-error-fast-game-player-count = Faster game is available only with two or three players.
explodingkittens-set-advanced-combos = Advanced combos: { $enabled }
explodingkittens-option-changed-advanced-combos = Advanced combos set to { $enabled }.
explodingkittens-option-advanced-combos-description = Extends pairs to every matching title and enables three of a kind. Matching Cat pairs remain available when this is off.
explodingkittens-set-nope-response = Nope response time: { $time }
explodingkittens-select-nope-response = Choose the Nope response time.
explodingkittens-option-changed-nope-response = Nope response time set to { $time }.
explodingkittens-option-nope-response-description = Sets how long players have to respond whenever an action or Nope is played.
explodingkittens-nope-response-5 = 5 seconds
explodingkittens-nope-response-10 = 10 seconds
explodingkittens-nope-response-15 = 15 seconds
explodingkittens-nope-response-20 = 20 seconds
explodingkittens-error-invalid-nope-response = Choose a valid Nope response time.

explodingkittens-card-exploding-kitten = Exploding Kitten
explodingkittens-card-defuse = Defuse
explodingkittens-card-nope = Nope
explodingkittens-card-attack = Attack
explodingkittens-card-skip = Skip
explodingkittens-card-favor = Favor
explodingkittens-card-shuffle = Shuffle
explodingkittens-card-see-future = See the Future
explodingkittens-card-beard-cat = Beard Cat
explodingkittens-card-cattermelon = Cattermelon
explodingkittens-card-hairy-potato-cat = Hairy Potato Cat
explodingkittens-card-rainbow-ralphing-cat = Rainbow-Ralphing Cat
explodingkittens-card-tacocat = Tacocat
explodingkittens-card-unknown = Unknown card

explodingkittens-action-nope = Play Nope
explodingkittens-action-pass = Pass
explodingkittens-action-draw = Draw a card
explodingkittens-action-start-combo = Build a combo
explodingkittens-action-confirm-combo = Play selected combo
explodingkittens-action-cancel = Cancel
explodingkittens-action-use-defuse = Use Defuse
explodingkittens-action-accept-explosion = Explode without using Defuse
explodingkittens-action-read-hand = Read hand
explodingkittens-action-read-piles = Read draw and discard piles
explodingkittens-action-read-table = Read table
explodingkittens-action-check-nope-timer = Check Nope time
explodingkittens-action-name-pair = pair
explodingkittens-action-name-triple = three-of-a-kind combo
explodingkittens-target-player = { $player }, { $cards ->
    [one] 1 card
   *[other] { $cards } cards
}
explodingkittens-card-selected = Selected: { $card }
explodingkittens-card-not-selected = Not selected: { $card }
explodingkittens-give-card-label = Give { $card }
explodingkittens-insert-top = Insert on top
explodingkittens-insert-bottom = Insert on the bottom
explodingkittens-insert-position = Insert with { $cards } cards above it

explodingkittens-error-eliminated = You have already exploded.
explodingkittens-error-card-missing = That card is no longer available.
explodingkittens-error-card-not-combo = Exploding Kittens cannot be used in combos.
explodingkittens-error-combo-too-large = A combo can contain only two or three cards.
explodingkittens-error-basic-combo-pair-only = Advanced combos are off, so this combo is limited to a pair.
explodingkittens-error-combo-name-mismatch = Choose cards with the same name.
explodingkittens-error-action-in-progress = Finish the current action first.
explodingkittens-error-defuse-only-after-kitten = Defuse is used only after drawing an Exploding Kitten.
explodingkittens-error-nope-only-in-response = Nope is used only while an action is waiting to resolve.
explodingkittens-error-cat-needs-combo = Play Cat Cards as a matching pair or three of a kind.
explodingkittens-error-cat-needs-pair = Play Cat Cards as a matching pair.
explodingkittens-error-card-not-playable = That card cannot be played now.
explodingkittens-error-deck-empty = The draw pile is empty.
explodingkittens-error-no-combo = You do not have a matching pair or three of a kind.
explodingkittens-error-no-cat-pair = You do not have a matching Cat pair.
explodingkittens-error-advanced-combo-required = That combination requires advanced combos.
explodingkittens-error-no-target-with-cards = No other player has a card to give or steal.
explodingkittens-error-invalid-combo = Select exactly two or three cards with the same name.
explodingkittens-error-invalid-cat-pair = Select exactly two matching Cat Cards.
explodingkittens-error-not-nope-window = There is no action for you to Nope now.
explodingkittens-error-already-passed-nope = You already passed this Nope window.
explodingkittens-error-nope-own-action = You cannot Nope your own action. Wait for another player to respond.
explodingkittens-error-nope-own-nope = You cannot Nope the Nope you just played. Wait for another player to respond.
explodingkittens-error-no-nope = You do not have a Nope.
explodingkittens-error-no-defuse = You do not have a Defuse.
explodingkittens-error-invalid-target = That player cannot be targeted.
explodingkittens-error-invalid-request = That card cannot be requested.
explodingkittens-error-invalid-position = That reinsertion position is no longer available.

explodingkittens-game-started = Exploding Kittens begins with { $players } players and { $cards } cards in the draw pile.
explodingkittens-hand = { $count ->
    [one] Your card: { $cards }.
   *[other] Your { $count } cards: { $cards }.
}
explodingkittens-hand-empty = Your hand is empty.
explodingkittens-combo-selection-count = { $count ->
    [one] 1 card selected.
   *[other] { $count } cards selected.
}
explodingkittens-you-play-card = You play { $card }.
explodingkittens-player-plays-card = { $player } plays { $card }.
explodingkittens-you-play-pair = You play a { $card } pair against { $target }.
explodingkittens-player-plays-pair = { $player } plays a { $card } pair against { $target }.
explodingkittens-you-play-triple = You play three { $card } cards against { $target } and request { $request }.
explodingkittens-player-plays-triple = { $player } plays three { $card } cards against { $target } and requests { $request }.
explodingkittens-you-play-nope = You play Nope.
explodingkittens-player-plays-nope = { $player } plays Nope.
explodingkittens-you-pass-nope = You pass.
explodingkittens-nope-time-remaining = { $seconds ->
    [one] 1 second remains.
   *[other] { $seconds } seconds remain.
}
explodingkittens-your-action-canceled = Your { $action } is canceled.
explodingkittens-player-action-canceled = { $player }'s { $action } is canceled.
explodingkittens-your-action-resolves = Your { $action } takes effect.
explodingkittens-player-action-resolves = { $player }'s { $action } takes effect.
explodingkittens-your-shuffle-resolves = Your Shuffle takes effect. The draw pile is shuffled.
explodingkittens-player-shuffle-resolves = { $player }'s Shuffle takes effect. The draw pile is shuffled.
explodingkittens-your-attack-resolves = Your Attack takes effect. { $target } must take { $turns ->
    [one] 1 turn.
   *[other] { $turns } turns.
}
explodingkittens-attack-resolves-target = { $player }'s Attack takes effect. You must take { $turns ->
    [one] 1 turn.
   *[other] { $turns } turns.
}
explodingkittens-player-attack-resolves = { $player }'s Attack takes effect. { $target } must take { $turns ->
    [one] 1 turn.
   *[other] { $turns } turns.
}
explodingkittens-future-cards = Your See the Future takes effect. Next cards, in order: { $cards }.
explodingkittens-player-see-future-resolves = { $player }'s See the Future takes effect.
explodingkittens-your-favor-resolves = Your Favor takes effect. { $target } is choosing a card.
explodingkittens-favor-resolves-target = { $player }'s Favor takes effect. Choose a card to give.
explodingkittens-player-favor-resolves = { $player }'s Favor takes effect. { $target } is choosing a card.
explodingkittens-you-draw-card = You draw { $card }.
explodingkittens-player-draws-card = { $player } draws a card.
explodingkittens-you-draw-kitten = You draw an Exploding Kitten.
explodingkittens-player-draws-kitten = { $player } draws an Exploding Kitten.
explodingkittens-you-defuse = You use Defuse.
explodingkittens-player-defuses = { $player } uses Defuse.
explodingkittens-you-reinsert-kitten = You return the Exploding Kitten to the draw pile.
explodingkittens-player-reinserts-kitten = { $player } returns the Exploding Kitten to the draw pile.
explodingkittens-you-have-turns = You have { $turns ->
    [one] 1 turn
   *[other] { $turns } turns
} remaining.
explodingkittens-player-has-turns = { $player } has { $turns ->
    [one] 1 turn
   *[other] { $turns } turns
} remaining.
explodingkittens-you-explode = You explode.
explodingkittens-player-explodes = { $player } explodes.
explodingkittens-you-win = You are the last player standing and win Exploding Kittens.
explodingkittens-player-wins = { $player } is the last player standing and wins Exploding Kittens.

explodingkittens-favor-transfer-you = { $target } gives you { $card }.
explodingkittens-favor-transfer-target = You give { $card } to { $player }.
explodingkittens-favor-transfer-public = { $target } gives a card to { $player }.
explodingkittens-pair-transfer-you = You randomly take { $card } from { $target }.
explodingkittens-pair-transfer-target = { $player } randomly takes your { $card }.
explodingkittens-pair-transfer-public = { $player } randomly takes a card from { $target }.
explodingkittens-triple-transfer-you = { $target } gives you the requested { $card }.
explodingkittens-triple-transfer-target = You give the requested { $card } to { $player }.
explodingkittens-triple-transfer-public = { $target } gives the requested card to { $player }.
explodingkittens-triple-miss-you = { $target } does not have the requested { $card }.
explodingkittens-triple-miss-target = You do not have the { $card } requested by { $player }.
explodingkittens-triple-miss-public = { $target } does not have the { $card } requested by { $player }.

explodingkittens-no-discard = no discarded cards
explodingkittens-piles = Draw pile: { $deck }. Discard pile: { $discard }. Top discard: { $top }.
explodingkittens-table-piles = Draw pile: { $deck }. Discard pile: { $discard }.
explodingkittens-table-turn = Current turn: { $player }, { $turns ->
    [one] 1 turn remaining.
   *[other] { $turns } turns remaining.
}
explodingkittens-table-player = { $player }: { $cards ->
    [one] 1 card
   *[other] { $cards } cards
}, { $status }.
explodingkittens-status-alive = still playing
explodingkittens-status-eliminated = eliminated
explodingkittens-phase-normal = Waiting for a play or draw.
explodingkittens-phase-combo = A combo is being selected.
explodingkittens-phase-target = A target is being selected.
explodingkittens-phase-request = A card is being requested.
explodingkittens-phase-nope = A Nope window is open.
explodingkittens-phase-favor-give = A Favor card is being given.
explodingkittens-phase-defuse = An Exploding Kitten is awaiting a Defuse decision.
explodingkittens-phase-reinsert = An Exploding Kitten is being returned to the draw pile.
explodingkittens-phase-game-over = The game is over.

explodingkittens-results-winner = Winner: { $player }.
explodingkittens-results-place = { $rank }. { $player }.
