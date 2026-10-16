game-name-bingo = بينجو

bingo-pattern-line = أي خط
bingo-pattern-four-corners = الزوايا الأربع
bingo-pattern-letter-x = حرف إكس
bingo-pattern-blackout = البطاقة الكاملة

bingo-call-interval-5 = 5 ثوانٍ
bingo-call-interval-15 = 15 ثانية
bingo-call-interval-30 = 30 ثانية
bingo-call-interval-45 = 45 ثانية
bingo-call-interval-60 = 60 ثانية

bingo-set-pattern = النمط الفائز: { $pattern }
bingo-select-pattern = اختر النمط الفائز:
bingo-option-changed-pattern = أصبح النمط الفائز الآن { $pattern }.
bingo-desc-pattern = الشكل اللازم للفوز. "أي خط" يعني صفًا أو عمودًا أو قطرًا كاملًا. "الزوايا الأربع" تتطلب جميع مربعات الزوايا الأربعة. "حرف إكس" يتطلب كلا القطرين. "البطاقة الكاملة" تتطلب البطاقة بأكملها.

bingo-set-call-interval = وتيرة النداء: { $seconds }
bingo-select-call-interval = اختر وتيرة النداء:
bingo-option-changed-interval = أصبحت وتيرة النداء المستهدفة الآن { $seconds }.
bingo-desc-call-interval = الوقت المستهدف من رقم معلَن إلى الرقم التالي. تترك اللعبة دائمًا نافذة قصيرة لإعلان بينجو، لذا قد تستغرق أسرع وتيرة وقتًا أطول قليلًا.

bingo-cell-free = المركز الحر، مُعلَّم تلقائيًا.
bingo-cell-marked = { $letter } { $number }، مُعلَّم.
bingo-cell-unmarked = { $letter } { $number }، غير مُعلَّم.
bingo-cell-is-free = المركز الحر مُعلَّم بالفعل.
bingo-you-already-won = لديك بينجو بالفعل في هذه الجولة.

bingo-you-mark = تم تعليم { $letter } { $number }.
bingo-you-unmark = تم إلغاء تعليم { $letter } { $number }.

bingo-claim-bingo = أعلن بينجو!
bingo-repeat-call = كرّر الرقم الأخير
bingo-check-called = عرض الأرقام المنادى عليها
bingo-no-calls-yet = لم يُنادَ على أي أرقام بعد.
bingo-claim-in-progress = يجري التحقق من إعلان بينجو آخر. حاول مرة أخرى بعد لحظة.
bingo-claim-in-progress-you = يجري التحقق من إعلان بينجو الخاص بك بالفعل.
bingo-claim-wait-for-call = انتظر حتى يُعلَن الرقم الجاري سحبه، ثم حاول مرة أخرى.
bingo-claim-unchanged = لم تتغيّر بطاقتك منذ آخر فحص غير ناجح. غيّر علامة أو انتظر الرقم التالي قبل إعلان بينجو مرة أخرى.
bingo-checking-claim-you = تعلن بينجو! جارٍ التحقق من بطاقتك...
bingo-checking-claim = { $player } يعلن بينجو! جارٍ التحقق من البطاقة...
bingo-whose-turn-checking = جارٍ التحقق من بطاقة { $player }...
bingo-whose-turn-checking-you = جارٍ التحقق من بطاقتك...
bingo-whose-turn-checking-card = جارٍ التحقق من بطاقة بينجو...
bingo-whose-turn-drawing = جارٍ سحب الرقم التالي...
bingo-whose-turn-waiting = { $seconds ->
    [one] الرقم التالي بعد ثانية واحدة.
    [two] الرقم التالي بعد ثانيتين.
    [few] الرقم التالي بعد { $seconds } ثوانٍ.
    [many] الرقم التالي بعد { $seconds } ثانية.
   *[other] الرقم التالي بعد { $seconds } ثانية.
}
bingo-claim-incorrect-you = بطاقتك لا تحتوي على بينجو صالح بعد.
bingo-claim-incorrect = بطاقة { $player } لا تحتوي على بينجو صالح بعد.
bingo-claim-incomplete-you = بطاقتك لا تكمل النمط الفائز بعد.
bingo-claim-incomplete = بطاقة { $player } لا تكمل النمط الفائز بعد.
bingo-marked-number-not-called = لقد علّمت { $letter } { $number }، لكن لم يُنادَ على هذا الرقم بعد.

bingo-last-call = الرقم الأخير: { $letter } { $number }

bingo-status-called-count = تم النداء على { $count } من { $total } رقمًا.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = تبدأ لعبة بينجو! النمط الفائز هو { $pattern }. تتبع الأرقام وتيرة مستهدفة واحدة كل { $interval } ثانية، مع وقت متبقٍ بعد كل نداء لإعلان بينجو. علّم بطاقتك، ثم اضغط B عندما تكون جاهزًا.
bingo-game-start-touch = تبدأ لعبة بينجو! النمط الفائز هو { $pattern }. تتبع الأرقام وتيرة مستهدفة واحدة كل { $interval } ثانية، مع وقت متبقٍ بعد كل نداء لإعلان بينجو. علّم بطاقتك، ثم استخدم إيماءة الضغط المطوّل على البطاقة في جهازك أو اختر "أعلن بينجو".
bingo-game-start-spectator = تبدأ لعبة بينجو! النمط الفائز هو { $pattern }. تتبع الأرقام وتيرة مستهدفة واحدة كل { $interval } ثانية، مع وقت متبقٍ بعد كل نداء ليعلن اللاعبون بينجو.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = بينجو! تفوز بـ { $numbers }!
bingo-claim-correct = بينجو! { $player } يفوز بـ { $numbers }!
bingo-claim-correct-no-numbers-you = بينجو! أنت تفوز!
bingo-claim-correct-no-numbers = بينجو! { $player } يفوز!
bingo-deck-exhausted = تم النداء على جميع الأرقام الخمسة والسبعين، ولم يعلن أحد بينجو صالحًا. تنتهي الجولة دون فائز.

bingo-error-invalid-interval = "{ $value }" ليست وتيرة نداء صالحة.
bingo-error-invalid-pattern = { $value } ليس نمطًا فائزًا معروفًا.

bingo-end-calls = { $count ->
    [one] تم النداء على رقم واحد في هذه الجولة.
    [two] تم النداء على رقمين في هذه الجولة.
    [few] تم النداء على { $count } أرقام في هذه الجولة.
    [many] تم النداء على { $count } رقمًا في هذه الجولة.
   *[other] تم النداء على { $count } رقم في هذه الجولة.
}
bingo-end-winner-line = الفائز: { $player }
bingo-end-no-winner = لم يعلن أحد بينجو صالحًا في هذه الجولة.
