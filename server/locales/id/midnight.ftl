game-name-midnight = 1-4-24
midnight-roll = Lempar dadu
midnight-bank = Catat skor
midnight-check-dice = Bacakan dadu saat ini
midnight-check-round-status = Lihat status ronde
midnight-round-start = Ronde { $round } dari { $total }.
midnight-round-start-brief = Ronde { $round } dari { $total }.
midnight-you-rolled = Hasil lemparan Anda: { $dice }.
midnight-player-rolled = Hasil lemparan { $player }: { $dice }.
midnight-you-rolled-brief = Lemparan Anda: { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.
midnight-you-keep = Anda menyimpan dadu ke-{ $index } dengan angka { $die }.
midnight-player-keeps = { $player } menyimpan dadu ke-{ $index } dengan angka { $die }.
midnight-you-keep-brief = Anda menyimpan { $die }.
midnight-player-keeps-brief = { $player } menyimpan { $die }.
midnight-you-unkeep = Anda melepas dadu ke-{ $index } dengan angka { $die } untuk dilempar ulang.
midnight-player-unkeeps = { $player } melepas dadu ke-{ $index } dengan angka { $die } untuk dilempar ulang.
midnight-you-unkeep-brief = Anda memilih untuk melempar ulang { $die }.
midnight-player-unkeeps-brief = { $player } memilih untuk melempar ulang { $die }.
midnight-you-scored = Anda memenuhi syarat dengan angka 1 dan 4, menghasilkan { $score } poin dari { $scoring_dice }.
midnight-scored = { $player } memenuhi syarat dengan angka 1 dan 4, menghasilkan { $score } poin dari { $scoring_dice }.
midnight-you-scored-brief = Anda mendapat { $score } poin.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = Anda tidak memenuhi syarat karena belum mendapat { $missing }.
midnight-player-disqualified = { $player } tidak memenuhi syarat karena belum mendapat { $missing }.
midnight-you-disqualified-brief = Anda belum mendapat { $missing }.
midnight-player-disqualified-brief = { $player } belum mendapat { $missing }.
midnight-you-win-round = Anda memenangi ronde { $round } dengan skor { $score }.
midnight-round-winner = { $player } memenangi ronde { $round } dengan skor { $score }.
midnight-you-win-round-brief = Anda memenangi ronde { $round }: { $score }.
midnight-round-winner-brief = { $player } memenangi ronde { $round }: { $score }.
midnight-round-tie = Ronde berakhir seri dengan skor { $score } antara { $players }. Tidak ada yang mendapat kemenangan ronde.
midnight-all-disqualified = Tidak ada pemain yang memenuhi syarat angka 1 dan 4. Tidak ada yang mendapat kemenangan ronde.
midnight-all-disqualified-brief = Tidak ada yang memenuhi syarat.
midnight-you-win-game = Anda memenangi permainan dengan { $wins } { $wins ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}!
midnight-game-winner = { $player } memenangi permainan dengan { $wins } { $wins ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}!
midnight-you-win-game-brief = Anda menang: { $wins }.
midnight-game-winner-brief = { $player } menang: { $wins }.
midnight-game-tie = Permainan berakhir seri. { $players } masing-masing meraih { $wins } { $wins ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}.
midnight-set-rounds = Jumlah ronde: { $rounds }
midnight-enter-rounds = Masukkan jumlah ronde yang akan dimainkan:
midnight-option-changed-rounds = Jumlah ronde diubah menjadi { $rounds }
midnight-desc-rounds = Jumlah ronde Midnight sebelum skor akhir dihitung. Nilai bawaan 5, dari 1 sampai 20.
midnight-error-rounds-out-of-range = Midnight mendukung { $min } sampai { $max } ronde. Pengaturan saat ini: { $rounds }.
midnight-need-to-roll = Lempar dadu sebelum memilih dadu untuk disimpan.
midnight-no-dice-to-keep = Tidak ada lagi dadu yang dapat dilempar atau disimpan.
midnight-must-keep-one = Simpan setidaknya satu dadu dari lemparan terbaru sebelum melempar lagi.
midnight-must-roll-first = Lempar dadu sebelum mencatat skor giliran.
midnight-keep-all-first = Tentukan pilihan untuk setiap dadu sebelum mencatat skor. Simpan atau lepas semua dadu yang belum terkunci terlebih dahulu.
midnight-invalid-die-index = Dadu tersebut tidak tersedia dalam lemparan ini.
midnight-die-locked = { $value } (terkunci)
midnight-die-kept = { $value } (disimpan)
midnight-die-value = { $value }
midnight-die-index = Dadu ke-{ $index }
midnight-your-dice-not-rolled = Anda belum melempar pada giliran ini.
midnight-player-dice-not-rolled = { $player } belum melempar pada giliran ini.
midnight-your-dice-status =
    { $qualified ->
        [yes] Dadu Anda: { $dice }. Terkunci: { $locked }, disimpan untuk lemparan berikutnya: { $kept }, masih dapat dilempar: { $remaining }. Skor jika dicatat sekarang adalah { $score } dari { $scoring_dice } dan sudah memenuhi syarat.
       *[no] Dadu Anda: { $dice }. Terkunci: { $locked }, disimpan untuk lemparan berikutnya: { $kept }, masih dapat dilempar: { $remaining }. Anda masih memerlukan { $missing } untuk memenuhi syarat.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] Dadu { $player }: { $dice }. Terkunci: { $locked }, disimpan untuk lemparan berikutnya: { $kept }, masih dapat dilempar: { $remaining }. Skor jika dicatat sekarang adalah { $score } dari { $scoring_dice } dan sudah memenuhi syarat.
       *[no] Dadu { $player }: { $dice }. Terkunci: { $locked }, disimpan untuk lemparan berikutnya: { $kept }, masih dapat dilempar: { $remaining }. Masih memerlukan { $missing } untuk memenuhi syarat.
    }
midnight-status-round = Ronde { $round } dari { $total }
midnight-status-current-player = Giliran saat ini: { $player }
midnight-status-current-not-rolled = { $player } belum melempar.
midnight-status-current-dice =
    { $qualified ->
        [yes] Dadu { $player } saat ini: { $dice }. Potensi skor: { $score } dari { $scoring_dice }. Terkunci { $locked }, disimpan { $kept }, masih dapat dilempar { $remaining }.
       *[no] Dadu { $player } saat ini: { $dice }. Masih memerlukan { $missing }. Terkunci { $locked }, disimpan { $kept }, masih dapat dilempar { $remaining }.
    }
midnight-status-dice-not-rolled = belum dilempar
midnight-status-last-qualified = Giliran terakhir: hasil lemparan { $player } adalah { $dice }, menghasilkan { $score } poin.
midnight-status-last-disqualified = Giliran terakhir: hasil lemparan { $player } adalah { $dice } dan tidak memenuhi syarat.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } kemenangan ronde. Skor ronde ini { $current }, memenuhi syarat.
       *[no] { $rank }. { $player }: { $wins } kemenangan ronde. Skor ronde ini { $current }, tidak memenuhi syarat.
    }
midnight-score-unit-round-wins = { $count ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] kemenangan ronde
   *[other] kemenangan ronde
}
