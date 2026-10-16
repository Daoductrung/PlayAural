game-name-fivecarddraw = بوكر سحب الخمس بطاقات

draw-set-starting-chips = الرقاقات الابتدائية: { $count }
draw-enter-starting-chips = أدخل الرقاقات الابتدائية
draw-option-changed-starting-chips = تم ضبط الرقاقات الابتدائية على { $count }.
fivecarddraw-desc-starting-chips = رصيد كل لاعب الافتتاحي في سحب الخمس بطاقات، من 100 إلى 1,000,000 رقاقة. الافتراضي: 20,000.

draw-set-ante = الرهان المسبق: { $count }
draw-enter-ante = أدخل مبلغ الرهان المسبق
draw-option-changed-ante = تم ضبط الرهان المسبق على { $count }.
fivecarddraw-desc-ante = مساهمة إلزامية يدفعها كل لاعب نشط قبل كل يد. يجب أن تكون أقل من الرصيد الابتدائي (الافتراضي 100، النطاق 0 إلى 1,000,000 رقاقة).

draw-set-turn-timer = مؤقّت الدور: { $mode }
draw-select-turn-timer = اختر مؤقّت الدور
draw-option-changed-turn-timer = تم ضبط مؤقّت الدور على { $mode }.
fivecarddraw-desc-turn-timer = حد زمني اختياري لكل قرار رهان أو سحب: 5 أو 10 أو 15 أو 20 أو 30 أو 45 أو 60 أو 90 ثانية، أو غير محدود. الافتراضي: غير محدود.

draw-set-raise-mode = نمط المزايدة: { $mode }
draw-select-raise-mode = اختر نمط المزايدة
draw-option-changed-raise-mode = تم ضبط نمط المزايدة على { $mode }.
fivecarddraw-desc-raise-mode = نمط حد المزايدة: بلا حد، أو حد القدر، أو حد ضعف القدر. تتطلب الأنماط المعتمدة على القدر رهانًا مسبقًا أكبر من 0 كي تُفتَح جولة الرهان الأولى بشكل طبيعي (الافتراضي بلا حد).

draw-set-max-raises = أقصى عدد مزايدات في جولة الرهان: { $count }
draw-enter-max-raises = أدخل أقصى عدد مزايدات في جولة الرهان (0 لغير محدود)
draw-option-changed-max-raises = تم ضبط أقصى عدد مزايدات في جولة الرهان على { $count }.
fivecarddraw-desc-max-raises = أقصى عدد مزايدات مسموح به في جولة رهان واحدة، من 0 إلى 10. اضبط 0 لإلغاء حد المزايدة. الافتراضي: 0.

draw-set-draw-limit = قاعدة السحب: { $mode }
draw-select-draw-limit = اختر قاعدة السحب
draw-option-changed-draw-limit = تم ضبط قاعدة السحب على { $mode }.
fivecarddraw-desc-draw-limit = قاعدة السحب: استبدل حتى 3 بطاقات، أو اسمح بـ 4 بطاقات فقط عند الاحتفاظ بآس. الافتراضي: حتى 3 بطاقات.
draw-limit-three-cards = حتى 3 بطاقات (قياسي)
draw-limit-four-with-ace = حتى 4 بطاقات عند الاحتفاظ بآس

draw-error-ante-too-high = يجب أن يكون الرهان المسبق ({ $ante } رقاقة) أقل من الرصيد الابتدائي ({ $chips } رقاقة) كي يتمكن اللاعبون من اتخاذ قرارات الرهان بعد التوزيع.
draw-error-capped-mode-needs-ante = { $mode ->
    [pot_limit] حد القدر
    [double_pot] حد ضعف القدر
   *[other] نمط المزايدة المحدود هذا
} يتطلب رهانًا مسبقًا أكبر من 0 كي يتوفر للاعب الأول مبلغ معتمد على القدر للمراهنة.

draw-antes-posted = تم دفع الرهانات المسبقة. يحتوي القدر الآن على { $amount } رقاقة.
draw-betting-round-1 = جولة الرهان الأولى.
draw-betting-round-2 = جولة الرهان الثانية.
draw-begin-draw = مرحلة السحب. ابتداءً من أول لاعب نشط على يسار الموزّع، اختر البطاقات التي تريد استبدالها أو ابقَ على أوراقك.
draw-not-draw-phase = سحب البطاقات متاح فقط بعد جولة الرهان الأولى. تابع إجراء الرهان الحالي.
draw-not-betting = الرهان غير متاح أثناء مرحلة السحب. اختر أي بطاقات لاستبدالها، ثم اختر سحب البطاقات.
draw-fold-not-available = الانسحاب غير متاح أثناء مرحلة السحب. اختر أي بطاقات لاستبدالها، ثم اختر سحب البطاقات.

draw-toggle-discard = اختر البطاقة { $index } لاستبدالها
draw-card-keep = { $card }
draw-card-discard = { $card }، مختارة للاستبدال
draw-draw-cards = اسحب البطاقات
draw-draw-cards-count = { $count ->
    [0] البقاء على الأوراق
    [one] استبدال بطاقة واحدة
   *[other] استبدال { $count } بطاقات
}
draw-dealt-cards = بطاقاتك الخمس هي { $cards }.
draw-you-drew-cards = بطاقاتك البديلة الـ{ $count } { $count ->
    [one] هي
   *[other] هي
} { $cards }.
draw-you-draw = تستبدل { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
draw-player-draws = { $player } يستبدل { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
draw-you-stand-pat = تبقى على أوراقك وتحتفظ بالبطاقات الخمس كلها.
draw-player-stands-pat = { $player } يبقى على أوراقه ويحتفظ بالبطاقات الخمس كلها.
draw-you-discard-limit = لا يمكنك استبدال أكثر من { $count } بطاقات بموجب قاعدة السحب المختارة.
draw-four-requires-kept-ace = استبدال 4 بطاقات يتطلب الاحتفاظ بآس واحد على الأقل. ألغِ اختيار آس أو استبدل ما لا يزيد عن 3 بطاقات.

draw-raise-invalid = أدخل عددًا صحيحًا أكبر من 0 لمبلغ المزايدة.
draw-raise-cap-reached = تم بلوغ حد الـ{ $count } مزايدات في جولة الرهان هذه. يمكنك المجاراة أو الانسحاب.
draw-raise-over-stack = حاولت المزايدة بـ { $requested } رقاقة، لكن لديك { $chips } رقاقة فقط متبقية. أدخل مزايدة أصغر أو اختر دفع كل الرقائق.
draw-raise-too-small = حاولت المزايدة بـ { $requested } رقاقة. أدنى مزايدة هي { $minimum } رقاقة.
draw-raise-over-limit = حاولت المزايدة بـ { $requested } رقاقة. بموجب { $mode ->
    [pot_limit] حد القدر
    [double_pot] حد ضعف القدر
   *[other] نمط المزايدة المختار
}، أكبر مزايدة متاحة بعد المجاراة هي { $maximum } رقاقة.
draw-all-in-over-limit = لا يمكنك دفع كل الرقائق برصيدك المتبقي البالغ { $stack } رقاقة لأن { $mode ->
    [pot_limit] حد القدر
    [double_pot] حد ضعف القدر
   *[other] نمط المزايدة المختار
} يسمح حاليًا بمزايدة لا تتجاوز { $maximum } رقاقة بعد المجاراة. استخدم المزايدة لإدخال مبلغ مسموح به.
draw-all-in-raise-cap-reached = لا يمكنك دفع كل الرقائق كمزايدة كاملة لأن حد الـ{ $count } مزايدات قد بُلغ بالفعل. يمكنك المجاراة أو الانسحاب.
draw-all-in-unavailable-raise-cap = دفع كل الرقائق غير متاح لأنه سيكون مزايدة كاملة بعد بلوغ حد المزايدات. يمكنك المجاراة أو الانسحاب.
draw-all-in-unavailable-limit = دفع كل الرقائق غير متاح لأن رصيدك يتجاوز حد الرهان الحالي. استخدم المزايدة لإدخال مبلغ مسموح به.
draw-raise-unavailable-cap = المزايدة غير متاحة لأن جولة الرهان هذه بلغت حد المزايدات.
draw-raise-unavailable-limit = المزايدة الكاملة غير متاحة برصيدك وحد الرهان الحالي. يمكنك المجاراة أو الانسحاب أو دفع كل الرقائق متى كان ذلك مسموحًا.

draw-current-bet = رهان الطاولة الحالي هو { $amount } رقاقة.
draw-raise-range = أدنى مزايدة هي { $minimum } رقاقة. يمكنك المزايدة بما يصل إلى { $maximum } رقاقة بعد المجاراة.
draw-no-full-raise-available = تحتاج { $to_call } رقاقة للمجاراة ولديك { $chips } رقاقة متبقية، لذا لا يمكنك إجراء مزايدة كاملة. يمكنك المجاراة بكل رقائقك أو الانسحاب.
draw-dealer-unavailable = لا يوجد موقع موزّع لليد الحالية بعد.
draw-position-unavailable = لست نشطًا في اليد الحالية، لذا ليس لديك موقع رهان.

draw-card-key = مفتاح البطاقة { $index }

draw-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] رقاقة واحدة
    [two] رقاقتان
    [few] رقاقات
    [many] رقاقة
   *[other] رقاقة
}
