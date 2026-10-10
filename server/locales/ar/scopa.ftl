game-name-scopa = سكوبا

scopa-initial-table = بطاقات الطاولة: { $cards }
scopa-no-initial-table = لا بطاقات على الطاولة للبدء.
scopa-you-capture = تأسر { $cards } بـ { $card }.
scopa-player-captures = يأسر { $player } { $cards } بـ { $card }.
scopa-you-capture-scopa = تأسر { $cards } بـ { $card } وتسجّل سكوبا!
scopa-player-captures-scopa = يأسر { $player } { $cards } بـ { $card } ويسجّل سكوبا!
scopa-you-capture-clear = تأسر { $cards } بـ { $card }، وتخلي الطاولة.
scopa-player-captures-clear = يأسر { $player } { $cards } بـ { $card }، ويخلي الطاولة.
scopa-you-put-down = تضع { $card }.
scopa-player-puts-down = يضع { $player } { $card }.
scopa-clear-table-suffix = ، وتخلي الطاولة.
scopa-you-get-remaining-cards = تحصل على بطاقات الطاولة المتبقية: { $cards }.
scopa-player-gets-remaining-cards = يحصل { $player } على بطاقات الطاولة المتبقية: { $cards }.
scopa-you-instant-win = تفوز فورًا بسكوبا!
scopa-your-team-instant-win = يفوز فريقك فورًا بسكوبا!
scopa-instant-win = يفوز { $player } فورًا بسكوبا!
scopa-scoring-round = جارٍ احتساب نتيجة الجولة...
scopa-you-most-cards = تسجّل نقطة واحدة لأكثر البطاقات ({ $count } بطاقة).
scopa-your-team-most-cards = يسجّل فريقك نقطة واحدة لأكثر البطاقات ({ $count } بطاقة).
scopa-most-cards = يسجّل { $player } نقطة واحدة لأكثر البطاقات ({ $count } بطاقة).
scopa-most-cards-tie = أكثر البطاقات تعادل - لا نقطة تُمنح.
scopa-you-most-diamonds = تسجّل نقطة واحدة لأكثر الماس ({ $count } من الماس).
scopa-your-team-most-diamonds = يسجّل فريقك نقطة واحدة لأكثر الماس ({ $count } من الماس).
scopa-most-diamonds = يسجّل { $player } نقطة واحدة لأكثر الماس ({ $count } من الماس).
scopa-most-diamonds-tie = أكثر الماس تعادل - لا نقطة تُمنح.
scopa-you-seven-diamonds = تسجّل نقطة واحدة لـ7 الماس.
scopa-your-team-seven-diamonds = يسجّل فريقك نقطة واحدة لـ7 الماس.
scopa-seven-diamonds = يسجّل { $player } نقطة واحدة لـ7 الماس.
scopa-you-seven-diamonds-multi = تسجّل نقطة واحدة لأكثر عدد من 7 الماس ({ $count } × 7 الماس).
scopa-your-team-seven-diamonds-multi = يسجّل فريقك نقطة واحدة لأكثر عدد من 7 الماس ({ $count } × 7 الماس).
scopa-seven-diamonds-multi = يسجّل { $player } نقطة واحدة لأكثر عدد من 7 الماس ({ $count } × 7 الماس).
scopa-seven-diamonds-tie = 7 الماس تعادل - لا نقطة تُمنح.
scopa-you-most-sevens = تسجّل نقطة واحدة لأكثر السبعات ({ $count } سبعة).
scopa-your-team-most-sevens = يسجّل فريقك نقطة واحدة لأكثر السبعات ({ $count } سبعة).
scopa-most-sevens = يسجّل { $player } نقطة واحدة لأكثر السبعات ({ $count } سبعة).
scopa-most-sevens-tie = أكثر السبعات تعادل - لا نقطة تُمنح.
scopa-you-primiera = تسجّل نقطة واحدة للبريميرا ({ $score } نقطة).
scopa-your-team-primiera = يسجّل فريقك نقطة واحدة للبريميرا ({ $score } نقطة).
scopa-primiera = يسجّل { $player } نقطة واحدة للبريميرا ({ $score } نقطة).
scopa-primiera-tie = البريميرا تعادل - لا نقطة تُمنح.
scopa-primiera-none = لم يأسر أحد بطاقات من الأنواع الأربعة جميعها، لذا لا تُمنح نقطة بريميرا.
scopa-you-napola = تسجّل { $points } نقطة للنابولا.
scopa-your-team-napola = يسجّل فريقك { $points } نقطة للنابولا.
scopa-napola = يسجّل { $player } { $points } نقطة للنابولا.

scopa-manual-select-prompt = يجب أن تختار البطاقات التي تريد أسرها.

scopa-capture-option = أسر { $cards }

scopa-error-conflict-escoba-asso = لا يمكن تفعيل إسكوبا وأسو بيليا توتو في الوقت نفسه.
scopa-error-conflict-instant-inverse = لا يمكن تفعيل الفوز الفوري بسكوبا مع الوضع العكسي.
scopa-error-conflict-instant-no-scopas = لا يمكن تفعيل الفوز الفوري بسكوبا عندما لا تسجّل السكوبا نقاطًا.

scopa-score-line-target-pending = { $player }: { $score }/{ $target } { $unit } (+{ $round_score } سكوبا معلّقة { $pending_unit } هذه الجولة)
scopa-score-line-pending = { $player }: { $score } { $unit } (+{ $round_score } سكوبا معلّقة { $pending_unit } هذه الجولة)
scopa-target-tie-continue = تتعادل عدة أطراف عند { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}، لذا تستمر سكوبا بعد الهدف البالغ { $target } { $target ->
    [one] نقطة
   *[other] نقاط
} حتى يُكسر التعادل.
scopa-round-scores = نتائج الجولة:
scopa-round-score-line = { $player }: +{ $round_score } (الإجمالي: { $total_score })
scopa-table-empty = لا توجد بطاقات على الطاولة.
scopa-no-such-card = لا بطاقة في ذلك الموضع.
scopa-captured-count = أسرت { $count } بطاقة

scopa-view-table = عرض الطاولة
scopa-view-captured = عرض المأسور
scopa-view-table-card = عرض بطاقة الطاولة { $index }
scopa-pause-timer = إيقاف المؤقّت مؤقتًا

scopa-hint-match =  -> { $card }
scopa-hint-multi =  -> { $count } بطاقات

scopa-enter-target-score = أدخل النتيجة المستهدفة (1-121)
scopa-desc-target-score = النتيجة اللازمة للفوز في سكوبا (الافتراضي 11، النطاق 1-121).
scopa-set-cards-per-deal = البطاقات لكل توزيعة: { $cards }
scopa-enter-cards-per-deal = أدخل عدد البطاقات لكل توزيعة (1-10)
scopa-set-decks = عدد مجموعات الأوراق: { $decks }
scopa-enter-decks = أدخل عدد مجموعات الأوراق (1-6)
scopa-toggle-escoba = إسكوبا (المجموع إلى 15): { $enabled }
scopa-toggle-hints = إظهار تلميحات الأسر: { $enabled }
scopa-set-mechanic = آلية سكوبا: { $mechanic }
scopa-select-mechanic = اختر آلية سكوبا
scopa-toggle-instant-win = الفوز الفوري بسكوبا: { $enabled }
scopa-desc-team-mode = يختار اللعب الفردي أو أحجام فرق ثابتة لسكوبا.
scopa-toggle-team-scoring = تجميع بطاقات الفريق للاحتساب: { $enabled }
scopa-toggle-inverse = الوضع العكسي (بلوغ الهدف = الإقصاء): { $enabled }
scopa-toggle-manual = اختيار الأسر يدويًا: { $enabled }
scopa-toggle-asso = أسو بيليا توتو (الآس يأخذ كل شيء): { $enabled }
scopa-toggle-primiera = احتساب بريميرا التقليدي: { $enabled }
scopa-toggle-napola = نابولا (تسلسل الماس): { $enabled }

scopa-option-changed-cards = تم ضبط البطاقات لكل توزيعة على { $cards }.
scopa-desc-cards-per-deal = عدد البطاقات التي يستلمها كل لاعب في توزيعة سكوبا (الافتراضي 3، النطاق 1-10).
scopa-option-changed-decks = تم ضبط عدد مجموعات الأوراق على { $decks }.
scopa-desc-number-of-decks = عدد مجموعات سكوبا المكوّنة من 40 بطاقة التي تُخلط معًا (الافتراضي 1، النطاق 1-6).
scopa-option-changed-escoba = إسكوبا { $enabled }.
scopa-desc-escoba = يحوّل الأسر إلى قواعد إسكوبا، حيث يجب أن يبلغ مجموع البطاقة الملعوبة وبطاقات الطاولة المأسورة 15.
scopa-option-changed-hints = تلميحات الأسر { $enabled }.
scopa-desc-show-capture-hints = يُظهر بطاقات الطاولة التي يمكن لكل بطاقة في اليد أسرها.
scopa-option-changed-mechanic = تم ضبط آلية سكوبا على { $mechanic }.
scopa-desc-scopa-mechanic = يختار احتساب الكنسة العادي، أو عدم احتساب نقاط السكوبا، أو احتساب السكوبا فقط.
scopa-option-changed-instant = الفوز الفوري بسكوبا { $enabled }.
scopa-desc-instant-win-scopas = عند التفعيل، تفوز السكوبا الصالحة باللعبة فورًا. لا يمكن الجمع بين هذا و"بلا سكوبا" أو السكوبا العكسية.
scopa-option-changed-team-scoring = احتساب بطاقات الفريق { $enabled }.
scopa-desc-team-card-scoring = يتحكم في ما إذا كان زملاء الفريق يجمعون بطاقاتهم المأسورة لاحتساب نهاية الجولة. إذا عُطّل في لعبة جماعية، تُقيَّم بطاقات كل لاعب على حدة وتُضاف أي نقاط يفوز بها إلى فريقه.
scopa-option-changed-inverse = الوضع العكسي { $enabled }.
scopa-desc-inverse-scopa = يعكس الهدف بحيث يؤدي بلوغ النتيجة المستهدفة إلى إقصاء لاعب أو فريق.
scopa-option-changed-manual = اختيار الأسر يدويًا { $enabled }.
scopa-desc-manual-selection = يتيح للاعبين اختيار تركيبة الأسر يدويًا عند وجود أكثر من أسر قانوني.
scopa-option-changed-asso = أسو بيليا توتو { $enabled }.
scopa-desc-asso-piglia-tutto = يفعّل "الآس يأخذ كل شيء": يكنس الآس الطاولة ويسجّل سكوبا ما لم يكن هناك آس آخر موجود بالفعل. لا يمكن الجمع بين هذا وإسكوبا.
scopa-option-changed-primiera = احتساب بريميرا التقليدي { $enabled }.
scopa-desc-primiera-scoring = يفعّل احتساب بريميرا التقليدي؛ وعند إيقافه تستخدم اللعبة نسخة "أكثر السبعات" الأبسط.
scopa-option-changed-napola = نابولا { $enabled }.
scopa-desc-napola = يمنح نقاطًا إضافية لأسر تسلسل ماس متصل يبدأ بالآس.

scopa-mechanic-normal = عادي
scopa-mechanic-no_scopas = بلا سكوبا
scopa-mechanic-only_scopas = سكوبا فقط

scopa-timer-not-active = مؤقّت الجولة غير نشط.

scopa-error-not-enough-cards = لا توجد بطاقات كافية في { $decks } { $decks ->
    [one] مجموعة
    *[other] مجموعات
} لـ { $players } { $players ->
    [one] لاعب
    *[other] لاعبين
} بواقع { $cards_per_deal } بطاقة لكل منهم. (المطلوب { $cards_per_deal } × { $players } = { $cards_needed } بطاقة، لكن المتوفر فقط { $total_cards }.)

scopa-line-format = { $rank }. { $player }: { $points }
