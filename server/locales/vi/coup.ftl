# Thông báo trò chơi Đảo Chính
# Note: Common messages like round-start, turn-start are in games.ftl

game-name-coup = Đảo Chính

coup-action-income = Thu nhập (cộng 1 xu)
coup-action-foreign-aid = Viện trợ nước ngoài (cộng 2 xu)
coup-action-coup = Đảo chính (tốn 7 xu)
coup-action-tax = Thu thuế (Tướng quân, cộng 3 xu)
coup-action-assassinate = Ám sát (Sát thủ, tốn 3 xu)
coup-action-steal = Trộm xu (Đô đốc, cộng 2 xu)
coup-action-exchange = Trao đổi bài (Sứ giả)

coup-action-challenge = Thách thức!
coup-action-block = Chặn!
coup-action-pass = Bỏ qua

coup-action-lose-influence = Mất lá bài
coup-action-return-card = Trả lại lá bài

coup-card-duke = Tướng quân
coup-card-assassin = Sát thủ
coup-card-captain = Đô đốc
coup-card-ambassador = Sứ giả
coup-card-contessa = Nữ bá tước

coup-return-card-format = Trả lại lá { $card }
coup-return-card-exchanged-format = Đã trao đổi: { $card }
coup-card-already-exchanged = Lá bài này đã được trao đổi rồi.

coup-select-target = Chọn mục tiêu:
coup-must-coup = Bạn đang có từ 10 xu trở lên và bắt buộc phải Đảo chính!
coup-target-invalid = { $target } không phải mục tiêu còn sống hợp lệ.
coup-cannot-challenge-action = Bạn không thể thách thức hành động này.
coup-cannot-block-now = Bạn không thể chặn vào lúc này.
coup-only-target-can-block = Chỉ mục tiêu của hành động mới có thể chặn.
coup-cannot-block-action = Hành động này không thể bị chặn.
coup-no-active-claim = Không có tuyên bố nào đang diễn ra để thách thức.

coup-you-take-income = Bạn nhận Thu nhập.
coup-takes-income = { $player } nhận Thu nhập.
coup-you-claim-foreign-aid = Bạn yêu cầu Viện trợ nước ngoài.
coup-claims-foreign-aid = { $player } yêu cầu Viện trợ nước ngoài.
coup-you-take-foreign-aid = Bạn nhận Viện trợ nước ngoài và lấy 2 xu.
coup-takes-foreign-aid = { $player } đã nhận Viện trợ nước ngoài.
coup-you-play-coup = Bạn tiến hành Đảo chính nhắm vào { $target }!
coup-coup-targets-you = { $player } tiến hành Đảo chính nhắm vào bạn!
coup-plays-coup = { $player } tiến hành Đảo chính nhắm vào { $target }!
coup-you-claim-tax = Bạn tuyên bố mình là Tướng quân và yêu cầu Thu thuế.
coup-claims-tax = { $player } tuyên bố là Tướng quân và yêu cầu Thu thuế.
coup-you-take-tax = Bạn thu thuế và lấy 3 xu.
coup-takes-tax = { $player } đã thu thuế.
coup-you-claim-assassinate = Bạn tuyên bố mình là Sát thủ và nhắm vào { $target }.
coup-assassination-claimed-against-you = { $player } tuyên bố là Sát thủ và nhắm vào bạn.
coup-claims-assassinate = { $player } tuyên bố là Sát thủ và nhắm vào { $target }.
coup-you-assassinate = Cuộc Ám sát của bạn nhắm vào { $target } được thực hiện.
coup-you-are-assassinated = Cuộc Ám sát của { $player } nhắm vào bạn được thực hiện.
coup-assassinates = { $player } ám sát { $target }.
coup-you-claim-steal = Bạn tuyên bố mình là Đô đốc và cố trộm 2 xu từ { $target }.
coup-steal-claimed-against-you = { $player } tuyên bố là Đô đốc và cố trộm 2 xu từ bạn.
coup-claims-steal = { $player } tuyên bố là Đô đốc và cố trộm 2 xu từ { $target }.
coup-you-steal = Bạn trộm { $amount } xu từ { $target }.
coup-you-are-stolen-from = { $player } trộm { $amount } xu từ bạn.
coup-steals = { $player } trộm { $amount } xu từ { $target }.
coup-you-claim-exchange = Bạn tuyên bố mình là Sứ giả để trao đổi bài.
coup-claims-exchange = { $player } tuyên bố là Sứ giả để trao đổi bài.
coup-you-exchange = Bạn rút bài để trao đổi với bộ bài triều đình.
coup-exchanges = { $player } rút 2 lá bài để trao đổi.
coup-you-exchange-complete = Bạn đã hoàn tất trao đổi bài.
coup-exchange-complete = { $player } đã hoàn thành việc trao đổi bài { GENDER_TERM($player_gender, "possessive-determiner") }.

coup-drew-replacement-card = Bạn đã rút được lá { $character } để thay thế.
coup-action-pass-confirmed = Bạn đã bỏ qua.
coup-player-passes-reaction = { $player } bỏ qua trong cửa sổ phản ứng này.

coup-waiting-for-reactions = Đang chờ người chơi Thách thức hoặc Chặn...
coup-you-eliminated = Bạn đã mất toàn bộ ảnh hưởng và bị loại khỏi cuộc chơi. Toàn bộ xu của bạn được trả về ngân khố.
coup-player-eliminated = { $player } đã mất tất cả lá bài { GENDER_TERM($player_gender, "possessive-determiner") } và bị loại khỏi cuộc chơi.
coup-you-win-game = Bạn là người sống sót cuối cùng và giành chiến thắng!
coup-cannot-afford-assassinate = Bạn cần ít nhất 3 xu để ám sát.
coup-cannot-afford-coup = Bạn cần ít nhất 7 xu để tiến hành Đảo chính.
coup-your-block-successful = Lời chặn của bạn thành công. Hành động ban đầu thất bại.
coup-block-successful = { $player } đã chặn hành động thành công!
coup-you-assassination-refunded = Bạn được trả lại { $amount } xu Ám sát vì lời tuyên bố Sát thủ đã bị thách thức thành công.
coup-assassination-refunded = { $player } được trả lại { $amount } xu Ám sát vì lời tuyên bố Sát thủ đã bị thách thức thành công.

coup-you-challenge = Bạn thách thức { $target }!
coup-player-challenges-you = { $challenger } thách thức lời tuyên bố của bạn!
coup-challenges = { $challenger } thách thức { $target }!
coup-you-catch-bluff = Bạn lật tẩy cú bịp của { $player }. { $player } phải mất một lá ảnh hưởng.
coup-your-bluff-caught = { $challenger } lật tẩy cú bịp của bạn. Bạn phải mất một lá ảnh hưởng.
coup-challenge-succeeded = { $challenger } lật tẩy cú bịp của { $player }. { $player } phải mất một lá ảnh hưởng.
coup-you-prove-claim = Bạn lật lá { $character } và chứng minh lời tuyên bố của mình. { $challenger } phải mất một lá ảnh hưởng.
coup-you-lose-challenge = { $player } lật lá { $character }. Bạn thách thức sai và phải mất một lá ảnh hưởng.
coup-challenge-failed = { $player } đã nói thật và lật lá { $character }. { $challenger } phải mất một lá ảnh hưởng.
coup-you-block-foreign-aid = Bạn tuyên bố mình là Tướng quân để chặn Viện trợ nước ngoài của { $target }.
coup-your-foreign-aid-blocked = { $player } tuyên bố là Tướng quân để chặn Viện trợ nước ngoài của bạn.
coup-blocks-foreign-aid = { $blocker } tuyên bố là Tướng quân để chặn Viện trợ nước ngoài của { $target }.
coup-you-block-assassination = Bạn tuyên bố mình là Nữ bá tước để chặn cuộc Ám sát của { $target }.
coup-your-assassination-blocked = { $player } tuyên bố là Nữ bá tước để chặn cuộc Ám sát của bạn.
coup-blocks-assassinate = { $blocker } tuyên bố là Nữ bá tước để chặn cuộc Ám sát của { $target }.
coup-you-block-steal = Bạn tuyên bố mình là Đô đốc hoặc Sứ giả để chặn hành động Trộm của { $target }.
coup-your-steal-blocked = { $player } tuyên bố là Đô đốc hoặc Sứ giả để chặn hành động Trộm của bạn.
coup-blocks-steal = { $blocker } tuyên bố là Đô đốc hoặc Sứ giả để chặn hành động Trộm xu của { $target }.

coup-you-lose-influence = Bạn mất lá { $character }!
coup-loses-influence = { $player } mất lá { $character } { GENDER_TERM($player_gender, "possessive-determiner") }!
coup-must-lose-influence = Bạn phải chọn một lá bài để bỏ đi.
coup-must-return-card = Vui lòng chọn một lá bài để trả lại bộ bài.
coup-returned-card = Bạn đã trả lại lá { $character } vào bộ bài.

coup-you-are-eliminated = Bạn đã bị loại và không thể thực hiện hành động này.

coup-action-check-wealth = Kiểm tra tài sản
coup-action-check-hand = Kiểm tra bài trên tay
coup-action-check-table = Kiểm tra bàn chơi

coup-wealth-line = { $player }: { $coins } xu
coup-no-alive-players = Không còn người chơi nào còn sống.
coup-no-cards = Bạn không có lá bài nào.
coup-hand-context = Bạn có { $coins } xu. Các lá bài của bạn: { $cards }.
coup-table-line = { $player } đã mất: { $cards }
coup-table-empty = Chưa có lá bài nào bị lật.

coup-end-winner = Người thắng
coup-end-eliminated = Đã bị loại
coup-end-line = { $rank }. { $name } ({ $status }) đang có { $coins } xu. Các lá bài: { $cards }

coup-set-mandatory-coup = Ngưỡng xu bắt buộc Đảo chính là { $coins }
coup-enter-mandatory-coup = Nhập số xu bắt buộc phải Đảo chính từ 10 đến 20:
coup-option-changed-mandatory-coup = Ngưỡng Đảo chính bắt buộc đã thay đổi.
coup-desc-mandatory-coup-threshold = Số xu khiến người chơi bắt buộc phải đảo chính thay vì chọn hành động khác (mặc định 10, phạm vi 10-20).

coup-set-timer-duration = Thời gian chờ phản ứng là { $seconds } giây
coup-enter-timer-duration = Nhập thời gian cho phép Thách thức hoặc Chặn từ 3 đến 15 giây:
coup-option-changed-timer = Thời gian chờ đã thay đổi.
coup-desc-timer-duration-seconds = Thời gian dành cho phản ứng và thách thức có hẹn giờ trong Đảo Chính (mặc định 7 giây, phạm vi 3-15).
