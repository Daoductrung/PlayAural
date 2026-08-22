game-name-ludo = لودو
ludo-roll-die = لفة يموت
ludo-move-token = نقل الرمز
ludo-move-token-n = نقل الرمز { $token }
ludo-check-board = عرض حالة اللوحة
ludo-select-token = حدد الرمز المميز للنقل:
ludo-roll = { $player } لفات { $roll }.
ludo-you-roll = أنت تتدحرج { $roll }.
ludo-no-moves = { $player } ليس لديه تحركات صالحة.
ludo-you-no-moves = ليس لديك أي تحركات صالحة.
ludo-error-roll-pending-move = لقد تدحرجت بالفعل ولديك خطوة صالحة. انقل أحد الرموز المتاحة لديك قبل التدحرج مرة أخرى.
ludo-you-enter-board =
    { $brief ->
        [yes]
            { $safe ->
                [yes] أنت: رمز { $token } خارج +{ $spaces } إلى { $position }، آمن.
               *[no] أنت: رمز { $token } خارج +{ $spaces } ل { $position }.
            }
       *[no]
            { $safe ->
                [yes] قمت بإدخال الرمز المميز { $token } على الموقف { $position }، وهي ساحة آمنة.
               *[no] قمت بإدخال الرمز المميز { $token } على الموقف { $position }.
            }
    }
ludo-enter-board =
    { $brief ->
        [yes]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }): رمز { $token } خارج +{ $spaces } إلى { $position }، آمن.
               *[no]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }): رمز مميز { $token } خارج +{ $spaces } إلى { $position }.
            }
       *[no]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }) يدخل الرمز { $token } على الموقف { $position }، وهي ساحة آمنة.
               *[no]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }) يدخل الرمز { $token } على الموقف { $position }.
            }
    }
ludo-you-move-track =
    { $brief ->
        [yes]
            { $safe ->
                [yes] أنت: رمز { $token } +{ $spaces } إلى { $position }، آمن.
               *[no] أنت: رمز { $token } +{ $spaces } إلى { $position }.
            }
       *[no]
            { $safe ->
                [yes] قمت بتحريك الرمز المميز { $token } إلى الموضع { $position }، وهي ساحة آمنة.
               *[no] قمت بتحريك الرمز المميز { $token } إلى الموضع { $position }.
            }
    }
ludo-move-track =
    { $brief ->
        [yes]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }): رمز مميز { $token } +{ $spaces } إلى { $position }، آمن.
               *[no]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }): رمز { $token } +{ $spaces } إلى { $position }.
            }
       *[no]
            { $safe ->
                [yes]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }) رمز التحرك { $token } إلى الموقف { $position }، وهي ساحة آمنة.
               *[no]
                    { $player } ({ $color ->
                        [red] أحمر
                        [blue] أزرق
                        [green] أخضر
                        [yellow] أصفر
                       *[other] { $color }
                    }) رمز التحرك { $token } إلى الموضع { $position }.
            }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] أنت: رمز { $token } +{ $spaces } الى المنزل { $position }/{ $total }.
       *[no] قمت بتحريك الرمز المميز { $token } في العمود الرئيسي الخاص بك ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): رمز مميز { $token } +{ $spaces } الى المنزل { $position }/{ $total }.
       *[no]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) رمز التحرك { $token } في العمود الرئيسي ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] أنت: رمز { $token } المنزل ({ $finished }/4).
       *[no] رمزك { $token } يصل إلى المنزل. ({ $finished }/4 انتهى)
    }
ludo-home-finish =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): رمز { $token } المنزل ({ $finished }/4).
       *[no]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) رمز { $token } يصل إلى المنزل. ({ $finished }/4 انتهى)
    }
ludo-you-move-home =
    { $brief ->
        [yes] أنت: رمز { $token } +{ $spaces } الى المنزل { $position }/{ $total }.
       *[no] قمت بتحريك الرمز المميز { $token } في عمودك الرئيسي ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): رمز { $token } +{ $spaces } الى المنزل { $position }/{ $total }.
       *[no]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) رمز التحرك { $token } في العمود الرئيسي ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes]
            أنت: التقط { $count } من { $captured_player } ({ $captured_color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $captured_color }
            }) إلى ياردة.
       *[no]
            قمت بالتقاط { $count ->
                [one] 1 رمز
               *[other] { $count } الرموز
            } من { $captured_player } ({ $captured_color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $captured_color }
            }) وأرسل { $count ->
                [one]
               *[other] لهم
            } العودة إلى الفناء.
    }
ludo-your-token-captured =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): { $count ->
                [one] رمزك
               *[other]  { $count } الخاص بك  الرموز
            } إلى الفناء.
       *[no]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يلتقط { $count ->
                [one] رمزك
               *[other] { $count } من رموزك
            } ويرسل { $count ->
                [one]
               *[other] لهم
            } العودة إلى الفناء.
    }
ludo-captures =
    { $brief ->
        [yes]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }): التقاط { $count } من { $captured_player } ({ $captured_color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $captured_color }
            }) إلى الفناء.
       *[no]
            { $player } ({ $color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $color }
            }) يلتقط { $count ->
                [one] 1 رمز
               *[other] { $count } الرموز
            } من { $captured_player } ({ $captured_color ->
                [red] أحمر
                [blue] أزرق
                [green] أخضر
                [yellow] أصفر
               *[other] { $captured_color }
            }). أرسل مرة أخرى إلى الفناء.
    }
ludo-extra-turn = { $player } توالت 6. دورة إضافية.
ludo-you-extra-turn = لقد تدحرجت 6. دورة إضافية.
ludo-you-too-many-sixes = لقد تدحرجت { $count } الستات على التوالي. تم التراجع عن تحركاتك من تسلسل الدور هذا، وينتهي دورك.
ludo-too-many-sixes = { $player } توالت { $count } الستات على التوالي. تم التراجع عن التحركات. بدوره ينتهي.
ludo-you-winner = فزت! جميع الرموز الأربعة في المنزل.
ludo-winner =
    { $player } ({ $color ->
        [red] أحمر
        [blue] أزرق
        [green] أخضر
        [yellow] أصفر
       *[other] { $color }
    }) يفوز! جميع الرموز الأربعة في المنزل.
ludo-end-score-line =
    { $index }. { $player }: { $count ->
        [one] 1 رمز مميز للمنزل
       *[other] { $count } الرموز الرئيسية
    }
ludo-board-player =
    { $player } ({ $color ->
        [red] أحمر
        [blue] أزرق
        [green] أخضر
        [yellow] أصفر
       *[other] { $color }
    }): { $finished }/4 انتهى
ludo-token-yard = الرمز { $token } (ساحة)
ludo-token-track =
    { $safe ->
        [yes] الرمز { $token } (الموضع { $position }، المربع الآمن)
       *[no] الرمز { $token } (الموضع { $position })
    }
ludo-token-home = الرمز { $token } (العمود الرئيسي { $position }/{ $total })
ludo-token-finished = الرمز { $token } (انتهى)
ludo-last-roll = آخر لفة: { $roll }
ludo-set-max-sixes = الحد الأقصى لستة متتالية: { $max_consecutive_sixes }
ludo-enter-max-sixes = أدخل الحد الأقصى لعدد الستات المتتالية
ludo-option-changed-max-sixes = تم ضبط الحد الأقصى للستات المتتالية على { $max_consecutive_sixes }.
ludo-desc-max-consecutive-sixes = كم عدد الستات المتتالية التي يمكن للاعب أن يرميها قبل معاقبة الدور أو تمريره (الافتراضي 3، النطاق 0-5).
ludo-set-safe-start-squares = مربعات البداية الآمنة: { $enabled }
ludo-option-changed-safe-start-squares = تم ضبط مربعات البداية الآمنة على { $enabled }.
ludo-desc-safe-start-squares = التحكم في ما إذا كان سيتم التعامل مع مربع البداية الخاص بكل لاعب كمربع آمن.
