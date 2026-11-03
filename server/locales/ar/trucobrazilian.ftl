# Options
trucobrazilian-desc-team-mode = الوضع الفردي لعبة واحد ضد واحد للاعبين اثنين. يستخدم 2 ضد 2 أربعة لاعبين، ويستخدم 3 ضد 3 ستة لاعبين؛ ويتشارك الشريكان النتيجة ويجوز لهما الإعلان نيابةً عن الفريق كله.

# French deck
trucobrazilian-rank-ace = آس
trucobrazilian-rank-jack = ولد
trucobrazilian-rank-queen = ملكة
trucobrazilian-rank-king = ملك
trucobrazilian-suit-diamonds = الماس
trucobrazilian-suit-spades = البستوني
trucobrazilian-suit-hearts = القلوب
trucobrazilian-suit-clubs = السباتي
trucobrazilian-card-name = { $rank } { $suit }

# Calls
trucobrazilian-call-truco = تروكو
trucobrazilian-call-seis = سيس
trucobrazilian-call-nove = نوفي
trucobrazilian-call-doze = دوزي
trucobrazilian-call-onze = ماو دي أونزي

# Actions and information
trucobrazilian-action-onze-play = جوغار (ألعب التوزيعة)
trucobrazilian-action-onze-run = كورير (أهرب وأتنازل عن التوزيعة)
trucobrazilian-read-vira = قراءة الفيرا والمانيليا
trucobrazilian-no-vira = لم تُكشف الفيرا بعد.
trucobrazilian-vira = الفيرا هي { $card }. المانيليا هي { $manilha }.
trucobrazilian-vira-is = الفيرا هي { $card }. المانيليا هي { $manilha }.

# Game flow
trucobrazilian-game-start = تبدأ لعبة تروكو البرازيلي. يفوز أول فريق يبلغ { $points } نقطة. في كل توزيعة، تحدد بطاقة مكشوفة تسمى الفيرا (vira) المانيليات (manilhas).
trucobrazilian-onze-your-team = لدى فريقك 11 نقطة: ماو دي أونزي (mão de onze). اختر جوغار لتلعب التوزيعة مقابل 3 نقاط دون إعلانات، أو كورير لتمنح الفريق الآخر نقطة واحدة.
trucobrazilian-onze-team = لدى { $team } 11 نقطة ويقرر ما إذا كان سيلعب ماو دي أونزي.
trucobrazilian-onze-play-you = تلعب ماو دي أونزي. تساوي التوزيعة 3 نقاط ولا يُسمح بأي إعلانات.
trucobrazilian-onze-play-player = يلعب { $player } ماو دي أونزي. تساوي التوزيعة 3 نقاط ولا يُسمح بأي إعلانات.
trucobrazilian-onze-run-you = تهرب. يسجّل الفريق الآخر نقطة واحدة.
trucobrazilian-onze-run-player = يهرب { $player }. يسجّل الفريق الآخر نقطة واحدة.
trucobrazilian-ferro = لدى الفريقين 11 نقطة: ماو دي فيرو (mão de ferro). لا يُسمح بأي إعلانات، ومن يفز بالتوزيعة يفز باللعبة.
trucobrazilian-reason-onze-run = الهروب في ماو دي أونزي
trucobrazilian-hand-annulled = تعادلت اللمّات الثلاث كلها. أُلغيت التوزيعة ولا يسجّل أحد أي نقاط.

# Errors and descriptions
trucobrazilian-error-onze-pending = يجب أن يقرر { $team } أولًا ما إذا كان سيلعب ماو دي أونزي.
trucobrazilian-error-no-calls = لا يُسمح بالإعلانات في هذه التوزيعة لأنها ماو دي أونزي أو ماو دي فيرو.
trucobrazilian-desc-onze-play = العب التوزيعة. تساوي { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} ولا يُسمح بأي إعلانات.
trucobrazilian-desc-onze-run = اهرب وتنازل عن التوزيعة. يسجّل الفريق الآخر نقطة واحدة.

trucobrazilian-action-accept = أسيتو (أقبل)
trucobrazilian-action-decline = كورير (أرفض وأهرب)
trucobrazilian-accept-you = تقول أسيتو على { $call }.
trucobrazilian-accept-player = يقول { $player } أسيتو على { $call }.
trucobrazilian-decline-you = تهرب من { $call }.
trucobrazilian-decline-player = يهرب { $player } من { $call }.
trucobrazilian-pending-answer = أعلن { $player } { $call }. رُدّ بـ أسيتو أو كورير، أو ارفع.
trucobrazilian-error-answer-first = يجب أن ترد على { $call } قبل أي شيء آخر. اختر أسيتو أو كورير، أو ارفع.
trucobrazilian-error-raise-max = دوزي هو أعلى إعلان بالفعل ولا يمكن رفعه.
trucobrazilian-status-onze-pending = يجب أن يقرر { $team } ما إذا كان سيلعب ماو دي أونزي.
trucobrazilian-status-no-calls = لا يُسمح بالإعلانات في هذه التوزيعة. تساوي التوزيعة { $points } { $points ->
    [one] نقطة
   *[other] نقاط
}.

# Mão de ferro (both sides at 11) is played face down; mão de onze partners see each other's cards
trucobrazilian-blind-cards = ماو دي فيرو: بطاقاتك الـ { $count } مقلوبة ولا يمكنك رؤيتها. اخترها بحسب موضعها؛ وتُكشف كل واحدة عند لعبها.
trucobrazilian-blind-hand = ماو دي فيرو: لديك { $count } { $count ->
    [one] بطاقة مقلوبة
   *[other] بطاقات مقلوبة
}، ولا يمكنك { $count ->
    [one] رؤيتها
   *[other] رؤيتها
}.
trucobrazilian-action-play-blind = العب البطاقة المقلوبة { $number }
trucobrazilian-desc-blind-card = بطاقة مقلوبة. لن تراها حتى تُلعب.
trucobrazilian-onze-partner-cards = يُريك شريكك { $partner } بطاقاته: { $cards }.
