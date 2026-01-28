# Five Card Draw (Poker Rút 5 Lá)

game-name-fivecarddraw = Poker Rút 5 Lá

draw-set-starting-chips = Chip khởi điểm: { $count }
draw-enter-starting-chips = Nhập số chip khởi điểm
draw-option-changed-starting-chips = Số chip khởi điểm đã đặt là { $count }.

draw-set-ante = Cược đáy (Ante): { $count }
draw-enter-ante = Nhập số tiền cược đáy
draw-option-changed-ante = Cược đáy đã đặt là { $count }.

draw-set-turn-timer = Thời gian lượt: { $mode }
draw-select-turn-timer = Chọn thời gian lượt
draw-option-changed-turn-timer = Thời gian lượt đã đặt là { $mode }.

draw-set-raise-mode = Chế độ tố: { $mode }
draw-select-raise-mode = Chọn chế độ tố
draw-option-changed-raise-mode = Chế độ tố đã đặt là { $mode }.

draw-set-max-raises = Tố tối đa: { $count } lần
draw-enter-max-raises = Nhập số lần tố tối đa (0 là không giới hạn)
draw-option-changed-max-raises = Số lần tố tối đa đã đặt là { $count }.

draw-antes-posted = Đã đặt cược đáy: { $amount }.
draw-betting-round-1 = Vòng cược.
draw-betting-round-2 = Vòng cược.
draw-begin-draw = Giai đoạn đổi bài.
draw-not-draw-phase = Chưa đến lúc rút bài.
draw-not-betting = Bạn không thể cược trong giai đoạn đổi bài.

draw-toggle-discard = Chọn bỏ lá bài thứ { $index }
draw-card-keep = Giữ { $card }
draw-card-discard = Bỏ { $card }
draw-card-kept = Giữ { $card }.
draw-card-discarded = Bỏ { $card }.
draw-draw-cards = Đổi bài
draw-draw-cards-count = Đổi { $count } { $count ->
    [one] lá
   *[other] lá
}
draw-dealt-cards = Bạn được chia { $cards }.
draw-you-drew-cards = Bạn rút được { $cards }.
draw-you-draw = Bạn đổi { $count } { $count ->
    [one] lá
   *[other] lá
}.
draw-player-draws = { $player } đổi { $count } { $count ->
    [one] lá
   *[other] lá
}.
draw-you-stand-pat = Bạn giữ nguyên bài.
draw-player-stands-pat = { $player } giữ nguyên bài.
draw-you-discard-limit = Bạn có thể bỏ tối đa { $count } lá.
draw-player-discard-limit = { $player } có thể bỏ tối đa { $count } lá.

# Phím tắt chọn bài
draw-card-key = Phím bài { $index }

# Màn hình kết thúc
draw-winner-chips = { $rank }. { $player }: { $chips } chip
