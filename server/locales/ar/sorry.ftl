game-name-sorry = سوري!

sorry-set-rules-profile = ملف القواعد: { $profile }
sorry-select-rules-profile = اختر ملف قواعد
sorry-option-changed-rules-profile = تم ضبط ملف القواعد على { $profile }.
sorry-desc-rules-profile = يختار ملف قواعد سوري، بما في ذلك مجموعة أوراق 00390 الكلاسيكية أو قواعد النواة الأحدث بنمط A5065.
sorry-rules-profile-classic-00390 = الكلاسيكية 00390
sorry-rules-profile-a5065-core = نواة A5065

sorry-toggle-auto-apply-single-move = التطبيق التلقائي للتحرك الوحيد: { $enabled }
sorry-option-changed-auto-apply-single-move = تم ضبط التطبيق التلقائي للتحرك الوحيد على { $enabled }.
sorry-desc-auto-apply-single-move = عند التفعيل، تُطبَّق تلقائيًا أي ورقة لها تحرك قانوني واحد فقط.
sorry-toggle-faster-setup-one-pawn-out = إعداد أسرع (بيدق واحد خارج): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = تم ضبط الإعداد الأسرع على { $enabled }.
sorry-desc-faster-setup-one-pawn-out = يبدأ كل لاعب ببيدق واحد خارج البداية بالفعل لتقليل الانتظار المبكر.
sorry-error-unsupported-rules-profile = ملف قواعد سوري المحدد "{ $profile }" غير مدعوم. اختر الكلاسيكية 00390 أو نواة A5065 قبل البدء.

sorry-draw-card = سحب ورقة
sorry-check-board = قراءة اللوحة
sorry-check-pawns = تفقّد بيادقك
sorry-check-card = تفقّد الورقة الحالية
sorry-check-status = تفقّد الحالة

sorry-move-slot = خيار التحرك { $slot }
sorry-move-slot-fallback = اختر تحركًا
sorry-move-start = حرّك البيدق { $pawn } من { $position } خارج البداية
sorry-move-forward = حرّك البيدق { $pawn } من { $position } للأمام { $steps }
sorry-move-backward = حرّك البيدق { $pawn } من { $position } للخلف { $steps }
sorry-move-swap = بدّل البيدق { $pawn } عند { $position } مع بيدق { $target_player } { $target_pawn } عند { $target_position }
sorry-move-sorry = استخدم سوري! بالبيدق { $pawn } عند { $position } ضد بيدق { $target_player } { $target_pawn } عند { $target_position }
sorry-move-split7-pick = قسّم الـ7 بين البيدق { $pawn_a } عند { $position_a } والبيدق { $pawn_b } عند { $position_b }
sorry-move-split7-option = البيدق { $pawn_a } عند { $position_a } يتحرك { $steps_a }، والبيدق { $pawn_b } عند { $position_b } يتحرك { $steps_b }

sorry-card-none = لا توجد ورقة نشطة
sorry-card-sorry = سوري!
sorry-choose-move = اختر تحركًا.
sorry-choose-split = اختر كيفية تقسيم الـ7.
sorry-error-draw-pending-move = لقد سحبت ورقة بالفعل. اختر أحد التحركات المتاحة لتلك الورقة قبل السحب مرة أخرى.

sorry-game-started = تبدأ سوري. اللاعبون: { $players }.
sorry-draw-announcement = يسحب { $player } { $card }.
sorry-you-draw-announcement = تسحب { $card }.
sorry-no-legal-moves = ليس لدى { $player } تحرك قانوني لـ { $card }.
sorry-you-no-legal-moves = ليس لديك تحرك قانوني لـ { $card }.
sorry-deck-exhausted = مجموعة أوراق سوري فارغة، لذا تنتهي اللعبة هنا.
sorry-you-extra-turn = سحبت 2 وتحصل على دور آخر.
sorry-player-extra-turn = سحب { $player } 2 ويحصل على دور آخر.

sorry-play-start =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } من البداية إلى { $destination }.
       *[no] يُخرج { $player } البيدق { $pawn } إلى { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] أنت: البيدق { $pawn } من البداية إلى { $destination }.
       *[no] تُخرج البيدق { $pawn } إلى { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } +{ $steps } إلى { $destination }.
       *[no] يحرّك { $player } البيدق { $pawn } للأمام { $steps } مربعات إلى { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] أنت: البيدق { $pawn } +{ $steps } إلى { $destination }.
       *[no] تحرّك البيدق { $pawn } للأمام { $steps } مربعات إلى { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } -{ $steps } إلى { $destination }.
       *[no] يحرّك { $player } البيدق { $pawn } للخلف { $steps } مربعات إلى { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] أنت: البيدق { $pawn } -{ $steps } إلى { $destination }.
       *[no] تحرّك البيدق { $pawn } للخلف { $steps } مربعات إلى { $destination }.
    }

sorry-play-swap =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } يبادل بيدق { $target_player } { $target_pawn }؛ { $destination }.
       *[no] يبادل { $player } البيدق { $pawn } مع بيدق { $target_player } { $target_pawn } وينتهي عند { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] أنت: البيدق { $pawn } يبادل بيدق { $target_player } { $target_pawn }؛ { $destination }.
       *[no] تبادل البيدق { $pawn } مع بيدق { $target_player } { $target_pawn } وتنتهي عند { $destination }.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: سوري! البيدق { $pawn } إلى { $destination }؛ بيدق { $target_player } { $target_pawn } إلى البداية.
       *[no] يلعب { $player } سوري!، ويزيح بيدق { $target_player } { $target_pawn }، وينتهي عند { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] أنت: سوري! البيدق { $pawn } إلى { $destination }؛ بيدق { $target_player } { $target_pawn } إلى البداية.
       *[no] تلعب سوري!، وتزيح بيدق { $target_player } { $target_pawn }، وتنتهي عند { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: البيدق { $pawn_a } +{ $steps_a } إلى { $destination_a }؛ البيدق { $pawn_b } +{ $steps_b } إلى { $destination_b }.
       *[no] يقسّم { $player } الـ7: البيدق { $pawn_a } يتحرك { $steps_a } مربعات إلى { $destination_a }، والبيدق { $pawn_b } يتحرك { $steps_b } مربعات إلى { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] أنت: البيدق { $pawn_a } +{ $steps_a } إلى { $destination_a }؛ البيدق { $pawn_b } +{ $steps_b } إلى { $destination_b }.
       *[no] تقسّم الـ7: البيدق { $pawn_a } يتحرك { $steps_a } مربعات إلى { $destination_a }، والبيدق { $pawn_b } يتحرك { $steps_b } مربعات إلى { $destination_b }.
    }

sorry-pawn-home = يُدخل { $player } البيدق { $pawn } إلى البيت.
sorry-you-pawn-home = يصل بيدقك { $pawn } إلى البيت.

sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: بيدقك { $pawn } إلى البداية.
       *[no] أُعيد بيدقك { $pawn } إلى البداية بإزاحة من { $by_player }.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] أنت: بيدق { $target_player } { $pawn } إلى البداية.
       *[no] تُزيح بيدق { $target_player } { $pawn } عائدًا إلى البداية.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: بيدق { $target_player } { $pawn } إلى البداية.
       *[no] يُزيح { $player } بيدق { $target_player } { $pawn } عائدًا إلى البداية.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] أنت: بيدقك { $pawn } إلى البداية.
       *[no] تُزيح بيدقك { $pawn } عائدًا إلى البداية.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: البيدق الخاص { $pawn } إلى البداية.
       *[no] يُزيح { $player } بيدق { GENDER_TERM($player_gender, "possessive-determiner") } الخاص { $pawn } عائدًا إلى البداية.
    }
sorry-current-card = الورقة الحالية: { $card }.
sorry-view-your-pawn = بيدقك { $pawn }: { $zone }.
sorry-board-your-color = لونك: { $color }.
sorry-board-summary-heading = ملخص سريع:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = البيدق { $pawn } عند { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = مربعات المسار:
sorry-board-private-areas-heading = المناطق الخاصة:
sorry-board-square-line = المربع { $square }: { $status }
sorry-board-square-empty = فارغ
sorry-board-square-slide = انزلاق { $color }
sorry-board-square-token = بيدق { $pawn } لـ { $player }
sorry-board-start-line = منطقة بداية { $color } لـ { $player }: { $pawns }
sorry-board-safety-line = مساحة أمان { $color } { $space } لـ { $player }: { $pawns }
sorry-board-home-line = بيت { $color } لـ { $player }: { $pawns }
sorry-board-area-empty = فارغ
sorry-board-area-pawn = البيدق { $pawn }
sorry-color-red = أحمر
sorry-color-blue = أزرق
sorry-color-yellow = أصفر
sorry-color-green = أخضر
sorry-location-start = البداية
sorry-location-track = المربع { $position }
sorry-location-home-path = مساحة أمان { $steps }
sorry-location-home = البيت
sorry-zone-start = في البداية
sorry-zone-track = على مربع المسار { $position }
sorry-zone-home-path = في منطقة الأمان الخطوة { $steps }
sorry-zone-home = البيت

sorry-status-turn-number = الدور { $count }
sorry-status-phase = المرحلة: { $phase }
sorry-status-current-card = الورقة: { $card }
sorry-status-current-player = اللاعب الحالي: { $player }
sorry-phase-draw = سحب
sorry-phase-choose-move = اختيار التحرك
sorry-phase-choose-split = تقسيم السبعة
sorry-phase-resolving = تنفيذ التحرك

sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] بيدق واحد في البيت
   *[other] { $count } بيادق في البيت
}
