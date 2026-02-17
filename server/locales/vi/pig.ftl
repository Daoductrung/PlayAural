# Pig game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-pig = Pig
pig-category = Game xúc xắc

# Actions
pig-roll = Gieo xúc xắc
pig-bank = Chốt { $points } điểm

# Game events (Pig-specific)
pig-rolls = { $player } gieo xúc xắc...
pig-roll-result = Được { $roll }, tổng cộng là { $total }
pig-bust = Ôi không, gieo phải 1! { $player } mất { $points } điểm.
pig-bank-action = { $player } quyết định chốt { $points } điểm, tổng cộng là { $total }
pig-winner = Chúng ta đã có người chiến thắng, đó là { $player }!

# Pig-specific options
pig-set-min-bank = Điểm chốt tối thiểu: { $points }
pig-set-dice-sides = Số mặt xúc xắc: { $sides }
pig-enter-min-bank = Nhập số điểm chốt tối thiểu:
pig-enter-dice-sides = Nhập số mặt của xúc xắc:
pig-option-changed-min-bank = Điểm chốt tối thiểu đã đổi thành { $points }
pig-option-changed-dice = Xúc xắc giờ có { $sides } mặt

# Disabled reasons
pig-need-more-points = Bạn cần thêm điểm mới được chốt.

# Validation errors
pig-error-min-bank-too-high = Điểm chốt tối thiểu phải thấp hơn điểm mục tiêu.

# Formatting
pig-line-format = { $rank }. { $player }: { $points }
