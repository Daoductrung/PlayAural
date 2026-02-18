game-name-fivecarddraw = Five Card Draw

draw-set-starting-chips = Số chip ban đầu: { $count }
draw-enter-starting-chips = Nhập số chip ban đầu
draw-option-changed-starting-chips = Số chip ban đầu đã được đặt là { $count }.

draw-set-ante = Cược góp: { $count }
draw-enter-ante = Nhập số tiền cược góp
draw-option-changed-ante = Cược góp đã được đặt là { $count }.

draw-set-turn-timer = Thời gian mỗi lượt: { $mode }
draw-select-turn-timer = Chọn thời gian mỗi lượt
draw-option-changed-turn-timer = Thời gian mỗi lượt đã được đặt là { $mode }.

draw-set-raise-mode = Chế độ tố: { $mode }
draw-select-raise-mode = Chọn chế độ tố
draw-option-changed-raise-mode = Chế độ tố đã được đặt là { $mode }.

draw-set-max-raises = Số lần tố tối đa: { $count }
draw-enter-max-raises = Nhập số lần tố tối đa (0 để không giới hạn)
draw-option-changed-max-raises = Số lần tố tối đa đã được đặt là { $count }.

draw-antes-posted = Đã đóng cược góp: { $amount }.
draw-betting-round-1 = Vòng cược.
draw-betting-round-2 = Vòng cược.
draw-begin-draw = Giai đoạn đổi bài.
draw-not-draw-phase = Chưa đến lúc đổi bài.
draw-not-betting = Bạn không thể cược trong giai đoạn đổi bài.

draw-toggle-discard = Chọn đổi lá bài thứ { $index }
draw-card-keep = Giữ { $card }
draw-card-discard = Bỏ { $card }
draw-card-kept = Giữ { $card }.
draw-card-discarded = Bỏ { $card }.
draw-draw-cards = Đổi bài
draw-draw-cards-count = Đổi { $count } { $count ->
    [one] lá bài
   *[other] lá bài
}
draw-dealt-cards = Bạn được chia { $cards }.
draw-you-drew-cards = Bạn rút được { $cards }.
draw-you-draw = Bạn đổi { $count } { $count ->
    [one] lá bài
   *[other] lá bài
}.
draw-player-draws = { $player } đổi { $count } { $count ->
    [one] lá bài
   *[other] lá bài
}.
draw-you-stand-pat = Bạn giữ nguyên bài.
draw-player-stands-pat = { $player } giữ nguyên bài.
draw-you-discard-limit = Bạn có thể bỏ tối đa { $count } lá bài.
draw-player-discard-limit = { $player } có thể bỏ tối đa { $count } lá bài.

draw-card-key = Phím bài { $index }

draw-winner-chips = { $rank }. { $player }: { $chips } chip
