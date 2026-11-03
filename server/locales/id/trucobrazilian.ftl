# Options
trucobrazilian-desc-team-mode = Perorangan adalah permainan satu lawan satu untuk 2 pemain. 2v2 menggunakan 4 pemain dan 3v3 menggunakan 6 pemain; rekan berbagi skor dan boleh memanggil untuk seluruh tim.

# French deck
trucobrazilian-rank-ace = As
trucobrazilian-rank-jack = Jack
trucobrazilian-rank-queen = Queen
trucobrazilian-rank-king = King
trucobrazilian-suit-diamonds = Wajik
trucobrazilian-suit-spades = Sekop
trucobrazilian-suit-hearts = Hati
trucobrazilian-suit-clubs = Keriting
trucobrazilian-card-name = { $rank } { $suit }

# Calls
trucobrazilian-call-truco = Truco
trucobrazilian-call-seis = Seis
trucobrazilian-call-nove = Nove
trucobrazilian-call-doze = Doze
trucobrazilian-call-onze = Mão de onze

# Actions and information
trucobrazilian-action-onze-play = Jogar (mainkan ronde ini)
trucobrazilian-action-onze-run = Correr (lari dan lepaskan ronde ini)
trucobrazilian-read-vira = Baca vira dan manilha
trucobrazilian-no-vira = Vira belum dibuka.
trucobrazilian-vira = Vira-nya adalah { $card }. Manilha-nya adalah { $manilha }.
trucobrazilian-vira-is = Vira-nya adalah { $card }. Manilha-nya adalah { $manilha }.

# Game flow
trucobrazilian-game-start = Truco Brasil dimulai. Pihak pertama yang mencapai { $points } poin menang. Setiap ronde, satu kartu yang dibuka, disebut vira, menentukan manilha.
trucobrazilian-onze-your-team = Tim Anda memiliki 11 poin: mão de onze. Pilih Jogar untuk memainkan ronde ini seharga 3 poin tanpa panggilan, atau Correr untuk memberi pihak lawan 1 poin.
trucobrazilian-onze-team = { $team } memiliki 11 poin dan sedang memutuskan apakah akan memainkan mão de onze.
trucobrazilian-onze-play-you = Anda memainkan mão de onze. Ronde ini bernilai 3 poin dan tidak ada panggilan yang diizinkan.
trucobrazilian-onze-play-player = { $player } memainkan mão de onze. Ronde ini bernilai 3 poin dan tidak ada panggilan yang diizinkan.
trucobrazilian-onze-run-you = Anda lari. Pihak lawan mendapat 1 poin.
trucobrazilian-onze-run-player = { $player } lari. Pihak lawan mendapat 1 poin.
trucobrazilian-ferro = Kedua pihak memiliki 11 poin: mão de ferro. Tidak ada panggilan yang diizinkan dan siapa pun yang memenangkan ronde ini memenangkan permainan.
trucobrazilian-reason-onze-run = lari di mão de onze
trucobrazilian-hand-annulled = Ketiga trik seri. Ronde ini dibatalkan dan tidak ada yang mendapat poin.

# Errors and descriptions
trucobrazilian-error-onze-pending = { $team } harus memutuskan lebih dulu apakah akan memainkan mão de onze.
trucobrazilian-error-no-calls = Memanggil tidak diizinkan di ronde ini karena ini adalah mão de onze atau mão de ferro.
trucobrazilian-desc-onze-play = Mainkan ronde ini. Nilainya { $points } { $points ->
    [one] poin
   *[other] poin
} dan tidak ada panggilan yang diizinkan.
trucobrazilian-desc-onze-run = Lari dan lepaskan ronde ini. Pihak lawan mendapat 1 poin.

trucobrazilian-action-accept = Aceito (terima)
trucobrazilian-action-decline = Correr (tolak dan lari)
trucobrazilian-accept-you = Anda mengatakan Aceito untuk { $call }.
trucobrazilian-accept-player = { $player } mengatakan Aceito untuk { $call }.
trucobrazilian-decline-you = Anda lari dari { $call }.
trucobrazilian-decline-player = { $player } lari dari { $call }.
trucobrazilian-pending-answer = { $player } memanggil { $call }. Jawab dengan Aceito atau Correr, atau naikkan.
trucobrazilian-error-answer-first = Anda harus menjawab { $call } sebelum melakukan hal lain. Pilih Aceito atau Correr, atau naikkan.
trucobrazilian-error-raise-max = Doze sudah menjadi panggilan tertinggi dan tidak bisa dinaikkan lagi.
trucobrazilian-status-onze-pending = { $team } harus memutuskan apakah akan memainkan mão de onze.
trucobrazilian-status-no-calls = Panggilan tidak diizinkan di ronde ini. Ronde ini bernilai { $points } { $points ->
    [one] poin
   *[other] poin
}.

# Mão de ferro (both sides at 11) is played face down; mão de onze partners see each other's cards
trucobrazilian-blind-cards = Mão de ferro: { $count } kartu Anda tertutup dan Anda tidak bisa melihatnya. Pilih kartu berdasarkan posisinya; setiap kartu terbuka saat dimainkan.
trucobrazilian-blind-hand = Mão de ferro: Anda memegang { $count } { $count ->
    [one] kartu
   *[other] kartu
} tertutup, dan Anda tidak bisa melihat { $count ->
    [one] kartu itu
   *[other] kartu-kartu itu
}.
trucobrazilian-action-play-blind = Mainkan kartu tertutup { $number }
trucobrazilian-desc-blind-card = Kartu tertutup. Anda tidak akan melihatnya sampai kartu itu dimainkan.
trucobrazilian-onze-partner-cards = Rekan Anda { $partner } menunjukkan kartunya kepada Anda: { $cards }.
