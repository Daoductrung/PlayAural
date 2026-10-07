game-name-flip7 = Flip 7

# Tuỳ chọn
flip7-set-target-score = Điểm mục tiêu: { $score }
flip7-enter-target-score = Nhập điểm mục tiêu
flip7-option-changed-target = Đã đặt điểm mục tiêu là { $score }.
flip7-desc-target-score = Mốc điểm bắt đầu xét thắng sau mỗi vòng. Người có tổng điểm cao nhất sẽ thắng; nếu cùng dẫn đầu, trận đấu tiếp tục. Mặc định: 200, phạm vi 50–1000.

# Các lá bài
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = Nhân đôi
flip7-card-second-chance = Cơ hội thứ hai
flip7-card-freeze = Đóng băng
flip7-card-flip-three = Lật 3

# Hành động trong lượt
flip7-hit = Lật một lá
flip7-stay = Dừng lại và giữ { $points } { $points ->
        [one] điểm
       *[other] điểm
    }
flip7-stay-base = Dừng lại và giữ điểm
flip7-stay-banked = Dừng lại và giữ điểm (đã dừng)
flip7-you-stay = Bạn dừng lại và giữ { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-player-stays = { $player } dừng lại và giữ { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.

# Vòng đấu
flip7-round-start = Vòng { $round }. { $dealer } chia bài.
flip7-round-start-you = Vòng { $round }. Bạn chia bài.
flip7-round-end = Vòng { $round } đã kết thúc.
flip7-round-score = { $player } ghi { $points } { $points ->
        [one] điểm
       *[other] điểm
    } trong vòng này. Tổng điểm trận: { $total } { $total ->
        [one] điểm
       *[other] điểm
    }.
flip7-round-score-you = Bạn ghi { $points } { $points ->
        [one] điểm
       *[other] điểm
    } trong vòng này. Tổng điểm trận: { $total } { $total ->
        [one] điểm
       *[other] điểm
    }.
flip7-round-bust = { $player } đã cháy bài và không được điểm.
flip7-round-bust-you = Bạn đã cháy bài và không được điểm trong vòng này.
flip7-match-win = { $player } chiến thắng trận đấu!
flip7-match-win-you = Bạn chiến thắng trận đấu!
flip7-deck-reshuffled = Chồng bài bỏ được xáo thành chồng bài rút mới.
flip7-you-pending-bust-discarded = Bạn đã cháy bài, nên các lá hành động đang chờ xử lý bị bỏ.
flip7-player-pending-bust-discarded = { $player } đã cháy bài, nên các lá hành động đang chờ xử lý bị bỏ.

# Lật bài
flip7-you-turn-card = Bạn lật một lá bài.
flip7-player-turns-card = { $player } lật một lá bài.
flip7-your-card-is = Lá bài: { $card }.
flip7-player-card-is = Lá của { $player }: { $card }.
flip7-you-stop-alone = Bạn là người duy nhất còn trong vòng, nên tự dừng lại và giữ { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-player-stops-alone = { $player } là người duy nhất còn trong vòng, nên tự dừng lại và giữ { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-you-set-second-chance = Bạn giữ lại một lá Cơ hội thứ hai.
flip7-player-sets-second-chance = { $player } giữ lại một lá Cơ hội thứ hai.
flip7-second-chance-saves = Cơ hội thứ hai giúp { $player } tránh cháy bài vì lật trùng { $value }.
flip7-second-chance-saves-you = Cơ hội thứ hai giúp bạn tránh cháy bài vì lật trùng { $value }.
flip7-you-bust = Bạn lật thêm một lá { $value } và cháy bài. Bạn không ghi điểm trong vòng này.
flip7-player-busts = { $player } lật thêm một lá { $value }, cháy bài và không ghi điểm trong vòng này.
flip7-flip-seven = { $player } hoàn thành Flip 7 và nhận thêm { $bonus } điểm!
flip7-flip-seven-you = Bạn hoàn thành Flip 7 và nhận thêm { $bonus } điểm!

# Lựa chọn có mục tiêu
flip7-choice-required = Hãy chọn mục tiêu cho lá { $action }.
flip7-target-freeze = Đóng băng { $target } ({ $points } { $points ->
        [one] điểm
       *[other] điểm
    })
flip7-target-flip-three = Buộc { $target } lật ba lá
flip7-target-second-chance-self = Giữ Cơ hội thứ hai
flip7-target-second-chance = Trao Cơ hội thứ hai cho { $target }
flip7-you-stop-player = Bạn đóng băng { $target } ở mức { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-player-stops-player = { $player } đóng băng { $target } ở mức { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-you-stop-yourself = Bạn dùng Đóng băng lên chính mình ở mức { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-player-stops-themself = { $player } dùng Đóng băng lên chính mình ở mức { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-you-flip-three = Bạn buộc { $target } lật ba lá.
flip7-player-flip-three = { $player } buộc { $target } lật ba lá.
flip7-you-flip-three-self = Bạn tự lật ba lá.
flip7-player-flips-three-self = { $player } tự lật ba lá.
flip7-you-give-second-chance = Bạn trao Cơ hội thứ hai cho { $target }.
flip7-player-gives-second-chance = { $player } trao Cơ hội thứ hai cho { $target }.
flip7-you-discard-second-chance = Không ai có thể nhận, nên lá Cơ hội thứ hai bị loại bỏ.
flip7-player-discards-second-chance = { $player } không thể trao lá Cơ hội thứ hai, nên nó bị loại bỏ.
flip7-you-discard-action = Không có ai để nhắm vào, nên { $action } bị loại bỏ.
flip7-player-discards-action = { $player } không có ai để nhắm vào, nên { $action } bị loại bỏ.

# Hành động thông tin
flip7-check-area = Nghe khu vực của tôi
flip7-check-area-description = Nghe các lá đang ngửa, trạng thái và điểm vòng hiện tại của bạn.
flip7-check-table = Xem bàn chơi
flip7-check-table-description = Mở bảng cập nhật trực tiếp về vòng đấu, giai đoạn hiện tại, bài công khai và điểm của từng người chơi.
flip7-check-deck = Nghe bộ bài
flip7-check-deck-description = Nghe số lá còn trong chồng bài rút và chồng bài bỏ.
flip7-check-scores = Nghe điểm
flip7-review-scores = Xem điểm chi tiết
flip7-you-label = Bạn
flip7-area-status-playing = còn trong vòng
flip7-area-status-scored = đã ghi điểm
flip7-area-status-stayed = đã dừng
flip7-area-status-busted = đã cháy bài
flip7-area-numbers-none = không có
flip7-area-inline = { $who}, { $status }. Lá số: { $numbers }. Điểm vòng: { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-area-inline-with-specials = { $who}, { $status }. Lá số: { $numbers }. Lá khác: { $specials }. Điểm vòng: { $points } { $points ->
        [one] điểm
       *[other] điểm
    }.
flip7-area-resolving-card = { $area } Lá đang được xử lý: { $card }.
flip7-check-round = Vòng { $round }. Điểm mục tiêu { $target }.
flip7-table-line = { $area } Tổng điểm trận: { $total } { $total ->
        [one] điểm
       *[other] điểm
    }.
flip7-deck-line = Chồng bài rút: { $count ->
        [one] { $count } lá
       *[other] { $count } lá
    }
flip7-discard-line = Chồng bài bỏ: { $count ->
        [one] { $count } lá
       *[other] { $count } lá
    }

# Trạng thái lượt và chuỗi sự kiện
flip7-whose-turn-choice-you = Bạn đang chọn mục tiêu cho lá { $action }.
flip7-whose-turn-choice-player = { $player } đang chọn mục tiêu cho lá { $action }.
flip7-whose-turn-dealing-you = Vòng { $round }: bạn đang chia bài.
flip7-whose-turn-dealing-player = Vòng { $round }: { $player } đang chia bài.
flip7-whose-turn-deal-card-you = Vòng { $round }: lá khởi đầu của bạn chưa xử lý xong.
flip7-whose-turn-deal-card-player = Vòng { $round }: lá khởi đầu của { $player } chưa xử lý xong.
flip7-whose-turn-card-you = Lá bài của bạn chưa xử lý xong.
flip7-whose-turn-card-player = Lá bài của { $player } chưa xử lý xong.
flip7-whose-turn-flip-three-you = Bạn đang lật 3 lá.
flip7-whose-turn-flip-three-player = { $player } đang lật 3 lá.
flip7-whose-turn-banking-you = Bạn đang dừng lại và giữ điểm.
flip7-whose-turn-banking-player = { $player } đang dừng lại và giữ điểm.
flip7-whose-turn-round-end = Vòng { $round } đang chốt điểm.
flip7-whose-turn-match-end = Đang công bố người thắng.
flip7-whose-turn-resolving = Chuỗi lật bài hiện tại chưa kết thúc.

# Lý do bị chặn
flip7-error-wait-card = Hãy đợi lá bài hiện tại được xử lý xong.
flip7-error-make-choice = Hãy chọn mục tiêu trước khi lật thêm hoặc dừng lại.
flip7-error-wait-choice = Hãy đợi lựa chọn mục tiêu hiện tại hoàn tất.
flip7-error-wait-flip-three = Hãy đợi Lật 3 hoàn tất.
flip7-error-wait-dealing = Hãy đợi việc chia bài hoàn tất.
flip7-error-not-playing-round = Bạn không còn chơi trong vòng này.
flip7-error-no-cards-to-bank = Bạn cần có ít nhất một lá trong khu vực trước khi dừng.
flip7-error-no-choice = Không có lựa chọn lá bài nào cần trả lời.
flip7-error-wait-banking = Hãy đợi việc giữ điểm hiện tại hoàn tất.
flip7-error-choice-not-ready = Hãy đợi danh sách mục tiêu xuất hiện.

# Màn hình kết thúc
flip7-line-format = { $rank }. { $player }: { $points }
