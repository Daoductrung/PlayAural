# Backgammon localization

game-name-backgammon = لعبة الطاولة
# Colors
backgammon-color-red = أحمر
backgammon-color-white = ابيض
# Menu helpers
backgammon-unavailable = غير متاح
# Game start
backgammon-game-started = { $red } يلعب باللون الأحمر، { $white } يلعب الأبيض.
backgammon-opening-roll = لفة الافتتاح: { $red } لفات { $red_die }, { $white } لفات { $white_die }.
backgammon-opening-tie = كلاهما توالت { $die }، إعادة المتداول.
backgammon-opening-winner-you = اذهب أولاً مع { $die1 } و { $die2 }.
backgammon-opening-winner-player = { $player } يذهب أولاً مع { $die1 } و { $die2 }.
# Dice
backgammon-roll-you = أنت تتدحرج { $die1 } و { $die2 }.
backgammon-roll-player = { $player } لفات { $die1 } و { $die2 }.
# No moves
backgammon-no-moves-you = ليس لديك أي تحركات قانونية، لذلك ينتهي دورك.
backgammon-no-moves-player = { $player } ليس لديه تحركات قانونية، لذلك ينتهي دورهم.
# Brief move commentary
backgammon-brief-move-normal =
    { $is_self ->
        [yes] أنت: { $src } إلى { $dest }.
       *[no] { $player }: { $src } إلى { $dest }.
    }
backgammon-brief-move-hit =
    { $is_self ->
        [yes] أنت: { $src } إلى { $dest }، ضرب { $opponent }.
        [spectator] { $player }: { $src } إلى { $dest }، يضرب { $opponent }.
       *[no] { $player }: { $src } إلى { $dest }، ضربك.
    }
backgammon-brief-move-bar =
    { $is_self ->
        [yes] أنت: شريط إلى { $dest }.
       *[no] { $player }: شريط إلى { $dest }.
    }
backgammon-brief-move-bar-hit =
    { $is_self ->
        [yes] أنت: شريط إلى { $dest }، ضرب { $opponent }.
        [spectator] { $player }: شريط إلى { $dest }، ضرب { $opponent }.
       *[no] { $player }: شريط إلى { $dest }، ضربك.
    }
backgammon-brief-move-bearoff =
    { $is_self ->
        [yes] أنت: { $src } عن.
       *[no] { $player }: { $src } عن.
    }
# Verbose move commentary
backgammon-verbose-move-normal =
    { $is_self ->
        [yes] تقوم بتحريك قطعة المدقق من النقطة { $src } للإشارة { $dest }.
       *[no] { $player } يحرك قطعة المدقق من النقطة { $src } للإشارة { $dest }.
    } { $src_count ->
        [0] نقطة { $src } الآن فارغ، { $dest_count } على النقطة { $dest }.
       *[other] { $src_count } الآن على النقطة { $src }, { $dest_count } على النقطة { $dest }.
    }
backgammon-verbose-move-hit =
    { $is_self ->
        [yes] تقوم بتحريك قطعة المدقق من النقطة { $src } لالتقاط { $opponent }مدقق على النقطة { $dest }.
        [spectator] { $player } يحرك قطعة المدقق من النقطة { $src } لالتقاط { $opponent }مدقق على النقطة { $dest }.
       *[no] { $player } يحرك قطعة المدقق من النقطة { $src } لالتقاط المدقق الخاص بك على النقطة { $dest }.
    } { $src_count ->
        [0] نقطة { $src } الآن فارغ.
       *[other] { $src_count } تبقى على النقطة { $src }.
    }
backgammon-verbose-move-bar =
    { $is_self ->
        [yes] تقوم بالدخول من الشريط إلى النقطة { $dest }.
       *[no] { $player } يدخل من الشريط إلى النقطة { $dest }.
    } { $dest_count } الآن على النقطة { $dest }.
backgammon-verbose-move-bar-hit =
    { $is_self ->
        [yes] تدخل من الشريط لتلتقط { $opponent }مدقق على النقطة { $dest }.
        [spectator] { $player } يدخل من الشريط لالتقاط { $opponent }المدقق على النقطة { $dest }.
       *[no] { $player } يدخل من الشريط لالتقاط المدقق الخاص بك على النقطة { $dest }.
    }
backgammon-verbose-move-bearoff =
    { $is_self ->
        [yes] تنطلق من النقطة { $src }.
       *[no] { $player } ينطلق من النقطة { $src }.
    } { $src_count ->
        [0] نقطة { $src } الآن فارغ.
       *[other] { $src_count } تبقى على النقطة { $src }.
    }
# Doubling
backgammon-doubles-you = أنت تعرض مضاعفة المكعب إلى { $value }.
backgammon-doubles-player = { $player } عروض مضاعفة المكعب إلى { $value }.
backgammon-accepts-you = أنت تقبل المضاعفة وتحصل على ملكية المكعب.
backgammon-accepts-player = { $player } يقبل المضاعفة ويأخذ ملكية المكعب.
backgammon-drops-you = قمت بإسقاط المضاعفة والتنازل عن قيمة المكعب الحالية.
backgammon-drops-player = { $player } يسقط المضاعفة ويتنازل عن قيمة المكعب الحالية.
backgammon-accept = يقبل
backgammon-drop = إسقاط
# Point labels
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } مختارة
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count } مختارة
# Action labels
backgammon-label-double = مزدوج
backgammon-label-undo = تراجع
backgammon-label-next = التالي
backgammon-label-previous = السابق
backgammon-label-deselect = قم بإلغاء التحديد
backgammon-label-next-destination = الوجهة التالية
backgammon-label-previous-destination = الوجهة السابقة
# Selection feedback
backgammon-selected-point = النقطة المختارة { $point }, { $count } لعبة الداما.
backgammon-selected-bar = شريط المحدد.
backgammon-deselected = تم إلغاء التحديد.
backgammon-no-checkers-there = لا توجد لعبة الداما هناك.
backgammon-not-your-checkers = هذه ليست لعبة الداما الخاصة بك.
backgammon-no-moves-from-here = لا تحركات قانونية من هنا.
backgammon-must-enter-from-bar = يجب الدخول من الشريط أولا.
backgammon-illegal-move = تحرك غير قانوني.
backgammon-no-dice-remaining = لم يتبق لديك نرد لاستخدام هذا الدور.
backgammon-no-checkers-on-bar = ليس لديك لعبة الداما على الشريط للدخول.
backgammon-invalid-destination = هذه الوجهة ليست نقطة طاولة قابلة للعب.
backgammon-source-empty = نقطة { $point } ليس لديه مدقق للتحرك.
backgammon-source-opponent = نقطة { $point } تحتوي على قطع الداما الخاصة بخصمك.
backgammon-destination-blocked = نقطة { $point } تم حظره بواسطة { $count } لعبة الداما المتعارضة.
backgammon-bar-entry-blocked = لا يمكنك الدخول عند النقطة { $point }; تم حظره بواسطة { $count } لعبة الداما المتعارضة.
backgammon-no-die-for-bar-entry = لا يدخل أي من أحجار النرد المتبقية ({ $dice }) عند النقطة { $point }.
backgammon-no-die-for-destination = لا يتحرك أي من أحجار النرد المتبقية ({ $dice }) من النقطة { $src } للإشارة { $dest }.
backgammon-must-use-forced-die = يجب عليك استخدام { $dice } الآن لأن لعبة الطاولة تتطلب كلا من النرد عندما يكون ذلك ممكنًا، أو النرد الأعلى عندما يمكن لعب نرد واحد فقط.
backgammon-bearoff-not-home = لا يمكنك التخلص بعد لأنه ليس كل قطع الداما موجودة في اللوحة الرئيسية الخاصة بك.
backgammon-bearoff-blocked = لا يمكنك تحمل من { $point }-نقطة مع { $die }، لأن هناك لعبة الداما على { $blocking_point }-نقطة.
backgammon-bearoff-no-die = لا يمكنك تحمل من { $point }-أشر بالنرد المتبقي لديك ({ $die }).
backgammon-nothing-to-undo = لا يوجد شيء للتراجع عنه.
backgammon-undone = تم التراجع عن التحرك.
backgammon-cannot-double = لا يمكنك مضاعفة الآن.
backgammon-cannot-undo = لا يوجد شيء للتراجع عنه.
backgammon-not-doubling-phase = لا يوجد ضعف للرد عليه.
backgammon-need-roll-first = تحتاج إلى رمي النرد قبل تحريك قطعة الداما.
backgammon-confirm-drop-double = يؤدي الإسقاط إلى التنازل عن هذه اللعبة بقيمة المكعب الحالية. اضغط على Drop مرة أخرى خلال 10 ثوانٍ للتأكيد.
# Info keybinds
backgammon-check-status = حالة
backgammon-check-cube = مكعب
backgammon-check-pip = عدد النقاط
backgammon-check-score = النتيجة
backgammon-check-score-detailed = النتيجة التفصيلية
backgammon-check-dice = النرد
backgammon-status = الشريط الأحمر: { $bar_red }. الشريط الأبيض: { $bar_white }. اللون الأحمر: { $off_red }. الأبيض: { $off_white }.
backgammon-dice = { $dice }
backgammon-dice-none = لا النرد.
backgammon-cube-status =
    مكعب في { $value }. { $owner ->
        [center] في المنتصف، يمكن لأي من اللاعبين أن يتضاعف.
       *[other] يملكها { $owner }.
    } { $can_double ->
        [yes] المضاعفة متاحة الآن.
        [crawford] هذه لعبة كروفورد، لا يسمح بالمضاعفة.
       *[no] المضاعفة غير متاحة في الوقت الحالي.
    }
backgammon-cube-no-match = لا يوجد مكعب مزدوج في الألعاب الفردية.
backgammon-pip-count = عدد النقاط الحمراء: { $red_pip }. عدد النقاط البيضاء: { $white_pip }.
backgammon-match-score-line = { $player }: { $score } من { $match_length }.
backgammon-match-score-cube-line = مكعب: { $cube }.
# Scoring
backgammon-wins-game-you =
    لقد فزت { $points } نقطة{ $points ->
        [one] { "" }
       *[other] ق
    }.
backgammon-wins-game-player =
    { $player } يفوز { $points } نقطة{ $points ->
        [one] { "" }
       *[other] ق
    }.
backgammon-new-game = بداية اللعبة { $number }.
backgammon-match-winner-you = لقد فزت بالمباراة!
backgammon-match-winner-player = { $player } يفوز بالمباراة!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. تطابق مع { $match_length }.
backgammon-crawford = لعبة كروفورد: لا مضاعفة هذه اللعبة.
# Difficulty levels
backgammon-difficulty-random = عشوائي
backgammon-difficulty-simple = بسيط
# Options
backgammon-option-match-length = مدة المباراة: { $match_length }
backgammon-option-select-match-length = تحديد طول المباراة (1-25)
backgammon-option-changed-match-length = تم ضبط طول المطابقة على { $match_length }.
backgammon-desc-match-length = النقاط اللازمة للفوز بمباراة الطاولة. القيمة 1 هي لعبة واحدة بدون مكعب مزدوج (الافتراضي 1، النطاق من 1 إلى 25).
backgammon-option-bot-difficulty = صعوبة البوت: { $bot_difficulty }
backgammon-option-select-bot-difficulty = حدد صعوبة الروبوت
backgammon-option-changed-bot-difficulty = تم ضبط صعوبة الروبوت على { $bot_difficulty }.
backgammon-desc-bot-difficulty = يختار كيفية قيام الروبوتات بالتحركات: يلعب Random التحركات القانونية بشكل فضفاض، بينما يفضل Simple الحركات التكتيكية الأقوى.
