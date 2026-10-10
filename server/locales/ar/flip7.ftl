game-name-flip7 = فليب 7

# Options
flip7-set-target-score = النتيجة المستهدفة: { $score }
flip7-enter-target-score = أدخل النتيجة المستهدفة
flip7-option-changed-target = تم ضبط النتيجة المستهدفة على { $score }.
flip7-desc-target-score = النتيجة التي تُفعّل التحقق من الفوز بعد الجولة. صاحب أعلى مجموع يفوز؛ وإذا تعادل المتصدّرون تستمر المباراة. الافتراضي: 200، المدى 50-1000.

# Cards
flip7-card-number = { $value }
flip7-card-modifier = +{ $value }
flip7-card-double = مضاعفة
flip7-card-second-chance = فرصة ثانية
flip7-card-freeze = تجميد
flip7-card-flip-three = اقلب ثلاثًا

# Turn actions
flip7-hit = اقلب بطاقة
flip7-stay = توقّف وأودِع { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }
flip7-stay-base = توقّف وأودِع
flip7-stay-banked = توقّف وأودِع (توقفت بالفعل)
flip7-you-stay = تتوقف وتودع { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-player-stays = { $player } يتوقف ويودع { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.

# Round
flip7-round-start = الجولة { $round }. { $dealer } يوزّع.
flip7-round-start-you = الجولة { $round }. أنت توزّع.
flip7-round-end = انتهت الجولة { $round }.
flip7-round-score = { $player } سجّل { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    } هذه الجولة. مجموع المباراة: { $total } { $total ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-round-score-you = سجّلت { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    } هذه الجولة. مجموع المباراة: { $total } { $total ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-round-bust = { $player } تجاوز ولم يسجّل شيئًا.
flip7-round-bust-you = تجاوزت ولم تسجّل شيئًا هذه الجولة.
flip7-match-win = { $player } يفوز بالمباراة!
flip7-match-win-you = فزت بالمباراة!
flip7-deck-reshuffled = تم خلط كومة المهملات لتكوين كومة سحب جديدة.
flip7-you-pending-bust-discarded = تجاوزت، لذا تم التخلّص من بطاقات الحركة التي تحتفظ بها.
flip7-player-pending-bust-discarded = { $player } تجاوز، لذا تم التخلّص من بطاقات الحركة المحتفظ بها.

# Drawing cards
flip7-you-turn-card = تقلب بطاقة.
flip7-player-turns-card = { $player } يقلب بطاقة.
flip7-your-card-is = البطاقة: { $card }.
flip7-player-card-is = بطاقة { $player }: { $card }.
flip7-you-stop-alone = أنت اللاعب الوحيد المتبقّي، لذا تتوقف وتودع { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-player-stops-alone = { $player } هو اللاعب الوحيد المتبقّي، لذا يتوقف ويودع { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-you-set-second-chance = تضع فرصة ثانية جانبًا.
flip7-player-sets-second-chance = { $player } يضع فرصة ثانية جانبًا.
flip7-second-chance-saves = الفرصة الثانية تنقذ { $player } من { $value } المكرّر.
flip7-second-chance-saves-you = الفرصة الثانية تنقذك من { $value } المكرّر.
flip7-you-bust = تقلب { $value } آخر فتتجاوز. لا تسجّل شيئًا هذه الجولة.
flip7-player-busts = { $player } يقلب { $value } آخر فيتجاوز، ولا يسجّل شيئًا هذه الجولة.
flip7-flip-seven = { $player } يكمل فليب 7 ويحصل على مكافأة { $bonus } نقطة!
flip7-flip-seven-you = تكمل فليب 7 وتحصل على مكافأة { $bonus } نقطة!

# Targeted choices
flip7-choice-required = اختر هدفًا لـ { $action }.
flip7-target-freeze = تجميد { $target } ({ $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    })
flip7-target-flip-three = اجعل { $target } يقلب ثلاث بطاقات
flip7-target-second-chance-self = احتفظ بالفرصة الثانية
flip7-target-second-chance = امنح فرصة ثانية لـ { $target }
flip7-you-stop-player = تجمّد { $target } عند { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-player-stops-player = { $player } يجمّد { $target } عند { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-you-stop-yourself = تجمّد نفسك عند { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-player-stops-themself = { $player } يجمّد نفسه عند { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-you-flip-three = تجعل { $target } يقلب ثلاث بطاقات.
flip7-player-flip-three = { $player } يجعل { $target } يقلب ثلاث بطاقات.
flip7-you-flip-three-self = تقلب ثلاث بطاقات.
flip7-player-flips-three-self = { $player } يقلب ثلاث بطاقات.
flip7-you-give-second-chance = تمنح فرصة ثانية لـ { $target }.
flip7-player-gives-second-chance = { $player } يمنح فرصة ثانية لـ { $target }.
flip7-you-discard-second-chance = لا أحد يستطيع أخذها، لذا يتم التخلّص من الفرصة الثانية.
flip7-player-discards-second-chance = { $player } لا يستطيع منح الفرصة الثانية لأحد، لذا يتم التخلّص منها.
flip7-you-discard-action = لا يمكن استهداف أحد، لذا يتم التخلّص من { $action }.
flip7-player-discards-action = { $player } ليس لديه من يستهدفه، لذا يتم التخلّص من { $action }.

# Information actions
flip7-check-area = مراجعة منطقتي
flip7-check-area-description = استمع إلى بطاقاتك المكشوفة وحالة الجولة ونتيجتك في الجولة الحالية.
flip7-check-table = مراجعة الطاولة
flip7-check-table-description = افتح عرضًا حيًّا للجولة والمرحلة الحالية وبطاقات كل لاعب العلنية ونتائجهم.
flip7-check-deck = فحص المجموعة
flip7-check-deck-description = استمع إلى عدد البطاقات المتبقية في كومة السحب وكومة المهملات.
flip7-check-scores = فحص النتائج
flip7-review-scores = نتائج مفصّلة
flip7-you-label = أنت
flip7-area-status-playing = ما زال يلعب
flip7-area-status-scored = سجّل
flip7-area-status-stayed = توقّف
flip7-area-status-busted = تجاوز
flip7-area-numbers-none = لا شيء
flip7-area-inline = { $who }، { $status }. بطاقات الأرقام: { $numbers }. نتيجة الجولة: { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-area-inline-with-specials = { $who }، { $status }. بطاقات الأرقام: { $numbers }. بطاقات أخرى: { $specials }. نتيجة الجولة: { $points } { $points ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-area-resolving-card = { $area } البطاقة قيد الحسم: { $card }.
flip7-check-round = الجولة { $round }. النتيجة المستهدفة { $target }.
flip7-table-line = { $area } مجموع المباراة: { $total } { $total ->
        [one] نقطة
        [two] نقطتان
        [few] نقاط
        [many] نقطة
       *[other] نقطة
    }.
flip7-deck-line = كومة السحب: { $count ->
        [one] بطاقة واحدة
        [two] بطاقتان
        [few] { $count } بطاقات
        [many] { $count } بطاقة
       *[other] { $count } بطاقة
    }
flip7-discard-line = كومة المهملات: { $count ->
        [one] بطاقة واحدة
        [two] بطاقتان
        [few] { $count } بطاقات
        [many] { $count } بطاقة
       *[other] { $count } بطاقة
    }

# Turn and sequence status
flip7-whose-turn-choice-you = أنت تختار هدفًا لـ { $action }.
flip7-whose-turn-choice-player = { $player } يختار هدفًا لـ { $action }.
flip7-whose-turn-dealing-you = الجولة { $round }: أنت توزّع.
flip7-whose-turn-dealing-player = الجولة { $round }: { $player } يوزّع.
flip7-whose-turn-deal-card-you = الجولة { $round }: بطاقتك الافتتاحية قيد الحسم.
flip7-whose-turn-deal-card-player = الجولة { $round }: بطاقة { $player } الافتتاحية قيد الحسم.
flip7-whose-turn-card-you = بطاقتك قيد الحسم.
flip7-whose-turn-card-player = بطاقة { $player } قيد الحسم.
flip7-whose-turn-flip-three-you = أنت تقلب ثلاث بطاقات.
flip7-whose-turn-flip-three-player = { $player } يقلب ثلاث بطاقات.
flip7-whose-turn-banking-you = أنت تتوقف وتودع.
flip7-whose-turn-banking-player = { $player } يتوقف ويودع.
flip7-whose-turn-round-end = الجولة { $round } قيد التسوية.
flip7-whose-turn-match-end = يتم الإعلان عن الفائز.
flip7-whose-turn-resolving = سلسلة بطاقات قيد الحسم.

# Blocking reasons
flip7-error-wait-card = انتظر حتى يتم حسم البطاقة الحالية.
flip7-error-make-choice = اختر هدفًا قبل القلب أو التوقف.
flip7-error-wait-choice = انتظر حتى يتم حسم اختيار الهدف الحالي.
flip7-error-wait-flip-three = انتظر حتى تنتهي بطاقة "اقلب ثلاثًا".
flip7-error-wait-dealing = انتظر حتى يتم توزيع البطاقات.
flip7-error-not-playing-round = لم تعد تلعب في هذه الجولة.
flip7-error-no-cards-to-bank = تحتاج إلى بطاقة واحدة على الأقل في منطقتك قبل أن تتمكن من التوقف.
flip7-error-no-choice = لا يوجد اختيار بطاقة للإجابة عليه.
flip7-error-wait-banking = انتظر حتى يتم إيداع النقاط الحالية.
flip7-error-choice-not-ready = انتظر حتى يُفتح اختيار الهدف.

# End screen
flip7-line-format = { $rank }. { $player }: { $points }
