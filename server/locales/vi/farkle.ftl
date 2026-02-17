# Farkle game messages

# Game info
game-name-farkle = Farkle

# Actions - Roll and Bank
farkle-roll = Gieo { $count } { $count ->
    [one] viên
   *[other] viên
}
farkle-bank = Chốt { $points } điểm

# Scoring combination actions (matching v10 exactly)
farkle-take-single-one = Một con 1 được { $points } điểm
farkle-take-single-five = Một con 5 được { $points } điểm
farkle-take-three-kind = Ba con { $number } được { $points } điểm
farkle-take-four-kind = Bốn con { $number } được { $points } điểm
farkle-take-five-kind = Năm con { $number } được { $points } điểm
farkle-take-six-kind = Sáu con { $number } được { $points } điểm
farkle-take-small-straight = Sảnh nhỏ được { $points } điểm
farkle-take-large-straight = Sảnh lớn được { $points } điểm
farkle-take-three-pairs = Ba đôi được { $points } điểm
farkle-take-double-triplets = Hai bộ ba được { $points } điểm
farkle-take-full-house = Cù lũ được { $points } điểm

# Game events (matching v10 exactly)
farkle-rolls = { $player } gieo { $count } { $count ->
    [one] viên
   *[other] viên
}...
farkle-roll-result = { $dice }
farkle-farkle = FARKLE! { $player } mất { $points } điểm
farkle-takes-combo = { $player } lấy { $combo } được { $points } điểm
farkle-you-take-combo = Bạn lấy { $combo } được { $points } điểm
farkle-hot-dice = Nóng tay! (Được gieo tiếp)
farkle-banks = { $player } chốt { $points } điểm, tổng cộng { $total }
farkle-winner = { $player } thắng với { $score } điểm!
farkle-winners-tie = Hòa nhau! Những người thắng: { $players }

# Check turn score action
farkle-turn-score = { $player } đang có { $points } điểm trong lượt này.
farkle-no-turn = Hiện không có ai đang chơi.

# Farkle-specific options
farkle-set-target-score = Điểm mục tiêu: { $score }
farkle-enter-target-score = Nhập điểm mục tiêu (500-5000):
farkle-option-changed-target = Điểm mục tiêu đã đặt là { $score }.

# Disabled action reasons
farkle-must-take-combo = Bạn phải chọn tổ hợp điểm trước.
farkle-cannot-bank = Bạn không thể chốt điểm lúc này.

# Combo names (for announcements)
farkle-combo-single-1 = Một con 1
farkle-combo-single-5 = Một con 5
farkle-combo-three-kind = Ba con { $number }
farkle-combo-four-kind = Bốn con { $number }
farkle-combo-five-kind = Năm con { $number }
farkle-combo-six-kind = Sáu con { $number }
farkle-combo-small-straight = Sảnh nhỏ
farkle-combo-large-straight = Sảnh lớn
farkle-combo-three-pairs = Ba đôi
farkle-combo-double-triplets = Hai bộ ba
farkle-combo-full-house = Cù lũ

# Formatting
farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } ({ $points } điểm)

farkle-check-turn-score = Xem điểm lượt này
farkle-roll-label = Gieo xúc xắc
farkle-bank-label = Chốt điểm
