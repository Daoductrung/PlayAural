# Options
trucospanish-length-18 = 18 نقطة لكل كامي (came)
trucospanish-length-24 = 24 نقطة لكل كامي (came)
trucospanish-set-length = طول الكامي (came): { $mode }
trucospanish-select-length = اختر طول الكامي (came):
trucospanish-option-changed-length = أصبح طول الكامي (came) { $mode }.
trucospanish-desc-length = تُكسب اللعبة بالفوز بكاميين (cames). يُلعب الكامي حتى عدد النقاط المختار: 24 كما في بطولة الفايّاس (Falles) في فالنسيا وبطولة الجامعة البوليتكنيكية في فالنسيا (Universitat Politècnica de València)، أو 18 كما في بطولة توريّنت (Torrent) ووصف متحف تاريخ فالنسيا (Museu d'Història de València). عندما يبلغه فريق، يفوز بالكامي وتبدأ النتيجتان من الصفر من جديد. تساوي لا فالتا (La falta) ما يحتاجه المتقدم لإنهاء الكامي، ويفوز جوك فورا (Joc fora) باللعبة كاملة.
trucospanish-desc-team-mode = الوضع الفردي لعبة واحد ضد واحد للاعبين اثنين. يستخدم 2 ضد 2 أربعة لاعبين؛ ويتشارك الشريكان النتيجة ويجوز لهما الإعلان نيابةً عن الفريق كله.

# Calls
trucospanish-call-truc = تروك
trucospanish-call-retruc = ريتروك
trucospanish-call-quatre-val = كواتر فال
trucospanish-call-joc-fora = جوك فورا
trucospanish-call-envit = إنفيت
trucospanish-call-torna = تورنا
trucospanish-call-la-falta = لا فالتا

# Actions and messages
trucospanish-action-accept = فول (أقبل)
trucospanish-action-decline = نو فول (أرفض)
trucospanish-action-mazo = مين فاتش (أترك التوزيعة)
trucospanish-accept-you = تقول فول على { $call }.
trucospanish-accept-player = يقول { $player } فول على { $call }.
trucospanish-decline-you = تقول نو فول على { $call }.
trucospanish-decline-player = يقول { $player } نو فول على { $call }.
trucospanish-mazo-you = تقول مين فاتش وتتنازل عن التوزيعة نيابةً عن فريقك كله.
trucospanish-mazo-player = يقول { $player } مين فاتش ويتنازل عن التوزيعة نيابةً عن الفريق كله.
trucospanish-reason-truc = التروك
trucospanish-reason-envit = الإنفيت
trucospanish-game-start = تبدأ لعبة تروكو الإسباني. افز بكاميين (cames) من { $points } نقطة لتفوز باللعبة.
trucospanish-desc-mazo = تنازل عن التوزيعة نيابةً عن فريقك كله. يسجّل الفريق الآخر القيمة الحالية للتوزيعة.
trucospanish-came-you = تفوز بكامي (came)! لديك { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}. تبدأ النتيجة من الصفر من جديد.
trucospanish-came-player = يفوز { $player } بكامي (came) ولديه { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}. تبدأ النتيجة من الصفر من جديد.
trucospanish-came-your-team = يفوز فريقك بكامي (came)! لديكم { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}. تبدأ النتيجة من الصفر من جديد.
trucospanish-came-team = يفوز { $team } بكامي (came) ولديه { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}. تبدأ النتيجة من الصفر من جديد.

trucospanish-pending-answer = أعلن { $player } { $call }. رُدّ بـ فول أو نو فول، أو ارفع.
trucospanish-error-answer-first = يجب أن ترد على { $call } قبل أي شيء آخر. اختر فول أو نو فول، أو ارفع.
trucospanish-error-raise-max = جوك فورا هو أعلى إعلان بالفعل ولا يمكن رفعه.
trucospanish-error-bad-count = يحتاج تروكو الإسباني إلى لاعبين اثنين أو أربعة، لكن العدد الحالي { $count }.
trucospanish-error-team-mode-count = لا يمكن استخدام وضع الفرق { $mode } مع { $count } لاعبين. استخدم الوضع الفردي للاعبين اثنين أو 2 ضد 2 لأربعة لاعبين.
trucospanish-status-envit-open = ما زال بالإمكان إعلان الإنفيت في هذه التوزيعة.
trucospanish-status-envit-closed = أُغلق الإنفيت في هذه التوزيعة.
trucospanish-status-no-truc = لم يُعلَن أي تروك. تساوي التوزيعة { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.
trucospanish-falta-value = لا فالتا تساوي { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.
trucospanish-reveal-envit-you = فزت بالإنفيت ببطاقاتك: { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.
trucospanish-reveal-envit-player = فاز { $player } بالإنفيت بـ { $cards }، بقيمة { $value } { $value ->
    [one] نقطة
   *[other] نقاط
}.
trucospanish-error-envit-late = لا يمكن إعلان الإنفيت إلا قبل أن تلعب أول بطاقة لك.
trucospanish-error-envit-closed = أُغلق الإنفيت لأن التروك قُبل بالفعل.
trucospanish-error-envit-done = لُعب الإنفيت بالفعل في هذه التوزيعة.
trucospanish-error-envit-cannot-raise = لا يمكن إضافة { $call } إلى الإنفيت الجاري.

# Score and game end (the game is won with two cames)
trucospanish-score-line = { $team }: { $score } { $score ->
    [one] نقطة
   *[other] نقاط
} في هذا الكامي، فاز بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}
trucospanish-game-win-you = تفوز باللعبة بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}!
trucospanish-game-win-player = يفوز { $player } باللعبة بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}.
trucospanish-game-win-your-team = يفوز فريقك باللعبة بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}!
trucospanish-game-win-team = يفوز { $team } باللعبة بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}.
trucospanish-end-line = { $rank }. { $team }: { $score } { $score ->
    [one] كامي
   *[other] كامي
}
trucospanish-cames-line = { $team }: فاز بـ { $cames } { $cames ->
    [one] كامي
   *[other] كامي
}
