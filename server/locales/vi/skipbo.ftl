game-name-skipbo = Skip-Bo

skipbo-stock-mode-standard = Tiêu chuẩn (30 hoặc 20 lá)
skipbo-stock-mode-short = Nhanh 10 lá
skipbo-stock-mode-short-15 = Nhanh 15 lá
skipbo-scoring-single = Một ván
skipbo-scoring-match = Trận tính điểm

skipbo-set-stock-mode = Kho bài: { $mode }
skipbo-select-stock-mode = Chọn số lá trong kho bài:
skipbo-option-changed-stock-mode = Kho bài hiện dùng chế độ { $mode }.
skipbo-desc-stock-mode = Tiêu chuẩn dùng 30 lá cho 2 đến 4 người chơi và 20 lá cho 5 hoặc 6 người chơi. Ván nhanh dùng 10 hoặc 15 lá cho mỗi người.

skipbo-set-scoring-mode = Thể thức trận: { $mode }
skipbo-select-scoring-mode = Chọn thể thức trận:
skipbo-option-changed-scoring-mode = Thể thức trận hiện là { $mode }.
skipbo-desc-scoring-mode = Một ván kết thúc khi một người chơi hoặc một cặp đồng đội đánh hết kho bài. Trận tính điểm tiếp tục qua nhiều ván cho đến khi có bên đạt mốc điểm.

skipbo-set-winning-score = Mốc thắng trận: { $score } điểm
skipbo-enter-winning-score = Nhập mốc thắng trận từ 25 đến 5000 điểm:
skipbo-option-changed-winning-score = Mốc thắng trận hiện là { $score } điểm.
skipbo-desc-winning-score = Số điểm cần để thắng một trận tính điểm. Mốc chính thức là 500 điểm.
skipbo-desc-team-mode = Chế độ Cá nhân cho mỗi người một kho bài và điểm riêng. Chế độ đồng đội dùng các đội hai người; đồng đội có thể đánh từ kho bài và chồng bài bỏ của nhau, nhưng không được đánh bài trên tay của nhau.

skipbo-card-number = { $value }
skipbo-card-wild = Lá Skip-Bo vạn năng
skipbo-card-wild-as = Skip-Bo thay số { $value }

skipbo-source-your-hand = bài trên tay bạn
skipbo-source-player-hand = bài trên tay của { $owner }
skipbo-source-your-stock = kho bài của bạn
skipbo-source-player-stock = kho bài của { $owner }
skipbo-source-your-discard = chồng bài bỏ { $pile } của bạn
skipbo-source-player-discard = chồng bài bỏ { $pile } của { $owner }

skipbo-action-source-hand = bài trên tay
skipbo-action-source-stock = kho bài
skipbo-action-source-player-stock = kho bài của { $owner }
skipbo-action-source-discard = chồng bài bỏ { $pile }
skipbo-action-source-player-discard = chồng bài bỏ { $pile } của { $owner }

skipbo-play-action = { $card } — { $source } vào chồng bài xây { $pile }
skipbo-card-action = { $card } — { $source }
skipbo-card-desc-play-or-discard = Chồng bài xây có thể đánh: { $piles }. Chọn lá này để đánh, hoặc bỏ bài và kết thúc lượt.
skipbo-card-desc-discard-only = Chọn lá này để bỏ bài và kết thúc lượt.
skipbo-card-desc-choose-building = Chồng bài xây có thể đánh: { $piles }. Chọn lá này rồi chọn một chồng.
skipbo-end-turn-empty = Kết thúc lượt mà không bỏ bài
skipbo-end-turn-empty-desc = Bạn không có bài trên tay và cũng không còn lá nào để rút nên không thể bỏ bài.
skipbo-select-card-move = Chọn nơi chuyển lá bài này đến:
skipbo-move-building-empty = Chồng bài xây { $pile }: trống; đánh { $card }
skipbo-move-building-top = Chồng bài xây { $pile }: trên cùng là { $current }; đánh { $card }
skipbo-move-discard-empty = Chồng bài bỏ { $pile }: trống; bỏ vào đây và kết thúc lượt
skipbo-move-discard-top = Chồng bài bỏ { $pile }: trên cùng là { $top }; bỏ vào đây và kết thúc lượt

skipbo-read-building-piles = Xem các chồng bài xây
skipbo-read-stock-piles = Xem các kho bài
skipbo-read-own-discard-piles = Xem các chồng bài bỏ của bạn
skipbo-read-discard-piles = Xem các chồng bài bỏ của người khác
skipbo-select-discard-owner = Chọn người chơi để xem các chồng bài bỏ:
skipbo-game-start = Ván chơi bắt đầu. Mỗi kho bài có { $stock_count } lá.
skipbo-game-start-quick = Ván nhanh bắt đầu. Mỗi kho bài có { $stock_count } lá.
skipbo-match-game-start = Ván tính điểm thứ { $game } bắt đầu. Mỗi kho bài có { $stock_count } lá.
skipbo-match-game-start-quick = Ván tính điểm nhanh thứ { $game } bắt đầu. Mỗi kho bài có { $stock_count } lá.
skipbo-initial-stock-you = Lá ngửa trên kho bài của bạn là { $card }.
skipbo-initial-stock-player = Lá ngửa trên kho bài của { $player } là { $card }.
skipbo-draw-turn-you = Bạn rút { $count } { $count ->
    [one] lá
   *[other] lá
} để bắt đầu lượt. Bài trên tay bạn là { $hand }.
skipbo-draw-turn-player = { $player } rút { $count } { $count ->
    [one] lá
   *[other] lá
} để bắt đầu lượt của { GENDER_TERM($player_gender, "object") }.
skipbo-refill-you = Bạn đã đánh hết bài trên tay nên lập tức rút { $count } { $count ->
    [one] lá
   *[other] lá
}. Bài trên tay bạn là { $hand }.
skipbo-refill-player = { $player } đã đánh hết bài trên tay và lập tức rút { $count } { $count ->
    [one] lá
   *[other] lá
}.
skipbo-no-refill-you = Bạn không còn bài trên tay và cũng không còn lá nào để rút.
skipbo-no-refill-player = { $player } không còn bài trên tay, nhưng cũng không còn lá nào để rút.
skipbo-recycle-completed = Chồng bài rút đã hết. Các chồng bài xây hoàn tất được xáo lại thành chồng bài rút mới gồm { $count } lá.

skipbo-play-you = Bạn đánh { $card } từ { $source } vào chồng bài xây { $pile }.
skipbo-play-player = { $player } đánh { $card } từ { $source } vào chồng bài xây { $pile }.
skipbo-complete-building-you = Bạn hoàn tất chồng bài xây { $pile } ở số 12. Các lá được đặt sang một bên để xáo lại khi cần, và vị trí đó lại trống.
skipbo-complete-building-player = { $player } hoàn tất chồng bài xây { $pile } ở số 12. Các lá được đặt sang một bên để xáo lại khi cần, và vị trí đó lại trống.
skipbo-next-stock-you = Lá ngửa kế tiếp trên kho bài của bạn là { $card }; còn { $count } { $count ->
    [one] lá
   *[other] lá
}.
skipbo-next-stock-player = Lá ngửa kế tiếp trên kho bài của { $player } là { $card }; kho bài này còn { $count } { $count ->
    [one] lá
   *[other] lá
}.
skipbo-stock-cleared-you = Kho bài của bạn đã hết. Cặp đồng đội của bạn vẫn cần đánh hết kho còn lại.
skipbo-stock-cleared-player = Kho bài của { $player } đã hết. Cặp đồng đội vẫn cần đánh hết kho còn lại.
skipbo-discard-you = Bạn bỏ lá { $card } lên chồng bài bỏ { $pile } và kết thúc lượt.
skipbo-discard-player = { $player } bỏ lá { $card } lên chồng bài bỏ { $pile } và kết thúc lượt của { GENDER_TERM($player_gender, "object") }.
skipbo-empty-end-you = Bạn không có lá nào để bỏ nên kết thúc lượt mà không bỏ bài.
skipbo-empty-end-player = { $player } không có lá nào để bỏ và kết thúc lượt của { GENDER_TERM($player_gender, "object") } mà không bỏ bài.

skipbo-single-win-you = Bạn đánh hết kho bài và thắng ván chơi.
skipbo-single-win-player = { $player } đánh hết kho bài của { GENDER_TERM($player_gender, "object") } và thắng ván chơi.
skipbo-single-win-team-you = Cặp đồng đội của bạn đánh hết cả hai kho bài và thắng ván chơi.
skipbo-single-win-team = Đội { $team } đánh hết cả hai kho bài và thắng ván chơi.
skipbo-scored-game-win-you = Bạn đánh hết kho bài và thắng ván tính điểm thứ { $game }, nhận { $points } điểm khi các kho bài đối phương còn tổng cộng { $remaining } lá. Tổng điểm của bạn trong trận là { $total }.
skipbo-scored-game-win-player = { $player } đánh hết kho bài của { GENDER_TERM($player_gender, "object") } và thắng ván tính điểm thứ { $game }, nhận { $points } điểm khi các kho bài đối phương còn tổng cộng { $remaining } lá. Tổng điểm của { $player } trong trận là { $total }.
skipbo-scored-game-win-team-you = Cặp đồng đội của bạn đánh hết cả hai kho bài và thắng ván tính điểm thứ { $game }, nhận { $points } điểm khi kho bài của các đội đối phương còn tổng cộng { $remaining } lá. Tổng điểm của đội bạn trong trận là { $total }.
skipbo-scored-game-win-team = Đội { $team } đánh hết cả hai kho bài và thắng ván tính điểm thứ { $game }, nhận { $points } điểm khi kho bài của các đội đối phương còn tổng cộng { $remaining } lá. Tổng điểm của đội trong trận là { $total }.
skipbo-next-round = Ván tính điểm kế tiếp sẽ sớm bắt đầu. Vị trí bắt đầu chuyển sang ghế kế tiếp.
skipbo-match-win-you = Bạn thắng trận Skip-Bo với { $score } điểm.
skipbo-match-win-player = { $player } thắng trận Skip-Bo với { $score } điểm.
skipbo-match-win-team-you = Cặp đồng đội của bạn thắng trận Skip-Bo với { $score } điểm.
skipbo-match-win-team = Đội { $team } thắng trận Skip-Bo với { $score } điểm.

skipbo-building-empty = Chồng bài xây { $pile }: trống; cần số 1.
skipbo-building-top = Chồng bài xây { $pile }: trên cùng là { $value }; cần số { $needed }.
skipbo-draw-count = Chồng bài rút: { $draw_count } lá. Bài từ các chồng bài xây hoàn tất đang chờ xáo lại: { $recycle_count } lá.
skipbo-stock-empty = Kho bài của { $player }: trống.
skipbo-stock-status = Kho bài của { $player }: lá ngửa là { $card }, tổng cộng { $count } { $count ->
    [one] lá
   *[other] lá
}.
skipbo-discard-your-header = Các chồng bài bỏ của bạn:
skipbo-discard-player-header = Các chồng bài bỏ của { $player }:
skipbo-discard-empty = Chồng bài bỏ { $pile }: trống.
skipbo-discard-top = Chồng bài bỏ { $pile }: trên cùng là { $card }, tổng cộng { $count } { $count ->
    [one] lá
   *[other] lá
}.
skipbo-hand-empty = Bạn chưa có bài trên tay.
skipbo-hand-menu-card = Bài trên tay: { $card }

skipbo-error-invalid-stock-mode = Số lá trong kho bài không hợp lệ. Hãy chọn Tiêu chuẩn, Nhanh 10 lá hoặc Nhanh 15 lá.
skipbo-error-invalid-scoring-mode = Thể thức trận đã chọn không được hỗ trợ. Hãy chọn Một ván hoặc Trận tính điểm.
skipbo-error-winning-score-range = Mốc thắng trận phải nằm trong khoảng { $min } đến { $max } điểm; giá trị hiện tại là { $value }.
skipbo-error-partnership-player-count = Chế độ đồng đội cần đúng 4 người cho hai đội hoặc 6 người cho ba đội.
skipbo-error-game-not-active = Hiện không có ván Skip-Bo nào đang diễn ra.
skipbo-error-round-transition = Ván hiện tại đã kết thúc. Hãy chờ ván kế tiếp bắt đầu.
skipbo-error-card-move-selection-you = Hãy chọn nơi chuyển lá bài đã chọn trước.
skipbo-error-play-changed = Nước đánh đó không còn hợp lệ vì lá bài hoặc chồng bài xây đã thay đổi. Hãy chọn một hành động hiện có trong trình đơn lượt.
skipbo-error-card-changed = Lá đó không còn dùng được. Hãy chọn một hành động hiện có trong trình đơn lượt.
skipbo-error-cards-available = Bạn vẫn còn lá có thể bỏ. Hãy chọn lá đó và một trong bốn chồng bài bỏ để kết thúc lượt.
skipbo-error-no-discard-targets = Hiện không có người chơi nào khác để xem các chồng bài bỏ.
skipbo-error-discard-target-changed = Không còn xem được các chồng bài bỏ của người chơi đó. Hãy chọn một người đang tham gia.
skipbo-discard-owner-unavailable = Người chơi này không còn ở bàn

skipbo-result-line = { $rank }. { $player }: { $points }
