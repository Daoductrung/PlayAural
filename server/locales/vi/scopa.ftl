# Scopa game messages
# Note: Common messages like round-start, turn-start, target-score, team-mode are in games.ftl

# Game name
game-name-scopa = Scopa

# Game events
scopa-initial-table = Bài trên bàn: { $cards }
scopa-no-initial-table = Không có bài nào trên bàn để bắt đầu.
scopa-you-collect = Bạn ăn được { $cards } bằng lá { $card }
scopa-player-collects = { $player } ăn được { $cards } bằng lá { $card }
scopa-you-put-down = Bạn đánh xuống lá { $card }.
scopa-player-puts-down = { $player } đánh xuống lá { $card }.
scopa-scopa-suffix =  - SCOPA!
scopa-clear-table-suffix = , quét sạch bàn.
scopa-remaining-cards = { $player } nhận các lá bài còn lại trên bàn.
scopa-scoring-round = Vòng tính điểm...
scopa-most-cards = { $player } được 1 điểm vì nhiều bài nhất ({ $count } lá).
scopa-most-cards-tie = Hòa số lượng bài - không ai được điểm.
scopa-most-diamonds = { $player } được 1 điểm vì nhiều Rô nhất ({ $count } lá Rô).
scopa-most-diamonds-tie = Hòa số lượng Rô - không ai được điểm.
scopa-seven-diamonds = { $player } được 1 điểm vì có lá 7 Rô.
scopa-seven-diamonds-multi = { $player } được 1 điểm vì có nhiều 7 Rô nhất ({ $count } × 7 Rô).
scopa-seven-diamonds-tie = Hòa lá 7 Rô - không ai được điểm.
scopa-most-sevens = { $player } được 1 điểm vì nhiều lá 7 nhất ({ $count } lá 7).
scopa-most-sevens-tie = Hòa số lượng lá 7 - không ai được điểm.
scopa-round-scores = Điểm vòng chơi:
scopa-round-score-line = { $player }: +{ $round_score } (tổng: { $total_score })
scopa-table-empty = Không có bài nào trên bàn.
scopa-no-such-card = Không có bài ở vị trí đó.
scopa-captured-count = Bạn đã ăn được { $count } lá bài

# View actions
scopa-view-table = Xem bàn
scopa-view-captured = Xem bài đã ăn
scopa-view-table-card = Xem lá bài bàn { $index }
scopa-pause-timer = Tạm dừng đồng hồ

# Capture hints
scopa-hint-match =  -> { $card }
scopa-hint-multi =  -> { $count } lá bài

# Scopa-specific options
scopa-enter-target-score = Nhập điểm mục tiêu (1-121)
scopa-set-cards-per-deal = Số bài mỗi lần chia: { $cards }
scopa-enter-cards-per-deal = Nhập số bài mỗi lần chia (1-10)
scopa-set-decks = Số bộ bài: { $decks }
scopa-enter-decks = Nhập số bộ bài (1-6)
scopa-toggle-escoba = Escoba (tổng bằng 15): { $enabled }
scopa-toggle-hints = Hiển thị gợi ý nước ăn bài: { $enabled }
scopa-set-mechanic = Cơ chế Scopa: { $mechanic }
scopa-select-mechanic = Chọn cơ chế Scopa
scopa-toggle-instant-win = Thắng ngay khi được Scopa: { $enabled }
scopa-toggle-team-scoring = Gộp bài của đội để tính điểm: { $enabled }
scopa-toggle-inverse = Chế độ Đảo ngược (đạt điểm mục tiêu = bị loại): { $enabled }

# Option change announcements
scopa-option-changed-cards = Số bài mỗi lần chia đã đặt là { $cards }.
scopa-option-changed-decks = Số bộ bài đã đặt là { $decks }.
scopa-option-changed-escoba = Escoba { $enabled }.
scopa-option-changed-hints = Gợi ý nước ăn bài { $enabled }.
scopa-option-changed-mechanic = Cơ chế Scopa đã đặt là { $mechanic }.
scopa-option-changed-instant = Thắng ngay khi được Scopa { $enabled }.
scopa-option-changed-team-scoring = Tính điểm bài theo đội { $enabled }.
scopa-option-changed-inverse = Chế độ Đảo ngược { $enabled }.

# Scopa mechanic choices
scopa-mechanic-normal = Bình thường
scopa-mechanic-no_scopas = Không tính điểm Scopa
scopa-mechanic-only_scopas = Chỉ tính điểm Scopa

# Disabled action reasons
scopa-timer-not-active = Đồng hồ vòng chơi không hoạt động.

# Validation errors
scopa-error-not-enough-cards = Không đủ bài trong { $decks } { $decks ->
    [one] bộ
   *[other] bộ
} cho { $players } { $players ->
    [one] người chơi
   *[other] người chơi
} với { $cards_per_deal } lá mỗi người. (Cần { $cards_per_deal } × { $players } = { $cards_needed } lá, nhưng chỉ có { $total_cards }.)

# Formatting
scopa-line-format = { $rank }. { $player }: { $points }
