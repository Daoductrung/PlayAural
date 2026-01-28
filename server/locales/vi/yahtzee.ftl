# Thông báo trò chơi Yahtzee

# Thông tin trò chơi
game-name-yahtzee = Yahtzee

# Hành động - Gieo xúc xắc
yahtzee-roll = Gieo lại (còn { $count } lần)
yahtzee-roll-all = Gieo xúc xắc

# Các mục ghi điểm Phần Trên
yahtzee-score-ones = Mặt 1 lấy { $points } điểm
yahtzee-score-twos = Mặt 2 lấy { $points } điểm
yahtzee-score-threes = Mặt 3 lấy { $points } điểm
yahtzee-score-fours = Mặt 4 lấy { $points } điểm
yahtzee-score-fives = Mặt 5 lấy { $points } điểm
yahtzee-score-sixes = Mặt 6 lấy { $points } điểm

# Các mục ghi điểm Phần Dưới
yahtzee-score-three-kind = Bộ ba (3 con giống nhau) lấy { $points } điểm
yahtzee-score-four-kind = Bộ bốn (4 con giống nhau) lấy { $points } điểm
yahtzee-score-full-house = Cù lũ lấy { $points } điểm
yahtzee-score-small-straight = Sảnh nhỏ lấy { $points } điểm
yahtzee-score-large-straight = Sảnh lớn lấy { $points } điểm
yahtzee-score-yahtzee = Yahtzee (5 con giống nhau) lấy { $points } điểm
yahtzee-score-chance = Cơ hội (Tổng điểm bất kỳ) lấy { $points } điểm

# Sự kiện trò chơi
yahtzee-you-rolled = Bạn gieo được: { $dice }. Số lần gieo còn lại: { $remaining }
yahtzee-player-rolled = { $player } gieo được: { $dice }. Số lần gieo còn lại: { $remaining }

# Thông báo ghi điểm
yahtzee-you-scored = Bạn ghi { $points } điểm vào ô { $category }.
yahtzee-player-scored = { $player } ghi { $points } điểm vào ô { $category }.

# Thưởng Yahtzee
yahtzee-you-bonus = Thưởng Yahtzee! +100 điểm
yahtzee-player-bonus = { $player } nhận được thưởng Yahtzee! +100 điểm

# Thưởng Phần Trên
yahtzee-you-upper-bonus = Thưởng phần trên! +35 điểm (tổng phần trên là { $total })
yahtzee-player-upper-bonus = { $player } đạt được thưởng phần trên! +35 điểm
yahtzee-you-upper-bonus-missed = Bạn trượt phần thưởng phần trên (được { $total }, cần 63).
yahtzee-player-upper-bonus-missed = { $player } trượt phần thưởng phần trên.

# Chế độ ghi điểm
yahtzee-choose-category = Chọn một ô để ghi điểm.
yahtzee-continuing = Tiếp tục lượt.

# Kiểm tra trạng thái
yahtzee-check-scoresheet = Kiểm tra bảng điểm
yahtzee-view-dice = Kiểm tra xúc xắc
yahtzee-your-dice = Xúc xắc của bạn: { $dice }.
yahtzee-your-dice-kept = Xúc xắc của bạn: { $dice }. Đang giữ: { $kept }
yahtzee-not-rolled = Bạn chưa gieo xúc xắc.

# Hiển thị bảng điểm
yahtzee-scoresheet-header = === Bảng điểm của { $player } ===
yahtzee-scoresheet-upper = Phần Trên:
yahtzee-scoresheet-lower = Phần Dưới:
yahtzee-scoresheet-category-filled = { $category }: { $points }
yahtzee-scoresheet-category-open = { $category }: -
yahtzee-scoresheet-upper-total-bonus = Tổng Phần Trên: { $total } (THƯỞNG: +35)
yahtzee-scoresheet-upper-total-needed = Tổng Phần Trên: { $total } (cần thêm { $needed } để thưởng)
yahtzee-scoresheet-yahtzee-bonus = Thưởng Yahtzee: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = TỔNG ĐIỂM: { $total }

# Tên các danh mục (dùng cho thông báo)
yahtzee-category-ones = Mặt 1
yahtzee-category-twos = Mặt 2
yahtzee-category-threes = Mặt 3
yahtzee-category-fours = Mặt 4
yahtzee-category-fives = Mặt 5
yahtzee-category-sixes = Mặt 6
yahtzee-category-three-kind = Bộ ba
yahtzee-category-four-kind = Bộ bốn
yahtzee-category-full-house = Cù lũ
yahtzee-category-small-straight = Sảnh nhỏ
yahtzee-category-large-straight = Sảnh lớn
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Cơ hội

# Kết thúc trò chơi
yahtzee-winner = { $player } thắng với { $score } điểm!
yahtzee-winners-tie = Hòa nhau! { $players } đều đạt { $score } điểm!

# Tùy chọn
yahtzee-set-rounds = Số ván chơi: { $rounds }
yahtzee-enter-rounds = Nhập số ván chơi (1-10):
yahtzee-option-changed-rounds = Số ván chơi được đặt là { $rounds }.

# Lý do hành động bị vô hiệu hóa
yahtzee-no-rolls-left = Bạn không còn lượt gieo nào.
yahtzee-roll-first = Bạn cần gieo xúc xắc trước.
yahtzee-category-filled = Ô đó đã được ghi điểm rồi.
