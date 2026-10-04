game-name-midnight = 1-4-24

midnight-roll = Gieo xúc xắc
midnight-bank = Chốt điểm
midnight-check-dice = Đọc xúc xắc hiện tại
midnight-check-round-status = Xem trạng thái vòng

midnight-round-start = Vòng { $round } trên { $total }.
midnight-round-start-brief = Vòng { $round }/{ $total }.

midnight-you-rolled = Bạn gieo được: { $dice }.
midnight-player-rolled = { $player } gieo được: { $dice }.
midnight-you-rolled-brief = Bạn gieo { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = Bạn giữ viên { $index }, mặt { $die }.
midnight-player-keeps = { $player } giữ viên { $index }, mặt { $die }.
midnight-you-keep-brief = Bạn giữ { $die }.
midnight-player-keeps-brief = { $player } giữ { $die }.
midnight-you-unkeep = Bạn trả viên { $index }, mặt { $die }, về nhóm gieo lại.
midnight-player-unkeeps = { $player } trả viên { $index }, mặt { $die }, về nhóm gieo lại.
midnight-you-unkeep-brief = Bạn gieo lại { $die }.
midnight-player-unkeeps-brief = { $player } gieo lại { $die }.

midnight-you-scored = Bạn đủ điều kiện với 1 và 4, ghi { $score } điểm từ { $scoring_dice }.
midnight-scored = { $player } đủ điều kiện với 1 và 4, ghi { $score } điểm từ { $scoring_dice }.
midnight-you-scored-brief = Bạn ghi { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = Bạn không đủ điều kiện vì thiếu { $missing }.
midnight-player-disqualified = { $player } không đủ điều kiện vì { GENDER_TERM($player_gender, "subject") } thiếu { $missing }.
midnight-you-disqualified-brief = Bạn thiếu { $missing }.
midnight-player-disqualified-brief = { $player } thiếu { $missing }.

midnight-you-win-round = Bạn thắng vòng { $round } với { $score } điểm.
midnight-round-winner = { $player } thắng vòng { $round } với { $score } điểm.
midnight-you-win-round-brief = Bạn thắng V{ $round }: { $score }.
midnight-round-winner-brief = { $player } thắng V{ $round }: { $score }.
midnight-round-tie = Vòng này hòa ở { $score } điểm giữa { $players }. Không ai được tính vòng thắng.
midnight-all-disqualified = Tất cả người chơi đều thiếu bộ 1 và 4 bắt buộc. Không ai được tính vòng thắng.
midnight-all-disqualified-brief = Không ai đủ điều kiện.

midnight-you-win-game = Bạn thắng chung cuộc với { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}!
midnight-game-winner = { $player } thắng chung cuộc với { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}!
midnight-you-win-game-brief = Bạn thắng: { $wins }.
midnight-game-winner-brief = { $player } thắng: { $wins }.
midnight-game-tie = Trò chơi hòa. { $players } cùng kết thúc với { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}.

midnight-set-rounds = Số vòng chơi: { $rounds }
midnight-enter-rounds = Nhập số vòng chơi:
midnight-option-changed-rounds = Số vòng chơi đã đổi thành { $rounds }
midnight-desc-rounds = Số vòng 1-4-24 sẽ chơi trước khi tính tổng cuối cùng (mặc định 5, phạm vi 1-20).
midnight-error-rounds-out-of-range = 1-4-24 hỗ trợ từ { $min } đến { $max } vòng. Thiết lập hiện tại: { $rounds }.

midnight-need-to-roll = Hãy gieo xúc xắc trước khi chọn viên để giữ.
midnight-no-dice-to-keep = Không còn viên nào để gieo hoặc giữ.
midnight-must-keep-one = Hãy giữ ít nhất một viên vừa gieo trước khi gieo tiếp.
midnight-must-roll-first = Hãy gieo xúc xắc trước khi chốt điểm lượt này.
midnight-keep-all-first = Hãy quyết định tất cả xúc xắc trước khi chốt điểm. Giữ hoặc trả lại mọi viên chưa khóa trước đã.
midnight-invalid-die-index = Viên xúc xắc đó không có trong lần gieo này.

midnight-die-locked = { $value } (đã khóa)
midnight-die-kept = { $value } (đang giữ)
midnight-die-value = { $value }
midnight-die-index = Viên { $index }

midnight-your-dice-not-rolled = Bạn chưa gieo trong lượt này.
midnight-player-dice-not-rolled = { $player } chưa gieo trong lượt này.
midnight-your-dice-status =
    { $qualified ->
        [yes] Xúc xắc của bạn: { $dice }. Đã khóa: { $locked }; đang giữ cho lần gieo tới: { $kept }; còn sống: { $remaining }. Điểm đủ điều kiện hiện tại là { $score } từ { $scoring_dice }.
       *[no] Xúc xắc của bạn: { $dice }. Đã khóa: { $locked }; đang giữ cho lần gieo tới: { $kept }; còn sống: { $remaining }. Bạn vẫn cần { $missing } để đủ điều kiện.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] Xúc xắc của { $player }: { $dice }. Đã khóa: { $locked }; đang giữ cho lần gieo tới: { $kept }; còn sống: { $remaining }. Điểm đủ điều kiện hiện tại là { $score } từ { $scoring_dice }.
       *[no] Xúc xắc của { $player }: { $dice }. Đã khóa: { $locked }; đang giữ cho lần gieo tới: { $kept }; còn sống: { $remaining }. { GENDER_TERM($player_gender, "subject-capitalized") } vẫn cần { $missing } để đủ điều kiện.
    }

midnight-status-round = Vòng { $round } trên { $total }
midnight-status-current-player = Đang tới lượt: { $player }
midnight-status-current-not-rolled = { $player } chưa gieo.
midnight-status-current-dice =
    { $qualified ->
        [yes] Xúc xắc hiện tại của { $player }: { $dice }. Điểm tạm tính: { $score } từ { $scoring_dice }. Khóa { $locked}, giữ { $kept}, còn sống { $remaining}.
       *[no] Xúc xắc hiện tại của { $player }: { $dice }. Thiếu { $missing}. Khóa { $locked}, giữ { $kept}, còn sống { $remaining}.
    }
midnight-status-dice-not-rolled = chưa gieo
midnight-status-last-qualified = Lượt trước: { $player } gieo { $dice } và ghi { $score } điểm.
midnight-status-last-disqualified = Lượt trước: { $player } gieo { $dice } và không đủ điều kiện.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } vòng thắng; vòng hiện tại { $current}, đủ điều kiện.
       *[no] { $rank }. { $player }: { $wins } vòng thắng; vòng hiện tại { $current}, chưa đủ điều kiện.
    }

midnight-score-unit-round-wins = { $count ->
    [one] vòng thắng
   *[other] vòng thắng
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] vòng thắng
   *[other] vòng thắng
}
