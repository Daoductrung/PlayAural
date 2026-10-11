game-name-bingo = Bingo
bingo-pattern-line = Satu garis
bingo-pattern-four-corners = Empat sudut
bingo-pattern-letter-x = Huruf X
bingo-pattern-blackout = Seluruh kartu
bingo-call-interval-5 = 5 detik
bingo-call-interval-15 = 15 detik
bingo-call-interval-30 = 30 detik
bingo-call-interval-45 = 45 detik
bingo-call-interval-60 = 60 detik
bingo-set-pattern = Pola kemenangan: { $pattern }
bingo-select-pattern = Pilih pola kemenangan:
bingo-option-changed-pattern = Pola kemenangan kini { $pattern }.
bingo-desc-pattern = Pola yang harus dilengkapi untuk menang. Satu garis berarti satu baris, kolom, atau diagonal penuh. Empat sudut memerlukan keempat petak sudut. Huruf X memerlukan kedua diagonal. Seluruh kartu berarti semua petak harus ditandai.
bingo-set-call-interval = Jeda pengumuman angka: { $seconds }
bingo-select-call-interval = Pilih jeda pengumuman angka:
bingo-option-changed-interval = Target jeda pengumuman angka kini { $seconds }.
bingo-desc-call-interval = Target waktu antara dua pengumuman angka. Permainan selalu menyediakan waktu singkat untuk menyerukan Bingo, jadi jeda tercepat mungkin sedikit lebih lama.
bingo-cell-free = Petak bebas di tengah, ditandai otomatis.
bingo-cell-marked = { $letter } { $number }, sudah ditandai.
bingo-cell-unmarked = { $letter } { $number }, belum ditandai.
bingo-cell-is-free = Petak bebas di tengah sudah ditandai.
bingo-you-already-won = Anda sudah meraih Bingo pada ronde ini.
bingo-you-mark = { $letter } { $number } ditandai.
bingo-you-unmark = Tanda pada { $letter } { $number } dihapus.
bingo-claim-bingo = Serukan Bingo!
bingo-repeat-call = Ulangi angka terakhir
bingo-check-called = Lihat angka yang sudah diumumkan
bingo-no-calls-yet = Belum ada angka yang diumumkan.
bingo-claim-in-progress = Seruan Bingo pemain lain sedang diperiksa. Coba lagi sebentar.
bingo-claim-in-progress-you = Seruan Bingo Anda sedang diperiksa.
bingo-claim-wait-for-call = Tunggu hingga angka yang sedang diundi diumumkan, lalu coba lagi.
bingo-claim-unchanged = Kartu Anda belum berubah sejak pemeriksaan terakhir yang gagal. Ubah tanda atau tunggu angka berikutnya sebelum menyerukan Bingo lagi.
bingo-checking-claim-you = Anda menyerukan Bingo! Kartu Anda sedang diperiksa.
bingo-checking-claim = { $player } menyerukan Bingo! Kartunya sedang diperiksa.
bingo-whose-turn-checking = Kartu { $player } sedang diperiksa.
bingo-whose-turn-checking-you = Kartu Anda sedang diperiksa.
bingo-whose-turn-checking-card = Sebuah kartu Bingo sedang diperiksa.
bingo-whose-turn-drawing = Angka berikutnya sedang diundi.
bingo-whose-turn-waiting = { $seconds ->
    [one] Angka berikutnya dalam { $seconds } detik.
   *[other] Angka berikutnya dalam { $seconds } detik.
}
bingo-claim-incorrect-you = Kartu Anda belum memenuhi syarat Bingo.
bingo-claim-incorrect = Kartu { $player } belum memenuhi syarat Bingo.
bingo-claim-incomplete-you = Kartu Anda belum melengkapi pola kemenangan.
bingo-claim-incomplete = Kartu { $player } belum melengkapi pola kemenangan.
bingo-marked-number-not-called = Anda menandai { $letter } { $number }, tetapi angka itu belum diumumkan.
bingo-last-call = Angka terakhir: { $letter } { $number }
bingo-status-called-count = Sudah diumumkan: { $count } dari { $total } angka.
bingo-status-called-entry = { $letter } { $number }
bingo-game-start = Bingo dimulai! Pola kemenangannya { $pattern }. Angka diumumkan dengan target jeda { $interval } detik, disertai waktu untuk menyerukan Bingo setelah setiap angka. Tandai kartu Anda, lalu tekan B saat siap.
bingo-game-start-touch = Bingo dimulai! Pola kemenangannya { $pattern }. Angka diumumkan dengan target jeda { $interval } detik, disertai waktu untuk menyerukan Bingo setelah setiap angka. Tandai kartu Anda, lalu gunakan gestur tekan lama perangkat Anda pada kartu atau pilih Serukan Bingo.
bingo-game-start-spectator = Bingo dimulai! Pola kemenangannya { $pattern }. Angka diumumkan dengan target jeda { $interval } detik, disertai waktu bagi pemain untuk menyerukan Bingo setelah setiap angka.
bingo-number-called = { $letter } { $number }
bingo-claim-correct-you = Bingo! Anda menang dengan { $numbers }!
bingo-claim-correct = Bingo! { $player } menang dengan { $numbers }!
bingo-claim-correct-no-numbers-you = Bingo! Anda menang!
bingo-claim-correct-no-numbers = Bingo! { $player } menang!
bingo-deck-exhausted = Seluruh 75 angka sudah diumumkan dan belum ada seruan Bingo yang sah. Ronde berakhir tanpa pemenang.
bingo-error-invalid-interval = "{ $value }" bukan jeda pengumuman yang valid.
bingo-error-invalid-pattern = { $value } bukan pola kemenangan yang dikenal.
bingo-end-calls = { $count ->
    [one] { $count } angka diumumkan pada ronde ini.
   *[other] { $count } angka diumumkan pada ronde ini.
}
bingo-end-winner-line = Pemenang: { $player }
bingo-end-no-winner = Tidak ada seruan Bingo yang sah pada ronde ini.
