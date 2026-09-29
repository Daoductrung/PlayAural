game-name-tradeoff = Tradeoff

tradeoff-round-start = Vòng { $round }.
tradeoff-iteration = Lượt gieo { $iteration } trên 3.

tradeoff-you-rolled = Bạn gieo được: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = đang đổi
tradeoff-trade-status-keeping = đang giữ
tradeoff-confirm-trades = Xác nhận đổi ({ $count } viên)
tradeoff-keeping = Đang giữ { $value }.
tradeoff-trading = Đang đổi { $value }.
tradeoff-you-traded = Bạn bỏ { $count } viên vào hũ chung để đổi: { $dice }.
tradeoff-player-traded = { $player } bỏ { $count } viên vào hũ chung để đổi: { $dice }.
tradeoff-you-traded-brief = Bạn đổi { $count } viên.
tradeoff-player-traded-brief = { $player } đổi { $count } viên.
tradeoff-you-traded-none = Bạn giữ cả năm viên của lượt gieo này, nên lần này bạn sẽ không lấy từ hũ chung.
tradeoff-player-traded-none = { $player } giữ cả năm viên của lượt gieo này.

tradeoff-your-turn-take = Đến lượt bạn lấy một viên xúc xắc từ hũ chung.
tradeoff-take-die = Lấy viên { $value } (còn { $remaining })
tradeoff-you-take = Bạn lấy một viên { $value }.
tradeoff-player-takes = { $player } lấy một viên { $value }.

tradeoff-you-scored = Bạn ghi { $points } điểm với { $sets }.
tradeoff-player-scored = { $player } ghi { $points } điểm với { $sets }.
tradeoff-you-scored-brief = Bạn ghi { $points } điểm trong vòng này.
tradeoff-player-scored-brief = { $player } ghi { $points } điểm trong vòng này.
tradeoff-you-no-sets = Bạn ghi 0 điểm vì 15 viên xúc xắc không tạo được bộ ghi điểm nào.
tradeoff-no-sets = { $player } ghi 0 điểm vì 15 viên xúc xắc { GENDER_TERM($player_gender, "possessive-determiner") } không tạo được bộ ghi điểm nào.

tradeoff-set-triple = bộ ba con { $value }
tradeoff-set-group = nhóm năm con { $value }
tradeoff-set-mini-straight = sảnh ngắn { $low }-{ $high }
tradeoff-set-double-triple = hai bộ ba ({ $v1 } và { $v2 })
tradeoff-set-straight = sảnh { $low }-{ $high }
tradeoff-set-double-group = hai nhóm năm ({ $v1 } và { $v2 })
tradeoff-set-all-groups = ba nhóm năm
tradeoff-set-all-triplets = năm bộ ba

tradeoff-round-scores = Điểm vòng { $round }:
tradeoff-round-scores-brief = Điểm:
tradeoff-score-line = { $player }: +{ $round_points } (tổng: { $total })
tradeoff-score-line-brief = { $player }: +{ $round_points }, tổng { $total }.
tradeoff-leader = { $player } đang dẫn đầu với { $score } điểm.
tradeoff-leader-brief = Dẫn đầu: { $player }, { $score } điểm.

tradeoff-you-win = Bạn thắng với { $score } điểm!
tradeoff-winner = { $player } thắng với { $score } điểm!
tradeoff-you-tie-win = Bạn đồng thắng với { $players } ở mức { $score } điểm!
tradeoff-winners-tie = Hòa nhau! { $players } cùng đạt { $score } điểm!

tradeoff-view-hand = Xem tay giữ của bạn
tradeoff-view-pool = Xem hũ chung
tradeoff-view-players = Xem người chơi
tradeoff-hand-state-empty = chưa giữ viên nào
tradeoff-hand-empty = Tay giữ của bạn đang trống. Nếu bạn vừa gieo, hãy dùng các lựa chọn xúc xắc để quyết định giữ hay đổi trước khi xác nhận.
tradeoff-hand-display = Tay giữ của bạn trong vòng này ({ $count } viên): { $dice }.
tradeoff-hand-display-with-roll = Tay giữ của bạn trong vòng này ({ $count } viên): { $dice }. Lượt gieo hiện tại: { $roll }. Còn { $trade_count } viên đang được đánh dấu để đổi.
tradeoff-roll-die-status = vị trí { $position }: { $value }, { $status }
tradeoff-die-count = { $value }: { $count }
tradeoff-pool-display = Hũ chung ({ $count } viên): { $dice }.
tradeoff-pool-empty = Hũ chung hiện đang trống.
tradeoff-player-info = { $player }: tay giữ: { $hand }. Lần vừa rồi đã đổi: { $traded }.
tradeoff-player-info-no-trade = { $player }: tay giữ: { $hand }. Lần vừa rồi không đổi viên nào.

tradeoff-not-trading-phase = Bạn chỉ có thể đổi hoặc xác nhận xúc xắc khi các viên vừa gieo đang chờ chọn trong giai đoạn đổi.
tradeoff-not-taking-phase = Bạn chỉ có thể lấy xúc xắc sau khi mọi người đã xác nhận đổi và hũ chung đã mở.
tradeoff-already-confirmed = Bạn đã xác nhận lựa chọn đổi này rồi. Hãy chờ những người chơi còn lại; nếu bạn đã đổi xúc xắc, bạn sẽ lấy từ hũ chung khi đến lượt.
tradeoff-no-die = Không có viên xúc xắc nào cho hành động đổi đó.
tradeoff-no-die-position = Vị trí { $position } không có trong lượt gieo hiện tại của bạn.
tradeoff-no-rolled-dice = Hiện bạn không có lượt gieo nào đang chờ chọn đổi.
tradeoff-no-more-takes = Bạn đã lấy lại đúng số viên mình đã đổi trong lượt gieo này.
tradeoff-not-in-pool = Hiện trong hũ chung không có viên { $value }. Hãy chọn một giá trị đang có trong hũ.
tradeoff-not-your-take-turn = Đang là lượt { $player } lấy từ hũ chung. Hãy chờ đến khi tên bạn được thông báo rồi mới chọn xúc xắc.
tradeoff-no-trading-die-value = Bạn không có viên { $value } nào đang được đánh dấu để đổi.
tradeoff-no-kept-die-value = Bạn không có viên { $value } nào đang giữ để đánh dấu đổi.
tradeoff-value-trade-style-required = Phím Shift+số để đánh dấu đổi chỉ dùng với kiểu giữ xúc xắc Theo giá trị. Hãy dùng phím số thường theo vị trí, hoặc đổi tùy chọn cá nhân về kiểu Theo giá trị.
tradeoff-use-plain-number-to-take = Hãy dùng phím số thường, không dùng Shift+số, để lấy xúc xắc từ hũ chung.
tradeoff-no-dice-key-phase = Phím số chỉ dùng khi đang chọn đổi xúc xắc hoặc đang lấy xúc xắc từ hũ chung.

tradeoff-set-target = Điểm mục tiêu: { $score }
tradeoff-enter-target = Nhập điểm mục tiêu:
tradeoff-option-changed-target = Điểm mục tiêu đã đặt là { $score }.
tradeoff-desc-target-score = Tổng điểm một người chơi cần đạt hoặc vượt qua sau một vòng tính điểm để thắng (mặc định 60, phạm vi 30-500).
tradeoff-error-target-out-of-range = Điểm mục tiêu { $score } nằm ngoài phạm vi cho phép từ { $min } đến { $max }.
