game-name-pusoydos = بوسوي دوس

# =============================================================================
# =============================================================================


# =============================================================================
# Option labels and prompts
# =============================================================================

pusoydos-set-game-mode = وضع اللعبة: { $choice }
pusoydos-select-game-mode = اختر وضع اللعبة:
pusoydos-option-changed-game-mode = تم ضبط وضع اللعبة على { $choice }.
pusoydos-desc-game-mode = الإقصاء: افز بالجولات لتخرج، وآخر لاعب هو الخاسر. الخسائر: من ينهون في المركز الأخير يجمعون خسائر، وأول من يبلغ الحد يخسر. النقاط: الفائز بالجولة يجمع نقاط عقوبة من الخاسرين، وأول من يبلغ الهدف يفوز. الإقصاء بالنقاط: الخاسرون يجمعون نقاط عقوبتهم، ومن يبلغ الحد يخرج، وآخر من يبقى يفوز.

pusoydos-mode-elimination = الإقصاء
pusoydos-mode-losses = الخسائر
pusoydos-mode-points = النقاط
pusoydos-mode-points-elimination = الإقصاء بالنقاط

pusoydos-set-rounds-to-win = الجولات اللازمة للفوز: { $count }
pusoydos-enter-rounds-to-win = أدخل عدد الجولات اللازمة للإقصاء (الأدنى: 1، الأقصى: 10):
pusoydos-option-changed-rounds-to-win = تم ضبط الجولات اللازمة للفوز على { $count }.
pusoydos-desc-rounds-to-win = وضع الإقصاء فقط: عدد الجولات التي يجب على اللاعب الفوز بها قبل مغادرة اللعبة فائزًا (الافتراضي 2، النطاق 1-10).

pusoydos-set-losses-to-lose = الخسائر اللازمة للخروج: { $count }
pusoydos-enter-losses-to-lose = أدخل عدد الخسائر اللازمة للخسارة (الأدنى: 1، الأقصى: 10):
pusoydos-option-changed-losses-to-lose = تم ضبط الخسائر اللازمة للخسارة على { $count }.
pusoydos-desc-losses-to-lose = وضع الخسائر فقط: عدد مرات الإنهاء في المركز الأخير التي يمكن للاعب تحمّلها قبل خسارة اللعبة (الافتراضي 3، النطاق 1-10).

pusoydos-set-target-score = النتيجة المستهدفة: { $score }
pusoydos-enter-target-score = أدخل النتيجة المستهدفة (الأدنى: 10، الأقصى: 10000):
pusoydos-option-changed-target-score = تم ضبط النتيجة المستهدفة على { $score }.
pusoydos-desc-target-score = أوضاع النقاط فقط: عتبة النتيجة للفوز في وضع النقاط، أو الإقصاء في وضع الإقصاء بالنقاط (الافتراضي 100، النطاق 10-10000).

pusoydos-set-turn-timer = مؤقّت الدور: { $choice }
pusoydos-select-turn-timer = اختر مدة مؤقّت الدور:
pusoydos-option-changed-turn-timer = تم ضبط مؤقّت الدور على { $choice }.
pusoydos-desc-turn-timer = الحد الزمني لكل دور: غير محدود، أو 10، أو 15، أو 20، أو 30، أو 45، أو 60، أو 90 ثانية (الافتراضي غير محدود).

pusoydos-timer-10 = 10 ثوانٍ
pusoydos-timer-15 = 15 ثانية
pusoydos-timer-20 = 20 ثانية
pusoydos-timer-30 = 30 ثانية
pusoydos-timer-45 = 45 ثانية
pusoydos-timer-60 = 60 ثانية
pusoydos-timer-90 = 90 ثانية
pusoydos-timer-unlimited = غير محدود

pusoydos-set-allow-2-in-straights = السماح بالـ2 في التسلسلات: { $enabled }
pusoydos-option-changed-allow-2-in-straights = تم ضبط السماح بالـ2 في التسلسلات على { $enabled }.
pusoydos-desc-allow-2-in-straights = ما إذا كان يمكن استخدام الـ2 في التسلسلات (مثل A-2-3-4-5).

pusoydos-set-instant-wins = الفوز الفوري: { $enabled }
pusoydos-option-changed-instant-wins = تم ضبط الفوز الفوري على { $enabled }.
pusoydos-desc-instant-wins = ما إذا كانت الأيادي الموزّعة الخاصة (التنين، أو أربع 2، أو ستة أزواج) تفوز بالجولة فورًا. لا يمكن الجمع بين هذا وتمرير البطاقات.

pusoydos-set-card-passing = تمرير البطاقات: { $choice }
pusoydos-select-card-passing = اختر وضع تمرير البطاقات:
pusoydos-option-changed-card-passing = تم ضبط تمرير البطاقات على { $choice }.
pusoydos-desc-card-passing = تبادل البطاقات بين الفائزين والخاسرين بعد التوزيع: إيقاف، أو بسيط، أو كامل. يتطلب التمرير الكامل لاعبين اثنين أو أربعة بالضبط، ولا يمكن الجمع بين التمرير والفوز الفوري.

pusoydos-passing-off = إيقاف
pusoydos-passing-simple = بسيط (الأول والأخير يتبادلان بطاقة واحدة)
pusoydos-passing-full = كامل (الأول/الأخير يتبادلان بطاقتين، والثاني/الثالث يتبادلان واحدة)

pusoydos-set-penalty-tier = مستوى العقوبة: { $choice }
pusoydos-select-penalty-tier = اختر مستوى العقوبة:
pusoydos-option-changed-penalty-tier = تم ضبط مستوى العقوبة على { $choice }.
pusoydos-desc-penalty-tier = أوضاع النقاط فقط: مدى صرامة معاقبة البطاقات المتبقية في نهاية الجولة.

pusoydos-penalty-standard = قياسي (10 بطاقات أو أكثر: ×2، 13 بطاقة: ×3)
pusoydos-penalty-aggressive = صارم (8-9: ×2، 10-12: ×3، 13: ×4)
pusoydos-penalty-flat = ثابت (نقطة واحدة لكل بطاقة، دون مضاعفة)

pusoydos-set-penalty-per-two = عقوبة لكل 2 محتفظ به: { $enabled }
pusoydos-option-changed-penalty-per-two = تم ضبط العقوبة لكل 2 محتفظ به على { $enabled }.
pusoydos-desc-penalty-per-two = أوضاع النقاط فقط: كل 2 متبقٍّ في يد خاسرة يضاعف عقوبة تلك اليد.

# =============================================================================
# Game flow announcements
# =============================================================================


pusoydos-new-hand = الجولة { $round }.
pusoydos-dealt = تم توزيع { $count } بطاقة: { $cards }.

pusoydos-you-first-player = لديك 3 السباتي وتبدأ أولًا.
pusoydos-first-player = لدى { $player } 3 السباتي ويبدأ أولًا.
pusoydos-you-first-player-lowest = لديك أدنى بطاقة وتبدأ أولًا.
pusoydos-first-player-lowest = لدى { $player } أدنى بطاقة ويبدأ أولًا.

# Elimination mode
pusoydos-you-eliminated = فزت بـ { $count } جولة وخرجت! أحسنت اللعب.
pusoydos-player-eliminated = فاز { $player } بـ { $count } جولة وخرج! أحسن اللعب.
pusoydos-you-last-player = أنت آخر لاعب متبقٍّ. انتهت اللعبة!
pusoydos-last-player = { $player } هو آخر لاعب متبقٍّ. انتهت اللعبة!
pusoydos-players-remaining = يتبقّى { $count } { $count ->
    [one] لاعب
   *[other] لاعبين
}.

# Losses mode
pusoydos-you-round-loser = أنهيت في المركز الأخير وتلقّيت خسارة! ({ $count } { $count ->
    [one] خسارة
   *[other] خسائر
} إجمالًا.)
pusoydos-round-loser = أنهى { $player } في المركز الأخير وتلقّى خسارة! ({ $count } { $count ->
    [one] خسارة
   *[other] خسائر
} إجمالًا.)
pusoydos-you-losses-game-over = بلغت { $count } خسارة وخسرت اللعبة!
pusoydos-losses-game-over = بلغ { $player } { $count } خسارة وخسر اللعبة!

# Points mode
pusoydos-penalty-entry = { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} من { $player }
pusoydos-you-penalty-summary = فزت بالجولة: { $breakdown }. ({ $gained } هذه الجولة، { $total } إجمالًا.)
pusoydos-penalty-summary = فاز { $player } بالجولة: { $breakdown }. ({ $gained } هذه الجولة، { $total } إجمالًا.)
pusoydos-you-win-round = فزت بالجولة!
pusoydos-round-winner = فاز { $player } بالجولة!
pusoydos-you-go-out = خرجت!
pusoydos-player-goes-out = خرج { $player }!
pusoydos-you-points-winner = بلغت { $score } نقطة وفزت باللعبة!
pusoydos-points-winner = بلغ { $player } { $score } نقطة وفاز باللعبة!

# Points elimination mode
pusoydos-you-points-elim-penalty = حصلت على { $points } نقطة. ({ $total } إجمالًا.)
pusoydos-points-elim-penalty = حصل { $player } على { $points } نقطة. ({ $total } إجمالًا.)
pusoydos-you-points-elim-eliminated = بلغت { $score } نقطة وتم إقصاؤك!
pusoydos-points-elim-eliminated = بلغ { $player } { $score } نقطة وتم إقصاؤه!
pusoydos-you-points-elim-winner = أنت آخر لاعب باقٍ. لقد فزت!
pusoydos-points-elim-winner = { $player } هو آخر لاعب باقٍ. فاز { $player }!

# Instant wins
pusoydos-you-instant-win-dragon = لديك تنين (تسلسل من 13 بطاقة)! فوز فوري!
pusoydos-instant-win-dragon = لدى { $player } تنين (تسلسل من 13 بطاقة)! فوز فوري!
pusoydos-you-instant-win-four-twos = لديك جميع البطاقات الأربع من فئة 2! فوز فوري!
pusoydos-instant-win-four-twos = لدى { $player } جميع البطاقات الأربع من فئة 2! فوز فوري!
pusoydos-you-instant-win-six-pairs = لديك ستة أزواج! فوز فوري!
pusoydos-instant-win-six-pairs = لدى { $player } ستة أزواج! فوز فوري!
pusoydos-checking-instant-wins = جارٍ التحقق من أيادي الفوز الفوري...
pusoydos-no-instant-wins = لا فوز فوري هذه الجولة.

# Card passing
pusoydos-passing-phase = مرحلة تمرير البطاقات.
pusoydos-loser-gives = يعطي { $loser } { $count ->
    [one] أعلى بطاقة { GENDER_TERM($loser_gender, "possessive-determiner") }
   *[other] أعلى { $count } بطاقات { GENDER_TERM($loser_gender, "possessive-determiner") }
} إلى { $winner }.
pusoydos-winner-gives-back = يعيد { $winner } { $count ->
    [one] بطاقة واحدة
   *[other] { $count } بطاقات
} إلى { $loser }.
pusoydos-select-cards-to-give = اختر { $count ->
    [one] بطاقة واحدة
   *[other] { $count } بطاقات
} لإعادتها إلى { $recipient }:
pusoydos-cards-exchanged = تم تبادل البطاقات.
pusoydos-passed-cards = أعطيت { $cards } إلى { $recipient }.
pusoydos-received-cards = استلمت { $cards } من { $sender }.

# =============================================================================
# Card interaction and actions
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (محدّدة)

pusoydos-play-none = اختر بطاقات للعبها.
pusoydos-play-invalid = تركيبة غير صالحة.
pusoydos-play-combo = العب { $combo }

pusoydos-pass = تمرير
pusoydos-check-trick = فحص الأكلة
pusoydos-read-hand = قراءة اليد
pusoydos-check-turn-timer = فحص مؤقّت الدور
pusoydos-read-card-counts = أعداد البطاقات
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}
pusoydos-card-counts-empty = لا لاعبين نشطين لديهم بطاقات لعدّها.
pusoydos-timer-disabled = مؤقّت الدور معطّل.
pusoydos-timer-remaining = يتبقّى { $seconds } ثانية.

# Keybind labels
pusoydos-key-play = لعب البطاقات المحددة
pusoydos-key-pass = تمرير
pusoydos-key-trick = فحص الأكلة الحالية
pusoydos-key-hand = قراءة يدك
pusoydos-key-counts = أعداد البطاقات
pusoydos-key-timer = مؤقّت الدور

# =============================================================================
# Errors
# =============================================================================

pusoydos-error-full-passing-players = يتطلب التمرير الكامل للبطاقات لاعبين اثنين أو أربعة بالضبط.
pusoydos-error-instant-wins-card-passing = الفوز الفوري وتمرير البطاقات متعارضان. عطّل أحدهما قبل بدء اللعبة.
pusoydos-error-no-cards = لم تحدّد أي بطاقات.
pusoydos-error-invalid-combo = البطاقات المحددة لا تشكّل تركيبة صالحة.
pusoydos-error-first-turn-3c = يجب أن تتضمن 3 السباتي في اللعبة الأولى.
pusoydos-error-wrong-length = يجب أن تلعب { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} بالضبط للتغلب على الأكلة الحالية.
pusoydos-error-lower-combo = تركيبتك أدنى من الأكلة الحالية.
pusoydos-error-must-play = لا يمكنك التمرير عند بدء أكلة جديدة.
pusoydos-error-select-cards-to-give = اختر { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} بالضبط لإعادتها إلى { $recipient }.
pusoydos-error-select-required-give-cards = اختر العدد المطلوب من البطاقات قبل تأكيد التبادل.
pusoydos-error-eliminated = أنت خارج هذه اللعبة بالفعل.
pusoydos-confirm-pass = استخدم إجراء التمرير مرة أخرى للتأكيد.

# =============================================================================
# Broadcasts
# =============================================================================

pusoydos-you-play-single = تلعب { $card }.
pusoydos-player-plays-single = يلعب { $player } { $card }.
pusoydos-you-play-combo = تلعب { $combo } من { $cards }.
pusoydos-player-plays-combo = يلعب { $player } { $combo } من { $cards }.
pusoydos-you-pass = تمرّر.
pusoydos-player-passes = يمرّر { $player }.
pusoydos-you-win-trick = تفوز بالأكلة.
pusoydos-trick-won = يفوز { $player } بالأكلة.

pusoydos-trick-empty = الأكلة فارغة.
pusoydos-trick-status = لعب { $player } { $combo } من { $cards }.
pusoydos-your-hand = يدك: { $cards }.

pusoydos-score-no-scores = لا نتائج بعد.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] فوز
   *[other] انتصارات
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] خسارة
   *[other] خسائر
}
pusoydos-score-points = { $player }: { $score } نقطة

pusoydos-you-one-card = تبقّت لديك بطاقة واحدة!
pusoydos-one-card = تبقّت لدى { $player } بطاقة واحدة!

# =============================================================================
# Combo names
# =============================================================================

pusoydos-combo-single = فردية
pusoydos-combo-pair = زوج
pusoydos-combo-three_of_a_kind = ثلاثة متماثلة
pusoydos-combo-straight = تسلسل
pusoydos-combo-flush = فلَش
pusoydos-combo-full_house = فُل هاوس
pusoydos-combo-four_of_a_kind = أربعة متماثلة
pusoydos-combo-straight_flush = ستريت فلَش

# Instant win hand names
pusoydos-combo-dragon = تنين
pusoydos-combo-four_twos = أربع 2
pusoydos-combo-six_pairs = ستة أزواج

# =============================================================================
# End screen
# =============================================================================

pusoydos-game-over = انتهت اللعبة! خسر { $player }!
pusoydos-game-over-points = انتهت اللعبة! فاز { $player } بـ { $score } نقطة!
pusoydos-game-over-losses = انتهت اللعبة! خسر { $player } بـ { $count } خسارة!
pusoydos-line-format = { $rank }. { $player }: { $score } نقطة
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] فوز
   *[other] انتصارات
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] خسارة
   *[other] خسائر
}
