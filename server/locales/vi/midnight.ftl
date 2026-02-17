# 1-4-24 (Midnight) game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-midnight = 1-4-24
midnight-category = Game xúc xắc

# Actions
midnight-roll = Gieo xúc xắc
midnight-keep-die = Giữ { $value }
midnight-bank = Chốt điểm

# Game events
midnight-turn-start = Lượt của { $player }.
midnight-you-rolled = Bạn gieo được: { $dice }.
midnight-player-rolled = { $player } gieo được: { $dice }.

# Keeping dice
midnight-you-keep = Bạn giữ { $die }.
midnight-player-keeps = { $player } giữ { $die }.
midnight-you-unkeep = Bạn bỏ giữ { $die }.
midnight-player-unkeeps = { $player } bỏ giữ { $die }.

# Turn status
midnight-you-have-kept = Đã giữ: { $kept }. Số lần gieo còn lại: { $remaining }.
midnight-player-has-kept = { $player } đã giữ: { $kept }. Còn { $remaining } viên xúc xắc.

# Scoring
midnight-you-scored = Bạn được { $score } điểm.
midnight-scored = { $player } được { $score } điểm.
midnight-you-disqualified = Bạn không có cả 1 và 4. Không đủ điều kiện!
midnight-player-disqualified = { $player } không có cả 1 và 4. Không đủ điều kiện!

# Round results
midnight-round-winner = { $player } thắng vòng này!
midnight-round-tie = Vòng này hòa giữa { $players }.
midnight-all-disqualified = Tất cả người chơi đều không đủ điều kiện! Vòng này không có người thắng.

# Game winner
midnight-game-winner = { $player } thắng chung cuộc với { $wins } vòng thắng!
midnight-game-tie = Hòa nhau! { $players } mỗi người thắng { $wins } vòng.

# Options
midnight-set-rounds = Số vòng chơi: { $rounds }
midnight-enter-rounds = Nhập số vòng chơi:
midnight-option-changed-rounds = Số vòng chơi đã đổi thành { $rounds }

# Disabled reasons
midnight-need-to-roll = Bạn cần gieo xúc xắc trước.
midnight-no-dice-to-keep = Không có xúc xắc nào để giữ.
midnight-must-keep-one = Bạn phải giữ ít nhất một viên mỗi lần gieo.
midnight-must-roll-first = Bạn phải gieo xúc xắc trước.
midnight-must-roll-first = Bạn phải gieo xúc xắc trước.
midnight-keep-all-first = Bạn phải giữ tất cả xúc xắc trước khi chốt điểm.

# Dice labels
midnight-die-locked = { $value } (Đã khóa)
midnight-die-kept = { $value } (Đang giữ)
midnight-die-value = { $value }

# End Screen
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}

midnight-die-index = Viên { $index }
