game-name-truco = Truco

# Tùy chọn
truco-set-variant = Biến thể: { $mode }
truco-select-variant = Chọn biến thể Truco:
truco-option-changed-variant = Biến thể hiện là { $mode }.
truco-desc-variant = Truco Argentina dùng bộ bài Tây Ban Nha 40 lá, có envido và flor tùy chọn. Truco Brazil (Paulista) dùng bộ bài Tây với một lá bài được lật, gọi là vira, quyết định các lá mạnh nhất, và các mức tăng đáng 3, 6, 9 và 12 điểm. Truco Tây Ban Nha (Truc Valencia) dùng bộ bài 22 lá với envit và Joc fora, đáng cả ván chơi.
truco-variant-argentine = Truco Argentina
truco-variant-brazilian = Truco Brazil
truco-variant-spanish = Truco Tây Ban Nha
truco-length-15 = 15 điểm
truco-length-30 = 30 điểm
truco-set-length = Độ dài ván chơi: { $mode }
truco-select-length = Chọn độ dài ván chơi:
truco-option-changed-length = Độ dài ván chơi hiện là { $mode }.
truco-desc-length = Ở ván 15 điểm, bên nào đạt 15 điểm trước sẽ thắng. Ở ván 30 điểm, các điểm từ 1 đến 15 là malas (nửa đầu) và các điểm từ 16 đến 30 là buenas (nửa sau); bên nào đạt 30 điểm trước sẽ thắng.
truco-set-flor = Flor: { $enabled }
truco-option-changed-flor = Flor hiện là { $enabled }.
truco-desc-flor = Khi bật, người được chia ba lá bài cùng chất có flor. Flor được thông báo tự động và hủy envido. Flor trị giá 3 điểm, Contraflor 6 điểm, còn Contraflor al resto trị giá số điểm mà bên đang dẫn đầu còn cần để thắng. Chỉ người có flor mới được trả lời hoặc tăng. Flor có giá trị 20 cộng với giá trị của cả ba lá (hình người tính là 0), nên 7, 6 và 5 cùng chất là 38; flor cao hơn sẽ thắng. Khi tắt, ba lá bài cùng chất không có giá trị đặc biệt.
truco-desc-team-mode = Individual là ván một đấu một dành cho 2 người chơi. 2v2 dùng 4 người chơi và 3v3 dùng 6 người chơi; đồng đội chia sẻ điểm số và có thể gọi thay cho cả đội.

# Bộ bài Tây Ban Nha
truco-suit-oros = Đồng tiền
truco-suit-copas = Cốc
truco-suit-espadas = Kiếm
truco-suit-bastos = Gậy
truco-card-name = { $rank } { $suit }

# Tiếng gọi
truco-call-truco = Truco
truco-call-retruco = Retruco
truco-call-valecuatro = Vale cuatro
truco-call-envido = Envido
truco-call-real-envido = Real envido
truco-call-falta-envido = Falta envido
truco-call-flor = Flor
truco-call-contraflor = Contraflor
truco-call-contraflor-al-resto = Contraflor al resto

# Hành động
truco-action-play-card = { $card }
truco-action-accept = Quiero (chấp nhận)
truco-action-decline = No quiero (từ chối)
truco-action-mazo = Me voy al mazo (bỏ bài của bạn)
truco-read-hand = Đọc các lá bài của bạn
truco-read-table = Đọc các lá bài trên bàn
truco-read-calls = Đọc các tiếng gọi hiện tại

# Diễn biến ván chơi và ván bài
truco-game-start-flor = Truco bắt đầu, có flor. Bên nào đạt { $points } điểm trước sẽ thắng.
truco-game-start-no-flor = Truco bắt đầu, không có flor. Bên nào đạt { $points } điểm trước sẽ thắng.
truco-hand-start = Ván bài { $hand } bắt đầu. Bài đã được chia.
truco-dealer-you = Bạn chia bài.
truco-dealer-player = { $player } chia bài.
truco-mano-you = Bạn là mano và đánh trước.
truco-mano-player = { $player } là mano và đánh trước.
truco-your-cards = Bài của bạn: { $cards }.
truco-no-cards = Bạn không còn lá bài nào.
truco-your-turn = Đến lượt bạn đánh một lá bài.

# Đánh bài và các lượt
truco-play-you = Bạn đánh { $card }.
truco-play-player = { $player } đánh { $card }.
truco-trick-win-you = Lượt { $trick }: bạn thắng với { $card }.
truco-trick-win-teammate = Lượt { $trick }: đồng đội { $player } của bạn thắng với { $card }.
truco-trick-win-opponent = Lượt { $trick }: { $player } thắng với { $card } cho { $team }.
truco-trick-tie = Lượt { $trick } hòa, gọi là parda.

# Gọi và trả lời
truco-call-you = Bạn gọi { $call }.
truco-call-player = { $player } gọi { $call }.
truco-call-goes-first-you = Bạn gọi { $call }. Envido được xử lý trước, trước khi trả lời Truco.
truco-call-goes-first-player = { $player } gọi { $call }. Envido được xử lý trước, trước khi trả lời Truco.
truco-pending-answer = { $player } đã gọi { $call }. Hãy trả lời bằng Quiero hoặc No quiero, hoặc tăng mức cược.
truco-pending-wait = Đang chờ { $team } trả lời { $call }.
truco-accept-you = Bạn nói Quiero với { $call }.
truco-accept-player = { $player } nói Quiero với { $call }.
truco-decline-you = Bạn nói No quiero với { $call }.
truco-decline-player = { $player } nói No quiero với { $call }.
truco-mazo-you = Bạn nói Me voy al mazo và bỏ bài của mình.
truco-mazo-player = { $player } nói Me voy al mazo và bỏ bài.
truco-team-folded-your-team = Tất cả mọi người trong đội của bạn đã bỏ bài.
truco-team-folded-team = Tất cả mọi người trong { $team } đã bỏ bài.
truco-flor-announce-you = Bạn có flor.
truco-flor-announce-player = { $player } có flor.
truco-flor-cancels-envido = Envido bị hủy vì có flor.
truco-reveal-envido-you = Envido thắng với bài của bạn: { $cards }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
truco-reveal-envido-player = Envido do { $player } thắng với { $cards }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
truco-reveal-flor-you = Flor thắng với bài của bạn: { $cards }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
truco-reveal-flor-player = Flor do { $player } thắng với { $cards }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}.

# Envido và flor
truco-falta-envido-value = Falta envido trị giá { $points } { $points ->
    [one] điểm
   *[other] điểm
}.
truco-falta-envido-game = Falta envido: cả hai bên đều đang ở malas, nên bên thắng sẽ thắng toàn bộ ván chơi.

# Điểm và bảng điểm
truco-reason-truco = Truco
truco-reason-envido = Envido
truco-reason-flor = Flor
truco-reason-hand = ván bài
truco-points-your-team = Đội của bạn ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
} nhờ { $reason }.
truco-points-team = { $team } ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
} nhờ { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] điểm
   *[other] điểm
}.
truco-half-buenas-your-team = Đội của bạn bước vào buenas, nửa sau.
truco-half-buenas-team = { $team } bước vào buenas, nửa sau.

# Thông tin
truco-status-no-truco = Chưa có Truco nào được gọi. Ván bài đáng { $points } { $points ->
    [one] điểm
   *[other] điểm
}.
truco-status-truco = Ván bài đang ở mức { $call }, trị giá { $points } { $points ->
    [one] điểm
   *[other] điểm
}.
truco-status-truco-pending = { $call } đang chờ { $team } trả lời.
truco-status-envido-open = Vẫn có thể gọi envido trong ván bài này.
truco-status-envido-closed = Envido đã đóng trong ván bài này.
truco-table-empty = Chưa có lá bài nào được đánh.
truco-table-trick = Lượt { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Lỗi và lý do hành động bị vô hiệu
truco-error-bad-count = Truco cần 2, 4 hoặc 6 người chơi, nhưng hiện có { $count }.
truco-error-team-mode-count = Không thể dùng chế độ đội { $mode } với { $count } người chơi. Hãy dùng Individual cho 2 người, 2v2 cho 4 người hoặc 3v3 cho 6 người.
truco-error-not-your-turn = Đang là lượt đánh bài của { $player }.
truco-error-answer-first = Bạn phải trả lời { $call } trước khi làm việc khác. Hãy chọn Quiero hoặc No quiero, hoặc tăng mức cược.
truco-error-nothing-to-answer = Không có tiếng gọi nào đang chờ bạn trả lời.
truco-error-own-team-call = Đội của bạn đã gọi. Hãy chờ { $team } trả lời { $call }.
truco-error-envido-late = Chỉ có thể gọi envido trước khi bạn đánh lá bài đầu tiên.
truco-error-envido-closed = Envido đã đóng vì Truco đã được chấp nhận.
truco-error-envido-done = Envido đã được chơi trong ván bài này.
truco-error-raise-max = Truco đã ở mức Vale cuatro và không thể tăng thêm.
truco-error-raise-holder = Đội của bạn đã gọi Truco gần nhất. Bây giờ chỉ { $team } mới có thể tăng.
truco-error-flor-none = Bạn đã bỏ bài ở ván này nên không thể gọi hoặc trả lời.
truco-error-flor-holders-only = Chỉ người có flor mới có thể trả lời hoặc tăng một flor.
truco-error-card-not-held = Bạn không có lá bài đó.
truco-error-hand-over = Ván bài đã kết thúc.

# Kết thúc ván chơi
truco-game-win-you = Bạn thắng ván chơi với { $score } { $score ->
    [one] điểm
   *[other] điểm
}!
truco-game-win-player = { $player } thắng ván chơi với { $score } { $score ->
    [one] điểm
   *[other] điểm
}!
truco-game-win-your-team = Đội của bạn thắng ván chơi với { $score } { $score ->
    [one] điểm
   *[other] điểm
}!
truco-game-win-team = { $team } thắng ván chơi với { $score } { $score ->
    [one] điểm
   *[other] điểm
}!
truco-end-title = Kết quả Truco
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] điểm
   *[other] điểm
}.

# Lỗi bổ sung và thông báo chế độ cá nhân
truco-error-flor-off = Ván này đã tắt flor, nên không có gì để gọi hoặc trả lời.
truco-error-flor-window = Phải giải quyết flor trước. Không thể gọi Truco cho đến khi lá bài đầu tiên được đánh.
truco-error-flor-window-closed = Chỉ có thể gọi Contraflor khi cả hai bên đều có flor và trước khi lá bài đầu tiên được đánh.
truco-error-envido-flor = Envido bị hủy trong ván bài này vì có người có flor.
truco-error-envido-cannot-raise = Không thể thêm { $call } vào envido đang được chơi.
truco-points-you = Bạn ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
} nhờ { $reason }.
truco-points-player = { $player } ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
} nhờ { $reason }.
truco-half-buenas-you = Bạn bước vào buenas, nửa sau.
truco-half-buenas-player = { $player } bước vào buenas, nửa sau.

# Thông tin lá bài, mô tả và cử chỉ chạm
truco-card-info-label = Thông tin mục
truco-card-info = { $card }: thắng { $beats } trong số { $total } lá còn lại của bộ bài này.
truco-card-info-envido = { $card }: thắng { $beats } trong số { $total } lá còn lại của bộ bài này. Giá trị envido: { $value }.
truco-desc-call-ladder = { $call }: nâng ván bài lên { $points } { $points ->
    [one] điểm
   *[other] điểm
}. Nếu bị từ chối, bên đã gọi thắng { $refused } { $refused ->
    [one] điểm
   *[other] điểm
}.
truco-desc-call-envido = { $call }: hai bên so sánh envido. Nếu được chấp nhận, bên thắng ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
}. Nếu bị từ chối, bên đã gọi ghi { $refused } { $refused ->
    [one] điểm
   *[other] điểm
}.
truco-desc-call-flor = { $call }: những người có flor so sánh flor. Nếu được chấp nhận, bên thắng ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
}. Nếu bị từ chối, bên đã gọi ghi { $refused } { $refused ->
    [one] điểm
   *[other] điểm
}.
truco-desc-accept = Chấp nhận { $call } và tiếp tục chơi.
truco-desc-decline = Từ chối { $call }. Bên kia ghi { $points } { $points ->
    [one] điểm
   *[other] điểm
} và ván bài kết thúc.
truco-desc-mazo = Bỏ bài của bạn. Nếu cả đội của bạn đều bỏ bài, bên kia thắng ván.
truco-trick-tie-neutral = Lượt { $trick } hòa.
