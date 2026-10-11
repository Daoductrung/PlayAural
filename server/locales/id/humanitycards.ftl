game-name-humanitycards = Cards Against Humanity
hc-set-winning-score = Skor kemenangan: { $score }
hc-enter-winning-score = Masukkan skor kemenangan:
hc-option-changed-winning-score = Skor kemenangan diatur menjadi { $score }.
hc-desc-winning-score = Jumlah kartu pemenang yang harus dikumpulkan pemain untuk memenangkan pertandingan. Bawaan 7, dapat diatur dari 3 hingga 20.
hc-set-hand-size = Jumlah kartu di tangan: { $count }
hc-enter-hand-size = Masukkan jumlah kartu di tangan:
hc-option-changed-hand-size = Jumlah kartu di tangan diatur menjadi { $count }.
hc-desc-hand-size = Jumlah kartu jawaban yang dipegang setiap pemain setelah pengisian ulang. Semakin banyak kartu, semakin banyak pilihan, tetapi ronde bisa lebih lama. Bawaan 10, dapat diatur dari 5 hingga 15.
hc-set-card-language = Bahasa kartu: { $language }
hc-select-card-language = Pilih bahasa kartu
hc-option-changed-card-language = Bahasa kartu diatur menjadi { $language }.
hc-desc-card-language = Bahasa semua kartu pertanyaan dan jawaban dalam pertandingan, terpisah dari bahasa antarmuka masing-masing pemain. Bawaan bahasa Inggris. Pilihannya bahasa Inggris, Spanyol, dan Portugis Brasil.
hc-card-language-pt-br = Portugis Brasil
hc-card-blank = bagian kosong
hc-card-same-again = kartu yang sama lagi
hc-set-card-packs = Paket kartu ({ $count } dari { $total } dipilih)
hc-option-changed-card-packs = Pilihan paket kartu diubah.
hc-desc-card-packs = Pilih paket pertanyaan dan jawaban bahasa Inggris untuk permainan. Kartu yang persis sama dari beberapa paket hanya disertakan sekali. Setidaknya satu paket harus tetap dipilih.
hc-pack-group-current = Paket utama AS saat ini
hc-pack-group-main-decks = Edisi paket utama
hc-pack-group-official-add-ons = Ekspansi dan paket resmi
hc-pack-group-family = Family Edition
hc-pack-group-community = Paket komunitas
hc-pack-group-all = Semua paket
hc-set-czar-selection = Pemilihan juri: { $mode }
hc-select-czar-selection = Pilih cara menentukan juri
hc-option-changed-czar-selection = Pemilihan juri diatur menjadi { $mode }.
hc-desc-czar-selection = Menentukan juri setiap ronde: bergiliran menurut urutan duduk, dipilih secara acak, atau pemenang ronde sebelumnya.
hc-set-num-judges = Jumlah juri: { $count }
hc-enter-num-judges = Masukkan jumlah juri:
hc-option-changed-num-judges = Jumlah juri diatur menjadi { $count }.
hc-desc-num-judges = Jumlah juri setiap ronde. Harus lebih sedikit daripada jumlah pemain agar ada yang mengirim jawaban. Jika ada beberapa juri, siapa pun di antara mereka dapat memilih pemenang. Bawaan 1, dapat diatur dari 1 hingga 3.
hc-czar-rotating = Bergiliran
hc-czar-random = Acak
hc-czar-winner = Pemenang terakhir
hc-game-starting = Mengocok kartu.
hc-dealing-cards = Membagikan { $count } kartu kepada setiap pemain.
hc-round-start = Ronde { $round }.
hc-judge-is = { $judges } { $count ->
    [1] menjadi juri
   *[other] menjadi juri
}.
hc-you-are-judge = Anda menjadi juri ronde ini.
hc-you-and-others-are-judges = Anda dan { $judges } menjadi juri ronde ini.
hc-black-card = Pertanyaannya: { $text }
hc-black-card-draw = Ambil { $count } { $count ->
    [one] kartu tambahan
   *[other] kartu tambahan
} terlebih dahulu.
hc-black-card-pick = Pilih { $count } kartu.
hc-view-black-card = Periksa kartu pertanyaan
hc-no-question-card = Belum ada kartu pertanyaan untuk dijawab.
hc-select-cards = Pilih { $count } { $count ->
    [one] kartu
   *[other] kartu
} dari tangan Anda.
hc-card-selected = { $text }, dipilih
hc-card-selected-position = { $text }, dipilih sebagai jawaban ke-{ $position }
hc-card-not-selected = { $text }
hc-submit-cards = Kirim ({ $selected } dari { $required } dipilih)
hc-submission-progress = { $submitted } dari { $total } pemain sudah mengirim jawaban.
hc-already-submitted = Anda sudah mengirim kartu jawaban.
hc-you-submitted = Anda mengirim kartu jawaban.
hc-player-submitted = { $player } mengirim kartu jawaban.
hc-judge-cannot-submit = Anda menjadi juri ronde ini, jadi tidak dapat mengirim jawaban.
hc-not-submission-phase = Anda hanya dapat memilih dan mengirim kartu putih saat tahap pengumpulan jawaban.
hc-card-not-in-hand = Kartu pada posisi itu tidak ada di tangan Anda.
hc-judge-has-no-submission = Juri tidak memiliki jawaban untuk ditinjau pada ronde ini.
hc-no-submission-active = Belum ada jawaban yang dapat ditinjau.
hc-wrong-card-count = Anda harus memilih tepat { $count } { $count ->
    [one] kartu
   *[other] kartu
}.
hc-selection-full = Anda sudah memilih { $count } { $count ->
    [one] kartu
   *[other] kartu
}. Batalkan salah satu pilihan sebelum memilih kartu lain.
hc-judging-start = Semua jawaban sudah terkumpul! Saatnya menilai.
hc-choose-best-card = Pilih kartu terbaik
hc-choose-best-card-for = Pilih kartu terbaik untuk: { $prompt }
hc-card-number = Kartu { $number }
hc-submission-number = Jawaban { $number }
hc-only-judges-pick = Hanya juri yang dapat memilih jawaban pemenang.
hc-not-judging-phase = Jawaban pemenang hanya dapat dipilih saat tahap penilaian.
hc-submission-not-available = Jawaban itu sudah tidak tersedia.
hc-you-win-round = Anda memenangkan ronde! Skor Anda kini { $score }.
hc-player-wins-round = { $player } memenangkan ronde! Skor: { $score }.
hc-score-line = { $player }: { $score } { $score ->
    [one] poin
   *[other] poin
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] poin
   *[other] poin
}
hc-all-submissions = Jawaban lainnya:
hc-your-winning-answer = Jawaban Anda yang menang: { $text }
hc-winning-answer-player = Jawaban pemenang dari { $player }: { $text }
hc-your-other-submission = Jawaban Anda lainnya: { $text }
hc-other-submission-player = { $player }: { $text }
hc-preview-submission = Tinjau jawaban sebelum dikirim
hc-view-submission = Periksa jawaban Anda
hc-preview-submission-text = Tinjauan jawaban: { $text }
hc-your-submission = Jawaban Anda: { $text }
hc-select-cards-first = Pilih setidaknya 1 kartu terlebih dahulu.
hc-review-hand = Periksa kartu di tangan
hc-hand-empty = Anda tidak memiliki kartu di tangan.
hc-hand-card = { $number }. { $text }
hc-hand-card-selected = { $number }. { $text }, dipilih sebagai jawaban ke-{ $position }
hc-review-answers = Periksa semua jawaban
hc-answer-line = Jawaban { $number }: { $text }
hc-no-answers-to-review = Belum ada jawaban yang dapat diperiksa.
hc-game-winner = { $player } menang dengan { $score } poin!
hc-you-win = Anda menang dengan { $score } poin!
hc-deck-reshuffled = Kartu putih yang sudah dibuang dikocok kembali ke tumpukan.
hc-black-deck-reshuffled = Kartu hitam yang sudah dibuang dikocok kembali ke tumpukan.
hc-not-enough-cards = Kartu tidak cukup. Coba aktifkan lebih banyak paket.
hc-error-too-many-judges = { $judges } juri memerlukan setidaknya { $required } pemain, tetapi meja ini hanya memiliki { $players } pemain. Kurangi jumlah juri atau tambahkan pemain.
hc-error-no-valid-packs = Belum ada paket kartu yang dapat digunakan. Pilih setidaknya satu paket sebelum memulai.
hc-error-no-black-cards = Paket yang dipilih tidak memiliki kartu pertanyaan hitam. Pilih paket lain sebelum memulai.
hc-error-not-enough-white-cards = { $players } pemain dengan { $hand_size } kartu per orang memerlukan setidaknya { $needed } kartu putih, tetapi paket yang dipilih hanya menyediakan { $available }. Aktifkan lebih banyak paket atau kurangi jumlah kartu di tangan.
hc-error-pick-exceeds-hand-size = Paket yang dipilih memiliki pertanyaan yang membutuhkan { $pick } jawaban, tetapi jumlah kartu di tangan hanya { $hand_size }. Tambah jumlah kartu di tangan atau pilih paket lain.
hc-toggle-card-keybind = Pilih atau batalkan pilihan kartu { $number }
hc-submit-cards-keybind = Kirim kartu
hc-whose-judge = Siapa jurinya
hc-waiting-for = Menunggu { $names } mengirim jawaban.
hc-all-submitted-waiting-judge = Semua pemain sudah mengirim jawaban. Menunggu penilaian { $judge }.
