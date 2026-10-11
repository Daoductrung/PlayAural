game-name-farkle = Farkle

farkle-roll = Lempar { $count } { $count ->
    [one] dadu
   *[other] dadu
}
farkle-bank = Amankan { $points } poin
farkle-take-single-one = Satu dadu angka 1, { $points } poin
farkle-take-single-five = Satu dadu angka 5, { $points } poin
farkle-take-three-kind = Tiga dadu angka { $number }, { $points } poin
farkle-take-four-kind = Empat dadu angka { $number }, { $points } poin
farkle-take-five-kind = Lima dadu angka { $number }, { $points } poin
farkle-take-six-kind = Enam dadu angka { $number }, { $points } poin
farkle-take-small-straight = Urutan pendek, { $points } poin
farkle-take-large-straight = Urutan panjang, { $points } poin
farkle-take-three-pairs = Tiga pasang, { $points } poin
farkle-take-double-triplets = Dua kelompok tiga angka sama, { $points } poin
farkle-take-full-house = Empat angka sama dan sepasang, { $points } poin
farkle-you-roll = Anda melempar { $count } { $count ->
    [one] dadu
   *[other] dadu
}.
farkle-player-rolls = { $player } melempar { $count } { $count ->
    [one] dadu
   *[other] dadu
}.
farkle-you-roll-brief = Anda melempar { $count } dadu.
farkle-player-rolls-brief = { $player } melempar { $count } dadu.
farkle-roll-result = Hasil dadu: { $dice }.
farkle-roll-result-brief = Dadu: { $dice }.
farkle-you-farkle = Farkle! Anda kehilangan { $points } poin giliran ini.
farkle-player-farkles = Farkle! { $player } kehilangan { $points } poin giliran ini.
farkle-you-farkle-brief = Farkle. Anda kehilangan { $points } poin.
farkle-player-farkles-brief = Farkle. { $player } kehilangan { $points } poin.
farkle-you-take-combo = Anda menyimpan { $combo } senilai { $points } poin.
farkle-player-takes-combo = { $player } menyimpan { $combo } senilai { $points } poin.
farkle-you-take-combo-brief = Anda: { $combo }, tambah { $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }, tambah { $points }.
farkle-you-hot-dice = Hot dice! Keenam dadu Anda menghasilkan poin. Anda boleh melempar keenamnya lagi.
farkle-player-hot-dice = Hot dice! Keenam dadu { $player } menghasilkan poin dan boleh dilempar lagi.
farkle-you-hot-dice-brief = Anda mendapat hot dice.
farkle-player-hot-dice-brief = { $player } mendapat hot dice.
farkle-you-bank = Anda mengamankan { $points } poin. Total Anda kini { $total }.
farkle-player-banks = { $player } mengamankan { $points } poin. Totalnya kini { $total }.
farkle-you-bank-brief = Anda mengamankan { $points } poin. Total { $total }.
farkle-player-banks-brief = { $player } mengamankan { $points } poin. Total { $total }.
farkle-you-win = Anda menang dengan { $score } poin!
farkle-winner = { $player } menang dengan { $score } poin!
farkle-you-win-brief = Anda menang: { $score }.
farkle-winner-brief = { $player } menang: { $score }.
farkle-winners-tie = Skor seri setelah mencapai target! Pemain yang mengikuti babak penentuan: { $players }.
farkle-tiebreaker-round-start = Babak penentuan ke-{ $round }. Pemain yang masih bertanding: { $players }.
farkle-your-turn-score = Anda memiliki { $points } poin pada giliran ini.
farkle-turn-score = { $player } memiliki { $points } poin pada giliran ini.
farkle-no-turn = Saat ini tidak ada pemain yang sedang mendapat giliran.
farkle-set-target-score = Target skor: { $score }
farkle-enter-target-score = Masukkan target skor, dari 500 sampai 5000:
farkle-option-changed-target = Target skor diatur menjadi { $score }.
farkle-desc-target-score = Skor yang memicu giliran terakhir Farkle dan memberi peluang untuk menang. Nilai bawaan 1000, dari 500 sampai 5000.
farkle-set-entrance-score = Minimum skor pertama: { $score }
farkle-enter-entrance-score = Masukkan minimum skor pertama, dari 0 sampai 5000:
farkle-option-changed-entrance = Minimum skor pertama diatur menjadi { $score }.
farkle-desc-min-entrance-score = Poin giliran minimum untuk mengamankan skor pertama. Nilainya tidak boleh melebihi target skor. Nilai bawaan 50, dari 0 sampai 5000.
farkle-set-bank-score = Minimum poin untuk diamankan: { $score }
farkle-enter-bank-score = Masukkan minimum poin untuk diamankan, dari 0 sampai 5000:
farkle-option-changed-bank = Minimum poin untuk diamankan diatur menjadi { $score }.
farkle-desc-min-bank-score = Poin giliran minimum untuk mengamankan poin setelah pemain memiliki skor. Nilainya tidak boleh melebihi target skor. Nilai bawaan 30, dari 0 sampai 5000.
farkle-error-entrance-above-target = Minimum skor pertama, { $entrance }, tidak boleh melebihi target skor { $target }.
farkle-error-bank-above-target = Minimum poin untuk diamankan, { $bank }, tidak boleh melebihi target skor { $target }.
farkle-must-take-combo = Simpan setidaknya satu dadu atau kombinasi yang menghasilkan poin sebelum melempar lagi.
farkle-cannot-bank = Anda hanya dapat mengamankan poin setelah menyimpan dadu atau kombinasi yang menghasilkan poin pada giliran ini.
farkle-must-reach-entrance-score = Anda memerlukan setidaknya { $points } poin giliran untuk mengamankan skor pertama.
farkle-must-reach-bank-score = Anda memerlukan setidaknya { $points } poin giliran sebelum dapat mengamankan poin.
farkle-confirm-risky-roll = Anda bisa mengamankan { $points } poin sekarang. Melempar lagi berisiko menghanguskannya. Ulangi tindakan Lempar dalam { $seconds } detik untuk mengonfirmasi.
farkle-invalid-combo-action = Pilihan skor tersebut tidak dikenali. Pilih salah satu kombinasi yang tersedia saat ini.
farkle-combo-no-longer-available = Kombinasi tersebut tidak lagi tersedia. Pilihan kombinasi penghasil poin telah diperbarui.
farkle-combo-single-1 = Satu dadu angka 1
farkle-combo-single-5 = Satu dadu angka 5
farkle-combo-three-kind = Tiga dadu angka { $number }
farkle-combo-four-kind = Empat dadu angka { $number }
farkle-combo-five-kind = Lima dadu angka { $number }
farkle-combo-six-kind = Enam dadu angka { $number }
farkle-combo-small-straight = Urutan pendek
farkle-combo-large-straight = Urutan panjang
farkle-combo-three-pairs = Tiga pasang
farkle-combo-double-triplets = Dua kelompok tiga angka sama
farkle-combo-full-house = Empat angka sama dan sepasang
farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo }, { $points } poin
farkle-check-turn-score = Periksa skor giliran
farkle-roll-label = Lempar dadu
farkle-bank-label = Amankan poin
