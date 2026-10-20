game-name-tossup = رمية الحظ

tossup-roll-first =
    رمي { $count } { $count ->
        [one] نردة
       *[other] نردات
    }
tossup-roll-remaining =
    رمي { $count } { $count ->
        [one] نردة متبقية
       *[other] نردات متبقية
    }
tossup-bank =
    حفظ { $points } { $points ->
        [one] نقطة
       *[other] نقطة
    }
tossup-check-turn-status = عرض حالة الدور

tossup-game-start = تبدأ رمية الحظ بقواعد { $rules }، و{ $dice } نردة لكل مجموعة، وعتبة هدف قدرها { $target }. تجاوز العتبة وأكمل الأدوار المتبقية للفوز.
tossup-game-start-brief = تبدأ رمية الحظ. تجاوز { $target }.
tossup-round-start = تبدأ الجولة { $round }.
tossup-round-start-brief = الجولة { $round }.

tossup-your-turn =
    دورك. نتيجتك المحفوظة هي { $score }؛ ارمِ { $dice } { $dice ->
        [one] نردة
       *[other] نردات
    } للبدء.
tossup-player-turn =
    دور { $player } بـ { $score } نقطة محفوظة و{ $dice } { $dice ->
        [one] نردة
       *[other] نردات
    }.
tossup-your-turn-brief = دورك: { $score } نقطة.
tossup-player-turn-brief = دور { $player }: { $score } نقطة.

tossup-you-roll = رميتَ { $results }.
tossup-player-rolls = رمى { $player } { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] أنت: { $results }؛ مجموع الدور { $turn_points }؛ مجموعة جديدة من { $dice_count }.
       *[no] أنت: { $results }؛ مجموع الدور { $turn_points }؛ { $dice_count } متبقية.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }؛ مجموع الدور { $turn_points }؛ مجموعة جديدة من { $dice_count }.
       *[no] { $player }: { $results }؛ مجموع الدور { $turn_points }؛ { $dice_count } متبقية.
    }

tossup-result-green = { $count } خضراء
tossup-result-yellow = { $count } صفراء
tossup-result-red = { $count } حمراء

tossup-you-have-points =
    نحّيتَ جانباً { $gained } { $gained ->
        [one] نردة خضراء
       *[other] نردات خضراء
    }. مجموع دورك هو { $turn_points }، مع { $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } متبقية.
tossup-player-has-points =
    نحّى { $player } جانباً { $gained } { $gained ->
        [one] نردة خضراء
       *[other] نردات خضراء
    } ولديه { $turn_points } نقطة دور، مع { $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } متبقية.

tossup-you-get-fresh = كل نردة خضراء. تحصل على مجموعة جديدة من { $count } نردة ويمكنك الرمي مجدداً أو الحفظ.
tossup-player-gets-fresh = كل نردة خضراء. يحصل { $player } على مجموعة جديدة من { $count } نردة.

tossup-you-bust =
    { $variant ->
        [Standard] ضوء أحمر: لم ترمِ أي خضراء ورميت حمراء واحدة على الأقل. ينتهي دورك وتخسر { $points } نقطة غير محفوظة.
       *[PlayAural] كل النردات المرمية حمراء. ينتهي دورك وتخسر { $points } نقطة غير محفوظة.
    }
tossup-player-busts =
    { $variant ->
        [Standard] ضوء أحمر: لم يرمِ { $player } أي خضراء ورمى حمراء واحدة على الأقل، ما أنهى الدور وأفقده { $points } نقطة غير محفوظة.
       *[PlayAural] كل نردات { $player } المرمية حمراء، ما أنهى الدور وأفقده { $points } نقطة غير محفوظة.
    }
tossup-you-bust-brief = أنت: { $results }؛ خسارة؛ تفقد { $points }.
tossup-player-busts-brief = { $player }: { $results }؛ خسارة؛ يفقد { $points }.

tossup-you-bank = تحفظ { $points } نقطة، فيصبح مجموع نتيجتك { $total }.
tossup-player-banks = يحفظ { $player } { $points } نقطة، فتصبح النتيجة الإجمالية { GENDER_TERM($player_gender, "possessive-determiner") } الآن { $total }.
tossup-you-bank-brief = تحفظ { $points }؛ الإجمالي { $total }.
tossup-player-banks-brief = يحفظ { $player } { $points }؛ الإجمالي { $total }.

tossup-you-trigger-final-turns =
    تجاوزت عتبة { $target } نقطة بـ { $score }.
    { $count ->
        [one] يحصل اللاعب المتبقي على دور أخير واحد.
       *[other] يحصل اللاعبون المتبقون البالغ عددهم { $count } على دور أخير واحد لكل منهم.
    }
tossup-player-triggers-final-turns =
    يتجاوز { $player } عتبة { $target } نقطة بـ { $score }.
    { $count ->
        [one] يحصل اللاعب المتبقي على دور أخير واحد.
       *[other] يحصل اللاعبون المتبقون البالغ عددهم { $count } على دور أخير واحد لكل منهم.
    }
tossup-you-trigger-final-turns-brief =
    حددت النتيجة الواجب تجاوزها عند { $score }؛ يتبقى { $count } { $count ->
        [one] دور.
       *[other] دور.
    }
tossup-player-triggers-final-turns-brief =
    يحدد { $player } النتيجة الواجب تجاوزها عند { $score }؛ يتبقى { $count } { $count ->
        [one] دور.
       *[other] دور.
    }

tossup-you-win = تفوز في رمية الحظ بـ { $score } نقطة.
tossup-winner = يفوز { $player } في رمية الحظ بـ { $score } نقطة.
tossup-you-win-brief = تفوز: { $score }.
tossup-winner-brief = يفوز { $player }: { $score }.
tossup-tie-tiebreaker = { $players } متعادلون على أعلى نتيجة فوق الهدف. يستمر هؤلاء اللاعبون وحدهم في جولة كسر التعادل.
tossup-tie-tiebreaker-brief = كسر التعادل: { $players }.
tossup-tiebreaker-round-start = تبدأ جولة كسر التعادل { $round } لـ { $players }.
tossup-tiebreaker-round-start-brief = جولة كسر التعادل { $round }: { $players }.

tossup-your-turn-awaiting-roll =
    لم يبدأ دورك في الرمي بعد. لديك { $score } نقطة محفوظة و{ $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } جاهزة.
tossup-player-turn-awaiting-roll =
    لم يرمِ { $player } بعد. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $score } نقطة محفوظة و{ $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } جاهزة.
tossup-your-turn-status =
    كانت رميتك الأخيرة { $results }. لديك { $turn_points } نقطة دور غير محفوظة، و{ $score } نقطة محفوظة، و{ $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } جاهزة للرمي.
tossup-player-turn-status =
    رمى { $player } آخر مرة { $results }. { GENDER_TERM($player_gender, "subject-have-capitalized") } { $turn_points } نقطة دور غير محفوظة، و{ $score } نقطة محفوظة، و{ $dice_count } { $dice_count ->
        [one] نردة
       *[other] نردات
    } جاهزة للرمي.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] الحفظ الآن سيضعك في الصدارة بـ { $total } نقطة، فوق عتبة { $target } نقطة.
       *[no] لديك حالياً { $points } نقطة دور غير محفوظة.
    }
    رمي { $dice } { $dice ->
        [one] نردة
       *[other] نردات
    } لديه احتمال نحو { $risk } بالمئة للخسارة. اضغط رمي مرة أخرى خلال { $seconds } ثانية للتأكيد، أو احفظ لحماية النقاط.

tossup-set-rules-variant = القواعد: { $variant }
tossup-select-rules-variant = اختر قواعد النرد والخسارة:
tossup-option-changed-rules = تم تغيير القواعد إلى { $variant }.
tossup-desc-rules-variant = الكلاسيكية تستخدم ثلاثة أوجه خضراء ووجهين أصفرين ووجهاً أحمر واحداً لكل نردة؛ الرمية الخالية من الأخضر وفيها حمراء واحدة على الأقل تُعدّ خسارة. المتسامحة تمنح الألوان الثلاثة فرصاً متساوية ولا تخسر إلا عند ظهور كل الأوجه حمراء.

tossup-desc-target-score = تدخل اللعبة أدوار الاستجابة الأخيرة بعد أن يحفظ لاعب أكثر من هذه النتيجة (الافتراضي 100، المدى 20-500).
tossup-set-starting-dice = نردات لكل مجموعة: { $count }
tossup-enter-starting-dice = أدخل عدد النردات في كل مجموعة جديدة:
tossup-option-changed-dice = تم تغيير عدد النردات لكل مجموعة إلى { $count }.
tossup-desc-starting-dice = اختر كم نردة تبدأ كل دور وتعود بعد أن تصبح كل نردة خضراء (الافتراضي 10، المدى 5-20).


tossup-rules-standard = الكلاسيكية
tossup-rules-PlayAural = المتسامحة
tossup-rules-standard-desc = ثلاثة أوجه خضراء، ووجهان أصفران، ووجه أحمر واحد. خسارة عند عدم ظهور أخضر مع حمراء واحدة على الأقل.
tossup-rules-PlayAural-desc = فرص متساوية للألوان الثلاثة. خسارة فقط عندما تكون كل نردة مرمية حمراء.

tossup-error-roll-not-playing = لا يمكنك الرمي لأن رمية الحظ ليست قيد التشغيل حالياً.
tossup-error-roll-no-turn = لا يمكنك الرمي لأنه لا يوجد دور نشط في رمية الحظ الآن.
tossup-error-roll-not-your-turn = لا يمكنك الرمي أثناء دور { $player }. انتظر حتى يصل الدور إليك.
tossup-error-bank-not-playing = لا يمكنك الحفظ لأن رمية الحظ ليست قيد التشغيل حالياً.
tossup-error-bank-no-turn = لا يمكنك الحفظ لأنه لا يوجد دور نشط في رمية الحظ الآن.
tossup-error-bank-not-your-turn = لا يمكنك الحفظ أثناء دور { $player }. انتظر حتى يصل الدور إليك.
tossup-error-bank-roll-first = ارمِ مرة واحدة على الأقل قبل الحفظ. يمكن حفظ رمية كلها صفراء بصفر نقطة لإنهاء دورك.
tossup-error-spectator-action = يمكن للمتفرجين عرض حالة رمية الحظ العامة، لكن لا يمكنهم الرمي أو حفظ النقاط.
tossup-error-status-not-playing = حالة الدور غير متاحة لأن رمية الحظ ليست قيد التشغيل حالياً.
tossup-error-status-no-turn = حالة الدور غير متاحة لأنه لا يوجد لاعب نشط في رمية الحظ الآن.
tossup-error-target-out-of-range = عتبة الهدف هي { $value }؛ يجب أن تكون من { $min } إلى { $max } نقطة.
tossup-error-dice-out-of-range = حجم المجموعة الجديدة هو { $value }؛ يجب أن يكون من { $min } إلى { $max } نردة.
tossup-error-rules-variant = قيمة القواعد "{ $variant }" غير مدعومة. اختر الكلاسيكية أو المتسامحة.

tossup-line-format = { $rank }. { $player }: { $points }
