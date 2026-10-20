# Metal Pipe game messages

game-name-metalpipe = الأنبوب المعدني

metalpipe-mode-single = ضربة واحدة
metalpipe-mode-multiple = ضربات متعددة
metalpipe-self-bonk-allowed = ضرب النفس مسموح
metalpipe-self-bonk-blocked = ضرب النفس ممنوع

metalpipe-game-start = تبدأ لعبة الأنبوب المعدني في وضع { $mode }. سيختار الأنبوب كل شيء تلقائيًا.
metalpipe-game-start-brief = الأنبوب المعدني: { $mode }.

metalpipe-you-hit-other = تلوّح بالأنبوب المعدني وتضرب { $bonked }. يُقصى { $bonked }.
metalpipe-player-hits-you = { $bonker } يلوّح بالأنبوب المعدني ويضربك. أنت مُقصى.
metalpipe-player-hits-other = { $bonker } يلوّح بالأنبوب المعدني ويضرب { $bonked }. يُقصى { $bonked }.
metalpipe-you-hit-self = تضرب نفسك بالأنبوب المعدني بطريقة ما وتُقصى.
metalpipe-player-hits-self = { $bonker } يضرب { GENDER_TERM($bonker_gender, "reflexive") } بالأنبوب المعدني بطريقة ما ويُقصى.

metalpipe-you-hit-other-brief = ضربت { $bonked }. { $bonked } خارج اللعبة.
metalpipe-player-hits-you-brief = { $bonker } ضربك. أنت خارج اللعبة.
metalpipe-player-hits-other-brief = { $bonker } ضرب { $bonked }. { $bonked } خارج اللعبة.
metalpipe-you-hit-self-brief = ضربت نفسك. خارج اللعبة.
metalpipe-player-hits-self-brief = { $bonker } ضرب نفسه. خارج اللعبة.

metalpipe-you-win = أنت تفوز. لقد نطق الأنبوب المعدني.
metalpipe-you-win-with-others = تفوز مع { $players }. لقد نطق الأنبوب المعدني.
metalpipe-players-win = { $players } يفوزون. لقد نطق الأنبوب المعدني.
metalpipe-you-win-brief = أنت تفوز.
metalpipe-you-win-with-others-brief = أنت و{ $players } تفوزون.
metalpipe-players-win-brief = الفائزون: { $players }.
metalpipe-no-winner = لا يترك الأنبوب المعدني أي فائز.
metalpipe-no-winner-brief = لا فائز.

metalpipe-check-status = عرض حالة الأنبوب
metalpipe-status-mode = الوضع: { $mode }؛ { $self_bonk }.
metalpipe-status-progress = الضربات المنفّذة: { $count }. اللاعبون الباقون: { $alive } من { $total }.
metalpipe-status-awaiting = لم ينزل الأنبوب بعد.
metalpipe-status-last-other = آخر ضربة: { $bonker } ضرب { $bonked }.
metalpipe-status-last-self = آخر ضربة: { $bonker } ضرب { GENDER_TERM($bonker_gender, "reflexive") }.
metalpipe-status-player = { $player }: { $status }.
metalpipe-status-alive = باقٍ
metalpipe-status-eliminated = مُقصى
metalpipe-no-turn-automatic = تُحسم لعبة الأنبوب المعدني تلقائيًا. لا يزال { $alive } لاعبين باقين، ولا يوجد لاعب له دور يدوي.

metalpipe-final-results = نتائج الأنبوب المعدني
metalpipe-end-winner = الفائز: { $player }.
metalpipe-end-winners = الفائزون: { $players }.
metalpipe-line-format = { $player }: { $status }

metalpipe-set-multiple-bonks = الضربات المتعددة: { $enabled }
metalpipe-option-changed-multiple-bonks = تم ضبط الضربات المتعددة على { $enabled }.
metalpipe-desc-multiple-bonks = عند التفعيل، يستمر الأنبوب في اختيار الضاربين والأهداف حتى يتبقّى لاعب واحد فقط (الوضع الافتراضي: معطّل).
metalpipe-set-allow-self-bonk = السماح بضرب النفس: { $enabled }
metalpipe-option-changed-allow-self-bonk = تم ضبط السماح بضرب النفس على { $enabled }.
metalpipe-desc-allow-self-bonk = عند التفعيل، يمكن للضارب المختار عشوائيًا أن يصبح الهدف أيضًا (الوضع الافتراضي: مفعّل).
