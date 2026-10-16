game-name-uno = أونو

# Colors
uno-color-red = أحمر
uno-color-yellow = أصفر
uno-color-green = أخضر
uno-color-blue = أزرق
uno-color-wild = متغيّرة

# Card names
uno-card-number = { $color } { $value }
uno-card-skip = { $color } تخطّي
uno-card-reverse = { $color } عكس
uno-card-draw-two = { $color } اسحب اثنتين
uno-card-wild = متغيّرة
uno-card-wild-four = متغيّرة اسحب أربعًا

# Options
uno-set-winning-score = حدّ النتيجة: { $score }
uno-enter-winning-score = أدخل حدّ النتيجة
uno-option-changed-winning-score = تم ضبط حدّ النتيجة على { $score }.
uno-desc-winning-score = حدّ النتيجة المستخدَم في وضع احتساب نقاط أونو المحدَّد (الافتراضي 300، النطاق 10-2000).

uno-set-scoring-mode = الاحتساب: { $mode }
uno-select-scoring-mode = اختر وضع الاحتساب
uno-option-changed-scoring-mode = تم ضبط الاحتساب على { $mode }.
uno-desc-scoring-mode = يحدّد ما إذا كان أول لاعب يبلغ الحدّ يفوز، أم أن اللاعبين الذين يبلغون الحدّ يُقصَون.
uno-scoring-first = أول من يبلغ الحدّ يفوز
uno-scoring-elimination = الإقصاء

uno-set-skip-after-draw = عقوبات السحب تُخطّي الدور: { $enabled }
uno-option-changed-skip-after-draw = عقوبات السحب تُخطّي الدور { $enabled }.
uno-desc-skip-after-draw = يتحكّم فيما إذا كانت عقوبتا اسحب اثنتين ومتغيّرة اسحب أربعًا تُخطّيان أيضًا دور اللاعب المستهدَف.

uno-set-responses = الردود التراكمية: { $enabled }
uno-option-changed-responses = الردود التراكمية { $enabled }.
uno-desc-responses = يتيح للاعبين تكديس بطاقات السحب ردًّا على عقوبتي اسحب اثنتين أو متغيّرة اسحب أربعًا.

uno-set-advanced-responses = الردود المتقدّمة: { $enabled }
uno-option-changed-advanced-responses = الردود المتقدّمة { $enabled }.
uno-desc-advanced-responses = يتيح ردودًا دفاعية إضافية على أكوام السحب، مثل مطابقة بطاقات التخطّي أو العكس أو المتغيّرة. يتطلّب الردود التراكمية.

uno-set-wait-for-draw-responses = انتظار ردود السحب: { $enabled }
uno-option-changed-wait-for-draw-responses = انتظار ردود السحب { $enabled }.
uno-desc-wait-for-draw-responses = إذا كوّنت البطاقة الأخيرة كومة سحب، يُنتظَر ردّ اللاعب التالي أو سحبه قبل احتساب نقاط الجولة. يتطلّب الردود التراكمية.

uno-set-bluff = تحدّيات متغيّرة اسحب أربعًا: { $enabled }
uno-option-changed-bluff = تحدّيات متغيّرة اسحب أربعًا { $enabled }.
uno-desc-bluff = يفعّل قواعد تحدّي متغيّرة اسحب أربعًا على اللعبات غير القانونية.

uno-set-straights = التسلسلات: { $enabled }
uno-option-changed-straights = التسلسلات { $enabled }.
uno-desc-straights = يتيح للاعب الاستمرار خارج دوره بالرقم التالي أو السابق من اللون نفسه بعد بطاقة رقمية.

uno-set-interceptions = الاعتراضات: { $enabled }
uno-option-changed-interceptions = الاعتراضات { $enabled }.
uno-desc-interceptions = يتيح للاعبين التدخّل خارج دورهم ببطاقة مطابقة تمامًا. المحاولات غير الصحيحة تضيف 3 نقاط جزاء.

uno-set-super-interceptions = الاعتراضات الفائقة: { $enabled }
uno-option-changed-super-interceptions = الاعتراضات الفائقة { $enabled }.
uno-desc-super-interceptions = يوسّع الاعتراضات لمطابقة الرقم أو رمز الحركة حتى عند اختلاف اللون. يتطلّب الاعتراضات.

uno-set-zero-seven = قاعدة الصفر/السبعة: { $enabled }
uno-option-changed-zero-seven = قاعدة الصفر/السبعة { $enabled }.
uno-desc-zero-seven-rule = يفعّل قاعدة البيت حيث يُدوّر الصفر أيدي الجميع، وتتيح السبعة للاعب تبديل الأيدي أو الرفض.

uno-set-free-draws = السحوبات المجانية في كل دور: { $count }
uno-enter-free-draws = أدخل عدد السحوبات المجانية في كل دور
uno-option-changed-free-draws = تم ضبط السحوبات المجانية في كل دور على { $count }.
uno-desc-free-draws = كم مرة يجوز للاعب بشري أن يسحب رغم امتلاكه بطاقة قابلة للعب (الافتراضي 0، النطاق 0-999).

# Option validation
uno-error-advanced-responses-require-responses = تتطلّب الردود المتقدّمة تفعيل الردود التراكمية.
uno-error-wait-responses-require-responses = يتطلّب انتظار ردود السحب تفعيل الردود التراكمية.
uno-error-super-interceptions-require-interceptions = تتطلّب الاعتراضات الفائقة تفعيل الاعتراضات.

# Actions
uno-draw = سحب
uno-say-uno = أونو
uno-read-top = قراءة البطاقة العليا
uno-read-color = قراءة اللون الحالي
uno-read-counts = قراءة أعداد البطاقات
uno-read-hand = قراءة قيمة يدك
uno-sort-color = ترتيب حسب اللون
uno-sort-number = ترتيب حسب الرقم

# Gameplay announcements
uno-new-hand = الجولة { $round }.
uno-start-card = يكشف { $player } عن { $card }.
uno-you-start-card = تكشف عن { $card }.
uno-current-color = اللون الحالي: { $color }.
uno-dealt-cards = يُوزَّع على الجميع { $cards } بطاقات.
uno-choose-opening-color-you = اختر اللون الافتتاحي.
uno-choose-opening-color-player = على { $player } اختيار اللون الافتتاحي.
uno-direction-reversed = انعكس اتجاه اللعب.
uno-player-plays = يلعب { $player } { $card }.
uno-you-play = تلعب { $card }.
uno-player-chooses-color = يختار { $player } { $color }.
uno-you-choose-color = تختار { $color }.
uno-player-draws-one = يسحب { $player } بطاقة.
uno-player-draws-many = يسحب { $player } { $count } بطاقات.
uno-you-draw-one = تسحب بطاقة.
uno-you-draw-many = تسحب { $count } بطاقات.
uno-cant-play = لا يستطيع { $player } اللعب.
uno-you-cant-play = لا يمكنك اللعب.
uno-you-skipped = تم تخطّي دورك.
uno-says-uno = يقول { $player } أونو!
uno-you-say-uno = تقول أونو!
uno-callout = يُنبّه { $caller } على { $player } لعدم قوله أونو! يسحب { $player } { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
uno-you-callout = تُنبّه على { $player } لعدم قوله أونو! يسحب { $player } { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
uno-callout-you = يُنبّه { $caller } عليك لعدم قولك أونو! تسحب { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
uno-error-already-said-uno = لقد قلت أونو بالفعل.
uno-error-no-uno-call = لا يوجد تنبيه أونو متاح الآن.
uno-cannot-play-that = لا يمكنك لعب { $card }. { $reason }
uno-reshuffle = إعادة خلط كومة المرميّات.
uno-hand-blocked = لا أحد يستطيع اللعب. تنتهي الجولة.
uno-error-choose-color-first = اختر لونًا لبطاقتك المتغيّرة قبل لعب بطاقة أخرى.
uno-error-wait-color-choice = انتظر اختيار لاعب البطاقة المتغيّرة للون قبل أن تلعب.
uno-error-wild-transition = انتظر حتى يسري اللون المختار قبل لعب بطاقة أخرى.
uno-error-choose-swap-first = اختر هدفًا لتبديل الأيدي أو ارفض قبل القيام بإجراء آخر.
uno-error-wait-swap-choice = انتظر انتهاء اختيار تبديل أيدي السبعة قبل أن تلعب.
uno-error-wait-next-hand = انتظر بدء الجولة التالية قبل لعب بطاقة.
uno-error-wait-intro = انتظر انتهاء إعداد الجولة قبل لعب بطاقة.
uno-reason-draw-stack-response = هناك كومة سحب من { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} ضدّك؛ العب بطاقة ردّ صالحة أو اسحب العقوبة.
uno-reason-draw-stack-no-response = هناك عقوبة سحب من { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} ضدّك، والردود التراكمية مُعطَّلة؛ اسحب العقوبة بدلًا من ذلك.
uno-reason-match-required = البطاقة العليا هي { $top }، واللون النشط هو { $color }؛ طابِق اللون، أو طابِق الرقم أو رمز الحركة، أو العب بطاقة متغيّرة.
uno-reason-card-not-available = تلك البطاقة غير متاحة في الحالة الراهنة.

# Bluff challenge
uno-bluff-challenge = تحدّي متغيّرة اسحب أربعًا
uno-bluff-caught = لعب { $player } متغيّرة اسحب أربعًا بشكل غير قانوني ويسحب { $count } بطاقات!
uno-you-bluff-caught = لعبت متغيّرة اسحب أربعًا بشكل غير قانوني وتسحب { $count } بطاقات!
uno-bluff-wrong = تحدّى { $player } متغيّرة اسحب أربعًا بالخطأ ويسحب { $count } بطاقات!
uno-you-bluff-wrong = تحدّيت متغيّرة اسحب أربعًا بالخطأ وتسحب { $count } بطاقات!

# Zero / seven rule
uno-rotate-hands = يمرّر الجميع أيديهم!
uno-swap-hands = يبدّل { $player } الأيدي مع { $target }!
uno-you-swap = تبدّل الأيدي مع { $target }!
uno-swap-with-you = يبدّل { $player } الأيدي معك!
uno-swap-with = تبديل الأيدي مع { $player }
uno-choose-swap = اختر لاعبًا لتبديل الأيدي معه، أو ارفض.
uno-swap-none = عدم التبديل
uno-you-swap-none = تحتفظ بيدك.
uno-swap-none-other = يحتفظ { $player } بيد { GENDER_TERM($player_gender, "possessive-determiner") }.

# Interceptions / straights
uno-player-intercepts = يعترض { $player } بـ{ $card }!
uno-you-intercept = تعترض بـ{ $card }!
uno-bad-intercept = اعتراض غير صالح. { $points } نقاط جزاء.
uno-not-your-turn = ليس دورك.

# Info
uno-no-top = لا توجد بطاقة عليا بعد.
uno-top-card = { $card }.
uno-color-is = { $color }.
uno-count-you = أنت { $count }
uno-count-player = { $player } { $count }
uno-deck-count = مجموعة الأوراق { $count }
uno-sorting-color = الترتيب حسب اللون.
uno-sorting-number = الترتيب حسب الرقم.

# Round / game end
uno-round-winner = يفوز { $player } بالجولة!
uno-you-win-round = تفوز بالجولة!
uno-round-points-from = { $points } من { $player }
uno-round-points-from-you = { $points } منك
uno-round-points-from-with-interception = { $points } من { $player } ({ $hand_points } يد + { $penalty } عقوبة اعتراض)
uno-round-points-from-you-with-interception = { $points } منك ({ $hand_points } يد + { $penalty } عقوبة اعتراض)
uno-round-details-none = لم تُؤخذ أي نقاط من الخصوم.
uno-round-summary = { $details }. يكسب { $player } { $total }.
uno-round-summary-you = { $details }. تكسب { $total }.
uno-you-add-penalty-points = تضيف { $points } نقاط جزاء إلى مجموعك في هذه الجولة.
uno-player-adds-penalty-points = يضيف { $player } { $points } نقاط جزاء إلى مجموع { GENDER_TERM($player_gender, "possessive-determiner") } في هذه الجولة.
uno-you-add-penalty-points-with-interception = تضيف { $points } نقاط جزاء إلى مجموعك في هذه الجولة ({ $hand_points } من يدك زائد { $penalty } عقوبة اعتراض).
uno-player-adds-penalty-points-with-interception = يضيف { $player } { $points } نقاط جزاء إلى مجموع { GENDER_TERM($player_gender, "possessive-determiner") } في هذه الجولة ({ $hand_points } من يد { GENDER_TERM($player_gender, "possessive-determiner") } زائد { $penalty } عقوبة اعتراض).
uno-you-are-eliminated = بلغت حدّ الإقصاء البالغ { $limit } نقطة وخرجت من اللعبة.
uno-player-is-eliminated = بلغ { $player } حدّ الإقصاء البالغ { $limit } نقطة وخرج من اللعبة.
uno-you-win-game =
    { $mode ->
        [elimination] أنت آخر لاعب متبقٍّ وتفوز بـ{ $score } نقطة جزاء.
       *[first_to_limit] تفوز باللعبة بـ{ $score } نقطة!
    }
uno-player-wins-game =
    { $mode ->
        [elimination] { $player } آخر لاعب متبقٍّ ويفوز بـ{ $score } نقطة جزاء.
       *[first_to_limit] يفوز { $player } باللعبة بـ{ $score } نقطة!
    }
uno-game-tie = أُقصي الجميع. اللعبة تعادل!
uno-line-format = { $rank }. { $player }: { $score }
uno-score-line-first = { $player }: { $score }/{ $target } نقطة.
uno-score-line-elimination = { $player }: { $score }/{ $target } نقطة جزاء.

# Hand value (d key)
uno-read-hand-value = { $count ->
    [one] { $count } بطاقة
   *[other] { $count } بطاقات
 } بقيمة { $points ->
    [one] { $points } نقطة
   *[other] { $points } نقاط
 }.
