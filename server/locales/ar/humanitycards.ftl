# Humanity Cards - English localization

game-name-humanitycards = بطاقات ضد الإنسانية
# Options
hc-set-winning-score = نتيجة الفوز: { $score }
hc-enter-winning-score = أدخل النتيجة الفائزة:
hc-option-changed-winning-score = تم تعيين نتيجة الفوز على { $score }.
hc-desc-winning-score = عدد البطاقات الفائزة التي يحتاج اللاعب إلى جمعها للفوز بالمباراة (الافتراضي 7، النطاق 3-20).
hc-set-hand-size = حجم اليد: { $count }
hc-enter-hand-size = أدخل حجم اليد:
hc-option-changed-hand-size = تم ضبط حجم اليد على { $count }.
hc-desc-hand-size = كم عدد بطاقات الإجابة التي يحملها كل لاعب بعد كل إعادة تعبئة. توفر الأيدي الأكبر حجمًا المزيد من الخيارات ولكن تجعل الجولات تستغرق وقتًا أطول (الافتراضي 10، النطاق 5-15).
hc-set-card-packs = حزم البطاقات ({ $count } من { $total } مختارة)
hc-option-changed-card-packs = تم تغيير اختيار حزمة البطاقة.
hc-desc-card-packs = اختر الإجابة والحزم السريعة التي سيتم تبديلها في اللعبة. يجب أن تظل حزمة واحدة على الأقل محددة.
hc-set-czar-selection = اختيار بطاقة القيصر: { $mode }
hc-select-czar-selection = حدد وضع اختيار بطاقة القيصر
hc-option-changed-czar-selection = تم ضبط تحديد بطاقة القيصر على { $mode }.
hc-desc-czar-selection = التحكم في من يحكم كل جولة: التناوب حسب ترتيب الجلوس، أو الاختيار العشوائي، أو الفائز بالجولة الأخيرة.
hc-set-num-judges = عدد الحكام: { $count }
hc-enter-num-judges = أدخل عدد المحكمين:
hc-option-changed-num-judges = تم ضبط عدد الحكام على { $count }.
hc-desc-num-judges = كم عدد قياصرة البطاقات الذين يحكمون في كل جولة. يجب أن يكون العدد أقل من عدد اللاعبين حتى يتمكن شخص واحد على الأقل من غير الحكم من التقديم؛ مع وجود عدة حكام، يمكن لأي قاض اختيار الفائز (الافتراضي 1، النطاق 1-3).
hc-czar-rotating = الدورية
hc-czar-random = عشوائي
hc-czar-winner = الفائز الأخير
# Game flow
hc-game-starting = خلط الطوابق...
hc-dealing-cards = التعامل { $count } بطاقات لكل لاعب.
hc-round-start = جولة { $round }.
# Judge announcement
hc-judge-is =
    { $judges } { $count ->
        [1] هو قيصر البطاقة
       *[other] هم قياصرة البطاقة
    }.
hc-you-are-judge = أنت قيصر البطاقة في هذه الجولة.
hc-you-and-others-are-judges = أنت و { $judges } هم قياصرة البطاقة في هذه الجولة.
hc-you-are-not-judge = أنت لست "قيصر البطاقة" في هذه الجولة.
# Black card
hc-black-card = الموجه هو: { $text }
hc-black-card-pick = اختر { $count }.
hc-view-black-card = عرض بطاقة الأسئلة
# Submission phase
hc-select-cards =
    حدد { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } من يدك.
hc-card-selected = { $text }، تم التحديد
hc-card-not-selected = { $text }
hc-submit-cards = إرسال ({ $selected } من { $required } المحدد)
hc-submission-progress = { $submitted } من { $total } تم تقديم اللاعبين.
hc-waiting-for-submissions = في انتظار التقديمات...
hc-already-submitted = لقد قدمت بالفعل بطاقاتك.
hc-you-submitted = لقد قدمت بطاقاتك.
hc-player-submitted = { $player } قدموا بطاقاتهم.
hc-judge-cannot-submit = أنت مسؤول البطاقات في هذه الجولة، لذا لا يمكنك إرسال إجابة.
hc-not-submission-phase = يمكنك فقط تحديد وإرسال البطاقات البيضاء خلال مرحلة التقديم.
hc-card-not-in-hand = فتحة البطاقة هذه ليست في يدك.
hc-judge-has-no-submission = ليس لدى Card Czar إرسال لمعاينة هذه الجولة.
hc-no-submission-active = لا يوجد إرسال نشط للمعاينة الآن.
hc-wrong-card-count =
    تحتاج إلى تحديد { $count } { $count ->
        [one] بالضبط بطاقة
       *[other] بطاقات
    }.
# Judging phase
hc-judging-start = جميع البطاقات موجودة! الوقت للحكم.
hc-choose-best-card = اختر البطاقة الأفضل
hc-choose-best-card-for = اختر أفضل بطاقة تطابق: { $prompt }
hc-select-winner-prompt = اختر التقديم الفائز
hc-card-number = بطاقة { $number }
hc-submission-number = تقديم { $number }
hc-submission-option = { $text }
hc-only-judges-pick = يمكن لقائد البطاقة فقط اختيار التقديم الفائز.
hc-not-judging-phase = يمكنك فقط اختيار العرض الفائز خلال مرحلة التحكيم.
hc-submission-not-available = هذا الإرسال لم يعد متاحا.
# Results
hc-you-win-round = لقد فزت بالجولة! درجاتك الآن { $score }.
hc-player-wins-round = { $player } يفوز بالجولة! نتيجة: { $score }.
hc-round-scores = النتائج بعد الجولة { $round }:
hc-score-line =
    { $player }: { $score } { $score ->
        [one] نقطة
       *[other] النقاط
    }
hc-final-score-line =
    { $rank }. { $player }: { $score } { $score ->
        [one] نقطة
       *[other] النقاط
    }
hc-all-submissions = التقديمات الأخرى:
hc-your-winning-answer = إجابتك الفائزة: { $text }
hc-winning-answer-player = { $player }الإجابة الفائزة: { $text }
hc-your-other-submission = إرسالك الآخر: { $text }
hc-other-submission-player = { $player }: { $text }
# View
hc-preview-submission = معاينة التقديم الخاص بك
hc-view-submission = عرض التقديم الخاص بك
hc-preview-submission-text = معاينة: { $text }
hc-your-submission = تقديمك: { $text }
hc-select-cards-first = حدد بطاقة واحدة على الأقل أولاً.
# Win
hc-game-winner = { $player } يفوز مع { $score } نقاط!
hc-you-win = تربح مع { $score } نقاط!
hc-english-content-note = ملاحظة: نص بطاقة الأسئلة والأجوبة يدعم حاليًا اللغة الإنجليزية فقط.
# Deck management
hc-deck-reshuffled = تم إعادة خلط كومة تجاهل البطاقة البيضاء في المجموعة.
hc-black-deck-reshuffled = تم إعادة خلط كومة تجاهل البطاقة السوداء في المجموعة.
hc-not-enough-cards = لا توجد بطاقات كافية. حاول تمكين المزيد من الحزم.
hc-error-too-many-judges = { $judges } يتطلب القضاة على الأقل { $required } اللاعبين، ولكن هذا الجدول لديه { $players }. قم بتقليل عدد الحكام أو إضافة المزيد من اللاعبين.
hc-error-no-valid-packs = لم يتم تحديد أي حزم بطاقات صالحة. حدد حزمة واحدة على الأقل قبل البدء.
hc-error-no-black-cards = لا تحتوي حزم البطاقات المحددة على أي بطاقات مطالبة سوداء. حدد حزمة أخرى قبل البدء.
hc-error-not-enough-white-cards = { $players } لاعبين بحجم يد { $hand_size } بحاجة على الأقل { $needed } البطاقات البيضاء، لكن الحزم المحددة توفر فقط { $available }. تمكين المزيد من الحزم أو تقليل حجم اليد.
hc-error-pick-exceeds-hand-size = تتضمن الحزم المحددة موجهًا يتطلب { $pick } الإجابات، ولكن حجم اليد هو فقط { $hand_size }. زيادة حجم اليد أو اختيار حزم مختلفة.
# Hand management
hc-view-hand = عرض اليد
hc-toggle-card-keybind = تبديل البطاقة { $number }
hc-submit-cards-keybind = إرسال البطاقات
# Scores
hc-view-scores = عرض النتائج
hc-no-scores = لا توجد نتائج حتى الآن.
# Whose turn / whose judge
hc-whose-judge = من يحكم
hc-waiting-for = في انتظار { $names } لتقديم.
hc-all-submitted-waiting-judge = لقد قدم جميع اللاعبين. في انتظار { $judge } للحكم.
