# Thông báo trò chơi Một Bốn Hai Tư (Midnight)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, điểm mục tiêu nằm trong games.ftl

# Thông tin trò chơi
game-name-midnight = Một Bốn Hai Tư (1-4-24)
midnight-category = Game Xúc Xắc

# Hành động
midnight-roll = Gieo xúc xắc
midnight-keep-die = Giữ con { $value }
midnight-bank = Chốt điểm

# Sự kiện trò chơi
midnight-turn-start = Lượt của { $player }.
midnight-you-rolled = Bạn gieo được: { $dice }.
midnight-player-rolled = { $player } gieo được: { $dice }.

# Giữ xúc xắc
midnight-you-keep = Bạn giữ con { $die }.
midnight-player-keeps = { $player } giữ con { $die }.
midnight-you-unkeep = Bạn bỏ giữ con { $die }.
midnight-player-unkeeps = { $player } bỏ giữ con { $die }.

# Trạng thái lượt
midnight-you-have-kept = Đã giữ: { $kept }. Còn lại: { $remaining }.
midnight-player-has-kept = { $player } đã giữ: { $kept }. Còn lại { $remaining } xúc xắc.

# Ghi điểm
midnight-you-scored = Bạn ghi được { $score } điểm.
midnight-scored = { $player } ghi được { $score } điểm.
midnight-you-disqualified = Bạn không có đủ 1 và 4. Bị loại!
midnight-player-disqualified = { $player } không có đủ 1 và 4. Bị loại!

# Kết quả vòng
midnight-round-winner = { $player } thắng vòng này!
midnight-round-tie = Vòng này hòa giữa { $players }.
midnight-all-disqualified = Tất cả người chơi đều bị loại! Vòng này không có người thắng.

# Người thắng chung cuộc
midnight-game-winner = { $player } thắng chung cuộc với { $wins } vòng thắng!
midnight-game-tie = Hòa chung cuộc! { $players } mỗi người thắng { $wins } vòng.

# Tùy chọn
midnight-set-rounds = Số vòng chơi: { $rounds }
midnight-enter-rounds = Nhập số vòng chơi:
midnight-option-changed-rounds = Số vòng chơi đã đổi thành { $rounds }

# Lý do hành động bị vô hiệu hóa
midnight-need-to-roll = Bạn cần gieo xúc xắc trước.
midnight-no-dice-to-keep = Không có xúc xắc nào để giữ.
midnight-must-keep-one = Bạn phải giữ ít nhất một xúc xắc mỗi lần gieo.
midnight-must-roll-first = Bạn phải gieo xúc xắc trước.
# Dòng này bị lặp trong file gốc, tôi vẫn dịch để đảm bảo tính toàn vẹn
midnight-must-roll-first = Bạn phải gieo xúc xắc trước.
midnight-keep-all-first = Bạn phải giữ tất cả xúc xắc trước khi chốt điểm.

# Nhãn xúc xắc
midnight-die-locked = { $value } (Đã khóa)
midnight-die-kept = { $value } (Đã giữ)
midnight-die-value = { $value }

# Màn hình kết thúc
midnight-end-score = { $rank }. { $player }: thắng { $wins } { $wins ->
    [one] vòng
   *[other] vòng
}

midnight-die-index = Xúc xắc {  }
