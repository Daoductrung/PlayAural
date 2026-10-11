game-name-ludo = Ludo
ludo-roll-die = Lempar dadu
ludo-move-token = Pindahkan bidak
ludo-move-token-n = Pindahkan bidak { $token }
ludo-check-board = Lihat status papan
ludo-select-token = Pilih bidak yang akan dipindahkan:
ludo-roll = { $player } mendapat angka { $roll }.
ludo-you-roll = Anda mendapat angka { $roll }.
ludo-no-moves = { $player } tidak memiliki langkah yang diperbolehkan.
ludo-you-no-moves = Anda tidak memiliki langkah yang diperbolehkan.
ludo-error-roll-pending-move = Anda sudah melempar dadu dan memiliki langkah yang diperbolehkan. Pindahkan salah satu bidak yang dapat bergerak sebelum melempar lagi.
ludo-you-enter-board =
    { $brief ->
        [yes]
            { $safe ->
                [yes] Anda: bidak { $token } keluar, maju { $spaces } ke { $position }, aman.
               *[no] Anda: bidak { $token } keluar, maju { $spaces } ke { $position }.
            }
       *[no]
            { $safe ->
                [yes] Anda mengeluarkan bidak { $token } ke petak { $position }, yang merupakan petak aman.
               *[no] Anda mengeluarkan bidak { $token } ke petak { $position }.
            }
    }
ludo-enter-board =
    { $brief ->
        [yes]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }): bidak { $token } keluar, maju { $spaces } ke { $position }, aman.
               *[no]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }): bidak { $token } keluar, maju { $spaces } ke { $position }.
            }
       *[no]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }) mengeluarkan bidak { $token } ke petak { $position }, yang merupakan petak aman.
               *[no]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }) mengeluarkan bidak { $token } ke petak { $position }.
            }
    }
ludo-you-move-track =
    { $brief ->
        [yes]
            { $safe ->
                [yes] Anda: bidak { $token } maju { $spaces } ke { $position }, aman.
               *[no] Anda: bidak { $token } maju { $spaces } ke { $position }.
            }
       *[no]
            { $safe ->
                [yes] Anda memindahkan bidak { $token } ke petak { $position }, yang merupakan petak aman.
               *[no] Anda memindahkan bidak { $token } ke petak { $position }.
            }
    }
ludo-move-track =
    { $brief ->
        [yes]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }): bidak { $token } maju { $spaces } ke { $position }, aman.
               *[no]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }): bidak { $token } maju { $spaces } ke { $position }.
            }
       *[no]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }) memindahkan bidak { $token } ke petak { $position }, yang merupakan petak aman.
               *[no]
                    { $player } ({ $color ->
                        [red] Merah
                        [blue] Biru
                        [green] Hijau
                        [yellow] Kuning
                       *[other] { $color }
                    }) memindahkan bidak { $token } ke petak { $position }.
            }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] Anda: bidak { $token } maju { $spaces } ke petak { $position } dari { $total } pada jalur rumah.
       *[no] Anda memindahkan bidak { $token } ke jalur rumah Anda (petak { $position } dari { $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }): bidak { $token } maju { $spaces } ke petak { $position } dari { $total } pada jalur rumah.
       *[no]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) memindahkan bidak { $token } ke jalur rumah (petak { $position } dari { $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] Anda: bidak { $token } sampai di rumah. { $finished } dari 4 selesai.
       *[no] Bidak { $token } Anda sampai di rumah. { $finished } dari 4 bidak sudah selesai.
    }
ludo-home-finish =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }): bidak { $token } sampai di rumah. { $finished } dari 4 selesai.
       *[no]
            Bidak { $token } milik { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) sampai di rumah. { $finished } dari 4 bidak sudah selesai.
    }
ludo-you-move-home =
    { $brief ->
        [yes] Anda: bidak { $token } maju { $spaces } ke petak { $position } dari { $total } pada jalur rumah.
       *[no] Anda memindahkan bidak { $token } di jalur rumah Anda (petak { $position } dari { $total }).
    }
ludo-move-home =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }): bidak { $token } maju { $spaces } ke petak { $position } dari { $total } pada jalur rumah.
       *[no]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) memindahkan bidak { $token } di jalur rumah (petak { $position } dari { $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes]
            Anda: memulangkan { $count } bidak milik { $captured_player } ({ $captured_color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $captured_color }
            }) ke area awal.
       *[no]
            Anda menangkap { $count ->
                [one] 1 bidak
               *[other] { $count } bidak
            } dari { $captured_player } ({ $captured_color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $captured_color }
            }) dan memulangkan { $count ->
                [one] bidak tersebut
               *[other] semua bidak tersebut
            } ke area awal.
    }
ludo-your-token-captured =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) memulangkan { $count ->
                [one] bidak Anda
               *[other] { $count } bidak Anda
            } ke area awal.
       *[no]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) menangkap { $count ->
                [one] bidak Anda
               *[other] { $count } bidak Anda
            } dan memulangkan { $count ->
                [one] bidak tersebut
               *[other] semua bidak tersebut
            } ke area awal.
    }
ludo-captures =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }): memulangkan { $count } bidak milik { $captured_player } ({ $captured_color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $captured_color }
            }) ke area awal.
       *[no]
            { $player } ({ $color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $color }
            }) menangkap { $count ->
                [one] 1 bidak
               *[other] { $count } bidak
            } dari { $captured_player } ({ $captured_color ->
                [red] Merah
                [blue] Biru
                [green] Hijau
                [yellow] Kuning
               *[other] { $captured_color }
            }) dan memulangkannya ke area awal.
    }
ludo-extra-turn = { $player } mendapat angka 6. Giliran tambahan.
ludo-you-extra-turn = Anda mendapatkan angka 6. Giliran tambahan.
ludo-you-too-many-sixes = Anda mendapat angka 6 sebanyak { $count } kali berturut-turut. Semua gerakan dalam rangkaian giliran ini dibatalkan dan giliran Anda berakhir.
ludo-too-many-sixes = { $player } mendapat angka 6 sebanyak { $count } kali berturut-turut. Semua gerakan dalam rangkaian giliran ini dibatalkan. Giliran berakhir.
ludo-you-winner = Anda menang! Keempat bidak ada di rumah.
ludo-winner =
    { $player } ({ $color ->
        [red] Merah
        [blue] Biru
        [green] Hijau
        [yellow] Kuning
       *[other] { $color }
    }) menang! Keempat bidak ada di rumah.
ludo-end-score-line =
    { $index }. { $player }: { $count ->
        [one] 1 bidak sampai di rumah
       *[other] { $count } bidak sampai di rumah
    }
ludo-board-player =
    { $player } ({ $color ->
        [red] Merah
        [blue] Biru
        [green] Hijau
        [yellow] Kuning
       *[other] { $color }
    }): { $finished } dari 4 selesai
ludo-token-yard = Bidak { $token } (area awal)
ludo-token-track =
    { $safe ->
        [yes] Bidak { $token } (petak { $position }, petak aman)
       *[no] Bidak { $token } (petak { $position })
    }
ludo-token-home = Bidak { $token } (jalur rumah, petak { $position } dari { $total })
ludo-token-finished = Bidak { $token } (selesai)
ludo-last-roll = Hasil dadu terakhir: { $roll }
ludo-set-max-sixes = Batas angka 6 berturut-turut: { $max_consecutive_sixes }
ludo-enter-max-sixes = Masukkan batas angka 6 berturut-turut
ludo-option-changed-max-sixes = Batas angka 6 berturut-turut diatur menjadi { $max_consecutive_sixes }.
ludo-desc-max-consecutive-sixes = Batas angka 6 berturut-turut dalam satu rangkaian giliran sebelum gerakan dibatalkan dan giliran beralih. Bawaan 3, antara 0 dan 5.
ludo-set-safe-start-squares = Petak awal aman: { $enabled }
ludo-option-changed-safe-start-squares = Petak awal aman diatur menjadi { $enabled }.
ludo-desc-safe-start-squares = Menentukan apakah petak awal setiap pemain merupakan petak aman.
