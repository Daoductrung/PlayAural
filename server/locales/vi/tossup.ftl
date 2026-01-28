# Thông báo trò chơi Tung Hứng (Toss Up)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, điểm mục tiêu nằm trong games.ftl

# Thông tin trò chơi
game-name-tossup = Tung Hứng (Toss Up)
tossup-category = Game Xúc Xắc

# Hành động
tossup-roll-first = Gieo { $count } xúc xắc
tossup-roll-remaining = Gieo { $count } xúc xắc còn lại
tossup-bank = Chốt { $points } điểm

# Sự kiện trò chơi
tossup-turn-start = Lượt của { $player }. Điểm: { $score }
tossup-you-roll = Bạn gieo được: { $results }.
tossup-player-rolls = { $player } gieo được: { $results }.

tossup-result-green = { $count } xanh
tossup-result-yellow = { $count } vàng
tossup-result-red = { $count } đỏ

# Trạng thái lượt
tossup-you-have-points = Điểm lượt: { $turn_points }. Còn lại: { $dice_count } xúc xắc.
tossup-player-has-points = { $player } có { $turn_points } điểm lượt. Còn lại { $dice_count } xúc xắc.

# Xúc xắc mới (khi đã dùng hết xúc xắc xanh)
tossup-you-get-fresh = Hết xúc xắc! Nhận lại { $count } xúc xắc mới.
tossup-player-gets-fresh = { $player } nhận lại { $count } xúc xắc mới.

# Mất lượt (Bust)
tossup-you-bust = MẤT TRẮNG! Bạn mất { $points } điểm của lượt này.
tossup-player-busts = { $player } bị mất trắng và mất { $points } điểm!

# Chốt điểm
tossup-you-bank = Bạn chốt { $points } điểm. Tổng điểm: { $total }.
tossup-player-banks = { $player } chốt { $points } điểm. Tổng điểm: { $total }.

# Người thắng
tossup-winner = { $player } thắng với { $score } điểm!
tossup-tie-tiebreaker = Hòa giữa { $players }! Vào vòng phân định thắng thua!

# Tùy chọn
tossup-set-rules-variant = Biến thể luật: { $variant }
tossup-select-rules-variant = Chọn biến thể luật:
tossup-option-changed-rules = Biến thể luật đã đổi thành { $variant }

tossup-set-starting-dice = Số xúc xắc khởi điểm: { $count }
tossup-enter-starting-dice = Nhập số lượng xúc xắc khởi điểm:
tossup-option-changed-dice = Số xúc xắc khởi điểm đổi thành { $count }

# Các biến thể luật
tossup-rules-standard = Tiêu chuẩn
tossup-rules-PlayAural = PlayAural

# Giải thích luật
tossup-rules-standard-desc = Mỗi xúc xắc có 3 mặt xanh, 2 mặt vàng, 1 mặt đỏ. Mất trắng nếu không có mặt xanh nào và có ít nhất một mặt đỏ.
tossup-rules-PlayAural-desc = Phân bố màu đều nhau. Mất trắng nếu tất cả xúc xắc đều là màu đỏ.

# Lý do hành động bị vô hiệu hóa
tossup-need-points = Bạn cần có điểm mới được chốt.

# Định dạng
tossup-line-format = {  }. {  }: {  }
