game-name-senet = Senet
senet-game-started = { $p1 } menjadi pemain 1, { $p2 } menjadi pemain 2. { $first } mendapat giliran pertama.
senet-throw-you = Anda melempar stik dan mendapat { $result }.{ $bonus ->
    [yes] {" "}Lemparan tambahan!
   *[no] {""}
}
senet-throw-other = { $player } melempar stik dan mendapat { $result }.{ $bonus ->
    [yes] {" "}Lemparan tambahan!
   *[no] {""}
}
senet-move-you = Anda berpindah dari petak { $from } ke petak { $to }.
senet-move-other = { $player } berpindah dari petak { $from } ke petak { $to }.
senet-swap-you = Anda bertukar tempat dengan { $opponent } di petak { $to }. { $opponent } mundur ke petak { $from }.
senet-swap-other = { $player } bertukar tempat dengan { $opponent } di petak { $to }. { $opponent } mundur ke petak { $from }.
senet-bearoff-you = Anda mengeluarkan bidak dari petak { $from }. Tersisa { $remaining } bidak.
senet-bearoff-other = { $player } mengeluarkan bidak dari petak { $from }. Tersisa { $remaining } bidak.
senet-water-you = Anda mendarat di Rumah Air! Bidak dikembalikan ke petak { $dest }.
senet-water-other = { $player } mendarat di Rumah Air! Bidak dikembalikan ke petak { $dest }.
senet-happiness-you = Anda mencapai Rumah Kebahagiaan.
senet-happiness-other = { $player } mencapai Rumah Kebahagiaan.
senet-horus-auto-you = Bidak Anda keluar dari Rumah Horus karena tidak ada lagi bidak Anda di baris pertama. Tersisa { $remaining } bidak.
senet-horus-auto-other = Bidak { $player } keluar dari Rumah Horus karena tidak ada lagi bidaknya di baris pertama. Tersisa { $remaining } bidak.
senet-no-moves-you = Anda tidak memiliki langkah yang sah.
senet-no-moves-other = { $player } tidak memiliki langkah yang sah.
senet-sq-empty = { $sq }
senet-sq-own = { $sq }, milik Anda
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }, milik Anda
senet-sq-opponent-special = { $sq }, { $name }, { $owner }
senet-house-rebirth = Kelahiran Kembali
senet-house-happiness = Kebahagiaan
senet-house-water = Air
senet-house-three-truths = Tiga Kebenaran
senet-house-re-atum = Re-Atum
senet-house-horus = Horus
senet-status = { $p1 }: { $off1 } bidak sudah keluar. { $p2 }: { $off2 } bidak sudah keluar.{ $phase ->
    [throwing] {" "}Menunggu lemparan.
   *[moving] {" "}Hasil lemparan: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = Stik belum dilempar.
senet-wins-you = Anda menang! Semua bidak Anda telah melewati rumah terakhir.
senet-wins-other = { $player } menang! Semua bidaknya telah melewati rumah terakhir.
senet-check-status = Status
senet-check-sticks = Stik
senet-next-piece = Bidak berikutnya
senet-previous-piece = Bidak sebelumnya
senet-score-line = { $player }: { $off } bidak sudah keluar.
senet-not-your-piece = Itu bukan bidak Anda.
senet-no-piece-there = Tidak ada bidak di sana.
senet-no-moves-from-here = Tidak ada langkah yang sah dari petak ini.
senet-need-throw-first = Lempar stik sebelum memilih bidak yang akan dipindahkan.
senet-no-movable-pieces = Tidak ada bidak Anda yang dapat bergerak dengan hasil lemparan ini.
senet-error-exactly-two-players = Senet harus dimainkan oleh tepat 2 pemain aktif. Jumlah pemain aktif saat ini: { $count }.
senet-option-bot-difficulty = Tingkat kesulitan bot: { $bot_difficulty }
senet-option-select-bot-difficulty = Pilih tingkat kesulitan bot
senet-option-changed-bot-difficulty = Tingkat kesulitan bot diatur menjadi { $bot_difficulty }.
senet-desc-bot-difficulty = Tentukan cara bot Senet memilih langkah. Acak memilih langkah secara acak, sedangkan Sederhana mengutamakan langkah taktis yang lebih aman.
senet-difficulty-random = Acak
senet-difficulty-simple = Sederhana
