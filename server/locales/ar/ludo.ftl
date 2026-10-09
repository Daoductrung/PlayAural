game-name-ludo = لودو

ludo-roll-die = رمي النرد
ludo-move-token = تحريك قطعة
ludo-move-token-n = تحريك القطعة { $token }
ludo-check-board = عرض حالة اللوحة
ludo-select-token = اختر قطعة لتحريكها:

ludo-roll = يرمي { $player } { $roll }.
ludo-you-roll = ترمي { $roll }.
ludo-no-moves = ليست لدى { $player } تحركات صالحة.
ludo-you-no-moves = ليست لديك تحركات صالحة.
ludo-error-roll-pending-move = لقد رميت بالفعل ولديك تحرك صالح. حرّك إحدى قطعك المتاحة قبل الرمي مرة أخرى.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] أنت: القطعة { $token } تخرج +{ $spaces } إلى { $position }، آمنة.
           *[no] أنت: القطعة { $token } تخرج +{ $spaces } إلى { $position }.
        }
       *[no] { $safe ->
            [yes] تُدخل القطعة { $token } إلى الموضع { $position }، وهو مربع آمن.
           *[no] تُدخل القطعة { $token } إلى الموضع { $position }.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): القطعة { $token } تخرج +{ $spaces } إلى { $position }، آمنة.
           *[no] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): القطعة { $token } تخرج +{ $spaces } إلى { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يُدخل القطعة { $token } إلى الموضع { $position }، وهو مربع آمن.
           *[no] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يُدخل القطعة { $token } إلى الموضع { $position }.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] أنت: القطعة { $token } +{ $spaces } إلى { $position }، آمنة.
           *[no] أنت: القطعة { $token } +{ $spaces } إلى { $position }.
        }
       *[no] { $safe ->
            [yes] تحرّك القطعة { $token } إلى الموضع { $position }، وهو مربع آمن.
           *[no] تحرّك القطعة { $token } إلى الموضع { $position }.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): القطعة { $token } +{ $spaces } إلى { $position }، آمنة.
           *[no] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): القطعة { $token } +{ $spaces } إلى { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يحرّك القطعة { $token } إلى الموضع { $position }، وهو مربع آمن.
           *[no] { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يحرّك القطعة { $token } إلى الموضع { $position }.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] أنت: القطعة { $token } +{ $spaces } إلى البيت { $position }/{ $total }.
       *[no] تحرّك القطعة { $token } إلى عمود بيتك ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }): القطعة { $token } +{ $spaces } إلى البيت { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $color }
        }) يحرّك القطعة { $token } إلى عمود البيت ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] أنت: القطعة { $token } وصلت البيت ({ $finished }/4).
       *[no] قطعتك { $token } تصل إلى البيت. ({ $finished }/4 مكتملة)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }): القطعة { $token } وصلت البيت ({ $finished }/4).
       *[no] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $color }
        }) القطعة { $token } تصل إلى البيت. ({ $finished }/4 مكتملة)
    }
ludo-you-move-home =
    { $brief ->
        [yes] أنت: القطعة { $token } +{ $spaces } إلى البيت { $position }/{ $total }.
       *[no] تحرّك القطعة { $token } داخل عمود بيتك ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }): القطعة { $token } +{ $spaces } إلى البيت { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }) يحرّك القطعة { $token } داخل عمود البيت ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes] أنت: أسر { $count } من قطع { $captured_player } ({ $captured_color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $captured_color }
        }) إلى الساحة.
       *[no] تأسر { $count ->
            [one] قطعة واحدة
           *[other] { $count } قطع
        } من قطع { $captured_player } ({ $captured_color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $captured_color }
        }) وترسل { $count ->
            [one] القطعة
           *[other] القطع
        } إلى الساحة.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }): { $count ->
            [one] قطعتك
           *[other] { $count } من قطعك
        } إلى الساحة.
       *[no] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $color }
        }) يأسر { $count ->
            [one] قطعتك
           *[other] { $count } من قطعك
        } ويرسل { $count ->
            [one] القطعة
           *[other] القطع
        } إلى الساحة.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $color }
        }): أسر { $count } من قطع { $captured_player } ({ $captured_color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
           *[other] { $captured_color }
        }) إلى الساحة.
       *[no] { $player } ({ $color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $color }
        }) يأسر { $count ->
            [one] قطعة واحدة
           *[other] { $count } قطع
        } من قطع { $captured_player } ({ $captured_color ->
            [red] أحمر
            [blue] أزرق
            [green] أخضر
            [yellow] أصفر
            *[other] { $captured_color }
        }). أُعيدت إلى الساحة.
    }
ludo-extra-turn = رمى { $player } 6. دور إضافي.
ludo-you-extra-turn = رميت 6. دور إضافي.
ludo-you-too-many-sixes = رميت الرقم 6 { $count } مرات متتالية. تُلغى تحركاتك من هذا الدور، وينتهي دورك.
ludo-too-many-sixes = رمى { $player } الرقم 6 { $count } مرات متتالية. أُلغيت التحركات. ينتهي الدور.
ludo-you-winner = لقد فزت! جميع القطع الأربع في البيت.
ludo-winner = { $player } ({ $color ->
    [red] أحمر
    [blue] أزرق
    [green] أخضر
    [yellow] أصفر
    *[other] { $color }
}) يفوز! جميع القطع الأربع في البيت.

ludo-end-score-line = { $index }. { $player }: { $count ->
    [one] قطعة واحدة في البيت
   *[other] { $count } قطع في البيت
}

ludo-board-player = { $player } ({ $color ->
    [red] أحمر
    [blue] أزرق
    [green] أخضر
    [yellow] أصفر
    *[other] { $color }
}): { $finished }/4 مكتملة
ludo-token-yard = القطعة { $token } (الساحة)
ludo-token-track =
    { $safe ->
        [yes] القطعة { $token } (الموضع { $position }، مربع آمن)
       *[no] القطعة { $token } (الموضع { $position })
    }
ludo-token-home = القطعة { $token } (عمود البيت { $position }/{ $total })
ludo-token-finished = القطعة { $token } (مكتملة)
ludo-last-roll = آخر رمية: { $roll }

ludo-set-max-sixes = الحد الأقصى لمرات الرقم 6 المتتالية: { $max_consecutive_sixes }
ludo-enter-max-sixes = أدخل الحد الأقصى لمرات الرقم 6 المتتالية
ludo-option-changed-max-sixes = تم ضبط الحد الأقصى لمرات الرقم 6 المتتالية على { $max_consecutive_sixes }.
ludo-desc-max-consecutive-sixes = كم مرة متتالية يمكن للاعب رمي الرقم 6 قبل أن يُعاقَب الدور أو يُمرَّر (الافتراضي 3، المدى 0-5).
ludo-set-safe-start-squares = مربعات البداية الآمنة: { $enabled }
ludo-option-changed-safe-start-squares = تم ضبط مربعات البداية الآمنة على { $enabled }.
ludo-desc-safe-start-squares = يتحكم في ما إذا كان مربع بداية كل لاعب يُعامَل كمربع آمن.

