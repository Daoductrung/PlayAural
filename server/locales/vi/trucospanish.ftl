# Tùy chọn
trucospanish-length-18 = 18 điểm mỗi came
trucospanish-length-24 = 24 điểm mỗi came
trucospanish-set-length = Độ dài came: { $mode }
trucospanish-select-length = Chọn độ dài came:
trucospanish-option-changed-length = Độ dài came hiện là { $mode }.
trucospanish-desc-length = Thắng hai came là thắng ván chơi. Mỗi came được chơi đến số điểm đã chọn: 24 như ở giải vô địch Falles của València và giải đấu của Universitat Politècnica de València, hoặc 18 như ở giải đấu Torrent và mô tả của Museu d'Història de València. Khi một bên đạt số điểm đó, bên ấy thắng came và cả hai bảng điểm trở về không. La falta trị giá số điểm mà bên đang dẫn đầu còn cần để kết thúc came, và Joc fora thắng cả ván chơi.
trucospanish-desc-team-mode = Individual là ván một đấu một cho 2 người chơi. 2v2 dùng 4 người chơi; đồng đội chia sẻ điểm và có thể gọi thay cho cả đội.

# Lời gọi
trucospanish-call-truc = Truc
trucospanish-call-retruc = Retruc
trucospanish-call-quatre-val = Quatre val
trucospanish-call-joc-fora = Joc fora
trucospanish-call-envit = Envit
trucospanish-call-torna = Torna
trucospanish-call-la-falta = La falta

# Hành động và thông báo
trucospanish-action-accept = Vull (chấp nhận)
trucospanish-action-decline = No vull (từ chối)
trucospanish-action-mazo = Me'n vaig (bỏ ván này)
trucospanish-accept-you = Bạn nói Vull với { $call }.
trucospanish-accept-player = { $player } nói Vull với { $call }.
trucospanish-decline-you = Bạn nói No vull với { $call }.
trucospanish-decline-player = { $player } nói No vull với { $call }.
trucospanish-mazo-you = Bạn nói Me'n vaig và bỏ ván này thay cho cả đội.
trucospanish-mazo-player = { $player } nói Me'n vaig và bỏ ván này thay cho cả đội.
trucospanish-reason-truc = Truc
trucospanish-reason-envit = Envit
trucospanish-game-start = Truco Tây Ban Nha bắt đầu. Thắng hai came, mỗi came { $points } điểm, để thắng ván chơi.
trucospanish-desc-mazo = Bỏ ván này thay cho cả đội. Bên kia ghi giá trị hiện tại của ván.
trucospanish-came-you = Bạn thắng một came! Bạn có { $cames } { $cames ->
    [one] came
   *[other] came
}. Bảng điểm trở về không.
trucospanish-came-player = { $player } thắng một came và có { $cames } { $cames ->
    [one] came
   *[other] came
}. Bảng điểm trở về không.
trucospanish-came-your-team = Đội của bạn thắng một came! Đội bạn có { $cames } { $cames ->
    [one] came
   *[other] came
}. Bảng điểm trở về không.
trucospanish-came-team = { $team } thắng một came và có { $cames } { $cames ->
    [one] came
   *[other] came
}. Bảng điểm trở về không.

trucospanish-pending-answer = { $player } đã gọi { $call }. Hãy trả lời bằng Vull hoặc No vull, hoặc tăng mức cược.
trucospanish-error-answer-first = Bạn phải trả lời { $call } trước khi làm việc khác. Hãy chọn Vull hoặc No vull, hoặc tăng mức cược.
trucospanish-error-raise-max = Joc fora đã là tiếng gọi cao nhất và không thể tăng thêm.
trucospanish-error-bad-count = Truco Tây Ban Nha cần 2 hoặc 4 người chơi, nhưng hiện có { $count }.
trucospanish-error-team-mode-count = Chế độ đội { $mode } không dùng được với { $count } người chơi. Hãy dùng Individual cho 2 người chơi hoặc 2v2 cho 4 người chơi.
trucospanish-status-envit-open = Vẫn có thể gọi envit trong ván này.
trucospanish-status-envit-closed = Envit đã đóng trong ván này.
trucospanish-status-no-truc = Chưa có Truc nào được gọi. Ván bài đáng { $points } { $points ->
    [one] điểm
   *[other] điểm
}.
trucospanish-falta-value = La falta đáng { $points } { $points ->
    [one] điểm
   *[other] điểm
}.
trucospanish-reveal-envit-you = Envit đã thắng với các lá của bạn: { $cards }, đáng { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
trucospanish-reveal-envit-player = { $player } thắng envit với { $cards }, đáng { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
trucospanish-error-envit-late = Chỉ có thể gọi envit trước khi bạn đánh lá đầu tiên.
trucospanish-error-envit-closed = Envit đã đóng vì Truc đã được chấp nhận.
trucospanish-error-envit-done = Envit đã được chơi trong ván này.
trucospanish-error-envit-cannot-raise = Không thể thêm { $call } vào envit đang chơi.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] điểm
   *[other] điểm
} trong came này, đã thắng { $cames } { $cames ->
    [one] came
   *[other] came
}
trucospanish-game-win-you = Bạn thắng ván chơi với { $cames } { $cames ->
    [one] came
   *[other] came
}!
trucospanish-game-win-player = { $player } thắng ván chơi với { $cames } { $cames ->
    [one] came
   *[other] came
}.
trucospanish-game-win-your-team = Đội của bạn thắng ván chơi với { $cames } { $cames ->
    [one] came
   *[other] came
}!
trucospanish-game-win-team = { $team } thắng ván chơi với { $cames } { $cames ->
    [one] came
   *[other] came
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] came
   *[other] came
}
trucospanish-cames-line = { $team }: đã thắng { $cames } { $cames ->
    [one] came
   *[other] came
}
