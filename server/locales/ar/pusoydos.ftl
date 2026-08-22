game-name-pusoydos = بوسوي دوس

# =============================================================================
# =============================================================================


# =============================================================================
# Option labels and prompts
# =============================================================================

pusoydos-set-game-mode = وضع اللعبة: { $choice }
pusoydos-select-game-mode = اختر وضع اللعبة:
pusoydos-option-changed-game-mode = تم ضبط وضع اللعبة على { $choice }.
pusoydos-desc-game-mode = الإقصاء: الفوز بجولات الخروج، اللاعب الأخير هو الخاسر. الخسائر: يتراكم أصحاب المركز الأخير في الضربات، ويخسرون أولاً إلى الحد الأقصى. النقاط: الفائز بالجولة يجمع نقاط الجزاء من الخاسرين، أول من يصل إلى الهدف يفوز. القضاء على النقاط: يجمع الخاسرون نقاط الجزاء الخاصة بهم، ويصلون إلى الحد الأقصى ويخرجون، ويفوز آخر شخص صامد.
pusoydos-mode-elimination = القضاء
pusoydos-mode-losses = الخسائر
pusoydos-mode-points = النقاط
pusoydos-mode-points-elimination = القضاء على النقاط
pusoydos-set-rounds-to-win = جولات الفوز: { $count }
pusoydos-enter-rounds-to-win = أدخل الجولات المطلوب التخلص منها (الحد الأدنى: 1، الحد الأقصى: 10):
pusoydos-option-changed-rounds-to-win = تم تعيين جولات الفوز على { $count }.
pusoydos-desc-rounds-to-win = وضع الإقصاء فقط: عدد الجولات التي يجب على اللاعب الفوز بها قبل مغادرة اللعبة كفائز (الافتراضي 2، النطاق 1-10).
pusoydos-set-losses-to-lose = الخسائر التي يجب خسارتها: { $count }
pusoydos-enter-losses-to-lose = أدخل الخسائر اللازمة للخسارة (الحد الأدنى: 1، الحد الأقصى: 10):
pusoydos-option-changed-losses-to-lose = الخسائر التي يجب خسارتها مضبوطة على { $count }.
pusoydos-desc-losses-to-lose = وضع الخسائر فقط: عدد مرات إنهاء المركز الأخير التي يمكن للاعب أن يحققها قبل أن يخسر اللعبة (الافتراضي 3، النطاق 1-10).
pusoydos-set-target-score = النتيجة المستهدفة: { $score }
pusoydos-enter-target-score = أدخل النتيجة المستهدفة (الحد الأدنى: 10، الحد الأقصى: 10000):
pusoydos-option-changed-target-score = تم ضبط النتيجة المستهدفة على { $score }.
pusoydos-desc-target-score = أوضاع النقاط فقط: حد النتيجة للفوز في وضع النقاط، أو الإزالة في وضع تصفية النقاط (الافتراضي 100، النطاق 10-10000).
pusoydos-set-turn-timer = مؤقت الدوران: { $choice }
pusoydos-select-turn-timer = حدد مدة مؤقت الدوران:
pusoydos-option-changed-turn-timer = قم بضبط المؤقت على { $choice }.
pusoydos-desc-turn-timer = الحد الزمني لكل دور: غير محدود، 10، 15، 20، 30، 45، 60، أو 90 ثانية (افتراضي غير محدود).
pusoydos-timer-10 = 10 ثواني
pusoydos-timer-15 = 15 ثانية
pusoydos-timer-20 = 20 ثانية
pusoydos-timer-30 = 30 ثانية
pusoydos-timer-45 = 45 ثانية
pusoydos-timer-60 = 60 ثانية
pusoydos-timer-90 = 90 ثانية
pusoydos-timer-unlimited = غير محدود
pusoydos-set-allow-2-in-straights = السماح بـ 2 في الخطوط المستقيمة: { $enabled }
pusoydos-option-changed-allow-2-in-straights = السماح بضبط 2 في المستقيم على { $enabled }.
pusoydos-desc-allow-2-in-straights = ما إذا كان يمكن استخدام الرقم 2 في الخطوط المستقيمة (على سبيل المثال A-2-3-4-5).
pusoydos-set-instant-wins = الانتصارات الفورية: { $enabled }
pusoydos-option-changed-instant-wins = تم تعيين الانتصارات الفورية على { $enabled }.
pusoydos-desc-instant-wins = سواء كانت توزيعات الورق الخاصة (Dragon، Four 2s، Six Pairs) تفوز بالجولة على الفور. لا يمكن دمج هذا مع تمرير البطاقة.
pusoydos-set-card-passing = تمرير البطاقة: { $choice }
pusoydos-select-card-passing = حدد وضع تمرير البطاقة:
pusoydos-option-changed-card-passing = تم ضبط تمرير البطاقة على { $choice }.
pusoydos-desc-card-passing = تبادل البطاقات بين الفائزين والخاسرين بعد التعامل: إيقاف، بسيط، أو كامل. يتطلب التمرير الكامل 2 أو 4 لاعبين بالضبط، ولا يمكن الجمع بين التمرير والانتصارات الفورية.
pusoydos-passing-off = معطلة
pusoydos-passing-simple = بسيطة (بطاقة المبادلة الأولى والأخيرة)
pusoydos-passing-full = كامل (المبادلة الأولى/الأخيرة 2، المبادلة الثانية/الثالثة 1)
pusoydos-set-penalty-tier = مستوى الجزاء: { $choice }
pusoydos-select-penalty-tier = حدد فئة العقوبة:
pusoydos-option-changed-penalty-tier = تم ضبط مستوى الجزاء على { $choice }.
pusoydos-desc-penalty-tier = أوضاع النقاط فقط: مدى قوة معاقبة البطاقات المتبقية في نهاية الجولة.
pusoydos-penalty-standard = قياسي (+10 بطاقات: x2، 13 بطاقة: x3)
pusoydos-penalty-aggressive = عدوانية (8-9: x2، 10-12: x3، 13: x4)
pusoydos-penalty-flat = ثابت (نقطة واحدة لكل بطاقة، بدون مضاعف)
pusoydos-set-penalty-per-two = ركلة جزاء لكل 2 عقد: { $enabled }
pusoydos-option-changed-penalty-per-two = تم ضبط ركلة الجزاء لكل 2 على { $enabled }.
pusoydos-desc-penalty-per-two = أوضاع النقاط فقط: كل 2 متبقية في توزيع الورق الخاسر تضاعف عقوبة تلك اليد.

# =============================================================================
# Game flow announcements
# =============================================================================

pusoydos-new-hand = جولة { $round }.
pusoydos-dealt = تعامل { $count } البطاقات: { $cards }.
pusoydos-you-first-player = لديك 3 من النوادي وتذهب أولا.
pusoydos-first-player = { $player } لديه 3 من الأندية ويذهب أولا.
pusoydos-you-first-player-lowest = لديك أدنى بطاقة وتذهب أولا.
pusoydos-first-player-lowest = { $player } لديه أدنى بطاقة ويذهب أولا.
# Elimination mode
pusoydos-you-eliminated = لقد فزت { $count } جولات وخرجت! لعبت بشكل جيد.
pusoydos-player-eliminated = { $player } يفوز { $count } جولات وخرج! لعبت بشكل جيد.
pusoydos-you-last-player = أنت آخر لاعب متبقي. انتهت اللعبة!
pusoydos-last-player = { $player } هو اللاعب الأخير المتبقي. انتهت اللعبة!
pusoydos-players-remaining =
    { $count } { $count ->
        [one] لاعب
       *[other] اللاعبين
    } متبقي.
# Losses mode
pusoydos-you-round-loser =
    تنتهي أخيرًا وتخسر! ({ $count } { $count ->
        [one] الخسارة
       *[other] الخسائر
    } الإجمالي.)
pusoydos-round-loser =
    { $player } ينتهي أخيرًا ويخسر! ({ $count } { $count ->
        [one] الخسارة
       *[other] الخسائر
    } الإجمالي.)
pusoydos-you-losses-game-over = تصل { $count } الخسائر وخسارة اللعبة!
pusoydos-losses-game-over = { $player } يصل { $count } الخسائر ويخسر اللعبة!
# Points mode
pusoydos-penalty-entry =
    { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } من { $player }
pusoydos-you-penalty-summary = لقد فزت بالجولة: { $breakdown }. ({ $gained } هذه الجولة، { $total } الإجمالي.)
pusoydos-penalty-summary = { $player } يفوز بالجولة: { $breakdown }. ({ $gained } هذه الجولة، { $total } الإجمالي.)
pusoydos-you-win-round = لقد فزت بالجولة!
pusoydos-round-winner = { $player } يفوز بالجولة!
pusoydos-you-go-out = اخرج!
pusoydos-player-goes-out = { $player } يخرج!
pusoydos-you-points-winner = تصل { $score } النقاط والفوز باللعبة!
pusoydos-points-winner = { $player } يصل { $score } النقاط ويفوز باللعبة!
# Points elimination mode
pusoydos-you-points-elim-penalty = تحصل على { $points } نقاط. ({ $total } المجموع.)
pusoydos-points-elim-penalty = { $player } يحصل { $points } نقاط. ({ $total } المجموع.)
pusoydos-you-points-elim-eliminated = تصل { $score } النقاط ويتم القضاء عليها!
pusoydos-points-elim-eliminated = { $player } يصل { $score } نقاط ويتم القضاء عليها!
pusoydos-you-points-elim-winner = أنت آخر لاعب يقف. فزت!
pusoydos-points-elim-winner = { $player } هو آخر لاعب يقف. { $player } يفوز!
# Instant wins
pusoydos-you-instant-win-dragon = لديك تنين (13 بطاقة متتالية)! فوز فوري!
pusoydos-instant-win-dragon = { $player } لديه تنين (13 بطاقة على التوالي)! فوز فوري!
pusoydos-you-instant-win-four-twos = لديك كل أربعة 2S! فوز فوري!
pusoydos-instant-win-four-twos = { $player } لديه كل أربعة 2S! فوز فوري!
pusoydos-you-instant-win-six-pairs = لديك ستة أزواج! فوز فوري!
pusoydos-instant-win-six-pairs = { $player } لديه ستة أزواج! فوز فوري!
pusoydos-checking-instant-wins = جارٍ التحقق من توزيعات الورق المربحة بشكل فوري...
pusoydos-no-instant-wins = لا يوجد فوز فوري في هذه الجولة.
# Card passing
pusoydos-passing-phase = مرحلة تمرير البطاقة.
pusoydos-loser-gives =
    { $loser } يعطي { $count ->
        [one] أعلى بطاقتهم
       *[other] هُم { $count } أعلى البطاقات
    } إلى { $winner }.
pusoydos-winner-gives-back =
    { $winner } يعطي { $count ->
        [one] بطاقة
       *[other] { $count } بطاقات
    } العودة إلى { $loser }.
pusoydos-select-cards-to-give =
    حدد { $count ->
        [one] بطاقة واحدة
       *[other] { $count } بطاقات
    } لرد الجميل ل { $recipient }:
pusoydos-cards-exchanged = تم تبادل البطاقات.
pusoydos-passed-cards = لقد قدمت { $cards } إلى { $recipient }.
pusoydos-received-cards = لقد تلقيت { $cards } من { $sender }.

# =============================================================================
# Card interaction and actions
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (مختار)
pusoydos-play-none = حدد البطاقات للعب.
pusoydos-play-invalid = تركيبة غير صالحة.
pusoydos-play-combo = لعب { $combo }
pusoydos-pass = تمرير
pusoydos-check-trick = خدعة التحقق
pusoydos-read-hand = قراءة اليد
pusoydos-check-turn-timer = تحقق من مؤقت الدوران
pusoydos-read-card-counts = عدد البطاقات
pusoydos-card-count-line =
    { $player }: { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }
pusoydos-card-counts-empty = لا يوجد لدى أي لاعب نشط بطاقات لعدها.
pusoydos-timer-disabled = تم تعطيل مؤقت الدوران.
pusoydos-timer-remaining = { $seconds } الثواني المتبقية.
# Keybind labels
pusoydos-key-play = لعب البطاقات المختارة
pusoydos-key-pass = تمرير
pusoydos-key-trick = تحقق من الخدعة الحالية
pusoydos-key-hand = اقرأ يدك
pusoydos-key-counts = تعداد البطاقات
pusoydos-key-timer = تشغيل الموقت

# =============================================================================
# Errors
# =============================================================================

pusoydos-error-full-passing-players = يتطلب التمرير الكامل للبطاقة 2 أو 4 لاعبين بالضبط.
pusoydos-error-instant-wins-card-passing = انتصارات فورية وتعارض تمرير البطاقة. قم بتعطيل واحد منهم قبل بدء اللعبة.
pusoydos-error-no-cards = لم تقم بتحديد أية بطاقات.
pusoydos-error-invalid-combo = البطاقات المحددة لا تشكل مجموعة صالحة.
pusoydos-error-first-turn-3c = يجب عليك تضمين 3 من الأندية في المسرحية الأولى.
pusoydos-error-wrong-length =
    يجب أن تلعب بالضبط { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } للتغلب على الحيلة الحالية.
pusoydos-error-lower-combo = مجموعتك أقل من الخدعة الحالية.
pusoydos-error-must-play = لا يمكنك المرور عند بدء خدعة جديدة.
pusoydos-error-select-cards-to-give =
    حدد بالضبط { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } لرد الجميل ل { $recipient }.
pusoydos-error-select-required-give-cards = قم باختيار العدد المطلوب من البطاقات قبل تأكيد الاستبدال.
pusoydos-error-eliminated = لقد خرجت بالفعل من هذه اللعبة.
pusoydos-confirm-pass = استخدم إجراء المرور مرة أخرى للتأكيد.

# =============================================================================
# Broadcasts
# =============================================================================

pusoydos-you-play-single = أنت تلعب { $card }.
pusoydos-player-plays-single = { $player } مسرحيات { $card }.
pusoydos-you-play-combo = أنت تلعب { $combo } من { $cards }.
pusoydos-player-plays-combo = { $player } يلعب { $combo } من { $cards }.
pusoydos-you-pass = لقد نجحت.
pusoydos-player-passes = { $player } يمر.
pusoydos-you-win-trick = لقد فزت بالخدعة.
pusoydos-trick-won = { $player } يفوز بالخدعة.
pusoydos-trick-empty = الحيلة فارغة.
pusoydos-trick-status = { $player } لعبت { $combo } من { $cards }.
pusoydos-your-hand = يدك: { $cards }.
pusoydos-score-no-scores = لا توجد نتائج حتى الآن.
pusoydos-score-wins =
    { $player }: { $count } { $count ->
        [one] فوز
       *[other] يفوز
    }
pusoydos-score-losses =
    { $player }: { $count } { $count ->
        [one] خسارة
       *[other] خسائر
    }
pusoydos-score-points = { $player }: { $score } النقاط
pusoydos-you-one-card = لديك بطاقة واحدة متبقية!
pusoydos-one-card = { $player } لديه بطاقة واحدة متبقية!

# =============================================================================
# Combo names
# =============================================================================

pusoydos-combo-single = مفردة
pusoydos-combo-pair = زوج
pusoydos-combo-three_of_a_kind = ثلاثة من نفس النوع
pusoydos-combo-straight = مستقيم
pusoydos-combo-flush = دافق
pusoydos-combo-full_house = فول هاوس
pusoydos-combo-four_of_a_kind = أربعة من نفس النوع
pusoydos-combo-straight_flush = تدفق مستقيم
# Instant win hand names
pusoydos-combo-dragon = التنين
pusoydos-combo-four_twos = أربع 2 ثانية
pusoydos-combo-six_pairs = ستة أزواج

# =============================================================================
# End screen
# =============================================================================

pusoydos-game-over = انتهت اللعبة! { $player } ضائع!
pusoydos-game-over-points = انتهت اللعبة! { $player } يفوز مع { $score } نقاط!
pusoydos-game-over-losses = انتهت اللعبة! { $player } يخسر مع { $count } خسائر!
pusoydos-line-format = { $rank }. { $player }: { $score } النقاط
pusoydos-line-format-wins =
    { $rank }. { $player }: { $wins } { $wins ->
        [one] فوز
       *[other] يفوز
    }
pusoydos-line-format-losses =
    { $rank }. { $player }: { $losses } { $losses ->
        [one] خسارة
       *[other] خسائر
    }
