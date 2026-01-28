# Five Card Draw (Poker 5 Lá)

game-name-fivecarddraw = Poker 5 Lá

draw-set-starting-chips = Chip khởi điểm: { $count }
draw-enter-starting-chips = Nhập số chip khởi điểm
draw-option-changed-starting-chips = Chip khởi điểm được đặt là { $count }.

draw-set-ante = Tiền gà (Ante): { $count }
draw-enter-ante = Nhập số tiền gà
draw-option-changed-ante = Tiền gà được đặt là { $count }.

draw-set-turn-timer = Hẹn giờ lượt: { $mode }
draw-select-turn-timer = Chọn kiểu hẹn giờ lượt
draw-option-changed-turn-timer = Hẹn giờ lượt được đặt là { $mode }.

draw-set-raise-mode = Chế độ Tố: { $mode }
draw-select-raise-mode = Chọn chế độ Tố
draw-option-changed-raise-mode = Chế độ Tố được đặt là { $mode }.

draw-set-max-raises = Số lần Tố tối đa: { $count }
draw-enter-max-raises = Nhập số lần Tố tối đa (0 là không giới hạn)
draw-option-changed-max-raises = Số lần Tố tối đa được đặt là { $count }.

draw-antes-posted = Đã góp tiền gà: { $amount }.
draw-betting-round-1 = Vòng cược.
draw-betting-round-2 = Vòng cược.
draw-begin-draw = Giai đoạn đổi bài.
draw-not-draw-phase = Chưa đến lúc đổi bài.
draw-not-betting = Bạn không thể đặt cược trong giai đoạn đổi bài.

draw-toggle-discard = Chọn/Bỏ chọn đổi lá bài số { $index }
draw-card-keep = Giữ lá { $card }
draw-card-discard = Bỏ lá { $card }
draw-card-kept = Giữ lại { $card }.
draw-card-discarded = Sẽ bỏ lá { $card }.
draw-draw-cards = Đổi bài
draw-draw-cards-count = Đổi { $count } { $count ->
    [one] lá bài
   *[other] lá bài
}
draw-dealt-cards = Bạn được chia các lá: { $cards }.
draw-you-drew-cards = Bạn rút được: { $cards }.
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
draw-you-discard-limit = Bạn có thể đổi tối đa { $count } lá bài.
draw-player-discard-limit = { $player } có thể đổi tối đa { $count } lá bài.

# Phím tắt
draw-card-key = Phím tắt lá bài { $index }

# Màn hình kết thúc
draw-winner-chips = { $rank }. { $player }: { $chips } chip
