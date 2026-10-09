game-name-tradeoff = المقايضة

tradeoff-round-start = الجولة { $round }.
tradeoff-iteration = اليد { $iteration } من 3.

tradeoff-you-rolled = رميت: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = للمقايضة
tradeoff-trade-status-keeping = للاحتفاظ
tradeoff-confirm-trades = تأكيد المقايضات ({ $count } نردة)
tradeoff-keeping = الاحتفاظ بـ { $value }.
tradeoff-trading = مقايضة { $value }.
tradeoff-you-traded = قايضت { $count } نردة في المجمّع: { $dice }.
tradeoff-player-traded = قايض { $player } { $count } نردة في المجمّع: { $dice }.
tradeoff-you-traded-brief = قايضت { $count } نردة.
tradeoff-player-traded-brief = قايض { $player } { $count } نردة.
tradeoff-you-traded-none = احتفظت بالنرد الخمس من هذه اليد، لذا لن تأخذ من المجمّع هذه المرة.
tradeoff-player-traded-none = احتفظ { $player } بالنرد الخمس من هذه اليد.

tradeoff-your-turn-take = دورك لأخذ نردة من المجمّع.
tradeoff-take-die = خذ { $value } (المتبقي { $remaining })
tradeoff-you-take = تأخذ { $value }.
tradeoff-player-takes = يأخذ { $player } { $value }.

tradeoff-you-scored = أحرزت { $points } نقطة بـ { $sets }.
tradeoff-player-scored = أحرز { $player } { $points } نقطة بـ { $sets }.
tradeoff-you-scored-brief = أحرزت { $points } نقطة في هذه الجولة.
tradeoff-player-scored-brief = أحرز { $player } { $points } نقطة في هذه الجولة.
tradeoff-you-no-sets = أحرزت 0 نقطة لأن نردك الخمسة عشر لم تكوّن أي مجموعة محتسبة.
tradeoff-no-sets = أحرز { $player } 0 نقطة لأن نرد { GENDER_TERM($player_gender, "possessive-determiner") } الخمسة عشر لم تكوّن أي مجموعة محتسبة.

tradeoff-set-triple = ثلاثية من { $value }
tradeoff-set-group = مجموعة من { $value }
tradeoff-set-mini-straight = تسلسل صغير { $low }-{ $high }
tradeoff-set-double-triple = ثلاثية مزدوجة ({ $v1 } و{ $v2 })
tradeoff-set-straight = تسلسل { $low }-{ $high }
tradeoff-set-double-group = مجموعة مزدوجة ({ $v1 } و{ $v2 })
tradeoff-set-all-groups = كل المجموعات
tradeoff-set-all-triplets = كل الثلاثيات

tradeoff-round-scores = نتائج الجولة { $round }:
tradeoff-round-scores-brief = النتائج:
tradeoff-score-line = { $player }: ‎+{ $round_points } (المجموع: { $total })
tradeoff-score-line-brief = { $player}: ‎+{ $round_points }، المجموع { $total }.
tradeoff-leader = يتصدّر { $player } بـ { $score }.
tradeoff-leader-brief = المتصدّر: { $player }، { $score }.

tradeoff-you-win = تفوز بـ { $score } نقطة!
tradeoff-winner = يفوز { $player } بـ { $score } نقطة!
tradeoff-you-tie-win = تتعادل على الفوز مع { $players } عند { $score } نقطة!
tradeoff-winners-tie = إنه تعادل! تعادل { $players } عند { $score } نقطة!

tradeoff-view-hand = عرض يدك
tradeoff-view-pool = عرض المجمّع
tradeoff-view-players = عرض اللاعبين
tradeoff-hand-state-empty = لا يوجد نرد محتفظ به بعد
tradeoff-hand-empty = يدك المحتفظ بها فارغة. إذا كنت قد رميت للتو، استخدم خيارات النرد لتحديد ما تحتفظ به قبل تأكيد المقايضات.
tradeoff-hand-display = يدك المحتفظ بها في هذه الجولة ({ $count } نردة): { $dice }.
tradeoff-hand-display-with-roll = يدك المحتفظ بها في هذه الجولة ({ $count } نردة): { $dice }. الرمية الحالية: { $roll }. لا تزال { $trade_count } نردة مُعلّمة للمقايضة.
tradeoff-roll-die-status = الموضع { $position}: { $value }، { $status }
tradeoff-die-count = { $value}: { $count }
tradeoff-pool-display = المجمّع ({ $count } نردة): { $dice }.
tradeoff-pool-empty = المجمّع فارغ.
tradeoff-player-info = { $player}: اليد المحتفظ بها: { $hand }. آخر مقايضة: { $traded }.
tradeoff-player-info-no-trade = { $player}: اليد المحتفظ بها: { $hand }. لم يقايض شيئًا آخر مرة.

tradeoff-not-trading-phase = لا يمكنك تغيير خيارات المقايضة أو تأكيدها إلا بينما ينتظر نردك المرميّ حديثًا في مرحلة المقايضة.
tradeoff-not-taking-phase = لا يمكنك أخذ النرد إلا بعد أن يؤكّد كل لاعب مقايضاته ويُفتح المجمّع المشترك.
tradeoff-already-confirmed = لقد أكّدت اختيار المقايضة هذا بالفعل. انتظر اللاعبين الآخرين؛ إذا قايضت نردًا، فستأخذ من المجمّع عندما يحين دورك.
tradeoff-no-die = لا توجد نردة متاحة لإجراء المقايضة هذا.
tradeoff-no-die-position = الموضع { $position } غير متاح في رميتك الحالية.
tradeoff-no-rolled-dice = ليس لديك حاليًا نرد مرميّ ينتظر خيارات المقايضة.
tradeoff-no-more-takes = لقد أخذت بالفعل العدد نفسه من النرد الذي قايضته في هذه اليد.
tradeoff-not-in-pool = لا توجد { $value } في المجمّع المشترك الآن. اختر إحدى قيم المجمّع الظاهرة بدلًا من ذلك.
tradeoff-not-your-take-turn = إنه دور { $player } للأخذ من المجمّع. انتظر حتى يُعلَن اسمك قبل اختيار نردة.
tradeoff-no-trading-die-value = ليست لديك { $value } مُعلّمة للمقايضة حاليًا.
tradeoff-no-kept-die-value = ليست لديك { $value } محتفظ بها لتعليمها للمقايضة.
tradeoff-value-trade-style-required = تُستخدم عناصر التحكم بالمقايضة Shift+رقم فقط مع نمط الاحتفاظ بقيم النرد. استخدم مفاتيح الأرقام العادية حسب الموضع، أو غيّر نمط احتفاظك بالنرد الشخصي.
tradeoff-use-plain-number-to-take = استخدم مفتاح الرقم العادي، لا Shift+رقم، لأخذ نردة من المجمّع.
tradeoff-no-dice-key-phase = تُستخدم مفاتيح الأرقام فقط أثناء اختيار المقايضات أو أخذ النرد من المجمّع.

tradeoff-set-target = النتيجة المستهدفة: { $score }
tradeoff-enter-target = أدخل النتيجة المستهدفة:
tradeoff-option-changed-target = تم ضبط النتيجة المستهدفة على { $score }.
tradeoff-desc-target-score = مجموع النتيجة الذي يجب أن يبلغه اللاعب أو يتجاوزه بعد جولة محتسبة ليفوز (الافتراضي 60، النطاق 30-500).
tradeoff-error-target-out-of-range = النتيجة المستهدفة { $score } خارج النطاق المسموح من { $min } إلى { $max }.
