# Thông báo trò chơi Bài Chổi (Scopa)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, điểm mục tiêu, chế độ đội nằm trong games.ftl

# Tên trò chơi
game-name-scopa = Bài Chổi (Scopa)

# Sự kiện trò chơi
scopa-initial-table = Bài trên bàn: { $cards }
scopa-no-initial-table = Không có bài nào trên bàn để bắt đầu.
scopa-you-collect = Bạn dùng { $card } ăn được { $cards }
scopa-player-collects = { $player } dùng { $card } ăn được { $cards }
scopa-you-put-down = Bạn đánh ra { $card }.
scopa-player-puts-down = { $player } đánh ra { $card }.
scopa-scopa-suffix =  - SCOPA! (QUÉT SẠCH!)
scopa-clear-table-suffix = , quét sạch bàn chơi.
scopa-remaining-cards = { $player } nhận các lá bài còn lại trên bàn.
scopa-scoring-round = Đang tính điểm...
scopa-most-cards = { $player } được 1 điểm nhờ có nhiều lá bài nhất ({ $count } lá).
scopa-most-cards-tie = Số lượng lá bài bằng nhau - không ai được điểm.
scopa-most-diamonds = { $player } được 1 điểm nhờ có nhiều lá Rô nhất ({ $count } lá Rô).
scopa-most-diamonds-tie = Số lượng lá Rô bằng nhau - không ai được điểm.
scopa-seven-diamonds = { $player } được 1 điểm nhờ có lá 7 Rô.
scopa-seven-diamonds-multi = { $player } được 1 điểm nhờ có nhiều lá 7 Rô nhất ({ $count } × 7 Rô).
scopa-seven-diamonds-tie = Số lượng 7 Rô bằng nhau - không ai được điểm.
scopa-most-sevens = { $player } được 1 điểm nhờ có nhiều lá 7 nhất ({ $count } lá 7).
scopa-most-sevens-tie = Số lượng lá 7 bằng nhau - không ai được điểm.
scopa-round-scores = Điểm số vòng này:
scopa-round-score-line = { $player }: +{ $round_score } (tổng: { $total_score })
scopa-table-empty = Không có lá bài nào trên bàn.
scopa-no-such-card = Không có lá bài nào ở vị trí đó.
scopa-captured-count = Bạn đã ăn được { $count } lá bài

# Hành động xem
scopa-view-table = Xem bài trên bàn
scopa-view-captured = Xem bài đã ăn
scopa-view-table-card = Xem lá bài trên bàn số { $index }
scopa-pause-timer = Tạm dừng đồng hồ

# Gợi ý nước đi
scopa-hint-match =  -> ăn { $card }
scopa-hint-multi =  -> ăn { $count } lá bài

# Tùy chọn riêng cho Scopa
scopa-enter-target-score = Nhập điểm mục tiêu (1-121)
scopa-set-cards-per-deal = Số lá mỗi lần chia: { $cards }
scopa-enter-cards-per-deal = Nhập số lá mỗi lần chia (1-10)
scopa-set-decks = Số bộ bài: { $decks }
scopa-enter-decks = Nhập số bộ bài (1-6)
scopa-toggle-escoba = Escoba (tổng bằng 15): { $enabled }
scopa-toggle-hints = Hiển thị gợi ý nước ăn bài: { $enabled }
scopa-set-mechanic = Cơ chế Scopa: { $mechanic }
scopa-select-mechanic = Chọn cơ chế Scopa
scopa-toggle-instant-win = Thắng ngay lập tức khi Scopa: { $enabled }
scopa-toggle-team-scoring = Gom chung bài của đội để tính điểm: { $enabled }
scopa-toggle-inverse = Chế độ Đảo ngược (đạt điểm mục tiêu là bị loại): { $enabled }

# Thông báo thay đổi tùy chọn
scopa-option-changed-cards = Số lá mỗi lần chia được đặt là { $cards }.
scopa-option-changed-decks = Số bộ bài được đặt là { $decks }.
scopa-option-changed-escoba = Chế độ Escoba { $enabled }.
scopa-option-changed-hints = Gợi ý nước ăn bài { $enabled }.
scopa-option-changed-mechanic = Cơ chế Scopa được đặt là { $mechanic }.
scopa-option-changed-instant = Thắng ngay lập tức khi Scopa { $enabled }.
scopa-option-changed-team-scoring = Tính điểm chung cho đội { $enabled }.
scopa-option-changed-inverse = Chế độ Đảo ngược { $enabled }.

# Các lựa chọn cơ chế Scopa
scopa-mechanic-normal = Bình thường
scopa-mechanic-no_scopas = Không tính Scopa (Quét bàn không có điểm)
scopa-mechanic-only_scopas = Chỉ tính điểm Scopa

# Lý do hành động bị vô hiệu hóa
scopa-timer-not-active = Đồng hồ vòng chơi đang không hoạt động.

# Lỗi xác thực
scopa-error-not-enough-cards = Không đủ bài trong { $decks } { $decks ->
    [one] bộ bài
   *[other] bộ bài
} để chia cho { $players } { $players ->
    [one] người chơi
   *[other] người chơi
} với { $cards_per_deal } lá mỗi người. (Cần { $cards_per_deal } × { $players } = { $cards_needed } lá, nhưng chỉ có { $total_cards } lá.)

# Định dạng
scopa-line-format = {  }. {  }: {  }
