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
ludo-enter-board = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) cho quân { $token } xuất chuồng.
ludo-move-track = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) đi quân { $token } đến ô { $position }.
ludo-enter-home = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) đưa quân { $token } vào đường về đích.
ludo-home-finish = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) đưa quân { $token } về đích. ({ $finished }/4 quân về đích)
ludo-move-home = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) đi quân { $token } trên đường về đích ({ $position }/{ $total }).
ludo-captures = { $player } ({ $color ->
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
ludo-extra-turn = { $player } gieo được 6 và có thêm lượt.
ludo-you-extra-turn = Bạn gieo được 6 và được thêm lượt.
ludo-too-many-sixes = { $player } gieo { $count } lần 6 liên tiếp. Các nước đi trong chuỗi lượt này bị hoàn tác.
ludo-winner = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}) thắng! Cả 4 quân đã về đích.

ludo-board-player = { $player } ({ $color ->
    [red] Đỏ
    [blue] Xanh dương
    [green] Xanh lá
    [yellow] Vàng
    *[other] { $color }
}): { $finished }/4 quân về đích
ludo-token-yard = Quân { $token } (trong chuồng)
ludo-token-track = Quân { $token } (ô { $position })
ludo-token-home = Quân { $token } (đường về đích { $position }/{ $total })
ludo-token-finished = Quân { $token } (đã về đích)
ludo-last-roll = Lần gieo gần nhất: { $roll }

ludo-set-max-sixes = Số lần 6 liên tiếp tối đa: { $max_consecutive_sixes }
ludo-enter-max-sixes = Nhập số lần 6 liên tiếp tối đa
ludo-option-changed-max-sixes = Số lần 6 liên tiếp tối đa đã đổi thành { $max_consecutive_sixes }.
ludo-set-safe-start-squares = Ô xuất phát an toàn: { $enabled }
ludo-option-changed-safe-start-squares = Ô xuất phát an toàn đã đổi thành { $enabled }.
