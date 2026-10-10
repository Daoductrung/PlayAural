game-name-farkle = فاركل

farkle-roll = ارمِ { $count } { $count ->
    [one] حجر نرد
    [two] حجرا نرد
    [few] أحجار نرد
    [many] حجر نرد
   *[other] حجر نرد
}
farkle-bank = أودِع { $points } نقطة

farkle-take-single-one = واحد مفرد مقابل { $points } نقطة
farkle-take-single-five = خمسة مفردة مقابل { $points } نقطة
farkle-take-three-kind = ثلاثة من { $number } مقابل { $points } نقطة
farkle-take-four-kind = أربعة من { $number } مقابل { $points } نقطة
farkle-take-five-kind = خمسة من { $number } مقابل { $points } نقطة
farkle-take-six-kind = ستة من { $number } مقابل { $points } نقطة
farkle-take-small-straight = تسلسل صغير مقابل { $points } نقطة
farkle-take-large-straight = تسلسل كبير مقابل { $points } نقطة
farkle-take-three-pairs = ثلاثة أزواج مقابل { $points } نقطة
farkle-take-double-triplets = ثلاثيتان مقابل { $points } نقطة
farkle-take-full-house = أربعة متشابهة مع زوج مقابل { $points } نقطة

farkle-you-roll = ترمي { $count } { $count ->
    [one] حجر نرد
    [two] حجرا نرد
    [few] أحجار نرد
    [many] حجر نرد
   *[other] حجر نرد
}.
farkle-player-rolls = يرمي { $player } { $count } { $count ->
    [one] حجر نرد
    [two] حجرا نرد
    [few] أحجار نرد
    [many] حجر نرد
   *[other] حجر نرد
}.
farkle-you-roll-brief = ترمي { $count }.
farkle-player-rolls-brief = يرمي { $player } { $count }.
farkle-roll-result = يُظهر النرد: { $dice }.
farkle-roll-result-brief = النرد: { $dice }.
farkle-you-farkle = فاركل! تخسر { $points } من نقاط الدور.
farkle-player-farkles = فاركل! يخسر { $player } { $points } من نقاط الدور.
farkle-you-farkle-brief = فاركل: تخسر { $points }.
farkle-player-farkles-brief = فاركل: يخسر { $player } { $points }.

farkle-you-take-combo = تحتفظ بـ { $combo } مقابل { $points } نقطة.
farkle-player-takes-combo = يحتفظ { $player } بـ { $combo } مقابل { $points } نقطة.
farkle-you-take-combo-brief = أنت: { $combo }، +{ $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }، +{ $points }.

farkle-you-hot-dice = نرد ساخن! سجّلت بالأحجار الستة كلها ويمكنك رميها جميعًا مرة أخرى.
farkle-player-hot-dice = نرد ساخن! سجّل { $player } بالأحجار الستة كلها ويمكنه رميها جميعًا مرة أخرى.
farkle-you-hot-dice-brief = أنت: نرد ساخن.
farkle-player-hot-dice-brief = { $player }: نرد ساخن.

farkle-you-bank = تودِع { $points } نقطة. أصبح مجموعك الآن { $total }.
farkle-player-banks = يودِع { $player } { $points } نقطة ليصبح مجموعه { $total }.
farkle-you-bank-brief = تودِع { $points }؛ المجموع { $total }.
farkle-player-banks-brief = يودِع { $player } { $points }؛ المجموع { $total }.

farkle-you-win = تفوز بـ { $score } نقطة!
farkle-winner = يفوز { $player } بـ { $score } نقطة!
farkle-you-win-brief = تفوز: { $score }.
farkle-winner-brief = يفوز { $player }: { $score }.
farkle-winners-tie = تعادل عند الهدف! لاعبو كسر التعادل: { $players }.
farkle-tiebreaker-round-start = جولة كسر التعادل { $round }. ما زال يتنافس: { $players }.

farkle-your-turn-score = لديك { $points } نقطة في هذا الدور.
farkle-turn-score = لدى { $player } { $points } نقطة في هذا الدور.
farkle-no-turn = لا أحد يأخذ دورًا حاليًا.
farkle-set-target-score = النتيجة المستهدفة: { $score }
farkle-enter-target-score = أدخل النتيجة المستهدفة (500-5000):
farkle-option-changed-target = تم ضبط النتيجة المستهدفة على { $score }.
farkle-desc-target-score = النتيجة اللازمة لتفعيل أدوار فاركل الأخيرة واحتمال الفوز (الافتراضي 1000، المدى 500-5000).

farkle-set-entrance-score = الحد الأدنى لنتيجة الدخول: { $score }
farkle-enter-entrance-score = أدخل الحد الأدنى لنتيجة الدخول (0-5000):
farkle-option-changed-entrance = تم ضبط الحد الأدنى لنتيجة الدخول على { $score }.
farkle-desc-min-entrance-score = الحد الأدنى لنتيجة الدور المطلوب لإيداع أول نقاط للاعب. لا يمكن أن يكون أعلى من النتيجة المستهدفة (الافتراضي 50، المدى 0-5000).

farkle-set-bank-score = الحد الأدنى لنتيجة الإيداع: { $score }
farkle-enter-bank-score = أدخل الحد الأدنى لنتيجة الإيداع (0-5000):
farkle-option-changed-bank = تم ضبط الحد الأدنى لنتيجة الإيداع على { $score }.
farkle-desc-min-bank-score = الحد الأدنى لنتيجة الدور المطلوب قبل أن يصبح الإيداع متاحًا بعد أن يكون اللاعب على اللوحة بالفعل. لا يمكن أن يكون أعلى من النتيجة المستهدفة (الافتراضي 30، المدى 0-5000).

farkle-error-entrance-above-target = لا يمكن أن يكون الحد الأدنى لنتيجة الدخول ({ $entrance }) أعلى من النتيجة المستهدفة ({ $target }).
farkle-error-bank-above-target = لا يمكن أن يكون الحد الأدنى لنتيجة الإيداع ({ $bank }) أعلى من النتيجة المستهدفة ({ $target }).

farkle-must-take-combo = يجب أن تحتفظ بحجر نرد مُسجِّل أو تركيبة واحدة على الأقل قبل الرمي مجددًا.
farkle-cannot-bank = لا يمكنك الإيداع إلا بعد الاحتفاظ بحجر نرد مُسجِّل أو تركيبة في هذا الدور.
farkle-must-reach-entrance-score = تحتاج إلى { $points } من نقاط الدور على الأقل قبل إيداع أول نتيجة لك.
farkle-must-reach-bank-score = تحتاج إلى { $points } من نقاط الدور على الأقل قبل الإيداع.
farkle-confirm-risky-roll = يمكنك إيداع { $points } نقطة الآن. الرمي مجددًا يخاطر بخسارتها؛ كرّر الرمي خلال { $seconds } ثانية للتأكيد.
farkle-invalid-combo-action = اختيار التسجيل هذا غير معروف. يرجى اختيار إحدى التركيبات المدرجة حاليًا.
farkle-combo-no-longer-available = لم تعد تلك التركيبة متاحة. تم تحديث خيارات التسجيل الحالية.
farkle-combo-single-1 = واحد مفرد
farkle-combo-single-5 = خمسة مفردة
farkle-combo-three-kind = ثلاثة من { $number }
farkle-combo-four-kind = أربعة من { $number }
farkle-combo-five-kind = خمسة من { $number }
farkle-combo-six-kind = ستة من { $number }
farkle-combo-small-straight = تسلسل صغير
farkle-combo-large-straight = تسلسل كبير
farkle-combo-three-pairs = ثلاثة أزواج
farkle-combo-double-triplets = ثلاثيتان
farkle-combo-full-house = أربعة متشابهة مع زوج

farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } مقابل { $points } نقطة

farkle-check-turn-score = فحص نتيجة الدور
farkle-roll-label = ارمِ النرد
farkle-bank-label = أودِع النقاط

