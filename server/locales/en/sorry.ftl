game-name-sorry = Sorry!

sorry-set-rules-profile = Rules profile: { $profile }
sorry-select-rules-profile = Choose a rules profile
sorry-option-changed-rules-profile = Rules profile set to { $profile }.
sorry-rules-profile-classic-00390 = Classic 00390
sorry-rules-profile-a5065-core = A5065 Core

sorry-toggle-auto-apply-single-move = Auto apply single move: { $enabled }
sorry-option-changed-auto-apply-single-move = Auto apply single move set to { $enabled }.
sorry-toggle-faster-setup-one-pawn-out = Faster setup (one pawn out): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = Faster setup set to { $enabled }.
sorry-error-unsupported-rules-profile = The selected Sorry rules profile "{ $profile }" is not supported. Choose Classic 00390 or A5065 Core before starting.

sorry-draw-card = Draw card
sorry-check-board = Read board
sorry-check-pawns = Check your pawns
sorry-check-card = Check current card
sorry-check-status = Check status

sorry-move-slot = Move option { $slot }
sorry-move-slot-fallback = Choose move
sorry-move-start = Move pawn { $pawn } from { $position } out of start
sorry-move-forward = Move pawn { $pawn } from { $position } forward { $steps }
sorry-move-backward = Move pawn { $pawn } from { $position } backward { $steps }
sorry-move-swap = Swap pawn { $pawn } at { $position } with { $target_player } pawn { $target_pawn } at { $target_position }
sorry-move-sorry = Use Sorry! with pawn { $pawn } at { $position } against { $target_player } pawn { $target_pawn } at { $target_position }
sorry-move-split7-pick = Split 7 between pawn { $pawn_a } at { $position_a } and pawn { $pawn_b } at { $position_b }
sorry-move-split7-option = Pawn { $pawn_a } at { $position_a } moves { $steps_a }, pawn { $pawn_b } at { $position_b } moves { $steps_b }

sorry-card-none = no active card
sorry-card-sorry = Sorry!
sorry-choose-move = Choose a move.
sorry-choose-split = Choose how to split 7.
sorry-error-draw-pending-move = You already drew a card. Choose one of the available moves for that card before drawing again.

sorry-game-started = Sorry begins. Players: { $players }.
sorry-draw-announcement = { $player } draws { $card }.
sorry-you-draw-announcement = You draw { $card }.
sorry-no-legal-moves = { $player } has no legal move for { $card }.
sorry-you-no-legal-moves = You have no legal move for { $card }.
sorry-deck-exhausted = The Sorry deck is empty, so the game ends here.
sorry-you-extra-turn = You drew a 2 and take another turn.
sorry-player-extra-turn = { $player } drew a 2 and takes another turn.

sorry-play-start =
    { $brief ->
        [yes] { $player }: pawn { $pawn } start to { $destination }.
       *[no] { $player } brings pawn { $pawn } out to { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] You: pawn { $pawn } start to { $destination }.
       *[no] You bring pawn { $pawn } out to { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: pawn { $pawn } +{ $steps } to { $destination }.
       *[no] { $player } moves pawn { $pawn } forward { $steps } spaces to { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] You: pawn { $pawn } +{ $steps } to { $destination }.
       *[no] You move pawn { $pawn } forward { $steps } spaces to { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: pawn { $pawn } -{ $steps } to { $destination }.
       *[no] { $player } moves pawn { $pawn } backward { $steps } spaces to { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] You: pawn { $pawn } -{ $steps } to { $destination }.
       *[no] You move pawn { $pawn } backward { $steps } spaces to { $destination }.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: pawn { $pawn } swaps { $target_player } pawn { $target_pawn }; { $destination }.
       *[no] { $player } swaps pawn { $pawn } with { $target_player } pawn { $target_pawn } and finishes on { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] You: pawn { $pawn } swaps { $target_player } pawn { $target_pawn }; { $destination }.
       *[no] You swap pawn { $pawn } with { $target_player } pawn { $target_pawn } and finish on { $destination }.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: Sorry! pawn { $pawn } to { $destination }; { $target_player } pawn { $target_pawn } start.
       *[no] { $player } plays Sorry!, replacing { $target_player } pawn { $target_pawn }, and finishes on { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] You: Sorry! pawn { $pawn } to { $destination }; { $target_player } pawn { $target_pawn } start.
       *[no] You play Sorry!, replace { $target_player } pawn { $target_pawn }, and finish on { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: pawn { $pawn_a } +{ $steps_a } to { $destination_a }; pawn { $pawn_b } +{ $steps_b } to { $destination_b }.
       *[no] { $player } splits 7: pawn { $pawn_a } moves { $steps_a } spaces to { $destination_a }, and pawn { $pawn_b } moves { $steps_b } spaces to { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] You: pawn { $pawn_a } +{ $steps_a } to { $destination_a }; pawn { $pawn_b } +{ $steps_b } to { $destination_b }.
       *[no] You split 7: pawn { $pawn_a } moves { $steps_a } spaces to { $destination_a }, and pawn { $pawn_b } moves { $steps_b } spaces to { $destination_b }.
    }

sorry-pawn-home = { $player } gets pawn { $pawn } home.
sorry-you-pawn-home = Your pawn { $pawn } reaches home.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: your pawn { $pawn } to start.
       *[no] Your pawn { $pawn } was bumped back to start by { $by_player }.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] You: { $target_player } pawn { $pawn } to start.
       *[no] You bump { $target_player } pawn { $pawn } back to start.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: { $target_player } pawn { $pawn } to start.
       *[no] { $player } bumps { $target_player } pawn { $pawn } back to start.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] You: own pawn { $pawn } to start.
       *[no] You bump your own pawn { $pawn } back to start.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: own pawn { $pawn } to start.
       *[no] { $player } bumps their own pawn { $pawn } back to start.
    }

sorry-current-card = Current card: { $card }.
sorry-view-your-pawn = Your pawn { $pawn }: { $zone }.
sorry-board-your-color = Your color: { $color }.
sorry-board-summary-heading = Quick summary:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = pawn { $pawn } at { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = Track squares:
sorry-board-private-areas-heading = Private areas:
sorry-board-square-line = Square { $square }: { $status }
sorry-board-square-empty = empty
sorry-board-square-slide = { $color } slide
sorry-board-square-token = pawn { $pawn } of { $player }
sorry-board-start-line = { $color } start area of { $player }: { $pawns }
sorry-board-safety-line = { $color } safety space { $space } of { $player }: { $pawns }
sorry-board-home-line = { $color } home of { $player }: { $pawns }
sorry-board-area-empty = empty
sorry-board-area-pawn = pawn { $pawn }
sorry-color-red = red
sorry-color-blue = blue
sorry-color-yellow = yellow
sorry-color-green = green
sorry-location-start = start
sorry-location-track = square { $position }
sorry-location-home-path = safety space { $steps }
sorry-location-home = home
sorry-zone-start = in start
sorry-zone-track = on track square { $position }
sorry-zone-home-path = in safety zone step { $steps }
sorry-zone-home = home

sorry-status-turn-number = Turn { $count }
sorry-status-phase = Phase: { $phase }
sorry-status-current-card = Card: { $card }
sorry-status-current-player = Current player: { $player }
sorry-phase-draw = draw
sorry-phase-choose-move = choose move
sorry-phase-choose-split = split seven
sorry-phase-resolving = resolving move

sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 pawn home
   *[other] { $count } pawns home
}
