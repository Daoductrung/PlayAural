game-name-dominos = الدومينو
dominos-desc-team-mode = العب فرديًا، أو استخدم أي ترتيب فرق زوجي صالح يدعمه عدد اللاعبين الحالي.

# Options
dominos-set-target-score = النتيجة المستهدفة: { $score }
dominos-enter-target-score = أدخل النتيجة المستهدفة
dominos-option-changed-target-score = تم ضبط النتيجة المستهدفة على { $score }.
dominos-desc-target-score = النتيجة المستهدفة اللازمة للفوز في الدومينو (الافتراضي 100، النطاق 20-500).

dominos-set-draw-mode = الوضع: { $mode }
dominos-select-draw-mode = اختر الوضع
dominos-option-changed-draw-mode = تم ضبط الوضع على { $mode }.
dominos-desc-draw-mode = يختار وضع السحب، حيث يسحب اللاعبون من مخزن السحب، أو وضع الحظر، حيث يمرّر اللاعبون المحظورون.

dominos-set-domino-set = مجموعة الدومينو: { $domino_set }
dominos-select-domino-set = اختر مجموعة الدومينو
dominos-option-changed-domino-set = تم تغيير مجموعة الدومينو إلى { $domino_set }.
dominos-desc-domino-set = حجم مجموعة الدومينو. تدعم مزدوج 6 حتى 5 لاعبين، وتدعم مزدوج 9 حتى 7 لاعبين، وتدعم مزدوج 12 حتى 12 لاعبًا (الافتراضي مزدوج 6).

dominos-set-spinner = الدوّار: { $enabled }
dominos-option-changed-spinner = تم ضبط الدوّار على { $enabled }.
dominos-desc-spinner-enabled = يتحكم في ما إذا كان المزدوج الافتتاحي يُنشئ دوّارًا رباعي الاتجاهات (الافتراضي مفعّل).

dominos-set-opening-rule = قاعدة الافتتاح: { $opening_rule }
dominos-select-opening-rule = اختر قاعدة الافتتاح
dominos-option-changed-opening-rule = تم ضبط قاعدة الافتتاح على { $opening_rule }.
dominos-desc-opening-rule = يختار كيفية اختيار أول حجر في كل جولة دومينو.

# Option choice labels
dominos-mode-draw = سحب
dominos-mode-block = حظر

dominos-set-double6 = مزدوج 6
dominos-set-double9 = مزدوج 9
dominos-set-double12 = مزدوج 12

dominos-opening-highest-double = أعلى مزدوج
dominos-opening-highest-tile = أعلى حجر
dominos-opening-set-max-double = أعلى مزدوج في المجموعة
dominos-opening-random-player = لاعب عشوائي
dominos-opening-round-winner = الفائز بالجولة السابقة

# Actions
dominos-draw = سحب
dominos-knock = طرق
dominos-view-chain = عرض السلسلة
dominos-read-ends = قراءة الأطراف
dominos-read-hand = قراءة اليد
dominos-read-counts = قراءة الأعداد
dominos-play-tile = { $tile }
dominos-open-with-tile = افتتح بـ { $tile }
dominos-play-tile-at = العب { $tile } على { $side }
dominos-play-tile-multi = العب { $tile } على { $sides }
dominos-select-side = اختر طرفًا

# Board sides
dominos-side-left = يسار
dominos-side-right = يمين
dominos-side-up = أعلى
dominos-side-down = أسفل

# Validation and disabled reasons
dominos-draw-only-mode = السحب متاح فقط في وضع السحب.
dominos-must-play = لديك بالفعل حجر قابل للعب.
dominos-boneyard-empty = مخزن السحب فارغ.
dominos-must-draw = يجب أن تسحب قبل الطرق.
dominos-illegal-side = ذلك الطرف غير قانوني للحجر المحدد.
dominos-no-play-for-tile = لا يمكن لعب { $tile } الآن.
dominos-choose-side-keybind = اختر طرفًا بمفتاح الاتجاه. الأطراف القانونية: { $sides }.
dominos-opening-must-play = لم تُفتتح الجولة بعد. يجب أن تختار حجرًا لبدء السلسلة.
dominos-error-set-too-small = لا يمكن توزيع أحجار كافية لـ { $players } لاعبين من مجموعة مزدوج-{ $selected_pip }. اختر مزدوج-{ $required_pip } على الأقل لحجم الطاولة هذا.

# Gameplay
dominos-you-open-round = أنت تبدأ هذه الجولة. اختر أي حجر من يدك لافتتاح السلسلة.
dominos-player-opens-round = { $player } يبدأ هذه الجولة ويختار الحجر الافتتاحي.
dominos-you-opened = افتتحت الجولة بـ { $tile }.
dominos-player-opened = افتتح { $player } الجولة بـ { $tile }.
dominos-you-opened-spinner = افتتحت الجولة بـ { $tile }، منشئًا دوّارًا رباعي الاتجاهات.
dominos-player-opened-spinner = افتتح { $player } الجولة بـ { $tile }، منشئًا دوّارًا رباعي الاتجاهات.
dominos-you-drew-single = سحبت { $tile } من مخزن السحب.
dominos-you-drew-many = سحبت { $count } أحجار من مخزن السحب.
dominos-player-drew-single = سحب { $player } حجرًا واحدًا من مخزن السحب.
dominos-player-drew-many = سحب { $player } { $count } أحجار من مخزن السحب.
dominos-you-played = لعبت { $tile } على فرع { $side }.
dominos-you-played-drawn = سحبت ولعبت { $tile } على فرع { $side }.
dominos-player-played = لعب { $player } { $tile } على فرع { $side }.
dominos-you-knock = تطرق لأنه ليس لديك حجر قانوني للعب.
dominos-player-knocks = يطرق { $player }.
dominos-you-won-round = أفرغت يدك وسجّلت { $points } نقطة من أحجار الخصوم.
dominos-player-won-round = أفرغ { $player } يد { GENDER_TERM($player_gender, "possessive-determiner") } وسجّل { $points } نقطة من أحجار الخصوم.
dominos-round-blocked-tie = الجولة محظورة. أدنى مجموع نقاط هو { $pips }، لكنه متعادل. لا نقاط تُسجَّل.
dominos-round-blocked-winner = الجولة محظورة. يملك { $team } أدنى مجموع نقاط بـ { $pips } ويسجّل { $points } نقطة.
dominos-match-tied-continue = بلغت عدة فرق { $score } نقطة. تستمر اللعبة حتى يُكسر التعادل.
dominos-match-winner = يفوز { $team } باللعبة بـ { $score } نقطة.

# Status boxes
dominos-chain-header = السلسلة
dominos-chain-empty = السلسلة فارغة.
dominos-chain-center = المركز: { $tile }
dominos-branch-empty = لا أحجار
dominos-chain-branch = { $side }: { $tiles }. الطرف المفتوح { $open_end }.
dominos-boneyard-count = مخزن السحب: { $count } حجر متبقٍّ.
dominos-end-info = { $side } { $value }

dominos-hand-header = يدك
dominos-hand-line = { $tile } بقيمة { $points } نقطة.
dominos-hand-line-playable = { $tile } بقيمة { $points } نقطة. قابل للعب على { $sides }.
dominos-hand-line-opening-playable = { $tile } بقيمة { $points } نقطة. يمكنك استخدامه لافتتاح هذه الجولة.
dominos-hand-total = إجمالي النقاط في اليد: { $pips }.
dominos-player-count = لدى { $player } { $count } حجر
dominos-no-other-players = لا لاعبين آخرين.

# End screen
dominos-line-format = { $rank }. { $player }: { $points }
