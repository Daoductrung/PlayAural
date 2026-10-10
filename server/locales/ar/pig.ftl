game-name-pig = بيغ
pig-desc-team-mode = اللعب فردياً أو ضمن ترتيب فرق مدعوم. يتشارك الفريق نتيجة واحدة ويفوز فوراً عندما يحتفظ أحد أعضائه بنقاط كافية.

pig-roll = رمي النرد
pig-hold = الاحتفاظ بـ { $points } نقطة
pig-check-turn-status = عرض حالة الدور

pig-game-start =
    تبدأ بيغ. أول { $team ->
        [yes] فريق
       *[no] لاعب
    } يحتفظ بـ { $target } نقطة يفوز. للنرد { $sides } وجهاً، ورمي الرقم 1 يُفقد كل نقطة غير محفوظة من ذلك الدور. { $minimum ->
        [0] يمكنك الاحتفاظ بعد أي رمية مُسجِّلة للنقاط.
       *[other] يجب أن تجمع { $minimum } نقطة دور على الأقل قبل الاحتفاظ.
    }
pig-game-start-brief =
    تبدأ بيغ. الهدف: { $target }. النرد: { $sides } وجهاً. الحد الأدنى للاحتفاظ: { $minimum }.{ $team ->
        [yes] الفرق تتشارك النتائج.
       *[no] نتائج فردية.
    }
pig-round-start = تبدأ الجولة { $round }. سيأخذ كل لاعب نشط دوراً واحداً.
pig-round-start-brief = الجولة { $round }.

pig-you-roll-result = رميتَ { $roll }. أصبح مجموع دورك الآن { $total } نقطة.
pig-player-roll-result = رمى { $player } { $roll }. أصبح مجموع الدور { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الآن { $total } نقطة.
pig-you-roll-result-brief = أنت: { $roll }؛ مجموع الدور { $total }.
pig-player-roll-result-brief = { $player }: { $roll }؛ مجموع الدور { $total }.

pig-you-bust = رميتَ الرقم 1 وخسرت كل نقاطك غير المحفوظة البالغة { $points }. ينتهي دورك دون نتيجة.
pig-player-busts = رمى { $player } الرقم 1 وخسر كل النقاط غير المحفوظة البالغة { $points }. ينتهي الدور { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } دون نتيجة.
pig-you-bust-brief = رميتَ 1 وخسرت { $points } نقطة دور.
pig-player-busts-brief = رمى { $player } 1 وخسر { $points } نقطة دور.

pig-you-hold =
    تحتفظ بـ { $points } نقطة. { $team ->
        [yes] أصبح لدى فريقك الآن { $total } نقطة.
       *[no] أصبحت نتيجتك الإجمالية الآن { $total } نقطة.
    }
pig-player-holds =
    يحتفظ { $player } بـ { $points } نقطة. { $team ->
        [yes] أصبح لدى { $team_name } الآن { $total } نقطة.
       *[no] أصبحت النتيجة الإجمالية { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الآن { $total } نقطة.
    }
pig-you-hold-brief =
    تحتفظ بـ { $points }؛{ $team ->
        [yes] إجمالي { $team_name } { $total }.
       *[no] إجماليك { $total }.
    }
pig-player-holds-brief =
    يحتفظ { $player } بـ { $points }؛{ $team ->
        [yes] إجمالي { $team_name } { $total }.
       *[no] الإجمالي { $total }.
    }

pig-you-win =
    { $team ->
        [yes] فريقك، { $winner }، هو الفائز في بيغ بـ { $score } نقطة!
       *[no] أنت الفائز في بيغ بـ { $score } نقطة!
    }
pig-winner =
    { $team ->
        [yes] الفائز هو { $winner }، بـ { $score } نقطة!
       *[no] الفائز هو { $winner }، بـ { $score } نقطة!
    }
pig-you-win-brief =
    { $team ->
        [yes] الفائز: فريقك، { $winner }، بـ { $score }.
       *[no] الفائز: أنت، بـ { $score }.
    }
pig-winner-brief = الفائز: { $winner }، بـ { $score }.

pig-confirm-risky-roll =
    الرمي مرة أخرى يعرّض { $points } نقطة غير محفوظة للخطر، مع احتمال { $risk } بالمئة لخسارتها. { $winning ->
        [yes] الاحتفاظ الآن سيمنحك { $total } نقطة ويفوز باللعبة.
       *[no] الاحتفاظ الآن سيمنحك { $total } من أصل { $target } نقطة لازمة للفوز.
    } اضغط رمي مرة أخرى خلال { $seconds } ثانية للتأكيد.

pig-action-resolving = النرد لا يزال يدور. انتظر النتيجة.
pig-no-turn-points = ارمِ النرد مرة واحدة على الأقل قبل الاحتفاظ.
pig-need-more-points = لديك { $current } نقطة دور، لكن هذه الطاولة تتطلب { $required } على الأقل قبل الاحتفاظ.

pig-desc-target-score = أول لاعب أو فريق يحتفظ بهذا العدد من النقاط الإجمالية يفوز فوراً (الافتراضي 100، المدى 10-1000).
pig-set-min-bank = الحد الأدنى للاحتفاظ: { $points }
pig-set-dice-sides = وجوه النرد: { $sides }
pig-enter-min-bank = أدخل الحد الأدنى لنقاط الدور اللازمة للاحتفاظ:
pig-enter-dice-sides = أدخل عدد وجوه النرد:
pig-option-changed-min-bank = تم تغيير الحد الأدنى للاحتفاظ إلى { $points } نقطة.
pig-desc-min-bank = عدد نقاط الدور المطلوبة قبل أن يصبح الاحتفاظ متاحاً. اضبطها على 0 للعبة بيغ القياسية؛ يجب أن تبقى أقل من النتيجة الهدف (الافتراضي 0، المدى 0-999).
pig-option-changed-dice = أصبح للنرد الآن { $sides } وجهاً.
pig-desc-dice-sides = عدد وجوه النرد الواحد. رمي الرقم 1 يُفقد دائماً مجموع الدور (الافتراضي 6، المدى 4-20).

pig-error-target-out-of-range = النتيجة الهدف { $value } غير صالحة. اختر قيمة من { $min } إلى { $max }.
pig-error-min-bank-out-of-range = الحد الأدنى للاحتفاظ { $value } غير صالح. اختر قيمة من { $min } إلى { $max }.
pig-error-dice-sides-out-of-range = نرد بـ { $value } وجهاً غير مدعوم. اختر من { $min } إلى { $max } وجهاً.
pig-error-min-bank-too-high = يجب أن يكون الحد الأدنى للاحتفاظ { $minimum } أقل من النتيجة الهدف البالغة { $target }.

pig-status-target = النتيجة الهدف: { $target } نقطة.
pig-status-round = الجولة الحالية: { $round }.
pig-status-current-turn = يلعب { $player }: { $banked } محفوظة، { $turn } في هذا الدور، { $potential } إذا احتفظ الآن.
pig-status-standing = { $rank }. { $team }: { $score } نقطة.

pig-line-format = { $rank }. { $player }: { $points }
