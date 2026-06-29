game-name-ludo = Ludo

ludo-roll-die = Roll die
ludo-move-token = Move token
ludo-move-token-n = Move token { $token }
ludo-check-board = View board status
ludo-select-token = Select token to move:

ludo-roll = { $player } rolls a { $roll }.
ludo-you-roll = You roll a { $roll }.
ludo-no-moves = { $player } has no valid moves.
ludo-you-no-moves = You have no valid moves.
ludo-error-roll-pending-move = You already rolled and have a valid move. Move one of your available tokens before rolling again.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] You: token { $token } out +{ $spaces } to { $position }, safe.
           *[no] You: token { $token } out +{ $spaces } to { $position }.
        }
       *[no] { $safe ->
            [yes] You enter token { $token } onto position { $position }, which is a safe square.
           *[no] You enter token { $token } onto position { $position }.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }): token { $token } out +{ $spaces } to { $position }, safe.
           *[no] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }): token { $token } out +{ $spaces } to { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }) enters token { $token } onto position { $position }, which is a safe square.
           *[no] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }) enters token { $token } onto position { $position }.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] You: token { $token } +{ $spaces } to { $position }, safe.
           *[no] You: token { $token } +{ $spaces } to { $position }.
        }
       *[no] { $safe ->
            [yes] You move token { $token } to position { $position }, which is a safe square.
           *[no] You move token { $token } to position { $position }.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }): token { $token } +{ $spaces } to { $position }, safe.
           *[no] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }): token { $token } +{ $spaces } to { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }) moves token { $token } to position { $position }, which is a safe square.
           *[no] { $player } ({ $color ->
                [red] Red
                [blue] Blue
                [green] Green
                [yellow] Yellow
               *[other] { $color }
            }) moves token { $token } to position { $position }.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] You: token { $token } +{ $spaces } to home { $position }/{ $total }.
       *[no] You move token { $token } into your home column ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }): token { $token } +{ $spaces } to home { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $color }
        }) moves token { $token } into the home column ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] You: token { $token } home ({ $finished }/4).
       *[no] Your token { $token } reaches home. ({ $finished }/4 finished)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }): token { $token } home ({ $finished }/4).
       *[no] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $color }
        }) token { $token } reaches home. ({ $finished }/4 finished)
    }
ludo-you-move-home =
    { $brief ->
        [yes] You: token { $token } +{ $spaces } to home { $position }/{ $total }.
       *[no] You move token { $token } in your home column ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }): token { $token } +{ $spaces } to home { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }) moves token { $token } in the home column ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes] You: capture { $count } of { $captured_player } ({ $captured_color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $captured_color }
        }) to yard.
       *[no] You capture { $count ->
            [one] 1 token
           *[other] { $count } tokens
        } of { $captured_player } ({ $captured_color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $captured_color }
        }) and send { $count ->
            [one] it
           *[other] them
        } back to yard.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }): { $count ->
            [one] your token
           *[other] your { $count } tokens
        } to yard.
       *[no] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $color }
        }) captures { $count ->
            [one] your token
           *[other] { $count } of your tokens
        } and sends { $count ->
            [one] it
           *[other] them
        } back to yard.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $color }
        }): capture { $count } of { $captured_player } ({ $captured_color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
           *[other] { $captured_color }
        }) to yard.
       *[no] { $player } ({ $color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $color }
        }) captures { $count ->
            [one] 1 token
           *[other] { $count } tokens
        } of { $captured_player } ({ $captured_color ->
            [red] Red
            [blue] Blue
            [green] Green
            [yellow] Yellow
            *[other] { $captured_color }
        }). Sent back to yard.
    }
ludo-extra-turn = { $player } rolled a 6. Extra turn.
ludo-you-extra-turn = You rolled a 6. Extra turn.
ludo-you-too-many-sixes = You rolled { $count } sixes in a row. Your moves from this turn sequence are undone, and your turn ends.
ludo-too-many-sixes = { $player } rolled { $count } sixes in a row. Moves undone. Turn ends.
ludo-you-winner = You win! All 4 tokens are home.
ludo-winner = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}) wins! All 4 tokens are home.
ludo-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 token home
   *[other] { $count } tokens home
}

ludo-board-player = { $player } ({ $color ->
    [red] Red
    [blue] Blue
    [green] Green
    [yellow] Yellow
    *[other] { $color }
}): { $finished }/4 finished
ludo-token-yard = Token { $token } (yard)
ludo-token-track =
    { $safe ->
        [yes] Token { $token } (position { $position }, safe square)
       *[no] Token { $token } (position { $position })
    }
ludo-token-home = Token { $token } (home column { $position }/{ $total })
ludo-token-finished = Token { $token } (finished)
ludo-last-roll = Last roll: { $roll }

ludo-set-max-sixes = Max consecutive sixes: { $max_consecutive_sixes }
ludo-enter-max-sixes = Enter max consecutive sixes
ludo-option-changed-max-sixes = Max consecutive sixes set to { $max_consecutive_sixes }.
ludo-set-safe-start-squares = Safe start squares: { $enabled }
ludo-option-changed-safe-start-squares = Safe start squares set to { $enabled }.
