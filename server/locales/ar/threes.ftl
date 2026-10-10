game-name-threes = الثلاثات

threes-roll = رمي النرد
threes-bank = الحفظ وإنهاء الدور
threes-check-hand = فحص النرد

threes-you-rolled = رميت: { $dice }.
threes-you-rolled-brief = رميت { $dice }.
threes-player-rolled = رمى { $player }: { $dice }.
threes-player-rolled-brief = { $player }: { $dice }.

threes-turn-you = دورك في الجولة { $round } من { $total }. مجموعك الحالي { $score }؛ المجموع الأقل يفوز.
threes-turn-you-brief = دورك. المجموع { $score }.
threes-turn-other = دور { $player } في الجولة { $round } من { $total }. مجموع { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الحالي { $score }.
threes-turn-other-brief = دور { $player}. المجموع { $score }.

threes-you-keep = تحتفظ بالنردة { $index }، التي تظهر { $die }.
threes-you-keep-brief = احتفاظ بـ { $die }.
threes-player-keeps = يحتفظ { $player } بالنردة { $index }، التي تظهر { $die }.
threes-player-keeps-brief = يحتفظ { $player } بـ { $die }.
threes-you-unkeep = تطلق النردة { $index }، التي تظهر { $die }، كي يُعاد رميها.
threes-you-unkeep-brief = إعادة رمي { $die }.
threes-player-unkeeps = يطلق { $player } النردة { $index }، التي تظهر { $die }، كي يُعاد رميها.
threes-player-unkeeps-brief = يعيد { $player } رمي { $die }.

threes-your-dice = نردك هو { $dice }. إذا احتُسب الآن، يساوي هذا الدور { $score } نقطة، مع { $remaining } نردة لا تزال غير مقفلة.
threes-player-dice = نرد { $player } هو { $dice }. إذا احتُسب الآن، يساوي هذا الدور { $score } نقطة، مع { $remaining } نردة لا تزال غير مقفلة.
threes-no-dice-yet = لم ترمِ النرد في هذا الدور بعد.
threes-dice-locked = مقفلة
threes-dice-kept = محتفظ بها
threes-dice-format-status = { $value } ({ $status })
threes-die-index = النردة { $index }
threes-die-value = احتفاظ بـ { $value }
threes-die-kept-label = إعادة رمي { $value }
threes-die-locked-label = { $value } مقفلة

threes-you-scored = تحرز { $score } نقطة في هذا الدور. مجموعك الآن { $total }.
threes-you-scored-brief = أحرزت { $score }. المجموع { $total }.
threes-scored = يحرز { $player } { $score } نقطة في هذا الدور. مجموع { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الآن { $total }.
threes-scored-brief = { $player }: { $score }، المجموع { $total }.
threes-you-shot-moon = أطلقت نحو القمر بخمس ستات وتحرز { $score } نقطة. مجموعك الآن { $total }.
threes-you-shot-moon-brief = إطلاق نحو القمر: { $score }. المجموع { $total }.
threes-shot-moon = أطلق { $player } نحو القمر بخمس ستات ويحرز { $score } نقطة. مجموع { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الآن { $total }.
threes-shot-moon-brief = أطلق { $player } نحو القمر: { $score }، المجموع { $total }.

threes-round-start = تبدأ الجولة { $round } من { $total }.
threes-round-start-brief = الجولة { $round }.
threes-round-scores-header = نتائج الجولة { $round }:
threes-round-scores-header-brief = النتائج بعد الجولة { $round }:
threes-score-pair = { $player }: { $score }

threes-winner = يفوز { $player } بـ { $score } نقطة!
threes-winner-you = تفوز في الثلاثات بـ { $score } نقطة!
threes-winner-you-brief = تفوز بـ { $score }.
threes-winner-other = يفوز { $player } في الثلاثات بـ { $score } نقطة!
threes-winner-other-brief = يفوز { $player } بـ { $score }.
threes-tie = يتعادل { $players } على المجموع الأقل بـ { $score } نقطة!
threes-tie-brief = تعادل: { $players }، { $score }.
threes-tie-you = تتعادل مع { $players } على المجموع الأقل عند { $score } نقطة!
threes-tie-you-brief = تتعادل مع { $players } عند { $score }.

threes-set-rounds = الجولات: { $rounds }
threes-enter-rounds = أدخل عدد الجولات:
threes-option-changed-rounds = تم ضبط عدد الجولات على { $rounds }.
threes-desc-rounds = عدد الجولات التي تُلعب. يأخذ كل لاعب دورًا واحدًا في كل جولة، والمجموع الأقل يفوز (الافتراضي 10، النطاق 1-20).

threes-error-roll-not-playing = لا يمكنك الرمي لأن الثلاثات لم تبدأ.
threes-error-roll-no-turn = لا يمكنك الرمي لأنه لا يوجد دور نشط متاح الآن.
threes-error-roll-not-your-turn = لا يمكنك الرمي الآن لأنه دور { $player }.
threes-error-roll-last-die = لا يمكنك الرمي مجددًا لأنه لم يتبقَّ سوى نردة واحدة غير مقفلة؛ يجب احتساب الدور الآن.
threes-error-roll-must-keep = احتفظ بنردة واحدة غير مقفلة على الأقل قبل الرمي مجددًا.
threes-error-bank-not-playing = لا يمكنك الحفظ لأن الثلاثات لم تبدأ.
threes-error-bank-no-turn = لا يمكنك الحفظ لأنه لا يوجد دور نشط متاح الآن.
threes-error-bank-not-your-turn = لا يمكنك الحفظ الآن لأنه دور { $player }.
threes-error-bank-roll-first = ارمِ النرد قبل محاولة حفظ نتيجة دورك.
threes-error-bank-keep-all = احتفظ بكل نردة غير مقفلة قبل الحفظ، كي تُحتسب نتيجة الدور كاملة.
threes-error-check-not-playing = لا يمكن فحص النرد إلا بعد بدء الثلاثات.
threes-error-check-no-turn = لا يمكن فحص النرد لأنه لا يوجد دور نشط متاح الآن.
threes-error-check-your-dice-not-rolled = لم ترمِ بعد، لذا لا يوجد نرد حالي لفحصه.
threes-error-check-player-dice-not-rolled = لم يرمِ { $player } بعد، لذا لا يوجد نرد حالي لفحصه.
threes-error-toggle-last-die = لا يمكنك تغيير آخر نردة غير مقفلة؛ يجب احتساب الدور من هنا.
threes-error-rounds-out-of-range = لا يمكن أن تبدأ الثلاثات بـ { $rounds } جولة. اختر قيمة من { $min } إلى { $max }.
threes-invalid-die-index = تلك النردة غير متاحة في دور الثلاثات هذا.

threes-keep-all-first = احتفظ بكل النرد أولًا كي تحفظ.
threes-line-format = { $rank }. { $player }: { $points }
