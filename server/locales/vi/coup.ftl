# Coup game messages
# Note: Common messages like round-start, turn-start are in games.ftl

game-name-coup = Đảo Chính

coup-action-income = Thu nhập (cộng 1 xu)
coup-action-foreign-aid = Viện trợ nước ngoài (cộng 2 xu)
coup-action-coup = Đảo chính (tốn 7 xu)
coup-action-tax = Thu thuế (Tướng quân, cộng 3 xu)
coup-action-assassinate = Ám sát (Sát thủ, tốn 3 xu)
coup-action-steal = Trộm đồ (Đô đốc, cộng 2 xu)
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

coup-select-target = Chọn mục tiêu:
coup-must-coup = Bạn đang có từ 10 xu trở lên và bắt buộc phải Đảo chính!
coup-not-enough-coins = Bạn không có đủ xu.
coup-cannot-challenge-action = Bạn không thể thách thức hành động này.
coup-cannot-block-now = Bạn không thể chặn vào lúc này.
coup-only-target-can-block = Chỉ mục tiêu của hành động mới có thể chặn.
coup-cannot-block-action = Hành động này không thể bị chặn.
coup-no-active-claim = Không có tuyên bố nào đang diễn ra để thách thức.

coup-takes-income = { $player } nhận Thu nhập.
coup-claims-foreign-aid = { $player } yêu cầu Viện trợ nước ngoài.
coup-takes-foreign-aid = { $player } đã nhận Viện trợ nước ngoài.
coup-plays-coup = { $player } tiến hành Đảo chính nhắm vào { $target }!
coup-claims-tax = { $player } tuyên bố là Tướng quân và yêu cầu Thu thuế.
coup-takes-tax = { $player } đã thu thuế.
coup-claims-assassinate = { $player } tuyên bố là Sát thủ và nhắm vào { $target }.
coup-assassinates = { $player } ám sát { $target }.
coup-claims-steal = { $player } tuyên bố là Đô đốc và cố gắng trộm đồ của { $target }.
coup-steals = { $player } trộm { $amount } xu từ { $target }.
coup-claims-exchange = { $player } tuyên bố là Sứ giả để trao đổi bài.
coup-exchanges = { $player } rút 2 lá bài để trao đổi.
coup-exchange-complete = { $player } đã hoàn thành việc trao đổi bài.

coup-drew-replacement-card = Bạn đã rút được lá { $character } để thay thế.
coup-action-pass-confirmed = Bạn đã bỏ qua.

coup-waiting-for-reactions = Đang chờ người chơi Thách thức hoặc Chặn...
coup-player-eliminated = { $player } đã mất tất cả lá bài và bị loại khỏi cuộc chơi.
coup-game-over = Trò chơi kết thúc! { $winner } là người cuối cùng còn sống sót và giành chiến thắng!
coup-target-is-dead = Mục tiêu không hợp lệ: { $target } đã bị loại.
coup-cannot-afford-assassinate = Bạn cần ít nhất 3 xu để ám sát.
coup-cannot-afford-coup = Bạn cần ít nhất 7 xu để tiến hành Đảo chính.
coup-bluff-called = { $player } đã bị lật tẩy nói dối và phải bỏ một lá bài!
coup-bluff-wrong = { $challenger } đã đoán sai và phải bỏ một lá bài!
coup-block-successful = { $blocker } đã chặn hành động thành công!
coup-action-resolves = Hành động được thực hiện thành công.

coup-challenges = { $challenger } thách thức { $target }!
coup-challenge-succeeded = { $player } đã bị lật tẩy!
coup-challenge-failed = { $player } đã nói thật, họ lật lên lá { $character }!
coup-blocks-foreign-aid = { $blocker } tuyên bố là Tướng quân để chặn Viện trợ nước ngoài của { $target }.
coup-blocks-assassinate = { $blocker } tuyên bố là Nữ bá tước để chặn cuộc Ám sát của { $target }.
coup-blocks-steal = { $blocker } tuyên bố là Đô đốc hoặc Sứ giả để chặn hành động Trộm đồ của { $target }.

coup-loses-influence = { $player } mất lá { $character }!
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

coup-set-timer-duration = Thời gian chờ phản ứng là { $seconds } giây
coup-enter-timer-duration = Nhập thời gian cho phép Thách thức hoặc Chặn từ 3 đến 15 giây:
coup-option-changed-timer = Thời gian chờ đã thay đổi.
