game-name-yahtzee = ياتزي

yahtzee-roll = إعادة الرمي (تبقّى { $count })
yahtzee-roll-all = ارمِ النرد

yahtzee-score-ones = خانة الواحد مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-twos = خانة الاثنين مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-threes = خانة الثلاثة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-fours = خانة الأربعة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-fives = خانة الخمسة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-sixes = خانة الستة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-three-kind = ثلاثة متشابهة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-four-kind = أربعة متشابهة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-full-house = فُل هاوس مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-small-straight = ستريت صغير مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-large-straight = ستريت كبير مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-yahtzee = ياتزي مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-score-chance = الفرصة مقابل { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}
yahtzee-you-rolled = رميت: { $dice }. { $remaining ->
    [0] اختر فئة تسجيل.
   *[other] { $remaining } { $remaining ->
        [one] رمية
        [two] رميتان
        [few] رميات
        [many] رمية
       *[other] رمية
    } متبقّية.
}
yahtzee-player-rolled = رمى { $player }: { $dice }. { $remaining ->
    [0] { GENDER_TERM($player_gender, "subject-capitalized") } بحاجة إلى اختيار فئة تسجيل.
   *[other] { $remaining } { $remaining ->
        [one] رمية
        [two] رميتان
        [few] رميات
        [many] رمية
       *[other] رمية
    } متبقّية.
}
yahtzee-you-rolled-brief = رميت: { $dice }.
yahtzee-player-rolled-brief = رمى { $player }: { $dice }.

yahtzee-you-scored = سجّلت { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
} في { $category }.
yahtzee-player-scored = سجّل { $player } { $points } { $points ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
} في { $category }.
yahtzee-you-scored-brief = { $points } في { $category }.
yahtzee-player-scored-brief = { $player }: { $points } في { $category }.

yahtzee-you-bonus = مكافأة ياتزي! +100 نقطة
yahtzee-player-bonus = حصل { $player } على مكافأة ياتزي! +100 نقطة
yahtzee-you-bonus-brief = مكافأة ياتزي، +100.
yahtzee-player-bonus-brief = { $player }: مكافأة ياتزي، +100.
yahtzee-you-upper-bonus = مكافأة القسم العلوي! +35 نقطة ({ $total } في القسم العلوي)
yahtzee-player-upper-bonus = حصل { $player } على مكافأة القسم العلوي! +35 نقطة ({ $total } في القسم العلوي)
yahtzee-you-upper-bonus-brief = مكافأة القسم العلوي، +35.
yahtzee-player-upper-bonus-brief = { $player }: مكافأة القسم العلوي، +35.
yahtzee-you-upper-bonus-missed = فاتتك مكافأة القسم العلوي. سجّلت { $total }؛ كنت بحاجة إلى { $needed } إضافية.
yahtzee-player-upper-bonus-missed = فاتت { $player } مكافأة القسم العلوي بـ { $total } في القسم العلوي، بنقص { $needed }.
yahtzee-you-upper-bonus-missed-brief = فاتت مكافأة القسم العلوي؛ بنقص { $needed }.
yahtzee-player-upper-bonus-missed-brief = { $player }: فاتت مكافأة القسم العلوي، بنقص { $needed }.

yahtzee-check-scoresheet = عرض بطاقة النتائج
yahtzee-check-all-scorecards = عرض بطاقة النتائج لكل اللاعبين
yahtzee-select-scorecard-player = اختر بطاقة نتائج لاعب.
yahtzee-scorecard-no-players = لا يملك أي لاعب نشط بطاقة نتائج في هذه اللعبة بعد.
yahtzee-scorecard-player-unavailable = لم يعد ذلك اللاعب متاحًا للعرض. افتح قائمة بطاقات النتائج مجددًا واختر لاعبًا نشطًا.
yahtzee-view-dice = عرض اليد
yahtzee-your-dice = نردك: { $dice }.
yahtzee-your-dice-kept = نردك: { $dice }. المحتفظ به: { $kept }.
yahtzee-current-dice = نرد { $player }: { $dice }.
yahtzee-current-dice-kept = نرد { $player }: { $dice }. المحتفظ به: { $kept }.
yahtzee-not-rolled = لم يرمِ اللاعب الحالي بعد.

yahtzee-scoresheet-header = بطاقة نتائج { $player }
yahtzee-scoresheet-upper = القسم العلوي:
yahtzee-scoresheet-lower = القسم السفلي:
yahtzee-scoresheet-upper-total-bonus = مجموع القسم العلوي: { $total } (مكافأة: +35)
yahtzee-scoresheet-upper-total-needed = مجموع القسم العلوي: { $total } ({ $needed } إضافية للمكافأة)
yahtzee-scoresheet-yahtzee-bonus = مكافآت ياتزي: { $count } × 100 = { $total }
yahtzee-scoresheet-grand-total = النتيجة الإجمالية: { $total }

yahtzee-category-ones = خانة الواحد
yahtzee-category-twos = خانة الاثنين
yahtzee-category-threes = خانة الثلاثة
yahtzee-category-fours = خانة الأربعة
yahtzee-category-fives = خانة الخمسة
yahtzee-category-sixes = خانة الستة
yahtzee-category-three-kind = ثلاثة متشابهة
yahtzee-category-four-kind = أربعة متشابهة
yahtzee-category-full-house = فُل هاوس
yahtzee-category-small-straight = ستريت صغير
yahtzee-category-large-straight = ستريت كبير
yahtzee-category-yahtzee = ياتزي
yahtzee-category-chance = الفرصة
yahtzee-you-win = تفوز بـ { $score } { $score ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}!
yahtzee-player-wins = يفوز { $player } بـ { $score } { $score ->
    [one] نقطة
    [two] نقطتان
    [few] نقاط
    [many] نقطة
   *[other] نقطة
}!
yahtzee-winners-tie = إنه تعادل! سجّل { $players } جميعًا { $score } نقطة!

yahtzee-set-rounds = عدد الألعاب: { $rounds }
yahtzee-enter-rounds = أدخل عدد الألعاب (1-10):
yahtzee-option-changed-rounds = تم ضبط عدد الألعاب على { $rounds }.
yahtzee-desc-num-games = عدد بطاقات نتائج ياتزي الكاملة التي تُلعب قبل مقارنة المجاميع النهائية (الافتراضي 1، المدى 1-10).

yahtzee-no-rolls-left = لم تتبقَّ لك رميات؛ اختر فئة تسجيل مفتوحة لإنهاء دورك.
yahtzee-roll-first = ارمِ النرد قبل اختيار فئة تسجيل.
yahtzee-category-filled = تلك الفئة لديها نتيجة بالفعل. اختر فئة ما زالت مفتوحة في بطاقة نتائجك.
yahtzee-joker-upper-required = قاعدة الجوكر: لأن هذا الياتزي يُظهر { $face }، يجب أن تسجّل في خانة القسم العلوي الخاصة بـ { $face } قبل أي فئة أخرى.
yahtzee-joker-lower-required = قاعدة الجوكر: خانة القسم العلوي الخاصة بـ { $face } ممتلئة بالفعل، لذا يجب أن تختار فئة مفتوحة في القسم السفلي قبل استخدام خانة أخرى في القسم العلوي.
