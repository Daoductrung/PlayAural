game-name-midnight = 1-4-24

midnight-roll = ارمِ النرد
midnight-bank = إيداع
midnight-check-dice = اقرأ النرد الحالي
midnight-check-round-status = عرض حالة الجولة

midnight-round-start = الجولة { $round } من { $total }.
midnight-round-start-brief = الجولة { $round }/{ $total }.

midnight-you-rolled = رميت: { $dice }.
midnight-player-rolled = رمى { $player }: { $dice }.
midnight-you-rolled-brief = ترمي { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = تحتفظ بحجر النرد { $index }، الذي يُظهر { $die }.
midnight-player-keeps = يحتفظ { $player } بحجر النرد { $index }، الذي يُظهر { $die }.
midnight-you-keep-brief = تحتفظ بـ { $die }.
midnight-player-keeps-brief = يحتفظ { $player } بـ { $die }.
midnight-you-unkeep = تُعيد حجر النرد { $index }، الذي يُظهر { $die }، إلى مجموعة إعادة الرمي.
midnight-player-unkeeps = يُعيد { $player } حجر النرد { $index }، الذي يُظهر { $die }، إلى مجموعة إعادة الرمي.
midnight-you-unkeep-brief = تُعيد رمي { $die }.
midnight-player-unkeeps-brief = يُعيد { $player } رمي { $die }.

midnight-you-scored = تتأهّل بالرقمين 1 و4، وتسجّل { $score } من { $scoring_dice }.
midnight-scored = يتأهّل { $player } بالرقمين 1 و4، ويسجّل { $score } من { $scoring_dice }.
midnight-you-scored-brief = تسجّل { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = لا تتأهّل لأنك تفتقد { $missing }.
midnight-player-disqualified = لا يتأهّل { $player } لأن { GENDER_TERM($player_gender, "subject-be") } يفتقد { $missing }.
midnight-you-disqualified-brief = تفتقد { $missing }.
midnight-player-disqualified-brief = يفتقد { $player } { $missing }.
midnight-you-win-round = تفوز بالجولة { $round } بـ { $score }.
midnight-round-winner = يفوز { $player } بالجولة { $round } بـ { $score }.
midnight-you-win-round-brief = تفوز بالجولة { $round }: { $score }.
midnight-round-winner-brief = يفوز { $player } بالجولة { $round }: { $score }.
midnight-round-tie = تعادلت الجولة عند { $score } بين { $players }. لا يُمنح فوز بالجولة.
midnight-all-disqualified = أخفق كل اللاعبين في الحصول على الرقمين 1 و4 المطلوبين. لا يُمنح فوز بالجولة.
midnight-all-disqualified-brief = لا أحد يتأهّل.

midnight-you-win-game = تفوز باللعبة بـ { $wins } { $wins ->
    [one] جولة مكسوبة
    [two] جولتان مكسوبتان
    [few] جولات مكسوبة
    [many] جولة مكسوبة
   *[other] جولة مكسوبة
}!
midnight-game-winner = يفوز { $player } باللعبة بـ { $wins } { $wins ->
    [one] جولة مكسوبة
    [two] جولتان مكسوبتان
    [few] جولات مكسوبة
    [many] جولة مكسوبة
   *[other] جولة مكسوبة
}!
midnight-you-win-game-brief = تفوز: { $wins }.
midnight-game-winner-brief = يفوز { $player }: { $wins }.
midnight-game-tie = إنه تعادل في اللعبة. أنهى { $players } كل منهم بـ { $wins } { $wins ->
    [one] جولة مكسوبة
    [two] جولتان مكسوبتان
    [few] جولات مكسوبة
    [many] جولة مكسوبة
   *[other] جولة مكسوبة
}.
midnight-set-rounds = الجولات المراد لعبها: { $rounds }
midnight-enter-rounds = أدخل عدد الجولات المراد لعبها:
midnight-option-changed-rounds = تم تغيير الجولات المراد لعبها إلى { $rounds }
midnight-desc-rounds = عدد جولات اللعبة التي تُلعب قبل التسجيل النهائي (الافتراضي 5، المدى 1-20).
midnight-error-rounds-out-of-range = تدعم اللعبة من { $min } إلى { $max } جولة. الإعداد الحالي: { $rounds }.

midnight-need-to-roll = ارمِ النرد قبل اختيار النرد للاحتفاظ به.
midnight-no-dice-to-keep = لم يتبقَّ نرد للرمي أو الاحتفاظ.
midnight-must-keep-one = احتفظ بحجر نرد مرمي حديثًا واحد على الأقل قبل الرمي مجددًا.
midnight-must-roll-first = ارمِ النرد قبل إيداع دورك.
midnight-keep-all-first = احسم كل حجر نرد قبل الإيداع. احتفظ بكل الأحجار غير المقفلة أو أعِدها أولًا.
midnight-invalid-die-index = ذلك الحجر غير متاح في هذه الرمية.

midnight-die-locked = { $value } (مقفل)
midnight-die-kept = { $value } (محتفظ به)
midnight-die-value = { $value }
midnight-die-index = حجر النرد { $index }

midnight-your-dice-not-rolled = لم ترمِ بعد في هذا الدور.
midnight-player-dice-not-rolled = لم يرمِ { $player } بعد في هذا الدور.
midnight-your-dice-status =
    { $qualified ->
        [yes] نردك: { $dice }. المقفل: { $locked }؛ المحتفظ به للرمية التالية: { $kept }؛ النرد الحيّ: { $remaining }. ستكون نتيجة التأهّل الحالية { $score } من { $scoring_dice }.
       *[no] نردك: { $dice }. المقفل: { $locked }؛ المحتفظ به للرمية التالية: { $kept }؛ النرد الحيّ: { $remaining }. ما زلت بحاجة إلى { $missing } للتأهّل.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] نرد { $player }: { $dice }. المقفل: { $locked }؛ المحتفظ به للرمية التالية: { $kept }؛ النرد الحيّ: { $remaining }. ستكون نتيجة التأهّل الحالية { $score } من { $scoring_dice }.
       *[no] نرد { $player }: { $dice }. المقفل: { $locked }؛ المحتفظ به للرمية التالية: { $kept }؛ النرد الحيّ: { $remaining }. المتطلب المتبقّي بالنسبة إلى { GENDER_TERM($player_gender, "object") } هو { $missing }.
    }
midnight-status-round = الجولة { $round } من { $total }
midnight-status-current-player = الدور الحالي: { $player }
midnight-status-current-not-rolled = لم يرمِ { $player } بعد.
midnight-status-current-dice =
    { $qualified ->
        [yes] النرد الحالي لـ { $player }: { $dice }. النتيجة المحتملة: { $score } من { $scoring_dice }. مقفل { $locked }، محتفظ به { $kept }، حيّ { $remaining }.
       *[no] النرد الحالي لـ { $player }: { $dice }. مفقود { $missing }. مقفل { $locked }، محتفظ به { $kept }، حيّ { $remaining }.
    }
midnight-status-dice-not-rolled = لم يُرمَ
midnight-status-last-qualified = الدور الأخير: رمى { $player } { $dice } وسجّل { $score }.
midnight-status-last-disqualified = الدور الأخير: رمى { $player } { $dice } ولم يتأهّل.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } من الجولات المكسوبة؛ الجولة الحالية { $current }، متأهّل.
       *[no] { $rank }. { $player }: { $wins } من الجولات المكسوبة؛ الجولة الحالية { $current }، غير متأهّل.
    }

midnight-score-unit-round-wins = { $count ->
    [one] جولة مكسوبة
    [two] جولتان مكسوبتان
    [few] جولات مكسوبة
    [many] جولة مكسوبة
   *[other] جولة مكسوبة
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] جولة مكسوبة
    [two] جولتان مكسوبتان
    [few] جولات مكسوبة
    [many] جولة مكسوبة
   *[other] جولة مكسوبة
}

