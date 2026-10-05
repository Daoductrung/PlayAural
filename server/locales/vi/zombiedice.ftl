game-name-zombiedice = Zombie Dice

zombiedice-set-target-score = Mốc thắng: { $score } não
zombiedice-enter-target-score = Nhập mốc thắng từ 5 đến 50 não:
zombiedice-option-changed-target-score = Mốc thắng hiện là { $score } não.
zombiedice-desc-target-score = Khi một người đạt mốc này, những người còn lại trong vòng sẽ chơi nốt. Mốc chính thức là 13 não; tăng hoặc giảm mốc sẽ kéo dài hoặc rút ngắn ván.

zombiedice-roll-first = Gieo 3 xúc xắc
zombiedice-roll-first-description = Rút kín ba viên xúc xắc trong cốc rồi gieo.
zombiedice-roll-again = Gieo tiếp — { $brains } { $brains ->
    [one] não
   *[other] não
} chưa ghi
zombiedice-roll-again-description = Gieo lại { $footprints } { $footprints ->
    [one] viên dấu chân
   *[other] viên dấu chân
} và rút thêm { $draw } { $draw ->
    [one] viên
   *[other] viên
} cho đủ ba. Phát súng thứ ba sẽ xóa sạch { $brains } { $brains ->
    [one] não
   *[other] não
} chưa ghi điểm.
zombiedice-bank = Dừng và ghi { $brains } { $brains ->
    [one] não
   *[other] não
}
zombiedice-bank-keybind = Dừng và ghi điểm
zombiedice-bank-description = Kết thúc lượt và ghi { $brains } { $brains ->
    [one] não
   *[other] não
}.
zombiedice-check-turn-totals = Nghe tổng trong lượt
zombiedice-check-turn-totals-description = Nghe tổng số não, phát súng và dấu chân của lượt hiện tại.
zombiedice-review-turn = Xem chi tiết lượt
zombiedice-review-turn-description = Xem mọi xúc xắc công khai, số viên trong cốc, lần gieo gần nhất và số não chưa ghi.
zombiedice-review-table = Xem tình hình bàn
zombiedice-review-table-description = Xem mốc thắng, giai đoạn, thứ tự lượt, người đang chơi và điểm số.

zombiedice-game-start = Zombie Dice bắt đầu. Mốc thắng: { $target } não. { $first } đi trước. Thứ tự: { $order }.
zombiedice-your-turn = Đến lượt bạn. Đã ghi: { $score } { $score ->
    [one] não
   *[other] não
}. Hãy gieo ba viên.
zombiedice-player-turn = Đến lượt { $player }. Đã ghi: { $score } { $score ->
    [one] não
   *[other] não
}.
zombiedice-you-refill-cup = Cốc gần cạn: bạn trả lại { $count } { $count ->
    [one] viên xúc xắc não
   *[other] viên xúc xắc não
}. Vẫn tính đủ { $brains } { $brains ->
    [one] não
   *[other] não
} của lượt.
zombiedice-player-refills-cup = Cốc gần cạn: { $player } trả lại { $count } { $count ->
    [one] viên xúc xắc não
   *[other] viên xúc xắc não
}. Vẫn tính đủ { $brains } { $brains ->
    [one] não
   *[other] não
} của lượt.
zombiedice-you-roll = Bạn gieo: { $results }.
zombiedice-player-rolls = { $player } gieo: { $results }.
zombiedice-you-bust = Bạn gieo: { $results }. Tổng { $shotguns } phát súng—bị bắn hạ, mất { $brains } { $brains ->
    [one] não
   *[other] não
} chưa ghi.
zombiedice-player-busts = { $player } gieo: { $results }. Tổng { $shotguns } phát súng—bị bắn hạ, mất { $brains } { $brains ->
    [one] não
   *[other] não
} chưa ghi.
zombiedice-you-bank = Bạn ghi { $brains } { $brains ->
    [one] não
   *[other] não
}. Tổng: { $total }.
zombiedice-player-banks = { $player } ghi { $brains } { $brains ->
    [one] não
   *[other] não
}. Tổng: { $total }.
zombiedice-you-trigger-final-round = Bạn đạt { $score } não. Vòng cuối còn { $remaining } { $remaining ->
    [one] người chơi
   *[other] người chơi
}.
zombiedice-player-triggers-final-round = { $player } đạt { $score } não. Vòng cuối còn { $remaining } { $remaining ->
    [one] người chơi
   *[other] người chơi
}.
zombiedice-tiebreak-start = Vòng phân thắng bại { $round }: { $players } cùng có { $score } não. Mỗi người một lượt.
zombiedice-you-win = Bạn thắng Zombie Dice với { $score } não.
zombiedice-player-wins = { $player } thắng Zombie Dice với { $score } não.

zombiedice-error-roll-before-stopping = Hãy gieo một lần trước khi dừng. Sau bất kỳ lần gieo an toàn nào, bạn được phép dừng với 0 não.
zombiedice-error-roll-resolving = Xúc xắc vẫn đang lăn.
zombiedice-error-target-score-range = Mốc thắng phải từ { $min } đến { $max } não; giá trị hiện tại là { $value }.

zombiedice-color-green = xanh lá
zombiedice-color-yellow = vàng
zombiedice-color-red = đỏ
zombiedice-face-brain = não
zombiedice-face-footprint = dấu chân
zombiedice-face-shotgun = phát súng
zombiedice-roll-result = { $color } ra { $face }
zombiedice-pool-color = { $count } { $count ->
    [one] viên xúc xắc
   *[other] viên xúc xắc
} { $color }
zombiedice-no-dice = không có

zombiedice-status-no-turn = Hiện chưa có lượt Zombie Dice nào.
zombiedice-your-turn-totals = Bạn: { $brains } { $brains ->
    [one] não
   *[other] não
}, { $shotguns } { $shotguns ->
    [one] phát súng
   *[other] phát súng
} và { $footprints } { $footprints ->
    [one] dấu chân
   *[other] dấu chân
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] não
   *[other] não
}, { $shotguns } { $shotguns ->
    [one] phát súng
   *[other] phát súng
} và { $footprints } { $footprints ->
    [one] dấu chân
   *[other] dấu chân
}.
zombiedice-status-turn-you = Lượt của bạn — đã ghi: { $score } { $score ->
    [one] não
   *[other] não
}.
zombiedice-status-turn-player = Lượt của { $player } — đã ghi: { $score } { $score ->
    [one] não
   *[other] não
}.
zombiedice-status-turn-totals = Lượt này: { $brains } { $brains ->
    [one] não
   *[other] não
}, { $shotguns } { $shotguns ->
    [one] phát súng
   *[other] phát súng
} và { $footprints } { $footprints ->
    [one] dấu chân
   *[other] dấu chân
}.
zombiedice-status-cup = Trong cốc: { $count } { $count ->
    [one] viên xúc xắc
   *[other] viên xúc xắc
}.
zombiedice-status-footprints = Dấu chân phải gieo lại: { $dice }.
zombiedice-status-brain-dice = Xúc xắc não đã đặt riêng: { $dice }.
zombiedice-status-shotgun-dice = Xúc xắc súng đã đặt riêng: { $dice }.
zombiedice-status-last-roll = Lần gieo gần nhất: { $results }.
zombiedice-status-awaiting-roll = Lượt này chưa gieo.
zombiedice-status-table-header = Zombie Dice — vòng { $round }; mốc thắng: { $target } não.
zombiedice-status-table-header-tiebreak = Zombie Dice — mốc thắng: { $target } não.
zombiedice-status-main-round = Giai đoạn: ván chính.
zombiedice-status-final-round = Vòng cuối — { $player } đã đạt mốc.
zombiedice-status-tiebreak = Vòng phân thắng bại { $round }: { $players }.
zombiedice-status-current-you = Lượt của bạn.
zombiedice-status-current-player = Lượt của { $player }.
zombiedice-status-turn-order = Thứ tự lượt: { $players }.
zombiedice-status-score-you = Bạn: { $score } { $score ->
    [one] não
   *[other] não
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] não
   *[other] não
}.

zombiedice-score-unit-brains = { $count ->
    [one] não
   *[other] não
}
zombiedice-results-header = Kết quả Zombie Dice
zombiedice-results-winner = Người thắng: { $player } với { $score } não.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] não
   *[other] não
}.
