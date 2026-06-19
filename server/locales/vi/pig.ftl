game-name-pig = Pig

pig-roll = Gieo xúc xắc
pig-hold = Giữ { $points } điểm
pig-check-turn-status = Xem tình hình lượt chơi

pig-game-start =
    Ván Pig bắt đầu. { $team ->
        [yes] Đội
       *[no] Người chơi
    } đầu tiên giữ đủ { $target } điểm sẽ thắng ngay. Xúc xắc có { $sides } mặt; gieo trúng mặt 1 sẽ làm mất toàn bộ điểm chưa giữ trong lượt đó. { $minimum ->
        [0] Bạn có thể giữ điểm sau bất kỳ lần gieo nào ghi được điểm.
       *[other] Bạn phải tích lũy ít nhất { $minimum } điểm lượt mới được giữ điểm.
    }
pig-game-start-brief =
    Bắt đầu Pig. Điểm đích: { $target }. Xúc xắc: { $sides } mặt. Mức giữ tối thiểu: { $minimum }.{ $team ->
        [yes] Các thành viên dùng chung điểm đội.
       *[no] Mỗi người có điểm riêng.
    }
pig-round-start = Bắt đầu vòng lượt { $round }. Mỗi người chơi đang tham gia sẽ có một lượt.
pig-round-start-brief = Vòng lượt { $round }.

pig-you-roll-result = Bạn gieo được { $roll }. Điểm lượt hiện tại của bạn là { $total }.
pig-player-roll-result = { $player } gieo được { $roll }. Điểm lượt hiện tại của họ là { $total }.
pig-you-roll-result-brief = Bạn: { $roll }; điểm lượt { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; điểm lượt { $total }.

pig-you-bust = Bạn gieo trúng mặt 1 và mất toàn bộ { $points } điểm chưa giữ. Lượt của bạn kết thúc mà không ghi được điểm.
pig-player-busts = { $player } gieo trúng mặt 1 và mất toàn bộ { $points } điểm chưa giữ. Lượt của họ kết thúc mà không ghi được điểm.
pig-you-bust-brief = Bạn gieo trúng 1 và mất { $points } điểm lượt.
pig-player-busts-brief = { $player } gieo trúng 1 và mất { $points } điểm lượt.

pig-you-hold =
    Bạn giữ { $points } điểm. { $team ->
        [yes] Đội của bạn hiện có { $total } điểm.
       *[no] Tổng điểm của bạn hiện là { $total }.
    }
pig-player-holds =
    { $player } giữ { $points } điểm. { $team ->
        [yes] { $team_name } hiện có { $total } điểm.
       *[no] Tổng điểm của họ hiện là { $total }.
    }
pig-you-hold-brief =
    Bạn giữ { $points };{ $team ->
        [yes] { $team_name } có tổng cộng { $total }.
       *[no] tổng điểm của bạn là { $total }.
    }
pig-player-holds-brief =
    { $player } giữ { $points };{ $team ->
        [yes] { $team_name } có tổng cộng { $total }.
       *[no] tổng điểm là { $total }.
    }

pig-you-win =
    { $team ->
        [yes] Đội của bạn, { $winner }, là đội thắng Pig với { $score } điểm!
       *[no] Bạn là người thắng Pig với { $score } điểm!
    }
pig-winner =
    { $team ->
        [yes] Bên thắng là { $winner } với { $score } điểm!
       *[no] Người thắng là { $winner } với { $score } điểm!
    }
pig-you-win-brief =
    { $team ->
        [yes] Đội thắng: đội của bạn, { $winner }, với { $score } điểm.
       *[no] Người thắng: bạn, với { $score } điểm.
    }
pig-winner-brief = Bên thắng: { $winner }, với { $score } điểm.

pig-confirm-risky-roll =
    Nếu gieo tiếp, bạn có thể mất { $points } điểm chưa giữ; xác suất gieo trúng mặt 1 là { $risk } phần trăm. { $winning ->
        [yes] Nếu giữ điểm ngay, bạn sẽ có { $total } điểm và thắng ván.
       *[no] Nếu giữ điểm ngay, bạn sẽ có { $total } trên { $target } điểm cần để thắng.
    } Hãy nhấn Gieo xúc xắc lần nữa trong vòng { $seconds } giây để xác nhận.

pig-action-resolving = Xúc xắc vẫn đang lăn. Hãy chờ kết quả.
pig-no-turn-points = Hãy gieo xúc xắc ít nhất một lần trước khi giữ điểm.
pig-need-more-points = Bạn đang có { $current } điểm lượt, nhưng bàn này yêu cầu ít nhất { $required } điểm mới được giữ.

pig-set-min-bank = Mức giữ tối thiểu: { $points } điểm
pig-set-dice-sides = Số mặt xúc xắc: { $sides }
pig-enter-min-bank = Nhập số điểm lượt tối thiểu cần có để được giữ điểm:
pig-enter-dice-sides = Nhập số mặt của xúc xắc:
pig-option-changed-min-bank = Mức giữ tối thiểu đã đổi thành { $points } điểm.
pig-option-changed-dice = Xúc xắc giờ có { $sides } mặt.
pig-desc-target-score = Người chơi hoặc đội đầu tiên giữ đủ tổng điểm này sẽ thắng ngay.
pig-desc-min-bank = Số điểm lượt cần có trước khi được phép Giữ điểm. Đặt là 0 để chơi theo luật Pig tiêu chuẩn.
pig-desc-dice-sides = Số mặt của một viên xúc xắc. Pig tiêu chuẩn dùng xúc xắc sáu mặt; gieo trúng mặt 1 luôn làm mất điểm lượt.
pig-desc-team-mode = Chơi cá nhân hoặc dùng chung một tổng điểm với đồng đội. Đội thắng ngay khi một thành viên giữ đủ điểm.

pig-error-target-out-of-range = Điểm đích { $value } không hợp lệ. Hãy chọn từ { $min } đến { $max }.
pig-error-min-bank-out-of-range = Mức giữ tối thiểu { $value } không hợp lệ. Hãy chọn từ { $min } đến { $max }.
pig-error-dice-sides-out-of-range = Không hỗ trợ xúc xắc { $value } mặt. Hãy chọn từ { $min } đến { $max } mặt.
pig-error-min-bank-too-high = Mức giữ tối thiểu { $minimum } phải thấp hơn điểm đích { $target }.

pig-status-target = Điểm đích: { $target }.
pig-status-round = Vòng lượt hiện tại: { $round }.
pig-status-current-turn = { $player } đang chơi: đã giữ { $banked } điểm, có { $turn } điểm trong lượt, và sẽ có { $potential } điểm nếu giữ ngay.
pig-status-standing = { $rank }. { $team }: { $score } điểm.

pig-line-format = { $rank }. { $player }: { $points }
