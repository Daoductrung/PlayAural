game-name-sorry = ببخشید!

sorry-set-rules-profile = پروفایل قوانین: { $profile }
sorry-select-rules-profile = یک پروفایل قوانین را انتخاب کنید
sorry-option-changed-rules-profile = پروفایل قوانین روی { $profile } تنظیم شد.
sorry-desc-rules-profile = پروفایل قوانین ببخشید را انتخاب می‌کند، شامل دسته‌ی کلاسیک ۰۰۳۹۰ یا قوانین اصلی جدیدتر A5065.
sorry-rules-profile-classic-00390 = کلاسیک ۰۰۳۹۰
sorry-rules-profile-a5065-core = اصلی A5065

sorry-toggle-auto-apply-single-move = اعمال خودکار حرکت تکی: { $enabled }
sorry-option-changed-auto-apply-single-move = اعمال خودکار حرکت تکی روی { $enabled } تنظیم شد.
sorry-desc-auto-apply-single-move = وقتی فعال باشد، کارتی که فقط یک حرکت قانونی دارد به‌طور خودکار اعمال می‌شود.
sorry-toggle-faster-setup-one-pawn-out = راه‌اندازی سریع‌تر (یک مهره خارج): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = راه‌اندازی سریع‌تر روی { $enabled } تنظیم شد.
sorry-desc-faster-setup-one-pawn-out = هر بازیکن را با یک مهره که قبلاً خارج شده شروع می‌کند تا انتظار اولیه کاهش یابد.
sorry-error-unsupported-rules-profile = پروفایل قوانین ببخشید انتخاب‌شده "{ $profile }" پشتیبانی نمی‌شود. قبل از شروع، کلاسیک ۰۰۳۹۰ یا اصلی A5065 را انتخاب کنید.

sorry-draw-card = کشیدن کارت
sorry-check-board = مشاهده‌ی صفحه
sorry-check-pawns = بررسی مهره‌های خود
sorry-check-card = بررسی کارت فعلی
sorry-check-status = بررسی وضعیت

sorry-move-slot = گزینه‌ی حرکت { $slot }
sorry-move-slot-fallback = انتخاب حرکت
sorry-move-start = حرکت مهره { $pawn } از { $position } خارج از شروع
sorry-move-forward = حرکت مهره { $pawn } از { $position } به جلو { $steps }
sorry-move-backward = حرکت مهره { $pawn } از { $position } به عقب { $steps }
sorry-move-swap = جابه‌جایی مهره { $pawn } در { $position } با مهره‌ی { $target_player } { $target_pawn } در { $target_position }
sorry-move-sorry = استفاده از ببخشید! با مهره { $pawn } در { $position } علیه مهره‌ی { $target_player } { $target_pawn } در { $target_position }
sorry-move-split7-pick = تقسیم ۷ بین مهره { $pawn_a } در { $position_a } و مهره { $pawn_b } در { $position_b }
sorry-move-split7-option = مهره { $pawn_a } در { $position_a } { $steps_a } حرکت می‌کند، مهره { $pawn_b } در { $position_b } { $steps_b } حرکت می‌کند

sorry-card-none = بدون کارت فعال
sorry-card-sorry = ببخشید!
sorry-choose-move = یک حرکت انتخاب کنید.
sorry-choose-split = نحوه‌ی تقسیم ۷ را انتخاب کنید.
sorry-error-draw-pending-move = شما قبلاً یک کارت کشیده‌اید. قبل از کشیدن مجدد، یکی از حرکت‌های موجود برای آن کارت را انتخاب کنید.

sorry-game-started = ببخشید آغاز شد. بازیکنان: { $players }.
sorry-draw-announcement = { $player } { $card } می‌کشد.
sorry-you-draw-announcement = شما { $card } می‌کشید.
sorry-no-legal-moves = { $player } برای { $card } حرکت قانونی ندارد.
sorry-you-no-legal-moves = شما برای { $card } حرکت قانونی ندارید.
sorry-deck-exhausted = دسته‌ی ببخشید خالی است، بنابراین بازی در اینجا به پایان می‌رسد.
sorry-you-extra-turn = شما ۲ کشیدید و یک نوبت دیگر می‌گیرید.
sorry-player-extra-turn = { $player } ۲ کشید و یک نوبت دیگر می‌گیرد.

sorry-play-start =
    { $brief ->
        [yes] { $player }: مهره { $pawn } شروع به { $destination }.
       *[no] { $player } مهره { $pawn } را به { $destination } می‌آورد.
    }
sorry-you-play-start =
    { $brief ->
        [yes] شما: مهره { $pawn } شروع به { $destination }.
       *[no] شما مهره { $pawn } را به { $destination } می‌آورید.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: مهره { $pawn } +{ $steps } به { $destination }.
       *[no] { $player } مهره { $pawn } را { $steps } خانه به جلو به { $destination } حرکت می‌دهد.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] شما: مهره { $pawn } +{ $steps } به { $destination }.
       *[no] شما مهره { $pawn } را { $steps } خانه به جلو به { $destination } حرکت می‌دهید.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: مهره { $pawn } -{ $steps } به { $destination }.
       *[no] { $player } مهره { $pawn } را { $steps } خانه به عقب به { $destination } حرکت می‌دهد.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] شما: مهره { $pawn } -{ $steps } به { $destination }.
       *[no] شما مهره { $pawn } را { $steps } خانه به عقب به { $destination } حرکت می‌دهید.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: مهره { $pawn } با مهره‌ی { $target_player } { $target_pawn } جابه‌جا می‌شود؛ { $destination }.
       *[no] { $player } مهره { $pawn } را با مهره‌ی { $target_player } { $target_pawn } جابه‌جا می‌کند و در { $destination } تمام می‌کند.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] شما: مهره { $pawn } با مهره‌ی { $target_player } { $target_pawn } جابه‌جا می‌شود؛ { $destination }.
       *[no] شما مهره { $pawn } را با مهره‌ی { $target_player } { $target_pawn } جابه‌جا می‌کنید و در { $destination } تمام می‌کنید.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: ببخشید! مهره { $pawn } به { $destination }; مهره‌ی { $target_player } { $target_pawn } به شروع.
       *[no] { $player } ببخشید! بازی می‌کند، مهره‌ی { $target_player } { $target_pawn } را جایگزین می‌کند و در { $destination } تمام می‌کند.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] شما: ببخشید! مهره { $pawn } به { $destination }; مهره‌ی { $target_player } { $target_pawn } به شروع.
       *[no] شما ببخشید! بازی می‌کنید، مهره‌ی { $target_player } { $target_pawn } را جایگزین می‌کنید و در { $destination } تمام می‌کنید.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: مهره { $pawn_a } +{ $steps_a } به { $destination_a }; مهره { $pawn_b } +{ $steps_b } به { $destination_b }.
       *[no] { $player } ۷ را تقسیم می‌کند: مهره { $pawn_a } { $steps_a } خانه به { $destination_a } حرکت می‌کند، و مهره { $pawn_b } { $steps_b } خانه به { $destination_b } حرکت می‌کند.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] شما: مهره { $pawn_a } +{ $steps_a } به { $destination_a }; مهره { $pawn_b } +{ $steps_b } به { $destination_b }.
       *[no] شما ۷ را تقسیم می‌کنید: مهره { $pawn_a } { $steps_a } خانه به { $destination_a } حرکت می‌کند، و مهره { $pawn_b } { $steps_b } خانه به { $destination_b } حرکت می‌کند.
    }

sorry-pawn-home = { $player } مهره { $pawn } را به خانه رساند.
sorry-you-pawn-home = مهره { $pawn } شما به خانه رسید.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: مهره { $pawn } شما به شروع.
       *[no] مهره { $pawn } شما توسط { $by_player } به شروع برگردانده شد.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] شما: مهره‌ی { $target_player } { $pawn } به شروع.
       *[no] شما مهره‌ی { $target_player } { $pawn } را به شروع برمی‌گردانید.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: مهره‌ی { $target_player } { $pawn } به شروع.
       *[no] { $player } مهره‌ی { $target_player } { $pawn } را به شروع برمی‌گرداند.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] شما: مهره‌ی خود { $pawn } به شروع.
       *[no] شما مهره‌ی خود { $pawn } را به شروع برمی‌گردانید.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: مهره‌ی خود { $pawn } به شروع.
       *[no] { $player } مهره‌ی خود { $pawn } را به شروع برمی‌گرداند.
    }

sorry-current-card = کارت فعلی: { $card }.
sorry-view-your-pawn = مهره‌ی شما { $pawn }: { $zone }.
sorry-board-your-color = رنگ شما: { $color }.
sorry-board-summary-heading = خلاصه‌ی سریع:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = مهره { $pawn } در { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = خانه‌های مسیر:
sorry-board-private-areas-heading = مناطق خصوصی:
sorry-board-square-line = خانه‌ی { $square }: { $status }
sorry-board-square-empty = خالی
sorry-board-square-slide = سرسره‌ی { $color }
sorry-board-square-token = مهره { $pawn } از { $player }
sorry-board-start-line = منطقه‌ی شروع { $color } { $player }: { $pawns }
sorry-board-safety-line = فضای امن { $color } { $space } { $player }: { $pawns }
sorry-board-home-line = خانه‌ی { $color } { $player }: { $pawns }
sorry-board-area-empty = خالی
sorry-board-area-pawn = مهره { $pawn }
sorry-color-red = قرمز
sorry-color-blue = آبی
sorry-color-yellow = زرد
sorry-color-green = سبز
sorry-location-start = شروع
sorry-location-track = خانه‌ی { $position }
sorry-location-home-path = فضای امن { $steps }
sorry-location-home = خانه
sorry-zone-start = در شروع
sorry-zone-track = در خانه‌ی مسیر { $position }
sorry-zone-home-path = در منطقه‌ی امن مرحله‌ی { $steps }
sorry-zone-home = خانه

sorry-status-turn-number = نوبت { $count }
sorry-status-phase = مرحله: { $phase }
sorry-status-current-card = کارت: { $card }
sorry-status-current-player = بازیکن فعلی: { $player }
sorry-phase-draw = کشیدن
sorry-phase-choose-move = انتخاب حرکت
sorry-phase-choose-split = تقسیم هفت
sorry-phase-resolving = در حال اجرای حرکت

sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] ۱ مهره در خانه
   *[other] { $count } مهره در خانه
}