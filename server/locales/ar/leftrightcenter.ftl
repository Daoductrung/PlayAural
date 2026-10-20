game-name-leftrightcenter = يسار وسط يمين

lrc-roll = ارمِ { $count } { $count ->
    [one] نردة
   *[other] نرد
}
lrc-roll-label = ارمِ النرد

lrc-face-left = يسار
lrc-face-center = وسط
lrc-face-right = يمين
lrc-face-dot = نقطة

lrc-you-roll = ترمي { $results }.
lrc-player-rolls = { $player } يرمي { $results }.
lrc-you-roll-brief = أنت: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = تمرّر { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} يسارًا إلى { $target }. تبقّى لديك { $remaining }؛ لدى { $target } الآن { $target_total }.
lrc-player-passes-left = { $player } يمرّر { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} يسارًا إلى { $target }. تبقّى لدى { $player } { $remaining }؛ لدى { $target } الآن { $target_total }.
lrc-you-pass-left-brief = أنت، يسارًا إلى { $target }: { $count }. المتبقي: { $remaining }.
lrc-player-passes-left-brief = { $player }، يسارًا إلى { $target }: { $count }. المتبقي: { $remaining }.

lrc-you-pass-right = تمرّر { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} يمينًا إلى { $target }. تبقّى لديك { $remaining }؛ لدى { $target } الآن { $target_total }.
lrc-player-passes-right = { $player } يمرّر { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} يمينًا إلى { $target }. تبقّى لدى { $player } { $remaining }؛ لدى { $target } الآن { $target_total }.
lrc-you-pass-right-brief = أنت، يمينًا إلى { $target }: { $count }. المتبقي: { $remaining }.
lrc-player-passes-right-brief = { $player }، يمينًا إلى { $target }: { $count }. المتبقي: { $remaining }.

lrc-you-pass-center = تضع { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} في الوسط. تبقّى لديك { $remaining }؛ يحمل الوسط الآن { $center }.
lrc-player-passes-center = { $player } يضع { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} في الوسط. تبقّى لدى { $player } { $remaining }؛ يحمل الوسط الآن { $center }.
lrc-you-pass-center-brief = أنت، الوسط: { $count }. المتبقي: { $remaining }. إجمالي الوسط: { $center }.
lrc-player-passes-center-brief = { $player }، الوسط: { $count }. المتبقي: { $remaining }. إجمالي الوسط: { $center }.

lrc-you-keep-all = كل نردك نقاط، لذا تحتفظ بكل الـ { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
}.
lrc-player-keeps-all = كل نرد { $player } نقاط، لذا { GENDER_TERM($player_gender, "subject-have") } كل الـ { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
} متبقية.
lrc-you-keep-all-brief = أنت: بلا تمرير؛ { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
}.
lrc-player-keeps-all-brief = { $player }: بلا تمرير؛ { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
}.

lrc-you-skip-no-chips = ليس لديك رقاقات، لذا يُتخطّى دورك. تبقى في اللعبة ويمكنك تلقّي الرقاقات من أي من الجارين.
lrc-player-skips-no-chips = ليس لدى { $player } رقاقات، لذا يُتخطّى الدور { GENDER_TERM($player_gender, "possessive-determiner") }. { GENDER_TERM($player_gender, "subject-be-capitalized") } لا يزال في اللعبة ويمكنه تلقّي الرقاقات من أي من الجارين.
lrc-you-skip-no-chips-brief = أنت: بلا رقاقات؛ تم تخطّي الدور.
lrc-player-skips-no-chips-brief = { $player }: بلا رقاقات؛ تم تخطّي الدور.

lrc-you-win = أنت آخر لاعب يملك رقاقات وتفوز مع تبقّي { $count }. تطالب بالـ { $center } { $center ->
    [one] رقاقة
   *[other] رقاقات
} الموجودة في الوسط.
lrc-player-wins = { $player } آخر لاعب يملك رقاقات ويفوز مع تبقّي { $count }. وتُمنح { GENDER_TERM($player_gender, "object") } الـ { $center } { $center ->
    [one] رقاقة
   *[other] رقاقات
} الموجودة في الوسط.
lrc-you-win-brief = تفوز. رقاقاتك: { $count }. الوسط: { $center }.
lrc-player-wins-brief = { $player } يفوز. الرقاقات: { $count }. الوسط: { $center }.

lrc-roll-already-resolving = رميتك قيد التسوية بالفعل. انتظر انتهاء تمرير الرقاقات.
lrc-no-chips-to-roll = ليس لديك رقاقات لرميها. سيُتخطّى دورك تلقائيًا.

lrc-center-pot = وعاء الوسط: { $count } { $count ->
    [one] رقاقة
   *[other] رقاقات
}.
lrc-check-center = التحقق من وعاء الوسط
lrc-check-last-roll = التحقق من آخر رمية
lrc-last-roll-none = لم يُرمَ أي نرد بعد.
lrc-last-roll-you = كانت آخر رمية لك { $results }.
lrc-last-roll-player = { $player } رمى آخر مرة { $results }.

lrc-set-starting-chips = الرقاقات الابتدائية: { $count }
lrc-enter-starting-chips = أدخل الرقاقات الابتدائية:
lrc-option-changed-starting-chips = تم ضبط الرقاقات الابتدائية على { $count }.
leftrightcenter-desc-starting-chips = عدد الرقاقات التي يبدأ بها كل لاعب في يسار وسط يمين (الافتراضي 3، النطاق 1-10).
lrc-error-starting-chips-invalid = يجب أن تكون الرقاقات الابتدائية بين { $min } و { $max }؛ القيمة الحالية { $count }.

lrc-line-format = { $player }: { $chips } { $chips ->
    [one] رقاقة
   *[other] رقاقات
}
