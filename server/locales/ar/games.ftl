game-round-start = الجولة { $round }.
game-round-end = اكتملت الجولة { $round }.
game-turn-start = حان دور { $player }.
game-turn-start-you = حان دورك.
game-turn-start-player = حان دور { $player }.
game-no-turn = ليس دور أحد الآن.

game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score }/{ $target } { $unit }
game-score-unit-points = { $count ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
game-score-unit-chips = { $count ->
    [one] رقاقة
    [two] رقاقتان
    [few] رقاقات
    [many] رقاقة
   *[other] رقاقة
}
game-score-unit-coins = { $count ->
    [one] عملة
    [two] عملتان
    [few] عملات
    [many] عملة
   *[other] عملة
}
game-score-unit-health = صحة
game-score-unit-ninetynine-tokens = { $count ->
    [one] رمز
    [two] رمزان
    [few] رموز
    [many] رمزًا
   *[other] رمز
}
game-score-unit-tokens-home = { $count ->
    [one] رمز في البيت
    [two] رمزان في البيت
    [few] رموز في البيت
    [many] رمزًا في البيت
   *[other] رمز في البيت
}
game-score-unit-pawns-home = { $count ->
    [one] بيدق في البيت
    [two] بيدقان في البيت
    [few] بيادق في البيت
    [many] بيدقًا في البيت
   *[other] بيدق في البيت
}
game-score-unit-hand-wins = { $count ->
    [one] يد رابحة
    [two] يدان رابحتان
    [few] أيدٍ رابحة
    [many] يدًا رابحة
   *[other] يد رابحة
}
game-score-unit-light = ضوء
game-final-scores-header = النتائج النهائية:

game-winner = فاز { $player }!
game-winner-you = لقد فزت!
game-winner-score = فاز { $player } بـ { $score } نقطة!
game-tiebreaker = تعادل! جولة حسم!
game-eliminated = تم إقصاء { $player } بـ { $score } نقطة.

game-set-target-score = النتيجة المستهدفة: { $score }
game-enter-target-score = أدخل النتيجة المستهدفة:
game-option-changed-target = تم تعيين النتيجة المستهدفة إلى { $score }.

game-set-team-mode = وضع الفِرَق: { $mode }
game-select-team-mode = اختر وضع الفِرَق
game-option-changed-team = تم تعيين وضع الفِرَق إلى { $mode }.
game-team-mode-individual = فردي
game-team-mode-x-teams-of-y = { $num_teams } فِرَق من { $team_size }
game-team-name = الفريق { $index }
team-arrangement-started = بدأ ترتيب الفِرَق. راجع الفِرَق، وبدّل الأعضاء إذا لزم الأمر، ثم أكّد للبدء.
team-arrangement-confirm = تأكيد الفِرَق والبدء
team-arrangement-read = قراءة الفِرَق
team-arrangement-select-member-action = اختيار عضو فريق
team-arrangement-select-member = اختر عضو فريق
team-arrangement-select-swap-target = اختر لاعبًا للتبديل معه
team-arrangement-swap-member = اختر هدف التبديل
team-arrangement-swap-member-selected = بدّل { $player } مع...
team-arrangement-cancel = إلغاء ترتيب الفِرَق
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = ترتيب الأدوار: { $players }
team-arrangement-member-option = { $player }، { $team }، { $selected }
team-arrangement-selected = محدّد
team-arrangement-not-selected = غير محدّد
team-arrangement-member-selected = تم اختيار { $player } من { $team }. اختر لاعبًا من فريق آخر للتبديل معه.
team-arrangement-swapped = تبادل { $first } و{ $second } الفريقين.
team-arrangement-cancelled = تم إلغاء ترتيب الفِرَق.
team-arrangement-cancelled-roster = تم إلغاء ترتيب الفِرَق لأن قائمة اللاعبين تغيّرت.
team-arrangement-refreshed = تغيّرت قائمة اللاعبين. تم تحديث ترتيب الفِرَق.
team-arrangement-in-progress = أنهِ ترتيب الفِرَق أو ألغِه أولًا.
team-arrangement-not-active = ترتيب الفِرَق غير نشط.
team-arrangement-select-first = اختر عضو فريق أولًا.
team-arrangement-player-missing = لم يعد ذلك اللاعب متاحًا لترتيب الفِرَق.
team-arrangement-same-team = اختر شخصًا من فريق مختلف.
team-arrangement-swap-failed = تعذّر تبديل عضوَي الفريق هذين.
team-arrangement-swapped-player = بدّل { $player } موقعي { $first } و{ $second } بين الفريقين.
team-arrangement-swapped-you = بدّلت موقعي { $first } و{ $second } بين الفريقين.

status-box-closed = تم إغلاق معلومات الحالة.

game-leave = مغادرة اللعبة

round-timer-paused = أوقف { $player } اللعبة مؤقتًا (اضغط p لبدء الجولة التالية).
round-timer-paused-you = أوقفت اللعبة مؤقتًا (اضغط p لبدء الجولة التالية).
dice-keeping = الاحتفاظ بـ { $value }.
dice-rerolling = إعادة رمي { $value }.
dice-locked = هذا النرد مقفل ولا يمكن تغييره.
dice-status-label-locked = { $value } (مقفل)
dice-status-label-kept = { $value } (محتفَظ به)

game-deal-counter = التوزيع { $current }/{ $total }.
game-you-deal = أنت توزّع البطاقات.
game-player-deals = { $player } يوزّع البطاقات.

card-name = { $rank } { $suit }
no-cards = لا توجد بطاقات

suit-diamonds = الماس
suit-clubs = السباتي
suit-hearts = القلوب
suit-spades = البستوني

rank-ace = آس
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = ولد
rank-queen = ملكة
rank-king = ملك

rank-ace-plural = آسات
rank-two-plural = اثنينات
rank-three-plural = ثلاثات
rank-four-plural = أربعات
rank-five-plural = خمسات
rank-six-plural = ستات
rank-seven-plural = سبعات
rank-eight-plural = ثمانيات
rank-nine-plural = تسعات
rank-ten-plural = عشرات
rank-jack-plural = أولاد
rank-queen-plural = ملكات
rank-king-plural = ملوك


poker-high-card-with = أعلى ورقة { $high }، مع { $rest }
poker-high-card = أعلى ورقة { $high }
poker-pair-with = زوج من { $pair }، مع { $rest }
poker-pair = زوج من { $pair }
poker-two-pair-with = زوجان، { $high } و{ $low }، مع { $kicker }
poker-two-pair = زوجان، { $high } و{ $low }
poker-trips-with = ثلاثة متشابهة، { $trips }، مع { $rest }
poker-trips = ثلاثة متشابهة، { $trips }
poker-straight-high = ستريت أعلاه { $high }
poker-flush-high-with = فلاش أعلاه { $high }، مع { $rest }
poker-full-house = فُل هاوس، { $trips } فوق { $pair }
poker-quads-with = أربعة متشابهة، { $quads }، مع { $kicker }
poker-quads = أربعة متشابهة، { $quads }
poker-royal-flush = رويال فلاش
poker-straight-flush-high = ستريت فلاش أعلاه { $high }
poker-unknown-hand = يد غير معروفة

game-error-invalid-team-mode = وضع الفِرَق المختار غير صالح للعدد الحالي من اللاعبين.

documentation-menu = التوثيق
introduction = مقدمة
community-rules = قواعد المجتمع
global-keys = عناصر التحكم العامة
game-rules = قواعد اللعبة
changelog = سجل التغييرات
donation = التبرّع
contact = التواصل
document-not-found = لم يُعثر على المستند.
help = مساعدة

# Game Info (Ctrl+I)
game-info = معلومات اللعبة
game-info-header = معلومات اللعبة الحالية
game-info-name = اللعبة: {$game}
game-info-players = اللاعبون: {$count}
game-info-host = المضيف: {$host}
game-info-status = الحالة: {$status}
game-info-status-waiting = في انتظار الردهة
game-info-status-playing = قيد التقدّم
game-info-options-header = الإعدادات:
game-info-no-options = لا تحتوي هذه اللعبة على خيارات تهيئة مخصّصة.

# How to Play (Ctrl+F1)
how-to-play = كيفية اللعب
game-rules-not-available = قواعد {$game} غير متاحة بعد.
