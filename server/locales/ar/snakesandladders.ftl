game-name-snakesandladders = الثعابين والسلالم
game-snakesandladders-desc = تسابق من منطقة البداية إلى المربع 100. اصعد السلالم، وانزلق على الثعابين، وكن أول من يصل إلى النهاية.

snakes-roll = رمي النرد
snakes-check-positions = تفقّد المواضع

snakes-turn-start-you = دورك. قطعتك في منطقة البداية قبل المربع 1.
snakes-turn-start-other = دور { $player }. قطعة { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } في منطقة البداية قبل المربع 1.
snakes-turn-you = دورك. أنت على المربع { $position }.
snakes-turn-other = دور { $player }. { GENDER_TERM($player_gender, "subject-be-capitalized") } على المربع { $position }.

snakes-roll-you = ترمي { $roll }.
snakes-roll-other = يرمي { $player } { $roll }.
snakes-enter-you = تتحرك من منطقة البداية إلى المربع { $position }.
snakes-enter-other = يتحرك { $player } من منطقة البداية إلى المربع { $position }.
snakes-enter-you-brief = أنت: المربع { $position }.
snakes-enter-other-brief = { $player }: المربع { $position }.
snakes-move-you = تتحرك { $roll } مربعات من المربع { $start } إلى المربع { $position }.
snakes-move-other = يتحرك { $player } { $roll } مربعات من المربع { $start } إلى المربع { $position }.
snakes-move-you-brief = أنت: المربع { $position }.
snakes-move-other-brief = { $player }: المربع { $position }.
snakes-bounce-you = من المربع { $start }، تتجاوز رميتك { $roll } المربع { $target }، لذا ترتد من النهاية إلى المربع { $position }.
snakes-bounce-other = من المربع { $start }، يرمي { $player } { $roll }، ويتجاوز المربع { $target }، ويرتد من النهاية إلى المربع { $position }.
snakes-bounce-you-brief = ترتد إلى المربع { $position }.
snakes-bounce-other-brief = يرتد { $player } إلى المربع { $position }.
snakes-restored-bounce-you = تنتهي رميتك المحفوظة بارتدادك إلى المربع { $position }.
snakes-restored-bounce-other = تنتهي رمية { $player } المحفوظة بارتداد { GENDER_TERM($player_gender, "object") } إلى المربع { $position }.
snakes-exact-miss-you = تحتاج إلى { $needed } للوصول إلى المربع { $target }، لكنك رميت { $roll }، لذا تبقى على المربع { $position }.
snakes-exact-miss-other = يحتاج { $player } إلى { $needed } للوصول إلى المربع { $target }، لكنه يرمي { $roll }، مما يُبقي { GENDER_TERM($player_gender, "object") } على المربع { $position }.
snakes-exact-miss-you-brief = تحتاج إلى { $needed }، رميت { $roll }، وتبقى على المربع { $position }.
snakes-exact-miss-other-brief = يحتاج { $player } إلى { $needed }، يرمي { $roll }، ويبقى على المربع { $position }.
snakes-ladder-you = تهبط عند أسفل سلّم في المربع { $start } وتصعد إلى المربع { $end }، فتكسب { $distance } مربعات.
snakes-ladder-other = يهبط { $player } عند أسفل سلّم في المربع { $start } ويصعد إلى المربع { $end }، فيكسب { $distance } مربعات.
snakes-ladder-you-brief = تصعد من المربع { $start } إلى { $end }.
snakes-ladder-other-brief = يصعد { $player } من المربع { $start } إلى { $end }.
snakes-snake-you = تهبط على رأس ثعبان في المربع { $start } وتنزلق إلى ذيله في المربع { $end }، فتخسر { $distance } مربعات.
snakes-snake-other = يهبط { $player } على رأس ثعبان في المربع { $start } وينزلق إلى ذيله في المربع { $end }، فيخسر { $distance } مربعات.
snakes-snake-you-brief = تنزلق من المربع { $start } إلى { $end }.
snakes-snake-other-brief = ينزلق { $player } من المربع { $start } إلى { $end }.
snakes-extra-turn-you = رميت 6، لذا تحصل على دور آخر من المربع { $position }.
snakes-extra-turn-other = رمى { $player } 6، مما يمنح { GENDER_TERM($player_gender, "object") } دورًا آخر من المربع { $position }.
snakes-win-you = تصل إلى المربع { $position } وتفوز باللعبة!
snakes-win-other = يصل { $player } إلى المربع { $position } ويفوز باللعبة!

snakes-status-goal = الهدف: المربع { $target }. قاعدة النهاية: { $rule }.
snakes-status-current-start = { $player }: منطقة البداية قبل المربع 1. الدور الحالي.
snakes-status-player-start = { $player }: منطقة البداية قبل المربع 1.
snakes-status-current-position = { $player }: المربع { $position }، { $remaining } متبقٍّ. الدور الحالي.
snakes-status-player-position = { $player }: المربع { $position }، { $remaining } متبقٍّ.
snakes-status-player-finished = { $player }: المربع { $position }، أنهى.

snakes-finish-bounce-back = الارتداد
snakes-finish-exact-stay = رمية مطابقة؛ ابقَ مكانك بعد التجاوز
snakes-set-finish-rule = قاعدة النهاية: { $rule }
snakes-select-finish-rule = اختر قاعدة النهاية
snakes-option-changed-finish-rule = تم تغيير قاعدة النهاية إلى { $rule }.
snakesandladders-desc-finish-rule = يختار ما إذا كان تجاوز المربع 100 يرتد للخلف أم يترك اللاعب بانتظار رمية مطابقة.
snakes-set-extra-turn-six = دور إضافي عند 6: { $enabled }
snakes-option-changed-extra-turn-six = تم تغيير الدور الإضافي عند 6 إلى { $enabled }.
snakesandladders-desc-extra-turn-on-six = يتحكم في ما إذا كان رمي الرقم ستة يمنح دورًا آخر.

snakes-error-roll-not-playing = يمكنك رمي النرد فقط بعد أن تبدأ لعبة الثعابين والسلالم.
snakes-error-roll-not-your-turn = لا يمكنك الرمي الآن لأن لاعبًا آخر يأخذ دوره. انتظر حتى ينتقل الدور إليك.
snakes-error-roll-resolving = رميتك السابقة لا تزال قيد الحل. انتظر انتهاء تسلسل الحركة أو الثعبان أو السلّم قبل الرمي مرة أخرى.
snakes-error-positions-not-playing = المواضع متاحة فقط أثناء وجود لعبة ثعابين وسلالم قيد التقدم.
snakes-error-invalid-finish-rule = قاعدة النهاية المحددة، { $rule }، غير مدعومة. اختر الارتداد أو رمية مطابقة؛ ابقَ مكانك بعد التجاوز.

snakes-end-score = { $rank }. { $player }: المربع { $position }
snakes-end-score-start = { $rank }. { $player }: منطقة البداية قبل المربع 1
