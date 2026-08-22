game-round-start = جولة { $round }.
game-round-end = جولة { $round } مكتمل.
game-turn-start = إنه { $player }دور.
game-turn-start-you = لقد حان دورك.
game-turn-start-player = إنه { $player }دور.
game-no-turn = لا أحد بدوره الآن.
game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score }/{ $target } { $unit }
game-score-unit-points =
    { $count ->
        [one] نقطة
       *[other] النقاط
    }
game-score-unit-chips =
    { $count ->
        [one] شريحة
       *[other] شيبس
    }
game-score-unit-coins =
    { $count ->
        [one] عملة
       *[other] عملات معدنية
    }
game-score-unit-health = صحة
game-score-unit-ninetynine-tokens =
    { $count ->
        [one] رمز
       *[other] الرموز
    }
game-score-unit-tokens-home =
    { $count ->
        [one] رمز المنزل
       *[other] الرموز الرئيسية
    }
game-score-unit-pawns-home =
    { $count ->
        [one] رهن البيت
       *[other] بيادق الوطن
    }
game-score-unit-hand-wins =
    { $count ->
        [one] فوز يدوي
       *[other] فوز اليد
    }
game-score-unit-light = ضوء
game-final-scores-header = النتائج النهائية:
game-winner = { $player } يفوز!
game-winner-you = فزت!
game-winner-score = { $player } يفوز مع { $score } نقاط!
game-tiebreaker = إنها ربطة عنق! الجولة الفاصلة!
game-tiebreaker-players = إنها تعادل بين { $players }! الجولة الفاصلة!
game-eliminated = { $player } تم القضاء عليه مع { $score } نقاط.
game-set-target-score = النتيجة المستهدفة: { $score }
game-enter-target-score = أدخل النتيجة المستهدفة:
game-option-changed-target = تم ضبط النتيجة المستهدفة على { $score }.
game-set-team-mode = وضع الفريق: { $mode }
game-select-team-mode = اختر وضع الفريق
game-option-changed-team = تم ضبط وضع الفريق على { $mode }.
game-team-mode-individual = فردي
game-team-mode-x-teams-of-y = { $num_teams } فرق { $team_size }
game-team-name = فريق { $index }
team-arrangement-started = بدأ ترتيب الفريق. قم بمراجعة الفرق، وقم بتبديل الأعضاء إذا لزم الأمر، ثم أكد البدء.
team-arrangement-confirm = قم بتأكيد الفرق وابدأ
team-arrangement-read = قراءة الفرق
team-arrangement-select-member-action = اختر عضو الفريق
team-arrangement-select-member = اختر أحد أعضاء الفريق
team-arrangement-select-swap-target = حدد لاعبًا للتبديل معه
team-arrangement-swap-member = اختر هدف المبادلة
team-arrangement-swap-member-selected = مبادلة { $player } مع...
team-arrangement-cancel = إلغاء ترتيب الفريق
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = ترتيب الدوران: { $players }
team-arrangement-member-option = { $player }, { $team }, { $selected }
team-arrangement-selected = مختارة
team-arrangement-not-selected = لم يتم التحديد
team-arrangement-member-selected = { $player } من { $team } مختارة. اختر لاعبًا من فريق آخر للتبديل معه.
team-arrangement-swapped = { $first } و { $second } لقد تبادلت الفرق.
team-arrangement-cancelled = تم إلغاء ترتيب الفريق.
team-arrangement-cancelled-roster = تم إلغاء ترتيب الفريق بسبب تغير قائمة اللاعبين.
team-arrangement-refreshed = تغيرت قائمة اللاعبين. تم تحديث ترتيب الفريق.
team-arrangement-in-progress = قم بإنهاء أو إلغاء ترتيب الفريق أولاً.
team-arrangement-not-active = ترتيب الفريق غير نشط.
team-arrangement-select-first = حدد أحد أعضاء الفريق أولاً.
team-arrangement-player-missing = هذا اللاعب لم يعد متاحًا لترتيب الفريق.
team-arrangement-same-team = اختر شخصًا من فريق مختلف.
team-arrangement-swap-failed = لا يمكن تبديل أعضاء الفريق هؤلاء.
status-box-closed = معلومات الحالة مغلقة.
game-leave = ترك اللعبة
round-timer-paused = { $player } أوقفت اللعبة مؤقتًا (اضغط على p لبدء الجولة التالية).
round-timer-resumed = تم استئناف مؤقت الجولة.
round-timer-countdown = الجولة القادمة في { $seconds }...
dice-keeping = حفظ { $value }.
dice-rerolling = إعادة التدوير { $value }.
dice-locked = هذا القالب مغلق ولا يمكن تغييره.
dice-status-label-locked = { $value } (مقفل)
dice-status-label-kept = { $value } (محفوظ)
game-deal-counter = صفقة { $current }/{ $total }.
game-you-deal = أنت توزع البطاقات.
game-player-deals = { $player } يتعامل مع البطاقات.
card-name = { $rank } من { $suit }
no-cards = لا توجد بطاقات
suit-diamonds = الماس
suit-clubs = الأندية
suit-hearts = قلوب
suit-spades = البستوني
rank-ace = الآس
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = جاك
rank-queen = الملكة
rank-king = ملك
rank-ace-plural = ارسالا ساحقا
rank-two-plural = ثنائي
rank-three-plural = الثلاثات
rank-four-plural = أربع
rank-five-plural = الخمسات
rank-six-plural = الستات
rank-seven-plural = السبعات
rank-eight-plural = ثمانية
rank-nine-plural = تسعات
rank-ten-plural = عشرات
rank-jack-plural = الرافعات
rank-queen-plural = ملكات
rank-king-plural = ملوك
poker-high-card-with = { $high } عالية مع { $rest }
poker-high-card = { $high } عالية
poker-pair-with = زوج { $pair }مع { $rest }
poker-pair = زوج { $pair }
poker-two-pair-with = زوجان، { $high } و { $low }مع { $kicker }
poker-two-pair = زوجان، { $high } و { $low }
poker-trips-with = ثلاثة من نفس النوع, { $trips }مع { $rest }
poker-trips = ثلاثة من نفس النوع، { $trips }
poker-straight-high = { $high } ارتفاع مستقيم
poker-flush-high-with = { $high } تدفق عالي، مع { $rest }
poker-full-house = فول هاوس، { $trips } على { $pair }
poker-quads-with = أربعة من نفس النوع، { $quads }مع { $kicker }
poker-quads = أربعة من نفس النوع، { $quads }
poker-royal-flush = رويال فلوش
poker-straight-flush-high = { $high } ارتفاع مستقيم فلوش
poker-unknown-hand = يد مجهولة
game-error-invalid-team-mode = وضع الفريق المحدد غير صالح للعدد الحالي من اللاعبين.
documentation-menu = توثيق
introduction = مقدمة
community-rules = قواعد المجتمع
global-keys = الضوابط العالمية
game-rules = قواعد اللعبة
changelog = سجل التغيير
donation = هبة
contact = اتصل
document-not-found = لم يتم العثور على الوثيقة.
help = مساعدة
# Game Info (Ctrl+I)
game-info = معلومات اللعبة
game-info-header = معلومات اللعبة الحالية
game-info-name = لعبة: { $game }
game-info-players = اللاعبين: { $count }
game-info-host = المضيف: { $host }
game-info-status = الحالة: { $status }
game-info-status-waiting = الانتظار في الردهة
game-info-status-playing = قيد التنفيذ
game-info-options-header = الإعدادات:
game-info-no-options = لا تحتوي هذه اللعبة على خيارات تكوين مخصصة.
# How to Play (Ctrl+F1)
how-to-play = كيفية اللعب
game-rules-not-available = قواعد { $game } ليست متاحة بعد.
