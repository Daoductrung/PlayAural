game-name-tossup = Toss Up

tossup-roll-first = Gieo { $count } viên xúc xắc
tossup-roll-remaining = Gieo { $count } viên xúc xắc còn lại
tossup-bank = Chốt { $points } điểm
tossup-check-turn-status = Kiểm tra lượt hiện tại

tossup-game-start = Toss Up bắt đầu với luật { $rules }, mỗi bộ có { $dice } viên xúc xắc và mốc điểm { $target }. Hãy vượt mốc rồi chờ các lượt còn lại kết thúc để giành chiến thắng.
tossup-game-start-brief = Toss Up bắt đầu. Hãy vượt { $target } điểm.
tossup-round-start = Vòng { $round } bắt đầu.
tossup-round-start-brief = Vòng { $round }.

tossup-your-turn = Đến lượt bạn. Bạn đã chốt { $score } điểm; hãy gieo { $dice } viên xúc xắc để bắt đầu.
tossup-player-turn = Đến lượt { $player }, đang có { $score } điểm đã chốt và { $dice } viên xúc xắc.
tossup-your-turn-brief = Lượt bạn: { $score } điểm.
tossup-player-turn-brief = Lượt { $player }: { $score } điểm.

tossup-you-roll = Bạn gieo được { $results }.
tossup-player-rolls = { $player } gieo được { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] Bạn: { $results }; điểm lượt { $turn_points }; nhận bộ mới { $dice_count } viên.
       *[no] Bạn: { $results }; điểm lượt { $turn_points }; còn { $dice_count } viên.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; điểm lượt { $turn_points }; nhận bộ mới { $dice_count } viên.
       *[no] { $player }: { $results }; điểm lượt { $turn_points }; còn { $dice_count } viên.
    }

tossup-result-green = { $count } mặt xanh
tossup-result-yellow = { $count } mặt vàng
tossup-result-red = { $count } mặt đỏ

tossup-you-have-points = Bạn để riêng { $gained } viên mặt xanh. Điểm lượt hiện tại là { $turn_points }, còn { $dice_count } viên xúc xắc.
tossup-player-has-points = { $player } để riêng { $gained } viên mặt xanh, có { $turn_points } điểm lượt và còn { $dice_count } viên xúc xắc.

tossup-you-get-fresh = Tất cả xúc xắc đều ra mặt xanh. Bạn nhận bộ mới gồm { $count } viên và có thể gieo tiếp hoặc chốt điểm.
tossup-player-gets-fresh = Tất cả xúc xắc đều ra mặt xanh. { $player } nhận bộ mới gồm { $count } viên.

tossup-you-bust =
    { $variant ->
        [Standard] Dính đèn đỏ: bạn không gieo được mặt xanh nào nhưng có ít nhất một mặt đỏ. Lượt kết thúc và bạn mất { $points } điểm chưa chốt.
       *[PlayAural] Tất cả xúc xắc vừa gieo đều ra mặt đỏ. Lượt kết thúc và bạn mất { $points } điểm chưa chốt.
    }
tossup-player-busts =
    { $variant ->
        [Standard] Dính đèn đỏ: { $player } không gieo được mặt xanh nào nhưng có ít nhất một mặt đỏ, nên lượt kết thúc và mất { $points } điểm chưa chốt.
       *[PlayAural] Tất cả xúc xắc của { $player } đều ra mặt đỏ, nên lượt kết thúc và mất { $points } điểm chưa chốt.
    }
tossup-you-bust-brief = Bạn: { $results }; mất trắng; mất { $points } điểm.
tossup-player-busts-brief = { $player }: { $results }; mất trắng; mất { $points } điểm.

tossup-you-bank = Bạn chốt { $points } điểm, nâng tổng điểm lên { $total }.
tossup-player-banks = { $player } chốt { $points } điểm, nâng tổng điểm { GENDER_TERM($player_gender, "possessive-determiner") } lên { $total }.
tossup-you-bank-brief = Bạn chốt { $points }; tổng { $total }.
tossup-player-banks-brief = { $player } chốt { $points }; tổng { $total }.

tossup-you-trigger-final-turns = Bạn vượt mốc { $target } với { $score } điểm. { $count } người còn lại, mỗi người được chơi một lượt cuối.
tossup-player-triggers-final-turns = { $player } vượt mốc { $target } với { $score } điểm. { $count } người còn lại, mỗi người được chơi một lượt cuối.
tossup-you-trigger-final-turns-brief = Bạn đặt điểm cần vượt ở { $score }; còn { $count } lượt.
tossup-player-triggers-final-turns-brief = { $player } đặt điểm cần vượt ở { $score }; còn { $count } lượt.

tossup-you-win = Bạn thắng Toss Up với { $score } điểm.
tossup-winner = { $player } thắng Toss Up với { $score } điểm.
tossup-you-win-brief = Bạn thắng: { $score }.
tossup-winner-brief = { $player } thắng: { $score }.
tossup-tie-tiebreaker = { $players } đang hòa ở điểm cao nhất trên mốc. Chỉ những người này tiếp tục vào vòng phân định.
tossup-tie-tiebreaker-brief = Phân định: { $players }.
tossup-tiebreaker-round-start = Vòng phân định { $round } bắt đầu cho { $players }.
tossup-tiebreaker-round-start-brief = Vòng phân định { $round }: { $players }.

tossup-your-turn-awaiting-roll = Bạn chưa gieo trong lượt này. Bạn có { $score } điểm đã chốt và { $dice_count } viên xúc xắc sẵn sàng.
tossup-player-turn-awaiting-roll = { $player } chưa gieo trong lượt này. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $score } điểm đã chốt và { $dice_count } viên xúc xắc sẵn sàng.
tossup-your-turn-status = Lần gieo gần nhất của bạn là { $results }. Bạn có { $turn_points } điểm lượt chưa chốt, { $score } điểm đã chốt và { $dice_count } viên sẵn sàng gieo.
tossup-player-turn-status = Lần gieo gần nhất của { $player } là { $results }. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $turn_points } điểm lượt chưa chốt, { $score } điểm đã chốt và { $dice_count } viên sẵn sàng gieo.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] Nếu chốt ngay, bạn sẽ dẫn đầu với { $total } điểm và đã vượt mốc { $target }.
       *[no] Bạn đang có { $points } điểm lượt chưa chốt.
    }
    Gieo { $dice } viên có khoảng { $risk } phần trăm nguy cơ mất trắng. Nhấn Gieo lần nữa trong vòng { $seconds } giây để xác nhận, hoặc chốt điểm để bảo toàn số điểm này.

tossup-set-rules-variant = Luật chơi: { $variant }
tossup-select-rules-variant = Chọn cách phân bố màu và điều kiện mất trắng:
tossup-option-changed-rules = Đã đổi luật chơi thành { $variant }.
tossup-desc-rules-variant = Luật Cổ điển có ba mặt xanh, hai mặt vàng và một mặt đỏ trên mỗi viên; nếu không có mặt xanh nhưng có ít nhất một mặt đỏ thì mất trắng. Luật Dễ thở chia đều cơ hội cho ba màu và chỉ mất trắng khi tất cả đều ra mặt đỏ.

tossup-desc-target-score = Trò chơi bước vào các lượt cuối sau khi có người chốt điểm vượt mốc này (mặc định 100, phạm vi 20-500).
tossup-set-starting-dice = Số xúc xắc mỗi bộ: { $count }
tossup-enter-starting-dice = Nhập số viên xúc xắc trong mỗi bộ mới:
tossup-option-changed-dice = Đã đổi số xúc xắc mỗi bộ thành { $count }.
tossup-desc-starting-dice = Chọn số viên khi bắt đầu mỗi lượt và khi nhận bộ mới sau lúc mọi viên đều ra mặt xanh (mặc định 10, phạm vi 5-20).


tossup-rules-standard = Cổ điển
tossup-rules-PlayAural = Dễ thở
tossup-rules-standard-desc = Ba mặt xanh, hai mặt vàng và một mặt đỏ. Mất trắng nếu không có mặt xanh nhưng có ít nhất một mặt đỏ.
tossup-rules-PlayAural-desc = Ba màu có cơ hội bằng nhau. Chỉ mất trắng khi mọi viên vừa gieo đều ra mặt đỏ.

tossup-error-roll-not-playing = Bạn không thể gieo vì ván Toss Up hiện chưa diễn ra.
tossup-error-roll-no-turn = Bạn không thể gieo vì hiện chưa có lượt Toss Up nào đang hoạt động.
tossup-error-roll-not-your-turn = Bạn không thể gieo trong lượt của { $player }. Hãy chờ đến lượt mình.
tossup-error-bank-not-playing = Bạn không thể chốt điểm vì ván Toss Up hiện chưa diễn ra.
tossup-error-bank-no-turn = Bạn không thể chốt điểm vì hiện chưa có lượt Toss Up nào đang hoạt động.
tossup-error-bank-not-your-turn = Bạn không thể chốt điểm trong lượt của { $player }. Hãy chờ đến lượt mình.
tossup-error-bank-roll-first = Hãy gieo ít nhất một lần trước khi chốt điểm. Nếu gieo toàn mặt vàng, bạn có thể chốt 0 điểm để kết thúc lượt.
tossup-error-spectator-action = Khán giả có thể kiểm tra trạng thái công khai của Toss Up, nhưng không thể gieo hoặc chốt điểm.
tossup-error-status-not-playing = Chưa thể kiểm tra lượt vì ván Toss Up hiện chưa diễn ra.
tossup-error-status-no-turn = Chưa thể kiểm tra lượt vì Toss Up hiện không có người chơi nào đang tới lượt.
tossup-error-target-out-of-range = Mốc điểm đang là { $value }; giá trị phải từ { $min } đến { $max } điểm.
tossup-error-dice-out-of-range = Số xúc xắc mỗi bộ đang là { $value }; giá trị phải từ { $min } đến { $max } viên.
tossup-error-rules-variant = Giá trị luật “{ $variant }” không được hỗ trợ. Hãy chọn Cổ điển hoặc Dễ thở.

tossup-line-format = { $rank }. { $player }: { $points }
