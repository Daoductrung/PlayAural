# Thông báo trò chơi Tradeoff

# Thông tin game
game-name-tradeoff = Tradeoff

# Luồng vòng chơi và lượt
tradeoff-round-start = Vòng { $round }.
tradeoff-iteration = Ván { $iteration } trên 3.

# Giai đoạn 1: Trao đổi
tradeoff-you-rolled = Bạn gieo được: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = đổi
tradeoff-trade-status-keeping = giữ
tradeoff-confirm-trades = Xác nhận đổi ({ $count } viên)
tradeoff-keeping = Đang giữ con { $value }.
tradeoff-trading = Đang đổi con { $value }.
tradeoff-player-traded = { $player } đã đổi: { $dice }.
tradeoff-player-traded-none = { $player } giữ lại toàn bộ xúc xắc.

# Giai đoạn 2: Lấy từ kho
tradeoff-your-turn-take = Đến lượt bạn lấy một viên từ kho.
tradeoff-take-die = Lấy con { $value } (còn { $remaining } viên)
tradeoff-you-take = Bạn lấy một con { $value }.
tradeoff-player-takes = { $player } lấy một con { $value }.

# Giai đoạn 3: Tính điểm
tradeoff-player-scored = { $player } ({ $points } điểm): { $sets }.
tradeoff-no-sets = { $player }: không có bộ nào.

# Mô tả các bộ (ngắn gọn)
tradeoff-set-triple = bộ ba { $value }
tradeoff-set-group = nhóm { $value }
tradeoff-set-mini-straight = sảnh nhỏ { $low }-{ $high }
tradeoff-set-double-triple = hai bộ ba ({ $v1 } và { $v2 })
tradeoff-set-straight = sảnh { $low }-{ $high }
tradeoff-set-double-group = hai nhóm ({ $v1 } và { $v2 })
tradeoff-set-all-groups = toàn bộ là nhóm
tradeoff-set-all-triplets = toàn bộ là bộ ba

# Kết thúc vòng
tradeoff-round-scores = Điểm vòng { $round }:
tradeoff-score-line = { $player }: +{ $round_points } (tổng: { $total })
tradeoff-leader = { $player } dẫn đầu với { $score } điểm.

# Kết thúc game
tradeoff-winner = { $player } thắng với { $score } điểm!
tradeoff-winners-tie = Hòa nhau! { $players } hòa với { $score } điểm!

# Kiểm tra trạng thái
tradeoff-view-hand = Xem xúc xắc trên tay
tradeoff-view-pool = Xem kho
tradeoff-view-players = Xem người chơi
tradeoff-hand-display = Trên tay bạn ({ $count } viên): { $dice }
tradeoff-pool-display = Kho ({ $count } viên): { $dice }
tradeoff-player-info = { $player }: { $hand }. Đã đổi: { $traded }.
tradeoff-player-info-no-trade = { $player }: { $hand }. Không đổi gì.

# Thông báo lỗi
tradeoff-not-trading-phase = Không phải giai đoạn trao đổi.
tradeoff-not-taking-phase = Không phải giai đoạn lấy từ kho.
tradeoff-already-confirmed = Đã xác nhận rồi.
tradeoff-no-die = Không có xúc xắc để chọn.
tradeoff-no-more-takes = Không còn lượt lấy.
tradeoff-not-in-pool = Viên này không có trong kho.

# Tùy chọn
tradeoff-set-target = Điểm mục tiêu: { $score }
tradeoff-enter-target = Nhập điểm mục tiêu:
tradeoff-option-changed-target = Điểm mục tiêu đã đặt là { $score }.
