game-name-ludo = لودو

ludo-roll-die = پرتاب تاس
ludo-move-token = حرکت مهره
ludo-move-token-n = حرکت مهره { $token }
ludo-check-board = مشاهده‌ی وضعیت صفحه
ludo-select-token = مهره‌ای را برای حرکت انتخاب کنید:

ludo-roll = { $player } { $roll } می‌اندازد.
ludo-you-roll = شما { $roll } می‌اندازید.
ludo-no-moves = { $player } حرکت معتبری ندارد.
ludo-you-no-moves = شما حرکت معتبری ندارید.
ludo-error-roll-pending-move = شما قبلاً تاس انداخته‌اید و یک حرکت معتبر دارید. قبل از انداختن مجدد، یکی از مهره‌های موجود خود را حرکت دهید.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] شما: مهره { $token } خارج +{ $spaces } به { $position }، امن.
           *[no] شما: مهره { $token } خارج +{ $spaces } به { $position }.
        }
       *[no] { $safe ->
            [yes] شما مهره { $token } را در موقعیت { $position } وارد می‌کنید که یک خانه‌ی امن است.
           *[no] شما مهره { $token } را در موقعیت { $position } وارد می‌کنید.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }): مهره { $token } خارج +{ $spaces } به { $position }، امن.
           *[no] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }): مهره { $token } خارج +{ $spaces } به { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }) مهره { $token } را در موقعیت { $position } وارد می‌کند که یک خانه‌ی امن است.
           *[no] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }) مهره { $token } را در موقعیت { $position } وارد می‌کند.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] شما: مهره { $token } +{ $spaces } به { $position }، امن.
           *[no] شما: مهره { $token } +{ $spaces } به { $position }.
        }
       *[no] { $safe ->
            [yes] شما مهره { $token } را به موقعیت { $position } حرکت می‌دهید که یک خانه‌ی امن است.
           *[no] شما مهره { $token } را به موقعیت { $position } حرکت می‌دهید.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }): مهره { $token } +{ $spaces } به { $position }، امن.
           *[no] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }): مهره { $token } +{ $spaces } به { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }) مهره { $token } را به موقعیت { $position } حرکت می‌دهد که یک خانه‌ی امن است.
           *[no] { $player } ({ $color ->
                [red] قرمز
                [blue] آبی
                [green] سبز
                [yellow] زرد
               *[other] { $color }
            }) مهره { $token } را به موقعیت { $position } حرکت می‌دهد.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] شما: مهره { $token } +{ $spaces } به خانه { $position }/{ $total }.
       *[no] شما مهره { $token } را به ستون خانه‌ی خود ({ $position }/{ $total }) حرکت می‌دهید.
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }): مهره { $token } +{ $spaces } به خانه { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $color }
        }) مهره { $token } را به ستون خانه ({ $position }/{ $total }) حرکت می‌دهد.
    }
ludo-you-home-finish =
    { $brief ->
        [yes] شما: مهره { $token } در خانه ({ $finished }/۴).
       *[no] مهره { $token } شما به خانه رسید. ({ $finished }/۴ کامل شد)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }): مهره { $token } در خانه ({ $finished }/۴).
       *[no] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $color }
        }) مهره { $token } به خانه رسید. ({ $finished }/۴ کامل شد)
    }
ludo-you-move-home =
    { $brief ->
        [yes] شما: مهره { $token } +{ $spaces } به خانه { $position }/{ $total }.
       *[no] شما مهره { $token } را در ستون خانه‌ی خود ({ $position }/{ $total }) حرکت می‌دهید.
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }): مهره { $token } +{ $spaces } به خانه { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }) مهره { $token } را در ستون خانه ({ $position }/{ $total }) حرکت می‌دهد.
    }
ludo-you-capture =
    { $brief ->
        [yes] شما: { $count } مهره از { $captured_player } ({ $captured_color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $captured_color }
        }) را به حیاط می‌فرستید.
       *[no] شما { $count ->
            [one] ۱ مهره
           *[other] { $count } مهره
        } از { $captured_player } ({ $captured_color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $captured_color }
        }) را می‌گیرید و به حیاط بازمی‌گردانید.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }): { $count ->
            [one] مهره‌ی شما
           *[other] { $count } مهره‌ی شما
        } به حیاط.
       *[no] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $color }
        }) { $count ->
            [one] مهره‌ی شما
           *[other] { $count } مهره‌ی شما
        } را می‌گیرد و به حیاط بازمی‌گرداند.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $color }
        }): { $count } مهره از { $captured_player } ({ $captured_color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
           *[other] { $captured_color }
        }) به حیاط.
       *[no] { $player } ({ $color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $color }
        }) { $count ->
            [one] ۱ مهره
           *[other] { $count } مهره
        } از { $captured_player } ({ $captured_color ->
            [red] قرمز
            [blue] آبی
            [green] سبز
            [yellow] زرد
            *[other] { $captured_color }
        }) را می‌گیرد. به حیاط بازگردانده شد.
    }
ludo-extra-turn = { $player } ۶ انداخت. نوبت اضافی.
ludo-you-extra-turn = شما ۶ انداختید. نوبت اضافی.
ludo-you-too-many-sixes = شما { $count } بار پشت‌سر هم ۶ انداختید. حرکت‌های این دنباله‌ی نوبت لغو شد و نوبت شما تمام شد.
ludo-too-many-sixes = { $player } { $count } بار پشت‌سر هم ۶ انداخت. حرکت‌ها لغو شد. نوبت تمام شد.
ludo-you-winner = شما برنده شدید! هر ۴ مهره در خانه هستند.
ludo-winner = { $player } ({ $color ->
    [red] قرمز
    [blue] آبی
    [green] سبز
    [yellow] زرد
    *[other] { $color }
}) برنده شد! هر ۴ مهره در خانه هستند.
ludo-end-score-line = { $index }. { $player }: { $count ->
    [one] ۱ مهره در خانه
   *[other] { $count } مهره در خانه
}

ludo-board-player = { $player } ({ $color ->
    [red] قرمز
    [blue] آبی
    [green] سبز
    [yellow] زرد
    *[other] { $color }
}): { $finished }/۴ کامل شد
ludo-token-yard = مهره { $token } (حیاط)
ludo-token-track =
    { $safe ->
        [yes] مهره { $token } (موقعیت { $position }، خانه‌ی امن)
       *[no] مهره { $token } (موقعیت { $position })
    }
ludo-token-home = مهره { $token } (ستون خانه { $position }/{ $total })
ludo-token-finished = مهره { $token } (کامل شد)
ludo-last-roll = آخرین پرتاب: { $roll }

ludo-set-max-sixes = حداکثر شش‌های پشت‌سرهم: { $max_consecutive_sixes }
ludo-enter-max-sixes = حداکثر شش‌های پشت‌سرهم را وارد کنید
ludo-option-changed-max-sixes = حداکثر شش‌های پشت‌سرهم روی { $max_consecutive_sixes } تنظیم شد.
ludo-desc-max-consecutive-sixes = تعداد شش‌های پشت‌سرهم که یک بازیکن می‌تواند قبل از جریمه یا پایان نوبت بیندازد (پیش‌فرض ۳، محدوده ۰-۵).
ludo-set-safe-start-squares = خانه‌های شروع امن: { $enabled }
ludo-option-changed-safe-start-squares = خانه‌های شروع امن روی { $enabled } تنظیم شد.
ludo-desc-safe-start-squares = کنترل می‌کند که آیا خانه‌ی شروع هر بازیکن به عنوان خانه‌ی امن در نظر گرفته می‌شود یا نه.