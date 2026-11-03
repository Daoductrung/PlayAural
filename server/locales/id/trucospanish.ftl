# Options
trucospanish-length-18 = 18 poin per came
trucospanish-length-24 = 24 poin per came
trucospanish-set-length = Panjang came: { $mode }
trucospanish-select-length = Pilih panjang came:
trucospanish-option-changed-length = Panjang came kini { $mode }.
trucospanish-desc-length = Permainan dimenangkan dengan memenangkan dua came. Satu came dimainkan sampai jumlah poin yang dipilih: 24 seperti pada kejuaraan Falles di València dan turnamen Universitat Politècnica de València, atau 18 seperti pada turnamen Torrent dan deskripsi Museu d'Història de València. Ketika sebuah pihak mencapainya, pihak itu memenangkan came dan kedua skor kembali mulai dari nol. La falta bernilai sebanyak poin yang masih dibutuhkan pihak yang memimpin untuk menyelesaikan came, dan Joc fora memenangkan seluruh permainan.
trucospanish-desc-team-mode = Perorangan adalah permainan satu lawan satu untuk 2 pemain. 2v2 menggunakan 4 pemain; rekan berbagi skor dan boleh memanggil untuk seluruh tim.

# Calls
trucospanish-call-truc = Truc
trucospanish-call-retruc = Retruc
trucospanish-call-quatre-val = Quatre val
trucospanish-call-joc-fora = Joc fora
trucospanish-call-envit = Envit
trucospanish-call-torna = Torna
trucospanish-call-la-falta = La falta

# Actions and messages
trucospanish-action-accept = Vull (terima)
trucospanish-action-decline = No vull (tolak)
trucospanish-action-mazo = Me'n vaig (tinggalkan ronde ini)
trucospanish-accept-you = Anda mengatakan Vull untuk { $call }.
trucospanish-accept-player = { $player } mengatakan Vull untuk { $call }.
trucospanish-decline-you = Anda mengatakan No vull untuk { $call }.
trucospanish-decline-player = { $player } mengatakan No vull untuk { $call }.
trucospanish-mazo-you = Anda mengatakan Me'n vaig dan melepaskan ronde ini untuk seluruh tim Anda.
trucospanish-mazo-player = { $player } mengatakan Me'n vaig dan melepaskan ronde ini untuk seluruh tim.
trucospanish-reason-truc = Truc
trucospanish-reason-envit = Envit
trucospanish-game-start = Truco Spanyol dimulai. Menangkan dua came sebesar { $points } poin untuk memenangkan permainan.
trucospanish-desc-mazo = Lepaskan ronde ini untuk seluruh tim Anda. Pihak lawan mendapat nilai ronde saat ini.
trucospanish-came-you = Anda memenangkan satu came! Anda punya { $cames } { $cames ->
    [one] came
   *[other] came
}. Skor kembali mulai dari nol.
trucospanish-came-player = { $player } memenangkan satu came dan punya { $cames } { $cames ->
    [one] came
   *[other] came
}. Skor kembali mulai dari nol.
trucospanish-came-your-team = Tim Anda memenangkan satu came! Anda punya { $cames } { $cames ->
    [one] came
   *[other] came
}. Skor kembali mulai dari nol.
trucospanish-came-team = { $team } memenangkan satu came dan punya { $cames } { $cames ->
    [one] came
   *[other] came
}. Skor kembali mulai dari nol.

trucospanish-pending-answer = { $player } memanggil { $call }. Jawab dengan Vull atau No vull, atau naikkan.
trucospanish-error-answer-first = Anda harus menjawab { $call } sebelum melakukan hal lain. Pilih Vull atau No vull, atau naikkan.
trucospanish-error-raise-max = Joc fora sudah menjadi panggilan tertinggi dan tidak bisa dinaikkan lagi.
trucospanish-error-bad-count = Truco Spanyol membutuhkan 2 atau 4 pemain, tetapi saat ini ada { $count }.
trucospanish-error-team-mode-count = Mode tim { $mode } tidak bisa digunakan dengan { $count } pemain. Gunakan Perorangan untuk 2 pemain atau 2v2 untuk 4 pemain.
trucospanish-status-envit-open = Envit masih bisa dipanggil di ronde ini.
trucospanish-status-envit-closed = Envit sudah ditutup untuk ronde ini.
trucospanish-status-no-truc = Belum ada Truc yang dipanggil. Ronde ini bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.
trucospanish-falta-value = La falta bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.
trucospanish-reveal-envit-you = Envit dimenangkan dengan kartu Anda: { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.
trucospanish-reveal-envit-player = Envit dimenangkan oleh { $player } dengan { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.
trucospanish-error-envit-late = Envit hanya bisa dipanggil sebelum Anda memainkan kartu pertama.
trucospanish-error-envit-closed = Envit sudah ditutup karena Truc sudah diterima.
trucospanish-error-envit-done = Envit sudah dimainkan di ronde ini.
trucospanish-error-envit-cannot-raise = { $call } tidak bisa ditambahkan ke envit yang sedang dimainkan.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] poin
   *[other] poin
} di came ini, { $cames } { $cames ->
    [one] came
   *[other] came
} dimenangkan
trucospanish-game-win-you = Anda memenangkan permainan dengan { $cames } { $cames ->
    [one] came
   *[other] came
}!
trucospanish-game-win-player = { $player } memenangkan permainan dengan { $cames } { $cames ->
    [one] came
   *[other] came
}.
trucospanish-game-win-your-team = Tim Anda memenangkan permainan dengan { $cames } { $cames ->
    [one] came
   *[other] came
}!
trucospanish-game-win-team = { $team } memenangkan permainan dengan { $cames } { $cames ->
    [one] came
   *[other] came
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] came
   *[other] came
}
trucospanish-cames-line = { $team }: { $cames } { $cames ->
    [one] came
   *[other] came
} dimenangkan
