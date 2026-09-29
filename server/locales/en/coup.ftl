game-name-coup = Coup

coup-action-income = Income (+1 coin)
coup-action-foreign-aid = Foreign Aid (+2 coins)
coup-action-coup = Coup (Cost: 7 coins)
coup-action-tax = Tax (Duke, +3 coins)
coup-action-assassinate = Assassinate (Assassin, Cost: 3 coins)
coup-action-steal = Steal (Captain, +2 coins)
coup-action-exchange = Exchange (Ambassador)

coup-action-challenge = Challenge!
coup-action-block = Block!
coup-action-pass = Pass

coup-action-lose-influence = Lose Influence
coup-action-return-card = Return Card

coup-card-duke = Duke
coup-card-assassin = Assassin
coup-card-captain = Captain
coup-card-ambassador = Ambassador
coup-card-contessa = Contessa

coup-return-card-format = Return { $card }
coup-return-card-exchanged-format = Exchanged: { $card }
coup-card-already-exchanged = That card has already been exchanged.

coup-select-target = Select target:
coup-must-coup = You have 10 or more coins and must Coup!
coup-target-invalid = { $target } is not a valid living target.
coup-cannot-challenge-action = You cannot challenge this action.
coup-cannot-block-now = You cannot block right now.
coup-only-target-can-block = Only the target can block this action.
coup-cannot-block-action = This action cannot be blocked.
coup-no-active-claim = There is no active claim to challenge.

coup-you-take-income = You take Income.
coup-takes-income = { $player } takes Income.
coup-you-claim-foreign-aid = You claim Foreign Aid.
coup-claims-foreign-aid = { $player } claims Foreign Aid.
coup-you-take-foreign-aid = You take Foreign Aid and gain 2 coins.
coup-takes-foreign-aid = { $player } takes Foreign Aid.
coup-you-play-coup = You stage a Coup against { $target }!
coup-coup-targets-you = { $player } stages a Coup against you!
coup-plays-coup = { $player } stages a Coup against { $target }!
coup-you-claim-tax = You claim the Duke and demand Tax.
coup-claims-tax = { $player } claims the Duke and demands Tax.
coup-you-take-tax = You collect Tax and gain 3 coins.
coup-takes-tax = { $player } collects Tax.
coup-you-claim-assassinate = You claim the Assassin and target { $target }.
coup-assassination-claimed-against-you = { $player } claims the Assassin and targets you.
coup-claims-assassinate = { $player } claims the Assassin and targets { $target }.
coup-you-assassinate = Your assassination against { $target } resolves.
coup-you-are-assassinated = { $player }'s assassination against you resolves.
coup-assassinates = { $player } assassinates { $target }.
coup-you-claim-steal = You claim the Captain and attempt to steal from { $target }.
coup-steal-claimed-against-you = { $player } claims the Captain and attempts to steal from you.
coup-claims-steal = { $player } claims the Captain and attempts to steal from { $target }.
coup-you-steal = You steal { $amount } coins from { $target }.
coup-you-are-stolen-from = { $player } steals { $amount } coins from you.
coup-steals = { $player } steals { $amount } coins from { $target }.
coup-you-claim-exchange = You claim the Ambassador to exchange cards.
coup-claims-exchange = { $player } claims the Ambassador to exchange cards.
coup-you-exchange = You draw cards to exchange with the Court deck.
coup-exchanges = { $player } draws 2 cards to exchange.
coup-you-exchange-complete = You completed your exchange.
coup-exchange-complete = { $player } has completed { GENDER_TERM($player_gender, "possessive-determiner") } exchange.

coup-drew-replacement-card = You drew a { $character } as a replacement.
coup-action-pass-confirmed = You passed.
coup-player-passes-reaction = { $player } passes on this reaction window.

coup-waiting-for-reactions = Waiting for players to Challenge or Block...
coup-you-eliminated = You have lost all your influence and are eliminated from the game. Your coins return to the treasury.
coup-player-eliminated = { $player } has lost all { GENDER_TERM($player_gender, "possessive-determiner") } influence and is eliminated from the game.
coup-you-win-game = You are the last survivor and win the game!
coup-cannot-afford-assassinate = You need at least 3 coins to assassinate.
coup-cannot-afford-coup = You need at least 7 coins to stage a Coup.
coup-your-block-successful = Your block succeeds. The original action fails.
coup-block-successful = { $player } successfully blocked the action!
coup-you-assassination-refunded = Your { $amount } assassination coins are returned because the Assassin claim was successfully challenged.
coup-assassination-refunded = { $player } gets { $amount } assassination coins back because the Assassin claim was successfully challenged.

coup-you-challenge = You challenge { $target }!
coup-player-challenges-you = { $challenger } challenges your claim!
coup-challenges = { $challenger } challenges { $target }!
coup-you-catch-bluff = You catch { $player } bluffing. { $player } must lose an influence.
coup-your-bluff-caught = { $challenger } catches your bluff. You must lose an influence.
coup-challenge-succeeded = { $challenger } catches { $player } bluffing. { $player } must lose an influence.
coup-you-prove-claim = You reveal { $character } and prove your claim. { $challenger } must lose an influence.
coup-you-lose-challenge = { $player } reveals { $character }. You challenged incorrectly and must lose an influence.
coup-challenge-failed = { $player } was telling the truth and revealed { $character }. { $challenger } must lose an influence.
coup-you-block-foreign-aid = You claim the Duke to block { $target }'s Foreign Aid.
coup-your-foreign-aid-blocked = { $player } claims the Duke to block your Foreign Aid.
coup-blocks-foreign-aid = { $blocker } claims the Duke to block { $target }'s Foreign Aid.
coup-you-block-assassination = You claim the Contessa to block { $target }'s Assassination.
coup-your-assassination-blocked = { $player } claims the Contessa to block your Assassination.
coup-blocks-assassinate = { $blocker } claims the Contessa to block { $target }'s Assassination.
coup-you-block-steal = You claim the Captain or Ambassador to block { $target }'s Steal.
coup-your-steal-blocked = { $player } claims the Captain or Ambassador to block your Steal.
coup-blocks-steal = { $blocker } claims the Captain/Ambassador to block { $target }'s Steal.

coup-you-lose-influence = You lose your { $character }!
coup-loses-influence = { $player } loses { GENDER_TERM($player_gender, "possessive-determiner") } { $character }!
coup-must-lose-influence = You must choose an influence to lose.
coup-must-return-card = Please select a card to return to the deck.
coup-returned-card = You returned a { $character } to the deck.

coup-you-are-eliminated = You have been eliminated and cannot perform this action.

coup-action-check-wealth = Check Wealth
coup-action-check-hand = Check Hand
coup-action-check-table = Check Table

coup-wealth-line = { $player }: { $coins } coins
coup-no-alive-players = No players are currently alive.
coup-no-cards = You have no cards.
coup-hand-context = You have { $coins } coins. Your cards: { $cards }.
coup-table-line = { $player } lost: { $cards }
coup-table-empty = No cards have been revealed yet.

coup-end-winner = Winner
coup-end-eliminated = Eliminated
coup-end-line = { $rank }. { $name } ({ $status }) - { $coins } coins. Cards: { $cards }

coup-set-mandatory-coup = Mandatory Coup Coin Threshold ({ $coins })
coup-enter-mandatory-coup = Enter coins required to force a Coup (10 - 20):
coup-option-changed-mandatory-coup = Mandatory Coup threshold changed.
coup-desc-mandatory-coup-threshold = Coin total at which a player must Coup instead of choosing another action (default 10, range 10-20).

coup-set-timer-duration = Interrupt Timer Duration ({ $seconds }s)
coup-enter-timer-duration = Enter duration for Challenge/Block window (3 - 15 seconds):
coup-option-changed-timer = Timer duration changed.
coup-desc-timer-duration-seconds = Time allowed for timed Coup reactions and challenges (default 7 seconds, range 3-15).
