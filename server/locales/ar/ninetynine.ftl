game-name-ninetynine = تسعة وتسعون
ninetynine-round = الجولة { $round }.

ninetynine-you-play = تلعب { $card }. المجموع الآن { $count }.
ninetynine-player-plays = يلعب { $player } { $card }. المجموع الآن { $count }.

ninetynine-direction-reverses = ينعكس اتجاه اللعب!

ninetynine-you-skipped = تم تخطّي دورك.
ninetynine-player-skipped = تم تخطّي { $player }.

n99-card-plus-10 = ‎+10
n99-card-minus-10 = ‎-10
n99-card-pass = تمرير
n99-card-reverse = عكس
n99-card-skip = تخطّي
n99-card-ninety-nine = تسعة وتسعون

ninetynine-you-lose-tokens = تخسر { $amount } { $amount ->
    [one] رمز
    [two] رمزين
    [few] رموز
    [many] رمزًا
    *[other] رمز
}.
ninetynine-player-loses-tokens = يخسر { $player } { $amount } { $amount ->
    [one] رمز
    [two] رمزين
    [few] رموز
    [many] رمزًا
    *[other] رمز
}.

ninetynine-you-eliminated = لقد تم إقصاؤك!
ninetynine-player-eliminated = تم إقصاء { $player }!

ninetynine-you-win = أنت تفوز باللعبة!
ninetynine-player-wins = يفوز { $player } باللعبة!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] رمز
    [two] رمزين
    [few] رموز
    [many] رمزًا
   *[other] رمز
}

ninetynine-you-draw = تسحب { $card }.
ninetynine-player-draws = يسحب { $player } بطاقة.

ninetynine-you-no-valid-cards = ليست لديك أي بطاقات لا تتجاوز 99!
ninetynine-player-no-valid-cards = ليست لدى { $player } أي بطاقات لا تتجاوز 99!
ninetynine-no-valid-cards = ليست لدى { $player } أي بطاقات لا تتجاوز 99!

ninetynine-current-count = المجموع هو { $count }.
ninetynine-next-round-wait = ستبدأ الجولة التالية خلال { $seconds } ثانية.

ninetynine-ace-choice = هل تلعب الآس كـ ‎+1 أم ‎+11؟
ninetynine-ace-add-eleven = إضافة 11
ninetynine-ace-add-one = إضافة 1

ninetynine-ten-choice = هل تلعب الـ 10 كـ ‎+10 أم ‎-10؟
ninetynine-ten-add = إضافة 10
ninetynine-ten-subtract = طرح 10
ninetynine-select-card-choice = اختر طريقة لعب هذه البطاقة.
ninetynine-choice-1 = الخيار 1
ninetynine-choice-2 = الخيار 2

ninetynine-draw-card = سحب بطاقة
ninetynine-draw-prompt = من فضلك اسحب بطاقة.
ninetynine-no-card-to-draw = لا توجد بطاقة متاحة للسحب. تابع بيدك الحالية.

ninetynine-set-tokens = الرموز الابتدائية: { $tokens }
ninetynine-enter-tokens = أدخل عدد الرموز الابتدائية:
ninetynine-option-changed-tokens = تم ضبط الرموز الابتدائية على { $tokens }.
ninetynine-desc-starting-tokens = عدد رموز النجاة التي يبدأ بها كل لاعب في تسعة وتسعين. يُقصى اللاعب بعد خسارة جميع رموزه (الافتراضي 9، النطاق 1-50).
ninetynine-set-rules = نسخة القواعد: { $rules }
ninetynine-select-rules = اختر نسخة القواعد
ninetynine-option-changed-rules = تم ضبط نسخة القواعد على { $rules }.
ninetynine-desc-rules-variant = يختار مجموعة أوراق تسعة وتسعين القياسية المكونة من 52 بطاقة أو مجموعة بطاقات الحركة الخاصة.
ninetynine-set-hand-size = حجم اليد: { $size }
ninetynine-enter-hand-size = أدخل حجم اليد:
ninetynine-option-changed-hand-size = تم ضبط حجم اليد على { $size }.
ninetynine-desc-hand-size = عدد البطاقات التي تُوزّع لكل لاعب في بداية كل جولة من تسعة وتسعين (الافتراضي 3، النطاق 1-13).
ninetynine-set-autodraw = السحب التلقائي: { $enabled }
ninetynine-option-changed-autodraw = تم ضبط السحب التلقائي على { $enabled }.
ninetynine-desc-autodraw = عند التفعيل، يسحب اللاعبون بطاقة بديلة تلقائيًا بعد اللعب. وعند الإيقاف، يجب على اللاعبين السحب يدويًا.

ninetynine-rules-action-cards = قواعد بطاقات الحركة.

ninetynine-rules-variant-standard = قياسي
ninetynine-rules-variant-action-cards = بطاقات الحركة

ninetynine-choose-first = عليك أن تختار أولًا.
ninetynine-round-transition-waiting = في انتظار بدء الجولة التالية.
ninetynine-pause-timer = إيقاف المؤقّت مؤقتًا
ninetynine-timer-not-active = مؤقّت الجولة غير نشط.
ninetynine-error-too-many-cards = عدد البطاقات المطلوب أكثر من اللازم: { $players } لاعب × { $hand_size } بطاقة يتجاوز مجموعة الأوراق المكونة من { $deck_size } بطاقة.
ninetynine-check-count = التحقق من المجموع
