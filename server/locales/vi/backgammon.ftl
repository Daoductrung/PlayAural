# Backgammon localization

game-name-backgammon = Cờ thỏ cáo

# Colors
backgammon-color-red = đỏ
backgammon-color-white = trắng

# Menu helpers
backgammon-unavailable = không khả dụng

# Game start
backgammon-game-started = { $red } chơi Đỏ, { $white } chơi Trắng.
backgammon-opening-roll = Lượt tung mở màn: { $red } tung được { $red_die }, { $white } tung được { $white_die }.
backgammon-opening-tie = Cả hai đều tung được { $die }, tung lại.
backgammon-opening-winner = { $player } đi trước với { $die1 } và { $die2 }.

# Dice
backgammon-roll = { $player } tung được { $die1 } và { $die2 }.

# No moves
backgammon-no-moves = { $player } không có nước đi hợp lệ.

# Move commentary (shorthand)
backgammon-move-normal = { $src } đến { $dest }, còn { $remain } { $count }.
backgammon-move-emptying = Bỏ trống { $src } đến { $dest }, { $count }.
backgammon-move-hit = { $src } để bắt ở { $dest }, còn { $remain }.
backgammon-move-emptying-hit = Bỏ trống { $src } để bắt ở { $dest }.
backgammon-move-bar = Từ thanh đến { $dest }, { $count }.
backgammon-move-bar-hit = Từ thanh để bắt ở { $dest }, { $count }.
backgammon-move-bearoff = Đưa quân ra từ { $src }, còn { $remain }.

# Verbose move commentary
backgammon-verbose-move-normal = { $is_self ->
    [yes] Bạn di chuyển một quân từ điểm { $src } đến điểm { $dest }.
    *[no] { $player } di chuyển một quân từ điểm { $src } đến điểm { $dest }.
} { $src_count ->
    [0] Điểm { $src } hiện đã trống, { $dest_count } ở điểm { $dest }.
    *[other] { $src_count } hiện ở điểm { $src }, { $dest_count } ở điểm { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] Bạn di chuyển một quân từ điểm { $src } để bắt quân của { $opponent } ở điểm { $dest }.
    [spectator] { $player } di chuyển một quân từ điểm { $src } để bắt quân của { $opponent } ở điểm { $dest }.
    *[no] { $player } di chuyển một quân từ điểm { $src } để bắt quân của bạn ở điểm { $dest }.
} { $src_count ->
    [0] Điểm { $src } hiện đã trống.
    *[other] Còn { $src_count } ở điểm { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] Bạn nhập quân từ thanh vào điểm { $dest }.
    *[no] { $player } nhập quân từ thanh vào điểm { $dest }.
} hiện có { $dest_count } ở điểm { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] Bạn nhập quân từ thanh để bắt quân của { $opponent } ở điểm { $dest }.
    [spectator] { $player } nhập quân từ thanh để bắt quân của { $opponent } ở điểm { $dest }.
    *[no] { $player } nhập quân từ thanh để bắt quân của bạn ở điểm { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] Bạn đưa quân ra từ điểm { $src }.
    *[no] { $player } đưa quân ra từ điểm { $src }.
} { $src_count ->
    [0] Điểm { $src } hiện đã trống.
    *[other] Còn { $src_count } ở điểm { $src }.
}

# Doubling
backgammon-doubles = { $player } nhân đôi lên { $value }.
backgammon-accepts = { $player } chấp nhận.
backgammon-drops = { $player } bỏ.
backgammon-accept = Chấp nhận
backgammon-drop = Bỏ

# Point labels
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } đã chọn
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } đã chọn

# Action labels
backgammon-label-double = Nhân đôi
backgammon-label-undo = Hoàn tác

# Selection feedback
backgammon-selected-point = Đã chọn điểm { $point }, { $count } quân.
backgammon-selected-bar = Đã chọn thanh.
backgammon-deselected = Đã bỏ chọn.
backgammon-no-checkers-there = Không có quân ở đó.
backgammon-not-your-checkers = Đó không phải quân của bạn.
backgammon-no-moves-from-here = Không có nước đi hợp lệ từ đây.
backgammon-must-enter-from-bar = Phải nhập quân từ thanh trước.
backgammon-illegal-move = Nước đi không hợp lệ.
backgammon-bearoff-blocked = Bạn không thể đưa quân ra từ điểm { $point } với { $die }, vì còn quân ở điểm { $blocking_point } của bạn.
backgammon-bearoff-no-die = Bạn không thể đưa quân ra từ điểm { $point } với các xúc xắc còn lại ({ $die }).
backgammon-nothing-to-undo = Không có gì để hoàn tác.
backgammon-undone = Đã hoàn tác nước đi.
backgammon-cannot-double = Bạn không thể nhân đôi lúc này.
backgammon-cannot-undo = Không có gì để hoàn tác.
backgammon-not-doubling-phase = Không có lời nhân đôi nào để phản hồi.

# Info keybinds
backgammon-check-status = Trạng thái
backgammon-check-cube = Khối nhân
backgammon-check-pip = Số điểm pip
backgammon-check-score = Điểm
backgammon-check-dice = Xúc xắc
backgammon-status = Thanh Đỏ: { $bar_red }. Thanh Trắng: { $bar_white }. Đỏ đã ra: { $off_red }. Trắng đã ra: { $off_white }.
backgammon-dice = { $dice }
backgammon-dice-none = Không còn xúc xắc.
backgammon-cube-status = Khối nhân ở { $value }. { $owner ->
    [center] Ở giữa, cả hai người chơi đều có thể nhân đôi.
    *[other] Sở hữu bởi { $owner }.
} { $can_double ->
    [yes] Có thể nhân đôi ngay bây giờ.
    [crawford] Đây là ván Crawford, không được nhân đôi.
    *[no] Hiện không thể nhân đôi.
}
backgammon-cube-no-match = Không có khối nhân trong ván đơn.
backgammon-pip-count = Số điểm pip Đỏ: { $red_pip }. Số điểm pip Trắng: { $white_pip }.
backgammon-match-score = { $red } { $red_score }, { $white } { $white_score }. Trận đến { $match_length }. Khối nhân: { $cube }.

# Scoring
backgammon-wins-game = { $player } thắng { $points } điểm.
backgammon-new-game = Bắt đầu ván { $number }.
backgammon-match-winner = { $player } thắng trận!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. Trận đến { $match_length }.
backgammon-crawford = Ván Crawford: không nhân đôi ở ván này.

# Difficulty levels
backgammon-difficulty-random = Ngẫu nhiên
backgammon-difficulty-simple = Đơn giản

# Options
backgammon-option-match-length = Độ dài trận: { $match_length }
backgammon-option-select-match-length = Đặt độ dài trận (1-25)
backgammon-option-changed-match-length = Độ dài trận đã được đặt thành { $match_length }.
backgammon-option-bot-difficulty = Độ khó bot: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Chọn độ khó bot
backgammon-option-changed-bot-difficulty = Độ khó bot đã được đặt thành { $bot_difficulty }.
