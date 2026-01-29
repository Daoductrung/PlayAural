# Thông báo cho trò chơi Trái Phải Giữa (Left Right Center)

# Tên trò chơi
game-name-leftrightcenter = Trái Phải Giữa

# Hành động
lrc-roll = Gieo { $count } { $count ->
    [one] xúc xắc
   *[other] xúc xắc
}

# Các mặt xúc xắc
lrc-face-left = Trái
lrc-face-right = Phải
lrc-face-center = Giữa
lrc-face-dot = Chấm

# Sự kiện trò chơi
lrc-roll-results = { $player } gieo được { $results }.
lrc-pass-left = { $player } chuyển { $count } { $count ->
    [one] chip
   *[other] chip
} sang { $target }.
lrc-pass-right = { $player } chuyển { $count } { $count ->
    [one] chip
   *[other] chip
} sang { $target }.
lrc-pass-center = { $player } bỏ { $count } { $count ->
    [one] chip
   *[other] chip
} vào giữa.
lrc-no-chips = { $player } không còn chip để gieo.
lrc-center-pot = Có { $count } { $count ->
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

# Tùy chọn
lrc-set-starting-chips = Số chip khởi điểm: { $count }
lrc-enter-starting-chips = Nhập số chip khởi điểm:
lrc-option-changed-starting-chips = Số chip khởi điểm được đặt là { $count }.

# Định dạng
lrc-line-format = { $player }: { $chips }
