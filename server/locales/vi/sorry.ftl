game-name-sorry = Sorry!

sorry-set-rules-profile = Luật chơi: { $profile }
sorry-select-rules-profile = Chọn bộ luật
sorry-option-changed-rules-profile = Luật chơi đã đổi thành { $profile }.
sorry-rules-profile-classic-00390 = Bản cổ điển 00390
sorry-rules-profile-a5065-core = Bản A5065 Core

sorry-toggle-auto-apply-single-move = Tự đi khi chỉ có một nước: { $enabled }
sorry-option-changed-auto-apply-single-move = Tự đi khi chỉ có một nước đã đổi thành { $enabled }.
sorry-toggle-faster-setup-one-pawn-out = Khởi đầu nhanh (ra sẵn một quân): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = Khởi đầu nhanh đã đổi thành { $enabled }.
sorry-error-unsupported-rules-profile = Bộ luật Sorry "{ $profile }" không được hỗ trợ. Hãy chọn Classic 00390 hoặc A5065 Core trước khi bắt đầu.

sorry-draw-card = Rút thẻ
sorry-check-board = Xem bàn cờ
sorry-check-pawns = Xem quân của bạn
sorry-check-card = Xem thẻ hiện tại
sorry-check-status = Xem trạng thái

sorry-move-slot = Nước đi { $slot }
sorry-move-slot-fallback = Chọn nước đi
sorry-move-start = Đưa quân { $pawn } từ { $position } ra khỏi điểm xuất phát
sorry-move-forward = Đi quân { $pawn } từ { $position } tiến { $steps }
sorry-move-backward = Đi quân { $pawn } từ { $position } lùi { $steps }
sorry-move-swap = Đổi chỗ quân { $pawn } ở { $position } với quân { $target_pawn } của { $target_player } ở { $target_position }
sorry-move-sorry = Dùng thẻ Sorry! với quân { $pawn } ở { $position } để thay quân { $target_pawn } của { $target_player } ở { $target_position }
sorry-move-split7-pick = Chia 7 cho quân { $pawn_a } ở { $position_a } và quân { $pawn_b } ở { $position_b }
sorry-move-split7-option = Quân { $pawn_a } ở { $position_a } đi { $steps_a }, quân { $pawn_b } ở { $position_b } đi { $steps_b }

sorry-card-none = chưa có thẻ nào
sorry-card-sorry = Sorry!
sorry-choose-move = Hãy chọn một nước đi.
sorry-choose-split = Hãy chọn cách chia 7.
sorry-error-draw-pending-move = Bạn đã rút thẻ rồi. Hãy chọn một nước đi hợp lệ của thẻ đó trước khi rút tiếp.

sorry-game-started = Ván Sorry bắt đầu. Người chơi: { $players }.
sorry-draw-announcement = { $player } rút được thẻ { $card }.
sorry-you-draw-announcement = Bạn rút được thẻ { $card }.
sorry-no-legal-moves = { $player } không có nước đi hợp lệ với thẻ { $card }.
sorry-you-no-legal-moves = Bạn không có nước đi hợp lệ với thẻ { $card }.
sorry-deck-exhausted = Chồng bài Sorry! đã hết, nên ván cờ kết thúc tại đây.
sorry-you-extra-turn = Bạn rút thẻ 2 và được đi thêm lượt.
sorry-player-extra-turn = { $player } rút thẻ 2 và được đi thêm lượt.

sorry-play-start =
    { $brief ->
        [yes] { $player }: quân { $pawn } xuất phát đến { $destination }.
       *[no] { $player } xuất quân { $pawn } đến { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] Bạn: quân { $pawn } xuất phát đến { $destination }.
       *[no] Bạn xuất quân { $pawn } đến { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: quân { $pawn } +{ $steps } đến { $destination }.
       *[no] { $player } đi quân { $pawn } tiến { $steps } bước đến { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] Bạn: quân { $pawn } +{ $steps } đến { $destination }.
       *[no] Bạn đi quân { $pawn } tiến { $steps } bước đến { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: quân { $pawn } -{ $steps } đến { $destination }.
       *[no] { $player } đi quân { $pawn } lùi { $steps } bước về { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] Bạn: quân { $pawn } -{ $steps } đến { $destination }.
       *[no] Bạn đi quân { $pawn } lùi { $steps } bước về { $destination }.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: quân { $pawn } đổi { $target_player } quân { $target_pawn }; { $destination }.
       *[no] { $player } đổi chỗ quân { $pawn } với quân { $target_pawn } của { $target_player }, rồi dừng ở { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] Bạn: quân { $pawn } đổi { $target_player } quân { $target_pawn }; { $destination }.
       *[no] Bạn đổi chỗ quân { $pawn } với quân { $target_pawn } của { $target_player }, rồi dừng ở { $destination }.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: Sorry! quân { $pawn } đến { $destination }; { $target_player } quân { $target_pawn } về xuất phát.
       *[no] { $player } dùng lá Sorry! để thay quân { $target_pawn } của { $target_player }, rồi dừng ở { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] Bạn: Sorry! quân { $pawn } đến { $destination }; { $target_player } quân { $target_pawn } về xuất phát.
       *[no] Bạn dùng lá Sorry! để thay quân { $target_pawn } của { $target_player }, rồi dừng ở { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: quân { $pawn_a } +{ $steps_a } đến { $destination_a }; quân { $pawn_b } +{ $steps_b } đến { $destination_b }.
       *[no] { $player } chia 7: quân { $pawn_a } đi { $steps_a } bước đến { $destination_a }, còn quân { $pawn_b } đi { $steps_b } bước đến { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] Bạn: quân { $pawn_a } +{ $steps_a } đến { $destination_a }; quân { $pawn_b } +{ $steps_b } đến { $destination_b }.
       *[no] Bạn chia 7: quân { $pawn_a } đi { $steps_a } bước đến { $destination_a }, còn quân { $pawn_b } đi { $steps_b } bước đến { $destination_b }.
    }

sorry-pawn-home = { $player } đưa quân { $pawn } về nhà.
sorry-you-pawn-home = Quân { $pawn } của bạn đã về nhà.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: quân { $pawn } của bạn về xuất phát.
       *[no] Quân { $pawn } của bạn bị { $by_player } đẩy về điểm xuất phát.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] Bạn: { $target_player } quân { $pawn } về xuất phát.
       *[no] Bạn đẩy quân { $pawn } của { $target_player } về điểm xuất phát.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: { $target_player } quân { $pawn } về xuất phát.
       *[no] { $player } đẩy quân { $pawn } của { $target_player } về điểm xuất phát.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] Bạn: quân mình { $pawn } về xuất phát.
       *[no] Bạn đẩy chính quân { $pawn } của mình về điểm xuất phát.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: quân mình { $pawn } về xuất phát.
       *[no] { $player } đẩy chính quân { $pawn } của mình về điểm xuất phát.
    }

sorry-current-card = Thẻ hiện tại: { $card }.
sorry-view-your-pawn = Quân { $pawn } của bạn: { $zone }.
sorry-board-your-color = Màu quân của bạn: { $color }.
sorry-board-summary-heading = Tóm tắt nhanh:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = quân { $pawn } ở { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = Các ô trên đường đua:
sorry-board-private-areas-heading = Khu riêng của từng người chơi:
sorry-board-square-line = Ô { $square }: { $status }
sorry-board-square-empty = trống
sorry-board-square-slide = cầu trượt màu { $color }
sorry-board-square-token = quân { $pawn } của { $player }
sorry-board-start-line = Khu xuất phát màu { $color } của { $player }: { $pawns }
sorry-board-safety-line = Ô an toàn { $space } màu { $color } của { $player }: { $pawns }
sorry-board-home-line = Nhà màu { $color } của { $player }: { $pawns }
sorry-board-area-empty = trống
sorry-board-area-pawn = quân { $pawn }
sorry-color-red = đỏ
sorry-color-blue = xanh dương
sorry-color-yellow = vàng
sorry-color-green = xanh lá
sorry-location-start = ô xuất phát
sorry-location-track = ô { $position }
sorry-location-home-path = ô an toàn số { $steps }
sorry-location-home = nhà
sorry-zone-start = đang ở điểm xuất phát
sorry-zone-track = đang ở ô { $position }
sorry-zone-home-path = đang ở đường an toàn bậc { $steps }
sorry-zone-home = đã về nhà

sorry-status-turn-number = Lượt { $count }
sorry-status-phase = Giai đoạn: { $phase }
sorry-status-current-card = Thẻ: { $card }
sorry-status-current-player = Người đang chơi: { $player }
sorry-phase-draw = rút thẻ
sorry-phase-choose-move = chọn nước đi
sorry-phase-choose-split = chia 7
sorry-phase-resolving = đang xử lý nước đi

sorry-end-score-line = { $index }. { $player }: { $count } quân đã về nhà
