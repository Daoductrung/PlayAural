# Humanity Cards - Arabic localization

game-name-humanitycards = بطاقات ضد الإنسانية

# الخيارات
hc-set-winning-score = النتيجة الفائزة: { $score }
hc-enter-winning-score = أدخل النتيجة الفائزة:
hc-option-changed-winning-score = تم ضبط النتيجة الفائزة على { $score }.
hc-desc-winning-score = عدد البطاقات الفائزة التي يحتاج اللاعب إلى جمعها للفوز بالمباراة (الافتراضي 7، النطاق 3-20).

hc-set-hand-size = حجم اليد: { $count }
hc-enter-hand-size = أدخل حجم اليد:
hc-option-changed-hand-size = تم ضبط حجم اليد على { $count }.
hc-desc-hand-size = عدد بطاقات الإجابة التي يحملها كل لاعب بعد كل إعادة تعبئة. اليد الأكبر تمنح خيارات أكثر لكنها تجعل الجولات أطول (الافتراضي 10، النطاق 5-15).

hc-set-card-language = لغة البطاقات: { $language }
hc-select-card-language = اختر لغة البطاقات
hc-option-changed-card-language = تم ضبط لغة البطاقات على { $language }.
hc-desc-card-language = تحدد لغة كل بطاقة محفِّز وإجابة في المباراة. هذا مستقل عن لغة واجهة كل لاعب (الافتراضي الإنجليزية؛ الخيارات: الإنجليزية والإسبانية والبرتغالية البرازيلية).
hc-card-language-pt-br = البرتغالية البرازيلية
hc-card-blank = فارغة
hc-card-same-again = البطاقة نفسها مرة أخرى

hc-set-card-packs = حزم البطاقات ({ $count } من { $total } محددة)
hc-option-changed-card-packs = تم تغيير اختيار حزم البطاقات.
hc-desc-card-packs = اختر حزم الإجابات والمحفِّزات الإنجليزية التي تُخلط في اللعبة. البطاقات المكررة تمامًا من الحزم المتداخلة تُدرج مرة واحدة فقط. يجب أن تبقى حزمة واحدة على الأقل محددة.
hc-pack-group-current = مجموعة الأوراق الأمريكية الرئيسية الحالية
hc-pack-group-main-decks = إصدارات المجموعة الرئيسية
hc-pack-group-official-add-ons = التوسعات والحزم الرسمية
hc-pack-group-family = إصدار العائلة
hc-pack-group-community = حزم المجتمع
hc-pack-group-all = كل الحزم

hc-set-czar-selection = اختيار الحَكَم: { $mode }
hc-select-czar-selection = اختر وضع اختيار الحَكَم
hc-option-changed-czar-selection = تم ضبط اختيار الحَكَم على { $mode }.
hc-desc-czar-selection = يتحكم في من يحكم كل جولة: بالتناوب حسب ترتيب الجلوس، أو بالاختيار العشوائي، أو الفائز بالجولة الأخيرة.

hc-set-num-judges = عدد الحُكَّام: { $count }
hc-enter-num-judges = أدخل عدد الحُكَّام:
hc-option-changed-num-judges = تم ضبط عدد الحُكَّام على { $count }.
hc-desc-num-judges = كم عدد الحُكَّام الذين يحكمون كل جولة. يجب أن يكون العدد أقل من عدد اللاعبين كي يتمكن لاعب واحد غير حَكَم على الأقل من التقديم؛ مع تعدد الحُكَّام، يمكن لأي حَكَم اختيار الفائز (الافتراضي 1، النطاق 1-3).

hc-czar-rotating = بالتناوب
hc-czar-random = عشوائي
hc-czar-winner = الفائز الأحدث

# سير اللعبة
hc-game-starting = جارٍ خلط مجموعات الأوراق...
hc-dealing-cards = توزيع { $count } بطاقة لكل لاعب.
hc-round-start = الجولة { $round }.

# إعلان الحَكَم
hc-judge-is = { $judges } { $count ->
    [1] هو الحَكَم
   *[other] هم الحُكَّام
}.
hc-you-are-judge = أنت الحَكَم في هذه الجولة.
hc-you-and-others-are-judges = أنت و{ $judges } الحُكَّام في هذه الجولة.

# البطاقة السوداء
hc-black-card = المحفِّز هو: { $text }
hc-black-card-draw = اسحب أولًا { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} إضافية.
hc-black-card-pick = اختر { $count }.
hc-view-black-card = عرض بطاقة السؤال
hc-no-question-card = لا توجد بطاقة سؤال نشطة الآن.

# مرحلة التقديم
hc-select-cards = اختر { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} من يدك.
hc-card-selected = { $text }، محددة
hc-card-selected-position = { $text }، محددة كإجابة { $position }
hc-card-not-selected = { $text }
hc-submit-cards = تقديم ({ $selected } من { $required } محددة)
hc-submission-progress = قدّم { $submitted } من { $total } لاعبين.
hc-already-submitted = لقد قدّمت بطاقاتك بالفعل.
hc-you-submitted = قدّمت بطاقاتك.
hc-player-submitted = قدّم { $player } البطاقات { GENDER_TERM($player_gender, "possessive-determiner") }.
hc-judge-cannot-submit = أنت الحَكَم في هذه الجولة، لذا لا يمكنك تقديم إجابة.
hc-not-submission-phase = يمكنك اختيار البطاقات البيضاء وتقديمها فقط أثناء مرحلة التقديم.
hc-card-not-in-hand = خانة البطاقة تلك ليست في يدك.
hc-judge-has-no-submission = ليس لدى الحَكَم تقديم لمعاينته في هذه الجولة.
hc-no-submission-active = لا يوجد تقديم نشط لمعاينته الآن.
hc-wrong-card-count = يجب أن تختار { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} بالضبط.
hc-selection-full = لقد اخترت { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} بالفعل. ألغِ تحديد واحدة قبل اختيار أخرى.

# مرحلة الحكم
hc-judging-start = وصلت كل البطاقات! حان وقت الحكم.
hc-choose-best-card = اختر أفضل بطاقة
hc-choose-best-card-for = اختر أفضل بطاقة تناسب: { $prompt }
hc-card-number = البطاقة { $number }
hc-submission-number = التقديم { $number }
hc-only-judges-pick = الحَكَم وحده يمكنه اختيار التقديم الفائز.
hc-not-judging-phase = يمكنك اختيار تقديم فائز فقط أثناء مرحلة الحكم.
hc-submission-not-available = لم يعد ذلك التقديم متاحًا.

# النتائج
hc-you-win-round = تفوز بالجولة! نتيجتك الآن { $score }.
hc-player-wins-round = يفوز { $player } بالجولة! النتيجة: { $score }.
hc-score-line = { $player }: { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}
hc-all-submissions = تقديمات أخرى:
hc-your-winning-answer = إجابتك الفائزة: { $text }
hc-winning-answer-player = إجابة { $player } الفائزة: { $text }
hc-your-other-submission = تقديمك الآخر: { $text }
hc-other-submission-player = { $player }: { $text }

# العرض
hc-preview-submission = عاين تقديمك
hc-view-submission = عرض تقديمك
hc-preview-submission-text = معاينة: { $text }
hc-your-submission = تقديمك: { $text }
hc-select-cards-first = اختر بطاقة واحدة على الأقل أولًا.
hc-review-hand = راجع يدك
hc-hand-empty = يدك فارغة.
hc-hand-card = { $number }. { $text }
hc-hand-card-selected = { $number }. { $text }، محددة كإجابة { $position }
hc-review-answers = راجع الإجابات
hc-answer-line = الإجابة { $number }: { $text }
hc-no-answers-to-review = لا توجد إجابات للمراجعة الآن.

# الفوز
hc-game-winner = يفوز { $player } بـ { $score } نقطة!
hc-you-win = تفوز بـ { $score } نقطة!

# إدارة مجموعة الأوراق
hc-deck-reshuffled = أُعيد خلط كومة رمي البطاقات البيضاء في المجموعة.
hc-black-deck-reshuffled = أُعيد خلط كومة رمي البطاقات السوداء في المجموعة.
hc-not-enough-cards = لا توجد بطاقات كافية. جرّب تفعيل حزم أكثر.
hc-error-too-many-judges = يتطلب { $judges } حُكَّام { $required } لاعبين على الأقل، لكن هذه الطاولة بها { $players }. قلّل عدد الحُكَّام أو أضف لاعبين.
hc-error-no-valid-packs = لم تُحدَّد أي حزمة بطاقات صالحة. حدد حزمة واحدة على الأقل قبل البدء.
hc-error-no-black-cards = لا تحتوي حزم البطاقات المحددة على أي بطاقات محفِّز سوداء. اختر حزمة أخرى قبل البدء.
hc-error-not-enough-white-cards = يحتاج { $players } لاعبين بحجم يد { $hand_size } إلى { $needed } بطاقة بيضاء على الأقل، لكن الحزم المحددة توفر { $available } فقط. فعّل حزمًا أكثر أو قلّل حجم اليد.
hc-error-pick-exceeds-hand-size = تتضمن الحزم المحددة محفِّزًا يتطلب { $pick } إجابات، لكن حجم اليد { $hand_size } فقط. زِد حجم اليد أو اختر حزمًا مختلفة.

# إدارة اليد
hc-toggle-card-keybind = تبديل البطاقة { $number }
hc-submit-cards-keybind = تقديم البطاقات

# دور من / حَكَم من
hc-whose-judge = من يحكم
hc-waiting-for = بانتظار تقديم { $names }.
hc-all-submitted-waiting-judge = قدّم كل اللاعبين. بانتظار حكم { $judge }.
