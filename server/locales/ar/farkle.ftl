game-name-farkle = فركل
farkle-roll =
    لفة { $count } { $count ->
        [one] يموت
       *[other] النرد
    }
farkle-bank = بنك { $points } النقاط
farkle-take-single-one = مفردة 1 لـ { $points } النقاط
farkle-take-single-five = مفردة 5 لـ { $points } النقاط
farkle-take-three-kind = ثلاثة { $number }لـ { $points } النقاط
farkle-take-four-kind = أربعة { $number }لـ { $points } النقاط
farkle-take-five-kind = خمسة { $number }لـ { $points } النقاط
farkle-take-six-kind = ستة { $number }لـ { $points } النقاط
farkle-take-small-straight = صغير على التوالي ل { $points } النقاط
farkle-take-large-straight = كبير على التوالي ل { $points } النقاط
farkle-take-three-pairs = ثلاثة أزواج لـ { $points } النقاط
farkle-take-double-triplets = ثلاثة توائم مزدوجة لـ { $points } النقاط
farkle-take-full-house = أربعة من نفس النوع مع زوج لـ { $points } النقاط
farkle-you-roll =
    أنت تتدحرج { $count } { $count ->
        [one] يموت
       *[other] النرد
    }.
farkle-player-rolls =
    { $player } لفات { $count } { $count ->
        [one] يموت
       *[other] النرد
    }.
farkle-you-roll-brief = أنت تتدحرج { $count }.
farkle-player-rolls-brief = { $player } لفات { $count }.
farkle-roll-result = عرض النرد: { $dice }.
farkle-roll-result-brief = النرد: { $dice }.
farkle-you-farkle = فاركل! تخسر { $points } نقاط الانعطاف.
farkle-player-farkles = فاركل! { $player } يخسر { $points } نقاط الانعطاف.
farkle-you-farkle-brief = فركل : تخسر { $points }.
farkle-player-farkles-brief = فركل : { $player } يخسر { $points }.
farkle-you-take-combo = احتفظ { $combo } ل { $points } نقاط.
farkle-player-takes-combo = { $player } يبقي { $combo } ل { $points } نقاط.
farkle-you-take-combo-brief = أنت: { $combo }, +{ $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }, +{ $points }.
farkle-you-hot-dice = النرد الساخن! لقد سجلت جميع أحجار النرد الستة ويمكنك رمي النرد الستة مرة أخرى.
farkle-player-hot-dice = النرد الساخن! { $player } سجل كل النرد الستة ويمكنه رمي النرد الستة مرة أخرى.
farkle-you-hot-dice-brief = أنت: النرد الساخن.
farkle-player-hot-dice-brief = { $player }: النرد الساخن.
farkle-you-bank = أنت البنك { $points } نقاط. مجموعك الآن { $total }.
farkle-player-banks = { $player } البنوك { $points } نقطة ليصبح المجموع { $total }.
farkle-you-bank-brief = أنت البنك { $points }; المجموع { $total }.
farkle-player-banks-brief = { $player } البنوك { $points }; المجموع { $total }.
farkle-you-win = تربح مع { $score } نقاط!
farkle-winner = { $player } يفوز مع { $score } نقاط!
farkle-you-win-brief = لقد فزت: { $score }.
farkle-winner-brief = { $player } الانتصارات: { $score }.
farkle-winners-tie = التعادل في الهدف! لاعبو الشوط الفاصل: { $players }.
farkle-tiebreaker-round-start = الجولة الفاصلة { $round }. ما زال ينافس: { $players }.
farkle-your-turn-score = لديك { $points } نقاط في هذا المنعطف.
farkle-turn-score = { $player } لديه { $points } نقاط في هذا المنعطف.
farkle-no-turn = لا أحد يأخذ دوره حاليا.
farkle-set-target-score = النتيجة المستهدفة: { $score }
farkle-enter-target-score = أدخل النتيجة المستهدفة (500-5000):
farkle-option-changed-target = تم ضبط النتيجة المستهدفة على { $score }.
farkle-desc-target-score = النتيجة المطلوبة لبدء دورة Farkle النهائية وربما الفوز (الافتراضي 1000، النطاق 500-5000).
farkle-set-entrance-score = الحد الأدنى لدرجة القبول: { $score }
farkle-enter-entrance-score = أدخل الحد الأدنى لدرجة القبول (0-5000):
farkle-option-changed-entrance = تم ضبط الحد الأدنى لدرجة القبول على { $score }.
farkle-desc-min-entrance-score = الحد الأدنى من نقاط الدور المطلوبة لتحصيل النقاط الأولى للاعب. لا يمكن أن يكون أعلى من النتيجة المستهدفة (الافتراضي 50، النطاق 0-5000).
farkle-set-bank-score = الحد الأدنى لدرجة البنك: { $score }
farkle-enter-bank-score = أدخل الحد الأدنى من نقاط البنك (0-5000):
farkle-option-changed-bank = تم تعيين الحد الأدنى لدرجة البنك على { $score }.
farkle-desc-min-bank-score = الحد الأدنى من نقاط الدور المطلوبة قبل أن يصبح البنك متاحًا بعد أن يكون اللاعب موجودًا بالفعل على اللوحة. لا يمكن أن يكون أعلى من النتيجة المستهدفة (الافتراضي 30، النطاق 0-5000).
farkle-error-entrance-above-target = لا يمكن أن يكون الحد الأدنى لدرجة القبول ({ $entrance }) أعلى من الدرجة المستهدفة ({ $target }).
farkle-error-bank-above-target = لا يمكن أن يكون الحد الأدنى لدرجة البنك ({ $bank }) أعلى من الدرجة المستهدفة ({ $target }).
farkle-must-take-combo = يجب عليك الاحتفاظ بنرد أو مجموعة واحدة على الأقل من النرد قبل التدحرج مرة أخرى.
farkle-cannot-bank = لا يمكنك إجراء المعاملات البنكية إلا بعد الاحتفاظ بنرد التسجيل أو المجموعة في هذا الدور.
farkle-must-reach-entrance-score = تحتاج على الأقل { $points } قم بتحويل النقاط قبل الحصول على نتيجتك الأولى.
farkle-must-reach-bank-score = تحتاج على الأقل { $points } نقاط التحول قبل الخدمات المصرفية.
farkle-confirm-risky-roll = يمكنك البنك { $points } النقاط الآن. إن التدحرج مرة أخرى يخاطر بفقدانها. كرر لفة داخل { $seconds } ثواني للتأكيد.
farkle-invalid-combo-action = لم يتم التعرف على خيار التسجيل هذا. الرجاء اختيار إحدى المجموعات المدرجة حاليًا.
farkle-combo-no-longer-available = لم تعد مجموعة التسجيل هذه متاحة. تم تحديث خيارات التسجيل الحالية.
farkle-combo-single-1 = مفردة 1
farkle-combo-single-5 = فردي 5
farkle-combo-three-kind = ثلاثة { $number }ق
farkle-combo-four-kind = أربعة { $number }ق
farkle-combo-five-kind = خمسة { $number }ق
farkle-combo-six-kind = ستة { $number }ق
farkle-combo-small-straight = صغير على التوالي
farkle-combo-large-straight = كبير مستقيم
farkle-combo-three-pairs = ثلاثة أزواج
farkle-combo-double-triplets = ثلاثي مزدوج
farkle-combo-full-house = أربعة من نفس النوع مع زوج
farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } ل { $points } النقاط
farkle-check-turn-score = تحقق من نتيجة الدور
farkle-roll-label = لفة النرد
farkle-bank-label = نقاط البنك
