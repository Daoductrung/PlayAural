game-name-truco = تروكو

# Options
truco-set-variant = النسخة: { $mode }
truco-select-variant = اختر نسخة تروكو:
truco-option-changed-variant = أصبحت النسخة { $mode }.
truco-desc-variant = يستخدم تروكو الأرجنتيني مجموعة الأوراق الإسبانية من 40 بطاقة، مع إنفيدو (Envido) وفلور (Flor) اختياري. يستخدم تروكو البرازيلي (باوليستا) مجموعة أوراق فرنسية مع بطاقة مكشوفة تسمى فيرا (vira) تحدد أقوى البطاقات، وتساوي الرفعات 3 و6 و9 و12 نقطة. يستخدم تروكو الإسباني (تروك فالنسي) مجموعة من 22 بطاقة مع إنفيت (envit) وجوك فورا (Joc fora) الذي يساوي اللعبة كاملة.
truco-variant-argentine = تروكو الأرجنتيني
truco-variant-brazilian = تروكو البرازيلي
truco-variant-spanish = تروكو الإسباني
truco-length-15 = 15 نقطة
truco-length-30 = 30 نقطة
truco-set-length = طول اللعبة: { $mode }
truco-select-length = اختر طول اللعبة:
truco-option-changed-length = أصبح طول اللعبة { $mode }.
truco-desc-length = في لعبة من 15 نقطة يفوز أول فريق يبلغ 15 نقطة. في لعبة من 30 نقطة، تكون النقاط من 1 إلى 15 هي المالاس (malas، النصف الأول) والنقاط من 16 إلى 30 هي البوينس (buenas، النصف الثاني)؛ ويفوز أول فريق يبلغ 30.
truco-set-flor = فلور: { $enabled }
truco-option-changed-flor = أصبح فلور { $enabled }.
truco-desc-flor = عند التفعيل، يكون للاعب الذي وُزّعت عليه ثلاث بطاقات من النوع نفسه فلور. يُعلَن عنه تلقائيًا ويلغي الإنفيدو. يساوي الفلور 3 نقاط، وكونترافلور 6، أما كونترافلور آل ريستو فيساوي ما يحتاجه الفريق المتقدم ليفوز. لا يجوز الرد أو الرفع إلا للاعب لديه فلور. يُحسب الفلور 20 زائد قيم البطاقات الثلاث كلها (الصور قيمتها صفر)، فيكون 7 و6 و5 من نوع واحد 38؛ ويفوز الفلور الأعلى. عند الإيقاف، لا قيمة خاصة لثلاث بطاقات من نوع واحد.
truco-desc-team-mode = الوضع الفردي لعبة واحد ضد واحد للاعبين اثنين. يستخدم 2 ضد 2 أربعة لاعبين، ويستخدم 3 ضد 3 ستة لاعبين؛ ويتشارك الشريكان النتيجة ويجوز لهما الإعلان نيابةً عن الفريق كله.

# Spanish deck
truco-suit-oros = النقود
truco-suit-copas = الكؤوس
truco-suit-espadas = السيوف
truco-suit-bastos = العصي
truco-card-name = { $rank } { $suit }

# Calls
truco-call-truco = تروكو
truco-call-retruco = ريتروكو
truco-call-valecuatro = فالي كواترو
truco-call-envido = إنفيدو
truco-call-real-envido = ريال إنفيدو
truco-call-falta-envido = فالتا إنفيدو
truco-call-flor = فلور
truco-call-contraflor = كونترافلور
truco-call-contraflor-al-resto = كونترافلور آل ريستو

# Actions
truco-action-play-card = { $card }
truco-action-accept = كييرو (أقبل)
truco-action-decline = نو كييرو (أرفض)
truco-action-mazo = ميه فوي آل مازو (أطوي بطاقاتي)
truco-read-hand = قراءة بطاقاتك
truco-read-table = قراءة البطاقات على الطاولة
truco-read-calls = قراءة الإعلانات الحالية

# Game and hand flow
truco-game-start-flor = تبدأ لعبة تروكو مع فلور. يفوز أول فريق يبلغ { $points } نقطة.
truco-game-start-no-flor = تبدأ لعبة تروكو بدون فلور. يفوز أول فريق يبلغ { $points } نقطة.
truco-hand-start = تبدأ التوزيعة { $hand }. وُزّعت البطاقات.
truco-dealer-you = أنت توزّع.
truco-dealer-player = { $player } يوزّع.
truco-mano-you = أنت المانو (mano) وتلعب أولًا.
truco-mano-player = { $player } هو المانو (mano) ويلعب أولًا.
truco-your-cards = بطاقاتك: { $cards }.
truco-no-cards = لم تبقَ لديك أي بطاقات.
truco-your-turn = دورك لتلعب بطاقة.

# Playing cards and tricks
truco-play-you = تلعب { $card }.
truco-play-player = يلعب { $player } { $card }.
truco-trick-win-you = اللمّة { $trick }: تفوز بها بـ { $card }.
truco-trick-win-teammate = اللمّة { $trick }: يفوز بها زميلك { $player } بـ { $card }.
truco-trick-win-opponent = اللمّة { $trick }: يفوز بها { $player } بـ { $card } لصالح { $team }.
truco-trick-tie = اللمّة { $trick } تعادل، ويسمى باردا (parda).

# Calling and answering
truco-call-you = تُعلن { $call }.
truco-call-player = يُعلن { $player } { $call }.
truco-call-goes-first-you = تُعلن { $call }. يُحسم الإنفيدو أولًا، قبل الرد على التروكو.
truco-call-goes-first-player = يُعلن { $player } { $call }. يُحسم الإنفيدو أولًا، قبل الرد على التروكو.
truco-pending-answer = أعلن { $player } { $call }. رُدّ بـ كييرو أو نو كييرو، أو ارفع.
truco-pending-wait = بانتظار رد { $team } على { $call }.
truco-accept-you = تقول كييرو (أقبل) على { $call }.
truco-accept-player = يقول { $player } كييرو (أقبل) على { $call }.
truco-decline-you = تقول نو كييرو (أرفض) على { $call }.
truco-decline-player = يقول { $player } نو كييرو (أرفض) على { $call }.
truco-mazo-you = تقول ميه فوي آل مازو (أطوي بطاقاتي) وتطوي بطاقاتك.
truco-mazo-player = يقول { $player } ميه فوي آل مازو (أطوي بطاقاتي) ويطوي بطاقاته.
truco-team-folded-your-team = طوى جميع أفراد فريقك بطاقاتهم.
truco-team-folded-team = طوى جميع أفراد { $team } بطاقاتهم.
truco-flor-announce-you = لديك فلور.
truco-flor-announce-player = لدى { $player } فلور.
truco-flor-cancels-envido = أُلغي الإنفيدو بسبب الفلور.
truco-reveal-envido-you = فزت بالإنفيدو ببطاقاتك: { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.
truco-reveal-envido-player = فاز { $player } بالإنفيدو بـ { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.
truco-reveal-flor-you = فزت بالفلور ببطاقاتك: { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.
truco-reveal-flor-player = فاز { $player } بالفلور بـ { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.

# Envido and flor
truco-falta-envido-value = فالتا إنفيدو تساوي { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.
truco-falta-envido-game = فالتا إنفيدو: الفريقان كلاهما في المالاس، لذا يفوز الرابح باللعبة كاملة.

# Points and score
truco-reason-truco = التروكو
truco-reason-envido = الإنفيدو
truco-reason-flor = الفلور
truco-reason-hand = التوزيعة
truco-points-your-team = يسجّل فريقك { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} عن { $reason }.
truco-points-team = يسجّل { $team } { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} عن { $reason }.
truco-score-line = { $team }: { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}.
truco-half-buenas-your-team = يدخل فريقك البوينس (buenas)، النصف الثاني.
truco-half-buenas-team = يدخل { $team } البوينس (buenas)، النصف الثاني.

# Information
truco-status-no-truco = لم يُعلَن أي تروكو. تساوي التوزيعة { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.
truco-status-truco = التوزيعة عند { $call }، وتساوي { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.
truco-status-truco-pending = { $call } بانتظار رد { $team }.
truco-status-envido-open = ما زال بالإمكان إعلان الإنفيدو في هذه التوزيعة.
truco-status-envido-closed = أُغلق الإنفيدو في هذه التوزيعة.
truco-table-empty = لم تُلعب أي بطاقة بعد.
truco-table-trick = اللمّة { $trick }: { $cards }.
truco-table-played = { $player }: { $card }

# Errors and disabled-action reasons
truco-error-bad-count = يحتاج تروكو إلى 2 أو 4 أو 6 لاعبين، لكن العدد الحالي { $count }.
truco-error-team-mode-count = لا يمكن استخدام وضع الفرق { $mode } مع { $count } لاعبين. استخدم الوضع الفردي للاعبين اثنين، أو 2 ضد 2 لأربعة لاعبين، أو 3 ضد 3 لستة لاعبين.
truco-error-not-your-turn = حان دور { $player } ليلعب بطاقة.
truco-error-answer-first = يجب أن ترد على { $call } قبل أي شيء آخر. اختر كييرو أو نو كييرو، أو ارفع.
truco-error-nothing-to-answer = لا يوجد إعلان ينتظر ردك.
truco-error-own-team-call = فريقك هو من أعلن ذلك. انتظر رد { $team } على { $call }.
truco-error-envido-late = لا يمكن إعلان الإنفيدو إلا قبل أن تلعب أول بطاقة لك.
truco-error-envido-closed = أُغلق الإنفيدو لأن التروكو قُبل بالفعل.
truco-error-envido-done = لُعب الإنفيدو بالفعل في هذه التوزيعة.
truco-error-raise-max = التروكو عند فالي كواترو بالفعل ولا يمكن رفعه.
truco-error-raise-holder = فريقك هو من أعلن آخر تروكو. لا يستطيع رفعه الآن إلا { $team }.
truco-error-flor-none = لقد طويت بطاقاتك في هذه التوزيعة، لذا لا يمكنك الإعلان أو الرد.
truco-error-flor-holders-only = لا يجوز الرد على الفلور أو رفعه إلا للاعب لديه فلور.
truco-error-card-not-held = ليست لديك هذه البطاقة.
truco-error-hand-over = انتهت التوزيعة بالفعل.

# Game end
truco-game-win-you = تفوز باللعبة بـ { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}!
truco-game-win-player = يفوز { $player } باللعبة بـ { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}!
truco-game-win-your-team = يفوز فريقك باللعبة بـ { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}!
truco-game-win-team = يفوز { $team } باللعبة بـ { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}!
truco-end-title = نتائج تروكو
truco-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] نقطة
   *[other] نقاط
}.

# Additional errors and individual-mode messages
truco-error-flor-off = الفلور متوقف في هذه اللعبة، فلا شيء يمكن إعلانه أو الرد عليه.
truco-error-flor-window = يجب حسم الفلور أولًا. لا يمكن إعلان التروكو حتى تُلعب أول بطاقة.
truco-error-flor-window-closed = لا يمكن إعلان كونترافلور إلا عندما يكون لدى الفريقين فلور وقبل أن تُلعب أول بطاقة.
truco-error-envido-flor = أُلغي الإنفيدو في هذه التوزيعة لأن لدى أحد اللاعبين فلور.
truco-error-envido-cannot-raise = لا يمكن إضافة { $call } إلى الإنفيدو الجاري.
truco-points-you = تسجّل { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} عن { $reason }.
truco-points-player = يسجّل { $player } { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} عن { $reason }.
truco-half-buenas-you = تدخل البوينس (buenas)، النصف الثاني.
truco-half-buenas-player = يدخل { $player } البوينس (buenas)، النصف الثاني.

# Card information, descriptions and touch gestures
truco-card-info-label = معلومات العنصر
truco-card-info = { $card }: تغلب { $beats } من البطاقات الأخرى البالغ عددها { $total } في هذه المجموعة.
truco-card-info-envido = { $card }: تغلب { $beats } من البطاقات الأخرى البالغ عددها { $total } في هذه المجموعة. قيمة الإنفيدو: { $value }.
truco-desc-call-ladder = { $call }: يرفع قيمة التوزيعة إلى { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}. إذا رُفض، يفوز الفريق المُعلِن بـ { $refused } { $refused ->
    [one] نقطة
   *[other] نقاط
}.
truco-desc-call-envido = { $call }: يقارن الفريقان إنفيدو كل منهما. إذا قُبل، يسجّل الفائز { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}. وإذا رُفض، يسجّل الفريق المُعلِن { $refused } { $refused ->
    [one] نقطة
   *[other] نقاط
}.
truco-desc-call-flor = { $call }: يقارن أصحاب الفلور فلورهم. إذا قُبل، يسجّل الفائز { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}. وإذا رُفض، يسجّل الفريق المُعلِن { $refused } { $refused ->
    [one] نقطة
   *[other] نقاط
}.
truco-desc-accept = اقبل { $call } وواصل اللعب.
truco-desc-decline = ارفض { $call }. يسجّل الفريق الآخر { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} وتنتهي التوزيعة.
truco-desc-mazo = اطوِ بطاقاتك. إذا طوى جميع أفراد فريقك بطاقاتهم، يفوز الفريق الآخر بالتوزيعة.
truco-trick-tie-neutral = اللمّة { $trick } متعادلة.
