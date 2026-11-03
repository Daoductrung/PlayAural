game-name-truco = Truco

# Options
truco-set-variant = Varian: { $mode }
truco-select-variant = Pilih varian Truco:
truco-option-changed-variant = Varian kini { $mode }.
truco-desc-variant = Truco Argentina menggunakan dek Spanyol 40 kartu, dengan envido dan flor sebagai pilihan. Truco Brasil (Paulista) menggunakan dek Prancis dengan satu kartu yang dibuka, yaitu vira, yang menentukan kartu terkuat, dan kenaikan senilai 3, 6, 9, dan 12 poin. Truco Spanyol (Truc Valencia) menggunakan dek 22 kartu dengan envit dan Joc fora, yang bernilai seluruh permainan.
truco-variant-argentine = Truco Argentina
truco-variant-brazilian = Truco Brasil
truco-variant-spanish = Truco Spanyol
truco-length-15 = 15 poin
truco-length-30 = 30 poin
truco-set-length = Panjang permainan: { $mode }
truco-select-length = Pilih panjang permainan:
truco-option-changed-length = Panjang permainan kini { $mode }.
truco-desc-length = Dalam permainan 15 poin, pihak pertama yang mencapai 15 poin menang. Dalam permainan 30 poin, poin 1 sampai 15 adalah malas (babak pertama) dan poin 16 sampai 30 adalah buenas (babak kedua); pihak pertama yang mencapai 30 menang.
truco-set-flor = Flor: { $enabled }
truco-option-changed-flor = Flor kini { $enabled }.
truco-desc-flor = Jika aktif, pemain yang mendapat tiga kartu dengan jenis yang sama memiliki flor. Flor diumumkan otomatis dan membatalkan envido. Flor bernilai 3 poin, Contraflor 6 poin, dan Contraflor al resto bernilai sebanyak poin yang masih dibutuhkan pihak yang memimpin untuk menang. Hanya pemain yang memiliki flor yang bisa menjawab atau menaikkan. Flor dihitung 20 ditambah nilai ketiga kartunya (kartu gambar bernilai nol), jadi 7, 6, dan 5 dari satu jenis menjadi 38; flor yang lebih tinggi menang. Jika nonaktif, tiga kartu dengan jenis yang sama tidak memiliki nilai khusus.
truco-desc-team-mode = Perorangan adalah permainan satu lawan satu untuk 2 pemain. 2v2 menggunakan 4 pemain dan 3v3 menggunakan 6 pemain; rekan berbagi skor dan boleh memanggil untuk seluruh tim.

# Spanish deck
truco-suit-oros = Koin
truco-suit-copas = Piala
truco-suit-espadas = Pedang
truco-suit-bastos = Pentungan
truco-card-name = { $rank } { $suit }

# Calls
truco-call-truco = Truco
truco-call-retruco = Retruco
truco-call-valecuatro = Vale cuatro
truco-call-envido = Envido
truco-call-real-envido = Real envido
truco-call-falta-envido = Falta envido
truco-call-flor = Flor
truco-call-contraflor = Contraflor
truco-call-contraflor-al-resto = Contraflor al resto

# Actions
truco-action-play-card = { $card }
truco-action-accept = Quiero (terima)
truco-action-decline = No quiero (tolak)
truco-action-mazo = Me voy al mazo (lipat kartu Anda)
truco-read-hand = Baca kartu Anda
truco-read-table = Baca kartu di meja
truco-read-calls = Baca panggilan saat ini

# Game and hand flow
truco-game-start-flor = Truco dimulai dengan flor. Pihak pertama yang mencapai { $points } poin menang.
truco-game-start-no-flor = Truco dimulai tanpa flor. Pihak pertama yang mencapai { $points } poin menang.
truco-hand-start = Ronde { $hand } dimulai. Kartu dibagikan.
truco-dealer-you = Anda yang membagi kartu.
truco-dealer-player = { $player } yang membagi kartu.
truco-mano-you = Anda adalah mano dan bermain pertama.
truco-mano-player = { $player } adalah mano dan bermain pertama.
truco-your-cards = Kartu Anda: { $cards }.
truco-no-cards = Kartu Anda sudah habis.
truco-your-turn = Giliran Anda memainkan kartu.

# Playing cards and tricks
truco-play-you = Anda memainkan { $card }.
truco-play-player = { $player } memainkan { $card }.
truco-trick-win-you = Trik { $trick }: Anda menang dengan { $card }.
truco-trick-win-teammate = Trik { $trick }: rekan Anda { $player } menang dengan { $card }.
truco-trick-win-opponent = Trik { $trick }: { $player } menang dengan { $card } untuk { $team }.
truco-trick-tie = Trik { $trick } seri, disebut parda.

# Calling and answering
truco-call-you = Anda memanggil { $call }.
truco-call-player = { $player } memanggil { $call }.
truco-call-goes-first-you = Anda memanggil { $call }. Envido didahulukan, sebelum Truco dijawab.
truco-call-goes-first-player = { $player } memanggil { $call }. Envido didahulukan, sebelum Truco dijawab.
truco-pending-answer = { $player } memanggil { $call }. Jawab dengan Quiero atau No quiero, atau naikkan.
truco-pending-wait = Menunggu { $team } menjawab { $call }.
truco-accept-you = Anda mengatakan Quiero untuk { $call }.
truco-accept-player = { $player } mengatakan Quiero untuk { $call }.
truco-decline-you = Anda mengatakan No quiero untuk { $call }.
truco-decline-player = { $player } mengatakan No quiero untuk { $call }.
truco-mazo-you = Anda mengatakan Me voy al mazo dan melipat kartu Anda.
truco-mazo-player = { $player } mengatakan Me voy al mazo dan melipat kartunya.
truco-team-folded-your-team = Semua anggota tim Anda sudah melipat kartu.
truco-team-folded-team = Semua anggota { $team } sudah melipat kartu.
truco-flor-announce-you = Anda memiliki flor.
truco-flor-announce-player = { $player } memiliki flor.
truco-flor-cancels-envido = Envido dibatalkan karena ada flor.
truco-reveal-envido-you = Envido dimenangkan dengan kartu Anda: { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.
truco-reveal-envido-player = Envido dimenangkan oleh { $player } dengan { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.
truco-reveal-flor-you = Flor dimenangkan dengan kartu Anda: { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.
truco-reveal-flor-player = Flor dimenangkan oleh { $player } dengan { $cards }, bernilai { $value } { $value ->
    [one] poin
   *[other] poin
}.

# Envido and flor
truco-falta-envido-value = Falta envido bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.
truco-falta-envido-game = Falta envido: kedua pihak masih di malas, jadi pemenangnya memenangkan seluruh permainan.

# Points and score
truco-reason-truco = Truco
truco-reason-envido = Envido
truco-reason-flor = Flor
truco-reason-hand = ronde ini
truco-points-your-team = Tim Anda mendapat { $points } { $points ->
    [one] poin
   *[other] poin
} dari { $reason }.
truco-points-team = { $team } mendapat { $points } { $points ->
    [one] poin
   *[other] poin
} dari { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] poin
   *[other] poin
}.
truco-half-buenas-your-team = Tim Anda memasuki buenas, babak kedua.
truco-half-buenas-team = { $team } memasuki buenas, babak kedua.

# Information
truco-status-no-truco = Belum ada Truco yang dipanggil. Ronde ini bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.
truco-status-truco = Ronde ini berada di { $call }, bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.
truco-status-truco-pending = { $call } menunggu jawaban dari { $team }.
truco-status-envido-open = Envido masih bisa dipanggil di ronde ini.
truco-status-envido-closed = Envido sudah ditutup untuk ronde ini.
truco-table-empty = Belum ada kartu yang dimainkan.
truco-table-trick = Trik { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Errors and disabled-action reasons
truco-error-bad-count = Truco membutuhkan 2, 4, atau 6 pemain, tetapi saat ini ada { $count }.
truco-error-team-mode-count = Mode tim { $mode } tidak bisa digunakan dengan { $count } pemain. Gunakan Perorangan untuk 2 pemain, 2v2 untuk 4 pemain, atau 3v3 untuk 6 pemain.
truco-error-not-your-turn = Sekarang giliran { $player } memainkan kartu.
truco-error-answer-first = Anda harus menjawab { $call } sebelum melakukan hal lain. Pilih Quiero atau No quiero, atau naikkan.
truco-error-nothing-to-answer = Tidak ada panggilan yang menunggu jawaban Anda.
truco-error-own-team-call = Tim Anda yang membuat panggilan itu. Tunggu { $team } menjawab { $call }.
truco-error-envido-late = Envido hanya bisa dipanggil sebelum Anda memainkan kartu pertama.
truco-error-envido-closed = Envido sudah ditutup karena Truco sudah diterima.
truco-error-envido-done = Envido sudah dimainkan di ronde ini.
truco-error-raise-max = Truco sudah mencapai Vale cuatro dan tidak bisa dinaikkan lagi.
truco-error-raise-holder = Tim Anda yang membuat panggilan Truco terakhir. Sekarang hanya { $team } yang bisa menaikkannya.
truco-error-flor-none = Anda sudah melipat kartu di ronde ini, jadi tidak bisa memanggil atau menjawab.
truco-error-flor-holders-only = Hanya pemain yang memiliki flor yang bisa menjawab atau menaikkan flor.
truco-error-card-not-held = Anda tidak memegang kartu itu.
truco-error-hand-over = Ronde ini sudah berakhir.

# Game end
truco-game-win-you = Anda memenangkan permainan dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
truco-game-win-player = { $player } memenangkan permainan dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
truco-game-win-your-team = Tim Anda memenangkan permainan dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
truco-game-win-team = { $team } memenangkan permainan dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
truco-end-title = Hasil Truco
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] poin
   *[other] poin
}.

# Additional errors and individual-mode messages
truco-error-flor-off = Flor dinonaktifkan di permainan ini, jadi tidak ada yang bisa dipanggil atau dijawab.
truco-error-flor-window = Flor harus diselesaikan lebih dulu. Truco tidak bisa dipanggil sampai kartu pertama dimainkan.
truco-error-flor-window-closed = Contraflor hanya bisa dipanggil selama kedua pihak memiliki flor dan sebelum kartu pertama dimainkan.
truco-error-envido-flor = Envido dibatalkan di ronde ini karena ada pemain yang memiliki flor.
truco-error-envido-cannot-raise = { $call } tidak bisa ditambahkan ke envido yang sedang dimainkan.
truco-points-you = Anda mendapat { $points } { $points ->
    [one] poin
   *[other] poin
} dari { $reason }.
truco-points-player = { $player } mendapat { $points } { $points ->
    [one] poin
   *[other] poin
} dari { $reason }.
truco-half-buenas-you = Anda memasuki buenas, babak kedua.
truco-half-buenas-player = { $player } memasuki buenas, babak kedua.

# Card information, descriptions and touch gestures
truco-card-info-label = Informasi item
truco-card-info = { $card }: mengalahkan { $beats } dari { $total } kartu lain di dek ini.
truco-card-info-envido = { $card }: mengalahkan { $beats } dari { $total } kartu lain di dek ini. Nilai envido: { $value }.
truco-desc-call-ladder = { $call }: menaikkan nilai ronde menjadi { $points } { $points ->
    [one] poin
   *[other] poin
}. Jika ditolak, pihak yang memanggil mendapat { $refused } { $refused ->
    [one] poin
   *[other] poin
}.
truco-desc-call-envido = { $call }: kedua pihak membandingkan envido mereka. Jika diterima, pemenang mendapat { $points } { $points ->
    [one] poin
   *[other] poin
}. Jika ditolak, pihak yang memanggil mendapat { $refused } { $refused ->
    [one] poin
   *[other] poin
}.
truco-desc-call-flor = { $call }: para pemegang flor membandingkan flor mereka. Jika diterima, pemenang mendapat { $points } { $points ->
    [one] poin
   *[other] poin
}. Jika ditolak, pihak yang memanggil mendapat { $refused } { $refused ->
    [one] poin
   *[other] poin
}.
truco-desc-accept = Terima { $call } dan lanjutkan bermain.
truco-desc-decline = Tolak { $call }. Pihak lawan mendapat { $points } { $points ->
    [one] poin
   *[other] poin
} dan ronde berakhir.
truco-desc-mazo = Lipat kartu Anda. Jika semua anggota tim Anda sudah melipat kartu, pihak lawan memenangkan ronde.
truco-trick-tie-neutral = Trik { $trick } seri.
