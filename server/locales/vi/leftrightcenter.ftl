# Thông báo cho trò chơi Left Right Center

# Tên trò chơi
game-name-leftrightcenter = Left Right Center

# Hành động
lrc-roll = Gieo { $count } { $count ->
    [one] viên
   *[other] viên
}

# Các mặt xúc xắc
lrc-face-left = Trái
lrc-face-right = Phải
lrc-face-center = Giữa
lrc-face-dot = Chấm

# Sự kiện trong game
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
lrc-center-pot = Giữa bàn đang có { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-player-chips = { $player } hiện có { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-winner = { $player } thắng với { $count } { $count ->
    [one] chip
   *[other] chip
}!

# Tùy chọn
lrc-set-starting-chips = Chip khởi điểm: { $count }
lrc-enter-starting-chips = Nhập số chip khởi điểm:
lrc-option-changed-starting-chips = Số chip khởi điểm đã đặt là { $count }.

# ?nh d?ng
lrc-line-format = {  }: {  }

# Định dạng
lrc-line-format = {  }: {  }
