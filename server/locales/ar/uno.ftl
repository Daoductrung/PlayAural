game-name-uno = اونو
# Colors
uno-color-red = أحمر
uno-color-yellow = أصفر
uno-color-green = أخضر
uno-color-blue = أزرق
uno-color-wild = بري
# Card names
uno-card-number = { $color } { $value }
uno-card-skip = { $color } تخطي
uno-card-reverse = { $color } عكس
uno-card-draw-two = { $color } رسم اثنين
uno-card-wild = بري
uno-card-wild-four = وايلد درو فور
# Options
uno-set-winning-score = حد النتيجة: { $score }
uno-enter-winning-score = أدخل حد النتيجة
uno-option-changed-winning-score = تم ضبط حد النتيجة على { $score }.
uno-desc-winning-score = حد النتيجة المستخدم بواسطة وضع تسجيل UNO المحدد (الافتراضي 300، النطاق 10-2000).
uno-set-scoring-mode = التسجيل: { $mode }
uno-select-scoring-mode = حدد وضع التسجيل
uno-option-changed-scoring-mode = تم ضبط النتيجة على { $mode }.
uno-desc-scoring-mode = يختار ما إذا كان أول لاعب يصل إلى الحد سيفوز، أو سيتم استبعاد اللاعبين الذين وصلوا إلى الحد.
uno-scoring-first = أول من يحد من الانتصارات
uno-scoring-elimination = القضاء
uno-set-skip-after-draw = تعادل ضربات الجزاء تخطي الدور: { $enabled }
uno-option-changed-skip-after-draw = تعادل ضربات الجزاء تخطي الدور { $enabled }.
uno-desc-skip-after-draw = التحكم في ما إذا كانت ضربات الجزاء Draw Two وWild Draw Four تتخطى دور الهدف أيضًا.
uno-set-responses = تكديس الردود: { $enabled }
uno-option-changed-responses = تكديس الردود { $enabled }.
uno-desc-responses = يسمح للاعبين بتكديس بطاقات السحب ردًا على عقوبات Draw Two أو Wild Draw Four.
uno-set-advanced-responses = الردود المتقدمة: { $enabled }
uno-option-changed-advanced-responses = ردود متقدمة { $enabled }.
uno-desc-advanced-responses = يسمح باستجابات دفاعية إضافية لرسم مجموعات، مثل مطابقة بطاقات التخطي أو العكس أو Wild Cards. يتطلب التراص الردود.
uno-set-wait-for-draw-responses = انتظر ردود السحب: { $enabled }
uno-option-changed-wait-for-draw-responses = انتظر ردود السحب { $enabled }.
uno-desc-wait-for-draw-responses = إذا قامت البطاقة الأخيرة بإنشاء كومة سحب، فانتظر حتى يستجيب اللاعب التالي أو يسحب قبل تسجيل الجولة. يتطلب التراص الردود.
uno-set-bluff = تحديات Wild Draw Four: { $enabled }
uno-option-changed-bluff = تحديات Wild Draw Four { $enabled }.
uno-desc-bluff = تمكين قواعد التحدي Wild Draw Four للمسرحيات غير القانونية.
uno-set-straights = المستقيم : { $enabled }
uno-option-changed-straights = المستقيمات { $enabled }.
uno-desc-straights = يتيح للاعب الاستمرار خارج الدور بالرقم التالي أو السابق من نفس اللون بعد بطاقة الأرقام.
uno-set-interceptions = الاعتراضات: { $enabled }
uno-option-changed-interceptions = اعتراضات { $enabled }.
uno-desc-interceptions = يتيح للاعبين القفز خارج الدور باستخدام بطاقة مطابقة تمامًا. المحاولات غير الصالحة تضيف 3 نقاط جزاء.
uno-set-super-interceptions = اعتراضات فائقة: { $enabled }
uno-option-changed-super-interceptions = اعتراضات فائقة { $enabled }.
uno-desc-super-interceptions = يقوم بتوسيع الاعتراضات لمطابقة الرقم أو رمز الإجراء حتى عندما يختلف اللون. يتطلب اعتراضات.
uno-set-zero-seven = قاعدة الصفر / السبعة : { $enabled }
uno-option-changed-zero-seven = قاعدة صفر / سبعة { $enabled }.
uno-desc-zero-seven-rule = لتمكين قاعدة المجموعة حيث يقوم 0 بتدوير أيدي الجميع و7 يسمح للاعب بتبديل الأيدي أو الرفض.
uno-set-free-draws = سحوبات مجانية لكل دور: { $count }
uno-enter-free-draws = أدخل سحوبات مجانية لكل دور
uno-option-changed-free-draws = تم ضبط السحوبات المجانية لكل دور على { $count }.
uno-desc-free-draws = كم مرة يمكن للاعب أن يرسم على الرغم من أنه يحمل بطاقة قابلة للعب (الافتراضي 0، النطاق 0-999).
# Option validation
uno-error-advanced-responses-require-responses = تتطلب الاستجابات المتقدمة تمكين تكديس الاستجابات.
uno-error-wait-responses-require-responses = يتطلب انتظار استجابات السحب تمكين تجميع الاستجابات.
uno-error-super-interceptions-require-interceptions = تتطلب الاعتراضات الفائقة تفعيل الاعتراضات.
# Actions
uno-draw = رسم
uno-say-uno = اونو
uno-read-top = قراءة البطاقة العليا
uno-read-color = قراءة اللون الحالي
uno-read-counts = قراءة عدد البطاقات
uno-read-hand = اقرأ قيمة يدك
uno-sort-color = فرز حسب اللون
uno-sort-number = الترتيب حسب الرقم
# Gameplay announcements
uno-new-hand = جولة { $round }.
uno-start-card = { $player } يظهر { $card }.
uno-you-start-card = لقد حضرت { $card }.
uno-current-color = اللون الحالي: { $color }.
uno-dealt-cards = يتم التعامل مع الجميع { $cards } بطاقات.
uno-choose-opening-color-you = اختر لون الافتتاح.
uno-choose-opening-color-player = { $player } يجب اختيار اللون الافتتاحي.
uno-direction-reversed = يتم عكس الاتجاه.
uno-player-plays = { $player } مسرحيات { $card }.
uno-you-play = أنت تلعب { $card }.
uno-player-chooses-color = { $player } يختار { $color }.
uno-you-choose-color = اخترت { $color }.
uno-player-draws-one = { $player } يرسم بطاقة.
uno-player-draws-many = { $player } رسم { $count } بطاقات.
uno-you-draw-one = أنت ترسم بطاقة.
uno-you-draw-many = أنت ترسم { $count } بطاقات.
uno-cant-play = { $player } لا أستطيع اللعب.
uno-you-cant-play = لا يمكنك اللعب.
uno-you-skipped = لقد تم تخطيك.
uno-says-uno = { $player } يقول أونو!
uno-you-say-uno = أنت تقول أونو!
uno-callout =
    { $caller } ينادي { $player } لعدم قول UNO! { $player } رسم { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
uno-you-callout =
    أنت تنادي { $player } لعدم قول UNO! { $player } رسم { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
uno-callout-you =
    { $caller } يناديك لعدم قول UNO! أنت ترسم { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
uno-error-already-said-uno = لقد قلت بالفعل UNO.
uno-error-no-uno-call = لا توجد مكالمة UNO متاحة الآن.
uno-cannot-play-that = لا يمكنك اللعب { $card }. { $reason }
uno-reshuffle = إعادة خلط كومة المهملات.
uno-hand-blocked = لا أحد يستطيع اللعب. تنتهي الجولة.
uno-error-choose-color-first = اختر لونًا لبطاقة Wild الخاصة بك قبل لعب بطاقة أخرى.
uno-error-wait-color-choice = انتظر حتى يختار لاعب Wild Card اللون قبل اللعب.
uno-error-wild-transition = انتظر حتى يصبح اللون المختار ساري المفعول قبل لعب بطاقة أخرى.
uno-error-choose-swap-first = اختر هدفًا للتبديل اليدوي أو ارفضه قبل اتخاذ إجراء آخر.
uno-error-wait-swap-choice = انتظر حتى ينتهي خيار تبديل الأيدي السبعة قبل اللعب.
uno-error-wait-next-hand = انتظر حتى تبدأ الجولة التالية قبل لعب البطاقة.
uno-error-wait-intro = انتظر حتى ينتهي إعداد الجولة قبل لعب البطاقة.
uno-reason-draw-stack-response =
    هناك مكدس سحب لـ { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } ضدك؛ لعب بطاقة استجابة صالحة أو رسم العقوبة.
uno-reason-draw-stack-no-response =
    هناك عقوبة التعادل { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } ضدك، وتكديس الردود متوقف؛ رسم العقوبة بدلا من ذلك.
uno-reason-match-required = البطاقة العلوية هي { $top }واللون النشط هو { $color }; قم بمطابقة اللون أو مطابقة الرقم أو رمز الإجراء أو تشغيل بطاقة Wild Card.
uno-reason-card-not-available = هذه البطاقة غير متوفرة في الوضع الحالي.
# Bluff challenge
uno-bluff-challenge = تحدي وايلد دراو فور
uno-bluff-caught = { $player } لعبت لعبة Wild Draw Four غير القانونية وتعادلت { $count } بطاقات!
uno-you-bluff-caught = لقد لعبت لعبة Wild Draw Four غير القانونية وقمت بالرسم { $count } بطاقات!
uno-bluff-wrong = { $player } تحدى Wild Draw Four بشكل غير صحيح وتعادل { $count } بطاقات!
uno-you-bluff-wrong = لقد تحديت Wild Draw Four بشكل غير صحيح وقمت بالرسم { $count } بطاقات!
# Zero / seven rule
uno-rotate-hands = الجميع يمرر أيديهم!
uno-swap-hands = { $player } يتبادل الأيدي مع { $target }!
uno-you-swap = قمت بتبديل الأيدي مع { $target }!
uno-swap-with-you = { $player } يتبادل الأيدي معك!
uno-swap-with = مبادلة الأيدي مع { $player }
uno-choose-swap = اختر لاعبًا لتبديل الأيدي معه أو رفضه.
uno-swap-none = لا تبدل
uno-you-swap-none = أنت تبقي يدك.
uno-swap-none-other = { $player } يبقي أيديهم.
# Interceptions / straights
uno-player-intercepts = { $player } يعترض مع { $card }!
uno-you-intercept = أنت تعترض مع { $card }!
uno-bad-intercept = اعتراض غير صالح. { $points } نقاط الجزاء.
uno-not-your-turn = إنه ليس دورك.
# Info
uno-no-top = لا توجد بطاقة أعلى حتى الآن.
uno-top-card = { $card }.
uno-color-is = { $color }.
uno-count-you = أنت { $count }
uno-count-player = { $player } { $count }
uno-deck-count = ظهر السفينة { $count }
uno-sorting-color = الفرز حسب اللون.
uno-sorting-number = الترتيب حسب الرقم.
# Round / game end
uno-round-winner = { $player } يفوز بالجولة!
uno-you-win-round = لقد فزت بالجولة!
uno-round-points-from = { $points } من { $player }
uno-round-points-from-you = { $points } منك
uno-round-points-from-with-interception = { $points } من { $player } ({ $hand_points } يد + { $penalty } عقوبة الاعتراض)
uno-round-points-from-you-with-interception = { $points } منك ({ $hand_points } يد + { $penalty } عقوبة اعتراض)
uno-round-details-none = لم يتم أخذ أي نقاط من المعارضين.
uno-round-summary = { $details }. { $player } مكاسب { $total }.
uno-round-summary-you = { $details }. تكسب { $total }.
uno-you-add-penalty-points = قمت بإضافة { $points } نقاط الجزاء إلى مجموع نقاطك لهذه الجولة.
uno-player-adds-penalty-points = { $player } يضيف { $points } نقاط الجزاء إلى مجموعهم لهذه الجولة.
uno-you-add-penalty-points-with-interception = قمت بإضافة { $points } نقاط الجزاء هي مجموع نقاطك لهذه الجولة ({ $hand_points } من يدك بالإضافة إلى { $penalty } عقوبة الاعتراض).
uno-player-adds-penalty-points-with-interception = { $player } يضيف { $points } نقاط الجزاء إلى مجموعهم في هذه الجولة ({ $hand_points } من أيديهم بالإضافة إلى { $penalty } عقوبة الاعتراض).
uno-you-are-eliminated = لقد وصلت إلى { $limit }-نقطة القضاء على الحد والخروج من اللعبة.
uno-player-is-eliminated = { $player } وصلت إلى { $limit }-نقطة القضاء على الحد والخروج من اللعبة.
uno-you-win-game =
    { $mode ->
        [elimination] أنت آخر لاعب متبقي وتفوز بـ { $score } نقاط الجزاء.
       *[first_to_limit] تفوز باللعبة مع { $score } نقاط!
    }
uno-player-wins-game =
    { $mode ->
        [elimination] { $player } هو آخر لاعب متبقي ويفوز به { $score } نقاط الجزاء.
       *[first_to_limit] { $player } يفوز بالمباراة مع { $score } نقاط!
    }
uno-game-tie = لقد تم القضاء على الجميع. اللعبة هي التعادل!
uno-line-format = { $rank }. { $player }: { $score }
uno-score-line-first = { $player }: { $score }/{ $target } نقاط.
uno-score-line-elimination = { $player }: { $score }/{ $target } نقاط الجزاء.
# Hand value (d key)
uno-read-hand-value =
    { $count ->
        [one] { $count } بطاقة
       *[other] { $count } بطاقات
    } يستحق { $points ->
        [one] { $points } نقطة
       *[other] { $points } النقاط
    }.
