game-name-battleship = Tàu Chiến

# Tùy chọn
battleship-set-grid-size = Vùng tác chiến: { $size }
battleship-select-grid-size = Chọn kích thước vùng tác chiến
battleship-option-changed-grid-size = Đã đặt vùng tác chiến thành { $size }.

battleship-set-placement-mode = Triển khai: { $mode }
battleship-select-placement-mode = Chọn chế độ triển khai
battleship-option-changed-placement-mode = Đã đặt chế độ triển khai thành { $mode }.

battleship-set-replay-on-hit = Tiếp tục khai hỏa khi trúng: { $enabled }
battleship-option-changed-replay-on-hit = Đã đặt tiếp tục khai hỏa khi trúng thành { $enabled }.

battleship-set-turn-timer = Thời gian lượt: { $seconds }
battleship-select-turn-timer = Chọn thời gian lượt
battleship-option-changed-turn-timer = Đã đặt thời gian lượt thành { $seconds }.

# Nhãn lựa chọn
battleship-grid-6x6 = 6 x 6
battleship-grid-8x8 = 8 x 8
battleship-grid-10x10 = 10 x 10
battleship-grid-12x12 = 12 x 12

battleship-placement-auto = Tự động
battleship-placement-manual = Thủ công

battleship-timer-off = Tắt
battleship-timer-30 = 30 giây
battleship-timer-45 = 45 giây
battleship-timer-60 = 60 giây

# Kiểm tra thiết lập
battleship-error-invalid-grid-size = Kích thước vùng tác chiến { $size } không được hỗ trợ.
battleship-error-grid-too-small = Vùng tác chiến { $size } x { $size } quá nhỏ cho đầy đủ hạm đội. Hãy dùng ít nhất { $minimum } x { $minimum }.
battleship-error-invalid-placement-mode = Chế độ triển khai { $mode } không được hỗ trợ.
battleship-error-invalid-turn-timer = Thời gian lượt { $seconds } không được hỗ trợ.

# Tên tàu chiến
battleship-ship-carrier = Hàng không mẫu hạm
battleship-ship-battleship = Thiết giáp hạm
battleship-ship-destroyer = Khu trục hạm
battleship-ship-submarine = Tàu ngầm
battleship-ship-patrol = Tàu tuần tiễu
battleship-ship-unknown = Chiến hạm

# Hướng triển khai
battleship-horizontal = Ngang
battleship-vertical = Dọc

# Hành động
battleship-orient-horizontal = Triển khai ngang
battleship-orient-vertical = Triển khai dọc
battleship-orient-horizontal-at = Triển khai { $ship } nằm ngang tại { $coord }
battleship-orient-vertical-at = Triển khai { $ship } theo chiều dọc tại { $coord }
battleship-toggle-view = Chuyển bản đồ
battleship-read-fleet = Tình trạng hạm đội
battleship-read-enemy-fleet = Trinh sát hạm đội địch

# Giai đoạn triển khai
battleship-deploy-start = Giai đoạn triển khai. Bố trí { $ship }, dài { $size } ô. Chọn tọa độ rồi chọn hướng triển khai.
battleship-choose-orientation = Triển khai { $ship } tại { $coord }, dài { $size } ô. Chọn hướng.
battleship-ship-placed = { $ship } đã triển khai tại { $coord }, hướng { $orientation }.
battleship-cannot-place = Không thể triển khai { $ship } tại { $coord } { $orientation }. Tàu không vừa hoặc chồng lên tàu khác.
battleship-place-next-ship = Tàu tiếp theo: { $ship }, dài { $size } ô.
battleship-deploy-done = Hạm đội đã sẵn sàng chiến đấu. Chờ đối phương triển khai.
battleship-deploy-complete = Triển khai hoàn tất.
battleship-select-cell-first = Hãy chọn tọa độ trên bản đồ trước.
battleship-deploy-in-progress = Đang trong giai đoạn triển khai.
battleship-deploy-status-header = Giai đoạn triển khai hạm đội.
battleship-deploy-status-ready-self = Bạn đã sẵn sàng.
battleship-deploy-status-ready-other = { $player } đã sẵn sàng.
battleship-deploy-status-not-ready-self = Bạn chưa sẵn sàng.
battleship-deploy-status-not-ready-other = { $player } chưa sẵn sàng.

# Giai đoạn chiến đấu
battleship-battle-start = Toàn bộ hạm đội đã vào vị trí. Khai hỏa!

# Trúng — ngôi thứ nhất (người bắn), ngôi thứ hai (mục tiêu), ngôi thứ ba (khán giả)
battleship-hit-self = Bạn khai hỏa tọa độ { $coord }. Trúng đích!
battleship-hit-target = { $player } nã đạn vào tọa độ { $coord } của bạn. Trúng đích!
battleship-hit-spectator = { $player } nã đạn vào tọa độ { $coord } của { $target }. Trúng đích!

# Trượt — ngôi thứ nhất/hai/ba
battleship-miss-self = Bạn khai hỏa tọa độ { $coord }. Trượt.
battleship-miss-target = { $player } nã đạn vào tọa độ { $coord } của bạn. Trượt.
battleship-miss-spectator = { $player } nã đạn vào tọa độ { $coord } của { $target }. Trượt.

# Đánh chìm — ngôi thứ nhất/hai/ba
battleship-sunk-self = Bạn đã đánh chìm { $ship } của địch!
battleship-sunk-target = { $player } đã đánh chìm { $ship } của bạn!
battleship-sunk-spectator = { $player } đã đánh chìm { $ship } của { $target }!

# Chiến thắng — ngôi thứ nhất/hai/ba
battleship-victory-self = Bạn chiến thắng! Toàn bộ hạm đội địch đã bị tiêu diệt.
battleship-victory-target = { $player } chiến thắng! Toàn bộ hạm đội của bạn đã bị đánh chìm.
battleship-victory-spectator = { $player } chiến thắng! Toàn bộ hạm đội của { $target } đã bị đánh chìm.

battleship-shot-in-flight = Đạn pháo vẫn đang bay. Hãy chờ kết quả trước khi khai hỏa tiếp.
battleship-not-your-turn = Chưa đến lượt bạn khai hỏa. Hãy chờ { $player } chọn tọa độ.
battleship-wait-for-turn = Hãy chờ lệnh khai hỏa tiếp theo trước khi chọn tọa độ.
battleship-already-shot = Bạn đã bắn vào { $coord } rồi. Hãy chọn một tọa độ chưa trinh sát.
battleship-switch-to-shots = Bạn đang xem vùng biển của mình nên không thể khai hỏa. Nhấn V để chuyển sang bản đồ mục tiêu.
battleship-timeout-fire = Hết giờ! Tự động khai hỏa tọa độ { $coord }.

# Chuyển bản đồ
battleship-view-own = Đang xem vùng biển của bạn.
battleship-view-shots = Đang xem bản đồ mục tiêu.

# Nhãn ô
battleship-cell-empty = { $coord }, biển trống.
battleship-cell-ship-placed = { $coord }, { $ship }.
battleship-cell-unknown = { $coord }, chưa trinh sát.
battleship-cell-hit = { $coord }, trúng.
battleship-cell-sunk = { $coord }, { $ship }, chìm.
battleship-cell-miss = { $coord }, trượt.
battleship-cell-own-ship = { $coord }, { $ship } của bạn.
battleship-cell-own-hit = { $coord }, { $ship } của bạn, bị trúng.
battleship-cell-own-sunk = { $coord }, { $ship } của bạn, đã chìm.
battleship-cell-own-miss = { $coord }, đạn trượt.

# Tình trạng hạm đội
battleship-fleet-header = Hạm Đội Của Bạn
battleship-status-intact = Sẵn sàng chiến đấu
battleship-status-damaged = Hư hại ({ $hits } trên { $size } bị trúng)
battleship-status-sunk = Đã chìm

battleship-enemy-fleet-header = Hạm Đội Địch
battleship-enemy-fleet-summary = Đã tiêu diệt { $sunk } trên { $total } chiến hạm địch.
battleship-enemy-ship-sunk = { $ship } (dài { $size } ô): Đã chìm

# Màn hình kết thúc
battleship-winner-line = { $player } chiến thắng!
battleship-stats-line = { $player }: { $shots } phát bắn, { $hits } trúng đích, { $accuracy }% chính xác
