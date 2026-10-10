game-name-zombiedice = نرد الزومبي

zombiedice-set-target-score = الأدمغة اللازمة للفوز: { $score }
zombiedice-enter-target-score = أدخل هدف الفوز من 5 إلى 50 دماغًا:
zombiedice-option-changed-target-score = أصبح هدف الفوز الآن { $score } دماغًا.
zombiedice-desc-target-score = الوصول إلى هذه النتيجة يبدأ الجولة الأخيرة لأي لاعبين ما زالوا ينتظرون دورهم. الهدف الرسمي هو 13 دماغًا؛ والأهداف الأقل أو الأعلى تجعل المباراة أقصر أو أطول.

zombiedice-roll-first = ارمِ 3 أحجار نرد
zombiedice-roll-first-description = اسحب ثلاثة أحجار نرد مخفية من الكوب وارمِها.
zombiedice-roll-again = ارمِ مجددًا — { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
} على المحكّ
zombiedice-roll-again-description = أعد رمي أحجار الخطوات وعددها { $footprints }، واسحب { $draw } من الأحجار الجديدة لتصبح ثلاثة. الطلقة الثالثة تمحو كل الأدمغة غير المودعة وعددها { $brains }.
zombiedice-bank = توقّف وسجّل { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}
zombiedice-bank-keybind = توقّف وسجّل
zombiedice-bank-description = أنهِ دورك وأودِع { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.
zombiedice-check-turn-totals = فحص مجاميع الدور
zombiedice-check-turn-totals-description = استمع إلى الأدمغة والطلقات والخطوات الحالية.
zombiedice-review-turn = مراجعة الدور الحالي
zombiedice-review-turn-description = راجع كل حجر نرد علني وعدد الكوب وآخر رمية والأدمغة غير المودعة.
zombiedice-review-table = مراجعة الطاولة
zombiedice-review-table-description = راجع الهدف ومرحلة المباراة وترتيب الأدوار والدور الحالي والنتائج.

zombiedice-game-start = تبدأ لعبة نرد الزومبي. الهدف: { $target } دماغًا. { $first } يبدأ أولًا. الترتيب: { $order }.
zombiedice-your-turn = دورك. المُودَع: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}. ارمِ ثلاثة أحجار نرد.
zombiedice-player-turn = دور { $player }. المُودَع: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.
zombiedice-you-refill-cup = الكوب منخفض: تُعيد { $count } { $count ->
    [one] حجر دماغ
    [two] حجرَي دماغ
    [few] أحجار أدمغة
    [many] حجر دماغ
   *[other] حجر دماغ
}. تبقى { $brains } من أدمغة دورك محسوبة.
zombiedice-player-refills-cup = الكوب منخفض: يُعيد { $player } { $count } { $count ->
    [one] حجر دماغ
    [two] حجرَي دماغ
    [few] أحجار أدمغة
    [many] حجر دماغ
   *[other] حجر دماغ
}. تبقى { $brains } من أدمغة دوره محسوبة.
zombiedice-you-roll = ترمي: { $results }.
zombiedice-player-rolls = { $player } يرمي: { $results }.
zombiedice-you-bust = ترمي: { $results }. { $shotguns } طلقات — أُصبت. تخسر { $brains } من الأدمغة غير المودعة.
zombiedice-player-busts = { $player } يرمي: { $results }. { $shotguns } طلقات — أُصيب. يخسر { $player } { $brains } من الأدمغة غير المودعة.
zombiedice-you-bank = تودِع { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}. المجموع: { $total }.
zombiedice-player-banks = يودِع { $player } { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}. المجموع: { $total }.
zombiedice-you-trigger-final-round = تصل إلى { $score } دماغًا. يتبقّى في الجولة الأخيرة { $remaining } { $remaining ->
    [one] لاعب
    [two] لاعبان
    [few] لاعبين
    [many] لاعبًا
   *[other] لاعب
}.
zombiedice-player-triggers-final-round = يصل { $player } إلى { $score } دماغًا. يتبقّى في الجولة الأخيرة { $remaining } { $remaining ->
    [one] لاعب
    [two] لاعبان
    [few] لاعبين
    [many] لاعبًا
   *[other] لاعب
}.
zombiedice-tiebreak-start = كسر التعادل { $round }: { $players }، متعادلون عند { $score } دماغًا. دور واحد لكل منهم.
zombiedice-you-win = تفوز بنرد الزومبي بـ { $score } دماغًا.
zombiedice-player-wins = يفوز { $player } بنرد الزومبي بـ { $score } دماغًا.
zombiedice-error-roll-before-stopping = ارمِ مرة واحدة قبل التوقف. بعد أي رمية آمنة، يجوز التوقف عند 0 دماغ.
zombiedice-error-roll-resolving = ما زال النرد يتدحرج.
zombiedice-error-target-score-range = يجب أن يكون هدف الفوز من { $min } إلى { $max } دماغًا؛ القيمة الحالية هي { $value }.

zombiedice-color-green = أخضر
zombiedice-color-yellow = أصفر
zombiedice-color-red = أحمر
zombiedice-face-brain = دماغ
zombiedice-face-footprint = خطوة
zombiedice-face-shotgun = طلقة
zombiedice-roll-result = { $face } { $color }
zombiedice-pool-color = { $count } من النرد بلون { $color }
zombiedice-no-dice = لا شيء

zombiedice-status-no-turn = لا يوجد دور نشط في نرد الزومبي.
zombiedice-your-turn-totals = أنت: { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}، { $shotguns } { $shotguns ->
    [one] طلقة
    [two] طلقتان
    [few] طلقات
    [many] طلقة
   *[other] طلقة
}، و{ $footprints } { $footprints ->
    [one] خطوة
    [two] خطوتان
    [few] خطوات
    [many] خطوة
   *[other] خطوة
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}، { $shotguns } { $shotguns ->
    [one] طلقة
    [two] طلقتان
    [few] طلقات
    [many] طلقة
   *[other] طلقة
}، و{ $footprints } { $footprints ->
    [one] خطوة
    [two] خطوتان
    [few] خطوات
    [many] خطوة
   *[other] خطوة
}.
zombiedice-status-turn-you = دورك — المُودَع: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.
zombiedice-status-turn-player = دور { $player } — المُودَع: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.
zombiedice-status-turn-totals = هذا الدور: { $brains } { $brains ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}، { $shotguns } { $shotguns ->
    [one] طلقة
    [two] طلقتان
    [few] طلقات
    [many] طلقة
   *[other] طلقة
}، و{ $footprints } { $footprints ->
    [one] خطوة
    [two] خطوتان
    [few] خطوات
    [many] خطوة
   *[other] خطوة
}.
zombiedice-status-cup = الكوب: { $count } { $count ->
    [one] حجر نرد
    [two] حجرا نرد
    [few] أحجار نرد
    [many] حجر نرد
   *[other] حجر نرد
}.
zombiedice-status-footprints = خطوات لإعادة الرمي: { $dice }.
zombiedice-status-brain-dice = أحجار الأدمغة الموضوعة جانبًا: { $dice }.
zombiedice-status-shotgun-dice = أحجار الطلقات الموضوعة جانبًا: { $dice }.
zombiedice-status-last-roll = آخر رمية: { $results }.
zombiedice-status-awaiting-roll = لا رمية بعد في هذا الدور.
zombiedice-status-table-header = نرد الزومبي — الجولة { $round }؛ الهدف: { $target } دماغًا.
zombiedice-status-table-header-tiebreak = نرد الزومبي — الهدف: { $target } دماغًا.
zombiedice-status-main-round = المرحلة: اللعب الرئيسي.
zombiedice-status-final-round = الجولة الأخيرة — { $player } بلغ الهدف.
zombiedice-status-tiebreak = كسر التعادل { $round }: { $players }.
zombiedice-status-current-you = دورك.
zombiedice-status-current-player = دور { $player }.
zombiedice-status-turn-order = ترتيب الأدوار: { $players }.
zombiedice-status-score-you = أنت: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.

zombiedice-score-unit-brains = { $count ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}
zombiedice-results-header = نتائج نرد الزومبي
zombiedice-results-winner = الفائز: { $player } بـ { $score } دماغًا.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] دماغ
    [two] دماغان
    [few] أدمغة
    [many] دماغًا
   *[other] دماغ
}.

