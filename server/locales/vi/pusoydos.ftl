game-name-pusoydos = Pusoy Dos

# =============================================================================
# =============================================================================


# =============================================================================
# Option labels and prompts
# =============================================================================

pusoydos-set-game-mode = Chế độ chơi: { $choice }
pusoydos-select-game-mode = Chọn chế độ chơi:
pusoydos-option-changed-game-mode = Đã đặt chế độ chơi thành { $choice }.
pusoydos-desc-game-mode = Loại bỏ: thắng đủ số vòng để về đích, người cuối cùng còn lại là người thua. Số lần thua: ai về chót sẽ bị tính một lần thua, người đầu tiên chạm giới hạn sẽ thua. Điểm: người thắng vòng thu điểm phạt từ những người thua, ai đạt mục tiêu trước sẽ thắng. Loại bỏ theo điểm: người thua tự cộng điểm phạt của mình, chạm giới hạn là bị loại, người trụ lại cuối cùng sẽ thắng.

pusoydos-mode-elimination = Loại bỏ
pusoydos-mode-losses = Số lần thua
pusoydos-mode-points = Điểm
pusoydos-mode-points-elimination = Loại bỏ theo điểm

pusoydos-set-rounds-to-win = Số vòng để thắng: { $count }
pusoydos-enter-rounds-to-win = Nhập số vòng cần thắng để được loại ra (tối thiểu: 1, tối đa: 10):
pusoydos-option-changed-rounds-to-win = Đã đặt số vòng để thắng thành { $count }.
pusoydos-desc-rounds-to-win = Chỉ dùng trong chế độ Loại bỏ: số vòng một người chơi phải thắng trước khi rời ván với tư cách người thắng (mặc định 2, phạm vi 1-10).

pusoydos-set-losses-to-lose = Số lần thua để bị loại: { $count }
pusoydos-enter-losses-to-lose = Nhập số lần thua cần để thua ván (tối thiểu: 1, tối đa: 10):
pusoydos-option-changed-losses-to-lose = Đã đặt số lần thua để bị loại thành { $count }.
pusoydos-desc-losses-to-lose = Chỉ dùng trong chế độ Số lần thua: số lần về chót trước khi một người chơi thua cả ván (mặc định 3, phạm vi 1-10).

pusoydos-set-target-score = Điểm mục tiêu: { $score }
pusoydos-enter-target-score = Nhập điểm mục tiêu (tối thiểu: 10, tối đa: 10000):
pusoydos-option-changed-target-score = Đã đặt điểm mục tiêu thành { $score }.
pusoydos-desc-target-score = Chỉ dùng trong các chế độ điểm: mốc điểm để thắng trong chế độ Điểm, hoặc để bị loại trong chế độ Loại bỏ theo điểm (mặc định 100, phạm vi 10-10000).

pusoydos-set-turn-timer = Thời gian mỗi lượt: { $choice }
pusoydos-select-turn-timer = Chọn thời gian mỗi lượt:
pusoydos-option-changed-turn-timer = Đã đặt thời gian mỗi lượt thành { $choice }.
pusoydos-desc-turn-timer = Giới hạn thời gian mỗi lượt: Không giới hạn, 10, 15, 20, 30, 45, 60 hoặc 90 giây (mặc định Không giới hạn).

pusoydos-timer-10 = 10 giây
pusoydos-timer-15 = 15 giây
pusoydos-timer-20 = 20 giây
pusoydos-timer-30 = 30 giây
pusoydos-timer-45 = 45 giây
pusoydos-timer-60 = 60 giây
pusoydos-timer-90 = 90 giây
pusoydos-timer-unlimited = Không giới hạn

pusoydos-set-allow-2-in-straights = Cho phép lá 2 trong sảnh: { $enabled }
pusoydos-option-changed-allow-2-in-straights = Đã đặt cho phép lá 2 trong sảnh thành { $enabled }.
pusoydos-desc-allow-2-in-straights = Có cho phép dùng lá 2 trong sảnh hay không (ví dụ A-2-3-4-5).

pusoydos-set-instant-wins = Thắng ngay lập tức: { $enabled }
pusoydos-option-changed-instant-wins = Đã đặt thắng ngay lập tức thành { $enabled }.
pusoydos-desc-instant-wins = Có cho phép các bộ bài chia đặc biệt (Rồng, Bốn lá 2, Sáu đôi) thắng vòng ngay lập tức hay không. Không thể bật cùng lúc với trao đổi bài.

pusoydos-set-card-passing = Trao đổi bài: { $choice }
pusoydos-select-card-passing = Chọn chế độ trao đổi bài:
pusoydos-option-changed-card-passing = Đã đặt trao đổi bài thành { $choice }.
pusoydos-desc-card-passing = Trao đổi bài giữa người thắng và người thua sau khi chia bài: Tắt, Đơn giản hoặc Đầy đủ. Trao đổi đầy đủ chỉ hợp lệ khi có đúng 2 hoặc 4 người, và không thể dùng cùng thắng ngay lập tức.

pusoydos-passing-off = Tắt
pusoydos-passing-simple = Đơn giản (người nhất và người chót đổi 1 lá)
pusoydos-passing-full = Đầy đủ (người nhất/chót đổi 2 lá, người nhì/ba đổi 1 lá)

pusoydos-set-penalty-tier = Mức phạt: { $choice }
pusoydos-select-penalty-tier = Chọn mức phạt:
pusoydos-option-changed-penalty-tier = Đã đặt mức phạt thành { $choice }.
pusoydos-desc-penalty-tier = Chỉ dùng trong các chế độ điểm: mức độ phạt nặng đối với số bài còn lại trên tay khi kết thúc vòng.

pusoydos-penalty-standard = Tiêu chuẩn (từ 10 lá: x2, đủ 13 lá: x3)
pusoydos-penalty-aggressive = Nặng (8-9 lá: x2, 10-12 lá: x3, 13 lá: x4)
pusoydos-penalty-flat = Cố định (1 điểm mỗi lá, không nhân hệ số)

pusoydos-set-penalty-per-two = Phạt thêm cho mỗi lá 2 giữ lại: { $enabled }
pusoydos-option-changed-penalty-per-two = Đã đặt phạt thêm cho mỗi lá 2 giữ lại thành { $enabled }.
pusoydos-desc-penalty-per-two = Chỉ dùng trong các chế độ điểm: mỗi lá 2 còn lại trên tay người thua sẽ nhân đôi mức phạt của tay đó.

# =============================================================================
# Game flow announcements
# =============================================================================


pusoydos-new-hand = Vòng { $round }.
pusoydos-dealt = Đã chia { $count } lá bài: { $cards }.

pusoydos-you-first-player = Bạn có lá 3 Tép và đi trước.
pusoydos-first-player = { $player } có lá 3 Tép và đi trước.
pusoydos-you-first-player-lowest = Bạn có lá bài nhỏ nhất và đi trước.
pusoydos-first-player-lowest = { $player } có lá bài nhỏ nhất và đi trước.

# Elimination mode
pusoydos-you-eliminated = Bạn đã thắng { $count } vòng và về đích! Chơi hay lắm.
pusoydos-player-eliminated = { $player } đã thắng { $count } vòng và về đích! Chơi hay lắm.
pusoydos-you-last-player = Bạn là người chơi cuối cùng còn lại. Ván kết thúc!
pusoydos-last-player = { $player } là người chơi cuối cùng còn lại. Ván kết thúc!
pusoydos-players-remaining = Còn lại { $count } { $count ->
    [one] người chơi
   *[other] người chơi
}.

# Losses mode
pusoydos-you-round-loser = Bạn về chót và bị tính một lần thua! (Tổng cộng { $count } { $count ->
    [one] lần thua
   *[other] lần thua
}.)
pusoydos-round-loser = { $player } về chót và bị tính một lần thua! (Tổng cộng { $count } { $count ->
    [one] lần thua
   *[other] lần thua
}.)
pusoydos-you-losses-game-over = Bạn đã chạm { $count } lần thua và thua cả ván!
pusoydos-losses-game-over = { $player } đã chạm { $count } lần thua và thua cả ván!

# Points mode
pusoydos-penalty-entry = { $points } điểm từ { $player }
pusoydos-you-penalty-summary = Bạn thắng vòng này: { $breakdown }. (Được { $gained } điểm vòng này, tổng cộng { $total }.)
pusoydos-penalty-summary = { $player } thắng vòng này: { $breakdown }. (Được { $gained } điểm vòng này, tổng cộng { $total }.)
pusoydos-you-win-round = Bạn thắng vòng này!
pusoydos-round-winner = { $player } thắng vòng này!
pusoydos-you-go-out = Bạn đã về đích!
pusoydos-player-goes-out = { $player } đã về đích!
pusoydos-you-points-winner = Bạn đạt { $score } điểm và thắng cả ván!
pusoydos-points-winner = { $player } đạt { $score } điểm và thắng cả ván!

# Points elimination mode
pusoydos-you-points-elim-penalty = Bạn bị { $points } điểm. (Tổng cộng { $total }.)
pusoydos-points-elim-penalty = { $player } bị { $points } điểm. (Tổng cộng { $total }.)
pusoydos-you-points-elim-eliminated = Bạn đạt { $score } điểm và bị loại!
pusoydos-points-elim-eliminated = { $player } đạt { $score } điểm và bị loại!
pusoydos-you-points-elim-winner = Bạn là người trụ lại cuối cùng. Bạn thắng!
pusoydos-points-elim-winner = { $player } là người trụ lại cuối cùng. { $player } thắng!

# Instant wins
pusoydos-you-instant-win-dragon = Bạn có một bộ Rồng (sảnh 13 lá)! Thắng ngay lập tức!
pusoydos-instant-win-dragon = { $player } có một bộ Rồng (sảnh 13 lá)! Thắng ngay lập tức!
pusoydos-you-instant-win-four-twos = Bạn có cả bốn lá 2! Thắng ngay lập tức!
pusoydos-instant-win-four-twos = { $player } có cả bốn lá 2! Thắng ngay lập tức!
pusoydos-you-instant-win-six-pairs = Bạn có sáu đôi! Thắng ngay lập tức!
pusoydos-instant-win-six-pairs = { $player } có sáu đôi! Thắng ngay lập tức!
pusoydos-checking-instant-wins = Đang kiểm tra các bộ bài thắng ngay lập tức...
pusoydos-no-instant-wins = Không có bộ thắng ngay lập tức nào trong vòng này.

# Card passing
pusoydos-passing-phase = Giai đoạn trao đổi bài.
pusoydos-loser-gives = { $loser } đưa { $count ->
    [one] lá bài lớn nhất { GENDER_TERM($loser_gender, "possessive-determiner") }
   *[other] { $count } lá bài lớn nhất { GENDER_TERM($loser_gender, "possessive-determiner") }
} cho { $winner }.
pusoydos-winner-gives-back = { $winner } trả lại { $count ->
    [one] một lá bài
   *[other] { $count } lá bài
} cho { $loser }.
pusoydos-select-cards-to-give = Chọn { $count ->
    [one] 1 lá bài
   *[other] { $count } lá bài
} để trả lại cho { $recipient }:
pusoydos-cards-exchanged = Đã trao đổi bài xong.
pusoydos-passed-cards = Bạn đã đưa { $cards } cho { $recipient }.
pusoydos-received-cards = Bạn nhận được { $cards } từ { $sender }.

# =============================================================================
# Card interaction and actions
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (đã chọn)

pusoydos-play-none = Chọn bài để đánh.
pusoydos-play-invalid = Tổ hợp bài không hợp lệ.
pusoydos-play-combo = Đánh { $combo }

pusoydos-pass = Bỏ lượt
pusoydos-check-trick = Xem bài trên bàn
pusoydos-read-hand = Đọc bài trên tay
pusoydos-check-turn-timer = Xem thời gian lượt
pusoydos-read-card-counts = Số lá còn lại
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] lá
   *[other] lá
}
pusoydos-card-counts-empty = Không có người chơi đang hoạt động nào còn bài để đếm.
pusoydos-timer-disabled = Đồng hồ lượt đang tắt.
pusoydos-timer-remaining = Còn lại { $seconds } giây.

# Keybind labels
pusoydos-key-play = Đánh các lá đã chọn
pusoydos-key-pass = Bỏ lượt
pusoydos-key-trick = Xem lượt bài hiện tại
pusoydos-key-hand = Đọc bài trên tay
pusoydos-key-counts = Số lá còn lại
pusoydos-key-timer = Thời gian lượt

# =============================================================================
# Errors
# =============================================================================

pusoydos-error-full-passing-players = Trao đổi bài đầy đủ cần đúng 2 hoặc 4 người chơi.
pusoydos-error-instant-wins-card-passing = Thắng ngay lập tức và trao đổi bài mâu thuẫn với nhau. Hãy tắt một trong hai tùy chọn trước khi bắt đầu ván.
pusoydos-error-no-cards = Bạn chưa chọn lá bài nào.
pusoydos-error-invalid-combo = Các lá đã chọn không tạo thành một tổ hợp hợp lệ.
pusoydos-error-first-turn-3c = Bạn phải đánh kèm lá 3 Tép trong lượt đầu tiên.
pusoydos-error-wrong-length = Bạn phải đánh đúng { $count } { $count ->
    [one] lá bài
   *[other] lá bài
} để chặn lượt bài hiện tại.
pusoydos-error-lower-combo = Tổ hợp của bạn nhỏ hơn lượt bài hiện tại.
pusoydos-error-must-play = Bạn không thể bỏ lượt khi đang khai một lượt bài mới.
pusoydos-error-select-cards-to-give = Hãy chọn đúng { $count } { $count ->
    [one] lá
   *[other] lá
} để trả lại cho { $recipient }.
pusoydos-error-select-required-give-cards = Hãy chọn đủ số lá cần trao đổi trước khi xác nhận.
pusoydos-error-eliminated = Bạn không còn trong phần chơi đang diễn ra của ván này.
pusoydos-confirm-pass = Dùng lại hành động bỏ lượt để xác nhận.

# =============================================================================
# Broadcasts
# =============================================================================

pusoydos-you-play-single = Bạn đánh { $card }.
pusoydos-player-plays-single = { $player } đánh { $card }.
pusoydos-you-play-combo = Bạn đánh tổ hợp { $combo } gồm { $cards }.
pusoydos-player-plays-combo = { $player } đánh tổ hợp { $combo } gồm { $cards }.
pusoydos-you-pass = Bạn bỏ lượt.
pusoydos-player-passes = { $player } bỏ lượt.
pusoydos-you-win-trick = Bạn giành được lượt bài.
pusoydos-trick-won = { $player } giành được lượt bài.

pusoydos-trick-empty = Bàn đang trống.
pusoydos-trick-status = { $player } đã đánh tổ hợp { $combo } gồm { $cards }.
pusoydos-your-hand = Bài của bạn: { $cards }.

pusoydos-score-no-scores = Chưa có điểm.
pusoydos-score-wins = { $player }: { $count } vòng thắng
pusoydos-score-losses = { $player }: { $count } lần thua
pusoydos-score-points = { $player }: { $score } điểm

pusoydos-you-one-card = Bạn chỉ còn một lá bài!
pusoydos-one-card = { $player } chỉ còn một lá bài!

# =============================================================================
# Combo names
# =============================================================================

pusoydos-combo-single = lá lẻ
pusoydos-combo-pair = đôi
pusoydos-combo-three_of_a_kind = sám cô
pusoydos-combo-straight = sảnh
pusoydos-combo-flush = thùng
pusoydos-combo-full_house = cù lũ
pusoydos-combo-four_of_a_kind = tứ quý
pusoydos-combo-straight_flush = thùng phá sảnh

# Instant win hand names
pusoydos-combo-dragon = Rồng
pusoydos-combo-four_twos = Bốn lá 2
pusoydos-combo-six_pairs = Sáu đôi

# =============================================================================
# End screen
# =============================================================================

pusoydos-game-over = Ván đấu kết thúc! { $player } đã thua!
pusoydos-game-over-points = Ván đấu kết thúc! { $player } thắng với { $score } điểm!
pusoydos-game-over-losses = Ván đấu kết thúc! { $player } thua với { $count } lần thua!
pusoydos-line-format = { $rank }. { $player }: { $score } điểm
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] lần thua
   *[other] lần thua
}
