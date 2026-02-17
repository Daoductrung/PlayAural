# Messages for Left Right Center (English)

# Game name
game-name-leftrightcenter = Left Right Center

# Actions
lrc-roll = Gieo { $count } { $count ->
    [one] viên
   *[other] viên
}

# Dice faces
lrc-face-left = Trái
lrc-face-right = Phải
lrc-face-center = Giữa
lrc-face-dot = Chấm

# Game events
lrc-roll-results = { $player } gieo được { $results }.
lrc-pass-left = { $player } chuyển { $count } { $count ->
    [one] chip
   *[other] chip
} cho { $target }.
lrc-pass-right = { $player } chuyển { $count } { $count ->
    [one] chip
   *[other] chip
} cho { $target }.
lrc-pass-center = { $player } bỏ { $count } { $count ->
    [one] chip
   *[other] chip
} vào giữa.
lrc-no-chips = { $player } không còn chip để gieo.
lrc-center-pot = { $count } { $count ->
    [one] chip
   *[other] chip
} ở giữa.
lrc-player-chips = { $player } hiện có { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-winner = { $player } thắng với { $count } { $count ->
    [one] chip
   *[other] chip
}!

# Options
lrc-set-starting-chips = Số chip ban đầu: { $count }
lrc-enter-starting-chips = Nhập số chip ban đầu:
lrc-option-changed-starting-chips = Số chip ban đầu đã được đặt là { $count }.

# Formatting
lrc-line-format = { $player }: { $chips }
lrc-check-center = Kiểm tra hũ giữa
lrc-roll-label = Gieo xúc xắc
