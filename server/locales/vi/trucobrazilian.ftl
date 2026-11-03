# Tùy chọn
trucobrazilian-desc-team-mode = Individual là ván một đấu một cho 2 người chơi. 2v2 dùng 4 người chơi và 3v3 dùng 6 người chơi; đồng đội chia sẻ điểm và có thể gọi thay cho cả đội.

# Bộ bài Pháp
trucobrazilian-rank-ace = Át
trucobrazilian-rank-jack = J
trucobrazilian-rank-queen = Q
trucobrazilian-rank-king = K
trucobrazilian-suit-diamonds = rô
trucobrazilian-suit-spades = bích
trucobrazilian-suit-hearts = cơ
trucobrazilian-suit-clubs = chuồn
trucobrazilian-card-name = { $rank } { $suit }

# Lời gọi
trucobrazilian-call-truco = Truco
trucobrazilian-call-seis = Seis
trucobrazilian-call-nove = Nove
trucobrazilian-call-doze = Doze
trucobrazilian-call-onze = Mão de onze

# Hành động và thông tin
trucobrazilian-action-onze-play = Jogar (chơi ván này)
trucobrazilian-action-onze-run = Correr (chạy và bỏ ván này)
trucobrazilian-read-vira = Đọc lá vira và manilha
trucobrazilian-no-vira = Chưa có lá vira nào được lật.
trucobrazilian-vira = Lá vira là { $card }. Manilha là { $manilha }.
trucobrazilian-vira-is = Lá vira là { $card }. Manilha là { $manilha }.

# Diễn biến ván chơi
trucobrazilian-game-start = Truco Brazil bắt đầu. Bên nào đạt { $points } điểm trước sẽ thắng. Mỗi ván, một lá bài được lật gọi là vira quyết định các manilha.
trucobrazilian-onze-your-team = Đội của bạn có 11 điểm: mão de onze. Chọn Jogar để chơi ván này với 3 điểm và không được gọi, hoặc Correr để tặng bên kia 1 điểm.
trucobrazilian-onze-team = { $team } có 11 điểm và đang quyết định có chơi mão de onze hay không.
trucobrazilian-onze-play-you = Bạn chơi mão de onze. Ván này đáng 3 điểm và không được gọi.
trucobrazilian-onze-play-player = { $player } chơi mão de onze. Ván này đáng 3 điểm và không được gọi.
trucobrazilian-onze-run-you = Bạn chạy. Bên kia ghi 1 điểm.
trucobrazilian-onze-run-player = { $player } chạy. Bên kia ghi 1 điểm.
trucobrazilian-ferro = Cả hai bên đều có 11 điểm: mão de ferro. Không được gọi và ai thắng ván này sẽ thắng cả trận.
trucobrazilian-reason-onze-run = việc chạy trong mão de onze
trucobrazilian-hand-annulled = Cả ba lượt đều hòa. Ván bài bị hủy và không ai ghi điểm.

# Lỗi và mô tả
trucobrazilian-error-onze-pending = { $team } phải quyết định trước có chơi mão de onze hay không.
trucobrazilian-error-no-calls = Ván này không được gọi vì đây là mão de onze hoặc mão de ferro.
trucobrazilian-desc-onze-play = Chơi ván này. Ván đáng { $points } { $points ->
    [one] điểm
   *[other] điểm
} và không được gọi.
trucobrazilian-desc-onze-run = Chạy và bỏ ván này. Bên kia ghi 1 điểm.

trucobrazilian-action-accept = Aceito (chấp nhận)
trucobrazilian-action-decline = Correr (từ chối và chạy)
trucobrazilian-accept-you = Bạn nói Aceito với { $call }.
trucobrazilian-accept-player = { $player } nói Aceito với { $call }.
trucobrazilian-decline-you = Bạn chạy khỏi { $call }.
trucobrazilian-decline-player = { $player } chạy khỏi { $call }.
trucobrazilian-pending-answer = { $player } đã gọi { $call }. Hãy trả lời bằng Aceito hoặc Correr, hoặc tăng mức cược.
trucobrazilian-error-answer-first = Bạn phải trả lời { $call } trước khi làm việc khác. Hãy chọn Aceito hoặc Correr, hoặc tăng mức cược.
trucobrazilian-error-raise-max = Doze đã là tiếng gọi cao nhất và không thể tăng thêm.
trucobrazilian-status-onze-pending = { $team } phải quyết định có chơi mão de onze hay không.
trucobrazilian-status-no-calls = Ván này không được gọi. Ván bài đáng { $points } { $points ->
    [one] điểm
   *[other] điểm
}.

# Mão de ferro (cả hai bên đều 11) chơi với bài úp; ở mão de onze, đồng đội xem được bài của nhau
trucobrazilian-blind-cards = Mão de ferro: { $count } lá bài của bạn đang úp và bạn không thể nhìn thấy. Hãy chọn theo vị trí; mỗi lá được lật khi đánh ra.
trucobrazilian-blind-hand = Mão de ferro: bạn có { $count } { $count ->
    [one] lá bài
   *[other] lá bài
} úp và không thể nhìn thấy.
trucobrazilian-action-play-blind = Đánh lá bài úp số { $number }
trucobrazilian-desc-blind-card = Một lá bài úp. Bạn sẽ không thấy nó cho đến khi nó được đánh ra.
trucobrazilian-onze-partner-cards = Đồng đội { $partner } cho bạn xem bài của họ: { $cards }.
