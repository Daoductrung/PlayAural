game-name-yahtzee = Yahtzee

yahtzee-roll = Gieo lại (còn { $count } lần)
yahtzee-roll-all = Gieo xúc xắc

yahtzee-score-ones = Số 1 được { $points } điểm
yahtzee-score-twos = Số 2 được { $points } điểm
yahtzee-score-threes = Số 3 được { $points } điểm
yahtzee-score-fours = Số 4 được { $points } điểm
yahtzee-score-fives = Số 5 được { $points } điểm
yahtzee-score-sixes = Số 6 được { $points } điểm

yahtzee-score-three-kind = Bộ ba đồng nhất được { $points } điểm
yahtzee-score-four-kind = Bộ bốn đồng nhất được { $points } điểm
yahtzee-score-full-house = Cù lũ được { $points } điểm
yahtzee-score-small-straight = Sảnh nhỏ được { $points } điểm
yahtzee-score-large-straight = Sảnh lớn được { $points } điểm
yahtzee-score-yahtzee = Yahtzee được { $points } điểm
yahtzee-score-chance = Cơ hội được { $points } điểm

yahtzee-you-rolled = Bạn gieo được: { $dice }. { $remaining ->
    [0] Chọn một mục ghi điểm.
   *[other] Còn { $remaining } lần gieo.
}
yahtzee-player-rolled = { $player } gieo được: { $dice }. { $remaining ->
    [0] { GENDER_TERM($player_gender, "subject-capitalized") } phải chọn một mục ghi điểm.
   *[other] Còn { $remaining } lần gieo.
}
yahtzee-you-rolled-brief = Bạn gieo: { $dice }.
yahtzee-player-rolled-brief = { $player } gieo: { $dice }.

yahtzee-you-scored = Bạn ghi được { $points } điểm vào mục { $category }.
yahtzee-player-scored = { $player } ghi được { $points } điểm vào mục { $category }.
yahtzee-you-scored-brief = { $points } điểm vào { $category }.
yahtzee-player-scored-brief = { $player }: { $points } điểm vào { $category }.

yahtzee-you-bonus = Thưởng Yahtzee! +100 điểm
yahtzee-player-bonus = { $player } nhận thưởng Yahtzee! +100 điểm
yahtzee-you-bonus-brief = Thưởng Yahtzee, +100.
yahtzee-player-bonus-brief = { $player }: thưởng Yahtzee, +100.

yahtzee-you-upper-bonus = Thưởng Phần trên! +35 điểm ({ $total } điểm ở Phần trên)
yahtzee-player-upper-bonus = { $player } nhận thưởng Phần trên! +35 điểm ({ $total } điểm ở Phần trên)
yahtzee-you-upper-bonus-brief = Thưởng Phần trên, +35.
yahtzee-player-upper-bonus-brief = { $player }: thưởng Phần trên, +35.
yahtzee-you-upper-bonus-missed = Không đạt thưởng Phần trên. Bạn có { $total } điểm; còn thiếu { $needed } điểm.
yahtzee-player-upper-bonus-missed = { $player } không đạt thưởng Phần trên với { $total } điểm, còn thiếu { $needed } điểm.
yahtzee-you-upper-bonus-missed-brief = Trượt thưởng Phần trên; thiếu { $needed } điểm.
yahtzee-player-upper-bonus-missed-brief = { $player }: trượt thưởng Phần trên, thiếu { $needed } điểm.

yahtzee-check-scoresheet = Xem bảng điểm
yahtzee-check-all-scorecards = Xem bảng điểm của mọi người chơi
yahtzee-select-scorecard-player = Chọn bảng điểm của người chơi.
yahtzee-scorecard-no-players = Chưa có người chơi đang hoạt động nào có bảng điểm trong ván này.
yahtzee-scorecard-player-unavailable = Người chơi đó không còn khả dụng để xem. Hãy mở lại danh sách bảng điểm và chọn một người chơi đang hoạt động.
yahtzee-view-dice = Kiểm tra xúc xắc trên tay
yahtzee-your-dice = Xúc xắc của bạn: { $dice }.
yahtzee-your-dice-kept = Xúc xắc của bạn: { $dice }. Đang giữ: { $kept }.
yahtzee-current-dice = Xúc xắc của { $player }: { $dice }.
yahtzee-current-dice-kept = Xúc xắc của { $player }: { $dice }. Đang giữ: { $kept }.
yahtzee-not-rolled = Người chơi hiện tại chưa gieo xúc xắc.

yahtzee-scoresheet-header = Bảng điểm của { $player }
yahtzee-scoresheet-upper = Phần trên:
yahtzee-scoresheet-lower = Phần dưới:
yahtzee-scoresheet-upper-total-bonus = Tổng Phần trên: { $total } (đã nhận thưởng +35)
yahtzee-scoresheet-upper-total-needed = Tổng Phần trên: { $total } (cần thêm { $needed } điểm để nhận thưởng)
yahtzee-scoresheet-yahtzee-bonus = Thưởng Yahtzee: { $count } x 100 = { $total } điểm
yahtzee-scoresheet-grand-total = Tổng điểm: { $total }

yahtzee-category-ones = Số 1
yahtzee-category-twos = Số 2
yahtzee-category-threes = Số 3
yahtzee-category-fours = Số 4
yahtzee-category-fives = Số 5
yahtzee-category-sixes = Số 6
yahtzee-category-three-kind = Bộ ba đồng nhất
yahtzee-category-four-kind = Bộ bốn đồng nhất
yahtzee-category-full-house = Cù lũ
yahtzee-category-small-straight = Sảnh nhỏ
yahtzee-category-large-straight = Sảnh lớn
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Cơ hội

yahtzee-you-win = Bạn thắng với { $score } điểm!
yahtzee-player-wins = { $player } thắng với { $score } điểm!
yahtzee-winners-tie = Hòa nhau! { $players } đều ghi được { $score } điểm!

yahtzee-set-rounds = Số ván chơi: { $rounds }
yahtzee-enter-rounds = Nhập số ván chơi (1-10):
yahtzee-option-changed-rounds = Số ván chơi đã được đặt là { $rounds }.
yahtzee-desc-num-games = Số bảng điểm Yahtzee hoàn chỉnh sẽ chơi trước khi so tổng cuối cùng (mặc định 1, phạm vi 1-10).

yahtzee-no-rolls-left = Bạn không còn lần gieo nào; hãy chọn một mục ghi điểm còn trống để kết thúc lượt.
yahtzee-roll-first = Hãy gieo xúc xắc trước khi chọn mục ghi điểm.
yahtzee-category-filled = Mục đó đã có điểm. Hãy chọn một mục còn trống trên bảng điểm của bạn.
yahtzee-joker-upper-required = Quy tắc Joker: vì Yahtzee này ra mặt { $face }, bạn phải ghi vào ô Phần trên cho số { $face } trước mọi mục khác.
yahtzee-joker-lower-required = Quy tắc Joker: ô Phần trên cho số { $face } đã được ghi rồi, nên bạn phải chọn một mục còn trống ở Phần dưới trước khi dùng ô Phần trên khác.
