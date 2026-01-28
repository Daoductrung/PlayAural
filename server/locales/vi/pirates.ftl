# Pirates of the Lost Seas game messages
# Note: Common messages like round-start, turn-start are in games.ftl

# Game name
game-name-pirates = Cướp Biển Vùng Biển Bị Lãng Quên

# Game start and setup
pirates-welcome = Chào mừng đến với Cướp Biển Vùng Biển Bị Lãng Quên! Hãy giong buồm ra khơi, thu thập ngọc và chiến đấu với những tên cướp biển khác!
pirates-oceans = Chuyến đi của bạn sẽ đi qua: { $oceans }
pirates-gems-placed = { $total } viên ngọc đã được rải rác khắp biển. Hãy tìm tất cả chúng!
pirates-golden-moon = Mặt Trăng Vàng đang lên! Mọi điểm XP nhận được sẽ nhân ba trong vòng này!

# Turn announcements
pirates-turn = Lượt của { $player }. Vị trí { $position }
pirates-status-line = { $player }: Cấp { $level }, { $xp } XP, { $points }, { $gems }
pirates-end-score-line = { $rank }. { $player }: { $points }, cấp { $level }

# Movement actions
pirates-move-left = Đi sang trái
pirates-move-right = Đi sang phải
pirates-move-2-left = Đi 2 ô sang trái
pirates-move-2-right = Đi 2 ô sang phải
pirates-move-3-left = Đi 3 ô sang trái
pirates-move-3-right = Đi 3 ô sang phải

# Movement messages
pirates-move-you = Bạn đi về phía { $direction } đến vị trí { $position }.
pirates-move-you-tiles = Bạn đi { $tiles } ô về phía { $direction } đến vị trí { $position }.
pirates-move = { $player } đi về phía { $direction } đến vị trí { $position }.
pirates-map-edge = Bạn không thể đi xa hơn. Bạn đang ở vị trí { $position }.

# Position and status
pirates-check-status = Kiểm tra trạng thái
pirates-check-position = Kiểm tra vị trí
pirates-check-moon = Kiểm tra độ sáng mặt trăng
pirates-your-position = Vị trí của bạn: { $position } tại { $ocean }
pirates-moon-brightness = Mặt Trăng Vàng có độ sáng { $brightness }%. ({ $collected } trên tổng số { $total } ngọc đã được thu thập).
pirates-no-golden-moon = Hiện không thấy Mặt Trăng Vàng trên bầu trời.

# Gem collection
pirates-gem-found-you = Bạn tìm thấy một viên { $gem }! Trị giá { $value } điểm.
pirates-gem-found = { $player } tìm thấy một viên { $gem }! Trị giá { $value } điểm.
pirates-all-gems-collected = Tất cả ngọc đã được thu thập!

# Winner
pirates-winner = { $player } thắng với { $score } điểm!

# Skills menu
pirates-use-skill = Sử dụng kỹ năng
pirates-select-skill = Chọn một kỹ năng để sử dụng

# Combat - Attack initiation
pirates-cannonball = Bắn đại bác
pirates-no-targets = Không có mục tiêu nào trong phạm vi { $range } ô.
pirates-attack-you-fire = Bạn bắn đại bác vào { $target }!
pirates-attack-incoming = { $attacker } bắn đại bác vào bạn!
pirates-attack-fired = { $attacker } bắn đại bác vào { $defender }!

# Combat - Rolls
pirates-attack-roll = Xúc xắc tấn công: { $roll }
pirates-attack-bonus = Thưởng tấn công: +{ $bonus }
pirates-defense-roll = Xúc xắc phòng thủ: { $roll }
pirates-defense-roll-others = { $player } lắc { $roll } để phòng thủ.
pirates-defense-bonus = Thưởng phòng thủ: +{ $bonus }

# Combat - Hit results
pirates-attack-hit-you = Trúng trực diện! Bạn bắn trúng { $target }!
pirates-attack-hit-them = Bạn bị trúng đạn của { $attacker }!
pirates-attack-hit = { $attacker } bắn trúng { $defender }!

# Combat - Miss results
pirates-attack-miss-you = Đại bác của bạn trượt { $target }.
pirates-attack-miss-them = Đại bác bắn trượt bạn!
pirates-attack-miss = Đại bác của { $attacker } trượt { $defender }.

# Combat - Push
pirates-push-you = Bạn đẩy { $target } về bên { $direction } đến vị trí { $position }!
pirates-push-them = { $attacker } đẩy bạn về bên { $direction } đến vị trí { $position }!
pirates-push = { $attacker } đẩy { $defender } về bên { $direction } từ { $old_pos } đến { $new_pos }.

# Combat - Gem stealing
pirates-steal-attempt = { $attacker } cố gắng trộm ngọc!
pirates-steal-rolls = Xúc xắc trộm: { $steal } vs phòng thủ: { $defend }
pirates-steal-success-you = Bạn trộm được viên { $gem } từ { $target }!
pirates-steal-success-them = { $attacker } trộm mất viên { $gem } của bạn!
pirates-steal-success = { $attacker } trộm viên { $gem } từ { $defender }!
pirates-steal-failed = Cú trộm thất bại!

# XP and Leveling
pirates-xp-gained = +{ $xp } XP
pirates-level-up = { $player } đạt cấp { $level }!
pirates-level-up-you = Bạn đạt cấp { $level }!
pirates-level-up-multiple = { $player } tăng { $levels } cấp! Hiện tại cấp { $level }!
pirates-level-up-multiple-you = Bạn tăng { $levels } cấp! Hiện tại cấp { $level }!
pirates-skills-unlocked = { $player } mở khóa kỹ năng mới: { $skills }.
pirates-skills-unlocked-you = Bạn mở khóa kỹ năng mới: { $skills }.

# Skill activation
pirates-skill-activated = { $player } kích hoạt { $skill }!
pirates-buff-expired = Hiệu ứng { $skill } của { $player } đã hết.

# Sword Fighter skill
pirates-sword-fighter-activated = Kiếm Sĩ kích hoạt! +4 thưởng tấn công trong { $turns } lượt.

# Push skill (defense buff)
pirates-push-activated = Đẩy Lùi kích hoạt! +3 thưởng phòng thủ trong { $turns } lượt.

# Skilled Captain skill
pirates-skilled-captain-activated = Thuyền Trưởng Tài Ba kích hoạt! +2 tấn công và +2 phòng thủ trong { $turns } lượt.

# Double Devastation skill
pirates-double-devastation-activated = Hủy Diệt Kép kích hoạt! Tầm bắn tăng lên 10 ô trong { $turns } lượt.

# Battleship skill
pirates-battleship-activated = Thiết Giáp Hạm kích hoạt! Bạn có thể bắn hai lần trong lượt này!
pirates-battleship-no-targets = Không có mục tiêu cho lần bắn { $shot }.
pirates-battleship-shot = Bắn lần { $shot }...

# Portal skill
pirates-portal-no-ships = Không nhìn thấy thuyền nào khác để dịch chuyển tới.
pirates-portal-fizzle = Cổng dịch chuyển của { $player } tắt ngấm mà không có đích đến.
pirates-portal-success = { $player } dịch chuyển tới { $ocean } tại vị trí { $position }!

# Gem Seeker skill
pirates-gem-seeker-reveal = Biển cả thì thầm về một viên { $gem } tại vị trí { $position }. (còn { $uses } lần dùng)

# Level requirements
pirates-requires-level-15 = Cần cấp 15
pirates-requires-level-150 = Cần cấp 150

# XP Multiplier options
pirates-set-combat-xp-multiplier = hệ số xp chiến đấu: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = kinh nghiệm cho chiến đấu
pirates-set-find-gem-xp-multiplier = hệ số xp tìm ngọc: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = kinh nghiệm tìm ngọc

# Gem stealing options
pirates-set-gem-stealing = Trộm ngọc: { $mode }
pirates-select-gem-stealing = Chọn chế độ trộm ngọc
pirates-option-changed-stealing = Trộm ngọc đặt thành { $mode }.

# Gem stealing mode choices
pirates-stealing-with-bonus = Có cộng điểm xúc xắc
pirates-stealing-no-bonus = Không cộng điểm
pirates-stealing-disabled = Vô hiệu hóa

# Directions
pirates-dir-left = trái
pirates-dir-right = phải

# Oceans
pirates-ocean-rory = Đại Dương Rory
pirates-ocean-dev = Vực Thẳm Nhà Phát Triển
pirates-ocean-par = Biển Thiên Đường Lập Trình Viên
pirates-ocean-pal = Vùng Nước Cung Điện
pirates-ocean-sil = Eo Biển Silva
pirates-ocean-kai = Dòng Chảy Kai
pirates-ocean-gam = Vịnh Game Thủ
pirates-ocean-ser = Biển Phòng Máy Chủ
pirates-ocean-bat = Vịnh Chiến Trường
pirates-ocean-cod = Kênh Biên Dịch Mã

# Gems
pirates-gem-0 = ngọc mắt mèo
pirates-gem-1 = hồng ngọc
pirates-gem-2 = ngọc hồng lựu
pirates-gem-3 = kim cương
pirates-gem-4 = ngọc bích
pirates-gem-5 = ngọc lục bảo
pirates-gem-6 = ngọc hoàng cung
pirates-gem-7 = ngọc nhựa lớn
pirates-gem-8 = đá khốn kiếp xanh tuyệt vời
pirates-gem-9 = thạch anh tím
pirates-gem-10 = nhẫn vàng
pirates-gem-11 = đá đỏ tía tuyệt vời
pirates-gem-12 = đá đỏ máu tuyệt vời
pirates-gem-13 = đá mặt trăng
pirates-gem-14 = ngọc lưu ly
pirates-gem-15 = hổ phách
pirates-gem-16 = thạch anh vàng
pirates-gem-17 = ngọc trai đen chắc chắn không bị nguyền rủa (tm)
pirates-gem-unknown = ngọc chưa biết
pirates-gem-none = không có ngọc

# Skills
pirates-skill-cannon-name = Bắn Đại Bác
pirates-skill-cannon-desc = Bắn một quả đại bác vào người chơi trong phạm vi 5 ô.
pirates-skill-instinct-name = Bản Năng Thủy Thủ
pirates-skill-instinct-desc = Hiển thị thông tin khu vực bản đồ và trạng thái đã dò.
pirates-skill-portal-name = Cổng Dịch Chuyển
pirates-skill-portal-desc = Dịch chuyển đến vị trí ngẫu nhiên trong một đại dương có người chơi khác.
pirates-skill-seeker-name = Dò Ngọc
pirates-skill-seeker-desc = Tiết lộ vị trí của một viên ngọc chưa được thu thập.
pirates-skill-sword-name = Kiếm Sĩ
pirates-skill-sword-desc = Tăng +4 tấn công trong 3 lượt.
pirates-skill-push-name = Đẩy Lùi
pirates-skill-push-desc = Tăng +3 phòng thủ trong 4 lượt.
pirates-skill-captain-name = Thuyền Trưởng Tài Ba
pirates-skill-captain-desc = Tăng +2 tấn công và +2 phòng thủ trong 4 lượt.
pirates-skill-battleship-name = Thiết Giáp Hạm
pirates-skill-battleship-desc = Bắn hai quả đại bác trong một lượt.
pirates-skill-devastation-name = Hủy Diệt Kép
pirates-skill-devastation-desc = Tăng tầm bắn lên 10 ô trong 3 lượt.

# Skill status
pirates-skill-cooldown = { $name } đang hồi chiêu ({ $turns } lượt).
pirates-skill-active = { $name } đang kích hoạt ({ $turns } lượt còn lại).
pirates-skill-no-uses = Không còn lượt sử dụng.
pirates-skill-not-turn = Không phải lượt của bạn.
pirates-skill-no-targets = Không có mục tiêu trong tầm.
pirates-skill-incompatible = Không thể dùng { $skill } khi { $active } đang kích hoạt.

# Sailor's Instinct
pirates-instinct-fully = Đã dò hết
pirates-instinct-partially = Đã dò một phần ({ $count }/5)
pirates-instinct-uncharted = Chưa dò
pirates-instinct-sector = Khu vực { $sector } ({ $start }-{ $end }): { $status }

pirates-req-level = Cần cấp { $level }
pirates-menu-active = { $name } (kích hoạt: { $turns } lượt)
pirates-menu-cooldown = { $name } (hồi chiêu: { $turns } lượt)
pirates-menu-activate = { $name } (kích hoạt)
pirates-menu-back = Quay lại
pirates-instinct-header = Các khu vực bản đồ:
pirates-menu-gem-seeker = { $name } (còn { $uses } lần dùng)
pirates-ocean-unknown = Biển Không tên
