game-name-bunko = Bunko
bunko-roll = Lempar dadu
bunko-check-status = Periksa status
bunko-check-last-roll = Periksa lemparan terakhir
bunko-game-start = Bunko dimulai. Pemain: { $players }.
bunko-round-start = Ronde { $round } dari { $total_rounds }. Angka target ronde ini adalah { $target }.
bunko-round-start-brief = Ronde { $round } dari { $total_rounds }. Target { $target }.
bunko-you-win-round = Anda memenangi ronde { $round } dengan { $score } poin untuk angka target { $target }.
bunko-player-wins-round = { $player } memenangi ronde { $round } dengan { $score } poin untuk angka target { $target }.
bunko-you-win-round-brief = Anda memenangi ronde { $round }: { $score }.
bunko-player-wins-round-brief = { $player } memenangi ronde { $round }: { $score }.
bunko-you-roll-match = Hasil lemparan Anda { $dice }, menghasilkan { $points } { $points ->
    [one] poin
   *[other] poin
} untuk angka target { $target }. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-player-rolls-match = Hasil lemparan { $player } adalah { $dice }, menghasilkan { $points } { $points ->
    [one] poin
   *[other] poin
} untuk angka target { $target }. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-you-roll-match-brief = Anda: { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-player-rolls-match-brief = { $player }: { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-you-roll-mini_bunko = Hasil lemparan Anda { $dice }. Ketiga dadu sama tetapi bukan angka target { $target }, sehingga Anda mendapat mini Bunko senilai { $points } poin. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-player-rolls-mini_bunko = Hasil lemparan { $player } adalah { $dice }. Ketiga dadu sama tetapi bukan angka target { $target }, sehingga menghasilkan mini Bunko senilai { $points } poin. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-you-roll-mini_bunko-brief = Anda: mini Bunko { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-player-rolls-mini_bunko-brief = { $player }: mini Bunko { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-you-roll-bunko = Hasil lemparan Anda { $dice }. Bunko! Tiga dadu dengan angka target { $target } menghasilkan { $points } poin. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-player-rolls-bunko = Hasil lemparan { $player } adalah { $dice }. Bunko! Tiga dadu dengan angka target { $target } menghasilkan { $points } poin. Skor ronde: { $round_total }. Skor keseluruhan: { $total }.
bunko-you-roll-bunko-brief = Anda: Bunko { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-player-rolls-bunko-brief = { $player }: Bunko { $dice }, tambah { $points }. Skor ronde { $round_total }, total { $total }.
bunko-you-roll-no_score = Hasil lemparan Anda { $dice }. Tidak ada dadu dengan angka target { $target } maupun mini Bunko, jadi Anda tidak mendapat poin. Giliran Anda berakhir.
bunko-player-rolls-no_score = Hasil lemparan { $player } adalah { $dice }. Tidak ada dadu dengan angka target { $target } maupun mini Bunko, jadi tidak mendapat poin. Giliran beralih.
bunko-you-roll-no_score-brief = Anda: { $dice }, nol poin. Giliran berakhir.
bunko-player-rolls-no_score-brief = { $player }: { $dice }, nol poin. Giliran beralih.
bunko-last-roll-none = Belum ada lemparan pada ronde ini.
bunko-last-roll-match = Lemparan terakhir { $player } adalah { $dice }, menghasilkan { $points } { $points ->
    [one] poin
   *[other] poin
} untuk angka target { $target }.
bunko-last-roll-match-you = Lemparan terakhir Anda adalah { $dice }, menghasilkan { $points } { $points ->
    [one] poin
   *[other] poin
} untuk angka target { $target }.
bunko-last-roll-mini_bunko = Lemparan terakhir { $player } adalah { $dice }, menghasilkan mini Bunko senilai { $points } poin karena ketiga dadu sama tetapi bukan angka target { $target }.
bunko-last-roll-mini_bunko-you = Lemparan terakhir Anda adalah { $dice }, menghasilkan mini Bunko senilai { $points } poin karena ketiga dadu sama tetapi bukan angka target { $target }.
bunko-last-roll-bunko = Lemparan terakhir { $player } adalah { $dice }, menghasilkan Bunko. Tiga dadu dengan angka target { $target } bernilai { $points } poin.
bunko-last-roll-bunko-you = Lemparan terakhir Anda adalah { $dice }, menghasilkan Bunko. Tiga dadu dengan angka target { $target } bernilai { $points } poin.
bunko-last-roll-no_score = Lemparan terakhir { $player } adalah { $dice }, tanpa poin untuk angka target { $target }.
bunko-last-roll-no_score-you = Lemparan terakhir Anda adalah { $dice }, tanpa poin untuk angka target { $target }.
bunko-status-round = Ronde { $round } dari { $total_rounds }. Angka target: { $target }.
bunko-status-turn = Pemain saat ini: { $player }.
bunko-status-leader = Pemimpin: { $player } dengan { $rounds } { $rounds ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
} dan { $total } poin keseluruhan.
bunko-standings-header = Klasemen. Pemenang ditentukan berdasarkan { $mode }.
bunko-score-line = { $rank }. { $player }: { $rounds } { $rounds ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}, { $total } poin keseluruhan, { $current } pada ronde ini, { $bunkos } { $bunkos ->
    [one] Bunko
   *[other] Bunko
}, { $mini_bunkos } { $mini_bunkos ->
    [one] mini Bunko
   *[other] mini Bunko
}
bunko-roll-already-resolving = Dadu Anda masih bergulir. Tunggu hasilnya sebelum melempar lagi.
bunko-error-round-count-invalid = Bunko memerlukan { $min } sampai { $max } ronde. Pengaturan saat ini adalah { $count }.
bunko-error-winning-mode-invalid = Bunko tidak mendukung cara penentuan pemenang "{ $mode }". Pilih kemenangan ronde atau skor total.
bunko-set-round-count = Jumlah ronde: { $count }
bunko-enter-round-count = Masukkan jumlah ronde:
bunko-option-changed-round-count = Jumlah ronde diubah menjadi { $count }.
bunko-desc-round-count = Jumlah ronde Bunko sebelum pemenang ditentukan. Nilai bawaan 6, dari 1 sampai 12.
bunko-set-winning-mode = Penentuan pemenang: { $mode }
bunko-select-winning-mode = Pilih cara penentuan pemenang:
bunko-option-changed-winning-mode = Penentuan pemenang diubah menjadi { $mode }.
bunko-desc-winning-mode = Tentukan apakah pemenang Bunko diperingkat berdasarkan kemenangan ronde atau skor total.
bunko-winning-mode-round-wins = kemenangan ronde
bunko-winning-mode-total-score = skor total
