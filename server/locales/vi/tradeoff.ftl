# Tradeoff game messages

# Game info
game-name-tradeoff = Tradeoff

# Round and iteration flow
tradeoff-round-start = Vòng { $round }.
tradeoff-iteration = Lượt gieo { $iteration } trên 3.

# Phase 1: Trading
tradeoff-you-rolled = Bạn gieo được: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = đang đổi
tradeoff-trade-status-keeping = đang giữ
tradeoff-confirm-trades = Xác nhận đổi ({ $count } viên)
tradeoff-keeping = Đang giữ { $value }.
tradeoff-trading = Đang đổi { $value }.
tradeoff-player-traded = { $player } đã đổi: { $dice }.
tradeoff-player-traded-none = { $player } giữ lại tất cả xúc xắc.

# Phase 2: Taking from pool
tradeoff-your-turn-take = Đến lượt bạn lấy một viên xúc xắc từ hũ chung.
tradeoff-take-die = Lấy viên { $value } (còn lại { $remaining })
tradeoff-you-take = Bạn lấy một viên { $value }.
tradeoff-player-takes = { $player } lấy một viên { $value }.

# Phase 3: Scoring
tradeoff-player-scored = { $player } ({ $points } điểm): { $sets }.
tradeoff-no-sets = { $player }: không có bộ nào.

# Set descriptions (concise)
tradeoff-set-triple = bộ ba con { $value }
tradeoff-set-group = nhóm con { $value }
tradeoff-set-mini-straight = sảnh mini { $low }-{ $high }
tradeoff-set-double-triple = bộ ba đôi ({ $v1 } và { $v2 })
tradeoff-set-straight = sảnh { $low }-{ $high }
tradeoff-set-double-group = nhóm đôi ({ $v1 } và { $v2 })
tradeoff-set-all-groups = tất cả nhóm
tradeoff-set-all-triplets = tất cả bộ ba

# Round end
tradeoff-round-scores = Điểm vòng { $round }:
tradeoff-score-line = { $player }: +{ $round_points } (tổng: { $total })
tradeoff-leader = { $player } đang dẫn đầu với { $score } điểm.

# Game end
tradeoff-winner = { $player } thắng với { $score } điểm!
tradeoff-winners-tie = Hòa nhau! { $players } cùng đạt { $score } điểm!

# Status checks
tradeoff-view-hand = Xem xúc xắc trên tay
tradeoff-view-pool = Xem hũ chung
tradeoff-view-players = Xem người chơi
tradeoff-hand-display = Tay của bạn ({ $count } viên): { $dice }
tradeoff-pool-display = Hũ chung ({ $count } viên): { $dice }
tradeoff-player-info = { $player }: { $hand }. Đã đổi: { $traded }.
tradeoff-player-info-no-trade = { $player }: { $hand }. Không đổi viên nào.

# Error messages
tradeoff-not-trading-phase = Không phải giai đoạn đổi xúc xắc.
tradeoff-not-taking-phase = Không phải giai đoạn lấy xúc xắc.
tradeoff-already-confirmed = Đã xác nhận rồi.
tradeoff-no-die = Không có viên nào để chọn.
tradeoff-no-more-takes = Không còn lượt lấy nào.
tradeoff-not-in-pool = Viên xúc xắc đó không có trong hũ chung.

# Options
tradeoff-set-target = Điểm mục tiêu: { $score }
tradeoff-enter-target = Nhập điểm mục tiêu:
tradeoff-option-changed-target = Điểm mục tiêu đã đặt là { $score }.
