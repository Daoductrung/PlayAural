game-name-ludo = Cờ cá ngựa

ludo-roll-die = Gieo xúc xắc
ludo-move-token = Đi quân
ludo-move-token-n = Đi quân { $token }
ludo-check-board = Xem thế cờ
ludo-select-token = Chọn quân để đi:

ludo-roll = { $player } gieo được { $roll }.
ludo-you-roll = Bạn gieo được { $roll }.
ludo-no-moves = { $player } không có nước đi hợp lệ.
ludo-you-no-moves = Bạn không có nước đi hợp lệ.
ludo-error-roll-pending-move = Bạn đã gieo xúc xắc và đang có nước đi hợp lệ. Hãy đi một quân có thể đi trước khi gieo tiếp.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] Bạn: quân { $token } xuất chuồng +{ $spaces } đến ô { $position }, an toàn.
           *[no] Bạn: quân { $token } xuất chuồng +{ $spaces } đến ô { $position }.
        }
       *[no] { $safe ->
            [yes] Bạn xuất chuồng quân { $token } đến ô { $position }, là ô an toàn.
           *[no] Bạn xuất chuồng quân { $token } đến ô { $position }.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }): quân { $token } xuất chuồng +{ $spaces } đến ô { $position }, an toàn.
           *[no] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }): quân { $token } xuất chuồng +{ $spaces } đến ô { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }) cho quân { $token } xuất chuồng đến ô { $position }, là ô an toàn.
           *[no] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }) cho quân { $token } xuất chuồng đến ô { $position }.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] Bạn: quân { $token } +{ $spaces } đến ô { $position }, an toàn.
           *[no] Bạn: quân { $token } +{ $spaces } đến ô { $position }.
        }
       *[no] { $safe ->
            [yes] Bạn đi quân { $token } đến ô { $position }, là ô an toàn.
           *[no] Bạn đi quân { $token } đến ô { $position }.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }): quân { $token } +{ $spaces } đến ô { $position }, an toàn.
           *[no] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }): quân { $token } +{ $spaces } đến ô { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }) đi quân { $token } đến ô { $position }, là ô an toàn.
           *[no] { $player } ({ $color ->
                [red] Đỏ
                [blue] Xanh dương
                [green] Xanh lá
                [yellow] Vàng
               *[other] { $color }
            }) đi quân { $token } đến ô { $position }.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] Bạn: quân { $token } +{ $spaces } đến đường về { $position }/{ $total }.
       *[no] Bạn đưa quân { $token } vào đường về đích ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }): quân { $token } +{ $spaces } đến đường về { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $color }
        }) đưa quân { $token } vào đường về đích ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] Bạn: quân { $token } về đích ({ $finished }/4).
       *[no] Quân { $token } của bạn đã về đích. ({ $finished }/4 quân về đích)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }): quân { $token } về đích ({ $finished }/4).
       *[no] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $color }
        }) đưa quân { $token } về đích. ({ $finished }/4 quân về đích)
    }
ludo-you-move-home =
    { $brief ->
        [yes] Bạn: quân { $token } +{ $spaces } đến đường về { $position }/{ $total }.
       *[no] Bạn đi quân { $token } trên đường về đích ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }): quân { $token } +{ $spaces } đến đường về { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }) đi quân { $token } trên đường về đích ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes] Bạn: đá { $count } quân của { $captured_player } ({ $captured_color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $captured_color }
        }) về chuồng.
       *[no] Bạn đá { $count ->
            [one] 1 quân
           *[other] { $count } quân
        } của { $captured_player } ({ $captured_color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $captured_color }
        }) về chuồng.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }): { $count } quân của bạn về chuồng.
       *[no] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $color }
        }) đá { $count ->
            [one] quân của bạn
           *[other] { $count } quân của bạn
        } về chuồng.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $color }
        }): đá { $count } quân của { $captured_player } ({ $captured_color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
           *[other] { $captured_color }
        }) về chuồng.
       *[no] { $player } ({ $color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $color }
        }) đá { $count ->
            [one] 1 quân
           *[other] { $count } quân
        } của { $captured_player } ({ $captured_color ->
            [red] Đỏ
            [blue] Xanh dương
            [green] Xanh lá
            [yellow] Vàng
            *[other] { $captured_color }
        }) về chuồng.
    }
ludo-extra-turn = { $player } gieo được 6 và có thêm lượt.
ludo-you-extra-turn = Bạn gieo được 6 và được thêm lượt.
ludo-you-too-many-sixes = Bạn gieo { $count } lần 6 liên tiếp. Các nước đi trong chuỗi lượt này của bạn bị hoàn tác, và lượt của bạn kết thúc.
ludo-too-many-sixes = { $player } gieo { $count } lần 6 liên tiếp. Các nước đi trong chuỗi lượt này bị hoàn tác.
ludo-you-winner = Bạn thắng! Cả 4 quân đã về đích.
ludo-winner = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) thắng! Cả 4 quân đã về đích.
ludo-end-score-line = { $index }. { $player }: { $count } quân về đích

ludo-board-player = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}): { $finished }/4 quân về đích
ludo-token-yard = Quân { $token } (trong chuồng)
ludo-token-track =
    { $safe ->
        [yes] Quân { $token } (ô { $position }, ô an toàn)
       *[no] Quân { $token } (ô { $position })
    }
ludo-token-home = Quân { $token } (đường về đích { $position }/{ $total })
ludo-token-finished = Quân { $token } (đã về đích)
ludo-last-roll = Lần gieo gần nhất: { $roll }

ludo-set-max-sixes = Số lần 6 liên tiếp tối đa: { $max_consecutive_sixes }
ludo-enter-max-sixes = Nhập số lần 6 liên tiếp tối đa
ludo-option-changed-max-sixes = Số lần 6 liên tiếp tối đa đã đổi thành { $max_consecutive_sixes }.
ludo-set-safe-start-squares = Ô xuất phát an toàn: { $enabled }
ludo-option-changed-safe-start-squares = Ô xuất phát an toàn đã đổi thành { $enabled }.
