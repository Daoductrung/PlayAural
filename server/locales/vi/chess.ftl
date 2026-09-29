game-name-chess = Cờ vua

chess-set-time-control = Kiểm soát thời gian: { $control }
chess-select-time-control = Chọn kiểu thời gian
chess-option-changed-time-control = Đã đổi kiểu thời gian thành { $control }.
chess-desc-time-control = Chọn đồng hồ cờ vua, từ không tính giờ đến bullet, blitz, rapid hoặc classical.
chess-time-untimed = Không giới hạn
chess-time-bullet-1-0 = Bullet 1+0
chess-time-bullet-2-1 = Bullet 2+1
chess-time-blitz-3-0 = Blitz 3+0
chess-time-blitz-3-2 = Blitz 3+2
chess-time-blitz-5-0 = Blitz 5+0
chess-time-rapid-10-0 = Rapid 10+0
chess-time-rapid-10-5 = Rapid 10+5
chess-time-classical-30-0 = Classical 30+0

chess-set-draw-handling = Xử lý cờ hòa: { $mode }
chess-select-draw-handling = Chọn cách xử lý cờ hòa
chess-option-changed-draw-handling = Đã đổi cách xử lý cờ hòa thành { $mode }.
chess-desc-draw-handling = Chọn luật hòa tự động kết thúc ván ngay hay cần người chơi yêu cầu hòa.
chess-draw-handling-automatic = Tự động
chess-draw-handling-claim-required = Phải yêu cầu

chess-toggle-draw-offers = Cho phép đề nghị cờ hòa: { $enabled }
chess-option-changed-draw-offers = Cho phép đề nghị cờ hòa: { $enabled }.
chess-desc-allow-draw-offers = Quy định người chơi có thể đề nghị hòa và phản hồi đề nghị hòa hay không.
chess-toggle-undo-requests = Cho phép xin đi lại: { $enabled }
chess-option-changed-undo-requests = Cho phép xin đi lại: { $enabled }.
chess-desc-allow-undo-requests = Quy định người chơi có thể xin đi lại để đối thủ chấp nhận hoặc từ chối hay không.
chess-error-invalid-time-control = Kiểu thời gian "{ $control }" không được hỗ trợ trong Cờ vua.
chess-error-invalid-draw-handling = Cách xử lý cờ hòa "{ $mode }" không được hỗ trợ trong Cờ vua.

chess-read-board = Đọc bàn cờ
chess-check-status = Xem tình trạng
chess-flip-board = Lật bàn cờ
chess-check-clock = Xem đồng hồ
chess-claim-draw = Yêu cầu cờ hòa
chess-offer-draw = Đề nghị cờ hòa
chess-accept-draw = Chấp nhận cờ hòa
chess-decline-draw = Từ chối cờ hòa
chess-request-undo = Xin đi lại
chess-accept-undo = Chấp nhận đi lại
chess-decline-undo = Từ chối đi lại
chess-type-move = Nhập nước cờ
chess-enter-move = Nhập nước cờ, ví dụ e2e4, Nf3, O-O, hoặc e8=Q

chess-promote-queen = Phong hậu
chess-promote-rook = Phong xe
chess-promote-bishop = Phong tượng
chess-promote-knight = Phong mã

chess-color-white = trắng
chess-color-black = đen

chess-piece-pawn = tốt
chess-piece-knight = mã
chess-piece-bishop = tượng
chess-piece-rook = xe
chess-piece-queen = hậu
chess-piece-king = vua
chess-piece-with-color = { $piece } { $color }

chess-square-empty-label = { $square }, trống
chess-square-piece-label = { $square }, { $piece }
chess-square-selected-label = đang chọn, { $label }
chess-square-move-target = { $square }, nước đi hợp lệ
chess-square-capture-target = { $square }, có thể ăn { $piece }
chess-square-empty = { $square } đang trống.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = Hãy chọn một quân của bạn trước.
chess-piece-no-legal-moves = Quân này không có nước đi hợp lệ.
chess-piece-selected = Đã chọn { $piece } ở { $square }. Có { $count } nước đi hợp lệ.
chess-selection-cleared = Đã bỏ chọn.
chess-illegal-move = Nước đi không hợp lệ.
chess-invalid-castle = Không thể nhập thành ở đó.
chess-promotion-pending = Hãy chọn quân phong cấp trước.
chess-choose-promotion = Hãy chọn quân để phong cấp.
chess-typed-move-empty = Hãy nhập một nước cờ trước khi gửi.
chess-typed-move-parse-error = Không hiểu "{ $move }" là nước cờ nào. Hãy thử dạng tọa độ như e2e4, ký pháp như Nf3, nhập thành như O-O, hoặc phong cấp như e8=Q.
chess-typed-move-ambiguous = "{ $move }" khớp với nhiều nước hợp lệ. Hãy thêm cột, hàng, hoặc ô xuất phát, ví dụ Nbd2 hoặc Rae1.
chess-typed-move-illegal = "{ $move }" không hợp lệ trong thế cờ hiện tại.
chess-typed-move-bad-promotion = "{ $move }" có quân phong cấp, nhưng chỉ có thể phong cấp khi tốt của bạn tới hàng cuối. Hãy dùng hậu, xe, tượng, hoặc mã.

chess-game-started = Ván cờ bắt đầu. { $white } đi quân trắng. { $black } đi quân đen.
chess-you-win-checkmate = Chiếu hết. Bạn thắng.
chess-player-wins-checkmate = Chiếu hết. { $player } thắng.
chess-draw = Cờ hòa.
chess-draw-stalemate = Cờ hòa do bí hòa.
chess-draw-fifty-move = Cờ hòa theo Luật 50 nước.
chess-draw-seventy-five-move = Cờ hòa bắt buộc theo Luật 75 nước.
chess-draw-threefold = Cờ hòa do thế cờ lặp lại ba lần.
chess-draw-fivefold = Cờ hòa bắt buộc do thế cờ lặp lại năm lần.
chess-draw-insufficient-material = Cờ hòa vì không đủ quân để chiếu hết.
chess-draw-agreement = Cờ hòa do hai bên thỏa thuận.
chess-draw-timeout-insufficient = Cờ hòa. Đối phương hết giờ nhưng không đủ quân để chiếu hết.
chess-you-are-in-check = Vua của bạn đang bị chiếu.
chess-player-is-in-check = Vua của { $player } đang bị chiếu.
chess-you-lose-on-time = Bạn hết giờ. { $winner } thắng ván cờ.
chess-player-loses-on-time = { $player } hết giờ. { $winner } thắng ván cờ.

chess-you-en-passant = Bạn đi { $piece } từ { $from_square } đến { $to_square } và bắt tốt qua đường.
chess-player-en-passant = { $player } đi { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } từ { $from_square } đến { $to_square } và bắt tốt qua đường.
chess-you-en-passant-brief = Bạn { $from_square } x { $to_square } qua đường.
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } qua đường.
chess-you-capture = Bạn đi { $piece } từ { $from_square } đến { $to_square }, ăn { $captured_piece }.
chess-player-captures = { $player } đi { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } từ { $from_square } đến { $to_square }, ăn { $captured_piece }.
chess-you-capture-brief = Bạn { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = Bạn nhập thành cánh vua.
chess-player-castles-kingside = { $player } nhập thành cánh vua.
chess-you-castle-kingside-brief = Bạn O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = Bạn nhập thành cánh hậu.
chess-player-castles-queenside = { $player } nhập thành cánh hậu.
chess-you-castle-queenside-brief = Bạn O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = Bạn đi { $piece } từ { $from_square } đến { $to_square }.
chess-player-moves = { $player } đi { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } từ { $from_square } đến { $to_square }.
chess-you-move-brief = Bạn { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = Bạn phong cấp ở { $square }.
chess-player-promotes = { $player } phong cấp ở { $square }.
chess-you-promote-to = Bạn phong tốt ở { $square } thành { $piece }.
chess-player-promotes-to = { $player } phong tốt ở { $square } thành { $piece }.
chess-you-promote-to-brief = Bạn phong { $square } thành { $piece }.
chess-player-promotes-to-brief = { $player } phong { $square } thành { $piece }.
chess-you-offer-draw = Bạn đề nghị cờ hòa.
chess-player-offers-draw = { $player } đề nghị cờ hòa.
chess-you-accept-draw = Bạn chấp nhận cờ hòa.
chess-player-accepts-draw = { $player } chấp nhận cờ hòa.
chess-you-decline-draw = Bạn từ chối cờ hòa.
chess-player-declines-draw = { $player } từ chối cờ hòa.
chess-you-request-undo = Bạn xin đi lại.
chess-player-requests-undo = { $player } xin đi lại.
chess-you-accept-undo = Bạn chấp nhận đi lại.
chess-player-accepts-undo = { $player } chấp nhận đi lại.
chess-you-decline-undo = Bạn từ chối đi lại.
chess-player-declines-undo = { $player } từ chối đi lại.
chess-draw-offer-too-early = Chỉ có thể đề nghị cờ hòa sau khi cả hai bên đều đã đi ít nhất một nước.
chess-claim-available-fifty-move = Hiện giờ có thể yêu cầu cờ hòa theo Luật 50 nước.
chess-claim-available-threefold = Hiện giờ có thể yêu cầu cờ hòa do thế cờ lặp lại ba lần.
chess-you-claim-draw-fifty-move = Bạn yêu cầu cờ hòa theo Luật 50 nước.
chess-draw-claimed-fifty-move = { $player } yêu cầu cờ hòa theo Luật 50 nước.
chess-you-claim-draw-threefold = Bạn yêu cầu cờ hòa do thế cờ lặp lại ba lần.
chess-draw-claimed-threefold = { $player } yêu cầu cờ hòa do thế cờ lặp lại ba lần.

chess-status-white = Trắng: { $player }
chess-status-black = Đen: { $player }
chess-status-turn = Lượt đi: { $color } ({ $player })
chess-status-move-count = Số nước trọn vẹn: { $count }. Số lượt quân đã đi: { $plies }.
chess-status-promotion-pending = Đang chờ chọn quân phong cấp.
chess-status-check = Bên sắp đi đang bị chiếu tướng.
chess-status-time-control = Kiểm soát thời gian: { $control }
chess-status-draw-offer = Đang chờ phản hồi đề nghị cờ hòa từ { $player }.
chess-status-undo-request = Đang chờ phản hồi xin đi lại từ { $player }.
chess-clock-line = Đồng hồ { $color }: { $time }
chess-clock-untimed = không giới hạn
chess-clock-announcement = Trắng còn { $white }. Đen còn { $black }.
chess-clock-announcement-untimed = Ván cờ này không giới hạn thời gian.

chess-board-flipped = Đã lật bàn cờ theo phía { $color }.
chess-empty = trống
chess-board-rank-line = Hàng { $rank }: { $pieces }

chess-end-winner = { $player } thắng với quân { $color }.
chess-end-move-count = Số nước trọn vẹn: { $count }. Số lượt quân đã đi: { $plies }.
