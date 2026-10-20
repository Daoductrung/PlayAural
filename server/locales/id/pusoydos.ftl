game-name-pusoydos = Pusoy Dos
pusoydos-set-game-mode = Mode permainan: { $choice }
pusoydos-select-game-mode = Pilih mode permainan:
pusoydos-option-changed-game-mode = Mode permainan diubah menjadi { $choice }.
pusoydos-desc-game-mode = Lolos: menangkan sejumlah ronde untuk keluar sebagai pemenang. Pemain terakhir yang tersisa kalah. Kekalahan: pemain di urutan terakhir mendapat satu catatan kalah. Pemain pertama yang mencapai batas kekalahan kalah dalam permainan. Poin: pemenang ronde mendapat poin penalti dari pemain yang kalah. Pemain pertama yang mencapai target menang. Eliminasi Poin: pemain yang kalah mengumpulkan poin penaltinya sendiri dan tersingkir saat mencapai batas. Pemain terakhir yang bertahan menang.
pusoydos-mode-elimination = Lolos
pusoydos-mode-losses = Kekalahan
pusoydos-mode-points = Poin
pusoydos-mode-points-elimination = Eliminasi Poin
pusoydos-set-rounds-to-win = Ronde untuk lolos: { $count }
pusoydos-enter-rounds-to-win = Masukkan jumlah kemenangan ronde untuk lolos, 1 sampai 10:
pusoydos-option-changed-rounds-to-win = Jumlah kemenangan ronde untuk lolos diubah menjadi { $count }.
pusoydos-desc-rounds-to-win = Khusus mode Lolos. Jumlah ronde yang harus dimenangkan agar pemain keluar sebagai pemenang. Nilai bawaan 2, rentang 1 sampai 10.
pusoydos-set-losses-to-lose = Batas kekalahan: { $count }
pusoydos-enter-losses-to-lose = Masukkan batas kekalahan, 1 sampai 10:
pusoydos-option-changed-losses-to-lose = Batas kekalahan diubah menjadi { $count }.
pusoydos-desc-losses-to-lose = Khusus mode Kekalahan. Berapa kali pemain boleh finis terakhir sebelum dinyatakan kalah dalam permainan. Nilai bawaan 3, rentang 1 sampai 10.
pusoydos-set-target-score = Target skor: { $score }
pusoydos-enter-target-score = Masukkan target skor, 10 sampai 10000:
pusoydos-option-changed-target-score = Target skor diubah menjadi { $score }.
pusoydos-desc-target-score = Khusus mode poin. Batas skor untuk menang dalam mode Poin atau tersingkir dalam mode Eliminasi Poin. Nilai bawaan 100, rentang 10 sampai 10000.
pusoydos-set-turn-timer = Batas waktu giliran: { $choice }
pusoydos-select-turn-timer = Pilih batas waktu giliran:
pusoydos-option-changed-turn-timer = Batas waktu giliran diubah menjadi { $choice }.
pusoydos-desc-turn-timer = Batas waktu setiap giliran. Pilih tanpa batas, 10, 15, 20, 30, 45, 60, atau 90 detik. Bawaannya tanpa batas.
pusoydos-timer-10 = 10 detik
pusoydos-timer-15 = 15 detik
pusoydos-timer-20 = 20 detik
pusoydos-timer-30 = 30 detik
pusoydos-timer-45 = 45 detik
pusoydos-timer-60 = 60 detik
pusoydos-timer-90 = 90 detik
pusoydos-timer-unlimited = Tanpa batas
pusoydos-set-allow-2-in-straights = Izinkan kartu 2 dalam Straight: { $enabled }
pusoydos-option-changed-allow-2-in-straights = Kartu 2 dalam Straight: { $enabled }.
pusoydos-desc-allow-2-in-straights = Tentukan apakah kartu 2 boleh digunakan dalam Straight, misalnya As, 2, 3, 4, 5.
pusoydos-set-instant-wins = Menang langsung: { $enabled }
pusoydos-option-changed-instant-wins = Menang langsung: { $enabled }.
pusoydos-desc-instant-wins = Tentukan apakah susunan kartu khusus saat pembagian, yaitu Dragon, Empat Kartu Dua, dan Enam Pasangan, langsung memenangkan ronde. Tidak dapat digabung dengan pertukaran kartu.
pusoydos-set-card-passing = Pertukaran kartu: { $choice }
pusoydos-select-card-passing = Pilih mode pertukaran kartu:
pusoydos-option-changed-card-passing = Pertukaran kartu diubah menjadi { $choice }.
pusoydos-desc-card-passing = Pertukaran kartu antara pemenang dan pemain yang kalah setelah kartu dibagikan. Pilih Nonaktif, Sederhana, atau Lengkap. Pertukaran lengkap memerlukan tepat 2 atau 4 pemain. Pertukaran kartu tidak dapat digabung dengan menang langsung.
pusoydos-passing-off = Nonaktif
pusoydos-passing-simple = Sederhana, pemain urutan pertama dan terakhir bertukar 1 kartu
pusoydos-passing-full = Lengkap, pertama dan terakhir bertukar 2 kartu, kedua dan ketiga bertukar 1 kartu
pusoydos-set-penalty-tier = Tingkat penalti: { $choice }
pusoydos-select-penalty-tier = Pilih tingkat penalti:
pusoydos-option-changed-penalty-tier = Tingkat penalti diubah menjadi { $choice }.
pusoydos-desc-penalty-tier = Khusus mode poin. Tentukan seberapa besar penalti untuk kartu yang tersisa di akhir ronde.
pusoydos-penalty-standard = Standar, mulai 10 kartu dikali 2, 13 kartu dikali 3
pusoydos-penalty-aggressive = Berat, 8 sampai 9 dikali 2, 10 sampai 12 dikali 3, 13 dikali 4
pusoydos-penalty-flat = Tetap, 1 poin per kartu tanpa pengali
pusoydos-set-penalty-per-two = Penalti setiap kartu 2 yang tersisa: { $enabled }
pusoydos-option-changed-penalty-per-two = Penalti setiap kartu 2 yang tersisa: { $enabled }.
pusoydos-desc-penalty-per-two = Khusus mode poin. Setiap kartu 2 yang masih dipegang pemain yang kalah menggandakan penaltinya.
pusoydos-new-hand = Ronde { $round }.
pusoydos-dealt = Anda mendapat { $count } kartu: { $cards }.
pusoydos-you-first-player = Anda memiliki 3 keriting dan mendapat giliran pertama.
pusoydos-first-player = { $player } memiliki 3 keriting dan mendapat giliran pertama.
pusoydos-you-first-player-lowest = Anda memiliki kartu terendah dan mendapat giliran pertama.
pusoydos-first-player-lowest = { $player } memiliki kartu terendah dan mendapat giliran pertama.
pusoydos-you-eliminated = Anda telah memenangkan { $count } ronde dan lolos! Permainan yang bagus.
pusoydos-player-eliminated = { $player } telah memenangkan { $count } ronde dan lolos! Permainan yang bagus.
pusoydos-you-last-player = Anda satu-satunya pemain yang tersisa. Permainan berakhir!
pusoydos-last-player = { $player } satu-satunya pemain yang tersisa. Permainan berakhir!
pusoydos-players-remaining = Tersisa { $count } { $count ->
    [one] pemain
   *[other] pemain
}.
pusoydos-you-round-loser = Anda finis terakhir dan mendapat satu catatan kalah. Total { $count } { $count ->
    [one] kekalahan
   *[other] kekalahan
}.
pusoydos-round-loser = { $player } finis terakhir dan mendapat satu catatan kalah. Total { $count } { $count ->
    [one] kekalahan
   *[other] kekalahan
}.
pusoydos-you-losses-game-over = Anda mencapai { $count } kekalahan dan kalah dalam permainan!
pusoydos-losses-game-over = { $player } mencapai { $count } kekalahan dan kalah dalam permainan!
pusoydos-penalty-entry = { $points } { $points ->
    [one] poin
   *[other] poin
} dari { $player }
pusoydos-you-penalty-summary = Anda memenangkan ronde: { $breakdown }. Mendapat { $gained } pada ronde ini, total { $total }.
pusoydos-penalty-summary = { $player } memenangkan ronde: { $breakdown }. Mendapat { $gained } pada ronde ini, total { $total }.
pusoydos-you-win-round = Anda memenangkan ronde!
pusoydos-round-winner = { $player } memenangkan ronde!
pusoydos-you-go-out = Kartu Anda habis!
pusoydos-player-goes-out = Kartu { $player } habis!
pusoydos-you-points-winner = Anda mencapai { $score } poin dan memenangkan permainan!
pusoydos-points-winner = { $player } mencapai { $score } poin dan memenangkan permainan!
pusoydos-you-points-elim-penalty = Anda mendapat { $points } poin penalti. Total { $total }.
pusoydos-points-elim-penalty = { $player } mendapat { $points } poin penalti. Total { $total }.
pusoydos-you-points-elim-eliminated = Anda mencapai { $score } poin dan tersingkir!
pusoydos-points-elim-eliminated = { $player } mencapai { $score } poin dan tersingkir!
pusoydos-you-points-elim-winner = Hanya Anda yang masih bertahan. Anda menang!
pusoydos-points-elim-winner = Hanya { $player } yang masih bertahan. { $player } menang!
pusoydos-you-instant-win-dragon = Anda memiliki Dragon, urutan 13 kartu! Anda langsung menang!
pusoydos-instant-win-dragon = { $player } memiliki Dragon, urutan 13 kartu! Langsung menang!
pusoydos-you-instant-win-four-twos = Anda memiliki keempat kartu 2! Anda langsung menang!
pusoydos-instant-win-four-twos = { $player } memiliki keempat kartu 2! Langsung menang!
pusoydos-you-instant-win-six-pairs = Anda memiliki enam pasangan! Anda langsung menang!
pusoydos-instant-win-six-pairs = { $player } memiliki enam pasangan! Langsung menang!
pusoydos-checking-instant-wins = Memeriksa susunan kartu untuk menang langsung.
pusoydos-no-instant-wins = Tidak ada yang menang langsung pada ronde ini.
pusoydos-passing-phase = Tahap pertukaran kartu.
pusoydos-loser-gives = { $loser } memberikan { $count ->
    [one] kartu tertingginya
   *[other] { $count } kartu tertingginya
} kepada { $winner }.
pusoydos-you-give-highest = Anda memberikan { $count ->
    [one] kartu tertinggi Anda
   *[other] { $count } kartu tertinggi Anda
} kepada { $winner }.
pusoydos-winner-gives-back = { $winner } mengembalikan { $count ->
    [one] satu kartu
   *[other] { $count } kartu
} kepada { $loser }.
pusoydos-select-cards-to-give = Pilih { $count ->
    [one] 1 kartu
   *[other] { $count } kartu
} untuk dikembalikan kepada { $recipient }:
pusoydos-cards-exchanged = Pertukaran kartu selesai.
pusoydos-passed-cards = Anda memberikan { $cards } kepada { $recipient }.
pusoydos-received-cards = Anda menerima { $cards } dari { $sender }.
pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (dipilih)
pusoydos-play-none = Pilih kartu yang akan dimainkan.
pusoydos-play-invalid = Kombinasi tidak sah.
pusoydos-play-combo = Mainkan { $combo }
pusoydos-pass = Lewat
pusoydos-check-trick = Periksa adu kartu
pusoydos-read-hand = Bacakan kartu di tangan
pusoydos-check-turn-timer = Periksa waktu giliran
pusoydos-read-card-counts = Jumlah kartu
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] kartu
   *[other] kartu
}
pusoydos-card-counts-empty = Tidak ada pemain aktif dengan kartu yang bisa dihitung.
pusoydos-timer-disabled = Batas waktu giliran dinonaktifkan.
pusoydos-timer-remaining = Tersisa { $seconds } detik.
pusoydos-key-play = Mainkan kartu yang dipilih
pusoydos-key-pass = Lewat
pusoydos-key-trick = Periksa adu kartu saat ini
pusoydos-key-hand = Bacakan kartu Anda
pusoydos-key-counts = Jumlah kartu
pusoydos-key-timer = Waktu giliran
pusoydos-error-full-passing-players = Pertukaran kartu lengkap memerlukan tepat 2 atau 4 pemain.
pusoydos-error-instant-wins-card-passing = Menang langsung dan pertukaran kartu tidak dapat digunakan bersamaan. Nonaktifkan salah satunya sebelum memulai permainan.
pusoydos-error-no-cards = Anda belum memilih kartu.
pusoydos-error-invalid-combo = Kartu yang dipilih tidak membentuk kombinasi yang sah.
pusoydos-error-first-turn-3c = Anda harus menyertakan 3 keriting dalam kombinasi pembuka permainan.
pusoydos-error-wrong-length = Anda harus memainkan tepat { $count } { $count ->
    [one] kartu
   *[other] kartu
} untuk mengalahkan kombinasi di meja.
pusoydos-error-lower-combo = Kombinasi Anda lebih rendah daripada kombinasi di meja.
pusoydos-error-must-play = Anda tidak boleh lewat saat membuka adu kartu baru.
pusoydos-error-select-cards-to-give = Pilih tepat { $count } { $count ->
    [one] kartu
   *[other] kartu
} untuk dikembalikan kepada { $recipient }.
pusoydos-error-select-required-give-cards = Pilih kartu sesuai jumlah yang diminta sebelum mengonfirmasi pertukaran.
pusoydos-error-eliminated = Anda sudah keluar dari permainan ini.
pusoydos-confirm-pass = Pilih Lewat sekali lagi untuk mengonfirmasi.
pusoydos-you-play-single = Anda memainkan { $card }.
pusoydos-player-plays-single = { $player } memainkan { $card }.
pusoydos-you-play-combo = Anda memainkan { $combo } dengan kartu { $cards }.
pusoydos-player-plays-combo = { $player } memainkan { $combo } dengan kartu { $cards }.
pusoydos-you-pass = Anda lewat.
pusoydos-player-passes = { $player } lewat.
pusoydos-you-win-trick = Anda memenangkan adu kartu.
pusoydos-trick-won = { $player } memenangkan adu kartu.
pusoydos-trick-empty = Belum ada kartu dalam adu kartu ini.
pusoydos-trick-status = { $player } memainkan { $combo } dengan kartu { $cards }.
pusoydos-your-hand = Kartu Anda: { $cards }.
pusoydos-score-no-scores = Belum ada skor.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] kemenangan
   *[other] kemenangan
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] kekalahan
   *[other] kekalahan
}
pusoydos-score-points = { $player }: { $score } poin
pusoydos-you-one-card = Kartu Anda tinggal satu!
pusoydos-one-card = Kartu { $player } tinggal satu!
pusoydos-combo-single = Kartu Tunggal
pusoydos-combo-pair = Pasangan
pusoydos-combo-three_of_a_kind = Three of a Kind
pusoydos-combo-straight = Straight
pusoydos-combo-flush = Flush
pusoydos-combo-full_house = Full House
pusoydos-combo-four_of_a_kind = Four of a Kind
pusoydos-combo-straight_flush = Straight Flush
pusoydos-combo-dragon = Dragon
pusoydos-combo-four_twos = Empat Kartu Dua
pusoydos-combo-six_pairs = Enam Pasangan
pusoydos-game-over = Permainan berakhir! { $player } kalah!
pusoydos-game-over-points = Permainan berakhir! { $player } menang dengan { $score } poin!
pusoydos-game-over-losses = Permainan berakhir! { $player } kalah dengan { $count } kekalahan!
pusoydos-line-format = { $rank }. { $player }: { $score } poin
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] kemenangan
   *[other] kemenangan
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] kekalahan
   *[other] kekalahan
}
