# Thông báo trò chơi Cướp Biển Vùng Biển Thất Lạc (Pirates of the Lost Seas)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt nằm trong games.ftl

# Tên trò chơi
game-name-pirates = Cướp Biển Vùng Biển Thất Lạc

# Bắt đầu trò chơi và thiết lập
pirates-welcome = Chào mừng đến với Cướp Biển Vùng Biển Thất Lạc! Hãy giong buồm ra khơi, thu thập đá quý và chiến đấu với những tên cướp biển khác!
pirates-oceans = Hành trình của bạn sẽ đi qua: { $oceans }
pirates-gems-placed = { $total } viên đá quý đã rải rác khắp các vùng biển. Hãy tìm tất cả chúng!
pirates-golden-moon = Trăng Vàng đang lên! Tất cả điểm kinh nghiệm (XP) nhận được sẽ nhân ba trong vòng này!

# Thông báo lượt
pirates-turn = Lượt của { $player }. Vị trí { $position }
pirates-status-line = { $player }: Cấp { $level }, { $xp } XP, { $points } điểm, { $gems } đá quý
pirates-end-score-line = { $rank }. { $player }: { $points } điểm, cấp { $level }

# Hành động di chuyển
pirates-move-left = Giong buồm sang trái
pirates-move-right = Giong buồm sang phải
pirates-move-2-left = Giong buồm 2 ô sang trái
pirates-move-2-right = Giong buồm 2 ô sang phải
pirates-move-3-left = Giong buồm 3 ô sang trái
pirates-move-3-right = Giong buồm 3 ô sang phải

# Thông báo di chuyển
pirates-move-you = Bạn giong buồm sang { $direction } tới vị trí { $position }.
pirates-move-you-tiles = Bạn giong buồm { $tiles } ô sang { $direction } tới vị trí { $position }.
pirates-move = { $player } giong buồm sang { $direction } tới vị trí { $position }.
pirates-map-edge = Bạn không thể đi xa hơn nữa. Bạn đang ở vị trí { $position }.

# Vị trí và trạng thái
pirates-check-status = Kiểm tra trạng thái
pirates-check-position = Kiểm tra vị trí
pirates-check-moon = Kiểm tra độ sáng của trăng
pirates-your-position = Vị trí của bạn: { $position } tại { $ocean }
pirates-moon-brightness = Trăng Vàng đang sáng { $brightness }%. (Đã thu thập { $collected } trên tổng số { $total } viên đá quý).
pirates-no-golden-moon = Hiện không thấy Trăng Vàng trên bầu trời.

# Thu thập đá quý
pirates-gem-found-you = Bạn tìm thấy một viên { $gem }! Trị giá { $value } điểm.
pirates-gem-found = { $player } tìm thấy một viên { $gem }! Trị giá { $value } điểm.
pirates-all-gems-collected = Tất cả đá quý đã được thu thập!

# Người thắng
pirates-winner = { $player } thắng với { $score } điểm!

# Menu Kỹ năng
pirates-use-skill = Sử dụng kỹ năng
pirates-select-skill = Chọn một kỹ năng để dùng

# Chiến đấu - Khởi đầu tấn công
pirates-cannonball = Bắn đại bác
pirates-no-targets = Không có mục tiêu trong tầm { $range } ô.
pirates-attack-you-fire = Bạn bắn một quả đại bác vào { $target }!
pirates-attack-incoming = { $attacker } bắn một quả đại bác vào bạn!
pirates-attack-fired = { $attacker } bắn một quả đại bác vào { $defender }!

# Chiến đấu - Gieo xúc xắc
pirates-attack-roll = Điểm tấn công: { $roll }
pirates-attack-bonus = Thưởng tấn công: +{ $bonus }
pirates-defense-roll = Điểm phòng thủ: { $roll }
pirates-defense-roll-others = { $player } gieo được { $roll } điểm phòng thủ.
pirates-defense-bonus = Thưởng phòng thủ: +{ $bonus }

# Chiến đấu - Kết quả trúng
pirates-attack-hit-you = Trúng trực diện! Bạn đã bắn trúng { $target }!
pirates-attack-hit-them = Bạn đã bị { $attacker } bắn trúng!
pirates-attack-hit = { $attacker } bắn trúng { $defender }!

# Chiến đấu - Kết quả trượt
pirates-attack-miss-you = Quả đại bác của bạn bắn trượt { $target }.
pirates-attack-miss-them = Quả đại bác bắn trượt bạn!
pirates-attack-miss = Quả đại bác của { $attacker } bắn trượt { $defender }.

# Chiến đấu - Đẩy lùi
pirates-push-you = Bạn đẩy { $target } sang { $direction } tới vị trí { $position }!
pirates-push-them = { $attacker } đẩy bạn sang { $direction } tới vị trí { $position }!
pirates-push = { $attacker } đẩy { $defender } sang { $direction } từ { $old_pos } đến { $new_pos }.

# Chiến đấu - Cướp đá quý
pirates-steal-attempt = { $attacker } cố gắng cướp đá quý!
pirates-steal-rolls = Điểm cướp: { $steal } vs phòng thủ: { $defend }
pirates-steal-success-you = Bạn đã cướp được một viên { $gem } từ { $target }!
pirates-steal-success-them = { $attacker } đã cướp mất viên { $gem } của bạn!
pirates-steal-success = { $attacker } cướp một viên { $gem } từ { $defender }!
pirates-steal-failed = Nỗ lực cướp thất bại!

# XP và Lên cấp
pirates-xp-gained = +{ $xp } XP
pirates-level-up = { $player } đã đạt cấp { $level }!
pirates-level-up-you = Bạn đã đạt cấp { $level }!
pirates-level-up-multiple = { $player } đã tăng { $levels } cấp! Hiện tại là cấp { $level }!
pirates-level-up-multiple-you = Bạn đã tăng { $levels } cấp! Hiện tại là cấp { $level }!
pirates-skills-unlocked = { $player } mở khóa kỹ năng mới: { $skills }.
pirates-skills-unlocked-you = Bạn mở khóa kỹ năng mới: { $skills }.

# Kích hoạt kỹ năng
pirates-skill-activated = { $player } kích hoạt { $skill }!
pirates-buff-expired = Hiệu ứng { $skill } của { $player } đã hết.

# Kỹ năng Kiếm Sĩ
pirates-sword-fighter-activated = Kiếm Sĩ kích hoạt! +4 tấn công trong { $turns } lượt.

# Kỹ năng Đẩy (Buff phòng thủ)
pirates-push-activated = Đẩy Lùi kích hoạt! +3 phòng thủ trong { $turns } lượt.

# Kỹ năng Thuyền Trưởng Tài Ba
pirates-skilled-captain-activated = Thuyền Trưởng Tài Ba kích hoạt! +2 tấn công và +2 phòng thủ trong { $turns } lượt.

# Kỹ năng Hủy Diệt Kép
pirates-double-devastation-activated = Hủy Diệt Kép kích hoạt! Tầm bắn tăng lên 10 ô trong { $turns } lượt.

# Kỹ năng Chiến Hạm
pirates-battleship-activated = Chiến Hạm kích hoạt! Bạn có thể bắn hai lần trong lượt này!
pirates-battleship-no-targets = Không có mục tiêu cho lần bắn thứ { $shot }.
pirates-battleship-shot = Đang bắn lần { $shot }...

# Kỹ năng Cổng Dịch Chuyển
pirates-portal-no-ships = Không thấy tàu nào khác để dịch chuyển tới.
pirates-portal-fizzle = Cổng dịch chuyển của { $player } xì khói và không có đích đến.
pirates-portal-success = { $player } dịch chuyển tới { $ocean } tại vị trí { $position }!

# Kỹ năng Tìm Đá Quý
pirates-gem-seeker-reveal = Biển cả thì thầm về một viên { $gem } tại vị trí { $position }. (Còn { $uses } lần dùng)

# Yêu cầu cấp độ
pirates-requires-level-15 = Yêu cầu cấp 15
pirates-requires-level-150 = Yêu cầu cấp 150

# Tùy chọn Hệ số XP
pirates-set-combat-xp-multiplier = Hệ số XP chiến đấu: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Kinh nghiệm nhận được khi chiến đấu
pirates-set-find-gem-xp-multiplier = Hệ số XP tìm đá quý: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Kinh nghiệm nhận được khi tìm thấy đá quý

# Tùy chọn Cướp đá quý
pirates-set-gem-stealing = Cướp đá quý: { $mode }
pirates-select-gem-stealing = Chọn chế độ cướp đá quý
pirates-option-changed-stealing = Chế độ cướp đá quý được đặt là { $mode }.

# Các lựa chọn chế độ cướp đá quý
pirates-stealing-with-bonus = Có cộng điểm thưởng
pirates-stealing-no-bonus = Không cộng điểm thưởng
pirates-stealing-disabled = Tắt

# Hướng
pirates-dir-left = trái
pirates-dir-right = phải

# Các Vùng Biển
pirates-ocean-rory = Đại Dương Rory
pirates-ocean-dev = Vực Thẳm Nhà Phát Triển
pirates-ocean-par = Biển Thiên Đường Lập Trình
pirates-ocean-pal = Vùng Nước Cung Điện
pirates-ocean-sil = Eo Biển Silva
pirates-ocean-kai = Dòng Chảy Kai
pirates-ocean-gam = Vịnh Game Thủ
pirates-ocean-ser = Biển Máy Chủ
pirates-ocean-bat = Vịnh Chiến Trường
pirates-ocean-cod = Kênh Biên Dịch Mã

# Các loại đá quý
pirates-gem-0 = đá opal
pirates-gem-1 = hồng ngọc
pirates-gem-2 = ngọc hồng lựu
pirates-gem-3 = kim cương
pirates-gem-4 = đá sapphire
pirates-gem-5 = ngọc lục bảo
pirates-gem-6 = ngọc cung điện
pirates-gem-7 = ngọc nhựa cỡ lớn
pirates-gem-8 = đá khốn kiếp xanh dương tuyệt đỉnh
pirates-gem-9 = thạch anh tím
pirates-gem-10 = nhẫn vàng
pirates-gem-11 = đá bột giấy đỏ tuyệt đỉnh
pirates-gem-12 = đá máu đỏ tuyệt đỉnh
pirates-gem-13 = đá mặt trăng
pirates-gem-14 = đá lapis lazuli
pirates-gem-15 = hổ phách
pirates-gem-16 = thạch anh vàng
pirates-gem-17 = ngọc trai đen (chắc chắn không bị nguyền rủa)
pirates-gem-unknown = đá quý không xác định
pirates-gem-none = không có đá quý

# Kỹ năng (Mô tả)
pirates-skill-cannon-name = Bắn Đại Bác
pirates-skill-cannon-desc = Bắn đại bác vào một người chơi trong phạm vi 5 ô.
pirates-skill-instinct-name = Trực Giác Thủy Thủ
pirates-skill-instinct-desc = Hiển thị thông tin khu vực bản đồ và trạng thái khám phá.
pirates-skill-portal-name = Cổng Dịch Chuyển
pirates-skill-portal-desc = Dịch chuyển tới vị trí ngẫu nhiên trong một vùng biển có người chơi khác.
pirates-skill-seeker-name = Tìm Đá Quý
pirates-skill-seeker-desc = Tiết lộ vị trí của một viên đá quý chưa được thu thập.
pirates-skill-sword-name = Kiếm Sĩ
pirates-skill-sword-desc = Tăng +4 tấn công trong 3 lượt.
pirates-skill-push-name = Đẩy Lùi
pirates-skill-push-desc = Tăng +3 phòng thủ trong 4 lượt.
pirates-skill-captain-name = Thuyền Trưởng Tài Ba
pirates-skill-captain-desc = Tăng +2 tấn công và +2 phòng thủ trong 4 lượt.
pirates-skill-battleship-name = Chiến Hạm
pirates-skill-battleship-desc = Bắn hai quả đại bác trong một lượt.
pirates-skill-devastation-name = Hủy Diệt Kép
pirates-skill-devastation-desc = Tăng tầm bắn đại bác lên 10 ô trong 3 lượt.

# Trạng thái kỹ năng
pirates-skill-cooldown = { $name } đang hồi chiêu (còn { $turns } lượt).
pirates-skill-active = { $name } đang kích hoạt (còn { $turns } lượt).
pirates-skill-no-uses = Không còn lượt sử dụng.
pirates-skill-not-turn = Chưa đến lượt của bạn.
pirates-skill-no-targets = Không có mục tiêu trong tầm.
pirates-skill-incompatible = Không thể dùng { $skill } khi { $active } đang kích hoạt.

# Trực Giác Thủy Thủ
pirates-instinct-fully = Đã khám phá hoàn toàn
pirates-instinct-partially = Đã khám phá một phần ({ $count }/5)
pirates-instinct-uncharted = Chưa khám phá
pirates-instinct-sector = Khu vực { $sector } ({ $start }-{ $end }): { $status }

pirates-req-level = Yêu cầu cấp { $level }
pirates-menu-active = { $name } (đang chạy: { $turns } lượt)
pirates-menu-cooldown = { $name } (hồi chiêu: { $turns } lượt)
pirates-menu-activate = { $name } (kích hoạt)
pirates-menu-back = Quay lại
pirates-instinct-header = Các Khu Vực Bản Đồ:
pirates-menu-gem-seeker = { $name } (còn { $uses } lần dùng)
pirates-ocean-unknown = Vùng Biển Không Xác Định
