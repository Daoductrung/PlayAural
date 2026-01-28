# Thông báo trò chơi Thương Vụ Đổi Chác (Tradeoff)

# Thông tin trò chơi
game-name-tradeoff = Thương Vụ Đổi Chác (Tradeoff)

# Luồng vòng chơi và ván đấu
tradeoff-round-start = Vòng { $round }.
tradeoff-iteration = Ván { $iteration } / 3.

# Giai đoạn 1: Đổi chác
tradeoff-you-rolled = Bạn gieo được: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = đổi
tradeoff-trade-status-keeping = giữ
tradeoff-confirm-trades = Xác nhận đổi ({ $count } xúc xắc)
tradeoff-keeping = Giữ { $value }.
tradeoff-trading = Đổi { $value }.
tradeoff-player-traded = { $player } đã đổi: { $dice }.
tradeoff-player-traded-none = { $player } giữ lại tất cả xúc xắc.

# Giai đoạn 2: Lấy từ kho chung
tradeoff-your-turn-take = Đến lượt bạn lấy một xúc xắc từ kho chung.
tradeoff-take-die = Lấy con { $value } (còn { $remaining })
tradeoff-you-take = Bạn lấy một con { $value }.
tradeoff-player-takes = { $player } lấy một con { $value }.

# Giai đoạn 3: Tính điểm
tradeoff-player-scored = { $player } ({ $points } điểm): { $sets }.
tradeoff-no-sets = { $player }: không có bộ nào.

# Mô tả các bộ (ngắn gọn)
tradeoff-set-triple = bộ ba con { $value }
tradeoff-set-group = nhóm các con { $value }
tradeoff-set-mini-straight = sảnh nhỏ { $low }-{ $high }
tradeoff-set-double-triple = hai bộ ba (con { $v1 } và { $v2 })
tradeoff-set-straight = sảnh { $low }-{ $high }
tradeoff-set-double-group = hai nhóm (con { $v1 } và { $v2 })
tradeoff-set-all-groups = tất cả theo nhóm
tradeoff-set-all-triplets = tất cả là bộ ba

# Kết thúc vòng
tradeoff-round-scores = Điểm số Vòng { $round }:
tradeoff-score-line = { $player }: +{ $round_points } (tổng: { $total })
tradeoff-leader = { $player } dẫn đầu với { $score }.

# Kết thúc trò chơi
tradeoff-winner = { $player } thắng với { $score } điểm!
tradeoff-winners-tie = Hòa nhau! { $players } cùng đạt { $score } điểm!

# Kiểm tra trạng thái
tradeoff-view-hand = Xem xúc xắc trên tay
tradeoff-view-pool = Xem kho chung
tradeoff-view-players = Xem người chơi
tradeoff-hand-display = Tay bạn ({ $count } xúc xắc): { $dice }
tradeoff-pool-display = Kho chung ({ $count } xúc xắc): { $dice }
tradeoff-player-info = { $player }: { $hand }. Đã đổi: { $traded }.
tradeoff-player-info-no-trade = { $player }: { $hand }. Không đổi gì.

# Thông báo lỗi
tradeoff-not-trading-phase = Không phải giai đoạn đổi chác.
tradeoff-not-taking-phase = Không phải giai đoạn lấy xúc xắc.
tradeoff-already-confirmed = Đã xác nhận rồi.
tradeoff-no-die = Không có xúc xắc nào để chọn.
tradeoff-no-more-takes = Không còn lượt lấy nào.
tradeoff-not-in-pool = Xúc xắc đó không có trong kho.

# Tùy chọn
tradeoff-set-target = Điểm mục tiêu: { $score }
tradeoff-enter-target = Nhập điểm mục tiêu:
tradeoff-option-changed-target = Điểm mục tiêu được đặt là { $score }.
