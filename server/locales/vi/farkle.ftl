# Thông báo trò chơi Farkle

# Thông tin trò chơi
game-name-farkle = Farkle

# Hành động - Gieo và Chốt điểm
farkle-roll = Gieo { $count } { $count ->
    [one] xúc xắc
   *[other] xúc xắc
}
farkle-bank = Chốt { $points } điểm

# Hành động chọn tổ hợp điểm (khớp chính xác với v10)
farkle-take-single-one = Lấy con 1 lẻ được { $points } điểm
farkle-take-single-five = Lấy con 5 lẻ được { $points } điểm
farkle-take-three-kind = Lấy bộ ba con { $number } được { $points } điểm
farkle-take-four-kind = Lấy bộ bốn con { $number } được { $points } điểm
farkle-take-five-kind = Lấy bộ năm con { $number } được { $points } điểm
farkle-take-six-kind = Lấy bộ sáu con { $number } được { $points } điểm
farkle-take-small-straight = Lấy Sảnh nhỏ được { $points } điểm
farkle-take-large-straight = Lấy Sảnh lớn được { $points } điểm
farkle-take-three-pairs = Lấy Ba đôi được { $points } điểm
farkle-take-double-triplets = Lấy Hai bộ ba được { $points } điểm
farkle-take-full-house = Lấy Cù lũ được { $points } điểm

# Sự kiện trò chơi (khớp chính xác với v10)
farkle-rolls = { $player } gieo { $count } { $count ->
    [one] xúc xắc
   *[other] xúc xắc
}...
farkle-roll-result = { $dice }
farkle-farkle = FARKLE! { $player } mất { $points } điểm.
farkle-takes-combo = { $player } lấy { $combo } được { $points } điểm
farkle-you-take-combo = Bạn lấy { $combo } được { $points } điểm
farkle-hot-dice = Ăn trọn bộ!
farkle-banks = { $player } chốt { $points } điểm, nâng tổng điểm lên { $total }
farkle-winner = { $player } thắng với { $score } điểm!
farkle-winners-tie = Hòa nhau! Những người thắng cuộc: { $players }

# Hành động kiểm tra điểm lượt
farkle-turn-score = { $player } hiện có { $points } điểm trong lượt này.
farkle-no-turn = Hiện không có ai đang thực hiện lượt.

# Tùy chọn riêng cho Farkle
farkle-set-target-score = Điểm mục tiêu: { $score }
farkle-enter-target-score = Nhập điểm mục tiêu (500-5000):
farkle-option-changed-target = Điểm mục tiêu được đặt là { $score }.

# Lý do hành động bị vô hiệu hóa
farkle-must-take-combo = Bạn phải chọn một tổ hợp ăn điểm trước.
farkle-cannot-bank = Bạn không thể chốt điểm vào lúc này.

# Tên các tổ hợp (dùng cho thông báo)
farkle-combo-single-1 = Con 1 lẻ
farkle-combo-single-5 = Con 5 lẻ
farkle-combo-three-kind = Bộ ba con { $number }
farkle-combo-four-kind = Bộ bốn con { $number }
farkle-combo-five-kind = Bộ năm con { $number }
farkle-combo-six-kind = Bộ sáu con { $number }
farkle-combo-small-straight = Sảnh nhỏ
farkle-combo-large-straight = Sảnh lớn
farkle-combo-three-pairs = Ba đôi
farkle-combo-double-triplets = Hai bộ ba
farkle-combo-full-house = Cù lũ

# Định dạng
farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } được { $points } điểm

farkle-check-turn-score = Kiểm tra điểm lượt này
farkle-roll-label = Gieo xúc xắc
farkle-bank-label = Chốt điểm
