# Thông báo trò chơi Xúc Xắc Heo (Pig)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, điểm mục tiêu nằm trong games.ftl

# Thông tin trò chơi
game-name-pig = Xúc Xắc Heo (Pig)
pig-category = Game Xúc Xắc

# Hành động
pig-roll = Gieo xúc xắc
pig-bank = Chốt { $points } điểm

# Sự kiện trò chơi (Riêng cho Pig)
pig-rolls = { $player } gieo xúc xắc...
pig-roll-result = Ra con { $roll }, tổng điểm lượt này là { $total }
pig-bust = Ôi không, con 1! { $player } mất { $points } điểm.
pig-bank-action = { $player } quyết định chốt { $points } điểm, nâng tổng điểm lên { $total }
pig-winner = Chúng ta đã có người chiến thắng, đó là { $player }!

# Tùy chọn riêng cho Pig
pig-set-min-bank = Điểm chốt tối thiểu: { $points }
pig-set-dice-sides = Số mặt xúc xắc: { $sides }
pig-enter-min-bank = Nhập số điểm tối thiểu để được chốt:
pig-enter-dice-sides = Nhập số mặt của xúc xắc:
pig-option-changed-min-bank = Điểm chốt tối thiểu được đổi thành { $points }
pig-option-changed-dice = Xúc xắc bây giờ có { $sides } mặt

# Lý do hành động bị vô hiệu hóa
pig-need-more-points = Bạn cần thêm điểm mới được chốt.

# Lỗi xác thực
pig-error-min-bank-too-high = Điểm chốt tối thiểu phải nhỏ hơn điểm mục tiêu.

# Định dạng
pig-line-format = {  }. {  }: {  }
