# Toss Up game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-tossup = Toss Up
tossup-category = Game xúc xắc

# Actions
tossup-roll-first = Gieo { $count } xúc xắc
tossup-roll-remaining = Gieo { $count } xúc xắc còn lại
tossup-bank = Chốt { $points } điểm

# Game events
tossup-turn-start = Lượt của { $player }. Điểm: { $score }
tossup-you-roll = Bạn gieo được: { $results }.
tossup-player-rolls = { $player } gieo được: { $results }.

tossup-result-green = { $count } xanh
tossup-result-yellow = { $count } vàng
tossup-result-red = { $count } đỏ

# Turn status
tossup-you-have-points = Điểm lượt này: { $turn_points }. Xúc xắc còn lại: { $dice_count }.
tossup-player-has-points = { $player } có { $turn_points } điểm lượt này. Còn { $dice_count } xúc xắc.

# Fresh dice
tossup-you-get-fresh = Hết xúc xắc! Nhận lại { $count } xúc xắc mới.
tossup-player-gets-fresh = { $player } nhận lại { $count } xúc xắc mới.

# Bust
tossup-you-bust = Mất trắng! Bạn mất { $points } điểm trong lượt này.
tossup-player-busts = { $player } mất trắng và mất { $points } điểm!

# Bank
tossup-you-bank = Bạn chốt { $points } điểm. Tổng điểm: { $total }.
tossup-player-banks = { $player } chốt { $points } điểm. Tổng điểm: { $total }.

# Winner
tossup-winner = { $player } thắng với { $score } điểm!
tossup-tie-tiebreaker = Hòa giữa { $players }! Vào vòng phân định thắng thua!

# Options
tossup-set-rules-variant = Biến thể luật: { $variant }
tossup-select-rules-variant = Chọn biến thể luật:
tossup-option-changed-rules = Biến thể luật đã đổi thành { $variant }

tossup-set-starting-dice = Số xúc xắc ban đầu: { $count }
tossup-enter-starting-dice = Nhập số lượng xúc xắc ban đầu:
tossup-option-changed-dice = Số xúc xắc ban đầu đã đổi thành { $count }

# Rules variants
tossup-rules-standard = Tiêu chuẩn
tossup-rules-PlayAural = PlayAural

# Rules explanations
tossup-rules-standard-desc = 3 xanh, 2 vàng, 1 đỏ mỗi viên. Mất trắng nếu không có màu xanh và có ít nhất một màu đỏ.
tossup-rules-PlayAural-desc = Phân bố đều. Mất trắng nếu tất cả xúc xắc đều là màu đỏ.

# Disabled reasons
tossup-need-points = Bạn cần có điểm mới chốt được.

# Formatting
tossup-line-format = { $rank }. { $player }: { $points }
