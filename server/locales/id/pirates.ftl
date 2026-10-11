game-name-pirates = Pirates of the Lost Seas
# Setup and round flow
pirates-welcome = Selamat datang di Pirates of the Lost Seas. Jelajahi jalur sepanjang empat puluh petak, kumpulkan permata yang tersebar, dan ungguli awak kapal lawan.
pirates-welcome-brief = Selamat datang di Pirates of the Lost Seas.
pirates-oceans = Perjalanan Anda melintasi { $oceans }.
pirates-gems-placed = Sebanyak { $total } permata telah disembunyikan di sepanjang jalur. Pemilik muatan bernilai tertinggi menang setelah permata terakhir diambil.
pirates-gems-placed-brief = Sebanyak { $total } permata disembunyikan di sepanjang jalur.
pirates-golden-moon = Bulan Emas terbit pada ronde { $round }. Semua perolehan XP pada ronde ini dikalikan tiga.
pirates-golden-moon-brief = Bulan Emas: XP tiga kali lipat pada ronde { $round }.
pirates-turn-you = Giliran Anda di ronde { $round }. Anda berada di posisi { $position } di { $ocean }.
pirates-turn-you-brief = Giliran Anda. Posisi { $position }.
pirates-turn = Giliran { $player } pada ronde { $round }, pada posisi { $position } di { $ocean }.
pirates-turn-brief = Giliran { $player }.
# Movement and map information
pirates-move-left = Berlayar satu petak ke kiri
pirates-move-right = Berlayar satu petak ke kanan
pirates-move-2-left = Berlayar dua petak ke kiri
pirates-move-2-right = Berlayar dua petak ke kanan
pirates-move-3-left = Berlayar tiga petak ke kiri
pirates-move-3-right = Berlayar tiga petak ke kanan
pirates-move-you =
    Anda berlayar { $tiles } { $tiles ->
        [one] petak
       *[other] petak
    } ke { $direction } menuju posisi { $position } di { $ocean }.
pirates-move-you-brief = Anda berlayar ke posisi { $position }.
pirates-move =
    { $player } berlayar { $tiles } { $tiles ->
        [one] petak
       *[other] petak
    } ke { $direction } menuju posisi { $position } di { $ocean }.
pirates-move-brief = { $player } berlayar ke posisi { $position }.
pirates-map-edge = Anda tidak dapat berlayar lebih jauh ke arah itu. Posisi { $position } adalah ujung jalur. Pilih tindakan lain.
pirates-dir-left = kiri
pirates-dir-right = kanan
pirates-your-position = Anda berada di posisi { $position }, sektor { $sector }, di { $ocean }.
pirates-check-position = Periksa posisi
pirates-check-moon = Periksa Bulan Emas
pirates-moon-active = Bulan Emas aktif pada ronde { $round }. XP dikalikan tiga. Para awak kapal telah mengambil { $collected } dari { $total } permata. Tersisa { $remaining } permata.
pirates-moon-inactive = Bulan Emas tidak aktif pada ronde { $round }. Bulan Emas kembali dalam { $rounds } { $rounds ->
    [one] ronde
    *[other] ronde
    } lagi. Para awak kapal telah mengambil { $collected } dari { $total } permata. Tersisa { $remaining } permata.
# Status and results
pirates-check-status = Periksa status awak kapal
pirates-check-status-detailed = Status awak kapal terperinci
pirates-status-line =
    { $player }: level { $level }, total { $xp } XP, { $progress } dari { $needed } XP menuju level berikutnya, { $points }, { $gem_count } { $gem_count ->
        [one] permata
       *[other] permata
    }{ $detail ->
        [yes] , posisi { $position } di { $ocean }, muatan: { $gems }, efek aktif: { $skills }
       *[no] { "" }
    }.
pirates-end-score-line = { $rank }. { $player }: { $points }, level { $level }
pirates-all-gems-collected = Permata terakhir telah diambil. Para awak kapal membandingkan muatan mereka.
pirates-all-gems-collected-brief = Permata terakhir diambil.
pirates-you-win = Anda menang dengan { $score } poin.
pirates-you-win-brief = Anda menang: { $score } poin.
pirates-winner = { $player } menang dengan { $score } poin.
pirates-winner-brief = { $player } menang: { $score } poin.
pirates-you-tie = Anda berbagi posisi pertama dengan { $players }, masing-masing mendapat { $score } poin.
pirates-you-tie-brief = Anda berbagi posisi pertama dengan { $score } poin.
pirates-players-tie = { $players } berbagi posisi pertama dengan { $score } poin.
pirates-players-tie-brief = { $players } seri dengan { $score } poin.
# Gems and XP
pirates-gem-found-you = Anda mengambil { $gem }, senilai { $value } { $value ->
    [one] poin
    *[other] poin
    }. Muatan Anda kini bernilai { $score } poin. Tersisa { $remaining } permata di laut.
pirates-gem-found-you-brief = Anda mengambil { $gem }. Skor: { $score }.
pirates-gem-found = { $player } mengambil { $gem }, senilai { $value } { $value ->
    [one] poin
    *[other] poin
    }. Muatan pemain tersebut kini bernilai { $score } poin. Tersisa { $remaining } permata di laut.
pirates-gem-found-brief = { $player } mengambil { $gem }.
pirates-xp-gained-you =
    Anda mendapatkan { $xp } XP untuk { $reason ->
        [gem] mengambil permata
        [attack] mengenai sasaran dengan meriam
        [defense] menangkis serangan meriam
       *[other] menyelesaikan suatu tindakan
    }. Anda sekarang memiliki total { $total } XP.
pirates-xp-gained-you-brief = Anda mendapatkan { $xp } XP. Jumlah: { $total }.
pirates-xp-gained-player =
    { $player } memperoleh { $xp } XP untuk { $reason ->
        [gem] mengambil permata
        [attack] mengenai sasaran dengan meriam
        [defense] menangkis serangan meriam
       *[other] menyelesaikan suatu tindakan
    }, mencapai total { $total } XP.
pirates-xp-gained-player-brief = { $player } mendapatkan { $xp } XP.
pirates-level-up-you = Anda mencapai level { $level }.
pirates-level-up-you-brief = Anda mencapai level { $level }.
pirates-level-up = { $player } mencapai level { $level }.
pirates-level-up-brief = { $player } mencapai level { $level }.
pirates-level-up-multiple-you = Anda naik { $levels } level dan mencapai level { $level }.
pirates-level-up-multiple-you-brief = Anda mencapai level { $level }.
pirates-level-up-multiple = { $player } naik { $levels } level dan mencapai level { $level }.
pirates-level-up-multiple-brief = { $player } mencapai level { $level }.
pirates-skills-unlocked-you = Pada level { $level }, Anda membuka { $skills }.
pirates-skills-unlocked-you-brief = Anda membuka { $skills }.
pirates-skills-unlocked = Pada level { $level }, { $player } membuka { $skills }.
pirates-skills-unlocked-brief = { $player } membuka { $skills }.
# Cannon combat
pirates-cannonball = Tembakkan meriam
pirates-select-cannon-target = Pilih kapal dalam jangkauan meriam
pirates-target-option = { $player }, berjarak { $distance } { $distance ->
    [one] petak
    *[other] petak
    }, { $score } poin, membawa { $gems } { $gems ->
    [one] permata
    *[other] permata
    }
pirates-target-unavailable = Kapal tidak tersedia
pirates-no-targets = Tidak ada kapal lawan dalam jangkauan meriam Anda, yaitu { $range } petak. Pilih bergerak atau kemampuan lain yang tersedia.
pirates-target-out-of-range = { $target } sudah berada di luar jangkauan meriam Anda, yaitu { $range } petak dari posisi { $position }. Pilih tindakan lain.
pirates-attack-you-fire = Anda menembakkan peluru meriam ke { $target }.
pirates-attack-you-fire-brief = Anda menembak { $target }.
pirates-attack-incoming = { $attacker } menembakkan peluru meriam ke arah Anda.
pirates-attack-incoming-brief = { $attacker } menembaki Anda.
pirates-attack-fired = { $attacker } menembakkan peluru meriam ke { $defender }.
pirates-attack-fired-brief = { $attacker } menembak { $defender }.
pirates-combat-rolls-you = Dadu serangan Anda menghasilkan { $attack_die }, ditambah { $attack_bonus }, sehingga totalnya { $attack_total }. Dadu pertahanan { $defender } menghasilkan { $defense_die }, ditambah { $defense_bonus }, sehingga totalnya { $defense_total }.
pirates-combat-rolls-you-brief = Serangan { $attack_total }, pertahanan { $defense_total }.
pirates-combat-rolls-defender = Dadu serangan { $attacker } menghasilkan { $attack_die }, ditambah { $attack_bonus }, sehingga totalnya { $attack_total }. Dadu pertahanan Anda menghasilkan { $defense_die }, ditambah { $defense_bonus }, sehingga totalnya { $defense_total }.
pirates-combat-rolls-defender-brief = Serangan { $attack_total }, pertahanan Anda { $defense_total }.
pirates-combat-rolls-observer = Dadu serangan { $attacker } menghasilkan { $attack_die }, ditambah { $attack_bonus }, sehingga totalnya { $attack_total }. Dadu pertahanan { $defender } menghasilkan { $defense_die }, ditambah { $defense_bonus }, sehingga totalnya { $defense_total }.
pirates-combat-rolls-observer-brief = { $attacker } mendapat { $attack_total }, { $defender } mendapat { $defense_total }.
pirates-attack-hit-you = Tepat sasaran. Serangan Anda sebesar { $attack_total } mengalahkan pertahanan { $target } sebesar { $defense_total }. Pilih tindakan penyerbuan yang tersedia.
pirates-attack-hit-you-brief = Anda mengenai { $target }, { $attack_total } melawan { $defense_total }.
pirates-attack-hit-them = { $attacker } mengenai Anda, { $attack_total } melawan { $defense_total }, dan kini dapat menyerbu kapal Anda.
pirates-attack-hit-them-brief = { $attacker } mengenai Anda, { $attack_total } melawan { $defense_total }.
pirates-attack-hit = { $attacker } mengenai { $defender }, { $attack_total } melawan { $defense_total }, dan dapat menyerbu kapal lawan.
pirates-attack-hit-brief = { $attacker } mengenai { $defender }.
pirates-attack-hit-no-boarding-you = Tepat sasaran. Serangan Anda sebesar { $attack_total } mengalahkan pertahanan { $target } sebesar { $defense_total }. Tembakan Kapal Perang ini memberi XP, tetapi tidak membuka penyerbuan.
pirates-attack-hit-no-boarding-you-brief = Anda mengenai { $target }, { $attack_total } melawan { $defense_total }. Tanpa penyerbuan.
pirates-attack-hit-no-boarding-them = { $attacker } mengenai Anda, { $attack_total } melawan { $defense_total }. Tembakan Kapal Perang tidak membuka penyerbuan.
pirates-attack-hit-no-boarding-them-brief = { $attacker } mengenai Anda. Tanpa penyerbuan.
pirates-attack-hit-no-boarding = { $attacker } mengenai { $defender }, { $attack_total } melawan { $defense_total }. Tembakan Kapal Perang ini tidak membuka penyerbuan.
pirates-attack-hit-no-boarding-brief = { $attacker } mengenai { $defender }. Tanpa penyerbuan.
pirates-attack-miss-you = Total serangan Anda sebesar { $attack_total } tidak mengalahkan total pertahanan { $target } sebesar { $defense_total }. Giliran Anda berakhir.
pirates-attack-miss-you-brief = Serangan Anda ke { $target } gagal, { $attack_total } melawan { $defense_total }.
pirates-attack-miss-them = Anda memukul mundur { $attacker } dengan total pertahanan { $defense_total } terhadap { $attack_total }.
pirates-attack-miss-them-brief = Anda menahan serangan { $attacker }, { $defense_total } melawan { $attack_total }.
pirates-attack-miss = { $defender } menahan serangan { $attacker }, { $defense_total } melawan { $attack_total }.
pirates-attack-miss-brief = Serangan { $attacker } ke { $defender } gagal.
# Boarding
pirates-resolve-boarding = Selesaikan penyerbuan kapal
pirates-select-boarding-action = Tembakan meriam mengenai sasaran. Pilih tindakan penyerbuan kapal
pirates-boarding-steal = Coba curi permata
pirates-boarding-push-left = Tabrak kapal lawan ke kiri
pirates-boarding-push-right = Tabrak kapal lawan ke kanan
pirates-boarding-option-unknown = Tindakan penyerbuan tidak dikenal
pirates-must-resolve-boarding = Selesaikan penyerbuan kapal Anda sebelum mengambil tindakan lain pada giliran ini.
pirates-no-pending-boarding = Tidak ada penyerbuan kapal yang perlu Anda selesaikan.
pirates-boarding-stale = Kapal sasaran penyerbuan sudah tidak tersedia sehingga penyerbuan dibatalkan. Pilih tindakan lain pada giliran ini.
pirates-boarding-option-unavailable = { $action } sudah tidak tersedia terhadap { $defender }. Pilih salah satu tindakan penyerbuan yang tersedia saat ini.
pirates-push-you = Anda menabrak { $target } ke { $direction } dari posisi { $old_pos } ke { $new_pos }, sejauh { $distance } petak. Bonus dorongan Anda menambah jarak sebesar { $bonus } petak.
pirates-push-you-brief = Anda menabrak { $target } hingga terdorong ke posisi { $position }.
pirates-push-them = { $attacker } menabrak Anda ke { $direction } dari posisi { $old_pos } ke { $new_pos }, sejauh { $distance } petak.
pirates-push-them-brief = { $attacker } menabrak Anda hingga terdorong ke posisi { $position }.
pirates-push = { $attacker } menabrak { $defender } ke { $direction } dari posisi { $old_pos } ke { $new_pos }, sejauh { $distance } petak.
pirates-push-brief = { $attacker } menabrak { $defender } hingga terdorong ke posisi { $position }.
pirates-steal-rolls-you = Total pencurian Anda { $steal }. Total penjagaan { $target } adalah { $defend }.
pirates-steal-rolls-you-brief = Pencurian { $steal }, penjagaan { $defend }.
pirates-steal-rolls-defender = Total pencurian { $attacker } adalah { $steal }, total penjagaan Anda adalah { $defend }.
pirates-steal-rolls-defender-brief = Pencurian { $steal }, penjagaan Anda { $defend }.
pirates-steal-rolls-observer = { $attacker } mencoba mencuri dari { $defender }: pencurian { $steal }, penjagaan { $defend }.
pirates-steal-rolls-observer-brief = Pencurian { $attacker } sebesar { $steal } melawan penjagaan { $defender } sebesar { $defend }.
pirates-steal-success-you = Anda mencuri { $gem } dari { $target }. Muatan Anda bernilai { $attacker_score } poin, sedangkan muatan lawan bernilai { $defender_score } poin.
pirates-steal-success-you-brief = Anda mencuri { $gem } dari { $target }.
pirates-steal-success-them = { $attacker } mencuri { $gem } Anda. Muatannya bernilai { $attacker_score } poin, sedangkan muatan Anda bernilai { $defender_score } poin.
pirates-steal-success-them-brief = { $attacker } mencuri { $gem } Anda.
pirates-steal-success = { $attacker } mencuri { $gem } dari { $defender }. Nilai muatan mereka kini masing-masing { $attacker_score } dan { $defender_score } poin.
pirates-steal-success-brief = { $attacker } mencuri { $gem } dari { $defender }.
pirates-steal-failed-you = Total pencurian Anda sebesar { $steal } tidak mengalahkan total penjagaan { $target } sebesar { $defend }. Anda tidak mencuri apa pun.
pirates-steal-failed-you-brief = Pencurian Anda gagal, { $steal } melawan { $defend }.
pirates-steal-failed-defender = Anda menggagalkan pencurian { $attacker }, { $defend } melawan { $steal }, dan mempertahankan muatan Anda.
pirates-steal-failed-defender-brief = Anda menghentikan pencurian { $attacker }.
pirates-steal-failed = { $defender } menghentikan pencurian { $attacker }, { $defend } melawan { $steal }.
pirates-steal-failed-brief = { $attacker } gagal mencuri dari { $defender }.
pirates-steal-no-gems-you = Anda tidak dapat mencuri dari { $target } karena kapalnya tidak membawa permata. Pilih menabrak kapal sebagai gantinya.
pirates-steal-no-gems-you-brief = { $target } tidak memiliki permata untuk dicuri.
pirates-steal-no-gems-defender = { $attacker } tidak dapat mencuri dari Anda karena kapal Anda tidak membawa permata.
pirates-steal-no-gems-defender-brief = Anda tidak memiliki permata untuk dicuri { $attacker }.
pirates-steal-no-gems = { $attacker } tidak dapat mencuri dari { $defender } karena kapal yang diserang tidak membawa permata.
pirates-steal-no-gems-brief = { $defender } tidak memiliki permata untuk dicuri.
# Skills and skill state
pirates-use-skill = Gunakan kemampuan
pirates-select-skill = Pilih kemampuan yang sudah terbuka
pirates-unknown-skill = Kemampuan tidak diketahui
pirates-skill-error = { $message }
pirates-skill-selection-stale = Kemampuan itu tidak tersedia lagi pada level atau keadaan permainan saat ini. Buka kembali menu kemampuan dan pilih kemampuan yang tersedia.
pirates-req-level = { $skill } memerlukan level { $required }, Anda berada pada level { $current }.
pirates-requires-level =
    { $action ->
        [move_2] Berlayar dua petak
        [move_3] Berlayar tiga petak
       *[other] Tindakan itu
    } memerlukan level { $required }, Anda berada pada level { $current }.
pirates-skill-cooldown = { $name } masih dalam waktu tunggu selama { $turns } giliran Anda lagi.
pirates-skill-active = { $name } sudah aktif dan masih bertahan selama { $turns } giliran Anda lagi.
pirates-skill-already-activated-this-turn = Anda sudah mengaktifkan bonus pertempuran pada giliran ini. Selanjutnya, pilih bergerak atau menembakkan meriam.
pirates-skill-no-uses = Kesempatan menggunakan Pencari Permata sudah habis untuk permainan ini.
pirates-skill-no-gems = Pencari Permata tidak menemukan sasaran karena semua permata sudah diambil.
pirates-skill-no-targets = Tidak ada kapal lawan dalam jangkauan kemampuan ini, yaitu { $range } petak.
pirates-skill-incompatible = { $skill } tidak dapat diaktifkan saat { $active } aktif. Tunggu hingga efek saat ini berakhir.
pirates-battleship-after-buff = Kapal Perang tidak dapat digunakan setelah Anda mengaktifkan bonus pertempuran pada giliran ini. Gunakan bonus itu untuk tembakan meriam biasa atau tunggu giliran berikutnya.
pirates-menu-active = { $name }, aktif selama { $turns } giliran lagi
pirates-menu-cooldown = { $name }, waktu tunggu { $turns } giliran lagi
pirates-menu-activate = Aktifkan { $name }
pirates-menu-gem-seeker = { $name }, tersisa { $uses } penggunaan
pirates-active-skill-status = { $skill }, tersisa { $turns } giliran
pirates-no-active-skills = tidak ada
pirates-skill-activated = { $player } mengaktifkan { $skill }. { $effect }
pirates-skill-activated-brief = { $player } mengaktifkan { $skill }.
pirates-buff-expired-you = Efek { $skill } Anda berakhir sebelum giliran ini dimulai.
pirates-buff-expired-you-brief = { $skill } Anda berakhir.
pirates-buff-expired = Efek { $skill } milik { $player } berakhir sebelum gilirannya dimulai.
pirates-buff-expired-brief = { $skill } milik { $player } berakhir.
pirates-skill-instinct-name = Naluri Pelaut
pirates-skill-instinct-desc = Periksa setiap sektor yang berisi lima petak untuk mengetahui permata yang belum diambil dan kapal lawan. Tindakan informasi ini tidak mengakhiri giliran.
pirates-instinct-header = Peta Naluri Pelaut, terbagi menjadi delapan sektor:
pirates-instinct-sector = Sektor { $sector }, posisi { $start } sampai { $end }: { $gems } { $gems ->
    [one] permata yang belum diambil
    *[other] permata yang belum diambil
    }, { $players } { $players ->
    [one] kapal lawan
    *[other] kapal lawan
    }.
pirates-skill-portal-name = Portal
pirates-skill-portal-desc = Pilih samudra lain yang berisi kapal lawan, atau pilih Acak untuk berpindah seketika ke sembarang petak di peta. Waktu tunggu: 3 giliran Anda.
pirates-resolve-portal = Pilih tujuan Portal
pirates-select-portal-ocean = Pilih samudra lain yang berisi kapal lawan, atau pilih Acak untuk sembarang petak di peta
pirates-portal-option = { $ocean }, kapal: { $ships }, { $gems } { $gems ->
    [one] permata yang belum diambil
    *[other] permata yang belum diambil
    }
pirates-portal-option-random = Petak acak di peta
pirates-portal-option-unavailable = Samudra itu tidak dapat menjadi tujuan Portal karena merupakan samudra Anda saat ini atau tidak berisi kapal lawan. Pilih tujuan lain.
pirates-must-resolve-portal = Anda sudah menggunakan Portal dan harus menyelesaikannya pada giliran ini. Pilih tujuan atau pilih Acak untuk berpindah dan mengakhiri giliran.
pirates-no-pending-portal = Tidak ada tujuan Portal yang perlu Anda pilih saat ini.
pirates-portal-no-ships = Tidak ada samudra berisi kapal lawan yang dapat dipilih sebagai tujuan Portal. Namun, Acak tetap dapat membawa Anda ke sembarang petak di peta.
pirates-portal-fizzle-you = Tujuan Portal Anda sudah tidak tersedia. Pilih Acak untuk berpindah seketika ke sembarang petak di peta, atau pilih tujuan lain yang tersedia.
pirates-portal-fizzle-you-brief = Pilih Acak atau tujuan Portal lain yang valid.
pirates-portal-fizzle = Tujuan Portal { $player } tidak lagi valid.
pirates-portal-fizzle-brief = { $player } harus memilih tujuan Portal lain.
pirates-portal-success-you = Anda melewati Portal menuju { $ocean } dan tiba di posisi { $position }. Portal memasuki waktu tunggu selama 3 giliran Anda.
pirates-portal-success-you-brief = Anda melewati Portal ke posisi { $position } di { $ocean }.
pirates-portal-success = { $player } melakukan perjalanan melalui Portal ke { $ocean }, tiba di posisi { $position }.
pirates-portal-success-brief = { $player } melewati Portal ke posisi { $position }.
pirates-skill-seeker-name = Pencari Permata
pirates-skill-seeker-desc = Ungkap posisi tepat satu permata yang belum diambil. Dapat digunakan tiga kali per permainan dan tidak mengakhiri giliran.
pirates-gem-seeker-reveal = Pencari Permata menemukan { $gem } di posisi { $position }. Anda masih dapat menggunakannya { $uses } kali dalam permainan ini.
pirates-skill-sword-name = Pendekar Pedang
pirates-skill-sword-desc = Tambah serangan sebesar 2 selama 3 giliran Anda. Waktu tunggu: 6 giliran. Tidak dapat aktif bersamaan dengan Kapten Andal.
pirates-sword-fighter-activated = Anda mengaktifkan Pendekar Pedang. Serangan bertambah { $bonus } selama { $turns } giliran Anda. Waktu tunggu: { $cooldown } giliran. Anda masih dapat bergerak atau menembak pada giliran ini.
pirates-sword-fighter-activated-brief = Pendekar Pedang aktif. Serangan bertambah { $bonus }.
pirates-skill-push-name = Dorongan Kuat
pirates-skill-push-desc = Tambah jarak dorongan saat penyerbuan sebesar 2 petak selama 3 giliran Anda. Waktu tunggu: 6 giliran.
pirates-push-activated = Anda mengaktifkan Dorongan Kuat. Jarak dorongan saat penyerbuan bertambah { $bonus } petak selama { $turns } giliran Anda. Waktu tunggu: { $cooldown } giliran. Anda masih dapat bergerak atau menembak pada giliran ini.
pirates-push-activated-brief = Dorongan Kuat aktif. Jarak dorongan bertambah { $bonus }.
pirates-skill-captain-name = Kapten Andal
pirates-skill-captain-desc = Tambah serangan sebesar 1 dan pertahanan sebesar 1 selama 4 giliran Anda. Waktu tunggu: 7 giliran. Tidak dapat aktif bersamaan dengan Pendekar Pedang.
pirates-skilled-captain-activated = Anda mengaktifkan Kapten Andal. Serangan bertambah { $attack } dan pertahanan bertambah { $defense } selama { $turns } giliran Anda. Waktu tunggu: { $cooldown } giliran. Anda masih dapat bergerak atau menembak pada giliran ini.
pirates-skilled-captain-activated-brief = Kapten Andal aktif. Serangan bertambah { $attack }, pertahanan bertambah { $defense }.
pirates-skill-battleship-name = Kapal Perang
pirates-skill-battleship-desc = Tembakkan dua peluru meriam ke sasaran yang dipilih awak kapal, tanpa membuka penyerbuan. Giliran berakhir. Waktu tunggu: 4 giliran.
pirates-battleship-activated = Anda menggunakan Kapal Perang untuk { $shots } tembakan meriam. Awak kapal memilih sasaran paling berharga dalam jangkauan untuk setiap tembakan. Tembakan yang mengenai sasaran tidak membuka penyerbuan. Waktu tunggu: { $cooldown } giliran.
pirates-battleship-activated-brief = Anda menggunakan Kapal Perang untuk { $shots } tembakan.
pirates-battleship-activated-player = { $player } menggunakan Kapal Perang untuk { $shots } tembakan meriam. Tembakan yang mengenai sasaran tidak membuka penyerbuan.
pirates-battleship-activated-player-brief = { $player } menggunakan Kapal Perang.
pirates-battleship-shot = Awak kapal Anda menembakkan peluru Kapal Perang ke-{ $shot } ke { $target }.
pirates-battleship-shot-brief = Tembakan ke-{ $shot } ke { $target }.
pirates-battleship-shot-player = Awak kapal { $player } menembakkan peluru Kapal Perang ke-{ $shot } ke { $target }.
pirates-battleship-shot-player-brief = { $player } menembak { $target }.
pirates-battleship-no-targets = Awak kapal Anda tidak dapat melepaskan tembakan ke-{ $shot } karena tidak ada lawan dalam jarak { $range } petak. Kapal Perang selesai.
pirates-battleship-no-targets-brief = Tidak ada sasaran untuk tembakan ke-{ $shot }.
pirates-battleship-no-targets-player = { $player } tidak dapat melepaskan tembakan Kapal Perang ke-{ $shot } karena tidak ada lawan dalam jarak { $range } petak.
pirates-battleship-no-targets-player-brief = { $player } tidak memiliki sasaran untuk tembakan ke-{ $shot }.
pirates-skill-devastation-name = Kehancuran Ganda
pirates-skill-devastation-desc = Tambah jangkauan meriam biasa dari 5 menjadi 10 petak selama 3 giliran Anda. Waktu tunggu: 10 giliran. Tidak dapat digabungkan dengan Kapal Perang.
pirates-double-devastation-activated = Anda mengaktifkan Kehancuran Ganda. Jangkauan meriam menjadi { $range } petak selama { $turns } giliran Anda. Waktu tunggu: { $cooldown } giliran. Anda masih dapat bergerak atau menembak pada giliran ini.
pirates-double-devastation-activated-brief = Kehancuran Ganda aktif. Jangkauan { $range } petak.
# Options and validation
pirates-set-combat-xp-multiplier = Pengali XP pertempuran: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Masukkan pengali XP pertempuran dari 0.1 sampai 3.0
pirates-option-changed-combat-xp = Pengali XP pertempuran diatur menjadi { $combat_multiplier }.
pirates-desc-combat-xp-multiplier = Mengalikan XP dari tembakan meriam yang mengenai sasaran dan pertahanan yang berhasil. Pengali Bulan Emas diterapkan terpisah. Bawaan 1.0, dari 0.1 sampai 3.0.
pirates-set-find-gem-xp-multiplier = Pengali XP pengumpulan permata: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Masukkan pengali XP pengumpulan permata dari 0.1 sampai 3.0
pirates-option-changed-find-gem-xp = Pengali XP pengumpulan permata diatur menjadi { $find_gem_multiplier }.
pirates-desc-find-gem-xp-multiplier = Mengalikan XP saat kapal mengambil permata, termasuk setelah dipindahkan secara paksa. Bawaan 1.0, dari 0.1 sampai 3.0.
pirates-set-gem-stealing = Pencurian permata: { $mode }
pirates-select-gem-stealing = Pilih penggunaan bonus pertempuran untuk dadu pencurian saat penyerbuan
pirates-option-changed-stealing = Pencurian permata disetel ke { $mode }.
pirates-desc-gem-stealing = Menentukan apakah permata dapat dicuri setelah tembakan mengenai sasaran dan apakah bonus serangan serta pertahanan yang aktif memengaruhi lemparan pencurian.
pirates-stealing-with-bonus = Aktif dengan bonus pertempuran
pirates-stealing-no-bonus = Aktif tanpa bonus pertempuran
pirates-stealing-disabled = Nonaktif, penyerbuan hanya dapat mendorong kapal
pirates-error-combat-xp-range = Pengali XP pertempuran bernilai { $value }, di luar rentang { $min } sampai { $max }. Atur dalam rentang tersebut sebelum memulai.
pirates-error-gem-xp-range = Pengali XP pengumpulan permata bernilai { $value }, di luar rentang { $min } sampai { $max }. Atur dalam rentang tersebut sebelum memulai.
pirates-error-stealing-mode = Mode pencurian permata yang disimpan, { $mode }, tidak didukung. Pilih salah satu mode mencuri permata yang terdaftar sebelum memulai.
# Ocean names
pirates-ocean-rory = Samudra Rory
pirates-ocean-dev = Palung Pengembang
pirates-ocean-par = Laut Surga Pemrogram
pirates-ocean-pal = Perairan Istana
pirates-ocean-sil = Selat Silva
pirates-ocean-kai = Arus Kai
pirates-ocean-gam = Teluk Gamer
pirates-ocean-ser = Laut Ruang Server
pirates-ocean-bat = Teluk Pertempuran
pirates-ocean-cod = Selat Kompilasi Kode
pirates-ocean-unknown = Samudra Tak Dikenal
# Gem names
pirates-gem-0 = opal
pirates-gem-1 = rubi
pirates-gem-2 = garnet
pirates-gem-3 = berlian
pirates-gem-4 = safir
pirates-gem-5 = zamrud
pirates-gem-6 = permata istana
pirates-gem-7 = permata plastik besar
pirates-gem-8 = bastardstone biru yang menakjubkan
pirates-gem-9 = ametis
pirates-gem-10 = cincin emas
pirates-gem-11 = ppulpstone merah yang mengagumkan
pirates-gem-12 = gorestone merah yang mengagumkan
pirates-gem-13 = batu bulan
pirates-gem-14 = lapis lazuli
pirates-gem-15 = ambar
pirates-gem-16 = sitrin
pirates-gem-17 = mutiara hitam yang pasti tidak terkutuk, merek dagang
pirates-gem-unknown = permata yang tidak diketahui
pirates-gem-none = tidak ada permata
