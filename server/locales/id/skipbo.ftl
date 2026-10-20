game-name-skipbo = Skip-Bo
skipbo-stock-mode-standard = Standar (30 atau 20 kartu)
skipbo-stock-mode-short = Cepat 10 kartu
skipbo-stock-mode-short-15 = Cepat 15 kartu
skipbo-scoring-single = Satu permainan
skipbo-scoring-match = Pertandingan berpoin
skipbo-set-stock-mode = Tumpukan stok: { $mode }
skipbo-select-stock-mode = Pilih jumlah kartu dalam tumpukan stok:
skipbo-option-changed-stock-mode = Tumpukan stok kini menggunakan { $mode }.
skipbo-desc-stock-mode = Standar menggunakan 30 kartu stok untuk 2 sampai 4 pemain dan 20 kartu untuk 5 atau 6 pemain. Permainan cepat menggunakan 10 atau 15 kartu stok untuk setiap pemain.
skipbo-set-scoring-mode = Format pertandingan: { $mode }
skipbo-select-scoring-mode = Pilih format pertandingan:
skipbo-option-changed-scoring-mode = Format pertandingan kini { $mode }.
skipbo-desc-scoring-mode = Satu permainan berakhir ketika satu pemain atau pasangan menghabiskan tumpukan stoknya. Pertandingan berpoin berlanjut selama beberapa permainan sampai ada yang mencapai target poin.
skipbo-set-winning-score = Target pertandingan: { $score } poin
skipbo-enter-winning-score = Masukkan target pertandingan dari 25 sampai 5000 poin:
skipbo-option-changed-winning-score = Target pertandingan kini { $score } poin.
skipbo-desc-winning-score = Jumlah poin untuk memenangkan pertandingan berpoin. Target resminya 500 poin.
skipbo-desc-team-mode = Dalam mode Perorangan, setiap pemain memiliki tumpukan stok dan poin sendiri. Mode pasangan resmi menggunakan tim beranggotakan dua orang. Rekan boleh memainkan kartu dari tumpukan stok dan buangan satu sama lain, tetapi tidak dari kartu di tangan rekannya.
skipbo-card-number = { $value }
skipbo-card-wild = Wild Skip-Bo
skipbo-card-wild-as = Skip-Bo sebagai { $value }
skipbo-source-your-hand = kartu di tangan Anda
skipbo-source-player-hand = kartu di tangan { $owner }
skipbo-source-your-stock = tumpukan stok Anda
skipbo-source-player-stock = tumpukan stok { $owner }
skipbo-source-your-discard = tumpukan buangan { $pile } Anda
skipbo-source-player-discard = tumpukan buangan { $pile } milik { $owner }
skipbo-action-source-hand = kartu di tangan
skipbo-action-source-stock = stok
skipbo-action-source-player-stock = stok { $owner }
skipbo-action-source-discard = tumpukan buangan { $pile }
skipbo-action-source-player-discard = tumpukan buangan { $pile } milik { $owner }
skipbo-play-action = { $card }, dari { $source } ke tumpukan { $pile }
skipbo-card-action = { $card }, { $source }
skipbo-card-desc-play-or-discard = Tumpukan susun yang tersedia: { $piles }. Pilih kartu untuk memainkannya atau membuangnya dan mengakhiri giliran.
skipbo-card-desc-discard-only = Pilih kartu untuk membuangnya dan mengakhiri giliran.
skipbo-card-desc-choose-building = Tumpukan susun yang tersedia: { $piles }. Pilih kartu untuk menentukan tumpukan tujuan.
skipbo-end-turn-empty = Akhiri giliran tanpa membuang kartu
skipbo-end-turn-empty-desc = Kartu di tangan Anda sudah habis dan tidak ada kartu yang bisa diambil, jadi Anda tidak bisa membuang kartu.
skipbo-select-card-move = Pilih tujuan kartu ini:
skipbo-move-building-empty = Tumpukan susun { $pile }: kosong. Mainkan { $card }
skipbo-move-building-top = Tumpukan susun { $pile }: kartu teratas { $current }. Mainkan { $card }
skipbo-move-discard-empty = Tumpukan buangan { $pile }: kosong. Buang ke sini dan akhiri giliran
skipbo-move-discard-top = Tumpukan buangan { $pile }: kartu teratas { $top }. Buang ke sini dan akhiri giliran
skipbo-read-building-piles = Lihat tumpukan susun
skipbo-read-stock-piles = Lihat tumpukan stok
skipbo-read-own-discard-piles = Lihat tumpukan buangan Anda
skipbo-read-discard-piles = Lihat tumpukan buangan pemain lain
skipbo-select-discard-owner = Pilih pemilik tumpukan buangan yang ingin dilihat:
skipbo-game-start = Permainan dimulai. Setiap tumpukan stok berisi { $stock_count } kartu.
skipbo-game-start-quick = Permainan cepat dimulai. Setiap tumpukan stok berisi { $stock_count } kartu.
skipbo-match-game-start = Permainan berpoin ke-{ $game } dimulai. Setiap tumpukan stok berisi { $stock_count } kartu.
skipbo-match-game-start-quick = Permainan cepat berpoin ke-{ $game } dimulai. Setiap tumpukan stok berisi { $stock_count } kartu.
skipbo-initial-stock-you = Kartu stok Anda yang terbuka adalah { $card }.
skipbo-initial-stock-player = Kartu stok { $player } yang terbuka adalah { $card }.
skipbo-draw-turn-you = Anda mengambil { $count } { $count ->
    [one] kartu
   *[other] kartu
    } untuk memulai giliran. Kartu di tangan Anda: { $hand }.
skipbo-draw-turn-player = { $player } mengambil { $count } { $count ->
    [one] kartu
   *[other] kartu
    } untuk memulai giliran.
skipbo-refill-you = Anda telah memainkan semua kartu di tangan dan langsung mengambil { $count } { $count ->
    [one] kartu
   *[other] kartu
    }. Kartu di tangan Anda: { $hand }.
skipbo-refill-player = { $player } telah memainkan semua kartu di tangan dan langsung mengambil { $count } { $count ->
    [one] kartu
   *[other] kartu
    }.
skipbo-no-refill-you = Kartu di tangan Anda sudah habis dan tidak ada kartu yang bisa diambil.
skipbo-no-refill-player = Kartu di tangan { $player } sudah habis, tetapi tidak ada kartu yang bisa diambil.
skipbo-recycle-completed = Tumpukan ambil kosong. Tumpukan susun yang sudah lengkap dikocok menjadi tumpukan ambil baru berisi { $count } kartu.
skipbo-play-you = Anda memainkan { $card } dari { $source } ke tumpukan susun { $pile }.
skipbo-play-player = { $player } memainkan { $card } dari { $source } ke tumpukan susun { $pile }.
skipbo-complete-building-you = Anda melengkapi tumpukan susun { $pile } hingga 12. Kartu-kartunya disisihkan untuk dikocok ulang dan tempat tumpukan itu kembali kosong.
skipbo-complete-building-player = { $player } melengkapi tumpukan susun { $pile } hingga 12. Kartu-kartunya disisihkan untuk dikocok ulang dan tempat tumpukan itu kembali kosong.
skipbo-next-stock-you = Kartu stok Anda berikutnya yang terbuka adalah { $card }. Tersisa { $count } { $count ->
    [one] kartu
   *[other] kartu
    } dalam tumpukan stok Anda.
skipbo-next-stock-player = Kartu stok { $player } berikutnya yang terbuka adalah { $card }. Tumpukan stok itu masih berisi { $count } { $count ->
    [one] kartu
   *[other] kartu
    }.
skipbo-stock-cleared-you = Tumpukan stok Anda sudah habis. Pasangan Anda masih harus menghabiskan tumpukan stok yang satunya.
skipbo-stock-cleared-player = Tumpukan stok { $player } sudah habis. Pasangan ini masih harus menghabiskan tumpukan stok yang satunya.
skipbo-discard-you = Anda membuang { $card } ke tumpukan buangan { $pile } dan mengakhiri giliran.
skipbo-discard-player = { $player } membuang { $card } ke tumpukan buangan { $pile } dan mengakhiri giliran.
skipbo-empty-end-you = Anda tidak memiliki kartu untuk dibuang, jadi giliran berakhir tanpa membuang kartu.
skipbo-empty-end-player = { $player } tidak memiliki kartu untuk dibuang dan mengakhiri giliran tanpa membuang kartu.
skipbo-single-win-you = Anda menghabiskan tumpukan stok dan memenangkan permainan.
skipbo-single-win-player = { $player } menghabiskan tumpukan stoknya dan memenangkan permainan.
skipbo-single-win-team-you = Pasangan Anda menghabiskan kedua tumpukan stok dan memenangkan permainan.
skipbo-single-win-team = Tim { $team } menghabiskan kedua tumpukan stok dan memenangkan permainan.
skipbo-scored-game-win-you = Anda menghabiskan tumpukan stok dan memenangkan permainan berpoin ke-{ $game }. Anda mendapat { $points } poin, dengan { $remaining } kartu tersisa di seluruh tumpukan stok lawan. Total pertandingan Anda kini { $total }.
skipbo-scored-game-win-player = { $player } menghabiskan tumpukan stoknya dan memenangkan permainan berpoin ke-{ $game }, mendapat { $points } poin dengan { $remaining } kartu tersisa di seluruh tumpukan stok lawan. Total pertandingan kini { $total }.
skipbo-scored-game-win-team-you = Pasangan Anda menghabiskan kedua tumpukan stok dan memenangkan permainan berpoin ke-{ $game }. Pasangan Anda mendapat { $points } poin, dengan { $remaining } kartu tersisa di seluruh tumpukan stok lawan. Total pertandingan pasangan Anda kini { $total }.
skipbo-scored-game-win-team = Tim { $team } menghabiskan kedua tumpukan stok dan memenangkan permainan berpoin ke-{ $game }, mendapat { $points } poin dengan { $remaining } kartu tersisa di seluruh tumpukan stok lawan. Total pertandingan tim kini { $total }.
skipbo-next-round = Permainan berpoin berikutnya segera dimulai. Posisi pemain pembuka maju satu tempat duduk.
skipbo-match-win-you = Anda memenangkan pertandingan Skip-Bo dengan { $score } poin.
skipbo-match-win-player = { $player } memenangkan pertandingan Skip-Bo dengan { $score } poin.
skipbo-match-win-team-you = Pasangan Anda memenangkan pertandingan Skip-Bo dengan { $score } poin.
skipbo-match-win-team = Tim { $team } memenangkan pertandingan Skip-Bo dengan { $score } poin.
skipbo-building-empty = Tumpukan susun { $pile }: kosong. Membutuhkan 1.
skipbo-building-top = Tumpukan susun { $pile }: kartu teratas { $value }. Membutuhkan { $needed }.
skipbo-draw-count = Tumpukan ambil: { $draw_count } kartu. Kartu dari tumpukan susun lengkap yang menunggu dikocok ulang: { $recycle_count }.
skipbo-stock-empty = Tumpukan stok { $player }: kosong.
skipbo-stock-status = Tumpukan stok { $player }: { $card } terbuka, total { $count } { $count ->
    [one] kartu
   *[other] kartu
    }.
skipbo-discard-your-header = Tumpukan buangan Anda:
skipbo-discard-player-header = Tumpukan buangan { $player }:
skipbo-discard-empty = Tumpukan buangan { $pile }: kosong.
skipbo-discard-top = Tumpukan buangan { $pile }: kartu teratas { $card }, total { $count } { $count ->
    [one] kartu
   *[other] kartu
    }.
skipbo-hand-empty = Anda belum memiliki kartu di tangan.
skipbo-hand-menu-card = Di tangan: { $card }
skipbo-error-invalid-stock-mode = Jumlah kartu stok yang dipilih tidak didukung. Pilih Standar, Cepat 10, atau Cepat 15.
skipbo-error-invalid-scoring-mode = Format pertandingan yang dipilih tidak didukung. Pilih Satu permainan atau Pertandingan berpoin.
skipbo-error-winning-score-range = Target pertandingan harus dari { $min } sampai { $max } poin. Nilai saat ini { $value }.
skipbo-error-partnership-player-count = Mode pasangan memerlukan tepat 4 pemain untuk dua pasangan atau 6 pemain untuk tiga pasangan.
skipbo-error-game-not-active = Permainan Skip-Bo ini sedang tidak berlangsung.
skipbo-error-round-transition = Permainan saat ini sudah berakhir. Tunggu permainan berikutnya dimulai.
skipbo-error-card-move-selection-you = Tentukan dahulu tujuan kartu yang dipilih.
skipbo-error-play-changed = Langkah itu tidak tersedia lagi karena kartu atau tumpukan susunnya berubah. Pilih tindakan yang tersedia di menu giliran saat ini.
skipbo-error-card-changed = Kartu itu tidak tersedia lagi. Pilih tindakan yang tersedia di menu giliran saat ini.
skipbo-error-cards-available = Anda masih memiliki kartu untuk dibuang. Akhiri giliran dengan memilih kartu itu dan salah satu dari empat tumpukan buangan Anda.
skipbo-error-no-discard-targets = Tidak ada tumpukan buangan pemain lain yang tersedia.
skipbo-error-discard-target-changed = Tumpukan buangan pemain itu tidak tersedia lagi. Pilih pemain yang masih tersedia.
skipbo-discard-owner-unavailable = Pemain tidak tersedia lagi
skipbo-result-line = { $rank }. { $player }: { $points }
