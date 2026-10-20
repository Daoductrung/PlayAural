# Backgammon localization

game-name-backgammon = الطاولة

# Colors
backgammon-color-red = أحمر
backgammon-color-white = أبيض

# Game start
backgammon-game-started = { $red } يلعب بالأحمر، { $white } يلعب بالأبيض.
backgammon-game-started-you-red = أنت تلعب بالأحمر. { $opponent } يلعب بالأبيض.
backgammon-game-started-you-white = أنت تلعب بالأبيض. { $opponent } يلعب بالأحمر.
backgammon-opening-roll = رمية الافتتاح: { $red } يرمي { $red_die }، { $white } يرمي { $white_die }.
backgammon-opening-roll-you = رمية الافتتاح: ترمي { $your_die }، { $opponent } يرمي { $opponent_die }.
backgammon-opening-tie = رمى كلاكما { $die }، تُعاد الرمية.
backgammon-opening-winner-you = تبدأ أولاً بـ { $die1 } و{ $die2 }.
backgammon-opening-winner-player = { $player } يبدأ أولاً بـ { $die1 } و{ $die2 }.

# Dice
backgammon-roll-you = ترمي { $die1 } و{ $die2 }.
backgammon-roll-player = { $player } يرمي { $die1 } و{ $die2 }.

# No moves
backgammon-no-moves-you = ليست لديك تحركات قانونية، لذا ينتهي دورك.
backgammon-no-moves-player = { $player } ليست لديه تحركات قانونية، لذا ينتهي دور { GENDER_TERM($player_gender, "possessive-determiner") }.

# Brief move commentary
backgammon-brief-move-normal = { $is_self ->
    [yes] أنت: { $src } إلى { $dest }.
    *[no] { $player }: { $src } إلى { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] أنت: { $src } إلى { $dest }، وأصبت { $opponent }.
    [spectator] { $player }: { $src } إلى { $dest }، وأصاب { $opponent }.
    *[no] { $player }: { $src } إلى { $dest }، وأصابك.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] أنت: من الحاجز إلى { $dest }.
    *[no] { $player }: من الحاجز إلى { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] أنت: من الحاجز إلى { $dest }، وأصبت { $opponent }.
    [spectator] { $player }: من الحاجز إلى { $dest }، وأصاب { $opponent }.
    *[no] { $player }: من الحاجز إلى { $dest }، وأصابك.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] أنت: إخراج من { $src }.
    *[no] { $player }: إخراج من { $src }.
}
# Verbose move commentary
backgammon-verbose-move-normal = { $is_self ->
    [yes] تنقل قطعة من النقطة { $src } إلى النقطة { $dest }.
    *[no] { $player } ينقل قطعة من النقطة { $src } إلى النقطة { $dest }.
} { $src_count ->
    [0] النقطة { $src } أصبحت فارغة الآن، و{ $dest_count } على النقطة { $dest }.
    *[other] { $src_count } الآن على النقطة { $src }، و{ $dest_count } على النقطة { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] تنقل قطعة من النقطة { $src } لتأسر قطعة { $opponent } على النقطة { $dest }.
    [spectator] { $player } ينقل قطعة من النقطة { $src } ليأسر قطعة { $opponent } على النقطة { $dest }.
    *[no] { $player } ينقل قطعة من النقطة { $src } ليأسر قطعتك على النقطة { $dest }.
} { $src_count ->
    [0] النقطة { $src } أصبحت فارغة الآن.
    *[other] { $src_count } متبقية على النقطة { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] تدخل من الحاجز إلى النقطة { $dest }.
    *[no] { $player } يدخل من الحاجز إلى النقطة { $dest }.
} { $dest_count } الآن على النقطة { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] تدخل من الحاجز لتأسر قطعة { $opponent } على النقطة { $dest }.
    [spectator] { $player } يدخل من الحاجز ليأسر قطعة { $opponent } على النقطة { $dest }.
    *[no] { $player } يدخل من الحاجز ليأسر قطعتك على النقطة { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] تُخرج قطعة من النقطة { $src }.
    *[no] { $player } يُخرج قطعة من النقطة { $src }.
} { $src_count ->
    [0] النقطة { $src } أصبحت فارغة الآن.
    *[other] { $src_count } متبقية على النقطة { $src }.
}
# Doubling
backgammon-doubles-you = تعرض مضاعفة المكعب إلى { $value }.
backgammon-doubles-player = { $player } يعرض مضاعفة المكعب إلى { $value }.
backgammon-accepts-you = تقبل المضاعفة وتتولى ملكية المكعب.
backgammon-accepts-player = { $player } يقبل المضاعفة ويتولى ملكية المكعب.
backgammon-drops-you = ترفض المضاعفة وتتنازل عن قيمة المكعب الحالية.
backgammon-drops-player = { $player } يرفض المضاعفة ويتنازل عن قيمة المكعب الحالية.
backgammon-accept = قبول
backgammon-drop = رفض

# Point labels
backgammon-point-empty = { $point }
backgammon-point-occupied = { $point } { $color }، { $count }
backgammon-point-occupied-selected = { $point } { $color }، { $count } محددة
backgammon-point-occupied-selected-bearoff = { $point } { $color }، { $count } محددة؛ فعّل مرة أخرى للإخراج

# Action labels
backgammon-label-double = مضاعفة
backgammon-label-roll = رمي النرد
backgammon-label-undo = تراجع
backgammon-label-deselect = إلغاء التحديد
backgammon-label-next-destination = الوجهة التالية
backgammon-label-previous-destination = الوجهة السابقة

# Selection feedback
backgammon-no-checkers-there = لا توجد قطع هناك.
backgammon-not-your-checkers = هذه ليست قطعك.
backgammon-no-moves-from-here = لا تحركات قانونية من هنا.
backgammon-must-enter-from-bar = يجب الدخول من الحاجز أولاً.
backgammon-illegal-move = تحرّك غير قانوني.
backgammon-no-dice-remaining = لم يتبقَّ لديك نرد لاستخدامه في هذا الدور.
backgammon-no-checkers-on-bar = ليست لديك قطع على الحاجز لإدخالها.
backgammon-invalid-destination = هذه الوجهة ليست نقطة طاولة صالحة للعب.
backgammon-source-empty = النقطة { $point } لا تحتوي على قطعة للتحريك.
backgammon-source-opponent = النقطة { $point } تحتوي على قطع خصمك.
backgammon-destination-blocked = النقطة { $point } محجوبة بـ { $count } من قطع الخصم.
backgammon-bar-entry-blocked = لا يمكنك الدخول على النقطة { $point }؛ فهي محجوبة بـ { $count } من قطع الخصم.
backgammon-no-die-for-bar-entry = لا يسمح أيٌّ من نردك المتبقي ({ $dice }) بالدخول على النقطة { $point }.
backgammon-no-die-for-destination = لا يسمح أيٌّ من نردك المتبقي ({ $dice }) بالتحرك من النقطة { $src } إلى النقطة { $dest }.
backgammon-must-use-forced-die = يجب أن تستخدم { $dice } الآن لأن الطاولة تتطلب استخدام كلا الحجرين عند الإمكان، أو الحجر الأكبر عندما يمكن لعب حجر واحد فقط.
backgammon-move-would-waste-die = هذا التحرك سيمنعك من استخدام أكبر عدد ممكن من النرد كما تتطلب القواعد. اختر تحركًا قانونيًا آخر.
backgammon-bearoff-not-home = لا يمكنك الإخراج بعد. القطع خارج لوحة ديارك: { $outside }. القطع على الحاجز: { $bar }. أدخل كل قطعة إلى النقاط من 1 إلى 6 وأخلِ الحاجز أولاً.
backgammon-bearoff-outside-home-point = النقطة { $point } خارج لوحة ديارك. يمكن فقط للقطع على النقاط من 1 إلى 6 أن تخرج.
backgammon-bearoff-blocked = لا يمكنك الإخراج من النقطة { $point } بـ { $die }، لأن هناك قطعًا على النقطة { $blocking_point }.
backgammon-bearoff-no-die = لا يمكنك الإخراج من النقطة { $point } بنردك المتبقي ({ $die }).
backgammon-nothing-to-undo = لا شيء للتراجع عنه.
backgammon-undo-move = { $listener ->
    [actor] تتراجع عن تحركك من { $source } إلى { $destination }.
    *[observer] { $player } يتراجع عن تحرك { GENDER_TERM($player_gender, "possessive-determiner") } من { $source } إلى { $destination }.
}
backgammon-undo-hit = { $listener ->
    [actor] تتراجع عن تحركك من { $source } إلى { $destination }، مستعيدًا قطعة { $opponent }.
    [target] { $player } يتراجع عن تحرك { GENDER_TERM($player_gender, "possessive-determiner") } من { $source } إلى { $destination }، مستعيدًا قطعتك.
    *[observer] { $player } يتراجع عن تحرك { GENDER_TERM($player_gender, "possessive-determiner") } من { $source } إلى { $destination }، مستعيدًا قطعة { $opponent }.
}
backgammon-selection-cleared = تم إلغاء تحديد القطعة.
backgammon-no-selection = لا توجد قطعة محددة.
backgammon-cannot-double = لا يمكنك المضاعفة الآن.
backgammon-double-single-game = مكعب المضاعفة لا يُستخدم في اللعبة الفردية.
backgammon-double-crawford = هذه لعبة كراوفورد، لذا مكعب المضاعفة غير متاح.
backgammon-double-dead-cube = ستفوز بالمباراة بالفعل عند الفوز بقيمة المكعب الحالية، لذا فالمكعب ميت بالنسبة لك ولا يمكن مضاعفته.
backgammon-double-cube-owned = { $opponent } يملك المكعب، لذا { GENDER_TERM($opponent_gender, "subject") } وحده من يمكنه عرض المضاعفة التالية.
backgammon-double-cube-owned-unknown = خصمك يملك المكعب، لذا لا يمكنك عرض المضاعفة التالية.
backgammon-double-before-roll-only = يمكنك عرض المضاعفة فقط في بداية دورك، قبل الرمي.
backgammon-cannot-undo = لا شيء للتراجع عنه.
backgammon-not-doubling-phase = لا توجد مضاعفة للرد عليها.
backgammon-need-roll-first = عليك رمي النرد قبل تحريك أي قطعة.
backgammon-roll-before-moving-only = يمكنك الرمي فقط في بداية دورك، قبل التحرك.
backgammon-confirm-drop-double = الرفض يعني التنازل عن هذه اللعبة بقيمة المكعب الحالية. اضغط رفض مرة أخرى خلال { $seconds } ثانية للتأكيد.

# Info keybinds
backgammon-check-status = الحالة
backgammon-check-cube = المكعب
backgammon-check-pip = عدد النقاط
backgammon-check-dice = النرد
backgammon-check-legal-moves = التحركات القانونية
backgammon-status = { $red_self ->
    [yes] أنت، الأحمر
    *[no] { $red }، الأحمر
} — الحاجز: { $bar_red }، خارج الديار: { $outside_red }، تم إخراجها: { $off_red }. { $white_self ->
    [yes] أنت، الأبيض
    *[no] { $white }، الأبيض
} — الحاجز: { $bar_white }، خارج الديار: { $outside_white }، تم إخراجها: { $off_white }.
backgammon-dice = { $is_self ->
    [yes] نردك المتبقي: { $dice }.
    *[no] نرد { $player } المتبقي: { $dice }.
}
backgammon-dice-none = لا نرد.
backgammon-no-dice-list = لا شيء
backgammon-cube-status = المكعب عند { $value }. { $owner ->
    [center] في المنتصف، يمكن لأي لاعب المضاعفة.
    [self] أنت تملك المكعب.
    *[other] مملوك لـ { $owner }.
} { $can_double ->
    [yes] المضاعفة متاحة الآن.
    [crawford] هذه لعبة كراوفورد، لا يُسمح بالمضاعفة.
    [dead] المكعب ميت بالنسبة للاعب الحالي لأن قيمته تكفي بالفعل للفوز بالمباراة.
    *[no] المضاعفة غير متاحة الآن.
}
backgammon-cube-no-match = لا يوجد مكعب مضاعفة في الألعاب الفردية.
backgammon-pip-count = { $red_self ->
    [yes] أنت، الأحمر
    *[no] { $red }، الأحمر
}: { $red_pip } نقطة. { $white_self ->
    [yes] أنت، الأبيض
    *[no] { $white }، الأبيض
}: { $white_pip } نقطة.
backgammon-match-score-line = { $is_self ->
    [yes] أنت: { $score } من { $match_length }.
    *[no] { $player }: { $score } من { $match_length }.
}
backgammon-match-score-cube-line = المكعب: { $cube }.

# Legal move status
backgammon-legal-moves-awaiting-roll = { $is_self ->
    [yes] يجب أن ترمي قبل أن تتوفر أي تحركات للقطع.
    *[no] يجب أن يرمي { $player } قبل أن تتوفر أي تحركات للقطع.
}
backgammon-legal-moves-awaiting-double-response = { $is_self ->
    [yes] يجب أن تقبل أو ترفض المضاعفة المعروضة قبل أن يستمر اللعب.
    *[no] يجب أن يقبل { $player } أو يرفض المضاعفة المعروضة قبل أن يستمر اللعب.
}
backgammon-legal-moves-none = { $is_self ->
    [yes] ليست لديك تحركات قطع قانونية.
    *[no] ليست لدى { $player } تحركات قطع قانونية.
}
backgammon-move-source-bar = الحاجز
backgammon-move-destination-off = خارج اللوحة
backgammon-legal-move-line = { $is_self ->
    [yes] أنت: { $source } إلى { $destination } باستخدام { $die }
    *[no] { $player }: { $source } إلى { $destination } باستخدام { $die }
}{ $hit ->
    [yes] ، مع إصابة قطعة مكشوفة.
    *[no] .
}
backgammon-wins-game-you = تفوز بـ { $points ->
    [one] نقطة واحدة
    [two] نقطتين
    [few] { $points } نقاط
    [many] { $points } نقطة
    *[other] { $points } نقطة
}. { $result ->
    [single] فوز عادي عند المكعب { $cube }.
    [gammon] جامون عند المكعب { $cube }.
    [backgammon] باكغامون عند المكعب { $cube }.
    *[drop] رفض خصمك المضاعفة عند المكعب { $cube }.
}
backgammon-wins-game-player = يفوز { $player } بـ { $points ->
    [one] نقطة واحدة
    [two] نقطتين
    [few] { $points } نقاط
    [many] { $points } نقطة
    *[other] { $points } نقطة
}. { $result ->
    [single] فوز عادي عند المكعب { $cube }.
    [gammon] جامون عند المكعب { $cube }.
    [backgammon] باكغامون عند المكعب { $cube }.
    *[drop] رفض خصمه المضاعفة عند المكعب { $cube }.
}
backgammon-new-game = بدء اللعبة { $number }.
backgammon-match-winner-you = لقد فزت بالمباراة!
backgammon-match-winner-player = { $player } يفوز بالمباراة!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. المباراة حتى { $match_length }.
backgammon-crawford = لعبة كراوفورد: لا مضاعفة في هذه اللعبة.

# Difficulty levels
backgammon-difficulty-random = عشوائي
backgammon-difficulty-simple = بسيط

# Options
backgammon-option-match-length = طول المباراة: { $match_length }
backgammon-option-select-match-length = حدد طول المباراة (1-25)
backgammon-option-changed-match-length = تم ضبط طول المباراة على { $match_length }.
backgammon-desc-match-length = النقاط اللازمة للفوز بمباراة الطاولة. القيمة 1 تعني لعبة فردية بلا مكعب مضاعفة (الافتراضي 1، المدى 1-25).
backgammon-option-bot-difficulty = صعوبة الروبوت: { $bot_difficulty }
backgammon-option-select-bot-difficulty = اختر صعوبة الروبوت
backgammon-option-changed-bot-difficulty = تم ضبط صعوبة الروبوت على { $bot_difficulty }.
backgammon-desc-bot-difficulty = يحدد كيف يقوم الروبوت بتحركاته: العشوائي يلعب تحركات قانونية باسترخاء، بينما البسيط يفضل تحركات تكتيكية أقوى.
