game-name-sorry = آسف!
sorry-set-rules-profile = ملف القواعد: { $profile }
sorry-select-rules-profile = اختر ملف تعريف القواعد
sorry-option-changed-rules-profile = تم تعيين ملف تعريف القواعد على { $profile }.
sorry-desc-rules-profile = يختار ملف تعريف قواعد آسف، بما في ذلك مجموعة 00390 الكلاسيكية أو القواعد الأساسية الأحدث على طراز A5065.
sorry-rules-profile-classic-00390 = كلاسيك 00390
sorry-rules-profile-a5065-core = A5065 كور
sorry-toggle-auto-apply-single-move = تطبيق تلقائي لحركة واحدة: { $enabled }
sorry-option-changed-auto-apply-single-move = تطبيق تلقائي لحركة واحدة مضبوطة على { $enabled }.
sorry-desc-auto-apply-single-move = عند التمكين، يتم تطبيق البطاقة التي تحتوي على حركة قانونية واحدة فقط تلقائيًا.
sorry-toggle-faster-setup-one-pawn-out = إعداد أسرع (بيدق واحد): { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = تم ضبط الإعداد الأسرع على { $enabled }.
sorry-desc-faster-setup-one-pawn-out = يبدأ كل لاعب ببيدق واحد خارج بالفعل لتقليل الانتظار المبكر.
sorry-error-unsupported-rules-profile = ملف تعريف قواعد آسف المحدد "{ $profile }" غير مدعوم. اختر Classic 00390 أو A5065 Core قبل البدء.
sorry-draw-card = سحب البطاقة
sorry-check-board = قراءة المجلس
sorry-check-pawns = تحقق من بيادقك
sorry-check-card = التحقق من البطاقة الحالية
sorry-check-status = التحقق من الحالة
sorry-move-slot = خيار النقل { $slot }
sorry-move-slot-fallback = اختر نقل
sorry-move-start = تحريك البيدق { $pawn } من { $position } من البداية
sorry-move-forward = تحريك البيدق { $pawn } من { $position } إلى الأمام { $steps }
sorry-move-backward = تحريك البيدق { $pawn } من { $position } الى الوراء { $steps }
sorry-move-swap = مبادلة البيدق { $pawn } في { $position } مع { $target_player } البيدق { $target_pawn } في { $target_position }
sorry-move-sorry = استخدم آسف! مع البيدق { $pawn } في { $position } ضد { $target_player } البيدق { $target_pawn } في { $target_position }
sorry-move-split7-pick = تقسيم 7 بين البيدق { $pawn_a } في { $position_a } والرهن { $pawn_b } في { $position_b }
sorry-move-split7-option = البيدق { $pawn_a } في { $position_a } تحركات { $steps_a }، البيدق { $pawn_b } في { $position_b } تحركات { $steps_b }
sorry-card-none = لا توجد بطاقة نشطة
sorry-card-sorry = آسف!
sorry-choose-move = اختر خطوة.
sorry-choose-split = اختر كيفية تقسيم 7.
sorry-error-draw-pending-move = لقد قمت بالفعل برسم بطاقة. اختر إحدى الحركات المتاحة لتلك البطاقة قبل الرسم مرة أخرى.
sorry-game-started = آسف يبدأ. اللاعبين: { $players }.
sorry-draw-announcement = { $player } رسم { $card }.
sorry-you-draw-announcement = أنت ترسم { $card }.
sorry-no-legal-moves = { $player } ليس له أي تحرك قانوني لـ { $card }.
sorry-you-no-legal-moves = ليس لديك أي تحرك قانوني لـ { $card }.
sorry-deck-exhausted = مجموعة آسف فارغة، لذا تنتهي اللعبة هنا.
sorry-you-extra-turn = لقد رسمت 2 وأخذت منعطفًا آخر.
sorry-player-extra-turn = { $player } رسم 2 ويأخذ منعطفًا آخر.
sorry-play-start =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } البدء في { $destination }.
       *[no] { $player } يجلب البيدق { $pawn } إلى { $destination }.
    }
sorry-you-play-start =
    { $brief ->
        [yes] أنت : البيدق { $pawn } البدء في { $destination }.
       *[no] تحضر البيدق { $pawn } إلى { $destination }.
    }
sorry-play-forward =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } +{ $steps } إلى { $destination }.
       *[no] { $player } تحركات البيدق { $pawn } إلى الأمام { $steps } مسافات إلى { $destination }.
    }
sorry-you-play-forward =
    { $brief ->
        [yes] أنت : البيدق { $pawn } +{ $steps } إلى { $destination }.
       *[no] قمت بتحريك البيدق { $pawn } إلى الأمام { $steps } مسافات إلى { $destination }.
    }
sorry-play-backward =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } -{ $steps } إلى { $destination }.
       *[no] { $player } تحركات البيدق { $pawn } الى الوراء { $steps } مسافات إلى { $destination }.
    }
sorry-you-play-backward =
    { $brief ->
        [yes] أنت : البيدق { $pawn } -{ $steps } إلى { $destination }.
       *[no] قمت بتحريك البيدق { $pawn } الى الوراء { $steps } مسافات إلى { $destination }.
    }
sorry-play-swap =
    { $brief ->
        [yes] { $player }: البيدق { $pawn } مقايضة { $target_player } البيدق { $target_pawn }; { $destination }.
       *[no] { $player } مقايضة البيدق { $pawn } مع { $target_player } البيدق { $target_pawn } وينتهي في { $destination }.
    }
sorry-you-play-swap =
    { $brief ->
        [yes] أنت : البيدق { $pawn } مقايضة { $target_player } البيدق { $target_pawn }; { $destination }.
       *[no] قمت بتبديل البيدق { $pawn } مع { $target_player } البيدق { $target_pawn } والانتهاء من { $destination }.
    }
sorry-play-sorry =
    { $brief ->
        [yes] { $player }: آسف! البيدق { $pawn } إلى { $destination }; { $target_player } بيدق { $target_pawn } يبدأ.
       *[no] { $player } يلعب آسف!، ليحل محل { $target_player } البيدق { $target_pawn }، وينتهي في { $destination }.
    }
sorry-you-play-sorry =
    { $brief ->
        [yes] أنت: آسف! البيدق { $pawn } إلى { $destination }; { $target_player } البيدق { $target_pawn } يبدأ.
       *[no] أنت تلعب آسف!، استبدل { $target_player } البيدق { $target_pawn }، والانتهاء في { $destination }.
    }
sorry-play-split7 =
    { $brief ->
        [yes] { $player }: البيدق { $pawn_a } +{ $steps_a } إلى { $destination_a }; البيدق { $pawn_b } +{ $steps_b } ل { $destination_b }.
       *[no] { $player } الانقسامات 7: البيدق { $pawn_a } تحركات { $steps_a } مسافات إلى { $destination_a }، والرهن { $pawn_b } تحركات { $steps_b } مسافات إلى { $destination_b }.
    }
sorry-you-play-split7 =
    { $brief ->
        [yes] أنت : البيدق { $pawn_a } +{ $steps_a } إلى { $destination_a }; البيدق { $pawn_b } +{ $steps_b } إلى { $destination_b }.
       *[no] قمت بتقسيم 7: البيدق { $pawn_a } تحركات { $steps_a } مسافات إلى { $destination_a }، والرهن { $pawn_b } التحركات { $steps_b } مسافات إلى { $destination_b }.
    }
sorry-pawn-home = { $player } يحصل على البيدق { $pawn } بيت.
sorry-you-pawn-home = بيدقك { $pawn } يصل إلى المنزل.
sorry-your-pawn-captured =
    { $brief ->
        [yes] { $by_player }: بيدقك { $pawn } للبدء.
       *[no] بيدقك { $pawn } تم ارتداؤه مرة أخرى للبدء بـ { $by_player }.
    }
sorry-you-captured-pawn =
    { $brief ->
        [yes] أنت: { $target_player } البيدق { $pawn } للبدء.
       *[no] أنت عثرة { $target_player } البيدق { $pawn } العودة للبدء.
    }
sorry-pawn-captured =
    { $brief ->
        [yes] { $player }: { $target_player } البيدق { $pawn } للبدء.
       *[no] { $player } المطبات { $target_player } البيدق { $pawn } العودة للبدء.
    }
sorry-you-bumped-own-pawn =
    { $brief ->
        [yes] أنت: بيدق خاص { $pawn } للبدء.
       *[no] أنت تصطدم ببيدقك { $pawn } العودة للبدء.
    }
sorry-player-bumped-own-pawn =
    { $brief ->
        [yes] { $player }: البيدق الخاص { $pawn } للبدء.
       *[no] { $player } يصطدم بيدقهم { $pawn } العودة للبدء.
    }
sorry-current-card = البطاقة الحالية: { $card }.
sorry-view-your-pawn = بيدقك { $pawn }: { $zone }.
sorry-board-your-color = لونك : { $color }.
sorry-board-summary-heading = ملخص سريع:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = البيدق { $pawn } في { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = مربعات المسار:
sorry-board-private-areas-heading = المناطق الخاصة:
sorry-board-square-line = ساحة { $square }: { $status }
sorry-board-square-empty = فارغة
sorry-board-square-slide = { $color } الشريحة
sorry-board-square-token = البيدق { $pawn } من { $player }
sorry-board-start-line = { $color } منطقة البداية { $player }: { $pawns }
sorry-board-safety-line = { $color } مساحة الأمان { $space } من { $player }: { $pawns }
sorry-board-home-line = { $color } منزل { $player }: { $pawns }
sorry-board-area-empty = فارغة
sorry-board-area-pawn = البيدق { $pawn }
sorry-color-red = أحمر
sorry-color-blue = أزرق
sorry-color-yellow = أصفر
sorry-color-green = أخضر
sorry-location-start = ابدأ
sorry-location-track = مربع { $position }
sorry-location-home-path = مساحة الأمان { $steps }
sorry-location-home = الصفحة الرئيسية
sorry-zone-start = في البداية
sorry-zone-track = في ساحة المسار { $position }
sorry-zone-home-path = في خطوة منطقة الأمان { $steps }
sorry-zone-home = الصفحة الرئيسية
sorry-status-turn-number = بدوره { $count }
sorry-status-phase = المرحلة: { $phase }
sorry-status-current-card = البطاقة: { $card }
sorry-status-current-player = اللاعب الحالي: { $player }
sorry-phase-draw = رسم
sorry-phase-choose-move = اختر التحرك
sorry-phase-choose-split = سبليت سبعة
sorry-phase-resolving = خطوة حل
sorry-end-score-line =
    { $index }. { $player }: { $count ->
        [one] 1 بيدق المنزل
       *[other] { $count } بيادق المنزل
    }
