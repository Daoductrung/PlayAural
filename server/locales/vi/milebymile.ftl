# Thông báo trò chơi Đường Đua Nghìn Dặm (Mile by Mile)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, chế độ đội nằm trong games.ftl

# Tên trò chơi
game-name-milebymile = Đường Đua Nghìn Dặm

# Tùy chọn trò chơi
milebymile-set-distance = Quãng đường đua: { $miles } dặm
milebymile-enter-distance = Nhập quãng đường đua (300-3000)
milebymile-set-winning-score = Điểm thắng: { $score } điểm
milebymile-enter-winning-score = Nhập điểm thắng (1000-10000)
milebymile-toggle-perfect-crossing = Yêu cầu về đích chính xác: { $enabled }
milebymile-toggle-stacking = Cho phép tấn công cộng dồn: { $enabled }
milebymile-toggle-reshuffle = Xào lại bài đã bỏ: { $enabled }
milebymile-toggle-karma = Luật Nghiệp chướng: { $enabled }
milebymile-set-rig = Sắp xếp bộ bài (Gian lận): { $rig }
milebymile-select-rig = Chọn kiểu sắp xếp bộ bài

# Thông báo thay đổi tùy chọn
milebymile-option-changed-distance = Quãng đường đua được đặt là { $miles } dặm.
milebymile-option-changed-winning = Điểm thắng được đặt là { $score } điểm.
milebymile-option-changed-crossing = Yêu cầu về đích chính xác { $enabled }.
milebymile-option-changed-stacking = Cho phép tấn công cộng dồn { $enabled }.
milebymile-option-changed-reshuffle = Xào lại bài đã bỏ { $enabled }.
milebymile-option-changed-karma = Luật Nghiệp chướng { $enabled }.
milebymile-option-changed-rig = Kiểu sắp xếp bộ bài được đặt là { $rig }.

# Trạng thái
milebymile-status = { $score_info }, { $miles } dặm, Sự cố: { $problems }, Bảo hộ: { $safeties }

# Hành động bài
milebymile-no-matching-safety = Bạn không có Lá Bảo hộ tương ứng!
milebymile-cant-play = Bạn không thể đánh { $card } vì { $reason }.
milebymile-no-card-selected = Chưa chọn lá bài nào để bỏ.
milebymile-no-valid-targets = Không có mục tiêu hợp lệ cho Lá tấn công này!
milebymile-you-drew = Bạn đã rút: { $card }
milebymile-discards = { $player } bỏ một lá bài.
milebymile-select-target = Chọn một mục tiêu

# Đánh bài dặm đường
milebymile-plays-distance-individual = { $player } đánh Lá { $distance } dặm, hiện đang ở dặm thứ { $total }.
milebymile-plays-distance-team = { $player } đánh Lá { $distance } dặm; đội của họ hiện đang ở dặm thứ { $total }.

# Hoàn thành hành trình
milebymile-journey-complete-perfect-individual = { $player } đã hoàn thành hành trình với màn về đích chuẩn xác tuyệt đối!
milebymile-journey-complete-perfect-team = Đội { $team } đã hoàn thành hành trình với màn về đích chuẩn xác tuyệt đối!
milebymile-journey-complete-individual = { $player } đã hoàn thành hành trình!
milebymile-journey-complete-team = Đội { $team } đã hoàn thành hành trình!

# Đánh bài nguy cơ (Hazard)
milebymile-plays-hazard-individual = { $player } đánh Lá { $card } lên { $target }.
milebymile-plays-hazard-team = { $player } đánh Lá { $card } lên Đội { $team }.

# Đánh bài Khắc phục/Bảo hộ
milebymile-plays-card = { $player } đánh Lá { $card }.
milebymile-plays-dirty-trick = { $player } đánh Lá { $card } như một Đòn Phản Công!

# Bộ bài
milebymile-deck-reshuffled = Chồng bài bỏ đã được xào lại vào bộ bài rút.

# Cuộc đua
milebymile-new-race = Cuộc đua mới bắt đầu!
milebymile-race-complete = Cuộc đua hoàn tất! Đang tính điểm...
milebymile-earned-points = { $name } kiếm được { $score } điểm trong cuộc đua này: { $breakdown }.
milebymile-total-scores = Tổng điểm:
milebymile-team-score = { $name }: { $score } điểm

# Chi tiết điểm số
milebymile-from-distance = { $miles } từ quãng đường đi được
milebymile-from-trip = { $points } từ việc hoàn thành chuyến đi
milebymile-from-perfect = { $points } từ việc về đích chuẩn xác
milebymile-from-safe = { $points } từ chuyến đi an toàn (không dùng Lá 200)
milebymile-from-shutout = { $points } từ việc thắng trắng (đối thủ không đi được dặm nào)
milebymile-from-safeties = { $points } từ { $count } { $safeties ->
    [one] Lá bảo hộ
   *[other] Lá bảo hộ
}
milebymile-from-all-safeties = { $points } từ việc có đủ 4 Lá bảo hộ
milebymile-from-dirty-tricks = { $points } từ { $count } { $tricks ->
    [one] đòn phản công
   *[other] đòn phản công
}

# Kết thúc trò chơi
milebymile-wins-individual = { $player } thắng trò chơi!
milebymile-wins-team = Đội { $team } thắng trò chơi! ({ $members })
milebymile-final-score = Điểm tổng kết: { $score } điểm

# Luật Nghiệp chướng - xung đột (cả hai đều mất nghiệp)
milebymile-karma-clash-you-target = Bạn và mục tiêu đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-you-attacker = Bạn và { $attacker } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-others = { $attacker } và { $target } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-your-team = Đội của bạn và mục tiêu đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-target-team = Bạn và Đội { $team } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-other-teams = Đội { $attacker } và Đội { $target } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.

# Luật Nghiệp chướng - kẻ tấn công bị tẩy chay
milebymile-karma-shunned-you = Bạn đã bị tẩy chay vì sự hung hăng của mình! Bạn bị mất điểm Nghiệp.
milebymile-karma-shunned-other = { $player } đã bị tẩy chay vì sự hung hăng của họ!
milebymile-karma-shunned-your-team = Đội của bạn đã bị tẩy chay vì sự hung hăng! Đội bạn bị mất điểm Nghiệp.
milebymile-karma-shunned-other-team = Đội { $team } đã bị tẩy chay vì sự hung hăng của họ!

# Giả Nhân Nghĩa (False Virtue)
milebymile-false-virtue-you = Bạn dùng Giả Nhân Nghĩa và lấy lại điểm Nghiệp!
milebymile-false-virtue-other = { $player } dùng Giả Nhân Nghĩa và lấy lại điểm Nghiệp!
milebymile-false-virtue-your-team = Đội của bạn dùng Giả Nhân Nghĩa và lấy lại điểm Nghiệp!
milebymile-false-virtue-other-team = Đội { $team } dùng Giả Nhân Nghĩa và lấy lại điểm Nghiệp!

# Sự cố/Bảo hộ (cho hiển thị trạng thái)
milebymile-none = không có

# Lý do không đánh được bài
milebymile-reason-not-on-team = bạn không ở trong đội nào
milebymile-reason-stopped = bạn đang bị dừng xe (đèn đỏ/hỏng hóc)
milebymile-reason-has-problem = bạn đang gặp sự cố ngăn cản việc lái xe
milebymile-reason-speed-limit = đang bị giới hạn tốc độ
milebymile-reason-exceeds-distance = nó sẽ vượt quá { $miles } dặm
milebymile-reason-no-targets = không có mục tiêu hợp lệ
milebymile-reason-no-speed-limit = bạn không bị giới hạn tốc độ
milebymile-reason-has-right-of-way = Lá Ưu Tiên cho phép bạn đi mà không cần đèn xanh
milebymile-reason-already-moving = xe của bạn đang chạy rồi
milebymile-reason-must-fix-first = bạn phải sửa { $problem } trước
milebymile-reason-has-gas = xe bạn vẫn còn xăng
milebymile-reason-tires-fine = lốp xe vẫn ổn
milebymile-reason-no-accident = xe bạn không bị tai nạn
milebymile-reason-has-safety = bạn đã có Lá bảo hộ đó rồi
milebymile-reason-has-karma = bạn vẫn còn điểm Nghiệp
milebymile-reason-generic = lá bài này không thể đánh vào lúc này

# Tên lá bài
milebymile-card-out-of-gas = Hết Xăng
milebymile-card-flat-tire = Xịt Lốp
milebymile-card-accident = Tai Nạn
milebymile-card-speed-limit = Giới Hạn Tốc Độ
milebymile-card-stop = Đèn Đỏ
milebymile-card-gasoline = Xăng
milebymile-card-spare-tire = Lốp Dự Phòng
milebymile-card-repairs = Sửa Chữa
milebymile-card-end-of-limit = Hết Giới Hạn
milebymile-card-green-light = Đèn Xanh
milebymile-card-extra-tank = Thùng Xăng Phụ
milebymile-card-puncture-proof = Lốp Chống Đinh
milebymile-card-driving-ace = Tay Lái Lụa
milebymile-card-right-of-way = Xe Ưu Tiên
milebymile-card-false-virtue = Giả Nhân Nghĩa
milebymile-card-miles = { $miles } dặm

# Trạng thái chi tiết


# Lý do hành động bị vô hiệu hóa
milebymile-no-dirty-trick-window = Không có cơ hội đánh đòn phản công.
milebymile-not-your-dirty-trick = Đây không phải cơ hội đánh đòn phản công của đội bạn.
milebymile-between-races = Hãy đợi cuộc đua tiếp theo bắt đầu.

# Lỗi xác thực
milebymile-error-karma-needs-three-teams = Luật Nghiệp chướng yêu cầu ít nhất 3 xe/đội khác nhau.

# Định dạng
milebymile-line-format = { $rank }. { $name }: { $points }

# Chọn mục tiêu
milebymile-target-individual = { $name } ({ $miles } dặm)
milebymile-target-team = Đội { $team }: { $members } ({ $miles } dặm)

milebymile-discard-card = Bỏ bài
milebymile-detailed-status = Trạng thái chi tiết
milebymile-check-status = Kiểm tra trạng thái
milebymile-dirty-trick = Đòn Phản Công
milebymile-info-button = Thông tin
milebymile-info-msg-individual = { $player }: Sự cố: { $hazards }. Bảo hộ: { $safeties }. Đã đi: { $miles } dặm.
milebymile-info-msg-team = Đội { $team } ({ $members }): Sự cố: { $hazards }. Bảo hộ: { $safeties }. Đã đi: { $miles } dặm.
